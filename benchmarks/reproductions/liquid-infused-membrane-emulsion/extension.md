# Operating window, area estimate and design extension (#340)

Three results build on the reproduction (`comparison.md`). They differ in standing:

| Part | Standing |
| --- | --- |
| 1. Operating window against TMP | model result from the reproduced inputs. Checked only against the source's own Table 3 (5 of 8); not independently validated |
| 2. Membrane area | measured flux of one case with an assumed feed basis. A batch-cell figure only |
| 3. Pore radius halved | **HYPOTHETICAL design extension (not validated)** |

Numbers come from `results/comparison.json`. Figures are `results/operating_window.svg` and
`results/extension_pore_radius.svg`.

## 1. At what pressures does oil permeate selectively?

Threshold model: oil enters when TMP >= 2 gamma23 / r. Water enters when TMP >= 2 gamma_w / r,
where gamma_w is the interface the aqueous phase must cross (`inputs.yaml`
configuration_rules). Swept from 0 to 0.7 bar in 1 mbar steps (`results/sweep.csv`).

| Emulsion | Membrane | Oil entry [bar] | Water entry [bar] | Selective window [bar] | Window narrowed by fit CIs [bar] |
| --- | --- | --- | --- | --- | --- |
| SDS 10 | dry (hexadecane-filled) | 0 | 0.287 | 0-0.287 | 0-0.224 |
| SDS 50 | dry | 0 | 0.154 | 0-0.154 | 0-0.031 |
| CTAB 10 | dry | 0 | 0.147 | 0-0.147 | 0-0.086 |
| CTAB 50 | dry | 0 | 0.046 | 0-0.046 | none |
| SDS 10 | K101-infused | 0.096 | 0.392 | 0.096-0.392 | 0.098-0.323 |
| SDS 50 | K101-infused | 0.096 | 0.259 | 0.096-0.259 | 0.098-0.130 |
| CTAB 10 | K101-infused | 0.096 | 0.254 | 0.096-0.254 | 0.097-0.189 |
| CTAB 50 | K101-infused | 0.096 | 0.153 | 0.096-0.153 | 0.097-0.102 (5 mbar, under one controller accuracy) |

In physical terms:

- The window is set by interfacial tensions, not by the membrane. Surfactant lowers the
  water/oil tension and closes the window from above. At 50 % cmc CTAB, the dry membrane is
  selective only below 0.046 bar, which is 8 steps of the 5.5 mbar controller.
- The K101 infusion raises the water bound by adding gamma23 = 8.7 mN/m. It also creates an
  oil bound of about 0.08 to 0.10 bar. Oil needs that pressure to displace K101, whereas it
  wicks into the dry membrane spontaneously.
- The runs at up to 0.1 bar sat just above the K101 oil bound. They were inside the model
  window for every K101 case, yet water leaked at 50 % cmc (`comparison.md`). **The model
  window is therefore an upper estimate of where operation is selective.** For 50 % cmc it is
  not supported by the observations.
- The selective window supported by both the model and Table 3 is SDS 10 and CTAB 10 (both
  membranes) at TMP up to 0.1 bar (for CTAB 10 on the dry membrane only at the nominal fit:
  0.1 bar lies inside the band of the water entry pressure, whose low edge is 0.086 bar), with oil entry 0.08 bar measured on the K101-infused
  membrane.

## 2. Membrane area, only where flux data support it

One flux record exists: K101-infused membrane, SDS 10 emulsion, 0.1 bar, dead-end, with the
feed chamber refreshed repeatedly. Average oil flux 4.0e-6 m3 m-2 s-1 (14.4 L m-2 h-1).

| Quantity | Value |
| --- | --- |
| Oil volume fraction of the feed (5 wt% hexadecane, water density) | 0.0673 |
| Test cell area (25 mm diameter) | 4.91e-4 m2, about 7.1 mL/h of oil |
| Area to pass all the oil of 1 m3/h of this feed, at the measured flux (assumed basis) | **4.7 m2 per m3/h of feed** |
| Darcy capacity of the open pores at 0.1 bar (LLD cycle 1 permeability) | 2.05e-4 m3 m-2 s-1, 51 times the measured flux (164 times if Table S3 used 1 mPa s, see below) |
| Creaming supply from the largest droplets (phi x 19.85 um/s) | 1.3e-6 m3 m-2 s-1 |

The flux is limited by how fast oil reaches the membrane, not by permeation. The open pores
could pass 51 times more oil at the same TMP. This uses the SI Table S3 permeability with the
hexadecane viscosity, 3.2 mPa s. SI p. S7 states that 1 mPa s was used for Table S3; if so, the
permeability on a hexadecane basis is 3.2 times higher, the capacity about 160 times the
measured flux, and the implied dry porosity 0.68 instead of 0.21. Either way the flux is
supply-limited. The source states that the flux falls as the
droplet concentration falls and depends on how often the feed is refreshed. The measured
average is also three times the steady creaming supply from the largest droplets, so it
includes oil that accumulated between refreshes. The 4.7 m2 figure is therefore a batch,
gravity-fed figure for this one emulsion. It does not scale with TMP and does not carry over to
a continuous module. No area is given for the other seven cases: there are no flux data for
them, and the two 50 % cmc cases were not selective.

## 3. HYPOTHETICAL design extension (not validated): halve the pore radius

**Changed input:** every curvature radius multiplied by 0.5 (mean pore radius 1.78 to
0.89 um), with the same PVDF/K101 chemistry. **Design case:** SDS 10 emulsion on the
K101-infused membrane, the only case that is selective in both model and observation and has
flux data. The usable TMP range is the window narrowed by the fit CIs and by a margin of
2 x 5.5 mbar (controller accuracy) on each side.

| Quantity | Base, r = 1.78 um | Changed, r = 0.89 um | Ratio |
| --- | --- | --- | --- |
| Oil entry [bar] | 0.096 | 0.191 | 2 |
| Water entry [bar] | 0.392 | 0.783 | 2 |
| Water/oil entry ratio | 4.09 | 4.09 | 1 |
| Usable TMP range [bar] | 0.109-0.312 | 0.207-0.636 | - |
| Tolerable TMP variation [bar] | 0.204 | 0.429 | 2.11 |
| Controller steps (5.5 mbar) in usable range | 37 | 78 | - |
| Darcy capacity at top of usable range [m3 m-2 s-1] | 6.4e-4 | 3.3e-4 | 0.51 |

Engineering consequence:

- **Halving the pores doubles every threshold and the window width.** A module could then
  tolerate 0.43 bar of TMP variation instead of 0.20 bar: axial pressure drop along the
  channel plus pressure ripple plus set-point error. That is the property a crossflow module
  needs most. (The usable variation more than doubles because the fixed control margin takes a
  smaller share.)
- **Within the threshold model, pore size does not change the water/oil entry-pressure
  ratio** (4.09 for any r, because both bounds scale with 1/r). In the model, surfactant level,
  oil and infusion liquid set selectivity. Whether real leakage, which the model does not
  capture at 50 % cmc (largest pores, K101 loss), depends on pore size is not known.
- **Smaller pores halve the permeation capacity at the top of the window.** Capacity goes as
  r^2 x (1/r) = r. While the flux is supply-limited (part 2), this costs nothing. It would
  start to matter only if oil delivery became faster than about 3e-4 m3 m-2 s-1.

Extrapolation and validity flags:

- **Operating pressure outside the observed range.** The changed case's usable TMP range,
  0.207 to 0.636 bar, lies entirely above the highest TMP at which the source ran emulsions
  (0.1 bar). So does the base range (0.109 to 0.312 bar): its lower bound has the control margin
  added to the 0.098 bar oil bound. No measurement backs the selective behaviour, the leakage at
  50 % cmc or the supply-limited flux at these pressures. In `results/extension_pore_radius.svg`
  the region above 0.1 bar is shaded grey; the whole usable range lies above it for pore
  radius scales 0.25 to 1.09 (`comparison.json` design_extension).

- The radius scaling assumes the liquid lining scales with the pore. Not measured.
- kappa = phi r^2 / 24 at unchanged porosity and active-pore fraction is the source's simple
  model, applied outside the one membrane it was fitted to.
- Surfactant depletion by adsorption in the pore grows as r falls (SI eq S8). The authors found
  bulk concentration matched the LEPs at r of about 1.7 um. At 0.89 um this is not known.
  Stronger depletion would raise the water bound, so the window would err on the safe side.
- The design case is at 10 % cmc, inside the fitted IFT range (up to 50 % cmc).
- The model window was not borne out at 50 % cmc (`comparison.md`). The extension is offered
  only for the 10 % cmc case, where it was.

## What a continuous (crossflow) module would need

The data support only a dead-end, gravity-fed batch cell. Sizing a crossflow module needs:

1. **Steady oil flux against TMP and crossflow velocity**, so that oil delivery to the wall
   is measured rather than gravity creaming into a quiescent cell. Without it, no area can be
   given: the present flux is supply-limited and set by the refresh schedule.
2. **Droplet transport and coalescence at the wall under shear.** This means the deposition
   rate as a function of droplet size distribution, wall shear stress and oil fraction, and
   whether a continuous oil film forms on the membrane, which the gating mechanism relies on.
3. **Water breakthrough as a function of TMP, not a single 0.1 bar point.** This means water
   fraction or flux against pressure for each surfactant level, to place the real upper bound.
   At 50 % cmc it lies below the model bound.
4. **Pore size distribution in the liquid-lined state** (or the LEP of the largest lined
   pores), because breakthrough starts in the largest pores. The fitted curvature radius is a
   single value.
5. **Long-term retention of the infusion liquid under emulsion flow.** Only an LLD estimate
   exists (about 45 % retained, i.e. about 55 % displaced, after pure oil flow). A K101 loss
   rate under emulsion flow sets the module life and whether re-infusion is needed.
6. **Axial pressure drop of the chosen channel geometry**, to check it against the tolerable
   TMP variation (0.20 bar for the base membrane). This also needs the permeate-side pressure.
7. **Fouling and surfactant adsorption over time**, and the effect of real oils (crude or
   edible oils, whose IFTs differ from hexadecane's).
8. **Temperature dependence of the IFTs and viscosities.** All data are at 20 to 24 C.

Review status: specialist review not yet done; optional follow-up with a specialist in
membrane separation and interfacial transport.
