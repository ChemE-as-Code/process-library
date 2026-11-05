# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-05 | DESIGN.md, process.yaml, flowsheet, equipment list, lca/ | review of #386: HN3 from hydrazine and nitrous acid (hydrazine limit on the recovered methanol S3, purge with the hydrazine oxidised before the azide is destroyed); the still's residue at about 360 K with the caustic liquor's boiling-point elevation (S17, Q6, C-101 on tempered hot water, an open reaction-hazard item); the purge without a chemical slug, an Atlas gap; LCI and sheets regenerated; tests/test_sodium_azide_1.py | the HN3 claim, the still temperature and the purge's Atlas link were wrong |
| 2026-11-05 | process.yaml, lca/, benchmarks | Atlas manifest (concept, unreviewed, `publication.status: internal`); preliminary gate-to-gate LCI per kg NaN3, the five purchased feeds and the nitrogen linked to their library producers, utilities and treatments gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme); KPIs: hydrazine hydrate per kg with the patent's Example 2 range, off-gas with no_open_reference | issue #167 scope |
| 2026-11-05 | DESIGN.md | source register, decisions D-001..D-016 (route, batch basis, charge ratios, assumed kinetics, tear streams, still, precipitation, filter-dryer, jackets, screening with k/10 and k/100, LCI with the N2O item, process-safety notes, recycle and purge), core features used, core limits L-1..L-12, open inputs | record the route, the basis, the hazard result and what core could not do |
| 2026-11-05 | process/, equipment/ | design basis, materials, reactions, flowsheet (4 blocks, 13 steps, 41 streams) with the two vented semi-batches, the batch still, the precipitation with spectators and the filter-dryer, the mother-liquor and methanol recycles converged; batch recipe (cycle 12.14 h, 652.6 batches/a of 1027.6 kg), R-101, R-102 and F-101 sized, jackets checked; BFD/PFD built | balanced concept PFD on core main's batch work-up models (core#165) |
| 2026-11-05 | all | scaffold from cheme init (core main 7334d7c) | start of the case |
