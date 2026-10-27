I fixed the error CI reported, but CI will probably still fail. That error was hiding four more, and fixing those means editing files outside this folder. Everything is committed in two commits (54d6397, 45e3db5) and nothing is pushed.

## CI (PR #190)
- **Cause:** the two failing library tests (`test_jsonld_identifiers` and `test_the_library_builds_strict_with_the_utilities`) both failed for one reason. `lca/dataset.yaml` had `allocation: none`, and the library build won't export that for a dataset with two products (hydrogen and export steam).
- **Fix:** `lca/lca.yaml` now splits the burdens between hydrogen and steam by exergy: hydrogen takes 90.1 %. The exergy values come from a new script, `scripts/allocation_exergy.py`, and the file now says why this departs from the library's allocation rules. I regenerated the LCA outputs.
- **Checked locally:** I ran the library build directly, not the full pytest suite, because one dependency would not build on the local Python. The allocation error and warning are gone, but four errors appeared that the allocation error had been hiding:
  - `feed:NG` and `feed:NGF` have no mapping, because they are registered as chemical `methane`.
  - The emissions `emission:C2H6` and `emission:C3H8` have no biosphere flow identity.

  These need a change outside this folder, which I was told not to touch. One option is entries in `lci/mappings.yaml` (an `exchanges` override pointing `hydrogen-1/feed:NG` and `feed:NGF` at `natural-gas`, and `biosphere` entries for ethane and propane). The other is the `natural-gas` registry entry D-014 already plans. Expect CI to fail on these next.

## Review findings
There were no critical or high findings. I closed three:
- **#1 (medium, allocation):** with exergy allocation the headline is now 9.11 kg CO2-eq per kg H2. The unallocated 10.10 kg is still shown for comparison in `results.md`. `lca/README.md` now opens with how to read the number, and D-013 is updated.
- **#2 (medium, zero emissions):** a new combustion estimate for the reformer firing replaces the zero CH4 and CO and adds N2O and NOx, and the "emissions incomplete" warning is gone.
  - CH4 and N2O use IPCC 2006 default factors for natural gas.
  - CO and NOx use EMEP/EEA 2019 factors that I wrote from memory and did not re-read. They are marked to be checked against the guidebook; please verify them.
  - C2H6, C3H8 and H2 stay at zero because the reactor solver writes them that way. They are labelled as the complete-combustion assumption, not a measured value.
- **#6 (low):** the deaerator / condensate stripper vent is now listed as an open item in `lca/README.md` and D-013.

PROGRESS.md has a Response entry for each.

**Left open:**
- **#3 and #7:** both need library changes outside this folder (a maturity level below `concept`; a `natural-gas` chemical entry).
- **#4 and #5:** low-priority rewording and adding a cited benchmark comparison, planned for the next stage.
- **#8:** the review itself says no action is needed at concept.

## Re-runs
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** the same gates fail as before (P&IDs, layout, datasheets). `design-review` now also fails because the review record no longer matches the changed files. That clears with a new independent review, not something I can do myself.
- **`cheme maturity`:** level none, with the same over-claim warning (#3).
- **`cheme process streams`:** every block and step balances.
- **`cheme assess lca --coverage`:** partial screening carbon footprint, no errors.

Merge is pending: the branch needs a new independent review and the `lci/mappings.yaml` change above before CI can pass.
