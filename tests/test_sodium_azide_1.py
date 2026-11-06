"""sodium-azide-1 (#167): the folder's stated numbers and safety claims against its own files.

Fast, without core: the flowsheet, materials, process.yaml and lca.yaml are read as YAML and the
statements the review of process-library#386 found wrong are checked against them:

- the still's residue S17 takes the caustic liquor's boiling-point elevation: at the still's
  pressure water boils at about 319 K (the NIST Antoine data in materials.yaml), and a residue with
  more than 50 wt% NaOH on a NaOH-plus-water basis boils about 40 K above it, so S17 is not the
  335 K of an ideal Raoult trial; Q6, the crystallizer's lumped duty, is the one of S17's
  temperature, and DESIGN.md no longer says the still stays at or below 335 K (or 65 C);
- the HN3 reasoning counts hydrazine with nitrous acid, not only azide with acid: process.yaml does
  not say that no hydrazoic acid can form, DESIGN.md D-015 names hydrazine in the recovered
  methanol S3 as an HN3 path into R-101, with a limit, and the purge's route oxidises the hydrazine
  before the azide is destroyed with nitrite and acid (lca.yaml, DESIGN.md D-015, D-016);
- the purge has no chemical slug in process.yaml, so the Atlas build does not link it to average
  wastewater treatment (it stays a gap, as the off-gas does; DESIGN.md D-013).

Core 1.9.0 (DESIGN.md D-006, D-011, D-012, D-017):

- the two recycles are `tears:` that propagate converges, not hand-converged ASSUMED values: S11
  and S3 are calculated (S3's flow stays an ASSUMED charge ratio), and the fresh feeds' charge
  ratios of D-004 still hold at the converged recycle;
- the reactors', the still's boil-up and the crystallizer's duties are the models' (calculated):
  R-102's Q2 is the heat of AZ and SIDE less the warming of the absorbed methyl nitrite, below the
  126.68 kW typed up to 1.8.0;
- no hand `hazard.mtt`: core's default MTT is methanol's boiling point, in R-102 only because the
  recycled mother liquor brings methanol into the charge (products are not candidates);
- each vented reactor states a vent capacity that passes the methyl nitrite R-101 makes (R-102's
  with the N2O and NH3 still formed; no nitrogen sweep counted), and the gas released at the MTSR
  stays within it (with core, the screening itself); the blocked vent is a recorded finding whose
  pressures follow from core's gas release and the recipe's vessels.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "sodium-azide-1"

#: K, at least the boiling-point elevation of a 50-55 wt% NaOH solution (Duhring lines: about 40 K)
MIN_BPE = 30.0


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").replace("#", " ").split())


def _section(heading: str) -> str:
    """One DESIGN.md decision, its whitespace collapsed."""
    raw = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    start = raw.index(f"## {heading}")
    end = raw.find("\n## ", start + 3)
    return " ".join(raw[start:end if end > 0 else None].split())


@pytest.fixture(scope="module")
def flowsheet() -> dict:
    return _yaml("process/flowsheet.yaml")


def _stream(flowsheet: dict, sid: str) -> dict:
    return next(s for s in flowsheet["streams"] if s["id"] == sid)


def _find(node, bid: str):
    if isinstance(node, dict):
        if node.get("id") == bid and ("still" in node or "crystallizer" in node):
            return node
        for v in node.values():
            found = _find(v, bid)
            if found is not None:
                return found
    elif isinstance(node, list):
        for v in node:
            found = _find(v, bid)
            if found is not None:
                return found
    return None


def _mass_fractions(stream: dict, molar_mass: dict[str, float]) -> dict[str, float]:
    comp = stream["state"]["design"]["composition"]
    assert comp["basis"] == "mole_fraction"
    mass = {k: x * molar_mass[k] for k, x in comp["values"].items()}
    total = sum(mass.values())
    return {k: m / total for k, m in mass.items()}


def test_still_residue_counts_the_boiling_point_elevation(flowsheet):
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    still = _find(flowsheet, "ST101")["still"]
    p_bar = still["pressure"] / 100.0  # kPa(a) -> bar
    vp = materials["H2O"]["vapour_pressure"]
    t_water = vp["b"] / (vp["a"] - math.log10(p_bar)) - vp["c"]
    assert 315.0 < t_water < 322.0, t_water

    s17 = _stream(flowsheet, "S17")
    w = _mass_fractions(s17, {k: c["molar_mass"] for k, c in materials.items()})
    naoh_salt_free = w["NAOH"] / (w["NAOH"] + w["H2O"])
    assert naoh_salt_free > 0.5, naoh_salt_free  # the end liquor is a strong caustic solution

    t17 = s17["state"]["design"]["temperature"]["value"]
    assert t17 >= t_water + MIN_BPE, (
        f"S17 {t17} K: the residue boils at least {MIN_BPE} K above water ({t_water:.1f} K at "
        f"{still['pressure']} kPa(a)) with {naoh_salt_free:.1%} NaOH on a NaOH-plus-water basis"
    )
    assert "boiling-point elevation" in s17["state"]["design"]["temperature"]["source"]


def test_crystallizer_duty_uses_the_still_residue_temperature(flowsheet):
    cr = _find(flowsheet, "CR101")["crystallizer"]
    materials = {c["id"]: c["molar_mass"] for c in _yaml("process/materials.yaml")["components"]}
    s17, s19 = _stream(flowsheet, "S17"), _stream(flowsheet, "S19")
    flow = s17["state"]["design"]["flow"]["value"]  # kg/h
    t17 = s17["state"]["design"]["temperature"]["value"]

    def crystals(s):  # kg/h of NAN3S
        comp = s["state"]["design"]["composition"]["values"]
        mw = sum(x * materials[k] for k, x in comp.items())
        return s["state"]["design"]["flow"]["value"] * comp["NAN3S"] * materials["NAN3S"] / mw

    formed = crystals(s19) - crystals(s17)
    duty = (flow * cr["energy"]["heat_capacity"] * (t17 - cr["temperature"]) - formed * cr["energy"]["heat_of_crystallization"]) / 3600.0
    q6 = next(s for s in flowsheet["streams"] if s["id"] == "Q6")["state"]["design"]["duty"]["value"]
    assert q6 == pytest.approx(duty, rel=0.01), (q6, duty)


def test_design_does_not_claim_the_still_stays_cool():
    text = _text("DESIGN.md")
    for claim in ("below about 65 C", "at or below 335 K", "The still and the dryer stay at"):
        assert claim not in text, f"DESIGN.md still claims: {claim!r}"
    assert "boiling-point elevation" in _section("D-007")


def test_hn3_from_hydrazine_and_nitrous_acid_is_covered():
    assert "no hydrazoic acid can form" not in _text("process.yaml")
    assert "no hydrazoic acid can form" not in _text("DESIGN.md")
    d015 = _section("D-015")
    assert re.search(r"hydrazine in S3 meets nitrous acid in R-101", d015), "D-015: hydrazine in S3 as an HN3 path"
    assert re.search(r"limit on S3.*mg/kg hydrazine", d015), "D-015: a hydrazine limit on the recovered methanol"
    assert "HAZOP" in d015 and "carry-over into S3" in d015


@pytest.mark.parametrize("where", ["lca", "D-015", "D-016"])
def test_purge_oxidises_hydrazine_before_the_azide_is_destroyed(where):
    if where == "lca":
        flows = {f["key"]: f for f in _yaml("lca/lca.yaml")["flows"]}
        text = flows["product:PURGE"]["treatment"]["route"]
    else:
        text = _section(where)
    oxid = re.search(r"oxid\w* (of )?the hydrazine|hydrazine (is )?oxidi[sz]ed", text)
    nitrous = re.search(r"nitrite and acid", text)
    assert oxid and nitrous, f"{where}: the purge's two steps are not both named"
    assert oxid.start() < nitrous.start(), f"{where}: the hydrazine must be oxidised before nitrite and acid"


def test_purge_is_not_linked_as_generic_wastewater():
    manifest = _yaml("process.yaml")
    keys = {item.get("inventory_key") for group in manifest["chemistry"].values() for item in group}
    assert "product:PURGE" not in keys, "process.yaml gives the purge a chemical slug: the Atlas would treat it as average wastewater"
    assert "product:OFFGAS" not in keys
    overrides = (_yaml("lca/mappings.yaml") or {}).get("exchanges") or {}
    assert "product:PURGE" not in overrides or not overrides["product:PURGE"].get("chemical")


# --- core 1.9.0: tears, model duties, default MTT, vent capacity -----------------------------

#: J/(mol K)
R_GAS = 8.314462618
P_ATM = 101.325  # kPa


def _materials() -> dict[str, dict]:
    return {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}


def _step(flowsheet: dict, sid: str) -> dict:
    return next(s for s in flowsheet["steps"] if s["id"] == sid)


def _kmol_h(flowsheet: dict, sid: str) -> dict[str, float]:
    """Component flows of a material stream, kmol/h."""
    mats = _materials()
    design = _stream(flowsheet, sid)["state"]["design"]
    flow, comp = design["flow"]["value"], design["composition"]
    if comp["basis"] == "mole_fraction":
        mw = sum(x * mats[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mw * x for k, x in comp["values"].items()}
    return {k: flow * w / mats[k]["molar_mass"] for k, w in comp["values"].items()}


def _duty(flowsheet: dict, qid: str) -> dict:
    return _stream(flowsheet, qid)["state"]["design"]["duty"]


def _hours_per_batch(flowsheet: dict) -> float:
    batch = _yaml("process/recipe.yaml")["batch_size"]
    return batch["value"] / _stream(flowsheet, batch["stream"])["state"]["design"]["flow"]["value"]


def test_plant_requires_core_1_9():
    assert _yaml("plant.yaml")["requires"] == "cheme-as-code>=1.9"


def test_recycles_are_tears_that_propagate_converges(flowsheet):
    tears = {t["stream"]: t for t in flowsheet["tears"]}
    assert set(tears) == {"S11", "S3"}
    for tear in tears.values():
        assert sum(tear["initial"]["composition"].values()) == pytest.approx(1.0, abs=1e-3)
    assert flowsheet["convergence"]["method"] == "wegstein"
    s11 = _stream(flowsheet, "S11")["state"]["design"]
    for key in ("flow", "composition"):
        assert s11[key]["provenance"] == "calculated", key
        assert "(tear, wegstein)" in s11[key]["source"], s11[key]["source"]
    s3 = _stream(flowsheet, "S3")["state"]["design"]
    assert s3["flow"]["provenance"] == "assumed"  # the charge ratio of D-004 stays a design input
    assert s3["composition"]["provenance"] == "calculated" and "(tear, wegstein)" in s3["composition"]["source"]
    assert _step(flowsheet, "X101")["split"] == {"recycle": 0.95}  # the 5 % purge of D-016
    for s in flowsheet["streams"]:
        for key, value in (s.get("state", {}).get("design") or {}).items():
            if isinstance(value, dict) and value.get("provenance") == "assumed":
                assert "converged over" not in value.get("source", ""), (s["id"], key)
    assert "converged by a hand driver" not in _section("D-006")
    assert "tears:" in _section("D-006")


def test_charge_ratios_hold_at_the_converged_recycle(flowsheet):
    charge, nitrite, meoh = (_kmol_h(flowsheet, s) for s in ("S12", "S1", "S3"))
    hydrazine = charge["N2H4"]
    for value, target in (
        (charge["NAOH"] / hydrazine, 1.20),  # D-004: 74.0 on 61.8 mol
        (charge["H2O"] / hydrazine, 6.63),
        (nitrite["NANO2"] / hydrazine, 0.769),
        (meoh["MEOH"] / nitrite["NANO2"], 1.002),
    ):
        assert value == pytest.approx(target, rel=5e-4), (value, target)


def test_duties_are_written_by_the_models(flowsheet):
    for qid in ("Q1", "Q2", "Q3", "Q6"):
        duty = _duty(flowsheet, qid)
        assert duty["provenance"] == "calculated" and " duty " in duty["source"], (qid, duty)
    for qid in ("Q4", "Q5", "Q7", "Q8"):  # condensers and the dryer: no model writes them
        assert _duty(flowsheet, qid)["provenance"] == "assumed", qid
    assert _step(flowsheet, "ST101")["energy_port"] == "steam"


def test_q2_is_the_reaction_heat_less_the_dose_warming(flowsheet):
    heats = {r["id"]: -r["heat_of_reaction"]["value"] for r in _yaml("process/reactions.yaml")["reactions"]}
    r102 = _step(flowsheet, "R102")
    s12, s13, s14, s7 = (_kmol_h(flowsheet, s) for s in ("S12", "S13", "S14", "S7"))
    az = s13["NAN3"] + s13["NAN3S"] - s12["NAN3"] - s12["NAN3S"]  # kmol/h
    side = s14["N2O"]
    released = (az * heats["AZ"] + side * heats["SIDE"]) / 3600.0  # kW
    assert released == pytest.approx(126.68, abs=0.05)  # the duty typed up to core 1.8.0
    absorbed = s7["MEONO"] * r102["batch"]["dosing"][0]["absorbed"]
    t_dose = _stream(flowsheet, "S7")["state"]["design"]["temperature"]["value"]
    t_batch = _stream(flowsheet, "S13")["state"]["design"]["temperature"]["value"]
    warming = absorbed * _materials()["MEONO"]["liquid_heat_capacity"] * (t_batch - t_dose) / 3600.0
    assert warming == pytest.approx(0.48, abs=0.01)
    q2 = _duty(flowsheet, "Q2")["value"]
    assert q2 == pytest.approx(released - warming, rel=1e-3), (q2, released, warming)
    assert "126.198" in _section("D-012") and "2.08 kWh" in _section("D-012")


def test_no_hand_mtt_methanol_boils_first(flowsheet):
    mats = _materials()
    for rid, charge, left_out in (("R101", "S4", {"MEONO"}), ("R102", "S12", {"MEONO", "N2O", "NH3"})):
        assert "mtt" not in _step(flowsheet, rid)["hazard"], rid
        comp = _stream(flowsheet, charge)["state"]["design"]["composition"]["values"]
        boils = {k: mats[k]["normal_boiling_point"] for k, x in comp.items()
                 if x > 0 and k not in left_out and "normal_boiling_point" in mats[k]}
        assert min(boils, key=boils.get) == "MEOH", (rid, boils)
    assert mats["MEOH"]["normal_boiling_point"] == 337.63
    # R-102: core takes no product as an MTT candidate (ADR 0058), so the default finds methanol
    # only in the charge, which the recycled mother liquor S11 brings (the wash filtrate S25 and
    # the dryer's vapour S27; the filtrate S21 carries none); without it the default would be
    # water's boiling point and `hazard.mtt: 337.63` must come back (D-011)
    x = {s: _stream(flowsheet, s)["state"]["design"]["composition"]["values"].get("MEOH", 0.0)
         for s in ("S11", "S12", "S21", "S25", "S27")}
    assert x["S12"] == pytest.approx(0.058, abs=0.001) and x["S11"] > 0.2, x
    assert x["S21"] == 0.0 and x["S25"] > 0.5 and x["S27"] > 0.5, x
    d011 = _section("D-011")
    assert "a product" not in d011
    assert "R-102's default MTT depends on that recycle" in d011 and "hazard.mtt: 337.63" in d011


def test_vent_capacity_passes_the_methyl_nitrite_r101_makes(flowsheet):
    """D-017: the mean methyl nitrite rate of the dosing, about 44.5 m3/h at 298 K, must pass R-101's
    vent (its line to R-102), and R-102's (when R-102 stops absorbing) with the N2O and NH3 the
    dissolved methyl nitrite still forms. No nitrogen sweep is counted, and none is claimed."""
    r101 = _step(flowsheet, "R101")
    dosing_h = r101["batch"]["dosing"][0]["time"] / 3600.0
    hours = _hours_per_batch(flowsheet)
    per_batch = _kmol_h(flowsheet, "S7")["MEONO"] * hours  # kmol
    assert per_batch == pytest.approx(18.18, abs=0.01)  # cheme process recipe
    s14 = _kmol_h(flowsheet, "S14")
    side_gas = (s14["N2O"] + s14["NH3"]) * hours  # kmol per batch, formed while dosing
    for rid, temperature, extra in (("R101", 298.15, 0.0), ("R102", 313.15, side_gas)):
        mean = (per_batch + extra) / dosing_h * R_GAS * temperature / P_ATM  # m3/h
        hazard = _step(flowsheet, rid)["hazard"]
        assert hazard["provenance"] == "assumed" and "ASSUMED" in hazard["source"]
        assert hazard["vent_capacity"] >= 1.05 * mean, (rid, hazard["vent_capacity"], mean)
        assert "with the nitrogen sweep" not in hazard["source"], rid
        assert "no nitrogen sweep counted" in hazard["source"], rid
    assert "with the nitrogen sweep" not in _section("D-017")
    assert "No nitrogen sweep is counted" in _section("D-017")


def _number(pattern: str, text: str) -> list[float]:
    return [float(v) for v in re.findall(pattern, text)]


def test_blocked_vent_is_a_recorded_finding():
    """D-017's blocked-vent pressures from core's numbers: the most gas one reaction forms and
    the MTSR (screen()), into the head space of the recipe's vessel above its batch, as an ideal
    gas; a D-017 that no longer matches the recipe or the screening fails."""
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.recipe import recipe_report
    from chemeascode.domains.safety.reaction_hazards import screen

    d017 = _section("D-017")
    entries = {e.node: e for e in screen(PROCESS).entries}
    recipe = recipe_report(PROCESS)
    vessels = {v.unit: v for v in recipe.vessels}
    vents = {v.unit: v for v in recipe.vents}
    # D-017 lists R-101 first, then R-102: "(V m3 less B m3" and "about P MPa" in that order
    stated_space = re.findall(r"\(([0-9.]+) m3 less ([0-9.]+) m3", d017)
    stated_mpa = _number(r"about ([0-9.]+) MPa", d017)
    assert len(stated_space) == 2 and len(stated_mpa) == 2, (stated_space, stated_mpa)
    for i, (rid, unit) in enumerate((("R101", "M101+R101"), ("R102", "M102+R102"))):
        gas = entries[rid].gas_release
        vessel = vessels[unit]
        space = vessel.volume - vessel.working_volume  # m3
        rise = gas["formed_kmol"] * R_GAS * gas["temperature_K"] / space / 1000.0  # MPa
        assert float(stated_space[i][0]) == pytest.approx(vessel.volume, abs=0.05), rid
        assert float(stated_space[i][1]) == pytest.approx(vessel.working_volume, abs=0.005), rid
        assert stated_mpa[i] == pytest.approx(rise, abs=0.006), (rid, stated_mpa[i], rise)
        assert f"{gas['formed_kmol']:.3f} kmol" in d017, (rid, gas["formed_kmol"])
    # R-101 while the acid still runs: the generator's peak methyl nitrite into its head space
    r101 = vessels["M101+R101"]
    kpa_s = vents["R101"].peak_rate * R_GAS * vents["R101"].temperature / (r101.volume - r101.working_volume)
    assert _number(r"about ([0-9.]+) kPa/s", d017) == [pytest.approx(kpa_s, abs=0.05)]
    assert "relief device" in d017 and "trips on high pressure" in d017
    assert "29.4 m3/h" in d017 and "6.34 m3/h" in d017


def test_core_screens_the_gas_release_within_the_vents():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entries = {e.node: e for e in report.entries}
    for node, rate, mtsr, capacity in (("R101", 29.39, 298.56, 50.0), ("R102", 6.34, 318.92, 60.0)):
        e = entries[node]
        assert e.mtt == pytest.approx(337.63) and "MEOH" in e.mtt_basis, (node, e.mtt_basis)
        assert e.mtsr == pytest.approx(mtsr, abs=0.05)
        gas = e.gas_release
        assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(rate, abs=0.05)
        assert gas["vent_capacity_m3_h"] == capacity and gas["capacity_ratio"] < 1.0
        assert f"| {capacity:.0f} m3/h | {gas['capacity_ratio']:.2f} |" in _section("D-017"), node
    assert entries["R102"].accumulation == pytest.approx(0.0198, abs=5e-5)
    assert not [f for f in report.findings if f.level in ("warning", "error")]
