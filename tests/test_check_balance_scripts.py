"""Balance-script reproducibility (scripts/check_balance_scripts.py, ADR 0027): the checker
re-runs a process's balance script and compares its balance-output with the flowsheet values
that cite it."""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import check_balance_scripts as cbs  # noqa: E402

# `cheme run SCRIPT` stand-in: runs the script with this interpreter in the working directory
FAKE_CHEME = textwrap.dedent(
    """
    import runpy, sys
    assert sys.argv[1] == "run", sys.argv
    sys.argv = sys.argv[2:]
    runpy.run_path(sys.argv[0], run_name="__main__")
    """
)

EMIT = textwrap.dedent(
    """
    import json, os
    from pathlib import Path

    VALUES = {values!r}
    print("balance done")
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        Path(target).write_text(json.dumps({{"contract": "balance-output/1",
                                            "script": "scripts/bal.py",
                                            "cases": {{"design": VALUES}}}}))
    """
)

FLOWSHEET = {
    "schema": "cheme/process/v1",
    "kind": "flowsheet",
    "tolerance": {"abs": 1.0, "rel": 0.005},
    "streams": [
        {
            "id": "S1",
            "state": {
                "design": {
                    "flow": {
                        "value": 1000.0,
                        "basis": "mass",
                        "provenance": "assumed",
                        "source": "scripts/bal.py: the feed",
                    },
                    "temperature": {
                        "value": 300.0,
                        "provenance": "assumed",
                        "source": "design basis, D-001",
                    },
                    "composition": {
                        "basis": "mole_fraction",
                        "values": {"A": 0.6, "B": 0.4},
                        "provenance": "assumed",
                        "source": "scripts/bal.py (D-002)",
                    },
                }
            },
        },
        {
            "id": "Q1",
            "kind": "energy",
            "state": {
                "design": {
                    "duty": {
                        "value": 50.0,
                        "provenance": "assumed",
                        "source": "scripts/bal.py, eta 0.7",
                    }
                }
            },
        },
    ],
}

GOOD = {
    "S1": {"flow": 1000.4, "temperature": 999.0, "composition": {"A": 0.60004, "B": 0.39996}},
    "Q1": {"duty": 50.2},
}


def _process(
    tmp_path: Path, values: dict | None, flowsheet: dict = FLOWSHEET, script: str | None = None
) -> Path:
    folder = tmp_path / "processes" / "p-1"
    (folder / "process").mkdir(parents=True)
    (folder / "scripts").mkdir()
    (folder / "process" / "flowsheet.yaml").write_text(yaml.safe_dump(flowsheet))
    if script is None:
        script = EMIT.format(values=values)
    (folder / "scripts" / "bal.py").write_text(script)
    return folder


@pytest.fixture
def cheme(tmp_path: Path) -> list[str]:
    fake = tmp_path / "fake_cheme.py"
    fake.write_text(FAKE_CHEME)
    return [sys.executable, str(fake)]


def test_cited_values_only_script_sources():
    cited = cbs.cited_values(FLOWSHEET)
    assert [(c.script, c.stream, c.quantity) for c in cited] == [
        ("scripts/bal.py", "S1", "flow"),
        ("scripts/bal.py", "S1", "composition"),
        ("scripts/bal.py", "Q1", "duty"),
    ]
    assert cited[1].value == {"A": 0.6, "B": 0.4}


def test_agreeing_script_passes(tmp_path, cheme):
    (res,) = cbs.check_process(_process(tmp_path, GOOD), cheme)
    assert res.status == "checked" and not res.failed, res
    # the temperature does not cite the script, so its different value is not compared
    assert {f.quantity for f in res.findings} == {"flow", "composition.A", "composition.B", "duty"}


def test_drift_beyond_the_flowsheet_tolerance_fails(tmp_path, cheme):
    values = json.loads(json.dumps(GOOD))
    values["S1"]["flow"] = 1010.0  # 1 + 0.005 * 1010 = 6.05 allowed, 10 off
    (res,) = cbs.check_process(_process(tmp_path, values), cheme)
    assert res.failed
    (bad,) = [f for f in res.findings if f.status != "ok"]
    assert (bad.stream, bad.quantity, bad.status) == ("S1", "flow", "drift")
    assert bad.deviation == pytest.approx(10.0) and bad.allowed == pytest.approx(6.05)


def test_composition_component_missing_on_one_side_is_compared_with_zero(tmp_path, cheme):
    values = json.loads(json.dumps(GOOD))
    values["S1"]["composition"] = {"A": 0.6, "B": 0.39, "C": 0.01}
    (res,) = cbs.check_process(_process(tmp_path, values), cheme)
    bad = {f.quantity for f in res.findings if f.status != "ok"}
    assert bad == {"composition.B", "composition.C"}


def test_value_cited_but_not_emitted_is_missing(tmp_path, cheme):
    values = {"S1": GOOD["S1"]}
    (res,) = cbs.check_process(_process(tmp_path, values), cheme)
    assert res.failed
    assert [(f.stream, f.status) for f in res.findings if f.status != "ok"] == [("Q1", "missing")]


def test_script_without_contract_is_not_migrated_and_not_run(tmp_path, cheme):
    folder = _process(tmp_path, None, script="raise SystemExit('must not run')\n")
    (res,) = cbs.check_process(folder, cheme)
    assert res.status == "not-migrated" and not res.failed and res.findings == []
    (ran,) = cbs.check_process(folder, cheme, run_unmigrated=True)
    assert ran.status == "error" and ran.failed


def test_failing_script_is_an_error(tmp_path, cheme):
    folder = _process(tmp_path, None, script="# BALANCE_OUTPUT\nraise SystemExit(3)\n")
    (res,) = cbs.check_process(folder, cheme)
    assert res.status == "error" and res.failed and "exit 3" in res.message


def test_output_breaking_the_contract_is_an_error(tmp_path, cheme):
    script = EMIT.format(values=GOOD).replace("balance-output/1", "balance-output/9")
    (res,) = cbs.check_process(_process(tmp_path, None, script=script), cheme)
    assert res.status == "error" and "contract" in res.message


def test_missing_script_is_reported(tmp_path, cheme):
    folder = _process(tmp_path, GOOD)
    (folder / "scripts" / "bal.py").unlink()
    (res,) = cbs.check_process(folder, cheme)
    assert res.status == "missing-script" and res.failed


def _with_conversion_duty(stream: str) -> dict:
    """FLOWSHEET plus a duty that core's conversion-step model writes on ``stream``."""
    fs = json.loads(json.dumps(FLOWSHEET))
    fs["streams"].append(
        {
            "id": stream,
            "kind": "energy",
            "state": {
                "design": {
                    "duty": {
                        "value": 120.0,
                        "provenance": "calculated",
                        "source": f"{cbs.CONVERSION_DUTY} of R1 (core ADR 0059)",
                    }
                }
            },
        }
    )
    return fs


def test_a_duty_core_writes_is_found_in_the_flowsheet():
    assert cbs.conversion_duties(_with_conversion_duty("Q2")) == {("design", "Q2"): 120.0}
    assert cbs.conversion_duties(FLOWSHEET) == {}  # an assumed duty citing a script is not one


def test_script_giving_a_duty_core_writes_is_a_duplicate(tmp_path, cheme):
    folder = _process(tmp_path, {**GOOD, "Q2": {"duty": 121.0}}, _with_conversion_duty("Q2"))
    (res,) = cbs.check_process(folder, cheme)
    assert res.failed
    (bad,) = [f for f in res.findings if f.status != "ok"]
    assert (bad.stream, bad.quantity, bad.status) == ("Q2", "duty", "duplicate")
    assert (bad.flowsheet, bad.script_value) == (120.0, 121.0)
    md = cbs.markdown([res])
    assert "| p-1 | design | Q2 | duty | duplicate |" in md
    # leaving the duty out of the balance output passes: the script keeps it as a printout
    (ok,) = cbs.check_process(_process(tmp_path / "b", GOOD, _with_conversion_duty("Q2")), cheme)
    assert not ok.failed, ok


def test_fixed_tolerances_for_temperature_and_pressure():
    fs = {"tolerance": {"abs": 0.5, "rel": 0.002}}
    assert cbs.tolerance(fs, "flow") == {"abs": 0.5, "rel": 0.002}
    assert cbs.tolerance(fs, "duty") == {"abs": 0.5, "rel": 0.002}
    assert cbs.tolerance({}, "flow") == cbs.DEFAULT_TOLERANCE
    assert cbs.tolerance(fs, "temperature") == {"abs": 0.5, "rel": 0.0}
    cited = cbs.Cited("scripts/bal.py", "design", "S1", "temperature", 300.0, "scripts/bal.py")
    (ok,) = cbs.compare("p", cited, {"design": {"S1": {"temperature": 300.4}}}, fs)
    (bad,) = cbs.compare("p", cited, {"design": {"S1": {"temperature": 300.6}}}, fs)
    assert ok.status == "ok" and bad.status == "drift"


def test_phase_compares_equal():
    cited = cbs.Cited("scripts/bal.py", "design", "S1", "phase", "vapor", "scripts/bal.py")
    (ok,) = cbs.compare("p", cited, {"design": {"S1": {"phase": "vapor"}}}, {})
    (bad,) = cbs.compare("p", cited, {"design": {"S1": {"phase": "liquid"}}}, {})
    assert ok.status == "ok" and bad.status == "drift"


def test_main_exit_code_markdown_and_strict(tmp_path, cheme):
    _process(tmp_path, {"S1": GOOD["S1"]})  # Q1 missing
    md, js = tmp_path / "drift.md", tmp_path / "report.json"
    argv = [
        "--library",
        str(tmp_path),
        "--cheme",
        " ".join(f'"{c}"' for c in cheme),
        "--markdown",
        str(md),
        "--json",
        str(js),
    ]
    assert cbs.main(argv) == 1
    assert "| p-1 | design | Q1 | duty | missing |" in md.read_text(encoding="utf-8")
    assert json.loads(js.read_text(encoding="utf-8"))[0]["failed"] is True


def test_main_strict_fails_on_not_migrated(tmp_path, cheme):
    _process(tmp_path, None, script="print('old style')\n")
    argv = ["--library", str(tmp_path), "--cheme", " ".join(f'"{c}"' for c in cheme)]
    assert cbs.main(argv) == 0
    assert cbs.main([*argv, "--strict"]) == 1


def test_long_form_carries_a_basis_that_must_match():
    cited = cbs.cited_values(FLOWSHEET)[1]  # S1 composition, mole_fraction
    assert cited.basis == "mole_fraction"
    same = {"basis": "mole_fraction", "values": {"A": 0.6, "B": 0.4}}
    other = {"basis": "mass_fraction", "values": {"A": 0.6, "B": 0.4}}
    ok = cbs.compare("p", cited, {"design": {"S1": {"composition": same}}}, FLOWSHEET)
    (bad,) = cbs.compare("p", cited, {"design": {"S1": {"composition": other}}}, FLOWSHEET)
    assert all(f.status == "ok" for f in ok)
    assert (bad.quantity, bad.status) == ("composition.basis", "drift")
    flow = cbs.cited_values(FLOWSHEET)[0]
    (f,) = cbs.compare("p", flow, {"design": {"S1": {"flow": {"value": 1000.0}}}}, FLOWSHEET)
    assert f.status == "ok"


def _known(tmp_path: Path, entries: list[dict]) -> Path:
    path = tmp_path / "known.yaml"
    path.write_text(yaml.safe_dump({"known": entries}))
    return path


KNOWN_Q1 = {
    "process": "p-1",
    "script": "scripts/bal.py",
    "case": "design",
    "stream": "Q1",
    "quantity": "duty",
    "status": "drift",
    "flowsheet": 50.0,
    "script_value": 60.0,
    "reason": "pending owner decision, process-library#292",
}


def test_known_deviation_is_reported_but_does_not_fail(tmp_path, cheme):
    _process(tmp_path, {**GOOD, "Q1": {"duty": 60.0}})
    md = tmp_path / "drift.md"
    argv = ["--library", str(tmp_path), "--cheme", " ".join(f'"{c}"' for c in cheme)]
    assert cbs.main(argv) == 1  # no known list: the drift fails
    known = _known(tmp_path, [KNOWN_Q1])
    assert cbs.main([*argv, "--known", str(known), "--markdown", str(md)]) == 0
    text = md.read_text(encoding="utf-8")
    assert "| p-1 | design | Q1 | duty | known |" in text
    assert "process-library#292" in text


def test_known_deviation_fails_again_when_a_value_moves(tmp_path, cheme):
    _process(tmp_path, {**GOOD, "Q1": {"duty": 61.0}})  # recorded script value is 60.0
    known = _known(tmp_path, [KNOWN_Q1])
    argv = ["--library", str(tmp_path), "--cheme", " ".join(f'"{c}"' for c in cheme)]
    assert cbs.main([*argv, "--known", str(known)]) == 1


def test_stale_known_entry_fails(tmp_path, cheme):
    _process(tmp_path, GOOD)  # Q1 agrees now: the entry matches nothing
    known = _known(tmp_path, [KNOWN_Q1])
    argv = ["--library", str(tmp_path), "--cheme", " ".join(f'"{c}"' for c in cheme)]
    assert cbs.main([*argv, "--known", str(known)]) == 1


def test_known_missing_value_matches_without_script_value(tmp_path, cheme):
    _process(tmp_path, {"S1": GOOD["S1"]})  # Q1 missing
    entry = {k: v for k, v in KNOWN_Q1.items() if k != "script_value"} | {"status": "missing"}
    known = _known(tmp_path, [entry])
    argv = ["--library", str(tmp_path), "--cheme", " ".join(f'"{c}"' for c in cheme)]
    assert cbs.main([*argv, "--known", str(known)]) == 0


def test_library_known_deviation_file_is_well_formed():
    entries = cbs.load_known(KIT / cbs.KNOWN_FILE)
    assert entries, "the known-deviation list is expected to exist while entries are pending"
    for e in entries:
        assert "process-library#" in e["reason"]
        assert (KIT / "processes" / e["process"] / e["script"]).is_file()
