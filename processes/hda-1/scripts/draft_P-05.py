"""Draft of P-05: benzene column C-202 with its total condenser E-203, reflux drum V-202,
reflux and product pumps P-202A/B, the thermosyphon reboiler E-204 on LP steam and the benzene
product cooler E-207 to the battery limit.

Provenance only: P-05 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-05.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-025; streams S20-S22, S26 and duties Q7, Q8, Q11 of
process/flowsheet.yaml (the column, condenser, drum and reboiler are lumped in step C202).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Marker,
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)
from pid_common import DRUM, HX, LEFT, PUMP, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
BOTTOM = 248

# ---- equipment
c202 = equipment(sheet, "ProcessColumn", "C-202", shape="COLUMN_SHAPE", at=(130, 135),
                 scale=(1.0, 2.4),
                 nozzles=[Nozzle("N1", (-10, -27), 80), Nozzle("N2", (0, -60), 450),
                          Nozzle("N3", (10, -48), 125), Nozzle("N4", (0, 60), 50),
                          Nozzle("N5", (-10, 45), 200), Nozzle("N6", (-10, 25), 500),
                          Nozzle("N7", (-10, -50), 150), Nozzle("N8", (-10, 55), 50),
                          Nozzle("N9", (-10, 0), 25), Nozzle("N10", (6, 58), 50)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(130, 150))
e203 = equipment(sheet, "TubularHeatExchanger", "E-203", shape=HX, at=(180, 60),
                 nozzles=[Nozzle("T1", (-17.5, 0), 450), Nozzle("T2", (17.5, 0), 150),
                          Nozzle("S1", (-7, -7), 300), Nozzle("S2", (7, -7), 300)],
                 label_at=(180, 74))
v202 = equipment(sheet, "Vessel", "V-202", shape=DRUM, at=(240, 100), scale=(1.4, 1.0),
                 nozzles=[Nozzle("N1", (-14, -8), 150), Nozzle("N2", (0, -15), 50),
                          Nozzle("N3", (0, 15), 150), Nozzle("N4", (-14, 6), 50),
                          Nozzle("N5", (14, 6), 40), Nozzle("N6", (14, -5), 50), Nozzle("N7", (-8, 15), 50)],
                 label_at=(240, 100))
e204 = equipment(sheet, "TubularHeatExchanger", "E-204", shape=HX, at=(65, 170),
                 nozzles=[Nozzle("S1", (-7, -7), 250), Nozzle("S2", (-7, 7), 50),
                          Nozzle("T1", (7, 7), 200), Nozzle("T2", (7, -7), 500)],
                 label_at=(48, 185))
e207 = equipment(sheet, "TubularHeatExchanger", "E-207", shape=HX, at=(345, 90),
                 nozzles=[Nozzle("T1", (-17.5, 0), 65), Nozzle("T2", (17.5, 0), 65),
                          Nozzle("S1", (-7, -7), 100), Nozzle("S2", (7, -7), 100)],
                 label_at=(345, 104))
p202a = equipment(sheet, "CentrifugalPump", "P-202A", shape=PUMP, at=(277, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 125)],
                  label_at=(277, 202))
p202b = equipment(sheet, "CentrifugalPump", "P-202B", shape=PUMP, at=(325, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 125)],
                  label_at=(338, 202))

# ---- feed from LV-408 (P-04)
line(sheet, "AR-120", dn=80, fluid="Stabilised aromatics", route=[
    offpage("in", at=(LEFT, 108), note="from LV-408, P-04", note_at=(26, 102)), c202["N1"]],
    label_at=(88, 102))

# ---- column relief to the flare
psv514 = valve("PSV514", "GlobeValve", tag="PSV-514", at=(100, 55))
line(sheet, "FL-548", dn=150, fluid="Relief gas", route=[
    c202["N7"], (100, 85), psv514,
    offpage("out", at=(100, TOP), note="to flare header, P-07", rotation=270, note_at=(80, 12))],
    label_at=(88, 40))

# ---- overhead, total condenser, reflux drum
line(sheet, "PG-530", dn=450, fluid="Benzene vapour", route=[
    c202["N2"], (130, 60), e203["T1"]], label_at=(145, 52))
line(sheet, "BZ-531", dn=150, fluid="Benzene", route=[
    e203["T2"], (215, 60), (215, 92), v202["N1"]], label_at=(205, 80))
cw_relief = tee("T544", at=(173, 40), branch="left", branch_dn=25)
line(sheet, "CWS-542", dn=300, fluid="Cooling water", route=[
    offpage("in", at=(173, TOP), note="from CW supply, P-08", rotation=90, note_at=(152, 9)),
    cw_relief, e203["S1"]], label_at=(165, 48))
line(sheet, "CWR-543", dn=300, fluid="Cooling water", route=[
    e203["S2"],
    offpage("out", at=(187, TOP), note="to CW return, P-08", rotation=270, note_at=(205, 18))],
    label_at=(198, 32))
psv515 = valve("PSV515", "GlobeValve", tag="PSV-515", at=(155, 30))
line(sheet, "CWS-544", dn=25, fluid="Cooling water", route=[
    cw_relief.branch, (155, 40), psv515,
    offpage("out", at=(155, 20), note="to atmosphere (safe location)", rotation=270,
            note_at=(130, 23))],
    label_at=(143, 36))

# ---- V-202 pressure: vent to the flare on PV-504, nitrogen through the regulator PCV-505
n2_in = tee("T550", at=(240, 55), branch="left", branch_dn=25)
pv504 = valve("PV504", "GlobeValve", tag="PV-504", at=(265, 40))
line(sheet, "FL-549", dn=50, fluid="Relief gas", route=[
    v202["N2"], n2_in, (240, 40), pv504, (285, 40),
    offpage("out", at=(285, TOP), note="to flare header, P-07", rotation=270, note_at=(282, 7))],
    label_at=(252, 70))
line(sheet, "N2-550", dn=25, fluid="Nitrogen", route=[
    offpage("in", at=(225, TOP), note="from N2 header, P-07", rotation=90, note_at=(232, 6)),
    valve("PCV505", "GlobeValve", tag="PCV-505", at=(225, 40)), (225, 55), n2_in.branch],
    label_at=(232, 30))

# ---- reflux and distillate: V-202 -> P-202A/B -> reflux FV-507 to C-202, distillate LV-506
suction = tee("T533", at=(247, 190), branch="down", branch_dn=150)
line(sheet, "BZ-532", dn=150, fluid="Benzene", route=[
    v202["N3"], (240, 190), suction, valve("HV532", "GateValve", at=(255, 190)),
    valve("SR532", "Strainer", at=(262, 190)), p202a["N1"]], label_at=(228, 150))
line(sheet, "BZ-533", dn=150, fluid="Benzene", route=[
    suction.branch, (247, 212), (310, 212), valve("HV533", "GateValve", at=(310, 205)),
    valve("SR533", "Strainer", at=(310, 198)), (310, 190), p202b["N1"]], label_at=(280, 218))
join = tee("T535", at=(277, 164), branch="right", branch_dn=125)
minflow = tee("T536", at=(277, 156), branch="left", branch_dn=40)
fv507 = valve("FV507", "GlobeValve", tag="FV-507", at=(295, 140))
distillate = tee("T537", at=(320, 140), branch="up", branch_dn=65)
line(sheet, "BZ-534", dn=125, fluid="Benzene", route=[
    p202a["N2"], valve("CV534", "SwingCheckValve", at=(277, 176)),
    valve("HV534", "GateValve", at=(277, 170)), join, minflow, (277, 140), fv507, distillate,
    (360, 140), (360, 235), (150, 235), (150, 87), c202["N3"]], label_at=(300, 227))
line(sheet, "BZ-535", dn=125, fluid="Benzene", route=[
    p202b["N2"], valve("CV535", "SwingCheckValve", at=(325, 176)),
    valve("HV535", "GateValve", at=(325, 170)), (325, 164), join.branch], label_at=(338, 168))
line(sheet, "BZ-536", dn=40, fluid="Benzene", route=[
    minflow.branch, valve("HV536", "GlobeValve", at=(268, 156)), (262, 156), (262, 106),
    v202["N5"]], label_at=(270, 128))
lv506 = valve("LV506", "GlobeValve", tag="LV-506", at=(320, 115))
line(sheet, "BZ-537", dn=65, fluid="Benzene", route=[
    distillate.branch, lv506, (320, 90), e207["T1"]], label_at=(310, 78))

# ---- product cooler E-207 and benzene product to storage
line(sheet, "BZ-121", dn=65, fluid="Benzene", route=[
    e207["T2"], (385, 90),
    offpage("out", at=(385, BOTTOM), note="to benzene storage (B/L)", rotation=90,
            note_at=(368, 252))],
    label_at=(375, 170))
line(sheet, "CWS-545", dn=100, fluid="Cooling water", route=[
    offpage("in", at=(338, TOP), note="from CW supply, P-08", rotation=90, note_at=(318, 9)),
    e207["S1"]], label_at=(328, 60))
e207_relief = tee("T547", at=(352, 50), branch="right", branch_dn=25)
line(sheet, "CWR-546", dn=100, fluid="Cooling water", route=[
    e207["S2"], e207_relief,
    offpage("out", at=(352, TOP), note="to CW return, P-08", rotation=270, note_at=(372, 9))],
    label_at=(361, 30))
psv516 = valve("PSV516", "GlobeValve", tag="PSV-516", at=(370, 38))
line(sheet, "CWR-547", dn=25, fluid="Cooling water", route=[
    e207_relief.branch, (370, 50), psv516,
    offpage("out", at=(370, 22), note="to atmosphere (safe location)", rotation=270,
            note_at=(394, 28))],
    label_at=(382, 44))

# ---- reboiler E-204 (thermosyphon) on LP steam, condensate to the header
line(sheet, "TO-538", dn=200, fluid="Toluene / biphenyl", route=[
    c202["N5"], (72, 180), e204["T1"]], label_at=(96, 186))
line(sheet, "PG-539", dn=500, fluid="Toluene / biphenyl (two-phase)", route=[
    e204["T2"], (72, 160), c202["N6"]], label_at=(96, 154))
tv502 = valve("TV502", "GlobeValve", tag="TV-502", at=(35, 140))
line(sheet, "LS-540", dn=250, fluid="LP steam", route=[
    offpage("in", at=(LEFT, 140), note="from LP steam header, P-08", note_at=(30, 148)),
    tv502, (58, 140), e204["S1"]], label_at=(45, 132))
line(sheet, "CD-541", dn=50, fluid="Condensate", route=[
    e204["S2"], valve("ST541", "SteamTrap", at=(58, 200)), (58, 225),
    offpage("out", at=(LEFT, 225), note="to condensate header, P-08", rotation=180,
            note_at=(32, 219))],
    label_at=(45, 210))

# ---- bottoms to C-203 (P-06) on the sump level
lv508 = valve("LV508", "GlobeValve", tag="LV-508", at=(130, 222))
line(sheet, "TO-122", dn=50, fluid="Toluene / biphenyl", route=[
    c202["N4"], lv508,
    offpage("out", at=(130, BOTTOM), note="to C-203, P-06", rotation=90, note_at=(112, 252))],
    label_at=(140, 242))

# ---- drains to the closed drain system
line(sheet, "DR-551", dn=50, fluid="Drain", route=[
    c202["N10"], valve("HV551", "GateValve", at=(136, 199)),
    offpage("out", at=(136, 206), note="to drain", rotation=90,
            note_at=(141, 213))], labels=False)
line(sheet, "DR-552", dn=50, fluid="Drain", route=[
    v202["N7"], valve("HV552", "GateValve", at=(232, 121)),
    offpage("out", at=(232, 128), note="to drain", rotation=90,
            note_at=(222, 131))], labels=False)

# ---- relief valves
make_safety_valve(sheet, "PSV514", label_at=(88, 60))
make_safety_valve(sheet, "PSV515", label_at=(143, 27))
make_safety_valve(sheet, "PSV516", label_at=(386, 36))

# ---- instruments
instrument(sheet, "TIC-502", at=(95, 122), sensing=c202["N9"], signal_to=tv502,
           signal_points=[(35, 122)])
instrument(sheet, "PI-503", at=(148, 72), sensing="Line_PG530_S1", sensing_at=(148, 60))
instrument(sheet, "PIC-504", at=(265, 25), sensing="Line_FL549_S2", sensing_at=(250, 40),
           signal_to=pv504)
instrument(sheet, "LIC-506", at=(290, 95), sensing=v202["N6"], signal_to=lv506,
           signal_points=[(305, 95), (305, 115)])
instrument(sheet, "FIC-507", at=(295, 125), sensing="Line_BZ534_S3", sensing_at=(288, 140),
           signal_to=fv507)
instrument(sheet, "LIC-508", at=(95, 210), sensing=c202["N8"], signal_to=lv508,
           signal_points=[(95, 222)])
instrument(sheet, "TI-509", at=(398, 120), sensing="Line_BZ121_S1", sensing_at=(385, 120))
instrument(sheet, "AI-510", at=(398, 150), sensing="Line_BZ121_S1", sensing_at=(385, 150))
instrument(sheet, "FI-511", at=(398, 180), sensing="Line_BZ121_S1", sensing_at=(385, 180))
instrument(sheet, "LZ-512", at=(200, 115), sensing=v202["N4"])

note(sheet, "TIC-502: tray temperature on the LP steam TV-502 (Q7). PIC-504: V-202 pressure on the vent "
     "PV-504; PCV-505 self-acting nitrogen pad. FIC-507: reflux (R 2.18, D-014)", at=(20, 262))
note(sheet, "LIC-506: V-202 level on the distillate LV-506 through E-207. LZ-512: low-low stops "
     "P-202A/B (C&E I-501). HV-536: minimum flow. AI-510: benzene purity (D-002)", at=(20, 269))
note(sheet, "PSV-514: C-202, E-203 process side and V-202 (fire, CW failure); PSV-515, PSV-516: E-203 "
     "and E-207 CW sides blocked in (D-025)", at=(20, 276))

save(sheet, target)
