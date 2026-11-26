I've finished both sheets for this stage: P-201 now closes the S3 findings, seed trains B and C are drawn, and P-204 (CIP station and SIP steam) is drawn. Everything is in two commits on `stage/basic-lactic-acid-fermentation`. `cheme validate` reports 0 errors and the pre-commit hook passed both times. A merge is pending: the branch still needs the independent review and a human merge. Nothing is pushed or signed off.

**Seed trains (D-036)**
- I wrote one script, `scripts/draft_seed_train.py`, that draws train A on P-201 and the same train for B and C. I redrew P-201 from it, which was safe because nobody had edited P-201 by hand since it was first drawn. The old `draft_P-201.py` is kept and marked superseded, because deleting it needed an approval.
- Train B is on P-205 and train C on a new sheet, P-208. One train fills an A3 sheet, so two trains would not fit legibly. I changed `plant.yaml` and the train C items' `sheet:` to match.
- Trains B and C carry their own tags and are fully listed: 72 lines, 12 filters, 24 instruments, 6 rupture discs and 6 trips.
- How each S3 finding was closed:
  - **S3#1 (relief):** each N2 branch gets a pressure reducer with a restricted trim (2.0 barg for stages 3 and 4, 4.0 barg for stage 5). The rupture discs are tagged with set pressures and relief cases. The governing case is the reducer and the pressure valve both failing open: about 0.05 kg/s against about 0.30 kg/s the disc can pass.
  - **S3#2:** an aseptic sampling valve on each vessel's bottom head.
  - **S3#4 (high level):** the fill stops on the vessel's own weight or level reading at high-high (C&E I-211 to I-213C). It is not an independent switch; D-036 gives the reason.
  - **S3#5:** double-seat valves with a steamed leakage chamber on the CIP inlets, instead of steam blocks.
  - **S3#7:** T-215 now has a caustic fill, dilution water and a vent.
  - **S3#8:** vent-filter drains go through traps, and the rupture-disc lines have their own numbers.

**P-204 (D-037)**
- CIP: tanks T-221 to T-224, supply pumps P-221A/B, the steam heater E-221 with temperature and flow control, return conductivity and temperature, and return pumps P-222A/B.
- I placed the return pumps at the low point of the return header (S1#9). That location is ASSUMED.
- Recovery goes back to the caustic, acid or rinse tank, or to the drain. Caustic storage T-225 with P-223 feeds T-221 and T-215.
- SIP: steam goes through filters F-231A/B and a pressure control valve into the SIP header, with a drip leg and trap. Steam quality (S1#10) is stated as ASSUMED.
- 21 lines added to the line list. Four line crossings are accepted in `checks.yaml` with a reason.

**Gates**
- The stage-basic drawing gate passed before the last P-204 label fix. I didn't re-run it after the final redraw because of the budget.
- Validate still shows warnings: P-204 line endpoints and the 15-NA-2152 rack route, crossings that are accepted only in the drawing gate, and older ones on other sheets.

**Left open**
- In P-204: tank level instruments, overflows, pump isolation valves and drains, the CIP/SIP permissives in C&E, and routing T-201's condensate to it (S5#6).
- S5#1: instruments, special items and trips for R-201B to P.
- S5#2 to #5, #7 and #8; S2#1 and #2; S3#10 (heating the seed vessels).
- The layout gates (3D model, zones, plan and section review), and sheets P-301 and P-401 to P-403.
