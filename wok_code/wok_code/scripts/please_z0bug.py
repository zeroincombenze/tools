#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = "2.0.7"


class PleaseZ0bug(object):

    def __init__(self, please):
        self.please = please

    def get_aliases(self):
        return ["zerobug", "travis"]

    def get_actions(self):
        return ["lint", "show", "summary", "test", "z0bug"]

    def action_opts(self, parser):
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
            "--full",
            action="store_true",
            help="run final travis with full features",
        )
        parser.add_argument(
            "-j",
            "--python",
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

    def do_action(self):
        """
NAME
    please z0bug - execute lint and tests

SYNOPSIS
    please [options] z0bug
    please [options] zerobug
    please [options] travis (deprecated)

DESCRIPTION
    This action executes the lint and the regression tests.
    In previous version of please it was called travis; now travis is deprecated

OPTIONS
    -A REGEX, --trace-after REGEX
                        travis stops after executed yaml statement
    -B, --debug         disable log to file in order to debug session
    -C, --no-cache      do not use stored PYPI
    -c FILE, --odoo-config FILE
                        Odoo configuration file
    -D DEBUG_LEVEL, --debug-level DEBUG_LEVEL
                        travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
    -d NAME, --database NAME
    -E, --no-savenv     do not save virtual environment into ~/VME/.. if does not exist
    -e LOCALE, --locale LOCALE
                        use locale
    -f, --full          run final travis with full features
    -k, --keep          keep database after tests
    -H PATH, --home-devel PATH
                        Home devel directory
    -L LINT_LEVEL, --lint-level LINT_LEVEL
                        lint_check_level; may be: minimal,reduced,average,nearby,oca;
                        def value from .travis.yml
    -l FILE, --log FILE log file name
    -m, --missing       show missing line in report coverage after test
    -n, --dry-run       do nothing
    -Q FILE, --tools-config FILE
                        configuration file
    -q, --quiet         silent mode
    -S true|false, --syspkg true|false
                        use python system packages (def yaml dependents)
    -T REGEX, --trace REGEX
                        trace stops before executing yaml statement
    -v, --verbose
    -V, --version       show program's version number and exit
    -X true|false, --translation true|false
                        enable translation test (def yaml dependents)
    -Y PATH, --yaml-file PATH
                        file yaml to process (def .travis.yml)
    -Z, --zero          use local zeroincombenze tools

EXAMPLES
    please z0bug

BUGS
    No known bugs."""
        please = self.please
        please.sh_subcmd = please.pickle_params(cmd_subst="travis")
        if please.is_odoo_pkg():
            params = please.pickle_params(cmd_subst="lint")
            cmd = please.build_sh_me_cmd(params=params)
            sts = please.run_traced(cmd)
            if sts == 0:
                params = please.pickle_params(cmd_subst="test")
                cmd = please.build_sh_me_cmd(params=params)
                sts = please.run_traced(cmd)
            return sts
        return please.do_iter_action(self, act_all_pypi=True, act_tools=False)
