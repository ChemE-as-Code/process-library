# 0007. Attributional cut-off system model, substitution as a separate database, and an allocation hierarchy

- **Status:** Proposed, 2026-10-25 (applied by the build; the methodology is a draft for the
  owner's and an LCA expert's decision)
- **Scope:** [system-model.md](../system-model.md), `lci/mappings.yaml`, `scripts/build_lci.py`

## Context

Before this decision the database inherited whatever the process studies did: the ASU's dataset
carried end-of-life recycling credits (avoided primary metal), which would mix a substitution
model into a database meant to be linked to an ecoinvent cut-off background. Multi-output
processes were allocated by each study's method. Published chemical LCI databases (ecoinvent,
Carbon Minds) document one methodology, one system model per database and variants as separate
databases.

## Decision

- **One system model per build.** The default database is attributional with the cut-off
  approach (`system_model: cutoff` in `lci/mappings.yaml`). A cut-off build refuses negative
  (avoided) technosphere amounts; recycling and energy-recovery outputs are left out through
  `cutoff_exclusions:`, each with its decision.
- **Variants are separate databases.** `build_lci.py --system-model substitution` builds
  `cheme-as-code-atlas-<version>-substitution`, adding only the credits of `substitution:`. It
  is never mixed into the default build. APOS is not built (#51).
- **Allocation hierarchy** (ISO 14044 4.3.4.2, TfS PCF Guideline v3, WBCSD 2014): subdivision;
  a clear physical relationship (exergy for products of one separation, energy for co-produced
  fuels); otherwise the WBCSD price-ratio rule (economic above a ratio of 5, else mass); CO2 as a
  co-product cut before conditioning (a zero share); a published sector rule overrides as a
  documented deviation. Steps 1, 2, 4 and 5 are curated; step 3 is computed when prices are
  known. A departure is a **finding**, which fails `--strict`.
- The methodology has a version (`METHODOLOGY_VERSION`, 1.0.0) recorded in every build.

## Consequences

- The database is consistent with an ecoinvent cut-off background, and every exclusion and
  allocation is recorded per dataset.
- ASU-1's cut-off GOX result is higher than its study's by exactly the excluded recycling
  credits; this is expected and documented.
- The cut-off criteria for minor flows (1 % rules) are not checked by the build, because datasets
  do not record cut flows in a readable form; they are a review item.
- Status **Proposed**: the rules are the working basis of the build, not a reviewed
  methodology. The owner and an LCA expert decide; a change of system model or allocation
  method is a MAJOR change ([0012](0012-versioning-releases-and-dois.md)).

## Evidence

- `2f6c009` "LCI database: one declared system model (cut-off) and release governance" and
  `d39f60a` review fixes, [#68](https://github.com/ChemE-as-Code/process-library/pull/68) (closes #52).
- [system-model.md](../system-model.md) status banner ("draft for decision", coordinator's
  decisions of 2026-10-25), `lci/mappings.yaml` header and `allocation.asu-1`.
