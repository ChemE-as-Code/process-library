"""Throwaway generator for pid/P-02.xml (front-end purification), stage S2.

Reuses the helper functions of scripts/draft_P-01.py (everything above its "# Equipment" marker).
After the first run the XML is the source of truth (AGENTS.md).
Usage: python3 scripts/draft_P-02.py pid/P-02.xml && plantcode fmt pid/P-02.xml
"""
import os
import sys

_src = open(os.path.join(os.path.dirname(__file__), "draft_P-01.py"), encoding="utf-8").read()
exec(_src[:_src.index("# Equipment\n")])          # noqa: S102 - helpers only

def N(eid, suf):
    return ("%s_%s" % (eid, suf), "%s_%s_Node" % (eid, suf))


P = lambda *b: ("pipe", list(b))     # noqa: E731
I = lambda o: ("item", o)            # noqa: E731
E = lambda o, k=0: ("end", o, k)     # noqa: E731

column_shape("ShapeASU_V2101", 15, 35, [(-25, 25)])
TOP, BOT = 109.3, 175.0
for eid, tag, x, air_in, air_out, rg_in, rg_out in [("V2101A", "V-2101A", 110, 100, 100, 120, 120),
                                                     ("V2101B", "V-2101B", 190, 200, 200, 180, 180)]:
    equipment(eid, "PressureVessel", tag, "ShapeASU_V2101", x, 140,
              [("N1", "N1", air_in, BOT, 600), ("N2", "N2", air_out, TOP, 500), ("N3", "N3", rg_in, TOP, 600),
               ("N4", "N4", rg_out, BOT, 600)], (x - 27 if x < 150 else x + 27, 140), inst=[("I1", x + 15, 150)])
equipment("E2101", "ElectricHeater", "E-2101", "ShapeASU_Cooler", 150, 40,
          [("N1", "N1", 144, 40, 500), ("N2", "N2", 150, 46, 600)], (162, 36), inst=[("I1", 156, 40)])
equipment("F2101", "GasFilter", "F-2101", "ShapeASU_Filter", 265, 60,
          [("N1", "N1", 260, 60, 500), ("N2", "N2", 270, 60, 500)], (265, 74), inst=[("I1", 265, 52)])

PIPE_INST[("AIR-2001", 3, 1)] = [("I1", 225, 60), ("I2", 240, 60)]
PIPE_INST[("RG-2002", 1, 1)] = [("I1", 150, 55)]
PIPE_INST[("RG-2001", 1, 1)] = [("I1", 60, 30)]


def xv(vid, x, y, rot, d, tag):
    return valve(vid, "BallValve", x, y, rot, d, tag, act=0 if x < 150 else 180)


# ---- air from the DCAC to the adsorbers (line AIR-1004 continues from P-01)
OPC_AIR = offpage("OPC_AIR1004_in", True, 20, 215, 0, 600, "from P-01 C-1101", (22, 210, "CenterCenter"))
TA = tee("Tee_AIR1004_A", 100, 215, 0, 270, 600)
XA1, XB1 = xv("XV2101A", 100, 195, 270, 600, "XV-2101A"), xv("XV2101B", 200, 195, 270, 600, "XV-2101B")
system("AIR-1004", 600, "Air",
       [(None, (OPC_AIR["id"], OPC_AIR["nodes"][0]), [P(), E(TA)], None),
        (None, (TA["id"], TA["nodes"][2]), [P(), I(XA1), P()], N("V2101A", "N1")),
        (None, (TA["id"], TA["nodes"][1]), [P((200, 215)), I(XB1), P()], N("V2101B", "N1"))], (40, 219))
# ---- dry air out, header, dust filter
TO = tee("Tee_AIR2001_O", 200, 60, 0, 90, 500)
XA2, XB2 = xv("XV2102A", 100, 90, 270, 500, "XV-2102A"), xv("XV2102B", 200, 90, 270, 500, "XV-2102B")
system("AIR-2001", 500, "Dry air",
       [(None, N("V2101A", "N2"), [P(), I(XA2), P((100, 60)), E(TO)], None),
        (None, N("V2101B", "N2"), [P(), I(XB2), P(), E(TO, 2)], None),
        (None, (TO["id"], TO["nodes"][1]), [P()], N("F2101", "N1"))], (206, 56))
OPC_DA = offpage("OPC_AIR2002", False, 385, 60, 0, 500, "to P-03 E-3101 / K-3101", (390, 55, "CenterCenter"))
system("AIR-2002", 500, "Dry air", [(None, N("F2101", "N2"), [P(), E(OPC_DA)], None)], (300, 56))
# ---- regeneration gas: waste N2 in, heater, to the bed in regeneration, out via silencer
OPC_RG = offpage("OPC_RG2001", True, 20, 30, 0, 500, "from P-03 WN-3002", (22, 25, "CenterCenter"))
FV5 = valve("FV2105", "GlobeValve", 80, 30, 0, 500, "FV-2105", act=270)
system("RG-2001", 500, "Waste nitrogen",
       [(None, (OPC_RG["id"], OPC_RG["nodes"][0]), [P(), I(FV5), P((144, 30))], N("E2101", "N1"))], (40, 37))
TR = tee("Tee_RG2002", 150, 80, 90, 180, 600)
XA3, XB3 = xv("XV2103A", 120, 95, 90, 600, "XV-2103A"), xv("XV2103B", 180, 95, 90, 600, "XV-2103B")
system("RG-2002", 600, "Waste nitrogen",
       [(None, N("E2101", "N2"), [P(), E(TR)], None),
        (None, (TR["id"], TR["nodes"][2]), [P((120, 80)), I(XA3), P()], N("V2101A", "N3")),
        (None, (TR["id"], TR["nodes"][1]), [P((150, 86), (180, 86)), I(XB3), P()], N("V2101B", "N3"))], (153, 76))
TG = tee("Tee_RG2003", 150, 195, 270, 0, 600)
XA4, XB4 = xv("XV2104A", 120, 185, 90, 600, "XV-2104A"), xv("XV2104B", 180, 185, 90, 600, "XV-2104B")
SIL = valve("S2101", "Silencer", 150, 160, 270, 600, "S-2101", shape_id="ShapeASU_Silencer", sc=1.0, half=6.0, srot=0)
system("RG-2003", 600, "Waste nitrogen",
       [(None, N("V2101A", "N4"), [P(), I(XA4), P((120, 200), (150, 200)), E(TG)], None),
        (None, N("V2101B", "N4"), [P(), I(XB4), P((180, 195)), E(TG, 2)], None),
        (None, (TG["id"], TG["nodes"][1]), [P(), E(SIL)], None)], (153, 205))

# ---- instruments
instrument("KS-2101", 150, 120, "V2101A_I1", "V2101A_I1_Pos", tgt="left")
instrument("AIA-2102", 225, 40, "Line_AIR2001_S3", "Line_AIR2001_S3_P1_I1")
instrument("AIA-2103", 240, 80, "Line_AIR2001_S3", "Line_AIR2001_S3_P1_I2", tgt="top")
instrument("TIC-2104", 128, 50, "Line_RG2002_S1", "Line_RG2002_S1_P1_I1", tgt="right",
           signal=[(128, 46.25), (128, 44), (145, 44)])
instrument("FIC-2105", 60, 15, "Line_RG2001_S1", "Line_RG2001_S1_P1_I1", signal=[(66.75, 15), (80, 15), TOPS["FV2105"]])
instrument("PDIA-2106", 280, 40, "F2101_I1", "F2101_I1_Pos", tgt="left")
instrument("TSHH-2107", 175, 22, "E2101_I1", "E2101_I1_Pos", tgt="left")

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
