# Electrified distillation with flash vapour circulation: does composition feedback recover purity?

Case study for issue #335 (scope tracker #333). It follows ADR 0030 (reference reproductions,
tolerances frozen first) and the layout of ADR 0031 (a reproduction plus a labelled design
extension; status Proposed, merged in #344).

**Engineering question.** In a fully electrified methanol/water column, a three-stage heat pump
compresses the overhead vapour to boil the bottoms. Part of the throttled condensate flashes and
returns to the compressor suction: the flash vapour circulation (FVC). Does adding composition
feedback to temperature control recover product purity after a ±20 % change in feed composition,
and how does compressor power respond?

**Source.** Cui, Zhang, Qi and Kiss, *Control of fully electrified heat pump assisted distillation
process by flash vapor circulation*, Chem. Eng. Res. Des. 220 (2025) 450-460,
doi 10.1016/j.cherd.2025.07.023, CC BY 4.0. The supporting-information workbook holds the Aspen
Plus stream and stage tables and the Aspen Dynamics responses of both control structures. The
model files are not public.

**Answer (ours, against the source).** Yes, in both the source's Aspen model and ours (simulation
only; no plant data exist for this column). CS1 (stage-35 temperature control, fixed reflux ratio)
leaves the distillate off specification: 0.9988 / 0.9731 after +20 / -20 % feed methanol (source
0.9980 / 0.9784). CS2 (plus a distillate composition loop on the reflux ratio) returns it to 0.99,
with reflux ratios 0.284 / 0.762 (source 0.303 / 0.721).

At +20 % methanol, CS1's fixed reflux drives the heat pump above its design load. Compressor power
rises from 307 to 418 kW (source 303 to 441 kW), the FVC flow rises from 8 to 34 kmol/h (source
7.3 to 41.4) and the COP falls to 4.0 (source 3.7). CS2 lowers the power to 284 kW (source
283 kW) at COP 4.7. At -20 % methanol, CS2 needs about 4 % more power than CS1 to hold the
specification.

The conclusion (CS2 recovers purity and needs less power at +20 % methanol) holds in all 23
sensitivity variants and the base case (holdups, hydraulics, tuning, analyser lag, exchanger
capacity, NRTL alpha); comparison.json records both direction flags for every row. The transient
shape does not reproduce: our CS2 is faster than the source's.

## Status

| Item | Status |
| --- | --- |
| Reproduction | **partial** under the frozen rule (`tolerances.yaml`): 18 of 19 primary checks pass, both direction checks pass. The CS1 purity at -20 % methanol misses: 0.9731 against 0.9784, tolerance ±0.003. Read the count with care: 2 of the 17 numeric checks (CS2 x_D at ±20 % methanol) are the controller set point, held by integral action, so 14 of the other 15 pass; and the 7 nominal checks are consistency checks of the reconstruction, because NRTL and the enthalpies are fitted to the same SI stage data. The step responses at ±20 % methanol are the independent tests. Secondary (transient) checks: 14 of 21. See `comparison.md`. |
| Independent validation | none: the reference is itself a simulation, and no plant or experimental data were used |
| Design extension | hypothetical: CS2 distillate set point 0.99 to 0.995 (`extension.md`) |
| Specialist review | not yet (optional follow-up: a specialist in distillation dynamics and process control) |

## Rerun

From the repository root (needs `uv`; downloads the 0.5 MB SI workbook once into
`~/.cache/cheme-reproductions/electrified-distillation-control/` and checks its sha256):

```sh
uv run benchmarks/reproductions/electrified-distillation-control/run.py
```

About 1.5 minutes on a laptop. It writes `results/` and prints the verdict. Exit status 0 means the script ran,
not that the checks passed. The P&ID is rebuilt with cheme-as-code (1.2.1 used) from `case/`:

```sh
cd benchmarks/reproductions/electrified-distillation-control/case
cheme sheet new P-01 --force && cheme run scripts/draft_P-01.py pid/P-01.xml && cheme render pid/P-01.xml -o P-01.svg
```

## Files

| File | What |
| --- | --- |
| `source.yaml` | pinned article and SI (DOI, version, sha256, licence, access date), case specification, reported results restated as facts with locators |
| `inputs.yaml` | every model input with value, unit, label (measured, reconstructed, assumed, as in ADR 0031; `origin: literature` marks values from other publications) and source or rationale; the gaps |
| `tolerances.yaml` | frozen acceptance tolerances and the pass rule (commit 9aeb7614, before any comparison run) |
| `run.py` | the model, tuning, scenarios, checks (tolerances read from `tolerances.yaml`, its sha256 recorded), sensitivity study, extension and figures; single entry point |
| `results/comparison.json` | every compared quantity, fitted parameters, tuning, end values, series every 0.1 h, sensitivity, extension |
| `results/fig_composition_steps.svg` | purity, reflux ratio and compressor power against time, CS1 and CS2, ±20 % methanol, ours and the source's |
| `results/fig_nominal_profiles.svg` | nominal temperature and composition profiles, ours against the SI |
| `results/fig_throughput_steps.svg` | ±20 % throughput steps (context; CS1 +20 % is the calibration case) |
| `results/fig_sensitivity.svg` | end values and IAE across the base case and the 23 sensitivity variants |
| `results/fig_extension_operating_map.svg` | steady power, reflux ratio and purity against feed methanol; 0.99 and 0.995 set points |
| `case/` | minimal cheme case: `plant.yaml`, `scripts/draft_P-01.py` (our drawing script), `pid/P-01.xml` (DEXPI 2.0.1), `P-01.svg` (render) |
| `comparison.md` | run details, reference against ours, verdict, deviations and their explanations |
| `extension.md` | the hypothetical design extension and its flags |
| `NOTICE.md` | attribution of the source's data (CC BY 4.0) used in the comparison and the figures |

## Control loops and the P&ID

`case/P-01.svg` is our control-loop P&ID, drawn by cheme from `case/scripts/draft_P-01.py`. It is
not traced from the paper's figures. Its ISA tags map to the source's loops (section 3.2). The
vessels of LC1-LC3 are our reading of the article's wording ("reflux drum", "column sump", "base
level of distillation column") on the FVC-2 flowsheet, labelled reconstructed in `source.yaml`:

| Loop (source) | Tag on P-01 | Measured | Manipulated |
| --- | --- | --- | --- |
| FC1 | FIC-101 | feed flow | FV-101 (V1) |
| PC1 | PIC-102 | column top pressure | PV-102, cooling water of E-104 (COND) |
| PC2 | PIC-103 | compressor discharge pressure | PV-103 (V2) |
| TC | TIC-104 -> JIC-105 | stage 35 temperature | total compressor power; K-102, K-103 in fixed ratio to K-101 |
| LC1 | LIC-106 | V-101 (FLASH-D) level | LV-106, distillate (V4) |
| RR | FFIC-107 | reflux / distillate | FV-107, reflux (V3) |
| CC (CS2 only) | AIC-108 -> FFIC-107 | distillate methanol (3 min analyser lag) | reflux ratio set point |
| LC2 | LIC-109 | column sump level | LV-109, withdrawal (V6) |
| LC3 | LIC-110 | V-102 (FLASH-R) level | LV-110, bottoms (V8) |

In run.py, FC1, PC1 and PC2 are taken as ideal: fixed feed and fixed pressures, with the FVC flow
closing the suction balance. The other loops are simulated with the source's level gains and
deadtimes and our Tyreus-Luyben tuning. `cheme validate` in `case/` reports 0 errors and 11
drawing warnings, all line crossings (7 signal lines over pipes, 4 pipe crossings); the layout
keeps them few rather than none.

## Evidence gaps

- **No model files.** Tray hydraulics, exchanger areas and UA, pressure-drop coefficients,
  compressor maps and controller ranges are not published. We reconstruct them (`inputs.yaml`) and
  vary them. They change the transient (IAE, settling) but not the end values.
- **Heat-pump capacity above the design load** is one reconstructed parameter (kappa = 0.19),
  calibrated on the CS1 +20 % throughput case. The CS1 power at +20 % methanol depends on it
  (356-495 kW across the variants; source 441 kW). The CS2 result does not.
- **Tuning results** (Ku, Pu, Kc, tau_I) of the source are not reported; ours come from our own
  linearised model by the same Tyreus-Luyben method.
- **Property method** not stated; NRTL fitted to the SI equilibrium points instead (no databank
  values used).
- **Table 1** settling-time definition not stated; compared like-for-like with our own rule.
- **CS1 purity at -20 % methanol** misses the tolerance for a steady-state reason we cannot locate
  without the Aspen file (`comparison.md`, deviation 1).
- **Core capability gap.** cheme 1.2.1 has no dynamic column model and no control-loop simulation:
  the dynamics live in this case's run.py. cheme's P&ID authoring covered the loop drawing. The gap
  is reusable (any column control study needs a tray-by-tray dynamic model with PI loops). Opened as
  core#143 and linked from #333.

## Credits

Source data: Chengtian Cui, Xiaodong Zhang, Meng Qi and Anton A. Kiss, *Control of fully
electrified heat pump assisted distillation process by flash vapor circulation*, Chem. Eng. Res.
Des. 220 (2025) 450-460, doi 10.1016/j.cherd.2025.07.023, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Our figures replot values from its
supporting information beside our results; the values are replotted, not modified, and each figure
carries the citation. The workbook's own licence is not stated separately, so we use it as a source
of facts and do not redistribute it. Details in `NOTICE.md`.
