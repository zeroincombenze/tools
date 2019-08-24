#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys
from zerobug import Z0BUG

__version__ = "0.1.0.1.1"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug
        self.os_tree = ['10.0',
                        '10.0/l10n-italy',
                        '10.0/l10n-italy/l10n_it_base',
                        '/tmp/zerobug']

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        RES = False
        if not z0ctx['dry_run']:
            self.root = self.Z.build_os_tree(z0ctx, self.os_tree)
        for path in self.os_tree:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                RES = os.path.isdir(path)
            sts = self.Z.test_result(z0ctx,
                                     'mkdir %s' % path,
                                     RES,
                                     True)
        return sts

    def test_09(self, z0ctx):
        sts = TEST_SUCCESS
        RES = False
        if not z0ctx['dry_run']:
            self.Z.remove_os_tree(z0ctx, self.os_tree)
        for path in self.os_tree:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                RES = os.path.isdir(path)
            sts = self.Z.test_result(z0ctx,
                                     'rmdir %s' % path,
                                     RES,
                                     False)
        return sts

#
# Run main if executed as a script
if __name__ == "__main__":
    ctx = Z0BUG.parseoptest(sys.argv[1:],
                             version=version())
    sts = Z0BUG.main_local(ctx, RegressionTest)
    exit(sts)