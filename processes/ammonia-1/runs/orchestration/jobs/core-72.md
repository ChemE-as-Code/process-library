# Task: ChemE-as-Code/core#72 (route a line with battery limits at both ends)

Read the issue first: `gh issue view 72`.

In ammonia-1 the cooling-water supply and return headers run from a battery limit along the main
rack to a battery limit (branches to the users tee off them). The router does not route a line
whose both ends are battery limits, so the agent wrote the header routes by hand into
`piping/routing.yaml` (pinned).

Goal: the router routes a line with battery-limit ends at both ends (along the rack/tier its
intent names, or the default), with its branches/tees resolved as for other lines; a clear
finding when it still cannot (naming why). Pinned routes stay pinned and win. Without such lines
behaviour is unchanged (golden files unchanged). Tests (fixture with a BL-to-BL header and two
branches), docs and the bundled skill `pipe-routing`; rerun `scripts/build_skill_manifest.py`
and regenerate `tests/data/init-manifest.txt` per AGENTS.md if a skill changes; an ADR only if
a public file format changes.
Check it on the real case without committing there: copy `~/Developer/test/process-library/processes/ammonia-1` (on main, tag nh3-run-final) into a scratch folder of this worktree (`build/` or similar, ignored, never edit the original), apply the new input there and run this branch's `uv run cheme layout build` / `cheme check`; report in the PR what changed on the real case (findings before/after). Do not touch the other open issues. Follow the preamble's deliverable (PR, CI green, do not merge). On the scratch copy, unpin the cooling-water headers and report whether the router now
routes them, and how the result compares with the hand-written routes (length, clashes).
