---
name: phase-calculation
description: Identify the phases of a pure component or mixture with a flash at given temperature, pressure and composition (vapour, liquid, liquid-liquid, vapour-liquid, vapour-liquid-liquid; no solids), through thermo with an equation of state or an activity-coefficient model. Use when phase identification or a flash is needed for a stream.
---

# Phase calculation

## Purpose and when to use

Runs a flash through thermo and reports the number of phases, their fractions and
compositions. Use it to identify the phase of a stream or mixture. It is a calculation without a
stated application range: stream properties written to `process/flowsheet.yaml` come from
`plantcode process props` (see `process-design`), which uses one validated method.

## Required inputs and missing inputs

- A thermodynamic model that has been recommended (`thermodynamic-model-selection`) or given.
  Do not pick one yourself.
- Components (names or CAS numbers), the temperature and the absolute pressure with units, and
  the overall mole fractions for a mixture.
- `allow_two_liquids`: set it when liquid-liquid separation is expected, as a stated assumption.

If the temperature, pressure, composition or model is missing, ask for it.

## Workflow and tools

```python
from plantcode.domains.process.thermodynamics.phase import phase_determination

result = phase_determination(
    components=["ethanol", "water"],
    overall_composition=[0.25, 0.75],
    temperature_value=70,
    temperature_unit="°C",
    pressure_value=1,
    pressure_unit="bar(a)",
    thermodynamic_model={"liquid_phase_model": "NRTL", "vapor_phase_model": "ideal_gas"},
    allow_two_liquids=False,
)
```

Models: `{"eos_model": "Peng-Robinson" | "Redlich-Kwong" | "Redlich-Kwong-Soave"}`, or
`{"liquid_phase_model": "NRTL" | "Wilson" | "UNIFAC", "vapor_phase_model": <an EOS> |
"ideal_gas"}`. The names are exact and case-sensitive. Needs the `props` extra
(`pip install 'plantcode[props]'`). There is no CLI command.

## Validation and failure handling

- `ValueError` "Invalid thermodynamic model input": compare the names with the values above and
  call again.
- The recommended model is not available: report it; use a similar one only with approval.
- A gauge pressure is refused, because no ambient pressure is known: give it as absolute.
- Check `flash_convergence_error` before using the result.

## Outputs and provenance

`FlashCalculationResult`: `temperature_K`, `pressure_Pa`, `gas_count`, `liquid_count`, `betas`,
`gas_composition`, `liquid_compositions`, `component_cas_numbers`, the inputs
(`provided_facts`) and `source` (thermo). Report the model and the assumptions with the result.

## Required human judgment

An engineer reviews the model choice and `allow_two_liquids`. A result near a phase boundary
needs confirmation from data.

## References

- `thermodynamic-model-selection`, `process-design`
- Interaction parameters: thermo's ChemSep databases and
  `src/plantcode/domains/process/thermodynamics/data/chemsep/` (SRK, Artistic License 2.0)
