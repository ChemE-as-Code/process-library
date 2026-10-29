"""Draft of P-109: synthesis loop, hot part - make-up / recycle junction (M502), recycle
circulator K-502 with anti-surge recycle, converter feed/effluent exchanger E-501 with the
converter inlet temperature bypass, ammonia converter R-501 and the effluent waste heat boiler
E-502 (boiler water from and steam-water mixture to the steam drum in U-801, P-113).

Provenance only: P-109 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-109.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-029; streams S38-S45 of process/flowsheet.yaml.
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
EXCHANGER = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
BED = "COLUMN_PACKED_BED_SHAPE"

k502 = equipment(sheet, "CentrifugalCompressor", "K-502", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                 at=(85, 160), scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 300), Nozzle("N2", (15, 0), 300)],
                 label_at=(85, 182))
# E-501: converter feed in the shell, converter effluent in the tubes
e501 = equipment(sheet, "TubularHeatExchanger", "E-501", shape=EXCHANGER, at=(160, 190),
                 nozzles=[Nozzle("T1", (-17.5, 0), 300), Nozzle("T2", (17.5, 0), 400),
                          Nozzle("S1", (-7, -7), 300), Nozzle("S2", (7, -7), 400)],
                 label_at=(160, 203))
r501 = equipment(sheet, "Vessel", "R-501", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(240, 115), scale=(1.2, 2.0),
                 nozzles=[Nozzle("N1", (0, -30), 400), Nozzle("N2", (0, 30), 450),
                          Nozzle("N3", (12, -15), 25), Nozzle("N4", (12, 0), 25),
                          Nozzle("N5", (12, 15), 25)],
                 markers=[Marker(BED, -16, 0.45), Marker(BED, 0, 0.45), Marker(BED, 16, 0.45)],
                 label_at=(218, 100))
e502 = equipment(sheet, "TubularHeatExchanger", "E-502", shape=EXCHANGER, at=(310, 170),
                 nozzles=[Nozzle("T1", (-17.5, 0), 450), Nozzle("T2", (17.5, 0), 400),
                          Nozzle("S1", (-7, -7), 400), Nozzle("S2", (7, -7), 250)],
                 label_at=(310, 183))

# Compressed make-up gas (P-108) joins the warm recycle gas (P-110): M502
mu_in = tee("T1093A", at=(30, 160), branch="up", branch_dn=200)
asr_in = tee("T1093B", at=(42, 160), branch="up", branch_dn=150)
line(sheet, "PG-1093", dn=300, fluid="Synthesis gas", route=[
    offpage("in", at=(12, 160), note="from E-505, P-110"), mu_in, asr_in, k502["N1"]],
    label_at=(20, 172))
line(sheet, "PG-1088", dn=200, fluid="Synthesis gas", route=[
    offpage("in", at=(12, 70), note="from K-501, P-108"), (30, 70), mu_in.branch],
    label_at=(42, 95))

# Circulator discharge to the E-501 shell; anti-surge recycle and converter inlet bypass
asr_out = tee("T1095A", at=(112, 160), branch="up", branch_dn=150)
byp_out = tee("T1095B", at=(128, 160), branch="up", branch_dn=150)
line(sheet, "PG-1095", dn=300, fluid="Synthesis gas", route=[
    k502["N2"], asr_out, byp_out, (153, 160), e501["S1"]], label_at=(128, 172))
uv1802 = valve("UV1802", "GlobeValve", tag="UV-1802", at=(77, 125))
line(sheet, "PG-1104", dn=150, fluid="Synthesis gas", route=[
    asr_out.branch, (112, 125), uv1802, (42, 125), asr_in.branch], label_at=(90, 116.5))

byp_in = tee("T1096", at=(167, 140), branch="left", branch_dn=150)
line(sheet, "PG-1096", dn=400, fluid="Synthesis gas", route=[
    e501["S2"], byp_in, (167, 60), (240, 60), r501["N1"]], label_at=(222, 51.5))
tv1803 = valve("TV1803", "GlobeValve", tag="TV-1803", at=(147, 140))
line(sheet, "PG-1097", dn=150, fluid="Synthesis gas", route=[
    byp_out.branch, (128, 140), tv1803, byp_in.branch], label_at=(140, 131.5))

# Converter effluent: waste heat boiler E-502, then the E-501 tubes, then to E-503 (P-110)
line(sheet, "PG-1098", dn=450, fluid="Synthesis gas", route=[
    r501["N2"], (240, 170), e502["T1"]], label_at=(262, 178.5))
line(sheet, "PG-1099", dn=400, fluid="Synthesis gas", route=[
    e502["T2"], (345, 170), (345, 225), (185, 225), (185, 190), e501["T2"]],
    label_at=(265, 233.5))
line(sheet, "PG-1102", dn=300, fluid="Synthesis gas", route=[
    e501["T1"], (125, 190), (125, 240),
    offpage("out", at=(12, 240), note="to E-503, P-110", rotation=180)], label_at=(60, 248.5))

# E-502 steam side: natural circulation from and to the steam drum (U-801, P-113)
line(sheet, "BW-1100", dn=400, fluid="Boiler water", route=[
    offpage("in", at=(EDGE, 120), note="from steam drum U-801, P-113", rotation=180),
    (303, 120), e502["S1"]], label_at=(355, 111.5))
line(sheet, "SM-1101", dn=250, fluid="Steam-water mixture", route=[
    e502["S2"], (317, 140), offpage("out", at=(EDGE, 140), note="to steam drum U-801, P-113")],
    label_at=(360, 148.5))

# Instruments
instrument(sheet, "UIC-1802", at=(56, 141), sensing="Line_PG1093_S3", sensing_at=(56, 160),
           signal_to=uv1802)
instrument(sheet, "TIC-1803", at=(200, 40), sensing="Line_PG1096_S2", sensing_at=(200, 60),
           signal_to=tv1803, signal_points=[(147, 40)])
instrument(sheet, "AI-1804", at=(187, 100), sensing="Line_PG1096_S2", sensing_at=(167, 100))
instrument(sheet, "TI-1805", at=(270, 92), sensing=r501["N3"])
instrument(sheet, "TI-1806", at=(270, 112), sensing=r501["N4"])
instrument(sheet, "TI-1807", at=(270, 132), sensing=r501["N5"])
instrument(sheet, "TI-1808", at=(222, 160), sensing="Line_PG1098_S1", sensing_at=(240, 160))
instrument(sheet, "PI-1809", at=(187, 78), sensing="Line_PG1096_S2", sensing_at=(167, 78))
instrument(sheet, "TI-1810", at=(290, 210), sensing="Line_PG1099_S1", sensing_at=(290, 225))
instrument(sheet, "TI-1811", at=(108, 215), sensing="Line_PG1102_S1", sensing_at=(125, 215))

note(sheet, "K-502: recycle circulator, electric drive (D-016); UIC-1802 anti-surge on the suction flow",
     at=(20, 262))
note(sheet, "R-501: 3 adiabatic beds, interbed exchange inside the converter; TIC-1803 converter inlet by the E-501 bypass",
     at=(20, 269))
note(sheet, "AI-1804: H2/N2 ratio of the converter feed, trims the process air (P-103, S4); loop relief on V-501 (P-110)",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
