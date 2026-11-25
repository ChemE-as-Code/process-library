"""QSDsan worker v1. Core stages the model and publishes the validated stream values."""

import json
import shutil
import sys
import time
from pathlib import Path

from wwtp_a2o.domains.process.diagrams import project_documents
from wwtp_a2o.domains.process.model import validate_inputs
from wwtp_a2o.domains.process.simulation import calculate
from wwtp_a2o.integrations.qsdsan import upstream_evidence
from wwtp_a2o.interfaces.report import write_saved_report
from wwtp_a2o.project.artifacts import make_adapter, save_calculation, write_json
from wwtp_a2o.project.design_review import save_design_snapshot


def main(request: Path, response: Path) -> None:
    started = time.perf_counter()
    spec = json.loads(request.read_bytes())
    data = json.loads(Path(spec["input"]).read_bytes())
    if data["case_id"] != spec["case"]:
        raise ValueError("Requested case differs from the model input")
    data["solver"].setdefault("wall_limit_s", 180)
    validate_inputs(data)
    if data != json.loads(Path("process/case-inputs.json").read_bytes()):
        raise ValueError(
            "Regenerate the process configuration for the changed inputs before simulating"
        )
    import yaml

    diagrams = project_documents(data)
    sheet = yaml.safe_load(Path("process/flowsheet.yaml").read_bytes())
    expected = diagrams["process/flowsheet.yaml"]
    for name in ("feeds", "products", "blocks", "steps", "streams"):
        keys = ("id", "from", "to", "template") if name == "streams" else ("id", "block", "ports")

        def graph(rows, fields):
            return {row["id"]: {key: row.get(key) for key in fields} for row in rows}

        if graph(sheet[name], keys) != graph(expected[name], keys):
            raise ValueError(f"The authored {name} differ from the configured A2/O model")
    evidence = Path(spec["evidence"])
    source = evidence / "source"
    source.mkdir()
    for name in spec["files"]:
        dest = source / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(name, dest)
    write_json(evidence / "inputs.json", data)
    parameters, upstream = upstream_evidence(data, False)
    for path in upstream:
        shutil.copyfile(path, source / path.name)
    calculation = calculate(data, False)
    parameters["component_order"] = calculation.component_order
    write_json(evidence / "model_parameters.json", parameters)
    save_calculation(evidence, calculation)
    result = dict(
        calculation.result, run_id=evidence.name, elapsed_total_s=time.perf_counter() - started
    )
    write_json(evidence / "result.json", result)
    adapter = make_adapter(result, calculation.streams, calculation.reactors, {}, [])
    if result["status"] == "completed":
        digest = save_design_snapshot(evidence, data, calculation, result["run_id"])
        adapter["verification"] = {**adapter["verification"], "design_snapshot_sha256": digest}
    write_json(evidence / "adapter-result.json", adapter)
    write_saved_report(evidence, data, result)
    write_json(response, adapter)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
