# Verification of the 200-day baseline

The default BDF run uses relative tolerance 1e-6, absolute tolerance 1e-8 and a maximum time step of one day. At the same settings the default run reproduced the final states of the EXPOsan 1.5.3 ASM2d CSTR factory, with reconstructed effluent differences within 1.8e-15 in the reported units. This comparison concerns software reproduction.

| Final effluent | Value | Unit |
| --- | ---: | --- |
| Flow | 18,061 | m³/day |
| COD | 44.91763 | mg COD/L |
| Total nitrogen | 15.67771 | mg N/L |
| Total phosphorus | 7.39093 | mg P/L |
| Suspended solids | 12.88570 | mg TSS/L |
| Ammonium nitrogen | 3.00813 | mg N/L |
| Orthophosphate phosphorus | 6.92253 | mg P/L |

On Windows and Ubuntu, `cheme process simulate --fill` completed 200 days with QSDsan and EXPOsan 1.5.3. All 84 final values (seven quantities across twelve streams) matched the saved baseline within a relative tolerance of 1e-6 and an absolute tolerance of 1e-8. The Ubuntu solver recorded 827 time points, so the cross-platform check compared the final outputs.

A repeat from a clean copy of the staged example on Windows with core commit `5437b17` reproduced all 170 model states at all 804 recorded time points exactly. Of the 84 derived stream values, 70 were identical and 14 differed only at floating-point precision. In a separate check of the native Stream table, all 84 values matched the saved stream data at the displayed precision with the correct unit. Selecting the effluent stream on the PFD displayed the same seven quantities.

A successful run checks the requested duration, finite states, nonnegativity within tolerance, external water balance, stream mapping, biological volume and TN/TP component sums. The final 20-day state-span screen is a local diagnostic.

## Review checks at core commit `5437b17`

The 22 example tests passed on both Windows and Ubuntu. After a successful Windows fill, a second 200-day run with `--check` preserved the contents of every file under `process/`. Changing the influent flow in the input alone marked the saved values stale. The worker refused the inconsistent fill and the earlier flowsheet, run record and evidence retained their file hashes.

With the same staged example on Ubuntu, a browser check compared 12 rows and seven quantities in the native Stream table against the new run's CSV and checked all seven quantities on the effluent stream's PFD panel. The saved HTML report's links and image resolved within its own run folder.

## Outstanding numerical questions

Previous tighter BDF and LSODA runs were interrupted after extended runtimes. A Radau run failed at about day 0.1413. Solver and initialization sensitivity, whole-system nitrogen and phosphorus balances including accumulation, sludge and gas, and steady-state robustness remain open. No plant data were used. Chemical dosing, sludge treatment and blower energy fall outside this case.
