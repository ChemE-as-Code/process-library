---
name: mto-estimate
description: Take off the bulk materials of the 3D layout model and price them - plantcode assess mto (pipe length by DN, class and insulation; elbows, tees, reducers, flanges and gaskets; valves by type and DN; steel tonnage by section; grating, insulation and concrete) and plantcode assess estimate (unit rates from estimate/rates.yaml, then direct, indirect and contingency factors). Use when a material take-off, a bill of quantities, a bulk-material or factor estimate is asked for, when the gate mto fails, or after the layout model changed.
---

# Material take-off and estimate

## Purpose and when to use

Turn the committed 3D model (`layout/plant-model.yaml`) into quantities, and the quantities into
an estimate whose every number has a source. `plantcode assess mto` counts what the model shows;
`plantcode assess estimate` prices those quantities with the project's own unit rates and
applies the factor method. Use it for a material take-off or bill of quantities, a factor
estimate of the bulk materials, a comparison of two layouts by their quantities, when the gate
`mto` fails, and after every rebuild of the model that will be reported.

## Required inputs and missing inputs

- A current model: `plantcode layout build` without `layout-model-outdated`, and the lines
  routed that the take-off should cover (`plantcode layout report`). An unrouted line has no
  length, fittings or flanges in the take-off.
- `estimate/rates.yaml` (`plantcode schema rates`) for an estimate: the currency, the cost year,
  one rate per take-off category (more where size, class or group change the price), and the
  factors. Every rate and factor needs `status` (`ASSUMED`, or `QUOTED` when a quotation backs
  it), `source` and `year`. The file `plantcode init` writes is an **example** (`example: true`,
  currency `XXX`): its numbers price nothing.
- **Never invent a price.** When the project has no rate for a category, leave the rows unpriced
  (the estimate reports them) and ask for a source: a quotation, the company's cost database, a
  published cost index or estimating handbook named with its edition and year. A number from
  memory is not a source.

## Workflow and tools

1. **Take off.** `plantcode assess mto` (Markdown), `--csv`, `--json`. Read the totals first, then
   the findings: `mto-section-unknown` (members whose section has no mass per metre: their steel
   is not in the tonnage), `mto-no-pipes`.
2. **Check the counts against the model.** Look at the largest rows and at anything surprising:
   a DN with a long length but few pipes (a long rack run), many `bend <deg>` rows (pinned or
   skewed routes), a reducing tee whose branch is larger than its run (two lines meeting the
   wrong way), flanges much more than twice the valves plus the piped nozzles. Open the item in
   the viewer or `plantcode layout render` before trusting it.
3. **What the take-off does not count.** It counts the model: pipe as routed (no allowance for
   field routing, small bore or vents and drains not on the P&ID), fittings at the bends and
   junctions it draws (no olets, couplings, spectacle blinds, weldolets for instruments),
   flanges at valves and piped nozzles (not at spool breaks), steel members with a section (not
   shoes, chairs, base plates, connections, tank and platform handrails drawn as rings), grating
   plan area, insulation of pipes (not of valves, flanges or equipment shells beyond the
   insulated cylinders the model draws), concrete of plinths, foundations, ring walls and bund
   walls (not paving, piles or sumps). Add allowances as factors or explicit rates, with the
   reason, not by editing the take-off.
4. **Rates.** In `estimate/rates.yaml`: the first rate of a category whose `where:` matches a
   row prices it, so order specific before general (`{item: "*Control*"}` before all valves,
   `{dn_max: 50}` before all pipe). Filters: `item`, `dn_min`, `dn_max`, `class`, `spec`,
   `group`. Units are fixed per category (pipe m; fittings, flanges, gaskets, valves, inline ea;
   steel t; grating and insulation m2; concrete m3). Record the cost year and escalate rates of
   other years yourself (the estimate reports them as `estimate-rate-year`, unescalated).
5. **Factors.** `kind: direct` with `applies_to: [categories]` (erection, testing, painting, on the
   materials of those categories), `indirect` (engineering, construction management, on the
   direct cost), `contingency` (on direct plus indirect). State the estimate's class and
   accuracy in `basis:`; the factors must fit it.
6. **Estimate.** `plantcode assess estimate` (Markdown), `--csv`, `--json`. Resolve
   `estimate-unpriced` (add a rate, or say why the rows stay unpriced), read
   `estimate-rate-unused` (a rate shadowed by an earlier one).
7. **Write and gate.** `plantcode assess mto --write` and `plantcode assess estimate --write`
   write `estimate/mto.csv|md` and `estimate/estimate.csv|md`; commit them with the model. The
   gate `kind: mto` (`checks/checks.yaml`) requires `mto-current` (the CSV is what the current
   model gives), and once the project prices its plant `rates` (not an example, every row
   priced) and `estimate-current`.

## Validation and failure handling

- `plantcode validate` checks `estimate/rates.yaml` against its schema (a rate's unit must be
  its category's; ids unique).
- `plantcode assess mto --check` and `plantcode assess estimate --check` exit 1 when the
  written files are not what the current model and rates give: rewrite them, never edit them.
- No model (`mto-model-missing`): build and commit the model first. No rates
  (`estimate-no-rates`): write them; the take-off alone still works.
- A finding you cannot resolve (an unknown section, an unpriced row) goes into the estimate's
  basis in `DESIGN.md` with its effect on the total, not into a silent allowance.

## Outputs and provenance

- `estimate/mto.csv` (columns category, item, dn, dn2, class, spec, group, count, quantity,
  unit, length_m) and `estimate/mto.md` (with the model's `output_sha256`).
- `estimate/estimate.csv` and `estimate/estimate.md`: every priced row with its rate id,
  status, source and year; every factor with its base; the totals; the findings.
- `--json` adds the git commit and the fingerprints of the files it read (`source`).
  `GET /api/mto` serves the take-off (and the estimate when rates exist) of a committed revision.

## Required human judgment

Quantities from a layout model at concept or basic stage are incomplete by nature; the
allowances for what it does not count, the unit rates, their sources and escalation, the
factors, the estimate's class and accuracy, and the contingency are a cost engineer's
decisions. An agent may assemble and check the numbers and propose rates **only** from a source
the project gives it; it never presents an assumed price as a quotation, and never signs off
an estimate. Record who decided each rate and factor (their `source`) and review the estimate
like any other deliverable (skill `review`).

## References

- `plantcode schema rates`, `estimate/README.md`, `docs/framework/mto.md` (rows, rules, the API)
- `docs/framework/layout-model.md` (what the model holds)
- skills `pipe-routing`, `structures-access`, `layout-yaml`, `review`
