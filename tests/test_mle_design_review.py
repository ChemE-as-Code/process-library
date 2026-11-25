"""The review reads only the snapshot bound to the current published MLE run."""

import json
import runpy
from hashlib import sha256
from pathlib import Path

import pytest

MLE = Path(__file__).resolve().parents[1] / "processes" / "wwtp-mle"
current_snapshot = runpy.run_path(str(MLE / "review_design.py"))["current_snapshot"]


@pytest.fixture
def published_run(tmp_path):
    evidence = tmp_path / "process" / "simulation-runs" / "example-run"
    evidence.mkdir(parents=True)
    model_input = tmp_path / "baseline.json"
    model_input.write_bytes(b'{"days":200}')
    path = evidence / "design-snapshot.json"
    snapshot = {"case": "baseline", "run_id": evidence.name, "day": 200, "sources": {}}
    record = {
        "case": "baseline",
        "execution": {"state": "completed"},
        "outcome": {"integration": {"completed": True, "achieved_end": 200}},
        "verification": {},
        "evidence": evidence.relative_to(tmp_path).as_posix(),
        "inputs": {
            "fingerprints": {
                "baseline.json": "sha256:" + sha256(model_input.read_bytes()).hexdigest()
            },
        },
        "model_fingerprint": "test-fingerprint",
        "tool": "cheme-as-code",
    }
    record_path = tmp_path / "process" / "simulation-run.json"

    def publish():
        path.write_bytes(json.dumps(snapshot).encode())
        record["verification"]["design_snapshot_sha256"] = sha256(path.read_bytes()).hexdigest()
        record_path.write_bytes(json.dumps({"cases": {"baseline": record}}).encode())

    publish()
    return path, model_input, snapshot, publish


def test_review_identifies_the_published_run(tmp_path, published_run):
    path, _, _, _ = published_run
    result, source = current_snapshot(tmp_path)
    assert result == path
    assert source["run_id"] == "example-run"
    assert source["day"] == 200
    assert source["snapshot"] == "process/simulation-runs/example-run/design-snapshot.json"


def test_review_refuses_changed_input(tmp_path, published_run):
    _, model_input, _, _ = published_run
    model_input.write_bytes(b'{"days":100}')
    with pytest.raises(ValueError, match="Run inputs or published stream values changed"):
        current_snapshot(tmp_path)


def test_review_refuses_changed_evidence(tmp_path, published_run):
    path, _, _, _ = published_run
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="differs from the published run evidence"):
        current_snapshot(tmp_path)


def test_review_refuses_a_snapshot_from_another_run(tmp_path, published_run):
    _, _, snapshot, publish = published_run
    snapshot["run_id"] = "previous-run"
    publish()
    with pytest.raises(ValueError, match="does not describe the published MLE run"):
        current_snapshot(tmp_path)
