# Building and CI

<!-- readme: ## Building the catalog and the LCI database | body -->

<!-- readme: ## Repository size -->

## These docs

The site is built with MkDocs and the Material theme, pinned in `requirements-docs.txt` to the
versions ChemE-as-Code/core uses. Pages include their sections from the repository's files with
comments such as `<!-- readme: ## Repository size -->` (`docs/hooks/includes.py`, core's hook);
the process and schema pages are generated (`docs/hooks/library.py`). A section renamed or
removed in a source fails the strict build:

```sh
python -m venv .venv && .venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs serve           # http://127.0.0.1:8000
.venv/bin/mkdocs build --strict  # what CI runs (.github/workflows/docs.yml); writes site/
```

CI builds the site on every pull request. It is not deployed.
