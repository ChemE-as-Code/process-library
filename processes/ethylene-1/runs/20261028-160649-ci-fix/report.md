I fixed four of the five causes of the CI failure and committed (`3f6329b`, `ef48aaf`, not pushed). The fifth cause can't be fixed inside this folder, so the library tooling tests will still fail on one warning. All ten review findings are closed.

**CI (PR 215).** The `library` job failed because the library's dataset builder (`scripts/build_lci.py`) found five errors and two warnings in ethylene-1's LCA dataset. I reproduced them locally with the CI's Python environment. After the fixes the build has 0 errors in both the cut-off and substitution builds.
- **Steam units:** the dataset counts MP, LP and SHP steam as heat in kWh, but they were mapped to the library's `steam` entry, which counts kg. In `lca/mappings.yaml` they now use the kWh entry `steam-heat`, as hda-1 and nitric-acid-1 do.
- **C2H4 and C2H6 in the flue gas:** both are zero after complete combustion and were marked burden-free, which the library rejects for these two. In `lca/lca.yaml` they are now ordinary emissions to air. That makes two more reported gaps (14 → 16), both zero amounts with no climate factor.
- **Allocation warning:** I added a stated reason for using mass allocation (no co-product prices exist at concept stage). That cleared the warning.
- **Still failing:** one warning remains, "study allocation 'mass' differs from the dataset's default None". The `cheme` tool leaves `method: mass` out of `dataset.yaml` because mass is its default, and the library builder reads the missing value as None. ethylene-1 is the first library process to use mass allocation, so it is the first to hit this. The only fixes are outside this folder: either the builder treats a missing method as mass, or `cheme` keeps the method when writing. Changing the allocation method just to pass CI would be wrong.

I recorded these LCA changes in DESIGN.md D-016 and PROGRESS.md.

**Review findings**
- **Closed:** #1, the only high finding (no criticals). I re-checked it: the CO2 figure now reads 0.472 kg/kg ethylene unallocated and 0.433 kg/kg with mass allocation, in `process.yaml` and DESIGN.md D-016/D-018. The earlier commit `63fe760` closed #1 to #10 and PROGRESS.md already had a Response line for each. I added one line confirming the re-check.
- **Left open:** none.

**Checks re-run**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: the concept process gates pass. These fail:
  - `pids-exist`, plus the layout, lifting, MTO, electrical, HVAC and datasheet gates: out of scope for this case study (review #10).
  - `design-review`: the reviewed files have changed since then, so a new independent review is needed.
- `cheme maturity`: calculation maturity none, with the known warning that the claimed concept maturity exceeds it.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: partial screening carbon footprint with 16 gaps. Mass, element and carbon balances close; energy closure is 57.8 %. Publishable.

A merge is pending: the branch needs that new review, and the remaining CI warning needs the library or `cheme` fix first.

STATUS: BLOCKED: one CI warning remains (`method: mass` left out of the dataset); the fix belongs in `scripts/build_lci.py` or `cheme`, outside `processes/ethylene-1/`.