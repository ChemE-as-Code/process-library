I fixed the CI failure, closed four of the six review findings, and left two open. The review (`reviews/2026-10-28-pfd-lci-review.md`) had no critical or high findings, so all of this was medium or low. Everything is committed in three commits on `case/acetone-1` (022313c, bed39df, then a PROGRESS.md commit), not pushed. Each finding has a "Response" row in PROGRESS.md.

**CI (PR #210):** the failing test was the strict library build in `tests/test_utilities.py`. It warned "study allocation 'mass' differs from the dataset's default None", because core leaves the default `mass` out of `lca/dataset.yaml` while `lca/lca.yaml` stated it. I removed the explicit `method: mass` (mass is the default for both tools), added a comment saying why, and regenerated the LCA outputs (022313c). That test file now passes locally with the CI's own command (33 passed); I didn't run the rest of the CI suite. The proper fix belongs in the library's `scripts/build_lci.py`, outside this folder, and is still due (DESIGN.md I-10).

**Findings closed**
- **#1 (medium), aqueous effluent:** new decision D-016 says the modelled effluent (64 kg/t phenol) is a lower bound against the source's "water 1–4 t/t" and names the streams that are missing. I added no effluent allowance, because there is no source for one. The effluent entry in `lca/lca.yaml` is flagged, and re-reading that source section is new open item I-11.
- **#3 (low), heat duties:**
  - The spent-air condenser duty Q10 is re-estimated from 330 to 1 260 kW, so total cooling water rises from 61 903 to 62 833 kW (1.543 kWh per kg acetone).
  - D-011 now states that the oxidation heat uses a gas-basis value and is probably about 30 % low. It also says the two side-reaction heats are omitted, not zero.
  - The "independent closure within 2.7 %" is now called a consistency check, since most of it holds by construction.
  - The reaction heats are marked CALCULATED in their source text; the schema only allows `given` or `assumed` as provenance. The BFD/PFD and LCA outputs are rebuilt.
- **#4 (low), acetone yield:** D-009 now says the model's yield (0.627 t/t) is above the stoichiometric 0.617 t/t, why, and that this understates the per-kg burdens by about 1–2 %. Adding a sourced acetone loss stays with open item I-05.
- **#5 (low), acid loading:** D-007 marks the acid loading ASSUMED; the patent range is kept only as a pointer, since its full text wasn't read.

**Findings left open**
- **#2 (low), maturity claim:** marking the feed compositions as given would not help. The feed flows are derived from capacity (`assumed`), so `cheme maturity` stays at "none" either way. Calling pure cumene or dry air a specification would also overstate the data, so the existing note stands, as the review itself allows.
- **#6 (low), LCA cut-offs and dataset metadata:** the exclusions can't take an amount in the `lca` schema, and the free N2/O2 flows can't take a compartment (I tried; it fails to load). I didn't have a verified product classification (CPC) code, so I left it out rather than guess.

**Checks after the changes**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: mass, element and carbon balances close, 13 gaps, all described.
- `cheme maturity`: none, with the known warning from #2.
- `cheme check`: the concept gates pass except the plot plan, which is out of scope. The design-review gate now fails because the review is older than these changes; it needs a new independent review, which I can't write myself.

Merge is pending: the branch needs that new review and a human merge.

STATUS: DONE