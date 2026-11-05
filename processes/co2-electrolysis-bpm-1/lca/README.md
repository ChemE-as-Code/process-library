# LCA of the two pilot skids (#331)

A **screening, partial carbon footprint** (climate change only) and a reconciled life cycle
inventory of the two CO2-to-CO pilot skids of #330, per kg of CO delivered, for the 1,000 h
design campaign: Skid A on one 1 M KOH fill, Skid B on continuous 5 M KOH dosing. It is not a
full LCA (one category), not a comparative assertion (no critical review, ISO 14044 6), and its
result has gaps that are listed, never set to zero (library ADR 0029). The decisions are
DESIGN.md D-024 to D-027; the tables at the end are regenerated with the design.

## Files

| file | what | written by |
|---|---|---|
| `lca.yaml` | goal and scope (`cheme schema lca`): functional unit, boundary, case skid-a, allocation none, every flow's background or why it has none, the replaced stack parts, the cut-off, the scenarios, the dataset documentation | people; `scripts/regen.py` step 20 writes `functional_unit.kg_per_unit`, `operation.hours_per_year` and the parts' `per_replacement` and `every_years` from the design |
| `factors.yaml` | the open profiles `ember-2025` and `desnz-ghg-2026`, and the DESNZ water factor per kg | people |
| `mappings.yaml` | the Atlas build's overrides for this process's exchanges (ADR 0022): the names a licensed background would link, **not checked: no ecoinvent licence** | people |
| `dataset.yaml` | Skid A's unallocated LCI dataset (case skid-a, per hour of operation) | `cheme assess lca --write` |
| `datasets/<id>-skid-b.yaml` | Skid B's own dataset (case skid-b; its id, title and uuid name the case, core ADR 0045) | `cheme assess lca --write --case skid-b` |
| `inventory.csv`, `results.*`, `gaps.csv`, `manifest.json` | Skid A's inventory per kg CO, its results with every scenario, the gaps, what the results rest on | `cheme assess lca --write` |
| `scenarios/*.json` | one record per scenario (Skid B and the electricity mixes) with its verdict against the baseline | `cheme assess lca-scenarios --write` |
| `sensitivity-*.json`, `ranking.json` | membrane life, H2 co-product, electricity mix, duration; the A against B ranking rule | `scripts/lca_sensitivity.py` (regen step 17) |
| `../results/scenarios/<H>h/lca.json` | per scenario: every exchange per kg CO for both skids, the reconciliation (E10), the balances, the run fingerprints, the totals and the gaps | `scripts/regen.py` step 20 (`scripts/_lca.py`) |

Never edit a generated file: change the design or `lca.yaml` and run
`cheme run scripts/regen.py --duration 1000` (the 10,000 h scenario with `--scratch`); a step 20
error fails the run (exit 4). `cheme run scripts/regen.py --check` regenerates both scenarios and
compares (the gate `skid-regen-current`). The LCA alone: `cheme assess lca --check`,
`cheme assess lca --check --case skid-b`, `cheme assess lca-scenarios --check`.

What CI enforces (`.github/workflows/validate.yml`): `cheme assess lca-scenarios --check`
(blocking), the fast E10 tests on the committed records (`tests/test_co2_electrolysis_bpm_skids.py`,
library job) and the regeneration of both scenarios with E1 to E10 asserted (engineering job,
which does not compare with the committed files). The gates `lca`, `lca-case-dataset-current`
and `skid-regen-current` run in CI only inside `cheme check --no-write`, which is informational
(`continue-on-error`): run `cheme run scripts/regen.py --check` and the two `cheme assess lca
--check` commands before committing.

## Scope

- **Functional unit**: 1 kg of CO contained in the product at >= 0.99 mol/mol dry (the rest
  H2) and 5.0 bar(a) at the skid boundary. `kg_per_unit` is the kg of product gas per kg of
  contained CO, from the composition of the product stream that `scripts/skid_balance.py`
  writes.
- **Boundary**: cradle to gate, NL (ASSUMED site), 2026; operation 8,000 h/a (ASSUMED), life
  10 years (ASSUMED, a pilot skid).
- **Allocation: none.** CO is the only product: the cathode's H2 is burnt with the PSA tail gas
  in the oxidiser X-x32 and the anode O2 is vented, without burden and without credit under
  cut-off. Recovering the H2 is a sensitivity below, not a design.
- **CO2 origin**: merchant liquefied CO2, a fossil industrial by-product (ASSUMED, an owner
  decision, D-016): the vented CO2 is fossil, and its supply has no open factor (a gap).
- **Construction**: left out. Core 1.5.0 selects construction by equipment tag, not by case,
  so Skid B's dataset would carry Skid A's frames and tanks; it is a `cutoff:` entry with that
  reason and stays open.

## Backgrounds and method

- **Ember** (`ember-2025`): Yearly Electricity Data, release of 2026-09-15, data year 2025,
  CC BY 4.0: life-cycle emissions intensity of gross generation (upstream, supply chain and
  manufacturing included; no T&D losses, generation-based, no imports), modelled per
  technology on a mixed GWP basis (upstream methane at GWP 21): there is no single GWP basis.
  The grid electricity of the baseline (NL) and of every mix scenario. Used as a proxy for the
  supply at the consumer (no T&D losses). Attribution: Ember (2026), Yearly Electricity Data
  (release 2026-09-15), https://ember-energy.org/data/yearly-electricity-data/, CC BY 4.0; subset,
  converted to kg CO2e/kWh.
- **DESNZ** (`desnz-ghg-2026`): UK Government GHG Conversion Factors 2026, flat file v1.2,
  Open Government Licence v3.0, GB, GWP100 of AR4/AR5. The water supply (per m3, divided by
  1000 kg/m3 in `factors.yaml`, a proxy: GB mains water for NL demineralised water) and the UK
  grid of the cross-basis scenario. Contains public sector information licensed under the Open
  Government Licence v3.0.
- **Elementary emissions**: the plant's CO2 to air by `ipcc2021-gwp100` (AR6).
- **Mixed vintages**: AR4/AR5 (DESNZ), AR6 (the plant's CO2) and Ember's mixed basis in one
  total (`cheme.lca-method-mix`): read the result as a screening, partial carbon footprint.
- No ecoinvent or other licensed data. The calculation is core's factors backend
  (`cheme assess lca --write`, `cheme assess lca-scenarios --write`); CI runs
  `cheme assess lca-scenarios --check` (blocking) and the gates with `cheme assess lca --check`
  only informationally (above).

## Data classes

| exchange | measured (4TU series: U, FE, WDE, Cx) | design estimate | background |
|---|---|---|---|
| feed:POWER | U and FE at 200 mA/cm2 (the stacks' DC power) | rectifier 0.95; pumps, compressor, PSA and dosing pump ESTIMATE | Ember NL (published, used as proxy) |
| feed:CO2 | FE CO, WDE, Cx (what the cells take out) | 10 sccm/cm2, recycle 0.95 | gap |
| feed:WATER | FE H2 | saturation, condensate; Skid B's make-up from the duty | DESNZ water (proxy) |
| feed:KOH-FILL, feed:KOH-DOSE | WDE, Cx | the duty's fill and dose at the ASSUMED volumes and setpoints | gap |
| emission:CO2 (vent) | FE CO | recovery 0.90, recycle 0.95, oxidiser | ipcc2021-gwp100 (published) |
| product:SPENT, product:BLEED, product:CONDENSATE | WDE, Cx | the duty's routes; condensate at 1 mol/kg | gap |
| product:CW | U, FE (stack heat) | isothermal by assumption | gap |
| consumables (membrane, Ag, carbon paper, Ni foam) | - | cells x area x ASSUMED areal mass, 4,000 h interval | gap |

Every measured value is a 1 h bench measurement in fresh 1 M KOH held constant over the
campaign by assumption (D-014). `results/scenarios/<H>h/lca.json` labels every exchange.

## Gaps (ADR 0029)

No open factor exists for: the merchant CO2, KOH (fill and dose), the neutralisation of the
spent anolyte, the bleed and the condensate, the heat rejected to cooling water, the bipolar
membrane and its incineration, the Ag of the cathode, its carbon paper and the burning of it at
the silver refiner, and the Ni foam (the DESNZ construction metals factor is not used for
nickel). Each stays in the inventory with its quantity and is excluded from the totals; Skid A's
dose and bleed are listed at 0 (the table counts the non-zero gaps apart). Construction is cut
off (above). Two quantities sit inside these gaps and are stated, not counted:

- **the dilution water of the KOH solutions** (Skid A's fill 11.5 kg, Skid B's fill and dose
  4.4 kg per kg CO at 1,000 h): core counts each solution as one exchange, so its water is part
  of the KOH gap and not in `feed:WATER`. The table gives it at the water factor; the ranking's
  difference and break-even use the totals with it (DESIGN.md D-025);
- **the fossil CO2 of the carbonate wastes**: the spent anolyte, the bleed and the condensate
  carry about 7 % of the CO2 fed as K2CO3, which neutralisation with acid releases as fossil CO2
  (about 0.25 kg per kg CO for either skid, some 15 % on top of the vent's). It is part of the
  treatment gaps (DESIGN.md D-026).

The flows that distinguish the two skids are KOH, the alkaline wastes and construction, and none
has a factor: **ranking not determined** (`ranking.json`). With the solutions' water counted,
Skid B is higher in electricity and the separately fed water, lower in the solutions' water and
equal in the vent CO2, higher in total, and it uses more KOH and makes more alkaline waste per kg
CO; only Skid A's larger reservoir (construction) could reverse that, and it cannot be stated per
case yet.

## Sensitivities

- **H2 as a co-product**: the H2 of the tail gas, if a separation (not designed) recovered it,
  would carry about a tenth of the burden by mass or more than half by lower heating value
  (CODATA heats of combustion). Substitution has no open factor (missing). Open.
- **Membrane life** (1,000, 4,000 and 20,000 h, ASSUMED): an inventory sensitivity only (m2 of
  membrane, g of membrane, Ag and Ni per kg CO). Its impact is not computable: the parts are
  gaps, and core's scenarios cannot vary a consumable's amount (design core gap C4).
- **Electricity mix**: Ember NL, EU-27, DE, FR and world for both skids, and the DESNZ UK grid
  as a cross-basis check (verdict not comparable). The Ember pairs have no differing scope
  dimension; their verdict reads "proxy" only because the water background is a UK factor in
  every geography.
- **Duration** (1,000 against 10,000 h): KOH per kg CO by exchange; the characterised totals do
  not change (no KOH or waste factor).

## What core 1.5.0 does not do, and the alternative used

- The KOH exchanges count the solutions (the flowsheet's streams), not KOH 100 %: the KOH is
  their composition, and the reconciliation compares that with the duty totals. Their dilution
  water is therefore inside the KOH gaps, not in `feed:WATER` (core counts an exchange as one
  flow): `results/scenarios/<H>h/lca.json` states it at the water factor (`solution_water`) and
  the ranking uses it. The Atlas proxies `potassium-hydroxide-1m` and `-5m` convert each solution
  into KOH 100 % and deionised water by its composition, which a test compares with the
  datasets.
- `cheme assess lca --balance` takes no `--case`: Skid B's balance runs in a temporary copy
  whose `lca.yaml` studies case skid-b (regen step 20).
- Core reports the element and carbon balances `not-assessable` while the replaced parts have
  no composition (a consumable takes none); K and C close on every exchange that has one.
- `cheme assess lca-cases` prints six significant figures per kg of product gas: compared with
  the datasets at rel 1e-5 after `kg_per_unit`.
- A consumable's amount cannot vary per scenario (gap C4): the membrane-life impact is not
  computed.
- Construction cannot be stated per case: cut off, open.
- The case dataset's file name is core's `<dataset id>-<case>`, the dataset id derived from the
  flowsheet title, not `co2-electrolysis-bpm-1-skid-b`.
- The Atlas build named every activity after the process title, so the two skids' activities
  would have shared name, reference product, location and unit: `scripts/build_lci.py` now adds
  ", case skid-b" to a design case's dataset (library ADR 0034).

## Tables

<!-- regen:lca begin (scripts/lca_sensitivity.py; do not edit) -->
Generated from results/scenarios/<H>h/lca.json (design campaign 1000 h unless stated). Per kg CO delivered.

**Inventory per kg CO** (both skids; the background or why it is a gap)

| exchange | Skid A | Skid B | unit | background (A) |
|---|---|---|---|---|
| consumable:anode-ni-foam | 0.0002432 | 0.0002432 | kg | gap |
| consumable:cathode-gde-ag | 7.289e-07 | 7.289e-07 | kg | gap |
| consumable:cathode-gdl-carbon | 6.949e-05 | 6.949e-05 | kg | gap |
| consumable:membrane-bpm | 0.000139 | 0.000139 | kg | gap |
| emission:CO2 | 1.712 | 1.712 | kg | PUBLISHED |
| emission:H2O | 1.465 | 1.465 | kg | none |
| emission:N2 | 6.501 | 6.501 | kg | none |
| emission:O2 | 2.551 | 2.551 | kg | none |
| feed:AIR | 8.475 | 8.475 | kg | none |
| feed:CO2 | 3.537 | 3.537 | kg | gap |
| feed:KOH-DOSE (KOH 0 / 1.167) | 0 | 5.077 | kg | gap |
| feed:KOH-FILL (KOH 0.6494 / 0.02785) | 12.15 | 0.5212 | kg | gap |
| feed:POWER | 34.56 | 34.56 | kWh | PROXY |
| feed:WATER | 2.593 | 16.91 | kg | PROXY |
| product:BLEED (KOH 0 / 0.5335) | 0 | 19.47 | kg | gap |
| product:CONDENSATE | 1.299 | 1.299 | kg | gap |
| product:CW | 22.11 | 22.11 | kWh | gap |
| product:O2VENT | 1.564 | 1.564 | kg | none |
| product:SPENT (KOH 0.001644 / 0.01392) | 12.23 | 0.5218 | kg | gap |
| product:VENT | 10.66 | 10.66 | kg | none |

**Climate change, NL grid** (kg CO2e per kg CO; a partial screening carbon footprint, gaps excluded)

| | Skid A | Skid B |
|---|---|---|
| electricity (Ember 2025 NL) | 8.766 | 8.767 |
| vent CO2 (fossil) | 1.712 | 1.712 |
| water (DESNZ, proxy) | 0.0004961 | 0.003235 |
| characterised total | 10.48 | 10.48 |
| water in the KOH solutions (inside the KOH gaps; at the water factor) | 0.002201 | 0.0008422 |
| total with that water (the ranking's basis) | 10.48077 | 10.48303 |
| not counted: fossil CO2 of the carbonate wastes, released when neutralised (inside the waste gaps; 7.2 % of the CO2 fed) | 0.2541 | 0.2541 |
| gaps (exchanges without a factor; of them non-zero) | 13 (11 non-zero) | 13 (13 non-zero) |

**Electricity mix** (characterised total, kg CO2e per kg CO; verdict against the baseline)

| grid | Skid A | Skid B | verdict |
|---|---|---|---|
| NL (Ember 2025) | 10.48 | 10.48 | baseline |
| EU-27 (Ember 2025) | 8.988 | 8.992 | proxy |
| DE (Ember 2025) | 13.26 | 13.26 | proxy |
| FR (Ember 2025) | 3.137 | 3.14 | proxy |
| world (Ember 2025) | 17.61 | 17.62 | proxy |
| UK at the consumer (DESNZ 2026): cross-basis check | 8.084 | n/a | not comparable |

**Duration** (per kg CO)

| skid | quantity | 1000 h | 10000 h |
|---|---|---|---|
| A | KOH fill (KOH 100 %), kg per kg CO | 0.6494 | 0.6494 |
| A | KOH dosed (KOH 100 %), kg per kg CO | 0 | 0 |
| A | KOH in all (fill + dosed), kg per kg CO | 0.6494 | 0.6494 |
| B | KOH fill (KOH 100 %), kg per kg CO | 0.02785 | 0.002785 |
| B | KOH dosed (KOH 100 %), kg per kg CO | 1.167 | 1.167 |
| B | KOH in all (fill + dosed), kg per kg CO | 1.195 | 1.17 |

**Membrane life** (inventory only; impact not computable: gap)

| life | m2 BPM | g membrane | g Ag | g carbon paper | g Ni |
|---|---|---|---|---|---|
| 1,000 h | 0.00278 | 0.5559 | 0.002916 | 0.278 | 0.9728 |
| 4,000 h (design) | 0.0006949 | 0.139 | 0.0007289 | 0.06949 | 0.2432 |
| 20,000 h | 0.000139 | 0.0278 | 0.0001458 | 0.0139 | 0.04864 |

**H2 as a co-product** (not designed): 0.116 kg H2 per kg CO would carry 10.4 % of the burden by mass or 58.0 % by LHV; substitution missing.

**Skid A against Skid B: ranking not determined.** Distinguishing flows without a documented factor: feed:KOH-DOSE, feed:KOH-FILL, product:BLEED, product:SPENT, construction. Break-even KOH factor: -0.004142 kg CO2e/kg KOH (none).

**Reconciliation (E10)**: the datasets equal the duty totals per kg CO at 1000 h yes, 10000 h yes (largest relative difference 1.6e-08, tolerance 1e-6).
<!-- regen:lca end -->
