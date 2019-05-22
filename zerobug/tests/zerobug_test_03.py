#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import sys
from zerobug import Z0test

__version__ = "0.2.14.2"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        if z0ctx['dry_run']:
            # sts = TEST_SUCCESS
            sts = self.Z.sanity_check('-q', full=z0ctx)
            ctx['ctr'] = 46
        else:
            sts = self.Z.sanity_check('-e', full=z0ctx)
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_file(ctx, RegressionTest)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
