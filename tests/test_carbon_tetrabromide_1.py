"""carbon-tetrabromide-1 (#152): the folder's stated numbers against its own files.

Fast, without core: the flowsheet, recipe, reactions, lca.yaml and DESIGN.md are read as YAML and
text, and what the review of process-library#389 found wrong is checked against them:

- the LCA outputs are current: every input hash that lca/manifest.json and lca/dataset.yaml
  record is the hash of the committed file (``cheme assess lca --check`` failed once because
  process.yaml was edited after ``--write``);
- the reactor jackets are checked at the mean brine temperature, the log-mean equivalent of the
  BRINE utility's supply and return against the liquor, not at the supply temperature (core takes
  ``coolant_temperature`` as constant, D-003);
- the filter-dryer's drying rate needs a heating medium below CBr4's polymorph transition at
  320.05 K (46.9 C), the reason D-008 gives for drying at 308 K;
- the vacuum condenser's heat is an energy stream to a cooling-water utility and an LCI exchange,
  about the latent heat of the dryer vapour S17 (it was once dismissed as small);
- the heats of HYPO, DISP and HALO follow from the formation enthalpies their sources name
  (DISP was once -28 kJ/mol against the -26.8 its values give);
- D-003's single-filter-dryer case and P3's year-average power agree with the cycle;
- the coverage ranks are unique after the merge of main, and the shared benchmarks file keeps
  benzyl-chloroformate-1's entries next to this dataset's, under the dataset's current id.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "carbon-tetrabromide-1"

#: K, CBr4's polymorph transition (46.9 C, Wikipedia, Carbon tetrabromide; DESIGN.md SRC-2)
T_TRANSITION = 320.05

#: kJ/mol, standard enthalpies of formation named in reactions.yaml and DESIGN.md SRC-3..SRC-5
HF = {
    "Br2(l)": 0.0,
    "OH-": -230.0,
    "Br-": -121.0,
    "H2O(l)": -285.8,
    "BrO-": -94.1,
    "BrO3-": -67.1,
    "acetone(l)": -249.4,
    "CBr4(s)": 29.4,
    "CH3COO-": -486.0,
}

#: the ionic form of each reaction (Na+ cancels), as its heat_of_reaction source writes it
IONIC = {
    "HYPO": ({"Br2(l)": 1, "OH-": 2}, {"Br-": 1, "BrO-": 1, "H2O(l)": 1}),
    "DISP": ({"BrO-": 3}, {"BrO3-": 1, "Br-": 2}),
    "HALO": ({"acetone(l)": 1, "BrO-": 4}, {"CBr4(s)": 1, "CH3COO-": 1, "OH-": 3}),
}


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _section(heading: str) -> str:
    """One DESIGN.md decision, its whitespace collapsed."""
    raw = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    start = raw.index(f"## {heading}")
    end = raw.find("\n## ", start + 3)
    return " ".join(raw[start:end if end > 0 else None].split())


@pytest.fixture(scope="module")
def fs() -> dict:
    return _yaml("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def recipe() -> dict:
    return _yaml("process/recipe.yaml")


def _node(fs: dict, nid: str) -> dict:
    return next(n for group in ("feeds", "products", "steps") for n in fs.get(group, []) if n["id"] == nid)


def _stream(fs: dict, sid: str) -> dict:
    return next(s for s in fs["streams"] if s["id"] == sid)


def _design(fs: dict, sid: str) -> dict:
    return _stream(fs, sid)["state"]["design"]


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_lca_outputs_are_current_with_their_inputs():
    """cheme assess lca --check fails when an input changed after --write; so does this."""
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    dataset = _yaml("lca/dataset.yaml")
    recorded = {**manifest["inputs"], **dataset["provenance"]["files"]}
    assert "process.yaml" in recorded and "process/flowsheet.yaml" in recorded
    stale = [rel for rel, h in recorded.items() if _sha(PROCESS / rel) != h]
    assert not stale, f"edited after cheme assess lca --write: {stale}; rerun it and commit"


def _mean_coolant(t_process: float, supply: float, ret: float) -> float:
    """The constant coolant temperature with the log-mean driving force of the two ends."""
    hot, cold = t_process - supply, t_process - ret
    return t_process - (hot - cold) / math.log(hot / cold)


@pytest.mark.parametrize("proc, step, outlet", [("HYPOBROMITE", "M101", "S6"), ("HALOFORM", "R101", "S8")])
def test_jackets_are_checked_at_the_mean_brine_temperature(fs, recipe, proc, step, outlet):
    up = next(u for u in recipe["unit_procedures"] if u["id"] == proc)
    jacket = up["vessel"]["jacket"]
    brine = _node(fs, "BRINE")["utility"]
    supply = brine["supply_temperature"]["value"]
    ret = brine["return_temperature"]["value"]
    assert ret > supply, "the brine warms in the jacket"
    t_process = _design(fs, outlet)["temperature"]["value"]  # the isothermal semi-batch's
    expected = _mean_coolant(t_process, supply, ret)
    assert jacket["coolant_temperature"] > supply + 1.0, (
        f"{proc}: the jacket is checked at the brine's supply temperature, {supply} K"
    )
    assert abs(jacket["coolant_temperature"] - expected) <= 0.05, (jacket["coolant_temperature"], expected)
    # the reactor's heat goes to that utility
    q = next(s for s in fs["streams"] if s.get("kind") == "energy" and s["from"].startswith(f"{step}."))
    assert q["to"].startswith("BRINE."), q


def test_dosing_times_stated_in_design_match_the_flowsheet(fs):
    d003 = _section("D-003")
    for step, what in (("M101", "bromine"), ("R101", "acetone")):
        hours = _node(fs, step)["batch"]["dosing"][0]["time"] / 3600.0
        m = re.search(rf"dose the {what} ([\d.]+) h", d003)
        assert m, f"D-003 no longer states the {what} dosing time"
        assert abs(float(m.group(1)) - hours) < 0.05, (what, m.group(1), hours)


def test_drying_rate_keeps_the_heating_medium_below_the_transition(fs):
    dryer = _node(fs, "D101")["dryer"]
    rate = dryer["drying_rate"]["value"]  # kg/(m2 h)
    latent = dryer["energy"]["latent_heat"]["H2O"]  # kJ/kg
    t_cake = dryer["temperature"]
    m = re.search(r"U (\d+) W/\(m2 K\)", dryer["drying_rate"]["source"])
    assert m, "the drying rate's source no longer states its wall coefficient"
    u = float(m.group(1))  # W/(m2 K)
    flux = rate * latent / 3.6  # W/m2
    t_medium = t_cake + flux / u
    assert t_cake < T_TRANSITION
    assert t_medium < T_TRANSITION, (
        f"a {rate} kg/(m2 h) rate needs a heating medium at {t_medium:.1f} K, above the {T_TRANSITION} K transition"
    )
    assert "318.15" in dryer["drying_rate"]["source"]
    assert "318" in _section("D-008")


def test_vacuum_condenser_heat_goes_to_cooling_water_and_the_lci(fs):
    dryer = _node(fs, "D101")["dryer"]
    q5 = [s for s in fs["streams"] if s.get("kind") == "energy" and s["from"].startswith("D101.")
          and s["to"].split(".")[0] != "D101"]
    assert len(q5) == 1, "D101's condenser heat has no energy stream"
    target = q5[0]["to"].split(".")[0]
    assert _node(fs, target)["utility"]["kind"] == "cooling_water"
    vapour = _design(fs, "S17")["flow"]["value"]  # kg/h, almost all water
    latent_kw = vapour * dryer["energy"]["latent_heat"]["H2O"] / 3600.0
    duty = q5[0]["state"]["design"]["duty"]["value"]
    assert latent_kw <= duty <= 1.03 * latent_kw, (duty, latent_kw)
    keys = {f["key"] for f in _yaml("lca/lca.yaml")["flows"]}
    assert f"product:{target}" in keys, "the condenser's cooling water is not an LCI exchange"
    basis = (PROCESS / "process" / "design-basis.yaml").read_text(encoding="utf-8")
    assert "not counted: small" not in basis


@pytest.mark.parametrize("rid", sorted(IONIC))
def test_heats_of_reaction_follow_their_formation_enthalpies(rid):
    reaction = next(r for r in _yaml("process/reactions.yaml")["reactions"] if r["id"] == rid)
    reactants, products = IONIC[rid]
    hess = sum(n * HF[k] for k, n in products.items()) - sum(n * HF[k] for k, n in reactants.items())
    stated = reaction["heat_of_reaction"]["value"] / 1000.0  # kJ/mol
    assert abs(stated - hess) <= 0.05, f"{rid}: {stated} kJ/mol against the Hess sum {hess:.2f}"


def test_disp_heat_stated_in_design_matches_reactions():
    disp = next(r for r in _yaml("process/reactions.yaml")["reactions"] if r["id"] == "DISP")
    m = re.search(r"DISP (-[\d.]+) kJ per mol of bromate", _section("D-005"))
    assert m and float(m.group(1)) == disp["heat_of_reaction"]["value"] / 1000.0


def test_single_filter_dryer_case_and_p3_agree_with_the_cycle(fs):
    basis = _yaml("process/design-basis.yaml")["capacity"]
    hours = basis["operating_hours_per_year"]
    d003 = _section("D-003")
    m = re.search(r"one unit, occupied ([\d.]+) h a batch, would be the bottleneck \(cycle ([\d.]+) h, (\d+) batches a year", d003)
    assert m, "D-003 no longer states the single-filter-dryer case"
    occupied, cycle, batches = float(m.group(1)), float(m.group(2)), int(m.group(3))
    assert occupied == cycle, "one unit occupied longer than the reactor's cycle sets the cycle"
    assert abs(batches - hours / cycle) < 1.0, (batches, hours / cycle)
    p3 = next(s for s in fs["streams"] if s["id"] == "P3")["state"]["design"]["duty"]
    m = re.search(r"([\d.]+) kW while a batch is in F-101, ([\d.]+) h a batch over the ([\d.]+) h cycle", p3["source"])
    assert m, "P3's source no longer states its occupancy"
    kw, occ, plant_cycle = (float(g) for g in m.groups())
    assert occ == pytest.approx(occupied, abs=0.01)
    assert p3["value"] == pytest.approx(kw * occ / plant_cycle, abs=0.005)
    assert abs(basis["batches_per_year"] - hours / plant_cycle) < 1.0


def test_coverage_ranks_are_unique():
    entries = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))["entries"]
    ranks = [e["rank"] for e in entries]
    dupes = sorted({r for r in ranks if ranks.count(r) > 1})
    assert not dupes, f"coverage ranks used twice: {dupes}"
    rank = {e["id"]: e["rank"] for e in entries}
    assert rank["carbon-tetrabromide"] > rank["benzyl-chloroformate"]


def test_shared_benchmarks_keep_both_entries():
    bench = yaml.safe_load((KIT / "benchmarks" / "chlorinated-organics.yaml").read_text(encoding="utf-8"))
    kpis = set(bench["kpis"])
    assert {"bcf-specific-benzyl-alcohol", "bcf-specific-phosgene"} <= kpis
    assert {"cbr4-specific-bromine", "cbr4-specific-wastewater"} <= kpis
    datasets = {d["process"]: d["dataset"] for d in bench["datasets"]}
    assert "benzyl-chloroformate-1" in datasets
    assert datasets["carbon-tetrabromide-1"] == _yaml("lca/dataset.yaml")["id"]


def test_published_with_cc_by():
    """Public by default (ADR 0036): the entry is published under CC-BY-4.0."""
    assert _yaml("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}
