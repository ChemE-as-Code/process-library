"""Draft of P-04: the trestle lines between the tank area and the loading platform: loading
lines A and B (DN 800) with their tank-end flow control and ESD valves, the tank-end and
platform crossovers, the circulation header with the spray take-off, the circulation return
to the tanks, thermal relief, and vapour return lines A and B (DN 750).

Provenance only: P-04 is hand-maintained after this first revision. Run:
cheme run scripts/draft_P-04.py pid/P-04.xml (on the empty A3 frame).
Streams S2, S3, S6, S7, S10; decisions D-008, D-009, D-012, D-013, D-016, D-017, D-021.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import Lists, Sheet, note, offpage, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-04")
UP, DOWN, LEFT = 270, 90, 180
YA, YB, YC, YVA, YVB = 70, 120, 28, 195, 222

# ---- loading line A ---------------------------------------------------------------------------
ta_c = tee("T4A1", at=(80, YA), branch="up", branch_dn=250)
ta_x = tee("T4A2", at=(100, YA), branch="down", branch_dn=800)
ta_t = tee("T4A3", at=(200, YA), branch="up", branch_dn=25)
ta_p = tee("T4A4", at=(330, YA), branch="down", branch_dn=250)
fv1 = valve("FV4101", "ButterflyValve", tag="FV-4101", at=(125, YA))
xv1 = valve("XV4101", "BallValve", tag="XV-4101", at=(150, YA))
la = L.line(sheet, "LNG-4001", dn=800, fluid="LNG", frm="LNG-2001", to="LNG-5001",
            insulation="cold (PIR 200 mm)",
            notes="Loading line A over the trestle, ~2.45 km; 6,000 m3/h at 3.4 m/s with both lines loading, ~91 kPa (S3, D-008, D-011); out-leg of the circulation loop in holding (S2 holding).",
            route=[offpage("in", at=(14, YA), note="from LNG-2001 (P-02)", note_at=(30, YA - 6)),
                   ta_c, ta_x, fv1, xv1, ta_t, ta_p,
                   offpage("out", at=(405, YA), note="to LNG-5001 (P-05)", note_at=(390, YA - 6))],
            label_at=(250, YA - 8))
# ---- loading line B ---------------------------------------------------------------------------
tb_r = tee("T4B1", at=(80, YB), branch="down", branch_dn=250)
tb_x = tee("T4B2", at=(100, YB), branch="up", branch_dn=800)
tb_t = tee("T4B3", at=(220, YB), branch="up", branch_dn=25)
tb_p = tee("T4B4", at=(330, YB), branch="up", branch_dn=250)
fv2 = valve("FV4102", "ButterflyValve", tag="FV-4102", at=(125, YB))
xv2 = valve("XV4102", "BallValve", tag="XV-4102", at=(150, YB))
lb = L.line(sheet, "LNG-4002", dn=800, fluid="LNG", frm="LNG-3001", to="LNG-6001",
            insulation="cold (PIR 200 mm)",
            notes="Loading line B, as LNG-4001; return leg of the circulation loop in holding through the platform crossover LNG-4003 (D-008).",
            route=[offpage("in", at=(14, YB), note="from LNG-3001 (P-03)", note_at=(30, YB - 6)),
                   tb_r, tb_x, fv2, xv2, tb_t, tb_p,
                   offpage("out", at=(405, YB), note="to LNG-6001 (P-06)", note_at=(390, YB - 6))],
            label_at=(275, YB - 8))
# crossovers
xv3 = valve("XV4103", "BallValve", tag="XV-4103", at=(330, 95))
t_d5 = tee("T4X5", at=(330, 82), branch="right", branch_dn=80)
t_d6 = tee("T4X6", at=(330, 108), branch="right", branch_dn=80)
L.line(sheet, "LNG-4003", dn=250, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Platform crossover: circulation loop in holding (~314 m3/h, S10); open while loading so both lines reach the loading berth (D-008); receives the jetty drain pumps.",
       route=[ta_p.branch, t_d5, xv3, t_d6, tb_p.branch], label_at=(316, 102))
for nb, tt, y in [("5", t_d5, 82), ("6", t_d6, 108)]:
    L.line(sheet, f"LNG-{nb}006", dn=80, fluid="LNG", frm=f"P-{nb}101", to="LNG-4003",
           notes=f"Jetty drain pump P-{nb}101 discharge into the platform crossover, ~60 m3/h (D-016). Drawn on P-0{nb} and P-04.",
           route=[offpage("in", at=(372, y), note=f"from P-{nb}101 (P-0{nb})", note_at=(384, y - 6 if nb == "6" else y + 6), rotation=180), tt.branch],
           labels=False)
xv6 = valve("XV4106", "BallValve", tag="XV-4106", at=(100, 95))
L.line(sheet, "LNG-4006", dn=800, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Tank-end crossover: either tank's pumps load through both lines (D-008, D-011).",
       route=[ta_x.branch, xv6, tb_x.branch], label_at=(86, 102))

# ---- circulation header, spray take-off, circulation return ------------------------------------
tc3 = tee("T4C1", at=(40, YC), branch="up", branch_dn=250)
tcs = tee("T4C2", at=(60, YC), branch="up", branch_dn=80)
L.line(sheet, "LNG-2002", dn=250, fluid="LNG", frm="P-2102", to="LNG-4001",
       notes="see P-02",
       route=[offpage("in", at=(14, YC), note="from P-2102 (P-02)", note_at=(22, YC + 6)), tc3, tcs,
              (80, YC), ta_c.branch],
       label_at=(100, YC - 4))
L.line(sheet, "LNG-3002", dn=250, fluid="LNG", frm="P-3102", to="LNG-2002",
       notes="see P-03",
       route=[offpage("in", at=(40, 10), note="from P-3102 (P-03)", note_at=(22, 10), rotation=DOWN),
              tc3.branch], labels=False)
L.line(sheet, "LNG-4008", dn=80, fluid="LNG", frm="LNG-2002", to="BOG-1001 (TV-7103)",
       notes="Spray LNG to the BOG desuperheater TV-7103 (S7, 3.5 t/h at loading, D-010). Drawn on P-04 and P-07.",
       route=[tcs.branch, offpage("out", at=(60, 10), note="spray to P-07", note_at=(72, 10),
                                  rotation=UP)], labels=False)
tr2 = tee("T4R1", at=(80, 158), branch="left", branch_dn=250)
xv5 = valve("XV4105", "BallValve", tag="XV-4105", at=(80, 140))
lr = L.line(sheet, "LNG-4005", dn=250, fluid="LNG", frm="LNG-4002", to="T-2101",
            notes="Circulation return from line B to the tanks (holding, S10); to T-2101 or, via LNG-4009, T-3101 (D-008).",
            route=[tb_r.branch, xv5, tr2, (80, 172),
                   offpage("out", at=(80, 178), note="to T-2101 (P-02)", note_at=(94, 182), rotation=DOWN)],
            label_at=(66, 132))
L.line(sheet, "LNG-4009", dn=250, fluid="LNG", frm="LNG-4005", to="T-3101",
       notes="Circulation return branch to T-3101.",
       route=[tr2.branch, (50, 158), (50, 172),
              offpage("out", at=(50, 178), note="to T-3101 (P-03)", note_at=(36, 182), rotation=DOWN)],
       label_at=(36, 150))

# ---- thermal relief of the blocked-in lines (D-017) ------------------------------------------
for tt, x, k, line_no, side, yv in [(ta_t, 200, "1", "LNG-4001", "A", 42), (tb_t, 220, "2", "LNG-4002", "B", 92)]:
    v = L.relief(f"PSV411{k}", f"PSV-411{k}", f"BOG-401{k}", 15.5,
                 f"thermal expansion of {line_no} blocked in between XV-410{k} and the platform ESD valve",
                 f"Thermal relief of loading line {side} into vapour return line {side} (D-017).")
    L.line(sheet, f"BOG-401{k}", dn=25, fluid="Boil-off gas", frm=f"{line_no} (PSV-411{k})",
           to=f"BOG-400{k}", notes=f"Thermal relief outlet of loading line {side} to vapour return line {side}.",
           route=[tt.branch, v, offpage("out", at=(x, yv), note=f"to vapour return {side}",
                                        note_at=(x + 18, yv), rotation=UP)],
           labels=False)

# ---- vapour return lines ------------------------------------------------------------------------
va = L.line(sheet, "BOG-4001", dn=750, fluid="Boil-off gas", frm="BOG-5001 (Berth 2)", to="BOG-1001",
            insulation="cold (PIR 150 mm)",
            notes="Vapour return line A over the trestle (Berth 2), 45.6 t/h at loading (S6), ~9 m/s (D-009, D-012).",
            route=[offpage("in", at=(405, YVA), note="from BOG-5001 (P-05)", note_at=(382, YVA - 6),
                           rotation=LEFT),
                   offpage("out", at=(14, YVA), note="to BOG header (P-01)", note_at=(30, YVA - 6),
                           rotation=LEFT)],
            label_at=(200, YVA - 8))
vb = L.line(sheet, "BOG-4002", dn=750, fluid="Boil-off gas", frm="BOG-6001 (Berth 1)", to="BOG-1001",
            insulation="cold (PIR 150 mm)",
            notes="Vapour return line B over the trestle (Berth 1), as BOG-4001.",
            route=[offpage("in", at=(405, YVB), note="from BOG-6001 (P-06)", note_at=(382, YVB + 6),
                           rotation=LEFT),
                   offpage("out", at=(14, YVB), note="to BOG header (P-01)", note_at=(30, YVB + 6),
                           rotation=LEFT)],
            label_at=(200, YVB + 8))

# ---- instruments ----------------------------------------------------------------------------------
L.inst(sheet, "FIC-4101", "Loading line A flow (loading rate)",
       "Ramps the loading up and down to the carrier's cargo plan; FV-4101 butterfly (D-011).",
       at=(170, 84), sensing=la.segments[2], sensing_at=(170, YA), signal_to=fv1, fail_action="FL")
L.inst(sheet, "FIC-4102", "Loading line B flow (loading rate)", "As FIC-4101.",
       at=(170, 134), sensing=lb.segments[2], sensing_at=(170, YB), signal_to=fv2, fail_action="FL")
L.inst(sheet, "UZ-4101", "Loading line A tank-end ESD valve XV-4101", "ESD-1 closes (C&E I-501, I-601).",
       at=(150, 57), signal_to=xv1, fail_action="FC")
L.inst(sheet, "UZ-4102", "Loading line B tank-end ESD valve XV-4102", "ESD-1 closes (C&E I-501, I-601).",
       at=(150, 107), signal_to=xv2, fail_action="FC")
L.inst(sheet, "HS-4103", "Platform crossover XV-4103", "Open in holding (circulation) and while loading (D-008).",
       at=(346, 95), signal_to=xv3, fail_action="FL")
L.inst(sheet, "HS-4106", "Tank-end crossover XV-4106", "Operator selection (D-008).",
       at=(114, 95), signal_to=xv6, fail_action="FL")
L.inst(sheet, "HS-4105", "Circulation return XV-4105", "Open in holding (D-008).",
       at=(94, 140), signal_to=xv5, fail_action="FL")
L.inst(sheet, "TI-4102", "Circulation return temperature at the tanks",
       "Holding: the loop is cold when the rise is under 3 K (D-008).",
       at=(96, 166), sensing=lr.segments[1], sensing_at=(80, 166))
for tag, service, x, seg, y, yb in [
        ("PI-4105", "Loading line A pressure at the platform", 285, la.segments[-2], YA, 57),
        ("TI-4103", "Loading line A temperature at the platform (cooldown)", 302, la.segments[-2], YA, 57),
        ("PI-4106", "Loading line B pressure at the platform", 285, lb.segments[-2], YB, 134),
        ("TI-4104", "Loading line B temperature at the platform (cooldown)", 302, lb.segments[-2], YB, 134),
        ("PI-4121", "Vapour return A pressure at the platform", 285, va.segments[0], YVA, 182),
        ("TI-4122", "Vapour return A temperature at the platform", 302, va.segments[0], YVA, 182),
        ("PI-4123", "Vapour return B pressure at the platform", 285, vb.segments[0], YVB, 209),
        ("TI-4124", "Vapour return B temperature at the platform", 302, vb.segments[0], YVB, 209)]:
    L.inst(sheet, tag, service, at=(x, yb), sensing=seg, sensing_at=(x, y))

note(sheet, "Trestle ~1.98 km at 178 deg; ~2.45 km per line tank to platform (D-013). Expansion loops,", at=(150, 158))
note(sheet, "guides, drip trays to the impoundment sump and the low-point drains are not shown (D-021).", at=(150, 164))
note(sheet, "Circulation (holding): P-2102 / P-3102 -> LNG-2002 -> line A -> XV-4103 -> line B -> LNG-4005 (D-008).", at=(150, 170))
note(sheet, "UZ-4101 / UZ-4102: see C&E I-501, I-601 (ESD-1 of either berth).", at=(12, 252))
note(sheet, "LNG-3002 (DN 250): T-3101 circulation; LNG-4008 (DN 80): spray to the desuperheater; LNG-5006 / -6006 (DN 80): drains;", at=(12, 258))
note(sheet, "BOG-4011 / BOG-4012 (DN 25): thermal relief of the loading lines into the vapour return.", at=(12, 264))

L.finish(sheet, target)
