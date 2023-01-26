#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NAME
    please - developers shell

SYNOPSIS
    please [options] action

DESCRIPTION
    please is an interactive developers shell aim to help development and testing
    software.

    Action is one of:

    * help - show this help or specific action help
    * install - install some components (currently just python3)
    * z0bug - execute lint and tests


OPTIONS
    -n      Do nothing (dry-run)

EXAMPLES
    please help z0bug

BUGS
    No known bugs.

AUTHOR
    Antonio Maria Vigliotti (antoniomaria.vigliotti@gmail.com)
"""
import os
import sys
import argparse
import itertools
from z0lib import z0lib


__version__ = "2.0.5"


class Please(object):

    def __init__(self, opt_args, cli_args, home_devel=None, odoo_root=None):
        self.opt_args = opt_args
        self.cli_args = cli_args
        params = self.pickle_params()
        self.params = params
        home_devel = home_devel or opt_args.home_devel or os.environ.get(
            "HOME_DEVEL", os.path.expanduser("~/devel"))
        self.home_devel = home_devel
        odoo_root = odoo_root or os.path.dirname(home_devel)
        self.odoo_root = odoo_root
        self.pypi_list = self.get_pypi_list(act_tools=False)

    def pickle_params(self, cmd_subst=None):
        params = ""
        for arg in self.cli_args:
            if cmd_subst and not arg.startswith("-"):
                arg = cmd_subst
                cmd_subst = None
            if "<" in arg or ">" in arg:
                arg = "'%s'" % arg.replace("'", r"\'")
            elif " " in arg:
                if '"' in arg:
                    arg = '"%s"' % arg.replace('"', r"\"")
                else:
                    arg = '"%s"' % arg
            elif '"' in arg:
                arg = '"%s"' % arg.replace('"', r"\"")
            elif "'" in arg:
                arg = '"%s"' % arg
            else:
                arg = "%s" % arg
            params += arg + " "
        return params.strip()

    def get_home_pypi(self):
        return os.path.join(self.home_devel, "pypi")

    def get_home_tools(self):
        return os.path.join(self.home_devel, "tools")

    def get_home_pypi_pkg(self, pkgname):
        root = self.get_home_pypi() if self.opt_args.debug else self.get_home_tools()
        if pkgname == "tools":
            return os.path.join(root, pkgname)
        elif self.opt_args.debug:
            return os.path.join(root, pkgname, pkgname)
        else:
            return os.path.join(root, pkgname)

    def is_pypi_pkg(self, path=None):
        path = path or os.getcwd()
        pkgname = os.path.basename(path)
        pkgpath = self.get_home_pypi_pkg(pkgname)
        root = pkgpath if pkgname != "tools" else os.path.dirname(pkgpath)
        return (
            path.startswith(root)
            and os.path.isfile(os.path.join(root, "setup.py"))
            and os.path.isdir(pkgpath)
        )

    def is_all_pypi(self, path=None):
        path = path or os.getcwd()
        return path == self.get_home_pypi()

    def is_odoo_pkg(self, path=None):
        path = path or os.getcwd()
        return (
            os.path.isfile(os.path.join(path, "__manifest__.py"))
            or os.path.isfile(os.path.join(path, "__openerp__.py"))
        ) and os.path.isfile(os.path.join(path, "__init__.py"))

    def is_repo_ocb(self, path=None):
        path = path or os.getcwd()
        if (
            os.path.isdir(os.path.join(path, ".git"))
            and (
                os.path.isfile(os.path.join(path, "odoo-bin"))
                or os.path.isfile(os.path.join(path, "openerp-server"))
            )
            and os.path.isfile(os.path.join(path, "__init__.py"))
            and os.path.isdir(os.path.join(path, "addons"))
            and (
                os.path.isdir(os.path.join(path, "odoo"))
                or os.path.isdir(os.path.join(path, "openerp"))
            )
        ):
            return True
        if os.path.basename(path) in ("addons", "odoo", "openerp"):
            return self.is_repo_ocb(path=os.path.dirname(path))
        return False

    def is_repo_odoo(self, path=None):
        path = path or os.getcwd()
        if not os.path.isdir(os.path.join(path, ".git")):
            return False
        for fn in os.listdir(path):
            if self.is_odoo_pkg(path=os.path.join(path, fn)):
                return True
        return self.is_repo_ocb(os.path.dirname(path))

    def get_pypi_list(self, path=None, act_tools=True):
        path = path or (
            self.get_home_pypi() if self.opt_args.debug else self.get_home_tools())
        pypi_list = []
        if os.path.isdir(path):
            for fn in os.listdir(path):
                if fn == "tools" and not act_tools:
                    continue
                if self.is_pypi_pkg(path=os.path.join(path, fn)):
                    pypi_list.append(fn)
        return sorted(pypi_list)

    def get_1st_no_switch(self):
        cmd = param = ""
        for arg in self.cli_args:
            if not arg.startswith("-"):
                if not cmd:
                    cmd = arg
                else:
                    param = arg
                    break
        return cmd, param

    def get_actions_list(self):
        actions = self.opt_args.action.split("+") if self.opt_args.action else ""
        return list(itertools.chain.from_iterable([x.split(",") for x in actions]))

    def build_cmd(self, params=None):
        params = params or self.params
        cmd = "%s.sh" % os.path.splitext(os.path.abspath(__file__))[0]
        if not os.path.isfile(cmd):
            cmd = os.path.split(cmd)
            cmd = os.path.join(os.path.dirname(cmd[0]), cmd[1])
        if not os.path.isfile(cmd):
            print("Internal package error: file %s not found!" % cmd)
            return ""
        cmd += " " + params
        return cmd

    def do_external_cmd(self):
        cmd = self.build_cmd()
        if not cmd:
            return 1
        return os.system(cmd)

    def do_action_pypipkg(self, action, pkg, path=None):
        path = path or os.path.join(self.home_devel, "pypi", pkg, pkg)
        os.chdir(path)
        return getattr(self, action)

    def do_iter_action(self, action, path=None, act_all_pypi=None, act_tools=None):
        """Iter multiple command on sub projects.

        Args:
            action (str): action name to execute
            act_all_pypi (bool): action on all pypi packages
            act_tools (bool): package tools included in act_all_pypi
        """
        path = path or os.getcwd()
        if act_all_pypi and self.is_all_pypi(path=path):
            sts = 0
            for fn in self.pypi_list:
                sts = self.do_action_pypipkg(action, fn)
                if sts:
                    break
                os.chdir(path)
            if sts:
                return sts
            if act_tools:
                return self.do_action_pypipkg(action, "tools")
            return sts
        elif (
            self.is_pypi_pkg(path=path)
            or self.is_odoo_pkg(path=path)
            or self.is_repo_odoo(path=path)
            or self.is_repo_ocb(path=path)
        ):
            return os.system(self.params)
        return 126

    def do_travis(self):
        if self.is_odoo_pkg():
            params = self.pickle_params(cmd_subst="lint")
            cmd = self.build_cmd(params=params)
            sts = os.system(cmd)
            if sts == 0:
                params = self.pickle_params(cmd_subst="test")
                cmd = self.build_cmd(params=params)
                sts = os.system(cmd)
            return sts
        return self.do_iter_action("do_travis", act_all_pypi=True, act_tools=False)

    def do_z0bug(self):
        """"
NAME
    please z0bug - execute lint and tests

SYNOPSIS
    please [options] z0bug

DESCRIPTION
    This command executes the lint and the regression tests.
    In previous version of please this command were called travis;
    travis is now deprecated

OPTIONS
    -n      Do nothing (dry-run)

EXAMPLES
    please z0bug

BUGS
    No known bugs.

AUTHOR
    Antonio Maria Vigliotti (antoniomaria.vigliotti@gmail.com)
"""
        return self.do_travis()

    def do_install_python3(self):
        """"
NAME
    please install python3 - install a specific python version

SYNOPSIS
    please install python3 PYTHON3_VERSION

DESCRIPTION
    This command installs a specific python version on system from source.
    To install python you must be the root usre o you must have the admin privileges.

OPTIONS
    -n      Do nothing (dry-run)

EXAMPLES
    please python3 3.9

BUGS
    No known bugs.

AUTHOR
    Antonio Maria Vigliotti (antoniomaria.vigliotti@gmail.com)
"""
        cmd = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "install_python_3_from_source.sh"
        )
        if not os.path.isfile(cmd):
            print("Internal package error: file %s not found!" % cmd)
            return 127
        if not self.opt_args.sub2:
            print("You must specify the python version: 3.6 or 3.7 or 3.8 or 3.9")
            return 1
        cmd += " " + self.opt_args.sub2
        if self.opt_args.dry_run:
            z0lib.run_traced(
                cmd, verbose=self.opt_args.verbose, dry_run=self.opt_args.dry_run)
            return 0
        return os.system(cmd)

    def do_help_z0bug(self):
        print(self.do_travis.__doc__)
        return 0

    def do_help(self):
        print(__doc__)
        return 0


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Zeroincombenze® developer shell",
        epilog=(
            "© 2015-2023 by SHS-AV s.r.l.\n"
            "Author: antoniomaria.vigliotti@gmail.com\n"
            "Full documentation at: https://zeroincombenze-tools.readthedocs.io/\n"
        ),
    )
    parser.add_argument(
        "-A", "--trace-after", help="travis stops after executed yaml statement"
    )
    parser.add_argument("-B", "--debug", action="count", default=0, help="debug mode")
    parser.add_argument(
        "-b", "--odoo-branch", default="12.0", help="default Odoo version"
    )
    parser.add_argument(
        "-C", "--no-cache", action="store_true", help="do not use stored PYPI"
    )
    # parser.add_argument("-C", "--config",
    #                     help="Configuration file")
    parser.add_argument("-c", "--odoo-config", help="Odoo configuration file")
    parser.add_argument(
        "-D",
        "--debug-level",
        help="travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)",
    )
    parser.add_argument("--from-date diff", help="date to search in log")
    parser.add_argument("-d", "--database")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=(
            "force copy (push) | build (publish/test) | set_exec (wep) |"
            " full (status)"
        ),
    )
    parser.add_argument(
        "-k",
        "--keep",
        action="store_true",
        help=(
            "keep coverage statistics in annotate test/keep original repository |"
            " tests/ in publish"
        ),
    )
    parser.add_argument("-H", "--home-devel", help="Home devel directory")
    parser.add_argument("-L", "--log", help="log file name")
    parser.add_argument(
        "-m",
        "--missing",
        action="store_true",
        help="show missing line in report coverage after test",
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-p", "--target-path", help="Local directory")
    parser.add_argument(
        "-q", "--quiet", action="store_false", dest="verbose", help="silent mode"
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-y", "--assume-yes", action="store_true")
    parser.add_argument("action", nargs="?")
    parser.add_argument("sub1", nargs="?")
    parser.add_argument("sub2", nargs="?")
    parser.add_argument("sub3", nargs="?")
    parser.add_argument("sub4", nargs="?")
    opt_args = parser.parse_args(cli_args)

    please = Please(opt_args, cli_args)
    actions, param = please.get_1st_no_switch()
    actions = please.get_actions_list()

    done = False
    for action in actions:
        cmd2 = "do_%s_%s" % (action, param)
        cmd = "do_%s" % action
        xcmd = "do_external_cmd"
        if hasattr(please, cmd2):
            sts = getattr(please, cmd2)()
        elif hasattr(please, cmd):
            sts = getattr(please, cmd)()
        else:
            sts = getattr(please, xcmd)()
        if sts:
            return sts
        done = True
    if not done:
        parser.print_help()
    return 0


if __name__ == "__main__":
    exit(main())
