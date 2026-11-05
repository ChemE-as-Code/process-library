"""The LCA of the two pilot skids (#331): step 20 of scripts/regen.py and the arithmetic it records.

After the calculation record (step 16), one regeneration also keeps the LCA of the design current
(DESIGN.md D-024 to D-027):

1. the values lca/lca.yaml takes from the design, by targeted edits (scripts/_yamledit.py):
   ``functional_unit.kg_per_unit`` (1 / w_CO of the CO product the balance wrote), the
   consumables' ``per_replacement`` (cells x cell area x the ASSUMED areal mass of each part) and
   ``every_years`` (the stacks' replacement interval over the operating hours), and
   ``operation.hours_per_year``;
2. core's LCA: ``cheme assess lca --write`` (lca/dataset.yaml, inventory, results, gaps,
   manifest: case skid-a, Skid A), ``--write --case skid-b`` (Skid B's own dataset in
   lca/datasets/, core ADR 0045), ``cheme assess lca-scenarios --write`` (lca/scenarios/), and the
   readings ``cheme assess lca --json``, ``--balance --json`` (Skid B's in a temporary copy whose
   lca.yaml studies case skid-b: ``--balance`` takes no ``--case``) and ``lca-cases --json``;
3. the scenario's LCA record results/scenarios/<H>h/lca.json: per skid every exchange per kg CO
   delivered (with its KOH, K and C where it has a composition), its data class and background
   status, the reconciliation of the datasets against the duty totals of the calculation record
   (E10: the fill, dose, bleed, final inventory and condensate by KOH, K, C and mass, the
   spent inventory's share of the anolyte water, the power and the CO), the spent inventory's
   and the bleed's mass over the duty's volumes against a density band, the K and C balances,
   the run fingerprints and the flowsheet sources that cite them (a run value without a source
   is uncited), the scenario totals and contributions, the gaps (and which are non-zero), the
   KOH solutions' dilution water at the water factor (inside the KOH gaps in core's totals), the
   fossil CO2 the carbonate wastes release when neutralised (inside the waste gaps), the
   duty-sized tanks' volumes, and the inputs of the sensitivities (scripts/lca_sensitivity.py
   writes those into lca/ once both design scenarios have a record).

Reads core only through scripts/_core.py (its commands' --json output); writes nothing outside
lca/ and the scenario's record folder.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import _core
import _results as res
import _yamledit as ye
import yaml

SCHEMA = "process-library/skid-lca/1"
SCENARIO_LCA = "results/scenarios/{h}h/lca.json"
LCA_YAML = "lca/lca.yaml"
#: the files core's LCA writes (compared by regen --check at the design duration)
LCA_OUTPUTS = (
    "lca/dataset.yaml",
    "lca/inventory.csv",
    "lca/results.csv",
    "lca/results.md",
    "lca/gaps.csv",
    "lca/manifest.json",
)
LCA_TREES = ("lca/datasets", "lca/scenarios")
#: the skids: their flowsheet case, the CO product, the PSA tail gas, the streams the duty
#: run fills (their sources cite the run) and the auxiliary power streams
SKIDS = {
    "A": {
        "case": "skid-a", "duty": "D-A", "stack": "STK-A", "pump": "P-101", "product": "S108", "tail": "S109",
        "run_streams": [f"S1{i:02d}" for i in range(1, 19)] + ["Q101", "Q105"],
        "aux": ["Q102", "Q103", "Q104"], "tanks": ["T-101"],
    },
    "B": {
        "case": "skid-b", "duty": "D-B", "stack": "STK-B", "pump": "P-201", "product": "S208", "tail": "S209",
        "run_streams": [f"S2{i:02d}" for i in range(1, 24)] + ["Q201", "Q205"],
        "aux": ["Q202", "Q203", "Q204", "Q206"], "tanks": ["T-201", "T-202"],
    },
}  # fmt: skip
CASE_B = "skid-b"
#: the replaced stack parts (lca/lca.yaml consumables) and their areal mass, kg/m2, all ASSUMED
#: (DESIGN.md D-026): the bipolar membrane about 0.15 mm of ion-exchange polymer; the cathode's
#: 100 nm of Ag (process/design-basis.yaml capacity.reference_cell.cathode) at the bulk density
#: 10.49 g/cm3; the cathode's carbon-paper gas-diffusion layer (Sigracet 39BB, about 0.3 mm with
#: its microporous layer; no datasheet value is used); a nickel foam anode
AREAL_KG_M2 = {
    "membrane-bpm": 0.20, "cathode-gde-ag": 100e-9 * 10.49e3, "cathode-gdl-carbon": 0.10,
    "anode-ni-foam": 0.35,
}  # fmt: skip
#: the make-up water's density, kg/L (scripts/skid_balance.py RHO_WATER)
RHO_WATER = 0.997
#: the band an anolyte leaving the reservoir (spent inventory, bleed) must lie in, kg/L: from
#: water to a concentrated KOH and K2CO3 solution (the 5 M dose is 1.22 kg/L); ASSUMED bounds of a
#: plausibility check of the volumes the duty gives against the masses the balance writes
DENSITY_BAND_KG_L = (RHO_WATER, 1.35)
#: lower heating values, kJ/mol: CO 282.98 (process/reactions.yaml COX, CODATA), H2 241.826
#: (CODATA Key Values, Cox, Wagman, Medvedev 1989: dfH(H2O, g) = -241.826 kJ/mol)
LHV_KJ_MOL = {"CO": 282.98, "H2": 241.826}
#: the reconciliation tolerances (E10): the datasets against the duty totals, and core's
#: lca-cases rows, which print 6 significant figures
REL = 1e-6
REL_CASES = 1e-5
#: what each exchange's amount rests on (lca/README.md, DESIGN.md D-025): measured (the 4TU
#: series: U, FE, WDE and Cx), design estimate (the duty, the stack, the conditioning, the parts),
#: background (an open profile, published or proxy) or none
DATA_CLASS = {
    "feed:POWER": "design estimate: the stacks' DC power from the measured U at the measured FE (stack sizing), the rectifier at 0.95 and the auxiliaries ESTIMATE",
    "feed:CO2": "design estimate: 10 sccm/cm2 (the bench ratio) less the CO, the co-ion carbon (measured WDE and Cx) and the ASSUMED 0.95 recycle",
    "feed:WATER": "design estimate: saturation, condensate and hydrogen evolution (measured FE H2); Skid B's make-up from the duty",
    "feed:AIR": "design estimate: twice the stoichiometric air of the tail gas",
    "feed:KOH-FILL": "design estimate: the duty's initial fill (Skid A sized to the horizon at the measured WDE and Cx)",
    "feed:KOH-DOSE": "design estimate: the duty's dosed solution at the ASSUMED setpoints (measured WDE and Cx)",
    "product:CO": "design estimate: the measured FE CO at the ASSUMED recovery 0.90",
    "product:VENT": "design estimate: the ASSUMED 0.05 of the unreacted CO2 not recycled and the CO not recovered",
    "product:O2VENT": "design estimate: the anode O2 of the overall reactions (measured FE)",
    "product:BLEED": "design estimate: the duty's bleed by route (measured WDE and Cx)",
    "product:SPENT": "design estimate: the duty's final inventory by route",
    "product:CONDENSATE": "design estimate: the measured K+ share of the co-ion current at an ASSUMED 1 mol/kg",
    "product:CW": "design estimate: the stack heat from the measured U and FE (isothermal by assumption)",
    "consumable": "design estimate: cells x area x ASSUMED areal mass, at the ASSUMED 4000 h interval",
}
#: the formulas of the components, for K and C per kg (process/materials.yaml has them too)
ELEMENTS = {
    "KOH": {"K": 1}, "K2CO3": {"K": 2, "C": 1}, "KHCO3": {"K": 1, "C": 1}, "CO2": {"C": 1},
    "CO": {"C": 1},
}  # fmt: skip


class LcaError(RuntimeError):
    """The LCA cannot be reconciled with the design (a finding of the run, exit 1)."""


def _load(root: Path, rel: str) -> Any:
    return yaml.safe_load((root / rel).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(a: float, b: float) -> float:
    scale = max(abs(a), abs(b))
    return 0.0 if scale == 0 else abs(a - b) / scale


def _molar_masses(root: Path) -> dict[str, float]:
    return {c["id"]: float(c["molar_mass"]) for c in _load(root, "process/materials.yaml")["components"]}


def _state(flowsheet: dict, sid: str, case: str) -> dict:
    stream = next(s for s in flowsheet["streams"] if s["id"] == sid)
    return stream["state"][case]


def case_dataset_path(root: Path) -> Path:
    """Skid B's dataset, written by ``cheme assess lca --write --case skid-b``."""
    found = sorted((root / "lca" / "datasets").glob(f"*-{CASE_B}.yaml"))
    if len(found) != 1:
        raise LcaError(f"lca/datasets/: expected one *-{CASE_B}.yaml, found {[p.name for p in found]}")
    return found[0]


# -- 1: the values lca/lca.yaml takes from the design ----------------------------------------


def scope_values(root: Path, stacks: dict[str, dict]) -> dict[str, Any]:
    """kg_per_unit, the consumables' amounts and the operating hours from the design as it is.

    *stacks*: the ``cheme process stack --json`` entries of STK-A and STK-B."""
    flowsheet = _load(root, "process/flowsheet.yaml")
    w = {}
    for key, skid in SKIDS.items():
        comp = _state(flowsheet, skid["product"], skid["case"])["composition"]
        if comp.get("basis") != "mass_fraction":
            raise LcaError(f"{skid['product']}: composition basis {comp.get('basis')}, not mass_fraction")
        w[key] = float(comp["values"]["CO"])
    if _rel(w["A"], w["B"]) > 1e-9:
        raise LcaError(f"the CO products differ: w_CO {w['A']} (S108) and {w['B']} (S208)")
    cells_cfg = {s["id"]: s for s in _load(root, "process/cells.yaml")["stacks"]}
    per_skid = []
    rho_anolyte: dict[str, float] = {}
    for key, skid in SKIDS.items():
        st = stacks[skid["stack"]]
        rep = cells_cfg[skid["stack"]]["replacement"]
        if rep["interval"]["unit"] != "h" or rep["operating_hours"]["unit"] != "h/a":
            raise LcaError(f"{skid['stack']}: replacement units {rep['interval']['unit']}, {rep['operating_hours']['unit']}")
        rho = _core.equipment_number(st, skid["pump"], "density_kg_m3")
        if rho is None:
            raise LcaError(f"{skid['stack']}: the stack report gives no density of {skid['pump']}")
        rho_anolyte[key] = float(rho) / 1000.0
        per_skid.append(
            (
                int(_core.stack_value(st, "cells_total")),
                float(st["point"]["area_m2"]),
                float(rep["interval"]["value"]),
                float(rep["operating_hours"]["value"]),
            )
        )
    if per_skid[0] != per_skid[1]:
        raise LcaError(f"the stacks differ ({per_skid}): the study-level consumables need identical stacks")
    cells, area_m2, interval_h, hours = per_skid[0]
    replaced_m2 = cells * area_m2
    return {
        "kg_per_unit": 1.0 / w["A"],
        "w_co": w["A"],
        "cells": cells,
        "cell_area_m2": area_m2,
        "replaced_m2": replaced_m2,
        "interval_h": interval_h,
        "hours_per_year": hours,
        "rho_anolyte_kg_l": rho_anolyte,
        "consumables": {
            cid: {
                "per_replacement": replaced_m2 * kg_m2,
                "every_years": interval_h / hours,
                "areal_kg_m2": kg_m2,
            }
            for cid, kg_m2 in AREAL_KG_M2.items()
        },
    }


def sync_scope(root: Path, values: dict[str, Any]) -> bool:
    """Write *values* into lca/lca.yaml (targeted edits); True when the file changed."""
    changes: list = [
        (["functional_unit", "kg_per_unit"], round(values["kg_per_unit"], 9)),
        (["operation", "hours_per_year"], int(h) if (h := values["hours_per_year"]).is_integer() else h),
    ]
    for cid, c in values["consumables"].items():
        changes.append((["consumables", ("id", cid), "per_replacement"], float(f"{c['per_replacement']:.8g}")))
        changes.append((["consumables", ("id", cid), "every_years"], float(f"{c['every_years']:.8g}")))
    scope = _load(root, LCA_YAML)
    have = {cid: c for cid, c in ((c["id"], c) for c in scope.get("consumables") or [])}
    missing = set(values["consumables"]) - set(have)
    if missing:
        raise LcaError(f"lca/lca.yaml has no consumable {', '.join(sorted(missing))}")
    return ye.edit_file(root / LCA_YAML, changes)


# -- 2: core's LCA -----------------------------------------------------------------------------


def _json(result: _core.Result) -> Any:
    return result.json()


def run_core(root: Path) -> dict[str, Any]:
    """Write the LCA outputs and read core's JSON (the study's case, Skid B's balance)."""
    _core.cheme(root, "assess", "lca", "--write")
    # a case dataset of an earlier flowsheet title would be left beside the new one: remove it
    for stale in (root / "lca" / "datasets").glob(f"*-{CASE_B}.yaml"):
        stale.unlink()
    _core.cheme(root, "assess", "lca", "--write", "--case", CASE_B)
    _core.cheme(root, "assess", "lca-scenarios", "--write")
    out = {
        "lca": _json(_core.cheme(root, "assess", "lca", "--json")),
        "balance": {"A": _json(_core.cheme(root, "assess", "lca", "--balance", "--json"))},
        "cases": _json(_core.cheme(root, "assess", "lca-cases", "--json")),
    }
    # --balance takes no --case: Skid B's in a copy whose lca.yaml studies case skid-b
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / root.name
        keep = ("process", "lca", "equipment", "plant.yaml", "process.yaml")
        copy.mkdir()
        for rel in keep:
            src = root / rel
            if src.is_dir():
                shutil.copytree(src, copy / rel)
            elif src.exists():
                shutil.copyfile(src, copy / rel)
        ye.edit_file(copy / LCA_YAML, [(["case"], CASE_B)])
        out["balance"]["B"] = _json(_core.cheme(copy, "assess", "lca", "--balance", "--json"))
    return out


# -- 3: per kg CO, the reconciliation, the record --------------------------------------------


def per_kg(dataset: dict, kg_per_unit: float, molar: dict[str, float]) -> dict[str, Any]:
    """Every exchange of a dataset per kg CO delivered (the functional unit)."""
    ref = next(e for e in dataset["exchanges"] if e["key"] == "product:CO")
    co_kg_h = float(ref["amount"]) / kg_per_unit
    rows: dict[str, dict] = {}
    for e in dataset["exchanges"]:
        if e["key"] == "product:CO":
            continue
        amount = float(e["amount"]) / co_kg_h
        row: dict[str, Any] = {"amount": amount, "unit": f"{e['unit']}/kg CO", "type": e.get("type")}
        comp = (e.get("composition") or {}).get("fractions")
        if comp and e["unit"] == "kg":
            row["components_kg"] = {c: amount * float(x) for c, x in comp.items()}
            k = sum(amount * float(x) * 1000 / molar[c] * ELEMENTS.get(c, {}).get("K", 0) for c, x in comp.items())
            cc = sum(amount * float(x) * 1000 / molar[c] * ELEMENTS.get(c, {}).get("C", 0) for c, x in comp.items())
            row["k_mol"] = k
            row["c_mol"] = cc
        rows[e["key"]] = row
    fractions = (ref.get("composition") or {}).get("fractions") or {}
    product_c = sum(kg_per_unit * float(x) * 1000 / molar[c] * ELEMENTS.get(c, {}).get("C", 0) for c, x in fractions.items())
    return {"co_kg_h": co_kg_h, "product_kg_h": float(ref["amount"]), "product_c_mol": product_c, "exchanges": rows}


def _get(rows: dict, key: str, field: str = "amount") -> float:
    row = rows.get(key)
    if row is None:
        return 0.0
    if field.startswith("components_kg."):
        return float((row.get("components_kg") or {}).get(field.split(".", 1)[1], 0.0))
    return float(row.get(field) or 0.0)


def _water_share(ex: dict) -> float:
    """The spent inventory's share of the water that leaves the reservoir as liquid."""
    spent, bleed = _get(ex, "product:SPENT", "components_kg.H2O"), _get(ex, "product:BLEED", "components_kg.H2O")
    return spent / (spent + bleed) if spent + bleed else 0.0


def reconcile(rows: dict, record: dict, key: str, aux_kw: float, eta: float, molar: dict, rho_fill: float) -> list[dict]:
    """The dataset per kg CO against the duty totals over the CO delivered (E10, rel 1e-6).

    *rho_fill*: the anolyte density the fill is made at, kg/L (the recirculation pump's)."""
    s = record["skids"][key]
    did = SKIDS[key]["duty"]
    t = record["duties"][did]["totals"]
    hours = float(s["duty_result"]["operating_time_h"])
    delivered = float(s["totals_delivered_kg"])
    m_koh = molar["KOH"] * 1e-3
    ex = rows["exchanges"]
    pairs = (
        ("electricity: DC / rectifier efficiency + auxiliaries", _get(ex, "feed:POWER"), (t["energy_kwh"] / eta + aux_kw * hours) / delivered, "kWh"),
        ("KOH fill (KOH 100 %)", _get(ex, "feed:KOH-FILL", "components_kg.KOH"), t["initial_cation_mol"] * m_koh / delivered, "kg"),
        ("fill solution (initial volume x anolyte density)", _get(ex, "feed:KOH-FILL"), t["initial_volume_l"] * rho_fill / delivered, "kg"),
        ("KOH dosed (KOH 100 %)", _get(ex, "feed:KOH-DOSE", "components_kg.KOH"), t["dosing_hydroxide_kg"] / delivered, "kg"),
        ("dosing solution", _get(ex, "feed:KOH-DOSE"), (t["dosing_solution_kg"] or 0.0) / delivered, "kg"),
        ("bleed K", _get(ex, "product:BLEED", "k_mol"), t["bleed_cation_mol"] / delivered, "mol"),
        ("bleed C", _get(ex, "product:BLEED", "c_mol"), t["bleed_carbon_mol"] / delivered, "mol"),
        ("final inventory K", _get(ex, "product:SPENT", "k_mol"), t["final_cation_mol"] / delivered, "mol"),
        ("final inventory C", _get(ex, "product:SPENT", "c_mol"), t["final_carbon_mol"] / delivered, "mol"),
        ("condensate K (the K+ through the membrane)", _get(ex, "product:CONDENSATE", "k_mol"), t["membrane_cation_mol"] / delivered, "mol"),
        ("spent inventory's share of the anolyte water out (final volume over final volume + bleed)", _water_share(ex),
         t["final_volume_l"] / (t["final_volume_l"] + t["bleed_l"]) if t["final_volume_l"] + t["bleed_l"] else 0.0, "1"),
        ("CO delivered", rows["co_kg_h"] * hours, delivered, "kg per campaign"),
    )  # fmt: skip
    out = []
    for what, lca, duty, unit in pairs:
        r = _rel(lca, duty)
        shown = unit if "campaign" in unit or unit == "1" else f"{unit}/kg CO"
        out.append({"quantity": what, "lca": lca, "duty": duty, "unit": shown, "rel": r, "ok": r <= REL})
    return out


def densities(rows: dict, record: dict, key: str) -> list[dict]:
    """The spent inventory's and the bleed's mass over the duty's volumes, kg/L, against
    DENSITY_BAND_KG_L: the masses come from the water balance (scripts/skid_balance.py), the
    volumes from the duty, so a volume or density error shows here."""
    t = record["duties"][SKIDS[key]["duty"]]["totals"]
    delivered = float(record["skids"][key]["totals_delivered_kg"])
    lo, hi = DENSITY_BAND_KG_L
    out = []
    for what, ex_key, litres in (("spent inventory", "product:SPENT", t["final_volume_l"]), ("bleed", "product:BLEED", t["bleed_l"])):
        if not litres:
            continue
        kg_l = _get(rows["exchanges"], ex_key) * delivered / float(litres)
        out.append({"quantity": what, "exchange": ex_key, "litres": float(litres), "kg_l": kg_l, "band_kg_l": [lo, hi], "ok": lo <= kg_l <= hi})
    return out


def data_class(key: str) -> str:
    kind = key.split(":")[0]
    if kind in ("consumable", "disposal"):
        return DATA_CLASS["consumable"]
    if kind == "emission":
        return "design estimate: the vents' composition (" + DATA_CLASS["product:VENT"].split(": ", 1)[1] + ")"
    return DATA_CLASS.get(key, "design estimate")


def balances(rows: dict, molar: dict[str, float]) -> dict[str, Any]:
    """K and C by route from the dataset's compositions (per kg CO): fill + dose = bleed +
    spent + condensate; CO2 fed = C in the CO + the anolyte (spent, bleed) + the condensate +
    the CO2 vented."""
    ex = rows["exchanges"]
    k_in = _get(ex, "feed:KOH-FILL", "k_mol") + _get(ex, "feed:KOH-DOSE", "k_mol")
    k_out = sum(_get(ex, k, "k_mol") for k in ("product:BLEED", "product:SPENT", "product:CONDENSATE"))
    c_in = _get(ex, "feed:CO2", "c_mol")
    c_routes = {
        "product": rows["product_c_mol"],
        "anolyte": _get(ex, "product:SPENT", "c_mol") + _get(ex, "product:BLEED", "c_mol"),
        "condensate": _get(ex, "product:CONDENSATE", "c_mol"),
        "vented": _get(ex, "emission:CO2") * 1000 / molar["CO2"],
    }
    c_out = sum(c_routes.values())
    return {
        "k_in_mol": k_in, "k_out_mol": k_out, "k_rel": _rel(k_in, k_out), "k_closed": _rel(k_in, k_out) <= REL,
        "c_fed_mol": c_in, "c_routes_mol": c_routes, "c_rel": _rel(c_in, c_out), "c_closed": _rel(c_in, c_out) <= REL,
        "c_shares": {k: v / c_in for k, v in c_routes.items()} if c_in else {},
    }  # fmt: skip


def _core_balance(doc: dict) -> dict[str, Any]:
    """What core's --balance says about K and C (the assessable exchanges)."""
    el = doc.get("elements") or {}
    carbon = doc.get("carbon") or {}
    return {
        "status": doc.get("status"),
        "k_closed": bool((el.get("K") or {}).get("closed")),
        "c_closed": bool((el.get("C") or {}).get("closed")),
        "carbon_by_origin_closed": bool(carbon.get("closed")),
        "carbon_kg_c_h": {"inputs": carbon.get("inputs"), "outputs": carbon.get("outputs")},
        "no_composition": sorted(doc.get("no_composition") or {}),
        "mass_closed": bool((doc.get("mass") or {}).get("closed")),
    }


def _impacts(lca: dict, scenario: str) -> dict[str, Any]:
    contrib = {
        i["key"]: {"value": i["value"], "basis": i["basis"], "status": i["status"]}
        for i in lca.get("impacts") or []
        if i["scenario"] == scenario and i["category"] == "climate-change"
    }
    gaps = {
        g["key"]: {"quantity": g["quantity"], "unit": g["unit"], "reason": g["reason"]}
        for g in lca.get("gaps") or []
        if g["scenario"] == scenario and g["category"] == "climate-change"
    }
    comp = (lca.get("comparability") or {}).get(scenario) or {}
    return {
        "total": ((lca.get("scenarios") or {}).get(scenario) or {}).get("climate-change"),
        "contributions": contrib,
        "gaps": gaps,
        "verdict": comp.get("verdict"),
        "reasons": comp.get("reasons") or [],
        "compared": comp.get("compared") or [],
    }


def _cites(state: dict, sid: str, cite: str) -> bool:
    """True when the stream's run value (a Q stream's duty, a material stream's flow) is there
    and its source cites the run; so does any other of the two the stream has."""
    own = "duty" if sid.startswith("Q") else "flow"
    if not isinstance(state.get(own), dict):
        return False
    for q in ("flow", "duty"):
        if q in state:
            source = (state[q] or {}).get("source") if isinstance(state[q], dict) else None
            if not source or cite not in str(source):
                return False
    return True


#: the KOH solutions' exchanges, whose dilution water core counts inside the KOH gap
SOLUTIONS = ("feed:KOH-FILL", "feed:KOH-DOSE")


def solution_water(rows: dict, impacts: dict) -> dict[str, Any]:
    """The dilution water of the KOH solutions per kg CO, and what it would add at the factor of
    feed:WATER. Core counts an exchange as one flow, so the solutions (KOH and their water) are
    one gap each and their water is not in feed:WATER (DESIGN.md D-025)."""
    ex = rows["exchanges"]
    water = {k: _get(ex, k, "components_kg.H2O") for k in SOLUTIONS}
    contrib = (impacts["contributions"].get("feed:WATER") or {}).get("value")
    amount = _get(ex, "feed:WATER")
    factor = None if contrib is None or not amount else float(contrib) / amount
    total = sum(water.values())
    return {
        "kg_per_kg": water,
        "kg": total,
        "water_factor_kg_co2e_per_kg": factor,
        "kg_co2e": None if factor is None else total * factor,
        "total_with_it": None if factor is None or impacts["total"] is None else impacts["total"] + total * factor,
        "note": "the KOH solutions' dilution water: inside the KOH gaps (core counts each solution as one exchange), not in feed:WATER; here at the feed:WATER factor",
    }


def carbonate_co2(bal: dict, molar: dict[str, float]) -> dict[str, Any]:
    """The fossil carbon the alkaline wastes carry as carbonate (spent anolyte, bleed,
    condensate): released as CO2 when they are neutralised with acid, inside the waste gaps."""
    c = bal["c_routes_mol"]["anolyte"] + bal["c_routes_mol"]["condensate"]
    return {
        "c_mol_per_kg": c,
        "kg_co2_per_kg": c * molar["CO2"] / 1000.0,
        "share_of_co2_fed": c / bal["c_fed_mol"] if bal["c_fed_mol"] else None,
        "note": "fossil CO2 the carbonate wastes release when neutralised (acidified): inside the waste gaps, not counted (no open factor for the treatment)",
    }


def _tanks_m3(skid_record: dict, tags: list[str]) -> dict[str, float]:
    """The duty-sized tanks' held volumes, m3 (the reservoir; Skid B's dosing day tank)."""
    out = {skid_record["reservoir_tag"]: float(skid_record["reservoir_held_m3"])}
    if skid_record.get("dosing_tank_held_l") is not None:
        day = [t for t in tags if t != skid_record["reservoir_tag"]]
        if len(day) != 1:
            raise LcaError(f"the dosing tank of {tags} cannot be told apart from the reservoir")
        out[day[0]] = float(skid_record["dosing_tank_held_l"]) / 1000.0
    return out


def build(root: Path, record: dict, scope: dict[str, Any], core: dict[str, Any]) -> dict[str, Any]:
    """The scenario's LCA record (results/scenarios/<H>h/lca.json)."""
    molar = _molar_masses(root)
    flowsheet = _load(root, "process/flowsheet.yaml")
    cells_cfg = {s["id"]: s for s in _load(root, "process/cells.yaml")["stacks"]}
    listed = {e["tag"]: e for e in _load(root, "equipment/equipment-list.yaml")["equipment"]}
    datasets = {"A": _load(root, "lca/dataset.yaml"), "B": yaml.safe_load(case_dataset_path(root).read_text(encoding="utf-8"))}
    manifest = json.loads((root / "lca" / "manifest.json").read_text(encoding="utf-8"))
    lca = core["lca"]
    status = lca.get("factor_status") or {}
    scenario_of = {"A": "baseline", "B": "skid-b"}
    cases_rows = {row["case"]: row for row in core["cases"]}
    skids: dict[str, Any] = {}
    for key, skid in SKIDS.items():
        case = skid["case"]
        rows = per_kg(datasets[key], scope["kg_per_unit"], molar)
        eta = float(cells_cfg[skid["stack"]]["electrical"]["rectifier_efficiency"]["value"])
        aux = sum(float(_state(flowsheet, q, case)["duty"]["value"]) for q in skid["aux"])
        rec = reconcile(rows, record, key, aux, eta, molar, scope["rho_anolyte_kg_l"][key])
        dens = densities(rows, record, key)
        # core's lca-cases rows (per kg of product gas, 6 significant figures) per kg CO
        case_row = cases_rows[case]["per_unit"]
        cases_check = []
        for k, v in sorted(case_row.items()):
            mine = _get(rows["exchanges"], k)
            theirs = float(v["amount"]) * scope["kg_per_unit"]
            r = _rel(mine, theirs)
            cases_check.append({"key": k, "lca_cases": theirs, "dataset": mine, "rel": r, "ok": r <= REL_CASES or (mine == theirs == 0.0)})
        # the run that sized the equipment: its fingerprint on the duty-sized tanks and in the
        # sources of every flowsheet value the duty run fills
        fp = record["skids"][key]["run_fingerprint"]
        tanks = {tag: listed[tag]["dimensions"].get("fingerprint") for tag in skid["tanks"]}
        cite = f"(run {fp})"
        uncited = [sid for sid in skid["run_streams"] if not _cites(_state(flowsheet, sid, case), sid, cite)]
        h2_kg_h = float(_state(flowsheet, skid["tail"], case)["flow"]["value"]) * float(
            _state(flowsheet, skid["tail"], case)["composition"]["values"].get("H2", 0.0)
        )
        impacts = _impacts(lca, scenario_of[key])
        bal = balances(rows, molar)
        skids[key] = {
            "case": case,
            "dataset": datasets[key]["id"],
            "dataset_uuid": datasets[key].get("uuid"),
            "dataset_title": datasets[key].get("title"),
            "co_delivered_kg_h": rows["co_kg_h"],
            "product_kg_h": rows["product_kg_h"],
            "exchanges": {
                k: dict(r, data_class=data_class(k), status=status.get(scenario_of[key], {}).get(k))
                for k, r in rows["exchanges"].items()
            },
            "reconciliation": rec,
            "reconciled": all(r["ok"] for r in rec),
            "densities": dens,
            "densities_plausible": all(r["ok"] for r in dens),
            "lca_cases": cases_check,
            "lca_cases_agree": all(r["ok"] for r in cases_check),
            "balance": bal,
            "core_balance": _core_balance(core["balance"][key]),
            "run_fingerprint": fp,
            "tank_fingerprints": tanks,
            "tanks_carry_run": all(v == fp for v in tanks.values()),
            "sources_uncited": uncited,
            "h2_tail_kg_per_kg": h2_kg_h / rows["co_kg_h"],
            "impacts": impacts,
            "gaps_nonzero": sorted(k for k, g in impacts["gaps"].items() if g["quantity"]),
            "solution_water": solution_water(rows, impacts),
            "carbonate_co2": carbonate_co2(bal, molar),
            "tanks_m3": _tanks_m3(record["skids"][key], skid["tanks"]),
        }
    a, b = (skids[k]["exchanges"] for k in ("A", "B"))
    makeup = _get(b, "feed:WATER") - _get(a, "feed:WATER")
    t_b = record["duties"]["D-B"]["totals"]
    makeup_duty = t_b["makeup_water_l"] * RHO_WATER / float(record["skids"]["B"]["totals_delivered_kg"])
    skids["B"]["reconciliation"].append(
        {"quantity": "make-up water (Skid B's water less Skid A's)", "lca": makeup, "duty": makeup_duty,
         "unit": "kg/kg CO", "rel": _rel(makeup, makeup_duty), "ok": _rel(makeup, makeup_duty) <= REL}
    )  # fmt: skip
    skids["B"]["reconciled"] = all(r["ok"] for r in skids["B"]["reconciliation"])
    scenarios = {sid: _impacts(lca, sid) for sid in (lca.get("scenario_ids") or [])}
    scenarios["baseline"] = _impacts(lca, "baseline")
    flowsheet_sha = "sha256:" + _sha(root / "process" / "flowsheet.yaml")
    return {
        "schema": SCHEMA,
        "issue": 331,
        "duration_h": record["duration_h"],
        "functional_unit": "1 kg CO delivered (contained in the product at >= 0.99 mol/mol dry, 5.0 bar(a))",
        "kg_per_unit": scope["kg_per_unit"],
        "classification": lca.get("classification"),
        "label": lca.get("label"),
        "reasons": lca.get("reasons"),
        "manifest_flowsheet": manifest["inputs"].get("process/flowsheet.yaml"),
        "manifest_fingerprints_flowsheet": manifest["inputs"].get("process/flowsheet.yaml") == flowsheet_sha,
        "parts": {
            "cells": scope["cells"],
            "cell_area_m2": scope["cell_area_m2"],
            "replaced_m2": scope["replaced_m2"],
            "interval_h": scope["interval_h"],
            "hours_per_year": scope["hours_per_year"],
            "areal_kg_m2": dict(AREAL_KG_M2),
            "rho_anolyte_kg_l": dict(scope["rho_anolyte_kg_l"]),
        },
        "lhv_kj_mol": dict(LHV_KJ_MOL),
        "molar_mass": {c: molar[c] for c in ("CO", "H2", "KOH", "CO2")},
        "skids": skids,
        "scenarios": scenarios,
    }


def step(root: Path, h: float, record: dict, stacks: dict[str, dict]) -> dict[str, Any]:
    """Regen step 20: sync the scope, run core's LCA, write results/scenarios/<H>h/lca.json."""
    scope = scope_values(root, stacks)
    changed = sync_scope(root, scope)
    core = run_core(root)
    doc = build(root, record, scope, core)
    out = root / SCENARIO_LCA.format(h=f"{h:g}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(res.dump(doc), encoding="utf-8")
    return {"path": out, "doc": doc, "scope_changed": changed}
