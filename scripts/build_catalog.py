# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6", "jsonschema>=4.23"]
# ///
"""Build the Process Atlas catalog from a process library.

A library holds one folder per process, ``processes/<id>/``, with a ``process.yaml`` (schema
``schemas/process.schema.json``) and, for a plantcode project, its engineering files beside it.
Chemicals are named once in ``chemicals/chemicals.yaml``.

The builder reads checked-in files only; it never imports or runs plantcode. Preview SVGs are
rendered beforehand by ``render_previews.py`` into an artifacts directory, which is optional.

Output (``--out``), all JSON with sorted keys, no timestamps, so two runs on the same commit are
byte-identical:

- ``catalog.json``: the list of processes (summaries), families (with their taxonomy title,
  group and ISIC Rev.4 / NACE Rev. 2 classes, ``taxonomy/families.yaml``), library commit
- ``processes/<id>.json``: one process in full; each flow names its chemical by slug and its
  ``grade`` (null when none: registry.py ``flow_grade``)
- ``chemicals.json``: the registry, each with the processes that make and use it, and so does
  each of its grades
- ``graph.json``: process and chemical nodes (by slug, never by grade), input/output edges
- ``coverage.json``: when the library has a ``coverage.yaml``, the coverage roadmap with each
  entry's covering processes and how many of the top entries are covered, at which tiers
- ``artifacts/<id>/<sheet>.svg``: preview drawings copied from ``--artifacts``
- ``scenarios/<id>/<scenario>.json``: core's per-scenario LCA records (``cheme assess
  lca-scenarios --write``), for Brightway jobs and other consumers

Summaries and details carry the manifest's ``facets`` (feedstock basis, product classes, unit
operations, region), always with every key: a missing list is ``[]``, a missing region null.

Errors (schema, unknown chemical or grade, a family outside the taxonomy, a registry check of
``registry.check``: CAS check digit, InChIKey, properties against the formula, duplicate
crosswalk names; folder/id mismatch, broken artifact link) exit 1. Warnings
(a preview not rendered, an inventory key the LCA does not have) are printed, and fail the build
with ``--strict``.

``catalog.json`` records the build's ``mode``: ``preview`` (the default: every process, as the
library has it) or ``public`` (``--public``, for publication; rules in ``publication.py``):

- only processes with ``publication.status: public``; the others are absent from every file;
- ``repository`` is dropped unless its ``access`` is ``public``, ``publication.exclude`` always;
- an LCA whose values may not be published (``publication.lca_withheld``: placeholder
  factors, no or a stale run manifest ``lca/manifest.json``, or a result core's policy marks not
  publishable, e.g. restricted sources such as a licensed database) keeps its goal, functional
  unit, boundary, allocation, categories, inventory, class and sources, but not its ``totals``
  and ``contributions`` (``values_withheld: <reason>``; the summary's headline ``value`` is
  null);
- an LCA's design cases and regional scenarios (core's ``lca/scenarios/<id>.json`` records)
  keep their geography, year, electricity, links and states in every build; a scenario whose
  values may not be published (the LCA withheld, the record stale, or its own policy not
  publishable) loses its ``totals`` (``values_withheld``), here and in its copied record
  ``scenarios/<id>/<scenario>.json``;
- an LCA's ``data_sources`` (from core's run manifest) stay in every build: the attribution its
  sources' licences ask for travels with the numbers;
- a viewer snapshot is copied only if its manifest's ``excluded`` covers the publication
  excludes (else an error), and for a withheld LCA without its ``lca`` answer and LCA result
  files.

    uv run build_catalog.py --library ../process-library --out dist [--artifacts build/previews] [--public]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

import registry as reg
from publication import LCA_RESULT_FILES, is_public, lca_withheld, snapshot_excludes

CATALOG_SCHEMA = "cheme-as-code/catalog/v1"
#: core's per-scenario LCA record (``cheme assess lca-scenarios``).
SCENARIO_SCHEMA = "cheme/lca-scenario/v1"
HERE = Path(__file__).resolve().parent
#: A preview larger than this is listed but not copied; the page offers the source instead.
MAX_PREVIEW_BYTES = 5_000_000
#: Markup that must never reach the site, even though previews are shown as <img>.
UNSAFE_SVG = re.compile(r"<script|<foreignObject|\son[a-z]+\s*=|(?:xlink:)?href\s*=\s*[\"'](?!#)", re.I)
SHEET_KINDS = ("bfd", "pfd", "pid")


def _schema_dir() -> Path:
    """schemas/ beside this script (library-kit) or one level up (process-library/scripts)."""
    for base in (HERE, HERE.parent):
        if (base / "schemas" / "process.schema.json").is_file():
            return base / "schemas"
    raise SystemExit("schemas/process.schema.json not found beside the builder")


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


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _number(text: str | None) -> float | None:
    try:
        return float(text) if text not in (None, "") else None
    except ValueError:
        return None


def _git(library: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(
            ["git", "-C", str(library), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.strip()


def _behind(library: Path, made_from: str | None, source_commit: str | None) -> bool:
    """Whether an artefact made from *made_from* misses the process's last change *source_commit*.

    Current when the change is contained in that commit (equal or an ancestor); a later commit
    elsewhere in the library does not make it stale.
    """
    if not made_from or not source_commit or made_from == source_commit:
        return False
    try:
        done = subprocess.run(
            ["git", "-C", str(library), "merge-base", "--is-ancestor", source_commit, made_from],
            capture_output=True,
        )
    except OSError:
        return True
    return done.returncode != 0


def _schema_errors(validator: Draft202012Validator, data: Any) -> list[str]:
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]


FACET_LISTS = ("feedstock_basis", "product_classes", "unit_operations")


def _facets(manifest: dict) -> dict:
    """The manifest's ``facets``, always complete: missing lists are [], a missing region None."""
    facets = manifest.get("facets") or {}
    return {**{key: list(facets.get(key, [])) for key in FACET_LISTS}, "region": facets.get("region")}


# --- plantcode project files ---------------------------------------------------------------


def _sheets(plant: dict) -> list[dict]:
    return [
        {"id": s["id"], "kind": s.get("kind", "pid"), "file": s["file"], "title": s.get("title", s["id"])}
        for s in plant.get("sheets", [])
    ]


#: What the catalog gives of each LCA data source (core's run manifest background.sources).
DATA_SOURCE_FIELDS = ("id", "title", "provider", "version", "url", "licence", "publication", "attribution")


def _lca(folder: Path, where: str, report: Report, capacity: str | None = None) -> dict | None:
    """Functional unit, totals per scenario and category, contributions and inventory."""
    lca_dir = folder / "lca"
    if not (lca_dir / "lca.yaml").is_file():
        return None
    study = _yaml(lca_dir / "lca.yaml") or {}
    factors = _yaml(lca_dir / "factors.yaml") if (lca_dir / "factors.yaml").is_file() else {}
    if not (lca_dir / "results.csv").is_file():
        report.warn(where, "lca/lca.yaml without lca/results.csv (run the LCA with --write)")
        return None
    results = _csv(lca_dir / "results.csv")
    inventory = _csv(lca_dir / "inventory.csv") if (lca_dir / "inventory.csv").is_file() else []

    fu = study.get("functional_unit", {})
    categories = {c["id"]: c for c in (factors or {}).get("categories", [])}
    # plantcode writes a "total" row per scenario and category; it is authoritative. The sum of
    # the contributions is only the fallback for a results file without one.
    sums: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    stated: dict[str, dict[str, float]] = defaultdict(dict)
    units: dict[str, str] = {}
    contributions = []
    statuses = set()
    for row in results:
        impact = _number(row.get("impact")) or 0.0
        units[row["category"]] = row.get("category_unit", "")
        if row["key"] == "total":
            stated[row["scenario"]][row["category"]] = impact
            continue
        sums[row["scenario"]][row["category"]] += impact
        statuses.add(row.get("status", ""))
        if row["scenario"] == "baseline":
            contributions.append(
                {
                    "key": row["key"],
                    "category": row["category"],
                    "basis": row.get("basis", ""),
                    "impact": impact,
                    "share": _number(row.get("share")),
                    "phase": row.get("phase", ""),
                    "status": row.get("status", ""),
                }
            )
    contributions.sort(key=lambda c: (c["category"], -abs(c["impact"]), c["key"]))
    totals = {s: {**sums.get(s, {}), **stated.get(s, {})} for s in sums.keys() | stated.keys()}

    run = {}
    sources: list[dict] = []
    if (lca_dir / "manifest.json").is_file():
        try:
            manifest_data = json.loads((lca_dir / "manifest.json").read_text(encoding="utf-8")) or {}
            run = manifest_data.get("result") or {}
            sources = (manifest_data.get("background") or {}).get("sources") or []
        except ValueError:
            report.warn(where, "lca/manifest.json does not parse: rewrite it with cheme assess lca --write")
    withheld = lca_withheld(folder)
    example = bool((factors or {}).get("example"))
    if example:
        factors_status = "placeholder"
    elif statuses <= {"PUBLISHED", "EPD"}:
        factors_status = "published"
    else:
        factors_status = "mixed"
    allocation = study.get("allocation") or {}
    scenario_part = _scenarios(folder, where, report, withheld, capacity)
    # a scenario record says which totals are computable: a category whose data the baseline
    # has is missing there (or all of whose contributions are gaps) has no total, never the
    # lower sum results.csv gives
    for scenario in scenario_part.get("scenarios", []):
        if scenario["id"] in totals:
            totals[scenario["id"]] = {
                cat: value for cat, value in totals[scenario["id"]].items() if scenario["totals"].get(cat) is not None
            }
    return {
        "goal": study.get("goal", ""),
        "functional_unit": {
            "product": fu.get("product"),
            "amount": fu.get("amount"),
            "unit": fu.get("unit"),
            "label": f"{fu.get('amount', '')} {fu.get('unit', '')} {fu.get('product', '')}".strip(),
        },
        "boundary": study.get("boundary", ""),
        "allocation": allocation.get("method"),
        "backend": study.get("backend", "factors"),
        "factors_status": factors_status,
        # core's classification (complete, screening, partial, unavailable) and policy
        "result": {
            "classification": run.get("classification"),
            "label": run.get("label"),
            "gaps": run.get("gaps"),
            "publication": run.get("publication"),
        },
        "publishable": withheld is None,
        "withheld_reason": withheld,
        # the background data the numbers rest on, with what their licences ask a user of the
        # numbers to show (OGL-3.0, CC BY: the attribution), from core's run manifest
        "data_sources": [
            {key: s.get(key, "") for key in DATA_SOURCE_FIELDS} for s in sources
        ],
        "categories": [
            {
                "id": cid,
                "title": categories.get(cid, {}).get("title", cid),
                "unit": units[cid] or categories.get(cid, {}).get("unit", ""),
                "method": categories.get(cid, {}).get("method", ""),
            }
            for cid in sorted(units)
        ],
        "totals": {
            scenario: {cat: round(value, 6) for cat, value in sorted(cats.items())}
            for scenario, cats in sorted(totals.items())
        },
        "contributions": contributions,
        "inventory": [
            {
                "key": r["key"],
                "title": r.get("title", ""),
                "phase": r.get("phase", ""),
                "direction": r.get("direction", ""),
                "kind": r.get("kind", ""),
                "quantity": _number(r.get("quantity")),
                "unit": r.get("unit", ""),
                "provenance": r.get("provenance", ""),
            }
            for r in inventory
        ],
        "sources": sorted(
            str(p.relative_to(folder)) for p in lca_dir.glob("*") if p.suffix in {".yaml", ".csv", ".md"}
        ),
        **scenario_part,
    }


#: What the catalog keeps of each exchange's link in a scenario record (core's linked inventory).
LINK_FIELDS = (
    "key", "title", "phase", "amount", "unit", "state", "background", "baseline", "replaced",
    "location", "year", "status", "source_id", "note",
)


def _record_stale(folder: Path, record: dict) -> bool:
    """Whether a scenario record's input file fingerprints no longer match the files. The
    mapping, background profiles and software are checked by core (``cheme assess
    lca-scenarios --check`` in CI), not here."""
    import hashlib

    for rel, sha in ((record.get("inputs") or {}).get("files") or {}).items():
        target = folder / rel
        if not target.is_file():
            return True
        content = target.read_bytes().replace(b"\r\n", b"\n")
        if "sha256:" + hashlib.sha256(content).hexdigest() != sha:
            return True
    return False


def _scenarios(folder: Path, where: str, report: Report, lca_withheld_reason: str | None, capacity: str | None = None) -> dict:
    """The design cases and regional background scenarios of core's records
    (``lca/scenarios/<id>.json``, ``cheme assess lca-scenarios --write``, schema
    :data:`SCENARIO_SCHEMA`): one entry per scenario, the baseline first, each with its design
    case, geography, year, electricity, foreground relation, linked exchanges (state: linked,
    proxy, missing, ...), characterised totals per functional unit with the allocation, and
    whether its values may be published (``withheld_reason``). No record: no scenarios."""
    records = []
    for path in sorted((folder / "lca" / "scenarios").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            report.warn(where, f"{path.relative_to(folder)} does not parse: rewrite it with cheme assess lca-scenarios --write")
            continue
        if data.get("schema") != SCENARIO_SCHEMA:
            report.warn(where, f"{path.relative_to(folder)}: schema {data.get('schema')!r}, expected {SCENARIO_SCHEMA}")
            continue
        missing = [k for k in ("id", "scenario", "design_case", "foreground", "linked_inventory", "impacts") if not isinstance(data.get(k), (dict, str))]
        if missing:
            report.warn(where, f"{path.relative_to(folder)}: not a complete scenario record (no {', '.join(missing)}); skipped")
            continue
        records.append((path, data))
    if not records:
        return {}
    records.sort(key=lambda r: (r[1]["scenario"]["kind"] != "baseline", r[1]["scenario"]["id"]))
    cases: dict[str, dict] = {}
    scenarios = []
    for path, data in records:
        case = data["design_case"]
        foreground = data["foreground"]
        known = cases.setdefault(
            case["id"],
            {
                **case,
                "foreground": {
                    "layer": foreground["layer"],
                    "basis": foreground["basis"],
                    "boundary": foreground.get("boundary", ""),
                    "fingerprint": foreground["fingerprint"],
                    "exchanges": foreground["exchanges"],
                },
            },
        )
        if known["foreground"]["fingerprint"] != foreground["fingerprint"]:
            report.warn(where, f"{path.relative_to(folder)}: case {case['id']} has another foreground than the other records (rewrite them together)")
        stale = _record_stale(folder, data)
        if stale:
            report.warn(where, f"{path.relative_to(folder)} is stale: its inputs changed (cheme assess lca-scenarios --write)")
        publication = data.get("publication") or {}
        withheld = (
            lca_withheld_reason
            or ("stale-scenario-record" if stale else None)
            or (None if publication.get("publishable") else f"{publication.get('policy') or 'unknown'}-sources")
        )
        impacts = data["impacts"]
        scenario = data["scenario"]
        scenarios.append(
            {
                "id": scenario["id"],
                "record_id": data["id"],
                "kind": scenario["kind"],
                "title": scenario.get("title"),
                "location": scenario.get("location"),
                "year": scenario.get("year"),
                "electricity": scenario.get("electricity"),
                "source": scenario.get("source"),
                "design_case": case["id"],
                "relation": foreground["relation"],
                "foreground_fingerprint": foreground["fingerprint"],
                "layers": {
                    "foreground": foreground["layer"],
                    "linked_inventory": data["linked_inventory"]["layer"],
                    "impacts": impacts["layer"],
                },
                "functional_unit": impacts["functional_unit"],
                "allocation": impacts["allocation"],
                "categories": impacts["categories"],
                "totals": impacts["totals"],
                "partial_categories": impacts.get("partial_categories", []),
                "comparable": impacts.get("comparable", True),
                "dropped": impacts.get("dropped", []),
                "classification": impacts["classification"],
                "reasons": impacts["reasons"],
                "links": [{k: link.get(k) for k in LINK_FIELDS} for link in data["linked_inventory"]["exchanges"]],
                "gaps": len({(g["key"], g["category"]) for g in data.get("gaps", [])}),
                "notes": data.get("notes", []),
                "warnings": [w["message"] for w in data.get("warnings", []) if w.get("level") != "info"],
                "publication": publication,
                "stale": stale,
                "withheld_reason": withheld,
                "record": f"scenarios/{folder.name}/{path.name}",
            }
        )
    # one design case without a declared capacity: the manifest's documented capacity, with its
    # source (it describes that one design, never another case)
    if len(cases) == 1 and capacity:
        (only,) = cases.values()
        if not only.get("capacity"):
            only["capacity"] = capacity
            only["capacity_source"] = "process.yaml basis.capacity"
    # the technology/configuration every case and scenario shares
    technology = records[0][1].get("process", {}).get("technology")
    return {"technology": technology, "design_cases": list(cases.values()), "scenarios": scenarios}


def _gates(folder: Path) -> dict | None:
    path = folder / "checks" / "status.json"
    if not path.is_file():
        return None
    checks = json.loads(path.read_text(encoding="utf-8")).get("checks", [])
    counts: dict[str, int] = defaultdict(int)
    for check in checks:
        counts[check.get("status", "unknown")] += 1
    return {
        "total": len(checks),
        "counts": dict(sorted(counts.items())),
        "checks": [{"id": c["id"], "title": c.get("title", ""), "stage": c.get("stage", ""), "status": c.get("status", "")} for c in checks],
    }


def _design_basis(folder: Path) -> dict | None:
    path = folder / "process" / "design-basis.yaml"
    if not path.is_file():
        return None
    basis = _yaml(path) or {}
    return {
        "assumptions": [str(a) for a in basis.get("assumptions", [])],
        "source": "process/design-basis.yaml",
    }


def _representations(folder: Path, pid: str, plant: dict | None, artifacts: Path | None, out: Path, where: str, report: Report) -> list[dict]:
    """Every representation the process has, with its preview state."""
    reps: list[dict] = []
    if plant is None:
        return reps
    for sheet in _sheets(plant):
        rep = {"kind": sheet["kind"], "id": sheet["id"], "title": sheet["title"], "source": sheet["file"]}
        if not (folder / sheet["file"]).is_file():
            report.error(where, f"plant.yaml lists {sheet['file']}, which does not exist")
            rep["status"] = "missing-source"
            reps.append(rep)
            continue
        svg = artifacts / pid / f"{sheet['id']}.svg" if artifacts else None
        if svg is None or not svg.is_file():
            report.warn(where, f"no preview rendered for {sheet['id']}")
            rep["status"] = "not-generated"
        elif svg.stat().st_size > MAX_PREVIEW_BYTES:
            rep["status"] = "too-large"
            rep["bytes"] = svg.stat().st_size
        elif UNSAFE_SVG.search(svg.read_text(encoding="utf-8", errors="replace")):
            report.error(where, f"preview {svg.name} contains scripts or external references")
            rep["status"] = "rejected"
        else:
            target = out / "artifacts" / pid / svg.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(svg, target)
            rep["status"] = "preview"
            rep["preview"] = f"artifacts/{pid}/{svg.name}"
            rep["bytes"] = svg.stat().st_size
        reps.append(rep)
    extras = [
        ("process-model", "process/flowsheet.yaml", "Flowsheet and stream table"),
        ("simulation", "process/simulation.yaml", "Process simulation"),
        ("layout-3d", "layout/plant-model.yaml", "3D plant layout"),
        ("equipment-list", "equipment/equipment-list.yaml", "Equipment list"),
        ("estimate", "estimate/estimate.md", "Cost estimate"),
        ("lca", "lca/lca.yaml", "Life cycle assessment"),
    ]
    for kind, source, title in extras:
        if (folder / source).is_file():
            reps.append({"kind": kind, "id": kind, "title": title, "source": source, "status": "viewer"})
    kind_order = {k: i for i, k in enumerate((*SHEET_KINDS, *(e[0] for e in extras)))}
    reps.sort(key=lambda r: (kind_order.get(r["kind"], 99), r["id"]))
    return reps


def _render_info(artifacts: Path | None, pid: str) -> dict | None:
    path = artifacts / pid / "render.json" if artifacts else None
    return json.loads(path.read_text(encoding="utf-8")) if path and path.is_file() else None


SNAPSHOT_SCHEMA = "cheme/viewer-snapshot/v1"


def _withhold_lca_values(manifest: dict, target: Path) -> None:
    """Drop the snapshot's ``lca`` answer and LCA result files (footprint values) in *target*."""
    from fnmatch import fnmatchcase

    def result_file(key: str) -> bool:
        endpoint, _, path = key.partition("?path=")
        return endpoint in ("file", "yaml") and any(fnmatchcase(path, glob.replace("**", "*")) for glob in LCA_RESULT_FILES)

    entries = manifest.get("entries", {})
    for key in sorted(k for k in entries if k == "lca" or result_file(k)):
        (target / "data" / entries.pop(key)["file"]).unlink(missing_ok=True)
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _viewer(
    snapshots: Path | None, pid: str, out: Path, where: str, report: Report, publish: dict | None = None
) -> dict | None:
    """The process's viewer snapshot (``cheme export-static``), copied into the output.

    *publish* (public builds) holds the process manifest and whether its LCA values are
    withheld: the snapshot must have been exported without the publication excludes.
    """
    source = snapshots / pid if snapshots else None
    if source is None or not (source / "manifest.json").is_file():
        return None
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SNAPSHOT_SCHEMA:
        report.error(where, f"viewer snapshot has schema {manifest.get('schema')!r}, expected {SNAPSHOT_SCHEMA}")
        return None
    if publish is not None:
        missing = sorted(set(snapshot_excludes(publish["manifest"])) - set(manifest.get("excluded") or []))
        if missing:
            report.error(where, f"snapshot was not exported for publication (excluded lacks {', '.join(missing)}; run export_snapshots.py --public)")
            return None
    target = out / "snapshots" / pid
    shutil.copytree(source, target)
    if publish is not None and publish["withhold"]:
        _withhold_lca_values(manifest, target)
    entries = manifest.get("entries", {})
    ok = {key for key, entry in entries.items() if entry.get("status") == 200}
    return {
        "snapshot": f"snapshots/{pid}/",
        "commit": manifest["source"].get("commit"),
        "dirty": manifest["source"].get("dirty"),
        "tool": manifest["source"].get("tool"),
        "skipped": [s["path"] for s in manifest.get("skipped", [])],
        "sheets": sorted(key.split("path=", 1)[1] for key in ok if key.startswith("pid.svg?path=")),
        "views": sorted(
            view for view, key in (("streams", "streams"), ("layout", "layout"), ("lca", "lca"), ("mto", "mto"), ("checks", "checks"))
            if key in ok
        ),
    }


# --- build ---------------------------------------------------------------------------------


def build(
    library: Path,
    out: Path,
    artifacts: Path | None,
    commit: str | None,
    snapshots: Path | None = None,
    public: bool = False,
) -> Report:
    report = Report()
    schemas = _schema_dir()
    process_validator = Draft202012Validator(json.loads((schemas / "process.schema.json").read_text()))
    chem_validator = Draft202012Validator(json.loads((schemas / "chemicals.schema.json").read_text()))

    registry_path = library / "chemicals" / "chemicals.yaml"
    if not registry_path.is_file():
        report.error(str(registry_path), "missing chemical registry")
        return report
    registry = _yaml(registry_path)
    registry_problems = _schema_errors(chem_validator, registry)
    for message in registry_problems:
        report.error("chemicals/chemicals.yaml", message)
    chemicals = {c["slug"]: c for c in registry.get("chemicals", [])}
    if len(chemicals) != len(registry.get("chemicals", [])):
        report.error("chemicals/chemicals.yaml", "duplicate slug")
    # the checks beyond the schema need a registry the schema accepts
    products = reg.load(registry) if not registry_problems else reg.Registry(chemicals)
    for message in reg.check(products) if not registry_problems else []:
        report.error("chemicals/chemicals.yaml", message)
    families_path = library / "taxonomy" / "families.yaml"
    taxonomy = reg.load_families(families_path if families_path.is_file() else _schema_dir().parent / "taxonomy" / "families.yaml")

    # Git facts only when the library is a checkout of its own, not a folder inside another repo
    # (a test fixture, the interim assembled library).
    own_repo = _git(library, "rev-parse", "--show-toplevel") == str(library)
    if commit is None and own_repo:
        commit = _git(library, "rev-parse", "HEAD")
    dirty = bool(_git(library, "status", "--porcelain")) if own_repo else None

    if out.exists():
        shutil.rmtree(out)
    (out / "processes").mkdir(parents=True)

    summaries, details = [], []
    for manifest_path in sorted((library / "processes").glob("*/process.yaml")):
        folder = manifest_path.parent
        where = str(manifest_path.relative_to(library))
        manifest = _yaml(manifest_path) or {}
        problems = _schema_errors(process_validator, manifest)
        for message in problems:
            report.error(where, message)
        if problems:
            continue
        pid = manifest["id"]
        if pid != folder.name:
            report.error(where, f"id {pid!r} differs from folder name {folder.name!r}")
            continue
        flows = {k: manifest["chemistry"].get(k, []) for k in ("inputs", "outputs", "utilities")}
        facets = _facets(manifest)
        for group, items in flows.items():
            for number, item in enumerate(items):
                slug, grade, problem = reg.flow_grade(products, pid, item)
                if slug not in chemicals:
                    report.error(where, f"chemistry.{group}: unknown chemical {slug!r} (add it to chemicals/chemicals.yaml)")
                elif problem:
                    report.error(where, f"chemistry.{group}: {problem}")
                # the graph joins by slug; the grade travels beside it
                items[number] = {**item, "chemical": slug, "grade": grade}
        for family in manifest["families"]:
            if taxonomy and family not in taxonomy:
                report.error(where, f"family {family!r} is not in taxonomy/families.yaml")
        if public and not is_public(manifest):
            continue

        plant = _yaml(folder / "plant.yaml") if (folder / "plant.yaml").is_file() else None
        capacity = (manifest.get("basis") or {}).get("capacity")
        lca = _lca(folder, where, report, capacity) if manifest.get("lca", {}).get("source", "auto") == "auto" and plant else None
        if lca:
            keys = {row["key"] for row in lca["inventory"]}
            for group, items in flows.items():
                for item in items:
                    key = item.get("inventory_key")
                    if key and keys and key not in keys:
                        report.warn(where, f"chemistry.{group}: inventory_key {key!r} is not in lca/inventory.csv")
        reps = _representations(folder, pid, plant, artifacts, out, where, report)
        source_commit = _git(library, "log", "-1", "--format=%H", "--", str(folder.relative_to(library))) if own_repo else None
        render = _render_info(artifacts, pid)
        stale = bool(render) and _behind(library, render.get("source_commit"), source_commit)
        withhold = bool(lca) and not lca["publishable"]
        publish = {"manifest": manifest, "withhold": withhold} if public else None
        viewer = _viewer(snapshots, pid, out, where, report, publish) if plant else None
        if viewer:
            viewer["stale"] = _behind(library, viewer["commit"], source_commit)

        detail = {
            "id": pid,
            "title": manifest["title"],
            "summary": manifest["summary"],
            "description": manifest.get("description", ""),
            "families": manifest["families"],
            "keywords": manifest.get("keywords", []),
            "facets": facets,
            "maturity": manifest["maturity"],
            "validation": manifest["validation"],
            "chemistry": flows,
            "basis": manifest.get("basis"),
            "authors": manifest.get("authors", []),
            "maintainers": manifest.get("maintainers", []),
            "references": manifest.get("references", []),
            "repository": manifest.get("repository"),
            "publication": manifest.get("publication"),
            "engineering": None
            if plant is None
            else {
                "tool": "plantcode",
                "name": plant.get("name", ""),
                "description": plant.get("description", ""),
                "stage": plant.get("stage"),
                "stages": plant.get("stages", []),
                "requires": plant.get("requires"),
            },
            "representations": reps,
            "viewer": viewer,
            "design_basis": _design_basis(folder) if plant else None,
            "gates": _gates(folder) if plant else None,
            "lca": lca,
            "provenance": {
                "library_commit": commit,
                "source_commit": source_commit,
                "previews": render,
                "previews_stale": stale,
            },
        }
        if public:
            _publish(detail)
        for scenario in (lca or {}).get("scenarios", []):
            _copy_record(folder, scenario, out, public)
        details.append(detail)
        baseline = (lca or {}).get("totals", {}).get("baseline", {})
        headline = None
        if lca and lca["categories"]:
            first = lca["categories"][0]
            headline = {
                "category": first["id"],
                "title": first["title"],
                "value": baseline.get(first["id"]),
                "unit": first["unit"],
                "functional_unit": lca["functional_unit"]["label"],
                "factors_status": lca["factors_status"],
            }
            if "values_withheld" in lca:
                headline["values_withheld"] = lca["values_withheld"]
        summaries.append(
            {
                "id": pid,
                "title": manifest["title"],
                "summary": manifest["summary"],
                "families": manifest["families"],
                "keywords": manifest.get("keywords", []),
                "facets": facets,
                "maturity": manifest["maturity"],
                "validation": manifest["validation"]["status"],
                "inputs": sorted({f["chemical"] for f in flows["inputs"]}),
                "outputs": sorted({f["chemical"] for f in flows["outputs"] if f["role"] not in ("emission", "waste")}),
                "utilities": sorted({f["chemical"] for f in flows["utilities"]}),
                "representations": sorted({r["kind"] for r in reps if r.get("status") != "missing-source"}),
                "engineering_project": plant is not None,
                "interactive": viewer is not None,
                "lca": headline,
            }
        )

    # chemicals with their producers and consumers; graph
    uses: dict[str, dict[str, list]] = {slug: {"produced_by": [], "consumed_by": []} for slug in chemicals}
    grade_uses: dict[tuple[str, str], dict[str, set]] = {key: {"produced_by": set(), "consumed_by": set()} for key in products.grades}
    nodes, edges = [], set()
    for d in details:
        nodes.append({"id": f"process:{d['id']}", "type": "process", "label": d["title"], "maturity": d["maturity"], "families": d["families"]})
        for group, items in d["chemistry"].items():
            for item in items:
                slug = item["chemical"]
                if slug not in uses:
                    continue
                outgoing = group == "outputs"
                uses[slug]["produced_by" if outgoing else "consumed_by"].append({"process": d["id"], "role": item["role"]})
                if (slug, item["grade"]) in grade_uses:
                    grade_uses[(slug, item["grade"])]["produced_by" if outgoing else "consumed_by"].add((d["id"], item["role"]))
                edge = (f"process:{d['id']}", f"chemical:{slug}") if outgoing else (f"chemical:{slug}", f"process:{d['id']}")
                edges.add((*edge, item["role"]))
    used = {slug for slug, u in uses.items() if u["produced_by"] or u["consumed_by"]}
    for slug in sorted(used):
        nodes.append({"id": f"chemical:{slug}", "type": "chemical", "label": chemicals[slug]["name"], "kind": chemicals[slug]["kind"]})
    chemical_list = [
        {
            **chemicals[slug],
            "produced_by": sorted({(u["process"], u["role"]) for u in uses[slug]["produced_by"]}),
            "consumed_by": sorted({(u["process"], u["role"]) for u in uses[slug]["consumed_by"]}),
        }
        for slug in sorted(chemicals)
    ]
    for chem in chemical_list:
        for key in ("produced_by", "consumed_by"):
            chem[key] = [{"process": p, "role": r} for p, r in chem[key]]
        if chem.get("grades"):
            chem["grades"] = [
                {**g, **{key: [{"process": p, "role": r} for p, r in sorted(grade_uses[(chem["slug"], g["slug"])][key])] for key in ("produced_by", "consumed_by")}}
                for g in chem["grades"]
            ]

    families: dict[str, int] = defaultdict(int)
    for s in summaries:
        for fam in s["families"]:
            families[fam] += 1

    library_info = {"commit": commit, "dirty": dirty}
    _write(out / "catalog.json", {
        "schema": CATALOG_SCHEMA,
        "mode": "public" if public else "preview",
        "library": library_info,
        "processes": summaries,
        "families": [_family(f, n, taxonomy) for f, n in sorted(families.items())],
        "chemical_count": len(used),
    })
    for d in details:
        _write(out / "processes" / f"{d['id']}.json", d)
    if (library / "coverage.yaml").is_file():
        _write(out / "coverage.json", _coverage(library / "coverage.yaml", details, taxonomy, chemicals, report))
    _write(out / "chemicals.json", {"schema": CATALOG_SCHEMA, "library": library_info, "chemicals": chemical_list})
    _write(out / "graph.json", {
        "schema": CATALOG_SCHEMA,
        "library": library_info,
        "nodes": nodes,
        "edges": [{"source": s, "target": t, "role": r} for s, t, r in sorted(edges)],
    })

    # every link in the output must resolve
    for d in details:
        for rep in d["representations"]:
            if rep.get("preview") and not (out / rep["preview"]).is_file():
                report.error(d["id"], f"broken preview link {rep['preview']}")
        if d["viewer"] and not (out / d["viewer"]["snapshot"] / "manifest.json").is_file():
            report.error(d["id"], f"broken snapshot link {d['viewer']['snapshot']}")
    return report


def _family(slug: str, count: int, taxonomy: dict[str, dict]) -> dict:
    """A family of catalog.json: its slug and process count, with the taxonomy's title, group and
    ISIC Rev.4 / NACE Rev. 2 classes (null when the library has no taxonomy)."""
    entry = taxonomy.get(slug) or {}
    return {"slug": slug, "count": count, "title": entry.get("title"), "group": entry.get("group"), "isic": entry.get("isic", []), "nace": entry.get("nace", [])}


def _coverage(path: Path, details: list[dict], taxonomy: dict[str, dict], chemicals: dict[str, dict], report: Report) -> dict:
    """``coverage.json``: the roadmap of ``coverage.yaml`` (schema ``schemas/coverage.schema.json``)
    with each entry's covering processes of this build and a summary: how many of the top
    ``summary_top`` entries are covered, at which tiers. An entry's ``covered_by`` names a process
    and the tier it reaches; a process left out of this build (``--public``) does not count."""
    where = path.name
    data = _yaml(path) or {}
    validator = Draft202012Validator(json.loads((_schema_dir() / "coverage.schema.json").read_text()))
    problems = _schema_errors(validator, data)
    for message in problems:
        report.error(where, message)
    if problems:
        return {"schema": CATALOG_SCHEMA, "entries": [], "summary": None}
    built = {d["id"]: d for d in details}
    entries, ids = [], set()
    for entry in sorted(data["entries"], key=lambda e: e["rank"]):
        at = f"{where} {entry['id']}"
        if entry["id"] in ids:
            report.error(at, "id appears twice")
        ids.add(entry["id"])
        if taxonomy and entry["family"] not in taxonomy:
            report.error(at, f"family {entry['family']!r} is not in taxonomy/families.yaml")
        cited = [entry["volume"].get("source"), *entry.get("open_sources", [])]
        for source in sorted({s for s in cited if s and s not in data.get("sources", {})}):
            report.error(at, f"cites unknown source {source!r} (add it to sources:)")
        covered = []
        for cover in entry.get("covered_by", []):
            process = built.get(cover["process"])
            if not (path.parent / "processes" / cover["process"] / "process.yaml").is_file():
                report.error(at, f"covered_by unknown process {cover['process']!r}")
            if process is None:
                continue
            made = {f["chemical"] for f in process["chemistry"]["outputs"] if f["role"] in ("main-product", "co-product")}
            if entry.get("chemical") in chemicals and entry["chemical"] not in made:
                report.warn(at, f"covered_by {cover['process']}, which does not make {entry['chemical']}")
            covered.append(cover)
        entries.append({**entry, "covered_by": covered})
    for entry in entries:
        for link in entry.get("feeds", []):
            if link not in ids:
                report.error(f"{where} {entry['id']}", f"feeds unknown entry {link!r}")
    top = data.get("summary_top", 50)
    ranked = entries[:top]
    tiers: dict[str, int] = defaultdict(int)
    for entry in ranked:
        if entry["covered_by"]:
            tiers[str(max(c["tier"] for c in entry["covered_by"]))] += 1
    return {
        "schema": CATALOG_SCHEMA,
        "criteria": data.get("criteria", []),
        "entries": entries,
        "summary": {"top": len(ranked), "covered": sum(1 for e in ranked if e["covered_by"]), "by_tier": dict(sorted(tiers.items()))},
    }


def _publish(detail: dict) -> None:
    """Apply the public build's rules to one process's *detail* in place (module docstring)."""
    repository = detail.get("repository")
    if repository and repository.get("access") != "public":
        detail["repository"] = None
    if detail.get("publication"):
        detail["publication"] = {k: v for k, v in detail["publication"].items() if k != "exclude"}
    lca = detail.get("lca")
    if lca and not lca["publishable"]:
        del lca["totals"], lca["contributions"]
        lca["values_withheld"] = lca["withheld_reason"]
    for scenario in (lca or {}).get("scenarios", []):
        if scenario["withheld_reason"]:
            del scenario["totals"]
            scenario["values_withheld"] = scenario["withheld_reason"]
            # the same scenario's sum from results.csv, when the LCA itself is not withheld
            (lca.get("totals") or {}).pop(scenario["id"], None)


def _copy_record(folder: Path, scenario: dict, out: Path, public: bool) -> None:
    """Core's full scenario record, for Brightway jobs and other consumers, at
    ``scenarios/<process>/<scenario>.json``; in a public build without its impact numbers
    when they may not be published (geography, states and gaps hold none)."""
    data = json.loads((folder / "lca" / "scenarios" / Path(scenario["record"]).name).read_text(encoding="utf-8"))
    if public and scenario["withheld_reason"]:
        # no impact number of any kind: the totals and the sum of what was characterised
        for key in ("totals", "characterised_sum"):
            data["impacts"].pop(key, None)
        data["impacts"]["values_withheld"] = scenario["withheld_reason"]
    _write(out / scenario["record"], data)


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, required=True, help="library root (holds processes/ and chemicals/)")
    parser.add_argument("--out", type=Path, required=True, help="output directory (replaced)")
    parser.add_argument("--artifacts", type=Path, help="pre-rendered previews: <dir>/<id>/<sheet>.svg")
    parser.add_argument("--snapshots", type=Path, help="viewer snapshots (cheme export-static): <dir>/<id>/manifest.json")
    parser.add_argument("--commit", help="library commit to record (default: git HEAD of --library)")
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--public", action="store_true", help="build for publication: published processes only, footprints the LCA's publication policy does not permit withheld")
    args = parser.parse_args(argv)

    report = build(
        args.library.resolve(),
        args.out.resolve(),
        args.artifacts.resolve() if args.artifacts else None,
        args.commit,
        args.snapshots.resolve() if args.snapshots else None,
        args.public,
    )
    for message in report.warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in report.errors:
        print(f"error: {message}", file=sys.stderr)
    failed = bool(report.errors or (args.strict and report.warnings))
    if not failed:
        count = len(json.loads((args.out / "catalog.json").read_text())["processes"])
        print(f"catalog: {count} process(es) -> {args.out}{' (public)' if args.public else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
