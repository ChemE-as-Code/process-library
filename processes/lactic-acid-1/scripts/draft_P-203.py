"""P-203, P-206, P-207: production fermenters R-201B to P as typicals of R-201A, their common
headers, the harvest pumps and the broth hold tank T-201 (provenance script; the XML is the source).

    cheme sheet new P-203 ; cheme run scripts/draft_P-203.py pid/P-203.xml P-203   (R-201B to I)
    cheme sheet new P-206 ; cheme run scripts/draft_P-203.py pid/P-206.xml P-206   (R-201J to P)
    cheme sheet new P-207 ; cheme run scripts/draft_P-203.py pid/P-207.xml P-207   (harvest, T-201)

Each fermenter column is drawn by one loop body (D-035): R-201x with A-201x, the top headers
(inoculum, sterile medium, CIP supply, SIP steam, N2) dropping to the head through one branch
valve each (it stands for R-201A's steam block), the N2 inlet filter F-202x, the vent filter
F-201x to atmosphere, the tempered-water pump P-201x on the coils, and below the vessel the
harvest header with the CIP return branch and the milk-of-lime ring main branch. The drops of the
headers cross the headers below them (the headers are common to all fermenters); those crossings
are accepted in checks.yaml by the Line_Hdr_*/Line_Drop_* id pattern.
"""

import sys
from math import sqrt
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

target = Path(sys.argv[1])
part = sys.argv[2]
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
FILTER = "GAS_FILTER_SHAPE"
LEFT, RIGHT = 14, 406
X0, STEP = 70, 42
CY, SX, SY = 128, 1.2, 2.6
W, H, HB = 10 * SX, 14.3 * SY, 1.73 * SY              # half width 12, half height 37.2, head 4.5
FH = 5.6                                               # filter nozzle offset at scale 0.45


def hy(dx):
    """Y offset of a nozzle on the top head at dx from the axis."""
    return -H + HB * (1 - sqrt(1 - (dx / W) ** 2))


# key, header line, header DN, fluid, header y, drop dx, branch line (without the letter), branch DN
TOP = [("IN", "100-IN-2004", 100, 20, -9, "100-IN-2005", 100),
       ("SM", "200-SM-2001", 200, 27, -5, "200-SM-2002", 200),
       ("CS", "100-CS-2015", 100, 34, -1, "100-CS-2016", 100),
       ("SS", "150-SS-2019", 150, 41, 2, "100-SS-2020", 100),
       ("NS", "80-NS-2008", 80, 48, -17, "50-NS-2025", 50)]
BOTTOM = [("BR", "250-BR-2011", 250, 200, 0, "200-BR-2010", 200),
          ("CR", "150-CR-2017", 150, 208, 8, "100-CR-2018", 100),
          ("ML", "100-ML-1102", 100, 216, 16, "25-ML-2024", 25)]
FROM = {"IN": "100-IN-2004 from R-213A to C", "SM": "200-SM-2001 from E-101", "CS": "100-CS-2015 from P-204",
        "SS": "150-SS-2019 from P-204", "NS": "80-NS-2008 from B/L", "BR": "250-BR-2011 from R-201A",
        "CR": "150-CR-2017 from R-201A", "ML": "100-ML-1102 past R-201A"}
END_P206 = {"BR": "250-BR-2011 to P-202A/B (P-207)", "CR": "150-CR-2017 to P-222A/B (P-204)",
            "ML": "Return leg 100-ML-1103 (P-102)"}


def column(s, cx, tees):
    """One fermenter R-201<s> at axis cx; tees[key] is its header tee."""
    r = equipment(sheet, "Vessel", f"R-201{s}", shape=VESSEL, at=(cx, CY), scale=(SX, SY), nozzles=[
        Nozzle("N2", (-9, hy(-9)), 100), Nozzle("N1", (-5, hy(-5)), 200), Nozzle("N5", (-1, hy(-1)), 100),
        Nozzle("N4", (8, hy(8)), 150), Nozzle("N6", (-W, -H + HB), 150), Nozzle("C2", (-W, -18), 150),
        Nozzle("C1", (-W, 22), 150), Nozzle("N3", (W, 22), 25), Nozzle("N9", (0, H), 200)],
        label_at=(cx, CY - 24))
    equipment(sheet, "Agitator", f"A-201{s}", shape="AGITATOR_SHAPE", at=(cx, CY + 4), scale=0.8,
              label_at=(cx, CY + 13))
    fv = equipment(sheet, "GasFilter", f"F-201{s}", shape=FILTER, at=(cx + 8, 82), scale=0.45,
                   nozzles=[Nozzle("N1", (0, FH), 150), Nozzle("N2", (0, -FH), 150)], label_at=(cx + 20, 82))
    fg = equipment(sheet, "GasFilter", f"F-202{s}", shape=FILTER, at=(cx - 17, 60), scale=0.45,
                   nozzles=[Nozzle("N1", (0, -FH), 50), Nozzle("N2", (0, FH), 150)], label_at=(cx - 28, 60))
    pump = equipment(sheet, "CentrifugalPump", f"P-201{s}", shape=PUMP, at=(cx - 9, 182),
                     nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 150)], label_at=(cx - 13, 193))

    def drop(key, route, dn, fluid=None):
        number = {k: b for k, *_, b, _ in TOP + BOTTOM}[key] + s
        line(sheet, number, id=f"Line_Drop_{key}_{s}", dn=dn, fluid=fluid or key, labels=False, route=route)

    # Top: inoculum, medium, CIP supply with the head SIP steam teed in, N2 through F-202x
    drop("IN", [tees["IN"].branch, valve(f"IN_{s}_HV", "BallValve", at=(cx - 9, 54)), r["N2"]], 100)
    drop("SM", [tees["SM"].branch, valve(f"SM_{s}_HV", "BallValve", at=(cx - 5, 60)), r["N1"]], 200)
    t_sip = tee(f"CS_{s}_TSIP", at=(cx - 1, 66), branch="right", branch_dn=100)
    drop("CS", [tees["CS"].branch, valve(f"CS_{s}_HV", "BallValve", at=(cx - 1, 54)), t_sip, r["N5"]], 100)
    drop("SS", [tees["SS"].branch, valve(f"SS_{s}_HV", "BallValve", at=(cx + 2, 60)), (cx + 2, 66),
                t_sip.branch], 100)
    drop("NS", [tees["NS"].branch, fg["N1"]], 50)
    line(sheet, f"150-NS-2009{s}", id=f"Line_NS_{s}", dn=150, fluid="NS", labels=False, route=[
        fg["N2"], (cx - 17, 72), (cx - 12, 72), valve(f"NS_{s}_HV", "BallValve", at=(cx - 12, 82)), r["N6"]])
    # Vent through F-201x to atmosphere
    line(sheet, f"150-VT-2006{s}", id=f"Line_VT_{s}", dn=150, fluid="VT", labels=False, route=[r["N4"], fv["N1"]])
    line(sheet, f"150-VT-2007{s}", id=f"Line_VTO_{s}", dn=150, fluid="VT", labels=False, route=[
        fv["N2"], offpage("out", at=(cx + 8, 70), note="atm", note_at=(cx + 13, 69))])
    # Bottom: harvest with the CIP return teed off, lime branch to the low shell nozzle
    t_cr = tee(f"BR_{s}_TCR", at=(cx, 180), branch="right", branch_dn=100)
    drop("BR", [r["N9"], valve(f"BR_{s}_HV", "BallValve", at=(cx, 172)), t_cr,
                valve(f"BR_{s}_HV2", "BallValve", at=(cx, 190)), tees["BR"].branch], 200)
    drop("CR", [t_cr.branch, valve(f"CR_{s}_HV", "BallValve", at=(cx + 4, 180)), (cx + 8, 180),
                tees["CR"].branch], 100)
    drop("ML", [tees["ML"].branch, valve(f"ML_{s}_HV", "BallValve", at=(cx + 16, 172)), (cx + 16, 150), r["N3"]], 25)
    # Tempered-water loop through the half-pipe coils
    line(sheet, f"150-TW-2022{s}", id=f"Line_TWS_{s}", dn=150, fluid="TW", labels=False, route=[
        pump["N2"], (cx - 9, 170), (cx - 14, 170), (cx - 14, 150), r["C1"]])
    line(sheet, f"150-TW-2023{s}", id=f"Line_TWR_{s}", dn=150, fluid="TW", labels=False, route=[
        r["C2"], (cx - 16.5, 110), pump["N1"]])


def headers(letters, last):
    """The common headers through the columns; last: the sheet ends them (P-206)."""
    xs = [X0 + STEP * i for i in range(len(letters))]
    tees = {s: {} for s in letters}
    for key, number, dn, y, dx, _, bdn in TOP + BOTTOM:
        up = key in {k for k, *_ in BOTTOM}
        run = []
        for s, cx in zip(letters, xs):
            t = tee(f"Hdr_{key}_T{s}", at=(cx + dx, y), branch="up" if up else "down", branch_dn=bdn)
            tees[s][key] = t
            run.append(t)
        start = offpage("in", at=(LEFT, y), note=FROM[key] if part == "P-203" else f"{number} from P-203",
                        note_at=(40, y - 2.3))
        if not last:
            end = [offpage("out", at=(RIGHT, y), note="P-206", note_at=(400, y - 2.3))]
        elif key in END_P206:
            end = [offpage("out", at=(RIGHT, y), note=END_P206[key], note_at=(380, y - 2.3))]
        else:                                          # top headers end at a low-point drain (N2: vent)
            xe = xs[-1] + 44
            kind = "SteamTrap" if key == "SS" else "BallValve"
            end = [valve(f"Hdr_{key}_END", kind, at=(xe - 8, y)),
                   offpage("out", at=(xe, y), note="vent" if key == "NS" else "drain", note_at=(xe + 8, y - 2.3))]
        line(sheet, number, id=f"Line_Hdr_{key}", dn=dn, fluid=key, labels=False, route=[start, *run, *end])
    for s, cx in zip(letters, xs):
        column(s, cx, tees[s])


if part in ("P-203", "P-206"):
    letters = "BCDEFGHI" if part == "P-203" else "JKLMNOP"
    headers(letters, last=part == "P-206")
    first, lastl = letters[0], letters[-1]
    note(sheet, f"R-201{first} to R-201{lastl}: typicals of R-201A (P-202), instrumented, steam-blocked and SIP-connected "
         "as R-201A; branch line numbers as R-201A's with the fermenter letter (D-035).", at=(10, 254), size=2.5)
    note(sheet, "Each branch valve drawn stands for R-201A's steam block (two valves, SS between, CD bleed). Bottom SIP, "
         "sampling, the TW loop's CW and LP-steam injection and trips I-201 to I-204 as R-201A.", at=(10, 260), size=2.5)
    note(sheet, "NOT AERATED (D-019): N2 overlay through F-202x, vent through F-201x. Fermenters 2.5 barg and full vacuum, "
         "150 C (D-016, D-034). Sterile boundary at the branch valves (D-020).", at=(10, 266), size=2.5)

if part == "P-207":
    t201 = equipment(sheet, "Tank", "T-201", shape=VESSEL, at=(190, 130), scale=(3.0, 4.0), nozzles=[
        Nozzle("N1", (-15, -55.5), 200), Nozzle("L1", (15, -55.5)), Nozzle("T1", (-30, 20)),
        Nozzle("C1", (-30, 45), 50), Nozzle("C2", (30, 45), 25), Nozzle("N9", (0, 57.2), 200)],
        label_at=(190, 82))
    equipment(sheet, "Agitator", "A-202", shape="AGITATOR_SHAPE", at=(190, 140), scale=1.5, label_at=(208, 160))
    pa = equipment(sheet, "CentrifugalPump", "P-202A", shape=PUMP, at=(80, 110),
                   nozzles=[Nozzle("N1", (-7.5, 0), 250), Nozzle("N2", (0, -7.5), 200)], label_at=(80, 123))
    pb = equipment(sheet, "CentrifugalPump", "P-202B", shape=PUMP, at=(80, 150),
                   nozzles=[Nozzle("N1", (-7.5, 0), 250), Nozzle("N2", (0, -7.5), 200)], label_at=(80, 160))
    fa = equipment(sheet, "CentrifugalPump", "P-203A", shape=PUMP, at=(290, 205),
                   nozzles=[Nozzle("N1", (-7.5, 0), 200), Nozzle("N2", (0, -7.5), 150)], label_at=(290, 216))
    fb = equipment(sheet, "CentrifugalPump", "P-203B", shape=PUMP, at=(290, 235),
                   nozzles=[Nozzle("N1", (-7.5, 0), 200), Nozzle("N2", (0, -7.5), 150)], label_at=(290, 246))
    # Harvest header to the harvest pumps, A duty, B spare
    t_h = tee("BR_TH", at=(60, 110), branch="down", branch_dn=250)
    line(sheet, "250-BR-2011", id="Line_250BR2011", dn=250, fluid="BR", label_at=(36, 100), route=[
        offpage("in", at=(LEFT, 110), note="Harvest header from R-201P (P-206)", note_at=(36, 116)), t_h, pa["N1"]])
    line(sheet, "250-BR-2011", id="Line_250BR2011_B", dn=250, fluid="BR", labels=False, route=[
        t_h.branch, (60, 150), pb["N1"]])
    t_d = tee("BR_TD", at=(80, 84), branch="right", branch_dn=200)
    harvest = line(sheet, "200-BR-2012", id="Line_200BR2012", dn=200, fluid="BR", label_at=(152, 56), route=[
        pa["N2"], valve("BR_NRA", "CheckValve", at=(80, 96)), t_d, (80, 64), (175, 64), t201["N1"]])
    line(sheet, "200-BR-2012", id="Line_200BR2012_B", dn=200, fluid="BR", labels=False, route=[
        pb["N2"], (80, 136), (96, 136), valve("BR_NRB", "CheckValve", at=(96, 118)), (96, 84), t_d.branch])
    # Feed to the centrifuges, A duty (variable speed), B spare
    t_f = tee("BR_TF", at=(270, 205), branch="down", branch_dn=200)
    line(sheet, "200-BR-2013", id="Line_200BR2013", dn=200, fluid="BR", label_at=(222, 200), route=[
        t201["N9"], valve("BR_HVT", "BallValve", at=(190, 197)), (190, 205), t_f, fa["N1"]])
    line(sheet, "200-BR-2013", id="Line_200BR2013_B", dn=200, fluid="BR", labels=False, route=[
        t_f.branch, (270, 235), fb["N1"]])
    t_g = tee("BR_TG", at=(306, 170), branch="down", branch_dn=150)
    line(sheet, "150-BR-2014", id="Line_150BR2014", dn=150, fluid="BR", label_at=(350, 165), route=[
        fa["N2"], valve("BR_NRFA", "CheckValve", at=(290, 189)), (290, 170), t_g,
        offpage("out", at=(RIGHT, 170), note="To S-301A to C (P-301)", note_at=(384, 176))])
    line(sheet, "150-BR-2014", id="Line_150BR2014_B", dn=150, fluid="BR", labels=False, route=[
        fb["N2"], (290, 222), (306, 222), valve("BR_NRFB", "CheckValve", at=(306, 205)), t_g.branch])
    # LP-steam coil on TIC-2052
    tv = valve("LS_TV2052", "GlobeValve", at=(120, 175), tag="TV-2052")
    line(sheet, "50-LS-2054", id="Line_50LS2054", dn=50, fluid="LS", label_at=(70, 170), route=[
        offpage("in", at=(LEFT, 175), note="LP steam", note_at=(26, 170)), tv, t201["C1"]])
    line(sheet, "25-CD-2055", id="Line_25CD2055", dn=25, fluid="CD", label_at=(252, 165), route=[
        t201["C2"], (236, 175), valve("CD_ST", "SteamTrap", at=(246, 175)),
        offpage("out", at=(260, 175), note="drain", note_at=(266, 180))])
    instrument(sheet, "FI-2053", at=(130, 46), sensing=harvest, sensing_at=(130, 64))
    instrument(sheet, "LIC-2051", at=(230, 52), sensing=t201["L1"])
    instrument(sheet, "TIC-2052", at=(120, 150), sensing=t201["T1"], signal_to=tv)
    note(sheet, "T-201: about 2500 m3, agitated (A-202), insulated, LP-steam coil on TIC-2052 holding at or above 323 K "
         "(D-005, D-024). Harvest 280 m3/h in about 4 h.", at=(10, 254), size=2.5)
    note(sheet, "LIC-2051 sets the feed to S-301A to C by the speed of P-203A (variable speed, D-024). Pumps: A duty, "
         "B spare. 150-BR-2014 heat-traced and insulated at 323 K (D-005).", at=(10, 260), size=2.5)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
