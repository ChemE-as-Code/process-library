# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, library registries | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision in its own change, CONTRIBUTING); preliminary gate-to-gate LCI per kg benzyl bromide, the bromine linked to bromine-1, the toluene to btx-1, the nitrogen per batch to asu-1, the hydrobromic acid a co-product by mass of its HBr (shares 0.6556/0.3444), the other backgrounds gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme); chemical benzyl-bromide; coverage entry (rank 106, provisional: ranks 100-105 are reserved for other sessions); tests/test_benzyl_bromide_1.py; benchmarks/chlorinated-organics.yaml (two KPIs, no open reference) | issue #139 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-013, the k/10 and k/100 sensitivity and the hazards (D-011), the core features used and the core limits hit (L-1..L-9) | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, scripts/balance.py, equipment/ | design basis, materials (NIST Antoine constants for the stills), reactions (two series brominations with ASSUMED effective rates), flowsheet (3 blocks, 10 steps, 32 streams) with the semi-batch R101 and its HBr vent (core ADR 0054), the stills ST101 and ST102 with cuts (ADR 0055) and the toluene recycle at its fixed point; batch recipe (cycle 7.05 h, 1124 batches/a of 889.6 kg, R-101 4 m3 with its jacket check); BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the batch entry (core 1.8.0) |
| 2026-11-06 | all | scaffold copied from benzoyl-chloride-1 (cheme init files of cheme-as-code 1.8.0), its content replaced | start of the case |
