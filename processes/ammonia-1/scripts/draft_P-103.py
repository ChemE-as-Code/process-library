"""Draft of P-103: process air compressor K-101, secondary reformer R-102, its waste heat boiler
E-105, the high-temperature shift converter R-201 and its waste heat boiler E-201.

Provenance only: P-103 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-103.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-027; streams S11-S19, S75, S86 of process/flowsheet.yaml.
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

BED = [Marker("COLUMN_PACKED_BED_SHAPE", 6, 1.2)]
VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
WHB = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
EDGE = 400

k101 = equipment(sheet, "CentrifugalCompressor", "K-101", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                 at=(80, 45), scale=1.5,
                 nozzles=[Nozzle("N1", (-11.25, 0), 1200), Nozzle("N2", (11.25, 0), 250),
                          Nozzle("N3", (-5, 11.25), 300), Nozzle("N4", (5, 11.25), 300)],
                 label_at=(80, 28))
r102 = equipment(sheet, "Vessel", "R-102", shape=VESSEL, at=(170, 150), scale=(1.2, 1.8),
                 nozzles=[Nozzle("N1", (0, -27), 700), Nozzle("N2", (12, -18), 300),
                          Nozzle("N3", (0, 27), 900), Nozzle("N4", (-12, 8), 25)],
                 markers=BED, label_at=(192, 165))
e105 = equipment(sheet, "TubularHeatExchanger", "E-105", shape=WHB, at=(240, 215),
                 nozzles=[Nozzle("T1", (-17.5, 0), 900), Nozzle("T2", (17.5, 0), 600),
                          Nozzle("S1", (-7, 7), 450), Nozzle("S2", (7, 7), 300)],
                 label_at=(240, 204))
r201 = equipment(sheet, "Vessel", "R-201", shape=VESSEL, at=(320, 150), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (0, -21), 600), Nozzle("N2", (0, 21), 700),
                          Nozzle("N3", (-10, 0), 25)],
                 markers=[Marker("COLUMN_PACKED_BED_SHAPE", 0, 0.9)], label_at=(338, 150))
e201 = equipment(sheet, "TubularHeatExchanger", "E-201", shape=WHB, at=(350, 200),
                 nozzles=[Nozzle("T1", (-17.5, 0), 700), Nozzle("T2", (17.5, 0), 600),
                          Nozzle("S1", (-7, 7), 200), Nozzle("S2", (7, 7), 125)],
                 label_at=(350, 189))

# Process air: atmosphere -> K-101 (4 stages, intercooled, D-016/D-024) -> E-104 (P-102)
fv1201 = valve("FV1201", "ButterflyValve", tag="FV-1201", at=(30, 45))
line(sheet, "PA-1030", dn=1200, fluid="Air", route=[
    offpage("in", at=(12, 45), note="from atmosphere (filter)", note_at=(29, 51)), fv1201,
    k101["N1"]], label_at=(60, 54))
relief = tee("T1054", at=(100, 45), branch="down", branch_dn=100)
blow = tee("T1022", at=(110, 45), branch="up", branch_dn=150)
line(sheet, "PA-1022", dn=250, fluid="Process air", route=[
    k101["N2"], relief, blow, valve("CV1022", "SwingCheckValve", at=(135, 45)),
    offpage("out", at=(EDGE, 45), note="to E-104, P-102")], label_at=(300, 36.5))
# K-101 discharge relief: drawn with a globe valve placeholder that is then made a
# SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE by hand (D-027)
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "PA-1054", dn=100, fluid="Process air", route=[
    relief.branch, valve("PSV1212", "GlobeValve", tag="PSV-1212", at=(100, 60)),
    offpage("out", at=(100, 75), note="to atmosphere", rotation=90)], label_at=(113, 64))
fv1202 = valve("FV1202", "GlobeValve", tag="FV-1202", at=(140, 18))
line(sheet, "PA-1031", dn=150, fluid="Process air", route=[
    blow.branch, (110, 18), fv1202, valve("SL1031", "Silencer", at=(170, 18)),
    offpage("out", at=(200, 18), note="to atmosphere")], label_at=(125, 9))
line(sheet, "CWS-1041", dn=300, fluid="Cooling water", route=[
    offpage("in", at=(12, 85), note="from CW supply"), (75, 85), (75, 80), k101["N3"]],
    label_at=(40, 76.5))
line(sheet, "CWR-1042", dn=300, fluid="Cooling water", route=[
    k101["N4"], (85, 95), offpage("out", at=(12, 95), note="to CW return", rotation=180)],
    label_at=(40, 100))

# Reformed gas from R-101 (P-102) and preheated air from E-104 (P-102) into R-102
line(sheet, "PG-1009", dn=700, fluid="Process gas", route=[
    offpage("in", at=(12, 112), note="from R-101, P-102"), (170, 112), r102["N1"]],
    label_at=(60, 103.5))
xv1204 = valve("XV1204", "BallValve", tag="XV-1204", at=(330, 75))
line(sheet, "PA-1023", dn=300, fluid="Process air", route=[
    offpage("in", at=(EDGE, 75), note="from E-104, P-102", rotation=180), xv1204,
    valve("CV1023", "SwingCheckValve", at=(280, 75)), (250, 75), (250, 132), r102["N2"]],
    label_at=(300, 66.5))

# R-102 -> E-105 (with the hot bypass of TV-1207) -> R-201 -> E-201 -> E-401 (CO2 removal sheet)
byp_out = tee("T1032", at=(170, 190), branch="right", branch_dn=400)
line(sheet, "PG-1032", dn=900, fluid="Process gas", route=[
    r102["N3"], byp_out, (170, 215), e105["T1"]], label_at=(150, 205))
byp_in = tee("T1033", at=(275, 215), branch="up", branch_dn=400)
line(sheet, "PG-1033", dn=600, fluid="Process gas", route=[
    e105["T2"], byp_in, (290, 215), (290, 115), (320, 115), r201["N1"]], label_at=(270, 110))
tv1207 = valve("TV1207", "GlobeValve", tag="TV-1207", at=(225, 190))
line(sheet, "PG-1036", dn=400, fluid="Process gas", route=[
    byp_out.branch, tv1207, (275, 190), byp_in.branch], label_at=(250, 185))
line(sheet, "PG-1034", dn=700, fluid="Process gas", route=[
    r201["N2"], (320, 200), e201["T1"]], label_at=(305, 182))
line(sheet, "PG-1035", dn=600, fluid="Process gas", route=[
    e201["T2"], offpage("out", at=(EDGE, 200), note="to E-401")], label_at=(378, 191.5))

# Waste heat boilers: boiler water from and steam-water mixture to the steam drum (U-801)
line(sheet, "BW-1037", dn=450, fluid="Boiler water", route=[
    offpage("in", at=(12, 238), note="from U-801 (steam drum)"), (233, 238), e105["S1"]],
    label_at=(60, 229.5))
line(sheet, "SM-1038", dn=300, fluid="Steam-water mixture", route=[
    e105["S2"], (247, 252), offpage("out", at=(12, 252), note="to U-801 (steam drum)",
                                   rotation=180)], label_at=(60, 257))
line(sheet, "BW-1039", dn=200, fluid="Boiler water", route=[
    offpage("in", at=(EDGE, 245), note="from U-801 (steam drum)", rotation=180), (343, 245),
    e201["S1"]], label_at=(370, 249.5))
line(sheet, "SM-1040", dn=125, fluid="Steam-water mixture", route=[
    e201["S2"], (357, 222), offpage("out", at=(EDGE, 222), note="to U-801 (steam drum)")],
    label_at=(372, 226.5))

# Instruments
instrument(sheet, "FIC-1201", at=(30, 28), sensing="Line_PA1030_S1", sensing_at=(45, 45),
           signal_to=fv1201)
instrument(sheet, "UIC-1202", at=(140, 32), sensing="Line_PA1022_S3", sensing_at=(122, 45),
           signal_to=fv1202)
instrument(sheet, "PI-1203", at=(160, 60), sensing="Line_PA1022_S3", sensing_at=(160, 45))
instrument(sheet, "US-1204", at=(330, 92), signal_to=xv1204)
instrument(sheet, "TZ-1205", at=(140, 182), sensing="Line_PG1032_S1", sensing_at=(170, 182))
instrument(sheet, "TI-1206", at=(135, 158), sensing=r102["N4"])
instrument(sheet, "TIC-1207", at=(225, 170), sensing="Line_PG1033_S2", sensing_at=(290, 170),
           signal_to=tv1207)
instrument(sheet, "AI-1208", at=(265, 140), sensing="Line_PG1033_S2", sensing_at=(290, 140))
instrument(sheet, "PDI-1209", at=(298, 150), sensing=r201["N3"])
instrument(sheet, "TI-1210", at=(345, 178), sensing="Line_PG1034_S1", sensing_at=(320, 185))
instrument(sheet, "TI-1211", at=(385, 212), sensing="Line_PG1035_S1", sensing_at=(385, 200))

note(sheet, "XV-1204: see C&E I-103 (R-102 outlet high-high temperature)", at=(215, 60))
note(sheet, "FIC-1201 setpoint from the H2/N2 ratio at the converter", at=(215, 30))
note(sheet, "UIC-1202: anti-surge control of K-101", at=(215, 23))
note(sheet, "K-101: 4 stages, intercoolers in the package, electric drive", at=(20, 277))
note(sheet, "R-102 refractory lined; burner zone and Ni bed; R-201 Fe-Cr catalyst",
     at=(20, 270))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
