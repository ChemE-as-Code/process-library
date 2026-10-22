# Shapes in the reference shape catalogue

Reuse these by id (`<References objects="#ShapeN" property="Shape"/>` in a ShapeUsage). They are in `empty-sheet.xml` already.

| id | name | used by |
|---|---|---|
| Shape21 | CENTRIFUGAL_PUMP_SHAPE | CentrifugalPump1 |
| Shape22 | RECIPROCATING_PUMP_SHAPE | ReciprocatingPump1 |
| Shape23 | VESSEL_WITH_DISHED_HEADS_SHAPE | Tank1 |
| Shape18 | PLATE_TYPE_HEAT_EXCHANGER_SHAPE | PlateHeatExchanger1 |
| Shape20 | FLOATING_HEAD_TUBE_BUNDLE_HEAT_EXCHANGER_SHAPE | TubularHeatExchanger1 |
| Shape24 | MANHOLE_SHAPE | Nozzle19 |
| Shape19 | NOZZLE_SHAPE | Nozzle1, Nozzle10, Nozzle11, Nozzle12, Nozzle13, Nozzle14, Nozzle15, Nozzle16, Nozzle17, Nozzle18, Nozzle2, Nozzle3, Nozzle4, Nozzle5, Nozzle6, Nozzle7, Nozzle8, Nozzle9 |
| Shape8 | BALL_VALVE_SHAPE | BallValve1, BallValve2, BallValve3, BallValve4, BallValve5 |
| Shape3 | GLOBE_VALVE_SHAPE | GlobeValve1, GlobeValve2, GlobeValve3 |
| Shape6 | SWING_CHECK_VALVE_SHAPE | SwingCheckValve1 |
| Shape5 | BUTTERFLY_VALVE_SHAPE | ButterflyValve1 |
| Shape9 | ANGLE_SAFETY_VALVE_SPRING_LOADED_SHAPE | SpringLoadedGlobeSafetyValve1 |
| Shape13 | BLIND_COVER_SHAPE | BlindFlange1, BlindFlange2 |
| Shape7 | REDUCER_GENERAL_SHAPE | PipeReducer1 |
| Shape12 | T_TYPE_CONNECTION_SHAPE | PipeTee1, PipeTee2, PipeTee3, PipeTee4, PipeTee5 |
| Shape15 | PIPING_INSULATED_SHAPE | PipingNetworkSegment19 |
| Shape11 | SLOPE_SHAPE | PipingNetworkSegment8 |
| Shape1 | CONTROLLED_ACTUATOR_SHAPE | ControlledActuator1, ControlledActuator2, ControlledActuator3 |
| Shape2 | ARROW_FOR_INLET_OF_ESSENTIAL_SUBSTANCES_SHAPE | FlowInPipeOffPageConnector1 |
| Shape14 | ARROW_FOR_OUTLET_OF_ESSENTIAL_SUBSTANCES_SHAPE | FlowOutPipeOffPageConnector1 |
| Shape4 | DIRECTION_OF_FLOW_SHAPE_FOR_PRIMARY_SEGMENT | PipingNetworkSegment18, PipingNetworkSegment3 |
| Shape10 | DIRECTION_OF_FLOW_SHAPE_FOR_SECONDARY_SEGMENT | PipingNetworkSegment19, PipingNetworkSegment20, PipingNetworkSegment21, PipingNetworkSegment22, PipingNetworkSegment23, PipingNetworkSegment8 |
| Shape16 | INSTRUMENTATION_BUBBLE_SHAPE_FIELD | ProcessInstrumentationFunction1 |
| Shape17 | INSTRUMENTATION_BUBBLE_SHAPE_CENTRAL | ProcessInstrumentationFunction2, ProcessInstrumentationFunction3, ProcessInstrumentationFunction4 |

# Shapes cheme-as-code adds

Also in `empty-sheet.xml` (after the reference shapes). For a sheet made before they were added, `cheme fragment shape NAME --sheet pid/<sheet>.xml` prints the Shape to paste into its catalogue, or says it is there already. The registration number is the shape's name, as the reference does for its shapes without a number, until the ISO 10628-2:2012 number is checked against the standard (not yet done for any added shape). Never invent a number, nor borrow one from a symbol of another name.

| id | name | ISO 10628 number | meaning | scale on A3 | default for |
|---|---|---|---|---|---|
| Shape_CentrifugalCompressor | CENTRIFUGAL_COMPRESSOR_SHAPE | name (ISO number not verified) | compressor, centrifugal (turbo); general compressor | 1.0 (15 mm circle); 1.5 for a main air compressor | CentrifugalCompressor, Compressor, RotaryCompressor |
| Shape_AxialCompressor | AXIAL_COMPRESSOR_SHAPE | name (ISO number not verified) | compressor, axial: wide inlet left, narrow outlet right | 1.0 (20 x 15 mm) | AxialCompressor |
| Shape_Turbine | TURBINE_SHAPE | name (ISO number not verified) | turbine or expander: narrow inlet left, wide outlet right | 1.0 (20 x 15 mm); mirror (rotation 180) for flow right to left | Turbine, GasTurbine, SteamTurbine |
| Shape_Blower | BLOWER_SHAPE | name (ISO number not verified) | blower or fan, with tangential outlet | 1.0 (15 mm circle) | Blower, CentrifugalBlower, AxialBlower, Fan, RadialFan, AxialFan |
| Shape_Column | COLUMN_SHAPE | name (ISO number not verified) | column body with dished heads (20 x 100 mm); stretch it with ScaleY | ScaleX 1.0, ScaleY 0.6-1.6 (60-160 mm high); draw beds/trays as markers on it | ProcessColumn |
| Shape_ColumnPackedBed | COLUMN_PACKED_BED_SHAPE | name (ISO number not verified) | packed bed (or adsorbent bed) marker inside a column or vessel: crossed box 20 x 20 mm | ScaleX = column ScaleX, ScaleY = bed height / 20 |  |
| Shape_ColumnTray | COLUMN_TRAY_SHAPE | name (ISO number not verified) | one tray inside a column (downcomer on the right); draw one per tray shown | ScaleX = column ScaleX, ScaleY 1.0; IsMirrored for the downcomer on the left |  |
| Shape_GasFilter | GAS_FILTER_SHAPE | name (ISO number not verified) | filter, gas (also a general filter): box with dashed filter medium | 1.0 (10 x 16 mm) | GasFilter, Filter, LiquidFilter |
| Shape_Silencer | SILENCER_SHAPE | name (ISO number not verified) | silencer (Plant/Piping.Silencer, an inline fitting): ends at x = -6 and 6 | 0.5 inline (ends 3 mm from the centre: fragment valve --class Silencer) |  |
| Shape_AirCooler | AIR_COOLER_SHAPE | name (ISO number not verified) | air cooler (air-cooled heat exchanger) with fan below | 1.0 (30 x 15 mm) | AirCoolingSystem |
| Shape_HeatExchangerGeneral | HEAT_EXCHANGER_GENERAL_SHAPE | name (ISO number not verified) | heat exchanger, cooler or heater, general (circle with a crossing flow path) | 1.0 (15 mm circle) | HeatExchanger, Heater, SpiralHeatExchanger |
| Shape_ShellAndTubeHeatExchanger | SHELL_AND_TUBE_HEAT_EXCHANGER_SHAPE | name (ISO number not verified) | shell-and-tube cooler or heater with fixed tube sheets | 1.0 (35 x 10 mm) |  |
| Shape_ElectricHeater | ELECTRIC_HEATER_SHAPE | name (ISO number not verified) | electric heater: box with heating element and supply | 1.0 (20 x 15 mm) | ElectricHeater |
| Shape_AmbientVaporizer | AMBIENT_VAPORIZER_SHAPE | name (ISO number not verified) | ambient-air vaporizer (finned tubes), class HeatExchanger or AirCoolingSystem | 1.0 (16 x 25 mm) |  |
| Shape_FlatBottomTank | FLAT_BOTTOM_TANK_SHAPE | name (ISO number not verified) | storage tank with flat bottom and cone roof (class Tank) | 1.0-2.0 (30 x 25 mm at 1.0) |  |
| Shape_PlateFinHeatExchanger | PLATE_FIN_HEAT_EXCHANGER_SHAPE | name (ISO number not verified) | plate-fin (brazed aluminium) heat exchanger, class PlateHeatExchanger | 1.0-3.0 (16 x 30 mm at 1.0) |  |
| Shape_GateValve | GATE_VALVE_SHAPE | name (ISO number not verified) | gate valve: two triangles, no dot (ends at x = -5 and 5) | 0.4 inline (ends 2 mm from the centre) |  |
