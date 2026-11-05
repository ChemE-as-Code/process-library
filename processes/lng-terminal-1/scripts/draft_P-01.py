"""Draft of P-01: LNG rundown from trains 1-4 and the top / bottom fill of both tanks; the tank
vapour header with the vapour return lines, the make-up gas and the branch to the flare.

Provenance only: P-01 is hand-maintained after this first revision (no `generator:` in
plant.yaml). Run: cheme run scripts/draft_P-01.py pid/P-01.xml (on the empty A3 frame).
Streams S1, S6, S8 of process/flowsheet.yaml; decisions D-005, D-007, D-009, D-017, D-021.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import Lists, Sheet, note, offpage, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-01")
UP, DOWN = 270, 90
ROWS = {1: 35, 2: 60, 3: 85, 4: 110}

# ---- rundown header LNG-1001: train 1 tie-in, trains 2-4 join, branches to the tanks ----------
tt = {k: tee(f"T101{k}", at=(95, ROWS[k]), branch="left", branch_dn=500) for k in (2, 3, 4)}
trv = tee("T1021", at=(95, 122), branch="right", branch_dn=25)
tk1 = tee("T1002", at=(150, 150), branch="down", branch_dn=900)
tk2b = tee("T1003", at=(205, 150), branch="down", branch_dn=900)
hdr = L.line(sheet, "LNG-1001", dn=900, fluid="LNG", frm="BL (train 1)", to="T-3101 (top fill)",
             notes="Rundown header from the four trains, 3,365 t/h (~7,560 m3/h), 3.4 m/s at DN 900 (S1, D-005); train 1 ties in at the battery limit (D-021); ends as the T-3101 top fill.",
             route=[offpage("in", at=(14, 35), note="from train 1 rundown (BL)", note_at=(27, 41)),
                    valve("XV1111", "BallValve", tag="XV-1111", at=(40, 35)),
                    valve("CV1111", "SwingCheckValve", at=(58, 35)), (95, 35), tt[2], tt[3], tt[4],
                    trv, (95, 150), tk1, valve("XV1103", "BallValve", tag="XV-1103", at=(180, 150)),
                    tk2b, (230, 150), valve("XV1108", "BallValve", tag="XV-1108", at=(230, 198)),
                    offpage("out", at=(230, 226), note="to T-3101 top fill (P-03)",
                            note_at=(222, 234), rotation=DOWN)],
             label_at=(120, 158))
for k in (2, 3, 4):
    y = ROWS[k]
    L.line(sheet, f"LNG-101{k}", dn=500, fluid="LNG", frm=f"BL (train {k})", to="LNG-1001",
           notes=f"Train {k} rundown, ~841 t/h (~1,890 m3/h), 2.7 m/s at DN 500 (D-003).",
           route=[offpage("in", at=(14, y), note=f"from train {k} rundown (BL)", note_at=(27, y + 6)),
                  valve(f"XV111{k}", "BallValve", tag=f"XV-111{k}", at=(40, y)),
                  valve(f"CV111{k}", "SwingCheckValve", at=(58, y)), tt[k].branch],
           label_at=(80, y + 6))
psv1121 = L.relief("PSV1121", "PSV-1121", "BOG-1004", 15.5,
                   "thermal expansion of the blocked-in rundown header",
                   "Thermal relief of LNG-1001 between XV-1111..1114 and XV-1102/1103, to the BOG header (D-017).")
L.line(sheet, "BOG-1004", dn=25, fluid="Boil-off gas", frm="LNG-1001 (PSV-1121)", to="BOG-1001",
       notes="Thermal relief outlet to the tank vapour header.",
       route=[trv.branch, psv1121, offpage("out", at=(130, 122), note="to BOG header",
                                          note_at=(128, 115))],
       label_at=(112, 129))

# T-2101 fill: ESD valve, then top or bottom fill
tsplit = tee("T1004", at=(150, 182), branch="right", branch_dn=900)
L.line(sheet, "LNG-1002", dn=900, fluid="LNG", frm="LNG-1001", to="T-2101 (top fill)",
       notes="Fill to T-2101; top fill (rundown heavier than the tank's top layer) or bottom fill via LNG-1004, chosen from AI-1102 against LTD-2103 (rollover, D-007).",
       route=[tk1.branch, valve("XV1102", "BallValve", tag="XV-1102", at=(150, 166)), tsplit,
              valve("XV1106", "BallValve", tag="XV-1106", at=(150, 200)),
              offpage("out", at=(150, 226), note="to T-2101 top fill (P-02)", note_at=(120, 234),
                      rotation=DOWN)],
       label_at=(132, 186))
L.line(sheet, "LNG-1004", dn=900, fluid="LNG", frm="LNG-1002", to="T-2101 (bottom fill)",
       notes="T-2101 bottom fill (D-007).",
       route=[tsplit.branch, (172, 182), valve("XV1107", "BallValve", tag="XV-1107", at=(172, 200)),
              offpage("out", at=(172, 226), note="to T-2101 bottom fill (P-02)", note_at=(160, 242),
                      rotation=DOWN)],
       label_at=(181, 174))
L.line(sheet, "LNG-1003", dn=900, fluid="LNG", frm="LNG-1001", to="T-3101 (bottom fill)",
       notes="T-3101 bottom fill (D-007); the top fill is the end of LNG-1001.",
       route=[tk2b.branch, valve("XV1109", "BallValve", tag="XV-1109", at=(205, 200)),
              offpage("out", at=(205, 226), note="to T-3101 bottom fill (P-03)", note_at=(196, 242),
                      rotation=DOWN)],
       label_at=(214, 174))

# instruments of the rundown
for k, y in ROWS.items():
    seg = hdr.segments[0] if k == 1 else f"Line_LNG101{k}_S1"
    L.inst(sheet, f"FI-111{k}", f"Train {k} rundown flow", "Ultrasonic; tank inventory balance.",
           at=(76, y - 9), sensing=seg, sensing_at=(76, y))
    L.inst(sheet, f"UZ-111{k}", f"Train {k} rundown battery-limit ESD valve XV-111{k}",
           "ESD-1 of the terminal closes the rundown; the train turns down (C&E I-101).",
           at=(40, y - 10), signal_to=f"XV111{k}", fail_action="FC")
for tag, service, x in [("AI-1102", "LNG rundown density / composition", 108),
                        ("TI-1103", "LNG rundown temperature", 123),
                        ("PI-1104", "LNG rundown header pressure", 138)]:
    L.inst(sheet, tag, service,
           "Chooses top or bottom fill against the tank's density profile (rollover, D-007)."
           if tag == "AI-1102" else "", at=(x, 141), sensing=hdr.segments[4], sensing_at=(x, 150))
L.inst(sheet, "UZ-1102", "T-2101 fill ESD valve XV-1102",
       "Closes on T-2101 high-high level or pressure (C&E I-201, I-203).",
       at=(135, 166), signal_to="XV1102", fail_action="FC")
L.inst(sheet, "UZ-1103", "T-3101 fill ESD valve XV-1103",
       "Closes on T-3101 high-high level or pressure (C&E I-301, I-303).",
       at=(180, 140), signal_to="XV1103", fail_action="FC")
for tag, vid, x, y in [("HS-1106", "XV1106", 135, 200), ("HS-1107", "XV1107", 187, 200),
                       ("HS-1109", "XV1109", 219, 210), ("HS-1108", "XV1108", 245, 198)]:
    L.inst(sheet, tag, f"Fill selection valve XV-{vid[2:]}",
           "Operator selection (DCS), top or bottom fill.", at=(x, y), signal_to=vid,
           fail_action="FL")

# ---- tank vapour header BOG-1001 to the BOG compressors --------------------------------------
b3 = tee("T1103", at=(285, 40), branch="down", branch_dn=600)
b6 = tee("T1106", at=(305, 40), branch="up", branch_dn=750)
b7 = tee("T1107", at=(320, 40), branch="up", branch_dn=750)
bm = tee("T1109", at=(345, 40), branch="down", branch_dn=150)
bf = tee("T1108", at=(380, 40), branch="down", branch_dn=900)
bog = L.line(sheet, "BOG-1001", dn=750, fluid="Boil-off gas", frm="T-2101", to="D-7101",
             notes="Tank vapour header from T-2101 (P-02) with T-3101, the vapour return lines and the make-up (P-01) to the BOG suction drum with the desuperheater spray (P-07); holding 21.9 t/h (S8), loading 49.1 t/h with the return (S6) (D-009). Drawn on P-02, P-01 and P-07.",
             route=[offpage("in", at=(250, 40), note="from T-2101 (P-02)", note_at=(258, 32)),
                    b3, b6, b7, bm, bf,
                    offpage("out", at=(405, 40), note="to D-7101 (P-07)", note_at=(390, 33))],
             label_at=(332, 52))
L.line(sheet, "BOG-1003", dn=600, fluid="Boil-off gas", frm="T-3101", to="BOG-1001",
       notes="T-3101 vapour outlet to the tank vapour header. Drawn on P-03 and P-01.",
       route=[offpage("in", at=(285, 92), note="from T-3101 (P-03)", note_at=(262, 100),
                      rotation=UP), b3.branch],
       label_at=(275, 68))
for k, tb, x, side, nx in [("6", b6, 305, "A", 282), ("7", b7, 320, "B", 344)]:
    L.line(sheet, f"BOG-400{int(k) - 5}", dn=750, fluid="Boil-off gas", frm=f"BOG-{'5' if side == 'A' else '6'}001 (Berth {'2' if side == 'A' else '1'})",
           to="BOG-1001", insulation="cold (PIR 150 mm)",
           notes=f"Vapour return line {side} over the trestle (Berth {'2' if side == 'A' else '1'}) into the tank vapour header; 45.6 t/h at loading (S6), ~9 m/s (D-009, D-012). Drawn on P-04 and P-01.",
           route=[offpage("in", at=(x, 14), note=f"from vapour return {side} (P-04)",
                          note_at=(nx, 9), rotation=DOWN), tb.branch],
           label_at=(x - 10 if side == "A" else x + 10, 25))
pv1111 = valve("PV1111", "GlobeValve", tag="PV-1111", at=(345, 66))
L.line(sheet, "BOG-1009", dn=150, fluid="Boil-off gas", frm="BOG-7002", to="BOG-1001",
       notes="Make-up gas from the compressor discharge against tank vacuum, PV-1111 (D-017). Drawn on P-07 and P-01.",
       route=[offpage("in", at=(345, 92), note="from BOG compressors (P-07)", note_at=(332, 100),
                      rotation=UP), pv1111, bm.branch],
       label_at=(335, 80))
pv1110 = valve("PV1110", "GlobeValve", tag="PV-1110", at=(380, 66))
L.line(sheet, "FL-8001", dn=900, fluid="Flare gas", frm="BOG-1001 (PV-1110)", to="D-8101", insulation="none",
       notes="Storage and loading flare header from the tank pressure control valve PV-1110 (ahead of the tank PSVs) to the knock-out drum, with the BOG relief valves, the purge and carrier de-inerting joining on P-08; design case the BOG compressor trip at loading, ~54 t/h (D-017). Drawn on P-01 and P-08.",
       route=[bf.branch, pv1110,
              offpage("out", at=(380, 92), note="to D-8101 (P-08)", note_at=(378, 100),
                      rotation=DOWN)],
       label_at=(370, 80))
L.inst(sheet, "TI-1112", "BOG header temperature", at=(268, 54), sensing=bog.segments[0],
       sensing_at=(268, 40))
L.inst(sheet, "PIC-1111", "Tank vapour header pressure, low split: make-up gas PV-1111",
       "Holds the tanks above their vacuum set point (D-017).",
       at=(360, 56), sensing=bog.segments[4], sensing_at=(360, 40), signal_to=pv1111,
       fail_action="FC")
L.inst(sheet, "PIC-1110", "Tank vapour header pressure, high split: BOG compressors then PV-1110 to the flare",
       "Output 1 sets the BOG compressor load (PIC-7101, P-07); output 2 opens PV-1110 (D-017).",
       at=(396, 56), sensing=bog.segments[5], sensing_at=(396, 40), signal_to=pv1110,
       fail_action="FC")

note(sheet, "Rundown subcooled -161.5 degC, 215 kPa(a) at the tanks (D-005). Top or bottom fill", at=(12, 252))
note(sheet, "from AI-1102 against the tank's density profile LTD-2103 / LTD-3103 (rollover, D-007).", at=(12, 258))
note(sheet, "UZ-111x: see C&E I-101. UZ-1102: C&E I-201, I-203. UZ-1103: C&E I-301, I-303.", at=(12, 264))
note(sheet, "PIC-1110 / PIC-1111: split-range tank pressure control (D-017).", at=(250, 120))

L.finish(sheet, target)
