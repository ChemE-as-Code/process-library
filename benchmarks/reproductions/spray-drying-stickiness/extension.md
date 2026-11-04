# Design extension: droplet stickiness in a pilot spray dryer when inlet humidity or feed solids change

**HYPOTHETICAL design extension, not validated.** No dryer in the sources, and no dryer-scale
data, stand behind these numbers. The droplet model is the one from the reproduction. That
reproduction FAILED under its frozen rule (`comparison.md`): it places the surface glass
transition 22-36 % earlier than the thesis model, and it does not reproduce the measured locked
radius. Every dryer, droplet, stickiness and residence-time input below is labelled `assumed` in
`inputs.yaml` (section `extension`). The droplet model itself uses the material and gas-film
specification of the thesis model, labelled `reconstructed` there. Results:
`results/extension.json`, figure `results/fig3_dryer_stickiness.svg`.

## Question

A maltodextrin (DE 12) solution is spray dried in a co-current chamber held at a fixed outlet
temperature. We ask two things:

- Does a change in **inlet air humidity**, or in **feed solids**, move the time at which a
  droplet's surface stops being sticky?
- Where does that time fall relative to the time a droplet or particle can spend in the chamber
  before it meets a wall?

## Assumed dryer and method

| Item | Value |
| --- | --- |
| Chamber | 1.0 m diameter, 1.0 m cylinder, 60° cone; total height 1.87 m; volume 1.01 m³ |
| Drying air | 120 kg/h dry air (±20 % for the residence range), inlet 180 °C, outlet 85 °C held by the feed rate, 10 % heat loss |
| Feed | MD12 solution at 25 °C; base 30 wt% solids |
| Base inlet humidity | 8 g water per kg dry air |
| Energy and water balance (base) | evaporation 4.07 kg/h, feed 5.82 kg/h, powder 1.75 kg/h; outlet humidity 42 g/kg, outlet RH 11.1 % |
| Droplets | initial diameter 60 µm (median) and 150 µm (coarse tail); slip 0.2 m/s; gas at outlet conditions (well-mixed chamber). This is the slow-drying bound for the drying time. It is not conservative for re-softening of dried powder in hotter gas (see the flags) |
| Stickiness | sticky while surface T - Tg > (T - Tg)c. The band is (T - Tg)c = 0-20 K. The approximate bouncing onset is 3.5-5.5 × t_glass, from the thesis falling-droplet column (DE 5-21): bouncing only after 3.5 (DE 5) to 4.5 (DE 21) t_glass, and sticking collisions up to 5.5 t_glass for DE 12. It is not a bound |

**Residence-time window, a range rather than a point:**

- **Core pass:** the total height divided by an assumed axial core velocity of 1-3 m/s, which
  gives **0.62-1.87 s**. This is the shortest time for a droplet carried by the central jet to
  reach the cone wall and the outlet.
- **Mean gas residence:** V/Q at outlet conditions, which gives **23-35 s** for a gas flow of
  ±20 %.
- A recirculating fines fraction stays longer than the mean gas residence. That tail is not
  bounded here.

## Result

**Changed input 1: inlet humidity**, with feed solids at 30 wt%. At a fixed outlet temperature,
the same water load is added to wetter air:

| Inlet humidity | Outlet RH | Wet bulb | t_glass, 60 µm | t_glass, 150 µm | Powder in equilibrium with outlet air: moisture, T - Tg | Modelled mean moisture at 3 t_full, 60 / 150 µm |
| --- | --- | --- | --- | --- | --- | --- |
| 5 g/kg | 10.3 % | 42.5 °C | 0.31 s | 1.78 s | 3.5 wt%, -26.3 K | 8.1 / 8.3 wt% |
| 8 g/kg (base) | 11.1 % | 43.4 °C | 0.33 s | 1.87 s | 3.6 wt%, -24.9 K | 8.0 / 8.2 wt% |
| 15 g/kg | 12.9 % | 45.3 °C | 0.36 s | 2.06 s | 3.9 wt%, -22.2 K | 7.9 / 8.1 wt% |
| 25 g/kg | 15.4 % | 47.9 °C | 0.41 s | 2.34 s | 4.2 wt%, -18.9 K | 7.8 / 8.0 wt% |

**Changed input 2: feed solids**, with inlet humidity at 8 g/kg. The feed rate adjusts to hold
85 °C at the outlet:

| Feed solids | t_glass, 60 µm | 3.5-5.5 × t_glass, 60 µm | t_glass, 150 µm | 3.5-5.5 × t_glass, 150 µm |
| --- | --- | --- | --- | --- |
| 20 wt% | 0.45 s | 1.58-2.48 s | 2.61 s | 9.1-14.3 s |
| 30 wt% | 0.33 s | 1.14-1.79 s | 1.87 s | 6.5-10.3 s |
| 40 wt% | 0.21 s | 0.75-1.18 s | 1.22 s | 4.3-6.7 s |

The onset factor is defined on the thesis model's t_glass. Here it multiplies this model's
t_glass, which case B places 22-36 % early: the thesis model's t_glass is 1.29-1.57 times ours.
On the thesis time scale the upper end, 5.5 × t_glass, would be 1.9-3.9 s at 60 µm and
10.5-22.5 s at 150 µm (`tglass_bias_thesis_over_this_model` in `extension.json`; dotted in
fig3).

For every case the surface margin T - Tg falls steeply through the 0-20 K band. It crosses
+20 K only 3-9 % earlier than 0 K, so the choice of (T - Tg)c within that band matters little
here. The bouncing onset matters much more. In the outlet gas assumed here, the surface stays
glassy once it is glassy, up to 3 t_full. This holds only for particles that never re-enter gas
hotter than about 137-146 °C (see the flags).

**Moisture at the end of the horizon.** At 3 t_full (2.3-2.6 s at 60 µm, 13.4-15.2 s at 150 µm)
the modelled particles still hold 7.3-8.8 wt% water on average, about twice the equilibrium
moisture below. Their surface is glassy; their interior is wetter than equilibrium.

## Engineering consequence (physical terms)

- **Moist inlet air mainly slows drying.** Raising the inlet humidity from 5 to 25 g/kg raises the
  outlet RH from 10 to 15 %. That lifts the wet-bulb temperature by 5 K and lowers the vapour
  driving force, and the time to a glassy surface grows by about 30 % for both droplet sizes.
- **Humid air does not make the dried MD12 powder sticky at the outlet.** In equilibrium with
  the 85 °C outlet air, its moisture of 3.5-4.2 wt% keeps it 19-26 K below its glass
  transition. This assumes the particle equilibrates within the 23-35 s mean gas residence; at
  the end of the modelled horizon (3 t_full) it still holds 7.3-8.8 wt% water on average.
  - The powder would reach Tg only above an outlet RH of 34 %. That needs about 118 g/kg in the
    inlet air, which ambient air never has.
  - With (T - Tg)c = 20 K, it would need 53 % outlet RH.
  - The humidity margin is large because MD12 has a high dry Tg (425 K). A low-Tg feed, such as
    sugars or high-DE maltodextrin, would not have this margin.
- **Feed solids control the sticky window.** Going from 20 to 40 wt% halves the time to a glassy
  surface for both sizes (0.45 to 0.21 s at 60 µm; 2.6 to 1.2 s at 150 µm). The surface is
  enriched faster when there is less water to remove; this is the thesis's finding (B6 is
  reproduced).
- **Against the residence-time window:**
  - **60 µm droplets** have a glassy surface by 0.2-0.45 s, before the shortest core pass
    (0.62 s). Their approximate bouncing onset, 3.5-5.5 × t_glass (0.75-2.5 s), overlaps the
    whole core-pass window (0.62-1.87 s), and more so on the thesis time scale (up to 3.9 s). So
    they may still collide as sticky during the core pass.
  - **150 µm droplets** reach a glassy surface only at 1.2-2.6 s, inside or after the core-pass
    window, and their bouncing onset (4.3-14 s, up to 22.5 s on the thesis time scale) lies well
    beyond it. Humid inlet air adds 0.5 s to the time to a glassy surface; higher feed solids
    remove up to 1.4 s.
  - Under these assumptions, coarse droplets carried by the core flow are the ones whose surface
    could still be above the assumed (T - Tg)c at first wall contact. Whether they deposit is not
    determined here (see measurements 1, 4, 5 and 8 below).
  - In the outlet gas, every case reaches a glassy surface far below the mean gas residence
    time (23-35 s). Recirculating particles are glassy long before they leave, provided they
    never re-enter gas hotter than about 137-146 °C, where dried powder in equilibrium with the
    gas is above its Tg (flags below).
- **Hypotheses to test (not a design reading):** if the surface state at first wall contact
  governs early deposition in this dryer, these changes would reduce it, in the order the model
  suggests:
  1. Raise feed solids, if atomisation allows.
  2. Narrow the coarse tail of the spray.
  3. Lengthen the path to the first wall contact.

  The model suggests a lower inlet humidity changes the time to a glassy surface by only about
  0.1 s at 60 µm.

## Out-of-range and extrapolation flags

- **Droplet size:** 60-150 µm, against 432-480 µm in the reproduced cases. Drying times scale
  about with R0², and the model has been compared only at the larger sizes.
- **Gas temperature:** 85 °C, against 20-65 °C in the compared cases. The thesis applied the
  model up to 125 °C but found it too simple at spray-drying rates.
- **Time-scale bias:** the reproduction gave a glassy surface 22-36 % earlier than the thesis
  model. If that model is right, every t_glass above is short by a factor of 1.29-1.57, and so
  is every bouncing-onset time derived from it.
- **Constant gas conditions:** the real gas cools from 180 to 85 °C along the chamber and gets
  wetter. Near the atomiser, droplets dry faster than shown, so for the drying time the outlet
  gas is a slow-drying bound.
- **Outlet gas is not conservative for re-softening.** Along the gas path from the inlet
  (180 °C) to the outlet (85 °C), with humidity linear in temperature, dried powder in
  equilibrium with the local gas is above its Tg wherever the gas is hotter than about 145 °C
  (base, 8 g/kg; 137 °C at 25 g/kg inlet humidity, 146 °C at 5 g/kg). At the inlet temperature
  it is 29-32 K above Tg; with (T - Tg)c = 20 K the threshold gas temperature is 166-170 °C
  (`equilibrium_powder_along_gas_line` in `extension.json`). Fines recirculated into the hot
  zone near the atomiser can therefore re-soften. This is an equilibrium state; how fast a
  particle approaches it in the hot zone is not modelled.
- **Fixed droplet size:** the size is held fixed when solids change. In practice, higher
  viscosity at 40 wt% coarsens the spray and offsets part of the gain.
- **Property extrapolation:** the GAB parameters have no temperature dependence and are used at
  85 °C. The Gordon-Taylor parameters are for MD12 only.
- **No collision or impact model:** stickiness is judged from the surface state only. The thesis
  shows that this is an order-of-magnitude predictor of collision outcome, and that impact
  velocity matters.
- **Residence window:** the core velocity (1-3 m/s) is assumed and is not derived from a flow
  model. Ballistic wall impact of spray droplets right after atomisation is not modelled.

## Dryer-scale measurements needed to infer wall deposition

These numbers do not give a deposition rate. Inferring wall deposition in a real dryer would need
measurements such as:

1. **Deposit mass flux by zone:** removable wall coupons or panels in the cylinder, the cone and
   near the atomiser, weighed after timed runs. Record the deposit moisture and morphology too.
2. **Closure of the solids balance:** feed solids against powder collected at the chamber
   outlet, cyclone and filter, over a steady run.
3. **Gas temperature and humidity fields:** traversing probes in the chamber, to replace the
   well-mixed assumption.
4. **Particle size, velocity and flux near the wall:** phase-Doppler or high-speed imaging. This
   gives the size and impact velocity of the particles that actually reach the walls.
5. **Particle moisture near the wall:** isokinetic sampling at the deposit locations, to place
   wall contacts on the T - Tg axis.
6. **Wall temperature:** a cooled or heated wall shifts the surface T - Tg at impact.
7. **Residence-time distribution:** tracer pulse tests, gas and particle, to replace the assumed
   core velocity and to bound the recirculating tail.
8. **Stickiness at the dryer's impact velocity:** a dynamic test (particle gun, or fluidised bed
   for low velocity) on the produced powder, giving (T - Tg)c for MD12. The thesis review shows
   (T - Tg)c varies by tens of kelvin with the test and the velocity.

## Status

Hypothetical design extension. Not validated, and not independent of the reproduction model.
Specialist review: not yet (an optional follow-up).
