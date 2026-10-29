The review is committed as `7a2aa6a` (`reviews/2026-10-28-pfd-lci-review.md`, reviewed commit `a747a45`). It has one high, three medium and four low findings, so the branch needs a fix before it merges. It is not pushed and the merge is pending. I changed no design files, and the branch changes nothing outside `processes/ethylene-glycol-1/`.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings, including the new review record.
- **`cheme check`:** the concept-stage gates pass except the plot plan. Layout was declared out of scope, so the concept stage can't pass as configured.
- **`cheme maturity`:** the evidence reaches no calculation level, but `process.yaml` claims `concept`. The file says so openly, and `concept` is the lowest value the schema allows.
- **`cheme process streams` and `propagate --check`:** every step balance closes. Both reactors' extents match what DESIGN.md states.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 11 gaps, each with a description. Mass, element and carbon balances close, and there are no zero-filled or licensed values.

My hand checks of the main numbers also hold: ethylene, oxygen and CO2 per tonne of EO, the 1.68 t MEG per t ethylene, the recycle gas composition, the inerts purge balance, the water balance per kg MEG, the compressor power and the reactor heat.

**Findings:**
- **#1 (high):** the EO loop's energy balance doesn't close.
  - The balance script counts all 83.5 MW of reaction heat as steam raised in the EO reactor (R-101), which is only true if gas leaves at its inlet temperature. The flowsheet has the gas entering at 333 K and leaving at 523 K.
  - The equipment list describes E-101 as a feed/effluent exchanger, but only its trim cooler is modelled.
  - Even with that exchanger in place, the gas still heats up about 40 K inside the reactor. That takes roughly 17 MW of the reaction heat, so less steam is raised for the rest of the plant.
  - The result is that the MP steam import, 1.62 GJ/t MEG in DESIGN.md and the LCI, is too low by more than the ±50 % the design claims for its energy estimate.
- **#2 (medium):** heating the glycol reactor feed from about 397 K to 423 K (about 10.6 MW) is not counted anywhere. The recycle water also gains 10 K across a splitter, which can't happen (about 3.8 MW). Together with #1, the steam import is about 2 to 2.5 times too low: roughly 50 MW instead of 22.5 MW.
- **#3 (medium):** the glycol-to-water rate ratio of 2.0 is assumed without a source. It puts the MEG share and the MEG per t ethylene at the top of the cited ranges, and no sensitivity is given.
- **#4 (medium):** the silver catalyst, potassium carbonate make-up and moderator are left out only in a comment in `lca.yaml`. They are not declared, so the dataset's limitations don't show them.
- **Low:**
  - **#5:** the purge gap description says 2.7 kg CO2 per kg purge; its own composition gives 2.2.
  - **#6:** the maturity claim in `process.yaml` exceeds the evidence.
  - **#7:** the heavy glycols residue is below the cited range.
  - **#8:** the concept-stage plot-plan check fails although layout is out of scope.

VERDICT: fix