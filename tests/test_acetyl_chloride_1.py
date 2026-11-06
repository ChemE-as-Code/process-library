"""acetyl-chloride-1 (#142): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md and process.yaml are checked against them:

- the yield on acetic acid and PCl3 (92.40 % of theory) and the specific PCl3 use (0.630 kg/kg)
  follow from S1, S3 and S10;
- the one-stage distillate S8 is the 97.3 wt% DESIGN.md states, and the product S10 the
  99.84 wt% with about 366 ppm P;
- the specified splits D101 and K101 close on their inlets, and the lower phase is close to the
  source it is calibrated to (CS 272 248 B2, Example 1, HCl-free);
- R101's vent fraction of acetyl chloride is the one scripts/balance.py estimates;
- the jacket's heating medium stays below the MTT, the still's below the decomposition of
  phosphorous acid, and the cooling check uses the log-mean water temperature;
- the criticality classes D-011 states as possible without a TD24 are the ones core's
  `criticality()` can give; the water and HCl release cases stay among the open items;
- the batch size, the agitator and pump powers and the blocked-vent gas rate follow from the
  recipe core gives, every vent source has an emission exclusion, and the failure of the
  steam-heated warming loop is a release case (review of #393);
- core 1.9.0 (D-014): the models write R101's Q2 and the still's net boil-up Q3 (calculated, at
  their `energy_port`), Q2 is the reactions' heat less the dose warmed and Q3 the distillate's
  latent heat (closed forms from the streams), the reboiler's reflux share Q7 and heat-up Q8 are
  their own assumed streams and keep the 1.8.0 reboiler total, R-101's own evaporative cooling
  that the model leaves out stays within the bound DESIGN.md records, E-103's load Q6 is taken
  per source on the same premise (R-101's gas off the reacting mass, the still's nitrogen, the
  dry purge) while the vent fraction keeps its stated upper bound, and the LCI counts every
  heat stream;
- the vent capacity covers its stated basis, core's gas release at the MTSR and (with core) the
  largest cooling-failure release over the batch with the margin DESIGN.md states, and the
  boiling and water cases beyond it are recorded as a design finding;
- the plant requires cheme-as-code 1.9;
- the process is public with CC-BY-4.0, every library entry is (ADR 0036).
"""

from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acetyl-chloride-1"
MW = {"ACOH": 60.052, "PCL3": 137.324, "ACCL": 78.495, "H3PO3": 81.995, "H2O": 18.015, "HCL": 36.458}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"]}


def _components(state: dict) -> dict[str, float]:
    """kg/h of each component (flow kg/h; mole or mass fractions)."""
    comp, flow = state["composition"], state["flow"]["value"]
    if comp["basis"] == "mass_fraction":
        return {n: flow * x for n, x in comp["values"].items()}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: flow * x * MW[n] / mean for n, x in comp["values"].items()}


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


def test_the_stated_yield_and_pcl3_use_follow_from_the_flowsheet(streams):
    acid = _components(streams["S1"])["ACOH"] / MW["ACOH"]
    pcl3 = _components(streams["S3"])["PCL3"] / MW["PCL3"]
    assert acid / pcl3 == pytest.approx(3.0, rel=1e-5)  # CS 272 248 B2, Example 1
    product = _components(streams["S10"])["ACCL"] / MW["ACCL"]
    assert product / acid == pytest.approx(0.9240, abs=5e-5)
    assert "92.40 % of theory" in _text("DESIGN.md")
    assert "92.4 % of theory" in _text("README.md") and "92.4 % of theory" in _text("process.yaml")
    specific = streams["S3"]["flow"]["value"] / streams["S10"]["flow"]["value"]
    assert specific == pytest.approx(0.630, abs=5e-4)


def test_one_still_stage_is_not_the_product_and_the_column_gives_the_stated_purity(streams):
    s8 = _components(streams["S8"])
    assert s8["ACCL"] / sum(s8.values()) == pytest.approx(0.9731, abs=1e-4)
    assert s8["PCL3"] / sum(s8.values()) == pytest.approx(0.0261, abs=1e-4)
    assert "97.31 wt% acetyl chloride with 2.61 wt% PCl3" in _text("DESIGN.md")
    s10 = _components(streams["S10"])
    assert s10["ACCL"] / sum(s10.values()) == pytest.approx(0.9984, abs=5e-5)
    ppm_p = s10["PCL3"] / sum(s10.values()) * 30.974 / MW["PCL3"] * 1e6
    assert ppm_p == pytest.approx(366, abs=1)


@pytest.mark.parametrize(("inlet", "outlets"), [("S4", ("S6", "S7")), ("S8", ("S10", "S11"))])
def test_the_specified_splits_close_on_their_inlets(streams, inlet, outlets):
    feed = _components(streams[inlet])
    out = {n: sum(_components(streams[o]).get(n, 0.0) for o in outlets) for n in feed}
    for name, value in feed.items():
        assert out[name] == pytest.approx(value, rel=1e-3, abs=1e-4), name


def test_the_lower_phase_is_close_to_the_source_it_is_calibrated_to(streams):
    s7 = _components(streams["S7"])
    total = sum(s7.values())
    # CS 272 248 B2, Example 1: 96 g with about 6 % HCl, 2 % AcCl, 10 % AcOH, the rest H3PO3;
    # the model vents its HCl, so the comparison is HCl-free
    source = {"H3PO3": 82 / 94, "ACOH": 10 / 94, "ACCL": 2 / 94}
    for name, share in source.items():
        assert s7[name] / total == pytest.approx(share, abs=0.01), name
    per_mol = total / (_components(streams["S3"])["PCL3"] / MW["PCL3"])  # g per mol PCl3
    assert per_mol == pytest.approx(96 * 0.94, rel=0.03)


def test_the_vent_fraction_is_the_scripts_estimate(sheet, streams):
    spec = importlib.util.spec_from_file_location("accl_balance", PROCESS / "scripts" / "balance.py")
    balance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(balance)
    recipe = _load("process/recipe.yaml")
    hours = recipe["hours_per_year"]["value"]
    batches = balance.CAPACITY * hours / recipe["batch_size"]["value"]
    inert = _components(streams["S5"])["HCL"] / MW["HCL"] + balance.N2_VENT_NM3_PER_BATCH / 22.414 * batches / hours
    p_cold = balance.psat("ACCL", balance.T_VENT)
    passing = inert * p_cold / (balance.P - p_cold)
    s1, s3 = _components(streams["S1"]), _components(streams["S3"])
    pcl3 = s3["PCL3"] / MW["PCL3"]
    converted = pcl3 - _components(streams["S4"])["PCL3"] / MW["PCL3"]
    formed = 3.0 * (converted - s1["H2O"] / MW["H2O"] / 3.0)
    step = next(s for s in sheet["steps"] if s["id"] == "R101")
    stated = step["batch"]["vent"]["fraction"]["ACCL"]
    assert stated == pytest.approx(passing / formed, rel=0.01)
    assert f"{stated * 100:.3f} %" in _text("DESIGN.md")


def test_heating_media_stay_below_the_stated_limits_and_the_jacket_uses_the_log_mean(sheet):
    step = next(s for s in sheet["steps"] if s["id"] == "R101")
    mtt = step["hazard"]["mtt"]
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["heating_temperature"] < mtt - 2.0  # the tempered water warms the acid below the MTT
    lmtd = (15.0 - 5.0) / math.log(15.0 / 5.0)  # cooling water 298.15 -> 308.15 K against 313.15 K
    assert jacket["coolant_temperature"] == pytest.approx(313.15 - lmtd, abs=0.01)
    lps = next(f for f in sheet["feeds"] if f["id"] == "LPS")
    assert lps["utility"]["supply_temperature"]["value"] < 473.0  # H3PO3 disproportionates at about 200 C


def test_the_mixed_residue_temperature_follows_from_its_inlets(streams):
    t9, t11, t12 = (streams[s]["temperature"]["value"] for s in ("S9", "S11", "S12"))
    assert min(t9, t11) - 0.01 <= t12 <= max(t9, t11) + 0.01


def test_published_public_with_cc_by():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.8.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:5\.5e-4 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 324.15
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 290.0 + 0.25 * i) for i in range(400)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 315.8 K)" in _text("DESIGN.md")


def test_water_ingress_and_the_sources_hcl_are_open_items(streams):
    # 1 kg of water with PCl3 or acetyl chloride: one HCl per water, as gas at 313 K, 101.325 kPa
    volume = 1.0 / MW["H2O"] * 8.314 * 313.15 / 101.325
    assert volume == pytest.approx(1.43, abs=0.005)
    design = _text("DESIGN.md")
    assert "about 1.43 m3 at 313 K" in design
    assert "Loss of the scrubber water while R-101 doses" in design
    # CS 272 248 B2: 6 wt% HCl in 96 g of lower phase per mol PCl3, at this plant's batch
    cycle = _load("process/recipe.yaml")["batch_size"]["value"] / streams["S10"]["flow"]["value"]
    pcl3 = streams["S3"]["flow"]["value"] * cycle / MW["PCL3"]
    assert pcl3 * 0.06 * 96 == pytest.approx(38.6, abs=0.1)
    assert "38.6 kg a batch" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "anti-suck-back" in equipment and "scrubber's water flow" in equipment


def test_the_allocation_shares_are_the_mass_shares_of_the_coproducts(streams):
    allocation = _load("lca/lca.yaml")["allocation"]
    product, crude = streams["S10"]["flow"]["value"], streams["S7"]["flow"]["value"]
    assert allocation["shares"]["ACCL"] == pytest.approx(product / (product + crude), abs=5e-4)
    assert sum(allocation["shares"].values()) == pytest.approx(1.0)


def test_the_scrubber_bleed_is_one_percent_hcl(streams):
    bleed = _components(streams["S16"])
    assert bleed["HCL"] / sum(bleed.values()) == pytest.approx(0.01, abs=1e-4)


# The durations `cheme process recipe` (core v1.8.0) prints for this recipe: the ones "from the
# model" (warming, dosing, post-reaction, distillation) are not in recipe.yaml.
RECIPE_H = {"cycle": 5.781, "heat": 0.537, "dose": 2.0, "react": 0.494, "distil": 2.126, "cool": 0.5}


def _step_hours(recipe: dict, procedure: str, step: str) -> float:
    unit = next(u for u in recipe["unit_procedures"] if u["id"] == procedure)
    return next(s for s in unit["operations"] if s["id"] == step)["duration"]["value"]


def test_the_batch_size_source_states_the_recipes_cycle():
    # Review of #393: the source quoted an earlier 5.503 h cycle and 1439.1 batches.
    batch = _load("process/recipe.yaml")["batch_size"]
    found = re.search(r"over the ([\d.]+) batches the ([\d.]+) h cycle allows, 252\.525 kg/h x ([\d.]+) h", batch["source"])
    assert found, batch["source"]
    batches, cycle, cycle_again = (float(g) for g in found.groups())
    assert cycle == cycle_again == RECIPE_H["cycle"]
    assert 2000e3 / batches == pytest.approx(batch["value"], rel=1e-3)
    assert 252.525 * cycle == pytest.approx(batch["value"], rel=1e-3)


def test_the_agitator_and_pump_powers_follow_from_the_recipes_durations(sheet):
    # Review of #393: P1 and P2 were derived from an earlier recipe (3.54 h, 2.02 h, 2.52 h).
    recipe = _load("process/recipe.yaml")
    links = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}
    r101_on = _step_hours(recipe, "REACT", "charge") + RECIPE_H["heat"] + RECIPE_H["dose"] + RECIPE_H["react"]
    assert links["P1"]["value"] == pytest.approx(4.0 * r101_on / RECIPE_H["cycle"], abs=0.01)
    assert f"{r101_on:.2f} h of R-101's 5.78 h cycle" in links["P1"]["source"]
    still_on = RECIPE_H["distil"] + RECIPE_H["cool"]
    energy = 2.0 * still_on + 1.0 * RECIPE_H["distil"]
    assert links["P2"]["value"] == pytest.approx(energy / RECIPE_H["cycle"], abs=0.01)
    for stated in (f"({still_on:.2f} h)", f"({RECIPE_H['distil']:.2f} h)", f"{energy:.2f} kWh per 5.78 h cycle"):
        assert stated in links["P2"]["source"], stated
    total = sum(links[p]["value"] for p in ("P1", "P2", "P3"))
    assert f"Electricity {total:.2f} kW" in _text("DESIGN.md")


def test_the_blocked_vent_gas_rate_is_stated_in_the_right_unit():
    # Review of #393: core's 1.874e-4 kmol/(s m3) was written as 0.19 mmol/(s m3).
    peak_kmol_s, batch_m3 = 0.0003331, 1.777  # `cheme process recipe`: vent of R101, vessel
    assert peak_kmol_s / batch_m3 == pytest.approx(1.87e-4, abs=5e-7)
    design = _text("DESIGN.md")
    assert "mmol/(s m3)" not in design
    assert "a peak of 1.87e-4 kmol/(s m3), 0.19 mol/(s m3): 0.33 mol/s or about 31 m3/h" in design


def test_every_vent_source_has_an_emission_exclusion():
    # Review of #393: R-101 vents through E-103 to A-101 but no exclusion named it
    # (`cheme.lci-emissions-incomplete`).
    excluded = {tag for e in _load("lca/lca.yaml")["emission_exclusions"] for tag in e.get("equipment", [])}
    assert {"R-101", "E-103", "A-101", "T-101", "T-102"} <= excluded


def test_the_warming_loop_failure_is_a_release_case(sheet):
    # Review of #393: the steam-heated warming loop can push R-101 past its MTT without reaction.
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    steam = next(f for f in sheet["feeds"] if f["id"] == "LPS")["utility"]["supply_temperature"]["value"]
    mtt = next(s for s in sheet["steps"] if s["id"] == "R101")["hazard"]["mtt"]
    duty_kw = jacket["u"] * 4.9 * (steam - mtt) / 1000.0  # 4.9 m2: core's jacket area at the charge
    assert duty_kw == pytest.approx(129.0, abs=1.0)
    assert duty_kw / 30.1 * 3.6 == pytest.approx(15.4, abs=0.2)  # kmol/h of acetyl chloride vapour
    design = _text("DESIGN.md")
    assert "(d) Failure of the warming loop's temperature control" in design
    assert "300 W/(m2 K) x 4.9 m2 x (412 - 324) K = 129 kW" in design
    assert "about 15 kmol/h (1.2 t/h) of acetyl chloride vapour" in design


# ---- core 1.9.0 (D-014) -------------------------------------------------------------------

R_GAS = 8.314  # kJ/(kmol K)
REBOILER_1_8 = 56.3958  # kW, the typed Q3 of core 1.8.0: (1 + R) x latent + heat-up
Q2_HAND_1_8 = 1.2696  # kW, the typed Q2 of core 1.8.0


def _energy(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}


def _step(sheet, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _materials() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


def _balance_module():
    spec = importlib.util.spec_from_file_location("accl_balance_19", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_models_write_q2_and_q3_at_their_energy_ports(sheet):
    duties = _energy(sheet)
    assert _step(sheet, "R101")["energy_port"] == "q"
    assert _step(sheet, "ST101")["energy_port"] == "steam"
    q2, q3 = duties["Q2"], duties["Q3"]
    assert q2["provenance"] == "calculated" and "semibatch duty R101" in q2["source"] and q2.get("fingerprint")
    assert q3["provenance"] == "calculated" and "still duty ST101" in q3["source"] and q3.get("fingerprint")
    assert q2["value"] == pytest.approx(2.67099, abs=1e-5)
    assert q3["value"] == pytest.approx(27.5838, abs=1e-4)
    for qid in ("Q7", "Q8"):
        assert duties[qid]["provenance"] == "assumed" and "scripts/balance.py" in duties[qid]["source"], qid


def test_q2_is_the_reaction_heat_less_the_dose_warmed(streams):
    # ADR 0059: -sum dHr xi + C_dose (T - T_dose), from the streams and reactions.yaml
    heats = {r["id"]: r["heat_of_reaction"]["value"] for r in _load("process/reactions.yaml")["reactions"]}
    cp = {n: c.get("liquid_heat_capacity", 0.0) for n, c in _materials().items()}
    s1, s3, s4 = (_components(streams[s]) for s in ("S1", "S3", "S4"))
    pcl3_in = s3["PCL3"] / MW["PCL3"]
    hyd = s1["H2O"] / MW["H2O"] / 3.0
    accl = pcl3_in - s4["PCL3"] / MW["PCL3"] - hyd
    released = -(heats["ACCL"] * accl + heats["HYD"] * hyd) / 3600.0
    dose = pcl3_in * cp["PCL3"] * (313.15 - 298.15) / 3600.0
    assert released == pytest.approx(3.2503, abs=1e-4) and dose == pytest.approx(0.5793, abs=1e-4)
    assert streams["Q2"]["duty"]["value"] == pytest.approx(released - dose, rel=1e-4)
    # the 1.8.0 hand value deducted 1.40 kW of vapour latent heat and condensate rewarming
    assert released - dose - Q2_HAND_1_8 == pytest.approx(1.4014, abs=1e-3)
    design = _text("DESIGN.md")
    assert "The typed Q2, 1.2696 kW, against the semi-batch model's 2.67099 kW" in design
    assert "(1.2028 kW), and that vapour's condensate returned cold and rewarmed (0.1986 kW)" in design


def test_q3_is_the_distillates_latent_heat_and_the_reboiler_keeps_its_total(streams):
    hvap = {n: c.get("heat_of_vaporization", 0.0) for n, c in _materials().items()}
    latent = sum(v / MW[n] * hvap[n] for n, v in _components(streams["S8"]).items()) / 3600.0
    q3, q7, q8 = (streams[q]["duty"]["value"] for q in ("Q3", "Q7", "Q8"))
    assert q3 == pytest.approx(latent, rel=1e-4)
    assert q7 == pytest.approx(_balance_module().REFLUX * latent, rel=1e-4)  # reflux ratio 1 (D-008)
    # the heat-up: the charge to its first bubble point, the residue on to the last
    cp = {n: c.get("liquid_heat_capacity", 0.0) for n, c in _materials().items()}
    rate = lambda sid: sum(v / MW[n] * cp[n] for n, v in _components(streams[sid]).items())  # noqa: E731
    t0, t1 = streams["S8"]["temperature"]["value"], streams["S9"]["temperature"]["value"]
    heat_up = (rate("S6") * (t0 - 313.15) + rate("S9") * (t1 - t0)) / 3600.0
    assert q8 == pytest.approx(heat_up, abs=2e-4)
    assert q3 + q7 + q8 == pytest.approx(REBOILER_1_8, abs=2e-4)
    design = _text("DESIGN.md")
    assert "The typed Q3, 56.3958 kW, against the still model's 27.5838 kW" in design
    assert "Q7 27.5838 kW (the reflux share) and Q8 1.2282 kW (the heat-up)" in design


def test_r101s_own_evaporative_cooling_is_within_the_recorded_bound(streams, capsys, monkeypatch):
    monkeypatch.delenv("BALANCE_OUTPUT", raising=False)
    balance = _balance_module()
    balance.main()
    out = capsys.readouterr().out
    found = re.search(r"gas off the reacting mass ([\d.]+) kmol/h \(([\d.]+) of E-103's inert\), net ([\d.]+) kW \(([\d.]+)% of Q2\)", out)
    assert found, out
    share, kw, percent = float(found.group(2)), float(found.group(3)), float(found.group(4))
    # the HCl and the head space the dose displaces, of the HCl and the batch's nitrogen
    displaced = _components(streams["S3"])["PCL3"] / MW["PCL3"] * _materials()["PCL3"]["liquid_molar_volume"]
    gas = 101.325 * displaced / (R_GAS * 313.15)
    hcl = _components(streams["S5"])["HCL"] / MW["HCL"]
    assert hcl + gas == pytest.approx(0.0119, abs=2e-4)  # the vapour is subtracted in the script
    assert share == pytest.approx(0.1336, abs=5e-4)
    assert kw <= 0.19 and percent == pytest.approx(7.0, abs=0.05)
    assert kw / streams["Q2"]["duty"]["value"] * 100 == pytest.approx(percent, abs=0.05)
    design = _text("DESIGN.md")
    assert "at most 0.19 kW (7 % of Q2" in design
    assert "0.0093 kmol/h (13.4 % of the inert)" in design and "at most 0.187 kW, 7.0 %" in design


def test_e103s_load_is_taken_per_source_and_the_vent_fraction_is_its_upper_bound(sheet, streams, capsys, monkeypatch):
    # Review of #393: on Q2's premise only R-101's HCl and displaced head space leave the
    # reacting mass; the still's and receivers' 3 Nm3 leave over the product at 303 K, and
    # R-101's 5 Nm3 purge runs dry before the charge
    balance = _balance_module()
    assert balance.N2_R101_PURGE_NM3_PER_BATCH == 5.0 and balance.N2_STILL_NM3_PER_BATCH == 3.0
    recipe = _load("process/recipe.yaml")
    per_nm3 = balance.CAPACITY / recipe["batch_size"]["value"] / 22.414  # kmol/h per Nm3 a batch
    hvap = {n: c.get("heat_of_vaporization", 0.0) for n, c in _materials().items()}
    p_cold = balance.psat("ACCL", 268.15)

    def moles(sid):
        kmols = {n: v / MW[n] for n, v in _components(streams[sid]).items()}
        return {n: v / sum(kmols.values()) for n, v in kmols.items()}

    def source(inert, liquid, t):
        p = {n: liquid.get(n, 0.0) * balance.psat(n, t) for n in ("ACCL", "PCL3", "ACOH")}
        vap = {n: inert * pi / (101.325 - sum(p.values())) for n, pi in p.items()}
        passing = inert * p_cold / (101.325 - p_cold)
        heat = (vap["ACCL"] - passing) * hvap["ACCL"] + vap["ACOH"] * hvap["ACOH"]
        heat += (inert * 29.1 + sum(vap.values()) * 67.8) * (t - 268.15)
        return heat / 3600.0, passing, sum(p.values())

    hcl = _components(streams["S5"])["HCL"] / MW["HCL"]
    _, _, p_upper = source(1.0, moles("S6"), 313.15)
    displaced = _components(streams["S3"])["PCL3"] / MW["PCL3"] * _materials()["PCL3"]["liquid_molar_volume"]
    r101_gas = hcl + 101.325 * displaced / (R_GAS * 313.15) * (1.0 - p_upper / 101.325)
    r101, pass_r101, _ = source(r101_gas, moles("S6"), 313.15)
    still, pass_still, _ = source(3.0 * per_nm3, moles("S10"), 303.15)
    purge = 5.0 * per_nm3 * 29.1 * (298.15 - 268.15) / 3600.0
    q6 = streams["Q6"]["duty"]["value"]
    assert r101 == pytest.approx(0.1713, abs=2e-4) and still == pytest.approx(0.1685, abs=2e-4)
    assert purge == pytest.approx(0.0094, abs=1e-4)
    assert q6 == pytest.approx(r101 + still + purge, abs=2e-4) and q6 == pytest.approx(0.3492, abs=1e-4)
    # the 1.8.0 basis, all the inert saturated over the upper phase at 313 K
    bound, _, _ = source(hcl + 8.0 * per_nm3, moles("S6"), 313.15)
    assert bound == pytest.approx(1.2826, abs=2e-4)
    assert bound - q6 == pytest.approx(0.9334, abs=2e-4)
    # what Q6 still counts twice: R-101's share (in Q2) and the still's (in Q4)
    to_utilities = sum(streams[i]["duty"]["value"] for i in ("Q2", "Q4", "Q5", "Q6"))
    assert to_utilities == pytest.approx(60.54, abs=0.005)
    assert (r101 + still) / to_utilities * 100 == pytest.approx(0.6, abs=0.05)
    # the vent fraction keeps the upper bound; per source it is 0.099 %
    s1, s3 = _components(streams["S1"]), _components(streams["S3"])
    converted = s3["PCL3"] / MW["PCL3"] - _components(streams["S4"])["PCL3"] / MW["PCL3"]
    formed = 3.0 * (converted - s1["H2O"] / MW["H2O"] / 3.0)
    per_source = (pass_r101 + pass_still) / formed
    assert per_source == pytest.approx(0.00099, abs=5e-6)
    stated = _step(sheet, "R101")["batch"]["vent"]["fraction"]["ACCL"]
    assert (stated - per_source) * formed * MW["ACCL"] == pytest.approx(0.29, abs=0.005)
    monkeypatch.delenv("BALANCE_OUTPUT", raising=False)
    balance.main()
    out = capsys.readouterr().out
    assert f"vent fraction {per_source:.6f} (not used: the flowsheet keeps the upper bound" in out
    assert f"Q6 per source {q6:.4f} kW" in out
    design = _text("DESIGN.md")
    assert f"{per_source * 100:.3f} %" in design and "Q6 0.35 kW to brine" in design
    assert "the 1.4014 kW rise of Q2 comes with a 0.9334 kW cut of Q6" in design
    assert "at most 0.34 kW, 0.6 % of the 60.54 kW to cooling water and brine" in design
    assert "likely below" not in design  # the 4.7/68 kPa ratio does not cover the head space
    vent_source = _step(sheet, "R101")["batch"]["source"]
    assert "an upper bound" in vent_source and "per source about 0.099 %" in vent_source
    assert "the HCl and the nitrogen carry" not in vent_source


def test_every_heat_stream_reaches_the_lci(streams):
    rows = {r.split(",")[0]: r.split(",") for r in (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()[1:]}
    duty = lambda *ids: sum(streams[i]["duty"]["value"] for i in ids)  # noqa: E731
    assert float(rows["feed:LPS"][5]) == pytest.approx(duty("Q1", "Q3", "Q7", "Q8"), abs=1e-3)
    assert rows["feed:LPS"][-1].split() == ["Q1", "Q3", "Q7", "Q8"]
    assert float(rows["product:CW"][5]) == pytest.approx(duty("Q2", "Q4", "Q5"), abs=1e-3)
    product = streams["S10"]["flow"]["value"]
    assert duty("Q2", "Q4", "Q5") / product == pytest.approx(0.2384, abs=5e-5)
    assert duty("Q1", "Q3", "Q7", "Q8") / product == pytest.approx(0.2304, abs=5e-5)
    assert "0.238 kWh/kg removed by cooling water" in _text("process.yaml")
    assert "cooling water 0.238 kWh removed" in _text("DESIGN.md")
    # the brine: E-103's Q6 per source (review of #393), 0.0051 kWh/kg on the 1.8.0 basis
    assert float(rows["product:BRINE"][5]) == pytest.approx(duty("Q6"), abs=1e-4)
    assert duty("Q6") / product == pytest.approx(0.0014, abs=5e-5)
    assert "0.0014 kWh/kg removed by brine" in _text("process.yaml")
    assert "brine 0.0014 kWh removed (0.0051 until core 1.9.0, D-014)" in _text("DESIGN.md")


# The vent's basis and the cooling-failure releases (core 1.9.0, scratch copies for k/10 and
# k/100, 2026-11-06): m3/h of gas at the MTSR and the largest over the batch (D-011, D-014).
RELEASE = {"design": (0.41, 31.2), "k/10": (0.53, 37.2), "k/100": (0.46, 37.9)}


def test_the_vent_capacity_covers_its_basis_and_the_cooling_failures(sheet):
    hazard = _step(sheet, "R101")["hazard"]
    capacity = hazard["vent_capacity"]
    assert capacity == 50.0 and hazard["provenance"] == "assumed" and "D-014" in hazard["source"]
    peak = 0.0003331 * R_GAS * 313.15 / 101.325 * 3600.0  # `cheme process recipe`: the vent's peak
    assert peak == pytest.approx(30.8, abs=0.05)
    source_hcl = 38.6 / MW["HCL"] / 2.0 * R_GAS * 313.15 / 101.325  # CS 272 248 B2's HCl over 2 h
    assert source_hcl == pytest.approx(13.6, abs=0.05)
    assert peak + source_hcl == pytest.approx(44.4, abs=0.05) and peak + source_hcl < capacity
    design = _text("DESIGN.md")
    for case, (at_mtsr, largest) in RELEASE.items():
        assert largest < capacity and at_mtsr < capacity, case
        label = "5.5e-4 (design)" if case == "design" else case
        assert re.search(rf"\| {re.escape(label)} \|[^\n]*\| {at_mtsr:.2f} m3/h \| {largest:.1f} m3/h at \d+ s, {largest / capacity:.2f} \|", design), case
    # the line from R-101 to E-103 with the acetic acid's vapour at the HCl peak
    vapour = _balance_module().psat("ACOH", 313.15) / 101.325
    assert vapour == pytest.approx(0.047, abs=0.001)
    assert capacity / (1.0 - vapour) == pytest.approx(52.5, abs=0.5)
    assert "sized for about 53 m3/h (for example DN50, about 6.8 m/s)" in design
    assert 52.5 / 3600.0 / (math.pi / 4 * 0.0525**2) == pytest.approx(6.8, abs=0.1)


def test_the_cases_beyond_the_vent_are_a_design_finding(sheet):
    capacity = _step(sheet, "R101")["hazard"]["vent_capacity"]
    design = _text("DESIGN.md")
    assert "Design finding: the vent covers every cooling failure core screens, but not the boiling and water cases." in design
    # (d) the warming loop's steam valve open: 129 kW (72 kW for a loop at 373 K) at 30.1 kJ/mol
    for kw, m3_h, ratio in ((129.0, 410, 8.2), (72.0, 229, 4.6)):
        volume = kw / 30.1 * 3.6 * R_GAS * 324.15 / 101.325
        assert volume == pytest.approx(m3_h, abs=1.0) and volume / capacity == pytest.approx(ratio, abs=0.05)
    assert "about 410 m3/h of acetyl chloride vapour at 324 K (229 m3/h for a loop at 373 K), 8.2 (4.6) times" in design
    # (a) water: 1.43 m3 of HCl per kg, the vent's room at the HCl peak and otherwise
    per_kg = 1.0 / MW["H2O"] * R_GAS * 313.15 / 101.325
    assert (capacity - RELEASE["design"][1]) / per_kg == pytest.approx(13, abs=0.5)
    assert capacity / per_kg == pytest.approx(35, abs=0.5)
    assert "a jacket leak of about 13 kg/h of water at the start of the dosing (35 kg/h otherwise)" in design
    # (1) k/100: the boil-off at the MTT, 5.45 kW at 30.1 kJ/mol, against E-103's year average
    kmol_h = 5.45 / 30.1 * 3.6
    assert kmol_h == pytest.approx(0.65, abs=0.01)
    assert kmol_h * R_GAS * 324.15 / 101.325 == pytest.approx(17.3, abs=0.1)
    q6 = next(s for s in sheet["streams"] if s["id"] == "Q6")["state"]["design"]["duty"]["value"]
    assert 5.45 / q6 == pytest.approx(15.6, abs=0.06)
    assert 5.45 / 1.2826 == pytest.approx(4.2, abs=0.06)  # against the 1.8.0 upper bound
    assert "15.6 times E-103's year-average 0.35 kW (4.2 times the 1.28 kW upper bound of D-010)" in design
    assert "relief device" in design and "interlocked on R-101's pressure" in design


def test_core_screens_the_gas_release_against_the_vent():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.chemistry.thermochemistry import R
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.recipe import hours_per_batch
    from chemeascode.domains.process.stirred_tank import solve_node, vent_gas_rate
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(0.4057, abs=1e-3)
    assert gas["vent_capacity_m3_h"] == 50.0 and gas["capacity_ratio"] < 0.01
    assert entry.mtsr == pytest.approx(315.79, abs=0.01) and entry.mtt == pytest.approx(324.15)
    assert not [f for f in report.findings if f.level in ("warning", "error")]
    # the largest release over the batch: vent_gas_rate at every point of the cooling profile
    process, _ = load(PROCESS)
    case = process.flowsheet.default_case()
    hours = hours_per_batch(process, case)
    item = process.nodes["R101"]
    inlets = [
        s
        for s in process.flowsheet.streams
        if s.kind == "material" and (end := process.ends(s)[1]) is not None and end.node == "R101"
    ]
    solved, _ = solve_node(process, item, inlets, case)
    best = max(
        (
            hours * vent_gas_rate(process, item, p.moles, p.mtsr(), solved.pressure) * R * p.mtsr() / solved.pressure * 3600.0,
            p.time,
        )
        for p in solved.cooling_profile
    )
    assert best[0] == pytest.approx(RELEASE["design"][1], abs=0.05) and best[1] == pytest.approx(69, abs=1)
    assert best[0] / 50.0 == pytest.approx(0.62, abs=0.005)


def test_requires_core_1_9():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.9"
    assert "Needs cheme-as-code 1.9.0" in _text("README.md") and "Needs cheme-as-code 1.9.0" in _text("process.yaml")
    assert "## Core features used (core 1.9.0)" in (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    assert "L-9 (resolved in core 1.9.0, ADR 0059" in _text("DESIGN.md")
