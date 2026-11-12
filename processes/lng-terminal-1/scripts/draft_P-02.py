"""Draft of P-02: LNG tank T-2101 (Phase 1, as built) with its in-tank pumps; the sheet is drawn
by scripts/draft_tank.py with the digit 2.

Generator of P-02 (plant.yaml `generator:`, frame pid/frames/P-02.xml): `cheme regen P-02`
rebuilds the sheet; change draft_tank.py, never the XML (D-021).
"""

import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], sys.argv[1], "2"]
runpy.run_path(str(Path(__file__).resolve().parent / "draft_tank.py"), run_name="__main__")
