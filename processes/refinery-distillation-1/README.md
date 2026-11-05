# Crude oil distillation, atmospheric and vacuum

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI datasets only, with no flowsheet and no simulation. The first separation of a refinery: the crude distillation unit (CDU) splits desalted crude into gas, LPG, naphtha, kerosene, gas oil and atmospheric residue, and the high vacuum unit (HVU) splits the residue into vacuum gas oil and vacuum residue. Every crude passes through it, so this is the continuous route, and the only one.

## How it is built

Two hand-written **Tier 1** datasets, one per unit, as the sources report them:

| Dataset | Basis | Products (unallocated) |
|---|---|---|
| `lca/datasets/crude-atmospheric-distillation.yaml` | 1 t desalted crude | refinery gas 1 kg, LPG 20 kg, naphtha 144 kg, kerosene 82 kg, gas oil 227 kg, atmospheric residue 526 kg |
| `lca/datasets/atmospheric-residue-vacuum-distillation.yaml` | 1 t atmospheric residue | vacuum gas oil 603 kg, vacuum residue 397 kg |

The vacuum dataset's feed links to the atmospheric dataset's residue (`lca/mappings.yaml`). Every amount is the `formula` of its `parameters`, each with its source.

| Item | Source | Standing |
|---|---|---|
| Cut yields | TotalEnergies data sheet of Johan Sverdrup crude (assay of 2021), TBP curve, read at the REF BREF's cut points (180, 240, 360 degC) and at 560 degC for the vacuum cut (ASSUMED) | one crude, manufacturer literature; TBP yields taken as plant yields (ASSUMED) |
| Fuel, electricity, steam, cooling water | REF BREF 2015, Table 3.77 (section 3.19), midpoints of the ranges | EU data whose sources date from 1999 to 2001 |
| Sour water | REF BREF 3.19: 0.08 to 0.75 m3/t for the CDU (midpoint); for the HVU, the steam (ASSUMED) | the water input of the CDU closes the balance (ASSUMED) |
| Furnace CO2, CH4, N2O | IPCC 2006 Vol. 2, Tables 1.4 and 2.2, refinery gas defaults, times the fuel | the fuel is ASSUMED to be refinery gas |
| NOx, SO2, CO, particulates | REF BREF Table 3.78, one plant's loads calculated from permit limits | upper-bound character |
| Fugitive hydrocarbons | REF BREF 3.19: 5 to 190 t/yr for an 8.7 Mt/yr refinery, midpoint | booked in the CDU dataset for both units |
| Clean-out sludge | REF BREF 3.19: 6.3 to 20 t/day for an 8.7 Mt/yr crude unit, midpoint at 365 days | composition not stated, so outside the balance; treatment not mapped (a gap) |
| Allocation default (LHV) | IPCC 2006 Vol. 2, Table 1.2, default NCV of each cut's fuel category | category defaults, not values of these cuts |

**Element balance.** Every hydrocarbon stream is counted as the pseudo-component CH2 (ASSUMED), so the recorded balance is a mass balance of the cuts and the water. It says nothing about how carbon, hydrogen and sulfur split between the cuts. The fuel is counted in kWh, so its combustion emissions are outside the balance (core warns `cheme.lci-mass-outside-balance` for them).

**Allocation.** The datasets stay unallocated. For the export they name energy (LHV), the system model's step 2 for co-produced fuels. It is written as a dataset `allocation.deviation` because there is no curated rule for this process in `lci/mappings.yaml` yet; a `physical-energy` entry there would record it as the hierarchy's rule.

## Benchmarks

`benchmarks/refining.yaml`, seven KPIs. The independent ones are from US DOE (2007), converted from per barrel with the assay's densities (ASSUMED for the US slate). Fuel plus power is inside DOE's range for the HVU. For the CDU it is below DOE's range, because the expression cannot count the boiler fuel for steam, grid losses and desalting, all of which DOE includes. The electricity and CO2 references are single values, so the midpoints sit just outside them, with the reasons recorded. The REF BREF fuel range is the dataset's own source.

## What is weak

- **One crude.** Johan Sverdrup is a medium, slightly sour North Sea crude (28.7 API, 0.81 wt% S) refined in Europe. A light crude gives more naphtha and less residue, and a heavy one the opposite. Every cut moves with the crude.
- **The utility data are old**: the REF BREF table cites sources of 1999 to 2001. `valid_until` (reference year + 5) lapsed in 2006.
- **Steam pressure is not stated.** Steam is counted by mass and linked to the shared background, not to an Atlas boiler.
- Midpoints of ranges are our choice; the source does not recommend them. The CDU wastewater range is ninefold, and its midpoint dominates the water input.
- **Furnace fuel** is ASSUMED to be refinery gas at IPCC's 57.6 kg CO2/GJ. The REF BREF gives 43 kg/GJ for a hydrogen-rich fuel gas, and 74 to 79 kg/GJ for liquid fuels (Table 3.59).
- The fuel input stays a mapping gap: refinery fuel gas comes from the site's own units, and the library has no producer of it. The sludge's treatment is a gap too.

## Linking

Products carry the registry slugs `refinery-fuel-gas`, `liquefied-petroleum-gas`, `naphtha`, `kerosene`, `gas-oil`, `atmospheric-residue`, `vacuum-gas-oil`, `vacuum-residue`, and the feed `crude-oil`. `hydrotreating-1` links the gas oil, and `fcc-1` and `hydrocracking-1` link the vacuum gas oil, in their own `lca/mappings.yaml`. `catalytic-reforming-1` does not take this naphtha: it needs hydrotreated heavy naphtha, another grade. Naphtha steam cracking has no entry yet. `crude-oil`, `feed:fuel` and `output:sludge` are reported gaps.

## Not counted yet (TODO)

Desalting, H2S and NH3 in the overhead gas and sour water, ejector non-condensables, furnace decoking, overhead corrosion chemicals, and heat integration with other units. The full lists are in each dataset's `system_boundary.excluded`.
