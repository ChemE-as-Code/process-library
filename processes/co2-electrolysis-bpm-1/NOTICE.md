# Notice

`scripts/adapt_4tu.py` downloads, and `data/measured/` and `experiments/electrochemistry/` hold
values calculated from, the dataset

> G. Prats Vergel, H. Mu, N. Kolobov, J. Biemolt, D. A. Vermaas, T. Burdyny, "Data underlying the
> publication: Water Dissociation Efficiencies control the viability of reverse-bias bipolar
> membranes for CO2 electrolysis", 4TU.ResearchData, version 1 (2025),
> https://doi.org/10.4121/5c4fc325-a71b-4ca8-9c1b-01c0405936a2.v1

licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The derived values are
our calculation from the raw titration volumes, cell voltages, flow-meter readings and gas
chromatograph mole fractions (DESIGN.md D-002, D-005), not a copy of the dataset. The figures
`figures/polarisation.svg`, `faradaic-efficiency.svg`, `partial-current-density.svg` and
`water-dissociation-efficiency.svg` are drawn by `cheme` from those values. None of the dataset's
files are redistributed here. The cell configuration in `process/design-basis.yaml` and the
Faradaic-efficiency method (the gas conversion factors of a CO2-calibrated flow meter) restate
facts from the Methods and Supplementary Note 5 of

> G. Prats Vergel et al., "Water dissociation efficiencies control the viability of reverse-bias
> bipolar membranes for CO2 electrolysis", Nature Chemical Engineering (2025),
> https://doi.org/10.1038/s44286-025-00306-7

`figures/cell-cross-section.svg` is drawn by `scripts/cell_section.py` from our own files, not
traced from the paper.

The formation enthalpies behind the heats of reaction in `process/reactions.yaml` are the CODATA
Key Values for Thermodynamics (Cox, Wagman, Medvedev, Hemisphere, New York, 1989), used as facts
with their source.
