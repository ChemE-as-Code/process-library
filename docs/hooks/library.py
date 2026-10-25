"""MkDocs hook: pages generated from the library itself, and nav entries that may be missing.

- ``processes/<id>.md``, one page per published process (``processes/*/process.yaml`` with
  ``publication.status: public``, the rule of scripts/publication.py): the manifest's key facts and
  the process folder's README.md (included through docs/hooks/includes.py, unless the process's
  ``publication.exclude`` names it). Each is added to the nav section "Processes".
- ``reference/<name>.md``, one page per ``schemas/<name>.schema.json``: a field table of every
  object in the schema, map entries included (``<key>`` in a path). Each is added to the nav
  section "Schemas", and a page line ``<!-- schema-list -->`` becomes a list of them. A property
  of the schema missing from its page is a warning, so ``mkdocs build --strict`` fails.
- Nav entries listed in OPTIONAL are dropped while their page does not exist, so the nav may name
  pages that other changes add.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import posixpath
import re
from pathlib import Path

import yaml
from includes import _headings  # docs/hooks/ is on sys.path while MkDocs loads a hook
from mkdocs.structure.files import File

log = logging.getLogger("mkdocs.hooks.library")

OPTIONAL = {"system-model.md", "governance.md", "coverage.md"}

_root = Path(".")
_blob = ""  # GitHub URL prefix of repository files
_pages: dict[str, str] = {}  # src_uri -> Markdown
_schemas: list[tuple[str, str, str]] = []  # (nav title, src_uri, file it checks) per schema page


def _escape(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|").replace("<", "&lt;")


def _code(value) -> str:
    return f"`{json.dumps(value) if not isinstance(value, str) else value}`"


def _type(node: dict) -> str:
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return f"[{name}](#{name})"
    if "const" in node:
        return f"const {_code(node['const'])}"
    if "enum" in node:
        return "one of " + ", ".join(_code(v) for v in node["enum"])
    kind = node.get("type", "any")
    if kind == "array":
        return f"array of {_type(node.get('items', {}))}"
    return kind if isinstance(kind, str) else " or ".join(kind)


def _constraints(node: dict) -> str:
    keys = ("pattern", "format", "minLength", "maxLength", "minItems", "minProperties", "minimum", "exclusiveMinimum")
    out = [f"{k}: {_code(node[k])}" for k in keys if k in node]
    if node.get("uniqueItems"):
        out.append("unique")
    if "propertyNames" in node:
        names = node["propertyNames"]
        out.append("keys: " + (_type(names) if "$ref" in names else _constraints(names) or "any"))
    for word, key in (("exactly one", "oneOf"), ("at least one", "anyOf")):
        alternatives = node.get(key, [])
        if alternatives and all(set(a) == {"required"} for a in alternatives):
            out.append(f"{word} of " + " / ".join(", ".join(f"`{r}`" for r in a["required"]) for a in alternatives))
    return "; ".join(out)


def _map_entry(node: dict) -> dict | None:
    """The schema of a map's values (``additionalProperties`` holding an object schema)."""
    entry = node.get("additionalProperties")
    return entry if isinstance(entry, dict) and "properties" in entry else None


def _rows(node: dict, prefix: str = "") -> list[str]:
    rows, required = [], set(node.get("required", []))
    for name, child in node.get("properties", {}).items():
        path = prefix + name
        doc = _escape(child.get("description", ""))
        extra = _constraints(child) or _constraints(child.get("items", {}))
        entry = _map_entry(child)
        kind = "map of object" if entry else _type(child)
        cells = [f"`{path}`", kind, "yes" if name in required else "", doc, _escape(extra)]
        rows.append("| " + " | ".join(cells) + " |")
        if "properties" in child:
            rows += _rows(child, path + ".")
        elif "properties" in child.get("items", {}):
            rows += _rows(child["items"], path + "[].")
        elif entry:
            own = _constraints(entry)
            rows.append(f"| `{path}.<key>` | object | | {_escape(entry.get('description', ''))} | {_escape(own)} |")
            rows += _rows(entry, path + ".<key>.")
    return rows


def _table(node: dict) -> str:
    head = "| field | type | required | description | constraints |\n|---|---|---|---|---|"
    return "\n".join([head, *_rows(node)])


def _schema_page(path: Path) -> tuple[str, str]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    title = schema.get("title", path.name)
    rel = path.relative_to(_root).as_posix()
    parts = [f"# {title}", ""]
    if "description" in schema:
        parts += [schema["description"], ""]
    parts += [
        f"Generated from [`{rel}`]({_blob}{rel}) (`$id` `{schema.get('$id', '')}`). "
        "Fields not listed are not allowed where the object sets `additionalProperties: false`. "
        "A map (an object whose keys are free, within the row's key constraint) has its entries "
        "listed under `<key>`.",
        "",
        _table(schema),
    ]
    for name, node in schema.get("$defs", {}).items():
        parts += ["", f"## {name}", ""]
        if "description" in node:
            parts += [node["description"], ""]
        parts.append(_table(node) if "properties" in node else f"{_type(node)}. {_escape(_constraints(node))}")
    page = "\n".join(parts) + "\n"
    for name in sorted(_property_names(schema)):
        if not re.search(rf"`[^`|]*\b{re.escape(name)}` \|", page):
            log.warning("%s: property '%s' is missing from its reference page", rel, name)
    return title, page


def _property_names(node) -> set[str]:
    """Every property name declared anywhere in a schema."""
    names = set()
    if isinstance(node, dict):
        names |= set(node.get("properties", {}) if isinstance(node.get("properties"), dict) else ())
        for value in node.values():
            names |= _property_names(value)
    elif isinstance(node, list):
        for value in node:
            names |= _property_names(value)
    return names


def _first_heading(readme: Path) -> str | None:
    lines = readme.read_text(encoding="utf-8").splitlines()
    return next((f"# {text}" for _, level, text in _headings(lines) if level == 1), None)


def _glob(pattern: str) -> re.Pattern:
    """A publication.exclude glob: ``**`` spans directories, ``*`` stays in one (scripts/publication.py)."""
    out = re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.compile(out.replace(r"\?", "[^/]") + "$")


def _process_page(folder: Path, manifest: dict, excludes: list[str]) -> tuple[str, str]:
    pid = manifest.get("id", folder.name)
    title = manifest.get("title", pid)
    rel = folder.relative_to(_root).as_posix()
    facts = [
        ("id", f"`{pid}`"),
        ("maturity", f"`{manifest.get('maturity', '')}`"),
        ("review", f"`{(manifest.get('validation') or {}).get('status', '')}`"),
        ("license", f"`{(manifest.get('publication') or {}).get('license', '')}`"),
        ("families", ", ".join(f"`{f}`" for f in manifest.get("families", []))),
        ("capacity", _escape((manifest.get("basis") or {}).get("capacity", ""))),
    ]
    parts = [f"# {title}", "", _escape(manifest.get("summary", "")), "", "| | |", "|---|---|"]
    parts += [f"| {k} | {v} |" for k, v in facts if v.strip("`")]
    parts += ["", f"From [`{rel}/process.yaml`]({_blob}{rel}/process.yaml) (the Atlas manifest).", ""]
    readme = folder / "README.md"
    published = not any(_glob(g).match("README.md") for g in excludes)
    if published and readme.is_file() and (heading := _first_heading(readme)):
        parts += ["## The process folder", "", f"<!-- include: {rel}/README.md :: {heading} | body -->"]
    return title, "\n".join(parts) + "\n"


def _walk(nav, fn):
    """Apply fn to every list in the nav tree (in place)."""
    if isinstance(nav, list):
        fn(nav)
        for item in nav:
            if isinstance(item, dict):
                for value in item.values():
                    _walk(value, fn)


def _section(nav, title: str) -> list | None:
    found = []

    def look(items):
        found.extend(v for item in items if isinstance(item, dict) for k, v in item.items() if k == title and isinstance(v, list))

    _walk(nav, look)
    return found[0] if found else None


def _publication(root: Path):
    spec = importlib.util.spec_from_file_location("publication", root / "scripts" / "publication.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def on_config(config):
    global _root, _blob
    _root = Path(config.config_file_path).parent
    _blob = (config.repo_url or "").rstrip("/") + "/blob/main/"
    docs = Path(config.docs_dir)
    publication = _publication(_root)
    _pages.clear()
    _schemas.clear()

    def missing(item) -> bool:  # an optional page that does not exist (yet)
        targets = item.values() if isinstance(item, dict) else [item]
        return any(t in OPTIONAL and not (docs / t).is_file() for t in targets if isinstance(t, str))

    def prune(items):
        items[:] = [item for item in items if not missing(item)]

    _walk(config.nav, prune)

    processes = _section(config.nav, "Processes")
    for folder in sorted(p.parent for p in (_root / "processes").glob("*/process.yaml")):
        manifest = yaml.safe_load((folder / "process.yaml").read_text(encoding="utf-8")) or {}
        if not publication.is_public(manifest):  # internal and candidate processes stay out
            continue
        title, text = _process_page(folder, manifest, publication.snapshot_excludes(manifest))
        uri = f"processes/{folder.name}.md"
        _pages[uri] = text
        if processes is not None:
            processes.append({title: uri})

    schemas = _section(config.nav, "Schemas")
    for path in sorted((_root / "schemas").glob("*.schema.json")):
        title, text = _schema_page(path)
        uri = f"reference/{path.name.removesuffix('.schema.json')}.md"
        _pages[uri] = text
        short, _, checks = title.partition(" (")
        _schemas.append((short, uri, checks.rstrip(")")))
        if schemas is not None:
            schemas.append({short: uri})

    def drop_empty(items):  # a section left with no page
        items[:] = [item for item in items if not (isinstance(item, dict) and any(v == [] for v in item.values()))]

    _walk(config.nav, drop_empty)
    return config


def on_files(files, config):
    for uri, text in _pages.items():
        file = File.generated(config, uri, content=text)
        file.edit_uri = None  # its source is not in docs/
        files.append(file)
    return files


def on_page_markdown(markdown, page, config, files):
    here = posixpath.dirname(page.file.src_uri) or "."

    def listing(_match) -> str:
        items = []
        for short, uri, checks in _schemas:
            items.append(f"- [{short}]({posixpath.relpath(uri, here)})" + (f" (`{checks}`)" if checks else ""))
        return "\n".join(items)

    return re.sub(r"^<!--\s*schema-list\s*-->\s*$", listing, markdown, flags=re.M)
