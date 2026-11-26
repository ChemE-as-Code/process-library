I finished all three tasks for this stage: the S5b#1 fix, then P-301 and P-401. Each was committed separately, and the pre-commit hook ran `cheme validate` on every commit with 0 errors. Nothing is pushed, merged or signed off.

**Commits on `stage/basic-lactic-acid-fermentation`**
1. **S5b#1 (`d0e8fffa`):** the SIP header set point PIC-2205 drops from 3 to 1.5 barg (recorded in D-037).
   - 1.5 barg is 60 % of the fermenters' 2.5 barg design pressure and disc set point, and below the seed vessels' 3.0 and 6.0 barg, so a normal SIP no longer bursts a disc.
   - Steam at 1.5 barg is about 127 C, which still leaves margin for the 121 C vessel SIP.
   - PV-2205 fails closed and alarms high at 1.8 barg (both assumed). I did not add per-vessel pressure control.
   - At the new pressure the DN80 bottom SIP inlets reach about 60 m/s at heat-up peak. I accepted that as assumed and left it for detail engineering to check.
2. **P-301 (`eba0eac0`, D-038):** cell removal, acidulation and gypsum filtration.
   - Three centrifuges S-301A to C, each on its own feed flow loop; the cell mass cake goes through hopper V-301 and pumps P-301A/B to anaerobic digestion.
   - R-301 gets agitator A-301 (newly listed). The 93 % acid is dosed in ratio to the clarified broth flow, trimmed by a pH loop (pH about 2.5, assumed).
   - The heat is removed by a pump-around through E-301, sized on 2.0 MW.
   - The belt filter S-302 drains to filtrate receiver V-303 with vacuum pumps K-301A/B and filtrate pumps P-306A/B.
   - One change to an earlier decision: the acid now goes into the tank at the impeller, not into the pump-around as D-025 said (avoids local heat and gypsum scale in the slurry line and exchanger). The reason is in D-038.
3. **P-401 (`3406a099`, D-039):** four-effect falling-film evaporator E-401A to D in forward feed.
   - Each effect has a circulation pump P-403x and a sump level loop on the transfer to the next effect; LP steam to E-401A is flow-controlled.
   - The vapour cascades to the surface condenser E-402; condensates go to receiver V-401 under vacuum pumps K-401A/B.
   - The concentrate leaves by P-402A/B on a density loop.
   - The effect pressures (1.0, 0.6, 0.3, 0.12 bar(a)) are assumed, and the vapour line sizes (DN600 to DN1400) follow from them.

**What to know about the drawings**
- Each sheet has crossings that cannot be drawn away, accepted in `checks.yaml` as proposals for the design review: 2 on P-301 and 7 on P-401.
- About 10 cosmetic drawing warnings remain on P-401: effect tags sitting on their symbol outline, the DIC-4002 measuring line through its valve actuator, and a product off-page note crowding a pump label.
- DEXPI's diameter standard has no DN250 to DN1400, so those sizes appear only in the line numbers and the line list, not on the nozzles.

**What is left**
- Carry-over items S5b#2 to #10 and the S5 findings are for close-out stage S9.
- P-402 and P-403 are not drawn.
- New items are not yet in the layout (A-301 at least). The layout gates still fail: no plant model, no zones, no layout review.
- Open on P-301: R-301 level trips, vacuum pressure indication, belt filter interlocks.
- Open on P-401: vacuum control, evaporator CIP, relief of E-401A's steam chest.

A merge is pending: the branch is waiting for the independent review, and a human or the reviewer has to merge it.
