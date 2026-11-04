# Comparison: MD12 droplet drying and surface glass transition, model vs references

- **References:** `source.yaml`. A is the measured sessile-droplet trajectory of Sewalt et al.
  (2022, CC BY 4.0). B is the modelled t_glass of the thesis model (Sewalt 2024, Table 5.1, DE 12,
  particle ejector). C (informational) is the measured locking times (thesis Table 4.1).
- **Tolerances:** `tolerances.yaml`, frozen in commit 0f6f7b49 before any run. That commit was
  amended once before the first run: the first version (923867f2, never pushed) had two
  `computed_as:` strings starting with `|`, which YAML could not parse. Only the quoting changed.
  `git diff 0f6f7b49 HEAD -- tolerances.yaml` is empty.
- **Run:** `uv run benchmarks/reproductions/spray-drying-stickiness/run.py` from the repository
  root, 2026-11-04. uv chose Python 3.13.16 with numpy 2.3.4, scipy 1.16.3, matplotlib 3.10.7 and
  pyyaml 6.0.3. The model uses 150 radial cells, BDF with rtol 1e-6. Wall time is about 15 s.
  Two runs give byte-identical `results/`.
- **Order:**
  1. Commit 0f6f7b49 freezes the sources, inputs and tolerances.
  2. Commit aff3efd3 holds the first comparison run, with its script and results.
  3. The current commit holds the second run.
  The script changed between the two runs in three ways, none of which touches an input or a
  tolerance:
  - The cell state became solute content per cell instead of volume fraction (see I1 below).
  - Post-hoc diagnostics were added (not scored).
  - Figure labels were fixed.
  Every scored physical value is unchanged to four significant digits between the runs.

## Result: FAIL under the frozen rule

8 of 12 scored checks pass. The verdict is FAIL because each reference group has a failure: A3 in
group A, and B1-B4 in group B. The first run was also FAIL; in that run I1 failed as well
(7.7e-6 against 1e-6).

| Check | Reference | This model | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| A1 initial d² rate, sessile droplet | 880 µm²/s | 801 µm²/s | -9.0 % | rel 30 % | pass |
| A2 locking time vs model t_glass | about 160 s | 178.4 s | +11.5 % | rel 25 % | pass |
| A3 locked radius vs model radius at t_glass | 141 µm | 113.5 µm | -19.5 % | rel 10 % | **fail** |
| B1 t_glass, 10 wt%, 25 °C | 53.9 s | 34.3 s | -36.3 % | rel 25 % | **fail** |
| B2 t_glass, 20 wt%, 25 °C | 27.5 s | 18.0 s | -34.7 % | rel 25 % | **fail** |
| B3 t_glass, 30 wt%, 25 °C | 11.9 s | 8.14 s | -31.6 % | rel 25 % | **fail** |
| B4 t_glass, 20 wt%, 45 °C | 15.5 s | 11.3 s | -27.3 % | rel 25 % | **fail** |
| B5 t_glass, 20 wt%, 65 °C | 10.3 s | 7.98 s | -22.5 % | rel 25 % | pass |
| B6 t_glass(30 wt%) / t_glass(10 wt%), 25 °C | 0.221 | 0.237 | +0.016 | abs 0.05 | pass |
| I1 solute mass conservation, all runs | - | 8.3e-15 | - | rel 1e-6 | pass |
| I2 grid convergence, 150 vs 300 cells | - | 0.27 % (B), 0.01 % (A) | - | rel 2 % | pass |
| I3 t_full closure of the gas-velocity reconstruction | - | 2.6e-14 | - | rel 1e-3 | pass |

The reconstructed gas velocities for case B are 2.05, 1.67 and 1.40 m/s at 25, 45 and 65 °C.
They reproduce the thesis t_full of 57.96, 36.90 and 26.41 s for R0 = 240 µm.

## Informational comparisons (declared before the run, not scored)

| Quantity | Reference | This model |
| --- | --- | --- |
| A: centre mass fraction at 60 s | 15 ± 2 wt% (OCT bulk) | 13.5 wt% |
| A: outer 10 µm mean mass fraction at 60 s | 23 ± 3 wt% (OCT near interface) | 16.0 wt% |
| A: end of constant-rate drying (model: d² rate 10 % below initial) | about 60 s | 175 s |
| A1 bracket: no substrate heat | 880 µm²/s | 582 µm²/s (t_glass 274 s) |
| A1 bracket: isothermal droplet at 20 °C | 880 µm²/s | 1503 µm²/s (t_glass 89 s) |
| Viscosity at 10 wt%, 20 °C | 1.1 mPa s | 1.48 mPa s |
| Viscosity at 46 wt%, 20 °C | about 0.1 Pa s | 0.16 Pa s |
| Water self-diffusion at 25 °C (D0 reading check) | 2.30e-9 m²/s (Mills 1973) | 2.26e-9 m²/s |
| Popov f(90°) (sessile factor check) | 2 (exact) | 2.000 |

**C: measured locking time vs modelled surface glass, DE 12, particle ejector.** All values are
t / t_full.

| Condition | Measured locking (thesis Table 4.1) | Thesis model t_glass (Table 5.1) | This model t_glass |
| --- | --- | --- | --- |
| 10 wt%, 25 °C | 1.04 ± 0.02 | 0.93 | 0.59 |
| 20 wt%, 25 °C | 0.86 ± 0.04 | 0.48 | 0.31 |
| 30 wt%, 25 °C | 0.52 ± 0.11 | 0.21 | 0.14 |
| 20 wt%, 45 °C | 0.90 ± 0.12 | 0.42 | 0.31 |
| 20 wt%, 65 °C | 0.79 ± 0.06 | 0.39 | 0.30 |

In the nitrogen jet, both models put the surface glass transition well before the measured
locking point: by 11 to 60 % in the thesis model and by 43 to 73 % in ours. The thesis reaches
the same conclusion: locking is not the surface glass transition.

## Deviations and explanations

1. **A3, locked radius (fail).** The model droplet keeps shrinking until its surface is glassy at
   178 s, which leaves a radius of 113.5 µm. The measured droplet stopped shrinking at 141 µm.
   - A post-hoc diagnostic shows the model droplet passing 141 µm at 141 s. At that moment its
     surface is 37 wt% and its centre 28 wt%. The surface is still 119 K above its Tg, so it is a
     liquid.
   - The OCT paper reports a similar state near locking: a surface plateau of 40-46 wt% and a bulk
     above 30 wt%. It also finds the skin "not fully dry": 40 µm thick against 20 µm if fully dry.
   - So the sessile droplet locks into a viscous, non-glassy skin about 20-40 s before any
     surface-glass criterion is met.
   - A2 passes because, for this droplet, the modelled glass time happens to fall within 12 % of
     the measured locking time. A3 shows that the droplet state at that time differs: smaller and
     denser in the model. A1 and A2 together do not show that the surface glass marks locking,
     and A3 shows it does not.
2. **A1 brackets.** The isothermal and the no-substrate-heat bounds give 1503 and 582 µm²/s. The
   measured 880 µm²/s lies between them, nearer the evaporatively cooled bound.
   - The scored central case, with substrate conduction at k_s = 0.15 W/m/K, is 9 % low.
   - The sessile shape factor (0.68 of an isolated sphere at 154°) and evaporative cooling account
     for most of the rate.
3. **A, concentrations and the falling-rate onset.** The model has no internal flow. The OCT
   droplet recirculates at about 20 µm/s, a Péclet number of about 10 against solute diffusion.
   This flow changes where the solute accumulates.
   - The paper also measures accumulation near the substrate, which a spherical 1D model cannot
     show.
   - The model's surface enrichment at 60 s (16 against 13.5 wt%) is weaker than the measured
     23 against 15 wt%. The OCT concentration is uncertain: it reads 14 wt% initially for a
     10 wt% solution.
   - The model has no distinct falling-rate period. Its rate falls only when the surface water
     activity drops below 1, which by GAB happens above 61 wt% solids, at about 175 s. The
     measured transition at about 60 s is not reproduced. The cap of the GAB form at a_w = 1
     below 61 wt% is a likely cause.
4. **B1-B5, thesis t_glass (four fail).** Our model reaches a glassy surface 22-36 % earlier than
   the thesis model. The bias is uniform in sign and shrinks as the gas temperature rises.
   - The solids effect is reproduced: B6, the ratio of the 30 and 10 wt% times, is 0.237 against
     0.221. So the shape of the model is right and its time scale is short.
   - The post-hoc diagnostics (`comparison.json`, `post_hoc_diagnostics`) test each reconstructed
     or uncertain reading on its own. None closes the gap uniformly:
     - Nusselt coefficient 0.6 instead of the printed 0.4: -34 to -24 %.
     - Initial droplet temperature at the wet-bulb temperature: -35 to -27 %.
     - Flory-Huggins χ = 0: -30 % at 10 wt%, -5 % at 30 wt%.
     - The literal D0 = 1.48e-5 m²/s: -10 % at 10 wt%, +153 % at 30 wt%.
   - Things we cannot check: the reference model's grid, time step and surface-cell treatment are
     not stated, and the MSc thesis it draws on (Presili 2020) was not available. The
     reproduction of the thesis time scale stays open, and the cause is not identified.
   - Our model's surface reaches the glass transition at 82-85 wt% solids. The thesis example
     quotes about 80 wt%, so the surface criterion itself agrees.
5. **I1 in the first run (fail at 7.7e-6, fixed).** The first script stored the volume fraction
   of each cell. Total solute is then a nonlinear function of the states (the sum of φᵢVᵢ(R)),
   and an implicit integrator conserves it only to about its tolerance. The second script stores
   the solute content of each cell, a linear invariant, and conserves it to 8e-15. The scored
   values changed by at most 1.8e-6 relative, the extension values by at most 9e-6. The tolerance's reason, "conserves
   solute by construction", described the intended scheme. The first implementation did not meet
   it.

## Gaps found (reported, not fixed here)

- The measured d(t) curve is only in a figure (OCT Fig. 2b). We compared three stated features
  (initial rate, locking time, locked radius), not the curve. Digitising the figure would add an
  uncertainty of about ±2 % of full scale and was not needed for the scored checks.
- The time origin of the OCT data is ambiguous by about 9 s (imaging started about 9 s after
  dispensing).
- Thesis Table 5.1 rows for the falling droplet column cannot be reproduced: the initial diameter
  used for each condition is not stated.
- Four model parameters are read from garbled print (`inputs.yaml`, label reconstructed). The
  thesis gives no licence, so its model cannot be redistributed beyond the facts restated here.
- No measured (T - Tg)c exists for MD12. The extension uses an assumed band.
