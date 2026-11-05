"""Draft of a tank sheet (P-02: T-2101, P-03: T-3101): the full-containment LNG tank with its
four in-tank loading pumps and the circulation pump, their discharge header, minimum-flow
returns, the fill and circulation-return lines, the vapour outlet, the PSVs and vacuum relief
valves and the tank instrumentation.

Provenance only: the sheets are hand-maintained after this first revision. Run:
cheme run scripts/draft_tank.py pid/P-02.xml 2   (or pid/P-03.xml 3), on the empty A3 frame.
Decisions D-007, D-008, D-011, D-017, D-021. All nozzles of a full-containment tank pass
through the roof; the sheet draws the bottom fill, the circulation return, the relief valves
and the instrument connections on the shell for clarity (D-021).

Revision after the basic-design review (reviews/2026-11-05-basic-design.md) and HAZOP H-01 /
H-02: thermal relief of the pump header and the circulation header back into the tank (#6,
H-02 A2), N+1 pressure and vacuum relief with the vacuum set less negative than the design
vacuum (#15), an independent second high-high level LZT-n106 on its own nozzle, 1oo2 with
LZT-n102 (#16), an isolation valve and a vent / N2 purge connection on every pump column
(#24, H-02 A3). Round 2: the CV/HV spool of each column is relieved to the column by a
pressure-equalising hole in the check valve disc (sheet note), the relief valve tags are
printed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chemeascode.domains.piping.authoring import label  # noqa: E402
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
# the column stack from the header down: isolation valve, check valve, vent tee, FIC, min-flow tee
HEADER_Y, CIRC_Y, HV_Y, CV_Y, VENT_Y, MF_Y = 50, 35, 57, 65, 73, 96
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
# thermal relief returns (roof nozzles): header PSV right of the columns, circulation PSV left
TR_HDR_X, TR_CIRC_X, BOG_DX, FILL_DX = 184, 59, 70, -68
# right shell: pressure PSVs, vacuum valves (N+1 each), circulation return
PSV_Y = [141, 155, 169]
VAC_Y = [184, 198, 212]
PSV_X, VAC_X = 228, 238  # valve positions; their tags above them, the line labels beside
RET_Y = 232

# ---- the tank and its pumps ------------------------------------------------------------------
noz = [Nozzle("N1", (FILL_DX, roof(FILL_DX)), 900), Nozzle("N2", (-72, 56), 900),
       Nozzle("N3", (BOG_DX, roof(BOG_DX)), 750 if n == "2" else 600)]
noz += [Nozzle(nz, (72, y - CY), 250) for nz, y in zip(["N4", "N5", "N11"], PSV_Y)]
noz += [Nozzle(nz, (72, y - CY), 250) for nz, y in zip(["N6", "N7", "N12"], VAC_Y)]
noz += [Nozzle("N8", (72, RET_Y - CY), 250),
        Nozzle("N9", (TR_HDR_X - CX, roof(TR_HDR_X - CX)), 25),
        Nozzle("N10", (TR_CIRC_X - CX, roof(TR_CIRC_X - CX)), 25)]
noz += [Nozzle(f"M{k}", (x - CX, roof(x - CX)), 150 if k != "R" else 100) for k, x in mf_x.items()]
# instrument nozzles top to bottom; I8 (LZT-n106, its own nozzle) sits next to LZT-n102
INSTS = [  # (nozzle, tag, service, notes)
    ("I1", f"LT-{n}101", f"{TK} level (radar, primary)", "Inventory and level control of the fill."),
    ("I2", f"LZT-{n}102", f"{TK} level (independent servo, high-high and low-low)", f"C&E I-{n}01, I-{n}02."),
    ("I8", f"LZT-{n}106", f"{TK} level (second independent high-high, own nozzle)",
     f"Independent of LZT-{n}102 and LT-{n}101; 1oo2 high-high with LZT-{n}102 (either trips), C&E I-{n}01 (review 2026-11-05 #16)."),
    ("I3", f"LTD-{n}103", f"{TK} level-temperature-density profile", "Stratification and rollover warning (D-007)."),
    ("I4", f"TI-{n}104", f"{TK} liquid and vapour temperatures (multipoint)", "Cooldown and stratification."),
    ("I5", f"PI-{n}111", f"{TK} pressure", "Split-range pressure control is on the header, PIC-1110 / PIC-1111 (P-01)."),
    ("I6", f"PZT-{n}112", f"{TK} pressure (independent, high-high and low-low)", f"C&E I-{n}03, I-{n}04."),
    ("I7", f"TI-{n}105", f"{TK} annular space and bottom temperatures", "Inner tank leak detection; bottom heating control.")]
inst_y = [139 + 10 * i for i in range(len(INSTS))]
noz += [Nozzle(nz, (-72, y - CY), 50) for (nz, *_), y in zip(INSTS, inst_y)]
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


def hv(k):
    """The column isolation valve (review #24): HV-n151A..D, HV-n152 for the circulation pump."""
    tag = f"HV-{n}151{k}" if k != "R" else f"HV-{n}152"
    return valve(tag.replace("-", ""), "BallValve", tag=tag, at=(COLS.get(k, CIRC_X), HV_Y))


# ---- discharge header and pump columns --------------------------------------------------------
heads = {k: tee(f"T{n}1H{k}", at=(COLS[k], HEADER_Y), branch="down", branch_dn=450) for k in "BCD"}
mfs = {k: tee(f"T{n}1M{k}", at=(COLS.get(k, CIRC_X), MF_Y), branch="right",
              branch_dn=150 if k != "R" else 100) for k in "ABCDR"}
vents = {k: tee(f"T{n}1V{k}", at=(COLS.get(k, CIRC_X), VENT_Y), branch="right", branch_dn=25)
         for k in "ABCDR"}
hvs = {k: hv(k) for k in "ABCDR"}
tr_hdr = tee(f"T{n}1PH", at=(TR_HDR_X, HEADER_Y), branch="down", branch_dn=25)
tr_circ = tee(f"T{n}1PR", at=(CIRC_X, 45), branch="left", branch_dn=25)
line_a = L.line(sheet, f"LNG-{n}001", dn=800, fluid="LNG", frm=f"P-{n}101A", to=f"LNG-400{int(n) - 1} (P-04)",
                notes=f"{TK} loading pump discharge header to loading line {side}, up to 12,000 m3/h (D-011); segments S1-S3 are the DN 450 column of P-{n}101A, where the header starts (D-021); thermal relief PSV-{n}141 (review #6).",
                segments=[{"number": s, "nominal_diameter": "DN450", "notes": f"P-{n}101A pump column"}
                          for s in ("S1", "S2", "S3")],
                route=[pumps["A"]["N2"], mfs["A"], vents["A"],
                       valve(f"CV{n}121A", "SwingCheckValve", tag=f"CV-{n}121A", at=(COLS["A"], CV_Y)), hvs["A"],
                       (COLS["A"], HEADER_Y), heads["B"], heads["C"], heads["D"], tr_hdr,
                       offpage("out", at=(285, HEADER_Y), note=f"to trestle line {side} (P-04)",
                               note_at=(272, HEADER_Y + 6))],
                label_at=(225, HEADER_Y - 8))
# the column of P-n101A (segments S1-S3) is DN 450 like the others
set_dn(sheet, [f"T{n}1MA_N1", f"T{n}1MA_N2", f"T{n}1VA_N1", f"T{n}1VA_N2", f"CV{n}121A_N1",
               f"CV{n}121A_N2", f"HV{n}151A_N1", f"HV{n}151A_N2", f"T{n}1HB_N1"], 450,
       segments=[f"Line_LNG{n}001_S1", f"Line_LNG{n}001_S2", f"Line_LNG{n}001_S3"])
for k in "BCD":
    L.line(sheet, f"LNG-{n}01{ord(k) - 64}", dn=450, fluid="LNG", frm=f"P-{n}101{k}", to=f"LNG-{n}001",
           notes=f"P-{n}101{k} pump column (3,000 m3/h, D-011) with its check valve and isolation valve HV-{n}151{k}.",
           route=[pumps[k]["N2"], mfs[k], vents[k],
                  valve(f"CV{n}121{k}", "SwingCheckValve", tag=f"CV-{n}121{k}", at=(COLS[k], CV_Y)), hvs[k],
                  heads[k].branch],
           label_at=(COLS[k] - 9, 165))
L.line(sheet, f"LNG-{n}002", dn=250, fluid="LNG", frm=f"P-{n}102", to="LNG-4001" if n == "2" else "LNG-2002",
       notes=(f"{TK} circulation pump discharge and circulation header into loading line A, with the desuperheater spray take-off; holding ~314 m3/h (D-008, D-010). Thermal relief PSV-{n}142 (review #6). Drawn on P-02 and P-04."
              if n == "2" else f"{TK} circulation pump discharge into the circulation header LNG-2002. Thermal relief PSV-{n}142 (review #6). Drawn on P-03 and P-04."),
       route=[pumps["R"]["N2"], mfs["R"], vents["R"],
              valve(f"CV{n}122", "SwingCheckValve", tag=f"CV-{n}122", at=(CIRC_X, CV_Y)), hvs["R"], tr_circ,
              (CIRC_X, CIRC_Y), offpage("out", at=(285, CIRC_Y), note="to circulation and spray (P-04)",
                                         note_at=(262, CIRC_Y - 6))],
       label_at=(200, CIRC_Y - 8))
for k, x in [("R", CIRC_X), *COLS.items()]:
    label(sheet, hvs[k].id, "PipingComponentNumber", at=(x + 9, HV_Y))
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
    # column vent / N2 purge connection (review #24, H-02 A3): DN 25, ball valve, open to the roof
    j = "12345"["ABCDR".index(k)]
    L.line(sheet, f"BOG-{n}01{j}", dn=25, fluid="Boil-off gas",
           frm=pump_tag, to="atmosphere (roof) / N2 hose", insulation="none", labels=False,
           notes=f"{pump_tag} column vent and N2 purge connection HV-{n}16{j} (ball valve, blind-flanged, to atmosphere at the roof; N2 hose for purging before the pump is lifted; vendor to confirm, H-02 A3). Number and size in the sheet note.",
           route=[vents[k].branch,
                  valve(f"HV{n}16{j}", "BallValve", tag=f"HV-{n}16{j}", at=(x + 5, VENT_Y)),
                  offpage("out", at=(x + 10, VENT_Y))])
L.inst(sheet, f"PI-{n}117", f"{TK} loading header pressure", at=(250, HEADER_Y + 12),
       sensing=line_a.segments[-1], sensing_at=(250, HEADER_Y))

# ---- thermal relief of the blockable headers back into the tank (review #6, H-02 A2) ---------
blocked = "XV-4101" if n == "2" else "XV-4102"
for tee_, nz, line_no, psv, x, hdr, where in [
        (tr_hdr, "N9", f"LNG-{n}031", f"PSV-{n}141", TR_HDR_X, f"LNG-{n}001",
         f"pump discharge header LNG-{n}001 between the column check valves and {blocked} (P-04)"),
        (tr_circ, "N10", f"LNG-{n}032", f"PSV-{n}142", TR_CIRC_X, f"LNG-{n}002",
         f"circulation header LNG-{n}002 behind the check valve of P-{n}102")]:
    # tag beside the vertical relief line: right of PSV-n141, left of PSV-n142
    v = L.relief(psv.replace("-", ""), psv, line_no, 15.0,
                 f"thermal expansion of the blocked-in {where}",
                 f"Thermal relief of {hdr} into {TK} through a roof nozzle; set at the 15 barg design pressure of the LNG lines (review #6).",
                 label_at=(x + 12, 82) if nz == "N9" else (x - 11, 80))
    v.at = (x, 82 if nz == "N9" else 80)
    route = [tee_.branch, v, tank[nz]] if nz == "N9" else [tee_.branch, (x, 45), v, tank[nz]]
    L.line(sheet, line_no, dn=25, fluid="LNG", frm=hdr, to=TK, labels=False, route=route,
           notes=f"{psv} inlet and discharge, thermal relief of {hdr} back into {TK} (roof nozzle). Number and size in the sheet note.")

# ---- fill, circulation return, vapour -------------------------------------------------------
L.line(sheet, "LNG-1002" if n == "2" else "LNG-1001", dn=900, fluid="LNG",
       frm="LNG-1001" if n == "2" else "BL (train 1)", to=TK,
       notes=(f"Fill to {TK}; top fill (spray ring under the deck) or bottom fill via LNG-1004, chosen from AI-1102 against LTD-2103 (rollover, D-007). Drawn on P-01 and P-02."
              if n == "2" else "rundown header (see P-01); its end is the T-3101 top fill."),
       route=[offpage("in", at=(14, 112), note="top fill from P-01", note_at=(22, 106)),
              (CX + FILL_DX, 112), tank["N1"]], label_at=(30, 120))
L.line(sheet, "LNG-1004" if n == "2" else "LNG-1003", dn=900, fluid="LNG",
       frm="LNG-1002" if n == "2" else "LNG-1001", to=TK,
       notes=f"{TK} bottom fill (internal down-comer to the tank bottom) (D-007). Drawn on P-01 and P-0{n}.",
       route=[offpage("in", at=(14, 226), note="bottom fill from P-01", note_at=(24, 220)), tank["N2"]],
       label_at=(30, 234))
xvr = valve(f"XV{n}123", "BallValve", tag=f"XV-{n}123", at=(232, RET_Y))
L.line(sheet, "LNG-4005" if n == "2" else "LNG-4009", dn=250, fluid="LNG",
       frm="LNG-4002" if n == "2" else "LNG-4005", to=TK,
       notes=(f"Circulation return from line B to the tanks (holding, S10); to T-2101 or, via LNG-4009, T-3101 (D-008). Drawn on P-04 and P-02."
              if n == "2" else "Circulation return branch to T-3101. Drawn on P-04 and P-03."),
       route=[offpage("in", at=(285, RET_Y), note="circulation return from P-04", note_at=(266, RET_Y + 8),
                      rotation=180), xvr, tank["N8"]],
       label_at=(210, RET_Y + 8))
L.inst(sheet, f"HS-{n}123", f"{TK} circulation return valve XV-{n}123",
       "Opened for the tank that receives the circulation (D-008).",
       at=(232, RET_Y - 13), signal_to=xvr.id, fail_action="FL")
L.line(sheet, "BOG-1001" if n == "2" else "BOG-1003", dn=750 if n == "2" else 600,
       fluid="Boil-off gas", frm=TK, to="D-7101" if n == "2" else "BOG-1001",
       notes=("see P-01" if n == "2" else "T-3101 vapour outlet to the tank vapour header. Drawn on P-03 and P-01."),
       route=[tank["N3"], (CX + BOG_DX, 100), (285, 100),
              offpage("out", at=(290, 100), note="to BOG header (P-01)", note_at=(276, 94))],
       label_at=(212, 93))

# ---- relief: 3 PSVs to atmosphere, 3 vacuum relief valves, N+1 each (D-017, review #15) -------
N1_NOTE = "N+1, interlocked locked-open inlet isolation (vendor)"
for i, (nz, y) in enumerate(zip(["N4", "N5", "N11"], PSV_Y)):
    s = "ABC"[i]
    riser = 236 + 12 * i
    v = L.relief(f"PSV{n}131{s}", f"PSV-{n}131{s}", f"BOG-{n}00{2 + i}", 0.29,
                 "loss of the BOG compressors at loading (45.6 t/h return plus the rundown displacement), fire, rollover as a check case",
                 f"{TK} pressure relief to atmosphere through an elevated tailpipe; last resort after PV-1110 (D-017). Set at the design pressure +29 kPa(g), ASSUMED. {N1_NOTE} (review #15).",
                 label_at=(PSV_X, y - 4))
    v.at = (PSV_X, y)
    L.line(sheet, f"BOG-{n}00{2 + i}", dn=250, fluid="Boil-off gas", frm=TK, to="atmosphere",
           notes=f"PSV-{n}131{s} inlet and tailpipe to atmosphere.", insulation="none",
           route=[tank[nz], (205, y), v, (riser, y),
                  offpage("out", at=(riser, 125), note="to atmosphere" if i == 0 else None,
                          note_at=(248, 116), rotation=UP)],
           label_at=(206, y - 7))
for i, (nz, y) in enumerate(zip(["N6", "N7", "N12"], VAC_Y)):
    s = "ABC"[i]
    v = L.relief(f"PSV{n}133{s}", f"PSV-{n}133{s}", f"A-{n}00{1 + i}", -0.003,
                 "vacuum: withdrawal at the full loading rate with the make-up gas failed",
                 f"{TK} vacuum relief valve admitting air; last resort after PIC-1111 make-up and the I-{n}04 trip (D-017). Set -0.3 kPa(g), less negative than the -0.5 kPa(g) design vacuum, ASSUMED. {N1_NOTE} (review #15).",
                 cls="BreatherValve", label_at=(VAC_X, y - 4))
    v.at = (VAC_X, y)
    L.line(sheet, f"A-{n}00{1 + i}", dn=250, fluid="Air", frm="atmosphere", to=TK,
           notes=f"Vacuum relief inlet of {TK} (PSV-{n}133{s}).", insulation="none",
           route=[offpage("in", at=(285, y), note="from atmosphere" if i == 0 else None,
                          note_at=(276, y - 6), rotation=180), v, tank[nz]],
           label_at=(256, y - 7))

# ---- tank instrumentation (D-007) -------------------------------------------------------------
for (nz, tag, service, notes_), y in zip(INSTS, inst_y):
    L.inst(sheet, tag, service, notes_, at=(30, y), sensing=tank[nz])

NOTES = [
    f"{TK}: full containment, 225,000 m3 working, {phase} (D-007). In-tank pumps hang in their pump columns with foot valves; every nozzle passes through the roof (drawn on the shell for clarity, D-021).",
    f"Minimum-flow returns FV-{n}111A..D: LNG-{n}021..{n}024 DN 150; FV-{n}112: LNG-{n}025 DN 100.",
    f"Column isolation HV-{n}151A..D, HV-{n}152 above the check valves; column vent / N2 purge BOG-{n}011..{n}015 DN 25 with HV-{n}161..{n}165 (blind-flanged, to atmosphere at the roof).",
    # the spool between the column check valve and HV-n151 / HV-n152 is blockable (round 2)
    f"CV-{n}121A..D, CV-{n}122: disc with a pressure-equalising hole, relieving the CV/HV spool to the pump column (thermal relief; vendor, D-021).",
    f"Thermal relief to {TK} (roof nozzles), set 15.0 barg: PSV-{n}141 on LNG-{n}001 via LNG-{n}031, PSV-{n}142 on LNG-{n}002 via LNG-{n}032, DN 25.",
    f"PSV-{n}131A..C (0.29 barg) and vacuum relief PSV-{n}133A..C (-0.3 kPa(g)): {N1_NOTE}.",
    f"LZT-{n}102: see C&E I-{n}01, I-{n}02. LZT-{n}106: independent high-high, 1oo2 with LZT-{n}102 (C&E I-{n}01). PZT-{n}112: see C&E I-{n}03, I-{n}04."]
for i, text in enumerate(NOTES):
    note(sheet, text, at=(12, 252 + 4.6 * i))

L.finish(sheet, target)
