# cheme-as-code-lci

One-call import of the ChemE-as-Code Process Atlas LCI database (a bw2io Excel workbook built by
`scripts/build_lci.py`) into a Brightway 2.5 project, linked to the background databases you
are licensed for. See [`../lci/README.md`](../lci/README.md) for the modelling rules and caveats.

```python
import bw2data as bd
from cheme_as_code_lci import install

bd.projects.set_current("my-project")          # already holds ecoinvent and its biosphere
report = install("cheme-as-code-atlas-0.1.0.xlsx", background="ecoinvent-3.11-cutoff", location="FR")
print(report.summary())                        # every Atlas-to-Atlas link and the supply chains
```

An input that another Atlas process makes links to the Atlas market of its grade (delivered,
with transport and losses); `prefer_atlas="plant"` or `pin=["<activity code>"]` links it to the
plant gate instead, and `prefer_atlas=False` to your background.

The unallocated multi-output datasets (`cheme-as-code-atlas-<version>-multifunctional.json`)
install as a Brightway `multifunctional` database, whose allocation you choose (exergy, mass,
energy, price where stated, the build's share); with each process's default it reproduces the
workbook. Needs the extra: `pip install "./python[multifunctional]"`.

```python
from cheme_as_code_lci import install_multifunctional

report = install_multifunctional("lci/", background="ecoinvent-3.11-cutoff", location="FR")
```
