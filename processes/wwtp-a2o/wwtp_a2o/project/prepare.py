"""Write native engineering documents and ask the unchanged core to build/validate."""

from pathlib import Path

from wwtp_a2o.domains.process.diagrams import project_documents
from wwtp_a2o.integrations.cheme import build_and_validate
from wwtp_a2o.project.artifacts import write_json


def prepare_project(root: Path, data: dict) -> None:
    import yaml

    documents = project_documents(data)
    (root / "process").mkdir(parents=True, exist_ok=True)
    write_json(root / "process/case-inputs.json", data)
    for name, value in documents.items():
        (root / name).write_text(
            yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    build_and_validate(root)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Generate the A2/O engineering documents in a new directory."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
        parser.error("Choose an empty output directory so authored project files are preserved.")
    data = json.loads(args.input.read_bytes())
    data["solver"].setdefault("wall_limit_s", 180)
    prepare_project(args.output, data)
