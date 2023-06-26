#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


def do_create_gitignore(path, submodules):
    root = os.environ.get("HOME_DEVEL")
    if not root or not os.path.isdir(root):
        if os.path.isdir(os.path.expanduser("~/odoo/devel")):
            root = os.path.expanduser("~/odoo/devel")
        elif os.path.isdir(os.path.expanduser("~/devel")):
            root = os.path.expanduser("~/devel")
        else:
            print("Development directory ~/devel not found!")
            return 1
    template = os.path.join(root, "pypi", "tools", "templates", "gitignore")
    if not os.path.isfile(template):
        print("Template %s not found!" % template)
        return 2
    target = ""
    with open(template, "r") as fd:
        trig = ""
        for line in fd.read().split("\n"):
            found = line.startswith("!")
            if trig == "odoo":
                for x in submodules:
                    if x == line:
                        found = True
                        break
            elif trig == "pypi":
                if (
                    # "/docs/_build/" not in line
                    ".egg-info/" not in line
                    and os.path.join(*[path] + [x for x in line.split("/") if x])
                ):
                    found = True
            if not trig or found:
                target += "%s\n" % line
            if line.startswith("# odoo repositories"):
                trig = "odoo"
            if line.startswith("# tools building path"):
                trig = "pypi"
    if target:
        ffn = os.path.join(path, ".gitignore")
        bakfile = "%s~" % ffn
        if os.path.isfile(bakfile):
            os.remove(bakfile)
        if os.path.isfile(ffn):
            os.rename(ffn, bakfile)
        with open(ffn, "w") as fd:
            fd.write(target)
            print("Created file %s" % ffn)


def main(argv=None):
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
        if not os.path.isdir(os.path.join(path, ".git")):
            print("Path %s is not a git project!" % sys.argv[0])
            return 1
        submodules = []
        for fn in os.listdir(path):
            if fn in (
                "addons_kalamitica",
                "coverage",
                "generic",
                "nardo_modules",
                "venv_odoo",
                "website-themes",
            ):
                submodules.append("/%s" % fn)
                continue
            ffn = os.path.join(path, fn)
            if os.path.isdir(os.path.join(ffn, ".git")):
                submodules.append("/%s" % fn)
        return do_create_gitignore(path, submodules)
    else:
        print("Path %s does not exist!" % sys.argv[0])
        return 2
    return 0


if __name__ == "__main__":
    exit(main())
