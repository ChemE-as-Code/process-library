# 0035. A batch process folder describes a dedicated train; campaigns on a multipurpose plant are out of scope

- **Status:** Proposed, 2026-11-05
- **Deciders:** the owner (to accept); drafted for core#158
- **Scope:** the library structure (what a process folder describes) and the LCI pipeline (how a
  batch process's per-batch flows and cleaning enter its dataset); `REFERENCE.md`,
  `CONTRIBUTING.md`

## Context

Most fine-chemical candidates without a process folder (#133 to #167; the batch candidates of
core#158) are made in batches, often by dosing an exothermic reagent into a charge. Many are
made on **multipurpose plants**: one train of reactors, filters and dryers runs a
**campaign** of one product for weeks, is cleaned, and then makes another product. The library
must decide what a batch process folder describes, and how the flows that only batch operation
has enter its LCI: cleaning between batches and between campaigns, the share of shared
equipment, and the per-batch purges and rinses.

What the library and core already do:

- One process folder holds one engineering project (ADR 0002) and one product's route. Its
  LCI dataset is per functional unit of that product.
- `silicon-carbide-1` DESIGN.md D-003 models its batch furnaces as time-averaged flows per
  hour: the LCI per kg and the balance do not depend on the schedule.
- `co2-electrolysis-bpm-1` DESIGN.md D-011 rejected a per-campaign batch flowsheet because
  the LCA has no case structure for it, and averaged the campaign's fill and spent anolyte
  instead.
- Core 1.7.0 (core#158; core ADR 0050 to 0053) adds `reactor: semibatch` and a batch recipe
  `process/recipe.yaml`. The recipe states the batch size and the unit procedures, derives the
  cycle time and the batches per year, sizes batch vessels and checks their jackets, and checks
  that the flowsheet holds the recipe's year averages (`cheme.recipe-basis`). LCA consumables
  may be given `per_batch` (core ADR 0053), converted with the recipe's batches per year.

Options considered:

1. **A campaign on a shared multipurpose train**, with the train, its other products and the
   changeovers in the folder. This needs several products in one folder (against ADR 0002),
   an allocation of the shared equipment and of the changeover cleaning between products the
   library does not hold, and a schedule (core#158 package 6, not built).
2. **One folder per product, each on a share of a multipurpose train.** The share needs the
   other products' campaigns, which are not in the folder, so the allocation cannot be checked.
3. **One folder per product on a dedicated train** (the default proposal of core#158). The
   folder's equipment makes only this product. Cleaning between its own batches belongs to it.
   Campaigns and changeovers stay out of scope until a later ADR.

## Decision

The library takes option 3.

- **A batch process folder describes one dedicated train** that makes its product, batch after
  batch, all year: its equipment, its recipe and its cleaning belong to it alone. A real plant
  that is multipurpose is described as if the train were dedicated to this product. DESIGN.md
  says so in a decision (`D-NNN Dedicated train`, with the reason), and `process.yaml` names it
  in `basis` (for example `capacity: "... in N batches/a of M kg on a dedicated train
  (ASSUMED)"`).
- **The batch basis is stated.** A Tier 2 batch entry gives its batch size and recipe in
  `process/recipe.yaml` (core ADR 0051). Its flowsheet holds the recipe's year averages, and
  `cheme validate` shows no `cheme.recipe-basis` warning. A Tier 0/1 batch entry needs no
  recipe. Its flows are time averages as in `silicon-carbide-1` D-003, and its `basis` states
  the operation as batch.
- **What enters the LCI per kg**:
  - every material and energy flow of a batch, including the cleaning and rinsing between its
    own batches, the nitrogen purges, the washes and the off-spec or rework share. What the
    flowsheet does not carry is an `lca/lca.yaml` consumable with `per_batch` (core ADR 0053),
    so its batch count follows the recipe. What the flowsheet carries (a wash the balance
    needs) is a stream at its year-average rate: per-batch amount x batches per year / hours,
    with that arithmetic in the stream's `source` (for example "per batch 0.5 m3 rinse water
    (ASSUMED) x 1320 batches/a");
  - the capital goods as for any other folder: the dedicated train's equipment (if the folder
    states them), with no share of other products' equipment.
- **What does not enter**: changeover cleaning between campaigns of different products, idle
  time of a multipurpose train, and shared tank farms or solvent recovery serving other
  products. `DESIGN.md` lists them as out of scope in the dedicated-train decision. The LCI
  gaps list (`lca/gaps.csv`) does not count them as gaps, because they are outside the
  boundary.
- **Campaigns stay out of scope** until a later ADR takes up option 1 or 2. That ADR will
  follow core's campaign scheduling (core#158 package 6) and needs a rule for allocating shared
  equipment and changeovers between the products of one train.

## Consequences

- Positive: each batch folder stays one product with one boundary, the build needs no new
  rule, and a batch dataset is comparable with a continuous one of the same product (the same
  functional unit, the same boundary rules).
- Positive: the recipe makes the batch basis explicit and checked. A flowsheet that does not
  hold the recipe's year averages is a warning, not a silent second basis.
- Negative: a product that in reality shares a multipurpose train gets no share of the
  changeovers and of the idle capital. Its burden per kg is a lower bound for that plant.
  DESIGN.md says so.
- Negative: a per-batch flow the balance needs is still a year-average stream written by hand
  (amount x batches / hours), and does not follow a change of the cycle by itself.
- Follow-ups: a campaign ADR once core#166 (core#158 package 6) exists.

## Evidence

- core#158 (the batch plan), core ADR 0050 (semi-batch), core ADR 0051 (batch recipe).
- `processes/silicon-carbide-1/DESIGN.md` D-003 (time-averaged batch furnaces),
  `processes/co2-electrolysis-bpm-1/DESIGN.md` D-011 (campaign flowsheet rejected).
- The NBS pilot `processes/n-bromosuccinimide-1` (#140) is the first entry under this rule.
