"""Reactions: every reaction the library's processes carry, the same reaction once.

``build_catalog.py`` writes them to ``reactions.json`` from each catalogued process's
``process/reactions.yaml`` (core's ``cheme/reactions/v1``), with the components of
``process/materials.yaml`` and the catalysts of ``process/catalysts.yaml``. Everything is read
from what the processes already have, which ``cheme validate`` checks in each folder; nothing is
estimated here.

The same reaction (:func:`build`): the same species with the same coefficients, up to a common
factor (``2 H2 + O2 -> 2 H2O`` is ``H2 + 0.5 O2 -> H2O``). A species is its component's CAS
number; a component without one stays its process's own (``<process>/<id>``), so pseudo
components (lignin, lumped heavy ends) are never merged across processes, and one CAS number
twice in a reaction (a phase change) is told apart by the component's phase. Direction counts
only for an irreversible reaction: ``A <=> B`` is ``B <=> A``, ``A -> B`` is not ``B -> A``; a
reversible and an irreversible statement of one stoichiometry are two reactions, linked as each
other's ``variants``. Each occurrence keeps what its process says: id, title, equation as
written, conversion, heat of reaction (and its value for the merged equation, ``per_equation``),
equilibrium constant, rate, catalyst (with its catalysts.yaml entry and window), phase,
sources and element balance.

The element balance (``balance``, :func:`_balance`) is core's (``cheme check``'s
``cheme.reaction-element-balance``): the atoms of each element, summed over the process's own
stoichiometry with the formulas of its ``materials.yaml``, change by no more than 1e-9
(``balanced``) or do (``unbalanced``, with the change per element); a component that is not in
``materials.yaml``, has no formula, or has one core's ``parse_formula`` does not read (a charge,
a hydrate, an element outside its table) makes it ``not-checkable``, never ``balanced``. The
parser is core's when ``chemeascode`` is importable, else :func:`parse_formula`, a copy of it
(``tests/test_reactions.py`` compares the two). A reaction's ``balance`` counts its processes
(:func:`_balance_summary`); ``has_sources`` says whether any occurrence cites a source.

A species maps to the registry chemical (``chemicals/chemicals.yaml``) with its component's CAS
number; otherwise it has no chemical. It is shown by its formula when it has a CAS number,
else by its component id. Its formula and name are not the first process's (:func:`_label`):
the registry's when it has the chemical, else the formula most processes write (on a tie
``Ca(OH)2`` before ``CaH2O2``, ``SO2`` before ``O2S``) and the name without a process's own note in brackets ("Calcium
carbonate (lime mud)" is "Calcium carbonate"); each occurrence keeps its process's own names
(``names``).

The slug is made from the merged equation (formulas in one order, :func:`_canonical`,
coefficients, ``to`` or ``eq``), so it stays the same as long as the reaction does, however a process spells a formula
(``Ca(OH)2``, ``CaH2O2``); one too long, or shared by two reactions (same formulas, different
species: isomers), gets a hash of the reaction instead of its tail.

Templates (optional, ``--cheme``): a reaction whose stoichiometry is one of the toolkit's
reaction library (``cheme chemistry library``), in the same direction unless one of the two is
reversible, names that entry, so a reader can start a process of their own from it. Without
the command, ``templates`` is null.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from publication import excluded, snapshot_excludes

REACTIONS = "process/reactions.yaml"
MATERIALS = "process/materials.yaml"
CATALYSTS = "process/catalysts.yaml"
REACTIONS_SCHEMA = "cheme/reactions/v1"
#: What the Atlas shows as the command of a template (``{entry}``: its id).
TEMPLATE_COMMAND = "cheme chemistry library {entry} --add"
#: A slug longer than this keeps its head and ends in the reaction's hash.
MAX_SLUG = 80
#: The catalyst fields the catalog publishes (core's ``cheme/catalysts/v1``).
CATALYST_FIELDS = ("id", "name", "active_phase", "promoters", "support", "window", "poisons", "sources")

Key = tuple[tuple[str, Fraction | float], ...]


#: The elements core's ``parse_formula`` reads (the keys of its ``formulas.ATOMIC_MASS``).
FORMULA_ELEMENTS = frozenset(
    "H He Li B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Ti V Cr Mn Fe Co Ni Cu Zn Br Kr Mo Ru Rh Pd Ag I Xe Pt".split()
)
#: An element change larger than this is unbalanced (core's ``element_change``).
BALANCE_TOLERANCE = 1e-9
_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)|(\()|(\))(\d*)")


def parse_formula(formula: str) -> dict[str, int] | None:
    """Atoms per element of a molecular formula (``C2H6O``, ``Ca(OH)2``); None when the text is
    no formula core reads (charges, hydrates, isotopes, an element outside
    :data:`FORMULA_ELEMENTS`). A copy of core's ``chemistry.formulas.parse_formula``."""
    text = formula.replace(" ", "")
    if not text:
        return None
    stack: list[dict[str, int]] = [{}]
    at = 0
    while at < len(text):
        match = _FORMULA_TOKEN.match(text, at)
        if match is None:
            return None
        element, count, opening, closing, multiplier = match.groups()
        if element:
            if element not in FORMULA_ELEMENTS:
                return None
            top = stack[-1]
            top[element] = top.get(element, 0) + int(count or 1)
        elif opening:
            stack.append({})
        elif closing:
            if len(stack) < 2:
                return None
            group = stack.pop()
            for name, n in group.items():
                stack[-1][name] = stack[-1].get(name, 0) + n * int(multiplier or 1)
        at = match.end()
    if len(stack) != 1 or not stack[0]:
        return None
    return stack[0]


def _parser():
    """Core's ``parse_formula`` when ``chemeascode`` is importable, else :func:`parse_formula`."""
    try:
        from chemeascode.domains.chemistry.formulas import parse_formula as core
    except ImportError:
        return parse_formula
    return core


def _balance(stoichiometry: dict, components: dict[str, dict], withheld: bool = False, parse=parse_formula) -> dict:
    """The element balance of a reaction as its process writes it (module docstring):
    ``status``, ``change`` (element -> atoms created; ``unbalanced`` only) and ``missing``, the
    components it could not count, each with its ``reason``: ``no-component`` (not in
    materials.yaml), ``no-formula``, ``unreadable`` (with the ``formula``), or ``withheld`` (a
    public build that does not publish materials.yaml)."""
    missing: list[dict] = []
    change: dict[str, float] = {}
    for local, nu in stoichiometry.items():
        component = None if withheld else components.get(local)
        formula = (component or {}).get("formula")
        formula = "" if formula is None else str(formula)
        atoms = parse(formula) if formula.strip() else None
        if atoms is None:
            reason = "withheld" if withheld else "no-component" if component is None else "unreadable" if formula.strip() else "no-formula"
            missing.append({"component": local, "formula": formula if reason == "unreadable" else None, "reason": reason})
            continue
        for element, n in atoms.items():
            change[element] = change.get(element, 0.0) + float(nu) * n
    if missing:
        return {"status": "not-checkable", "change": {}, "missing": missing}
    change = {e: _number(round(v, 9)) for e, v in sorted(change.items()) if abs(v) > BALANCE_TOLERANCE}
    return {"status": "unbalanced" if change else "balanced", "change": change, "missing": []}


def _balance_summary(rows: list[dict]) -> dict:
    """A reaction's balance over its processes (a process can state it more than once): a
    process is ``unbalanced`` when any of its statements is, ``balanced`` when every one is,
    else ``not_checkable``. The reaction is ``unbalanced`` in any process, ``balanced`` in every
    one, ``not-checkable`` when no process balances, else ``partial`` (balanced where it could
    be checked); with the counts of processes and the ``reasons`` (``_balance``'s) why a
    statement could not be checked."""
    by_process: dict[str, set[str]] = {}
    for r in rows:
        by_process.setdefault(r["process"], set()).add(r["balance"]["status"])
    counts = Counter(
        "unbalanced" if "unbalanced" in states else "balanced" if states == {"balanced"} else "not_checkable"
        for states in by_process.values()
    )
    status = (
        "unbalanced" if counts["unbalanced"]
        else "balanced" if counts["balanced"] == len(by_process)
        else "not-checkable" if not counts["balanced"]
        else "partial"
    )
    reasons = sorted({m["reason"] for r in rows for m in r["balance"]["missing"]})
    return {"status": status, "balanced": counts["balanced"], "unbalanced": counts["unbalanced"], "not_checkable": counts["not_checkable"], "reasons": reasons}


def _cited(value: Any) -> bool:
    """Whether a source field says anything: a non-blank text, or a list holding one."""
    if isinstance(value, (list, tuple)):
        return any(_cited(v) for v in value)
    return isinstance(value, str) and bool(value.strip())


def _has_sources(row: dict) -> bool:
    """Whether an occurrence cites a source: for the reaction, its conversion, its heat of
    reaction or its catalyst (the catalysts.yaml entry's); a blank text is none (as the Atlas
    reads them)."""
    return (
        _cited(row["sources"])
        or _cited((row["conversion"] or {}).get("source"))
        or _cited((row["heat_of_reaction"] or {}).get("source"))
        or _cited(((row["catalyst"] or {}).get("entry") or {}).get("sources"))
    )


def _yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _normalise(coefficients: dict[str, float]) -> tuple[dict[str, Fraction | float], float]:
    """The smallest whole coefficients of the same reaction, and the factor that makes them.

    Coefficients that are not ratios of small numbers are scaled to make the smallest one 1.
    """
    fractions = {s: Fraction(c).limit_denominator(1000) for s, c in coefficients.items()}
    if all(abs(float(f) - c) <= 1e-9 * max(1.0, abs(c)) for (s, c), f in zip(coefficients.items(), fractions.values())):
        lcm = math.lcm(*(f.denominator for f in fractions.values()))
        gcd = math.gcd(*(int(f * lcm) for f in fractions.values()))
        factor = Fraction(lcm, gcd)
        return {s: f * factor for s, f in fractions.items()}, float(factor)
    factor = 1.0 / min(abs(c) for c in coefficients.values())
    return {s: round(c * factor, 6) for s, c in coefficients.items()}, factor


def _number(value: Fraction | float) -> int | float:
    if isinstance(value, Fraction) and value.denominator == 1:
        return int(value)
    value = float(value)
    return int(value) if value.is_integer() else value


def _key(coefficients: dict[str, Fraction | float]) -> Key:
    return tuple(sorted(coefficients.items()))


def _flip(key: Key) -> Key:
    return tuple((s, -c) for s, c in key)


def _unoriented(key: Key) -> Key:
    return min(key, _flip(key))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def _slug_part(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", label.lower()) or "x"


def _coefficient_text(value: Fraction | float) -> str:
    number = abs(_number(value))
    return "" if number == 1 else f"{number:g}"


def _equation(species: list[dict], reversible: bool) -> str:
    side = lambda sign: " + ".join(  # noqa: E731
        f"{_coefficient_text(s['coefficient'])} {s['label']}".strip() for s in species if (s["coefficient"] > 0) == sign
    )
    return f"{side(False)} {'<=>' if reversible else '->'} {side(True)}"


#: IUPAC's element sequence (Red Book 2005, Table VI), least electronegative first: the order a
#: formula is written in when not organic (:func:`_canonical`): NaCl, SO2, NH3, H2SO4, CaCO3.
ELEMENT_SEQUENCE = (
    "Rn Xe Kr Ar Ne He Fr Cs Rb K Na Li Ra Ba Sr Ca Mg Be "
    "Lr No Md Fm Es Cf Bk Cm Am Pu Np U Pa Th Ac Lu Yb Tm Er Ho Dy Tb Gd Eu Sm Pm Nd Pr Ce La Y Sc "
    "Rf Hf Zr Ti Db Ta Nb V Sg W Mo Cr Bh Re Tc Mn Hs Os Ru Fe Mt Ir Rh Co Ds Pt Pd Ni Rg Au Ag Cu "
    "Cn Hg Cd Zn Tl In Ga Al B Pb Sn Ge Si C Bi Sb As P N H Po Te Se S O At I Br Cl F"
).split()


def _canonical(formula: str) -> str:
    """*formula* in one order however a process writes it, brackets multiplied out
    (``Ca(OH)2`` and ``CaH2O2`` are ``CaH2O2``): an organic one (C and H) in Hill order (C, H,
    then alphabetically), any other in :data:`ELEMENT_SEQUENCE` (``SO2``, not ``O2S``). A
    formula it cannot read is returned as it is."""
    if not re.fullmatch(r"(?:[A-Z][a-z]?\d*|\(|\)\d*)+", formula):
        return formula
    stack: list[Counter] = [Counter()]
    for element, count, bracket, multiple in re.findall(r"([A-Z][a-z]?)(\d*)|([()])(\d*)", formula):
        if element:
            stack[-1][element] += int(count or 1)
        elif bracket == "(":
            stack.append(Counter())
        elif len(stack) > 1:
            inner = stack.pop()
            for e, n in inner.items():
                stack[-1][e] += n * int(multiple or 1)
        else:
            return formula
    if len(stack) != 1:
        return formula
    atoms = stack[0]
    if "C" in atoms and "H" in atoms:
        order = ["C", "H", *sorted(e for e in atoms if e not in ("C", "H"))]
    else:
        order = sorted(atoms, key=lambda e: (ELEMENT_SEQUENCE.index(e) if e in ELEMENT_SEQUENCE else len(ELEMENT_SEQUENCE), e))
    return "".join(f"{e}{atoms[e] if atoms[e] > 1 else ''}" for e in order)


def _label(skey: str, seen: list[dict], chemical: dict | None) -> tuple[str, str | None]:
    """A merged species' formula (or component id) and name (module docstring): *seen* has its
    process, component id and component in each occurrence."""
    if not skey.startswith("cas:"):
        return seen[0]["id"], seen[0]["component"].get("name")
    # counted once per process
    formulas = Counter(f for _, f in {(s["process"], s["component"].get("formula")) for s in seen} if f)
    formula = (chemical or {}).get("formula") or (
        # most written; on a tie one with brackets (Ca(OH)2), then the canonical order
        min(formulas, key=lambda f: (-formulas[f], "(" not in f, _canonical(f) != f, f)) if formulas else seen[0]["id"]
    )
    if chemical and chemical.get("name"):
        return formula, chemical["name"]
    # a process's own note on a component ("(lime mud)") is not the species'; one CAS number
    # twice in a reaction keeps it, as it tells the two apart
    names = Counter(
        n if "@" in skey else re.sub(r"\s+\([^()]*\)$", "", n)
        for _, n in {(s["process"], s["component"].get("name")) for s in seen} if n
    )
    return formula, min(names, key=lambda n: (-names[n], n)) if names else None


def _readable_slug(species: list[dict], reversible: bool) -> str:
    def side(sign: bool) -> str:
        parts = sorted((_slug_part(_canonical(s["label"]) if s["cas"] else s["label"]), s["coefficient"]) for s in species if (s["coefficient"] > 0) == sign)
        return "-".join(_coefficient_text(c).replace(".", "p") + label for label, c in parts)

    left, right = side(False), side(True)
    if reversible:
        left, right = sorted((left, right))
    return f"{left}-{'eq' if reversible else 'to'}-{right}"


def _components(folder: Path) -> dict[str, dict]:
    path = folder / MATERIALS
    data = (_yaml(path) or {}) if path.is_file() else {}
    return {c["id"]: c for c in data.get("components") or [] if isinstance(c, dict) and "id" in c}


def _catalysts(folder: Path) -> dict[str, dict]:
    path = folder / CATALYSTS
    data = (_yaml(path) or {}) if path.is_file() else {}
    return {c["id"]: c for c in data.get("catalysts") or [] if isinstance(c, dict) and "id" in c}


def _catalyst(text: str | None, catalysts: dict[str, dict]) -> dict | None:
    """The reaction's catalyst: its text and, when it names one of catalysts.yaml (by id or
    name), that entry."""
    if not text:
        return None
    entry = catalysts.get(text) or next((c for c in catalysts.values() if c.get("name") == text), None)
    return {
        "text": text,
        "id": entry["id"] if entry else None,
        "entry": {k: entry[k] for k in CATALYST_FIELDS if k in entry} if entry else None,
    }


def _model(reaction: dict) -> str | None:
    """How the process models it: kinetics (a rate law or mechanism), conversion, equilibrium
    (reversible, from an equilibrium constant or the components' formation data), or null
    (stoichiometry only)."""
    if reaction.get("rate") or reaction.get("mechanism"):
        return "kinetics"
    if reaction.get("conversion"):
        return "conversion"
    if reaction.get("equilibrium_constant") or reaction.get("reversible"):
        return "equilibrium"
    return None


def _species_keys(owner: str, stoichiometry: dict, components: dict[str, dict]) -> dict[str, str]:
    """Each component id of a reaction -> its species key: ``cas:<CAS>``, or ``<owner>/<id>``
    without one. Two ids of one CAS number in one reaction (a phase change: dissolved and solid
    NaCN) stay apart by the component's phase, else its id."""
    cas = {local: (components.get(local) or {}).get("cas") for local in stoichiometry}
    shared = {c for c in cas.values() if c and list(cas.values()).count(c) > 1}
    return {
        local: f"{owner}/{local}" if not c
        else f"cas:{c}@{(components.get(local) or {}).get('phase') or local}" if c in shared
        else f"cas:{c}"
        for local, c in cas.items()
    }


def _mapped(stoichiometry: dict, keys: dict[str, str]) -> dict[str, float]:
    """Coefficients per species key, without zeros."""
    return {keys[local]: float(c) for local, c in stoichiometry.items() if c != 0}


def load_templates(cli: list[str], report) -> list[dict] | None:
    """The toolkit's reaction library (``cheme chemistry library --json``, then each entry):
    one record per template reaction with its unoriented stoichiometry key; None, with a
    warning, when the command does not answer."""

    def run(*args: str) -> Any:
        done = subprocess.run([*cli, "chemistry", "library", *args, "--json"], capture_output=True, text=True, encoding="utf-8", timeout=120, check=True)
        return json.loads(done.stdout)

    try:
        listing = run()
        entries = [run(entry) for entry in sorted(listing)]
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        report.warn("reactions", f"no template matches: `{' '.join(cli)} chemistry library --json` failed ({type(exc).__name__})")
        return None
    templates = []
    for entry in entries:
        components = {c["id"]: c for c in entry.get("components") or []}
        for reaction in entry.get("reactions") or []:
            coefficients = _mapped(reaction["stoichiometry"], _species_keys(f"template:{entry['id']}", reaction["stoichiometry"], components))
            if not coefficients:
                continue
            templates.append({
                "key": _key(_normalise(coefficients)[0]),
                "reversible": bool(reaction.get("reversible")),
                "entry": entry["id"],
                "title": entry.get("title", ""),
                "reaction": reaction["id"],
                "model_basis": (entry.get("model_basis") or {}).get("kind"),
            })
    return templates


def build(library: Path, details: list[dict], chemicals: dict[str, dict], report, public: bool = False, templates: list[dict] | None = None) -> list[dict]:
    """The reactions of the catalogued processes (*details*: in a public build, the published
    ones only), merged as the module docstring says, sorted by slug."""
    by_cas = {c["cas"]: slug for slug, c in sorted(chemicals.items()) if c.get("cas")}
    parse = _parser()
    seen: dict[str, list[dict]] = defaultdict(list)
    groups: dict[tuple[bool, Key], dict] = {}
    for detail in sorted(details, key=lambda d: d["id"]):
        pid = detail["id"]
        folder = library / "processes" / pid
        path = folder / REACTIONS
        if not path.is_file():
            continue
        excludes = snapshot_excludes(_yaml(folder / "process.yaml")) if public else []
        if excluded(REACTIONS, excludes):
            continue
        where = f"processes/{pid}/{REACTIONS}"
        data = _yaml(path) or {}
        if data.get("schema") != REACTIONS_SCHEMA:
            report.error(where, f"schema {data.get('schema')!r}, expected {REACTIONS_SCHEMA}")
            continue
        withheld = excluded(MATERIALS, excludes)
        components = {} if withheld else _components(folder)
        catalysts = {} if excluded(CATALYSTS, excludes) else _catalysts(folder)
        for number, reaction in enumerate(data.get("reactions") or []):
            stoichiometry = reaction.get("stoichiometry") if isinstance(reaction, dict) else None
            if not isinstance(stoichiometry, dict) or not stoichiometry or not all(
                isinstance(c, (int, float)) and not isinstance(c, bool) for c in stoichiometry.values()
            ):
                report.error(where, f"reactions[{number}]: no stoichiometry of numbers")
                continue
            for local in stoichiometry:
                if local not in components and not excluded(MATERIALS, excludes):
                    report.warn(where, f"{reaction.get('id')}: {local!r} is not a component of {MATERIALS}")
            keys = _species_keys(pid, stoichiometry, components)
            coefficients = _mapped(stoichiometry, keys)
            if not coefficients:
                report.error(where, f"{reaction.get('id')}: every coefficient is zero")
                continue
            normalised, factor = _normalise(coefficients)
            key = _key(normalised)
            reversible = bool(reaction.get("reversible", False))
            if reversible:
                key = _unoriented(key)
            group = groups.setdefault((reversible, key), {"occurrences": [], "species": {}})
            for local, skey in keys.items():
                component = components.get(local) or {}
                seen[skey].append({"process": pid, "id": local, "component": component})
                group["species"].setdefault(skey, {"key": skey, "cas": component.get("cas"), "chemical": by_cas.get(component.get("cas"))})
            # the occurrence's coefficients against the merged ones (negative: written the other way)
            first = next(iter(coefficients))
            orientation = 1 if dict(key)[first] * coefficients[first] > 0 else -1
            group["occurrences"].append({"reaction": reaction, "pid": pid, "detail": detail, "factor": factor * orientation, "order": list(coefficients), "catalysts": catalysts, "keys": keys, "components": components,
                                         "balance": _balance(stoichiometry, components, withheld, parse)})

    for group in groups.values():
        for skey, species in group["species"].items():
            label, name = _label(skey, seen[skey], chemicals.get(species["chemical"]) if species["chemical"] else None)
            group["species"][skey] = {"key": skey, "label": label, "name": name, "cas": species["cas"], "chemical": species["chemical"]}

    distinct = [_distinct(reversible, key, group, templates) for (reversible, key), group in groups.items()]
    slugs = Counter(r["slug"] for r in distinct)
    for item, (reversible, key) in zip(distinct, groups):
        if slugs[item["slug"]] > 1 or len(item["slug"]) > MAX_SLUG:
            item["slug"] = f"{item['slug'][:MAX_SLUG - 9].rstrip('-')}-{_hash(repr((reversible, key)))}"
    by_stoichiometry: dict[Key, list[str]] = defaultdict(list)
    for item, (_, key) in zip(distinct, groups):
        by_stoichiometry[_unoriented(key)].append(item["slug"])
    for item, (_, key) in zip(distinct, groups):
        item["variants"] = sorted(s for s in by_stoichiometry[_unoriented(key)] if s != item["slug"])
    return sorted(distinct, key=lambda r: r["slug"])


def _distinct(reversible: bool, key: Key, group: dict, templates: list[dict] | None) -> dict:
    coefficients = dict(key)
    occurrences = group["occurrences"]
    if reversible:
        # shown the way most processes write it (the first one on a tie)
        ways = Counter(o["factor"] > 0 for o in occurrences)
        if ways[False] > ways[True] or (ways[False] == ways[True] and occurrences[0]["factor"] < 0):
            coefficients = {s: -c for s, c in coefficients.items()}
            for o in occurrences:
                o["factor"] = -o["factor"]
    # species in the first process's order, reactants first
    order = list(dict.fromkeys(s for o in occurrences for s in o["order"]))
    order = [s for s in order if s in coefficients]
    species = [{**group["species"][s], "coefficient": _number(coefficients[s])} for s in order]
    species.sort(key=lambda s: s["coefficient"] > 0)
    rows = [_occurrence(o) for o in occurrences]
    titles = list(dict.fromkeys(r["title"] for r in rows if r["title"]))
    matches = [] if templates is None else sorted(
        ({k: t[k] for k in ("entry", "title", "reaction", "model_basis")} for t in templates if _same(t, reversible, key)),
        key=lambda t: (t["entry"], t["reaction"]),
    )
    return {
        "slug": _readable_slug(species, reversible),
        "equation": _equation(species, reversible),
        "title": titles[0] if titles else None,
        "titles": titles,
        "reversible": reversible,
        "species": species,
        "processes": sorted({r["process"] for r in rows}),
        "families": sorted({f for r in rows for f in r["families"]}),
        "models": sorted({r["model"] or "stoichiometry" for r in rows}),
        "has_catalyst": any(r["catalyst"] for r in rows),
        "has_conversion": any(r["conversion"] for r in rows),
        "has_heat_of_reaction": any(r["heat_of_reaction"] for r in rows),
        "has_sources": any(_has_sources(r) for r in rows),
        "balance": _balance_summary(rows),
        "templates": matches,
        "occurrences": rows,
    }


def _same(template: dict, reversible: bool, key: Key) -> bool:
    """Whether a template states this reaction: the same stoichiometry, in the same direction
    unless one of them is reversible."""
    if reversible or template["reversible"]:
        return _unoriented(template["key"]) == _unoriented(key)
    return template["key"] == key


def _occurrence(o: dict) -> dict:
    reaction, detail, factor = o["reaction"], o["detail"], o["factor"]
    conversion = reaction.get("conversion")
    heat = reaction.get("heat_of_reaction")
    if heat:
        heat = {
            "value": heat["value"],
            "unit": heat.get("unit", "kJ/kmol"),
            "temperature": heat.get("temperature", 298.15),
            "provenance": heat.get("provenance"),
            "source": heat.get("source", ""),
            # per extent of the merged equation as shown
            "per_equation": round(heat["value"] * factor, 6),
        }
    return {
        "process": o["pid"],
        "process_title": detail["title"],
        "maturity": detail["maturity"],
        "validation": detail["validation"]["status"],
        "families": detail["families"],
        "id": reaction.get("id"),
        "title": reaction.get("title") or None,
        "equation": reaction.get("equation") or None,
        "stoichiometry": reaction["stoichiometry"],
        # the process's own component names, by its ids (the merged species have one name each)
        "names": {local: o["components"][local]["name"] for local in reaction["stoichiometry"] if (o["components"].get(local) or {}).get("name")},
        "factor": _number(round(factor, 9)),
        "phase": reaction.get("phase"),
        "model": _model(reaction),
        "conversion": None if not conversion else {
            "key": conversion["key"],
            "species": o["keys"].get(conversion["key"]),
            "value": conversion["value"],
            "provenance": conversion.get("provenance"),
            "source": conversion.get("source", ""),
        },
        "heat_of_reaction": heat or None,
        "equilibrium_constant": reaction.get("equilibrium_constant"),
        "rate": reaction.get("rate"),
        "catalyst": _catalyst(reaction.get("catalyst"), o["catalysts"]),
        "sources": list(reaction.get("sources") or []),
        "balance": o["balance"],
    }
