"""Print the read-only core design review for a published A2/O snapshot."""

import json
import subprocess
import sys
from pathlib import Path

from wwtp_a2o.foundation.runtime import environment
from wwtp_a2o.project.design_review import current_snapshot


def main():
    try:
        path, source = current_snapshot(Path.cwd())
        run = subprocess.run(
            [sys.executable, "-m", "chemeascode", "process", "activated-sludge-review", str(path)],
            env=environment(),
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        report = {"source": source, **json.loads(run.stdout)}
    except subprocess.CalledProcessError as error:
        print("Use a core Python with the activated-sludge-review command.", file=sys.stderr)
        print(error.stderr.rstrip(), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Cannot review the current A2/O run: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0
