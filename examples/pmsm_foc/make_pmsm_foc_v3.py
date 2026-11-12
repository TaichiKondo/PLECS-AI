"""pmsm_foc_v2 -> pmsm_foc_v3: continuous PI controllers -> discrete PI.

Current loops sampled with the PWM period (Ts_i = 1/fsw), speed loop at
1 kHz (Ts_w). Backward Euler integration. Gains, limits and anti-windup
are copied from v2. The discrete PID has the same terminals as the
continuous one (tests/block_tests.py: discrete_pi), so wiring is kept.
"""
from plecs_ai import edit as pe

SRC, DST = "pmsm_foc_v2", "pmsm_foc_v3"
t = pe.read(SRC + ".plecs")
t = pe.set_model_name(t, SRC, DST)

KEEP = ("cont_type", "kp", "ki", "up_limit", "low_limit", "aw_method", "kbc", "x0")
for name, ts in [("PI_d", "Ts_i"), ("PI_q", "Ts_i"), ("PI_w", "Ts_w")]:
    t = pe.swap_block(t, name, "Discrete_PID_Controller",
                      {"int_method": "2", "t_sample": ts}, keep=KEEP)

t = pe.set_init_commands(t, pe.get_init_commands(t) + (
    "\n\n% Discrete controllers (pmsm_foc_v3): sample times\n"
    "Ts_i = 1/fsw\nTs_w = 1e-3"))

pe.write(DST + ".plecs", t)
print("wrote", DST + ".plecs")
