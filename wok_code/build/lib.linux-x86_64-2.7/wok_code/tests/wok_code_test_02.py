#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
from zerobug import z0test


__version__ = "2.0.0"

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
        # sts = 0
        # home = os.path.expanduser('~')
        cmd = os.path.join(self.Z.rundir, 'do_migrate')
        os.system('%s -V' % cmd)

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
