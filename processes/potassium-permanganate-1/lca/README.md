# LCA of potassium-permanganate-1

Preliminary gate-to-gate (foreground) life cycle inventory per 1 kg of dried technical-grade
KMnO4 at the dryer outlet (DESIGN.md D-011). Every exchange comes from the balanced flowsheet
(`process/flowsheet.yaml`, stream or energy-stream id in `inventory.csv`); every background is
declared `missing:` with the activity it should connect to, so it is a reported gap, never 0.

| file | what | written by |
|---|---|---|
| `lca.yaml` | goal and scope, functional unit, allocation (none), every flow with its background description and provenance, emission exclusions | people (this run) |
| `factors.yaml` | the packaged open screening profile `desnz-ghg-2026`; no project factor | `cheme init` |
| `mappings.yaml` | this process's overrides for the Atlas LCI build (utility unit conventions only; raw materials and wastes unmapped on purpose) | people (this run) |
| `inventory.csv`, `results.csv`, `results.md`, `gaps.csv`, `uncertainty.csv`, `dataset.yaml`, `manifest.json` | generated | `cheme assess lca --write` |

Mass check (per kg product, from `inventory.csv`): inputs 3.9295 kg (ore 0.7874, KOH solution
0.9197, air 0.8769, lime 0.0320, water 1.3135) = outputs 3.9295 kg (product 1, residue 0.3902,
purge 0.7035, roaster off-gas 1.7669, H2 0.0080, O2 0.0095, dryer vapour 0.0516); the flowsheet
gives 4911.9 kg/h in and out for 1250 kg/h product, the same ratio. `cheme assess lca
--coverage`: mass, element and carbon-origin balances closed.

Open: backgrounds for ore, KOH, lime, residue landfill and Mn effluent treatment; dust of the
roaster off-gas and the dryer exhaust (not estimated, no dust method in the schema); H2 to air
has no GWP100 factor; CPC classification not looked up.
