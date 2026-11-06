"""The basis errata of the frozen hand expectations of the CO2 pilot skids (ADR 0030).

processes/co2-electrolysis-bpm-1/results/expected-errata.yaml records a design input changed
after the freezing (kind ``basis``; X-2, the pH 12.2 trip that T-101 is sized to, DESIGN.md
D-058) with the frozen items it supersedes. Fast, without core: every superseding value follows
from the frozen closed forms (tests/skid_formulas.py, tests/lca_formulas.py) at the erratum's
basis, every frozen value it names is the frozen file's, and no frozen item that the new basis
moves is left out. tests/test_co2_electrolysis_bpm_skids.py compares the regenerated results
with these values under the frozen tolerances.
"""

from __future__ import annotations

import lca_formulas as lf
import pytest
import skid_formulas as f
import yaml

ERRATA = f.PROCESS / "results" / "expected-errata.yaml"
#: the frozen file of each closed-form module, and how to compute its values at a basis
FILES = {
    "results/expected.yaml": (f.load_expected, f.hand_values, f.lookup),
    "results/expected-lca.yaml": (lf.load_expected, lf.lci_values, lf.lookup),
}


def _basis_errata() -> list[dict]:
    doc = yaml.safe_load(ERRATA.read_text(encoding="utf-8"))
    return [e for e in doc["errata"] if e.get("kind") == "basis"]


def _frozen_items(doc: dict) -> dict[str, dict]:
    return {i["key"]: i for block in doc["expectations"].values() for i in block.get("items") or []}


def _at_basis(key: str, values: dict, lookup, design: dict):
    """The value of *key* at *design*. The frozen closed form of the longest campaign in the
    envelope divides by the volume per hour at its default pH 12, whatever the design's
    threshold, so it is recomputed here at the basis' pH."""
    if key == "E2.max_duration_in_envelope_h":
        p = f.measured_point("P200")
        per_h = f.volume_to_horizon_l(
            1.0,
            values["E1"]["total_current_a"],
            p["wde"][0],
            f.stated_co_ion_carbon_fraction(),
            design["koh_fill_mol_l"],
            design["threshold_ph"],
        )
        return values["E2"]["max_volume_in_envelope_l"] / per_h
    return lookup(values, key)


@pytest.mark.parametrize("erratum", _basis_errata(), ids=lambda e: e["id"])
def test_superseding_values_follow_from_the_frozen_formulas(erratum):
    design = {**f.DESIGN, **erratum["basis"]}
    assert set(erratum["supersedes"]) <= set(FILES) == set(erratum["frozen_files"])
    for name, rows in erratum["supersedes"].items():
        load, compute, lookup = FILES[name]
        frozen = _frozen_items(load())
        values = compute(design)
        for row in rows:
            key = row["key"]
            assert key in frozen, f"{erratum['id']}: {key} is not in {name}"
            assert row["frozen"] == frozen[key]["value"], f"{erratum['id']}: {key} frozen value"
            assert row["unit"] == frozen[key]["unit"], f"{erratum['id']}: {key} unit"
            # stored to about 7 significant figures, as the frozen files
            want = _at_basis(key, values, lookup, design)
            assert row["value"] == pytest.approx(want, rel=2e-6), f"{erratum['id']}: {key}"
            assert row["value"] != row["frozen"], f"{erratum['id']}: {key} does not change"


@pytest.mark.parametrize("erratum", _basis_errata(), ids=lambda e: e["id"])
def test_every_item_the_basis_moves_is_superseded(erratum):
    """A frozen item whose closed form moves with the new basis and that the erratum does not
    list would be compared with a stale value."""
    design = {**f.DESIGN, **erratum["basis"]}
    for name, (load, compute, lookup) in FILES.items():
        listed = {r["key"] for r in (erratum["supersedes"].get(name) or [])}
        old, new = compute(), compute(design)
        for key in _frozen_items(load()):
            a, b = lookup(old, key), _at_basis(key, new, lookup, design)
            if isinstance(a, (int, float)) and not isinstance(a, bool):
                moved = b != pytest.approx(a, rel=1e-9, abs=1e-15)
            else:
                moved = a != b
            assert not moved or key in listed, f"{erratum['id']}: {name} {key} moves ({a} -> {b}) but is not superseded"


def test_x2_is_the_design_basis_trip():
    basis = yaml.safe_load((f.PROCESS / "process" / "design-basis.yaml").read_text(encoding="utf-8"))
    threshold = basis["capacity"]["pilot_skid"]["threshold"]
    x2 = next(e for e in _basis_errata() if e["id"] == "X-2")
    assert x2["basis"] == {"threshold_ph": threshold["trip"]["ph"]}
    # the stability criterion stays the frozen one (D-003)
    assert threshold["ph"] == f.load_expected()["design"]["threshold_ph"]
