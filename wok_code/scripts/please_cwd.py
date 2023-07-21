#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from datetime import datetime, timedelta
import re

import psycopg2

__version__ = "2.0.11"


class PleaseCwd(object):
    """NAME
        Various actions on current working directory.

    SYNOPSIS
        please [action] [cwd] [options]

        * clean: clean temporary file in current working directory and sub directories
        * defcon precommit|gitignore: set default values for some configuration files
        * docs: create project documentation from egg-info or readme directory
        * edit: edit pofile or other project file
        * replace: replace master local barnch of current package (only pypi pkgs)
        * translate: create it.po file with italian translation for Odoo module
        * update: update current package into devel virtual environment (only pypi pkgs)
        * wep_db: remove old databases

    DESCRIPTION
        This command creates execute one of %(actions)s
        on current working directory.

    OPTIONS
      %(options)s

    EXAMPLES
        please docs

    BUGS
        No known bugs.

    SEE ALSO
        Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>"""

    def __init__(self, please):
        self.please = please

    def action_opts(self, parser, for_help=False):
        self.please.add_argument(parser, "-B")
        self.please.add_argument(parser, "-b")
        self.please.add_argument(parser, "-c")
        if not for_help:
            self.please.add_argument(parser, "-n")
        self.please.add_argument(parser, "-f")
        if not for_help:
            self.please.add_argument(parser, "-q")
        self.please.add_argument(parser, "-v")
        parser.add_argument(
            "--no-verify", action="store_true", help="Disable pre-commit on replace"
        )
        parser.add_argument(
            "--odoo-venv", action="store_true", help="Update Odoo virtual environmens"
        )
        parser.add_argument(
            "--vme", action="store_true", help="Update $HOME/VME virtual environments"
        )
        parser.add_argument("args", nargs="*")
        return parser

    def do_clean(self):
        please = self.please
        is_odoo = please.is_odoo_pkg()
        is_pypi = please.is_pypi_pkg()
        if (
                is_odoo
                or is_pypi
                or please.is_repo_odoo()
                or please.is_repo_ocb()
        ):
            sts = 0
            for root, dirs, files in os.walk(
                    os.path.dirname(os.getcwd())
                    if is_pypi and os.path.basename(os.getcwd()) != "tools"
                    else os.getcwd()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + os.path.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        break
            logdir = os.path.join(os.getcwd(), "tests", "logs")
            if is_odoo and os.path.isdir(logdir):
                last = " "
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_[0-9]{8}.txt$", fn) and fn[12:] > last:
                            last = fn[12:]
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_[0-9]{8}.txt$", fn) and fn[12:] != last:
                            cmd = "rm " + os.path.join(root, fn)
                            sts = please.run_traced(cmd)
                            if sts:
                                break
            return sts
        return please.do_iter_action("do_clean", act_all_pypi=True, act_tools=True)

    def do_clean_db(self):
        def connect_db():
            return psycopg2.connect(
                dbname="template1",
                user="odoo",
            )

        please = self.please
        sts = 126
        remove_ts = datetime.now() - timedelta(
            seconds=30 if please.opt_args.force else 1800)
        for fn in sorted(os.listdir(os.path.expanduser("~/"))):
            if not fn.startswith("VENV_"):
                continue
            ffn = os.path.expanduser("~/%s" % fn)
            fn_ts = max(
                datetime.fromtimestamp(os.path.getmtime(ffn)),
                datetime.fromtimestamp(os.path.getmtime(ffn))
            )
            if fn_ts < remove_ts:
                sts = please.run_traced("rm -fR " + ffn, rtime=True)
                if sts:
                    break

        cr = connect_db().cursor()
        cr.execute(
            "SELECT datname,"
            "(pg_stat_file('base/'||oid ||'/PG_VERSION')).modification as datmod,"
            "datdba::regrole"
            " FROM pg_database order by datmod"
        )
        rex = re.compile("^(test|template)_[a-z]+")
        date_limit = datetime.strftime(datetime.now() - timedelta(30), "%Y-%m-%d")
        for row in cr.fetchall():
            db_name, db_date, db_user = row[0], row[1], row[2]
            if (
                    datetime.strftime(db_date, "%Y-%m-%d") < date_limit
                    and rex.match(db_name)
            ):
                sts = please.run_traced("dropdb -U%s %s" % (db_user, db_name),
                                        rtime=True)
                if sts:
                    break
        return sts

    def do_defcon(self):
        print("Missed sepcification:\nplease defcon precommit|gitignore")
        return 126

    def _do_defcon(self, tmpl_fn, tgt_fn):
        please = self.please
        branch = target = ""
        sts = 126
        submodules = []
        py23 = 3

        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_repo_ocb():
            is_odoo_pkg = True
            sts, branch = please.get_odoo_branch_from_git()
            if sts == 0:
                py23 = 2 if int(branch.split(".")[0]) <= 10 else 3
            sts = 0
        else:
            is_odoo_pkg = False

        for fn in os.listdir(os.getcwd()):
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
            ffn = os.path.join(os.getcwd(), fn)
            if os.path.isdir(os.path.join(ffn, ".git")):
                submodules.append("/%s" % fn)

        if please.opt_args.debug:
            if os.environ.get("HOME_DEVEL"):
                srcpath = os.path.join(os.environ["HOME_DEVEL"], "pypi")
            elif os.path.isdir("~/odoo/tools"):
                srcpath = os.path.expanduser("~/odoo/devel/pypi")
            else:
                srcpath = os.path.expanduser("~/devel/pypi")
            srcpath = os.path.join(srcpath, "tools", "templates")
        else:
            if os.environ.get("HOME_DEVEL"):
                srcpath = os.path.join(
                    os.path.dirname(os.environ["HOME_DEVEL"]), "tools"
                )
            elif os.path.isdir("~/odoo/tools"):
                srcpath = os.path.expanduser("~/odoo/tools")
            else:
                srcpath = os.path.expanduser("~/odoo/tools")
            srcpath = os.path.join(srcpath, "templates")

        if is_odoo_pkg and py23 == 2 and tmpl_fn == "pre-commit-config2.yaml":
            srcpath = os.path.join(srcpath, "pre-commit-config2.yaml")
        else:
            srcpath = os.path.join(srcpath, tmpl_fn)
        if not os.path.isfile(srcpath):
            print("File %s not found" % srcpath)
            sts = 1
        elif sts == 126:
            sts = 0

        if sts == 0:
            max_ctr = 10
            while not os.path.isdir(".git"):
                max_ctr -= 1
                if not max_ctr:
                    print("Git repository not found!")
                    sts = 1
                    break
                os.chdir(os.path.dirname(os.getcwd()))
        if sts == 0:
            tgtpath = os.path.join(os.getcwd(), tgt_fn)
            with open(srcpath, "r") as fd:
                trig = ""
                for line in fd.read().split("\n"):
                    if "entry: arcangelo" in line:
                        if branch:
                            target += re.sub("entry: arcangelo .*",
                                             "entry: arcangelo -i -b%s\n" % branch,
                                             line)
                        else:
                            target += re.sub("entry: arcangelo .*",
                                             "entry: arcangelo -i -P\n",
                                             line)
                        continue
                    found = line.startswith("!")
                    if trig == "odoo":
                        if branch and line.startswith(" "):
                            found = True
                        else:
                            for x in submodules:
                                if x == line:
                                    found = True
                                    break
                    elif trig == "pypi":
                        if not branch and line.startswith(" "):
                            found = True
                        else:
                            if (
                                ".egg-info/" not in line
                                and os.path.isdir(os.path.join(
                                    *[os.getcwd()] + [x for x in line.split("/") if x]
                                ))
                            ):
                                found = True
                    if not trig or found:
                        target += "%s\n" % line
                    if re.match("^ *# odoo repositories", line):
                        trig = "odoo"
                    elif re.match("^ *# tools building path", line):
                        trig = "pypi"

            if not please.opt_args.dry_run:
                if please.opt_args.verbose:
                    print("File %s updated/created" % tgtpath)
                with open(tgtpath, "w") as fd:
                    fd.write(target)
            elif please.opt_args.verbose:
                print("File %s should be updated/created" % tgtpath)
        return sts

    def do_defcon_precommit(self):
        return self._do_defcon("pre-commit-config.yaml", ".pre-commit-config.yaml")

    def do_defcon_gitignore(self):
        return self._do_defcon("gitignore", ".gitignore")

    def do_docs(self):
        please = self.please
        if (
                please.is_odoo_pkg()
                or please.is_repo_odoo()
                or please.is_repo_ocb()
                or please.is_pypi_pkg()
        ):
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh")
            )
            sts = please.run_traced(cmd, rtime=True)
            if sts == 0:
                please.sh_subcmd = please.pickle_params(cmd_subst="wep", rm_obj=True)
                cmd = please.build_sh_me_cmd()
                please.run_traced(cmd, rtime=True)
            return sts
        return please.do_iter_action("do_docs", act_all_pypi=True, act_tools=True)

    def do_edit(self):
        please = self.please
        if please.is_odoo_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd)
        return 1

    def do_publish(self):
        print("Missed specification:\nplease publish pypi|test_pypi")
        return 126

    def do_publish_pypi(self):
        please = self.please
        if please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd, rtime=True)
        return 126

    def do_replace(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            sts = self.do_docs()
        if sts == 0:
            for root, dirs, files in os.walk(os.getcwd()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + os.path.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        break
        if sts == 0:
            if os.environ.get("HOME_DEVEL"):
                tgtdir = os.path.join(
                    os.path.dirname(os.environ["HOME_DEVEL"]), "tools"
                )
            elif os.path.isdir("~/odoo/tools"):
                tgtdir = os.path.expanduser("~/odoo/tools")
            else:
                tgtdir = os.path.expanduser("~/tools")
            if not os.path.isdir(tgtdir):
                print("Tools directory %s not found!" % tgtdir)
                return 2
            srcdir = os.getcwd()
            pkgname = os.path.basename(srcdir)
            if pkgname != "tools":
                sts = 0
                if not please.opt_args.no_verify:
                    sts = please.run_traced("pre-commit run", rtime=True)
                if sts == 0:
                    sts = please.run_traced(
                        "rsync -a --exclude=.* --exclude=*~ %s/ %s/"
                        % (srcdir, os.path.join(tgtdir, pkgname)),
                        rtime=True,
                    )
                if sts == 0:
                    for item in ("setup.py", "README.rst"):
                        fn = os.path.join(os.path.dirname(srcdir), item)
                        if not os.path.isfile(fn):
                            continue
                        sts = please.run_traced(
                            "cp %s %s" % (fn, os.path.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            else:
                for item in ("egg-info", "docs", "tests", "templates", "license_text"):
                    sts = please.run_traced(
                        "rsync -a --exclude=.* --exclude=*~  %s/ %s/"
                        % (os.path.join(srcdir, item), os.path.join(tgtdir, item)),
                        rtime=True,
                    )
                    if sts:
                        break
                if sts == 0:
                    for item in (
                        "install_tools.sh",
                        "LICENSE",
                        "odoo_default_tnl.xlsx",
                        "README.rst",
                    ):
                        fn = os.path.join(srcdir, item)
                        if not os.path.isfile(fn):
                            continue
                        sts = please.run_traced(
                            "cp %s %s" % (fn, os.path.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            return sts
        return please.do_iter_action("do_replace", act_all_pypi=True, act_tools=False)

    def do_translate(self):
        please = self.please
        if please.is_odoo_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd, rtime=True)
        return 1

    def do_update(self):
        please = self.please
        if please.is_pypi_pkg():
            if os.environ.get("HOME_DEVEL"):
                tgtdir = os.path.join(os.environ["HOME_DEVEL"], "venv")
            else:
                tgtdir = os.path.expanduser("~/devel/venv")
            if not os.path.isdir(tgtdir):
                print("Tools directory %s not found!" % tgtdir)
                return 2
            srcdir = os.getcwd()
            pkgname = os.path.basename(srcdir)
            if pkgname != "tools":
                sts = please.run_traced(
                    "vem %s update %s" % (tgtdir, os.path.dirname(srcdir)), rtime=True
                )
            if sts == 0 and please.opt_args.vme:
                sts = self.do_update_vme()
            if sts == 0 and please.opt_args.odoo_venv:
                sts = self.do_update_venv()
            return sts
        return please.do_iter_action("do_update", act_all_pypi=True, act_tools=False)

    def do_update_venv(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            srcdir = os.getcwd()
            pkgname = os.path.basename(srcdir)
            if pkgname != "tools":
                rex = re.compile(r"[a-z0-9][a-z0-9_.]+$")
                for root, dirs, files in os.walk(os.path.expanduser("~/")):
                    for fn in sorted(dirs):
                        if not rex.match(fn):
                            continue
                        tgtdir = os.path.join(root, fn, "venv_odoo")
                        if not os.path.isdir(tgtdir):
                            continue
                        sts = please.run_traced(
                            "vem %s update %s" % (tgtdir, os.path.dirname(srcdir)),
                            rtime=True,
                        )
                        if sts:
                            break
        return sts

    def do_update_vme(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            srcdir = os.getcwd()
            pkgname = os.path.basename(srcdir)
            if pkgname != "tools":
                vme_dir = os.path.expanduser("~/VME")
                for fn in sorted(os.listdir(vme_dir)):
                    tgtdir = os.path.join(vme_dir, fn)
                    if not os.path.isdir(tgtdir) or not os.path.isdir(
                        os.path.join(tgtdir, "bin")
                    ):
                        continue
                    sts = please.run_traced(
                        "vem %s update %s" % (tgtdir, os.path.dirname(srcdir)),
                        rtime=True,
                    )
                    if sts:
                        break
        return sts

    def do_action(self):
        return 126
