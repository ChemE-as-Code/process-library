"""Draft of P-04: topping column C-201 with its partial condenser E-201, reflux drum V-201, reflux
pumps P-201A/B, thermosyphon reboiler E-202 on LP steam and bottoms pumps P-202A/B to C-202.

Provenance only: P-04 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-04.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-016, D-020; streams S15-S17 and duties Q6, Q7 of
process/flowsheet.yaml (the column, condenser and reboiler are lumped in step C201: the
overhead, reflux and reboiler circulation lines have ASSUMED DN).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Marker,
    Nozzle,
    Sheet,
    instrument,
    label,
    offpage,
    tee,
    valve,
)
from pid_common import (  # noqa: E402
    BOTTOM,
    COLUMN,
    DRUM,
    EDGE,
    HX,
    LEFT,
    PUMP,
    TOP,
    equipment,
    fail_label,
    line,
    make_safety_valve,
    notes,
    save,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
OVHD = 45        # overhead and condenser
REFLUX = 120     # reflux run to the column
BOT = 188        # bottoms to C-202


def pump(tag, x, y, dn_in, dn_out, label_y):
    return equipment(sheet, "CentrifugalPump", tag, shape=PUMP, at=(x, y),
                     nozzles=[Nozzle("N1", (-7.5, 0), dn_in), Nozzle("N2", (0, -7.5), dn_out)],
                     label_at=(x, label_y))


# ---- equipment
c201 = equipment(sheet, "ProcessColumn", "C-201", shape=COLUMN, at=(120, 135), scale=(1.0, 2.4),
                 nozzles=[Nozzle("N1", (-10, -25), 250), Nozzle("N2", (0, -60), 700),
                          Nozzle("N3", (10, -50), 125), Nozzle("N4", (0, 60), 300),
                          Nozzle("N5", (-10, 45), 250), Nozzle("N6", (-10, 31), 450),
                          Nozzle("N7", (-10, -50), 150), Nozzle("N8", (10, 37), 50),
                          Nozzle("N9", (-10, 0), 25)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(120, 150))
e201 = equipment(sheet, "TubularHeatExchanger", "E-201", shape=HX, at=(190, OVHD),
                 nozzles=[Nozzle("T1", (-17.5, 0), 700), Nozzle("T2", (17.5, 0), 500),
                          Nozzle("S1", (7, -7), 500), Nozzle("S2", (-7, -7), 500)],
                 label_at=(190, 58))
v201 = equipment(sheet, "Vessel", "V-201", shape=DRUM, at=(260, 90), scale=(1.0, 1.6),
                 rotation=90,
                 nozzles=[Nozzle("N1", (-16, -10), 500), Nozzle("N2", (16, -10), 125),
                          Nozzle("N3", (16, 10), 150), Nozzle("N4", (-24, 2), 50),
                          Nozzle("N5", (24, 2), 50)],
                 label_at=(260, 90))
e202 = equipment(sheet, "TubularHeatExchanger", "E-202", shape=HX, at=(60, 173),
                 nozzles=[Nozzle("S1", (-7, -7), 500), Nozzle("S2", (-7, 7), 100),
                          Nozzle("T1", (7, 7), 250), Nozzle("T2", (7, -7), 450)],
                 label_at=(64, 190))
p201a = pump("P-201A", 230, 160, 150, 125, 172)
p201b = pump("P-201B", 265, 160, 150, 125, 172)
p202a = pump("P-202A", 155, 220, 300, 250, 232)
p202b = pump("P-202B", 190, 220, 300, 250, 232)

# ---- feed from LV-310 (P-03), relief of the column to the flare header
line(sheet, "CM-115", dn=250, fluid="Crude methanol", route=[
    offpage("in", at=(LEFT, 110), note="from LV-310, P-03"), c201["N1"]], label_at=(88, 102))
psv413 = valve("PSV413", "GlobeValve", tag="PSV-413", at=(95, 60))
line(sheet, "FL-443", dn=150, fluid="Relief gas", route=[
    c201["N7"], (95, 85), psv413,
    offpage("out", at=(95, TOP), note="to LP flare header", rotation=270, note_at=(75, 20))],
    label_at=(83, 40))

# ---- overhead, partial condenser on cooling water, reflux drum, off-gas to fuel
line(sheet, "PG-430", dn=700, fluid="Topping column overhead", route=[
    c201["N2"], (120, OVHD), e201["T1"]], label_at=(146, 37))
line(sheet, "PG-431", dn=500, fluid="Topping column overhead", route=[
    e201["T2"], (244, OVHD), v201["N1"]], label_at=(226, 37))
line(sheet, "CWR-441", dn=500, fluid="Cooling water return", route=[
    e201["S2"],
    offpage("out", at=(183, TOP), note="CW return", rotation=270, note_at=(169, 20))],
    label_at=(171, 28))
line(sheet, "CWS-440", dn=500, fluid="Cooling water", route=[
    offpage("in", at=(197, TOP), note="CW supply", rotation=90, note_at=(211, 20)),
    e201["S1"]], label_at=(209, 28))
pv404 = valve("PV404", "GlobeValve", tag="PV-404", at=(330, 40))
line(sheet, "FG-116", dn=125, fluid="Fuel gas", route=[
    v201["N2"], (276, 40), pv404,
    offpage("out", at=(EDGE, 40), note="to fuel gas header (B/L)")], label_at=(372, 48))

# ---- reflux: V-201 -> P-201A/B -> C-201 on the drum level
suction = tee("T433", at=(250, 180), branch="up", branch_dn=150)
line(sheet, "RF-432", dn=150, fluid="Reflux", route=[
    v201["N3"], (276, 180), suction, (215, 180), valve("HV432", "GateValve", at=(215, 173)),
    valve("SR432", "Strainer", at=(215, 166)), (215, 160), p201a["N1"]], label_at=(296, 150))
line(sheet, "RF-433", dn=150, fluid="Reflux", route=[
    suction.branch, valve("HV433", "GateValve", at=(250, 174)),
    valve("SR433", "Strainer", at=(250, 167)), (250, 160), p201b["N1"]], labels=False)
label(sheet, "Line_RF433", "LineNumber", at=(244, 177))
join = tee("T435", at=(230, 132), branch="right", branch_dn=125)
lv405 = valve("LV405", "GlobeValve", tag="LV-405", at=(180, REFLUX))
line(sheet, "RF-434", dn=125, fluid="Reflux", route=[
    p201a["N2"], valve("CV434", "SwingCheckValve", at=(230, 146)),
    valve("HV434", "GateValve", at=(230, 140)), join, (230, REFLUX), lv405, (150, REFLUX),
    (150, 85), c201["N3"]], label_at=(200, 128))
line(sheet, "RF-435", dn=125, fluid="Reflux", route=[
    p201b["N2"], valve("CV435", "SwingCheckValve", at=(265, 146)),
    valve("HV435", "GateValve", at=(265, 140)), (265, 132), join.branch], label_at=(247, 125))

# ---- thermosyphon reboiler E-202 on LP steam, condensate to the header
line(sheet, "CM-436", dn=250, fluid="Topping column bottoms", route=[
    c201["N5"], e202["T1"]], label_at=(90, 186))
line(sheet, "PG-437", dn=450, fluid="Topping column bottoms (two-phase)", route=[
    e202["T2"], c201["N6"]], label_at=(90, 158))
tv402 = valve("TV402", "GlobeValve", tag="TV-402", at=(35, 150))
line(sheet, "LS-438", dn=500, fluid="LP steam", route=[
    offpage("in", at=(LEFT, 150), note="from LP steam header"),
    tv402, (53, 150), e202["S1"]], label_at=(30, 158))
line(sheet, "CD-439", dn=100, fluid="Condensate", route=[
    e202["S2"], valve("ST439", "SteamTrap", at=(53, 205)),
    offpage("out", at=(53, BOTTOM), note="to condensate header", rotation=90,
            note_at=(76, 244))],
    label_at=(41, 222))

# ---- bottoms: P-202A/B to C-202 (P-05) on the sump level
bsuction = tee("T444", at=(128, 220), branch="down", branch_dn=300)
line(sheet, "CM-444", dn=300, fluid="Stabilised methanol", route=[
    c201["N4"], (120, 220), bsuction, valve("HV444", "GateValve", at=(134, 220)),
    valve("SR444", "Strainer", at=(141, 220)), p202a["N1"]], label_at=(108, 208))
line(sheet, "CM-445", dn=300, fluid="Stabilised methanol", route=[
    bsuction.branch, (128, 238), (175, 238), valve("HV445", "GateValve", at=(175, 232)),
    valve("SR445", "Strainer", at=(175, 226)), (175, 220), p202b["N1"]], label_at=(117, 229))
bjoin = tee("T446", at=(155, 194), branch="right", branch_dn=250)
lv408 = valve("LV408", "GlobeValve", tag="LV-408", at=(172, BOT))
line(sheet, "CM-117", dn=250, fluid="Stabilised methanol", route=[
    p202a["N2"], valve("CV117", "SwingCheckValve", at=(155, 206)),
    valve("HV117", "GateValve", at=(155, 200)), bjoin, (155, BOT), lv408,
    offpage("out", at=(EDGE, BOT), note="to C-202, P-05")], label_at=(372, 196))
line(sheet, "CM-446", dn=250, fluid="Stabilised methanol", route=[
    p202b["N2"], valve("CV446", "SwingCheckValve", at=(190, 206)),
    valve("HV446", "GateValve", at=(190, 200)), (190, 194), bjoin.branch], label_at=(202, 202))
make_safety_valve(sheet, "PSV413", label_at=(83, 60))

# ---- instruments
instrument(sheet, "FI-401", at=(60, 92), sensing="Line_CM115_S1", sensing_at=(60, 110))
instrument(sheet, "TIC-402", at=(85, 135), sensing=c201["N9"], signal_to=tv402,
           signal_points=[(35, 135)], fail_action="FC")
instrument(sheet, "PIC-404", at=(305, 58), sensing="Line_FG116_S1", sensing_at=(305, 40),
           signal_to=pv404, signal_points=[(330, 58)], fail_action="FO")
instrument(sheet, "LIC-405", at=(212, 92), sensing=v201["N4"], signal_to=lv405,
           signal_points=[(180, 92)], fail_action="FO")
instrument(sheet, "TI-407", at=(226, 62), sensing="Line_PG431_S1", sensing_at=(244, 62))
instrument(sheet, "LIC-408", at=(172, 172), sensing=c201["N8"], signal_to=lv408,
           fail_action="FC")
instrument(sheet, "PI-409", at=(140, 60), sensing="Line_PG430_S1", sensing_at=(120, 60))
instrument(sheet, "LZ-411", at=(305, 92), sensing=v201["N5"])
fail_label(sheet, "Inst_TIC402", (35, 150), "up")
fail_label(sheet, "Inst_PIC404", (330, 40), "down")
fail_label(sheet, "Inst_LIC405", (180, REFLUX), "up-left")
fail_label(sheet, "Inst_LIC408", (172, BOT), "up")

notes(sheet,
      "TIC-402: column temperature on the LP steam TV-402. PIC-404: column pressure on the "
      "off-gas PV-404. LIC-405: all condensed liquid is refluxed, on the V-201 level (D-020)",
      "LIC-408: sump level on the bottoms LV-408 to C-202. LZ-411: V-201 level low-low stops "
      "P-201A/B (C&E I-401). Pump minimum-flow protection with the pump vendor (D-020)",
      "PSV-413: C-201 and V-201 (fire, CW failure, gas blow-by through V-102), to the LP flare "
      "header. C-201, E-201, V-201 designed for full vacuum (loss of heat). DN ASSUMED (D-020)")

save(sheet, target)
