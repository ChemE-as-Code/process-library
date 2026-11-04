"""Labelled cross-section of the reverse-bias BPM CO2 electrolysis cell (#329).

Drawn from the configuration in process/design-basis.yaml (capacity.reference_cell), not
from any figure of the paper. Schematic: layer widths are chosen for legibility, not to
scale. Writes figures/cell-cross-section.svg.

Run from the process folder: cheme run scripts/cell_section.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

W, H = 900, 640
TOP, BOTTOM = 150, 440  # vertical extent of the layers

# Layers left to right: (key, label lines, x0, x1, fill, vertical label)
LAYERS = [
    ("flow_cathode", ["cathode flow field"], 40, 170, "#e8eef5", False),
    ("gdl", ["gas diffusion layer"], 170, 250, "#8c8c8c", True),
    ("catalyst", ["Ag catalyst"], 250, 268, "#c4c4d4", True),
    ("cel", ["CEL"], 268, 318, "#f3c9a6", True),
    ("junction", [], 318, 324, "#8a2e2e", False),
    ("ael", ["AEL"], 324, 374, "#bcd7ea", True),
    ("anode", ["Ni foam anode"], 374, 470, "#d3d3b0", True),
    ("anolyte", ["anolyte channel"], 470, 600, "#dfeef7", False),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, anchor="middle", weight="normal", fill="black"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
            f'fill="{fill}">{esc(s)}</text>')


def arrow(x0, y0, x1, y1, color="black", width=1.6):
    return (f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{width}" '
            f'marker-end="url(#head-{color.strip("#")})"/>')


def path(d, color="black", dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    head = "" if dash else f' marker-end="url(#head-{color.strip("#")})"'
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.2"{extra}{head}/>'


def main() -> None:
    cell = yaml.safe_load((ROOT / "process" / "design-basis.yaml").read_text())["capacity"]["reference_cell"]
    colors = ["black", "#b03030", "#1f5f99", "#2e7d32"]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         'font-family="Helvetica, Arial, sans-serif">', "<defs>"]
    for c in colors:
        p.append(f'<marker id="head-{c.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                 f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    p.append("</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    p.append(text(W / 2, 28, "Reverse-bias bipolar-membrane CO2 electrolysis cell (zero-gap MEA)", 16, weight="bold"))
    p.append(text(W / 2, 48, f"{cell['hardware']}, active area {cell['active_area']}; schematic, not to scale", 12,
                  fill="#444"))

    for key, label, x0, x1, fill, vertical in LAYERS:
        p.append(f'<rect x="{x0}" y="{TOP}" width="{x1 - x0}" height="{BOTTOM - TOP}" fill="{fill}" stroke="#333" '
                 'stroke-width="0.8"/>')
        for line in label:
            if vertical:
                cx = (x0 + x1) / 2 + 4
                p.append(f'<text transform="translate({cx} {BOTTOM - 70}) rotate(-90)" font-size="12" '
                         f'text-anchor="middle">{esc(line)}</text>')
            else:
                p.append(text((x0 + x1) / 2, TOP + 20, line, 12))

    # external circuit, above the layers
    p.append(path(f"M210,{TOP} L210,82 L420,82 L420,{TOP}", "#555", dash="4 3"))
    p.append(text(315, 76, "DC supply: electrons to the cathode", 11, fill="#555"))
    p.append(text(321, TOP - 8, "junction: H2O -> H+ + OH-", 11, fill="#8a2e2e"))

    # water dissociation fluxes from the junction
    y = 205
    p.append(arrow(318, y, 262, y, "#b03030"))
    p.append(text(292, y - 6, "H+", 12, fill="#b03030"))
    p.append(arrow(324, y + 28, 380, y + 28, "#1f5f99"))
    p.append(text(352, y + 22, "OH-", 12, fill="#1f5f99"))
    # co-ion leaks (the WDE loss)
    y = 290
    p.append(arrow(470, y, 270, y, "#2e7d32", 1.3))
    p.append(text(520, y + 4, "K+", 11, fill="#2e7d32"))
    p.append(arrow(262, y + 30, 468, y + 30, "#2e7d32", 1.3))
    p.append(text(535, y + 34, "HCO3- / CO3--", 11, fill="#2e7d32"))
    p.append(text(535, y + 56, "co-ion leaks", 10, fill="#2e7d32"))

    # electrode reactions
    p.append(text(105, TOP + 60, "cathode:", 11, weight="bold"))
    p.append(text(105, TOP + 76, "CO2 + 2 H+ + 2 e-", 10))
    p.append(text(105, TOP + 90, "-> CO + H2O", 10))
    p.append(text(105, TOP + 108, "2 H+ + 2 e- -> H2", 10))
    p.append(text(535, TOP + 60, "anode:", 11, weight="bold"))
    p.append(text(535, TOP + 76, "4 OH- -> O2", 10))
    p.append(text(535, TOP + 90, "+ 2 H2O + 4 e-", 10))

    # brackets below the layers, on two rows
    def bracket(x0, x1, y, label, sub):
        p.append(f'<path d="M{x0},{y - 8} L{x0},{y} L{x1},{y} L{x1},{y - 8}" fill="none" stroke="#333"/>')
        p.append(text((x0 + x1) / 2, y + 16, label, 12, weight="bold"))
        p.append(text((x0 + x1) / 2, y + 30, sub, 11, fill="#444"))

    bracket(170, 268, BOTTOM + 16, "gas-diffusion cathode", cell["cathode"])
    bracket(268, 374, BOTTOM + 66, "bipolar membrane, reverse bias", cell["membrane"].split(" bipolar")[0])

    # cathode gas in and out
    p.append(arrow(105, BOTTOM + 100, 105, BOTTOM + 4))
    p.append(text(105, BOTTOM + 116, "CO2 feed", 11))
    p.append(text(105, BOTTOM + 130, cell["cathode_feed"], 10, fill="#444"))
    p.append(arrow(105, TOP - 4, 105, TOP - 44))
    p.append(text(115, TOP - 30, "CO, H2,", 11, anchor="start"))
    p.append(text(115, TOP - 16, "unreacted CO2", 11, anchor="start"))

    # reservoir and recirculation
    rx0, rx1, ry0, ry1 = 690, 860, 210, 380
    rc = (rx0 + rx1) / 2
    p.append(f'<rect x="{rx0}" y="{ry0}" width="{rx1 - rx0}" height="{ry1 - ry0}" fill="#dfeef7" stroke="#333"/>')
    p.append(text(rc, ry0 + 22, "anolyte reservoir", 12, weight="bold"))
    p.append(text(rc, ry0 + 40, cell["anolyte"]["volume"] + ", " + cell["anolyte"]["composition"], 10))
    p.append(text(rc, ry0 + 56, "recirculated " + cell["anolyte"]["recirculation"], 10))
    for k, line in enumerate(["OH- is consumed at the anode", "and resupplied by the BPM at the", "WDE; the shortfall (1 - WDE)",
                              "lowers the anolyte pH over time"]):
        p.append(text(rc, ry0 + 88 + 14 * k, line, 10, fill="#444"))
    p.append(path(f"M535,{TOP} L535,{TOP - 40} L{rc},{TOP - 40} L{rc},{ry0 - 2}"))
    p.append(text(620, TOP - 46, "anolyte + O2", 11))
    p.append(path(f"M{rc},{ry1} L{rc},{BOTTOM + 70} L535,{BOTTOM + 70} L535,{BOTTOM + 2}"))
    p.append(text(620, BOTTOM + 86, "anolyte return", 11))

    p.append(text(W / 2, H - 28, "Drawn by scripts/cell_section.py from process/design-basis.yaml. Configuration: Prats Vergel "
                  "et al., Nat. Chem. Eng. (2025), Methods.", 10, fill="#555"))
    p.append(text(W / 2, H - 14, "CEL / AEL: cation / anion exchange layer of the bipolar membrane.", 10, fill="#555"))
    p.append("</svg>")
    out = ROOT / "figures" / "cell-cross-section.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(p) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
