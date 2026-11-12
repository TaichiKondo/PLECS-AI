"""Build a new .plecs model from scratch out of catalog blocks.

    from plecs_ai.build import Model
    m = Model("my_model", time_span=0.3, max_step=1e-4)
    m.init("Vdc = 300\\nfsw = 10e3")
    m.add("Constant", "Vref", (100, 100), {"Value": "1"})
    m.add("Gain", "G", (200, 100), {"K": "2"})
    m.wire("Vref", 1, "G", 1)
    m.outport("G", 2, (300, 100))           # top-level outport 1
    m.write("my_model.plecs")                # runs plecs_ai.check first

Model settings (solver etc.) come from plecs_ai/templates/empty.plecs: the
header of a model saved by PLECS Standalone 5.0 (samples/parts_sample.plecs)
with all components removed.

Layout: PLECS refuses to load a model where a wire runs over an unconnected
terminal. Give long wires corner points, use Goto/From for signals that
travel far, and look at the result with plecs_ai.snapshot.
"""
import os
import re

from . import edit as pe
from .check import check

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "templates", "empty.plecs")


def _set_line(block, key, value):
    pat = re.compile(r"\n      %s +\S+\n" % key)
    assert len(pat.findall(block)) == 1, key
    return pat.sub("\n      %-13s %s\n" % (key, value), block)


class Model:
    def __init__(self, name, time_span=1.0, max_step=None, rel_tol=None):
        self.name = name
        t = pe.read(TEMPLATE)
        t = pe.set_model_name(t, "empty", name)
        t = self._header(t, "TimeSpan", "%g" % time_span)
        if max_step is not None:
            t = self._header(t, "MaxStep", "%g" % max_step)
        if rel_tol is not None:
            t = self._header(t, "RelTol", "%g" % rel_tol)
        self.head = t[:t.index("  }\n}\n")]  # up to the end of Schematic
        self.comps, self.conns, self.notes, self.terms = [], [], [], []
        self.names = set()
        self.n_out = 0

    @staticmethod
    def _header(t, key, value):
        return pe.replace_once(t, re.search(r'\n  %s +"[^"\n]*"\n' % key, t).group(0),
                               '\n  %s "%s"\n' % (key.ljust(13), value))

    def init(self, commands):
        """InitializationCommands (plain text, real newlines)."""
        self.head = pe.set_init_commands(self.head, commands)

    def add(self, key, name, pos, params=None, direction=None, flipped=None,
            label=None, show_name=None):
        """Place a catalog block. direction: up/right/down/left (rotation),
        flipped: True/False, label: north/south/east/west."""
        assert name not in self.names, name
        self.names.add(name)
        b = pe.new_block(key, name, pos, params)
        if direction:
            b = _set_line(b, "Direction", direction)
        if flipped is not None:
            b = _set_line(b, "Flipped", "on" if flipped else "off")
        if label:
            b = _set_line(b, "LabelPosition", label)
        if show_name is not None:
            b = _set_line(b, "Show", "on" if show_name else "off")
        self.comps.append(b)
        return name

    def wire(self, src, src_t, dst, dst_t, points=None, kind="Signal"):
        """points: list of (x, y) corners."""
        pts = "; ".join("%d, %d" % p for p in points) if points else None
        self.conns.append(pe.connection(kind, src, src_t, dst, dst_t, pts))

    def node(self, src, src_t, dsts, kind="Signal", points=None):
        """One source to several destinations: dsts = [(dst, t[, points])]."""
        s = "    Connection {\n      Type          %s\n" % kind
        s += '      SrcComponent  "%s"\n      SrcTerminal   %d\n' % (src, src_t)
        if points:
            s += "      Points        [%s]\n" % "; ".join("%d, %d" % p for p in points)
        for d in dsts:
            s += "      Branch {\n"
            if len(d) > 2 and d[2]:
                s += "        Points        [%s]\n" % "; ".join("%d, %d" % p for p in d[2])
            s += '        DstComponent  "%s"\n        DstTerminal   %d\n      }\n' % d[:2]
        self.conns.append(s + "    }\n")

    def goto(self, tag, pos, src=None, src_t=1, **kw):
        """Goto block with tag; optionally wired from (src, src_t)."""
        name = self.add("Goto", "Goto_" + tag, pos, {"Tag": tag}, show_name=False, **kw)
        if src:
            self.wire(src, src_t, name, 1)
        return name

    def from_(self, tag, pos, dst=None, dst_t=1, suffix="", **kw):
        name = self.add("From", "From_%s%s" % (tag, suffix), pos, {"Tag": tag},
                        show_name=False, **kw)
        if dst:
            self.wire(name, 1, dst, dst_t)
        return name

    def outport(self, src, src_t, pos, name=None):
        """New top-level outport wired from (src, src_t). Returns its index."""
        self.n_out += 1
        name = name or "Out%d" % self.n_out
        self.add("Output", name, pos, {"Index": str(self.n_out)})
        self.wire(src, src_t, name, 1)
        self.terms.append('  Terminal {\n    Type          Output\n'
                          '    Index         "%d"\n  }\n' % self.n_out)
        return self.n_out

    def scope(self, axes, pos, name="Scope"):
        """Scope fed from Goto tags so that people can look at the waveforms
        in PLECS right after a run. Every generated model should have one.

        axes: up to 3 of (axis title, [tag, ...]); each axis gets a Mux.
        pos: (x, y) of the Scope; Froms and Muxes are placed to its left.
        """
        assert 1 <= len(axes) <= 3, "the catalog Scope has 3 axes"
        x, y = pos
        ys = [y - 10, y, y + 10][:len(axes)] if len(axes) == 3 else \
            [y - 5, y + 5][:len(axes)] if len(axes) == 2 else [y]
        rows = [y - 45, y, y + 50][:len(axes)]
        b = pe.new_block("Scope", name, pos)
        for title, _ in axes:
            b = b.replace('      Axis {\n        Name          ""\n',
                          '      Axis {\n        Name          "%s"\n' % title, 1)
        self.names.add(name)
        self.comps.append(b)
        for k, ((title, tags), ry, ty) in enumerate(zip(axes, rows, ys)):
            n = len(tags)
            pts = None if ry == ty else [(x - 60, ry), (x - 60, ty)]
            if n == 1:  # a 1-input Mux is drawn red by PLECS: wire directly
                f = self.from_(tags[0], (x - 180, ry), suffix="_%s%d_1" % (name, k + 1))
                self.wire(f, 1, name, 1 + k, pts)
                continue
            mux = self.add("SignalMux", "%s_mux%d" % (name, k + 1), (x - 120, ry),
                           {"Width": str(n)}, show_name=False)
            for j, tag in enumerate(tags):
                self.from_(tag, (x - 180, ry - 5 * (n - 1) + 10 * j), mux, 2 + j,
                           suffix="_%s%d_%d" % (name, k + 1, j + 1))
            self.wire(mux, 1, name, 1 + k, pts)
        return name

    def frame(self, left, top, right, bottom, title=None):
        self.notes.append(pe.rect_annotation(left, top, right, bottom))
        if title:
            self.notes.append(pe.text_annotation([title], ((left + right) // 2, top - 15)))

    def text(self, lines, center):
        self.notes.append(pe.text_annotation(lines, center))

    def render(self):
        head = pe.replace_once(self.head, "  Schematic {\n",
                               "".join(self.terms) + "  Schematic {\n")
        return (head + "".join(self.comps) + "".join(self.conns)
                + "".join(self.notes) + "  }\n}\n")

    def write(self, path, overwrite=False):
        """Check and write. An existing file is not replaced unless
        overwrite=True: the user may have edited the model in PLECS since."""
        assert overwrite or not os.path.exists(path), (
            "%s exists (maybe edited in PLECS). Write a new file name, or "
            "pass overwrite=True if it is known to be untouched." % path)
        text = self.render()
        errors, _ = check(text)
        assert not errors, "\n".join(errors)
        pe.write(path, text)
        return path
