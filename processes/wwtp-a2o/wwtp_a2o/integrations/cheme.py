"""Bridge to the existing ChemE installation, without changing its shared interfaces."""

import json
import subprocess
import sys
from pathlib import Path

from wwtp_a2o.foundation.runtime import CORE_PYTHON, environment


def build_and_validate(root: Path) -> None:
    for command, logfile in ((["process", "build"], "build.log"), (["validate"], "validation.log")):
        result = subprocess.run(
            [str(CORE_PYTHON), "-c", "from chemeascode.interfaces.cli import app; app()", *command],
            cwd=root,
            env=environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        (root / "process" / logfile).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"ChemE {command} failed; see process/{logfile}")


def core_worker(root: Path, action: str, run: Path) -> str:
    result = subprocess.run(
        [str(CORE_PYTHON), "-m", "wwtp_a2o.integrations.cheme", action, str(run)],
        cwd=root,
        env=environment(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if action == "validate":
        (run / "adapter_validation.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"ChemE {action} failed: {result.stdout}{result.stderr}")
    return result.stdout


def collect_metadata(root: Path, run: Path) -> dict:
    """Reuse the real SourceRevision and Finding types in core's own environment."""
    return json.loads(core_worker(root, "metadata", run))


def worker(action: str, run: Path) -> None:
    # This worker runs in core's environment; the numerical environment stays independent.
    from chemeascode.foundation.findings import Finding
    from chemeascode.foundation.provenance import source_revision
    from chemeascode.foundation.schemas.run import AdapterResult, finding_dict

    if action == "validate":
        AdapterResult.model_validate_json((run / "adapter-result.json").read_text(encoding="utf-8"))
        print("Adapter schema passed")
        return
    if action != "metadata":
        raise ValueError("Unknown ChemE worker action")
    request = json.loads((run / "metadata_request.json").read_text(encoding="utf-8"))
    root = Path(request["root"])
    source = request.get("source")
    if source is None:
        source = source_revision(root, request["paths"]).as_dict()
    # Effective inputs are run-local/ignored and must never appear committed.
    effective = (run / "inputs.json").relative_to(root).as_posix()
    source["dirty"] = sorted(set(source["dirty"]) | {effective})
    findings = [
        finding_dict(
            Finding(
                file=(run / "result.json").relative_to(root).as_posix(),
                level="info" if passed else "error",
                rule="wwtp." + key.replace("_", "-"),
                message="Passed" if passed else "Failed",
                key=key,
                hint="Inspect result.json and inputs.json; this check is not plant validation.",
            )
        )
        for key, passed in request["checks"].items()
    ]
    print(json.dumps({"source": source, "findings": findings}))


if __name__ == "__main__":
    worker(sys.argv[1], Path(sys.argv[2]).resolve())
