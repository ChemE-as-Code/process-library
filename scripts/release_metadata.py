# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Draft the archive metadata of an Atlas LCI release: ``.zenodo.json`` and ``CITATION.cff`` with
the release's version and date, written into the release folder for the owner to check. Both
describe the same work, the LCI database (the title of ``.zenodo.json``), not the whole library.

Nothing is uploaded, tagged or published: the release decision is the owner's
(docs/governance.md, "Releases and DOIs"). The repository's own files are not changed; the DOI
is added to them after the owner has deposited the archive.

    uv run scripts/release_metadata.py --version 0.2.0 --out release [--date 2026-11-01]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?$")


def zenodo(source: Path, version: str, released: str) -> dict:
    data = json.loads(source.read_text(encoding="utf-8"))
    data["version"] = version
    data["publication_date"] = released
    return data


def citation(source: Path, version: str, released: str, title: str) -> str:
    """The repository's CITATION.cff turned into the citation of the LCI database release: its
    ``title`` and ``message`` name the database (the root file cites the whole library, code
    included, which the release's version does not describe), with ``version`` and
    ``date-released`` set. A text edit, so the file keeps its comments and layout."""
    lines, skipping = [], False
    for line in source.read_text(encoding="utf-8").splitlines():
        if re.match(r"^[A-Za-z-]+:", line):
            skipping = bool(re.match(r"^(version|date-released|message):", line))
        elif skipping and (line.startswith(" ") or not line.strip()):
            continue
        if not skipping:
            lines.append(line)
    at = next(i for i, line in enumerate(lines) if line.startswith("title:"))
    lines[at:at + 1] = [
        "message: >-",
        f"  If you use the {title}, please cite this release as below.",
        "  It is licensed under CC BY 4.0 (LICENSE-DATA of the ChemE-as-Code process library).",
        f"title: {title}",
        f"version: {version}",
        f"date-released: '{released}'",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--version", required=True, help="the release's semantic version, e.g. 0.2.0")
    parser.add_argument("--out", type=Path, required=True, help="release folder (the drafts go to <out>/archive/)")
    parser.add_argument("--date", default=date.today().isoformat(), help="release date (default: today)")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root holding .zenodo.json and CITATION.cff")
    args = parser.parse_args(argv)
    if not SEMVER.match(args.version):
        print(f"error: --version {args.version!r} is not a semantic version (MAJOR.MINOR.PATCH)", file=sys.stderr)
        return 1
    archive = args.out / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    data = zenodo(args.root / ".zenodo.json", args.version, args.date)
    (archive / ".zenodo.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (archive / "CITATION.cff").write_text(citation(args.root / "CITATION.cff", args.version, args.date, data["title"]), encoding="utf-8")
    print(f"drafted {archive / '.zenodo.json'} and {archive / 'CITATION.cff'} for {args.version}: nothing was published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
