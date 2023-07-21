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
import re

from z0lib import z0lib
from zerobug import z0test, z0testodoo


__version__ = "2.0.11"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0
VERSIONS_TO_TEST = ("14.0", "13.0", "12.0", "10.0", "8.0", "7.0", "6.1")
MAJVERS_TO_TEST = (14, 13, 12, 10, 8, 7, 6)
SUB_TO_TEST = ("v", "V", "VENV-", "odoo", "odoo_", "ODOO", "OCB-",
               "oca", "librerp", "VENV_123-", "devel")


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug

    def run_odoo_test(self, vid):
        os.putenv("ODOO_GIT_ORGID", "zero")
        os.putenv("ODOO_GIT_SHORT", "(oca|librerp)")
        os.putenv("ODOO_DB_USER", "")
        cmd = "run_odoo_debug -b%s -vn" % vid
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Return status %s executing %s" % (sts, cmd))
            print(stderr)
        return sts, stdout, stderr

    def test_01(self, z0ctx):
        sts, stdout, stderr = z0lib.run_traced("run_odoo_debug --version")
        if sts:
            self.Z.test_result(z0ctx, "run_odoo_debug --version", 0, sts)
            return sts
        self.Z.test_result(
            z0ctx,
            "run_odoo_debug --version",
            __version__,
            (stdout + stderr).split("\n")[0]
        )
        return sts

    def test_02(self, z0ctx):
        sts = 0
        for version in VERSIONS_TO_TEST:
            maj_version = int(version.split(".")[0])
            for sub in SUB_TO_TEST:
                if sub == "librerp" and version in ("12.0", "6.1"):
                    continue
                elif sub.startswith("VENV") and version == "6.1":
                    continue
                if sub == "devel":
                    vid = version + "-" + sub
                elif sub in ("odoo", "odoo_", "ODOO", "OCB-", "oca", "librerp"):
                    vid = "%s%d" % (sub, maj_version)
                else:
                    vid = sub + version
                if not z0ctx["dry_run"]:
                    if re.match("VENV", vid):
                        z0testodoo.build_odoo_env(
                            z0ctx, version, name=os.path.expanduser("~/%s/odoo" % vid))
                    elif re.search("v7|v6", vid):
                        z0testodoo.build_odoo_env(
                            z0ctx, version,
                            name=os.path.expanduser("~/%s" % vid),
                            hierarchy="server",
                        )
                    else:
                        z0testodoo.build_odoo_env(
                            z0ctx, version, name=os.path.expanduser("~/%s" % vid))
                if re.search("v7|v6", vid):
                    TRES = "~/%s/server/openerp-server"
                elif re.match("VENV", vid) and maj_version == 6:
                    TRES = "~/%s/odoo/server/openerp-server"
                elif re.match("VENV", vid) and maj_version < 10:
                    TRES = "~/%s/odoo/openerp-server"
                elif re.match("VENV", vid) and maj_version >= 10:
                    TRES = "~/%s/odoo/odoo-bin"
                elif maj_version < 10:
                    TRES = "~/%s/openerp-server"
                else:
                    TRES = "~/%s/odoo-bin"
                # TRES = TRES.replace("~", self.Z.testdir)
                TRES = os.path.expanduser(TRES % vid)
                cmd = "run_odoo_debug -b%s -vn" % vid
                sts, stdout, stderr = self.run_odoo_test(vid)
                sts = self.Z.test_result(
                    z0ctx,
                    cmd,
                    None,
                    re.search("File .*no.*(exist|esistente)", (stdout + stderr)),
                )
                if sts:
                    return sts
                sts = self.Z.test_result(
                    z0ctx,
                    cmd,
                    True,
                    bool(re.search("cd.*/%s.*%s.*--config" % (vid, TRES),
                                   stdout.replace("\n", " "))),
                )
                if sts:
                    return sts
        return sts

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir,
                                          "scripts",
                                          "run_odoo_debug.py")
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
