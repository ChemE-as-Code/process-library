# 0031. A case study is a reference reproduction plus one labelled design extension, rerun by one command

- **Status:** Accepted, 2026-11-06 (proposed 2026-11-04)
- **Deciders:** the owner (drafted by the coordinator's agent for #333)
- **Scope:** library structure (benchmarks), evaluation protocol

## Context

Tracker #333 broadens the engineering questions the library demonstrates: water harvesting with
a metal-organic framework, control of electrified distillation, fluidised-bed atomic layer
deposition, spray drying, a microfluidic T-junction, linked recycling inventories, a
liquid-infused membrane, kinetic-model discrimination and quantum-dot optical quality (#334 to
#342). Each case reproduces one published result and then changes one design input to show the
engineering consequence.

ADR 0030 covers the first half: a numerical reproduction in `benchmarks/reproductions/<id>/`,
with a pinned source and tolerances committed before the run. It does not cover three things
these cases need:

- **A design extension.** The changed-input result is a hypothetical design calculation built
  on the reproduced model. It is not a reproduction and not validation, and a reader must be
  able to tell the three apart.
- **Models that are not cheme flowsheets.** Most cases are a sorption isotherm, a droplet
  model, a kinetic model or a spectrum analysis. cheme has no unit for them yet, so the HDA
  layout (`case/` with a `plant.yaml`) does not fit.
- **Third-party measurement data.** Several cases start from an archived dataset (4TU.ResearchData,
  Zenodo). Its licence may not allow republication under CC BY 4.0 (ADR 0024, CLAUDE.md).

Options considered: (a) a process folder per case (`processes/<id>/`), which would mix
reproduced results with design data and contradict ADR 0030; (b) a new top-level `cases/`
folder, which would split reproductions across two places; (c) extend the ADR 0030 folder with
the files below.

## Decision

A case study is a folder `benchmarks/reproductions/<id>/` under ADR 0030, with these additions:

- `run.py` is the single rerun command, `uv run benchmarks/reproductions/<id>/run.py` from the
  library root. Its dependencies are pinned in its inline script metadata (PEP 723). It writes
  `results/` deterministically: `comparison.json` with every compared quantity and the
  verdict under the frozen rule, the extension's results, and figures drawn by our own code.
- `inputs.yaml` lists every model input with its value, unit and label: **measured** (from the
  source's data), **reconstructed** (derived by us from the source, for example digitised from
  a figure, with the method and its uncertainty) or **assumed** (our choice, with the reason).
- `extension.md` reports the changed-input result, labelled **hypothetical design extension**:
  the engineering consequence in physical terms and every input outside the reproduced range.
- `README.md` carries a status table with four rows: reproduction (pass, fail, partial or not
  achievable, under the frozen rule), independent validation (none unless data independent of
  the fitted source exist), design extension (hypothetical) and specialist review (not yet;
  an optional follow-up once a working result exists).
- Where the source does not provide what a reproduction needs, `sufficiency.md` records what
  exists, where, under which licence, what is missing, and the scope that is achievable. A
  case reports that scope rather than filling the gap with invented data.
- **Third-party data are downloaded at run time**, from the pinned URL or DOI, into a cache
  outside git (`$XDG_CACHE_HOME/cheme-reproductions/<id>/`), and checked against the sha256
  recorded in `source.yaml`. Raw data files are committed only when their licence allows
  publication under CC BY 4.0, with a `NOTICE.md` next to them. Reported numbers restated as
  facts with locators stay in `source.yaml`, as in ADR 0030.
- The tolerance rule of ADR 0030 holds unchanged: `tolerances.yaml` (with `source.yaml` and
  `inputs.yaml`) is committed in its own commit before the first run that compares computed
  values with reported ones.
- A case's results are not design data for a process folder (ADR 0030). A case that finds a
  reusable capability missing from cheme opens a core issue and links it from #333.

## Consequences

- Each case reruns with one command and no cheme installation; the cases can be added in
  parallel without a schema change.
- CI does not run the cases: `validate.yml` validates `processes/*/plant.yaml` only, and the
  downloads would make CI depend on external repositories. A rerun is a manual check. A
  scheduled CI job that reruns the cases and compares `results/` is a possible follow-up.
- A dataset that is withdrawn or changed upstream breaks the rerun; the sha256 makes that
  visible rather than silent. Datasets with a versioned DOI should be pinned to the version.
- The models live in plain Python scripts, outside core. When a case's model is generally
  useful (a sorption working-capacity unit, a droplet-drying unit), moving it into core is a
  separate decision recorded there.

## Evidence

- Accepted by the owner on 2026-11-06.
- Tracker #333 and cases #334 to #342 (one pull request each, branches `repro/<n>-<id>`).
- ADR 0030 and `benchmarks/reproductions/idaes-hda-tutorial/`, the reproduction this extends.
