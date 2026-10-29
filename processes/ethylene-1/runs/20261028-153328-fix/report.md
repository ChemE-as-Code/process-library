I worked through every finding in `reviews/2026-10-28-pfd-lci-review.md`. The fixes are in commit `63fe760`, and the "Response" entries are in PROGRESS.md in commit `09df597`. Nothing was pushed, and nothing outside `processes/ethylene-1/` changed. All ten findings were wording and disclosure fixes: no stream value, balance or LCI number changed.

**Closed:**
- **#1 (high, the only critical or high finding):** the CO2 figure was mislabelled. It now reads 0.472 kg/kg ethylene unallocated and 0.433 kg/kg with mass allocation (ethylene share 91.6 %), in `process.yaml`, D-016 and D-018. D-016 now says that `inventory.csv` is allocated per kg of ethylene and `dataset.yaml` is unallocated.
- **#2 (medium):** I took the review's second option and corrected the text rather than the model. D-014 no longer claims the C2 splitter and demethaniser reboilers are "heat-integrated"; it says they are not modelled and not credited. The refrigeration power (78.3 MW) and the condenser duties are now labelled conservative upper estimates in D-014, D-018, the Q402/Q501/Q503 source texts and `lca.yaml` feed:POWER.
- **#4 (medium):** the `cheme maturity` result (none) and the acknowledged `maturity-claim-exceeds` warning are now in the manifest's validation notes.
- **#5–#9 (low):** yield basis (0.788 kg/kg fresh feed, 0.82 kg/kg ethane), the primary-energy arithmetic (8.6–9.8 GJ/t, at or below the lower end of the BREF range), where the feed CO2 goes (spent caustic, not flue gas), the propane coil's product slate (D-005), and the caustic ratio marked unsourced with both caustic LCI exchanges flagged as upper bounds.
- **#10 (low):** DESIGN.md now records that this case study is not taken to a concept sign-off, because the plot plan is outside its scope.

**Left partly open:**
- **#3 (medium):** the disclosure is done. `process.yaml`, the allocation note in `lca.yaml` and D-015 now say the CO2 and power per kg are gross because the exported steam carries no burden. The review also proposed an LCA scenario that nets the steam against the power or credits it by substitution. I didn't build it: it needs a separate flowsheet case and belongs with the allocation decision. It is recorded as open in D-015. A follow-up review should split this finding rather than mark it fully closed.

**Checks after the changes:**
- **`cheme validate`:** 0 errors, 0 warnings. The BFD and PFD were rebuilt and the LCA outputs rewritten.
- **`cheme check`:** the same gates pass as before. `design-review` now fails, as expected, because the reviewed files changed; a new independent review is needed. The plot-plan, P&ID, layout, MTO and datasheet gates still fail because that work is outside the scope.
- **`cheme maturity`:** calculation maturity none, unchanged and now stated in the manifest.
- **`cheme process streams`:** every block and step balance is ok.
- **`cheme assess lca --coverage`:** partial screening carbon footprint, mass, element and carbon balances closed, publishable; the declared gaps are unchanged.

Merge pending: branch `case/ethylene-1` needs a new review, then a merge by a human or the reviewer.

STATUS: DONE