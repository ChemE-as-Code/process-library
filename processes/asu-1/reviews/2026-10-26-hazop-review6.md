---
topic: hazop
reviewed_commit: 8ccc3234de6b689b057ce5164e4ad940c7718d29
scope: [safety/hazop/H-01, safety/hazop/H-02, safety/hazop/H-03, safety/hazop/H-04, safety/hazop/SESSION.md, safety/risk-matrix.yaml]
reviewer: Claude (independent review agent; did not author D-109 .. D-113)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), sixth independent review

Independent review of branch `claude/keen-lovelace-sd87qc` at 8ccc323: the revision D-113 of
H-01 .. H-04 and SESSION.md (`git diff ef7ad14 8ccc323 -- safety/ DESIGN.md`), made after D-109
(fail positions), D-110 (turndown and ratio limits), D-111 (I-05 .. I-18, screening LOPA,
FSLL-2117, LSLL-3125, PSHH-4152) and D-112. Every scenario D-113 touched was read by id before and
after, against the C&E, loops.yaml, the instrument list and each study's `assessment_basis`
credit convention.

Verdict: the revision is mechanically clean (stamps current, bands current, counts right, nothing
accepted on anyone's behalf), but **one high and four medium findings** on the engineering
content: two credits of I-14 that its effects do not support, a cause broadened so that it defeats
a credited alarm, a likelihood reduction from the D-110 ratio limit that its own cause text
contradicts, and fail positions the studies now rest on but do not stamp. Accepting #1, #3 and #4
as proposed would move H03-S33, H01-S13, H04-S79 and H04-S80 back to high (and H04-S80 back to
very-high initial), so D-113's counts and SESSION.md would change with them.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-hazop-review6#1 | H-03 | H03-S33 | I-14 (H03-SG27) is credited one order (5/B -> 5/A, high -> medium) although the cause is "FV-3111 fails open or FIC-3111 fails low" and I-14's only effect on the LOX over-draw is closing that same FV-3111 (`cheme validate`: info control-shared-element FIC-3111 / I-14 / FV-3111). The K-4101 trip does not stop a LOX over-draw. The study's convention gives nothing for a safeguard that shares a valve with the cause. D-111 row 10 makes the same claim. | high | open | Do not count I-14 in H03-S33 (residual 5/B, high, with H03-A4 / H03-A3) and rate again. If the team wants the credit, give I-14 its own final element on the LOX purge (a shut-off valve in series with FV-3111) through H03-A4, and correct D-111 row 10. |
| 2026-10-26-hazop-review6#2 | H-03 | H03-S34 | For a refrigeration deficit, I-14 is credited (5/B -> 5/A) because "the draws stop while the deficit lasts". But after the K-4101 trip PIC-4101 vents the GOX make through PV-4101B at VNT-4003 (H03-S54's own consequence, D-019, D-109), so the vapour leaving the LP column is unchanged. I-14 neither unloads the MAC nor restores refrigeration. The trip arrests an over-draw that lowers the LP pressure (H03-S33 via the K-4101 branch, H04-S75, H04-S80), not a deficit. | medium | open | Do not count I-14 in H03-S34 (5/B, high), or record how the trip arrests the boil-down under a deficit (hold-up against time). If a function is wanted, add a MAC unload or plant stop on LSLL-3125 to the C&E for the team's LOPA. Reword D-111 (3), which names H03-S34. |
| 2026-10-26-hazop-review6#3 | H-01 | H01-S13 | The revision adds "LIC-1106 fails low" to the cause but still credits the LIC-1106 high alarm in the one residual rating (4/B medium). For that branch the alarm shares the transmitter with the cause; the basis concedes this in words but not in the code. The mist eliminator does not stop a sump from flooding, so on that branch only I-06 is left (4/C, high). D-111 row 2 says "LIC-1106 is the initiator". | medium | open | Split the scenario: keep "LV-1106 sticks closed" as H01-S13 and give "LIC-1106 fails low" a new id with its own rating. Or rate H01-S13 at its worst branch (4/C, high). |
| 2026-10-26-hazop-review6#4 | H-04 | H04-S79, H04-S80, H04-S85 | The D-110 ratio limit uses FIC-1101, which measures the MAC discharge (S2) upstream of the TSA. A TSA switchover dip therefore happens at a constant FIC-1101 flow and is not tracked. S79's and S80's own causes still name that dip, which comes every TSA cycle. Lowering the cause likelihood from E to D ("a few times in the plant life"; S80 very-high -> high initial, both high -> medium residual) is not supported, and neither is S85's one-order credit of the clamp for the turndown branch. S85's cause and notes are stale: "clamp fixed at the design GAN draw (D-096)", "D-096 leaves the clamp as a ratio open (H04-A28)". S79 / S80 lower the initial rating while S85 credits a residual for the same D-110 change. | medium | open | Keep E for S79 / S80 (S80 initial 5/D very-high, residual 5/B high), or record why a TSA dip is too short or too small to reach the consequence (its duration against the column hold-up and the 5 min lag). Revise S85's cause and notes for D-110 and use one treatment for all three. Correct D-113 (6) and SESSION.md 3.3 / 3.4 with the result. |
| 2026-10-26-hazop-review6#5 | H-01, H-02, H-03 | analysed inputs | D-109's fail positions are recorded in control/loops.yaml (`fail:`), with the TSA valves in the instrument list. The causes and ratings of H01-S12 .. S17, S27, S45, H02-S13, S15, S32, S33 and H03-S12, S35, S50, S52 and the PV-3110B scenario now rest on them. Only H-04 stamps control/loops.yaml and control/sequences.yaml. A later change to a P-01 .. P-03 fail position or to KS-2101's restart behaviour would not raise hazop-input-changed in H-01 .. H-03. | medium | open | Once the team has reassessed: `cheme safety hazop stamp H-01 --input control/loops.yaml --write`, and the same for H-02 (also control/sequences.yaml) and H-03. |
| 2026-10-26-hazop-review6#6 | H-02 | H02-S13 | The cause still reads "FV-2105 fails closed", but D-109 sets FV-2105 to fail open. FV-1108 and TV-1105 were reworded to "sticks closed"; this one was missed. | low | open | Reword to "FV-2105 sticks closed or FIC-2105 fails low", as for FV-1108 and TV-1105. |
| 2026-10-26-hazop-review6#7 | H-02 | H02-S13, H02-S15, H02-S20 | I-08 (FSLL-2117) and I-10 (TSHH-2107) are each credited one order (D -> B). Both are SIL a trips of the same final element, the E-2101 supply, which `cheme validate` reports as also shared with TIC-2104. Their independence (separate logic and switching device) is not recorded. The same pattern existed before, then with the FIC-2105 trip. | low | open | The team decides. Either record in H02-SG20 / SG7 that the two trips use separate logic and separate switching devices (contactor apart from the thyristor), or credit one order for the pair (asset 3/C, medium). |
| 2026-10-26-hazop-review6#8 | H-03 | H03-S54 | With LSLL-3125 failed low, the latching I-14 cannot be reset, so FV-3111 stays closed until the transmitter is repaired or I-14 is bypassed. The consequence says the purge stops only "until the operator restores it". H03-SG19 (the FIC-3111 low-flow alarm) is listed, but the alarm only reports what the trip did. | low | open | State the latched state and the route back to a purge: repair, or a controlled bypass with compensating measures, or draining through HV-3118 (H03-A5). Keep the link to H03-S35. Have H03-A4 weigh the 1oo2 vote against this spurious-trip consequence. |
| 2026-10-26-hazop-review6#9 | H-04 | H04-S76, H04-SG42 | The 30 min PV-4101B-open alarm is credited one order (3/D -> 3/C) on the operator turning the air flow down. Below the 70 % minimum of D-110 (1) the operator cannot turn down, and the vent runs by design or the plant stops. H04-SG42 bundles the ratio limits (control) and this alarm into one safeguard of kind control. | low | open | Split the alarm into its own safeguard (kind alarm). State that the response below 70 % demand is a plant stop or storage (D-110 (1)), or credit the alarm only within the turndown range. |
| 2026-10-26-hazop-review6#10 | H-04 | H04-S03 / VNT-4003 | On instrument-air loss PV-4101B fails open (D-109) while K-4101 unloads and its ESD valves close. The cold box then vents its GOX and the boil-off of its standing liquid at VNT-4003 for the length of the air outage. No scenario names air loss as a cause of a GOX vent (H04-S03 is a vent-loop fault; H04-S01 now excludes air loss). | low | open | Add air loss to H04-S03's cause (or a new scenario under its deviation) and ask the zones owner, with H04-A26, whether VNT-4003 / Z-O2-V1 cover a release lasting the air outage. |
| 2026-10-26-hazop-review6#11 | SESSION.md | section 2 | The node table is stale: H01-N4 shows 5 deviations / 7 scenarios (now 6 / 8), H03-N8 shows 4 / 5 (now 5 / 6) and H04-N9 shows 4 / 6 (now 5 / 7). Session 0 grew to 225 min with the new LOPA / fail-position item, but is still headed "about 3 hours" within "about 21.5 hours". | low | open | Update the three rows, their minutes, the Session 0 heading and the total. |
| 2026-10-26-hazop-review6#12 | DESIGN.md | D-113 (2) | The list of revised scenarios leaves out three that the commit changed: H01-S1 and H01-S5 (residual basis: the I-05 note) and H04-S04 (notes: K-4101 trips in the C&E, XV-4118 fail closed). The bands are unchanged. | low | open | Name them in the next HAZOP decision entry (traceability only). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None open: hazop-review5 had no finding and carried none (hazop-review3#1 .. #7 were closed in
hazop-review4).

## Checked and fine
- `cheme safety hazop check H-01 .. H-04`: each `draft`, 0 errors, 0 warnings, 2 info (proposals
  not accepted: 109 / 79 / 113 / 174; matrix proposed). The info line about hazop-review5 is what
  this record replaces.
- `cheme validate`: 126 files, 0 errors, 95 warnings (P&ID template metadata, drawing and old
  review-record warnings, none in the studies); no `hazop-input-changed`.
- Stamps: the sha256 of every `analysed:` file of the four studies equals its recorded revision
  (34 of 34). `cheme safety hazop rate H-01 .. H-04` (without --write) exits 0; all 562 ratings
  are `current`.
- Recount (scratch script over the YAML, worst band residual where rated, else initial): 223 -> 226
  scenarios; high 86 -> 73, medium 82 -> 95, low 55 -> 58; very-high initial 9 -> 8 (H02-S22, S27,
  H03-S29, H04-S05, S30, S38, S55, S60); 94 actions before and after; every high scenario has an
  action; no scenario without a residual rating (H02-S32 now has one). These match D-113 (6). The
  14 high -> medium and 3 medium -> low changes are exactly those D-113 lists.
- SESSION.md: the state table per study (45 / 37 / 54 / 90; 8 / 12 / 21 / 32 high, 18 / 14 / 23 / 40
  medium, 19 / 11 / 10 / 18 low; 26 / 14 / 23 / 31 actions), the 8 very-high rows of 3.3 and the 73
  rows of 3.4 equal the studies; 3.6 lists the new items.
- Status: every node, deviation, scenario, rating, safeguard and action in the four studies is
  `status: proposed, by: agent`; no `accepted`, no `accepted_by`, no action closed or added (94).
  D-113 and SESSION.md say nothing is a team acceptance.
- The 20 "Proposed answer" texts (H01-A3, A4, A6, A8; H02-A1, A2, A6; H03-A1 .. A4, A12; H04-A01,
  A02, A13, A14, A22, A23, A28, A29) match D-109 .. D-112, control/cause-effect.yaml, loops.yaml
  (the LICA-3102 LAH) and the instrument list (KS-2101 holding its step; PT-4152 and the PT-4102 /
  PT-4152 deviation alarm). Each says "for the team"; the partial ones name what stays open.
- Credit convention applied correctly elsewhere: I-05 with the VIA-1104 alarm counted once
  (H01-S1, S5, S6, S41; H01-S4 credits I-05 as one order, the alarm not again); I-07 with the
  AIA-2102 alarm one order together, and not credited where AIA-2102 is the cause (H02-S10); the
  unconfirmed SIL 2 functions I-11, I-12 and I-14 take one order (H03-S16, S18 stay high);
  I-17 on its own transmitter adds one order where PT-4102 or the selector is the cause (H04-S82,
  S87), and is not counted beyond A in H04-S11; I-13, I-15 and I-16 take one order each, as their
  former kind-other trips did. Where I-15 / I-16 close a valve that is the cause (H04-S49), the
  pump stop still acts.
- H04-S75 and H04-S80: I-14 on its own tapping trips K-4101 apart from UY-4151, FT-4148 and
  PT-4150, and PIC-4101 then holds the LP pressure on PV-4101B. The credit is supported for the
  over-draw (apart from the likelihood question of #4). The PIC-4101 low alarm is not counted
  twice with LICA-3102 (H04-S80).
- New scenarios: H01-S45 (DCAC water pumps dead-headed on air loss, asset 2/D both, the
  standby pump not counted, actions H01-A17 and H01-A4) is credible and sensibly rated. H04-S90
  (the backup's PV-4111 / PV-4112 fail closed on air loss, asset 3/D high, H04-A14, #105) is
  credible, and the reassessment found it, not D-109. H03-S54 is credible; see #8.
- The D-109 .. D-111 changes asked about: spurious trips of the SIL 2 functions are covered by
  H03-S54 (I-14) and by the existing "XV-3117 closes spuriously or the compander trips" scenarios
  (I-11, I-12). The TSA valves failing last are covered by H02-S32, now rated (3/C, 4/B) with
  H02-SG19 one order and the reservoir size left to H02-A6. FV-3111 closing on signal or air loss
  is in H03-S35's cause; its initial C rests on the purge being lost for days, not on the valve
  frequency. PV-4101B failing open on air loss is #10. XV-3105 open on air loss (H04-S21) and
  TV-3124 kept fail open (H03-S12, D-112) are covered.
- Node texts H02-N6 (FSLL-2117), H03-N8 (LSLL-3125) and H04-N1, N3, N4, N9 name the new
  instruments and interlocks consistently with the C&E.

## Not checked
- The screening LOPA of D-111 itself (initiating frequencies, PFDs, modifiers, targets), except
  where a HAZOP credit depends on it (#1, #2, #3). The LOPA / SIL session is the team's.
- The P&ID drawing of FSLL-2117, LSLL-3125 and PSHH-4152 and the control records changed in
  D-109 .. D-112 (outside this scope; they are this study's analysed inputs only).
- The scenarios D-113 did not touch, beyond what earlier reviewers confirmed.
- The team session, the matrix acceptance and the human review (the owner's).
