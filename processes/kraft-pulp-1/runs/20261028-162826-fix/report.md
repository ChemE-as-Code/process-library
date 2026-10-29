I closed the one high finding and every medium and low finding except one, in two commits on `case/kraft-pulp-1` (`b356adc` for the changes, `0d409dd` for the PROGRESS.md responses). Nothing is pushed, and nothing outside `processes/kraft-pulp-1/` changed.

**Findings closed (review 2026-10-28-pfd-lci-review):**
- **#1 (high), fossil CO2 understated:** I set `carbon_accounting.trace_emissions: false` in `lca/lca.yaml`, so each CO2 flow keeps the origin declared on it (fossil or biogenic). The published climate result is now **0.0823 kg CO2-eq/kg pulp** (it was 0.050). That matches the inventory and the hand check.
  - One error is still in the core tool, not in this case. The product's carbon content is still split by the plant-wide fossil share, so `results.md` shows a "fossil carbon content of the product" of 0.0084 kg C. It should be 0, since the pulp's carbon is all wood carbon.
  - I put a visible warning about this in `lca/README.md`, in `process.yaml` `validation.notes` and in DESIGN.md D-012. It still needs raising with core.
- **#2 (medium), core dependencies not checked:** I recorded core main at `7bed468`. The issues are in `ChemE-as-Code/core-archive`, all closed:
  - **#364:** covers only salt water (NaCl), so the white, green and black liquors are still outside it.
  - **#365:** adds a solids basis, which changes nothing here.
  - **#370:** covers the lime kiln. I added `process/furnaces.yaml` and ran `cheme process furnace`. The installed cheme 0.8.0 lacks Cantera, so I ran it from core `7bed468` in a temporary uv environment; the installed tool is unchanged.
  - **Kiln result:** with 15 % heat losses (assumed), the balance needs 15.4 MW of fuel against the 17.4 MW in the flowsheet. The sourced 1.5 GJ/ADt therefore implies about 24 % losses, which is plausible. Core also warns that the kiln's specific fuel use is below its typical range; D-009 explains why that range doesn't fit here.
- **#3 (medium):** counting the lime-kiln calcination CO2 as biogenic is now marked as an assumed convention, because no guidance document is cited. Counted as fossil instead, it would add 0.172 kg CO2-eq/kg.
- **#4:** `validation.notes` now says the calculation maturity is none, and why.
- **#5:** D-011 says which black-liquor solids mass the steam ratio applies to, and checks the steam figure against heating value and boiler efficiency (66–75 %).
- **#6:** the heat of reaction for lime calcination is now 178.32 kJ/mol, from the furnace run's thermochemistry. The other inorganic heats of reaction are still recalled values, marked assumed; they enter no balance.
- **#7:** D-014 explains that the 20.7 % "energy closure" only compares cooling-water heat with exported electricity, so the check does not apply.
- **#8:** the chlorine dioxide and sulfuric acid inputs now have a fixed basis in `lca.yaml` and `mappings.yaml`, with the conversion needed for a 100 % background dataset.
- **#9:** D-001 now compares the route with sulfite, soda/AQ and mechanical/CTMP pulping.

**Left open:**
- **#10 (low), PFD readability:** the review proposes pinning a tidier PFD layout at the next stage, so I left it for then.
- **#11** was already accepted in the review.

**Re-runs after the changes:**

| command | result |
|---|---|
| `cheme validate` | 0 errors, 0 warnings |
| `cheme process streams` | every block and step balances |
| `cheme assess lca --coverage` | partial screening carbon footprint with the same 17 gaps; mass, element and carbon-origin balances closed; publishable |
| `cheme maturity` | unchanged: calculation maturity none, and the `concept` claim still gets the claim-exceeds warning |
| `cheme check` | concept gates pass |

`cheme check` also shows `design-review` failing, because the files the review covered have changed; it needs a fresh independent review. The P&ID, layout and datasheet gates fail as expected at the concept stage.

**Merge pending:** a reviewer still needs to re-review the branch and merge it.

STATUS: DONE