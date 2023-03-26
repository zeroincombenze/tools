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
from zerobug import z0test


__version__ = "2.0.6"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.root = ''

    def test_01(self, z0ctx):
        sts, stdout, stderr = z0lib.run_traced("do_migrate --version")
        if sts:
            self.Z.test_result(
                z0ctx, "do_migrate --version", 0, sts)
            return sts
        self.Z.test_result(z0ctx, "do_migrate --version", __version__,
                           (stdout + stderr).split("\n")[0])
        return sts

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "do_migrate.py"))

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
