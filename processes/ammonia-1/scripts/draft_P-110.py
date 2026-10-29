"""Draft of P-110: synthesis loop, cold part - loop water cooler E-503, cold exchanger E-505,
ammonia chiller E-504 (refrigerant from the K-701 package, P-111), ammonia separator V-501
with the purge take-off (SPL501), the separator liquid let-down (LV501) and the let-down
vessel V-502.

Provenance only: P-110 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-110.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-029; streams S45-S54, S99 of process/flowsheet.yaml.
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
EXCHANGER = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"

# Loop gas in the tubes of all three exchangers
e503 = equipment(sheet, "TubularHeatExchanger", "E-503", shape=EXCHANGER, at=(60, 80),
                 nozzles=[Nozzle("T1", (-17.5, 0), 300), Nozzle("T2", (17.5, 0), 300),
                          Nozzle("S1", (-7, -7), 350), Nozzle("S2", (7, -7), 350)],
                 label_at=(60, 93))
e505 = equipment(sheet, "TubularHeatExchanger", "E-505", shape=EXCHANGER, at=(150, 80),
                 nozzles=[Nozzle("T1", (-17.5, 0), 300), Nozzle("T2", (17.5, 0), 300),
                          Nozzle("S1", (7, 7), 250), Nozzle("S2", (-7, 7), 300)],
                 label_at=(150, 67))
e504 = equipment(sheet, "TubularHeatExchanger", "E-504", shape=EXCHANGER, at=(240, 80),
                 nozzles=[Nozzle("T1", (-17.5, 0), 300), Nozzle("T2", (17.5, 0), 250),
                          Nozzle("S1", (-7, -7), 200), Nozzle("S2", (7, -7), 900),
                          Nozzle("L1", (-14, -6), 25)],
                 label_at=(240, 93))
v501 = equipment(sheet, "Vessel", "V-501", shape=VESSEL, at=(250, 170), scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (10, -8), 250), Nozzle("N2", (0, -21), 250),
                          Nozzle("N3", (0, 21), 150), Nozzle("N4", (-10, -8), 100),
                          Nozzle("N5", (-10, 8), 50), Nozzle("N6", (10, 12), 50)],
                 label_at=(232, 200))
v502 = equipment(sheet, "Vessel", "V-502", shape=VESSEL, at=(335, 215), rotation=90,
                 scale=(1.0, 1.6),
                 nozzles=[Nozzle("N1", (-20, -10), 150), Nozzle("N2", (20, -10), 40),
                          Nozzle("N3", (15, 10), 150), Nozzle("N4", (-15, 10), 50),
                          Nozzle("N5", (0, -10), 80)],
                 label_at=(300, 232))

# Converter effluent from E-501 (P-109): E-503 -> E-505 hot side -> E-504 -> V-501
line(sheet, "PG-1102", dn=300, fluid="Synthesis gas", route=[
    offpage("in", at=(12, 80), note="from E-501, P-109"), e503["T1"]], label_at=(28, 88))
line(sheet, "PG-1105", dn=300, fluid="Synthesis gas (two-phase)", route=[
    e503["T2"], e505["T1"]], label_at=(115, 71.5))
line(sheet, "PG-1106", dn=300, fluid="Synthesis gas (two-phase)", route=[
    e505["T2"], e504["T1"]], label_at=(195, 71.5))
line(sheet, "PG-1107", dn=250, fluid="Synthesis gas (two-phase)", route=[
    e504["T2"], (275, 80), (275, 162), v501["N1"]], label_at=(290, 100))

# Separator gas: purge take-off (SPL501), cold recycle gas through the E-505 shell to K-502
purge = tee("T1108", at=(200, 125), branch="down", branch_dn=25)
line(sheet, "PG-1108", dn=250, fluid="Synthesis gas", route=[
    v501["N2"], (250, 125), purge, (157, 125), e505["S1"]], label_at=(225, 116.5))
line(sheet, "PG-1093", dn=300, fluid="Synthesis gas", route=[
    e505["S2"], (143, 110), offpage("out", at=(12, 110), note="to K-502, P-109", rotation=180)],
    label_at=(60, 101.5))
fv1905 = valve("FV1905", "GlobeValve", tag="FV-1905", at=(200, 150))
line(sheet, "PG-1109", dn=25, fluid="Purge gas", route=[
    purge.branch, fv1905, (200, 230),
    offpage("out", at=(12, 230), note="to X-601, P-112", rotation=180)], label_at=(100, 221.5))

# Separator liquid: low-low level trip valve, let-down valve LV501, let-down vessel V-502
xv1904 = valve("XV1904", "BallValve", tag="XV-1904", at=(272, 205))
lv1903 = valve("LV1903", "GlobeValve", tag="LV-1903", at=(295, 205))
line(sheet, "AL-1111", dn=150, fluid="Liquid ammonia", route=[
    v501["N3"], (250, 205), xv1904, lv1903, v502["N1"]], label_at=(282, 210))
pv1906 = valve("PV1906", "GlobeValve", tag="PV-1906", at=(372, 172))
line(sheet, "PG-1113", dn=40, fluid="Let-down gas", route=[
    v502["N2"], (355, 172), pv1906,
    offpage("out", at=(EDGE, 172), note="to X-601, P-112")], label_at=(346, 185))
lv1907 = valve("LV1907", "GlobeValve", tag="LV-1907", at=(375, 240))
line(sheet, "AL-1114", dn=150, fluid="Liquid ammonia", route=[
    v502["N3"], (350, 240), lv1907,
    offpage("out", at=(EDGE, 240), note="to V-701, P-111")], label_at=(360, 248.5))

# Refrigerant (ammonia) from and to the K-701 package (P-111)
lv1908 = valve("LV1908", "GlobeValve", tag="LV-1908", at=(233, 52))
line(sheet, "AL-1117", dn=200, fluid="Ammonia refrigerant (liquid)", route=[
    offpage("in", at=(EDGE, 30), note="from K-701 receiver, P-111", rotation=180), (233, 30),
    lv1908, e504["S1"]], label_at=(320, 21.5))
line(sheet, "AG-1118", dn=900, fluid="Ammonia refrigerant (vapour)", route=[
    e504["S2"], (247, 45), offpage("out", at=(EDGE, 45), note="to K-701 suction, P-111")],
    label_at=(320, 53.5))

# Cooling water to E-503 (headers on P-114)
line(sheet, "CWS-1115", dn=350, fluid="Cooling water", route=[
    offpage("in", at=(12, 55), note="from CW supply, P-114"), (53, 55), e503["S1"]],
    label_at=(33, 62))
line(sheet, "CWR-1116", dn=350, fluid="Cooling water", route=[
    e503["S2"], (67, 30), offpage("out", at=(12, 30), note="to CW return, P-114", rotation=180)],
    label_at=(42, 37))

# Relief to the flare header (P-114); globe valve placeholders made
# SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE by hand, as in D-027
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "PG-1119", dn=100, fluid="Synthesis gas", route=[
    v501["N4"], valve("PSV1911", "GlobeValve", tag="PSV-1911", at=(226, 162)), (215, 162),
    (215, 245), offpage("out", at=(12, 245), note="to flare header, P-114", rotation=180)],
    label_at=(100, 253.5))
line(sheet, "PG-1120", dn=80, fluid="Let-down gas", route=[
    v502["N5"], valve("PSV1912", "GlobeValve", tag="PSV-1912", at=(335, 192)), (335, 150),
    offpage("out", at=(EDGE, 150), note="to flare header, P-114")], label_at=(368, 141.5))

# Instruments
instrument(sheet, "TI-1901", at=(90, 62), sensing="Line_PG1105_S1", sensing_at=(90, 80))
instrument(sheet, "LIC-1903", at=(225, 190), sensing=v501["N5"], signal_to=lv1903,
           signal_points=[(225, 222), (295, 222)])
instrument(sheet, "LZ-1904", at=(282, 182), sensing=v501["N6"], signal_to=xv1904)
instrument(sheet, "FIC-1905", at=(180, 175), sensing="Line_PG1109_S1", sensing_at=(200, 175),
           signal_to=fv1905, signal_points=[(180, 150)])
instrument(sheet, "PIC-1906", at=(385, 195), sensing="Line_PG1113_S1", sensing_at=(355, 197),
           signal_to=pv1906)
instrument(sheet, "LIC-1907", at=(300, 245), sensing=v502["N4"], signal_to=lv1907,
           signal_points=[(300, 256), (375, 256)])
instrument(sheet, "LIC-1908", at=(212, 50), sensing=e504["L1"], signal_to=lv1908)
instrument(sheet, "TI-1909", at=(292, 125), sensing="Line_PG1107_S1", sensing_at=(275, 125))
instrument(sheet, "PI-1910", at=(232, 138), sensing="Line_PG1108_S1", sensing_at=(250, 138))

note(sheet, "LZ-1904: see C&E I-107 (V-501 level low-low: gas blow-by from 14.7 MPa into V-502)",
     at=(20, 262))
note(sheet, "LV-1903: separator let-down 14,700 to 2500 kPa(a); outlet two-phase, line size after the valve open (S99)",
     at=(20, 269))
note(sheet, "PSV-1911, PSV-1912: set pressure and relief case open (S8); E-504 shell relief with the K-701 package",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
