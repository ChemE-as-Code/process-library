"""Draft of P-107: methanator feed heater E-401 (HTS effluent / treated gas), methanator R-401,
effluent cooler E-402, synthesis gas knock-out drum V-401 and the molecular sieve dryer
package X-401.

Provenance only: P-107 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-107.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-028; streams S75, S20, S27, S29-S35 of process/flowsheet.yaml.
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

EDGE = 400
VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
EXCHANGER = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"

# E-401: HTS effluent in the tubes, treated gas in the shell
e401 = equipment(sheet, "TubularHeatExchanger", "E-401", shape=EXCHANGER, at=(90, 150),
                 nozzles=[Nozzle("T1", (-17.5, 0), 600), Nozzle("T2", (17.5, 0), 600),
                          Nozzle("S1", (-7, -7), 350), Nozzle("S2", (7, -7), 500)],
                 label_at=(90, 162))
r401 = equipment(sheet, "Vessel", "R-401", shape=VESSEL, at=(175, 110), scale=(1.0, 1.6),
                 nozzles=[Nozzle("N1", (0, -24), 500), Nozzle("N2", (0, 24), 500),
                          Nozzle("N3", (-10, 0), 25), Nozzle("N4", (10, 8), 25)],
                 markers=[Marker("COLUMN_PACKED_BED_SHAPE", 0, 1.1)], label_at=(197, 100))
e402 = equipment(sheet, "TubularHeatExchanger", "E-402", shape=EXCHANGER, at=(225, 160),
                 nozzles=[Nozzle("T1", (-17.5, 0), 500), Nozzle("T2", (17.5, 0), 350),
                          Nozzle("S1", (-7, 7), 500), Nozzle("S2", (7, 7), 500)],
                 label_at=(225, 149))
v401 = equipment(sheet, "Vessel", "V-401", shape=VESSEL, at=(285, 140), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (-10, -5), 350), Nozzle("N2", (0, -21), 350),
                          Nozzle("N3", (0, 21), 25), Nozzle("N4", (10, -8), 50),
                          Nozzle("N5", (10, 8), 50)],
                 label_at=(268, 118))
x401 = equipment(sheet, "Vessel", "X-401", shape=VESSEL, at=(345, 90), scale=(1.0, 1.6),
                 nozzles=[Nozzle("N1", (0, -24), 350), Nozzle("N2", (0, 24), 350),
                          Nozzle("N3", (10, 10), 25)],
                 markers=[Marker("COLUMN_PACKED_BED_SHAPE", 0, 1.1)], label_at=(368, 75))

# HTS effluent from E-201 (P-103) through the tubes to R-202 (P-104); the hot bypass of
# TV-1601 holds the LT shift inlet temperature
hot_split = tee("T1035", at=(40, 150), branch="down", branch_dn=300)
line(sheet, "PG-1035", dn=600, fluid="Process gas", route=[
    offpage("in", at=(12, 150), note="from E-201, P-103"), hot_split, e401["T1"]],
    label_at=(55, 141.5))
hot_join = tee("T1043", at=(125, 200), branch="left", branch_dn=300)
line(sheet, "PG-1043", dn=600, fluid="Process gas", route=[
    e401["T2"], (125, 150), hot_join, (125, 240),
    offpage("out", at=(12, 240), note="to R-202, P-104", rotation=180)], label_at=(60, 231.5))
tv1601 = valve("TV1601", "GlobeValve", tag="TV-1601", at=(80, 200))
line(sheet, "PG-1082", dn=300, fluid="Process gas", route=[
    hot_split.branch, (40, 200), tv1601, hot_join.branch], label_at=(60, 205))

# Treated gas from C-301 (P-105) through the shell to the methanator
line(sheet, "PG-1056", dn=350, fluid="Process gas", route=[
    offpage("in", at=(12, 100), note="from C-301, P-105"), (83, 100), e401["S1"]],
    label_at=(45, 91.5))
xv1604 = valve("XV1604", "BallValve", tag="XV-1604", at=(140, 60))
line(sheet, "PG-1077", dn=500, fluid="Process gas", route=[
    e401["S2"], (97, 60), xv1604, (175, 60), r401["N1"]], label_at=(120, 51.5))
line(sheet, "PG-1078", dn=500, fluid="Process gas", route=[
    r401["N2"], (175, 160), e402["T1"]], label_at=(190, 147))
line(sheet, "PG-1079", dn=350, fluid="Process gas", route=[
    e402["T2"], (260, 160), (260, 135), v401["N1"]], label_at=(251, 151))
line(sheet, "PG-1080", dn=350, fluid="Process gas", route=[
    v401["N2"], (285, 50), (345, 50), x401["N1"]], label_at=(315, 41.5))
line(sheet, "PG-1081", dn=350, fluid="Process gas", route=[
    x401["N2"], (345, 128), offpage("out", at=(EDGE, 128), note="to K-501, P-108")],
    label_at=(375, 119.5))

# Condensate and regeneration water to the steam system (U-801)
lv1609 = valve("LV1609", "GlobeValve", tag="LV-1609", at=(285, 185))
line(sheet, "PC-1083", dn=25, fluid="Process condensate", route=[
    v401["N3"], lv1609, (285, 200), offpage("out", at=(EDGE, 200), note="to U-801")],
    label_at=(350, 204.5))
line(sheet, "PC-1084", dn=25, fluid="Process condensate", route=[
    x401["N3"], offpage("out", at=(EDGE, 100), note="to U-801")], label_at=(378, 104.5))

# Cooling water to E-402
line(sheet, "CWS-1085", dn=500, fluid="Cooling water", route=[
    offpage("in", at=(EDGE, 230), note="from CW supply", rotation=180), (218, 230), e402["S1"]],
    label_at=(330, 234.5))
tv1608 = valve("TV1608", "GlobeValve", tag="TV-1608", at=(232, 190))
line(sheet, "CWR-1086", dn=500, fluid="Cooling water", route=[
    e402["S2"], tv1608, (232, 215), offpage("out", at=(EDGE, 215), note="to CW return")],
    label_at=(330, 219.5))

# Instruments
instrument(sheet, "TIC-1601", at=(100, 222), sensing="Line_PG1043_S2", sensing_at=(125, 222),
           signal_to=tv1601)
instrument(sheet, "TI-1602", at=(62, 175), sensing="Line_PG1035_S2", sensing_at=(62, 150))
instrument(sheet, "TI-1603", at=(120, 75), sensing="Line_PG1077_S1", sensing_at=(120, 60))
instrument(sheet, "AI-1604", at=(65, 78), sensing="Line_PG1056_S1", sensing_at=(65, 100))
instrument(sheet, "TZ-1605", at=(145, 110), sensing=r401["N3"], signal_to=xv1604)
instrument(sheet, "TI-1606", at=(205, 125), sensing=r401["N4"])
instrument(sheet, "AI-1607", at=(155, 145), sensing="Line_PG1078_S1", sensing_at=(175, 145))
instrument(sheet, "TIC-1608", at=(250, 185), sensing="Line_PG1079_S1", sensing_at=(260, 160),
           signal_to=tv1608)
instrument(sheet, "LIC-1609", at=(310, 170), sensing=v401["N5"], signal_to=lv1609)
instrument(sheet, "AI-1610", at=(375, 140), sensing="Line_PG1081_S1", sensing_at=(375, 128))
instrument(sheet, "PI-1611", at=(310, 62), sensing="Line_PG1080_S1", sensing_at=(310, 50))

note(sheet, "TZ-1605: see C&E I-106 (methanator high-high temperature)", at=(20, 262))
note(sheet, "X-401: molecular sieve package (adsorbers, regeneration heater and gas inside)",
     at=(20, 269))
note(sheet, "R-401: Ni catalyst; AI-1604 CO + CO2 slip from C-301, AI-1607 after R-401",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
