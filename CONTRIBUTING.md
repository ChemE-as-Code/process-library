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
   `scripts/build_lci.py ... --strict` with an LCI dataset). CI runs the same.

Do not rewrite another process's engineering files; change them through that process's own
review (its `DESIGN.md`, `reviews/`).
