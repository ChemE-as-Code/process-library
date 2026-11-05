"""Generator of pid/P-02.xml: Skid B of #330 (train 2xx), from the frame pid/frames/P-02.xml.

The sheet is generated (`plant.yaml` `generator:`): change this script or `_skid_pid.py` and
run `cheme regen P-02`, never edit the XML. Run by hand (cheme-as-code's interpreter):

    cheme run scripts/draft_P-02.py pid/P-02.xml
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Sheet

import _skid_pid

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-02.xml")
if not target.exists():
    sys.exit(f"{target} does not exist: cheme regen P-02 starts it from pid/frames/P-02.xml")
sheet = Sheet.load(target)
_skid_pid.draw(sheet, "B")
sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
