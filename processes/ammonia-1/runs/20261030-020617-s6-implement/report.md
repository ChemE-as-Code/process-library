I've drafted a HAZOP study of all fourteen P&IDs and committed it as one commit (`6a8441b`) on `stage/basic-hazop`. Every entry is still a proposal, and all bands are provisional because the project's risk matrix is example data.

**What the study holds** (`safety/hazop/H-01/study.yaml`)
- It analyses P-101 to P-114 together with the trip list (`control/cause-effect.yaml`), the control loops (`control/loops.yaml`) and the relief-device list (`piping/special-items.yaml`), each recorded at its current revision.
- 16 nodes, 62 deviations, 66 scenarios, 59 safeguards and 40 actions. Safeguards are only things that are actually drawn or listed: trips, alarms, control loops, relief valves and check valves.
- Every entry is `status: proposed`, `by: agent`. No team has met, so the `team:` field is empty.
- Every scenario is rated before safeguards; 8 also have a rating with safeguards. Those 8 credit only trips that have their own sensor and their own valve, separate from the control loop whose failure causes the scenario.
- Bands were set by `cheme safety hazop rate --write`, never by hand. Worst band per scenario: 32 high, 26 medium, 8 low. Every high scenario has an action.

**Check results**
- `cheme safety hazop check`: 0 errors, 0 warnings, state draft. The two remaining notes say the proposals are not yet accepted by a team and the risk matrix is example data; only a team can clear them.
- `cheme validate`: 0 errors, 239 warnings, the same as on `main`.
- `cheme check` and `cheme maturity`: unchanged from `main`. The 6 failing basic gates are earlier sections' (S2, S5) and calculation maturity is still none.

**Actions:** all 40 stay open as proposals, each with an owner, the stage it is due by, and why it is carried. None is closed, because closing an action is the team's decision.

**Main findings for the team**
- **Gas blow-by into low-pressure equipment with no independent trip:** V-201 into the condensate stripper in U-801, V-502 into V-701, and V-401.
- **Reverse flow:**
  - Loop gas can flow back through a stopped K-501 into the front end, which runs at about 2,900 kPa(a), behind one check valve.
  - Process gas can flow back into the air line when K-101 trips; XV-1204 closes only on the R-102 high-temperature trip (I-103).
- **Front end blocked in** after the methanator trip (I-106) or a K-501 trip, with no front-end vent to flare drawn.
- **E-504 tube rupture:** loop gas would enter the refrigerant side, which has no relief device.
- **Steam drum low level:** one boiler feed pump and no low-low trip protect all the waste heat boilers.
- **Furnace and converter:** H-101 has no burner management and no independent tube-temperature protection, and R-501 has no high-temperature trip.
- **Flare header:** ammonia and hydrogen reliefs share one header.

The questions the trip list left to the HAZOP are answered as proposed actions, not by editing it. Eleven actions are relief cases handed to S8.

**Not changed:** no P&ID, list, loop, sequence or trip-list entry was edited. `DESIGN.md` gains decision D-031 and `PROGRESS.md` a row. I used no outside sources and no new ASSUMED values. The one inference is marked in the study: the condensate stripper is taken to run near atmospheric pressure because its overhead goes to the CO2 vent.

**Open items**
- `safety/risk-matrix.yaml` must be replaced by the project's own matrix, then the study re-rated. I did not invent criteria.
- A HAZOP team has to hold the sessions and accept, change or reject each proposal.
- The vendor packages (compressors, dryer, purge gas recovery, steam system, burner management) need their own HAZOPs.
- I did not add a `kind: hazop` gate: the plan doesn't name one, and it couldn't pass before a team accepts the study.
- No review record yet; that is for the independent reviewer.

The PR description is in `build/pr-body.md`. Merge is pending: the orchestrator pushes and an independent reviewer reviews and merges.

STATUS: DONE