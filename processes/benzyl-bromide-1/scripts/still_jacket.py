"""C-101's jacket against the stills' constant boil-up (DESIGN.md D-007, core limit L-6).

A hand check, outside the balance: core's still (ADR 0055) boils up at a constant rate whatever
the pot's level; the jacket can only give U x wetted area x (steam - pot). This script repeats
the stills' one Rayleigh stage on Raoult's law (the same Antoine data as cheme process stills,
from materials.yaml), follows the pot's volume (the components' molar volumes, materials.yaml),
the wetted area of C-101 (4 m3, D 1.62 m, a DIN 28011 dished bottom: crown radius D, volume
0.0998 D^3; below the head's brim the wetted area is taken as the spherical cap of radius D) and
boils up at the smaller of the stated boil-up and the jacket's duty. U 300 W/(m2 K), ASSUMED as
R-101's (D-003); LP steam at 421.05 K (SRC-10).

Run from the folder: `uv run python scripts/still_jacket.py` (needs only PyYAML).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import balance as b  # noqa: E402

D = 1.62  # m, C-101 (equipment list, as R-101's 4 m3 at H/D 1.2)
U = 300.0  # W/(m2 K), ASSUMED (D-003)
T_STEAM = 421.05  # K, LP steam 450 kPa(a) (SRC-10)
CYCLE = 7.0456  # h, the recipe's cycle (D-003): kmol/h x CYCLE = kmol a batch
V_HEAD = 0.0998 * D**3  # m3, DIN 28011 dished end


def cap(v: float) -> float:
    """m2: the wetted area of a spherical cap of radius D holding v m3."""
    lo, hi = 0.0, D
    for _ in range(80):
        h = 0.5 * (lo + hi)
        lo, hi = (h, hi) if math.pi * h * h * (3 * D - h) / 3 < v else (lo, h)
    return 2 * math.pi * D * h


def area(v: float) -> float:
    if v <= V_HEAD:
        return cap(v)
    return cap(V_HEAD) + (v - V_HEAD) / (math.pi * D * D / 4) * math.pi * D


def run(comps: dict, moles: dict[str, float], p: float, boilup: float, stop) -> dict:
    """One Rayleigh stage to `stop(x)`; hours at the constant boil-up and jacket-limited."""
    n = {k: v for k, v in moles.items() if v > 0 and k != "HBR"}
    step, t_const, t_jacket, q_end = 5e-4, 0.0, 0.0, 0.0
    while True:
        total = sum(n.values())
        x = {k: v / total for k, v in n.items()}
        if stop(x):
            break
        t = b.bubble(comps, n, p)
        ps = {k: x[k] * b.p_sat(comps, k, t) for k in n}
        y = {k: v / sum(ps.values()) for k, v in ps.items()}
        volume = sum(v * comps[k]["liquid_molar_volume"] for k, v in n.items())
        q_end = U * area(volume) * (T_STEAM - t) / 1000.0
        energy = step * sum(y[k] * comps[k]["heat_of_vaporization"] for k in n) / 3600.0  # kWh
        t_const += energy / boilup
        t_jacket += energy / min(boilup, q_end)
        for k in n:
            n[k] -= y[k] * step
    volume = sum(v * comps[k]["liquid_molar_volume"] for k, v in n.items())
    mass = sum(v * comps[k]["molar_mass"] for k, v in n.items())
    return {"moles": n, "h_const": t_const, "h_jacket": t_jacket, "volume": volume,
            "mass": mass, "area": area(volume), "q_end": q_end}


def main() -> None:
    streams, comps, _ = b.load()
    s6 = {k: v * CYCLE for k, v in b.kmol(streams, comps, "S6").items()}
    strip = run(comps, s6, b.P_STRIP, 150.0, lambda x: x["TOL"] < 0.15)
    state = {"cut": "forerun"}

    def st102_stop(x: dict) -> bool:
        if state["cut"] == "forerun" and x["TOL"] < 0.002:
            state["cut"] = "main"
        return state["cut"] == "main" and x["BNBR"] < 0.35

    vac = run(comps, strip["moles"], b.P_VAC, 80.0, st102_stop)
    print(f"dished bottom of C-101 holds {V_HEAD:.3f} m3")
    for name, r, q in (("ST101", strip, 150.0), ("ST102", vac, 80.0)):
        print(f"{name}: {r['h_const']:.2f} h at {q:.0f} kW, {r['h_jacket']:.2f} h jacket-limited; "
              f"end {r['mass']:.1f} kg, {r['volume']:.4f} m3, wetted {r['area']:.2f} m2, "
              f"jacket {r['q_end']:.1f} kW")
    extra = strip["h_jacket"] - strip["h_const"] + vac["h_jacket"] - vac["h_const"]
    print(f"C-101 longer by {extra:.2f} h a batch")


if __name__ == "__main__":
    main()
