"""Draft of P-03: purge hydrogen PSA package PK-101, tail-gas compressor K-102 with its
spillback, and the tail-gas aftercooler E-103.

Provenance only: P-03 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-03.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-024, D-025; streams S13, S29-S34 of process/flowsheet.yaml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)
from pid_common import EDGE, HX, LEFT, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

# ---- equipment
pk101 = equipment(sheet, "Vessel", "PK-101", shape="COLUMN_FIXED_BED_SHAPE", at=(110, 120),
                  scale=(1.2, 1.6),
                  nozzles=[Nozzle("N1", (-18, 20), 80), Nozzle("N2", (0, -40), 40),
                           Nozzle("N3", (18, 30), 250)],
                  label_at=(110, 172))
k102 = equipment(sheet, "CentrifugalCompressor", "K-102", shape="COMPRESSOR_SHAPE",
                 at=(250, 150), scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 250), Nozzle("N2", (15, 0), 200)],
                 label_at=(250, 172))
e103 = equipment(sheet, "TubularHeatExchanger", "E-103", shape=HX, at=(335, 150), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 200), Nozzle("T2", (21, 0), 150),
                          Nozzle("S1", (-7, -8.4), 80), Nozzle("S2", (7, -8.4), 80)],
                 label_at=(335, 168))

# ---- purge gas from FV-211 (P-02) into the package
line(sheet, "HG-113", dn=80, fluid="Purge gas", route=[
    offpage("in", at=(LEFT, 140), note="from FV-211, P-02", note_at=(26, 146)),
    valve("HV330", "GateValve", at=(60, 140)), pk101["N1"]], label_at=(40, 133))

# ---- PSA hydrogen back to the K-101 suction (P-02) on the PSA pressure control PV-301
pv301 = valve("PV301", "GlobeValve", tag="PV-301", at=(80, 30))
line(sheet, "HG-125", dn=40, fluid="Hydrogen", route=[
    pk101["N2"], (110, 30), pv301, valve("HV331", "GateValve", at=(55, 30)),
    offpage("out", at=(LEFT, 30), note="to K-101 suction, P-02", rotation=180,
            note_at=(28, 24))],
    label_at=(128, 52))

# ---- tail gas to K-102: tail-gas side relief, spillback return
psv_in = tee("T332", at=(170, 150), branch="up", branch_dn=150)
spill_in = tee("T330A", at=(205, 150), branch="down", branch_dn=150)
line(sheet, "FG-126", dn=250, fluid="Fuel gas", route=[
    pk101["N3"], (150, 150), valve("HV332", "GateValve", at=(152, 150)), psv_in, spill_in,
    k102["N1"]], label_at=(150, 160))
psv307 = valve("PSV307", "GlobeValve", tag="PSV-307", at=(170, 110))
line(sheet, "FL-332", dn=150, fluid="Relief gas", route=[
    psv_in.branch, psv307,
    offpage("out", at=(170, TOP), note="to flare header, P-07", rotation=270, note_at=(153, 12))],
    label_at=(180, 90))

# ---- K-102 discharge: relief, check valve, aftercooler
psv_out = tee("T331", at=(285, 150), branch="up", branch_dn=100)
line(sheet, "FG-127", dn=200, fluid="Fuel gas", route=[
    k102["N2"], psv_out, valve("CV127", "SwingCheckValve", at=(300, 150)), e103["T1"]],
    label_at=(300, 140))
psv308 = valve("PSV308", "GlobeValve", tag="PSV-308", at=(285, 110))
line(sheet, "FL-331", dn=100, fluid="Relief gas", route=[
    psv_out.branch, psv308,
    offpage("out", at=(285, TOP), note="to flare header, P-07", rotation=270, note_at=(268, 12))],
    label_at=(295, 90))

# ---- cooled tail gas to the site fuel gas header; spillback to the K-102 suction
spill_out = tee("T330B", at=(372, 150), branch="down", branch_dn=150)
line(sheet, "FG-128", dn=150, fluid="Fuel gas", route=[
    e103["T2"], spill_out,
    offpage("out", at=(EDGE, 150), note="to fuel gas header (B/L)", note_at=(396, 158))],
    label_at=(390, 140))
pv303 = valve("PV303", "GlobeValve", tag="PV-303", at=(290, 205))
line(sheet, "FG-330", dn=150, fluid="Fuel gas", route=[
    spill_out.branch, (372, 205), pv303, (205, 205), spill_in.branch], label_at=(330, 212))

# ---- cooling water to E-103 (P-08)
cw_relief = tee("T335", at=(342, 60), branch="right", branch_dn=25)
line(sheet, "CWS-333", dn=80, fluid="Cooling water", route=[
    offpage("in", at=(328, TOP), note="from CW supply, P-08", rotation=90, note_at=(310, 9)),
    e103["S1"]], label_at=(318, 100))
line(sheet, "CWR-334", dn=80, fluid="Cooling water", route=[
    e103["S2"], cw_relief,
    offpage("out", at=(342, TOP), note="to CW return, P-08", rotation=270, note_at=(360, 9))],
    label_at=(352, 100))
psv309 = valve("PSV309", "GlobeValve", tag="PSV-309", at=(370, 45))
line(sheet, "CWR-335", dn=25, fluid="Cooling water", route=[
    cw_relief.branch, (370, 60), psv309,
    offpage("out", at=(370, 22), note="to atmosphere (safe location)", rotation=270,
            note_at=(392, 18))],
    label_at=(382, 52))

# ---- relief valves: placeholders made safety valves (pid_common.make_safety_valve)
make_safety_valve(sheet, "PSV307", label_at=(158, 115))
make_safety_valve(sheet, "PSV308", label_at=(273, 115))
make_safety_valve(sheet, "PSV309", label_at=(386, 40))

# ---- instruments
instrument(sheet, "PIC-301", at=(80, 55), sensing="Line_HG125_S1", sensing_at=(110, 55),
           signal_to=pv301)
instrument(sheet, "AI-302", at=(35, 50), sensing="Line_HG125_S1", sensing_at=(35, 30))
instrument(sheet, "PIC-303", at=(220, 180), sensing="Line_FG126_S3", sensing_at=(220, 150),
           signal_to=pv303, signal_points=[(290, 180)])
instrument(sheet, "TI-304", at=(272, 130), sensing="Line_FG127_S1", sensing_at=(272, 150))
instrument(sheet, "TI-305", at=(360, 130), sensing="Line_FG128_S1", sensing_at=(360, 150))
instrument(sheet, "FI-306", at=(381, 180), sensing="Line_FG128_S2", sensing_at=(381, 150))

note(sheet, "PK-101: adsorber beds, switching valves, tail gas surge drum, cycle control and their relief "
     "in the vendor package (D-024); PV-301 holds the adsorption pressure", at=(20, 262))
note(sheet, "PIC-303: tail gas pressure at the K-102 suction (PSA desorption pressure) on the spillback "
     "PV-303; K-102 machine protection in its package", at=(20, 269))
note(sheet, "PSV-307: PSA switching valve failed open (feed gas into the tail gas side); PSV-308: "
     "K-102 discharge blocked; PSV-309: E-103 CW side blocked in (D-025)", at=(20, 276))

save(sheet, target)
