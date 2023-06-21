#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


TAG = "# -*- coding: utf-8 -*-"
UNTAG = "# -*- encoding: utf-8 -*-"


def do_set_utf8(ffn):
    found_tag = False
    with open(ffn, "r") as fd:
        lines = fd.read().split("\n")
        coding_line = -1
        rm_lines = []
        for nro, line in enumerate(lines):
            if line == TAG:
                if coding_line < 0:
                    found_tag = True
                    coding_line = nro
                    continue
                rm_lines.append(nro)
                continue
            elif line == UNTAG:
                rm_lines.append(nro)
                continue
            elif line.startswith("# flake8:") or line.startswith("# pylint:"):
                if coding_line:
                    rm_lines.append(coding_line)
                    found_tag = False
                    coding_line = -1
                    continue
            if coding_line < 0 and (
                not line
                or (
                    (not line.startswith("#!") or nro)
                    and not line.startswith("# flake8:")
                    and not line.startswith("# pylint:")
                )
            ):
                coding_line = nro
            if not line or not line.startswith("#") or nro > 3:
                break
        for nro in sorted(rm_lines, reverse=True):
            if nro < coding_line:
                coding_line -= 1
            del lines[nro]
        if not found_tag and coding_line >= 0:
            lines.insert(coding_line, TAG)
    if not found_tag or rm_lines:
        bakfile = "%s~" % ffn
        if os.path.isfile(bakfile):
            os.remove(bakfile)
        if os.path.isfile(ffn):
            os.rename(ffn, bakfile)
        with open(ffn, "w") as fd:
            fd.write("\n".join(lines))
            print(ffn)


def main(argv):
    argv = argv or sys.argv[1:]
    path = None
    for param in argv:
        if param.startswith("-"):
            pass
        else:
            path = os.path.expanduser(param)
    if not path:
        print("No path supplied! Use %s PATH" % sys.argv[0])
        return 1
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            if "setup" in dirs:
                del dirs[dirs.index("setup")]
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                ffn = os.path.join(root, fn)
                do_set_utf8(ffn)
    elif os.path.isfile(path):
        do_set_utf8(path)
    else:
        print("Path %s does not exist!" % sys.argv[0])
        return 2
    return 0


if __name__ == "__main__":
    exit(main(None))
