"""Helpers for scripted edits of .plecs files.

All functions work on LF text; read()/write() convert from/to CRLF + ASCII.
The "rules" mentioned in comments are the editing rules of the plecs skill
(.claude/skills/plecs/SKILL.md).
"""
import os
import re

WIDTH = 79


def read(path):
    with open(path, "rb") as f:
        raw = f.read()
    raw.decode("ascii")  # rule 3: file must be pure ASCII
    assert b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b""), \
        "expected CRLF line endings"
    return raw.decode("ascii").replace("\r\n", "\n")


def write(path, text):
    assert "\r" not in text
    with open(path, "wb") as f:
        f.write(text.replace("\n", "\r\n").encode("ascii"))


def replace_once(text, old, new):
    """Rule 4: the target must occur exactly once."""
    n = text.count(old)
    assert n == 1, "expected exactly 1 occurrence, found %d: %r" % (n, old[:60])
    return text.replace(old, new)


def component_span(text, name):
    """(start, end) of the top-level 'Component { ... }' block with this Name.

    name is the string as written in the file (escapes such as \\n included).
    """
    key = '\n      Name          "%s"\n' % name
    assert text.count(key) == 1, "component name not unique/found: %r" % name
    pos = text.index(key)
    start = text.rindex("\n    Component {\n", 0, pos) + 1
    end = text.index("\n    }\n", pos) + len("\n    }\n")
    return start, end


def get_component(text, name):
    s, e = component_span(text, name)
    return text[s:e]


def replace_in_component(text, name, old, new):
    """Rule 4: narrow to one component first, then replace exactly once."""
    s, e = component_span(text, name)
    return text[:s] + replace_once(text[s:e], old, new) + text[e:]


def set_block_param(block, variable, value):
    """Change one Parameter's Value inside a single component's text.

    The old value may be wrapped over several lines; the new one is wrapped
    the same way when it is long. value is the string as stored in the file.
    """
    pat = re.compile(r'(        Variable      "%s"\n)        Value         '
                     r'"[^"\n]*"\n(?:"[^\n]*"\n)*' % re.escape(variable))
    assert len(pat.findall(block)) == 1, variable
    return pat.sub(lambda m: m.group(1) + wrap_string(
        "        Value         ", value), block)


def set_param(text, name, variable, value):
    """Change the Value of one Parameter of one component."""
    s, e = component_span(text, name)
    block = set_block_param(text[s:e], variable, value)
    return text[:s] + block + text[e:]


def clone_component(text, src_name, new_name, position, edits=()):
    """Copy an existing component (rule 2), rename and move it.

    edits: sequence of (old, new) applied exactly once inside the copy.
    """
    block = get_component(text, src_name)
    block = replace_once(block, '      Name          "%s"\n' % src_name,
                         '      Name          "%s"\n' % new_name)
    block = re.sub(r"\n      Position      \[[^\]]*\]\n",
                   "\n      Position      [%d, %d]\n" % position, block, count=1)
    for old, new in edits:
        block = replace_once(block, old, new)
    return block


# ---- block catalog (plecs_ai/blocks/*.plecs, filled by plecs_ai.harvest) -----

BLOCKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocks")
_NAME_LINE = re.compile(r'\n      Name          (?:base64 )?"[^"\n]*"\n')
_POS_LINE = re.compile(r"\n      Position      \[[^\]]*\]\n")


def iter_components(text):
    """Yield the text of every top-level Component block."""
    for m in re.finditer(r"(?<=\n)    Component \{\n.*?\n    \}\n", text, re.S):
        yield m.group(0)


def block_key(block):
    """Catalog key: the Type, or the library name for library references."""
    typ = re.search(r"\n      Type          (\S+)\n", block).group(1)
    if typ != "Reference":
        return typ
    m = re.search(r'\n      SrcComponent  "([^"\n]*)"\n((?:"[^\n]*"\n)*)', block)
    src = m.group(1) + "".join(ln[1:-1] for ln in m.group(2).split("\n") if ln)
    # library paths escape a "/" inside a name, e.g. "Machine (6\/4)"
    leaf = re.split(r"(?<!\\)/", src)[-1].replace("\\\\n", " ")
    return re.sub(r"[^A-Za-z0-9]+", "_", leaf).strip("_")


def list_blocks():
    return sorted(f[:-6] for f in os.listdir(BLOCKS_DIR) if f.endswith(".plecs"))


def new_block(key, name, position, params=None):
    """A component from the catalog, renamed, placed and parameterised.

    Only block types that PLECS itself has saved once are in the catalog
    (rule 2: never guess the format of a block). Add types with
    'python -m plecs_ai.harvest'. name must be ASCII.
    """
    path = os.path.join(BLOCKS_DIR, key + ".plecs")
    assert os.path.exists(path), \
        "block %r is not in the catalog; available: %s" % (key, list_blocks())
    block = read(path)
    assert len(_NAME_LINE.findall(block)) == 1 and len(_POS_LINE.findall(block)) == 1
    block = _NAME_LINE.sub(lambda m: '\n      Name          "%s"\n' % name, block)
    block = _POS_LINE.sub("\n      Position      [%d, %d]\n" % position, block)
    for var, val in (params or {}).items():
        block = set_block_param(block, var, val)
    if key in ("SignalMux", "SignalDemux") and re.fullmatch(r"\d+", str(
            (params or {}).get("Width", ""))):
        block = set_frame(block, (-2, -5 * int(params["Width"]),
                                  7, 5 * int(params["Width"])))
    return block


def set_frame(block, frame):
    """Set the Frame (left, top, right, bottom) of one component's text.

    Mux/Demux must be 10 per input high (frame +-5*Width), otherwise the
    terminals stick out of the bar (seen in a model the user fixed in PLECS).
    """
    line = "      Frame         [%d, %d; %d, %d]\n" % frame
    if re.search(r"\n      Frame +\[", block):
        return re.sub(r"\n      Frame +\[[^\]]*\]\n", "\n" + line, block, count=1)
    m = re.search(r"\n      LabelPosition +\S+\n", block)
    return block[:m.end()] + line + block[m.end():]


def swap_block(text, name, key, params=None, keep=()):
    """Replace a component by a catalog block of another type, in place.

    Name, Position, Direction, Flipped and LabelPosition are kept, so the
    wiring stays valid as long as the new type uses the same terminal
    numbers (check that with tests/block_tests.py first). keep: parameter
    names whose current values are copied over (e.g. gains and limits).
    """
    s, e = component_span(text, name)
    old = text[s:e]
    get = lambda k: re.search(r"\n      %s +([^\n]*)\n" % k, old).group(1)
    vals = {}
    for var in keep:
        m = re.search(r'        Variable      "%s"\n        Value         "([^"\n]*)"'
                      % re.escape(var), old)
        assert m, (name, var)
        vals[var] = m.group(1)
    vals.update(params or {})
    pos = tuple(int(v) for v in get("Position").strip("[]").split(","))
    new = new_block(key, name, pos, vals)
    for k in ("Direction", "Flipped", "LabelPosition", "Show"):
        new = re.sub(r"\n      %s +\S+\n" % k, "\n      %-13s %s\n" % (k, get(k)),
                     new, count=1)
    return text[:s] + new + text[e:]


def remove_component(text, name):
    """Delete a top-level component and every connection that touches it.

    Only plain connections (no Branch) may touch it; anything else is a
    wiring decision that has to be made by hand.
    """
    s, e = component_span(text, name)
    text = text[:s] + text[e:]
    for conn in re.findall(r"(?<=\n)    Connection \{\n.*?\n    \}\n", text, re.S):
        if re.search(r'Component  "%s"\n' % re.escape(name), conn):
            assert "Branch {" not in conn, "branched connection at %s" % name
            text = replace_once(text, conn, "")
    return text


def insert_components(text, blocks):
    """Rule 5: new components go right before the first Connection."""
    marker = "    Connection {\n"
    pos = text.index(marker)
    return text[:pos] + "".join(blocks) + text[pos:]


def append_connections(text, items):
    """Add connections and annotations to the top-level schematic.

    Connections go right after the last existing top-level Connection and
    annotations at the very end. Order matters: PLECS silently ignored
    connections placed after the annotations of a file saved by PLECS.
    """
    tail = "  }\n}\n"
    assert text.endswith(tail)
    conns = [c for c in items if c.startswith("    Connection {")]
    notes = [c for c in items if not c.startswith("    Connection {")]
    last = [m.end() for m in re.finditer(
        r"(?<=\n)    Connection \{\n.*?\n    \}\n", text, re.S)]
    pos = last[-1] if last else len(text) - len(tail)
    text = text[:pos] + "".join(conns) + text[pos:]
    return text[:-len(tail)] + "".join(notes) + tail


def connection(kind, src, src_t, dst, dst_t, points=None):
    s = "    Connection {\n      Type          %s\n" % kind
    s += '      SrcComponent  "%s"\n      SrcTerminal   %d\n' % (src, src_t)
    if points:
        s += "      Points        [%s]\n" % points
    s += '      DstComponent  "%s"\n      DstTerminal   %d\n    }\n' % (dst, dst_t)
    return s


# ---- annotations (format copied from frames the user drew in PLECS) ---------

def text_annotation(lines, center):
    """Text note. lines: list of plain-text lines; center: (x, y) of the box.

    Non-ASCII text is stored as base64 of the UTF-8 HTML, like PLECS does.
    """
    for ln in lines:
        assert not set(ln) & set('<>&"\\'), ln
    html = "<html><body>\n" + "\n".join("<p>%s</p>" % ln for ln in lines) \
        + "</body></html>"
    prefix = "      Name          "
    try:
        html.encode("ascii")
        name = wrap_string(prefix, html.replace("\n", "\\n"))
    except UnicodeEncodeError:
        import base64
        b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
        name = wrap_string(prefix + "base64 ", b64)
    return ("    Annotation {\n" + name
            + "      Position      [%d, %d]\n    } \n" % center)


def rect_annotation(left, top, right, bottom):
    """Black frame, 2 wide, no fill (same style as the user's frames)."""
    return ("    RectangleAnnotation {\n"
            "      Position     [%d, %d]\n"
            "      Width        %d\n"
            "      Height       %d\n"
            "      CornerRadius 3\n"
            "      Thickness    2\n"
            "      PenColor     4278190080\n"
            "      PenAlpha     1\n"
            "      BrushColor   0\n"
            "      BrushAlpha   0\n"
            "    } \n" % ((left + right) // 2, (top + bottom) // 2,
                          right - left, bottom - top))


# ---- wrapped string values (InitializationCommands etc.) -------------------

def wrap_string(prefix, escaped):
    """Format 'prefix "escaped"' with PLECS' 79-column continuation style.

    escaped is the string body as stored in the file (with \\n, \\" escapes).
    """
    lines, cur, room = [], prefix + '"', WIDTH - len(prefix) - 2
    i = 0
    while True:
        chunk = escaped[i:i + room]
        # never cut inside an escape sequence: an odd run of trailing
        # backslashes means the cut would split '\x'
        if i + room < len(escaped):
            while (len(chunk) - len(chunk.rstrip("\\"))) % 2 == 1:
                chunk = chunk[:-1]
        lines.append(cur + chunk + '"')
        i += len(chunk)
        if i >= len(escaped):
            break
        cur, room = '"', WIDTH - 2
    return "\n".join(lines) + "\n"


def get_wrapped(text, key, indent="  "):
    """Return (start, end, escaped_body) of a possibly multi-line string."""
    m = re.search(r'^%s%s +"' % (indent, re.escape(key)), text, re.M)
    assert m, key
    start, pos, body = m.start(), m.end() - 1, ""
    while True:
        eol = text.index("\n", pos)
        line = text[pos:eol]
        assert line[0] == '"' and line[-1] == '"'
        body += line[1:-1]
        pos = eol + 1
        if text[pos] != '"':
            return start, pos, body


def get_init_commands(text):
    """Decoded InitializationCommands (real newlines)."""
    _, _, body = get_wrapped(text, "InitializationCommands")
    return body.replace("\\n", "\n")


def set_init_commands(text, commands):
    assert '"' not in commands and "\\" not in commands
    start, end, _ = get_wrapped(text, "InitializationCommands")
    new = wrap_string("  InitializationCommands ", commands.replace("\n", "\\n"))
    out = text[:start] + new + text[end:]
    assert get_init_commands(out) == commands
    return out


def set_model_name(text, old, new):
    return replace_once(text, 'Plecs {\n  Name          "%s"\n' % old,
                        'Plecs {\n  Name          "%s"\n' % new)
