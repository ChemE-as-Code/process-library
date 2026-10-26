"""Reference impacts of an Atlas LCI workbook, for the change report (``build_lci.py --previous``).

The change report shows, per dataset and activity, how a **reference impact set** moved between
two builds. A reference impact needs a background; the library has no licensed one and packages
none (no ecoinvent factors or results). The reference is therefore stated as:

- **background: none, Atlas foreground only** (``BACKGROUND``). An activity's reference impact
  is the characterised sum of its own biosphere exchanges plus, through every input linked
  inside the Atlas (an exchange of the Atlas database, or an ``atlas activity`` alternative,
  as ``install(prefer_atlas=True)`` links it), those of the Atlas activities it draws on, per
  1 unit of its reference product (the workbook's production amount). Every input linked to a
  background activity (electricity, materials, transport, treatment, ...) and the inputs of the
  screening proxies are **left out**: they contribute nothing here, and the report lists them;
- **method: core's packaged characterisation of direct emissions** (``CATEGORIES``; today
  ``ipcc2021-gwp100``, IPCC 2021 AR6 GWP100 as ``chemeascode/domains/assessment/lca/data/
  methods.yaml`` states it with its source). An elementary flow is matched by its biosphere3
  UUID (``atlas flow uuid``), else its name and categories, against core's elementary-flow
  crosswalk (``data/elementary-flows.yaml``) and characterised by its CAS number, compartment and
  origin with core's ``methods.factor``. A flow the crosswalk does not hold, or one of an origin
  the method does not characterise although it lists the substance, is reported as
  uncharacterised (counted as 0). No factor is written here: they are read from core.

Both builds are characterised with the same (installed) core, so a delta comes from the inventory
alone. Without core installed (``cheme-as-code``) nothing is computed and the report says so.

Pure Python (no numpy): the Atlas graph is small; the linear system ``h = d + A h`` is solved by
Gaussian elimination.
"""

from __future__ import annotations

import math
from typing import Any

#: The reference impact set: packaged category ids of core (``methods.categories()``).
CATEGORIES = ("ipcc2021-gwp100",)
BACKGROUND = {
    "id": "none-atlas-foreground-only",
    "label": "No background database: Atlas foreground only (direct emissions of each activity and of the Atlas activities it links to, prefer_atlas)",
    "excluded": [
        "every input linked to a background activity (electricity, fuels, materials, construction, transport, waste treatment, ...): its supply chain contributes 0",
        "the inputs of the screening proxies (proxy:*), which link to the background",
        "exchanges the build leaves out (cut-off exclusions, free inputs, pass-through emissions; datapackage.json system_model.excluded and the activity comments)",
        "elementary flows that are not characterised (listed per activity: not in core's crosswalk, or an origin the method does not characterise)",
    ],
}
FUNCTIONAL_UNIT = "1 unit of each activity's reference product (production amount 1, after allocation), as in the workbook"
#: Brightway's unit name of the kg the packaged factors are per.
KILOGRAM = "kilogram"


class Unavailable(Exception):
    """Core's packaged characterisation cannot be read; the message says why."""


def _core() -> tuple[Any, Any, str]:
    """Core's ``methods`` and ``elementary`` modules and its version (lazy: only for a report)."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        from chemeascode.domains.assessment.lca import elementary, methods
    except ImportError as failure:
        raise Unavailable(f"core's packaged characterisation is not installed (cheme-as-code; {failure})") from failure
    try:
        release = version("cheme-as-code")
    except PackageNotFoundError:
        release = "unknown"
    return methods, elementary, release


def method_labels() -> list[dict]:
    """The reference categories as the report states them (raises ``Unavailable``)."""
    methods, _, release = _core()
    packaged = methods.categories()
    missing = [c for c in CATEGORIES if c not in packaged]
    if missing:
        raise Unavailable(f"core {release} packages no category {', '.join(missing)}")
    return [
        {
            "id": c,
            "title": packaged[c]["title"],
            "unit": packaged[c]["unit"],
            "method": packaged[c]["method"],
            "source": packaged[c]["source"],
            "factors": f"cheme-as-code {release}, chemeascode/domains/assessment/lca/data/methods.yaml",
        }
        for c in CATEGORIES
    ]


class Characteriser:
    """Factors of the reference categories per workbook biosphere exchange, from core."""

    def __init__(self) -> None:
        self.methods, elementary, _ = _core()
        self.by_uuid: dict[str, dict] = {}
        self.by_name: dict[tuple[str, str], dict] = {}
        for entry in elementary.crosswalk()["flows"].values():
            bio = entry.get("biosphere3") or {}
            for sub, uuid in (bio.get("uuid") or {}).items():
                found = {**entry, "subcompartment": sub}
                if uuid:
                    self.by_uuid[uuid] = found
                categories = elementary.BIOSPHERE3_CATEGORIES.get((entry["compartment"], sub))
                if categories and bio.get("name"):
                    self.by_name.setdefault((bio["name"], "::".join(categories)), found)

    def factors(self, exchange: dict) -> tuple[dict[str, float], str | None]:
        """``({category: factor per amount}, why uncharacterised or None)``. A flow outside the
        method (a resource, or a substance the method has no row for) has factor 0 and no reason."""
        entry = self.by_uuid.get(str(exchange.get("atlas flow uuid") or "")) or self.by_name.get((exchange.get("name"), str(exchange.get("categories") or "")))
        if entry is None:
            return {c: 0.0 for c in CATEGORIES}, "not in core's elementary-flow crosswalk"
        if entry["compartment"] == "resource":
            return {c: 0.0 for c in CATEGORIES}, None
        if exchange.get("unit") != KILOGRAM:
            return {c: 0.0 for c in CATEGORIES}, f"in {exchange.get('unit')}, the factors are per kg"
        found, gap = {}, None
        for category in CATEGORIES:
            origin = entry.get("origin") or "unspecified"
            value = self.methods.factor(category, entry.get("cas"), entry["compartment"], origin)
            if value is None:
                if self.methods.listed(category, entry.get("cas"), entry["compartment"]):
                    gap = f"{category} lists the substance but not origin {origin}"
                value = 0.0
            found[category] = value
        return found, gap


def _solve(matrix: list[list[float]], rhs: list[list[float]]) -> list[list[float]] | None:
    """``matrix x = rhs`` (several right-hand sides) by Gaussian elimination with partial
    pivoting; None when the matrix is singular."""
    n = len(matrix)
    a = [row[:] + rhs[i][:] for i, row in enumerate(matrix)]
    width = len(a[0]) if a else 0
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col and a[r][col]:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    return [[a[i][j] / a[i][i] for j in range(n, width)] for i in range(n)]


def impacts(activities: dict[str, dict], db_name: str, characteriser: Characteriser) -> dict[str, dict]:
    """The reference impacts of every activity of a workbook (``build_lci.read_workbook``) by
    code: ``{category: value}``, plus ``excluded`` (background inputs and uncharacterised flows
    of the activity and the Atlas activities it draws on). An activity in a cycle that cannot be
    solved gets ``None`` values and a reason."""
    codes = sorted(activities)
    index = {c: i for i, c in enumerate(codes)}
    by_identity: dict[tuple, str] = {}
    for code in codes:
        meta = activities[code]["meta"]
        by_identity[(activities[code]["name"], meta.get("reference product"), meta.get("location"))] = code

    n = len(codes)
    direct = [[0.0] * len(CATEGORIES) for _ in range(n)]
    links = [[0.0] * n for _ in range(n)]
    upstream: list[set[str]] = [set() for _ in range(n)]
    background: list[set[str]] = [set() for _ in range(n)]
    uncharacterised: list[set[str]] = [set() for _ in range(n)]
    for code in codes:
        i = index[code]
        for exchange in activities[code]["exchanges"]:
            amount = float(exchange.get("amount") or 0)
            kind = exchange.get("type")
            if kind == "biosphere":
                factors, why = characteriser.factors(exchange)
                for k, category in enumerate(CATEGORIES):
                    direct[i][k] += amount * factors[category]
                if why:
                    uncharacterised[i].add(f"{exchange.get('name')} ({exchange.get('categories')}): {why}")
            elif kind == "technosphere":
                target = None
                if exchange.get("atlas activity"):  # install(prefer_atlas=True) links it inside the Atlas
                    target = by_identity.get((exchange["atlas activity"], exchange.get("atlas reference product"), exchange.get("atlas location")))
                elif exchange.get("database") == db_name:
                    target = by_identity.get((exchange.get("name"), exchange.get("reference product"), exchange.get("location")))
                if target is None:
                    background[i].add(f"{exchange.get('name')} | {exchange.get('reference product')} | {exchange.get('location')}")
                else:
                    links[i][index[target]] += amount
                    upstream[i].add(target)

    matrix = [[(1.0 if i == j else 0.0) - links[i][j] for j in range(n)] for i in range(n)]
    solved = _solve(matrix, direct) if n else []

    def reach(i: int) -> set[int]:
        seen, stack = {i}, [i]
        while stack:
            for code in upstream[stack.pop()]:
                j = index[code]
                if j not in seen:
                    seen.add(j)
                    stack.append(j)
        return seen

    found = {}
    for code in codes:
        i = index[code]
        nodes = reach(i)
        entry: dict[str, Any] = {c: (None if solved is None else _round(solved[i][k])) for k, c in enumerate(CATEGORIES)}
        entry["excluded"] = {
            "background_inputs": sorted(set().union(*(background[j] for j in nodes))),
            "uncharacterised_flows": sorted(set().union(*(uncharacterised[j] for j in nodes))),
        }
        if len(nodes) > 1:
            entry["atlas_upstream"] = sorted(codes[j] for j in nodes if j != i)
        if solved is None:
            entry["problem"] = "the Atlas-internal links form a system that cannot be solved"
        found[code] = entry
    return found


def _round(value: float) -> float:
    rounded = float(f"{value:.12g}")
    return 0.0 if rounded == 0 else rounded


def _delta(old: float | None, new: float | None) -> dict:
    entry: dict[str, Any] = {"previous": old, "current": new}
    if old is not None and new is not None:
        entry["delta"] = _round(new - old)
        entry["relative_change"] = _round((new - old) / old) if old else (0.0 if new == old else None)
    return entry


def compare(old: dict[str, dict], new: dict[str, dict], old_db: str, new_db: str, datasets: list[dict]) -> dict:
    """The ``impact`` section of the change report, and per dataset entry of *datasets* (mutated:
    each gets ``impacts`` by activity code) the reference impacts before and after, with the
    absolute and relative delta when the activity is in both builds. An added or removed
    dataset or activity is reported with its one value and no delta."""
    try:
        labels = method_labels()
        characteriser = Characteriser()
    except Unavailable as failure:
        return {"status": f"not computed: {failure}", "background": BACKGROUND, "categories": [{"id": c} for c in CATEGORIES]}
    before, after = impacts(old, old_db, characteriser), impacts(new, new_db, characteriser)

    def of(workbook: dict[str, dict], pid: str, did: str) -> list[str]:
        return [c for c, a in workbook.items() if a["meta"].get("atlas process") == pid and a["meta"].get("atlas dataset") == did]

    for d in datasets:
        codes = sorted(set(of(old, d["process"], d["dataset"])) | set(of(new, d["process"], d["dataset"])))
        per: dict[str, dict] = {}
        for code in codes:
            a, b = before.get(code), after.get(code)
            meta = (new.get(code) or old.get(code))["meta"]
            entry: dict[str, Any] = {"reference_product": meta.get("reference product"), "unit": meta.get("unit")}
            if a is None or b is None:
                entry["status"] = "added" if a is None else "removed"
            for category in CATEGORIES:
                entry[category] = _delta(a.get(category) if a else None, b.get(category) if b else None)
            for key in ("excluded", "atlas_upstream", "problem"):
                if key in (b or a):
                    entry[key] = (b or a)[key]
            per[code] = entry
        d["impacts"] = per
    return {
        "status": "computed",
        "categories": labels,
        "background": BACKGROUND,
        "functional_unit": FUNCTIONAL_UNIT,
        "note": (
            "A screening reference for comparing releases, not an LCA result: without a background the values are "
            "the Atlas foreground's direct emissions only. Link the database to a licensed background for full impacts."
        ),
    }


def markdown(changes: dict) -> list[str]:
    """The reference-impact section of CHANGES.md."""
    impact = changes.get("impact")
    if not isinstance(impact, dict):
        return []
    lines = ["## Reference impacts", ""]
    if impact.get("status") != "computed":
        return [*lines, f"Reference impacts {impact.get('status', 'not computed')}.", ""]
    for category in impact["categories"]:
        lines.append(f"Method: {category['title']} ({category['id']}, {category['unit']}); factors from {category['factors']}. Source: {category['source']}")
    lines += [
        "",
        f"Background: {impact['background']['label']}. Per {impact['functional_unit']}.",
        "",
        "Excluded (contributes 0):",
        "",
        *[f"- {item}" for item in impact["background"]["excluded"]],
        "",
        impact["note"],
        "",
    ]
    for category in impact["categories"]:
        cid, unit = category["id"], category["unit"]
        lines += [f"| process | dataset | activity | previous ({unit}) | current ({unit}) | delta | relative | background inputs left out | uncharacterised flows |", "|---|---|---|---|---|---|---|---|---|"]
        for d in changes["datasets"]:
            for code, entry in (d.get("impacts") or {}).items():
                value = entry[cid]
                rel = value.get("relative_change")
                excluded = entry["excluded"]
                lines.append(
                    f"| {d['process']} | {d['dataset']} | `{code}` | {_text(value['previous'])} | {_text(value['current'])} | "
                    f"{_text(value.get('delta')) if 'delta' in value else entry.get('status', '-')} | {f'{rel * 100:+.2f} %' if rel is not None else '-'} | "
                    f"{len(excluded['background_inputs'])} | {len(excluded['uncharacterised_flows'])} |"
                )
        lines.append("")
    return lines


def _text(value: float | None) -> str:
    return "-" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{value:.6g}"
