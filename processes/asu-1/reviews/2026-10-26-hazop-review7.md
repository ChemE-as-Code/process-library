---
topic: hazop
reviewed_commit: a793d37d4b397f229afa41db8163fac005b93d9e
scope: [safety/hazop/H-01, safety/hazop/H-02, safety/hazop/H-03, safety/hazop/H-04, safety/hazop/SESSION.md, safety/risk-matrix.yaml]
reviewer: Claude (independent review agent; did not author D-114 or D-115)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), seventh independent review

This is an independent review of branch `claude/keen-lovelace-sd87qc` at a793d37: the revision
D-115 of H-01 .. H-04 and SESSION.md (`git diff 0841d30 a793d37 -- safety/`). D-115 answers
hazop-review6 #1 .. #12 and carries D-114 into the studies. I read every scenario that D-115
changed or added, by id, before and after. I checked each one against the C&E, loops.yaml and
each study's `assessment_basis` credit convention: an interlock whose SIL is not confirmed takes
one order; a safeguard that shares its sensor or final element with the cause takes none.

**Verdict.** All 12 findings of hazop-review6 are closed by a793d37, with the I-14 credit
resting on the D-114 effect change in 0841d30. The revision is mechanically clean:
- the stamps and bands are current;
- the counts are right;
- nothing is accepted on anyone's behalf.

This record raises 4 new low findings and no critical, high or medium one. The I-14 bases
overstate how quickly the boiling stops (control-review7#1). A spurious I-19 trip is not
studied. The scenarios for air loss with power on sit in a mode defined for power loss. One
note repeats a wrong statement about the matrix bands.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-hazop-review7#1 | H-03, H-04 | H03-S33, H03-S34, H04-S75, H04-S80, H04-S92, H03-SG27, H04-SG39 | The one-order I-14 credits are now valid in principle, because I-14 stops the air through the motor breakers, apart from FV-3111 and the control system. But their bases say "once the air stops E-3103 no longer boils", "the boil-down stops whatever the refrigeration does" and "the PV-4101B vent then carries only the standing vapour". After the MAC trip, the air-path inventory and the HP column vapour and flash keep condensing in E-3103 for some minutes, so the LP sump keeps boiling down (control-review7#1). The credit holds only if the LSLL-3125 margin covers that boil-off. That margin is not yet set (#103). | low | open | Keep the one-order credit. In the bases, write "provided the LSLL-3125 margin covers the post-trip boil-off (control-review7#1, #103)", and list that condition in SESSION.md 3.7 for the team. |
| 2026-10-26-hazop-review7#2 | H-01, H-04 | I-19 (PSLL-1116), spurious trip | I-19 is a 1oo1 low-pressure trip that stops the whole plant: the MAC set, the compander, K-4101 and K-4102. H03-S54 studies the spurious trip of I-14 (2/D medium, a plant stop with the backup), but no scenario studies a spurious PSLL-1116 trip, for example a transmitter fault or a short header dip at an IA dryer change-over. Its consequence is the same plant stop, and it is likelier than an I-14 spurious trip if the switch sits at the package outlet. | low | open | Add a scenario under H01-N4 or H04-N2-OP for a spurious I-19 trip (asset 2, with the backup), and give the vote and delay (2oo3, 10 s) to the SRS with H03-A4's spurious-trip weighing (#106). |
| 2026-10-26-hazop-review7#3 | H-01, H-04 | modes, H01-S45, H04-S93, H04-S95 | The new scenarios for "instrument-air failure with power on" are tagged `power-fail`. Each study defines that mode as "loss of power, and of instrument air where it follows". Air loss with power on is the case that control-review6#2 asked to be added as its own case, and it is not a power failure. A team that filters the worksheet by mode will not find these scenarios under a matching heading. | low | open | Add a mode `air-fail` ("loss of instrument air with power on") to H-01 .. H-04 and tag H01-S45, H04-S93 and H04-S95 (and the D-109 air-loss branches) with it. Or widen the description of the power-fail mode. |
| 2026-10-26-hazop-review7#4 | H-04, SESSION.md | H04-S95 notes, SESSION.md 3.7 | The H04-S95 note says "A rating of 5/B stays high under this matrix although the LOPA target (asset 1e-3) is met: the asset targets sit in the matrix's medium band". Under safety/risk-matrix.yaml, 1e-3 at severity 5 is the B/C boundary, which is high on both sides. The asset targets sit in the high band, which is why the rating stays high (control-review6#5, still open). The team should not be told the opposite. | low | open | Correct the note, and SESSION.md 3.7's I-19 item, to say that the asset targets of D-111 / D-114 lie in the matrix's high band, for #106. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-26-hazop-review6#1 | I-14 credited in H03-S33 although its only effect on the LOX over-draw was closing FV-3111, the valve of the cause. | high | closed a793d37 | C&E I-14 no longer acts on FV-3111 (0841d30). It stops the air and K-4101 through motor breakers. The H03-S33 residual basis says so (5/A medium, one order, convention kept). H03-SG27 is retitled. The remaining caveat is #1. |
| 2026-10-26-hazop-review6#2 | I-14 credited in H03-S34 (refrigeration deficit) though a K-4101 trip does not arrest a deficit. | medium | closed a793d37 | With the MAC stopped, the deficit no longer drives a boil-down. The H03-S34 basis explains this, and states that a K-4101 trip alone would not have arrested it. Caveat #1. |
| 2026-10-26-hazop-review6#3 | H01-S13 credits the LIC-1106 alarm for a "LIC-1106 fails low" branch. | medium | closed a793d37 | H01-S13 is now "LV-1106 sticks closed (LIC-1106 healthy)", 4/D -> 4/B medium, with the mist eliminator dropped. The new H01-S46 "LIC-1106 fails low", with I-06 only, is 4/D -> 4/C high, with H01-A3. |
| 2026-10-26-hazop-review6#4 | D-110 ratio-limit credit lowers H04-S79 / S80 / S85 although the TSA dip is not tracked. | medium | closed a793d37 | H04-S79 3/E -> 3/D high. H04-S80 5/D very-high -> 5/B high. H04-S85 3/E -> 3/D high. The clamp / limit is not credited in any of them, the causes name the TSA dip every cycle and FT-1101 high, and S85's text is current. All three are treated alike. |
| 2026-10-26-hazop-review6#5 | H-01 .. H-03 do not stamp control/loops.yaml (and H-02 not sequences.yaml). | medium | closed a793d37 | `analysed:` now holds control/loops.yaml in H-01, H-02 and H-03, and control/sequences.yaml in H-02. `cheme validate` reports no hazop-input-changed. |
| 2026-10-26-hazop-review6#6 | H02-S13 cause "FV-2105 fails closed" against D-109. | low | closed a793d37 | The cause now reads "FV-2105 sticks closed or FIC-2105 fails low ... (FV-2105 fails open on loss of air or signal, D-109)". |
| 2026-10-26-hazop-review6#7 | I-08 and I-10 credited one order each without recorded independence. | low | closed a793d37 | H02-S13, S15, S17 and S20 now credit the pair once (3/D -> 3/C medium). The H02-SG6, SG7 and SG20 notes give the shared protection relay and supply. |
| 2026-10-26-hazop-review6#8 | H03-S54 understates the latched state after a spurious LSLL-3125 trip. | low | closed a793d37 | H03-S54 is now a whole-plant stop, latched until repair or a bypass under permit, with no purge part (FV-3111 is no I-14 effect), 2/D medium, and H03-A4 weighs 1oo2. |
| 2026-10-26-hazop-review6#9 | The 30 min vent alarm is credited below the 70 % minimum and bundled in SG42. | low | closed a793d37 | H04-SG43 is the alarm (kind alarm). SG42 holds the ratio limits only. H04-S76 covers the turndown inside the range (3/C medium). The new H04-S91 covers the vent below 70 % without the alarm credit (3/D -> 3/C medium, H04-A26). |
| 2026-10-26-hazop-review6#10 | No scenario names air loss as a cause of a GOX vent at VNT-4003. | low | closed a793d37 | H04-S03's cause names its own signal or air loss. The new H04-S93 (plant-wide air loss, 3/D -> 3/C medium, H04-A26, zones owner) covers the vent. |
| 2026-10-26-hazop-review6#11 | SESSION.md node table, Session 0 minutes and total stale. | low | closed a793d37 | The rows recomputed from the studies agree with SESSION.md: H01-N4 6 / 9, H03-N8 5 / 6, H04-N1 7 / 15, N2 7 / 10, N9 5 / 7. The study totals 229 / 198 / 276 / 445 min equal 5 min per node plus 4 per scenario. Session 0 is 4 h, the total about 23 h. |
| 2026-10-26-hazop-review6#12 | D-113 (2) omits H01-S1, H01-S5 and H04-S04. | low | closed a793d37 | D-115 #12 records them. |

## Checked and fine
- `cheme safety hazop check H-01 .. H-04`: each `draft`, with 0 errors, 0 warnings and 2 infos
  (proposals not accepted: 111 / 79 / 113 / 181; the matrix is proposed). The review line names
  hazop-review6#1 as open, which this record closes.
- `cheme validate`: 129 files, 0 errors, 97 warnings (none in the studies), no
  `hazop-input-changed`. `cheme safety hazop rate H-01 .. H-04` (without --write) exits 0, and
  all 580 ratings are `current`.
- **Recount** (scratch script `build/r7_count.py` over the YAML; worst band, residual where
  rated):
  - 232 scenarios (46 / 37 / 54 / 95);
  - high 79 (9 / 12 / 21 / 37), medium 98 (17 / 18 / 23 / 40), low 55 (20 / 7 / 10 / 18);
  - 9 very-high initial: H02-S22, S27, H03-S29, H04-S05, S30, S38, S55, S60, S80;
  - 94 actions (26 / 14 / 23 / 31);
  - every high scenario has an action, and every scenario has a residual rating;
  - no duplicate id.

  These equal D-115 and the SESSION.md state table, 3.3 (nine) and 3.4 (79).
- **New scenarios and credits:**
  - H01-S46: 4/D -> 4/C high. Only I-06 is credited; the shared-transmitter alarm is not.
  - H04-S91: 3/D -> 3/C. Only the elevated vent is credited, one order.
  - H04-S92: 5/C -> 5/A medium. The LICA-3102 alarm and I-14 take one order each, and the
    PIC-4101 alarm of the failed loop is not counted.
  - H04-S93: 3/D -> 3/C medium.
  - H04-S94: people 4/C -> 4/B through the fire wall, as H04-S05 / S07. Asset 5/C stays high,
    because the discrepancy alarms are not in the files and I-13 acts after ignition.
  - H04-S95: people 4/C -> 4/A (I-19 plus the fire wall, one order each); asset 5/C -> 5/B high.

  Each follows its study's convention, and each high one has an action (H01-A3, H04-A13,
  H04-A01).
- **Revised scenarios:**
  - H01-S45 credits I-19 one order (2/D -> 2/C low).
  - H03-S35's cause no longer names I-14.
  - Node texts H03-N8 and H04-N1 and the new deviation H04-N2-OP agree with the C&E.
  - Status: every node, deviation, scenario, rating, safeguard and action is `status: proposed,
    by: agent`. No `accepted`, no `accepted_by`, no action closed, and none added (94).

## Not checked
- The LOPA rows themselves (control-review7 #2, #3 and control-review6 #5 .. #7). The HAZOP
  credits do not use their SIL beyond one order.
- The scenarios D-115 did not touch, beyond what earlier reviewers confirmed.
- The post-trip boil-off (#1, control-review7#1), which needs the sump geometry and a dynamic
  check.
- The team session, the matrix acceptance and the human review (the owner's).
