#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
# from past.builtins import basestring

import os
import sys
from zerobug import Z0BUG
from zerobug import Z0testOdoo

__version__ = "1.0.2.99"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        # sts = TEST_SUCCESS
        for ver in ('12.0', '10.0', '7.0', '8.0'):
            if ver in ('7.0', '8.0'):
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/openerp' % ver,
                           )
            else:
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/odoo' % ver,
                           )
            RES = False
            if not z0ctx['dry_run']:
                self.root = Z0testOdoo.build_odoo_env(z0ctx, ver)
            for path in OS_TREE:
                if not z0ctx['dry_run']:
                    path = os.path.join(self.root, path)
                    RES = os.path.isdir(path)
                sts = self.Z.test_result(z0ctx,
                                         'odoo %s' % path,
                                         True,
                                         RES)
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, OS_TREE[2], 'release.py')
            sts = self.Z.test_result(z0ctx,
                                     'odoo %s' % path,
                                     True,
                                     os.path.isfile(path))
            if not z0ctx['dry_run']:
                base = "openerp-server" if ver in ('7.0',
                                                   '8.0') else 'odoo-bin'
                path = os.path.join(self.root, OS_TREE[0], base)
            sts = self.Z.test_result(z0ctx,
                                     'odoo %s' % path,
                                     True,
                                     os.path.isfile(path))
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in ('12.0', '10.0', '7.0', '8.0'):
            if ver in ('7.0', '8.0'):
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/openerp' % ver,
                           )
            else:
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/odoo' % ver,
                           )
            RES = False
            if not z0ctx['dry_run']:
                self.Z.remove_os_tree(z0ctx, OS_TREE)
            for path in OS_TREE:
                if not z0ctx['dry_run']:
                    path = os.path.join(self.root, path)
                    RES = os.path.isdir(path)
                sts = self.Z.test_result(z0ctx,
                                         'rmdir %s' % path,
                                         False,
                                         RES)
        return sts

    def test_03(self, z0ctx):
        # sts = TEST_SUCCESS
        for ver in ('12.0', '10.0', '7.0', '8.0'):
            if ver in ('7.0', '8.0'):
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/server/openerp' % ver,
                           )
                hy = 'server'
            else:
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/odoo/odoo' % ver,
                           )
                hy = 'tree'
            RES = False
            if not z0ctx['dry_run']:
                self.root = Z0testOdoo.build_odoo_env(z0ctx, ver, hierarchy=hy)
            for path in OS_TREE:
                if not z0ctx['dry_run']:
                    path = os.path.join(self.root, path)
                    RES = os.path.isdir(path)
                sts = self.Z.test_result(z0ctx,
                                         'odoo %s' % path,
                                         True,
                                         RES)
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, OS_TREE[2], 'release.py')
            sts = self.Z.test_result(z0ctx,
                                     'odoo %s' % path,
                                     True,
                                     os.path.isfile(path))
            if not z0ctx['dry_run']:
                base = "openerp-server" if ver in ('7.0',
                                                   '8.0') else 'odoo-bin'
                path = os.path.join(self.root, OS_TREE[0], base)
            sts = self.Z.test_result(z0ctx,
                                     'odoo %s' % path,
                                     True,
                                     os.path.isfile(path))
        return sts

    def test_04(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in ('12.0', '10.0', '7.0', '8.0'):
            if ver in ('7.0', '8.0'):
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/server/openerp' % ver,
                           )
            else:
                OS_TREE = (ver,
                           '%s/addons' % ver,
                           '%s/odoo/odoo' % ver,
                           )
            RES = False
            if not z0ctx['dry_run']:
                self.Z.remove_os_tree(z0ctx, OS_TREE)
            for path in OS_TREE:
                if not z0ctx['dry_run']:
                    path = os.path.join(self.root, path)
                    RES = os.path.isdir(path)
                sts = self.Z.test_result(z0ctx,
                                         'rmdir %s' % path,
                                         False,
                                         RES)
        return sts

    def test_05(self, z0ctx):
        self.repos_dir = self.module_dir = ''
        for ver in ('12.0', '10.0', '7.0', '8.0'):
            if not z0ctx['dry_run']:
                self.root = Z0testOdoo.build_odoo_env(z0ctx, ver)
                self.repos_dir = Z0testOdoo.build_odoo_repos(
                    z0ctx, self.root, ver, 'l10n-italy')
            sts = self.Z.test_result(
                z0ctx,
                'repository l10n-italy: %s' % self.repos_dir,
                True,
                os.path.isdir(self.repos_dir))
            if not z0ctx['dry_run']:
                module_name = 'l10n_it'
                manifest = {
                    'version': '0.1.0',
                }
                self.module_dir = Z0testOdoo.build_odoo_module(
                    z0ctx, self.repos_dir, module_name, manifest)
            sts = self.Z.test_result(
                z0ctx,
                'module l10n_it: %s' % self.module_dir,
                True,
                os.path.isdir(self.module_dir))
        return sts

    def test_06(self, z0ctx):
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
                                 'odoo %s' % path,
                                 True,
                                 os.path.isfile(path))
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, self.os_tree[0], 'odoo-bin')
        sts = self.Z.test_result(z0ctx,
                                 'odoo %s' % path,
                                 True,
                                 os.path.isfile(path))
        return sts

    def setup(self, z0ctx):
        self.os_tree = ['10.0',
                        '10.0/addons',
                        '10.0/odoo',]
        self.Z.remove_os_tree(z0ctx, self.os_tree)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))
