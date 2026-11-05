# Benzene, toluene and xylenes from catalytic reformate

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of benzene, toluene and mixed xylenes together. The feed is debutanised catalytic reformate, and the plant has these steps:

- splitting off the C9+ aromatics (by mass only: they leave as the bottoms of the xylene column,
  or of a reformate splitter where the plant has one, and no energy is counted for a separate splitter);
- solvent extraction (sulfolane type) with solvent recovery;
- clay treatment;
- benzene, toluene and xylene columns.

Raffinate and C9+ aromatics leave as co-products. All units run continuously, with two clay treaters swapped when the clay is spent (LVOC BREF 4.3.6.3).

## How it is built

`lca/datasets/btx-reformate-extraction.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance.

| Item | Source | Standing |
|---|---|---|
| Reformate slate: 8.5 % benzene, 26.3 % toluene, 26.1 % xylenes, 74.3 % total aromatics | US DOE (2000) profile, Table 4-1, p. 108 | One typical slate citing 1990s sources. The table says "% yield" without a basis, and reading it as wt% is ASSUMED. C9+ aromatics (13.4 %) and non-aromatics (25.7 %) are taken by difference. |
| Recovery of benzene and toluene, 99.5 % | Honeywell UOP web page (ED Sulfolane) | A manufacturer's lower bound for extractive distillation, ASSUMED to hold for this unit. |
| Recovery of xylenes, 98 % | none read | ASSUMED, TODO |
| Electricity 41.5, steam 576.5 and fuel 512 kWh/t | LVOC BREF Table 4.3, p. 217 (BB2, BTX extraction) | Midpoints of the ranges in the 2012 data collection, gross values. |
| Spent clay 0.377 kg/t, solvent sludge 0.0265 kg/t | LVOC BREF Table 4.5 and 4.3.6.4, p. 219 | Midpoints of the source's ranges. |
| Water drained, 0.3 kg/t | LVOC BREF 4.3.2.2, p. 215 | The source says "a few hundred grams" per tonne; 0.3 kg is our reading of that. |

The balance follows from the slate and the recoveries: 1661 kg of reformate gives 140 kg benzene, 435 kg toluene, 425 kg mixed xylenes, 438 kg raffinate and 223 kg of C9+ aromatics.

The dataset models the non-aromatics as C7H16 and the C9+ cut as C9H12 (both ASSUMED). The reformate and the raffinate are mixtures, but core's element balance needs one formula per exchange. Each therefore gets a lumped C/H formula with 10^6 carbon atoms per lump, computed from the parameters. Those formulas must be recomputed whenever a composition or recovery parameter changes (`provenance.notes`).

The BREF's fuel is counted as heat from natural gas, delivered (ASSUMED). Its combustion is in the background activity, as in `hda-1`, so the dataset lists no flue gas. IPCC 2006 Vol. 3 gives no process emission factor for BTX extraction: the process converts nothing chemically, so all its CO2 comes from energy use.

The dataset has no allocation of its own: all five products are co-products. The default allocation is mass, recorded as a deviation because there are no sourced prices for the WBCSD price-ratio test (`allocation.deviation`).

## What is weak

- **The feed slate is a single, old, US figure.** It sets the split of the basis into benzene, toluene and xylenes, and how much reformate is needed. Reformates vary with the reformer's feed and severity: CCR reformates exceed 70 % v/v aromatics (REF BREF 2015, section 2.6). No open EU reformate composition was found.
- **No independent energy check.** Both bound benchmarks (`benchmarks/aromatics.yaml`) are the LVOC BREF table whose midpoints the dataset takes, so "inside" is true by construction. The independent references are recorded but not bound: US DOE (2000) includes the reformer, and a UOP patent (US 5,176,821) gives 388 to 582 kWh per t of extract for the extraction, about half the dataset's 1130 kWh/t, which adds the benzene, toluene and xylene columns. The patent does not say which steps it covers.
- **The energy covers the extraction unit only (BB2).** The reformate splitter that removes the C9+ cut is usually a refinery column, and its energy is left out (TODO). The source does not say whether its "per tonne of product" means the extract or one product. Its fuel range is wide (149 to 875 kWh/t), and the plants differ in configuration and heat integration.
- **Nothing is counted for:**
  - solvent make-up;
  - fugitive and vent VOC, including benzene;
  - SO2 from solvent degradation;
  - condensates and organics in the effluent.

  The BREF does not quantify these for extraction units, so they are TODO excludes, not zeros.
- The 98 % xylene recovery is not sourced, and the recoveries of benzene and toluene are a manufacturer's bound.
- `valid_until` is the reference year + 5, which gives 2017, so it has already lapsed.

## Linking

The main product has the registry slug `benzene`. Toluene, `xylenes`, `aromatics-raffinate` and `heavy-aromatics` are co-products. The reformate (`reformate`) links the Atlas producer `catalytic-reforming-1` explicitly (`lca/mappings.yaml`). The link is by mass, and the two datasets model the reformate differently: `catalytic-reforming-1` as C9H15 (0.877 kg C/kg), this one as the DOE slate (0.891 kg C/kg). So the linked system supplies about 22 kg less carbon per t of BTX than this dataset consumes (1.5 %, our arithmetic); it is not closed in carbon. Clay, spent clay and the solvent-regenerator sludge are reported gaps.

No existing consumer of benzene or toluene links to this dataset yet. `ethylbenzene-1` and `cumene-1` (benzene) and `hda-1` (toluene) each choose their supplier in their own `lca/mappings.yaml`. The products have no grade of their own, and the build takes the first producer by process id, so an unpinned consumer of benzene or toluene added later would get `btx-1` (before `hda-1` and `styrene-1`). A new consumer should pin its supplier.

## Not counted yet (TODO)

Splitter energy, solvent make-up, VOC and SO2, effluent organics, para-xylene recovery and isomerisation, the pygas and HDA variants. The full list is in the dataset's `system_boundary.excluded`.
