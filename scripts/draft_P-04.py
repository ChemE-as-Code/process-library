"""Throwaway generator for pid/P-04.xml (products, storage, backup), stage S4.

Reuses the helper functions of scripts/draft_P-01.py (everything above its "# Equipment" marker).
After the first run the XML is the source of truth (AGENTS.md).
Layout (D-024): GOX train along the top (y 45), GAN train in the middle (y 115), LIN storage and
backup bottom left, LOX storage and backup bottom right; the backup GOX riser runs up the right edge.
Usage: python3 scripts/regen.py P-04
"""
import os
import sys

_src = open(os.path.join(os.path.dirname(__file__), "draft_P-01.py"), encoding="utf-8").read()
exec(_src[:_src.index("# Equipment\n")])          # noqa: S102 - helpers only
LABEL_ROW = True


def N(eid, suf):
    return ("%s_%s" % (eid, suf), "%s_%s_Node" % (eid, suf))


P = lambda *b: ("pipe", list(b))     # noqa: E731
I = lambda o: ("item", o)            # noqa: E731
E = lambda o, k=0: ("end", o, k)     # noqa: E731


def psv(vid, x, y, d, tag, lab=(-2, -3, "RightCenter")):
    return valve(vid, "SpringLoadedGlobeSafetyValve", x, y, 270, d, tag, lab=lab)


def sil(vid, x, y, rot, d, tag, srot, lab):
    return valve(vid, "Silencer", x, y, rot, d, tag, shape_id="ShapeASU_Silencer", sc=1.0, half=6.0, srot=srot, lab=lab)


def extra_signal(tag, pts):
    """Second signal line of an instrument (one controller acting on two final elements)."""
    iid = "Inst_" + tag.replace("-", "")
    k = len(DRW) - 1
    while ('id="%s_Drawing"' % iid) not in DRW[k]:
        k -= 1
    mark = '</Components><Components property="NodePositions">'
    DRW[k] = DRW[k].replace(mark, static(iid + "_Signal2", [polyline(iid + "_Signal2Line", pts, 0.2, (0, 0, 0),
                                                                      "Dash")]) + mark, 1)


def note(tag, x, y, txt, al="LeftCenter"):
    """Annotation (trip outputs) inside the drawing group of an instrument."""
    iid = "Inst_" + tag.replace("-", "")
    k = len(DRW) - 1
    while ('id="%s_Drawing"' % iid) not in DRW[k]:
        k -= 1
    mark = '</Components><Components property="NodePositions">'
    DRW[k] = DRW[k].replace(mark, static(iid + "_Note", [text(iid + "_NoteText", x, y, txt, 2.0, al)]) + mark, 1)


# ---- shapes: flat-bottom double-wall storage tank, ambient-air vaporizer
shape("ShapeASU_T41", "FLAT_BOTTOM_TANK_SHAPE",
      [polyline("ShapeASU_T41_P1", [(-15, 30), (-15, -27), (-12, -30), (12, -30), (15, -27), (15, 30)], 0.35, EQ,
                closed=True),
       polyline("ShapeASU_T41_P2", [(-12.5, 28), (-12.5, -26), (-10.5, -28), (10.5, -28), (12.5, -26), (12.5, 28)],
                0.2, EQ, "Dash", closed=True)])
shape("ShapeASU_Vap", "AMBIENT_AIR_VAPORIZER_SHAPE",
      [polyline("ShapeASU_Vap_P1", [(-8, -4), (8, -4), (8, 4), (-8, 4)], 0.35, EQ, closed=True)]
      + [polyline("ShapeASU_Vap_F%d" % i, [(x, -4), (x, 4)], 0.2, EQ) for i, x in enumerate((-4, 0, 4))])

# ---- equipment
equipment("K4101", "CentrifugalCompressor", "K-4101", "ShapeASU_Compressor", 110, 45,
          [("N1", "N1", 98, 45, 500), ("N2", "N2", 122, 45, 200), ("N3", "N3", 104, 53.75, 300),
           ("N4", "N4", 116, 51.25, 300)], (92, 57), inst=[("I1", 110, 37.5), ("I2", 120, 50.4)])
equipment("E4101", "TubularHeatExchanger", "E-4101", "ShapeASU_Cooler", 110, 67,
          [("N1", "N1", 107, 61.8, 300), ("N2", "N2", 113, 61.8, 300)], (97, 72))
equipment("E4102", "TubularHeatExchanger", "E-4102", "ShapeASU_Cooler", 138, 45,
          [("N1", "N1", 132, 45, 200), ("N2", "N2", 144, 45, 200), ("N3", "N3", 135, 50.2, 100),
           ("N4", "N4", 141, 50.2, 100)], (138, 36))
equipment("K4102", "CentrifugalCompressor", "K-4102", "ShapeASU_Compressor", 100, 115,
          [("N1", "N1", 88, 115, 250), ("N2", "N2", 112, 115, 150)], (104, 101), inst=[("I1", 100, 121)])
equipment("E4103", "TubularHeatExchanger", "E-4103", "ShapeASU_Cooler", 125, 115,
          [("N1", "N1", 119, 115, 150), ("N2", "N2", 131, 115, 150), ("N3", "N3", 122, 120.2, 100),
           ("N4", "N4", 128, 120.2, 100)], (125, 106))
for eid, tag, x in [("T4102", "T-4102", 50), ("T4101", "T-4101", 250)]:
    equipment(eid, "Tank", tag, "ShapeASU_T41", x, 195,
              [("N1", "N1", x + 10, 165, 40), ("N2", "N2", x - 2, 165, 100), ("N3", "N3", x + 15, 175, 80),
               ("N4", "N4", x + 8, 225, 80), ("N5", "N5", x + 15, 185, 25)], (x, 200),
              inst=[("I1", x - 15, 180), ("I2", x - 15, 200)] + ([("I3", x - 15, 220)] if x > 100 else []))
for pre, x0 in [("4102", 95), ("4101", 295)]:
    for k, y, ly in [("A", 233, 224), ("B", 251, 258)]:
        equipment("P%s%s" % (pre, k), "CentrifugalPump", "P-%s%s" % (pre, k), "Shape21", x0, y,
                  [("N1", "N1", x0 - 7.5, y, 80), ("N2", "N2", x0 + 7.5, y, 50)], (x0 if k == "A" else x0 + 15, ly))
for pre, x0 in [("4106", 152), ("4105", 352)]:
    for k, y, ly in [("A", 233, 226), ("B", 251, 258)]:
        equipment("E%s%s" % (pre, k), "HeatExchanger", "E-%s%s" % (pre, k), "ShapeASU_Vap", x0, y,
                  [("N1", "N1", x0 - 8, y, 50), ("N2", "N2", x0 + 8, y, 100)], (x0, ly))

# ---- instrument sensing points on pipes
PIPE_INST[("GOX-4001", 1, 1)] = [("I1", 28, 45)]
PIPE_INST[("GOX-4001", 3, 2)] = [("I1", 88, 45)]
PIPE_INST[("GOX-4002", 7, 2)] = [("I1", 240, 45)]
PIPE_INST[("GOX-4002", 8, 1)] = [("I1", 318, 45)]
PIPE_INST[("GAN-4001", 1, 1)] = [("I1", 26, 115)]
PIPE_INST[("GAN-4001", 2, 1)] = [("I1", 60, 115), ("I2", 78, 115)]
PIPE_INST[("GAN-4002", 3, 2)] = [("I1", 150, 115)]
PIPE_INST[("GAN-4003", 4, 1)] = [("I1", 192, 195)]
PIPE_INST[("GAN-4003", 4, 2)] = [("I1", 192, 160)]
PIPE_INST[("GOX-4004", 4, 1)] = [("I1", 400, 200)]
PIPE_INST[("GOX-4004", 4, 2)] = [("I1", 400, 160)]

# ---- GOX compressor K-4101: suction vent, ESD, recycle, aftercooler, relief, blowdown, export
OPC_G = offpage("OPC_GOX4001_in", True, 20, 45, 0, 500, "from P-03 E-3101", (16, 52, "CenterCenter"))
TV3 = tee("Tee_GOX4001_V", 42, 45, 0, 270, 500, 300)
TRC = tee("Tee_GOX4001_R", 65, 45, 0, 90, 500, 150)
XV17 = valve("XV4117", "BallValve", 76, 45, 0, 500, "XV-4117", act=270)
system("GOX-4001", 500, "Oxygen", [(None, (OPC_G["id"], OPC_G["nodes"][0]), [P(), E(TV3)], None),
                                   (None, (TV3["id"], TV3["nodes"][1]), [P(), E(TRC)], None),
                                   (None, (TRC["id"], TRC["nodes"][1]), [P(), I(XV17), P()], N("K4101", "N1"))],
       (44, 42))
PV1B = valve("PV4101B", "GlobeValve", 42, 36, 270, 300, "PV-4101B", act=0, lab=(-3, 0, "RightCenter"))
S42 = sil("S4102", 42, 24, 270, 300, "S-4102", 0, (-6, 0, "RightCenter"))
OPC_V3 = offpage("OPC_VNT4003_atm", False, 42, 15, 270, 300, "to atm. (elevated, safe location)", (46, 10, "LeftCenter"))
system("VNT-4003", 300, "Oxygen", [(None, (TV3["id"], TV3["nodes"][2]), [P(), I(PV1B), P(), I(S42), P(), E(OPC_V3)],
                                    None)], (48, 26, "v"))
system("GOX-4005", 300, "Oxygen", [(None, N("K4101", "N3"), [P((104, 58), (107, 58))], N("E4101", "N1")),
                                   (None, N("E4101", "N2"), [P((113, 58), (116, 58))], N("K4101", "N4"))],
       (88, 63, "v"))
for ln, nz, x, inflow, rot, lab, eq in [("CW-4001", "N3", 135, True, 270, (122, 59, "v"), "E4102"),
                                        ("CWR-4001", "N4", 141, False, 90, (145, 59, "v"), "E4102"),
                                        ("CW-4002", "N3", 122, True, 270, (112.5, 124, "v"), "E4103"),
                                        ("CWR-4002", "N4", 128, False, 90, (137, 128.5, "v"), "E4103")]:
    y = 58 if eq == "E4102" else 128
    o = offpage("OPC_%s" % ln.replace("-", ""), inflow, x, y, rot, 100, "CW" if inflow else "CWR",
                (x, y + 12, "CenterCenter"))
    system(ln, 100, "Cooling water" if inflow else "Cooling water return",
           [(None, (o["id"], o["nodes"][0]), [P()], N(eq, nz))] if inflow else
           [(None, N(eq, nz), [P(), E(o)], None)], lab)
TRY = tee("Tee_GOX4002_R", 155, 45, 0, 90, 200, 150)
TPS = tee("Tee_GOX4002_PSV", 165, 45, 0, 270, 200, 80)
TBD = tee("Tee_GOX4002_BD", 180, 45, 0, 270, 200, 150)
XV18 = valve("XV4118", "BallValve", 195, 45, 0, 200, "XV-4118", act=270, lab=(0, 15, "CenterCenter"))
# pressure-equalizing bypasses around the 31 bara ESD valves (O2 review F2, D-024): open first, XV opens on low dP
TA1 = tee("Tee_GOX4002_EQ1", 189, 45, 0, 90, 200, 25)
TA2 = tee("Tee_GOX4002_EQ2", 201, 45, 0, 90, 200, 25)
TB1 = tee("Tee_GOX4002_EQ3", 339, 45, 0, 90, 200, 25)
TB2 = tee("Tee_GOX4002_EQ4", 351, 45, 0, 90, 200, 25)
HV29 = valve("HV4129", "GlobeValve", 195, 52, 0, 25, "HV-4129", lab=(0, 4.5, "CenterCenter"))
HV30 = valve("HV4130", "GlobeValve", 345, 52, 0, 25, "HV-4130", lab=(0, 4.5, "CenterCenter"))
CV1 = valve("CV_GOX4002", "SwingCheckValve", 208, 45, 0, 200)
TBK = tee("Tee_GOX4002_BK", 300, 45, 0, 270, 200, 100)
XV19 = valve("XV4119", "BallValve", 345, 45, 0, 200, "XV-4119", act=270, lab=(0, 15, "CenterCenter"))
# true double block and bleed at the BL (D-013): XV-4119 + XV-4132, bleed XV-4133 between them
TBL = tee("Tee_GOX4002_BL", 357, 45, 0, 90, 200, 25)
XV32 = valve("XV4132", "BallValve", 364, 45, 0, 200, "XV-4132", act=270, lab=(0, 15, "CenterCenter"))
XV33 = valve("XV4133", "BallValve", 357, 55, 90, 25, "XV-4133", act=0, lab=(10, 0, "LeftCenter"))
OPC_B1 = offpage("OPC_VNT4006_atm", False, 357, 64, 90, 25, "to atm. (safe location)", (361, 68, "LeftCenter"))
OPC_GX = offpage("OPC_GOX4002_BL", False, 376, 45, 0, 200, "to GOX BL", (380, 40, "LeftCenter"))
PS22 = psv("PSV4122", 165, 33, 80, "PSV-4122")
system("GOX-4002", 200, "Oxygen", [(None, N("K4101", "N2"), [P()], N("E4102", "N1")),
                                   (None, N("E4102", "N2"), [P(), E(TRY)], None),
                                   (None, (TRY["id"], TRY["nodes"][1]), [P(), E(TPS)], None),
                                   (None, (TPS["id"], TPS["nodes"][1]), [P(), E(TBD)], None),
                                   (None, (TBD["id"], TBD["nodes"][1]), [P(), E(TA1)], None),
                                   (None, (TA1["id"], TA1["nodes"][1]), [P(), I(XV18), P(), E(TA2)], None),
                                   (None, (TA2["id"], TA2["nodes"][1]), [P(), I(CV1), P(), E(TBK)], None),
                                   (None, (TBK["id"], TBK["nodes"][1]), [P(), E(TB1)], None),
                                   (None, (TB1["id"], TB1["nodes"][1]), [P(), I(XV19), P(), E(TB2)], None),
                                   (None, (TB2["id"], TB2["nodes"][1]), [P(), E(TBL)], None),
                                   (None, (TBL["id"], TBL["nodes"][1]), [P(), I(XV32), P(), E(OPC_GX)], None),
                                   (80, (TPS["id"], TPS["nodes"][2]), [P(), E(PS22)], None),
                                   (25, (TA1["id"], TA1["nodes"][2]), [P((189, 52)), I(HV29), P((201, 52)), E(TA2, 2)], None),
                                   (25, (TB1["id"], TB1["nodes"][2]), [P((339, 52)), I(HV30), P((351, 52)), E(TB2, 2)], None)],
       (258, 43))
UV03 = valve("UV4103", "GlobeValve", 135, 80, 180, 150, "UV-4103", act=90, lab=(4, -3, "LeftCenter"))
system("GOX-4003", 150, "Oxygen", [(None, (TRY["id"], TRY["nodes"][2]), [P((155, 80)), I(UV03), P((65, 80))],
                                    (TRC["id"], TRC["nodes"][2]))], (70, 78))
system("VNT-4006", 25, "Oxygen", [(None, (TBL["id"], TBL["nodes"][2]), [P(), I(XV33), P(), E(OPC_B1)], None)],
       (346, 63, "v"))
# blowdown XV-4116 and PSV-4122 into VNT-4002, silencer S-4101, separate from the tank vent (D-019)
TV2 = tee("Tee_VNT4002", 180, 22, 0, 90, 150)
_tv2 = TV2["xml"](0).replace(node("Tee_VNT4002_N1", 150), node("Tee_VNT4002_N1", 80))
TV2["xml"] = lambda _d: _tv2     # PSV-4122 outlet side is DN80
XV16 = valve("XV4116", "BallValve", 180, 34, 270, 150, "XV-4116", act=0, lab=(10, -3, "LeftCenter"))
S41 = sil("S4101", 200, 22, 0, 150, "S-4101", 90, (0, -8, "CenterCenter"))
OPC_V2 = offpage("OPC_VNT4002_atm", False, 215, 14, 270, 150, "to atm. (elevated, safe location)", (219, 10, "LeftCenter"))
system("VNT-4002", 150, "Oxygen", [(None, (TBD["id"], TBD["nodes"][2]), [P(), I(XV16), P()], (TV2["id"], TV2["nodes"][2])),
                                   (None, (PS22["id"], PS22["nodes"][1]), [P((170, 33), (170, 22)), E(TV2)], None),
                                   (None, (TV2["id"], TV2["nodes"][1]), [P(), I(S41), P((215, 22)), E(OPC_V2)], None)],
       (217, 28, "v"))

# ---- GAN compressor K-4102: O2 analyzer with divert to vent, export, cold box purge take-off
TAS = tee("Tee_GAN4002_AS", 135, 115, 0, 90, 150, 100)
TAS2 = tee("Tee_GAN4001_AS", 86, 115, 0, 90, 250, 100)
OPC_N = offpage("OPC_GAN4001_in", True, 20, 115, 0, 250, "from P-03 E-3101", (16, 122, "CenterCenter"))
TDV = tee("Tee_GAN4001_D", 40, 115, 0, 270, 250, 150)
system("GAN-4001", 250, "Nitrogen", [(None, (OPC_N["id"], OPC_N["nodes"][0]), [P(), E(TDV)], None),
                                     (None, (TDV["id"], TDV["nodes"][1]), [P(), E(TAS2)], None),
                                     (None, (TAS2["id"], TAS2["nodes"][1]), [P()], N("K4102", "N1"))], (56, 123))
XV05 = valve("XV3105", "BallValve", 40, 103, 270, 150, "XV-3105", act=180)
OPC_DV = offpage("OPC_VNT4004_atm", False, 40, 92, 270, 150, "to atm. (elevated)", (44, 84, "LeftCenter"))
system("VNT-4004", 150, "Nitrogen", [(None, (TDV["id"], TDV["nodes"][2]), [P(), I(XV05), P(), E(OPC_DV)], None)],
       (46, 90, "v"))
CV2 = valve("CV_GAN4002", "SwingCheckValve", 140, 115, 0, 150)
FV05 = valve("FV4105", "GlobeValve", 162, 115, 0, 150, "FV-4105", act=270)
TUN = tee("Tee_GAN4002_UN", 176, 115, 0, 270, 150, 50)
TBK2 = tee("Tee_GAN4002_BK", 192, 115, 0, 90, 150, 100)
XV20 = valve("XV4120", "BallValve", 202, 115, 0, 150, "XV-4120", act=270, lab=(0, -10.5, "CenterCenter"))
TBN = tee("Tee_GAN4002_BL", 208, 115, 0, 90, 150, 25)
XV34 = valve("XV4134", "BallValve", 214, 115, 0, 150, "XV-4134", act=270, lab=(0, -10.5, "CenterCenter"))
XV35 = valve("XV4135", "BallValve", 208, 123, 90, 25, "XV-4135", act=0, lab=(-3, 0, "RightCenter"))
OPC_B2 = offpage("OPC_VNT4007_atm", False, 208, 132, 90, 25, "to atm.", (212, 136, "LeftCenter"))
OPC_NX = offpage("OPC_GAN4002_BL", False, 222, 115, 0, 150, "to GAN pipeline, 8 barg (BL)", (232, 115, "LeftCenter"))
system("GAN-4002", 150, "Nitrogen", [(None, N("K4102", "N2"), [P()], N("E4103", "N1")),
                                     (None, N("E4103", "N2"), [P(), E(TAS)], None),
                                     (None, (TAS["id"], TAS["nodes"][1]), [P(), I(CV2), P(), I(FV05), P(), E(TUN)], None),
                                     (None, (TUN["id"], TUN["nodes"][1]), [P(), E(TBK2)], None),
                                     (None, (TBK2["id"], TBK2["nodes"][1]), [P(), I(XV20), P(), E(TBN)], None),
                                     (None, (TBN["id"], TBN["nodes"][1]), [P(), I(XV34), P(), E(OPC_NX)], None)],
       (140, 123))
OPC_UN = offpage("OPC_UN3001_out", False, 176, 102, 270, 50, "to P-03 PV-3113 (casing purge)", (180, 98, "LeftCenter"))
system("UN-3001", 50, "Nitrogen", [(None, (TUN["id"], TUN["nodes"][2]), [P(), E(OPC_UN)], None)], (178, 108, "v"))

system("VNT-4007", 25, "Nitrogen", [(None, (TBN["id"], TBN["nodes"][2]), [P(), I(XV35), P(), E(OPC_B2)], None)],
       (196, 131, "v"))
# K-4102 anti-surge: cooled discharge (E-4103 outlet, upstream of the check valve) back to the suction, UV fails open
UV31 = valve("UV4131", "GlobeValve", 115, 143, 180, 100, "UV-4131", act=270)
system("GAN-4004", 100, "Nitrogen", [(None, (TAS["id"], TAS["nodes"][2]), [P((135, 143)), I(UV31), P((86, 143))],
                                      (TAS2["id"], TAS2["nodes"][2]))], (88, 141))

# ---- storage, backup pumps and vaporizers: LIN (left, into GAN-4002), LOX (right, into GOX-4002)
for (tk, liq, inl, inl_note, vent, vnt_fl, vnt_note, tpsv, ptag, pre, vpre, _liq, gas, psvp, psvv, pv, pvx, act,
     ptop, gx, pcv, xo, mf, tsv, vb) in [
        ("T4102", "LIN", "LIN-3001", "from P-03 LN-3001 (subcooled)", "VNT-4005", "Nitrogen", "to atm. (elevated)",
         "4124", "4110", "4102", "4106", "LIN", "GAN-4003", "4126", "4128", "4112", 192, 0, "T-4102", 0, "4112", "4137", "4139", "4141", "4143"),
        ("T4101", "LOX", "LOX-3001", "from P-03 FV-3111 (LOX + HC purge)", "VNT-4001", "Oxygen",
         "to atm. (safe location)", "4123", "4109", "4101", "4105", "LOX", "GOX-4004", "4125", "4127", "4111", 400, 180,
         "T-4101", 200, "4111", "4136", "4138", "4140", "4142")]:
    x = 50 + gx                           # tank centre
    fluid = "Liquid nitrogen" if liq == "LIN" else "Liquid oxygen"
    o = offpage("OPC_%s_in" % inl.replace("-", ""), True, x + 40, 150, 180, 40, inl_note, (x + 44, 156, "LeftCenter"))
    # tank inlet block valve and TSV on the transfer line from P-03 (trapped liquid, D-011)
    tt = tee("Tee_%s_TSV" % inl.replace("-", ""), x + 24, 150, 180, 270, 40, 25)
    hvi = valve("HV_%s_in" % tk, "BallValve", x + 17, 150, 180, 40)
    tsvv = psv("TSV" + tsv, x + 24, 144, 25, "TSV-" + tsv)
    ot = offpage("OPC_TSV%s_atm" % tsv, False, x + 30, 138, 270, 25, "to atm.", (x + 30, 131, "CenterCenter"))
    system(inl, 40, fluid, [(None, (o["id"], o["nodes"][0]), [P(), E(tt)], None),
                            (None, (tt["id"], tt["nodes"][1]), [P(), I(hvi), P((x + 10, 150))], N(tk, "N1")),
                            (25, (tt["id"], tt["nodes"][2]), [P(), E(tsvv)], None),
                            (25, (tsvv["id"], tsvv["nodes"][1]), [P((x + 30, 144)), E(ot)], None)], (x + 12, 158))
    pvv = valve("PV" + ptag, "GlobeValve", x - 2, 155, 270, 100, "PV-" + ptag, act=180, lab=(-9, 4, "RightCenter"))
    tvb = tee("Tee_%s_VB" % vent.replace("-", ""), x - 2, 160.5, 270, 0, 100, 50)
    vbv = psv("PSV" + vb, x + 3, 157, 50, "PSV-" + vb, lab=(1, -4.5, "CenterCenter"))     # vacuum breaker
    ov = offpage("OPC_%s_atm" % vent.replace("-", ""), False, x - 2, 140, 270, 100, vnt_note, (x + 2, 136, "LeftCenter"))
    ps = psv("PSV" + tpsv, x + 22, 173, 80, "PSV-" + tpsv, lab=(2, 4, "LeftCenter"))
    op = offpage("OPC_PSV%s_atm" % tpsv, False, x + 28, 165, 270, 80, "to atm.", (x + 31, 161, "LeftCenter"))
    system(vent, 100, "Oxygen" if liq == "LOX" else vnt_fl,
           [(None, N(tk, "N2"), [P(), E(tvb)], None),
            (None, (tvb["id"], tvb["nodes"][1]), [P(), I(pvv), P(), E(ov)], None),
            (50, (tvb["id"], tvb["nodes"][2]), [P((x + 3, 160.5)), E(vbv)], None),
            (80, N(tk, "N3"), [P(), E(ps)], None),
            (80, (ps["id"], ps["nodes"][1]), [P((x + 28, 173)), E(op)], None)], (x, 145))
    # pumps A/B with check valves, pump discharge PSV (back to the tank), vaporizers A/B, outlet PSV, riser
    p0 = x + 45
    ts = tee("Tee_%s4001" % liq, p0 - 17, 233, 0, 90, 80)
    xvo = valve("XV" + xo, "BallValve", x + 18, 233, 0, 80, "XV-" + xo, act=270, lab=(0, 5, "CenterCenter"))
    hsa = valve("HV_P%sA_S" % pre, "BallValve", p0 - 12, 233, 0, 80)
    hsb = valve("HV_P%sB_S" % pre, "BallValve", p0 - 12, 251, 0, 80)
    system("%s-4001" % liq, 80, fluid, [(None, N(tk, "N4"), [P((x + 8, 233)), I(xvo), P(), E(ts)], None),
                                         (None, (ts["id"], ts["nodes"][1]), [P(), I(hsa), P()], N("P%sA" % pre, "N1")),
                                         (None, (ts["id"], ts["nodes"][2]), [P((p0 - 17, 251)), I(hsb), P()],
                                          N("P%sB" % pre, "N1"))],
           (x + 3, 246))
    hda = valve("HV_P%sA_D" % pre, "BallValve", p0 + 11, 233, 0, 50)
    hdb = valve("HV_P%sB_D" % pre, "BallValve", p0 + 11, 251, 0, 50)
    cva = valve("CV_P%sA" % pre, "SwingCheckValve", p0 + 16, 233, 0, 50)
    cvb = valve("CV_P%sB" % pre, "SwingCheckValve", p0 + 16, 251, 0, 50)
    tmf = tee("Tee_%s4002_MF" % liq, p0 + 25, 233, 0, 270, 50, 25)
    trj = tee("Tee_%s4003_J" % liq, p0 + 25, 185, 180, 90, 25)
    hmf = valve("HV" + mf, "GlobeValve", p0 + 25, 205, 270, 25, "HV-" + mf, lab=(-3, 0, "RightCenter"))
    td = tee("Tee_%s4002_D" % liq, p0 + 21, 233, 0, 90, 50)
    tp = tee("Tee_%s4002_PSV" % liq, p0 + 29, 233, 0, 270, 50, 25)
    tv = tee("Tee_%s4002_V" % liq, p0 + 39, 233, 0, 90, 50)
    hva = valve("HV_E%sA" % vpre, "BallValve", p0 + 45, 233, 0, 50)
    hvb = valve("HV_E%sB" % vpre, "BallValve", p0 + 45, 251, 0, 50)
    pp = psv("PSV" + psvp, p0 + 29, 226, 25, "PSV-" + psvp, lab=(6, 2, "LeftCenter"))
    system("%s-4002" % liq, 50, fluid,
           [(None, N("P%sA" % pre, "N2"), [P(), I(hda), P(), I(cva), P(), E(td)], None),
            (None, N("P%sB" % pre, "N2"), [P(), I(hdb), P(), I(cvb), P((p0 + 21, 251)), E(td, 2)], None),
            (None, (td["id"], td["nodes"][1]), [P(), E(tmf)], None),
            (None, (tmf["id"], tmf["nodes"][1]), [P(), E(tp)], None),
            (None, (tp["id"], tp["nodes"][1]), [P(), E(tv)], None),
            (None, (tv["id"], tv["nodes"][1]), [P(), I(hva), P()], N("E%sA" % vpre, "N1")),
            (None, (tv["id"], tv["nodes"][2]), [P((p0 + 39, 251)), I(hvb), P()], N("E%sB" % vpre, "N1")),
            (25, (tp["id"], tp["nodes"][2]), [P(), E(pp)], None)], (p0 + 23, 243, "v"))
    # pump cool-down / min-flow return to the tank vapour space; the discharge header PSV relieves into it
    system("%s-4003" % liq, 25, fluid,
           [(None, (pp["id"], pp["nodes"][1]), [P((p0 + 33, 226), (p0 + 33, 185)), E(trj)], None),
            (None, (trj["id"], trj["nodes"][1]), [P()], N(tk, "N5")),
            (None, (tmf["id"], tmf["nodes"][2]), [P(), I(hmf), P(), E(trj, 2)], None)], (p0 + 35, 200, "v"))
    v0 = p0 + 57                          # vaporizer centre
    tm = tee("Tee_%s_M" % gas.replace("-", ""), v0 + 16, 233, 0, 90, 100)
    tq = tee("Tee_%s_PSV" % gas.replace("-", ""), v0 + 26, 233, 0, 270, 100, 25)
    pq = psv("PSV" + psvv, v0 + 26, 226, 25, "PSV-" + psvv)
    oq = offpage("OPC_PSV%s_atm" % psvv, False, v0 + 32, 218, 270, 25, "to atm.",
                 (v0 + 32, 207, "CenterCenter") if liq == "LIN" else (v0 + 36, 214, "LeftCenter"))
    pvb = valve("PV" + pv, "GlobeValve", pvx, 175, 270, 100, "PV-" + pv, act=act,
                lab=(-3, 0, "RightCenter") if act == 0 else (3, 0, "LeftCenter"))
    riser = [P((pvx, 233)), I(pvb), P()] if liq == "LIN" else [P((pvx, 233)), I(pvb), P((pvx, 30), (300, 30))]
    join = (TBK2["id"], TBK2["nodes"][2]) if liq == "LIN" else (TBK["id"], TBK["nodes"][2])
    system(gas, 100, "Nitrogen" if liq == "LIN" else "Oxygen",
           [(None, N("E%sA" % vpre, "N2"), [P(), E(tm)], None),
            (None, N("E%sB" % vpre, "N2"), [P((v0 + 16, 251)), E(tm, 2)], None),
            (None, (tm["id"], tm["nodes"][1]), [P(), E(tq)], None),
            (None, (tq["id"], tq["nodes"][1]), riser, join),
            (25, (tq["id"], tq["nodes"][2]), [P(), E(pq)], None),
            (25, (pq["id"], pq["nodes"][1]), [P((v0 + 32, 226)), E(oq)], None)],
           (194, 140, "v") if liq == "LIN" else (350, 28))

# ---- instruments
instrument("AI-3104", 28, 58, "Line_GOX4001_S1", "Line_GOX4001_S1_P1_I1", tgt="top")
instrument("PIC-4101", 88, 30, "Line_GOX4001_S3", "Line_GOX4001_S3_P2_I1",
           signal=[(81.25, 30), (52, 30), (52, 36), TOPS["PV4101B"]])
extra_signal("PIC-4101", [(94.75, 30), (101, 30), (101, 40.6)])          # K-4101 inlet guide vanes
instrument("TSHH-4104", 110, 22, "K4101_I1", "K4101_I1_Pos")
instrument("UIC-4103", 122, 97, "K4101_I2", "K4101_I2_Pos", tgt="top", signal=[(128.75, 97), (135, 97), TOPS["UV4103"]])
instrument("UIC-4131", 100, 133, "K4102_I1", "K4102_I1_Pos", tgt="top", signal=[(106.75, 133), (115, 133), TOPS["UV4131"]])
note("TSHH-4104", 118, 22, "trips K-4101, ESD + blowdown")
instrument("PIC-4102", 240, 31, "Line_GOX4002_S7", "Line_GOX4002_S7_P2_I1")
note("PIC-4102", 248, 31, "K-4101 load (with PIC-4101); HH trips K-4101")
instrument("AI-4115", 318, 59, "Line_GOX4002_S8", "Line_GOX4002_S8_P1_I1", tgt="top")
instrument("AIA-3105", 26, 101, "Line_GAN4001_S1", "Line_GAN4001_S1_P1_I1",
           signal=[(32.75, 101), (32.8, 101), TOPS["XV3105"]])
instrument("FIC-3107", 60, 101, "Line_GAN4001_S2", "Line_GAN4001_S2_P1_I1",
           signal=[(60, 97.25), (60, 94), (91, 94), (91, 105.6)])
instrument("PIC-4106", 78, 101, "Line_GAN4001_S2", "Line_GAN4001_S2_P1_I2")
instrument("FIC-4105", 150, 101, "Line_GAN4002_S3", "Line_GAN4002_S3_P2_I1",
           signal=[(156.75, 101), (162, 101), TOPS["FV4105"]])
for tk, x, pica, lia, pv in [("T4102", 50, "PICA-4110", "LIA-4108", "PV4110"), ("T4101", 250, "PICA-4109", "LIA-4107",
                                                                                 "PV4109")]:
    instrument(pica, x - 28, 180, tk + "_I1", tk + "_I1_Pos", tgt="right",
               signal=[(x - 28, 176.25), (x - 28, 155), TOPS[pv]])
    instrument(lia, x - 28, 200, tk + "_I2", tk + "_I2_Pos", tgt="right")
instrument("AIA-4121", 222, 220, "T4101_I3", "T4101_I3_Pos", tgt="right")
instrument("TSLL-4114", 206, 195, "Line_GAN4003_S4", "Line_GAN4003_S4_P1_I1", tgt="left")
note("TSLL-4114", 195, 188, "LL: stops P-4102A/B, closes PV-4112")
instrument("PIC-4112", 210, 160, "Line_GAN4003_S4", "Line_GAN4003_S4_P2_I1", tgt="left",
           signal=[(210, 163.75), (210, 175), TOPS["PV4112"]])
instrument("TSLL-4113", 386, 200, "Line_GOX4004_S4", "Line_GOX4004_S4_P1_I1", tgt="right")
note("TSLL-4113", 397, 207, "LL: stops P-4101A/B, closes PV-4111", "RightCenter")
instrument("PIC-4111", 382, 160, "Line_GOX4004_S4", "Line_GOX4004_S4_P2_I1", tgt="right",
           signal=[(382, 163.75), (382, 175), TOPS["PV4111"]])

path = sys.argv[1]
doc = open(path, encoding="utf-8").read()
conc = ('<Components property="TaggedPlantItems">%s</Components><Components property="PipingNetworkSystems">%s'
        '</Components><Components property="ProcessInstrumentationFunctions">%s</Components>'
        % ("".join(CON), "".join(SYS), "".join(INS)))
a = '<Components property="MetaData">'
assert doc.count(a) == 1 and "TaggedPlantItems" not in doc, "run on the empty sheet only"
doc = doc.replace(a, conc + a, 1)
i = doc.index('<Object id="PlantModel1_Drawing1" type="Core/Diagram.Diagram">')
j = doc.index('<Components property="Groups">', i) + len('<Components property="Groups">')
doc = doc[:j] + "".join(DRW) + doc[j:]
k = doc.index('<Components property="Shapes">') + len('<Components property="Shapes">')
doc = doc[:k] + "".join(SHP) + doc[k:]
open(path, "w", encoding="utf-8").write(doc)
print("equipment %d, lines %d, instruments %d" % (len(CON), len(SYS), len(INS)))
