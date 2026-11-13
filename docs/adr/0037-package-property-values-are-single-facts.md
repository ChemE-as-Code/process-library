# 0037. Property values computed by an open-source package are single facts with their source

- **Status:** Accepted, 2026-11-06
- **Deciders:** the owner, as the library's maintainer (recorded by an agent session)
- **Scope:** the rules on sources and licences ([ADR 0013](0013-licences-and-no-third-party-content.md),
  CONTRIBUTING.md "Sources, licences and what may not be copied", CLAUDE.md "Sources and
  licences") as they apply to property values taken from open-source packages, and the source
  register of each entry's `DESIGN.md`. ADR 0013 stands in full; this record says how one kind
  of fact is used and recorded under it.

## Context

Most engineering entries take pure-component properties from the open-source packages of core's
environment, `thermo` and `chemicals` (Caleb Bell, MIT licence; core pins thermo 0.6.1 and
chemicals 1.5.2). Core reaches them through `cheme chemistry props --source Thermo` (offline),
the stream-property calls of `cheme process props`, and the balance scripts that import them.
The publication review of [PR #411](https://github.com/ChemE-as-Code/process-library/pull/411)
counted 58 already-public entries that use thermo values.

The packages are open-source, but the values they compute are not all open data:

- thermo's default method for many compounds is **DIPPR_PERRY_8E**, a correlation whose
  coefficients thermo bundles from Perry's Chemical Engineers' Handbook, 8th ed., a licensed
  book that draws on the DIPPR 801 database. For methyl bromide it gives the heat of
  vaporisation (23.32 kJ/mol at 298 K, 23.53 at 293 K, 18.84 at 384 K) and the liquid density
  (1663.1 kg/m3) used by methylmagnesium-bromide-1 and methyltriphenylphosphonium-bromide-1, and
  for bromine the liquid density at 293 K used by phosphorus-tribromide-1.
- thermo's **VDI_PPDS** correlations take their coefficients from the VDI Heat Atlas, also a
  licensed book; thermo offers them for many compounds.
- `chemicals` bundles tables of the CRC Handbook of Chemistry and Physics (for example
  `CRC_inorganic_data`, `CRC_standard_data`, `Hvap_data_CRC`), also a licensed work.

The source registers had called such values "open data". The publication review corrected the
wording in three entries and left one question to the maintainers: **may values that a package
computes from such bundled coefficients (DIPPR_PERRY_8E, or VDI_PPDS) be published in the library at
all?** If not, every entry that uses them would have to re-source them (from the NIST WebBook,
SRD 69, PubChem/HSDB, or thermo's own estimation methods, which differ by a few per cent: 23.2 to
24.2 kJ/mol at 298 K against 23.3 for methyl bromide's heat of vaporisation; the packaged CRC
values are 22.8).

Options considered:

1. **Forbid them** and re-source every such value across the library. Large, and it replaces
   measured-correlation values by estimates or by values that are not more open.
2. **Accept them as open data.** Wrong: the package's licence covers its code, and says nothing
   about the rights in the coefficients it bundles.
3. **Accept them as single facts with their source**, as ADR 0013 already accepts a property value
   taken from a paper or a handbook, and keep the ban on copying tables. The owner's decision of
   2026-11-06.

## Decision

- **A property value that an open-source package computes from its bundled coefficients or
  tables is a fact, and may be used in a library entry**, in our own form, like any other
  property value (ADR 0013, "facts and numbers ... with their source"). This covers thermo's
  default methods such as DIPPR_PERRY_8E, its VDI_PPDS correlations (coefficients from the VDI
  Heat Atlas) in the same way, and the packaged CRC tables of `chemicals`.
- **Where the line to licensed databases runs.** A value computed from coefficients that a
  published handbook printed and an open-source package bundles (Perry's 8th ed., itself drawing
  on DIPPR 801; the VDI Heat Atlas; the CRC Handbook) is a fact from that handbook, like a value
  read from the handbook itself, not a value taken from a licensed database in ADR 0013's sense.
  A value read from DIPPR 801 itself, or from any other subscription or commercial database, is
  still not taken, even if a package bundles it.
- **Single values only.** An entry uses the values its design needs, each at the condition it
  needs (a heat of vaporisation at 298 K, a density at 293 K). **Copying whole tables or
  coefficient sets into the library stays forbidden** (ADR 0013; CLAUDE.md and CONTRIBUTING.md
  "Sources and licences"): no DIPPR or Perry coefficients, no table of CRC rows, no dump of a
  package's data file, in any file of the library.
- **The entry's source register names the source fully**: the package and its version (for
  example `thermo` 0.6.1, `chemicals` 1.5.2), the method or table (DIPPR_PERRY_8E,
  `CRC_inorganic_data`), and the underlying work the coefficients come from (Perry's Chemical
  Engineers' Handbook, 8th ed., drawing on DIPPR 801; the CRC Handbook).
- **No false claims.** The register does not call such values open data, and does not say the
  underlying work was read when only the package was queried ("not read here").
- **An open source is preferred where it is at hand** (the NIST WebBook, SRD 69; PubChem/HSDB),
  but its absence is not a reason to leave a package value out.

## Consequences

- The values already in the library stand; no entry has to re-source them. The question left
  open by PR #411 is settled, and the entries that left it to the maintainers cite this record.
- A source register row for package values records: the package and version, the method or
  table, the underlying work and that it was not read, the values used (per component, or where
  they are printed, such as `process/materials.yaml`), and the decisions that use them. Its
  access column says "open-source package queried; single values, facts only", not "open data".
- The method is not always visible: `cheme chemistry props --source Thermo` names the source
  "Thermo" but not thermo's method, so the author looks it up (thermo's `.method` of the
  property object) when it matters. Naming the method in core's output is a possible core
  follow-up.
- Older source registers that call package values "open data" (CRC or DIPPR alike) are wrong in
  wording, not in substance; they are corrected when the entry is next touched. The library test
  `tests/test_publication_policy.py` pins the narrower rule that no source register row naming
  DIPPR or Perry's calls its values open data. Update 2026-11-12 (issue #426): the older registers
  are corrected (formic-acid-1 follows, issue #433), and the test covers rows naming Yaws, CRC or
  VDI as well, and variants of the claim such as "open software data" or "open-source data".
- The rule does not open the door to licensed databases: a value from a commercial property
  database, or from ecoinvent, is still not taken (ADR 0013); the packages' bundled handbook
  coefficients are accepted only as the Decision's bullet "Where the line to licensed databases
  runs" draws it, as facts from the handbook that printed them.

## Evidence

- PR #411, publication review "Thermo's DIPPR_PERRY_8E values: wording fixed, publication question
  open (maintainer decision)".
- CONTRIBUTING.md "Sources, licences and what may not be copied" points here.
- processes/methylmagnesium-bromide-1 SRC-7, processes/sodium-azide-1 SRC-5 and
  processes/phosphorus-tribromide-1 SRC-3 record the package, version, method and underlying
  work; methyltriphenylphosphonium-bromide-1 SRC-6 follows when PR #406 has landed.
- `tests/test_publication_policy.py`: no source register row that names DIPPR, Perry's, Yaws, CRC
  or VDI calls its values open data, "open software data" or the like (Yaws, CRC, VDI and the
  variants since issue #426).
