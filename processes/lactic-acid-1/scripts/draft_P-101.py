"""P-101 medium preparation (generated sheet, `cheme regen P-101`).

Syrup and CSL receipt, storage and day tanks and the in-line blend of syrup, CSL and process
water into the medium tank V-101 (D-014). The steriliser it feeds is on P-103 (D-015).
Layout (A3 frame): syrup top left, CSL below it, V-101 right.
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-101.xml")
sheet = Sheet.load(target)

TANK = "TANK_CONE_ROOF_SHAPE"
VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"


def tank(tag, at, scale=1.0, dn=150, dn_out=None):
    """A vertical tank: N1 top inlet, N2 bottom outlet, L1 level connection on the right."""
    hw, hh = 10 * scale, 12.5 * scale
    return equipment(
        sheet, "Tank", tag, shape=TANK, at=at, scale=scale,
        nozzles=[Nozzle("N1", (0, -hh), dn), Nozzle("N2", (0, hh), dn_out or dn),
                 Nozzle("L1", (hw, -hh / 2))],
    )


def pump_pair(a, b, x, y, dn_s, num_s, src, dn_d, num_d, dst, fluid):
    """Pumps A (x, y) and B (x + 45, y), suction header at y + 18 from the left, the
    discharge header leaving B upwards at y - 37; A joins both by tees."""
    pa = equipment(sheet, "CentrifugalPump", a, shape=PUMP, at=(x, y),
                   nozzles=[Nozzle("N1", (-7.5, 0), dn_s), Nozzle("N2", (0, -7.5), dn_d)])
    pb = equipment(sheet, "CentrifugalPump", b, shape=PUMP, at=(x + 45, y),
                   nozzles=[Nozzle("N1", (-7.5, 0), dn_s), Nozzle("N2", (0, -7.5), dn_d)])
    key = a.replace("-", "")
    ts = tee(f"{key}_TS", at=(x - 18, y + 18), branch="up")
    td = tee(f"{key}_TD", at=(x + 45, y - 37), branch="left")
    sline = line(sheet, num_s, dn=dn_s, fluid=fluid, route=[
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


# ---- Syrup: receipt, storage T-101A/B, P-101A/B, day tank T-103 ----
t101a = tank("T-101A", (60, 100), 1.2)
t101b = tank("T-101B", (108, 100), 1.2)
t103 = tank("T-103", (230, 100))
tr = tee("T101_TR", at=(60, 48), branch="down")
line(sheet, "150-PM-1008", dn=150, fluid="PM", route=[
    offpage("in", at=(12, 48), note="Syrup 70 wt% receipt"), tr, (108, 48), t101b["N1"]])
line(sheet, "150-PM-1008", id="Line_150PM1008_A", dn=150, fluid="PM", labels=False,
     route=[tr.branch, t101a["N1"]])
tm = tee("T101_TM", at=(108, 140), branch="up")
pump_pair("P-101A", "P-101B", 140, 122, 150, "150-PM-1009",
          [t101a["N2"], valve("T101A_HV", "GateValve", at=(60, 132)), (60, 140), tm],
          150, "150-PM-1009", [(185, 66), (230, 66), t103["N1"]], "PM")
line(sheet, "150-PM-1009", id="Line_150PM1009_B", dn=150, fluid="PM", labels=False,
     route=[t101b["N2"], tm.branch])

# ---- V-101 medium tank and the blend: syrup, CSL, process water on ratio control ----
v101 = equipment(sheet, "Vessel", "V-101", shape=VESSEL, at=(370, 130), scale=1.6,
                 nozzles=[Nozzle("N1", (-8, -24), 150), Nozzle("N2", (8, -24), 150),
                          Nozzle("N3", (-16, 16), 40), Nozzle("N4", (16, -16), 200),
                          Nozzle("N5", (0, 24), 250), Nozzle("L1", (-16, -10))])
fv1011 = valve("FV1011", "GlobeValve", at=(342, 66), tag="FV-1011")
syrup = pump_pair("P-102A", "P-102B", 270, 122, 150, "150-PM-1001",
                  [t103["N2"], valve("T103_HV", "GateValve", at=(230, 132)), (230, 140)],
                  150, "150-PM-1001", [(315, 66), fv1011, (362, 66), v101["N1"]], "PM")
fv1012 = valve("FV1012", "GlobeValve", at=(330, 32), tag="FV-1012")
water = line(sheet, "150-PW-1003", dn=150, fluid="PW", route=[
    offpage("in", at=(12, 32), note="Process water from BL"), fv1012, (378, 32), v101["N2"]])

# ---- CSL: receipt, T-102, P-103A/B, day tank T-104, P-105A/B dosing ----
t102 = tank("T-102", (60, 230), dn=50)
t104 = tank("T-104", (190, 230), dn=50, dn_out=40)
line(sheet, "50-PM-1010", dn=50, fluid="PM", route=[
    offpage("in", at=(12, 192), note="Corn steep liquor receipt"), (60, 192), t102["N1"]])
pump_pair("P-103A", "P-103B", 100, 252, 50, "50-PM-1011",
          [t102["N2"], valve("T102_HV", "GateValve", at=(60, 261)), (60, 270)],
          50, "50-PM-1011", [(145, 194), (190, 194), t104["N1"]], "PM")
fv1013 = valve("FV1013", "GlobeValve", at=(315, 194), tag="FV-1013")
csl = pump_pair("P-105A", "P-105B", 230, 252, 40, "40-PM-1002",
                [t104["N2"], valve("T104_HV", "GateValve", at=(190, 261)), (190, 270)],
                40, "40-PM-1002", [(275, 194), fv1013, (345, 194), (345, 150), v101["N3"]], "PM")

# ---- V-101 outlet to the steriliser (P-103) and the divert return from it ----
line(sheet, "250-PM-1004", dn=250, fluid="PM", route=[
    v101["N5"], valve("V101_HV", "GateValve", at=(370, 180)),
    valve("XV1033", "BallValve", at=(370, 205), tag="XV-1033"), (370, 225),
    offpage("out", at=(414, 225), note="Medium to P-103")])
line(sheet, "200-PM-1007", dn=200, fluid="PM", labels=False, route=[
    offpage("in", at=(414, 90), note="Divert 200-PM-1007 from P-103"), (400, 90),
    valve("XV1030", "BallValve", at=(400, 104), tag="XV-1030"), (400, 114), v101["N4"]])

# ---- Instruments ----
instrument(sheet, "LI-1003", at=(84, 70), sensing=t101a["L1"])
instrument(sheet, "LI-1004", at=(132, 80), sensing=t101b["L1"])
instrument(sheet, "LI-1001", at=(255, 80), sensing=t103["L1"])
instrument(sheet, "LI-1005", at=(88, 208), sensing=t102["L1"])
instrument(sheet, "LI-1002", at=(215, 208), sensing=t104["L1"])
instrument(sheet, "LIC-1014", at=(330, 115), sensing=v101["L1"])
instrument(sheet, "FIC-1011", at=(325, 50), sensing=syrup[1], sensing_at=(325, 66), signal_to=fv1011)
instrument(sheet, "FIC-1012", at=(290, 18), sensing=water, sensing_at=(290, 32), signal_to=fv1012)
instrument(sheet, "FIC-1013", at=(295, 210), sensing=csl[1], sensing_at=(295, 194), signal_to=fv1013)

# ---- Notes ----
note(sheet, "Tanks insulated, LP-steam coils hold 323 K (D-014). Pumps: A duty, B spare.",
     at=(10, 284), size=2.0)
note(sheet, "Blend in campaigns at the fill rate, 200 t/h (D-014): FIC-1011/1012/1013 "
     "in ratio to FIC-1021 (P-103), trimmed by LIC-1014.", at=(10, 289), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
