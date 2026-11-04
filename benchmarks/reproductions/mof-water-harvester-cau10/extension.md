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
| Adsorption: bed and inlet air | 313.15 K, equilibrium with the inlet air | assumed (equal to the isotherm temperature, 313.0 K) |
| End-of-adsorption loading | adsorption branch at the inlet RH | measured |
| Regeneration state | p/p0 0.05 at the bed, desorption branch: 0.0156 g/g | measured loading, assumed state |
| Condenser | 30 °C (4.25 kPa) | assumed |
| Regeneration temperature | 85.1 °C, from p/p0 0.05 and the condenser pressure | reconstructed, **extrapolated** (characteristic curve outside 288 K to 313 K) |
| Adsorption enthalpy | 2641 kJ/kg (47.6 kJ/mol) = h_fg 2406 kJ/kg + R T ln(1/α) | reconstructed (Dubinin relation; not measured) |
| Adsorbent heat capacity | 0.90 kJ/(kg K) | assumed |
| Packed bed density | 600 kg/m3 | assumed |
| Cycle | 1 per day, 6 h desorption | assumed; affects only daily yield and mean heat duty |

Sizing: working capacity Δq = q_ads(RH) − q_des(0.05); adsorbent mass m = yield / (recovery × Δq);
packed volume V = m / ρ_bed. Mass is per kilogram of pellets as measured (binder included).

## Result: required adsorbent against inlet humidity

Figure: `results/harvester_mass_vs_rh.svg` (run.py; not committed, see README.md).

| Inlet RH at 313 K | Vapour in air | Working capacity | Adsorbent | Packed volume | Flag |
| --- | --- | --- | --- | --- | --- |
| 0.15 | 7.7 g/m3 | 0.0024 g/g | 519 kg | 865 L | infeasible |
| 0.18 | 9.2 g/m3 | 0.0070 g/g | 179 kg | 298 L | infeasible |
| 0.19 | 9.7 g/m3 | 0.015 g/g | 83 kg | 139 L | infeasible, on the step |
| 0.195 | 10.0 g/m3 | 0.066 g/g | 19 kg | 32 L | on the step |
| 0.20 | 10.2 g/m3 | 0.183 g/g | 6.8 kg | 11.4 L | on the step |
| 0.22 | 11.2 g/m3 | 0.253 g/g | 4.9 kg | 8.2 L | |
| 0.30 | 15.3 g/m3 | 0.269 g/g | 4.65 kg | 7.7 L | base case |
| 0.42 | 21.5 g/m3 | 0.281 g/g | 4.44 kg | 7.4 L | highest supported RH |

Below an inlet RH of 0.195 the working capacity is less than 10 % of the plateau value
(0.028 g/g, threshold in `inputs.yaml`), and below about RH 0.125 the bed takes up no water
beyond its regeneration loading. Between 0.189 and 0.219 the inlet sits on the step: a change of 0.01 in RH
changes the mass by up to a factor of ten, so a design point there is not robust. Above the step
the mass is almost flat: from RH 0.22 to 0.42 it falls by only 10 %.

## Changed-input example: inlet RH 0.30 → 0.18

| | Base, RH 0.30 | Changed, RH 0.18 | Change |
| --- | --- | --- | --- |
| Working capacity | 0.269 g/g | 0.0070 g/g | ÷ 38.5 |
| Adsorbent for 1 kg per cycle | 4.65 kg | 179 kg | × 38.5 |
| Packed volume | 7.7 L | 298 L | × 38.5 |
| Regeneration heat per kg water collected | 3.74 MJ (1.04 kWh) | 11.3 MJ (3.15 kWh) | × 3.0 |
| of which desorption enthalpy | 3.30 MJ | 3.30 MJ | same |
| of which heating the bed | 0.44 MJ | 8.04 MJ | × 18 |
| Mean heat duty over 6 h | 173 W | 525 W | × 3.0 |

**Physical interpretation.** The inlet air carries 40 % less water (15.3 to 9.2 g/m3), but the
adsorbent needed rises 38-fold. At RH 0.30 the hydrophobic pores of CAU-10-H are filled with
the water cluster that forms at the step; at RH 0.18 the step has not been reached, and only a
small amount of water is held at low pressure, little more than the bed still holds after
regeneration. The harvester then cycles almost dry pellets: most of the regeneration heat goes
into warming the bed rather than desorbing water. For this adsorbent the feasible design
condition is a threshold, the step position, not a gradual trade-off with humidity.

## Sensitivity of the base case (one at a time)

| Change | Result |
| --- | --- |
| Regeneration p/p0 0.0317 or 0.0705 (ends of the measured desorption branch) | 4.62 or 4.68 kg |
| Recovery 0.6 or 0.9 | 6.20 or 4.13 kg |
| Packed density 400 or 800 kg/m3 | 11.6 or 5.8 L |

The regeneration state hardly matters on the plateau, because the regeneration loading
(0.014 to 0.018 g/g) is small against 0.28 g/g. Mass scales with 1/recovery and volume with
1/density, both assumed.

## Out-of-range and extrapolation flags

- **Inlet RH above 0.4246** is outside the measured series; the sweep stops at 0.42.
- **Temperature.** All loadings are read at 313 K. Colder night air at 25 °C, with the bed at
  25 °C, would by the characteristic curve step at RH 0.182 (4.2 g/m3) instead of 0.197
  (10.0 g/m3 at 40 °C). That would widen the feasible region in absolute humidity by more than
  a factor of two, but it is an extrapolation and is not used in the sweep. Bed temperature is
  therefore as important a design variable as humidity.
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
  regeneration loading from the desorption branch.
