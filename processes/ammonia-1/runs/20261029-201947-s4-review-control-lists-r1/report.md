I approved S4 of ammonia-1 and merged PR #255 (merge commit `fefac80`) after all CI checks passed. One section target is not fully met: `cheme control report` still has 4 info findings, though no gate counts them.

**What I re-ran**
- **Validate:** 0 errors, and nothing reported for the equipment, line or instrument lists or the process links.
- **Control report:** 0 errors, 0 warnings, 4 info. All four are sequence steps written as text because they need connections the P&IDs don't show yet: start-up nitrogen, the front-end vent to flare (twice) and the converter start-up heater. The PR reports them honestly, D-030 lists them as open, and the `control-complete` gate passes.
- **`cheme check`:** S4's gates pass (`process-basic`, `process-links`, `pids-valid`, `drawing-clean`, `pids-exist`), and so does the detail gate `control-complete`. The failing gates belong to other sections. This matches the PR body.
- **Spot checks against the stream table:** the setpoints from the flowsheet, the steam ratio (3.146) and air ratio (2.277), O2 1.69 mol%, H2/N2 3.007 and the solvent rate of 1313 m³/h all agree. The provenance labels are honest and I found no copied third-party content.
- **I-104:** removing LV-1307 as a trip effect is correct, since a trip must not act on its own loop's control valve. This closes part of an earlier finding.

**New findings** (in `reviews/2026-10-29-control-lists.md`, committed and pushed, with a PR comment)
1. **Medium:** three start-up sequences can't start as written. Before step 1, they require trips I-101, I-105 and I-107 to be reset while their causes are still present (no steam yet, empty sump, empty separator). These trips latch, so they cannot be reset then.
2. **Medium:** no loop controls the front-end pressure or the capacity of synthesis gas compressor K-501, and no vent is drawn. The design notes (D-030) reject such a loop because there is no turndown case, but a loop doesn't need one to exist.
3. **Low:** the LP steam setpoint (657 kg/h) assumes saturated steam. The LP steam is let down from superheated MP steam, which gives about 540 kg/h.
4. **Low:** the front-end trip sequence hands over to the normal shutdown, whose permissives it has just made impossible. Its reset also leaves out I-105 and I-106.
5. **Low:** the H2/N2 setpoint of 3.0 is marked "calculated", but it is the stoichiometric target rounded from the simulated 3.007.
6. **Low:** the author made two shell edits against the repository rules. The PR disclosed them and the diff shows no damage.

**Still open from earlier reviews:** I-101 still doesn't close the tail-gas valve XV-1105, and the separator V-201 still has no low-low level protection. The other earlier medium and low findings are unchanged.

Both new medium findings should be fixed before the basic design review (S5r) and the HAZOP (S6). No merge is pending.

FINDINGS: critical=0 high=0 medium=2 low=4
VERDICT: approve
STATUS: DONE