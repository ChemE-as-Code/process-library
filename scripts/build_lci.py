# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6", "jsonschema>=4.23", "openpyxl>=3.1"]
# ///
"""Build the Atlas LCI export: a Brightway foreground database from a process library.

Input, per process (``processes/<id>/``): core's unallocated LCI datasets (``kind:
lci_dataset``), ``lca/dataset.yaml`` of a plantcode project (``cheme assess lca --write``) and
any hand-written ``lca/datasets/*.yaml`` of a manifest-only process; ``process.yaml`` for the
title, maturity and the chemical slug of each inventory key; ``lca/lca.yaml`` for the study's
allocation and functional unit. Linking comes from ``lci/mappings.yaml`` (library root, else the
staged copy beside this script; schema ``schemas/lci-mappings.schema.json``). YAML files only:
chemeascode is never imported.

Output (``--out``; ``<out>/lci/`` is replaced):

- ``lci/cheme-as-code-atlas-<version>.xlsx``: one Brightway database in bw2io's ExcelImporter
  format (``bw2io.ExcelImporter``; layout as bw2io's ``data/examples/example.xlsx``): a
  ``Database`` section, then per activity its metadata rows and an ``Exchanges`` table.
- ``lci/datapackage.json``: version, library commit, per process its title, maturity, data and
  factor status, allocation, functional unit and activities.
- ``lci/index.json``: the summary the Atlas reads (files with size and sha256, activities per
  process, caveats).

Modelling rules (also written into every activity's ``comment``):

- one single-output activity per co-product, 1 unit of it, allocated with the study's method
  (``lca/lca.yaml``), else the dataset's default, else mass; the unallocated multi-output form
  is not exported;
- construction, maintenance, transport and end of life are technosphere inputs per unit of
  product, as core's dataset already spreads them over the plant's life;
- free inputs (ambient air) and free pass-through emissions are not exported (see mappings);
- a technosphere amount is the quantity of the linked activity's reference product, as in
  core's study; the installer flips the sign for a treatment activity (production -1);
- an input whose chemical another Atlas process produces names that activity too, so the
  installer can link it inside the Atlas (``prefer_atlas``).

Deterministic: sorted, no timestamps (the workbook's document properties and zip entry dates
are fixed), so two runs on the same input are byte-identical.

``--public`` exports only the processes with ``publication.status: public`` (``publication.py``);
an input another, unpublished process makes is then not linked to it. The LCI carries no
characterisation factors, so placeholder factors stay a caveat, as in the preview build.

    uv run build_lci.py --library ../process-library --out dist [--version 0.1.0] [--public]
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from openpyxl import Workbook

from publication import is_public

HERE = Path(__file__).resolve().parent
DATAPACKAGE_SCHEMA = "cheme-as-code/lci-datapackage/v1"
INDEX_SCHEMA = "cheme-as-code/lci-index/v1"
#: Schema strings of core's LCA files before and after the rename to cheme.
DATASET_SCHEMAS = ("cheme/lca/v1", "plantcode/lca/v1")
#: Inventory units of core's datasets -> Brightway unit names (core integrations/brightway.py).
BW_UNITS = {
    "kg": "kilogram",
    "kWh": "kilowatt hour",
    "m": "meter",
    "m2": "square meter",
    "m3": "cubic meter",
    "ea": "unit",
    "tkm": "ton kilometer",
}
EXCHANGE_TYPES = ("product", "input", "output", "emission")
KEY = re.compile(r"^[a-z][a-z-]*:[A-Za-z0-9_.\-]+$")
PROPORTIONAL = ("mass", "economic", "energy", "exergy", "shares")
#: Core marks an output whose components are counted by its emission:* exchanges this way.
RELEASED = "released to the environment"
DEFAULT_BACKGROUND = "ecoinvent-3.11-cutoff"
DEFAULT_BIOSPHERE = "biosphere3"
FIXED_TIME = datetime(2000, 1, 1)
EXCHANGE_COLUMNS = (
    "name",
    "amount",
    "unit",
    "type",
    "database",
    "reference product",
    "location",
    "categories",
    "uncertainty type",
    "loc",
    "scale",
    "comment",
    "atlas key",
    "atlas location rule",
    "atlas activity",
    "atlas reference product",
    "atlas location",
)
CAVEATS = (
    "No background data is included: link the database to the ecoinvent (or other) databases you "
    "are licensed for; background activities are referenced by name, reference product, unit and "
    "location only.",
    "The datasets are screening level (concept-stage flows and duties, about +/-30 %); check each "
    "process's maturity and review status before use.",
    "Screening proxies (code proxy:*) stand in where a dataset counts a flow in a unit the "
    "background has no activity for; their amounts are assumptions (see lci/mappings.yaml).",
    "Atmospheric pass-through emissions and the ambient air intake are not exported (curated "
    "decision in lci/mappings.yaml).",
)


class BuildError(Exception):
    """An input the builder cannot use; the message says where and why."""


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def _yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _git(library: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(["git", "-C", str(library), *args], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.strip()


def _number(value: float) -> float:
    """12 significant digits: stable text, far below any data's precision."""
    rounded = float(f"{value:.12g}")
    return 0.0 if rounded == 0 else rounded


def _base_dir(name: str) -> Path:
    """schemas/ or lci/ beside this script (library-kit) or one level up (process-library/scripts)."""
    for base in (HERE, HERE.parent):
        if (base / name).is_dir():
            return base / name
    raise SystemExit(f"{name}/ not found beside the builder")


# --- inputs ----------------------------------------------------------------------------------


def load_mappings(path: Path) -> dict:
    data = _yaml(path) or {}
    schema = json.loads((_base_dir("schemas") / "lci-mappings.schema.json").read_text(encoding="utf-8"))
    problems = [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]
    if problems:
        raise BuildError(f"{path}: " + "; ".join(problems))
    data.setdefault("proxies", {})
    data.setdefault("biosphere", {})
    data.setdefault("pass_through", {})
    data.setdefault("exchanges", {})
    for tid, entry in data["technosphere"].items():
        if "proxy" in entry and entry["proxy"] not in data["proxies"]:
            raise BuildError(f"{path}: technosphere.{tid}: unknown proxy {entry['proxy']!r}")
    for pid, proxy in data["proxies"].items():
        for item in proxy["inputs"]:
            target = data["technosphere"].get(item["use"])
            if target is None or "activity" not in target:
                raise BuildError(f"{path}: proxies.{pid}: input {item['use']!r} is not a technosphere entry with an activity")
    return data


def validate_dataset(data: Any, where: str) -> dict:
    """Check the fields of core's lci_dataset this builder relies on; raise BuildError."""
    problems: list[str] = []
    if not isinstance(data, dict):
        raise BuildError(f"{where}: not a mapping")
    if data.get("kind") != "lci_dataset":
        problems.append(f"kind is {data.get('kind')!r}, not 'lci_dataset'")
    if data.get("schema") not in DATASET_SCHEMAS:
        problems.append(f"schema {data.get('schema')!r} is not one of {', '.join(DATASET_SCHEMAS)}")
    if not isinstance(data.get("id"), str) or not re.fullmatch(r"[A-Za-z0-9_.\-]+", data.get("id") or ""):
        problems.append("id: missing or not [A-Za-z0-9_.-]+")
    if data.get("scope", "foreground") != "foreground":
        problems.append(f"scope {data.get('scope')!r}: only foreground datasets are exported (a linked dataset is already a footprint)")
    exchanges = data.get("exchanges")
    if not isinstance(exchanges, list) or not exchanges:
        problems.append("exchanges: missing or empty")
        exchanges = []
    keys: list[str] = []
    for number, exchange in enumerate(exchanges):
        at = f"exchanges[{number}]"
        if not isinstance(exchange, dict):
            problems.append(f"{at}: not a mapping")
            continue
        key = exchange.get("key")
        if not isinstance(key, str) or not KEY.match(key):
            problems.append(f"{at}: key {key!r} is not <kind>:<id>")
            continue
        at = key
        keys.append(key)
        if exchange.get("type") not in EXCHANGE_TYPES:
            problems.append(f"{at}: type {exchange.get('type')!r} is not one of {', '.join(EXCHANGE_TYPES)}")
        amount = exchange.get("amount")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount):
            problems.append(f"{at}: amount {amount!r} is not a finite number")
        if exchange.get("unit") not in BW_UNITS:
            problems.append(f"{at}: unit {exchange.get('unit')!r} is not one of {', '.join(BW_UNITS)}")
        link = exchange.get("link")
        if link is not None and not isinstance(link, dict):
            problems.append(f"{at}: link is not a mapping")
        if exchange.get("free") and link:
            problems.append(f"{at}: free takes no link")
        if exchange.get("type") == "product":
            if link or exchange.get("free"):
                problems.append(f"{at}: a product has no background")
            if isinstance(amount, (int, float)) and amount < 0:
                problems.append(f"{at}: a product's amount is negative")
    doubled = sorted({k for k in keys if keys.count(k) > 1})
    if doubled:
        problems.append(f"exchanges appear twice: {', '.join(doubled)}")
    if exchanges and not any(isinstance(e, dict) and e.get("type") == "product" for e in exchanges):
        problems.append("a dataset needs at least one product")
    allocation = data.get("allocation")
    if allocation is not None and not isinstance(allocation, dict):
        problems.append("allocation is not a mapping")
    if problems:
        raise BuildError(f"{where}: " + "; ".join(problems))
    return data


def _name(exchange: dict) -> str:
    return exchange["key"].split(":", 1)[1]


def _properties(exchange: dict, allocation: dict) -> dict:
    """A product's properties: the study's (allocation.properties, prices) over the dataset's."""
    own = dict(exchange.get("properties") or {})
    given = dict((allocation.get("properties") or {}).get(_name(exchange)) or {})
    if given.get("price") is None and _name(exchange) in (allocation.get("prices") or {}):
        given["price"] = allocation["prices"][_name(exchange)]
    return {k: given.get(k) if given.get(k) is not None else own.get(k) for k in ("price", "energy", "exergy")}


def shares(dataset: dict, allocation: dict, where: str) -> dict[str, float]:
    """Each product's share of the burdens (by key) under ``allocation['method']``, as core's
    ``allocation.weights``; raise BuildError when the method cannot apply."""
    products = [e for e in dataset["exchanges"] if e["type"] == "product"]
    method = allocation.get("method", "mass")
    if len(products) == 1:
        return {products[0]["key"]: 1.0}
    if method not in PROPORTIONAL:
        raise BuildError(
            f"{where}: allocation {method!r} cannot be exported as one activity per co-product; "
            f"use one of {', '.join(PROPORTIONAL)}"
        )
    raw: dict[str, float] = {}
    for product in products:
        name = _name(product)
        if method == "shares":
            value = (allocation.get("shares") or {}).get(name)
            if value is None:
                raise BuildError(f"{where}: allocation shares: no share of {name}")
            raw[product["key"]] = float(value)
        elif method == "mass":
            if product["unit"] != "kg":
                raise BuildError(f"{where}: mass allocation: {name} is counted in {product['unit']}, not kg")
            raw[product["key"]] = float(product["amount"])
        else:
            what = {"economic": "price", "energy": "energy", "exergy": "exergy"}[method]
            value = _properties(product, allocation)[what]
            if value is None:
                raise BuildError(f"{where}: {method} allocation: no {what} of {name}")
            raw[product["key"]] = float(product["amount"]) * float(value)
    total = sum(raw.values())
    if total <= 0:
        raise BuildError(f"{where}: {method} allocation gives the products no weight")
    return {k: v / total for k, v in raw.items()}


@dataclass
class Dataset:
    path: str  # from the library root
    data: dict
    allocation: dict
    allocation_source: str  # study | dataset | default
    shares: dict[str, float]


@dataclass
class Process:
    pid: str
    manifest: dict
    study: dict | None
    factors: dict | None
    datasets: list[Dataset]
    chemicals: dict[str, str]  # inventory key -> chemical slug (process.yaml)


def _discover(library: Path, report: Report, public: bool = False) -> list[Process]:
    processes = []
    for manifest_path in sorted((library / "processes").glob("*/process.yaml")):
        folder = manifest_path.parent
        files = []
        if (folder / "lca" / "dataset.yaml").is_file():
            files.append(folder / "lca" / "dataset.yaml")
        files.extend(sorted((folder / "lca" / "datasets").glob("*.yaml")))
        if not files:
            continue
        manifest = _yaml(manifest_path) or {}
        pid = manifest.get("id")
        if pid != folder.name:
            report.error(str(manifest_path.relative_to(library)), f"id {pid!r} differs from folder name {folder.name!r}")
            continue
        if public and not is_public(manifest):
            continue
        study = _yaml(folder / "lca" / "lca.yaml") if (folder / "lca" / "lca.yaml").is_file() else None
        factors = _yaml(folder / "lca" / "factors.yaml") if (folder / "lca" / "factors.yaml").is_file() else None
        chemicals = {}
        for group in ("inputs", "outputs", "utilities"):
            for item in (manifest.get("chemistry") or {}).get(group, []) or []:
                if item.get("inventory_key"):
                    chemicals[item["inventory_key"]] = item["chemical"]
        datasets = []
        for path in files:
            where = str(path.relative_to(library))
            try:
                data = validate_dataset(_yaml(path), where)
                study_allocation = (study or {}).get("allocation") if path.name == "dataset.yaml" else None
                if study_allocation:
                    allocation, source = study_allocation, "study"
                elif data.get("allocation"):
                    allocation, source = data["allocation"], "dataset"
                else:
                    allocation, source = {"method": "mass"}, "default"
                if source == "study" and data.get("allocation") and data["allocation"].get("method") != study_allocation.get("method"):
                    report.warn(where, f"study allocation {study_allocation.get('method')!r} differs from the dataset's default {data['allocation'].get('method')!r}: the study's is used")
                datasets.append(Dataset(where, data, allocation, source, shares(data, allocation, where)))
            except BuildError as failure:
                report.errors.append(str(failure))
        if datasets:
            processes.append(Process(pid, manifest, study, factors, datasets, chemicals))
    return processes


# --- linking ---------------------------------------------------------------------------------


def _chemical(process: Process, exchange: dict, mappings: dict, registry: set[str]) -> str | None:
    override = mappings["exchanges"].get(f"{process.pid}/{exchange['key']}") or mappings["exchanges"].get(exchange["key"]) or {}
    if override.get("chemical"):
        return override["chemical"]
    if exchange["key"] in process.chemicals:
        return process.chemicals[exchange["key"]]
    name = _name(exchange).lower()
    return name if name in registry else None


@dataclass
class Linker:
    mappings: dict
    db_name: str
    registry: set[str]
    #: chemical slug -> [(process id, activity row)] of every Atlas activity that makes it
    producers: dict[str, list[tuple[str, dict]]] = field(default_factory=dict)
    #: (path, product key) -> activity row, for link.dataset
    by_dataset: dict[tuple[str, str], dict] = field(default_factory=dict)
    proxies_used: set[str] = field(default_factory=set)

    def technosphere(self, tid: str, unit: str, where: str) -> dict:
        entry = self.mappings["technosphere"][tid]
        if "proxy" in entry:
            proxy = self.mappings["proxies"][entry["proxy"]]
            self.proxies_used.add(entry["proxy"])
            target = {
                "name": proxy["name"],
                "reference product": proxy["reference_product"],
                "unit": proxy["unit"],
                "location": proxy["location"],
                "database": self.db_name,
                "atlas location rule": "fixed",
            }
        else:
            activity = entry["activity"]
            site = activity["location"] == "site"
            target = {
                "name": activity["name"],
                "reference product": activity["reference_product"],
                "unit": activity["unit"],
                "location": self.mappings["default_site_location"] if site else activity["location"],
                "atlas location rule": "site" if site else "fixed",
            }
        if target["unit"] != unit:
            raise BuildError(f"{where}: mapped to {tid!r} in {target['unit']}, but the exchange is in {unit}")
        return target

    def resolve(self, process: Process, dataset: Dataset, exchange: dict) -> tuple[str, dict | str]:
        """``("skip", why)``, ``("technosphere", fields)`` or ``("biosphere", fields)``."""
        where = f"{dataset.path} {exchange['key']}"
        unit = BW_UNITS[exchange["unit"]]
        link = exchange.get("link") or {}
        if exchange.get("free"):
            if exchange["type"] == "emission":
                component = _name(exchange)
                if component not in self.mappings["pass_through"]:
                    raise BuildError(f"{where}: free emission of {component} is not in lci/mappings.yaml pass_through (curate the decision there)")
                return "skip", f"{exchange['key']} (pass-through: {self.mappings['pass_through'][component]['decision'].strip()})"
            return "skip", f"{exchange['key']} (free: {exchange.get('source') or 'no burden'})"
        if exchange["type"] == "output" and not link and str(exchange.get("source", "")).startswith(RELEASED):
            return "skip", f"{exchange['key']} (released to the environment: counted by its emission:* exchanges)"

        override = self.mappings["exchanges"].get(f"{process.pid}/{exchange['key']}") or self.mappings["exchanges"].get(exchange["key"]) or {}
        if override.get("use"):
            if override["use"] not in self.mappings["technosphere"]:
                raise BuildError(f"{where}: override uses unknown technosphere entry {override['use']!r}")
            return "technosphere", self.technosphere(override["use"], unit, where)

        if exchange["type"] == "emission":
            if link.get("biosphere"):
                flow = link["biosphere"]
                return "biosphere", {"name": flow["name"], "categories": list(flow.get("categories") or []), "unit": unit}
            component = _name(exchange)
            origin = (link.get("elementary") or {}).get("origin", "fossil")
            entry = self.mappings["biosphere"].get(f"{component}/{origin}") or self.mappings["biosphere"].get(component)
            if entry is None:
                raise BuildError(f"{where}: emission of {component} ({origin}) is not in lci/mappings.yaml biosphere")
            return "biosphere", {"name": entry["flow"]["name"], "categories": list(entry["flow"]["categories"]), "unit": unit}

        if link.get("biosphere"):
            flow = link["biosphere"]
            return "biosphere", {"name": flow["name"], "categories": list(flow.get("categories") or []), "unit": unit}
        if link.get("activity"):
            activity = link["activity"]
            location = activity.get("location")
            return "technosphere", {
                "name": activity["name"],
                "reference product": activity.get("reference_product") or "",
                "unit": unit,
                "location": location or self.mappings["default_site_location"],
                "atlas location rule": "fixed" if location else "site",
            }
        if link.get("dataset"):
            ref = link["dataset"]
            product = ref["product"] if ":" in ref["product"] else f"product:{ref['product']}"
            row = self.by_dataset.get((ref["path"], product))
            if row is None:
                raise BuildError(f"{where}: link.dataset {ref['path']}#{product} is not an exported Atlas dataset of this library")
            return "technosphere", {**self._own(row), "atlas location rule": "fixed"}

        chemical = _chemical(process, exchange, self.mappings, self.registry)
        if chemical and chemical in self.mappings["technosphere"]:
            return "technosphere", self.technosphere(chemical, unit, where)
        factor = link.get("factor")
        if factor and factor in self.mappings["technosphere"]:
            return "technosphere", self.technosphere(factor, unit, where)
        tried = ", ".join(x for x in (f"chemical {chemical!r}" if chemical else "", f"factor {factor!r}" if factor else "") if x) or "no chemical slug or factor id"
        raise BuildError(f"{where}: no mapping ({tried}); add it to lci/mappings.yaml technosphere or exchanges")

    def _own(self, row: dict) -> dict:
        return {"name": row["name"], "reference product": row["reference product"], "unit": row["unit"], "location": row["location"], "database": self.db_name}

    def atlas_alternative(self, process: Process, exchange: dict, unit: str) -> tuple[dict | None, list[str]]:
        """The Atlas activity of another process that makes this input's chemical, and the other
        candidates when several do (the first by process id and name is taken: deterministic,
        and reported, so that a second producer never replaces the first silently)."""
        if exchange["type"] != "input":
            return None, []
        chemical = _chemical(process, exchange, self.mappings, self.registry)
        candidates = sorted(
            ((pid, row) for pid, row in self.producers.get(chemical or "", []) if pid != process.pid and row["unit"] == unit),
            key=lambda c: (c[0], c[1]["name"]),
        )
        if not candidates:
            return None, []
        return candidates[0][1], [f"{pid}: {row['name']}" for pid, row in candidates[1:]]


# --- activities ------------------------------------------------------------------------------


def _uncertainty(exchange: dict, amount: float) -> dict:
    """A lognormal gsd2 as Brightway's lognormal (type 2): loc ln(amount), scale ln(gsd2)/2."""
    given = exchange.get("uncertainty") or {}
    if given.get("distribution", "lognormal") != "lognormal" or not given.get("gsd2") or amount <= 0:
        return {}
    return {"uncertainty type": 2, "loc": _number(math.log(amount)), "scale": _number(math.log(given["gsd2"]) / 2)}


def _product_rows(process: Process, dataset: Dataset, registry_names: dict[str, str]) -> list[dict]:
    rows = []
    location = dataset.data.get("location") or "GLO"
    for exchange in dataset.data["exchanges"]:
        if exchange["type"] != "product" or dataset.shares.get(exchange["key"], 0.0) <= 0:
            continue
        chemical = process.chemicals.get(exchange["key"])
        title = exchange.get("title") or _name(exchange)
        name = registry_names.get(chemical or "", "")
        product = title if not name or name.lower() in title.lower() else f"{name}, {title}"
        rows.append(
            {
                "code": f"{process.pid}:{dataset.data['id']}:{exchange['key']}",
                "name": f"{process.manifest['title']}",
                "reference product": product,
                "unit": BW_UNITS[exchange["unit"]],
                "location": location,
                "key": exchange["key"],
                "amount": float(exchange["amount"]),
                "chemical": chemical,
            }
        )
    return rows


def _factors_status(factors: dict | None) -> str:
    if not factors:
        return "none"
    if factors.get("example"):
        return "placeholder"
    statuses = {f.get("status") for f in factors.get("factors", [])}
    return "published" if statuses <= {"PUBLISHED", "EPD"} else "mixed"


def _data_status(dataset: dict) -> dict[str, int]:
    counts = {"given": 0, "calculated": 0, "assumed": 0}
    for exchange in dataset["exchanges"]:
        counts[exchange.get("provenance", "assumed")] = counts.get(exchange.get("provenance", "assumed"), 0) + 1
    return counts


def _functional_unit(study: dict | None) -> dict | None:
    fu = (study or {}).get("functional_unit")
    if not fu:
        return None
    return {"product": fu.get("product"), "amount": fu.get("amount", 1.0), "unit": fu.get("unit", "t")}


def _comment(process: Process, dataset: Dataset, row: dict, skipped: list[str], commit: str | None, version: str) -> str:
    method = dataset.allocation.get("method", "mass")
    share_text = ", ".join(f"{_name({'key': k})} {v * 100:.1f} %" for k, v in sorted(dataset.shares.items(), key=lambda kv: -kv[1]))
    allocation_source = {"study": "the study's (lca/lca.yaml)", "dataset": "the dataset's default", "default": "the default (mass)"}[dataset.allocation_source]
    lines = [
        f"ChemE-as-Code Process Atlas, process {process.pid}: {process.manifest['title']}.",
        f"Maturity: {process.manifest.get('maturity', 'unknown')}; review: {(process.manifest.get('validation') or {}).get('status', 'unknown')}. Screening-level data.",
        f"1 {row['unit']} of {row['reference product']}, from the unallocated LCI dataset {dataset.data['id']} ({dataset.path}, basis {dataset.data.get('basis', '1 h of operation')}).",
        f"Allocation: {method}, {allocation_source}; shares {share_text}. One single-output activity per co-product; the multi-output form is not exported.",
        "Construction, maintenance, transport and end of life are technosphere inputs per unit of product, spread over the plant's life as in the dataset.",
        "Technosphere amounts are quantities of the linked reference product (a treatment activity is linked with the sign flipped by the installer).",
    ]
    if skipped:
        lines.append("Not exported: " + "; ".join(skipped) + ".")
    if dataset.allocation.get("source"):
        lines.append(f"Allocation source: {' '.join(str(dataset.allocation['source']).split())}")
    lines.append(f"Atlas LCI {version}; library commit {commit or 'unknown'}.")
    return "\n".join(lines)


@dataclass
class Activity:
    row: dict
    comment: str
    metadata: dict
    exchanges: list[dict]


def build_activities(processes: list[Process], mappings: dict, registry: dict[str, dict], db_name: str, commit: str | None, version: str, report: Report) -> tuple[list[Activity], list[Activity], dict[str, list[dict]]]:
    names = {slug: c.get("name", slug) for slug, c in registry.items()}
    linker = Linker(mappings, db_name, set(registry))
    rows_by_process: dict[str, list[tuple[Dataset, dict]]] = {}
    for process in processes:
        for dataset in process.datasets:
            for row in _product_rows(process, dataset, names):
                rows_by_process.setdefault(process.pid, []).append((dataset, row))
                linker.by_dataset[(dataset.path, row["key"])] = row
                if row["chemical"]:
                    linker.producers.setdefault(row["chemical"], []).append((process.pid, row))
    for producers in linker.producers.values():
        producers.sort(key=lambda p: (p[0], p[1]["code"]))

    activities: list[Activity] = []
    for process in processes:
        for dataset, row in rows_by_process.get(process.pid, []):
            per_unit = dataset.shares[row["key"]] / row["amount"] if row["amount"] > 0 else None
            if per_unit is None:
                report.error(dataset.path, f"{row['key']} has no amount")
                continue
            exchanges = [
                {
                    "name": row["name"],
                    "amount": 1.0,
                    "unit": row["unit"],
                    "type": "production",
                    "database": db_name,
                    "reference product": row["reference product"],
                    "location": row["location"],
                    "atlas key": row["key"],
                }
            ]
            skipped: list[str] = []
            for exchange in dataset.data["exchanges"]:
                if exchange["type"] == "product":
                    continue
                try:
                    kind, target = linker.resolve(process, dataset, exchange)
                except BuildError as failure:
                    report.errors.append(str(failure))
                    continue
                if kind == "skip":
                    skipped.append(str(target))
                    continue
                amount = _number(float(exchange["amount"]) * per_unit)
                entry = {"amount": amount, "type": kind, "atlas key": exchange["key"], **target}
                if kind == "biosphere":
                    entry["categories"] = "::".join(target["categories"])
                else:
                    alternative, others = linker.atlas_alternative(process, exchange, target["unit"])
                    if others:
                        report.warn(
                            f"{process.pid}: {exchange['key']}",
                            f"several Atlas producers: {alternative['name']} is used, not {', '.join(others)}; link one explicitly (link.dataset) to choose",
                        )
                    if alternative is not None and target.get("database") != db_name:
                        entry.update({"atlas activity": alternative["name"], "atlas reference product": alternative["reference product"], "atlas location": alternative["location"]})
                entry.update(_uncertainty(exchange, amount))
                if exchange.get("title"):
                    entry["comment"] = exchange["title"]
                exchanges.append(entry)
            comment = _comment(process, dataset, row, skipped, commit, version)
            metadata = {
                "code": row["code"],
                "reference product": row["reference product"],
                "unit": row["unit"],
                "location": row["location"],
                "type": "process",
                "production amount": 1,
                "comment": comment,
                "atlas process": process.pid,
                "atlas dataset": dataset.data["id"],
                "atlas maturity": process.manifest.get("maturity", ""),
                "atlas allocation": dataset.allocation.get("method", "mass"),
            }
            activities.append(Activity(row, comment, metadata, exchanges))

    proxies: list[Activity] = []
    for pid in sorted(linker.proxies_used):
        proxy = mappings["proxies"][pid]
        row = {"code": f"proxy:{pid}", "name": proxy["name"], "reference product": proxy["reference_product"], "unit": proxy["unit"], "location": proxy["location"]}
        exchanges = [{"name": row["name"], "amount": 1.0, "unit": row["unit"], "type": "production", "database": db_name, "reference product": row["reference product"], "location": row["location"]}]
        for item in proxy["inputs"]:
            target = linker.technosphere(item["use"], mappings["technosphere"][item["use"]]["activity"]["unit"], f"proxies.{pid}")
            exchanges.append({"amount": _number(item["amount"]), "type": "technosphere", "atlas key": f"proxy:{item['use']}", "comment": item["source"], **target})
        comment = "\n".join(
            [
                "Atlas screening proxy (lci/mappings.yaml): stands in where datasets count a flow in a unit the background has no activity for.",
                f"{' '.join(proxy['source'].split())}",
                "Inputs: " + "; ".join(f"{i['use']} {i['amount']:g}: {i['source']}" for i in proxy["inputs"]),
                f"Atlas LCI {version}; library commit {commit or 'unknown'}.",
            ]
        )
        metadata = {"code": row["code"], "reference product": row["reference product"], "unit": row["unit"], "location": row["location"], "type": "process", "production amount": 1, "comment": comment, "atlas proxy": pid}
        proxies.append(Activity(row, comment, metadata, exchanges))

    by_process = {pid: [r for _, r in rows] for pid, rows in rows_by_process.items()}
    return activities, proxies, by_process


# --- workbook --------------------------------------------------------------------------------


def _activity_block(activity: Activity) -> list[list[Any]]:
    rows: list[list[Any]] = [["Activity", activity.row["name"]]]
    rows.extend([key, value] for key, value in activity.metadata.items())
    rows.append(["Exchanges"])
    columns = [c for c in EXCHANGE_COLUMNS if any(c in e for e in activity.exchanges)]
    rows.append(list(columns))
    for exchange in activity.exchanges:
        rows.append([exchange.get(c) for c in columns])
    rows.append([])
    return rows


def write_workbook(path: Path, db_name: str, database_meta: dict, activities: list[Activity], proxies: list[Activity], about: list[str]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "about"
    # A1 = "skip": bw2io's ExcelImporter ignores this sheet.
    ws.append(["skip"])
    for line in about:
        ws.append([line])
    ws = wb.create_sheet("database")
    ws.append(["Database", db_name])
    for key, value in database_meta.items():
        ws.append([key, value])
    sheets: dict[str, list[Activity]] = {}
    for activity in activities:
        sheets.setdefault(activity.metadata["atlas process"], []).append(activity)
    for pid, group in sorted(sheets.items()):
        ws = wb.create_sheet(pid[:31])
        for activity in group:
            for row in _activity_block(activity):
                ws.append(row)
    if proxies:
        ws = wb.create_sheet("proxies")
        for activity in proxies:
            for row in _activity_block(activity):
                ws.append(row)
    wb.properties.creator = "ChemE-as-Code Process Atlas (build_lci.py)"
    wb.properties.created = FIXED_TIME
    wb.properties.modified = FIXED_TIME
    buffer = io.BytesIO()
    wb.save(buffer)
    _normalise_zip(buffer.getvalue(), path)


def _normalise_zip(raw: bytes, path: Path) -> None:
    """Rewrite the xlsx with fixed entry dates and document timestamps (openpyxl stamps the
    save time into docProps/core.xml and every zip entry)."""
    stamp = FIXED_TIME.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as source, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "docProps/core.xml":
                text = data.decode("utf-8")
                text = re.sub(r"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:)", rf"\g<1>{stamp}\g<2>", text)
                data = text.encode("utf-8")
            entry = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            target.writestr(entry, data)
    path.write_bytes(out.getvalue())


# --- build -----------------------------------------------------------------------------------


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(library: Path, out: Path, version: str, commit: str | None = None, mappings_path: Path | None = None, public: bool = False) -> Report:
    report = Report()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]*", version):
        report.error("--version", f"{version!r}: letters, digits and . + _ - only")
        return report
    mappings_path = mappings_path or (library / "lci" / "mappings.yaml")
    if not mappings_path.is_file():
        mappings_path = _base_dir("lci") / "mappings.yaml"
    try:
        mappings = load_mappings(mappings_path)
    except BuildError as failure:
        report.errors.append(str(failure))
        return report
    registry_path = library / "chemicals" / "chemicals.yaml"
    if not registry_path.is_file():
        report.error(str(registry_path), "missing chemical registry")
        return report
    registry = {c["slug"]: c for c in (_yaml(registry_path) or {}).get("chemicals", [])}

    own_repo = _git(library, "rev-parse", "--show-toplevel") == str(library)
    if commit is None and own_repo:
        commit = _git(library, "rev-parse", "HEAD")
    dirty = bool(_git(library, "status", "--porcelain")) if own_repo else None

    processes = _discover(library, report, public)
    db_name = f"cheme-as-code-atlas-{version}"
    activities, proxies, by_process = build_activities(processes, mappings, registry, db_name, commit, version, report)
    if report.errors:
        return report
    if not activities:
        report.warn(str(library), "no process has an LCI dataset (processes/<id>/lca/dataset.yaml or lca/datasets/*.yaml)")

    lci = out / "lci"
    if lci.exists():
        shutil.rmtree(lci)
    lci.mkdir(parents=True)
    xlsx_name = f"{db_name}.xlsx"
    about = [
        f"ChemE-as-Code Process Atlas: LCI foreground database {db_name}.",
        "Brightway 2.5 (bw2io ExcelImporter) format. This sheet is skipped by the importer (A1 = skip).",
        "Import: pip install the helper (process-library python/, package cheme-as-code-lci), then cheme_as_code_lci.install(path, background=<your ecoinvent database>, location=<site country>).",
        f"Library commit: {commit or 'unknown'}. Mappings: lci/mappings.yaml. Details per process: datapackage.json.",
        *CAVEATS,
    ]
    database_meta = {
        "format": "ChemE-as-Code Process Atlas LCI (bw2io Excel)",
        "atlas version": version,
        "atlas library commit": commit or "unknown",
        "atlas default background": DEFAULT_BACKGROUND,
        "atlas default site location": mappings["default_site_location"],
    }
    write_workbook(lci / xlsx_name, db_name, database_meta, activities, proxies, about)

    def activity_list(rows: list[dict]) -> list[dict]:
        return [{"code": r["code"], "name": r["name"], "reference_product": r["reference product"], "unit": r["unit"], "location": r["location"]} for r in rows]

    process_entries = []
    for process in processes:
        first = process.datasets[0]
        process_entries.append(
            {
                "id": process.pid,
                "title": process.manifest.get("title", process.pid),
                "maturity": process.manifest.get("maturity"),
                "validation": (process.manifest.get("validation") or {}).get("status"),
                "factors_status": _factors_status(process.factors),
                "functional_unit": _functional_unit(process.study),
                "allocation": {"method": first.allocation.get("method", "mass"), "source": first.allocation_source},
                "datasets": [
                    {
                        "id": d.data["id"],
                        "path": d.path,
                        "basis": d.data.get("basis", "1 h of operation"),
                        "allocation": {"method": d.allocation.get("method", "mass"), "source": d.allocation_source, "shares": {k: _number(v) for k, v in sorted(d.shares.items())}},
                        "data_status": _data_status(d.data),
                        "generator": (d.data.get("provenance") or {}).get("generator", ""),
                    }
                    for d in process.datasets
                ],
                "activities": activity_list(by_process.get(process.pid, [])),
            }
        )
    datapackage = {
        "schema": DATAPACKAGE_SCHEMA,
        "name": db_name,
        "version": version,
        "format": "bw2io ExcelImporter workbook",
        "library": {"commit": commit, "dirty": dirty},
        "brightway": {"database": db_name, "default_background": DEFAULT_BACKGROUND, "default_biosphere": DEFAULT_BIOSPHERE, "default_site_location": mappings["default_site_location"]},
        "resources": [{"path": xlsx_name, "mediatype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}],
        "processes": process_entries,
        "proxies": activity_list([p.row for p in proxies]),
        "caveats": list(CAVEATS),
    }
    _write_json(lci / "datapackage.json", datapackage)

    caveats = list(CAVEATS)
    for entry in process_entries:
        if entry["factors_status"] == "placeholder":
            caveats.append(f"{entry['id']}: the study's characterisation factors are placeholders (example: true); the LCI carries no factors, but its plantcode results are not meaningful numbers.")
    index = {
        "schema": INDEX_SCHEMA,
        "version": version,
        "database": db_name,
        "library_commit": commit,
        "files": [
            {"name": name, "path": f"lci/{name}", "bytes": (lci / name).stat().st_size, "sha256": _sha256(lci / name)}
            for name in (xlsx_name, "datapackage.json")
        ],
        "processes": {e["id"]: [{"code": a["code"], "name": a["name"], "reference_product": a["reference_product"], "unit": a["unit"]} for a in e["activities"]] for e in process_entries},
        "caveats": caveats,
    }
    _write_json(lci / "index.json", index)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, required=True, help="library root (holds processes/ and chemicals/)")
    parser.add_argument("--out", type=Path, required=True, help="output directory; <out>/lci/ is replaced")
    parser.add_argument("--version", default="dev", help="database version, part of its name and file name (default: dev)")
    parser.add_argument("--commit", help="library commit to record (default: git HEAD of --library)")
    parser.add_argument("--mappings", type=Path, help="lci/mappings.yaml (default: <library>/lci/, else the staged copy)")
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--public", action="store_true", help="published processes only (publication.status: public)")
    args = parser.parse_args(argv)

    report = build(args.library.resolve(), args.out.resolve(), args.version, args.commit, args.mappings.resolve() if args.mappings else None, args.public)
    for message in report.warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in report.errors:
        print(f"error: {message}", file=sys.stderr)
    failed = bool(report.errors or (args.strict and report.warnings))
    if not failed:
        index = json.loads((args.out / "lci" / "index.json").read_text(encoding="utf-8"))
        count = sum(len(v) for v in index["processes"].values())
        print(f"lci: {count} activit{'y' if count == 1 else 'ies'} from {len(index['processes'])} process(es) -> {args.out / 'lci'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
