"""P-201 seed train A, stages 3 to 5 (provenance script; the XML is the source).

    cheme sheet new P-201 --title 'Seed train A, stages 3 to 5'
    cheme run scripts/draft_P-201.py pid/P-201.xml

Seed fermenters R-211A (1 m3), R-212A (10 m3) and R-213A (107 m3) with agitators, jackets on
cooling water, sterile N2 inlet and vent filters, rupture discs, steam blocks on the medium,
base, inoculum and transfer connections, CIP supply and return, SIP steam; the seed base tank
T-215 with P-215A/B and the sterile filter F-215 (D-013, D-020, D-030). Trains B and C are drawn
as typicals on P-205.
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import (
    Nozzle,
    Sheet,
    equipment,
    instrument,
    line,
    note,
    offpage,
    tee,
    valve,
)

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-201.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
LEFT, RIGHT = 14, 406
Y_SM, Y_NS, Y_CS, Y_NA, Y_SS = 14, 24, 34, 44, 54      # top headers, SIP steam lowest
Y_CR, Y_SB = 224, 236                                   # bottom headers
Y_VB = 60                                              # top of the vertical steam blocks
X_LBL = 85                                              # header labels, clear of the drops


class Block:
    """A steam block: two ball valves, steam fed and condensate bled between them (D-020)."""

    def __init__(self, key, x, y, d=0, steam="up"):
        self.key, self.steam = key, steam
        if d == 0:                                       # vertical, flow down
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y)),
                          tee(f"{key}_SBS", at=(x, y + 5), branch="left", branch_dn=15),
                          tee(f"{key}_SBB", at=(x, y + 10), branch="left", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x, y + 15))]
            self.ss_x, self.ss_y = x - 8, y + 5
            self.bleed = [(x - 4, y + 10), (x - 4, y + 14), (x - 4, y + 19)]
        else:                                            # horizontal, d = +1 right, -1 left
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y)),
                          tee(f"{key}_SBS", at=(x + 5 * d, y), branch="down" if steam == "down" else "up",
                              branch_dn=15),
                          tee(f"{key}_SBB", at=(x + 10 * d, y), branch="down", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x + 16 * d, y))]
            self.ss_x, self.ss_y = x + 5 * d, y
            self.bleed = [None, (x + 10 * d, y + 5), (x + 10 * d, y + 10)]
        self.ts, self.tb = self.items[1], self.items[2]
        self.hdr = tee(f"{key}_SSH", at=(self.ss_x, Y_SB if steam == "down" else Y_SS),
                       branch="up" if steam == "down" else "down", branch_dn=15)

    def finish(self, ss_number):
        if self.bleed[0] is None:
            route = [self.hdr.branch, self.ts.branch]
        else:
            route = [self.hdr.branch, (self.ss_x, self.ss_y), self.ts.branch]
        line(sheet, "15-SS-2148", id=f"Line_{self.key}_SS", dn=15, fluid="SS", labels=False, route=route)
        b1, trap, end = self.bleed
        route = [self.tb.branch] + ([b1] if b1 else []) + [
            valve(f"{self.key}_ST", "SteamTrap", at=trap), offpage("out", at=end, note="drain")]
        line(sheet, "15-CD-2149", id=f"Line_{self.key}_CD", dn=15, fluid="CD", labels=False, route=route)


def seed(k, cx, cy, sx, sy, dn_m, dn_out, prev=None):
    """Seed fermenter R-21kA with agitator, nozzles and its own lines; returns its geometry."""
    w, h = 10 * sx, 14.3 * sy
    tag, key = f"R-21{k}A", f"R21{k}A"
    nz = [Nozzle("N1", (-0.5 * w, -h), dn_m), Nozzle("N4", (0.5 * w, -h), 25),
          Nozzle("N5", (0.15 * w, -h), 25), Nozzle("N6", (w, -0.7 * h), 25),
          Nozzle("N3", (w, -0.15 * h), 15 if k < 3 else 25), Nozzle("N7", (-0.85 * w, -0.8 * h), 25),
          Nozzle("N9", (0, h), dn_out), Nozzle("C1", (-w, 0.7 * h), 25), Nozzle("C2", (-w, 0.3 * h), 25),
          Nozzle("T1", (-0.97 * w, 0.88 * h)), Nozzle("A1", (w, 0.65 * h)), Nozzle("P1", (0.8 * w, -0.85 * h)),
          Nozzle("L1", (-0.2 * w, -h)), Nozzle("W1", (0.85 * w, 0.85 * h))]
    if prev:
        nz.append(Nozzle("N2", (-w, -0.55 * h), prev))
    r = equipment(sheet, "Vessel", tag, shape=VESSEL, at=(cx, cy), scale=(sx, sy), nozzles=nz,
                  label_at=(cx + 0.05 * w, cy - h + 6))
    equipment(sheet, "Agitator", f"A-21{k}A", shape="AGITATOR_SHAPE", at=(cx, cy + 0.2 * h),
              label_at=(cx + 0.55 * w, cy + 0.2 * h + 4))
    g = dict(k=k, cx=cx, cy=cy, w=w, h=h, top=cy - h, bot=cy + h, r=r, key=key, blocks=[])
    return g


sm_tees, ss_tees, ns_tees, cs_tees, cr_tees, sb_tees = [], [], [], [], [], []

# ---- Equipment ----
R1 = seed(1, 115, 125, 2.0, 1.4, 25, 25)
R2 = seed(2, 225, 128, 2.4, 1.8, 50, 50, prev=25)
R3 = seed(3, 341, 132, 2.6, 2.4, 100, 100, prev=50)
TRAIN = [R1, R2, R3]

t215 = equipment(sheet, "Tank", "T-215", shape=VESSEL, at=(28, 118),
                 nozzles=[Nozzle("N2", (0, 14.3), 15), Nozzle("L1", (10, 8))])
pa = equipment(sheet, "CentrifugalPump", "P-215A", shape=PUMP, at=(40, 195),
               nozzles=[Nozzle("N1", (-7.5, 0), 15), Nozzle("N2", (0, -7.5), 15)])
pb = equipment(sheet, "CentrifugalPump", "P-215B", shape=PUMP, at=(66, 208),
               nozzles=[Nozzle("N1", (-7.5, 0), 15), Nozzle("N2", (0, -7.5), 15)])
f215 = equipment(sheet, "Filter", "F-215", shape="LIQUID_FILTER_SHAPE", at=(66, 150), scale=0.4,
                 nozzles=[Nozzle("N1", (0, 5), 15), Nozzle("N2", (0, -5), 15)], label_at=(57, 150))

# ---- Per-vessel tees, blocks and filters (positions first, lines after the headers) ----
for g in TRAIN:
    k, cx, cy, w, h, key = g["k"], g["cx"], g["cy"], g["w"], g["h"], g["key"]
    xm, xc, xv, xg = cx - 0.5 * w, cx + 0.15 * w, cx + 0.5 * w, cx + w + 10
    g["xm"], g["xc"], g["xv"], g["xg"] = xm, xc, xv, xg
    dn_m = {1: 25, 2: 50, 3: 100}[k]
    g["t_sm"] = tee(f"{key}_TSM", at=(xm, Y_SM), branch="down", branch_dn=dn_m)
    g["t_ns"] = tee(f"{key}_TNS", at=(xg, Y_NS), branch="down", branch_dn=25)
    g["t_cs"] = tee(f"{key}_TCS", at=(xc, Y_CS), branch="down", branch_dn=25)
    g["t_cr"] = tee(f"{key}_TCR", at=(cx, Y_CR), branch="up", branch_dn=dn_m)
    g["t_sb"] = tee(f"{key}_TSB", at=(cx - 8, Y_SB), branch="up", branch_dn=25)
    g["b_sm"] = Block(f"{key}M", xm, Y_VB)
    sm_tees.append(g["t_sm"]); ns_tees.append(g["t_ns"]); cs_tees.append(g["t_cs"])
    cr_tees.append(g["t_cr"]); sb_tees.append(g["t_sb"]); ss_tees.append(g["b_sm"].hdr)
    # bottom cluster: bottom valve, SIP tee, transfer tee, CIP return valve
    g["t_sip"] = tee(f"{key}_TSIP", at=(cx, g["bot"] + 10), branch="left", branch_dn=25)
    g["t_tr"] = tee(f"{key}_TTR", at=(cx, g["bot"] + 16), branch="right")
    fv = equipment(sheet, "GasFilter", f"F-24{2 * k - 1}A", shape="GAS_FILTER_SHAPE", at=(xv, 79), scale=0.4,
                   nozzles=[Nozzle("N1", (0, 5), 25), Nozzle("N2", (0, -5), 25)], label_at=(xv + 11, 84))
    fg = equipment(sheet, "GasFilter", f"F-24{2 * k}A", shape="GAS_FILTER_SHAPE", at=(xg, 74), scale=0.4,
                   nozzles=[Nozzle("N1", (0, -5), 25), Nozzle("N2", (0, 5), 25)], label_at=(xg - 11, 69))
    g["fv"], g["fg"] = fv, fg

# base (NaOH to R-211A, R-212A; lime to R-213A): horizontal blocks from the right
for g in TRAIN:
    x, yb = g["cx"] + g["w"], g["cy"] - 0.15 * g["h"]
    g["yb"] = yb
    g["b_base"] = Block(f"{g['key']}B", x + 23 if g["k"] < 3 else x + 21, yb, d=-1)
    ss_tees.append(g["b_base"].hdr)
R1["t_na"] = tee("R211A_TNA", at=(R1["cx"] + R1["w"] + 34, Y_NA), branch="down")

# inoculum in (R-212A, R-213A): horizontal blocks from the left
for g in (R2, R3):
    xr = g["cx"] - g["w"] - 28
    g["xr"], g["yi"] = xr, g["cy"] - 0.55 * g["h"]
    g["b_in"] = Block(f"{g['key']}I", xr + 5, g["yi"], d=1)
    ss_tees.append(g["b_in"].hdr)

# R-213A transfer out to the inoculum header: block steamed from the bottom SIP header
y_out = R3["bot"] + 16
R3["b_out"] = Block("R213AO", R3["cx"] + 16, y_out, d=1, steam="down")
sb_tees.append(R3["b_out"].hdr)

# ---- Headers ----
def header(number, dn, fluid, y, tees, text, out_text=None, reverse=False, lbl=(X_LBL, None), nx=42):
    ends = [offpage("in", at=(LEFT, y), note=text, note_at=(nx, y - 3)),
            offpage("out", at=(RIGHT, y), note=out_text, note_at=(388, y - 3) if out_text else None)]
    if reverse:
        ends = [offpage("in", at=(RIGHT, y), note=out_text, note_at=(388, y - 3)),
                offpage("out", at=(LEFT, y), note=text, note_at=(nx, y - 3))]
    tees = sorted(tees, key=lambda t: -t.at[0] if reverse else t.at[0])
    line(sheet, number, dn=dn, fluid=fluid, label_at=(lbl[0], lbl[1] or y + 1.5), route=[ends[0], *tees, ends[1]])


header("100-SM-2003", 100, "SM", Y_SM, sm_tees, "Sterile medium, 200-SM-2001 (P-203)", "Trains B, C (P-205)",
       lbl=(178, None))
header("40-NS-2141", 40, "NS", Y_NS, ns_tees, "N2, 80-NS-2008 (P-203)", "P-205", lbl=(178, None))
header("50-CS-2142", 50, "CS", Y_CS, cs_tees, "CIP supply, 100-CS-2015 (P-204)", "P-205", lbl=(178, None))
header("50-SS-2140", 50, "SS", Y_SS, ss_tees, "SIP steam, 150-SS-2019 (P-204)", "P-205", lbl=(X_LBL - 40, Y_SS + 4))
header("50-CR-2143", 50, "CR", Y_CR, cr_tees, "From P-205", "CIP return, P-204", lbl=(250, Y_CR - 6), nx=30)
header("50-SS-2144", 50, "SS", Y_SB, sb_tees, "SIP steam, 150-SS-2019 (P-204)", "P-205", lbl=(250, Y_SB + 4))

# ---- Seed base system: T-215, P-215A/B, F-215, NaOH header ----
ts = tee("P215_TS", at=(28, 195), branch="right")
td = tee("P215_TD", at=(66, 172), branch="left")
line(sheet, "15-NA-2145", dn=15, fluid="NA", label_at=(38, 160), route=[
    t215["N2"], valve("T215_HV", "BallValve", at=(28, 142)), ts, (28, 208),
    valve("P215_HVSB", "BallValve", at=(50, 208)), pb["N1"]])
line(sheet, "15-NA-2145", id="Line_P215_SA", dn=15, fluid="NA", labels=False, route=[ts.branch, pa["N1"]])
line(sheet, "15-NA-2146", dn=15, fluid="NA", label_at=(78, 182), route=[
    pb["N2"], valve("P215_NRB", "CheckValve", at=(66, 194)), valve("P215_HVDB", "BallValve", at=(66, 185)),
    td, f215["N1"]])
line(sheet, "15-NA-2146", id="Line_P215_DA", dn=15, fluid="NA", labels=False, route=[
    pa["N2"], valve("P215_NRA", "CheckValve", at=(40, 182)), (40, 172), td.branch])
av = {g["k"]: valve(f"AV21{g['k']}2A", "GlobeValve",
                    at=(g["cx"] + g["w"] + (29 if g["k"] < 3 else 31), g["yb"]), tag=f"AV-21{g['k']}2A")
      for g in TRAIN}
na = line(sheet, "15-NA-2147", dn=15, fluid="NA", label_at=(76, 100), route=[
    f215["N2"], (66, Y_NA), R1["t_na"], (R2["cx"] + R2["w"] + 34, Y_NA), (R2["cx"] + R2["w"] + 34, R2["yb"]),
    av[2], *R2["b_base"].items, R2["r"]["N3"]])
line(sheet, "15-NA-2111A", dn=15, fluid="NA", labels=False, route=[
    R1["t_na"].branch, (R1["t_na"].at[0], R1["yb"]), av[1], *R1["b_base"].items, R1["r"]["N3"]])
line(sheet, "25-ML-2131A", dn=25, fluid="ML", label_at=(396, R3["yb"] - 10), route=[
    offpage("in", at=(RIGHT, R3["yb"]), note="Ring main", note_at=(398, R3["yb"] - 4)),
    av[3], *R3["b_base"].items, R3["r"]["N3"]])

# ---- Per-vessel lines ----
for g in TRAIN:
    k, cx, cy, w, h, key, r = g["k"], g["cx"], g["cy"], g["w"], g["h"], g["key"], g["r"]
    dn_m = {1: 25, 2: 50, 3: 100}[k]
    line(sheet, f"{dn_m}-SM-21{k}0A", dn=dn_m, fluid="SM", labels=False,
         route=[g["t_sm"].branch, *g["b_sm"].items, r["N1"]])
    line(sheet, f"25-NS-21{k}2A", dn=25, fluid="NS", labels=False, route=[g["t_ns"].branch, g["fg"]["N1"]])
    line(sheet, f"25-NS-21{k}3A", dn=25, fluid="NS", labels=False, route=[
        g["fg"]["N2"], valve(f"PV21{k}4A", "GlobeValve", at=(g["xg"], 88), tag=f"PV-21{k}4A"),
        (g["xg"], cy - 0.7 * h), r["N6"]])
    line(sheet, f"25-VT-21{k}4A", dn=25, fluid="VT", labels=False, route=[r["N4"], g["fv"]["N1"]])
    line(sheet, f"25-VT-21{k}5A", dn=25, fluid="VT", labels=False, route=[
        g["fv"]["N2"], valve(f"{key}_HVV", "GlobeValve", at=(g["xv"], 67)),
        offpage("out", at=(g["xv"], 60), note="vent atm.", note_at=(g["xv"] + 9, 60))])
    line(sheet, f"25-CS-21{k}6A", dn=25, fluid="CS", labels=False, route=[
        g["t_cs"].branch, valve(f"{key}_HVC", "BallValve", at=(g["xc"], 92)), r["N5"]])
    line(sheet, f"{dn_m}-CR-21{k}7A", dn=dn_m, fluid="CR",
         labels=False, route=[
             r["N9"], valve(f"{key}_HVBV", "BallValve", at=(cx, g["bot"] + 5)), g["t_sip"], g["t_tr"],
             valve(f"{key}_HVCR", "BallValve", at=(cx, g["bot"] + 24)), g["t_cr"].branch])
    line(sheet, "25-SS-2150", id=f"Line_{key}_SIP", dn=25, fluid="SS", labels=False, route=[
        g["t_sb"].branch, valve(f"{key}_HVS", "BallValve", at=(cx - 8, 214)), (cx - 8, g["bot"] + 10),
        g["t_sip"].branch])
    line(sheet, f"25-VT-21{k}8A", dn=25, fluid="VT", labels=False, route=[
        r["N7"], valve(f"{key}_RD", "RuptureDisc", at=(cx - w - 2, cy - 0.8 * h)),
        (cx - w - 6, cy - 0.8 * h),
        offpage("out", at=(cx - w - 6, 86), note="vent", note_at=(cx - w - 6, 80))])
    tv = valve(f"TV21{k}1A", "GlobeValve", at=(cx - w - 9, cy + 0.7 * h), tag=f"TV-21{k}1A")
    line(sheet, f"25-CW-21{k}9A", dn=25, fluid="CW", labels=False, route=[
        offpage("in", at=(cx - w - 18, cy + 0.7 * h), note="CW", note_at=(cx - w - 19, cy + 0.7 * h - 4)), tv,
        r["C1"]])
    line(sheet, f"25-CW-21{k}9A", id=f"Line_{key}_CWR", dn=25, fluid="CW", labels=False, route=[
        r["C2"], offpage("out", at=(cx - w - 12, cy + 0.3 * h), note="CWR", note_at=(cx - w - 12, cy + 0.3 * h + 4))])
    g["tv"] = tv
    for b in g["blocks"]:
        pass

# transfers: R-211A -> R-212A, R-212A -> R-213A, R-213A -> inoculum header
for src, dst, number in ((R1, R2, "25-IN-2118A"), (R2, R3, "50-IN-2128A")):
    yt = src["bot"] + 16
    line(sheet, number, dn=int(number.split("-")[0]), fluid="IN", label_at=(src["cx"] + 14, yt + 3), route=[
        src["t_tr"].branch, valve(f"{src['key']}_HVT", "BallValve", at=(src["cx"] + 8, yt)),
        (dst["xr"], yt), (dst["xr"], dst["yi"]), *dst["b_in"].items, dst["r"]["N2"]])
line(sheet, "100-IN-2138A", dn=100, fluid="IN", label_at=(392, y_out - 5), route=[
    R3["t_tr"].branch, valve("R213A_HVT", "BallValve", at=(R3["cx"] + 9, y_out)), *R3["b_out"].items,
    offpage("out", at=(RIGHT, y_out), note="Inoculum, P-203", note_at=(392, y_out + 5))])

# steam supplies and bleeds of every block
for g in TRAIN:
    g["b_sm"].finish("50-SS-2140")
    g["b_base"].finish("50-SS-2140")
for g in (R2, R3):
    g["b_in"].finish("50-SS-2140")
R3["b_out"].finish("50-SS-2144")

# ---- Instruments ----
for g in TRAIN:
    k, cx, cy, w, h, r = g["k"], g["cx"], g["cy"], g["w"], g["h"], g["r"]
    instrument(sheet, f"TIC-21{k}1A", at=(cx - w - 9, g["bot"] + 8), sensing=r["T1"], signal_to=g["tv"])
    instrument(sheet, f"AIC-21{k}2A", at=(av[k].at[0], cy + 0.65 * h + 5), sensing=r["A1"], signal_to=av[k])
    if k < 3:
        instrument(sheet, f"WI-21{k}3A", at=(cx + w + 8, g["bot"] + 3), sensing=r["W1"])
    else:
        instrument(sheet, "LI-2133A", at=(cx - 0.2 * w, 86), sensing=r["L1"])
    instrument(sheet, f"PIC-21{k}4A", at=(cx + 0.8 * w + 6, 96), sensing=r["P1"],
               signal_to=f"PV21{k}4A")
instrument(sheet, "LI-2151", at=(14 + 30, 100), sensing=t215["L1"])

# ---- Notes ----
note(sheet, "Stages 1 (7 L flask) and 2 (72 L lab fermenter) are grown in the microbiology laboratory "
     "off-plot; stage 2 inoculates R-211A through a steamed sterile coupling (D-013).", at=(10, 250), size=2.0)
note(sheet, "Not aerated (D-019): sterile N2 overlay through F-242A/244A/246A on PIC-21x4A; vents through "
     "F-241A/243A/245A (housing drains not drawn). For the transfer the vent valve closes and PIC-2134A "
     "raises R-213A to the transfer pressure (D-030).", at=(10, 256), size=2.0)
note(sheet, "Steam blocks: two ball valves, steam fed and condensate bled between them, on every medium, base, "
     "inoculum and transfer connection (sterile boundary, D-020); CIP and SIP valves are steamed with the vessel.",
     at=(10, 262), size=2.0)
note(sheet, "Trains B and C on P-205, as train A (typical). Base: NaOH 10 wt% through the sterile filter F-215 "
     "to stages 3 and 4, milk of lime to stage 5 (D-013). Jackets on cooling water.", at=(10, 268), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
