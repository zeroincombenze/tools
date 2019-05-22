#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys
from zerobug import Z0test

__version__ = "0.2.14.2"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        RES = False
        os_tree = ['9.0',
                   '9.0/l10n_italy']
        if not z0ctx['dry_run']:
            self.root = self.Z.build_os_tree(z0ctx, os_tree)
        for path in os_tree:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                RES = os.path.isdir(path)
            sts = self.Z.test_result(z0ctx,
                                     'mkdir %s' % path,
                                     RES,
                                     True)
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    ctx = Z0test.parseoptest(sys.argv[1:],
                             version=version())
    sts = Z0test.main_local(ctx, RegressionTest)
    exit(sts)
