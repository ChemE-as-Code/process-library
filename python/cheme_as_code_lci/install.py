"""``install()``: the Atlas LCI workbook into the current Brightway project, linked to your
background.

The workbook (``cheme-as-code-atlas-<version>.xlsx``, bw2io ExcelImporter format) references
background activities by name, reference product, unit and location only, and biosphere flows by
name, categories and unit. ``install`` reads it with ``bw2io.ExcelImporter``, applies the
importer's standard strategies, links the rest against *background* and *biosphere* with
``match_database``, and writes the database only when every exchange is linked; otherwise it
returns the unlinked exchanges (nothing is dropped, nothing is written).

Atlas fields in the workbook steer it:

- ``atlas location rule: site``: the exchange's location is the plant's site, replaced by
  *location* (default: the workbook's ``atlas default site location``);
- ``atlas activity`` / ``atlas reference product`` / ``atlas location``: another Atlas
  activity makes this input; with ``prefer_atlas`` the exchange links to it instead of the
  background;
- a technosphere amount is the quantity of the linked reference product (as in plantcode's
  study), so an exchange linked to a treatment activity (production -1) gets its sign flipped;
- ``atlas flow uuid``: the biosphere3 UUID of an elementary flow. The flow whose code is that
  UUID in *biosphere* is taken first (when its unit agrees); name, categories and unit are the
  fallback for a biosphere database with other codes;
- ``atlas pedigree``: the five pedigree scores of the exchange, written as Brightway's
  ``pedigree`` (reliability, completeness, temporal, geographical and further technological
  correlation); the lognormal itself is in the standard uncertainty columns;
- ``atlas superseded by``: the activity is deprecated; it is installed and stays linkable, and
  the report names its successor.

The report also names the database's system model (``atlas system model``) and the version
of the methodology it was built under.
"""

from __future__ import annotations

import functools
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BACKGROUND = "ecoinvent-3.11-cutoff"
TECHNOSPHERE_FIELDS = ("name", "reference product", "unit", "location")
BIOSPHERE_FIELDS = ("name", "categories", "unit")
#: The order of the scores in ``atlas pedigree``, as Brightway names them.
PEDIGREE_KEYS = ("reliability", "completeness", "temporal correlation", "geographical correlation", "further technological correlation")
#: The system models the Atlas builds (build_lci.py SYSTEM_MODELS), for the report.
SYSTEM_MODELS = {
    "cutoff": "attributional, cut-off",
    "substitution": "attributional, substitution variant (avoided-burden credits for recovered materials, energy and exported co-products)",
}


#: Metadata keys of ``bd.databases[name]`` that identify a background database (as core's
#: ``brightway.expect``).
IDENTITY = ("provider", "version", "system_model")


@dataclass
class InstallReport:
    """What ``install`` did. ``unlinked`` is empty and ``written`` true on success."""

    database: str
    source: str
    background: str
    biosphere: str
    location: str
    location_is_default: bool
    prefer_atlas: bool
    #: Whether the background's provider, version and system model were checked (``expect``)
    #: against its metadata, not only its name.
    verified: bool = False
    activities: int = 0
    exchanges: int = 0
    #: "<activity> <- <atlas activity>": inputs linked inside the Atlas (prefer_atlas)
    atlas_links: list[str] = field(default_factory=list)
    #: exchanges linked to a treatment activity, whose sign was flipped
    sign_flipped: list[str] = field(default_factory=list)
    #: every exchange that found no partner: activity, name, type, unit, location, ...
    unlinked: list[dict] = field(default_factory=list)
    written: bool = False
    #: the database's system model id (cutoff, substitution) and methodology version; "" when the
    #: workbook records none (built before the system model was declared)
    system_model: str = ""
    methodology_version: str = ""
    #: "<activity> -> <successor>" of every deprecated activity (installed, with a pointer)
    superseded: list[str] = field(default_factory=list)
    #: elementary flows linked by their biosphere3 UUID, and by name, categories and unit
    biosphere_by_uuid: int = 0
    biosphere_by_name: int = 0

    @property
    def ok(self) -> bool:
        return self.written and not self.unlinked

    def summary(self) -> str:
        lines = [
            f"{self.database}: {self.activities} activities, {self.exchanges} exchanges from {self.source}",
            f"background {self.background!r}, biosphere {self.biosphere!r}, site location {self.location}"
            + (" (the workbook's default: pass location=...)" if self.location_is_default else ""),
            f"system model: {SYSTEM_MODELS.get(self.system_model, self.system_model or 'not recorded')}"
            + (f" ({self.system_model})" if self.system_model in SYSTEM_MODELS else "")
            + (f"; methodology {self.methodology_version}" if self.methodology_version else ""),
            f"linked inside the Atlas: {len(self.atlas_links)}; treatment links with flipped sign: {len(self.sign_flipped)}",
            f"elementary flows linked by biosphere3 UUID: {self.biosphere_by_uuid}; by name and categories: {self.biosphere_by_name}",
        ]
        if self.superseded:
            lines.append(f"deprecated activities (installed, superseded): {len(self.superseded)}")
            lines += [f"  - {text}" for text in self.superseded]
        if self.unlinked:
            lines.append(f"NOT WRITTEN: {len(self.unlinked)} unlinked exchange(s):")
            lines += [f"  - {u['activity']}: {u['type']} {u['name']!r} [{u.get('location') or u.get('categories') or ''}] ({u['unit']})" for u in self.unlinked]
        else:
            lines.append("written" if self.written else "not written")
        return "\n".join(lines)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path_or_version: str | Path) -> Path:
    """The workbook: a path to it, a directory holding the Atlas ``index.json`` (or ``lci/``
    with one), or a version whose ``cheme-as-code-atlas-<version>.xlsx`` is in the current
    directory. A workbook listed in an ``index.json`` beside it must match its sha256."""
    path = Path(path_or_version)
    if path.is_dir():
        index = path / "index.json" if (path / "index.json").is_file() else path / "lci" / "index.json"
        if not index.is_file():
            raise FileNotFoundError(f"{path}: no index.json (the Atlas LCI download folder)")
        files = [f for f in json.loads(index.read_text(encoding="utf-8"))["files"] if f["name"].endswith(".xlsx")]
        if len(files) != 1:
            raise FileNotFoundError(f"{index}: expected one workbook, found {len(files)}")
        path = index.parent / files[0]["name"]
    elif not path.is_file() and path.suffix != ".xlsx":
        path = Path(f"cheme-as-code-atlas-{path_or_version}.xlsx")
    if not path.is_file():
        raise FileNotFoundError(f"{path}: not found (download it from the Process Atlas, Download LCI)")
    index = path.parent / "index.json"
    if index.is_file():
        listed = {f["name"]: f["sha256"] for f in json.loads(index.read_text(encoding="utf-8")).get("files", [])}
        if path.name in listed and listed[path.name] != _sha256(path):
            raise ValueError(f"{path}: sha256 differs from {index}; the download is incomplete or modified")
    return path


def _biosphere(bd, given: str | None) -> str:
    if given:
        if given not in bd.databases:
            raise ValueError(f"no biosphere database {given!r} in project {bd.projects.current!r}")
        return given
    if bd.config.biosphere in bd.databases:
        return bd.config.biosphere
    found = sorted(d for d in bd.databases if d.endswith("biosphere") or d.startswith("biosphere"))
    if len(found) != 1:
        raise ValueError(f"cannot tell the biosphere database ({', '.join(found) or 'none found'}): pass biosphere=...")
    return found[0]


def _link_by_uuid(bd, importer, bio: str, report: InstallReport) -> None:
    """Link every biosphere exchange that names a biosphere3 UUID (``atlas flow uuid``) to the
    flow of that code in *bio*, if there is one and its unit is the exchange's. The rest is left
    to the name, categories and unit match."""
    for ds in importer.data:
        for exc in ds["exchanges"]:
            uuid = exc.get("atlas flow uuid")
            if exc.get("type") != "biosphere" or exc.get("input") or not uuid:
                continue
            try:
                node = bd.get_node(database=bio, code=uuid)
            except Exception:  # bw2data raises its own lookup errors (UnknownObject, DoesNotExist)
                continue
            if node.get("unit") in (None, exc.get("unit")):
                exc["input"] = node.key
                report.biosphere_by_uuid += 1


def _check_background(bd, background: str, biosphere: str | None, expect: dict[str, str] | None) -> str:
    """Check *background* against *expect*; return the biosphere database's name."""
    if background not in bd.databases:
        raise ValueError(f"no background database {background!r} in project {bd.projects.current!r}")
    bio = _biosphere(bd, biosphere)
    meta = bd.databases[background]
    for key, want in (expect or {}).items():
        if key not in IDENTITY:
            raise ValueError(f"expect: unknown key {key!r} (one of {', '.join(IDENTITY)})")
        found = str(meta.get(key) or "")
        if want and found != want:
            raise ValueError(
                f"background {background!r} records {key} {found or '(none)'!r}, expected {want!r}; "
                f"import that database, or, when it is that one, record it: "
                f"bd.databases[{background!r}][{key!r}] = {want!r}; bd.databases.flush()"
            )
    return bio


def _link_external(bd, importer, background: str, bio: str, report: InstallReport) -> None:
    """Link the biosphere (UUID first, then name, categories, unit) and the background (name,
    reference product, unit, location); flip the sign of a link to a treatment activity; count
    and list what stays unlinked."""
    _link_by_uuid(bd, importer, bio, report)
    importer.match_database(bio, fields=BIOSPHERE_FIELDS, edge_kinds=["biosphere"])
    importer.match_database(background, fields=TECHNOSPHERE_FIELDS, edge_kinds=["technosphere"])

    for ds in importer.data:
        report.activities += 1
        for exc in ds["exchanges"]:
            report.exchanges += 1
            if exc.get("type") == "biosphere" and exc.get("input"):
                report.biosphere_by_name += 1
            if not exc.get("input"):
                report.unlinked.append(
                    {k: exc.get(k) for k in ("name", "type", "unit", "location", "reference product", "categories", "atlas key")}
                    | {"activity": _label(ds)}
                )
            elif exc["type"] == "technosphere" and exc["input"][0] == background:
                node = bd.get_node(database=exc["input"][0], code=exc["input"][1])
                if sum(e["amount"] for e in node.production()) < 0:
                    exc["amount"] = -exc["amount"]
                    if exc.get("uncertainty type") == 2:
                        exc["negative"] = exc["amount"] < 0
                    report.sign_flipped.append(f"{_label(ds)}: {exc['name']}")
    report.biosphere_by_name -= report.biosphere_by_uuid  # counted above: every linked biosphere exchange


def _label(ds: dict) -> str:
    return f"{ds.get('name')} | {ds.get('reference product', '')}"


def install(
    path_or_version: str | Path,
    background: str = DEFAULT_BACKGROUND,
    biosphere: str | None = None,
    location: str | None = None,
    prefer_atlas: bool = True,
    overwrite: bool = False,
    expect: dict[str, str] | None = None,
) -> InstallReport:
    """Import the Atlas workbook into the current project, linked to *background* (e.g. your
    ecoinvent database) and *biosphere* (default ``biosphere3``, else the one ``*biosphere``
    database). *location* is the plant site for site-specific inputs such as grid electricity.
    Refuses to replace an existing database of the same name unless *overwrite*. Writes only
    when every exchange is linked; the report lists any that are not.

    *expect* (``{"provider": "ecoinvent", "version": "3.10", "system_model": "cutoff"}``, any
    of them) is checked against the background's metadata (``bd.databases[background]``): a
    local database name alone does not identify a database, and the mappings are written for
    one provider, version and system model. A mismatch refuses; without *expect* the report
    says the background was matched by name only (``verified`` false)."""
    import bw2data as bd
    import bw2io as bi
    from bw2io.strategies import link_iterable_by_fields

    path = resolve(path_or_version)
    bio = _check_background(bd, background, biosphere, expect)

    importer = bi.ExcelImporter(str(path))
    name = importer.db_name
    if name in bd.databases and not overwrite:
        raise ValueError(f"database {name!r} exists in project {bd.projects.current!r}; pass overwrite=True to replace it")
    default_site = str(importer.metadata.get("atlas default site location") or "GLO")
    report = InstallReport(
        name, str(path), background, bio, location or default_site, location is None, prefer_atlas, verified=any((expect or {}).values()),
        system_model=str(importer.metadata.get("atlas system model") or ""), methodology_version=str(importer.metadata.get("atlas methodology version") or ""),
    )

    for ds in importer.data:
        if ds.get("atlas superseded by"):
            report.superseded.append(f"{_label(ds)} -> {ds['atlas superseded by']}")
        for exc in ds["exchanges"]:
            if exc.get("atlas pedigree"):
                scores = [int(x) for x in str(exc["atlas pedigree"]).split(",")]
                exc["pedigree"] = dict(zip(PEDIGREE_KEYS, scores, strict=True))
            if exc.get("atlas location rule") == "site":
                exc["location"] = report.location
            if prefer_atlas and exc.get("atlas activity"):
                exc.update({"name": exc["atlas activity"], "reference product": exc["atlas reference product"], "location": exc["atlas location"], "database": name})
                report.atlas_links.append(f"{_label(ds)} <- {exc['atlas activity']} | {exc['atlas reference product']}")

    # The importer's own biosphere step links against config.biosphere; link against *bio* instead.
    importer.strategies = [
        s for s in importer.strategies if not (isinstance(s, functools.partial) and s.func is link_iterable_by_fields)
    ]
    importer.apply_strategies()
    _link_external(bd, importer, background, bio, report)
    if report.unlinked:
        return report

    if name in bd.databases:
        del bd.databases[name]
    importer.metadata.update({"atlas background": background, "atlas biosphere": bio, "atlas site location": report.location, "atlas prefer_atlas": prefer_atlas})
    importer.write_database(activate_parameters=False)
    report.written = True
    return report
