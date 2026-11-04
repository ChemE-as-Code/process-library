"""Generator of pid/P-01.xml: Skid A of #330 (train 1xx), from the frame pid/frames/P-01.xml.

The sheet is generated (`plant.yaml` `generator:`): change this script or `_skid_pid.py` and
run `cheme regen P-01`, never edit the XML. Run by hand (cheme-as-code's interpreter):

    cheme run scripts/draft_P-01.py pid/P-01.xml
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Sheet

import _skid_pid

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-01.xml")
if not target.exists():
    sys.exit(f"{target} does not exist: cheme regen P-01 starts it from pid/frames/P-01.xml")
sheet = Sheet.load(target)
_skid_pid.draw(sheet, "A")
sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
