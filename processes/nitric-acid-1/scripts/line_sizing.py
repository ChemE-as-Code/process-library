"""First-pass line sizes for the nitric-acid-1 P&IDs (D-017, ASSUMED).

Run: cheme run scripts/line_sizing.py

For each PFD material stream: the volumetric flow from the design case of
process/flowsheet.yaml (mass flow, pressure, temperature, mole fractions), the inside diameter
at a design velocity, and the next DN up. Gas density as an ideal gas; liquid densities are
round ASSUMED values (not calculated: core has no aqueous HNO3 package, D-012). The inside
diameter is taken as the DN (smallest DN25), as hda-1 does; pipe schedules and pressure
classes come with the pipe specs. Design velocities (ASSUMED, usual first-pass values):
gas 20 m/s below 1000 kPa(a), 15 m/s at or above; liquid 1.5 m/s (pump discharge) and
1.0 m/s (gravity or letdown); the hot burner gas S11 at 30 m/s (refractory-lined duct).
Writes nothing; DESIGN.md D-017 and piping/line-list.yaml quote the result.
"""

import math
from pathlib import Path

import yaml

R = 8.314462618  # J/(mol K)
M = {"NH3": 17.031, "N2": 28.014, "O2": 31.998, "AR": 39.948, "H2O": 18.015, "NO": 30.006,
     "NO2": 46.006, "N2O": 44.013, "HNO3": 63.013}
# ASSUMED liquid densities, kg/m3 (round values for the first pass)
LIQUID = {"S01": 617.0, "S02": 617.0, "S04": 617.0,      # liquid NH3 at 288 K
          "S17": 1260.0, "S18": 1260.0,                   # 42 wt% weak acid at 313 K
          "S24": 996.0,                                   # process water
          "S30": 1360.0, "S31": 1360.0}                   # 60 wt% acid at 313 K
LETDOWN = {"S17", "S30", "S31"}                           # gravity / letdown legs, 1 m/s
DN = [25, 40, 50, 65, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900,
      1000, 1100, 1200, 1400, 1600, 1800, 2000, 2200, 2400]

flowsheet = yaml.safe_load(Path("process/flowsheet.yaml").read_text())
print(f"{'stream':6} {'title':48} {'m3/s':>8} {'v m/s':>6} {'d mm':>7} {'DN':>5}")
for stream in flowsheet["streams"]:
    state = stream.get("state", {}).get("design", {})
    if "flow" not in state:
        continue
    sid = stream["id"]
    flow = state["flow"]["value"] / 3600.0  # kg/s
    if sid in LIQUID:
        rho = LIQUID[sid]
        v = 1.0 if sid in LETDOWN else 1.5
    else:
        comp = state["composition"]
        x = comp["values"]
        if comp.get("basis") == "mass_fraction":
            continue
        mw = sum(M[c] * f for c, f in x.items()) / sum(x.values()) / 1000.0
        p = state["pressure"]["value"] * 1000.0
        t = state["temperature"]["value"]
        rho = p * mw / (R * t)
        v = 30.0 if sid == "S11" else (15.0 if p >= 1.0e6 else 20.0)
    q = flow / rho
    d = math.sqrt(4 * q / (math.pi * v)) * 1000.0
    size = next(n for n in DN if n >= d)
    print(f"{sid:6} {stream['title'][:48]:48} {q:8.3f} {v:6.1f} {d:7.0f} {size:>5}")
