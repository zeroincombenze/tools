#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import os.path as pth
import sys


# allow using isolated test environment
def pkg_here(here):
    while (
        pth.basename(here) in ("tests", "scripts")
        or pth.basename(pth.dirname(here)) == "local"
    ):
        here = pth.dirname(here)
    if here not in sys.path:
        sys.path.insert(0, here)


pkg_here(pth.dirname(pth.abspath(__file__)))  # noqa: E402
pkg_here(pth.abspath(os.getcwd()))  # noqa: E402
from z0lib import z0lib  # noqa: E402
# from z0lib.scripts.main import get_metadata  # noqa: E402
from zerobug import z0test  # noqa: E402

__version__ = "2.0.14"

MODULE_ID = "z0lib"
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def run_test_cmd(self, cmd, test_sts):
        sts, stdout, stderr = z0lib.run_traced(cmd, verbose=False)
        self.assertEqual(test_sts, sts, msg_info=cmd)
        if sts == 0 and cmd.startswith('ls ') or cmd == "ls":
            self.assertTrue(len(stdout) > 0)

    def run_os_system(self, cmd, test_sts):
        sts = z0lib.os_system(cmd, verbose=False)
        self.assertEqual(test_sts, sts, msg_info=cmd)

    def test_01(self):
        # self.assertEqual(__version__, get_metadata()["version"])
        if os.getenv("TRAVIS_PYTHON_VERSION"):
            self.assertEqual(
                os.getenv("TRAVIS_PYTHON_VERSION"),
                "%d.%d" % (sys.version_info[0], sys.version_info[1]))

        self.run_test_cmd("true", 0)
        self.run_test_cmd("false", 1)
        self.run_test_cmd("NOT_EXIST", 127)
        fn = os.path.join(self.Z.testdir, "NOT_EXIST")
        if os.path.isfile(fn):
            os.unlink(fn)
        self.run_test_cmd("touch %s" % fn, 0)
        self.assertTrue(os.path.isfile(fn), msg="touched %s" % fn)
        self.run_test_cmd("rm -f %s" % fn, 0)
        self.assertFalse(os.path.isfile(fn), msg="removed %s" % fn)
        self.run_test_cmd("cd %s" % fn, 1)
        self.run_test_cmd("ls", 0)
        self.run_test_cmd("mkdir %s" % fn, 0)
        self.assertTrue(os.path.isdir(fn), msg="dir %s created" % fn)
        self.run_test_cmd("rm -fR %s" % fn, 0)
        self.assertFalse(os.path.isdir(fn), msg="dir %s removed" % fn)

    def test_02(self):
        fn = os.path.expanduser("~/16.0")
        if os.path.isdir(fn):
            os.system("rm -fR %s" % fn)
        self.run_test_cmd("mkdir %s" % fn, 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "addons"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "odoo"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "odoo", "addons"), 0)
        self.run_test_cmd("touch %s" % os.path.join(fn, "odoo", "release.py"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, ".git"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "repo1"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "repo1", ".git"), 0)
        self.run_test_cmd("mkdir %s" % os.path.join(fn, "repo1", "module_a"), 0)
        sts, stdout, stderr = z0lib.run_traced(
            "git clone https://github.com/zeroincombenze/OCB.git %s -b16.0" % (
                self.Z.testdir),
            verbose=False)
        tgtfn = os.path.join(self.Z.testdir, "16.0")
        self.assertTrue(os.path.isdir(tgtfn), msg="dir %s created" % tgtfn)
        fn = os.path.join(tgtfn, "addons")
        self.assertTrue(os.path.isdir(fn), msg="dir %s created" % fn)
        fn = os.path.join(tgtfn, "odoo")
        self.assertTrue(os.path.isdir(fn), msg="dir %s created" % fn)
        fn = os.path.join(tgtfn, "odoo", "addons")
        self.assertTrue(os.path.isdir(fn), msg="dir %s created" % fn)
        fn = os.path.join(tgtfn, "odoo", "release.py")
        self.assertTrue(os.path.isfile(fn), msg="file %s created" % fn)
        fn = os.path.join(tgtfn, "repo1")
        self.assertFalse(os.path.isdir(fn), msg="dir %s not created" % fn)

    def test_03(self):
        self.run_os_system("true", 0)
        self.run_os_system("false", 1)
        self.run_os_system("NOT_EXIST", 127)
        fn = os.path.join(self.Z.testdir, "NOT_EXIST")
        if os.path.isfile(fn):
            os.unlink(fn)
        self.run_os_system("touch %s" % fn, 0)
        self.assertTrue(os.path.isfile(fn), msg="touched %s" % fn)
        self.run_os_system("rm -f %s" % fn, 0)
        self.assertFalse(os.path.isfile(fn), msg="removed %s" % fn)
        self.run_test_cmd("cd %s" % fn, 1)
        self.run_test_cmd("ls", 0)
        self.run_os_system("mkdir %s" % fn, 0)
        self.assertTrue(os.path.isdir(fn), msg="dir %s created" % fn)
        self.run_os_system("rm -fR %s" % fn, 0)
        self.assertFalse(os.path.isdir(fn), msg="dir %s removed" % fn)

    def test_04(self):
        cmd = "ls|grep test"
        sts, stdout, stderr = z0lib.run_traced(cmd, verbose=False)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertTrue(len(stdout.split("\n")) > 1)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
