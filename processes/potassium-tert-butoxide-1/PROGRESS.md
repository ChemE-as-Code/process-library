# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, shared files, di-tert-butyl-dicarbonate-1 | Atlas manifest (public, CC-BY-4.0, concept, unreviewed); preliminary gate-to-gate LCI per kg KOtBu with nitrogen per batch, the make-up's tert-butanol linked to tert-butanol-1 (kg contained), nitrogen to asu-1, potassium metal a gap with its proxy (KCl + Na) recorded, the hydrogen flared without credit; registry entry potassium; coverage rank 111 (provisional); REFERENCE.md and docs/coverage.md rows; benchmarks/oxygenates.yaml with two KPIs (no_open_reference); tests/test_potassium_tert_butoxide_1.py; di-tert-butyl-dicarbonate-1's feed:KOTBU linked to this product kg for kg (D-014) | issue #418 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-014, the rate sensitivity (k/10, k/100), the hazards of hydrogen and of potassium with water, the core features used and the core limits L-1..L-12 | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, equipment/, scripts/ | design basis, materials, reactions, flowsheet (4 blocks, 15 steps) with a vented semi-batch with vent vapour and condenser, a batch still with heat-up and metal, a dryer, the alcohol recycle at a tear and the make-up's sieve dehydration (scripts/makeup_drying.py, balance-output contract); batch recipe (831.6 kg a batch, cycle 6.586 h, 1202 batches/a), vessels and jacket; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD on core 1.10.0 |
| 2026-11-06 | all | scaffold from cheme init (core 1.10.0) | start of the case |
