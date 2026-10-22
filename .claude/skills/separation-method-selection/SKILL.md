---
name: separation-method-selection
description: Screen and rank separation methods and sequences (conventional and intensified distillation, DWC/TCD, heat-pump and membrane-assisted options) for a binary or multicomponent mixture with the Li, Somoza-Tornos and Kiss (2025) decision matrix, from retrieved property data and the screening questions Q1-Q7. Use when separation methods or a distillation sequence have to be selected or justified.
---

# Separation method selection

## Purpose and when to use

Implements Li, Somoza-Tornos & Kiss (2025), "A systematic selection and decision matrix for
energy-efficient intensified distillation technologies", CPPM 20(2): 293-307: the high-level
screening, the PI matrix with a COP estimate for HPAD/HIDiC, the azeotrope-specific methods for
binaries, and for ternaries the distillation sequence efficiency (DSE), DWC/TCD scoring and the
PI matrix per adjacent pair. Use it to screen candidates for a separation block of the
flowsheet. The result is a ranking to discuss, not a design.

## Required inputs and missing inputs

Retrieved numeric values for every component, never estimates or the functions' defaults:
normal boiling points (K), melting points (for Q1), heats of vaporisation (kJ/mol),
viscosities (mPa s), the relative volatility of each adjacent pair (from vapour pressures and
activity coefficients, never from boiling points), feed mole fractions, the operating pressure
(bar, absolute), target recovery and purity (0-1), the minimum or operating reflux ratio, and
for a ternary the middle-key fraction. If one is missing, request it before calling.

## Workflow and tools

1. Answer Q1-Q7, each with a flag and a one-sentence justification backed by numbers:
   - Q1 solidification: `has_solidification_risk`;
   - Q2 non-condensables: `has_non_condensable`;
   - Q3 thermal sensitivity at the reboiler temperature: `has_thermosensitive`;
   - Q4 lightest component above 0.80 mole fraction: `large_light_fraction` (compare the
     number exactly: 69.81 mol% is 0.6981, false);
   - Q5 heaviest component above 0.80: `large_heavy_fraction`;
   - Q6 azeotrope, that is, the relative volatility crosses 1.0 (a positive deviation alone is
     not one: methanol/water and acetone/water are zeotropic, ethanol/water is azeotropic),
     and whether it is pressure-sensitive: `azeotrope`, `pressure_sensitive_azeotrope`;
   - Q7 the number of products: 2 for the binary function, 3 or more for the other.
2. Call the function:

```python
from chemeascode.domains.process.separations.selection import (
    select_binary_separation_methods,
    select_multicomponent_separation_methods,
)

r = select_binary_separation_methods(
    component_names=[...],
    molar_fractions=[...],
    boiling_points_K=[...],
    relative_volatility=...,
    heat_of_vaporization=[...],
    viscosity=[...],
    pressure=...,
    recovery=...,
    purity=...,
    reflux_ratio=...,
    azeotrope=False,
)
r.result.ranked_methods, r.result.high_level_assessment, r.assumptions, r.errors
```

A YES to Q1, Q2, Q3, Q4, Q5 or (binary) Q6 resolves the selection in the pre-screen, and the PI
matrix is not evaluated. The binary function corrects Q4/Q5 from the mole fractions and warns
when `azeotrope` is set with a relative volatility well above 1. The multicomponent function
trusts the flags and has no azeotrope branch. There is no CLI command; the functions need only
the base dependencies.

## Validation and failure handling

- `r.errors` is set: an input was invalid; fix it and call again. Read `r.assumptions` (the
  guardrail corrections) before reporting.
- Never fabricate results or property values, and never leave the flags to the function.

## Outputs and provenance

Report the screening flags with their justification, the COP interpretation (3 or more
favourable, below 3 marginal), every method with a positive score in rank order, the excluded
methods with their reason, for a ternary the DSE result and each adjacent pair separately, and
the inputs used. Record the selected method and its basis in `DESIGN.md`; write the flowsheet
block with `process-design`.

## Required human judgment

Ask a person when Q3 is ambiguous, when the pressure sensitivity of an azeotrope cannot be
determined from data, or when a required input is missing. The choice of method is an
engineering decision.

## References

- `src/chemeascode/domains/process/separations/selection.py`: the matrices and the scoring
- `phase-calculation` (phase and azeotrope checks), `process-design`
