"""P-403 ethanol column C-402, hydrolysis R-402 and stripper C-403 (provenance script; the XML is the source).

    cheme sheet new P-403
    cheme run --fmt pid/P-403.xml scripts/draft_P-403.py pid/P-403.xml

The ester column overhead (100-PL-4210 from P-402) feeds C-402 at 1 atm: reboiler E-431 on LP
steam (TIC-4302), condenser E-432, reflux drum V-431, P-431A/B for the reflux (FIC-4305) and the
ethanol to the header 50-ET-4101 (LIC-4304). The bottoms (ester and water) go by P-432A/B on
LIC-4303 (pump speed), mixed with the water recycle from P-404, through the heater E-441
(TIC-4401) into the stirred hydrolysis reactor R-402; P-442A/B on LIC-4403 feed the stripper
C-403, drawn as C-402 mirrored; its ethanol joins the header with the make-up from P-404, its
bottoms go to the concentrator E-404A on P-404 (D-008, D-009, D-042).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Nozzle, Sheet, equipment, instrument, line, note, offpage, tee, valve

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-403.xml")
blank = Path("build/P-403_blank.xml")      # the empty sheet of `cheme sheet new`, kept for reruns
if not blank.exists():
    Sheet.load(target).save(blank, fmt=False)
sheet = Sheet.load(blank)

PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_SHAPE"
LEFT, RIGHT, TOP, BOTTOM = 14, 406, 14, 243


def pump(tag, at, dn, left=False, label_at=None):
    """Suction on the left (or on the right with left=True: discharge to the left)."""
    s = 1 if left else -1
    return equipment(sheet, "CentrifugalPump", tag, shape=PUMP, at=at, label_at=label_at, rotation=180 if left else 0,
                     nozzles=[Nozzle("N1", (-7.5 * s, 0), dn[0]), Nozzle("N2", (7.5 * s, 0), dn[1])])


def column(n, cx, m, ov_dn, rb_dn, feed_side, feed_y, label_at, l1_side, lic_at, lic_note_at):
    """C-402 (m=1) or C-403 (m=-1, mirrored: reboiler right, drum left). Returns the parts."""
    X = lambda dx: cx + m * dx
    c = equipment(sheet, "ProcessColumn", f"C-40{n}", shape="COLUMN_TRAYS_SHAPE", at=(cx, 100), scale=(1.0, 2.6),
                  label_at=label_at,
                  nozzles=[Nozzle("V", (0, -65), ov_dn), Nozzle("RV", (-6 * m, -65), 80),
                           Nozzle("F", (feed_side * 10, feed_y - 100), 100), Nozzle("RF", (10 * m, -52), 50),
                           Nozzle("T1", (-10 * m, 20)), Nozzle("L1", (10 * l1_side, 58)), Nozzle("RB", (-10 * m, 50), rb_dn),
                           Nozzle("B", (0, 65), 150)])
    a = 3 if n == 2 else 5          # loop and line numbers 43xx (C-402) and 45xx (C-403)
    # relief and overhead
    line(sheet, f"80-RV-4{a}09", dn=80, fluid="RV", labels=False, route=[
        c["RV"], valve(f"PSV4{a}09", "CheckValve", at=(X(-6), 24), tag=f"PSV-4{a}09"),   # no safety valve class (D-031)
        offpage("out", at=(X(-6), TOP))])
    cond = equipment(sheet, "TubularHeatExchanger", f"E-4{a}2", shape=HX, at=(X(35), 38), scale=1.2,
                     label_at=(X(18), 40),
                     nozzles=[Nozzle("N1", (0, -9), ov_dn), Nozzle("N2", (0, 9), 100), Nozzle("C1", (10 * m, -5), 250),
                              Nozzle("C2", (10 * m, 5), 250)])
    line(sheet, f"{ov_dn}-VP-4{a}01", dn=ov_dn, fluid="VP", label_at=(X(12), 11), route=[
        c["V"], (cx, 20), (X(35), 20), cond["N1"]])
    cw = 250 if n == 2 else 300
    line(sheet, f"{cw}-CW-4{a}10", dn=cw, fluid="CW", labels=False, route=[
        offpage("in", at=(X(51), TOP), note="CW", note_at=(X(51) + 4 * m, 24)), (X(51), 33), cond["C1"]])
    line(sheet, f"{cw}-CW-4{a}11", dn=cw, fluid="CW", labels=False, route=[
        cond["C2"], (X(59), 43), offpage("out", at=(X(59), TOP), note="CWR", note_at=(X(59) + 5 * m, 30))])
    drum = equipment(sheet, "Vessel", f"V-4{a}1", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(X(50), 82), rotation=90,
                     label_at=(X(50), 82),
                     nozzles=[Nozzle("N1", (-15 * m, -10), 100), Nozzle("P1", (-4 * m, -10)), Nozzle("N3", (8 * m, -10), 25),
                              Nozzle("N2", (0, 10), 80), Nozzle("L1", (15 * m, 0))])
    line(sheet, f"100-PL-4{a}02", dn=100, fluid="PL", labels=False, route=[cond["N2"], drum["N1"]])
    line(sheet, f"25-VT-4{a}12", dn=25, fluid="VT", labels=False, route=[
        drum["N3"], (X(58), 62), (X(71), 62), offpage("out", at=(X(71), TOP), note="vent hdr", note_at=(X(71) + 7 * m, 24))])
    instrument(sheet, f"PI-4{a}01", at=(X(46), 61), sensing=drum["P1"])
    # reflux and distillate pumps
    qa = pump(f"P-4{a}1A", (X(65), 117), (80, 65), left=(m < 0), label_at=(X(65), 108))
    qb = pump(f"P-4{a}1B", (X(65), 135), (80, 65), left=(m < 0), label_at=(X(65), 147))
    t_qs = tee(f"V4{a}1_TS", at=(X(50), 117), branch="right" if m > 0 else "left", branch_dn=80)
    line(sheet, f"80-PL-4{a}03", dn=80, fluid="PL", labels=False, route=[drum["N2"], t_qs, (X(50), 135), qb["N1"]])
    line(sheet, f"80-PL-4{a}03", id=f"Line_PL4{a}03_A", dn=80, fluid="PL", labels=False, route=[t_qs.branch, qa["N1"]])
    t_qd = tee(f"V4{a}1_TD", at=(X(84), 117), branch="down", branch_dn=65)
    t_rf = tee(f"RF4{a}_T", at=(X(80), 135), branch="down", branch_dn=50)
    lv = valve(f"LV4{a}04", "GlobeValve", at=(X(90), 75), tag=f"LV-4{a}04")
    fv = valve(f"FV4{a}05", "GlobeValve", at=(X(65), 153), tag=f"FV-4{a}05")
    # reboiler on LP steam
    reb = equipment(sheet, "TubularHeatExchanger", f"E-4{a}1", shape=HX, at=(X(-30), 182), scale=1.5,
                    label_at=(X(-30), 200),
                    nozzles=[Nozzle("N1", (0, -11.25), rb_dn), Nozzle("N2", (0, 11.25), 150), Nozzle("S", (-11 * m, -6), 250),
                             Nozzle("C", (-11 * m, 6), 50)])
    line(sheet, f"{rb_dn}-VP-4{a}13", dn=rb_dn, fluid="VP", labels=False, route=[reb["N1"], (X(-30), 150), c["RB"]])
    tv = valve(f"TV4{a}02", "GlobeValve", at=(X(-47), 176), tag=f"TV-4{a}02")
    line(sheet, f"250-LS-4{a}14", dn=250, fluid="LS", labels=False, route=[
        offpage("in", at=(X(-53), BOTTOM), note="LP steam", note_at=(X(-55), 253)), (X(-53), 176), tv, reb["S"]])
    line(sheet, f"50-CD-4{a}15", dn=50, fluid="CD", labels=False, route=[
        reb["C"], (X(-45), 188), valve(f"E4{a}1_ST", "SteamTrap", at=(X(-45), 205)),
        offpage("out", at=(X(-45), BOTTOM), note="LPC", note_at=(X(-41), 253))])
    instrument(sheet, f"TIC-4{a}02", at=(X(-25), 120), sensing=c["T1"], signal_to=tv, signal_points=[(X(-47), 120)])
    # bottoms: thermosyphon feed and the bottoms pumps
    bdn = (100, 80) if n == 2 else (100, 100)
    pa = pump(f"P-4{a}2A", (X(15), 210), bdn, left=(m < 0), label_at=(X(15), 201))
    pb = pump(f"P-4{a}2B", (X(15), 226), bdn, left=(m < 0), label_at=(X(15), 237))
    t_b = tee(f"C40{n}_TB", at=(cx, 197), branch="left" if m > 0 else "right", branch_dn=150)
    t_s = tee(f"C40{n}_TS", at=(cx, 210), branch="right" if m > 0 else "left", branch_dn=100)
    line(sheet, f"150-PL-4{a}16", dn=150, fluid="PL", labels=False, route=[c["B"], t_b, t_s, (cx, 226), pb["N1"]])
    line(sheet, f"150-PL-4{a}16", id=f"Line_PL4{a}16_R", dn=150, fluid="PL", labels=False, route=[
        t_b.branch, (X(-30), 197), reb["N2"]])
    line(sheet, f"150-PL-4{a}16", id=f"Line_PL4{a}16_A", dn=100, fluid="PL", labels=False, route=[t_s.branch, pa["N1"]])
    instrument(sheet, f"LIC-4{a}03", at=lic_at, sensing=c["L1"])
    note(sheet, f"LIC-4{a}03: P-4{a}2A/B speed", at=lic_note_at, size=2.0)
    return dict(c=c, drum=drum, qa=qa, qb=qb, t_qd=t_qd, t_rf=t_rf, fv=fv, lv=lv, pa=pa, pb=pb, X=X, a=a, m=m)


def reflux(k):
    """The spare pump's discharge and the reflux, once the header has placed the discharge tee."""
    X, a, m = k["X"], k["a"], k["m"]
    line(sheet, f"65-ET-4{a}05", id=f"Line_ET4{a}05_B", dn=65, fluid="ET", labels=False, route=[
        k["qb"]["N2"], valve(f"P4{a}1B_NR", "CheckValve", at=(X(76), 135)), k["t_rf"], (X(84), 135), k["t_qd"].branch])
    rf = line(sheet, f"50-ET-4{a}06", dn=50, fluid="ET", label_at=(X(37), 118), route=[
        k["t_rf"].branch, (X(80), 153), k["fv"], (X(25), 153), (X(25), 48), k["c"]["RF"]])
    instrument(sheet, f"FIC-4{a}05", at=(X(52), 162), sensing=rf, sensing_at=(X(52), 153), signal_to=k["fv"])
    instrument(sheet, f"LIC-4{a}04", at=(X(76), 92), sensing=k["drum"]["L1"], signal_to=k["lv"],
               signal_points=[(X(76), 75)])


# ---- C-402 ethanol column (left) and C-403 stripper (right, mirrored) ----
k2 = column(2, 75, 1, 450, 400, -1, 80, label_at=(50, 100), l1_side=1, lic_at=(97, 165), lic_note_at=(91, 175))
k3 = column(3, 345, -1, 500, 400, -1, 110, label_at=(372, 100), l1_side=1, lic_at=(366, 160),
            lic_note_at=(321, 190))
line(sheet, "100-PL-4210", dn=100, fluid="PL", labels=False, route=[
    offpage("in", at=(LEFT, 80), note="From P-421A/B, 100-PL-4210 (P-402)", note_at=(40, 72)), k2["c"]["F"]])

# ---- Ethanol header 50-ET-4101 to E-411 (P-402): C-402 distillate, C-403 distillate, make-up ----
t_h2 = tee("ETH_T2", at=(165, 40), branch="right", branch_dn=65)
t_h3 = tee("ETH_T3", at=(165, 28), branch="right", branch_dn=25)
line(sheet, "50-ET-4101", dn=50, fluid="ET", label_at=(180, 60), route=[
    k2["qa"]["N2"], valve("P431A_NR", "CheckValve", at=(153, 117)), k2["t_qd"], (165, 117), k2["lv"], t_h2, t_h3,
    offpage("out", at=(165, TOP), note="To E-411, 50-ET-4101 (P-402)", note_at=(190, 20))])
line(sheet, "65-ET-4505", dn=65, fluid="ET", label_at=(215, 46), route=[
    k3["qa"]["N2"], valve("P451A_NR", "CheckValve", at=(267, 117)), k3["t_qd"], (255, 117), k3["lv"], (255, 40), t_h2.branch])
line(sheet, "25-ET-4701", dn=25, fluid="ET", labels=False, route=[
    offpage("in", at=(212, TOP), note="25-ET-4701 (P-404)", note_at=(226, 20)), (212, 28), t_h3.branch])
reflux(k2)
reflux(k3)

# ---- Hydrolysis: C-402 bottoms + water recycle, E-441, R-402, P-442A/B to C-403 ----
t_pd = tee("C402_TD", at=(110, 210), branch="down", branch_dn=80)
t_m = tee("M402_T", at=(150, 210), branch="down", branch_dn=100)
e441 = equipment(sheet, "TubularHeatExchanger", "E-441", shape=HX, at=(180, 210), scale=1.2, label_at=(164, 201),
                 nozzles=[Nozzle("P1", (-9, 0), 150), Nozzle("P2", (9, 0), 150), Nozzle("S", (5, 7), 125),
                          Nozzle("C", (-5, 7), 25)])
line(sheet, "80-PL-4401", dn=80, fluid="PL", label_at=(128, 201), route=[
    k2["pa"]["N2"], valve("P432A_NR", "CheckValve", at=(103, 210)), t_pd, t_m, e441["P1"]])
line(sheet, "80-PL-4401", id="Line_PL4401_B", dn=80, fluid="PL", labels=False, route=[
    k2["pb"]["N2"], valve("P432B_NR", "CheckValve", at=(103, 226)), (110, 226), t_pd.branch])
line(sheet, "100-PL-4402", dn=100, fluid="PL", labels=False, route=[
    offpage("in", at=(150, BOTTOM), note="Water recycle from P-461A/B, 100-PL-4402 (P-404)", note_at=(118, 253)),
    t_m.branch])
r402 = equipment(sheet, "Vessel", "R-402", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(215, 125), scale=(1.5, 1.8),
                 label_at=(243, 112), markers=[("AGITATOR_SHAPE", 0, 3)],
                 nozzles=[Nozzle("N1", (-8, -25.7), 150), Nozzle("N3", (8, -25.7), 80), Nozzle("L1", (15, 15)),
                          Nozzle("B", (0, 25.7), 150)])
feed = line(sheet, "150-PL-4403", dn=150, fluid="PL", label_at=(172, 150), route=[
    e441["P2"], (189, 92), (207, 92), r402["N1"]])
tv44 = valve("TV4401", "GlobeValve", at=(198, 232), tag="TV-4401")
line(sheet, "125-LS-4404", dn=125, fluid="LS", labels=False, route=[
    offpage("in", at=(208, BOTTOM), note="LP steam", note_at=(214, 253)), (208, 232), tv44, (185, 232), e441["S"]])
line(sheet, "25-CD-4405", dn=25, fluid="CD", labels=False, route=[
    e441["C"], valve("E441_ST", "SteamTrap", at=(175, 228)), offpage("out", at=(175, BOTTOM), note="LPC", note_at=(178, 253))])
instrument(sheet, "TIC-4401", at=(198, 186), sensing=feed, sensing_at=(189, 186), signal_to=tv44)
line(sheet, "80-RV-4406", dn=80, fluid="RV", labels=False, route=[
    r402["N3"], valve("PSV4406", "CheckValve", at=(223, 85), tag="PSV-4406"), (223, 72), (240, 72),
    offpage("out", at=(240, TOP))])
ra = pump("P-442A", (230, 180), (150, 100), label_at=(230, 171))
rb = pump("P-442B", (230, 198), (150, 100), label_at=(230, 209))
t_rs = tee("R402_TS", at=(215, 180), branch="right", branch_dn=150)
line(sheet, "150-PL-4407", dn=150, fluid="PL", labels=False, route=[r402["B"], t_rs, (215, 198), rb["N1"]])
line(sheet, "150-PL-4407", id="Line_PL4407_A", dn=150, fluid="PL", labels=False, route=[t_rs.branch, ra["N1"]])
t_rd = tee("R402_TD", at=(248, 180), branch="down", branch_dn=100)
lv44 = valve("LV4403", "GlobeValve", at=(300, 180), tag="LV-4403")
line(sheet, "100-PL-4408", dn=100, fluid="PL", label_at=(290, 188), route=[
    ra["N2"], valve("P442A_NR", "CheckValve", at=(242, 180)), t_rd, lv44, (325, 180), (325, 110), k3["c"]["F"]])
line(sheet, "100-PL-4408", id="Line_PL4408_B", dn=100, fluid="PL", labels=False, route=[
    rb["N2"], valve("P442B_NR", "CheckValve", at=(242, 198)), (248, 198), t_rd.branch])
instrument(sheet, "LIC-4403", at=(242, 140), sensing=r402["L1"], signal_to=lv44, signal_points=[(242, 170), (300, 170)])

# ---- C-403 bottoms to E-404A (P-404) ----
t_xd = tee("C403_TD", at=(310, 210), branch="down", branch_dn=100)
line(sheet, "100-PL-4507", dn=100, fluid="PL", labels=False, route=[
    k3["pa"]["N2"], valve("P452A_NR", "CheckValve", at=(317, 210)), t_xd, (290, 210),
    offpage("out", at=(290, BOTTOM), note="To E-404A, 100-PL-4507 (P-404)", note_at=(262, 253))])
line(sheet, "100-PL-4507", id="Line_PL4507_B", dn=100, fluid="PL", labels=False, route=[
    k3["pb"]["N2"], valve("P452B_NR", "CheckValve", at=(317, 226)), (310, 226), t_xd.branch])

# ---- Notes ----
note(sheet, "C-402 at 1 atm, reflux ratio 3; C-403 at 1 atm, reflux ratio 2 (ASSUMED, D-009). Both overheads (S18, S19, about "
     "91 wt% ethanol) and the make-up S17 form the ethanol header 50-ET-4101 to E-411 (P-402); the make-up holds the ratio (D-008).",
     at=(10, 258), size=2.0)
note(sheet, "R-402 hydrolysis at 363 K, 4 h, about 260 m3, agitated (D-008, D-010); feed S24 + water recycle S29 heated in E-441 "
     "(Q11 1.39 MW). Relief valves and vents to the vent header (ethanol, D-012): flammable area for area classification.",
     at=(10, 262), size=2.0)

sheet.save(target)
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
