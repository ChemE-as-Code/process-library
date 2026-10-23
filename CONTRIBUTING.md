# Adding a process

1. `cp -R templates/process processes/<id>`: `<id>` is a lowercase slug and never changes once
   listed (it is the Atlas URL).
2. Fill in `process.yaml`. Be honest about `maturity` (how far the design is taken) and
   `validation.status` (who has checked it): passing automated checks is not a review.
3. Every chemical under `chemistry` must be a slug of `chemicals/chemicals.yaml`; add new ones in
   the same change, with CAS, InChIKey and ChEBI where they exist. Grade and phase (GOX, LOX) go
   in the flow's `note`, not in the registry.
4. Optional, as the process matures:
   - a cheme-as-code engineering project in the same folder (`cheme init`, then P&IDs, process
     YAML, layout, LCA): the catalog derives its sheets, gates, design basis and LCA results;
   - an LCI dataset (`lca/dataset.yaml`, written by `cheme assess lca --write`, or hand-written
     `lca/datasets/*.yaml`), and if it needs new background links, entries in `lci/mappings.yaml`.
5. Check: `uv run scripts/build_catalog.py --library . --out dist --strict` (and
   `scripts/build_lci.py ... --strict` with an LCI dataset). CI runs the same, and the public
   build (`--public`, below).

## Sources, licences and what may not be copied

The library is published: process data and designs under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (LICENSE-DATA), code under MIT
(LICENSE). Contribute only what may be published under these licences:

- **Never copy third-party content**: tables, figures, drawings, P&IDs, datasheet or manual
  text, screenshots or text from papers, books, standards, vendor documents or websites, and no
  values from licensed databases (ecoinvent factors or results, commercial property data).
- **Facts and numbers are fine in your own form, with their source** (`source:`/`provenance:`
  fields, `references:` in `process.yaml`, DESIGN.md); estimates are marked ASSUMED.
- **Draw and write everything yourself**: drawings are generated from the library's own files.
- **Openly licensed material** only with its licence and attribution in a `NOTICE.md` next to it,
  and only if that licence is compatible with CC BY 4.0 / MIT.

By contributing you agree that your contribution is published under these licences.

## Publishing a process

The Atlas has two builds. The preview build (the default) shows every process as the library
has it. The public build (`--public` of `build_catalog.py`, `build_lci.py` and
`export_snapshots.py`) is what may be published, and its data is public as a whole:

- Only processes with `publication.status: public` in `process.yaml` are in it; `internal`
  (the default) and `candidate` are left out entirely. Setting `public` is the maintainers'
  decision, made in its own change.
- `publication.license` names the license it is published under (an SPDX id, e.g.
  `CC-BY-4.0`). There is no default: state it when you set `public`.
- `repository` is shown only when its `access` is `public`.
- An LCA with placeholder factors (`lca/factors.yaml` `example: true`) is shown without its
  footprint values (totals, contributions, the headline value, the viewer's LCA answer and
  `lca/results.*`, `lca/uncertainty.csv`); its goal, functional unit, boundary and inventory stay.
- The viewer snapshot is exported without these paths, which always apply in public builds:
  `.claude/**`, `AGENTS.md`, `CLAUDE.md`, `reviews/**`, `PROGRESS.md`, `scripts/agent-run/**`,
  `**/.gitattributes` (kept in `scripts/publication.py`; change both together), and
  `process.yaml` itself (the catalog publishes what of it may be public). Add your own
  under `publication.exclude` (globs relative to the process folder: `**` spans directories,
  `*` stays in one, a plain name is the file at the folder root), for example `DESIGN.md` or
  `docs/private/**`. Everything else in the folder, including `README.md` and `DESIGN.md`, is
  published as text: write it for the public or exclude it.

```yaml
publication: {status: public, license: CC-BY-4.0, exclude: ["docs/private/**"]}
```

Do not rewrite another process's engineering files; change them through that process's own
review (its `DESIGN.md`, `reviews/`).
