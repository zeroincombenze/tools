# -*- coding: utf-8 -*-
# Copyright (C) 2015-2021 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function, unicode_literals
import os
import os.path
import sys
import subprocess
from string import Template
from subprocess import Popen, PIPE
import shutil
import argparse
import glob
from os0 import os0
import magic


__version__ = "1.0.5"
# Module to test version (if supplied version test is executed)
# REQ_TEST_VERSION = "0.1.4"

# return code
TEST_FAILED = 1
TEST_SUCCESS = 0
if os.name == "posix":
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    CLEAR = "\033[0;m"
else:                                                       # pragma: no cover
    RED = ''
    GREEN = ''
    CLEAR = ''
fail_msg = RED + "Test FAILED!" + CLEAR
success_msg = GREEN + "Test successfully terminated" + CLEAR
# max # of test
MAX_TEST_NUM = 10
# Apply for configuration file (True/False)
APPLY_CONF = False
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = None
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
# Warning: set all LXs with no values -> LX=(), with 1 value -> LX=(value,)
# List of string parameters in [options] of config file
LX_CFG_S = ('opt_debug', 'opt_verbose', 'opt_noctr')
# List of pure boolean parameters in [options] of config file
LX_CFG_B = ('opt_debug', 'python2', 'python3')
# List of string parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_S = ('opt_echo',     'logfn',
                'opt_tjlib',    'opt_oelib',
                'dry_run',      'opt_new',
                'opt_verbose',  'opt_debug',
                'opt_noctr',    'run4cover',
                'max_test',     'min_test',
                'opt_pattern',  'no_run_on_top',
                'qsanity',      'esanity',
                'python2',      'python3')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_B = ('qsanity', 'esanity', 'opt_debug', 'opt_tjlib', 'opt_oelib')
# List of numeric parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_N = ('ctr', 'max_test', 'min_test')
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_CFG_S
LX_SB = ('dry_run',)
#
DEFDCT = {'run4cover': False,
          'opt_debug': False,
          'opt_new': False
          }
#
LX_OPT_ARGS = {'opt_debug': '-B',
               'opt_echo': '-e',
               'opt_tjlib': '-J',
               'logfn': '-l',
               'dry_run': '-n',
               'opt_new': '-N',
               'opt_oelib': '-O',
               'opt_pattern': '-p',
               'run_on_top': '-R',
               'min_test': '-r',
               'opt_verbose': '-v',
               'max_test': '-z',
               'opt_noctr': '-0',
               'run4cover': '-C',
               'python2': '-2',
               'python3': '-3'}

DEFAULT_COVERARC = r"""# Config file .coveragerc 2019-08-22
[run]
include =
#    ${TRAVIS_BUILD_DIR}/*
    *.py

omit =
    */scenario/*
    */scenarios/*
    */test/*
    */tests/*
    *_example/*
    __main__.py
    setup.py
    */site-packages/*
    */lib/python*/*
    */lib64/python*/*
    */__init__.py
    */__openerp__.py
    */__manifest__.py
[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover

    # Don't complain about null context checking
    if context is None:

    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug

    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError

    # Don't complain if non-runnable code isn't run:
    if __name__ == .__main__.:
    if 0:
    if False:

    # Ignore unit test failure
    return TEST_FAILED
"""


class Macro(Template):
    delimiter = '${'
    idpattern = r'[^}]+?}'

    def substitute(self, **kwargs):
        nk = {}
        for k, v in kwargs.items():
            nk[k + '}'] = v
        return super(Macro, self).substitute(**nk)

    def safe_substitute(self, **kwargs):
        nk = {}
        for k, v in kwargs.items():
            nk[k + '}'] = v
        return super(Macro, self).safe_substitute(**nk)


class SanityTest():
    """Auto test for z0testlib
    This class is structured exactly as a target test
    """
    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        """Sanity autotest #1"""
        opts = ['-n']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -n",
                                 True,
                                 ctx['dry_run'])
        if sts == TEST_SUCCESS:
            if os.isatty(0):
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (tty)",
                                         True,
                                         ctx['run_tty'])
            else:                                           # pragma: no cover
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (tty)",
                                         False,
                                         ctx['run_tty'])
        if sts == TEST_SUCCESS:
            if os.isatty(0):
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (daemon)",
                                         False,
                                         ctx['run_daemon'])
            else:                                           # pragma: no cover
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (daemon)",
                                         True,
                                         ctx['run_daemon'])
        if sts == TEST_SUCCESS:
            if os.isatty(0):
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (-e)",
                                         True,
                                         ctx['opt_echo'])
            else:                                           # pragma: no cover
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (-e)",
                                         False,
                                         ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-k)",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-l)",
                                     '~/z0bug.log',
                                     ctx['logfn'])
        ctx = self.Z._ready_opts(ctx)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Counter",
                                     0,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-r)",
                                     0,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-z)",
                                     0,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            if os.environ.get("COVERAGE_PROCESS_START", ""):
                tres = True
            else:                                           # pragma: no cover
                tres = False
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-0)",
                                     tres,
                                     ctx['opt_noctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -B",
                                     0,
                                     ctx['opt_debug'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Run on Top",
                                     True,
                                     ctx['run_on_top'])
        return sts

    def test_02(self, z0ctx):
        """Sanity autotest #2"""
        tlog = "~/dev/z0testlib.log"
        opts = ['-n']
        ctx = self.Z.parseoptest(opts, tlog=tlog)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -n",
                                 True,
                                 ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-k)",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-l)",
                                     tlog,
                                     ctx['logfn'])
        return sts

    def test_03(self, z0ctx):
        """Sanity autotest #3"""
        tlog = "~/dev/z0testlib.log"
        opts = ['-n', '-l', tlog]
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -n",
                                 True,
                                 ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-k)",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-l)",
                                     tlog,
                                     ctx['logfn'])
        return sts

    def test_04(self, z0ctx):
        """Sanity autotest #4"""
        opts = ['-e']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -e",
                                 True,
                                 ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -e (-N)",
                                     True,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -e (-n)",
                                     False,
                                     ctx['dry_run'])
        return sts

    def test_05(self, z0ctx):
        """Sanity autotest #5"""
        opts = ['-q']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -q",
                                 False,
                                 ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -q (-N)",
                                     True,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -q (-n)",
                                     False,
                                     ctx['dry_run'])
        return sts

    def test_06(self, z0ctx):
        """Sanity autotest #6"""
        opts = ['-r0']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -r0",
                                 0,
                                 ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Run on Top",
                                     False,
                                     ctx['run_on_top'])
        if sts == TEST_SUCCESS:
            opts = ['-r', '0']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r 0",
                                     0,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r 0 -N",
                                     True,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-r13']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r13",
                                     13,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r13 -n",
                                     False,
                                     ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -q -N",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-r', '13', '-N']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r 13",
                                     13,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r 13 -N",
                                     True,
                                     ctx['opt_new'])
        return sts

    def test_07(self, z0ctx):
        """Sanity autotest #7"""
        opts = ['-r', '0', '-z', '13']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -r 0",
                                 0,
                                 ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -r 0 -z 13",
                                     13,
                                     ctx['max_test'])
        return sts

    def test_08(self, z0ctx):
        """Sanity autotest #8"""
        opts = []
        ctx = self.Z.parseoptest(opts)
        ctx['WLOGCMD'] = "wecho-0"
        # sts = self.simulate_main(ctx, '1')
        sts = self.Z.main(ctx, UT=['__test_01'])
        # if os.environ.get("COVERAGE_PROCESS_START", ""):
        #     tres = 0
        # else:                                             # pragma: no cover
        tres = 1
        sts = self.Z.test_result(z0ctx,
                                 "UT",
                                 tres,
                                 ctx['max_test'])
        if sts == TEST_SUCCESS:
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '2')
            sts = self.Z.main(ctx, UT=['__test_02'])
            # if os.environ.get("COVERAGE_PROCESS_START", ""):
            #     tres = 0
            # else:                                         # pragma: no cover
            tres = 2
            sts = self.Z.test_result(z0ctx,
                                     "UT",
                                     tres,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            # if os.environ.get("COVERAGE_PROCESS_START", ""):
            #     tres = 0
            # else:                                         # pragma: no cover
            tres = 3
            sts = self.Z.test_result(z0ctx,
                                     "UT",
                                     tres,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -0",
                                     0,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            tres = 3
            sts = self.Z.test_result(z0ctx,
                                     "UT -n",
                                     tres,
                                     ctx['max_test'])
            tres = 3
            sts = self.Z.test_result(z0ctx,
                                     "UT -n",
                                     tres,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-n', '-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -n -0",
                                     0,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            tres = 13
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13",
                                     tres,
                                     ctx['max_test'])
            tres = 3
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13",
                                     tres,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13 -0",
                                     13,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-0', '-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13 -0 -n",
                                     13,
                                     ctx['max_test'])
        return sts


class Z0test(object):
    """The command line program to execute all tests in professional way.
    """

    def version(self):
        return __version__

    def __init__(self, argv=None, id=None, version=None, autorun=False):
        self.autorun = autorun
        this_fqn = None
        if argv is None:
            if len(sys.argv) and not sys.argv[0].startswith('-'):
                argv = sys.argv[1:]
                this_fqn = sys.argv[0]
            else:
                argv = []
        else:
            self.autorun = True
        this_fqn = os.path.abspath(this_fqn or self._get_this_fqn())
        this = os.path.splitext(os.path.basename(this_fqn))[0]
        this_dir = os.getcwd()
        if (not os.path.basename(this_dir) == 'tests' and 
                not os.path.isdir('./tests')):
            this_dir = os.path.dirname(this_fqn)
        self.this_dir = this_dir
        if os.path.basename(this_dir) == 'tests':
            self.testdir = self.this_dir
            self.rundir = os.path.abspath(os.path.join(self.this_dir, '..'))
        else:                                               # pragma: no cover
            if os.path.isdir('./tests'):
                self.testdir = os.path.join(self.this_dir,
                                            'tests')
            else:
                self.testdir = self.this_dir
            self.rundir = self.this_dir
        # Testing package dir must be the 1.st one in sys.path
        this_pkg_dir = os.path.dirname(self.rundir)
        PYTHONPATH = os.environ.get('PYTHONPATH', '')
        if this_pkg_dir not in sys.path:
            if PYTHONPATH:
                p = ':%s:' % PYTHONPATH
                if p.find(':%s:' % this_pkg_dir) < 0:
                    PYTHONPATH = '%s:%s' % (this_pkg_dir, PYTHONPATH)
            else:
                PYTHONPATH = this_pkg_dir
        if this == 'test_zerobug':
            this_pkg_dir = '%s/%s' % (self.rundir, 'dummy')
            PYTHONPATH = '%s:%s' % (this_pkg_dir, PYTHONPATH)
        os.putenv('PYTHONPATH', PYTHONPATH)
        self.PYTHONPATH = PYTHONPATH
        if this_pkg_dir in sys.path:
            ix = sys.path.index(this_pkg_dir)
            del sys.path[ix]
        sys.path.insert(0, this_pkg_dir)

        if not id:
            if this.startswith('test_'):
                id = this[5:]
            elif (this.startswith('all_tests') or
                    this.startswith('zerobug') or
                    this == '__main__'):
                id = os.path.basename(self.rundir)
            else:
                id = this
            if id[-3:] >= '_00' and id[-3:] <= '_99':
                id = id[0:-3]
            if id[-5:] == '_test':
                id = id[0:-5]
        else:
            self.autorun = True
        self.module_id = id
        if this == 'zerobug':
            self.pattern = [self.module_id + '_test*', 'test_*']
        else:
            self.pattern = this
        # If auto regression test is executing
        self.def_tlog_fn = os.path.join(self.testdir,
                                        self.module_id + "_test.log")
        self.ctr_list = []
        if self.autorun:
            self.ctx = self.parseoptest(argv, version=version)
            sys.exit(self.main())

    def _create_parser(self, version, ctx):
        """Standard test option parser; same funcionality of bash version
        -b --debug      run test in debug mode
        -C --no-coverage run test w/o coverage
        -e --echo        set echo
        -h --help        show help
        -f --failfast    RESERVED TO --failfast (stop on first failure)
        -k --keep        keep current logfile
        -J               load travisrc library (only in bash scripts)
        -l --logname     set log filename
        -N --new         create new logfile
        -n --dry-run     count and display # unit tests
        -O               load odoorc library (only in bash scripts)
        -q --quiet       run tests without output (quiet mode)
        -R --run-inner   run test inner mode (no final result)
        -r --restart     restart count next to number
        -s --start       count 1st test next to number (deprecated, use -r)
        -V --version     show version
        -v --verbose     verbose mode
        -x --qsanity     execute silently test library sanity check and exit
        -X --esanity     execute test library sanity check and exit
        -z --end         display total # tests when execute them
        -0 --no-count    no count # unit tests
        -1 --coverage    run test for coverage (obsoslete)
        -2               python2
        -3               python3
        """
        parser = argparse.ArgumentParser(
            description="Regression test on " + self.module_id,
            epilog="© 2015-2021 by SHS-AV s.r.l."
                   " - http://wiki.zeroincombenze.org/en/Zerobug")
        parser.add_argument("-B", "--debug",
                            help="trace msgs in zerobug.tracehis",
                            action="store_true",
                            dest="opt_debug",
                            default=False)
        parser.add_argument("-C", "--no-coverage",
                            help="run tests without coverage",
                            action="store_false",
                            dest="run4cover",
                            default=True)
        parser.add_argument("-e", "--echo",
                            help="enable echoing even if not interactive tty",
                            action="store_true",
                            dest="opt_echo_e",
                            default=False)
        parser.add_argument("-J",
                            help="load travisrc",
                            action="store_true",
                            dest="opt_tjlib",
                            default=False)
        parser.add_argument("-k", "--keep",
                            help="keep current logfile",
                            action="store_false",
                            dest="opt_new_k",
                            default=True)
        parser.add_argument("-l", "--logname",
                            help="set logfile name",
                            dest="logfn",
                            metavar="file")
        parser.add_argument("-N", "--new",
                            help="create new logfile",
                            action="store_true",
                            dest="opt_new_N",
                            default=False)
        parser.add_argument("-n", "--dry-run",
                            help="count and display # unit tests",
                            action="store_true",
                            dest="dry_run",
                            default=False)
        parser.add_argument("-O",
                            help="load odoorc",
                            action="store_true",
                            dest="opt_oelib",
                            default=False)
        parser.add_argument("-p", "--search-pattern",
                            help="test file pattern",
                            dest="opt_pattern",
                            metavar="file_list",
                            default='')
        parser.add_argument("-q", "--quiet",
                            help="run tests without output (quiet mode)",
                            action="store_false",
                            dest="opt_echo_q",
                            default=True)
        parser.add_argument("-R", "--run-inner",
                            help="inner mode w/o final messages",
                            action="store_true",
                            dest="no_run_on_top")
        parser.add_argument("-r", "--restart",
                            help="set to counted tests, 1st one next to this",
                            dest="min_test",
                            metavar="number")
        parser.add_argument("-s", "--start",
                            help="deprecated",
                            dest="min_test2",
                            metavar="number")
        parser.add_argument("-V", "--version",
                            action="version",
                            version=version)
        parser.add_argument("-v", "--verbose",
                            help="verbose mode",
                            action="store_true",
                            dest="opt_verbose",
                            default=ctx['run_tty'])
        parser.add_argument("-x", "--qsanity",
                            help="like -X but run silently",
                            action="store_true",
                            dest="qsanity",
                            default=False)
        parser.add_argument("-X", "--esanity",
                            help="execute test library sanity check and exit",
                            action="store_true",
                            dest="esanity",
                            default=False)
        parser.add_argument("-z", "--end",
                            help="display total # tests when execute them",
                            dest="max_test",
                            metavar="number")
        parser.add_argument("-0", "--no-count",
                            help="no count # unit tests",
                            action="store_true",
                            dest="opt_noctr",
                            default=False)
        parser.add_argument("-1", "--coverage",
                            help="run tests for coverage (obsolete)",
                            action="store_true",
                            dest="run4cover",
                            default=True)
        parser.add_argument("-2", "--python2",
                            help="use python2",
                            action="store_true",
                            dest="python2",
                            default=False)
        parser.add_argument("-3", "--python3",
                            help="use python3",
                            action="store_true",
                            dest="python3",
                            default=False)
        return parser

    def _create_params_dict(self, ctx):
        """Create all params dictionary"""
        ctx = self._create_def_params_dict(ctx)
        if ('min_test' not in ctx or
                ctx.get('min_test', None) is None) and \
                ('max_test' not in ctx or
                 ctx.get('max_test', None) is None):
            if 'run_on_top' not in ctx:
                ctx['run_on_top'] = True
            ctx['min_test'] = 0
            ctx['max_test'] = 0
        else:
            ctx['run_on_top'] = False
            if not ctx.get('min_test', None):
                ctx['min_test'] = 0
            if not ctx.get('max_test', None):
                ctx['max_test'] = 0
        ctx['min_test'] = int(ctx.get('min_test', '0'))
        ctx['max_test'] = int(ctx.get('max_test', '0'))
        if 'opt_echo' not in ctx or ctx['opt_echo'] is None:
            ctx['opt_echo'] = ctx['run_tty']
        if ctx['dry_run']:
            ctx['opt_new'] = False
        elif 'opt_new' not in ctx or ctx['opt_new'] is None:
            if ctx.get('min_test', 0) == 0 or \
                    ctx.get('min_test', 0) is None:
                ctx['opt_new'] = True
            else:
                ctx['opt_new'] = False
        if not ctx['logfn'] or ctx['logfn'] == '':
            if 'tlog' in ctx:
                ctx['logfn'] = ctx['tlog']
            else:
                ctx['logfn'] = "~/" + ctx['this'] + ".log"
        if not ctx.get('WLOGCMD', None) \
                and not ctx.get('_run_autotest', False):
            os0.set_tlog_file(ctx['logfn'],
                              new=ctx['opt_new'],
                              echo=ctx['opt_echo'])
        try:
            subprocess.call(['coverage', '--version'],
                stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
            if os.environ.get("COVERAGE_PROCESS_START", ""):
                ctx['COVERAGE_PROCESS_START'] = \
                    os.environ["COVERAGE_PROCESS_START"]
                ctx['run4cover'] = True
            if ctx['run4cover']:
                if not ctx.get('COVERAGE_PROCESS_START',
                               ''):                       # pragma: no cover
                    ctx['COVERAGE_PROCESS_START'] = os.path.abspath(
                        os.path.join(self.rundir,
                                     '.coveragerc'))
        except OSError:
            ctx['run4cover'] = False
        return ctx

    def _create_def_params_dict(self, ctx):
        """Create default params dictionary"""
        opt_obj = ctx.get('_opt_obj', None)
        conf_obj = ctx.get('_conf_obj', None)
        s = "options"
        if conf_obj:                                        # pragma: no cover
            if not conf_obj.has_section(s):
                conf_obj.add_section(s)
            for p in LX_CFG_S:
                ctx[p] = conf_obj.get(s, p)
            for p in LX_CFG_B:
                ctx[p] = conf_obj.getboolean(s, p)
        else:
            DEFDCT = self.default_conf(ctx)
            for p in LX_CFG_S:
                if p in DEFDCT:
                    ctx[p] = DEFDCT[p]
            for p in LX_CFG_B:
                if p in DEFDCT:
                    ctx[p] = DEFDCT[p]
        if opt_obj:
            for p in LX_OPT_CFG_S:
                if p == 'opt_echo':
                    if hasattr(opt_obj, 'opt_echo_q') and \
                            getattr(opt_obj, 'opt_echo_q') is False:
                        ctx[p] = False
                    elif hasattr(opt_obj, 'opt_echo_e') and \
                            getattr(opt_obj, 'opt_echo_e'):
                        ctx[p] = True
                    else:
                        ctx[p] = None
                elif p == 'opt_new':
                    if hasattr(opt_obj, 'opt_new_k') and \
                            getattr(opt_obj, 'opt_new_k') is False:
                        ctx[p] = False
                    elif hasattr(opt_obj, 'opt_new_N') and \
                            getattr(opt_obj, 'opt_new_N'):
                        ctx[p] = True
                    else:
                        ctx[p] = None
                elif p == 'min_test':
                    if hasattr(opt_obj, 'min_test2') and \
                            getattr(opt_obj, 'min_test2'):
                        ctx[p] = int(getattr(opt_obj, 'min_test2'))
                    else:
                        ctx[p] = None
                elif p == 'no_run_on_top' and hasattr(opt_obj, p):
                    ctx['run_on_top'] = not getattr(opt_obj, p)
                elif hasattr(opt_obj, p):
                    ctx[p] = getattr(opt_obj, p)
            for p in LX_OPT_CFG_B:
                if hasattr(opt_obj, p):
                    ctx[p] = os0.str2bool(getattr(opt_obj, p), None)
            for p in LX_OPT_CFG_N:
                if hasattr(opt_obj, p) and getattr(opt_obj, p):
                    ctx[p] = int(getattr(opt_obj, p))
        for p in LX_SB:
            ctx[p] = os0.str2bool(ctx[p], ctx[p])
        return ctx

    def _get_this_fqn(self):
        # i = 1
        # valid = False
        # auto_this = False
        # this_fqn = False
        # while not valid and i < len(inspect.stack()):
        #     this_fqn = os.path.abspath(inspect.stack()[i][1])
        #     this = os.path.splitext(os.path.basename(this_fqn))[0]
        #     if this[0] == '<' and this[-1] == '>':
        #         i += 1
        #     elif this in ("__init__", "pdb", "cmd", "z0testlib"):
        #         i += 1
        #         if this == "__init__":
        #             auto_this = this_fqn
        #     else:
        #         valid = True
        #         if this in ('pkgutil', 'runpy'):
        #             this_fqn = os.path.dirname(auto_this)
        #             id = 'test_%s.py' % os.path.basename(this_fqn)
        #             this_fqn = os.path.join(this_fqn, id)
        # return this_fqn
        return os.path.abspath(sys.argv[0])

    def parseoptest(self, arguments, version=None, tlog=None):
        ctx = {}
        ctx['os_name'] = os.name
        ctx['rundir'] = self.rundir
        ctx['testdir'] = self.testdir
        this_fqn = self._get_this_fqn()
        ctx['this_fqn'] = this_fqn
        this = os.path.splitext(os.path.basename(this_fqn))[0]
        ctx['this'] = this
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:                                               # pragma: no cover
            ctx['run_daemon'] = True
        ctx['run_tty'] = os.isatty(0)
        if tlog:
            ctx['tlog'] = tlog
        else:
            ctx['tlog'] = self.def_tlog_fn
        # running autotest
        if version is None:
            ctx['_run_autotest'] = True
        parser = self._create_parser(version, ctx)
        ctx['_parser'] = parser
        opt_obj = parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        ctx = self._create_params_dict(ctx)
        if ctx['esanity']:                                  # pragma: no cover
            exit(self.sanity_check('-e'))
        elif ctx['qsanity']:                                # pragma: no cover
            exit(self.sanity_check('-q'))
        return ctx

    def default_conf(self, ctx):
        return DEFDCT

    def _inherit_opts(self, ctx):
        args = ['-R']
        for p in LX_OPT_CFG_S:
            if p == 'opt_echo':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
                else:
                    args.append('-q')
            elif p == 'opt_verbose' or p == 'opt_noctr' or p == 'opt_debug':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'logfn':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p] + ctx[p])
            elif p == 'run4cover':
                if p in ctx and not ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'min_test':
                args.append(LX_OPT_ARGS[p] + str(ctx['ctr']))
            elif not ctx.get('opt_noctr', None) and p == 'max_test':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p] + str(ctx[p]))
        return args

    def _ready_opts(self, ctx):
        if 'max_test' not in ctx or ctx['max_test'] is None:
            ctx['max_test'] = ctx.get('max_test', 0)
        if 'min_test' not in ctx or ctx['min_test'] is None:
            ctx['min_test'] = ctx.get('min_test', 0)
        if 'ctr' not in ctx or ctx['ctr'] is None:
            ctx['ctr'] = ctx.get('ctr', 0)
        ctx['_prior_msg'] = ctx.get('_prior_msg', '')
        return ctx

    def _save_opt(self, ctx, p):
        if p in ctx:
            if ctx.get('_run_autotest', False):
                sp = 'ratsave_' + p
            else:
                sp = 'save_' + p
            ctx[sp] = ctx[p]
        return ctx

    def _save_options(self, ctx):
        for p in ('dry_run', 'min_test', 'ctr'):
            ctx = self._save_opt(ctx, p)
        return ctx

    def _restore_opt(self, ctx, p):
        if ctx.get('_run_autotest', False):
            sp = 'ratsave_' + p
        else:
            sp = 'save_' + p
        if sp in ctx:
            ctx[p] = ctx[sp]
            del ctx[sp]
        elif p in ctx:
            del ctx[p]
        return ctx

    def _restore_options(self, ctx):
        for p in ('dry_run', 'min_test', 'ctr'):
            ctx = self._restore_opt(ctx, p)
        return ctx

    def set_shabang(self, ctx, testfile):
        if (not ctx.get('python3', False) and
                not ctx.get('python2', False) and
                os.path.isfile(testfile)):
            do_rewrite = False
            with open(testfile, 'rb') as fd:
                source = fd.read().decode('utf-8')
                if source.startswith('#!'):
                    do_rewrite = True
                    new_source = '#!%s\n' % sys.executable
                    for ln in source.split('\n')[1:]:
                        new_source += '%s\n' % ln
            if do_rewrite:
                with open(testfile, 'wb') as fd:
                    fd.write(new_source.encode('utf-8'))

    def test_version(self, ctx, testname):
        """testname format is '__version_T_VVVVFILE' where:
            T: type - May be:
                   'V' = exec 'testfile -V'
                   'v' = exec 'testfile -v'
                   'P' = exec 'testfile --version'
                   '1' = use VVVV
                   '0' = use internal value __version__
            VVVV: version - Version to match (must be {0-9.}+)
            FILE: pathfile to execute to match version (macro expanded)
        """
        if ctx['dry_run']:
            ctx['ctr'] = 1
            return TEST_SUCCESS
        tver = testname[10]
        file = ''
        version = ''
        i = 12
        while i < len(testname):
            if testname[i].isdigit() or testname[i] == '.':
                version = version + testname[i]
            else:
                file = Macro(testname[i:])
                file = file.safe_substitute(**ctx)
                break
            i += 1
        msg = "version %s %s" % (os.path.basename(file), version)
        res = ""
        cmd = ""
        if tver == "V":
            cmd = file + " -V"
        elif tver == "v":
            cmd = file + " -v"
        elif tver == "P":
            cmd = file + " --version"
        elif tver == "1":
            cmd = "grep __version__ %s|head -n1|awk -F= '{print $2}'" % file
        elif tver == "0":
            res = __version__
        if cmd:
            os0.muteshell(cmd, keepout=True)
            stdout_fd = open(os0.setlfilename(os0.bgout_fn, 'r'))
            res = stdout_fd.read().strip()
            stdout_fd.close()
            os.remove(os0.bgout_fn)
        return self.test_result(ctx,
                                msg,
                                version,
                                res)

    def doctest(self, ctx, testname):
        """testname format is '__doctest_FILE' where:
        FILE: pathfile to execute doctest (macro expanded)
        """
        if ctx['dry_run']:
            return TEST_SUCCESS
        file = Macro(testname[10:])
        file = file.safe_substitute(**ctx)
        msg = "doctest %s" % os.path.basename(file)
        # cmd = 'sys.executable -m doctest %s' % file
        FNULL = open(os.devnull, 'w')
        res = subprocess.call(['sys.executable', '-m', 'doctest', file],
                              stdout=FNULL,
                              stderr=subprocess.STDOUT)
        return self.test_result(ctx,
                                msg,
                                TEST_SUCCESS,
                                res)

    def _exec_tests_4_count(self, test_list, ctx, TestCls=None):
        if ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, '>>> exec_tests_4_count(autotest)')
        else:
            self.dbgmsg(ctx, '>>> exec_tests_4_count(%s)' % test_list)
        opt4childs = ['-n', '-R']
        ctx = self._ready_opts(ctx)
        ctx = self._save_options(ctx)
        testctr = 0
        if TestCls:
            T = TestCls(self)
            if hasattr(TestCls, 'setup'):
                getattr(T, 'setup')(ctx)
        for testname in test_list:
            self.dbgmsg(ctx,
                        '- min=%d, max=%d, ctr=%d, -0=%s, Cover=%s' %
                        (ctx['min_test'],
                         ctx['max_test'],
                         ctx['ctr'],
                         ctx.get('opt_noctr', False),
                         ctx.get('run4cover', False)))
            ctx['dry_run'] = True
            basetn = os.path.basename(testname)
            ctx['ctr'] = 0
            if testname.startswith('__test'):
                ctx['ctr'] = int(testname[7:9])
            elif testname.startswith('__version'):
                self.test_version(ctx, testname)
            elif testname.startswith('__doctest'):
                self.doctest(ctx, testname)
            elif TestCls and hasattr(TestCls, testname):
                getattr(T, testname)(ctx)
            elif os.path.splitext(basetn)[0] != ctx['this']:
                mime = magic.Magic(
                    mime=True).from_file(os.path.realpath(testname))
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.testdir, testname)
                if mime == 'text/x-python':
                    if ctx.get('python3', False):
                        test_w_args = ['python3'] + [testname] + opt4childs
                    elif ctx.get('python2', False):
                        test_w_args = ['python2'] + [testname] + opt4childs
                    else:
                        test_w_args = [sys.executable] + [testname] + opt4childs
                else:
                    test_w_args = [testname] + opt4childs
                self.dbgmsg(ctx, ">>>  test_w_args=%s" % test_w_args)
                p = Popen(test_w_args,
                          stdin=PIPE,
                          stdout=PIPE,
                          stderr=PIPE)
                res, err = p.communicate()
                try:
                    ctx['ctr'] = int(res)
                except BaseException:                        # pragma: no cover
                    ctx['ctr'] = 0
                self.ctr_list.append(ctx['ctr'])
            self.dbgmsg(ctx, '- testctr=%d+%d' % (testctr, ctx['ctr']))
            testctr += ctx['ctr']
        if TestCls and hasattr(TestCls, 'teardown'):
            getattr(T, 'teardown')(ctx)
        ctx = self._restore_options(ctx)
        ctx['ctr'] = testctr
        if ctx.get('max_test', 0) == 0:
            ctx['max_test'] = ctx.get('min_test', 0) + testctr
        self.dbgmsg(ctx, '- c=%d, min=%d, max=%d' % (ctx['ctr'],
                                                     ctx['min_test'],
                                                     ctx['max_test']))
        ctx['_prior_msg'] = ''
        return TEST_SUCCESS

    def _exec_all_tests(self, test_list, ctx, TestCls=None):
        if ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, '>>> exec_all_tests(autotest)')
        else:
            self.dbgmsg(ctx, '>>> exec_all_tests()')
        ctx = self._ready_opts(ctx)
        if (not ctx.get('_run_autotest', False) and
                ctx.get('run4cover', False and
                not os.path.isfile(ctx['COVERAGE_PROCESS_START']))):
            with open(ctx['COVERAGE_PROCESS_START'], 'w') as fd:
                fd.write(DEFAULT_COVERARC)
        ix = 0
        sts = 0
        ctx['ctr'] = ctx['min_test']
        self.dbgmsg(ctx, '- c=%d, ctr_list=%s' % (ctx['ctr'], self.ctr_list))
        if TestCls:
            T = TestCls(self)
        if TestCls and hasattr(TestCls, 'setup'):
            getattr(T, 'setup')(ctx)
        for testname in test_list:
            self.dbgmsg(ctx,
                        '- min=%d, max=%d, ctr=%d, -0=%s, Cover=%s' %
                        (ctx['min_test'],
                         ctx['max_test'],
                         ctx['ctr'],
                         ctx.get('opt_noctr', False),
                         ctx.get('run4cover', False)))
            opt4childs = self._inherit_opts(ctx)
            basetn = os.path.basename(testname)
            if testname.startswith('__test'):
                sts = self.test_result(ctx,
                                       testname,
                                       True,
                                       True)
            elif testname.startswith('__version'):
                sts = self.test_version(ctx, testname)
            elif testname.startswith('__doctest'):
                self.doctest(ctx, testname)
            elif TestCls and hasattr(TestCls, testname):
                if ctx.get('opt_debug', False):
                    self.dbgmsg(ctx, ">>> %s()" % testname)
                sts = getattr(T, testname)(ctx)
            elif os.path.splitext(basetn)[0] != ctx['this']:
                mime = magic.Magic(
                    mime=True).from_file(os.path.realpath(testname))
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.testdir, testname)
                if mime == 'text/x-python':
                    self.dbgmsg(ctx, '- ctr=%d' % ctx['ctr'])
                    if os.environ.get('TRAVIS_PDB') == 'true':
                        if ctx.get('python3', False):
                            test_w_args = ['python3', '-m', 'pdb', testname
                                           ] + opt4childs
                        elif ctx.get('python2', False):
                            test_w_args = ['python2', '-m', 'pdb', testname
                                           ] + opt4childs
                        else:
                            test_w_args = [sys.executable, '-m', 'pdb', testname
                                           ] + opt4childs
                    elif (ctx.get('run4cover', False) and
                            not ctx.get('dry_run', False)):
                        self.set_shabang(ctx, testname)
                        test_w_args = [
                            'coverage',
                            'run',
                            '-a',
                            '--rcfile=%s' % ctx['COVERAGE_PROCESS_START'],
                            testname
                        ] + opt4childs
                    else:
                        if ctx.get('python3', False):
                            test_w_args = ['python3'] + [testname] + opt4childs
                        elif ctx.get('python2', False):
                            test_w_args = ['python2'] + [testname] + opt4childs
                        else:
                            test_w_args = [sys.executable] + [testname] + opt4childs
                    self.dbgmsg(ctx, ">>> subprocess.call(%s)" % test_w_args)
                    try:
                        sts = subprocess.call(test_w_args)
                    except OSError:
                        sts = 127
                else:
                    self.dbgmsg(ctx, ">>> %s(%s)" % (testname, opt4childs))
                    test_w_args = [testname] + opt4childs
                    try:
                        sts = subprocess.call(test_w_args)
                    except OSError:
                        sts = 127
                if not ctx.get('opt_noctr', False):
                    ctx['ctr'] += self.ctr_list[ix]
                ix += 1
            if sts or ctx.get('teststs', TEST_SUCCESS):      # pragma: no cover
                sts = TEST_FAILED
                break
        ctx['min_test'] = ctx['ctr']
        if TestCls and hasattr(TestCls, 'teardown'):
            getattr(T, 'teardown')(ctx)
        return sts

    def main_local(self, ctx, Test, UT1=None, UT=None):
        """Default main program for local tests"""
        self.dbgmsg(ctx, '>>> main_local(%s)' % Test)
        test_num = 0
        test_list = []
        for i in range(MAX_TEST_NUM):
            tname = "test_{0:02}".format(test_num)
            if hasattr(Test, tname):
                test_list.append(tname)
            test_num += 1
        if not ctx.get('opt_noctr', False):
            self._exec_tests_4_count(test_list, ctx, Test)
        if ctx.get('dry_run', False):
            if not ctx.get('_run_autotest', False):
                print(ctx['max_test'])
            sts = TEST_SUCCESS
        else:
            if not ctx.get('_run_autotest', False):
                os0.set_tlog_file(ctx.get('logfn', None),
                                  new=ctx.get('opt_new', False),
                                  echo=ctx.get('opt_echo', False))
            sts = self._exec_all_tests(test_list, ctx, Test)
        return sts
    #
    # def main_file(self, ctx=None, Test=None, UT1=None, UT=None):
    #     print('Deprecatede method: use main(..)')
    #     self.main(ctx=ctx, Test=Test, UT1=UT1, UT=UT)

    def main(self, ctx=None, Test=None, UT1=None, UT=None):
        """Default main program for test execution
        ctx: context
        Test: test class for internal tests;
              if supplied only internal tests are executed
        UT1: protected Unit Test list (w/o log)
        UT: Unit Test list (if None, search for files)
        """
        if ctx is None:
            ctx = self.ctx
        if (ctx.get('opt_debug', False) and
                ctx.get('run_on_top', False) and
                not ctx.get('_run_autotest', False)):
            self.dbgmsg(ctx, "# Test tree of %s!" % self.module_id)
        self.dbgmsg(ctx, '>>> main()')
        self.dbgmsg(ctx,
                    '- min=%s, max=%s, -0=%s, Cover=%s' %
                    (ctx.get('min_test', None),
                     ctx.get('max_test', None),
                     ctx.get('opt_noctr', False),
                     ctx.get('run4cover', False)))
        # Execute sanity check on test library (no if zerobug testing itself)
        if (ctx['this'] != 'test_zerobug' and
                ctx.get('run_on_top', False) and
                not ctx.get('_run_autotest', False)):
            if (ctx.get('run4cover', False) and
                    not ctx.get('dry_run', False)):
                try:
                    subprocess.call(['coverage', 'erase'],
                                    stdout=open('/dev/null', 'w'),
                                    stderr=open('/dev/null', 'w'))
                except OSError:
                    print('Coverage not found!')
                    ctx['run4cover'] = False
        test_list = []
        if UT is not None and isinstance(UT, list):
            self.dbgmsg(ctx, '>>> test_list=%s' % UT)
            test_list = UT
        elif not ctx.get('_run_autotest', False):
            # Discover test files
            test_list = []
            for pattern in ctx['opt_pattern'] and ctx['opt_pattern'].split(
                    ',') or self.pattern:
                self.dbgmsg(ctx, '- Search for files %s' % pattern)
                test_files = os.path.abspath(
                    os.path.join(self.testdir, pattern))
                for fn in sorted(glob.glob(test_files)):
                    mime = magic.Magic(
                        mime=True).from_file(os.path.realpath(fn))
                    if mime in ('text/x-python', 'text/x-shellscript'):
                        test_list.append(fn)
        if len(test_list) == 0 and Test is not None:
            self.dbgmsg(ctx, '- len(test_list) == 0 ')
            test_num = 0
            for i in range(MAX_TEST_NUM):
                tname = "test_{0:02}".format(test_num)
                if hasattr(Test, tname):
                    test_list.append(tname)
                test_num += 1
        self.dbgmsg(ctx, '- test_list=%s' % test_list)
        if not ctx.get('opt_noctr', False):
            self._exec_tests_4_count(test_list, ctx, Test)
        if ctx.get('dry_run', False):
            if not ctx.get('_run_autotest', False):
                print(ctx['ctr'])
            sts = TEST_SUCCESS
        else:
            if not ctx.get('_run_autotest', False):
                os0.set_tlog_file(ctx.get('logfn', None),
                                  new=ctx.get('opt_new', False),
                                  echo=ctx.get('opt_echo', False))
            sts = self._exec_all_tests(test_list, ctx, Test)
            if (ctx.get('run_on_top', False) and
                    not ctx.get('_run_autotest', False)):
                if sts == TEST_SUCCESS:
                    print(success_msg)
                else:
                    print(fail_msg)
        return sts

    def dbgmsg(self, ctx, msg, echo=None):
        if ctx.get('opt_debug', False):
            fmode = 'w' if msg[0] == "!" else 'a'
            with open(os.path.join(
                    self.testdir, 'z0bug.tracehis'), fmode) as fd:
                fd.write("%s> %s\n" % (os.path.basename(ctx['this_fqn']), msg))
        if echo:
            print('#DEBUG>>> %s' % msg)

    def msg_test(self, ctx, msg):
        # ctx = self.ready_opts(ctx)
        if msg == ctx['_prior_msg']:
            # NEWLN = False
            prfx = "\x1b[A"
        else:
            # NEWLN = True
            prfx = ""
            ctx['_prior_msg'] = msg
        if not ctx.get('dry_run', False):
            if ctx.get('WLOGCMD', None):
                if ctx['WLOGCMD'] == "echo" or ctx['WLOGCMD'] == "wecho-1":
                    if not ctx.get('opt_noctr', None):
                        print("%sTest %d/%d: %s" % (prfx,
                                                    ctx['ctr'],
                                                    ctx['max_test'],
                                                    msg))
                    else:
                        print("%sTest %d: %s" % (prfx,
                                                 ctx['ctr'],
                                                 msg))
            else:
                if not ctx.get('opt_noctr', None):
                    txt = "{0}Test {1}/{2}: {3}".format(prfx,
                                                        ctx['ctr'],
                                                        ctx['max_test'],
                                                        msg)
                else:
                    txt = "{0}Test {1}: {2}".format(prfx,
                                                    ctx['ctr'],
                                                    msg)
                os0.wlog(txt)

    def test_result(self, ctx, msg, test_value, result_val):
        ctx = self._ready_opts(ctx)
        ctx['ctr'] += 1
        if ctx.get('teststs', TEST_SUCCESS):                 # pragma: no cover
            return TEST_FAILED
        self.msg_test(ctx, msg)
        if not ctx.get('dry_run', False):
            if test_value != result_val:                     # pragma: no cover
                print("Test '%s' failed: expected '%s', found '%s'" %
                      (msg,
                       test_value,
                       result_val))
                ctx['teststs'] = TEST_FAILED
                if ctx.get('on_error', '') != 'continue':
                    raise AssertionError
                else:
                    return TEST_FAILED
        return TEST_SUCCESS

    def _init_test_ctx(self, opt_echo, full=None):
        """Set context value for autotest"""
        z0ctx = {}
        if full:                                            # just for tests
            for p in 'min_test', 'max_test', 'opt_debug', 'opt_noctr', \
                     'dry_run':
                if p in full:
                    z0ctx[p] = full[p]
        if opt_echo == '-e':
            z0ctx['WLOGCMD'] = 'echo'
        elif opt_echo == '-q':
            z0ctx['WLOGCMD'] = 'wecho-0'
        z0ctx['this'] = self.module_id
        z0ctx['this_fqn'] = './' + self.module_id
        z0ctx['_run_autotest'] = True
        self.def_tlog_fn = '~/z0bug.log'
        return z0ctx

    def sanity_check(self, opt_echo, full=None):
        """Internal regression test
        Module z0testlib is needed to run regression tests
        This function run auto validation tests for z0testlib functions
        """
        z0ctx = self._init_test_ctx(opt_echo, full)
        sts = self.main(z0ctx, SanityTest)
        if full:
            for p in 'min_test', 'max_test', 'ctr':
                full[p] = z0ctx[p]
        del z0ctx
        return sts

    def build_os_tree(self, ctx, os_tree):
        """Create a filesytem tree to test
        """
        root = os.path.join(
            os.path.dirname(ctx.get('this_fqn', './Z0BUG/tests')), 'res')
        if not os.path.isdir(root):
            os.mkdir(root)
        if not isinstance(os_tree, (list, tuple)):
            os_tree = [os_tree]
        for path in os_tree:
            if path[0] not in ('~', '/') and not path.startswith('./'):
                path = os.path.join(root, path)
            if not os.path.isdir(path):
                os.makedirs(path)
        return root
 
    def remove_os_tree(self, ctx, os_tree):
        """Remove a filesytem tree created to test"""
        root = os.path.join(os.path.dirname(ctx['this_fqn']), 'res')
        if not os.path.isdir(root):
            return
        if not isinstance(os_tree, (list, tuple)):
            os_tree = [os_tree]
        for path in os_tree:
            if path[0] not in ('.', '/'):
                path = os.path.join(root, path)
            if not os.path.isdir(path):
                continue
            shutil.rmtree(path, ignore_errors=True)


class Z0testOdoo(object):

    def __init__(self, argv=None):
        this_fqn = None
        if not argv and len(sys.argv) and not sys.argv[0].startswith('-'):
            this_fqn = sys.argv[0]
            this_fqn = os.path.abspath(this_fqn)
        this_dir = os.getcwd()
        if (not os.path.basename(this_dir) == 'tests' and
                not os.path.isdir('./tests')):
            this_dir = os.path.dirname(this_fqn)
        self.this_dir = this_dir
        if os.path.basename(this_dir) == 'tests':
            self.testdir = self.this_dir
            self.rundir = os.path.abspath(os.path.join(self.this_dir, '..'))
        else:                                               # pragma: no cover
            if os.path.isdir('./tests'):
                self.testdir = os.path.join(self.this_dir,
                                            'tests')
            else:
                self.testdir = self.this_dir
            self.rundir = self.this_dir

    def get_outer_dir(self):
        """Get dir out of current virtual environment
        In local tests it serves to find local Odoo repositories to avoid
        git clone or wget from web.
        """
        outer_dir = os.environ.get('TRAVIS_BUILD_DIR', os.getcwd())
        if os.path.basename(outer_dir) == 'tests':
            outer_dir = os.path.abspath(
                os.path.join(outer_dir, '..', '..', '..', '..'))
        else:
            outer_dir = os.path.abspath(
                os.path.join(outer_dir, '..', '..', '..'))
        return outer_dir

    def get_local_odoo_path(self, git_org, reponame, branch, home=None):
        outer_dir = home or self.get_outer_dir()
        majver = branch.split('.')[0]
        found_path = False
        for reporg in (reponame, reponame.lower(), git_org, git_org.lower()):
            if found_path:
                break
            for odoo_ver in (branch, majver):
                if found_path:
                    break
                src_repo_path = os.path.join(
                    outer_dir, '%s%s' % (reporg, odoo_ver))
                if os.path.isdir(src_repo_path):
                    found_path = True
                    break
                src_repo_path = os.path.join(
                    outer_dir, '%s-%s' % (reporg, odoo_ver))
                if os.path.isdir(src_repo_path):
                    found_path = True
                    break
                if reponame == 'OCB':
                    continue
                for nm in ('', 'extra', 'private-addons', 'powerp'):
                    if nm:
                        src_repo_path = os.path.join(
                            outer_dir, odoo_ver, nm, reporg)
                    else:
                        src_repo_path = os.path.join(outer_dir, odoo_ver, reporg)
                    if os.path.isdir(src_repo_path):
                        found_path = True
                        break
        if not found_path:
            # Local dir of current project is like '~/12.0'
            src_repo_path = os.path.join(outer_dir, branch)
            if not os.path.isdir(src_repo_path):
                src_repo_path = False
        return src_repo_path

    def build_odoo_env(self, ctx, version,
                       hierarchy=None, name=None, retodoodir=None):
        """Build a simplified Odoo directory tree
        version: 15.0, 14.0, 13.0, ..., 7.0, 6.1
        name: name of odoo dir (default equal to version)
        hierarchy: flat,tree,server (def=flat)
        """
        name = name or version
        if version in ('10.0', '11.0', '12.0', '13.0', '14.0', '15.0'):
            if hierarchy == 'tree':
                odoo_home = os.path.join(name, 'odoo', 'odoo')
            else:
                odoo_home = os.path.join(name, 'odoo')
            script = 'odoo-bin'
        elif version in ('6.1', '7.0', '8.0', '9.0'):
            if hierarchy == 'server':
                odoo_home = os.path.join(name, 'server', 'openerp')
            else:
                odoo_home = os.path.join(name, 'openerp')
            script = 'openerp-server'
        else:
            raise KeyError('Invalid Odoo version')
        os_tree = [name,
                   os.path.join(name, 'addons'),
                   odoo_home,
                   os.path.join(odoo_home, 'addons'),
                   os.path.join(name, '.git'),
                   ]
        root = Z0test().build_os_tree(ctx, os_tree)
        RELEASE_PY = '''
RELEASE_LEVELS = [ALPHA, BETA, RELEASE_CANDIDATE, FINAL] = ['alpha', 'beta', 'candidate', 'final']
RELEASE_LEVELS_DISPLAY = {ALPHA: ALPHA,
                          BETA: BETA,
                          RELEASE_CANDIDATE: 'rc',
                          FINAL: ''}
version_info = (%s, %s, 0, 'final', 0, '')
version = '.'.join(map(str, version_info[:2])) + RELEASE_LEVELS_DISPLAY[version_info[3]] + str(version_info[4] or '') + version_info[5]
series = serie = major_version = '.'.join(map(str, version_info[:2]))'''
        if name[0] not in ('~', '/') and not name.startswith('./'):
            odoo_root = os.path.join(root, name)
        else:
            odoo_root = name
        odoo_home = os.path.join(os.path.dirname(odoo_root), odoo_home)
        with open(os.path.join(odoo_home, 'release.py'), 'w') as fd:
            versions = version.split('.')
            fd.write(RELEASE_PY % (versions[0], versions[1]))
        with open(os.path.join(odoo_home, '__init__.py'), 'w') as fd:
            fd.write('import release\n')
        with open(os.path.join(odoo_root, script), 'w') as fd:
            fd.write('\n')
        with open(os.path.join(odoo_root, '.travis.yml'), 'w') as fd:
            fd.write('\n')
        with open(os.path.join(odoo_root, 'README.rst'), 'w') as fd:
            fd.write('\n')
        if retodoodir:
            return odoo_root
        return root

    def create_repo(self, ctx, root, reponame, version,
                    hierarchy=None, name=None, repotype=None):
        REPOTYPES = {
            'oca': {
                'd': ['.git',],
                'f': ['README.md', '.travis.yml'],
            },
            'zero': {
                'd': ['egg-info', '.git'],
                'f': ['README.rst', '.travis.yml'],
            },
        }
        name = name or version
        repotype = repotype or 'oca'
        odoo_root = os.path.join(root, name)
        if not os.path.isdir(odoo_root):
            odoo_root = root
        repodir = os.path.join(odoo_root, reponame)
        if not os.path.isdir(repodir):
            os.mkdir(repodir)
        for ldir in REPOTYPES.get(repotype, {}).get('d', []):
            path = os.path.join(repodir, ldir)
            if not os.path.isdir(path):
                os.mkdir(path)
        for fn in REPOTYPES.get(repotype, {}).get('f', []):
            path = os.path.join(repodir, fn)
            if not os.path.isfile(path):
                open(path, 'w').close()
        return repodir

    def create_module(self, ctx, repo_root, name, version, moduletype=None):
        MODULETYPES = {
            'simple': {
                'd': [],
                'f': ['__init__.py'],
            },
        }
        moduletype = moduletype or 'simple'
        moduledir = os.path.join(repo_root, name)
        if not os.path.isdir(moduledir):
            os.mkdir(moduledir)
        majver = int(version.split('.')[0])
        if majver < 10:
            ffn = os.path.join(moduledir, '__openerp__.py')
        else:
            ffn = os.path.join(moduledir, '__manifest__.py')
        with open(ffn, 'w') as fd:
            fd.write(str({
                'name': name,
                'version': version,
                'summary': 'This module is a fake, just for test!',
            }))
        for ldir in MODULETYPES.get(moduletype, {}).get('d', []):
            path = os.path.join(moduledir, ldir)
            if not os.path.isdir(path):
                os.mkdir(path)
        for fn in MODULETYPES.get(moduletype, {}).get('f', []):
            path = os.path.join(moduledir, fn)
            if not os.path.isfile(path):
                open(path, 'w').close()
        return moduledir

    def real_git_clone(self, remote, reponame, branch, odoo_path):
        odoo_url = 'https://github.com/%s/%s.git' % (remote, reponame)
        os.system('git clone --depth=50 %s -b %s %s' % (
            odoo_url, branch, odoo_path))
        os.system(
            'git --work-tree=%s --git-dir=%s/.git remote rename origin %s' % (
                odoo_path, odoo_path, remote))

    def git_clone(self, remote, reponame, branch, odoo_path, force=None):
        if force or os.environ.get('TRAVIS') == 'true':
            self.real_git_clone(remote, reponame, branch, odoo_path)
        elif not os.path.isdir(odoo_path):
            src_repo_path = self.get_local_odoo_path(remote, reponame, branch)
            if not os.path.isdir(src_repo_path):
                self.real_git_clone(remote, reponame, branch, odoo_path)
            elif reponame == 'OCB':
                for nm in ('addons', 'odoo', 'openerp'):
                    src_path = os.path.join(src_repo_path, nm)
                    dst_path = os.path.join(odoo_path, nm)
                    if os.path.isdir(src_path):
                        shutil.copytree(
                            src_path, dst_path,
                            symlinks=True,
                            ignore=shutil.ignore_patterns(
                                '*.pyc', '.idea/', 'setup/'))
                for nm in ('.travis.yml', 'odoo-bin', 'openerp-server',
                           'openerp-wsgi.py', 'requirements.txt'):
                    src_path = os.path.join(src_repo_path, nm)
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, odoo_path)
            else:
                shutil.copytree(
                    src_repo_path, os.path.join(odoo_path, reponame),
                    symlinks=True,
                    ignore=shutil.ignore_patterns('*.pyc', '.idea/', 'setup/'))