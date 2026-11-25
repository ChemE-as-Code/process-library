# MLE pre-denitrification waterline

This generic teaching case uses the EXPOsan 1.5.3 ASM1 CSTR configuration.
Two anoxic tanks and three aerobic tanks feed a secondary clarifier. The final
aerobic tank returns nitrate-bearing mixed liquor to the first anoxic tank.
The clarifier returns activated sludge separately and discharges waste sludge.

See [the design basis](DESIGN.md), [BFD](process/BFD.xml) and [PFD](process/PFD.xml).

## Static checks and simulation

Library CI checks the example's format and static validity. Executing the
example needs the shared worker result contract from core `225c19c` (#325) or a
compatible later core. The configuration
uses QSDsan's default dynamic mode. The worker returns v2 and reports completion
of the requested interval separately from steady-state assessment.
The worker has a 600-second wall-clock allowance for slower machines.

Use Python 3.12 and install `requirements.lock.txt` into a dedicated environment.
Set `CHEME_QSDSAN_PYTHON` to the absolute path of that environment's Python.
From this process folder, with the compatible core on PATH:

```text
cheme fmt --check
cheme validate
cheme process simulate --fill
cheme process build
cheme validate
cheme process streams --json
python verify_baseline.py
```

The verification script compares the final 50 stream values and units against
[the saved baseline](inputs/reference-streams.json) with `rtol=1e-6` and `atol=1e-8`.
Each run keeps its own ignored evidence folder. Flow, COD, TN, TSS and ammonium
nitrogen appear in the native stream table. ASM1 does not supply TP or phosphate
for this case.

## Review retention time and secondary clarifier loading

Use a core Python environment containing commit `291daae` (core #337) or a
compatible later core. After `cheme process simulate --fill`, run the following
from the example folder with that environment's Python:

```text
python review_design.py
```

The report identifies the saved run and uses its final flow and TSS values, CSTR
liquid volumes, and the clarifier area, depth and modeled TSS profile. Core
calculates HRT, reactor-only and waterline TSS SRT, and secondary clarifier loads.
Incomplete inputs are listed with their deferral reasons. The report reads
`design-snapshot.json` from the evidence folder referenced by the current
`process/simulation-run.json`. It checks the input fingerprints and snapshot
digest before calculating. Save its JSON output outside the example if needed.

For a one-factor sensitivity example, copy the process folder, add
`"waste_flow_m3_d": 423.5` to the copy's `inputs/baseline.json`, then rerun
`cheme process simulate --fill` and `python review_design.py` there. This is a
10% increase over the model's default WAS flow of 385 m³/day. Use
`verify_baseline.py` on the default case.

The input assumes constant influent and the published EXPOsan initial conditions.
This case supports software reproduction. Equipment capacity, dynamic wet-weather
performance and calibration to an operating plant require independent evidence.
