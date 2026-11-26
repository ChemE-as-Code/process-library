"""P-404 product concentration, storage and ethanol make-up (provenance script; the XML is the source).

    cheme run --fmt pid/P-404.xml scripts/draft_P-404.py pid/P-404.xml

The ethanol-free hydrolysate from C-403 (100-PL-4507, P-403) is concentrated to 88 wt% in the
two falling-film effects E-404A (LP steam, FIC-4601) and E-404B (heated by the vapour of
E-404A, at 20 kPa(a)); the last vapour condenses in E-461 under the liquid-ring pumps K-461A/B
(PIC-4610). The condensates collect in V-461; P-461A/B return them as the hydrolysis water
(100-PL-4402 to P-403, LIC-4615) with a purge to the waste water (FIC-4614). The product leaves
E-404B by P-462A/B on LIC-4616 through the cooler E-405 (TIC-4804) to T-401A/B, each with
LIT-4808x and an independent LSHH-4809x closing its fill valve XV-4807x; P-481A/B load trucks.
Ethanol make-up: T-402 (tanker fill through XV-4704, closed by LSHH-4705), P-472A/B, FV-4701 on
the ratio controller FFIC-4701 into 25-ET-4701 (P-403) (D-008, D-009, D-042, D-044).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Nozzle, Sheet, equipment, instrument, line, note, offpage, tee, valve

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-404.xml")
blank = Path("build/P-404_blank.xml")      # the empty sheet, kept for reruns
if not blank.exists():
    Sheet.load(target).save(blank, fmt=False)
sheet = Sheet.load(blank)

PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_SHAPE"
LEFT, RIGHT, TOP, BOTTOM = 14, 406, 14, 243


def pump(tag, at, dn, label_at):
    return equipment(sheet, "CentrifugalPump", tag, shape=PUMP, at=at, label_at=label_at,
                     nozzles=[Nozzle("N1", (-7.5, 0), dn[0]), Nozzle("N2", (7.5, 0), dn[1])])


def pump_pair(tags, x, y, dy, dn, num, suction_from, suction_dn, disc_num, disc_dn, fluid, ts_x, b_label=None):
    """Two pumps at (x, y) and (x, y + dy), suction tee at ts_x (below the source), discharge join tee 20 mm right."""
    pa = pump(tags[0], (x, y), dn, label_at=(x, y - 11))
    pb = pump(tags[1], (x, y + dy), dn, label_at=b_label or (x, y + dy + 11))
    ts = tee(f"{tags[0][:5]}_TS".replace("-", ""), at=(ts_x, y), branch="right", branch_dn=dn[0])
    line(sheet, num, dn=suction_dn, fluid=fluid, labels=False, route=[*suction_from, ts, (ts_x, y + dy), pb["N1"]])
    line(sheet, num, id=f"Line_{num.replace('-', '')}_A", dn=dn[0], fluid=fluid, labels=False, route=[ts.branch, pa["N1"]])
    tj = tee(f"{tags[0][:5]}_TD".replace("-", ""), at=(x + 20, y), branch="down", branch_dn=dn[1])
    SPARES.append(lambda: line(sheet, disc_num, id=f"Line_{disc_num.replace('-', '')}_B", dn=dn[1], fluid=fluid,
                               labels=False, route=[pb["N2"], valve(f"{tags[1].replace('-', '')}_NR", "CheckValve",
                                                                    at=(x + 13, y + dy)), (x + 20, y + dy), tj.branch]))
    return pa, pb, tj, valve(f"{tags[0].replace('-', '')}_NR", "CheckValve", at=(x + 13, y))


SPARES = []    # the spare pumps' discharges, drawn once the main discharge has placed the join tee


# ---- Concentrator: E-404A on LP steam, E-404B on the vapour of E-404A ----
ea = equipment(sheet, "ThinFilmEvaporator", "E-404A", shape="THIN_FILM_EVAPORATOR_SHAPE", at=(60, 90), scale=1.6,
               label_at=(83, 62),
               nozzles=[Nozzle("F", (-6, -20), 100), Nozzle("V", (6, -20), 600), Nozzle("S", (-16, -10), 300),
                        Nozzle("C", (-16, 14), 80), Nozzle("B", (0, 20), 80), Nozzle("L1", (16, 0))])
eb = equipment(sheet, "ThinFilmEvaporator", "E-404B", shape="THIN_FILM_EVAPORATOR_SHAPE", at=(130, 90), scale=1.6,
               label_at=(154, 64),
               nozzles=[Nozzle("V", (6, -20), 1200), Nozzle("S", (-16, -10), 600), Nozzle("F", (-16, 14), 80),
                        Nozzle("C", (16, 10), 80), Nozzle("B", (0, 20), 80), Nozzle("L1", (12, 18))])
line(sheet, "100-PL-4507", id="Line_PL4507_P404", dn=100, fluid="PL", label_at=(30, 46), route=[
    offpage("in", at=(LEFT, 40), note="From P-452A/B, 100-PL-4507 (P-403)", note_at=(36, 35)), (54, 40), ea["F"]])
fv01 = valve("FV4601", "GlobeValve", at=(24, 80), tag="FV-4601")
steam = line(sheet, "300-LS-4601", dn=300, fluid="LS", labels=False, route=[
    offpage("in", at=(LEFT, 80), note="LP steam", note_at=(22, 87)), fv01, ea["S"]])
instrument(sheet, "FIC-4601", at=(34, 64), sensing=steam, sensing_at=(34, 80), signal_to=fv01)
line(sheet, "80-CD-4602", dn=80, fluid="CD", labels=False, route=[
    ea["C"], valve("E404A_ST", "SteamTrap", at=(28, 104)), offpage("out", at=(LEFT, 104), note="LPC", note_at=(20, 100))])
line(sheet, "600-VP-4603", dn=600, fluid="VP", label_at=(83, 21), route=[
    ea["V"], (66, 30), (100, 30), (100, 80), eb["S"]])
lv04 = valve("LV4604", "GlobeValve", at=(82, 124), tag="LV-4604")
line(sheet, "80-PL-4604", dn=80, fluid="PL", label_at=(84, 131), route=[
    ea["B"], (60, 124), lv04, (106, 124), (106, 104), eb["F"]])
instrument(sheet, "LIC-4604", at=(88, 106), sensing=ea["L1"], signal_to=lv04)

# ---- Condenser E-461, condensate drum V-461, vacuum K-461A/B ----
e461 = equipment(sheet, "TubularHeatExchanger", "E-461", shape=HX, at=(185, 40), scale=1.5, label_at=(167, 54),
                 nozzles=[Nozzle("N1", (-11.25, 0), 1200), Nozzle("N2", (0, 11.25), 100), Nozzle("C1", (-6, -10), 450),
                          Nozzle("C2", (6, -10), 450), Nozzle("V", (10, -6), 100)])
line(sheet, "1200-VP-4606", dn=1200, fluid="VP", label_at=(152, 35), route=[eb["V"], (136, 40), e461["N1"]])
line(sheet, "450-CW-4608", dn=450, fluid="CW", labels=False, route=[
    offpage("in", at=(179, TOP), note="CW", note_at=(173, 20)), e461["C1"]])
line(sheet, "450-CW-4609", dn=450, fluid="CW", labels=False, route=[
    e461["C2"], offpage("out", at=(191, TOP), note="CWR", note_at=(198, 20))])
v461 = equipment(sheet, "Vessel", "V-461", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(185, 100), rotation=90,
                 label_at=(185, 100),
                 nozzles=[Nozzle("N1", (0, -10), 100), Nozzle("N4", (-15, 0), 80), Nozzle("N2", (0, 10), 100),
                          Nozzle("L1", (15, 0))])
line(sheet, "100-PC-4607", dn=100, fluid="PC", labels=False, route=[e461["N2"], v461["N1"]])
line(sheet, "80-PC-4605", dn=80, fluid="PC", labels=False, route=[eb["C"], (160, 100), v461["N4"]])
ka = equipment(sheet, "Compressor", "K-461A", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(225, 60), label_at=(225, 49),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
kb = equipment(sheet, "Compressor", "K-461B", shape="COMPRESSOR_LIQUID_RING_SHAPE", at=(225, 78), label_at=(225, 88),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)])
t_k = tee("VA461_T", at=(210, 60), branch="right", branch_dn=100)
vac = line(sheet, "100-VA-4610", dn=100, fluid="VA", labels=False, route=[e461["V"], (210, 34), t_k, (210, 78), kb["N1"]])
line(sheet, "100-VA-4610", id="Line_VA4610_A", dn=100, fluid="VA", labels=False, route=[t_k.branch, ka["N1"]])
instrument(sheet, "PIC-4610", at=(198, 70), sensing=vac, sensing_at=(210, 70))
t_v = tee("VT461_T", at=(236, 60), branch="left", branch_dn=80)
line(sheet, "80-VT-4611", dn=80, fluid="VT", labels=False, route=[
    kb["N2"], (236, 78), t_v, offpage("out", at=(236, TOP), note="vent hdr", note_at=(229, 20))])
line(sheet, "80-VT-4611", id="Line_VT4611_A", dn=80, fluid="VT", labels=False, route=[ka["N2"], t_v.branch])

# ---- Condensate pumps P-461A/B: water recycle (LIC-4615) and purge (FIC-4614) ----
pa, pb, tj, nr = pump_pair(("P-461A", "P-461B"), 210, 122, 16, (100, 100), "100-PL-4612", [v461["N2"]], 100,
                           "100-PL-4402", 100, "PC", 185, b_label=(196, 148))
t_s = tee("PL4402_T", at=(240, 122), branch="down", branch_dn=25)
lv15 = valve("LV4615", "GlobeValve", at=(250, 100), tag="LV-4615")
line(sheet, "100-PL-4402", id="Line_PL4402_P404", dn=100, fluid="PC", label_at=(262, 70), route=[
    pa["N2"], nr, tj, t_s, (250, 122), lv15,
    offpage("out", at=(250, TOP), note="To E-441, 100-PL-4402 (P-403)", note_at=(282, 20))])
fv14 = valve("FV4614", "GlobeValve", at=(250, 136), tag="FV-4614")
purge = line(sheet, "25-PL-4614", dn=25, fluid="PC", labels=False, route=[
    t_s.branch, (240, 136), fv14, offpage("out", at=(262, 136), note="drain", note_at=(267, 131))])
instrument(sheet, "LIC-4615", at=(214, 100), sensing=v461["L1"], signal_to=lv15)
instrument(sheet, "FIC-4614", at=(256, 149), sensing=purge, sensing_at=(256, 136), signal_to=fv14,
           signal_points=[(250, 149)])

# ---- Product: P-462A/B on LIC-4616, cooler E-405 (TIC-4804), product tanks T-401A/B ----
qa, qb, tq, nq = pump_pair(("P-462A", "P-462B"), 150, 160, 18, (80, 50), "80-PL-4801", [eb["B"]], 80,
                           "50-PL-4802", 50, "PL", 130)
lv16 = valve("LV4616", "GlobeValve", at=(180, 160), tag="LV-4616")
e405 = equipment(sheet, "TubularHeatExchanger", "E-405", shape=HX, at=(205, 160), scale=1.2, label_at=(226, 152),
                 nozzles=[Nozzle("P1", (-9, 0), 50), Nozzle("P2", (9, 0), 50), Nozzle("C1", (5, 7), 100),
                          Nozzle("C2", (-5, 7), 100)])
line(sheet, "50-PL-4802", dn=50, fluid="PL", labels=False, route=[qa["N2"], nq, tq, lv16, e405["P1"]])
instrument(sheet, "LIC-4616", at=(156, 130), sensing=eb["L1"], signal_to=lv16, signal_points=[(180, 130)])
tv04 = valve("TV4804", "GlobeValve", at=(210, 200), tag="TV-4804")
line(sheet, "100-CW-4804", dn=100, fluid="CW", labels=False, route=[
    offpage("in", at=(210, BOTTOM), note="CW", note_at=(216, 238)), tv04, e405["C1"]])
line(sheet, "100-CW-4805", dn=100, fluid="CW", labels=False, route=[
    e405["C2"], offpage("out", at=(200, BOTTOM), note="CWR", note_at=(193, 238))])

ta = equipment(sheet, "Tank", "T-401A", shape="TANK_CONE_ROOF_SHAPE", at=(312, 62), scale=1.4, label_at=(312, 66),
               nozzles=[Nozzle("N1", (-6, -16), 50), Nozzle("N3", (6, -16), 80), Nozzle("N2", (0, 17.5), 100),
                        Nozzle("L1", (14, 0)), Nozzle("L2", (-14, -6))])
tb = equipment(sheet, "Tank", "T-401B", shape="TANK_CONE_ROOF_SHAPE", at=(372, 62), scale=1.4, label_at=(372, 66),
               nozzles=[Nozzle("N1", (-6, -16), 50), Nozzle("N3", (6, -16), 80), Nozzle("N2", (0, 17.5), 100),
                        Nozzle("L1", (14, 0)), Nozzle("L2", (-14, -6))])
t_f = tee("PL4803_T", at=(306, 26), branch="down", branch_dn=50)
xa = valve("XV4807A", "BallValve", at=(306, 36), tag="XV-4807A")
xb = valve("XV4807B", "BallValve", at=(366, 36), tag="XV-4807B")
prod = line(sheet, "50-PL-4803", dn=50, fluid="PL", label_at=(262, 168), route=[
    e405["P2"], (275, 160), (275, 26), t_f, (366, 26), xb, tb["N1"]])
line(sheet, "50-PL-4803", id="Line_PL4803_A", dn=50, fluid="PL", labels=False, route=[t_f.branch, xa, ta["N1"]])
instrument(sheet, "TIC-4804", at=(230, 176), sensing=prod, sensing_at=(230, 160), signal_to=tv04,
           signal_points=[(230, 200)])
for s, t, xv, x in (("A", ta, xa, 312), ("B", tb, xb, 372)):
    line(sheet, f"80-VT-4812{s}", dn=80, fluid="VT", labels=False, route=[
        t["N3"], offpage("out", at=(x + 6, 38), note="atm.", note_at=(x + 13, 38))])
    instrument(sheet, f"LSHH-4809{s}", at=(x - 22, 50), sensing=t["L2"], signal_to=xv, fail_action="FC",
               signal_points=[(x - 22, 36)])
instrument(sheet, "LIT-4808A", at=(338, 62), sensing=ta["L1"])
instrument(sheet, "LIT-4808B", at=(398, 62), sensing=tb["L1"])

# tank outlets to the loading pumps P-481A/B
t_h = tee("PL4810_T", at=(325, 95), branch="down", branch_dn=100)
line(sheet, "100-PL-4810", id="Line_PL4810_H", dn=100, fluid="PL", labels=False, route=[
    ta["N2"], valve("T401A_HV", "BallValve", at=(312, 87)), (312, 95), t_h, (372, 95),
    valve("T401B_HV", "BallValve", at=(372, 87)), tb["N2"]])
ra, rb, tr, nr8 = pump_pair(("P-481A", "P-481B"), 340, 112, 16, (100, 100), "100-PL-4810", [t_h.branch], 100,
                            "100-PL-4811", 100, "PL", 325)
line(sheet, "100-PL-4811", dn=100, fluid="PL", label_at=(384, 102), route=[
    ra["N2"], nr8, tr, offpage("out", at=(RIGHT, 112), note="To truck loading", note_at=(390, 121))])

# ---- Ethanol make-up: T-402, P-472A/B, FFIC-4701 ----
t402 = equipment(sheet, "Tank", "T-402", shape="TANK_CONE_ROOF_SHAPE", at=(330, 190), scale=1.2, label_at=(330, 194),
                 nozzles=[Nozzle("N1", (-5, -14), 50), Nozzle("N3", (5, -14), 50), Nozzle("N2", (0, 15), 25),
                          Nozzle("L1", (12, 0)), Nozzle("L2", (-12, -5))])
xv04 = valve("XV4704", "BallValve", at=(325, 163), tag="XV-4704")
line(sheet, "50-ET-4702", dn=50, fluid="ET", labels=False, route=[
    offpage("in", at=(RIGHT, 156), note="Ethanol from tanker", note_at=(388, 151)), (325, 156), xv04, t402["N1"]])
line(sheet, "50-VT-4703", dn=50, fluid="VT", labels=False, route=[
    t402["N3"], (335, 168), offpage("out", at=(348, 168), note="vent (PVRV + FA)", note_at=(362, 168))])
instrument(sheet, "LSHH-4705", at=(305, 175), sensing=t402["L2"], signal_to=xv04, fail_action="FC",
           signal_points=[(305, 163)])
instrument(sheet, "LIT-4706", at=(356, 190), sensing=t402["L1"])
sa_, sb_, ts_, ns_ = pump_pair(("P-472A", "P-472B"), 350, 214, 16, (25, 25), "25-ET-4707",
                               [t402["N2"], valve("T402_HV", "BallValve", at=(330, 207))], 25, "25-ET-4701", 25, "ET", 330)
fv4701 = valve("FV4701", "GlobeValve", at=(382, 214), tag="FV-4701")
mk = line(sheet, "25-ET-4701", id="Line_ET4701_P404", dn=25, fluid="ET", labels=False, route=[
    sa_["N2"], ns_, ts_, fv4701, offpage("out", at=(RIGHT, 214), note="To 50-ET-4101 (P-403)", note_at=(388, 222))])
instrument(sheet, "FFIC-4701", at=(394, 200), sensing=mk, sensing_at=(394, 214), signal_to=fv4701)

for draw in SPARES:
    draw()

# ---- Notes ----
note(sheet, "E-404A/B falling film, once through, E-404B at 20 kPa(a) (D-008, D-009, Q14 11.0 MW, Q15 13.1 MW); LIC-4604 and "
     "LIC-4616 hold the sumps; PIC-4610 sets the speed of K-461A/B. Condensates S28 to V-461: recycle S29 on LIC-4615, purge S30 "
     "on FIC-4614.", at=(10, 254), size=2.0)
note(sheet, "T-401A/B and T-402: LSHH-4809A/B and LSHH-4705 close XV-4807A/B and XV-4704 (C&E I-401 to I-403). FFIC-4701 holds "
     "the ethanol make-up S17 in ratio to the acid feed of R-401 (D-008). T-402 ethanol, N2 blanketed: flammable area (D-012).",
     at=(10, 258), size=2.0)

sheet.save(target)
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
