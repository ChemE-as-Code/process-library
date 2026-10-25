# System model of the Atlas LCI database

Methodology version: **1.0.0** (the version `build_lci.py` records as `METHODOLOGY_VERSION` in
every `datapackage.json` and activity comment; versioning rules in
[governance.md](governance.md)).

> **Status: draft for decision.** An agent drafted this document from the coordinator's decisions
> of 2026-10-25 (process-library#52). The owner and an LCA expert decide on it. Until they have,
> treat the rules as the working basis of the build, not as a reviewed methodology.

This page says how the Atlas turns the LCI datasets of its processes into one consistent
database: which system model it follows, how multi-output processes are allocated, what is cut
off, and how the build checks it. The process's own study (`lca/lca.yaml`) may answer its own
question with other choices. The database does not inherit them silently: it applies the rules
below and records, per dataset, which rule was used and why.

## 1. System model

- **Attributional, cut-off.** The default build is an attributional database with the cut-off
  approach to recycling and waste, which is consistent with linking it to an ecoinvent cut-off
  background (the default background named in the build, `ecoinvent-3.11-cutoff`).
- **One model per build.** `lci/mappings.yaml` declares `system_model: cutoff`. Every activity
  comment and `datapackage.json` (`system_model`) state the model and the methodology version.
- **Variants are separate databases.** A substitution build (`build_lci.py --system-model
  substitution`) is a labelled variant named `cheme-as-code-atlas-<version>-substitution`. It
  adds avoided-burden credits (today: the end-of-life recycling credits of ASU-1) and nothing
  else. It is never mixed into the default build. An APOS variant is not built yet (#51).

## 2. Multi-functionality

ISO 14044 (4.3.4.2) sets the order: avoid allocation where possible, by dividing the process or
by expanding the system; where it cannot be avoided, partition the inputs and outputs by an
underlying physical relationship; where that cannot be established either, by another
relationship such as economic value. The TfS PCF Guideline (v3) applies the same order to
chemical products, and the WBCSD *Life Cycle Metrics for Chemical Products* (2014) adds a
practical rule for choosing between mass and economic allocation. The Atlas hierarchy follows
them:

1. **Subdivision** where the data allow. A dataset that is subdivided has one product and needs
   no allocation (`rule: single-output`).
2. **A physical relationship, where one is clear:**
   - **exergy** for products of one separation that leave it in different thermodynamic states
     (`rule: physical-exergy`);
   - **energy content (LHV)** for co-produced fuels and hydrogen (`rule: physical-energy`),
     unless one of the co-products has no energy content; then step 3 applies.
3. **Otherwise the WBCSD rule:** economic allocation when the ratio of the highest to the
   lowest price per kg of the co-products is above 5, mass allocation otherwise (`rule:
   economic` or `mass`). Co-products below 1 % of the output mass do not enter this decision;
   when only one co-product is left, there is nothing to compare and the rule gives mass. Under
   economic allocation, such a minor co-product without a price gets an economic weight of 0.
   The rule needs every co-product in kg: prices per MJ and per kg do not compare, so a dataset
   with a co-product counted in another unit needs a curated rule (step 2 or 5).
4. **CO2 as a co-product** (e.g. from ammonia synthesis): the cut is placed before conditioning,
   as TfS does. The CO2 carries only the burden of its own purification, drying and compression
   (`rule: co2-cutoff`). In the build this is `method: shares` with a share of **0** for the CO2
   co-product (named by `product:`): it takes nothing of the main process. Its conditioning is
   a separate, subdivided dataset (step 1). The mappings refuse any other method for this rule,
   and the build refuses a non-zero CO2 share.
5. **A published sector rule** (product category rules or sector recommendations, e.g. Euro
   Chlor for chlor-alkali, PlasticsEurope for steam crackers, ISOPA for isocyanates) overrides
   the rules above (steps 1 to 4) for its process, as a documented deviation (`rule: pcr`).

Exported steam, heat and fuels are co-products: in the cut-off build they are allocated by
energy or exergy (documented per process), never credited. Credits for them belong to the
substitution variant.

### How the build applies it

The build cannot tell from the numbers whether a separation or a fuel co-production is the
underlying physical relationship, so steps 1, 2, 4 and 5 are **curated decisions**. Step 3 is
**computed** when prices are known.

| situation | what the export uses | recorded as |
|---|---|---|
| one product | nothing to allocate | `single-output` |
| a curated entry in `lci/mappings.yaml` `allocation:` (by process or process/dataset) | its method; the rule must allow the method (exergy for `physical-exergy`, energy for `physical-energy`, ...) or the mappings fail to load | `source: mappings`, the rule and its reason |
| prices of every major co-product known (all co-products in kg), method equals the WBCSD choice | that method | `economic` or `mass`, with the price ratio |
| prices known, method differs | the WBCSD choice, with a **finding** | `source: hierarchy`, `follows_hierarchy: false` |
| no rule, and no price ratio (a price missing, or a co-product not in kg) | the study's method, with a **finding** | `unresolved`, `follows_hierarchy: false` |

A deviation from the hierarchy is recorded only as a curated entry with `rule: deviation` and
its reason. The study (`lca/lca.yaml`) and the dataset cannot record one: core's allocation
schema has no field for it and refuses unknown keys.

A finding is a build warning: `--strict` (CI, releases) fails on it. `datapackage.json` lists
the findings (`system_model.allocation_findings`) and, per dataset, `allocation: {method,
source, rule, reason, follows_hierarchy, shares}`. The rule also checks itself where it can: a
curated `economic` or `mass` rule that contradicts the price ratio, or an energy rule for a
product with zero energy content, is a finding.

**ASU-1** keeps exergy in the database (`lci/mappings.yaml`, `allocation.asu-1`): GOX, GAN, LOX
and LIN come from one cryogenic separation and leave it in different states, which is step 2a.
This is the study's method too (asu-1 DESIGN.md D-056), so the study and the database agree.
Economic allocation is not used: it would need prices of the four products (#46), and step 2
comes first.

## 3. Wastes, recyclables and energy recovery

- **Cut-off at the point of recycling or energy recovery.** Material sent to recycling and waste
  sent to incineration with energy recovery leave the producer's system without burden. The
  recycler, or the user of the recovered energy, carries the treatment. The producer gets no
  credit for the avoided primary material or energy.
- **Waste treatment without recovery** (landfill, incineration without recovery, wastewater
  treatment) stays in the producer's system as a technosphere exchange to the treatment
  activity.
- **In the build:** `lci/mappings.yaml` `cutoff_exclusions:` lists the technosphere ids the
  cut-off model leaves out, each with its decision. An exchange that resolves to one of them is
  not exported, and the decision is written into the activity comment ("Excluded by the cut-off
  system model") and `datapackage.json` (`system_model.excluded`). Independently of the
  mappings, a cut-off build refuses any negative technosphere amount (an avoided burden), and
  `lci/mappings.yaml` refuses a proxy with a negative input outside `substitution:`.
- **ASU-1:** its dataset carries end-of-life steel and aluminium recycling credits (90 %
  recovery, avoided primary metal), as its study models them. The database excludes them under
  cut-off (`cutoff_exclusions.steel-recycling`, `aluminium-recycling`); the substitution variant
  keeps them through the credit proxies. The dataset itself is unchanged. In the CI round trip
  the cut-off GOX result is higher than the study's by exactly those credits.

## 4. Cut-off criteria for minor flows

ISO 14044 (4.2.3.3) lets a study leave out flows of little significance, provided the criteria
(mass, energy, environmental relevance) are stated. The Atlas criteria:

- a flow may be cut when it is below 1 % of the process's total input mass, **and** the cut
  flows together stay below 1 % of that mass (cooling water is not part of the mass basis),
  **and** the flow is not environmentally relevant;
- never cut: catalysts containing precious or critical metals, and flows with high
  characterisation factors (N2O, SF6, HFCs, heavy metals), whatever their mass;
- every cut flow is named in the dataset with the reason.

The build does not check these criteria yet: datasets do not record cut flows in a form it can
read. They are part of the review checklist ([governance.md](governance.md)).

## 5. Infrastructure, capital goods and catalysts

- **Infrastructure** is included when the design provides it: construction materials from the
  take-off, spread over the plant's life (as core's dataset does for ASU-1). Otherwise the
  dataset states that infrastructure is excluded. The two are never mixed silently within one
  dataset.
- **Catalysts and adsorbents** are consumables: their make-up per unit of product is an input,
  and their end of life follows section 3. Precious or critical metal catalysts are never cut.
- **Maintenance** (spares, replaced equipment) is an input per unit of product, like
  construction.

## 6. Other conventions

- **Electricity:** industrial power links to the medium-voltage market of the site's country
  by default (`install(location=...)`).
- **Data freshness:** primary data at most 5 years old and secondary data at most 10 years old
  at the reference year. A dataset will record a `valid_until` year (core#179); `datapackage.json`
  carries it (null until core writes it).
- **Atmospheric pass-through** (components taken in with the air and returned unchanged) is not
  exported, as decided in `lci/mappings.yaml` `pass_through:`.
- **Data quality, nomenclature, carbon:** the pedigree matrix and TfS DQR (core#178), EF 3.1
  flow identifiers (core#175, core#177) and the biogenic carbon rules (core#181) are part of
  this methodology once core implements them; they will raise the methodology version.

## 7. How other chemical LCI databases document their methodology

Two published chemical LCI databases show what users expect from the documentation of one.

- **ecoinvent** documents its methodology in a data-quality guideline (Weidema et al. 2013) and
  publishes each release in several system models: an attributional cut-off model (recyclable
  material is cut off at the producer, secondary material enters burden-free apart from its
  recycling), an attributional model that allocates at the point of substitution (APOS), and a
  consequential model. Each system model is a separate database built from the same unit
  processes. Datasets carry pedigree scores and uncertainty; every version comes with change
  reports per dataset.
- **Carbon Minds, cm.chemicals** (methodology document V2.03, 2026) describes one methodology
  for every dataset in a public document. It is versioned with each release, a change report
  accompanies each release, and the methodology has had an external critical review. Their
  technology datasets are checked by mass and elemental balances, with gaps closed by
  thermodynamic models or literature and the deviations documented. The model is layered: plant,
  integrated site, national production and consumption mixes, and an extension layer of
  simplified (stoichiometric) models at a lower data-quality rating. Biogenic carbon is traced
  through the supply chain and its content always reported. Several data-quality schemes are
  reported side by side, with a primary data share. Each dataset has ILCD documentation with use
  advice, a statement of included and excluded life-cycle stages and their GHG Protocol scopes.
  Waste incineration is modelled from the waste's composition (following Doka 2003).

**What the Atlas adopts:**

| practice | Atlas |
|---|---|
| one public, versioned methodology document | this page, methodology version in every build |
| one system model per database, variants as separate databases | cut-off default; substitution variant with its own name (section 1) |
| change report per release | `build_lci.py --previous` (exchange level today; [governance.md](governance.md)) |
| external critical review of the methodology | planned: the review procedure in [governance.md](governance.md) |
| mass and elemental balances per technology dataset | from the flowsheet for engineered processes; to be checked by the build (follow-up) |
| layered model: plant, site, production and consumption mixes, simplified extension layer | planned (core#182, #47, #49): tiered generation and market datasets |
| biogenic carbon content always reported | planned (core#181) |
| several data-quality schemes and a primary data share | planned (core#178): pedigree, TfS DQR, PEF-style indicators, PDS |
| per-dataset documentation of included and excluded stages | activity comments and `datapackage.json` today; ILCD export planned (#51) |

## References

- ISO 14044:2006, *Environmental management - Life cycle assessment - Requirements and
  guidelines*, clauses 4.2.3.3 (cut-off criteria) and 4.3.4 (allocation).
- Together for Sustainability (TfS), *The Product Carbon Footprint Guideline for the Chemical
  Industry*, version 3.
- WBCSD Chemicals, *Life Cycle Metrics for Chemical Products: A guideline by the chemical sector
  to assess and report on the environmental footprint of products, based on life cycle
  assessment*, World Business Council for Sustainable Development, 2014.
- Weidema, B. P., Bauer, C., Hischier, R., Mutel, C., Nemecek, T., Reinhard, J., Vadenbo, C. O.,
  Wernet, G. (2013). *Overview and methodology. Data quality guideline for the ecoinvent database
  version 3*. Ecoinvent Report 1 (v3). St. Gallen: The ecoinvent Centre.
- Carbon Minds GmbH, *cm.chemicals database methodology*, version 2.03, 2026 (cited for its
  approach only; no content reproduced).
- Doka, G. (2003). *Life cycle inventories of waste treatment services*. ecoinvent report No. 13.
  Swiss Centre for Life Cycle Inventories, Dübendorf.
