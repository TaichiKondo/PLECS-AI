"""Thin helper around the PLECS Standalone XML-RPC interface.

The RPC server must be enabled in the PLECS preferences. The URL is taken
from the environment variable PLECS_RPC_URL (default http://localhost:1080).
Models are given as a path to the .plecs file, or as a bare model name which
is looked up in the current working directory.
"""
import os
import time
import xmlrpc.client

URL = os.environ.get("PLECS_RPC_URL", "http://localhost:1080")
Fault = xmlrpc.client.Fault


def connect():
    return xmlrpc.client.ServerProxy(URL).plecs


def model_path(model):
    """Absolute path of 'name', 'name.plecs' or 'dir/name.plecs'."""
    if not model.lower().endswith(".plecs"):
        model += ".plecs"
    return os.path.abspath(model)


def model_name(model):
    return os.path.splitext(os.path.basename(model_path(model)))[0]


def results_dir():
    """./results (created on demand); meant to be git-ignored."""
    d = os.path.abspath("results")
    os.makedirs(d, exist_ok=True)
    return d


def load(plecs, model, reload=True):
    """Open the model. reload=True closes it first so disk edits are picked up.

    Closing discards unsaved changes made in the PLECS GUI.
    """
    name = model_name(model)
    if reload:
        try:
            plecs.close(name)
        except Fault:
            pass  # not open yet
    plecs.load(model_path(model))
    return name


def simulate(plecs, model, model_vars=None, solver_opts=None, reload=False):
    """Load and run. Returns (time_list, list_of_signal_lists, wall_seconds).

    The model needs at least one top-level Signal Outport, otherwise PLECS
    returns no data.
    """
    name = load(plecs, model, reload)
    opts = {}
    if model_vars:
        opts["ModelVars"] = model_vars
    if solver_opts:
        opts["SolverOpts"] = solver_opts
    t0 = time.time()
    res = plecs.simulate(name, opts) if opts else plecs.simulate(name)
    wall = time.time() - t0
    if not isinstance(res, dict) or "Time" not in res:
        raise RuntimeError("simulate returned no data (no top-level outport?): %r"
                           % (res,))
    return res["Time"], res["Values"], wall


def circuit_bitmap(plecs, model, subsystem=None, reload=True):
    """PNG bytes of the schematic plus component frames (pixel coordinates).

    Uses plecs.webserver('getCircuitBitmap', ...), which is not in the manual
    (found in the RT Box demo 'automated_testing_robot_framework', PLECS 5.0).
    """
    path = load(plecs, model, reload)
    if subsystem:
        path += "/" + subsystem
    res = plecs.webserver("getCircuitBitmap", path, {})
    return res["imageData"].data, res["components"]


def frange(t0, t1, dt):
    """t0, t0+dt, ..., t1. Rounded so that the last value never exceeds t1:
    PLECS rejects OutputTimes outside [start, TimeSpan]."""
    n = int(round((t1 - t0) / dt))
    return [min(t1, round(t0 + i * dt, 12)) for i in range(n + 1)]
