"""P-01: control loops of the reproduced FVC heat-pump column, CS1 and CS2 (#335, tracker #333).

Drawn from our own reading of the case (../../source.yaml case.control_structures and
../../inputs.yaml control), not traced from the publication. Tags are ours; the note on the sheet
maps them to the block names of the source (COLUMN, COMP1-3, HEX1-3, COND, FLASH-D, FLASH-R, V1-V8).
DN values are indicative only (nothing is sized here).

Run from case/ (cheme-as-code's interpreter has pyDEXPI):

    cheme sheet new P-01 --force
    cheme run scripts/draft_P-01.py pid/P-01.xml
    cheme render pid/P-01.xml -o P-01.svg
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-01.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
COMP = "COMPRESSOR_CENTRIFUGAL_SHAPE"
Y = 36            # compressor train axis


def hx(tag, at, shell_up=False, label_dy=-12, shell_dn=(100, 100), tube_dn=(150, 150)):
    sy = -7 if shell_up else 7
    return equipment(sheet, "TubularHeatExchanger", tag, shape=HX, at=at,
                     nozzles=[Nozzle("T1", (-17.5, 0), tube_dn[0]), Nozzle("T2", (17.5, 0), tube_dn[1]),
                              Nozzle("S1", (-7, sy), shell_dn[0]), Nozzle("S2", (7, sy), shell_dn[1])],
                     label_at=(at[0], at[1] + label_dy))


def comp(tag, x, extra=(), suction_dn=150):
    return equipment(sheet, "CentrifugalCompressor", tag, shape=COMP, at=(x, Y), scale=1.5,
                     nozzles=[Nozzle("N1", (-11.25, 0), suction_dn), Nozzle("N2", (11.25, 0), 150), *extra],
                     label_at=(x - 2, Y - 15))


# --- equipment -------------------------------------------------------------------------------
c101 = equipment(sheet, "ProcessColumn", "C-101", shape="COLUMN_SHAPE", at=(45, 140), scale=(1.0, 3.6),
                 nozzles=[Nozzle("N1", (0, -90), 250), Nozzle("N2", (10, -80), 80),
                          Nozzle("N3", (-10, 30), 80), Nozzle("N4", (0, 90), 100),
                          Nozzle("N5", (10, 68), 250), Nozzle("N6", (-10, 74), 25),
                          Nozzle("N7", (-10, 86), 25), Nozzle("N8", (-10, 52), 25),
                          Nozzle("N9", (-10, -84), 25)],
                 label_at=(58, 140))
k101 = comp("K-101", 175, suction_dn=250)
e101 = hx("E-101", (213, Y))
k102 = comp("K-102", 252)
e102 = hx("E-102", (290, Y))
k103 = comp("K-103", 329)
e103 = hx("E-103", (375, 80), label_dy=-10, shell_dn=(100, 200))
e104 = hx("E-104", (375, 130), shell_up=True, label_dy=12, shell_dn=(80, 80), tube_dn=(100, 150))
v101 = equipment(sheet, "Vessel", "V-101", shape=VESSEL, at=(150, 112), scale=(1.0, 1.2),
                 nozzles=[Nozzle("N1", (10, -12), 100), Nozzle("N2", (0, -18), 100),
                          Nozzle("N3", (0, 18), 80), Nozzle("N4", (-10, 8), 25)],
                 label_at=(176, 122))
v102 = equipment(sheet, "Vessel", "V-102", shape=VESSEL, at=(270, 215), scale=(1.0, 1.2),
                 nozzles=[Nozzle("N1", (10, -6), 200), Nozzle("N2", (-10, -10), 250),
                          Nozzle("N3", (0, 18), 50), Nozzle("N4", (-10, 6), 25)],
                 label_at=(292, 228))
p101 = equipment(sheet, "CentrifugalPump", "P-101", shape=PUMP, at=(160, 150),
                 nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (0, -7.5), 80)], label_at=(150, 162))
p102 = equipment(sheet, "CentrifugalPump", "P-102", shape=PUMP, at=(140, 262),
                 nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 100)], label_at=(158, 266))
p103 = equipment(sheet, "CentrifugalPump", "P-103", shape=PUMP, at=(290, 255),
                 nozzles=[Nozzle("N1", (-7.5, 0), 50), Nozzle("N2", (0, -7.5), 50)], label_at=(276, 266))

# --- feed ------------------------------------------------------------------------------------
fv101 = valve("FV101", tag="FV-101", at=(24, 170))
line(sheet, "PL-001", dn=80, fluid="Methanol/water feed", route=[
    offpage("in", at=(9, 170), note="feed", note_at=(22, 178)), fv101, c101["N3"]], labels=False)

# --- overhead vapour, flash vapour circulation and the compressor train ---------------------
tfvc = tee("TFVC", at=(150, Y), branch="down", branch_dn=100)
line(sheet, "PL-002", dn=250, fluid="Methanol vapour", route=[
    c101["N1"], (45, Y), tfvc, k101["N1"]], label_at=(95, Y - 5))
line(sheet, "PL-003", dn=100, fluid="Flash vapour circulation (FVC)", route=[
    tfvc.branch, v101["N2"]], label_at=(132, 70))
line(sheet, "PL-004", dn=150, fluid="Compressed vapour", route=[k101["N2"], e101["T1"]], labels=False)
line(sheet, "PL-005", dn=150, fluid="Compressed vapour", route=[e101["T2"], k102["N1"]], labels=False)
line(sheet, "PL-006", dn=150, fluid="Compressed vapour", route=[k102["N2"], e102["T1"]], labels=False)
line(sheet, "PL-007", dn=150, fluid="Compressed vapour", route=[e102["T2"], k103["N1"]], labels=False)
line(sheet, "PL-008", dn=150, fluid="Compressed vapour", route=[
    k103["N2"], (350, Y), (350, 80), e103["T1"]], label_at=(357, 60))
line(sheet, "PL-009", dn=150, fluid="Methanol, condensing", route=[
    e103["T2"], (405, 80), (405, 130), e104["T2"]], labels=False)
pv103 = valve("PV103", tag="PV-103", at=(250, 170))
line(sheet, "PL-010", dn=100, fluid="Methanol condensate", route=[
    e104["T1"], (350, 130), (350, 170), pv103, (170, 170), (170, 100), v101["N1"]], label_at=(225, 165))

# --- reflux and distillate ------------------------------------------------------------------
tsp = tee("TSP", at=(115, 138), branch="down", branch_dn=80)
fv107 = valve("FV107", tag="FV-107", at=(75, 100))
line(sheet, "PL-011", dn=80, fluid="Methanol", route=[v101["N3"], (150, 150), p101["N1"]], labels=False)
line(sheet, "PL-012", dn=80, fluid="Reflux", route=[
    p101["N2"], (160, 138), tsp, (75, 138), fv107, (75, 60), c101["N2"]], label_at=(84, 80))
lv106 = valve("LV106", tag="LV-106", at=(115, 150))
line(sheet, "PL-013", dn=80, fluid="Methanol product", route=[
    tsp.branch, lv106, offpage("out", at=(115, 166), note="methanol, 0.99", rotation=90)], labels=False)

# --- bottoms circuit: sump -> E-101 -> E-102 -> E-103 -> V-102 (FLASH-R) --------------------
lv109 = valve("LV109", tag="LV-109", at=(175, 248))
line(sheet, "PL-014", dn=100, fluid="Water (bottoms withdrawal)", route=[
    c101["N4"], (45, 262), p102["N1"]], labels=False)
line(sheet, "PL-015", dn=100, fluid="Water (bottoms withdrawal)", route=[
    p102["N2"], (140, 248), lv109, (206, 248), e101["S1"]], label_at=(190, 243))
line(sheet, "PL-016", dn=100, fluid="Water, heating", route=[
    e101["S2"], (220, 54), (283, 54), e102["S1"]], labels=False)
line(sheet, "PL-017", dn=100, fluid="Water, heating", route=[
    e102["S2"], (297, 54), (335, 54), (335, 95), (368, 95), e103["S1"]], labels=False)
line(sheet, "PL-018", dn=200, fluid="Water, two-phase", route=[
    e103["S2"], (382, 105), (310, 105), (310, 209), v102["N1"]], label_at=(322, 150))
line(sheet, "PL-019", dn=250, fluid="Steam (boil-up)", route=[
    v102["N2"], (65, 205), (65, 208), c101["N5"]], label_at=(120, 200))
lv110 = valve("LV110", tag="LV-110", at=(305, 240))
line(sheet, "PL-020", dn=50, fluid="Water", route=[v102["N3"], (270, 255), p103["N1"]], labels=False)
line(sheet, "PL-021", dn=50, fluid="Water product", route=[
    p103["N2"], (290, 240), lv110, offpage("out", at=(322, 240), note="water, 0.9999")], labels=False)

# --- trim condenser cooling water (PC1) ---------------------------------------------------
pv102 = valve("PV102", tag="PV-102", at=(345, 115))
line(sheet, "CWS-022", dn=80, fluid="Cooling water", route=[
    offpage("in", at=(326, 115), note="CWS"), pv102, (368, 115), e104["S1"]], labels=False)
line(sheet, "CWR-023", dn=80, fluid="Cooling water", route=[
    e104["S2"], (382, 112), offpage("out", at=(397, 112), note="CWR")], labels=False)

# --- instruments: CS1 ----------------------------------------------------------------------
instrument(sheet, "FIC-101", at=(24, 155), sensing="Line_PL001_S1", sensing_at=(15, 170), signal_to=fv101)
instrument(sheet, "PIC-102", at=(20, 56), sensing=c101["N9"], signal_to=pv102,
           signal_points=[(20, 8), (345, 8)])
instrument(sheet, "PIC-103", at=(272, 182), sensing="Line_PL010_S1", sensing_at=(272, 170), signal_to=pv103)
jic105 = instrument(sheet, "JIC-105", at=(203, 14), sensing=k101["N2"], sensing_at=(186, Y))
instrument(sheet, "TIC-104", at=(20, 192), sensing=c101["N8"], signal_to=jic105,
           signal_points=[(12, 192), (12, 14), (196, 14)])
instrument(sheet, "LIC-106", at=(128, 124), sensing=v101["N4"], signal_to=lv106)
ffic107 = instrument(sheet, "FFIC-107", at=(92, 118), sensing="Line_PL012_S1", sensing_at=(75, 118), signal_to=fv107)
instrument(sheet, "LIC-109", at=(20, 218), sensing=c101["N6"], signal_to=lv109,
           signal_points=[(20, 240), (175, 240)])
instrument(sheet, "LIC-110", at=(245, 228), sensing=v102["N4"], signal_to=lv110,
           signal_points=[(245, 236), (305, 236)])
# --- CS2 adds the distillate composition loop --------------------------------------------
instrument(sheet, "AIC-108", at=(96, 160), sensing="Line_PL013_S1", sensing_at=(115, 158), signal_to=ffic107)

note(sheet, "Feed 100 kmol/h methanol/water at 30 C. CS1: TIC-104 holds stage 35 by the total compressor power (JIC-105 sets K-101; K-102 and K-103 follow in fixed ratio).",
     at=(12, 272), size=2.2)
note(sheet, "CS1: FFIC-107 keeps reflux / distillate fixed. CS2: AIC-108 (distillate methanol, 3 min analyser lag) resets the ratio.",
     at=(12, 276), size=2.2)
note(sheet, "PIC-102 holds the column top pressure by the E-104 cooling (and so the FVC flow); PIC-103 holds the compressor discharge by PV-103.",
     at=(12, 280), size=2.2)
note(sheet, "Source names: C-101 COLUMN, K-101..103 COMP1..3, E-101..103 HEX1..3, E-104 COND, V-101 FLASH-D, V-102 FLASH-R,",
     at=(12, 284), size=2.2)
note(sheet, "FV-101 V1, PV-103 V2, FV-107 V3, LV-106 V4, LV-109 V6, LV-110 V8. Drawn by us for #335; DN indicative, not sized.",
     at=(12, 288), size=2.2)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
