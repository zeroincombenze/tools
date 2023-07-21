#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NAME
    please - developers shell

SYNOPSIS
    please [options] action [obj]

DESCRIPTION
    please is an interactive developers shell aims to help development and testing
    software.

    The parameter action is one of: %(actions)s
    The optional obj may be on of %(objs)s

OPTIONS
  %(options)s

EXAMPLES
    please help z0bug

BUGS
    No known bugs.

SEE ALSO
    Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>
"""
import os
import sys
import argparse
import re

# import re
import itertools

from z0lib import z0lib

try:
    from please_z0bug import PleaseZ0bug  # noqa: F401
except ImportError:
    from .please_z0bug import PleaseZ0bug  # noqa: F401
try:
    from please_apache import PleaseApache  # noqa: F401
except ImportError:
    from .please_apache import PleaseApache  # noqa: F401
try:
    from please_cwd import PleaseCwd  # noqa: F401
except ImportError:
    from .please_cwd import PleaseCwd  # noqa: F401
try:
    from please_python import PleasePython  # noqa: F401
except ImportError:
    from .please_python import PleasePython  # noqa: F401

__version__ = "2.0.11"

KNOWN_ACTIONS = [
    "help",
    "chkconfig",
    "config",
    "duplicate",
    "export",
    "import",
    "list",
    "lsearch",
    "push",
    "pythonhosted",
    "replica",
    "version",
]


class Please(object):
    def __init__(self, cli_args=[]):
        self.clsname = self.__class__.__name__
        self.cls = self
        self.cli_args = []
        self.store_actions_n_aliases()
        self.parse_top_cli_args(cli_args=cli_args)
        if self.objname:
            clsname = self.clsname_of_param(self.objname)
            if clsname != "Please" and clsname in globals():
                self.clsname = clsname
            self.cls = self.get_cls_of_param(self.objname)

        if not self.actions and self.objname:
            if hasattr(self.cls, "get_default_action"):
                self.actions = [getattr(self.cls, "get_default_action")()]

        self.main_action = None
        if not self.magic.startswith("-"):
            if not self.actions and not self.magic:
                print("No action declared for %s" % self.objname)
                sys.exit(126)
            for action in self.actions or [self.magic]:
                if action not in self.known_actions:
                    print("Unknown action %s" % action)
                    sys.exit(126)
                if action != "help" and not self.objname:
                    print("Missed object for action %s" % "+".join(self.actions))
                    if self.main_action:
                        print(
                            "Please specify one of %s"
                            % self.default_obj[self.main_action]
                        )
                    sys.exit(126)
                if not self.main_action:
                    self.main_action = action
                    break
            for action in self.actions:
                if action != "help" and self.objname not in self.default_obj[action]:
                    print("Invalid action %s for %s" % (action, self.objname))
                    sys.exit(126)
            self.opt_args = self.get_parser().parse_args(self.cli_args)
            # TODO: workaround due to sub-commands?
            if self.opt_args.verbose > 1:
                self.opt_args.verbose -= 1
        else:
            self.opt_args = self.get_parser().parse_args(
                [x for x in self.cli_args if x != self.magic]
            )
        self.home_devel = self.opt_args.home_devel or os.environ.get(
            "HOME_DEVEL", os.path.expanduser("~/devel")
        )
        self.odoo_root = os.path.dirname(self.home_devel)
        self.pypi_list = self.get_pypi_list(act_tools=False)
        self.sh_subcmd = self.pickle_params()

    def get_actfunctions_of_cls(self, cls, ignore_def=False, ret_action=False):
        excl = ["do_external_cmd", "do_action_pypipkg", "do_iter_action"]
        if ignore_def:
            excl.append("do_action")
        if ret_action:
            excl.append("do_help")
        if sys.version_info[0] == 2:
            functon_list = [
                x
                for x in dir(cls)
                if x.startswith("do_") and x not in excl and callable(getattr(cls, x))
            ]
        else:
            functon_list = [
                x
                for x in cls.__dir__()
                if x.startswith("do_") and x not in excl and callable(getattr(cls, x))
            ]
        if ret_action:
            return [x[3:] for x in functon_list]
        return functon_list

    def store_actions_n_aliases(self):
        def store_defult_obj(action, clsname):
            if action not in self.known_actions:
                self.known_actions.append(action)
            if action not in self.default_obj:
                self.default_obj[action] = []
            if clsname not in self.default_obj[action]:
                self.default_obj[action].append(clsname)

        self.known_actions = KNOWN_ACTIONS
        self.known_objs = []
        self.default_obj = {}
        self.aliases = {}
        for fn in sorted(os.listdir(os.path.dirname(__file__))):
            if not fn.startswith("please_") or not fn.endswith(".py"):
                continue
            # module_name = fn[: -3]
            # clsname = "".join([x[0].upper() + x[1:].lower()
            #                    for x in module_name.split("_")])
            # try:
            #     cls = getattr(__import__(module_name, fromlist=[clsname]), clsname)
            # except ImportError:
            #     print("Internal error: file %s is not valid!" % fn)
            #     continue
            param = fn[7:-3]
            cls = self.get_cls_of_param(param)
            clsname = cls.__class__.__name__
            if clsname.startswith("Please"):
                clsname = clsname[6:].lower()
                if param != clsname:
                    print("Invalid configuration %s" % fn)
                    continue

            self.known_objs.append(param)
            if hasattr(cls, "get_aliases"):
                for alias in getattr(cls, "get_aliases")():
                    self.aliases[alias] = clsname
                    if alias not in self.known_objs:
                        self.known_objs.append(alias)
            action_list = self.get_actfunctions_of_cls(cls, ret_action=True)
            for action in action_list:
                store_defult_obj(action, clsname)
            if hasattr(cls, "get_actions"):
                for action in getattr(cls, "get_actions")():
                    store_defult_obj(action, clsname)

    def clsname_of_param(self, param=None):
        if param == "help":
            return "Please"
        if param in self.aliases:
            param = self.aliases[param]
        return "".join(["Please", param.capitalize()])

    def get_cls_of_param(self, param=None):
        if not param:
            return self
        return self.get_cls_from_clsname(self.clsname_of_param(param))

    def get_cls_from_clsname(self, clsname):
        if clsname not in globals() or clsname == "Please":
            return self
        return globals()[clsname](self)

    def build_function_name_of_cls(self, action):
        def build_valid_name(cls, params):
            if not params:
                fctname = "do_action"
                if cls == "Please" or not hasattr(cls, fctname):
                    fctname = "do_external_cmd"
            else:
                parms = []
                rev_parms = []
                for param in params:
                    parms.append(param)
                    rev_parms.insert(0, param)
                fctname = "do_" + "_".join(parms)
                if not hasattr(cls, fctname):
                    fctname = "do_" + "_".join(rev_parms)
                if not hasattr(cls, fctname):
                    return build_valid_name(cls, params[:-1])
            return fctname

        if action == "help":
            return "do_%s" % action
        if self.sub1:
            return build_valid_name(self.cls, [action, self.sub1])
        return build_valid_name(self.cls, [action])

    def get_parser(self, param=None):
        parser = self.base_opts()
        param = param or self.objname
        if param and hasattr(self.cls, "action_opts"):
            sub_parser = parser.add_subparsers()
            self.cls.action_opts(sub_parser.add_parser(param))
        return parser

    def run_traced(self, cmd, disable_output=False, rtime=False):
        if rtime:
            if self.opt_args.dry_run:
                if self.opt_args.verbose:
                    print("> " + cmd)
                return 0
            if self.opt_args.verbose:
                print("$ " + cmd)
            return os.system(cmd)
        sts, stdout, stderr = z0lib.run_traced(
            cmd, verbose=self.opt_args.verbose, dry_run=self.opt_args.dry_run
        )
        if not disable_output:
            print(stdout + stderr)
        return sts

    def add_argument(self, parser, arg):
        if arg in ("-B", "--debug"):
            parser.add_argument(
                "-B", "--debug", action="count", default=0, help="debug mode"
            )
        elif arg in ("-b", "--odoo-branch", "--branch"):
            parser.add_argument(
                "-b",
                arg if arg != "-b" else "--odoo-branch",
                metavar="BRANCH",
                help="default Odoo version",
            )
        elif arg in ("-c", "--odoo-config"):
            parser.add_argument(
                "-c", "--odoo-config", metavar="FILE", help="Odoo configuration file"
            )
        elif arg in ("-d", "--database"):
            parser.add_argument(
                "-d", "--database", metavar="NAME", help="Database to manage"
            )
        elif arg in ("-f", "--force"):
            parser.add_argument(
                "-f",
                "--force",
                action="store_true",
                help=(
                    "force copy (push) | build (publish/test) | set_exec (wep) |"
                    " full (status)"
                ),
            )
        elif arg in ("-j", "--python"):
            parser.add_argument(
                "-j",
                "--python",
                metavar="PYVER",
                help="Run test with specific python version",
            )
        elif arg in ("-l", "--log"):
            parser.add_argument("-l", "--log", metavar="FILE", help="log file name")
        elif arg in ("-n", "--dry-run"):
            parser.add_argument(
                "-n",
                "--dry-run",
                help="do nothing (dry-run)",
                action="store_true",
            )
        elif arg in ("-q", "--quite"):
            parser.add_argument(
                "-q",
                "--quiet",
                action="store_false",
                dest="verbose",
                help="silent mode",
            )
        elif arg in ("-v", "--verbose"):
            parser.add_argument(
                "-v", "--verbose", help="verbose mode", action="count", default=0
            )
        elif arg in ("-y", "--assume-yes"):
            parser.add_argument("-y", "--assume-yes", action="store_true")
        else:
            raise NotImplementedError

    def base_opts(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=(
                "Zeroincombenze® developer shell.\n"
                # "action is one of: " + ", ".join(self.actions) + "\n"
                "obj after action may be on of "
                + ", ".join(self.known_objs)
                + "\n"
            ),
            epilog=(
                "Help available issuing: please help ACTION\n"
                "© 2015-2023 by SHS-AV s.r.l.\n"
                "Author: antoniomaria.vigliotti@gmail.com\n"
                "Full documentation at: https://zeroincombenze-tools.readthedocs.io/\n"
            ),
        )
        parser.add_argument(
            "-H", "--home-devel", metavar="PATH", help="Home devel directory"
        )
        self.add_argument(parser, "-n")
        parser.add_argument(
            "-Q", "--tools-config", metavar="FILE", help="Configuration file"
        )
        self.add_argument(parser, "-q")
        self.add_argument(parser, "-v")
        parser.add_argument("-V", "--version", action="version", version=__version__)
        parser.add_argument("action", nargs="?")
        return parser

    def pickle_params(self, cmd_subst=None, rm_obj=None, slist=[]):
        """Command line has the follow format:  action object [switches] [sub-action]
        This function returns a string with the command line list with single value
        enclosed by quote if needed (i.e ['a>b'] -> ['"a>b"'] and specific adjustment:
        * action can be replaced by cmd_subst parameter
        * object can be removed by rm_obj flag
        * every switch or sub-action can be replaced by another value from slist:
            - ['a', 'b']:  action obj a -> action obj b
            - ['a', '']:  action obj a -> action obj
            - ['-a', '-b']: action obj -a -> action obj -b
            - ['-a', '-b']: action obj -ax -> action obj -bx
            - ['-a', '']: action obj -a -> action obj
            - ['-a', '']: action obj -ax -> action obj
            - ['--a', '--b']: action obj --a -> action obj --b
            - ['--a', '']: action obj --a -> action obj
            - ['--a=', '--b']: action obj --a=x -> action obj --b=x
            - ['--a=', '']: action obj --a=x -> action obj
            - ['--a=x', '--b']: action obj --a=x -> action obj --b
            - ['--a=x', '--b=y']: action obj --a=x -> action obj --b=y
            - ['--a=x', '']: action obj --a=x -> action obj
            - ['--a=x', '']: action obj --a=x -> action obj
        Returned value can be applied to python call()
        """
        params = ""
        ignore_arg = False
        for arg in self.cli_args:
            if ignore_arg:
                ignore_arg = False
                continue
            if cmd_subst and not arg.startswith("-"):
                arg = cmd_subst
                cmd_subst = None
            else:
                for (k, v) in slist:
                    if arg == k:
                        arg = v
                    elif arg.startswith("--") and k.startswith("--"):
                        if arg.split("=", 1)[0] == k:
                            arg = v + "=" + arg.split("=", 1)[1] if v else None
                    elif (
                            arg.startswith("-") and not arg.startswith("--")
                            and k.startswith("-") and not k.startswith("--")
                    ):
                        if k[1] in arg and "*" in k:
                            if arg.endswith(k[1]):
                                ignore_arg = True
                            arg = arg[:arg.index(k[1])]
                        elif k[1] in arg:
                            arg = arg.replace(k[1], v)
            if arg is None or arg == self.objname and rm_obj:
                continue
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
            params += arg + " "
        return params.strip()

    def parse_top_cli_args(self, cli_args=[]):
        self.actions = self.objname = self.sub1 = self.magic = ""
        cli_args = cli_args
        for arg in cli_args:
            if arg.startswith("-"):
                if arg in ("-h", "--help", "-V", "--version"):
                    self.magic = arg
            else:
                arg = arg.replace("-", "_")
                arg0 = self.aliases.get(arg, arg)
                if arg == "help":
                    self.magic = self.magic or "help"
                elif not self.actions and arg0 not in self.known_objs:
                    self.actions = arg
                elif not self.objname and arg0 in self.known_objs:
                    self.objname = arg0
                elif not self.sub1:
                    self.sub1 = arg
                else:
                    break
            if (self.actions and self.objname and self.sub1) or (
                self.actions and self.magic.startswith("-")
            ):
                break
        self.actions = self.get_actions_list(self.actions)
        if (
            self.actions
            and not self.objname
            # and len(self.default_obj.get(self.actions, [])) == 1
        ):
            objs = list(itertools.chain.from_iterable(
                [self.default_obj[x] for x in self.default_obj if x in self.actions]))
            if len(objs) == 1:
                self.objname = objs[0]
        if not self.objname and self.sub1 and self.sub1 in self.known_objs:
            self.objname = self.sub1
            self.sub1 = ""
        if not self.magic and not self.actions and not self.objname:
            self.actions = ["help"]
        if self.magic.startswith("-"):
            self.cli_args = cli_args
        else:
            args = []
            head = True
            while len(cli_args):
                arg = cli_args.pop(0)
                if arg.startswith("-"):
                    args.append(arg)
                elif head:
                    # action is discarded!
                    args.append("+".join(self.actions) or self.magic)
                    if self.objname:
                        args.append(self.objname)
                    head = False
                elif arg != self.objname:
                    args.append(arg)
            self.cli_args = args

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
        if pkgname == "tools":
            return root
        return os.path.join(root, pkgname)

    def is_pypi_pkg(self, path=None):
        path = path or os.getcwd()
        pkgname = os.path.basename(path)
        while pkgname in (
            "tests",
            "travis",
            "_travis",
            "docs",
            "examples",
            "egg-info",
            "junk",
            "scripts",
        ):
            path = os.path.dirname(path)
            pkgname = os.path.basename(path)
        pkgpath = self.get_home_pypi_pkg(pkgname)
        root = pkgpath if pkgname == "tools" else os.path.dirname(pkgpath)
        pkgpath2 = self.get_home_tools_pkg(pkgname)
        return (
            os.path.isdir(pkgpath)
            and path.startswith(root)
            and os.path.isfile(os.path.join(root, "setup.py"))
            and (
                os.path.isfile(os.path.join(pkgpath, "__init__.py"))
                or pkgname == "tools"
            )
        ) or (
            os.path.isdir(pkgpath2)
            and path.startswith(pkgpath2)
            and pkgname == "tools"
            or (
                os.path.isfile(os.path.join(pkgpath2, "setup.py"))
                and os.path.isfile(os.path.join(pkgpath2, "__init__.py"))
            )
        )

    def is_all_pypi(self, path=None):
        path = path or os.getcwd()
        return path == self.get_home_pypi()

    def is_odoo_pkg(self, path=None):
        path = path or os.getcwd()
        files = os.listdir(path)
        filtered = [
            x
            for x in files
            if x in ("__manifest__.py", "__openerp__.py", "__init__.py")
        ]
        return len(filtered) == 2 and "__init__.py" in filtered

    def is_repo_ocb(self, path=None):
        path = path or os.getcwd()
        if (
            os.path.isdir(os.path.join(path, ".git"))
            and (
                os.path.isfile(os.path.join(path, "odoo-bin"))
                or os.path.isfile(os.path.join(path, "openerp-server"))
            )
            and os.path.isdir(os.path.join(path, "addons"))
            and (
                os.path.isdir(os.path.join(path, "odoo"))
                and os.path.isfile(os.path.join(path, "odoo", "__init__.py")))
                or (os.path.isdir(os.path.join(path, "openerp"))
                    and os.path.isfile(os.path.join(path, "odoo", "__init__.py")))
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
            subpath = os.path.join(path, fn)
            if os.path.isdir(subpath) and self.is_odoo_pkg(path=subpath):
                return True
        return self.is_repo_ocb(os.path.dirname(path))

    def get_odoo_branch_from_git(self, raise_if_not_found=True):
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
                if raise_if_not_found:
                    print("Unrecognized git branch")
                sts = 1
        if sts == 0:
            branch = branch[x.start(): x.end()]
        return sts, branch

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

    def build_sh_me_cmd(self, cmd=None, params=None):
        if not cmd:
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
        path = (
            path
            or os.path.join(self.home_devel, "pypi", pkg, pkg)
            if pkg != "tools" else os.path.join(self.home_devel, "pypi", pkg)
        )
        if self.opt_args.verbose:
            print("$ cd " + path)
        os.chdir(path)
        return getattr(self.cls, action)()

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
                if fn != "tools":
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

    def do_help(self):
        actions = set()
        if not self.objname:
            for cls in [self.get_cls_of_param(x) for x in self.known_objs]:
                actions |= set(
                    [
                        x.split("_")[0]
                        for x in self.get_actfunctions_of_cls(
                            cls, ignore_def=True, ret_action=True
                        )
                    ]
                )
            cls_doc = ""
            parser = self.get_parser()
        else:
            actions |= set(
                [
                    x.split("_")[0]
                    for x in self.get_actfunctions_of_cls(
                        self.cls, ignore_def=True, ret_action=True
                    )
                ]
            )
            cls_doc = self.cls.__doc__
            parser = self.base_opts()
            if hasattr(self.cls, "action_opts"):
                parser = self.cls.action_opts(parser, for_help=True)

        actions = list(actions)
        action = actions[0] if len(actions) == 1 else None
        actions = ", ".join(sorted(actions))
        options = []
        valid = False
        for ln in parser.format_help().split("\n"):
            if ln.startswith("optional"):
                valid = True
            elif not ln.startswith(" "):
                valid = False
            elif valid:
                options.append(ln)
        options = "\n  ".join(options)
        params = {
            "actions": actions,
            "objs": ", ".join(self.known_objs),
            "options": options,
        }
        print(
            (
                action
                and hasattr(self.cls, action)
                and getattr(self.cls, action).__doc__
                or cls_doc
                or __doc__
            )
            % params
        )
        return 0


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    please = Please(cli_args)
    done = False
    if not please.magic.startswith("-"):
        for action in please.actions or [please.magic]:
            cmd = please.build_function_name_of_cls(please.magic or action)
            if hasattr(please.cls, cmd):
                please.sh_subcmd = please.pickle_params(cmd_subst=action)
                sts = getattr(please.cls, cmd)()
            elif cmd != "do_help" and hasattr(please.cls, "do_action"):
                please.sh_subcmd = please.pickle_params(cmd_subst=action)
                sts = getattr(please.cls, "do_action")()
            elif hasattr(please, cmd):
                sts = getattr(please, cmd)()
            else:
                sts = 126
            if sts:
                return sts
            done = True
    if not done:
        if cli_args and please.magic.startswith("-"):
            please.get_parser().parse_args([please.objname, please.magic])
        else:
            please.get_parser().print_help()
    return 0


if __name__ == "__main__":
    exit(main())
