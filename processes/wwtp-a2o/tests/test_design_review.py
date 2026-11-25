import json
from hashlib import sha256
from types import SimpleNamespace

import numpy as np
import pytest

from wwtp_a2o.project.design_review import DESIGN_STREAMS, current_snapshot, design_snapshot


@pytest.mark.parametrize("missing_layer", [False, True])
def test_snapshot_uses_final_clarifier_states_and_the_o3_outlet(missing_layer):
    headers = [["-", "t [d]"], ["C1", "TSS2 [mg/L]"], ["O3", "Q [m3/d]"]]
    states = [[200.0, 300.0], [10.0, 11.0]]
    if not missing_layer:
        headers.append(["C1", "TSS1 [mg/L]"])
        states.append([100.0, 120.0])
    calculation = SimpleNamespace(
        headers=headers,
        states=np.array(states),
        time_days=[0.0, 200.0],
        reactors=[{"reactor": "O3", "volume_m3": 1000}],
        streams=[{"stream": sid, "TSS": 230.0, "flow": 11.0} for sid in DESIGN_STREAMS],
    )
    data = {"case_id": "baseline", "clarifier": {"N_layer": 2, "surface_area": 20, "height": 4}}
    snapshot = design_snapshot(data, calculation, "test-run")
    assert snapshot["day"] == 200
    assert snapshot["tanks"][0]["sample_stream"] == "TO_CLARIFIER"
    assert snapshot["tanks"][0]["mlss_mg_L"] == 230
    assert snapshot["clarifier"]["layer_tss_mg_L"] == (None if missing_layer else [120.0, 300.0])


@pytest.mark.parametrize("change", [None, "input", "digest", "run_id"])
def test_review_checks_the_published_snapshot(tmp_path, change):
    evidence = tmp_path / "process" / "simulation-runs" / "run-id"
    evidence.mkdir(parents=True)
    model_input = tmp_path / "input.json"
    model_input.write_bytes(b"{}")
    path = evidence / "design-snapshot.json"
    content = {
        "case": "baseline",
        "run_id": "other-run" if change == "run_id" else evidence.name,
        "day": 200,
        "sources": {},
    }
    path.write_bytes(json.dumps(content).encode())
    record = {
        "case": "baseline",
        "execution": {"state": "completed"},
        "outcome": {"integration": {"completed": True, "achieved_end": 200}},
        "verification": {"design_snapshot_sha256": sha256(path.read_bytes()).hexdigest()},
        "evidence": evidence.relative_to(tmp_path).as_posix(),
        "inputs": {"fingerprints": {"input.json": "sha256:" + sha256(b"{}").hexdigest()}},
        "model_fingerprint": "model",
        "tool": "cheme-as-code",
    }
    (tmp_path / "process" / "simulation-run.json").write_text(
        json.dumps({"cases": {"baseline": record}}), encoding="utf-8"
    )
    if change is None:
        resolved, source = current_snapshot(tmp_path)
        assert resolved == path
        assert source["run_id"] == content["run_id"]
        return
    if change == "input":
        model_input.write_bytes(b'{"days":100}')
    if change == "digest":
        path.write_bytes(b"{}")
    message = {
        "input": "Run inputs or published stream values changed",
        "digest": "differs from the published run evidence",
        "run_id": "does not describe the published A2/O run",
    }
    with pytest.raises(ValueError, match=message[change]):
        current_snapshot(tmp_path)
