# -*- coding: utf-8 -*-
#
#
#    Copyright (C) SHS-AV s.r.l. (http://www.shs-av.com/)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
"""@mainpage
Zeroincombenze® continuous testing framework with tools for python programs
===========================================================================

This library can run unit test of target package software.
Supported languages are *python* (through z0testlib.py)
and *bash* (through z0testrc)

*zerobug* supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
The *zerobug* module provides all code that make it easy to support testing
both for python programs both for bash scripts.
*zerobug* differs from pytest standard library because show execution test with
a message like "n/tot message" where *n* is current unit test and *tot* is the
total unit test to execute, that is a sort of advancing test progress.

*zerobug* is built on follow concepts:

-# test main - it is a main program to executes all test runners
-# test runner - it is a programm to executes one or more test suites
-# test suite - it is a collection of test cases
-# test case -it is a smallest unit test

Test main file (usually is called 'all_tests') execute the test suite declared
in source file. If no test list declared, it searches for test runner files
named 'test_[0-9]*' executed in sorted order.
This behavior differs slightly from pytest standard library.

Test suite is a collection of test case named 'test_[0-9]*'
executed in sorted order. Also this behavior differs from
pytest standard library.

Because *zerobug* can show total number of unit test to execute, it run tests
in 2 passes. In the first pass it counts test, in second pass executes really
it.

Every unit test file may be called with follows switches:

    $ unit_test [-hek][-l file][-Nnq][-s number][-Vv][-z number][-0]
    where:
    -h             this help
    -e             enable echoing even if not interactive tty
    -f             RESERVED TO --failfast (stop on first failure)
    -k             keep current logfile
    -l file        set logfile name
    -N             create new logfile
    -n             count and display # unit tests (do no test, return success)
    -q             run tests in quiet mode (no echo)
    -r number      run tests counting 1st test next to number
    -s number      run tests counting 1st test next to number (deprecated, MUST BECOME -r)
    -V             show version (do no test, return success);
                   version on unit test should be the same of tested software
    -v             verbose mode
    -x             execute silently library sanity check and exit [no bash]
    -X             execute library sanity check and exit [no bash]
    -z number      display total # tests when execute them
    -0             no count # unit tests
    -1             run test for coverage
    (w/o switches) do run test and return test result


Package, test environment and deployment are:

    ./                  Package directory
                        inside python test program is self.pkg_dir
                        inside bash test script is $RUNDIR
    ./tests             Unit test directory
                        should contains one of 'all_tests' or 'test_PKGNAME'
                        inside python test program is self.test_dir
                        inside bash test script is $TESTDIR
    ./tests/z0testlib   Python file unit test library from zerobug package
                        may be not present if zerobug python package installed
    ./tests/z0testrc    Bash file unit test library from zerobug package
                        may be not present if zerobug python package installed
                        inside bash test script is $Z0TLIBDIR
    ./tests/z0librc     Local bash script library for bash scripts;
                        Could be in user root directory or in /etc directory
                        inside bash test script is $Z0LIBDIR
    ./_travis           Interface to travis emulator if present;
                        it used in local host to emualte some travis functions
                        inside bash test script is $TRAVISDIR

Unit test can run in package directory or in ./tests directory of package.


Every test can inquire internal context.

    this_fqn      parent caller full qualified name (i.e. /opt/odoo/z0bug.pyc)
    this          parent name, w/o extension (i.e. z0bug)
    ctr;          test counter [both bash and python tests]
    dry_run       dry-run (do nothing) [opt_dry_run in bash test]          "-n"
    esanity       True if required sanity check with echo                  "-X"
    max_test      # of tests to execute [both bash and python tests]       "-z"
    min_test      # of test executed before this one                       "-r"
    on_error      behavior after error, 'continue' or 'raise' (default)
    opt_echo      True if echo test result onto std output                 "-e"
    opt_new       new log file [both bash and python tests]                "-N"
    opt_noctr     do not count # tests [both bash and python tests]        "-0"
    opt_verbose   show messages during execution                           "-v"
    logfn         real trace log file name from switch                     "-l"
    qsanity       True if required sanity check w/o echo                   "-x"
    run4cover     Run tests for coverage (use coverage run rather python)  "-1"
    run_daemon    True if execution w/o tty as stdio
    run_on_top    Top test (not parent)
    run_tty       Opposite of run_daemon
    tlog          default tracelog file name
    _run_autotest True if running auto-test
    _parser       parser
    _opt_obj      parser obj, to acquire optional switches
    WLOGCMD       override opt_echo; may be None, 'echo', 'echo-1', 'echo-0'
    Z0            this library object

Environment read:

DEV_ENVIRONMENT Name of package; if set test is under travis emulator control

COVERAGE_PROCESS_START
                Name of coverage conf file; if set test is running for coverage
"""

# import pdb
import os
import os.path
import sys
import subprocess
from subprocess import Popen, PIPE
# import logging
import argparse
import inspect
import glob
from os0 import os0
# import coverage.plugin


# Z0test library version
__version__ = "0.2.11"
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
LX_CFG_B = ('opt_debug', )
# List of string parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_S = ('opt_echo',     'logfn',
                'opt_tjlib',    'opt_oelib',
                'dry_run',      'opt_new',
                'opt_verbose',  'opt_debug',
                'opt_noctr',    'run4cover',
                'max_test',     'min_test')
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
          'opt_new': False}
#
LX_OPT_ARGS = {'opt_debug': '-b',
               'opt_echo': '-e',
               'opt_tjlib': '-J',
               'logfn': '-l',
               'dry_run': '-n',
               'opt_new': '-N',
               'opt_oelib': '-O',
               'min_test': '-r',
               'opt_verbose': '-v',
               'max_test': '-z',
               'opt_noctr': '-0',
               'run4cover': '-1'}
#
#
# class ZeroBugPlugin(coverage.plugin.CoveragePlugin):
#
#     def file_tracer(self, filename):
#         fd = open('./coverage.z0bug', 'a')
#         fd.write("%s\n" % filename)
#         fd.close()
#         print "<<<<<%s>>>>>" % filename
#         # return FileTracer(filename)
#
#
# class FileTracer(coverage.plugin.FileTracer):
#
#     def __init__(self, filename):
#         pass


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
        ctx = self.Z.ready_opts(ctx)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Counter",
                                     0,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-s)",
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
                                     "Opt -b",
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
        opts = ['-s0']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -s0",
                                 0,
                                 ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Run on Top",
                                     False,
                                     ctx['run_on_top'])
        if sts == TEST_SUCCESS:
            opts = ['-s', '0']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 0",
                                     0,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 0 -N",
                                     True,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-s13']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s13",
                                     13,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s13 -n",
                                     False,
                                     ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -q -N",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-s', '13', '-N']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 13",
                                     13,
                                     ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 13 -N",
                                     True,
                                     ctx['opt_new'])
        return sts

    def test_07(self, z0ctx):
        """Sanity autotest #7"""
        opts = ['-s', '0', '-z', '13']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -s 0",
                                 0,
                                 ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 0 -z 13",
                                     13,
                                     ctx['max_test'])
        return sts

    def test_08(self, z0ctx):
        """Sanity autotest #8"""
        opts = []
        ctx = self.Z.parseoptest(opts)
        ctx['WLOGCMD'] = "wecho-0"
        # sts = self.simulate_main(ctx, '1')
        sts = self.Z.main_file(ctx, UT=['__test_01'])
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
            sts = self.Z.main_file(ctx, UT=['__test_02'])
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
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
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
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -0",
                                     3,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
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
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -n -0",
                                     3,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
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
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13 -0",
                                     13,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-0', '-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            # sts = self.simulate_main(ctx, '3')
            sts = self.Z.main_file(ctx, UT=['__test_01', '__test_02'])
            sts = self.Z.test_result(z0ctx,
                                     "UT -z13 -0 -n",
                                     13,
                                     ctx['max_test'])
        return sts


class Z0test(object):
    """The command line program to execute all tests in professional way.
    """

    def __init__(self, argv=None, id=None, version=None, autorun=False):
        self.autorun = autorun
        this_fqn = self.get_this_fqn()
        if argv is None:
            argv = sys.argv[1:]
            if len(sys.argv) > 0:
                this_fqn = sys.argv[0]
        else:
            self.autorun = True
        this_fqn = os.path.abspath(this_fqn)
        this = os0.nakedname(os.path.basename(this_fqn))
        this_dir = os.path.dirname(this_fqn)
        self.this_dir = this_dir
        if os.path.basename(this_dir) == 'tests':
            self.test_dir = self.this_dir
            self.pkg_dir = os.path.abspath(self.this_dir + '/..')
        else:                                               # pragma: no cover
            if os.path.isdir('.tests'):
                self.test_dir = os.path.join(self.this_dir,
                                             'tests')
            else:
                self.test_dir = self.this_dir
            self.pkg_dir = self.this_dir
        x = os.path.dirname(self.pkg_dir)
        PYTHONPATH = os.environ['PYTHONPATH']
        if x not in sys.path:
            p = ':%s:' % PYTHONPATH
            if p.find(':%s:' % x) < 0:
                PYTHONPATH = '%s:%s' % (x, PYTHONPATH)
        if this == 'test_zerobug':
            x = '%s/%s' % (self.pkg_dir, 'dummy')
            PYTHONPATH = '%s:%s' % (x, PYTHONPATH)
        os.putenv('PYTHONPATH', PYTHONPATH)
        self.PYTHONPATH = PYTHONPATH
        if not id:
            if this[0:5] == 'test_':
                id = this[5:]
            elif this[0:5] == 'all_tests':
                id = os.path.basename(self.pkg_dir)
            else:
                id = this
            if id[-3:] >= '_00' and id[-3:] <= '_99':
                id = id[0:-3]
            if id[-5:] == '_test':
                id = id[0:-5]
        else:
            self.autorun = True
        self.module_id = id
        self.pattern = self.module_id + "_test*"
        # If auto regression test is executing
        self.def_tlog_fn = os.path.join(self.test_dir,
                                        self.module_id + "_test.log")
        self.ctr_list = []
        if self.autorun:
            self.ctx = self.parseoptest(argv,
                                        version=version)
            sts = self.main_file()
            sys.exit(sts)

    def create_parser(self, version, ctx):
        """Standard test option parser; same funcionality of bash version
        -b --debug      run test in debug mode
        -e --echo       set echo
        -h --help       show help
        -f --failfast   RESERVED TO --failfast (stop on first failure)
        -k --keep       keep current logfile
        -J              load travisrc library (only in bash scripts)
        -l --logname    set log filename
        -N --new        create new logfile
        -n --dry-run    count and display # unit tests
        -O              load odoorc library (only in bash scripts)
        -q --quiet      run tests without output (quiet mode)
        -r --restart    restart count next to number
        -s --start      count 1st test next to number (deprecated MUST BECOME -r)
        -V --version    show version
        -v --verbose    verbose mode
        -x --qsanity    execute silently test library sanity check and exit
        -X --esanity    execute test library sanity check and exit
        -z --end        display total # tests when execute them
        -0 --no-count   no count # unit tests
        -1 --coverage   run test for coverage
        """
        parser = argparse.ArgumentParser(
            description="Regression test on " + self.module_id,
            epilog="© 2015-2018 by SHS-AV s.r.l."
                   " - http://wiki.zeroincombenze.org/en/Zerobug")
        parser.add_argument("-b", "--debug",
                            help="run tests in debug mode",
                            action="store_true",
                            dest="opt_debug",
                            default=False)
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
        parser.add_argument("-q", "--quiet",
                            help="run tests without output (quiet mode)",
                            action="store_false",
                            dest="opt_echo_q",
                            default=True)
        parser.add_argument("-r", "--restart",
                            help="set to counted tests, 1st one next to this",
                            dest="min_test",
                            metavar="number")
        parser.add_argument("-s", "--start",
                            help="set to counted tests, 1st one next to this",
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
                            help="run tests for coverage",
                            action="store_true",
                            dest="run4cover",
                            default=False)
        return parser

    def create_params_dict(self, ctx):
        """Create all params dictionary"""
        ctx = self.create_def_params_dict(ctx)
        if ('min_test' not in ctx or
                ctx.get('min_test', None) is None) and \
                ('max_test' not in ctx or
                 ctx.get('max_test', None) is None):
            ctx['run_on_top'] = True
            del ctx['min_test']
            del ctx['max_test']
        else:
            ctx['run_on_top'] = False
            if not ctx.get('min_test', None):
                ctx['min_test'] = 0
            if not ctx.get('max_test', None):
                ctx['max_test'] = 0
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
        if os.environ.get("COVERAGE_PROCESS_START", ""):
            ctx['COVERAGE_PROCESS_START'] = \
                os.environ["COVERAGE_PROCESS_START"]
            ctx['run4cover'] = True
        if ctx['run4cover']:
            ctx['opt_noctr'] = True
            if not ctx.get('COVERAGE_PROCESS_START', ''):   # pragma: no cover
                ctx['COVERAGE_PROCESS_START'] = os.path.abspath(
                    os.path.join(self.pkg_dir,
                                 '.coveragerc'))
        return ctx

    def create_def_params_dict(self, ctx):
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

    def get_this_fqn(self):
        i = 1
        valid = False
        while not valid:
            this_fqn = os.path.abspath(inspect.stack()[i][1])
            this = os0.nakedname(os.path.basename(this_fqn))
            if this in ("__init__", "pdb", "cmd", "z0testlib"):
                i += 1
            else:
                valid = True
        return this_fqn

    def parseoptest(self, arguments, version=None, tlog=None):
        ctx = {}
        this_fqn = self.get_this_fqn()
        ctx['this_fqn'] = this_fqn
        this = os0.nakedname(os.path.basename(this_fqn))
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
        parser = self.create_parser(version, ctx)
        ctx['_parser'] = parser
        opt_obj = parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        ctx = self.create_params_dict(ctx)
        if ctx['esanity']:                                  # pragma: no cover
            exit(self.sanity_check('-e'))
        elif ctx['qsanity']:                                # pragma: no cover
            exit(self.sanity_check('-q'))
        return ctx

    def default_conf(self, ctx):
        return DEFDCT

    def inherit_opts(self, ctx):
        args = []
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
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'min_test':
                args.append(LX_OPT_ARGS[p] + str(ctx['ctr']))
            elif not ctx.get('opt_noctr', None) and p == 'max_test':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p] + str(ctx[p]))
        return args

    def ready_opts(self, ctx):
        if 'max_test' not in ctx or ctx['max_test'] is None:
            ctx['max_test'] = ctx.get('max_test', 0)
        if 'min_test' not in ctx or ctx['min_test'] is None:
            ctx['min_test'] = ctx.get('min_test', 0)
        if 'ctr' not in ctx or ctx['ctr'] is None:
            ctx['ctr'] = ctx.get('ctr', 0)
        ctx['_prior_msg'] = ctx.get('_prior_msg', '')
        return ctx

    def save_opt(self, ctx, p):
        if p in ctx:
            if ctx.get('_run_autotest', False):
                sp = 'ratsave_' + p
            else:
                sp = 'save_' + p
            ctx[sp] = ctx[p]
        return ctx

    def save_options(self, ctx):
        for p in ('dry_run', 'min_test', 'ctr'):
            ctx = self.save_opt(ctx, p)
        return ctx

    def restore_opt(self, ctx, p):
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

    def restore_options(self, ctx):
        for p in ('dry_run', 'min_test', 'ctr'):
            ctx = self.restore_opt(ctx, p)
        return ctx

    def test_version(self, ctx, version, tver, file):
        if ctx['dry_run']:
            ctx['ctr'] = 1
            return TEST_SUCCESS
        x = os.path.basename(file)
        msg = "version %s" % x
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

    def exec_tests_4_count(self, test_list, ctx, TestCls=None):
        if ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, '.exec_tests_4_count (autotest)')
        else:
            self.dbgmsg(ctx, '.exec_tests_4_count')
        opt4childs = ['-n']
        ctx = self.ready_opts(ctx)
        ctx = self.save_options(ctx)
        # self.actrs = []
        testctr = 0
        if TestCls:
            T = TestCls(self)
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
            if testname[0:6] == '__test':
                # ctx['dry_run'] = True
                ctx['ctr'] = int(testname[7:9])
            elif testname[0:9] == '__version':
                self.test_version(ctx, "", "", "")
            elif TestCls and hasattr(TestCls, testname):
                getattr(T, testname)(ctx)
            elif os0.nakedname(basetn) != ctx['this']:
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.test_dir, testname)
                if basetn.endswith('.py'):
                    test_w_args = ['python'] + [testname] + opt4childs
                else:
                    test_w_args = [testname] + opt4childs
                self.dbgmsg(ctx, " %s" % test_w_args)
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
        ctx = self.restore_options(ctx)
        ctx['ctr'] = testctr
        if ctx.get('max_test', 0) == 0:
            ctx['max_test'] = ctx.get('min_test', 0) + testctr
        self.dbgmsg(ctx, '- c=%d, min=%d, max=%d' % (ctx['ctr'],
                                                     ctx['min_test'],
                                                     ctx['max_test']))
        ctx['_prior_msg'] = ''
        return TEST_SUCCESS

    def exec_all_tests(self, test_list, ctx, TestCls=None):
        if ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, '.exec_all_tests (autotest)')
        else:
            self.dbgmsg(ctx, '.exec_all_tests')
        ctx = self.ready_opts(ctx)
        if not ctx.get('_run_autotest', False) and \
                ctx.get('run4cover', False) and \
                not os.path.isfile(ctx['COVERAGE_PROCESS_START']):
            fd = open(ctx['COVERAGE_PROCESS_START'], 'w')
            fd.write("[report]\n")
            fd.write("omit =\n")
            fd.write("    */usr/lib*/python*\n")
            fd.write("    */__init__.py\n")
            fd.close()
        ix = 0
        sts = 0
        ctx['ctr'] = ctx['min_test']
        self.dbgmsg(ctx, '- c=%d, ctr_list=%s' % (ctx['ctr'], self.ctr_list))
        if TestCls:
            T = TestCls(self)
        for testname in test_list:
            self.dbgmsg(ctx,
                        '- min=%d, max=%d, ctr=%d, -0=%s, Cover=%s' %
                        (ctx['min_test'],
                         ctx['max_test'],
                         ctx['ctr'],
                         ctx.get('opt_noctr', False),
                         ctx.get('run4cover', False)))
            opt4childs = self.inherit_opts(ctx)
            basetn = os.path.basename(testname)
            if testname[0:6] == '__test':
                sts = self.test_result(ctx,
                                       testname,
                                       True,
                                       True)
            elif testname[0:9] == '__version':
                t = testname[10]
                x = ''
                v = ''
                i = 12
                while i < len(testname):
                    if str.isdigit(testname[i]) or testname[i] == '.':
                        v = v + testname[i]
                    else:
                        x = testname[i:]
                        break
                    i += 1
                sts = self.test_version(ctx, v, t, x)
            elif TestCls and hasattr(TestCls, testname):
                if ctx.get('opt_debug', False):
                    self.dbgmsg(ctx, " %s" % testname)
                sts = getattr(T, testname)(ctx)
            elif os0.nakedname(basetn) != ctx['this']:
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.test_dir, testname)
                if basetn[-3:] == '.py' or basetn[-4:] == '.pyc':
                    # if ctx.get('run4cover', False):
                    #     ctx['ctr'] = self.ctr_list[ix]
                    #     ix += 1
                    # else:
                    #     test_w_args = ['python', testname, '-n']
                    #     self.dbgmsg(ctx, " %s" % test_w_args)
                    #     p = Popen(test_w_args,
                    #               stdin=PIPE,
                    #               stdout=PIPE,
                    #               stderr=PIPE)
                    #     res, err = p.communicate()
                    #     try:
                    #         ctx['ctr'] += int(res)
                    #     except:
                    #         ctx['ctr'] += 0
                    self.dbgmsg(ctx, '- ctr=%d' % ctx['ctr'])
                    if ctx.get('run4cover', False):
                        test_w_args = ['coverage',
                                       'run',
                                       '-a',
                                       '--rcfile',
                                       ctx['COVERAGE_PROCESS_START'],
                                       testname] + opt4childs
                    else:
                        test_w_args = ['python'] + [testname] + opt4childs
                    self.dbgmsg(ctx, " %s" % test_w_args)
                    sts = subprocess.call(test_w_args)
                else:
                    # test_w_args = [testname, '-n']
                    # self.dbgmsg(ctx, " %s" % test_w_args)
                    # p = Popen(test_w_args,
                    #           stdin=PIPE,
                    #           stdout=PIPE,
                    #           stderr=PIPE)
                    # res, err = p.communicate()
                    # try:
                    #     ctx['ctr'] += int(res)
                    # except:
                    #     ctx['ctr'] += 0
                    self.dbgmsg(ctx, " %s %s" % (testname, opt4childs))
                    test_w_args = [testname] + opt4childs
                    sts = subprocess.call(test_w_args)
                ctx['ctr'] += self.ctr_list[ix]
                ix += 1
            if sts or \
                    ctx.get('teststs', TEST_SUCCESS):       # pragma: no cover
                sts = TEST_FAILED
                break
        ctx['min_test'] = ctx['ctr']
        return sts

    def main_local(self, ctx, Test, UT1=None, UT=None):
        """Default main program for local tests"""
        self.dbgmsg(ctx, '.main_local')
        test_num = 0
        test_list = []
        for i in range(MAX_TEST_NUM):
            tname = "test_{0:02}".format(test_num)
            if hasattr(Test, tname):
                test_list.append(tname)
            test_num += 1
        # if not ctx.get('opt_noctr', None) or ctx.get('run4cover', False):
        self.exec_tests_4_count(test_list, ctx, Test)
        if ctx.get('dry_run', False):
            if not ctx.get('_run_autotest', False):
                print ctx['max_test']
            sts = TEST_SUCCESS
        else:
            if not ctx.get('_run_autotest', False):
                os0.set_tlog_file(ctx.get('logfn', None),
                                  new=ctx.get('opt_new', False),
                                  echo=ctx.get('opt_echo', False))
            sts = self.exec_all_tests(test_list, ctx, Test)
        return sts

    def main_file(self, ctx=None, Test=None, UT1=None, UT=None):
        """Default main program for test execution
        ctx: context
        Test: test class for internal tests;
              if supplied only internal tests are executed
        UT1: protected Unit Test list (w/o log)
        UT: Unit Test list (if None, search for files)
        """
        if ctx is None:
            ctx = self.ctx
        if ctx.get('opt_debug', False) and \
                ctx.get('run_on_top', False) and \
                not ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, "!Test tree of %s!" % self.module_id)
        self.dbgmsg(ctx, '.main_file')
        self.dbgmsg(ctx,
                    '- min=%s, max=%s, -0=%s, Cover=%s' %
                    (ctx.get('min_test', None),
                     ctx.get('max_test', None),
                     ctx.get('opt_noctr', False),
                     ctx.get('run4cover', False)))
        # Execute sanity check on test library (no if zerobug testing itself)
        if ctx['this'] != 'test_zerobug' and \
                ctx.get('run_on_top', False) and \
                not ctx.get('_run_autotest', False):
            sts = self.sanity_check('-q')
            if sts == TEST_FAILED:                         # pragma: no cover
                print "Invalid test library!"
                exit(TEST_FAILED)
        test_list = []
        if UT is not None and isinstance(UT, list):
            self.dbgmsg(ctx, '- UT list')
            test_list = UT
        elif not ctx['this'].startswith(self.pattern) and \
                not ctx.get('_run_autotest', False):
            self.dbgmsg(ctx, '- Search for files %s' % self.pattern)
            test_files = os.path.abspath(
                os.path.join(self.test_dir,
                             self.pattern))
            for fn in sorted(glob.glob(test_files)):
                if len(fn) - fn.rfind('.') <= 4:
                    if fn.endswith('.py'):
                        test_list.append(fn)
                    elif os.access(fn, os.X_OK) and fn.endswith('.sh'):
                        test_list.append(fn)
                elif os.access(fn, os.X_OK) and os.name == 'posix':
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
        # if not ctx.get('opt_noctr', None) or ctx.get('run4cover', False):
        self.exec_tests_4_count(test_list, ctx, Test)
        if ctx.get('dry_run', False):
            if not ctx.get('_run_autotest', False):
                print ctx['ctr']
                # sys.stderr.write("%d\n" % ctx['max_test'])
            sts = TEST_SUCCESS
        else:
            if not ctx.get('_run_autotest', False):
                os0.set_tlog_file(ctx.get('logfn', None),
                                  new=ctx.get('opt_new', False),
                                  echo=ctx.get('opt_echo', False))
            sts = self.exec_all_tests(test_list, ctx, Test)
            if ctx.get('run_on_top', False) and \
                    not ctx.get('_run_autotest', False):
                if sts == TEST_SUCCESS:
                    print success_msg
                else:
                    print fail_msg
        return sts

    def main(self, ctx, Test):
        """Default main program for all tests"""
        if Test:
            sts = self.main_file(ctx, Test)
        else:
            sts = self.main_file(ctx)
        return sts

    def dbgmsg(self, ctx, msg):
        if ctx.get('opt_debug', False):
            if msg[0] == "!":
                fd = open(self.test_dir + '/z0bug.tracehis', 'w')
            else:
                fd = open(self.test_dir + '/z0bug.tracehis', 'a')
            fd.write("%s> %s\n" % (os.path.basename(ctx['this_fqn']), msg))
            fd.close()

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
                        print "%sTest %d/%d: %s" % (prfx,
                                                    ctx['ctr'],
                                                    ctx['max_test'],
                                                    msg)
                    else:
                        print "%sTest %d: %s" % (prfx,
                                                 ctx['ctr'],
                                                 msg)
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
        ctx = self.ready_opts(ctx)
        ctx['ctr'] += 1
        if ctx.get('teststs', TEST_SUCCESS):                 # pragma: no cover
            return TEST_FAILED
        self.msg_test(ctx, msg)
        if not ctx.get('dry_run', False):
            if test_value != result_val:                     # pragma: no cover
                print "Test '%s' failed: expected '%s', found '%s'" % \
                    (msg,
                     test_value,
                     result_val)
                ctx['teststs'] = TEST_FAILED
                if ctx.get('on_error', '') != 'continue':
                    raise AssertionError
                else:
                    return TEST_FAILED
        return TEST_SUCCESS

    def init_test_ctx(self, opt_echo, full=None):
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
        z0ctx = self.init_test_ctx(opt_echo, full)
        sts = self.main_file(z0ctx, SanityTest)
        if full:
            for p in 'min_test', 'max_test', 'ctr':
                    full[p] = z0ctx[p]
        del z0ctx
        return sts


# main = Z0test(autorun=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
