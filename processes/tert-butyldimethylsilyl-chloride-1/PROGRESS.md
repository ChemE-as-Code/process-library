# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-13 | DESIGN.md, README.md, process.yaml, lca/, tests | source register, core features used, decisions D-001..D-014 (route, capacity, recipe, the order of addition, kinetics, filter-dryer, rectification and flaking, vent, utilities, jackets and heating media, the screening with the k/10, k/100 and uninitiated cases, water ingress, LCI, dedicated train, solvent loop), method table, core limits L-1..L-13; preliminary LCI (THF linked to thf-1, nitrogen to asu-1, the other feeds' proxies named); tests/test_tert_butyldimethylsilyl_chloride_1.py | record the route, the basis, the hazard result and what core could not do |
| 2026-11-12 | process/, equipment/ | design basis, materials, reactions (Grignard formation, disproportionation, silylation), flowsheet: R-101 semi-batch with a vent, its vapour and condenser, R-102 semi-batch with the Grignard solution dosed into the silane, filter-dryer, rectifying still, solvent recycle at its tear S29; batch recipe (cycle 9.86 h, 803.3 batches/a of 721.9 kg, R-101 6.3 m3 and R-102 8 m3 with their jackets checked); BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the batch Grignard route |
| 2026-11-12 | all | scaffold from cheme init (core 1.11.0) | start of the case |
