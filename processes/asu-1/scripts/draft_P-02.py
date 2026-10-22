"""Throwaway generator for pid/P-02.xml (front-end purification), stage S2.

Reuses the helper functions of scripts/draft_P-01.py (everything above its "# Equipment" marker).
After the first run the XML is the source of truth (AGENTS.md).
Usage: python3 scripts/draft_P-02.py pid/P-02.xml && cheme fmt pid/P-02.xml
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

column_shape("ShapeASU_V2101", 15, 35, [(-25, 25)])
TOP, BOT = 109.3, 175.0
# Layout (D-022): the product header (top) and the regeneration outlet header (bottom) run outside the
# two beds; the regeneration inlet with E-2101 and the feed-air inlet sit between the beds, so no line crosses.
for eid, tag, x, out, inn, lx in [("V2101A", "V-2101A", 90, 80, 100, 63), ("V2101B", "V-2101B", 230, 240, 220, 257)]:
    equipment(eid, "PressureVessel", tag, "ShapeASU_V2101", x, 140,
              [("N1", "N1", inn, BOT, 600), ("N2", "N2", out, TOP, 500), ("N3", "N3", inn, TOP, 600),
               ("N4", "N4", out, BOT, 600), ("N5", "N5", x, 105, 150)], (lx, 140),
              inst=[("I1", x + 15, 150), ("I2", x + 15, 128)] if x > 150 else [("I2", x - 15, 155)])
equipment("E2101", "ElectricHeater", "E-2101", "ShapeASU_Cooler", 160, 108,
          [("N1", "N1", 160, 114, 500), ("N2", "N2", 160, 102, 600)], (176, 106), inst=[("I1", 166, 110)])
equipment("F2101", "GasFilter", "F-2101", "ShapeASU_Filter", 300, 55,
          [("N1", "N1", 295, 55, 500), ("N2", "N2", 305, 55, 500)], (300, 69), inst=[("I1", 300, 47)])

PIPE_INST[("AIR-2001", 1, 1)] = [("I1", 80, 100)]
PIPE_INST[("AIR-2001", 2, 1)] = [("I1", 240, 100)]
PIPE_INST[("AIR-2001", 3, 1)] = [("I1", 260, 55), ("I2", 275, 55)]
PIPE_INST[("RG-2001", 1, 1)] = [("I1", 120, 140)]
PIPE_INST[("RG-2002", 2, 1)] = [("I1", 160, 87), ("I2", 160, 84)]
PIPE_INST[("RG-2003", 1, 1)] = [("I1", 80, 180)]
PIPE_INST[("RG-2003", 5, 1)] = [("I1", 240, 180)]


def xv(vid, x, y, rot, d, tag, act, lab=None, cls="BallValve"):
    return valve(vid, cls, x, y, rot, d, tag, act=act, lab=lab)


# ---- dry air out (outer top nozzles), header, dust filter; PSV-2108A/B on the bed tops
TO = tee("Tee_AIR2001_O", 240, 55, 0, 90, 500)
XA2 = xv("XV2102A", 80, 85, 270, 500, "XV-2102A", 180, (3, 0, "LeftCenter"))
XB2 = xv("XV2102B", 240, 85, 270, 500, "XV-2102B", 0, (-3, 0, "RightCenter"))
PSA = valve("PSV2108A", "SpringLoadedGlobeSafetyValve", 90, 70, 270, 150, "PSV-2108A", lab=(3, -3, "LeftCenter"))
PSB = valve("PSV2108B", "SpringLoadedGlobeSafetyValve", 230, 70, 270, 150, "PSV-2108B", lab=(-2, -3, "RightCenter"))
system("AIR-2001", 500, "Dry air",
       [(None, N("V2101A", "N2"), [P(), I(XA2), P((80, 55)), E(TO)], None),
        (None, N("V2101B", "N2"), [P(), I(XB2), P(), E(TO, 2)], None),
        (None, (TO["id"], TO["nodes"][1]), [P()], N("F2101", "N1")),
        (150, N("V2101A", "N5"), [P(), E(PSA)], None),
        (150, N("V2101B", "N5"), [P(), E(PSB)], None)], (150, 51))
OPC_DA = offpage("OPC_AIR2002", False, 390, 55, 0, 500, "to P-03 E-3101 / K-3101", (390, 50, "CenterCenter"))
system("AIR-2002", 500, "Dry air", [(None, N("F2101", "N2"), [P(), E(OPC_DA)], None)], (330, 51))
# ---- regeneration gas from P-03, FV-2105, E-2101 with bypass XV-2109 (cooling step), to the bed tops
OPC_RG = offpage("OPC_RG2001", True, 112, 140, 0, 500, "from P-03 WN-3002 (RG-2001)", (108, 134, "LeftCenter"))
FV5 = valve("FV2105", "GlobeValve", 128, 140, 0, 500, "FV-2105", act=270, lab=(-1, 5, "LeftCenter"))
TB = tee("Tee_RG2001_B", 145, 140, 0, 270, 500)
XBP = xv("XV2109", 145, 118, 270, 500, "XV-2109", 180, (-7, 6, "RightCenter"), "ButterflyValve")
TJ = tee("Tee_RG2002_J", 160, 93, 270, 180, 600, 500)
system("RG-2001", 500, "Waste nitrogen",
       [(None, (OPC_RG["id"], OPC_RG["nodes"][0]), [P(), I(FV5), P(), E(TB)], None),
        (None, (TB["id"], TB["nodes"][1]), [P((160, 140))], N("E2101", "N1")),
        (None, (TB["id"], TB["nodes"][2]), [P(), I(XBP), P((145, 93)), E(TJ, 2)], None)], (114, 149))
TR = tee("Tee_RG2002", 160, 80, 270, 0, 600)
XA3 = xv("XV2103A", 100, 99, 90, 600, "XV-2103A", 0, (3, 4, "LeftCenter"))
XB3 = xv("XV2103B", 220, 99, 90, 600, "XV-2103B", 180, (-3, 4, "RightCenter"))
system("RG-2002", 600, "Waste nitrogen",
       [(None, N("E2101", "N2"), [P(), E(TJ)], None),
        (None, (TJ["id"], TJ["nodes"][1]), [P(), E(TR)], None),
        (None, (TR["id"], TR["nodes"][1]), [P((100, 80)), I(XA3), P()], N("V2101A", "N3")),
        (None, (TR["id"], TR["nodes"][2]), [P((220, 80)), I(XB3), P()], N("V2101B", "N3"))], (170, 77))
# ---- feed air from P-01 (between the beds), inlet valves with repressurization bypasses XV-2111A/B
OPC_AIR = offpage("OPC_AIR1004_in", True, 160, 222, 270, 600, "from P-01 C-1101", (164, 226, "LeftCenter"))
TA = tee("Tee_AIR1004_A", 160, 205, 270, 0, 600)
seg, objs = [], {}
for k, x, bx, act in [("A", 100, 112, 180), ("B", 220, 208, 0)]:
    t1 = tee("Tee_AIR1004_%s1" % k, x, 198, 270, 0 if bx > x else 180, 600, 100)
    t2 = tee("Tee_AIR1004_%s2" % k, x, 182, 270, 0 if bx > x else 180, 600, 100)
    sgn = -1 if bx > x else 1
    v = xv("XV2101" + k, x, 190, 270, 600, "XV-2101" + k, act, (sgn * 3, 5, "RightCenter" if sgn < 0 else "LeftCenter"))
    r = xv("XV2111" + k, bx, 190, 270, 100, "XV-2111" + k, 0 if bx > x else 180,
           (-sgn * 3, 5, "LeftCenter" if sgn < 0 else "RightCenter"), "GlobeValve")
    first = (TA["id"], TA["nodes"][1 if k == "A" else 2])
    seg += [(None, first, [P((x, 205)), E(t1)], None),
            (None, (t1["id"], t1["nodes"][1]), [P(), I(v), P(), E(t2)], None),
            (None, (t2["id"], t2["nodes"][1]), [P()], N("V2101" + k, "N1")),
            (100, (t1["id"], t1["nodes"][2]), [P((bx, 198)), I(r), P((bx, 182)), E(t2, 2)], None)]
system("AIR-1004", 600, "Air", [(None, (OPC_AIR["id"], OPC_AIR["nodes"][0]), [P(), E(TA)], None)] + seg, (122, 211))
# ---- regeneration gas out (outer bottom nozzles) with depressurization bypasses XV-2112A/B, S-2101, atmosphere
TG = tee("Tee_RG2003", 240, 240, 0, 270, 600)
SIL = valve("S2101", "Silencer", 290, 240, 0, 600, "S-2101", shape_id="ShapeASU_Silencer", sc=1.0, half=6.0, srot=90,
            lab=(0, -9, "CenterCenter"))
OPC_V = offpage("OPC_RG2003_atm", False, 320, 226, 270, 600, "to atmosphere (safe location)", (324, 222, "LeftCenter"))
seg = []
for k, x, bx, act in [("A", 80, 68, 180), ("B", 240, 252, 0)]:
    br = 180 if bx < x else 0
    t1 = tee("Tee_RG2003_%s1" % k, x, 190, 90, br, 600, 100)
    t2 = tee("Tee_RG2003_%s2" % k, x, 210, 90, br, 600, 100)
    sgn = 1 if bx < x else -1
    v = xv("XV2104" + k, x, 200, 90, 600, "XV-2104" + k, act, (sgn * 3, 0, "LeftCenter" if sgn > 0 else "RightCenter"))
    r = xv("XV2112" + k, bx, 200, 90, 100, "XV-2112" + k, act,
           (-sgn * 3, 6, "RightCenter" if sgn > 0 else "LeftCenter"), "GlobeValve")
    tail = [P((80, 240)), E(TG)] if k == "A" else [P(), E(TG, 2)]
    seg += [(None, N("V2101" + k, "N4"), [P(), E(t1)], None),
            (None, (t1["id"], t1["nodes"][1]), [P(), I(v), P(), E(t2)], None),
            (None, (t2["id"], t2["nodes"][1]), tail, None),
            (100, (t1["id"], t1["nodes"][2]), [P((bx, 190)), I(r), P((bx, 210)), E(t2, 2)], None)]
system("RG-2003", 600, "Waste nitrogen",
       seg + [(None, (TG["id"], TG["nodes"][1]), [P(), I(SIL), P((320, 240)), E(OPC_V)], None)], (140, 246))

# ---- instruments
instrument("KS-2101", 300, 150, "V2101B_I1", "V2101B_I1_Pos", tgt="left")
instrument("AIA-2102", 260, 38, "Line_AIR2001_S3", "Line_AIR2001_S3_P1_I1")
instrument("AIA-2103", 275, 72, "Line_AIR2001_S3", "Line_AIR2001_S3_P1_I2", tgt="top")
instrument("TIC-2104", 185, 88, "Line_RG2002_S2", "Line_RG2002_S2_P1_I1", tgt="left",
           signal=[(185, 91.75), (185, 99), (166, 99)])
instrument("FIC-2105", 118, 124, "Line_RG2001_S1", "Line_RG2001_S1_P1_I1",
           signal=[(124.75, 124), (128, 124), TOPS["FV2105"]])
instrument("PDIA-2106", 318, 38, "F2101_I1", "F2101_I1_Pos", tgt="left")
instrument("PDI-2115A", 58, 155, "V2101A_I2", "V2101A_I2_Pos", tgt="right")
instrument("PDI-2115B", 272, 125, "V2101B_I2", "V2101B_I2_Pos", tgt="left")
instrument("TSHH-2116", 124, 90, "Line_RG2002_S2", "Line_RG2002_S2_P1_I2", tgt="right")
instrument("TSHH-2107", 185, 118, "E2101_I1", "E2101_I1_Pos", tgt="left")
instrument("TI-2113A", 60, 95, "Line_AIR2001_S1", "Line_AIR2001_S1_P1_I1", tgt="right")
instrument("TI-2113B", 260, 95, "Line_AIR2001_S2", "Line_AIR2001_S2_P1_I1", tgt="left")
instrument("TI-2114A", 60, 178, "Line_RG2003_S1", "Line_RG2003_S1_P1_I1", tgt="right")
instrument("TI-2114B", 270, 178, "Line_RG2003_S5", "Line_RG2003_S5_P1_I1", tgt="left")

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
