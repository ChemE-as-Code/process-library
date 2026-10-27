I've closed the one high finding (#1) and seven of the medium and low ones. Four stay open, and none of those is critical or high. Everything is committed in three commits on `case/hda-1` (`d4740fd`, `462bacc` and a third that adds the PROGRESS.md responses). Nothing is pushed, and nothing outside `processes/hda-1/` or any review or run record was edited.

**Closed** (each has a Response entry in PROGRESS.md with its commit):
- **#1 (high):** the LCA would have reached the catalog as a 0 kg CO2-eq result. process.yaml now has `lca: {source: none, notes: …}` until a background is linked. I checked that the catalog builder only reads `lca/` when the source is `auto`. The tool behaviour that causes it is a `total` row of 0 written when every contribution is a gap. It is recorded in DESIGN.md D-011 as something to report to core and the library tooling.
- **#2 (medium):** the boundary is now labelled one way everywhere: a cradle-to-gate study with only its foreground inventory, every background a gap. This covers DESIGN.md, process.yaml and lca.yaml. The memo heading now reads "plant boundary (battery limits)".
- **#3 (medium):** the omissions are now declared in lca.yaml, and `--coverage` lists them:
  - fugitive leaks: not estimated, and not claimed to be negligible;
  - no process wastewater: this rests on a new assumption, a dry vacuum pump on C-203, recorded in D-008;
  - vacuum-pump power and small-pump power: each about 15 kW, ASSUMED, entered as cut-off flows.
- **#5:** D-005 now gives the reaction heat as ~1.95 MW (7.0 GJ/h), not ~7 MW.
- **#6:** the two pressure rises without a pump step (S17 and S23) are noted on the streams and in D-010. The BFD/PFD were rebuilt.
- **#8:** the gas-basis LHV is kept, with the reason written down (it moves benzene's energy share by about 0.2 percentage points).
- **#10:** D-013 explains that `publication: public` in the LCA files only means the sources allow publication. process.yaml's `internal` status is what decides.
- **#11:** the script docstring is corrected.

**Left open:**
- **#4 (medium):** the Douglas (1988) reactor values still need reading in the book. I couldn't check them in this run, so they stay labelled "recalled, not read".
- **#7:** the core issue for the PFD symbol bug needs to be filed by a maintainer.
- **#9:** showing the fuel-gas credit side by side with other allocations only makes sense once backgrounds are linked.
- **#12:** the plot plan belongs to a later layout run.

**Check results after the changes:**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme process streams`:** every block and step balances.
- **`cheme assess lca --coverage`:** a partial screening result with 10 gaps and no total; mass, element and carbon balances close.
- **`cheme maturity`:** level none, while process.yaml claims `concept`. This is unchanged and is explained in the manifest.
- **`cheme check`:** five of the six applicable concept gates pass. `layout-plot-plan` still fails (#12). The basic-stage `design-review` gate now reports the 2026-10-27 review as out of date because the files it covered have changed, so a new independent review of these commits is needed.

**Merge:** pending. The branch needs that re-review and a human merge, and the concept stage can't be signed off while `layout-plot-plan` fails.
