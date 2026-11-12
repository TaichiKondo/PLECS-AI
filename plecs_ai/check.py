"""Pre-load checks for an edited .plecs file (rule 6 of the plecs skill).

usage: python -m plecs_ai.check EDITED.plecs [ORIGINAL.plecs]
Exit code 0 only if every check passes. With ORIGINAL, prints the diff and the
decoded InitializationCommands so the change can be reviewed.
"""
import difflib
import re
import sys

from . import edit as pe


def strip_strings(line):
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)


def parse(text):
    """Very small parser: returns a tree of (key, value_or_children)."""
    root, stack = [], []
    cur = root
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith('"'):  # continuation of a wrapped string
            k, v = cur[-1]
            cur[-1] = (k, v[:-1] + s[1:])
            continue
        bare = strip_strings(s)
        if bare.endswith("{") and "}" not in bare:
            node = []
            cur.append((s[:-1].strip(), node))
            stack.append(cur)
            cur = node
        elif bare == "}":
            cur = stack.pop()
        else:
            k, _, v = s.partition(" ")
            cur.append((k, v.strip()))
    assert not stack, "unbalanced braces"
    return root


def children(node, key):
    return [v for k, v in node if k == key and isinstance(v, list)]


def value(node, key):
    for k, v in node:
        if k == key and not isinstance(v, list):
            return v
    return None


def check(text):
    errors = []
    # 1. braces (outside string literals)
    depth = 0
    for i, ln in enumerate(text.split("\n"), 1):
        bare = strip_strings(ln)
        depth += bare.count("{") - bare.count("}")
        if depth < 0:
            errors.append("line %d: closing brace without opening" % i)
        if len(ln) > pe.WIDTH:
            errors.append("line %d: %d chars > %d" % (i, len(ln), pe.WIDTH))
    if depth != 0:
        errors.append("brace depth at EOF is %d" % depth)
    if errors:
        return errors, None

    # PLECS silently drops connections that come after annotations
    for sch in re.finditer(r"\n( *)Schematic \{\n", text):
        ind = sch.group(1) + "  "
        body = text[sch.end():]
        first_note = re.search(r"\n%s(?:Rectangle)?Annotation \{" % ind, "\n" + body)
        if first_note and re.search(r"\n%sConnection \{" % ind,
                                    ("\n" + body)[first_note.end():].split(
                                        "\n" + sch.group(1) + "}")[0]):
            errors.append("Connection after an annotation in a Schematic: "
                          "PLECS ignores it (put connections first)")
    if errors:
        return errors, None

    tree = parse(text)
    plecs = children(tree, "Plecs")[0]
    sch = children(plecs, "Schematic")[0]
    comps = children(sch, "Component")

    # 2. unique component names
    names = [value(c, "Name") for c in comps]
    for n in set(names):
        if names.count(n) > 1:
            errors.append("duplicate component name %s" % n)

    # 3./4. connections: endpoints exist, each terminal used once
    used = {}

    def walk(conn, top):
        for k in ("SrcComponent", "DstComponent"):
            n = value(conn, k)
            if n is None:
                continue
            term = value(conn, k.replace("Component", "Terminal"))
            if n not in names:
                errors.append("connection to unknown component %s" % n)
            key = (n, term)
            used[key] = used.get(key, 0) + 1
        has_dst = value(conn, "DstComponent") is not None
        br = children(conn, "Branch")
        if has_dst == bool(br):
            errors.append("connection from %s: needs either Dst or Branches"
                          % value(top, "SrcComponent"))
        for b in br:
            walk(b, top)

    for c in children(sch, "Connection"):
        if value(c, "Type") not in ("Wire", "Signal", "Rotational",
                                    "Translational", "Magnetic", "HeatPipe"):
            errors.append("bad connection type %s" % value(c, "Type"))
        walk(c, c)
    for (n, term), cnt in used.items():
        if cnt > 1:
            errors.append("terminal %s of %s used %d times" % (term, n, cnt))

    # 5. From / Goto tags
    def tag(c):
        for p in children(c, "Parameter"):
            if value(p, "Variable") == '"Tag"':
                return value(p, "Value")
    gotos = [tag(c) for c in comps if value(c, "Type") == "Goto"]
    for g in set(gotos):
        if gotos.count(g) > 1:
            errors.append("duplicate Goto tag %s" % g)
    for c in comps:
        if value(c, "Type") == "From" and tag(c) not in gotos:
            errors.append("From tag %s has no Goto" % tag(c))

    # 6. top-level outports <-> Terminal declarations
    n_term = len([t for t in children(plecs, "Terminal")])
    n_out = len([c for c in comps if value(c, "Type") in ("Output", "Input")])
    if n_term != n_out:
        errors.append("%d top-level Terminal entries but %d port blocks"
                      % (n_term, n_out))

    # 7. model name
    info = {"name": value(plecs, "Name"), "components": len(comps),
            "connections": len(children(sch, "Connection"))}
    return errors, info


def main():
    path = sys.argv[1]
    text = pe.read(path)  # asserts ASCII + CRLF
    errors, info = check(text)
    if info:
        print("model %(name)s: %(components)d components, "
              "%(connections)d connections" % info)
        import os
        stem = os.path.splitext(os.path.basename(path))[0]
        if info["name"] != '"%s"' % stem:
            errors.append("model Name %s does not match file name" % info["name"])
    if len(sys.argv) > 2:
        orig = pe.read(sys.argv[2])
        # round trip: our wrapper must reproduce PLECS' own wrapping
        assert pe.set_init_commands(orig, pe.get_init_commands(orig)) == orig, \
            "string wrapping does not round-trip on the original"
        print("---- InitializationCommands ----")
        print(pe.get_init_commands(text))
        print("---- diff against %s ----" % sys.argv[2])
        d = list(difflib.unified_diff(orig.split("\n"), text.split("\n"),
                                      lineterm="", n=1))
        print("\n".join(d))
        print("---- %d diff lines ----" % len(d))
    for e in errors:
        print("ERROR:", e)
    print("CHECK", "FAILED" if errors else "OK")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
