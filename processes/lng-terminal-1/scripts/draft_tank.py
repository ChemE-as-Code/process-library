"""Draft of a tank sheet (P-02: T-2101, P-03: T-3101): the full-containment LNG tank with its
four in-tank loading pumps and the circulation pump, their discharge header, minimum-flow
returns, the fill and circulation-return lines, the vapour outlet, the PSVs and vacuum relief
valves and the tank instrumentation.

Provenance only: the sheets are hand-maintained after this first revision. Run:
cheme run scripts/draft_tank.py pid/P-02.xml 2   (or pid/P-03.xml 3), on the empty A3 frame.
Decisions D-007, D-008, D-011, D-017, D-021. All nozzles of a full-containment tank pass
through the roof; the sheet draws the bottom fill, the circulation return, the relief valves
and the instrument connections on the shell for clarity (D-021).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import (  # noqa: E402
    Lists, Nozzle, Sheet, equipment, note, offpage, set_dn, tank_shape, tee, valve)

target, n = Path(sys.argv[1]), sys.argv[2]
phase = "Phase 1, as built" if n == "2" else "Phase 2"
side = "A" if n == "2" else "B"
sheet = Sheet.load(target)
L = Lists(f"P-0{n}")
TK = f"T-{n}101"
UP = 270
CX, CY, SC = 120, 170, 2.4
HEADER_Y, CIRC_Y, MF_Y, CV_Y = 50, 35, 88, 68
DOME = [(-30, -14), (-26, -19), (-18, -23.5), (-8, -25.6), (0, -26), (8, -25.6), (18, -23.5),
        (26, -19), (30, -14)]


def roof(dx):
    """Offset of the roof below the tank centre at dx (sheet mm), on the drawn dome."""
    u = dx / SC
    for (x0, y0), (x1, y1) in zip(DOME, DOME[1:]):
        if x0 <= u <= x1:
            return SC * (y0 + (y1 - y0) * (u - x0) / (x1 - x0))
    raise ValueError(dx)


# pump columns (x on the sheet): the circulation pump left, loading pumps A-D
CIRC_X = 66
COLS = {"A": 90, "B": 114, "C": 138, "D": 162}
PUMP_Y = 218
mf_x = {k: x + 16 for k, x in COLS.items()} | {"R": CIRC_X + 16}

# ---- the tank and its pumps ------------------------------------------------------------------
noz = [Nozzle("N1", (-65, roof(-65)), 900), Nozzle("N2", (-72, 44), 900),
       Nozzle("N3", (66, roof(66)), 750 if n == "2" else 600), Nozzle("N4", (72, -20), 250), Nozzle("N5", (72, -5), 250),
       Nozzle("N6", (72, 10), 250), Nozzle("N7", (72, 25), 250), Nozzle("N8", (72, 55), 250)]
noz += [Nozzle(f"M{k}", (x - CX, roof(x - CX)), 150 if k != "R" else 100) for k, x in mf_x.items()]
inst_y = [140, 150, 160, 170, 180, 190, 200]
noz += [Nozzle(f"I{i + 1}", (-72, y - CY), 50) for i, y in enumerate(inst_y)]
tank = equipment(sheet, "Tank", TK, shape=tank_shape(sheet), at=(CX, CY), scale=SC, nozzles=noz,
                 label_at=(126, 152))
pumps = {}
for k, x in COLS.items():
    pumps[k] = equipment(sheet, "CentrifugalPump", f"P-{n}101{k}", shape="CENTRIFUGAL_PUMP_SHAPE",
                         at=(x, PUMP_Y), nozzles=[Nozzle("N1", (-7.5, 0), 450), Nozzle("N2", (0, -7.5), 450)],
                         label_at=(x, PUMP_Y + 12))
pumps["R"] = equipment(sheet, "CentrifugalPump", f"P-{n}102", shape="CENTRIFUGAL_PUMP_SHAPE",
                       at=(CIRC_X, PUMP_Y), nozzles=[Nozzle("N1", (-7.5, 0), 250), Nozzle("N2", (0, -7.5), 250)],
                       label_at=(CIRC_X, PUMP_Y + 12))

# ---- discharge header and pump columns --------------------------------------------------------
heads = {k: tee(f"T{n}1H{k}", at=(COLS[k], HEADER_Y), branch="down", branch_dn=450) for k in "BCD"}
mfs = {k: tee(f"T{n}1M{k}", at=(COLS.get(k, CIRC_X), MF_Y), branch="right",
              branch_dn=150 if k != "R" else 100) for k in "ABCDR"}
line_a = L.line(sheet, f"LNG-{n}001", dn=800, fluid="LNG", frm=f"P-{n}101A", to=f"LNG-400{int(n) - 1}",
                notes=f"{TK} loading pump discharge header to loading line {side}, up to 12,000 m3/h (D-011); segment S1 is the DN 450 column of P-{n}101A, where the header starts (D-021).",
                segments=[{"number": "S1", "nominal_diameter": "DN450", "notes": f"P-{n}101A pump column"}],
                route=[pumps["A"]["N2"], mfs["A"], valve(f"CV{n}121A", "SwingCheckValve", at=(COLS["A"], CV_Y)),
                       (COLS["A"], HEADER_Y), heads["B"], heads["C"], heads["D"],
                       offpage("out", at=(285, HEADER_Y), note=f"to LNG-400{int(n) - 1} (P-04)",
                               note_at=(272, HEADER_Y + 6))],
                label_at=(225, HEADER_Y - 8))
# the column of P-n101A (segment S1) is DN 450 like the others
set_dn(sheet, [f"T{n}1MA_N1", f"T{n}1MA_N2", f"CV{n}121A_N1", f"CV{n}121A_N2", f"T{n}1HB_N1"], 450,
       segments=[f"Line_LNG{n}001_S1"])
for k in "BCD":
    L.line(sheet, f"LNG-{n}01{ord(k) - 64}", dn=450, fluid="LNG", frm=f"P-{n}101{k}", to=f"LNG-{n}001",
           notes=f"P-{n}101{k} pump column (3,000 m3/h, D-011).",
           route=[pumps[k]["N2"], mfs[k], valve(f"CV{n}121{k}", "SwingCheckValve", at=(COLS[k], CV_Y)),
                  heads[k].branch],
           label_at=(COLS[k] - 9, 165))
L.line(sheet, f"LNG-{n}002", dn=250, fluid="LNG", frm=f"P-{n}102", to="LNG-4001" if n == "2" else "LNG-2002",
       notes=(f"{TK} circulation pump discharge and circulation header into loading line A, with the desuperheater spray take-off; holding ~314 m3/h (D-008, D-010). Drawn on P-02 and P-04."
              if n == "2" else f"{TK} circulation pump discharge into the circulation header LNG-2002. Drawn on P-03 and P-04."),
       route=[pumps["R"]["N2"], mfs["R"], valve(f"CV{n}122", "SwingCheckValve", at=(CIRC_X, CV_Y)),
              (CIRC_X, CIRC_Y), offpage("out", at=(285, CIRC_Y), note="to circulation and spray (P-04)",
                                         note_at=(262, CIRC_Y - 6))],
       label_at=(200, CIRC_Y - 8))
for k in "ABCDR":
    x = COLS.get(k, CIRC_X)
    tag = f"FV-{n}111{k}" if k != "R" else f"FV-{n}112"
    vid = tag.replace("-", "")
    pump_tag = f"P-{n}101{k}" if k != "R" else f"P-{n}102"
    L.line(sheet, f"LNG-{n}02{'12345'['ABCDR'.index(k)]}", dn=150 if k != "R" else 100, fluid="LNG",
           frm=pump_tag, to=TK, labels=False,
           notes=f"{pump_tag} minimum-flow return into {TK} (ASSUMED ~30 % of rated flow, D-011); number and size in the sheet note (no room for labels between the columns).",
           route=[mfs[k].branch, valve(vid, "GlobeValve", tag=tag, at=(x + 8, MF_Y)), (mf_x[k], MF_Y),
                  tank[f"M{k}"]])
    seg = (f"Line_LNG{n}001_S1" if k == "A" else
           (f"Line_LNG{n}002_S1" if k == "R" else f"Line_LNG{n}01{ord(k) - 64}_S1"))
    L.inst(sheet, tag.replace("FV", "FIC"), f"{pump_tag} minimum flow",
           "Opens the minimum-flow return below the pump's minimum continuous flow (D-011).",
           at=(x + 8, MF_Y - 13), sensing=seg, sensing_at=(x, MF_Y - 13), signal_to=vid,
           fail_action="FO")
L.inst(sheet, f"PI-{n}117", f"{TK} loading header pressure", at=(250, HEADER_Y + 12),
       sensing=line_a.segments[-1], sensing_at=(250, HEADER_Y))

# ---- fill, circulation return, vapour -------------------------------------------------------
L.line(sheet, "LNG-1002" if n == "2" else "LNG-1001", dn=900, fluid="LNG",
       frm="LNG-1001" if n == "2" else "BL (train 1)", to=TK,
       notes=(f"Fill to {TK}; top fill (spray ring under the deck) or bottom fill via LNG-1004, chosen from AI-1102 against LTD-2103 (rollover, D-007). Drawn on P-01 and P-02."
              if n == "2" else "rundown header (see P-01); its end is the T-3101 top fill."),
       route=[offpage("in", at=(14, 112), note="top fill from P-01", note_at=(22, 106)),
              (CX - 65, 112), tank["N1"]], label_at=(32, 120))
L.line(sheet, "LNG-1004" if n == "2" else "LNG-1003", dn=900, fluid="LNG",
       frm="LNG-1002" if n == "2" else "LNG-1001", to=TK,
       notes=f"{TK} bottom fill (internal down-comer to the tank bottom) (D-007). Drawn on P-01 and P-0{n}.",
       route=[offpage("in", at=(14, 214), note="bottom fill from P-01", note_at=(24, 208)), tank["N2"]],
       label_at=(30, 222))
xvr = valve(f"XV{n}123", "BallValve", tag=f"XV-{n}123", at=(232, 225))
L.line(sheet, "LNG-4005" if n == "2" else "LNG-4009", dn=250, fluid="LNG",
       frm="LNG-4002" if n == "2" else "LNG-4005", to=TK,
       notes=(f"Circulation return from line B to the tanks (holding, S10); to T-2101 or, via LNG-4009, T-3101 (D-008). Drawn on P-04 and P-02."
              if n == "2" else "Circulation return branch to T-3101. Drawn on P-04 and P-03."),
       route=[offpage("in", at=(285, 225), note="circulation return from P-04", note_at=(266, 233),
                      rotation=180), xvr, tank["N8"]],
       label_at=(210, 233))
L.inst(sheet, f"HS-{n}123", f"{TK} circulation return valve XV-{n}123",
       "Opened for the tank that receives the circulation (D-008).",
       at=(232, 211), signal_to=xvr.id, fail_action="FL")
L.line(sheet, "BOG-1001" if n == "2" else "BOG-1003", dn=750 if n == "2" else 600,
       fluid="Boil-off gas", frm=TK, to="D-7101" if n == "2" else "BOG-1001",
       notes=("see P-01" if n == "2" else "T-3101 vapour outlet to the tank vapour header. Drawn on P-03 and P-01."),
       route=[tank["N3"], (CX + 66, 100), (285, 100),
              offpage("out", at=(290, 100), note="to BOG header (P-01)", note_at=(276, 94))],
       label_at=(212, 93))

# ---- relief: 2 PSVs to atmosphere, 2 vacuum relief valves (D-017) ----------------------------
for i, (nz, y) in enumerate([("N4", 150), ("N5", 165)]):
    s = "AB"[i]
    v = L.relief(f"PSV{n}131{s}", f"PSV-{n}131{s}", f"BOG-{n}00{2 + i}", 0.29,
                 "fire on the tank roof and loss of the BOG compressors with the rundown continuing (rollover as a check case)",
                 f"{TK} pressure relief to atmosphere through an elevated tailpipe; last resort after PV-1110 (D-017). Set at the design pressure +29 kPa(g), ASSUMED.")
    L.line(sheet, f"BOG-{n}00{2 + i}", dn=250, fluid="Boil-off gas", frm=TK, to="atmosphere",
           notes=f"PSV-{n}131{s} inlet and tailpipe to atmosphere.", insulation="none",
           route=[tank[nz], (205, y), v, (238 + 12 * i, y),
                  offpage("out", at=(238 + 12 * i, 125), note="to atmosphere" if i == 0 else None,
                          note_at=(244, 116), rotation=UP)],
           label_at=(220, y - 8))
for i, (nz, y) in enumerate([("N6", 180), ("N7", 195)]):
    s = "AB"[i]
    v = L.relief(f"PSV{n}133{s}", f"PSV-{n}133{s}", f"A-{n}00{1 + i}", -0.005,
                 "vacuum: withdrawal at the full loading rate with the make-up gas failed",
                 f"{TK} vacuum relief valve admitting air; last resort after PIC-1111 make-up and the I-{n}04 trip (D-017). Set -0.5 kPa(g), ASSUMED.",
                 cls="BreatherValve")
    L.line(sheet, f"A-{n}00{1 + i}", dn=250, fluid="Air", frm="atmosphere", to=TK,
           notes=f"Vacuum relief inlet of {TK} (PSV-{n}133{s}).", insulation="none",
           route=[offpage("in", at=(285, y), note="from atmosphere" if i == 0 else None,
                          note_at=(276, y - 6), rotation=180), v, tank[nz]],
           label_at=(256, y - 8 if i == 0 else y + 7))

# ---- tank instrumentation (D-007) -------------------------------------------------------------
for i, (tag, service, notes_) in enumerate([
        (f"LT-{n}101", f"{TK} level (radar, primary)", "Inventory and level control of the fill."),
        (f"LZT-{n}102", f"{TK} level (independent servo, high-high and low-low)", f"C&E I-{n}01, I-{n}02."),
        (f"LTD-{n}103", f"{TK} level-temperature-density profile", "Stratification and rollover warning (D-007)."),
        (f"TI-{n}104", f"{TK} liquid and vapour temperatures (multipoint)", "Cooldown and stratification."),
        (f"PI-{n}111", f"{TK} pressure", "Split-range pressure control is on the header, PIC-1110 / PIC-1111 (P-01)."),
        (f"PZT-{n}112", f"{TK} pressure (independent, high-high and low-low)", f"C&E I-{n}03, I-{n}04."),
        (f"TI-{n}105", f"{TK} annular space and bottom temperatures", "Inner tank leak detection; bottom heating control.")]):
    L.inst(sheet, tag, service, notes_, at=(30, inst_y[i]), sensing=tank[f"I{i + 1}"])

note(sheet, f"{TK}: full containment, 225,000 m3 working, {phase} (D-007). In-tank pumps hang in their pump columns", at=(12, 252))
note(sheet, "with foot valves; every nozzle passes through the roof (drawn on the shell for clarity, D-021).", at=(12, 258))
note(sheet, f"Minimum-flow returns FV-{n}111A..D: LNG-{n}021..{n}024 DN 150; FV-{n}112: LNG-{n}025 DN 100.", at=(12, 264))
note(sheet, f"LZT-{n}102: see C&E I-{n}01, I-{n}02. PZT-{n}112: see C&E I-{n}03, I-{n}04.", at=(12, 270))

L.finish(sheet, target)
