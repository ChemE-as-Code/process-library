I closed eight of the nine findings, with one change to the design itself: the azine reactor and decanter headspaces are now inerted with nitrogen. The review had no critical or high findings, so all of this work was on medium and low ones. Two commits are on `case/hydrazine-1` (`dd9831e`, `86d154d`) and nothing is pushed.

**CI:** there was no failed run to read. Every run for PR 235 is still queued (checked again at the end). I ran the CI steps locally instead and none shows an error for hydrazine-1:
- `cheme fmt --check`, `cheme validate` (0 errors, 0 warnings) and `cheme assess lca --check` pass.
- The strict LCI build gives only gaps and warnings that come from core not being installed here, the same for every process.
- The library tests: 386 passed, 1 failed. That test also fails only because core is missing locally.
- The catalog build gives only "no preview rendered" warnings, which don't fail CI.

So I changed nothing for CI; once those runs finish, the real logs should be checked.

**Findings closed**
- **#2 (medium), headspace inerting:** new decision D-015 adds a nitrogen sweep of 634 kg/h (about 0.32 kg per kg hydrate) to keep oxygen at or below 8 mol% in the vent. That target is assumed: it sits about 3 points below an oxygen limit for MEK that I took from general knowledge, not from a source. Sourcing the limit is added to I-04. The balance script, flowsheet, BFD/PFD and LCI are updated; the vent grows to about 756 kg/h, and the ammonia and MEK make-up rise by 3.9 and 8.3 kg/h.
- **#1 (medium), hydrolysis column steam:** it is now called a lower bound in D-010, on Q05, in the steam entry of `lca/lca.yaml` and in `process.yaml`. A high variant (reflux 2.5 plus an assumed hydrolysis heat of 25–75 kJ/mol) gives 4.3–4.9 MW instead of 2.6 MW, or 18 % more MP steam. It is in `scripts/balance.py` and the written records, but not as an LCA scenario: that needs a second solved flowsheet case, which waits for the column simulation (I-02).
- **#3:** the peroxide demand per kg N2H4 at yields 0.81 / 0.85 / 0.95 is now recorded: 1.317 / 1.255 / 1.123 kg. I-01 stays open because Hayashi et al. 1976 has still not been read.
- **#4:** the peroxide entry now says its quantity is the mass of 70 wt% solution, so a background stated per kg of pure H2O2 must be applied to 0.70 of it.
- **#5:** the reactor cooling duty (Q08) is now called an order-of-magnitude estimate, not a lower bound.
- **#7:** each NIST formation enthalpy now has its own species page link by CAS number. The values were still not re-fetched, and the source register says so.
- **#8:** new open item I-11 covers materials for peroxide and hydrazine service, and the R-101 note now points to it.
- **#9:** `process.yaml` now explains that the 0 total in `lca/results.csv` is not a zero footprint. The report to cheme-as-code has not been filed yet.

Each closed finding has a Response entry in PROGRESS.md.

**Left open**
- **#6:** the warning that the claimed maturity exceeds the evidence can only be accepted by a person, or removed by giving the capacity a sourced basis.

**Final checks**
- `cheme check`: all concept and process gates pass. `design-review` now fails because the review is out of date after this revision, so a new independent review is needed. The P&ID, layout and datasheet gates fail as before; they are outside the concept stage.
- `cheme maturity`: still calculation maturity none, with the #6 warning.
- `cheme process streams`: all 4 blocks and 11 steps balance.
- `cheme assess lca --coverage`: mass, element and carbon balances close; the result is still a partial screening with 15 background gaps, now including nitrogen, and no impact claimed.

A merge is pending: the branch needs that new review, a merge from main (as the review noted), and a human to merge it.

STATUS: DONE