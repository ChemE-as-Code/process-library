# A2/O wastewater example

- Keep code, identifiers, UI and generated reports in English.
- This is a generic EXPOsan-derived ASM2d A2/O teaching example, not original
  BSM1, a Bergambacht model, a plant validation, or an approved design.
- Preserve every run. Each saved simulation gets a new directory under process/simulation-runs/.
- Generate diagrams through the installed ChemE process builder.
- Keep wastewater concentrations and their COD/N/P measurement bases explicit.
- Execution completion, numerical checks, steady-state screening, reference
  comparison, conservation and plant validation are separate claims.
- Keep the thin root entry points; place implementation under wwtp_a2o following
  core/docs/framework/contributing.md's domain/integration/project/interface direction.
- Optional simulator imports belong inside integration functions. Diagram/input
  inspection must not load QSDsan, EXPOsan or a web framework.
- Run the local pytest suite, ruff check and ruff format --check with the example configuration matching
  core conventions. Use requirements-dev.txt; do not alter numerical pins casually.
- Before numerical refactoring, preserve a source snapshot and a completed run.
  Compare accepted solver states, trajectories, outputs and diagrams afterwards.
