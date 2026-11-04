# Data sufficiency: fluidised-bed ALD on powders (#336)

Written after the comparison run, in response to review (ADR 0031 asks for this file where the
source lacks what a reproduction needs). The gaps were already recorded in the README
(Evidence gaps) and in `comparison.md` (Not evaluable). This file collects them in one place.

## What exists

| Item | Where | Licence and access |
| --- | --- | --- |
| Model article, Grillo, Kreutzer and van Ommen, CEJ 268 (2015) 384-398 | doi:10.1016/j.cej.2015.01.067 | closed access; not consulted |
| Open version: chapter 7 of Grillo's TU Delft thesis (2018) | doi:10.4233/uuid:97fabd08-203c-4471-9596-7ad91f7eb2c0, file sha256 in `source.yaml` | openly downloadable; no open licence; download and distribution only for strictly personal use without consent (cover page); chapter 7 is also the Elsevier article. Facts and numbers only |
| Model equations: reactor scale (Table 7.1, p. 178), agglomerate scale (Table 7.2, p. 185), coverage balances (Table 7.3, p. 187), time scales (Table 7.4, p. 188), parameters (Table 7.5) | thesis chapter 7 | as above |
| Reported results: tau_sat_min (Eq. 7.25), time scales, H* text values (p. 199), Fig. 7.3 and Fig. 7.4 curves (vector paths, digitised) | thesis chapter 7 | as above |
| ALD-on-particles literature index, version 2025-02-07 | Zenodo 10.5281/zenodo.14832687 | CC BY-NC-ND 4.0; discovery only, not redistributed |

## What is missing

- TMA inlet concentration of the dynamic simulations. Reconstructed (40 mbar) from the 46.4 s
  saturation time, which is therefore not a check.
- Travis et al. rate expressions nu_1 to nu_3 and their parameters. Our kinetics are lumped and
  fitted to tau_rxn only, so the CH4 yield (about 1.5 per TMA) cannot be evaluated.
- Molecular diffusivity of TMA in N2 (value and Lennard-Jones energy). Reconstructed from tau_ga.
- eps_mf and T for Fig. 7.4. Table 7.5 values assumed.
- Any experimental outlet-precursor or coverage time series. Candidates exist but were not
  examined: King et al. 2007 (in situ mass spectrometry) and Valdesueiro et al. 2015 (TMA/H2O
  on TiO2 at 1 atm) (`addendum.yaml`).

## Achievable scope

- Reproducible: the analytical results (Eq. 7.25) and the transport time scales and Thiele
  moduli (Table 7.4).
- Partly reproducible: the quasi-steady utilisation reduction and bed height (Eqs. 7.51 and
  7.52). The two bed heights stated in the text pass (G3 2/2, the 1 mbar value only just, at
  +9.4 % against a 10 % tolerance). The Fig. 7.4 curves agree at 13 of 20 points (G4), with
  deviations from -35 % to +16 % that depend on bubble size; we attribute them to a difference
  in K_be/u_b whose cause is not identified.
- Partly reproducible: the dynamic bubble-phase profile (Fig. 7.3), which depends on the
  exchange and hardly on the kinetics.
- Not reproducible from the published material: the dynamic saturation time and the CH4
  yield. So issue deliverable 1 ("reproduce one utilisation or coverage result from the
  dynamic model") cannot be fully met from this source alone.
- Not validated: no independent data were used.
