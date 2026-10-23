# cheme-as-code-lci

One-call import of the ChemE-as-Code Process Atlas LCI database (a bw2io Excel workbook built by
`scripts/build_lci.py`) into a Brightway 2.5 project, linked to the background databases you
are licensed for. See [`../lci/README.md`](../lci/README.md) for the modelling rules and caveats.

```python
import bw2data as bd
from cheme_as_code_lci import install

bd.projects.set_current("my-project")          # already holds ecoinvent and its biosphere
report = install("cheme-as-code-atlas-0.1.0.xlsx", background="ecoinvent-3.11-cutoff", location="FR")
print(report.summary())
```
