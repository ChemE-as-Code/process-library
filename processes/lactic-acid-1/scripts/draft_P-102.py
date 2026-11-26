"""P-102 lime slaking and milk-of-lime ring main (provenance script; the XML is the source).

    cheme sheet new P-102 --force --title 'Lime slaking and milk-of-lime ring main'
    cheme run scripts/draft_P-102.py pid/P-102.xml

Quicklime silo V-102, weigh feeder X-102, slaker R-101 with its cooling coil, P-107A/B to the
milk-of-lime tank T-105 and the ring main pumps P-106A/B with the ring's return (D-018, D-022).
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-102.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"


def pump_pair(a, b, x, y, dn_s, num_s, src, dn_d, num_d, dst, fluid):
    """Pumps A (x, y) and B (x + 45, y) as on P-101: suction header at y + 18, discharge up from B."""
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


# ---- Quicklime silo V-102 and weigh feeder X-102 ----
v102 = equipment(sheet, "Silo", "V-102", shape="SILO_SHAPE", at=(50, 95),
                 nozzles=[Nozzle("N1", (0, -15), 100), Nozzle("N2", (0, 15), 150), Nozzle("L1", (9, -12))])
x102 = equipment(sheet, "Feeder", "X-102", shape="MIXER_SHAPE", at=(50, 150),
                 nozzles=[Nozzle("N1", (0, -8), 150), Nozzle("N2", (8, 0), 150), Nozzle("W1", (-8, 0))])
line(sheet, "100-QL-1110", dn=100, fluid="QL", route=[
    offpage("in", at=(12, 40), note="Quicklime from trucks (pneumatic)"), (50, 40), v102["N1"]])
line(sheet, "150-QL-1104", dn=150, fluid="QL", route=[v102["N2"], x102["N1"]])

# ---- Slaker R-101 with its cooling coil and vent ----
r101 = equipment(sheet, "Vessel", "R-101", shape=VESSEL, at=(130, 190), scale=1.4,
                 nozzles=[Nozzle("N1", (-6, -20), 150), Nozzle("N2", (-14, -12), 80),
                          Nozzle("N3", (0, 20), 80), Nozzle("N4", (14, -14), 150),
                          Nozzle("C1", (-14, 10), 100), Nozzle("C2", (-14, 0), 100),
                          Nozzle("T1", (-14, 17))])
line(sheet, "150-QL-1104", id="Line_150QL1104_F", dn=150, fluid="QL", labels=False,
     route=[x102["N2"], (124, 150), r101["N1"]])
water = line(sheet, "80-PW-1105", dn=80, fluid="PW", route=[
    offpage("in", at=(12, 178), note="Process water (slaking)"),
    valve("FV1105", "GlobeValve", at=(90, 178), tag="FV-1105"), r101["N2"]])
line(sheet, "150-VT-1106", dn=150, fluid="VT", route=[
    r101["N4"], (160, 176), offpage("out", at=(160, 12), note="To wet scrubber", note_at=(178, 14))])
tv1033 = valve("TV1033", "GlobeValve", at=(80, 200), tag="TV-1033")
line(sheet, "100-CW-1107", dn=100, fluid="CW", labels=False, route=[
    offpage("in", at=(12, 200), note="CW supply"), tv1033, r101["C1"]])
line(sheet, "100-CW-1108", dn=100, fluid="CW", labels=False, route=[
    r101["C2"], offpage("out", at=(12, 190), note="CW return")])

# ---- P-107A/B to the milk-of-lime tank T-105 ----
t105 = equipment(sheet, "Tank", "T-105", shape=VESSEL, at=(260, 150), scale=1.4,
                 nozzles=[Nozzle("N1", (-6, -20), 80), Nozzle("N2", (6, -20), 100),
                          Nozzle("N3", (0, 20), 150), Nozzle("L1", (14, -10))])
pump_pair("P-107A", "P-107B", 175, 225, 80, "80-ML-1101",
          [r101["N3"], valve("R101_HV", "GateValve", at=(130, 228)), (130, 243)],
          80, "80-ML-1101", [(220, 110), (254, 110), t105["N1"]], "ML")

# ---- Ring main pumps P-106A/B, supply and return ----
pump_pair("P-106A", "P-106B", 300, 215, 150, "150-ML-1109",
          [t105["N3"], valve("T105_HV", "GateValve", at=(260, 200)), (260, 233)],
          100, "100-ML-1102", [(345, 80), offpage("out", at=(414, 80), note="Ring main to the fermenters")], "ML")
pv1035 = valve("PV1035", "GlobeValve", at=(320, 40), tag="PV-1035")
ret = line(sheet, "100-ML-1103", dn=100, fluid="ML", route=[
    offpage("in", at=(414, 40), note="Ring main return"), pv1035, (266, 40), t105["N2"]])

# ---- Instruments ----
instrument(sheet, "LI-1031", at=(80, 62), sensing=v102["L1"])
instrument(sheet, "WIC-1032", at=(22, 165), sensing=x102["W1"])
instrument(sheet, "TIC-1033", at=(95, 222), sensing=r101["T1"], signal_to=tv1033)
instrument(sheet, "LIC-1034", at=(292, 125), sensing=t105["L1"])
instrument(sheet, "PIC-1035", at=(345, 25), sensing=ret, sensing_at=(345, 40), signal_to=pv1035)
instrument(sheet, "FIL-1036", at=(385, 56), sensing=ret, sensing_at=(385, 40))

# ---- Notes ----
note(sheet, "V-102: bin vent filter; X-102 rotary valve and screw, rate WIC-1032 set by LIC-1034 (D-022).",
     at=(180, 262), size=2.0)
note(sheet, "R-101: agitated, cooling coil to 323 K (Q1 820 kW); grit screen at the outlet (D-006, D-022).",
     at=(180, 268), size=2.0)
note(sheet, "Ring main DN 100 past every fermenter and seed stage 5 (P-201 to P-203); PV-1035 holds "
     "the ring pressure, FIL-1036 low return flow alarms (D-018). Pumps: A duty, B spare.",
     at=(10, 280), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
