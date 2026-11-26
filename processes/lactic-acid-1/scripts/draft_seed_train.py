"""Seed trains A, B and C, stages 3 to 5 (provenance script; the XML sheets are the source).

    cheme sheet new P-201 --force          # train A, with the seed base system T-215
    cheme run scripts/draft_seed_train.py pid/P-201.xml
    cheme sheet new P-205                  # train B, typical of train A
    cheme run scripts/draft_seed_train.py pid/P-205.xml
    cheme sheet new P-208                  # train C, typical of train A
    cheme run scripts/draft_seed_train.py pid/P-208.xml

The train letter follows from the sheet file. Seed fermenters R-211x (1 m3), R-212x (10 m3) and
R-213x (107 m3) with agitators, jackets on cooling water, sterile N2 through a restricted-trim
pressure reducer and the inlet filters, vent filters with condensate drains, rupture discs, steam
blocks on the medium, base, inoculum and transfer connections, double-seat CIP inlet valves, the
batch stop of the medium fill, aseptic sampling valves, CIP return and SIP steam (D-013, D-020,
D-030, D-036). Train A carries the seed base system T-215, P-215A/B and F-215. Replaces
scripts/draft_P-201.py.
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
T = {"P-201": "A", "P-205": "B", "P-208": "C"}[target.stem]
PREV = {"A": None, "B": "P-201", "C": "P-205"}[T]
NEXT = {"A": "P-205", "B": "P-208", "C": None}[T]

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
LEFT, RIGHT = 14, 406
Y_SM, Y_NS, Y_CS, Y_NA, Y_SS = 14, 24, 34, 44, 54      # top headers, SIP steam lowest
Y_CR, Y_SB = 224, 236                                   # bottom headers
Y_VB = 60                                              # top of the vertical steam blocks
X_LBL = 85                                              # header labels, clear of the drops


class Block:
    """A steam block: two ball valves, steam fed and condensate bled between them (D-020)."""

    def __init__(self, key, x, y, d=0, steam="up", tag=None):
        self.key, self.steam = key, steam
        if d == 0:                                       # vertical, flow down
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y)),
                          tee(f"{key}_SBS", at=(x, y + 5), branch="left", branch_dn=15),
                          tee(f"{key}_SBB", at=(x, y + 10), branch="left", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x, y + 15), tag=tag)]
            self.ss_x, self.ss_y = x - 8, y + 5
            self.bleed = [(x - 4, y + 10), (x - 4, y + 14), (x - 4, y + 19)]
        else:                                            # horizontal, d = +1 right, -1 left
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y)),
                          tee(f"{key}_SBS", at=(x + 5 * d, y), branch="down" if steam == "down" else "up",
                              branch_dn=15),
                          tee(f"{key}_SBB", at=(x + 10 * d, y), branch="down", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x + 16 * d, y), tag=tag)]
            self.ss_x, self.ss_y = x + 5 * d, y
            self.bleed = [None, (x + 10 * d, y + 5), (x + 10 * d, y + 10)]
        self.ts, self.tb = self.items[1], self.items[2]
        self.hdr = tee(f"{key}_SSH", at=(self.ss_x, Y_SB if steam == "down" else Y_SS),
                       branch="up" if steam == "down" else "down", branch_dn=15)

    def finish(self):
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
    """Seed fermenter R-21k with agitator, nozzles and its own lines; returns its geometry."""
    w, h = 10 * sx, 14.3 * sy
    tag, key = f"R-21{k}{T}", f"R21{k}{T}"
    nz = [Nozzle("N1", (-0.5 * w, -h), dn_m), Nozzle("N4", (0.5 * w, -h), 25),
          Nozzle("N5", (0.15 * w, -h), 25), Nozzle("N6", (w, -0.7 * h), 25),
          Nozzle("N3", (w, -0.15 * h), 15 if k < 3 else 25), Nozzle("N7", (-0.85 * w, -0.8 * h), 25),
          Nozzle("N9", (0, h), dn_out), Nozzle("C1", (-w, 0.7 * h), 25), Nozzle("C2", (-w, 0.3 * h), 25),
          Nozzle("S1", (0.4 * w, 0.95 * h), 15),
          Nozzle("T1", (-0.97 * w, 0.88 * h)), Nozzle("A1", (w, 0.65 * h)), Nozzle("P1", (0.8 * w, -0.85 * h)),
          Nozzle("L1", (-0.2 * w, -h)), Nozzle("W1", (0.85 * w, 0.85 * h))]
    if prev:
        nz.append(Nozzle("N2", (-w, -0.55 * h), prev))
    r = equipment(sheet, "Vessel", tag, shape=VESSEL, at=(cx, cy), scale=(sx, sy), nozzles=nz,
                  label_at=(cx + 0.05 * w, cy - h + 6))
    equipment(sheet, "Agitator", f"A-21{k}{T}", shape="AGITATOR_SHAPE", at=(cx, cy + 0.2 * h),
              label_at=(cx + 0.55 * w, cy + 0.2 * h + 4))
    return dict(k=k, cx=cx, cy=cy, w=w, h=h, top=cy - h, bot=cy + h, r=r, key=key)


sm_tees, ss_tees, ns_tees, cs_tees, cr_tees, sb_tees = [], [], [], [], [], []

# ---- Equipment ----
R1 = seed(1, 115, 125, 2.0, 1.4, 25, 25)
R2 = seed(2, 225, 128, 2.4, 1.8, 50, 50, prev=25)
R3 = seed(3, 341, 132, 2.6, 2.4, 100, 100, prev=50)
TRAIN = [R1, R2, R3]

if T == "A":
    t215 = equipment(sheet, "Tank", "T-215", shape=VESSEL, at=(28, 118),
                     nozzles=[Nozzle("N1", (-5, -14.3), 15), Nozzle("N4", (5, -14.3), 25),
                              Nozzle("N2", (0, 14.3), 15), Nozzle("L1", (10, 8))])
    pa = equipment(sheet, "CentrifugalPump", "P-215A", shape=PUMP, at=(40, 195), label_at=(56, 189),
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
    g["b_sm"] = Block(f"{key}M", xm, Y_VB, tag=f"XV-21{k}8{T}")
    sm_tees.append(g["t_sm"]); ns_tees.append(g["t_ns"]); cs_tees.append(g["t_cs"])
    cr_tees.append(g["t_cr"]); sb_tees.append(g["t_sb"]); ss_tees.append(g["b_sm"].hdr)
    # bottom cluster: bottom valve, SIP tee, transfer tee, CIP return valve
    g["t_sip"] = tee(f"{key}_TSIP", at=(cx, g["bot"] + 10), branch="left", branch_dn=25)
    g["t_tr"] = tee(f"{key}_TTR", at=(cx, g["bot"] + 16), branch="right")
    fv = equipment(sheet, "GasFilter", f"F-24{2 * k - 1}{T}", shape="GAS_FILTER_SHAPE", at=(xv, 79), scale=0.4,
                   nozzles=[Nozzle("N1", (0, 5), 25), Nozzle("N2", (0, -5), 25), Nozzle("D1", (3, 4), 15)],
                   label_at=(xv + 11, 79))
    fg = equipment(sheet, "GasFilter", f"F-24{2 * k}{T}", shape="GAS_FILTER_SHAPE", at=(xg, 74), scale=0.4,
                   nozzles=[Nozzle("N1", (0, -5), 25), Nozzle("N2", (0, 5), 25)], label_at=(xg - 11, 69))
    g["fv"], g["fg"] = fv, fg

# base (NaOH to R-211, R-212; lime to R-213): horizontal blocks from the right
for g in TRAIN:
    x, yb = g["cx"] + g["w"], g["cy"] - 0.15 * g["h"]
    g["yb"] = yb
    g["b_base"] = Block(f"{g['key']}B", x + 23 if g["k"] < 3 else x + 21, yb, d=-1)
    ss_tees.append(g["b_base"].hdr)
R1["t_na"] = tee(f"R211{T}_TNA", at=(R1["cx"] + R1["w"] + 34, Y_NA), branch="down")
R2["t_na"] = tee(f"R212{T}_TNA", at=(R2["cx"] + R2["w"] + 34, Y_NA), branch="down")

# inoculum in (R-212, R-213): horizontal blocks from the left
for g in (R2, R3):
    xr = g["cx"] - g["w"] - 28
    g["xr"], g["yi"] = xr, g["cy"] - 0.55 * g["h"]
    g["b_in"] = Block(f"{g['key']}I", xr + 5, g["yi"], d=1)
    ss_tees.append(g["b_in"].hdr)

# R-213 transfer out to the inoculum header: block steamed from the bottom SIP header
y_out = R3["bot"] + 16
R3["b_out"] = Block(f"R213{T}O", R3["cx"] + 16, y_out, d=1, steam="down")
sb_tees.append(R3["b_out"].hdr)


# ---- Headers: from train A to B (P-205) to C (P-208); C closes them ----
def header(number, dn, fluid, y, tees, text, end, lbl=(X_LBL, None), nx=42):
    """A header left to right; `text` is train A's source, `end` closes it on train C."""
    src = text if T == "A" else f"{number} ({PREV})"
    first = offpage("in", at=(LEFT, y), note=src, note_at=(nx if T == "A" else 33, y - 3))
    if NEXT:
        last = [offpage("out", at=(RIGHT, y), note=f"Train {chr(ord(T) + 1)} ({NEXT})", note_at=(388, y - 3))]
    else:
        last = end(number, y)
    line(sheet, number, dn=dn, fluid=fluid, label_at=(lbl[0], lbl[1] or y + 1.5),
         route=[first, *sorted(tees, key=lambda t: t.at[0]), *last])


def trap_end(number, y):
    return [valve(f"END_{number.replace('-', '_')}", "SteamTrap", at=(RIGHT - 10, y)),
            offpage("out", at=(RIGHT, y), note="End, drain", note_at=(389, y - 3))]


def drain_end(number, y):
    return [valve(f"END_{number.replace('-', '_')}", "BallValve", at=(RIGHT - 10, y)),
            offpage("out", at=(RIGHT, y), note="End, drain", note_at=(389, y - 3))]


def blind_end(number, y):
    return [offpage("out", at=(RIGHT, y), note="Blind flange", note_at=(390, y - 3))]


header("100-SM-2003", 100, "SM", Y_SM, sm_tees, "Sterile medium, 200-SM-2001 (P-203)", trap_end, lbl=(178, None))
header("40-NS-2141", 40, "NS", Y_NS, ns_tees, "N2, 80-NS-2008 (P-203)", blind_end, lbl=(178, None))
header("50-CS-2142", 50, "CS", Y_CS, cs_tees, "CIP supply, 100-CS-2015 (P-204)", drain_end, lbl=(178, None))
header("50-SS-2140", 50, "SS", Y_SS, ss_tees, "SIP steam, 150-SS-2019 (P-204)", trap_end,
       lbl=(X_LBL - 40, Y_SS + 4))
header("50-SS-2144", 50, "SS", Y_SB, sb_tees, "SIP steam, 150-SS-2019 (P-204)", trap_end, lbl=(250, Y_SB + 4))
# CIP return: collected from C (P-208) through B (P-205) and A to the station (P-204)
cr_src = {"A": "From train B (P-205)", "B": "From train C (P-208)", "C": "Header end, SIP steam connection"}[T]
cr_dst = {"A": "CIP return, 150-CR-2017 (P-204)", "B": "Train A (P-201)", "C": "Train B (P-205)"}[T]
line(sheet, "50-CR-2143", dn=50, fluid="CR", label_at=(250, Y_CR - 6), route=[
    offpage("in", at=(LEFT, Y_CR), note=cr_src, note_at=(36, Y_CR - 3)), *sorted(cr_tees, key=lambda t: t.at[0]),
    offpage("out", at=(RIGHT, Y_CR), note=cr_dst, note_at=(384, Y_CR - 3))])

# ---- Seed base: T-215, P-215A/B, F-215 on train A; the NaOH header 15-NA-2147 to B and C ----
av = {g["k"]: valve(f"AV21{g['k']}2{T}", "GlobeValve",
                    at=(g["cx"] + g["w"] + (29 if g["k"] < 3 else 31), g["yb"]), tag=f"AV-21{g['k']}2{T}")
      for g in TRAIN}
if T == "A":
    ts = tee("P215_TS", at=(28, 195), branch="right")
    td = tee("P215_TD", at=(66, 172), branch="left")
    tf = tee("T215_TF", at=(23, 92), branch="left", branch_dn=15)
    line(sheet, "15-NA-2152", dn=15, fluid="NA", labels=False, route=[
        offpage("in", at=(23, 72), note="NaOH 50 wt%, P-223 (P-204)", note_at=(48, 72)),
        valve("T215_HVF", "BallValve", at=(23, 82)), tf, t215["N1"]])
    line(sheet, "15-PW-2153", dn=15, fluid="PW", labels=False, route=[
        offpage("in", at=(LEFT, 92), note="PW", note_at=(15, 88)), tf.branch])
    line(sheet, "25-VT-2154", dn=25, fluid="VT", labels=False, route=[
        t215["N4"], offpage("out", at=(33, 92), note="vent", note_at=(36, 88))])
    line(sheet, "15-NA-2145", dn=15, fluid="NA", label_at=(38, 160), route=[
        t215["N2"], valve("T215_HV", "BallValve", at=(28, 142)), ts, (28, 208),
        valve("P215_HVSB", "BallValve", at=(50, 208)), pb["N1"]])
    line(sheet, "15-NA-2145", id="Line_P215_SA", dn=15, fluid="NA", labels=False, route=[ts.branch, pa["N1"]])
    line(sheet, "15-NA-2146", dn=15, fluid="NA", label_at=(78, 182), route=[
        pb["N2"], valve("P215_NRB", "CheckValve", at=(66, 194)), valve("P215_HVDB", "BallValve", at=(66, 185)),
        td, f215["N1"]])
    line(sheet, "15-NA-2146", id="Line_P215_DA", dn=15, fluid="NA", labels=False, route=[
        pa["N2"], valve("P215_NRA", "CheckValve", at=(40, 182)), (40, 172), td.branch])
    na_first = [f215["N2"], (66, Y_NA)]
else:
    na_first = [offpage("in", at=(LEFT, Y_NA), note=f"NaOH 10 wt%, 15-NA-2147 ({PREV})", note_at=(42, Y_NA - 3))]
na_last = ([offpage("out", at=(RIGHT, Y_NA), note=f"Train {chr(ord(T) + 1)} ({NEXT})", note_at=(388, Y_NA - 3))]
           if NEXT else blind_end("15-NA-2147", Y_NA))
line(sheet, "15-NA-2147", dn=15, fluid="NA", label_at=(76, 100) if T == "A" else (90, Y_NA + 1.5),
     route=[*na_first, R1["t_na"], R2["t_na"], *na_last])
for g in (R1, R2):
    line(sheet, f"15-NA-21{g['k']}1{T}", dn=15, fluid="NA", labels=False, route=[
        g["t_na"].branch, (g["t_na"].at[0], g["yb"]), av[g["k"]], *g["b_base"].items, g["r"]["N3"]])
line(sheet, f"25-ML-2131{T}", dn=25, fluid="ML", label_at=(396, R3["yb"] - 6), route=[
    offpage("in", at=(RIGHT, R3["yb"]), note="Ring main", note_at=(399, R3["yb"] - 14)),
    av[3], *R3["b_base"].items, R3["r"]["N3"]])

# ---- Per-vessel lines ----
for g in TRAIN:
    k, cx, cy, w, h, key, r = g["k"], g["cx"], g["cy"], g["w"], g["h"], g["key"], g["r"]
    dn_m = {1: 25, 2: 50, 3: 100}[k]
    line(sheet, f"{dn_m}-SM-21{k}0{T}", dn=dn_m, fluid="SM", labels=False,
         route=[g["t_sm"].branch, *g["b_sm"].items, r["N1"]])
    line(sheet, f"25-NS-21{k}2{T}", dn=25, fluid="NS", labels=False, route=[
        g["t_ns"].branch, valve(f"PCV21{k}6{T}", "GlobeValve", at=(g["xg"], 61), tag=f"PCV-21{k}6{T}"),
        g["fg"]["N1"]])
    line(sheet, f"25-NS-21{k}3{T}", dn=25, fluid="NS", labels=False, route=[
        g["fg"]["N2"], valve(f"PV21{k}4{T}", "GlobeValve", at=(g["xg"], 88), tag=f"PV-21{k}4{T}"),
        (g["xg"], cy - 0.7 * h), r["N6"]])
    line(sheet, f"25-VT-21{k}4{T}", dn=25, fluid="VT", labels=False, route=[r["N4"], g["fv"]["N1"]])
    line(sheet, f"25-VT-21{k}5{T}", dn=25, fluid="VT", labels=False, route=[
        g["fv"]["N2"], valve(f"{key}_HVV", "GlobeValve", at=(g["xv"], 67)),
        offpage("out", at=(g["xv"], 60), note="vent atm.", note_at=(g["xv"] + 9, 60))])
    line(sheet, "15-CD-2149", id=f"Line_{key}_FCD", dn=15, fluid="CD", labels=False, route=[
        g["fv"]["D1"], (g["xv"] + 5, 83), valve(f"{key}_FST", "SteamTrap", at=(g["xv"] + 5, 86)),
        offpage("out", at=(g["xv"] + 5, 90), note="drain", note_at=(g["xv"] + 9, 93 if k < 3 else 88))])
    line(sheet, f"25-CS-21{k}6{T}", dn=25, fluid="CS", labels=False, route=[
        g["t_cs"].branch, valve(f"XV21{k}9{T}", "BallValve", at=(g["xc"], 92), tag=f"XV-21{k}9{T}"), r["N5"]])
    line(sheet, f"{dn_m}-CR-21{k}7{T}", dn=dn_m, fluid="CR",
         labels=False, route=[
             r["N9"], valve(f"{key}_HVBV", "BallValve", at=(cx, g["bot"] + 5)), g["t_sip"], g["t_tr"],
             valve(f"{key}_HVCR", "BallValve", at=(cx, g["bot"] + 24)), g["t_cr"].branch])
    line(sheet, "25-SS-2150", id=f"Line_{key}_SIP", dn=25, fluid="SS", labels=False, route=[
        g["t_sb"].branch, valve(f"{key}_HVS", "BallValve", at=(cx - 8, 214)), (cx - 8, g["bot"] + 10),
        g["t_sip"].branch])
    line(sheet, f"25-VT-215{4 + k}{T}", dn=25, fluid="VT", labels=False, route=[
        r["N7"], valve(f"{key}_RD", "RuptureDisc", at=(cx - w - 2, cy - 0.8 * h)),
        (cx - w - 6, cy - 0.8 * h),
        offpage("out", at=(cx - w - 6, 86), note="vent", note_at=(cx - w - 6, 80))])
    note(sheet, f"PSE-21{k}5{T}", at={1: (74, cy - 0.8 * h + 1), 2: (196.5, 100), 3: (311, 95)}[k],
         size=2.0)  # RuptureDisc carries no tag
    xs, ys = cx + 0.4 * w, g["bot"] + 6
    line(sheet, f"15-BR-215{7 + k}{T}" if k < 3 else f"15-BR-2160{T}", dn=15, fluid="BR", labels=False, route=[
        r["S1"], (xs, ys), valve(f"{key}_SPV", "BallValve", at=(xs + 4, ys)),
        offpage("out", at=(xs + 9, ys), note="sample, drain", note_at=(xs + 9, ys + 5))])
    tv = valve(f"TV21{k}1{T}", "GlobeValve", at=(cx - w - 9, cy + 0.7 * h), tag=f"TV-21{k}1{T}")
    line(sheet, f"25-CW-21{k}9{T}", dn=25, fluid="CW", labels=False, route=[
        offpage("in", at=(cx - w - 18, cy + 0.7 * h), note="CW", note_at=(cx - w - 19, cy + 0.7 * h - 4)), tv,
        r["C1"]])
    line(sheet, f"25-CW-21{k}9{T}", id=f"Line_{key}_CWR", dn=25, fluid="CW", labels=False, route=[
        r["C2"], offpage("out", at=(cx - w - 12, cy + 0.3 * h), note="CWR", note_at=(cx - w - 12, cy + 0.3 * h + 4))])
    g["tv"] = tv

# transfers: R-211 -> R-212, R-212 -> R-213, R-213 -> inoculum header
for src, dst, number in ((R1, R2, f"25-IN-2118{T}"), (R2, R3, f"50-IN-2128{T}")):
    yt = src["bot"] + 16
    line(sheet, number, dn=int(number.split("-")[0]), fluid="IN", label_at=(src["cx"] + 14, yt + 3), route=[
        src["t_tr"].branch, valve(f"{src['key']}_HVT", "BallValve", at=(src["cx"] + 8, yt)),
        (dst["xr"], yt), (dst["xr"], dst["yi"]), *dst["b_in"].items, dst["r"]["N2"]])
line(sheet, f"100-IN-2138{T}", dn=100, fluid="IN", label_at=(392, y_out - 5), route=[
    R3["t_tr"].branch, valve(f"R213{T}_HVT", "BallValve", at=(R3["cx"] + 9, y_out)), *R3["b_out"].items,
    offpage("out", at=(RIGHT, y_out), note="Inoculum, 100-IN-2004 (P-203)", note_at=(388, y_out + 5))])

# steam supplies and bleeds of every block
for g in TRAIN:
    g["b_sm"].finish()
    g["b_base"].finish()
for g in (R2, R3):
    g["b_in"].finish()
R3["b_out"].finish()

# ---- Instruments ----
for g in TRAIN:
    k, cx, cy, w, h, r = g["k"], g["cx"], g["cy"], g["w"], g["h"], g["r"]
    instrument(sheet, f"TIC-21{k}1{T}", at=(cx - w - 9, g["bot"] + 8), sensing=r["T1"], signal_to=g["tv"])
    instrument(sheet, f"AIC-21{k}2{T}", at=(av[k].at[0], cy + 0.65 * h + 5), sensing=r["A1"], signal_to=av[k])
    if k < 3:
        instrument(sheet, f"WIS-21{k}3{T}", at=(cx + w + 12, g["bot"] + 3), sensing=r["W1"])  # trip in C&E
    else:
        instrument(sheet, f"LIS-2133{T}", at=(cx - 0.2 * w, 86), sensing=r["L1"], signal_to=g["b_sm"].items[3])
    instrument(sheet, f"PIC-21{k}4{T}", at=(cx + 0.8 * w + 6, 100 if k < 3 else 96), sensing=r["P1"],
               signal_to=f"PV21{k}4{T}")
if T == "A":
    instrument(sheet, "LI-2151", at=(14 + 30, 100), sensing=t215["L1"])

# ---- Notes ----
if T == "A":
    note(sheet, "Stages 1 (7 L flask) and 2 (72 L lab fermenter) are grown in the microbiology laboratory "
         "off-plot; stage 2 inoculates R-211A through a steamed sterile coupling (D-013). Trains B (P-205) and "
         "C (P-208) are typicals of train A.", at=(10, 250), size=2.0)
else:
    note(sheet, f"Train {T}: typical of train A (P-201), same sizes, set points, interlocks and notes; stage 2 "
         f"from the laboratory inoculates R-211{T} through a steamed sterile coupling (D-013, D-036). NaOH from "
         "T-215, P-215A/B and F-215 on P-201.", at=(10, 250), size=2.0)
note(sheet, f"Not aerated (D-019): sterile N2 overlay through PCV-21x6{T} (restricted trim; 2.0 barg for "
     f"stages 3, 4; 4.0 barg for stage 5), F-242{T}/244{T}/246{T} and PV-21x4{T} on PIC-21x4{T}; vents through "
     f"F-241{T}/243{T}/245{T} (housing drains to traps). Rupture discs PSE-21x5{T} (D-036).",
     at=(10, 256), size=2.0)
note(sheet, "Steam blocks: two ball valves, steam fed and condensate bled between them, on every medium, base, "
     f"inoculum and transfer connection (sterile boundary, D-020). CIP inlets: double-seat valves XV-21x9{T} with "
     "a steamed leakage chamber; sampling: steam-sterilisable aseptic sampling valves (D-036).",
     at=(10, 262), size=2.0)
note(sheet, f"Fill batch stop: WIS-21x3{T}/LIS-2133{T} high-high closes XV-21x8{T} (C&E I-211 to I-213). Base: "
     "NaOH 10 wt% through the sterile filter F-215 to stages 3 and 4, milk of lime to stage 5 (D-013). "
     "Jackets on cooling water.", at=(10, 268), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
