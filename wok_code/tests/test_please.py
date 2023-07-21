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

from z0lib import z0lib
from zerobug import z0test, z0testodoo


__version__ = "2.0.11"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.root = ''

    def _touch_file(self, fn):
        if not os.path.isfile(fn):
            with open(fn, "w") as fd:
                fd.write("# Fake\n")

    def test_01(self, z0ctx):
        cmd = "please --version"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(z0ctx, cmd, __version__, (stdout + stderr).split("\n")[0])

        cmd = "please"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd,
            True,
            "please is an interactive developers shell aims to help" in stdout,
        )

        cmd = "please help"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd,
            True,
            "please is an interactive developers shell aims to help" in stdout,
        )

        cmd = "please help z0bug"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(z0ctx, cmd, True, " please test" in stdout)

        cmd = "please -h"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, cmd, True, "2015-2023 by SHS-AV s.r.l." in (stdout + stderr)
        )

        cmd = "please z0bug -h"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, cmd, True, "-T REGEX, --trace REGEX" in (stdout + stderr)
        )
        return sts

    def test_02(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please z0bug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis emulate -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.tool_pkgdir)
        cmd = "please zerobug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis emulate -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.pypi_dir)
        cmd = "please zerobug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis emulate -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please zerobug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "pre-commit run" in stdout.split("\n")[0],
        )
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "please.sh lint -vn" in stdout.split("\n")[1],
        )
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "please.sh test -vn" in stdout.split("\n")[2],
        )
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "please.sh translate -vn" in stdout.split("\n")[3],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please zerobug -vn --no-verify --no-translate"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "please.sh lint -vn" in stdout.split("\n")[0],
        )
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True,
            "please.sh test -vn" in stdout.split("\n")[1],
        )
        return sts

    def test_03(self, z0ctx):
        cmd = "please create apache erp.example.com -qn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd,
            "File ~/erp.example.com.conf will be created",
            stdout.split("\n")[0],
        )

        os.chdir(self.pypi_dir)
        cmd = "please defcon gitignore -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            ".gitignore should be updated/created" in stdout.split("\n")[0],
        )

        os.chdir(self.odoo_repodir)
        cmd = "please defcon gitignore -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            ".gitignore should be updated/created" in stdout.split("\n")[0],
        )

        os.chdir(self.pypi_dir)
        cmd = "please defcon precommit -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            ".pre-commit-config.yaml should be updated/created" in stdout.split("\n")[0]
        )

        os.chdir(self.odoo_repodir)
        cmd = "please defcon precommit -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            ".pre-commit-config.yaml should be updated/created" in stdout.split("\n")[0]
        )
        return sts

    def test_04(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        with open("please.py~", "w") as fd:
            fd.write("# Fake file\n")
        cmd = "please clean -vn"
        target_file = os.path.join(os.getcwd(), "please.py~")
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> rm -f " + target_file,
            stdout.split("\n")[0],
        )

        cmd = "please clean -v"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "$ rm -f " + target_file,
            stdout.split("\n")[0],
        )
        self.Z.test_result(z0ctx, cmd, False, os.path.isfile(target_file))
        return sts

    def test_05(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis test -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.pypi_dir)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis test -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "/please.sh test -vn" in stdout.split("\n")[2],
        )
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "/please.sh translate -vn" in stdout.split("\n")[3],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please test -vn --no-translate"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "/please.sh test -vn" in stdout.split("\n")[2],
        )
        return sts

    def test_06(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis lint -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.pypi_dir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            "> travis lint -vn",
            stdout.split("\n")[0],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "> pre-commit run" in stdout.split("\n")[0],
        )
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "/please.sh lint -vn" in stdout.split("\n")[1],
        )

        os.chdir(self.odoo_moduledir)
        cmd = "please lint -vn --no-verify"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "/please.sh lint -vn" in stdout.split("\n")[0],
        )
        return sts

    def _test_07(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please show -n"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), "> travis show", stdout.split("\n")[0]
        )

        os.chdir(self.pypi_dir)
        cmd = "please show -n"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), "> travis show", stdout.split("\n")[0]
        )

        os.chdir(self.odoo_moduledir)
        fn = os.path.join(self.odoo_moduledir, "tests", "logs", "show-log.sh")
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True, fn in stdout.split("\n")[0]
        )
        return sts

    def test_08(self, z0ctx):
        os.chdir(self.pypi_dir)
        cmd = "please replace -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx, "%s> %s" % (os.getcwd(), cmd), True, "> rsync -a " in stdout
        )

        os.chdir(self.pypi_dir)
        cmd = "please update -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            self.Z.test_result(z0ctx, cmd, 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "%s> %s" % (os.getcwd(), cmd),
            True,
            "> vem " in stdout.split("\n")[0],
        )
        return sts

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "please.py")
        )
        if not z0ctx['dry_run']:
            self.tool_pkgdir = os.path.expanduser("~/tools/wok_code")

            devel_root = os.path.expanduser("~/devel")
            self.Z.build_os_tree(
                z0ctx,
                [
                    devel_root,
                    os.path.join(devel_root, "pypi"),
                    os.path.join(devel_root, "pypi", ".git"),
                    os.path.join(devel_root, "pypi", "wok_code"),
                    os.path.join(devel_root, "pypi", "wok_code", "wok_code"),
                ],
            )
            self.pypi_dir = os.path.join(devel_root, "pypi", "wok_code", "wok_code")
            self._touch_file(os.path.join(devel_root, "pypi", "wok_code", "setup.py"))
            self._touch_file(os.path.join(devel_root, "pypi", "wok_code", "README.rst"))
            self._touch_file(
                os.path.join(devel_root, "pypi", "wok_code", "wok_code", "__init__.py")
            )

            self.odoo_root = z0testodoo.build_odoo_env(z0ctx, "12.0")
            self.odoo_repodir = z0testodoo.create_repo(
                z0ctx,
                self.odoo_root,
                'test_repo',
                "12.0",
            )
            self.odoo_moduledir = z0testodoo.create_module(
                z0ctx, self.odoo_repodir, 'test_module', "12.0"
            )
            if not os.path.isdir(os.path.join(self.odoo_moduledir, "tests")):
                os.mkdir(os.path.join(self.odoo_moduledir, "tests"))
            if not os.path.isdir(os.path.join(self.odoo_moduledir, "tests", "logs")):
                os.mkdir(os.path.join(self.odoo_moduledir, "tests", "logs"))
            self._touch_file(
                os.path.join(self.odoo_moduledir, "tests", "logs", "show-log.sh")
            )

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
