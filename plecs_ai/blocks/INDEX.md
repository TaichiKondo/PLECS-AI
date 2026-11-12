# ブロックのカタログ（自動生成）

`python -m plecs_ai.harvest` が生成する。手で編集しない。端子の意味は `.claude/skills/plecs/reference/blocks.md` に書く。

端子：番号:in／out（`/wire` は電気、`/magnetic` などはその他の物理領域。無印は信号）。取り込んだファイルの配線で使われていたものだけを示す。

| キー | 種類（Typeまたはライブラリ） | 端子 | パラメータ | 取り込み元 |
|---|---|---|---|---|
| `2_Level_IGBT_Conv` | Components/Electrical/Converters/2-Level IGBT Conv. | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in, 5:in/wire+out/wire, 6:in/wire+out/wire | therm, Rth, T_init | boosted_motor_drive.plecs |
| `2_Pulse_Generator` | Components/Control/Modulators/2-Pulse Generator | 1:in, 2:in, 3:in, 4:out | - | thyristor_converter_2_pulse.plecs |
| `3_Phase_Index_Based_Modulation` | Components/Control/Modulators/3-Phase Index-Based Modulation | 1:out, 2:in, 3:in | config | three_phase_t_type_inverter.plecs |
| `3_Phase_Overmodulation` | Components/Control/Modulators/3-Phase Overmodulation | 1:out, 2:in | - | voltage_source_inverter.plecs |
| `3ph_RRF` | Components/Control/Transformations/3ph->RRF | 1:in, 2:out, 3:in | - | boosted_motor_drive.plecs |
| `3ph_SRF` | Components/Control/Transformations/3ph->SRF | 1:in, 2:out | - | double_fed_induction_generator_wind_turbine.plecs |
| `6_Pulse_Generator` | Components/Control/Modulators/6-Pulse Generator | 1:in, 2:in, 3:in, 4:out | pulsewidth, pulsetype | cycloconverter.plecs |
| `ACVoltageSource` | ACVoltageSource | 1:in/wire+out/wire, 2:in/wire+out/wire | V, w, phi | boost_converter_with_pfc_and_thermal_model.plecs |
| `Abs` | Abs | 1:in, 2:out | - | boosted_motor_drive.plecs |
| `AmbientTemperature` | AmbientTemperature | 1:in/heatpipe+out/heatpipe | AllowStarConnection | boost_converter_with_pfc_and_thermal_model.plecs |
| `Ammeter` | Ammeter | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:out | - | (private model) |
| `AngleSensor` | AngleSensor | 1:in/rotational+out/rotational, 2:out, 3:in/rotational | SecondFlange, theta0 | boosted_motor_drive.plecs |
| `Assert_Dynamic_Upper_Limit` | Components/Assertions/Assert Dynamic Upper Limit | 1:in, 2:in | include_limit, action, message | three_phase_t_type_inverter.plecs |
| `Assert_Range` | Components/Assertions/Assert Range | 1:in | upper_limit, lower_limit, include_limits, action, message | buck_converter_bcm.plecs |
| `Assertion` | Assertion | 1:in | Action, Message, HighlightLevel | half_bridge_llc_converter_with_analysis_tools.plecs |
| `BLDC_Machine` | Components/Electrical/Machines/BLDC Machine | 1:in/wire, 2:in/wire, 3:in/wire, 4:out/rotational | Kc, Ks, R, L0, Lc, Ls, Tc, Ts, J, F, p, wm0, thm0, i0 | brushless_dc_machine.plecs |
| `Blanking_Time` | Components/Control/Modulators/Blanking Time | 1:out, 2:in | tb | boosted_motor_drive.plecs |
| `Blanking_Time_3_Level` | Components/Control/Modulators/Blanking Time (3-Level) | 1:out, 2:in | tb | three_phase_t_type_inverter.plecs |
| `Breaker` | Breaker | 1:in/wire, 2:out/wire, 3:in | s_init, SwitchModel, f_grid | single_phase_pv_inverter_with_partial_shading.plecs |
| `CScript` | CScript | 1:in, 2:in+out, 3:out | DialogGeometry, NumInputs, NumOutputs, NumContStates, NumDiscStates, NumZCSignals, DirectFeedthrough, Ts, Parameters, LangStandard, GnuExtensions, RuntimeCheck, Declarations, StartFcn, OutputFcn, UpdateFcn, DerivativeFcn, TerminateFcn, StoreCustomStateFcn, RestoreCustomStateFcn | boosted_motor_drive.plecs |
| `Capacitor` | Capacitor | 1:in/wire+out/wire, 2:in/wire+out/wire | C, v_init | (private model) |
| `Clock` | Clock | 1:out | - | buck_converter_bcm.plecs |
| `CombinatorialLogic` | CombinatorialLogic | 1:in, 2:out | TruthTable | diode_rectifier_with_pfc.plecs |
| `Comparator` | Comparator | 1:in, 2:in, 3:out | - | (private model) |
| `Constant` | Constant | 1:out | Value, DataType | (private model) |
| `ConstantRelationalOperator` | ConstantRelationalOperator | 1:in, 2:out | Operator, Threshold | bridgeless_boost_pfc_converter.plecs |
| `ConstantTemperature` | ConstantTemperature | 1:out/heatpipe, 2:in/heatpipe | T | buck_converter_with_thermal_model.plecs |
| `ConstantTemperatureGnd` | ConstantTemperatureGnd | 1:in/heatpipe+out/heatpipe | T | boost_converter_with_pfc_and_thermal_model.plecs |
| `Continuous_PID_Controller` | Components/Control/Continuous/Continuous PID Controller | 1:in, 2:out, 6:in, 7:in | cont_type, par_source, kp, ki, kd, kf, ex_reset, x0_source, x0, ex_sat, sat_lim, up_limit, low_limit, aw_method, kbc | (private model) |
| `ControlledForce` | ControlledForce | 1:out/translational, 2:in | SecondFlange, DiscretizationBehavior, StateSpaceInlining | electric_vehicle_with_active_damping.plecs |
| `ControlledRotationalSpeed` | ControlledRotationalSpeed | 1:in/rotational, 2:in | SecondFlange, StateSpaceInlining | look_up_table_based_pmsm.plecs |
| `ControlledTorque` | ControlledTorque | 1:in/rotational+out/rotational, 2:in, 3:in/rotational+out/rotational | SecondFlange, StateSpaceInlining | brushless_dc_machine.plecs |
| `CurrentSource` | CurrentSource | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | DiscretizationBehavior, StateSpaceInlining | (private model) |
| `DCCurrentSource` | DCCurrentSource | 1:out/wire, 2:in/wire | I | multi_phase_current_source_inverter.plecs |
| `DCVoltageSource` | DCVoltageSource | 1:in/wire+out/wire, 2:in/wire+out/wire | V | boost_converter.plecs |
| `DC_Machine` | Components/Electrical/Machines/DC Machine | 1:in/wire, 2:in/wire, 3:in/wire, 4:out/wire, 5:out/rotational | Ra, La, Rf, Lf, Laf, J, F, wm0, thm0, ia0, if0 | dc_motor_drive_with_armature_chopper.plecs |
| `D_Flip_flop` | Components/Control/Logical/D Flip-flop | 1:in, 2:in, 3:out | trigger, x_init | synchronous_buck_converter.plecs |
| `Dead_Zone` | Components/Control/Discontinuous/Dead Zone | 1:in, 2:out | lower, upper | brushless_dc_machine.plecs |
| `Delay` | Delay | 1:in, 2:out | N, X0, Ts | boosted_motor_drive.plecs |
| `Diode` | Diode | 1:in/wire+out/wire, 2:in/wire+out/wire | Vf, Ron, thermal, Rth, Np, T_init, SwitchModel, f_grid | parts_sample.plecs |
| `Diode_Rectifier` | Components/Electrical/Converters/Diode Rectifier | 1:out/wire, 2:out/wire, 3:in/wire, 4:out/wire, 5:out/wire | Vf, Ron, therm, Rth, T_init | synchronous_generator_feeding_a_rectifier.plecs |
| `DiscreteTransferFunction` | DiscreteTransferFunction | 1:in, 2:out | Numerator, Denominator, Ts, X0 | buck_converter_with_digital_controls.plecs |
| `Discrete_PID_Controller` | Components/Control/Discrete/Discrete PID Controller | 1:in, 2:out, 6:in | cont_type, par_source, kp, ki, kd, kf, ex_reset, x0_source, x0, ex_sat, sat_lim, int_method, t_sample, up_limit, low_limit, aw_method, kbc | buck_converter_with_peak_current_control.plecs |
| `Display` | Display | 1:in | Notation, Precision | boost_converter_with_pfc_and_thermal_model.plecs |
| `Drr1` | Components/Electrical/Power Semiconductors/Drr1 | 1:in/wire, 2:in/wire | Vf, Ron, Roff, If0, dIrdt, trr, Irrm, Qrr, Lrr | buck_converter_with_stray_igbt_tail_current.plecs |
| `EdgeDetection` | EdgeDetection | 1:in, 2:out | Direction | buck_converter_bcm.plecs |
| `Enable` | Enable | - | Index, DataType, Width, ShowOutput | power_split_hybrid_vehicle_system.plecs |
| `FCHB1` | Components/Electrical/Power Modules/FCHB1 | 1:in, 2:in/wire, 3:in/wire, 4:in, 5:in/wire+out/wire, 6:in/wire+out/wire, 7:in/wire+out/wire | semiSymbol, N, assert, Configuration | flying_capacitor_dcdc_converter.plecs |
| `ForceSensor` | ForceSensor | 1:in/translational, 2:out, 3:in/translational+out/translational | SecondFlange | electric_vehicle_with_active_damping.plecs |
| `Fourier_Transform` | Components/Control/Filters/Fourier Transform | 1:in, 2:out | ts, fs, n | single_phase_active_filter.plecs |
| `From` | From | 1:out | Tag, Visibility, NoMatchingCounterpartAction, CustomMessage, HighlightLevel | (private model) |
| `FsmBlock` | FsmBlock | 1:out, 2:in+out, 3:in+out, 4:in+out, 5:in+out, 6:in+out, 7:in, 8:in, 9:in, 10:in | InputVariables, InputTypes, InternalConstants, InternalConstantValues, InternalVariables, InternalVariableValues, OutputVariables, Declarations, TransitionOrder, SampleTime, Animate | buck_converter_bcm.plecs |
| `Function` | Function | 1:in, 2:out | f(u) | boost_converter_with_pfc_and_thermal_model.plecs |
| `Gain` | Gain | 1:in, 2:out | K, Multiplication, OutputDataType, DataTypeOverflowMode, GainDataType | parts_sample.plecs |
| `Gear` | Gear | 1:in/rotational+out/rotational, 2:in/rotational | g | direct_flux_vector_control.plecs |
| `Goto` | Goto | 1:in | Tag, Visibility, NoMatchingCounterpartAction, CustomMessage, HighlightLevel | (private model) |
| `Ground` | Ground | 1:in/wire+out/wire | - | buck_converter_with_parameter_sweep.plecs |
| `HB1` | Components/Electrical/Power Modules/HB1 | 1:in, 2:in/wire+out/wire, 3:in/wire, 4:in/wire+out/wire, 5:in | semiSymbol, assert, Configuration | direct_flux_vector_control.plecs |
| `HeatFlowMeter` | HeatFlowMeter | 1:in/heatpipe+out/heatpipe, 2:in/heatpipe+out/heatpipe | - | buck_converter_with_thermal_model.plecs |
| `HeatSink` | HeatSink | 1:in/heatpipe+out/heatpipe, 2:in/heatpipe | Cth, T_init, Width | boost_converter_with_pfc_and_thermal_model.plecs |
| `IGBT2` | Components/Electrical/Power Semiconductors/IGBT2 | 1:in/wire, 2:in, 3:in/wire | Vces, Ic, Vf, Ron, Roff, tr, tf, Lsig, i_init | buck_converter_with_stray_igbt_tail_current.plecs |
| `Igbt` | Igbt | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | Vf, Ron, s_init, thermal, Rth, T_init | bridgeless_boost_pfc_converter.plecs |
| `IgbtWithDiode` | IgbtWithDiode | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | s_init, thermal, Rth, T_init | boosted_motor_drive.plecs |
| `Inductor` | Inductor | 1:in/wire+out/wire, 2:in/wire+out/wire | L, i_init | (private model) |
| `Inertia` | Inertia | 1:in/rotational+out/rotational, 2:in/rotational+out/rotational | J, w0, theta0 | boosted_motor_drive.plecs |
| `Input` | Input | 1:out | Index, Width | boost_converter_with_pfc_and_thermal_model.plecs |
| `Integrator` | Integrator | 1:in, 2:out, 3:in, 4:out | ExternalReset, InitialConditionSource, x0, ShowStatePort, EnableWrapping, UpperLimit, LowerLimit | parts_sample.plecs |
| `Label` | Label | 1:in/wire+out/wire | Tag, Visibility | buck_converter_with_voltage_controls.plecs |
| `Lim_Op_Amp` | Components/Electrical/Electronics/Lim. Op-Amp | 1:out/wire, 2:out/wire, 3:out/wire, 4:out/wire | A, Vlim | operational_amplifier_circuits.plecs |
| `LogicalOperator` | LogicalOperator | 1:out, 2:in, 3:in, 4:in | Operator, Inputs | (private model) |
| `Lookup1D` | Lookup1D | 1:in, 2:out | x, f(x), ZeroCrossingSignals | boost_converter_with_pfc_and_thermal_model.plecs |
| `Lookup2D` | Lookup2D | 1:in, 2:in, 3:out | x, y, f(x,y), ZeroCrossingSignals | double_fed_induction_generator_wind_turbine.plecs |
| `Lookup3D` | Lookup3D | 1:in, 2:in, 3:in, 4:out | x, y, z, f(x,y,z), ZeroCrossingSignals | single_phase_pv_inverter.plecs |
| `Loop_Gain_Meter` | Components/Control/Small Signal Analysis/Loop Gain Meter | 1:in, 2:out | invert | buck_converter_with_loop_gain_analysis.plecs |
| `MFB1` | Components/Electrical/Power Modules/MFB1 | 1:in, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire, 5:in, 6:in/wire, 7:in, 8:in | semiSymbol, N, assert, Configuration | cascaded_multilevel_inverter.plecs |
| `MHB1` | Components/Electrical/Power Modules/MHB1 | 1:in, 2:in/wire, 3:in/wire+out/wire, 4:in/wire+out/wire, 5:in, 6:in/wire+out/wire | semiSymbol, N, assert, switchModel, combineRevDiode, thermalIgbtDiode, thermalIgbt, thermalMosfetDiode, thermalMosfet, thermalRevDiode, Configuration | hvdc_transmission_system_with_mmcs.plecs |
| `MagneticInterface` | MagneticInterface | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/magnetic+out/magnetic, 4:in/magnetic+out/magnetic | n, Polarity | cuk_converter_with_integrated_magnetics.plecs |
| `MagneticPermeance` | MagneticPermeance | 1:in/magnetic+out/magnetic, 2:out/magnetic | P, F_init | double_fed_induction_generator_wind_turbine.plecs |
| `MagneticResistance` | MagneticResistance | 1:in/magnetic, 2:in/magnetic | R | double_fed_induction_generator_wind_turbine.plecs |
| `ManualSignalSwitch` | ManualSignalSwitch | 1:out, 2:in, 3:in | SwitchState | (private model) |
| `ManualSwitch` | ManualSwitch | 1:in/wire, 2:in/wire | s | single_phase_active_filter.plecs |
| `Mass` | Mass | 1:in/translational+out/translational, 2:out/translational | m, v0, x0 | electric_vehicle_with_active_damping.plecs |
| `Math` | Math | 1:out, 2:in, 3:in | Operator | direct_flux_vector_control.plecs |
| `Memory` | Memory | 1:in, 2:out | X0 | boost_converter_with_pfc_and_thermal_model.plecs |
| `MinMax` | MinMax | 1:out, 2:in, 3:in, 4:in | Operation, Inputs | boosted_motor_drive.plecs |
| `Monoflop` | Monoflop | 1:in, 2:out | Trigger, DurationSource, Duration, Rounding | series_capacitor_buck_converter.plecs |
| `Mosfet` | Mosfet | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | Ron, s_init, thermal, Rth, T_init | boost_converter.plecs |
| `MosfetWithDiode` | MosfetWithDiode | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | Ron, s_init, thermal, Rth, Np, T_init | (private model) |
| `Moving_Average` | Components/Control/Filters/Moving Average | 1:out, 2:in | x0, T_period, buffer_size | (private model) |
| `MutInductor` | MutInductor | 1:in/wire, 2:out/wire, 3:in/wire, 4:in/wire+out/wire | Windings, L, i_init | boost_converter_with_pfc_and_thermal_model.plecs |
| `NPC1` | Components/Electrical/Power Modules/NPC1 | 1:in, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire, 5:in, 6:in, 7:in, 8:in/wire+out/wire | semiSymbol, assert, switchModel, combineRevDiode, thermalIgbtDiode, thermalIgbt, thermalMosfetDiode, thermalMosfet, thermalRevDiode, thermalDiode, Configuration | npc_converter.plecs |
| `Netlist` | Netlist | 1:in/wire+out/wire, 2:in/wire, 3:in/wire | Netlist | demo_plecs_spice.plecs |
| `Non_Excited_SM` | Components/Electrical/Machines/Non-Excited SM | 1:in/wire, 2:in/wire, 3:in/wire, 4:in/rotational | R, Lls, p, is0, Id_r, Iq_r, Psid_r, Psiq_r, Lmidd_r, Lmidq_r, Lmiqq_r, Nxdq, icheck, J, F, wm0, thm0 | look_up_table_based_pmsm.plecs |
| `Offset` | Offset | 1:in, 2:out | Offset, DataType, DataTypeOverflowMode | buck_converter_bcm.plecs |
| `Op_Amp` | Components/Electrical/Electronics/Op-Amp | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire+out/wire | A | buck_converter_with_parameter_sweep.plecs |
| `Output` | Output | 1:in | Index, Width | (private model) |
| `P_air` | Components/Magnetic/Components/P_air | 1:in/magnetic+out/magnetic, 2:in/magnetic+out/magnetic | A, l, F_init | cuk_converter_with_integrated_magnetics.plecs |
| `P_leak` | Components/Magnetic/Components/P_leak | 1:in/magnetic+out/magnetic, 2:in/magnetic | P, F_init | cuk_converter_with_integrated_magnetics.plecs |
| `P_lin` | Components/Magnetic/Components/P_lin | 1:in/magnetic+out/magnetic, 2:in/magnetic+out/magnetic | A, l, mu_r, F_init | phase_shift_dcdc_converter_with_integrated_magnetics.plecs |
| `P_sat` | Components/Magnetic/Components/P_sat | 1:in/magnetic+out/magnetic, 2:in/magnetic+out/magnetic | fitting, A, l, mu_r_unsat, mu_r_sat, B_sat, F_init | cuk_converter_with_integrated_magnetics.plecs |
| `Peak_Current_Controller` | Components/Control/Modulators/Peak Current Controller | 1:in, 2:in, 3:out | fs, dmin, dmax, Islope | buck_converter_with_cascaded_controls.plecs |
| `PeriodicAverage` | PeriodicAverage | 1:out, 2:in | T_average | parts_sample.plecs |
| `PeriodicImpulseAverage` | PeriodicImpulseAverage | 1:out, 2:in | T_average | parts_sample.plecs |
| `Periodic_Average` | Components/Control/Filters/Periodic Average | 1:out, 2:in | T_average | multiphase_synchronous_buck_converter.plecs |
| `Perm_Magnet_SM` | Components/Electrical/Machines/Perm.-Magnet SM | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/rotational+out/rotational | configuration, R, L, phi, J, F, p, wm0, thm0, is0 | boosted_motor_drive.plecs |
| `PiSectionLine` | PiSectionLine | 1:in/wire, 2:in/wire+out/wire, 3:in/wire | L, R, C, G, l, n, v_init | hvdc_transmission_system_with_mmcs.plecs |
| `Planetary_Gear_Set` | Components/Mechanical/Rotational/Components/Planetary Gear Set | 1:in/rotational, 2:in/rotational, 3:in/rotational | Ns, Np, Nr, J_planet, w_init_planet | power_split_hybrid_vehicle_system.plecs |
| `PlecsProbe` | PlecsProbe | 1:out | - | boost_converter_with_pfc_and_thermal_model.plecs |
| `Polar_rect` | Components/Control/Transformations/Polar->rect | 1:in, 2:out | - | boosted_motor_drive.plecs |
| `Port` | Port | 1:in/wire+out/wire | Index, Width | boost_converter_with_pfc_and_thermal_model.plecs |
| `PositionSensor` | PositionSensor | 1:in/translational, 2:out | SecondFlange, x0 | servo_drive_with_optimum_braking.plecs |
| `Product` | Product | 1:out, 2:in, 3:in, 4:in | IconShape, Inputs, DataType, DataTypeOverflowMode | (private model) |
| `PulseGenerator` | PulseGenerator | 1:out | Hi, Lo, f, DutyCycle, Delay, DataType | boost_converter.plecs |
| `Pulse_Delay` | Components/Control/Delays/Pulse Delay | 1:out, 2:in | T_d, y_init, buffer_size | buck_converter_bcm.plecs |
| `Quantizer` | Components/Control/Discontinuous/Quantizer | 1:in, 2:out | q, stepDetection | single_phase_pv_inverter_with_partial_shading.plecs |
| `RRF_3ph` | Components/Control/Transformations/RRF->3ph | 1:in, 2:out, 3:in | - | hvdc_transmission_system_with_mmcs.plecs |
| `RRF_SRF` | Components/Control/Transformations/RRF->SRF | 1:in, 2:out, 3:in | - | boosted_motor_drive.plecs |
| `Rack_and_Pinion` | Components/Mechanical/Translational/Components/Rack and Pinion | 1:out/rotational, 2:out/translational | R | servo_drive_with_optimum_braking.plecs |
| `Ramp` | Components/Control/Sources/Ramp | 1:out | slope, start, X0, XFinal | (private model) |
| `RateLimiter` | RateLimiter | 1:in, 2:out | RisingRateLimit, FallingRateLimit, SampleTimeMode | demo_plecs_spice.plecs |
| `Rect_polar` | Components/Control/Transformations/Rect->polar | 1:in, 2:out | - | boosted_motor_drive.plecs |
| `RelationalOperator` | RelationalOperator | 1:in, 2:in, 3:out | Operator | boost_converter_with_pfc_and_thermal_model.plecs |
| `Relay` | Relay | 1:in, 2:out | OnSwitchValue, OffSwitchValue, OnOutputValue, OffOutputValue, InitialState, DataType | brushless_dc_machine.plecs |
| `Resistor` | Resistor | 1:in/wire+out/wire, 2:in/wire+out/wire | R | (private model) |
| `RotationalBacklash` | RotationalBacklash | 1:in/rotational+out/rotational, 2:in/rotational+out/rotational | b, theta0 | servo_drive_with_optimum_braking.plecs |
| `RotationalClutch` | RotationalClutch | 1:out/rotational, 2:out/rotational, 3:in | s_init, theta0 | two_axle_vehicle_with_driving_profile.plecs |
| `RotationalDamper` | RotationalDamper | 1:in/rotational+out/rotational, 2:in/rotational+out/rotational | D, theta0 | boosted_motor_drive.plecs |
| `RotationalFriction` | RotationalFriction | 1:in/rotational, 2:in/rotational+out/rotational | tau_brk, tau_C, c_v | electric_vehicle_with_active_damping.plecs |
| `RotationalPort` | RotationalPort | 1:in/rotational+out/rotational | Index, Width | direct_flux_vector_control.plecs |
| `RotationalReference` | RotationalReference | 1:in/rotational+out/rotational | - | brushless_dc_machine.plecs |
| `RotationalSpeedSensor` | RotationalSpeedSensor | 1:in/rotational+out/rotational, 2:out, 3:in/rotational+out/rotational | SecondFlange | boosted_motor_drive.plecs |
| `RotationalSpring` | RotationalSpring | 1:in/rotational+out/rotational, 2:in/rotational+out/rotational | c, theta0, dtheta0 | boosted_motor_drive.plecs |
| `Rounding` | Rounding | 1:in, 2:out | Operation, DataType, DataTypeOverflowMode | llc_variable_frequency_resonant_converter.plecs |
| `SRF_3ph` | Components/Control/Transformations/SRF->3ph | 1:in, 2:out | - | double_fed_induction_generator_wind_turbine.plecs |
| `SRF_RRF` | Components/Control/Transformations/SRF->RRF | 1:in, 2:out, 3:in | - | boosted_motor_drive.plecs |
| `SR_Flip_flop` | Components/Control/Logical/SR Flip-flop | 1:in, 2:in, 3:out | x_init | power_split_hybrid_vehicle_system.plecs |
| `Salient_Pole_SM` | Components/Electrical/Machines/Salient-Pole SM | 1:in/wire, 2:in/wire, 3:out/wire, 4:in/wire, 5:in/wire, 6:out/rotational | configuration, Rs, Lls, Lm0, Lmdsat, psiT, fT, Rf, Llf, Rk, Llk, ue, J, F, p, wm0, thm0, is0, if0, psis0 | synchronous_generator_feeding_a_rectifier.plecs |
| `Saturation` | Saturation | 1:in, 2:out | UpperLimit, LowerLimit | parts_sample.plecs |
| `Sawtooth_PWM` | Components/Control/Modulators/Sawtooth PWM | 1:out, 2:in | config, ramp, fc, carrier_phaseshift, carrier_limits, output_values | type2_and_type3_compensator_analysis_for_power_supplies.plecs |
| `Scope` | Scope | 1:in, 2:in, 3:in, 4:in, 5:in, 6:in, 7:in | - | (private model) |
| `SignalDemux` | SignalDemux | 1:in, 2:out, 3:out, 4:out, 5:out, 6:out, 7:out, 8:out, 9:out, 10:out, 11:out | Width | boost_converter_with_pfc_and_thermal_model.plecs |
| `SignalMux` | SignalMux | 1:out, 2:in, 3:in, 4:in, 5:in, 6:in, 7:in, 8:in, 9:in, 10:in, 11:in | Width | (private model) |
| `SignalSelector` | SignalSelector | 1:in, 2:out | InputWidth, OutputIndices | boosted_motor_drive.plecs |
| `SignalSwitch` | SignalSwitch | 1:out, 2:in, 3:in, 4:in | Criteria, Threshold | parts_sample.plecs |
| `Signum` | Signum | 1:in, 2:out | - | brushless_dc_machine.plecs |
| `SineGenerator` | SineGenerator | 1:out | Amplitude, Bias, Frequency, Phase, Units | parts_sample.plecs |
| `Sine_Wave` | Deprecated/Control/Sources/Sine Wave | 1:out | Amplitude, Bias, Frequency, Phase, Units | cascaded_multilevel_inverter.plecs |
| `Single_Phase_PLL` | Components/Control/Continuous/Single-Phase PLL | 1:in, 5:out | type, f0, Vpk, theta0, sincos, units, contr_design, kp, ki, kANF, kSOGI | single_phase_active_filter.plecs |
| `Slip_Ring_IM` | Components/Electrical/Machines/Slip-Ring IM | 1:in/wire, 2:out/wire, 3:in/wire, 4:in/wire, 5:out/wire, 6:in/wire, 7:in/rotational | Rs, Lls, Rr, Llr, Lm, ue, J, F, p, wm0, thm0, is0, psisdq0 | double_fed_induction_generator_wind_turbine.plecs |
| `SmallSignalPerturbation` | SmallSignalPerturbation | 1:out, 2:in | ShowInput | buck_converter_with_analysis_tools.plecs |
| `SmallSignalResponse` | SmallSignalResponse | 1:in, 2:in | ShowReference, InvertReference | buck_converter_with_analysis_tools.plecs |
| `Space_Vector_PWM` | Components/Control/Modulators/Space Vector PWM | 1:out, 2:in, 3:in | pattern, fs, output_values | boosted_motor_drive.plecs |
| `Squirrel_Cage_IM` | Components/Electrical/Machines/Squirrel-Cage IM | 1:in/wire, 2:out/wire, 3:out/wire, 4:out/rotational | Rs, Lls, Rr, Llr, Lm, J, F, p, wm0, thm0, is0, psisdq0 | induction_machine_drive_controlled_with_dtc.plecs |
| `Step` | Step | 1:out | Time, Before, After, DataType | parts_sample.plecs |
| `Sum` | Sum | 1:out, 2:in, 3:in, 4:in, 5:in | IconShape, Inputs, DataType, DataTypeOverflowMode | (private model) |
| `Switch` | Switch | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | s_init, SwitchModel, f_grid | buck_converter_bcm.plecs |
| `SwitchLossCalculator` | SwitchLossCalculator | 1:out | T_average, ConductionLoss, SwitchingLoss, TurnOnLoss, TurnOffLoss, TotalLoss, GroupTypes | boost_converter_with_pfc_and_thermal_model.plecs |
| `Switched_Reluctance_Machine_10_8` | Components/Electrical/Machines/Switched Reluctance Machine (10\\/8) | 1:in/wire, 2:in/wire+out/wire, 3:out/rotational | R, Lu, La, Lsat, Psisat, J, F, wm0, thm0, i0 | switched_reluctance_machine_10_8.plecs |
| `Switched_Reluctance_Machine_6_4` | Components/Electrical/Machines/Switched Reluctance Machine (6\\/4) | 1:in/wire, 2:in/wire+out/wire, 3:out/rotational | R, Lu, La, Lsat, Psisat, J, F, wm0, thm0, i0 | switched_reluctance_machine_6_4.plecs |
| `Switched_Reluctance_Machine_8_6` | Components/Electrical/Machines/Switched Reluctance Machine (8\\/6) | 1:in/wire, 2:in/wire+out/wire, 3:out/rotational | R, Lu, La, Lsat, Psisat, J, F, wm0, thm0, i0 | switched_reluctance_machine_8_6.plecs |
| `Symmetrical_PWM` | Components/Control/Modulators/Symmetrical PWM | 1:out, 2:in | sampling, fc, carrier_phaseshift, carrier_limits, output_values | boosted_motor_drive.plecs |
| `Symmetrical_PWM_3_Level` | Components/Control/Modulators/Symmetrical PWM (3-Level) | 1:out, 2:in | sampling, fc, offset, input_limits, phic | three_phase_t_type_inverter.plecs |
| `ThermalChain` | ThermalChain | 1:in/heatpipe+out/heatpipe, 2:in/heatpipe+out/heatpipe | Rth, Cth, T_init | boost_converter_with_pfc_and_thermal_model.plecs |
| `ThermalGround` | ThermalGround | 1:out/heatpipe | - | buck_converter_with_thermal_model.plecs |
| `ThermalResistor` | ThermalResistor | 1:in/heatpipe+out/heatpipe, 2:in/heatpipe+out/heatpipe | Rth | boost_converter_with_pfc_and_thermal_model.plecs |
| `ThreePhaseMeter` | ThreePhaseMeter | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire+out/wire, 5:in/wire+out/wire, 6:in/wire+out/wire, 7:out, 8:out, 9:in/wire+out/wire | voltage | boosted_motor_drive.plecs |
| `ThreePhaseVoltageSource` | ThreePhaseVoltageSource | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire+out/wire | V, w, phi, neutral | cycloconverter.plecs |
| `Three_Phase_PLL` | Components/Control/Continuous/Three-Phase PLL | 1:in, 2:out | type, f0, Vpk, theta0, units, contr_design, kp, ki, k | cycloconverter.plecs |
| `Thyristor` | Thyristor | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | Vf, Ron, s_init, thermal, Rth, T_init | plant_code_generation.plecs |
| `Thyristor_Inverter` | Components/Electrical/Converters/Thyristor Inverter | 1:in/wire, 2:in/wire, 3:in/wire, 4:in, 5:in/wire, 6:in/wire | Vf, Ron, therm, Rth, T_init | cycloconverter.plecs |
| `Thyristor_Rectifier` | Components/Electrical/Converters/Thyristor Rectifier | 1:out/wire, 2:out/wire, 3:out/wire, 4:in, 5:out/wire, 6:in/wire+out/wire | Vf, Ron, therm, Rth, T_init | cycloconverter.plecs |
| `Total_Harmonic_Distortion` | Components/Control/Filters/Total Harmonic Distortion | 1:in, 2:out | ts, fs | single_phase_active_filter.plecs |
| `TransferFunction` | TransferFunction | 1:in, 2:out | Numerator, Denominator, X0 | boost_converter_with_pfc_and_thermal_model.plecs |
| `Transformer` | Transformer | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire+out/wire, 5:in/wire+out/wire, 6:in/wire+out/wire, 7:in/wire, 8:in/wire | Windings, n, Polarity, Lm, im0 | dual_active_bridge_converter.plecs |
| `TranslationalFriction` | TranslationalFriction | 1:in/translational+out/translational, 2:in/translational | F_brk, F_C, c_v | electric_vehicle_with_active_damping.plecs |
| `TranslationalHardStop` | TranslationalHardStop | 1:in/translational, 2:out/translational | x_max, x_min, x0 | servo_drive_with_optimum_braking.plecs |
| `TranslationalPort` | TranslationalPort | 1:in/translational | Index, Width | electric_vehicle_with_active_damping.plecs |
| `TranslationalReference` | TranslationalReference | 1:in/translational+out/translational | - | electric_vehicle_with_active_damping.plecs |
| `TranslationalSpeedSensor` | TranslationalSpeedSensor | 1:in/translational+out/translational, 2:out | SecondFlange | electric_vehicle_with_active_damping.plecs |
| `Transmission_Line` | Components/Electrical/Passive Components/Transmission Line | 1:in/wire, 2:in/wire, 3:out/wire, 4:out/wire, 5:out/wire, 6:in/wire, 7:out/wire | L_, M_, R_, C_ph2n_, C_ph2ph_, l, n, Configuration | double_fed_induction_generator_wind_turbine.plecs |
| `TriangleGenerator` | TriangleGenerator | 1:out | Min, Max, f, DutyCycle, Delay | (private model) |
| `Trigger` | Trigger | - | Index, Width, TriggerType, ShowOutput | buck_converter_bcm.plecs |
| `Trigonometry` | Trigonometry | 1:in, 2:out | Operator, Unit | brushless_dc_machine.plecs |
| `Turn_on_Delay` | Components/Control/Delays/Turn-on Delay | 1:in, 2:out | DeadTimeSource, T_d, Rounding | parts_sample.plecs |
| `VSI1` | Components/Electrical/Power Modules/VSI1 | 1:in, 2:out/wire, 3:out/wire, 4:out/wire, 5:in, 6:in/wire, 7:in, 8:in, 9:in/wire, 10:in, 11:in | semiSymbol, assert, switchModel, Configuration | three_phase_motor_drive_with_analysis_tools.plecs |
| `Variable_Frequency_PWM` | Components/Control/Modulators/Variable Frequency PWM | 1:in, 2:in, 3:out | CarrierType, Sampling, Frequency, CarrierLimits, OutputValues | half_bridge_llc_converter_with_analysis_tools.plecs |
| `Variable_Phase_PWM` | Components/Control/Modulators/Variable Phase PWM | 1:in, 2:out, 3:in | CarrierType, Sampling, Frequency, CarrierLimits, OutputValues | dual_active_bridge_converter.plecs |
| `VoltageSource` | VoltageSource | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in | DiscretizationBehavior, StateSpaceInlining | (private model) |
| `Voltmeter` | Voltmeter | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:out | - | (private model) |
| `WireMux` | WireMux | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 4:in/wire+out/wire, 5:in/wire, 6:in/wire | Width | microgrid_in_island_operation.plecs |
| `WireSelector` | WireSelector | 1:in/wire+out/wire, 2:in/wire+out/wire | InputWidth, OutputIndices | multiphase_synchronous_buck_converter.plecs |
| `XYPlot` | XYPlot | 1:in, 2:in | - | double_fed_induction_generator_wind_turbine.plecs |
| `Yd_Trafo` | Components/Electrical/Transformers/Yd Trafo | 1:in/wire, 2:in/wire, 3:in/wire, 4:in/wire, 5:out/wire, 6:out/wire, 7:out/wire | L, R, n, im, phim, Rfe, legs, phaseshift, i1, i2 | wind_power_system_pmsg.plecs |
| `Yy_Trafo` | Components/Electrical/Transformers/Yy Trafo | 1:in/wire+out/wire, 2:in/wire+out/wire, 3:in/wire+out/wire, 5:in/wire+out/wire, 6:in/wire+out/wire, 7:in/wire+out/wire | L, R, n, im, phim, Rfe, legs, phaseshift, i1, i2 | cycloconverter.plecs |
| `ZeroOrderHold` | ZeroOrderHold | 1:in, 2:out | Ts | parts_sample.plecs |
