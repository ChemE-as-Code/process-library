"""Compare two real runs after a refactor; this is a software regression check only."""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


def numerical_comparison(left, right, rtol=1e-12, atol=1e-12) -> dict:
    """Use the tolerances recorded before the post-refactor solve; never fit a tolerance."""
    differences = []
    failures = []
    count = 0

    def walk(a, b, path):
        nonlocal count
        if isinstance(a, dict) and isinstance(b, dict):
            if a.keys() != b.keys():
                failures.append(path + ": keys differ")
                return
            for key in a:
                walk(a[key], b[key], path + "/" + str(key))
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                failures.append(path + ": lengths differ")
                return
            for index, (x, y) in enumerate(zip(a, b, strict=True)):
                walk(x, y, path + "/" + str(index))
        elif type(a) in (int, float) and type(b) in (int, float):
            count += 1
            difference = abs(a - b)
            limit = atol + rtol * max(abs(a), abs(b))
            if not (math.isfinite(a) and math.isfinite(b)) or difference > limit:
                failures.append(path)
            if difference:
                differences.append(
                    {
                        "path": path,
                        "absolute_difference": difference,
                        "normalized_to_limit": difference / limit,
                    }
                )
        elif a != b:
            failures.append(path + ": value differs")

    walk(left, right, "")
    return {
        "passed": not failures,
        "rtol": rtol,
        "atol": atol,
        "numeric_values_compared": count,
        "nonzero_difference_count": len(differences),
        "maximum_absolute_difference": max(
            (d["absolute_difference"] for d in differences),
            default=0.0,
        ),
        "maximum_fraction_of_limit": max(
            (d["normalized_to_limit"] for d in differences),
            default=0.0,
        ),
        "differences": differences,
        "failures": failures,
    }


def read_csv(path):
    text_fields = {
        "stream",
        "from",
        "to",
        "reactor",
        "component",
        "measurement_basis",
        "basis_status",
    }

    def value(key, text):
        if key in text_fields:
            return text
        try:
            return float(text)
        except ValueError:
            return text

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: value(k, v) for k, v in row.items()} for row in csv.DictReader(handle)]


def compare_runs(before: Path, after: Path) -> dict:
    """Check full saved outputs; metadata and elapsed times intentionally differ."""
    records = {}
    for name in (
        "inputs.json",
        "solver_state_headers.json",
        "streams.csv",
        "reactors.csv",
        "influent_components.csv",
        "trajectory.csv",
        "trajectory.png",
        "process_snapshot/flowsheet.yaml",
        "process_snapshot/materials.yaml",
        "process_snapshot/BFD.xml",
        "process_snapshot/PFD.xml",
        "source/system.py",
        "source/initial_conditions_asm2d.xlsx",
    ):
        records[name] = (before / name).read_bytes() == (after / name).read_bytes()
    arrays = {}
    with (
        np.load(before / "solver_states.npz") as left,
        np.load(after / "solver_states.npz") as right,
    ):
        for key in ("time_days", "states"):
            same_shape = left[key].shape == right[key].shape
            arrays[key] = {
                "before_shape": list(left[key].shape),
                "after_shape": list(right[key].shape),
                "exactly_equal": bool(same_shape and np.array_equal(left[key], right[key])),
                "max_absolute_difference": (
                    float(np.max(np.abs(left[key] - right[key]))) if same_shape else None
                ),
            }
    left = json.loads((before / "result.json").read_text(encoding="utf-8"))
    right = json.loads((after / "result.json").read_text(encoding="utf-8"))
    excluded = {"run_id", "elapsed_total_s", "elapsed_simulation_s", "source", "findings"}
    left_result = {key: value for key, value in left.items() if key not in excluded}
    right_result = {key: value for key, value in right.items() if key not in excluded}
    records["result_fields_excluding_execution_metadata"] = left_result == right_result
    adapter_left = json.loads((before / "adapter-result.json").read_text(encoding="utf-8"))
    adapter_right = json.loads((after / "adapter-result.json").read_text(encoding="utf-8"))
    left_adapter = {k: v for k, v in adapter_left.items() if k not in {"inputs", "findings"}}
    right_adapter = {k: v for k, v in adapter_right.items() if k not in {"inputs", "findings"}}
    records["adapter_calculated_values"] = left_adapter == right_adapter
    numeric = {
        name: numerical_comparison(read_csv(before / name), read_csv(after / name))
        for name in ("streams.csv", "trajectory.csv", "reactors.csv", "influent_components.csv")
    }
    numeric["result_fields_excluding_execution_metadata"] = numerical_comparison(
        left_result,
        right_result,
    )
    numeric["adapter_calculated_values"] = numerical_comparison(left_adapter, right_adapter)
    all_equivalent = (
        all(value for name, value in records.items() if name not in numeric)
        and all(a["exactly_equal"] for a in arrays.values())
        and all(value["passed"] for value in numeric.values())
    )
    return {
        "before_run": before.name,
        "after_run": after.name,
        "criterion": (
            "Solver arrays and structural files must be exactly equal. Derived numeric outputs "
            "use atol=1e-12 plus rtol=1e-12 times the larger absolute value, as planned before "
            "the post-refactor solve. Text, keys and table structure must match."
        ),
        "files_and_fields": records,
        "accepted_solver_arrays": arrays,
        "derived_output_comparison": numeric,
        "effluent": {
            key: {
                "before": value,
                "after": right["effluent"][key],
                "difference": right["effluent"][key] - value,
            }
            for key, value in left["effluent"].items()
        },
        "all_exact": all(records.values()) and all(a["exactly_equal"] for a in arrays.values()),
        "all_equivalent": all_equivalent,
        "scope": "Software refactoring regression; not physical validation or solver robustness.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare_runs(args.before, args.after)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["all_equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
