# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-05 | process.yaml, lca/, library registries | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision in its own change, CONTRIBUTING); preliminary gate-to-gate LCI per kg benzoyl chloride, the nitrogen per batch linked to asu-1, the hydrochloric acid a by-product at shares 1/0, the other backgrounds gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme); chemicals benzoic-acid, benzotrichloride, benzoyl-chloride, zinc-chloride (Zn's IUPAC 2021 abridged atomic weight 65.38 added to scripts/registry.py for it); coverage entry (rank 94, provisional); tests/test_benzoyl_chloride_1.py; benchmarks/chlorinated-organics.yaml (two KPIs) | issue #156 scope |
| 2026-11-05 | DESIGN.md | source register, decisions D-001..D-013, the k/10 and k/100 sensitivity (D-011), the core features used and the core limits hit (L-1..L-9) | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-05 | process/, scripts/balance.py, equipment/ | design basis, materials (NIST Antoine constants for the still), reactions, flowsheet (4 blocks, 6 steps, 20 streams) with the semi-batch R101 and its HCl vent (core ADR 0054), the batch still ST101 (ADR 0055) and the column K101 as a specified split; batch recipe (cycle 4.87 h, 1627 batches/a of 1229.47 kg, R-101 1.6 m3 with its jacket check); BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the batch entry (core 1.8.0) |
| 2026-11-05 | all | scaffold from cheme init (cheme-as-code 1.8.0) | start of the case |
