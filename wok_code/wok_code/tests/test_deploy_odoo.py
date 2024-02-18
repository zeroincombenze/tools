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
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "deploy_odoo.py")
        )

    def find_cmd_in_stdout(self, cmd, stdout):
        self.assertMatch(stdout.replace("\n", " "), ".*" + cmd,
                         msg="Cmd <<<%s>>> not found!" % cmd)

    def test_01_version(self):
        sts, stdout, stderr = z0lib.run_traced("deploy_odoo --version")
        self.assertEqual(sts, 0, msg_info="deploy_odoo --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02_clone_oca(self):
        cmd = "deploy_odoo -mnv -b16.0 -Goca -p %s clone -r %s" % (
            os.path.join(self.odoo_testdir, "oca16"),
            "OCB,crm,l10n-italy,web")
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone https://github.com/odoo/odoo.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout)
        self.find_cmd_in_stdout(
            "OCB +unstaged +16.0 +odoo +https://github.com/odoo/odoo.git",
            stdout)
        self.find_cmd_in_stdout(
            "git clone https://github.com/OCA/crm.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout)
        self.find_cmd_in_stdout(
            "crm +unstaged +16.0 +oca +https://github.com/OCA/crm.git",
            stdout)
        self.find_cmd_in_stdout(
            "git clone https://github.com/OCA/l10n-italy.git .* -b 16.0"
            " --depth=1 --single-branch",
            stdout)
        self.find_cmd_in_stdout(
            "l10n-italy +unstaged +16.0"
            " +oca +https://github.com/OCA/l10n-italy.git",
            stdout)

    def test_03_clone_zero(self):
        cmd = "deploy_odoo -Kmnv -b16.0 -gGzero -p %s clone -r %s" % (
            os.path.join(self.odoo_testdir, "16.0"),
            "OCB,crm,l10n-italy,web")
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/OCB.git .* -b 16.0",
            stdout)
        self.find_cmd_in_stdout(
            "OCB +unstaged +16.0"
            " +zeroincombenze +git@github.com:zeroincombenze/OCB.git",
            stdout)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/crm.git .* -b 16.0",
            stdout)
        self.find_cmd_in_stdout(
            "crm +unstaged +16.0"
            " +zeroincombenze +git@github.com:zeroincombenze/crm.git",
            stdout)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/l10n-italy.git .* -b 16.0",
            stdout)
        self.find_cmd_in_stdout(
            "l10n-italy +unstaged +16.0"
            " +zeroincombenze +git@github.com:zeroincombenze/l10n-italy.git",
            stdout)

    def test_03_update(self):
        self.root = z0testodoo.build_odoo_env({}, "16.0")
        odoo_root = os.path.join(self.root, "16.0")
        z0testodoo.create_module(
            {}, os.path.join(odoo_root, "odoo", "addons"), "base", "16.0.0.1.0"
        )
        repodir = z0testodoo.create_repo(
            {}, odoo_root, "crm", "16.0"
        )
        z0testodoo.create_module(
            {}, repodir, "crm_test", "16.0.0.1.0"
        )
        cmd = "deploy_odoo -nv -b16.0 -gGzero -p %s update" % odoo_root
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            " cd %s.*git branch.*git remote.*git pull" % odoo_root,
            stdout)

    def test_04_amend(self):
        odoo_root = os.path.join(self.root, "16.0")
        cmd = ("deploy_odoo -Kmnv -b16.0 -gGzero -p %s amend -r OCB,crm,l10n-italy,web"
               % odoo_root)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.find_cmd_in_stdout(
            "git clone git@github.com:zeroincombenze/l10n-italy.git l10n-italy/",
            stdout)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



