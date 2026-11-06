"""benzoyl-chloride-1 (#156): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md and
process.yaml are checked against them:

- the yield on benzotrichloride (97.15 % of theory, two benzoyl chloride per benzotrichloride)
  and the specific benzotrichloride use (0.716 kg/kg) follow from S4 and S11;
- the product meets the patent's purity (above 99.5 %) and the design basis' (99.99 wt%, about
  12 ppm of benzotrichloride at most), and the absorber makes 30 wt% acid;
- the process is not set public in the change that adds it (CONTRIBUTING, "Publishing a
  process");
- (review of #390) the criticality classes D-011 states as possible without a TD24 are the ones
  Stoessel's scheme (core's `criticality()`) can give for the stated MTSR and MTT; the residue
  S13 is drained above its ideal benzoic acid liquidus; and the water and HCl release cases
  stay among the open items with their stoichiometric gas volume;
- (core 1.10.0, ADR 0061) the still ST101 carries its column (15 stages at reflux 2): its
  product's purity and recovery as D-008 states them, the reboiler Q4 and the condenser Q5
  written by the model at (R + 1) times the product's latent heat, and the hand column K101, its
  return S12, the mixer M102 and the reflux share Q6 gone;
- (core 1.10.0, ADR 0062) R101's vent carries the liquid's vapour through the reflux condenser
  E-102 at 308 K: the vent model writes Q8, Q2 holds the vapour's terms, and the jacket and E-102
  together remove the liquid's heat plus the HCl cooled to 308 K;
- (core 1.9.0, ADR 0058; with the vapour, core 1.10.0) R-101's vent capacity covers the gas
  released at the MTSR with the stated margin, and the blocked-vent pressure stays an open finding
  (D-014); in D-011's k/10 and k/100 cases the release exceeds it, which D-011's table and D-014
  record as open.
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
    assert yield_ == pytest.approx(0.97145, abs=5e-5)
    assert "97.15 %" in _text("DESIGN.md")
    specific = streams["S4"]["flow"]["value"] / streams["S11"]["flow"]["value"]
    assert specific == pytest.approx(0.716, abs=5e-4)


def test_product_purity_and_acid_strength(streams):
    product = _components(streams["S11"])
    total = sum(product.values())
    assert product["BZCL"] / total > 0.9999  # the design basis' 99.99 wt% (D-002)
    assert product["BTC"] / total < 12e-6  # about 12 ppm of benzotrichloride at most
    acid = _components(streams["S8"])
    assert acid["HCL"] / sum(acid.values()) == pytest.approx(0.30, abs=1e-3)


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


def _step(sheet: dict, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def test_the_still_column_gives_the_stated_purity_and_recovery(sheet, streams):
    still = _step(sheet, "ST101")["still"]
    column = still["column"]
    assert (column["stages"], column["reflux"], column["ratio"]) == (15, "constant", 2)
    assert column["provenance"] == "assumed" and still["boilup"]["value"] == 200
    # the product cut is the still's model output, passed through the cooler E101
    for sid in ("S9", "S11", "S13"):
        assert "still ST101 from S5" in streams[sid]["flow"]["source"] or sid == "S11"
    assert "pass-through E101 from S9" in streams["S11"]["flow"]["source"]
    crude, product = _components(streams["S5"]), _components(streams["S11"])
    total = sum(product.values())
    # D-008: 99.9989 wt%, 11.0 ppm of benzotrichloride, 97.31 % of the crude's benzoyl chloride
    # and 1.54 % of its benzotrichloride over, none of its benzoic acid
    assert product["BZCL"] / total == pytest.approx(0.999989, abs=2e-6)
    assert product["BTC"] / total * 1e6 == pytest.approx(11.0, abs=0.2)
    assert product["BZCL"] / crude["BZCL"] == pytest.approx(0.9731, abs=2e-4)
    assert product["BTC"] / crude["BTC"] == pytest.approx(0.0154, abs=2e-4)
    assert product.get("BA", 0.0) / crude["BA"] < 1e-6
    design = _text("DESIGN.md")
    assert "99.9989 wt% benzoyl chloride with 11.0 ppm" in design
    # the scan's row for the split's own column: 60 % of the benzotrichloride over (D-008, D-015)
    assert "| 5, 1 (the specified split's column) | 99.938 | 429 ppm | 60.0 % |" in design


def test_the_column_choice_records_its_trade_against_twenty_stages():
    # D-008: 15 stages at reflux 2 is the least boil-up only of the cases with at most 15 stages;
    # 20 stages at reflux 1.5 meets the product with less steam and is rejected on the trade
    design = _text("DESIGN.md")
    assert "| 20, 1.5 | 99.9992 | 8 ppm | 1.2 % | 1.51 h | 61.9 kW |" in design
    assert "Rejected: 20 stages at reflux 1.5" in design
    assert "least boil-up of the cases scanned that keeps" not in design
    assert "least boil-up of the cases scanned that keeps" not in _text("process/flowsheet.yaml")


def test_the_coolers_keep_the_cooling_water_minimum_approach(sheet, streams):
    # D-009: E-101 (the product, S11) and E-102 (the off-gas, S6) leave at least the minimum
    # approach above the cooling water's supply; Q7 is the product cooled from the column's top
    cw = next(p for p in sheet["products"] if p["id"] == "CW")["utility"]
    floor = cw["supply_temperature"]["value"] + cw["min_approach"]["value"]
    assert streams["S11"]["temperature"]["value"] >= floor - 1e-9
    assert streams["S6"]["temperature"]["value"] >= floor - 1e-9
    basis = yaml.safe_load((PROCESS / "process" / "design-basis.yaml").read_text(encoding="utf-8"))
    delivery = next(p for p in basis["products"] if p["name"] == "Benzoyl chloride")["delivery"]
    assert delivery["temperature_K"] == streams["S11"]["temperature"]["value"]
    product = _components(streams["S11"])
    cooled = streams["S9"]["temperature"]["value"] - streams["S11"]["temperature"]["value"]
    q7 = sum(v / MW[n] for n, v in product.items()) * 187.0 * cooled / 3600.0
    assert _energy(sheet)["Q7"]["state"]["design"]["duty"]["value"] == pytest.approx(q7, rel=1e-3)


def test_the_hand_column_and_its_streams_are_gone(sheet):
    steps = {s["id"] for s in sheet["steps"]}
    ids = {s["id"] for s in sheet["streams"]}
    assert not {"K101", "M102"} & steps and {"ST101", "E101"} <= steps
    assert not {"S10", "S12", "Q6"} & ids
    # only what core has no model for still comes from the balance script (D-006)
    cited = sorted(
        s["id"]
        for s in sheet["streams"]
        for q in s["state"]["design"].values()
        if isinstance(q, dict) and str(q.get("source", "")).startswith("scripts/balance.py")
    )
    assert cited == ["Q1", "Q3", "Q7", "S1", "S2", "S4", "S7"]


def test_the_models_write_q2_and_the_vent_condenser_q8(sheet, streams):
    energy = _energy(sheet)
    q2 = energy["Q2"]["state"]["design"]["duty"]
    q8 = energy["Q8"]["state"]["design"]["duty"]
    assert q2["provenance"] == "calculated" and "semibatch duty R101" in q2["source"]
    assert q8["provenance"] == "calculated" and "vent condenser duty R101" in q8["source"]
    assert energy["Q8"]["from"] == "R101.q_vent" and energy["Q8"]["to"].startswith("CW.")
    vent = _step(sheet, "R101")["batch"]["vent"]
    assert vent["condenser"]["temperature"] == 308.15 and vent["condenser"]["returns"] == "vessel"
    assert vent["condenser"]["energy_port"] == "q_vent"
    # the off-gas leaves E-102 at its temperature, with a little benzoyl chloride (D-010)
    s6 = _components(streams["S6"])
    assert streams["S6"]["temperature"]["value"] == 308.15
    assert s6["BZCL"] == pytest.approx(0.18, abs=0.01)
    # Q2: the reaction heat (-50 kJ/mol, one HCl per extent) less the dose warmed 298 -> 413 K,
    # less the vapour's cooling: below the liquid terms; with E-102 the two remove the liquid
    # terms plus the HCl cooled from 413 to 308 K (29.1 kJ/(kmol K), SRC-8)
    extent = s6["HCL"] / MW["HCL"]
    liquid = (50_000.0 * extent - _components(streams["S4"])["BTC"] / MW["BTC"] * 250.0 * (413.15 - 298.15)) / 3600.0
    assert q2["value"] == pytest.approx(2.889, abs=2e-3) and q2["value"] < liquid
    assert q8["value"] == pytest.approx(3.330, abs=2e-3)
    gas = extent * 29.1 * (413.15 - 308.15) / 3600.0
    assert q2["value"] + q8["value"] == pytest.approx(liquid + gas, rel=5e-3)


def test_the_still_writes_the_reboiler_and_the_condenser(sheet, streams):
    energy = _energy(sheet)
    hvap = {"BZCL": 49_600.0, "BA": 63_300.0, "BTC": 52_000.0}  # kJ/kmol, materials.yaml (NIST)
    latent = sum(v / MW[n] * hvap[n] for n, v in _components(streams["S9"]).items() if n in hvap) / 3600.0
    reflux = _step(sheet, "ST101")["still"]["column"]["ratio"]
    q4 = energy["Q4"]["state"]["design"]["duty"]
    q5 = energy["Q5"]["state"]["design"]["duty"]
    assert q4["provenance"] == "calculated" and "still duty ST101" in q4["source"]
    assert q5["provenance"] == "calculated" and "still condenser duty ST101" in q5["source"]
    assert q4["value"] == pytest.approx((1.0 + reflux) * latent, rel=1e-4)
    assert q5["value"] == pytest.approx(q4["value"], rel=1e-9)
    assert q4["value"] == pytest.approx(74.25, abs=0.01)
    assert energy["Q4"]["to"] == "ST101.steam" and energy["Q5"]["from"] == "ST101.condenser"
    still = _step(sheet, "ST101")
    assert still["energy_port"] == "steam" and still["still"]["condenser_port"] == "condenser"
    # the LCI's LP steam is the reboiler alone; the cooling water takes every cooler
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()
    assert next(line for line in inventory if line.startswith("feed:LPS,")).endswith(",Q4")
    assert next(line for line in inventory if line.startswith("product:CW,")).endswith(",Q2 Q3 Q5 Q7 Q8")


def test_the_vent_capacity_covers_the_gas_release_at_the_mtsr(sheet):
    r101 = _step(sheet, "R101")
    capacity = r101["hazard"]["vent_capacity"]
    assert r101["hazard"]["provenance"] == "assumed"
    # D-014: 0.6550 mol/s of HCl at the MTSR 421.9 K and 101.325 kPa(a), as an ideal gas, with the
    # liquid's vapour 0.239 of the gas (core 1.10.0, no condenser credited)
    hcl = 0.6550e-3 * 8.314 * 421.9 / 101.325 * 3600.0
    assert hcl == pytest.approx(81.64, abs=0.05)
    release = hcl / (1.0 - 0.239)
    assert release == pytest.approx(107.2, abs=0.15)
    assert capacity == 10.0 * math.ceil(1.2 * 107.2 / 10.0) == 130.0
    assert capacity > 75.25  # the normal peak of HCl at 413 K (cheme process recipe)
    design = _text("DESIGN.md")
    assert "107.2 m3/h (per batch" in design and "`hazard.vent_capacity: 130`" in design
    # the blocked-vent case stays an open finding: 0.317 kmol in the 0.41 m3 head space
    rise = 0.3169 * 8.314 * 421.9 / (1.6 - 1.19) / 1000.0
    assert rise == pytest.approx(2.7, abs=0.05)
    assert "by about 2.7 MPa at 421.9 K" in design and "needs a relief device" in design
    # 8 % more HCl than the recipe's normal peak by volume, 6 % in moles (0.6166 mol/s at 413.15 K)
    assert round(100.0 * (hcl / 75.25 - 1.0)) == 8
    assert round(100.0 * (0.6550 / 0.6166 - 1.0)) == 6
    assert "8 % more HCl by volume (6 % more in moles" in design
    # with the vapour, the 1.9.0 capacity (100 m3/h, the HCl alone) is exceeded: D-015's finding
    assert f"{release / 100.0:.2f} times those 100 m3/h" in design


def test_the_vent_capacity_is_exceeded_in_the_rate_constant_sensitivity(sheet):
    # D-011's k/10 and k/100 cases (core 1.10.0 reactor-hazards on a scratch copy, only A
    # divided): the gas release at the MTSR with the liquid's vapour against the 130 m3/h is
    # recorded as an open finding
    capacity = _step(sheet, "R101")["hazard"]["vent_capacity"]
    cases = {
        "k/10": (1.255e-3, 443.3, 0.398, 273.2, "2.10 x"),
        "k/100": (3.096e-3, 484.8, 0.85, 2951, "22.7 x"),
    }
    design = _text("DESIGN.md")
    table = (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
    for name, (rate, mtsr, share, m3_h, ratio) in cases.items():
        hcl = rate * 8.314 * mtsr / 101.325 * 3600.0
        assert hcl / (1.0 - share) == pytest.approx(m3_h, rel=3e-3)
        assert float(ratio.split()[0]) == pytest.approx(m3_h / capacity, abs=6e-3)
        row = next(line for line in table if line.startswith(f"| {name} |"))
        assert f"{m3_h} m3/h with {share} vapour: {ratio}" in row and "cheme.reactor-hazard-vent" in row
    # the basis for k/10: 1.2 x its release, rounded up to the next 10 m3/h
    assert 10.0 * math.ceil(1.2 * 273.2 / 10.0) == 330.0
    assert "the vent capacity holds only for the assumed kinetics." in design
    assert "about 330 m3/h with the liquid's vapour (1.2 x 273.2 m3/h, rounded up" in design
    for path in ("process.yaml", "equipment/equipment-list.yaml"):
        assert "273.2 m3/h" in _text(path) and "330 m3/h" in _text(path)


def test_core_screens_the_gas_release_within_the_vent():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    (entry,) = report.entries
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(107.2, abs=0.1)
    assert gas["vapour_share"] == pytest.approx(0.239, abs=1e-3)
    assert gas["vent_capacity_m3_h"] == 130.0 and gas["capacity_ratio"] < 1.0
    assert entry.mtsr == pytest.approx(421.9, abs=0.05)
    assert not [f for f in report.findings if f.level in ("warning", "error")]
