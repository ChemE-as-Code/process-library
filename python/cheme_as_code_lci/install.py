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
  activity makes this input, the market of its grade when the library has one (``atlas link:
  market``), else a plant; with ``prefer_atlas`` the exchange links to it instead of the
  background. ``atlas plant activity`` / ``... reference product`` / ``... location`` name the
  plant beside a market: ``prefer_atlas="plant"``, or *pin* for single activities, link to it;
- ``atlas code`` / ``atlas link`` / ``atlas check``: every Atlas-to-Atlas link (also a market's
  suppliers and an explicit ``link.dataset``) with the build's compatibility check (grade, unit,
  system model, allocation, boundary); the report lists them all, and the supply chains;
- a technosphere amount is the quantity of the linked reference product (as in plantcode's
  study), so an exchange linked to a treatment activity (production -1) gets its sign flipped.
"""

from __future__ import annotations

import functools
import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BACKGROUND = "ecoinvent-3.11-cutoff"
TECHNOSPHERE_FIELDS = ("name", "reference product", "unit", "location")
BIOSPHERE_FIELDS = ("name", "categories", "unit")


#: Metadata keys of ``bd.databases[name]`` that identify a background database (as core's
#: ``brightway.expect``).
IDENTITY = ("provider", "version", "system_model")
PREFER = ("market", "plant")


@dataclass
class AtlasLink:
    """One exchange linked inside the Atlas database, with the build's compatibility check."""

    consumer: str  # "<name> | <reference product>" of the activity that takes the input
    consumer_code: str
    key: str  # the exchange's atlas key
    provider: str
    provider_code: str
    #: market | plant (no market of the grade) | pinned (a plant chosen by pin, prefer_atlas="plant"
    #: or link.dataset) | supply (a market's producer) | import (a consumption mix's other market)
    kind: str
    check: str

    @property
    def compatible(self) -> bool:
        return self.check.startswith("compatible")

    def __str__(self) -> str:
        return f"{self.consumer} <- {self.provider} [{self.kind}]: {self.check or 'no check recorded'}"


@dataclass
class InstallReport:
    """What ``install`` did. ``unlinked`` is empty and ``written`` true on success."""

    database: str
    source: str
    background: str
    biosphere: str
    location: str
    location_is_default: bool
    prefer_atlas: bool | str
    #: Whether the background's provider, version and system model were checked (``expect``)
    #: against its metadata, not only its name.
    verified: bool = False
    #: the Atlas database's system model and methodology version (its workbook metadata)
    system_model: str = "unknown"
    methodology_version: str = "unknown"
    activities: int = 0
    exchanges: int = 0
    #: every exchange linked inside the Atlas: inputs (prefer_atlas), markets' suppliers, link.dataset
    atlas_links: list[AtlasLink] = field(default_factory=list)
    #: incompatible Atlas links, unused pins, a background of another system model
    warnings: list[str] = field(default_factory=list)
    #: exchanges linked to a treatment activity, whose sign was flipped
    sign_flipped: list[str] = field(default_factory=list)
    #: every exchange that found no partner: activity, name, type, unit, location, ...
    unlinked: list[dict] = field(default_factory=list)
    written: bool = False

    @property
    def ok(self) -> bool:
        return self.written and not self.unlinked

    def chains(self) -> list[str]:
        """The supply chains of the inputs linked inside the Atlas: ``consumer <- market <- plant``."""
        by_consumer: dict[str, list[AtlasLink]] = {}
        for link in self.atlas_links:
            by_consumer.setdefault(link.consumer_code, []).append(link)
        providers = {link.provider_code for link in self.atlas_links}

        def down(link: AtlasLink, seen: tuple[str, ...]) -> list[str]:
            below = [x for x in by_consumer.get(link.provider_code, []) if x.provider_code not in seen]
            if not below:
                return [link.provider]
            return [f"{link.provider} <- {tail}" for x in below for tail in down(x, (*seen, x.provider_code))]

        return [
            f"{link.consumer} <- {tail}"
            for link in self.atlas_links
            if link.consumer_code not in providers  # start at the activities nothing in the Atlas takes
            for tail in down(link, (link.consumer_code, link.provider_code))
        ]

    def summary(self) -> str:
        kinds: dict[str, int] = {}
        for link in self.atlas_links:
            kinds[link.kind] = kinds.get(link.kind, 0) + 1
        lines = [
            f"{self.database}: {self.activities} activities, {self.exchanges} exchanges from {self.source}",
            f"system model {self.system_model} (methodology {self.methodology_version})",
            f"background {self.background!r}, biosphere {self.biosphere!r}, site location {self.location}"
            + (" (the workbook's default: pass location=...)" if self.location_is_default else ""),
            f"linked inside the Atlas: {len(self.atlas_links)}"
            + (f" ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))})" if kinds else "")
            + f"; treatment links with flipped sign: {len(self.sign_flipped)}",
        ]
        lines += [f"  - {link}" for link in self.atlas_links]
        chains = self.chains()
        if chains:
            lines.append("supply chains inside the Atlas:")
            lines += [f"  - {chain}" for chain in chains]
        lines += [f"warning: {w}" for w in self.warnings]
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


def _plain(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


def _label(ds: dict) -> str:
    return f"{ds.get('name')} | {ds.get('reference product', '')}"


def install(
    path_or_version: str | Path,
    background: str = DEFAULT_BACKGROUND,
    biosphere: str | None = None,
    location: str | None = None,
    prefer_atlas: bool | str = True,
    overwrite: bool = False,
    expect: dict[str, str] | None = None,
    pin: Iterable[str] = (),
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
    says the background was matched by name only (``verified`` false).

    *prefer_atlas*: ``True`` or ``"market"`` links an input another Atlas process makes to the
    Atlas activity the build chose, the market of its grade where one exists; ``"plant"`` links
    it to the plant beside the market instead (at the plant gate: no distribution or losses);
    ``False`` keeps the background. *pin* names single inputs that go to the plant while the
    rest go to the market: a consuming activity's code, or ``"<code>/<atlas key>"`` for one of
    its inputs. The report lists every Atlas-to-Atlas link with the build's compatibility check
    and the supply chains (``report.chains()``)."""
    import bw2data as bd
    import bw2io as bi
    from bw2io.strategies import link_iterable_by_fields

    mode = "market" if prefer_atlas is True else prefer_atlas or None
    if mode not in (None, *PREFER):
        raise ValueError(f"prefer_atlas: {prefer_atlas!r} is not True, False, 'market' or 'plant'")
    path = resolve(path_or_version)
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

    importer = bi.ExcelImporter(str(path))
    name = importer.db_name
    if name in bd.databases and not overwrite:
        raise ValueError(f"database {name!r} exists in project {bd.projects.current!r}; pass overwrite=True to replace it")
    default_site = str(importer.metadata.get("atlas default site location") or "GLO")
    report = InstallReport(name, str(path), background, bio, location or default_site, location is None, prefer_atlas, verified=any((expect or {}).values()))
    report.system_model = str(importer.metadata.get("atlas system model") or "unknown")
    report.methodology_version = str(importer.metadata.get("atlas methodology version") or "unknown")
    theirs = str(meta.get("system_model") or "")
    if theirs and report.system_model != "unknown" and _plain(report.system_model) not in _plain(theirs):
        report.warnings.append(f"background {background!r} records system model {theirs!r}; the Atlas database is {report.system_model!r}: do not mix them in one study")

    pins, used = set(pin), set()
    for ds in importer.data:
        code = str(ds.get("code") or "")
        for exc in ds["exchanges"]:
            if exc.get("atlas location rule") == "site":
                exc["location"] = report.location
            if exc.get("type") == "production":
                continue
            if exc.get("database") == name and exc.get("atlas code"):  # a market's supplier, link.dataset
                provider = f"{exc.get('name')} | {exc.get('reference product', '')}"
                report.atlas_links.append(AtlasLink(_label(ds), code, str(exc.get("atlas key") or ""), provider, exc["atlas code"], exc.get("atlas link") or "fixed", exc.get("atlas check") or ""))
            elif mode and exc.get("atlas activity"):
                keys = {code, f"{code}/{exc.get('atlas key')}"} & pins
                used |= keys
                plant = (mode == "plant" or keys) and exc.get("atlas plant activity")
                prefix, kind, check = ("atlas plant ", "pinned", exc.get("atlas plant check")) if plant else ("atlas ", exc.get("atlas link") or "plant", exc.get("atlas check"))
                exc.update({"name": exc[f"{prefix}activity"], "reference product": exc[f"{prefix}reference product"], "location": exc[f"{prefix}location"], "database": name})
                provider = f"{exc['name']} | {exc['reference product']}"
                report.atlas_links.append(AtlasLink(_label(ds), code, str(exc.get("atlas key") or ""), provider, str(exc.get(f"{prefix}code") or ""), kind, check or ""))
    for unused in sorted(pins - used):
        report.warnings.append(f"pin {unused!r} matched no input linked inside the Atlas")
    for link in report.atlas_links:
        if link.check and not link.compatible:
            report.warnings.append(f"incompatible Atlas link: {link}")

    # The importer's own biosphere step links against config.biosphere; link against *bio* instead.
    importer.strategies = [
        s for s in importer.strategies if not (isinstance(s, functools.partial) and s.func is link_iterable_by_fields)
    ]
    importer.apply_strategies()
    importer.match_database(bio, fields=BIOSPHERE_FIELDS, edge_kinds=["biosphere"])
    importer.match_database(background, fields=TECHNOSPHERE_FIELDS, edge_kinds=["technosphere"])

    for ds in importer.data:
        report.activities += 1
        for exc in ds["exchanges"]:
            report.exchanges += 1
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
                        exc["negative"] = True
                    report.sign_flipped.append(f"{_label(ds)}: {exc['name']}")
    if report.unlinked:
        return report

    if name in bd.databases:
        del bd.databases[name]
    importer.metadata.update({"atlas background": background, "atlas biosphere": bio, "atlas site location": report.location, "atlas prefer_atlas": prefer_atlas})
    importer.write_database(activate_parameters=False)
    report.written = True
    return report
