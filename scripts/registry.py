"""The chemicals and products registry and the family taxonomy: the rules the build scripts share.

``chemicals/chemicals.yaml`` (schema ``schemas/chemicals.schema.json``) holds substances,
mixtures and utilities by slug, each with optional grades (``<slug>/<grade>``), properties,
classifications and crosswalks; ``taxonomy/families.yaml`` the process families with their ISIC
Rev.4 classes. Rules in docs/registry.md.

- :func:`split` and :func:`flow_grade` resolve what a flow names to a slug and a grade: the
  flow's own ``<slug>/<grade>``, else the registry's ``flow_grades`` entry for
  ``<process>/<inventory_key>``, else no grade (the substance);
- :func:`check` is the build-time validation beyond the schema: CAS check digits, standard
  InChIKeys, molar mass, elemental composition and carbon content against the formula
  (IUPAC 2021 atomic weights), mixture compositions, unique crosswalk names and
  ``flow_grades`` that name a known grade; :func:`unused_flow_grades` finds the entries whose
  ``<process>/<inventory_key>`` no flow has (the catalog build warns);
- :func:`compare_property` compares a study's allocation property with the registry's.

Every script imports it from beside itself (``scripts/`` is on ``sys.path`` when one runs).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

#: IUPAC 2021 abridged standard atomic weights (Prohaska et al. 2022, Pure Appl. Chem. 94:573),
#: for the elements the registry's formulas use; add an element with its abridged value.
ATOMIC_WEIGHTS = {
    "H": 1.0080, "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.95, "K": 39.098,
    "Ca": 40.078, "Ti": 47.867, "Fe": 55.845,
}
#: Relative tolerance of a molar mass against its formula; absolute of a mass fraction.
MOLAR_MASS_TOLERANCE = 1e-3
FRACTION_TOLERANCE = 1e-3
#: A mixture's components given as values must sum to 100 % within this (rounded data).
COMPOSITION_TOLERANCE = 0.5
#: A study's allocation property may differ from the registry's by this share before it is a
#: finding (docs/registry.md, "Study properties").
STUDY_TOLERANCE = 0.02
#: Study property (core's ProductProperties, per unit of the product; compared only for a product
#: counted in kg) -> (registry property, factor to kJ/kg).
STUDY_PROPERTIES = {"exergy": ("exergy", 1.0), "energy": ("lhv", 1000.0)}

ELEMENT = re.compile(r"([A-Z][a-z]?)(\d*)")


@dataclass
class Registry:
    chemicals: dict[str, dict]
    #: (slug, grade) -> grade entry
    grades: dict[tuple[str, str], dict] = field(default_factory=dict)
    #: "<process>/<inventory_key>" -> "<slug>/<grade>"
    flow_grades: dict[str, str] = field(default_factory=dict)

    def grade(self, slug: str, grade: str | None) -> dict | None:
        return self.grades.get((slug, grade)) if grade else None

    def properties(self, slug: str, grade: str | None = None) -> dict:
        """The grade's properties over its substance's."""
        own = (self.chemicals.get(slug) or {}).get("properties") or {}
        return {**own, **((self.grade(slug, grade) or {}).get("properties") or {})}


def load(data: dict) -> Registry:
    chemicals = {c["slug"]: c for c in data.get("chemicals", [])}
    grades = {(slug, g["slug"]): g for slug, c in chemicals.items() for g in c.get("grades", [])}
    return Registry(chemicals, grades, dict(data.get("flow_grades") or {}))


def split(ref: str) -> tuple[str, str | None]:
    """``"oxygen/lox"`` -> ``("oxygen", "lox")``; ``"oxygen"`` -> ``("oxygen", None)``."""
    slug, _, grade = ref.partition("/")
    return slug, grade or None


def flow_grade(registry: Registry, pid: str, item: dict) -> tuple[str, str | None, str | None]:
    """A flow's ``(slug, grade, problem)``. The flow's own grade wins; ``flow_grades`` fills it
    in for a flow that names only the substance; a conflict between the two is a problem."""
    slug, grade = split(item["chemical"])
    mapped = registry.flow_grades.get(f"{pid}/{item['inventory_key']}") if item.get("inventory_key") else None
    problem = None
    if mapped:
        mapped_slug, mapped_grade = split(mapped)
        if mapped_slug != slug:
            problem = f"flow_grades maps {item['inventory_key']} to {mapped}, but the flow is {item['chemical']}"
        elif grade and mapped_grade != grade:
            problem = f"flow_grades maps {item['inventory_key']} to {mapped}, but the flow names grade {grade!r}"
        else:
            grade = mapped_grade
    if grade and (slug, grade) not in registry.grades and slug in registry.chemicals:
        problem = problem or f"unknown grade {slug}/{grade} (add it under grades of {slug} in chemicals/chemicals.yaml)"
    return slug, grade, problem


# --- validation ------------------------------------------------------------------------------


def cas_valid(cas: str) -> bool:
    """The CAS check digit: the other digits, from the right, times 1, 2, 3, ..., mod 10."""
    digits = cas.replace("-", "")
    if not re.fullmatch(r"\d{5,10}", digits):
        return False
    body, check = digits[:-1], int(digits[-1])
    return sum(int(d) * i for i, d in enumerate(reversed(body), start=1)) % 10 == check


def inchikey_problem(key: str) -> str | None:
    """None for a standard InChIKey (14-10-1 letters, flag S and version A in the second block)."""
    if not re.fullmatch(r"[A-Z]{14}-[A-Z]{10}-[A-Z]", key):
        return "is not 14-10-1 upper-case letters"
    if key[23:25] != "SA":
        return "is not a standard InChIKey (the second block must end in SA)"
    return None


def parse_formula(formula: str) -> dict[str, int]:
    """``"CH4"`` -> ``{"C": 1, "H": 4}``; raise ValueError for what this simple parser cannot read
    (brackets, charges, hydrates) or an element without an atomic weight here."""
    if not re.fullmatch(r"(?:[A-Z][a-z]?\d*)+", formula):
        raise ValueError(f"formula {formula!r} is not elements and counts")
    counts: dict[str, int] = {}
    for element, count in ELEMENT.findall(formula):
        if element not in ATOMIC_WEIGHTS:
            raise ValueError(f"formula {formula!r}: no atomic weight of {element} in registry.ATOMIC_WEIGHTS")
        counts[element] = counts.get(element, 0) + int(count or 1)
    return counts


def molar_mass(formula: str) -> float:
    return sum(ATOMIC_WEIGHTS[e] * n for e, n in parse_formula(formula).items())


def mass_fractions(formula: str) -> dict[str, float]:
    total = molar_mass(formula)
    return {e: ATOMIC_WEIGHTS[e] * n / total for e, n in parse_formula(formula).items()}


def _check_properties(where: str, properties: dict, formula: str | None, problems: list[str]) -> None:
    if not formula:
        return
    try:
        expected_mass, fractions = molar_mass(formula), mass_fractions(formula)
    except ValueError as failure:
        problems.append(f"{where}: {failure}")
        return
    given = (properties.get("molar_mass") or {}).get("value")
    if given is not None and abs(given - expected_mass) > MOLAR_MASS_TOLERANCE * expected_mass:
        problems.append(f"{where}: molar_mass {given} g/mol differs from {expected_mass:.3f} of the formula {formula}")
    composition = (properties.get("elemental_composition") or {}).get("value")
    if composition is not None:
        elements = set(composition) | set(fractions)
        wrong = [e for e in sorted(elements) if abs(composition.get(e, 0.0) - fractions.get(e, 0.0)) > FRACTION_TOLERANCE]
        if wrong:
            problems.append(f"{where}: elemental_composition of {', '.join(wrong)} differs from the formula {formula}")
    carbon = (properties.get("carbon_content") or {}).get("value")
    if carbon is not None and abs(carbon - fractions.get("C", 0.0)) > FRACTION_TOLERANCE:
        problems.append(f"{where}: carbon_content {carbon} differs from {fractions.get('C', 0.0):.4f} of the formula {formula}")


def _check_composition(where: str, composition: dict | None, chemicals: dict, problems: list[str]) -> None:
    if not composition:
        return
    percent = [c["value"] for c in composition["components"] if "value" in c and c["unit"].endswith("%")]
    every = all("value" in c for c in composition["components"])
    if every and percent and abs(sum(percent) - 100.0) > COMPOSITION_TOLERANCE:
        problems.append(f"{where}: composition sums to {sum(percent):g} %, not 100 %")
    for component in composition["components"]:
        if "chemical" in component and component["chemical"] not in chemicals:
            problems.append(f"{where}: composition names unknown chemical {component['chemical']!r}")
        low, high = (component.get("range") or [0, 0])
        if low > high:
            problems.append(f"{where}: composition range of {component.get('chemical') or component.get('component')} is reversed")


def check(registry: Registry) -> list[str]:
    """Problems the schema cannot see, each ``"<where>: <message>"``; empty when the registry is sound."""
    problems: list[str] = []
    owners: dict[tuple[str, str], list[str]] = {}
    for slug, chem in sorted(registry.chemicals.items()):
        where = f"chemicals.{slug}"
        if chem.get("cas") and not cas_valid(chem["cas"]):
            problems.append(f"{where}: CAS {chem['cas']} fails its check digit")
        if chem.get("inchikey") and (why := inchikey_problem(chem["inchikey"])):
            problems.append(f"{where}: InChIKey {chem['inchikey']} {why}")
        _check_properties(where, chem.get("properties") or {}, chem.get("formula"), problems)
        _check_composition(where, chem.get("composition"), registry.chemicals, problems)
        for db, names in (chem.get("crosswalk") or {}).items():
            for name in names:
                owners.setdefault((db, name), []).append(slug)
        seen: set[str] = set()
        for grade in chem.get("grades", []):
            ref = f"{slug}/{grade['slug']}"
            if grade["slug"] in seen:
                problems.append(f"{where}: grade {grade['slug']!r} appears twice")
            seen.add(grade["slug"])
            _check_composition(f"chemicals.{ref}", grade.get("composition"), registry.chemicals, problems)
            for db, names in (grade.get("crosswalk") or {}).items():
                for name in names:
                    owners.setdefault((db, name), []).append(ref)
    for (db, name), refs in sorted(owners.items()):
        if len(refs) > 1:
            problems.append(f"crosswalk: {db} name {name!r} belongs to more than one entry ({', '.join(refs)})")
    for key, ref in sorted(registry.flow_grades.items()):
        slug, grade = split(ref)
        if (slug, grade) not in registry.grades:
            problems.append(f"flow_grades.{key}: unknown grade {ref}")
    return problems


def unused_flow_grades(registry: Registry, flow_keys: set[str]) -> list[str]:
    """The ``flow_grades`` keys that name no ``<process>/<inventory_key>`` of a flow in
    *flow_keys*: left over after a rename, or after the process named the grade itself."""
    return sorted(set(registry.flow_grades) - flow_keys)


# --- studies ---------------------------------------------------------------------------------


def compare_property(registry: Registry, slug: str, grade: str | None, name: str, study_value: float | None, unit: str = "kg") -> dict | None:
    """A study's allocation property (core's ``ProductProperties`` field *name*, per *unit* of
    the product) against the registry: ``{property, study, registry, unit, status}`` with status
    ``match``, ``mismatch`` or ``unchecked`` (the registry has no value, or the product is not
    counted in kg: the registry's values are per kg, and a volume or a piece is not converted),
    or None when the study has none."""
    if study_value is None or name not in STUDY_PROPERTIES:
        return None
    registry_name, factor = STUDY_PROPERTIES[name]
    entry = registry.properties(slug, grade).get(registry_name)
    result = {"property": name, "study": study_value, "registry": None, "unit": f"kJ/{unit}", "status": "unchecked"}
    if unit != "kg":
        return {**result, "note": f"the product is counted in {unit}; the registry's values are per kg"}
    if entry is None:
        return result
    expected = entry["value"] * factor
    result["registry"] = expected
    differs = abs(study_value - expected) > STUDY_TOLERANCE * abs(expected) if expected else study_value != 0
    result["status"] = "mismatch" if differs else "match"
    return result


# --- taxonomy --------------------------------------------------------------------------------


def load_families(path: Path) -> dict[str, dict]:
    """``taxonomy/families.yaml`` by slug (empty when the file is missing)."""
    if not path.is_file():
        return {}
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {f["slug"]: f for f in data.get("families", [])}
