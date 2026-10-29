I've closed the one high finding (#1) and eight of the nine medium/low findings (#2–#6, #8–#10). #7 stays open because it needs sourced data or a person to accept it. Everything is in two commits on `case/acetic-acid-1`, `34f3d03` (the changes) and `7955e60` (the Response entries in PROGRESS.md). Nothing was pushed, and nothing outside `processes/acetic-acid-1/` or any existing review or run record was touched.

**Findings closed**
- **#1 (high), the flash energy gap:** `scripts/balance.py` now balances the reactor (R-101) and the flash (V-102) separately. The reviewer's numbers check out: the reactor's external circuit removes 17.7 MW, and the flash split as specified needs 11.2 MW of heat. I kept the split and supplied that heat from the reactor circuit through a new flash heater, E-102 (reactor liquid at 463 K heating the flash at 413 K). This is option (b) from the review, recorded as decision D-014. It adds a new duty Q13 from R101 to V102 and E-102 in the equipment list.
  - Q03 is now the reactor's cooling-water duty only (6.6 MW), and D-008 is corrected.
  - The steam, cooling-water and LCI figures don't change, because the heat stays inside the plant.
  - **This arrangement is an assumption:** no source shows it for this route. If it isn't built, steam rises by about 0.19 kWh/kg (roughly 40 % more), which I recorded as the sensitivity case. The heater arrangement, split control and catalyst stability in a heated flash are a new open input, O-9.
- **#2:** I removed nitrogen and methane from the feedstock list. Hydrogen stays as a minor reactant, with a note saying methanol and CO are the real feedstocks. The registry entries for them still need a separate library PR outside this folder.
- **#3:** the unread source S2 no longer supports any decision. The low-water reason and the propionic acid value now rest on the patent's examples (S1).
- **#4:** the reactor feed S06 is now 378.7 K, from the mixer's enthalpy balance. `balance.py` prints it.
- **#5:** stream S18 is renamed by its composition (methyl acetate-rich). D-006 now says the decanter split is not checked against liquid-liquid equilibrium.
- **#6:** the gap count is corrected to 8.
- **#8:** DESIGN.md now records that the concept gate `layout-plot-plan` is open on purpose; the concept stage won't be signed off without a plot plan.
- **#9:** D-013 now explains why the inventory is called gate-to-gate while `lca.yaml` declares cradle-to-gate.
- **#10:** `lca/README.md` and D-013 say the generated 0 total means "no total", not a zero footprint. The underlying display issue in cheme-as-code still needs reporting.

**Findings left open**
- **#7 (low):** `cheme maturity` still warns that the claimed "concept" maturity exceeds the evidence. Clearing it needs sourced values for the separators, CO gas and capacity, or a person accepting the warning; I kept the existing disclosure.

**Checks after the changes**
- **`cheme validate`:** 0 errors and 0 warnings.
- **`cheme process streams`:** every block and step balances. Q13 shows 11,169 kW and S06 shows 378.7 K.
- **`cheme assess lca --coverage`:** partial screening carbon footprint with 8 gaps; the mass, element and carbon balances close, and it is publishable.
- **`cheme maturity`:** calculation maturity none, with the #7 warning.
- **`cheme check`:** concept gates pass except `layout-plot-plan`, and the basic and detail gates still fail as before. `design-review` now also fails because the reviewed files have changed since the review, so a fresh review is needed.

A merge is pending: the branch needs that re-review and a human merge.

STATUS: DONE