#!/home/odoo/devel/venv/bin/python3.8
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2024 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys

from z0lib import z0lib
from zerobug import z0test, z0testodoo


__version__ = "2.0.15"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def setup(self):
        # super(RegressionTest, self).setup()
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.path.join(os.getcwd(), "tests")
            self.rundir = os.getcwd()
        self.odoo_testdir = os.path.join(self.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.rundir, "do_git_checkout_new_branch.py")
        )

    def find_cmd_in_stdout(self, cmd, stdout):
        self.assertMatch(stdout.replace("\n", " "), ".*" + cmd,
                         msg="Cmd <<<%s>>> not found!" % cmd)

    def test_01_version(self):
        sts, stdout, stderr = z0lib.run_traced(
            "do_git_checkout_new_branch --version")
        self.assertEqual(sts, 0, msg_info="do_git_checkout_new_branch.py --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02_checkout(self):
        zero_vid = "16.0"
        oca_vid = "oca16"
        full_version = "16.0.1.0.0"
        version = full_version.rsplit(".", 3)[0]
        # build_odoo_env accepts only version, so we create hierarchy and then rename it
        self.root = z0testodoo.build_odoo_env({}, version)
        oca_root = os.path.join(self.root, oca_vid)
        os.rename(os.path.join(self.root, version), oca_root)
        z0testodoo.create_module(
            {}, os.path.join(oca_root, "odoo", "addons"), "base", full_version
        )
        repodir = z0testodoo.create_repo(
            {}, oca_root, "l10n-italy", version
        )
        z0testodoo.create_module(
            {}, repodir, "l10n_account", full_version
        )
        cmd = "do_git_checkout_new_branch -nv -b%s -Gzero -p %s -o %s" % (
            version, os.path.join(self.root, zero_vid), oca_root)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)

        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/OCB.git",
            stdout)
        self.find_cmd_in_stdout(
            "git checkout -b 16.0",
            stdout)
        self.find_cmd_in_stdout(
            "rsync -avz --delete .*",
            stdout)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



