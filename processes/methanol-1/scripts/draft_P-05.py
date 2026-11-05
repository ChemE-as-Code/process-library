"""Draft of P-05: refining column C-202 with its total condenser E-203, reflux drum V-202, reflux
and product pumps P-203A/B, thermosyphon reboiler E-204 on LP steam and bottoms water pumps
P-204A/B.

Provenance only: P-05 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-05.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-016, D-020; streams S17-S19 and duties Q8, Q9 of
process/flowsheet.yaml (the column, condenser and reboiler are lumped in step C202: the
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
OVHD = 40        # overhead and condenser
REFLUX = 115     # reflux run to the column
PRODUCT = 188    # methanol product to the battery limit
BOT = 200        # bottoms water to the battery limit


def pump(tag, x, y, dn_in, dn_out, label_y):
    return equipment(sheet, "CentrifugalPump", tag, shape=PUMP, at=(x, y),
                     nozzles=[Nozzle("N1", (-7.5, 0), dn_in), Nozzle("N2", (0, -7.5), dn_out)],
                     label_at=(x, label_y))


# ---- equipment
c202 = equipment(sheet, "ProcessColumn", "C-202", shape=COLUMN, at=(120, 130), scale=(1.0, 2.4),
                 nozzles=[Nozzle("N1", (-10, -20), 250), Nozzle("N2", (0, -60), 1800),
                          Nozzle("N3", (10, -50), 300), Nozzle("N4", (0, 60), 80),
                          Nozzle("N5", (-10, 45), 400), Nozzle("N6", (-10, 31), 800),
                          Nozzle("N7", (-10, -50), 200), Nozzle("N8", (10, 48), 50),
                          Nozzle("N9", (-10, 0), 25)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(120, 145))
e203 = equipment(sheet, "TubularHeatExchanger", "E-203", shape=HX, at=(190, OVHD),
                 nozzles=[Nozzle("T1", (-17.5, 0), 1800), Nozzle("T2", (17.5, 0), 300),
                          Nozzle("S1", (7, -7), 1400), Nozzle("S2", (-7, -7), 1400)],
                 label_at=(190, 53))
v202 = equipment(sheet, "Vessel", "V-202", shape=DRUM, at=(260, 85), scale=(1.0, 1.6),
                 rotation=90,
                 nozzles=[Nozzle("N1", (-16, -10), 300), Nozzle("N2", (16, -10), 50),
                          Nozzle("N3", (16, 10), 300), Nozzle("N4", (-24, 2), 50),
                          Nozzle("N5", (24, 2), 50)],
                 label_at=(260, 85))
e204 = equipment(sheet, "TubularHeatExchanger", "E-204", shape=HX, at=(60, 168),
                 nozzles=[Nozzle("S1", (-7, -7), 1100), Nozzle("S2", (-7, 7), 200),
                          Nozzle("T1", (7, 7), 400), Nozzle("T2", (7, -7), 800)],
                 label_at=(64, 185))
p203a = pump("P-203A", 230, 155, 300, 300, 167)
p203b = pump("P-203B", 265, 155, 300, 300, 167)
p204a = pump("P-204A", 155, 228, 80, 65, 239)
p204b = pump("P-204B", 190, 228, 80, 65, 239)

# ---- feed from LV-408 (P-04), relief of the column to the flare header
line(sheet, "CM-117", dn=250, fluid="Stabilised methanol", route=[
    offpage("in", at=(LEFT, 110), note="from LV-408, P-04"), c202["N1"]], label_at=(88, 102))
psv513 = valve("PSV513", "GlobeValve", tag="PSV-513", at=(95, 55))
line(sheet, "FL-543", dn=200, fluid="Relief gas", route=[
    c202["N7"], (95, 80), psv513,
    offpage("out", at=(95, TOP), note="to flare header", rotation=270, note_at=(79, 20))],
    label_at=(83, 36))

# ---- overhead, total condenser on cooling water, reflux drum, vent to the flare header
line(sheet, "PG-530", dn=1800, fluid="Refining column overhead", route=[
    c202["N2"], (120, OVHD), e203["T1"]], label_at=(146, 32))
line(sheet, "ME-531", dn=300, fluid="Methanol condensate", route=[
    e203["T2"], (244, OVHD), v202["N1"]], label_at=(226, 32))
line(sheet, "CWR-541", dn=1400, fluid="Cooling water return", route=[
    e203["S2"],
    offpage("out", at=(183, TOP), note="CW return", rotation=270, note_at=(169, 20))],
    labels=False)
line(sheet, "CWS-540", dn=1400, fluid="Cooling water", route=[
    offpage("in", at=(197, TOP), note="CW supply", rotation=90, note_at=(211, 20)),
    e203["S1"]], labels=False)
pv504 = valve("PV504", "GlobeValve", tag="PV-504", at=(330, 35))
line(sheet, "VG-532", dn=50, fluid="Vent gas", route=[
    v202["N2"], (276, 35), pv504,
    offpage("out", at=(EDGE, 35), note="to flare header")], label_at=(372, 43))

# ---- reflux on the V-202 level; product on flow, taken off the reflux below the pumps
suction = tee("T533", at=(250, 175), branch="up", branch_dn=300)
line(sheet, "RF-533", dn=300, fluid="Methanol", route=[
    v202["N3"], (276, 175), suction, (215, 175), valve("HV533", "GateValve", at=(215, 168)),
    valve("SR533", "Strainer", at=(215, 161)), (215, 155), p203a["N1"]], label_at=(296, 140))
line(sheet, "RF-534", dn=300, fluid="Methanol", route=[
    suction.branch, valve("HV534", "GateValve", at=(250, 169)),
    valve("SR534", "Strainer", at=(250, 162)), (250, 155), p203b["N1"]], labels=False)
join = tee("T536", at=(230, 127), branch="right", branch_dn=300)
product = tee("T118", at=(200, REFLUX), branch="down", branch_dn=200)
lv505 = valve("LV505", "GlobeValve", tag="LV-505", at=(170, REFLUX))
line(sheet, "RF-535", dn=300, fluid="Methanol", route=[
    p203a["N2"], valve("CV535", "SwingCheckValve", at=(230, 141)),
    valve("HV535", "GateValve", at=(230, 135)), join, (230, REFLUX), product, lv505,
    (150, REFLUX), (150, 80), c202["N3"]], label_at=(176, 122))
line(sheet, "RF-536", dn=300, fluid="Methanol", route=[
    p203b["N2"], valve("CV536", "SwingCheckValve", at=(265, 141)),
    valve("HV536", "GateValve", at=(265, 135)), (265, 127), join.branch], labels=False)
fv507 = valve("FV507", "GlobeValve", tag="FV-507", at=(330, PRODUCT))
line(sheet, "ME-118", dn=200, fluid="Methanol", route=[
    product.branch, (200, PRODUCT), fv507,
    offpage("out", at=(EDGE, PRODUCT), note="to methanol rundown tanks (B/L)")],
    label_at=(188, 148))

# ---- thermosyphon reboiler E-204 on LP steam, condensate to the header
line(sheet, "WW-537", dn=400, fluid="Refining column bottoms", route=[
    c202["N5"], e204["T1"]], label_at=(90, 181))
line(sheet, "PG-538", dn=800, fluid="Refining column bottoms (two-phase)", route=[
    e204["T2"], c202["N6"]], label_at=(90, 153))
tv502 = valve("TV502", "GlobeValve", tag="TV-502", at=(35, 145))
line(sheet, "LS-539", dn=1100, fluid="LP steam", route=[
    offpage("in", at=(LEFT, 145), note="from LP steam header"),
    tv502, (53, 145), e204["S1"]], label_at=(30, 153))
line(sheet, "CD-542", dn=200, fluid="Condensate", route=[
    e204["S2"], valve("ST542", "SteamTrap", at=(53, 205)),
    offpage("out", at=(53, BOTTOM), note="to condensate header", rotation=90,
            note_at=(76, 244))],
    label_at=(41, 222))

# ---- bottoms water: P-204A/B to the battery limit on the sump level
bsuction = tee("T544", at=(128, 228), branch="down", branch_dn=80)
line(sheet, "WW-544", dn=80, fluid="Process water", route=[
    c202["N4"], (120, 228), bsuction, valve("HV544", "GateValve", at=(134, 228)),
    valve("SR544", "Strainer", at=(141, 228)), p204a["N1"]], labels=False)
line(sheet, "WW-545", dn=80, fluid="Process water", route=[
    bsuction.branch, (128, 244), (175, 244), valve("HV545", "GateValve", at=(175, 238)),
    valve("SR545", "Strainer", at=(175, 233)), (175, 228), p204b["N1"]], labels=False)
bjoin = tee("T546", at=(155, 205), branch="right", branch_dn=65)
lv508 = valve("LV508", "GlobeValve", tag="LV-508", at=(165, BOT))
line(sheet, "WW-119", dn=65, fluid="Process water", route=[
    p204a["N2"], valve("CV119", "SwingCheckValve", at=(155, 215)),
    valve("HV119", "GateValve", at=(155, 210)), bjoin, (155, BOT), lv508,
    offpage("out", at=(EDGE, BOT), note="to wastewater treatment (B/L)")], label_at=(380, 208))
line(sheet, "WW-546", dn=65, fluid="Process water", route=[
    p204b["N2"], valve("CV546", "SwingCheckValve", at=(190, 215)),
    valve("HV546", "GateValve", at=(190, 210)), (190, 205), bjoin.branch], labels=False)
make_safety_valve(sheet, "PSV513", label_at=(83, 55))

# ---- instruments
instrument(sheet, "FI-501", at=(60, 92), sensing="Line_CM117_S1", sensing_at=(60, 110))
instrument(sheet, "TIC-502", at=(85, 130), sensing=c202["N9"], signal_to=tv502,
           signal_points=[(35, 130)], fail_action="FC")
instrument(sheet, "PIC-504", at=(305, 53), sensing="Line_VG532_S1", sensing_at=(305, 35),
           signal_to=pv504, signal_points=[(330, 53)], fail_action="FO")
instrument(sheet, "LIC-505", at=(212, 87), sensing=v202["N4"], signal_to=lv505,
           signal_points=[(170, 87)], fail_action="FO")
instrument(sheet, "FIC-507", at=(300, 172), sensing="Line_ME118_S1", sensing_at=(300, PRODUCT),
           signal_to=fv507, signal_points=[(330, 172)], fail_action="FC")
instrument(sheet, "LIC-508", at=(165, 178), sensing=c202["N8"], signal_to=lv508,
           fail_action="FC")
instrument(sheet, "AI-509", at=(362, 172), sensing="Line_ME118_S1", sensing_at=(362, PRODUCT))
instrument(sheet, "PI-510", at=(140, 55), sensing="Line_PG530_S1", sensing_at=(120, 55))
instrument(sheet, "LZ-511", at=(305, 87), sensing=v202["N5"])
instrument(sheet, "TI-512", at=(226, 57), sensing="Line_ME531_S1", sensing_at=(244, 57))
fail_label(sheet, "Inst_TIC502", (35, 145), "up")
fail_label(sheet, "Inst_PIC504", (330, 35), "down")
fail_label(sheet, "Inst_LIC505", (170, REFLUX), "up-left")
fail_label(sheet, "Inst_FIC507", (330, PRODUCT), "up")
fail_label(sheet, "Inst_LIC508", (165, BOT), "up")

notes(sheet,
      "TIC-502: column temperature on the LP steam TV-502. LIC-505: reflux on the V-202 level; "
      "FIC-507: product on flow, the smaller branch (D-020). AI-509: water in the Grade AA product",
      "PIC-504: column pressure on the vent PV-504. LIC-508: sump level on the bottoms LV-508. "
      "LZ-511: V-202 level low-low stops P-203A/B (C&E I-501). Fusel-oil draw not modelled (D-008)",
      "PSV-513: C-202 and V-202 (fire, cooling water failure). E-203 also subcools the product "
      "(D-008). Overhead, reflux and reboiler DN ASSUMED (D-016)")

save(sheet, target)
