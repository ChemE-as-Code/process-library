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

- ``catalog.json``: the list of processes (summaries), families, library commit
- ``processes/<id>.json``: one process in full
- ``chemicals.json``: the registry, each with the processes that make and use it
- ``graph.json``: process and chemical nodes, input/output edges
- ``artifacts/<id>/<sheet>.svg``: preview drawings copied from ``--artifacts``

Errors (schema, unknown chemical, folder/id mismatch, broken artifact link) exit 1. Warnings
(a preview not rendered, an inventory key the LCA does not have) are printed, and fail the build
with ``--strict``.

    uv run build_catalog.py --library ../process-library --out dist [--artifacts build/previews]
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

CATALOG_SCHEMA = "cheme-as-code/catalog/v1"
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


def _schema_errors(validator: Draft202012Validator, data: Any) -> list[str]:
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]


# --- plantcode project files ---------------------------------------------------------------


def _sheets(plant: dict) -> list[dict]:
    return [
        {"id": s["id"], "kind": s.get("kind", "pid"), "file": s["file"], "title": s.get("title", s["id"])}
        for s in plant.get("sheets", [])
    ]


def _lca(folder: Path, where: str, report: Report) -> dict | None:
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

    example = bool((factors or {}).get("example"))
    if example:
        factors_status = "placeholder"
    elif statuses <= {"PUBLISHED", "EPD"}:
        factors_status = "published"
    else:
        factors_status = "mixed"
    allocation = study.get("allocation") or {}
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
    }


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


def _viewer(snapshots: Path | None, pid: str, out: Path, where: str, report: Report) -> dict | None:
    """The process's viewer snapshot (``cheme export-static``), copied into the output."""
    source = snapshots / pid if snapshots else None
    if source is None or not (source / "manifest.json").is_file():
        return None
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SNAPSHOT_SCHEMA:
        report.error(where, f"viewer snapshot has schema {manifest.get('schema')!r}, expected {SNAPSHOT_SCHEMA}")
        return None
    target = out / "snapshots" / pid
    shutil.copytree(source, target)
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
    library: Path, out: Path, artifacts: Path | None, commit: str | None, snapshots: Path | None = None
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
    for message in _schema_errors(chem_validator, registry):
        report.error("chemicals/chemicals.yaml", message)
    chemicals = {c["slug"]: c for c in registry.get("chemicals", [])}
    if len(chemicals) != len(registry.get("chemicals", [])):
        report.error("chemicals/chemicals.yaml", "duplicate slug")

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
        for group, items in flows.items():
            for item in items:
                if item["chemical"] not in chemicals:
                    report.error(where, f"chemistry.{group}: unknown chemical {item['chemical']!r} (add it to chemicals/chemicals.yaml)")

        plant = _yaml(folder / "plant.yaml") if (folder / "plant.yaml").is_file() else None
        lca = _lca(folder, where, report) if manifest.get("lca", {}).get("source", "auto") == "auto" and plant else None
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
        stale = bool(render and source_commit and render.get("source_commit") not in (None, source_commit))
        viewer = _viewer(snapshots, pid, out, where, report) if plant else None
        if viewer:
            viewer["stale"] = bool(source_commit and viewer["commit"] not in (None, source_commit))

        detail = {
            "id": pid,
            "title": manifest["title"],
            "summary": manifest["summary"],
            "description": manifest.get("description", ""),
            "families": manifest["families"],
            "keywords": manifest.get("keywords", []),
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
        summaries.append(
            {
                "id": pid,
                "title": manifest["title"],
                "summary": manifest["summary"],
                "families": manifest["families"],
                "keywords": manifest.get("keywords", []),
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

    families: dict[str, int] = defaultdict(int)
    for s in summaries:
        for fam in s["families"]:
            families[fam] += 1

    library_info = {"commit": commit, "dirty": dirty}
    _write(out / "catalog.json", {
        "schema": CATALOG_SCHEMA,
        "library": library_info,
        "processes": summaries,
        "families": [{"slug": f, "count": n} for f, n in sorted(families.items())],
        "chemical_count": len(used),
    })
    for d in details:
        _write(out / "processes" / f"{d['id']}.json", d)
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
    args = parser.parse_args(argv)

    report = build(
        args.library.resolve(),
        args.out.resolve(),
        args.artifacts.resolve() if args.artifacts else None,
        args.commit,
        args.snapshots.resolve() if args.snapshots else None,
    )
    for message in report.warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in report.errors:
        print(f"error: {message}", file=sys.stderr)
    failed = bool(report.errors or (args.strict and report.warnings))
    if not failed:
        count = len(json.loads((args.out / "catalog.json").read_text())["processes"])
        print(f"catalog: {count} process(es) -> {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
