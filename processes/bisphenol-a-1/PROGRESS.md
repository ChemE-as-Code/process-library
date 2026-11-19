# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md | preliminary gate-to-gate LCI (phenol and acetone linked to acetone-1, LP and HP steam as heat delivered, the tar a gap, the EU risk assessment's site releases recorded as emission exclusions), the Atlas manifest (public, CC-BY-4.0), the public README, SRC-1 to SRC-9, D-001 to D-014, core features and limits L-1 to L-4 | concept deliverables (#510) |
| 2026-11-19 | equipment/equipment-list.yaml, process/design-basis.yaml | design basis and the equipment of the PFD's steps with first sizes (R-101 and X-201 from US 6 960 697 B2's space times) and duties | concept deliverables (#510) |
| 2026-11-19 | process/materials.yaml, reactions.yaml, flowsheet.yaml, simulation.yaml, BFD.xml, PFD.xml | seven components with liquid heat capacities (the adduct a solid solvate), five reactions, a 5-block / 17-step PFD: phenol polishing, three resin beds (conversion step, core's duty), water dosing, vacuum flash and core's adduct crystallizer with its energy balance, core's filter with a phenol displacement wash, mother-liquor isomerisation and purge to a cracking still, condensate column, adduct melter (core's duty) and phenol stripper; the recycle at two tears with three design specifications (rate, ratio, wash); the water dose set by hand so that the evaporation's latent heat matches the crystallizer's duty (D-007) | the resin route of US 4 391 997 A and US 5 723 688 A (D-001 to D-011) |
| 2026-11-19 | checks/checks.yaml | the assumptions gate's command as in the library's other entries (`grep`, no `python` on the PATH) | the scaffold's command fails with exit 127 where no `python` is on the PATH |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0) | start of the case (#510) |
