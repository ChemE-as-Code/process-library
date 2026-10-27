You are developing a new case study in the ChemE-as-Code process library: methanol, issue
ChemE-as-Code/process-library#118. Your working directory is the new, freshly initialised process
folder `processes/methanol-1/` (created by `cheme init` from current core main) on git branch
`case/methanol-1`. Follow this folder's CLAUDE.md/AGENTS.md and the library root CLAUDE.md
(sources and licences: no third-party tables/figures, facts with sources, estimates marked ASSUMED).

## Read first
- `gh issue view 118 --repo ChemE-as-Code/process-library --comments` (the issue body and the
  27 October 2026 literature notes and handoff contract). Read-only: do not comment on, edit or
  close any GitHub issue or PR.
- `processes/asu-1/` (one level up) as a worked example of the conventions; never modify it.
- The skills `tech-petchem-methanol-and-syngas`, `route-selection`, `flowsheet-development`,
  `process-design`, `process-simulation`, `thermodynamic-model-selection`, `reactions`.

## Scope of this run: design basis to a balanced PFD
Natural-gas route, bounded as the handoff proposes: a methanol synthesis loop plus crude-methanol
purification with a sourced syngas feed; reforming is outside the boundary (a sourced boundary
feed). Choose and record a capacity basis, product grade and feed composition with sources or
ASSUMED marks.

1. Route/boundary memo, design basis (`process/design-basis.yaml`), and `process.yaml`
   (`publication.status: internal`, maturity/validation honest).
2. BFD and then PFD in `process/flowsheet.yaml`: syngas compression/recycle, converter, heat
   recovery/cooling, HP/LP separation, purge, distillation (topping + refining column or a
   justified simplification), with stream table. Generate the drawings with `cheme process build`
   and check balances with cheme (mass/element closure; energy where core supports it).
3. Reaction/model evidence table in DESIGN.md: CO and CO2 hydrogenation plus WGS consistency.
   A sourced equilibrium/conversion model is acceptable for this stage; label it as such. Do not
   invent kinetics or vendor data. Where core cannot yet qualify a calculation (see core #315),
   do the independent work, state the gated step precisely and move on.
4. Update DESIGN.md, PROGRESS.md and the equipment/line lists as far as the PFD requires.

Out of scope for this run: P&IDs (delete the DEXPI reference sheet the template ships if it is
in your way, or leave it untouched), layout, HAZOP, TEA, LCA, datasheets.

## Working rules
- Run cheme checks (`cheme status`, `cheme check`, `cheme maturity`) and fix what you can. Do not
  sign off a stage (`--write`).
- Commit your work to the current branch in sensible steps (`git add .` from this folder).
  Do not push, do not switch branches, do not touch other process folders or library tooling.
- Destructive shell commands are refused in this run; work around them.
- You have a fixed dollar budget. Spend it on the PFD and its balances; prefer a complete,
  honest, balanced PFD over polish. Before finishing, make a final commit.

## Final answer
End with a short report: what was produced (files), the balance/check results, the sources used,
open/unresolved inputs and gated steps, and the recommended next stage.
