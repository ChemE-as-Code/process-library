"""Draft of P-03: LNG tank T-3101 (Phase 2) with its in-tank pumps; the sheet is drawn by
scripts/draft_tank.py with the digit 3.

Generator of P-03 (plant.yaml `generator:`, frame pid/frames/P-03.xml): `cheme regen P-03`
rebuilds the sheet; change draft_tank.py, never the XML (D-021).
"""

import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], sys.argv[1], "3"]
runpy.run_path(str(Path(__file__).resolve().parent / "draft_tank.py"), run_name="__main__")
