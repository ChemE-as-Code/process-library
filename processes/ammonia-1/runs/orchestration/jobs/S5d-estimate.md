# Your job: S5d-estimate of ammonia-1 (branch stage/basic-layout, PR #257; owner decision I-006b)
Branch: stage/basic-layout (checked out). The owner asked for one more focused attempt (cap USD 10)
to bring the capital estimate from class 5 to class 4 with sourced data found online. S5c (D-044)
kept `estimate/rates.yaml` as the example because it found no open bulk unit rates and the
correlations lacked factors for Cr-Mo, refractory-lined and >140 barg equipment. Read D-044,
`estimate/`, the skills `mto-estimate` and `tea` first.

Do (web search and fetch for every value; our own words; source with URL/DOI and exact locator;
year; status; mark ASSUMED where a judgement is applied):
1. Cost index: a published CEPCI value (latest annual you can cite) and the base year of each
   correlation, so every cost is escalated with a cited ratio.
2. Equipment costs: open, citable correlations (textbooks with published equations, government
   or university cost reports, e.g. NETL/DOE baseline methodology, open-access papers) including
   **material factors** (Cr-Mo, stainless, clad) and **pressure factors** up to the loop pressure,
   and a sourced approach for refractory-lined vessels and fired heaters/reformers.
3. Bulk/installation: a sourced factor method (e.g. detailed installation factors per equipment
   class for piping, instruments, electrical, civil, structural, insulation, paint, erection) in
   place of unit rates where open unit rates do not exist; take-off quantities stay from the MTO.
4. Put them in `estimate/rates.yaml` (status, source, year), rebuild `cheme assess estimate
   --write`, update the TEA. State the estimate class per AACE 18R-97 definition criteria (cite),
   its accuracy range, and what drives it; if class 4 is still not justified, say exactly which
   input is missing.
Do not change the layout, the flowsheet or the lifting work (a separate job does lifting).
`cheme validate` 0 errors; commit (decision D-045 in DESIGN.md, PROGRESS.md); write
`build/pr-comment.md` (short summary for the PR). Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
