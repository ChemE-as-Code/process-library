"""Reactions (reactions.json, scripts/reactions.py): every reaction of the processes, the same
reaction once, with each process's statement of it, the registry chemicals and the templates."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_catalog  # noqa: E402
import reactions as rx  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
LIBRARY = FIXTURES / "library"
REACTIONS = FIXTURES / "reactions"
FAKE_CHEME = [sys.executable, str(REACTIONS / "fake_cheme.py")]


@pytest.fixture
def library(tmp_path: Path) -> Path:
    """The fixture library with the reaction files laid over it."""
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    shutil.copytree(REACTIONS / "processes", copy / "processes", dirs_exist_ok=True)
    return copy


def _reactions(library: Path, out: Path, public: bool = False, cheme: list[str] | None = None) -> dict:
    report = build_catalog.build(library, out, None, commit="fixture", public=public, cheme=cheme)
    assert report.errors == []
    return json.loads((out / "reactions.json").read_text(encoding="utf-8"))


def _by_slug(data: dict) -> dict[str, dict]:
    return {r["slug"]: r for r in data["reactions"]}


def _edit(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_the_same_reaction_is_listed_once_with_each_process(library: Path, tmp_path: Path) -> None:
    data = _reactions(library, tmp_path / "out")
    assert data["schema"] == "cheme-as-code/catalog/v1" and data["mode"] == "preview"
    assert data["templates"] is None
    split = _by_slug(data)["2h2o-to-2h2-o2"]
    assert split["equation"] == "2 H2O -> 2 H2 + O2" and split["reversible"] is False
    assert split["processes"] == ["fixture-ammonia", "fixture-electrolysis"]
    assert split["families"] == ["ammonia", "electrolysis", "fertilizers", "hydrogen"]
    ammonia, electrolysis = split["occurrences"]
    # each process keeps its own id, equation and numbers; 4 H2O -> ... is twice the merged one
    assert (ammonia["id"], ammonia["factor"], ammonia["equation"]) == ("SPLIT4", 0.5, "4 H2O -> 4 H2 + 2 O2")
    assert ammonia["heat_of_reaction"]["value"] == 1000000.0 and ammonia["heat_of_reaction"]["per_equation"] == 500000.0
    assert ammonia["heat_of_reaction"]["unit"] == "kJ/kmol" and ammonia["conversion"] is None
    assert ammonia["catalyst"] == {"text": "free-text catalyst", "id": None, "entry": None}
    assert (electrolysis["id"], electrolysis["factor"], electrolysis["model"]) == ("SPLIT", 1, "conversion")
    assert electrolysis["conversion"] == {
        "key": "H2O", "species": "cas:7732-18-5", "value": 0.9, "provenance": "assumed", "source": "synthetic fixture value",
    }
    assert electrolysis["maturity"] == "concept" and electrolysis["validation"] == "unreviewed"
    assert electrolysis["process_title"] == "Fixture: water electrolysis" and electrolysis["sources"] == ["fixture source"]
    assert split["title"] == "Water splitting" and split["titles"] == ["Water splitting"]
    assert (split["has_catalyst"], split["has_conversion"], split["has_heat_of_reaction"]) == (True, True, True)
    assert split["models"] == ["conversion", "stoichiometry"]


def test_species_map_to_registry_chemicals_by_cas(library: Path, tmp_path: Path) -> None:
    split = _by_slug(_reactions(library, tmp_path / "out"))["2h2o-to-2h2-o2"]
    # the fixture registry gives only hydrogen a CAS number
    assert [(s["label"], s["coefficient"], s["chemical"]) for s in split["species"]] == [
        ("H2O", -2, None), ("H2", 2, "hydrogen"), ("O2", 1, None),
    ]
    assert split["species"][1] == {"key": "cas:1333-74-0", "label": "H2", "name": "Hydrogen", "cas": "1333-74-0", "chemical": "hydrogen", "coefficient": 2}


def test_a_component_without_cas_stays_its_process_own(library: Path, tmp_path: Path) -> None:
    oligo = _by_slug(_reactions(library, tmp_path / "out"))["nh3-to-lump"]
    assert [s["key"] for s in oligo["species"]] == ["cas:7664-41-7", "fixture-ammonia/LUMP"]
    assert oligo["species"][1]["label"] == "LUMP" and oligo["species"][1]["chemical"] is None
    assert oligo["models"] == ["stoichiometry"]


def test_a_reversible_reaction_is_one_whichever_way_it_is_written(library: Path, tmp_path: Path) -> None:
    ammonia = _by_slug(_reactions(library, tmp_path / "out"))["2nh3-eq-3h2-n2"]
    assert ammonia["equation"] == "N2 + 3 H2 <=> 2 NH3"  # the first one written, on a tie
    assert [(o["id"], o["factor"]) for o in ammonia["occurrences"]] == [("NH3_SYN", 1), ("NH3_DEC", -1)]
    assert ammonia["occurrences"][0]["heat_of_reaction"]["per_equation"] == -92000.0
    assert ammonia["models"] == ["equilibrium"]


def test_reversible_and_irreversible_statements_are_variants(library: Path, tmp_path: Path) -> None:
    reactions = _by_slug(_reactions(library, tmp_path / "out"))
    burn = reactions["2h2-o2-eq-2h2o"]
    assert burn["equation"] == "2 H2 + O2 <=> 2 H2O" and burn["occurrences"][0]["factor"] == 2
    assert burn["variants"] == ["2h2o-to-2h2-o2"] and reactions["2h2o-to-2h2-o2"]["variants"] == ["2h2-o2-eq-2h2o"]


def test_a_catalyst_of_catalysts_yaml_comes_with_its_window(library: Path, tmp_path: Path) -> None:
    split = _by_slug(_reactions(library, tmp_path / "out"))["2h2o-to-2h2-o2"]
    catalyst = split["occurrences"][1]["catalyst"]
    assert catalyst["text"] == catalyst["id"] == "PT_FIX"
    assert catalyst["entry"]["name"] == "Fixture platinum"
    assert catalyst["entry"]["window"] == {"temperature": [330.0, 360.0], "pressure": [100.0, 3000.0], "provenance": "assumed", "source": "synthetic fixture value"}


def test_a_public_build_has_the_published_processes_only(library: Path, tmp_path: Path) -> None:
    data = _reactions(library, tmp_path / "out", public=True)
    assert data["mode"] == "public"
    assert {p for r in data["reactions"] for p in r["processes"]} == {"fixture-electrolysis"}
    assert sorted(_by_slug(data)) == ["2h2-o2-eq-2h2o", "2h2o-to-2h2-o2"]
    assert all(r["variants"] == [s for s in _by_slug(data) if s != r["slug"]] for r in data["reactions"])
    # a reaction file the publication excludes stays out
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", lambda m: m["publication"]["exclude"].append("process/reactions.yaml"))
    assert _reactions(library, tmp_path / "excluded", public=True)["reactions"] == []
    assert _reactions(library, tmp_path / "preview")["reactions"] != []


@pytest.mark.parametrize("glob", [
    "process/reactions.yaml", "process/**/reactions.yaml", "**/reactions.yaml", "process/react[i]ons.yaml",
    "process/*.yaml", "process/**", "Process/Reactions.yaml",
])
def test_an_excluded_reaction_file_stays_out_of_a_public_build(library: Path, tmp_path: Path, glob: str) -> None:
    # core's export-static globs: ** is zero or more segments, [...] a class, case ignored
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", lambda m: m["publication"]["exclude"].append(glob))
    assert _reactions(library, tmp_path / "out", public=True)["reactions"] == []


@pytest.mark.parametrize("glob", ["process/materials.yaml", "process/catalysts.yaml", "**/catalysts.yaml", "process/[cm]*.yaml"])
def test_an_excluded_materials_or_catalysts_file_is_not_published(library: Path, tmp_path: Path, glob: str) -> None:
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", lambda m: m["publication"]["exclude"].append(glob))
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture", public=True)
    assert report.errors == []
    data = json.loads((tmp_path / "out" / "reactions.json").read_text(encoding="utf-8"))
    occurrences = [o for r in data["reactions"] for o in r["occurrences"]]
    assert occurrences
    if "materials" in glob or "[cm]" in glob:
        # no component of materials.yaml: no CAS number, name or formula, the process's own ids
        assert all(s["cas"] is None and s["name"] is None and s["chemical"] is None for r in data["reactions"] for s in r["species"])
        assert all(o["names"] == {} for o in occurrences)
    if "catalysts" in glob or "[cm]" in glob:
        assert all(o["catalyst"] is None or o["catalyst"]["entry"] is None for o in occurrences)
        assert any(o["catalyst"] for o in occurrences)


def test_formula_spelling_and_a_process_note_do_not_change_a_reaction(library: Path, tmp_path: Path) -> None:
    def respell(m: dict) -> None:
        water = next(c for c in m["components"] if c["id"] == "WATER")
        water.update(formula="OH2", name="Water (feed, demineralised)")

    _edit(library / "processes" / "fixture-ammonia" / "process" / "materials.yaml", respell)
    preview = _by_slug(_reactions(library, tmp_path / "preview"))
    public = _by_slug(_reactions(library, tmp_path / "public", public=True))
    # the same slug with or without the process that spells it otherwise
    split = preview["2h2o-to-2h2-o2"]
    assert "2h2o-to-2h2-o2" in public and split["processes"] == ["fixture-ammonia", "fixture-electrolysis"]
    # the formula most processes write, on a tie the one in the canonical order (H2O, not OH2);
    # the name without the process's note
    assert (split["species"][0]["label"], split["species"][0]["name"]) == ("H2O", "Water")
    assert public["2h2o-to-2h2-o2"]["species"][0]["label"] == "H2O"
    # each process keeps its own names
    assert split["occurrences"][0]["names"]["WATER"] == "Water (feed, demineralised)"


def test_one_order_for_a_formula() -> None:
    # organic: Hill; otherwise IUPAC's element sequence; unreadable: as written
    assert [rx._canonical(f) for f in ("Ca(OH)2", "CaH2O2", "O2S", "CH3COOH", "Al2(SO4)3", "OH2", "NH3", "ClNa", "X(")] == [
        "CaH2O2", "CaH2O2", "SO2", "C2H4O2", "Al2S3O12", "H2O", "NH3", "NaCl", "X(",
    ]


def test_templates_of_the_same_stoichiometry(library: Path, tmp_path: Path) -> None:
    data = _reactions(library, tmp_path / "out", cheme=FAKE_CHEME)
    assert data["templates"] == {"reactions": 2, "entries": 2, "command": "cheme chemistry library {entry} --add"}
    reactions = _by_slug(data)
    assert reactions["2nh3-eq-3h2-n2"]["templates"] == [
        {"entry": "ammonia", "title": "Fixture ammonia synthesis", "reaction": "NH3_SYN", "model_basis": "equilibrium"},
    ]
    # an irreversible template matches a reversible reaction, never the reverse irreversible one
    assert [t["entry"] for t in reactions["2h2-o2-eq-2h2o"]["templates"]] == ["burner"]
    assert reactions["2h2o-to-2h2-o2"]["templates"] == [] and reactions["nh3-to-lump"]["templates"] == []


def test_without_a_working_cheme_there_are_no_templates(library: Path, tmp_path: Path) -> None:
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture", cheme=["no-such-cheme-command"])
    assert report.errors == [] and any("no template matches" in w for w in report.warnings)
    data = json.loads((tmp_path / "out" / "reactions.json").read_text(encoding="utf-8"))
    assert data["templates"] is None and data["reactions"]


def test_build_is_byte_identical(library: Path, tmp_path: Path) -> None:
    for name in ("a", "b"):
        build_catalog.build(library, tmp_path / name, None, commit="fixture", cheme=FAKE_CHEME)
    assert (tmp_path / "a" / "reactions.json").read_bytes() == (tmp_path / "b" / "reactions.json").read_bytes()


def test_a_library_without_reactions_writes_an_empty_list(tmp_path: Path) -> None:
    assert _reactions(LIBRARY, tmp_path / "out")["reactions"] == []


def test_a_phase_change_keeps_both_species(library: Path, tmp_path: Path) -> None:
    folder = library / "processes" / "fixture-electrolysis" / "process"
    _edit(folder / "materials.yaml", lambda m: m["components"].append({"id": "ICE", "name": "Ice", "formula": "H2O", "cas": "7732-18-5", "phase": "solid"}))
    _edit(folder / "reactions.yaml", lambda r: r["reactions"].append({"id": "FREEZE", "equation": "H2O -> H2O(s)", "stoichiometry": {"H2O": -1, "ICE": 1}}))
    freeze = next(r for r in _reactions(library, tmp_path / "out")["reactions"] if r["occurrences"][0]["id"] == "FREEZE")
    assert [s["key"] for s in freeze["species"]] == ["cas:7732-18-5@H2O", "cas:7732-18-5@solid"]


def test_isomers_get_a_hashed_slug(library: Path, tmp_path: Path) -> None:
    folder = library / "processes" / "fixture-ammonia" / "process"
    _edit(folder / "materials.yaml", lambda m: m["components"].extend([
        {"id": "ETOH", "name": "Ethanol", "formula": "C2H6O", "cas": "64-17-5"},
        {"id": "DME", "name": "Dimethyl ether", "formula": "C2H6O", "cas": "115-10-6"},
    ]))
    _edit(folder / "reactions.yaml", lambda r: r["reactions"].extend([
        {"id": "A", "equation": "ETOH -> H2O + ...", "stoichiometry": {"ETOH": -1, "WATER": 1}},
        {"id": "B", "equation": "DME -> H2O + ...", "stoichiometry": {"DME": -1, "WATER": 1}},
    ]))
    slugs = [r["slug"] for r in _reactions(library, tmp_path / "out")["reactions"] if r["slug"].startswith("c2h6o-to-h2o")]
    assert len(slugs) == 2 and len(set(slugs)) == 2 and all(len(s) == len("c2h6o-to-h2o-") + 8 for s in slugs)


def test_a_reaction_without_numbers_is_an_error(library: Path, tmp_path: Path) -> None:
    _edit(library / "processes" / "fixture-ammonia" / "process" / "reactions.yaml", lambda r: r["reactions"].append({"id": "BAD", "stoichiometry": {"HYD": "two"}}))
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    assert any("reactions[5]: no stoichiometry of numbers" in e for e in report.errors)


@pytest.mark.parametrize(
    ("coefficients", "expected", "factor"),
    [
        ({"a": -2, "b": -1, "c": 2}, {"a": -2, "b": -1, "c": 2}, 1.0),
        ({"a": -1, "b": -0.5, "c": 1}, {"a": -2, "b": -1, "c": 2}, 2.0),
        ({"a": -4, "b": 2}, {"a": -2, "b": 1}, 0.5),
        ({"a": -1 / 3, "b": 1}, {"a": -1, "b": 3}, 3.0),
    ],
)
def test_normalise_finds_the_smallest_whole_coefficients(coefficients: dict, expected: dict, factor: float) -> None:
    normalised, got = rx._normalise(coefficients)
    assert {k: rx._number(v) for k, v in normalised.items()} == expected and got == pytest.approx(factor)


@pytest.mark.parametrize(
    ("path", "glob"),
    [
        ("process/reactions.yaml", "process/**/reactions.yaml"),
        ("process/reactions.yaml", "**/reactions.yaml"),
        ("process/reactions.yaml", "process/react[i]ons.yaml"),
        ("process/reactions.yaml", "process/*"),
        ("process/reactions.yaml", "*.yaml"),
        ("reactions.yaml", "*.yaml"),
        ("reviews", "reviews/**"),
        ("process/reactions.yaml", "process/?eactions.yaml"),
        ("process/reactions.yaml", "process"),
    ],
)
def test_excludes_match_as_core_export_static_does(path: str, glob: str) -> None:
    import publication

    export_static = pytest.importorskip("chemeascode.interfaces.api.export_static")
    assert publication.excluded(path, [glob]) == export_static.path_matches(path, glob)


# --- element balance: core's rule (cheme.reaction-element-balance) ----------------------------

def test_each_occurrence_has_its_element_balance(library: Path, tmp_path: Path) -> None:
    reactions = _by_slug(_reactions(library, tmp_path / "out"))
    split = reactions["2h2o-to-2h2-o2"]
    assert [o["balance"] for o in split["occurrences"]] == [{"status": "balanced", "change": {}, "missing": []}] * 2
    assert split["balance"] == {"status": "balanced", "balanced": 2, "unbalanced": 0, "not_checkable": 0, "reasons": []}
    # the fixture's NH3 -> LUMP (C10H20) is synthetic and does not balance: the change as written
    oligo = reactions["nh3-to-lump"]
    assert oligo["occurrences"][0]["balance"] == {"status": "unbalanced", "change": {"C": 10, "H": 17, "N": -1}, "missing": []}
    assert oligo["balance"]["status"] == "unbalanced"


def test_a_missing_or_unreadable_formula_is_not_checkable(library: Path, tmp_path: Path) -> None:
    def strip(m: dict) -> None:
        for c in m["components"]:
            if c["id"] == "OXY":
                del c["formula"]
            if c["id"] == "N2":
                c["formula"] = "N2.H2O"  # a hydrate: core's parser does not read it

    _edit(library / "processes" / "fixture-ammonia" / "process" / "materials.yaml", strip)
    reactions = _by_slug(_reactions(library, tmp_path / "out"))
    split = reactions["2h2o-to-2h2-o2"]
    assert split["occurrences"][0]["balance"] == {
        "status": "not-checkable", "change": {}, "missing": [{"component": "OXY", "formula": None, "reason": "no-formula"}],
    }
    # balanced in one process, not checkable in the other: never "balanced"
    assert split["balance"] == {"status": "partial", "balanced": 1, "unbalanced": 0, "not_checkable": 1, "reasons": ["no-formula"]}
    ammonia = next(r for r in reactions.values() if r["occurrences"][0]["id"] == "NH3_SYN")
    assert ammonia["balance"] == {"status": "not-checkable", "balanced": 0, "unbalanced": 0, "not_checkable": 1, "reasons": ["unreadable"]}
    assert ammonia["occurrences"][0]["balance"]["missing"] == [{"component": "N2", "formula": "N2.H2O", "reason": "unreadable"}]


def test_the_fixtures_formula_less_component_is_not_checkable(library: Path, tmp_path: Path) -> None:
    # the fixture's N2 + O2 -> 2 NO: its NOX component has no formula
    no = next(r for r in _reactions(library, tmp_path / "out")["reactions"] if r["occurrences"][0]["id"] == "NO_FORM")
    assert no["occurrences"][0]["balance"] == {"status": "not-checkable", "change": {}, "missing": [{"component": "NOX", "formula": None, "reason": "no-formula"}]}
    assert no["balance"] == {"status": "not-checkable", "balanced": 0, "unbalanced": 0, "not_checkable": 1, "reasons": ["no-formula"]}
    assert no["has_sources"] is False


def test_a_component_not_in_materials_is_not_checkable(library: Path, tmp_path: Path) -> None:
    _edit(library / "processes" / "fixture-ammonia" / "process" / "reactions.yaml", lambda r: r["reactions"].append(
        {"id": "GHOST", "stoichiometry": {"NH3": -1, "GHOST": 1}}))
    build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    data = json.loads((tmp_path / "out" / "reactions.json").read_text(encoding="utf-8"))
    ghost = next(o for r in data["reactions"] for o in r["occurrences"] if o["id"] == "GHOST")
    assert ghost["balance"]["missing"] == [{"component": "GHOST", "formula": None, "reason": "no-component"}]


def test_a_withheld_materials_file_is_not_checkable(library: Path, tmp_path: Path) -> None:
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", lambda m: m["publication"]["exclude"].append("process/materials.yaml"))
    data = _reactions(library, tmp_path / "out", public=True)
    occurrences = [o for r in data["reactions"] for o in r["occurrences"]]
    assert occurrences and all(o["balance"]["status"] == "not-checkable" for o in occurrences)
    assert {m["reason"] for o in occurrences for m in o["balance"]["missing"]} == {"withheld"}
    assert {tuple(r["balance"]["reasons"]) for r in data["reactions"] if "fixture-electrolysis" in r["processes"]} == {("withheld",)}


def test_the_reaction_balance_counts_processes_not_statements(library: Path, tmp_path: Path) -> None:
    # fixture-ammonia states NH3 synthesis both ways (NH3_SYN, NH3_DEC): one process, two statements
    ammonia = _by_slug(_reactions(library, tmp_path / "out"))["2nh3-eq-3h2-n2"]
    assert [o["process"] for o in ammonia["occurrences"]] == ["fixture-ammonia"] * 2
    assert ammonia["balance"] == {"status": "balanced", "balanced": 1, "unbalanced": 0, "not_checkable": 0, "reasons": []}


def _row(process: str, status: str, reason: str | None = None) -> dict:
    missing = [{"component": "X", "formula": None, "reason": reason}] if reason else []
    return {"process": process, "balance": {"status": status, "change": {}, "missing": missing}}


def test_a_process_balances_only_when_each_of_its_statements_does() -> None:
    summary = rx._balance_summary
    # one process, one statement balanced and one not checkable: not checked, never "balanced"
    assert summary([_row("a", "balanced"), _row("a", "not-checkable", "no-formula")]) == {
        "status": "not-checkable", "balanced": 0, "unbalanced": 0, "not_checkable": 1, "reasons": ["no-formula"],
    }
    assert summary([_row("a", "balanced"), _row("a", "unbalanced"), _row("b", "balanced")])["status"] == "unbalanced"
    assert summary([_row("a", "balanced"), _row("a", "unbalanced"), _row("b", "balanced")])["unbalanced"] == 1
    assert summary([_row("a", "balanced"), _row("b", "not-checkable", "withheld"), _row("b", "balanced")]) == {
        "status": "partial", "balanced": 1, "unbalanced": 0, "not_checkable": 1, "reasons": ["withheld"],
    }


def test_fractional_coefficients_balance_within_the_tolerance(library: Path, tmp_path: Path) -> None:
    components = {"A": {"formula": "Ca(OH)2"}, "B": {"formula": "CaO"}, "C": {"formula": "H2O"}, "D": {"formula": "NaCl"}}
    assert rx._balance({"A": -1, "B": 1, "C": 1}, components)["status"] == "balanced"
    assert rx._balance({"A": -1 / 3, "B": 1 / 3, "C": 1 / 3}, components)["status"] == "balanced"
    assert rx._balance({"A": -1, "B": 1, "C": 1 + 1e-12}, components)["status"] == "balanced"
    assert rx._balance({"A": -1, "B": 1, "C": 1.001}, components)["change"] == {"H": 0.002, "O": 0.001}
    # a charge-free ionic formula reads like any other
    assert rx._balance({"D": -1, "D2": 1}, {**components, "D2": {"formula": "ClNa"}})["status"] == "balanced"


@pytest.mark.parametrize("formula", [
    "H2O", "C2H6O", "Ca(OH)2", "Al2(SO4)3", "Fe2(SO4)3", "(CH3)3COH", "NaCl", "C 6 H 6", "Pt", "",
    "OH-", "Na+", "SO4-2", "CuSO400b75H2O", "CuSO4.5H2O", "D2O", "13CO2", "Xx", "Ba(OH)2", "W", "Ca(OH", "OH)2", "()", "h2o",
])
def test_the_formula_parser_is_cores(formula: str) -> None:
    formulas = pytest.importorskip("chemeascode.domains.chemistry.formulas")
    assert rx.parse_formula(formula) == formulas.parse_formula(formula)


def test_the_formula_elements_are_cores() -> None:
    formulas = pytest.importorskip("chemeascode.domains.chemistry.formulas")
    assert rx.FORMULA_ELEMENTS == set(formulas.ATOMIC_MASS)


def test_the_balance_is_cores_element_change() -> None:
    chemistry = pytest.importorskip("chemeascode.domains.chemistry.reactions")
    formulas = {"A": "Ca(OH)2", "B": "CaO", "C": "H2O"}
    for stoichiometry in ({"A": -1, "B": 1, "C": 1}, {"A": -1, "B": 1, "C": 2}, {"A": -2, "B": 1}):
        reaction = SimpleNamespace(stoichiometry=stoichiometry)
        ours = rx._balance(stoichiometry, {k: {"formula": f} for k, f in formulas.items()})
        assert ours["change"] == chemistry.element_change(reaction, formulas)


def test_a_reaction_has_sources_when_any_occurrence_cites_one(library: Path, tmp_path: Path) -> None:
    reactions = _by_slug(_reactions(library, tmp_path / "out"))
    # sources: for the reaction (SPLIT), its heat of reaction (NH3_SYN); none (OLIGO, H2_BURN)
    assert reactions["2h2o-to-2h2-o2"]["has_sources"] is True
    assert reactions["2nh3-eq-3h2-n2"]["has_sources"] is True
    assert reactions["nh3-to-lump"]["has_sources"] is False and reactions["2h2-o2-eq-2h2o"]["has_sources"] is False
    assert rx._has_sources({"sources": [], "conversion": None, "heat_of_reaction": None, "catalyst": {"text": "X", "id": "X", "entry": {"sources": ["a book"]}}})


def test_a_blank_source_is_none() -> None:
    # as the Atlas reads them: a source that is only white space cites nothing
    blank = {"sources": ["", "  "], "conversion": {"source": " "}, "heat_of_reaction": {"source": ""}, "catalyst": {"entry": {"sources": ["	"]}}}
    assert rx._has_sources(blank) is False
    assert rx._has_sources({**blank, "heat_of_reaction": {"source": "Perry's"}}) is True


def test_without_core_the_copy_parses(library: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "chemeascode.domains.chemistry.formulas", None)  # import raises ImportError
    assert rx._parser() is rx.parse_formula
    reactions = _by_slug(_reactions(library, tmp_path / "out"))
    assert reactions["2h2o-to-2h2-o2"]["balance"]["status"] == "balanced"
    assert reactions["nh3-to-lump"]["balance"]["status"] == "unbalanced"
