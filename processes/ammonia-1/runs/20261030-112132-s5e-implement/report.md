S5e is done. The four motor lanes the owner refused to accept are now clear by design, and the gates `lifting-study` and `layout-3d` both pass. Every basic gate passes except the two review gates, design-review and layout-review. `cheme validate` reports 0 errors.

**What changed**
- **Skills:** I updated `electrical-cabling` and `structures-access` to core v1.1.0. Neither had local changes. Rebuilding the 3D model on 1.1.0 by itself left its content unchanged.
- **Cable entry points:** K-101, K-102, K-103, K-501 and K-701 now have one each. Each sits on the side the tray arrives from, away from the crane pad. No datasheet gives a terminal-box side, so the sides and heights are marked ASSUMED; the vendors' terminal-box drawings would replace them.
  - Some tray ends sit below the machine top (4.5 m for K-101 and K-701, 5.5 m for K-501), so the cable enters the terminal box from below. At the default height the tray still reached into the lane of K-501 and K-701.
  - K-101's entry is 3 m out from the machine, because its lane from CP-107 runs at an angle.
- **Lifting results:**
  - K-101 lifts from CP-107 at 11.2 m and K-701 from CP-701 at 20.6 m. K-102 and K-103 lift from their own pads (CP-106 and CP-107, 7.5 m each). All four lanes are clear.
  - I accepted no lane and did not add, remove or reword any acceptance.
- **Extra blockers on the lanes the owner already accepted:** all three are cleared by design, and each lane is now blocked only by items its accepted reason names.
  - **K-501:** its motor tray is gone, cleared by the cable entry.
  - **E-505:** E-503's cooling-water nozzles now point north, so those lines stay low and out of the lane. Pad CP-505 moved 0.5 m north to avoid a new crossing.
  - **E-504:** the instrument tray sits on the PR-7 rack, which the old lane crossed. I added a pad, CP-507, on open ground west of E-504, and moved E-504 1 m north so its lane clears the rack columns. Its crane radius drops from 25.2 m to 11.3 m. Nothing runs over CP-507. E-502 and E-505 also lift from it now.
- **Stale wording:** the owner's accept reasons for K-501, E-505 and E-504 still mention the cleared blockers in their S5c notes. I left their wording as written and recorded this in a comment in `checks/checks.yaml` and in D-046.
- **Downstream:**
  - The cable schedule, MTO, estimate and LCA are rebuilt. Motor cables are 0.6–1.2 m longer each, and DN 350 pipe is 8.2 m shorter.
  - The bulk estimate falls 0.07 %; it still uses example rates.
  - The LCA results and the TEA are unchanged.
- **Records:** D-046 is in `DESIGN.md` and both changes are in `PROGRESS.md`. Two commits; the tree is clean.

**Still open**
- Two points for the lifting plan: how a crane reaches CP-507 (assumed under PR-7, lowest tier 6 m, or from road R-6), and whether a crane needing about 205 t capacity can set up on its 10 m × 9 m footprint.
- The detail gates `electrical` and `datasheets` still fail. The 8 tray-fill findings behind `electrical` were already there; they were hidden behind the model-version failure before the rebuild.
- `cheme maturity` is unchanged: balanced, with predictive failing on items from earlier sections.

The PR description is in `build/pr-body.md` and the short summary in `build/pr-comment.md`. The design and layout reviews, sign-off and merge are next. The merge is pending.

STATUS: DONE