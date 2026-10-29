---
topic: design
reviewed_commit: 2fa1746ee8ba43e4ec4a0cc6bcfa3ed79b73053d
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, lca/, process.yaml, scripts/balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/sodium-nitrite-1
merge: pending
---

# Sodium nitrite (sodium-nitrite-1) concept design and preliminary LCI: independent review

Branch `case/sodium-nitrite-1` (issue #168): 8 commits (97dcee7..2fa1746) on merge-base 9493d54.
I am an independent agent and did not write this design. I reviewed the design files and the
LCI and changed none of them. The run was scoped to concept work (design basis, balanced
BFD/PFD, preliminary gate-to-gate LCI), so P&IDs, layout, datasheets, HAZOP and TEA are out of
scope (see `runs/20261028-161008-design/task.md`).

The ids follow the repository format `<file stem>#n`. The task's short ids map one to one:
R-01 = #1, R-02 = #2, and so on.

## What I re-ran myself (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only $(git merge-base origin/main HEAD)..HEAD` | every changed path is under `processes/sodium-nitrite-1/`. The plain `origin/main..HEAD` diff shows deletions in other folders (e.g. `processes/thf-1/`). That is only because the branch starts from an older main (9493d54); this branch removes nothing |
| `cheme validate` | 16 files, 0 errors, 0 warnings. Infos only: `dexpi.load` reference cycles, and `cheme.decision-unknown D-023` from the commented template example in `checks/checks.yaml:76` |
| `cheme check` | every concept gate passes except `layout-plot-plan`, which is out of scope. The basic and detail gates fail on missing P&IDs, layout, datasheets and (until this record) the design review, as expected at this stage |
| `cheme maturity` | calculation maturity none, design maturity supported none. `cheme.maturity-claim-exceeds` warns on `maturity: concept`, which is the lowest value the schema allows (see Checked and fine) |
| `cheme process streams` | 4 blocks and 11 steps all ok. Extents: NH3_OX 9.685, NH3_N2O 0.1396, NH3_N2 0.1600, NO_OX 10.963, NITRITE_ABS 18.752, NITRATE_ABS 1.587, INVERSION 1.0706, CARB_NEU 0.0697 kmol/h |
| `cheme process propagate --check` | exit 0, nothing reported |
| `cheme assess lca --coverage` | partial screening carbon footprint. 8 gaps (7 `missing:` backgrounds, each with a description, plus NO outside the method). Mass, element and carbon-origin balances closed. DQR 2.33 |
| `cheme impact` | nothing to review |
| `cheme diff main --list` | process items only (PFD/BFD streams, sources, sinks, templates). No P&ID items |

## Hand checks of the numbers

- **Nitrogen.** NH3 680.19 kg/h = 39.94 kmol/h. HNO3 239.5 x 0.6 / 63.012 = 2.280 kmol/h, so 42.22
  kmol N/h enters. Out: NaNO2 in the product 35.88, NaNO3 in the product 0.24, NaNO3 co-product
  4.69 (40.82 kmol/h in products), N2O-N 0.559, N2-N 0.640 and NO 0.204, which is 42.22 kmol/h.
  Closed.
- **Absorber.** NOx to C201: 38.74 (burner) + 2.14 (inversion NO) = 40.88 kmol/h. 99.5 % of it
  absorbed gives 40.68 kmol/h, which equals 2 x 18.752 + 2 x 1.587. NaNO2 formed is 2 697 kg/h
  and NaNO3 135 kg/h, so 20.0:1, as stated. NO2 needed is 18.75 + 3.17 = 21.93 kmol/h, which
  equals 2 x NO_OX. That is an oxidation degree of 0.537.
- **Sodium and carbon.** Soda 2 164.37 kg/h = 20.42 kmol/h = 40.84 kmol Na/h, matching the Na in
  the products. CO2 in the tail gas is 20.41 kmol/h, i.e. all carbonate carbon except the 0.013
  kmol/h that stays in the product.
- **Tail gas.** Dry basis: O2 11.71 of 305.1 kmol/h (3.84 %), NOx 670 ppmv, N2O 916 ppmv. The
  water saturation at 40 degC / 105 kPa(a) (7.0 mol-%) matches IAPWS. Air at 10.30 mol-% NH3
  matches SRC-3.
- **Burner duty.** By hand, the heat released at 298 K is 2 435 (NO) + 43 (N2O) + 56 (N2) = 2 534
  kW. Less the sensible heat of the outlet to 473 K (about 570 kW), that leaves about 1 960 kW,
  against 1 964.2 kW from cheme. The adiabatic gauze temperature for 10.3 % NH3 from about
  30 degC comes out near 870 degC, inside SRC-3's 850-950 degC.
- **Crystalliser, inversion and nitrate line.** Component and water balances of CR301, D301,
  R401, CR401 and D401 recomputed. Inversion acid 143.7 kg/h HNO3 (239.5 kg/h of 60 %); NO
  released 64.2 kg/h; nitrate liquor 399.0 kg/h NaNO3. All consistent.
- **Duties.** These reproduce from the stated assumptions: dryers (2 500 kJ/kg / 0.5),
  CR301 (sensible heat 125 to 55 degC plus 13.9 kJ/mol), C201 (gas sensible, condensation, NO
  oxidation, absorption, about 1.67 MW against 1.73 MW), blower (about 83 kW isentropic against
  84.5 kW) and CR401 (single effect). The assumptions themselves are questioned in #1, #2, #4 and
  #5.
- **LCI.** Allocation factor 2 500 / (2 500 + 399.37) = 0.8623. Allocated inputs 13 118.55 /
  2 500 x 0.8623 = 4.5246 kg/kg, equal to the allocated outputs. Climate total 0.3098 + 4.244 g x
  273 = 1.468 kg CO2-eq/kg, 79 % from N2O. The inventory quantities equal the flowsheet streams
  divided by 2 500 kg/h, times 0.8623.
- **Source check.** I re-read SRC-2 (US 2 032 699, Google Patents). Its facts as used are
  correct: about 9 vol-% NOx, 215 g/l soda in three towers, about 40:1 nitrite:nitrate formed,
  storage liquor 25/5 %, about 1 000 g/l at about 125 degC, crystalliser about 65 to 55 degC,
  mother liquor 33/17/1.1 %. I also re-read SRC-3 (US 12 565 427 B2); see #3.

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | PFD | E301, Q6, feed:LPS (`scripts/balance.py:202-204`, DESIGN.md D-010) | (R-01) The evaporator steam is computed as evaporation x 2 257 kJ/kg / 1.8, so it counts latent heat only. It leaves out heating the feed: 12.2 t/h of liquor at 40 degC and 3.65 t/h of recycle at 55 degC, brought to the 125 degC concentrate. That is about 1.1 MW at cp 2.8-3.3 kJ/kg K. Boiling-point elevation of a near-saturated nitrite liquor (some 20 K) is also ignored, and so is the heat left in the 8.7 t/h condensate, which is sent to the dissolver at 60 degC with no stated heat recovery. With a cold feed, the 1.8 economy is optimistic. The external LP steam (1 245 kW to E301, two thirds of the plant's 1 837 kW and of the LCI's 0.634 kWh/kg) is probably understated by tens of percent. The mass balance is unaffected. | medium | open | Add the feed sensible heat (with any condensate/feed preheat shown explicitly) and a BPE allowance to the E301 duty, or justify the 1.8 economy for these conditions with a source. Then update Q6, Q7 and feed:LPS and rewrite the LCI. |
| 2026-10-28-pfd-lci-review#2 | PFD | E301, Q6 (DESIGN.md D-010, design-basis `utilities`) | (R-02) The temperature feasibility of site LP steam at 450 kPa(a) (147.6 degC) in E-301 is not shown. The concentrate leaves at 125 degC and 120 kPa(a), i.e. at or near atmospheric pressure with a large BPE. In a double effect ending there, the first effect has to boil at roughly 140-150 degC, so it needs steam above about 155 degC. The 1 000 kPa(a) WHB steam (180 degC) can drive it; 4.5 bar(a) steam cannot. D-010 still sends the "balance" of the evaporator heat to LP steam. | medium | open | State the effect pressures and temperatures. Either supply the balance heat at a higher level (MP steam, or more WHB steam), run the second effect under vacuum (then revise the 125 degC / 120 kPa concentrate state), or show that the LP steam serves a duty it can reach (e.g. feed preheat). Record the choice in D-010. |
| 2026-10-28-pfd-lci-review#3 | - | NH3_N2O, emission:N2O (`process/reactions.yaml` NH3_N2O, DESIGN.md D-005/D-013) | (R-03) N2O (79 % of the direct climate result) is set by analogy to the IPCC atmospheric nitric-acid default: 1.4 % of NH3, 12.3 kg/h, 0.018 kg N2O per kg NH3. The register lists SRC-3, an actual nitrite-plant burner, as "read". Its example states an N2O outlet of 19-20 kg/h from 546.4 kg/h NH3, about 0.036 kg/kg or 2.8 % of the NH3 nitrogen, i.e. about twice the assumed value. DESIGN.md does not mention this. At SRC-3's ratio the direct footprint would be about 2.6 instead of 1.47 kg CO2-eq/kg. SRC-3's example is itself not mass-consistent: its NO + NO2 outlet holds more nitrogen than its NH3 feed. That is why this is not rated higher, but the conflict should still be reported. | medium | open | Record SRC-3's N2O figure (with its inconsistency) in section 3 / D-005 as conflicting evidence. Add an N2O sensitivity, e.g. 1.4 % and 2.8 % of NH3, to the LCI or at least to D-013. State in D-013 and `process.yaml` that the N2O share is an analogy with an uncertainty of about a factor of 2. |
| 2026-10-28-pfd-lci-review#4 | PFD | S16, DESIGN.md section 4 "mother liquor recycle" | (R-04) The basis table says the 1.5 kg/kg mother-liquor recycle has "no effect on the external balance". It does affect it: the recycle's 1 786 kg/h of water is evaporated again in E-301 (20 % of the 8 996 kg/h). That sets part of the LP steam and CW, which are external exchanges of the LCI. | low | open | Reword: no effect on the external mass balance, but it sets about 20 % of the E-301 duty. Treat it as a sensitivity alongside #1. |
| 2026-10-28-pfd-lci-review#5 | PFD | S4, K101 (`scripts/balance.py:161,226`) | (R-05) The blower raises 101.3 to 131.3 kPa(a) at an isentropic efficiency of 0.75, which gives an outlet near 318 K. S4 is set to 303.15 K with no aftercooler. The burner inlet enthalpy, and so the WHB steam, are understated by about 40 kW. | low | open | Use the blower outlet temperature in S4 (or add the cooler) and rerun the burner duty. |
| 2026-10-28-pfd-lci-review#6 | PFD | T201, S8 | (R-06) The soda dissolver has no energy stream. Mixing condensate at 60 degC with soda at 25 degC plus the heat of solution of Na2CO3 (about -26.7 kJ/mol from the SRC-8 values, about 150 kW) gives about 70 degC, not the 45 degC set for S8. The difference ends up in the C201 cooling water. | low | open | Give T201 a cooler (CW duty), or set S8 to the adiabatic temperature and let C201's duty take it. |
| 2026-10-28-pfd-lci-review#7 | - | DESIGN.md D-002/D-005, SRC-3 row | (R-07) Two comparisons with SRC-3 are left unexplained. (a) SRC-3's example gives about 1.06 t/h NaNO2 (2 700-2 750 kg/h of 38-40 % liquor) per 546 kg/h NH3, about 1.9 kg/kg. The design gets 3.68 kg/kg, close to stoichiometric. The patent's own figures imply a low nitrogen yield or other products, and D-002 cites them only for sizing. (b) The WHB raises about 2.9 t/h here, against about 2.4 t/h scaled from SRC-3's 1.93-1.95 t/h; the design's burner feed is cold and SRC-3 preheats it to 140-170 degC. The register row quotes the 988-1 090 Nm3/h claim range, while D-002 uses the 546 kg/h example. | low | open | Add one sentence to D-002/D-005 on why the plant yield per NH3 and the steam differ from SRC-3's example, and quote which SRC-3 figures (example or claims) are used where. |
| 2026-10-28-pfd-lci-review#8 | - | lca/lca.yaml `emission:NH3`, `emission:NO2` | (R-08) NH3 and NO2 to air are declared `free: true` (zero burden), justified by their present 0 kg. Any later non-zero slip or NO2 split would then enter the LCI without characterisation. | low | open | Declare both as elementary emissions to air (`elementary: {compartment: air}`) with their 0 kg amount instead of `free`. |
| 2026-10-28-pfd-lci-review#9 | - | `process.yaml` chemistry notes | (R-09) The per-kg figures in `process.yaml` (NH3 0.272, soda 0.866, HNO3 0.096 kg/kg; power 0.076, LPS 0.73, CW 2.2 kWh/kg) are plant ratios before allocation. The LCI and D-013 give the allocated values (0.2346, 0.7465, ...). Only the CO2 note says "before allocation", so a reader sees two sets of numbers for the same exchanges. | low | open | Say "before allocation (plant ratio per kg NaNO2)" in each note, or quote the allocated values. |
| 2026-10-28-pfd-lci-review#10 | - | DESIGN.md D-008 (solubility plausibility) | (R-10) The plausibility argument cites "J. Chem. Eng. Data review 2021, as summarised" with no authors, DOI or locator, and two other values come from web search summaries. The near-saturation claim at 125 degC rests on these. | low | open | Give the DOI/locator of the J. Chem. Eng. Data review (or drop it), and mark these points as unverified in the source register. |
| 2026-10-28-pfd-lci-review#11 | - | DESIGN.md section 3 "NO/NO2 ratio control" | (R-11) The text says the plant holds the oxidation degree "near 0.5 and slightly below rather than above". The balance needs 0.537, i.e. above 0.5, because every nitrate needs excess NO2. The control statement reads as contradicting the model. | low | open | State the target as the balance value (about 0.53 for 20:1), controlled so that it does not exceed the value the nitrate specification allows. Keep the "NO excess favours nitrite" rationale. |
| 2026-10-28-pfd-lci-review#12 | - | lca/lca.yaml `emission:CO2`, D-013 | (R-12) Reporting soda-ash carbonate CO2 as a fossil emission here is right for a cut-off foreground. When feed:SODA is linked to soda-ash-1 (Solvay), that dataset must not also count the product-bound carbonate as emitted. Otherwise the CO2 is counted twice. This is not noted. | low | open | Add a note to D-013 and to the feed:SODA `missing:` text to check, when linking, that the background treats the carbonate carbon as bound in the product. |

## Previous findings

None: this is the first review record of this process (`reviews/` held only README.md, and
`grep '| open |' reviews/*.md` finds nothing).

## Drawing

No P&ID exists (`pid/` holds only README.md), so there were no drawing counts to quote. The BFD and
PFD are generated by `cheme process build`. `cheme validate` reports no `drawing` line for them
and no `cheme.generated-edited`. I did not render or read them visually (see Not checked).

## Checked and fine

- **Scope and boundary** match issue #168's case notes. The route is NOx from ammonia oxidation
  absorbed in soda solution, then crystallisation and separation. The nitrite/nitrate split and
  the nitrate disposition are stated (inversion to a NaNO3 co-product). NO/NO2 control is stated
  (see #11 for wording). Ammonia, soda ash and nitric acid are boundary feeds, with links to
  ammonia-1, soda-ash-1 and nitric-acid-1 noted.
- **Balances.** Mass, component and element balances close in every block and step. The
  plant-wide N, Na and C balances close by hand. The burner outlet and duty are calculated by
  cheme and confirmed by hand.
- **Provenance.** Key values are sourced or marked ASSUMED in `design-basis.yaml`,
  `reactions.yaml`, DESIGN.md section 4 and the stream provenance (`[A]` everywhere except the
  calculated S5).
- **Gated steps.** Electrolyte enthalpies and the multi-solute crystalliser are named precisely
  (core#364, #365/PR #395). The source register honestly separates read, summary, metadata and
  unverified entries (SRC-8 formation enthalpies flagged as recalled). The SRC-8 values used
  (NaNO2(aq) -344.8, NaNO3(aq) -447.48, Na2CO3(aq) -1157.38, Na2CO3(cr) -1130.68, HNO3(aq)
  -207.36 kJ/mol) agree with my own knowledge of the NBS tables, but I did not re-read the
  tables either. Verifying them stays an open input of DESIGN.md section 7.
- **IPCC default.** The value used (5 kg N2O per t HNO3 for atmospheric-pressure plants, Vol. 3
  Ch. 3 Table 3.3) and its conversion to 0.0143 mol N2O-N per mol product N are correct.
- **Licensing.** No third-party tables, figures or passages are copied. DESIGN.md and the
  `source:` fields give facts in own words with URLs, sections and status. Licensed sources
  (Ullmann) are used for route identity only.
- **LCI structure.** The functional unit is 1 kg of S18. Every exchange traces to flowsheet
  streams and energy streams. Allocation is mass-based, with the deviation from economic
  allocation stated. Every background is `missing:` with a description of the activity it
  should link to; none is zero-filled and no licensed value is used. `lca/mappings.yaml` holds
  no active overrides, with candidates listed, and the shared `lci/mappings.yaml` is untouched.
  Exclusions are listed with reasons. The inventory mass balance against the flowsheet closes
  (4.5246 kg/kg, allocated).
- **Maturity claim.** `process.yaml` claims `maturity: concept`, the lowest value of the schema
  enum. `validation.status: unreviewed`, `publication.status: internal`. The notes state
  honestly that `cheme maturity` reaches no level and why. The `cheme.maturity-claim-exceeds`
  warning cannot be cleared by a lower claim. This is the same situation as the other concept
  cases in the library.
- **Missing registry entries** for the consolidated PR are listed in DESIGN.md section 8.

## Not checked

- I did not look at the generated BFD/PFD drawings (no render). I relied on `cheme validate`
  and the stream table.
- I did not re-read SRC-4 (US 2 013 984), SRC-6, the IPCC page itself or the NBS tables (SRC-8).
- I did not check the plausibility of the ASSUMED electric loads (D-011), of the 0.05 kg/kg
  cake liquor (no washing), or of the product grade against a standard.
- Temperature feasibility of the other utilities, beyond #2, is not checked: the NH3 vaporiser
  on LP steam would work, but a lower-grade heat source would do.
- I did not run `build_lci.py` or the library tests.
- P&IDs, layout, datasheets, HAZOP and TEA are out of scope of this stage.

## Verdict

No critical or high findings. The balances close, the LCI is consistent with the flowsheet and
honest about its gaps. #1-#3 (evaporator steam, its temperature level, and the N2O evidence)
should be fixed before the LCI is linked to backgrounds or published. Merge is pending (a human
merges).
