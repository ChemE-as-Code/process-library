# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | process/flowsheet.yaml, simulation.yaml, design-basis.yaml, materials.yaml, reactions.yaml, BFD.xml, PFD.xml, equipment-list.yaml, lca/*, DESIGN.md, README.md, process.yaml | Review fixes on PR #502: MP steam 1600 kPa(a) for the cascade, C-201 and C-202 (LP steam was below or within 4 K of them); coolers Q15-Q19 (neutraliser, separator feed, brine, MDA solution, cascade reflux condenser) and the absorbent chiller in Q8; R-102 held at 388 K, not adiabatic; S22 at SRC-3's 318 K; Q6 from SRC-3's 81 C reaction solution; reaction heats sized (L-1 corrected); HCl gas saturated with MCB (740 ppmv), make-up 34.6 kg/h; SRC-3 locator (temperatures, second column, 430 t/a); property methods named; column tags D- to C-; product class chemicals; Atlas gaps stated | Review of PR #502 (17 findings) |
| 2026-11-19 | DESIGN.md, process.yaml, README.md, PROGRESS.md | Source register SRC-1..SRC-8, decisions D-001..D-012, core limits L-1..L-4, Atlas manifest (public, CC-BY-4.0, concept, unreviewed) | Document the concept stage of issue #465 |
| 2026-11-19 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml, manifest.json, results.md | Preliminary gate-to-gate LCI per kg of monomeric MDI, mass allocation with polymeric MDI and HCl gas; aniline, formalin, caustic soda and phosgene linked to their library producers, the rest gaps | D-012 |
| 2026-11-19 | process/materials.yaml, reactions.yaml, flowsheet.yaml, simulation.yaml, design-basis.yaml, BFD.xml, PFD.xml, equipment-list.yaml, plant.yaml | Design basis, 13 components, five reactions, 4-block / 19-step PFD, five tears and seven design specifications converged by cheme process propagate --fill, ASSUMED duties with their arithmetic, equipment list | D-001..D-011 |
| 2026-11-19 | all | Scaffold from cheme init (cheme-as-code 1.12.0) | Start of mdi-1 |
