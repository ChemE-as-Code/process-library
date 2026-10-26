# 0008. Distribute a Brightway Excel workbook linked to the user's background by name; ship no licensed data

- **Status:** Accepted, 2026-10-23
- **Scope:** `scripts/build_lci.py`, `lci/mappings.yaml`, `python/` (`cheme-as-code-lci`)

## Context

The Atlas datasets are foreground processes: they consume electricity, steel, transport and
other background products that come from ecoinvent or similar databases. ecoinvent is licensed;
its data and results may not be published under CC BY 4.0
([0013](0013-licences-and-no-third-party-content.md)). Users already hold their own licensed
background in a Brightway project and need the Atlas data to link into it with little effort.

## Decision

- The LCI database is published as **one versioned foreground database** in bw2io's **Excel
  workbook** format, `cheme-as-code-atlas-<version>.xlsx`, with `datapackage.json` and
  `index.json` beside it.
- Background activities are referenced **by name only** (name, reference product, unit,
  location; ecoinvent 3.11 cut-off conventions); elementary flows by their biosphere3 UUID with
  a fallback to name and categories. `lci/mappings.yaml` holds the curated links; an exchange
  that cannot be linked fails the build. No ecoinvent data is shipped or needed to build.
- The background is chosen at install time, not in the library: the pip-installable
  `cheme-as-code-lci` package (`python/`) offers `install(path, background=..., location=...)`,
  which imports the workbook, links it to the named background and biosphere, sets the site
  location of `site` inputs, prefers Atlas activities for inputs another Atlas process makes,
  and returns a report of what did not link.

## Consequences

- The database can be published under CC BY 4.0 and built in CI without a licence.
- The names have **not** been checked against a licensed ecoinvent copy in this repository;
  `install()` reports names that do not link and a curator fixes them in the mappings.
- Results depend on the user's background version; the database cannot ship impact results of
  its own. The CI round trip uses a stub background built from one process's example factors.
- One package more to maintain (`python/`), tested in the library job.

## Evidence

- `986803b` builder, mappings and installer moved in from `process-atlas/library-kit`,
  [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `lci/mappings.yaml` header, lci/README.md ("Bring your own ecoinvent"), python/README.md,
  the Brightway round-trip tests in `tests/`.
