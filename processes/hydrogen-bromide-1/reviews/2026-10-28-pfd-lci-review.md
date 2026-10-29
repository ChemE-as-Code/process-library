---
topic: design
reviewed_commit: 0004c580d99b213f52ebdb13e8e7c7f100884df0
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, process/simulation.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, lca/, process.yaml, scripts/balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydrogen-bromide-1
merge: pending
---

# Hydrogen bromide (hydrogen-bromide-1) concept design and preliminary LCI: independent review

Branch `case/hydrogen-bromide-1` (issue #130), four commits on the merge base `cc5624f`
(78bf828, cd09152, f6f18e7, 0004c58). I am an independent agent and did not write this design.
I reviewed the design files and the LCI and changed none of them. The design is at concept
stage, so P&IDs, layout, datasheets, HAZOP and TEA are out of scope (run task.md).

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --stat origin/main...HEAD` | 192 files, all under `processes/hydrogen-bromide-1/`; nothing else changed. (The two-dot diff against today's `origin/main` also shows `processes/thf-1/` because thf-1 was merged to main after this branch was cut. This branch does not delete it.) |
| `cheme validate` | 0 errors, 0 warnings. Info: `checks/checks.yaml:76` cites D-023, but that is in a commented example from the template, not a design reference. |
| `cheme check` | every concept gate passes except `layout-plot-plan` (out of scope); `design-review` fails until this record is merged; the basic and detail gates fail as expected (no P&IDs, layout or datasheets) |
| `cheme maturity` | calculation maturity none. `maturity-sourced-boundary` fails on the assumed feeds S1, S3 and S10; `balanced-model-basis` fails on the specified C201 and C202 splits; R101 (sourced conversion) and R102 (equilibrium) pass. Warning `maturity-claim-exceeds` for the claimed `concept`. Same as the run report says. |
| `cheme process streams` | VAP, SYN and ABS blocks and all seven steps balance; extents 6.1777 (R101) + 0.0019 (R102) kmol/h |
| `cheme process propagate --check` | clean, no stale calculated values |
| `cheme assess lca --coverage` | partial screening carbon footprint with 8 gaps: the six unlinked backgrounds (BR2, H2, DMW, LPS, POWER, CW) plus H2 and HBr to air (no GWP factor); mass, element and carbon-origin balances closed; publishable |

## Independent checks of the numbers

- **Stoichiometry.** Br2 987.542 kg/h = 6.1795 kmol/h gives 12.359 kmol/h = 1 000.0 kg/h HBr.
  H2 at 1.05 x Br2 = 6.488 kmol/h = 13.08 kg/h, with 0.1 mol-% N2 that makes 13.26 kg/h. The
  excess H2 is 0.62 kg/h. All match S1, S3 and S11.
- **Water.** Acid water 1 083.33 kg/h plus 0.13 kg/h vent water = 1 083.46 kg/h DMW (S10). The
  vent water matches saturation at 303 K and 190 kPa(a) (y about 0.022 on 0.31 kmol/h dry gas).
- **Vent HBr.** 5 mg/Nm3 on about 7.2 Nm3/h is 36 mg/h, i.e. 0.036 mg per kg HBr, as stated.
- **Reaction heat.** dHf(HBr, g) about -36.3 and dHf(Br2, g) +30.9 kJ/mol give -103.5 kJ/mol
  per extent, against -102.6 kJ/mol used: within 1 %.
- **R101 duty.** 6.18 kmol/h x 102.6 MJ/kmol = 176 kW at 298 K. Less about 15 kW to heat the
  products to 448 K, plus about 6 kW of feed preheat, gives about 167 kW, against 166.4 kW.
- **E102 duty.** 1 000 kg/h x 0.36 kJ/(kg K) x 115 K = 11.5 kW, against 11.8 kW.
- **E101 duty.** About 193 kJ/kg vaporisation at 298 K plus about 18 kJ/kg gas superheat to
  378 K = 58 kW, i.e. 98.5 kg/h of 450 kPa(a) steam. Br2 saturation at 300 kPa is about 368 K
  by Clausius-Clapeyron from the normal boiling point, which agrees.
- **Absorber.** 12.36 kmol/h x 72 MJ/kmol = 247 kW heat of solution, less 18 kW acid sensible
  heat = Q4 of about 232 kW. The overall hand closure (410.0 against 410.6 kW) checks.
- **Plausibility per kg HBr.** Bromine 0.988 kg is stoichiometric. Steam 0.058 kWh is set by the
  bromine latent heat. Cooling 0.41 kWh comes from the reaction heat plus the heat of solution.
  Electricity is 3 Wh, since no blower or compressor is needed (pressure-fed). All of these
  are consistent with a pressure-fed HBr burner and absorber of this type. The pump power
  (1.4 m3/h, 100 kPa, eta 0.5, 0.08 kW) checks.
- **LCI per functional unit.** In 0.987542 + 0.013263 + 1.08346 = 2.084265 kg; out 2.08333 +
  0.000935 = 2.084265 kg. This closes and agrees with the flowsheet. No zero-filled
  background: every feed and utility is `missing:` with a description, and is listed in
  `lca/gaps.csv`. No licensed (ecoinvent) values. `lca/mappings.yaml` exists and has no
  overrides, with the candidates listed in comments.
- **Sources and licences.** The register (DESIGN.md section 2) gives URL/DOI, locator, read
  status and terms. Patent and Wikipedia facts are restated in the design's own words; I found
  no copied tables, figures or passages. The Ullmann chapters are used for identity only.
- **Route and boundary.** The route is H2 + Br2 burner, catalytic finishing and absorption to
  48 wt-% acid. That is an intentional synthesis, as the issue's case notes ask, and the
  by-product and salt routes are rejected with reasons. The product-form question the issue
  raises (anhydrous gas or aqueous acid) is settled explicitly in D-002. The functional unit
  (kg HBr contained in 48 wt-% acid) and the dataset name make clear that this is not
  anhydrous HBr.
- **process.yaml.** Internal, `maturity: concept`, `validation.status: unreviewed`. The notes
  state that cheme maturity reaches no level and why (see R-08).

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:161-168 (D-009); scripts/balance.py:75 | heat of solution, Q4 | Q4 (232 kW) is 57 % of the cooling duty, and it rests on a chain of values not read at source. The -85.14 kJ/mol infinite-dilution value (SRC-6) comes from a search summary; the PDF was not opened. The 0.82 to 0.85 fraction is carried over from hydrogen-chloride-1 D-009, whose own HCl integral heats are "recalled NBS Circular 500 values, not read at source". The value is marked ASSUMED and its sensitivity is stated, so it does not mislead a reader. But the largest utility of the LCI has no sourced basis, even though primary data exist: the NBS tables give HBr dilution enthalpies at n H2O directly. | medium | open | Read the NBS tables (Wagman et al. 1982, J. Phys. Chem. Ref. Data 11 Suppl. 2, HBr(aq) at n H2O; or Parker 1965 at source) and interpolate at 4.87 mol water with a locator. Replace the HCl-analogy fraction, re-run `scripts/balance.py`, then update Q4 and the LCI. |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:49 (`emission_exclusions` id `catalyst`); DESIGN.md D-012 | R-102 activated carbon | The make-up activated carbon of R-102 is a routine consumable input, and the bromine-loaded spent carbon a routine waste. Both are left out of the inventory, filed under `method: non-routine` with no amount. So this background is neither a gap in `gaps.csv` nor a cut-off the 1 % rule can check (`cheme.lca-cutoff-unchecked`). It is probably small, but its omission is not visible as a gap. | medium | open | Give an ASSUMED carbon bed life and inventory (e.g. from the bed volume at a stated space velocity) and add `feed:ACT_C` (`missing:` activated carbon) and the spent carbon as a waste output. Or give the exclusion `cutoff: {amount, unit: kg, per_year}` and a routine method, so that it is checked against the 1 % criterion. |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:43 | emission:Br2 | Br2, a toxic substance, is declared `free: true` (burden-free in every category). It is 0 kg in this balance, but if a later balance gives the vent a bromine slip, that slip would count as burden-free without any warning. | low | open | Declare it as an elementary emission to air (`elementary: {compartment: air}`) like HBr, so that a non-zero amount becomes a characterised value or a gap. |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml:207; DESIGN.md D-008 | S9, C202 to C201 | The weak acid leaves the scrubber, which runs at 190 kPa(a), at 210 kPa(a) and enters the absorber at 200 kPa(a). There is no pump, and no elevation or gravity arrangement is stated. As written, the liquid flows uphill in pressure. | low | open | State in D-008 that C-202 sits above C-201 (gravity flow, about 2 m of liquid head, the usual stacked HCl/HBr arrangement). Otherwise add a weak-acid pump with its power (negligible in the LCI). |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md:74 | dHr unit | "dHr = -102.6 kJ per kmol extent" is wrong by a factor of 1 000: it should be kJ per mol (MJ per kmol). `process/reactions.yaml` holds -102 580 kJ/kmol correctly. | low | open | Correct the unit in section 3. |
| 2026-10-28-pfd-lci-review#6 | DESIGN.md section 2 (SRC-6, SRC-9); process.yaml:72 | source locators | SRC-9 (IAPWS-IF97) is cited "as commonly tabulated", with no table or equation locator. SRC-6 is a secondary search summary (see #1). The process.yaml reference "Wikipedia: Hydrogen bromide ... and Hydrobromic acid" gives only the hydrobromic acid URL. | low | open | Give the IF97 region and equation, or a table, for psat and the latent heat. Add the Hydrogen bromide Wikipedia URL as its own reference. |
| 2026-10-28-pfd-lci-review#7 | equipment/equipment-list.yaml (R-101) | design temperature | R-101 has a design temperature of 300 degC against a flame above 1 600 degC. The design temperature applies to the water-cooled chamber and jacket, but the entry does not say so, and the quartz or nickel burner tube is not covered. | low | open | Say which parts the 300 degC applies to and give the burner tube separately (or TBD) in the datasheet stage. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:36 | maturity claim | `cheme maturity` warns `maturity-claim-exceeds`: calculation maturity none against the claimed `concept`. `concept` is the manifest's lowest level, and `validation.notes` states plainly that cheme maturity reaches no level and why (assumed feeds, specified absorber and scrubber splits). So the claim is honest by disclosure, not misleading. | low | open | Keep the disclosure. Once the feeds are tied to a sourced basis and the absorber recovery to a source, re-run `cheme maturity` and remove the note. |

No critical or high findings. The balances close, the LCI is per functional unit and agrees with
the flowsheet, every background is a described gap, the key values are sourced or ASSUMED, and
nothing outside the process folder changed.

## Previous findings

None: this is the first review of hydrogen-bromide-1.

## Merge

Merge is pending. There are no open critical or high findings, so this review does not block
the merge. The medium findings #1 and #2 should be closed (or carried forward) before the next
stage.
