# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fetch the library's issues for the Process Atlas: every issue labelled ``process:<id>``.

The catalog builder reads checked-in files only and never the network; this script is the one
step that does, before it (``build_catalog.py --issues issues.json``). It writes the issues as
engineering items, read from their labels (core's docs/framework/issues.md):
``type:`` (action, hold, tq, change), ``gate:``, ``discipline:``, ``source:``, ``status:``,
``waiting:`` and ``process:``. Bodies and comments are not fetched.

The token comes from ``GITHUB_TOKEN`` or ``GH_TOKEN``, else ``gh auth token``; it needs
issues:read (and metadata:read) on the repository.

    uv run fetch_issues.py --repository ChemE-as-Code/process-library --out issues.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
SCHEMA = "process-library/issues/v1"
TYPES = ("action", "hold", "tq", "change")
GATES = ("concept", "basic", "detail")
MAX_PAGES = 50


def _token() -> str | None:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(name, "").strip():
            return os.environ[name].strip()
    gh = shutil.which("gh")
    if gh:
        run = subprocess.run([gh, "auth", "token"], capture_output=True, text=True, timeout=10)
        if run.returncode == 0 and run.stdout.strip():
            return run.stdout.strip()
    return None


def _get(url: str, token: str) -> Any:
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "process-library fetch_issues",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def record(item: dict[str, Any]) -> dict[str, Any]:
    """One API issue as an engineering item (the vocabulary of core's project/issues.py)."""
    names = [label["name"] for label in item.get("labels", [])]

    def tagged(prefix: str) -> list[str]:
        return sorted(n[len(prefix):] for n in names if n.startswith(prefix))

    # two gate: labels (one left by an edit) count at the earlier; an unknown one first (core's
    # project/issues.py does the same, so the Atlas and the gates agree)
    gates = sorted(tagged("gate:"), key=lambda g: (GATES.index(g) + 1 if g in GATES else 0, g))
    statuses = tagged("status:")
    types = [t for t in tagged("type:") if t in TYPES]
    first = lambda values: values[0] if values else None  # noqa: E731
    return {
        "number": item["number"],
        "title": item["title"],
        "state": item["state"],
        "status": "closed" if item["state"] == "closed" else first(statuses) or "open",
        "type": first(types),
        "gate": first(gates),
        "disciplines": tagged("discipline:"),
        "source": first(tagged("source:")),
        "waiting": first(tagged("waiting:")),
        "processes": tagged("process:"),
        "url": item["html_url"],
        "updated": item["updated_at"],
        "closed": item.get("closed_at"),
    }


def fetch(repository: str, token: str) -> dict[str, Any]:
    meta = _get(f"{API}/repos/{repository}", token)
    issues = []
    for page in range(1, MAX_PAGES + 1):
        query = urllib.parse.urlencode({"state": "all", "per_page": 100, "page": page})
        batch = _get(f"{API}/repos/{repository}/issues?{query}", token)
        issues += [
            record(i) for i in batch
            if "pull_request" not in i and any(label["name"].startswith("process:") for label in i["labels"])
        ]
        if len(batch) < 100:
            break
    else:
        raise SystemExit(f"error: {repository} has more than {MAX_PAGES * 100} issues and pull requests")
    return {
        "schema": SCHEMA,
        "repository": repository,
        "private": bool(meta.get("private", True)),
        "web": meta.get("html_url", f"https://github.com/{repository}"),
        "issues": sorted(issues, key=lambda i: i["number"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repository", required=True, help="owner/name")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    token = _token()
    if not token:
        print("error: no GitHub token (GITHUB_TOKEN, GH_TOKEN or gh auth login)", file=sys.stderr)
        return 1
    data = fetch(args.repository, token)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"issues: {len(data['issues'])} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
