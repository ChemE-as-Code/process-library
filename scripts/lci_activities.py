"""Per-activity documentation for ``datapackage.json`` (``activities``): what a dataset page of
the Atlas (``/lci/<code>/``, ChemE-as-Code/website#37) shows, so the site renders it without any
LCI logic of its own.

Every entry describes one exported activity as it is in the workbook: the allocated,
single-output activity per 1 unit of its reference product. It carries

- identity: ``code`` (stable), the dataset's UUID and version (core#179; no activity UUID: the
  library does not assign one), the process and dataset it comes from;
- ``header``: geography, time period, technology (level), production volume and classification
  (the dataset's own, core#179, else ISIC from the process's families in
  ``taxonomy/families.yaml`` and CPC/HS and CAS from the chemical registry, each with its source);
- ``allocation``: method, rule, source, reason, this product's share and any finding;
- ``exchanges``: every exported exchange with its amount per reference unit, unit, provenance
  (given, calculated, assumed), source text, pedigree scores and the lognormal they imply, the
  background link target by name (database, name, reference product, location, location rule),
  Atlas-internal links by code, and for elementary flows the biosphere3 UUID and compartment;
- ``used_by``: the activities of the database that link to this one;
- for a market (``kind: market``, ``markets/``, docs/markets.md): its suppliers and shares,
  transport and losses as exchanges with the status (cited, calculated, assumed) and source of
  each, and ``market`` with the datapackage's ``markets`` entry (layer, gross, facts, what is not
  exported, consumption); Atlas inputs link to markets by their ``market:<product>:<region>`` code
  (``atlas_alternative``), with the plant behind it as ``atlas_plant``;
- ``closure``: ``status: assessed`` with the dataset's mass, element and energy balance as
  ``lca/manifest.json`` records it (``balance``, core#174), or ``status: not-assessed`` with the
  reason;
- ``citation`` (DOI null until a release is deposited, docs/governance.md) and ``downloads``:
  each database file of this build that holds the activity (workbook, openLCA JSON-LD,
  multifunctional JSON) and how to find it there: the code, the JSON-LD process id and member,
  or the dataset code of the unallocated form;
- ``publication``: ``public`` or ``preview`` (``publication.py``). A ``--public`` build holds
  public processes only, so every entry of it is ``public``.

Dataset-level facts the page also shows (review, data quality, data status, benchmarks,
property checks, cut-off exclusions) stay where they are, in ``processes[].datasets[]``; an entry
names its dataset by ``process`` and ``dataset.id``. No entry carries an impact value: the LCI has
no characterisation factors, so placeholder factors cannot leak through it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from export_formats import _process_id
from publication import is_public

#: Order of the pedigree scores in a dataset's ``pedigree.scores`` (build_lci.PEDIGREE_FACTORS);
#: ``datapackage.json`` states it once (``pedigree_indicators``).
PEDIGREE_INDICATORS = ("reliability", "completeness", "temporal correlation", "geographical correlation", "further technological correlation")
#: What the per-dataset page names a database file's format by (its file name pattern).
FORMATS = {
    ".xlsx": "Brightway (bw2io ExcelImporter workbook)",
    "-olca-jsonld.zip": "openLCA JSON-LD",
    "-multifunctional.json": "Brightway multifunctional (unallocated)",
}
CLOSURE_SOURCE = "lca/manifest.json balance (core#174)"


def _format(path: str, mediatype: str | None) -> str:
    for suffix, label in FORMATS.items():
        if path.endswith(suffix):
            return label
    return mediatype or path.rsplit(".", 1)[-1]


def _identity(entry: dict) -> tuple:
    return (entry.get("name"), entry.get("reference product"), entry.get("location"), entry.get("unit"))


def _closure(library: Path, process: Any, dataset: Any) -> dict:
    """The dataset's balance from the plant's ``lca/manifest.json`` (core#174), else why none."""
    if dataset.path != f"processes/{process.pid}/lca/dataset.yaml":
        return {"status": "not-assessed", "reason": "a hand-written dataset: no lca/manifest.json records its balance (core#174)"}
    path = library / "processes" / process.pid / "lca" / "manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ValueError:
        manifest = {}
    balance = manifest.get("balance") if isinstance(manifest, dict) else None
    if not isinstance(balance, dict):
        return {"status": "not-assessed", "reason": "lca/manifest.json records no balance yet (written by cheme assess lca once core#174 is in)"}
    if balance.get("dataset") not in (None, dataset.data["id"]):
        return {"status": "not-assessed", "reason": f"lca/manifest.json records the balance of {balance.get('dataset')}, not of this dataset"}
    return {"status": "assessed", "source": CLOSURE_SOURCE, "balance": balance}


def _classification(process: Any, dataset: Any, row: dict, products: Any, families: dict[str, dict]) -> dict:
    own = dataset.data.get("classification")
    isic = sorted({code for slug in process.manifest.get("families") or [] for code in (families.get(slug) or {}).get("isic") or []})
    chemical = products.chemicals.get(row.get("chemical") or "") or {}
    product = chemical.get("classification") or {}
    out: dict[str, Any] = {"dataset": own or None}
    if isic:
        out["isic"] = {"codes": isic, "source": "taxonomy/families.yaml (ISIC Rev.4) of the process's families"}
    if product.get("cpc") or product.get("hs"):
        out["product"] = {**{k: product[k] for k in ("cpc", "hs") if product.get(k)}, "source": f"chemicals/chemicals.yaml ({row['chemical']})"}
    return out


def _exchange(entry: dict, source: dict | None, db_name: str, codes: dict[tuple, str]) -> dict:
    """One exported exchange of the workbook (*entry*) with the dataset exchange it comes from."""
    source = source or {}
    out: dict[str, Any] = {
        "key": entry.get("atlas key"),
        "title": source.get("title") or entry.get("comment") or "",
        "type": entry["type"],
        "amount": entry["amount"],
        "unit": entry["unit"],
        # core's default, as build_lci._data_status counts it
        "provenance": source.get("provenance") or "assumed",
        "source": " ".join(str(source.get("source") or "").split()),
    }
    if entry["type"] == "technosphere":
        out["direction"] = "input"
    elif entry["type"] == "biosphere":
        out["direction"] = "resource" if source.get("type") == "resource" else "emission"
    pedigree = source.get("pedigree") or {}
    if pedigree.get("scores"):
        out["pedigree"] = {"scores": list(pedigree["scores"]), "rule": pedigree.get("rule", "")}
    if entry.get("uncertainty type") == 2:
        out["uncertainty"] = {"distribution": "lognormal", "loc": entry["loc"], "scale": entry["scale"], **({"negative": True} if entry.get("negative") else {})}
    if entry.get("atlas carrier"):
        out["carrier"] = entry["atlas carrier"]
    if entry["type"] == "biosphere":
        out["flow"] = {
            "name": entry["name"],
            "uuid": entry.get("atlas flow uuid"),
            "compartment": [c for c in str(entry.get("categories") or "").split("::") if c],
            "database": entry.get("database"),
        }
    elif entry.get("database") == db_name:
        out["atlas"] = {
            "code": entry.get("atlas code") or codes.get(_identity(entry)),
            "name": entry["name"],
            "reference_product": entry["reference product"],
            "location": entry["location"],
            **({"kind": entry["atlas link"]} if entry.get("atlas link") else {}),
            **({"check": entry["atlas check"]} if entry.get("atlas check") else {}),
        }
    else:
        out["link"] = {
            "database": entry.get("database"),
            "name": entry["name"],
            "reference_product": entry.get("reference product"),
            "location": entry.get("location"),
            "location_rule": entry.get("atlas location rule"),
        }
        if entry.get("atlas activity"):
            alternative = {"name": entry["atlas activity"], "reference product": entry["atlas reference product"], "location": entry["atlas location"], "unit": entry["unit"]}
            out["atlas_alternative"] = {
                "code": entry.get("atlas code") or codes.get(_identity(alternative)),
                "name": entry["atlas activity"],
                "reference_product": entry["atlas reference product"],
                "location": entry["atlas location"],
                **({"kind": entry["atlas link"]} if entry.get("atlas link") else {}),
                **({"check": entry["atlas check"]} if entry.get("atlas check") else {}),
            }
        if entry.get("atlas plant code"):
            # a market is the alternative; the plant behind it, for an input that pins the plant
            out["atlas_plant"] = {
                "code": entry["atlas plant code"],
                "name": entry.get("atlas plant activity"),
                "reference_product": entry.get("atlas plant reference product"),
                "location": entry.get("atlas plant location"),
                **({"check": entry["atlas plant check"]} if entry.get("atlas plant check") else {}),
            }
    return out


#: A market exchange's comment ends in ``(<status>: <source>)`` (build_lci.build_markets).
MARKET_NOTE = re.compile(r"^(?P<title>.*?) \((?P<status>cited|calculated|assumed|given): (?P<source>.*)\)$", re.S)


def _downloads(resources: list[dict], code: str, *, dataset_code: str | None = None, dataset_uuid: str | None = None, products: int = 1, model: str = "cutoff", default: bool = True) -> list[dict]:
    """The database files of the build that hold the activity, and how to find it in each: the
    workbook and the multifunctional JSON by code (the multifunctional file holds a dataset with
    several products under the dataset's code, unallocated), the openLCA JSON-LD package by
    process id (a dataset's unallocated multi-output process, with its allocation factors).
    A file with this activity alone does not exist."""
    found = []
    for r in resources:
        path = r["path"]
        entry = {"path": path, "format": r.get("format") or _format(path, r.get("mediatype")), "mediatype": r.get("mediatype")}
        if r.get("format_version"):
            entry["format_version"] = r["format_version"]
        if path.endswith("-olca-jsonld.zip"):
            pid = _process_id(dataset_code, dataset_uuid, model, default) if dataset_code else _process_id(code, None, model, default)
            entry.update(select="process", value=pid, member=f"processes/{pid}.json")
            if dataset_code and products > 1:
                entry["note"] = "the dataset's unallocated multi-output process; this product's allocation factor is in it"
        elif path.endswith("-multifunctional.json"):
            single = not dataset_code or products == 1
            entry.update(select="code", value=code if single else dataset_code)
            if not single:
                entry["note"] = "the dataset unallocated, with all its products; this product is its desired_code"
        else:
            entry.update(select="code", value=code)
        found.append(entry)
    return found


def entries(
    activities: list,
    proxies: list,
    processes: list,
    products: Any,
    families: dict[str, dict],
    db_name: str,
    model: str,
    model_label: str,
    resources: list[dict],
    library: Path,
    version: str,
    site_location: str,
    markets: list | None = None,
    market_entries: list[dict] | None = None,
    default: bool = True,
) -> list[dict]:
    """The ``activities`` of ``datapackage.json``, sorted by code (see the module docstring).
    *markets* are the exported market activities, *market_entries* datapackage.json's
    ``markets`` (every market with its status, suppliers, facts and sources)."""
    markets = list(markets or [])
    codes = {_identity(a.exchanges[0]): a.row["code"] for a in [*activities, *proxies, *markets]}
    datasets = {(p.pid, d.data["id"]): (p, d) for p in processes for d in p.datasets}
    out: list[dict] = []
    for activity in activities:
        meta, row = activity.metadata, activity.row
        process, dataset = datasets[(meta["atlas process"], meta["atlas dataset"])]
        by_key = {e["key"]: e for e in dataset.data["exchanges"]}
        dataset_products = sum(1 for e in dataset.data["exchanges"] if e["type"] == "product")
        doc = dataset.data
        product = products.chemicals.get(row.get("chemical") or "") or {}
        share = dataset.shares.get(row["key"])
        share = None if share is None else float(f"{share:.12g}")  # as build_lci._number writes the dataset's shares
        version_text = str(doc.get("version") or "0.1.0")
        authors = [a.get("name") for a in process.manifest.get("authors") or [] if isinstance(a, dict) and a.get("name")]
        out.append(
            {
                "code": row["code"],
                "kind": "dataset",
                "process": process.pid,
                "process_title": process.manifest.get("title", process.pid),
                "dataset": {"id": doc["id"], "path": dataset.path, "uuid": doc.get("uuid"), "version": version_text, "title": doc.get("title", "")},
                "activity_uuid": None,
                "name": row["name"],
                "reference_product": row["reference product"],
                "unit": row["unit"],
                "location": row["location"],
                "chemical": row.get("chemical"),
                "grade": row.get("grade"),
                "cas": product.get("cas"),
                "state": row.get("state") or None,
                "description": " ".join(str(doc.get("description") or "").split()),
                "header": {
                    "geography": {"location": row["location"], "dataset": doc.get("geography"), "background_site_default": site_location},
                    "time": doc.get("time") or ({"start": doc["year"]} if doc.get("year") else None),
                    "valid_until": doc.get("valid_until"),
                    "technology": doc.get("technology"),
                    "technology_level": doc.get("technology_level"),
                    "boundary": doc.get("boundary"),
                    "basis": doc.get("basis", "1 h of operation"),
                    "production_volume": doc.get("production_volume"),
                    "maturity": process.manifest.get("maturity"),
                    "classification": _classification(process, dataset, row, products, families),
                    "rights": doc.get("rights"),
                },
                "system_model": {"id": model, "label": model_label},
                "allocation": {
                    "method": dataset.allocation.get("method", "mass"),
                    "rule": dataset.rule,
                    "source": dataset.allocation_source,
                    "reason": dataset.reason,
                    "share": share,
                    "follows_hierarchy": dataset.finding is None,
                    "finding": dataset.finding,
                },
                "reference_exchange": {"key": row["key"], "amount": 1, "unit": row["unit"]},
                "exchanges": [_exchange(e, by_key.get(e.get("atlas key")), db_name, codes) for e in activity.exchanges[1:]],
                "closure": _closure(library, process, dataset),
                "superseded_by": row.get("superseded_by"),
                "citation": {
                    "text": f"{', '.join(authors) + ': ' if authors else ''}{row['reference product']}, from {process.manifest.get('title', process.pid)} (dataset {doc['id']} {version_text}), ChemE-as-Code Process Atlas LCI database {version}, activity {row['code']}.",
                    "authors": authors,
                    "doi": None,
                },
                "downloads": _downloads(resources, row["code"], dataset_code=f"{process.pid}:{doc['id']}", dataset_uuid=doc.get("uuid"), products=dataset_products, model=model, default=default),
                "publication": "public" if is_public(process.manifest) else "preview",
            }
        )
    for proxy in proxies:
        meta, row = proxy.metadata, proxy.row
        out.append(
            {
                "code": row["code"],
                "kind": "proxy",
                "process": None,
                "name": row["name"],
                "reference_product": row["reference product"],
                "unit": row["unit"],
                "location": row["location"],
                "description": proxy.comment.splitlines()[1] if len(proxy.comment.splitlines()) > 1 else "",
                "system_model": {"id": model, "label": model_label},
                "reference_exchange": {"key": None, "amount": 1, "unit": row["unit"]},
                "exchanges": [_exchange(e, {"title": e.get("atlas key", ""), "provenance": "assumed", "source": e.get("comment", "")}, db_name, codes) for e in proxy.exchanges[1:]],
                "closure": {"status": "not-assessed", "reason": "a screening proxy of lci/mappings.yaml, not a dataset"},
                "citation": {"text": f"{row['name']}, ChemE-as-Code Process Atlas LCI database {version}, activity {row['code']}.", "authors": [], "doi": None},
                "downloads": _downloads(resources, row["code"], model=model, default=default),
                "publication": "public",
            }
        )
    by_market = {m["code"]: m for m in market_entries or []}
    for market in markets:
        row = market.row
        info = by_market.get(row["code"], {})
        exchanges = []
        for e in market.exchanges[1:]:
            note = MARKET_NOTE.match(str(e.get("comment") or ""))
            title = note["title"] if note else e.get("atlas key", "")
            if str(e.get("atlas key", "")).startswith("supplier:"):
                title = f"Supplier {e['name']}, {title}"
            source = {"title": title, "provenance": note["status"] if note else "assumed", "source": note["source"] if note else e.get("comment", "")}
            exchanges.append(_exchange(e, source, db_name, codes))
        out.append(
            {
                "code": row["code"],
                "kind": "market",
                "process": None,
                "name": row["name"],
                "reference_product": row["reference product"],
                "unit": row["unit"],
                "location": row["location"],
                "chemical": row.get("chemical"),
                "grade": row.get("grade"),
                "cas": (products.chemicals.get(row.get("chemical") or "") or {}).get("cas"),
                "description": f"Market of {row['reference product']} in {row['location']} ({info.get('layer') or row.get('layer')}), {info.get('path', 'markets/')}.",
                "system_model": {"id": model, "label": model_label},
                "reference_exchange": {"key": None, "amount": 1, "unit": row["unit"]},
                "exchanges": exchanges,
                "market": {
                    k: info[k]
                    for k in ("layer", "technology", "region", "path", "gross", "suppliers", "facts", "not_exported", "consumption", "excluded", "status")
                    if k in info
                },
                "closure": {"status": "not-assessed", "reason": "a market (markets/): its losses are stated as fractions, not balanced"},
                "citation": {"text": f"{row['name']}, {row['location']}, ChemE-as-Code Process Atlas LCI database {version}, activity {row['code']}.", "authors": [], "doi": None},
                "downloads": _downloads(resources, row["code"], model=model, default=default),
                # set below: public when every supplier is
                "publication": None,
            }
        )
    # a market is public when every supplier is (a public build exports no other: build_markets)
    state = {e["code"]: e["publication"] for e in out}
    changed = True
    while changed:
        changed = False
        for entry in out:
            if entry["kind"] != "market" or entry["publication"] is not None:
                continue
            suppliers = [s["code"] for s in (entry["market"].get("suppliers") or [])]
            known = [state.get(c) for c in suppliers]
            if any(k == "preview" for k in known) or any(c not in state for c in suppliers):
                entry["publication"] = "preview"
            elif all(k == "public" for k in known):
                entry["publication"] = "public"
            else:
                continue
            state[entry["code"]] = entry["publication"]
            changed = True
    for entry in out:
        if entry["publication"] is None:  # a cycle of imports: not shown publicly
            entry["publication"] = "preview"
    used_by: dict[str, set[str]] = {}
    for entry in out:
        for exchange in entry["exchanges"]:
            # the plant behind a market (atlas_plant) is not linked by default: not a use
            for link in ("atlas", "atlas_alternative"):
                target = (exchange.get(link) or {}).get("code")
                if target:
                    used_by.setdefault(target, set()).add(entry["code"])
    for entry in out:
        entry["used_by"] = sorted(used_by.get(entry["code"], ()))
    return sorted(out, key=lambda e: e["code"])
