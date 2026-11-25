I drew three sheets, P-101, P-102 and a new P-103, and closed the two review findings that had to come before P-101 (#1 and #5). Everything is committed on `stage/basic-lactic-acid-fermentation` in three commits. `cheme validate` shows 0 errors. I looked at the full render of every sheet; I didn't make detail crops.

**Sheet split.** The sheet template is A3, which is too small for storage, blending and the steriliser together and still readable. So the steriliser moved to a new sheet, P-103 (decision D-028):
- **P-101 Medium preparation:** syrup and corn steep liquor (CSL) receipt, storage tanks T-101A/B and T-102, day tanks T-103 and T-104, their pumps, the ratio blend (FIC-1011/1012/1013) into V-101 (LIC-1014), and new level indicators on the storage tanks. The sheet has no drawing findings.
- **P-103 Continuous steriliser:** feed pumps P-104A/B, regenerator E-101, steam heater E-102, holding tube X-101, a new sterile-side booster P-108A/B, trim cooler E-103 and back-pressure valve PV-1026. The single three-way divert valve is now a pair of on/off valves, XV-1025A/B. A note marks the sterile boundary, with the spec break at the holding-tube outlet. The divert trips are C&E entries I-101 to I-103.
- **P-102 Lime and ring main:** quicklime silo V-102, weigh feeder X-102, slaker R-101 with its cooling coil and scrubber vent, P-107A/B, milk-of-lime tank T-105, and ring-main pumps P-106A/B with supply and return. It has no drawing findings (D-029).

**Review findings closed (recorded in DESIGN.md):**
- **#1 (high), leak direction in E-101:** the booster after the holding tube keeps the sterile side of E-101 about 1 bar above the raw side (about 6.4 against 5.4 barg, ASSUMED pressure drops). A new differential-pressure transmitter, PDT-1028, diverts the medium if that margin falls below 1.0 bar.
- **#5, water into V-101:** there is no hot standby any more, and no water ever goes into V-101. Before each campaign the steriliser is re-sterilised on once-through water (413 K, 30 min) to wastewater; only diverted medium returns to V-101. I estimated the extra steam at about 0.3 MW as a year average (about +20 % on the medium-heating steam Q17) and about 50 m³ of water per campaign. This is in Open inputs: Q17 and the LCI don't carry it yet.

**List changes:**
- The equipment list has P-108A/B, and the steriliser items are now on sheet P-103.
- The line list has about 25 new or changed lines, each with its velocity basis.
- In the instrument list, valve tags (TV, PV, XV) are no longer listed as instruments, and the divert switch TSLL-1023 is replaced by the divert logic US-1025 plus relay UY-1025.
- R-101 is now listed as a Vessel, because this core version has no DEXPI class for a stirred-tank reactor. The seed fermenters will hit the same limit.

**Remaining warnings (10):**
- Five are on P-103:
  - Two signal lines cross the booster discharge line, which encloses the sterile-loop instruments.
  - The E-103 cooling-water connectors sit next to the exchanger rather than on the sheet edge, because every route to an edge crosses the sterile loop or the header.
  - One measuring line runs through a line label.
- Four come from P-202 trip switches listed before this session (TSHH-2012A, FSLL-2014A, LSHH-2032A, PALL-2041A) that have no interlock yet.
- One comes from the earlier S1 review record.

**Left to do:**
- Review findings #2 to #4 and #6 to #10 are still open:
  - #3 (SIP turnaround timing), #2 (seed transfer pressure) and #4 (vacuum protection) need to come before P-202.
  - #9 and #10 (CIP return, SIP steam quality) before P-204.
  - #8 (ring-main return velocity at peak draws) was not changed on P-102.
- `control/loops.yaml` has no entries for the new loops.
- P-108A/B are not placed in the layout.
- The steam coils on the syrup and CSL tanks are only named in a note, not drawn.
- DN 250 sizes are missing from the P-103 drawing data: the drawing library's pipe-size standard has no DN 250. The line list still says DN 250.
- P-201 to P-403, the 3D layout and the HAZOP draft are still to be done.

A merge is pending: the branch needs an independent review and a human merge. Nothing was pushed or signed off.
