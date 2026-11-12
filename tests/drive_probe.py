"""Exploratory probes for the motor-drive blocks (dq transforms, 2-level
converter, PMSM, rotational sensors). Prints values only; confirmed results
are moved into block_tests.py as cases with expectations.

usage: python tests/drive_probe.py GROUP   (GROUP: transform, conv, pmsm)
"""
import math
import sys

import block_tests as bt

C = bt.C
TH = 0.3
abc = [math.cos(TH), math.cos(TH - 2 * math.pi / 3), math.cos(TH + 2 * math.pi / 3)]

GROUPS = {
    "transform": {
        "abc_to_dq": dict(
            blocks={"a": C(abc[0]), "b": C(abc[1]), "c": C(abc[2]),
                    "m": ("SignalMux", {"Width": "3"}), "th": C(TH),
                    "t": ("3ph_RRF", {})},
            conns=[("Signal", "a", 1, "m", 2), ("Signal", "b", 1, "m", 3),
                   ("Signal", "c", 1, "m", 4), ("Signal", "m", 1, "t", 1),
                   ("Signal", "th", 1, "t", 3)],
            probe=("t", 2), width=2, expect=None),
        "dq_to_abc": dict(
            blocks={"d": C(1), "q": C(0),
                    "m": ("SignalMux", {"Width": "2"}), "th": C(TH),
                    "t": ("RRF_3ph", {})},
            conns=[("Signal", "d", 1, "m", 2), ("Signal", "q", 1, "m", 3),
                   ("Signal", "m", 1, "t", 1),
                   ("Signal", "th", 1, "t", 3)],
            probe=("t", 2), width=3, expect=None),
    },
    # Vdc = 100 V on 5(+)/6(-), gates [1 -1 -1], star load of 1 ohm per phase
    "conv": {
        "conv_gate": dict(
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
            probe=("am", 3), expect=None),
    },
    # shaft coasting at 100 rad/s (J = 1e6, wm0 = 100), phases loaded with 1 kohm star (nearly open)
    "pmsm": {},
}


def pmsm_case(probe, width=1):
    return dict(
        blocks={"pm": ("Perm_Magnet_SM", {
                    "configuration": "2", "R": "0.62", "L": "[4.14e-3 4.14e-3]",
                    "phi": "0.101", "J": "1e6", "F": "0", "p": "4",
                    "wm0": "100", "thm0": "0", "is0": "[0 0]"}),
                "ang": ("AngleSensor", {"SecondFlange": "1", "theta0": "0"}),
                "spd": ("RotationalSpeedSensor", {"SecondFlange": "1"}),
                "ra": ("Resistor", {"R": "1e3"}), "rb": ("Resistor", {"R": "1e3"}),
                "rc": ("Resistor", {"R": "1e3"}),
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
        probe=probe, width=width, expect=None)


GROUPS["pmsm"] = {"pmsm_speed": pmsm_case(("spd", 2)),
                  "pmsm_angle": pmsm_case(("ang", 2)),
                  "pmsm_va": pmsm_case(("va", 3)),
                  "pmsm_vdq": pmsm_case(("t", 2), 2)}

if __name__ == "__main__":
    bt.CASES = GROUPS[sys.argv[1]]
    bt.TIMES = [0.0103, 0.0256, 0.0412, 0.0567]
    sys.argv = sys.argv[:1]
    try:
        bt.main()
    except SystemExit:
        pass
