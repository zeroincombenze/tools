# -*- coding: utf-8 -*-
# Copyright (C) 2018-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
# import os
import sys

from zerobug import z0test

__version__ = '2.0.7'

MODULE_ID = 'odoo_score'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.Z.inherit_cls(self)

    def test_01(self, z0ctx):
        self.assertTrue(True, msg_info="Test")
        return self.ret_sts()


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )

