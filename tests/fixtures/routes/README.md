# Route fixture library (synthetic)

Two routes to the same product, for the route groups of `build_catalog.py` (`routes.json`,
`scripts/routes.py`) and the Atlas comparison pages (ChemE-as-Code/website#38). Every number is
synthetic and labelled so; none is engineering data or taken from a source.

- `route-electrolysis`: a plantcode-style process with an LCI dataset, an LCA whose footprint may
  be published (synthetic public source, run manifest with a data quality rating) and a Monte
  Carlo interval.
- `route-smr`: a manifest-only process with a hand-written Tier 1 LCI dataset and no LCA.

Both make `hydrogen/gaseous-30bar` per 1 kg. The deliberate mismatches: `route-smr`'s dataset
states `system_model: apos` (the other is cut-off), and it has no data quality rating.
