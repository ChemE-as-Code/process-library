"""Exchange formats of the Atlas LCI build beyond the bw2io workbook (process-library#51).

``build_lci.py`` calls :func:`write_formats` after the workbook. The writers read only what the
build already made: the allocated activities and proxies of the workbook, and the unallocated
multi-output form of each dataset (``build_lci.multi_output_datasets``), which comes from the
same datasets, mappings and linking. There is no second source of truth.

Files (``<out>/lci/``):

- ``<database>-olca-jsonld.zip``: an openLCA JSON-LD package (olca-schema 2, written with the
  ``olca-schema`` package). One **multi-output** unit process per dataset, with every co-product
  as an output, allocation factors and the build's method as the default allocation method, so
  that openLCA's allocated result per unit of a product is the workbook's activity. The markets
  (``market:<product>:<region>``) and the screening proxies are single-output processes; an
  exchange linked to an Atlas activity (a market's supplier, an input linked to a market or a
  plant) has that activity's process as its default provider. Product flows of the Atlas, background product flows
  (by name, to map to your background), elementary flows and locations are included; units and
  flow properties are references to openLCA's reference data (their UUIDs come from
  ``olca_schema.units``), so the target database needs openLCA's reference units and flow
  properties (every database created with reference data has them).
- ``<database>-multifunctional.json``: the same multi-output datasets for Brightway 2.5's
  ``multifunctional`` package (``MultifunctionalDatabase``), with the allocation properties per
  co-product (mass for products in kg, exergy, energy, price: only the values the dataset or
  study states) and the build's share. ``cheme_as_code_lci.install_multifunctional`` installs
  it; allocating it with the build's method gives the workbook's activities, with their codes.
  The markets and proxies are single-output processes under their activity codes.

A mapping gap of an unpublished process (``atlas gap``, ADR 0022) is carried unlinked and flagged
in both formats, never linked to a guess: in JSON-LD a flow of its own in the category
``ChemE-as-Code Atlas/unlinked (mapping gaps)`` (``atlas_uuid("flow", "gap", <type>, <name>,
<unit>)``) without a default provider, and the process description's ``UNLINKED`` note; in the
multifunctional file the exchange keeps ``atlas gap`` and has no database, so the installer
reports it unlinked and writes nothing.

Identifiers (deterministic, documented in lci/README.md):

- a dataset's process: the dataset's own ``uuid`` (core: uuid5 of ``<plant>/<dataset id>``) in
  the default build; ``atlas_uuid("process", <code>)`` when it has none, and
  ``atlas_uuid("process", <system model>, <code>)`` for a labelled variant (the substitution
  build's processes must not overwrite the default build's in one openLCA database);
- an Atlas product flow: ``atlas_uuid("flow", <activity code>)``; a background product flow:
  ``atlas_uuid("flow", "background", <reference product>, <unit>)``; a location:
  ``atlas_uuid("location", <code>)``;
- an elementary flow: its biosphere3 UUID where the build has one (``atlas flow uuid``: the
  ecoinvent elementary exchange id as distributed with bw2io, from core's crosswalk or the
  mappings). Otherwise ``atlas_uuid("flow", "elementary", <name>, <categories>, <unit>)``, said
  in the flow's description: it is **not** an EF 3.1 or ecoinvent identifier and must be mapped
  by name and category. EF 3.1 UUIDs are not recorded by core yet and are never
  guessed here.

``atlas_uuid`` is uuid5 in the namespace ``uuid5(NAMESPACE_URL,
"https://github.com/ChemE-as-Code/process-library/lci")``, following core's dataset namespace.

Deterministic: sorted entries, fixed zip dates, no ``lastChange`` stamps.
"""

from __future__ import annotations

import io
import json
import math
import uuid
import zipfile
from pathlib import Path
from typing import Any

import olca_schema as o
from olca_schema import units as olca_units

ATLAS_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/ChemE-as-Code/process-library/lci")
#: The olca-schema release the JSON-LD is written with (pinned in build_lci.py's dependencies).
OLCA_SCHEMA_PACKAGE = "olca-schema==2.6.2"
JSONLD_FORMAT = "openLCA JSON-LD (olca-schema)"
JSONLD_FORMAT_VERSION = "2"  # olca-schema.json {"version": 2}
MULTIFUNCTIONAL_SCHEMA = "cheme-as-code/lci-multifunctional/v1"
MULTIFUNCTIONAL_FORMAT = "Brightway 2.5 multifunctional database (JSON, for the multifunctional package)"
MULTIFUNCTIONAL_PACKAGE = "multifunctional==1.1.2"
#: Brightway unit names (build_lci.BW_UNITS values) -> openLCA reference unit names.
OLCA_UNITS = {
    "kilogram": "kg",
    "kilowatt hour": "kWh",
    "megajoule": "MJ",
    "meter": "m",
    "square meter": "m2",
    "square meter-year": "m2*a",
    "cubic meter": "m3",
    "unit": "Item(s)",
    "ton kilometer": "t*km",
    "kilo Becquerel": "kBq",
    "normal cubic meter": "Nm3",
}
#: build allocation method -> the multifunctional strategy label that reproduces it, and the
#: openLCA allocation type it is written as.
MF_STRATEGY = {"mass": "mass", "economic": "price", "energy": "energy", "exergy": "exergy", "shares": "share"}
MF_PROPERTY = {"mass": "mass", "economic": "price", "energy": "energy", "exergy": "exergy"}
OLCA_DEFAULT = {"mass": o.AllocationType.PHYSICAL_ALLOCATION, "energy": o.AllocationType.PHYSICAL_ALLOCATION, "exergy": o.AllocationType.PHYSICAL_ALLOCATION, "economic": o.AllocationType.ECONOMIC_ALLOCATION, "shares": o.AllocationType.CAUSAL_ALLOCATION}
PROPERTY_UNITS = {
    "mass": "kg per unit of the product (products counted in kg only: 1)",
    "exergy": "kJ per unit of the product (chemical + physical, dead state 298.15 K, 101.325 kPa; core ProductProperties)",
    "energy": "kJ per unit of the product (energy content, e.g. lower heating value; core ProductProperties)",
    "price": "per unit of the product, in the study's currency (core ProductProperties)",
    "share": "the build's allocation share of the product (sums to 1 over the dataset's products; not multiplied by the amount)",
}
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


class FormatError(Exception):
    """A dataset the writers cannot express in a format; the message says where and why."""


def atlas_uuid(*parts: str) -> str:
    return str(uuid.uuid5(ATLAS_NAMESPACE, "/".join(parts)))


def _process_id(code: str, own_uuid: str | None, model: str, default: bool) -> str:
    if default:
        return own_uuid or atlas_uuid("process", code)
    return atlas_uuid("process", model, code)


def _is_resource(entry: dict) -> bool:
    return str(entry.get("categories", "")).split("::")[0].startswith("natural resource")


def _identity(entry: dict) -> tuple:
    return (entry.get("name"), entry.get("reference product"), entry.get("location"), entry.get("unit"))


# --- openLCA JSON-LD ---------------------------------------------------------------------------


class _Olca:
    """Collects the root entities of one JSON-LD package, by id."""

    def __init__(self, db_name: str, model: str, default: bool, site: str) -> None:
        self.db_name = db_name
        self.model = model
        self.default = default
        self.site = site
        self.entities: dict[tuple[str, str], Any] = {}
        #: (name, reference product, location, unit) of an Atlas activity -> (flow ref, process ref)
        self.atlas: dict[tuple, tuple[o.Ref, o.Ref]] = {}

    def add(self, folder: str, entity: Any) -> None:
        self.entities.setdefault((folder, entity.id), entity)

    def units(self, bw_unit: str, where: str) -> tuple[o.Ref, o.Ref]:
        symbol = OLCA_UNITS.get(bw_unit)
        unit = olca_units.unit_ref(symbol) if symbol else None
        if unit is None:
            raise FormatError(f"{where}: unit {bw_unit!r} has no openLCA reference unit (olca_schema.units)")
        return unit, olca_units.property_ref(symbol)

    def location(self, code: str) -> o.Ref:
        entity = o.Location(id=atlas_uuid("location", code), name=code, code=code, last_change=None, version=None)
        entity.description = "Atlas location by its code (ISO 3166-1 alpha-2, GLO, RER or RoW); an Atlas identifier, not openLCA's reference location: merge or replace it with yours."
        self.add("locations", entity)
        return o.as_ref(entity)

    def flow(self, fid: str, name: str, kind: o.FlowType, bw_unit: str, where: str, category: str, description: str, location: str | None = None) -> o.Ref:
        _, prop = self.units(bw_unit, where)
        flow = o.Flow(id=fid, name=name, flow_type=kind, category=category, description=description, last_change=None, version=None)
        flow.flow_properties = [o.FlowPropertyFactor(flow_property=prop, conversion_factor=1.0, is_ref_flow_property=True)]
        if location:
            flow.location = self.location(location)
        self.add("flows", flow)
        return o.as_ref(flow)

    def atlas_flow(self, code: str, row: dict) -> o.Ref:
        description = [f"Atlas product {code}."]
        if row.get("chemical"):
            description.append(f"Chemical {row['chemical']}" + (f", grade {row['grade']}" if row.get("grade") else "") + ".")
        if row.get("state"):
            description.append(f"State: {row['state']}.")
        kind = code.split(":", 1)[0]
        category = {"proxy": "ChemE-as-Code Atlas/proxies", "market": "ChemE-as-Code Atlas/markets"}.get(kind, f"ChemE-as-Code Atlas/{kind}")
        return self.flow(atlas_uuid("flow", code), row["reference product"], o.FlowType.PRODUCT_FLOW, row["unit"], code, category, " ".join(description))

    def exchange_flow(self, entry: dict, where: str) -> tuple[o.Ref, o.Ref | None, str]:
        """The flow of a non-product exchange, its default provider (an Atlas process) and a note."""
        if entry.get("atlas gap"):
            # a mapping gap of an unpublished process (ADR 0022): no provider, no elementary flow
            # identity; an Atlas flow in its own category, flagged, never mapped to a guess
            kind = o.FlowType.ELEMENTARY_FLOW if entry["type"] == "biosphere" else o.FlowType.PRODUCT_FLOW
            fid = atlas_uuid("flow", "gap", entry["type"], entry["name"], entry["unit"])
            ref = self.flow(fid, entry["name"], kind, entry["unit"], where, "ChemE-as-Code Atlas/unlinked (mapping gaps)", "UNLINKED: a mapping gap of a preliminary LCI; map it before use.")
            return ref, None, f"UNLINKED ({entry['atlas gap']})."
        if entry["type"] == "biosphere":
            categories = [c for c in str(entry.get("categories", "")).split("::") if c]
            if entry.get("atlas flow uuid"):
                fid = entry["atlas flow uuid"]
                note = "Identified by its biosphere3 UUID (the ecoinvent elementary exchange id, as distributed with bw2io); not an EF 3.1 UUID."
            else:
                fid = atlas_uuid("flow", "elementary", entry["name"], "::".join(categories), entry["unit"])
                note = "Atlas identifier (uuid5), NOT an EF 3.1 or ecoinvent UUID: map this flow to your elementary flow list by name and category."
            ref = self.flow(fid, entry["name"], o.FlowType.ELEMENTARY_FLOW, entry["unit"], where, "Elementary flows/" + "/".join(categories), note)
            return ref, None, ""
        if entry.get("atlas activity"):
            # another Atlas process makes this input (or takes this utility output): linked to it,
            # as install(prefer_atlas=True); the alternative is the background or an Atlas proxy
            alternative = {"name": entry["atlas activity"], "reference product": entry["atlas reference product"], "location": entry["atlas location"], "unit": entry["unit"]}
            flow, provider = self.atlas[_identity(alternative)]
            if entry.get("database") == self.db_name:
                return flow, provider, f"Alternative: the Atlas proxy {self._background_text(entry)} (in this package)."
            return flow, provider, f"Background alternative: {self._background_text(entry)}."
        if entry.get("database") == self.db_name:
            flow, provider = self.atlas[_identity(entry)]
            return flow, provider, ""
        name = entry["reference product"]
        fid = atlas_uuid("flow", "background", name, entry["unit"])
        ref = self.flow(
            fid, name, o.FlowType.PRODUCT_FLOW, entry["unit"], where, "ChemE-as-Code Atlas/background (map to your database)",
            "Background product named as in ecoinvent 3.11 cut-off (unchecked against a licensed copy); an Atlas identifier: map it to your background's flow (openLCA flow mapping).",
        )
        return ref, None, f"Provider by name: {self._background_text(entry)}."

    def _background_text(self, entry: dict) -> str:
        location = entry.get("location") or ""
        rule = " (the plant site: replace it with yours)" if entry.get("atlas location rule") == "site" else ""
        return f"{entry['name']} | {entry['reference product']} | {location}{rule}"


def _uncertainty(entry: dict) -> o.Uncertainty | None:
    """Brightway's lognormal (type 2, scale = ln(GSD)) as openLCA's (geometric mean, GSD); none
    for a negative amount (openLCA's lognormal has no negative flag)."""
    if entry.get("uncertainty type") != 2 or entry["amount"] <= 0:
        return None
    return o.Uncertainty(distribution_type=o.UncertaintyType.LOG_NORMAL_DISTRIBUTION, geom_mean=entry["amount"], geom_sd=math.exp(float(entry["scale"])))


def _description(entry: dict, note: str) -> str | None:
    parts = [f"Atlas key {entry['atlas key']}." if entry.get("atlas key") else ""]
    if entry.get("comment"):
        parts.append(f"{entry['comment']}.")
    if entry.get("atlas pedigree"):
        parts.append(f"Pedigree (reliability, completeness, temporal, geographical, technological): {entry['atlas pedigree']}.")
    if entry.get("atlas carrier"):
        parts.append(f"Carrier: {entry['atlas carrier']}.")
    if entry.get("amount") and entry["amount"] < 0 and entry.get("uncertainty type") == 2:
        parts.append("Lognormal uncertainty of the magnitude not exported (negative amount).")
    if note:
        parts.append(note)
    text = " ".join(p for p in parts if p)
    return text or None


def _exchanges(builder: _Olca, entries: list[dict], where: str, first_id: int) -> list[o.Exchange]:
    found = []
    for number, entry in enumerate(entries, start=first_id):
        flow, provider, note = builder.exchange_flow(entry, where)
        unit, prop = builder.units(entry["unit"], where)
        is_input = entry["type"] == "technosphere" or (entry["type"] == "biosphere" and _is_resource(entry))
        exchange = o.Exchange(
            internal_id=number, amount=entry["amount"], flow=flow, unit=unit, flow_property=prop, is_input=is_input,
            default_provider=provider, uncertainty=_uncertainty(entry), description=_description(entry, note),
        )
        found.append(exchange)
    return found


def _version(text: str) -> str:
    """A semantic version as openLCA's ``xx.yy.zzz``."""
    parts = [int(p) if p.isdigit() else 0 for p in (text.split(".") + ["0", "0"])[:3]]
    return f"{parts[0]:02d}.{parts[1]:02d}.{parts[2]:03d}"


def _factors(dataset: dict) -> tuple[list[o.AllocationFactor], o.AllocationType | None, list[str]]:
    """Allocation factors of a multi-output dataset: the build's method as the default type
    (its shares, exactly), and PHYSICAL (mass) or ECONOMIC (price) factors beside it where every
    product has the property."""
    products = dataset["products"]
    if len(products) < 2:
        return [], None, []
    method = dataset["allocation"]["method"]
    default = OLCA_DEFAULT[method]
    lines = [f"{default.value}: {method} (the build's method, default): " + ", ".join(f"{p['key']} {p['share']:.6g}" for p in products)]
    by_type = {default: {p["code"]: p["share"] for p in products}}
    for kind, prop in ((o.AllocationType.PHYSICAL_ALLOCATION, "mass"), (o.AllocationType.ECONOMIC_ALLOCATION, "price")):
        if kind in by_type or not all(prop in p["properties"] for p in products):
            continue
        weights = {p["code"]: p["amount"] * p["properties"][prop] for p in products}
        total = sum(weights.values())
        if total > 0:
            by_type[kind] = {k: v / total for k, v in weights.items()}
            lines.append(f"{kind.value}: {prop}: " + ", ".join(f"{p['key']} {by_type[kind][p['code']]:.6g}" for p in products))
    factors = []
    for kind, shares in by_type.items():
        if kind == o.AllocationType.CAUSAL_ALLOCATION:
            continue  # written per exchange by the caller
        for p in products:
            factors.append(o.AllocationFactor(allocation_type=kind, product=o.Ref(ref_type=o.RefType.Flow, id=atlas_uuid("flow", p["code"]), name=p["reference product"]), value=shares[p["code"]]))
    return factors, default, lines


def _documentation(dataset: dict, caveats: list[str]) -> o.ProcessDocumentation:
    doc = o.ProcessDocumentation()
    if dataset.get("technology"):
        doc.technology_description = str(dataset["technology"])
    if isinstance(dataset.get("valid_until"), int):
        doc.valid_until = f"{dataset['valid_until']}-12-31"
    doc.use_advice = " ".join(caveats)
    return doc


def build_jsonld(datasets: list[dict], proxies: list, markets: list, db_name: str, model: str, default: bool, site: str, header: list[str], caveats: list[str]) -> dict[str, bytes]:
    """The JSON-LD package as {path in the zip: bytes}."""
    builder = _Olca(db_name, model, default, site)
    # every Atlas activity's product flow and the process that provides it (a dataset's
    # multi-output process for its products, the proxy's own process)
    for dataset in datasets:
        pid = _process_id(dataset["code"], dataset.get("uuid"), model, default)
        for product in dataset["products"]:
            flow = builder.atlas_flow(product["code"], product)
            builder.atlas[_identity(product)] = (flow, o.Ref(ref_type=o.RefType.Process, id=pid, name=dataset["name"], location=dataset["location"]))
    for single in [*markets, *proxies]:
        code = single.row["code"]
        flow = builder.atlas_flow(code, single.row)
        builder.atlas[_identity(single.row)] = (flow, o.Ref(ref_type=o.RefType.Process, id=_process_id(code, None, model, default), name=single.row["name"], location=single.row["location"]))

    for dataset in datasets:
        where = dataset["path"]
        pid = _process_id(dataset["code"], dataset.get("uuid"), model, default)
        exchanges = []
        for number, product in enumerate(dataset["products"], start=1):
            unit, prop = builder.units(product["unit"], where)
            flow, _ = builder.atlas[_identity(product)]
            properties = ", ".join(f"{k} {v:g}" for k, v in sorted(product["properties"].items()))
            exchanges.append(
                o.Exchange(
                    internal_id=number, amount=product["amount"], flow=flow, unit=unit, flow_property=prop, is_input=False,
                    is_quantitative_reference=number == 1, description=f"Atlas key {product['key']}; activity {product['code']}; allocation properties: {properties or 'none'}.",
                )
            )
        others = _exchanges(builder, dataset["exchanges"], where, len(exchanges) + 1)
        factors, method, lines = _factors(dataset)
        if method == o.AllocationType.CAUSAL_ALLOCATION:
            for p in dataset["products"]:
                ref = o.Ref(ref_type=o.RefType.Flow, id=atlas_uuid("flow", p["code"]), name=p["reference product"])
                factors += [o.AllocationFactor(allocation_type=method, product=ref, value=p["share"], exchange=o.ExchangeRef(internal_id=e.internal_id)) for e in others]
        allocation = dataset["allocation"]
        description = [
            *header,
            f"Unallocated multi-output dataset {dataset['dataset']} ({dataset['path']}), basis {dataset['basis']}; process {dataset['process']}, maturity {dataset['maturity'] or 'unknown'}.",
            f"Allocation (docs/system-model.md): {allocation['method']}, source {allocation['source']}, hierarchy rule {allocation['rule']}: {allocation['reason']}",
            *(["Allocation factors: " + "; ".join(lines) + "."] if lines else []),
            *dataset["notes"],
            "Technosphere amounts are quantities of the linked reference product; an input that your background models as a waste treatment must be mapped to the waste flow as an output.",
        ]
        process = o.Process(
            id=pid, name=dataset["name"], category=f"ChemE-as-Code Atlas/{dataset['process']}", process_type=o.ProcessType.UNIT_PROCESS,
            location=builder.location(dataset["location"]), description="\n".join(description), version=_version(dataset["version"]), last_change=None,
            exchanges=exchanges + others, last_internal_id=len(exchanges) + len(others), process_documentation=_documentation(dataset, caveats),
        )
        if factors:
            process.allocation_factors = factors
            process.default_allocation_method = method
        builder.add("processes", process)

    for folder, group in (("markets", markets), ("proxies", proxies)):
        for single in group:
            code = single.row["code"]
            where = f"{folder}.{code}"
            flow, _ = builder.atlas[_identity(single.row)]
            unit, prop = builder.units(single.row["unit"], where)
            reference = o.Exchange(internal_id=1, amount=1.0, flow=flow, unit=unit, flow_property=prop, is_input=False, is_quantitative_reference=True)
            others = _exchanges(builder, single.exchanges[1:], where, 2)
            process = o.Process(
                id=_process_id(code, None, model, default), name=single.row["name"], category=f"ChemE-as-Code Atlas/{folder}", process_type=o.ProcessType.UNIT_PROCESS,
                location=builder.location(single.row["location"]), description="\n".join([*header, single.comment]), version="00.01.000", last_change=None,
                exchanges=[reference, *others], last_internal_id=1 + len(others), process_documentation=_documentation({}, caveats),
            )
            builder.add("processes", process)

    files = {"olca-schema.json": json.dumps({"version": 2}).encode("utf-8")}
    for (folder, eid), entity in sorted(builder.entities.items()):
        data = entity.to_dict()
        data.pop("lastChange", None)
        files[f"{folder}/{eid}.json"] = (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    return files


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    """A zip with sorted entries and fixed dates: byte-identical for the same content."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as target:
        for name in sorted(files):
            entry = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            target.writestr(entry, files[name])
    path.write_bytes(out.getvalue())


# --- Brightway multifunctional ------------------------------------------------------------------


def _strategy(dataset: dict) -> str:
    """The multifunctional strategy label that reproduces the build's shares: the property of
    the build's method when every product has it, else the build's ``share``."""
    method = dataset["allocation"]["method"]
    prop = MF_PROPERTY.get(method)
    if prop and all(prop in p["properties"] for p in dataset["products"]):
        return MF_STRATEGY[method]
    return "share"


def build_multifunctional(datasets: list[dict], proxies: list, markets: list, db_name: str, database_meta: dict, header: list[str], caveats: list[str]) -> dict:
    """The multifunctional database as JSON-ready data. Exchanges keep the workbook's linking
    fields; an exchange to an Atlas activity names its code in this database: ``atlas code`` for
    an exchange linked inside the Atlas (a market's supplier, link.dataset, a proxy), ``atlas
    activity code`` for an exchange linked there with ``prefer_atlas`` (a market or a plant; it
    takes precedence over a proxy's ``atlas code``); the codes of the
    allocated activities, the markets and the proxies are the workbook's."""
    codes = {}
    for dataset in datasets:
        for product in dataset["products"]:
            codes[_identity(product)] = product["code"]
    for single in [*markets, *proxies]:
        codes[_identity(single.row)] = single.row["code"]

    def linked(entry: dict) -> dict:
        entry = dict(entry)
        if entry.get("categories"):
            entry["categories"] = [c for c in str(entry["categories"]).split("::") if c]
        if entry.get("atlas activity"):
            # linked to the Atlas only with prefer_atlas: its code is the alternative's, not a fixed link
            code = codes[(entry["atlas activity"], entry["atlas reference product"], entry["atlas location"], entry["unit"])]
            given = entry.pop("atlas code", None)
            if given is not None and given != code:
                raise FormatError(f"{entry.get('atlas key')}: atlas code {given} is not the code of {entry['atlas activity']} ({code})")
            entry["atlas activity code"] = code
        if entry.get("database") == db_name:
            # fixed inside the Atlas (a market's supplier, link.dataset, a proxy); an exchange on a
            # proxy may also name an Atlas activity above (a utility output), which prefer_atlas takes
            entry["atlas code"] = codes[_identity(entry)]
            del entry["database"]
        return entry

    processes = []
    for dataset in datasets:
        functional = [
            {
                "name": p["reference product"], "unit": p["unit"], "amount": p["amount"], "type": "production", "functional": True,
                "desired_code": p["code"], "properties": dict(sorted({**p["properties"], "share": p["share"]}.items())), "atlas key": p["key"],
                **({"atlas properties source": p["properties_source"]} if p["properties_source"] else {}),
            }
            for p in dataset["products"]
        ]
        allocation = dataset["allocation"]
        comment = [
            *header,
            f"Unallocated multi-output dataset {dataset['dataset']} ({dataset['path']}), basis {dataset['basis']}; process {dataset['process']}, maturity {dataset['maturity'] or 'unknown'}.",
            f"Allocation (docs/system-model.md): {allocation['method']}, source {allocation['source']}, hierarchy rule {allocation['rule']}: {allocation['reason']}",
            *dataset["notes"],
            *caveats,
        ]
        single = len(functional) == 1  # one product: an ordinary process under its activity code
        first = dataset["products"][0]
        processes.append(
            {
                "code": first["code"] if single else dataset["code"], "name": dataset["name"], "location": dataset["location"],
                **({"type": "process", "reference product": first["reference product"], "unit": first["unit"]} if single else {"type": "multifunctional", "default_allocation": _strategy(dataset)}),
                "comment": "\n".join(comment),
                "atlas process": dataset["process"], "atlas dataset": dataset["dataset"], "atlas allocation": allocation["method"], "atlas allocation rule": allocation["rule"],
                **({"atlas dataset uuid": dataset["uuid"]} if dataset.get("uuid") else {}),
                "exchanges": functional + [linked(e) for e in dataset["exchanges"]],
            }
        )
    for single in [*markets, *proxies]:
        row = single.row
        production = {"name": row["reference product"], "unit": row["unit"], "amount": 1.0, "type": "production", "functional": True}
        own = {"atlas market": single.metadata["atlas market"], "atlas layer": single.metadata.get("atlas layer")} if single.metadata.get("atlas market") else {"atlas proxy": single.metadata.get("atlas proxy")}
        processes.append(
            {
                "code": row["code"], "name": row["name"], "reference product": row["reference product"], "unit": row["unit"], "location": row["location"], "type": "process",
                "comment": single.comment, **own, "exchanges": [production] + [linked(e) for e in single.exchanges[1:]],
            }
        )
    return {
        "schema": MULTIFUNCTIONAL_SCHEMA,
        "format": MULTIFUNCTIONAL_FORMAT,
        "package": MULTIFUNCTIONAL_PACKAGE,
        "database": f"{db_name}-multifunctional",
        "allocated_database": db_name,
        "metadata": dict(database_meta),
        "allocation_properties": PROPERTY_UNITS,
        "processes": sorted(processes, key=lambda p: p["code"]),
    }


# --- entry point ---------------------------------------------------------------------------------


def write_formats(lci: Path, db_name: str, datasets: list[dict], markets: list, proxies: list, model: str, default: bool, site: str, database_meta: dict, header: list[str], caveats: list[str]) -> list[dict]:
    """Write the JSON-LD zip and the multifunctional JSON into *lci*; return their resource
    entries (name, format, format_version, mediatype) for datapackage.json and index.json.
    Raises FormatError when a dataset cannot be expressed."""
    jsonld = f"{db_name}-olca-jsonld.zip"
    write_zip(lci / jsonld, build_jsonld(datasets, proxies, markets, db_name, model, default, site, header, caveats))
    multifunctional = f"{db_name}-multifunctional.json"
    data = build_multifunctional(datasets, proxies, markets, db_name, database_meta, header, caveats)
    (lci / multifunctional).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return [
        {"name": jsonld, "format": JSONLD_FORMAT, "format_version": JSONLD_FORMAT_VERSION, "written_with": OLCA_SCHEMA_PACKAGE, "mediatype": "application/zip"},
        {"name": multifunctional, "format": MULTIFUNCTIONAL_FORMAT, "format_version": MULTIFUNCTIONAL_SCHEMA, "for": MULTIFUNCTIONAL_PACKAGE, "mediatype": "application/json"},
    ]
