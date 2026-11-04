# Data sufficiency: InP quantum-dot treatment and optical quality (#342)

Issue #342 is a P3 case of tracker #333: check the data before promising a result. This note
records what exists, under which terms, what is missing, and the scope chosen from it. It was
written after reading the sources and inspecting the files, and before any computed value was
compared with a reported one.

## What exists

| Item | Where | Terms | Content used here |
| --- | --- | --- | --- |
| Dataset v1 | 4TU.ResearchData, doi 10.4121/1370d230-bca3-4af4-af06-1a9f168a4b10.v1 | CC BY-NC-SA 4.0 | one 3.47 GB zip and a README; ordered by figure |
| Article | Chem. Mater. 2022, 34, 10093, doi 10.1021/acs.chemmater.2c02800; PMC9686131 | CC BY 4.0 (open access) | methods, reported PLQYs, peaks, widths, lifetimes |
| Supporting information | cm2c02800_si_001.pdf (via Europe PMC) | no separate licence stated; distributed as supplementary material of the CC BY 4.0 article (PMC9686131). We use only facts restated in our own words | captions of Figures S4-S9, S16, S19 (doses, conditions) |

The archive holds, for the optics: 64 absorbance files (PerkinElmer Lambda 365 ASCII, 300-700 or
300-900 nm, 1 nm), 63 emission files (Edinburgh FLS980, 387 nm excitation, corrected spectra),
3 decay records (Figure 1F) and one integrating-sphere record (Figure S19). 141 optical files
reduce to 110 distinct files: 31 are byte-identical copies stored under other figure folders,
sometimes under another name. The rest of the archive is NMR, XPS, XRD and DFT (about 3.4 GB of
cube files), not used.

Each absorbance header carries the original file name and the measurement date and time. The
emission headers carry instrument settings (slits, dwell, repeats, step, correction flags) but
no date; archive time stamps give dates for Figure 1, 4 and S9 files and only an export date
(2021-10-28) for S5-S8 and S16.

## Can the optical comparison be reproduced?

Yes, for the relative PLQY. Each PLQY session has a coumarin 102 reference recorded on the same
day with the same instrument settings (checked per pair in run.py), the absorbance at the
excitation wavelength of sample and reference, and corrected emission spectra. The Methods
state the reference quantum yield (0.95), the excitation wavelength (387 nm) and the method
(IUPAC relative method). The paper states numbers, not only curves: 55 %, 64 %, ca. 40 %, <5 %,
>70 %, 85 % (Figure 1E text), annotations 67 %, 85 %, <0.2 % (Figure 1F) and 55, 45, 54, 26 %
(Figure 4B), so no digitising is needed.

## What is missing or ambiguous

- **Processing details.** Refractive-index correction, absorbance or absorptance, baseline and
  integration range are not stated. The detector calibration curve is not archived; the
  emission headers say the correction was applied by the instrument. These are assumptions in
  inputs.yaml; sensitivities are reported.
- **Measurement solvent.** The solvent in the cuvette for aliquots is not stated (treatment in
  mesitylene or hexadecane, purified QDs in toluene).
- **Concentration.** The Methods say OD ~0.1 at 387 nm for all samples, but the 0 min aliquots
  have OD 0.31-0.36 and the RT aliquots 0.21-0.23 (raw OD at 387 nm, as inspected here; after
  the 680-700 nm baseline of run.py, 0.31-0.36 and 0.18-0.21): inner-filter and reabsorption effects are
  not controlled for those.
- **Sample identity.** See the flags in mapping.csv. The main ones: the Figure 4B "hot injection
  in situ HF" files are the washed 150 C sample of Figure 1 (text 64 %, Figure 4B 54 %); the
  200 C series mixes internal names HF130 and HF140; the ZnCl2 file says 60 min while the
  Methods and Figure 1E say 5 min; the Figure 1F 200 C decay is dated five days before the 200 C
  PLQY session; Figure S9's "as synthesized" is the 0 min aliquot of 2021-12-08; S6's benzoyl
  fluoride sample has no reference of its day; Figure 4B's heat-up in situ HF file has no stated
  conditions.
- **Batch and replicates.** No stock-batch identifier and no replicate measurement of any
  condition. Sessions span 2021-02 to 2022-10. Differences between sessions cannot be separated
  from batch, date or instrument effects.
- **Material balance.** Aliquot dilution and redispersion volumes are not stated, so the InP
  retained after treatment can only be estimated from absolute absorbance under an equal-dilution
  assumption, and not at all for washed samples.

## Scope decided

1. Reproduce the Figure 1E/1F PLQYs (primary), the Figure 1C absorption peak shift, the stated
   emission width, the Figure 4B comparison (a second documented treatment: pure InF3 against
   in situ HF on two syntheses), the S9 InF3 maximum, the Figure 1F lifetimes and the S19
   sphere value, under tolerances frozen before the run.
2. Map every optical file to sample, treatment and reference (mapping.csv); verify the mapping
   against the instrument headers at run time; flag ambiguities.
3. Screen all samples with a computable PLQY against stated quality criteria (PLQY, emission
   FWHM, OD window) with varied thresholds, and list confounders per sample.
4. One hypothetical design extension (extension.md) built only on the 150 C series of one
   session, where the equal-dilution assumption is most defensible.

Out of scope: NMR, XPS, XRD and DFT data; causal attribution of PLQY changes to surface chemistry
(the optical data alone cannot show it); any scale-up claim.
