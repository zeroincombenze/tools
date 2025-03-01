#!/bin/python3
import subprocess


REQUIREMENTS = [
    (8170, "test10"),
    (8172, "test12"),
    (8168, "test18"),
    (8167, "test7"),
    (8174, "test141"),
]


def run(cmd):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        outs, errs = proc.communicate(timeout=15)
    return (outs.decode("utf-8") if outs else outs,
            errs.decode("utf-8") if errs else errs)


def check_for_requirements(requirements):
    sts = 0
    for (port, db) in requirements:
        vid = "oca" + str(port - 8260) if port > 8200 else "oca" + str(port - 8160)
        outs, errs = run(["ss", "-lt"])
        port_found = False
        if outs:
            pattern = "0.0.0.0:" + str(port)
            for ln in outs.split("\n"):
                if pattern in ln:
                    port_found = True
                    break
        if not port_found:
            print("No Odoo instance running found at port <%s> (instance %s)" % (port,
                                                                                 vid))
            sts = 1
        outs, errs = run(["psql", "-Atl"])
        db_found = False
        if outs:
            pattern = db + "|"
            for ln in outs.split("\n"):
                if ln.startswith(pattern):
                    db_found = True
                    break
        if not db_found:
            print("No database <%s> found (instance %s)!" % (db, vid))
            sts = 1
    return sts


exit(check_for_requirements(REQUIREMENTS))
