#!/bin/python

import os
# import subprocess
from subprocess import PIPE, Popen


def os_run(cmd):
    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        outs, errs = proc.communicate(timeout=60)
    return (outs.decode("utf-8") if outs else outs,
            errs.decode("utf-8") if errs else errs)


def check_for_requirements(requirements=None):
    if not requirements:
        if os.path.isfile("egg-info/__manifest__.rst"):
            fqn = os.path.abspath("egg-info/__manifest__.rst")
        elif os.path.isfile("readme/__manifest__.rst"):
            fqn = os.path.abspath("readme/__manifest__.rst")
        else:
            fqn = ""
        contents = requirements = ""
        if fqn:
            with open(fqn, "r") as fd:
                contents = fd.read()
        for ln in contents.split("\n"):
            if ln.startswith(".. $set pg_requirements"):
                requirements = eval(ln[23:].strip())
                break
    sts = 0
    if not requirements:
        return sts
    for (port, db) in requirements:
        vid = "oca" + str(port - 8260) if port > 8200 else "oca" + str(port - 8160)
        outs, errs = os_run(["ss", "-lt"])
        port_found = False
        if outs:
            pattern = "0.0.0.0:" + str(port)
            for ln in outs.split("\n"):
                if pattern in ln:
                    port_found = True
                    break
        if port_found:
            print("Instance %s running at %s [OK]" % (vid, port))
        else:
            print("*** No Odoo instance running at port <%s> (name %s)!" % (port,
                                                                            vid))
            sts = 1
        outs, errs = os_run(["psql", "-Atl"])
        db_found = False
        if outs:
            pattern = db + "|"
            for ln in outs.split("\n"):
                if ln.startswith(pattern):
                    db_found = True
                    break
        if db_found:
            print("Instance %s with db %s, user admin/admin [OK]" % (vid, db))
        else:
            print("*** No database <%s> found (name %s)!" % (db, vid))
            sts = 1
    if sts:
        print("*** TEST FAILED!!!! ***")
    return sts


if __name__ == "__main__":
    exit(check_for_requirements())
