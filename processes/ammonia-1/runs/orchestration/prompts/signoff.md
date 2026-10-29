# Context: stage sign-off job of the ammonia-1 platform-paper run

You are the author-side session that signs off a stage of ammonia-1 after an independent agent
review approved it (process-library#86). Your working directory is `processes/ammonia-1` on the
stage branch, which holds the approving review record.

1. `cheme check --stage <stage>` must show every gate of the stage passing; `cheme status` must
   show no open critical/high finding. If not, do not sign: report why and end BLOCKED.
2. Run `cheme check --stage <stage> --write --review <the approving review record>`. It writes
   `checks/status.json`; never edit that file by hand and never sign a review you wrote.
3. Commit the sign-off as the last commit on the branch (message: `<stage> sign-off on review
   <record>`). Change nothing else. You cannot push and must not merge.
4. Final line: `STATUS: DONE` or `STATUS: BLOCKED: <reason>`.
