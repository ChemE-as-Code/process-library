# Data sufficiency: liquid-infused membrane, oil-in-water emulsion (#340)

Issue #340 (P3, tracker #333) asks first whether the published data are enough for a
reproduction, and of what. This note records what exists, where, under what terms, what is
missing, and the scope that follows. It was written before the tolerances were frozen.

## Source

Bazyar, van de Beek and Lammertink, "Liquid-Infused Membranes with Oil-in-Water Emulsions",
Langmuir 35 (29), 9513-9520, 2019, doi:10.1021/acs.langmuir.9b01055. Open access (ACS
AuthorChoice) under CC BY-NC-ND. Full text in PubMed Central as PMC6750837, version 1
(`pmcid-ver` PMC6750837.1); supporting information (SI) `la9b01055_si_002.pdf`, 23 pages.

Access used here:

| Item | Where | Obtained | Use |
| --- | --- | --- | --- |
| Article full text (JATS XML) | NCBI E-utilities efetch, db=pmc, id 6750837 | yes; byte-identical on three downloads (sha256 in `source.yaml`) | text, Tables 1-4, Table 2 fit parameters, stated pressures |
| Article PDF | ACS, University of Twente repository, Europe PMC | no: all three returned a bot-check page to a script | not needed; the XML has the same text and tables |
| SI PDF | Europe PMC supplementary-files archive (zip generated on request; the files inside were byte-identical in two downloads) | yes (sha256 in `source.yaml`) | Tables S1-S3, porometry numbers, membrane thickness, emulsion-run oil flux |
| Figure 4b (LEP against concentration) | same archive, `la9b01055_0004.jpg`, 400 x 174 px for both panels | yes, low resolution | the 12 measured LEP points, digitised (method and uncertainty in `source.yaml`) |
| Raw data (flux and pressure logs, IFT series, droplet size data) | none published | - | - |

Reuse terms: CC BY-NC-ND forbids derivatives of the article. We copy no text, table or figure.
We restate facts and numbers (property values, fitted parameters, stated pressures, water
fractions) in our own form with locators, which CLAUDE.md allows, and draw every figure from our
own code. The run fetches the article XML at runtime into a cache outside git; nothing of the
source is committed.

## What the data support

1. **Interfacial tensions.** Measured IFTs of the four surfactant solutions and pure water
   against hexadecane and against Krytox GPL 101 (SI Table S2), hexadecane-K101 IFT (SI Table
   S1), and the Szyszkowski fit parameters a and b with half confidence intervals (Table 2).
   Enough to recompute every tabulated IFT from the fit.
2. **Entry pressures.** Young-Laplace with complete non-wetting and the fitted curvature radii
   (Table 2). Reported numbers to compare with: hexadecane entry through the K101-infused
   membrane 0.08 bar; surfactant-solution entry through the hexadecane-infused membrane
   0.05 bar (CTAB 50) and 0.15 bar (SDS 50); the authors' combined-interface estimate for the
   K101-infused membrane under a hexadecane layer, 0.26 bar (SDS 50) and 0.15 bar (CTAB 50).
   The other LEP points (pure water, 10 % cmc, K101-infused) exist only in Figure 4b. We
   digitised all 12 points from the low-resolution figure image, with an uncertainty of about
   0.015 bar; they are compared as digitised values, not as reported numbers.
3. **Permeating phase.** Water fraction in the permeate for the eight combinations of emulsion
   (SDS or CTAB at 10 or 50 % cmc) and membrane (dry or K101-infused), all at a transmembrane
   pressure (TMP) of at most 0.1 bar (Table 3). This is the observed selectivity.
4. **Flux.** One flux record only: the oil flux through the K101-infused membrane from the
   SDS 10 emulsion in dead-end mode, average 0.4e-5 m3 m-2 s-1 at 0.1 bar (SI Figure S5 and its
   text), with the authors' Darcy permeability 1.74e-4 Darcy. Pure-hexadecane liquid-liquid
   displacement permeabilities for the dry and K101-infused membrane (SI Table S3).
5. **Membrane.** PVDF cast from 15 wt% in NMP, mean pore radius 1.78 um with spread 0.14 um,
   largest pore radius 1.92 um (first bubble point), thickness 134 um, test cell diameter
   25 mm (Figure 3).

## What is missing

- Figure 4b values as numbers. The digitised values carry about 0.015 bar uncertainty, which
  is close to the 22 mbar pressure step of the measurement.
- The exact TMP of each emulsion run (stated only as at most 0.1 bar; the SI flux calculation
  uses 0.1 bar).
- Any flux for the other seven emulsion-membrane combinations, any flux against TMP, and any
  water flux after breakthrough. A flux-pressure curve does not exist in the source.
- Time series of infusion-liquid retention under emulsion flow (only an LLD estimate of about
  45 % retained after pure hexadecane flow).
- Crossflow data of any kind: the study is dead-end, with gravity creaming bringing the oil to
  an upside-down membrane.

## Scope decided from this

- **Reproduction:** recompute the eight tabulated IFTs, the 12 digitised Figure 4b entry
  pressures, the four entry pressures stated in the text, the
  hexadecane entry pressure, the emulsion-run oil permeability and the three LLD active-pore
  fractions from the reported inputs, under tolerances frozen before the run.
- **Model against the paper's own observations (not independent validation):** apply the
  threshold model at 0.1 bar to the eight Table 3 cases and report how many it classifies
  correctly. Reported, not part of the pass rule (see `tolerances.yaml`).
- **Pressure sweep:** operating window (no permeation, selective oil permeation, water
  breakthrough) against TMP for every case.
- **Membrane area:** only for the one case with flux data (K101-infused, SDS 10, 0.1 bar,
  dead-end), stated as a batch-cell figure that does not carry over to a continuous module.
- **Design extension (hypothetical):** one changed input, the pore radius, and its effect on the
  window width and on the tolerable pressure variation in a module.
- **Crossflow sizing:** not achievable from these data; `extension.md` lists what would be
  needed.
