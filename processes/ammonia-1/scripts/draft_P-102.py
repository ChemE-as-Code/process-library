"""Draft of P-102: primary reformer furnace H-101 with its catalyst tubes R-101, the convection
coils E-103, E-102, E-104, E-101, E-106, E-107, the FD fan K-102 and the ID fan K-103.

Provenance only: P-102 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-102.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-027; streams S2, S3-S10, S11, S13, S14, S59, S61-S67, S80-S84.
The convection coils are drawn bottom (hottest) to top in flue gas order (D-024).
"""

import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    valve,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200); air and flue gas
# ducts above DN 1600 have no DEXPI standard
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")
duct = partial(authoring.line, standard="none")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

HX = "HEAT_EXCHANGER_SHAPE"
X = 230  # convection section axis
EDGE = 400


def coil(tag, y, dn_flue_in, dn_flue_out, dn_in, dn_out, side_in=1, side_out=1):
    """A convection coil: flue gas in at the bottom (F1), out at the top (F2); the process (or
    air, water) side in (P1) and out (P2) on the right (side 1) or the left (side -1)."""
    return equipment(sheet, "TubularHeatExchanger", tag, shape=HX, at=(X, y), scale=1.2,
                     nozzles=[Nozzle("F1", (0, 9), dn_flue_in), Nozzle("F2", (0, -9), dn_flue_out),
                              Nozzle("P1", (9 * side_in, -6), dn_in),
                              Nozzle("P2", (9 * side_out, 6), dn_out)],
                     label_at=(X - 22 * (side_in if side_in == side_out else 1), y - 9))


e107 = coil("E-107", 45, 2400, 2400, 200, 200)
e106 = coil("E-106", 79, 2800, 2400, 1800, 2400, side_in=-1, side_out=-1)
e101 = coil("E-101", 113, 3000, 2800, 150, 200)
e104 = coil("E-104", 147, 3400, 3000, 250, 300)
e102 = coil("E-102", 181, 3600, 3400, 400, 450)
e103 = coil("E-103", 215, 4000, 3600, 450, 500, side_out=-1)

h101 = equipment(sheet, "Furnace", "H-101", shape="FURNACE_SHAPE", at=(100, 200), scale=3.0,
                 nozzles=[Nozzle("B1", (-12, -37.5), 125), Nozzle("B2", (0, -37.5), 80),
                          Nozzle("B3", (12, -37.5), 2400), Nozzle("F1", (30, 30), 4000),
                          Nozzle("N1", (-20, 37.5), 25), Nozzle("N2", (0, 37.5), 25)],
                 label_at=(124, 172))
r101 = equipment(sheet, "TubularHeatExchanger", "R-101", shape=HX, at=(100, 200), scale=1.2,
                 nozzles=[Nozzle("N1", (9, -6), 500), Nozzle("N2", (-9, 6), 700)],
                 label_at=(100, 185))
k102 = equipment(sheet, "Fan", "K-102", shape="FAN_SHAPE", at=(150, 50),
                 nozzles=[Nozzle("N1", (-7.5, 0), 1800), Nozzle("N2", (7.5, 0), 1800)],
                 label_at=(150, 42))
k103 = equipment(sheet, "Fan", "K-103", shape="FAN_SHAPE", at=(320, 18),
                 nozzles=[Nozzle("N1", (-7.5, 0), 2400), Nozzle("N2", (7.5, 0), 2200)],
                 label_at=(320, 27))

# Flue gas path: radiant section -> E-103 -> E-102 -> E-104 -> E-101 -> E-106 -> E-107 -> K-103
duct(sheet, "FL-1014", dn=4000, fluid="Flue gas",
     route=[h101["F1"], (130, 240), (X, 240), e103["F1"]], label_at=(170, 245))
duct(sheet, "FL-1015", dn=3600, fluid="Flue gas", route=[e103["F2"], e102["F1"]])
duct(sheet, "FL-1016", dn=3400, fluid="Flue gas", route=[e102["F2"], e104["F1"]])
duct(sheet, "FL-1017", dn=3000, fluid="Flue gas", route=[e104["F2"], e101["F1"]])
duct(sheet, "FL-1018", dn=2800, fluid="Flue gas", route=[e101["F2"], e106["F1"]])
duct(sheet, "FL-1019", dn=2400, fluid="Flue gas", route=[e106["F2"], e107["F1"]])
duct(sheet, "FL-1020", dn=2400, fluid="Flue gas", route=[e107["F2"], (X, 18), k103["N1"]])
duct(sheet, "FL-1021", dn=2200, fluid="Flue gas", route=[
    k103["N2"], offpage("out", at=(EDGE, 18), note="to stack")])


# Process side of the coils (right-edge connectors to P-101 and P-103, D-027)
def side_in(number, dn, fluid, port, id=None):
    y = port.xy[1]
    line(sheet, number, dn=dn, fluid=fluid, label_at=(345, y - 7.5), id=id,
         route=[offpage("in", at=(EDGE, y), note=TEXT[number], rotation=180), port])


def side_out(number, dn, fluid, port):
    y = port.xy[1]
    line(sheet, number, dn=dn, fluid=fluid, label_at=(345, y + 4.5),
         route=[port, offpage("out", at=(EDGE, y), note=TEXT[number])])


TEXT = {
    "BW-1024": "from U-801 (BFW)", "BW-1025": "to U-801 (BFW)",
    "NG-1001": "from P-101", "NG-1003": "to V-101, P-101",
    "PA-1022": "from K-101, P-103", "PA-1023": "to R-102, P-103",
    "NG-1004": "from P-101", "PG-1006": "to R-100, P-101",
    "PG-1007": "from R-100, P-101",
}
side_in("BW-1024", 200, "Boiler feed water", e107["P1"])
side_out("BW-1025", 200, "Boiler feed water", e107["P2"])
side_in("NG-1001", 150, "Natural gas", e101["P1"])
side_out("NG-1003", 200, "Natural gas", e101["P2"])
side_in("PA-1022", 250, "Process air", e104["P1"])
side_out("PA-1023", 300, "Process air", e104["P2"])
# the mixed-feed segment of NG-1004 (S2 on P-101): its SegmentNumber is set to S2 after this
# script (cheme set Line_NG1004_P102_S1 SegmentNumber=S2, D-027)
side_in("NG-1004", 400, "Natural gas", e102["P1"], id="Line_NG1004_P102")
side_out("PG-1006", 450, "Process gas", e102["P2"])
side_in("PG-1007", 450, "Process gas", e103["P1"])
# E-103 -> R-101 catalyst tubes -> secondary reformer
line(sheet, "PG-1008", dn=500, fluid="Process gas",
     route=[e103["P2"], (150, 221), (150, 194), r101["N1"]], label_at=(185, 226))
line(sheet, "PG-1009", dn=700, fluid="Process gas", label_at=(35, 211),
     route=[r101["N2"], offpage("out", at=(15, 206), note="to R-102, P-103", rotation=180)])

# Combustion air: atmosphere -> K-102 -> E-106 -> burners
duct(sheet, "CA-1011", dn=1800, fluid="Air", route=[
    offpage("in", at=(15, 50), note="from atmosphere"), k102["N1"]])
duct(sheet, "CA-1012", dn=1800, fluid="Air",
     route=[k102["N2"], (200, 50), (200, 73), e106["P1"]])
fv1108 = valve("FV1108", "ButterflyValve", tag="FV-1108", at=(160, 85))
duct(sheet, "CA-1013", dn=2400, fluid="Air", label_at=(140, 77), route=[e106["P2"], fv1108, (112, 85), h101["B3"]])
# Fuel: natural gas from P-101 and tail gas from the purge gas recovery
xv1102 = valve("XV1102", "BallValve", tag="XV-1102", at=(35, 120))
pv1101 = valve("PV1101", "GlobeValve", tag="PV-1101", at=(60, 120))
line(sheet, "FG-1002", dn=80, fluid="Fuel gas", label_at=(82, 112), route=[
    offpage("in", at=(15, 120), note="from P-101"), xv1102, pv1101, (100, 120), h101["B2"]])
xv1105 = valve("XV1105", "BallValve", tag="XV-1105", at=(35, 145))
line(sheet, "FG-1010", dn=125, fluid="Tail gas", label_at=(72, 137), route=[
    offpage("in", at=(15, 145), note="from X-601 (tail gas)"), xv1105, (88, 145), h101["B1"]])

# Instruments
instrument(sheet, "PIC-1101", at=(60, 103), sensing="Line_FG1002_S1", sensing_at=(75, 120),
           signal_to=pv1101)
instrument(sheet, "US-1102", at=(35, 103), signal_to=xv1102)
instrument(sheet, "TIC-1103", at=(40, 190), sensing="Line_PG1009_S1", sensing_at=(55, 206))
instrument(sheet, "FI-1104", at=(60, 160), sensing="Line_FG1010_S1", sensing_at=(60, 145))
instrument(sheet, "US-1105", at=(35, 160), signal_to=xv1105)
instrument(sheet, "TI-1106", at=(170, 207), sensing="Line_PG1008_S1", sensing_at=(150, 207))
instrument(sheet, "PIC-1107", at=(70, 256), sensing=h101["N1"])
instrument(sheet, "PZ-1108", at=(100, 262), sensing=h101["N2"])
instrument(sheet, "AIC-1109", at=(262, 29), sensing="Line_FL1020_S1", sensing_at=(245, 18))
instrument(sheet, "FIC-1110", at=(160, 102), sensing="Line_CA1013_S1", sensing_at=(185, 85),
           signal_to=fv1108)
instrument(sheet, "TI-1111", at=(205, 256), sensing="Line_FL1014_S1", sensing_at=(205, 240))
instrument(sheet, "TI-1112", at=(370, 29), sensing="Line_FL1021_S1", sensing_at=(370, 18))
instrument(sheet, "TI-1113", at=(300, 164), sensing="Line_PA1023_S1", sensing_at=(300, 153))

note(sheet, "XV-1102, XV-1105: see C&E I-102", at=(20, 70))
note(sheet, "TIC-1103 resets PIC-1101 (reformer outlet temperature)", at=(20, 78))
note(sheet, "AIC-1109 resets FIC-1110 (excess air)", at=(130, 266))
note(sheet, "PIC-1107 (draft) acts on the K-103 speed", at=(130, 272))
note(sheet, "R-101: catalyst tubes in the radiant box of H-101", at=(130, 278))
note(sheet, "Air and flue gas ducts: DN = equivalent diameter, ASSUMED", at=(130, 284))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
