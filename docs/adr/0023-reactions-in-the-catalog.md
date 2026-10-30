# 0023. List the processes' reactions in the catalog as reactions.json, each reaction once

- **Status:** Proposed, 2026-10-30
- **Deciders:** the owner (proposed by an agent session)
- **Scope:** the Atlas catalog (`scripts/build_catalog.py`, `scripts/reactions.py`) and its
  publication rules

## Context

43 of the 50 processes carry their reactions (`process/reactions.yaml`, core's
`cheme/reactions/v1`) and 9 their catalysts (`process/catalysts.yaml`), checked by `cheme
validate` in each folder. The Atlas shows none of it. Many processes state the same reaction
(methane combustion, hydrogen combustion, water-gas shift), each with its own id, coefficients
and numbers. The toolkit's reaction library (`cheme chemistry library`) holds 23 entries with
generic sources and assumed catalyst windows; listing it beside the reviewed processes would
present template data as curated, so the Atlas needs the processes' own reactions instead, with
at most a pointer to a matching template. Options considered: a separate builder script, run
by the website after the catalog; or part of the catalog build, like `routes.json`. The catalog
build already applies the publication rules and replaces its output folder, so a separate
script would repeat the publication filter and depend on running in the right order.

## Decision

- `build_catalog.py` writes `reactions.json` (`cheme-as-code/catalog/v1`, the build `mode` and
  library commit) from the catalogued processes; `scripts/reactions.py` holds the rules.
- The same reaction is listed once: the same species, a species being its component's CAS
  number (a component without one stays its process's own), with the same coefficients up to a
  common factor; direction counts only for an irreversible reaction. A reversible and an
  irreversible statement of one stoichiometry are two reactions, linked as `variants`.
- Each process's statement is kept as an occurrence with what its files say (id, equation,
  conversion, heat of reaction and its value for the merged equation, catalyst with its
  catalysts.yaml entry, sources) and the process's maturity and review status. Nothing is
  estimated.
- Each occurrence carries its element balance, by core's rule (`cheme.reaction-element-balance`:
  atoms per element of the process's own stoichiometry and formulas, tolerance 1e-9):
  `balanced`, `unbalanced` with the change per element, or `not-checkable` with each component
  it could not count and why (not in materials.yaml, no formula, a formula the parser does not
  read, materials.yaml withheld). The parser is core's `parse_formula` when core is importable,
  else a copy of it, tested against core where core is installed. A reaction sums its
  processes (a process balances only when each of its occurrences does; `balanced` only when
  every process does); the Atlas never shows a balance it did not check. A reaction also says
  whether any occurrence cites a source (`has_sources`, a non-blank one); collecting and
  linking the sources themselves is the website's, from the occurrences' fields.
- A species links to the registry chemical with its CAS number, else to none. Its formula and
  name are the registry's, else the ones most processes write (a process's note in brackets
  dropped); each occurrence keeps its process's own names.
- The slug is made from the merged equation with each formula in one order (Hill for organic
  formulas, else IUPAC's element sequence), so `Ca(OH)2` and `CaH2O2` give the same slug and
  it does not depend on which processes are built; a hash is added when too long or shared by
  isomers.
- A public build lists the published processes only, and skips a file their
  `publication.exclude` covers, matched as core's `export-static --exclude` matches it
  (`publication.excluded`; case ignored, so it withholds whenever an export could).
- With `--cheme <command>`, a reaction names the templates of core's reaction library with its
  stoichiometry (same direction unless one is reversible); without it `templates` is null.

## Consequences

- The Atlas can show a reactions index and a page per reaction from one file, with the
  processes' own sources, without reaction logic of its own.
- A reaction's slug changes when its merged equation changes, or when an isomeric reaction
  with the same formulas arrives (both then get a hash): links to it break then.
- Merging needs CAS numbers: two processes stating the same reaction with a component that
  lacks one show it twice. Few registry chemicals have a CAS number yet, so most species link
  to no chemical page.
- Template matches depend on the core version the build ran with; CI builds without them.
- The element balance repeats a check `cheme check` already runs in CI, so in the library it is
  `balanced` everywhere (277 of 277 occurrences on 2026-10-30); it is published so the page can
  say so. The copy of core's parser must follow core: the comparison tests fail when they part.

## Evidence

- `scripts/reactions.py`, `scripts/build_catalog.py` (`--cheme`), REFERENCE.md ("Reactions").
- Tests: `tests/test_reactions.py`, fixture `tests/fixtures/reactions/`.
