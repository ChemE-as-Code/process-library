# Design extension (HYPOTHETICAL, not validated): a tighter distillate specification under CS2

**Status: hypothetical design extension.** It uses our reconstructed model outside the source's
cases: no published simulation or measurement covers it, and nothing here is reproduction or
validation. Numbers from `results/comparison.json`, `extension_HYPOTHETICAL`; figure
`results/fig_extension_operating_map.svg`.

## Changed input

One input changes: the CS2 composition set point, from **0.99 to 0.995 mol/mol methanol** in the
distillate (inputs.yaml `design_extension`). Everything else stays as in the reproduction: feed
100 kmol/h at 30 C, stage-35 temperature held by TC, the same heat-pump closure and the same
tuning. Steady states are solved directly; a 10 h dynamic run checks the set-point step at nominal
feed.

## Result

| Feed methanol | x_D set point | Reflux ratio | Reboiler duty | Compressor power | FVC flow | Bottoms water |
| --- | --- | --- | --- | --- | --- | --- |
| 0.64 | 0.990 | 0.762 | 1254 kW | 267 kW | 9.6 kmol/h | 0.99982 |
| 0.64 | 0.995 | 0.804 | 1274 kW | 271 kW (+1.6 %) | 9.4 kmol/h | 0.99982 |
| 0.80 | 0.990 | 0.659 | 1443 kW | 307 kW | 8.0 kmol/h | 0.9999 |
| 0.80 | 0.995 | 0.718 | 1481 kW | 327 kW (+6.7 %) | 13.5 kmol/h | 0.9999 |
| 0.96 | 0.990 | 0.284 | 1337 kW | 284 kW | 7.1 kmol/h | 0.99994 |
| 0.96 | 0.995 | 0.490 | 1523 kW | 349 kW (+23 %) | 17.9 kmol/h | 0.99994 |

The set-point step 0.99 to 0.995 at nominal feed settles in 0.5 h (|x_D - 0.995| < 5e-4) and ends
at reflux ratio 0.718 and 327 kW. Over the feed range 0.60-0.97 the steady compressor power peaks
at 370 kW at 0.92 feed methanol with the 0.995 set point, against 333 kW at 0.89 with 0.99.

## Engineering consequence

Halving the methanol-product impurity from 1.0 to 0.5 mol% costs little at a lean feed (+1.6 %
power at 0.64) and most at a rich feed (+23 % at 0.96). With a rich feed, CS2 holds 0.99 at a very
low reflux ratio (0.28). A tighter product needs the reflux ratio almost doubled (0.49), and the
extra boil-up pushes the heat pump above its design load. The trim condenser then rejects more of
the compressed vapour, and the flash vapour circulation rises to 18 kmol/h. In physical terms, the
reflux saving that makes CS2 attractive at rich feeds is largely spent when the specification
tightens.

Even so, on this model the power demand with the 0.995 set point stays below what our model's CS1
already needs inside the source's ±20 % envelope. The comparison is made within our model, at each
value of the capacity parameter kappa, because power above the design load depends on kappa
(comparison.json `extension_HYPOTHETICAL.peak_power_and_envelope_against_kappa`):

| kappa | Peak power, CS2 x_D 0.995 (at 0.92 feed methanol) | Peak power, CS2 x_D 0.99 (at 0.89) | Our CS1, +20 % methanol | Our CS1, +20 % throughput |
| --- | --- | --- | --- | --- |
| 0.10 | 418 kW | 354 kW | 495 kW | 531 kW |
| 0.19 (calibrated) | 370 kW | 333 kW | 418 kW | 441 kW |
| 0.30 | 348 kW | 323 kW | 380 kW | 396 kW |

At every kappa the 0.995 peak lies below both: 8-16 % below our CS1 +20 % methanol power and
12-21 % below our CS1 +20 % throughput power, with the smallest margin at kappa 0.30. The demand rests on two simplifications that bias it low above the
design load: the constant specific compressor work (the source's rises from 7.77 to 8.05 kJ/mol at
high FVC flow, comparison.md deviation 2) and the quadratic shape of the capacity closure. The
statement is therefore about power demand on this model, not about equipment: the installed
compressor rating (volumetric flow at suction, head, compressor maps, surge margin) is not
modelled and is not assessed here.

## Flags (out of range, extrapolation)

- The 0.995 specification lies outside every case the source simulated (all at 0.99).
- Feed fractions below 0.64 and above 0.96 lie outside the source's composition cases (grey bands
  in the figure).
- Compressor flows stay inside the range the capacity closure was calibrated over, expressed as
  the load ratio m_c / m_c0 to which the closure is applied: up to 1.441 (SI +20 % throughput
  over SI nominal, 202.2 / 140.3), which is 204.7 kmol/h in our model (m_c0 = 142.1 kmol/h). The
  largest flows are 171 kmol/h (ratio 1.21) for CS2 with 0.995 and 196 kmol/h (1.38) for CS1 at
  0.97 feed methanol. Each point in comparison.json carries this flag when it applies, together
  with the set-point and feed-range flags. The closure's shape between the two calibration points
  is assumed (quadratic), so powers above the design load carry the kappa uncertainty in the
  table above.
- At 0.96 feed with the 0.99 set point, the reflux ratio (0.284) is below the lowest the source
  reports (0.303); flagged in comparison.json.
- The vapour-pressure sets are extrapolated beyond their published ranges (inputs.yaml). The NRTL
  parameters are fitted to the SI profile, which spans the whole liquid range at the column's
  pressures.
- Tray hydraulics and holdups are assumed (inputs.yaml); they do not change steady states but do
  change the 0.5 h settling time.

Specialist review: not yet (optional follow-up, see README).

Source data in the figure (open markers): Cui et al. (2025), CC BY 4.0, replotted (NOTICE.md).
