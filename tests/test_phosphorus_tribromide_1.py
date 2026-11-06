"""phosphorus-tribromide-1 (#134): the folder's stated numbers against its own model.

Fast, without core: scripts/balance.py is plain Python, so the statements the folder makes in
comments and in DESIGN.md can be checked against the values the balance gives (review of
process-library#379):

- the heat of the red-phosphorus treatment T101 (REDP, 2 P + 3 Br2 -> 2 PBr3) is stated as about
  3 kJ per kg of product, about 0.1 kW and an adiabatic rise of about 5 K, in reactions.yaml,
  simulation.yaml and DESIGN.md D-007 (it was once written as 3 J per kg, 1000 times too small);
- the flowsheet header names R101's conversion as its ``batch.target`` (0.9999, D-005), not the
  rejected 0.999;
- the avoided solid PBr5 is credited to the reaction temperature above 100 C, as US 3 409 401
  says, not to the bromine excess (which forms PBr5, D-004);
- the process is public with CC-BY-4.0, every library entry is (ADR 0036).
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "phosphorus-tribromide-1"

#: kJ/kmol, formation enthalpy of red phosphorus: CRC -17.6 kJ/mol, or the element at 0 (the two
#: ends of the range DESIGN.md D-007 states)
HF_RED_P = (-17_600.0, 0.0)


def _balance():
    spec = importlib.util.spec_from_file_location("pbr3_balance", PROCESS / "scripts" / "balance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def redp_heat():
    """REDP's heat from the balance, per kg of product, in kW and as the still charge's
    adiabatic rise, at both formation enthalpies of red phosphorus."""
    b = _balance()
    _, _, s = b.solve()
    xi = s["_xi"]["REDP"]  # kmol/h of 2 P + 3 Br2 -> 2 PBr3
    product = b.total(s["S8"])  # kg/h
    feed_cp = sum(v * b.CP[n] for n, v in b.kmol(s["S7"]).items())  # kJ/(h K)
    out = []
    for hf in HF_RED_P:
        heat = -(2 * b.HF_PBR3_L - 2 * hf) * xi  # kJ/h released
        out.append({"kJ/kg": heat / product, "kW": heat / 3600.0, "K": heat / feed_cp})
    return out


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").replace("#", " ").split())


@pytest.mark.parametrize("rel", ["process/reactions.yaml", "process/simulation.yaml", "DESIGN.md"])
def test_red_phosphorus_heat_statement_matches_balance(rel, redp_heat):
    text = _text(rel)
    m = re.search(r"about ([\d.]+) (k?J) per kg of product", text)
    assert m, f"{rel}: no statement of T101's heat per kg of product"
    assert m.group(2) == "kJ", f"{rel}: T101's heat is stated in {m.group(2)} per kg, not kJ per kg"
    stated = float(m.group(1))
    lo = min(r["kJ/kg"] for r in redp_heat)
    hi = max(r["kJ/kg"] for r in redp_heat)
    assert 2.0 < lo <= hi < 3.5, (lo, hi)
    assert 0.8 * lo <= stated <= 1.2 * hi, f"{rel}: about {stated} kJ/kg against {lo:.2f}-{hi:.2f}"
    tail = text[m.end():m.end() + 400]
    kw = re.search(r"about ([\d.]+) kW", tail)
    dt = re.search(r"adiabatic rise of about ([\d.]+) K", tail)
    assert kw and dt, f"{rel}: the kW and the adiabatic rise belong next to the per-kg heat"
    kw_lo, kw_hi = (f(r["kW"] for r in redp_heat) for f in (min, max))
    dt_lo, dt_hi = (f(r["K"] for r in redp_heat) for f in (min, max))
    assert 0.8 * kw_lo <= float(kw.group(1)) <= 1.2 * kw_hi, (kw.group(1), kw_lo, kw_hi)
    assert 0.8 * dt_lo <= float(dt.group(1)) <= 1.2 * dt_hi, (dt.group(1), dt_lo, dt_hi)
    assert "not counted" in tail, f"{rel}: say that T101's heat is not counted"


def test_no_joule_per_kg_left_for_t101():
    for rel in ("process/reactions.yaml", "process/simulation.yaml", "DESIGN.md"):
        assert not re.search(r"\d J per kg", _text(rel)), rel


def test_flowsheet_header_names_the_batch_target():
    fs_path = PROCESS / "process" / "flowsheet.yaml"
    fs = yaml.safe_load(fs_path.read_text(encoding="utf-8"))
    r101 = next(st for st in fs["steps"] if st["id"] == "R101")
    target = r101["batch"]["target"]
    assert target["key"] == "P4"
    header = " ".join(
        line.lstrip("#").strip()
        for line in fs_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    )
    m = re.search(r"R101: [^;]*?to ([\d.]+) conversion of the white phosphorus", header)
    assert m, "the flowsheet header no longer names R101's conversion"
    assert float(m.group(1)) == target["conversion"], (m.group(1), target)
    assert _balance().CONVERSION == target["conversion"]


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.;])\s", text) if s]


@pytest.mark.parametrize("rel", ["process.yaml", "DESIGN.md"])
def test_avoided_pbr5_is_credited_to_the_temperature(rel):
    """US 3 409 401: the reaction above 100 C avoids the PBr5 deposits; the bromine excess
    keeps free phosphorus out but forms a little PBr5 (D-004, D-005)."""
    text = _text(rel)
    claims = [s for s in _sentences(text) if "PBr5" in s and "avoid" in s]
    assert claims, f"{rel}: no statement of what avoids the PBr5"
    for s in claims:
        assert not re.search(r"excess,? avoids", s), f"{rel}: credits the excess: {s}"
        assert "temperature" in s, f"{rel}: the avoided PBr5 is not credited to the temperature: {s}"


def test_published_public_with_cc_by():
    """ADR 0036: every library entry is public, with the library's CC BY 4.0 written explicitly."""
    manifest = yaml.safe_load((PROCESS / "process.yaml").read_text(encoding="utf-8"))
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
