# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, shared files | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision); preliminary gate-to-gate LCI per kg Boc2O with nitrogen per batch, phosgene, caustic and nitrogen linked to phosgene-1, chlor-alkali-1 and asu-1, potassium tert-butoxide (proxy tert-butanol + potassium recorded; tert-butanol-1 to be linked when it lands), hexane, DABCO, CO2 and the paraffin gaps; registry entries di-tert-butyl-dicarbonate, potassium-tert-butoxide, n-hexane, triethylenediamine, white-mineral-oil; coverage rank 104 (provisional); REFERENCE.md and docs/coverage.md rows; benchmarks/oxygenates.yaml with two KPIs (no_open_reference); tests/test_di_tert_butyl_dicarbonate_1.py | issue #160 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-014, the rate sensitivity (k/10, k/100) with the gas release over the batch, water ingress and the loss of the scrubber, the core features used and the core limits L-1..L-14 | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, scripts/, equipment/ | design basis, materials, reactions, flowsheet (5 blocks, 18 steps) with one semi-batch with two gas doses and a CO2 vent, a degassing still, two hexane strips, a vacuum still with cuts, two recycles at tears (hexane, paraffin heel); scripts/balance.py for the wash and vent splits and the duties the models leave out (ADR 0027 contract); batch recipe (657.28 kg a batch, cycle 10.41 h, 760.7 batches/a), R-101's vessel and jacket; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of a gas-dosed, gas-evolving batch with batch work-up on core 1.9.0 |
| 2026-11-06 | all | scaffold as the other batch entries (core 1.9.0) | start of the case |
