# -*- coding: utf-8 -*-
import os.path
import sys
import re


PG_PARAMS = {
    "9.5": {"port": 5437, "users": ["librerp6", "oca6", "oca7"]},
    "10": {"port": 5433, "users": ["odoo6", "oca8", "oca9"]},
    "12": {
        "port": 5432,
        "users": [
            "odoo7",
            "odoo8",
            "odoo9",
            "odoo10",
            "oca10",
            "odoo11",
            "oca11",
            "odoo12",
            "oca12",
            "odoo13",
            "oca13",
            "odoo14",
            "oca14",
            "odoo15",
            "oca15",
            "odoo15",
            "oca15",
            "odoo16",
            "oca16",
            "odoo17",
            "oca17",
            "odoo_www",
            "weblate",
            "librerp12",
            "kalamitica",
        ],
    },
    "14": {
        "port": 5434,
        "users": [
            "odoo16",
            "oca16",
            "odoo16",
            "oca16",
            "odoo17",
            "oca17",
            "odoo17",
            "oca17",
        ],
    },
    "15": {
        "port": 5435,
        "users": [
            "odoo17",
            "oca17",
            "odoo17",
            "oca17",
            "odoo18",
            "oca18",
            "odoo18",
            "oca18",
        ],
    },
    "16": {
        "port": 5436,
        "users": [
            "odoo17",
            "oca17",
            "odoo17",
            "oca17",
            "odoo18",
            "oca18",
            "odoo18",
            "oca18",
        ],
    },
}
ALL_ODOO_VERS = (
    "17.0",
    "16.0",
    "15.0",
    "14.0",
    "13.0",
    "12.0",
    "11.0",
    "10.0",
    "9.0",
    "8.0",
    "7.0",
    "6.1",
)


def replace_port_in_file(fqn, regex, port):
    if not os.path.isfile(fqn):
        print("File %s not found!" % fqn)
        exit(3)
    with open(fqn, "r") as fd:
        content = fd.read()
    new_content = ""
    updated = False
    for ln in content.split("\n"):
        if re.match(regex, ln):
            new_ln = regex[1:] + " " + str(port)
            if new_ln != ln:
                ln = new_ln
                updated = True
        new_content += ln + "\n"
    if updated:
        with open(fqn, "w") as fd:
            fd.write(new_content)


def replace_user_in_pgfile(fqn, replacements):
    if not os.path.isfile(fqn):
        print("File %s not found!" % fqn)
        exit(3)
    try:
        with open(fqn, "r") as fd:
            content = fd.read()
    except BaseException:
        print("Cannot update file %s" % fqn)
        return
    new_content = ""
    susp = False
    for ln in content.split("\n"):
        if ln == (
            "# TYPE  DATABASE        USER            " "ADDRESS                 METHOD"
        ):
            new_content += ln + "\n"
            new_content += replacements
            susp = True
        elif ln.startswith("#"):
            susp = False
        if susp:
            continue
        new_content += ln + "\n"
    while new_content.endswith("\n\n"):
        new_content = new_content[:-2]
    if not new_content.endswith("\n"):
        new_content += "\n"
    while content.endswith("\n\n"):
        content = content[:-2]
    if not content.endswith("\n"):
        content += "\n"
    if new_content != content:
        try:
            with open(fqn, "w") as fd:
                fd.write(new_content)
        except BaseException:
            print("Cannot update file %s" % fqn)


def search_pg_ver(user):
    def_pg_ver = ""
    for pg_ver in ["9.5"] + sorted([x for x in PG_PARAMS.keys() if x != "9.5"]):
        for uu in sorted(PG_PARAMS[pg_ver]["users"]):
            if uu == user:
                def_pg_ver = pg_ver
                break
    return def_pg_ver


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    print("")
    print("=" * 60)
    method = "trust"
    for pg_ver in ["9.5"] + sorted([x for x in PG_PARAMS.keys() if x != "9.5"]):
        print("Postgres %s -> %s" % (pg_ver, PG_PARAMS[pg_ver]["port"]))
        fqn = "/etc/postgresql/%s/main/postgresql.conf" % pg_ver
        print("File %s" % fqn)
        print("  port = %s" % PG_PARAMS[pg_ver]["port"])
        replace_port_in_file(fqn, "^port =", PG_PARAMS[pg_ver]["port"])
        fqn = "/etc/postgresql/%s/main/pg_hba.conf" % pg_ver
        if not os.path.isfile(fqn):
            print("File %s not found!" % fqn)
            continue
        print("File " + fqn)
        print("")
        replacements = ""
        for user in sorted(PG_PARAMS[pg_ver]["users"], reverse=True):
            ln = "local   all             %-39.39s %s" % (user, method)
            replacements += ln + "\n"
            print(ln)
            ln = "host    all             %-15.15s 127.0.0.1/32            %s" % (
                user,
                method,
            )
            replacements += ln + "\n"
            print(ln)
            ln = "host    all             %-15.15s ::1/128                 %s" % (
                user,
                method,
            )
            replacements += ln + "\n"
            print(ln)
        replacements += "\n"
        replace_user_in_pgfile(fqn, replacements)
        print("")
    print("")
    print("=" * 60)
    for odoo_ver in ALL_ODOO_VERS:
        odoo_major = eval(odoo_ver.split(".")[0])
        user = "odoo" + odoo_ver.split(".")[0]
        pg_ver = search_pg_ver(user)
        print("")
        fqn = "/etc/odoo/odoo%s%s.conf" % (
            odoo_major,
            "-server" if odoo_major < 10 else "",
        )
        print("File %s" % fqn)
        print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
        print("  db_user = %s" % user)
        replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])
        user = "oca" + odoo_ver.split(".")[0]
        pg_ver = search_pg_ver(user)
        print("")
        fqn = "/etc/odoo/odoo%s-oca.conf" % odoo_major
        print("File %s" % fqn)
        print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
        print("  db_user = %s" % user)
        replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])
        if odoo_ver in ("12.0", "6.1"):
            user = "librerp" + odoo_ver.split(".")[0]
            pg_ver = search_pg_ver(user)
            print("")
            fqn = "/etc/odoo/odoo%s-librerp.conf" % odoo_major
            print("File %s" % fqn)
            if os.path.isfile(fqn):
                print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
                print("  db_user = %s" % user)
                replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])
        if odoo_ver == "12.0":
            user = "kalamitica"
            pg_ver = search_pg_ver(user)
            print("")
            fqn = "/etc/odoo/odoo%s-kalamitica.conf" % odoo_major
            print("File %s" % fqn)
            print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
            print("  db_user = %s" % user)
            replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])

            fqn = "/etc/odoo/odoo%s-giolo.conf" % odoo_major
            print("File %s" % fqn)
            print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
            print("  db_user = %s" % user)
            replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])

            pg_ver = search_pg_ver(user)
            print("")
            fqn = "/etc/odoo/odoo%s-www_zeroincombenze.conf" % odoo_major
            print("File %s" % fqn)
            if os.path.isfile(fqn):
                print("File %s" % fqn)
                print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
                print("  db_user = %s" % user)
                replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])
            fqn = "/etc/odoo/odoo%s-wwww_shs_av.conf" % odoo_major
            print("File %s" % fqn)
            if os.path.isfile(fqn):
                print("File %s" % fqn)
                print("  db_port = %s" % PG_PARAMS[pg_ver]["port"])
                print("  db_user = %s" % user)
                replace_port_in_file(fqn, "^db_port =", PG_PARAMS[pg_ver]["port"])
    print("")
    print("=" * 60)
    for pg_ver in ["9.5"] + sorted([x for x in PG_PARAMS.keys() if x != "9.5"]):
        if pg_ver == "12":
            continue
        print("alias psql-%s='psql -p%s'" % (pg_ver, PG_PARAMS[pg_ver]["port"]))

    print("")
    print("=" * 60)
    print("sudo su - postgres")
    for pg_ver in ["9.5"] + sorted([x for x in PG_PARAMS.keys() if x != "9.5"]):
        cmd = "psql%s" % ("" if pg_ver == "12" else ("-" + pg_ver))
        for odoo_ver in ALL_ODOO_VERS:
            user = "odoo" + odoo_ver.split(".")[0]
            print(
                '%s template1 -c "create role %s with superuser createdb login"'
                % (cmd, user)
            )
            user = "oca" + odoo_ver.split(".")[0]
            print(
                '%s template1 -c "create role %s with superuser createdb login"'
                % (cmd, user)
            )
    return 0


if __name__ == "__main__":
    exit(main())
