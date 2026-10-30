The S5b basic close-out is still blocked. Both basic gates still fail: `lifting-study` and `maturity-balanced`. I closed or partly closed all six round-2 findings, but the high finding 2026-10-29-design#1 stays open. Everything is committed (last commit `2779497`), `cheme validate` reports 0 errors, and the PR comment is in `build/pr-comment.md`. Nothing is pushed, and the merge is pending.

**Closed**
- **design-s5b-r2#1** (`9a1a12f`): `estimate/rates.yaml` now has three cited factors:
  - design and engineering 0.30 (Towler & Sinnott 2013, Table 6.3);
  - contractor's fee 0.03 and contingency 0.15 (Turton et al. 2012, §7.3).

  The unit rates and the two erection factors are still placeholders, because I found no published bulk unit prices. D-035 now gives that as the reason, not the licence. The file stays marked as example. So the bulk estimate I committed (`estimate/estimate.*`) is labelled EXAMPLE and prices nothing. Deleting it was refused in unattended mode.
- **design-s5b-r2#2** (`9a1a12f`): D-033 now says the crane selection is left to the contractor and is not checked.
- **design-s5b-r2#3** (`9a1a12f`): the fans are now priced from their simulated inlet flows: K-102 at 37.5 m³/s and K-103 at 61.8 m³/s. This is purchased cost only, because the package has no installation factor for fans.
- **layout-s5b-r2#1** (`8ea180c`): DW-1073 now runs at grade at x 229, off crane pad CP-203. It then rises to 8.0 m and crosses west overhead, so no grade run blocks the access from the north road.
- **layout-s5b-r2#3**: the E-504 row of the acceptance proposal no longer offers the 2 m move.

**Partly closed**
- **layout-s5b-r2#2** (`8ea180c`, `62a28a0`): `scripts/pad_search.py` has a new `overhead` mode that checks every crane pad against all piping above it.
  - I shifted CP-204 and CP-212, moved CP-205, CP-206 and CP-207, and added CP-213 for C-301 and C-302. C-301's lift radius drops from 23.1 m to 13.8 m.
  - Two pads still sit under pipe: CP-211 (E-301) and CP-703 (V-701). The search found no clear position for either within 4 m, so they are left for routing at detail.

**Still open: 2026-10-29-design#1 (high)**
- **`lifting-study`**: the same 8 lanes are blocked: H-101, E-104, E-402, K-501, E-501, E-502, E-505 and E-504. They can only be cleared by the erection sequence. They are set out for the owner in `build/lifting-acceptance-proposal.md`, and none is accepted.
- **`maturity-balanced`**:
  - The feed check fails because the flows of S1, S12, S61, S26 and S70 are results of this design. Giving them as sourced values needs the owner's gas, air and water specification. Recording them as given would be inventing data.
  - The reactor check fails on the H-101 hydrogen and ammonia combustion values. I searched again and cited a closer ammonia source ([Sharma et al. 2024](https://www.jstage.jst.go.jp/article/jtst/19/2/19_24-00063/_article/-char/en)), a gas-fired furnace burning ammonia with methane. It is a bench-scale furnace with air preheated to about 1000 °C, against 250 °C at E-106, so it does not cover this duty. I found no published measurement of hydrogen burnout in a fired heater ([Zeeco/ExxonMobil field report](https://info.zeeco.com/hubfs/Articles/Advancements%20in%20Burner%20Technology.pdf) gives only CO and NOx). Both values stay `assumed`.
- **Estimate**: still class 5, not class 4, because the bulk unit rates need owner or contractor prices.

**Gates** (`cheme check --stage basic`): these pass: process-basic, process-links, pids-valid, drawing-clean, pids-exist, layout-plot-plan, layout-3d, mto, tea. These fail: lifting-study, maturity-balanced, and the design and layout reviews, which these commits make out of date until the S5r reviews run.

STATUS: BLOCKED: lifting-study (8 lanes only the erection sequence can clear; owner decision) and maturity-balanced (the feed flows need the owner's gas, air and water specification; no published source measures H2 or NH3 burnout for H-101's duty)