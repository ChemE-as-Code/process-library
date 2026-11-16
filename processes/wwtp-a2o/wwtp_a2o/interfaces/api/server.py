"""Optional web server startup, isolated from deterministic code."""

from pathlib import Path


def serve(root: Path, core: Path, port: int) -> None:
    import uvicorn

    from chemeascode.interfaces.api.serve import create_app

    app = create_app(root, ui_dir=core / "viewer/dist", run_checks_allowed=False)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
