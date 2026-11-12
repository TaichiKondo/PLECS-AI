"""Tools for AI-driven editing and simulation of PLECS Standalone models."""
import sys

# PLECS error messages are Japanese (UTF-8) when the GUI is Japanese. On a
# Japanese Windows console Python prints in cp932, which AI agents reading
# the output as UTF-8 see as garbage. Print UTF-8 instead.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
