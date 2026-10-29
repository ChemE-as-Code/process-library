"""Draft of P-101: natural gas feed, desulphurisation, process steam addition, prereformer.

Provenance only: P-101 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-101.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-027 (front-end P&IDs); streams S1-S9 of process/flowsheet.yaml.
"""

import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (
    Marker,
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

BED = [Marker("COLUMN_PACKED_BED_SHAPE", 0, 0.9)]
VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"

v101 = equipment(sheet, "Vessel", "V-101", shape=VESSEL, at=(180, 145), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (0, -21), 200), Nozzle("N2", (0, 21), 200),
                          Nozzle("N3", (-10, 0), 25)],
                 markers=BED, label_at=(196, 145))
r100 = equipment(sheet, "Vessel", "R-100", shape=VESSEL, at=(310, 145), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (0, -21), 450), Nozzle("N2", (0, 21), 450),
                          Nozzle("N3", (-10, 0), 25)],
                 markers=BED, label_at=(326, 145))

# NG-1001: natural gas from the battery limit (S1), fuel split (S2), process gas to E-101 (S3)
split = tee("T1001", at=(130, 35), branch="down", branch_dn=80)
fv1002 = valve("FV1002", "GlobeValve", tag="FV-1002", at=(250, 35))
xv1001 = valve("XV1001", "BallValve", tag="XV-1001", at=(85, 35))
line(sheet, "NG-1001", dn=150, fluid="Natural gas", route=[
    offpage("in", at=(15, 35), note="from battery limit"),
    valve("HV1001", "GateValve", tag="HV-1001", at=(40, 35)),
    xv1001,
    split,
    fv1002,
    offpage("out", at=(400, 35), note="to E-101, P-102"),
])
line(sheet, "FG-1002", dn=80, fluid="Fuel gas", route=[
    split.branch, (130, 57),
    offpage("out", at=(400, 57), note="to H-101 burners, P-102"),
])
# NG-1003: preheated gas from E-101 (S4) to the desulphuriser
line(sheet, "NG-1003", dn=200, fluid="Natural gas", route=[
    offpage("in", at=(400, 80), note="from E-101, P-102", rotation=180),
    (180, 80), v101["N1"],
])
# NG-1004: desulphurised gas (S5), steam added at T1004, mixed feed to E-102 (S7)
mix = tee("T1004", at=(230, 205), branch="down", branch_dn=300)
line(sheet, "NG-1004", dn=200, fluid="Natural gas", route=[
    v101["N2"], (180, 205), mix,
    offpage("out", at=(400, 205), note="to E-102, P-102"),
], label_at=(300, 196.5))
# NG-1004 is DN 400 (the mixed feed, segment S2) with S1 (V-101 to T1004) DN 200: the line
# builder takes one DN per line, so after this script `cheme set` gives Line_NG1004 and
# Line_NG1004_S2, T1004_N2 DN 400 (D-027)
note(sheet, "DN 200", at=(184, 185))
fv1006 = valve("FV1006", "GlobeValve", tag="FV-1006", at=(120, 240))
line(sheet, "SM-1005", dn=300, fluid="MP steam", route=[
    offpage("in", at=(15, 240), note="from U-801 (MP steam)"),
    valve("HV1005", "GateValve", tag="HV-1005", at=(40, 240)),
    fv1006,
    valve("CV1005", "SwingCheckValve", at=(180, 240)),
    (230, 240), mix.branch,
])
# PG-1006: prereformer feed from E-102 (S8); PG-1007: prereformer outlet to E-103 (S9)
line(sheet, "PG-1006", dn=450, fluid="Process gas", route=[
    offpage("in", at=(400, 105), note="from E-102, P-102", rotation=180),
    (310, 105), r100["N1"],
])
line(sheet, "PG-1007", dn=450, fluid="Process gas", route=[
    r100["N2"], (310, 180),
    offpage("out", at=(400, 180), note="to E-103, P-102"),
])

# Instruments
instrument(sheet, "PI-1001", at=(60, 18), sensing="Line_NG1001_S1", sensing_at=(60, 35))
instrument(sheet, "US-1001", at=(85, 18), signal_to=xv1001)
instrument(sheet, "FIC-1002", at=(250, 18), sensing="Line_NG1001_S2", sensing_at=(225, 35),
           signal_to=fv1002)
instrument(sheet, "TI-1003", at=(150, 95), sensing="Line_NG1003_S1", sensing_at=(180, 95))
instrument(sheet, "PDI-1004", at=(150, 145), sensing=v101["N3"])
instrument(sheet, "AI-1005", at=(150, 190), sensing="Line_NG1004_S1", sensing_at=(180, 190))
instrument(sheet, "FIC-1006", at=(120, 223), sensing="Line_SM1005_S1", sensing_at=(80, 240),
           signal_to=fv1006)
instrument(sheet, "FZ-1007", at=(205, 223), sensing="Line_SM1005_S1", sensing_at=(205, 240))
instrument(sheet, "TI-1008", at=(280, 120), sensing="Line_PG1006_S1", sensing_at=(310, 115))
instrument(sheet, "PDI-1009", at=(280, 145), sensing=r100["N3"])
instrument(sheet, "TI-1010", at=(280, 172), sensing="Line_PG1007_S1", sensing_at=(310, 172))

note(sheet, "XV-1001: see C&E I-101", at=(20, 70))
note(sheet, "FIC-1006 ratio to FIC-1002 (steam to carbon)", at=(20, 255))
note(sheet, "V-101: hydrogenation and ZnO beds; R-100: Ni catalyst", at=(20, 80))

sheet.save(target)
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
