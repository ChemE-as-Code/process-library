I've signed off the concept stage of ammonia-1. The sign-off is the last commit on `stage/concept-closeout` (`c6a1dcd`, "concept sign-off on review reviews/2026-10-29-concept.md"). It only adds `checks/status.json`, which `cheme check --write` generated; nothing else changed.

- **Gates:** `cheme check --stage concept` shows 7 gates passing and none failing. `issues-concept` doesn't apply because `plant.yaml` declares no issues.
- **Open findings:** none are critical or high. Four medium and low findings stay open: concept#1 (medium: X-601 has no separation distance from the A-900 control room and substation plot), concept#2–#4 (low) and pfd-lci-review#3 and #5. None of them blocks the sign-off.
- **Signer:** I signed as `author-agent`, not a person's name. The first attempt was refused because git has no `user.name` set, and I won't sign in the name of someone who didn't sign. The review was written by `review-agent`, a different agent, so I didn't sign my own review. If the sign-off should carry a person's name, run the `--write` again with `--by <name>` before merging.
- **Recorded commit:** `status.json` records the sign-off against `2ff4da1`, the commit before the sign-off commit, which is how the tool records it.
- **Commit identity:** git filled in the commit author automatically (Artur Schweidtmann, from the host name), the same as the earlier commits on this branch.

**Merge pending:** the branch is 9 commits ahead of `main` and not pushed. The concept stage is only reached once a human or the reviewer merges it into `main`.

STATUS: DONE