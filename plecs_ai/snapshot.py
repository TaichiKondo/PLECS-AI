"""Save a PNG of a model's schematic so the layout can be inspected.

usage: python -m plecs_ai.snapshot MODEL[.plecs] [SUBSYSTEM]
Writes results/MODEL[_SUBSYSTEM].png and prints the path. The model is
reloaded from disk first (unsaved GUI changes are discarded).
"""
import os
import sys

from .rpc import circuit_bitmap, connect, model_name, results_dir


def main():
    model = sys.argv[1]
    sub = sys.argv[2] if len(sys.argv) > 2 else None
    png, comps = circuit_bitmap(connect(), model, sub)
    stem = model_name(model) + ("_" + sub.replace("/", "_") if sub else "")
    out = os.path.join(results_dir(), stem + ".png")
    with open(out, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes, %d components)" % (out, len(png), len(comps)))


if __name__ == "__main__":
    main()
