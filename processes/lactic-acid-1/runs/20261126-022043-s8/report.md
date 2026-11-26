I built the 3D layout for stage S8 and committed it in two commits, with `layout/plant-model.yaml` included. Gate layout-3d still fails: about 480 clash and headroom findings remain, and the independent layout review is not recorded. `cheme validate` shows 0 errors and 1266 warnings, and the working tree is clean.

**What was done (decision D-043 in DESIGN.md)**
- **Fermenter rows:** the plot plan of D-026 stays: two rows of eight outdoors with rack PR-1 between them. Over each row a steel frame (ST-201, ST-202) carries a grating deck at 24.5 m, with a stair tower at each end. The agitator drives now stand on drive bridges on that deck rather than on the vessel head, and the vent and gas filters stand at the deck edge on the rack side. The fermenters have no shell platforms: the top is worked from the deck, the bottom valves, probes and sampling from grade. The equipment-list note for A-201A says the same now.
- **Seed building B-201:** the three seed trains now stand 10 m apart (they were 5–7 m apart and their small lines clashed), and the building has a 25 t overhead crane.
- **Every item placed:** the 13 missing items are placed (seed filters F-241 to F-246 B/C and A-301), 259 in total.
- **Racks:** each service has its own tier on PR-1, PR-4 and PR-6.
- **Routing:** every segment of DN 25 and above is routed. Ten headers started at off-page connectors the router could not pair with the line upstream, so I fixed their first segment by hand from the rack junction. The DN15 lines and the seed jackets' cooling water are skipped with a reason; the gate leaves both to detail engineering.
- **Zones:** a zone-2 screening envelope over the ethanol process area, release zones around the ethanol tank vent and pump seals, crane pads, laydowns and a truck unloading bay. All are ASSUMED; nobody has done an area classification yet.
- **Lifting:** the lifting study and the material take-off are written. In the lifting gate I accepted the items that are built in place and never lifted whole (the fermenters, T-101A/B, T-201, V-102, S-302), with that reason.
- **Drawings:** I rendered the plot plan, a section across both fermenter rows (x = 159 m) and a section through seed train A and the ethanol columns (y = 232 m), and looked at them.
- **P-404:** the layout build stops when a sheet listed in `plant.yaml` has no file. So I created P-404 as the empty template; its status changed from planned to drafted, and it is still to be drawn in S9.
- **Core limits:** I recorded three new ones as L-9 to L-11 in DESIGN.md (off-page pairing, a planned sheet stopping the build, platform levels inside buildings).

**Gates now**
- layout-plot-plan and mto pass.
- lifting-study fails only on the three centrifuges S-301A to C, whose removal lanes are blocked by their own lines.
- layout-3d fails for these reasons, all listed in DESIGN.md:
  - **Pipe clashes (at least 200; the listing stops there):** mostly the branches from PR-1 up to the fermenter tops. Each fermenter's branches leave the three tiers at the same point and rise in parallel through the tiers above. Fixing this needs a separate riser lane per service per fermenter, about 100 hand-set routes, which is the next layout task.
  - **Headroom (158):** mostly in the seed building. A building level cannot be limited to part of the floor, so each seed platform covers the whole 72 × 64 m floor in the model and almost every pipe there counts as too low.
  - **Pipe through equipment (63) and pipe through steel (15).**
  - **No layout review recorded:** this needs the independent reviewer.
- Not touched, as this stage was layout only: the drawing-clean crossing on P-403, P-404's drawing, and the P&ID and list findings. Those stay for S9.

No merge is pending yet: the branch stays unpushed and unmerged until the independent layout review is done.
