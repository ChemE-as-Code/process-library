"""Behaviour checks for the local example, separate from numerical validation."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from wwtp_a2o.domains.process.diagrams import project_documents
from wwtp_a2o.domains.process.model import connections, validate_inputs
from wwtp_a2o.foundation.runtime import ROOT, venv_python
from wwtp_a2o.project.artifacts import make_adapter
from wwtp_a2o.project.run import create_run


@pytest.fixture
def inputs():
    return json.loads((ROOT / "inputs/baseline.json").read_text(encoding="utf-8"))


def test_diagrams_preserve_baseline_documents(inputs):
    expected = json.loads(
        (Path(__file__).parent / "fixtures/diagram_documents.json").read_text(encoding="utf-8")
    )
    assert project_documents(inputs) == expected


def test_clarifier_label_tracks_the_input_without_changing_it(inputs):
    inputs["clarifier"]["N_layer"] = 12
    original = copy.deepcopy(inputs)
    steps = project_documents(inputs)["process/flowsheet.yaml"]["steps"]
    assert next(s for s in steps if s["id"] == "C1")["title"] == "C1: 12-layer nonreactive settler"
    assert inputs == original


@pytest.mark.parametrize("quantity", [-1, 0, float("nan"), float("inf")])
def test_invalid_volume_rejected_before_simulator_import(inputs, quantity):
    inputs["reactor_volumes_m3"]["A1"] = quantity
    with pytest.raises(ValueError, match="A1"):
        project_documents(inputs)


def test_waste_sludge_cannot_exceed_inflow(inputs):
    inputs["recycles"]["waste_sludge_m3_d"] = inputs["influent"]["flow_m3_d"]
    with pytest.raises(ValueError, match="Waste sludge"):
        validate_inputs(inputs)


def test_topology_keeps_external_water_balance_and_recycles(inputs):
    by_id = {sid: (a, b, q) for sid, a, b, q in connections(inputs)}
    assert by_id["RAS"][:2] == ("C1", "A1")
    assert by_id["INTERNAL"][:2] == ("O3", "A3")
    assert by_id["INFLUENT"][2] == by_id["EFFLUENT"][2] + by_id["WAS"][2]
    documents = project_documents(inputs)["process/flowsheet.yaml"]
    assert {s["id"] for s in documents["streams"]} == set(by_id)
    assert len(documents["blocks"]) == 4
    assert len(documents["steps"]) == 8


def test_domain_and_preparation_imports_are_lightweight_from_another_directory(tmp_path):
    code = """
import sys
from wwtp_a2o.domains.process.diagrams import project_documents
from wwtp_a2o.domains.process.simulation import calculate
from wwtp_a2o.project.prepare import prepare_project
blocked = {'qsdsan', 'exposan', 'matplotlib', 'numpy', 'fastapi', 'uvicorn', 'typer'}
assert not blocked.intersection(sys.modules), blocked.intersection(sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_new_runs_never_overwrite_previous_evidence(tmp_path):
    first = create_run(tmp_path, "baseline")
    (first / "result.json").write_text('{"preserve":true}', encoding="utf-8")
    second = create_run(tmp_path, "baseline")
    assert first != second
    assert (first / "result.json").read_text(encoding="utf-8") == '{"preserve":true}'
    assert create_run(tmp_path, "../../outside").parent == tmp_path / "process/simulation-runs"


def test_adapter_retains_wastewater_measurement_bases():
    result = {
        "status": "completed",
        "case_id": "baseline",
        "versions": {"qsdsan": "1.5.3"},
        "solver": {"method": "BDF"},
        "verification": {"plant_validation": "not_applicable_generic_example"},
        "steady_state_screen": {"status": "not_passed"},
    }
    stream = dict(stream="EFFLUENT", COD=1, TN=2, TP=3, TSS=4, NH4=5, PO4=6, flow=7)
    source = {
        "commit": None,
        "dirty": ["inputs/baseline.json"],
        "fingerprints": {"inputs/baseline.json": "sha256:" + "a" * 64},
    }
    record = make_adapter(result, [stream], [], source, [])
    values = record["streams"][0]["values"]
    assert values["COD"] == {"value": 1, "unit": "mg COD/L"}
    assert values["TN"] == {"value": 2, "unit": "mg N/L"}
    assert values["TP"] == {"value": 3, "unit": "mg P/L"}
    assert record["streams"][0]["filled"] == []
    assert record["inputs"] == source
    assert record["steady_state_screen"]["status"] == "not_passed"


def test_environment_path_supports_windows_and_posix(tmp_path):
    assert venv_python(tmp_path, "nt") == tmp_path / "Scripts/python.exe"
    assert venv_python(tmp_path, "posix") == tmp_path / "bin/python"


def test_saved_report_resolves_only_within_the_run(tmp_path):
    from wwtp_a2o.interfaces.cli.viewer import saved_report

    for folder in ("process/simulation-runs/new", "runs/old"):
        run = tmp_path / folder
        run.mkdir(parents=True)
        report = run / "report.html"
        report.touch()
        assert saved_report(tmp_path, run.name) == report
    for name in ("../old", r"..\old", "C:/outside", "/outside"):
        with pytest.raises(ValueError):
            saved_report(tmp_path, name)
    with pytest.raises(FileNotFoundError):
        saved_report(tmp_path, "missing")


def test_worker_refuses_mismatched_input_before_calculation(tmp_path, inputs, monkeypatch):
    from wwtp_a2o.interfaces.cli.cheme import main

    monkeypatch.chdir(tmp_path)
    (tmp_path / "process").mkdir()
    (tmp_path / "inputs.json").write_text(json.dumps(inputs))
    (tmp_path / "process/case-inputs.json").write_text("{}")
    request = tmp_path / "request.json"
    response = tmp_path / "response.json"
    request.write_text(json.dumps({"case": "baseline", "input": "inputs.json"}))
    with pytest.raises(ValueError, match="Regenerate"):
        main(request, response)
    assert not response.exists()
    assert (tmp_path / "process/case-inputs.json").read_text() == "{}"


def test_same_binary_in_another_environment_relaunches_example(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from wwtp_a2o.foundation import runtime

    target = venv_python(tmp_path / ".venv")
    target.parent.mkdir(parents=True)
    target.touch()
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    monkeypatch.setattr(runtime, "PYTHON", target)
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "other-env"))
    monkeypatch.setattr(sys, "executable", str(target))
    calls = []

    def launch(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", launch)
    entry = tmp_path / "run_example.py"
    with pytest.raises(SystemExit) as stopped:
        runtime.select_environment(entry)
    assert stopped.value.code == 0
    assert calls[0][:2] == [str(target), str(entry)]


def test_invalid_input_preserves_failure_evidence(tmp_path, inputs, monkeypatch):
    from wwtp_a2o.project import run as workflow

    for filename in ("requirements.lock.txt", "pyproject.toml"):
        (tmp_path / filename).write_text("", encoding="utf-8")
    monkeypatch.setattr(
        workflow,
        "collect_metadata",
        lambda *args: {
            "source": {"commit": None, "dirty": [], "fingerprints": {}},
            "findings": [],
        },
    )
    inputs["reactor_volumes_m3"]["A1"] = -1
    run = create_run(tmp_path, "invalid")
    outcome = workflow.execute(tmp_path, run, inputs)
    assert outcome.status == 1
    assert json.loads((run / "inputs.json").read_text())["reactor_volumes_m3"]["A1"] == -1
    assert "A1" in json.loads((run / "failure.json").read_text())["error"]
    assert not (tmp_path / "runs/latest.json").exists()


@pytest.mark.parametrize("explicit", [False, True], ids=["default", "override"])
def test_core_python_preserves_virtual_environment_link(tmp_path, explicit):
    core = tmp_path / "core"
    interpreter = venv_python(core / ".venv")
    if os.name == "nt":
        # A directory junction can be created without Windows symlink privileges.
        import _winapi

        target = tmp_path / "real-venv"
        venv_python(target).parent.mkdir(parents=True)
        venv_python(target).touch()
        core.mkdir()
        _winapi.CreateJunction(str(target), str(core / ".venv"))
    else:
        interpreter.parent.mkdir(parents=True)
        interpreter.symlink_to(sys.executable)
    assert interpreter.is_file() and interpreter.resolve() != interpreter
    env = {**os.environ, "CHEME_CORE_PATH": str(core), "PYTHONPATH": str(ROOT)}
    if explicit:
        env["CHEME_CORE_PYTHON"] = str(interpreter)
    else:
        env.pop("CHEME_CORE_PYTHON", None)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from wwtp_a2o.foundation.runtime import CORE_PYTHON; print(CORE_PYTHON)",
        ],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert Path(result.stdout.strip()) == interpreter
