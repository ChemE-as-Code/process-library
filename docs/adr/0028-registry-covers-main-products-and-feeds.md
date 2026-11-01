# 0028. Register every process's main product and feeds with verified identities; label functional units by product name

- **Status:** Accepted, 2026-10-31
- **Deciders:** the owner (proposed by an agent session)
- **Scope:** the chemicals registry (`chemicals/chemicals.yaml`), the processes' `chemistry`
  blocks, and the catalog build (`scripts/build_catalog.py`)

## Context

The registry held 15 entries (7 substances, 1 mixture, 7 utilities) while the 50 processes make
and use many more substances (#251). A process could list under `chemistry` only what the
registry has, so 42 processes did not list their main product and most did not list their
feeds. Their validation notes and chemistry notes said so ("The chemicals registry has no
..."), the Atlas showed those sentences, and the process graph could not link producers to
consumers (acetic-acid-1 makes what acetic-anhydride-1 uses, but neither listed it). The LCA
functional unit of the catalog showed the study's component id ("1 kg PROD", "1 kg HAC") instead
of a product name (#249).

Linking a flow to the registry has two effects in the build. In the catalog graph it only
joins processes by slug. In the LCI build, a flow with an `inventory_key` resolves its exchange
through the slug: the exchange then links to the slug's background mapping or to an Atlas
producer. For a product, the slug also names the reference product. Several processes already
state that their feeds carry no `inventory_key` for this reason (glycerol-1, hydrogen-bromide-1,
hydrogen-chloride-1, thf-1, D-013 in their DESIGN.md).

## Decision

- The registry has an entry for every main product and feed the processes name in their
  `chemistry` and LCA inventories, as far as the substance can be identified: 88 entries were
  added (103 in total). Process-specific mixtures without a defined composition (bauxite, wood
  chips, crude glycerol, raw natural gas, pyrolysis gasoline, ...) are `kind: mixture` with a
  description and no composition, as docs/registry.md, "Fuel mixtures", allows.
- Identities are verified programmatically before they go in (docs/registry.md, "Identities and
  how they are verified"): CAS <-> InChIKey and formula with the `chemicals` package, CID and
  ChEBI id against the same InChIKey with PubChem and ChEBI. A disagreement is written in the
  entry's `note`; an unverifiable id is left out. `tests/test_registry.py` repeats the
  `chemicals` package check offline and checks that identifiers are unique; CI installs
  `chemicals==1.5.2` for the tooling tests so that the check runs there too.
- Each process lists its main product (`role: main-product`) and its feeds. New feed entries
  carry no `inventory_key`, so they are not linked through their slug; their note starts with
  the inventory key. The build's existing name match still links one feed (thionyl-chloride-1's
  `feed:SULFUR`, see Consequences); that link is not yet reviewed. Main products carry their `inventory_key` unless the process states a
  reason against it (glycerol-1, natural-gas-processing-1; methanol-1 has no inventory).
- The catalog build warns for a process without a main product.
- The catalog's LCA `functional_unit` keeps `product` (the id) and adds `chemical`, `grade`,
  `product_name` (the grade's name, else the registry chemical's name) and `product_title` (the
  inventory row's title); `label` uses the product's name when the functional unit's product is
  a chemistry output with that `inventory_key`, else it keeps the id.

## Consequences

- The Atlas graph links the chains the library models (methanol -> acetic acid -> acetic
  anhydride; ammonia -> nitric acid -> sodium nitrite; chlor-alkali -> phosgene, ...), and
  chemical pages exist for the substances.
- The LCI export changes only in names and gap texts: main products' reference product names now
  start with the chemical's name; gap reasons name the chemical slug where an exchange's own name
  matches a registry slug. One link appears through the build's existing name match:
  thionyl-chloride-1's `feed:SULFUR` exchange (named "SULFUR") now links to the library's
  existing `sulfur` mapping (market for sulfur), one gap fewer. This link has not been reviewed
  for the process (DESIGN.md D-013 records feeds as unlinked); the owner either records it as
  reviewed in the process's mappings or the name match is restricted to flows with an
  `inventory_key`.
- Feeds are not yet linked in the LCI to their registry slug: linking them (and so to other Atlas
  processes or backgrounds) stays a per-process decision with its mapping review.
- For a product counted by mass of a solution or hydrate the label names the pure substance,
  not the solution, and so reads wrong as a substance basis: hydrogen peroxide 50 wt%, formalin,
  hydrobromic acid, hydroxylammonium sulfate 25.4 wt% solution (hydroxylamine-1), hydrochloric
  acid 33 wt% (hydrogen-chloride-1, labelled "hydrogen chloride"), nitric acid 60 wt%
  (nitric-acid-1), formic acid 85 wt% (formic-acid-1) and hydrazine hydrate 64 wt% N2H4
  (hydrazine-1, labelled "hydrazine", a different substance from the hydrate).
  `product_title` carries the inventory's wording. A grade per solution (`<slug>/<grade>` with
  its concentration, e.g. `nitric-acid/60wt`) would make the label exact; until then these
  eight labels are known to be inexact.
- The new substances have no standard chemical exergy yet; exergy allocation from registry data
  works only for the earlier entries.
- Process DESIGN.md and PROGRESS.md files still list the missing registry entries as open
  library items; they are records of their time and are not rewritten here.

## Evidence

- Issues #251 and #249.
- `chemicals/chemicals.yaml`, `docs/registry.md`, `scripts/build_catalog.py`
  (`_name_functional_unit`, the main-product warning), `tests/test_registry.py`
  (`test_registry_identifiers_are_unique`, `test_registry_identities_agree_with_the_chemicals_package`),
  `tests/test_build_catalog.py` (functional-unit and main-product tests).
