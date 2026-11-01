# 0012. Semantic versions for releases, datasets and methodology; releases drafted by CI, decided by the owner

- **Status:** Proposed, 2026-10-25 (docs/governance.md is a draft for the owner's review; its
  data contribution policy is a draft for TU Delft legal and has no force)
- **Scope:** [governance.md](../governance.md), `scripts/build_lci.py --version/--previous`,
  `.github/workflows/release.yml`, `scripts/release_metadata.py`

## Context

Users cite and compare LCI data across releases, so they need to know what changed and whether a
result moved by design or by correction. Publishing on Zenodo and minting a DOI cannot be undone,
and the repository mixes AGPL and MIT code with CC BY 4.0 data. Industrial partners may offer measured
data under restricted terms.

## Decision

- Three things carry a semantic version: the **database release** (`--version`, the database
  name `cheme-as-code-atlas-<version>`), each **dataset** (its own `version`), and the
  **methodology** (system-model.md header and `METHODOLOGY_VERSION`, kept equal by a test). The
  process manifest has none. MAJOR, MINOR and PATCH are defined by what changes (e.g. a change of
  allocation method or a removed activity code is MAJOR). Versions below 1.0.0 are screening
  releases.
- `build_lci.py --previous` writes an exchange-level **change report** and flags
  `version_not_raised`.
- `release.yml` is started by hand, has a read-only token, and only **drafts**: tests, the
  previous build, the public cut-off and substitution builds, archive metadata, all as a
  workflow artifact. It does not tag, release, deposit, mint a DOI or deploy. The release
  decision and the Zenodo deposit are the **owner's**, following a checklist.
- LCI review levels (`unreviewed`, `internal`, `independent-external`, `panel`) are separate from
  the engineering design review; datasets are deprecated with `superseded_by`, never deleted from
  a release, and activity codes are never reused.

## Consequences

- Nothing is published by automation; a release costs a manual step.
- The change report gives no impact delta (no library-wide reference background yet).
- Enabling the Zenodo GitHub integration would deposit **every** GitHub release as the LCI
  database under CC BY 4.0; only LCI releases may be tagged as releases, or deposits are made by
  hand.
- Status **Proposed**: no release has been made under these rules yet; the contribution policy
  (section 6) awaits TU Delft legal.

## Evidence

- `2f6c009` and `d39f60a`, [#68](https://github.com/ChemE-as-Code/process-library/pull/68) (closes #50).
- `0733ec0` dataset governance fields of core's contract v2 (core#179),
  [#75](https://github.com/ChemE-as-Code/process-library/pull/75).
- [governance.md](../governance.md) status banner, `.github/workflows/release.yml`.
