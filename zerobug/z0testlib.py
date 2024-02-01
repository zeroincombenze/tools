# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function, unicode_literals
from builtins import str as text
from io import open
import os
import sys

import argparse
import glob
import shutil
import stat
import subprocess
import re

from string import Template
from subprocess import PIPE, Popen
if sys.version_info[0] == 2:
    from inspect import getargspec
else:
    from inspect import signature
import unittest

import magic

from os0 import os0
from z0lib import z0lib
from python_plus import _c

__version__ = "2.0.14"

# return code
TEST_FAILED = 1
TEST_SUCCESS = 0
if os.name == "posix":
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    CLEAR = "\033[0;m"
else:  # pragma: no cover
    RED = ''
    GREEN = ''
    CLEAR = ''
fail_msg = RED + "Test FAILED!" + CLEAR
success_msg = GREEN + "Test successfully terminated" + CLEAR
# max # of test
MAX_TEST_NUM = 10
# Apply for configuration file (True/False)
APPLY_CONF = False
# Default configuration file (i.e. myfile.config or False for default)
CONF_FN = None
# Read Odoo configuration file (False or /etc/odoo-server.config)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.config)
OE_CONF = False
# Warning: set all LXs with no values -> LX=(), with 1 value -> LX=(value,)
# List of string parameters in [options] of config file
LX_CFG_S = ('failfast', 'opt_debug', 'opt_verbose', 'opt_noctr')
# List of pure boolean parameters in [options] of config file
LX_CFG_B = ('failfast', 'opt_debug', 'python2', 'python3')
# List of string parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_S = (
    'opt_echo',
    'logfn',
    'opt_tjlib',
    'opt_oelib',
    'dry_run',
    'opt_new',
    'opt_verbose',
    'failfast',
    'opt_debug',
    'opt_noctr',
    'run4cover',
    'max_test',
    'min_test',
    'opt_pattern',
    'no_run_on_top',
    'qsanity',
    'esanity',
    'python2',
    'python3',
)
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_B = ('qsanity', 'esanity', 'failfast', 'opt_debug',
                'opt_tjlib', 'opt_oelib')
# List of numeric parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_N = ('ctr', 'max_test', 'min_test')
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_CFG_S
LX_SB = ('failfast', 'dry_run')
#
DEFDCT = {'run4cover': False, 'failfast': False, 'opt_debug': False, 'opt_new': False}
#
LX_OPT_ARGS = {
    'opt_debug': '-B',
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
    'python3': '-3',
}

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


def sign_params(method):
    return (
        (getargspec(method).args + (getargspec(method).varargs or []))[1:]
        if sys.version_info[0] == 2 else list(signature(method).parameters))


def print_flush(msg):
    if sys.version_info[0] == 3:
        print(msg, flush=True)
    else:
        print(msg)
        sys.stdout.flush()


def main():
    return unittest.main()


class RunPypiTest(unittest.TextTestRunner):

    def startTest(self, test):
        super(RunPypiTest, self).startTest(test)
        print("self.startTest(test)")
        if not hasattr(test, "assert_counter"):
            test.assert_counter = 0

    def stopTest(self, test):
        super(RunPypiTest, self).stopTest(test)
        # self.testsRun
        print("self.stopTest(test)")
        # print("🏆🥇 %d tests SUCCESSFULLY completed" % self.assert_counter)
        print("%d tests SUCCESSFULLY completed" % test.assert_counter)

    def startTestRun(self):
        super(RunPypiTest, self).startTestRun()
        print("self.startTestRun()")
        if not hasattr(self, "assert_counter"):
            self.assert_counter = 0

    def stopTestRun(self):
        super(RunPypiTest, self).stopTestRun()
        #  self.testsRun
        print("self.stopTestRun()")
        # print("🏆🥇 %d tests SUCCESSFULLY completed" % self.assert_counter)
        print("%d tests SUCCESSFULLY completed" % self.assert_counter)


class PypiTest(unittest.TestCase):

    assert_counter = 0

    def _makeResult(self):
        super(PypiTest, self)._makeResult()

    def doCleanups(self):
        pass

    def version(self):
        return __version__

    # ----------------------------------
    # --  Counted assertion functions --
    # ----------------------------------

    def assertTrue(self, expr, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertTrue(expr, msg=msg)

    def assertFalse(self, expr, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertFalse(expr, msg=msg)

    def assertRaises(self, expected_exception, *args, **kwargs):     # pragma: no cover
        self.assert_counter += 1
        return super(PypiTest, self).assertRaises(expected_exception, *args, **kwargs)

    def assertEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertEqual(first, second, msg=msg)

    def assertNotEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertNotEqual(first, second, msg=msg)

    def assertIn(self, member, container, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIn(member, container, msg=msg)

    def assertNotIn(self, member, container, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertNotIn(member, container, msg=msg)

    def assertIs(self, expr1, expr2, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIs(expr1, expr2, msg=msg)

    def assertIsNot(self, expr1, expr2, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsNot(expr1, expr2, msg=msg)

    def assertLess(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertLess(first, second, msg=msg)

    def assertLessEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertLessEqual(first, second, msg=msg)

    def assertGreater(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertGreater(first, second, msg=msg)

    def assertGreaterEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertGreaterEqual(first, second, msg=msg)

    def assertIsNone(self, obj, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsNone(obj, msg=msg)

    def assertIsNotNone(self, obj, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsNotNone(obj, msg=msg)

    def assertIsInstance(self, obj, cls, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsInstance(obj, cls, msg=msg)

    def assertNotIsInstance(self, obj, cls, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertNotIsInstance(obj, cls, msg=msg)

    def assertMatch(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        msg = msg or ("Value <<%s>> does not match <<%s>>!" % (first, second))
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsNotNone(re.match(second, first), msg=msg)

    def assertNotMatch(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        msg = msg or ("Value <<%s>> does match <<%s>>!" % (first, second))
        if msg_info:
            print(("%d. " % self.assert_counter) + msg_info)
        return super(PypiTest, self).assertIsNone(re.match(second, first), msg=msg)


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


class SanityTest:
    """Auto test for z0testlib
    This class is structured exactly as a target test
    """

    def __init__(self, z0bug):
        self.Z = z0bug
        self.Z.inherit_cls(self)

    def test_01(self, z0ctx):
        """Sanity autotest #1"""
        opts = ['-n']
        ctx = self.Z.parseoptest(opts)
        self.assertTrue(ctx['dry_run'], msg_info="Opt -n")
        if os.isatty(0):
            self.assertTrue(ctx['run_tty'], msg_info="Opt -n (tty)")
        else:  # pragma: no cover
            self.assertFalse(ctx['run_tty'], msg_info="Opt -n (tty)")
        if os.isatty(0):
            self.assertFalse(ctx['run_daemon'], msg_info="Opt -n (daemon)")
        else:  # pragma: no cover
            self.assertTrue(ctx['run_daemon'], msg_info="Opt -n (daemon)")
        if os.isatty(0):
            self.assertTrue(ctx['opt_echo'], msg_info="Opt -n (-e)")
        else:  # pragma: no cover
            self.assertFalse(ctx['opt_echo'], msg_info="Opt -n (-e)")
        self.assertFalse(ctx['opt_new'], msg_info="Opt -n (-k)")
        ctx = self.Z._ready_opts(ctx)
        self.assertEqual(ctx['ctr'], 0, msg_info="Counter")
        self.assertEqual(ctx['min_test'], 0, msg_info="Opt -n (-r)")
        self.assertEqual(ctx['max_test'], 0, msg_info="Opt -n (-z)")
        self.assertTrue(ctx['opt_noctr'], msg_info="Opt -n (-Q)")
        self.assertEqual(ctx['opt_debug'], 0, msg_info="Opt -B")
        self.assertTrue(ctx['run_on_top'], msg_info="Run on Top")
        return self.ret_sts()

    def test_02(self, z0ctx):
        """Sanity autotest #2"""
        tlog = "~/devel/z0testlib.log"
        opts = ['-n']
        ctx = self.Z.parseoptest(opts, tlog=tlog)
        sts = self.Z.test_result(z0ctx, "Opt -n", True, ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -n (-k)", False, ctx['opt_new'])
        # if sts == TEST_SUCCESS:
        #     sts = self.Z.test_result(z0ctx, "Opt -n (-l)", tlog, ctx['logfn'])
        return sts

    # def test_03(self, z0ctx):
    #     """Sanity autotest #3"""
    #     tlog = "~/devel/z0testlib.log"
    #     opts = ['-n', '-l', tlog]
    #     ctx = self.Z.parseoptest(opts)
    #     sts = self.Z.test_result(z0ctx, "Opt -n", True, ctx['dry_run'])
    #     if sts == TEST_SUCCESS:
    #         sts = self.Z.test_result(z0ctx, "Opt -n (-k)", False, ctx['opt_new'])
    #     if sts == TEST_SUCCESS:
    #         sts = self.Z.test_result(z0ctx, "Opt -n (-l)", tlog, ctx['logfn'])
    #     return sts

    def test_04(self, z0ctx):
        """Sanity autotest #4"""
        opts = ['-e']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx, "Opt -e", True, ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -e (-N)", True, ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -e (-n)", False, ctx['dry_run'])
        return sts

    def test_05(self, z0ctx):
        """Sanity autotest #5"""
        opts = ['-q']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx, "Opt -q", False, ctx['opt_echo'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -q (-N)", True, ctx['opt_new'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -q (-n)", False, ctx['dry_run'])
        return sts

    def test_06(self, z0ctx):
        """Sanity autotest #6"""
        opts = ['-r0']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx, "Opt -r0", 0, ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Run on Top", False, ctx['run_on_top'])
        if sts == TEST_SUCCESS:
            opts = ['-r', '0']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx, "Opt -r 0", 0, ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -r 0 -N", True, ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-r13']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx, "Opt -r13", 13, ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -r13 -n", False, ctx['dry_run'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -q -N", False, ctx['opt_new'])
        if sts == TEST_SUCCESS:
            opts = ['-r', '13', '-N']
            ctx = self.Z.parseoptest(opts)
            sts = self.Z.test_result(z0ctx, "Opt -r 13", 13, ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -r 13 -N", True, ctx['opt_new'])
        return sts

    def test_07(self, z0ctx):
        """Sanity autotest #7"""
        opts = ['-r', '0', '-z', '13']
        ctx = self.Z.parseoptest(opts)
        sts = self.Z.test_result(z0ctx, "Opt -r 0", 0, ctx['min_test'])
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, "Opt -r 0 -z 13", 13, ctx['max_test'])
        return sts

    def test_08(self, z0ctx):
        """Sanity autotest #8"""
        opts = ["-Q"]
        ctx = self.Z.parseoptest(opts)
        ctx['WLOGCMD'] = "wecho-0"
        # sts = self.simulate_main(ctx, '1')
        self.Z.main(ctx, unittest_list=['__test_01'])          # pragma: no cover
        tres = 1
        sts = self.Z.test_result(z0ctx, "UT", tres, ctx['max_test'])
        if sts == TEST_SUCCESS:
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_02'])
            tres = 2
            sts += self.Z.test_result(z0ctx, "UT", tres, ctx['max_test'])
        if sts == TEST_SUCCESS:
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            tres = 3
            sts += self.Z.test_result(z0ctx, "UT", tres, ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.test_result(z0ctx, "UT -0", 0, ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-n', '-Q']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            tres = 3
            sts += self.Z.test_result(z0ctx, "UT -n", tres, ctx['max_test'])
            tres = 3
            sts += self.Z.test_result(z0ctx, "UT -n", tres, ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-n', '-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            sts += self.Z.test_result(z0ctx, "UT -n -0", 0, ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-n', '-Q']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            tres = 13
            sts += self.Z.test_result(z0ctx, "UT -z13", tres, ctx['max_test'])
            tres = 3
            sts = self.Z.test_result(z0ctx, "UT -z13", tres, ctx['ctr'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-0']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            sts += self.Z.test_result(z0ctx, "UT -z13 -0", 13, ctx['max_test'])
        if sts == TEST_SUCCESS:
            opts = ['-z13', '-0', '-n']
            ctx = self.Z.parseoptest(opts)
            ctx['WLOGCMD'] = "wecho-0"
            sts = self.Z.main(ctx, unittest_list=['__test_01', '__test_02'])
            sts += self.Z.test_result(z0ctx, "UT -z13 -0 -n", 13, ctx['max_test'])
        return sts


class Z0test(object):
    """The command line program to execute all tests in professional way."""

    def version(self):
        return __version__

    def __init__(self, argv=None, id=None, version=None, autorun=False):
        self.autorun = autorun
        if argv is None:
            if len(sys.argv) and not sys.argv[0].startswith('-'):
                argv = sys.argv[1:]
                self.this_fqn = os.path.abspath(sys.argv[0])
            else:
                argv = []
        else:
            self.autorun = True
            self.this_fqn = self._get_this_fqn()
        if "--ut" in argv:
            sys.exit(main())
        self.this = os.path.splitext(os.path.basename(self.this_fqn))[0]
        self.this_dir = os.path.abspath(os.getcwd())
        if (
                not os.path.basename(self.this_dir) == 'tests'
                and not os.path.isdir(os.path.join(self.this_dir, 'tests'))
        ):
            self.this_dir = os.path.dirname(self.this_fqn)
        if os.path.basename(self.this_dir) == 'tests':
            self.testdir = self.this_dir
            self.rundir = os.path.dirname(self.this_dir)
        elif os.path.isdir('./tests'):                              # pragma: no cover
            self.testdir = os.path.join(self.this_dir, 'tests')
            self.rundir = self.this_dir
        else:                                                       # pragma: no cover
            self.testdir = self.rundir = self.this_dir
        # Testing package dir must be the 1.st one in sys.path
        this_pkg_dir = os.path.dirname(self.rundir)
        if this_pkg_dir in sys.path:
            ix = sys.path.index(this_pkg_dir)
            del sys.path[ix]
        sys.path.insert(0, this_pkg_dir)
        if self.rundir in sys.path:
            ix = sys.path.index(self.rundir)
            del sys.path[ix]
        sys.path.insert(0, self.rundir)

        if not id:
            if self.this.startswith('test_'):
                id = self.this[5:]
            elif self.this.startswith('zerobug') or self.this == '__main__':
                id = os.path.basename(self.rundir)
            else:
                id = self.this
            if id[-3:] >= '_00' and id[-3:] <= '_99':
                id = id[0:-3]
            if id[-5:] == '_test':
                id = id[0:-5]
        else:
            self.autorun = True
        self.module_id = id
        if self.this == 'zerobug':
            self.pattern = [self.module_id + '_test*', 'test_*']
        else:
            self.pattern = [self.this, 'test_*']
        # If auto regression test is executing
        # self.def_tlog_fn = os.path.join(self.testdir, self.module_id + "_test.log")
        self.ctr_list = []
        if self.autorun:
            self.z0ctx = self.parseoptest(argv, version=version)
            sys.exit(self.main())
        self.home_devel = os.environ.get("HOME_DEVEL") or os.path.expanduser("~/devel")
        self.odoo_root = os.path.dirname(self.home_devel)
        self.z0ctx = {}

    def inherit_cls(self, test_cls):
        setattr(test_cls, "Z", self)
        for name in (
                "assertTrue", "assertFalse", "assertEqual", "assertNotEqual",
                "assertIn", "assertNotIn",
                "assertLess", "assertLessEqual", "assertGreater", "assertGreaterEqual",
                "assertMatch", "assertNotMatch",
                "ret_sts",
        ):
            setattr(test_cls, name, getattr(self, name))

    def _create_parser(self, version, ctx):
        parser = argparse.ArgumentParser(
            description="Regression test on " + self.module_id,
            epilog="© 2015-2023 by SHS-AV s.r.l."
            " - https://zeroincombenze-tools.readthedocs.io/en/latest/zerobug",
        )
        parser.add_argument(
            "-B",
            "--debug",
            help="run tests in debug mode",
            action="store_true",
            dest="opt_debug",
            default=False,
        )
        parser.add_argument(
            "-C",
            "--no-coverage",
            help="run tests without coverage",
            action="store_false",
            dest="run4cover",
            default=True,
        )
        parser.add_argument(
            "-e",
            "--echo",
            help="enable echoing even if not interactive tty (deprecated)",
            action="store_true",
            dest="opt_echo_e",
            default=False,
        )
        parser.add_argument(
            "-f",
            "--failfast",
            help="Stop on first fail or error",
            action="store_true",
        )
        parser.add_argument(
            "-J",
            help="load travisrc (deprecated)",
            action="store_true",
            dest="opt_tjlib",
            default=False,
        )
        parser.add_argument(
            "-k",
            "--keep",
            help="keep current logfile (deprecated)",
            action="store_false",
            dest="opt_new_k",
            default=True,
        )
        parser.add_argument(
            "-l", "--logname",
            help="set logfile name (deprecated)",
            dest="logfn",
            metavar="file"
        )
        parser.add_argument(
            "-N",
            "--new",
            help="create new logfile (deprecated)",
            action="store_true",
            dest="opt_new_N",
            default=False,
        )
        parser.add_argument(
            "-n",
            "--dry-run",
            help="count and display # unit tests (deprecated)",
            action="store_true",
            dest="dry_run",
            default=False,
        )
        parser.add_argument(
            "-O",
            help="load odoorc (deprecated)",
            action="store_true",
            dest="opt_oelib",
            default=False,
        )
        parser.add_argument(
            "-p",
            "--search-pattern",
            help="Pattern to match tests, comma separated ('test*.py' default)",
            dest="opt_pattern",
            metavar="file_list",
            default='',
        )
        parser.add_argument(
            "-Q",
            "--count",
            help="count # unit tests (deprecated)",
            action="store_false",
            dest="opt_noctr",
            default=True,
        )
        parser.add_argument(
            "-q",
            "--quiet",
            help="run tests without output (quiet mode, deprecated)",
            action="store_false",
            dest="opt_echo_q",
            default=True,
        )
        parser.add_argument(
            "-R",
            "--run-inner",
            help="inner mode w/o final messages",
            action="store_true",
            dest="no_run_on_top",
        )
        parser.add_argument(
            "-r",
            "--restart",
            help="restart count next to number",
            dest="min_test",
            metavar="number",
        )
        parser.add_argument(
            "-s", "--start", help="deprecated", dest="min_test2", metavar="number"
        )
        parser.add_argument("-V", "--version", action="version", version=version)
        parser.add_argument(
            "-v",
            "--verbose",
            help="verbose mode",
            action="store_true",
            dest="opt_verbose",
            default=ctx['run_tty'],
        )
        parser.add_argument(
            "-x",
            "--qsanity",
            help="like -X but run silently (deprecated)",
            action="store_true",
            dest="qsanity",
            default=False,
        )
        parser.add_argument(
            "-X",
            "--esanity",
            help="execute test library sanity check and exit (deprecated)",
            action="store_true",
            dest="esanity",
            default=False,
        )
        parser.add_argument(
            "-z",
            "--end",
            help="display total # tests when execute them",
            dest="max_test",
            metavar="number",
        )
        parser.add_argument(
            "-0",
            "--no-count",
            help="no count # unit tests (deprecated)",
            action="store_true",
            dest="opt_noctr",
            default=True,
        )
        return parser

    def set_tlog_file(self, ctx):
        pass

    def _create_params_dict(self, ctx):
        """Create all params dictionary"""
        ctx = self._create_def_params_dict(ctx)
        if ('min_test' not in ctx or ctx.get('min_test', None) is None) and (
            'max_test' not in ctx or ctx.get('max_test', None) is None
        ):
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
            if ctx.get('min_test', 0) == 0 or ctx.get('min_test', 0) is None:
                ctx['opt_new'] = True
            else:
                ctx['opt_new'] = False
        if not ctx['logfn'] or ctx['logfn'] == '':
            if 'tlog' in ctx:
                ctx['logfn'] = ctx['tlog']
            else:
                ctx['logfn'] = "~/" + ctx['this'] + ".log"
        sts, stdout, stderr = z0lib.run_traced('coverage --version', verbose=0)
        ctx['run4cover'] = (sts == 0)
        if os.environ.get("COVERAGE_PROCESS_START", ""):
            ctx["COVERAGE_PROCESS_START"] = os.environ["COVERAGE_PROCESS_START"]
        elif ctx['run4cover']:                                      # pragma: no cover
            ctx["COVERAGE_PROCESS_START"] = os.path.abspath(
                os.path.join(self.rundir, '.coveragerc')
            )
        if os.environ.get("COVERAGE_DATA_FILE", ""):
            ctx["COVERAGE_DATA_FILE"] = os.environ["COVERAGE_DATA_FILE"]
        return ctx

    def _create_def_params_dict(self, ctx):
        """Create default params dictionary"""
        opt_obj = ctx.get('_opt_obj', None)
        conf_obj = ctx.get('_conf_obj', None)
        s = "options"
        if conf_obj:  # pragma: no cover
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
                    if hasattr(opt_obj, 'opt_echo_q') and not opt_obj.opt_echo_q:
                        ctx[p] = False
                    elif hasattr(opt_obj, 'opt_echo_e') and opt_obj.opt_echo_e:
                        ctx[p] = True
                    else:
                        ctx[p] = None
                elif p == 'opt_new':
                    if hasattr(opt_obj, 'opt_new_k') and not opt_obj.opt_new_k:
                        ctx[p] = False
                    elif hasattr(opt_obj, 'opt_new_N') and opt_obj.opt_new_N:
                        ctx[p] = True
                    else:
                        ctx[p] = None
                elif p == 'min_test':
                    if hasattr(opt_obj, 'min_test2') and opt_obj.min_test2:
                        ctx[p] = int(opt_obj.min_test2)
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
        return os.path.abspath(sys.argv[0])

    def parseoptest(self, arguments, version=None, tlog=None):
        ctx = self._ready_opts({
            'ctr': 0,
            'max_test': 0,
            'min_test': 0,
            '_prior_msg': '',
        })
        ctx['os_name'] = os.name
        ctx['rundir'] = self.rundir
        ctx['testdir'] = self.testdir
        ctx['this_fqn'] = self.this_fqn
        ctx['this'] = self.this
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:  # pragma: no cover
            ctx['run_daemon'] = True
        ctx['run_tty'] = os.isatty(0)
        if version is None:
            ctx['_run_autotest'] = True
        parser = self._create_parser(version, ctx)
        ctx['_parser'] = parser
        opt_obj = parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        ctx = self._create_params_dict(ctx)
        # if ctx['esanity']:  # pragma: no cover
        #     exit(self.sanity_check('-e'))
        # elif ctx['qsanity']:  # pragma: no cover
        #     exit(self.sanity_check('-q'))
        return ctx

    def default_conf(self, ctx):
        return DEFDCT

    def _inherit_opts(self, ctx):
        # Set run inner (child of current process)
        args = ['-R']
        for p in LX_OPT_CFG_S:
            if p == 'opt_verbose' or p == 'opt_debug':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'run4cover':
                if p in ctx and not ctx[p]:
                    args.append(LX_OPT_ARGS[p])
            elif p == 'min_test':
                args.append(LX_OPT_ARGS[p] + str(ctx['ctr']))
            elif p == 'max_test':
                if p in ctx and ctx[p]:
                    args.append(LX_OPT_ARGS[p] + str(ctx[p]))
        return args

    def _ready_opts(self, ctx):
        ctx['max_test'] = ctx.get('max_test', 0)
        ctx['min_test'] = ctx.get('min_test', 0)
        ctx['_prior_msg'] = ctx.get('_prior_msg', '')
        for (kk, name, default) in (
                ("dry_run", "dry_run", False),
                ("ctr", "assert_counter", 0),
                ("failfast", "failfast", False),
                ("successful", "successful", True),
                ("this_fqn", "this_fqn", None),
                ("this", "this", None),
        ):
            ctx[kk] = ctx.get(kk, getattr(self, name, default))
            setattr(self, name, ctx[kk])
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
        if os.path.isfile(testfile):
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

    def ret_sts(self):
        return 0 if self.successful else 1

    def set_test_env(self, ctx):
        ctx["ctr"] = max(self.assert_counter, ctx["ctr"])
        ctx["successful"] &= self.successful

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
            sts, stdout, stderr = z0lib.run_traced(cmd, verbose=0)
            res = stdout.strip()
        return self.test_result(ctx, msg, version, res)

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
        res = subprocess.call(
            ['sys.executable', '-m', 'doctest', file],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
        )
        return self.test_result(ctx, msg, TEST_SUCCESS, res)

    def _exec_tests_4_count(self, test_list, ctx, Cls2Test=None):
        # Deprecated
        opt4childs = ['-n', '-R']
        ctx = self._ready_opts(ctx)
        ctx = self._save_options(ctx)
        testctr = 0
        if Cls2Test:
            runT = self.new_Cls2Test(Cls2Test)
            if hasattr(runT, 'setup'):
                ctx['dry_run'] = True
                self.exec_local_test(runT, "setup", ctx=ctx)
        for testname in test_list:
            ctx['dry_run'] = True
            basetn = os.path.basename(testname)
            ctx['ctr'] = 0
            if testname.startswith('__test'):
                ctx['ctr'] = int(testname[7:9])
            elif testname.startswith('__version'):
                self.test_version(ctx, testname)
            elif testname.startswith('__doctest'):
                self.doctest(ctx, testname)
            elif Cls2Test and hasattr(runT, testname):
                self.exec_local_test(runT, testname, ctx=ctx)
            elif os.path.splitext(basetn)[0] != ctx['this']:
                mime = magic.Magic(mime=True).from_file(os.path.realpath(testname))
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.testdir, testname)
                if mime == 'text/x-python':
                    test_w_args = [sys.executable] + [testname] + opt4childs
                else:
                    test_w_args = [testname] + opt4childs
                p = Popen(test_w_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                res, err = p.communicate()
                try:
                    ctx['ctr'] = int(res)
                except BaseException:  # pragma: no cover
                    ctx['ctr'] = 0
                self.ctr_list.append(ctx['ctr'])
            self.set_test_env(ctx)
            testctr += ctx['ctr']
        if Cls2Test and hasattr(runT, 'teardown'):
            ctx['dry_run'] = True
            self.exec_local_test(runT, "teardown", ctx=ctx)
        ctx = self._restore_options(ctx)
        ctx['ctr'] = testctr
        if ctx.get('max_test', 0) == 0:
            ctx['max_test'] = ctx.get('min_test', 0) + testctr
        ctx['_prior_msg'] = ''
        return TEST_SUCCESS

    def new_Cls2Test(self, Cls2Test):
        if (
                hasattr(Cls2Test, "__init__")
                and len(sign_params(getattr(Cls2Test, "__init__"))) in (1, 2)
        ):
            runT = Cls2Test(self)
        else:
            runT = Cls2Test()
        self.inherit_cls(runT)
        return runT

    def exec_local_test(self, T, testname, ctx=None):
        if len(sign_params(getattr(T, testname))):
            sts = getattr(T, testname)(ctx)
        else:
            sts = getattr(T, testname)()
        if sts is None:
            return self.ret_sts()
        return sts

    def _exec_all_tests(self, test_list, ctx, Cls2Test=None):
        ctx = self._ready_opts(ctx)
        if (
            not ctx.get('_run_autotest', False)
            and ctx.get('run4cover', False)
            and not os.path.isfile(ctx['COVERAGE_PROCESS_START'])
        ):
            with open(ctx['COVERAGE_PROCESS_START'], 'w') as fd:
                fd.write(DEFAULT_COVERARC)
        ix = 0
        sts = 0
        ctx['ctr'] = ctx['min_test']

        if Cls2Test:
            runT = self.new_Cls2Test(Cls2Test)
            if hasattr(runT, "setup"):
                sts = self.exec_local_test(runT, "setup", ctx=ctx)
        for testname in test_list:
            opt4childs = self._inherit_opts(ctx)
            basetn = os.path.basename(testname)
            if testname.startswith('__test'):
                sts = self.test_result(ctx, testname, True, True)
            elif testname.startswith('__version'):
                sts = self.test_version(ctx, testname)
            elif testname.startswith('__doctest'):
                self.doctest(ctx, testname)
            elif Cls2Test and hasattr(runT, testname):
                sts = self.exec_local_test(runT, testname, ctx=ctx)
            elif os.path.splitext(basetn)[0] != ctx['this']:
                mime = magic.Magic(mime=True).from_file(os.path.realpath(testname))
                if os.path.dirname(testname) == "":
                    testname = os.path.join(self.testdir, testname)
                if mime == 'text/x-python':
                    with open(os.path.realpath(testname), "r", encoding="utf-8") as fd:
                        content = fd.read()
                    if (
                            "\nclass PypiTest(z0testlib.PypiTest):" in content
                            or "\nimport unittest\n" in content
                    ):
                        opt4childs = []
                        del content
                    if os.environ.get('TRAVIS_PDB') == 'true':
                        test_w_args = [
                            sys.executable,
                            '-m',
                            'pdb',
                            testname,
                        ] + opt4childs
                    elif ctx.get('run4cover', False) and not ctx.get('dry_run', False):
                        self.set_shabang(ctx, testname)
                        test_w_args = [
                            'coverage',
                            'run',
                            '-a',
                            '--rcfile=%s' % ctx['COVERAGE_PROCESS_START'],
                            testname,
                        ] + opt4childs
                    else:
                        test_w_args = [sys.executable] + [testname] + opt4childs
                    if ctx.get("opt_verbose"):
                        if ctx.get('dry_run', False):
                            print_flush("    > " + " ".join(test_w_args))
                        else:
                            print_flush("    $ " + " ".join(test_w_args))
                    try:
                        sts = subprocess.call(test_w_args)
                    except OSError:
                        sts = 127
                else:
                    test_w_args = [testname] + opt4childs
                    try:
                        sts = subprocess.call(test_w_args)
                    except OSError:
                        sts = 127
                if not ctx.get('opt_noctr', False):
                    ctx['ctr'] += self.ctr_list[ix]
                ix += 1
            self.set_test_env(ctx)
            if sts or not ctx.get('successful'):  # pragma: no cover
                sts = TEST_FAILED
                break
        ctx['min_test'] = ctx['ctr']
        if Cls2Test and hasattr(runT, "teardown"):
            self.exec_local_test(runT, "teardown", ctx=ctx)
        return sts

    def main_local(self, ctx, Cls2Test, unittest_list=None):
        """Default main program for local tests"""
        ctx = self._ready_opts(ctx)
        test_list = sorted(
            [
                meth
                for meth in dir(Cls2Test)
                if (meth.startswith("test_")
                    and callable(getattr(Cls2Test, meth))
                    and (not unittest_list or meth in unittest_list))
            ]
        )
        return self._exec_all_tests(test_list, ctx, Cls2Test)

    def main(self, ctx={}, Cls2Test=None, unittest_list=None):
        """Default main program for test execution

        Args:
            ctx (dict): context
            Cls2Test (class): test class for internal tests
            unittest_list (list): Unit Test list (if None, search for files)
        """
        ctx = self._ready_opts(ctx)
        if (
            ctx['this'] != 'test_zerobug'
            and ctx.get('run_on_top', False)
            and not ctx.get('_run_autotest', False)
        ):
            if (
                    ctx.get("run_on_top", True)
                    and ctx.get('run4cover', False)
                    and not ctx.get('dry_run', False)
            ):
                if ctx["COVERAGE_DATA_FILE"]:
                    with open(ctx["COVERAGE_PROCESS_START"], "r") as fd:
                        coveragerc = fd.read()
                    if "data_file" not in coveragerc:
                        if ctx.get("opt_verbose"):
                            cmd = (
                                r"sed -E \"/^\[run\]/a\ndata_file=%s\""
                                % ctx["COVERAGE_DATA_FILE"]
                            )
                            if ctx.get('dry_run', False):
                                print_flush("    > " + cmd)
                            else:
                                print_flush("    $ " + cmd)
                        coveragerc = coveragerc.replace(
                            "[run]\n",
                            "[run]\ndata_file=%s\n\n" % ctx["COVERAGE_DATA_FILE"])
                        with open(ctx["COVERAGE_PROCESS_START"], "w") as fd:
                            fd.write(coveragerc)
                cmd = "coverage erase --rcfile=%s" % ctx["COVERAGE_PROCESS_START"]
                if ctx.get("opt_verbose"):
                    if ctx.get('dry_run', False):
                        print_flush("    > " + cmd)
                    else:
                        print_flush("    $ " + cmd)
                sts, stdout, stderr = z0lib.run_traced(cmd)
                if sts:
                    print_flush('Coverage not found!')
                    ctx['run4cover'] = False
        test_list = []
        if isinstance(unittest_list, (list, tuple)):
            test_list = unittest_list
        elif not ctx.get('_run_autotest', False):
            # Discover test files
            test_list = []
            for pattern in (
                ctx['opt_pattern'] and ctx['opt_pattern'].split(',') or self.pattern
            ):
                t_list = glob.glob(os.path.abspath(os.path.join(self.testdir, pattern)))
                if not pattern.endswith(".py") and not pattern.endswith(".sh"):
                    t_list += glob.glob(
                        os.path.abspath(os.path.join(self.testdir, pattern + ".py"))
                    )
                    t_list += glob.glob(
                        os.path.abspath(os.path.join(self.testdir, pattern + ".sh"))
                    )
                for fn in sorted(set(t_list)):
                    mime = magic.Magic(mime=True).from_file(os.path.realpath(fn))
                    if mime in ('text/x-python', 'text/x-shellscript'):
                        test_list.append(fn)
        if len(test_list) == 0 and Cls2Test is not None:
            test_list = sorted(
                [
                    meth
                    for meth in dir(Cls2Test)
                    if meth.startswith("test_") and callable(getattr(Cls2Test, meth))
                ]
            )
        sts = self._exec_all_tests(test_list, ctx, Cls2Test)
        if ctx.get('run_on_top', False) and not ctx.get('_run_autotest', False):
            if sts == 0:
                print_flush(success_msg)
                if ctx.get('run4cover', False) and not ctx.get('dry_run', False):
                    cmd = ("coverage report --show-missing --rcfile=%s"
                           % ctx["COVERAGE_PROCESS_START"])
                    if ctx.get("opt_verbose"):
                        if ctx.get('dry_run', False):
                            print_flush("    > " + cmd)
                        else:
                            print_flush("    $ " + cmd)
                    sts, stdout, stderr = z0lib.run_traced(cmd, verbose=0)
                    print_flush(stdout + stderr)
                    if sts:
                        ctx['run4cover'] = False
                    sts = 0
            else:
                print_flush(fail_msg)
        return sts

    def msg_test(self, ctx, msg):
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
                        print_flush(
                            "%sTest %d/%d: %s"
                            % (prfx, ctx['ctr'], ctx['max_test'], msg)
                        )
                    else:
                        print_flush("%sTest %d: %s" % (prfx, ctx['ctr'], msg))

    def test_result(self, ctx, msg, test_value, result_val, op=None):
        # This function is deprecated
        ctx = self._ready_opts(ctx)
        if not ctx.get('successful'):  # pragma: no cover
            return TEST_FAILED
        ctx['ctr'] += 1
        self.msg_test(ctx, msg)
        op = op or "=="
        if op not in ("==", "=~"):
            raise KeyError("Invalid operator " + op)
        if not ctx.get('dry_run', False):
            if op == "=~" and not re.match(result_val, test_value):
                print_flush(
                    "Test '%s' failed: value '%s' does not match '%s'"
                    % (msg, test_value, result_val)
                )
                ctx['successful'] = False
                if ctx.get('failfast'):
                    raise AssertionError
                else:
                    return TEST_FAILED
            elif op == "==" and test_value != result_val:  # pragma: no cover
                print_flush(
                    "Test '%s' failed: expected '%s', found '%s'"
                    % (msg, test_value, result_val)
                )
                ctx['successful'] = False
                if ctx.get('failfast'):
                    raise AssertionError
                else:
                    return TEST_FAILED
        return TEST_SUCCESS

    def test_failed(self, msg, first, second=None):
        print_flush(msg)
        print_flush("Value1='" + str(first) + "'")
        if second:
            print_flush("Value2='" + str(second) + "'")
        self.successful = False
        if self.failfast:
            raise AssertionError

    def assertTrue(self, expr, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if not bool(expr):
            self.test_failed(msg or "Invalid value <<%s>>!" % expr, expr)

    def assertFalse(self, expr, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if bool(expr):
            self.test_failed(msg or "Invalid value <<%s>>!" % expr, expr)

    def assertEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first != second:
            self.test_failed(
                msg or "Value <<%s>> is different from <<%s>>!" % (first, second),
                first, second)

    def assertNotEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first == second:
            self.test_failed(
                msg or "Value <<%s>> is equal to <<%s>>!" % (first, second),
                first, second)

    def assertIn(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first not in second:
            self.test_failed(
                msg or "Value <<%s>> is not in <<%s>>!" % (first, second),
                first, second)

    def assertNotIn(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first in second:
            self.test_failed(
                msg or "Value <<%s>> is in <<%s>>!" % (first, second),
                first, second)

    def assertLess(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first >= second:
            self.test_failed(
                msg or "Value <<%s>> is greater or equal to <<%s>>!" % (first, second),
                first, second)

    def assertLessEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first > second:
            self.test_failed(
                msg or "Value <<%s>> is greater than <<%s>>!" % (first, second),
                first, second)

    def assertGreater(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first <= second:
            self.test_failed(
                msg or "Value <<%s>> is less or equal to <<%s>>!" % (first, second),
                first, second)

    def assertGreaterEqual(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if first < second:
            self.test_failed(
                msg or "Value <<%s>> is less than <<%s>>!" % (first, second),
                first, second)

    def assertMatch(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if not re.match(second, first):
            self.test_failed(
                msg or "Value <<%s>> does not match <<%s>>!" % (first, second),
                first, second)

    def assertNotMatch(self, first, second, msg=None, msg_info=None):
        self.assert_counter += 1
        if msg_info:
            print_flush(("%d. " % self.assert_counter) + msg_info)
        if re.match(second, first):
            self.test_failed(
                msg or "Value <<%s>> matches <<%s>>!" % (first, second),
                first, second)

    def build_os_tree(self, *args):
        """Create a filesytem tree to test"""
        # Old version had the following signature: build_os_tree(self, ctx, os_tree)
        # Now param ctx is deprecated, so we have to analyze parameters
        os_tree = args[1] if len(args) == 2 else args[0]
        root = os.path.join(os.path.dirname(self.this_fqn), 'res')
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

    def remove_os_tree(self, *args):
        """Remove a filesytem tree created to test"""
        # Old version had the following signature: remove_os_tree(self, ctx, os_tree)
        # Now param ctx is deprecated, so we have to analyze parameters
        os_tree = args[1] if len(args) == 2 else args[0]
        root = os.path.join(os.path.dirname(self.this_fqn), 'res')
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
        if not argv and len(sys.argv) and not sys.argv[0].startswith('-'):
            self.this_fqn = os.path.abspath(sys.argv[0])
        self.this = os.path.splitext(os.path.basename(self.this_fqn))[0]
        self.this_dir = os.path.abspath(os.getcwd())
        if (
                not os.path.basename(self.this_dir) == 'tests'
                and not os.path.isdir(os.path.join(self.this_dir, 'tests'))
        ):
            self.this_dir = os.path.dirname(self.this_fqn)
        if os.path.basename(self.this_dir) == 'tests':
            self.testdir = self.this_dir
            self.rundir = os.path.dirname(self.this_dir)
        elif os.path.isdir('./tests'):                              # pragma: no cover
            self.testdir = os.path.join(self.this_dir, 'tests')
            self.rundir = self.this_dir
        else:                                                       # pragma: no cover
            self.testdir = self.rundir = self.this_dir

    def simulate_install_pypi(self, cmd):
        """Simulate pip post installation for"""
        PYCODE = r"""#!%(exec)s
import re
import sys
if sys.version_info[0] == 2:
    from %(pypi)s.scripts.%(cmd)s import main
else:
    from .%(pypi)s.scripts.%(cmd)s import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())"""
        params = {
            'exec': sys.executable,
            'cmd': os.path.splitext(cmd)[0],
            'pypi': os.path.basename(self.Z.rundir),
        }
        with open(os.path.join(self.Z.rundir, cmd), 'w') as fd:
            fd.write(_c(PYCODE % params))
            mode = os.fstat(fd.fileno()).st_mode
            mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.fchmod(fd.fileno(), stat.S_IMODE(mode))

    def get_outer_dir(self):
        """Get dir out of current virtual environment
        In local tests it serves to find local Odoo repositories to avoid
        git clone or wget from web.
        """
        outer_dir = os.environ.get('TRAVIS_BUILD_DIR', os.getcwd())
        if os.path.basename(outer_dir) == 'tests':
            outer_dir = os.path.abspath(os.path.join(outer_dir, '..', '..', '..', '..'))
        else:
            outer_dir = os.path.abspath(os.path.join(outer_dir, '..', '..', '..'))
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
                src_repo_path = os.path.join(outer_dir, '%s%s' % (reporg, odoo_ver))
                if os.path.isdir(src_repo_path):
                    found_path = True
                    break
                src_repo_path = os.path.join(outer_dir, '%s-%s' % (reporg, odoo_ver))
                if os.path.isdir(src_repo_path):
                    found_path = True
                    break
                if reponame == 'OCB':
                    continue
                for nm in ('', 'extra', 'private-addons', 'powerp'):
                    if nm:
                        src_repo_path = os.path.join(outer_dir, odoo_ver, nm, reporg)
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

    def build_odoo_env(self, ctx, version, hierarchy=None, name=None, retodoodir=None):
        """Build a simplified Odoo directory tree
        version: 16.0, 15.0, 14.0, 13.0, ..., 7.0, 6.1
        name: name of odoo dir (default equal to version)
        hierarchy: flat,tree,server (def=flat)
        """
        name = name or version
        if int(version.split(".")[0]) < 10:
            if hierarchy == 'server':
                odoo_home = os.path.join(name, 'server', 'openerp')
            else:
                odoo_home = os.path.join(name, 'openerp')
            script = 'openerp-server'
        else:
            if hierarchy == 'tree':
                odoo_home = os.path.join(name, 'odoo', 'odoo')
            else:
                odoo_home = os.path.join(name, 'odoo')
            script = 'odoo-bin'
        os_tree = [
            name,
            os.path.join(name, 'addons'),
            odoo_home,
            os.path.join(odoo_home, 'addons'),
            os.path.join(odoo_home, 'osv'),
            os.path.join(odoo_home, 'service'),
            os.path.join(odoo_home, 'tools'),
            os.path.join(name, '.git'),
        ]
        root = Z0test().build_os_tree(ctx, os_tree)
        RELEASE_PY = (
            """
RELEASE_LEVELS = [ALPHA, BETA, RELEASE_CANDIDATE, FINAL] = """
            """['alpha', 'beta', 'candidate', 'final']
RELEASE_LEVELS_DISPLAY = {ALPHA: ALPHA,
                          BETA: BETA,
                          RELEASE_CANDIDATE: 'rc',
                          FINAL: ''}
version_info = (%s, %s, 0, 'final', 0, '')
version = '.'.join(map(str, version_info[:2])) + """
            """RELEASE_LEVELS_DISPLAY[version_info[3]] + """
            """str(version_info[4] or '') + version_info[5]
series = serie = major_version = '.'.join(map(str, version_info[:2]))"""
        )
        if name[0] not in ('~', '/') and not name.startswith('./'):
            odoo_root = os.path.join(root, name)
        else:
            odoo_root = name
        odoo_home = os.path.join(os.path.dirname(odoo_root), odoo_home)
        with open(os.path.join(odoo_home, 'release.py'), 'w') as fd:
            versions = version.split('.')
            fd.write(RELEASE_PY % (versions[0], versions[1]))
        for fn in ("osv", "service", "tools"):
            with open(os.path.join(odoo_home, fn, "__init__.py"), 'w') as fd:
                fd.write('print("Fake Odoo")\n')
        init_py = ""
        for fn in (script, "models.py", "fields.py", "api.py"):
            if fn == "api.py" and (version.startswith("6") or version.startswith("7")):
                continue
            if fn == script:
                ffn = os.path.join(os.path.dirname(odoo_home), fn)
                for fn2 in ("release", "osv", "service", "tools"):
                    init_py += "import %s\n" % fn2
            else:
                ffn = os.path.join(odoo_home, fn)
                init_py += "import %s\n" % fn[:-3]
            with open(ffn, 'w') as fd:
                fd.write('print("Fake Odoo")\n')
                if fn == script:
                    mode = os.fstat(fd.fileno()).st_mode
                    mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    os.fchmod(fd.fileno(), stat.S_IMODE(mode))
        with open(os.path.join(odoo_home, "__init__.py"), 'w') as fd:
            fd.write(init_py)
        with open(os.path.join(odoo_root, '.travis.yml'), 'w') as fd:
            fd.write('\n')
        with open(os.path.join(odoo_root, 'README.rst'), 'w') as fd:
            fd.write('This directory is a fake, just for test!\n')
        if retodoodir:
            return odoo_root
        return root

    def create_repo(
        self, ctx, root, reponame, version, hierarchy=None, name=None, repotype=None
    ):
        REPOTYPES = {
            'oca': {'d': ['.git'], 'f': ['README.md', '.travis.yml']},
            'zero': {'d': ['egg-info', '.git'], 'f': ['README.rst', '.travis.yml']},
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

    def create_module(
        self, ctx, repo_root, name, version, moduletype=None, dependencies=None
    ):
        MODULETYPES = {'simple': {'d': [], 'f': ['__init__.py']}}
        moduletype = moduletype or 'simple'
        moduledir = os.path.join(repo_root, name)
        if not os.path.isdir(moduledir):
            os.mkdir(moduledir)
        majver = int(version.split('.')[0])
        if majver < 10:
            ffn = os.path.join(moduledir, '__openerp__.py')
            ffn_del = os.path.join(moduledir, '__manifest__.py')
        else:
            ffn = os.path.join(moduledir, '__manifest__.py')
            ffn_del = os.path.join(moduledir, '__openerp__.py')
        with open(ffn, 'w', encoding="utf-8") as fd:
            fd.write(
                text(
                    {
                        'name': name,
                        'version': version,
                        'summary': 'This module is a fake, just for test!',
                        'depends': dependencies if dependencies else [],
                    }
                )
            )
        if os.path.isfile(ffn_del):
            os.unlink(ffn_del)
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
        os.system('git clone --depth=50 %s -b %s %s' % (odoo_url, branch, odoo_path))
        os.system(
            'git --work-tree=%s --git-dir=%s/.git remote rename origin %s'
            % (odoo_path, odoo_path, remote)
        )

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
                            src_path,
                            dst_path,
                            symlinks=True,
                            ignore=shutil.ignore_patterns('*.pyc', '.idea/', 'setup/'),
                        )
                for nm in (
                    '.travis.yml',
                    'odoo-bin',
                    'openerp-server',
                    'openerp-wsgi.py',
                    'requirements.txt',
                ):
                    src_path = os.path.join(src_repo_path, nm)
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, odoo_path)
            else:
                shutil.copytree(
                    src_repo_path,
                    os.path.join(odoo_path, reponame),
                    symlinks=True,
                    ignore=shutil.ignore_patterns('*.pyc', '.idea/', 'setup/'),
                )

