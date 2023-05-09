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
    * create - create some components (currently just apache conf)
    * install - install some components (currently just python3)
    * z0bug - execute lint and tests
    * zerobug - execute lint and tests

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

try:
    from please_z0bug import PleaseZ0bug                                   # noqa: F401
except ImportError:
    from .please_z0bug import PleaseZ0bug                                  # noqa: F401
try:
    from please_apache import PleaseApache                                 # noqa: F401
except ImportError:
    from .please_apache import PleaseApache                                # noqa: F401

__version__ = "2.0.7"

KNOWN_ACTIONS = [
    "help",
    "chkconfig",
    "config",
    "docs",
    "duplicate",
    "edit",
    "export",
    "import",
    "install",
    "lint",
    "list",
    "lsearch",
    "publish",
    "push",
    "pythonhosted",
    "replace",
    "replica",
    "test",
    "translate",
    "version",
    "wep"
]


class Please(object):

    def __init__(self, cli_args=[]):
        self.clsname = self.__class__.__name__
        self.cli_args = []
        self.store_actions_n_aliases()
        actions, param, sub1, self.opt_with_help = self.get_no_switches(
            cli_args=cli_args)
        self.actions = self.get_actions_list(actions=actions)
        if param and param in self.knwon_objs:
            clsname = self.clsname_of_action(param)
            if clsname != "Please" and clsname in globals():
                self.clsname = clsname
        elif sub1 and sub1 in self.knwon_objs:
            clsname = self.clsname_of_action(sub1)
            if clsname != "Please" and clsname in globals():
                self.clsname = clsname
        elif (
            self.actions
            and len(self.actions) == 1
            and self.actions[0] in self.knwon_objs
        ):
            clsname = self.clsname_of_action(self.actions[0])
            if clsname != "Please" and clsname in globals():
                self.clsname = clsname
            if param:
                self.actions, param = [param], self.actions[0]
        self.main_action = None
        for action in self.actions:
            if action not in self.known_actions:
                print("Unknown action %s" % action)
                sys.exit(126)
            if action == "help":
                if param in self.known_actions:
                    self.main_action = param
            else:
                self.main_action = action

        self.opt_args = self.get_parser().parse_args([])
        self.cli_args = cli_args
        self.home_devel = self.opt_args.home_devel or os.environ.get(
            "HOME_DEVEL", os.path.expanduser("~/devel")
        )
        self.odoo_root = os.path.dirname(self.home_devel)
        self.pypi_list = self.get_pypi_list(act_tools=False)
        self.sh_subcmd = self.pickle_params()

    def store_actions_n_aliases(self):
        self.known_actions = KNOWN_ACTIONS
        self.knwon_objs = ["cwd"]
        self.aliases = {}
        for fn in sorted(os.listdir(os.path.dirname(__file__))):
            if not fn.startswith("please_") or not fn.endswith(".py"):
                continue
            action = fn[7: -3]
            cls = self.get_cls_of_action(action)
            clsname = cls.__class__.__name__
            if clsname.startswith("Please"):
                clsname = clsname[6:].lower()
                self.knwon_objs.append(clsname)

            if hasattr(cls, "get_aliases"):
                for alias in getattr(cls, "get_aliases")():
                    # for alias in getattr(cls(self), "get_aliases")():
                    self.aliases[alias] = action
                    if alias not in self.known_actions:
                        self.known_actions.append(alias)
            if hasattr(cls, "get_actions"):
                for action in getattr(cls, "get_actions")():
                    if action not in self.known_actions:
                        self.known_actions.append(action)
            else:
                self.known_actions.append(action)

    def clsname_of_action(self, action=None):
        if action == "help":
            return "Please"
        if action in self.aliases:
            action = self.aliases[action]
        return "".join(["Please", action[0].upper(), action[1:].lower()])

    def get_cls_of_action(self, action=None):
        if not action:
            return self
        clsname = (
            self.clsname
            if self.clsname != "Please" else self.clsname_of_action(action)
        )
        return self.get_cls_from_clsname(clsname)

    def get_cls_from_clsname(self, clsname):
        if clsname not in globals() or clsname == "Please":
            return self
        return globals()[clsname](self)

    def get_fctname_of_cls(self, cls, action, param, sub1):
        def build_fctname_of_cls(cls, params):
            if not params:
                fctname = "do_action"
                if clsname == "Please" or not hasattr(cls, fctname):
                    fctname = "do_external_cmd"
            else:
                parms = []
                rev_parms = []
                for param in params:
                    if param and param != clsname:
                        parms.append(param)
                        rev_parms.insert(0, param)
                fctname = "do_" + "_".join(parms)
                if not hasattr(cls, fctname):
                    fctname = "do_" + "_".join(rev_parms)
                if not hasattr(cls, fctname):
                    return build_fctname_of_cls(cls, params[: -1])
            return fctname

        clsname = cls.__class__.__name__
        if clsname.startswith("Please"):
            clsname = clsname[6:].lower()
        if action == "help":
            return "do_%s" % action
        if sub1:
            return build_fctname_of_cls(cls, [action, param, sub1])
        elif param:
            return build_fctname_of_cls(cls, [action, param])
        return build_fctname_of_cls(cls, [action])

    def get_parser(self, action=None):
        parser = self.common_opts()
        if action:
            cls = self.get_cls_of_action(action)
            if hasattr(cls, "action_opts"):
                parser = getattr(cls, "action_opts")(parser)
            else:
                parser = self.action_opts(parser)
        else:
            parser = self.action_opts(parser)
        return parser

    def merge_action_parser(self, action, cli_args):
        parser = self.get_parser(action)
        self.opt_args = parser.parse_args(cli_args)

    def run_traced(self, cmd):
        if not self.opt_args.dry_run and self.opt_args.verbose:
            print(">", cmd)
        return os.system(cmd)

    def common_opts(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Zeroincombenze® developer shell",
            epilog=(
                "Help available issuing: please help ACTION\n"
                "© 2015-2023 by SHS-AV s.r.l.\n"
                "Author: antoniomaria.vigliotti@gmail.com\n"
                "Full documentation at: https://zeroincombenze-tools.readthedocs.io/\n"
            ),
        )
        parser.add_argument(
            "-B", "--debug", action="count", default=0, help="debug mode"
        )
        parser.add_argument(
            "-b", "--odoo-branch", default="12.0",
            metavar="BRANCH_OR_VERSION",
            help="default Odoo version"
        )
        parser.add_argument(
            "-c", "--odoo-config", metavar="FILE",
            help="Odoo configuration file"
        )

        parser.add_argument("-d", "--database", metavar="NAME",)
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=(
                "force copy (push) | build (publish/test) | set_exec (wep) |"
                " full (status)"
            ),
        )
        parser.add_argument("-H", "--home-devel",  metavar="PATH",
                            help="Home devel directory")
        parser.add_argument("-l", "--log", metavar="FILE", help="log file name")
        parser.add_argument("-n", "--dry-run", action="store_true")
        parser.add_argument("-Q", "--tools-config", metavar="FILE",
                            help="Configuration file")
        parser.add_argument(
            "-q", "--quiet", action="store_false", dest="verbose", help="silent mode"
        )
        parser.add_argument("-v", "--verbose", action="count", default=0)
        parser.add_argument("-V", "--version", action="version", version=__version__)
        parser.add_argument("-y", "--assume-yes", action="store_true")
        parser.add_argument("action", nargs="?")
        parser.add_argument("param", nargs="?")
        parser.add_argument("sub1", nargs="?")
        parser.add_argument("sub2", nargs="?")
        parser.add_argument("sub3", nargs="?")
        return parser

    def action_opts(self, parser):
        parser.add_argument("--from-date diff", help="date to search in log")
        parser.add_argument(
            "-k",
            "--keep",
            action="store_true",
            help=(
                "keep coverage statistics in annotate test/keep original repository |"
                " tests/ in publish"
            ),
        )
        parser.add_argument("-p", "--target-path",  metavar="PATH",
                            help="Local directory")
        return parser

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

    def actions_args(self, action):
        args = []
        for arg in self.cli_args:
            if action and not arg.startswith("-"):
                args.append(action)
                action = None
            else:
                args.append(arg)
        return args

    def get_no_switches(self, cli_args=[]):
        cmd = param = sub1 = ""
        opt_with_help = False
        cli_args = cli_args or self.cli_args
        for arg in cli_args:
            if arg.startswith("-"):
                if arg in ("-h", "--help", "-V", "--version"):
                    opt_with_help = True
            else:
                if not cmd:
                    cmd = arg
                elif not param:
                    param = arg
                else:
                    sub1 = arg
            if (cmd and param and sub1) or (cmd and opt_with_help):
                break
        return cmd, param, sub1, opt_with_help

    def get_home_pypi(self):
        return os.path.join(self.home_devel, "pypi")

    def get_home_pypi_pkg(self, pkgname):
        root = self.get_home_pypi()
        if pkgname == "tools":
            return os.path.join(root, pkgname)
        else:
            return os.path.join(root, pkgname, pkgname)

    def get_home_tools(self):
        return os.path.join(self.odoo_root, "tools")

    def get_home_tools_pkg(self, pkgname):
        root = self.get_home_tools()
        return os.path.join(root, pkgname)

    def is_pypi_pkg(self, path=None):
        path = path or os.getcwd()
        pkgname = os.path.basename(path)
        while pkgname in ("tests",
                          "travis",
                          "_travis",
                          "docs",
                          "examples",
                          "egg-info",
                          "junk"):
            path = os.path.dirname(path)
            pkgname = os.path.basename(path)
        pkgpath = self.get_home_pypi_pkg(pkgname)
        root = pkgpath if pkgname == "tools" else os.path.dirname(pkgpath)
        pkgpath2 = self.get_home_tools_pkg(pkgname)
        return (
            os.path.isdir(pkgpath)
            and path.startswith(root)
            and os.path.isfile(os.path.join(root, "setup.py"))
        ) or (
            os.path.isdir(pkgpath2)
            and path.startswith(pkgpath2)
            and os.path.isfile(os.path.join(pkgpath2, "setup.py"))
        )

    def is_all_pypi(self, path=None):
        path = path or os.getcwd()
        return path == self.get_home_pypi()

    def is_odoo_pkg(self, path=None):
        path = path or os.getcwd()
        files = os.listdir(path)
        filtered = [x for x in files
                    if x in ("__manifest__.py",  "__openerp__.py", "__init__.py")]
        return len(filtered) == 2 and "__init__.py" in filtered

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
            self.get_home_pypi()
            if os.path.isdir(self.get_home_pypi())
            else self.get_home_tools()
        )
        pypi_list = []
        if os.path.isdir(path):
            for fn in os.listdir(path):
                fqn = os.path.join(path, fn)
                if fn == "tools" and not act_tools:
                    continue
                if not os.path.isdir(fqn):
                    continue
                if self.is_pypi_pkg(path=fqn):
                    pypi_list.append(fn)
        return sorted(pypi_list)

    def get_actions_list(self, actions=None):
        actions = actions.split("+") if actions else ""
        return list(itertools.chain.from_iterable([x.split(",") for x in actions]))

    def build_sh_me_cmd(self, params=None):
        cmd = "%s.sh" % os.path.splitext(os.path.abspath(__file__))[0]
        if not os.path.isfile(cmd):
            cmd = os.path.split(cmd)
            cmd = os.path.join(os.path.dirname(cmd[0]), cmd[1])
        if not os.path.isfile(cmd):
            print("Internal package error: file %s not found!" % cmd)
            return ""
        cmd += " " + (params or self.sh_subcmd)
        return cmd

    def do_external_cmd(self):
        cmd = self.build_sh_me_cmd()
        if not cmd:
            return 1
        return self.run_traced(cmd)

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
            return self.run_traced(self.sh_subcmd)
        return 126

    ##########################
    # -----  Commands  ----- #
    ##########################

    def travis_opts(self, parser):
        parser.add_argument(
            "-A", "--trace-after",
            metavar="REGEX",
            help="travis stops after executed yaml statement"
        )
        parser.add_argument(
            "-C", "--no-cache", action="store_true", help="do not use stored PYPI"
        )
        parser.add_argument(
            "-D",
            "--debug-level",
            help="travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)",
        )
        parser.add_argument(
            "-E", "--no-savenv", action="store_true",
            help="do not save virtual environment into ~/VME/... if does not exist"
        )
        parser.add_argument(
            "-e", "--locale", help="use locale"
        )
        parser.add_argument(
            "-f",
            "--full",
            action="store_true",
            help="run final travis with full features",
        )
        parser.add_argument(
            "-L",
            "--lint-level",
            help=("lint_check_level; may be: "
                  "minimal,reduced,average,nearby,oca; def value from .travis.yml"),
        )
        parser.add_argument(
            "-m",
            "--missing",
            action="store_true",
            help="show missing line in report coverage after test",
        )
        parser.add_argument(
            "-S", "--syspkg", metavar="true|false",
            help="use python system packages (def yaml dependents)"
        )
        parser.add_argument(
            "-T", "--trace",
            metavar="REGEX",
            help="trace stops before executing yaml statement"
        )
        parser.add_argument(
            "-X", "--translation",
            metavar="true|false",
            help="enable translation test (def yaml dependents)"
        )
        parser.add_argument(
            "-Y", "--yaml-file",
            metavar="PATH",
            help="file yaml to process (def .travis.yml)"
        )
        parser.add_argument(
            "-Z", "--zero", action="store_true",
            help="use local zeroincombenze tools"
        )
        return parser

    def do_install_python3(self):
        """
NAME
    please install python3 - install a specific python version

SYNOPSIS
    please install python3 PYTHON3_VERSION

DESCRIPTION
    This command installs a specific python version on system from source.
    To install python you must be the root user o you must have the admin
    privileges.

OPTIONS
    -n      Do nothing (dry-run)

EXAMPLES
    please python3 3.9

BUGS
    No known bugs."""
        cmd = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "install_python_3_from_source.sh",
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
                cmd, verbose=self.opt_args.verbose, dry_run=self.opt_args.dry_run
            )
            return 0
        return self.run_traced(cmd)

    def do_help(self):
        cls = self.get_cls_from_clsname(self.clsname)
        _, param, sub1, _ = self.get_no_switches(cli_args=self.cli_args)
        action = self.get_fctname_of_cls(cls, param, sub1, None)
        if hasattr(cls, action):
            print(getattr(cls, action).__doc__)
            return 0
        print(__doc__)
        return 0


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    please = Please(cli_args)
    _, param, sub1, _ = please.get_no_switches(cli_args=please.cli_args)
    done = False
    if not please.opt_with_help:
        for action in please.actions:
            cls = please.get_cls_of_action(action)
            cmd = please.get_fctname_of_cls(cls, action, param, sub1)
            if hasattr(cls, cmd):
                please.merge_action_parser(action, please.actions_args(action))
                please.sh_subcmd = please.pickle_params(cmd_subst=action)
                sts = getattr(cls, cmd)()
            elif cmd != "do_help" and hasattr(cls, "do_action"):
                please.merge_action_parser(action, please.actions_args(action))
                please.sh_subcmd = please.pickle_params(cmd_subst=action)
                sts = getattr(cls, "do_action")()
            elif hasattr(please, cmd):
                sts = getattr(please, cmd)()
            else:
                sts = 126
            if sts:
                return sts
            done = True
    if not done:
        if cli_args and please.opt_with_help:
            please.get_parser(please.main_action).parse_args(cli_args)
        else:
            please.get_parser().print_help()
    return 0


if __name__ == "__main__":
    exit(main())
