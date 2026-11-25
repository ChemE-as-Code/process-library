"""P-202 production fermenter R-201A, the typical of R-201A to P (provenance script; the XML is the source).

    cheme sheet new P-202 --title 'Production fermenter R-201A (typical)'
    cheme run scripts/draft_P-202.py pid/P-202.xml

R-201A with agitator A-201A, half-pipe coils on the tempered-water loop of P-201A (split range:
LP steam and cooling-water injection), pH on two probes with the milk-of-lime dosing branch and
its flush, radar level with an independent high-high trip of the fill, headspace pressure on the
vent back-pressure valve with a self-acting N2 make-up, sterile vent and inlet gas filters,
rupture disc, vacuum relief, aseptic sampling, steam blocks on every sterile entry, CIP and SIP
(D-016 to D-021, D-031). The second split-range signal of TIC-2011A (to TV-2011B) is pasted from
`cheme fragment signal` after the run.
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

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-202.xml")
sheet = Sheet.load(target)

VESSEL = "VESSEL_WITH_DISHED_HEADS_SHAPE"
LEFT, RIGHT = 14, 406
CX, CY, SX, SY = 200, 128, 4.0, 4.9
W, H = 10 * SX, 14.3 * SY                                # half width 40, half height 70


class Block:
    """A steam block: two ball valves, steam fed and condensate bled between them (D-020).

    d = +1 / -1: horizontal, flow right / left, steam from above and bleed below;
    d = 0: vertical, flow down, steam and bleed on the left.
    """

    def __init__(self, key, x, y, d=0, tags=(None, None)):
        self.key = key
        if d == 0:
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y), tag=tags[0]),
                          tee(f"{key}_SBS", at=(x, y + 5), branch="left", branch_dn=15),
                          tee(f"{key}_SBB", at=(x, y + 10), branch="left", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x, y + 15), tag=tags[1])]
            self.steam = (x - 10, y + 5)
            self.bleed = [(x - 4, y + 10), (x - 4, y + 14), (x - 4, y + 19)]
        else:
            self.items = [valve(f"{key}_SB1", "BallValve", at=(x, y), tag=tags[0]),
                          tee(f"{key}_SBS", at=(x + 5 * d, y), branch="up", branch_dn=15),
                          tee(f"{key}_SBB", at=(x + 10 * d, y), branch="down", branch_dn=15),
                          valve(f"{key}_SB2", "BallValve", at=(x + 16 * d, y), tag=tags[1])]
            self.steam = (x + 5 * d, y - 7)
            self.bleed = [None, (x + 10 * d, y + 5), (x + 10 * d, y + 10)]
        self.ts, self.tb = self.items[1], self.items[2]

    def finish(self, text_at=None):
        sx, sy = self.steam
        line(sheet, "15-SS-2033A", id=f"Line_{self.key}_SS", dn=15, fluid="SS", labels=False,
             route=[offpage("in", at=self.steam, note="SS", note_at=text_at or (sx - 5, sy - 2)), self.ts.branch])
        b1, trap, end = self.bleed
        route = [self.tb.branch] + ([b1] if b1 else []) + [
            valve(f"{self.key}_ST", "SteamTrap", at=trap), offpage("out", at=end, note="drain")]
        line(sheet, "15-CD-2034A", id=f"Line_{self.key}_CD", dn=15, fluid="CD", labels=False, route=route)


# ---- Equipment ----
r = equipment(sheet, "Vessel", "R-201A", shape=VESSEL, at=(CX, CY), scale=(SX, SY), nozzles=[
    Nozzle("N1", (-W, -44), 200), Nozzle("N2", (-W, -28), 100), Nozzle("N5", (-14, -69.5), 100),
    Nozzle("L1", (-34, -66)), Nozzle("P1", (22, -68.6)), Nozzle("P2", (32, -66.6)),   # on the 2:1 head
    Nozzle("N4", (W, -62), 150), Nozzle("N7", (W, -46), 150), Nozzle("N6", (W, -30), 150),
    Nozzle("S1", (W, 18), 25), Nozzle("A1", (W, 36)), Nozzle("A2", (W, 48)), Nozzle("N3", (W, 56), 25),
    Nozzle("LH", (-W, -58)), Nozzle("C2", (-W, -2), 150), Nozzle("T1", (-W, 22)), Nozzle("T2", (-W, 37)),
    Nozzle("C1", (-W, 56), 150), Nozzle("N9", (0, H), 200)],
    label_at=(CX + 4, CY - H + 8))
equipment(sheet, "Agitator", "A-201A", shape="AGITATOR_SHAPE", at=(CX, CY + 14), scale=2.0,
          label_at=(CX + 22, CY + 20))
pump = equipment(sheet, "CentrifugalPump", "P-201A", shape="CENTRIFUGAL_PUMP_SHAPE", at=(80, 195),
                 nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 150)], label_at=(96, 200))
fv = equipment(sheet, "GasFilter", "F-201A", shape="GAS_FILTER_SHAPE", at=(290, 50), scale=0.6,
               nozzles=[Nozzle("N1", (0, 7.5), 150), Nozzle("N2", (0, -7.5), 150), Nozzle("D1", (4, 6), 15)],
               label_at=(278, 46))
fg = equipment(sheet, "GasFilter", "F-202A", shape="GAS_FILTER_SHAPE", at=(330, 110), scale=0.6,
               nozzles=[Nozzle("N1", (0, 7.5), 150), Nozzle("N2", (0, -7.5), 150), Nozzle("D1", (-4, 6), 15)],
               label_at=(344, 106))

# ---- Sterile medium and inoculum (left shell), with steam blocks ----
b_sm = Block("SM", 104, 84, d=1, tags=("XV-2033A", "XV-2034A"))
line(sheet, "200-SM-2002A", dn=200, fluid="SM", label_at=(78, 89), route=[
    offpage("in", at=(LEFT, 84), note="Sterile medium, 200-SM-2001 (P-203)", note_at=(48, 80)),
    *b_sm.items, r["N1"]])
b_in = Block("IN", 120, 100, d=1)
line(sheet, "100-IN-2005A", dn=100, fluid="IN", label_at=(30, 105), route=[
    offpage("in", at=(LEFT, 100), note="Inoculum, 100-IN-2004 (P-203)", note_at=(36, 96)),
    *b_in.items, r["N2"]])

# ---- CIP supply through the spray device, head SIP steam into the same line (top) ----
b_cs = Block("CS", 186, 22)
t_sip = tee("CS_TSIP", at=(186, 46), branch="right", branch_dn=100)
line(sheet, "100-CS-2016A", dn=100, fluid="CS", label_at=(170, 40), route=[
    offpage("in", at=(186, LEFT), note="CIP supply, 100-CS-2015 (P-204)", note_at=(161, 14)),
    *b_cs.items, t_sip, r["N5"]])
line(sheet, "100-SS-2020A", dn=100, fluid="SS", label_at=(209, 38), route=[
    offpage("in", at=(196, LEFT), note="SIP steam, 150-SS-2019 (P-204)", note_at=(226, 14)),
    valve("SS_HVH", "BallValve", at=(196, 30)), (196, 46), t_sip.branch])

# ---- Vent: F-201A, back-pressure valve; CIP bypass of the filter; rupture disc ----
t_byp = tee("VT_TB", at=(254, 66), branch="up", branch_dn=100)
line(sheet, "150-VT-2006A", dn=150, fluid="VT", label_at=(262, 71), route=[
    r["N4"], t_byp, valve("VT_XV2043A", "ButterflyValve", at=(272, 66), tag="XV-2043A"), (290, 66), fv["N1"]])
pv = valve("VT_PV2041A", "GlobeValve", at=(318, 34), tag="PV-2041A")
line(sheet, "150-VT-2007A", dn=150, fluid="VT", label_at=(350, 38), route=[
    fv["N2"], (290, 34), pv, offpage("out", at=(RIGHT, 34), note="To atmosphere at a safe height",
                                     note_at=(381, 30))])
line(sheet, "100-VT-2028A", dn=100, fluid="VT", labels=False, route=[
    t_byp.branch, valve("VT_XV2044A", "ButterflyValve", at=(254, 57), tag="XV-2044A"),
    offpage("out", at=(254, 48), note="CIP vent", note_at=(258, 46))])
line(sheet, "150-VT-2027A", dn=150, fluid="VT", label_at=(352, 87), route=[
    r["N7"], valve("VT_PSE2045A", "RuptureDisc", at=(252, 82)),
    offpage("out", at=(RIGHT, 82), note="Relief to a safe location", note_at=(385, 78))])
note(sheet, "PSE-2045A", at=(246, 77), size=2.0)          # RuptureDisc carries no tag in pyDEXPI
line(sheet, "15-CD-2034A", id="Line_F201A_CD", dn=15, fluid="CD", labels=False, route=[
    fv["D1"], (300, 56), valve("F201A_ST", "SteamTrap", at=(300, 60)), offpage("out", at=(300, 65), note="drain")])

# ---- N2 overlay through F-202A, vacuum relief admitting air through the same filter ----
t_vac = tee("NS_TV", at=(330, 124), branch="right", branch_dn=50)
line(sheet, "150-NS-2009A", dn=150, fluid="NS", label_at=(280, 90), route=[fg["N2"], (330, 98), r["N6"]])
line(sheet, "150-NS-2026A", dn=150, fluid="NS", labels=False, route=[
    offpage("in", at=(330, 146), note="Air, atm. (vacuum break)", note_at=(353, 147)),
    valve("NS_PSV2046A", "CheckValve", at=(330, 135), tag="PSV-2046A"), t_vac, fg["N1"]])
line(sheet, "50-NS-2025A", dn=50, fluid="NS", label_at=(372, 129), route=[
    offpage("in", at=(RIGHT, 124), note="N2, 80-NS-2008 (P-203)", note_at=(390, 120)),
    valve("NS_HV", "BallValve", at=(394, 124)), valve("NS_PCV2042A", "GlobeValve", at=(366, 124), tag="PCV-2042A"),
    t_vac.branch])
line(sheet, "15-CD-2034A", id="Line_F202A_CD", dn=15, fluid="CD", labels=False, route=[
    fg["D1"], (320, 116), valve("F202A_ST", "SteamTrap", at=(320, 121)), offpage("out", at=(320, 127), note="drain")])

# ---- Aseptic sampling valve, steam flushed ----
t_smp = tee("SP_TS", at=(258, 146), branch="up", branch_dn=15)
line(sheet, "25-BR-2035A", dn=25, fluid="BR", labels=False, route=[
    r["S1"], valve("SP_HV", "BallValve", at=(248, 146)), t_smp, valve("SP_HV2", "BallValve", at=(266, 146)),
    offpage("out", at=(276, 146), note="Sample, drain", note_at=(274, 141))])
line(sheet, "15-SS-2033A", id="Line_SP_SS", dn=15, fluid="SS", labels=False, route=[
    offpage("in", at=(258, 139), note="SS", note_at=(253, 137)), t_smp.branch])

# ---- Milk-of-lime dosing branch with flush and steam block ----
av = valve("ML_AV2021A", "GlobeValve", at=(356, 184), tag="AV-2021A")
t_fl = tee("ML_TF", at=(330, 184), branch="down", branch_dn=25)
b_ml = Block("ML", 300, 184, d=-1)
line(sheet, "25-ML-2024A", dn=25, fluid="ML", label_at=(372, 189), route=[
    offpage("in", at=(RIGHT, 184), note="Milk of lime, 100-ML-1102 (P-203)", note_at=(386, 179)),
    valve("ML_HV", "BallValve", at=(394, 184)), av, t_fl, *b_ml.items, r["N3"]])
line(sheet, "25-PW-2032A", dn=25, fluid="PW", labels=False, route=[
    offpage("in", at=(330, 204), note="Flush water", note_at=(346, 205)),
    valve("PW_NR", "CheckValve", at=(330, 198)), valve("PW_HV", "BallValve", at=(330, 191)), t_fl.branch])

# ---- Tempered-water loop: P-201A through the half-pipe coils; overflow, CW and LP steam injection ----
t_ov = tee("TW_TOV", at=(60, 134), branch="left", branch_dn=80)
t_cw = tee("TW_TCW", at=(60, 146), branch="left", branch_dn=80)
t_ls = tee("TW_TLS", at=(60, 166), branch="left", branch_dn=25)
line(sheet, "150-TW-2023A", dn=150, fluid="TW", label_at=(100, 118), route=[
    r["C2"], (60, 126), t_ov, t_cw, t_ls, (60, 195), pump["N1"]])
tw_sup = line(sheet, "150-TW-2022A", dn=150, fluid="TW", label_at=(118, 188), route=[
    pump["N2"], (80, 184), r["C1"]])
line(sheet, "80-CW-2030A", dn=80, fluid="CW", labels=False, route=[
    t_ov.branch, offpage("out", at=(LEFT, 134), note="CWR", note_at=(20, 131))])
tv_cw = valve("TW_TV2011A", "GlobeValve", at=(36, 146), tag="TV-2011A")
line(sheet, "80-CW-2029A", dn=80, fluid="CW", labels=False, route=[
    offpage("in", at=(LEFT, 146), note="CW", note_at=(20, 143)), tv_cw, t_cw.branch])
tv_ls = valve("TW_TV2011B", "GlobeValve", at=(36, 166), tag="TV-2011B")
line(sheet, "25-LS-2031A", dn=25, fluid="LS", labels=False, route=[
    offpage("in", at=(LEFT, 166), note="LP steam", note_at=(18, 171)), tv_ls,
    valve("LS_NR", "CheckValve", at=(48, 166)), t_ls.branch])

# ---- Bottom valve cluster: bottom SIP steam, CIP return, harvest (steam blocks) ----
t_bs = tee("BR_TSIP", at=(CX, 209), branch="left", branch_dn=80)
t_cr = tee("BR_TCR", at=(CX, 215), branch="right", branch_dn=100)
b_br = Block("BR", CX, 221)
harvest = line(sheet, "200-BR-2010A", dn=200, fluid="BR", label_at=(300, 236), route=[
    r["N9"], valve("BR_HVBV", "BallValve", at=(CX, 203)), t_bs, t_cr, *b_br.items, (CX, 244),
    offpage("out", at=(RIGHT, 244), note="Harvest header, 250-BR-2011 (P-203)", note_at=(381, 248))])
b_cr = Block("CR", 210, 215, d=1)
line(sheet, "100-CR-2018A", dn=100, fluid="CR", label_at=(300, 220), route=[
    t_cr.branch, *b_cr.items,
    offpage("out", at=(RIGHT, 215), note="CIP return, 150-CR-2017 (P-204)", note_at=(382, 211))])
line(sheet, "80-SS-2021A", dn=80, fluid="SS", label_at=(110, 213), route=[
    offpage("in", at=(LEFT, 209), note="SIP steam, 150-SS-2019 (P-204)", note_at=(46, 205)),
    valve("SS_HVB", "BallValve", at=(150, 209)), t_bs.branch])

for b in (b_in, b_cs, b_ml, b_br):
    b.finish()
b_sm.finish(text_at=(114, 76))
b_cr.finish(text_at=(221, 207))

# ---- Instruments ----
instrument(sheet, "TIC-2011A", at=(36, 156), sensing=r["T1"], signal_to=tv_cw)
instrument(sheet, "TSHH-2012A", at=(122, 165), sensing=r["T2"])
instrument(sheet, "FSLL-2014A", at=(104, 172), sensing=tw_sup, sensing_at=(104, 184))
instrument(sheet, "TI-2015A", at=(176, 218), sensing=harvest, sensing_at=(CX, 218))
instrument(sheet, "AIC-2021A", at=(298, 164), sensing=r["A1"], signal_to=av)
instrument(sheet, "AI-2022A", at=(264, 176), sensing=r["A2"])
instrument(sheet, "LIC-2031A", at=(140, 50), sensing=r["L1"], signal_to=b_sm.items[0])
instrument(sheet, "LSHH-2032A", at=(140, 68), sensing=r["LH"], signal_to=b_sm.items[3])
instrument(sheet, "PIC-2041A", at=(222, 26), sensing=r["P1"], signal_to=pv)
instrument(sheet, "PALL-2043A", at=(240, 44), sensing=r["P2"])
note(sheet, "I-201, I-202: stop A-201A", at=(128, 176), size=2.0)
note(sheet, "I-203", at=(148, 74), size=2.0)

# ---- Notes ----
note(sheet, "Typical of R-201A to R-201P: B to P are instrumented as R-201A (P-203). 1291 m3, 1033 m3 of broth, "
     "323 K, design 2.5 / -0.3 barg, 150 C (D-016). A-201A: top entry, 160 kW, gearbox, double mechanical seal "
     "with a sterile barrier above headspace pressure.", at=(10, 254), size=2.0)
note(sheet, "NOT AERATED: anaerobic / microaerophilic fermentation, no sparger and no air train (D-019). Sterile N2 "
     "overlay at 0.3 barg: PIC-2041A on the vent back-pressure valve, PCV-2042A self-acting N2 make-up at 0.25 barg.",
     at=(10, 260), size=2.0)
note(sheet, "STERILE BOUNDARY: steam blocks (SS steam in, CD bleed) on medium, inoculum, lime, CIP supply, CIP return "
     "and harvest; sterile class SS316L inside (D-020). Lime is not sterile and crosses it when dosing (D-018).",
     at=(10, 266), size=2.0)
note(sheet, "TIC-2011A split range: TV-2011B LP steam (heat-up, lag phase), TV-2011A CW (D-017, D-031). Trips: "
     "I-201 TSHH-2012A, I-202 FSLL-2014A stop A-201A; I-203 LSHH-2032A closes XV-2034A; I-204 PALL-2043A.",
     at=(10, 272), size=2.0)
note(sheet, "F-201A isolated by XV-2043A and bypassed by XV-2044A during CIP; SIP steam at the head (through the "
     "spray line) and the bottom; PSE-2045A, PSV-2046A in piping/special-items.yaml (D-031).", at=(10, 278), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
