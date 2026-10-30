# Task: ChemE-as-Code/core#73 (motor cable entry point)

Read the issue first: `gh issue view 73` (and #71, #72 for context; they are not in scope).

Problem seen in the ammonia-1 run (process-library#86, PR process-library#257, branch
`stage/basic-layout`, `processes/ammonia-1`): `cheme layout build` routes each motor's power cable
tray so that its last horizontal run ends **over the motor**. For the compressors K-101, K-102,
K-103 and K-701 (and K-501) that tray lies inside the crane lift lane, which covers the whole
machine footprint, so `cheme layout lifting` reports the lane blocked and gate `lifting-study`
fails. A project has no way to say where a motor's cable enters (the terminal box side/position),
so the tray route cannot be steered clear.

Goal: let a project give a motor's **cable entry point** in `electrical/electrical-list.yaml`
(e.g. a side of the driven item's footprint and/or an offset or absolute position, and optionally
the elevation), and make the tray build end the tray at that point, beside the machine, with the
final cable drop (not a tray) to the terminal box, so a lift lane over the machine stays clear.
Without the new field the behaviour must stay exactly as today (golden files unchanged).

Acceptance checks:
1. Schema: the new optional field in the `electrical` kind (`cheme schema electrical`), with
   validation errors naming file, line, rule id and hint for an impossible entry point.
2. Tray build honours it; the cable schedule length includes the drop; the lifting study no
   longer counts a cable drop outside the lane as a blocker, and still counts any tray inside it.
3. Tests: a small fixture with a machine, a lift lane and a motor tray, before/after.
4. Docs and the bundled skill `electrical-cabling` (and `structures-access` if it mentions lifting
   blockers) explain the field; rerun `scripts/build_skill_manifest.py` and regenerate
   `tests/data/init-manifest.txt` as AGENTS.md says.
5. An ADR if this changes a public file format (it does: a new field); next free number.
6. Check it on the real case without committing there: in a scratch copy of
   `~/Developer/test/wt/nh3-basic-layout/processes/ammonia-1` (copy it into `build/` or /tmp of
   this worktree, never edit the original), add entry points for K-101, K-102, K-103, K-701 and
   run this branch's `uv run cheme layout build` and `cheme layout lifting` there; report in the
   PR how many lanes remain blocked and why.

Do not touch #71/#72. Follow the preamble's deliverable (PR, CI green, do not merge).
