S5b is blocked: neither target gate passes. `lifting-study` and `maturity-balanced` still fail. Both are closer, and nothing was accepted, relaxed or moved. The Class 4 estimate was not started.

The previous session had made no changes (it hit an API error), so this work started from 8485e00. Everything is committed on `stage/basic-layout` in three commits (cb1c46f, e324a09, 0db12b9), and the PR description is in `build/pr-body.md`. Review (S5r) and merge are pending; nothing is merged.

**1. maturity-balanced (still fails)**
- **Reactor model basis now passes.** The conversions of R100, R102A, R401 and H101 keep their values (1.0) but are now marked `given`, each with a published source and locator in `process/reactions.yaml` (decision D-034):
  - prereformer: patent EP 1586535 A2, para. [0003];
  - secondary reformer burner: Al-Dhfeery & Jassem 2012, p. 2, a model compared with plant data;
  - methanator: the EU BREF on ammonia (2007), §2.2.3.6, below 10 ppmv left;
  - furnace hydrocarbons: US EPA AP-42 §1.4, Table 1.4-2, footnote b;
  - furnace NH3: Lin et al. 2024, below 1 ppm at the furnace outlet.

  The H2 burnout in the furnace rests on an inference from the secondary-reformer source, not a direct measurement. D-034 says so.
- **What still fails is `sourced.boundary`.** The flows of the natural gas, the two air feeds and the two water make-ups are results of the design (radiant balance, H2/N2 = 3, excess air, water balances). No published source gives them for this flowsheet. Marking them `given` would need an owner's specification of those rates, as asu-1 had for its air, so I did not do it.
- **A sourced feed composition was tried and reverted.** I simulated the published EBTF natural-gas composition (it adds butanes and pentanes) with standard-atmosphere air, and DWSIM converged. The steam-system package script then gave a boiler duty of 197.5 MW (130 MW before) and a chiller duty 21 % higher. I could not explain or trace those jumps within the budget, so I reverted the change. The flowsheet is as it was, and the sources for a follow-up are recorded in D-034.
- **Two core limits** blocked declaring H101 as a Gibbs or equilibrium reactor instead: propagate found no Gibbs-energy step, and the equilibrium solve did not converge.

**2. lifting-study (still fails, 26 → 11 blocked lanes)**
- **Cleared by design (decision D-033):**
  - 13 new crane pads beside the items on their clear side;
  - 2 new laydowns, with two existing ones moved off the pads;
  - the V-502 relief line PG-1120 rerouted west of V-501.
- **E-504 stays put.** Moving it 2 m north cleared it of the PR-7 rack but created a headroom clash, so I reverted that.
- **The 11 left:** H-101, E-104, E-402, E-301, E-303, K-501, E-501, E-502, E-505, E-504 and V-701. Each is blocked by its own or the adjacent exchanger's piping, the PR-7 rack (E-504), or for H-101 its own tubes. Only the erection sequence clears them.
- **Owner's decision:** `build/lifting-acceptance-proposal.md` lists each lane with its blockers and the lifting plan's reason. Nothing is accepted.
- **No crane chart yet:** R-501 (658 t) and C-301 (514 t) need a crane of about the 1,000 t class.

**3. Class 4 estimate (not done)**
`estimate/rates.yaml` is still the template's example. No sourced rates or cost index, the equipment and estimate commands were not run, and the TEA is unchanged. The budget went to items 1 and 2.

**4. Other open review findings**
- Review finding simulation#1 is now partly closed (the model-basis part) for the reviewer.
- The finding on the unsourced natural-gas composition (pfd-lci-review#3) stays open, because the composition change was reverted.
- The rest are unchanged.

**Checks at 0db12b9**
- `cheme validate`: 0 errors, 184 warnings.
- `cheme check` (basic stage):
  - passes: process-basic, process-links, pids-valid, drawing-clean, pids-exist, layout-3d, mto, tea;
  - fails: lifting-study and maturity-balanced (above);
  - fails: design-review and layout-review, because this job changed their scope; the S5r reviews come next.
- `cheme maturity`: none. `sourced.boundary` is the only failing requirement of the sourced and balanced levels.

STATUS: BLOCKED: lifting-study fails on 11 lanes that only an owner's lifting-plan acceptance can clear (proposal in build/lifting-acceptance-proposal.md); maturity-balanced fails on sourced.boundary because no published source gives the boundary flows (S1, S12, S61, S26, S70), and an owner specification or a sourced feed-basis job is needed; the Class 4 estimate was not done.