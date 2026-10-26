"""Route groups: every route in the library that makes a product, per the same functional unit,
with the comparability of the routes computed rather than asserted (ChemE-as-Code/website#38).

``build_catalog.py`` writes them to ``routes.json``: one group per registry substance that some
process makes (role ``main-product`` or ``co-product``), with one route per process and LCI
dataset whose reference product is that substance. Everything is read from what the library
already has; nothing is estimated here:

- the route: the process's ``maturity`` and ``validation``, the dataset's ``technology``, tier
  (core#182 ``generation.tier`` and ``method``; none for a dataset derived from a flowsheet or
  written by hand), review records, geography (``location``, else the manifest's
  ``facets.region``), year, system model, boundary and allocation;
- the reference product: its registry grade (``registry.flow_grade``) and the state the dataset
  gives it (``state``);
- per functional unit: the energy, feedstock and emission exchanges of the dataset divided by the
  reference product's amount, in the group's functional unit when the units convert (mass only).
  Unallocated: for the main product of a multi-output dataset its other products carry none
  (``basis`` says so), as KPIs are reported; a co-product's route gets none (``missing``), as
  its share is the LCI build's allocation;
- the benchmark KPIs the catalog already evaluated (``benchmarks``);
- the footprint, only where the catalog keeps it: the headline category of the process's LCA
  when the LCA's functional unit is this product, with the Monte Carlo interval of
  ``lca/uncertainty.csv`` when there is one. A public build withholds it exactly as it withholds
  the LCA (``values_withheld``, no number); the interval goes with it;
- the data quality rating of core's run manifest (``lca/manifest.json`` ``data_quality``, TfS
  DQR) for the plant's own dataset;
- the market activities a consumer links to, from ``markets/*.yaml`` where the library has them
  (process-library#49): their code, region and layer.

Comparability (:data:`CRITERIA`): for each criterion the routes' values are compared. ``same``:
every route states the same value; ``differs``: a route states another value than most routes
(every route is flagged when no value has a majority); ``unknown``: a route states none;
``not-applicable``: fewer than two routes it applies to. Each flagged route carries the flag,
so the Atlas shows the warning next to its row. The DQR criterion holds when every route states a
DQR and none is more than :data:`DQR_SPREAD` above the best.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

import benchmarks as bm

#: The routes' TfS DQRs (1 best to 5) must lie within this of the best route's. ASSUMED: one
#: step of the pedigree scale, a library convention of this builder, not a value from a standard
#: or guideline; change it here and in docs/coverage.md (Route groups) together.
DQR_SPREAD = 1.0
#: Functional unit conversions the builder makes (mass only); other units are compared as given.
MASS = {"g": 0.001, "kg": 1.0, "t": 1000.0}
ENERGY_UNITS = {"kWh", "MJ", "GJ", "kJ"}
PRODUCT_ROLES = ("main-product", "co-product")
CRITERIA = {
    "product": "same reference product: registry grade and state",
    "functional_unit": "same functional unit (amount and unit of the reference product)",
    "boundary": "same system boundary of the inventory (the dataset's boundary)",
    "system_model": "same system model (docs/system-model.md)",
    "allocation": "same allocation method",
    "background": "same background data and boundary behind the impact numbers (only routes with a footprint)",
    "dqr": f"data quality: every route states a TfS DQR, none more than {DQR_SPREAD:g} above the best",
}
CRITICAL_REVIEW = (
    "ISO 14044 requires a critical review (by a panel of interested parties, ISO/TS 14071) of a "
    "comparative assertion intended to be disclosed to the public. These routes are listed side by "
    "side for screening; a statement that one is better than another needs that review."
)


def _yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _number(value: float) -> float:
    rounded = float(f"{value:.6g}")
    return 0.0 if rounded == 0 else rounded


def _uncertainty(folder: Path, category: str) -> dict | None:
    """The Monte Carlo interval of *category* in ``lca/uncertainty.csv`` (core's columns)."""
    path = folder / "lca" / "uncertainty.csv"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("category") != category:
                continue
            try:
                return {
                    "low": float(row["p2_5"]),
                    "median": float(row["median"]),
                    "high": float(row["p97_5"]),
                    "level": 0.95,
                    "iterations": int(row["iterations"]),
                    "source": "lca/uncertainty.csv",
                }
            except (KeyError, TypeError, ValueError):
                return None
    return None


def _data_quality(folder: Path) -> dict | None:
    path = folder / "lca" / "manifest.json"
    try:
        rating = (json.loads(path.read_text(encoding="utf-8")) or {}).get("data_quality") if path.is_file() else None
    except ValueError:
        return None
    if not isinstance(rating, dict) or not isinstance(rating.get("dqr"), (int, float)):
        return None
    return {k: rating[k] for k in ("dqr", "TeR", "GeR", "TiR", "weakest", "basis") if k in rating} | {"source": "lca/manifest.json"}


def _reference(flows: list[dict], slug: str, data: dict, study_product: str | None) -> dict | None:
    """The dataset's exchange of the product *slug*: the flow's ``inventory_key``, else the LCA's
    functional unit product, else the dataset's only product."""
    exchanges = {e.get("key"): e for e in data.get("exchanges", []) if isinstance(e, dict)}
    products = [e for e in exchanges.values() if e.get("type") == "product"]
    keys = [f.get("inventory_key") for f in flows if f.get("inventory_key")]
    for key in keys:
        if exchanges.get(key, {}).get("type") == "product":
            return exchanges[key]
    if keys:
        return None  # the flow names its exchange, and this dataset does not have it
    if study_product and len(flows) == 1 and f"product:{study_product}" in exchanges:
        return exchanges[f"product:{study_product}"]
    if len(products) == 1 and len(flows) == 1:
        return products[0]
    return None


def _per_fu(data: dict, reference: dict, scale: float) -> dict[str, list[dict]]:
    """Energy, feedstocks and emissions of the dataset per functional unit (*scale*: FU amount in
    the reference exchange's unit divided by the reference amount)."""
    groups: dict[str, list[dict]] = {"energy": [], "feedstocks": [], "emissions": []}
    for e in data.get("exchanges", []):
        if not isinstance(e, dict) or e is reference or not isinstance(e.get("amount"), (int, float)):
            continue
        if e.get("phase", "operation") != "operation":
            continue
        row = {"key": e["key"], "title": e.get("title", ""), "amount": _number(e["amount"] * scale), "unit": e.get("unit", "")}
        if e.get("type") == "input" and ((e.get("carrier") or {}).get("kind") or e.get("unit") in ENERGY_UNITS):
            row["carrier"] = (e.get("carrier") or {}).get("kind") or "energy"
            groups["energy"].append(row)
        elif e.get("type") in ("input", "resource"):
            if e.get("free"):
                row["free"] = True
            groups["feedstocks"].append(row)
        elif e.get("type") == "emission" and not e.get("free"):
            if e.get("cas"):
                row["cas"] = e["cas"]
            groups["emissions"].append(row)
    return groups


def _footprint(detail: dict, folder: Path, study_applies: bool) -> dict | None:
    """The headline footprint the catalog keeps for this route, or None."""
    lca = detail.get("lca")
    if not lca or not study_applies or not lca.get("categories"):
        return None
    first = lca["categories"][0]
    out = {
        "category": first["id"],
        "title": first.get("title", first["id"]),
        "unit": first.get("unit", ""),
        "functional_unit": lca["functional_unit"]["label"],
        "boundary": lca.get("boundary") or None,
        "factors_status": lca.get("factors_status"),
        "classification": (lca.get("result") or {}).get("classification"),
    }
    if "values_withheld" in lca:
        out["values_withheld"] = lca["values_withheld"]
        return out
    value = (lca.get("totals") or {}).get("baseline", {}).get(first["id"])
    out["value"] = value
    out["interval"] = _uncertainty(folder, first["id"]) if value is not None else None
    return out


def _background(detail: dict, footprint: dict | None) -> str | None:
    lca = detail.get("lca") or {}
    if not footprint:
        return None
    ids = sorted({s.get("id", "") for s in lca.get("data_sources", []) if s.get("id")})
    sources = ", ".join(ids) if ids else "no stated sources"
    return f"{lca.get('backend', 'factors')}: {sources} ({lca.get('factors_status')} factors); boundary {footprint.get('boundary') or 'not stated'}"


def _reviews(data: dict) -> list[str]:
    review = data.get("review")
    if review in (None, [], ""):
        return []
    if review in ("unreviewed", "none"):
        return ["none"]
    items = review if isinstance(review, list) else [review]
    return sorted({str(r.get("type", "none")) for r in items if isinstance(r, dict)})


def _route(detail: dict, folder: Path, path: Path | None, data: dict | None, slug: str, flows: list[dict], study: dict) -> dict:
    lca = detail.get("lca") or {}
    fu = lca.get("functional_unit") or {}
    grade = next((f.get("grade") for f in flows if f.get("grade")), None)
    route: dict[str, Any] = {
        "process": detail["id"],
        "title": detail["title"],
        "roles": sorted({f["role"] for f in flows}),
        "maturity": detail["maturity"],
        "validation": (detail.get("validation") or {}).get("status"),
        "grade": f"{slug}/{grade}" if grade else None,
        "region": (detail.get("facets") or {}).get("region"),
        "dataset": None,
    }
    reference = _reference(flows, slug, data, fu.get("product")) if data else None
    if data is None or reference is None:
        route["missing"] = "no LCI dataset of this product" if data is None else f"{path.relative_to(folder)} has no exchange of this product"
        route.update(functional_unit=None, boundary=None, system_model=None, allocation=None, state=None, technology=None,
                     tier=None, review=[], geography=route["region"], year=None, kpis=[], footprint=None,
                     background=None, data_quality=None)
        return route
    own = path.name == "dataset.yaml" and path.parent.name == "lca"
    # the plant's study is about this route when its functional unit is this exchange
    study_applies = own and bool(fu.get("product")) and reference["key"] == f"product:{fu['product']}"
    unit = reference.get("unit", "")
    if study_applies and fu.get("amount") is not None:
        functional_unit = {"amount": fu["amount"], "unit": fu.get("unit"), "source": "lca/lca.yaml"}
    else:
        functional_unit = {"amount": 1, "unit": unit, "source": f"{path.relative_to(folder)} (1 {unit} of {reference['key']})"}
    generation = data.get("generation") or {}
    time = data.get("time") or {}
    footprint = _footprint(detail, folder, study_applies)
    others = [e["key"] for e in data.get("exchanges", []) if isinstance(e, dict) and e.get("type") == "product" and e is not reference]
    allocation = (lca.get("allocation") if study_applies else None) or (data.get("allocation") or {}).get("method")
    if allocation is None and not others:
        allocation = "none (single product)"
    route.update(
        dataset={"id": data.get("id"), "path": str(path.relative_to(folder)), "reference": reference["key"], "basis": data.get("basis")},
        functional_unit=functional_unit,
        boundary=data.get("boundary") or None,
        system_model=data.get("system_model") or (study.get("system_model") if study_applies else None) or "cutoff",
        system_model_stated=bool(data.get("system_model") or (study_applies and study.get("system_model"))),
        allocation=allocation,
        state=reference.get("state"),
        technology=data.get("technology") or (study.get("technology") if study_applies else None) or None,
        tier=generation.get("tier"),
        tier_method=generation.get("method"),
        review=_reviews(data),
        geography=data.get("location") or route["region"],
        geography_description=(data.get("geography") or {}).get("description") or None,
        year=data.get("year") or time.get("start") or (study.get("year") if study_applies else None),
        footprint=footprint,
        background=_background(detail, footprint),
        data_quality=_data_quality(folder) if own else None,
        kpis=[
            {k: kpi.get(k) for k in ("kpi", "title", "value", "unit", "status")}
            for kpi in detail.get("benchmarks", [])
            if kpi.get("dataset") == data.get("id")
        ],
    )
    # per functional unit once the group's is known (build)
    # a co-product of a multi-output dataset: the whole process per unit of it says nothing
    # about this product without allocation shares, which are the LCI build's
    main = any(f["role"] == "main-product" for f in flows)
    route["_inventory"] = (data, reference, others, main)
    return route


def _inventory(route: dict, common: dict | None) -> dict | None:
    """The route's energy, feedstocks and emissions per functional unit: the group's (*common*)
    when the route's converts to it, else the route's own."""
    data, reference, others, main = route.pop("_inventory", (None, None, [], False))
    if data is None or not reference.get("amount"):
        return None
    if others and not main:
        return {"reference": reference["key"], "missing": f"a co-product of a multi-output dataset ({', '.join(others)} besides it): its share needs the allocation of the LCI database build"}
    unit = reference.get("unit", "")
    own = route["functional_unit"]
    fu = own
    if common and _fu_key(common) != _fu_key(own) and _fu_in(common, unit) is not None:
        fu = common
    amount = _fu_in(fu, unit)
    if amount is None:
        return {"functional_unit": _fu_key(fu), "reference": reference["key"], "missing": f"the functional unit ({_fu_key(fu)}) is not in the reference product's unit ({unit})"}
    return {
        "functional_unit": _fu_key(fu),
        "basis": "unallocated: the exchanges of the whole process per functional unit of this product"
        + (f"; the other products ({', '.join(others)}) carry none" if others else ""),
        "reference": reference["key"],
        **_per_fu(data, reference, amount / reference["amount"]),
    }


def _fu_in(functional_unit: dict, unit: str) -> float | None:
    """The functional unit's amount in *unit* (mass units convert), or None when it does not."""
    amount, fu_unit = float(functional_unit["amount"]), functional_unit.get("unit")
    if fu_unit == unit:
        return amount
    if fu_unit in MASS and unit in MASS:
        return amount * MASS[fu_unit] / MASS[unit]
    return None


def _fu_key(fu: dict | None) -> str | None:
    if not fu:
        return None
    return f"{fu['amount']:g} {fu.get('unit') or ''}".strip() if isinstance(fu.get("amount"), (int, float)) else None


def _product_key(route: dict) -> str | None:
    if route.get("grade") is None and route.get("state") is None:
        return None
    return json.dumps({"grade": route.get("grade"), "state": route.get("state")}, sort_keys=True)


def _compare(routes: list[dict]) -> dict:
    """Each criterion's status over *routes*, and the flags on the routes (in place)."""
    values = {
        "product": [_product_key(r) for r in routes],
        "functional_unit": [_fu_key(r.get("functional_unit")) for r in routes],
        "boundary": [r.get("boundary") for r in routes],
        "system_model": [r.get("system_model") if r.get("dataset") else None for r in routes],
        "allocation": [r.get("allocation") for r in routes],
        "background": [r.get("background") for r in routes],
    }
    result: dict[str, dict] = {}
    for route in routes:
        route["flags"] = []
    for criterion, column in values.items():
        applies = list(range(len(routes))) if criterion != "background" else [i for i, r in enumerate(routes) if r.get("footprint")]
        stated = [column[i] for i in applies if column[i] is not None]
        if len(applies) < 2:
            result[criterion] = {"status": "not-applicable", "description": CRITERIA[criterion]}
            continue
        counts = Counter(stated).most_common()
        majority = counts[0][0] if counts and (len(counts) == 1 or counts[0][1] > counts[1][1]) else None
        status = "same"
        for i in applies:
            value = column[i]
            if value is None:
                routes[i]["flags"].append({"criterion": criterion, "status": "unknown", "message": f"states no {criterion.replace('_', ' ')}"})
                status = "unknown" if status == "same" else status
            elif len(counts) > 1 and value != majority:
                expected = f"; most routes: {_shown(criterion, majority)}" if majority is not None else f"; the routes state {', '.join(sorted(_shown(criterion, v) for v, _ in counts))}"
                routes[i]["flags"].append({"criterion": criterion, "status": "differs", "message": f"{criterion.replace('_', ' ')} is {_shown(criterion, value)}{expected}"})
                status = "differs"
        result[criterion] = {"status": status, "description": CRITERIA[criterion], "values": sorted({_shown(criterion, v) for v in stated})}
    # data quality: every route rated, none more than DQR_SPREAD above the best
    rated = [(i, (r.get("data_quality") or {}).get("dqr")) for i, r in enumerate(routes)]
    if len(routes) < 2:
        result["dqr"] = {"status": "not-applicable", "description": CRITERIA["dqr"]}
    else:
        known = [d for _, d in rated if d is not None]
        best = min(known) if known else None
        status = "same"
        for i, dqr in rated:
            if dqr is None:
                routes[i]["flags"].append({"criterion": "dqr", "status": "unknown", "message": "states no data quality rating (TfS DQR)"})
                status = "unknown" if status == "same" else status
            elif dqr - best > DQR_SPREAD + 1e-9:
                routes[i]["flags"].append({"criterion": "dqr", "status": "differs", "message": f"DQR {dqr:g} is more than {DQR_SPREAD:g} above the best route's {best:g}"})
                status = "differs"
        result["dqr"] = {"status": status, "description": CRITERIA["dqr"], "range": {"best": best, "spread": DQR_SPREAD}}
    return result


def _shown(criterion: str, value: str | None) -> str | None:
    if criterion == "product" and value is not None:
        data = json.loads(value)
        state = data.get("state") or {}
        text = ", ".join(f"{k} {v}" for k, v in sorted(state.items()))
        return " ".join(p for p in (data.get("grade") or "no grade", f"({text})" if text else "") if p)
    return value


def _markets(library: Path, slug: str) -> list[dict]:
    """The market activities of *slug* (or one of its grades) in ``markets/*.yaml``: their code
    (``market:<product>:<region>[:<technology>]``), region, layer and title."""
    found = []
    for path in sorted((library / "markets").glob("*.yaml")) if (library / "markets").is_dir() else []:
        data = _yaml(path) or {}
        for market in data.get("markets", []) if isinstance(data, dict) else []:
            product = str(market.get("product", ""))
            if product != slug and not product.startswith(f"{slug}/"):
                continue
            code = ":".join(p for p in ("market", product, str(market.get("region", "")), market.get("technology") or "") if p)
            found.append({"code": code, "product": product, "region": market.get("region"), "layer": market.get("layer"),
                          "title": market.get("title"), "source": f"markets/{path.name}"})
    return found


def build(library: Path, details: list[dict], chemicals: dict[str, dict]) -> list[dict]:
    """The route groups of the built *details* (after the public rules), one per substance made;
    the flows' grades are resolved already (``registry.flow_grade``)."""
    makers: dict[str, list[tuple[dict, list[dict]]]] = {}
    for detail in details:
        by_slug: dict[str, list[dict]] = {}
        for flow in detail["chemistry"]["outputs"]:
            if flow.get("role") in PRODUCT_ROLES and flow["chemical"] in chemicals:
                by_slug.setdefault(flow["chemical"], []).append(flow)
        for slug, flows in by_slug.items():
            makers.setdefault(slug, []).append((detail, flows))
    groups = []
    for slug in sorted(makers):
        routes = []
        for detail, flows in sorted(makers[slug], key=lambda m: m[0]["id"]):
            folder = library / "processes" / detail["id"]
            study = (_yaml(folder / "lca" / "lca.yaml") or {}) if (folder / "lca" / "lca.yaml").is_file() else {}
            datasets = []
            for path in bm.dataset_files(folder):
                data = _yaml(path)
                if isinstance(data, dict) and data.get("kind") == "lci_dataset":
                    datasets.append((path, data))
            # one route per dataset and reference product: each grade the process makes is its own
            made, seen = [], set()
            for flow in flows:
                for p, d in datasets:
                    route = _route(detail, folder, p, d, slug, [flow], study)
                    key = (route["dataset"] or {}).get("path"), (route["dataset"] or {}).get("reference")
                    if route["dataset"] and key not in seen:
                        seen.add(key)
                        made.append(route)
            if not made:
                for grade in dict.fromkeys(f.get("grade") for f in flows):
                    made.append(_route(detail, folder, None, None, slug, [f for f in flows if f.get("grade") == grade], study))
            routes.extend(made)
        fus = Counter(k for k in (_fu_key(r.get("functional_unit")) for r in routes) if k)
        common = next((r["functional_unit"] for r in routes if fus and _fu_key(r.get("functional_unit")) == fus.most_common(1)[0][0]), None)
        for route in routes:
            route["inventory"] = _inventory(route, common)
        comparability = _compare(routes)
        groups.append(
            {
                "chemical": slug,
                "name": chemicals[slug]["name"],
                "functional_unit": fus.most_common(1)[0][0] if fus else None,
                "routes": routes,
                # None for one route: nothing to compare
                "comparable": all(c["status"] in ("same", "not-applicable") for c in comparability.values()) if len(routes) > 1 else None,
                "comparability": comparability,
                "reviewed_for_comparison": bool(routes) and all("panel" in r.get("review", []) for r in routes),
                "markets": _markets(library, slug),
            }
        )
    return groups
