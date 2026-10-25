"""MkDocs hook: pages generated from the library itself, and nav entries that may be missing.

- ``processes/<id>.md``, one page per ``processes/*/process.yaml``: the manifest's key facts and
  the process folder's README.md (included through docs/hooks/includes.py). Each is added to the
  nav section "Processes".
- ``reference/<name>.md``, one page per ``schemas/<name>.schema.json``: a field table of every
  object in the schema. Each is added to the nav section "Schemas".
- Nav entries listed in OPTIONAL are dropped while their page does not exist, so the nav may name
  pages that other changes add.

Generated pages have no edit link (their sources are not in docs/).
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from mkdocs.structure.files import File

OPTIONAL = {"system-model.md", "governance.md", "coverage.md"}

_root = Path(".")
_blob = ""  # GitHub URL prefix of repository files
_pages: dict[str, str] = {}  # src_uri -> Markdown


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
    keys = ("pattern", "format", "minLength", "maxLength", "minItems", "minimum", "exclusiveMinimum")
    out = [f"{k}: {_code(node[k])}" for k in keys if k in node]
    if node.get("uniqueItems"):
        out.append("unique")
    return "; ".join(out)


def _rows(node: dict, prefix: str = "") -> list[str]:
    rows, required = [], set(node.get("required", []))
    for name, child in node.get("properties", {}).items():
        path = prefix + name
        doc = _escape(child.get("description", ""))
        extra = _constraints(child) or _constraints(child.get("items", {}))
        cells = [f"`{path}`", _type(child), "yes" if name in required else "", doc, _escape(extra)]
        rows.append("| " + " | ".join(cells) + " |")
        if "properties" in child:
            rows += _rows(child, path + ".")
        elif "properties" in child.get("items", {}):
            rows += _rows(child["items"], path + "[].")
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
        "Fields not listed are not allowed where the object sets `additionalProperties: false`.",
        "",
        _table(schema),
    ]
    for name, node in schema.get("$defs", {}).items():
        parts += ["", f"## {name}", ""]
        if "description" in node:
            parts += [node["description"], ""]
        parts.append(_table(node) if "properties" in node else f"{_type(node)}. {_escape(_constraints(node))}")
    return title, "\n".join(parts) + "\n"


def _first_heading(readme: Path) -> str | None:
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line
    return None


def _process_page(folder: Path) -> tuple[str, str]:
    manifest = yaml.safe_load((folder / "process.yaml").read_text(encoding="utf-8")) or {}
    pid = manifest.get("id", folder.name)
    title = manifest.get("title", pid)
    rel = folder.relative_to(_root).as_posix()
    facts = [
        ("id", f"`{pid}`"),
        ("maturity", f"`{manifest.get('maturity', '')}`"),
        ("review", f"`{(manifest.get('validation') or {}).get('status', '')}`"),
        ("publication", f"`{(manifest.get('publication') or {}).get('status', 'internal')}`"),
        ("families", ", ".join(f"`{f}`" for f in manifest.get("families", []))),
        ("capacity", _escape((manifest.get("basis") or {}).get("capacity", ""))),
    ]
    parts = [f"# {title}", "", _escape(manifest.get("summary", "")), "", "| | |", "|---|---|"]
    parts += [f"| {k} | {v} |" for k, v in facts if v.strip("`")]
    parts += ["", f"From [`{rel}/process.yaml`]({_blob}{rel}/process.yaml) (the Atlas manifest).", ""]
    readme = folder / "README.md"
    if readme.is_file() and (heading := _first_heading(readme)):
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


def on_config(config):
    global _root, _blob
    _root = Path(config.config_file_path).parent
    _blob = (config.repo_url or "").rstrip("/") + "/blob/main/"
    docs = Path(config.docs_dir)
    _pages.clear()

    def missing(item) -> bool:  # an optional page that does not exist (yet)
        targets = item.values() if isinstance(item, dict) else [item]
        return any(t in OPTIONAL and not (docs / t).is_file() for t in targets if isinstance(t, str))

    def prune(items):
        items[:] = [item for item in items if not missing(item)]

    _walk(config.nav, prune)

    processes = _section(config.nav, "Processes")
    for folder in sorted(p.parent for p in (_root / "processes").glob("*/process.yaml")):
        title, text = _process_page(folder)
        uri = f"processes/{folder.name}.md"
        _pages[uri] = text
        if processes is not None:
            processes.append({title: uri})

    schemas = _section(config.nav, "Schemas")
    for path in sorted((_root / "schemas").glob("*.schema.json")):
        title, text = _schema_page(path)
        uri = f"reference/{path.name.removesuffix('.schema.json')}.md"
        _pages[uri] = text
        if schemas is not None:
            schemas.append({title.split(" (")[0]: uri})

    def drop_empty(items):  # a section left with no page
        items[:] = [item for item in items if not (isinstance(item, dict) and any(v == [] for v in item.values()))]

    _walk(config.nav, drop_empty)
    return config


def on_files(files, config):
    for uri, text in _pages.items():
        file = File.generated(config, uri, content=text)
        file.edit_uri = None
        files.append(file)
    return files
