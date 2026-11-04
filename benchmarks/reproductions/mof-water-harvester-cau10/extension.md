# Design extension: adsorbent bed for a CAU-10-H water harvester

> **HYPOTHETICAL design extension (not validated).** It uses the reproduced uptake series of
> sample 8 (comparison.md) as its only measured input. No harvester was built or measured. All
> design inputs and their labels are in `inputs.yaml`; numbers below are from
> `results/comparison.json` (`design_extension`).

## Question

How does the inlet humidity change the mass of adsorbent needed to collect a stated amount of
water per cycle?

## Design basis

| Input | Value | Label |
| --- | --- | --- |
| Water collected per cycle | 1.0 kg | assumed |
| Collection recovery (collected / desorbed) | 0.80 | assumed |
| Adsorption: bed and inlet air | 313.15 K, equilibrium with the inlet air | assumed (within 0.15 K of the isotherm temperature, 313.0 K; run.py stops above 0.5 K) |
| End-of-adsorption loading | adsorption branch at the inlet RH | measured points, linear interpolation (no measured point between p/p0 0.0836 and 0.1777) |
| Regeneration state | p/p0 0.05 at the bed, desorption branch: 0.0156 g/g | measured loading (interpolated between the two lowest desorption points, 0.0317 and 0.0705), assumed state |
| Condenser | 30 °C (4.25 kPa) | assumed |
| Regeneration temperature | 85.1 °C, from p/p0 0.05 and the condenser pressure | reconstructed, **extrapolated** (characteristic curve outside 288 K to 313 K) |
| Adsorption enthalpy | 2641 kJ/kg (47.6 kJ/mol) = h_fg 2406 kJ/kg + R T ln(1/α) | reconstructed (Dubinin relation; not measured); assumed range ±10 % |
| Adsorbent heat capacity | 0.90 kJ/(kg K) | assumed |
| Packed bed density | 600 kg/m3 | assumed |
| Cycle | 1 per day, 6 h desorption | assumed; affects only daily yield and mean heat duty |

Sizing: working capacity Δq = q_ads(RH) − q_des(0.05); adsorbent mass m = yield / (recovery × Δq);
packed volume V = m / ρ_bed. Mass is per kilogram of pellets as measured (binder included).

**Interpolation bounds.** The isotherm is monotonic, so the uptake at any RH lies between the
uptakes at the two measured points either side. run.py reports these bounds beside every
linear value (`interpolation_bounds`) and marks a segment as wide when the uptake changes by
more than 10 % across it or the points are more than 0.01 apart in p/p0. On the plateau the
bounds are narrow (base case 4.6 to 4.8 kg); below the step they are not.

## Result: required adsorbent against inlet humidity

Figure: `results/harvester_mass_vs_rh.svg` (run.py; not committed, see README.md). It shows the
linear value, the bounds as a band and the unmeasured gap.

| Inlet RH at 313 K | Vapour in air | Working capacity (bounds) | Adsorbent (bounds) | Packed volume | Flag |
| --- | --- | --- | --- | --- | --- |
| 0.15 | 7.7 g/m3 | 0.0024 g/g (0 to 0.0052) | 519 kg (242 kg to unbounded) | 865 L | infeasible; interpolated across the unmeasured gap |
| 0.18 | 9.2 g/m3 | 0.0070 g/g (0.0052 to 0.0152) | about 180 kg (82 to 242) | about 300 L | infeasible |
| 0.19 | 9.7 g/m3 | 0.015 g/g (0.0052 to 0.0152) | 83 kg (82 to 242) | 139 L | infeasible, on the step |
| 0.195 | 10.0 g/m3 | 0.066 g/g (0.057 to 0.067) | 19 kg (18.6 to 22.0) | 32 L | on the step |
| 0.20 | 10.2 g/m3 | 0.183 g/g (0.182 to 0.193) | 6.8 kg (6.5 to 6.9) | 11.4 L | on the step |
| 0.22 | 11.2 g/m3 | 0.253 g/g (0.243 to 0.253) | 4.9 kg (4.9 to 5.1) | 8.2 L | |
| 0.30 | 15.3 g/m3 | 0.269 g/g (0.262 to 0.269) | 4.65 kg (4.6 to 4.8) | 7.7 L | base case |
| 0.42 | 21.5 g/m3 | 0.281 g/g (0.276 to 0.282) | 4.44 kg (4.4 to 4.5) | 7.4 L | highest supported RH |

Below an inlet RH of 0.193 the working capacity is less than 10 % of the plateau value
(0.028 g/g, threshold in `inputs.yaml`). The crossing is solved on the interpolant at 0.1928
and lies in the measured segment 0.1926 to 0.1935, so this limit is well constrained. Where the
bed stops taking up any water beyond its regeneration loading is not known: the crossing lies
somewhere between p/p0 0.084 and 0.178, where no adsorption point was measured (linear
interpolation would put it at 0.126). The infeasibility below the step does not depend on the
gap: everywhere in it the working capacity is at most 0.0052 g/g, against the 0.028 g/g
threshold.

The step runs from RH 0.189 to 0.219 (10 % to 90 % of capacity), with its inflection at 0.197.
On the step a change of 0.01 in RH changes the mass by up to a factor of ten, so a design point
there is not robust. Above the step the mass is almost flat: from RH 0.22 to 0.42 it falls by
only 10 %.

## Changed-input example: inlet RH 0.30 → 0.18

The changed point lies between the measured adsorption points 0.1777 and 0.1903, across which
the uptake rises by 48 %. The linear value is quoted with its bounds and rounded accordingly.

| | Base, RH 0.30 | Changed, RH 0.18 (bounds) | Change (bounds) |
| --- | --- | --- | --- |
| Working capacity | 0.269 g/g | about 0.007 g/g (0.0052 to 0.0152) | ÷ about 38 (18 to 52) |
| Adsorbent for 1 kg per cycle | 4.65 kg | about 180 kg (82 to 242) | × about 38 (18 to 52) |
| Packed volume | 7.7 L | about 300 L (137 to 404) | × about 38 (18 to 52) |
| Regeneration heat per kg water collected | 3.74 MJ (1.04 kWh) | about 11 MJ, 3.1 kWh (2.0 to 3.9 kWh) | × about 3 (1.9 to 3.8) |
| of which desorption enthalpy | 3.30 MJ | 3.30 MJ | same |
| of which heating the bed | 0.44 MJ | about 8 MJ (3.8 to 10.8) | × about 18 (9 to 25) |
| Mean heat duty over 6 h | 173 W | about 525 W (330 to 650) | × about 3 (1.9 to 3.8) |

**Physical interpretation.** The inlet air carries 40 % less water (15.3 to 9.2 g/m3), but the
adsorbent needed rises by a factor of about 38, and by at least 18 whatever the uptake between
the two measured points. At RH 0.30 the bed is on the plateau of the isotherm, above the step;
at RH 0.18 the step has not been reached, and the bed holds little more water than it still
holds after regeneration. The article explains the step by the formation of a water cluster in
the hydrophobic pores (pp. 6 to 7, powder and single crystal); this case uses only the pellet
uptake series and does not test that mechanism. The harvester then cycles almost dry pellets:
most of the regeneration heat goes into warming the bed rather than desorbing water. For this
adsorbent the feasible design condition is a threshold, the step position, not a gradual
trade-off with humidity.

## Sensitivity of the base case (one at a time)

| Change | Result |
| --- | --- |
| Regeneration p/p0 0.0317 or 0.0705 (the two lowest measured desorption points, which bracket the regeneration state) | 4.62 or 4.68 kg |
| Recovery 0.6 or 0.9 | 6.20 or 4.13 kg |
| Packed density 400 or 800 kg/m3 | 11.6 or 5.8 L |
| Adsorption enthalpy −10 % or +10 % | base 0.95 or 1.13 kWh/kg; changed case 3.06 or 3.24 kWh/kg |
| Uptake between the measured points either side | base 4.6 to 4.8 kg; changed case 82 to 242 kg (table above) |

The regeneration loading rests on those two desorption points only, but it hardly matters on
the plateau, because it is small (0.014 to 0.018 g/g) against 0.28 g/g. Mass scales with
1/recovery and volume with 1/density, both assumed. The adsorption enthalpy range moves the
regeneration heat by about ±9 % in the base case and ±3 % in the changed case, where bed
heating dominates.

## Out-of-range and extrapolation flags

- **Inlet RH above 0.4246** is outside the measured series; the sweep stops at 0.42.
- **Unmeasured gap, p/p0 0.0836 to 0.1777.** Values in it (the RH 0.15 row, the point of zero
  working capacity) are interpolated across 0.094 in p/p0 and are reported with bounds.
- **Temperature.** All loadings are read at 313 K, and run.py stops if the bed temperature
  differs from it by more than 0.5 K. If the characteristic curve holds, colder night air at
  25 °C, with the bed at 25 °C, would step at RH 0.182 (4.2 g/m3) instead of 0.197
  (10.0 g/m3 at 40 °C). That would widen the feasible region in absolute humidity by more than
  a factor of two, so bed temperature could matter as much as humidity. This is an
  extrapolation and is not used in the sweep.
- **Regeneration temperature 85 °C** comes from the same characteristic curve, outside the
  288 K to 313 K range over which the article reports little temperature effect.
- **Adsorption enthalpy** is estimated, not measured; with only one isotherm temperature no
  isosteric heat can be fitted from the data.
- **Equilibrium in each half-cycle** is assumed. Mass transfer, the heat released during
  adsorption, pressure drop and air flow are not modelled, so the mass is a lower bound.
  Cycle time does not change the mass per cycle; it sets how much water per day a given bed
  makes (here 1 kg per day for 4.65 kg of pellets at one cycle per day).
- **Heat** excludes the housing, the heat exchanger and losses; it is a lower bound.
- **Low-pressure hysteresis** (comparison.md, item 5) is handled conservatively by reading the
  regeneration loading from the desorption branch. The desorption branch is read only below
  p/p0 0.1855, where it is monotonic.
