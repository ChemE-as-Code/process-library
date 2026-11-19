"""Compose recorded comparisons; the CLI only parses and presents."""

import json
import uuid
from datetime import datetime
from pathlib import Path

from wwtp_a2o.domains.process.comparison import compare
from wwtp_a2o.integrations.runner import execute_example
from wwtp_a2o.project.artifacts import write_json


def verify_runs(
    root: Path, baseline_run=None, reference_run=None, numerics_run=None, incomplete_probe=None
):
    baseline = baseline_run or execute_example(root, [])
    reference = reference_run or execute_example(root, ["--upstream-reference"])
    translation = compare(baseline, reference, rtol=1e-5, atol=1e-6)
    numerics = compare(baseline, numerics_run, rtol=1e-3, atol=1e-4) if numerics_run else None
    checked = [translation] + ([numerics] if numerics else [])
    ok = all(
        r["all_final_solver_states_pass"]
        and all(x["pass"] for x in r["effluent_comparison"].values())
        for r in checked
    )
    result = {
        "completed_comparisons_passed": ok,
        "baseline_vs_unmodified_upstream_factory": translation,
        "numerical_cross_check": numerics if numerics else {"status": "not_verified"},
        "threshold_basis": (
            "Local software regression tolerances selected before comparison; not"
            " an official benchmark tolerance or compliance threshold."
        ),
        "limits": [
            "Same underlying source, so not an independent physical validation.",
            "No whole-system elemental balance or initialization-sensitivity claim.",
            (
                "Baseline and reference use the current installed EXPOsan version and"
                " the same initial states."
            ),
        ],
    }
    result["incomplete_numerical_probes"] = []
    for probe in incomplete_probe or []:
        record = probe / "interruption.json"
        if not record.is_file():
            record = probe / "failure.json"
        result["incomplete_numerical_probes"].append(
            {
                "run": probe.name,
                "record": json.loads(record.read_text(encoding="utf-8")),
                "included_in_passed_comparisons": False,
            }
        )
    path = (
        root
        / "process/simulation-runs"
        / (datetime.now().strftime("%Y%m%d_%H%M%S") + "_verification_" + uuid.uuid4().hex[:6])
    )
    path.mkdir(exist_ok=False)
    write_json(path / "verification.json", result)
    return path, result, 0 if ok else 2
