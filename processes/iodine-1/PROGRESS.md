# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/ | Each `missing:` names the activity to connect; emission:I2 subcompartment non-urban-high-stack (origin noted as core limitation); melter-vent exclusion with an HCl upper bound; `cheme assess lca --write` rerun | review 2026-10-28-pfd-lci-review #2, #8, #5 (partly) |
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, equipment/equipment-list.yaml | Air-ratio check restated as a fresh-water upper bound with I2Cl- named, gated and a 2x sensitivity (D-005, D-007); 90 % recovery labelled as calibrated to SRC-3, not a check; SRC-2 as US Bureau of Mines; SRC-5 pH wording; M-301 design 175 °C; T-202 wetting-rate check; M301 listed as specified | review 2026-10-28-pfd-lci-review #1, #3, #4, #6, #9, #10 |
| 2026-10-28 | lca/mappings.yaml | Override `feed:LPS: use steam-heat` (steam counted as heat delivered, kWh) | PR #233 CI: the library Atlas build mapped the `steam` slug (per kg) to the kWh exchange and refused the unit (tests test_export_formats, test_utilities) |
| 2026-10-28 | lca/ | Preliminary gate-to-gate LCI: lca.yaml (FU 1 kg iodine, backgrounds unmapped with the activity to link), mappings.yaml (no overrides yet), inventory/gaps/dataset written; LCI mass and element balance closed | #145 scope step 4 (D-011) |
| 2026-10-28 | process.yaml, DESIGN.md | Atlas manifest (internal, concept, unreviewed), source register, basis and method tables, D-001..D-012, missing registry entries | #145 scope steps 1, 3, 5 |
| 2026-10-28 | process/, equipment/ | Design basis, materials, reactions, flowsheet (4 blocks, 11 steps, 24 material streams, air-loop and acid recycles), BFD/PFD built, equipment list; all balances close | #145 scope steps 1, 2 (D-001..D-010) |
| 2026-10-28 | all | Scaffold from cheme init and the process template | start of #145 |
