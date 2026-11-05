"""n-bromosuccinimide-1 (#140): the folder's stated numbers against its own model.

Fast, without core: scripts/balance.py is plain Python and repeats propagate's algebra (the
streams S7 to S13 agree to 5 significant figures, DESIGN.md D-014), so the statements the
folder makes in DESIGN.md and its comments can be checked against it (review of
process-library#382):

- the NBS lost (D-007: 4.3 % dissolved in the mother liquor, 2.0 % in the wash, 0.4 % through
  the filters as solid) is per NBS equivalent of the bromine dosed, and balance.py prints it on
  that basis;
- the free bromine left by R101 leaves mostly with the filtrates, not with the dryer's vapour
  (D-005 and the lca.yaml header);
- the electricity of D-009 and D-012 is the sum of the flowsheet's P1, P2 and P3, and P3 scales
  with F-101's hours per batch, not its number of units;
- the 25 C solubility entered as a `value` at 278 K is recorded as a workaround of core's
  no-extrapolation rule (core ADR 0025, lesson L-8);
- no core release is claimed that does not exist (core main 7334d7c is unreleased).
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "n-bromosuccinimide-1"


def _balance():
    spec = importlib.util.spec_from_file_location("nbs_balance", PROCESS / "scripts" / "balance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def solved():
    b = _balance()
    br2, s = b.solve()
    return b, br2, s


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").replace("#", " ").split())


def _section(head: str) -> str:
    """One ``## head ...`` section of DESIGN.md, whitespace collapsed."""
    raw = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    part = next(p for p in raw.split("\n## ") if p.startswith(head))
    return " ".join(part.split())


def _flowsheet() -> dict:
    return yaml.safe_load((PROCESS / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))


def test_nbs_losses_match_design(solved):
    b, br2, s = solved
    lost = b.losses(s, br2)
    d007 = _section("D-007")
    m = re.search(
        r"([\d.]+) % stays dissolved in the mother liquor, ([\d.]+) % in the wash, ([\d.]+) % "
        r"passes the filters as solid",
        d007,
    )
    assert m, "D-007 no longer states the losses in the form this test reads"
    stated = [float(g) / 100 for g in m.groups()]
    got = [lost["mother liquor"], lost["wash filtrate"], lost["solid through the filters"]]
    for want, have in zip(stated, got, strict=True):
        assert abs(want - have) < 0.0006, (stated, got)
    # the yield and the losses close on the bromine dosed
    product = s["S14"]
    yield_br2 = (product.get("NBS", 0.0) + product.get("NBS_S", 0.0)) / b.MW["NBS"] / br2
    assert abs(yield_br2 + sum(got) + (1 - b.CONVERSION) - 1) < 1e-9


@pytest.mark.parametrize("rel", ["DESIGN.md", "lca/lca.yaml"])
def test_free_bromine_fate_matches_balance(rel, solved):
    b, _, s = solved
    fate = b.bromine_fate(s)
    assert fate["S9"] > 0.9 and fate["S15"] < 0.02, fate  # the filtrates, not the dryer
    text = _text(rel)
    m = re.search(
        r"(\d+) % (?:of it leaves )?with the mother liquor S9, (\d+) % with the wash filtrate "
        r"S13, (?:and )?about (\d+) % (?:reaches D101 and leaves with its vapour|with the "
        r"dryer's vapour) S15",
        text,
    )
    assert m, f"{rel}: no statement of where the free bromine goes"
    for stated, sid in zip(m.groups(), ("S9", "S13", "S15"), strict=True):
        assert abs(int(stated) - 100 * fate[sid]) < 1.0, (rel, sid, stated, fate[sid])
    assert "leaves with the dryer's vapour (D101" not in text


def test_electricity_matches_power_streams(solved):
    b, _, s = solved
    streams = {st["id"]: st for st in _flowsheet()["streams"]}
    duty = {p: streams[p]["state"]["design"]["duty"]["value"] for p in ("P1", "P2", "P3")}
    total = sum(duty.values())
    d009 = _section("D-009")
    m = re.search(r"electricity ([\d.]+) kW year average", d009)
    assert m and float(m.group(1)) == pytest.approx(total), (m and m.group(1), duty)
    # P3 runs while a batch is in F-101: its energy per batch scales with F-101's occupancy
    occ = re.search(r"3 kW x ([\d.]+) / ([\d.]+) = ([\d.]+) kW", d009)
    assert occ, "D-009 no longer derives P3 from F-101's hours per batch"
    after, before, p3 = (float(g) for g in occ.groups())
    assert 3.0 * after / before == pytest.approx(p3, abs=0.01) == duty["P3"]
    d003 = _section("D-003")
    assert f"clean: {after:g} h" in d003, "P3's hours are not F-101's occupancy of D-003"
    per_kg = total / sum(s["S14"].values())
    d012 = _section("D-012")
    m = re.search(r"electricity ([\d.]+) kWh", d012)
    assert m and float(m.group(1)) == pytest.approx(per_kg, abs=0.0006), (m and m.group(1))
    note = _text("process.yaml")
    m = re.search(r"([\d.]+) kWh/kg NBS: agitators", note)
    assert m and float(m.group(1)) == pytest.approx(per_kg, abs=0.0006)
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8")
    row = next(r for r in inventory.splitlines() if r.startswith("feed:POWER,"))
    assert float(row.split(",")[7]) == pytest.approx(per_kg, rel=1e-4), row


def test_solubility_value_recorded_as_workaround():
    steps = {st["id"]: st for st in _flowsheet()["steps"]}
    for sid in ("CR101", "W101"):
        sol = steps[sid]["crystallizer"]["solubility"]
        if "value" in sol:  # a single value at 278 K from a 25 C source: core's ADR 0025 dodged
            assert sol["provenance"] == "assumed", sid
            assert "ADR 0025" in sol["source"] and "L-8" in sol["source"], sid
    design = _text("DESIGN.md")
    assert "- L-8 (open, D-014)" in design
    assert "ADR 0025" in _section("D-014")


@pytest.mark.parametrize("rel", ["DESIGN.md", "scripts/balance.py"])
def test_no_unreleased_core_claimed_as_released(rel):
    # core main 7334d7c (ADRs 0056, 0057) is unreleased: "1.8.0 when released" until the tag
    text = _text(rel)
    for claim in ("released as 1.8.0", "Resolved in core 1.8.0", "Since core 1.8.0"):
        assert claim not in text, f"{rel}: {claim!r}"
