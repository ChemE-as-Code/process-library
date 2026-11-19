# Design decisions

The EXPOsan 1.5.3 ASM2d CSTR configuration supplies a reproducible teaching case. The design basis is 18,446 m³/day at 15 °C, with 2,000 m³ anaerobic volume, 2,000 m³ anoxic volume and 3,999 m³ aerobic volume. Each aerated tank uses the specified oxygen transfer coefficient. The ten-layer secondary clarifier separates solids. It has no biological reactions.

The example owns the process inputs, worker, model construction and saved results. ChemE-as-Code core owns command dispatch, schema validation and presentation of the wastewater quantities in its native Stream table. The worker records the COD, nitrogen and phosphorus measurement bases as well as the units. Gas, solids and accumulation would also have to be accounted for to establish whole-system elemental balances.

The default run integrates 200 days. All new runs retain their own input, source and numerical evidence. The case has concept maturity and uses a constant influent. See [verification](VERIFICATION.md) for the numerical limits and [NOTICE](NOTICE.md) for source attribution.
