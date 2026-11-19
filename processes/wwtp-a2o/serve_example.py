"""Internal server entry point; launched in the existing ChemE core environment."""

from wwtp_a2o.interfaces.cli.serve import app

if __name__ == "__main__":
    app()
