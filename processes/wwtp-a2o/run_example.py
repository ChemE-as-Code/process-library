"""VS Code entry point. Implementation: wwtp_a2o/interfaces/cli/example.py."""

from pathlib import Path

from wwtp_a2o.foundation.runtime import select_environment

if __name__ == "__main__":
    select_environment(Path(__file__).resolve())
    from wwtp_a2o.interfaces.cli.example import app

    app()
