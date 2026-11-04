# Design extension: droplet stickiness in a pilot spray dryer when inlet humidity or feed solids change

**HYPOTHETICAL design extension, not validated.** No dryer in the sources, and no dryer-scale
data, stand behind these numbers. The droplet model is the one from the reproduction. That
reproduction FAILED under its frozen rule (`comparison.md`): it places the surface glass
transition 22-36 % earlier than the thesis model, and it does not reproduce the measured locked
radius. Every input below is labelled `assumed` in `inputs.yaml` (section `extension`). Results:
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
| Droplets | initial diameter 60 µm (median) and 150 µm (coarse tail); slip 0.2 m/s; gas at outlet conditions (well-mixed chamber, the slow-drying bound) |
| Stickiness | sticky while surface T - Tg > (T - Tg)c. The band is (T - Tg)c = 0-20 K. The late bound is 4 × t_glass, from the thesis falling-droplet column, where bouncing began only at 3.5-4.5 t_glass |

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

| Inlet humidity | Outlet RH | Wet bulb | t_glass, 60 µm | t_glass, 150 µm | Powder at outlet: equilibrium moisture, T - Tg |
| --- | --- | --- | --- | --- | --- |
| 5 g/kg | 10.3 % | 42.5 °C | 0.31 s | 1.78 s | 3.5 wt%, -26.3 K |
| 8 g/kg (base) | 11.1 % | 43.4 °C | 0.33 s | 1.87 s | 3.6 wt%, -24.9 K |
| 15 g/kg | 12.9 % | 45.3 °C | 0.36 s | 2.06 s | 3.9 wt%, -22.2 K |
| 25 g/kg | 15.4 % | 47.9 °C | 0.41 s | 2.34 s | 4.2 wt%, -18.9 K |

**Changed input 2: feed solids**, with inlet humidity at 8 g/kg. The feed rate adjusts to hold
85 °C at the outlet:

| Feed solids | t_glass, 60 µm | 4 × t_glass, 60 µm | t_glass, 150 µm | 4 × t_glass, 150 µm |
| --- | --- | --- | --- | --- |
| 20 wt% | 0.45 s | 1.80 s | 2.61 s | 10.4 s |
| 30 wt% | 0.33 s | 1.30 s | 1.87 s | 7.5 s |
| 40 wt% | 0.21 s | 0.86 s | 1.22 s | 4.9 s |

For every case the surface margin T - Tg falls steeply through the 0-20 K band. It crosses
+20 K only 3-9 % earlier than 0 K, so the choice of (T - Tg)c within that band matters little
here. The late bound matters much more. In all cases the surface stays glassy once it is glassy,
up to 3 t_full.

## Engineering consequence (physical terms)

- **Moist inlet air mainly slows drying.** Raising the inlet humidity from 5 to 25 g/kg raises the
  outlet RH from 10 to 15 %. That lifts the wet-bulb temperature by 5 K and lowers the vapour
  driving force, and the time to a glassy surface grows by about 30 % for both droplet sizes.
- **Humid air does not make the dried MD12 powder sticky at the outlet.** At 85 °C its
  equilibrium moisture of 3.5-4.2 wt% keeps it 19-26 K below its glass transition.
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
    (0.62 s). Under the 4 × t_glass late bound (0.9-1.8 s), they can still be sticky during the
    core pass.
  - **150 µm droplets** reach a glassy surface only at 1.2-2.6 s, inside or after the core-pass
    window, and their late bound (5-10 s) lies well beyond it. Coarse droplets that reach the cone
    wall with the core flow are therefore the likely source of wall deposit. Humid inlet air adds
    0.5 s to that time; higher feed solids remove up to 1.4 s.
  - Every case reaches a glassy surface far below the mean gas residence time (23-35 s). Particles
    that recirculate with the gas are glassy long before they leave.
- **Design reading (hypothetical):** to cut early wall contact of sticky droplets in this dryer,
  in order of effect:
  1. Raise feed solids, if atomisation allows.
  2. Narrow the coarse tail of the spray.
  3. Lengthen the path to the first wall contact.

  Holding a lower inlet humidity helps by only about 0.1 s at 60 µm.

## Out-of-range and extrapolation flags

- **Droplet size:** 60-150 µm, against 432-480 µm in the reproduced cases. Drying times scale
  about with R0², and the model has been compared only at the larger sizes.
- **Gas temperature:** 85 °C, against 20-65 °C in the compared cases. The thesis applied the
  model up to 125 °C but found it too simple at spray-drying rates.
- **Time-scale bias:** the reproduction gave a glassy surface 22-36 % earlier than the thesis
  model. If that model is right, every t_glass above is short by about a third.
- **Constant gas conditions:** the real gas cools from 180 to 85 °C along the chamber and gets
  wetter. Near the atomiser, droplets dry faster than shown.
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
