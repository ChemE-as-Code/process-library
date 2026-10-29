---
topic: design
reviewed_commit: 6e550ac4d20461a2c9bc9de500d3eccdbc7b73be
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, scripts/has_balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydroxylamine-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI), hydroxylamine-1

An independent review of the hydroxylamine-1 case study (issue #182): hydroxylammonium sulfate
solution made by NO hydrogenation, with NO generated inside the boundary. It covers the branch
`case/hydroxylamine-1` at `6e550ac` against `origin/main`. The reviewer did not write the design
and changed no design file.

Branch content (`git log --oneline origin/main..HEAD`): `38fa1ee` scaffold, `2c9040e` design
basis, BFD/PFD and lists, `3cab4f3` preliminary LCI, `6e550ac` run record. `git diff --stat
$(git merge-base origin/main HEAD)..HEAD`: 191 files changed, all added under
`processes/hydroxylamine-1/`. Nothing outside the folder changed. The two-dot diff against
`origin/main` also shows other processes because `origin/main` has moved on since the branch
point `9f27e7a`. That is not a change made by this branch. `cheme diff main --list` has nothing to
list because there are no P&IDs (`pid/` is empty at concept stage).

Finding ids follow `reviews/README.md`. Each finding also carries the R-number the task asked
for.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/reactions.yaml:15 | NH3_NO heat_of_reaction | R-01: the value is `-226600` kJ/kmol, but the schema defines `heat_of_reaction` per kmol of extent of the reaction as written. The reaction is written as `4 NH3 + 5 O2 -> 4 NO + 6 H2O`, so the value should be about -906 400 kJ/kmol, as the entry's own source text says ("-906 kJ per 4 NH3"). The other reactions follow the convention (O2_HYD -483 644 for 2 H2; HAS_FORM -455 180 for 2 NO). The value is not used at present: `cheme process reactors` gives `dHr ?` for lack of ideal-gas data, and the duties come from scripts/has_balance.py, which uses -226.6 kJ/mol NH3 correctly. Once core evaluates reactor heats or the energy audit (predictive.formation-data), the burner heat would come out 4x too small. | medium | open | Set `value: -906400` (or write the reaction per 1 NH3), and check that NH3_N2O and NH3_N2, if given heats later, also use the per-extent basis. |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:89; DESIGN.md D-007, D-009 | emission:NO, purge X-201 | R-02: the LCI publishes a direct emission of 33.7 g NO per kg NH2OH: 126 kg/h, about 2 mol% (~20 000 ppm) NO in the 5.9 t/h flue gas (scripts/has_balance.py flue gas w(NO) = 0.0213). No permitted plant could vent this. It comes from two assumptions with no source and no safety basis: the 30 % purge (D-007, ASSUMED) and zero NO/N2O destruction in the oxidiser (D-009). The purge also sets the NO utilisation (96.8 %), the hydrogen use and the N2O in the loop gas. The loop gas (73.9 % H2, 12.4 % NO, 6.5 % N2O) holds two oxidisers with hydrogen, and S6 names the N2O/H2/NO explosion hazard (O-7). The NO emission is uncharacterised in GWP100, so the 7.08 kg CO2-eq does not change. In any multi-impact use (acidification, eutrophication, PM, photochemical ozone) this placeholder would dominate and mislead. It is disclosed as conservative (D-009, O-8), so the rating is medium, not high. | medium | open | Either model the abatement that D-009 already names (e.g. NSCR with the purge's own hydrogen, or return of the purge to NO recovery) with a sourced or ASSUMED efficiency, or state in `dataset:` of lca/lca.yaml and in process.yaml `validation.notes` that the NO (and N2O) of the purge is unabated and is a placeholder pending O-8. Record the purge's flammability basis as an open safety hold (O-7) next to the purge sensitivity. |
| 2026-10-28-pfd-lci-review#3 | lca/results.md:1,13; lca/results.csv:3 | LCA result headline | R-03: the generated results read "LCA per 1 kg PROD ... Climate change 7.08026 kg CO2-eq" and give a `total` row. The functional unit is 1 kg NH2OH contained, which is 9.782 kg of PROD (`kg_per_unit`). The only characterised flow is the plant's direct N2O. Read plainly, a reader of results.md, or the Atlas through `lca: source: auto` in process.yaml, sees a product footprint per kg of solution, off in basis by a factor of 9.8 and missing every upstream burden. DESIGN.md D-011 warns about this, but process.yaml `validation.notes` does not. The "partial screening" label is printed, which limits the harm. | medium | open | Add to process.yaml `validation.notes` (and the lca.yaml `goal`, already partly there) that the only characterised number is direct N2O per kg NH2OH (= 9.78 kg solution), not a product footprint. Report the "per 1 kg PROD" label for a functional unit with `kg_per_unit` to cheme-as-code. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:89 | D-005 condenser E-102 | R-04: "0.38 kmol/h HNO3" is the extent of NO_ABS (4 NO + 3 O2 + 2 H2O -> 4 HNO3). The HNO3 formed is 1.53 kmol/h (96.9 kg/h), which is what the 0.62 wt% in 15.6 t/h stated in the same sentence corresponds to. | low | open | Write "extent 0.382 kmol/h, i.e. 1.53 kmol/h (96.9 kg/h) HNO3". |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md D-004 | condensate to acid make-up | R-05: the whole condensate (0.62 wt% HNO3) goes to the acid make-up, and its nitrate ends up in the product (0.26 wt%). By D-004's own summary of S2, the DOMO process sends only a weak condensate (<= 0.2 % HNO3) to the acid make-up and hydrogenates the stronger one separately. The design departs from its source three times over the concentration S2 used there, and no decision says so. It also has no view of what the nitrate does on the Pt catalyst (O-6). | low | open | State the deviation from S2 in D-004 explicitly, with its effect on the product spec (O-9), or split the condensate as S2 does. |
| 2026-10-28-pfd-lci-review#6 | equipment/equipment-list.yaml:16 | E-101 waste-heat boiler | R-06: the only design pressure given is 2 barg, which is the nitrous-gas side. The steam side raises MP steam at 1500 kPa(a) (about 14 barg), and the list shows no design pressure or temperature for it. | low | open | Give design conditions per side (gas side 2 barg / 950 C, steam side e.g. 16-17 barg / saturation + margin, ASSUMED). |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md D-008 | R-201 cooling | R-07: 9.2 MW is removed at 313 K with cooling water at 25/35 C. That leaves a 5 K approach at the warm end and an LMTD of about 9 K, which means a large heat-transfer area inside six stirred tanks (coils, jackets or external loops) that the concept does not check. S3/S4 allow 40-60 C. | low | open | Note the approach in D-008 and decide between a higher cascade temperature (inside S3/S4's range, with its effect on selectivity), external coolers or chilled water. Carry it as an open input. |
| 2026-10-28-pfd-lci-review#8 | DESIGN.md:37 | D-001 reason | R-08: "Reason: the issue asks for this route." Issue #182 and its scoping comment ask for a comparison of route families and a choice of product form. The route was set by the job brief (runs/20261028-154504-design/task.md:21), not by the issue. Two of the rejected alternatives are argued only partly from sources: HPO "route knowledge, not sourced", and Raschig from the IPCC chapter. | low | open | Cite the job brief as the reason for the route and keep the comparison open under O-1 (the Ullmann audit). |
| 2026-10-28-pfd-lci-review#9 | DESIGN.md:135 | D-007 N2O level | R-09: "2-3 % of S6's foam-free batch gas phase" contradicts the source register (S6: 2-3 % N2O *with* foam suppression, about 30 % without). | low | open | Write "with foam suppression". |
| 2026-10-28-pfd-lci-review#10 | scripts/has_balance.py:245 | cascade gas print | R-10: the script prints "cascade gas in: T=0.00 K". The temperature, 335.4 K, is only computed later and printed further down. This is cosmetic, but it is the provenance script of every duty. | low | open | Print the stream after its temperature is set. |
| 2026-10-28-pfd-lci-review#11 | process/PFD.xml (generated) | layout | R-11: the generated PFD is about 4.7:1 wide. Feed lines run the full width beneath the blocks, and at sheet scale the stream labels cannot be read (build/PFD.png). | low | open | Pin a more compact layout in `layout.pfd` of flowsheet.yaml (`cheme process layout --pin`), then `cheme process build`. |

## Previous findings
None: this is the first review record of hydroxylamine-1. `reviews/` held only README.md, and
`grep -h '| open |' reviews/*.md` finds nothing.

## Drawing
No P&IDs exist (concept stage). `cheme validate` prints no `drawing <sheet>:` line for the
generated BFD/PFD, and the gate `drawing-clean` passes. The PFD was rendered whole
(`cheme render process/PFD.xml --png`, build/PFD.png) and looked at at sheet scale only, which
gave finding #11. Tiles were not read (see Not checked).

## Checked and fine
Commands re-run by the reviewer at `6e550ac`:
- `cheme validate`: 17 files, **0 errors, 0 warnings**. Infos only: D-012/D-023 cited in the
  commented template examples of control/cause-effect.yaml and checks/checks.yaml, and the DEXPI
  loader's reference cycles. Compared: BFD, PFD and 12 lists. The list-vs-P&ID cross-checks
  were skipped because there is no P&ID.
- `cheme check`: concept gates ok (design-basis, concept-lists, process-concept,
  process-balances, assumptions-marked, process-links). Failing: `layout-plot-plan` (concept;
  out of this case's scope, as the run report says), `design-review` (this record addresses
  it), and the basic/detail gates (`pids-exist`, layout, mto, datasheets, electrical, hvac),
  which are not expected at concept.
- `cheme maturity`: calculation maturity **none**. The `process.yaml` claim `concept` gives the
  warning `cheme.maturity-claim-exceeds`, but `concept` is the lowest value the schema allows,
  and both process.yaml (comment and `validation.notes`) and DESIGN.md say so. This is honest,
  as for hydrogen-peroxide-1. `validation.status: unreviewed` is correct.
- `cheme process streams`: all 3 blocks and 19 steps close on mass and extents (NOX 19 803.8,
  HAS 37 025.0, OGT 5 944.9 kg/h). `cheme process propagate --check`: no output (nothing
  stale). `cheme impact`: nothing to review.
- `cheme run scripts/has_balance.py` reproduces every stream and duty in flowsheet.yaml
  (37 025.02 kg/h in = out; NO utilisation 0.9677; NH3 0.6123 and H2 0.1307 kg/kg NH2OH).
- `cheme assess lca --coverage`: partial screening carbon footprint. 13 background gaps, each
  with a `missing:` description, plus NO and H2 as uncharacterised elementary flows. Mass balance
  closed. The element balance cannot be assessed only because the catalyst consumables have no
  composition. No zero-filled background, no ecoinvent or licensed value, and `factors.yaml` is
  the packaged open profile. The per-process overrides (feed:LPS unit, `atlas: false` for H2 and
  STEAMD) are in lca/mappings.yaml with reasons. The functional unit is 1 kg NH2OH (9.78222 kg
  solution = 36 683.3 / 3750). Inventory in = out: 11.3675 kg per FU.

Independent hand checks against the stoichiometry (reviewer's own arithmetic):
- Burner: 134.8 kmol/h NH3. O2 179.3 kmol/h (ratio 1.33, S1). O2 used 167.7 and residual
  11.47 kmol/h, which matches O2_HYD 10.32 (90 %) plus NO_ABS 3 x 0.382. Steam:NH3 4.81 = 67.4/14.
  N2O share 1.40 % of NH3-N reproduces from IPCC 5 kg N2O/t HNO3 x 0.98.
- Burner heat about 8.5 MW. The rough adiabatic rise (about 1 000 kmol/h, cp about 39 kJ/kmol K)
  gives about 1 170 K against the 1 196 K reported. E-101 7.0 MW (1 196 -> 543 K) and E-102
  14.0 MW (condensing 15.6 t/h plus sensible) are consistent. K-101 99 kW reproduces from
  145 kmol/h, ratio 1.91, eta 0.75.
- Cascade: H2 consumed 197.4 kmol/h, off-gas H2 83.5 and purge H2 25.0 (= 2 x H2_COMB 12.52).
  Fresh H2 to the cascade 220.1 kmol/h = 443.76 kg/h. Selectivity 89.8 / 8.2 / 2.0 % on 126.4
  kmol/h NO converted. The 90 % per pass and the 30 % purge reproduce 12.4 mol% NO and 6.5 %
  N2O in the off-gas.
- Product: HAS 56.77 kmol/h x 164.14 = 9 318 kg/h = 25.4 wt%. AS 682 kg/h = 1.86 wt%.
  Total H2SO4 66.8 kmol/h = 6 650.7 kg/h x 0.985. HNO3 0.26 wt%.
- Reaction heats: -227.6, -508.6 and -192.2 kJ/mol NO reproduce from the stated NBS values.
  The R-201 reaction heat of 8.77 MW and the acid-dilution heat (E-201, from 350 K to 313 K)
  are consistent.
- Utilities per kg NH2OH reproduce: power 355 kW / 3 750 = 0.095 kWh; CW 24 342 kW = 6.49 kWh;
  LP heat 0.198 kWh; MP export 1.86 kWh.
- A rough whole-plant energy balance by the reviewer (reaction heats with vapour water + latent
  heat of the dilution steam + LP heat + power against CW + MP steam + flue gas) closes within a
  few % at concept accuracy.
- Plausibility: 84 % of NH3-N to NH2OH (0.61 t NH3/t NH2OH against 0.52 stoichiometric) and
  0.13 t H2/t NH2OH (0.092 stoichiometric) are of the order expected for NO-hydrogenation
  plants. The N2O of 7.5 kg/t caprolactam equivalent lies inside the IPCC default range. The
  burner temperature is inside S1's range.
- Sources: every key value is either cited with a locator in the DESIGN.md source register
  (S1-S7, S9, S10) or marked ASSUMED. S8 (NBS) is openly flagged as not re-read (O-4), and its
  heats are carried as `provenance: assumed`. Ullmann is a lead only, not used for numbers.
- Licences: no third-party table, figure or passage copied. Patent facts are summarised in the
  authors' own words with locators. The BFD/PFD are generated by `cheme process build` from the
  case's own YAML.
- Scope and boundary: the route, product form (25.4 wt% solution, per kg NH2OH) and boundary
  (NO generation inside, justified in D-001) match the job brief for issue #182. Registry entries
  that are missing are listed for the consolidated PR rather than added outside the folder.

## Not checked
- Tiles of the PFD/BFD, read only at sheet scale (finding #11). No P&IDs, layout, datasheets,
  HAZOP or control files exist at this stage.
- The cited patents and the IPCC chapter were not re-read by the reviewer. The values were
  checked for internal consistency and plausibility only, not against the documents.
- Energy closure in core (not evaluable: no property package for nitrous gas with steam or the
  aqueous salt solution; core #315, #364). The reviewer's balance is a hand estimate.
- The flammability and explosion limits of the burner feed and the cascade loop gas (O-7): these
  need a process-safety specialist with sourced limit data.
- `cheme diff main --list`: not applicable (no plant items on P&IDs).
