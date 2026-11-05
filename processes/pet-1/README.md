# Polyethylene terephthalate by continuous PTA polycondensation and SSP

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of bottle-grade PET resin, made from purified terephthalic acid (PTA) and ethylene glycol (MEG). The plant esterifies the two continuously, polycondenses the melt, cuts chips and then raises the viscosity by continuous solid-state polycondensation (SSP).

## Why this route

PTA-based continuous polycondensation is the main industrial route. The POL BREF (2007, section 10.2) describes it next to two others. The continuous DMT route releases methanol. The batch DMT process (DMT-BPU) runs in batch autoclaves. NAPCOR 2020 counts only PTA-based plants, because PET from DMT is a small share in North America. Its plants use melt phase with SSP, melt-to-resin (MTR, which reaches bottle-grade viscosity in the melt), or Integrex (integrated with PTA making). Every step of the modelled route is continuous: the BREF's continuous SSP reactors handle 20 to 400 t/d each, while batch SSP tumblers manage 1 to 4 kt/a.

## How it is built

`lca/datasets/pet-pta-continuous-ssp.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. Two open sources are used, and their facts are restated in our own words. Each parameter cites its table.

| Item | Source | Standing |
|---|---|---|
| PTA, isophthalic acid, MEG | stoichiometry of the repeat unit C10H8O4, with the BREF's polymer waste, effluent COD and air losses; isophthalic share from NAPCOR | calculated |
| Electricity, natural gas, water consumed | NAPCOR 2020, Table 36 (seven US plants, 2015) | industry average, several technologies |
| Polymer waste, other and hazardous waste, COD, acetaldehyde and glycol to air, catalyst, stabiliser | POL BREF Tables 10.4 and 10.5 | ranges of EU plants (midpoints) or upper bounds |
| CO2 and water of the heaters | complete combustion of the gas, taken as methane | calculated |

The feeds come out at 0.873 t of diacids (850 kg PTA, 23 kg isophthalic acid) and 0.334 t of MEG per t. The MEG is inside the BREF's 0.32 to 0.355 t/t. The diacids are just above its 0.825 to 0.87 t/t, because the polymer waste is taken at the midpoint of a very wide range (`benchmarks/polymers.yaml`). NAPCOR reports 0.860 t of diacids and 0.345 t of glycol per t.

## What is weak

- **Two sources from different places and times.** The energy and water are US plants of 2015. The losses and emissions are EU plants from about 2004. `valid_until` (2020) has lapsed.
- **Homopolymer model.** Diethylene glycol units, toners and other additives are left out. Isophthalic acid is counted with the terephthalic acid, since it has the same formula.
- **Polymer waste** is the midpoint of 0.14 to 18 kg/t, a 128-fold range (gsd2 11.3).
- **Effluent organics**: all of the BREF's COD before treatment is read as ethylene glycol (ASSUMED). Steam-ejector condensate is not counted, so the wastewater is only the reaction water.
- **Natural gas** is converted from volume to mass at an ASSUMED 15.56 °C and 101.325 kPa, as pure methane. Heater NOx and CO are not in either source.
- Acetaldehyde, glycol to air and hazardous waste are the BREF's upper bounds for EU plants. They are not conservative: NAPCOR's US plants report about five times the glycol to air (0.049 kg/t) and about ten times the hazardous waste (4.8 g/t), while its acetaldehyde (0.010 kg/t) is below the bound. NAPCOR's total solid waste (about 1.9 kg/t) is well below the BREF midpoints used here (about 13 kg/t of polymer and other waste). The "other waste" has no composition. It is outside the element balance, and the feeds do not supply its mass.
- The gas use is not stated by NAPCOR. Firing it in the heat-transfer-medium heaters is our reading (ASSUMED).
- The energy cannot be checked independently. The BREF gives only total energy per step. The dataset's 2930 MJ/t is inside the melt-phase range alone, and slightly below the sum of the lowest melt-phase and SSP values (about 2990 MJ/t). The BREF's single figure for TPA-based high-viscosity PET for food packaging, the grade nearest to bottle resin, is 18500 MJ/t, about six times higher, with no reason given.
- The antimony catalyst and the phosphorus stabiliser are named in the BREF's DMT section. Their use in the TPA process is our reading.

## Linking

The product has the registry slug `polyethylene-terephthalate` (new, with `terephthalic-acid` and `isophthalic-acid`). MEG links explicitly to `ethylene-glycol-1` (`lca/mappings.yaml`). PTA links explicitly to `terephthalic-acid-1`. Isophthalic acid is a reported mapping gap: no Atlas process makes it, and the shared vocabulary has no entry for it. Natural gas is not linked inside the Atlas, the same as in `styrene-1`.

## Not counted yet (TODO)

Nitrogen for SSP and blanketing, diethylene glycol and additives, VOC other than acetaldehyde and glycol, HTM losses, heater NOx and CO, NAPCOR's coal and minor fuels, ejector condensate, metals in the effluent, and the fate of the consumed water. The full list is in the dataset's `system_boundary.excluded`.
