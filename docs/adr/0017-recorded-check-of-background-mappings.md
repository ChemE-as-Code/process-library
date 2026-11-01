# 0017. Verify background mappings by a recorded check against a licensed copy

- **Status:** Proposed, 2026-10-27
- **Deciders:** the owner (proposed by an agent session, #303)
- **Scope:** the LCI pipeline (`lci/mappings.yaml`, `scripts/build_lci.py`), a new schema and
  record folder

## Context

`lci/mappings.yaml` links each LCI exchange to a background activity by name, reference product,
unit and location, and to biosphere3 flows by UUID or name and categories (ADR 0008). No
ecoinvent data may be in the library (ADR 0013), so the build cannot know whether a name exists.
The file said the names were "NOT checked against a licensed ecoinvent copy", and the only
safeguard was `install()`, which reports unlinked names to whoever installs the database. #303
asks for every name to be checked against licensed ecoinvent 3.11 (cut-off), and for the check
to be recorded: version, date, who, and the unmatched names. Before the library grows, a reader
of a build also needs to see whether that check was done and whether it still applies.

Options considered: a free-text note in `mappings.yaml` (cannot go stale automatically and is
not checked); running the check in CI (CI has no licensed database, and must never get one);
a script that a licence holder runs, writing a record the build reads (chosen).

## Decision

- `scripts/check_mappings.py`, run in a Brightway project that holds the licensed background
  and its biosphere, checks every `technosphere` and `substitution.technosphere` activity of
  `lci/mappings.yaml` (a `location: site` entry once per `--site`) and every `biosphere` flow
  (UUID first, else name and categories). It matches exactly as the installer does.
- It writes `lci/mapping-checks/<date>-<database>.yaml` (schema
  `schemas/lci-mapping-check.schema.json`, `cheme-as-code/lci-mapping-check/v1`): the database,
  its version and system model, the biosphere, the date, who checked, the sites, the counts,
  and each unmatched name with the reason (for a wrong location, the locations at which the same
  name exists). It records the library's own names only, never data of the background.
- Each record stores a hash of the checked names (`mappings_targets_sha256`). Edits to comments,
  sources, proxies or overrides keep the record valid. A changed or added name makes it stale.
- `build_lci.py` reads the latest record (by date, then file name) and writes
  `datapackage.json` `brightway.background_check` with `status` `unchecked`, `failed`, `stale` or
  `verified`. Anything but `verified` is listed in `index.json` `caveats`. An invalid record is a
  build error.
- The status is reported, not enforced: it is not a warning, so `--strict` and `--public`
  builds still pass with `unchecked`. Whether a public release requires `verified` is for the
  owner to decide, with the release rules (ADR 0012, #50).

## Consequences

- The check required by #303 has a fixed form, and every build says whether it holds.
- A name that a curator changes after the check is visible as `stale` at once, without
  rerunning the check in CI.
- Only a licence holder can produce a record. Until one is committed, every build reports
  `unchecked`.
- Flows that a dataset links by its own crosswalk UUID (core's elementary-flow crosswalk) are not
  in the mappings, so this check does not cover them. `install()` still reports them.
- A record proves the names existed in one release on one date. A new background release needs
  a new check.

## Evidence

- #303 (to-do: "check every `lci/mappings.yaml` name against a licensed ecoinvent 3.11 copy").
- `scripts/check_mappings.py`, `schemas/lci-mapping-check.schema.json`, `scripts/build_lci.py`
  (`background_check`), `lci/README.md` ("Linking").
- Tests: `tests/test_check_mappings.py` (matching, reasons, hash, build status) and
  `tests/test_lci_brightway.py::test_check_mappings_records_the_check_of_the_library_mappings`
  (the CLI in a Brightway project).
