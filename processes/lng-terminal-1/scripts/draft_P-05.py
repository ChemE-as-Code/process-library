"""Draft of P-05: Berth 2 loading arms (as built); the sheet is drawn by scripts/draft_berth.py
with the digit 5.

Generator of P-05 (plant.yaml `generator:`, frame pid/frames/P-05.xml): `cheme regen P-05`
rebuilds the sheet; change draft_berth.py, never the XML (D-021).
"""

import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], sys.argv[1], "5"]
runpy.run_path(str(Path(__file__).resolve().parent / "draft_berth.py"), run_name="__main__")
