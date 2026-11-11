# P&ID sheets

DEXPI 2.0.1 XML, one file per sheet. Start a new one with the `pid-draft` skill.

The sheets of hda-1 (S3b, DESIGN.md D-025), declared in `plant.yaml`. Each was first written by
`scripts/draft_<sheet>.py` and is hand-maintained from then on (no `generator:`).

| sheet | title | equipment |
|---|---|---|
| P-01 | Feed, heater and reactor | V-100, P-101, P-101B, E-101, H-101, R-101 |
| P-02 | HP separator and recycle gas | E-102, V-101, P-102, P-102B, K-101 |
| P-03 | Purge PSA and tail gas | PK-101, K-102, E-103 |
| P-04 | Stabiliser | C-201, E-201, V-201, P-201A/B, E-202 |
| P-05 | Benzene column, product | C-202, E-203, V-202, P-202A/B, E-204, E-207 |
| P-06 | Toluene column, biphenyl | C-203, E-205, V-203, PK-201, P-203A/B, E-206, P-204A/B |
| P-07 | Flare, nitrogen and fuel headers | headers FL-701, N2-702, NG-703 |
| P-08 | CW and steam headers | headers CWS-801, CWR-802, LS-803, MS-804, HS-805, CD-806 |

A line that continues on another sheet has the same number on both, and its off-page
connector names the other end and that sheet.
