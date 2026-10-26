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
- ``closure``: the dataset's mass, element and energy balance as ``lca/manifest.json`` records
  it (``balance``, core#174), or ``status: not-assessed`` with the reason;
- ``citation`` (DOI null until a release is deposited, docs/governance.md) and ``downloads``:
  the database files of this build that hold the activity, with the code to select it;
- ``publication``: ``public`` or ``preview`` (``publication.py``). A ``--public`` build holds
  public processes only, so every entry of it is ``public``.

Dataset-level facts the page also shows (review, data quality, data status, benchmarks,
property checks, cut-off exclusions) stay where they are, in ``processes[].datasets[]``; an entry
names its dataset by ``process`` and ``dataset.id``. No entry carries an impact value: the LCI has
no characterisation factors, so placeholder factors cannot leak through it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    return {"status": "assessed", "source": CLOSURE_SOURCE, **balance}


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
        out["atlas"] = {"code": codes.get(_identity(entry)), "name": entry["name"], "reference_product": entry["reference product"], "location": entry["location"]}
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
            out["atlas_alternative"] = {"code": codes.get(_identity(alternative)), "name": entry["atlas activity"], "reference_product": entry["atlas reference product"], "location": entry["atlas location"]}
    return out


def entries(activities: list, proxies: list, processes: list, products: Any, families: dict[str, dict], db_name: str, model: str, model_label: str, resources: list[dict], library: Path, version: str, site_location: str) -> list[dict]:
    """The ``activities`` of ``datapackage.json``, sorted by code (see the module docstring)."""
    codes = {_identity(a.exchanges[0]): a.row["code"] for a in [*activities, *proxies]}
    datasets = {(p.pid, d.data["id"]): (p, d) for p in processes for d in p.datasets}
    files = [{"path": r["path"], "format": _format(r["path"], r.get("mediatype")), "mediatype": r.get("mediatype"), "select": "code"} for r in resources]
    out: list[dict] = []
    for activity in activities:
        meta, row = activity.metadata, activity.row
        process, dataset = datasets[(meta["atlas process"], meta["atlas dataset"])]
        by_key = {e["key"]: e for e in dataset.data["exchanges"]}
        doc = dataset.data
        product = products.chemicals.get(row.get("chemical") or "") or {}
        share = dataset.shares.get(row["key"])
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
                "downloads": files,
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
                "downloads": files,
                "publication": "public",
            }
        )
    used_by: dict[str, set[str]] = {}
    for entry in out:
        for exchange in entry["exchanges"]:
            target = (exchange.get("atlas") or exchange.get("atlas_alternative") or {}).get("code")
            if target:
                used_by.setdefault(target, set()).add(entry["code"])
    for entry in out:
        entry["used_by"] = sorted(used_by.get(entry["code"], ()))
    return sorted(out, key=lambda e: e["code"])
