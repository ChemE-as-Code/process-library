I closed six of the review's seven findings and left one open. The review had no critical or high findings. Everything is committed in two commits (`462152f` for the changes, then the PROGRESS entries) and nothing was pushed. All changes are inside `processes/sodium-cyanide-1/`.

**CI:** I found nothing to fix. `gh pr checks 237` showed every finished check passing, including `validate (processes/sodium-cyanide-1)`, and the rest still queued or running. No run on the branch had failed, so there was no failed log to read. I noted this in PROGRESS.md.

**Findings closed:**
- **#1 (medium), steam export:** I kept the adiabatic converter and now state the export as an upper bound, probably 15–20 % too high. The note is in D-009/D-010, the Q8/Q9 provenance, lca.yaml and process.yaml. B-301's efficiency is now stated as ASSUMED 89 % of the tail gas heating value, with only the stack loss counted. No numbers changed, and the BFD/PFD were rebuilt because the flowsheet text changed.
- **#2 (medium), inputs missing from the LCI:** boiler feed water, phosphate make-up and the HCN stabiliser acid are now entries in lca.yaml, each listed as a gap.
  - Boiler feed water is two entries: the water that leaves with the exported steam, and the make-up for blowdown and condensate losses. D-012 now says how steam is counted.
  - The phosphate (20 t/a) and stabiliser (27 t/a) amounts are ASSUMED placeholders with no source, there only so the gaps show.
  - Mass still closes (15.65 kg in and out per kg product), and the gap count went from 12 to 18. I rewrote the generated LCA output files.
- **#4 (low):** D-010 and process.yaml now say the chiller power (about 0.8–1.2 MW) is not in the plant's 1.03 MW.
- **#5 (low):** when the Pt/Rh gauze gets a background dataset, it should count the net metal loss, not the whole charge each campaign. It stays a gap until then.
- **#6 (low):** D-004 now calls the catalyst-window warning a known warning rather than "accepted". No gate covers that rule, so there was no acceptance to record.
- **#7 (low):** D-012 now reports the 75.6 % energy closure. The tool only compares electricity and heat rejected with the steam exported. It leaves out the feeds' chemical energy, the reaction heat and the tail gas heating value, so the missing quarter is a limit of the ledger, not a real loss.

**Left open:**
- **#3 (low), the neutraliser product may be supersaturated:** I recorded the risk in D-008 with a likely reason (free NaOH lowers the solubility of the mother liquor) and a measure for basic engineering. I can't show the product stays in solution because there is no sourced NaCN solubility at different temperatures and NaOH levels.

**Re-runs after the changes:**
- `cheme validate`: 0 errors, 1 known warning (the catalyst window).
- `cheme process streams`: every block and step balances.
- `cheme maturity`: unchanged. Calculation maturity is none, with the same warning that the "concept" claim exceeds the evidence.
- `cheme assess lca --coverage`: a partial screening carbon footprint with 18 gaps; mass closes.
- `cheme check`: concept gates pass except the plot plan, as before. The basic-stage `design-review` gate now fails because the reviewed files have changed since the review, so it needs a new independent review.

A merge is pending: the branch needs that new independent review and a human merge.

STATUS: DONE