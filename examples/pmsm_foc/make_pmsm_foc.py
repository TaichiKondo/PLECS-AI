"""(Kept as the record of how pmsm_foc.plecs was first generated. The user
has since fixed block orientation in PLECS, so do not re-run; continue from
the saved file, see make_pmsm_foc_v2.py.)

Build pmsm_foc.plecs from scratch: speed-controlled PMSM with field
oriented control (id = 0), 2-level inverter and sine-triangle PWM.

Block conventions used here are confirmed by tests/block_tests.py
(abc_to_dq, dq_to_abc, two_level_converter, pmsm_*, symmetrical_pwm,
signal_demux).
"""
from plecs_ai.build import Model

INIT = """% PMSM vector control (id = 0). Edited by make_pmsm_foc.py
% Tune with ModelVars on the variables the blocks use directly
% (Kp_i, Ki_i, Kp_w, Ki_w, ...). Derived values are NOT recomputed.

% DC link and PWM
Vdc = 300
fsw = 10e3

% Machine (same data as the PLECS demo boosted_motor_drive)
Rs = 0.62
Ld = 4.14e-3
Lq = 4.14e-3
phi = 0.101
pp = 4
J = 1e-3
Fv = 1e-4
Kt = 1.5*pp*phi

% Current loops: PI zero cancels the stator time constant
wc_i = 2*pi*1000
Kp_i = wc_i*Lq
Ki_i = wc_i*Rs
V_lim = Vdc/2
Kbc_i = wc_i

% Speed loop
wc_w = 2*pi*50
Kp_w = wc_w*J/Kt
Ki_w = Kp_w*wc_w/4
Iq_max = 10
Kbc_w = wc_w
% Slew limit on the iq reference: a step would saturate the current PI
% and leave a slow L/R tail (see README)
diq_max = 1e4

% Test sequence: speed step, then load torque step
w_ref = 1000*2*pi/60
t_w = 0.01
T_load = 3
t_load = 0.15"""

m = Model("pmsm_foc", time_span=0.25, max_step=1e-5)
m.init(INIT)

PI = "Continuous_PID_Controller"


def pi(name, pos, kp, ki, lim, kbc):
    return m.add(PI, name, pos, {
        "cont_type": "3", "kp": kp, "ki": ki, "x0": "0", "up_limit": lim,
        "low_limit": "-" + lim, "aw_method": "2", "kbc": kbc})


def sum_(name, pos, signs="|+-"):
    return m.add("Sum", name, pos, {"Inputs": signs, "IconShape": "2"},
                 show_name=False)


# ---- power stage -----------------------------------------------------------
m.frame(40, 70, 830, 370, "Power stage")
m.add("DCVoltageSource", "Vdc", (90, 170), {"V": "Vdc"}, direction="down",
      flipped=False, label="west")
m.add("2_Level_IGBT_Conv", "Inverter", (230, 170), {}, direction="up",
      flipped=False, label="south")
m.wire("Vdc", 1, "Inverter", 5, [(90, 95), (230, 95)], kind="Wire")
m.wire("Vdc", 2, "Inverter", 6, [(90, 245), (230, 245)], kind="Wire")
m.from_("gates", (175, 125), direction="right")
m.wire("From_gates", 1, "Inverter", 4, [(245, 125)])

for k, (ph, y) in enumerate([("a", 120), ("b", 170), ("c", 220)]):
    am = m.add("Ammeter", "Am" + ph, (360, y), {}, direction="right",
               label="south")
    m.wire("Inverter", 1 + k, am, 1, [(290, 160 + 10 * k), (290, y)], kind="Wire")
    m.wire(am, 2, "PMSM", 1 + k, [(470, y), (470, 160 + 10 * k)], kind="Wire")

m.add("Perm_Magnet_SM", "PMSM", (530, 170), {
    "configuration": "2", "R": "Rs", "L": "[Ld Lq]", "phi": "phi", "J": "J",
    "F": "Fv", "p": "pp", "wm0": "0", "thm0": "0", "is0": "[0 0]"},
    direction="up", flipped=False, label="north")
m.add("RotationalSpeedSensor", "Speed", (640, 250), {"SecondFlange": "1"},
      direction="right", flipped=False, label="south")
m.add("AngleSensor", "Angle", (640, 310), {"SecondFlange": "1", "theta0": "0"},
      direction="right", flipped=False, label="south")
m.add("ControlledTorque", "Load", (640, 140), {"SecondFlange": "1"},
      direction="right", flipped=False, label="north")
m.node("PMSM", 4, [("Load", 1, [(600, 200), (600, 140)]),
                   ("Speed", 1, [(600, 250)]),
                   ("Angle", 1, [(600, 200), (600, 310)])],
       kind="Rotational", points=[(600, 200)])
m.add("Step", "T_load", (720, 100), {"Time": "t_load", "Before": "0",
                                      "After": "-T_load"}, label="north")
m.wire("T_load", 1, "Load", 2)
m.goto("wm", (790, 250), "Speed", 2)
m.add("Gain", "pp_theta", (720, 310), {"K": "pp"}, label="south")
m.wire("Angle", 2, "pp_theta", 1)
m.goto("theta_e", (790, 310), "pp_theta", 2)

# current measurement -> dq
m.add("SignalMux", "Iabc", (390, 320), {"Width": "3"}, show_name=False)
for k, ph in enumerate("abc"):
    m.goto("i" + ph, (390, 95 + 50 * k), "Am" + ph, 3)
    m.from_("i" + ph, (330, 310 + 10 * k), "Iabc", 2 + k)
m.add("3ph_RRF", "abc2dq", (460, 320), {}, label="south")
m.wire("Iabc", 1, "abc2dq", 1)
m.from_("theta_e", (400, 345), "abc2dq", 3, suffix="1")
m.add("SignalDemux", "Idq", (520, 320), {"Width": "2"}, flipped=False,
      show_name=False)
m.wire("abc2dq", 2, "Idq", 1)
m.goto("id", (570, 315), "Idq", 2)
m.goto("iq", (570, 325), "Idq", 3)

# ---- controller ------------------------------------------------------------
m.frame(40, 420, 1030, 830, "Vector control")
# d axis (top row)
m.add("Constant", "id_ref", (260, 470), {"Value": "0"}, label="south")
sum_("Sum_d", (330, 470))
m.wire("id_ref", 1, "Sum_d", 2)
m.from_("id", (330, 525), "Sum_d", 3, direction="up", label="east")
pi("PI_d", (430, 470), "Kp_i", "Ki_i", "V_lim", "Kbc_i")
m.wire("Sum_d", 1, "PI_d", 1)
sum_("Sum_vd", (530, 470))
m.wire("PI_d", 2, "Sum_vd", 2)
m.from_("vd_ff", (530, 525), "Sum_vd", 3, direction="up", label="east")

# q axis (bottom row) with speed loop in front
m.add("Step", "w_ref", (60, 590), {"Time": "t_w", "Before": "0",
                                    "After": "w_ref"}, label="south")
sum_("Sum_w", (130, 590))
m.node("w_ref", 1, [("Sum_w", 2), ("Goto_w_ref", 1, [(95, 545)])],
       points=[(95, 590)])
m.add("Goto", "Goto_w_ref", (115, 545), {"Tag": "w_ref"}, show_name=False)
m.from_("wm", (130, 645), "Sum_w", 3, direction="up", label="east")
pi("PI_w", (210, 590), "Kp_w", "Ki_w", "Iq_max", "Kbc_w")
m.wire("Sum_w", 1, "PI_w", 1)
m.add("RateLimiter", "Iq_slew", (285, 590), {
    "RisingRateLimit": "diq_max", "FallingRateLimit": "-diq_max",
    "SampleTimeMode": "2"}, direction="right", label="south")
m.wire("PI_w", 2, "Iq_slew", 1)
sum_("Sum_q", (330, 590))
m.node("Iq_slew", 2, [("Sum_q", 2), ("Goto_iq_ref", 1, [(310, 545)])],
       points=[(310, 590)])
m.add("Goto", "Goto_iq_ref", (290, 545), {"Tag": "iq_ref"}, show_name=False,
      direction="left")
m.from_("iq", (330, 645), "Sum_q", 3, direction="up", label="east")
pi("PI_q", (430, 590), "Kp_i", "Ki_i", "V_lim", "Kbc_i")
m.wire("Sum_q", 1, "PI_q", 1)
sum_("Sum_vq", (530, 590), "|++")
m.wire("PI_q", 2, "Sum_vq", 2)
m.from_("vq_ff", (530, 645), "Sum_vq", 3, direction="up", label="east")

# dq -> abc -> modulation -> PWM
m.add("SignalMux", "Vdq", (600, 530), {"Width": "2"}, show_name=False)
m.wire("Sum_vd", 1, "Vdq", 2, [(570, 470), (570, 520)])
m.wire("Sum_vq", 1, "Vdq", 3, [(570, 590), (570, 540)])
m.add("RRF_3ph", "dq2abc", (680, 530), {}, label="south")
m.wire("Vdq", 1, "dq2abc", 1, [(640, 530), (640, 525)])
m.from_("theta_e", (630, 560), "dq2abc", 3, suffix="2")
m.add("Gain", "Modulation", (760, 530), {"K": "2/Vdc"}, label="south")
m.wire("dq2abc", 2, "Modulation", 1)
m.add("Symmetrical_PWM", "PWM", (850, 530), {
    "sampling": "1", "fc": "fsw", "carrier_phaseshift": "0",
    "carrier_limits": "[-1 1]", "output_values": "[-1 1]"}, label="south")
m.wire("Modulation", 2, "PWM", 2)
m.goto("gates", (940, 530), "PWM", 1)

# decoupling feed-forward: vd_ff = -we*Lq*iq, vq_ff = we*(Ld*id + phi)
m.text(["Decoupling: vd_ff = -we Lq iq,  vq_ff = we (Ld id + phi)"], (330, 715))
m.add("Gain", "pp_w", (130, 760), {"K": "pp"}, label="south")
m.from_("wm", (70, 760), "pp_w", 1, suffix="1")
m.goto("we", (190, 760), "pp_w", 2)
m.from_("we", (300, 750), suffix="1")
m.from_("iq", (300, 770), suffix="1")
m.add("Product", "we_iq", (360, 760), {"Inputs": "**"}, show_name=False)
m.wire("From_we1", 1, "we_iq", 2)
m.wire("From_iq1", 1, "we_iq", 3)
m.add("Gain", "Lq_d", (430, 760), {"K": "-Lq"}, label="south")
m.wire("we_iq", 1, "Lq_d", 1)
m.goto("vd_ff", (500, 760), "Lq_d", 2)
m.from_("id", (600, 760), suffix="1")
m.add("Gain", "Ld_q", (660, 760), {"K": "Ld"}, label="south")
m.wire("From_id1", 1, "Ld_q", 1)
m.add("Constant", "phi_m", (660, 800), {"Value": "phi"}, label="south")
sum_("Sum_psi", (730, 760), "|++")
m.wire("Ld_q", 2, "Sum_psi", 2)
m.wire("phi_m", 1, "Sum_psi", 3, [(730, 800)])
m.from_("we", (760, 790), suffix="2")
m.add("Product", "we_psi", (800, 770), {"Inputs": "**"}, show_name=False)
m.wire("Sum_psi", 1, "we_psi", 2, [(770, 760), (770, 765)])
m.wire("From_we2", 1, "we_psi", 3, [(775, 790), (775, 775)])
m.goto("vq_ff", (870, 770), "we_psi", 1)

# ---- outputs: [wm w_ref id iq iq_ref] -----------------------------------------
m.frame(40, 880, 400, 1050, "Measurements (Out1)")
m.add("SignalMux", "Meas", (260, 965), {"Width": "5"}, show_name=False)
for k, tag in enumerate(["wm", "w_ref", "id", "iq", "iq_ref"]):
    m.from_(tag, (150, 925 + 20 * k), "Meas", 2 + k, suffix="_out")
m.outport("Meas", 1, (330, 965))

m.write("pmsm_foc.plecs")
print("wrote pmsm_foc.plecs")
