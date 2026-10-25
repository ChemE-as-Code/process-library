"""The benchmark registry: key performance indicators of each process family, their reference
ranges from cited open sources, and their evaluation on the LCI datasets.

``benchmarks/<family>.yaml`` (schema ``schemas/benchmarks.schema.json``) names per family its
KPIs, each with a unit and either reference ranges (a range, the conditions it holds for, the
source) or a recorded ``no_open_reference``, and the datasets they apply to, each KPI as an
expression over the dataset's exchanges (``feed:POWER / product:GOXP``). Rules in
docs/benchmarks.md.

- :func:`load` reads and checks the registry: schema, the family against the taxonomy, every
  binding naming a KPI and a reference that exist, every expression readable;
- :func:`evaluate` computes a dataset's KPIs in the exchanges' units, converts them to the KPI's
  unit through core's ``foundation.units`` (the package's one unit system) and compares them with
  the chosen reference: ``inside``, ``outside``, ``explained`` (outside, with an
  ``out_of_range_reason``), ``no-reference`` or ``unchecked`` (not computable here);
- :func:`kpi_count` and :func:`unused_bindings` are the coverage checks of the builds.

Both builders call it, so the catalog and ``datapackage.json`` report the same results.
Core is optional: without it a KPI whose unit differs from its expression's is ``unchecked``,
which is a warning, so ``--strict`` needs ``cheme-as-code[units]`` installed.

Every script imports it from beside itself (``scripts/`` is on ``sys.path`` when one runs).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA = "cheme-as-code/benchmarks/v1"
#: A public process needs at least this many KPIs, each sourced or with a no_open_reference.
MIN_KPIS = 2
#: Inventory units of core's datasets as Pint reads them; ``ea`` and ``tkm`` have no Pint
#: spelling, so a KPI over them must be stated in the expression's own unit.
PINT_SPELLING = {"kg": "kg", "kWh": "kWh", "m": "m", "m2": "m**2", "m3": "m**3"}
TOKEN = re.compile(r"\s*(?:(?P<key>[a-z][a-z-]*:[A-Za-z0-9_.\-]+)|(?P<number>\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)|(?P<op>[-+*/()]))")


class ExpressionError(ValueError):
    """An expression that cannot be read, or computed on a dataset."""


@dataclass
class Registry:
    #: family -> the file's data
    families: dict[str, dict] = field(default_factory=dict)
    #: (process, dataset id) -> [(family, binding)]
    bindings: dict[tuple[str, str], list[tuple[str, dict]]] = field(default_factory=dict)


def _number(value: float) -> float:
    rounded = float(f"{value:.12g}")
    return 0.0 if rounded == 0 else rounded


# --- expressions -----------------------------------------------------------------------------


def tokens(expression: str) -> list[tuple[str, str]]:
    """``[(kind, text)]`` with kind ``key``, ``number`` or ``op``; raise ExpressionError."""
    found, at = [], 0
    text = expression.rstrip()
    while at < len(text):
        match = TOKEN.match(text, at)
        if not match:
            raise ExpressionError(f"{expression!r}: cannot read {text[at:].strip()!r}")
        kind = match.lastgroup
        found.append((kind, match[kind]))
        at = match.end()
    if not found:
        raise ExpressionError("empty expression")
    return found


Quantity = tuple[float, dict[str, int]]  # value, unit exponents ({"kWh": 1, "kg": -1})


def compute(expression: str, amounts: dict[str, tuple[float, str]] | None = None) -> Quantity:
    """The expression's value and unit, the keys taken from *amounts* (``key -> (amount,
    unit)``). With *amounts* None, only the syntax is checked (every key counts as 1)."""
    items = tokens(expression)
    position = 0

    def peek() -> tuple[str, str] | None:
        return items[position] if position < len(items) else None

    def take() -> tuple[str, str]:
        nonlocal position
        position += 1
        return items[position - 1]

    def combine(a: dict[str, int], b: dict[str, int], sign: int) -> dict[str, int]:
        out = dict(a)
        for unit, power in b.items():
            out[unit] = out.get(unit, 0) + sign * power
        return {u: p for u, p in out.items() if p}

    def atom() -> Quantity:
        item = peek()
        if item is None:
            raise ExpressionError(f"{expression!r}: ends early")
        kind, text = take()
        if kind == "number":
            return float(text), {}
        if kind == "key":
            if amounts is None:
                return 1.0, {}
            if text not in amounts:
                raise ExpressionError(f"the dataset has no exchange {text}")
            value, unit = amounts[text]
            return float(value), {unit: 1}
        if text == "(":
            inner = sum_()
            if peek() != ("op", ")"):
                raise ExpressionError(f"{expression!r}: missing )")
            take()
            return inner
        if text == "-":
            value, unit = atom()
            return -value, unit
        raise ExpressionError(f"{expression!r}: unexpected {text!r}")

    def product() -> Quantity:
        value, unit = atom()
        while peek() in (("op", "*"), ("op", "/")):
            _, op = take()
            other, other_unit = atom()
            if op == "*":
                value, unit = value * other, combine(unit, other_unit, 1)
            elif other == 0:
                raise ExpressionError(f"{expression!r}: division by zero")
            else:
                value, unit = value / other, combine(unit, other_unit, -1)
        return value, unit

    def sum_() -> Quantity:
        value, unit = product()
        while peek() in (("op", "+"), ("op", "-")):
            _, op = take()
            other, other_unit = product()
            if amounts is not None and other_unit != unit:
                raise ExpressionError(f"{expression!r}: adds {unit_text(unit)} and {unit_text(other_unit)}")
            value = value + other if op == "+" else value - other
        return value, unit

    result = sum_()
    if peek() is not None:
        raise ExpressionError(f"{expression!r}: unexpected {peek()[1]!r}")
    return result


def unit_text(units: dict[str, int], spelling: dict[str, str] | None = None) -> str:
    """``{"kWh": 1, "kg": -1}`` -> ``kWh/kg``; with *spelling*, each unit as it maps there."""

    def part(unit: str, power: int) -> str:
        name = spelling[unit] if spelling else unit
        return name if power == 1 else f"({name})**{power}" if spelling else f"{name}^{power}"

    top = [part(u, p) for u, p in sorted(units.items()) if p > 0]
    bottom = [part(u, -p) for u, p in sorted(units.items()) if p < 0]
    text = "*".join(top) or "1"
    return text + "".join(f"/{b}" for b in bottom) if bottom else text


def convert(value: float, units: dict[str, int], target: str) -> float | None:
    """*value* in *units* expressed in *target*, through core's ``foundation.units``. None when
    the units differ and core is not installed; raise ExpressionError when they do not convert."""
    if unit_text(units) == target:
        return value
    if any(u not in PINT_SPELLING for u in units):
        raise ExpressionError(f"{unit_text(units)} does not convert (state the KPI in {unit_text(units)})")
    try:
        from chemeascode.foundation.units import UnitError, convert_units
    except ImportError:
        return None
    try:
        return convert_units(value, unit_text(units, PINT_SPELLING) if units else "dimensionless", target)
    except UnitError as failure:
        raise ExpressionError(f"{unit_text(units)} does not convert to {target}: {failure}") from failure


# --- the registry ----------------------------------------------------------------------------


def load(folder: Path, schema_path: Path, families: dict[str, dict]) -> tuple[Registry | None, list[str]]:
    """The registry in *folder* (``benchmarks/``) and its problems, each ``"<where>: <message>"``
    (errors for the builds). None when the library has no such folder."""
    if not folder.is_dir():
        return None, []
    validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    registry, problems = Registry(), []
    for path in sorted(folder.glob("*.yaml")):
        where = f"benchmarks/{path.name}"
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        errors = [
            f"{where}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
        ]
        if errors:
            problems.extend(errors)
            continue
        family = data["family"]
        if path.stem != family:
            problems.append(f"{where}: family {family!r} differs from the file name")
        if families and family not in families:
            problems.append(f"{where}: family {family!r} is not in taxonomy/families.yaml")
        for kid, kpi in data["kpis"].items():
            ids = [r["id"] for r in kpi.get("references", [])]
            if len(ids) != len(set(ids)):
                problems.append(f"{where}: kpis.{kid}: a reference id appears twice")
            for ref in kpi.get("references", []):
                if ref["range"][0] > ref["range"][1]:
                    problems.append(f"{where}: kpis.{kid}.{ref['id']}: range is reversed")
        seen: set[tuple[str, str]] = set()
        for binding in data.get("datasets", []):
            at = f"{where}: datasets {binding['process']}/{binding['dataset']}"
            target = (binding["process"], binding["dataset"])
            if target in seen:
                problems.append(f"{at}: listed twice")
            seen.add(target)
            for kid, evaluation in binding["kpis"].items():
                kpi = data["kpis"].get(kid)
                if kpi is None:
                    problems.append(f"{at}: unknown KPI {kid!r}")
                    continue
                ids = {r["id"] for r in kpi.get("references", [])}
                if ids and evaluation.get("reference") not in ids:
                    problems.append(f"{at}: kpis.{kid}: reference must be one of {', '.join(sorted(ids))}")
                if not ids and "reference" in evaluation:
                    problems.append(f"{at}: kpis.{kid}: the KPI has no references (no_open_reference)")
                try:
                    compute(evaluation["expression"])
                except ExpressionError as failure:
                    problems.append(f"{at}: kpis.{kid}: {failure}")
            registry.bindings.setdefault(target, []).append((family, binding))
        registry.families[family] = data
    return registry, problems


def evaluate(registry: Registry, pid: str, dataset: dict, shares: dict[str, float] | None = None) -> tuple[list[dict], list[str]]:
    """The KPIs of one LCI dataset (core's ``lci_dataset``) and the warnings they raise. *shares*
    (product key -> allocation share, from build_lci) adds each KPI's ``allocated`` value."""
    amounts = {e["key"]: (e["amount"], e["unit"]) for e in dataset.get("exchanges", []) if isinstance(e, dict) and "key" in e}
    results, warnings = [], []
    for family, binding in registry.bindings.get((pid, dataset.get("id")), []):
        for kid, evaluation in sorted(binding["kpis"].items()):
            kpi = registry.families[family]["kpis"][kid]
            at = f"benchmarks/{family}.yaml datasets {pid}/{dataset['id']} kpis.{kid}"
            result: dict[str, Any] = {
                "family": family,
                "kpi": kid,
                "title": kpi["title"],
                "unit": kpi["unit"],
                "expression": evaluation["expression"],
                "value": None,
                "reference": None,
            }
            reference = next((r for r in kpi.get("references", []) if r["id"] == evaluation.get("reference")), None)
            if reference:
                result["reference"] = reference
            else:
                result["no_open_reference"] = " ".join(kpi["no_open_reference"].split())
            reason = " ".join(evaluation.get("out_of_range_reason", "").split())
            try:
                raw, units = compute(evaluation["expression"], amounts)
                value = convert(raw, units, kpi["unit"])
                if value is None:
                    raise ExpressionError(f"{unit_text(units)} to {kpi['unit']} needs core's foundation.units (pip install 'cheme-as-code[units]')")
            except ExpressionError as failure:
                result.update(status="unchecked", problem=str(failure))
                warnings.append(f"{at}: not evaluated: {failure}")
                results.append(result)
                continue
            result["value"] = _number(value)
            if evaluation.get("per"):
                result["per"] = evaluation["per"]
                if shares and evaluation["per"] in shares:
                    result["allocated"] = _number(value * shares[evaluation["per"]])
            if reference is None:
                result["status"] = "no-reference"
            else:
                low, high = reference["range"]
                inside = low <= value <= high
                if inside:
                    result["status"] = "inside"
                    if reason:
                        warnings.append(f"{at}: {value:.4g} {kpi['unit']} is inside {low:g} to {high:g}, but an out_of_range_reason is given (stale? remove it)")
                elif reason:
                    result.update(status="explained", reason=reason)
                else:
                    result["status"] = "outside"
                    warnings.append(
                        f"{at}: {value:.4g} {kpi['unit']} is outside {low:g} to {high:g} {kpi['unit']} of reference "
                        f"{reference['id']}: fix the dataset, or give out_of_range_reason if the value is right"
                    )
            results.append(result)
    return results, warnings


def kpi_count(registry: Registry, pid: str, dataset_ids: list[str]) -> int:
    """How many distinct KPIs (family, id) are evaluated on the process's datasets."""
    return len({(family, kid) for did in dataset_ids for family, binding in registry.bindings.get((pid, did), []) for kid in binding["kpis"]})


def unused_bindings(registry: Registry, datasets: set[tuple[str, str]]) -> list[str]:
    """``<process>/<dataset>`` of the bindings that name no dataset of the library."""
    return sorted(f"{pid}/{did}" for pid, did in set(registry.bindings) - datasets)


def dataset_files(folder: Path) -> list[Path]:
    """A process folder's LCI datasets, in the builders' order."""
    files = [folder / "lca" / "dataset.yaml"] if (folder / "lca" / "dataset.yaml").is_file() else []
    return files + sorted((folder / "lca" / "datasets").glob("*.yaml"))
