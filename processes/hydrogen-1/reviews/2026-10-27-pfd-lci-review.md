---
topic: design
reviewed_commit: 84db928743610abf8e92c64d9dda30cd0f958ff4
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, scripts/h2_balance.py, lca/]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydrogen-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI, issue #117)

Independent review of the hydrogen-1 case (natural-gas SMR, HT shift, PSA, tail-gas firing,
steam export) as committed on `case/hydrogen-1` (commits c66ab70, 8eb5921, fb2c8d4, 84db928
on top of `origin/main`). The reviewer did not write the design. Every command quoted below
was re-run by the reviewer on 84db928; the run report was not taken on trust.

The finding ids follow the repository format (`<file stem>#n`); the R-nn labels asked for in
the review brief are given in the finding text.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | lca/lca.yaml:24-25, lca/results.md:13 | allocation, headline result | (R-01) Export steam is a big co-product (10.55 kg/kg H2, about 83 MW of 4.3 MPa steam against 299 MW of H2 LHV). Even so, `allocation: method: none` puts 100 % of the stack CO2 on hydrogen, and `results.md` headlines "partial screening carbon footprint ... 10.0997 kg CO2-eq". The same table shows a mass-allocation alternative (8.7 %, 0.87 kg) that has no physical meaning for steam. `lca/README.md`, D-013 and the run report all say this is direct stack CO2, not a footprint, and that allocation is still open. But a reader of `results.md` alone sees a single number that mixes in the steam's share. A rough system-expansion credit for steam from a natural-gas boiler would be of order 2 kg CO2/kg H2 (reviewer's estimate, not a result). | medium | open | Decide on the steam treatment (system expansion with the substitute named in `lca.yaml`, or energy/exergy allocation) before any number is quoted. Until then, put a line at the top of `lca/README.md` and in `process.yaml` validation notes saying that the 10.10 kg figure is unallocated and includes the steam's share. |
| 2026-10-27-pfd-lci-review#2 | lca/lca.yaml:94-100, lca/inventory.csv | emission:CH4, CO, C2H6, C3H8, H2 | (R-02) Unburnt CH4, CO, C2H6, C3H8 and H2 are inventory exchanges at "0 kg, calculated". In `results.md` CH4 goes through its GWP factor (0 x 29.8 = 0). The zero comes from the complete-combustion assumption (D-009), not from an emission estimate, so a downstream user of `inventory.csv` or `dataset.yaml` would read it as a determined zero. NOx and N2O are not listed at all. `cheme assess lca --coverage` still warns `cheme.lci-emissions-incomplete [H-301]`. The comment in `lca.yaml` and the README open items do state the gap. For gas-fired heaters the climate effect is small, so the headline number does not change. | medium | open | Replace the zero-valued combustible exchanges with `emission_estimates` (sourced factors for CH4, N2O, CO, NOx, PM of gas-fired process heaters), or with `emission_exclusions` that give the reason. Do not export determined-looking zeros. |
| 2026-10-27-pfd-lci-review#3 | process.yaml:36 | maturity | (R-03) `process.yaml` claims `maturity: concept`. `cheme maturity` reports `level: none` and warns `cheme.maturity-claim-exceeds`, because the boundary and the model basis are not sourced. The manifest explains this honestly in a comment and in `validation.notes`: `concept` is the lowest value of the schema enum, and `validation.status: unreviewed`. A reader of the catalogue's maturity field alone does not see that. | low | open | Keep the explanation. Ask the library to add a level below `concept` (or a `maturity_evidence: none` field) so that the claim and the evidence can agree; record this in D-011. |
| 2026-10-27-pfd-lci-review#4 | DESIGN.md:162, :167 | D-010, E-402 / E-101 | (R-04) D-010 describes the economizer E-402 as "flue gas 553 -> 423 K". In `scripts/h2_balance.py` (lines 276-282) the 553 -> 423 K zone also carries the low-temperature part of the feed preheat E-101 (about 4.9 MW): E-402's 9.35 MW alone cools the flue gas by only about 85 K. The duties are consistent, but the coil order in the text is not. The feasibility statement leaves out the E-101 low-temperature coil, whose hot end (feed to 533 K against flue gas at 553 K) has the tightest approach, 20 K. | low | open | Rewrite D-010 with the real convection coil order and the temperatures at each coil boundary from the script, including the 20 K approach of the E-101 cold coil. |
| 2026-10-27-pfd-lci-review#5 | DESIGN.md:191 | D-011 plausibility | (R-05) D-011 says the plant figures were "not compared with a published benchmark". The reviewer's comparison with general engineering knowledge finds them plausible (see Checked and fine), but the design itself cites no benchmark for the specific natural gas consumption, the methane slip, the PSA recovery or the steam export. | low | open | At the next stage, add a cited benchmark comparison (specific consumption in GJ per 1000 Nm3 H2 net of steam export, methane slip, PSA recovery range, direct CO2 per kg) to D-011 in our own words, together with the reaction-evidence file D-003 already plans. |
| 2026-10-27-pfd-lci-review#6 | lca/README.md:63-75, DESIGN.md:169-172 | process condensate | (R-06) The process condensate (S15, 49 t/h) goes straight back to boiler feed water with no stripper or deaerator (D-010 rejects them for this stage). The LCI's open items list combustion emissions, consumables and construction, but not the stripper or deaerator vent, which carries dissolved CO2 and traces of methanol and ammonia once modelled, nor the deaerator steam. | low | open | Add the condensate stripper or deaerator vent (and its steam) to the LCI open items and to D-013, so that the gap is described. |
| 2026-10-27-pfd-lci-review#7 | process.yaml:55-56 | chemistry inputs | (R-07) Natural gas (feedstock and trim fuel) is registered as `chemical: methane`, because `chemicals/chemicals.yaml` has no natural-gas entry (D-014). The note says it is 93 % CH4, but a catalogue reader filtering by chemical sees pure methane. | low | open | Add `natural-gas` (and CO, ethane, propane, demineralised water) to the registry in the consolidated PR named in D-014, then re-point both inputs. |
| 2026-10-27-pfd-lci-review#8 | checks/checks.yaml | gates | (R-08) `cheme check` fails `layout-plot-plan` (concept), `pids-exist`, `design-review`, `layout-3d`, `lifting-study`, `mto`, `layout-review` (basic) and `layout-detail`, `electrical`, `hvac`, `datasheets` (detail). Apart from `design-review`, which this record addresses, these are outside the scope of this run: the task excludes P&IDs, layout and datasheets. The run report says the same. | low | open | No action at concept. Before a basic-engineering stage, either deliver these or record a decision on which gates the library case is not meant to reach. |

## Previous findings
None: this is the first review record of this plant (`ls reviews/` before this record:
README.md only; `grep -h '| open |' reviews/*.md` finds nothing).

## Drawing
No P&ID in `pid/` (out of scope for this run, `pid/README.md` only). `process/BFD.xml` and
`process/PFD.xml` are generated from `process/flowsheet.yaml`. `cheme validate` reports no
`generated-sheet-drift` or `cheme.generated-edited` and prints no `drawing <sheet>:` count line
for them, so no drawing-lint counts can be quoted. The BFD and PFD were not rendered or read
in tiles (see Not checked).

## Checked and fine
- **Commands re-run on 84db928.**
  - `cheme validate`: 18 files, 0 errors, 0 warnings (infos only: catalyst poisons not
    declared as components, port cycles cut by the loader, D-023 in a template comment of
    `checks/checks.yaml`).
  - `cheme process streams`: all 6 blocks and 25 steps balance ("ok") with reaction extents.
  - `cheme process propagate --check`: exit 0, nothing to change.
  - `cheme impact`: nothing to review.
  - `cheme maturity`: level none (R-03).
  - `cheme assess lca --coverage`: partial screening, 6 technosphere gaps plus 5 elementary
    flows outside the method. Mass, element and carbon-origin balances are closed. Warnings:
    `lci-emissions-incomplete` (R-02) and the uncharacterised elementary flows.
  - `cheme run scripts/h2_balance.py` reproduces every boundary flow, duty and the CO2 split
    quoted in DESIGN.md, the flowsheet and the LCI (carbon in 2090.619 = CO2 out 2090.619
    kmol/h; 8.475 + 1.625 kg CO2/kg H2).
- **Scope.** Nothing outside `processes/hydrogen-1/` changed (`git diff --name-only
  origin/main..HEAD`). The route and boundary match issue #117's case notes: SMR, HT shift,
  PSA, tail gas as reformer fuel, steam export, pre-reformer optional and rejected with a
  reason (D-007), process and combustion CO2 kept apart (D-013).
- **Mass balance, hand-checked.**
  - S/C = 5196.5 / (1696.5 x 1.021) = 3.00.
  - H2 made: 3 x 1192 (SMR) + 517.6 + 597.8 (WGS) + 5 x 59.4 + 7 x 11.9 + 50.9 recycle
    ≈ 5122 kmol/h, against 5128 kmol/h in the PSA feed (0.1 %).
  - PSA: 0.88 x 5128 = 4512 kmol/h product, of which 50.9 kmol/h is recycle (split 0.01128).
  - Water consumed by reaction ≈ 2462 kmol/h. The condensate of 2717 kmol/h plus about
    17 kmol/h of vapour to the PSA (y_H2O = p_sat(313 K)/2950 kPa) closes the water.
  - Excess O2 in the flue gas = 185 / (2036 − 185) = 10 %.
- **Energy balance and duties, hand-checked.**
  - Duties against IAPWS enthalpies: steam drum 189.7 t/h from 503 K to 673 K at 4.3 MPa
    ≈ 116.6 MW (WHB 50.5 + coil 66.4); E-201 36.6 MW (BFW side 36.5 MW, and the gas side
    includes the water condensing below its dew point of about 446 K); convection section
    total 103.4 MW against about 102 MW from flue cp x ΔT.
  - Machines: FD fan 456 kW, ID fan 686 kW, BFW pump 357 kW, against 448, 669 and 359 kW.
  - Fuel LHV: tail gas H2 41.3 + CH4 86.2 + CO 18.2 = 145.7 MW; trim 73.3 MW; feedstock
    382 MW.
  - Overall first law on an LHV basis: 456.8 MW in (NG + power). Out: H2 299.4, export steam
    ≈ 82.7, stack sensible ≈ 14.5, cooling water 30.1, blowdown 0.6, plus ≈ 30 MW to vaporise
    the liquid make-up water consumed by reaction. That totals ≈ 457 MW: closed within about
    0.5 MW. The script's duties are mutually consistent.
- **Plausibility against general engineering knowledge.**
  - Methane conversion 75.5 % and 6.1 mol% dry slip at 1143 K / 3.2 MPa / S/C 3.
  - About 3.3 % CO dry after HT shift; 74 % H2 in the PSA feed; PSA recovery 0.88 at
    99.9 mol%.
  - Radiant efficiency 102 / 219 = 47 %; trim fuel a third of the firing (no air preheat).
  - Gross natural gas 0.45 Nm3/Nm3 H2 (180 MJ LHV/kg). Crediting the steam export at a 90 %
    boiler gives about 143 MJ/kg, or 12.9 GJ/1000 Nm3: in the usual range for a modern
    steam-exporting SMR.
  - Direct CO2 10.1 kg/kg; electricity 0.16 kWh/kg; steam export about 0.95 t/1000 Nm3. All
    plausible for this configuration.
- **Exchanger temperatures.** E-201, E-402, the steam coil and the WHB keep positive
  approaches. The tightest is 20 K at the hot end of the E-101 cold coil (R-04).
- **Provenance.** Every boundary and design value is `assumed` with a source (design basis,
  D-xxx, or `scripts/h2_balance.py`); there are no `given` values without a source. Script
  results are labelled assumed and say so (D-006, flowsheet header). DESIGN.md is open about
  what was not read: no rate law, no PSA source, no reaction-evidence file (D-003, D-008).
  Catalyst windows are flagged ASSUMED with their library source.
- **Licences.** No third-party tables, figures or passages found in DESIGN.md, the YAML,
  `lca/README.md` or the script: all text is the design's own wording. The LCI holds no
  licensed background values (all six technosphere flows `missing:` with a description of
  the activity to connect to). `lca/factors.yaml` uses only the packaged open profile.
- **LCI.**
  - Functional unit 1 kg H2 (S17). Every exchange equals a boundary stream divided by
    9109.9 kg/h, checked for NG, NGF, DMW, AIR, POWER, STEAMX, BD, CW and FLUE in
    `inventory.csv`.
  - Mass in 50.383 = out 50.383 kg/kg.
  - Feedstock and trim-fuel carbon are kept apart through two terminals. The trim fuel's
    supply-only mapping avoids counting combustion twice.

## Not checked
- The BFD and PFD were not rendered or read visually (no drawing counts are printed for
  generated sheets).
- The bibliographic details of the two references in `process.yaml` (the Ullmann's DOI and
  the Twigg edition) could not be checked without network access.
- Real-gas effects (Peng-Robinson at 3.2 MPa) on the equilibria, carbon-formation limits at
  S/C 3 with 4.9 % C2+ and no pre-reformer, and a pinch analysis: all open checks the design
  itself names (D-003, D-007, D-010).
- The issue #117 text (`gh issue view`) was not re-read: the scope was taken from the run's
  `task.md`.
- The equipment list against the PFD was checked only as far as `cheme validate`'s
  process-link check goes.
