"""Write the fixture's scenario records (SYNTHETIC numbers), in core's ``cheme/lca-scenario/v1``
format (``cheme assess lca-scenarios --write``), for ``fixture-electrolysis``.

The fixture is no computable cheme project, so its records are written here instead of by core.
Rerun after changing the files they fingerprint (``lca/lca.yaml``, ``lca/dataset.yaml``):

    uv run python tests/fixtures/make_scenario_records.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FOLDER = Path(__file__).parent / "library" / "processes" / "fixture-electrolysis"
FINGERPRINTED = ("lca/dataset.yaml", "lca/lca.yaml")
DATASET = "fixture-electrolysis"
FU = {"product": "H2", "amount": 1, "unit": "kg", "kg": 1, "reference_amount": {"value": 1, "unit": "kg"}}
SHARE = 41.7 / (41.7 + 333.6)
CATEGORIES = [{"id": "climate-change", "unit": "kg CO2-eq", "method": "IPCC 2021 GWP100"}]


def _sha(data) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_sha(rel: str) -> str:
    return "sha256:" + hashlib.sha256((FOLDER / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _exchanges(power: float) -> list[dict]:
    return [
        {"key": "feed:WATER", "title": "Deionised water", "type": "input", "phase": "operation", "amount": 375.3, "unit": "kg", "provenance": "assumed"},
        {"key": "feed:POWER", "title": "Stack and balance-of-plant power", "type": "input", "phase": "operation", "amount": power, "unit": "kWh", "provenance": "assumed"},
        {"key": "product:H2", "title": "Hydrogen at 30 bar", "type": "product", "phase": "operation", "amount": 41.7, "unit": "kg", "provenance": "assumed"},
        {"key": "product:O2", "title": "Oxygen vented or sold", "type": "product", "phase": "operation", "amount": 333.6, "unit": "kg", "provenance": "assumed"},
    ]


def _link(key, title, amount, unit, state, background, baseline, replaced=False, location=None, status=None, note=None, year=None) -> dict:
    return {
        "key": key, "title": title, "phase": "operation", "amount": amount, "unit": unit, "state": state,
        "background": background, "baseline": baseline, "replaced": replaced, "location": location,
        "year": year, "status": status, "source_id": "fixture" if background else None, "note": note,
    }


def _record(sid, kind, case, power, power_link, total, *, title=None, location=None, year=2026, electricity=None,
            replaces=None, missing=None, proxy=None, relation="unchanged", classification="screening",
            reasons=None, gaps=(), dropped=(), notes=(), extrapolated=False) -> dict:
    exchanges = _exchanges(power)
    per_fu = power * SHARE / 41.7
    return {
        "schema": "cheme/lca-scenario/v1",
        "id": f"{DATASET}/{case['id']}/{sid}",
        "scenario": {
            "id": sid, "kind": kind, "title": title, "location": location, "year": year,
            "electricity": electricity, "source": "SYNTHETIC fixture" if kind != "baseline" else None,
            "replaces": replaces or {}, "missing": missing or {}, "proxy": proxy or {},
        },
        "process": {"dataset": DATASET, "title": "Fixture: water electrolysis", "technology": "PEM electrolysis (fixture)"},
        "design_case": {**case, "extrapolated": extrapolated},
        "foreground": {
            "layer": "foreground", "relation": relation, "scope": "foreground", "basis": "1 h of operation",
            "boundary": "gate-to-gate foreground of the plant", "fingerprint": _sha(exchanges), "exchanges": exchanges,
        },
        "linked_inventory": {
            "layer": "linked-inventory", "backend": "factors", "basis": "1 h of operation",
            "exchanges": [
                _link("feed:WATER", "Deionised water", 375.3, "kg", "free", None, "free"),
                {**power_link, "amount": power},
            ],
        },
        "impacts": {
            "layer": "characterized-impact", "functional_unit": FU,
            "allocation": {"method": "mass", "shares": {"H2": round(SHARE, 6), "O2": round(1 - SHARE, 6)}},
            "categories": CATEGORIES,
            "totals": {"climate-change": None if dropped else total},
            "characterised_sum": {"climate-change": total},
            "partial_categories": [], "comparable": not dropped, "dropped": list(dropped),
            "dropped_by_category": {"climate-change": list(dropped)} if dropped else {},
            "classification": classification, "reasons": reasons or ["factors ASSUMED", "climate categories only: a carbon footprint, not a multi-impact LCA"],
        },
        "gaps": [
            {"category": "climate-change", "key": key, "reason": "missing", "quantity": round(per_fu, 6), "unit": "kWh",
             "phase": "operation", "detail": why, "why": "declared missing: no background available"}
            for key, why in gaps
        ],
        "notes": list(notes),
        "warnings": [],
        "publication": {"policy": "public", "publishable": True, "restricted_by": []},
        "inputs": {
            "files": {rel: _file_sha(rel) for rel in FINGERPRINTED},
            "mapping": "sha256:fixture",
            "scenario": None if kind == "baseline" else _sha(sid),
            "background": {"backend": "factors"},
            "software": {"cheme-as-code": "0.8"},
        },
    }


def main() -> None:
    design = {"id": "design", "description": "Design case (synthetic)", "capacity": "1 t/d H2", "provenance": "assumed",
              "applicability": {"range": "0.8-1.2 t/d H2", "source": "SYNTHETIC fixture envelope", "limitations": "fixture only"}, "source": None}
    part = {"id": "part-load", "description": "Part load, separately computed (synthetic): higher specific power", "capacity": "0.6 t/d H2",
            "provenance": "assumed", "applicability": None, "source": None}
    per_fu = 2293.5 * SHARE / 41.7
    unchanged = "background sensitivity: the foreground is the baseline's; physical flows and duties are unchanged"
    records = {
        "baseline": _record(
            "baseline", "baseline", design, 2293.5,
            _link("feed:POWER", "Stack and balance-of-plant power", 0, "kWh", "proxy", "electricity", "factor:electricity",
                  location="GB", status="PROXY", note="fixture grid for an undecided site", year=2026),
            round(per_fu * 0.4, 6), relation="baseline",
            reasons=["factors PROXY", "climate categories only: a carbon footprint, not a multi-impact LCA"],
        ),
        "nl-grid": _record(
            "nl-grid", "background", design, 2293.5,
            _link("feed:POWER", "Stack and balance-of-plant power", 0, "kWh", "linked", "electricity-nl-synthetic", "factor:electricity",
                  replaced=True, location="NL", status="ASSUMED", year=2025),
            round(per_fu * 0.3, 6), title="Netherlands grid average (SYNTHETIC)", location="NL", year=2025,
            electricity="grid-average", replaces={"electricity": "electricity-nl-synthetic"}, notes=[unchanged],
        ),
        "de-grid": _record(
            "de-grid", "background", design, 2293.5,
            _link("feed:POWER", "Stack and balance-of-plant power", 0, "kWh", "missing", None, "factor:electricity",
                  note="no DE grid factor in the fixture"),
            0.05, title="Germany grid average (no factor)", location="DE", year=2025, electricity="grid-average",
            missing={"feed:POWER": "no DE grid factor in the fixture"}, classification="partial",
            reasons=["1 exchanges without a burden in some category"], gaps=[("feed:POWER", "no DE grid factor in the fixture")],
            dropped=["feed:POWER"], notes=[unchanged],
        ),
        "part-load": _record(
            "part-load", "design-case", part, 2500.0,
            _link("feed:POWER", "Stack and balance-of-plant power", 0, "kWh", "proxy", "electricity", "factor:electricity",
                  location="GB", status="PROXY", note="fixture grid for an undecided site", year=2026),
            round(2500.0 * SHARE / 41.7 * 0.4, 6), title="Part load (separately computed case)", location=None,
            relation="design-case",
            notes=["design case part-load: the foreground was derived from that flowsheet case, not scaled from the baseline"],
        ),
    }
    target = FOLDER / "lca" / "scenarios"
    target.mkdir(parents=True, exist_ok=True)
    for sid, data in records.items():
        (target / f"{sid}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
