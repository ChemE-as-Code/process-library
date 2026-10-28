# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | process/, equipment/, lca/, DESIGN.md, process.yaml, checks/ | answers to review 2026-10-28-pfd-lci-review (responses below), commit c0f8d04 | close the critical/high findings before merge |
| 2026-10-28 | lca/, process.yaml, DESIGN.md | preliminary gate-to-gate LCI (13 exchanges, all backgrounds unmapped as gaps, mass allocation, carbon origin); process manifest; decisions D-001 to D-013, source register | issue #186 scope: design basis to LCI |
| 2026-10-28 | process/, equipment/, scripts/glycerol_balance.py | design basis, materials, reactions, balanced BFD/PFD (5 blocks, 9 steps), equipment list | concept flowsheet of crude glycerol refining |
| 2026-10-28 | all | scaffold from cheme init | new case glycerol-1 |

## Responses to review 2026-10-28-pfd-lci-review

| finding | status | what changed | commit |
|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 (high) | closed | design-basis.yaml feed composition and source now equal S1/D-004 (glycerol 59.841, methanol 29.332, NaOCH3 2.847, fatty matter 7.98 wt%, no water); water content stays the D-004 open item | c0f8d04 |
| 2026-10-28-pfd-lci-review#2 (high) | closed | D-009 vacuum system: booster ejectors J-403 on MP steam 1000 kPa(a), 1.5 kg motive steam per kg vapour (ASSUMED, not sourced), intercondenser E-403 at 8 kPa(a) on cooling water, liquid-ring pump P-404 in W4; motive steam S22 (feed MSTM, 222.5 kg/h, 0.18 kg/kg product) through S15 to WW; Q7 135.7 -> 244.5 kW; D-012 energy now about 1020 kWh/t; LCI flow feed:MSTM with a `missing:` background (15 gaps) | c0f8d04 |
| 2026-10-28-pfd-lci-review#3 (medium) | closed | S9 425 K (ASSUMED from the glycerol-water boiling estimate), E-201 moved to MP steam (feed MPS, Q1 537.8 kW); E-301 kept at 10 kPa(a)/403 K with water out 1 wt% (Raoult estimate), so S10, S11, Q3, Q4, Q5 recalculated; sourced data or VLE still open (D-007, D-008) | c0f8d04 |
| 2026-10-28-pfd-lci-review#4 (medium) | closed | equipment-list notes refer to stream and duty ids (S.., Q.., W..) instead of numbers | c0f8d04 |
| 2026-10-28-pfd-lci-review#5 (medium) | closed | lca.yaml `allocation.compare: [mass, shares, none]`, shares = methanol as a return (GLYC 0.873, FAL 0.127, MEOHR 0); D-013 states the return as the preferred treatment once the crude-glycerol background is chosen; mass kept as baseline | c0f8d04 |
| 2026-10-28-pfd-lci-review#6 (low) | closed | NEUT1 heat_of_reaction -55.8 kJ/mol (ASSUMED); S3 341.6 K and S7 342.6 K from an adiabatic balance in scripts/glycerol_balance.py; simulation.yaml comment 18 kW | c0f8d04 |
| 2026-10-28-pfd-lci-review#7 (low) | open | Thompson & He PDF not re-read (no text extraction in this session); recorded in DESIGN.md section 6 | - |
| 2026-10-28-pfd-lci-review#8 (low) | closed | process.yaml validation.notes names the cheme.maturity-claim-exceeds warning and when it closes; claim kept | c0f8d04 |
| 2026-10-28-pfd-lci-review#9 (low) | open | the still vent carries no methanol after D-008; the E-302 vent loss needs its vent design; recorded in DESIGN.md section 6 | - |
| 2026-10-28-pfd-lci-review#10 (low) | open | tool finding for cheme-as-code (outside this folder); recorded in DESIGN.md section 6, not quoted as evidence | - |
| 2026-10-28-pfd-lci-review#11 (low) | closed | checks.yaml template comment no longer cites a decision id | c0f8d04 |
