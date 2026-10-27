#!/usr/bin/env python3
"""Check the background names of lci/mappings.yaml against a licensed background database and
record the check (process-library#85, ADR 0017).

``lci/mappings.yaml`` links exchanges to the background by name only: an activity by name,
reference product, unit and location, an elementary flow by biosphere3 UUID or by name and
categories. Nothing in the repository proves those names exist. This script is run by someone
who holds a licence, in a Brightway project that holds the background (for example ecoinvent
3.11 cut-off) and its biosphere, and writes what it found to
``lci/mapping-checks/<date>-<database>.yaml`` (schema ``schemas/lci-mapping-check.schema.json``):
the database and version, the date, who checked, the sites a ``location: site`` entry was
checked for, and every name that did not match. ``build_lci.py`` reads the latest record and
states in ``datapackage.json`` whether the mappings are verified, failed, stale or unchecked.

The record holds the library's own names and, for an unmatched name, the locations at which the
background has the same name and reference product: identifiers, never data of the background
(CLAUDE.md, ADR 0013).

What is checked: every ``technosphere`` and ``substitution.technosphere`` entry with an
``activity`` (a ``location: site`` once per ``--site``; the mappings' ``default_site_location``
when none is given), and every ``biosphere`` entry's flow (by UUID when it has one, else by name
and categories). Not checked here: flows that a dataset links by its own crosswalk UUID; the
installer (``cheme_as_code_lci.install``) reports any of those that do not link.

    uv run --with bw2data --with pyyaml --with jsonschema scripts/check_mappings.py \\
        --project my-lca --background ecoinvent-3.11-cutoff --version "3.11" \\
        --checked-by "A. Curator" --site DE --site NL --write

Without ``--write`` the record is printed, not saved. The exit code is 1 when a name does not
match.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA = "cheme-as-code/lci-mapping-check/v1"
HERE = Path(__file__).resolve().parent
LIBRARY = HERE.parent
#: the mappings' placeholder for the plant's country, replaced at install time
SITE = "site"


def targets(mappings: dict) -> list[dict]:
    """Every background name of *mappings* that a background must hold, in file order. An
    activity keeps ``location: site`` unexpanded, so the list (and its hash) does not depend on
    the sites a check covers."""
    found: list[dict] = []
    sections = (("technosphere", mappings.get("technosphere") or {}), ("substitution.technosphere", ((mappings.get("substitution") or {}).get("technosphere") or {})))
    for section, entries in sections:
        for tid, entry in entries.items():
            activity = entry.get("activity")
            if activity:
                found.append({"entry": f"{section}.{tid}", "kind": "technosphere", "name": activity["name"], "reference_product": activity["reference_product"], "unit": activity["unit"], "location": activity["location"]})
    for fid, entry in (mappings.get("biosphere") or {}).items():
        flow = entry["flow"]
        found.append({"entry": f"biosphere.{fid}", "kind": "biosphere", "name": flow["name"], "categories": list(flow["categories"]), **({"uuid": flow["uuid"]} if flow.get("uuid") else {})})
    return found


def targets_sha256(mappings: dict) -> str:
    """The hash a record stores: a later change to any checked name makes the record stale,
    while edits to comments, sources or proxies' amounts do not."""
    text = json.dumps(targets(mappings), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check(mappings: dict, background: Iterable[dict], biosphere: Iterable[dict], sites: list[str]) -> tuple[int, list[dict]]:
    """Match the targets of *mappings* against *background* (dicts with name, reference
    product, unit, location) and *biosphere* (dicts with code, name, categories). Return the
    number of names checked and the unmatched ones, each with a ``reason``. Matching is exact,
    as the installer's (bw2io ``match_database`` on the same fields)."""
    activities = {(a.get("name"), a.get("reference product"), a.get("unit"), a.get("location")) for a in background}
    locations: dict[tuple, set[str]] = {}
    names = set()
    for name, product, unit, location in activities:
        locations.setdefault((name, product, unit), set()).add(str(location))
        names.add(name)
    biosphere = list(biosphere)
    by_code = {f.get("code"): f for f in biosphere}
    flows = {(f.get("name"), tuple(f.get("categories") or ())) for f in biosphere}

    checked = 0
    unmatched: list[dict] = []
    for target in targets(mappings):
        if target["kind"] == "technosphere":
            for location in (sites if target["location"] == SITE else [target["location"]]):
                checked += 1
                key = (target["name"], target["reference_product"], target["unit"], location)
                if key in activities:
                    continue
                miss = {**target, "location": location, **({"site": True} if target["location"] == SITE else {})}
                elsewhere = sorted(locations.get(key[:3], set()))
                if elsewhere:
                    miss["reason"] = "location not in the background"
                    miss["available_locations"] = elsewhere
                elif target["name"] in names:
                    miss["reason"] = "name in the background, with another reference product or unit"
                else:
                    miss["reason"] = "name not in the background"
                unmatched.append(miss)
        else:
            checked += 1
            if "uuid" in target:
                node = by_code.get(target["uuid"])
                if node is None:
                    unmatched.append({**target, "reason": "uuid not in the biosphere"})
                elif (node.get("name"), tuple(node.get("categories") or ())) != (target["name"], tuple(target["categories"])):
                    unmatched.append({**target, "reason": "uuid in the biosphere under another name or categories"})
            elif (target["name"], tuple(target["categories"])) not in flows:
                unmatched.append({**target, "reason": "name and categories not in the biosphere"})
    return checked, unmatched


def record(mappings: dict, checked: int, unmatched: list[dict], *, database: str, version: str, biosphere: str, sites: list[str], checked_by: str, date: dt.date, system_model: str | None = None, note: str | None = None) -> dict:
    """The check record written to lci/mapping-checks/."""
    return {
        "schema": SCHEMA,
        "background": {"database": database, "version": version, **({"system_model": system_model} if system_model else {})},
        "biosphere": biosphere,
        "checked": date.isoformat(),
        "checked_by": checked_by,
        "sites": list(sites),
        "tool": "scripts/check_mappings.py",
        "mappings_targets_sha256": targets_sha256(mappings),
        "result": {"checked": checked, "matched": checked - len(unmatched), "unmatched": len(unmatched)},
        "unmatched": unmatched,
        **({"note": note} if note else {}),
    }


def validate(data: Any, schema_path: Path | None = None) -> list[str]:
    schema = json.loads((schema_path or LIBRARY / "schemas" / "lci-mapping-check.schema.json").read_text(encoding="utf-8"))
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]


def status(mappings: dict, folder: Path, schema_path: Path | None = None) -> tuple[dict, list[str]]:
    """The state of the mappings' check, from the latest record in *folder* (by ``checked``,
    then file name): ``unchecked`` (no record), ``stale`` (a checked name changed since),
    ``failed`` (names did not match) or ``verified``. Returns it and the problems of invalid
    records (build errors)."""
    problems: list[str] = []
    records = []
    for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else []:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if isinstance(data, dict) and isinstance(data.get("checked"), dt.date):  # an unquoted date in a hand-edited record
            data["checked"] = data["checked"].isoformat()
        errors = validate(data, schema_path)
        if errors:
            problems += [f"lci/mapping-checks/{path.name}: {e}" for e in errors]
            continue
        records.append((str(data["checked"]), path.name, data))
    if not records:
        return {"status": "unchecked", "note": "not checked against a licensed background yet (scripts/check_mappings.py)"}, problems
    _, name, data = max(records, key=lambda r: (r[0], r[1]))
    state = {
        "record": f"lci/mapping-checks/{name}",
        "background": data["background"],
        "checked": str(data["checked"]),
        "checked_by": data["checked_by"],
        "sites": data["sites"],
        **data["result"],
    }
    if data["mappings_targets_sha256"] != targets_sha256(mappings):
        return {"status": "stale", **state, "note": "a checked name changed after the latest check; run scripts/check_mappings.py again"}, problems
    return {"status": "failed" if data["result"]["unmatched"] else "verified", **state}, problems


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "-", text.lower()).strip("-")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, default=LIBRARY, help="library root (default: this repository)")
    parser.add_argument("--project", required=True, help="Brightway project that holds the background and its biosphere")
    parser.add_argument("--background", required=True, help="background database name in the project, e.g. ecoinvent-3.11-cutoff")
    parser.add_argument("--version", required=True, help="the background's release, as its provider names it, e.g. 3.11")
    parser.add_argument("--system-model", help="the background's system model (default: its bd.databases metadata, if recorded)")
    parser.add_argument("--biosphere", default="biosphere3", help="biosphere database name (default: biosphere3)")
    parser.add_argument("--site", action="append", default=[], help="country checked for `location: site` entries; repeat (default: the mappings' default_site_location)")
    parser.add_argument("--checked-by", required=True, help="who ran the check (name; recorded)")
    parser.add_argument("--note", help="free text recorded with the check")
    parser.add_argument("--write", action="store_true", help="write lci/mapping-checks/<date>-<database>.yaml (default: print it)")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(HERE))
    import build_lci  # noqa: PLC0415 (the mappings' own loader and schema check)
    import bw2data as bd  # noqa: PLC0415 (only the person with the licensed project needs it)

    library = args.library.resolve()
    mappings = build_lci.load_mappings(library / "lci" / "mappings.yaml")
    if args.project not in bd.projects:
        raise SystemExit(f"no Brightway project {args.project!r}")
    bd.projects.set_current(args.project)
    for name in (args.background, args.biosphere):
        if name not in bd.databases:
            raise SystemExit(f"no database {name!r} in project {args.project!r}")
    background = [{k: a.get(k) for k in ("name", "reference product", "unit", "location")} for a in bd.Database(args.background)]
    biosphere = [{"code": f["code"], "name": f.get("name"), "categories": list(f.get("categories") or ())} for f in bd.Database(args.biosphere)]
    sites = args.site or [mappings["default_site_location"]]
    system_model = args.system_model or (str(bd.databases[args.background].get("system_model") or "") or None)
    checked, unmatched = check(mappings, background, biosphere, sites)
    data = record(
        mappings, checked, unmatched, database=args.background, version=args.version, biosphere=args.biosphere, sites=sites,
        checked_by=args.checked_by, date=dt.date.today(), system_model=system_model, note=args.note,
    )
    problems = validate(data, library / "schemas" / "lci-mapping-check.schema.json")
    if problems:
        raise SystemExit("record fails its schema: " + "; ".join(problems))
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120)
    if args.write:
        folder = library / "lci" / "mapping-checks"
        folder.mkdir(exist_ok=True)
        path = folder / f"{data['checked']}-{_slug(args.background)}.yaml"
        path.write_text(text, encoding="utf-8")
        print(f"{checked - len(unmatched)} of {checked} names matched -> {path}")
    else:
        print(text)
    for miss in unmatched:
        where = miss.get("location") or miss.get("uuid") or "/".join(miss.get("categories", []))
        print(f"unmatched: {miss['entry']}: {miss['name']!r} [{where}]: {miss['reason']}", file=sys.stderr)
    return 1 if unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
