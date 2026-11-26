"""P-103 continuous steriliser (provenance script; the XML is hand-maintained after the draft).

    cheme sheet new P-103 --force --title 'Continuous steriliser'
    cheme run scripts/draft_P-103.py pid/P-103.xml

Feed pumps P-104A/B, regenerator E-101, steam heater E-102, holding tube X-101, sterile-side
booster P-108A/B, E-101 hot side, trim cooler E-103, back-pressure valve PV-1026 and the divert
pair XV-1025A/B (D-015). Raw medium runs left to right at the bottom, the sterile medium back
along the top.
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-103.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
PHE = "PLATE_TYPE_HEAT_EXCHANGER_SHAPE"


def pump_pair(a, b, x, y, dn_s, num_s, src, dn_d, num_d, dst, fluid, s_label_at=None):
    """Pumps A (x, y) and B (x + 45, y), suction header at y + 18 from the left, the
    discharge header leaving B upwards at y - 37; A joins both by tees (as on P-101)."""
    pa = equipment(sheet, "CentrifugalPump", a, shape=PUMP, at=(x, y),
                   nozzles=[Nozzle("N1", (-7.5, 0), dn_s), Nozzle("N2", (0, -7.5), dn_d)])
    pb = equipment(sheet, "CentrifugalPump", b, shape=PUMP, at=(x + 45, y),
                   nozzles=[Nozzle("N1", (-7.5, 0), dn_s), Nozzle("N2", (0, -7.5), dn_d)])
    key = a.replace("-", "")
    ts = tee(f"{key}_TS", at=(x - 18, y + 18), branch="up")
    td = tee(f"{key}_TD", at=(x + 45, y - 37), branch="left")
    sline = line(sheet, num_s, dn=dn_s, fluid=fluid, label_at=s_label_at, route=[
        *src, ts, (x + 22, y + 18), (x + 22, y),
        valve(f"{key}_HVSB", "GateValve", at=(x + 30, y)), pb["N1"]])
    dline = line(sheet, num_d, id=f"Line_{key}_DB", dn=dn_d, fluid=fluid, route=[
        pb["N2"], valve(f"{key}_NRB", "SwingCheckValve", at=(x + 45, y - 15)),
        valve(f"{key}_HVDB", "GateValve", at=(x + 45, y - 25)), td, *dst])
    line(sheet, num_s, id=f"Line_{key}_SA", dn=dn_s, fluid=fluid, labels=False,
         route=[ts.branch, valve(f"{key}_HVSA", "GateValve", at=(x - 18, y + 8)),
                (x - 18, y), pa["N1"]])
    line(sheet, num_d, id=f"Line_{key}_DA", dn=dn_d, fluid=fluid, labels=False,
         route=[pa["N2"], valve(f"{key}_NRA", "SwingCheckValve", at=(x, y - 15)),
                valve(f"{key}_HVDA", "GateValve", at=(x, y - 25)), (x, y - 37), td.branch])
    return sline, dline


# ---- Feed: medium from V-101 (P-101) or once-through process water ----
tw = tee("P104_TW", at=(42, 233), branch="down", branch_dn=150)
e101 = equipment(sheet, "PlateHeatExchanger", "E-101", shape=PHE, at=(170, 155),
                 nozzles=[Nozzle("C1", (-10, 5), 200), Nozzle("C2", (10, 5), 200),
                          Nozzle("H1", (10, -5), 200), Nozzle("H2", (-10, -5), 200)])
feed = pump_pair("P-104A", "P-104B", 80, 215, 250, "250-PM-1004",
                 [offpage("in", at=(12, 233), note="Medium from V-101 (P-101)"), tw],
                 200, "200-PM-1005", [(125, 160), e101["C1"]], "PM")
line(sheet, "150-PW-1019", dn=150, fluid="PW", route=[
    offpage("in", at=(12, 270), note="Process water (re-sterilisation)"), (42, 270),
    valve("XV1034", "BallValve", at=(42, 254), tag="XV-1034"), tw.branch])

# ---- E-102 steam heater, X-101 holding tube ----
e102 = equipment(sheet, "PlateHeatExchanger", "E-102", shape=PHE, at=(220, 155),
                 nozzles=[Nozzle("P1", (-10, -5), 200), Nozzle("P2", (10, -5), 200),
                          Nozzle("S1", (10, 5), 200), Nozzle("S2", (-10, 5), 80)])
line(sheet, "200-PM-1012", dn=200, fluid="PM", route=[e101["C2"], (195, 160), (195, 150), e102["P1"]])
x101 = equipment(sheet, "Vessel", "X-101", shape=VESSEL, at=(262, 160), scale=(0.6, 1.2),
                 nozzles=[Nozzle("N1", (0, 18), 200), Nozzle("N2", (0, -18), 200)])
heated = line(sheet, "200-PM-1013", dn=200, fluid="PM", label_at=(238, 140), route=[
    e102["P2"], (242, 150), (242, 200), (262, 200), x101["N1"]])
tv1022 = valve("TV1022", "GlobeValve", at=(230, 190), tag="TV-1022")
line(sheet, "200-LS-1021", dn=200, fluid="LS", labels=False, route=[
    offpage("in", at=(230, 235), note="LP steam 200-LS-1021"), tv1022, e102["S1"]])
line(sheet, "80-SC-1022", dn=80, fluid="SC", labels=False, route=[
    e102["S2"], valve("E102_ST", "SteamTrap", at=(210, 185)),
    offpage("out", at=(210, 287), note="Condensate 80-SC-1022", note_at=(235, 282))])

# ---- Sterile side: X-101 outlet, booster P-108A/B, E-101 hot side, E-103 ----
e103 = equipment(sheet, "PlateHeatExchanger", "E-103", shape=PHE, at=(125, 100),
                 nozzles=[Nozzle("M1", (10, -5), 200), Nozzle("M2", (-10, -5), 200),
                          Nozzle("W1", (-10, 5), 150), Nozzle("W2", (10, 5), 150)])
hold, boosted = pump_pair("P-108A", "P-108B", 322, 92, 200, "200-SM-1006",
                          [x101["N2"], (262, 110)],
                          200, "200-SM-1014", [(367, 40), (180, 40), e101["H1"]], "SM",
                          s_label_at=(290, 122))
regen = line(sheet, "200-SM-1015", dn=200, fluid="SM", label_at=(148, 115),
             route=[e101["H2"], (160, 95), e103["M1"]])
tv1027 = valve("TV1027", "GlobeValve", at=(115, 122), tag="TV-1027")
line(sheet, "150-CW-1023", dn=150, fluid="CW", labels=False, route=[
    offpage("in", at=(115, 145), note="CW supply", note_at=(98, 150)), tv1027, e103["W1"]])
line(sheet, "150-CW-1024", dn=150, fluid="CW", labels=False, route=[
    e103["W2"], offpage("out", at=(135, 130), note="CW return")])

# ---- Back pressure, divert pair, sterile header ----
pv1026 = valve("PV1026", "GlobeValve", at=(100, 68), tag="PV-1026")
td = tee("XV1025_TD", at=(100, 45), branch="left")
xv1025a = valve("XV1025A", "BallValve", at=(220, 20), tag="XV-1025A")
cooled = line(sheet, "200-SM-1016", dn=200, fluid="SM", route=[
    e103["M2"], (100, 95), pv1026, td, (100, 20), xv1025a,
    offpage("out", at=(414, 20), note="Sterile medium header 200-SM-2001 (P-203, P-201)")])
t3 = tee("XV1025_T3", at=(62, 45), branch="up", branch_dn=150)
xv1025b = valve("XV1025B", "BallValve", at=(82, 45), tag="XV-1025B")
line(sheet, "200-PM-1007", dn=200, fluid="PM", route=[
    td.branch, xv1025b, t3, offpage("out", at=(12, 45), note="Divert to V-101 (P-101)")])
line(sheet, "150-WW-1018", dn=150, fluid="WW", route=[
    t3.branch, valve("XV1032", "BallValve", at=(62, 30), tag="XV-1032"),
    offpage("out", at=(62, 10), note="Wastewater", note_at=(78, 12))])

# ---- Instruments ----
instrument(sheet, "FIC-1021", at=(142, 182), sensing=feed[1], sensing_at=(142, 160))
instrument(sheet, "TIC-1022", at=(252, 222), sensing=heated, sensing_at=(252, 200), signal_to=tv1022,
           signal_points=[(237.2, 222)])
instrument(sheet, "PIC-1029", at=(318, 128), sensing=hold, sensing_at=(298, 110))
instrument(sheet, "US-1025", at=(250, 62), signal_to=xv1025a)
instrument(sheet, "UY-1025", at=(82, 62), signal_to=xv1025b)
instrument(sheet, "TT-1023", at=(270, 76), sensing=hold, sensing_at=(270, 110), signal_to="Inst_US1025")
instrument(sheet, "TT-1024", at=(286, 90), sensing=hold, sensing_at=(286, 110), signal_to="Inst_US1025")
instrument(sheet, "PDT-1028", at=(150, 72), sensing=regen, sensing_at=(150, 95), signal_to="Inst_US1025")
instrument(sheet, "PIC-1026", at=(80, 80), sensing=cooled, sensing_at=(100, 80), signal_to=pv1026)
instrument(sheet, "TIC-1027", at=(90, 122), sensing=cooled, sensing_at=(100, 88), signal_to=tv1027)

# ---- Notes ----
note(sheet, "STERILE BOUNDARY: spec break at the X-101 outlet; downstream sterile class SS316L, "
     "orbital-welded, drainable (D-020).", at=(60, 250), size=2.0)
note(sheet, "E-101: sterile side above raw side by booster P-108A/B; PDT-1028 (sterile out minus "
     "raw in) low diverts (D-015).", at=(60, 256), size=2.0)
note(sheet, "Divert (C&E I-101): TT-1023/1024 < 411 K or PDT-1028 low: US-1025 closes XV-1025A, "
     "UY-1025 opens XV-1025B.", at=(60, 262), size=2.0)
note(sheet, "Before each campaign: re-sterilised on once-through water (XV-1034), 413 K, 30 min, "
     "to wastewater (XV-1032).", at=(60, 268), size=2.0)
note(sheet, "No hot standby and no water into V-101 (D-015). Pumps: A duty, B spare.",
     at=(60, 274), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
