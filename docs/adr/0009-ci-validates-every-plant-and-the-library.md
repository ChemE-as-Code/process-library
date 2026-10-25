# 0009. CI validates every engineering project with cheme and builds the library

- **Status:** Accepted, 2026-10-23 (validation of the single ASU since 2026-10-18)
- **Scope:** `.github/workflows/validate.yml`, `.github/workflows/docs.yml`

## Context

Each engineering project is a cheme-as-code project with its own checks, and the library adds
contracts that span processes: manifests against the schemas, registry slugs, mappings,
allocation, benchmarks. Both must hold on every change, but a design in progress has open stage
gates that are progress, not errors.

## Decision

- The `validate` workflow runs on every push and pull request.
- A `discover` job lists `processes/*/plant.yaml`; a matrix job runs, **in each process
  folder**, `cheme fmt --check`, `cheme validate` and, when present,
  `cheme assess lca-scenarios --check`. `cheme check` (stage gates) runs informationally and
  does not fail the build.
- A `library` job runs the tooling tests (including the Brightway round trip) and builds the
  catalog (errors fail, warnings are listed), the LCI database with `--strict`, and the public
  catalog and LCI database (`--public`). Core is
  installed there so benchmarks can convert units (`ATLAS_REQUIRE_CORE`).
- The documentation site is built with `mkdocs build --strict` on every pull request
  (`docs.yml`); it is not deployed.
- CI publishes nothing ([0012](0012-versioning-releases-and-dois.md)).

## Consequences

- A new process folder with `plant.yaml` is validated without a workflow change.
- LCI warnings (allocation findings, benchmark values outside their range) fail CI through the
  strict LCI build; the catalog build in CI is not strict (its preview warnings are expected
  there), so `--strict` on the catalog is a contributor's check (CONTRIBUTING.md step 5).
- CI depends on private repositories while they are in development (core through a fine-grained
  token, pyDEXPI through a deploy key); a fork cannot run it.
- Gate failures are visible but not blocking; sign-off relies on the process's own review.

## Evidence

- `55be1e3` (first CI of the ASU), `0174ff3` (token for core).
- `986803b` matrix over `processes/*/plant.yaml` and the library job,
  [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `28bb7b9` public catalog in CI, [#20](https://github.com/ChemE-as-Code/process-library/pull/20);
  `3f0d2b5` docs build, [#67](https://github.com/ChemE-as-Code/process-library/pull/67).
- `.github/workflows/validate.yml`, README.md "CI".
