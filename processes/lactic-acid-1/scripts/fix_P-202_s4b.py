"""P-202 stage S4b fixes to the S4 review (provenance script, run once; the XML is the source).

    cheme run scripts/fix_P-202_s4b.py pid/P-202.xml

Prints the valve tags (S4#1), draws PCV-2042A as a self-acting regulator with its impulse line
downstream, adds the burst indicator XA-2045A of PSE-2045A (S4#5), labels the split-range
outputs of TIC-2011A (S4#6) and PSV-2046A (S4#7), and names the agitator drive and the half-pipe
coils (S4#2, S4#3). The drive (motor, gearbox, shaft, seal) and the coil outline are drawing-only
polylines added by hand after the run, with the motor shape this script puts in the catalogue
(D-033).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Sheet, instrument, label, note

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-202.xml")
sheet = Sheet.load(target)

# ---- Valve tags (S4#1) ----
for valve_id, at in [
    ("SM_SB1", (95, 77)), ("SM_SB2", (131, 77)),                 # XV-2033A, XV-2034A
    ("TW_TV2011A", (47, 143)), ("TW_TV2011B", (24, 162)),
    ("VT_PV2041A", (318, 39)), ("VT_XV2043A", (272, 62)), ("VT_XV2044A", (263, 57)),
    ("ML_AV2021A", (345, 180)), ("NS_PSV2046A", (341, 135)),
]:
    label(sheet, valve_id, "PipingComponentNumber", at=at, id=f"{valve_id}_TagLabel")

# ---- PCV-2042A: self-acting N2 make-up, impulse line from downstream (S4#1, D-031) ----
instrument(sheet, "PCV-2042A", at=(366, 113), sensing="Line_50NS2025A_S1", sensing_at=(348, 124),
           signal_to="NS_PCV2042A", location="field")
note(sheet, "self-acting, impulse", at=(376, 112), size=2.0)
note(sheet, "line downstream", at=(376, 115), size=2.0)

# ---- PSE-2045A burst indication (S4#5) ----
instrument(sheet, "XA-2045A", at=(256, 90), sensing="VT_PSE2045A")

# ---- Split-range outputs of TIC-2011A (S4#6) and PSV-2046A (S4#7) ----
note(sheet, "TV-2011A: 50-100 % (CW)", at=(63, 152), size=2.0)
note(sheet, "TV-2011B: 0-50 % (LP steam)", at=(63, 159.5), size=2.0)
note(sheet, "vacuum relief -0.2 barg", at=(334, 139.5), size=2.0)

# ---- Agitator drive and coils (S4#2, S4#3) ----
sheet.use_shape("MOTOR_SHAPE")
note(sheet, "G", at=(208, 43.5), size=2.0, align="CenterCenter")
note(sheet, "S", at=(212.5, 52), size=2.0, align="CenterCenter")
note(sheet, "A-201A top entry: motor M 160 kW,", at=(164, 84), size=2.0)
note(sheet, "gearbox G, double mechanical seal S", at=(164, 88), size=2.0)
note(sheet, "with sterile barrier above headspace p.", at=(164, 92), size=2.0)
note(sheet, "Half-pipe coils (TW side)", at=(164, 180), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
