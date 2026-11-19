"""The comparison must distinguish actual numeric changes from names such as INF."""

import json
from types import SimpleNamespace

import numpy as np
from compare_refactor import numerical_comparison, read_csv

from wwtp_a2o.domains.process.simulation import IntegrationStopped
from wwtp_a2o.foundation.runtime import ROOT
from wwtp_a2o.project.run import create_run


def test_csv_terminal_names_are_not_infinity(tmp_path):
    path = tmp_path / "streams.csv"
    path.write_text("stream,from,to,TN\nINFLUENT,INF,A1,15.6\n", encoding="utf-8")
    assert read_csv(path) == [{"stream": "INFLUENT", "from": "INF", "to": "A1", "TN": 15.6}]


def test_comparison_detects_numeric_and_structural_changes():
    assert numerical_comparison({"TN": 15.0}, {"TN": 15.0 + 1e-14})["passed"]
    assert not numerical_comparison({"TN": 15.0}, {"TN": 15.01})["passed"]
    assert not numerical_comparison({"TN": 15.0}, {"TP": 15.0})["passed"]
    assert not numerical_comparison([1.0], [1.0, 1.0])["passed"]
    assert not numerical_comparison(float("nan"), float("nan"))["passed"]


def test_incomplete_integration_retains_partial_accepted_states(tmp_path, monkeypatch):
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
    monkeypatch.setattr(workflow, "upstream_evidence", lambda *args: ({}, []))
    solution = SimpleNamespace(
        t=np.array([0.0, 0.1]),
        y=np.array([[1.0, 2.0]]),
        message="Deliberate incomplete integration",
    )

    def incomplete(*args):
        raise IntegrationStopped(solution, [["A1", "S_O2"]])

    monkeypatch.setattr(workflow, "calculate", incomplete)
    data = json.loads((ROOT / "inputs/baseline.json").read_text(encoding="utf-8"))
    run = create_run(tmp_path, "incomplete")
    outcome = workflow.execute(tmp_path, run, data, reference=True)
    assert outcome.status == 1
    with np.load(run / "solver_states.npz") as saved:
        assert np.array_equal(saved["states"], solution.y)
    assert (run / "failure.json").is_file()
    assert not (run / "result.json").exists()
    assert not (tmp_path / "runs/latest.json").exists()
