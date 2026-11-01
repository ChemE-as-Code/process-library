# Comparison: IDAES HDA tutorial vs cheme IDAES backend

- **Reference:** `source.yaml` (examples-pse `b9606ee`, base case, reported test assertions).
- **Tolerances:** `tolerances.yaml`, frozen in commit 1979740 before this run.
- **Run:** `case/`, `cheme process simulate --fill`, cheme-as-code 1.3.0 from core#104 worktree
  commit 00f519a, idaes-pse 2.13.0, IPOPT 3.13.2, property package `IDAES ideal VLE`, 2026-11-01;
  converged in 66 IPOPT iterations (`case/process/simulation-run.json`; its `dirty` list is
  because the run preceded the case commit, the inputs are unchanged since).

## Result: FAIL under the frozen rule (3 of 5 checks pass)

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
  not converge** ("IPOPT did not converge: other"), while the first run from empty streams
  converged. The filled values are used as the tear-stream first guess, so a warm start from
  the converged solution fails. Reproducible with `case/` as committed.
- The optimised case of the tutorial (`source.yaml` optimised_case) is out of scope: cheme has
  no optimisation.
- Pinned library CI (core v1.2.1) rejects `simulator: idaes` (`cheme.process-sim-schema`), but
  CI validates only `processes/*/plant.yaml`, so this folder does not break CI.

Tolerances were not changed after the run. A follow-up that adds dissolved light gases to the
backend should re-run against the same `tolerances.yaml`.
