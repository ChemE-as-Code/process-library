S3c (loop) is finished and committed on `stage/basic-pids-loop`, and all five of the section's gates pass. A merge is pending: the orchestrator pushes the branch, then an independent reviewer reviews and merges it.

**Sheets drawn (decision record: DESIGN.md D-029)**

| sheet | what it shows |
|---|---|
| P-109 | Synthesis loop and converter: circulator K-502, exchanger E-501, converter R-501, waste heat boiler E-502 |
| P-110 | Loop chilling and separation: coolers E-503, E-505, E-504, separator V-501, let-down vessel V-502 |
| P-111 | Product flash drum V-701, refrigeration package K-701 with condenser E-701, product line to storage at the battery limit |
| P-112 | Purge gas recovery package X-601 |
| P-113 | Steam system U-801 and feed water pump P-801 |
| P-114 | Cooling water supply/return headers and the flare header |

- **Lists:** the 15 loop items already in the equipment list now have their sheet; no equipment was added. 50 new lines, 45 new instruments and 4 new safety valves (relief cases open until S8) are listed. One trip is proposed in the cause-and-effect file: I-107, separator V-501 low-low level closes XV-1904, to stop gas blowing through from 14,700 kPa(a) into V-502.
- **Flowsheet links:** 27 streams are now linked to their lines, and the BFD and PFD were rebuilt.
- **Earlier sheets:** text-only changes on P-101..P-108. Their off-page notes now name the new sheet on the other end. Six cooling-water connectors moved 3 mm inwards so the longer notes stay inside the frame. I rendered and looked at every new sheet, and the layout model was rebuilt.

**Check results**
- `cheme validate`: 0 errors, 237 warnings. The warnings are layout findings (S5's scope), missing tag labels (a kind that was already there) and one 2.2 kW energy balance on K601 that dates from S2.
- Section gates: pids-exist, pids-valid, drawing-clean, process-basic and process-links all pass. The drawing counts are 0 on all 14 P&IDs.
- Other gates: design-review, layout-3d, lifting-study, mto, maturity-balanced, layout-review and the detail gates fail, as they did before this section. The new P-114 headers add unrouted lines to layout-3d, which is S5's work.
- `cheme maturity`: calculation maturity none, unchanged from S2. It fails on unsourced feeds and model basis, the property-range limit (core#315) and the plant energy closure (core#60).

**ASSUMED values added (marked in D-029 and the line list)**
- LP steam at 450 kPa(a), since D-015 gives no pressure.
- Line-sizing velocities, and DN 25 as the smallest line.
- 380 K discharge temperature for K-701, used for its discharge line size.
- Circulation ratio 5 for E-502.
- Sizes of the relief, flare, bypass and anti-surge lines, since no relief loads exist yet.
- What sits inside the K-701 and X-601 packages, following the flowsheet.

Liquid ammonia and refrigerant properties come from thermo's correlations; no third-party content was copied.

**Open items for review, S4 and S8**
- Block and bypass valves, vents, drains and sample points.
- Spare feed water pump.
- Trips on the converter, K-502 and K-701.
- Relief set pressures and cases.
- Line size after the separator let-down valve LV-1903, where the flow turns two-phase.
- Whether the ammonia reliefs need their own flare.

One process slip: I edited `scripts/draft_P-109.py` once with a shell heredoc instead of the Edit tool. The file is provenance only and I checked the final version.

The PR description is in `build/pr-body.md`.

STATUS: DONE