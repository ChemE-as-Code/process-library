# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/ (lca.yaml, mappings.yaml, inventory.csv, gaps.csv, dataset.yaml, manifest.json, results.*), process/flowsheet.yaml S08, process.yaml, DESIGN.md D-013 | Preliminary gate-to-gate LCI per kg 50 wt% product, every background unmapped with its target activity; air composition given in mass fractions so the dataset's N and O balances close exactly | Step 4 of issue #170: inventory from the balanced flowsheet; mass and element balances close |
| 2026-10-28 | process/, scripts/hp_balance.py, equipment/, piping/, DESIGN.md, process.yaml, plant.yaml | Design basis, materials, reactions (conversion model), balanced BFD/PFD (5 blocks, 18 steps, 36 material + 11 energy streams), equipment and line lists, decisions D-001..D-013 with the LVOC BREF 2017 source register | Concept stage of issue #170: route, basis and balanced flowsheet; all mass, component and element balances close in cheme |
| 2026-10-28 | (all) | Scaffold from cheme init and the process template | Start of hydrogen-peroxide-1 |
