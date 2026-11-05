# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, shared files | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision); preliminary gate-to-gate LCI per kg acetyl chloride with nitrogen per batch, acetic acid and nitrogen linked to acetic-acid-1 and asu-1, PCl3 a gap with its proxy (P4 + Cl2) recorded, mass allocation to the crude phosphorous acid; registry entries acetyl-chloride, phosphorus-trichloride, phosphorous-acid; coverage rank 107 (provisional; 100-104 reserved for another session); REFERENCE.md and docs/coverage.md rows; benchmarks/chlorinated-organics.yaml with two KPIs (no_open_reference); tests/test_acetyl_chloride_1.py | issue #142 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-013, the rate sensitivity (k/10, k/100), the release cases (water ingress, loss of the scrubber, loss of brine), the core features used and the core limits L-1..L-11 | record the route, the calibration, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, scripts/, equipment/ | design basis, materials, reactions (ACCL, HYD, AHYD), flowsheet (3 blocks, 9 steps, 25 streams) with a vented semi-batch, a calibrated phase split, a batch still with a specified-split column, a vent condenser and a scrubber; scripts/balance.py (feeds, splits, duties, mixed temperatures; balance-output contract); batch recipe (1459.91 kg a batch, cycle 5.781 h, 1370 batches/a), vessel and jacket; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of a dosed, vented, phase-split and distilled batch on core 1.8.0 |
| 2026-11-06 | all | scaffold from cheme init (core 1.8.0) | start of the case |
