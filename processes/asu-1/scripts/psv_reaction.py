"""Screening reaction forces of the relief valves that discharge to atmosphere (DESIGN.md
D-091 (2); review3#2). No stress analysis is done in this study; this script stands in for the
tailpipe loads. Provenance only; it reads nothing and writes nothing:

    cheme run scripts/psv_reaction.py

Method: the open-discharge reaction force after API 520 Part II (installation of
pressure-relieving devices), in our own form: momentum of the exit flow plus the exit area
times the exit static pressure above atmosphere. Ideal gas, adiabatic tailpipe, friction
neglected (conservative). At a choked exit v* = sqrt(2 k R T / ((k + 1) M)); if the choked exit
pressure would be below atmospheric, the exit is subsonic at atmospheric pressure. Without an
exit bore, W v* (1 + 1/k) bounds the force for any exit area. Every rate, set pressure and
temperature is ASSUMED (see D-091 (2)).
"""

import math

R = 8314.46  # J/(kmol K)
PA = 101325.0  # Pa
K = 1.40  # air, N2, O2 (ASSUMED ideal-gas value)
ID150, ID80 = 0.1627, 0.0847  # DN150 / DN80 schedule 10S bores, m (ASSUMED)
ID250 = 0.2646  # DN250 schedule 10S bore, m (ASSUMED): the upsized tailpipe of D-091 (5)
SET_BARG = {"PSV-3114": 3.5, "PSV-3116": 7.0}  # set = design pressure (equipment list)


def force(w_kgh: float, t: float, m: float, d_exit: float | None = None) -> tuple[float, float, str]:
    """(force N, exit velocity m/s, exit state) for w_kgh at stagnation temperature t (K)."""
    w = w_kgh / 3600
    ts = 2 * t / (K + 1)
    vs = math.sqrt(K * R * ts / m)
    if d_exit is None:
        return w * vs * (1 + 1 / K), vs, "bound"
    area = math.pi / 4 * d_exit**2
    ps = w / area * math.sqrt(R * ts / (K * m))
    if ps >= PA:
        return w * vs + area * (ps - PA), vs, f"choked, {ps / 1e5:.2f} bara"
    cp = K / (K - 1) * R / m
    lo, hi = 0.0, vs
    for _ in range(200):
        v = (lo + hi) / 2
        if PA * m / (R * (t - v * v / (2 * cp))) * v * area < w:
            lo = v
        else:
            hi = v
    return w * v, v, "subsonic, 1.01 bara"


def bore_flow(p1: float, t: float, m: float, d: float) -> float:
    """Mass flow (kg/h) through a bore d at p1 (Pa), t (K) from the choked-flow formula. At the
    tank relief pressure (1.563 / 1.013 = 1.54, below the critical ratio ~1.89 for k = 1.4) the
    flow is subcritical, so this is an upper bound on what the bore can pass (conservative)."""
    g = p1 * math.sqrt(K * m / (R * t)) * (2 / (K + 1)) ** ((K + 1) / (2 * (K - 1)))
    return g * math.pi / 4 * d**2 * 3600


# tag, rate kg/h, relieving bara, (cold K, warm K), molar mass, exit bore
CASES = [
    ("PSV-3114", 76560, 4.86, (94, 288), 28.33, ID150),
    ("PSV-3116", 110870, 8.71, (103, 288), 28.01, ID150),
    ("PSV-4123", round(bore_flow(1.563e5, 95, 32.0, ID80), -2), 1.563, (95, 288), 32.0, ID80),
    ("PSV-4124", round(bore_flow(1.563e5, 82, 28.01, ID80), -2), 1.563, (82, 288), 28.01, ID80),
]
BOUNDS = [
    ("PSV-1109", 111720, 313, 28.96),
    ("PSV-2108A/B", 111080, 288, 28.96),
    ("PSV-3119", 14870, 333, 28.96),
    ("PSV-4127", 20860, 288, 32.0),
    ("PSV-4128", 12510, 288, 28.01),
]

if __name__ == "__main__":
    for tag, w, p1, temps, m, d in CASES:
        for t in temps:
            f, v, state = force(w, t, m, d)
            print(f"{tag}: {w:,.0f} kg/h, {p1} bara, {t} K, exit {d * 1000:.1f} mm: "
                  f"v {v:.0f} m/s, {state}, F {f / 1000:.2f} kN")
    # built-up back pressure at the exit as a share of set (D-091 (5)): DN150 as modelled and
    # DN250 upsized; a conventional valve tolerates about 10 % (exit pressure only, the friction
    # of the tailpipe adds to it)
    for tag, w, p1, temps, m, _ in CASES[:2]:
        for d in (ID150, ID250):
            for t in temps:
                f, _, state = force(w, t, m, d)
                pe = float(state.split(", ")[1].split()[0])
                bp = max(pe - PA / 1e5, 0.0)
                print(f"{tag} back pressure, exit {d * 1000:.1f} mm, {t} K: {bp:.2f} barg, "
                      f"{bp / SET_BARG[tag] * 100:.0f} % of set {SET_BARG[tag]} barg, F {f / 1000:.2f} kN")
    for tag, w, t, m in BOUNDS:
        f, v, _ = force(w, t, m)
        print(f"{tag}: {w:,} kg/h, {t} K: v* {v:.0f} m/s, F <= {f / 1000:.2f} kN (any exit area)")
