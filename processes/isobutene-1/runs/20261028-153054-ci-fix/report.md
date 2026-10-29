I fixed the CI failure and closed five of the seven review findings. The newest review (`reviews/2026-10-28-pfd-lci-review.md`) had no critical or high findings; all seven are low. Everything is committed in five commits on `case/isobutene-1` and nothing is pushed.

**CI (PR 204, `library` job).** The library build test failed on one warning for this folder: the LCA study (`lca/lca.yaml`) said "mass allocation" explicitly, but the generated dataset (`lca/dataset.yaml`) records no allocation method when it is the default, which is also mass. I removed the explicit setting from `lca/lca.yaml`; the allocation and the results are unchanged (088ef37). I ran that test locally and the isobutene-1 warning is gone. The test still fails locally on warnings from other processes and the benchmarks, which come from an optional package missing on my machine, so CI on the next push is the real confirmation.

**Findings closed**
- **#1** – D-005 now cites the right patent table for the C8 figure (Example 1, Table 6, not Example 2); the design value 0.001 stays ASSUMED (32fd8c9).
- **#2** – The C-201 reboiler (Q7) now runs on LP instead of MP steam, since LP steam still leaves a 27 K approach against a 10 K minimum. The flowsheet, D-009, design basis, equipment list, manifest notes and LCA were updated, and the BFD/PFD rebuilt. Per kg isobutene this gives MP steam 1.16 MJ and LP steam 1.29 MJ (17d08e4).
- **#3** – The heater's fan and hot-oil pump power is no longer a cut-off: it is a new 30 kW ASSUMED energy stream (Q18) into H-101. Electricity in the inventory goes from 15.8 to 45.8 kW (17d08e4).
- **#4** – D-001 now says the run's task chose the route, not the issue. A new open item, I-09, records that the issue's comparison of C4 separation with on-purpose production has not been done (32fd8c9).
- **#5** – The 99.97 wt% purity in `process.yaml` now notes that the feed is pure MTBE and linear butenes and C5 are not modelled (D-003) (32fd8c9).

PROGRESS.md has a Response entry for the CI fix and for each finding (f58cbfb). A last commit only refreshes the file hashes recorded in the LCA dataset and manifest (fd46a49).

**Findings left open**
- **#6** – The concept gate `layout-plot-plan` still fails, as do the basic and detail gates. A concept sign-off needs either a plot plan or a human accepting the gate as out of scope for this case.
- **#7** – `cheme maturity` still reaches no maturity level, because the capacity and the MTBE assay have no source (I-01). Keeping the `concept` claim with its note is what the review proposed.

**Check results after the changes**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: the mass, element and carbon-origin balances are closed and the result is publishable; all 8 backgrounds are still gaps.
- `cheme maturity`: unchanged; it reaches no level and still warns that the `concept` claim exceeds it (#7).
- `cheme check`: `layout-plot-plan` fails (#6), and `design-review` now fails as well: the review covered commit 04ddb0e and these changes make it out of date. An independent re-review is needed; I did not write one myself.

Merge pending: it needs that re-review and a human merge.

STATUS: DONE