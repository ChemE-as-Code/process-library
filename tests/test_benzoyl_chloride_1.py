"""benzoyl-chloride-1 (#156): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md and
process.yaml are checked against them:

- the yield on benzotrichloride (97.19 % of theory, two benzoyl chloride per benzotrichloride)
  and the specific benzotrichloride use (0.715 kg/kg) follow from S4 and S11;
- the product meets the patent's purity (above 99.5 %) and the absorber makes 30 wt% acid;
- the column's specified split K101 closes on the still's distillate S9;
- the process is not set public in the change that adds it (CONTRIBUTING, "Publishing a
  process");
- (review of #390) the criticality classes D-011 states as possible without a TD24 are the ones
  Stoessel's scheme (core's `criticality()`) can give for the stated MTSR and MTT; the residue
  S13 is drained above its ideal benzoic acid liquidus; and the water and HCl release cases
  stay among the open items with their stoichiometric gas volume;
- (core 1.9.0, ADR 0059) R101's Q2 and the still's net boil-up Q4 are the models' duties
  (`calculated`), and the reboiler's share for the column's reflux is its own assumed stream Q6,
  so the reboiler's 1 + R times the distillate's latent heat is all counted;
- (core 1.9.0, ADR 0058) R-101's vent capacity covers the HCl released at the MTSR with the
  stated margin, and the blocked-vent pressure stays an open finding (D-014); in D-011's k/10
  and k/100 cases the release exceeds it, which D-011's table and D-014 record as open.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzoyl-chloride-1"
MW = {"BTC": 195.467, "BA": 122.123, "BZCL": 140.566, "ZNCL2": 136.28, "HCL": 36.458, "H2O": 18.015}


@pytest.fixture(scope="module")
def streams() -> dict[str, dict]:
    sheet = yaml.safe_load((PROCESS / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
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


def test_the_stated_yield_and_benzotrichloride_use_follow_from_the_flowsheet(streams):
    btc = _components(streams["S4"])["BTC"] / MW["BTC"]
    product = _components(streams["S11"])
    yield_ = product["BZCL"] / MW["BZCL"] / (2.0 * btc)
    assert yield_ == pytest.approx(0.9719, abs=5e-5)
    assert "97.19 %" in _text("DESIGN.md")
    specific = streams["S4"]["flow"]["value"] / streams["S11"]["flow"]["value"]
    assert specific == pytest.approx(0.715, abs=5e-4)


def test_product_purity_and_acid_strength(streams):
    product = _components(streams["S11"])
    assert product["BZCL"] / sum(product.values()) > 0.995
    acid = _components(streams["S8"])
    assert acid["HCL"] / sum(acid.values()) == pytest.approx(0.30, abs=1e-3)


def test_the_column_split_closes_on_the_still_distillate(streams):
    s9 = _components(streams["S9"])
    out = {n: _components(streams["S11"]).get(n, 0.0) + _components(streams["S12"]).get(n, 0.0) for n in s9}
    for name, value in s9.items():
        assert out[name] == pytest.approx(value, rel=1e-3, abs=1e-4)


def test_not_published_in_the_change_that_adds_it():
    manifest = yaml.safe_load((PROCESS / "process.yaml").read_text(encoding="utf-8"))
    assert manifest["publication"]["status"] == "internal"
    assert "license" not in manifest["publication"]


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.8.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:2\.7e-3 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 471.0
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 300.0 + 0.5 * i) for i in range(600)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 421.9 K" in _text("DESIGN.md")


def test_the_residue_is_drained_above_its_ideal_benzoic_acid_liquidus(streams):
    s13 = streams["S13"]
    assert s13["composition"]["basis"] == "mole_fraction"
    x_ba = s13["composition"]["values"]["BA"]
    tfus, dhfus, r = 395.2, 18000.0, 8.314  # NIST (SRC-2), as scripts/balance.py
    liquidus = 1.0 / (1.0 / tfus - r * math.log(x_ba) / dhfus)
    assert liquidus == pytest.approx(355.0, abs=0.5)
    assert s13["temperature"]["value"] - liquidus >= 15.0


def test_water_ingress_and_absorber_water_loss_are_open_items():
    # 1 kg of water with benzotrichloride: two HCl per water, as gas at 413 K and 101.325 kPa.
    volume = 1.0 / MW["H2O"] * 2.0 * 8.314 * 413.15 / 101.325
    assert volume == pytest.approx(3.8, abs=0.05)
    design = _text("DESIGN.md")
    assert "about 3.8 m3 at 413 K" in design
    assert "Loss of the absorber water while R-101 doses" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "anti-suck-back" in equipment and "A-101's water flow" in equipment


def _energy(sheet: dict) -> dict[str, dict]:
    return {s["id"]: s for s in sheet["streams"] if s.get("kind") == "energy"}


@pytest.fixture(scope="module")
def sheet() -> dict:
    return yaml.safe_load((PROCESS / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))


def test_the_models_write_q2_and_the_still_net_boilup_q4(sheet, streams):
    energy = _energy(sheet)
    q2 = energy["Q2"]["state"]["design"]["duty"]
    q4 = energy["Q4"]["state"]["design"]["duty"]
    assert q2["provenance"] == "calculated" and "semibatch duty R101" in q2["source"]
    assert q4["provenance"] == "calculated" and "still duty ST101" in q4["source"]
    # Q2: the reaction heat (-50 kJ/mol, one HCl per extent) less the dose warmed 298 -> 413 K
    extent = _components(streams["S6"])["HCL"] / MW["HCL"]
    dose = _components(streams["S4"])["BTC"] / MW["BTC"] * 250.0 * (413.15 - 298.15)
    assert q2["value"] == pytest.approx((50_000.0 * extent - dose) / 3600.0, rel=1e-4)
    still = next(s for s in sheet["steps"] if s["id"] == "ST101")
    assert still["energy_port"] == "steam" and energy["Q4"]["to"] == "ST101.steam"


def test_the_reboiler_is_the_net_boilup_plus_the_reflux_share(sheet, streams):
    energy = _energy(sheet)
    hvap = {"BZCL": 49_600.0, "BA": 63_300.0, "BTC": 52_000.0}  # kJ/kmol, materials.yaml (NIST)
    latent = sum(v / MW[n] * hvap[n] for n, v in _components(streams["S9"]).items() if n in hvap) / 3600.0
    reflux = 1.0  # K101's reflux ratio (D-008)
    q4 = energy["Q4"]["state"]["design"]["duty"]["value"]
    q6 = energy["Q6"]["state"]["design"]["duty"]
    assert q4 == pytest.approx(latent, rel=1e-4)
    assert q6["provenance"] == "assumed" and q6["source"].startswith("scripts/balance.py")
    assert q6["value"] == pytest.approx(reflux * latent, rel=1e-4)
    assert q4 + q6["value"] == pytest.approx(50.196, abs=2e-3)  # the reboiler of D-009
    # both from LP steam, so the LCI's feed:LPS counts the whole reboiler
    assert energy["Q4"]["from"].startswith("LPS.") and energy["Q6"]["from"].startswith("LPS.")
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8")
    row = next(line for line in inventory.splitlines() if line.startswith("feed:LPS,"))
    assert row.endswith(",Q4 Q6")


def test_the_vent_capacity_covers_the_gas_release_at_the_mtsr(sheet):
    r101 = next(s for s in sheet["steps"] if s["id"] == "R101")
    capacity = r101["hazard"]["vent_capacity"]
    assert r101["hazard"]["provenance"] == "assumed"
    # D-014: 0.6547 mol/s of HCl at the MTSR 421.9 K and 101.325 kPa(a), as an ideal gas
    release = 0.6547e-3 * 8.314 * 421.9 / 101.325 * 3600.0
    assert release == pytest.approx(81.6, abs=0.05)
    assert capacity == 10.0 * math.ceil(1.2 * release / 10.0) == 100.0
    assert capacity > 75.25  # the normal peak at 413 K (cheme process recipe)
    design = _text("DESIGN.md")
    assert "81.6 m3/h at 421.9 K" in design and "`hazard.vent_capacity: 100`" in design
    # the blocked-vent case stays an open finding: 0.317 kmol in the 0.41 m3 head space
    rise = 0.3169 * 8.314 * 421.9 / (1.6 - 1.19) / 1000.0
    assert rise == pytest.approx(2.7, abs=0.05)
    assert "by about 2.7 MPa at 421.9 K" in design and "needs a relief device" in design
    # 8 % above the recipe's normal peak by volume, 6 % in moles (0.6166 mol/s at 413.15 K)
    assert round(100.0 * (release / 75.25 - 1.0)) == 8
    assert round(100.0 * (0.6547 / 0.6166 - 1.0)) == 6
    assert "8 % more by volume" in design and "(6 % more in moles" in design


def test_the_vent_capacity_is_exceeded_in_the_rate_constant_sensitivity(sheet):
    # D-011's k/10 and k/100 cases (core 1.9.0 reactor-hazards on a scratch copy, only A
    # divided): the gas release at the MTSR against the 100 m3/h is recorded as an open finding
    capacity = next(s for s in sheet["steps"] if s["id"] == "R101")["hazard"]["vent_capacity"]
    cases = {"k/10": (1.254e-3, 443.3, 164.3, "1.64 x"), "k/100": (3.095e-3, 484.8, 443.2, "4.43 x")}
    design = _text("DESIGN.md")
    table = (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
    for name, (rate, mtsr, m3_h, ratio) in cases.items():
        assert rate * 8.314 * mtsr / 101.325 * 3600.0 == pytest.approx(m3_h, rel=2e-3)
        assert f"{m3_h / capacity:.2f} x" == ratio
        row = next(line for line in table if line.startswith(f"| {name} |"))
        assert f"{m3_h} m3/h: {ratio}" in row and "cheme.reactor-hazard-vent" in row
    # the basis for k/10: 1.2 x its release, rounded up to the next 100 m3/h
    assert 100.0 * math.ceil(1.2 * 164.3 / 100.0) == 200.0
    assert "the vent capacity holds only for the assumed kinetics." in design
    assert "about 200 m3/h of HCl (1.2 x 164.3 m3/h, rounded up)" in design
    for path in ("process.yaml", "equipment/equipment-list.yaml"):
        assert "164.3 m3/h" in _text(path) and "200 m3/h" in _text(path)


def test_core_screens_the_gas_release_within_the_vent():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    (entry,) = report.entries
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(81.6, abs=0.05)
    assert gas["vent_capacity_m3_h"] == 100.0 and gas["capacity_ratio"] < 1.0
    assert entry.mtsr == pytest.approx(421.9, abs=0.05)
    assert not [f for f in report.findings if f.level in ("warning", "error")]
