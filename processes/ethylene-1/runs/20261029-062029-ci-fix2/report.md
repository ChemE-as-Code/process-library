The library test that failed now passes, and the fix is committed locally as `fdc48ce` on `case/ethylene-1`, on top of the merge of `origin/main` (`3d1d16d`). Nothing is pushed.

**Cause:** `lca/lca.yaml` stated `allocation.method: mass`. When cheme writes `lca/dataset.yaml`, it leaves out a method that equals the default (mass), so the dataset's method was empty. The strict library build compares the two and warned that they differ, even though both meant mass.

**Fix (only inside `processes/ethylene-1/`):**
- **`lca/lca.yaml`:** I removed the explicit `method: mass` and added a comment saying why. Mass is still the method: the schema defaults to it, and so does the library build script (`scripts/build_lci.py`). Acetone-1 already handles it the same way.
- **Regenerated files:** `cheme assess lca --write` rewrote `lca/dataset.yaml` and `lca/manifest.json`. Only the recorded hash of `lca.yaml` changed; the LCA results are the same, so there are no physics changes.
- **`PROGRESS.md`:** new entry for this change.

**Checks:**
- `pytest -q tests/test_utilities.py` with the given command, run from the repository root: 33 passed. I didn't run it before the fix, so the failure itself wasn't reproduced here.
- `cheme validate`: 0 errors, 0 warnings.
- `cheme assess lca --check`: all LCA output files current.
- The pre-commit hook passed.

The branch still has to be pushed and the PR reviewed and merged; that merge is pending.

STATUS: DONE