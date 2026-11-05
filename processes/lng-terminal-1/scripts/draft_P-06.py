"""Draft of P-06: Berth 1 loading arms (Phase 2); the sheet is drawn by scripts/draft_berth.py
with the digit 6.

Generator of P-06 (plant.yaml `generator:`, frame pid/frames/P-06.xml): `cheme regen P-06`
rebuilds the sheet; change draft_berth.py, never the XML (D-021).
"""

import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], sys.argv[1], "6"]
runpy.run_path(str(Path(__file__).resolve().parent / "draft_berth.py"), run_name="__main__")
