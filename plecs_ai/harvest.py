"""Add block types to the catalog from .plecs files saved by PLECS.

usage: python -m plecs_ai.harvest FILE_OR_DIR [...] [--force]

Every leaf component (at any subsystem depth) whose type is not in
plecs_ai/blocks/ yet is stored, re-indented to top level, as
blocks/<key>.plecs. Components that carry their own schematic (Subsystem,
ConfigurableSubsystem, ...) and model references are skipped: they are not
self-contained blocks.

blocks/INDEX.md is regenerated from all catalog entries and the terminal
usage seen in every scanned file (terminal number, src = output side /
dst = input side, Signal or Wire). Meanings of the terminals go into
.claude/skills/plecs/reference/blocks.md by hand.
--force overwrites existing catalog entries.
"""
import collections
import json
import os
import re
import sys

from . import edit as pe

SKIP_TYPES = {"Subsystem", "ConfigurableSubsystem", "ModelReference"}
USAGE_FILE = os.path.join(pe.BLOCKS_DIR, "usage.json")


def read_any(path):
    """PLECS text in either CRLF (Standalone save) or LF (shipped demos)."""
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("ascii").replace("\r\n", "\n")


def blocks(text, keyword):
    """Yield (indent, block_text) for every 'keyword {' block at any depth."""
    lines = text.split("\n")
    open_re = re.compile(r"^( *)%s \{$" % keyword)
    for i, ln in enumerate(lines):
        m = open_re.match(ln)
        if not m:
            continue
        ind = m.group(1)
        for j in range(i + 1, len(lines)):
            if lines[j] in (ind + "}", ind + "} "):
                yield len(ind), "\n".join(lines[i:j + 1]) + "\n"
                break


def reindent(block, indent):
    shift = indent - 4
    out = []
    for ln in block.split("\n"):
        if ln.startswith('"'):  # continuation of a wrapped string
            out.append(ln)
        else:
            assert ln[:shift].strip() == "", ln
            out.append(ln[shift:])
    return "\n".join(out)


def schematics(text):
    """Yield (indent of children, schematic body) for every Schematic."""
    for ind, body in blocks(text, "Schematic"):
        yield ind + 2, body


def direct(body, keyword, child_indent):
    for ind, blk in blocks(body, keyword):
        if ind == child_indent:
            yield blk


def scan(text):
    """(components, usage) of one file.

    components: list of (key, top-level block text)
    usage: {key: set((terminal, 'src'|'dst', kind))}
    """
    comps, usage = [], collections.defaultdict(set)
    for ci, body in schematics(text):
        names = {}
        for blk in direct(body, "Component", ci):
            blk4 = reindent(blk, ci)
            typ = re.search(r"\n      Type          (\S+)\n", blk4)
            if not typ or typ.group(1) in SKIP_TYPES or "Schematic {" in blk4:
                continue
            if not re.search(r'\n      Name          (base64 )?"', blk4):
                continue
            key = pe.block_key(blk4)
            name = re.search(r'\n      Name          ((?:base64 )?"[^"\n]*")\n',
                             blk4).group(1)
            names[name] = key
            comps.append((key, blk4))
        for conn in direct(body, "Connection", ci):
            kind = re.search(r"Type +(\w+)", conn).group(1)
            for m in re.finditer(r'(Src|Dst)Component +((?:base64 )?"[^"\n]*")\n'
                                 r" +(?:Src|Dst)Terminal +(\d+)", conn):
                if m.group(2) in names:
                    usage[names[m.group(2)]].add(
                        (int(m.group(3)), m.group(1).lower(), kind))
    return comps, usage


def write_index(usage, sources):
    rows = []
    for key in pe.list_blocks():
        blk = pe.read(os.path.join(pe.BLOCKS_DIR, key + ".plecs"))
        typ = re.search(r"\n      Type          (\S+)\n", blk).group(1)
        params = re.findall(r'\n        Variable      "([^"]*)"', blk)
        terms = collections.defaultdict(set)
        for t, side, kind in usage.get(key, []):
            terms[t].add(("out" if side == "src" else "in") +
                         ("" if kind == "Signal" else "/" + kind.lower()))
        tdesc = ", ".join("%d:%s" % (t, "+".join(sorted(v)))
                          for t, v in sorted(terms.items())) or "-"
        lib = typ
        if typ == "Reference":
            m = re.search(r'\n      SrcComponent  "([^"\n]*)"\n((?:"[^\n]*"\n)*)',
                          blk)
            lib = (m.group(1) + "".join(ln[1:-1] for ln in m.group(2).split("\n")
                                        if ln)).replace("\\\\n", " ")
        rows.append("| `%s` | %s | %s | %s | %s |" % (
            key, lib, tdesc, ", ".join(params) or "-",
            sources.get(key, "")))
    with open(os.path.join(pe.BLOCKS_DIR, "INDEX.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("# ブロックのカタログ（自動生成）\n\n"
                "`python -m plecs_ai.harvest` が生成する。手で編集しない。"
                "端子の意味は `.claude/skills/plecs/reference/blocks.md` に書く。\n\n"
                "端子：番号:in／out（`/wire` は電気、`/magnetic` などはその他の物理領域。"
                "無印は信号）。取り込んだファイルの配線で使われていたものだけを示す。\n\n"
                "| キー | 種類（Typeまたはライブラリ） | 端子 | パラメータ | 取り込み元 |\n"
                "|---|---|---|---|---|\n")
        f.write("\n".join(rows) + "\n")
    return len(rows)


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    files = []
    for a in args:
        if os.path.isdir(a):
            for root, _, fs in os.walk(a):
                files += [os.path.join(root, f) for f in fs if f.endswith(".plecs")]
        else:
            files.append(a)
    files.sort()

    try:
        with open(USAGE_FILE, encoding="utf-8") as f:
            stored = json.load(f)
    except FileNotFoundError:
        stored = {"usage": {}, "sources": {}}
    usage = {k: set(map(tuple, v)) for k, v in stored["usage"].items()}
    sources = stored["sources"]

    known = set(pe.list_blocks())
    added, failed = [], []
    for path in files:
        try:
            comps, use = scan(read_any(path))
        except (UnicodeDecodeError, AssertionError) as e:
            failed.append((path, repr(e)[:80]))
            continue
        rel = os.path.basename(path)
        for key, u in use.items():
            usage.setdefault(key, set()).update(u)
        for key, blk in comps:
            if key in known and not (force and key not in added):
                continue
            if not re.fullmatch(r"[A-Za-z0-9_]+", key):
                continue
            pe.write(os.path.join(pe.BLOCKS_DIR, key + ".plecs"), blk)
            known.add(key)
            added.append(key)
            sources[key] = rel

    with open(USAGE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"usage": {k: sorted(v) for k, v in sorted(usage.items())},
                   "sources": dict(sorted(sources.items()))}, f, indent=0)
    n = write_index(usage, sources)
    print("scanned %d files, added %d types, catalog has %d"
          % (len(files), len(added), n))
    if added:
        print("added: " + ", ".join(sorted(added)))
    for path, err in failed:
        print("FAILED %s: %s" % (path, err))


if __name__ == "__main__":
    main()
