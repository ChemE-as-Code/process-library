"""P-204 CIP station and SIP steam (provenance script; the XML is the source).

    cheme sheet new P-204
    cheme run --fmt pid/P-204.xml scripts/draft_P-204.py pid/P-204.xml

CIP tanks T-221 (caustic), T-222 (acid), T-223 (fresh water), T-224 (recovered rinse) on a common
suction header to the supply pumps P-221A/B, the LP-steam heater E-221 on TIC-2201, FIC-2202 and the
supply header 100-CS-2015; the return header 150-CR-2017 with conductivity and temperature to the
self-priming return pumps P-222A/B and the recovery header to T-221, T-222, T-224 or the drain;
caustic 50 wt% T-225 and P-223; SIP steam through F-231A/B and PV-2205 into 150-SS-2019 (D-021, D-037).
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-204.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
LEFT, RIGHT, TOP = 14, 406, 14
Y_SUC, Y_REC, Y_SUP, Y_RET, Y_SS = 120, 22, 100, 190, 226
W, H = 16, 22.9                                          # tank half width and half height (scale 1.6)

# ---- CIP tanks ----
TANKS = {}
for tag, cx in (("T-221", 50), ("T-222", 100), ("T-223", 150), ("T-224", 200)):
    TANKS[tag] = equipment(sheet, "Tank", tag, shape=VESSEL, at=(cx, 70), scale=(1.6, 1.6),
                           label_at=(cx, 66),
                           nozzles=[Nozzle("N1", (-0.4 * W, -H), 100 if tag == "T-221" else 80), Nozzle("N4", (0.4 * W, -H), 50),
                                    Nozzle("N2", (0, H), 100 if tag == "T-221" else 80),
                                    Nozzle("N5", (W, 0.5 * H), 25)])
for i, (tag, cx) in enumerate((("T-221", 50), ("T-222", 100), ("T-223", 150), ("T-224", 200))):
    key = tag.replace("-", "")
    line(sheet, f"50-VT-224{i + 1}", dn=50, fluid="VT", labels=False, route=[
        TANKS[tag]["N4"], offpage("out", at=(cx + 0.4 * W, 38), note="vent", note_at=(cx + 0.4 * W + 7, 38))])

# ---- Supply: suction header, P-221A/B, E-221, FV-2202, supply header ----
pa = equipment(sheet, "CentrifugalPump", "P-221A", shape=PUMP, at=(280, 120), label_at=(280, 133),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 100)])
pb = equipment(sheet, "CentrifugalPump", "P-221B", shape=PUMP, at=(305, 145), label_at=(318, 152),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 100)])
e221 = equipment(sheet, "PlateHeatExchanger", "E-221", shape="PLATE_TYPE_HEAT_EXCHANGER_SHAPE", at=(340, 100), label_at=(326, 90),
                 nozzles=[Nozzle("N1", (-8, 0), 100), Nozzle("N2", (8, 0), 100), Nozzle("S1", (0, -8), 50),
                          Nozzle("S2", (0, 8), 25)])
suc = {tag: tee(f"SUC_{tag.replace('-', '')}", at=(cx, Y_SUC), branch="up", branch_dn=80)
       for tag, cx in (("T-222", 100), ("T-223", 150), ("T-224", 200))}
t_pb = tee("SUC_PB", at=(262, Y_SUC), branch="down", branch_dn=100)
line(sheet, "100-CS-2207", dn=100, fluid="CS", label_at=(232, Y_SUC - 5), route=[
    TANKS["T-221"]["N2"], valve("T221_XV", "BallValve", at=(50, 105)), (50, Y_SUC), *suc.values(), t_pb,
    pa["N1"]])
line(sheet, "100-CS-2207", id="Line_SUC_B", dn=100, fluid="CS", labels=False, route=[
    t_pb.branch, (262, 145), pb["N1"]])
for i, tag in enumerate(("T-222", "T-223", "T-224")):
    cx = suc[tag].at[0]
    line(sheet, f"80-CS-222{i + 1}", dn=80, fluid="CS", labels=False, route=[
        TANKS[tag]["N2"], valve(f"{tag.replace('-', '')}_XV", "BallValve", at=(cx, 105)), suc[tag].branch])
t_dj = tee("DIS_J", at=(305, Y_SUP), branch="down", branch_dn=80)
line(sheet, "100-CS-2208", dn=100, fluid="CS", label_at=(300, Y_SUP - 5), route=[
    pa["N2"], valve("P221A_NR", "CheckValve", at=(280, 106)), (280, Y_SUP), t_dj, e221["N1"]])
line(sheet, "100-CS-2208", id="Line_DIS_B", dn=100, fluid="CS", labels=False, route=[
    pb["N2"], valve("P221B_NR", "CheckValve", at=(305, 131)), t_dj.branch])  # DN 100 like A
fv = valve("FV2202", "GlobeValve", at=(366, Y_SUP), tag="FV-2202")
sup = line(sheet, "100-CS-2015", dn=100, fluid="CS", label_at=(372, Y_SUP + 9), route=[
    e221["N2"], fv, offpage("out", at=(RIGHT, Y_SUP), note="100-CS-2015 to P-203", note_at=(395, Y_SUP + 4))])
tv = valve("TV2201", "GlobeValve", at=(340, 70), tag="TV-2201")
line(sheet, "50-LS-2224", dn=50, fluid="LS", labels=False, route=[
    offpage("in", at=(340, TOP), note="LP steam", note_at=(352, TOP + 3)), tv, e221["S1"]])
line(sheet, "25-CD-2225", dn=25, fluid="CD", labels=False, route=[
    e221["S2"], valve("E221_ST", "SteamTrap", at=(340, 114)), offpage("out", at=(340, 122), note="condensate drain",
                                                                        note_at=(356, 124))])

# ---- Return: return header, P-222A/B, recovery header to the tanks or the drain ----
ra = equipment(sheet, "CentrifugalPump", "P-222A", shape=PUMP, at=(280, Y_RET), label_at=(280, 203),
               nozzles=[Nozzle("N1", (7.5, 0), 150), Nozzle("N2", (0, -7.5), 100)])
rb = equipment(sheet, "CentrifugalPump", "P-222B", shape=PUMP, at=(255, 215), label_at=(240, 222),
               nozzles=[Nozzle("N1", (7.5, 0), 150), Nozzle("N2", (0, -7.5), 100)])
t_rb = tee("RET_PB", at=(300, Y_RET), branch="down", branch_dn=150)
ret = line(sheet, "150-CR-2017", dn=150, fluid="CR", label_at=(360, Y_RET + 6), route=[
    offpage("in", at=(RIGHT, Y_RET), note="150-CR-2017 from P-203", note_at=(388, Y_RET + 4)), t_rb,
    ra["N1"]])
line(sheet, "150-CR-2017", id="Line_RET_B", dn=150, fluid="CR", labels=False, route=[
    t_rb.branch, (300, 215), rb["N1"]])
t_rj = tee("REC_J", at=(255, 170), branch="down", branch_dn=100)
t_dr = tee("REC_DR", at=(230, 170), branch="down", branch_dn=80)
rec = {tag: tee(f"REC_{tag.replace('-', '')}", at=(cx - 0.4 * W, Y_REC), branch="down", branch_dn=80)
       for tag, cx in (("T-224", 200), ("T-222", 100))}
line(sheet, "100-CR-2226", dn=100, fluid="CR", label_at=(172, Y_REC - 8), route=[
    ra["N2"], valve("P222A_NR", "CheckValve", at=(280, 177)), (280, 170), t_rj, t_dr, (222, 170), (222, Y_REC),
    *rec.values(), (43.6, Y_REC), valve("REC_T221", "BallValve", at=(43.6, 34)), TANKS["T-221"]["N1"]])
line(sheet, "100-CR-2226", id="Line_REC_B", dn=100, fluid="CR", labels=False, route=[
    rb["N2"], valve("P222B_NR", "CheckValve", at=(255, 198)), t_rj.branch])
for number, tag in (("80-CR-2227", "T-222"), ("80-CR-2228", "T-224")):
    x = rec[tag].at[0]
    line(sheet, number, dn=80, fluid="CR", labels=False, route=[
        rec[tag].branch, valve(f"REC_{tag.replace('-', '')}_V", "BallValve", at=(x, 34)), TANKS[tag]["N1"]])
line(sheet, "80-CR-2229", dn=80, fluid="CR", labels=False, route=[
    t_dr.branch, valve("REC_DR_V", "BallValve", at=(230, 178)),
    offpage("out", at=(230, 186), note="drain", note_at=(222, 188))])

# ---- Caustic: T-225, P-223 to T-221 and to T-215 (P-201) ----
t225 = equipment(sheet, "Tank", "T-225", shape=VESSEL, at=(50, 200), scale=(1.2, 1.2), label_at=(50, 196),
                 nozzles=[Nozzle("N1", (-12, -8.6), 50), Nozzle("N2", (0, 17.2), 25)])
p223 = equipment(sheet, "CentrifugalPump", "P-223", shape=PUMP, at=(75, 232), label_at=(90, 240),
                 nozzles=[Nozzle("N1", (-7.5, 0), 25), Nozzle("N2", (0, -7.5), 25)])
line(sheet, "50-NA-2235", dn=50, fluid="NA", labels=False, route=[
    offpage("in", at=(LEFT, 191.4), note="NaOH 50 wt%, tanker", note_at=(24, 186)),
    valve("T225_HVF", "BallValve", at=(30, 191.4)), t225["N1"]])
line(sheet, "25-NA-2230", dn=25, fluid="NA", labels=False, route=[
    t225["N2"], valve("T225_HV", "BallValve", at=(50, 224)), (50, 232), p223["N1"]])
t_na = tee("NA_T215", at=(75, 205), branch="right", branch_dn=15)
line(sheet, "25-NA-2231", dn=25, fluid="NA", label_at=(88, 178), route=[
    p223["N2"], valve("P223_NR", "CheckValve", at=(75, 218)), t_na, (75, 81.45), TANKS["T-221"]["N5"]])
line(sheet, "15-NA-2152", dn=15, fluid="NA", labels=False, route=[
    t_na.branch, (110, 205), offpage("out", at=(110, 240), note="To T-215 (P-201)", note_at=(126, 238))])

# ---- Fresh water to T-223 ----
line(sheet, "80-PW-2232", dn=80, fluid="PW", labels=False, route=[
    offpage("in", at=(143.6, TOP), note="Process water", note_at=(126, TOP + 3)),
    valve("T223_HVF", "BallValve", at=(143.6, 34)), TANKS["T-223"]["N1"]])

# ---- SIP steam: F-231A/B, PV-2205, header 150-SS-2019, drip leg ----
fa = equipment(sheet, "Filter", "F-231A", shape="GAS_FILTER_SHAPE", at=(160, 165), scale=0.6, label_at=(172, 160),
               nozzles=[Nozzle("N1", (0, -7), 150), Nozzle("N2", (0, 7), 150), Nozzle("P1", (4, -4)),
                        Nozzle("P2", (4, 4))])
fb = equipment(sheet, "Filter", "F-231B", shape="GAS_FILTER_SHAPE", at=(135, 165), scale=0.6, label_at=(123, 160),
               nozzles=[Nozzle("N1", (0, -7), 150), Nozzle("N2", (0, 7), 150)])
t_ls = tee("LS_TB", at=(135, 150), branch="down", branch_dn=150)
line(sheet, "150-LS-2233", dn=150, fluid="LS", label_at=(104, 145), route=[
    offpage("in", at=(LEFT, 150), note="LP steam 4.5 bar(a)", note_at=(30, 146)),
    valve("LS_HV", "GateValve", at=(30, 150)), t_ls, (160, 150), fa["N1"]])
line(sheet, "150-LS-2233", id="Line_LS_B", dn=150, fluid="LS", labels=False, route=[t_ls.branch, fb["N1"]])
t_sj = tee("SS_TJ", at=(160, 185), branch="left", branch_dn=150)
t_dl = tee("SS_DL", at=(200, Y_SS), branch="down", branch_dn=25)
pv = valve("PV2205", "GlobeValve", at=(160, 205), tag="PV-2205")
ss = line(sheet, "150-SS-2019", dn=150, fluid="SS", label_at=(330, Y_SS + 6), route=[
    fa["N2"], t_sj, pv, (160, Y_SS), t_dl,
    offpage("out", at=(RIGHT, Y_SS), note="150-SS-2019 to P-203", note_at=(384, Y_SS - 4))])
line(sheet, "150-SS-2019", id="Line_SS_B", dn=150, fluid="SS", labels=False, route=[
    fb["N2"], (135, 185), t_sj.branch])
line(sheet, "25-CD-2234", dn=25, fluid="CD", labels=False, route=[
    t_dl.branch, valve("SS_DL_ST", "SteamTrap", at=(200, 231)), offpage("out", at=(200, 237), note="drain",
                                                                         note_at=(209, 239))])

# ---- Instruments ----
instrument(sheet, "TIC-2201", at=(355, 84), sensing=sup, sensing_at=(355, Y_SUP), signal_to=tv)
instrument(sheet, "FIC-2202", at=(380, 84), sensing=sup, sensing_at=(380, Y_SUP), signal_to=fv)
instrument(sheet, "AIT-2203", at=(372, 176), sensing=ret, sensing_at=(372, Y_RET))
instrument(sheet, "TT-2204", at=(350, 176), sensing=ret, sensing_at=(350, Y_RET))
instrument(sheet, "PIC-2205", at=(180, 212), sensing=ss, sensing_at=(180, Y_SS), signal_to=pv)
instrument(sheet, "PDI-2206", at=(178, 170), sensing=fa["P1"])

# ---- Notes ----
note(sheet, "CIP (D-021, D-037): pre-rinse from T-224, NaOH about 2 wt% at 353 K for 30 min from T-221, rinse from "
     "T-223, nitric acid about 1 wt% weekly from T-222, final rinse recovered to T-224; one fermenter at a time "
     "(ASSUMED). AIT-2203 and TT-2204 switch the recovery valves (caustic to T-221, rinse to T-224, else drain).",
     at=(10, 250), size=2.0)
note(sheet, "P-222A/B self-priming, at the low point of the return header below the fermenter rows (S1#9, ASSUMED). "
     "Tank levels, vents and overflows: level transmitters at detail; vents to atmosphere as drawn.",
     at=(10, 256), size=2.0)
note(sheet, "SIP steam (S1#10, ASSUMED): plant LP steam, saturated, dryness 0.95 or better after the header separator "
     "of the utility area, through 1 um sintered filters F-231A/B (duty, standby; PDI-2206), PV-2205 holds 3 barg "
     "in 150-SS-2019; drip legs with traps at the low points; condensate to the drain (D-021).",
     at=(10, 262), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
