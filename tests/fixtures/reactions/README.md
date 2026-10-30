# Reaction fixture (synthetic)

Reaction files laid over a copy of the fixture library (`tests/fixtures/library`) by
`tests/test_reactions.py`, for `reactions.json` (`scripts/reactions.py`). The heats of reaction,
conversions, catalyst window and sources are synthetic and labelled so; none is engineering data
or taken from a source.

- `fixture-electrolysis` (public): water splitting, and hydrogen burning reversibly to water
  (a reversible variant of the same stoichiometry), with a catalyst of `catalysts.yaml`.
- `fixture-ammonia` (not public): the same water splitting written at twice the scale, ammonia
  synthesis written in both directions (one reversible reaction), a pseudo component
  without a CAS number (a reaction that does not balance), a component without a formula (a
  reaction whose element balance cannot be checked), and made-up references in the forms the
  Atlas links (a DOI of the 10.5555 test prefix, a US patent number, a URL); they cite nothing.
