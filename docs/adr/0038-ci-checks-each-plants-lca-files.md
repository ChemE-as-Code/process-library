# 0038. CI fails a plant whose LCA files are not current

- **Status:** Proposed, 2026-11-12
- **Deciders:** the owner (drafted for #422)
- **Scope:** the per-plant `validate` job (`.github/workflows/validate.yml`); extends
  [0009](0009-ci-validates-every-plant-and-the-library.md)

## Context

`cheme assess lca --write` writes a plant's LCA files (`lca/inventory.csv`, `results.csv`,
`results.md`, `gaps.csv`, `dataset.yaml`) and a run manifest, `lca/manifest.json`, that records
the sha256 of each input (`process.yaml`, `process/flowsheet.yaml`, `process/materials.yaml`,
`lca/lca.yaml`, ...), the sha256 of `results.csv` and the core version. The catalog publishes a
footprint only when that manifest still describes the committed files
(`scripts/publication.py` `lca_withheld`; otherwise `stale-run-manifest`).

Until now the per-plant job ran `cheme fmt --check`, `cheme validate` and, where present,
`cheme assess lca-scenarios --check`, but not `cheme assess lca --check`. An edit to a flowsheet,
`lca.yaml` or `process.yaml` without a rewrite of the LCA left the manifest stale, and CI stayed
green. The build only withholds the footprint quietly, so nothing failed. In #422, 15 public
processes had their footprint withheld this way. The core 1.11.0 pin bump (#429) rewrote every
plant's LCA, and `lca --check` then passed in 63 of 64 plants (in 12 before). The 64th,
lng-terminal-1, still recorded core 1.7 and an older `process.yaml`.

Options considered:
- (a) Keep it as it is and rewrite the LCAs at each pin bump. Footprints would stay withheld
  between bumps, and a rewrite can change numbers, so a stale run noticed months later is
  harder to review.
- (b) Make the catalog build strict about `stale-run-manifest`. That fails the library job for
  all plants at once and names the problem far from the change that caused it.
- (c) Run `cheme assess lca --check` in each plant's job, next to `lca-scenarios --check`, and
  fail the job. The pull request that changes an input has to carry the rewritten LCA, and its
  diff is read with the change that caused it.

## Decision

- **The per-plant `validate` job runs `cheme assess lca --check`** (step "LCA files current")
  in every process folder that has `lca/lca.yaml`, with the pinned core, after `cheme validate`
  and before `cheme assess lca-scenarios --check`.
- **A failure fails the job** (no `continue-on-error`). The fix is `cheme assess lca --write` in
  the process folder, with the diff read before committing: hashes and the version string only is
  a refresh, a changed result is a design change and is reviewed as one.
- **A core pin bump rewrites every plant's LCA** (`cheme assess lca --write`) together with the
  scenario records, as the header of `validate.yml` says.
- `tests/test_workflows.py` (`test_lca_files_checked_per_plant`) checks that the step exists,
  is limited to folders with `lca/lca.yaml`, and does not continue on error.

## Consequences

- A change to a flowsheet, `materials.yaml`, `lca.yaml` or `process.yaml` of a plant with an
  LCA needs the LCA rewritten in the same pull request. That includes a `process.yaml` edit
  that does not change a number (a description, a reference), because the manifest records the
  file's sha256.
- A core pin bump that changes any LCA output turns every plant red until the bump rewrites
  them; that is the existing rule for the scenario records, now for the main LCA files too.
- A footprint can no longer be withheld as `stale-run-manifest` on `main` without a red build.
  Withholding for its sources (`placeholder-factors`, `*-sources`) is unchanged and does not
  fail CI.
- The check adds one LCA run per plant to the job (seconds per plant with the factors backend).
  A plant with a Brightway backend would need core's `lca` extra in this job; none has one
  today.
- `cheme assess lca --check` only covers the case of `lca/lca.yaml`. A design case's own
  dataset is kept current by that plant's `kind: command` gate (`--case <case>`,
  [0034](0034-design-case-lci-datasets.md)), which stays informational.

## Evidence

- Issue #422 (15 public footprints withheld as `stale-run-manifest`; the pin bump #429 fixed
  them with unchanged numbers).
- On `main` at 0b155d62, only lng-terminal-1 failed `cheme assess lca --check` (core v1.11.0,
  c21e6c7). Its `cheme assess lca --write` changed the `process.yaml` sha256 and the version
  string (1.7 to 1.11) only (`processes/lng-terminal-1/PROGRESS.md`, 2026-11-12). After that,
  the check passed in all 64 plant folders with `lca/lca.yaml`, with core installed both with all
  extras and without any (as CI installs it).
- `.github/workflows/validate.yml` (job `validate`, step "LCA files current"),
  `tests/test_workflows.py`, `scripts/publication.py` (`lca_withheld`).
