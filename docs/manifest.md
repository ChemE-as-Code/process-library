# Process manifest

`process.yaml` is the Atlas contract of a process folder: what the Atlas needs to list, find
and link it. A cheme-as-code engineering project in the same folder keeps `plant.yaml` as its
engineering manifest; the catalog builder derives sheets, layout and LCA results from it, so
`process.yaml` holds only what cannot be derived.

## The template

A new process starts from `templates/process/` ([Contributing](contributing.md)):

<!-- include-code: templates/process/process.yaml yaml -->

## Schemas

The library's files are checked against JSON Schemas in `schemas/`. The reference pages are
generated from them, one per schema:

<!-- schema-list -->
