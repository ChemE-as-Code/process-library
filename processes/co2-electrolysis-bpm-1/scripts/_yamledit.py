"""Targeted text edits of hand-maintained YAML files (#330 scripts).

pyyaml would drop the comments of a file it rewrites, so scripts/regen.py replaces the text of
single values in place, as core's ``set_dimensions`` and ``set_duty_volume`` do: it locates
each value's node with ``yaml.compose`` and splices in the new value as flow-style text. Every
edit is then checked: the new file, loaded, must equal the old file loaded with exactly those
values replaced, or nothing is written (``EditRefused``). Only scalar and flow-style values
are replaced; a block-style target is refused rather than reformatted.
"""

from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path
from typing import Any

import yaml

#: a path element: a mapping key, a sequence index, or ``("id", value)``: the sequence item
#: whose ``id`` is *value*
PathItem = str | int | tuple[str, str]


class EditRefused(RuntimeError):
    """A targeted edit that would change more (or other) than the values it names."""


_PLAIN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-/ ]*$")
_RESERVED = {"true", "false", "yes", "no", "on", "off", "null", "y", "n", "~"}


def number(x: float, digits: int = 10) -> str:
    """A float as YAML text that reads back as a float (pyyaml needs a dot before an exponent)."""
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    if not math.isfinite(x):
        raise ValueError(f"not a finite number: {x}")
    if x == 0:
        return "0.0"
    text = format(x, f".{digits}g")
    if "e" in text:
        mantissa, exponent = text.split("e")
        if "." not in mantissa:
            mantissa += ".0"
        text = f"{mantissa}e{exponent}"
    elif "." not in text:
        text += ".0"
    return text


def flow(value: Any, digits: int = 10) -> str:
    """*value* (dict, list, str, number, bool, None) as one line of flow-style YAML."""
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_key(k)}: {flow(v, digits)}" for k, v in value.items()) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(flow(v, digits) for v in value) + "]"
    if value is None:
        return "null"
    if isinstance(value, (bool, int, float)):
        return number(value, digits)
    text = str(value)
    if _PLAIN.match(text) and text.lower() not in _RESERVED and not text.endswith(" "):
        return text
    return json.dumps(text, ensure_ascii=False)


def _key(k: Any) -> str:
    text = str(k)
    return text if _PLAIN.match(text) and " " not in text else json.dumps(text)


def _child(node: yaml.Node, item: PathItem) -> yaml.Node:
    if isinstance(item, tuple):
        field, wanted = item
        if not isinstance(node, yaml.SequenceNode):
            raise EditRefused(f"{item!r}: not a sequence")
        for entry in node.value:
            if isinstance(entry, yaml.MappingNode) and any(
                getattr(k, "value", None) == field and getattr(v, "value", None) == str(wanted)
                for k, v in entry.value
            ):
                return entry
        raise EditRefused(f"no item with {field} {wanted}")
    if isinstance(item, int):
        if not isinstance(node, yaml.SequenceNode) or item >= len(node.value):
            raise EditRefused(f"no index {item}")
        return node.value[item]
    if not isinstance(node, yaml.MappingNode):
        raise EditRefused(f"{item!r}: not a mapping")
    for k, v in node.value:
        if getattr(k, "value", None) == item:
            return v
    raise EditRefused(f"no key {item}")


def _node(root: yaml.Node, path: list[PathItem]) -> yaml.Node:
    node = root
    for item in path:
        node = _child(node, item)
    return node


def _set(data: Any, path: list[PathItem], value: Any) -> None:
    target = data
    for item in path[:-1]:
        target = _get(target, item)
    last = path[-1]
    if isinstance(last, tuple):
        raise EditRefused("the last path item names a value, not an item")
    target[last] = value


def _get(data: Any, item: PathItem) -> Any:
    if isinstance(item, tuple):
        field, wanted = item
        return next(e for e in data if isinstance(e, dict) and str(e.get(field)) == str(wanted))
    return data[item]


def edit_text(text: str, changes: list[tuple[list[PathItem], Any]], digits: int = 10) -> str:
    """*text* with each (path, value) replaced in place; refuses any other difference."""
    root = yaml.compose(text)
    spans = []
    for path, value in changes:
        node = _node(root, path)
        if isinstance(node, (yaml.MappingNode, yaml.SequenceNode)) and not node.flow_style:
            raise EditRefused(f"{path}: a block-style value is not replaced in place")
        spans.append((node.start_mark.index, node.end_mark.index, flow(value, digits)))
    spans.sort()
    for (_, end_a, _), (start_b, _, _) in zip(spans, spans[1:], strict=False):
        if start_b < end_a:
            raise EditRefused("overlapping edits")
    new = text
    for start, end, body in reversed(spans):
        new = new[:start] + body + new[end:]
    expected = copy.deepcopy(yaml.safe_load(text))
    for path, value in changes:
        _set(expected, path, yaml.safe_load(flow(value, digits)))
    if yaml.safe_load(new) != expected:
        raise EditRefused("the edit changes more than the named values")
    return new


def edit_file(path: Path, changes: list[tuple[list[PathItem], Any]], digits: int = 10) -> bool:
    """Apply *changes* to *path*; True when the file changed."""
    text = path.read_text(encoding="utf-8")
    new = edit_text(text, changes, digits)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def get(data: Any, path: list[PathItem]) -> Any:
    target = data
    for item in path:
        target = _get(target, item)
    return target
