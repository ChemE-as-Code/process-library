I reviewed the case at `adfad09` and found no critical or high findings: 2 medium and 7 low. The record is `reviews/2026-10-27-pfd-lci-review.md`, committed as `fa46c65` on `case/soda-ash-1`. I did not push it, and no design file was changed.

**What I re-ran:**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings.
- **Gates:** every concept gate in `cheme check` passes except the plot plan, which is out of scope. With this review committed, the `design-review` gate now passes too.
- **Maturity:** `cheme maturity` says the evidence supports no level, while `process.yaml` claims `concept`. `concept` is the lowest value the manifest allows, so the claim is honest.
- **Balances:** `cheme process streams` shows every block and step balanced, and `cheme process propagate --check` is clean.
- **LCA:** `cheme assess lca --coverage` gives a partial screening result with 11 gaps; mass, element and carbon balances close.
- **Balance script:** running `scripts/solvay_balance.py` reproduces every stream in `flowsheet.yaml`. Only files under `processes/soda-ash-1/` changed on the branch.

**Engineering checks by hand.** These all agree with the case:
- the sodium utilisation of 0.73, the 5 % excess lime and 1.04 t CaCl2 per t of product;
- the CO2 balance: 719 kg/t from the kiln, 306 kg/t vented;
- the kiln gas at 36.6 % CO2, the compressor at about 2.6 MW and the calciner at about 27.5 MW;
- consumption per tonne (salt 1.50 t, limestone 1.08 t, coke 88 kg, steam 1.88 t), at the optimistic end of typical Solvay figures.

The inventory is per kg of soda ash, and mass in equals mass out (13.299 kg per kg). No gap is filled with zero and no licensed values are used. I found no copied third-party content, and estimates are marked ASSUMED.

**Findings:**
- **R-01 (medium):** the only LCA number, 0.306 kg CO2-eq per kg, is the vented CO2 alone. Nothing in plain words says so, and the uncertainty interval looks like that of a full footprint. A catalogue reader could take it for the product's carbon footprint.
- **R-02 (medium):** the parameters that set the raw-material and waste flows have no sources (the "about 70–75 %" utilisation range has no locator). They are marked ASSUMED and called optimistic, but they push the inventory low.
- **Low:**
  - R-03: the energy cross-check adds numbers on different bases.
  - R-04: the stated formation enthalpies give 179.0 kJ/mol for calcination, not the 178.3 in the file.
  - R-05: the USGS and energy-review sources are missing from `references:`, and the EMEP edition differs between files.
  - R-06: the maturity notes don't say that `cheme maturity` supports no level.
  - R-07: the distiller tag D-601 looks like a decision id and triggers `decision-unknown` notices.
  - R-08: the distiller-waste CaCl2/NaCl discharge and the kiln pollutants are listed as gaps, with no amounts.
  - R-09: the kiln gas washer has no wash water or blowdown.

The merge to `main` is pending; a human has to do it. R-01 and R-02 should be fixed or accepted before the case goes into the catalogue, but they don't block the merge. Git set the commit author automatically from your username and hostname, so check that it's right.

VERDICT: merge
