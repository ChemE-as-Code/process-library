# Design extension: a 1 kg batch at fixed coverage

**HYPOTHETICAL design extension, not validated.** It uses our re-implementation of the source's
model (see `comparison.md`; verdict PARTIAL), our lumped kinetics, and the scale-up assumptions
in `inputs.yaml` (`extension`). No measured large-scale data exist for it. Numbers from
`results/comparison.json` (`extension`).

## Changed input

Batch size: 22.05 g of P-25 TiO2 (the source's lab case) increased to **1.0 kg**. Held fixed:
target coverage (pulse ends when the volume-mean site coverage reaches 0.99), TMA inlet
partial pressure 40 mbar (reconstructed for the lab case), superficial velocity 7 cm/s
(1.4 u_mf), 1.013 bar, 500 K, bed expansion H/H0 = 1.7. Two ways to fit 1 kg (7.7 l settled
powder at 130 kg/m3) into a bed:

- **Strategy A**, keep the settled height H0 = 60 mm and widen the bed (the source's rule,
  p. 189: tau_sat_min does not depend on d_t).
- **Strategy B**, keep the shape, H0/d_t = 1.

Bubble size in the scaled beds follows Darton et al. (1977) at mid-bed height. For the lab bed
the same correlation gives 1.05 cm, close to the source's 1 cm.

## Result

| | Lab (source case) | 1 kg, strategy A | 1 kg, strategy B |
| --- | --- | --- | --- |
| Bed diameter d_t | 60 mm | 404 mm | 214 mm |
| Settled / expanded bed height H0 / H | 60 / 102 mm | 60 / 102 mm | 214 / 364 mm |
| H0/d_t | 1.0 | 0.15 | 1.0 |
| Average bubble diameter d_b | 1.0 cm (source) | 1.05 cm | 2.14 cm |
| Bed height needed for 99.99 % uptake, H* (Eq. 7.52) | 9.2 cm | 10.0 cm | 31.0 cm |
| TMA feed during the pulse | 0.82 g/min | 37.3 g/min | 10.5 g/min |
| **TMA pulse to 99 % mean coverage** | **45.7 s** | **45.8 s** | **163.0 s** |
| TMA fed per pulse | 0.63 g | 28.5 g | 28.5 g |
| Precursor slip in the quasi-steady period, Eq. 7.51 (C_em = 0) | 4.2e-5 | 8.3e-5 | 2.4e-5 |
| Precursor slip at mid-pulse, our dynamic model | 7.4e-4 | 7.8e-4 | 2.1e-4 |
| Share of that slip leaving with the emulsion gas | 60 % | 57 % | 58 % |
| Precursor utilisation over the pulse (dynamic) | 99.91 % | 99.90 % | 99.97 % |
| Outlet C_TMA/C_in at pulse end | 4.0e-3 | 4.1e-3 | 1.1e-3 |
| Coverage at agglomerate centre at pulse end | 0.56 | 0.56 | 0.56 |
| Vessel: plenum + H + freeboard (TDH) + filter | 851 mm (60 mm ID) | 851 mm | 1113 mm |

Figures: `results/fig3-pulse-breakthrough-coverage.svg` (outlet precursor and coverage
against time for all three), `results/fig4-batch-sweep.svg` (pulse time and precursor slip from
22 g to 10 kg), `results/fig5-section-view-1kg.svg` (dimensioned section views of both 1 kg
vessels, drawn to scale).

## Engineering consequence

All statements hold in this model, with Darton bubble sizes and our lumped kinetics. Our K_be
is stronger than the source's at d_b <= 2 cm (Fig. 7.3: about 15 % at 1 cm; Fig. 7.4a at
u_mf = 5 cm/s: 2-9 % less H* than the source at 1-2 cm). The slip estimates below are
therefore optimistic by that margin.

- **In this model, precursor utilisation does not limit this scale-up at 1 atm.** In both
  strategies more than 99.9 % of the fed TMA is taken up before breakthrough. The outlet concentration stays
  at 2e-4 to 1e-3 of the inlet for most of the pulse, then breaks through sharply once the
  surface is nearly saturated: the bed acts as an adsorption column. TMA consumed per kg is set
  by the surface area (50 m2/g x 4.8 Al/nm2, about 28.5 g TMA per kg and half-cycle) and does not
  change with scale.
- **The pulse length is set by the settled bed height, not by the batch mass.** Pulse time is
  the number of surface sites per unit bed cross-section divided by the precursor flux per
  unit cross-section. Strategy A keeps H0 and therefore the 46 s pulse. It needs a 404 mm wide,
  shallow bed (H0/d_t = 0.15) and a 45-fold larger TMA delivery rate (37 g/min at 40 mbar).
  Strategy B needs only 13 times the lab TMA rate, but each TMA half-cycle takes 3.6 times as
  long (163 s), which cuts the cycles per hour.
- **A 99.99 % target is set by emulsion slip, not by bed height.** H* (Eq. 7.52) is the bed
  height for 1 - eta = 1e-4 when the emulsion concentration is zero. In our dynamic model the
  emulsion keeps about 2e-4 to 7e-4 of the inlet concentration in the quasi-steady period. The
  outlet slip is then 9 to 18 times the Eq. 7.51 value, and about 60 % of it leaves directly
  with the emulsion gas. Over the pulse, strategy A loses 0.095 % of the TMA, about ten times
  the 1e-4 that H* is sized for; strategy B loses 0.026 %. So H* < H does not mean that a
  99.99 % target is met. In our model this slip (2e-4 to 8e-4 at mid-pulse) is set by how fast
  the agglomerates take up TMA from the emulsion gas (film and pore diffusion with the lumped
  kinetics), not by the bubble exchange that H* sizes. It falls with the emulsion residence
  time: the 3.6 times deeper strategy-B bed has 2e-4. The source's own dynamic model may differ
  here; its kinetics are not given.
- **Bubble growth and bed depth.** In strategy B the larger bubbles (2.1 cm) need
  H* = 31 cm against 36 cm available. From 0.1 to 10 kg in
  strategy B, H*/H stays between 0.85 and 0.92 (`comparison.json` sweep), because the deeper
  bed compensates for the bubble growth it causes; in strategy A it stays at 0.98 (same bed
  height and bubble size as the lab bed). The 10 kg strategy-A point has H/d_t = 0.08, outside
  the source's back-mixing range (0.1 to 4); it is marked with a cross in fig4 and flagged in
  `comparison.json` (`in_range: false`). The margin is thin: with 4.5 cm bubbles in the
  strategy-B bed the precursor slip would rise to 1.7 % (eta 0.983), and with 8 cm bubbles to
  9.6 % (`sensitivity_db_strategy_B`). Bubble size is the number to measure before building.
- **Coverage uniformity inside agglomerates is the real quality risk at 1 atm.** With the
  agglomerates treated as rigid, as the source does, the reaction front moves inwards
  (Thiele modulus 8). At 99 % mean coverage the agglomerate centre is only 56 % covered,
  in every case, because this depends on the agglomerate, not on the bed. The source makes the same
  point. It adds (p. 195) that break-up and rearrangement of the agglomerates would level out
  the coverage, but only if their time scale is shorter than the diffusion time; that time
  scale is not known here. Extending the pulse beyond the 99 % point, or working at reduced pressure (Thiele
  modulus 1.6 at 1 mbar), is the design lever. It is not quantified here.
- **Choice.** For a fixed TMA delivery system, B (214 mm x 1.1 m) is the compact vessel with
  a 13-fold delivery rate. A keeps the lab cycle time but needs a wide, shallow bed, in which
  the distributor dominates gas distribution. At 1 kg its expanded H/d_t = 0.25 lies inside
  the range for which the source takes the solids as back-mixed (H/d_t from 0.1 to 4, p. 178;
  H0/d_t < 2 for P-25, p. 179); the lower limit is reached at about 6 kg.

## Scale-up assumptions (as drawn)

- Fluidisation velocity: u0 = 7 cm/s; u_mf = 5 cm/s (lab value for P-25, source ref. [38]),
  assumed independent of scale.
- Bed expansion: H/H0 = 1.7 (lab value), assumed independent of scale and bed shape.
- Bubble size: Darton et al. (1977) at mid-bed, distributor 1 cm2 per orifice.
- Freeboard: transport disengaging height TDH = 1000 u0^2/g = 0.50 m (Fournol et al. 1973,
  fine powders), plus 150 mm for filter candles (nanopowder elutriation) and 100 mm plenum.
- Geldart group: P-25 fluidises as agglomerates (d_ag about 300 um, rho_ag 47 kg/m3).
  (rho_p - rho_g) d_p = 14 g/cm3 um, far below the A/B boundary (about 225), so the bed is not
  group B. Whether it behaves as group A or C is not determined: the agglomerates lie off
  Geldart's chart, which was made for primary particles. The source treats it as a bubbling bed
  (agglomerate bubbling fluidisation, ABF).

## Out-of-range and extrapolation flags

- Batch mass 45 times the lab case; no data at this scale.
- Darton correlation and TDH correlation are for conventional group A/B powders, not
  nanoparticle agglomerates.
- Strategy A: H/d_t = 0.25 at 1 kg is inside the source's back-mixing range (0.1 to 4); the
  10 kg point (H/d_t = 0.08) is outside it and flagged. Distributor design and gas
  maldistribution are not modelled.
- Our bubble-emulsion exchange is stronger than the source's at d_b <= 2 cm, so the slip
  estimates are optimistic; the emulsion slip floor comes from our lumped kinetics.
- Lumped kinetics (not the source's Travis chemistry); TMA half-reaction only; the H2O
  half-reaction and the purges are not modelled, so the full cycle time is not given.
- P_TMA,in = 40 mbar was reconstructed from the source's saturation time. It is not a stated
  delivery condition. Pulse times scale as 1/P_TMA,in.
- Isothermal bed at 500 K. The reaction heat and the heating of a 1 kg batch are not assessed.
