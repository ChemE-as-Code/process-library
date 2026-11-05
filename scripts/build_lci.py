# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6", "jsonschema>=4.23", "openpyxl>=3.1", "olca-schema==2.6.2"]
# ///
"""Build the Atlas LCI export: a Brightway foreground database from a process library.

Input, per process (``processes/<id>/``): core's unallocated LCI datasets (``kind:
lci_dataset``; schema ``cheme/lci_dataset/v2``, and the v1 files), ``lca/dataset.yaml`` of a plantcode project (``cheme assess lca --write``),
a design case's own ``lca/datasets/<dataset id>-<case>.yaml`` beside it (``--write --case``, ADR 0034: its
activities are named ``<title>, case <case>``) and any hand-written ``lca/datasets/*.yaml`` of a
manifest-only process; ``process.yaml`` for the
title, maturity and the chemical slug of each inventory key; ``lca/lca.yaml`` for the study's
allocation and functional unit. Linking comes from ``lci/mappings.yaml`` (library root, else the
process library's own beside this script; schema ``schemas/lci-mappings.schema.json``), the shared
vocabulary, merged with each process's own exchange overrides in
``processes/<id>/lca/mappings.yaml`` (schema ``schemas/lci-process-mappings.schema.json``; the
same exchange in both is an error, ADR 0022); the
latest check of its background names against a licensed background (``lci/mapping-checks/``,
``check_mappings.py``) is recorded in ``datapackage.json`` (``brightway.background_check``). YAML files only:
chemeascode is never imported, except ``foundation.units`` for the benchmark unit conversion
(``benchmarks.convert``) and ``lca.cutoff`` for the cut-off criteria (``cutoff_results``), both
lazily.

Output (``--out``; ``<out>/lci/`` is replaced):

- ``lci/cheme-as-code-atlas-<version>.xlsx``: one Brightway database in bw2io's ExcelImporter
  format (``bw2io.ExcelImporter``; layout as bw2io's ``data/examples/example.xlsx``): a
  ``Database`` section, then per activity its metadata rows and an ``Exchanges`` table.
- ``lci/cheme-as-code-atlas-<version>-olca-jsonld.zip`` (openLCA JSON-LD) and
  ``lci/cheme-as-code-atlas-<version>-multifunctional.json`` (Brightway ``multifunctional``): the
  unallocated multi-output datasets, written by ``export_formats.py`` from the same activities;
- ``lci/datapackage.json``: version, library commit, per process its title, maturity, data and
  factor status, allocation, functional unit and activities; and ``activities``, per exported
  activity what its Atlas page shows (exchanges per reference unit with provenance, pedigree and
  link targets, header metadata, allocation, closure, citation, downloads; ``lci_activities.py``).
- ``lci/benchmarks.json``: every KPI result of the build with its allocated value and the counts
  by status (``benchmarks.report``, docs/benchmarks.md), the stored report of the comparison
- ``lci/gaps.json``: the mapping gaps per process (below), always
  written (``count`` 0 without gaps);
- ``lci/index.json``: the summary the Atlas reads (files with size, sha256, format and format
  version, activities per process, caveats).
- with ``--previous <dir>`` (an earlier build): ``lci/changes.json`` and ``lci/CHANGES.md``, the
  change report per dataset and activity (exchanges added, removed and changed) with the delta of
  a reference impact set per activity (``reference_impacts.py``: core's packaged IPCC 2021 GWP100
  on the Atlas foreground, no background; the report states what that leaves out).

Modelling rules (``docs/system-model.md``; also written into every activity's ``comment``):

- one system model per build: attributional cut-off (``system_model`` in the mappings). A
  cut-off build has no avoided-burden credits: an exchange mapped to ``cutoff_exclusions`` is
  left out with its decision, and a negative technosphere exchange is refused.
  ``--system-model substitution`` builds the labelled variant
  ``cheme-as-code-atlas-<version>-substitution`` with the credits of ``substitution:``;
- one single-output activity per co-product, 1 unit of it, allocated by the hierarchy: the
  curated rule of ``allocation:`` in the mappings, else the study's (``lca/lca.yaml``) or the
  dataset's method when it fits the WBCSD price-ratio rule or states its ``allocation.deviation``;
  otherwise a finding (``--strict`` fails). The unallocated multi-output form is in the
  JSON-LD and multifunctional files (``export_formats.py``), not in the workbook;
- the v2 contract: a ``resource`` exchange and an emission are biosphere exchanges
  identified by the biosphere3 UUID of their ``flow:`` identity (``atlas flow uuid``), name and
  categories as fallback; units are brought to one per kind (g, t to kg ...) or refused when
  Brightway has none (ea*h, ea*a); the pedigree is exported (``atlas pedigree``) with
  the lognormal it implies when the exchange has no distribution of its own; a dataset's version,
  methodology version, review, valid_until, system model and ``superseded_by`` (a deprecated
  dataset stays in the database with a pointer) are read, and its rating from ``lca/manifest.json``;
- construction, maintenance, transport and end of life are technosphere inputs per unit of
  product, as core's dataset already spreads them over the plant's life;
- free inputs (ambient air) and free pass-through emissions are not exported (see mappings);
- a technosphere amount is the quantity of the linked activity's reference product, as in
  core's study; the installer flips the sign for a treatment activity (production -1);
- markets (``markets/<substance>.yaml``, ``markets.py``, docs/markets.md) are activities of the
  same database, code ``market:<product>:<region>``: their Atlas producers weighted by production
  volume or sourced shares, transport legs in ton kilometer and losses, per kg delivered;
- an input whose chemical another Atlas process produces names an Atlas activity too, so the
  installer can link it inside the Atlas (``prefer_atlas``): the market of the input's grade
  (``markets.choose``) by default, with the plant (a producer of the same registry grade first)
  beside it for pinning. A producer of another grade is refused. Every Atlas-to-Atlas link
  carries a compatibility check (grade, unit, system model, allocation, boundary), written into
  the workbook (``atlas check``) and ``datapackage.json`` (``atlas_links``); a link at a plant
  gate because no market of the grade exists is a warning;
- a product's reference product is its registry grade's name when its flow has one
  (``registry.flow_grade``), else the substance's name with the exchange title; activity codes do
  not depend on it. ``datapackage.json`` activities carry ``chemical`` and ``grade``;
- each product's study ``exergy`` and ``energy`` are checked against the registry
  (``property_checks``, recorded per dataset in ``datapackage.json``); a mismatch over 2 %
  without a ``properties_reason`` is a warning;
- each dataset's KPIs of the benchmark registry (``benchmarks/<family>.yaml``, ``benchmarks.py``)
  are evaluated and recorded per dataset in ``datapackage.json`` (``benchmarks``): a value outside
  its reference range without an ``out_of_range_reason``, a KPI not evaluated (a unit conversion
  needs core's ``foundation.units``) and, in a library with a ``benchmarks/`` folder, a public
  process with fewer than two KPIs are warnings.
- the cut-off criteria (docs/system-model.md section 4) of a dataset that records its cut flows
  (``cutoff:``) are checked with core's ``lca.cutoff`` and recorded per dataset in
  ``datapackage.json`` (``cutoff``): a cut flow at or above 1 % of the input mass, the cut flows
  together at or above 1 %, a never-cut flow (precious or critical metal, high characterisation
  factor, heavy metal) and, without core installed, criteria not checked are warnings;

Errors (exit 1): ``chemicals/chemicals.yaml`` failing its schema or ``registry.check`` (checked
first, before any process is read), a benchmark file failing its schema or ``benchmarks.load``,
a market file failing its schema or ``markets.load``, a market whose supplier makes no activity of
its product, an unknown grade, a dataset that fails validation, an
allocation that cannot be exported. Warnings fail ``--strict``, except a public process with too
few benchmarked KPIs (``Report.advisories``, ADR 0026), which stays a warning.

Gaps (ADR 0022, ADR 0026): an exchange of any process, public or not, in any build, with no
technosphere mapping or no biosphere identity is neither an error nor a warning: it is reported (``Report.gaps``, ``gap:``
lines, ``lci/gaps.json``, ``datapackage.json`` ``processes[].gaps``, ``index.json`` ``gaps``) and
exported unlinked with its amount: no database, categories or Atlas alternative, column
``atlas gap``, the activity's ``atlas gaps`` and an ``UNLINKED`` comment line; never linked to a
guess, dropped or zero-filled. ``--strict`` does not fail on gaps.

Deterministic: sorted, no timestamps (the workbook's document properties and zip entry dates
are fixed), so two runs on the same input are byte-identical.

``--public`` exports only the processes with ``publication.status: public`` (``publication.py``);
an input another, unpublished process makes is then not linked to it. The LCI carries no
characterisation factors, so placeholder factors stay a caveat, as in the preview build.

    uv run build_lci.py --library ../process-library --out dist [--version 0.1.0] [--public]
        [--system-model substitution] [--previous <earlier build>]
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
from pathlib import Path, PurePath
from types import SimpleNamespace
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from openpyxl import Workbook
from referencing import Registry, Resource

import benchmarks as bm
import check_mappings
import export_formats
import lci_activities
import markets as mk
import reference_impacts
import registry as reg
from publication import is_public

HERE = Path(__file__).resolve().parent
#: a process's own exchange overrides, beside its LCI (ADR 0022)
PROCESS_MAPPINGS = Path("lca") / "mappings.yaml"
DATAPACKAGE_SCHEMA = "cheme-as-code/lci-datapackage/v1"
GAPS_SCHEMA = "cheme-as-code/lci-gaps/v1"
INDEX_SCHEMA = "cheme-as-code/lci-index/v1"
#: Schema strings of core's LCI dataset: v2 and the v1 files it still reads, which
#: declared the LCA files' id (``cheme/lca/v1``, and ``plantcode/lca/v1`` before the rename).
DATASET_SCHEMAS = ("cheme/lci_dataset/v2", "cheme/lca/v1", "plantcode/lca/v1")
#: Inventory units of core's datasets (``foundation.units.LCI_UNITS``) -> (the unit the export
#: counts the quantity in, factor to it). The export's units are the keys of ``BW_UNITS``.
UNIT_SCALING = {
    "kg": ("kg", 1.0),
    "g": ("kg", 0.001),
    "t": ("kg", 1000.0),
    "kWh": ("kWh", 1.0),
    "MWh": ("kWh", 1000.0),
    "MJ": ("MJ", 1.0),
    "GJ": ("MJ", 1000.0),
    "m": ("m", 1.0),
    "km": ("m", 1000.0),
    "m2": ("m2", 1.0),
    "m2*a": ("m2*a", 1.0),
    "m2*year": ("m2*a", 1.0),  # how the crosswalk writes biosphere3's unit
    "m3": ("m3", 1.0),
    "L": ("m3", 0.001),
    "ea": ("ea", 1.0),
    "tkm": ("tkm", 1.0),
    "kBq": ("kBq", 1.0),
    # biosphere3 and bw2io count gas volumes at a reference state in these units (e.g. Gas, natural in
    # Sm3); the reference state is core's (Nm3: 0 C, 1.01325 bar) and is not converted here
    "Nm3": ("Nm3", 1.0),
    "Sm3": ("Sm3", 1.0),
}
#: Units of core's table that Brightway has no counterpart for. Refused, with the reason.
UNSUPPORTED_UNITS = {
    "ea*h": "item-hours (rented equipment) have no Brightway unit; state the equipment's share as items (ea) or its burden in a background activity",
    "ea*a": "item-years have no Brightway unit; state the equipment's share as items (ea) or its burden in a background activity",
}
#: The export's units -> Brightway unit names (core integrations/brightway.py; biosphere3 for the last two).
BW_UNITS = {
    "kg": "kilogram",
    "kWh": "kilowatt hour",
    "MJ": "megajoule",
    "m": "meter",
    "m2": "square meter",
    "m2*a": "square meter-year",
    "m3": "cubic meter",
    "ea": "unit",
    "tkm": "ton kilometer",
    "kBq": "kilo Becquerel",
    "Nm3": "normal cubic meter",  # bw2io units.py
    "Sm3": "standard cubic meter",
}
EXCHANGE_TYPES = ("product", "input", "output", "emission", "resource")
#: Ciroth, Muller, Weidema, Lesage (2016), Int J LCA 21:1338-1348: the empirically based
#: uncertainty factors (squared geometric standard deviations) of the pedigree scores 1 to 5,
#: as core's ``foundation.uncertainty.PEDIGREE``. Order of the scores in a dataset's pedigree.
PEDIGREE_FACTORS = (
    ("reliability", (1.00, 1.54, 1.61, 1.69, 1.69)),
    ("completeness", (1.00, 1.03, 1.04, 1.08, 1.08)),
    ("temporal correlation", (1.00, 1.03, 1.10, 1.19, 1.29)),
    ("geographical correlation", (1.00, 1.04, 1.08, 1.11, 1.11)),
    ("further technological correlation", (1.00, 1.18, 1.65, 2.08, 2.80)),
)
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
KEY = re.compile(r"^[a-z][a-z-]*:[A-Za-z0-9_.\-]+$")
PROPORTIONAL = ("mass", "economic", "energy", "exergy", "shares")
#: Core marks an output whose components are counted by its emission:* exchanges this way.
RELEASED = "released to the environment"
DEFAULT_BACKGROUND = "ecoinvent-3.11-cutoff"
DEFAULT_BIOSPHERE = "biosphere3"
#: Version of docs/system-model.md: the methodology every dataset of a build is built under.
METHODOLOGY_VERSION = "1.1.0"
METHODOLOGY_DOCUMENT = "docs/system-model.md"
SYSTEM_MODELS = {
    "cutoff": "attributional, cut-off",
    "substitution": "attributional, substitution variant (avoided-burden credits at end of life)",
}
CHANGES_SCHEMA = "cheme-as-code/lci-changes/v2"  # v2: impact is an object (reference_impacts.py)
#: WBCSD (2014) rule, hierarchy step 3: economic allocation above this price ratio, else mass.
PRICE_RATIO = 5.0
#: Co-products below this share of the output mass do not enter the price-ratio decision.
MINOR_COPRODUCT = 0.01
#: The methods each curated rule of the hierarchy allows (lci/mappings.yaml allocation).
RULE_METHODS = {
    "physical-exergy": ("exergy",),
    "physical-energy": ("energy",),
    "economic": ("economic",),
    "mass": ("mass",),
    # step 4: the CO2 co-product gets a share of 0 of the main process; its conditioning is a
    # separate (subdivided) dataset, so only explicit shares can express it
    "co2-cutoff": ("shares",),
    "pcr": PROPORTIONAL,
    "deviation": PROPORTIONAL,
}
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
    "atlas flow uuid",
    "atlas pedigree",
    "atlas carrier",
    "atlas location rule",
    "atlas activity",
    "atlas reference product",
    "atlas location",
    "atlas code",
    "atlas link",
    "atlas check",
    "atlas plant activity",
    "atlas plant reference product",
    "atlas plant location",
    "atlas plant code",
    "atlas plant check",
    "atlas gap",
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


class GapError(BuildError):
    """An exchange without a technosphere mapping or a biosphere identity: a gap, which makes the
    process's LCI preliminary (reported, the exchange exported unlinked), in every process and
    build (ADR 0022, ADR 0026). *link* is the link it lacks: ``technosphere`` or ``biosphere``."""

    def __init__(self, message: str, link: str) -> None:
        super().__init__(message)
        self.link = link


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    #: mapping gaps (ADR 0022, ADR 0026): neither errors nor warnings, so ``--strict`` does not
    #: fail on them; one entry per dataset exchange (``lci/gaps.json``)
    gaps: list[dict] = field(default_factory=list)
    #: the warnings that do not fail ``--strict``: a public process's benchmark gap (ADR 0026)
    advisories: list[str] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")

    def advise(self, where: str, message: str) -> None:
        self.warn(where, message)
        self.advisories.append(self.warnings[-1])

    @property
    def strict_failures(self) -> list[str]:
        return [w for w in self.warnings if w not in self.advisories]

    def gap(self, process: str, dataset: Dataset, exchange: dict, link: str, reason: str) -> None:
        entry = {"process": process, "dataset": dataset.data["id"], "path": dataset.path, "key": exchange["key"], "type": exchange["type"], "link": link, "reason": reason}
        if entry not in self.gaps:  # once per exchange, not per co-product
            self.gaps.append(entry)


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


def _schema_problems(data: Any, name: str) -> list[str]:
    """*data* against ``schemas/<name>``; a ``$ref`` to the shared mappings schema resolves."""
    schemas = _base_dir("schemas")
    schema = json.loads((schemas / name).read_text(encoding="utf-8"))
    shared = json.loads((schemas / "lci-mappings.schema.json").read_text(encoding="utf-8"))
    registry = Registry().with_resource(shared["$id"], Resource.from_contents(shared))
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(Draft202012Validator(schema, registry=registry).iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]


def load_mappings(path: Path) -> dict:
    data = _yaml(path) or {}
    problems = _schema_problems(data, "lci-mappings.schema.json")
    if problems:
        raise BuildError(f"{path}: " + "; ".join(problems))
    data.setdefault("proxies", {})
    data.setdefault("biosphere", {})
    data.setdefault("pass_through", {})
    data.setdefault("exchanges", {})
    data.setdefault("cutoff_exclusions", {})
    data.setdefault("allocation", {})
    substitution = data.setdefault("substitution", {})
    substitution.setdefault("technosphere", {})
    substitution.setdefault("proxies", {})
    for pid, proxy in data["proxies"].items():
        credits = [item["use"] for item in proxy["inputs"] if item["amount"] < 0]
        if credits:
            raise BuildError(
                f"{path}: proxies.{pid}: negative input of {', '.join(credits)} is an avoided-burden credit; "
                "credits belong in substitution.proxies, never in the cut-off build"
            )
    for tid in data["cutoff_exclusions"]:
        if tid in data["technosphere"]:
            raise BuildError(f"{path}: cutoff_exclusions.{tid} is also a technosphere entry: a flow is linked or excluded, not both")
    for prefix, technosphere, proxies in (
        ("", data["technosphere"], data["proxies"]),
        ("substitution.", {**data["technosphere"], **substitution["technosphere"]}, {**data["proxies"], **substitution["proxies"]}),
    ):
        for tid, entry in technosphere.items():
            if "proxy" in entry and entry["proxy"] not in proxies:
                raise BuildError(f"{path}: {prefix}technosphere.{tid}: unknown proxy {entry['proxy']!r}")
        for pid, proxy in proxies.items():
            for item in proxy["inputs"]:
                target = data["technosphere"].get(item["use"])
                if target is None or "activity" not in target:
                    raise BuildError(f"{path}: {prefix}proxies.{pid}: input {item['use']!r} is not a technosphere entry with an activity")
    for key, entry in data["allocation"].items():
        if entry["method"] not in RULE_METHODS[entry["rule"]]:
            raise BuildError(f"{path}: allocation.{key}: rule {entry['rule']!r} does not allow method {entry['method']!r}")
    return data


def merge_process_mappings(library: Path, mappings: dict, report: Report) -> None:
    """Add each ``processes/<id>/lca/mappings.yaml`` (schema
    ``schemas/lci-process-mappings.schema.json``) to *mappings* ``exchanges`` as
    ``"<id>/<key>"``. A file failing its schema, or an exchange that ``lci/mappings.yaml``
    overrides too, is an error with the file."""
    for path in sorted((library / "processes").glob(f"*/{PROCESS_MAPPINGS}")):
        pid, where = path.parents[1].name, str(path.relative_to(library))
        try:
            data = _yaml(path) or {}
        except yaml.YAMLError as failure:
            report.error(where, f"not YAML: {failure}")
            continue
        problems = _schema_problems(data, "lci-process-mappings.schema.json")
        for message in problems:
            report.error(where, message)
        if problems:
            continue
        for key, entry in data["exchanges"].items():
            if f"{pid}/{key}" in mappings["exchanges"]:
                report.error(where, f"exchanges.{key} is also overridden in lci/mappings.yaml (exchanges.{pid}/{key}): keep one, in this file")
                continue
            mappings["exchanges"][f"{pid}/{key}"] = entry


def profile(mappings: dict, model: str) -> dict:
    """The mappings a build of *model* links with: the cut-off ones, plus ``substitution:`` for
    the substitution variant."""
    if model == "cutoff":
        return mappings
    extra = mappings["substitution"]
    return {
        **mappings,
        "technosphere": {**mappings["technosphere"], **extra["technosphere"]},
        "proxies": {**mappings["proxies"], **extra["proxies"]},
    }


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
        unit = exchange.get("unit")
        if unit in UNSUPPORTED_UNITS:
            problems.append(f"{at}: unit {unit}: {UNSUPPORTED_UNITS[unit]}")
        elif unit not in UNIT_SCALING:
            problems.append(f"{at}: unit {unit!r} is not one of {', '.join([*UNIT_SCALING, *UNSUPPORTED_UNITS])}")
        problems.extend(f"{at}: {text}" for text in _quality_problems(exchange))
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
    superseded = data.get("superseded_by")
    if superseded is not None:
        if not (isinstance(superseded, dict) and isinstance(superseded.get("id"), str) and isinstance(superseded.get("version"), str)):
            problems.append("superseded_by needs an id and a version")
        elif superseded["id"] == data.get("id") and superseded["version"] == str(data.get("version")):
            problems.append("superseded_by names the dataset itself")
    if problems:
        raise BuildError(f"{where}: " + "; ".join(problems))
    return data


def _flow_identities(exchange: dict) -> list[dict]:
    """The exchange's ``flow:`` (one mapping is read as a list, as in core)."""
    flow = exchange.get("flow")
    return [flow] if isinstance(flow, dict) else [f for f in flow or [] if isinstance(f, dict)]


def _quality_problems(exchange: dict) -> list[str]:
    """What is wrong with the v2 fields of one exchange this builder reads: pedigree, basic
    uncertainty, flow identities."""
    problems = []
    pedigree = exchange.get("pedigree")
    if pedigree is not None:
        scores = pedigree.get("scores") if isinstance(pedigree, dict) else None
        if not (isinstance(scores, list) and len(scores) == 5 and all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= 5 for x in scores)):
            problems.append("pedigree.scores is not five integers from 1 to 5")
    basic = exchange.get("basic_uncertainty")
    if pedigree is not None and basic is None:
        # core's table of basic uncertainties by exchange type (quality.BASIC) is not copied here, and
        # core fills the field in every dataset it generates: a hand-written pedigree must state it
        problems.append("pedigree without basic_uncertainty: state it (core's quality.basic_uncertainty for the exchange type)")
    own = exchange.get("uncertainty")
    if isinstance(own, dict) and own.get("pedigree") and not own.get("gsd2") and not own.get("basic"):
        problems.append("uncertainty.pedigree without gsd2 or basic: state the basic uncertainty")
    if basic is not None and (isinstance(basic, bool) or not isinstance(basic, (int, float)) or basic < 1):
        problems.append("basic_uncertainty is not a number of at least 1")
    for number, flow in enumerate(_flow_identities(exchange)):
        uuid = flow.get("uuid")
        if uuid is not None and not (isinstance(uuid, str) and UUID.match(uuid)):
            problems.append(f"flow[{number}].uuid {uuid!r} is not a lower-case UUID")
        if flow.get("list") != "biosphere3":
            continue
        per_unit = flow.get("per_unit", 1.0)
        if isinstance(per_unit, bool) or not isinstance(per_unit, (int, float)) or per_unit <= 0:
            problems.append(f"flow[{number}].per_unit {per_unit!r} is not a positive number")
        if flow.get("unit") and flow["unit"] not in UNIT_SCALING:
            problems.append(f"flow[{number}].unit {flow['unit']!r} has no Brightway unit")
    return problems


def normalise_units(data: dict) -> dict:
    """*data* with every exchange in the unit the export counts its quantity in (g and t in kg,
    MWh in kWh, GJ in MJ, L in m3, ...): Brightway activities count in one unit per kind, and
    the allocation by mass needs kg. The input is not changed."""
    exchanges = []
    for exchange in data["exchanges"]:
        unit, factor = UNIT_SCALING[exchange["unit"]]
        if unit != exchange["unit"] or factor != 1.0:
            exchange = {**exchange, "amount": exchange["amount"] * factor, "unit": unit}
        exchanges.append(exchange)
    return {**data, "exchanges": exchanges}


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
    minor = minor_coproducts(dataset)
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
            if value is None and method == "economic" and product["key"] in minor:
                value = 0.0  # a co-product below 1 % of the output mass without a price has no economic weight
            if value is None and method == "economic":
                raise BuildError(
                    f"{where}: economic allocation: no price of {name} in the study or the dataset, and the export "
                    "takes no registry price (none is recorded yet; docs/registry.md, Missing prices)"
                )
            if value is None:
                raise BuildError(f"{where}: {method} allocation: no {what} of {name}")
            raw[product["key"]] = float(product["amount"]) * float(value)
    total = sum(raw.values())
    if total <= 0:
        raise BuildError(f"{where}: {method} allocation gives the products no weight")
    return {k: v / total for k, v in raw.items()}


def minor_coproducts(dataset: dict) -> set[str]:
    """Keys of the co-products below 1 % of the output mass (only when every product is in kg)."""
    products = [e for e in dataset["exchanges"] if e["type"] == "product"]
    if len(products) < 2 or any(p["unit"] != "kg" for p in products):
        return set()
    mass = sum(float(p["amount"]) for p in products)
    return {p["key"] for p in products if mass > 0 and float(p["amount"]) / mass < MINOR_COPRODUCT}


def price_ratio(dataset: dict, allocation: dict) -> float | None:
    """The WBCSD decision ratio: the highest over the lowest price per kg of the co-products,
    leaving out co-products below 1 % of the output mass. None when a considered co-product has
    no price, or when a co-product is not counted in kg (prices per MJ and per kg do not compare,
    and the rule's alternative, mass allocation, needs kg). 1 when only one co-product is left:
    there is nothing to compare, so the rule gives mass."""
    products = [e for e in dataset["exchanges"] if e["type"] == "product"]
    if len(products) < 2 or any(p["unit"] != "kg" for p in products):
        return None
    minor = minor_coproducts(dataset)
    considered = [p for p in products if p["key"] not in minor]
    if len(considered) == 1:
        return 1.0
    prices = [_properties(p, allocation)["price"] for p in considered]
    if any(price is None for price in prices):
        return None
    low, high = min(map(float, prices)), max(map(float, prices))
    if high <= 0:
        return None
    return math.inf if low <= 0 else high / low


@dataclass
class Allocation:
    """The method the export uses for one dataset, and why (docs/system-model.md)."""

    allocation: dict
    source: str  # mappings | study | dataset | default | hierarchy
    rule: str  # single-output, a RULE_METHODS key, or unresolved
    reason: str
    finding: str | None = None


def choose_allocation(pid: str, data: dict, study_allocation: dict | None, mappings: dict) -> Allocation:
    """Apply the multi-functionality hierarchy: a curated rule (mappings ``allocation``) first;
    else the study's or dataset's method if it is the WBCSD price-ratio choice; else the
    price-ratio choice; else the given method, with a finding. A deviation from the hierarchy is
    stated where core allows it, ``allocation.deviation`` of the study or of the dataset (the
    study's first), or as a curated rule (``rule: deviation``) in the mappings, which wins."""
    own = data.get("allocation") or {}
    if study_allocation:
        base, source = study_allocation, "study"
    elif own:
        base, source = own, "dataset"
    else:
        base, source = {"method": "mass"}, "default"
    method = base.get("method", "mass")
    products = [e for e in data["exchanges"] if e["type"] == "product"]
    if len(products) == 1:
        return Allocation(base, source, "single-output", "one product: nothing to allocate")

    ratio = price_ratio(data, base)
    expected = None if ratio is None else ("economic" if ratio > PRICE_RATIO else "mass")
    ratio_text = "unbounded (a co-product has price 0)" if ratio == math.inf else f"{ratio:.3g}" if ratio is not None else "unknown"
    wbcsd = f"price ratio {ratio_text}: economic above {PRICE_RATIO:g}, else mass (WBCSD 2014)"
    not_kg = [_name(p) for p in products if p["unit"] != "kg"]
    gap = (
        f"{', '.join(not_kg)} is not counted in kg, so the WBCSD price ratio (per kg) does not apply"
        if not_kg else "not every co-product above 1 % of the output mass has a price, so the WBCSD price ratio is unknown"
    )

    entry = mappings["allocation"].get(f"{pid}/{data['id']}") or mappings["allocation"].get(pid)
    if entry:
        rule = entry["rule"]
        finding = None
        allocation = {**base, "method": entry["method"]}
        if "shares" in entry:
            allocation["shares"] = entry["shares"]
        if rule == "co2-cutoff":
            names = {_name(p) for p in products}
            co2 = entry["product"]
            if co2 not in names:
                raise BuildError(f"lci/mappings.yaml allocation.{pid}: co2-cutoff product {co2!r} is not a product of dataset {data['id']}")
            given = (allocation.get("shares") or {}).get(co2)
            if given is None or float(given) != 0:
                raise BuildError(
                    f"lci/mappings.yaml allocation.{pid}: co2-cutoff gives {co2} a share of {given!r} of the main process; "
                    "the cut is before conditioning, so its share is 0 and its conditioning is a separate dataset"
                )
        if rule in ("economic", "mass") and expected is None:
            finding = f"rule {rule}: {gap}, so it cannot be confirmed"
        elif rule in ("economic", "mass") and expected != rule:
            finding = f"rule {rule}, but the {wbcsd}"
        elif rule == "physical-energy":
            zero = [_name(p) for p in products if _properties(p, base)["energy"] == 0]
            if zero:
                finding = f"energy allocation, but {', '.join(zero)} has no energy content (the hierarchy then goes to step 3)"
        return Allocation(allocation, "mappings", rule, " ".join(entry["reason"].split()), finding)

    if expected == method:
        return Allocation(base, source, expected, wbcsd)
    deviation = " ".join(str(base.get("deviation") or own.get("deviation") or "").split())
    if deviation and method in PROPORTIONAL:
        return Allocation(base, source, "deviation", deviation)
    if expected:
        finding = (
            f"the {source}'s {method} allocation is not the hierarchy's {expected} ({wbcsd}); {expected} is exported. "
            f"State the reason in allocation.deviation of the study or the dataset (or a curated rule in lci/mappings.yaml allocation) to keep {method}"
        )
        return Allocation({**base, "method": expected}, "hierarchy", expected, wbcsd, finding)
    finding = (
        f"{method} allocation ({source}) does not follow the documented hierarchy: no allocation.deviation and no curated rule "
        f"in lci/mappings.yaml allocation, and {gap}"
    )
    return Allocation(base, source, "unresolved", "not shown to follow the hierarchy (see the build's findings)", finding)


@dataclass
class Dataset:
    path: str  # from the library root
    data: dict
    allocation: dict
    allocation_source: str  # mappings | study | dataset | default | hierarchy
    shares: dict[str, float]
    rule: str = "single-output"
    reason: str = ""
    finding: str | None = None
    #: sha256 of the dataset as read, before its units are normalised
    sha256: str = ""
    #: the data quality rating of lca/manifest.json (``data_quality``), for the plant's generated dataset
    data_quality: dict | None = None
    #: the dataset that replaces this one (``superseded_by``), resolved against the build
    successor: dict | None = None


@dataclass
class Process:
    pid: str
    manifest: dict
    study: dict | None
    factors: dict | None
    datasets: list[Dataset]
    chemicals: dict[str, str]  # inventory key -> chemical slug (process.yaml)
    grades: dict[str, str] = field(default_factory=dict)  # inventory key -> grade (registry.flow_grade)


def _data_quality(path: Path, report: Report, where: str) -> dict | None:
    """The data quality rating core writes into ``lca/manifest.json`` (``data_quality``: TfS DQR
    with TeR, GeR and TiR, the PEF-style P, C and DQR, the primary data share, the weighting
    basis), or None when the manifest has none (written before core recorded it, or no manifest)."""
    if not path.is_file():
        return None
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as failure:
        report.warn(where, f"not valid JSON, its data quality rating is not read: {failure}")
        return None
    rating = manifest.get("data_quality") if isinstance(manifest, dict) else None
    return rating if isinstance(rating, dict) else None


def resolve_successors(processes: list[Process], report: Report) -> None:
    """Resolve every ``superseded_by`` (a dataset id and version) against the datasets of the
    build, the same process first. A deprecated dataset stays in the database: only the pointer is
    added. A successor that is not in the build (unpublished, or a typo) is a warning."""
    for process in processes:
        for dataset in process.datasets:
            target = dataset.data.get("superseded_by")
            if not target:
                continue
            candidates = [(p, d) for p in [process, *[q for q in processes if q is not process]] for d in p.datasets if d.data["id"] == target["id"] and d is not dataset]
            found = next((c for c in candidates if _dataset_version(c[1])[0] == str(target["version"])), next(iter(candidates), None))
            entry: dict[str, Any] = {"id": target["id"], "version": str(target["version"]), "process": None, "resolved": found is not None, "activities": []}
            if found is None:
                report.warn(dataset.path, f"superseded_by {target['id']} {target['version']} is not a dataset of this build: the pointer is kept, but names nothing here")
            else:
                other, successor = found
                have = _dataset_version(successor)[0]
                if have != entry["version"]:
                    report.warn(dataset.path, f"superseded_by {target['id']} {entry['version']}, but the build has version {have}")
                entry["process"] = other.pid
                entry["activities"] = [f"{other.pid}:{successor.data['id']}:{key}" for key in sorted(successor.shares) if successor.shares[key] > 0]
            dataset.successor = entry


def check_system_models(processes: list[Process], model: str, report: Report) -> None:
    """A dataset that states its system model must fit the build: the cut-off build
    takes cut-off datasets; the substitution variant is made from cut-off or substitution ones.
    One database never mixes system models (docs/system-model.md)."""
    allowed = {"cutoff": ("cutoff",), "substitution": ("cutoff", "substitution")}[model]
    for process in processes:
        for dataset in process.datasets:
            stated = dataset.data.get("system_model")
            if stated and stated not in allowed:
                report.error(dataset.path, f"system_model {stated!r} does not fit the {model} build (it takes {', '.join(allowed)})")


def _discover(library: Path, report: Report, mappings: dict, public: bool = False, products: reg.Registry | None = None) -> list[Process]:
    products = products or reg.Registry({})
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
        chemicals, grades = {}, {}
        for group in ("inputs", "outputs", "utilities"):
            for item in (manifest.get("chemistry") or {}).get(group, []) or []:
                if item.get("inventory_key"):
                    slug, grade, problem = reg.flow_grade(products, pid, item)
                    if problem:
                        report.error(str(manifest_path.relative_to(library)), f"chemistry.{group}: {problem}")
                    chemicals[item["inventory_key"]] = slug
                    if grade:
                        grades[item["inventory_key"]] = grade
        quality = _data_quality(folder / "lca" / "manifest.json", report, str((folder / "lca" / "manifest.json").relative_to(library)))
        datasets = []
        for path in files:
            where = str(path.relative_to(library))
            try:
                raw = validate_dataset(_yaml(path), where)
                data = normalise_units(raw)
                study_allocation = (study or {}).get("allocation") if path.name == "dataset.yaml" else None
                choice = choose_allocation(pid, data, study_allocation, mappings)
                if choice.source == "study" and data.get("allocation") and data["allocation"].get("method") != study_allocation.get("method"):
                    report.warn(where, f"study allocation {study_allocation.get('method')!r} differs from the dataset's default {data['allocation'].get('method')!r}: the study's is used")
                if choice.finding:
                    report.warn(where, f"allocation: {choice.finding}")
                datasets.append(
                    Dataset(where, data, choice.allocation, choice.source, shares(data, choice.allocation, where), choice.rule, choice.reason, choice.finding, _content_sha256(raw),
                        quality if path.name == "dataset.yaml" else None)
                )
            except BuildError as failure:
                report.errors.append(str(failure))
        if datasets:
            processes.append(Process(pid, manifest, study, factors, datasets, chemicals, grades))
    return processes


def check_overrides(library: Path, processes: list[Process], mappings: dict, registry: set[str], report: Report, public: bool, foreign: frozenset[str] = frozenset()) -> None:
    """An override that cannot apply is an error, not a quiet gap (ADR 0026): a key matching no
    exchange, or a ``chemical`` no registry or mappings entry knows. A public build does not load
    the unpublished processes, so it checks only the keys of those it holds. *foreign* are the
    overrides of mappings written for another library (the fallback to the process library's own):
    they need not fit this one."""
    keys = {p.pid: {e["key"] for d in p.datasets for e in d.data["exchanges"]} for p in processes}
    every = set().union(*keys.values()) if keys else set()
    for key, entry in mappings["exchanges"].items():
        if key in foreign:
            continue
        chemical = entry.get("chemical")
        if chemical and chemical not in registry and chemical not in mappings["technosphere"] and chemical not in mappings["cutoff_exclusions"]:
            report.error("lci mappings", f"exchanges.{key}: chemical {chemical!r} is not in the registry or the mappings")
        if key in every:
            continue
        pid, slash, exchange = key.partition("/")
        if not slash:
            if not public:
                report.error("lci mappings", f"exchanges.{key}: no dataset has this exchange")
        elif pid in keys:
            if exchange not in keys[pid]:
                report.error("lci mappings", f"exchanges.{key}: {pid}'s datasets have no exchange {exchange!r}")
        elif not (library / "processes" / pid / "process.yaml").is_file():
            report.error("lci mappings", f"exchanges.{key}: no process {pid!r} in this library")


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
    #: registry slugs of kind ``utility``: an output of one (heat to cooling water, wastewater to
    #: treatment) is a service another Atlas process may provide, so it may link inside the Atlas
    utilities: set[str] = field(default_factory=set)
    #: chemical slug -> [(process id, activity row)] of every Atlas activity that makes it
    producers: dict[str, list[tuple[str, dict]]] = field(default_factory=dict)
    #: (path, product key) -> activity row, for link.dataset
    by_dataset: dict[tuple[str, str], dict] = field(default_factory=dict)
    proxies_used: set[str] = field(default_factory=set)
    model: str = "cutoff"
    markets: list[mk.Market] = field(default_factory=list)
    #: market code -> its activity row (exported markets only)
    market_rows: dict[str, dict] = field(default_factory=dict)
    #: plant activity code -> the dataset it is allocated from (for the allocation check)
    datasets: dict[str, Dataset] = field(default_factory=dict)
    #: plant activity code -> its row
    rows: dict[str, dict] = field(default_factory=dict)

    def known(self, tid: str | None) -> bool:
        return bool(tid) and (tid in self.mappings["technosphere"] or tid in self.mappings["cutoff_exclusions"])

    def link(self, tid: str, unit: str, where: str, key: str) -> tuple[str, dict | str]:
        """A technosphere id as ``("technosphere", fields)``, or ``("excluded", decision)`` when
        the cut-off model leaves it out of the producer's system."""
        if tid in self.mappings["technosphere"]:
            return "technosphere", self.technosphere(tid, unit, where)
        excluded = self.mappings["cutoff_exclusions"][tid]
        if self.model != "cutoff":
            raise BuildError(f"{where}: {tid!r} is excluded under cut-off and has no {self.model} mapping (lci/mappings.yaml substitution.technosphere)")
        return "excluded", " ".join(excluded["decision"].split())

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
        """``("skip", why)``, ``("excluded", why)``, ``("technosphere", fields)`` or ``("biosphere", fields)``."""
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
            if not self.known(override["use"]):
                raise BuildError(f"{where}: override uses unknown technosphere entry {override['use']!r}")
            return self.link(override["use"], unit, where, exchange["key"])
        if override.get("dataset"):  # the mappings' form of link.dataset: a chosen Atlas producer
            link = {"dataset": override["dataset"]}

        if exchange["type"] in ("emission", "resource"):
            return "biosphere", self.elementary(exchange, where)

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
            row = self.by_dataset.get((str(PurePath(ref["path"])), product))
            if row is None:
                raise BuildError(f"{where}: link.dataset {ref['path']}#{product} is not an exported Atlas dataset of this library")
            if row["unit"] != unit:
                raise BuildError(f"{where}: link.dataset {ref['path']}#{product} is in {row['unit']}, but the exchange is in {unit}")
            refusal = carrier_refusal(exchange.get("carrier"), row.get("carrier"))
            if refusal:
                raise BuildError(f"{where}: link.dataset {ref['path']}#{product} is outside its operating range: {refusal}")
            return "technosphere", {**self._own(row), "atlas location rule": "fixed", "atlas code": row["code"], "atlas link": "pinned"}

        chemical = _chemical(process, exchange, self.mappings, self.registry)
        if self.known(chemical):
            return self.link(chemical, unit, where, exchange["key"])
        factor = link.get("factor")
        if self.known(factor):
            return self.link(factor, unit, where, exchange["key"])
        tried = ", ".join(x for x in (f"chemical {chemical!r}" if chemical else "", f"factor {factor!r}" if factor else "") if x) or "no chemical slug or factor id"
        raise GapError(f"{where}: no mapping ({tried}); add it to lci/mappings.yaml technosphere or to the process's {PROCESS_MAPPINGS} exchanges", "technosphere")

    def elementary(self, exchange: dict, where: str) -> dict:
        """The biosphere flow of an emission or a resource, by the first of: its biosphere3
        identity (``flow:``; a curated ``biosphere:`` entry keyed by that UUID may
        correct the name and categories), ``link.biosphere``, the curated ``biosphere:`` entry
        of its component (``<component>/<origin>``, else ``<component>``). The result carries
        ``amount factor`` (the list's unit per unit of the exchange; the caller removes it)."""
        link = exchange.get("link") or {}
        unit = exchange["unit"]
        identity = next((f for f in _flow_identities(exchange) if f.get("list") == "biosphere3" and f.get("uuid")), None)
        if identity:
            entry = self.mappings["biosphere"].get(identity["uuid"])
            flow = entry["flow"] if entry else identity
            if not flow.get("name") or not flow.get("categories"):
                raise BuildError(f"{where}: flow identity {identity['uuid']} has no name and categories (give them in the dataset, or in lci/mappings.yaml biosphere)")
            list_unit, factor = UNIT_SCALING[identity.get("unit") or unit]
            per_unit = float(identity.get("per_unit", 1.0))
            if unit == list_unit:
                amount_factor = 1.0  # the amount is already in the list's unit; per_unit is per kg
            elif unit == "kg":
                amount_factor = per_unit * factor
            else:
                raise BuildError(
                    f"{where}: flow identity {identity['uuid']} is in {list_unit} (per_unit {per_unit:g} per kg) but the exchange is in {unit}: "
                    "state the amount in kg or in the list's unit"
                )
            return {
                "name": flow["name"],
                "categories": list(flow["categories"]),
                "unit": BW_UNITS[list_unit],
                "atlas flow uuid": identity["uuid"],
                "amount factor": amount_factor,
            }
        if link.get("biosphere"):
            flow = link["biosphere"]
            return {"name": flow["name"], "categories": list(flow.get("categories") or []), "unit": BW_UNITS[unit], "amount factor": 1.0}
        component = _name(exchange)
        origin = (link.get("elementary") or {}).get("origin") or exchange.get("origin") or "fossil"
        entry = self.mappings["biosphere"].get(f"{component}/{origin}") or self.mappings["biosphere"].get(component)
        if entry is None:
            raise GapError(
                f"{where}: {exchange['type']} of {component} ({origin}) has no biosphere3 flow identity and is not in lci/mappings.yaml biosphere",
                "biosphere",
            )
        found = {"name": entry["flow"]["name"], "categories": list(entry["flow"]["categories"]), "unit": BW_UNITS[unit], "amount factor": 1.0}
        if entry["flow"].get("uuid"):
            found["atlas flow uuid"] = entry["flow"]["uuid"]
        return found

    def _own(self, row: dict) -> dict:
        return {"name": row["name"], "reference product": row["reference product"], "unit": row["unit"], "location": row["location"], "database": self.db_name}

    def atlas_alternative(self, process: Process, exchange: dict, unit: str, location: str | None = None) -> AtlasChoice | None:
        """The Atlas activity this exchange links to with ``prefer_atlas``: the market of its grade
        (``markets.choose``) when one exists, else the plant; and the plant beside a market, for
        pinning. The exchange is an input, or an output of a utility (a service such as cooling
        or wastewater treatment), unless its override in the mappings says ``atlas: false``.
        Plants are the producers of the exchange's chemical in other processes, a producer of the
        grade the input names first (then only producers of that grade compete), then by process
        id and name (deterministic; the other candidates are reported, so that a second producer
        never replaces the first silently). A producer of another grade than the one the input
        names is refused."""
        chemical = _chemical(process, exchange, self.mappings, self.registry)
        if not (exchange["type"] == "input" or (exchange["type"] == "output" and chemical in self.utilities)):
            return None
        override = self.mappings["exchanges"].get(f"{process.pid}/{exchange['key']}") or self.mappings["exchanges"].get(exchange["key"]) or {}
        if override.get("atlas") is False:
            return None
        wanted = process.grades.get(exchange["key"])
        candidates, refused = [], []
        for pid, row in self.producers.get(chemical or "", []):
            if pid == process.pid or row["unit"] != unit:
                continue
            if wanted and row.get("grade") and row["grade"] != wanted:
                refused.append(f"{pid}: {row['name']} | {row['reference product']} (grade {chemical}/{row['grade']}, the input is {chemical}/{wanted})")
                continue
            candidates.append((pid, row))
        # a current producer of the grade the input names comes first (a deprecated dataset's last, a design case's own
        # dataset after its study's, ADR 0034), then by process id and name
        candidates.sort(key=lambda c: (c[1].get("deprecated", False), c[1].get("design_case") is not None,
                                       not wanted or c[1].get("grade") != wanted, c[0], c[1]["name"]))  # fmt: skip
        if not candidates:
            return AtlasChoice(None, None, [], refused) if refused else None
        if wanted and candidates[0][1].get("grade") == wanted:
            # the grade decides: only other producers of the same grade compete
            candidates = [c for c in candidates if c[1].get("grade") == wanted]
        plant = candidates[0][1]
        others = candidates[1:]
        grade = wanted or plant.get("grade")
        market, unchosen = mk.choose(self.markets, chemical or "", grade, location, exclude=process.pid)
        row = self.market_rows.get(market.code) if market else None
        if row is not None and row["unit"] != unit:
            row = None
        return AtlasChoice(row or plant, plant if row else None, others, refused, [m.code for m in unchosen] if market is None else [])

    def check(self, chemical: str | None, wanted: str | None, provider: dict, kind: str, need: dict | None = None) -> dict:
        """Compatibility of an Atlas-to-Atlas link: the provider's reference product
        grade and state, unit, system model, allocation and boundary. *kind* is ``market``,
        ``plant`` (no market of the grade), ``pinned`` (link.dataset), ``supply`` (a market's
        producer) or ``import`` (a consumption mix's other market). *need* is the consumer's
        carrier, checked against the provider's (a utility's operating range)."""
        checks: dict[str, dict] = {}
        ref = f"{provider['chemical']}/{provider['grade']}" if provider.get("grade") else provider.get("chemical") or provider["reference product"]
        if provider.get("chemical") and chemical and provider["chemical"] != chemical:
            checks["grade"] = {"status": "mismatch", "text": f"{ref} is not {chemical}"}
        elif not wanted:
            checks["grade"] = {"status": "note", "text": f"the input names {chemical or 'no chemical'} only; {ref} ({provider['reference product']}) is taken"}
        elif provider.get("grade") == wanted:
            checks["grade"] = {"status": "ok", "text": f"{ref} ({provider['reference product']})"}
        elif not provider.get("grade"):
            checks["grade"] = {"status": "note", "text": f"the provider names {ref} without a grade; the input is {chemical}/{wanted}"}
        else:
            checks["grade"] = {"status": "mismatch", "text": f"{ref}, the input is {chemical}/{wanted}"}
        checks["unit"] = {"status": "ok", "text": provider["unit"]}
        if need and provider.get("carrier"):
            refusal = carrier_refusal(need, provider["carrier"])
            checks["carrier"] = {"status": "mismatch", "text": refusal} if refusal else {"status": "ok", "text": f"{_carrier_text(need)} from {_carrier_text(provider['carrier'])}"}
        checks["system_model"] = {"status": "ok", "text": f"{self.model} (one database)"}
        if provider.get("market"):
            datasets = [self.datasets[c] for c in provider["suppliers"] if c in self.datasets]
        else:
            datasets = [self.datasets[provider["code"]]] if provider["code"] in self.datasets else []
        findings = [d for d in datasets if d.finding]
        methods = ", ".join(sorted({f"{d.allocation.get('method', 'mass')} ({d.rule})" for d in datasets})) or "none"
        checks["allocation"] = (
            {"status": "note", "text": f"{methods}; not shown to follow the hierarchy: {'; '.join(d.path for d in findings)}"}
            if findings else {"status": "ok", "text": methods}
        )
        if provider.get("market"):
            checks["boundary"] = {"status": "ok", "text": f"delivered ({provider['layer']}, {provider['location']}: transport and losses included)"}
        elif kind == "supply":
            checks["boundary"] = {"status": "ok", "text": "plant gate, into the market"}
        elif provider.get("chemical") in self.utilities and kind == "plant":
            checks["boundary"] = {"status": "note", "text": "plant gate of a site utility: no utility market yet (docs/markets.md)"}
        elif kind == "pinned":
            checks["boundary"] = {"status": "note", "text": "plant gate (pinned): no distribution or losses; the consumer's dataset counts its delivery"}
        else:
            checks["boundary"] = {"status": "note", "text": "plant gate: no market of this grade, so no distribution or losses"}
        compatible = all(c["status"] != "mismatch" for c in checks.values())
        text = ("compatible" if compatible else "INCOMPATIBLE") + ": " + "; ".join(f"{k.replace('_', ' ')} {v['text']}" for k, v in checks.items())
        return {"checks": checks, "compatible": compatible, "text": text}


@dataclass
class AtlasChoice:
    """The Atlas activity an input links to by default (a market, else a plant), the plant for
    pinning when the default is a market, the other plants and the refused ones (another grade),
    and the regional markets left unchosen (several, none for the consumer's region)."""

    target: dict | None
    plant: dict | None
    others: list[tuple[str, dict]]
    refused: list[str]
    unchosen: list[str] = field(default_factory=list)


# --- activities ------------------------------------------------------------------------------


def pedigree_gsd2(scores: list[int], basic: float) -> float:
    """The squared geometric standard deviation of pedigree *scores* on a *basic* uncertainty,
    combined as in ecoinvent: ``exp(sqrt(ln(basic)^2 + sum(ln(U_i)^2)))`` (core's
    ``foundation.uncertainty.pedigree_gsd2``)."""
    terms = [math.log(basic) ** 2] + [math.log(factors[score - 1]) ** 2 for (_, factors), score in zip(PEDIGREE_FACTORS, scores, strict=True)]
    return math.exp(math.sqrt(sum(terms)))


def _uncertainty(exchange: dict, amount: float) -> dict:
    """A lognormal gsd2 as Brightway's lognormal (type 2): loc ln(amount), scale ln(gsd2)/2.
    The exchange's own lognormal (a gsd2, or pedigree scores on a basic uncertainty) comes first,
    then the gsd2 of its pedigree (no exchange of a v2 dataset goes without one); the
    study's default distributions (lca.yaml) are not known to the dataset. Another distribution
    kind of the exchange (normal, triangular, uniform) is not exported; ``build`` warns."""
    given = exchange.get("uncertainty") or {}
    pedigree = exchange.get("pedigree") or {}
    if given:
        gsd2 = given.get("gsd2")
        if given.get("distribution", "lognormal") == "lognormal" and not gsd2 and given.get("pedigree"):
            gsd2 = pedigree_gsd2(given["pedigree"], given["basic"]) if given.get("basic") else None
        if given.get("distribution", "lognormal") != "lognormal":
            gsd2 = None
    elif pedigree.get("scores"):
        gsd2 = pedigree_gsd2(pedigree["scores"], exchange["basic_uncertainty"])
    else:
        gsd2 = None
    if not gsd2 or amount == 0:
        return {}
    # a negative amount (a credit of the substitution variant) is the lognormal of its magnitude
    # with Brightway's (stats_arrays) ``negative`` flag
    spec = {"uncertainty type": 2, "loc": _number(math.log(abs(amount))), "scale": _number(math.log(gsd2) / 2)}
    if amount < 0:
        spec["negative"] = True
    return spec


def _pedigree_column(exchange: dict) -> dict:
    """The five scores as ``"r,c,t,g,f"`` (reliability, completeness, temporal, geographical,
    further technological correlation); the installer turns them into Brightway's ``pedigree``."""
    scores = (exchange.get("pedigree") or {}).get("scores")
    return {"atlas pedigree": ",".join(str(x) for x in scores)} if scores else {}


def _carrier_text(carrier: dict | None) -> str:
    """An energy carrier as one line: kind, temperature, pressure, level, LHV."""
    if not carrier:
        return ""
    parts = [carrier["kind"]]
    if carrier.get("level"):
        parts.append(str(carrier["level"]))
    if carrier.get("temperature") is not None:
        parts.append(f"{carrier['temperature']:g} degC")
    if carrier.get("pressure") is not None:
        parts.append(f"{carrier['pressure']:g} bar(a)")
    if carrier.get("lhv") is not None:
        parts.append(f"LHV {carrier['lhv']:g} MJ/kg")
    return ", ".join(parts)


def carrier_refusal(need: dict | None, supply: dict | None) -> str | None:
    """Why a utility product with carrier *supply* cannot serve an exchange with carrier *need*,
    or None when it can or when either states no carrier (then there is nothing to check).

    The supply is a level: steam at its pressure serves steam at that pressure or below (let
    down, never raised) and heat up to its temperature; heat serves heat up to its temperature;
    cold (chilled or cooling water) serves a need at its temperature or warmer. Other kinds serve
    only their own kind."""
    if not need or not supply:
        return None
    nk, sk = need.get("kind"), supply.get("kind")

    def above(field: str, unit: str) -> str | None:
        n, s = need.get(field), supply.get(field)
        if n is not None and s is not None and n > s:
            return f"{nk} at {n:g} {unit} is above the supply's {s:g} {unit}"
        return None

    if sk == "steam" and nk == "steam":
        return above("pressure", "bar(a)") or above("temperature", "degC")
    if sk in ("steam", "heat") and nk == "heat":
        return above("temperature", "degC")
    if sk == "cold" and nk == "cold":
        n, s = need.get("temperature"), supply.get("temperature")
        if n is not None and s is not None and n < s:
            return f"cold at {n:g} degC is below the supply's {s:g} degC"
        return None
    if nk != sk:
        return f"a {nk} exchange cannot take {sk}"
    return None


def _state_text(state: dict | None) -> str:
    """A product's state as one line: phase, pressure, temperature, purity, grade."""
    if not state:
        return ""
    parts = [state["phase"]] if state.get("phase") else []
    if state.get("pressure") is not None:
        parts.append(f"{state['pressure']:g} bar(a)")
    if state.get("temperature") is not None:
        parts.append(f"{state['temperature']:g} degC")
    if state.get("purity") is not None:
        parts.append(f"{state['purity'] * 100:g} % {state.get('component') or 'main component'} ({state.get('basis') or 'basis not stated'})")
    if state.get("grade"):
        parts.append(f"grade {state['grade']}")
    return ", ".join(parts)


def design_case(dataset: Dataset) -> str | None:
    """The design case of a dataset that ``cheme assess lca --write --case <case>`` generated
    into ``lca/datasets/`` (ADR 0034: core ADR 0045's ``provenance.case``), else None. The
    study's own ``lca/dataset.yaml`` is never a case dataset, whatever case it was derived from."""
    if PurePath(dataset.path).name == "dataset.yaml" and PurePath(dataset.path).parent.name == "lca":
        return None
    provenance = dataset.data.get("provenance") or {}
    if provenance.get("generator") != "cheme assess lca":
        return None
    case = provenance.get("case")
    return str(case) if case else None


def _product_rows(process: Process, dataset: Dataset, products: reg.Registry, all_products: bool = False) -> list[dict]:
    """One row per allocated product (with *all_products*, also those with a share of 0, for the
    multi-output formats). Its reference product is the registry grade's name when the flow has
    a grade, else the substance's name with the exchange title. The activity's name is the
    process's title, with ", case <case>" for a design case's own dataset (ADR 0034), so that two
    designs of one process never share a name, reference product, location and unit."""
    rows = []
    location = dataset.data.get("location") or "GLO"
    case = design_case(dataset)
    title_of_process = process.manifest["title"] + (f", case {case}" if case else "")
    for exchange in dataset.data["exchanges"]:
        if exchange["type"] != "product" or (dataset.shares.get(exchange["key"], 0.0) <= 0 and not all_products):
            continue
        chemical = process.chemicals.get(exchange["key"])
        grade = process.grades.get(exchange["key"])
        title = exchange.get("title") or _name(exchange)
        name = (products.chemicals.get(chemical or "") or {}).get("name", chemical or "")
        graded = products.grade(chemical or "", grade)
        if graded:
            product = graded["name"]
        else:
            product = title if not name or name.lower() in title.lower() else f"{name}, {title}"
        rows.append(
            {
                "code": f"{process.pid}:{dataset.data['id']}:{exchange['key']}",
                "name": title_of_process + (f" [superseded by {dataset.successor['id']} {dataset.successor['version']}]" if dataset.successor else ""),
                "reference product": product,
                "unit": BW_UNITS[exchange["unit"]],
                "location": location,
                "key": exchange["key"],
                "amount": float(exchange["amount"]),
                "chemical": chemical,
                "grade": grade,
                "state": _state_text(exchange.get("state")),
                "carrier": exchange.get("carrier"),
                "deprecated": bool(dataset.data.get("superseded_by")),
                # a design case's own dataset (ADR 0034): never the default Atlas link of its product
                "design_case": case,
                "superseded_by": _successor_text(dataset.successor, exchange["key"]) if dataset.successor else None,
            }
        )
    return rows


def property_checks(process: Process, dataset: Dataset, products: reg.Registry, mappings: dict, report: Report) -> list[dict]:
    """Each product's allocation properties (exergy, energy) against the registry grade's or
    substance's (``registry.compare_property``; a product not counted in kg is ``unchecked``,
    as the registry's values are per kg). A mismatch is a warning unless
    ``lci/mappings.yaml`` gives the exchange a ``properties_reason``; then it is ``overridden``."""
    checks = []
    for exchange in dataset.data["exchanges"]:
        chemical = process.chemicals.get(exchange["key"])
        if exchange["type"] != "product" or chemical not in products.chemicals:
            continue
        grade = process.grades.get(exchange["key"])
        override = mappings["exchanges"].get(f"{process.pid}/{exchange['key']}") or mappings["exchanges"].get(exchange["key"]) or {}
        given = _properties(exchange, dataset.allocation)
        for name in sorted(reg.STUDY_PROPERTIES):
            result = reg.compare_property(products, chemical, grade, name, given.get(name), exchange["unit"])
            if result is None:
                continue
            if result["status"] == "mismatch" and override.get("properties_reason"):
                result.update(status="overridden", reason=override["properties_reason"].strip())
            elif result["status"] == "mismatch":
                ref = f"{chemical}/{grade}" if grade else chemical
                report.warn(
                    f"{dataset.path} {exchange['key']}",
                    f"{name} {result['study']:.6g} kJ/kg differs from the registry's {result['registry']:.6g} kJ/kg of {ref} by more than "
                    f"{reg.STUDY_TOLERANCE:.0%} (give lci/mappings.yaml exchanges.{process.pid}/{exchange['key']}.properties_reason if intended)",
                )
            checks.append({"key": exchange["key"], "chemical": chemical, "grade": grade, **{k: _number(v) if isinstance(v, float) else v for k, v in result.items()}})
    return checks


def benchmark_results(processes: list[Process], benchmarks: bm.Registry | None, public: bool, report: Report) -> dict[str, list[dict]]:
    """Each dataset's KPIs (``benchmarks.evaluate``, with its allocation shares), by dataset path.
    In a library with a benchmark registry, these are warnings: a public process with fewer than
    ``benchmarks.MIN_KPIS`` KPIs (one that does not fail ``--strict``, ADR 0026), a process bound under a family its process.yaml does not list,
    and, outside ``--public``, a binding that names no dataset of the library."""
    if benchmarks is None:
        return {}
    results = {}
    for process in processes:
        for dataset in process.datasets:
            results[dataset.path], warnings = bm.evaluate(benchmarks, process.pid, dataset.data, dataset.shares)
            report.warnings.extend(warnings)
        ids = [d.data["id"] for d in process.datasets]
        for text in bm.family_mismatches(benchmarks, process.pid, ids, process.manifest.get("families") or []):
            report.warn(process.pid, text)
        count = bm.kpi_count(benchmarks, process.pid, ids)
        if is_public(process.manifest) and count < bm.MIN_KPIS:
            report.advise(  # a warning that does not fail --strict (ADR 0026)
                process.pid,
                f"{count} benchmarked KPI(s); a public process needs at least {bm.MIN_KPIS}, each with a source or a "
                "recorded no_open_reference (benchmarks/<family>.yaml, docs/benchmarks.md)",
            )
    if not public:
        for name in bm.unused_bindings(benchmarks, {(p.pid, d.data["id"]) for p in processes for d in p.datasets}):
            report.warn("benchmarks", f"datasets {name}: no such LCI dataset in the library (renamed?)")
    return results


#: The findings of core's ``lca.cutoff`` that are the cut-off criteria (docs/system-model.md
#: section 4). Its system-model findings (negative inputs, recyclables to energy recovery) are not
#: read here: the build checks the system model itself (``check_system_models``, the cut-off build's
#: refusal of credits).
CUTOFF_RULES = ("cheme.lca-cutoff-share", "cheme.lca-cutoff-sum", "cheme.lca-cutoff-never", "cheme.lca-cutoff-unchecked")


def cutoff_results(processes: list[Process], report: Report) -> dict[str, dict]:
    """The cut-off criteria (docs/system-model.md section 4) of each dataset that records cut
    flows (``cutoff:``), checked with core's ``lca.cutoff`` so that the build and
    ``cheme assess lca`` apply the same rule: each cut flow and all of them together below 1 % of
    the input mass, no never-cut flow. By dataset path, for ``datapackage.json``. A cut flow that
    fails core's schema is an error; a broken criterion is a warning (``--strict`` fails); a cut
    flow without an amount in kg is recorded, not warned (core's info). Without core installed the
    criteria are not checked: a warning."""
    cut = [(p, d) for p in processes for d in p.datasets if d.data.get("cutoff")]
    if not cut:
        return {}
    try:
        import chemeascode.domains.assessment.lca.cutoff as core_cutoff
        from chemeascode.domains.assessment.lca.schemas import CutoffFlow
        from pydantic import ValidationError
    except ImportError:
        for _, dataset in cut:
            report.warn(dataset.path, "cutoff: the cut-off criteria are not checked: they need core's chemeascode (lca.cutoff) installed")
        return {d.path: {"flows": sorted(f.get("key", "") for f in d.data["cutoff"] if isinstance(f, dict)), "checked": False, "findings": []} for _, d in cut}
    results = {}
    for _, dataset in cut:
        data = dataset.data
        flows, problems = [], []
        for number, flow in enumerate(data["cutoff"] if isinstance(data["cutoff"], list) else [data["cutoff"]]):
            try:
                flows.append(CutoffFlow.model_validate(flow))
            except ValidationError as failure:
                problems.extend(f"cutoff[{number}]{''.join(f'.{x}' for x in e['loc'])}: {e['msg']}" for e in failure.errors())
        if problems:
            report.error(dataset.path, "; ".join(problems))
            continue
        # the fields core's input mass reads (the treatment is for a system-model rule not read here)
        exchanges = [
            SimpleNamespace(
                key=e["key"], type=e["type"], amount=e["amount"], unit=e["unit"], phase=e.get("phase", "operation"), treatment=None,
                carrier=SimpleNamespace(kind=e["carrier"].get("kind")) if isinstance(e.get("carrier"), dict) else None,
            )
            for e in data["exchanges"]
        ]
        view = SimpleNamespace(system_model=data.get("system_model"), basis=data.get("basis", "1 h of operation"), exchanges=exchanges, cutoff=flows)
        found = [f for f in core_cutoff.findings(view, dataset.path) if f.rule in CUTOFF_RULES]
        for finding in found:
            if finding.level != "info":
                report.warn(dataset.path, f"cutoff: {finding.message} ({finding.rule}; {finding.hint})")
        results[dataset.path] = {
            "flows": sorted(f.key for f in flows),
            "checked": True,
            "input_mass_kg": _number(core_cutoff.input_mass(view)),
            "findings": [{"rule": f.rule, "level": f.level, "message": f.message} for f in found],
        }
    return results


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


ALLOCATION_SOURCES = {
    "mappings": "the database's (lci/mappings.yaml allocation)",
    "study": "the study's (lca/lca.yaml)",
    "dataset": "the dataset's default",
    "default": "the default (mass)",
    "hierarchy": "the hierarchy's price-ratio rule, not the study's",
}


def _successor_text(successor: dict, key: str) -> str:
    """The successor of a deprecated activity: its activity code for the same product when the
    build has one, else the dataset id and version."""
    same = [code for code in successor["activities"] if code.endswith(f":{key}")]
    return same[0] if same else f"dataset {successor['id']} {successor['version']}" + ("" if successor["resolved"] else " (not in this build)")


def _comment(process: Process, dataset: Dataset, row: dict, skipped: list[str], excluded: list[str], model: str, commit: str | None, version: str, unlinked: list[str] | None = None) -> str:
    method = dataset.allocation.get("method", "mass")
    share_text = ", ".join(f"{_name({'key': k})} {v * 100:.1f} %" for k, v in sorted(dataset.shares.items(), key=lambda kv: -kv[1]))
    lines = [
        f"ChemE-as-Code Process Atlas, process {process.pid}: {process.manifest['title']}.",
        f"Maturity: {process.manifest.get('maturity', 'unknown')}; review: {(process.manifest.get('validation') or {}).get('status', 'unknown')}. Screening-level data.",
        f"System model: {SYSTEM_MODELS[model]} ({METHODOLOGY_DOCUMENT}, methodology {METHODOLOGY_VERSION})."
        + ("" if model == "cutoff" else " A labelled variant, not the default cut-off database: it contains avoided-burden credits."),
        f"1 {row['unit']} of {row['reference product']}, from the unallocated LCI dataset {dataset.data['id']} ({dataset.path}, basis {dataset.data.get('basis', '1 h of operation')}).",
        f"Allocation: {method}, {ALLOCATION_SOURCES[dataset.allocation_source]}; hierarchy rule {dataset.rule}: {dataset.reason}; shares {share_text}. One single-output activity per co-product; the multi-output form is in the openLCA JSON-LD and Brightway multifunctional files of the build.",
        "Construction, maintenance, transport and end of life are technosphere inputs per unit of product, spread over the plant's life as in the dataset.",
        "Technosphere amounts are quantities of the linked reference product (a treatment activity is linked with the sign flipped by the installer).",
    ]
    if row.get("state"):
        lines.append(f"Product state: {row['state']}.")
    if dataset.successor:
        lines.append(f"DEPRECATED: superseded by {_successor_text(dataset.successor, row['key'])}. Kept so that existing links resolve; use the successor.")
    if skipped:
        lines.append("Not exported: " + "; ".join(skipped) + ".")
    if excluded:
        lines.append("Excluded by the cut-off system model (no credit): " + "; ".join(excluded) + ".")
    if unlinked:
        lines.insert(1, f"PRELIMINARY: {len(unlinked)} exchange(s) of this dataset have no mapping yet, so its LCI is incomplete; do not read a result from it as complete.")
        lines.append(
            "UNLINKED (mapping gaps of a preliminary LCI): " + "; ".join(unlinked)
            + ". These exchanges have no background link and count no burden; install() refuses the database until they are mapped."
        )
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


@dataclass
class Built:
    activities: list[Activity]
    proxies: list[Activity]
    markets: list[Activity]
    #: process id -> its activity rows
    by_process: dict[str, list[dict]]
    #: every market of markets/, exported or not, for datapackage.json
    market_entries: list[dict] = field(default_factory=list)
    #: every Atlas-to-Atlas link with its compatibility check
    links: list[dict] = field(default_factory=list)


def build_activities(processes: list[Process], mappings: dict, products: reg.Registry, db_name: str, commit: str | None, version: str, report: Report, model: str = "cutoff", excluded_log: list[dict] | None = None, markets: list[mk.Market] | None = None, public: bool = False) -> Built:
    """*mappings* is the profile of *model* (``profile()``); every exchange the cut-off model
    excludes is appended to *excluded_log*."""
    utilities = {slug for slug, entry in products.chemicals.items() if entry.get("kind") == "utility"}
    linker = Linker(mappings, db_name, set(products.chemicals), utilities=utilities, model=model, markets=list(markets or []))
    excluded_log = [] if excluded_log is None else excluded_log
    links: list[dict] = []
    rows_by_process: dict[str, list[tuple[Dataset, dict]]] = {}
    for process in processes:
        for dataset in process.datasets:
            for row in _product_rows(process, dataset, products):
                rows_by_process.setdefault(process.pid, []).append((dataset, row))
                linker.by_dataset[(dataset.path, row["key"])] = row
                if row["chemical"]:
                    linker.producers.setdefault(row["chemical"], []).append((process.pid, row))
    for producers in linker.producers.values():
        producers.sort(key=lambda p: (p[0], p[1]["code"]))
    identities: dict[tuple, str] = {}
    for rows in rows_by_process.values():
        for dataset, row in rows:
            identity = (row["name"], row["reference product"], row["location"], row["unit"])
            if identity in identities:
                report.error(
                    dataset.path,
                    f"{row['code']} has the name, reference product, location and unit of {identities[identity]}: "
                    "the installer cannot tell them apart (a second dataset of one process for the same product needs its own "
                    "location, or must be a design case's dataset written by cheme assess lca --write --case, whose activity "
                    "name carries the case: ADR 0034)",
                )
            identities[identity] = row["code"]
            linker.datasets[row["code"]] = dataset
            linker.rows[row["code"]] = row
    market_activities, market_entries = build_markets(linker, products, db_name, commit, version, report, public, links)

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
            excluded: list[str] = []
            unlinked: list[str] = []
            for exchange in dataset.data["exchanges"]:
                if exchange["type"] == "product":
                    continue
                try:
                    kind, target = linker.resolve(process, dataset, exchange)
                except GapError as failure:
                    # a gap of a preliminary LCI, public or not (ADR 0026): exported unlinked (no database, no guess), never dropped
                    reason = str(failure).removeprefix(f"{dataset.path} {exchange['key']}: ")
                    report.gap(process.pid, dataset, exchange, failure.link, reason)
                    unlinked.append(f"{exchange['key']} ({reason})")
                    kind = "biosphere" if failure.link == "biosphere" else "technosphere"
                    target = {"name": _name(exchange), "unit": BW_UNITS[exchange["unit"]], "atlas gap": f"unlinked, no {failure.link} mapping: {reason}"}
                except BuildError as failure:
                    report.errors.append(str(failure))
                    continue
                if kind == "skip":
                    skipped.append(str(target))
                    continue
                if kind == "excluded":
                    excluded.append(f"{exchange['key']} ({target})")
                    entry = {"process": process.pid, "dataset": dataset.data["id"], "key": exchange["key"], "decision": target}
                    if entry not in excluded_log:
                        excluded_log.append(entry)
                    continue
                unallocated = float(exchange["amount"]) * (target.pop("amount factor", 1.0) if kind == "biosphere" else 1.0)
                amount = _number(unallocated * per_unit)
                gap = "atlas gap" in target
                if model == "cutoff" and kind == "technosphere" and amount < 0 and not gap:
                    refusal = (
                        f"{dataset.path} {exchange['key']}: negative technosphere amount: an avoided burden (credit), which a "
                        "cut-off build refuses; list the flow in lci/mappings.yaml cutoff_exclusions, or build the substitution variant"
                    )
                    if refusal not in report.errors:  # once per exchange, not per co-product
                        report.errors.append(refusal)
                    continue
                entry = {"amount": amount, "type": kind, "atlas key": exchange["key"], **target}
                entry["_unallocated"] = _number(unallocated)  # per basis, for the multi-output formats (not a workbook column)
                if gap:
                    pass  # unlinked: no categories, no provider, no Atlas alternative
                elif kind == "biosphere":
                    entry["categories"] = "::".join(target["categories"])
                elif target.get("atlas link") == "pinned":
                    # an exchange linked explicitly (link.dataset) has chosen its producer (its carrier was
                    # checked in resolve); one mapped to a proxy may still prefer an Atlas producer
                    provider = linker.rows[target["atlas code"]]
                    chemical = _chemical(process, exchange, mappings, linker.registry)
                    check = linker.check(chemical, process.grades.get(exchange["key"]), provider, "pinned", exchange.get("carrier"))
                    entry["atlas check"] = check["text"]
                    links.append(_link(row, exchange, provider, "pinned", check))
                else:
                    link_atlas(linker, process, exchange, row, entry, target, report, links)
                entry.update(_uncertainty(exchange, amount))
                kind_of = (exchange.get("uncertainty") or {}).get("distribution", "lognormal")
                if kind_of != "lognormal":
                    report.warn(f"{dataset.path} {exchange['key']}", f"uncertainty distribution {kind_of!r} (and the pedigree) is not exported: Brightway sees this exchange as deterministic")
                entry.update(_pedigree_column(exchange))
                carrier = _carrier_text(exchange.get("carrier"))
                if carrier:
                    entry["atlas carrier"] = carrier
                if exchange.get("title"):
                    entry["comment"] = exchange["title"]
                exchanges.append(entry)
            comment = _comment(process, dataset, row, skipped, excluded, model, commit, version, unlinked)
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
                "atlas system model": model,
                "atlas methodology version": METHODOLOGY_VERSION,
            }
            if row.get("state"):
                metadata["atlas product state"] = row["state"]
            if row.get("carrier"):
                metadata["atlas carrier"] = _carrier_text(row["carrier"])
            if dataset.successor:
                metadata["atlas superseded by"] = _successor_text(dataset.successor, row["key"])
            if unlinked:
                metadata["atlas gaps"] = len(unlinked)
                metadata["atlas preliminary"] = True
            activities.append(Activity(row, comment, metadata, exchanges))

    proxies: list[Activity] = []
    for pid in sorted(linker.proxies_used):
        proxy = mappings["proxies"][pid]
        row = {"code": f"proxy:{pid}", "name": proxy["name"], "reference product": proxy["reference_product"], "unit": proxy["unit"], "location": proxy["location"]}
        exchanges = [{"name": row["name"], "amount": 1.0, "unit": row["unit"], "type": "production", "database": db_name, "reference product": row["reference product"], "location": row["location"]}]
        for item in proxy["inputs"]:
            if model == "cutoff" and item["amount"] < 0:  # load_mappings refuses it already
                report.error(f"proxies.{pid}", f"negative input of {item['use']}: an avoided-burden credit in a cut-off build")
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
    return Built(activities, proxies, market_activities, by_process, market_entries, links)


def _link(consumer: dict, exchange: dict | str, provider: dict, kind: str, check: dict, plant: dict | None = None) -> dict:
    return {
        "consumer": consumer["code"],
        "key": exchange if isinstance(exchange, str) else exchange["key"],
        "provider": provider["code"],
        "kind": kind,
        "plant": plant["code"] if plant else None,
        "compatible": check["compatible"],
        "checks": check["checks"],
    }


def link_atlas(linker: Linker, process: Process, exchange: dict, row: dict, entry: dict, target: dict, report: Report, links: list[dict]) -> None:
    """Name the Atlas activity an input linked to the background can link to instead
    (``prefer_atlas``): the market of its grade, else the plant (a warning), with the plant beside
    a market for pinning, and the compatibility check of each."""
    choice = linker.atlas_alternative(process, exchange, target["unit"], row["location"])
    if choice is None:
        return
    where = f"{process.pid}: {exchange['key']}"
    chemical = _chemical(process, exchange, linker.mappings, linker.registry)
    wanted = process.grades.get(exchange["key"])

    def warn(message: str) -> None:  # once per input, not once per co-product of the consumer
        if f"{where}: {message}" not in report.warnings:
            report.warn(where, message)

    if choice.target is None:
        links.append({"consumer": row["code"], "key": exchange["key"], "provider": None, "kind": "refused", "plant": None, "compatible": False,
                      "checks": {"grade": {"status": "mismatch", "text": "; ".join(choice.refused)}}})
        return
    # a utility serves only within its operating range: the chosen target's carrier (a market's,
    # else that of the plant beside it) must cover the exchange's
    supply = choice.target.get("carrier") or (choice.plant or {}).get("carrier")
    refusal = carrier_refusal(exchange.get("carrier"), supply)
    if refusal:
        warn(f"not linked inside the Atlas: {choice.target['name']} is outside its operating range ({refusal}); the background mapping is used")
        links.append({"consumer": row["code"], "key": exchange["key"], "provider": None, "kind": "refused", "plant": None, "compatible": False,
                      "checks": {"carrier": {"status": "mismatch", "text": f"{choice.target['code']}: {refusal}"}}})
        return
    market = choice.target if choice.target.get("market") else None
    outside = [(pid, other) for pid, other in choice.others if not market or other["code"] not in market["suppliers"]]
    if outside:
        used = f"{market['code']} is used, and does not take" if market else f"{choice.target['name']} is used, not"
        warn(f"several Atlas producers: {used} {', '.join(f'{pid}: {other['name']}' for pid, other in outside)}; link one explicitly (link.dataset) to choose")
    kind = "market" if market else "plant"
    if market is None and chemical not in linker.utilities:  # a site utility has no market yet (docs/markets.md)
        product = f"{chemical}/{choice.target['grade']}" if choice.target.get("grade") else chemical
        regions = f" (several markets, none for {row['location']}: {', '.join(choice.unchosen)})" if choice.unchosen else ""
        warn(f"no market of {product}{regions}: the Atlas link goes to the plant gate of {choice.target['name']} (no distribution or losses); add a market in markets/{chemical}.yaml (docs/markets.md)")
    check = linker.check(chemical, wanted, choice.target, kind, exchange.get("carrier"))
    if not check["compatible"]:
        warn(f"Atlas link to {choice.target['code']}: {check['text']}")
    entry.update({
        "atlas activity": choice.target["name"], "atlas reference product": choice.target["reference product"], "atlas location": choice.target["location"],
        "atlas code": choice.target["code"], "atlas link": kind, "atlas check": check["text"],
    })
    if choice.plant is not None:
        plant_check = linker.check(chemical, wanted, choice.plant, "pinned", exchange.get("carrier"))
        entry.update({
            "atlas plant activity": choice.plant["name"], "atlas plant reference product": choice.plant["reference product"],
            "atlas plant location": choice.plant["location"], "atlas plant code": choice.plant["code"], "atlas plant check": plant_check["text"],
        })
    links.append(_link(row, exchange, choice.target, kind, check, choice.plant))


def _market_name(market: mk.Market, product: str) -> str:
    name = f"market for {product[:1].lower()}{product[1:]}"
    return f"{name} ({market.technology} technology)" if market.technology else name


def build_markets(linker: Linker, products: reg.Registry, db_name: str, commit: str | None, version: str, report: Report, public: bool, links: list[dict]) -> tuple[list[Activity], list[dict]]:
    """The market activities (markets.py) and an entry per market for datapackage.json. A market
    is ``planned`` (not exported, with its reason), ``withheld`` (a supplier is not in a public
    build) or ``exported``. Registers the exported rows in *linker* (``market_rows``)."""
    entries: dict[str, dict] = {}
    pending: dict[str, tuple[mk.Market, list[dict | None]]] = {}
    for market in linker.markets:
        entry = {
            "code": market.code, "product": market.product, "chemical": market.chemical, "grade": market.grade, "region": market.region,
            "layer": market.layer, "technology": market.technology, "path": market.path, "facts": market.facts(),
        }
        entries[market.code] = entry
        if market.planned:
            entry.update(status="planned", reason=" ".join(market.data["planned"].split()))
            continue
        suppliers: list[dict | None] = []
        withheld = []
        for supplier in market.suppliers:
            if "market" in supplier:
                suppliers.append(None)  # an import: the other market, resolved below
                continue
            found = [r for pid, r in linker.producers.get(market.chemical, []) if pid == supplier["process"] and r.get("grade") == market.grade]
            if len(found) > 1:  # a deprecated dataset beside its successor: the market takes the current one
                current = [r for r in found if not r.get("deprecated")]
                found = current if len(current) == 1 else found
            if len(found) > 1:  # a design case's own dataset beside the study's: the study's (ADR 0034)
                study = [r for r in found if not r.get("design_case")]
                found = study if len(study) == 1 else found
            if len(found) == 1:
                suppliers.append(found[0])
            elif found:
                report.error(f"{market.path} {market.code}", f"supplier {supplier['process']} has {len(found)} activities of {market.product} (several datasets): the market cannot choose")
            elif public:
                withheld.append(supplier["process"])
            else:
                report.error(f"{market.path} {market.code}", f"supplier {supplier['process']} exports no activity of {market.product} (is it a product of its LCI dataset, with this grade?)")
        if withheld:
            entry.update(status="withheld", reason=f"supplier(s) {', '.join(withheld)} not in the public build")
            continue
        units = {s["unit"] for s in suppliers if s}
        if len(units) > 1:
            report.error(f"{market.path} {market.code}", f"its suppliers count the product in several units: {', '.join(sorted(units))}")
            continue
        pending[market.code] = (market, suppliers)

    # imports need the other market; a market whose import is withheld or planned is withheld too
    resolved = False
    while not resolved:
        resolved = True
        for code, (market, suppliers) in list(pending.items()):
            for supplier in market.suppliers:
                other = f"market:{market.product}:{supplier['market']}" if "market" in supplier else None
                if other and other not in pending:
                    entries[code].update(status="withheld", reason=f"imports from {other}, which is {entries.get(other, {}).get('status', 'not defined')}")
                    del pending[code]
                    resolved = False
                    break

    for code, (market, suppliers) in pending.items():
        unit = next((s["unit"] for s in suppliers if s), None)
        reference = (products.grade(market.chemical, market.grade) or {}).get("name") or (products.chemicals.get(market.chemical) or {}).get("name", market.chemical)
        linker.market_rows[code] = {
            "code": code, "name": _market_name(market, reference), "reference product": reference, "unit": unit or "kilogram",
            "location": market.region, "chemical": market.chemical, "grade": market.grade, "market": True, "layer": market.layer,
            "suppliers": [s["code"] for s in suppliers if s],
        }
    built: list[Activity] = []
    for code, (market, suppliers) in pending.items():
        row = linker.market_rows[code]
        for number, supplier in enumerate(market.suppliers):
            if "market" in supplier:
                suppliers[number] = linker.market_rows[f"market:{market.product}:{supplier['market']}"]
        activity, notes = _market_activity(linker, market, row, suppliers, report, db_name, commit, version, links)
        if activity is not None:
            entries[code].update(
                status="exported", name=row["name"], reference_product=row["reference product"], unit=row["unit"], location=row["location"],
                gross=_number(market.gross()), suppliers=[{"code": s["code"], "share": _number(w)} for s, w in zip(suppliers, market.weights())],
                not_exported=notes, consumption=(market.data.get("consumption") or {"trade_source": market.data.get("trade_source")}),
                excluded=market.data.get("excluded") or [],
            )
            built.append(activity)
    return sorted(built, key=lambda a: a.row["code"]), [entries[m.code] for m in linker.markets]


def _market_activity(linker: Linker, market: mk.Market, row: dict, suppliers: list[dict], report: Report, db_name: str, commit: str | None, version: str, links: list[dict]) -> tuple[Activity | None, list[str]]:
    where = f"{market.path} {market.code}"
    gross = market.gross()
    exchanges = [{"name": row["name"], "amount": 1.0, "unit": row["unit"], "type": "production", "database": db_name, "reference product": row["reference product"], "location": row["location"]}]
    notes: list[str] = []
    lines_supply = []
    failed = False
    for supplier, weight, provider in zip(market.suppliers, market.weights(), suppliers):
        kind = "import" if "market" in supplier else "supply"
        check = linker.check(market.chemical, market.grade, provider, kind)
        key = f"supplier:{supplier.get('process') or supplier['market']}"
        basis = supplier.get("share") or supplier["production_volume"]
        exchanges.append({
            "amount": _number(weight * gross), "type": "technosphere", **linker._own(provider), "atlas key": key, "atlas code": provider["code"],
            "atlas link": kind, "atlas check": check["text"], "comment": f"share {weight:.4g} ({basis['status']}: {' '.join(basis['source'].split())})",
        })
        links.append(_link(row, key, provider, kind, check))
        lines_supply.append(f"{provider['name']} | {provider['reference product']} {weight * 100:.1f} %")
        for leg in supplier.get("transport") or []:
            failed |= _leg(linker, market, leg, weight * gross, f"transport:{supplier.get('process') or supplier['market']}:{leg['mode']}", exchanges, notes, report)
    for leg in market.data.get("distribution") or []:
        failed |= _leg(linker, market, leg, gross, f"distribution:{leg['mode']}", exchanges, notes, report)
    mass = gross
    for loss in market.data.get("losses") or []:
        lost = mass * float(loss["fraction"])
        mass -= lost
        component = loss.get("released_as")
        text = f"{loss['kind']} {float(loss['fraction']) * 100:.3g} % ({loss['status']}: {' '.join(loss['source'].split())})"
        if component is None:
            notes.append(f"loss:{loss['kind']} {_number(lost):g} {row['unit']} per {row['unit']}: lost, no release named")
        elif component in linker.mappings["biosphere"]:
            if row["unit"] != "kilogram":
                report.error(where, f"loss {loss['kind']} released as {component}: the product is counted in {row['unit']}, a release needs kilogram")
                failed = True
                continue
            flow = linker.mappings["biosphere"][component]["flow"]
            exchanges.append({"amount": _number(lost), "type": "biosphere", "name": flow["name"], "categories": "::".join(flow["categories"]), "unit": "kilogram",
                              "atlas key": f"loss:{loss['kind']}", "comment": text})
        elif component in linker.mappings["pass_through"]:
            notes.append(f"loss:{loss['kind']} {_number(lost):g} {row['unit']} per {row['unit']} released as {component} (an atmospheric constituent, as lci/mappings.yaml pass_through: no burden, not exported)")
        else:
            report.error(where, f"loss {loss['kind']} released as {component!r}, which is neither in lci/mappings.yaml biosphere nor in pass_through")
            failed = True
    if failed:
        return None, notes
    consumption = market.data.get("consumption")
    if consumption:
        statement = f"Consumption: {'equals production' if consumption['equals_production'] else 'differs from production'}: {' '.join(consumption['reason'].split())}"
    elif market.layer == "consumption-mix":
        statement = f"Consumption mix from trade data: {' '.join(market.data['trade_source'].split())}"
    else:
        statement = f"One technology ({market.technology}): chosen explicitly, never the default link of an input."
    lines = [
        f"ChemE-as-Code Process Atlas market {market.code}: {mk.LAYERS[market.layer]} ({market.path}, docs/markets.md).",
        f"System model: {SYSTEM_MODELS[linker.model]} ({METHODOLOGY_DOCUMENT}, methodology {METHODOLOGY_VERSION}).",
        f"1 {row['unit']} of {row['reference product']} delivered in {row['location']}; {_number(gross):g} {row['unit']} taken from the suppliers (losses on the way).",
        "Suppliers: " + "; ".join(lines_supply) + ".",
        statement,
        "Every share, volume, distance and loss has its status (cited, calculated, assumed) and source in datapackage.json (markets) and the market file.",
    ]
    if notes:
        lines.append("Not exported: " + "; ".join(notes) + ".")
    if market.data.get("excluded"):
        lines.append("Outside the market: " + "; ".join(" ".join(x.split()).rstrip(".") for x in market.data["excluded"]) + ".")
    lines.append(f"Atlas LCI {version}; library commit {commit or 'unknown'}.")
    comment = "\n".join(lines)
    metadata = {
        "code": row["code"], "reference product": row["reference product"], "unit": row["unit"], "location": row["location"], "type": "process",
        "production amount": 1, "comment": comment, "atlas market": market.code, "atlas layer": market.layer,
        "atlas system model": linker.model, "atlas methodology version": METHODOLOGY_VERSION,
    }
    return Activity(row, comment, metadata, exchanges), notes


def _leg(linker: Linker, market: mk.Market, leg: dict, mass: float, key: str, exchanges: list[dict], notes: list[str], report: Report) -> bool:
    """A transport leg as ton kilometer of its technosphere entry (``mass`` kg carried per unit
    delivered); a leg without one (a pipeline) is recorded only. True when it failed."""
    distance = float(leg["distance"]["value"])
    text = f"{leg['mode']} {distance:g} km ({leg['distance']['status']}: {' '.join(leg['distance']['source'].split())})"
    if not leg.get("use"):
        notes.append(f"{key} {distance:g} km: no background activity (driven by the producer's delivery pressure; pipeline infrastructure outside the market)")
        return False
    if leg["use"] not in linker.mappings["technosphere"]:
        report.error(f"{market.path} {market.code}", f"transport {leg['mode']} uses unknown technosphere entry {leg['use']!r}")
        return True
    try:
        target = linker.technosphere(leg["use"], "ton kilometer", f"{market.path} {market.code} {key}")
    except BuildError as failure:
        report.errors.append(str(failure))
        return True
    exchanges.append({"amount": _number(mass / 1000.0 * distance), "type": "technosphere", **target, "atlas key": key, "comment": text})
    return False


def multi_output_datasets(processes: list[Process], activities: list[Activity], products: reg.Registry) -> list[dict]:
    """The unallocated multi-output form of every exported dataset, for the writers of
    ``export_formats.py``: plain data from the same linking as the workbook (no second source of
    truth). Per dataset: its products (every product, a share of 0 included, with the allocation
    properties the dataset or study states: mass for a product in kg, exergy, energy, price) and
    its other exchanges with their amounts per basis (``_unallocated``), linked as in the
    workbook's activities."""
    by_dataset: dict[tuple[str, str], list[Activity]] = {}
    for activity in activities:
        by_dataset.setdefault((activity.metadata["atlas process"], activity.metadata["atlas dataset"]), []).append(activity)
    found = []
    for process in processes:
        for dataset in process.datasets:
            allocated = by_dataset.get((process.pid, dataset.data["id"]))
            if not allocated:
                continue
            first = allocated[0]
            items = []
            for row in _product_rows(process, dataset, products, all_products=True):
                exchange = next(e for e in dataset.data["exchanges"] if e["key"] == row["key"])
                given = _properties(exchange, dataset.allocation)
                properties = {"mass": 1.0} if exchange["unit"] == "kg" else {}
                properties.update({k: float(v) for k, v in given.items() if v is not None})
                items.append(
                    {
                        **{k: row[k] for k in ("code", "name", "reference product", "unit", "location", "key", "amount", "chemical", "grade", "state")},
                        "share": dataset.shares.get(row["key"], 0.0),
                        "properties": properties,
                        "properties_source": " ".join(str((exchange.get("properties") or {}).get("source") or "").split()),
                    }
                )
            exchanges = []
            for entry in first.exchanges[1:]:
                amount = entry["_unallocated"]
                # the lognormal of the amount per basis: the same spread, its own location
                moved = {k: v for k, v in entry.items() if k not in ("_unallocated", "loc", "negative")}
                moved["amount"] = amount
                if entry.get("uncertainty type") == 2 and amount != 0:
                    moved["loc"] = _number(math.log(abs(amount)))
                    if amount < 0:
                        moved["negative"] = True
                exchanges.append(moved)
            notes = [line for line in first.comment.splitlines() if line.startswith(("Not exported:", "Excluded by the cut-off", "DEPRECATED:", "UNLINKED"))]
            version, _ = _dataset_version(dataset)
            found.append(
                {
                    "code": f"{process.pid}:{dataset.data['id']}",
                    "process": process.pid,
                    "dataset": dataset.data["id"],
                    "path": dataset.path,
                    "uuid": dataset.data.get("uuid"),
                    "name": first.row["name"],
                    "title": process.manifest.get("title", process.pid),
                    "maturity": process.manifest.get("maturity", ""),
                    "location": first.row["location"],
                    "basis": dataset.data.get("basis", "1 h of operation"),
                    "version": version,
                    "valid_until": dataset.data.get("valid_until"),
                    "technology": dataset.data.get("technology"),
                    "description": dataset.data.get("description"),
                    "allocation": {"method": dataset.allocation.get("method", "mass"), "rule": dataset.rule, "reason": dataset.reason, "source": dataset.allocation_source},
                    "products": items,
                    "exchanges": exchanges,
                    "notes": notes,
                }
            )
    return found


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


def write_workbook(path: Path, db_name: str, database_meta: dict, activities: list[Activity], proxies: list[Activity], about: list[str], markets: list[Activity] | None = None) -> None:
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
    if markets:
        ws = wb.create_sheet("markets")
        for activity in markets:
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


# --- change report ---------------------------------------------------------------------------

#: Exchange fields that say what an exchange links to (the database name is left out: it carries
#: the version, so it changes in every release).
LINK_FIELDS = ("name", "reference product", "unit", "location", "categories")


def read_workbook(path: Path) -> dict[str, dict]:
    """The activities of an Atlas workbook by code, read as bw2io's ExcelImporter reads them
    (sections by their first cell): ``{code: {"name", "meta", "exchanges"}}``."""
    from openpyxl import load_workbook

    found: dict[str, dict] = {}
    wb = load_workbook(path, read_only=True, data_only=True)
    for ws in wb:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        if not rows or rows[0][0] in ("skip", "Database"):
            continue
        current: dict | None = None
        columns: list | None = None
        for row in rows:
            first = row[0] if row else None
            if first == "Activity":
                current, columns = {"name": row[1], "meta": {}, "exchanges": []}, None
            elif current is None or first is None:
                continue
            elif first == "Exchanges":
                columns = []
            elif columns == []:
                columns = [c for c in row if c is not None]
            elif columns:
                current["exchanges"].append({c: v for c, v in zip(columns, row) if v is not None})
            else:
                current["meta"][first] = row[1]
                if first == "code":
                    found[row[1]] = current
    wb.close()
    return found


def _by_exchange(exchanges: list[dict]) -> dict[str, dict]:
    """Exchanges by ``<type> <atlas key>`` (a repeated key gets ``#2``, ``#3``)."""
    keyed: dict[str, dict] = {}
    for exchange in exchanges:
        base = f"{exchange.get('type')} {exchange.get('atlas key') or exchange.get('name')}"
        key, number = base, 1
        while key in keyed:
            number += 1
            key = f"{base}#{number}"
        keyed[key] = exchange
    return keyed


def _diff_activity(old: list[dict], new: list[dict]) -> dict:
    before, after = _by_exchange(old), _by_exchange(new)
    changed = []
    for key in sorted(before.keys() & after.keys()):
        a, b = before[key], after[key]
        entry: dict[str, Any] = {"exchange": key}
        x, y = float(a.get("amount") or 0), float(b.get("amount") or 0)
        if not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-15):
            entry["amount"] = [x, y]
            entry["relative_change"] = _number((y - x) / x) if x else None
        link_a, link_b = ({f: e.get(f) for f in LINK_FIELDS if e.get(f) is not None} for e in (a, b))
        if link_a != link_b:
            entry["link"] = [link_a, link_b]
        if len(entry) > 1:
            changed.append(entry)
    diff = {"added": sorted(after.keys() - before.keys()), "removed": sorted(before.keys() - after.keys()), "changed": changed}
    return {k: v for k, v in diff.items() if v}


def _datasets(package: dict) -> dict[tuple[str, str], dict]:
    return {(p["id"], d["id"]): d for p in package.get("processes", []) for d in p.get("datasets", [])}


def change_report(previous: Path, package: dict, workbook: Path) -> dict:
    """What changed since the build in *previous* (a folder holding ``lci/`` or the ``lci/``
    folder itself), per dataset and per activity, at exchange level."""
    folder = previous / "lci" if (previous / "lci" / "datapackage.json").is_file() else previous
    if not (folder / "datapackage.json").is_file():
        raise BuildError(f"--previous {previous}: no datapackage.json (expected an Atlas LCI build folder)")
    old_package = json.loads((folder / "datapackage.json").read_text(encoding="utf-8"))
    old_workbook = folder / old_package["resources"][0]["path"]
    if not old_workbook.is_file():
        raise BuildError(f"--previous {previous}: {old_workbook.name} is missing")
    old, new = read_workbook(old_workbook), read_workbook(workbook)

    datasets = []
    before, after = _datasets(old_package), _datasets(package)
    for key in sorted(before.keys() | after.keys()):
        a, b = before.get(key), after.get(key)
        entry: dict[str, Any] = {"process": key[0], "dataset": key[1]}
        if a is None:
            entry["status"] = "added"
        elif b is None:
            entry["status"] = "removed"
        else:
            content = a.get("content_sha256") != b.get("content_sha256") if a.get("content_sha256") else None
            old_alloc, new_alloc = a.get("allocation", {}), b.get("allocation", {})
            method = old_alloc.get("method") != new_alloc.get("method")
            # the shares change with the study's prices or a curated rule, not only with the dataset file
            allocation_changed = method or old_alloc.get("shares") != new_alloc.get("shares")
            entry["status"] = "changed" if content or allocation_changed else "unchanged" if content is False else "unknown"
            entry["content_changed"] = content
            entry["allocation_changed"] = allocation_changed
            if method:
                entry["allocation"] = [old_alloc.get("method"), new_alloc.get("method")]
            # governance: a changed dataset gets a new version (docs/governance.md)
            entry["version_not_raised"] = bool(content or allocation_changed) and a.get("version") == b.get("version")
        entry["version"] = [(a or {}).get("version"), (b or {}).get("version")]
        datasets.append(entry)

    changed = {}
    for code in sorted(old.keys() & new.keys()):
        diff = _diff_activity(old[code]["exchanges"], new[code]["exchanges"])
        if diff:
            changed[code] = diff
    old_model = old_package.get("system_model") or {}
    return {
        "schema": CHANGES_SCHEMA,
        "from": {"version": old_package.get("version"), "database": old_package.get("name"), "library_commit": (old_package.get("library") or {}).get("commit"),
                 "system_model": old_model.get("id", "unrecorded"), "methodology_version": (old_model.get("methodology") or {}).get("version", "unrecorded")},
        "to": {"version": package["version"], "database": package["name"], "library_commit": package["library"]["commit"],
               "system_model": package["system_model"]["id"], "methodology_version": package["system_model"]["methodology"]["version"]},
        "impact": reference_impacts.compare(old, new, old_package.get("name"), package["name"], datasets),
        "datasets": datasets,
        "activities": {"added": sorted(new.keys() - old.keys()), "removed": sorted(old.keys() - new.keys()), "changed": changed},
    }


def changes_markdown(changes: dict) -> str:
    a, b = changes["from"], changes["to"]
    lines = [
        f"# Change report: {a['database']} -> {b['database']}",
        "",
        (
            f"Library commit {a['library_commit'] or 'unknown'} -> {b['library_commit'] or 'unknown'}. "
            f"System model {a['system_model']} -> {b['system_model']}; methodology {a['methodology_version']} -> {b['methodology_version']}."
        ),
        "",
        "## Datasets",
        "",
        "| process | dataset | status | version | note |",
        "|---|---|---|---|---|",
    ]
    for d in changes["datasets"]:
        note = []
        if d.get("version_not_raised"):
            note.append(f"{'content' if d.get('content_changed') else 'allocation'} changed, version not raised")
        if d.get("allocation"):
            note.append(f"allocation {d['allocation'][0]} -> {d['allocation'][1]}")
        elif d.get("allocation_changed"):
            note.append("allocation shares changed")
        lines.append(f"| {d['process']} | {d['dataset']} | {d['status']} | {d['version'][0] or '-'} -> {d['version'][1] or '-'} | {'; '.join(note)} |")
    lines += ["", *reference_impacts.markdown(changes)]
    activities = changes["activities"]
    lines += ["## Activities", ""]
    for what in ("added", "removed"):
        for code in activities[what]:
            lines.append(f"- {what}: `{code}`")
    for code, diff in activities["changed"].items():
        lines += ["", f"### `{code}`", ""]
        for key in diff.get("added", []):
            lines.append(f"- added: {key}")
        for key in diff.get("removed", []):
            lines.append(f"- removed: {key}")
        for entry in diff.get("changed", []):
            parts = []
            if "amount" in entry:
                rel = entry.get("relative_change")
                parts.append(f"amount {entry['amount'][0]:.6g} -> {entry['amount'][1]:.6g}" + (f" ({rel * 100:+.2f} %)" if rel is not None else ""))
            if "link" in entry:
                parts.append(f"link {entry['link'][0].get('name')} -> {entry['link'][1].get('name')}")
            lines.append(f"- changed: {entry['exchange']}: {'; '.join(parts)}")
    if not activities["added"] and not activities["removed"] and not activities["changed"]:
        lines.append("No activity changed.")
    return "\n".join(lines) + "\n"


# --- build -----------------------------------------------------------------------------------


#: Dataset fields recorded as they are in ``datapackage.json``, beside the ones the
#: builder reads: identity, geography, technology, classification.
DOCUMENTATION = ("uuid", "geography", "time", "technology", "technology_level", "classification", "production_volume", "data_generator")
#: Review types, weakest first (core ``ReviewType``).
REVIEW_ORDER = ("none", "internal", "independent-external", "panel")


def _review(value: Any) -> dict:
    """A dataset's review as ``{status, records}``: ``status`` is ``unreviewed``, or the
    strongest type of its records (internal, independent-external, panel). Core accepts a list
    of records, one record, or ``unreviewed``; an absent review is unreviewed."""
    if value in (None, "", "unreviewed", "none"):
        return {"status": "unreviewed"}
    records = [value] if isinstance(value, dict) else [r for r in value if isinstance(r, dict)] if isinstance(value, list) else []
    types = [r.get("type") for r in records if r.get("type") in REVIEW_ORDER and r.get("type") != "none"]
    records = [r for r in records if r.get("type") != "none"]
    return {"status": max(types, key=REVIEW_ORDER.index), "records": records} if types else {"status": "unreviewed"}


def _dataset_entry(d: Dataset) -> dict:
    version, version_source = _dataset_version(d)
    allocation = {
        "method": d.allocation.get("method", "mass"),
        "source": d.allocation_source,
        "rule": d.rule,
        "reason": d.reason,
        "follows_hierarchy": d.finding is None,
        "shares": {k: _number(v) for k, v in sorted(d.shares.items())},
    }
    if d.finding:
        allocation["finding"] = d.finding
    return {
        "id": d.data["id"],
        "path": d.path,
        "basis": d.data.get("basis", "1 h of operation"),
        "version": version,
        "version_source": version_source,
        "methodology_version": str(d.data.get("methodology_version") or METHODOLOGY_VERSION),
        "methodology_version_source": "dataset" if d.data.get("methodology_version") else "build",
        "system_model": d.data.get("system_model"),
        "content_sha256": d.sha256 or _content_sha256(d.data),
        "review": _review(d.data.get("review")),
        "valid_until": d.data.get("valid_until"),
        "superseded_by": d.successor,
        "deprecated": d.successor is not None,
        "allocation": allocation,
        "data_status": _data_status(d.data),
        "data_quality": d.data_quality,
        "documentation": {k: d.data[k] for k in DOCUMENTATION if d.data.get(k)},
        "generator": (d.data.get("provenance") or {}).get("generator", ""),
    }


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dataset_version(dataset: Dataset) -> tuple[str, str]:
    """A dataset's semantic version and where it comes from: its own ``version`` (read once
    core adds the field; core's schema refuses it today), else the initial 0.1.0
    (docs/governance.md)."""
    if dataset.data.get("version"):
        return str(dataset.data["version"]), "dataset"
    return "0.1.0", "initial"


def _content_sha256(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def build(library: Path, out: Path, version: str, commit: str | None = None, mappings_path: Path | None = None, public: bool = False, system_model: str | None = None, previous: Path | None = None) -> Report:
    report = Report()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]*", version):
        report.error("--version", f"{version!r}: letters, digits and . + _ - only")
        return report
    if previous is not None and previous.resolve() in (out.resolve(), (out / "lci").resolve()):
        report.error("--previous", "must not be the output folder (its lci/ is replaced)")
        return report
    mappings_path = mappings_path or (library / "lci" / "mappings.yaml")
    if not mappings_path.is_file():
        mappings_path = _base_dir("lci") / "mappings.yaml"
    try:
        mappings = load_mappings(mappings_path)
    except BuildError as failure:
        report.errors.append(str(failure))
        return report
    foreign = frozenset() if mappings_path.resolve().parent == (library / "lci").resolve() else frozenset(mappings["exchanges"])
    merge_process_mappings(library, mappings, report)
    if report.errors:
        return report
    registry_path = library / "chemicals" / "chemicals.yaml"
    if not registry_path.is_file():
        report.error(str(registry_path), "missing chemical registry")
        return report
    data = _yaml(registry_path) or {}
    schema = json.loads((_base_dir("schemas") / "chemicals.schema.json").read_text(encoding="utf-8"))
    problems = [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in Draft202012Validator(schema).iter_errors(data)]
    for message in problems or reg.check(reg.load(data)):
        report.error("chemicals/chemicals.yaml", message)
    if report.errors:
        return report
    products = reg.load(data)
    families_path = library / "taxonomy" / "families.yaml"
    taxonomy = reg.load_families(families_path if families_path.is_file() else _base_dir("schemas").parent / "taxonomy" / "families.yaml")
    benchmarks, problems = bm.load(library / "benchmarks", _base_dir("schemas") / "benchmarks.schema.json", taxonomy)
    for message in problems:
        report.errors.append(message)
    markets, problems = mk.load(library / "markets", _base_dir("schemas") / "markets.schema.json", products, library)
    for message in problems:
        report.errors.append(message)
    if report.errors:
        return report
    background_check, problems = check_mappings.status(mappings, mappings_path.parent / "mapping-checks", _base_dir("schemas") / "lci-mapping-check.schema.json")
    for message in problems:
        report.errors.append(message)
    if report.errors:
        return report
    model = system_model or mappings["system_model"]
    if model not in SYSTEM_MODELS:
        report.error("--system-model", f"{model!r} is not one of {', '.join(SYSTEM_MODELS)}")
        return report

    own_repo = _git(library, "rev-parse", "--show-toplevel") == str(library)
    if commit is None and own_repo:
        commit = _git(library, "rev-parse", "HEAD")
    dirty = bool(_git(library, "status", "--porcelain")) if own_repo else None

    processes = _discover(library, report, mappings, public, products)
    check_overrides(library, processes, mappings, set(products.chemicals), report, public, foreign)
    check_system_models(processes, model, report)
    resolve_successors(processes, report)
    # the default model's database carries the plain name; a variant is labelled in its name
    db_name = f"cheme-as-code-atlas-{version}" if model == mappings["system_model"] else f"cheme-as-code-atlas-{version}-{model}"
    excluded: list[dict] = []
    built = build_activities(processes, profile(mappings, model), products, db_name, commit, version, report, model, excluded, markets, public)
    activities, proxies, by_process = built.activities, built.proxies, built.by_process
    checks = {d.path: property_checks(p, d, products, mappings, report) for p in processes for d in p.datasets}
    kpis = benchmark_results(processes, benchmarks, public, report)
    cutoffs = cutoff_results(processes, report)
    if report.errors:
        return report
    if not activities:
        report.warn(str(library), "no process has an LCI dataset (processes/<id>/lca/dataset.yaml or lca/datasets/*.yaml)")

    lci = out / "lci"
    if lci.exists():
        shutil.rmtree(lci)
    lci.mkdir(parents=True)
    xlsx_name = f"{db_name}.xlsx"
    preliminary_note = (
        f"PRELIMINARY: {len(report.gaps)} exchange(s) of {len({g['process'] for g in report.gaps})} process(es) have no mapping yet: "
        "exported unlinked, without a background link (column atlas gap, lci/gaps.json); those activities are marked atlas preliminary. "
        "install() refuses the database until they are mapped."
    )
    about = [
        f"ChemE-as-Code Process Atlas: LCI foreground database {db_name}.",
        "Brightway 2.5 (bw2io ExcelImporter) format. This sheet is skipped by the importer (A1 = skip).",
        "Import: pip install the helper (process-library python/, package cheme-as-code-lci), then cheme_as_code_lci.install(path, background=<your ecoinvent database>, location=<site country>).",
        f"Library commit: {commit or 'unknown'}. Mappings: lci/mappings.yaml. Details per process: datapackage.json.",
        f"System model: {SYSTEM_MODELS[model]} ({METHODOLOGY_DOCUMENT}, methodology {METHODOLOGY_VERSION}).",
        *CAVEATS,
        *([preliminary_note] if report.gaps else []),
    ]
    database_meta = {
        "format": "ChemE-as-Code Process Atlas LCI (bw2io Excel)",
        "atlas version": version,
        "atlas library commit": commit or "unknown",
        "atlas default background": DEFAULT_BACKGROUND,
        "atlas default site location": mappings["default_site_location"],
        "atlas system model": model,
        "atlas methodology version": METHODOLOGY_VERSION,
    }
    write_workbook(lci / xlsx_name, db_name, database_meta, activities, proxies, about, built.markets)
    # the other exchange formats (process-library#51): written from the same activities
    try:
        formats = export_formats.write_formats(
            lci, db_name, multi_output_datasets(processes, activities, products), built.markets, proxies, model, model == mappings["system_model"],
            mappings["default_site_location"], database_meta, about[:1] + about[3:5], list(CAVEATS),
        )
    except export_formats.FormatError as failure:
        report.errors.append(str(failure))
        return report
    workbook_format = {"name": xlsx_name, "format": "bw2io ExcelImporter workbook", "format_version": "bw2io 0.9 Excel layout", "mediatype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

    def activity_list(rows: list[dict]) -> list[dict]:
        return [{"code": r["code"], "name": r["name"], "reference_product": r["reference product"], "unit": r["unit"], "location": r["location"], **({"chemical": r["chemical"], "grade": r["grade"]} if "chemical" in r else {}), **({"state": r["state"]} if r.get("state") else {}), **({"carrier": r["carrier"]} if r.get("carrier") else {}), **({"superseded_by": r["superseded_by"]} if r.get("superseded_by") else {})} for r in rows]

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
                "allocation": {"method": first.allocation.get("method", "mass"), "source": first.allocation_source, "rule": first.rule},
                "datasets": [{**_dataset_entry(d), "property_checks": checks.get(d.path, []), "benchmarks": kpis.get(d.path, []), **({"cutoff": cutoffs[d.path]} if d.path in cutoffs else {})} for d in process.datasets],
                "activities": activity_list(by_process.get(process.pid, [])),
            }
        )
    variant_caveats = [] if model == "cutoff" else [
        (
            f"This is the {model} variant ({db_name}), not the default cut-off database: it contains avoided-burden credits "
            "(lci/mappings.yaml substitution). Do not mix it with the cut-off database in one study."
        )
    ]
    if built.markets:
        variant_caveats.append(
            "Markets (code market:*) mix the Atlas's own producers of a product, not the region's actual production; most of their "
            "distances and losses are ASSUMED screening values (datapackage.json markets, docs/markets.md)."
        )
    gaps_by_process: dict[str, list[dict]] = {}
    for gap in report.gaps:
        gaps_by_process.setdefault(gap["process"], []).append({k: v for k, v in gap.items() if k != "process"})
    for entry in process_entries:
        entry["gaps"] = gaps_by_process.get(entry["id"], [])
        entry["gap_count"] = len(entry["gaps"])
        entry["preliminary"] = bool(entry["gaps"])
    preliminary = sorted(gaps_by_process)
    if report.gaps:
        variant_caveats.append(
            f"PRELIMINARY: {len(report.gaps)} exchange(s) of {len(gaps_by_process)} process(es) are mapping gaps "
            f"(lci/gaps.json): exported unlinked, without a background link (column atlas gap), so they count no burden and these processes' inventories "
            f"are incomplete: {', '.join(preliminary)}. An activity that links one of them inherits that. install() refuses the database until they are mapped."
        )
    findings = [f"{d.path}: {d.finding}" for p in processes for d in p.datasets if d.finding]
    datapackage = {
        "schema": DATAPACKAGE_SCHEMA,
        "name": db_name,
        "version": version,
        "citation": {"text": lci_activities.database_citation(version), "authors": list(lci_activities.CITATION_AUTHORS), "doi": None},
        "system_model": {
            "id": model,
            "label": SYSTEM_MODELS[model],
            "default": model == mappings["system_model"],
            "methodology": {"document": METHODOLOGY_DOCUMENT, "version": METHODOLOGY_VERSION},
            "excluded": excluded,
            "allocation_findings": findings,
        },
        "governance": {"document": "docs/governance.md", "versioning": "semantic: database release and every dataset"},
        "format": "bw2io ExcelImporter workbook",
        "library": {"commit": commit, "dirty": dirty},
        "brightway": {"database": db_name, "default_background": DEFAULT_BACKGROUND, "default_biosphere": DEFAULT_BIOSPHERE, "default_site_location": mappings["default_site_location"], "background_check": background_check},
        "resources": [{"path": f["name"], **{k: v for k, v in f.items() if k != "name"}} for f in (workbook_format, *formats)],
        "processes": process_entries,
        "proxies": activity_list([p.row for p in proxies]),
        "markets": built.market_entries,
        "atlas_links": built.links,
        "caveats": [*CAVEATS, *variant_caveats],
    }
    # per activity, what its Atlas page shows (website#37): scripts/lci_activities.py
    datapackage["activities"] = lci_activities.entries(
        activities, proxies, processes, products, taxonomy, db_name, model, SYSTEM_MODELS[model], datapackage["resources"], library, version, mappings["default_site_location"],
        markets=built.markets, market_entries=built.market_entries, default=model == mappings["system_model"],
    )
    datapackage["pedigree_indicators"] = list(lci_activities.PEDIGREE_INDICATORS)
    _write_json(lci / "datapackage.json", datapackage)
    # the stored report of the benchmark comparison (docs/benchmarks.md), allocated values included
    rows = [{"process": e["id"], "dataset": d["id"], **k} for e in process_entries for d in e["datasets"] for k in d["benchmarks"]]
    _write_json(lci / "benchmarks.json", bm.report(rows, "public" if public else "preview", {"commit": commit, "dirty": dirty}))
    # the mapping gaps (ADR 0022, ADR 0026): what to map before a process stops being preliminary
    _write_json(lci / "gaps.json", {"schema": GAPS_SCHEMA, "version": version, "database": db_name, "library_commit": commit, "count": len(report.gaps), "preliminary": preliminary, "processes": gaps_by_process})

    reports = []
    if previous is not None:
        try:
            changes = change_report(previous, datapackage, lci / xlsx_name)
        except BuildError as failure:
            report.errors.append(str(failure))
            return report
        _write_json(lci / "changes.json", changes)
        (lci / "CHANGES.md").write_text(changes_markdown(changes), encoding="utf-8")
        reports = ["changes.json", "CHANGES.md"]

    file_formats = {f["name"]: {k: v for k, v in f.items() if k in ("format", "format_version")} for f in (workbook_format, *formats)}
    file_formats["datapackage.json"] = {"format": "Atlas LCI datapackage", "format_version": DATAPACKAGE_SCHEMA}
    file_formats["benchmarks.json"] = {"format": "Atlas benchmark report", "format_version": bm.REPORT_SCHEMA}
    file_formats["gaps.json"] = {"format": "Atlas LCI mapping gaps", "format_version": GAPS_SCHEMA}
    file_formats.update({name: {"format": "Atlas LCI change report", "format_version": CHANGES_SCHEMA} for name in reports})
    caveats = [*CAVEATS, *variant_caveats]
    if background_check["status"] != "verified":
        detail = background_check.get("note") or f"{background_check['unmatched']} name(s) did not match {background_check['background']['database']} {background_check['background']['version']}"
        caveats.append(f"Background names (lci/mappings.yaml): {background_check['status']}, {detail} (datapackage.json brightway.background_check).")
    for entry in process_entries:
        if entry["factors_status"] == "placeholder":
            caveats.append(f"{entry['id']}: the study's characterisation factors are placeholders (example: true); the LCI carries no factors, but its plantcode results are not meaningful numbers.")
    index = {
        "schema": INDEX_SCHEMA,
        "version": version,
        "database": db_name,
        "library_commit": commit,
        "files": [
            {"name": name, "path": f"lci/{name}", "bytes": (lci / name).stat().st_size, "sha256": _sha256(lci / name), **file_formats.get(name, {})}
            for name in (xlsx_name, *(f["name"] for f in formats), "datapackage.json", "benchmarks.json", "gaps.json", *reports)
        ],
        "system_model": model,
        "methodology_version": METHODOLOGY_VERSION,
        "processes": {e["id"]: [{"code": a["code"], "name": a["name"], "reference_product": a["reference_product"], "unit": a["unit"], **({"preliminary": True} if e["preliminary"] else {})} for a in e["activities"]] for e in process_entries},
        "markets": [{"code": m.row["code"], "name": m.row["name"], "reference_product": m.row["reference product"], "unit": m.row["unit"], "location": m.row["location"]} for m in built.markets],
        "gaps": {pid: len(found) for pid, found in gaps_by_process.items()},
        "preliminary": preliminary,
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
    parser.add_argument("--mappings", type=Path, help="lci/mappings.yaml (default: <library>/lci/, else the process library's own)")
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--public", action="store_true", help="published processes only (publication.status: public)")
    parser.add_argument("--system-model", choices=sorted(SYSTEM_MODELS), help="default: the mappings' system_model (cutoff); substitution builds the labelled variant")
    parser.add_argument("--previous", type=Path, help="an earlier build (folder with lci/): write lci/changes.json and lci/CHANGES.md")
    args = parser.parse_args(argv)

    report = build(
        args.library.resolve(), args.out.resolve(), args.version, args.commit, args.mappings.resolve() if args.mappings else None, args.public,
        args.system_model, args.previous.resolve() if args.previous else None,
    )
    for gap in report.gaps:
        print(f"gap: {gap['process']}: {gap['path']} {gap['key']}: {gap['reason']}", file=sys.stderr)
    for message in report.warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in report.errors:
        print(f"error: {message}", file=sys.stderr)
    failed = bool(report.errors or (args.strict and report.strict_failures))
    if not failed:
        index = json.loads((args.out / "lci" / "index.json").read_text(encoding="utf-8"))
        count = sum(len(v) for v in index["processes"].values())
        markets = len(index.get("markets", []))
        print(f"lci: {count} activit{'y' if count == 1 else 'ies'} from {len(index['processes'])} process(es), {markets} market(s) -> {args.out / 'lci'}")
        if report.gaps:
            print(f"lci: {len(report.gaps)} mapping gap(s) in {len(index['gaps'])} preliminary process(es), exported unlinked -> {args.out / 'lci' / 'gaps.json'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
