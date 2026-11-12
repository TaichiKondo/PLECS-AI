"""Check catalog blocks in PLECS: terminal numbers and parameter meanings.

usage: python tests/block_tests.py [CASE ...]

Builds tests/block_tests.plecs from catalog blocks only. Each case wires a
small circuit, probes one terminal through its own top-level outport and
compares the value at a few time instants with the expectation. A case
whose expectation is None only prints the values (use this to find out what
an unknown parameter or terminal does, then write the expectation in).

A passing case is what "確認: 済" in reference/blocks.md refers to.
"""
import math
import os
import sys

from plecs_ai import edit as pe
from plecs_ai.check import check
from plecs_ai.rpc import connect, simulate

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "block_tests"
TIMES = [0.25, 0.55, 0.65, 0.75, 0.85]


def C(v):
    return ("Constant", {"Value": str(v)})


# name: blocks {local name: (key, params)}, conns [(kind, src, st, dst, dt)],
#       probe (local name, terminal), expect {time: value} or None,
#       optional width (signals on the probed terminal; value is then a list)
#       and tol (relative tolerance, default 1e-3)
CASES = {
    "gain": dict(
        blocks={"u": C(2), "g": ("Gain", {"K": "3"})},
        conns=[("Signal", "u", 1, "g", 1)], probe=("g", 2),
        expect={0.25: 6}),
    "step": dict(
        blocks={"s": ("Step", {"Time": "0.5", "Before": "1", "After": "4"})},
        conns=[], probe=("s", 1), expect={0.25: 1, 0.75: 4}),
    "integrator": dict(
        blocks={"u": C(2), "i": ("Integrator", {"x0": "1"})},
        conns=[("Signal", "u", 1, "i", 1)], probe=("i", 2),
        expect={0.25: 1.5, 0.75: 2.5}),
    "integrator_limit": dict(
        blocks={"u": C(2), "i": ("Integrator", {"UpperLimit": "1"})},
        conns=[("Signal", "u", 1, "i", 1)], probe=("i", 2),
        expect={0.25: 0.5, 0.75: 1}),
    "zoh": dict(
        blocks={"s": ("Step", {"Time": "0.5", "Before": "0", "After": "1"}),
                "z": ("ZeroOrderHold", {"Ts": "0.4"})},
        conns=[("Signal", "s", 1, "z", 1)], probe=("z", 2),
        expect={0.75: 0, 0.85: 1}),
    "saturation_hi": dict(
        blocks={"u": C(2), "q": ("Saturation", {"UpperLimit": "0.5",
                                                "LowerLimit": "-0.5"})},
        conns=[("Signal", "u", 1, "q", 1)], probe=("q", 2), expect={0.25: 0.5}),
    "saturation_lo": dict(
        blocks={"u": C(-2), "q": ("Saturation", {"UpperLimit": "0.5",
                                                 "LowerLimit": "-0.5"})},
        conns=[("Signal", "u", 1, "q", 1)], probe=("q", 2), expect={0.25: -0.5}),
    # SignalSwitch: 2 = data passed when the criterion holds, 3 = otherwise,
    # 4 = control. Criteria 1: ctrl >= Threshold, 2: ctrl > Threshold,
    # 3: ctrl ~= 0
    "signalswitch_crit1_05": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0.5),
                "w": ("SignalSwitch", {"Criteria": "1", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 10}),
    "signalswitch_crit1_04": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0.4),
                "w": ("SignalSwitch", {"Criteria": "1", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 20}),
    "signalswitch_crit2_05": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0.5),
                "w": ("SignalSwitch", {"Criteria": "2", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 20}),
    "signalswitch_crit2_06": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0.6),
                "w": ("SignalSwitch", {"Criteria": "2", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 10}),
    "signalswitch_crit3_0": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0),
                "w": ("SignalSwitch", {"Criteria": "3", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 20}),
    "signalswitch_crit3_04": dict(
        blocks={"a": C(10), "b": C(20), "c": C(0.4),
                "w": ("SignalSwitch", {"Criteria": "3", "Threshold": "0.5"})},
        conns=[("Signal", "a", 1, "w", 2), ("Signal", "b", 1, "w", 3),
               ("Signal", "c", 1, "w", 4)], probe=("w", 1), expect={0.25: 10}),
    "periodic_average": dict(
        blocks={"u": C(3), "p": ("PeriodicAverage", {"T_average": "0.1"})},
        conns=[("Signal", "u", 1, "p", 2)], probe=("p", 1), expect={0.75: 3}),
    "periodic_impulse_average": dict(
        blocks={"u": C(3), "p": ("PeriodicImpulseAverage", {"T_average": "0.1"})},
        conns=[("Signal", "u", 1, "p", 2)], probe=("p", 1), expect=None),
    # Units 1: Frequency in rad/s, 2: in Hz
    "sine_units1": dict(
        blocks={"s": ("SineGenerator", {"Amplitude": "2", "Frequency": "1",
                                        "Units": "1"})},
        conns=[], probe=("s", 1), expect={0.25: 0.494808}),
    "sine_units2": dict(
        blocks={"s": ("SineGenerator", {"Amplitude": "2", "Frequency": "1",
                                        "Units": "2"})},
        conns=[], probe=("s", 1), expect={0.25: 2, 0.75: -2}),
    "turn_on_delay": dict(
        blocks={"s": ("Step", {"Time": "0.5", "Before": "0", "After": "1"}),
                "d": ("Turn_on_Delay", {"T_d": "0.1"})},
        conns=[("Signal", "s", 1, "d", 1)], probe=("d", 2),
        expect={0.55: 0, 0.65: 1}),
    "transfer_function": dict(
        blocks={"u": C(1), "h": ("TransferFunction", {"Numerator": "[1]",
                                                      "Denominator": "[0.25 1]"})},
        conns=[("Signal", "u", 1, "h", 1)], probe=("h", 2),
        expect={0.25: 0.632121, 0.75: 0.950213}),
    "rate_limiter": dict(
        blocks={"s": ("Step", {"Time": "0.5", "Before": "0", "After": "1"}),
                "r": ("RateLimiter", {"RisingRateLimit": "2",
                                      "FallingRateLimit": "-2",
                                      "SampleTimeMode": "2"})},
        conns=[("Signal", "s", 1, "r", 1)], probe=("r", 2),
        expect={0.25: 0, 0.65: 0.3, 0.85: 0.7}),
    # RelationalOperator: out 3 = (in1 OP in2); OP 1..6 = == ~= < <= >= >
    "relational_1": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "1"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 1}),
    "relational_2": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "2"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 0}),
    "relational_3": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "3"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 0}),
    "relational_4": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "4"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 1}),
    "relational_5": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "5"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 1}),
    "relational_6": dict(
        blocks={"a": C(2), "b": C(2), "r": ("RelationalOperator", {"Operator": "6"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 0}),
    "relational_lt": dict(
        blocks={"a": C(1), "b": C(2), "r": ("RelationalOperator", {"Operator": "3"})},
        conns=[("Signal", "a", 1, "r", 1), ("Signal", "b", 1, "r", 2)],
        probe=("r", 3), expect={0.25: 1}),
    # V+ (1) -> R -> diode 1, diode 2 -> V- (2): conducts if 1 is the anode
    "diode_polarity": dict(
        blocks={"u": C(5), "v": ("VoltageSource", {}),
                "r": ("Resistor", {"R": "1"}), "d": ("Diode", {}),
                "a": ("Ammeter", {})},
        conns=[("Signal", "u", 1, "v", 3), ("Wire", "v", 1, "r", 1),
               ("Wire", "r", 2, "a", 1), ("Wire", "a", 2, "d", 1),
               ("Wire", "d", 2, "v", 2)],
        probe=("a", 3), expect={0.25: 5}),
    # DC source + ground: Voltmeter 1 on source terminal 1
    "dc_source_ground": dict(
        blocks={"v": ("DCVoltageSource", {"V": "7"}), "r": ("Resistor", {"R": "1"}),
                "m": ("Voltmeter", {}), "g": ("Ground", {})},
        conns=[("Wire", "v", 1, [("r", 1), ("m", 1)]),
               ("Wire", "v", 2, [("r", 2), ("m", 2), ("g", 1)])],
        probe=("m", 3), expect={0.25: 7}),
    # ideal switch closed by a control signal of 1
    "switch": dict(
        blocks={"u": C(5), "v": ("VoltageSource", {}), "r": ("Resistor", {"R": "1"}),
                "s": ("Switch", {}), "k": C(1), "a": ("Ammeter", {})},
        conns=[("Signal", "u", 1, "v", 3), ("Wire", "v", 1, "r", 1),
               ("Wire", "r", 2, "a", 1), ("Wire", "a", 2, "s", 1),
               ("Wire", "s", 2, "v", 2), ("Signal", "k", 1, "s", 3)],
        probe=("a", 3), expect={0.25: 5}),
}

# ---- motor drive blocks (found with drive_probe.py) ---------------------------
_TH = 0.3
_ABC = [math.cos(_TH), math.cos(_TH - 2 * math.pi / 3), math.cos(_TH + 2 * math.pi / 3)]
CASES.update({
    # 3ph->RRF: 1 = abc (width 3), 3 = angle, 2 = [d q] (width 2).
    # Amplitude invariant, d axis on cos(angle)
    "abc_to_dq": dict(
        blocks={"a": C(_ABC[0]), "b": C(_ABC[1]), "c": C(_ABC[2]),
                "m": ("SignalMux", {"Width": "3"}), "th": C(_TH),
                "t": ("3ph_RRF", {})},
        conns=[("Signal", "a", 1, "m", 2), ("Signal", "b", 1, "m", 3),
               ("Signal", "c", 1, "m", 4), ("Signal", "m", 1, "t", 1),
               ("Signal", "th", 1, "t", 3)],
        probe=("t", 2), width=2, expect={0.25: [1, 0]}),
    # RRF->3ph: 1 = [d q] (width 2), 3 = angle, 2 = abc (width 3)
    "dq_to_abc": dict(
        blocks={"d": C(1), "q": C(0), "m": ("SignalMux", {"Width": "2"}),
                "th": C(_TH), "t": ("RRF_3ph", {})},
        conns=[("Signal", "d", 1, "m", 2), ("Signal", "q", 1, "m", 3),
               ("Signal", "m", 1, "t", 1), ("Signal", "th", 1, "t", 3)],
        probe=("t", 2), width=3, expect={0.25: _ABC}),
    # 2-level converter: 1-3 = phases a-c, 4 = gates (width 3; 1 = upper
    # switch on, -1 = lower on), 5 = DC+, 6 = DC-. 100 V, [1 -1 -1], 1 ohm star
    "two_level_converter": dict(
        blocks={"v": ("DCVoltageSource", {"V": "100"}),
                "k": ("2_Level_IGBT_Conv", {}),
                "g1": C(1), "g2": C(-1), "g3": C(-1),
                "m": ("SignalMux", {"Width": "3"}),
                "ra": ("Resistor", {"R": "1"}), "rb": ("Resistor", {"R": "1"}),
                "rc": ("Resistor", {"R": "1"}), "am": ("Ammeter", {})},
        conns=[("Wire", "v", 1, "k", 5), ("Wire", "v", 2, "k", 6),
               ("Signal", "g1", 1, "m", 2), ("Signal", "g2", 1, "m", 3),
               ("Signal", "g3", 1, "m", 4), ("Signal", "m", 1, "k", 4),
               ("Wire", "k", 1, "am", 1), ("Wire", "am", 2, "ra", 1),
               ("Wire", "k", 2, "rb", 1), ("Wire", "k", 3, "rc", 1),
               ("Wire", "ra", 2, [("rb", 2), ("rc", 2)])],
        probe=("am", 3), expect={0.25: 100 / 1.5}),
})


CASES.update({
    # Symmetrical PWM: 2 = modulation (vector ok), 1 = switching signal.
    # carrier_limits [-1 1], output_values [-1 1]: the average equals the input.
    # The meaning of 'sampling' is not known yet (1, 2, 3 all pass this).
    "symmetrical_pwm": dict(
        blocks={"a": C(0.5), "b": C(0), "c": C(-0.5), "m": ("SignalMux", {"Width": "3"}),
                "p": ("Symmetrical_PWM", {"sampling": "1", "fc": "1000",
                                          "carrier_phaseshift": "0",
                                          "carrier_limits": "[-1 1]",
                                          "output_values": "[-1 1]"}),
                "avg": ("PeriodicAverage", {"T_average": "1e-3"})},
        conns=[("Signal", "a", 1, "m", 2), ("Signal", "b", 1, "m", 3),
               ("Signal", "c", 1, "m", 4), ("Signal", "m", 1, "p", 2),
               ("Signal", "p", 1, "avg", 2)],
        probe=("avg", 1), width=3, expect={0.25: [0.5, 0, -0.5]}),
    # Comparator: vector (+, terminal 1) against a scalar (-, terminal 2),
    # output 1 where + > -, else 0. Sine-triangle PWM: modulation on +,
    # carrier on -; map to converter gates with 2*s - 1
    "comparator_vector": dict(
        blocks={"a": C(0.5), "b": C(-0.5), "c": C(0.3),
                "m": ("SignalMux", {"Width": "3"}), "z": C(0.2),
                "k": ("Comparator", {})},
        conns=[("Signal", "a", 1, "m", 2), ("Signal", "b", 1, "m", 3),
               ("Signal", "c", 1, "m", 4), ("Signal", "m", 1, "k", 1),
               ("Signal", "z", 1, "k", 2)],
        probe=("k", 3), width=3, expect={0.25: [1, 0, 1]}),
    # Discrete PID: 1 = error in, 2 = out (same as the continuous one).
    # int_method 1: forward Euler, 2: backward Euler, 3: trapezoidal;
    # aw_method 1: none, 2: back-calculation (names read with plecs.get)
    "discrete_pi": dict(
        blocks={"e": C(1), "p": ("Discrete_PID_Controller", {
            "cont_type": "3", "kp": "2", "ki": "10", "int_method": "2",
            "t_sample": "1e-3", "up_limit": "inf", "low_limit": "-inf",
            "aw_method": "1", "kbc": "1", "x0": "0"})},
        conns=[("Signal", "e", 1, "p", 1)], probe=("p", 2),
        expect={0.25: 4.5, 0.75: 9.5}),
    "discrete_pi_limit": dict(
        blocks={"e": C(1), "p": ("Discrete_PID_Controller", {
            "cont_type": "3", "kp": "2", "ki": "10", "int_method": "2",
            "t_sample": "1e-3", "up_limit": "3", "low_limit": "-3",
            "aw_method": "2", "kbc": "10", "x0": "0"})},
        conns=[("Signal", "e", 1, "p", 1)], probe=("p", 2),
        expect={0.75: 3}),
    # SignalDemux: 1 = vector in, 2.. = elements out
    "signal_demux": dict(
        blocks={"a": C(3), "b": C(4), "m": ("SignalMux", {"Width": "2"}),
                "d": ("SignalDemux", {"Width": "2"})},
        conns=[("Signal", "a", 1, "m", 2), ("Signal", "b", 1, "m", 3),
               ("Signal", "m", 1, "d", 1)],
        probe=("d", 3), expect={0.25: 4}),
})


def _pmsm(probe, width=1, expect=None, tol=1e-3):
    """PMSM coasting at 100 rad/s (J = 1e6), phases open (1 Mohm star).
    p = 4, phi = 0.101: back EMF peak p*wm*phi = 40.4 V."""
    return dict(
        blocks={"pm": ("Perm_Magnet_SM", {
                    "configuration": "2", "R": "0.62", "L": "[4.14e-3 4.14e-3]",
                    "phi": "0.101", "J": "1e6", "F": "0", "p": "4",
                    "wm0": "100", "thm0": "0", "is0": "[0 0]"}),
                "ang": ("AngleSensor", {"SecondFlange": "1", "theta0": "0"}),
                "spd": ("RotationalSpeedSensor", {"SecondFlange": "1"}),
                "ra": ("Resistor", {"R": "1e6"}), "rb": ("Resistor", {"R": "1e6"}),
                "rc": ("Resistor", {"R": "1e6"}),
                "va": ("Voltmeter", {}), "vb": ("Voltmeter", {}), "vc": ("Voltmeter", {}),
                "m": ("SignalMux", {"Width": "3"}), "pp": ("Gain", {"K": "4"}),
                "t": ("3ph_RRF", {})},
        conns=[("Rotational", "pm", 4, [("ang", 1), ("spd", 1)]),
               ("Wire", "pm", 1, [("ra", 1), ("va", 1)]),
               ("Wire", "pm", 2, [("rb", 1), ("vb", 1)]),
               ("Wire", "pm", 3, [("rc", 1), ("vc", 1)]),
               ("Wire", "ra", 2, [("rb", 2), ("rc", 2), ("va", 2), ("vb", 2),
                                  ("vc", 2)]),
               ("Signal", "va", 3, "m", 2), ("Signal", "vb", 3, "m", 3),
               ("Signal", "vc", 3, "m", 4), ("Signal", "m", 1, "t", 1),
               ("Signal", "ang", 2, "pp", 1), ("Signal", "pp", 2, "t", 3)],
        probe=probe, width=width, expect=expect, tol=tol)


# Perm_Magnet_SM: 1-3 = phases, 4 = shaft. p = pole pairs, L = [Ld Lq],
# is0 = [id0 iq0]. Phase a flux = phi*cos(p*theta_m): EMF on +q axis.
# AngleSensor: mechanical angle wrapped to (-pi, pi]
CASES.update({
    "pmsm_speed": _pmsm(("spd", 2), expect={0.25: 100}),
    "pmsm_angle": _pmsm(("ang", 2), expect={
        0.25: math.remainder(25, 2 * math.pi), 0.75: math.remainder(75, 2 * math.pi)}),
    "pmsm_emf_a": _pmsm(("va", 3), expect={
        0.25: -40.4 * math.sin(100), 0.75: -40.4 * math.sin(300)}, tol=2e-3),
    "pmsm_emf_dq": _pmsm(("t", 2), 2, expect={0.25: [0, 40.4], 0.75: [0, 40.4]},
                         tol=2e-3),
})


def fmt(x):
    if isinstance(x, (list, tuple)):
        return "[" + " ".join("%.6g" % e for e in x) + "]"
    return "%.6g" % x


def close(got, want, tol):
    """Relative tolerance tol (absolute below magnitude 1); scalar or vector."""
    if isinstance(want, (list, tuple)):
        return len(got) == len(want) and all(close(g, w, tol)
                                             for g, w in zip(got, want))
    return abs(got - want) <= tol * max(1, abs(want))


def branch(kind, src, src_t, dsts):
    """One connection from src to several destinations (a junction)."""
    s = ("    Connection {\n      Type          %s\n"
         '      SrcComponent  "%s"\n      SrcTerminal   %d\n' % (kind, src, src_t))
    for d, dt in dsts:
        s += ('      Branch {\n        DstComponent  "%s"\n'
              "        DstTerminal   %d\n      }\n" % (d, dt))
    return s + "    }\n"


def build(cases):
    sample = pe.read(os.path.join(HERE, "..", "samples", "parts_sample.plecs"))
    head = sample[:sample.index("    Component {")]
    head = pe.set_model_name(head, "parts_sample", NAME)
    comps, conns, terms = [], [], []
    for row, (cname, case) in enumerate(cases):
        y = 60 + 150 * row
        for col, (local, (key, params)) in enumerate(case["blocks"].items()):
            comps.append(pe.new_block(key, "%s_%s" % (cname, local),
                                      (60 + 120 * col, y), params))
        p, pt = case["probe"]
        out = "%s_out" % cname
        ox, oy = 60 + 120 * len(case["blocks"]), y + 70
        px = 60 + 120 * list(case["blocks"]).index(p)
        probe_free = True
        for c in case["conns"]:
            if c[1:3] == (p, pt):  # probed terminal already wired: branch off
                c = c[:3] + ([c[3:]] if len(c) == 5 else list(c[3]),)
                probe_free = False
                conns.append(branch(c[0], "%s_%s" % (cname, p), pt,
                                    [("%s_%s" % (cname, d), dt) for d, dt in c[3]]
                                    + [(out, 1)]))
            elif len(c) == 5:
                kind, s, st, d, dt = c
                conns.append(pe.connection(kind, "%s_%s" % (cname, s), st,
                                           "%s_%s" % (cname, d), dt))
            else:  # (kind, src, terminal, [(dst, terminal), ...]): one node
                kind, s, st, dsts = c
                conns.append(branch(kind, "%s_%s" % (cname, s), st,
                                    [("%s_%s" % (cname, d), dt) for d, dt in dsts]))
        # the outport sits 70 below the row and the probe wire drops down
        # right next to the probed block: a straight wire along the row
        # would run over unconnected terminals, which PLECS refuses to load
        comps.append(pe.new_block("Output", out, (ox, oy), {"Index": str(row + 1)}))
        if probe_free:
            conns.append(pe.connection("Signal", "%s_%s" % (cname, p), pt, out, 1,
                                       "%d, %d" % (px + 50, oy)))
        terms.append('  Terminal {\n    Type          Output\n'
                     '    Index         "%d"\n  }\n' % (row + 1))
    head = pe.replace_once(head, "  Schematic {\n", "".join(terms) + "  Schematic {\n")
    text = head + "".join(comps) + "".join(conns) + "  }\n}\n"
    errors, _ = check(text)
    assert not errors, errors
    path = os.path.join(HERE, NAME + ".plecs")
    pe.write(path, text)
    return path


def main():
    names = sys.argv[1:] or list(CASES)
    cases = [(n, CASES[n]) for n in names]
    path = build(cases)
    t, v, _ = simulate(connect(), path, None,
                       {"TimeSpan": 1.0, "OutputTimes": TIMES}, reload=True)
    failed = 0
    k = 0
    for name, case in cases:
        w = case.get("width", 1)
        sigs, k = v[k:k + w], k + w
        got = {tt: [s[i] for s in sigs] for i, tt in enumerate(t)}
        if w == 1:
            got = {tt: g[0] for tt, g in got.items()}
        exp = case["expect"]
        tol = case.get("tol", 1e-3)
        if exp is None:
            print("INFO %-26s %s" % (name, ", ".join(
                "t=%.2f:%s" % (tt, fmt(got[tt])) for tt in TIMES)))
            continue
        bad = [(tt, fmt(got[tt]), fmt(ev)) for tt, ev in exp.items()
               if not close(got[tt], ev, tol)]
        failed += bool(bad)
        print("%s %-26s %s" % ("FAIL" if bad else "ok  ", name,
                               "; ".join("t=%.2f got %s want %s" % b for b in bad)))
    print("%d cases, %d failed" % (len(cases), failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
