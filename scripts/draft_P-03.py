"""Throwaway generator for pid/P-03.xml (cold box), stage S3.

Reuses the helper functions of scripts/draft_P-01.py (everything above its "# Equipment" marker).
After the first run the XML is the source of truth (AGENTS.md).
Usage: python3 scripts/draft_P-03.py pid/P-03.xml && cheme fmt pid/P-03.xml
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


def rect_shape(sid, name, hw, hh, hatch=True):
    prims = [polyline(sid + "_P1", [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)], 0.35, EQ, closed=True)]
    if hatch:
        prims.append(polyline(sid + "_P2", [(-hw, -hh), (hw, hh)], 0.2, EQ, "Dash"))
    shape(sid, name, prims)


rect_shape("ShapeASU_E3101", "PLATE_FIN_EXCHANGER_SHAPE_MHE", 15, 65)
rect_shape("ShapeASU_E3102", "PLATE_FIN_EXCHANGER_SHAPE_SC", 10, 26)
rect_shape("ShapeASU_E3103", "CONDENSER_REBOILER_SHAPE", 8, 4)
shape("ShapeASU_Turbine", "EXPANSION_TURBINE_SHAPE",
      [polyline("ShapeASU_Turbine_P1", [(-12, -5), (12, -10), (12, 10), (-12, 5)], 0.35, EQ, closed=True)])
column_shape("ShapeASU_C3102", 12, 51, [(-35, -10), (0, 25)])
column_shape("ShapeASU_C3101", 12, 30, [(-15, 15)])
column_shape("ShapeASU_V3101", 8, 8, [])

# ---- equipment
equipment("E3101", "PlateHeatExchanger", "E-3101", "ShapeASU_E3101", 120, 135,
          [("N1", "N1", 108, 70, 200), ("N2", "N2", 114, 70, 500), ("N3", "N3", 120, 70, 900),
           ("N4", "N4", 126, 70, 250), ("N5", "N5", 132, 70, 500),
           ("N6", "N6", 108, 200, 800), ("N7", "N7", 114, 200, 500), ("N8", "N8", 120, 200, 250),
           ("N9", "N9", 126, 200, 500), ("N10", "N10", 135, 115, 150)], (127, 100))
equipment("E3102", "PlateHeatExchanger", "E-3102", "ShapeASU_E3102", 354, 144,
          [("N1", "N1", 348, 170, 100), ("N2", "N2", 348, 118, 100), ("N3", "N3", 354, 170, 100),
           ("N4", "N4", 354, 118, 100), ("N5", "N5", 360, 118, 800), ("N6", "N6", 360, 170, 800)], (376, 160))
equipment("C3102", "ProcessColumn", "C-3102", "ShapeASU_C3102", 300, 109,
          [("N1", "N1", 300, 58, 800), ("N2", "N2", 288, 75, 150), ("N3", "N3", 288, 95, 350),
           ("N4", "N4", 312, 76, 100), ("N5", "N5", 312, 106, 100), ("N6", "N6", 288, 140, 500),
           ("N7", "N7", 288, 155, 40)], (300, 88),
          inst=[("I1", 312, 122), ("I3", 312, 153)])
equipment("E3103", "PlateHeatExchanger", "E-3103", "ShapeASU_E3103", 300, 150,
          [("N1", "N1", 297, 154, 300), ("N2", "N2", 303, 154, 150)], (281, 147))
equipment("C3101", "ProcessColumn", "C-3101", "ShapeASU_C3101", 300, 205,
          [("N1", "N1", 288, 226, 500), ("N2", "N2", 288, 190, 250), ("N3", "N3", 297, 176.3, 300),
           ("N4", "N4", 303, 176.3, 150), ("N5", "N5", 312, 190, 100), ("N6", "N6", 300, 235, 100),
           ("N7", "N7", 309, 179, 150), ("N8", "N8", 288, 205, 50)], (300, 214),
          inst=[("I1", 312, 229), ("I2", 312, 205)])
equipment("K3101", "CentrifugalCompressor", "K-3101", "ShapeASU_Compressor", 50, 100,
          [("N1", "N1", 38, 100, 250), ("N2", "N2", 62, 100, 200)], (50, 115))
equipment("E3104", "TubularHeatExchanger", "E-3104", "ShapeASU_Cooler", 75, 125,
          [("N1", "N1", 72, 119.8, 200), ("N2", "N2", 78, 119.8, 200), ("N3", "N3", 72, 130.2, 150),
           ("N4", "N4", 78, 130.2, 150)], (90, 128))
equipment("KT3101", "Turbine", "KT-3101", "ShapeASU_Turbine", 185, 115,
          [("N1", "N1", 173, 115, 150), ("N2", "N2", 197, 115, 350)], (185, 105),
          inst=[("I1", 180, 121), ("I2", 186, 122), ("I3", 192, 123)])
equipment("V3101", "Tank", "V-3101", "ShapeASU_V3101", 235, 205,
          [("N1", "N1", 239, 197.5, 25), ("N2", "N2", 231, 197.5, 50)], (235, 219))

PIPE_INST[("WN-3001", 1, 1)] = [("I1", 330, 44)]
PIPE_INST[("AIR-3004", 1, 1)] = [("I1", 240, 95)]
PIPE_INST[("LN-3001", 3, 1)] = [("I1", 335, 76)]
PIPE_INST[("LOX-3001", 1, 1)] = [("I1", 262, 155)]
PIPE_INST[("LOX-3001", 2, 1)] = [("I1", 240, 155)]
PIPE_INST[("UN-3001", 1, 2)] = [("I1", 185, 190)]

# ---- air from P-02, booster K-3101 with aftercooler E-3104, main exchanger
OPC_AIR = offpage("OPC_AIR2002_in", True, 20, 56, 0, 500, "from P-02 F-2101", (22, 51, "LeftCenter"))
TA = tee("Tee_AIR2002_B", 32, 56, 0, 90, 500, 250)
system("AIR-2002", 500, "Dry air", [(None, (OPC_AIR["id"], OPC_AIR["nodes"][0]), [P(), E(TA)], None),
                                    (None, (TA["id"], TA["nodes"][1]), [P((114, 56))], N("E3101", "N2"))], (84, 52))
# anti-surge (D-003): recycle AIR-3006 from the E-3104 outlet to the suction, UV-3120 by UIC-3120; check valve
TR = tee("Tee_AIR3005_R", 32, 72, 90, 0, 250, 150)
PIPE_INST[("AIR-3005", 2, 1)] = [("I1", 32, 80)]
system("AIR-3005", 250, "Dry air", [(None, (TA["id"], TA["nodes"][2]), [P(), E(TR)], None),
                                    (None, (TR["id"], TR["nodes"][1]), [P((32, 100))], N("K3101", "N1"))],
       (10, 93, "v"))
# PSV-3119 on AIR-3002 at the E-3104 outlet, upstream of the check valve (S4 review)
TP19 = tee("Tee_AIR3002_PSV", 78, 92, 270, 0, 200, 80)
PSV19 = valve("PSV3119", "SpringLoadedGlobeSafetyValve", 84, 88, 270, 80, "PSV-3119", lab=(2, 4.5, "LeftCenter"))
OPC_19 = offpage("OPC_PSV3119_atm", False, 90, 82, 270, 80, "to atm.", (90, 77, "CenterCenter"))
TD = tee("Tee_AIR3002_R", 78, 72, 270, 180, 200, 150)
CK = valve("CV_AIR3002", "SwingCheckValve", 93, 62, 0, 200)
system("AIR-3002", 200, "Air", [(None, N("K3101", "N2"), [P((72, 100))], N("E3104", "N1")),
                                (None, N("E3104", "N2"), [P(), E(TP19)], None),
                                (None, (TP19["id"], TP19["nodes"][1]), [P(), E(TD)], None),
                                (None, (TD["id"], TD["nodes"][1]), [P((78, 62)), I(CK), P((108, 62))],
                                 N("E3101", "N1")),
                                (80, (TP19["id"], TP19["nodes"][2]), [P((84, 92)), E(PSV19)], None),
                                (80, (PSV19["id"], PSV19["nodes"][1]), [P((90, 88)), E(OPC_19)], None)], (80, 104, "v"))
UV20 = valve("UV3120", "GlobeValve", 62, 72, 180, 150, "UV-3120", act=270, lab=(5, 4.5, "LeftCenter"))
system("AIR-3006", 150, "Air", [(None, (TD["id"], TD["nodes"][2]), [P(), I(UV20), P(), E(TR, 2)], None)], (35, 70))
for ln, nz, x, inflow, note, rot in [("CW-3001", "N3", 72, True, "CW", 270), ("CWR-3001", "N4", 78, False, "CWR", 90)]:
    o = offpage("OPC_%s" % ln.replace("-", ""), inflow, x, 145, rot, 150, note, (x, 157, "CenterCenter"))
    system(ln, 150, "Cooling water" if inflow else "Cooling water return",
           [(None, (o["id"], o["nodes"][0]), [P()], N("E3104", nz))] if inflow else
           [(None, N("E3104", nz), [P(), E(o)], None)], (x - 16 if inflow else x + 4, 137 if inflow else 145, "v"))
# ---- warm-end products and waste N2
OPC_GAN = offpage("OPC_GAN4001", False, 265, 36, 0, 250, "to P-04 K-4102", (262, 31, "RightCenter"))
OPC_GOX = offpage("OPC_GOX4001", False, 265, 48, 0, 500, "to P-04 K-4101", (262, 43, "RightCenter"))
system("GAN-4001", 250, "Nitrogen", [(None, N("E3101", "N4"), [P((126, 36)), E(OPC_GAN)], None)], (150, 34))
system("GOX-4001", 500, "Oxygen", [(None, N("E3101", "N5"), [P((132, 48)), E(OPC_GOX)], None)], (150, 46))
T1 = tee("Tee_WN3002_RG", 395, 80, 90, 180, 900, 500)
T2 = tee("Tee_WN3002_WN", 395, 110, 90, 180, 900, 700)
_t2 = T2["xml"](0).replace(node("Tee_WN3002_WN_N2", 900), node("Tee_WN3002_WN_N2", 600))
T2["xml"] = lambda _d: _t2     # run outlet to WN-3003 is DN600
system("WN-3002", 900, "Waste nitrogen", [(None, N("E3101", "N3"), [P((120, 24), (395, 24)), E(T1)], None),
                                          (None, (T1["id"], T1["nodes"][1]), [P(), E(T2)], None)], (150, 22))
OPC_RG = offpage("OPC_RG2001_out", False, 373, 80, 180, 500, "to P-02 E-2101", (379, 86, "CenterCenter"))
system("RG-2001", 500, "Waste nitrogen", [(None, (T1["id"], T1["nodes"][2]), [P(), E(OPC_RG)], None)], (374, 76))
PVA = valve("PV3110A", "GlobeValve", 386, 110, 180, 700, "PV-3110A", act=270, lab=(0, 5, "CenterCenter"))
OPC_WN = offpage("OPC_WN1001_out", False, 371, 110, 180, 700, "to P-01 C-1102", (377, 120, "CenterCenter"))
system("WN-1001", 700, "Waste nitrogen", [(None, (T2["id"], T2["nodes"][2]), [P(), I(PVA), P(), E(OPC_WN)], None)],
       (363, 104))
PVB = valve("PV3110B", "GlobeValve", 395, 150, 90, 600, "PV-3110B", act=180, lab=(3, 0, "LeftCenter"))
S31 = valve("S3101", "Silencer", 395, 175, 90, 600, "S-3101", shape_id="ShapeASU_Silencer", sc=1.0, half=6.0, srot=0,
            lab=(-6, 0, "RightCenter"))
OPC_V = offpage("OPC_WN3003_atm", False, 395, 195, 90, 600, "to atm. (elevated)", (393, 206, "RightCenter"))
system("WN-3003", 600, "Waste nitrogen",
       [(None, (T2["id"], T2["nodes"][1]), [P(), I(PVB), P(), I(S31), P(), E(OPC_V)], None)], (397, 130, "v"))
# ---- cold end: air to the HP column, GAN, GOX, waste N2 via the subcooler
system("AIR-3001", 500, "Air", [(None, N("E3101", "N7"), [P((114, 243), (284, 243), (284, 226))], N("C3101", "N1"))],
       (150, 241))
system("GAN-3001", 250, "Nitrogen", [(None, N("C3101", "N2"), [P((277, 190), (277, 236), (120, 236))],
                                      N("E3101", "N8"))], (150, 234))
system("GOX-3001", 500, "Oxygen", [(None, N("C3102", "N6"), [P((270, 140), (270, 229), (126, 229))],
                                    N("E3101", "N9"))], (150, 227))
system("WN-3001", 800, "Waste nitrogen", [(None, N("C3102", "N1"), [P((300, 44), (360, 44))], N("E3102", "N5")),
                                          (None, N("E3102", "N6"), [P((360, 250), (108, 250))], N("E3101", "N6"))],
       (150, 255))
# ---- expander
XV17 = valve("XV3117", "BallValve", 150, 115, 0, 150, "XV-3117", act=90, lab=(0, -4, "CenterCenter"))
system("AIR-3003", 150, "Air", [(None, N("E3101", "N10"), [P(), I(XV17), P()], N("KT3101", "N1"))], (137, 124, "v"))
system("AIR-3004", 350, "Air", [(None, N("KT3101", "N2"), [P((210, 115), (210, 95))], N("C3102", "N3"))], (212, 93))
# ---- columns, condenser, reflux and rich liquid via the subcooler
system("GAN-3002", 300, "Nitrogen", [(None, N("C3101", "N3"), [P()], N("E3103", "N1"))], (275, 168, "v"))
system("LN-3002", 150, "Liquid nitrogen", [(None, N("E3103", "N2"), [P()], N("C3101", "N4"))], (305, 163, "v"))
LV1 = valve("LV3101", "GlobeValve", 338, 106, 180, 100, "LV-3101", act=90, lab=(0, -3, "CenterCenter"))
system("RL-3001", 100, "Rich liquid", [(None, N("C3101", "N6"), [P((300, 240), (348, 240))], N("E3102", "N1")),
                                       (None, N("E3102", "N2"), [P((348, 106)), I(LV1), P()], N("C3102", "N5"))],
       (314, 238))
TL = tee("Tee_LN3001_LIN", 342, 76, 180, 270, 100, 40)
FV6 = valve("FV3106", "GlobeValve", 322, 76, 180, 100, "FV-3106", act=90, lab=(0, -3, "CenterCenter"))
system("LN-3001", 100, "Liquid nitrogen", [(None, N("C3101", "N5"), [P((354, 190))], N("E3102", "N3")),
                                           (None, N("E3102", "N4"), [P((354, 76)), E(TL)], None),
                                           (None, (TL["id"], TL["nodes"][1]), [P(), I(FV6), P()], N("C3102", "N4"))],
       (322, 194))
OPC_LIN = offpage("OPC_LIN3001", False, 342, 60, 270, 40, "to P-04 T-4102", (338, 62, "RightCenter"))
system("LIN-3001", 40, "Liquid nitrogen", [(None, (TL["id"], TL["nodes"][2]), [P(), E(OPC_LIN)], None)], (344, 70, "v"))
# ---- relief
PS14 = valve("PSV3114", "SpringLoadedGlobeSafetyValve", 272, 66, 270, 150, "PSV-3114", lab=(-2, -3, "RightCenter"))
PS16 = valve("PSV3116", "SpringLoadedGlobeSafetyValve", 318, 177, 270, 150, "PSV-3116", lab=(-2, -6, "RightCenter"))
# discharges leave the cold box to an elevated safe location (D-011); LP column relief is O2-rich
OPC_P14 = offpage("OPC_VNT3002_atm", False, 262, 57, 180, 150,
                  "to atm. outside cold box (elevated, safe location)", (252, 57, "RightCenter"))
OPC_P16 = offpage("OPC_VNT3003_atm", False, 326, 171, 270, 150, "to atm.", (329, 166, "LeftCenter"))
system("VNT-3002", 150, "Waste nitrogen", [(None, N("C3102", "N2"), [P((272, 75)), E(PS14)], None),
                                           (None, (PS14["id"], PS14["nodes"][1]), [P((277, 66), (277, 57)), E(OPC_P14)],
                                            None)], (274, 79, "v"))
system("VNT-3003", 150, "Nitrogen", [(None, N("C3101", "N7"), [P(), E(PS16)], None),
                                     (None, (PS16["id"], PS16["nodes"][1]), [P((326, 177)), E(OPC_P16)], None)],
       (322, 183, "v"))
# ---- LOX product with hydrocarbon purge, drain to V-3101
TX = tee("Tee_LOX3001_D", 250, 155, 180, 90, 40, 25)
FV11 = valve("FV3111", "GlobeValve", 225, 155, 180, 40, "FV-3111", act=90, lab=(0, -3, "CenterCenter"))
OPC_LOX = offpage("OPC_LOX3001", False, 150, 155, 180, 40, "to P-04 T-4101", (155, 150, "LeftCenter"))
system("LOX-3001", 40, "Liquid oxygen", [(None, N("C3102", "N7"), [P(), E(TX)], None),
                                         (None, (TX["id"], TX["nodes"][1]), [P(), I(FV11), P(), E(OPC_LOX)], None)],
       (160, 161))
HV = valve("HV3118", "GlobeValve", 250, 170, 90, 25, "HV-3118")
system("LOX-3002", 25, "Liquid oxygen", [(None, (TX["id"], TX["nodes"][2]), [P(), I(HV), P((250, 182), (239, 182))],
                                          N("V3101", "N1"))], (252, 190, "v"))
OPC_VV = offpage("OPC_VNT3001", False, 231, 186, 270, 50, "to atmosphere (safe location)", (228, 184, "RightCenter"))
system("VNT-3001", 50, "Oxygen", [(None, N("V3101", "N2"), [P(), E(OPC_VV)], None)], (214, 193, "v"))
# ---- cold box casing purge
OPC_UN = offpage("OPC_UN3001_in", True, 150, 205, 0, 50, "from P-04 GAN-4002", (145, 199, "LeftCenter"))
PV13 = valve("PV3113", "GlobeValve", 168, 205, 0, 50, "PV-3113", act=270, lab=(0, 5, "CenterCenter"))
OPC_CB = offpage("OPC_UN3001_out", False, 200, 205, 0, 50, "to cold box casing", (196, 211, "CenterCenter"))
PIPE_INST[("UN-3001", 1, 2)] = [("I1", 185, 205)]
system("UN-3001", 50, "Nitrogen", [(None, (OPC_UN["id"], OPC_UN["nodes"][0]), [P(), I(PV13), P(), E(OPC_CB)], None)],
       (150, 214))
# cold box casing breather with O2 analyzer on its exhaust (O2 review F7)
OPC_BI = offpage("OPC_VNT3004_in", True, 140, 186, 0, 50, "from cold box casing (breather)", (136, 192, "LeftCenter"))
PSV23 = valve("PSV3123", "SpringLoadedGlobeSafetyValve", 175, 184, 270, 50, "PSV-3123", lab=(-2, 4, "RightCenter"))
OPC_BO = offpage("OPC_VNT3004_atm", False, 182, 178, 270, 50, "to atm.", (186, 175, "LeftCenter"))
PIPE_INST[("VNT-3004", 1, 1)] = [("I1", 158, 186)]
system("VNT-3004", 50, "Nitrogen", [(None, (OPC_BI["id"], OPC_BI["nodes"][0]), [P(), E(PSV23)], None),
                                    (None, (PSV23["id"], PSV23["nodes"][1]), [P((182, 184)), E(OPC_BO)], None)], (142, 184))

# ---- instruments
instrument("LIC-3101", 330, 229, "C3101_I1", "C3101_I1_Pos", tgt="left",
           signal=[(336.75, 229), (342, 229), (342, 116), (338, 116), TOPS["LV3101"]])
instrument("PI-3121", 326, 205, "C3101_I2", "C3101_I2_Pos", tgt="left")
instrument("PDI-3112", 326, 122, "C3102_I1", "C3102_I1_Pos", tgt="left")
instrument("AIA-3103", 262, 145, "Line_LOX3001_S1", "Line_LOX3001_S1_P1_I1")
instrument("LICA-3102", 326, 151, "C3102_I3", "C3102_I3_Pos", tgt="left")
instrument("FIC-3106", 335, 90, "Line_LN3001_S3", "Line_LN3001_S3_P1_I1", tgt="top",
           signal=[(328.25, 90), (322, 90), TOPS["FV3106"]])
instrument("PIC-3110", 330, 34, "Line_WN3001_S1", "Line_WN3001_S1_P1_I1",
           signal=[(336.75, 34), (386, 34), (386, 102.8), (386, 150), TOPS["PV3110B"]])
instrument("TIC-3109", 240, 82, "Line_AIR3004_S1", "Line_AIR3004_S1_P1_I1")
instrument("SSHH-3108", 165, 138, "KT3101_I1", "KT3101_I1_Pos", tgt="top",
           signal=[(158.25, 138), (150, 138), TOPS["XV3117"]])
instrument("SIC-3108", 190, 138, "KT3101_I2", "KT3101_I2_Pos", tgt="top")
instrument("PDSLL-3115", 215, 138, "KT3101_I3", "KT3101_I3_Pos", tgt="top")
instrument("FIC-3111", 205, 170, "Line_LOX3001_S2", "Line_LOX3001_S2_P1_I1", tgt="right",
           signal=[(205, 166.25), (205, 163), TOPS["FV3111"]])
instrument("UIC-3120", 18, 80, "Line_AIR3005_S2", "Line_AIR3005_S2_P1_I1", tgt="right",
           signal=[(18, 76.25), (18, 62), (62, 62), TOPS["UV3120"]])
instrument("AIA-3122", 158, 175, "Line_VNT3004_S1", "Line_VNT3004_S1_P1_I1")
instrument("PIC-3113", 185, 225, "Line_UN3001_S1", "Line_UN3001_S1_P2_I1", tgt="top",
           signal=[(178.25, 225), (168, 225), (168, 220), (160, 220), (160, 197.8), TOPS["PV3113"]])

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
