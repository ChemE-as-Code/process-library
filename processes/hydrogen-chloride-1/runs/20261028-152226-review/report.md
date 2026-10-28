I reviewed the hydrogen-chloride-1 concept case at commit 60236ff and found nothing critical or high: 1 medium and 7 low findings. The record is `reviews/2026-10-28-pfd-lci-review.md`, committed as 985c6b4 and not pushed. With the record committed, `cheme validate` gives 0 errors and 0 warnings, and the `design-review` gate now passes. I changed no design file.

**What I re-ran myself:**
- **Validate:** 0 errors, 0 warnings.
- **Check:** every concept gate passes except `layout-plot-plan`, because layout was out of scope.
- **Maturity:** the evidence supports level "none", against the "concept" claim in `process.yaml`. "concept" is the lowest value the schema allows, and `process.yaml` says so openly.
- **Streams:** every block and step balances.
- **Propagate check:** no stale or deviating values.
- **LCA coverage:** "partial screening carbon footprint" with 7 gaps.
- **Changed files:** nothing outside `processes/hydrogen-chloride-1/` changed.

**Checked by hand and fine:**
- **Mass and element balances:** chlorine 0.972 kg per kg HCl, hydrogen 1.10 × stoichiometric, the demineralised water closure and the vent HCl at 10 mg/Nm³ all agree with the flowsheet and `scripts/balance.py`.
- **Duties:** the furnace heat release of 2268 kW and the absorber duty of 1672 kW agree with the script; the pump powers recalculate.
- **LCI:** per kg of HCl, mass in and out are both 3.03425 kg, and each exchange matches its flowsheet stream. Every background is left unlinked as a gap with a description, not as zero, and no licensed values are used. Per-process overrides sit in the folder's `lca/mappings.yaml`.
- **Sources:** facts are cited with locators and written in our own words; I saw nothing copied from third parties.
- **Scope:** route and boundary match issue #137 as described in the run's task notes.

**Findings:**
- **Medium (R-01):** the acid gets all the burden and the exported steam none. That departs from the library's allocation rules (ADR 0007), which fall back to comparing prices. The stated reason, that steam is counted in kWh so prices cannot be compared, does not hold. Once backgrounds are linked, the acid's footprint would be overstated by very roughly 5–15 %. No number is wrong today, because every background is still a gap.
- **Low (R-02):** 1.03 t steam per t HCl is close to the most that could be recovered at all. About 5 % of it comes from burning the oxygen impurity in the chlorine, and that is not flagged.
- **Low (R-03):** the absorber tail-gas water uses pure water's vapour pressure, although the gas leaves in contact with 33 % acid. It only shifts an internal stream by a few kg/h.
- **Low (R-04):** a comment in `flowsheet.yaml` says "equilibrium reactor"; R101 is a conversion reactor.
- **Low (R-05):** the one-line summary in `process.yaml` should state that the evidence supports maturity level "none".
- **Low (R-06):** the acid product and the chlorine feed are missing from `process.yaml`'s chemistry list, because the chemicals registry lacks them.
- **Low (R-07):** the integral heat of solution and the reaction enthalpies were taken from second-hand reads. The value of −61.4 kJ/mol is still plausible, and there are minor citation slips.
- **Low (R-08):** a template comment in `checks/checks.yaml` cites a decision D-023 that does not exist.

**Not checked:** I did not run the library LCI build (`build_lci.py --strict`), read the issue thread itself, or re-fetch the cited sources.

The task asked for ids R-01 …; the validator requires the form `2026-10-28-pfd-lci-review#n`, so the table uses that and puts the R-number at the start of each finding.

The merge is pending: it needs a human or the reviewer, not the author.

VERDICT: merge