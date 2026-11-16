# A2/O wastewater treatment

This example treats a constant wastewater influent in two anaerobic tanks, two anoxic tanks and three aerated tanks. A secondary clarifier separates the effluent and sludge. The model returns settled sludge to the first anaerobic tank and recycles mixed liquor from the last aerobic tank to the first anoxic tank.

The process configuration and inputs come from the ASM2d CSTR branch of EXPOsan 1.5.3. QSDsan 1.5.3 computes the biological reactions. This teaching case has no site measurements or plant calibration. See [source attribution](NOTICE.md) and the [verification record](VERIFICATION.md).

## Run the baseline

Use Python 3.12.13 and `uv`. Place the `core` and `process-library` checkouts side by side. The shared command and wastewater stream columns require the QSDsan integration from [core PR #254](https://github.com/ChemE-as-Code/core/pull/254). If core lives elsewhere, set `CHEME_CORE_PATH` to its checkout. The example locates core's Python in its virtual environment.

To review the two PRs together before the core change is merged, use a fresh checkout of the tested core revision. Run these commands from the parent of your `process-library` clone, in a directory where `core` does not already exist.

```sh
git clone https://github.com/ChemE-as-Code/core.git core
git -C core fetch origin pull/254/head
git -C core switch --detach 5437b17511b05b0b4316d50c1fcbcff131e67056
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

To open the native viewer, build it once with `npm ci` and `npm run build` from `core/viewer` (use `npm.cmd` in PowerShell if needed). Back in this example, run `.venv/Scripts/python.exe run_viewer.py` on Windows or `.venv/bin/python run_viewer.py` on Ubuntu. Choose **Stream table** or click a stream on the PFD. Water flow is in m³/day, COD in mg COD/L, TN and ammonium in mg N/L, TP and orthophosphate in mg P/L, and TSS in mg TSS/L. Historical reports open directly from their saved folders. The optional local launchers use `CHEME_CORE_PATH` to find the core checkout and accept `CHEME_CORE_PYTHON` to override its virtual-environment interpreter.

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
