# Purified terephthalic acid by air oxidation of p-xylene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This entry is a manifest and an LCI dataset only. It has no flowsheet and no simulation. The basis is one tonne of purified terephthalic acid (PTA).

## Route

p-Xylene is oxidised with air in acetic acid at about 200 °C and 20 bar, over a cobalt, manganese and bromide catalyst. The crude acid is crystallised, filtered and dried. It is then hydrogenated over palladium in hot water to remove 4-carboxybenzaldehyde, and recrystallised. This is the Amoco, or Mid-Century, process. US EPA AP-42 section 6.11 describes it as a continuous process. The LVOC BREF (section 2.1.2.3.8) names it as the way terephthalic acid is made, and LBNL-2001585 states that over 98 % of PET is made from PTA. The DMT route and oxygen-based oxidation are not modelled.

## How it is built

`lca/datasets/pta-px-air-oxidation.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H and O balance. The facts are in our own form, and each parameter names its source.

| Item | Source | Value used |
|---|---|---|
| p-Xylene, acetic acid, demineralised water | patent CN105001073A, background on a conventional 1.2 Mt/a plant | midpoints: 656 kg, 39 kg and 2.6 t per t |
| p-Xylene lost to residue, pond solids and mother liquor | the same patent | 4.8 kg/t, modelled as p-toluic acid (ASSUMED) |
| Cobalt; manganese | the same patent | 0.04 kg/t; 0.03 kg/t, the residue loss taken as the make-up (ASSUMED) |
| Electricity | MIDDEN report on Indorama Rotterdam (PBL and TNO 2021), Table 3 | 0.346 GJ/t, that is 96 kWh/t |
| Steam | IEA information paper (Saygin et al. 2009), Table 1: best practice for PTA, final energy (after Meyers 2005) | 2.6 GJ/t, that is 722 kWh/t |
| Vent VOC, CO, dust | US EPA AP-42 Table 6.11-1 (1983), less 99 % thermal oxidation (ASSUMED for every vent) | 0.20 kg VOC, 0.19 kg CO, 0.7 kg dust per t |
| CO2, effluent, oxygen | element balances | 95 kg CO2, 2.85 t effluent, 659 kg O2 per t |

Two cross-checks use figures from outside the model, though neither is fully independent:
- **CO2.** The 95 kg/t comes from the carbon balance: 57 kg/t from acetic acid and 39 kg/t from p-xylene. The MIDDEN report puts the 2016 CO2 from acetic acid burning at 23.1 kt (Table 4). Its own production estimate (350 kt/a at 80 % utilisation) turns that into about 83 kg CO2/t.
- **Effluent.** The 2.85 t/t from the water balance compares with the 3.0 t/t that follows from the patent's 3.6 Mt/a of sewage for the whole site.

## What is weak

- **The energy data are thin.** Electricity comes from one plant estimate, built from published figures. The report does not say whether off-gas expander power is netted out. The same report's steam, 0.981 GJ/t, is not used: the MIDDEN plant is Eastman-based (GPT equipment), with post-oxidation, and the report describes no hydrogenation step, so the hydropurification section modelled here (slurry heating to about 285 °C, staged crystallisation) would be missing. The steam is instead the IEA's best-practice value for PTA, 2.6 GJ/t of final energy (Table 1, after Meyers 2005). The paper does not name the route, so covering hydropurification is ASSUMED. The patent's 0.7 to 1.0 t of steam per t for conventional Chinese plants, at an unstated pressure, is about 1.4 to 2.2 GJ/t at an ASSUMED 2.0 to 2.2 GJ per t of steam. The IEA's Western European average (Table 13, after Boustead 2002) has 1.7 GJ/t of electricity, 1.7 GJ/t of steam and 1.6 GJ/t of fuel, so a plant that fires its hydropurification heaters would need more heat than the dataset counts. The steam's uncertainty is ASSUMED at gsd2 1.5, and the technological pedigree of both utilities is 4.
- **All three benchmark KPIs fall outside their ranges**, each with a stated reason (`benchmarks/oxygenates.yaml`):
  - The yield is 97.4 %, against the MIDDEN report's 98.3 to 98.9 %.
  - Acetic acid is 0.039 t/t, against LBNL's 0.04 to 0.09.
  - Electricity plus steam is 2.95 GJ/t, against LBNL's 5.3 to 9.7, whose basis is not stated; the IEA's figures in primary energy with fuel (7.6 GJ/t for the Western European average) fall inside it.
- The sources mix regions and years: Chinese feeds from about 2015, Dutch utilities for 2016 and US vent factors from 1983. `location` is GLO. `valid_until` is the reference year + 5, 2021, so it has already lapsed.
- The patent was read in Google's machine translation.
- These parts of the model are ASSUMED: the residue compound, the vent control applied to every vent, VOC counted as acetic acid, all water to the effluent, and complete combustion. AP-42's crude-TPA vent factors are also applied per kg of PTA.
- All the acetic acid not lost as vent VOC is counted as burnt. The patent puts about 2 to 3 kg/t of it into the residue and 0.6 to 1.8 kg/t into the effluent, so the CO2 is high by about 4 to 7 kg/t.
- The manganese make-up (0.03 kg/t) may be up to 0.05 kg/t. The patent gives a second loss of 0.02 kg/t, and the translation does not make clear whether it adds to the first.

## Linking

The product has the registry slug `terephthalic-acid`. The acetic acid links explicitly to `acetic-acid-1` (`lca/mappings.yaml`). p-Xylene is a reported mapping gap, because no Atlas process makes it (`btx-1` makes mixed xylenes, with no para-xylene recovery). `pet-1` links this PTA. Steam is counted as heat delivered.

## Not counted yet (TODO)

- Hydrogen and the palladium catalyst of the purification. Palladium is a precious metal and must never be cut.
- The bromine promoter and methyl bromide.
- Support fuel for the thermal oxidiser.
- The effluent's organic load and metals.
- Entrainer make-up.

The full list is in the dataset's `system_boundary.excluded`.

## Sources read

- Patent CN105001073A on Google Patents (machine translation).
- Tran and West (2021), PBL publication 4617, sections 1.4, 2.3 and 2.6.
- US EPA AP-42 section 6.11.
- LVOC BREF (2017), section 2.1.2.3.8.
- Karali et al. (2024), LBNL-2001585, section 2.3.
- Saygin et al. (2009), IEA information paper, Tables 1 and 13 (PTA rows).

Two open-access MDPI papers on PTA from 2026 (*Sustainability* 18:10769 and *Clean Technologies* 8:78) could not be retrieved (HTTP 403), so they are not cited.
