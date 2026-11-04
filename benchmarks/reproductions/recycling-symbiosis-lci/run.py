# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
# ]
# ///
"""Linked LDPE and PP recycling inventories (#339, tracker #333).

Run from the repository root:

    uv run benchmarks/reproductions/recycling-symbiosis-lci/run.py

1. Component reproduction: recomputes the per-kg-ethylene inventory of the PE pyrolysis model
   of Somoza-Tornos et al. (2020) from its global reaction and column recoveries, and compares
   it with the published table under the frozen tolerances (tolerances.yaml).
2. Mass-inventory reconciliation of the LDPE and PP chains in three configurations
   (disconnected with the other olefin burnt, disconnected with it sold, linked), under the
   library's cut-off model with mass allocation.
3. One changed input (the PP waste throughput) as a hypothetical design extension.

Writes results/comparison.json and results/*.svg. Every model input comes from inputs.yaml (and
the pinned library file it names); the reported reference values and the coproduct prices come
from source.yaml, the acceptance tolerances from tolerances.yaml. Exits non-zero only when the script itself fails, including a
failed internal reconciliation check; a reproduction outside tolerance is a verdict, recorded
in comparison.json.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import urllib.request
from importlib import metadata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402

CASE = "recycling-symbiosis-lci"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RESULTS = HERE / "results"

# --------------------------------------------------------------------------------------------
# inputs


def load_yaml(name: str) -> dict:
    with open(HERE / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


INP = load_yaml("inputs.yaml")
TOL = load_yaml("tolerances.yaml")
SRC = load_yaml("source.yaml")

AM = {el: v["value"] for el, v in INP["constants"]["atomic_mass"].items()}
M_CO2 = AM["C"] + 2 * AM["O"]


def parse_formula(formula: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[el] = out.get(el, 0) + (int(n) if n else 1)
    return out


def molar_mass(formula: str) -> float:
    return sum(AM[el] * n for el, n in parse_formula(formula).items())


def carbon_fraction(formula: str) -> float:
    return AM["C"] * parse_formula(formula).get("C", 0) / molar_mass(formula)


W_C_CH2 = carbon_fraction("CH2")
CO2_PER_KG_CH2 = W_C_CH2 * M_CO2 / AM["C"]

# --------------------------------------------------------------------------------------------
# pyrolysis models (per kg of pyrolysis feed)


def ldpe_pyrolysis() -> dict:
    """PE pyrolysis per kg feed from Eq. 1 (normalised) and the T1-T4 recoveries."""
    p = INP["pyrolysis_LDPE"]
    coef = {k: v for k, v in p["global_reaction_coefficients"].items() if k not in ("label", "source")}
    mass = {k: n * molar_mass(k) for k, n in coef.items()}
    total = sum(mass.values())
    frac = {k: m / total for k, m in mass.items()}
    rec = {k: v for k, v in p["recovery"].items() if k not in ("label", "source")}
    products = {k: frac[k] * r for k, r in rec.items()}
    fuel = {k: frac[k] - products.get(k, 0.0) for k in frac}
    fuel = {k: v for k, v in fuel.items() if v > 0}
    co2 = sum(m * carbon_fraction(k) * M_CO2 / AM["C"] for k, m in fuel.items())
    # element content of Eq. 1 products per pseudo-mole, against the CH2 of the polymer
    c_mol = sum(n * parse_formula(k).get("C", 0) for k, n in coef.items())
    h_mol = sum(n * parse_formula(k).get("H", 0) for k, n in coef.items())
    w_c_feed = sum(frac[k] * carbon_fraction(k) for k in frac)
    elec_per_kg_feed = p["net_electricity_per_kg_ethylene"]["value"] * products["C2H4"]
    return {
        "mass_fraction": frac,
        "products": products,  # kg per kg feed
        "fuel": fuel,
        "fuel_total": sum(fuel.values()),
        "co2": co2,
        "w_c_feed": w_c_feed,
        "electricity": elec_per_kg_feed,
        "eq1_pseudo_unit": {"C": c_mol, "H": h_mol, "mass_g": total, "H_deficit_vs_CH2": 1 - h_mol / (2 * c_mol)},
    }


def pp_yields() -> dict[str, float]:
    p = INP["pyrolysis_PP"]
    return {k: v for k, v in p["mass_yield"].items() if k not in ("label", "rationale")}


def pp_pyrolysis(ldpe: dict, yields: dict[str, float] | None = None) -> dict:
    """PP pyrolysis per kg feed from the assumed yields; the remainder closes the carbon on CH2."""
    y = dict(yields) if yields is not None else pp_yields()
    fuel_total = 1.0 - sum(y.values())
    if fuel_total <= 0:
        raise ValueError("PP pyrolysis yields reach or exceed 1 kg/kg")
    # the remainder holds the feed carbon (CH2) that the products do not (inputs.yaml pyrolysis_PP.fuel)
    c_products = sum(m * carbon_fraction(k) for k, m in y.items())
    w_c_rem = (W_C_CH2 - c_products) / fuel_total
    if not 0.0 < w_c_rem < 1.0:
        raise ValueError(f"PP remainder carbon fraction {w_c_rem:.4f} is not physical")
    co2 = fuel_total * w_c_rem * M_CO2 / AM["C"]
    w_c_feed = c_products + fuel_total * w_c_rem
    h_to_c_rem = ((1.0 - w_c_rem) / AM["H"]) / (w_c_rem / AM["C"])
    # same net electricity per kg feed as the LDPE model (assumed)
    return {
        "products": y,
        "fuel": {"remainder (C and H only)": fuel_total},
        "fuel_total": fuel_total,
        "fuel_carbon_fraction": w_c_rem,
        "fuel_H_to_C_molar": h_to_c_rem,
        "co2": co2,
        "w_c_feed": w_c_feed,
        "electricity": ldpe["electricity"],
    }


def element_balance(model: dict) -> dict:
    """Carbon of a pyrolysis model's products and fuel against a CH2 feed, per kg feed (diagnostic)."""
    return {
        "carbon_in_feed_as_CH2": W_C_CH2,
        "carbon_in_products_and_fuel": model["w_c_feed"],
        "imbalance_kg_C_per_kg_feed": model["w_c_feed"] - W_C_CH2,
        "imbalance_rel": (model["w_c_feed"] - W_C_CH2) / W_C_CH2,
    }


# --------------------------------------------------------------------------------------------
# component reproduction (Table 2 of the source, per kg ethylene)


def component_reproduction(ldpe: dict) -> dict:
    ref = SRC["component"]["reported_results"]["per_kg_ethylene"]
    y_eth = ldpe["products"]["C2H4"]
    ours = {
        "waste_PE_feed": 1.0 / y_eth,
        "methane": ldpe["products"]["CH4"] / y_eth,
        "propylene": ldpe["products"]["C3H6"] / y_eth,
        "benzene": ldpe["products"]["C6H6"] / y_eth,
        "direct_CO2_fuel_combustion": ldpe["co2"] / y_eth,
    }
    checks = {}
    for key, tol in TOL["component_checks"].items():
        r = ref[key]["value"]
        o = ours[key]
        dev = (o - r) / r
        checks[key] = {
            "reference": r,
            "ours": round(o, 6),
            "unit": "kg/kg ethylene",
            "deviation_rel": round(dev, 6),
            "tolerance_rel": tol["rel"],
            "status": "pass" if abs(dev) <= tol["rel"] else "fail",
        }
    # mass closure of the table itself: feed = products + fuel (not a frozen check; context)
    table_fuel = ref["waste_PE_feed"]["value"] - 1.0 - sum(ref[k]["value"] for k in ("methane", "propylene", "benzene"))
    verdict = "pass" if all(c["status"] == "pass" for c in checks.values()) else "fail"
    return {
        "reference": "source.yaml component.reported_results.per_kg_ethylene (Table 2)",
        "checks": checks,
        "verdict": verdict,
        "context": {
            "fuel_by_difference_in_table_kg_per_kg_ethylene": round(table_fuel, 4),
            "fuel_ours_kg_per_kg_ethylene": round(ldpe["fuel_total"] / y_eth, 4),
            "CO2_per_kg_table_fuel_implied": round(ref["direct_CO2_fuel_combustion"]["value"] / table_fuel, 4),
            "CO2_per_kg_our_fuel": round(ldpe["co2"] / ldpe["fuel_total"], 4),
            "eq1_pseudo_unit": {k: round(v, 5) for k, v in ldpe["eq1_pseudo_unit"].items()},
        },
    }


# --------------------------------------------------------------------------------------------
# displaced production: Atlas ethylene-1 gate-to-gate direct CO2 per kg hydrocarbon product


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned_library_file(d: dict) -> tuple[bytes, dict]:
    """The library file as committed at the pinned commit (inputs.yaml displaced_production).

    Read with git show so that a later change to the working-tree file cannot change the
    displaced-olefin value. The commit must be reachable from main (local or origin) and the
    content must match the pinned sha256; otherwise the run stops.
    """
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)

    commit = d["commit"]
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        raise RuntimeError(f"pinned commit {commit} of {d['path']} is not in this clone")
    reachable = any(git("merge-base", "--is-ancestor", commit, ref).returncode == 0
                    for ref in ("origin/main", "main"))
    if not reachable:
        raise RuntimeError(f"pinned commit {commit} of {d['path']} is not reachable from main or origin/main")
    shown = git("show", f"{commit}:{d['path']}")
    if shown.returncode != 0:
        raise RuntimeError(f"{d['path']} not found at pinned commit {commit}")
    data = shown.stdout
    digest = hashlib.sha256(data).hexdigest()
    if digest != d["sha256"]:
        raise RuntimeError(f"{d['path']} at {commit} has sha256 {digest}, not the pinned {d['sha256']}")
    work = REPO / d["path"]
    work_digest = sha256_file(work) if work.exists() else None
    return data, {
        "commit": commit,
        "commit_reachable_from_main": reachable,
        "read_from": "git show <commit>:<path>",
        "sha256": digest,
        "working_tree_sha256": work_digest,
        "working_tree_matches_pinned": work_digest == d["sha256"],
    }


def ethylene1_factor() -> dict:
    d = INP["displaced_production"]["dataset"]
    data, pin = pinned_library_file(d)
    digest = pin["sha256"]
    rows = {}
    import csv
    import io

    for row in csv.DictReader(io.StringIO(data.decode("utf-8"), newline="")):
        rows[row["key"]] = row
    products = ["product:ETHYLENE", "product:PROPYLENE", "product:CRUDEC4", "product:PYGAS"]
    # inventory.csv is per kg ethylene with mass allocation already applied to the emissions
    # (ethylene-1 DESIGN.md D-016); under mass allocation the value per kg is the same for every
    # hydrocarbon product, so it is used as it stands. The plant column (kg/h, unallocated) is a
    # cross-check of that reading.
    co2_alloc = float(rows["emission:CO2"]["quantity"])
    co2_plant = float(rows["emission:CO2"]["plant"])
    hc_plant = sum(float(rows[k]["plant"]) for k in products)
    eth_plant = float(rows["product:ETHYLENE"]["plant"])
    cross = co2_plant / hc_plant
    if abs(cross - co2_alloc) / co2_alloc > 1e-5:
        raise RuntimeError("ethylene-1 inventory.csv emission:CO2 is not the mass-allocated value per kg")
    return {
        "path": d["path"],
        **pin,
        "sha256_pinned": d["sha256"],
        "sha256_match": digest == d["sha256"],
        "co2_per_kg_hydrocarbon_product_mass_allocated_in_file": co2_alloc,
        "plant_co2_unallocated_kg_per_h": co2_plant,
        "plant_hydrocarbon_products_kg_per_h": hc_plant,
        "co2_unallocated_per_kg_ethylene": co2_plant / eth_plant,
        "cross_check_plant_co2_over_hydrocarbon_products": cross,
        "co2_per_kg_olefin_mass_allocated": co2_alloc,
    }


# --------------------------------------------------------------------------------------------
# the two chains


OWN = {"LDPE": "C2H4", "PP": "C3H6"}
OTHER = {"LDPE": "C3H6", "PP": "C2H4"}
PARTNER = {"LDPE": "PP", "PP": "LDPE"}


def chains(config: str, waste: dict[str, float], pyro: dict[str, dict], f_virgin: float) -> dict:
    mech = INP["mechanical_recycling"]
    s, y = mech["share_of_waste"]["value"], mech["yield"]["value"]
    subst_rec = mech["recyclate_substitution"]["value"]
    mono_per_poly = INP["polymerisation"]["monomer_per_kg_polymer"]["value"]
    subst_ole = INP["polymerisation"]["olefin_substitution"]["value"]
    deliver = INP["functional_basis"]["polymer_delivered_per_kg_waste"]["value"]

    f: dict[str, dict] = {}
    for name in ("LDPE", "PP"):
        W = waste[name]
        P = pyro[name]
        mech_in = W * s
        recyclate = mech_in * y
        rejects = mech_in - recyclate
        feed = W - mech_in + rejects
        rec = {k: feed * v for k, v in P["products"].items()}
        polymer = W * deliver
        from_monomer = polymer - recyclate * subst_rec
        demand = from_monomer * mono_per_poly
        own_rec = rec[OWN[name]]
        own_used = min(own_rec, demand)
        f[name] = {
            "waste": W,
            "mech_in": mech_in,
            "recyclate": recyclate,
            "rejects_to_pyrolysis": rejects,
            "pyrolysis_feed": feed,
            "recovered": rec,
            "polymer_delivered": polymer,
            "polymer_from_monomer": from_monomer,
            "monomer_demand": demand,
            "own_monomer_used": own_used,
            "own_monomer_surplus_exported": own_rec - own_used,
            "deficit_after_own": demand - own_used,
            "fuel_base": feed * P["fuel_total"],
            "co2_base": feed * P["co2"],
            "electricity_kWh": feed * P["electricity"],
            "carbon_in_pyrolysis_feed_as_CH2": feed * W_C_CH2,
            # carbon the pyrolysis model creates (+) or loses (-) against a CH2 feed (diagnostic)
            "pyrolysis_model_carbon_imbalance": feed * (P["w_c_feed"] - W_C_CH2),
        }

    # route the other olefin
    for name in ("LDPE", "PP"):
        a, b = f[name], f[PARTNER[name]]
        other = a["recovered"][OTHER[name]]
        if config == "D_fuel":
            sent, exported, burnt = 0.0, 0.0, other
        elif config == "D_market":
            sent, exported, burnt = 0.0, other, 0.0
        elif config == "L":
            sent = min(other, b["deficit_after_own"] / subst_ole)
            exported, burnt = other - sent, 0.0
        else:
            raise ValueError(config)
        a["other_olefin_recovered"] = other
        a["other_olefin_sent"] = sent
        a["other_olefin_exported"] = exported
        a["other_olefin_burnt"] = burnt
        b["olefin_received"] = sent * subst_ole

    for name in ("LDPE", "PP"):
        a = f[name]
        a["virgin_monomer"] = a["deficit_after_own"] - a["olefin_received"]
        a["fuel_burnt"] = a["fuel_base"] + a["other_olefin_burnt"]
        a["direct_co2"] = a["co2_base"] + a["other_olefin_burnt"] * CO2_PER_KG_CH2
        a["exported"] = {
            "CH4": a["recovered"]["CH4"],
            "C6H6": a["recovered"]["C6H6"],
            OWN[name]: a["own_monomer_surplus_exported"],
            OTHER[name]: a["other_olefin_exported"],
        }
        # cut-off attribution, mass allocation of the plant's direct CO2 among its products
        prod_mass = (a["own_monomer_used"] + a["own_monomer_surplus_exported"] + a["other_olefin_sent"]
                     + a["other_olefin_exported"] + a["recovered"]["CH4"] + a["recovered"]["C6H6"])
        a["pyrolysis_products_mass"] = prod_mass
        a["co2_per_kg_product_mass_alloc"] = a["direct_co2"] / prod_mass

    for name in ("LDPE", "PP"):
        a, b = f[name], f[PARTNER[name]]
        a["alloc_co2_own_monomer_used"] = a["own_monomer_used"] * a["co2_per_kg_product_mass_alloc"]
        a["alloc_co2_received_olefin"] = (a["olefin_received"] / subst_ole) * b["co2_per_kg_product_mass_alloc"]
        a["alloc_co2_exported"] = (sum(a["exported"].values())) * a["co2_per_kg_product_mass_alloc"]
        a["alloc_co2_sent"] = a["other_olefin_sent"] * a["co2_per_kg_product_mass_alloc"]
        a["polymer_foreground_co2_cutoff"] = a["alloc_co2_own_monomer_used"] + a["alloc_co2_received_olefin"]
        a["virgin_supply_gate_co2"] = a["virgin_monomer"] * f_virgin

    # ---------------- checks (internal) ----------------
    # The out side of each balance is rebuilt from the primary inputs (waste, delivery basis,
    # mechanical split, pyrolysis yields), not from the supply terms the routing computed, so the
    # in and out sides do not cancel term by term: a supply that misses or overshoots the
    # monomer demand, or a recovered stream that is lost or counted twice in routing, fails.
    checks = {}
    for name in ("LDPE", "PP"):
        a = f[name]
        W, P = waste[name], pyro[name]
        rec_ind = W * s * y                                   # recyclate, from the mechanical split
        feed_ind = W - rec_ind                                # pyrolysis feed (input not made into recyclate)
        from_mono_ind = W * deliver - rec_ind * subst_rec     # polymer the chain must make from monomer
        demand_ind = from_mono_ind * mono_per_poly            # monomer it must polymerise
        poly_loss = demand_ind - from_mono_ind                # polymerisation loss (0 at 1 kg/kg)
        other_out_ind = feed_ind * P["products"][OTHER[name]]  # the other olefin as recovered
        m_in = a["waste"] + a["virgin_monomer"] + a["olefin_received"]
        # out: delivered polymer and its losses, as the basis demands, plus every pyrolysis output
        # that leaves the folder as routed (exported, sent, burnt); the own monomer polymerised is
        # inside the polymer. In equals out only if own + received + virgin monomer meets the demand.
        m_out = rec_ind + from_mono_ind + poly_loss + sum(a["exported"].values()) + a["other_olefin_sent"] \
            + a["fuel_burnt"]
        checks[f"mass_closure_{name}"] = {"in": m_in, "out": m_out, "rel": abs(m_out - m_in) / m_in}
        # carbon: every hydrocarbon input as CH2 (waste, virgin and received olefin). The pyrolysis
        # model's own element imbalance enters as a declared term, so this check tests the chain
        # bookkeeping (routing, burning, export) and holds by construction for the pyrolysis unit.
        c_in_ch2 = (a["waste"] + a["virgin_monomer"] + a["olefin_received"]) * W_C_CH2
        c_in = c_in_ch2 + a["pyrolysis_model_carbon_imbalance"]
        c_out = (rec_ind + from_mono_ind + poly_loss) * W_C_CH2 + a["exported"]["CH4"] * carbon_fraction("CH4") \
            + a["exported"]["C6H6"] * carbon_fraction("C6H6") \
            + (a["exported"][OWN[name]] + a["exported"][OTHER[name]] + a["other_olefin_sent"]) * W_C_CH2 \
            + a["direct_co2"] * AM["C"] / M_CO2
        checks[f"carbon_closure_{name}"] = {
            "in_as_CH2": c_in_ch2, "pyrolysis_model_imbalance_term": a["pyrolysis_model_carbon_imbalance"],
            "in": c_in, "out": c_out, "rel": abs(c_out - c_in) / c_in,
            "rel_against_CH2_without_model_term_diagnostic": abs(c_out - c_in_ch2) / c_in_ch2,
            "note": "holds by construction for the pyrolysis unit; its element balance is reported under pyrolysis_element_balance",
        }
        # exchange: the sender's outflow is its recovered other olefin less what it sold and burnt
        # (recomputed from its pyrolysis feed); the receiver's supply must meet its demand rebuilt
        # from its own primary inputs, with the received olefin in place of virgin monomer.
        b, nb = f[PARTNER[name]], PARTNER[name]
        Wb, Pb = waste[nb], pyro[nb]
        rec_b = Wb * s * y
        demand_b = (Wb * deliver - rec_b * subst_rec) * mono_per_poly
        own_b = min((Wb - rec_b) * Pb["products"][OWN[nb]], demand_b)
        outflow = other_out_ind - a["other_olefin_exported"] - a["other_olefin_burnt"]
        checks[f"exchange_identity_{name}_to_{nb}"] = {
            "sent_from_sender_outflow": outflow,
            "received": b["olefin_received"],
            "abs": abs(outflow * subst_ole - b["olefin_received"])
            + abs(demand_b - own_b - b["olefin_received"] - b["virgin_monomer"]),
        }
    total_co2 = f["LDPE"]["direct_co2"] + f["PP"]["direct_co2"]
    alloc_sum = sum(f[n]["alloc_co2_own_monomer_used"] + f[n]["alloc_co2_sent"] + f[n]["alloc_co2_exported"]
                    for n in ("LDPE", "PP"))
    checks["allocation_conservation"] = {"unallocated": total_co2, "allocated_sum": alloc_sum,
                                         "rel": abs(alloc_sum - total_co2) / total_co2}
    rec_tol = TOL["reconciliation_checks"]
    for key, c in checks.items():
        if key.startswith("mass_closure"):
            c["status"] = "pass" if c["rel"] <= rec_tol["mass_closure"]["rel"] else "fail"
        elif key.startswith("carbon_closure"):
            c["status"] = "pass" if c["rel"] <= rec_tol["carbon_closure"]["rel"] else "fail"
        elif key.startswith("exchange_identity"):
            c["status"] = "pass" if c["abs"] <= rec_tol["exchange_identity"]["abs"] else "fail"
        else:
            c["status"] = "pass" if c["rel"] <= rec_tol["allocation_conservation"]["rel"] else "fail"

    virgin = {"C2H4": f["LDPE"]["virgin_monomer"], "C3H6": f["PP"]["virgin_monomer"]}
    exported_olefin = {
        "C2H4": f["LDPE"]["exported"]["C2H4"] + f["PP"]["exported"]["C2H4"],
        "C3H6": f["LDPE"]["exported"]["C3H6"] + f["PP"]["exported"]["C3H6"],
    }
    combined = {
        "virgin_olefin_bought_kg": sum(virgin.values()),
        "virgin_ethylene_kg": virgin["C2H4"],
        "virgin_propylene_kg": virgin["C3H6"],
        "olefin_exported_kg": sum(exported_olefin.values()),
        "olefin_burnt_kg": f["LDPE"]["other_olefin_burnt"] + f["PP"]["other_olefin_burnt"],
        "olefin_exchanged_kg": f["LDPE"]["other_olefin_sent"] + f["PP"]["other_olefin_sent"],
        "net_virgin_olefin_system_expansion_kg": sum(virgin.values()) - sum(exported_olefin.values()),
        "methane_exported_kg": f["LDPE"]["exported"]["CH4"] + f["PP"]["exported"]["CH4"],
        "benzene_exported_kg": f["LDPE"]["exported"]["C6H6"] + f["PP"]["exported"]["C6H6"],
        "foreground_direct_co2_kg": total_co2,
        "polymer_foreground_co2_cutoff_kg": f["LDPE"]["polymer_foreground_co2_cutoff"] + f["PP"]["polymer_foreground_co2_cutoff"],
        "exported_products_co2_cutoff_kg": f["LDPE"]["alloc_co2_exported"] + f["PP"]["alloc_co2_exported"],
        "virgin_supply_gate_co2_kg": sum(virgin.values()) * f_virgin,
        "net_virgin_supply_gate_co2_system_expansion_kg": (sum(virgin.values()) - sum(exported_olefin.values())) * f_virgin,
        "net_electricity_kWh": f["LDPE"]["electricity_kWh"] + f["PP"]["electricity_kWh"],
        "polymer_delivered_kg": f["LDPE"]["polymer_delivered"] + f["PP"]["polymer_delivered"],
        "waste_treated_kg": waste["LDPE"] + waste["PP"],
    }
    return {"config": config, "folders": f, "combined": combined, "checks": checks}


# --------------------------------------------------------------------------------------------
# sensitivities (not frozen checks): burnt-olefin heat credit, energy allocation, PP yields


def lhv(formula: str) -> float:
    """Lower heating value in MJ/kg from the standard enthalpy of combustion (inputs.yaml)."""
    c = INP["constants"]
    dch = c["combustion_enthalpy"][formula]["value"]  # kJ/mol, negative, water liquid
    n_h2o = parse_formula(formula).get("H", 0) / 2
    return (-dch - n_h2o * c["water_vaporisation_enthalpy"]["value"]) / molar_mass(formula)


def saturation_ratio(pyro: dict, W_L: float, W_P: float) -> float:
    base = chains("L", {"LDPE": W_L, "PP": W_P}, pyro, 0.0)
    mech = INP["mechanical_recycling"]
    feed_per_kg_pp = 1 - mech["share_of_waste"]["value"] * mech["yield"]["value"]
    return base["folders"]["LDPE"]["deficit_after_own"] / (pyro["PP"]["products"]["C2H4"] * feed_per_kg_pp) / W_L


def sensitivities(runs: dict, pyro: dict, waste: dict, f_virgin: float) -> dict:
    out: dict = {"label": "sensitivities, not frozen checks"}
    # (1) D_fuel: heat of the burnt olefin displaces natural gas (inputs.yaml configurations.D_fuel)
    hc = INP["configurations"]["D_fuel"]["heat_credit_sensitivity"]
    ef, disp = hc["natural_gas_co2_factor"]["value"], hc["displacement"]["value"]
    df = runs["D_fuel"]["folders"]
    heat = sum(df[n]["other_olefin_burnt"] * lhv(OTHER[n]) for n in ("LDPE", "PP"))
    gross = runs["D_fuel"]["combined"]["foreground_direct_co2_kg"] - runs["L"]["combined"]["foreground_direct_co2_kg"]
    credit = heat * disp * ef
    out["D_fuel_heat_credit"] = {
        "lhv_MJ_per_kg": {k: lhv(k) for k in ("C2H4", "C3H6")},
        "heat_of_burnt_olefin_MJ": heat,
        "natural_gas_co2_displaced_kg": credit,
        "co2_avoided_by_linking_no_heat_use_kg (upper bound)": gross,
        "co2_avoided_by_linking_with_heat_credit_kg": gross - credit,
    }
    # (2) energy (LHV) allocation of each plant's direct CO2, against mass (base)
    e: dict = {}
    for cfg, r in runs.items():
        f = r["folders"]
        per_mj = {}
        for n in ("LDPE", "PP"):
            a = f[n]
            energy = ((a["own_monomer_used"] + a["own_monomer_surplus_exported"]) * lhv(OWN[n])
                      + (a["other_olefin_sent"] + a["other_olefin_exported"]) * lhv(OTHER[n])
                      + a["recovered"]["CH4"] * lhv("CH4") + a["recovered"]["C6H6"] * lhv("C6H6"))
            per_mj[n] = a["direct_co2"] / energy
        e[cfg] = {}
        for n in ("LDPE", "PP"):
            a = f[n]
            pol = a["own_monomer_used"] * lhv(OWN[n]) * per_mj[n] \
                + a["olefin_received"] / INP["polymerisation"]["olefin_substitution"]["value"] * lhv(OTHER[n]) * per_mj[PARTNER[n]]
            e[cfg][n] = {"polymer_foreground_co2_energy_alloc_kg": pol,
                         "polymer_foreground_co2_mass_alloc_kg": a["polymer_foreground_co2_cutoff"]}
    out["energy_allocation"] = {"lhv_MJ_per_kg": {k: lhv(k) for k in ("CH4", "C2H4", "C3H6", "C6H6")}, "configurations": e}
    # (3) PP pyrolysis yields over the assumed range (inputs.yaml pyrolysis_PP.sensitivity_range)
    rng = INP["pyrolysis_PP"]["sensitivity_range"]
    rows = []
    for comp in ("C2H4", "C3H6"):
        for bound in ("low", "high"):
            y = pp_yields()
            y[comp] = rng[comp][bound]
            pyro_s = {"LDPE": pyro["LDPE"], "PP": pp_pyrolysis(pyro["LDPE"], y)}
            rs = {cfg: chains(cfg, waste, pyro_s, f_virgin) for cfg in ("D_fuel", "D_market", "L")}
            for cfg, r in rs.items():
                for key, c in r["checks"].items():
                    if c["status"] != "pass":
                        raise RuntimeError(f"sensitivity reconciliation check failed: {comp} {bound} {cfg}:{key}")
            rows.append({
                "varied": f"PP {comp} yield", "bound": bound, "value_kg_per_kg_feed": rng[comp][bound],
                "ethylene_to_LDPE_kg": rs["L"]["folders"]["PP"]["other_olefin_sent"],
                "propylene_to_PP_kg": rs["L"]["folders"]["LDPE"]["other_olefin_sent"],
                "virgin_olefin_saved_vs_D_fuel_kg": rs["D_fuel"]["combined"]["virgin_olefin_bought_kg"] - rs["L"]["combined"]["virgin_olefin_bought_kg"],
                "virgin_olefin_bought_L_kg": rs["L"]["combined"]["virgin_olefin_bought_kg"],
                "foreground_direct_co2_D_fuel_kg": rs["D_fuel"]["combined"]["foreground_direct_co2_kg"],
                "foreground_direct_co2_L_kg": rs["L"]["combined"]["foreground_direct_co2_kg"],
                "saturation_ratio_PP_to_LDPE": saturation_ratio(pyro_s, waste["LDPE"], waste["PP"]),
            })
    out["pp_yields"] = {"range": {k: {b: rng[k][b] for b in ("low", "high")} for k in ("C2H4", "C3H6")},
                        "label": rng["label"], "rows": rows}
    return out


# --------------------------------------------------------------------------------------------
# provenance check of the component source (download, hash, never parse or execute)


def cache_dir() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    d = base / "cheme-reproductions" / CASE
    d.mkdir(parents=True, exist_ok=True)
    return d


def verify_download(entry: dict, name: str) -> dict:
    """Download a pinned file into the cache and check its sha256; it is never parsed or executed."""
    target = cache_dir() / name
    status = {"url": entry["url"], "sha256_pinned": entry["sha256"], "cache": f"$XDG_CACHE_HOME or ~/.cache, cheme-reproductions/{CASE}/{target.name}"}
    try:
        if target.exists() and sha256_file(target) == entry["sha256"]:
            digest = entry["sha256"]
        else:
            # download to a .part file and replace the cached copy only when the hash matches;
            # on a mismatch the old cache is kept and the .part file is removed
            tmp = target.with_suffix(".part")
            req = urllib.request.Request(entry["url"], headers={"User-Agent": f"cheme-reproductions/{CASE} (provenance hash check)"})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
                fh.write(r.read())
            digest = sha256_file(tmp)
            if digest == entry["sha256"]:
                tmp.replace(target)
            else:
                tmp.unlink()
        status["sha256"] = digest
        status["status"] = "verified" if digest == entry["sha256"] else "hash mismatch"
    except OSError as exc:  # network failure: the numbers are in inputs.yaml, so the run goes on
        status["status"] = f"not verified ({type(exc).__name__})"
    return status


def verify_component_source() -> dict:
    return verify_download(SRC["component"]["files"][0], "somoza-tornos-2020-accepted-manuscript.pdf")


def verify_target_source() -> dict:
    book = SRC["target"]["records"]["abstract_book"]
    return verify_download({"url": book["download_url"], "sha256": book["sha256"]}, "setac-europe-2025-abstract-book.pdf")


# --------------------------------------------------------------------------------------------
# figures (our own code; light surface of the dataviz reference palette)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # blue, orange, aqua, yellow (slots 1-4)


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name: str):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None}, facecolor=SURFACE)
    plt.close(fig)


def fig_monomer_supply(runs: dict):
    labels = {"D_fuel": "Disconnected,\nother olefin burnt", "D_market": "Disconnected,\nother olefin sold", "L": "Linked\n(exchange)"}
    parts = [("recyclate", "Recyclate"), ("own_monomer_used", "Own recovered monomer"),
             ("olefin_received", "Olefin from the other chain"), ("virgin_monomer", "Virgin monomer")]
    fig, ax = plt.subplots(figsize=(8.2, 4.4), facecolor=SURFACE)
    style_axes(ax)
    x, ticks, ticklabels = 0.0, [], []
    for cfg in ("D_fuel", "D_market", "L"):
        for name in ("LDPE", "PP"):
            fold = runs[cfg]["folders"][name]
            bottom = 0.0
            for i, (key, _) in enumerate(parts):
                h = fold[key]
                if h > 0:
                    ax.bar(x, h, bottom=bottom, width=0.7, color=SERIES[i], edgecolor=SURFACE, linewidth=2)
                bottom += h
            ax.text(x, bottom + 15, name, ha="center", va="bottom", fontsize=8, color=INK2)
            x += 0.85
        ticks.append(x - 0.85 * 1.5)
        ticklabels.append(labels[cfg])
        x += 0.6
    ax.set_xticks(ticks, ticklabels, fontsize=9, color=INK)
    ax.set_ylabel("Polymer supplied per chain (kg)", color=INK, fontsize=9)
    ax.set_ylim(0, 1150)
    handles = [plt.Rectangle((0, 0), 1, 1, color=SERIES[i]) for i in range(len(parts))]
    ax.legend(handles, [p[1] for p in parts], loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4,
              frameon=False, fontsize=8, labelcolor=INK)
    ax.set_title("Where each chain's 1000 kg of polymer comes from", color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    save(fig, "monomer-supply.svg")


def fig_combined(runs: dict):
    cfgs = ["D_fuel", "D_market", "L"]
    names = {"D_fuel": "Disconnected, burnt", "D_market": "Disconnected, sold", "L": "Linked"}
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), facecolor=SURFACE)
    # panel 1: olefin balance of the combined system
    ax = axes[0]
    style_axes(ax)
    xs = np.arange(len(cfgs))
    bought = [runs[c]["combined"]["virgin_olefin_bought_kg"] for c in cfgs]
    net = [runs[c]["combined"]["net_virgin_olefin_system_expansion_kg"] for c in cfgs]
    ax.bar(xs - 0.18, bought, 0.34, color=SERIES[0], edgecolor=SURFACE, linewidth=2, label="Virgin olefin bought (cut-off)")
    ax.bar(xs + 0.18, net, 0.34, color=SERIES[1], edgecolor=SURFACE, linewidth=2, label="Net of olefin sold (system expansion)")
    for i in range(len(cfgs)):
        ax.text(xs[i] - 0.18, bought[i] + 8, f"{bought[i]:.0f}", ha="center", fontsize=8, color=INK2)
        ax.text(xs[i] + 0.18, net[i] + 8, f"{net[i]:.0f}", ha="center", fontsize=8, color=INK2)
    ax.set_xticks(xs, [names[c] for c in cfgs], fontsize=8, color=INK)
    ax.set_ylabel("kg olefin per basis", color=INK, fontsize=9)
    ax.set_title("Virgin olefin, both chains", color=INK, fontsize=10, loc="left")
    ax.set_ylim(0, max(bought) * 1.35)
    ax.legend(frameon=False, fontsize=7.5, labelcolor=INK, loc="upper right")
    # panel 2: foreground direct CO2
    ax = axes[1]
    style_axes(ax)
    co2 = [runs[c]["combined"]["foreground_direct_co2_kg"] for c in cfgs]
    ax.bar(xs, co2, 0.5, color=SERIES[2], edgecolor=SURFACE, linewidth=2)
    for i in range(len(cfgs)):
        ax.text(xs[i], co2[i] + 8, f"{co2[i]:.0f}", ha="center", fontsize=8, color=INK2)
    ax.set_xticks(xs, [names[c] for c in cfgs], fontsize=8, color=INK)
    ax.set_ylabel("kg fossil CO2 per basis", color=INK, fontsize=9)
    ax.set_title("Foreground direct CO2 (pyrolysis furnaces)", color=INK, fontsize=10, loc="left")
    fig.suptitle("Combined system: 1000 kg waste LDPE + 1000 kg waste PP, 2000 kg polymer delivered",
                 color=INK2, fontsize=8.5, x=0.01, ha="left", y=0.04)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "combined-inventory.svg")


def extension(pyro: dict, f_virgin: float) -> dict:
    W_L = INP["functional_basis"]["waste_LDPE_sorted"]["value"]
    base_pp = INP["functional_basis"]["waste_PP_sorted"]["value"]
    changed_pp = 4.0 * base_pp
    # saturation: PP waste at which the received ethylene covers the LDPE chain's deficit
    base = chains("L", {"LDPE": W_L, "PP": base_pp}, pyro, f_virgin)
    deficit = base["folders"]["LDPE"]["deficit_after_own"]
    mech = INP["mechanical_recycling"]
    feed_per_kg_pp = 1 - mech["share_of_waste"]["value"] * mech["yield"]["value"]
    w_sat = deficit / (pyro["PP"]["products"]["C2H4"] * feed_per_kg_pp)
    sweep = sorted(set(np.linspace(0.1 * base_pp, 6.0 * base_pp, 60).tolist()) | {w_sat})
    rows = []
    for w in sweep:
        r = chains("L", {"LDPE": W_L, "PP": float(w)}, pyro, f_virgin)
        rd = chains("D_fuel", {"LDPE": W_L, "PP": float(w)}, pyro, f_virgin)
        rows.append({
            "waste_PP_kg": float(w),
            "ethylene_to_LDPE_kg": r["folders"]["PP"]["other_olefin_sent"],
            "ethylene_surplus_sold_kg": r["folders"]["PP"]["other_olefin_exported"],
            "LDPE_virgin_ethylene_kg": r["folders"]["LDPE"]["virgin_monomer"],
            "propylene_to_PP_kg": r["folders"]["LDPE"]["other_olefin_sent"],
            "virgin_olefin_saved_vs_D_fuel_kg": rd["combined"]["virgin_olefin_bought_kg"] - r["combined"]["virgin_olefin_bought_kg"],
        })
    ch = chains("L", {"LDPE": W_L, "PP": changed_pp}, pyro, f_virgin)
    chd = chains("D_fuel", {"LDPE": W_L, "PP": changed_pp}, pyro, f_virgin)
    for key, c in {**ch["checks"], **chd["checks"]}.items():
        if c["status"] != "pass":
            raise RuntimeError(f"extension reconciliation check failed: {key}")

    def summary(run, run_d):
        return {
            "ethylene_received_by_LDPE_kg": run["folders"]["LDPE"]["olefin_received"],
            "ethylene_surplus_sold_kg": run["folders"]["PP"]["other_olefin_exported"],
            "LDPE_virgin_ethylene_kg": run["folders"]["LDPE"]["virgin_monomer"],
            "LDPE_share_of_ethylene_demand_met_by_exchange": run["folders"]["LDPE"]["olefin_received"] / run["folders"]["LDPE"]["monomer_demand"],
            "propylene_received_by_PP_kg": run["folders"]["PP"]["olefin_received"],
            "PP_virgin_propylene_kg": run["folders"]["PP"]["virgin_monomer"],
            "virgin_olefin_saved_vs_D_fuel_kg": run_d["combined"]["virgin_olefin_bought_kg"] - run["combined"]["virgin_olefin_bought_kg"],
            "net_virgin_olefin_system_expansion_kg": run["combined"]["net_virgin_olefin_system_expansion_kg"],
            "net_virgin_olefin_system_expansion_D_market_kg": chains("D_market", {"LDPE": W_L, "PP": run["folders"]["PP"]["waste"]}, pyro, f_virgin)["combined"]["net_virgin_olefin_system_expansion_kg"],
        }

    base_d = chains("D_fuel", {"LDPE": W_L, "PP": base_pp}, pyro, f_virgin)
    out = {
        "label": "HYPOTHETICAL design extension (not validated)",
        "changed_input": {"name": "functional_basis.waste_PP_sorted", "base": base_pp, "changed": changed_pp, "unit": "kg"},
        "base": summary(base, base_d),
        "changed": summary(ch, chd),
        "saturation_waste_PP_kg": w_sat,
        "saturation_ratio_PP_to_LDPE": w_sat / W_L,
        "sweep": [{k: round(v, 4) for k, v in r.items()} for r in rows],
    }
    # figure
    fig, ax = plt.subplots(figsize=(8.2, 4.2), facecolor=SURFACE)
    style_axes(ax)
    xw = [r["waste_PP_kg"] for r in rows]
    ax.plot(xw, [r["ethylene_to_LDPE_kg"] for r in rows], color=SERIES[0], linewidth=2, label="Ethylene sent from PP chain to LDPE chain")
    ax.plot(xw, [r["LDPE_virgin_ethylene_kg"] for r in rows], color=SERIES[1], linewidth=2, label="Virgin ethylene still bought by LDPE chain")
    ax.plot(xw, [r["ethylene_surplus_sold_kg"] for r in rows], color=SERIES[2], linewidth=2, label="Ethylene surplus sold")
    ax.axvline(w_sat, color=INK2, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(w_sat + 60, deficit * 0.80,
            f"saturation at {w_sat:.0f} kg waste PP\n({w_sat / W_L:.1f} x the LDPE batch)", fontsize=8, color=INK2, va="top")
    for wv, run, lab in ((base_pp, base, "base case"), (changed_pp, ch, "changed input")):
        yv = run["folders"]["LDPE"]["olefin_received"]
        ax.plot([wv], [yv], marker="o", markersize=8, color=SERIES[0], markeredgecolor=SURFACE,
                markeredgewidth=2, linestyle="none")
        ax.annotate(f"{lab}: {yv:.0f} kg", (wv, yv), xytext=(8, 10), textcoords="offset points", fontsize=8, color=INK2)
    ax.set_xlabel("Sorted waste PP treated, with 1000 kg waste LDPE (kg)", color=INK, fontsize=9)
    ax.set_ylabel("kg ethylene", color=INK, fontsize=9)
    ax.set_title("Hypothetical: the exchange is capped by the receiving chain's demand", color=INK, fontsize=11, loc="left")
    ax.set_ylim(0, deficit * 1.2)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    fig.tight_layout()
    save(fig, "extension-pp-throughput.svg")
    return out


# --------------------------------------------------------------------------------------------


def rounded(obj, nd=6):
    if isinstance(obj, float):
        return round(obj, nd)
    if isinstance(obj, dict):
        return {k: rounded(v, nd) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rounded(v, nd) for v in obj]
    return obj


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    plt.rcParams.update({"svg.hashsalt": CASE, "svg.fonttype": "none", "font.family": "DejaVu Sans"})

    ldpe = ldpe_pyrolysis()
    pp = pp_pyrolysis(ldpe)
    if abs(element_balance(pp)["imbalance_rel"]) > 1e-12:
        raise RuntimeError("PP pyrolysis model does not close on CH2")
    pyro = {"LDPE": ldpe, "PP": pp}
    comp = component_reproduction(ldpe)
    eth1 = ethylene1_factor()
    if not eth1["working_tree_matches_pinned"]:
        print(f"note: the working-tree {eth1['path']} differs from the pinned commit; the pinned version is used", file=sys.stderr)
    f_virgin = eth1["co2_per_kg_olefin_mass_allocated"]

    waste = {"LDPE": INP["functional_basis"]["waste_LDPE_sorted"]["value"],
             "PP": INP["functional_basis"]["waste_PP_sorted"]["value"]}
    runs = {cfg: chains(cfg, waste, pyro, f_virgin) for cfg in ("D_fuel", "D_market", "L")}
    failed = [f"{cfg}:{k}" for cfg, r in runs.items() for k, c in r["checks"].items() if c["status"] != "pass"]
    if failed:
        print("reconciliation checks failed: " + ", ".join(failed), file=sys.stderr)
        return 2

    # direction check against the target's qualitative claim (not a reproduction)
    L, Df, Dm = (runs[c]["combined"] for c in ("L", "D_fuel", "D_market"))
    direction = {
        "claim": TOL["target_checks"]["direction_check"]["claim"],
        "virgin_olefin_L_not_above_D": L["virgin_olefin_bought_kg"] <= min(Df["virgin_olefin_bought_kg"], Dm["virgin_olefin_bought_kg"]) + 1e-9,
        "direct_co2_L_not_above_D": L["foreground_direct_co2_kg"] <= min(Df["foreground_direct_co2_kg"], Dm["foreground_direct_co2_kg"]) + 1e-9,
        "net_virgin_olefin_L_minus_D_market_system_expansion_kg": L["net_virgin_olefin_system_expansion_kg"] - Dm["net_virgin_olefin_system_expansion_kg"],
        "counts_for_reproduction": False,
    }
    direction["status"] = "consistent" if direction["virgin_olefin_L_not_above_D"] and direction["direct_co2_L_not_above_D"] else "inconsistent"

    case_verdict = "partial" if comp["verdict"] == "pass" else "fail"
    ext = extension(pyro, f_virgin)
    sens = sensitivities(runs, pyro, waste, f_virgin)
    fig_monomer_supply(runs)
    fig_combined(runs)

    out = {
        "case": CASE,
        "issue": "ChemE-as-Code/process-library#339 (tracker #333)",
        "tolerances_file": "tolerances.yaml",
        "verdict": {
            "case": case_verdict,
            "target_reproduction": "not achievable",
            "component_reproduction": comp["verdict"],
            "rule": TOL["pass_rule"],
        },
        "component_reproduction": comp,
        "target": {"status": TOL["target_checks"]["status"], "direction_check": direction},
        "pyrolysis_models_per_kg_feed": {
            "LDPE": {"products": ldpe["products"], "fuel": ldpe["fuel"], "fuel_total": ldpe["fuel_total"],
                      "direct_co2": ldpe["co2"], "net_electricity_kWh": ldpe["electricity"],
                      "label": "reconstructed (Somoza-Tornos et al. 2020)"},
            "PP": {"products": pp["products"], "fuel_total": pp["fuel_total"], "direct_co2": pp["co2"],
                    "fuel_carbon_fraction": pp["fuel_carbon_fraction"], "fuel_H_to_C_molar": pp["fuel_H_to_C_molar"],
                    "net_electricity_kWh": pp["electricity"], "label": "assumed"},
        },
        "pyrolysis_element_balance": {
            "note": "diagnostic, per kg pyrolysis feed, against the CH2 of the polymer; not a frozen check",
            "LDPE": element_balance(ldpe),
            "PP": element_balance(pp),
        },
        "allocation": {
            "rule": "mass (docs/system-model.md step 3; step 2 not applied, inputs.yaml coproduct_treatment)",
            "price_ratio_max_min": max(v for k, v in SRC["component"]["model_facts"]["prices_eur_per_kg"].items() if k != "locator" and k != "waste_PE_sorted")
            / min(v for k, v in SRC["component"]["model_facts"]["prices_eur_per_kg"].items() if k != "locator" and k != "waste_PE_sorted"),
        },
        "displaced_production": eth1,
        "configurations": runs,
        "extension": ext,
        "sensitivities": sens,
        "provenance": {
            "component_source": verify_component_source(),
            "target_source_abstract_book": verify_target_source(),
            "python": platform.python_version(),
            "packages": {p: metadata.version(p) for p in ("numpy", "matplotlib", "pyyaml")},
            "figures": ["results/monomer-supply.svg", "results/combined-inventory.svg", "results/extension-pp-throughput.svg"],
        },
    }
    with open(RESULTS / "comparison.json", "w", encoding="utf-8") as fh:
        json.dump(rounded(out), fh, indent=2, sort_keys=False)
        fh.write("\n")

    print(f"case verdict: {case_verdict} (target: not achievable; component: {comp['verdict']})")
    for k, c in comp["checks"].items():
        print(f"  {k:30s} ref {c['reference']:>8} ours {c['ours']:>9.4f} dev {c['deviation_rel']:+.2%} tol {c['tolerance_rel']:.0%} {c['status']}")
    for cfg, r in runs.items():
        c = r["combined"]
        print(f"  {cfg:8s} virgin olefin {c['virgin_olefin_bought_kg']:7.1f} kg, exchanged {c['olefin_exchanged_kg']:6.1f} kg, "
              f"net (system expansion) {c['net_virgin_olefin_system_expansion_kg']:7.1f} kg, direct CO2 {c['foreground_direct_co2_kg']:6.1f} kg")
    print(f"  extension: saturation at {ext['saturation_waste_PP_kg']:.0f} kg waste PP")
    print(f"  source check: component {out['provenance']['component_source']['status']}, "
          f"target abstract book {out['provenance']['target_source_abstract_book']['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
