"""Throwaway generator for pid/P-01.xml (MAC and precooling), stage S2.

Writes the conceptual objects and their drawings into the empty sheet, in the XML form that
`plantcode fragment` prints (stdlib only; pyDEXPI is not importable here). After the first run the
XML is the source of truth (AGENTS.md); later changes are edits to pid/P-01.xml.
Usage: python3 scripts/draft_P-01.py pid/P-01.xml && plantcode fmt pid/P-01.xml
"""
import math
import sys

CON, DRW, SHP = [], [], []          # conceptual items, drawing groups, extra shapes
SYS, INS = [], []                   # piping systems, instrument functions
POS = {}                            # node id -> (position id, x, y)


def f(v):
    return repr(float(round(v, 4)))


def pt(x, y):
    return ('<AggregatedDataValue type="Core/Diagram.Point"><Data property="X"><Double>%s</Double>'
            '</Data><Data property="Y"><Double>%s</Double></Data></AggregatedDataValue>' % (f(x), f(y)))


def color(r, g, b):
    return ('<AggregatedDataValue type="Core/Diagram.Color"><Data property="B"><Integer>%d</Integer>'
            '</Data><Data property="G"><Integer>%d</Integer></Data><Data property="R"><Integer>%d'
            '</Integer></Data></AggregatedDataValue>' % (b, g, r))


def stroke(w=0.35, rgb=(0, 0, 0), dash="Solid"):
    return ('<Data property="Stroke"><AggregatedDataValue type="Core/Diagram.Stroke"><Data property='
            '"Color">%s</Data><Data property="DashStyle"><DataReference data="Core/Diagram.DashStyle.%s"/>'
            '</Data><Data property="Width"><Double>%s</Double></Data></AggregatedDataValue></Data>'
            % (color(*rgb), dash, f(w)))


def s(prop, val):
    return '<Data property="%s"><String>%s</String></Data>' % (prop, val)


def dn(d):
    return (s("NominalDiameterNumericalValueRepresentation", d) + s("NominalDiameterRepresentation", "DN " + str(d))
            + s("NominalDiameterTypeRepresentation", "DN"))


def node(nid, d):
    return '<Object id="%s" type="Plant/Piping.PipingNode">%s</Object>' % (nid, dn(d))


def nodepos(nid, x, y):
    pid = nid + "_Position"
    POS[nid] = (pid, x, y)
    return ('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="NodePositions">'
            '<Object id="%s" type="Plant/Diagram.PipingNodePosition"><References objects="#%s" property="Node"/>'
            '<Data property="Position">%s</Data></Object></Components><References objects="#%s" property="Represents"/>'
            '</Object>' % (nid, pid, nid, pt(x, y), nid))


def shapeuse(oid, shape, x, y, rot=0.0, sc=1.0, mirror=False):
    return ('<Object id="%s" type="Core/Diagram.ShapeUsage"><References objects="#%s" property="Shape"/>'
            '<Data property="IsMirrored"><Boolean>%s</Boolean></Data><Data property="Position">%s</Data>'
            '<Data property="Rotation"><Double>%s</Double></Data><Data property="ScaleX"><Double>%s</Double></Data>'
            '<Data property="ScaleY"><Double>%s</Double></Data></Object>'
            % (oid, shape, "true" if mirror else "false", pt(x, y), f(rot), f(sc), f(sc)))


def static(gid, elements):
    return ('<Object id="%s" type="Core/Diagram.Static"><Components property="Elements">%s</Components></Object>'
            % (gid, "".join(elements)))


def text(tid, x, y, txt, size=2.5, align="CenterCenter", attr=None):
    tpl = ""
    if attr:
        tpl = ('<Components property="Template"><Object id="%s_T" type="Core/Diagram.TextTemplate"><Components '
               'property="Fragments"><Object id="%s_F" type="Core/Diagram.AttributeRepresentation"><References '
               'objects="#%s" property="Object"/>%s<Data property="Type"><DataReference data="Core/Diagram.'
               'AttributeRepresentationType.Value"/></Data></Object></Components></Object></Components>'
               % (tid, tid, attr[0], s("AttributeName", attr[1])))
    return ('<Object id="%s" type="Core/Diagram.Text">%s<Data property="Alignment"><DataReference data="Core/Diagram.'
            'TextAlignment.%s"/></Data><Data property="Color">%s</Data>%s<Data property="Position">%s</Data>'
            '<Data property="Rotation"><Double>0.0</Double></Data><Data property="Size"><Double>%s</Double></Data>%s'
            '</Object>' % (tid, tpl, align, color(0, 0, 0), s("Font", "Calibri"), pt(x, y), f(size), s("Text", txt)))


def label(lid, cls, texts):
    return ('<Object id="%s" type="Plant/Diagram.%s"><Components property="Elements">%s</Components></Object>'
            % (lid, cls, "".join(texts)))


def polyline(oid, pts, w=0.25, rgb=(0, 0, 0), dash="Solid", closed=False):
    if closed:
        pts = list(pts) + [pts[0]]
    return ('<Object id="%s" type="Core/Diagram.PolyLine"><Data property="Points">%s</Data>%s</Object>'
            % (oid, "".join(pt(x, y) for x, y in pts), stroke(w, rgb, dash)))


def ellipse(oid, cx, cy, r, w=0.3):
    return ('<Object id="%s" type="Core/Diagram.Ellipse"><Data property="Center">%s</Data><Data property='
            '"FillStyle"><DataReference data="Core/Diagram.FillStyle.Transparent"/></Data><Data property='
            '"HorizontalSemiAxis"><Double>%s</Double></Data><Data property="Rotation"><Double>0.0</Double></Data>'
            '%s<Data property="VerticalSemiAxis"><Double>%s</Double></Data></Object>'
            % (oid, pt(cx, cy), f(r), stroke(w, (128, 0, 0)), f(r)))


def shape(sid, name, prims):
    SHP.append('<Object id="%s" type="Core/Diagram.Shape"><Components property="Primitives">%s</Components>%s%s'
               '</Object>' % (sid, "".join(prims), s("Name", name), s("SymbolRegistrationNumber", "ASU-" + sid[9:])))


EQ = (128, 0, 0)
# ---- custom shapes (equipment symbols not in the reference catalogue)
shape("ShapeASU_Compressor", "CENTRIFUGAL_COMPRESSOR_SHAPE",
      [polyline("ShapeASU_Compressor_P1", [(-12, -10), (12, -5), (12, 5), (-12, 10)], 0.35, EQ, closed=True)])
shape("ShapeASU_Filter", "GAS_FILTER_SHAPE",
      [polyline("ShapeASU_Filter_P1", [(-5, -8), (5, -8), (5, 8), (-5, 8)], 0.35, EQ, closed=True),
       polyline("ShapeASU_Filter_P2", [(-5, 8), (5, -8)], 0.25, EQ, "Dash"),
       polyline("ShapeASU_Filter_P3", [(-9, -4), (-5, -4)], 0.25, EQ),
       polyline("ShapeASU_Filter_P4", [(-9, 4), (-5, 4)], 0.25, EQ)])
shape("ShapeASU_Silencer", "SILENCER_SHAPE",
      [polyline("ShapeASU_Silencer_P1", [(-4, -6), (4, -6), (4, 6), (-4, 6)], 0.35, EQ, closed=True),
       polyline("ShapeASU_Silencer_P2", [(0, -6), (-3, -3), (3, 0), (-3, 3), (0, 6)], 0.25, EQ)])
shape("ShapeASU_Cooler", "HEAT_EXCHANGER_SHAPE",
      [ellipse("ShapeASU_Cooler_P1", 0, 0, 6, 0.35),
       polyline("ShapeASU_Cooler_P2", [(-3, 5.2), (-3, -1), (0, 2), (3, -1), (3, 5.2)], 0.25, EQ)])


def column_shape(sid, hw, hh, beds, extra=()):
    prims = [polyline(sid + "_P1", [(-hw, -hh + hw), (-hw, hh - 3), (-hw + 3, hh), (hw - 3, hh), (hw, hh - 3),
                                    (hw, -hh + hw), (hw * 0.7, -hh + hw * 0.3), (0, -hh), (-hw * 0.7, -hh + hw * 0.3)],
                      0.35, EQ, closed=True)]
    for i, (y0, y1) in enumerate(beds):
        prims.append(polyline("%s_B%d" % (sid, i), [(-hw, y0), (hw, y0), (-hw, y1), (hw, y1), (-hw, y0)], 0.2, EQ))
    for i, (y0, dash) in enumerate(extra):
        prims.append(polyline("%s_E%d" % (sid, i), [(-hw, y0), (hw, y0)], 0.2, EQ, dash))
    shape(sid, "COLUMN_SHAPE_" + sid[-5:], prims)


# DCAC 24 x 120, centre (205,110): CHW bed y 80..100, CW bed 125..142, mist eliminator 60
column_shape("ShapeASU_C1101", 12, 60, [(-30, -10), (15, 32)], [(-50, "Dash")])
# evaporative cooler 20 x 90, centre (330,110): bed 82..138
column_shape("ShapeASU_C1102", 10, 45, [(-28, 28)], [(-40, "Dash")])


# ---- equipment
def equipment(eid, cls, tag, shp, x, y, nozzles, lab, rot=0.0, sc=1.0, inst=()):
    """nozzles: (suffix, sub tag, x, y, DN). inst: (suffix, x, y) instrumentation node positions."""
    nz, nzd = [], []
    for suf, sub, nx, ny, d in nozzles:
        nid, nn = "%s_%s" % (eid, suf), "%s_%s_Node" % (eid, suf)
        nz.append('<Object id="%s" type="Plant/ProcessEquipment.ProcessNozzle"><Components property="Nodes">%s'
                  '</Components>%s</Object>' % (nid, node(nn, d), s("SubTagName", sub)))
        nzd.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s'
                   '</Components><References objects="#%s" property="Represents"/></Object>'
                   % (nid, nodepos(nn, nx, ny), nid))
    for suf, ix, iy in inst:                                   # instrument connections (no pipe)
        nid = "%s_%s" % (eid, suf)
        nz.append('<Object id="%s" type="Plant/ProcessEquipment.ProcessNozzle">%s</Object>' % (nid, s("SubTagName", suf)))
        nzd.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="NodePositions">'
                   '<Object id="%s_Pos" type="Plant/Diagram.InstrumentationNodePosition"><Data property="Position">%s'
                   '</Data></Object></Components><References objects="#%s" property="Represents"/></Object>'
                   % (nid, nid, pt(ix, iy), nid))
    inst = ()
    prefix, num = tag.split("-")
    seq = "".join(c for c in num if c.isdigit())
    CON.append('<Object id="%s" type="Plant/ProcessEquipment.%s"><Components property="Nozzles">%s</Components>%s%s%s'
               '%s</Object>' % (eid, cls, "".join(nz), s("TagName", tag), s("TagNamePrefix", prefix),
                                s("TagNameSequenceNumber", seq), s("TagNameSuffix", num[len(seq):]) if num[len(seq):] else ""))
    ipos = "".join('<Object id="%s_%s" type="Plant/Diagram.InstrumentationNodePosition"><Data property="Position">'
                   '%s</Data></Object>' % (eid, suf, pt(ix, iy)) for suf, ix, iy in inst)
    DRW.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s%s'
               '</Components>%s<References objects="#%s" property="Represents"/></Object>'
               % (eid, static(eid + "_Symbol", [shapeuse(eid + "_SymbolShape", shp, x, y, rot, sc)]), "".join(nzd),
                  label(eid + "_TagLabel", "EquipmentTagNameLabel",
                        [text(eid + "_TagText", lab[0], lab[1], tag, 3.0, attr=(eid, "TagName"))]),
                  '<Components property="NodePositions">%s</Components>' % ipos if ipos else "", eid))


def NUMATTR(cls):
    return "PositionNumber" if "Safety" in cls else "PipingComponentNumber"


DIRS = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}


def valve(vid, cls, x, y, rot, d, tag=None, act=None, shape_id=None, sc=0.4, half=2.0, srot=None):
    """Inline valve; act = side of the actuator (0/90/180/270) for a control valve."""
    dx, dy = DIRS[rot]
    n1, n2 = vid + "_N1", vid + "_N2"
    if cls == "SpringLoadedGlobeSafetyValve":         # inlet below, outlet to the right
        p1, p2 = (x, y + 2), (x + 2, y)
    else:
        p1, p2 = (x - half * dx, y - half * dy), (x + half * dx, y + half * dy)
    sid = shape_id or {"GlobeValve": "Shape3", "BallValve": "Shape8", "SwingCheckValve": "Shape6",
                       "ButterflyValve": "Shape5", "SpringLoadedGlobeSafetyValve": "Shape9"}[cls]
    els = [shapeuse(vid + "_SymbolShape", sid, x, y, 0.0 if cls == "SpringLoadedGlobeSafetyValve" else
                    (rot if srot is None else srot), sc)]
    top = None
    if act is not None:
        els.append(shapeuse(vid + "_ActuatorShape", "Shape1", x, y, act, 0.4))
        ax, ay = DIRS[act]
        top = (x + 7.2 * ax, y + 7.2 * ay)
    labs = ""
    if tag:
        ox, oy = (5, -3) if rot in (0, 180) else (3, 0)
        if act is not None:
            ox, oy = (5, 4.5) if rot in (0, 180) and act == 270 else (ox, oy)
            if rot in (90, 270) and act == 0:
                ox = -3
            if rot in (90, 270) and act == 180:
                ox = 3
            if rot in (0, 180) and act == 90:
                ox, oy = 5, -3
        al = "LeftCenter" if ox > 0 else "RightCenter"
        labs = label(vid + "_Label", "PipingComponentNumberLabel" if False else "ValveLabel",
                     [text(vid + "_LabelText", x + ox, y + oy, tag, 2.2, al, (vid, NUMATTR(cls)))])
    item = ('<Object id="%s" type="Plant/Piping.%s"><Components property="Nodes">%%s</Components>%s</Object>'
            % (vid, cls, s(NUMATTR(cls), tag) if tag else ""))
    drw = ('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s%s%s'
           '</Components><References objects="#%s" property="Represents"/></Object>'
           % (vid, nodepos(n1, *p1), nodepos(n2, *p2), static(vid + "_Symbol", els), labs, vid))
    return {"id": vid, "nodes": (n1, n2), "xml": lambda d: item % (node(n1, d) + node(n2, d)), "drw": drw, "top": top}


def tee(tid, x, y, rot, branch, d, bd=None):
    dx, dy = DIRS[rot]
    bx, by = DIRS[branch]
    e = 0.001
    n1, n2, n3 = tid + "_N1", tid + "_N2", tid + "_N3"
    drw = ('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s%s%s'
           '</Components><References objects="#%s" property="Represents"/></Object>'
           % (tid, nodepos(n1, x - e * dx, y - e * dy), nodepos(n2, x + e * dx, y + e * dy),
              nodepos(n3, x + e * bx, y + e * by), static(tid + "_Symbol", [shapeuse(tid + "_SymbolShape", "Shape12",
                                                                                     x, y, rot, 0.0001)]), tid))
    xml = ('<Object id="%s" type="Plant/Piping.PipeTee"><Components property="Nodes">%s%s%s</Components></Object>'
           % (tid, node(n1, d), node(n2, d), node(n3, bd or d)))
    return {"id": tid, "nodes": (n1, n2, n3), "xml": lambda _d: xml, "drw": drw, "top": None}


def offpage(cid, inflow, x, y, rot, d, note, note_at):
    """Off-page connector: node at (x, y); rot is the arrow direction."""
    n = cid + "_N"
    cls = "FlowInPipeOffPageConnector" if inflow else "FlowOutPipeOffPageConnector"
    drw = ('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s%s'
           '</Components><References objects="#%s" property="Represents"/></Object>'
           % (cid, nodepos(n, x, y), static(cid + "_Symbol", [shapeuse(cid + "_SymbolShape", "Shape2" if inflow else
                                                                       "Shape14", x, y, rot, 0.8)]),
              static(cid + "_Note", [text(cid + "_NoteText", note_at[0], note_at[1], note, 2.2, note_at[2])]), cid))
    xml = ('<Object id="%s" type="Plant/Piping.%s"><Components property="Nodes">%s</Components></Object>'
           % (cid, cls, node(n, d)))
    o = {"id": cid, "nodes": (n,), "xml": lambda _d: xml, "drw": drw, "top": None}
    if inflow:
        OBJ[cid] = o
    return o


TOPS = {}
OBJ = {}            # off-page connectors by id (a segment starting at one owns it)
PIPE_INST = {}      # pipe id -> [(suffix, x, y)] instrumentation node positions on that pipe


def system(line, d, fluid, segments, lab):
    """segments: list of (d or None, start (item, node), [steps], end (item, node) or None)
    step: ("pipe", [bends], pipe-id-suffix or None) | ("item", obj) | ("end", obj) item the segment ends at."""
    sid = "Line_" + line.replace("-", "")
    segx, segd = [], []
    for k, (sd, start, steps, end) in enumerate(segments, 1):
        sd = sd or d
        gid = "%s_S%d" % (sid, k)
        items, conns, cdrw, idrw = [], [], [], []
        cur = start
        objs = [st[1] for st in steps if st[0] == "item" or (st[0] == "end" and st[2] == 0)]
        if start[0] in OBJ:
            objs.insert(0, OBJ[start[0]])
        for o in objs:
            items.append(o["xml"](sd))
            idrw.append(o["drw"])
            if o["top"]:
                TOPS[o["id"]] = o["top"]
        pn = 0
        last_target = None
        for i, st in enumerate(steps):
            if st[0] != "pipe":
                o = st[1]
                cur = (o["id"], o["nodes"][1]) if st[0] == "item" else cur
                continue
            pn += 1
            nxt = None
            for st2 in steps[i + 1:]:
                if st2[0] in ("item", "end"):
                    nxt = (st2[1]["id"], st2[1]["nodes"][0])
                    break
                if st2[0] == "pipe":
                    break
            if nxt is None:
                nxt = end
            if steps[i + 1:] and steps[i + 1][0] == "end" and len(steps[i + 1]) > 2:
                nxt = (steps[i + 1][1]["id"], steps[i + 1][1]["nodes"][steps[i + 1][2]])
            pid = "%s_P%d" % (gid, pn)
            conns.append('<Object id="%s" type="Plant/Piping.Pipe"><References objects="#%s" property="SourceItem"/>'
                         '<References objects="#%s" property="SourceNode"/><References objects="#%s" property='
                         '"TargetItem"/><References objects="#%s" property="TargetNode"/></Object>'
                         % (pid, cur[0], cur[1], nxt[0], nxt[1]))
            bends = st[1]
            inner = ('<Data property="InnerPoints">%s</Data>' % "".join(pt(*b) for b in bends)) if bends else ""
            ipos = "".join('<Object id="%s_%s" type="Plant/Diagram.InstrumentationNodePosition"><Data property='
                           '"Position">%s</Data></Object>' % (pid, suf, pt(ix, iy))
                           for suf, ix, iy in PIPE_INST.get((line, k, pn), []))
            cdrw.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">'
                        '<Object id="%s_Line" type="Core/Diagram.Static"><Components property="Elements"><Object id='
                        '"%s_LineShape" type="Core/Diagram.ConnectorLine">%s<References objects="#%s" property="Source"/>'
                        '<References objects="#%s" property="Target"/>%s</Object></Components></Object></Components>'
                        '%s<References objects="#%s" property="Represents"/></Object>'
                        % (pid, pid, pid, inner, POS[cur[1]][0], POS[nxt[1]][0],
                           stroke(0.5 if sd >= 100 else 0.35), '<Components property="NodePositions">%s</Components>'
                           % ipos if ipos else "", pid))
            last_target = nxt
            cur = nxt
        segx.append('<Object id="%s" type="Plant/Piping.PipingNetworkSegment"><Components property="Connections">%s'
                    '</Components>%s<References objects="#%s" property="SourceItem"/><References objects="#%s" '
                    'property="SourceNode"/><References objects="#%s" property="TargetItem"/><References objects="#%s" '
                    'property="TargetNode"/>%s%s%s</Object>'
                    % (gid, "".join(conns), '<Components property="Items">%s</Components>' % "".join(items)
                       if items else "", start[0], start[1], last_target[0], last_target[1], s("FluidCode", fluid),
                       dn(sd), s("SegmentNumber", "S%d" % k)))
        segd.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s'
                    '</Components><References objects="#%s" property="Represents"/></Object>'
                    % (gid, "".join(cdrw), "".join(idrw), gid))
    SYS.append('<Object id="%s" type="Plant/Piping.PipingNetworkSystem"><Components property="Segments">%s</Components>'
               '%s%s%s</Object>' % (sid, "".join(segx), s("FluidCode", fluid), s("LineNumber", line), dn(d)))
    lx, ly = lab
    DRW.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s'
               '</Components><References objects="#%s" property="Represents"/></Object>'
               % (sid, "".join(segd), label(sid + "_Label", "PipingNetworkSystemLabel",
                                           [text(sid + "_LabelNo", lx, ly, line, 2.2, "LeftBottom", (sid, "LineNumber")),
                                            text(sid + "_LabelDN", lx, ly + 2.8, "DN %d" % d, 2.0, "LeftBottom",
                                                 (sid, "NominalDiameterRepresentation"))]), sid))


def instrument(tag, x, y, sensing, src_pos, tgt="bottom", signal=None, central=True):
    """sensing: id of the sensing item; src_pos: id of the InstrumentationNodePosition the measuring line starts at;
    tgt: bubble node the measuring line ends at; signal: list of points from a bubble node to the actuator."""
    letters, num = tag.split("-")
    iid = "Inst_" + tag.replace("-", "")
    cat, fun = letters[0], letters[1:]
    if letters.startswith("PD"):
        cat, fun = "P", letters[1:]
    INS.append('<Object id="%s" type="Plant/Instrumentation.ProcessInstrumentationFunction"><Components property='
               '"ProcessSignalGeneratingFunctions"><Object id="%s_PSGF" type="Plant/Instrumentation.'
               'ProcessSignalGeneratingFunction"><References objects="#%s" property="SensingLocation"/>%s</Object>'
               '</Components><Components property="SignalConveyingFunctions"><Object id="%s_ML" type="Plant/'
               'Instrumentation.MeasuringLineFunction"><References objects="#%s_PSGF" property="Source"/><References '
               'objects="#%s" property="Target"/></Object></Components><Data property="Location"><DataReference '
               'data="Plant/Enumerations.LocationClassification.%s"/></Data>%s%s%s</Object>'
               % (iid, iid, sensing, s("ProcessSignalGeneratingFunctionNumber", cat + "T" + num), iid, iid, iid,
                  "CentralLocation" if central else "Field", s("ProcessInstrumentationFunctionCategory", cat),
                  s("ProcessInstrumentationFunctionNumber", num), s("ProcessInstrumentationFunctions", fun)))
    nodes = {"top": (x, y - 3.75), "bottom": (x, y + 3.75), "left": (x - 6.75, y), "right": (x + 6.75, y)}
    npos = "".join('<Object id="%s_%s" type="Plant/Diagram.InstrumentationNodePosition"><Data property="Position">%s'
                   '</Data></Object>' % (iid, k, pt(*v)) for k, v in nodes.items())
    ml = ('<Object id="%s_ML_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups"><Object id='
          '"%s_ML_Line" type="Core/Diagram.Static"><Components property="Elements"><Object id="%s_ML_LineShape" type='
          '"Core/Diagram.ConnectorLine"><References objects="#%s" property="Source"/><References objects="#%s_%s" '
          'property="Target"/>%s</Object></Components></Object></Components><References objects="#%s_ML" property='
          '"Represents"/></Object>' % (iid, iid, iid, src_pos, iid, tgt, stroke(0.2, (0, 128, 0)), iid))
    sig = static(iid + "_Signal", [polyline(iid + "_SignalLine", signal, 0.2, (0, 0, 0), "Dash")]) if signal else ""
    DRW.append('<Object id="%s_Drawing" type="Core/Diagram.RepresentationGroup"><Components property="Groups">%s%s%s%s'
               '</Components><Components property="NodePositions">%s</Components><References objects="#%s" property='
               '"Represents"/></Object>'
               % (iid, static(iid + "_Bubble", [shapeuse(iid + "_BubbleShape", "Shape17" if central else "Shape16",
                                                         x, y)]),
                  label(iid + "_Label", "ProcessInstrumentationFunctionLabel",
                        [text(iid + "_Letters", x, y - 2.25, letters, 3.0, attr=None) .replace("", "") if False else
                         text2(iid, "Letters", x, y - 2.25, letters, [(iid, "ProcessInstrumentationFunctionCategory"),
                                                                     (iid, "ProcessInstrumentationFunctions")]),
                         text(iid + "_Number", x, y + 1.2, num, 3.0, attr=(iid, "ProcessInstrumentationFunctionNumber"))]),
                  ml, sig, npos, iid))


def text2(iid, suf, x, y, txt, attrs):
    """Text with several attribute fragments (letters = category + functions)."""
    tid = iid + "_" + suf
    frs = "".join('<Object id="%s_F%d" type="Core/Diagram.AttributeRepresentation"><References objects="#%s" '
                  'property="Object"/>%s<Data property="Type"><DataReference data="Core/Diagram.'
                  'AttributeRepresentationType.Value"/></Data></Object>' % (tid, i, o, s("AttributeName", a))
                  for i, (o, a) in enumerate(attrs, 1))
    return ('<Object id="%s" type="Core/Diagram.Text"><Components property="Template"><Object id="%s_T" type="Core/'
            'Diagram.TextTemplate"><Components property="Fragments">%s</Components></Object></Components><Data '
            'property="Alignment"><DataReference data="Core/Diagram.TextAlignment.CenterCenter"/></Data><Data '
            'property="Color">%s</Data>%s<Data property="Position">%s</Data><Data property="Rotation"><Double>0.0'
            '</Double></Data><Data property="Size"><Double>3.0</Double></Data>%s</Object>'
            % (tid, tid, frs, color(0, 0, 0), s("Font", "Calibri"), pt(x, y), s("Text", txt)))


# =============================================================================================
# Equipment
equipment("F1101", "GasFilter", "F-1101", "ShapeASU_Filter", 35, 70, [("N1", "N1", 40, 70, 1400)], (35, 82),
          inst=[("I1", 35, 62)])
equipment("K1101", "CentrifugalCompressor", "K-1101", "ShapeASU_Compressor", 85, 70,
          [("N1", "N1", 73, 70, 1400), ("N2", "N2", 77, 79.17, 900), ("N3", "N3", 82, 78.125, 900),
           ("N4", "N4", 87, 77.08, 700), ("N5", "N5", 92, 76.04, 700), ("N6", "N6", 97, 70, 600)], (58, 84),
          inst=[("I1", 88, 63.1)])
for eid, tag, x, y, d, lab in [("E1101", "E-1101", 75, 115, 900, (60, 115)), ("E1102", "E-1102", 95, 115, 700, (110, 115))]:
    equipment(eid, "TubularHeatExchanger", tag, "ShapeASU_Cooler", x, y,
              [("N1", "N1", x - 3, y - 5.2, d), ("N2", "N2", x + 3, y - 5.2, d), ("N3", "N3", x - 3, y + 5.2, 300),
               ("N4", "N4", x + 3, y + 5.2, 300)], lab)
equipment("E1103", "TubularHeatExchanger", "E-1103", "ShapeASU_Cooler", 125, 70,
          [("N1", "N1", 119, 70, 600), ("N2", "N2", 131, 70, 600), ("N3", "N3", 122, 75.2, 300),
           ("N4", "N4", 128, 75.2, 300)], (125, 61))
equipment("C1101", "ProcessColumn", "C-1101", "ShapeASU_C1101", 205, 110,
          [("N1", "N1", 193, 150, 600), ("N2", "N2", 205, 50, 600), ("N3", "N3", 193, 120, 200),
           ("N4", "N4", 217, 75, 150), ("N5", "N5", 205, 170, 250), ("N6", "N6", 196, 52.1, 150)], (222, 57),
          inst=[("I1", 217, 165), ("I2", 217, 150)])
equipment("C1102", "ProcessColumn", "C-1102", "ShapeASU_C1102", 330, 110,
          [("N1", "N1", 340, 145, 700), ("N2", "N2", 330, 65, 700), ("N3", "N3", 340, 72, 150),
           ("N4", "N4", 330, 155, 150)], (346, 60), inst=[("I1", 340, 135)])
for eid, tag, x, y, rot, d in [("P1101A", "P-1101A", 140, 200, 0, 200), ("P1101B", "P-1101B", 140, 225, 0, 200),
                               ("P1102A", "P-1102A", 290, 200, 180, 150), ("P1102B", "P-1102B", 290, 225, 180, 150)]:
    sx = -7.5 if rot == 0 else 7.5
    equipment(eid, "CentrifugalPump", tag, "Shape21", x, y,
              [("N1", "N1", x + sx, y, d), ("N2", "N2", x - sx, y, d)], (x, y + 11), rot=rot)

# instrument sensing points on pipes: (line, segment no, pipe no) -> positions
PIPE_INST[("AIR-1001", 1, 1)] = [("I1", 58, 70)]
PIPE_INST[("AIR-1002", 1, 1)] = [("I1", 112, 70)]
PIPE_INST[("AIR-1002", 3, 2)] = [("I1", 172, 70)]
PIPE_INST[("AIR-1004", 1, 1)] = [("I1", 268, 30)]
PIPE_INST[("CW-1001", 6, 1)] = [("I1", 180, 185)]


def N(eid, suf):
    return ("%s_%s" % (eid, suf), "%s_%s_Node" % (eid, suf))


P = lambda *b: ("pipe", list(b))     # noqa: E731
I = lambda o: ("item", o)            # noqa: E731
E = lambda o, k=0: ("end", o, k)     # noqa: E731

# ---- air path
system("AIR-1001", 1400, "Air", [(None, N("F1101", "N1"), [P()], N("K1101", "N1"))], (44, 67))
system("AIR-1005", 900, "Air", [(None, N("K1101", "N2"), [P((77, 95), (72, 95))], N("E1101", "N1")),
                                (None, N("E1101", "N2"), [P((78, 100), (82, 100))], N("K1101", "N3"))], (60, 93))
system("AIR-1006", 700, "Air", [(None, N("K1101", "N4"), [P((87, 95), (92, 95))], N("E1102", "N1")),
                                (None, N("E1102", "N2"), [P((98, 88), (92, 88))], N("K1101", "N5"))], (100, 92))
TBO = tee("Tee_AIR1002_BO", 145, 70, 0, 270, 600, 300)
CV1 = valve("CV_AIR1002", "SwingCheckValve", 160, 70, 0, 600)
system("AIR-1002", 600, "Air",
       [(None, N("K1101", "N6"), [P()], N("E1103", "N1")),
        (None, N("E1103", "N2"), [P(), E(TBO)], None),
        (None, (TBO["id"], TBO["nodes"][1]), [P(), I(CV1), P((187, 70), (187, 150))], N("C1101", "N1"))], (163, 79))
UV = valve("UV1102", "GlobeValve", 145, 52, 270, 300, "UV-1102", act=180)
SIL = valve("S1101", "Silencer", 145, 28, 270, 300, "S-1101", shape_id="ShapeASU_Silencer", sc=1.0, half=6.0, srot=0)
system("AIR-1003", 300, "Air", [(None, (TBO["id"], TBO["nodes"][2]), [P(), I(UV), P(), E(SIL)], None)], (147, 42))
PSV = valve("PSV1109", "SpringLoadedGlobeSafetyValve", 196, 40, 270, 150, "PSV-1109")
OPC_AIR = offpage("OPC_AIR1004", False, 380, 30, 0, 600, "to P-02 V-2101A/B", (385, 25, "CenterCenter"))
system("AIR-1004", 600, "Air", [(None, N("C1101", "N2"), [P((205, 30)), E(OPC_AIR)], None),
                                (150, N("C1101", "N6"), [P(), E(PSV)], None)], (290, 24))

# ---- cooling water to the DCAC
OPC_CW = offpage("OPC_CW1001", True, 110, 200, 0, 200, "CW supply", (100, 195, "CenterCenter"))
TCS = tee("Tee_CW1001_S", 125, 200, 0, 90, 200)
TCD = tee("Tee_CW1001_D", 170, 200, 0, 90, 200)
BV1 = valve("BV_P1101A_S", "BallValve", 129, 200, 0, 200)
BV2 = valve("BV_P1101B_S", "BallValve", 129, 225, 0, 200)
CV2 = valve("CV_P1101A_D", "SwingCheckValve", 158, 200, 0, 200)
CV3 = valve("CV_P1101B_D", "SwingCheckValve", 158, 225, 0, 200)
FV = valve("FV1108", "GlobeValve", 180, 160, 270, 200, "FV-1108", act=180)
system("CW-1001", 200, "Cooling water",
       [(None, (OPC_CW["id"], OPC_CW["nodes"][0]), [P(), E(TCS)], None),
        (None, (TCS["id"], TCS["nodes"][1]), [P(), I(BV1), P()], N("P1101A", "N1")),
        (None, (TCS["id"], TCS["nodes"][2]), [P((125, 225)), I(BV2), P()], N("P1101B", "N1")),
        (None, N("P1101A", "N2"), [P(), I(CV2), P(), E(TCD)], None),
        (None, N("P1101B", "N2"), [P(), I(CV3), P((170, 225)), E(TCD, 2)], None),
        (None, (TCD["id"], TCD["nodes"][1]), [P((180, 200)), I(FV), P((180, 120))], N("C1101", "N3"))], (106, 210))
# ---- DCAC sump water return
LV6 = valve("LV1106", "GlobeValve", 205, 185, 90, 250, "LV-1106", act=0)
OPC_CWR = offpage("OPC_CWR1001", False, 300, 250, 0, 250, "CW return", (305, 245, "CenterCenter"))
system("CWR-1001", 250, "Cooling water return",
       [(None, N("C1101", "N5"), [P(), I(LV6), P((205, 250)), E(OPC_CWR)], None)], (230, 244))
# ---- chilled water loop
TSH = tee("Tee_CHW1001_S", 310, 200, 180, 90, 150)
TDH = tee("Tee_CHW1001_D", 265, 200, 180, 90, 150)
BV3 = valve("BV_P1102A_S", "BallValve", 304, 200, 180, 150)
BV4 = valve("BV_P1102B_S", "BallValve", 304, 225, 180, 150)
CV4 = valve("CV_P1102A_D", "SwingCheckValve", 275, 200, 180, 150)
CV5 = valve("CV_P1102B_D", "SwingCheckValve", 275, 225, 180, 150)
TV = valve("TV1105", "GlobeValve", 250, 110, 270, 150, "TV-1105", act=0)
system("CHW-1001", 150, "Chilled water",
       [(None, N("C1102", "N4"), [P((330, 200)), E(TSH)], None),
        (None, (TSH["id"], TSH["nodes"][1]), [P(), I(BV3), P()], N("P1102A", "N1")),
        (None, (TSH["id"], TSH["nodes"][2]), [P((310, 225)), I(BV4), P()], N("P1102B", "N1")),
        (None, N("P1102A", "N2"), [P(), I(CV4), P(), E(TDH)], None),
        (None, N("P1102B", "N2"), [P(), I(CV5), P((265, 225)), E(TDH, 2)], None),
        (None, (TDH["id"], TDH["nodes"][1]), [P((250, 200)), I(TV), P((250, 75))], N("C1101", "N4"))], (252, 196))
# ---- evaporative cooler water feed, waste N2 in, vent
OPC_CW3 = offpage("OPC_CW1003", True, 390, 72, 180, 150, "CW supply", (395, 67, "CenterCenter"))
LV7 = valve("LV1107", "GlobeValve", 365, 72, 180, 150, "LV-1107", act=90)
system("CW-1003", 150, "Cooling water",
       [(None, (OPC_CW3["id"], OPC_CW3["nodes"][0]), [P(), I(LV7), P()], N("C1102", "N3"))], (343, 66))
OPC_WN = offpage("OPC_WN1001", True, 390, 145, 180, 700, "from P-03 WN-3002", (392, 140, "CenterCenter"))
system("WN-1001", 700, "Waste nitrogen",
       [(None, (OPC_WN["id"], OPC_WN["nodes"][0]), [P()], N("C1102", "N1"))], (350, 152))
OPC_ATM = offpage("OPC_WN1002", False, 330, 45, 270, 700, "to atmosphere (elevated)", (335, 33, "LeftCenter"))
system("WN-1002", 700, "Waste nitrogen", [(None, N("C1102", "N2"), [P(), E(OPC_ATM)], None)], (332, 55))
# ---- cooling water to intercoolers and aftercooler (utility connections)
cw_s, cwr_s = [], []
for eid, x, y in [("E1101", 75, 115), ("E1102", 95, 115), ("E1103", 125, 70)]:
    oi = offpage("OPC_CW1002_" + eid, True, x - 3, y + 20, 270, 300, "CW", (x - 3, y + 32, "CenterCenter"))
    oo = offpage("OPC_CWR1002_" + eid, False, x + 3, y + 20, 90, 300, "CWR", (x + 3, y + 32, "CenterCenter"))
    cw_s.append((None, (oi["id"], oi["nodes"][0]), [P()], N(eid, "N3")))
    cwr_s.append((None, N(eid, "N4"), [P(), E(oo)], None))
system("CW-1002", 300, "Cooling water", cw_s, (50, 138))
system("CWR-1002", 300, "Cooling water return", cwr_s, (50, 146))

# =============================================================================================
# Instruments
instrument("PDIA-1101", 35, 48, "F1101_I1", "F1101_I1_Pos")
instrument("FIC-1101", 58, 48, "Line_AIR1001_S1", "Line_AIR1001_S1_P1_I1",
           signal=[(64.75, 48), (73, 48), (73, 60)])
instrument("VIA-1104", 88, 45, "K1101_I1", "K1101_I1_Pos")
instrument("UIC-1102", 112, 50, "Line_AIR1002_S1", "Line_AIR1002_S1_P1_I1",
           signal=[(118.75, 50), (126, 50), (126, 52), TOPS["UV1102"]])
instrument("PIC-1103", 172, 52, "Line_AIR1002_S3", "Line_AIR1002_S3_P2_I1")
instrument("TIC-1105", 268, 110, "Line_AIR1004_S1", "Line_AIR1004_S1_P1_I1", tgt="top",
           signal=[(261.25, 110), TOPS["TV1105"]])
instrument("LIC-1106", 232, 165, "C1101_I1", "C1101_I1_Pos", tgt="left",
           signal=[(232, 168.75), (232, 185), TOPS["LV1106"]])
instrument("LSHH-1106", 232, 148, "C1101_I2", "C1101_I2_Pos", tgt="left")
instrument("LIC-1107", 365, 120, "C1102_I1", "C1102_I1_Pos", tgt="left", signal=[(365, 116.25), TOPS["LV1107"]])
instrument("FIC-1108", 164, 175, "Line_CW1001_S6", "Line_CW1001_S6_P1_I1", tgt="right",
           signal=[(164, 171.25), (164, 160), TOPS["FV1108"]])

# =============================================================================================
path = sys.argv[1]
doc = open(path, encoding="utf-8").read()
conc = ('<Components property="TaggedPlantItems">%s</Components><Components property="PipingNetworkSystems">%s'
        '</Components><Components property="ProcessInstrumentationFunctions">%s</Components>'
        % ("".join(CON), "".join(SYS), "".join(INS)))
a = '<Components property="MetaData">'
assert doc.count(a) == 1 and "TaggedPlantItems" not in doc, "run on the empty sheet only"
doc = doc.replace(a, conc + a, 1)
g = '<Object id="PlantModel1_Drawing1" type="Core/Diagram.Diagram">'
i = doc.index(g)
j = doc.index('<Components property="Groups">', i) + len('<Components property="Groups">')
doc = doc[:j] + "".join(DRW) + doc[j:]
k = doc.index('<Components property="Shapes">') + len('<Components property="Shapes">')
doc = doc[:k] + "".join(SHP) + doc[k:]
open(path, "w", encoding="utf-8").write(doc)
print("equipment %d, lines %d, instruments %d" % (len(CON), len(SYS), len(INS)))
