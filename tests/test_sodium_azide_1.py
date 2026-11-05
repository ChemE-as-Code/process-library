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
