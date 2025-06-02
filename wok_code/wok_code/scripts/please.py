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

    Return sts:
    1: generic error
    3: component not found (warning)
    33: component not found (fatal error)
    123: invalid environment
    125: invalid parameter supplied
    126: invalid action

OPTIONS
  %(options)s

EXAMPLES
    please help zerobug

BUGS
    No known bugs.

SEE ALSO
    Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>
"""

import os
import os.path as pth
import sys
import argparse
import math
import re

# from subprocess import call
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

__version__ = "2.0.22"

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
RMODE = "rU" if sys.version_info[0] == 2 else "r"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CLEAR = "\033[0;m"


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
                self.log_error("No action declared for %s" % self.objname)
                sys.exit(126)
            for action in self.actions or [self.magic]:
                if action not in self.known_actions:
                    self.log_error("Unknown action %s" % action)
                    sys.exit(126)
                if action != "help" and not self.objname:
                    self.log_error(
                        "Missed object for action %s" % "+".join(self.actions)
                    )
                    if self.main_action:
                        self.log_warning(
                            "Please specify one of %s"
                            % self.default_obj[self.main_action]
                        )
                    sys.exit(126)
                if not self.main_action:
                    self.main_action = action
                    break
            for action in self.actions:
                if action != "help" and self.objname not in self.default_obj[action]:
                    self.log_error("Invalid action %s for %s" % (action, self.objname))
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
            "HOME_DEVEL", pth.expanduser("~/devel")
        )
        self.odoo_root = pth.dirname(self.home_devel)
        self.pypi_list = self.get_pypi_list(act_tools=False)
        self.sh_subcmd = self.pickle_params()

    def log_info(self, msg):
        print(msg)

    def log_warning(self, msg):
        print(YELLOW + "  " + msg + CLEAR)

    def log_error(self, msg):
        print(RED + "  " + msg + CLEAR)

    def log_success(self, msg):
        print(GREEN + msg + CLEAR)

    def is_fatal_sts(self, sts):
        return sts in (1, 2) or sts > 9

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
        for fn in sorted(os.listdir(pth.dirname(__file__))):
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
                    self.log_warning("Invalid configuration %s" % fn)
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

    def os_system(self, cmd, verbose=None, rtime=None, with_shell=None):
        return z0lib.os_system(
            cmd,
            verbose=verbose if verbose is not None else self.opt_args.verbose,
            dry_run=self.opt_args.dry_run,
            rtime=rtime if rtime is not None else (verbose and verbose > 1),
            with_shell=with_shell,
        )

    def add_argument(self, parser, arg):
        if arg in ("-B", "--debug"):
            parser.add_argument(
                "-B", "--debug", action="count", default=0, help="debug mode"
            )
        elif arg in ("-b", "--odoo-branch", "--branch"):
            parser.add_argument(
                "-b",
                arg if arg != "-b" else "--odoo-branch",
                dest="branch",
                metavar="BRANCH",
                help="default Odoo version",
            )
        elif arg in ("-C", "--odoo-config"):
            parser.add_argument("-C", "--ignore-cache", action="store_true")
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
                    "force copy (push) | build (publish/test) |"
                    " full (status) | translate"
                ),
            )
        elif arg in ("-G", "--git-org"):
            parser.add_argument(
                "-G", "--git-org", metavar="NAME", help="Git organizzation"
            )
        elif arg in ("-j", "--python"):
            parser.add_argument(
                "-j",
                "--python",
                metavar="PYVER",
                help="Run test with specific python version",
            )
        elif arg in ("-L", "--lang"):
            parser.add_argument(
                "-L", "--lang", action="store", help="iso code", default="it_IT"
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
        elif arg in ("-O", "--oca"):
            parser.add_argument(
                "-O", "--oca", action="store_true", help="Use oca tools when possible"
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
                "-v", "--verbose", help="verbose mode", action="count", default=1
            )
        elif arg in ("-y", "--assume-yes"):
            parser.add_argument("-y", "--assume-yes", action="store_true")
        elif arg in ("--read-only"):
            parser.add_argument("--read-only", action="store_true")
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

    def pickle_params(self, cmd_subst=None, rm_obj=None, slist=[], inherit_opts=[]):
        """Command line has the follow format: <<action object [switches] [sub-action]>>
        This function returns a string from command line args with single value
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
        * special switches can inherit from current environment by inherit_opts:
            - ['-v'] inherits current verbose (-v or --verbose)
        Returned value can be applied to python call()
        """
        inherit_opts = inherit_opts or ["-v"]
        inherit_found = {k: False for k in inherit_opts}
        if "-q" in inherit_found:
            inherit_found["-v"] = True
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
                for k, v in slist:
                    if arg == k:
                        arg = v
                    elif arg.startswith("--") and k.startswith("--"):
                        # --switch=value
                        if arg.split("=", 1)[0] == k:
                            arg = v + "=" + arg.split("=", 1)[1] if v else None
                    elif (
                        arg.startswith("-")
                        and not arg.startswith("--")
                        and k.startswith("-")
                        and not k.startswith("--")
                    ):
                        # -s value or -svalue
                        if k[1] in arg and "*" in k:
                            if arg.endswith(k[1]):
                                ignore_arg = True
                            arg = arg[: arg.index(k[1])]
                        elif k[1] in arg:
                            arg = arg.replace(k[1], v)
            if arg is None or arg == self.objname and rm_obj:
                continue
            for kk in ("-v", "--verbose"):
                if arg.startswith(kk) and any(
                    [arg.startswith(k) for k in inherit_opts]
                ):
                    inherit_found[kk] = True
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
        for k, v in inherit_found.items():
            if not v:
                params += k + " "
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
            objs = list(
                itertools.chain.from_iterable(
                    [self.default_obj[x] for x in self.default_obj if x in self.actions]
                )
            )
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
        return pth.join(self.home_devel, "pypi")

    def get_home_pypi_pkg(self, pkgname):
        root = self.get_home_pypi()
        if pkgname == "tools":
            return pth.join(root, pkgname)
        else:
            return pth.join(root, pkgname, pkgname)

    def get_home_tools(self):
        return pth.join(self.odoo_root, "tools")

    def get_home_tools_pkg(self, pkgname):
        root = self.get_home_tools()
        if pkgname == "tools":
            return root
        return pth.join(root, pkgname)

    def get_pkg_tool_dir(self, pkgtool=False, pkgname=None):
        if hasattr(self.opt_args, "debug") and self.opt_args.debug:
            if pkgtool:
                tools_path = self.get_home_pypi_pkg("tools")
            elif pkgname:
                tools_path = self.get_home_pypi_pkg(pkgname)
            else:
                tools_path = self.get_home_pypi()
        elif pkgname:
            tools_path = self.get_home_tools_pkg(pkgname)
        else:
            tools_path = self.get_home_tools()
        return tools_path

    def is_pypi_pkg(self, path=None):
        path = path or os.getcwd()
        pkgname = pth.basename(path)
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
            path = pth.dirname(path)
            pkgname = pth.basename(path)
        pkgpath = self.get_home_pypi_pkg(pkgname)
        root = pkgpath if pkgname == "tools" else pth.dirname(pkgpath)
        pkgpath2 = self.get_home_tools_pkg(pkgname)
        return (
            pth.isdir(pkgpath)
            and path.startswith(root)
            and pth.isfile(pth.join(root, "setup.py"))
            and (pth.isfile(pth.join(pkgpath, "__init__.py")) or pkgname == "tools")
        ) or (
            pth.isdir(pkgpath2)
            and path.startswith(pkgpath2)
            and pkgname == "tools"
            or (
                pth.isfile(pth.join(pkgpath2, "setup.py"))
                and pth.isfile(pth.join(pkgpath2, "__init__.py"))
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
            pth.isdir(pth.join(path, ".git"))
            and (
                pth.isfile(pth.join(path, "odoo-bin"))
                or pth.isfile(pth.join(path, "openerp-server"))
            )
            and pth.isdir(pth.join(path, "addons"))
            and (
                pth.isdir(pth.join(path, "odoo"))
                and pth.isfile(pth.join(path, "odoo", "__init__.py"))
            )
            or (
                pth.isdir(pth.join(path, "openerp"))
                and pth.isfile(pth.join(path, "odoo", "__init__.py"))
            )
        ):
            return True
        if pth.basename(path) in ("addons", "odoo", "openerp"):
            return self.is_repo_ocb(path=pth.dirname(path))
        return False

    def is_repo_odoo(self, path=None):
        path = path or os.getcwd()
        if not pth.isdir(pth.join(path, ".git")):
            return False
        for fn in os.listdir(path):
            subpath = pth.join(path, fn)
            if pth.isdir(subpath) and self.is_odoo_pkg(path=subpath):
                return True
        return self.is_repo_ocb(pth.dirname(path))

    def get_next_module_path(self, path=None):
        path = path or os.getcwd()
        if pth.isdir(pth.join(path, "odoo", "addons")) and pth.isdir(
            pth.join(path, "addons")
        ):
            paths = []
            for root in pth.join(path, "odoo", "addons"), pth.join(path, "addons"):
                paths += [
                    pth.join(root, x)
                    for x in os.listdir(root)
                    if pth.isdir(pth.join(root, x))
                ]
        elif pth.isdir(pth.join(path, "openerp", "addons")) and pth.isdir(
            pth.join(path, "addons")
        ):
            paths = []
            for root in pth.join(path, "openerp", "addons"), pth.join(path, "addons"):
                paths += [
                    pth.join(root, x)
                    for x in os.listdir(root)
                    if pth.isdir(pth.join(root, x))
                ]
        else:
            paths = [
                pth.join(path, x)
                for x in os.listdir(path)
                if pth.isdir(pth.join(path, x))
            ]
        for subpath in paths:
            if self.is_odoo_pkg(path=subpath):
                yield subpath

    def adj_version(self, module_version, branch=None):
        branch = branch or self.branch
        if not module_version:
            module_version = "0.1.0"
        if module_version[0].isdigit():
            if not module_version.startswith(branch):
                module_version = branch + "." + module_version
        return module_version

    def read_manifest_file(self, manifest_path, force_version=None):
        try:
            with open(manifest_path, RMODE) as fd:
                manifest = eval(fd.read())
        except (ImportError, IOError, SyntaxError):
            raise Exception("Wrong manifest file %s" % manifest_path)
        if force_version:
            manifest["version"] = self.adj_version(manifest.get("version", ""))
        manifest["installable"] = manifest.get("installable", True)
        return manifest

    def get_odoo_version(self, path=None):
        path = path or pth.abspath(os.getcwd())
        home = pth.expanduser("~/")
        version = False
        while not self.is_repo_ocb(path):
            path = pth.dirname(path)
            if path == home or path == "/":
                break
        if self.is_repo_ocb(path):
            release = pth.join(path, "odoo", "release.py")
            if not pth.isfile(release):
                release = pth.join(path, "openerp", "release.py")
            if os.path.isfile(release):
                with open(release, "r") as fd:
                    for line in fd.read().split("\n"):
                        x = re.match(r"version_info *= *\([0-9]+ *, *[0-9]+", line)
                        if x:
                            version = "%d.%d" % eval(x.string.split("=")[1])[0:2]
                            break
        return version

    def get_odoo_branch_from_git(self, try_by_fs=False, raise_if_not_found=True):
        branch = ""
        sts, stdout, stderr = z0lib.os_system_traced(
            "git branch", verbose=False, dry_run=False, rtime=False
        )
        if sts == 0 and stdout:
            sts = 123
            for ln in stdout.split("\n"):
                if ln.startswith("*"):
                    branch = ln[2:]
                    sts = 0
                    break
        if sts == 0:
            x = re.match(r"[0-9]+\.[0-9]+", branch)
            if not x:
                if raise_if_not_found:
                    self.log_error("Unrecognized git branch")
                sts = 123
        if sts == 0:
            branch = branch[x.start(): x.end()]
        elif try_by_fs:
            branch = self.get_odoo_version()
            if branch:
                sts = 0
        return sts, branch

    def get_remote_info(self, verbose=True):
        verbose = verbose and self.opt_args.verbose
        stash_list = ""
        url = upstream = ""
        sts, stdout, stderr = z0lib.os_system_traced(
            "git remote -v", verbose=verbose, rtime=False
        )
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                if not ln:
                    continue
                lns = ln.split()
                if lns[0] == "origin":
                    url = lns[1]
                elif lns[0] == "upstream":
                    upstream = lns[1]
            sts, stdout, stderr = z0lib.os_system_traced(
                "git stash list", verbose=False
            )
            stash_list = stdout
        else:
            if self.path_is_ocb(os.getcwd()):
                url = "https://github.com/odoo/odoo.git"
            else:
                url = "https://github.com/OCA/%s.git" % os.path.basename(os.getcwd())
        return sts, url, upstream, stash_list

    def data_from_url(self, url):
        REV_SHORT_NAMES = {
            "zeroincombenze": "zero",
            "OCA": "oca",
        }

        def get_short_name(uri):
            git_org = pth.splitext(pth.basename(pth.dirname(uri)))[0]
            return REV_SHORT_NAMES.get(git_org, git_org)

        if "git@github.com:" in url:
            git_org = get_short_name(url.split("@")[1].split(":")[1])
            read_only = False
        elif "https:" in url:
            git_org = get_short_name(url.split(":")[1])
            read_only = True
        else:
            git_org = get_short_name(url)
            read_only = True
        return git_org, read_only

    def get_pypi_version(self, path=None):
        path = path or os.getcwd()
        setup = pth.join(path, "setup.py")
        if not pth.isfile(setup):
            setup = pth.join(pth.dirname(path), "setup.py")
        if not pth.isfile(setup):
            self.log_error("No file %s found!" % setup)
            return "2.0.0"
        sts, stdout, stderr = self.call_chained_python_cmd(setup, ["--version"])
        if sts:
            print(stderr)
            return "2.0.0"
        return stdout.split("\n")[0].strip()

    def get_logdir(self, path=None):
        path = path or os.getcwd()
        return pth.join(path, "tests", "logs")

    def get_pypi_list(self, path=None, act_tools=True):
        path = path or (
            self.get_home_pypi()
            if pth.isdir(self.get_home_pypi())
            else self.get_home_tools()
        )
        pypi_list = []
        if pth.isdir(path):
            for fn in os.listdir(path):
                fqn = pth.join(path, fn)
                if fn == "tools" and not act_tools:
                    continue
                if not pth.isdir(fqn):
                    continue
                if self.is_pypi_pkg(path=fqn):
                    pypi_list.append(fn)
        return sorted(pypi_list)

    def get_actions_list(self, actions=None):
        actions = actions.split("+") if actions else ""
        return list(itertools.chain.from_iterable([x.split(",") for x in actions]))

    def build_sh_me_cmd(self, cmd=None, params=None):
        if not cmd:
            cmd = "%s.sh" % pth.splitext(pth.abspath(__file__))[0]
            if not pth.isfile(cmd):
                cmd = pth.split(cmd)
                cmd = pth.join(pth.dirname(cmd[0]), cmd[1])
            if not pth.isfile(cmd):
                self.log_error("Internal package error: file %s not found!" % cmd)
                return ""
        if pth.basename(cmd) == cmd:
            dir = pth.dirname(pth.abspath(__file__))
            while True:
                if pth.isfile(pth.join(dir, cmd)):
                    cmd = pth.join(dir, cmd)
                    break
                if pth.basename(dir) == "scripts":
                    dir = pth.dirname(dir)
                else:
                    break
        cmd += " " + (params or self.sh_subcmd)
        return cmd

    def get_fqn_log(self, what=None, path=None):
        """Get fqn of logfile
        @what:  "sts" for log directories (0=exist, 3=missing)
                "cmd" for fqn show command
                "fqn" for fqn log filename
                "contents" for log filename content
        """
        what = what or "fqn"
        fqn_logdir = self.get_logdir(path=path)
        if not pth.isdir(pth.dirname(fqn_logdir)):
            self.log_warning(
                "Module %s w/o regression test!"
                % pth.basename(pth.dirname(fqn_logdir))
            )
            return 3 if what == "sts" else ""
        if not pth.isdir(fqn_logdir):
            self.log_warning(
                "Module %s w/o regression test result!"
                % pth.basename(pth.dirname(fqn_logdir))
            )
            return 3 if what == "sts" else ""
        if what == "sts":
            return 0
        fqn = pth.join(fqn_logdir, "show-log.sh")
        if not pth.isfile(fqn):
            self.log_error("Command %s not found!" % fqn)
            return ""
        if what == "cmd":
            return fqn
        contents = ""
        with open(fqn, RMODE) as fd:
            contents = fd.read()
        log_fqn = ""
        for ln in contents.split("\n"):
            if ln.startswith("less"):
                log_fqn = pth.join(fqn_logdir, ln.split("/")[-1])
                break
        if not log_fqn or not pth.isfile(log_fqn):
            self.log_warning("Test log file %s not found!" % log_fqn)
            return ""
        if what == "fqn":
            return log_fqn
        contents = ""
        with open(log_fqn, RMODE) as fd:
            contents = fd.read()
        return contents

    def esteem_rate(self, nlines, ntest, tested_lines):
        coverage = tested_lines * 100 / nlines
        xtest = int(nlines * 1.3 / math.log10(nlines))
        qrate = int(115 - math.log10(min(coverage, 80)) * 30)
        return int((coverage * qrate / 100) + (ntest * (100 - qrate) / xtest))

    def evaluate_log(self, contents, path=None):
        log_fqn = self.get_fqn_log(what="fqn", path=path)
        params = {"testpoints": 0}
        for ln in contents.split("\n"):
            if ln.startswith("TOTAL"):
                x = re.search("[0-9]+%?", ln)
                if x:
                    items = ln.split()
                    params["rate"] = items[-1]
                    params["total"] = int(items[-3])
                    params["uncover"] = int(items[-2])
                    params["cover"] = int(items[-3]) - int(items[-2])
            if "SUCCESSFULLY completed" in ln:
                x = re.search("[0-9]+ tests", ln)
                if x:
                    items = ln[x.start(): x.end()].split()
                    params["testpoints"] += int(items[0])
        if "total" not in params:
            self.log_warning("No stats found in %s" % log_fqn)
            return {}
        log_fqn = pth.join(log_fqn, "concurrent_test", "test_concurrent.log")
        if pth.isfile(log_fqn):
            with open(log_fqn, RMODE) as fd:
                contents = fd.read()
            for ln in contents.split("\n"):
                if "SUCCESSFULLY completed" in ln:
                    x = re.search("[0-9]+ tests", ln)
                    if x:
                        items = ln[x.start(): x.end()].split()
                        params["testpoints"] += int(items[0])
        # Q-rating = coverage (60%) + # testpoints*4/total (40%)
        params["esteem_rate"] = self.esteem_rate(
            params["total"], params["testpoints"], params["cover"])
        return params

    def merge_test_result(self):
        contents = self.get_fqn_log(what="contents")
        params = self.evaluate_log(contents)
        if not params:
            return 3
        test_cov_msg = (
            "* [QUA] Test coverage %(rate)s (%(total)d: %(uncover)d+%(cover)d)"
            " [%(testpoints)d TestPoints] - quality rating %(esteem_rate)d (target 100)"
            % params
        )
        changelog_fqn = pth.join("readme", "CHANGELOG.rst")
        if not pth.isfile(changelog_fqn):
            changelog_fqn = pth.join("egg-info", "CHANGELOG.rst")
        if not pth.isfile(changelog_fqn):
            self.log_warning("Changelog history file not found!")
            return 3
        sts = self.chain_python_cmd(
            "arcangelo.py", [changelog_fqn, "-i", '--test-res-msg="%s"' % test_cov_msg]
        )
        return sts

    def chain_python_cmd(self, pyfile, args, verbose=None, rtime=None):
        # call pyfile with args with rtime and return only sts
        return self.call_chained_python_cmd(pyfile, args, verbose=verbose, rtime=rtime)[
            0
        ]

    def call_chained_python_cmd(self, pyfile, args, verbose=None, rtime=None):
        # call pyfile with args with rtime and return sts, stdout, stderr
        cmd = [sys.executable]
        cmd.append(pth.join(pth.dirname(__file__), pyfile))
        for arg in args:
            cmd.append(arg)
        verbose = verbose if verbose is not None else self.opt_args.verbose
        rtime = rtime if rtime is not None else (verbose and verbose > 1)
        return z0lib.os_system_traced(
            cmd, verbose=verbose, dry_run=self.opt_args.dry_run, rtime=rtime
        )

    def do_docs(self):
        return PleaseCwd(self).do_docs()

    def do_translate(self):
        return PleaseCwd(self).do_translate()

    def do_external_cmd(self):
        cmd = self.build_sh_me_cmd()
        if not cmd:
            return 1
        return self.os_system(cmd)

    def do_action_pypipkg(self, action, pkg, path=None):
        path = (
            path or pth.join(self.home_devel, "pypi", pkg, pkg)
            if pkg != "tools"
            else pth.join(self.home_devel, "pypi", pkg)
        )
        if self.opt_args.verbose:
            print("$ cd " + path)
        os.chdir(path)
        return getattr(self.cls, action)()

    def do_iter_action(
        self, action, path=None, act_all_pypi=None, act_tools=None, pypi_list=[]
    ):
        """Iter multiple command on sub projects.

        Args:
            action (str): action name to execute
            act_all_pypi (bool): action on all pypi packages
            act_tools (bool): package tools included in act_all_pypi
        """
        path = path or os.getcwd()
        if act_all_pypi and self.is_all_pypi(path=path):
            sts = 0
            for fn in pypi_list or self.pypi_list:
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
            return self.os_system(self.sh_subcmd)
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

