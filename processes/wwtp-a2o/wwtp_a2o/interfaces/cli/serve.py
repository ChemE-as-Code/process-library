"""Parse viewer startup arguments; web dependencies remain in interfaces/api."""

import typer

from wwtp_a2o.foundation.runtime import CORE, ROOT

app = typer.Typer(add_completion=False)


@app.command()
def main(port: int = 8770):
    from wwtp_a2o.interfaces.api.server import serve

    serve(ROOT, CORE, port)
