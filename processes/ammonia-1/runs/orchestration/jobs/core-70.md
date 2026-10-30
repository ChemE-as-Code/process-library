# Task: ChemE-as-Code/core#70 (buried pipes vs the headroom rule)

Read the issue first: `gh issue view 70`.

The layout headroom rule (`cheme.layout-headroom`) treats every routed pipe as above grade. In
ammonia-1 the buried DN 1400 cooling-water headers cross roads R-5/R-6 at about -3.7 m and are
reported as too low, failing gates layout-3d and layout-detail (the owner had to accept them).

Goal: a project can declare a line (or a segment/route part) as **buried** in
`piping/routing.yaml` (e.g. `buried: {cover_m: ...}` or an intent), and:
1. the headroom rule does not apply to buried parts; a buried route under a road needs at least
   its declared cover (a new finding when the cover is less than a minimum, with the minimum
   ASSUMED/configurable and documented, never invented as a standard value without a source);
2. clash checks treat buried parts against above-grade objects sensibly (no clash with steel or
   equipment above grade), and the MTO can tell buried pipe (e.g. for coating/trench later; at
   least a flag in the take-off);
3. without the new field behaviour is unchanged (golden files unchanged).
Schema, validation findings with file/line/rule/hint, tests (fixture before/after), docs and the
bundled skill `pipe-routing` (and `layout-yaml` if relevant); rerun
`scripts/build_skill_manifest.py` and regenerate `tests/data/init-manifest.txt` per AGENTS.md;
an ADR (public file format change), next free number after merging origin/main.
Check it on the real case without committing there: copy `~/Developer/test/process-library/processes/ammonia-1` (on main, tag nh3-run-final) into a scratch folder of this worktree (`build/` or similar, ignored, never edit the original), apply the new input there and run this branch's `uv run cheme layout build` / `cheme check`; report in the PR what changed on the real case (findings before/after). Do not touch the other open issues. Follow the preamble's deliverable (PR, CI green, do not merge).
