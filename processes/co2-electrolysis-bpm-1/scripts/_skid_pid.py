"""The P&ID of one pilot skid of #330, drawn with core's authoring API.

`scripts/draft_P-01.py` (Skid A, train 1xx) and `scripts/draft_P-02.py` (Skid B, train 2xx)
call :func:`draw` on the frame `cheme regen` hands them (`plant.yaml` `generator:`); the
sheets are generated, never edited by hand (AGENTS.md). Both skids share the stacks, the
anolyte loop, the cathode gas train and the gas conditioning packages; Skid B adds the 5 M KOH
day tank and dosing pump, the make-up water on level and the bleed (DESIGN.md D-007, D-010,
D-017).

What is drawn follows the PFD (`process/flowsheet.yaml`): every step is an equipment item of
`equipment/equipment-list.yaml`, every material stream a line of `piping/line-list.yaml`
(the branches of a manifold carry their own line number), every instrument a tag of
`control/instrument-list.yaml`. The loops, trips and sequences are in `control/`; the sheet
shows the instruments and the control valves they act on, never the trip logic.

Concept-stage simplifications (DESIGN.md D-017): isolation and drain valves only where
operation needs them, no relief devices (not sized: open), the gas conditioning as two
black-box packages, the stacks' DC bus not drawn (the rectifier U-x01 and its JIC-x01 only),
the speed signals of FIC-x01 and AIC-201 to their pumps not drawn (control/loops.yaml). The
four stacks are fed in parallel by four manifolds: with the anolyte manifolds above and below
the stack row, the two cathode gas manifolds cross them three times each (accepted in
checks/checks.yaml with that reason).
"""

from __future__ import annotations

from chemeascode.domains.piping.authoring import (
    Nozzle,
    Sheet,
    equipment,
    instrument,
    line,
    note,
    offpage,
    tee,
    valve,
)

#: Stack centres (x, sheet mm) and the stack row's centre line.
STACK_X = (140.0, 170.0, 200.0, 230.0)
STACK_Y = 140.0
SUFFIX = "ABCD"
#: Manifold heights: cathode gas out and anolyte return above the row, anolyte supply and CO2
#: feed below it.
Y_CG, Y_RET, Y_SUP, Y_CO2 = 88.0, 105.0, 175.0, 200.0
#: Nominal diameters (ASSUMED, D-017): the anolyte loop DN 25 (11.2 L/min, about 0.3 m/s),
#: the cathode gas and the small liquid lines DN 15.
DN_LIQ, DN_GAS, DN_SMALL = 25, 15, 15


def draw(sheet: Sheet, skid: str) -> None:
    """Draw Skid *skid* ("A" or "B") on *sheet*."""
    n = {"A": 1, "B": 2}[skid]
    dosed = skid == "B"

    def t(prefix: str, k: int, suffix: str = "") -> str:
        return f"{prefix}-{n}{k:02d}{suffix}"

    def vid(prefix: str, k: int) -> str:
        return f"{prefix}{n}{k:02d}"

    def tid(line_number: str, s: str) -> str:
        return f"Tee_{line_number.replace('-', '')}_{s}"

    # -- equipment --------------------------------------------------------------------------
    stacks = [
        equipment(
            sheet,
            "ProcessEquipment",
            t("E", 1, s),
            shape="VESSEL_SHAPE",
            at=(x, STACK_Y),
            scale=(1.2, 1.2),
            label_at=(x, STACK_Y),
            nozzles=[
                Nozzle("N1", (0, 15), DN_LIQ),  # anolyte in
                Nozzle("N2", (0, -15), DN_LIQ),  # anolyte out with the anode O2
                Nozzle("N3", (9, 8), DN_GAS),  # cathode CO2 in
                Nozzle("N4", (9, -8), DN_GAS),  # cathode gas out
            ],
        )
        for x, s in zip(STACK_X, SUFFIX, strict=True)
    ]
    tx, ty = 70.0, 145.0  # the anolyte reservoir
    tank_nozzles = [
        Nozzle("N1", (6, -17.5), DN_LIQ),  # anolyte return
        Nozzle("N2", (-6, -17.5), DN_LIQ),  # O2 vent
        Nozzle("N3", (-14, -8), DN_LIQ),  # 1 M KOH fill
        Nozzle("N4", (6, 17.5), DN_LIQ),  # outlet to the recirculation pump
        Nozzle("N5", (-6, 17.5), DN_LIQ),  # drain (spent anolyte; Skid B also the bleed)
        Nozzle("N7", (14, 0), None),  # pH
    ]
    if dosed:
        tank_nozzles += [
            Nozzle("N6", (-14, 2), None),  # level, make-up control
            Nozzle("N8", (-12, -17.5), DN_SMALL),  # 5 M KOH dose
            Nozzle("N9", (-14, 12), DN_SMALL),  # make-up water
            Nozzle("N10", (14, 10), None),  # level, low-low trip (independent)
        ]
    else:
        tank_nozzles.append(Nozzle("N6", (14, -10), None))  # level
    tank = equipment(
        sheet,
        "Tank",
        t("T", 1),
        shape="TANK_CONE_ROOF_SHAPE",
        at=(tx, ty),
        scale=1.4,
        label_at=(tx, ty + 4),
        nozzles=tank_nozzles,
    )
    pump = equipment(
        sheet,
        "CentrifugalPump",
        t("P", 1),
        shape="CENTRIFUGAL_PUMP_SHAPE",
        at=(90.0, 230.0),
        label_at=(90.0, 243.0),
        nozzles=[Nozzle("N1", (-7.5, 0), DN_LIQ), Nozzle("N2", (0, -7.5), DN_LIQ)],
    )
    cooler = equipment(
        sheet,
        "PlateHeatExchanger",
        t("E", 11),
        shape="PLATE_TYPE_HEAT_EXCHANGER_SHAPE",
        at=(115.0, 205.0),
        rotation=90.0,
        label_at=(128.0, 205.0),
        nozzles=[
            Nozzle("N1", (-5, 5), DN_LIQ),  # anolyte in
            Nozzle("N2", (0, -15), DN_LIQ),  # anolyte out
            Nozzle("N3", (4, 15), DN_SMALL),  # cooling water in
            Nozzle("N4", (-4, 15), DN_SMALL),  # cooling water out
        ],
    )
    sep = equipment(
        sheet,
        "Vessel",
        t("V", 21),
        shape="VESSEL_DISHED_ENDS_SHAPE",
        at=(290.0, 80.0),
        scale=0.8,
        label_at=(290.0, 80.0),
        nozzles=[
            Nozzle("N1", (-7, 8), DN_GAS),  # cathode gas and condensate in
            Nozzle("N2", (0, -10), DN_GAS),  # gas out
            Nozzle("N3", (0, 10), DN_SMALL),  # condensate out
            Nozzle("N4", (7, 5), None),  # level
        ],
    )
    comp = equipment(
        sheet,
        "ReciprocatingCompressor",
        t("K", 31),
        shape="COMPRESSOR_RECIPROCATING_SHAPE",
        at=(330.0, 45.0),
        label_at=(330.0, 58.0),
        nozzles=[Nozzle("N1", (-7.5, 0), DN_GAS), Nozzle("N2", (7.5, 0), DN_GAS)],
    )
    psa = equipment(
        sheet,
        "ProcessEquipment",
        t("X", 31),
        shape="COLUMN_FIXED_BED_SHAPE",
        at=(365.0, 70.0),
        scale=0.6,
        label_at=(384.0, 66.0),
        nozzles=[
            Nozzle("N1", (-9, 8), DN_GAS),  # feed
            Nozzle("N2", (0, -15), DN_GAS),  # CO product
            Nozzle("N3", (-4, 15), DN_GAS),  # CO2 recycle
            Nozzle("N4", (4, 15), DN_GAS),  # tail gas
        ],
    )
    oxid = equipment(
        sheet,
        "ProcessEquipment",
        t("X", 32),
        shape="FURNACE_SHAPE",
        at=(390.0, 150.0),
        scale=0.8,
        label_at=(372.0, 152.0),
        nozzles=[
            Nozzle("N1", (-4, -10), DN_GAS),  # tail gas in
            Nozzle("N2", (0, 10), DN_GAS),  # air in
            Nozzle("N3", (8, -5), 25),  # flue gas out
        ],
    )
    equipment(
        sheet,
        "ProcessEquipment",
        t("U", 1),
        shape="VESSEL_SHAPE",
        at=(200.0, 235.0),
        scale=(1.4, 0.6),
        label_at=(200.0, 235.0),
    )
    equipment(sheet, "Fan", t("K", 41), shape="FAN_SHAPE", at=(265.0, 235.0),
              label_at=(265.0, 242.0))

    # -- anolyte loop -----------------------------------------------------------------------
    # return manifold above the stacks, from stack D to the reservoir
    ret_tees = [tee(tid(t("AN", 4), s), at=(x, Y_RET), branch="down")
                for x, s in zip(STACK_X[:3][::-1], "CBA", strict=True)]
    ret = line(
        sheet,
        t("AN", 4),
        dn=DN_LIQ,
        fluid="Anolyte",
        route=[stacks[3]["N2"], (STACK_X[3], Y_RET), *ret_tees, (tank["N1"].xy[0], Y_RET),
               tank["N1"]],
        label_at=(100.0, Y_RET - 7.0),
    )
    for tee_, stack, s in zip(ret_tees, stacks[2::-1], "CBA", strict=True):
        line(sheet, t("AN", 4, s), dn=DN_LIQ, fluid="Anolyte", route=[stack["N2"], tee_.branch],
             label_at=(stack["N2"].xy[0] - 9.0, (Y_RET + 125.0) / 2 - 2.0))
    # reservoir to pump to cooler
    line(
        sheet,
        t("AN", 1),
        dn=DN_LIQ,
        fluid="Anolyte",
        route=[tank["N4"], valve(vid("HV", 1), "BallValve", at=(tank["N4"].xy[0], 190.0),
                                 tag=t("HV", 1)),
               (tank["N4"].xy[0], 230.0), pump["N1"]],
        label_at=(85.0, 180.0),
    )
    an2 = line(sheet, t("AN", 2), dn=DN_LIQ, fluid="Anolyte",
               route=[pump["N2"], (90.0, 210.0), cooler["N1"]], label_at=(100.0, 216.0))
    # supply manifold below the stacks, from the cooler to stack D
    sup_tees = [tee(tid(t("AN", 3), s), at=(x, Y_SUP), branch="up")
                for x, s in zip(STACK_X[:3], "ABC", strict=True)]
    sup = line(
        sheet,
        t("AN", 3),
        dn=DN_LIQ,
        fluid="Anolyte",
        route=[cooler["N2"], (115.0, Y_SUP), *sup_tees, (STACK_X[3], Y_SUP), stacks[3]["N1"]],
        label_at=(123.0, 162.0),
    )
    for tee_, stack, s in zip(sup_tees, stacks[:3], "ABC", strict=True):
        line(sheet, t("AN", 3, s), dn=DN_LIQ, fluid="Anolyte", route=[tee_.branch, stack["N1"]],
             labels=False)
    # O2 vent, 1 M KOH fill, spent anolyte drain (Skid B: with the bleed)
    line(
        sheet,
        t("O2V", 1),
        dn=DN_LIQ,
        fluid="Oxygen",
        route=[tank["N2"], offpage("out", at=(tank["N2"].xy[0], 22.0),
                                   note="to atmosphere")],
        label_at=(tank["N2"].xy[0] + 10.0, 60.0),
    )
    line(
        sheet,
        t("KOH", 1),
        dn=DN_LIQ,
        fluid="KOH solution",
        route=[offpage("in", at=(14.0, tank["N3"].xy[1]), note="1 M KOH fill",
                       note_at=(18.0, tank["N3"].xy[1] - 12.0)),
               valve(vid("HV", 2), "BallValve", at=(36.0, tank["N3"].xy[1]), tag=t("HV", 2)),
               tank["N3"]],
        label_at=(26.0, tank["N3"].xy[1] + 6.0) if not dosed else (26.0, tank["N3"].xy[1] - 7.0),
    )
    bleed_tee = tee(tid(t("SP", 1), "BL"), at=(tank["N5"].xy[0], 200.0), branch="left",
                    branch_dn=DN_SMALL)
    sp_route = [tank["N5"]]
    if dosed:
        sp_route.append(bleed_tee)
    sp_route += [valve(vid("HV", 3), "BallValve", at=(tank["N5"].xy[0], 235.0), tag=t("HV", 3)),
                 (tank["N5"].xy[0], 252.0),
                 offpage("out", at=(14.0, 252.0), note="spent anolyte, end of run")]
    line(sheet, t("SP", 1), dn=DN_LIQ, fluid="Anolyte", route=sp_route,
         label_at=(52.0, 226.0))
    # cooling water
    line(
        sheet,
        t("CWS", 1),
        dn=DN_SMALL,
        fluid="Cooling water",
        route=[offpage("in", at=(165.0, 255.0), note="CW supply"),
               valve(vid("TV", 11), "GlobeValve", at=(140.0, 255.0), tag=t("TV", 11)),
               (cooler["N3"].xy[0], 255.0), cooler["N3"]],
        label_at=(128.0, 263.0),
    )
    line(
        sheet,
        t("CWR", 1),
        dn=DN_SMALL,
        fluid="Cooling water return",
        route=[cooler["N4"], offpage("out", at=(cooler["N4"].xy[0], 268.0), note="CW return")],
        label_at=(100.0, 254.0),
    )

    # -- cathode gas --------------------------------------------------------------------------
    # cathode gas manifold above the return manifold, from stack A to the separator
    cg_tees = [tee(tid(t("CG", 1), s), at=(x + 12.0, Y_CG), branch="down")
               for x, s in zip(STACK_X[1:], "BCD", strict=True)]
    line(
        sheet,
        t("CG", 1),
        dn=DN_GAS,
        fluid="Cathode gas",
        route=[stacks[0]["N4"], (STACK_X[0] + 12.0, stacks[0]["N4"].xy[1]),
               (STACK_X[0] + 12.0, Y_CG), *cg_tees, sep["N1"]],
        label_at=(262.0, Y_CG - 7.0),
    )
    for tee_, stack, s in zip(cg_tees, stacks[1:], "BCD", strict=True):
        line(sheet, t("CG", 1, s), dn=DN_GAS, fluid="Cathode gas",
             route=[stack["N4"], (tee_.branch.xy[0], stack["N4"].xy[1]), tee_.branch],
             labels=False)
    line(
        sheet,
        t("CG", 2),
        dn=DN_GAS,
        fluid="Cathode gas",
        route=[sep["N2"], (290.0, 45.0),
               valve(vid("PV", 21), "GlobeValve", at=(306.0, 45.0), tag=t("PV", 21)),
               comp["N1"]],
        label_at=(300.0, 58.0),
    )
    line(
        sheet,
        t("CG", 3),
        dn=DN_GAS,
        fluid="Cathode gas",
        route=[comp["N2"], valve(vid("CV", 31), "CheckValve", at=(342.0, 45.0)), (348.0, 45.0),
               (348.0, psa["N1"].xy[1]), psa["N1"]],
        label_at=(338.0, 30.0),
    )
    line(
        sheet,
        t("CD", 1),
        dn=DN_SMALL,
        fluid="Cathode condensate",
        route=[sep["N3"], (290.0, 105.0),
               valve(vid("LV", 22), "GlobeValve", at=(310.0, 105.0), tag=t("LV", 22)),
               (330.0, 105.0), offpage("out", at=(330.0, 160.0), note="to site effluent")],
        label_at=(318.0, 128.0),
    )
    # gas conditioning: product, recycle, tail gas, oxidiser
    line(
        sheet,
        t("CO", 1),
        dn=DN_GAS,
        fluid="CO",
        route=[psa["N2"], (365.0, 40.0),
               valve(vid("PV", 31), "GlobeValve", at=(386.0, 40.0), tag=t("PV", 31)),
               offpage("out", at=(410.0, 40.0), note="CO product")],
        label_at=(378.0, 48.0),
    )
    rec_tee = tee(tid(t("CO2", 1), "R"), at=(361.0, Y_CO2), branch="up")
    water_tee = tee(tid(t("CO2", 1), "W"), at=(330.0, Y_CO2), branch="down")
    co2_tees = [tee(tid(t("CO2", 1), s), at=(x + 16.0, Y_CO2), branch="up")
                for x, s in zip(STACK_X[:0:-1], "DCB", strict=True)]
    co2 = line(
        sheet,
        t("CO2", 1),
        dn=DN_GAS,
        fluid="CO2",
        route=[offpage("in", at=(410.0, Y_CO2), note="CO2 supply"),
               valve(vid("FV", 2), "GlobeValve", at=(385.0, Y_CO2), tag=t("FV", 2)),
               rec_tee, water_tee, *co2_tees, (STACK_X[0] + 16.0, Y_CO2),
               (STACK_X[0] + 16.0, stacks[0]["N3"].xy[1]), stacks[0]["N3"]],
        label_at=(300.0, Y_CO2 + 7.0),
    )
    for tee_, stack, s in zip(co2_tees, stacks[:0:-1], "DCB", strict=True):
        line(sheet, t("CO2", 1, s), dn=DN_GAS, fluid="CO2",
             route=[tee_.branch, (tee_.branch.xy[0], stack["N3"].xy[1]), stack["N3"]],
             labels=False)
    line(sheet, t("CO2", 2), dn=DN_GAS, fluid="CO2", route=[psa["N3"], rec_tee.branch],
         label_at=(350.0, 150.0))
    w1 = line(
        sheet,
        t("W", 1),
        dn=DN_SMALL,
        fluid="Water",
        route=[offpage("in", at=(410.0, 235.0), note="demineralised water"),
               valve(vid("HV", 4), "GlobeValve", at=(392.0, 235.0), tag=t("HV", 4)),
               (330.0, 235.0), water_tee.branch],
        label_at=(318.0, 222.0),
    )
    line(sheet, t("TG", 1), dn=DN_GAS, fluid="Tail gas",
         route=[psa["N4"], (369.0, 100.0), (oxid["N1"].xy[0], 100.0), oxid["N1"]],
         label_at=(397.0, 120.0))
    line(sheet, t("AIR", 1), dn=DN_GAS, fluid="Air",
         route=[offpage("in", at=(410.0, 172.0), note="air"), (oxid["N2"].xy[0], 172.0),
                oxid["N2"]],
         labels=False)
    line(sheet, t("FG", 1), dn=25, fluid="Flue gas",
         route=[oxid["N3"], offpage("out", at=(410.0, oxid["N3"].xy[1]), note="to atmosphere")],
         labels=False)

    # -- Skid B: 5 M KOH dosing, make-up water, bleed ------------------------------------------
    if dosed:
        day = equipment(
            sheet,
            "Tank",
            t("T", 2),
            shape="TANK_CONE_ROOF_SHAPE",
            at=(30.0, 40.0),
            scale=0.8,
            label_at=(30.0, 42.0),
            nozzles=[Nozzle("N1", (0, -10), DN_SMALL), Nozzle("N2", (0, 10), DN_SMALL),
                     Nozzle("N3", (8, 0), None)],
        )
        doser = equipment(
            sheet,
            "ReciprocatingPump",
            t("P", 2),
            shape="PUMP_DIAPHRAGM_SHAPE",
            at=(30.0, 75.0),
            label_at=(16.0, 75.0),
            nozzles=[Nozzle("N1", (0, -7.5), DN_SMALL), Nozzle("N2", (7.5, 0), DN_SMALL)],
        )
        line(sheet, t("KOH", 2), dn=DN_SMALL, fluid="KOH solution",
             route=[offpage("in", at=(30.0, 14.0), note="5 M KOH refill",
                            note_at=(44.0, 10.0)),
                    valve(vid("HV", 5), "BallValve", at=(30.0, 23.0), tag=t("HV", 5)),
                    day["N1"]],
             label_at=(16.0, 22.0))
        line(sheet, t("KOH", 3), dn=DN_SMALL, fluid="KOH solution",
             route=[day["N2"], doser["N1"]], label_at=(42.0, 56.0))
        line(sheet, t("KOH", 4), dn=DN_SMALL, fluid="KOH solution",
             route=[doser["N2"], (tank["N8"].xy[0], 75.0), tank["N8"]],
             label_at=(46.0, 68.0))
        line(sheet, t("W", 2), dn=DN_SMALL, fluid="Water",
             route=[offpage("in", at=(14.0, tank["N9"].xy[1]), note="make-up water",
                            note_at=(18.0, tank["N9"].xy[1] + 7.0)),
                    valve(vid("LV", 1), "GlobeValve", at=(26.0, tank["N9"].xy[1]),
                          tag=t("LV", 1)),
                    tank["N9"]],
             label_at=(42.0, 166.0))
        bl = line(sheet, t("BL", 1), dn=DN_SMALL, fluid="Anolyte",
                  route=[bleed_tee.branch,
                         valve(vid("FV", 3), "GlobeValve", at=(36.0, 200.0), tag=t("FV", 3)),
                         offpage("out", at=(14.0, 200.0), note="bleed to site effluent",
                                 note_at=(19.0, 193.0))],
                  label_at=(28.0, 206.0))

    # -- instruments ----------------------------------------------------------------------------
    instrument(sheet, t("TIC", 11), at=(140.0, 188.0), sensing=sup.segments[0],
               sensing_at=(115.0, 188.0), signal_to=vid("TV", 11), fail_action="FO")
    instrument(sheet, t("TSHH", 12), at=(110.0, Y_RET + 12.0), sensing=ret.segments[-1],
               sensing_at=(110.0, Y_RET))
    instrument(sheet, t("FIC", 1), at=(100.0, 198.0), sensing=an2.segments[0],
               sensing_at=(100.0, 210.0))
    instrument(sheet, t("FIC", 2), at=(398.0, Y_CO2 - 14.0), sensing=co2.segments[0],
               sensing_at=(398.0, Y_CO2), signal_to=vid("FV", 2), fail_action="FC")
    instrument(sheet, t("FI", 3), at=(355.0, 247.0), location="field", sensing=w1.segments[0],
               sensing_at=(355.0, 235.0))
    instrument(sheet, t("PIC", 21), at=(276.0, 57.0), sensing=f"Line_CG{n}02_S1",
               sensing_at=(290.0, 57.0), signal_to=vid("PV", 21),
               signal_points=[(276.0, 30.0), (306.0, 30.0)], fail_action="FO")
    instrument(sheet, t("LIC", 22), at=(311.0, 85.0), sensing=sep["N4"], signal_to=vid("LV", 22),
               fail_action="FC")
    instrument(sheet, t("PIC", 31), at=(374.0, 27.0), sensing=f"Line_CO{n}01_S1",
               sensing_at=(374.0, 40.0), signal_to=vid("PV", 31), fail_action="FC")
    instrument(sheet, t("AIC", 1) if dosed else t("AI", 1), at=(98.0, tank["N7"].xy[1]),
               sensing=tank["N7"])
    if dosed:
        instrument(sheet, t("LIC", 1), at=(42.0, tank["N6"].xy[1]), sensing=tank["N6"],
                   signal_to=vid("LV", 1), fail_action="FC")
        instrument(sheet, t("LIA", 2), at=(98.0, tank["N10"].xy[1]), sensing=tank["N10"])
        instrument(sheet, t("LIA", 3), at=(50.0, 40.0), sensing=day["N3"])
        instrument(sheet, t("FIC", 3), at=(50.0, 188.0), sensing=bl.segments[0],
                   sensing_at=(50.0, 200.0), signal_to=vid("FV", 3), fail_action="FC")
    else:
        instrument(sheet, t("LIA", 1), at=(98.0, tank["N6"].xy[1]), sensing=tank["N6"])
    instrument(sheet, t("JIC", 1), at=(222.0, 235.0))
    instrument(sheet, t("AIA", 41), at=(290.0, 228.0), location="field")
    instrument(sheet, t("AIA", 42), at=(290.0, 242.0), location="field")
    note(sheet, f"{t('U', 1)}: rectifier, DC bus to the stacks (not drawn)", at=(160.0, 222.0))
