# -*- coding: utf-8 -*-
"""@mainpage
Zeroincombenze® general purpose library
=======================================

Library with various functionalities for python and bash programs.
Area managed:
- parseoptargs: line command parser; expands python argparse and adds same
                functionalities to bash scripts
- xuname:       platform recognition (only bash); return info about host
- tracelog:     manage tracelog (only bash)
- run_traced:   execute (or dry_run) shell command
- findpkg:      find package in file system (only bash)
- CFG:          manage a dictionay value from config file
                like python ConfigParser (only bash)

@author: Antonio M. Vigliotti antoniomaria.vigliotti@gmail.com
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future import standard_library
from past.builtins import basestring

import argparse
import configparser
import inspect
import sys
import os
from builtins import object
import shutil
import shlex
from subprocess import PIPE, Popen
# from python_plus import qsplit
standard_library.install_aliases()  # noqa: E402


# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = "./clodoo.conf"
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = [
    "/etc/odoo/odoo-server.conf",
    "/etc/odoo-server.conf",
    "/etc/openerp/openerp-server.conf",
    "/etc/openerp-server.conf",
    "/etc/odoo/openerp-server.conf",
    "/etc/openerp/odoo-server.conf",
]
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
DEFDCT = {}
__version__ = "2.0.3"


def nakedname(path):
    return os.path.splitext(os.path.basename(path))[0]


def run_traced(cmd, verbose=None, dry_run=None, disable_alias=None, is_alias=None):

    def cmd_neutral_if(
        args, params=None, switches=None, no_params=None, no_switches=None
    ):
        params = params or []
        switches = switches or []
        no_params = no_params or []
        no_switches = no_switches or []
        if (set(params) - set(args)):
            return False
        if no_params and not (set(no_params) - set(args)):
            return False
        if switches:
            ctr = 0
            for item in switches:
                item = item[1:]
                if any([x for x in args if x.startswith("-") and item in x]):
                    ctr += 1
            if ctr != len(switches):
                return False
        if no_switches:
            ctr = 0
            for item in no_switches:
                item = item[1:]
                if any([x for x in args if x.startswith("-") and item in x]):
                    ctr += 1
            if ctr == len(no_switches):
                return False
        return True

    def simple_parse(args, params):
        argv = []
        opt_unk = False
        action = ""
        paths = []
        while args:
            arg = args.pop(0)
            argv.append(arg)
            if arg.startswith("--"):
                arg2 = arg.split("=", 1)
                if len(arg2) > 1:
                    arg = arg2[0]
                    if arg not in params:
                        opt_unk = True
                    params[arg] = arg2[1]
                else:
                    if arg not in params:
                        opt_unk = True
                    if arg in params and isinstance(params[arg], basestring):
                        arg2 = args.pop(0)
                        params[arg] = arg2
                        argv.append(arg2)
                    else:
                        params[arg] = True
            elif arg.startswith("-"):
                res = arg[1:]
                while res:
                    arg = "-" + res[0]
                    res = res[1:]
                    if arg not in params:
                        opt_unk = True
                    if arg in params and isinstance(params[arg], basestring):
                        if res:
                            params[arg] = res
                            res = ""
                        else:
                            arg2 = args.pop(0)
                            argv.append(arg2)
                            params[arg] = arg2
                    else:
                        params[arg] = True
            elif not action:
                action = arg
            else:
                paths.append(arg)
        return argv, opt_unk, paths, params

    def sh_any(args, verbose=None, dry_run=None):
        prcout = prcerr = ""
        if (
            cmd_neutral_if(args, params=['dir'])
            or cmd_neutral_if(args, params=['ls'])
        ):
            dry_run = False
        if dry_run:
            0, prcout, prcerr
        if sys.version_info[0] == 2:
            try:
                proc = Popen(args, stderr=PIPE, stdout=PIPE)
                prcout, prcerr = proc.communicate()
                sts = proc.returncode
                prcout = prcout.decode("utf-8")
                prcerr = prcerr.decode("utf-8")
            except OSError as e:
                if verbose:
                    print(e)
                sts = 127
            except BaseException:
                sts = 126
        else:
            try:
                with Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                    prcout, prcerr = proc.communicate()
                    sts = proc.returncode
                    prcout = prcout.decode("utf-8")
                    prcerr = prcerr.decode("utf-8")
            except FileNotFoundError as e:                                 # noqa: F821
                if verbose:
                    print(e)
                sts = 127
            except BaseException:
                sts = 126
        return sts, prcout, prcerr

    def sh_cd(args, verbose=None, dry_run=None):
        argv, opt_unk, paths, params = simple_parse(args, {})
        sts = 0
        tgtpath = paths[0] if paths else os.environ["HOME"]
        if os.path.isdir(tgtpath):
            os.chdir(tgtpath)
        elif not dry_run:
            sts = 1
        return sts, "", ""

    def sh_cp(args, verbose=None, dry_run=None):
        if dry_run:
            return 0, "", ""
        argv, opt_unk, paths, params = simple_parse(
            args, {
                "-r": False,
                "-R": False,
                "--recursive": False,
                "-L": False,
                "--dereference": False,
            }
        )
        if not opt_unk and paths[0] and paths[1]:
            if (
                paths[1]
                and os.path.basename(paths[1]) != os.path.basename(paths[0])
            ):
                paths[1] = os.path.join(paths[1], os.path.basename(paths[0]))
            if params["-r"] or params["-R"] or params["--recursive"]:
                if params["-L"] or params["--dereference"]:
                    shutil.copytree(paths[0], paths[1], symlinks=True)
                else:
                    shutil.copytree(paths[0], paths[1], symlinks=False)
            else:
                shutil.copy2(paths[0], paths[1])
            return 0, "", ""
        return sh_any(argv)

    def sh_git(args, verbose=None, dry_run=None):
        if (
            cmd_neutral_if(args, params=['git', 'status'])
            or cmd_neutral_if(args, params=['git', 'branch'], no_switches=['-b'])
            or cmd_neutral_if(args, params=['git', 'remote'], switches=['-v'])
        ):
            dry_run = False
        if dry_run:
            return 0, "", ""
        argv, opt_unk, paths, params = simple_parse(
            args, {
                "-b": "",
                "--branch": "",
                "--depth": "",
                "--single-branch": False,
                "--no-single-branch": False,
            }
        )
        srcpath = repo = ""
        if paths[0] == "clone":
            opt_branch = params["-b"] or params["--branch"]
            if opt_branch and opt_branch.split(".")[0].isdigit():
                majver = opt_branch.split(".")[0]
                repo = odoo_root = ""
                if (
                    paths[1].startswith("https://github.com/odoo/")
                    or paths[1].startswith("https://github.com/OCA/")
                ):
                    repo = paths[1].split("/")[-1][: -4]
                    odoo_root = "oca" + majver
                elif (
                    paths[1].startswith("https://github.com/zeroincombenze/")
                    or paths[1].startswith("https://github.com/LibrERP-network/")
                ):
                    repo = paths[1].split("/")[-1][: -4]
                    odoo_root = opt_branch
                if repo:
                    homes = [os.path.expanduser("~")]
                    if os.environ.get("TRAVIS_SAVED_HOME_DEVEL"):
                        homes.append(
                            os.path.dirname(os.environ["TRAVIS_SAVED_HOME_DEVEL"]))
                    if os.environ.get("HOME_DEVEL"):
                        homes.append(
                            os.path.dirname(os.environ["HOME_DEVEL"]))
                    sts, prcout, prcerr = sh_any(
                        ["getent", "passwd", str(os.getuid())])
                    if sts == 0 and prcout:
                        homes.append(prcout.split("\n")[0].split(":")[5])
                    for home in homes:
                        if repo == "tools":
                            srcpath = os.path.join(home, repo)
                        elif repo in ("OCB", "odoo"):
                            srcpath = os.path.join(home, odoo_root)
                        else:
                            srcpath = os.path.join(home, odoo_root, repo)
                        if os.path.isdir(srcpath):
                            break
                        srcpath = ""
        if srcpath:
            tgt = os.path.join(paths[2] if len(paths) > 2 else "./",
                               os.path.basename(srcpath))
            if os.path.isdir(tgt):
                return 1, "", ""
            os.mkdir(tgt)
            if repo in ("OCB", "odoo"):
                for fn in os.listdir(srcpath):
                    if os.path.isdir(os.path.join(srcpath, fn, ".git")):
                        continue
                    ffn = os.path.join(srcpath, fn)
                    if os.path.isdir(ffn):
                        run_traced(
                            "cp -r %s %s" % (ffn, tgt),
                            verbose=verbose,
                            dry_run=dry_run,
                            is_alias=True)
                    else:
                        run_traced(
                            "cp %s %s" % (ffn, tgt),
                            verbose=verbose,
                            dry_run=dry_run,
                            is_alias=True)
                return 0, "", ""
            else:
                return run_traced(
                    "cp -r %s %s" % (srcpath, tgt),
                    verbose=verbose,
                    dry_run=dry_run,
                    is_alias=True)
        return sh_any(argv, verbose=verbose, dry_run=dry_run)

    def sh_mkdir(args, verbose=None, dry_run=None):
        if dry_run:
            return 0, "", ""
        argv, opt_unk, paths, params = simple_parse(args, {})
        if opt_unk:
            with Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                proc.wait()
                sts = proc.returncode
        else:
            os.mkdir(paths[0])
            sts = 0 if os.path.exists(paths[0]) else 1
        return sts, "", ""

    def sh_rm(args, verbose=None, dry_run=None):
        if dry_run:
            return 0, "", ""
        argv, opt_unk, paths, params = simple_parse(
            args,
            {
                "-f": False,
                "-R": False,
            }
        )
        tgtpath = paths[0]
        sts = 0 if os.path.exists(tgtpath) else 1
        if sts:
            pass
        elif opt_unk or not params["-f"]:
            with Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                proc.wait()
                sts = proc.returncode
        elif params["-R"]:
            shutil.rmtree(tgtpath)
        else:
            os.unlink(tgtpath)
        return sts, "", ""

    if verbose:
        if is_alias:
            print('%s %s' % ("  >" if dry_run else "  $", cmd))
        else:
            print('%s %s' % (">" if dry_run else "$", cmd))
    args = shlex.split(cmd)
    if not disable_alias:
        method = {
            "cd": sh_cd,
            # "cp": sh_cp,
            "git": sh_git,
            "mkdir": sh_mkdir,
            "rm": sh_rm,
        }.get(args[0])
        if method:
            return method(args, verbose=verbose, dry_run=dry_run)
    return sh_any(args, verbose=verbose, dry_run=dry_run)


class CountAction(argparse.Action):
    def __init__(self, option_strings, dest, default=None, required=False, help=None):
        super(CountAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # new_count = argparse._ensure_value(namespace, self.dest, 0)
        new_count = self.dest if isinstance(self.dest, int) else 0
        if option_string != '-q':
            new_count += 1
        setattr(namespace, self.dest, new_count)


class parseoptargs(object):
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(description=args[0], epilog=args[1])
        if 'version' in kwargs:
            self.version = kwargs['version']
        self.param_list = []

    def add_argument(self, *args, **kwargs):
        """Add argument to param list
        @param *args    positional arg; format may be '-x', '--xx' or 'xxx'
        @param action   action done when option is encountered; may be
                    - 'store' ('=' in bash); get value follows param
                        i.e. --opt=value -l value
                    - 'store_const'  (then constant value in bash);
                        set constant value from 'const' param
                    - 'store_true' 'store_false': same above, boolean value
                    - 'append' (not implemented in bash)
                    - 'count' ('+' in bash); how many times option occurs
                    - CountAction; same ad 'count' but may reset by '-q' option
                    - 'help'
                    - 'version'
        @param dest     internal name of param
        @param default  declare default value
        @param metavar  complete help for action_store
        """
        if len(args) and args[0][0] != '-':
            self.param_list.append(args[0])
            self.parser.add_argument(*args, **kwargs)
        elif args[0] != '-h' and args[0] != '--help':
            if len(args) == 1:
                if args[0] == '-n' or args[0] == '--dry-run':
                    self.parser.add_argument(
                        '-n',
                        '--dry-run',
                        help='do nothing (dry-run)',
                        action='store_true',
                        dest='dry_run',
                        default=False,
                    )
                    self.param_list.append('dry_run')
                elif args[0] == '-q' or args[0] == '--quite':
                    self.parser.add_argument(
                        '-q',
                        '--quiet',
                        help="silent mode",
                        action=CountAction,
                        dest="opt_verbose",
                    )
                    self.param_list.append('opt_verbose')
                elif args[0] == '-V' or args[0] == '--version':
                    self.parser.add_argument(
                        '-V', '--version', action='version', version=self.version
                    )
                elif args[0] == '-v' or args[0] == '--verbose':
                    self.parser.add_argument(
                        '-v',
                        '--verbose',
                        help="verbose mode",
                        action=CountAction,
                        dest="opt_verbose",
                    )
                    self.param_list.append('opt_verbose')
                else:
                    raise NotImplementedError
            else:
                if 'dest' in kwargs:
                    self.param_list.append(kwargs['dest'])
                self.parser.add_argument(*args, **kwargs)

    def default_conf(self, ctx):
        return DEFDCT

    def get_this_fqn(self):
        i = 1
        valid = False
        while not valid:
            this_fqn = os.path.abspath(inspect.stack()[i][1])
            this = nakedname(this_fqn)
            if this in ("__init__", "pdb", "cmd", "z0testlib", "z0lib"):
                i += 1
            else:
                valid = True
        return this_fqn

    def create_params_dict(self, ctx):
        """Create default params dictionary"""
        opt_obj = ctx.get('_opt_obj', None)
        if opt_obj:
            for p in self.param_list:
                ctx[p] = getattr(opt_obj, p)
        return ctx

    def read_config(self, ctx):
        """Read both user configuration and local configuration."""
        if not ctx.get('conf_fn', None):
            if CONF_FN:
                ctx['conf_fn'] = CONF_FN
            else:
                ctx['conf_fn'] = "./" + ctx['caller'] + ".conf"
        conf_obj = configparser.ConfigParser(self.default_conf(ctx))
        if ODOO_CONF:
            if isinstance(ODOO_CONF, list):
                found = False
                for f in ODOO_CONF:
                    if os.path.isfile(f):
                        ctx['conf_fns'] = (f, ctx['conf_fn'])
                        found = True
                        break
                if not found:
                    ctx['conf_fns'] = ctx['conf_fn']
            else:
                if os.path.isfile(ODOO_CONF):
                    ctx['conf_fns'] = (ODOO_CONF, ctx['conf_fn'])
                elif os.path.isfile(OE_CONF):
                    ctx['conf_fns'] = (OE_CONF, ctx['conf_fn'])
                else:
                    ctx['conf_fns'] = ctx['conf_fn']
        else:
            ctx['conf_fns'] = ctx['conf_fn']
        ctx['conf_fns'] = conf_obj.read(ctx['conf_fns'])
        ctx['_conf_obj'] = conf_obj
        return ctx

    def parseoptargs(
        self, arguments, apply_conf=APPLY_CONF, version=None, tlog=None, doc=None
    ):
        """Parse command-line options.
        @param arguments list of arguments; should argv from command line
        @param version   software version to displya with -V option
                         in bash version reports __version__ variable of script
        """
        ctx = {}
        this_fqn = self.get_this_fqn()
        ctx['this_fqn'] = this_fqn
        this = nakedname(this_fqn)
        ctx['this'] = this
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:  # pragma: no cover
            ctx['run_daemon'] = True
        ctx['run_tty'] = os.isatty(0)
        if tlog:
            ctx['tlog'] = tlog
        else:
            ctx['tlog'] = this + '.log'
        # running autotest
        if version is None:
            ctx['_run_autotest'] = True
        ctx['_parser'] = self.parser
        opt_obj = self.parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        if apply_conf:
            if hasattr(opt_obj, 'conf_fn'):
                ctx['conf_fn'] = opt_obj.conf_fn
            ctx = self.read_config(ctx)
            opt_obj = self.parser.parse_args(arguments)
        ctx = self.create_params_dict(ctx)
        p = 'opt_verbose'
        if p in ctx and ctx[p] is None:
            if os.environ.get('VERBOSE_MODE', '') in ('0', '1'):
                ctx[p] = int(os.environ['VERBOSE_MODE'])
            elif os.isatty(0):
                ctx[p] = 1
            else:
                ctx[p] = 0
        return ctx
