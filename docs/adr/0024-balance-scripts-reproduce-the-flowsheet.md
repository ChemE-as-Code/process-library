# 0024. Balance scripts write the values the flowsheet cites; CI re-runs them and compares

- **Status:** Proposed, 2026-10-31
- **Deciders:** the owner (proposed by an agent session)
- **Scope:** process folders (`processes/<id>/scripts/`, `process/flowsheet.yaml`), the library
  tooling (`scripts/check_balance_scripts.py`) and CI (`.github/workflows/validate.yml`)

## Context

Where core cannot calculate a flowsheet yet, 43 processes carry a standalone balance script
(`processes/<id>/scripts/<name>.py`, run with `cheme run`). Its results were pasted by hand into
`process/flowsheet.yaml` as `provenance: assumed` with a `source` that starts with the script's
path (`source: "scripts/h2_balance.py: ..."`). `cheme validate` checks that the flowsheet
balances, not that it still is what the script calculates. CI never ran the scripts, so a script
changed after the paste, a value pasted from an older run or a typo went unnoticed: the
flowsheet and the script that is its stated source could drift apart.

The scripts emit their results in many forms: printed tables on stdout, some a YAML fragment of
the flowsheet's streams (`--yaml`, or a file named on the command line), a few nothing but the
summary lines. The flowsheet `source` names the script, not which printed number a value comes
from. There was no mechanical mapping from a flowsheet value to a script output.

Options considered:

1. **Parse stdout.** Fragile: every script prints differently, and a reformatted line would
   look like drift.
2. **Re-generate the flowsheet from the scripts' YAML fragments.** Only some scripts have one;
   the fragments do not cover all the hand-edited fields of a flowsheet; and regenerating would
   change files in CI.
3. **A written output file per script (`build/<script>.json`).** Clear, but it leaves an
   untracked artefact in the process folder, which `cheme` builds and the catalog look at.
4. **A small output contract, requested through an environment variable.** The script writes
   the cited values, keyed by the flowsheet's own stream ids, to a file the caller names. A
   plain `cheme run` is unchanged.

## Decision

- **The contract (`balance-output/1`).** A balance script whose numbers a flowsheet cites
  writes, when the environment variable `BALANCE_OUTPUT` names a file, a JSON document:

  ```json
  {"contract": "balance-output/1",
   "script": "scripts/h2_balance.py",
   "cases": {"design": {"S1": {"flow": 29303.44, "temperature": 288.15, "pressure": 3000.0},
                        "S14": {"composition": {"H2": 0.74, "CH4": 0.056}},
                        "Q1": {"duty": 18.8}}}}
  ```

  `cases` maps a flowsheet case (`state.<case>`) to stream or energy-stream ids to quantities
  (`flow`, `temperature`, `pressure`, `duty`, `composition`, `phase`), in the flowsheet's units
  and with the basis of its flow and composition. A quantity may carry its basis
  (`{"value": ..., "basis": "mass"}`, `{"values": {...}, "basis": "mass_fraction"}`); it must then
  be the flowsheet's. Each script carries its own small `write_balance_output()` (a process folder
  stays a self-contained project, runnable without the library tooling), and calls it with the
  same numbers it prints, so no engineering number is computed twice.
- **The checker.** `scripts/check_balance_scripts.py` collects every
  `streams[].state.<case>.<quantity>` whose `source` starts with `scripts/<name>.py`, re-runs each
  migrated script (its text names `BALANCE_OUTPUT`) with `cheme run` in its process folder and
  compares. A cited value that the output lacks is `missing`; one outside the tolerance is
  `drift`; a script that fails or breaks the contract is an `error`. Tolerance
  `|flowsheet - script| <= abs + rel * |script|`: for `flow` and `duty` the flowsheet's own
  `tolerance` (default abs 1.0, rel 0.005, as `cheme validate` uses for its balances); for
  `temperature` abs 0.5 K; `pressure` abs 0.5 kPa + rel 0.001; each composition component abs 1e-4
  + rel 0.005, a component on one side only compared with zero; `phase` equal.
- **CI.** The `balance-scripts` job of `validate.yml` installs the core commit that the other
  jobs pin, with the property extras the scripts import (`props,units,cantera`), runs the
  checker over the library and puts its table in the job summary. It fails on drift, missing
  values and errors of migrated scripts. A script not migrated yet is listed as `not-migrated`
  and does not fail the job (`--strict` makes it fail; to be switched on once all are migrated).
- **Changing a number.** A script change that moves a cited value updates the flowsheet in the
  same commit. Drift that the checker finds is reported and decided by the process owner; only a
  plain transcription error is corrected without a design decision.

## Consequences

- A flowsheet value sourced to a script is now as reproducible as the script: a stale paste
  fails CI instead of reaching the catalog.
- Every migration touches the script (about 30 lines) without changing what it prints. Scripts
  not migrated yet stay unchecked: the checker lists them, so the gap is visible.
- The scripts run with the pinned core: a core bump that changes property values (thermo,
  CoolProp, Cantera) can now turn the job red, which is the intended signal; the owner then
  re-runs the script and updates the flowsheet with the bump.
- The job adds a few minutes of CI (installing core with its property extras; the scripts
  themselves run in seconds).
- Values the flowsheet cites from documents (`D-00x`) or from core's own calculations are out of
  scope; so are equipment sizes and costs a script may also print.
- Open: switch on `--strict` when every cited script follows the contract; consider moving the
  helper into core (`cheme run` could set and read `BALANCE_OUTPUT` itself) if more projects
  outside the library adopt the pattern.

## Evidence

- `scripts/check_balance_scripts.py`, `tests/test_check_balance_scripts.py`
- `.github/workflows/validate.yml`, job `balance-scripts`
- Migrated scripts: `processes/{hydrogen-1,methanol-1,hda-1,nitric-acid-1}/scripts/` first,
  then further processes on the branch `quality/balance-script-reproducibility`; the checker's
  `not-migrated` lines list the rest.
- [CONTRIBUTING.md](../../CONTRIBUTING.md), "A balance script whose numbers go into the
  flowsheet"
