"""Screening empty weights of the equipment-list items for the basic layout's lifting study
(D-031). Provenance only: prints the values entered by hand as `dimensions.weight` (and
`lift_weight`) in equipment/equipment-list.yaml; every value is ASSUMED until the datasheets
(S7) and the vendors replace it.

Method (all parameters ASSUMED, chosen in this design, not taken from a source):
- pressure shells (vessels, columns, shell-and-tube exchangers with a diameter): wall
  t = P D / (2 S E - 1.2 P) + c (the thin-wall cylinder formula of the pressure-vessel codes),
  P = 1.1 x the operating gauge pressure of the item's notes (1000 kPa(a) where none is
  given), S = 138 MPa (carbon steel allowable stress), E = 1, c = 3 mm, t >= 8 mm; straight
  shell = overall length - D/2, two 2:1 ellipsoidal heads of 1.09 D^2 each; steel 7.85 t/m3;
  times a factor for what is not shell: vessels and reactors 1.3, columns 1.6, shell-and-tube
  exchangers 2.5 (tube bundle and channel); R-102 adds a 0.2 m refractory lining at 2.3 t/m3;
- machines, packages and furnace parts: envelope volume (length x width x height) x a bulk
  density: compressor trains with motor 0.35 t/m3, fans 0.3, pumps with motor 0.4, plate
  exchanger 0.5, convection coil modules 0.12, reformer tube headers 0.1, dryer package 0.1,
  cold box 0.08, steam-system package 0.06, radiant box (field-erected) 0.05;
- lift_weight (the heaviest single lift where the item is erected in parts): ASSUMED module
  sizes stated per item below.

Run: `cheme run scripts/estimate_weights.py` (or python3; needs PyYAML only).
"""

import math
import re

import yaml

S = 138e6
E = 1.0
C = 0.003
RHO = 7.85
FACTOR = {"Vessel": 1.3, "ProcessColumn": 1.6, "TubularHeatExchanger": 2.5}
DENSITY = {"CentrifugalCompressor": 0.35, "Fan": 0.3, "CentrifugalPump": 0.4, "PlateHeatExchanger": 0.5}
BOX_DENSITY = {  # by tag: furnace parts and packages
    "H-101": 0.05, "R-101": 0.1, "X-401": 0.1, "X-601": 0.08, "U-801": 0.06,
    **{t: 0.12 for t in ("E-101", "E-102", "E-103", "E-104", "E-106", "E-107")},
}
LIFT = {  # heaviest single lift, t (ASSUMED module sizes)
    "H-101": (50.0, "largest prefabricated radiant-box wall or roof module"),
    "R-101": (15.0, "one inlet header with its pigtails"),
    "X-401": (30.0, "one adsorber vessel of the dryer package"),
    "X-601": (60.0, "one cold-box module"),
    "U-801": (60.0, "the steam drum"),
}


def pressure_kpa(notes: str) -> float:
    found = re.findall(r"(\d[\d,]*)\s*kPa\(a\)", notes or "")
    return max(float(f.replace(",", "")) for f in found) if found else 1000.0


def shell_weight(item: dict) -> float:
    d = item["dimensions"]
    dia = d["diameter"]
    length = d.get("height") or d.get("length")
    p = 1.1 * max(pressure_kpa(item.get("notes", "")) - 101.3, 100.0) * 1e3
    t = max(p * dia / (2 * S * E - 1.2 * p) + C, 0.008)
    shell = math.pi * dia * (length - dia / 2) * t * RHO
    heads = 2 * 1.09 * dia**2 * t * RHO
    w = (shell + heads) * FACTOR[item["type"]]
    if item["tag"] == "R-102":
        w += math.pi * (dia - 0.2) * (length - dia / 2) * 0.2 * 2.3
    return w


def main() -> None:
    items = yaml.safe_load(open("equipment/equipment-list.yaml"))["equipment"]
    for item in items:
        d = item.get("dimensions") or {}
        tag = item["tag"]
        if tag in BOX_DENSITY or "diameter" not in d:
            volume = d["length"] * d.get("width", d.get("depth", 0)) * d["height"]
            w = volume * BOX_DENSITY.get(tag, DENSITY.get(item["type"], 0.2))
            how = f"envelope {volume:.0f} m3"
        else:
            w = shell_weight(item)
            how = f"shell at {pressure_kpa(item.get('notes', '')):.0f} kPa(a)"
        lift = LIFT.get(tag)
        extra = f"; lift_weight {lift[0]:.0f} t ({lift[1]})" if lift else ""
        print(f"{tag:8s} {w:7.1f} t  ({how}){extra}")


if __name__ == "__main__":
    main()
