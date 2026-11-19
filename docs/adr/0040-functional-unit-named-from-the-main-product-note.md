# 0040. Name the functional unit from a main product without an inventory key by its note

- **Status:** Proposed, 2026-11-19
- **Deciders:** the owner (proposed by an agent session)
- **Scope:** the catalog build (`scripts/build_catalog.py`); partly supersedes the label rule of
  [ADR 0028](0028-registry-covers-main-products-and-feeds.md)

## Context

ADR 0028 labels the catalog's LCA functional unit with the product's registry name. The label
uses the name only when a chemistry output has `inventory_key: product:<functional unit
product>`; otherwise it keeps the component id. ADR 0028 also lets a process leave a main
product without its `inventory_key` when it gives a reason: in the LCI build an inventory key
links the exchange to the slug's background mapping or to an Atlas producer. Such a flow's note
starts with the inventory key instead.

After ADR 0028, three of the library's 67 LCA studies still showed an id (#249):
glycerol-1 "1 kg GLYC", natural-gas-processing-1 "1 kg SALESGAS" (both give their reason in
`process.yaml`) and lng-terminal-1 "1000 kg SHIP". Each one's main product has no
`inventory_key`, and its note starts with `product:<id>`.

The options were:

- Add the `inventory_key`. This changes the LCI linking of the process, a per-process decision
  with its mapping review (ADR 0028). It is not a fix for a catalog label.
- Add a schema field that names the functional unit's flow. That would be a second way to say
  what the note convention already says.
- Take the only main product. This is wrong when the functional unit is a different output.
- Read the note convention of ADR 0028, and only for the main product.

## Decision

- The catalog takes the functional unit's product from the chemistry output whose
  `inventory_key` is `product:<id>`, as before. If there is none, it takes the `main-product`
  output that has no `inventory_key` and whose note starts with `product:<id>`, followed by a
  character that cannot continue the id (not a word character or `-`). Leading spaces of the
  note are ignored.
- A key that appears later in the note, a co-product, or a longer id (`product:<id>X`) does not
  match, and the label keeps the id as before.
- This changes only the catalog label and the `chemical`, `grade` and `product_name` fields of
  the catalog's `functional_unit`. The LCI build, which reads `inventory_key` only, is unchanged.
- `scripts/build_catalog.py` (`_functional_unit_flow`) holds the rule.

## Consequences

- Every LCA study of the library now resolves its product: glycerol-1 "1 kg glycerol",
  lng-terminal-1 "1000 kg liquefied natural gas (LNG)", natural-gas-processing-1 "1 kg methane".
  `tests/test_build_catalog.py` checks every study of the library, so a new process whose
  functional unit names no chemistry output fails the tooling tests.
- natural-gas-processing-1 labels its sales gas "methane", the chemical its chemistry block
  takes it as. Like the solutions listed in ADR 0028, this label is inexact as a substance
  basis. `product_title` ("Sales gas to transmission pipeline ...") carries the inventory's
  wording. A registry entry or grade for pipeline sales gas would make it exact.
- The note's opening words now carry meaning for the catalog. A process that rewrites the note
  of such a flow and drops the key from its start loses the name, and the library-wide test
  reports it.

## Evidence

- Issue #249; ADR 0028.
- `scripts/build_catalog.py` (`_functional_unit_flow`, `_name_functional_unit`).
- `tests/test_build_catalog.py`
  (`test_functional_unit_of_a_main_product_without_inventory_key_is_named_from_its_note`,
  `test_functional_unit_note_match_is_strict`,
  `test_every_library_functional_unit_names_a_chemistry_output`).
