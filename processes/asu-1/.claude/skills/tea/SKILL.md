---
name: tea
description: Techno-economic analysis of the plant - cheme assess tea (capital cost built up from the equipment or take-off estimate with OSBL, owner's cost and contingency; operating cost and revenue of the flowsheet's feeds and products; discounted cash flow with NPV, IRR, LCOP and payback; scenarios; tornado; break-even values; Monte Carlo P10/P50/P90) from the premises in estimate/tea.yaml, and cheme assess tea --compare REV to check two analyses share a basis. Use when an economic evaluation, a TEA, a levelised cost, an NPV or IRR, a business case, a cost of production, a price sensitivity or the comparison of design alternatives by cost is asked for, when the gate tea fails, or before a stage's investment decision.
---

# Techno-economic analysis

## Purpose and when to use

Support a decision with economics whose every number has a source. A TEA here is not "can it
be calculated" but "can we decide": it states the question, builds the capital cost from the
plant's own estimate, prices the flowsheet's feeds and products, and shows which premises
dominate the result and at which value of each the decision would turn. Use it for an economic
evaluation, a levelised cost of product (LCOP), an NPV or IRR, a comparison of alternatives
(each a branch, compared with `--compare`), when the gate `tea` fails, and at the end of a stage
whose decision depends on the economics.

## Required inputs and missing inputs

- `process/flowsheet.yaml` with the flows of the case (`cheme process streams`): every feed
  and product counts at its rate (kg/h, or kWh/h for an energy stream). Utilities must be their
  own feeds or products (POWER, CW) to be priced.
- A capital estimate: `cheme assess equipment` (skill `mto-estimate`; `estimate/cost-basis.yaml`
  with a cost index) or `cheme assess estimate`, or a given ISBL with its source.
- `estimate/tea.yaml` (`cheme schema tea`), schema `cheme/tea/v1`:

  ```yaml
  schema: cheme/tea/v1
  kind: tea
  currency: EUR
  cost_year: 2025
  decision:
    question: Proceed to basic engineering of the 500 t/d ASU?
    metric: lcop            # npv (at least threshold), irr (at least), lcop (at most)
    threshold: 60           # per the main product's price unit (EUR/t)
    confidence: 0.8         # with uncertainty: P(meets) the decision needs
  basis: {product: GOXP, specification: GOX 99.5 %, 30 barg at the fence,
          boundary: air intake to product battery limit, scale: 500 t/d O2, location: NL}
  capex:
    isbl:
      source: equipment     # equipment | mto | given (never both estimates)
      exchange_rate: {value: 0.92, source: ECB annual average 2025, year: 2025}
      escalation: {value: 1.0, source: CEPCI already of 2025 in cost-basis.yaml}
      purchased_installation: {value: 3.0, source: Turton Table A.4 typical FBM}
      uncovered_allowance: {value: 0.3, source: "14 of 39 items not costed, DESIGN.md D-0xx"}
    osbl: {value: 0.3, source: Towler and Sinnott 2022, sec. 7.3}
    owners_cost: {value: 0.1, source: ...}
    contingency: {value: 0.25, source: ...}
  operation: {hours_per_year: 8400, life_years: 25, ramp_up: [0.8], source: design basis}
  prices:
    - {key: feed:POWER, value: 95, unit: MWh, status: QUOTED, source: ..., year: 2025}
    - {key: product:GANP, value: 40, unit: t, source: ..., year: 2025,
       uncertainty: {gsd2: 1.5}, swing: {low: 0.7, high: 1.3}}
  free:
    - {key: product:VENT, reason: waste nitrogen vented to atmosphere}
  fixed_opex:
    maintenance: {value: 0.03, source: ...}       # x fixed capital
    labour: {operators: {value: 10, source: ...}, cost_per_operator: {value: 75000, source: ...}}
    insurance_tax: {value: 0.01, source: ...}
  finance:
    discount_rate: {value: 0.08, source: company hurdle rate (real)}
    tax_rate: {value: 0.258, source: NL corporate income tax 2025}
    construction: [0.4, 0.6]
    working_capital: {value: 0.05, source: ...}
  uncertainty: {iterations: 2000, seed: 1, defaults: {ASSUMED: {gsd2: 1.4}, QUOTED: {gsd2: 1.1}}}
  sensitivity: {swing: {low: 0.8, high: 1.2}}
  scenarios:
    - {id: power-2030, prices: {feed:POWER: 70}, source: ...}
    - {id: capex-overrun, scale: {capex:isbl: 1.3}}
  ```

- **Never invent a price.** Every price, factor and rate needs `status` (`ASSUMED`, or `QUOTED`
  when a quotation, contract or published price series backs it), `source` (the publication,
  table, page or the person who decided it) and `year`. Without a source, leave the flow
  unpriced (the report says so) and ask. A number from memory is not a source. A flow that
  genuinely has no value goes under `free:` with the reason.

## Workflow and tools

1. **State the decision first.** Which decision, which metric, which threshold. The detail of
   the analysis must fit it: a concept screening needs the dominating premises right, not a
   detailed tax model.
2. **Fix the basis.** Product specification (purity, pressure, state at the battery limit),
   boundary, scale, location and the cost year. Two analyses compare only on the same basis.
3. **Capital.** `cheme assess equipment` first; resolve its findings (skill `mto-estimate`).
   Then `isbl` in `tea.yaml`: convert currency and year explicitly, an installation factor for
   purchased-only items, an allowance for items no correlation covers (with the reason). The
   bare module cost includes installation and indirects: never add the take-off estimate on
   top. OSBL, owner's cost and contingency each as a fraction with its source.
4. **Estimate class against the stage.** `class_by_stage` (default concept 5, basic 4, detail
   3). The report warns when the estimate claims a finer class than the stage supports, or a
   coarser one than the stage needs (`cheme.tea-class-stage`). With no `isbl.uncertainty` the
   Monte Carlo spreads the ISBL over the class's AACE range.
5. **Run.** `cheme assess tea` (Markdown), `--json`, `--csv` (cash flow), `--sensitivity`.
   Read the findings first: `tea-price-missing`, `tea-capex-uncovered`, `tea-cost-year`,
   `tea-price-year`, `tea-basis-mismatch` (operation differs from `lca/lca.yaml`),
   `tea-capex-range` (an uncertainty narrower than the class supports), `tea-confidence`.
6. **Read what dominates.** The tornado (one input at a time) and the Monte Carlo's Spearman
   ranks name the premises that drive the decision; the break-even table gives the value of
   each at which the decision turns. Those premises are where evidence is worth buying: a
   quotation, a pilot result, a price contract.
7. **Alternatives.** Each design alternative on its branch; `cheme assess tea --compare
   <branch>` first lists the premises the two do not share (`cheme.tea-not-comparable`), then
   the results. Align the basis before reading a difference as the design's.
8. **Write and gate.** `cheme assess tea --write` writes `estimate/tea.md`,
   `tea-cashflow.csv`, `tea-sensitivity.csv` and, with a Monte Carlo, `tea-uncertainty.csv`;
   commit them with their inputs. The gate `kind: tea` requires `prices`, `no-example`,
   `class-stage`, `decision` and `tea-current` as the stage needs.

## Validation and failure handling

- `cheme validate` checks `estimate/tea.yaml` against its schema (units, unique keys, a
  construction schedule that sums to 1, a threshold for an lcop decision).
- `cheme assess tea --check` exits 1 when the written files are not what the current inputs
  give: rewrite them, never edit them.
- An error finding (no flowsheet product, a price of the wrong kind of unit, an estimate in
  another currency without an exchange rate) stops the evaluation; fix the input it names.
- A premise you cannot source goes into `DESIGN.md` with its effect on the result (its
  break-even value), not into a silent number.

## Outputs and provenance

- `estimate/tea.md`: decision and verdict, basis, capital build-up with the AACE range, flows
  with rate, price, status, source and year, fixed operating cost, results, scenarios, tornado,
  Monte Carlo statistics and drivers, break-even values, findings.
- `estimate/tea-cashflow.csv` (year, phase, capacity, capital, working_capital, revenue,
  variable_cost, fixed_cost, depreciation, tax, cash_flow, discounted, cumulative),
  `tea-sensitivity.csv` (input, base, swing, metric at each end, break-even),
  `tea-uncertainty.csv` (metric, deterministic, mean, P10, P50, P90, iterations, seed).
- `--json` adds the git commit and fingerprints of the files read; `GET /api/tea` serves the
  analysis of a committed revision.

## Required human judgment

The decision, the basis, every price, the factors, the discount and tax rate, the estimate's
class and the distributions are the project's economic premises: a cost engineer or the
business owner decides them. An agent may assemble, check and run the analysis, propose values
**only** from a source the project gives it, and point at the dominating premises; it never
presents an assumed price as quoted and never signs off an investment case. Good economics
still need strategic support: the report answers what the numbers say, not whether to proceed.

## References

- `cheme schema tea`, `estimate/README.md`, `docs/framework/tea.md`
- AACE International Recommended Practice No. 18R-97, Cost Estimate Classification System
- G. Towler, R. Sinnott, Chemical Engineering Design, 3rd ed., 2022, ch. 7 to 9 (capital cost
  build-up, operating cost, economic evaluation)
- R. Turton et al., Analysis, Synthesis, and Design of Chemical Processes, 5th ed., 2018
- skills `mto-estimate`, `process-design`, `lca`, `review`
