"""C-101's jacket against the stills' constant boil-up (DESIGN.md D-007, core limit L-6).

A hand check, outside the balance: core's still (ADR 0055) and its column (ADR 0061) boil up at a
constant rate whatever the pot's level; the jacket can only give U x wetted area x (steam - pot).
This script takes the path of each still in C-101 from core's own model (`cheme process stills`:
the share of the charge distilled, the hours and the pot's temperature along it), follows the
pot's volume (the moles left, at a molar volume between the charge's and the residue's, from the
components' molar volumes of materials.yaml), the wetted area of C-101 (4 m3, D 1.62 m, a DIN
28011 dished bottom: crown radius D, volume 0.0998 D^3; below the head's brim the wetted area is
taken as the spherical cap of radius D) and stretches each step of the path where the jacket
gives less than the stated boil-up. U 300 W/(m2 K), ASSUMED as R-101's (D-003); LP steam at
421.05 K (SRC-10).

Run from the folder: `cheme run scripts/still_jacket.py` (core's still model, cheme-as-code 1.10).
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
D = 1.62  # m, C-101 (equipment list, as R-101's 4 m3 at H/D 1.2)
U = 300.0  # W/(m2 K), ASSUMED (D-003)
T_STEAM = 421.05  # K, LP steam 450 kPa(a) (SRC-10)
V_HEAD = 0.0998 * D**3  # m3, DIN 28011 dished end
SUB = 40  # sub-steps per interval of core's profile


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


def molar_volume(comps: dict, x: dict[str, float]) -> float:
    return sum(f * comps[k]["liquid_molar_volume"] for k, f in x.items())


def run(entry: dict, comps: dict, boilup: float) -> dict:
    """Hours at the constant boil-up and jacket-limited, along core's path of one still."""
    sol = entry["solution"]
    n0 = sol["charge"]["kmol_per_batch"]
    v0 = molar_volume(comps, sol["charge"]["mole_fractions"])
    res = sol["residue"]
    v1 = molar_volume(comps, res["mole_fractions"])
    left_end = res["kmol_per_batch"] / n0  # the share of the charge left at the end
    points = sol["profile"]
    t_const = t_jacket = 0.0
    q_end = boilup
    for a, b in zip(points, points[1:]):
        for i in range(SUB):
            f0 = (i + 0.5) / SUB
            share = a["distilled"] + f0 * (b["distilled"] - a["distilled"])
            temp = a["temperature_K"] + f0 * (b["temperature_K"] - a["temperature_K"])
            left = 1.0 - share
            # the molar volume between the charge's and the residue's, by what has left
            w = (1.0 - left) / (1.0 - left_end) if left_end < 1.0 else 0.0
            volume = n0 * left * (v0 + w * (v1 - v0))
            q = U * area(volume) * (T_STEAM - temp) / 1000.0
            dt = (b["time_h"] - a["time_h"]) / SUB
            t_const += dt
            t_jacket += dt * boilup / min(boilup, q)
            q_end = q
    volume = res["kmol_per_batch"] * v1
    return {"h_const": t_const, "h_jacket": t_jacket, "volume": volume, "mass": res["kg_per_batch"],
            "area": area(volume), "q_end": q_end}


def main() -> None:
    from chemeascode.domains.process.batch_still import still_report

    materials = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    boilups = {s["id"]: s["still"]["boilup"]["value"] for s in sheet["steps"] if "still" in s}
    report = still_report(ROOT)
    print(f"dished bottom of C-101 holds {V_HEAD:.3f} m3")
    extra = 0.0
    for entry in report.units:
        name, q = entry["node"], boilups[entry["node"]]
        r = run(entry, comps, q)
        extra += r["h_jacket"] - r["h_const"]
        print(f"{name}: {r['h_const']:.2f} h at {q:.0f} kW, {r['h_jacket']:.2f} h jacket-limited; "
              f"end {r['mass']:.1f} kg, {r['volume']:.4f} m3, wetted {r['area']:.2f} m2, "
              f"jacket {r['q_end']:.1f} kW")
    print(f"C-101 longer by {extra:.2f} h a batch")


if __name__ == "__main__":
    main()
