# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | process.yaml, lca/, shared files, tests | Atlas manifest (public, CC-BY-4.0, concept, unreviewed); preliminary gate-to-gate LCI per kg of aspirin with nitrogen per batch, acetic anhydride, sulfuric acid and nitrogen linked to acetic-anhydride-1, sulfuric-acid-1 and asu-1, salicylic acid a gap with its Kolbe-Schmitt proxy recorded, economic allocation with the recovered acetic acid; registry entries acetylsalicylic-acid and salicylic-acid; coverage rank 121 (provisional), REFERENCE.md and docs/coverage.md rows; tests/test_acetylsalicylic_acid_1.py recomputing the hand duties, mixing temperatures, the yield, the allocation and the stated numbers | issue #476 scope |
| 2026-11-19 | DESIGN.md, README.md | source register SRC-1..SRC-9 (US 2 731 492 A, US 2 987 539 A, US 6 278 014 B1 read; NIST WebBook, the chemicals package, PubChem), decisions D-001..D-013 with the route's rejected alternatives, the thermal screening with k/10 and k/100 and the all-in batch, the core features used and the core limits L-1..L-8 | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-19 | process/, equipment/ | design basis, materials, reaction (heat by Hess's law on NIST data), flowsheet (3 blocks, 14 steps) with a dosed semi-batch, crystallizers with spectators, Ruth filters, a dryer, a vacuum batch still and two recycle tears; batch recipe (1710.65 kg a batch, cycle 11.57 h, 684.8 batches/a), vessels and R-101's jacket; every duty; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of a dosed batch with crystallisation, a filter-dryer and acid recovery on core 1.12.0 |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0) | start of the case |
