"""Keep local module ownership compatible with the framework's import direction."""

import ast

from wwtp_a2o.foundation.runtime import ROOT


def test_no_reverse_dependencies_or_ui_imports_in_calculations():
    violations = []
    for path in (ROOT / "wwtp_a2o").rglob("*.py"):
        relative = path.relative_to(ROOT / "wwtp_a2o")
        layer = relative.parts[0]
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                continue
            for name in names:
                if layer in {"foundation", "integrations", "domains", "project"} and (
                    name.startswith("wwtp_a2o.interfaces")
                ):
                    violations.append((str(relative), name))
                if layer in {"foundation", "integrations"} and name.startswith(
                    ("wwtp_a2o.domains", "wwtp_a2o.project")
                ):
                    violations.append((str(relative), name))
                if layer == "domains" and name.startswith("wwtp_a2o.project"):
                    violations.append((str(relative), name))
                if name in {"typer", "fastapi", "uvicorn"} and layer != "interfaces":
                    violations.append((str(relative), name))
    assert not violations
