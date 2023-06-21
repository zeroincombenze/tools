#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import re
from z0lib import z0lib

__version__ = "2.0.8"


class PleaseCwd(object):
    """NAME
        Various actions on current working directory.

    SYNOPSIS
        please [action] [cwd] [options]

        * clean: clean temporary file in current working directory and sub directories
        * def_precommit: set default .pre-commit-config.yaml
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
            self.please.add_argument(parser, "-q")
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "--no-verify", action="store_true", help="Disable pre-commit on replace"
        )
        parser.add_argument(
            "--vme", action="store_true", help="Update $HOME/VME virtual environmens"
        )
        parser.add_argument("args", nargs="*")
        return parser

    def do_clean(self):
        please = self.please
        is_odoo = please.is_odoo_pkg()
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            sts = 0
            for root, dirs, files in os.walk(os.getcwd()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + os.path.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        break
            if is_odoo and os.path.isdir(os.path.join("logs", "logs")):
                last = " "
                for root, dirs, files in os.walk(os.getcwd()):
                    for fn in files:
                        if re.match(r".*_[0-9]{8}.txt$", fn) and fn[:12] > last:
                            last = fn[12:]
                for root, dirs, files in os.walk(os.getcwd()):
                    for fn in files:
                        if re.match(r".*_[0-9]{8}.txt$", fn) and fn[:12] != last:
                            cmd = "rm " + os.unlink(os.path.join(root, fn))
                            sts = please.run_traced(cmd)
                            if sts:
                                break
            return sts
        return please.do_iter_action("do_clean", act_all_pypi=True, act_tools=True)

    def do_def_precommit(self):
        please = self.please
        fn = "pre-commit-config.yaml"
        sts = 126
        if please.is_odoo_pkg():
            branch = ""
            sts, stdout, stderr = z0lib.run_traced(
                "git branch", verbose=False, dry_run=False
            )
            if sts == 0 and stdout:
                sts = 1
                for ln in stdout.split("\n"):
                    if ln.startswith("*"):
                        branch = ln[2:]
                        sts = 0
                        break
            if sts == 0:
                x = re.match(r"[0-9]+\.[0-9]+", branch)
                if not x:
                    print("Unrecognize git branch")
                    sts = 1
            if sts == 0:
                branch = branch[x.start() : x.end()]
                pyver = 2 if int(branch.split(".")[0]) <= 10 else 3
                if os.environ.get("HOME_DEVEL"):
                    srcpath = os.path.join(os.environ["HOME_DEVEL"], "pypi")
                elif os.path.isdir("~/odoo/tools"):
                    srcpath = os.path.expanduser("~/odoo/devel/pypi")
                else:
                    srcpath = os.path.expanduser("~/devel/pypi")
                srcpath = os.path.join(srcpath, "tools", "templates")
                if pyver == 2:
                    srcpath = os.path.join(srcpath, "pre-commit-config2.yaml")
                else:
                    srcpath = os.path.join(srcpath, fn)
                if not os.path.isfile(srcpath):
                    print("File %s not found" % srcpath)
                    sts = 1
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
                tgtpath = os.path.join(os.getcwd(), "." + fn)
                with open(srcpath, "r") as fd:
                    content = fd.read()
                content = content.replace(
                    "entry: arcangelo -i -b0.0", "entry: arcangelo -i -b%s" % branch
                )
                if not please.opt_args.dry_run:
                    with open(tgtpath, "w") as fd:
                        fd.write(content)
        return sts

    def do_docs(self):
        please = self.please
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd, rtime=True)
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

    def do_replace(self):
        please = self.please
        if please.is_pypi_pkg():
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
            return sts
        return please.do_iter_action("do_update", act_all_pypi=True, act_tools=False)

    def do_update_vme(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            srcdir = os.getcwd()
            pkgname = os.path.basename(srcdir)
            if pkgname != "tools":
                vme_dir = os.path.expanduser("~/VME")
                for fn in os.listdir(vme_dir):
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

    def do_wep_db(self):
        please = self.please
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "travis.sh")
            )
            return please.run_traced(cmd, rtime=True)
        return 126

    def do_action(self):
        return 126
