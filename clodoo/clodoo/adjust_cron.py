#! /usr/bin/python3
"""
Adjust cron next call
Since odoo12.0, cron model changed: function was replaced by action_server
id / id
function / ir_actions_server_id
name / cron_name
args /
user_id / user_id
active / active
numbercall / numbercall
nextcall / nextcall
priority / priority
interval_type / interval_type
do_all / do_all
model /

"""
from datetime import datetime, timedelta, timezone
from subprocess import PIPE, Popen
import sys
import pytz
# import pdb; pdb.set_trace()


def os_system(cmd):
    prc = Popen(cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE)
    out, err = prc.communicate()
    sts = prc.wait()
    return sts, out.decode("utf8"), err.decode("utf8")


def extr_values(ln):
    # id,name/cron_name,interval_type,nextcall,priority,doall,interval_number,model/
    res = ln.split("|")
    id = int(res[0])
    name = res[1]
    intv_type = res[2]
    next = pytz.utc.localize(datetime.strptime(res[3][:19], "%Y-%m-%d %H:%M:%S"))
    prio = int(res[4])
    if intv_type == "minutes":
        minutes = int(res[6])
    elif intv_type == "days":
        minutes = int(res[6]) * 60 * 24
    elif intv_type == "weeks":
        minutes = int(res[6]) * 60 * 24 * 7
    else:
        minutes = 0
    return (id, name, intv_type, next, prio, minutes)


def eval_nextcall(name, minutes, next_ts):
    # ofs base offset since now (based on priority)
    # ofs2 supplemental offset since now
    if minutes > 0:
        ctr = 8192
        while next_ts < datetime.now(timezone.utc):
            next_ts = next_ts + timedelta(minutes=max(minutes, 3))
            ctr -= 1
            if not ctr:
                break
    return next_ts


def main(cli_args=[]):
    dry_run = force = help = port = False
    odoo_ver = "7"
    db = "cscs2016"
    param = ""
    for arg in cli_args:
        if arg.startswith("-"):
            if "f" in arg:
                force = True
            if "n" in arg:
                dry_run = True
            if "h" in arg:
                help = True
            if "p" in arg:
                param = "port"
            if "o" in arg:
                param = "odoo_ver"
        elif param:
            if param == "port":
                port = arg
            elif param == "odoo_ver":
                odoo_ver = arg.split(".")[0]
        else:
            db = arg
    if help:
        print("usage: cron_cscs [-f][-n][-o OVERSION][-p PORT][DBNAME]")
        exit(0)
    # utc=pytz.timezone("utc")
    if int(odoo_ver) < 12:
        fields = "id,name,interval_type,nextcall,priority,doall,interval_number,model"
    else:
        fields = "id,cron_name,interval_type,nextcall,priority,doall,interval_number"
    sql = "select %s from ir_cron where active=true order by nextcall" % fields
    cmd = ["psql"] if not port else ["psql", "-p", port]
    cmd = cmd + ["-Atc", sql, db]
    print(" ".join(cmd))
    sts, out, err = os_system(cmd)
    print(datetime.now(timezone.utc))
    print("cmd %s (%d)" % (" ".join(cmd), sts))
    if sts:
         print("Error")
         return sts
    for ln in out.split("\n"):
        if not ln:
            continue
        (id, name, intv_type, next, prio, minutes) = extr_values(ln)
        next_ts = eval_nextcall(name, minutes, next)
        ok = (next_ts == next)
        if ok and not force:
            print("%6d %-48.48s %s %s" % (id, name, next, "Ok" if ok else "(update)"))
            continue
        print("%6d %-48.48s %s %s" % (id, name, next_ts, "Ok" if ok else "(update)"))
        if dry_run:
            continue
        sql = "update ir_cron set nextcall='%s' where id=%d" % (
            next_ts.strftime("%Y-%m-%d %H:%M:%S"), id)
        cmd = ["psql"] if not port else ["psql", "-p", port]
        cmd = cmd + ["-c", sql, db]
        print(" ".join(cmd))
        sts, out, err = os_system(cmd)
        if sts:
            print("cmd <<<%s>>> failed" % " ".join(cmd))
    return sts


if __name__ == "__main__":
    exit(main(sys.argv[1:]))

