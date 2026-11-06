"""The publication policy (ADR 0036 on ADR 0010): every entry is public by default, written
explicitly, and the public build stays fail-closed.

- the process template writes ``publication: {status: public, license: CC-BY-4.0}``;
- every public entry of the library states a licence (the schema and the build have no default,
  so this test is what catches a public entry without one);
- an entry kept ``internal`` or ``candidate`` states its reason in a comment beside the status;
- ``scripts/publication.py`` still includes only ``status: public``: a manifest without a
  publication block, without a status, or with ``internal`` or ``candidate`` is not public.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import publication  # noqa: E402

MANIFESTS = sorted((KIT / "processes").glob("*/process.yaml"))


def _publication(path: Path) -> dict:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("publication") or {}


def test_the_template_writes_public_with_cc_by():
    manifest = yaml.safe_load((KIT / "templates" / "process" / "process.yaml").read_text(encoding="utf-8"))
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_a_public_entry_states_its_licence(path):
    pub = _publication(path)
    if pub.get("status") == "public":
        assert pub.get("license"), f"{path.parent.name}: public without publication.license (ADR 0036)"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_an_entry_kept_out_states_why(path):
    pub = _publication(path)
    if pub.get("status") == "public":
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("publication:")), None)
    assert start is not None, f"{path.parent.name}: no publication block; a new entry is public (ADR 0036)"
    end = next((i for i in range(start + 1, len(lines)) if lines[i] and not lines[i][0].isspace()), len(lines))
    before = lines[max(0, start - 5):start]
    block = lines[start:end]
    assert any(line.lstrip().startswith("#") for line in before) or any("#" in line for line in block), (
        f"{path.parent.name}: publication.status {pub.get('status')!r} without its reason in a comment (ADR 0036)"
    )


@pytest.mark.parametrize(
    "manifest",
    [None, {}, {"publication": None}, {"publication": {}}, {"publication": {"license": "CC-BY-4.0"}},
     {"publication": {"status": "internal", "license": "CC-BY-4.0"}}, {"publication": {"status": "candidate"}}],
)
def test_the_public_build_stays_fail_closed(manifest):
    assert not publication.is_public(manifest)


def test_public_is_public():
    assert publication.is_public({"publication": {"status": "public", "license": "CC-BY-4.0"}})
