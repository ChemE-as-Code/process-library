# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | README.md, lca/datasets/fischer-tropsch-fuel-rwgs-co2-h2.yaml (feed:electricity uncertainty text only; no amount, gsd2 or formula changed) | Electricity cross-check restated: CO2 compressor about 1.5 MW (223 to 238 kJ/kg at 72 % polytropic, k = 1.29, intercooled to 20 to 40 degC; was about 2 MW), recycle compressor roughly 0.5 to 1 MW (not checkable from the source), total about 3.6 to 4.1 MW, 16 to 26 % below the 4.87 MW used ("close to" dropped); lower bound of the recovered utility power 4.68 -> 4.69 MW (67.1 / 0.4335 - 150.1 = 4.687); README no longer says all flows come from the simulation: burner flue gas and combustion oxygen close the element balance over the ASSUMED model fuel | audit findings: the cross-check overstated its agreement with eq. 9, a misrounded bound, and estimate flows described as simulated |
