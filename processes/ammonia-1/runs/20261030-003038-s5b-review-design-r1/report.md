My verdict on S5b (PR #257) is **fix**: the two gates S5b was meant to close still fail, and the Class 4 estimate was not started. I committed the review record as `reviews/2026-10-30-design-s5b.md` (7a09cd1), pushed it to `stage/basic-layout` and posted the verdict as a PR comment. Nothing is merged; the merge is pending.

**Checks I re-ran myself:**
- **`cheme validate`:** 0 errors, 184 warnings.
- **`cheme check --stage basic`:** these pass: process-basic, process-links, pids-valid, drawing-clean, pids-exist, layout-3d, mto and tea.
- **Gates that still fail:**
  - **`lifting-study`:** 11 crane lanes are blocked, down from 26, and none was accepted.
  - **`maturity-balanced`:** the feed flows and compositions are not recorded as given with a source (`sourced.boundary`). The reactor model basis now passes.
  - **design-review and layout-review:** they fail because S5b changed their scope; my record replaces the design review.
- **`cheme maturity`:** reaches no level.
- **Estimate:** `estimate/rates.yaml` is still the template's example, and no estimate exists.
- **Layout:** `cheme layout build --check` says the model is current.

**Source spot-checks:**
- **Prereformer patent (EP 1586535 A2):** confirmed.
- **EU ammonia BREF, §2.2.3.6, p. 42 (carbon oxides below 10 ppmv after methanation):** confirmed.
- **Secondary-reformer paper (Al-Dhfeery & Jassem 2012):** I couldn't open it; the publisher redirects to a login.

**Engineering judgement:** the work is honest. It cleared 15 lanes by design, tried the E-504 move and the sourced feed composition and reverted both for stated reasons, and accepted nothing. Seven of the 11 remaining lanes are blocked by the item's own piping or (for H-101) its own tubes; the usual answer is to set the item before its piping, which is the owner's decision. The `sourced.boundary` blocker is also real: the gas, air and water feed rates come out of this flowsheet's design, so no publication gives them. Closing it needs either the owner to specify those rates or the project to adopt a published reference plant's feed basis.

**Findings:**
- **High (carried), 2026-10-29-design#1:** the lifting lanes and the sourced feed basis need the owner's decision; the Class 4 estimate is agent work that hasn't been done.
- **Medium, s5b#1:** two furnace conversions (hydrogen and ammonia burnout) are marked `given` on weak sources: one is an inference, the other an analogy from a coal-fired boiler. They are what makes the reactor model basis pass.
- **Medium, s5b#2:** a small change in feed composition moved the steam-system boiler duty from 130 to 197.5 MW with no explanation. The TEA's steam export credit and the later sourced-feed fix both depend on that script.
- **Low, s5b#3:** D-033 relies on `build/tools/pad_search.py`, which is in the ignored `build/` folder, so the "no pad clears these lanes" check can't be reproduced.
- **Low, s5b#4:** the PROGRESS.md row lists the E-504 move, which was reverted.
- **Low, s5b#5:** the PR description is still the original S5 text.

One earlier finding (simulation#1, the reactor model basis) is now closed. The others are carried forward unchanged.

FINDINGS: critical=0 high=0 medium=2 low=3
VERDICT: fix
STATUS: DONE