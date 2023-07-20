#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

__version__ = "2.0.11"


class PleaseZ0bug(object):
    """NAME
        please ACTION z0bug - execute lint and tests

    SYNOPSIS
        please [options] lint [z0bug|zerobug]       # execute lint check
        please [options] test [z0bug|zerobug]       # execute regression test
        please [options] show [z0bug|zerobug]       # show last lint and/or test result
        please [options] summary [z0bug|zerobug]    # show summary of last lint/test
        please [options] zerobug [z0bug|zerobug]    # execute lint + regression test
        please [options] travis                     # deprecated

    DESCRIPTION
        This actions execute the lint and/or the regression tests or show result.
        In previous version of please it was called travis; now travis is deprecated

    OPTIONS
      %(options)s

    EXAMPLES
        please test

    BUGS
        No known bugs.
    """

    def __init__(self, please):
        self.please = please

    def get_aliases(self):
        return ["zerobug", "travis"]

    def get_default_action(self):
        return "zerobug"

    def action_opts(self, parser, for_help=False):
        parser.add_argument(
            "-A",
            "--trace-after",
            metavar="REGEX",
            help="Test stops after executed yaml statement",
        )
        self.please.add_argument(parser, "-B")
        self.please.add_argument(parser, "-b")
        parser.add_argument(
            "-C", "--no-cache", action="store_true", help="Do not use stored PYPI"
        )
        self.please.add_argument(parser, "-c")
        parser.add_argument(
            "-D",
            "--debug-level",
            metavar="NUMBER",
            help="travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)",
        )
        parser.add_argument(
            "-E",
            "--no-savenv",
            action="store_true",
            help="Do not save virtual environment into ~/VME/... if does not exist",
        )
        parser.add_argument("-e", "--locale", metavar="ISO", help="use locale")
        self.please.add_argument(parser, "-f")
        parser.add_argument(
            "--full",
            action="store_true",
            help="Run final test with full features",
        )
        self.please.add_argument(parser, "--python")
        parser.add_argument(
            "-k",
            "--keep",
            action="store_true",
            help="Keep database test",
        )
        parser.add_argument(
            "-L",
            "--lint-level",
            help=(
                "lint_check_level; may be: "
                "minimal,reduced,average,nearby,oca; def value from .travis.yml"
            ),
        )
        parser.add_argument(
            "-m",
            "--missing",
            action="store_true",
            help="Show missing line in report coverage after test",
        )
        if not for_help:
            self.please.add_argument(parser, "-n")
        parser.add_argument(
            "-p",
            "--pattern",
            metavar="PATTERN",
            help="Pattern to match test files ('test*.py' default)",
        )
        if not for_help:
            self.please.add_argument(parser, "-q")
        parser.add_argument(
            "-S",
            "--syspkg",
            metavar="true|false",
            help="Use python system packages (def yaml dependents)",
        )
        parser.add_argument(
            "-T",
            "--trace",
            metavar="REGEX",
            help="Test stops before executing yaml statement",
        )
        if not for_help:
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "-X",
            "--translation",
            metavar="true|false",
            help="Enable translation test (def yaml dependents)",
        )
        parser.add_argument(
            "-Y",
            "--yaml-file",
            metavar="PATH",
            help="File yaml to process (def .travis.yml)",
        )
        parser.add_argument(
            "-Z", "--zero", action="store_true", help="Use local zeroincombenze tools"
        )
        parser.add_argument(
            "--no-translate", action="store_true", help="Disable translation after test"
        )
        parser.add_argument(
            "--no-verify", action="store_true", help="Disable pre-commit on lint"
        )
        parser.add_argument('--ignore-status', action='store_true')
        parser.add_argument("args", nargs="*")
        return parser

    def do_lint(self):
        please = self.please
        if please.is_odoo_pkg():
            sts = 0
            if not please.opt_args.no_verify:
                sts = please.run_traced("pre-commit run", rtime=True)
            if sts == 0:
                please.sh_subcmd = please.pickle_params(
                    rm_obj=True, slist=[("--no-verify", "")])
                cmd = please.build_sh_me_cmd()
                return please.run_traced(cmd, rtime=True)
            return sts
        elif please.is_repo_odoo() or please.is_repo_ocb() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(
                rm_obj=True, slist=[("--no-verify", "")])
            cmd = please.build_sh_me_cmd(cmd="travis")
            return please.run_traced(cmd, rtime=True)
        return please.do_iter_action("do_lint", act_all_pypi=True, act_tools=False)

    def do_show(self):
        please = self.please
        if please.is_odoo_pkg():
            cmd = os.path.join(os.getcwd(), "tests", "logs", "show-log.sh")
            return please.run_traced(cmd)
        elif please.is_repo_odoo() or please.is_repo_ocb() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(cmd="travis")
            return please.run_traced(cmd)
        return please.do_iter_action("do_show", act_all_pypi=True, act_tools=False)

    def do_summary(self):
        please = self.please
        if please.is_odoo_pkg():
            cmd = os.path.join(os.getcwd(), "tests", "logs", "show-log.sh")
            sts = please.run_traced(cmd)
            return 0 if please.opt_args.ignore_status else sts
        elif please.is_repo_odoo() or please.is_repo_ocb() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(cmd="travis")
            sts = please.run_traced(cmd)
            return 0 if please.opt_args.ignore_status else sts
        return please.do_iter_action("do_summary", act_all_pypi=True, act_tools=False)

    def do_test(self):
        please = self.please
        if please.is_odoo_pkg():
            if not please.opt_args.no_verify and os.path.isdir("tests"):
                sts, branch = please.get_odoo_branch_from_git()
                if please.opt_args.debug:
                    if os.environ.get("HOME_DEVEL"):
                        srcpath = os.path.join(os.environ["HOME_DEVEL"], "pypi")
                    elif os.path.isdir("~/odoo/tools"):
                        srcpath = os.path.expanduser("~/odoo/devel/pypi")
                    else:
                        srcpath = os.path.expanduser("~/devel/pypi")
                    srcpath = os.path.join(
                        srcpath, "z0bug_odoo", "z0bug_odoo", "testenv")
                else:
                    if os.environ.get("HOME_DEVEL"):
                        srcpath = os.path.join(
                            os.path.dirname(os.environ["HOME_DEVEL"]), "tools"
                        )
                    elif os.path.isdir("~/odoo/tools"):
                        srcpath = os.path.expanduser("~/odoo/tools")
                    else:
                        srcpath = os.path.expanduser("~/odoo/tools")
                    srcpath = os.path.join(srcpath, "z0bug_odoo", "testenv")
                if branch and int(branch.split(".")[0]) <= 7:
                    please.run_traced(
                        "cp %s/testenv_old_api.py tests/testenv.py" % srcpath,
                        rtime=True)
                else:
                    please.run_traced(
                        "cp %s/testenv.py tests/testenv.py" % srcpath, rtime=True)
                please.run_traced(
                    "cp %s/testenv.rst tests/testenv.rst" % srcpath, rtime=True)
            please.sh_subcmd = please.pickle_params(
                rm_obj=True, slist=[("--no-verify", ""), ("--no-translate", "")])
            cmd = please.build_sh_me_cmd()
            sts = please.run_traced(cmd, rtime=True)
            if sts == 0 and not please.opt_args.no_translate:
                please.sh_subcmd = please.pickle_params(
                    rm_obj=True,
                    slist=[("test", "translate"),
                           ("--no-verify", ""),
                           ("--no-translate", "")])
                cmd = please.build_sh_me_cmd()
                sts = please.run_traced(cmd, rtime=True)
            return sts
        elif please.is_repo_odoo() or please.is_repo_ocb() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(
                rm_obj=True, slist=[("--no-verify", ""), ("--no-translate", "")])
            cmd = please.build_sh_me_cmd(cmd="travis")
            return please.run_traced(cmd, rtime=True)
        return please.do_iter_action("do_test", act_all_pypi=True, act_tools=False)

    def do_zerobug(self):
        please = self.please
        if please.is_odoo_pkg():
            sts = 0
            if not please.opt_args.no_verify:
                sts = please.run_traced("pre-commit run", rtime=True)
            if sts == 0:
                please.sh_subcmd = please.pickle_params(
                    cmd_subst="lint",
                    rm_obj=True,
                    slist=[("--no-verify", ""), ("--no-translate", "")])
                cmd = please.build_sh_me_cmd()
                sts = please.run_traced(cmd, rtime=True)
            if sts == 0:
                please.sh_subcmd = please.pickle_params(
                    cmd_subst="test",
                    rm_obj=True,
                    slist=[("--no-verify", ""), ("--no-translate", "")])
                cmd = please.build_sh_me_cmd()
                sts = please.run_traced(cmd, rtime=True)
            if sts == 0 and not please.opt_args.no_translate:
                please.sh_subcmd = please.pickle_params(
                    rm_obj=True,
                    slist=[("z0bug", "translate"),
                           ("zerobug", "translate"),
                           ("--no-verify", ""),
                           ("--no-translate", "")])
                cmd = please.build_sh_me_cmd()
                sts = please.run_traced(cmd, rtime=True)
            return sts
        elif please.is_repo_odoo() or please.is_repo_ocb() or please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(
                cmd_subst="emulate",
                rm_obj=True,
                slist=[("--no-verify", ""), ("--no-translate", "")])
            cmd = please.build_sh_me_cmd(cmd="travis")
            return please.run_traced(cmd, rtime=True)
        return please.do_iter_action("do_zerobug", act_all_pypi=True, act_tools=False)

    #
    # def do_action(self):
    #     please = self.please
    #     if please.is_odoo_pkg():
    #         for action in please.actions:
    #             if action == "show":
    #                 cmd = os.path.join(os.getcwd(), "tests", "logs", "show-log.sh")
    #                 sts = please.run_traced(cmd)
    #                 if sts:
    #                     break
    #                 continue
    #             if action == "zerobug":
    #                 params = please.pickle_params(cmd_subst="lint")
    #             else:
    #                 params = please.pickle_params()
    #             cmd = please.build_sh_me_cmd(params=params)
    #             sts = please.run_traced(cmd)
    #             if sts == 0 and action == "zerobug":
    #                 params = please.pickle_params(cmd_subst="test")
    #                 cmd = please.build_sh_me_cmd(params=params)
    #                 sts = please.run_traced(cmd)
    #             if sts:
    #                 break
    #         return sts
    #     elif please.is_repo_odoo() or please.is_pypi_pkg():
    #         for action in please.actions:
    #             if action == "zerobug":
    #                 please.sh_subcmd = please.pickle_params(cmd_subst="emulate")
    #             elif action == "show":
    #                 please.sh_subcmd = please.pickle_params(cmd_subst="show-log")
    #             else:
    #                 please.sh_subcmd = please.pickle_params()
    #             cmd = please.build_sh_me_cmd(cmd="travis")
    #             sts = please.run_traced(cmd)
    #             if sts:
    #                 break
    #         return sts
    #     return please.do_iter_action(self, act_all_pypi=True, act_tools=False)
