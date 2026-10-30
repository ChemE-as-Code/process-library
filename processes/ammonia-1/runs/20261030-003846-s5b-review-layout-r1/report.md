I reviewed the layout side of S5b on PR #257 at commit 14ba335, and the verdict is **fix**. The record is `reviews/2026-10-30-layout-s5b.md`; I committed and pushed it as ce8b029 (that push also carried 14ba335 to the remote) and posted a comment on the PR. With this record the `layout-review` gate passes again.

**Gates, re-run myself:**
- `cheme validate`: 0 errors, 183 warnings.
- `cheme layout build --check`: model up to date, no clash, headroom or zone finding.
- `cheme check --stage basic`: everything passes except two gates:
  - **`lifting-study` fails**: 11 crane lanes are still blocked, none accepted, and there is still no crane chart.
  - **`maturity-balanced` fails**: the feed flows and compositions (S1, S12, S61, S26, S70) are not given with a published source.
- There is still no class 4 estimate: `cheme assess estimate --check` says no current estimate exists, and `estimate/rates.yaml` is still the example file.

**What S5b got right:**
- I checked all 27 crane pads and 14 laydowns in plan. No pad overlaps equipment, racks, structures, roads, pipes below 4 m or hazardous zones.
- Rerouting the V-502 relief line PG-1120 west of V-501 clears V-501's crane lane.
- The equipment weights used in the lifting study match the equipment list, and nothing was accepted or relaxed.

**New findings:**
- **Medium (s5b#1):** Some lanes are handed to the owner as "erection sequence only" without anyone trying to reroute the line in the way:
  - **V-701:** a pad on open ground just south of the vessel would have a clear lane except for AL-1129. That is a small line (DN 25) from X-601, not V-701's own outlet as the proposal says, and it runs along the top of the vessel.
  - **E-301 and E-303:** the demineralised-water line DW-1073 (also DN 25) runs 8.85 m up, straight over E-301, E-302 and E-303. It blocks every lane tried for E-303 and all but one for E-301.
  - The fix is to pin both lines with vias that keep them clear of these items, then re-run `cheme layout lifting`.
- **Low (s5b#2):** laydown LD-204 reaches 2 m into access road R-5.

**Still open from earlier reviews:** the high finding 2026-10-29-design#1 (the failing gates and missing estimate above), plus the medium ones: the H-101 fuel hazardous zone missing its valve trains (layout-r3#1) and the two design-s5b findings.

**Not verified:** I tried two of the newly cited sources (EPA AP-42 §1.4 and Lin et al. 2024). Both refused access, so I could not check them.

Merge is pending: not merged and no sign-off, as the task requires for this section.

FINDINGS: critical=0 high=0 medium=1 low=1
VERDICT: fix
STATUS: DONE