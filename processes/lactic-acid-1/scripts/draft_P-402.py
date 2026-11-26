"""P-402 esterification R-401 and ester column C-401 (provenance script; the XML is the source).

    cheme sheet new P-402
    cheme run --fmt pid/P-402.xml scripts/draft_P-402.py pid/P-402.xml

The concentrate (P-401) and the ethanol recycle and make-up (P-403) mix and are heated in E-411
on LP steam (TIC-4101), then enter R-401, a reactive distillation column on Amberlyst-15
packing. Its vapour goes on PIC-4102 to C-401, its sump liquid by P-411A/B on LIC-4104 to C-401.
C-401 runs at 20 kPa(a): thermosyphon reboiler E-421 on MP steam (TIC-4202), condenser E-422,
reflux drum V-421 under the liquid-ring pumps K-421A/B (PIC-4201), P-421A/B for the reflux
(FIC-4205) and the overhead to C-402 (LIC-4204); the residue leaves hot by P-422A/B on LIC-4203
(D-008, D-009, D-041).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Nozzle, Sheet, equipment, instrument, line, note, offpage, tee, valve

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-402.xml")
blank = Path("build/P-402_blank.xml")      # the empty sheet of `cheme sheet new`, kept for reruns
if not blank.exists():
    Sheet.load(target).save(blank, fmt=False)
sheet = Sheet.load(blank)

PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_SHAPE"
LEFT, RIGHT, TOP, BOTTOM = 14, 406, 14, 243


def pump(tag, at, suction=(-7.5, 0), discharge=(7.5, 0), dn=(100, 80), label_at=None):
    return equipment(sheet, "CentrifugalPump", tag, shape=PUMP, at=at, label_at=label_at,
                     nozzles=[Nozzle("N1", suction, dn[0]), Nozzle("N2", discharge, dn[1])])


# ---- Feed: concentrate and ethanol, heater E-411 ----
e411 = equipment(sheet, "TubularHeatExchanger", "E-411", shape=HX, at=(60, 60), scale=1.2, label_at=(46, 72),
                 nozzles=[Nozzle("P1", (-9, 0), 65), Nozzle("P2", (9, 0), 80), Nozzle("S", (0, -8), 50),
                          Nozzle("C", (0, 8), 25)])
t_mix = tee("MIX_T", at=(35, 60), branch="down", branch_dn=50)
line(sheet, "65-CL-4015", dn=65, fluid="CL", labels=False, route=[
    offpage("in", at=(LEFT, 60), note="From P-402A/B (P-401)", note_at=(20, 53)), t_mix, e411["P1"]])
line(sheet, "50-ET-4101", dn=50, fluid="ET", label_at=(24, 80), route=[
    offpage("in", at=(LEFT, 90), note="Ethanol from P-403", note_at=(16, 95)), (35, 90), t_mix.branch])
tv41 = valve("TV4101", "GlobeValve", at=(60, 32), tag="TV-4101")
line(sheet, "50-LS-4103", dn=50, fluid="LS", labels=False, route=[
    offpage("in", at=(60, TOP), note="LP steam", note_at=(70, 20)), tv41, e411["S"]])
line(sheet, "25-CD-4104", dn=25, fluid="CD", labels=False, route=[
    e411["C"], valve("E411_ST", "SteamTrap", at=(60, 82)), (60, 110),
    offpage("out", at=(LEFT, 110), note="LP condensate", note_at=(16, 115))])

# ---- R-401 reactive distillation (C-401 first: R-401's lines end on it) ----
c401 = equipment(sheet, "ProcessColumn", "C-401", shape="COLUMN_TRAYS_SHAPE", at=(250, 105), scale=(1.2, 3.0),
                 label_at=(224, 125),
                 nozzles=[Nozzle("V", (0, -75), 1000), Nozzle("RV", (-6, -75), 150), Nozzle("F1", (-12, -35), 150),
                          Nozzle("F2", (-12, -5), 80), Nozzle("RF", (12, -60), 80), Nozzle("T1", (12, 35)),
                          Nozzle("L1", (-12, 65)), Nozzle("RB", (12, 57), 600), Nozzle("B", (0, 75), 200)])
r401 = equipment(sheet, "ProcessColumn", "R-401", shape="COLUMN_SHAPE", at=(130, 110), scale=(1.0, 3.0),
                 label_at=(106, 140), markers=[("COLUMN_PACKED_BED_SHAPE", -10, 4)],
                 nozzles=[Nozzle("V", (0, -75), 150), Nozzle("RV", (-6, -75), 80), Nozzle("F", (-10, -50), 80),
                          Nozzle("T1", (10, -10)), Nozzle("L1", (10, 65)), Nozzle("B", (0, 75), 100)])
feed = line(sheet, "80-PL-4102", dn=80, fluid="PL", label_at=(95, 70), route=[e411["P2"], r401["F"]])
instrument(sheet, "TIC-4101", at=(88, 42), sensing=feed, sensing_at=(88, 60), signal_to=tv41)
pv41 = valve("PV4102", "GlobeValve", at=(180, 25), tag="PV-4102")
vap = line(sheet, "150-VP-4105", dn=150, fluid="VP", label_at=(195, 33), route=[
    r401["V"], (130, 25), pv41, (215, 25), (215, 70), c401["F1"]])
instrument(sheet, "PIC-4102", at=(160, 40), sensing=vap, sensing_at=(145, 25), signal_to=pv41)
line(sheet, "80-RV-4106", dn=80, fluid="RV", labels=False, route=[
    r401["RV"], valve("PSV4105", "CheckValve", at=(124, 24), tag="PSV-4105"),   # no safety valve class (D-031)
    offpage("out", at=(124, TOP))])
instrument(sheet, "TI-4103", at=(156, 100), sensing=r401["T1"])

# ---- P-411A/B: R-401 sump to C-401 on LIC-4104 ----
pa = pump("P-411A", (150, 212), label_at=(150, 203))
pb = pump("P-411B", (150, 232), label_at=(150, 243))
t_rs = tee("R401_TS", at=(130, 212), branch="right", branch_dn=100)
line(sheet, "100-PL-4107", dn=100, fluid="PL", labels=False, route=[r401["B"], t_rs, (130, 232), pb["N1"]])
line(sheet, "100-PL-4107", id="Line_PL4107_A", dn=100, fluid="PL", labels=False, route=[t_rs.branch, pa["N1"]])
t_rd = tee("R401_TD", at=(172, 212), branch="down", branch_dn=80)
lv41 = valve("LV4104", "GlobeValve", at=(185, 212), tag="LV-4104")
line(sheet, "80-PL-4108", dn=80, fluid="PL", label_at=(188, 150), route=[
    pa["N2"], valve("P411A_NR", "CheckValve", at=(164, 212)), t_rd, lv41, (200, 212), (200, 100), c401["F2"]])
line(sheet, "80-PL-4108", id="Line_PL4108_B", dn=80, fluid="PL", labels=False, route=[
    pb["N2"], valve("P411B_NR", "CheckValve", at=(164, 232)), (172, 232), t_rd.branch])
instrument(sheet, "LIC-4104", at=(160, 175), sensing=r401["L1"], signal_to=lv41, signal_points=[(185, 175)])

# ---- C-401 ester column at 20 kPa(a) ----
line(sheet, "150-RV-4206", dn=150, fluid="RV", labels=False, route=[
    c401["RV"], valve("PSV4206", "CheckValve", at=(244, 22), tag="PSV-4206"),
    offpage("out", at=(244, TOP))])
e422 = equipment(sheet, "TubularHeatExchanger", "E-422", shape=HX, at=(330, 40), scale=1.5, label_at=(316, 58),
                 nozzles=[Nozzle("N1", (0, -11.25), 1000), Nozzle("N2", (0, 11.25), 150), Nozzle("C1", (11, -6), 500),
                          Nozzle("C2", (11, 6), 500)])
line(sheet, "1000-VP-4202", dn=1000, fluid="VP", label_at=(290, 12), route=[c401["V"], (250, 20), (330, 20), e422["N1"]])
line(sheet, "500-CW-4203", dn=500, fluid="CW", labels=False, route=[
    offpage("in", at=(345, TOP), note="CW", note_at=(347, 24)), (345, 34), e422["C1"]])
line(sheet, "500-CW-4204", dn=500, fluid="CW", labels=False, route=[
    e422["C2"], (360, 46), offpage("out", at=(360, TOP), note="CWR", note_at=(367, 26))])

v421 = equipment(sheet, "Vessel", "V-421", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(345, 90), rotation=90,
                 label_at=(345, 90),
                 nozzles=[Nozzle("N1", (-15, -10), 150), Nozzle("P1", (-4, -10)), Nozzle("N3", (8, -10), 100),
                          Nozzle("N2", (0, 10), 150), Nozzle("L1", (15, 0))])
line(sheet, "150-PL-4205", dn=150, fluid="PL", labels=False, route=[e422["N2"], v421["N1"]])

# ---- Vacuum: K-421A/B on V-421, PIC-4201 ----
ka = equipment(sheet, "Compressor", "K-421A", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(392, 58), label_at=(392, 48),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
kb = equipment(sheet, "Compressor", "K-421B", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(392, 78), label_at=(392, 89),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
pv42 = valve("PV4201", "GlobeValve", at=(353, 70), tag="PV-4201")
t_k = tee("VA_T", at=(372, 58), branch="down", branch_dn=100)
line(sheet, "100-VA-4206", dn=100, fluid="VA", labels=False, route=[v421["N3"], pv42, (353, 58), t_k, ka["N1"]])
line(sheet, "100-VA-4206", id="Line_VA4206_B", dn=100, fluid="VA", labels=False, route=[t_k.branch, (372, 78), kb["N1"]])
line(sheet, "80-VT-4207", dn=80, fluid="VT", labels=False, route=[ka["N2"], offpage("out", at=(RIGHT, 58))])
line(sheet, "80-VT-4208", dn=80, fluid="VT", labels=False, route=[kb["N2"], offpage("out", at=(RIGHT, 78))])
instrument(sheet, "PIC-4201", at=(341, 68), sensing=v421["P1"], signal_to=pv42)

# ---- P-421A/B: reflux on FIC-4205, overhead to C-402 on LIC-4204 ----
qa = pump("P-421A", (360, 115), dn=(150, 100), label_at=(360, 106))
qb = pump("P-421B", (360, 135), dn=(150, 100), label_at=(360, 146))
t_qs = tee("V421_TS", at=(345, 115), branch="right", branch_dn=150)
line(sheet, "150-PL-4209", dn=150, fluid="PL", labels=False, route=[v421["N2"], t_qs, (345, 135), qb["N1"]])
line(sheet, "150-PL-4209", id="Line_PL4209_A", dn=150, fluid="PL", labels=False, route=[t_qs.branch, qa["N1"]])
t_qd = tee("V421_TD", at=(382, 115), branch="down", branch_dn=100)
t_rf = tee("RF_T", at=(395, 150), branch="left", branch_dn=80)
lv42 = valve("LV4204", "GlobeValve", at=(395, 190), tag="LV-4204")
line(sheet, "100-PL-4210", dn=100, fluid="PL", label_at=(384, 210), route=[
    qa["N2"], valve("P421A_NR", "CheckValve", at=(374, 115)), t_qd, (395, 115), t_rf, lv42,
    offpage("out", at=(395, BOTTOM), note="To C-402 (P-403)", note_at=(368, 249))])
line(sheet, "100-PL-4210", id="Line_PL4210_B", dn=100, fluid="PL", labels=False, route=[
    qb["N2"], valve("P421B_NR", "CheckValve", at=(374, 135)), (382, 135), t_qd.branch])
fv42 = valve("FV4205", "GlobeValve", at=(370, 150), tag="FV-4205")
reflux = line(sheet, "80-PL-4211", dn=80, fluid="PL", label_at=(296, 100), route=[
    t_rf.branch, fv42, (285, 150), (285, 45), c401["RF"]])
instrument(sheet, "FIC-4205", at=(350, 160), sensing=reflux, sensing_at=(350, 150), signal_to=fv42)
instrument(sheet, "LIC-4204", at=(378, 96), sensing=v421["L1"], signal_to=lv42, signal_points=[(386, 96), (386, 190)])

# ---- Reboiler E-421 on MP steam (TIC-4202), bottoms and residue ----
e421 = equipment(sheet, "TubularHeatExchanger", "E-421", shape=HX, at=(295, 180), scale=1.5, label_at=(276, 184),
                 nozzles=[Nozzle("N1", (0, -11.25), 600), Nozzle("N2", (0, 11.25), 200), Nozzle("S", (11, -6), 300),
                          Nozzle("C", (11, 6), 80)])
line(sheet, "600-VP-4212", dn=600, fluid="VP", labels=False, route=[e421["N1"], (295, 162), c401["RB"]])
tv42 = valve("TV4202", "GlobeValve", at=(318, 174), tag="TV-4202")
line(sheet, "300-MS-4215", dn=300, fluid="MS", labels=False, route=[
    offpage("in", at=(330, BOTTOM), note="MP steam", note_at=(326, 249)), (330, 174), tv42, e421["S"]])
line(sheet, "80-CD-4216", dn=80, fluid="CD", labels=False, route=[
    e421["C"], (312, 186), valve("E421_ST", "SteamTrap", at=(312, 200)),
    offpage("out", at=(312, BOTTOM), note="MPC", note_at=(316, 249))])
instrument(sheet, "TIC-4202", at=(274, 140), sensing=c401["T1"], signal_to=tv42, signal_points=[(318, 140)])

ra = pump("P-422A", (275, 216), dn=(80, 40), label_at=(275, 204))
rb = pump("P-422B", (275, 234), dn=(80, 40), label_at=(275, 247))
t_b = tee("C401_TB", at=(260, 195), branch="down", branch_dn=80)
t_s = tee("C401_TS", at=(260, 216), branch="right", branch_dn=80)
line(sheet, "200-PL-4213", dn=200, fluid="PL", labels=False, route=[c401["B"], (250, 195), t_b, (295, 195), e421["N2"]])
line(sheet, "80-RS-4217", dn=80, fluid="RS", labels=False, route=[t_b.branch, t_s, (260, 234), rb["N1"]])
line(sheet, "80-RS-4217", id="Line_RS4217_A", dn=80, fluid="RS", labels=False, route=[t_s.branch, ra["N1"]])
t_xd = tee("RES_T", at=(295, 234), branch="up", branch_dn=40)
line(sheet, "40-RS-4214", dn=40, fluid="RS", labels=False, route=[
    rb["N2"], valve("P422B_NR", "CheckValve", at=(289, 234)), t_xd, (303, 234),
    offpage("out", at=(303, BOTTOM), note="Residue to AD", note_at=(282, 253))])
line(sheet, "40-RS-4214", id="Line_RS4214_A", dn=40, fluid="RS", labels=False, route=[
    ra["N2"], valve("P422A_NR", "CheckValve", at=(289, 216)), (295, 216), t_xd.branch])
instrument(sheet, "LIC-4203", at=(224, 170), sensing=c401["L1"])
note(sheet, "LIC-4203: P-422A/B speed", at=(206, 177), size=2.0)

# ---- Notes ----
note(sheet, "Esterification (D-008, D-041): R-401 reactive distillation on Amberlyst-15 packing at about 351 K, 98 % conversion "
     "(ASSUMED); ethanol to lactic acid ratio held by the make-up on P-403.", at=(10, 256), size=2.0)
note(sheet, "C-401 at 20 kPa(a), reflux ratio 1 (ASSUMED, D-009); overhead ethyl lactate, ethanol and water to C-402; residue "
     "about 3.1 t/h at about 423 K, sent hot (traced) to anaerobic digestion off-plot.", at=(10, 260), size=2.0)
note(sheet, "Relief valves PSV-4105 and PSV-4206 and the vacuum pump exhausts to the vent header (ethanol, D-012); "
     "flammable area for area classification.", at=(10, 264), size=2.0)

sheet.save(target)
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
