# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
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
##############################################################################
"""Zeroincombenze® unit test library for python programs

This library can run unit test of target package software.
Run like z0testrc for bash scripts
Package and test enviroment and deployment is:
 ./pkg                  Package directory (may be pypi packge or Odoo module);
                        [$RUNDIR in bash test]
 ./pkg/tests            Unit test directory
                        (must contains one of 'all_tests' or 'test_PKG')
                        [$TESTDIR in bash test]
 ./pkg/tests/z0testlib  This unit test python file [z0testrc in bash test]
                        usually does not exist; may be a real file
                        (when is under test), or a link to ~/dev/;
                        on github.com must be a real file
 ./pkg/z0librc          Local bash script library for bash scipts;
                        may be a real file (when is under test), or a link;
                        if is not present is /etc/z0librc
 ./pkg/_travis          Interface to travis emulator;
                        usually is a link to ~/dev/_travis
                        [$TRAVISDIR in bash test]
                        on github.com become a directory with copy of travis
                        interface files; in future, could be become a
                        test project for all packages.

Unit test can run in package directory or in ./tests directory of package
Main unit test (usually 'all_tests' script) calls all unit test files
named 'test_[0-9]*' called by this library in numbered order.
In every unit test file the 'Test' class contains unit test functions
named 'test_[0-9]*' called by this library in numbered order.
Functions may be called with dry_run option by 'exec_tests_4_counts',
to count # of tests.
Function must be always return TEST_SUCCESS or TEST_FAILED status.
Every unit test file must call 'parseopttest' to crete context from
commandline which is:
$ unit_test [-hek][-l file][-Nnq][-s number][-Vv][-z number][-0]
where:
-h             this help
-e             enable echoing even if not interactive tty
-k             keep current logfile
-l file        set logfile name
-N             create new logfile
-n             count and display # unit tests (do no test, return success)
-q             run tests in quiet mode (no echo)
-s number      count 1st test next to number (do run test, return test result)
-V             show version (do no test, return success);
               version on unit test should be the same of tested software
-v             verbose mode
-x             execute silently test library sanity check and exit [no bash]
-X             execute test library sanity check and exit [no bash]
-z number      display total # tests when execute them
-0             no count # unit tests
(w/o switches) do run test and return test result

As result this library (and z0testrc for bash scripts) parse optional switches
and returns the follow context with appropriate values.
caller_fqn:     caller full qualified name (i.e. /opt/odoo/zar.pyc)
caller:         caller name, w/o extension (i.e. zar)
ctr;            test counter [also in bash test]
dry_run:        dry-run (do nothing) execution [opt_dry_run in bash test] "-n"
esanity:        True if required sanity check with echo                   "-X"
max_test:       # of tests to excecute [also in bash test]
opt_echo:       True if echo test result onto std output                  "-e"
opt_new:        new log file [also in bash test]                          "-N"
opt_noctr:      do not count # tests [also in bash test]                  "-0"
opt_verbose:    From -v switch; show message during execution             "-v"
logfn:          real trace log file name from switch                      "-l"
qsanity:        True if required sanity check w/o echo                    "-x"
run_daemon:     True if execution w/o tty as stdio
tlog:           default tracelog file name
_run_autotest:  True if running auto-test
_parser:        parser
_opt_obj:       parser obj, to acquire optional switches
WLOGCMD:        oveerride opt_echo; may be None, 'echo', 'echo-1' or 'echo-0'
Z0:             this library object
"""

import pdb
import os
import subprocess
from subprocess import Popen, PIPE
import logging
import argparse
import inspect
import glob
from os0 import os0


# Z0test library version
__version__ = "0.1.3"
# Module to test version (if supplied version test is executed)
# REQ_TEST_VERSION = "0.1.4"

# return code
TEST_FAILED = 1
TEST_SUCCESS = 0
RED = "\033[1;31m"
GREEN = "\033[1;32m"
CLEAR = "\033[0;m"
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
LX_CFG_S = ()
# List of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# List of string parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_S = ('opt_echo',    'logfn',
                'dry_run',     'opt_new',
                'opt_verbose',
                'opt_noctr')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_B = ('qsanity', 'esanity')
# List of numeric parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_N = ('ctr', 'max_test')
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_CFG_S
LX_SB = ('dry_run',)
#
DEFDCT = {}
#
LX_OPT_ARGS = {'opt_echo': '-e',
               'logfn': '-l',
               'dry_run': '-n',
               'opt_new': '-N',
               'ctr': '-s',
               'opt_verbose': '-v',
               'max_test': '-z',
               'opt_noctr': '-0'}


class Test():
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
                                         "Opt -n (daemon)",
                                         False,
                                         ctx['run_daemon'])
            else:
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (daemon)",
                                         True,
                                         ctx['run_daemon'])
        if sts == TEST_SUCCESS:
            if os.isatty(0):
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (-e)",
                                         False,
                                         ctx['opt_echo'])
            else:
                sts = self.Z.test_result(z0ctx,
                                         "Opt -n (-e)",
                                         True,
                                         ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-k)",
                                     False,
                                     ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-l)",
                                     "~/" + ctx['caller'] + ".log",
                                     ctx['logfn'])
        ctx = self.Z.ready_opts(ctx)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-s)",
                                     0,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-z)",
                                     0,
                                     ctx['max_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -n (-0)",
                                     False,
                                     ctx['opt_noctr'])
        return sts

    def test_02(self, z0ctx):
        """Sanity autotest #2"""
        # z0ctx = self.clear_test_ctx(z0ctx)
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
        # z0ctx = self.Z.clear_test_ctx(z0ctx)
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
        # z0ctx = self.Z.clear_test_ctx(z0ctx)
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
        # z0ctx = self.Z.clear_test_ctx(z0ctx)
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
        # z0ctx = self.Z.clear_test_ctx(z0ctx)
        # pdb.set_trace()
        opts = ['-s0']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -s0",
                                 0,
                                 ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-s', '0']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 0",
                                     0,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-s13']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s13",
                                     13,
                                     ctx['ctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -q (-n)",
                                     False,
                                     ctx['dry_run'])
        if sts == TEST_SUCCESS:
            opts = ['-s', '13']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 13",
                                     13,
                                     ctx['ctr'])
        return sts

    def test_07(self, z0ctx):
        """Sanity autotest #7"""
        # z0ctx = self.Z.clear_test_ctx(z0ctx)
        pdb.set_trace()
        opts = ['-s', '0', '-z', '13']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx,
                                 "Opt -s 0",
                                 0,
                                 ctx['ctr'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx,
                                     "Opt -s 0 (-z)",
                                     13,
                                     ctx['max_test'])
        return sts


class Z0test:

    def __init__(self, id=None):
        caller_fqn = inspect.stack()[1][1]
        this_dir = os.path.dirname(caller_fqn)
        caller = os0.nakedname(os.path.basename(caller_fqn))
        if not id:
            if caller[0:5] == 'test_':
                id = caller[5:]
            else:
                id = caller
            if id[-3:] >= '_00' and id[-3:] <= '_99':
                id = id[0:-3]
            if id[-5:] >= '_test':
                id = id[0:-5]
        self.module_id = id
        self.this_dir = this_dir
        # If auto regression test is executing
        self.tlog_fn = this_dir + "/" + self.module_id + "_test.log"

    def create_parser(self, version, ctx):
        """Standard test option parser; same funcionality of bash version
        -e --echo       set echo
        -h --help       show help
        -k --keep       keep current logfile
        -l --logname    set log filename
        -N --new        create new logfile
        -n --dry-run    count and display # unit tests
        -q --quiet      run tests without output (quiet mode)
        -s --start      count 1st test next to number
        -V --version    show version
        -v --verbose    verbose mode
        -x --qsanity    execute silently test library sanity check and exit
        -X --esanity    execute test library sanity check and exit
        -z --end        display total # tests when execute them
        -0 --no-count   no count # unit tests
        """
        parser = argparse.ArgumentParser(
            description="Regression test",
            epilog="© 2015-2016 by SHS-AV s.r.l."
                   " - http://www.zeroincombenze.org")
        parser.add_argument("-e", "--echo",
                            help="enable echoing even if not interactive tty",
                            action="store_true",
                            dest="opt_echo_e",
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
        parser.add_argument("-q", "--quiet",
                            help="run tests without output (quiet mode)",
                            action="store_false",
                            dest="opt_echo_q",
                            default=True)
        parser.add_argument("-s", "--start",
                            help="count 1st test next to number",
                            dest="ctr",
                            metavar="number")
        parser.add_argument("-V", "--version",
                            action="version",
                            version=version)
        parser.add_argument("-v", "--verbose",
                            help="verbose mode",
                            action="store_true",
                            dest="opt_verbose",
                            default=ctx['run_daemon'])
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
        return parser

    def create_params_dict(self, ctx):
        """Create all params dictionary"""
        # conf_obj = ctx.get('_conf_obj', None)
        ctx = self.create_def_params_dict(ctx)
        if 'opt_echo' not in ctx or ctx['opt_echo'] is None:
            ctx['opt_echo'] = ctx['run_daemon']
        if ctx['dry_run']:
            ctx['opt_new'] = False
        elif 'opt_new' not in ctx or ctx['opt_new'] is None:
            if ctx.get('ctr', 0) == 0 or \
                    ctx.get('ctr', 0) is None:
                ctx['opt_new'] = True
            else:
                ctx['opt_new'] = False
        if not ctx['logfn'] or ctx['logfn'] == '':
            if 'tlog' in ctx:
                ctx['logfn'] = ctx['tlog']
            else:
                ctx['logfn'] = "~/" + ctx['caller'] + ".log"
        if not ctx.get('WLOGCMD', None) \
                and not ctx.get('_run_autotest', False):
            os0.set_tlog_file(ctx['logfn'],
                              new=ctx['opt_new'],
                              echo=ctx['opt_echo'])
        return ctx

    def create_def_params_dict(self, ctx):
        """Create default params dictionary"""
        opt_obj = ctx.get('_opt_obj', None)
        conf_obj = ctx.get('_conf_obj', None)
        s = "options"
        if conf_obj:
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

    def parseoptest(self, arguments, version=None, tlog=None):
        ctx = {}
        caller_fqn = inspect.stack()[1][1]
        ctx['caller_fqn'] = caller_fqn
        caller = os0.nakedname(os.path.basename(caller_fqn))
        ctx['caller'] = caller
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:
            ctx['run_daemon'] = True
        if tlog:
            ctx['tlog'] = tlog
        else:
            ctx['tlog'] = self.tlog_fn
        # running autotest
        if version is None:
            ctx['_run_autotest'] = True
        parser = self.create_parser(version, ctx)
        ctx['_parser'] = parser
        opt_obj = parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        ctx = self.create_params_dict(ctx)
        # if 'opt_echo' not in ctx or ctx['opt_echo'] is None:
        #     ctx['opt_echo'] = ctx['run_daemon']
        if ctx['esanity']:
            exit(self.sanity_check('-e'))
        elif ctx['qsanity']:
            exit(self.sanity_check('-q'))
        return ctx

    def default_conf(self, ctx):
        return {}

    def inherit_opts(self, ctx):
        args = []
        for p in LX_OPT_CFG_S:
            if p == 'opt_echo':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
                else:
                    args.append('-q')
            elif p == 'opt_verbose' or p == 'opt_noctr':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'logfn':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p] + ctx[p])
        return args

    def ready_opts(self, ctx):
        if 'max_test' not in ctx or ctx['max_test'] is None:
            ctx['max_test'] = 0
        if 'ctr' not in ctx or ctx['ctr'] is None:
            ctx['ctr'] = 0
        if '_prior_msg' not in ctx:
            ctx['_prior_msg'] = ''
        return ctx

    def save_opt(self, ctx, p):
        if p in ctx:
            sp = 'save_' + p
            ctx[sp] = ctx[p]
        return ctx

    def restore_opt(self, ctx, p):
        sp = 'save_' + p
        if sp in ctx:
            ctx[p] = ctx[sp]
            del ctx[sp]
        elif p in ctx:
            del ctx[p]
        return ctx

    def exec_tests_4_count(self, test_list, ctx, TestCls=None):
        args = ['-n']
        ctx = self.ready_opts(ctx)
        for p in ('dry_run', 'ctr', 'max_test'):
            ctx = self.save_opt(ctx, p)
        if TestCls:
            T = TestCls(self)
        pdb.set_trace()
        for testname in test_list:
            # Check for internal test
            if TestCls and hasattr(TestCls, testname):
                if ctx.get('opt_noctr', None):
                    ctr = 0
                elif ctx.get('test_ctr', None):
                    ctr = ctx['test_ctr']
                else:
                    ctx['dry_run'] = True
                    ctx['ctr'] = 0
                    getattr(T, testname)(ctx)
                    ctr = ctx['ctr']
                ctx['max_test'] += ctr
            elif os0.nakedname(os.path.basename(testname)) != ctx['caller']:
                if ctx.get('opt_noctr', None):
                    ctr = 0
                elif ctx.get('test_ctr', None):
                    ctr = ctx['test_ctr']
                else:
                    test_w_args = ['python'] + [testname] + args
                    p = Popen(test_w_args,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    ctr = int(res)
                ctx['max_test'] += ctr
        for p in ('dry_run', 'ctr'):
            ctx = self.restore_opt(ctx, p)
        if ctx['save_max_test'] > 0:
            ctx['max_test'] = ctx['save_max_test']
        else:
            ctx['max_test'] += ctx['ctr']
        del ctx['save_max_test']
        if ctx.get('opt_noctr', None):
            ctx['max_test'] = 0
        ctx['_prior_msg'] = ''

    def exec_all_tests(self, test_list, ctx, TestCls=None):
        args = self.inherit_opts(ctx)
        ctx = self.ready_opts(ctx)
        sts = 0
        if TestCls:
            T = TestCls(self)
        self.init_logger(ctx)
        for testname in test_list:
            # Check for internal test
            if TestCls and hasattr(TestCls, testname):
                sts = getattr(T, testname)(ctx)
            elif os0.nakedname(os.path.basename(testname)) != ctx['caller']:
                if ctx.get('opt_noctr', None):
                    test_w_args = ['python'] + [testname]
                    sts = subprocess.call(test_w_args)
                else:
                    test_w_args = ['python'] + [testname] + args
                    sts = subprocess.call(test_w_args)
            if sts:
                break
        return sts

    def main_local(self, ctx, Test):
        """Default main program for local tests"""
        test_num = 0
        test_list = []
        for i in range(MAX_TEST_NUM):
            tname = "test_{0:02}".format(test_num)
            if hasattr(Test, tname):
                test_list.append(tname)
            test_num += 1
        self.exec_tests_4_count(test_list, ctx, Test)
        sts = self.exec_all_tests(test_list, ctx, Test)
        return sts

    def main_file(self, ctx):
        """Default main program for tests"""
        # Execute sanity check on test library
        sts = self.sanity_check('-q')
        if sts == TEST_FAILED:
            print "Invalid test library!"
            exit(TEST_FAILED)
        test_files = os.path.abspath(
            os.path.join(self.this_dir,
                         self.module_id + '_test*.py'))
        tests = glob.glob(test_files)
        self.exec_tests_4_count(tests, ctx)
        sts = self.exec_all_tests(tests, ctx)
        if not ctx.get('dry_run', False):
            if sts == TEST_SUCCESS:
                print success_msg
            else:
                print fail_msg

    def main(self, ctx, Test):
        """Default main program for all tests"""
        if Test:
            sts = self.main_local(ctx, Test)
        else:
            sts = self.main_file(ctx)
        return sts

    def init_logger(self, ctx):
        self.wlog = None
        file_log = ctx.get('logfn', None)
        self.wlog = logging.getLogger()
        self.wlog.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(message)s'))
        self.wlog.addHandler(ch)
        if file_log:
            fh = logging.FileHandler(file_log, 'w')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self.wlog.addHandler(fh)

    def msg_test(self, ctx, msg):
        ctx = self.ready_opts(ctx)
        if msg == ctx['_prior_msg']:
            NEWLN = False
            prfx = "\x1b[A"
        else:
            NEWLN = True
            prfx = ""
            ctx['_prior_msg'] = msg
        if not ctx.get('dry_run', False):
            if ctx.get('WLOGCMD', None):
                if ctx['WLOGCMD'] == "echo" or ctx['WLOGCMD'] == "wecho-1":
                    if ctx['max_test']:
                        print "%sTest %d/%d: %s" % (prfx,
                                                    ctx['ctr'],
                                                    ctx['max_test'],
                                                    msg)
                    else:
                        print "%sTest %d: %s" % (prfx,
                                                 ctx['ctr'],
                                                 msg)
            else:
                if ctx['max_test']:
                    txt = "{0}Test {1}/{2}: {3}".format(prfx,
                                                        ctx['ctr'],
                                                        ctx['max_test'],
                                                        msg)
                else:
                    txt = "{0}Test {1}: {2}".format(prfx,
                                                    ctx['ctr'],
                                                    msg)
                if NEWLN:
                    self.wlog.info(txt)
                else:
                    print "\x1b[A" + txt
                    self.wlog.debug(txt)

    def test_result(self, ctx, msg, test_value, res_value):
        ctx = self.ready_opts(ctx)
        # if ctx['ctr'] == 0:
        #     self.init_logger(ctx)
        ctx['ctr'] += 1
        self.msg_test(ctx, msg)
        if not ctx.get('dry_run', False):
            if test_value != res_value:
                print "Test failed: expected '%s', found '%s'" % (test_value,
                                                                  res_value)
                return TEST_FAILED
        return TEST_SUCCESS

    def init_test_ctx(self, opt_echo):
        """Set context value for autoest"""
        z0ctx = {}
        if opt_echo == '-e':
            z0ctx['WLOGCMD'] = 'echo'
        elif opt_echo == '-q':
            z0ctx['WLOGCMD'] = 'wecho-0'
        z0ctx = self.clear_test_ctx(z0ctx)
        # Value for auto regression test
        self.tlog_fn = '~/z0testlib.log'
        return z0ctx

    def clear_test_ctx(self, ctx):
        for p in (LX_OPT_CFG_S):
            if p in ctx:
                del ctx[p]
        for p in (LX_OPT_CFG_B):
            if p in ctx:
                del ctx[p]
        return ctx

    def sanity_check(self, opt_echo):
        """Internal regression test
        Module z0testlib is needed to run regression tests
        This function run auto validation tests for z0testlib functions
        """
        z0ctx = self.init_test_ctx(opt_echo)
        sts = self.main_local(z0ctx, Test)
        return sts

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
