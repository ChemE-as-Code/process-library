# <Process title>

`process.yaml` is all the Atlas needs: copy this folder to `processes/<id>/`, fill in the
manifest, add any new chemicals to `chemicals/chemicals.yaml`, and the catalog and the Atlas pick
the process up without any change to the site.

Optional, as the process matures:

| add | the Atlas then shows |
|---|---|
| `plant.yaml` and the ChemE-as-Code project files (`cheme init`) | the process is an engineering project: sheets, gates, design basis |
| `pid/*.xml`, `process/BFD.xml`, `process/PFD.xml` (listed in `plant.yaml`) | drawing previews, later the interactive Viewer |
| `process/flowsheet.yaml` | flowsheet and stream table |
| `layout/plant-model.yaml` | 3D layout (in the Viewer) |
| `lca/` with results (`cheme assess lca --write`) | footprint per functional unit, contributions, inventory |
| `checks/status.json` | engineering gate status |
| `runs/<run-id>/` (one per agent or work session, [docs/run-records.md](../../docs/run-records.md)) | nothing: the effort record stays in git |

Keep sources and assumptions with the data. The `maturity` field (the **design maturity**, a
claim capped by the **calculation maturity** that `cheme maturity` writes to
`checks/maturity.json`) and the `validation` field (the **review status**) are what tell a reader
whether this is a research concept or a reviewed design. The terms follow core's
[glossary](https://github.com/ChemE-as-Code/core/blob/main/docs/concepts/glossary.md).
