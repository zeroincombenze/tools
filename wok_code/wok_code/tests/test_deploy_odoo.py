#!/home/odoo/devel/venv/bin/python3.8
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import re
import sys

from z0lib import z0lib
from zerobug import z0test


__version__ = "2.0.21"

MODULE_ID = "wok_code"
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def setup(self):
        # super(, self).setup()
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.path.join(os.getcwd(), "tests")
            self.rundir = os.getcwd()
        self.odoo_testdir = os.path.join(self.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)
        z0lib.os_system(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "deploy_odoo.py")
        )

    def find_cmd_in_stdout(self, cmd, stdout):
        self.assertTrue(
            re.search(".*" + cmd, stdout, re.MULTILINE | re.DOTALL),
            msg="Cmd <<<%s>>> not found!" % cmd,
        )

    def test_01_version(self):
        sts, stdout, stderr = z0lib.os_system_traced(
            "deploy_odoo --version", rtime=False
        )
        self.assertEqual(sts, 0, msg_info="deploy_odoo --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02_clone_oca(self):
        # Create repository oca16
        git_dir = os.path.join(self.odoo_testdir, "oca16")
        cmd = "deploy_odoo clone -mTv -b16.0 -Goca -p %s -r %s" % (
            git_dir,
            "OCB,crm,l10n-italy,web",
        )
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone https://github.com/odoo/odoo.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout,
        )
        self.find_cmd_in_stdout(
            "git clone https://github.com/OCA/crm.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout,
        )
        self.find_cmd_in_stdout(
            "git clone https://github.com/OCA/l10n-italy.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout,
        )
        self.find_cmd_in_stdout(
            "git clone https://github.com/OCA/web.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout,
        )
        self.find_cmd_in_stdout("odoo +16.0 +odoo", stdout)
        self.find_cmd_in_stdout("crm +16.0 +oca", stdout)
        self.find_cmd_in_stdout("l10n-italy +16.0 +oca", stdout)
        self.find_cmd_in_stdout("web +16.0 +oca", stdout)

    def test_03_clone_zero(self):
        # create repo 16.0 (zero) w/o l10n-italy
        git_dir = os.path.join(self.odoo_testdir, "16.0")
        cmd = "deploy_odoo clone -KmTv -b16.0 -gGzero -p %s -r %s" % (
            git_dir,
            "OCB,crm,web",
        )
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/OCB.git .* -b 16.0", stdout
        )
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/crm.git .* -b 16.0", stdout
        )
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/web.git .* -b 16.0", stdout
        )
        self.find_cmd_in_stdout("OCB +16.0 +zero", stdout)
        self.find_cmd_in_stdout("crm +16.0 +zero", stdout)
        self.find_cmd_in_stdout("web +16.0 +zero", stdout)

    def test_04_amend(self):
        git_dir = os.path.join(self.odoo_testdir, "16.0")
        cmd = (
            "deploy_odoo amend -KmTv -b16.0 -gGzero -p %s -r OCB,crm,l10n-italy,web"
            % git_dir
        )
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/l10n-italy.git .* -b 16.0", stdout
        )
        self.find_cmd_in_stdout("l10n-italy +16.0 +zero", stdout)

    def test_05_update(self):
        git_dir = os.path.join(self.odoo_testdir, "16.0")
        cmd = "deploy_odoo update -Tv -b16.0 -gGzero -p %s" % git_dir
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(" cd %s.*git pull origin 16.0" % git_dir, stdout)

    def test_06_checkout(self):
        git_dir = os.path.join(self.odoo_testdir, "oca16")
        new_dir = os.path.join(self.odoo_testdir, "17.0")
        cmd = "deploy_odoo new-branch -mTv -b%s -gGzero -p %s -o %s" % (
            "17.0",
            new_dir,
            git_dir,
        )
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/OCB.git", stdout
        )
        self.find_cmd_in_stdout("please defcon gitignore", stdout)
        self.find_cmd_in_stdout("please defcon precommit", stdout)
        self.find_cmd_in_stdout("git remote add upstream", stdout)
        self.find_cmd_in_stdout("git checkout -b 17.0", stdout)
        self.find_cmd_in_stdout("rsync -avz --delete --exclude.*", stdout)
        self.find_cmd_in_stdout("cp .*/odoo-bin", stdout)
        self.find_cmd_in_stdout("OCB +17.0 +zero", stdout)
        self.find_cmd_in_stdout("crm +17.0 +zero", stdout)
        self.find_cmd_in_stdout("l10n-italy +17.0 +zero", stdout)
        self.find_cmd_in_stdout("web +17.0 +zero", stdout)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
