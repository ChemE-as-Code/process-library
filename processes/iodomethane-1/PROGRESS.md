# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | process.yaml, lca/, shared files, tests | Atlas manifest (internal, concept, unreviewed; publication is a maintainer's decision); preliminary gate-to-gate LCI per kg iodomethane with nitrogen, calcium chloride, sieve and activated carbon per batch, methanol, iodine and nitrogen linked to methanol-1, iodine-1 and asu-1, red phosphorus and sodium thiosulfate gaps with their proxies recorded; registry entries sodium-thiosulfate, calcium-chloride; coverage entry (rank provisional); REFERENCE.md and docs/coverage.md rows; two KPIs in benchmarks (no_open_reference); tests/test_iodomethane_1.py | issue #163 scope |
| 2026-11-06 | DESIGN.md | source register, decisions D-001..D-015 (the by-product H3PO3 over the patent's H3PO4, the iodine dosed as a solid instead of through the reflux, red phosphorus as a solid reactant, the MTT at the reflux temperature, the rate sensitivity k/10 and k/100 with the boil-off at the MTT, the release cases, the one-stage purity, the iodine's fate), the core features used and the core limits L-1..L-10 | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-06 | process/, scripts/, equipment/ | design basis, materials, reactions (MEI, THIO), flowsheet (5 blocks, 16 steps, 44 streams) with a semi-batch with a solid reactant and a vent, a still off the residue, a thiosulfate conversion step, specified-split washes and drying, a still with a specified-split column, a vent condenser; scripts/balance.py (balance-output contract); batch recipe (1401.58 kg a batch, cycle 22.201 h, 356.7 batches/a), vessel and jacket; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of a dosed, refluxed and distilled batch on core 1.9.0 |
| 2026-11-06 | all | scaffold copied from acetyl-chloride-1 (cheme init files of core 1.8.0/1.9.0) | start of the case |
