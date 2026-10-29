"""Draft of P-114: main utility headers - cooling water supply and return headers with the
branch to every cooling water user of P-103 to P-111, and the flare header collecting the
relief lines of P-104, P-108, P-110 and P-111.

Provenance only: P-114 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-114.py <frame> [<out>]. Lines and DN:
DESIGN.md D-029 (cooling water from the CW duties of process/flowsheet.yaml, 10 K rise).
"""

import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (
    Sheet,
    instrument,
    note,
    offpage,
    tee,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
line = partial(authoring.line, standard="Iso6708")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

EDGE = 400
XS = [40, 80, 120, 160, 200, 240, 280, 320, 360]
# (supply, return, DN, user, sheet)
USERS = [("CWS-1041", "CWR-1042", 300, "K-101", "P-103"),
         ("CWS-1052", "CWR-1053", 700, "E-203", "P-104"),
         ("CWS-1063", "CWR-1064", 400, "E-302", "P-105"),
         ("CWS-1074", "CWR-1075", 400, "E-303", "P-106"),
         ("CWS-1085", "CWR-1086", 500, "E-402", "P-107"),
         ("CWS-1091", "CWR-1092", 450, "K-501", "P-108"),
         ("CWS-1115", "CWR-1116", 350, "E-503", "P-110"),
         ("CWS-1130", "CWR-1131", 700, "E-701", "P-111"),
         ("CWS-1132", "CWR-1133", 125, "K-701", "P-111")]
# (relief line, DN, source, sheet)
RELIEF = [("PG-1055", 150, "PSV-1310", "P-104"), ("PG-1090", 150, "PSV-1704", "P-108"),
          ("PG-1119", 100, "PSV-1911", "P-110"), ("PG-1120", 80, "PSV-1912", "P-110"),
          ("AG-1134", 80, "PSV-2010", "P-111")]
FLARE_XS = [60, 120, 180, 240, 300]

# Cooling water supply header (from the cooling water pumps), branches up to the users
supply = [tee(f"T{s[4:]}", at=(x, 70), branch="up", branch_dn=dn)
          for x, (s, _, dn, _, _) in zip(XS, USERS)]
line(sheet, "CWS-1144", dn=1400, fluid="Cooling water", route=[
    offpage("in", at=(12, 70), note="from CW pumps (battery limit)"), *supply,
    offpage("out", at=(EDGE, 70), note="header end (blind)")], label_at=(20, 80))
for x, t, (s, _, dn, user, sh) in zip(XS, supply, USERS):
    line(sheet, s, dn=dn, fluid="Cooling water", route=[
        t.branch, offpage("out", at=(x, 35), note=f"to {user}, {sh}", note_at=(x - 3, 25),
                          rotation=270)],
        label_at=(x + 11, 52))

# Cooling water return header (to the cooling tower), branches up from the users
ret = [tee(f"T{r[4:]}", at=(x, 150), branch="down", branch_dn=dn)
       for x, (_, r, dn, _, _) in zip(XS, USERS)]
line(sheet, "CWR-1145", dn=1400, fluid="Cooling water", route=[
    offpage("in", at=(12, 150), note="header start (blind)"), *ret,
    offpage("out", at=(EDGE, 150), note="to cooling tower (battery limit)")],
    label_at=(20, 160))
for x, t, (_, r, dn, user, sh) in zip(XS, ret, USERS):
    line(sheet, r, dn=dn, fluid="Cooling water", route=[
        offpage("in", at=(x, 185), note=f"from {user}, {sh}", note_at=(x - 3, 193),
                rotation=270), t.branch],
        label_at=(x + 11, 168))

# Flare header: relief lines from the sheets, to the flare outside the battery limit
flare = [tee(f"T{n.replace('-', '')}", at=(x, 235), branch="up", branch_dn=dn)
         for x, (n, dn, _, _) in zip(FLARE_XS, RELIEF)]
line(sheet, "FLR-1146", dn=300, fluid="Relief gas", route=[
    offpage("in", at=(12, 235), note="header start (blind)"), *flare,
    offpage("out", at=(EDGE, 235), note="to flare (battery limit)")], label_at=(350, 243.5))
for x, t, (n, dn, psv, sh) in zip(FLARE_XS, flare, RELIEF):
    line(sheet, n, dn=dn, fluid="Relief gas", route=[
        offpage("in", at=(x, 208), note=f"from {psv}, {sh}", note_at=(x - 3, 199),
                rotation=90), t.branch],
        label_at=(x + 11, 222))

# Instruments
instrument(sheet, "TI-2301", at=(60, 95), sensing="Line_CWS1144_S2", sensing_at=(60, 70))
instrument(sheet, "PI-2302", at=(380, 95), sensing="Line_CWS1144_S10", sensing_at=(380, 70))
instrument(sheet, "TI-2303", at=(380, 125), sensing="Line_CWR1145_S10", sensing_at=(380, 150))

note(sheet, "Cooling water 10 K rise and up to 2.2 m/s ASSUMED (D-027, D-028); headers DN 1400 for 136.5 MW (D-029)",
     at=(20, 262))
note(sheet, "Flare header DN 300 ASSUMED: no relief loads yet (S8); NH3 relief to a separate NH3 flare system open (S8)",
     at=(20, 269))
note(sheet, "Cooling water pumps, cooling tower and flare outside the battery limit",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
