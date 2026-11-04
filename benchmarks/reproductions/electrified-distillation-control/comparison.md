# Comparison: Cui et al. (2025) FVC column, CS1 against CS2, with our tray-by-tray model

- **Reference:** `source.yaml`. Cui, Zhang, Qi and Kiss, Chem. Eng. Res. Des. 220 (2025) 450-460,
  doi 10.1016/j.cherd.2025.07.023, CC BY 4.0, final published version. Its supporting-information
  workbook (sha256 `4f57888e...a575`) holds the Aspen Plus stream and stage tables and the eight
  Aspen Dynamics time series. Every SI value below is the one run.py reads from that file.
- **Tolerances:** `tolerances.yaml`, frozen in commit 9aeb7614 with `source.yaml` and
  `inputs.yaml`, before any run that compared our values with the reported ones. Not changed since:
  `git diff 9aeb7614 HEAD -- benchmarks/reproductions/electrified-distillation-control/tolerances.yaml`
  is empty.
- **Run:** `uv run benchmarks/reproductions/electrified-distillation-control/run.py` from the
  repository root, 2026-11-04, from an empty cache (the SI downloaded and hash-checked). Python
  3.13.16, numpy 2.3.4, scipy 1.16.3, matplotlib 3.10.7, openpyxl 3.1.5, pyyaml 6.0.3; 150 s on
  a laptop. Output: `results/comparison.json` and five SVG figures. A second run in a separate copy
  gave byte-identical results.
- **Model:** our own, described in `inputs.yaml`. It has 38 equilibrium stages plus the drum
  (FLASH-D) and the reboiler flash (FLASH-R), and a quasi-steady energy balance per stage. NRTL
  parameters are fitted to the SI stage equilibrium data, and enthalpies to the SI stage and stream
  enthalpies. Hydraulics follow the Francis weir. The heat pump is quasi-steady, with one capacity
  parameter (kappa) calibrated on the CS1 +20 % throughput case. Controllers are tuned by
  Tyreus-Luyben on our linearised model. It is not the authors' Aspen model, which is not public.

## Result: PARTIAL under the frozen rule (18 of 19 primary checks pass; both direction checks pass)

The pass rule (`tolerances.yaml`) gives *partial* when at least 75 % of the primary checks pass
and both direction checks pass. One primary check fails: the CS1 distillate purity after the -20 %
methanol step.

### Nominal steady state (our model solved at the reported purities 0.99 and 0.9999)

| Check | Reference (SI / text) | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| Reflux ratio | 0.64636 | 0.65886 | +1.9 % | rel 10 % | pass |
| Reboiler duty (HEX1+HEX2+HEX3) | 1425.5 kW | 1443.1 kW | +1.2 % | rel 5 % | pass |
| Conventional condenser duty (V_top x latent heat) | 1307 kW | 1312.8 kW | +0.4 % | rel 5 % | pass |
| Total compressor power | 303.05 kW | 306.8 kW | +1.2 % | rel 5 % | pass |
| Stage 35 temperature | 88.91 C | 89.37 C | +0.46 K | abs 2 K | pass |
| Temperature profile, RMS over 38 stages | - | 0.17 K | - | abs 1 K | pass |
| Liquid methanol profile, RMS over 38 stages | - | 0.0043 | - | abs 0.02 | pass |

Not compared, ours only: COP 4.70 (text 4.72), overhead vapour 134.0 kmol/h (SI 133.0), FVC
8.0 kmol/h (SI 7.3), trim condenser 176 kW (SI 184.6). The NRTL fit gives b12 = -148.1 K and
b21 = 478.1 K (alpha 0.3). It reproduces the 40 SI equilibrium points to 0.08 K RMS in bubble
temperature and 0.0014 RMS in vapour mole fraction. The enthalpy fit reproduces the SI to 82 kJ/kmol
(liquid) and 13 kJ/kmol (vapour) RMS.

### Feed composition steps, values at 10 h

| Check | Reference (SI at 10 h) | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| CS1 +20 % methanol, distillate x_D | 0.99799 | 0.99875 | +0.00076 | abs 0.002 | pass |
| CS1 -20 % methanol, distillate x_D | 0.97836 | 0.97306 | **-0.00529** | abs 0.003 | **fail** |
| CS2 +20 % methanol, x_D | 0.99007 | 0.99000 | -0.00007 | abs 0.001 | pass |
| CS2 -20 % methanol, x_D | 0.99000 | 0.99000 | 0.00000 | abs 0.001 | pass |
| CS2 +20 % methanol, reflux ratio | 0.30311 | 0.28446 | -6.2 % | rel 15 % | pass |
| CS2 -20 % methanol, reflux ratio | 0.72118 | 0.76218 | +5.7 % | rel 10 % | pass |
| CS1 +20 % methanol, compressor power | 441.1 kW | 418.1 kW | -5.2 % | rel 10 % | pass |
| CS1 -20 % methanol, compressor power | 247.1 kW | 257.2 kW | +4.1 % | rel 10 % | pass |
| CS2 +20 % methanol, compressor power | 283.0 kW | 284.0 kW | +0.4 % | rel 10 % | pass |
| CS2 -20 % methanol, compressor power | 255.5 kW | 266.5 kW | +4.3 % | rel 10 % | pass |
| Direction: CS2 recovers purity | CS1 offsets +0.0080 / -0.0116; CS2 0.0001 / 0.0000 | CS1 +0.0088 / -0.0169; CS2 < 1e-7 | - | CS2 offset < 0.25 CS1 offset | pass |
| Direction: CS2 needs less power at +20 % methanol | 283 < 441 kW | 284 < 418 kW | - | - | pass |

The end values are steady: a direct steady-state solution of our model with the same control
specifications gives the same purities, reflux ratios and powers to four or more digits
(`scenarios_steady_state_solution` in comparison.json).

### Secondary checks (reported, not part of the verdict): 14 of 21 within tolerance

| Check | Reference | Ours | Ratio or deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| IAE x_D, CS1 +20 % MeOH | 0.0705 h | 0.0717 h | 1.02 | 0.5-2 | pass |
| IAE x_D, CS1 -20 % MeOH | 0.1007 h | 0.1274 h | 1.26 | 0.5-2 | pass |
| IAE x_D, CS2 +20 % MeOH | 0.0114 h | 0.0025 h | 0.22 | 0.5-2 | fail |
| IAE x_D, CS2 -20 % MeOH | 0.0031 h | 0.0009 h | 0.28 | 0.5-2 | fail |
| IAE bottoms water, CS1 +20 % / -20 % | 0.00262 / 0.00036 | 0.00035 / 0.00072 | 0.13 / 1.97 | 0.33-3 | fail / pass |
| IAE bottoms water, CS2 +20 % / -20 % | 0.00196 / 0.00043 | 0.00037 / 0.00072 | 0.19 / 1.66 | 0.33-3 | fail / pass |
| Settling of x_D (our rule on both), CS1 +20 % / -20 % | 1.33 / 1.60 h | 2.76 / 4.35 h | 2.08 / 2.72 | 0.5-2 | fail / fail |
| Settling of x_D, CS2 +20 % / -20 % | 5.41 / 1.93 h | 2.75 / 1.23 h | 0.51 / 0.64 | 0.5-2 | pass / pass |
| FVC flow at 10 h, CS1 +20 % / -20 % | 41.4 / 7.3 kmol/h | 34.2 / 10.0 | -7.2 / +2.7 | abs 5 | fail / pass |
| FVC flow at 10 h, CS2 +20 % / -20 % | 4.9 / 7.6 kmol/h | 7.0 / 9.5 | +2.1 / +1.9 | abs 5 | pass / pass |
| Direction: CS2 needs more power at -20 % MeOH | 255.5 > 247.1 kW | 266.5 > 257.2 kW | - | - | pass |
| CS1 -20 % throughput: power / x_D | 235.5 kW / 0.99076 | 245.2 kW / 0.99000 | +4.1 % / -0.0008 | rel 10 % / abs 0.002 | pass / pass |
| CS2 +20 % / -20 % throughput: reflux ratio | 0.6559 / 0.6380 | 0.6589 / 0.6589 | +0.5 % / +3.3 % | rel 5 % | pass / pass |

Source-internal check: Table 2's sixteen IAE values follow from the SI series (trapezoidal integral
of |x_D - 0.99| and |x_B,water - 0.9999| over 0-10 h, time in hours) to within 2.5 %
(`table2_vs_SI_series`). Table 1's settling times do not follow from any simple band rule we tried,
so settling is compared like-for-like: the last time after the step at which x_D differs from its
10 h value by more than 5e-4, applied to both models.

## The engineering question

**Does composition feedback recover purity after a feed composition change? Yes.** CS1 holds stage
35 but leaves the distillate off specification. Ours gives +0.0088 at 0.96 feed methanol (source
+0.0080) and -0.0169 at 0.64 (source -0.0116). CS2 returns x_D to 0.99 in both cases, by moving
the reflux ratio to 0.284 and 0.762 (source 0.303 and 0.721).

**How does compressor power respond?** At +20 % methanol, CS1 raises the power from 307 to 418 kW
(+36 %; source 303 to 441 kW, +46 %). CS2 lowers it to 284 kW (-7 %; source 283 kW, -7 %).
Under CS1 the fixed reflux ratio drives the overhead vapour up with the distillate flow. Above the
design load the exchangers no longer condense all the compressed vapour, the flash vapour
circulation rises from 8 to 34 kmol/h (source 7 to 41) and the COP falls from 4.70 to 4.01
(source 4.72 to 3.74). CS2 cuts the reflux, so the load stays below design and the COP stays at
4.71. At -20 % methanol both structures need less power than at nominal; CS2 needs 4 % more than
CS1 (ours 266 against 257 kW, source 255 against 247 kW), the price of holding 0.99.

**Sensitivity.** The sensitivity study (`fig_sensitivity.svg`, comparison.json `sensitivity`)
varied the following and re-ran all four composition cases:

- weir height and column diameter (tray holdup from about x0.5 to x2);
- drum, sump and FLASH-R holdups;
- TC and CC gains and integral times (x0.5 and x2);
- the analyser deadtime (6 and 10 min, retuned);
- the exchanger-capacity parameter kappa (0.10, 0.30, and no limit);
- the NRTL alpha (0.2 and 0.4, refitted).

The conclusion (CS2 recovers purity and needs less power at +20 % methanol) holds in all 24
variants. The end values do not depend on holdups or tuning: CS1 x_D at -20 % stays within
0.9731-0.9733 and CS2 reflux ratio at +20 % within 0.284-0.313. Only kappa moves the CS1 power at
+20 % methanol: 495 kW (kappa 0.10), 418 kW (0.19, calibrated), 380 kW (0.30) and 356 kW (no
capacity limit), against 441 kW in the source. The CS2 power does not move (284 kW in every
variant), because CS2 stays below the design load. The transient metrics do depend on what we
reconstructed. The CS2 IAE at +20 % methanol ranges from 0.0013 to 0.021 h, the latter with a
10 min analyser deadtime, which brackets the source's 0.0114 h. The CS2 settling time ranges from
2.0 to 7.4 h, against 5.4 h for the source by the same rule.

## Deviations and explanations

1. **CS1 at -20 % methanol (the failed check).** Our column loses more purity at a fixed reflux
   ratio when the feed is leaner: -0.0169 against -0.0116. The same shows in CS2, which needs
   reflux ratio 0.762 against the source's 0.721 to hold 0.99 (+5.7 %). Our nominal reflux ratio
   is 1.9 % higher than the source's. Together these say that our column has slightly less
   separating margin than the Aspen column, and the margin matters most when the feed moves away
   from the top pinch. The deviation is the same in every holdup, tuning and NRTL-alpha variant,
   so it is a steady-state difference. Possible causes we cannot separate without the Aspen file:
   the source's property method (not stated); pressure drops that vary with vapour load in Aspen
   Dynamics, which are fixed in ours; our quasi-steady energy balance; and vapour-pressure
   extrapolation of the NIST Antoine sets beyond their ranges (methanol above 357 K, water outside
   344-373 K). Not adjusted after the run.
2. **Compressor power at +20 % methanol under CS1 (-5 %, within tolerance).** It rests on the
   heat-pump capacity closure. The closure has one parameter, calibrated on the CS1 +20 %
   throughput case, where our model gives 441 kW against the source's 452 kW. The SI shows that
   the source's specific compressor work rises from 7.77 to 8.05 kJ/mol at high FVC flow; ours is
   constant. That explains about 3 of the 5 %. Exchanger UA, areas, pressure-drop coefficients and
   compressor maps are not published.
3. **Faster CS2, slower CS1 than the source (secondary).** Our CS2 settles in about half the source's
   time and has a quarter of its IAE. The paper attributes the slow CS2 to the 3 min analyser lag
   and to transport delay in the variable FVC flow. Our model has the analyser lag, but no
   transport delay: the heat-pump loop has no inventory. With a 10 min effective deadtime our CS2
   is as slow as the source's. Our CS1 drifts to its new purity more slowly (settling 2.8 and 4.4 h
   against 1.3 and 1.6 h), so the tray and drum holdups we assumed are probably larger in effect
   than the Aspen ones, or our tray hydraulics are slower. Table 1 cannot settle this, as its
   definition is not stated.
4. **Throughput steps.** Our model is scale-invariant: with fixed pressures and constant tray
   efficiency a feed-flow step moves all flows in proportion and leaves the reflux ratio needed for
   0.99 unchanged (0.6589). The source's reflux ratio moves to 0.656 and 0.638, presumably through
   load-dependent pressure drops. Within the 5 % secondary tolerance; outside the issue's question.
5. **Text against SI.** Section 3.2 of the article gives 99.76 and 97.75 mol% for CS1. The SI series
   end at 0.99799 and 0.97836. We compared with the SI.
6. **Stage numbering.** The paper counts the drum as stage 1, so its "feed stage 30" is block
   stage 29. The SI variable for the temperature controller is block Stage(35), which is what we use.

## Gaps found (reported, not fixed here)

- No Aspen Plus or Aspen Dynamics files are public. Tray hydraulics, exchanger UA and pressure
  drops, compressor maps and the Tyreus-Luyben results are not reported, so the transient shape
  (IAE, settling) cannot be reproduced except by reconstruction.
- The property method is not stated. We fitted NRTL to the SI's own equilibrium data rather than
  use a commercial databank, which would also be barred by the library's licence rule.
- The settling-time definition of Table 1 is not stated.
- cheme 1.2.1 (installed) can draw the control-loop P&ID from a script (`case/`), but holds no
  dynamic column model. The dynamics live in run.py (see README, core capability gap).
- Library CI does not check `benchmarks/reproductions/` (ADR 0030). `cheme validate` in `case/`
  passes with 0 errors and 11 drawing warnings (line crossings).
