#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re


def fmt_line(user, dbtype):
    if dbtype == "local":
        return "local\tall\t\t%s\t\t\t\t\ttrust" % user
    elif dbtype == "ipv4":
        return "host\tall\t\t%s\t\t127.0.0.1/32\t\ttrust" % user
    elif dbtype == "ipv6":
        return "host\tall\t\t%s\t\t::1/128\t\t\ttrust" % user
    return "###### INVALID LINE"


def do_conf_pg(ffn):
    found_tag = False
    done = False
    target = []
    # import pdb; pdb.set_trace()
    with open(ffn, "r") as fd:
        lines = fd.read().split("\n")
        for nro, line in enumerate(lines):
            if re.match(r"^[\s]*local[\s]*all[\s]*postgres", line):
                found_tag = True
            elif found_tag and re.match(r"^[\s]*local[\s]*all[\s]", line):
                if not done:
                    for role in ("odoo", "oca"):
                        for version in (
                            "",
                            "6",
                            "7",
                            "8",
                            "9",
                            "10",
                            "11",
                            "12",
                            "13",
                            "14",
                            "15",
                            "16",
                            "_www",
                        ):
                            if role == "oca" and version in ("", "6"):
                                continue
                            target.append(fmt_line("%s%s" % (role, version), "local"))
                            target.append(fmt_line("%s%s" % (role, version), "ipv4"))
                            target.append(fmt_line("%s%s" % (role, version), "ipv6"))
                    target.append(fmt_line("weblate", "local"))
                    target.append(fmt_line("weblate", "ipv4"))
                    target.append(fmt_line("weblate", "ipv6"))
                    target.append(fmt_line("kalamitica", "local"))
                    target.append(fmt_line("kalamitica", "ipv4"))
                    target.append(fmt_line("kalamitica", "ipv6"))
                    done = True
                continue
            target.append(line)

    if found_tag:
        bakfile = "%s.bak" % ffn
        if os.path.isfile(bakfile):
            os.remove(bakfile)
        if os.path.isfile(ffn):
            os.rename(ffn, bakfile)
        with open(ffn, "w") as fd:
            fd.write("\n".join(target))
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
        print("Supplied path is not a file")
        return 1
    elif os.path.isfile(path):
        do_conf_pg(path)
    else:
        print("Path %s does not exist!" % sys.argv[0])
        return 2
    return 0


if __name__ == "__main__":
    exit(main(None))
