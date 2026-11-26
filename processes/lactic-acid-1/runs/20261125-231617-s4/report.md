P-202 is drawn: production fermenter R-201A in full detail as the typical one. It's committed in two commits on `stage/basic-lactic-acid-fermentation`; the pre-commit hook passed and `cheme validate` shows 0 errors. I rendered the sheet and looked at it: one large vessel in the middle, utilities and the temperature loop on the left, the gas side and pH loop on the right, the bottom valve cluster below. The `drawing-clean` gate passes. One check is still owed: the second split-range signal (TIC-2011A to the LP steam valve TV-2011B) was pasted into the XML by hand, and the close crop of it rendered too small to confirm it is drawn cleanly.

**What R-201A shows**
- **Agitator:** A-201A, top entry, 160 kW, double mechanical seal with a sterile barrier (written as a note on the sheet).
- **Temperature:** half-pipe coils on the tempered-water loop of P-201A. TIC-2011A is split range: LP steam injection for heat-up and the lag phase, cooling-water injection for the growth phase, with the overflow going to the CW return. Two independent trips stop the agitator: high-high temperature (TSHH-2012A) and lost loop flow (FSLL-2014A).
- **pH:** two probes (AIC-2021A, and AI-2022A as a deviation check) on a DN 25 milk-of-lime branch with a water flush and a steam block.
- **Level:** the radar LIC-2031A closes the outer medium valve at the batch volume. An independent LSHH-2032A trips the inner valve.
- **Headspace:** PIC-2041A works the vent back-pressure valve. N2 make-up is a self-acting regulator, PCV-2042A, instead of the split range in the lists. It keeps working if the control system fails.
- **Filters and relief:**
  - The vent filter F-201A is isolated and bypassed during CIP, so the cartridge is not wetted.
  - The inlet filter F-202A also takes the vacuum relief PSV-2046A, which admits air through it.
  - The rupture disc PSE-2045A is sized on the SIP steam case.
- **Sterile boundary:**
  - Steam blocks on the medium, inoculum, lime, CIP supply, CIP return and harvest lines.
  - Head SIP steam enters through the CIP spray line; bottom SIP enters through the bottom valve cluster, with TI-2015A at the coldest point.
  - Aseptic sampling valve, steam-flushed.
  - A note marks the boundary, and another says the fermentation is not aerated.
- **Trips (I-201 to I-204):** the four R-201A trips are in `control/cause-effect.yaml`, and R-201A's four control loops are in `control/loops.yaml`.

**Decision D-031** records all of this, with the arithmetic and every ASSUMED value. It answers these findings:
- **S1#3 (SIP in the turnaround):** the timed turnaround is 12.5 h, not 12 h. The harvest period goes from 9.88 to 9.91 h, about 0.3 % fewer batches a year. I kept 16 fermenters and left the flowsheet unchanged.
- **S1#4 (vacuum):** the governing case is steam collapse after SIP, about 24 000 m3/h of gas demand. No filter path can pass that, so it is prevented by a trip and permissives rather than relieved. If the HAZOP does not credit that trip, the fermenters need a full-vacuum rating. This is an open HAZOP item.
- **S1#7 (heating):** the steam injection above.
- **S2#9 (lime and the sterile boundary):** the boundary is the steam block on the dosing branch; the non-sterile lime crossing it when dosing is an accepted risk.
- **For R-201A only:** S2#1/S3#5 (steam block on the CIP inlet) and S3#4 (high-level protection).

**List and drawing changes you should know about**
- R-201A to P are now listed as DEXPI `Vessel`, the same class as the seed fermenters. The sterile filters are `GasFilter`.
- The lime branch is renumbered 25-ML-2024A; the old number reused the sequence of a steam line.
- I added 13 lines and created `piping/special-items.yaml`.
- The authoring tools have no vacuum-relief valve, so PSV-2046A is drawn as a check valve. The rupture-disc symbol cannot carry a tag, so PSE-2045A is tagged by a note.
- I accepted 13 findings explicitly in `checks/checks.yaml`, each with a reason and no wildcards:
  - one measuring-line crossing at TIC-2011A;
  - eight short steam/flush stubs drawn at their valves instead of the sheet edge;
  - the 100-CS-2016A line labels, which are tight beside the CIP steam block;
  - the PSE-2045A note.

**What's left**
- The carry-over items stay for S9, as asked: the seed-train findings (S3#1 to #10), P-102 and P-103 fixes, S2#2/S2#3, and the control sequences that hold the CIP, fill and cooling permissives.
- I couldn't delete `pid/P-201.refused.xml` or the new `pid/P-202.refused.xml`: removing files needs your approval. Both are untracked.
- The 3D layout, lifting and MTO gates are still failing for the reasons stated before.
- The design-review gate fails until the independent review runs.

**Merge is pending.** Nothing was pushed, merged or signed off; the branch waits for the independent review.
