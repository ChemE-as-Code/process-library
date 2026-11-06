# 0036. Public is the default publication status

- **Status:** Accepted, 2026-11-06
- **Deciders:** the owner, as the library's maintainer (implemented by an agent session)
- **Scope:** the publication rules: `publication` of `process.yaml`
  (`schemas/process.schema.json`, `templates/process/process.yaml`), CONTRIBUTING.md "Publishing a
  process". Supersedes the rule of [ADR 0010](0010-public-and-preview-builds-fail-closed.md) that
  `internal` is the default and that setting `public` is the maintainers' decision in its own
  change, and the words "`internal` by default" of
  [ADR 0004](0004-process-manifest-and-entry-kinds.md). The rest of both stands; `scripts/publication.py`
  `is_public` now also requires the licence, which keeps ADR 0010's fail-closed rule.

## Context

Under ADR 0010 a new process was written with `publication.status: internal` and stayed out of
the public build until a maintainer set `public`, with a licence, in a change of its own. In
practice the owner has published every process: all 50 at once on 2026-11-01
([ADR 0026](0026-public-processes-may-be-preliminary.md)), and since then each entry has been
written for the public from its first commit, under the library's CC BY 4.0 for data and
designs, in a public repository. The separate publishing change added a step, a second pull
request per entry, and a period in which a finished entry was missing from the Atlas, without
protecting anything that the rules on sources and licences do not already protect. On
2026-11-06, 13 batch entries were waiting for that change (acetyl-chloride-1 to sodium-azide-1,
listed below).

Options considered:

1. **Keep `internal` as the default** and publish each entry in its own change. Keeps a manual
   step that the owner no longer wants to take entry by entry.
2. **Make the public build include every process unless it is marked internal.** Removes the
   step, but a missing field would then publish: the leak by omission ADR 0010 was written to
   prevent.
3. **Write `public` as the default value, and keep the build fail-closed.** Authors write the
   status and licence explicitly in every new entry, so the default lives in the template and the
   instructions, not in the code. The owner's decision of 2026-11-06.

## Decision

- **Every library entry is public.** A new entry is written with
  `publication: {status: public, license: CC-BY-4.0}` (CC BY 4.0 is the library's licence for data
  and designs, `LICENSE-DATA`). `templates/process/process.yaml` carries it, and CONTRIBUTING.md
  says so.
- **No separate maintainer change is needed to publish.** The pull request that adds an entry
  publishes it; its review is the review of what is published.
- **The builds stay fail-closed (ADR 0010).** The default is a value authors write, not a
  fallback of the build: `scripts/publication.py` `is_public` includes a process only when its
  `process.yaml` says `publication.status: public` and names its `publication.license`. A
  `process.yaml` without a status, with `internal` or `candidate`, or public without a licence,
  stays out of every `--public` build, so a forgotten field never publishes. The licence is
  written explicitly and has no default: the schema requires it on a public entry, the build
  leaves a public entry without one out, and the library tests (`tests/test_publication_policy.py`)
  fail on it, so the mistake neither publishes nor passes CI.
- **ADR 0013's rules apply in full.** No third-party content, facts and numbers only in our own
  form with their source, drawings generated from our own files, openly licensed material only
  with its licence and attribution. Since `README.md` and `DESIGN.md` are published as text,
  authors write them for the public from the first commit (or exclude a file with
  `publication.exclude`).
- **`internal` remains available** for an entry that must not be published, for example one that
  rests on data whose licence does not allow it, or an unfinished private study. Its
  `process.yaml` states its own reason in a comment beside the status (the template's generic
  comment does not count).
- **The 13 batch entries waiting on 2026-11-06 are published** with this change:
  acetyl-chloride-1, benzoyl-chloride-1, benzyl-bromide-1, benzyl-chloroformate-1,
  carbon-tetrabromide-1, copper-i-chloride-1, di-tert-butyl-dicarbonate-1, iodomethane-1,
  methylmagnesium-bromide-1, methyltriphenylphosphonium-bromide-1, p-toluenesulfonyl-chloride-1,
  phosphorus-tribromide-1 and sodium-azide-1. co2-electrolysis-bpm-1 stays internal until its
  own owners decide.

## Consequences

- An entry is in the Atlas when its pull request merges, with no second change.
- The protection moves earlier: the review of an entry's pull request is now also its publication
  review. A reviewer reads `README.md`, `DESIGN.md` and the data as public text, and checks the
  sources against ADR 0013.
- The public build still withholds by omission, so a malformed manifest keeps an entry out rather
  than letting it out. The cost is that an entry whose author forgets the status is silently
  missing from the public Atlas; the preview build shows it.
- A public entry can be preliminary (ADR 0026): public does not mean complete or reviewed, and the
  maturity and review status say how far it is.
- Entries that must stay out need a stated reason, which makes an exception visible instead of
  the norm.

## Evidence

- CONTRIBUTING.md "Adding a process" and "Publishing a process"; `templates/process/process.yaml`.
- `scripts/publication.py` `is_public`: `status: public` and a licence (before this change, the
  status alone); `schemas/process.schema.json` `publication`: a licence required when public.
- `tests/test_publication_policy.py`: the template writes public with CC-BY-4.0, every public
  entry states a licence, an internal entry states its own reason (not the template's comment),
  and a manifest without a status, or public without a licence, is not public. The nine entries
  whose tests pinned `internal` now assert public with CC-BY-4.0, and the other four
  (benzyl-chloroformate-1, carbon-tetrabromide-1, methylmagnesium-bromide-1, sodium-azide-1)
  gain the same assertion; the policy test covers every entry.
- The public catalog and LCI builds of this change list the 13 entries.
