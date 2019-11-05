#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys
from zerobug import Z0BUG

__version__ = "0.1.0.7"

MODULE_ID = 'odoo_score'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0BUG.main(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))