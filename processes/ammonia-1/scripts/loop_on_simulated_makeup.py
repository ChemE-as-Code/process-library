"""Synthesis loop and purge recovery of the concept balance on the simulated make-up gas (D-024).

The loop (SYN) and the purge gas recovery (PGR) are not simulated: their DWSIM recycles do not
pass the recycle test of core v1.0.0 (DESIGN.md D-024). Until they do, their values come from
the concept balance's own loop model (scripts/plant_balance.py, `loop`: Peng-Robinson flash
with ChemSep kij, equilibrium converter, HRU recoveries; D-006), solved here on the make-up gas
that `cheme process simulate` wrote to S34, at the flowsheet's purge fraction (SPL501). Nothing
is rescaled to 1500 t/d: the product follows from the simulated front end.

Also prints the gases dissolved in the process condensates (S25, S33, S35) that the steam
system's condensate stripper releases (D-015, D-024).

Run with `cheme run scripts/loop_on_simulated_makeup.py`; it writes nothing.
"""

import sys
from pathlib import Path

import yaml
from scipy.optimize import fsolve

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plant_balance as pb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FS = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())
STREAMS = {s["id"]: s for s in FS["streams"]}
PURGE = next(s for s in FS["steps"] if s["id"] == "SPL501")["split"]["purge"]


def kmol(sid):
    st = STREAMS[sid]["state"]["design"]
    x = st["composition"]["values"]
    mw = sum(v * pb.MW[c] for c, v in x.items())
    n = st["flow"]["value"] / mw
    out = pb.z()
    out.update({c: v * n for c, v in x.items()})
    return out


makeup = kmol("S34")
x0 = [kmol("S39")[c] for c in pb.LOOP] + [kmol("S36")[c] for c in ["H2", "N2", "AR", "CH4"]]
x = fsolve(lambda v: pb.loop(makeup, v, PURGE)[1], x0, xtol=1e-12, maxfev=4000)
s, res, inert = pb.loop(makeup, x, PURGE)
assert max(abs(r) for r in res) < 1e-6, res


def show(name, n, t=None, p=None):
    m = pb.mass(n)
    f = {c: round(v / pb.tot(n), 7) for c, v in n.items() if v > 1e-9}
    extra = f" T {t:.2f} K" if t is not None else ""
    extra += f" P {p:g} kPa" if p is not None else ""
    print(f"{name}: {m:.2f} kg/h{extra} {f}")


print(f"make-up S34 {pb.mass(makeup):.2f} kg/h, purge fraction {PURGE}, inerts at the converter inlet {inert:.4f}")
print(f"H2/N2 at the circulator suction {s['suc']['H2'] / s['suc']['N2']:.4f}")
show("S36 H2-rich gas", s["h2_rec"])
show("S39 warm recycle", s["recycle"], pb.T_REC)
show("S40 suction", s["suc"], s["T_suc"])
show("S42 converter feed", s["suc"], s["T_r501_in"])
show("S43 converter effluent", s["r501"])
print(f"T after E-502 {s['T_e502']:.2f} K, T after E-505 hot {s['T_e505h']:.2f} K, K-502 discharge {s['T_k502']:.2f} K")
show("S49 separator gas", s["v501_vap"])
show("S52 separator liquid", s["v501_liq"])
show("S53 let-down gas", s["v502_gas"], s["T_v502"])
show("S54 let-down liquid", s["v502_liq"], s["T_v502"])
show("S55 vent", s["vent"])
show("S56 flashed liquid", s["v701_liq"])
show("S58 recovered NH3", s["nh3_rec"])
show("S59 tail gas", s["tail"])
prod = pb.add(s["v701_liq"], s["nh3_rec"])
print(f"product NH3 {pb.mass(prod):.2f} kg/h = {pb.mass(prod) * 24 / 1000:.1f} t/d")
T_m601 = pb.t_of_h(s["hru_in"], pb.H(s["purge"], pb.T_SEP) + pb.H(s["v502_gas"], s["T_v502"])
                   + pb.H(s["vent"], pb.T_EVAP_CH), 200, 400)
print(f"S57 HRU feed T {T_m601:.2f} K")
print(f"duties kW: K-501 {s['W_k501']:.1f} (cooling {s['Q_k501']:.1f}), K-502 {s['W_k502']:.1f}, E-502 {s['Q_e502']:.1f}, "
      f"E-503 {s['Q_e503']:.1f}, E-504 {s['Q_e504']:.1f}, E-505 {s['Q_e505']:.1f}")

gas = pb.z()
for sid in ("S25", "S33", "S35"):
    for c, v in kmol(sid).items():
        if c != "H2O":
            gas[c] += v
show("gases dissolved in the process condensates", {c: v for c, v in gas.items() if v > 0})
