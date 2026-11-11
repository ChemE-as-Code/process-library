"""Draft of P-08: cooling water supply and return headers with the branch to every cooling
water user of P-02 to P-06, the LP, MP and HP steam headers to the three reboilers, and the
condensate header.

Provenance only: P-08 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-08.py <frame> [<out>]. Lines and DN:
DESIGN.md D-025 (cooling water from the CW duties of process/flowsheet.yaml, 10 K rise).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import Sheet, instrument, note, offpage, tee  # noqa: E402
from pid_common import EDGE, LEFT, line, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

# (supply, return, DN, user, sheet)
USERS = [("CWS-230", "CWR-231", 350, "E-102", "P-02"),
         ("CWS-333", "CWR-334", 80, "E-103", "P-03"),
         ("CWS-440", "CWR-441", 65, "E-201", "P-04"),
         ("CWS-542", "CWR-543", 300, "E-203", "P-05"),
         ("CWS-545", "CWR-546", 100, "E-207", "P-05"),
         ("CWS-642", "CWR-643", 150, "E-205", "P-06")]
XS = [55, 115, 175, 235, 295, 355]

# ---- cooling water supply header (from the site cooling water system), branches up
supply = [tee(f"T{s[4:]}S", at=(x, 55), branch="up", branch_dn=dn)
          for x, (s, _, dn, _, _) in zip(XS, USERS)]
line(sheet, "CWS-801", dn=500, fluid="Cooling water", route=[
    offpage("in", at=(LEFT, 55), note="from CW supply (B/L)", note_at=(26, 64)), *supply,
    offpage("out", at=(EDGE, 55), note="header end (blind)", note_at=(392, 64))],
    label_at=(30, 47))
for x, t, (s, _, dn, user, sh) in zip(XS, supply, USERS):
    line(sheet, s, dn=dn, fluid="Cooling water", route=[
        t.branch, offpage("out", at=(x, 24), note=f"to {user}, {sh}", note_at=(x, 15),
                          rotation=270)],
        label_at=(x + 11, 40))

# ---- cooling water return header (to the site cooling water system), branches from above
ret = [tee(f"T{r[4:]}R", at=(x, 115), branch="up", branch_dn=dn)
       for x, (_, r, dn, _, _) in zip(XS, USERS)]
line(sheet, "CWR-802", dn=500, fluid="Cooling water", route=[
    offpage("in", at=(LEFT, 115), note="header start (blind)", note_at=(26, 124)), *ret,
    offpage("out", at=(EDGE, 115), note="to CW return (B/L)", note_at=(390, 124))],
    label_at=(30, 107))
for x, t, (_, r, dn, user, sh) in zip(XS, ret, USERS):
    line(sheet, r, dn=dn, fluid="Cooling water", route=[
        offpage("in", at=(x, 85), note=f"from {user}, {sh}", note_at=(x, 76), rotation=90),
        t.branch],
        label_at=(x + 11, 100))

# ---- steam headers (from the site steam system), one reboiler each
STEAM = [("LS-803", "LS-540", 250, 250, "LP steam", "TV-502", "P-05", 150),
         ("MS-804", "MS-439", 100, 100, "MP steam", "TV-402", "P-04", 180),
         ("HS-805", "HS-640", 50, 50, "HP steam", "TV-602", "P-06", 210)]
for header, branch, hdn, bdn, fluid, dest, sh, y in STEAM:
    t = tee(f"T{branch.replace('-', '')}", at=(130, y), branch="down", branch_dn=bdn)
    line(sheet, header, dn=hdn, fluid=fluid, route=[
        offpage("in", at=(LEFT, y), note=f"from site {fluid} (B/L)", note_at=(32, y - 8)), t,
        offpage("out", at=(200, y), note="header end (blind)", note_at=(214, y - 8))],
        label_at=(80, y - 8))
    line(sheet, branch, dn=bdn, fluid=fluid, route=[
        t.branch, offpage("out", at=(130, y + 16), note=f"to {dest}, {sh}", note_at=(152, y + 16),
                          rotation=90)],
        label_at=(118, y + 9))

# ---- condensate header (to the site condensate return)
COND = [("CD-444", 50, "ST-444", "P-04", 270), ("CD-541", 50, "ST-541", "P-05", 310),
        ("CD-641", 25, "ST-641", "P-06", 350)]
cd_tees = [tee(f"T{n.replace('-', '')}", at=(x, 225), branch="up", branch_dn=dn)
           for n, dn, _, _, x in COND]
line(sheet, "CD-806", dn=80, fluid="Condensate", route=[
    offpage("in", at=(240, 225), note="header start (blind)", note_at=(240, 234)), *cd_tees,
    offpage("out", at=(EDGE, 225), note="to condensate return (B/L)", note_at=(388, 234))],
    label_at=(250, 217))
for t, (n, dn, src, sh, x) in zip(cd_tees, COND):
    line(sheet, n, dn=dn, fluid="Condensate", route=[
        offpage("in", at=(x, 190), note=f"from {src}, {sh}", note_at=(x, 181), rotation=90),
        t.branch],
        label_at=(x + 10, 206))

# ---- instruments
instrument(sheet, "TI-801", at=(385, 35), sensing="Line_CWS801_S7", sensing_at=(385, 55))
instrument(sheet, "PI-802", at=(85, 72), sensing="Line_CWS801_S2", sensing_at=(85, 55))
instrument(sheet, "TI-803", at=(385, 95), sensing="Line_CWR802_S7", sensing_at=(385, 115))

note(sheet, "Cooling water 25 -> 35 degC (design basis) at 1.5 m/s, ASSUMED: CWS-801 / CWR-802 DN 500 for "
     "10.8 MW (D-025). Cooling tower and pumps belong to the site", at=(20, 262))
note(sheet, "Steam at the design-basis levels LP 450, MP 1500, HP 4200 kPa(a) from the site; letdown and "
     "condensate flash at the utility interface A-800 open (D-025)", at=(20, 269))
note(sheet, "Branch DN as on the consumer sheets; header DN and supply pressures ASSUMED (D-025)",
     at=(20, 276))

save(sheet, target)
