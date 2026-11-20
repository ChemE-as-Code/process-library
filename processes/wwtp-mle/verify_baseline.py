"""Check a newly published 200-day MLE run against the saved stream reference."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RTOL = 1e-6
ATOL = 1e-8


def load(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    reference = load(ROOT / "inputs/reference-streams.json")
    case = reference["case"]
    days = reference["days"]
    record_path = ROOT / "process/simulation-run.json"
    require(record_path.is_file(), "Run cheme process simulate --fill first.")
    result = load(record_path)["cases"][case]
    require(
        result["schema"] == "cheme/adapter-result/v2" and result["status"] == "completed",
        "Expected a completed v2 worker result.",
    )
    outcome = result["outcome"]
    progress = outcome["integration"]
    require(
        outcome["mode"] == "dynamic"
        and outcome["convergence"] == "not-applicable"
        and outcome["steady_state"]["state"] == "not-evaluated"
        and progress["start"] == 0
        and progress["requested_end"] == days
        and progress["achieved_end"] == days
        and progress["time_unit"] == "day"
        and progress["completed"] is True,
        f"Expected a completed {days}-day integration and an unevaluated steady state.",
    )
    actual = {stream["id"]: stream["values"] for stream in result["streams"]}
    expected = reference["streams"]
    require(actual.keys() == expected.keys() and len(actual) == 10, "Stream IDs differ.")
    count = 0
    for stream, values in expected.items():
        require(actual[stream].keys() == values.keys(), f"{stream}: output quantities differ.")
        for key, cell in values.items():
            measured = actual[stream][key]
            require(measured["unit"] == cell["unit"], f"{stream}/{key}: unit differs.")
            require(
                math.isclose(measured["value"], cell["value"], rel_tol=RTOL, abs_tol=ATOL),
                f"{stream}/{key}: {measured['value']} differs from {cell['value']}",
            )
            count += 1
    require(count == 50, f"Expected 50 comparisons, got {count}.")
    print(f"{case}: day {days}, {count} stream values and units match the saved reference.")


if __name__ == "__main__":
    main()
