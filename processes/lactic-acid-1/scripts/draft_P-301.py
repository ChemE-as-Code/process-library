"""P-301 cell removal, acidulation and gypsum filtration (provenance script; the XML is the source).

    cheme sheet new P-301
    cheme run --fmt pid/P-301.xml scripts/draft_P-301.py pid/P-301.xml

Disc-stack centrifuges S-301A to C (two running) on FIC-3011x, cake hopper V-301 and cake pumps
P-301A/B; acidulation tank R-301 with agitator A-301, 93 wt% acid from T-301 by P-304A/B on
FFIC-3021 (ratio to FT-3020, trimmed by AIC-3024), pump-around P-303A/B through the spiral cooler
E-301 on TIC-3023; slurry pumps P-305A/B to the belt filter S-302, filtrate receiver V-303 with the
liquid-ring vacuum pumps K-301A/B and the filtrate pumps P-306A/B on LIC-3031 (D-007, D-025, D-038).
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-301.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
LEFT, RIGHT, TOP, BOTTOM = 14, 406, 14, 243
Y_FEED, Y_CLAR, Y_CAKE = 40, 100, 118

# ---- Cell removal: S-301A to C, V-301, P-301A/B ----
S = {}
for s, cx in (("A", 50), ("B", 85), ("C", 120)):
    S[s] = equipment(sheet, "Centrifuge", f"S-301{s}", shape="SEPARATOR_SHAPE", at=(cx, 70), label_at=(cx + 4.5, 92),
                     nozzles=[Nozzle("N1", (-4, -12.5), 150), Nozzle("N2", (7.5, -2), 150),
                              Nozzle("N3", (-3, 12.5), 100)])
t_fa = tee("FEED_TA", at=(46, Y_FEED), branch="down", branch_dn=150)
t_fb = tee("FEED_TB", at=(81, Y_FEED), branch="down", branch_dn=150)
fv = {s: valve(f"FV3011{s}", "GlobeValve", at=(cx - 4, 48), tag=f"FV-3011{s}")
      for s, cx in (("A", 50), ("B", 85), ("C", 120))}
feed = line(sheet, "150-BR-2014", dn=150, fluid="BR", label_at=(98, Y_FEED - 9), route=[
    offpage("in", at=(LEFT, Y_FEED), note="From P-203A/B (P-207)", note_at=(32, Y_FEED - 4)),
    t_fa, t_fb, (116, Y_FEED), fv["C"], S["C"]["N1"]])
drop = {"C": feed}
for s, t in (("A", t_fa), ("B", t_fb)):
    drop[s] = line(sheet, f"150-BR-3001{s}", dn=150, fluid="BR", labels=False, route=[t.branch, fv[s], S[s]["N1"]])
for s, cx in (("A", 50), ("B", 85), ("C", 120)):
    instrument(sheet, f"FIC-3011{s}", at=(cx - 16, 54), sensing=drop[s], sensing_at=(cx - 4, 54), signal_to=fv[s])

t_cb = tee("CLAR_TB", at=(97, Y_CLAR), branch="up", branch_dn=150)
t_cc = tee("CLAR_TC", at=(132, Y_CLAR), branch="up", branch_dn=150)

v301 = equipment(sheet, "Vessel", "V-301", shape="VESSEL_CONICAL_ENDS_SHAPE", at=(47, 150), label_at=(30, 150),
                 nozzles=[Nozzle("N1", (0, -12.5), 100), Nozzle("N2", (0, 12.5), 80)])
t_ka = tee("CAKE_TA", at=(47, Y_CAKE), branch="right", branch_dn=100)
t_kb = tee("CAKE_TB", at=(82, Y_CAKE), branch="up", branch_dn=100)
line(sheet, "100-CM-3004A", dn=100, fluid="CM", label_at=(30, 128), route=[S["A"]["N3"], t_ka, v301["N1"]])
line(sheet, "100-CM-3004C", dn=100, fluid="CM", labels=False, route=[S["C"]["N3"], (117, Y_CAKE), t_kb, t_ka.branch])
line(sheet, "100-CM-3004B", dn=100, fluid="CM", labels=False, route=[S["B"]["N3"], t_kb.branch])

ca = equipment(sheet, "RotaryPump", "P-301A", shape="PUMP_PROGRESSIVE_CAVITY_SHAPE", at=(70, 190), label_at=(70, 200),
               nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (7.5, 0), 50)])
cb = equipment(sheet, "RotaryPump", "P-301B", shape="PUMP_PROGRESSIVE_CAVITY_SHAPE", at=(70, 215), label_at=(70, 225),
               nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (7.5, 0), 50)])
t_cs = tee("CM_TS", at=(47, 190), branch="right", branch_dn=80)
line(sheet, "80-CM-3005", dn=80, fluid="CM", label_at=(30, 180), route=[
    v301["N2"], valve("V301_HV", "BallValve", at=(47, 172)), t_cs, (47, 215), cb["N1"]])
line(sheet, "80-CM-3005", id="Line_CMS_A", dn=80, fluid="CM", labels=False, route=[t_cs.branch, ca["N1"]])
t_cd = tee("CM_TD", at=(95, 215), branch="left", branch_dn=50)
line(sheet, "50-CM-3006", dn=50, fluid="CM", label_at=(106, 205), route=[
    ca["N2"], valve("P301A_NR", "CheckValve", at=(86, 190)), (95, 190), t_cd,
    offpage("out", at=(95, BOTTOM), note="Cell mass cake to AD (off-plot)", note_at=(72, 239))])
line(sheet, "50-CM-3006", id="Line_CMD_B", dn=50, fluid="CM", labels=False, route=[
    cb["N2"], valve("P301B_NR", "CheckValve", at=(86, 215)), t_cd.branch])

# ---- Acidulation: R-301 with A-301, clarified broth, acid, pump-around through E-301 ----
RW, RH = 20, 28.6
r301 = equipment(sheet, "Vessel", "R-301", shape=VESSEL, at=(215, 90), scale=(2.0, 2.0), label_at=(215, 72),
                 nozzles=[Nozzle("N1", (-10, -RH), 150), Nozzle("N6", (0, -RH), 100), Nozzle("N2", (RW, -15), 40),
                          Nozzle("N3", (-RW, 15), 200), Nozzle("N4", (-8, RH), 200), Nozzle("N5", (8, RH), 150),
                          Nozzle("L1", (RW, 10))])
equipment(sheet, "Agitator", "A-301", shape="AGITATOR_SHAPE", at=(215, 98), scale=1.2, label_at=(226, 112))
clar = line(sheet, "150-PL-3002", dn=150, fluid="PL", label_at=(150, Y_CLAR - 9), route=[
    S["A"]["N2"], (62, 68), (62, Y_CLAR), t_cb, t_cc, (170, Y_CLAR), (170, 50), (205, 50), r301["N1"]])
for s, t, cx in (("B", t_cb, 85), ("C", t_cc, 120)):
    line(sheet, f"150-PL-3002{s}", dn=150, fluid="PL", labels=False, route=[S[s]["N2"], (cx + 12, 68), t.branch])
line(sheet, "100-VT-3011", dn=100, fluid="VT", labels=False, route=[
    r301["N6"], offpage("out", at=(215, 42), note="vent to atm.", note_at=(228, 41))])

pa = equipment(sheet, "CentrifugalPump", "P-303A", shape=PUMP, at=(190, 150), label_at=(190, 161),
               nozzles=[Nozzle("N1", (7.5, 0), 200), Nozzle("N2", (0, -7.5), 200)])
pb = equipment(sheet, "CentrifugalPump", "P-303B", shape=PUMP, at=(175, 180), label_at=(175, 191),
               nozzles=[Nozzle("N1", (7.5, 0), 200), Nozzle("N2", (0, -7.5), 200)])
e301 = equipment(sheet, "SpiralHeatExchanger", "E-301", shape="HEAT_EXCHANGER_SPIRAL_SHAPE", at=(145, 130),
                 label_at=(130, 142),
                 nozzles=[Nozzle("N1", (7.5, 0), 200), Nozzle("N2", (0, -7.5), 200), Nozzle("C1", (0, 7.5), 200),
                          Nozzle("C2", (-7.5, 0), 200)])
t_ps = tee("PA_TS", at=(207, 150), branch="left", branch_dn=200)
line(sheet, "200-GS-3012", dn=200, fluid="GS", label_at=(195, 166), route=[
    r301["N4"], valve("R301_HV1", "BallValve", at=(207, 127)), t_ps, (207, 180), pb["N1"]])
line(sheet, "200-GS-3012", id="Line_PAS_A", dn=200, fluid="GS", labels=False, route=[t_ps.branch, pa["N1"]])
t_pd = tee("PA_TD", at=(175, 130), branch="down", branch_dn=200)
pump_around = line(sheet, "200-GS-3013", dn=200, fluid="GS", label_at=(176, 124), route=[
    pa["N2"], valve("P303A_NR", "CheckValve", at=(190, 137)), (190, 130), t_pd, e301["N1"]])
line(sheet, "200-GS-3013", id="Line_PAD_B", dn=200, fluid="GS", labels=False, route=[
    pb["N2"], valve("P303B_NR", "CheckValve", at=(175, 165)), t_pd.branch])
ret = line(sheet, "200-GS-3014", dn=200, fluid="GS", label_at=(160, 109), route=[
    e301["N2"], (145, 105), r301["N3"]])
tv = valve("TV3023", "GlobeValve", at=(145, 175), tag="TV-3023")
line(sheet, "200-CW-3015", dn=200, fluid="CW", label_at=(157, 215), route=[
    offpage("in", at=(145, BOTTOM), note="CW", note_at=(151, 239)), tv, e301["C1"]])
line(sheet, "200-CW-3016", dn=200, fluid="CW", label_at=(108, 222), route=[
    e301["C2"], (120, 130), offpage("out", at=(120, BOTTOM), note="CWR", note_at=(127, 239))])

# ---- Acid: T-301, P-304A/B to R-301 ----
t301 = equipment(sheet, "Tank", "T-301", shape="TANK_CONE_ROOF_SHAPE", at=(330, 55), scale=1.4, label_at=(330, 60),
                 nozzles=[Nozzle("N1", (-6, -16), 80), Nozzle("N3", (6, -16), 50), Nozzle("N2", (0, 17.5), 40)])
line(sheet, "80-SA-3009", dn=80, fluid="SA", labels=False, route=[
    offpage("in", at=(324, TOP), note="H2SO4 93 wt% from tanker", note_at=(305, 19)),
    valve("T301_HVF", "BallValve", at=(324, 26)), t301["N1"]])
line(sheet, "50-VT-3010", dn=50, fluid="VT", labels=False, route=[
    t301["N3"], offpage("out", at=(336, 26), note="vent (desiccant breather)", note_at=(355, 25))])
qa = equipment(sheet, "CentrifugalPump", "P-304A", shape=PUMP, at=(300, 85), label_at=(300, 96),
               nozzles=[Nozzle("N1", (7.5, 0), 40), Nozzle("N2", (0, -7.5), 40)])
qb = equipment(sheet, "CentrifugalPump", "P-304B", shape=PUMP, at=(275, 105), label_at=(275, 116),
               nozzles=[Nozzle("N1", (7.5, 0), 40), Nozzle("N2", (0, -7.5), 40)])
t_as = tee("SA_TS", at=(330, 85), branch="left", branch_dn=40)
line(sheet, "40-SA-3007", dn=40, fluid="SA", label_at=(342, 95), route=[
    t301["N2"], valve("T301_HV", "BallValve", at=(330, 78)), t_as, (330, 105), qb["N1"]])
line(sheet, "40-SA-3007", id="Line_SAS_A", dn=40, fluid="SA", labels=False, route=[t_as.branch, qa["N1"]])
t_ad = tee("SA_TD", at=(275, 62), branch="down", branch_dn=40)
fv21 = valve("FV3021", "GlobeValve", at=(260, 62), tag="FV-3021")
acid = line(sheet, "40-SA-3008", dn=40, fluid="SA", label_at=(287, 53), route=[
    qa["N2"], valve("P304A_NR", "CheckValve", at=(300, 71)), (300, 62), t_ad, fv21, (250, 62), (250, 75), r301["N2"]])
line(sheet, "40-SA-3008", id="Line_SAD_B", dn=40, fluid="SA", labels=False, route=[
    qb["N2"], valve("P304B_NR", "CheckValve", at=(275, 91)), t_ad.branch])

# ---- Slurry: P-305A/B to the belt filter S-302 ----
sa = equipment(sheet, "CentrifugalPump", "P-305A", shape=PUMP, at=(240, 150), label_at=(240, 161),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 150)])
sb = equipment(sheet, "CentrifugalPump", "P-305B", shape=PUMP, at=(260, 170), label_at=(260, 181),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 150)])
s302 = equipment(sheet, "Filter", "S-302", shape="LIQUID_FILTER_SHAPE", at=(352, 135), scale=(3.0, 0.6),
                 label_at=(352, 124),
                 nozzles=[Nozzle("N1", (-18, -7.5), 150), Nozzle("N2", (22.5, 0), 200), Nozzle("N3", (-12, 7.5), 200)])
t_ss = tee("GS_TS", at=(223, 150), branch="right", branch_dn=150)
line(sheet, "150-GS-3017", dn=150, fluid="GS", label_at=(236, 177), route=[
    r301["N5"], valve("R301_HV2", "BallValve", at=(223, 127)), t_ss, (223, 170), sb["N1"]])
line(sheet, "150-GS-3017", id="Line_GSS_A", dn=150, fluid="GS", labels=False, route=[t_ss.branch, sa["N1"]])
t_sd = tee("GS_TD", at=(260, 128), branch="left", branch_dn=150)
line(sheet, "150-GS-3018", dn=150, fluid="GS", label_at=(300, 124), route=[
    sb["N2"], valve("P305B_NR", "CheckValve", at=(260, 154)), t_sd, (260, 120), (334, 120), s302["N1"]])
line(sheet, "150-GS-3018", id="Line_GSD_A", dn=150, fluid="GS", labels=False, route=[
    sa["N2"], valve("P305A_NR", "CheckValve", at=(240, 136)), (240, 128), t_sd.branch])
line(sheet, "200-GC-3019", dn=200, fluid="GC", labels=False, route=[
    s302["N2"], offpage("out", at=(RIGHT, 135), note="Gypsum cake, conveyor", note_at=(392, 131))])

# ---- Filtrate: V-303, K-301A/B, P-306A/B ----
v303 = equipment(sheet, "Vessel", "V-303", shape=VESSEL, at=(340, 185), label_at=(340, 185),
                 nozzles=[Nozzle("N1", (0, -14.3), 200), Nozzle("N2", (10, -8), 150), Nozzle("N3", (0, 14.3), 200),
                          Nozzle("L1", (10, 6))])
line(sheet, "200-CL-3020", dn=200, fluid="CL", label_at=(326, 158), route=[s302["N3"], (340, 160), v303["N1"]])
ka = equipment(sheet, "Compressor", "K-301A", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(385, 177), label_at=(385, 188),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (7.5, 0), 150)])
kb = equipment(sheet, "Compressor", "K-301B", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(385, 157), label_at=(385, 148),
               nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (7.5, 0), 150)])
t_v = tee("VA_T", at=(371, 177), branch="up", branch_dn=150)
line(sheet, "150-VA-3023", dn=150, fluid="VA", label_at=(360, 182), route=[v303["N2"], t_v, ka["N1"]])
line(sheet, "150-VA-3023", id="Line_VA_B", dn=150, fluid="VA", labels=False, route=[t_v.branch, (371, 157), kb["N1"]])
line(sheet, "150-VT-3025", dn=150, fluid="VT", labels=False, route=[
    ka["N2"], offpage("out", at=(401, 177), note="atm.", note_at=(398, 172))])
line(sheet, "150-VT-3026", dn=150, fluid="VT", labels=False, route=[
    kb["N2"], offpage("out", at=(401, 157), note="atm.", note_at=(398, 152))])
fa = equipment(sheet, "CentrifugalPump", "P-306A", shape=PUMP, at=(360, 215), label_at=(360, 205),
               nozzles=[Nozzle("N1", (-7.5, 0), 200), Nozzle("N2", (7.5, 0), 150)])
fb = equipment(sheet, "CentrifugalPump", "P-306B", shape=PUMP, at=(360, 235), label_at=(360, 245),
               nozzles=[Nozzle("N1", (-7.5, 0), 200), Nozzle("N2", (7.5, 0), 150)])
t_fs = tee("CL_TS", at=(340, 215), branch="right", branch_dn=200)
line(sheet, "200-CL-3021", dn=200, fluid="CL", label_at=(322, 222), route=[
    v303["N3"], valve("V303_HV", "BallValve", at=(340, 206)), t_fs, (340, 235), fb["N1"]])
line(sheet, "200-CL-3021", id="Line_CLS_A", dn=200, fluid="CL", labels=False, route=[t_fs.branch, fa["N1"]])
t_fd = tee("CL_TD", at=(385, 215), branch="down", branch_dn=150)
lv = valve("LV3031", "GlobeValve", at=(395, 215), tag="LV-3031")
filt = line(sheet, "150-CL-3022", dn=150, fluid="CL", label_at=(377, 207), route=[
    fa["N2"], valve("P306A_NR", "CheckValve", at=(375, 215)), t_fd, lv,
    offpage("out", at=(RIGHT, 215), note="To E-401A (P-401)", note_at=(397, 221))])
line(sheet, "150-CL-3022", id="Line_CLD_B", dn=150, fluid="CL", labels=False, route=[
    fb["N2"], valve("P306B_NR", "CheckValve", at=(375, 235)), (385, 235), t_fd.branch])

# ---- Instruments ----
ft20 = instrument(sheet, "FT-3020", at=(158, 65), sensing=clar, sensing_at=(170, 65))
instrument(sheet, "FFIC-3021", at=(253, 47), sensing=acid, sensing_at=(268, 62), signal_to=fv21)
instrument(sheet, "LIC-3022", at=(248, 100), sensing=r301["L1"])
instrument(sheet, "TIC-3023", at=(160, 150), sensing=pump_around, sensing_at=(160, 130), signal_to=tv)
instrument(sheet, "AIC-3024", at=(182, 90), sensing=ret, sensing_at=(182, 105))
instrument(sheet, "LIC-3031", at=(395, 198), sensing=v303["L1"], signal_to=lv)

# ---- Notes ----
note(sheet, "Cell removal (D-025, D-038): disc-stack centrifuges S-301A to C, two running, one spare, each on FIC-3011x; "
     "the self-cleaning bowl discharges the cell mass intermittently into V-301; operating water, motors and CIP by the "
     "vendor (ASSUMED).", at=(10, 253), size=2.0)
note(sheet, "Acidulation (D-007, D-038): 93 wt% H2SO4 by FFIC-3021 in ratio to FT-3020 (1.01 mol per mol Ca), trimmed by "
     "AIC-3024 (pH about 2.5, ASSUMED), into R-301 near the impeller.", at=(10, 257), size=2.0)
note(sheet, "2.0 MW of dilution and reaction heat to CW through the pump-around P-303A/B and the spiral cooler E-301 on "
     "TIC-3023; LIC-3022 sets the P-305A/B speed (VFD).", at=(10, 261), size=2.0)
note(sheet, "Gypsum (D-038): horizontal vacuum belt filter S-302 with cloth wash, no cake wash (D-007); filtrate receiver V-303 "
     "on the liquid-ring vacuum pumps K-301A/B (seal water by the vendor); cake 20 wt% moisture to the belt conveyor.",
     at=(10, 265), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
