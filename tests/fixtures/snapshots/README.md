Viewer snapshot fixtures: real `cheme export-static` output of core's examples/process-recycle
(the same snapshot the viewer's e2e tests use), filed under fixture-electrolysis so the catalog
and the Atlas embedding can be tested. Its sheets and streams are the recycle example's, not the
fixture process's.

It is exported for publication: its manifest's `excluded` records the default excludes,
`process.yaml` and fixture-electrolysis's own `docs/private/**`, so the catalog's `--public` build accepts it.
Regenerate it with core (`cheme export-static --exclude` needs core with that option):

```sh
cp -R <core>/examples/process-recycle /tmp/recycle && cd /tmp/recycle
git init -q -b main && git add -A
GIT_AUTHOR_DATE=2026-10-22T22:32:38+02:00 GIT_COMMITTER_DATE=2026-10-22T22:32:38+02:00 \
  git -c user.name=fixture -c user.email=fixture@example.org commit -qm "process-recycle example"
cheme export-static <library>/tests/fixtures/snapshots/fixture-electrolysis --repo /tmp/recycle \
  --exclude '.claude/**' --exclude AGENTS.md --exclude CLAUDE.md --exclude 'reviews/**' \
  --exclude PROGRESS.md --exclude 'scripts/agent-run/**' --exclude '**/.gitattributes' \
  --exclude process.yaml --exclude 'docs/private/**'
```
