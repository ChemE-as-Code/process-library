"""The publication policy (ADR 0036 on ADR 0010): every entry is public by default, written
explicitly, and the public build stays fail-closed.

- the process template writes ``publication: {status: public, license: CC-BY-4.0}``;
- every public entry of the library states a licence (the schema requires one on a public
  entry, and the build leaves a public entry without one out, so this test names it);
- an entry kept ``internal`` or ``candidate`` states its own reason in a comment beside the
  status (the template's generic comment does not count), and every block states a status;
- ``scripts/publication.py`` includes only ``status: public`` with a licence: a manifest without
  a publication block, without a status, with ``internal`` or ``candidate``, or public without a
  licence is not public.
- values a package computes from coefficients or tables taken from a licensed handbook (Perry's,
  drawing on DIPPR 801; the CRC Handbook; the VDI Heat Atlas) are single facts with their source,
  never open data (ADR 0037): no source register row of a ``DESIGN.md`` that names DIPPR, Perry's,
  CRC or VDI calls its values open data.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import publication  # noqa: E402

MANIFESTS = sorted((KIT / "processes").glob("*/process.yaml"))
TEMPLATE = KIT / "templates" / "process" / "process.yaml"


def _publication(path: Path) -> dict:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("publication") or {}


def test_the_template_writes_public_with_cc_by():
    manifest = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_a_public_entry_states_its_licence(path):
    pub = _publication(path)
    if pub.get("status") == "public":
        assert pub.get("license"), f"{path.parent.name}: public without publication.license (ADR 0036)"


def _states_its_reason(text: str) -> bool:
    """Whether a comment of the entry's own stands within five lines above its publication block,
    or inside it; a line copied verbatim from the template is not the entry's reason."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("publication:")), None)
    if start is None:
        return False
    end = next((i for i in range(start + 1, len(lines)) if lines[i] and not lines[i][0].isspace()), len(lines))
    template = set(TEMPLATE.read_text(encoding="utf-8").splitlines())
    before = [line for line in lines[max(0, start - 5):start] if line not in template]
    block = [line for line in lines[start:end] if line not in template]
    return any(line.lstrip().startswith("#") for line in before) or any("#" in line for line in block)


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_an_entry_kept_out_states_why(path):
    pub = _publication(path)
    if pub.get("status") == "public":
        return
    text = path.read_text(encoding="utf-8")
    assert any(line.startswith("publication:") for line in text.splitlines()), (
        f"{path.parent.name}: no publication block; a new entry is public (ADR 0036)"
    )
    assert pub.get("status"), f"{path.parent.name}: publication block without a status (ADR 0036)"
    assert _states_its_reason(text), (
        f"{path.parent.name}: publication.status {pub.get('status')!r} without its reason in a comment (ADR 0036)"
    )


def test_the_template_comment_is_not_a_reason():
    """The template switched to internal, with no reason added, does not pass; with one it does."""
    text = TEMPLATE.read_text(encoding="utf-8")
    internal = text.replace("publication: {status: public, license: CC-BY-4.0}", "publication: {status: internal}")
    assert internal != text
    assert not _states_its_reason(internal)
    reason = internal.replace("publication: {status: internal}", "# Internal: the data licence forbids it.\npublication: {status: internal}")
    assert _states_its_reason(reason)


@pytest.mark.parametrize(
    "manifest",
    [None, {}, {"publication": None}, {"publication": {}}, {"publication": {"license": "CC-BY-4.0"}},
     {"publication": {"status": "internal", "license": "CC-BY-4.0"}}, {"publication": {"status": "candidate"}},
     {"publication": {"status": "public"}}, {"publication": {"status": "public", "license": ""}}],
)
def test_the_public_build_stays_fail_closed(manifest):
    assert not publication.is_public(manifest)


def test_public_is_public():
    assert publication.is_public({"publication": {"status": "public", "license": "CC-BY-4.0"}})


def test_the_schema_requires_a_licence_on_a_public_entry():
    import json

    import jsonschema

    schema = json.loads((KIT / "schemas" / "process.schema.json").read_text(encoding="utf-8"))
    sub = schema["properties"]["publication"]
    jsonschema.validate({"status": "public", "license": "CC-BY-4.0"}, sub)
    jsonschema.validate({"status": "internal"}, sub)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"status": "public"}, sub)


DESIGNS = sorted((KIT / "processes").glob("*/DESIGN.md"))
# DIPPR and Perry's in any case; CRC and VDI as written (the packaged tables and thermo's methods:
# CRC_standard_data, Hvap_data_CRC, VDI_PPDS, VDI_TABULAR), so no ordinary word matches them.
_PACKAGED_HANDBOOK = re.compile(r"(?i:DIPPR|Perry's)|CRC|VDI")
_NEGATED = re.compile(r"\b(?:not|no)\s+open data", re.IGNORECASE)
# Rows whose fix waits for an open pull request or issue; strict, so the entry leaves this list once
# fixed.
_PENDING: dict[str, str] = {
    "formic-acid-1": "SRC-7 calls its packaged CRC values open data: issue #433 (left out of #426 "
    "while #396 changed the entry)",
}


def _open_data_claims(text: str) -> list[int]:
    """Line numbers of source register rows that name DIPPR, Perry's, CRC or VDI and call something
    open data other than in 'not open data' / 'no open data'."""
    return [
        number
        for number, line in enumerate(text.splitlines(), 1)
        if line.startswith("|")
        and _PACKAGED_HANDBOOK.search(line)
        and "open data" in _NEGATED.sub("", line).lower()
    ]


@pytest.mark.parametrize("path", DESIGNS, ids=lambda p: p.parent.name)
def test_packaged_handbook_values_are_not_called_open_data(path):
    claims = _open_data_claims(path.read_text(encoding="utf-8"))
    if path.parent.name in _PENDING:
        assert claims, f"{path.parent.name} is fixed: remove it from _PENDING"
        pytest.xfail(_PENDING[path.parent.name])
    assert not claims, (
        f"{path.parent.name}/DESIGN.md lines {claims}: values a package computes from DIPPR/Perry's, CRC or "
        "VDI coefficients and tables are single facts with their source, not open data (ADR 0037)"
    )


def test_the_open_data_check_reads_negation():
    assert _open_data_claims("| SRC-1 | thermo DIPPR_PERRY_8E (Perry's 8th ed.) | open data |") == [1]
    assert _open_data_claims("| SRC-1 | thermo DIPPR_PERRY_8E | the values are not open data |") == []
    assert _open_data_claims("| SRC-1 | NIST WebBook | open data |") == []
    assert _open_data_claims("thermo's DIPPR fits are open data (prose, not a register row)") == []
    assert _open_data_claims("| S4 | chemicals: dHf (CRC, ATcT) | tool output | open data |") == [1]
    assert _open_data_claims("| SRC-1 | chemicals `Hvap_data_CRC` | open data packages |") == [1]
    assert _open_data_claims("| SRC-1 | thermo VDI_PPDS (VDI Heat Atlas) | open data |") == [1]
    assert _open_data_claims("| SRC-1 | chemicals `CRC_standard_data` | single values; not open data |") == []
    assert _open_data_claims("| SRC-1 | Wikipedia: no open data on the CRC value |") == []
    assert _open_data_claims("| SRC-1 | PubChem | REST query | open data |") == []
