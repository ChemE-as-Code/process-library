"""``install_multifunctional()``: the Atlas's unallocated multi-output datasets into a Brightway
2.5 project, as a ``multifunctional.MultifunctionalDatabase``, linked to your background.

The file (``cheme-as-code-atlas-<version>-multifunctional.json``, written by
``scripts/build_lci.py``; schema ``cheme-as-code/lci-multifunctional/v1``) holds one
multi-output process per Atlas dataset: every co-product is a functional production edge with
its allocation properties (``mass`` for a product in kg, ``exergy`` and ``energy`` in kJ per
unit, ``price``: only the values the dataset or study states) and the build's ``share``; the
other exchanges carry their amounts per dataset basis (e.g. 1 h of operation) and the same
linking fields as the workbook. The screening proxies are ordinary single-output processes.

``multifunctional`` allocates each process into read-only single-output processes whose codes
are the workbook's activity codes (``<process>:<dataset>:<product key>``). With the default
strategy of each process (the build's method: ``exergy`` for ASU-1, or ``share`` where the
properties cannot reproduce it) they are the workbook's activities. To choose another
allocation::

    node = bd.get_node(database=report.database, code="asu-1:asu-1-500-t-d-gox")
    node["default_allocation"] = "mass"     # or exergy, energy, price, share, equal
    node.save()
    bd.Database(report.database).process()

Linking is the workbook installer's (``install``): biosphere3 UUIDs first, then name,
categories and unit; background by name, reference product, unit and location; the plant site
replaced by *location*; treatment links with their sign flipped; an input another Atlas process
makes linked to the Atlas activity the build chose (the market of its grade where one exists) with
*prefer_atlas*, or to the plant with ``prefer_atlas="plant"``. The markets
(``market:<product>:<region>``) are single-output processes, linked to their suppliers. Nothing is
written unless everything links.
"""

from __future__ import annotations

import json
from pathlib import Path

from cheme_as_code_lci.install import (
    DEFAULT_BACKGROUND,
    PEDIGREE_KEYS,
    PREFER,
    AtlasLink,
    InstallReport,
    _check_background,
    _check_system_model,
    _label,
    _link_external,
    _sha256,
)

SCHEMA = "cheme-as-code/lci-multifunctional/v1"
#: Strategies the file uses beyond multifunctional's built-in ``mass`` and ``price``:
#: (property label, normalised by the production amount).
CUSTOM_STRATEGIES = (("exergy", True), ("energy", True), ("share", False))


def resolve_multifunctional(path: str | Path) -> Path:
    """The multifunctional file: its path, or a folder with the Atlas ``index.json`` (or
    ``lci/`` with one). A file listed in an ``index.json`` beside it must match its sha256."""
    path = Path(path)
    if path.is_dir():
        index = path / "index.json" if (path / "index.json").is_file() else path / "lci" / "index.json"
        if not index.is_file():
            raise FileNotFoundError(f"{path}: no index.json (the Atlas LCI download folder)")
        files = [f for f in json.loads(index.read_text(encoding="utf-8"))["files"] if f["name"].endswith("-multifunctional.json")]
        if len(files) != 1:
            raise FileNotFoundError(f"{index}: expected one multifunctional file, found {len(files)}")
        path = index.parent / files[0]["name"]
    if not path.is_file():
        raise FileNotFoundError(f"{path}: not found")
    index = path.parent / "index.json"
    if index.is_file():
        listed = {f["name"]: f["sha256"] for f in json.loads(index.read_text(encoding="utf-8")).get("files", [])}
        if path.name in listed and listed[path.name] != _sha256(path):
            raise ValueError(f"{path}: sha256 differs from {index}; the download is incomplete or modified")
    return path


def register_strategies() -> None:
    """Add the Atlas's property strategies (exergy, energy, share) to multifunctional's, for
    this project (persisted by ``add_custom_property_allocation_to_project``)."""
    import multifunctional as mf

    for label, normalise in CUSTOM_STRATEGIES:
        if label not in mf.allocation_strategies:
            mf.add_custom_property_allocation_to_project(label, normalize_by_production_amount=normalise)


def install_multifunctional(
    path: str | Path,
    background: str = DEFAULT_BACKGROUND,
    biosphere: str | None = None,
    location: str | None = None,
    prefer_atlas: bool | str = True,
    overwrite: bool = False,
    expect: dict[str, str] | None = None,
    allocation: str | None = None,
) -> InstallReport:
    """Install the unallocated datasets as ``<database>-multifunctional`` (a
    ``MultifunctionalDatabase``). *allocation* (``mass``, ``exergy``, ``energy``, ``price``,
    ``share``, ``equal``) replaces every process's default strategy; by default each process
    keeps the build's method. The other arguments are ``install``'s."""
    import bw2data as bd
    import bw2io as bi
    import multifunctional as mf

    mode = "market" if prefer_atlas is True else prefer_atlas or None
    if mode not in (None, *PREFER):
        raise ValueError(f"prefer_atlas: {prefer_atlas!r} is not True, False, 'market' or 'plant'")
    path = resolve_multifunctional(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"{path}: schema {data.get('schema')!r}, expected {SCHEMA!r}")
    bio = _check_background(bd, background, biosphere, expect)
    name = data["database"]
    if name in bd.databases and not overwrite:
        raise ValueError(f"database {name!r} exists in project {bd.projects.current!r}; pass overwrite=True to replace it")
    register_strategies()
    if allocation is not None and allocation not in mf.allocation_strategies:
        raise ValueError(f"allocation {allocation!r} is not one of {', '.join(sorted(mf.allocation_strategies))}")

    meta = data["metadata"]
    default_site = str(meta.get("atlas default site location") or "GLO")
    report = InstallReport(
        name, str(path), background, bio, location or default_site, location is None, prefer_atlas, verified=any((expect or {}).values()),
        system_model=str(meta.get("atlas system model") or ""), methodology_version=str(meta.get("atlas methodology version") or ""),
    )
    _check_system_model(bd, background, report)
    importer = bi.importers.base_lci.LCIImporter(name)
    importer.data = []
    for process in data["processes"]:
        ds = {k: v for k, v in process.items() if k != "exchanges"} | {"database": name}
        if allocation is not None and ds["type"] == "multifunctional":
            ds["default_allocation"] = allocation
        ds["exchanges"] = []
        for given in process["exchanges"]:
            exc = dict(given)
            if exc.get("categories"):
                exc["categories"] = tuple(exc["categories"])
            if exc.get("atlas pedigree"):
                exc["pedigree"] = dict(zip(PEDIGREE_KEYS, (int(x) for x in str(exc["atlas pedigree"]).split(",")), strict=True))
            if exc.get("atlas location rule") == "site":
                exc["location"] = report.location
            # an alternative inside the Atlas (prefer_atlas) goes before a proxy's fixed atlas code
            if mode and exc.get("atlas activity code"):
                plant = mode == "plant" and exc.get("atlas plant code")
                prefix, code, kind, check = (
                    ("atlas plant ", exc["atlas plant code"], "pinned", exc.get("atlas plant check")) if plant
                    else ("atlas ", exc["atlas activity code"], exc.get("atlas link") or "plant", exc.get("atlas check"))
                )
                exc["input"] = (name, code)
                provider = f"{exc[f'{prefix}activity']} | {exc[f'{prefix}reference product']}"
                report.atlas_links.append(AtlasLink(_label(ds), ds["code"], str(exc.get("atlas key") or ""), provider, code, kind, check or ""))
            elif exc.get("atlas code"):  # a market's supplier, link.dataset, a proxy
                # a proxy's alternative left out (prefer_atlas=False) is not what its link and check describe
                fixed = ("fixed", "") if exc.get("atlas activity code") else (exc.get("atlas link") or "fixed", exc.get("atlas check") or "")
                exc["input"] = (name, exc["atlas code"])
                provider = f"{exc.get('name')} | {exc.get('reference product', '')}"
                report.atlas_links.append(AtlasLink(_label(ds), ds["code"], str(exc.get("atlas key") or ""), provider, exc["atlas code"], *fixed))
            if exc["type"] == "production" and ds["type"] != "multifunctional":
                exc["input"] = (name, ds["code"])  # a single-output process makes its own product
            ds["exchanges"].append(exc)
        importer.data.append(ds)

    # functional edges are linked by multifunctional (to the allocated processes it creates)
    functional = {id(e) for ds in importer.data if ds["type"] == "multifunctional" for e in ds["exchanges"] if e.get("functional")}
    for ds in importer.data:
        for exc in ds["exchanges"]:
            if id(exc) in functional:
                exc["input"] = ("__functional__", "")
    for link in report.atlas_links:
        if link.check and not link.compatible:
            report.warnings.append(f"incompatible Atlas link: {link}")
    _link_external(bd, importer, background, bio, report)
    for ds in importer.data:
        for exc in ds["exchanges"]:
            if id(exc) in functional:
                del exc["input"]
    if report.unlinked:
        return report

    if name in bd.databases:
        del bd.databases[name]
    importer.metadata = dict(meta) | {
        "default_allocation": "share",  # each process names its own; this is the fallback
        "atlas background": background, "atlas biosphere": bio, "atlas site location": report.location, "atlas prefer_atlas": prefer_atlas,
    }
    importer.write_database(activate_parameters=False)
    report.written = True
    return report
