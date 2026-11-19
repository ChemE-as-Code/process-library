"""Start a local read-only viewer using core's optional web dependencies."""

import re
import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen

import typer

from wwtp_a2o.foundation.runtime import CORE, CORE_PYTHON, ROOT, environment


def check_viewer(port):
    if not 1024 <= port <= 65535:
        raise ValueError("Choose a port between 1024 and 65535")
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", port)) == 0:
            raise ValueError(f"Port {port} is busy. Stop its viewer or use --port {port + 1}.")
    if not (CORE / "viewer/dist/index.html").is_file():
        raise FileNotFoundError("Build the existing ChemE-as-Code viewer first")


def saved_report(root: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
        raise ValueError("Invalid run ID")
    root = root.resolve()
    for folder in (root / "process/simulation-runs", root / "runs"):
        expected = folder / run_id / "report.html"
        if expected.resolve() == expected and expected.is_file():
            return expected
    raise FileNotFoundError(f"No saved report for run {run_id}")


def launch_viewer(port=8770, run_id=None, no_browser=False):
    check_viewer(port)
    url = f"http://127.0.0.1:{port}/"
    report = saved_report(ROOT, run_id) if run_id else None
    process = subprocess.Popen(
        [str(CORE_PYTHON), "-u", str(ROOT / "serve_example.py"), "--port", str(port)],
        cwd=ROOT,
        env=environment(),
    )
    print(
        f"ChemE-as-Code viewer: {url}\nKeep this terminal open. Ctrl+C stops the viewer.",
        flush=True,
    )
    if report:
        print(f"Saved report: {report}", flush=True)

    def open_ready():
        for _ in range(120):
            if process.poll() is not None:
                return
            try:
                with urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        webbrowser.open(report.as_uri() if report else url)
                        return
            except OSError:
                time.sleep(0.5)

    if not no_browser:
        threading.Thread(target=open_ready, daemon=True).start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        return 0


app = typer.Typer(add_completion=False)


@app.command()
def main(port: int = 8770, run_id: str | None = None, no_browser: bool = False):
    raise typer.Exit(launch_viewer(port, run_id, no_browser))
