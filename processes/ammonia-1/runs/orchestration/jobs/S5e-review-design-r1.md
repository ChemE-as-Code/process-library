# Review this section's PR: S5e of ammonia-1 (PR #257), round 1
Review topic for the record: `design`.
This section ends with a stage sign-off: on `VERDICT: approve` do **not** merge.
Branch: stage/basic-layout (checked out). Earlier sections are merged on main.

## S5e lifting lanes with motor cable entry points (on stage/basic-layout, PR #257; I-007)
cheme is now core v1.1.0 (installed; the same version CI pins): a motor's `cable_entry` in
`electrical/electrical-list.yaml` ends its tray beside the machine (core#73, ADR 0035; skill
`electrical-cabling`). S5c (D-041) left gate `lifting-study` failing on the lanes of K-101,
K-102, K-103 and K-701, blocked by their motor trays; the owner did not accept these and asked
to clear them by design (I-007). Also, three lanes the owner accepted in I-006 (K-501, E-504,
E-505) picked up extra blockers in S9 (K-501 motor tray, E-504 instrument tray, E-505 cooling-water
lines of E-503): clear those extra blockers by design too where possible, and otherwise say so;
the acceptance covers only the blockers named in the original proposal.
1. Run `cheme skills update` for the skills changed in 1.1.0 (keep local changes, report them).
2. Give cable entry points to K-101, K-102, K-103, K-701 and K-501 (side away from the lift lane,
   real terminal-box side where the datasheet says), rebuild `cheme layout build`, then
   `cheme layout lifting`; fix the remaining tray/line blockers by routing intents, pad or lane
   changes. Never accept a lane yourself.
3. Rebuild cable schedule (`cheme layout cables --write`), MTO and estimate if quantities moved;
   `cheme validate` 0 errors; `cheme check` and `cheme maturity`; DESIGN.md decision (next free
   D-number) and PROGRESS.md; commit; `build/pr-comment.md` short summary.
STATUS: DONE when every basic gate except the two review gates passes, else BLOCKED with the
exact remaining requirement. The basic reviews (topics `design`, `layout`), sign-off and merge follow.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
