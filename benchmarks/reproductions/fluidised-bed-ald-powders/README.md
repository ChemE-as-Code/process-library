# Fluidised-bed ALD on powders: reproduction and scale-up

Case study for issue #336 (scope tracker #333). Protocol: ADR 0030 (reproductions,
tolerances frozen first) and ADR 0031 (case studies: a reproduction plus a labelled design
extension).

**Engineering question.** How do batch size and reactor height affect surface coverage and
precursor utilisation in fluidised-bed atomic layer deposition (ALD) on powders?

**System.** Trimethylaluminium (TMA) half-reaction on Degussa P-25 TiO2 nanoparticle
agglomerates in a bubbling fluidised bed at 500 K, as modelled by Grillo, Kreutzer and van
Ommen, Chem. Eng. J. 268 (2015) 384-398 (doi:10.1016/j.cej.2015.01.067). The article is
closed access. We used its open version, chapter 7 of F. Grillo's TU Delft thesis (2018,
doi:10.4233/uuid:97fabd08-203c-4471-9596-7ad91f7eb2c0). The ALD-on-particles literature index
(Zenodo 10.5281/zenodo.14832687, CC BY-NC-ND) was used for discovery only.

We re-implemented the model from the published equations in `run.py`: two-phase bubbling bed
(Table 7.1), agglomerate diffusion (Table 7.2), time scales, and the quasi-steady utilisation
and required bed height (Eqs. 7.24, 7.51, 7.52). The source's surface chemistry (Travis et al.)
is not given in the chapter. Our dynamic model therefore uses lumped first-order site
kinetics, fitted only to the reported reaction time scale.

## Status

| | Status |
| --- | --- |
| Reproduction | **partial** under the frozen rule: 29 of 38 comparisons pass, all of G1 (saturation time) and G3 (stated bed heights). Time scales: 11/11 within 1.6 % (tau_int 7 %). Required bed height H* from Fig. 7.4: 13/20, with up to -35 % at 1 cm bubbles. Dynamic bubble profile (Fig. 7.3): 1/3. The full dynamic model's saturation time and CH4 yield cannot be evaluated (inputs not stated). See `comparison.md` |
| Independent validation | none: no experimental outlet-precursor or coverage data used. The index lists four alumina-on-titania fluidised-bed papers, not examined as validation data |
| Design extension | hypothetical: 22 g to 1 kg at fixed 99 % mean coverage, two scale-up strategies, dimensioned section view (`extension.md`) |
| Specialist review | not yet (optional follow-up: ALD and fluidisation specialist) |

**Headline.** At 1.013 bar, more than 99.9 % of the TMA is taken up in both 1 kg designs. The
pulse length is set by the settled bed height: 46 s at H0 = 60 mm (bed 404 mm wide) and 163 s
at H0/d_t = 1 (214 mm x 364 mm expanded bed, vessel 1.11 m). Bubble size is the main risk to
utilisation: 4.5 cm bubbles in the 1 kg geometric scale-up would let 1.7 % of the TMA escape.

## Rerun

From the repository root (needs `uv`; no data download):

```sh
uv run benchmarks/reproductions/fluidised-bed-ald-powders/run.py
```

This writes `results/` deterministically in about 10 s. It exits non-zero only if the script
fails; the verdict is in `results/comparison.json`. To re-derive the digitised reference values
(downloads the 60 MB thesis to `~/.cache/cheme-reproductions/fluidised-bed-ald-powders/`,
checks its sha256):

```sh
uv run benchmarks/reproductions/fluidised-bed-ald-powders/digitise.py
```

## Files

| File | What |
| --- | --- |
| `source.yaml` | pinned sources (DOIs, file sha256, licences, access), reported results restated with locators, digitised values with method and uncertainty |
| `inputs.yaml` | every model input with value, unit, label (measured, reported, reconstructed, assumed) and source or rationale |
| `tolerances.yaml` | acceptance tolerances and pass rule, frozen in commit 38aa2e3f before the first comparison run; header discloses pre-freeze hand estimates |
| `digitise.py` | how the Fig. 7.3 and 7.4 values were read from the PDF's vector paths |
| `run.py` | single entry point: reproduction, dynamic model, extension, figures |
| `results/comparison.json` | every compared quantity, verdict, supplementary values, extension results |
| `results/fig1-required-bed-height.svg` | H* against bubble size, ours vs digitised source (Fig. 7.4) |
| `results/fig2-bubble-profile.svg` | dynamic bubble-phase TMA profile vs digitised source (Fig. 7.3) |
| `results/fig3-pulse-breakthrough-coverage.svg` | outlet TMA and coverage against time, lab and 1 kg (pulse timing) |
| `results/fig4-batch-sweep.svg` | pulse time and precursor slip, 22 g to 10 kg |
| `results/fig5-section-view-1kg.svg` | dimensioned section views of the two 1 kg vessels, with assumptions |
| `comparison.md` | run details, result tables, deviations and explanations |
| `extension.md` | HYPOTHETICAL design extension, engineering consequence, flags |

## Evidence gaps

- The version of record (CEJ) is closed access and was not consulted. The thesis chapter
  states that it was published as that article; equation, table and figure numbers here are
  the thesis numbers.
- The source does not state the TMA inlet concentration of its dynamic simulations, the
  Travis rate laws and parameters, the molecular diffusivity, or eps_mf and T for Fig. 7.4. The
  diffusivity is reconstructed from tau_ga (our Wilke-Lee estimate agrees within 0.5 %).
  P_TMA,in = 40 mbar is reconstructed from the 46.4 s saturation time, so that time is not a
  check.
- Fig. 7.3 and 7.4 values are digitised from vector paths (uncertainty in `source.yaml`). The
  remaining G4/G5 differences point to a weaker bubble-emulsion exchange at small bubbles in
  the source. We could not trace this to a stated equation or parameter (`comparison.md`,
  item 1).
- The source's bulk and agglomerate densities are not mutually consistent; we kept the batch
  surface area fixed.
- No independent (experimental) validation of utilisation or coverage. The design extension
  rests on scale-up correlations (Darton bubble size, Fournol TDH) that were not developed for
  nanoparticle agglomerates.
- Coverage inside rigid agglomerates is non-uniform at 1 atm (centre 56 % at 99 % mean). The
  effect of agglomerate break-up and re-formation is not modelled.
- The H2O half-reaction, purges, heat effects and the nano-porous gamma-alumina case of the
  source are not reproduced.
- No core issue filed: the case runs in plain Python. A candidate reusable capability is a
  two-phase bubbling fluidised-bed reactor model (bubble-emulsion exchange, film and
  intra-particle diffusion, surface-site balance). We did not find one in cheme core (GitHub code
  search returned nothing for the private repository, so this is not conclusive). Whether to
  add one is for the tracker to decide.
