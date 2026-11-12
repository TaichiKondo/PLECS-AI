"""pmsm_foc (generated, then orientation fixed by hand in PLECS) -> pmsm_foc_v2

1. PWM from a triangle carrier and a comparator instead of the Symmetrical
   PWM block (easier to see what happens). Comparator gives 0/1, the
   converter wants 1 (upper on) / -1 (lower on): gates = 2*s - 1.
2. A Scope so that a person can look at the waveforms right after a run:
   axis 1 speed [wm w_ref], axis 2 [id iq iq_ref], axis 3 phase currents.
"""
from plecs_ai import edit as pe

SRC, DST = "pmsm_foc", "pmsm_foc_v2"
t = pe.read(SRC + ".plecs")
t = pe.set_model_name(t, SRC, DST)

# ---- 1. sine-triangle PWM ------------------------------------------------------
t = pe.remove_component(t, "PWM")
t = pe.replace_in_component(t, "Goto_gates", "Position      [940, 530]",
                            "Position      [1000, 535]")
blocks = [
    pe.new_block("TriangleGenerator", "Carrier", (790, 590), {
        "Min": "-1", "Max": "1", "f": "fsw", "DutyCycle": "0.5", "Delay": "0"}),
    pe.new_block("Comparator", "PWM_cmp", (840, 535)),
    pe.new_block("Gain", "Gate_x2", (895, 535), {"K": "2"}),
    pe.new_block("Sum", "Gate_map", (950, 535), {"Inputs": "|+-", "IconShape": "2"}),
    pe.new_block("Constant", "One", (950, 590), {"Value": "1"}),
]
conns = [
    pe.connection("Signal", "Modulation", 2, "PWM_cmp", 1),
    pe.connection("Signal", "Carrier", 1, "PWM_cmp", 2, "815, 590; 815, 540"),
    pe.connection("Signal", "PWM_cmp", 3, "Gate_x2", 1),
    pe.connection("Signal", "Gate_x2", 2, "Gate_map", 2),
    pe.connection("Signal", "One", 1, "Gate_map", 3),
    pe.connection("Signal", "Gate_map", 1, "Goto_gates", 1),
]
# ---- 2. Scope ---------------------------------------------------------------------
FROM_Y = {"Mux_w": (930, ["wm", "w_ref"]), "Mux_i": (975, ["id", "iq", "iq_ref"]),
          "Mux_abc": (1025, ["ia", "ib", "ic"])}
for mux, (y, tags) in FROM_Y.items():
    n = len(tags)
    blocks.append(pe.new_block("SignalMux", mux, (560, y), {"Width": str(n)}))
    for k, tag in enumerate(tags):
        name = "From_%s_sc" % tag
        blocks.append(pe.new_block("From", name, (500, y - 5 * (n - 1) + 10 * k),
                                   {"Tag": tag}))
        conns.append(pe.connection("Signal", name, 1, mux, 2 + k))
scope = pe.new_block("Scope", "Scope", (680, 975))
for name in ["Speed [rad/s]", "dq current [A]", "Phase current [A]"]:
    scope = scope.replace('      Axis {\n        Name          ""\n',
                          '      Axis {\n        Name          "%s"\n' % name, 1)
blocks.append(scope)
conns += [
    pe.connection("Signal", "Mux_w", 1, "Scope", 1, "620, 930; 620, 965"),
    pe.connection("Signal", "Mux_i", 1, "Scope", 2),
    pe.connection("Signal", "Mux_abc", 1, "Scope", 3, "620, 1025; 620, 985"),
]
t = pe.insert_components(t, blocks)
t = pe.append_connections(t, conns + [
    pe.rect_annotation(440, 880, 760, 1060),
    pe.text_annotation(["Waveforms (Scope)"], (600, 865))])

pe.write(DST + ".plecs", t)
print("wrote", DST + ".plecs")
