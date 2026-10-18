"""Regenerate generated sheets from their empty frames (git 9aa9b38) with scripts/draft_<sheet>.py.

Usage: python3 scripts/regen.py P-03 [P-02 ...] [--out DIR]   (default: pid/)
"""
import subprocess
import sys

args = sys.argv[1:]
out = "pid"
if "--out" in args:
    i = args.index("--out")
    out = args[i + 1]
    del args[i:i + 2]
for sheet in args:
    path = "%s/%s.xml" % (out, sheet)
    frame = subprocess.run(["git", "show", "9aa9b38:pid/%s.xml" % sheet], check=True, capture_output=True).stdout
    open(path, "wb").write(frame)
    subprocess.run([sys.executable, "scripts/draft_%s.py" % sheet, path], check=True)
    subprocess.run(["plantcode", "fmt", path], check=True, capture_output=True)
