"""P-301 stage S7 fixes to the S6 review (provenance script, run once; the XML is the source).

    cheme run scripts/fix_P-301_s7.py pid/P-301.xml

Level instrumentation and overfill protection on the acid tank T-301 (S6#1, D-040): LIT-3012
(level with high, low and low-low alarms; LALL stops P-304A/B) and the independent level switch
LSHH-3013, which closes the tanker fill valve XV-3013 (the former hand valve T301_HVF, now
actuated). The trips are in control/cause-effect.yaml (I-301 to I-305).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Sheet, instrument, label, note

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-301.xml")
sheet = Sheet.load(target)

instrument(sheet, "LIT-3012", at=(356, 64), sensing="T301_L1")    # nozzles T301_L1/L2 pasted by hand first
instrument(sheet, "LSHH-3013", at=(306, 46), sensing="T301_L2",
           signal_to="T301_HVF", fail_action="FC")
label(sheet, "T301_HVF", "PipingComponentNumber", at=(316, 30), id="T301_HVF_TagLabel")
note(sheet, "LSHH-3013 closes XV-3013 (I-301);", at=(350, 80), size=2.0)
note(sheet, "LIT-3012 LALL stops P-304A/B (I-302)", at=(350, 84), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
