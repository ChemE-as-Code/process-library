"""P-401 four-effect evaporator E-401 (provenance script; the XML is the source).

    cheme sheet new P-401
    cheme run --fmt pid/P-401.xml scripts/draft_P-401.py pid/P-401.xml

Forward feed through the falling-film effects E-401A to D, each with its circulation and transfer
pump P-403x; LP steam to E-401A on FIC-4001, vapour of each effect heats the next; the last
effect's vapour to the surface condenser E-402; condensates to the receiver V-401 under the
liquid-ring vacuum pumps K-401A/B, condensate pumps P-401A/B; concentrate by P-402A/B on DIC-4002
to the esterifier (D-008, D-025, D-039).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import (
    Nozzle,
    Sheet,
    equipment,
    instrument,
    line,
    note,
    offpage,
    tee,
    valve,
)

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-401.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
LEFT, RIGHT, TOP, BOTTOM = 14, 406, 14, 243
Y_T, Y_VAP, Y_RIS, Y_HDR = 120, 50, 60, 177
CX = {"A": 55, "B": 135, "C": 215, "D": 295}
VAP = {"A": "600-VP-4003", "B": "800-VP-4004", "C": "1000-VP-4005", "D": "1400-VP-4006"}
VDN = {"A": 600, "B": 800, "C": 1000, "D": 1400}

E, P, TR = {}, {}, {}
for s, cx in CX.items():
    E[s] = equipment(sheet, "ThinFilmEvaporator", f"E-401{s}", shape="THIN_FILM_EVAPORATOR_SHAPE", at=(cx, 90),
                     scale=1.6, label_at=(cx, 82),
                     nozzles=[Nozzle("V", (-6, -20), VDN[s]), Nozzle("F", (6, -20), 150),
                              Nozzle("S", (-16, -10), 250 if s == "A" else VDN[chr(ord(s) - 1)]),
                              Nozzle("C", (-16, 14), {"A": 50, "B": 100}.get(s, 80)), Nozzle("B", (0, 20), 200), Nozzle("L1", (16, 0))])
    P[s] = equipment(sheet, "CentrifugalPump", f"P-403{s}", shape=PUMP, at=(cx + 30, 140), label_at=(cx + 30, 151),
                     nozzles=[Nozzle("N1", (-7.5, 0), 200), Nozzle("N2", (0, -7.5), 150)])

# ---- Circulation: sump, suction tee (feed or transfer in), pump, riser to the top ----
TS, TP = {}, None
for s, cx in CX.items():
    TS[s] = tee(f"SUC_{s}", at=(cx, Y_T), branch="left", branch_dn=100 if s != "A" else 150)
    route = [E[s]["B"], TS[s]]
    if s == "D":
        TP = tee("PROD_T", at=(cx, 131), branch="left", branch_dn=80)
        route.append(TP)
    line(sheet, f"200-CL-4012{s}", dn=200, fluid="CL", labels=False, route=[*route, (cx, 140), P[s]["N1"]])
    if s != "D":
        TR[s] = tee(f"RIS_{s}", at=(cx + 30, Y_T), branch="right", branch_dn=100)
        rr = [P[s]["N2"], TR[s]]
    else:
        rr = [P[s]["N2"]]
    line(sheet, f"150-CL-4011{s}", dn=150, fluid="CL", labels=False,
         route=[*rr, (cx + 30, Y_RIS), (cx + 6, Y_RIS), E[s]["F"]])

# ---- Feed, forward transfers with the sump level loops ----
feed = line(sheet, "150-CL-3022", dn=150, fluid="CL", label_at=(30, Y_T + 7), route=[
    offpage("in", at=(LEFT, Y_T), note="From P-306A/B (P-301)", note_at=(30, Y_T - 4)), TS["A"].branch])
LV = {}
for s, n in (("A", "B"), ("B", "C"), ("C", "D")):
    cx = CX[s]
    LV[s] = valve(f"LV4011{s}", "GlobeValve", at=(cx + 50, Y_T), tag=f"LV-4011{s}")
    line(sheet, f"100-CL-4013{s}", dn=100, fluid="CL", label_at=(cx + 45, Y_T + 7),
         route=[TR[s].branch, LV[s], TS[n].branch])
    instrument(sheet, f"LIC-4011{s}", at=(cx + 42, 98), sensing=E[s]["L1"], signal_to=LV[s])

# ---- Steam, vapour cascade, condensates ----
fv = valve("FV4001", "GlobeValve", at=(24, 80), tag="FV-4001")
steam = line(sheet, "250-LS-4001", dn=250, fluid="LS", labels=False, route=[
    offpage("in", at=(LEFT, 80), note="LP steam", note_at=(24, 87)), fv, E["A"]["S"]])
instrument(sheet, "FIC-4001", at=(34, 66), sensing=steam, sensing_at=(34, 80), signal_to=fv)
line(sheet, "50-CD-4002", dn=50, fluid="CD", labels=False, route=[
    E["A"]["C"], valve("E401A_ST", "SteamTrap", at=(28, 104)),
    offpage("out", at=(LEFT, 104), note="LP condensate", note_at=(24, 100))])
for s, n in (("A", "B"), ("B", "C"), ("C", "D")):
    cx = CX[s]
    line(sheet, VAP[s], dn=VDN[s], fluid="VP", label_at=(cx + 27, Y_VAP - 5), route=[
        E[s]["V"], (cx - 6, Y_VAP), (cx + 60, Y_VAP), (cx + 60, 80), E[n]["S"]])

e402 = equipment(sheet, "TubularHeatExchanger", "E-402", shape="HEAT_EXCHANGER_SHAPE", at=(350, 80), scale=1.5,
                 label_at=(336, 96),
                 nozzles=[Nozzle("N1", (0, -11.25), 1400), Nozzle("N2", (0, 11.25), 150), Nozzle("C1", (11, -6), 500),
                          Nozzle("C2", (11, 6), 500)])
vap_d = line(sheet, VAP["D"], dn=1400, fluid="VP", label_at=(322, Y_VAP - 5), route=[
    E["D"]["V"], (289, Y_VAP), (350, Y_VAP), e402["N1"]])
instrument(sheet, "PI-4003", at=(338, 38), sensing=vap_d, sensing_at=(338, Y_VAP))
line(sheet, "500-CW-4023", dn=500, fluid="CW", labels=False, route=[
    offpage("in", at=(372, TOP), note="CW", note_at=(366, 20)), (372, 74), e402["C1"]])
line(sheet, "500-CW-4024", dn=500, fluid="CW", labels=False, route=[
    e402["C2"], (384, 86), offpage("out", at=(384, TOP), note="CWR", note_at=(392, 20))])

v401 = equipment(sheet, "Vessel", "V-401", shape=VESSEL, at=(350, 185), label_at=(350, 185),
                 nozzles=[Nozzle("N1", (0, -14.3), 150), Nozzle("N4", (-10, -8), 100), Nozzle("N3", (10, -10), 100),
                          Nozzle("N2", (0, 14.3), 150), Nozzle("L1", (10, 8))])
line(sheet, "150-PC-4017", dn=150, fluid="PC", label_at=(362, 130), route=[e402["N2"], v401["N1"]])
TC = {s: tee(f"HDR_{s}", at=(CX[s] - 22, Y_HDR), branch="up", branch_dn=80) for s in ("C", "D")}
line(sheet, "100-PC-4016", dn=100, fluid="PC", label_at=(160, Y_HDR + 7), route=[
    E["B"]["C"], (CX["B"] - 22, 104), (CX["B"] - 22, Y_HDR), TC["C"], TC["D"], (340, Y_HDR), v401["N4"]])
for s in ("C", "D"):
    line(sheet, f"80-PC-4016{s}", dn=80, fluid="PC", labels=False, route=[
        E[s]["C"], (CX[s] - 22, 104), TC[s].branch])

# ---- Vacuum: K-401A/B on V-401 ----
ka = equipment(sheet, "Compressor", "K-401A", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(390, 152), label_at=(390, 142),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
kb = equipment(sheet, "Compressor", "K-401B", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(390, 175), label_at=(390, 186),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
t_k = tee("VA_T", at=(372, 175), branch="up", branch_dn=100)
line(sheet, "100-VA-4020", dn=100, fluid="VA", labels=False, route=[v401["N3"], t_k, kb["N1"]])
line(sheet, "100-VA-4020", id="Line_VA_A", dn=100, fluid="VA", labels=False, route=[t_k.branch, (372, 152), ka["N1"]])
for k, eq, y in (("4021", ka, 152), ("4022", kb, 175)):
    line(sheet, f"80-VT-{k}", dn=80, fluid="VT", labels=False, route=[
        eq["N2"], offpage("out", at=(402, y), note="atm.", note_at=(400, y - 4))])

# ---- Condensate pumps P-401A/B ----
pa = equipment(sheet, "CentrifugalPump", "P-401A", shape=PUMP, at=(365, 215), label_at=(365, 205),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (7.5, 0), 125)])
pb = equipment(sheet, "CentrifugalPump", "P-401B", shape=PUMP, at=(365, 235), label_at=(365, 245),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (7.5, 0), 125)])
t_cs = tee("PC_TS", at=(350, 215), branch="right", branch_dn=150)
line(sheet, "150-PC-4018", dn=150, fluid="PC", labels=False, route=[
    v401["N2"], valve("V401_HV", "BallValve", at=(350, 206)), t_cs, (350, 235), pb["N1"]])
line(sheet, "150-PC-4018", id="Line_PCS_A", dn=150, fluid="PC", labels=False, route=[t_cs.branch, pa["N1"]])
t_cd = tee("PC_TD", at=(385, 215), branch="down", branch_dn=125)
lv4 = valve("LV4004", "GlobeValve", at=(395, 215), tag="LV-4004")
line(sheet, "125-PC-4019", dn=125, fluid="PC", labels=False, route=[
    pa["N2"], valve("P401A_NR", "CheckValve", at=(377, 215)), t_cd, lv4,
    offpage("out", at=(RIGHT, 215), note="To WWT", note_at=(399, 221))])
line(sheet, "125-PC-4019", id="Line_PCD_B", dn=125, fluid="PC", label_at=(397, 228), route=[
    pb["N2"], valve("P401B_NR", "CheckValve", at=(377, 235)), (385, 235), t_cd.branch])
instrument(sheet, "LIC-4004", at=(395, 200), sensing=v401["L1"], signal_to=lv4)

# ---- Concentrate: P-402A/B on DIC-4002 to the esterifier ----
qa = equipment(sheet, "CentrifugalPump", "P-402A", shape=PUMP, at=(300, 215), label_at=(300, 205),
               nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (7.5, 0), 65)])
qb = equipment(sheet, "CentrifugalPump", "P-402B", shape=PUMP, at=(300, 235), label_at=(300, 245),
               nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (7.5, 0), 65)])
t_ps = tee("LA_TS", at=(280, 215), branch="right", branch_dn=80)
line(sheet, "80-CL-4014", dn=80, fluid="CL", label_at=(291, 160), route=[
    TP.branch, (280, 131), t_ps, (280, 235), qb["N1"]])
line(sheet, "80-CL-4014", id="Line_LAS_A", dn=80, fluid="CL", labels=False, route=[t_ps.branch, qa["N1"]])
dv = valve("DV4002", "GlobeValve", at=(318, 224), tag="DV-4002")
t_pd = tee("LA_TD", at=(318, 235), branch="left", branch_dn=65)
prod = line(sheet, "65-CL-4015", dn=65, fluid="CL", label_at=(334, 238), route=[
    qa["N2"], valve("P402A_NR", "CheckValve", at=(311, 215)), (318, 215), dv, t_pd,
    offpage("out", at=(318, BOTTOM), note="To R-401 (P-402)", note_at=(300, 248))])
line(sheet, "65-CL-4015", id="Line_LAD_B", dn=65, fluid="CL", labels=False, route=[
    qb["N2"], valve("P402B_NR", "CheckValve", at=(311, 235)), t_pd.branch])
instrument(sheet, "DIC-4002", at=(334, 212), sensing=prod, sensing_at=(318, 229), signal_to=dv)

# ---- Notes ----
note(sheet, "Four-effect falling-film evaporator, forward feed (D-008, D-039): 97 % of the water off, 81 t/h; effects at about "
     "1.0, 0.6, 0.3 and 0.12 bar(a) (ASSUMED); each effect's vapour heats the next.", at=(10, 253), size=2.0)
note(sheet, "FIC-4001 sets the LP steam (13.7 MW, Q4); DIC-4002 draws the concentrate at 71 wt% lactic acid (D-008); "
     "LIC-4011A to C hold the sumps on the forward transfers.", at=(10, 257), size=2.0)
note(sheet, "Condensates of E-401B to D and E-402 (14.5 MW, Q5) to V-401 under K-401A/B; P-401A/B on LIC-4004 to WWT (S15).",
     at=(10, 261), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
