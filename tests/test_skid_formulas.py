"""The frozen hand expectations of the CO2 pilot skids (#330) and their closed forms.

Fast, without core: the formulas of tests/skid_formulas.py reproduce core's ADR 0043 regression
(322.30 h to pH 12 at 1 L, 1 A, WDE 0.95, Cx 0.66) and every value frozen in
processes/co2-electrolysis-bpm-1/results/expected.yaml from the measured series. The regenerated
skid results are compared with the frozen values by tests/test_co2_electrolysis_bpm_skids.py.
"""

from __future__ import annotations

import hashlib

import pytest
import skid_formulas as f


@pytest.fixture(scope="module")
def expected() -> dict:
    return f.load_expected()


@pytest.fixture(scope="module")
def values() -> dict:
    return f.hand_values()


def test_formula_reproduces_the_adr_0043_regression(expected):
    """core ADR 0043 / docs/framework/electrolysis-duties.md: 322.30 h at 1 L and 3223.0 h at
    10 L (200 mA/cm2 on 5 cm2, 1 M KOH, Cx 0.66, WDE 0.95, no degassing)."""
    assert f.time_to_threshold_h(1.0, 1.0, 0.95, 0.66) == pytest.approx(322.30, abs=0.005)
    assert f.time_to_threshold_h(10.0, 1.0, 0.95, 0.66) == pytest.approx(3223.0, abs=0.05)
    for case in expected["regression"]["cases"]:
        t = f.time_to_threshold_h(
            case["volume_l"], case["current_a"], case["wde"], case["cx"], case["c0_mol_l"]
        )
        assert t == pytest.approx(case["value_h"], abs=case["tolerance"]["abs"])
    # the volume that reaches a horizon is the same closed form, inverted
    assert f.volume_to_horizon_l(322.3028553657901, 1.0, 0.95, 0.66) == pytest.approx(1.0)


def test_measured_series_is_the_frozen_one(expected):
    m = expected["measurements"]
    digest = hashlib.sha256((f.PROCESS / m["file"]).read_bytes()).hexdigest()
    assert digest == m["sha256"], "the measured series changed: re-derive and refreeze"


def test_stated_co_ion_split_is_the_measured_one_rounded(values):
    measured = values["inputs"]["co_ion_carbon_fraction_measured"]
    assert values["inputs"]["co_ion_carbon_fraction"] == round(measured, 3)


def _check(value, frozen: dict, where: str) -> None:
    want = frozen["value"]
    if isinstance(want, bool) or frozen.get("tolerance") == "exact":
        assert value == want, where
        return
    # the frozen file keeps about 7 significant figures (exact for rounded sizes)
    assert value == pytest.approx(want, rel=2e-6, abs=1e-12), where


def test_frozen_values_follow_from_the_formulas(expected, values):
    for name, item in expected["inputs"].items():
        _check(f.lookup(values, item["key"]), item, f"inputs.{name}")
    seen = 0
    for eid, block in expected["expectations"].items():
        for item in block.get("items", []):
            assert "tolerance" in item and "formula" in item, f"{eid} {item['key']}"
            _check(f.lookup(values, item["key"]), item, f"{eid} {item['key']}")
            seen += 1
    assert seen > 80


def test_hand_values_hold_the_section_7_relations(values):
    e1, e2, e3, e4 = values["E1"], values["E2"], values["E3"], values["E4"]
    assert (e1["cells"], e1["stacks"], e1["cells_per_stack"]) == (28, 4, 7)
    assert e1["co_formed_kg_h"] >= e1["formed_kg_h"]
    assert e2[1000]["fits_height"] and not e2[10000]["fits_height"]
    assert e2[10000]["fits_plan"], "plan containment alone would not see the 10,000 h tank"
    assert 1000 < e2["max_duration_in_envelope_h"] < 10000
    assert e2["volume_ratio"] == pytest.approx(10.0, rel=1e-3)
    assert e2["diameter_ratio"] == pytest.approx(10 ** (1 / 3), rel=1e-3)
    assert e3["ionic_strength_mol_l"] < 1.5  # the anolyte model's validity
    assert e3["makeup_water_l_h"] > 0
    assert e3["dosing_tank_held_l"] < e3["dosing_tank_without_interval_l"][1000]
    for h in (1000, 10000):
        assert e4["skid_a"][h] >= e4["floor_per_kg_delivered"]
        assert e4["skid_b_makeup"] + e4["skid_b_fill_share"][h] >= e4["floor_per_kg_delivered"]
    assert e4["skid_a_per_kg_formed_exact"] >= e4["floor_per_kg_formed"]
    assert e4["skid_b_makeup"] > e4["skid_a"][1000], "dosing does not save KOH"
    assert values["E5"][1000]["elapsed_h"] == 992.0
    assert values["E6"]["charge_ratio"] > 1 and values["E6"]["deficit_ratio"] > 1
    assert values["measured_state"]["carbon_mol_l"] <= 0.01
