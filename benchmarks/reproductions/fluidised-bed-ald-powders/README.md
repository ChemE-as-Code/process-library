# Fluidised-bed ALD on powders: reproduction and scale-up

Case study for issue #336 (scope tracker #333). Protocol: ADR 0030 (reproductions,
tolerances frozen first) and ADR 0031 (case studies: a reproduction plus a labelled design
extension; status Proposed, merged into this branch from main via PR #344).

**Engineering question.** How do batch size and reactor height affect surface coverage and
precursor utilisation in fluidised-bed atomic layer deposition (ALD) on powders?

**System.** Trimethylaluminium (TMA) half-reaction on Degussa P-25 TiO2 nanoparticle
agglomerates in a bubbling fluidised bed at 500 K, as modelled by Grillo, Kreutzer and van
Ommen, Chem. Eng. J. 268 (2015) 384-398 (doi:10.1016/j.cej.2015.01.067). The article is
closed access. We used its open version, chapter 7 of F. Grillo's TU Delft thesis (2018,
doi:10.4233/uuid:97fabd08-203c-4471-9596-7ad91f7eb2c0). The ALD-on-particles literature index
(Zenodo 10.5281/zenodo.14832687, CC BY-NC-ND) was used for discovery only.

We re-implemented the model from the published equations in `run.py`: two-phase bubbling bed
(Table 7.1, p. 178), agglomerate diffusion (Table 7.2, p. 185), time scales, and the
quasi-steady utilisation and required bed height (Eqs. 7.24, 7.51, 7.52). The chapter gives
the surface-coverage balances (Table 7.3, p. 187) but not the Travis et al. rate expressions
nu_1 to nu_3 or their parameters. Our dynamic model therefore uses lumped first-order site
kinetics, fitted only to the reported reaction time scale.

## Status

| | Status |
| --- | --- |
| Reproduction | **partial** under the frozen rule, **one pass from FAIL**: 29 of 38 comparisons pass (29 needed), all of G1 (saturation time) and G3 (stated bed heights). Five passes lie within 1.4 percentage points of their 10 % limit, among them the required 1 mbar bed-height check (+9.4 %, see below). Time scales: 11/11 within 1.6 % (tau_int 7 %). Required bed height H* from Fig. 7.4: 13/20, deviations from -35 % to +16 %. Dynamic bubble profile (Fig. 7.3): 1/3. Of 34 independent comparisons, 25 pass (73.5 %). Under a stricter budget written after the run (rounding and digitisation only; a sensitivity view, not the verdict of record) the result would be FAIL, 17/38. See `comparison.md` |
| Independent validation | none: no experimental outlet-precursor or coverage data used. A title search of the literature index (it has no substrate field) found four AlOx-on-titania fluidised-bed papers and missed others; candidate validation sources, not examined, are King et al. 2007 (outlet TMA by mass spectrometry) and Valdesueiro et al. 2015 (TMA/H2O on TiO2 at 1 atm) (`addendum.yaml`) |
| Design extension | hypothetical: 22 g to 1 kg at fixed 99 % mean coverage, two scale-up strategies, dimensioned section view (`extension.md`) |
| Specialist review | not yet (optional follow-up: ALD and fluidisation specialist) |

**Issue deliverables.**

| Deliverable (#336) | Status |
| --- | --- |
| 1. Select a powder/precursor system and reproduce one utilisation or coverage result from the dynamic model | **not met.** System: TMA on P-25 TiO2. The dynamic bubble profile (Fig. 7.3) agrees at 1 of 3 points. The dynamic saturation time and CH4 yield cannot be evaluated (inlet concentration and Travis rate expressions not stated). What is reproduced is the quasi-steady utilisation reduction (Eqs. 7.51 and 7.52, G3) and the time scales (Table 7.4) |
| 2. Change batch size at fixed target coverage; plot pulse timing, outlet precursor and coverage; dimensioned section with scale-up assumptions | met, as a hypothetical extension: 22 g to 1 kg at 99 % mean coverage, two strategies (`extension.md`, fig3 to fig5) |
| 3. Source version, numerical comparison, clean rerun command, input labels, evidence gaps | met: `source.yaml`, `comparison.md`, rerun below, `inputs.yaml` (labels corrected in `addendum.yaml`), Evidence gaps below |

**Why the verdict is marginal.** The bed heights at small bubbles differ from Fig. 7.4 in a way
that depends on bubble size and changes sign, from -35 % at d_b = 1 cm to +16 % at 4 cm; the
cause is not identified. Separately, the slope of the Fig. 7.3 profile implies a source
K_be/u_b about 15 % lower than ours at d_b = 1 cm. The required 1 mbar text check passes at
+9.4 % under a 10 % tolerance that was set after a hand estimate of +9.2 %; rounding of the
stated value explains 0.8 % of it, and the rest is an allowance for K_be evaluation that the
tolerance file does not quantify. With a tolerance based on rounding and digitisation only,
that check would fail and the verdict would be FAIL. The reader can judge the PARTIAL label
with that in mind (`comparison.md`, "How firm the PARTIAL verdict is").

**Headline (hypothetical extension, not validated).** In our model at 1.013 bar, with Darton
bubble sizes, more than 99.9 % of the TMA is taken up in both 1 kg designs. A 99.99 % target is
not met in either: emulsion slip, which Eq. 7.52 ignores, keeps the loss at 0.03-0.1 %. The
pulse length is set by the settled bed height: 46 s at H0 = 60 mm (bed 404 mm wide) and 163 s
at H0/d_t = 1 (214 mm x 364 mm expanded bed, vessel 1.11 m). Bubble size is the main risk to
utilisation: 4.5 cm bubbles in the 1 kg geometric scale-up would let 1.7 % of the TMA escape.
Our exchange is stronger than the source's at small bubbles, so these slips are optimistic.

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
| `inputs.yaml` | every model input with value, unit, label (measured, reported, reconstructed, assumed) and source or rationale; "reported" is a fourth label beside ADR 0031's three, and some labels are corrected in `addendum.yaml` |
| `tolerances.yaml` | acceptance tolerances and pass rule, frozen in commit 38aa2e3f before the first comparison run; header discloses pre-freeze hand estimates |
| `tolerances-strict-budget.yaml` | written after the run: a stricter budget (rounding and digitisation only), reported as a sensitivity view next to the frozen verdict |
| `addendum.yaml` | written after the run: corrections to `source.yaml` and `inputs.yaml` (titles, reuse terms, literature index, page locators, input labels) and the validity limits used to flag the extension |
| `sufficiency.md` | what the source provides, what is missing, and the achievable scope |
| `digitise.py` | how the Fig. 7.3 and 7.4 values were read from the PDF's vector paths |
| `run.py` | single entry point: reproduction, dynamic model, extension, figures |
| `results/comparison.json` | every compared quantity, verdict, supplementary values, extension results |
| `results/fig1-required-bed-height.svg` | H* against bubble size, ours vs digitised source (Fig. 7.4) |
| `results/fig2-bubble-profile.svg` | dynamic bubble-phase TMA profile vs digitised source (Fig. 7.3) |
| `results/fig3-pulse-breakthrough-coverage.svg` | outlet TMA and coverage against time, lab and 1 kg (pulse timing) |
| `results/fig4-batch-sweep.svg` | pulse time and precursor slip, 22 g to 10 kg (Eq. 7.51 and our dynamic model; out-of-range points crossed) |
| `results/fig5-section-view-1kg.svg` | dimensioned section views of the two 1 kg vessels, with assumptions |
| `comparison.md` | run details, result tables, deviations and explanations |
| `extension.md` | HYPOTHETICAL design extension, engineering consequence, flags |

## Evidence gaps

- The version of record (CEJ) is closed access and was not consulted. The thesis chapter
  states that it was published as that article; equation, table and figure numbers here are
  the thesis numbers.
- The source does not state the TMA inlet concentration of its dynamic simulations, the
  Travis rate laws and parameters, the molecular diffusivity, or eps_mf and T for Fig. 7.4. The
  diffusivity is reconstructed from tau_ga (our Wilke-Lee estimate agrees within 0.5 %). The
  chapter's surface-coverage balances are given (Table 7.3, p. 187); the rate expressions
  nu_1 to nu_3 and their parameters are not. See `sufficiency.md`.
  P_TMA,in = 40 mbar is reconstructed from the 46.4 s saturation time, so that time is not a
  check.
- Fig. 7.3 and 7.4 values are digitised from vector paths (uncertainty in `source.yaml`). The
  G4 differences depend on bubble size and change sign (-35 % to +16 %); the Fig. 7.3 slope
  implies a source exchange about 15 % weaker at d_b = 1 cm. We could not trace either to a
  stated equation or parameter (`comparison.md`, item 1).
- The thesis PDF may be downloaded and used only for strictly personal use without the
  author's consent (repository cover page); chapter 7 is also an Elsevier article. We use
  facts and numbers only.
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
