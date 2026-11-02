# IDAES HDA tutorial: reference reproduction

Numerical reproduction of the baseline IDAES HDA tutorial (examples-pse, pinned commit in
`source.yaml`) by the cheme IDAES backend (core#104), for issue #302. Protocol: ADR 0030.

This is **not** the hda-1 design: `processes/hda-1/` is an independent concept design
(DESIGN.md D-001) and uses nothing from here. Agreement here is agreement between two models
built on the same property and reaction assumptions, not validation.

| File | What |
| --- | --- |
| `source.yaml` | pinned revision, licence, case specification and reported results (facts, own form) |
| `tolerances.yaml` | acceptance tolerances, committed before the comparison run (frozen in 1979740; its header names this ADR by its number then, 0024, now 0030) |
| `reruns/` | later runs of `case/` kept as evidence, with released core v1.4.0 and v1.4.1 (comparison.md) |
| `case/` | the minimal cheme project that restates the case (`simulator: idaes`) |
| `comparison.md` | reference vs cheme, deviations and explanations |

Run (needs core with the IDAES backend and `CHEME_IDAES_PYTHON`):

```sh
cd case
cheme process simulate --fill
```
