# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-13 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (chlorine to chlor-alkali-1, nitrogen to asu-1, economic shares at ASSUMED relative prices), the Atlas manifest, the public README, D-001 to D-013 with the core features used and limits L-1 to L-8, the folder's tests | concept deliverables (#144) |
| 2026-11-13 | process/flowsheet.yaml, recipe.yaml, scripts/balance.py | the strip at 15 kPa(a) (the still counts the suspended PCl5 in its liquid, at 25 kPa it would end above the hot-water loop); K-201 at a constant reflux of 6; the gases' ideal-gas data so E-102's duty counts their cooling; R102's duty to cooling water (near balance); the chlorine dosed over 8 h (R-101's jacket); vent capacity 350 m3/h; feeds scaled to 500 t/a, batch 1280.5 kg (D-003, D-005, D-007 to D-011) | the recipe, the jacket checks and the screening |
| 2026-11-13 | process/reactions.yaml | DEC's share 0.15, calibrated to the oxalyl chloride in US 4 341 720 A's crude (85.0 %), not to the isolated yield (D-006) | the crude's assay is the measured quantity closest to what the reactions form |
| 2026-11-12 | process/ | materials, reactions and the flowsheet of Bayer's one-pot route: the chlorination R101, the reaction R102 with its vent and vent condenser, the strip ST101, the rectification ST201, the absorber A101, the heel and POCl3 recycles at the tears S3 and S13 (D-001) | the route of US 4 341 720 A, Examples 19 and 20 |
| 2026-11-12 | all | scaffold from cheme init (core 1.11.0) | start of the case |
