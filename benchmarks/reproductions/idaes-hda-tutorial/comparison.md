# Comparison: IDAES HDA tutorial vs cheme IDAES backend

- **Reference:** `source.yaml` (examples-pse `b9606ee`, base case, reported test assertions).
- **Tolerances:** `tolerances.yaml`, frozen in commit 1979740 before this run.
- **Run:** `case/`, `cheme process simulate --fill`, cheme-as-code 1.3.0 from core#104 worktree
  commit 00f519a, idaes-pse 2.13.0, IPOPT 3.13.2, property package `IDAES ideal VLE`, 2026-11-01;
  converged in 66 IPOPT iterations (`case/process/simulation-run.json`). Its `dirty` list is
  there because the run preceded the case commit. The specification inputs are unchanged since
  then, but the recorded `flowsheet.yaml` fingerprint is the pre-fill one: `--fill` rewrote that
  file with the solved stream values afterwards, so the committed `flowsheet.yaml` no longer
  matches it.
- **Order:** the repository holds one run record, `case/process/simulation-run.json`. It is pinned
  to commit 1979740 (`inputs.commit`), and its `run_at` (2026-11-01T10:31:38Z) is 70 s after
  that commit (10:30:28Z). No earlier run is recorded in the repository. The record cannot show
  that no uncommitted run happened before the freeze; the claim rests on this order.
- **Released core (2026-11-02):** the case was run again with core **v1.4.0** (704d1c4, the
  release with the IDAES backend; idaes-pse 2.13.0, IPOPT 3.13.2) from empty streams: the
  committed `flowsheet.yaml` with every `origin: simulated` value removed, in a scratch copy.
  Same model fingerprint (`59bf0c23c6278299`), converged in 66 iterations, and every stream and
  unit value in the run record identical (largest relative difference 0). The committed record
  above is therefore kept; the result below holds for the released backend.

## Result: FAIL under the frozen rule (3 of 5 checks pass; 1 of 3 against reference results)

Of the five checks, two are not comparisons with reference results: the F102 vapour pressure is
a specification that both models fix, and the overall mass closure is an internal check of the
cheme run. Against reference results (purity, F102 duty, operating cost), 1 of 3 passes.

| Check | Reference | cheme (IDAES backend) | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| Benzene purity, F102 vapour (BZ/(BZ+TOL)) | 0.82429 | 0.81722 | -0.00707 | abs 0.005 | **fail** |
| F102 heat duty | 7352.48 W | 7822.99 W | +6.40 % | rel 5 % | **fail** |
| F102 vapour pressure | 150000 Pa | 150000 Pa | 0 | abs 100 Pa | pass |
| Operating cost (reference formula on cheme duties) | 419122 $/a | 411265 $/a | -1.87 % | rel 5 % | pass |
| Overall mass closure | - | 102.84408 in, 102.84410 kg/h out | 1.9e-7 | rel 1e-4 | pass |

Operating cost uses the reference's cost coefficients (`source.yaml` derived_quantities) on
cheme's duties: H1 47.259 kW, E1 + F1 -54.610 kW (F101), R1 0 kW, F2 7.823 kW.

cheme values with no reported counterpart (not compared): R1 outlet 671.06 K, reaction extent
0.8438 kmol/h, F102 vapour 53.83 kg/h, purge 24.61 kg/h.

## Deviations and explanations

1. **Light gases in the liquid (structural, most likely main cause of both failures).** The
   tutorial's own property module (`hda_ideal_VLE.py` at the pinned commit) puts hydrogen and
   methane in vapour-liquid equilibrium as well; the cheme backend's `IDAES ideal VLE` keeps them
   vapour-only (core#104, docs/framework/idaes.md). In the reference some H2/CH4 leaves F101 in
   the liquid and flashes off in F102, which changes F102's duty and its benzene/toluene split.
   Not yet quantified (it needs the reference run with stream tables, or an option in core).
2. **Different pure-component data.** The reference uses the tutorial module's own
   vapour-pressure and heat-capacity data; cheme builds its package from IDAES's generic
   `BT_ideal` and `HC_PR` data. This affects the F101/F102 splits and all duties at a smaller
   level (the operating-cost agreement within 2 % bounds the duty-weighted effect).
3. **Isothermal compressor C101 omitted.** It runs at pressure ratio 1 (F101 at 350 kPa with no
   pressure drop, outlet fixed at 350 kPa), so it changes no state; the cheme IDAES backend
   refuses compressors with ideal VLE in any case. cheme's loop settles at 349.983 kPa rather
   than 350 kPa (mixer at lowest inlet pressure around the tear); effect negligible.
4. **F101 as cooler E1 + flash F1.** Equivalent to a flash with heat transfer at 325 K and no
   pressure drop; F1's own duty is ~0 W.
5. **Trace feeds omitted.** The reference fixes 1e-5 mol/s for every absent phase-component
   (about 1e-4 of the feed); cheme feeds are pure. Negligible.

## Gaps found (reported, not fixed here)

- core#104: no option to let H2/CH4 dissolve in the liquid (or to use the tutorial's package), so
  an exact reproduction of the tutorial is not possible with the backend as it is.
- core#104: no isothermal compressor and no compressor with ideal VLE (not needed here, ratio 1).
- core#104: **re-running `cheme process simulate --fill` (and `--check`) on the filled case did
  not converge** (still so with core v1.4.0) ("IPOPT did not converge: other"), while the first run from empty streams
  converged. The filled values are used as the tear-stream first guess, so a warm start from
  the converged solution fails. Reproducible with `case/` as committed.
- The optimised case of the tutorial (`source.yaml` optimised_case) is out of scope: cheme has
  no optimisation.
- Library CI validates only `processes/*/plant.yaml`, so this folder is not validated by CI.
  With core v1.4.0, which knows `simulator: idaes`, `cheme validate` in `case/` passes.

## Other simulators

A DWSIM run of the hda-1 design now exists (library PR #312). It is not comparable with this
case: it differs in scale, pressures, property basis and separation train, so it cannot serve
as a third leg here. The real third leg would be a DWSIM run of the tutorial case itself, with
the specification in `source.yaml`.

Tolerances were not changed after the run. A follow-up that adds dissolved light gases to the
backend should re-run against the same `tolerances.yaml`.
