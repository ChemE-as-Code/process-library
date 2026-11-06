# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, shared files, tests | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision); preliminary gate-to-gate LCI per kg CuCl with nitrogen and the rinse per batch, chlorine, hydrochloric acid, ethanol and nitrogen linked to chlor-alkali-1, hydrogen-chloride-1, ethanol-1 and asu-1, copper and sodium chloride gaps with their proxies recorded; registry entries copper and copper-i-chloride; coverage rank 104 (provisional); REFERENCE.md and docs/coverage.md rows; benchmarks/inorganic-chemicals.yaml with two KPIs (no_open_reference); tests/test_copper_i_chloride_1.py | issue #143 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-013, the rate sensitivity (k/10, k/100), the core features used and the core limits L-1..L-9 | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, equipment/ | design basis, materials, reactions, flowsheet (3 blocks, 19 steps) with a gas-dosed semi-batch, two recycle tears (the copper heel, the mother liquor), crystallizers with spectators, a settler, Ruth filters and a dryer; batch recipe (355.0 kg a batch, cycle 9.37 h, 846 batches/a), vessels and the jacket; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of a batch precipitation from a chloride liquor on core 1.9.0 |
| 2026-11-06 | all | scaffold copied from p-toluenesulfonyl-chloride-1 (cheme init's files, core 1.9.0) | start of the case |
