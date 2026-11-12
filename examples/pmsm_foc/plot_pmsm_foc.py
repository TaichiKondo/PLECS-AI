"""Plot results/pmsm_foc.json written by run_pmsm_foc.py.

usage: python plot_pmsm_foc.py [MODEL]   -> results/MODEL_waveforms.png
Needs matplotlib (the rest of plecs_ai does not).
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

model = sys.argv[1] if len(sys.argv) > 1 else "pmsm_foc"
with open(os.path.join("results", model + ".json")) as f:
    d = json.load(f)
t = [x * 1e3 for x in d["t"]]
wm, wref, i_d, i_q, iq_ref = d["v"]
rpm = 60 / (2 * math.pi)

fig, (a1, a2) = plt.subplots(2, 1, sharex=True, figsize=(8, 5.5))
a1.plot(t, [w * rpm for w in wref], color="#888888", lw=1, label="reference")
a1.plot(t, [w * rpm for w in wm], color="#1f6fb4", lw=1.4, label="speed")
a1.set_ylabel("speed [rpm]")
a1.legend(loc="lower right", frameon=False)
a1.grid(alpha=0.3)
a2.plot(t, i_q, color="#d0612a", lw=0.8, label="iq")
a2.plot(t, iq_ref, color="#7a3510", lw=1.2, ls="--", label="iq reference")
a2.plot(t, i_d, color="#2a8a4a", lw=0.8, label="id")
a2.set_ylabel("current [A]")
a2.set_xlabel("time [ms]")
a2.legend(loc="upper right", frameon=False)
a2.grid(alpha=0.3)
for a in (a1, a2):
    a.axvline(10, color="#bbbbbb", lw=0.8, ls=":")
    a.axvline(150, color="#bbbbbb", lw=0.8, ls=":")
a1.text(12, 50, "speed step", fontsize=8, color="#666666")
a1.text(152, 50, "load 3 N m", fontsize=8, color="#666666")
fig.tight_layout()
out = os.path.join("results", model + "_waveforms.png")
fig.savefig(out, dpi=110)
print("wrote", out)
