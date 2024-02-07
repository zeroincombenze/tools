#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
from zerobug import z0test
from z0lib import z0lib

__version__ = "2.0.9"

MODULE_ID = 'z0lib'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug

    def run_test_cmd(self, ctx, cmd):
        if ctx.get('dry_run', False):
            return 0
        sts, stdout, stderr = z0lib.run_traced(cmd, verbose=False)
        if cmd == 'false' or (cmd.startswith("cd") and "NOT_EXIST" in cmd):
            sts = 1 - sts
        elif cmd == "NOT_EXIST":
            sts = 127 - sts
        sts = self.Z.test_result(ctx, 'run_traced(%s)' % cmd, 0, sts)
        if sts == 0:
            if cmd.startswith('ls ') or cmd == "ls":
                sts = self.Z.test_result(ctx, 'result %s' % cmd, True, len(stdout) > 0)
        return sts

    def test_01(self, z0ctx):
        sts = self.Z.test_result(z0ctx,
                                 'python version',
                                 os.getenv("TRAVIS_PYTHON_VERSION"),
                                 "%d.%d" % (sys.version_info[0], sys.version_info[1]))
        sts += self.run_test_cmd(z0ctx, "true")
        sts += self.run_test_cmd(z0ctx, "false")
        sts += self.run_test_cmd(z0ctx, "NOT_EXIST")
        fn = os.path.join(self.Z.testdir, "NOT_EXIST")
        if os.path.isfile(fn):
            os.unlink(fn)
        sts += self.run_test_cmd(z0ctx, "touch %s" % fn)
        sts += self.Z.test_result(z0ctx, 'touched %s' % fn, True, os.path.isfile(fn))
        sts += self.run_test_cmd(z0ctx, "rm -f %s" % fn)
        sts += self.Z.test_result(
            z0ctx, 'removed %s' % fn, True, not os.path.isfile(fn))
        sts += self.run_test_cmd(z0ctx, "cd %s" % fn)
        sts += self.run_test_cmd(z0ctx, "ls")
        sts += self.run_test_cmd(z0ctx, "mkdir %s" % fn)
        sts += self.Z.test_result(
            z0ctx, 'dir %s created' % fn, True, os.path.isdir(fn))
        sts += self.run_test_cmd(z0ctx, "rm -fR %s" % fn)
        sts += self.Z.test_result(
            z0ctx, 'dir %s removed' % fn, True, not os.path.isdir(fn))
        return sts

    def test_02(self, z0ctx):
        fn = os.path.expanduser("~/16.0")
        if os.path.isdir(fn):
            os.system("rm -fR %s" % fn)
        self.run_test_cmd(z0ctx, "mkdir %s" % fn)
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "addons"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "odoo"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "odoo", "addons"))
        self.run_test_cmd(z0ctx, "touch %s" % os.path.join(fn, "odoo", "release.py"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, ".git"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "repo1"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "repo1", ".git"))
        self.run_test_cmd(z0ctx, "mkdir %s" % os.path.join(fn, "repo1", "module_a"))
        sts, stdout, stderr = z0lib.run_traced(
            "git clone https://github.com/zeroincombenze/OCB.git %s -b16.0" % (
                self.Z.testdir),
            verbose=False)
        tgtfn = os.path.join(self.Z.testdir, "16.0")
        sts += self.Z.test_result(
            z0ctx, 'dir %s created' % tgtfn, True, os.path.isdir(tgtfn))
        sts += self.Z.test_result(
            z0ctx, 'dir %s created' % os.path.join(tgtfn, "addons"),
            True,
            os.path.isdir(os.path.join(tgtfn, "addons")))
        sts += self.Z.test_result(
            z0ctx, 'dir %s created' % os.path.join(tgtfn, "odoo"),
            True,
            os.path.isdir(os.path.join(tgtfn, "odoo")))
        sts += self.Z.test_result(
            z0ctx, 'dir %s created' % os.path.join(tgtfn, "odoo", "addons"),
            True,
            os.path.isdir(os.path.join(tgtfn, "odoo", "addons")))
        sts += self.Z.test_result(
            z0ctx, 'file %s created' % os.path.join(tgtfn, "odoo", "release.py"),
            True,
            os.path.isfile(os.path.join(tgtfn, "odoo", "release.py")))
        sts += self.Z.test_result(
            z0ctx, 'dir %s not created' % os.path.join(tgtfn, "repo1"),
            False,
            os.path.isdir(os.path.join(tgtfn, "repo1")))

    def setup(self, z0ctx):
        pass

    def tearoff(self, z0ctx):
        pass


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



