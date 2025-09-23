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
- CFG:          manage a dictionary value from config file
                like python ConfigParser (only bash)

@author: Antonio M. Vigliotti antoniomaria.vigliotti@gmail.com
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from past.builtins import basestring

import argparse
import configparser
import inspect
import sys
import os
import os.path as pth
from os.path import expanduser as pthuser
from datetime import datetime
import re
from builtins import object
import shutil
import shlex


if sys.version_info[0] == 2:  # pragma: no cover
    from subprocess import PIPE, Popen
    DEVNULL = open("/dev/null", "w").fileno()
    # sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
else:
    from subprocess import PIPE, DEVNULL, Popen


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
RMODE = "rU" if sys.version_info[0] == 2 else "r"

__version__ = "2.1.1"


def os_env(key, default=None):
    return os.environ.get(key, default)


def nakedname(path):
    return pth.splitext(pth.basename(path))[0]


def wep_stdout(stdout):
    mo = True
    while mo:
        mo = re.search(r"\033\[[^a-z]+.", stdout)
        if mo:
            stdout = stdout[:mo.start()] + stdout[mo.end():]
    return stdout


def print_flush(msg, end=None, flush=True):
    if sys.version_info[0] == 3:                                     # pragma: no cover
        print(msg, end=end, flush=flush)
    else:  # pragma: no cover
        print(msg, end=end)
        if flush:
            sys.stdout.flush()


def echo_cmd_verbose(
        args, dry_run=False, os_level=0, humdrum=1, flush=False):  # pragma: no cover
    prompt = ">" if dry_run else "$"
    prompt = ("  " * os_level) + prompt
    eol = ""
    if humdrum == 0 and os_env("PS_RUN_COLOR"):
        prompt += "\033[" + os.environ["PS_RUN_COLOR"] + "m"
        if os_env("PS_NOP_COLOR"):
            eol = "\033[" + os.environ["PS_NOP_COLOR"] + "m"
        else:
            eol = "\033[0m"
    if isinstance(args, (tuple, list)):
        if flush and sys.version_info[0] == 3:
            print_flush("%s %s%s" % (prompt, join_args(args), eol), flush=flush)
        else:
            print_flush("%s %s%s" % (prompt, join_args(args), eol))
    else:
        if flush and sys.version_info[0] == 3:
            print_flush("%s %s%s" % (prompt, args, eol), flush=flush)
        else:
            print_flush("%s %s%s" % (prompt, args, eol))


def clear_tty(dry_run=None, flush=False, humdrum=1):
    if not dry_run and humdrum == 0:
        print_flush("\033[0m", end="", flush=flush)


def split_n_rm_comment_lines(stdout):
    lines = []
    for ln in stdout.split("\n"):
        if not wep_stdout(ln).startswith("#"):
            lines.append(ln)
    return lines


def split_n_extr_cmd_lines(stdout):
    lines = []
    for ln in stdout.split("\n"):
        ln2 = wep_stdout(ln)
        if not ln2.startswith(">") and not ln2.startswith("$"):
            lines.append(ln)
    return lines


def join_args(args):
    cmd = ""
    for arg in args:
        if "<" in arg or ">" in arg:
            arg = "'%s'" % arg.replace("'", r"\'")
        elif " " in arg:  # pragma: no cover
            if '"' in arg:
                arg = '"%s"' % arg.replace('"', r"\"")
            else:
                arg = '"%s"' % arg
        elif '"' in arg:
            arg = '"%s"' % arg.replace('"', r"\"")
        elif "'" in arg:
            arg = '"%s"' % arg
        else:
            pass
        cmd += " " + arg
    return cmd.strip()


def os_system_traced(
        args,
        verbose=0,
        dry_run=None,
        with_shell=None,
        rtime=None,
        os_level=0,
        flush=None,
        humdrum=1):
    # Execute <os.system> like function and return sts, stdout, stderr

    def read_from_proc_n_echo(proc, outerr, rtime):
        log = ""
        ctr = 3
        while True:
            ln = proc.stderr.readline() if outerr == "err" else proc.stdout.readline()
            if not ln:
                if ctr == 0 or proc.poll() is None:
                    break
                ctr -= 1
                continue
            ln = ln.decode("utf8")
            if rtime:
                print_flush(ln, end="", flush=True)
            log += ln
            ctr = 3
        return log

    joined_args = join_args(args) if isinstance(args, (tuple, list)) else args
    if verbose:
        echo_cmd_verbose(args, dry_run=dry_run, os_level=os_level, humdrum=humdrum)

    rtime = True if rtime is None else rtime
    with_shell = True if with_shell is None else with_shell
    prcout = prcerr = ""
    if dry_run:
        return 0, prcout, prcerr
    if sys.version_info[0] == 2:
        try:
            proc = Popen(
                args if not with_shell else joined_args,
                stderr=PIPE,
                stdout=PIPE,
                shell=with_shell,
                executable="/bin/bash" if with_shell else None)
            prcout = read_from_proc_n_echo(proc, "out", rtime)
            prcerr = read_from_proc_n_echo(proc, "err", rtime)
            sts = proc.wait()
        except OSError as e:  # noqa: F821
            if verbose:
                print_flush(e, flush=flush)
            sts = 127
        except BaseException as e:
            if verbose:
                print_flush(e, flush=flush)
            sts = 126
    else:
        try:
            with Popen(
                    args if not with_shell else joined_args,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=with_shell,
                    executable="/bin/bash" if with_shell else None,
            ) as proc:
                prcout = read_from_proc_n_echo(proc, "out", rtime)
                prcerr = read_from_proc_n_echo(proc, "err", rtime)
                sts = proc.wait()
        except FileNotFoundError as e:  # noqa: F821
            if verbose:
                print_flush(e, flush=flush)
            sts = 127
        except BaseException as e:
            if verbose:
                print_flush(e, flush=flush)
            sts = 126
    clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
    return sts, prcout, prcerr


def os_system(
        args,
        verbose=0,
        dry_run=None,
        with_shell=True,
        rtime=True,
        os_level=0,
        flush=None,
        humdrum=1):
    # Execute <os.system> like function (return just sts)

    joined_args = join_args(args) if isinstance(args, (tuple, list)) else args
    if verbose:
        echo_cmd_verbose(
            args, dry_run=dry_run, os_level=os_level, humdrum=humdrum, flush=flush)

    rtime = True if rtime is None else rtime
    with_shell = True if with_shell is None else with_shell
    if dry_run:
        return 0
    if sys.version_info[0] == 2:
        try:
            proc = Popen(
                args if not with_shell else joined_args,
                stdout=None if rtime else DEVNULL,
                stderr=None if rtime else DEVNULL,
                shell=with_shell,
                executable="/bin/bash" if with_shell else None)
            sts = proc.wait()
        except OSError as e:  # noqa: F821
            if verbose:
                print_flush(e, flush=flush)
            sts = 127
        except BaseException as e:
            if verbose:
                print_flush(e, flush=flush)
            sts = 126
    else:
        try:
            with Popen(
                    args if not with_shell else joined_args,
                    stdin=sys.stdin,
                    stdout=None if rtime else DEVNULL,
                    stderr=None if rtime else DEVNULL,
                    shell=with_shell,
                    executable="/bin/bash" if with_shell else None,
            ) as proc:
                sts = proc.wait()
        except FileNotFoundError as e:  # noqa: F821
            if verbose:
                print_flush(e, flush=flush)
            sts = 127
        except BaseException as e:
            if verbose:
                print_flush(e, flush=flush)
            sts = 126
    clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
    return sts


def run_traced(cmd,
               verbose=0,
               dry_run=None,
               disable_alias=None,
               is_alias=None,
               rtime=False,
               flush=True,
               humdrum=1):
    """Run system command with aliases log; return system status and trace log"""

    def cmd_neutral_if(
        args, params=None, switches=None, no_params=None, no_switches=None
    ):
        params = params or []
        switches = switches or []
        no_params = no_params or []
        no_switches = no_switches or []
        if set(params) - set(args):
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

    def sh_any(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        with_shell = False
        while 1:
            sts, prcout, prcerr = os_system_traced(
                args, verbose=verbose, dry_run=dry_run,
                with_shell=with_shell, rtime=rtime,
                flush=flush, humdrum=humdrum)
            if sts == 0 or with_shell or rtime:
                break
            with_shell = True
        clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
        return sts, prcout, prcerr

    def sh_cd(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        if verbose:
            echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
        argv, opt_unk, paths, params = simple_parse(args, {})
        sts = 0
        tgtpath = paths[0] if paths else os.environ["HOME"]
        if pth.isdir(tgtpath):
            os.chdir(tgtpath)
        elif not dry_run:
            sts = 1
        clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
        return sts, "", ""

    def sh_cp(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        if dry_run:
            if verbose:
                echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
            clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
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
            if verbose:
                echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
            if (
                paths[1]
                and pth.basename(paths[1]) != pth.basename(paths[0])
            ):
                paths[1] = pth.join(paths[1], pth.basename(paths[0]))
            if params["-r"] or params["-R"] or params["--recursive"]:
                if params["-L"] or params["--dereference"]:
                    shutil.copytree(paths[0], paths[1], symlinks=True)
                else:
                    shutil.copytree(paths[0], paths[1], symlinks=False)
            else:
                shutil.copy2(paths[0], paths[1])
            clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
            return 0, "", ""
        return sh_any(argv)

    def sh_git(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        if (
            cmd_neutral_if(args, params=['git', 'status'])
            or cmd_neutral_if(args, params=['git', 'branch'], no_switches=['-b'])
            or cmd_neutral_if(args, params=['git', 'remote'], switches=['-v'])
        ):
            dry_run = False
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
                    homes = [pthuser("~")]
                    if os_env("TRAVIS_SAVED_HOME_DEVEL"):
                        homes.append(
                            pth.dirname(os.environ["TRAVIS_SAVED_HOME_DEVEL"]))
                    if os_env("HOME_DEVEL"):
                        homes.append(
                            pth.dirname(os.environ["HOME_DEVEL"]))
                    sts, prcout, prcerr = sh_any(
                        ["getent", "passwd", str(os.getuid())])
                    if sts == 0 and prcout:
                        homes.append(prcout.split("\n")[0].split(":")[5])
                    for home in homes:
                        if repo == "tools":
                            srcpath = pth.join(home, repo)
                        elif repo in ("OCB", "odoo"):
                            srcpath = pth.join(home, odoo_root)
                        else:
                            srcpath = pth.join(home, odoo_root, repo)
                        if pth.isdir(srcpath):
                            break
                        srcpath = ""
        if srcpath:
            tgt = pth.join(paths[2] if len(paths) > 2 else "./", pth.basename(srcpath))
            if pth.isdir(tgt):
                if verbose:
                    echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
                clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
                return 1, "", ""
            os.mkdir(tgt)
            if repo in ("OCB", "odoo"):
                for fn in os.listdir(srcpath):
                    if pth.isdir(pth.join(srcpath, fn, ".git")):
                        continue
                    ffn = pth.join(srcpath, fn)
                    if pth.isdir(ffn):
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
                if verbose:
                    echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
                clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
                return 0, "", ""
            else:
                return run_traced(
                    "cp -r %s %s" % (srcpath, tgt),
                    verbose=verbose,
                    dry_run=dry_run,
                    is_alias=True)
        return sh_any(
            argv, verbose=verbose, dry_run=dry_run, flush=flush, humdrum=humdrum)

    def sh_mkdir(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        prcout = prcerr = ""
        if dry_run:
            if verbose:
                echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
            clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
            return 0, prcout, prcerr
        argv, opt_unk, paths, params = simple_parse(args, {})
        if opt_unk:
            sts, prcout, prcerr = os_system_traced(argv, verbose=verbose)
        else:
            os.mkdir(paths[0])
            sts = 0 if pth.exists(paths[0]) else 1
        clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
        return sts, prcout, prcerr

    def sh_rm(args, verbose=0, dry_run=None, flush=None, humdrum=1):
        prcout = prcerr = ""
        if dry_run:
            if verbose:
                echo_cmd_verbose(args, dry_run=dry_run, humdrum=humdrum)
            clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
            return 0, prcout, prcerr
        argv, opt_unk, paths, params = simple_parse(
            args,
            {
                "-f": False,
                "-R": False,
            }
        )
        tgtpath = paths[0]
        sts = 0 if pth.exists(tgtpath) else 1
        if sts:
            pass
        elif opt_unk or params["-f"]:
            sts, prcout, prcerr = os_system_traced(
                argv, verbose=verbose, flush=flush, humdrum=humdrum)
        elif params["-R"]:
            if verbose:
                echo_cmd_verbose(args, flush=flush, humdrum=humdrum)
            shutil.rmtree(tgtpath)
        else:
            if verbose:
                echo_cmd_verbose(args, flush=flush, humdrum=humdrum)
            os.unlink(tgtpath)
        clear_tty(dry_run=dry_run, flush=flush, humdrum=humdrum)
        return sts, prcout, prcerr

    args = shlex.split(cmd)
    if not disable_alias:
        method = {
            "cd": sh_cd,
            # "cp": sh_cp,
            "git": sh_git,
            "mkdir": sh_mkdir,
            "rm": sh_rm,
        }.get(args[0])
    else:
        method = {
            "cd": sh_cd,
        }.get(args[0])
    if method:
        return method(args, verbose=verbose, dry_run=dry_run, humdrum=humdrum)
    return sh_any(args, verbose=verbose, dry_run=dry_run, flush=flush, humdrum=humdrum)


def chain_python_cmd(
        pyfile,
        args,
        verbose=0,
        dry_run=False,
        rtime=None,
        flush=False,
        humdrum=1):
    cmd = [sys.executable]
    fqn = pyfile
    if "/" not in pyfile:
        fqn = pth.join(pth.dirname(__file__), pyfile)
        if not pth.isdir(fqn):
            fqn = pyfile
    cmd.append(fqn)
    for arg in args:
        cmd.append(arg)
    rtime = rtime if rtime is not None else (verbose and verbose > 1)
    return os_system(cmd,
                     verbose=verbose,
                     dry_run=dry_run,
                     rtime=rtime,
                     flush=flush,
                     humdrum=humdrum)


def chain_python_cmd_traced(
        pyfile,
        args,
        verbose=0,
        dry_run=False,
        rtime=None,
        flush=False,
        humdrum=1):
    cmd = [sys.executable]
    fqn = pyfile
    if "/" not in pyfile:
        fqn = pth.join(pth.dirname(__file__), pyfile)
        if not pth.isdir(fqn):
            fqn = pyfile
    cmd.append(fqn)
    for arg in args:
        cmd.append(arg)
    rtime = rtime if rtime is not None else (verbose and verbose > 1)
    return os_system_traced(cmd,
                            verbose=verbose,
                            dry_run=dry_run,
                            rtime=rtime,
                            flush=flush,
                            humdrum=humdrum)


class Package(object):

    def __init__(self, path=None):
        self.name = None
        self.path = None
        self.prjname = None
        self.prjpath = None
        self.root = None
        self.reposname = None
        self.git_orgid = None
        self.read_only = False
        self.url = None
        self.upstream = None
        self.stash_list = None
        self.dir_level = None
        self.confn = None
        self.branch = None
        self.version = None
        self.majver = None
        self.release = None
        self.manifest = None
        self.testdir = None
        self.rundir = None
        self.log_dir = None
        self.log_fqn = None
        self.log__daemon_fqn = None
        self.installable = True
        self.pyver = ".".join([str(x) for x in sys.version_info[0:2]])
        self.python_versions = []
        self.invalid_names = [
            "build",
            "debian",
            "dist",
            "doc",
            "docs",
            "egg-info",
            "examples",
            "filestore",
            "history",
            "howtos",
            "images",
            "junk",
            "migrations",
            "openupgrade",
            "readme",
            "redhat",
            "reference",
            "scripts",
            "server",
            "setup",
            "static",
            "tests",
            "tmp",
            "tools",
            "travis",
            # "_travis",
            "venv_odoo",
            "win32",
        ]
        self.get_info_from_path(path=path)

    def is_odoo_pkg(self, path=None):
        path = pth.abspath(path or os.getcwd())
        files = os.listdir(path)
        filtered = [
            x
            for x in files
            if x in ("__manifest__.py", "__openerp__.py", "__init__.py")
        ]
        return len(filtered) == 2 and "__init__.py" in filtered

    def is_pypi_pkg(self, path=None):
        path = pth.abspath(path or os.getcwd())
        return (
            pth.isfile(pth.join(path, "__init__.py")) and (
                pth.isfile(os.path.join(path, "setup.py"))
                or pth.isfile(os.path.join(path, "..", "setup.py")))
        )

    def is_repo_ocb(self, path=None):
        path = pth.abspath(path or os.getcwd())
        return (
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
        )

    def is_repo_odoo(self, path=None):
        path = pth.abspath(path or os.getcwd())
        if not pth.isdir(pth.join(path, ".git")):
            return False
        for fn in os.listdir(path):
            subpath = pth.join(path, fn)
            if pth.isdir(subpath) and self.is_odoo_pkg(path=subpath):
                return True
        return self.is_repo_ocb(pth.dirname(path))

    def is_repo_pypi(self, path=None):
        path = pth.abspath(path or os.getcwd())
        if not pth.isdir(pth.join(path, ".git")):
            return False
        for fn in os.listdir(path):
            subpath = pth.join(path, fn)
            if pth.isdir(subpath) and pth.isfile(pth.join(subpath, "setup.py")):
                return True
        return False

    def get_majver(self, version):
        majver = int(version.split(".")[0]) if version else 0
        return majver if 6 <= majver <= 19 else 0

    def extract_release(self, version):
        mo = re.search(r"[0-9]+\.[0-9]+", version)
        if mo:
            return version[mo.start(): mo.end()]
        return None

    def get_remote_info(self, path=None):
        path = pth.abspath(path or os.getcwd())
        saved_path = pth.abspath(os.getcwd())
        if path and path != saved_path:
            os.chdir(path)
        sts, stdout, stderr = os_system_traced(
            "git branch", verbose=False, dry_run=False, rtime=False
        )
        if sts == 0 and stdout:
            sts = 123
            for ln in stdout.split("\n"):
                if ln.startswith("*"):
                    self.branch = ln[2:]
                    sts = 0
                    break
            if sts == 0:
                release = self.extract_release(self.branch)
                if release:
                    self.release = release
                    if not self.version:
                        self.version = self.release
                        self.majver = self.get_majver(self.version)
        elif self.prjname == "Odoo":
            mo = re.search(r"[0-9]+\.[0-9]+", path)
            if not mo:
                mo = re.search(r"[0-9]+", path)
            if mo:
                branch = path[mo.start(): mo.end()]
                majver = self.get_majver(branch)
                if "." not in branch and majver:
                    branch += ".0" if majver > 6 else ".1"
                self.release = branch
                if not self.version:
                    self.version = branch
                    self.majver = majver
        sts, stdout, stderr = os_system_traced(
            "git remote -v", verbose=False, dry_run=False, rtime=False)
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                if not ln:
                    continue
                lns = ln.split()
                if lns[0] == "origin":
                    self.url = lns[1]
                elif lns[0] == "upstream":
                    self.upstream = lns[1]
            sts, stdout, stderr = os_system_traced(
                "git stash list", verbose=False
            )
            if sts == 0:
                self.stash_list = stdout
        elif self.prjname == "Odoo":
            self.git_orgid = "oca"
        elif self.prjname == "Z0tools":
            self.git_orgid = "zero"
        os.chdir(saved_path)

    def data_from_url(self):
        REV_SHORT_NAMES = {
            "zeroincombenze": "zero",
            "OCA": "oca",
        }

        def get_short_name(uri):
            git_org = pth.splitext(pth.basename(pth.dirname(uri)))[0]
            return REV_SHORT_NAMES.get(git_org, git_org)

        if self.url:
            if "git@github.com:" in self.url:
                self.git_orgid = get_short_name(self.url.split("@")[1].split(":")[1])
                self.read_only = False
            elif "https:" in self.url:
                self.git_orgid = get_short_name(self.url.split(":")[1])
                self.read_only = True
            else:
                self.git_orgid = get_short_name(self.url)
                self.read_only = True
        elif self.git_orgid == "oca":
            self.read_only = True

    def candidate(self, path):
        pkgname = pth.basename(path)
        if pkgname in self.invalid_names or pkgname.startswith((".", "_")):
            return False
        return pkgname

    def get_info_from_path(self, path=None):
        p = pth.abspath(path or os.getcwd())
        while pth.isdir(p) and not pthuser("~").startswith(p) and p != "/":
            pkgname = self.candidate(p)
            if not pkgname:
                if self.name and self.prjname and self.dir_level:
                    break
            elif not self.dir_level and self.is_odoo_pkg(path=p):
                self.path = p
                self.rundir = p
                self.name = pkgname
                self.prjname = "Odoo"
                self.dir_level = "module"
                if pth.isfile(pth.join(p, "__manifest__.py")):
                    self.manifest = pth.join(p, "__manifest__.py")
                elif pth.isfile(pth.join(p, "__openerp__.py")):
                    self.manifest = pth.join(p, "__openerp__.py")
                if pth.isdir(pth.join(p, "tests")):
                    self.testdir = pth.join(p, "tests")
                self.read_manifest_file()
            elif not self.dir_level and self.is_pypi_pkg(path=p):
                self.rundir = p
                if not self.name:
                    self.name = pkgname
                self.prjname = "Z0tools"
                self.dir_level = "module"
                if pth.isfile(pth.join(p, "setup.py")):
                    self.manifest = pth.join(p, "setup.py")
                    self.path = p
                    self.get_pypi_version()
                elif pth.isfile(pth.join(pth.dirname(p), "setup.py")):
                    self.manifest = pth.join(pth.dirname(p), "setup.py")
                    self.path = pth.dirname(p)
                    self.get_pypi_version(path=self.path)
                if pth.isdir(pth.join(p, "tests")):
                    self.testdir = pth.join(p, "tests")
            elif (not self.prjname
                  or self.prjname == "Odoo") and self.is_repo_ocb(path=p):
                self.root = p
                if not self.name and not self.prjpath:
                    self.name = "OCB"
                    self.prjname = "Odoo"
                    self.prjpath = p
                    if not self.reposname:
                        self.reposname = "OCB"
                    if not self.dir_level:
                        self.dir_level = "repo"
                    self.get_odoo_version(path=p)
                    self.get_remote_info(path=p)
                break
            elif (not self.prjname
                  or self.prjname == "Odoo") and self.is_repo_odoo(path=p):
                if not self.name:
                    self.name = pkgname
                self.prjname = "Odoo"
                self.prjpath = p
                self.reposname = pkgname
                if not self.dir_level:
                    self.dir_level = "repo"
                self.get_remote_info(path=p)
            elif (not self.prjname
                  or self.prjname == "Z0tools") and self.is_repo_pypi(path=p):
                if not self.name:
                    self.name = pkgname
                self.prjname = "Z0tools"
                self.prjpath = p
                # Wrong: just for compatibility with bash
                self.reposname = "tools"
                if not self.dir_level:
                    self.dir_level = "repo"
                self.get_remote_info(path=p)
            if self.prjname != "Odoo" and pth.isdir(pth.join(p, ".git")):
                break
            p = pth.dirname(p)
        self.data_from_url()
        if not self.prjname:
            self.prjname = os_env("PRJNAME")
        if not self.reposname:
            self.reposname = os_env("REPOSNAME")
        if not self.path:
            self.path = os_env("PKGPATH", os.getcwd())
        if not self.git_orgid:
            self.git_orgid = os_env("GIT_ORGID", "")

    def get_odoo_version(self, path=None):
        p = pth.abspath(path or os.getcwd())
        release = pth.join(p, "odoo", "release.py")
        if not pth.isfile(release):
            release = pth.join(p, "openerp", "release.py")
        if os.path.isfile(release):
            with open(release, RMODE) as fd:
                for line in fd.read().split("\n"):
                    mo = re.match(
                        r"version_info *= *\([0-9]+ *, *[0-9]+",
                        line.replace("FINAL", "0"))
                    if mo:
                        self.release = "%d.%d" % eval(mo.string.split("=")[1])[0:2]
                        if not self.version:
                            self.version = self.release
                            self.majver = self.get_majver(self.version)
                        break

    def get_pypi_version(self, path=None):
        if os.path.isfile(self.manifest):
            sts, stdout, stderr = chain_python_cmd_traced(
                self.manifest, ["--version"])
            if sts:
                raise Exception("Wrong manifest file %s" % self.manifest)
            self.version = stdout.split("\n")[0]
            if not self.release:
                self.release = self.version

    def read_manifest_file(self):
        try:
            with open(self.manifest, RMODE) as fd:
                manifest = eval(fd.read())
        except (ImportError, IOError, SyntaxError):
            raise Exception("Wrong manifest file %s" % self.manifest)
        version = manifest.get("version")
        majver = self.get_majver(version)
        if 6 <= majver <= 19:
            self.version = version
            self.majver = majver
            release = self.extract_release(version)
            if release and not self.release:
                self.release = release
        elif self.release:
            self.version = self.release
            self.majver = self.get_majver(self.version)
        self.installable = manifest.get("installable", True)

    def get_version_to_log(self):
        if self.prjname == "Odoo":
            ver = ("0" + (self.version or "18.0").split(".")[0])[-2:]
        elif self.prjname == "Z0tools":
            ver = (
                self.pyver.replace(".", "0")
                if re.match(r"[23]\.[6789]", self.pyver)
                else self.pyver.replace(".", "")
            )
        else:
            ver = ""
        return ver

    def get_uniqid(self, ignore_version=False):
        # UDI (Unique DB Identifier): format "{pkgname}_{git_org}{major_version}"
        # UMLI (Unique Module Log Identifier):
        #     format "{git_org}{major_version}.{repos}.{pkgname}"
        if ignore_version:
            ver = "..."
        else:
            ver = self.get_version_to_log()
        udi = self.name
        umli = ""
        if self.git_orgid and self.git_orgid not in (
                "oca", "odoo", "zero", "zeroincombenze"):
            udi += "_" + self.git_orgid
            umli = self.git_orgid
        if ver:
            udi += "_" + ver
        if self.reposname and self.reposname != "OCB":
            if umli:
                umli += "." + self.reposname
            else:
                umli = self.reposname
        if umli:
            umli += "." + self.name
        else:
            umli = self.name
        if ver and umli:
            umli += "_" + ver
        return udi, umli

    def get_log_dir(self, fqn=None):
        home = pthuser(os_env("TRAVIS_SAVED_HOME") or "~/")
        if fqn:
            logdir = pth.dirname(pthuser(pth.abspath(fqn)))
            self.log_dir = logdir
        elif self.log_dir:
            logdir = self.log_dir
        elif self.read_only:
            logdir = pth.join(home, "travis_log")
            self.log_dir = logdir
        else:
            testdir = self.testdir
            if not testdir:
                testdir = pthuser(pth.join(self.rundir, "tests"))
            logdir = pth.join(testdir, "logs")
            self.log_dir = logdir
        return logdir

    def get_log_filename(self, fqn=None):
        if fqn:
            log_fqn = pth.dirname(pthuser(pth.abspath(fqn)))
            logdir = pth.dirname(log_fqn)
            log_daemon_fqn = log_fqn.replace(".log", "_nohup.log")
            self.log_fqn = log_fqn
            self.log__daemon_fqn = log_daemon_fqn
        elif self.log_fqn:
            logdir = self.log_dir
            log_fqn = self.log_fqn
            log_daemon_fqn = self.log__daemon_fqn
        else:
            logdir = self.get_log_dir()
            udi, umli = self.get_uniqid()
            today = datetime.now()
            today = datetime(today.year, today.month, today.day)
            suffix = "%s+%05d.log" % (datetime.strftime(today, "%Y%m%d"),
                                      (datetime.now() - today).seconds)
            log_fqn = pth.join(logdir, "%s-%s" % (umli, suffix))
            log_daemon_fqn = pth.join(logdir, "%s_nohup-%s" % (umli, suffix))
            self.log_fqn = log_fqn
            self.log__daemon_fqn = log_daemon_fqn
        return logdir, log_fqn, log_daemon_fqn

    def list_log_filename(self, all_version=True):
        logdir = self.get_log_dir()
        # udi, umli = self.get_uniqid(ignore_version=all_version)
        ver = self.get_version_to_log()
        rex = (
            r"[0-9]{4}-?[0-9]{2}-?[0-9]{2}(\+[0-9]+)?.log" if all_version
            else r"_%s-[0-9]{4}-?[0-9]{2}-?[0-9]{2}(\+[0-9]+)?.log" % ver)
        log_filenames = []
        if pth.isdir(logdir):
            for fn in sorted(os.listdir(logdir), reverse=True):
                if re.search(rex, fn):
                    log_filenames.append(pth.join(logdir, fn))
        return log_filenames


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
                        default=0,
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
                elif len(args) == 2 and args[1].startswith("--"):
                    self.param_list.append(args[1][2:].replace("-", "_"))
                self.parser.add_argument(*args, **kwargs)

    def default_conf(self, ctx):
        return DEFDCT

    def get_this_fqn(self):
        i = 1
        valid = False
        while not valid:
            this_fqn = pth.abspath(inspect.stack()[i][1])
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
                    if pth.isfile(f):
                        ctx['conf_fns'] = (f, ctx['conf_fn'])
                        found = True
                        break
                if not found:
                    ctx['conf_fns'] = ctx['conf_fn']
            else:
                if pth.isfile(ODOO_CONF):
                    ctx['conf_fns'] = (ODOO_CONF, ctx['conf_fn'])
                elif pth.isfile(OE_CONF):
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
        @param version   software version to display with -V option
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
            if os_env('VERBOSE_MODE', '') in ('0', '1'):
                ctx[p] = int(os.environ['VERBOSE_MODE'])
            elif os.isatty(0):
                ctx[p] = 1
            else:
                ctx[p] = 0
        return ctx
