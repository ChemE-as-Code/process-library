I reviewed the phosgene-1 case at 44cc313 and found no critical or high findings: two medium and three low. The review record is committed as 8c797a0 (`reviews/2026-10-28-pfd-lci-review.md`). I did not change any design files and did not push.

**Commands I re-ran:**
- **`cheme validate`:** 0 errors and 0 warnings.
- **`cheme check`:** every concept gate passes except the plot plan, because layout is outside the issue's scope. The design-review gate now passes with this record.
- **`cheme maturity`:** the evidence supports no maturity level yet, because the feeds and conversions are assumed. `process.yaml` claims `concept`, which is the lowest value the schema allows, and its notes say plainly that no level is reached, so I don't count it as dishonest.
- **`cheme process streams` and `propagate --check`:** every balance closes and nothing deviates.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 12 gaps. Each gap has a description; none is zero-filled or uses licensed data.

**Other checks:**
- **Scope and route:** match issue #164, and nothing outside `processes/phosgene-1/` changed.
- **Hand recalculation:** I recomputed the main numbers myself and they match the flowsheet:
  - feeds, conversion and yield (99.47 % on chlorine);
  - reactor heat (5.18 MW) and the equilibrium check;
  - both condenser duties, from the phosgene vapour pressure;
  - caustic use, oxidiser temperature, CO₂ (22.4 g/kg) and the carbon balance;
  - utilities per kg of phosgene.
- **Sources:** facts are in the design agent's own words with a source register, and I found no copied third-party content.

**Findings:**
- **R-01 (medium):** the spent scrubber liquor is set to 313 K, but the design also says the scrubber has no cooler. Destroying the phosgene in caustic releases about 444 kJ/mol, roughly 114 kW, which would heat the liquor by about 80 K to near boiling. Either a liquor cooler of about 0.1 MW is missing (adding about 2 % to the cooling water in the LCI), or the scrubber vent and liquor streams are wrong.
- **R-02 (medium):** `DESIGN.md` D-012 says the activated-carbon catalyst replacement is "excluded and listed". It isn't in `lca/lca.yaml`, so it is missing from `gaps.csv`, the coverage report and the dataset.
- **R-03 (low):** the containment enclosure's extracted air goes to the scrubber (D-011), but that air flow and its fan power aren't in the balance, and the design doesn't say whether the extraction runs all the time or only in an emergency.
- **R-04 (low):** the excluded oxidiser NOx and fugitive emissions have no amount, so the 1 % cut-off rule can't be checked.
- **R-05 (low):** the patent EP1640341A2 is cited without paragraph or claim numbers, so its individual figures can't be traced.

A merge of `case/phosgene-1` is pending; a human has to do it.

VERDICT: merge