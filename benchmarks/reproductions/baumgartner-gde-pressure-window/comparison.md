# Comparison: GDE pressure-window reproduction (Baumgartner et al. 2022)

- **Reference:** `source.yaml`. The paper (ACS Sustainable Chem. Eng. 10 (14), 4683-4693,
  CC BY 4.0) and its two supporting-information files, each verified by sha256.
- **Data:** the supporting-information spreadsheet is the most primary data published. It
  tabulates one breakthrough pressure per sample and transition, plus averaged process values of
  each electrolysis run. No pressure time series and no data repository exist, so the
  reproduction starts from tabulated values, not raw data.
- **Tolerances:** `tolerances.yaml`, frozen in commit 39a382c. That commit came after the source
  record (5a4eb49) and before any comparison run. Its header lists what had been seen before the
  freeze: the full paper text, so every published number compared here, and a hand conversion
  of 40, 50 and 80 mbar to heights.
- **Runs:** `uv run --isolated benchmarks/reproductions/baumgartner-gde-pressure-window/reproduce.py`,
  2026-11-04, Python 3.12.15, numpy 2.2.6, openpyxl 3.1.5, matplotlib 3.10.3.
  - `reruns/2026-11-04-run.json` is the first comparison run. Its `dirty: true` is because the
    script was not yet committed. The exact script of that run is in no commit: the script
    committed with it in 9421aac already had the changed figure layout and the informational
    block (below), so checking out 9421aac does not reproduce this record byte for byte.
  - `reruns/2026-11-04-run-2.json` was run from an empty download cache and an empty uv cache,
    with the script as committed in fad8fed. Between the two runs, three things changed: the
    figure layout, an informational block (operating rows outside the 200 mA/cm2 scope of K2)
    and a download retry. Every frozen check is identical in the two records. This record's
    `dirty: true` is because `figures/`, the output of the first run, was not yet committed.
    It is the record a commit reproduces. A later commit made the download retry more robust
    (dropped connections, a non-zip answer, a missing member); it changes no computed number.
  - One earlier attempt stopped on an HTTP 500 from Europe PMC before any comparison. That
    failure is the reason for the retry.
- **Order of evidence:** `git log -- benchmarks/reproductions/baumgartner-gde-pressure-window/`
  shows the source record, then the tolerances, then the script and results. The records cannot
  prove that no uncommitted run happened before the freeze. That claim rests on the commit order
  and on this account.

## Result

| Check | Kind | Result under the frozen rule |
| --- | --- | --- |
| R1 | reproduction: window per GDE | **FAIL**: all 7 GDE windows match the sheet and all 4 match the text. The uncoated-GDL consistency sub-check fails for SGL 39BC: the sheet's 67 mbar is Sample 2 of SI Table S3, and the frozen check compared it against the table's mean of 62 mbar |
| R2 | reproduction: window spread | **pass**: 14.14 mbar against the text's 14 mbar and the sheet's 14.14 mbar (141.42 mbar for H23C6) |
| R3 | reproduction: the paper's heights | **pass** on the water basis: 40.9 / 81.7 / 51.1 cm against 41 / 81 / 51 cm |
| K1 | claim classification | range supported (6 of 6). C1 (below 51 cm) **contradicted** for 3 of 5 materials. C2 (H23C6 above 1 m) supported. C3 (H23C6 above 200 cm) supported at nominal values only |
| K2 | consistency of operating points | none outside: 3 inside and 3 at the edge, all near the gas-breakthrough end of the window |

The script exits 1 because R1 fails. The spreadsheet gives one of the two SGL 39BC samples,
while the frozen check compared it against the mean in SI Table S3. Both published values are
consistent with each other, so this is neither an error in the reproduction nor a data error in
the source (see below). Reproduction,
claim checks and consistency are reported separately and not pooled (tolerances.yaml
pass_rule).

### R1: flow-by window per coated GDE

Sign convention as in the paper: dp = p_L − p_G. Breakthrough pressures come from sheet deltaP,
columns H and I. The window is dp* = dp_L* − dp_G*.

| GDE | dp_G* / mbar | dp_L* / mbar | dp* ours | sheet (col. L) | text | status |
| --- | --- | --- | --- | --- | --- | --- |
| TGP-H-060 | −2 | 56 | 58 | 58 | 58 | pass |
| TGP-H-090 | −1 | 71 | 72 | 72 | – | pass |
| TGP-H-120 | −17 | 61 | 78 | 78 | 78 | pass |
| SGL 22BB | −8 | 41 | 49 | 49 | 49 | pass |
| SGL 39BC | −2 | 69 | 71 | 71 | – | pass |
| LT1400W | −3 | 38 | 41 | 41 | 41 | pass |
| H23C6 | −18 | 370 | 388 | 388 | – | pass |

**Deviations and explanations**

1. **SGL 39BC, uncoated GDL: 67 mbar against 62 mbar.** SI Table S3 lists two samples (57 and
   67 mbar) and their mean of 62 mbar. The spreadsheet's uncoated column gives 67 mbar, the
   second sample. The other six materials agree exactly. This sub-check was frozen as part of
   R1 ("also_checked", same rule), so R1 is recorded as FAIL. We do not reclassify it after the
   run. The coated-GDE windows, which carry the height argument, are unaffected. The two values
   are the paper's only replicate, and their 7 mbar sample standard deviation agrees with the
   10 mbar error the authors assume for every breakthrough pressure.
2. **The GDE windows reproduce exactly.** The window column is typed, not computed, so R1 does
   test the authors' arithmetic, and it holds. The windows' physical resolution is coarser:
   the liquid backpressure was raised in 10 mbar steps (SI section 6), and every value rests on
   one sample.
3. **Coated GDEs have a slightly negative gas-breakthrough pressure** (−1 to −18 mbar). The
   catalyst layer moves the whole window down, which the paper attributes to the more
   hydrophilic catalyst layer, without changing its width much.

### R2: window spread

sqrt(10² + 10²) = 14.14 mbar for every GDE but H23C6, and sqrt(100² + 100²) = 141.42 mbar for
H23C6. Both match the sheet's formula column and the text's ±14 mbar. These spreads are the
authors' estimates from two literature studies, not replicate spreads of these samples.

### R3: the paper's height conversions

h = dp* / (rho g), g = 9.80665 m/s².

| | window | published | ours, water 998.2 kg/m³ | deviation | ours, 1 M KHCO3 1065 kg/m³ (ASSUMED) |
| --- | --- | --- | --- | --- | --- |
| H1 | 40 mbar | 41 cm | 40.86 cm | −0.14 | 38.30 cm |
| H2 | 80 mbar | 81 cm | 81.72 cm | +0.72 | 76.60 cm |
| H3 | 50 mbar | 51 cm | 51.08 cm | +0.08 | 47.87 cm |

The paper's heights use the density of water. The windows were measured with 1 M KHCO3, which
is about 6.7 % denser (ASSUMED 1065 kg/m³, range 1055 to 1075, tolerances.yaml constants), so
the heights of the measured system are about 6 % lower: 38 to 77 cm instead of 41 to 81 cm, and
48 cm instead of 51 cm. No single convention reproduces all three published heights on the
water basis: H1 (40.86 cm, published 41) needs rounding, and H2 (81.72 cm, published 81) needs
truncation. The same holds for 1000 kg/m³ with g = 9.81 m/s². Rounding fits all three only if
rho g lies between about 9.82 and 9.88 kN/m³, above water's 9.79 kN/m³. The paper's exact
density basis and rounding therefore cannot be identified from the three values. The tolerance
allows either convention. As the tolerances header says, R3 is not blind: only the
water basis matched in the hand check before the freeze.

### h_max per GDE (reported, no rule)

The interval uses dp* ± 2 s together with the density range 1055 to 1075 kg/m³ (lower bound at
the higher density, upper bound at the lower).

| GDE | dp* / mbar | h_max water / cm | h_max 1 M KHCO3 / cm | interval / cm | FE_CO at 200 mA/cm2 (sheet) |
| --- | --- | --- | --- | --- | --- |
| TGP-H-060 | 58 | 59.3 | 55.5 | 28.2 to 83.4 | 81.0 % |
| TGP-H-090 | 72 | 73.6 | 68.9 | 41.5 to 96.9 | 71.0 % |
| TGP-H-120 | 78 | 79.7 | 74.7 | 47.2 to 102.7 | 46.5 % |
| SGL 22BB | 49 | 50.1 | 46.9 | 19.7 to 74.7 | 79.4 % |
| SGL 39BC | 71 | 72.5 | 68.0 | 40.5 to 96.0 | 75.0 % |
| LT1400W | 41 | 41.9 | 39.3 | 12.1 to 67.0 | 83.5 % |
| H23C6 | 388 | 396.4 | 371.5 | 99.7 to 648.4 | – (no 200 mA/cm2 run) |

Plot: `figures/h-max-per-gde.svg`. The interval is wide: ±2 s is ±28 mbar on windows of 41 to
78 mbar. It is also an upper bound for operation, for three reasons. The windows were measured at
open circuit, and the paper expects electrowetting to narrow them under current. A real set
point needs margin for pressure control, and the operating differential pressures in K2
scattered by 3 to 6 mbar (one standard deviation) in the lab cell. And friction adds to the
gradient when the catholyte flows upward (see below).

### K1: the paper's height claims

- **Range "40 to 80 mbar for most commercial materials": supported.** All six GDEs with MPL
  cracks lie between 41 and 78 mbar.
- **C1 "below 51 cm for every material with FE_CO above 50 %": contradicted on the nominal
  values.** Five GDEs exceed 50 % at 200 mA/cm2 in the sheet: TGP-H-060, TGP-H-090, SGL 22BB,
  SGL 39BC and LT1400W. Three of them exceed 51.5 cm on the paper's own water basis:
  - TGP-H-060: 59.3 cm;
  - TGP-H-090: 73.6 cm;
  - SGL 39BC: 72.5 cm.

  They still exceed it on the 1 M KHCO3 basis: 55.5, 68.9 and 68.0 cm. The claim holds for
  LT1400W (41.9 cm) and SGL 22BB (50.1 cm). Those are the materials the paper discusses as the
  best for mass transfer, and the statement "these same materials exhibited the lowest pressure
  window, below 50 mbar" fits them. It does not fit the whole set "above 50 %". Each of the
  three intervals includes 51 cm, so the data cannot exclude the claim within the authors'
  error. As a statement about the measured values, though, it is too strong. The sheet's
  efficiencies agree with the four in the text: TGP-H-060 81 %, TGP-H-090 71 %, TGP-H-120
  46.5 % (text 46 %) and SGL 39BC 75 %.
- **C2 "H23C6 allows cells taller than 1 m": supported.** 396 cm nominal, and 107 cm on the water
  basis even at dp* − 2 s.
- **C3 "above 200 cm": supported at nominal values only.** At dp* − 2 s it drops to 107 cm. The
  ±100 mbar error assumed for H23C6 dominates.

### K2: operating differential pressure against the open-circuit window

The sheet records gas minus liquid (FE, cell A8), so dp_op is the negative of column I.

| GDE | dp_op / mbar (sd) | window / mbar | class | liquid into gas outlet / mL min-1 | gas into liquid outlet |
| --- | --- | --- | --- | --- | --- |
| TGP-H-060 | −0.8 (5.0) | −2 to 56 | inside | 0.044 | 0 |
| TGP-H-090 | −1.4 (3.5) | −1 to 71 | edge, 0.4 below | 0.002 | 0 |
| TGP-H-120 | −5.5 (3.3) | −17 to 61 | inside | 0.003 | 0 |
| SGL 22BB | −8.5 (4.4) | −8 to 41 | edge, 0.5 below | 0 | 0 |
| SGL 39BC | −11.1 (6.0) | −2 to 69 | edge, 9.1 below | 0.002 | 0 |
| LT1400W | −0.4 (3.2) | −3 to 38 | inside | 0.002 | 0 |

Every 200 mA/cm2 run sat near the gas-breakthrough end of the window. Five of the six were
within one 10 mbar backpressure step of dp_G* (0.4 to 9.1 mbar from it). TGP-H-120 sat
11.5 mbar above dp_G*, inside the window. None recorded gas in the liquid outlet. This is consistent with the
open-circuit window: no run is outside it by more than the measurement step. It also shows the
authors' set point, just above gas breakthrough. In a tall cell that set point, applied at the
top, gives the full window as height (the plot below). The recorded liquid-into-gas flows of up
to 0.04 mL/min are small but not zero, even in flow-by.

**Informational, outside the frozen scope:** H23C6 has only a 100 mA/cm2 row. For H23C6 the
authors used a separate sample for each experiment (SI section 6), so this run and the window
measurement (−18 to 370 mbar) are on different samples. The operating dp was −64 mbar. That is
46 mbar below the window's gas-breakthrough pressure, which is within the ±100 mbar error the
authors assume for H23C6 and so not significant on its own. Yet liquid entered the gas outlet at
1.27 mL/min. For liquid to enter at dp = −64 mbar, the liquid-breakthrough pressure must have
fallen from 370 mbar to −64 mbar or lower, a drop of at least 434 mbar. That is more than three
times the 141 mbar spread of the window, so it is not explained by sample-to-sample variation
within the stated error. The electrode flooded under current at a far lower liquid pressure than
its open-circuit window allows. This matches the paper's report that the electrode lost its
hydrophobicity during electrolysis. It is the strongest sign in the data that C2 and C3 hold
only at open circuit.

## Pressure vs elevation: where the hydrostatic bound applies

`figures/pressure-vs-elevation.svg` shows SGL 39BC (window −2 to 69 mbar, FE_CO 75 %, the
material of the paper's stability test) in a 1 m tall flow-by electrode. The gas is at 345 mbar
gauge, the lab check-valve pressure, and is uniform. The liquid is 1 M KHCO3 at 1065 kg/m³. Its
pressure is set so that the top of the electrode sits exactly at gas breakthrough, dp = dp_G*,
which is the most favourable set point. Going down, the liquid pressure rises by rho g h. The
electrode stays in flow-by from the top down to h_max = 68 cm (dotted lines: 40 to 96 cm, the
interval), and the bottom 32 cm floods. Any other set point shortens the band. Moving it up
narrows the band from below, and moving it down causes gas breakthrough at the top.

The bound h_max = dp* / (rho g) holds when:

1. **The liquid is stagnant or slow, and friction along the channel is small against rho g h.**
   Laminar flow in a rectangular duct gives the frictional gradient (fRe) mu u / (2 Dh²), with
   the Shah and London fRe and mu 1.1 mPa s (ASSUMED). The ratio r is the frictional gradient
   over rho g = 10.4 kPa/m:

   | case | u | Re | friction / Pa m-1 | r |
   | --- | --- | --- | --- | --- |
   | lab cell, 100 mL/min, 30 mm × 3.5 mm (gap ASSUMED) | 15.9 mm/s | 96 | 18.5 | 1.8e-3 |
   | 1 m channel, 2 mm gap | 0.01 / 0.03 / 0.1 m/s | 39 / 116 / 386 | 33 / 99 / 330 | 3.2e-3 / 9.5e-3 / 3.2e-2 |
   | 1 m channel, 5 mm gap | 0.01 / 0.03 / 0.1 m/s | 96 / 289 / 963 | 5 / 16 / 53 | 5.1e-4 / 1.5e-3 / 5.1e-3 |

   Friction is three orders of magnitude below hydrostatics in the lab cell, and at most about
   3 % for a 2 mm gap at 0.1 m/s. With upward catholyte flow, as in the lab cell, friction
   lowers the pressure in the flow direction just as gravity does. The usable height then
   becomes dp* / (rho g (1 + r)), at most about 3 % less here. A narrower gap or a faster flow
   makes friction matter (r scales with u / gap²), and so does turbulence (Re above about 2000).
   Inlet and outlet manifolds and the porous-electrode boundary are not included.
2. **The gas pressure is uniform.** The gas hydrostatic term is about 0.2 mbar per metre for
   CO2, and the frictional drop of the gas channel is small at lab flows. A long serpentine or a
   high gas flow breaks this, and the gas-side profile then has to be added.
3. **The process is isothermal and the liquid composition uniform**, so density and surface
   tension are constant along the height.
4. **There are no gas bubbles in the catholyte.** Bubbles, from H2 evolution or gas breakthrough,
   lower the mixture density, which lengthens the band, but they make the profile depend on
   current and position.
5. **The window is the same everywhere.** These are single-sample, open-circuit values with a
   10 mbar step. Local variation of the material, and electrowetting under current, narrow it
   (see K2, H23C6).

In the lab cell, the exposed electrode is 22 mm tall, so the hydrostatic difference across it is
only 2.3 mbar, below the 10 mbar step. The measured breakthrough pressures are therefore
effectively point values, and the height argument is an extrapolation from them. Whether the
local dp stays inside the window along a tall channel with flow is the question scoped in
`scoping.md`.

## Verdict

The pressure windows of all seven GDEs and their stated spread are reproduced exactly from the
tabulated breakthrough pressures. The paper's height conversions are reproduced on a water
density basis. With the density of the 1 M KHCO3 actually used, every height is about 6 % lower.

R1 is recorded as FAIL under the frozen rule because of the uncoated SGL 39BC sub-check. The
spreadsheet carries Sample 2 of SI Table S3 (67 mbar), and the frozen check compared it against
the table's mean row (62 mbar). Table S3 lists 67 mbar too, so the two published copies do not
contradict each other, and this is not a data error in the source.

One published statement does not hold as written: "below 51 cm for every material above 50 %
FE_CO" is contradicted by three of five materials on nominal values, though not beyond the
authors' error.

The paper's main conclusion, that commercial cracked-MPL GDEs limit flow-by cells to well below
1 m, is unaffected: the largest nominal h_max among them is 80 cm on the water basis and 75 cm on
the KHCO3 basis.
