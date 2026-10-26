# 0015. datapackage.json documents every exported activity; the Atlas renders it without LCI logic

- **Status:** Proposed, 2026-10-26
- **Deciders:** the coordinator (for the owner's review)
- **Scope:** the LCI pipeline (`scripts/build_lci.py`, `scripts/lci_activities.py`) and its contract with the Atlas

## Context

ChemE-as-Code/website#37 asks for a documentation page per activity of the Atlas LCI database,
as ecoinvent and the EF node have: what the dataset represents, its exchanges with amounts,
units and provenance, its data quality, how it links, its review and its downloads. The issue
fixes the split: the pages are generated from `datapackage.json`, and the site stays a consumer
with no LCI logic. Until now `datapackage.json` held the processes, their datasets (review, data
quality, allocation shares, benchmarks) and a list of activity names, but not the exchanges of
the exported, allocated activity: those were only in the workbook, which the site would have to
parse and interpret (per-unit scaling, link rules, which column is a compartment).

Options: (a) the site reads the workbook; (b) a separate file per activity; (c) one
`activities` list in `datapackage.json`. (a) puts LCI logic into the site; (b) adds files the
Atlas's fail-closed public check (website `scripts/check-public.mjs`) would each have to allow;
(c) keeps one file that is already checksummed in `index.json` and checked for public processes.

## Decision

- `datapackage.json` has `activities`: one entry per activity of the workbook (datasets and
  screening proxies), sorted by code, written by `scripts/lci_activities.py` from the same
  `Activity` objects the workbook is written from, so the two cannot disagree.
- An entry carries what is per activity: identity (code, dataset UUID and version; no activity
  UUID, the library assigns none), header metadata (geography, time, technology, boundary,
  production volume, classification: the dataset's own, else ISIC from the process's families
  and CPC/HS and CAS from the chemical registry, each with its source), the allocation with this
  product's share, the exported exchanges per unit of the reference product (unit, provenance
  with core's default `assumed`, source, pedigree scores and the lognormal, background link by
  name, Atlas activity by code, elementary flows with biosphere3 UUID and compartment),
  `used_by`, `closure`, citation, downloads and `publication`.
- Markets (`markets/`, docs/markets.md) get an entry like any activity (`kind: market`): their
  suppliers, transport and losses are its exchanges, with the status and source of each, and
  `market` repeats the datapackage's `markets` entry. An input linked to a market names the
  market's code (`atlas_alternative`) and the plant behind it (`atlas_plant`). A market is
  `public` when all its suppliers are.
- `downloads` names, per database file, how to find the activity in it: the code in the workbook
  and the multifunctional JSON (the dataset code where the dataset has several products, which
  that file keeps unallocated), the process id and zip member in the openLCA JSON-LD package.
- Dataset-level facts stay in `processes[].datasets[]` (review, data quality, data status,
  benchmarks, property checks); an entry names its dataset, and the site joins by id.
- `closure` is the `balance` core writes into `lca/manifest.json` (core#174) for the plant's
  generated dataset, else `status: not-assessed` with the reason. `citation.doi` is null until a
  release is deposited (ADR 0012). Per-dataset files do not exist.
- No entry holds an impact value: the LCI has no characterisation factors. A `--public` build
  holds public processes only, so every entry, link and back-link names a public process.

## Consequences

- The Atlas renders `/lci/<code>/` pages and per-activity JSON-LD from one file it already
  publishes; new fields reach the pages without site changes to LCI rules.
- `datapackage.json` grows with the exchanges (about 35 kB per ASU-1 activity as written, indented).
- Open: an activity UUID (core#179 gives the dataset one), per-dataset files in each format
  (#51), the closure once core#174 is in, the DOI once a release is deposited (#50), and the
  impact deltas of the change report (#50) stay outside `activities`.

## Evidence

`scripts/lci_activities.py`, `tests/test_lci_activities.py` (entries match the workbook, links
and back-links by code, public build withholds unpublished processes, closure from the manifest,
no impact keys); ChemE-as-Code/website#37.
