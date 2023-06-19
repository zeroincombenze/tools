#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

__version__ = "2.0.8"


class PleaseZ0bug(object):

    def __init__(self, please):
        self.please = please

    def get_aliases(self):
        return ["zerobug", "travis"]

    def get_actions(self):
        return ["lint", "show", "summary", "test", "zerobug"]

    def get_default_action(self):
        return "zerobug"

    def action_opts(self, parser):
        parser.add_argument(
            "-A", "--trace-after",
            metavar="REGEX",
            help="travis stops after executed yaml statement"
        )
        self.please.add_argument(parser, "-B")
        self.please.add_argument(parser, "-b")
        parser.add_argument(
            "-C", "--no-cache", action="store_true", help="do not use stored PYPI"
        )
        self.please.add_argument(parser, "-c")
        parser.add_argument(
            "-D",
            "--debug-level",
            metavar="NUMBER",
            help="travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)",
        )
        parser.add_argument(
            "-E", "--no-savenv", action="store_true",
            help="do not save virtual environment into ~/VME/... if does not exist"
        )
        parser.add_argument(
            "-e", "--locale", metavar="ISO", help="use locale"
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="run final travis with full features",
        )
        parser.add_argument(
            "-j",
            "--python",
            metavar="PYVER",
            help=("test with specific python versions (comma separated)"),
        )
        parser.add_argument(
            "-k",
            "--keep",
            action="store_true",
            help=(
                "keep database test"
            ),
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
        self.please.add_argument(parser, "-n")
        self.please.add_argument(parser, "-q")
        parser.add_argument(
            "-S", "--syspkg", metavar="true|false",
            help="use python system packages (def yaml dependents)"
        )
        parser.add_argument(
            "-T", "--trace",
            metavar="REGEX",
            help="trace stops before executing yaml statement"
        )
        self.please.add_argument(parser, "-v")
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
        parser.add_argument('args', nargs="*")
        return parser

    def do_action(self):
        """
NAME
    please z0bug - execute lint and tests

SYNOPSIS
    please [options] lint [z0bug|zerobug]       # execute lint check
    please [options] test [z0bug|zerobug]       # execute regression test
    please [options] show [z0bug|zerobug]       # execute lint + regression test
    please [options] summary [z0bug|zerobug]    # show last lint and/or test result
    please [options] zerobug [z0bug|zerobug]    # show summary of last lint and/or test
    please [options] travis                     # deprecated

DESCRIPTION
    This actions execute the lint and/or the regression tests or show result.
    In previous version of please it was called travis; now travis is deprecated

OPTIONS
     -A --trace-after REGEX
                          test stops after executed yaml statement
     -B --debug           debug mode: do not create log in order to debug session
     -D --debug-level NUMBER
                          travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
     -d NAME, --database NAME
     -E --no-savenv       do not save virtual environment in ~/VME/... if does not exist
     -e --locale ISO
                          use locale
     --full               run final travis with full features
     -f --force           force to create stored VME or remove recent log (wep-db)
     -k --keep            keep DB and virtual environment before and after tests
     -j --python PYVER
                          test with specific python versions (comma separated)
     -L --lint-level LINT_LEVEL
                          lint_check_level: may be minimal,reduced,average,nearby,oca;
                          def value from .travis.yml
     -l --log FILE
                          log file name (def=/home/odoo/travis_log)
     -m --missing         show missing line in report coverage
     -n --dry-run         do nothing (dry-run)
     -p --pattern pattern
                          pattern to apply for test files (comma separated)
     -Q --config file
                          configuration file (def .z0tools.conf)
     -q --quiet           silent mode
     -S --syspkg false|true
                          use python system packages (def yaml dependents)
     -T --trace REGEX
                          trace stops before executing yaml statement
     -V --version         show version
     -v --verbose         verbose mode
     -X --translation 0|1
                          enable translation test (def yaml dependents)
     -Y --yaml-file FILE
                          file yaml to process (def .travis.yml)
     -Z --zero            use local zero-tools

EXAMPLES
    please zerobug

BUGS
    No known bugs."""
        please = self.please
        if please.is_odoo_pkg():
            for action in please.actions:
                if action == "show":
                    cmd = os.path.join(os.getcwd(), "tests", "logs", "show-log.sh")
                    sts = please.run_traced(cmd)
                    if sts:
                        break
                    continue
                if action == "zerobug":
                    params = please.pickle_params(cmd_subst="lint")
                else:
                    params = please.pickle_params()
                cmd = please.build_sh_me_cmd(params=params)
                sts = please.run_traced(cmd)
                if sts == 0 and action == "zerobug":
                    params = please.pickle_params(cmd_subst="test")
                    cmd = please.build_sh_me_cmd(params=params)
                    sts = please.run_traced(cmd)
                if sts:
                    break
            return sts
        elif please.is_repo_odoo() or please.is_pypi_pkg():
            for action in please.actions:
                if action == "zerobug":
                    please.sh_subcmd = please.pickle_params(cmd_subst="emulate")
                elif action == "show":
                    please.sh_subcmd = please.pickle_params(cmd_subst="show-log")
                else:
                    please.sh_subcmd = please.pickle_params()
                cmd = please.build_sh_me_cmd(cmd="travis")
                sts = please.run_traced(cmd)
                if sts:
                    break
            return sts
        return please.do_iter_action(self, act_all_pypi=True, act_tools=False)
