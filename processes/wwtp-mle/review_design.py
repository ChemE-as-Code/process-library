"""Review the MLE design snapshot belonging to the current published Stream table."""

import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path


def project_file(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside the MLE project: {relative}")
    return path


def current_snapshot(root):
    """Resolve the accepted run's evidence and check its input and snapshot bytes."""
    root = root.resolve()
    entry = json.loads((root / "process/simulation-run.json").read_bytes())["cases"]["baseline"]
    integration = entry["outcome"]["integration"]
    if entry["execution"]["state"] != "completed" or not integration["completed"]:
        raise ValueError("The MLE case has no completed integration to review")
    verification = entry["verification"]
    digest = verification.get("design_snapshot_sha256")
    if not digest:
        raise ValueError("This run predates design snapshots; run the updated MLE worker")
    evidence = project_file(root, entry["evidence"])
    if evidence.parent != (root / "process/simulation-runs").resolve():
        raise ValueError("Expected an MLE simulation evidence folder")
    for name, expected in entry["inputs"]["fingerprints"].items():
        path = project_file(root, name)
        if not path.is_file() or "sha256:" + sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Run inputs or published stream values changed: {name}; rerun MLE")
    path = project_file(root, evidence / "design-snapshot.json")
    if path.parent != evidence:
        raise ValueError("The design snapshot must be in this run's evidence folder")
    content = path.read_bytes()
    if sha256(content).hexdigest() != digest:
        raise ValueError("The design snapshot differs from the published run evidence")
    snapshot = json.loads(content)
    if (
        snapshot["case"] != entry["case"]
        or snapshot["run_id"] != evidence.name
        or snapshot["day"] != integration["achieved_end"]
    ):
        raise ValueError("The design snapshot does not describe the published MLE run")
    source = {
        "case": snapshot["case"],
        "run_id": snapshot["run_id"],
        "day": snapshot["day"],
        "snapshot": path.relative_to(root).as_posix(),
        "model_fingerprint": entry["model_fingerprint"],
        "core_run_tool": entry["tool"],
        "inputs": entry["inputs"],
        "field_sources": snapshot["sources"],
    }
    return path, source


def main():
    try:
        path, source = current_snapshot(Path.cwd())
        result = subprocess.run(
            [sys.executable, "-m", "chemeascode", "process", "activated-sludge-review", str(path)],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        report = {"source": source, **json.loads(result.stdout)}
    except subprocess.CalledProcessError as error:
        print(
            "Use a core Python environment with the activated-sludge-review command.",
            file=sys.stderr,
        )
        print(error.stderr.rstrip(), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Cannot review the current MLE run: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
