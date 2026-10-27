The error CI reported is fixed, but **CI will still fail**: fixing it uncovered further errors that can only be fixed outside this folder. The review had no critical or high findings; I closed 8 of the 10 open medium/low ones.

## CI (PR #194)
- **Cause:** both failing tests broke on one error. `lca/dataset.yaml` used `allocation: none`, which the library build cannot export when a process has several products (here Cl2, NaOH and H2).
- **Fix:** `lca/lca.yaml` now splits the burdens by the mass of what each product contains: Cl2, NaOH as 100 % and dry H2. That gives Cl2 46.5 %, NaOH 52.1 %, H2 1.4 %. The file also says why this departs from the library's allocation rules: there are no sourced prices, and cheme's built-in mass method counts the water in the caustic and the wet hydrogen. DESIGN.md D-013 is revised to match.
- **Still failing:** I ran the library's strict build locally. It now gets past the allocation and fails on about 25 missing entries in `../../lci/mappings.yaml`: links for the raw materials, spent acid and sludge, steam counted in kWh instead of kg, NaCl and Na2SO4 to water, and 11 zero-amount emissions. The build used to stop at the allocation, so these were hidden. I listed them all in DESIGN.md §7.
- **What would make CI pass:** someone adds those mappings in a library PR. The only fix inside this folder would be deleting `lca/dataset.yaml`. I didn't, because `cheme assess lca --write` regenerates it on every run. Tell me if you want it removed anyway.

## Findings closed
- **#1:** mass shares on the contained products, as above.
- **#2:** `lca/README.md` now points to DESIGN.md §6.
- **#3:** CO2 is now counted directly as fossil CO2 to air instead of a gap. The climate figure is now 1.1 g CO2-eq per kg Cl2, and DESIGN.md §6 says it covers this CO2 only.
- **#4:** the hydrogen-vent exclusion now says why the upper end of the BREF range does not apply here. I gave no amounts.
- **#7:** Ullmann's removed from the references in `process.yaml`.
- **#8:** the D-023 example in `checks.yaml` is now a placeholder.
- **#9:** D-004 now says how many electrolysers and rectifiers to use is open.
- **#10:** C-401 is now designed for 2 barg / full vacuum.

## Findings left open
- **#5 (C401 maturity):** neither `Stripping` nor `Desorbing` is a valid DEXPI class, so C401 stays `SeparatingByFlash`. The wrong maturity reading is noted for cheme-as-code in DESIGN.md §7.
- **#11 (`build_fs_schema.json`):** the file is at the worktree root, outside this folder, so I didn't delete it.
- **#6** was already accepted in the review.
- For #3, NaCl and Na2SO4 to water are still gaps, because no open characterisation for them is packaged.

## Checks after the changes
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** concept gates pass, apart from the layout gate (out of scope), as before. `design-review` now fails because the review record is older than these changes, so a new independent review is needed.
- **`cheme maturity`:** level none, as before.
- **`cheme process streams`:** every block and step closes in mass.
- **`cheme assess lca --coverage`:** partial screening carbon footprint, 14 gaps; mass, element and carbon balances closed.

Three commits on `case/chlor-alkali-1` (6086d5a, e3d269d, 69289b2), not pushed. A merge is pending: it needs the new review and the library mapping PR to get CI green.
