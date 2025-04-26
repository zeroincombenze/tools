#!/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
from subprocess import PIPE, Popen
from z0lib import z0lib
from python_plus import _u


def os_run(cmd):
    if sys.version_info[0] == 2:
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
        outs, errs = proc.communicate()
    else:
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            outs, errs = proc.communicate(timeout=60)
    return (
        outs.decode("utf-8") if outs else outs,
        errs.decode("utf-8") if errs else errs,
    )


def check_for_requirements(requirements=None):
    if not requirements:
        if os.path.isfile("egg-info/__manifest__.rst"):
            fqn = os.path.abspath("egg-info/__manifest__.rst")
        elif os.path.isfile("readme/__manifest__.rst"):
            fqn = os.path.abspath("readme/__manifest__.rst")
        else:
            z0lib.print_flush("No configuration file found!")
            return 126
        contents = requirements = ""
        if fqn:
            with open(fqn, "r") as fd:
                contents = _u(fd.read())
        for ln in contents.split("\n"):
            if ln.startswith(".. $set pg_requirements"):
                requirements = eval(ln[23:].strip())
                break
    sts = 0
    if not requirements:
        return sts
    for port, db in requirements:
        vid = "oca" + str(port - 8260) if port > 8200 else "odoo" + str(port - 8160)
        outs, errs = os_run(["ss", "-lt"])
        port_found = False
        if outs:
            pattern = "0.0.0.0:" + str(port)
            for ln in outs.split("\n"):
                if pattern in ln:
                    port_found = True
                    break
        if port_found:
            z0lib.print_flush("Instance %s running at %s [OK]" % (vid, port))
        else:
            z0lib.print_flush(
                "*** No Odoo instance running at port <%s> (name %s)!" % (port, vid)
            )
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
            z0lib.print_flush(
                "Instance %s with db %s, user admin/admin [OK]" % (vid, db)
            )
        else:
            z0lib.print_flush("*** No database <%s> found (name %s)!" % (db, vid))
            sts = 1
    if sts:
        z0lib.print_flush("*** TEST FAILED!!!! ***")
    return sts


if __name__ == "__main__":
    exit(check_for_requirements())
