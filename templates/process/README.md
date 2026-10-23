# <Process title>

`process.yaml` is all the Atlas needs: copy this folder to `processes/<id>/`, fill in the
manifest, add any new chemicals to `chemicals/chemicals.yaml`, and the catalog and the Atlas pick
the process up without any change to the site.

Optional, as the process matures:

| add | the Atlas then shows |
|---|---|
| `plant.yaml` and the plantcode project files (`plantcode init`) | the process is an engineering project: sheets, gates, design basis |
| `pid/*.xml`, `process/BFD.xml`, `process/PFD.xml` (listed in `plant.yaml`) | drawing previews, later the interactive Viewer |
| `process/flowsheet.yaml` | flowsheet and stream table |
| `layout/plant-model.yaml` | 3D layout (in the Viewer) |
| `lca/` with results (`plantcode assess lca --write`) | footprint per functional unit, contributions, inventory |
| `checks/status.json` | engineering gate status |

Keep sources and assumptions with the data. The `maturity` and `validation` fields are what tell
a reader whether this is a research concept or a reviewed design.
