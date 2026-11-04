"""Draft of P-07: flare header collecting every relief and vent line of P-01 to P-06, the
nitrogen header and the natural gas header with their branches.

Provenance only: P-07 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-07.py <frame> [<out>]. Lines and DN:
DESIGN.md D-025 (relief loads are the relief study's, S8: the flare header DN is a
placeholder).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import Sheet, instrument, note, offpage, tee  # noqa: E402
from pid_common import EDGE, LEFT, line, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

# (relief or vent line, DN, source, sheet)
RELIEF = [("FL-133", 80, "PSV-118", "P-01"), ("FL-135", 150, "PSV-119", "P-01"),
          ("FL-234", 150, "PSV-214", "P-02"), ("FL-332", 150, "PSV-307", "P-03"),
          ("FL-331", 100, "PSV-308", "P-03"), ("FL-443", 100, "PSV-413", "P-04"),
          ("FL-548", 150, "PSV-514", "P-05"), ("FL-549", 50, "PV-504", "P-05"),
          ("FL-645", 150, "PSV-615", "P-06"), ("FL-646", 50, "PK-201", "P-06")]
FLARE_XS = [40, 75, 110, 145, 180, 215, 250, 285, 320, 355]
FLARE_Y = 205

# ---- flare header: relief and vent lines from the sheets, to the site flare at the battery limit
flare = [tee(f"T{n.replace('-', '')}", at=(x, FLARE_Y), branch="up", branch_dn=dn)
         for x, (n, dn, _, _) in zip(FLARE_XS, RELIEF)]
line(sheet, "FL-701", dn=300, fluid="Relief gas", route=[
    offpage("in", at=(LEFT, FLARE_Y), note="header start (blind)", note_at=(24, 214)), *flare,
    offpage("out", at=(EDGE, FLARE_Y), note="to site flare (B/L)", note_at=(390, 214))],
    label_at=(380, 196))
for i, (x, t, (n, dn, src, sh)) in enumerate(zip(FLARE_XS, flare, RELIEF)):
    line(sheet, n, dn=dn, fluid="Relief gas", route=[
        offpage("in", at=(x, 160), note=f"from {src}, {sh}", note_at=(x, 150 if i % 2 else 142),
                rotation=90), t.branch],
        label_at=(x + 10, 182))

# ---- nitrogen header: to the V-100 blanket (P-01) and the V-202 pad (P-05)
N2 = [("N2-136", "PCV-105", "P-01", 120), ("N2-550", "PCV-505", "P-05", 200)]
n2_tees = [tee(f"T{n.replace('-', '')}", at=(x, 70), branch="up", branch_dn=25)
           for n, _, _, x in N2]
line(sheet, "N2-702", dn=50, fluid="Nitrogen", route=[
    offpage("in", at=(LEFT, 70), note="from site nitrogen (B/L)", note_at=(30, 79)), *n2_tees,
    offpage("out", at=(260, 70), note="header end (blind)", note_at=(272, 79))],
    label_at=(60, 62))
for t, (n, dest, sh, x) in zip(n2_tees, N2):
    line(sheet, n, dn=25, fluid="Nitrogen", route=[
        t.branch, offpage("out", at=(x, 30), note=f"to {dest}, {sh}", note_at=(x, 22),
                          rotation=270)],
        label_at=(x + 10, 50))

# ---- natural gas header: to the H-101 burners (P-01)
ng_tee = tee("T137", at=(120, 115), branch="up", branch_dn=50)
line(sheet, "NG-703", dn=50, fluid="Natural gas", route=[
    offpage("in", at=(LEFT, 115), note="from site natural gas (B/L)", note_at=(32, 124)), ng_tee,
    offpage("out", at=(260, 115), note="header end (blind)", note_at=(272, 124))],
    label_at=(60, 107))
line(sheet, "NG-137", dn=50, fluid="Natural gas", route=[
    ng_tee.branch, offpage("out", at=(120, 92), note="to XV-112, P-01", note_at=(138, 92),
                           rotation=270)],
    label_at=(110, 102))

# ---- instruments
instrument(sheet, "PI-701", at=(230, 50), sensing="Line_N2702_S3", sensing_at=(230, 70))
instrument(sheet, "PI-702", at=(230, 95), sensing="Line_NG703_S2", sensing_at=(230, 115))
instrument(sheet, "PI-703", at=(380, 230), sensing="Line_FL701_S11", sensing_at=(380, FLARE_Y))

note(sheet, "Flare header DN 300 and the branch DN are placeholders: no relief loads yet (S8). Flare "
     "knock-out drum, seal and stack belong to the site flare outside the battery limit", at=(20, 262))
note(sheet, "Continuous purge of the flare header (nitrogen or fuel gas) and the header slope to the "
     "knock-out drum are open for S8 / detail (D-025)", at=(20, 269))
note(sheet, "Nitrogen and natural gas from the site networks; supply pressures ASSUMED (D-025)",
     at=(20, 276))

save(sheet, target)
