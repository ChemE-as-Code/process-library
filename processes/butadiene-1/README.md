# 1,3-Butadiene by extractive distillation of a crude C4 cut

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of 1,3-butadiene, recovered from the crude C4 cut of a naphtha steam cracker by continuous extractive distillation with a polar solvent. Raffinate-1 (butenes and butanes) and a purge of C3 and C4 acetylenes to fuel use are co-products.

## Route

Almost all butadiene is a co-product of steam cracking, recovered from the C4 cut. US DOE (2000, p. 34) puts it at over 95 %, and Neelis et al. (2007, Table A1) give the route from steam cracking a 100 % share in Western Europe. Butadiene and butane form an azeotrope, so it is recovered by extractive distillation or extraction with a polar solvent (LVOC BREF 2017, section 3.2.2.4). BASF says about a third of the world's extraction plants use its NMP process; US EPA (2025) names acetonitrile, DMF, furfural and others as well, and US EPA (1996, p. 4-6) calls furfural the typical solvent of the US plants it describes. The plants run continuously; BASF cites four to eight years between turnarounds. On-purpose dehydrogenation of butane or butenes is a minor route and is not modelled.

## How it is built

`lca/datasets/butadiene-c4-extractive-distillation.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. The crude C4, raffinate and purge are mixtures, so their C/H formulas are lumped from the parameters. They must be recomputed when a parameter changes.

| Item | Source | Value used |
|---|---|---|
| Crude C4 composition | US EPA (1996), Table 4-3: a typical naphtha-cracker C4 cut | 39.3 wt% 1,3-butadiene, 50.8 % butenes, 8.4 % butanes, 1.5 % C3 and C4 alkynes and 1,2-butadiene |
| Butadiene recovery | BASF web page: yield above 98 % | 0.98, the bound itself (ASSUMED) |
| Electricity, steam | IEA paper, Table 13: estimated current Western European average for C4 separation | 0.7 GJ/t (194 kWh/t) and 7.3 GJ/t of steam heat (2028 kWh/t) |
| Butadiene to air | US EPA (1996), Table 4-5: facility means of process vents and of the wastewater | 0.016 and 0.468 kg/t |

That gives 2.60 t of crude C4, 1.54 t of raffinate-1 and 59 kg of purge per t of butadiene.

Benchmarks (`benchmarks/olefins.yaml`) compare the electricity and steam with Neelis et al. (2007), which gives 0.90 and 6.43 GJ/t. That study is separate from the IEA paper, though Patel co-authored both. It gives single values, so the dataset is explained, not inside: 22 % lower in electricity and 14 % higher in steam, within the 10 to 30 % uncertainty that Neelis et al. state. The IEA best-practice values (0.5 and 6.7 GJ/t) are recorded too.

## What is weak

- **The crude C4 is one typical cut** from a 1996 document. Real cuts range from about 39 to 44 % butadiene for naphtha (LVOC BREF Table 3.3 gives about 44 % for light naphtha) and US EPA (2025, section 3.1, p. 46) names crude butadiene streams of up to 75 %. The feed and raffinate per t scale with it.
- **The recovery is the licensor's bound.** That all unrecovered butadiene leaves in the purge, and that the purge goes to fuel use, are ASSUMED. As an exported fuel, the purge is a co-product (`docs/system-model.md`, section 2) and takes 2.3 % of the burdens by mass. Where it is burnt, and its CO2 (about 190 kg/t butadiene if burnt completely, our arithmetic), are outside this boundary. A plant that flares it or hydrogenates it selectively would need another model.
- The energy figures do not name the solvent. They are averages from about 2006 (valid_until 2011, lapsed) and gross: no heat export is stated.
- The butadiene emissions are US data of 1984, rated E. The wastewater mean sits on a range of four orders of magnitude.
- Mass allocation between butadiene, raffinate-1 and the purge is a preliminary deviation, since no sourced prices exist (dataset `allocation`).
- Uncertainty is ASSUMED from the spread between sources and Neelis et al.'s stated range.

## Linking

The product has the registry slug `butadiene`, the co-products `c4-raffinate` (raffinate-1) and `c4-acetylenes-purge`, all new. `feed:crude-c4` is not linked: `ethylene-1` makes an ethane-cracker cut of about 80 mol% butadiene, another grade (`lca/mappings.yaml`). It stays a reported gap. The purge is a co-product, so it needs no link. The butadiene emission links to the biosphere flow Butadiene (air, unspecified) through the shared `C4H6` entry in `lci/mappings.yaml`.

## Not counted yet (TODO)

Solvent make-up, cooling water, nitrogen, inhibitor, wastewater volume and its organics, equipment leaks, and the C5+ in real feeds. The full list is in the dataset's `system_boundary.excluded`.
