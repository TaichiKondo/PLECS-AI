"""Speed step and load step test of pmsm_foc.

usage: python run_pmsm_foc.py [MODEL] [var=value ...]
Out1 = [wm w_ref id iq iq_ref], sampled every 20 us (twice per PWM period).
"""
import json
import math
import os
import sys

from plecs_ai.rpc import connect, frange, results_dir, simulate

model = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else "pmsm_foc"
mvars = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
T_W, T_LOAD, T_END = 0.01, 0.15, 0.25
W_REF = 1000 * 2 * math.pi / 60
KT = 1.5 * 4 * 0.101
T_LOAD_NM = mvars.get("T_load", 3.0)

t, v, wall = simulate(connect(), model, mvars or None,
                      {"TimeSpan": T_END, "OutputTimes": frange(0, T_END, 2e-5)},
                      reload=True)
with open(os.path.join(results_dir(), model + ".json"), "w") as f:
    json.dump({"t": t, "v": v, "vars": mvars}, f)
wm, wref, i_d, i_q, iq_ref = v
n = len(t)
print("%s %s: %d points, wall %.1f s" % (model, mvars, n, wall))


def window(a, b):
    return [i for i in range(n) if a <= t[i] < b]


def mean(idx, s):
    return sum(s[i] for i in idx) / len(idx)


# speed step
w = window(T_W, T_LOAD)
peak = max(wm[i] for i in w)
t10 = next(t[i] for i in w if wm[i] >= 0.1 * W_REF)
t90 = next(t[i] for i in w if wm[i] >= 0.9 * W_REF)
outside = [t[i] for i in w if abs(wm[i] - W_REF) > 0.01 * W_REF]
ss = window(T_LOAD - 0.02, T_LOAD)
print("speed step 0 -> %.1f rad/s (1000 rpm) at %.3f s" % (W_REF, T_W))
print("  rise time 10-90%%     %.2f ms" % ((t90 - t10) * 1e3))
print("  overshoot             %.2f %%" % ((peak - W_REF) / W_REF * 100))
print("  settling (1%% band)    %.2f ms after the step"
      % ((outside[-1] - T_W) * 1e3 if outside else 0))
print("  steady state error    %+.4f rad/s" % (mean(ss, wm) - W_REF))
print("  iq during accel: max %.2f A (limit 10)" % max(i_q[i] for i in w))

# load step
w = window(T_LOAD, T_END)
dip = min(wm[i] for i in w)
outside = [t[i] for i in w if abs(wm[i] - W_REF) > 0.01 * W_REF]
ss = window(T_END - 0.02, T_END)
print("load step %.1f N m at %.3f s" % (T_LOAD_NM, T_LOAD))
print("  speed dip             %.2f rad/s (%.2f %%)"
      % (W_REF - dip, (W_REF - dip) / W_REF * 100))
print("  recovery (1%% band)    %.2f ms" % ((outside[-1] - T_LOAD) * 1e3 if outside else 0))
print("  iq steady             %.3f A  (expected (T + F w)/Kt = %.3f A)"
      % (mean(ss, i_q), (T_LOAD_NM + 1e-4 * W_REF) / KT))
print("  iq - iq_ref (mean)    %+.4f A" % (mean(ss, i_q) - mean(ss, iq_ref)))
print("  id mean / max |id|    %+.4f A / %.3f A"
      % (mean(ss, i_d), max(abs(i_d[i]) for i in w)))
