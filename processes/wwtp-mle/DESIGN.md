# MLE waterline design basis

## D-001. Use a published software example for the concept flowsheet

The baseline uses the EXPOsan 1.5.3 ASM1 CSTR configuration at 20 °C and
constant 18,446 m³/day influent. Five biological tanks provide 5,999 m³.
The model returns mixed liquor from the final aerobic tank to the first anoxic
tank. The clarifier sends RAS to the first anoxic tank and WAS out of the
waterline. Internal recycle, RAS and WAS are 55,338, 18,446 and 385 m³/day.

A2/O is an alternative when biological phosphorus removal is part of the
design objective. The library examples have different models and inputs.
A process comparison requires matched conditions.

The baseline is a software example, not plant measurements. The generic
diagram symbols represent calculation units at concept stage. Wet-weather
capacity, oxygen-transfer equipment, whole-system nitrogen balance and site
performance require separate evidence.

## D-002. Keep dynamic solver completion separate from steady-state assessment

The worker publishes a final snapshot after integrating through day 200.
The shared worker result records steady state as not evaluated. The underlying
ASM1 example exports flow, COD, TN, TSS and ammonium nitrogen. TP and
orthophosphate are outside this baseline's state representation.
