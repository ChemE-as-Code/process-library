"""Draft of P-02: ammonia-air mixing M-101 with the NH3/air ratio control and the burner trips,
ammonia burner R-101 (Pt/Rh gauze) and waste-heat boiler E-102 with its steam-side interfaces.

Provenance only: P-02 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-02.py build/frames/P-02.xml pid/P-02.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-020; streams S03, S08, S10-S12 and
the energy stream Q05 of process/flowsheet.yaml.
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
from pid_common import (  # noqa: E402
    BOTTOM,
    DRUM,
    EDGE,
    HX,
    LEFT,
    TOP,
    TRAIN,
    equipment,
    line,
    make_safety_valve,
    save,
    valve_marks,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

NH3 = 60        # ammonia vapour line
AIR = 150       # primary air line and mixer axis
GAS = 205       # burner gas through the waste-heat boiler
STEAM_X = 290.2

# ---- equipment
m101 = equipment(sheet, "StaticMixer", "M-101", shape="STATIC_MIXER_SHAPE", at=(165, AIR),
                 scale=1.5,
                 nozzles=[Nozzle("N1", (-11.25, 0), 1000), Nozzle("N2", (0, -11.25), 250),
                          Nozzle("N3", (11.25, 0), 1000)],
                 label_at=(165, 170))
r101 = equipment(sheet, "Vessel", "R-101", shape=DRUM, at=(250, 150), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (0, -24), 1000), Nozzle("N2", (0, 24), 1400),
                          Nozzle("N3", (12, -15), 50), Nozzle("N4", (-12, 5), 50)],
                 label_at=(268, 178))
e102 = equipment(sheet, "TubularHeatExchanger", "E-102", shape=HX, at=(300, GAS), scale=1.4,
                 nozzles=[Nozzle("T1", (-24.5, 0), 1400), Nozzle("T2", (24.5, 0), 1400),
                          Nozzle("S1", (-9.8, -9.8), 200), Nozzle("S2", (9.8, 9.8), 100)],
                 label_at=(300, 228))

# ---- ammonia vapour: trip valves, ratio-controlled flow valve, check valve, into the mixer
xv203 = valve("XV203", "BallValve", tag="XV-203", at=(55, NH3))
fv201 = valve("FV201", "GlobeValve", tag="FV-201", at=(140, NH3))
xv204 = valve("XV204", "BallValve", tag="XV-204", at=(165, 90))
line(sheet, "NV-102", dn=250, fluid="Ammonia", route=[
    offpage("in", at=(LEFT, NH3), note="NH3 vapour from E-101, P-01"),
    xv203, fv201, (165, NH3), xv204, valve("CV202", "SwingCheckValve", at=(165, 118)),
    m101["N2"]], label_at=(95, 52))

# ---- primary air into the mixer, mixture to the burner
line(sheet, "PA-105", dn=1100, fluid="Air", route=[
    offpage("in", at=(LEFT, AIR), note="primary air from K-101, P-01"), m101["N1"]],
    label_at=(85, 158))
line(sheet, "AM-201", dn=1000, fluid="Ammonia-air mixture", route=[
    m101["N3"], (205, AIR), (205, 110), (250, 110), r101["N1"]], label_at=(190, 102))

# ---- burner gas through the waste-heat boiler to the tail-gas heater
line(sheet, "NX-202", dn=1400, fluid="Nitrous gas", route=[
    r101["N2"], (250, GAS), e102["T1"]], label_at=(236, 214))
line(sheet, "NX-203", dn=1400, fluid="Nitrous gas", route=[
    e102["T2"], offpage("out", at=(EDGE, GAS), note="nitrous gas to E-103, P-03")],
    label_at=(365, 197))

# ---- steam side: HP steam to the export header with its relief, BFW from the economiser
psv_tee = tee("T204", at=(STEAM_X, 60), branch="right", branch_dn=150)
line(sheet, "HS-204", dn=200, fluid="HP steam", route=[
    e102["S1"], psv_tee,
    offpage("out", at=(STEAM_X, TOP), note="HP steam to export header (B/L)", rotation=270,
            note_at=(262, 12))], label_at=(305, 105))
psv215 = valve("PSV215", "GlobeValve", tag="PSV-215", at=(315, 60))
line(sheet, "HS-206", dn=150, fluid="HP steam", route=[
    psv_tee.branch, psv215, (335, 60),
    offpage("out", at=(335, TOP), note="to atmosphere (silencer)", rotation=270,
            note_at=(360, 12))], label_at=(318, 68))
line(sheet, "BW-313", dn=100, fluid="Boiler feed water", route=[
    offpage("in", at=(309.8, BOTTOM), note="BFW from E-104, P-03", rotation=270,
            note_at=(335, 252)),
    e102["S2"]], label_at=(322, 238))
make_safety_valve(sheet, "PSV215", label_at=(315, 52))

# ---- instruments: ratio control, burner trips, burner and boiler indications
instrument(sheet, "FFIC-201", at=(115, 80), sensing="Line_NV102_S1", sensing_at=(115, NH3),
           signal_to=fv201, fail_action="FC")
instrument(sheet, "FI-202", at=(115, 125), sensing="Line_PA105_S1", sensing_at=(115, AIR),
           signal_to="Inst_FFIC201")
instrument(sheet, "US-209", at=(55, 80), signal_to=xv203, fail_action="FC")
instrument(sheet, "FFZ-205", at=(85, 80), sensing="Line_NV102_S1", sensing_at=(85, NH3),
           signal_to="Inst_US209")
instrument(sheet, "FZ-206", at=(55, 125), sensing="Line_PA105_S1", sensing_at=(55, AIR),
           signal_to="Inst_US209")
instrument(sheet, "TZ-207", at=(190, 90), sensing=r101["N3"],
           sensing_points=[(275, 135), (275, 90)], signal_to=xv204, fail_action="FC")
instrument(sheet, "TI-208", at=(222, 155), sensing=r101["N4"])
instrument(sheet, "AI-210", at=(190, 170), sensing="Line_AM201_S1", sensing_at=(190, AIR))
instrument(sheet, "PI-211", at=(228, 128), sensing="Line_AM201_S1", sensing_at=(228, 110),
           location="field")
instrument(sheet, "TI-212", at=(350, 222), sensing="Line_NX203_S1", sensing_at=(350, GAS))
instrument(sheet, "PI-213", at=(312, 130), sensing="Line_HS204_S1", sensing_at=(STEAM_X, 130),
           location="field")
instrument(sheet, "TI-214", at=(312, 150), sensing="Line_HS204_S1", sensing_at=(STEAM_X, 150))

valve_marks(sheet, "Inst_US209", "XV203", (55, NH3), "down")
valve_marks(sheet, "Inst_FFIC201", "FV201", (140, NH3), "down")
valve_marks(sheet, "Inst_TZ207", "XV204", (165, 90), "right")

note(sheet, "Burner trips (C&E I-201 to I-204): US-209 closes XV-203, TZ-207 closes XV-204; both "
     "close on every burner and train trip. FZ-206 also to US-612 (P-06, C&E I-401)",
     at=(20, 262))
note(sheet, "R-101 and E-102 in one vessel (vendor); ignition burner and start-up purge: "
     "SEQ-START-BURNER. E-102 steam drum, circulation and BFW level control: boiler package (D-020)",
     at=(20, 269))
note(sheet, "Relief: everything on this sheet downstream of CV105 (P-01), incl. M-101, R-101 and the "
     "E-102 tube rupture, by PSV-316 (P-03); PSV-111 only up to CV105 (D-022)", at=(20, 276))

save(sheet, target)
