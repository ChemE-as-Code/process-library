"""Market datasets: the supply-chain layer of the Atlas LCI database.

``markets/<substance>.yaml`` (schema ``schemas/markets.schema.json``) names per product (a
registry slug or ``<slug>/<grade>``) and region the market a consumer links to: the Atlas
producers of the product weighted by production volume or by sourced shares, the transport from
them to the consumer (mode and distance) and the losses on the way (boil-off, handling, pipeline
leakage). Rules in docs/markets.md.

- :func:`load` reads and checks the files: schema, products and grades against the registry,
  one market per code, the layer's rules (a production mix states how it stands for
  consumption, a consumption mix names its trade data, a technology market its technology),
  weights of one kind per market (volumes in one unit, or shares that sum to 1);
- :meth:`Market.weights` and :meth:`Market.gross` are the numbers the builder writes: each
  supplier's share, and the kg taken from the suppliers per kg delivered;
- :func:`choose` picks the market an input links to by default (``prefer_atlas``).

``build_lci.py`` turns each market into a Brightway activity with the code
``market:<product>:<region>`` (``market:<product>:<region>:<technology>`` for a technology
market), in the same database as the plant activities.

Every script imports it from beside itself (``scripts/`` is on ``sys.path`` when one runs).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

import registry as reg

SCHEMA = "cheme-as-code/markets/v1"
#: The shares of a market sum to 1 within this.
SHARE_TOLERANCE = 1e-6
#: A consumer in a region without its own market links to the first of these that exists.
FALLBACK_REGIONS = ("GLO", "RER")
LAYERS = {
    "technology": "technology-specific: one technology, one region",
    "production-mix": "production mix: the region's producers weighted by production volume",
    "consumption-mix": "consumption mix: production plus imports minus exports, from trade data",
}


@dataclass
class Market:
    path: str  # from the library root
    data: dict
    chemical: str
    grade: str | None

    @property
    def product(self) -> str:
        return self.data["product"]

    @property
    def region(self) -> str:
        return self.data["region"]

    @property
    def layer(self) -> str:
        return self.data["layer"]

    @property
    def technology(self) -> str | None:
        return self.data.get("technology") if self.layer == "technology" else None

    @property
    def planned(self) -> bool:
        return bool(self.data.get("planned"))

    @property
    def code(self) -> str:
        return f"market:{self.product}:{self.region}" + (f":{self.technology}" if self.technology else "")

    @property
    def suppliers(self) -> list[dict]:
        return self.data.get("suppliers") or []

    def weights(self) -> list[float]:
        """Each supplier's share of the market, in the order of ``suppliers``."""
        raw = [float((s.get("share") or s.get("production_volume"))["value"]) for s in self.suppliers]
        total = sum(raw)
        return [w / total for w in raw] if total > 0 else raw

    def gross(self) -> float:
        """kg taken from the suppliers per kg delivered: the losses multiply."""
        kept = math.prod(1.0 - float(loss["fraction"]) for loss in self.data.get("losses") or [])
        return 1.0 / kept

    def facts(self) -> list[dict]:
        """Every number of the market with its status and source, for datapackage.json."""
        found = []
        for number, supplier in enumerate(self.suppliers):
            who = supplier.get("process") or f"market {supplier.get('market')}"
            for what in ("production_volume", "share"):
                if what in supplier:
                    found.append({"what": f"suppliers[{number}] {who} {what}", **supplier[what]})
            for leg in supplier.get("transport") or []:
                found.append({"what": f"suppliers[{number}] {who} transport {leg['mode']}", **leg["distance"]})
        for leg in self.data.get("distribution") or []:
            found.append({"what": f"distribution {leg['mode']}", **leg["distance"]})
        for loss in self.data.get("losses") or []:
            found.append({"what": f"loss {loss['kind']}", "value": loss["fraction"], "unit": "kg/kg", "status": loss["status"], "source": loss["source"]})
        return found


def _check(market: Market, products: reg.Registry) -> list[str]:
    data, problems = market.data, []
    if market.chemical not in products.chemicals:
        problems.append(f"product {market.product}: {market.chemical!r} is not a slug of chemicals/chemicals.yaml")
    elif market.grade and (market.chemical, market.grade) not in products.grades:
        problems.append(f"product {market.product}: unknown grade (add it under grades of {market.chemical} in chemicals/chemicals.yaml)")
    suppliers = market.suppliers
    if market.planned != (not suppliers):
        problems.append("a market has suppliers, or is planned (with the reason) and has none")
    layer = market.layer
    if layer == "technology":
        if not data.get("technology"):
            problems.append("a technology market names its technology")
        other = sorted({s["technology"] for s in suppliers if s.get("technology") and s["technology"] != data.get("technology")})
        if other:
            problems.append(f"technology market {data.get('technology')!r} has suppliers of {', '.join(other)}")
    elif data.get("technology"):
        problems.append(f"technology is for a technology market, not a {layer}")
    if layer == "production-mix" and "consumption" not in data:
        problems.append("a production mix states how it stands for consumption (consumption: equals_production, reason)")
    if layer == "consumption-mix":
        if not data.get("trade_source"):
            problems.append("a consumption mix names its trade data (trade_source)")
        if "consumption" in data:
            problems.append("consumption is the statement of a production mix; a consumption mix has trade_source")
    if layer != "consumption-mix" and any("market" in s for s in suppliers):
        problems.append(f"imports (suppliers with market:) belong in a consumption mix, not a {layer}")
    if any(s.get("market") == market.region for s in suppliers):
        problems.append("a market cannot import from itself")
    if suppliers:
        kinds = {("share" in s, "production_volume" in s) for s in suppliers}
        if kinds == {(True, False)}:
            total = sum(float(s["share"]["value"]) for s in suppliers)
            if abs(total - 1.0) > SHARE_TOLERANCE:
                problems.append(f"the shares sum to {total:.6g}, not 1")
        elif kinds == {(False, True)}:
            if layer == "consumption-mix":
                problems.append("a consumption mix weights its suppliers by shares from its trade data, not by production volume")
            units = {s["production_volume"]["unit"] for s in suppliers}
            if len(units) > 1:
                problems.append(f"production volumes in several units: {', '.join(sorted(units))}")
            if sum(float(s["production_volume"]["value"]) for s in suppliers) <= 0:
                problems.append("the production volumes sum to 0")
        else:
            problems.append("every supplier has a share, or every supplier a production_volume, not both or neither")
        processes = [s["process"] for s in suppliers if "process" in s]
        doubled = sorted({p for p in processes if processes.count(p) > 1})
        if doubled:
            problems.append(f"suppliers appear twice: {', '.join(doubled)}")
    for leg in [*(data.get("distribution") or []), *(leg for s in suppliers for leg in s.get("transport") or [])]:
        if leg["mode"] != "pipeline" and not leg.get("use") and leg["distance"]["value"] > 0:
            problems.append(f"transport by {leg['mode']} needs a technosphere entry (use:), only a pipeline may name none")
    return problems


def load(folder: Path, schema_path: Path, products: reg.Registry, root: Path | None = None) -> tuple[list[Market], list[str]]:
    """The markets of ``markets/*.yaml`` and the problems found (empty when there is no folder)."""
    if not folder.is_dir():
        return [], []
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    markets: list[Market] = []
    problems: list[str] = []
    seen: dict[str, str] = {}
    for path in sorted(folder.glob("*.yaml")):
        where = str(path.relative_to(root)) if root else path.name
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        errors = sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
        if errors:
            problems.extend(f"{where}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in errors)
            continue
        for number, entry in enumerate(data["markets"]):
            chemical, grade = reg.split(entry["product"])
            market = Market(where, entry, chemical, grade)
            at = f"{where} markets[{number}] {market.code}"
            if chemical != path.stem:
                problems.append(f"{at}: a market of {chemical} belongs in markets/{chemical}.yaml")
            if market.code in seen:
                problems.append(f"{at}: the same market as {seen[market.code]}")
                continue
            seen[market.code] = at
            found = _check(market, products)
            problems.extend(f"{at}: {p}" for p in found)
            if not found:
                markets.append(market)
    # one market a consumer links to per product and region: a technology market is chosen explicitly
    regional = [m for m in markets if m.layer != "technology"]
    for market in markets:
        for supplier in market.suppliers:
            if "market" in supplier and not any(m.product == market.product and m.region == supplier["market"] for m in regional):
                problems.append(f"{market.path} {market.code}: imports from market {market.product}:{supplier['market']}, which is not defined")
    return markets, problems


def choose(markets: list[Market], chemical: str, grade: str | None, location: str | None, exclude: str | None = None) -> tuple[Market | None, list[Market]]:
    """The market of ``<chemical>/<grade>`` an input at *location* links to by default, and the
    other regional markets of the product: the market of the consumer's region, else the first
    of :data:`FALLBACK_REGIONS`, else the only one. None when there is none, or when several
    exist and none fits (the caller reports it). Technology markets and planned markets are
    never chosen by default; neither is a market whose only supplier is *exclude* (the
    consumer's own process)."""
    candidates = sorted(
        (
            m for m in markets
            if m.chemical == chemical and m.grade == grade and m.layer != "technology" and not m.planned
            and not (exclude and all(s.get("process") == exclude for s in m.suppliers))
        ),
        key=lambda m: m.region,
    )
    by_region = {m.region: m for m in candidates}
    for region in (location, *FALLBACK_REGIONS):
        if region in by_region:
            chosen = by_region[region]
            return chosen, [m for m in candidates if m is not chosen]
    if len(candidates) == 1:
        return candidates[0], []
    return None, candidates
