# 0005. Shared vocabularies: a chemicals registry with slugs and grades, and a family taxonomy mapped to ISIC/NACE

- **Status:** Accepted, 2026-10-25 (registry slugs since 2026-10-23)
- **Scope:** `chemicals/chemicals.yaml`, `taxonomy/families.yaml`, `scripts/registry.py`, their schemas

## Context

The Atlas graph links processes through the chemicals one makes and another uses. Free-text
names would never join ("oxygen", "O2", "GOX"). The LCI database, however, needs more than a
substance: an ASU makes gaseous oxygen at 30 barg and liquid oxygen, which are different
reference products with different burdens. Processes also need a classification that users and
statistics recognise.

## Decision

- **Chemicals registry** (`chemicals/chemicals.yaml`, `cheme-as-code/chemicals/v2`): every
  chemical a process names is a **slug** of the registry, with identity (CAS, InChIKey, ChEBI),
  properties only with a source, CPC/HS codes and crosswalk names. New chemicals are added in
  the same change as the process that names them.
- **Grades:** a product in a defined state and purity is a grade of its substance
  (`oxygen/gox-30barg-99.5`, `oxygen/lox`). The Atlas graph joins by substance (one oxygen node);
  the LCI export names the grade as its reference product. A flow names its grade itself
  (`chemical: oxygen/lox`) or through the registry's `flow_grades` map; a contradiction or an
  unknown grade fails the build.
- **Family taxonomy** (`taxonomy/families.yaml`): process families mapped to ISIC Rev.4 and
  NACE Rev. 2. `process.yaml` `families`, the coverage roadmap and the benchmark files use these
  slugs; a new family goes into the taxonomy and the schema enum together.
- The shared rules live in `scripts/registry.py`, used by both builders.

## Consequences

- Processes link in the Atlas without coordination beyond the registry; the registry becomes the
  product master data of the LCI database.
- `flow_grades` was chosen over a `grade:` field or a default grade per substance because the
  ASU's `process.yaml` is changed only by its own review, and a default would be wrong for
  oxygen (two ASU grades). It must be kept in agreement with the processes until they name
  their grades themselves; a stale entry is a warning.
- Every new chemical needs registry work; the registry is a shared file that concurrent changes
  can conflict on.

## Evidence

- `986803b` first registry and schema, [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `ca60886` "Registry v2 (grades, sourced properties, CPC/HS, crosswalks), family taxonomy and
  coverage roadmap" and `b533e54` review fixes, [#69](https://github.com/ChemE-as-Code/process-library/pull/69); issue #46.
- [registry.md](../registry.md) ("Why a mapping, not a field with a default"),
  `schemas/chemicals.schema.json`, `schemas/families.schema.json`, `tests/test_registry.py`.
