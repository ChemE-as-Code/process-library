"""Draft of P-104: low-temperature shift converter R-202, the CO2 regenerator reboiler E-202
(process-gas side), the final cooler E-203 and the process condensate separator V-201.

Provenance only: P-104 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-104.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-027; streams S20-S25 of process/flowsheet.yaml.
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
    valve,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
EDGE = 400

r202 = equipment(sheet, "Vessel", "R-202", shape=VESSEL, at=(70, 110), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (0, -21), 600), Nozzle("N2", (0, 21), 600),
                          Nozzle("N3", (-10, 0), 25)],
                 markers=[Marker("COLUMN_PACKED_BED_SHAPE", 0, 0.9)], label_at=(88, 110))
e202 = equipment(sheet, "TubularHeatExchanger", "E-202", shape="KETTLE_REBOILER_SHAPE",
                 at=(160, 120),
                 nozzles=[Nozzle("T1", (-17.5, -3.63), 600), Nozzle("T2", (-17.5, 1.62), 500),
                          Nozzle("S1", (2.62, 4.25), 600), Nozzle("S2", (6.12, -11.5), 800),
                          Nozzle("S3", (17.5, -1), 600)],
                 label_at=(150, 100))
e203 = equipment(sheet, "TubularHeatExchanger", "E-203", shape="HEAT_EXCHANGER_FIXED_TUBES_SHAPE",
                 at=(230, 210),
                 nozzles=[Nozzle("T1", (-17.5, 0), 500), Nozzle("T2", (17.5, 0), 450),
                          Nozzle("S1", (-7, 7), 700), Nozzle("S2", (7, 7), 700)],
                 label_at=(230, 199))
v201 = equipment(sheet, "Vessel", "V-201", shape=VESSEL, at=(320, 190), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (-12, -5), 450), Nozzle("N2", (0, -24), 400),
                          Nozzle("N3", (0, 24), 125), Nozzle("N4", (12, -10), 50),
                          Nozzle("N5", (12, 10), 50), Nozzle("N6", (-8, -22), 150)],
                 label_at=(300, 172))

# Process gas: E-401 (CO2 removal sheet) -> R-202 -> E-202 -> E-203 -> V-201 -> C-301
line(sheet, "PG-1043", dn=600, fluid="Process gas", route=[
    offpage("in", at=(12, 70), note="from E-401"), (70, 70), r202["N1"]], label_at=(40, 61.5))
line(sheet, "PG-1044", dn=600, fluid="Process gas", route=[
    r202["N2"], (70, 145), (110, 145), (110, 116.37), e202["T1"]], label_at=(92, 136.5))
line(sheet, "PG-1045", dn=500, fluid="Process gas", route=[
    e202["T2"], (125, 121.62), (125, 210), e203["T1"]], label_at=(160, 201.5))
line(sheet, "PG-1046", dn=450, fluid="Process gas", route=[
    e203["T2"], (280, 210), (280, 185), v201["N1"]], label_at=(265, 201.5))
line(sheet, "PG-1047", dn=400, fluid="Process gas", route=[
    v201["N2"], (320, 160), offpage("out", at=(EDGE, 160), note="to C-301")],
    label_at=(370, 164.5))
# V-201 relief (fire case and blocked outlet, not sized: S8): globe valve placeholder made a
# SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE by hand (D-027)
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "PG-1055", dn=150, fluid="Process gas", route=[
    v201["N6"], (312, 155), valve("PSV1310", "GlobeValve", tag="PSV-1310", at=(296, 155)),
    offpage("out", at=(272, 155), note="to flare", rotation=180)], label_at=(292, 146.5))
lv1307 = valve("LV1307", "GlobeValve", tag="LV-1307", at=(320, 228))
line(sheet, "PC-1048", dn=125, fluid="Process condensate", route=[
    v201["N3"], lv1307, (320, 240), offpage("out", at=(EDGE, 240), note="to U-801 (stripper)")],
    label_at=(360, 244.5))

# E-202 shell side: the regenerator bottoms of C-302 (CO2 removal sheet) boiled by the gas
line(sheet, "AM-1049", dn=600, fluid="aMDEA solution", route=[
    offpage("in", at=(EDGE, 140), note="from C-302 (bottoms)", rotation=180), (162.62, 140),
    e202["S1"]], label_at=(300, 131.5))
line(sheet, "AM-1050", dn=800, fluid="aMDEA vapour", route=[
    e202["S2"], (166.12, 60), offpage("out", at=(EDGE, 60), note="to C-302 (reboiler vapour)")],
    label_at=(300, 51.5))
line(sheet, "AM-1051", dn=600, fluid="aMDEA solution", route=[
    e202["S3"], offpage("out", at=(EDGE, 119), note="to C-302 (lean solvent)")],
    label_at=(300, 110.5))

# Cooling water to E-203
line(sheet, "CWS-1052", dn=700, fluid="Cooling water", route=[
    offpage("in", at=(12, 245), note="from CW supply"), (223, 245), e203["S1"]],
    label_at=(60, 236.5))
tv1306 = valve("TV1306", "GlobeValve", tag="TV-1306", at=(237, 240))
line(sheet, "CWR-1053", dn=700, fluid="Cooling water", route=[
    e203["S2"], tv1306, (237, 255), offpage("out", at=(12, 255), note="to CW return",
                                            rotation=180)], label_at=(60, 259.5))

# Instruments
instrument(sheet, "TI-1301", at=(45, 82), sensing="Line_PG1043_S1", sensing_at=(70, 80))
instrument(sheet, "TI-1302", at=(45, 138), sensing="Line_PG1044_S1", sensing_at=(70, 138))
instrument(sheet, "PDI-1303", at=(45, 110), sensing=r202["N3"])
instrument(sheet, "AI-1304", at=(90, 160), sensing="Line_PG1044_S1", sensing_at=(90, 145))
instrument(sheet, "TI-1305", at=(100, 180), sensing="Line_PG1045_S1", sensing_at=(125, 180))
instrument(sheet, "TIC-1306", at=(260, 232), sensing="Line_PG1046_S1", sensing_at=(260, 210),
           signal_to=tv1306)
instrument(sheet, "LIC-1307", at=(350, 225), sensing=v201["N5"], signal_to=lv1307)
instrument(sheet, "LZ-1308", at=(355, 182), sensing=v201["N4"])
instrument(sheet, "PI-1309", at=(345, 148), sensing="Line_PG1047_S1", sensing_at=(345, 160))

note(sheet, "LZ-1308: see C&E I-104 (liquid carry-over to C-301)", at=(20, 275))
note(sheet, "R-202: Cu-Zn catalyst; E-202 duty sets the C-302 regeneration heat (D-009)",
     at=(20, 282))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
