"""Screening empty weights of the hda-1 equipment for the lifting study (S5, D-027).

The lifting rule of the 3D layout needs a crane for every item of 5 t or more, so every item
that could reach 5 t needs an empty `weight` in equipment/equipment-list.yaml. No datasheet
gives a weight yet (S7), so this script estimates them from the list dimensions and design
pressures. Every result is ASSUMED, a screening value for crane and laydown planning, to be
replaced by the vendors' weights.

Method (each rule an ASSUMED screening choice of this design):
- pressure shells (vessels, columns, exchanger shells): cylindrical shell thickness from the
  thin-wall hoop-stress formula t = P R / (S E - 0.6 P) + c, S 138 MPa (carbon steel plate at
  moderate temperature, ASSUMED), joint efficiency E 0.85, corrosion allowance c 3 mm, at least
  8 mm (handling minimum, ASSUMED); vacuum service at least 10 mm (stiffening not designed);
  two 2:1 ellipsoidal heads taken as 1.1 x the disc area of the diameter each; steel 7850 kg/m3;
- nozzles, manways, supports and attachments: + 15 % of the shell and heads;
- columns: trays at 60 kg per m2 of column cross-section (a light valve tray with its support
  ring, ASSUMED) at a 0.6 m tray spacing over the height, plus a skirt of 2 m at the shell
  thickness;
- R-101: 150 mm castable refractory lining at 2100 kg/m3 on the shell (the reactor is empty,
  thermal, D-021; lining ASSUMED, as in the uncovered allowance of D-019);
- shell-and-tube exchangers: 2.5 x the shell and heads (tube bundle, tube sheets, channel),
  ASSUMED; E-101 is two shells (D-024), each weighed alone (the heaviest single lift);
- machines and packages, no shell: weight per footprint area of the list dimensions, ASSUMED
  (centrifugal compressor train with motor on a common base 1.0 t/m2; reciprocating compressor
  train 1.0 t/m2; PSA package 0.5 t/m2 per lift, the adsorbers set one by one; fired heater
  H-101 by its coil and casing, see below; pumps under 1 t, not computed).
- H-101: a vertical cylindrical heater of 4 m x 14 m: casing 6 mm plate, refractory 100 mm at
  1000 kg/m3 (ceramic fibre and castable mix, ASSUMED), coil 30 % of the casing and lining,
  stack excluded (set separately). ASSUMED.

Run: python scripts/s5_weights.py (no extra packages). Prints the weight per item in tonnes.
"""

import math

S = 138e6  # Pa, allowable stress, ASSUMED
E = 0.85
C = 0.003
RHO = 7850.0


def shell_thickness(p_barg: float, d: float, vacuum: bool = False) -> float:
    p = max(p_barg, 0.0) * 1e5
    t = p * (d / 2) / (S * E - 0.6 * p) + C
    return max(t, 0.010 if vacuum else 0.008)


def shell_and_heads(d: float, length: float, t: float) -> float:
    cyl = math.pi * d * length * t * RHO
    heads = 2 * 1.1 * math.pi * (d / 2) ** 2 * t * RHO
    return cyl + heads


def vessel(d, length, p, vacuum=False):
    t = shell_thickness(p, d, vacuum)
    return 1.15 * shell_and_heads(d, length, t), t


def column(d, h, p, vacuum=False):
    m, t = vessel(d, h, p, vacuum)
    trays = int(h / 0.6) * 60.0 * math.pi * (d / 2) ** 2
    skirt = math.pi * d * 2.0 * t * RHO
    return m + trays + skirt, t


def exchanger(d, length, p):
    m, t = vessel(d, length, p)
    return 2.5 * m, t


ITEMS = {
    # tag: (kind, diameter or length, height/length or width, design pressure barg, extra)
    "V-100": ("vessel", 1.8, 3.6, 3.5),
    "R-101": ("reactor", 2.5, 9.0, 42.0),
    "V-101": ("vessel", 1.4, 5.0, 42.0),
    "E-101": ("exchanger", 1.6, 9.0, 42.0),
    "E-102": ("exchanger", 1.1, 7.0, 42.0),
    "E-103": ("exchanger", 0.7, 5.0, 6.0),
    "C-201": ("column", 1.0, 12.5, 9.0),
    "E-201": ("exchanger", 0.5, 4.0, 9.0),
    "E-202": ("exchanger", 0.9, 5.0, 14.0),
    "V-201": ("vessel", 0.6, 1.8, 9.0),
    "C-202": ("column", 2.2, 38.0, 3.5),
    "E-203": ("exchanger", 0.9, 6.0, 3.5),
    "E-204": ("exchanger", 1.2, 7.0, 3.5),
    "V-202": ("vessel", 1.6, 4.0, 3.5),
    "C-203": ("column_vac", 1.4, 14.0, 3.5),
    "E-205": ("exchanger", 0.6, 4.5, 3.5),
    "E-206": ("exchanger", 0.6, 4.0, 3.5),
    "V-203": ("vessel_vac", 1.0, 2.5, 3.5),
    "E-207": ("exchanger", 0.4, 4.0, 10.0),
    "K-101": ("machine", 6.0, 4.0, 1.0),
    "K-102": ("machine", 5.0, 3.0, 1.0),
    "PK-101": ("machine", 10.0, 6.0, 0.5),
    "PK-201": ("machine", 3.0, 2.0, 0.5),
    "H-101": ("heater", 4.0, 14.0, None),
}


def main() -> None:
    for tag, (kind, a, b, p) in ITEMS.items():
        if kind == "vessel":
            m, t = vessel(a, b, p)
        elif kind == "vessel_vac":
            m, t = vessel(a, b, p, vacuum=True)
        elif kind == "column":
            m, t = column(a, b, p)
        elif kind == "column_vac":
            m, t = column(a, b, p, vacuum=True)
        elif kind == "exchanger":
            m, t = exchanger(a, b, p)
        elif kind == "reactor":
            m, t = vessel(a, b, p)
            lining = math.pi * (a - 0.15) * b * 0.15 * 2100.0
            m += lining
        elif kind == "machine":
            m, t = a * b * p * 1000.0, 0.0
        elif kind == "heater":
            casing = math.pi * a * b * 0.006 * RHO
            refr = math.pi * (a - 0.1) * b * 0.10 * 1000.0
            m, t = 1.3 * (casing + refr), 0.006
        print(f"{tag:7s} {kind:11s} t {t * 1000:5.1f} mm  {m / 1000:6.1f} t")


if __name__ == "__main__":
    main()
