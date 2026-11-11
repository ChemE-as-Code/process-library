"""The frozen LCI hand expectations of the CO2 pilot skids (#331, E10) and their closed forms.

Fast, without core: tests/lca_formulas.py reproduces every value frozen in
processes/co2-electrolysis-bpm-1/results/expected-lca.yaml from the measured series and the
design inputs, and the inventory closes on its own (K and C by route, the carbon shares). The
regenerated LCA is compared with the frozen values by tests/test_co2_electrolysis_bpm_skids.py.
"""

from __future__ import annotations

import hashlib

import lca_formulas as f
import pytest


@pytest.fixture(scope="module")
def expected() -> dict:
    return f.load_expected()


@pytest.fixture(scope="module")
def values() -> dict:
    return f.lci_values()


def test_measured_series_is_the_frozen_one(expected):
    m = expected["measurements"]
    digest = hashlib.sha256((f.sf.PROCESS / m["file"]).read_bytes()).hexdigest()
    assert digest == m["sha256"], "the measured series changed: re-derive and refreeze"


def test_formulas_reproduce_every_frozen_value(expected, values):
    items = expected["expectations"]["E10"]["items"]
    assert items
    for item in items:
        got = f.lookup(values, item["key"])
        # the frozen file keeps about 7 significant figures
        assert got == pytest.approx(item["value"], rel=2e-6, abs=1e-12), item["key"]


def test_the_hand_inventory_closes(values):
    shares = values["co2"]["carbon_share"]
    assert sum(shares.values()) == pytest.approx(1.0, rel=1e-12)
    for h, skids in values["routes"].items():
        for skid, r in skids.items():
            k_in = r["fill_k"] + r["dose_k"]
            k_out = r["bleed_k"] + r["spent_k"] + r["condensate_k"]
            assert k_in == pytest.approx(k_out, rel=1e-12), (h, skid)
            # the carbon that crosses to the anolyte leaves with the spent inventory or the bleed
            c_anolyte = shares["anolyte"] * values["co2"]["fresh_kg_per_kg"] / (f.M["CO2"] * 1e-3)
            assert r["spent_c"] + r["bleed_c"] == pytest.approx(c_anolyte, rel=1e-9), (h, skid)


def test_the_parts_scale_with_the_inverse_life(values):
    p = values["parts"]
    assert p[1000]["membrane_m2_per_kg"] == pytest.approx(4 * p[4000]["membrane_m2_per_kg"])
    assert p[20000]["membrane_m2_per_kg"] == pytest.approx(p[4000]["membrane_m2_per_kg"] / 5)
