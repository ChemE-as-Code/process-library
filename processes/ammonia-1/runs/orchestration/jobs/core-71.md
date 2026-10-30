# Task: ChemE-as-Code/core#71 (several power trays per rack)

Read the issue first: `gh issue view 71`.

In ammonia-1 the main-rack power tray is 53-54 % full against a 30 % fill limit (10 kV cables of
three large compressors). The tray-fill finding says to widen or split the tray, but
`electrical/tray-rules.yaml` allows only one power tray per rack, so the second tray cannot be
declared; the only way out was accepting the finding (gate electrical fails).

Goal: a project can declare **several power trays per rack** (e.g. a count or a list of power
tray tiers/positions per rack, optionally by voltage class: HV/MV separate from LV, as is common
practice; say where that practice is stated if you cite it), and the tray build distributes the
cables over them (deterministic: e.g. by voltage class first, then fill), each tray checked for
fill and separation; the cable schedule names the tray of each cable. The fill finding's hint
then names the real way out. Without the new field behaviour is unchanged (golden files
unchanged). Schema, validation findings with file/line/rule/hint, tests, docs and the bundled
skill `electrical-cabling`; rerun `scripts/build_skill_manifest.py` and regenerate
`tests/data/init-manifest.txt` per AGENTS.md; an ADR (public file format change), next free
number after merging origin/main.
Check it on the real case without committing there: copy `~/Developer/test/process-library/processes/ammonia-1` (on main, tag nh3-run-final) into a scratch folder of this worktree (`build/` or similar, ignored, never edit the original), apply the new input there and run this branch's `uv run cheme layout build` / `cheme check`; report in the PR what changed on the real case (findings before/after). Do not touch the other open issues. Follow the preamble's deliverable (PR, CI green, do not merge). Report whether the ammonia-1 `electrical` gate passes with a second power tray.
