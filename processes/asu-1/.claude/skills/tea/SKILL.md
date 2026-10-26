---
name: tea
description: Techno-economic analysis of the plant - cheme assess tea (capital cost built up from the equipment or take-off estimate or a scaled reference cost, with OSBL, owner's cost and contingency; revenue and variable cost of the flowsheet's feeds and products, their components, consumables, emissions with a carbon price, in one or several operating cases, continuous or batch; fixed cost and periodic events such as catalyst or stack replacement and turnarounds; discounted cash flow with NPV, IRR, LCOP, cash cost and payback; cost of production per unit; scenarios; tornado; break-even values; Monte Carlo P10/P50/P90) from the premises in estimate/tea.yaml, and cheme assess tea --compare REV to check two analyses share a basis. Use when an economic evaluation, a TEA, a levelised cost, an NPV or IRR, a business case, a cost of production, a price sensitivity or the comparison of design alternatives by cost is asked for, when the gate tea fails, or before a stage's investment decision.
---

# Techno-economic analysis

## Purpose and when to use

Support a decision with economics whose every number has a source. A TEA here is not "can it
be calculated" but "can we decide": it states the question, builds the capital cost from the
plant's own estimate, prices what the plant buys and sells, and shows which premises dominate
the result and at which value of each the decision would turn. It works for continuous and batch
plants, for one or several operating cases, for material and energy products (an LCOE or LCOH
is the LCOP of an energy product). Use it for an economic evaluation, a levelised cost of
product (LCOP), a cost of production, an NPV or IRR, a comparison of alternatives (each a
branch, compared with `--compare`), when the gate `tea` fails, and at the end of a stage whose
decision depends on the economics.

## Required inputs and missing inputs

- `process/flowsheet.yaml` with the flows of the case(s) (`cheme process streams`): every feed
  and product counts at its rate (kg/h, or kWh/h for an energy stream). Utilities must be their
  own feeds or products (POWER, CW) to be priced; a component can only be priced or charged when
  the streams carry a composition.
- A capital estimate: `cheme assess equipment` (skill `mto-estimate`; `estimate/cost-basis.yaml`
  with a cost index), `cheme assess estimate`, or a given ISBL with its source (scaled from a
  reference capacity when it is for another size).
- `estimate/tea.yaml` (`cheme schema tea`), schema `cheme/tea/v1`. A complete example (every
  `source` here is a placeholder to replace):

  ```yaml
  schema: cheme/tea/v1
  kind: tea
  currency: EUR
  cost_year: 2025
  decision:
    question: Proceed to basic engineering of the 500 t/d plant?
    metric: lcop            # npv, irr (at least threshold); lcop, cash_cost (at most)
    threshold: 60           # per basis.unit (EUR/t here)
    confidence: 0.8         # with uncertainty: P(meets) the decision needs
  basis:
    product: PROD
    unit: t
    specification: "99.5 wt%, 30 barg at the fence"
    boundary: feed intake to product battery limit
    scale: 500 t/d
    location: NL
  cases:                    # or case: design (one case)
    - {case: design, share: {value: 0.7, source: operating plan}, source: operating plan}
    - case: turndown
      share: {value: 0.3, source: operating plan}
      prices: {feed:POWER: 40}
      source: night tariff
  capex:
    isbl:
      source: equipment     # equipment | mto | given (never both estimates)
      exchange_rate: {value: 0.92, source: ECB annual average 2025, year: 2025}
      escalation: {value: 1.0, source: CEPCI already of 2025 in cost-basis.yaml}
      location_factor: {value: 1.1, source: "Towler and Sinnott 2022, location factors"}
      purchased_installation: {value: 3.0, source: Turton Table A.4 typical FBM}
      uncovered_allowance: {value: 0.3, source: "items not costed, DESIGN.md D-0xx"}
    osbl: {value: 0.3, source: "Towler and Sinnott 2022, sec. 7.3"}
    owners_cost: {value: 0.1, source: owner's estimate}
    contingency: {value: 0.25, source: class 4 estimate practice}
  operation:
    hours_per_year: 8400
    life_years: 25
    ramp_up: [0.8]
    utilisation: {value: 0.95, source: market outlook}
    source: design basis
  prices:
    - {key: feed:POWER, value: 95, unit: MWh, status: QUOTED, source: supply contract, year: 2025}
    - key: feed:GAS
      value: 9
      unit: MMBtu
      conversion: {value: 0.0455, source: "LHV of the gas, 0.0455 MMBtu/kg"}
      source: hub price
      year: 2025
    - {key: product:OFFGAS, component: H2, value: 2000, unit: t, source: H2 value, year: 2025}
    - key: product:PROD
      value: 70
      unit: t
      escalation: 0.01
      source: offtake term sheet
      year: 2025
      uncertainty: {gsd2: 1.3}
      swing: {low: 0.8, high: 1.2}
  free:
    - {key: product:VENT, reason: nitrogen vented to atmosphere}
  variable_opex:
    - {id: naoh, per: feed:FEED, amount: {value: 0.002, source: lab}, unit: kg NaOH, value: 0.4, category: chemical, source: supplier, year: 2025}
    - {id: credit, per: product:PROD, amount: {value: 1, source: scheme}, unit: kg, value: -0.05, category: incentive, profile: [1, 1, 1, 0], source: subsidy scheme, year: 2025}
  emissions:
    price: {value: 80, source: EU ETS forward 2025, year: 2025}
    escalation: 0.05
    sources:
      - {id: flue, key: product:FLUE, component: CO2, factor: {value: 1, source: CO2 itself}, captured: {value: 0.9, source: capture design}}
    allocation: {benchmark: {value: 0.1, source: product benchmark}, per: product:PROD, fraction: {value: 0.5, source: free allocation}, profile: [1, 0.8, 0.6, 0.4, 0.2, 0]}
  fixed_opex:
    maintenance: {value: 0.03, source: Towler and Sinnott}       # x fixed capital
    labour: {operators: {value: 10, source: staffing plan}, cost_per_operator: {value: 75000, source: HR cost plan}}
    insurance_tax: {value: 0.01, source: insurer}
  events:
    - {id: catalyst, kind: replacement, cost: {value: 250000, source: vendor}, every_years: 3, source: vendor}
    - {id: turnaround, kind: turnaround, fraction_of_isbl: {value: 0.02, source: site practice}, every_years: 4, downtime_days: 21, source: site practice}
    - {id: grant, kind: one_off, cost: {value: -1000000, source: grant letter}, first_year: 0, source: grant letter}
  finance:
    discount_rate: {value: 0.08, source: company hurdle rate (real)}
    tax_rate: {value: 0.258, source: NL corporate income tax 2025}
    losses: carry_forward
    construction: [0.4, 0.6]
    working_capital_days: {feed_inventory: {value: 30, source: plan}, receivables: {value: 45, source: plan}, payables: {value: 30, source: plan}, source: plan}
  uncertainty: {iterations: 2000, seed: 1, rate_mode: throughput, throughput: {distribution: normal, cv: 0.05}, defaults: {ASSUMED: {gsd2: 1.4}, QUOTED: {gsd2: 1.1}}}
  sensitivity: {swing: {low: 0.8, high: 1.2}}
  scenarios:
    - {id: power-2030, prices: {feed:POWER: 70}, source: price outlook}
    - {id: capex-overrun, scale: {capex:isbl: 1.3}}
    - {id: no-carbon-price, prices: {carbon: 0}}
  ```

  A batch plant gives `operation.batch: {cycle_time, basis_hours, trains, batches_per_year,
  success_rate, source}` (the flowsheet's rates are those of one batch over `basis_hours`), and
  variable items may be `per: batch`. An ISBL from a reference plant gives `isbl: {source: given,
  value, scaling: {reference, unit, exponent}}`.

- **Never invent a price.** Every price, factor and rate needs `status` (`ASSUMED`, or `QUOTED`
  when a quotation, contract or published price series backs it) and `source` (the publication,
  table, page or the person who decided it); give its `year`, which is checked against
  `cost_year` (a price without a year is reported). Without a source, leave the flow unpriced
  (the report says so) and ask. A number from memory is not a source. A flow that genuinely has
  no value goes under `free:` with the reason.

## Workflow and tools

1. **State the decision first.** Which decision, which metric, which threshold. The detail of
   the analysis must fit it: a concept screening needs the dominating premises right, not a
   detailed tax model.
2. **Fix the basis.** Product specification (purity, pressure, state at the battery limit),
   boundary, scale, location and the cost year, and the unit the product's cost is stated in.
   Two analyses compare only on the same basis.
3. **Capital.** `cheme assess equipment` first; resolve its findings (skill `mto-estimate`).
   Then `isbl` in `tea.yaml`: convert currency and year explicitly, a location factor, an
   installation factor for purchased-only items, an allowance for items no correlation covers
   (with the reason). The bare module cost includes installation and indirects: never add the
   take-off estimate on top. OSBL, owner's cost and contingency each as a fraction with its
   source.
4. **Estimate class against the stage.** `class_by_stage` (default concept 5, basic 4, detail
   3). The report warns when the estimate claims a finer class than the stage supports, or a
   coarser one than the stage needs (`cheme.tea-class-stage`). With no `isbl.uncertainty` the
   Monte Carlo spreads the ISBL over the class's AACE range.
5. **What the plant buys and sells.** Price every flow with a rate or list it free; price a
   component where only it has value or cost; use `conversion` for a unit of another kind (per
   MMBtu of a gas flow in kg, per Nm3); put consumables the flowsheet does not carry in
   `variable_opex`; a carbon price in `emissions`; price paths (`profile`, `escalation`) where
   prices are expected to move.
6. **Run.** `cheme assess tea` (Markdown), `--json`, `--csv` (cash flow), `--sensitivity`.
   Read the findings first.
7. **Read what dominates.** The cost of production shows where the money goes; the tornado (one
   input at a time) and the Monte Carlo's Spearman ranks name the premises that drive the
   decision; the break-even table gives the value of each at which the decision turns. Those
   premises are where evidence is worth buying: a quotation, a pilot result, a price contract.
8. **Alternatives.** Each design alternative on its branch; `cheme assess tea --compare
   <branch>` first lists the premises the two do not share (`cheme.tea-not-comparable`), then
   the results. Align the basis before reading a difference as the design's.
9. **Write and gate.** `cheme assess tea --write` writes `estimate/tea.md`,
   `tea-cashflow.csv`, `tea-sensitivity.csv` and, with a Monte Carlo, `tea-uncertainty.csv`;
   commit them with their inputs. The gate `kind: tea` requires `prices`, `no-example`,
   `class-stage`, `decision` and `tea-current` as the stage needs.

## Validation and failure handling

- `cheme validate` checks `estimate/tea.yaml` against its schema (units, unique keys and ids,
  shares of cases summing to 1, a construction schedule summing to 1, a threshold for an lcop or
  cash_cost decision, exclusive alternatives such as working_capital and working_capital_days).
- `cheme assess tea --check` exits 1 when the written files are not what the current inputs
  give: rewrite them, never edit them.
- An error finding (no flowsheet product, a price of a unit that needs a conversion, a component
  the streams do not carry, an estimate in another currency without an exchange rate) stops the
  evaluation; fix the input it names. `docs/framework/tea.md` lists every rule.
- A premise you cannot source goes into `DESIGN.md` with its effect on the result (its
  break-even value), not into a silent number.

## Outputs and provenance

- `estimate/tea.md`: decision and verdict, basis, capital build-up with the AACE range, every
  priced line with rate, price, status, source and year, emissions, fixed operating cost,
  periodic events, cost of production per unit, results, scenarios, tornado, Monte Carlo
  statistics and drivers, break-even values, findings.
- `estimate/tea-cashflow.csv` (year, phase, capacity, capital, working_capital, revenue,
  variable_cost, fixed_cost, periodic, depreciation, tax, cash_flow, discounted, cumulative),
  `tea-sensitivity.csv` (input, base, unit, low, high, basis, metric, at_low, at_high,
  break_even_multiplier, break_even_value), `tea-uncertainty.csv` (metric, unit, deterministic,
  mean, p10, p50, p90, valid, iterations, seed).
- `--json` adds the git commit and fingerprints of the files read; `GET /api/tea` serves the
  analysis of a committed revision, and the viewer shows it on its TEA page.

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
- G. D. Ulrich, P. T. Vasudevan, How to estimate utility costs, Chemical Engineering, April 2006
- skills `mto-estimate`, `process-design`, `lca`, `review`
