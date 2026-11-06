# Ammonium nitrate and calcium ammonium nitrate

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and two LCI datasets, with no flowsheet and no simulation. Ammonia is neutralised with 60 wt% nitric acid. The resulting solution is evaporated and then either prilled or granulated as solid AN, or mixed with ground limestone and granulated as CAN.

## Route

Neutralising nitric acid with ammonia is how essentially all AN is made: the LVIC-AAF BREF (section 9.2.1) and the US EPA's AP-42 background report for section 8.3 (1996, section 2.2) both describe it as the route every plant uses. CAN is the same AN solution mixed with dolomite, limestone or calcium carbonate before granulation. The BREF calls it Western Europe's most applied fertiliser (section 9.1). AN and calcium carbonate from the nitrophosphate (Odda) process are another source (BREF section 9.2.2) and are not modelled.

The plants are continuous. Neutralisers are free-boiling vessels, circulating loops or pipe reactors (BREF 9.2.2), and the BREF's water figures are calculated for about 8640 operating hours a year (Table 9.6).

## How it is built

Each dataset in `lca/datasets/` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed N, H, O (and Ca, C) balance. The source is chapter 9 of the EU LVIC-AAF BREF (2007). Its facts are written in our own form, each with its table in `parameters`.

| Dataset | Basis | Feeds | Utilities | Emissions |
|---|---|---|---|---|
| `ammonium-nitrate-pressure-neutralisation-solid` | 1 t solid AN, as NH4NO3 | stoichiometry plus the sourced NH3 and dust losses: 212.8 kg NH3 and 1312 kg of 60 % acid | electricity 42.5 kWh (25 to 60), steam 25 kg (0 to 50), Table 9.3 | AMI Linz scrubber and prill tower, Table 9.4; waste water of AMI Linz, Table 9.5 |
| `calcium-ammonium-nitrate-granulation` | 1 t CAN, about 27 % N | 164.4 kg NH3, 1014 kg of 60 % acid, 227 kg limestone | electricity 30 kWh (10 to 50), steam 175 kg (150 to 200), Table 9.3 | midpoint of AMI Linz and DSM Geleen, Table 9.4; waste water as the midpoint of AMI Linz (Table 9.5) and DSM Geleen (Table 9.6) |

Two integer formulas let the element balance count mixtures:

- The 60 wt% acid is written as (HNO3)3(H2O)7, which is 59.985 wt%.
- CAN is written as (NH4NO3)17(CaCO3)4, which is 27.04 % N. The grade is ASSUMED: the BREF says only "less than 28 % N".

The acid's water leaves as the sourced waste water (AMI Linz, 0.24 m3 per t N; for CAN also DSM Geleen), and the rest leaves as vapour. That split is ASSUMED: the BREF names the outlets (process steam, condensate reused in the nitric acid plant or as scrubber water, condensate to treatment) but gives no shares.

The AN feeds come out at 0.2128 t NH3 and 0.7873 t HNO3 per t, against 0.213 and 0.789 in the BREF's Table 9.8 (Uhde's expected figures for new plants). The datasets do not use those numbers, so this is a check of the stoichiometry, not a transcription. The 0.2 % of acid the reference has beyond stoichiometry is nitric acid loss, which the dataset does not count (TODO). Both are `explained` in `benchmarks/fertilizers.yaml`. The electricity and steam KPIs take the same ranges as the datasets and are not independent. By hand, solid AN needs about 0.2 GJ/t of electricity and steam. That is inside the 0.09 to 0.22 GJ/t the BREF gives for modern plants (Table 9.3, infoMil 2001), but it is not bound because the steam is in kg.

## What is weak

- **Emissions to air come from two plants.** The table is headed "CAN". For AN, the dataset sums AMI Linz's central scrubber and its prilling tower for technical-grade AN. For CAN, DSM Geleen's numbered dryers and coolers are read as three parallel lines. Both readings are ASSUMED. The two plants differ by a factor of 3 for dust and 6 for ammonia. AMI Linz's second cooling drum has a concentration but no g/t figure, so it is not counted.
- **AN dust is near the low end.** The same table gives two UK AN plants: 30 g/t from one prilling tower with modern abatement and 400 g/t from another plant's prill towers and coolers. The dataset's 38 g/t is near the first. The US AP-42 factors for prill towers and coolers (background report, Table 2.3-1) are higher again, by about an order of magnitude. They are not used.
- **Steam is import only.** Pressure neutralisers raise steam, and a 4 bar unit can export 240 kg/t (Table 9.8). No export is counted, so there is no co-product and no credit. The source gives no pressure for the ranges used, so the steam links to the shared background entry by mass (`lca/mappings.yaml`).
- CAN steam: one plant in the same table (AMI Linz) reports 13 kg/t, against the range of 150 to 200 kg/t that the dataset uses.
- The waste water of CAN is the midpoint of two plants: AMI Linz's AN figure per t of nitrogen (65 kg/t CAN) and DSM Geleen's CAN process condensate and scrubber water (293 kg/t). We derived the Geleen figure from Table 9.6 as the specific N emission divided by the N concentration. The midpoint is ASSUMED, and so is the vapour that remains.
- Midpoints of ranges are our choice; the source does not recommend them.
- Solid AN is counted as pure NH4NO3. Commercial grades (33.5 to 34.5 % N) carry moisture, stabilisers and coating.
- The data are EU plants of about 2000 to 2006. `valid_until` is the reference year + 5, 2006, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention), ASSUMED values elsewhere.

## Linking

`feed:ammonia` is linked to `ammonia-1` and `feed:nitric-acid` to `nitric-acid-1`, whose product is 60 wt% acid by mass of solution, the same basis (`lca/mappings.yaml`). Limestone links to the shared background entry. The products have the registry slugs `ammonium-nitrate` and `calcium-ammonium-nitrate`. An NPK entry can link to either one once it exists.

## Not counted yet (TODO)

Nitrogen in the waste water (core's crosswalk has no nitrate or ammonium flow to water yet), nitric acid and fluoride to air, N2O from AN decomposition, cooling water, steam export, additives and coating, and moisture. The full list is in each dataset's `system_boundary.excluded`.
