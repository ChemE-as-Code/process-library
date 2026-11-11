# Scoping: an optional spatial solver for the flow-by pressure profile

Status: **scoped, not implemented** (issue #332, third task). This page proposes a model of the
cell interior: one catholyte channel and the gas channel on either side of one gas diffusion
electrode. It has nothing to do with the 3D plant layout (`processes/<id>/layout/`, `cheme layout`).
It would not place equipment, route pipes or feed a process folder.

## The question

> In a vertical flow-by cell with an electrode H tall, a catholyte gap b and a catholyte flow Q,
> does the local differential pressure dp(z) = p_L(z) − p_G(z) along the electrode face stay
> inside the measured window [dp_G*, dp_L*] of the chosen GDE? If not, what fraction of the
> electrode area lies outside it, and at which set point of the liquid outlet pressure is that
> fraction smallest?

The reference case is SGL 39BC (window −2 to 69 mbar at open circuit), H = 1.0 m, b = 2 and 5 mm,
and mean velocities 0.01 to 0.1 m/s. These are the cases of the frictional check in
`comparison.md`. The answer is a profile dp(z), not a single number. It shows where a tall cell
floods first and how much margin the set point leaves.

## Whether a spatial solver is needed

For fully developed laminar flow in a straight channel, a one-dimensional estimate already
answers the question: dp(z) = dp_top + (rho g + friction gradient)(H − z). `reproduce.py`
evaluates the two parts separately: the hydrostatic profile (the figure) and, per case, the
frictional gradient and its ratio r to rho g, which is 0.05 to 3 % for the cases above. Because
the profile is linear, the combined estimate is their sum. A 2D or 3D solver adds information
only where that estimate stops holding:

1. **Inlet and outlet manifolds and entrance lengths.** Distributor jets, a developing velocity
   profile and contraction losses at the ports add local pressure changes. These are largest at
   the bottom, which is the end nearest flooding. The hydrodynamic entrance length is not small
   for every case above. The round-tube estimate 0.05 Re Dh gives 0.8 to 7.7 cm for the 2 mm
   gap and 4.8 to 48 cm for the 5 mm gap, so at 5 mm and 0.1 m/s the flow would develop over
   about half of a 1 m electrode. The parallel-plate correlation of Shah and London,
   L/Dh ≈ 0.011 Re + 0.315/(1 + 0.0175 Re), gives about a quarter of that: 0.2 to 1.7 cm and
   1.2 to 10.6 cm. The extra pressure drop of the developing region, of order 0.7 rho u²/2, is
   at most about 0.04 mbar, against about 104 mbar of hydrostatic change over 1 m, so the 1D
   result changes little. The fully developed gradient is still not the local gradient over
   that length.
2. **Non-uniform gap.** A GDE compressed by the gasket, or a flow field with ribs or a spacer
   mesh, gives a non-uniform b(x, z), and friction scales as 1/b².
3. **Gas side.** The frictional drop of a long or serpentine gas channel makes p_G(z)
   non-uniform. It can partly cancel the hydrostatic liquid gradient or add to it.
4. **Two-phase catholyte.** Bubbles from hydrogen evolution or gas breakthrough lower the
   mixture density and change the gradient with current and position.

**Decision rule:** implement only if the one-dimensional ratio r = friction gradient / rho g
exceeds 0.05 for a design case, if its entrance length (Shah and London, above) exceeds 10 % of
H, if the cell has manifolds or a non-uniform gap whose losses cannot be bounded by hand, or if
a collaborator's measured pressure profile (below) becomes available to compare with. Of the
1 m cases above, only the 5 mm gap at 0.1 m/s reaches the entrance-length trigger (10.6 cm).
At the lab conditions of the paper (r = 1.8e-3) none applies: the entrance length, about 7 mm,
is a third of the 22 mm electrode, but the whole hydrostatic difference across that electrode
is only 2.3 mbar.

## Candidate tools

- **EchemFEM** (Firedrake-based finite elements for electrochemical transport). It suits the
  coupled extension: ion transport, current distribution and gas evolution in the catholyte and
  the porous electrode. The free-flow part would be a Stokes or Navier-Stokes solve in Firedrake
  beside it. EchemFEM's own transport equations are not needed for the pressure question alone.
- **A collaborator's COMSOL model** (laminar flow, optionally with Brinkman flow in the porous
  layer and a bubbly-flow model). It suits the single-phase question directly, but it is not
  open, so its inputs and mesh would be recorded here and its results kept as a run record.
  The model itself would not be included.

Either tool answers the same question with the same boundary conditions and the same comparison
data below.

## Model and boundary conditions

| Boundary or term | Condition |
| --- | --- |
| Domain | catholyte channel H × W × b (2D: the H × b plane at mid-width; 3D for manifolds or ribs); gas channel the same, optional |
| Catholyte inlet (bottom) | flow rate Q, fully developed profile (or the manifold geometry, if modelled) |
| Catholyte outlet (top) | pressure p_out, the set point, swept |
| Walls, membrane side | no slip, impermeable |
| GDE face | no slip, impermeable in flow-by. An extension adds Darcy or Brinkman flow into the porous layer with the measured CO2 permeability (SI Table S4) to bound the leakage |
| Gas channel | inlet flow as designed, outlet at the check-valve pressure (345 mbar gauge in the lab); or p_G uniform if the gas side is not modelled |
| Body force | gravity, −rho g e_z |
| Properties | 1 M KHCO3 at 20 °C: rho 1065 kg/m³ (range 1055 to 1075), mu 1.1 mPa s (both ASSUMED, as in tolerances.yaml); isothermal |
| Output | dp(z) on the GDE face (and dp(x, z) in 3D); area fraction with dp < dp_G* or dp > dp_L*; the set point p_out that minimises it |

No current is applied in the single-phase case. Electrowetting, the narrowing of the window under
current, is a property of the GDE that this flow model cannot predict. It enters only as a
reduced window taken from measurements.

## Comparison data

1. **Verification against analytic results (required before any use):**
   - hydrostatic profile at Q = 0: dp(z) linear with slope rho g, to machine precision;
   - fully developed laminar segment: frictional gradient within 0.5 % of the Shah and London
     rectangular-duct value used in `reproduce.py`;
   - the 1 m cases of `comparison.md`: dp change within 0.5 % of (rho g + friction gradient)
     times the length, with rho g and the friction gradient as `reproduce.py` records them per
     case, taken between the end of the entrance length (Shah and London, above) and 5 gap
     widths below the outlet.
2. **The lab cell of the paper (consistency):** 100 mL/min, 30 mm wide, 33 mm flow channel, the
   catholyte pressure and the reactor differential pressure of the SI spreadsheet (sheet FE).
   The cell is too short (22 mm electrode) to resolve a profile. It checks only the absolute
   level and the port losses, within the 3 to 6 mbar scatter of the recorded values.
3. **Validation (needed, not available here):** a pressure profile measured along a tall
   flow-by cell, with taps at several heights on the liquid and gas side and the height at which
   liquid breakthrough first appears, at a stated flow and set point. This paper does not provide
   one. A collaborator's tall-cell data, or a published data set found later, would be recorded
   in a new `source.yaml` entry with checksums, as for the present data. Without it the solver
   is verified, not validated.

## Mesh-convergence plan

- **Meshes:** three structured meshes with a refinement ratio of 2 in every direction (coarse,
  medium, fine). At least 10 cells across the gap b on the coarse mesh, graded towards the walls,
  and at least 200 along H. In 3D, at least 20 across W.
- **Quantities:**
  - dp between the bottom and the top of the GDE face;
  - the maximum of |dp(z) − dp_1D(z)| along the face;
  - the height z* at which dp crosses dp_L* for the worst set point;
  - the flooded area fraction.
- **Criterion:** observed order of convergence within 0.5 of the scheme's formal order, and a
  grid convergence index (Richardson extrapolation, safety factor 1.25) on the fine mesh below
  1 % for dp and below 1 mm for z*. Results are reported from the fine mesh, with the GCI beside
  them. A case that does not converge to this level is reported as unresolved, not used.
- **Solver tolerances:** nonlinear residual below 1e-10 relative. A halved tolerance must change
  no reported quantity by more than 0.1 % of its GCI.

## What would be committed if it is implemented

A sub-folder `spatial/` in this reproduction, holding:

- the model definition (geometry and boundary conditions as data);
- a script with exact version pins (Firedrake/EchemFEM), or a record of the COMSOL version and
  model inputs for the collaborator's model;
- the three-mesh results with the GCI;
- the verification results;
- a run record in `reruns/`.

Tolerances for the verification and validation comparisons would be frozen in their own commit
before the first run, as ADR 0030 requires. None of it would go into a process folder.
