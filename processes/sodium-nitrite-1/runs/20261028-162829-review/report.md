I've reviewed the sodium nitrite case and found nothing critical or high, so it can be merged. The review is committed as `0adee49` (`reviews/2026-10-28-pfd-lci-review.md`, reviewing HEAD `2fa1746`). It has 12 findings: 3 medium and 9 low. Nothing is pushed, and a merge by a human is pending.

**What I re-ran:**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings, both before and after adding the review.
- **Gates:** `cheme check` passes every concept gate except the plot plan, which is out of scope. The later-stage gates fail as expected because there are no P&IDs, layout or datasheets yet.
- **Maturity:** `cheme maturity` reports none. `process.yaml` claims `concept`, which is the lowest value the schema allows, and its notes say so honestly.
- **Balances:** `cheme process streams` shows all 4 blocks and 11 steps balanced, and `propagate --check` is clean.
- **LCI:** `cheme assess lca --coverage` shows 8 gaps. Each missing background has a description, nothing is filled with zero, and the mass, element and carbon balances close.
- **Scope:** nothing outside `processes/sodium-nitrite-1/` changed. The plain diff against `origin/main` shows deletions in other folders only because the branch starts from an older main.

**Checked by hand:**
- The nitrogen, sodium and carbon balances for the whole plant close.
- The absorber gives the stated 20:1 nitrite:nitrate ratio, with 0.537 of the NO oxidised to NO2.
- The burner duty comes out at about 1,960 kW, against cheme's 1,964 kW.
- The tail gas is 670 ppmv NOx, 916 ppmv N2O and 3.8 % O2 (dry).
- The LCI quantities match the flowsheet after allocation, with 86.2 % of the burden on NaNO2. The direct emissions give 1.47 kg CO2-eq/kg.
- I re-read the main patent source (US 2 032 699) and its numbers are used correctly.
- I found no copied third-party content.

**Medium findings:**
- **#1 Evaporator steam is probably understated.** The calculation counts only the heat to boil off water. It leaves out heating about 16 t/h of liquor from 40–55 °C up to 125 °C (about 1.1 MW) and the boiling-point rise of the strong liquor. Site LP steam is likely low by tens of percent, both in the plant figures and in the LCI.
- **#2 The site LP steam may be too cold for the evaporator.** At 450 kPa(a) it is 147.6 °C, and a double effect ending at 125 °C near atmospheric pressure needs steam above roughly 155 °C. The waste-heat-boiler steam is hot enough; the site steam may not be.
- **#3 A conflicting N2O figure isn't reported.** One of the cited patents (US 12 565 427) reports about twice the N2O per kg of ammonia that the design assumes from the IPCC value; the design doesn't mention it. N2O is 79 % of the direct climate result. That patent's own nitrogen figures don't add up, which is why I rated this medium rather than high.

**Low findings:**
- The blower outlet temperature and the soda dissolver temperature are inconsistent with the rest of the balance.
- Two comparisons with that same patent, on product yield per kg of ammonia and on steam raised, are left unexplained.
- Ammonia and NO2 emissions to air are marked burden-free.
- The per-kg figures in `process.yaml` are before allocation, while the LCI shows allocated ones.
- One solubility source has no DOI.
- The NO/NO2 control wording ("slightly below 0.5") contradicts the 0.537 in the balance.
- When the soda ash supply is linked later, its CO2 could be counted twice.

The task asked for ids R-01 onwards. The record uses the repository's own id format (`2026-10-28-pfd-lci-review#n`), which the validator checks, and shows R-01 to R-12 next to each one.

VERDICT: merge