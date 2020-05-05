#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function,unicode_literals
from past.builtins import basestring

# import pdb
import os
import sys
from zerobug import Z0BUG
from zerobug import Z0testOdoo

__version__ = "0.2.14.17"

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
        if not z0ctx['dry_run']:
            self.root = Z0testOdoo.build_odoo_env(z0ctx, '10.0')
        for path in self.os_tree:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                RES = os.path.isdir(path)
            sts = self.Z.test_result(z0ctx,
                                     'mkdir %s' % path,
                                     True,
                                     RES)
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, self.os_tree[2], 'release.py')
        sts = self.Z.test_result(z0ctx,
                                 path,
                                 True,
                                 os.path.isfile(path))
        return sts

    def test_02(self, z0ctx):
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
                                     False,
                                     RES)
        return sts

    def test_03(self, z0ctx):
        sts = TEST_SUCCESS
        RES = False
        if not z0ctx['dry_run']:
            remote = 'OCA'
            reponame = 'OCB'
            branch = '10.0'
            odoo_path = os.path.join(self.root, branch)
            Z0testOdoo.git_clone(remote, reponame, branch, odoo_path)
        for path in self.os_tree:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                RES = os.path.isdir(path)
            sts = self.Z.test_result(z0ctx,
                                     'mkdir %s' % path,
                                     True,
                                     RES)
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, self.os_tree[2], 'release.py')
        sts = self.Z.test_result(z0ctx,
                                 path,
                                 True,
                                 os.path.isfile(path))
        return sts

    def setup(self, z0ctx):
        self.os_tree = ['10.0',
                        '10.0/addons',
                        '10.0/odoo',]

#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))
