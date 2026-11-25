# A2/O wastewater treatment

This example treats a constant wastewater influent in two anaerobic tanks, two anoxic tanks and three aerated tanks. A secondary clarifier separates the effluent and sludge. The model returns settled sludge to the first anaerobic tank and recycles mixed liquor from the last aerobic tank to the first anoxic tank.

The process configuration and inputs come from the ASM2d CSTR branch of EXPOsan 1.5.3. QSDsan 1.5.3 computes the biological reactions. This teaching case has no site measurements or plant calibration. See [source attribution](NOTICE.md) and the [verification record](VERIFICATION.md).

## Run the baseline

Use Python 3.12.13 and `uv`. Place the `core` and `process-library` checkouts side by side. The QSDsan integration in [core PR #254](https://github.com/ChemE-as-Code/core/pull/254) supplies the shared command and wastewater stream columns. The design review uses [core PR #337](https://github.com/ChemE-as-Code/core/pull/337). If core lives elsewhere, set `CHEME_CORE_PATH` to its checkout. The example locates core's Python in its virtual environment.

To run the baseline and design review together, use a core checkout at `291daae` or a compatible later version. Run these commands from the parent of your `process-library` clone, in a directory where `core` does not already exist.

```sh
git clone https://github.com/ChemE-as-Code/core.git core
git -C core switch --detach 291daaef46e7a8f4f1af7b7ef8f28f5746c15eca
```

1. From the core checkout, create the command-line environment with `uv sync --locked --python 3.12.13 --no-dev --extra serve`.
2. Open `process-library/processes/wwtp-a2o` in your terminal. Create the separate numerical environment and run the baseline.

**PowerShell**

```powershell
uv venv --python 3.12.13 --prompt WWTP-A2O .venv
uv pip sync --python .venv/Scripts/python.exe requirements.lock.txt
$env:CHEME_QSDSAN_PYTHON = (Resolve-Path .venv/Scripts/python.exe).Path
& ..\..\..\core\.venv\Scripts\cheme.exe process simulate --fill
```

**Ubuntu**

```bash
uv venv --python 3.12.13 --prompt WWTP-A2O .venv
uv pip sync --python .venv/bin/python requirements.lock.txt
export CHEME_QSDSAN_PYTHON="$PWD/.venv/bin/python"
../../../core/.venv/bin/cheme process simulate --fill
```

## Inspect the output

Open the `report.html` path printed by the command for the final effluent, stream results, trajectories and numerical checks. Each fill saves a new directory under `process/simulation-runs/`. Both `--fill` and `--check` execute this repository's worker with your account's permissions using the interpreter you select in `CHEME_QSDSAN_PYTHON`. Run them only on a checkout you trust. Core stages the declared files and discards check-only results. The shared viewer reads the filled project and the record in `process/simulation-run.json`. The BFD groups the biological zones, and the PFD shows the seven tanks and the clarifier.

After a fill, run `cheme process build` with the same core environment to refresh the BFD and PFD fingerprints. The filled flowsheet otherwise makes the saved drawings appear outdated; rebuilding them does not rerun the numerical model.

To open the native viewer, build it once with `npm ci` and `npm run build` from `core/viewer` (use `npm.cmd` in PowerShell if needed). Back in this example, run `.venv/Scripts/python.exe run_viewer.py` on Windows or `.venv/bin/python run_viewer.py` on Ubuntu. Choose **Stream table** or click a stream on the PFD. Water flow is in m³/day, COD in mg COD/L, TN and ammonium in mg N/L, TP and orthophosphate in mg P/L, and TSS in mg TSS/L. Historical reports open directly from their saved folders. The optional local launchers use `CHEME_CORE_PATH` to find the core checkout and accept `CHEME_CORE_PYTHON` to override its virtual-environment interpreter.

The **Liquid flow** column carries the wastewater volume flow; the generic **Flow** column is reserved for mass flow in kg/h. The generic nonreactive mass-balance section remains not evaluable without mass-flow inputs. It does not establish nitrogen or phosphorus conservation for this biological model.

## Review retention time and secondary clarifier loading

After a successful fill, run `python review_design.py` from this example folder using
the same core Python environment. The report identifies the saved run and calculates
nominal HRT, reactor-only and clarifier-inclusive TSS SRT, and secondary clarifier loads.
The worker saves the final outlet flows and TSS, reactor volumes, and C1's modeled
equal-volume TSS layers in `design-snapshot.json`. The read-only review checks the
run's input fingerprints and snapshot digest. When a complete clarifier profile is
unavailable, the core calculation reports which metrics it deferred and why.

For a one-factor sensitivity run, use a separate copy of this example. Set
`recycles.waste_sludge_m3_d` in the copy's `inputs/baseline.json` to `423.5`
for a 10% increase from 385 m³/day. Generate and incorporate the proposed
engineering documents using the steps below before simulating. Run the same design
review on the resulting snapshot. The comparison describes simulated operating
conditions for this teaching example.

## Files

| File | Purpose |
| --- | --- |
| `inputs/baseline.json` | Influent, volumes, recycles, oxygen transfer and solver settings |
| `process/simulation.yaml` | QSDsan worker, input path and timeout for the shared command |
| `process/flowsheet.yaml`, `process/BFD.xml`, `process/PFD.xml` | Process connectivity and generated diagrams |
| `process/simulation-run.json` | Case-specific evidence path and input fingerprints after a fill |
| `wwtp_a2o/` | Model construction, execution, reporting and verification |
| `tests/` | Input, topology, evidence, numerical comparison and environment checks |

For development, sync `requirements-dev.txt` in place of `requirements.lock.txt` and run `python -m pytest -q tests`, `ruff check .` and `ruff format --check .` in the example environment.

## Update the engineering documents

After changing the model layout or its inputs, generate a proposed set of documents in an empty directory with the example Python environment:

```sh
python -m wwtp_a2o.project.prepare --input inputs/baseline.json --output build/proposed-model
```

Review the proposed topology, materials, case inputs and diagrams before incorporating them. The simulation command only fills calculated stream values. The project record identifies the input files, model and evidence for each case.
