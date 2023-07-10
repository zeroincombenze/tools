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
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))
from zerobug import z0test, z0testodoo                                     # noqa: E402


__version__ = "2.0.9"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0
VERSIONS = ('16.0', '12.0', '10.0', '7.0', '8.0')


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.root = ''

    def get_ocb_tree(self, ver, name=None, hy=None):
        ocb_name = name or ver
        if int(ver.split(".")[0]) < 10:
            OS_TREE = (
                '%s/server' % ocb_name if hy else '%s' % ocb_name,
                '%s/addons' % ocb_name,
                '%s/server/openerp' % ocb_name if hy else '%s/openerp' % ocb_name,
                '%s/.git' % ocb_name,
            )
            hy = 'server' if hy else None
        else:
            OS_TREE = (
                '%s/odoo' % ocb_name if hy else '%s' % ocb_name,
                '%s/addons' % ocb_name,
                '%s/odoo/odoo' % ocb_name if hy else '%s/odoo' % ocb_name,
                '%s/.git' % ocb_name,
            )
            hy = 'tree' if hy else None
        return OS_TREE, hy

    def do_test_ocb(self, z0ctx, ver, name=None, hy=None):
        sts = TEST_SUCCESS
        OS_TREE, hy = self.get_ocb_tree(ver, name=name, hy=hy)
        res = False
        if not z0ctx['dry_run']:
            self.root = z0testodoo.build_odoo_env(z0ctx, ver, name=name, hierarchy=hy)
        for path in OS_TREE:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                res = os.path.isdir(path)
            sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, res)
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, OS_TREE[2], 'release.py')
        sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, os.path.isfile(path))
        if not z0ctx['dry_run']:
            base = "openerp-server" if int(ver.split(".")[0]) < 10 else 'odoo-bin'
            path = os.path.join(self.root, OS_TREE[0], base)
        sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, os.path.isfile(path))
        return sts

    def do_test_repo(self, z0ctx, ver, name=None, hy=None):
        ocb_name = name if name else ver
        repotype = 'oca' if name else 'zero'
        sts = TEST_SUCCESS
        repodir = False
        if not z0ctx['dry_run']:
            repodir = z0testodoo.create_repo(
                z0ctx,
                self.root,
                'test_repo',
                ver,
                hierarchy=hy,
                name=name,
                repotype=repotype,
            )
        sts += self.Z.test_result(
            z0ctx,
            '%s/test_repo' % ocb_name,
            repodir,
            os.path.join(self.root, ocb_name, 'test_repo'),
        )

        moduledir = ''
        if not z0ctx['dry_run']:
            moduledir = z0testodoo.create_module(z0ctx, repodir, 'test_module', ver)
        sts += self.Z.test_result(
            z0ctx,
            '%s/test_repo/test_module' % ocb_name,
            moduledir,
            os.path.join(self.root, ocb_name, 'test_repo', 'test_module'),
        )
        return sts

    def do_remove_tree(self, z0ctx, ver, name=None, hy=None):
        sts = TEST_SUCCESS
        OS_TREE, hy = self.get_ocb_tree(ver, name=name, hy=hy)
        res = False
        if not z0ctx['dry_run']:
            self.Z.remove_os_tree(z0ctx, OS_TREE)
        for path in OS_TREE:
            if not z0ctx['dry_run']:
                path = os.path.join(self.root, path)
                res = os.path.isdir(path)
            sts += self.Z.test_result(z0ctx, 'rmdir %s' % path, False, res)
        return sts

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            sts += self.do_test_ocb(z0ctx, ver)
            sts += self.do_test_repo(z0ctx, ver)
            sts += self.do_test_ocb(z0ctx, ver, name=name)
            sts += self.do_test_repo(z0ctx, ver, name=name)
            name = os.path.expanduser('~/%s' % ver)
            sts += self.do_test_ocb(z0ctx, ver, name=name)
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            sts += self.do_remove_tree(z0ctx, ver)
            sts += self.do_remove_tree(z0ctx, ver, name=name)
            name = os.path.expanduser('~/%s' % ver)
            sts += self.do_remove_tree(z0ctx, ver, name=name)
        return sts

    def test_03(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            sts += self.do_test_ocb(z0ctx, ver, hy=True)
            sts += self.do_test_ocb(z0ctx, ver, name=name, hy=True)
        return sts

    def test_04(self, z0ctx):
        sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            sts += self.do_remove_tree(z0ctx, ver, hy=True)
            sts += self.do_remove_tree(z0ctx, ver, name=name, hy=True)
        return sts

    def test_05(self, z0ctx):
        sts = TEST_SUCCESS
        res = False
        remote = 'OCA'
        reponame = 'OCB'
        branch = '14.0'
        if not z0ctx['dry_run']:
            name = os.path.join(
                os.path.expanduser('~/'), 'oca%s' % branch.split('.')[0]
            )
            self.root = z0testodoo.build_odoo_env(z0ctx, branch, name=name)
            odoo_path = os.path.join(os.path.expanduser('~/'), 'OCB-%s' % branch)
            z0testodoo.git_clone(remote, reponame, branch, odoo_path)
        for path in self.os_tree:
            if not z0ctx['dry_run']:
                res = os.path.isdir(path)
            sts += self.Z.test_result(z0ctx, 'mkdir %s' % path, True, res)
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, self.os_tree[2], 'release.py')
        sts += self.Z.test_result(
            z0ctx, 'git clone OCA/OCB/14.0 -> %s' % path, True, os.path.isfile(path)
        )
        if not z0ctx['dry_run']:
            path = os.path.join(self.root, self.os_tree[0], 'odoo-bin')
        sts += self.Z.test_result(
            z0ctx, 'git clone OCA/OCB/14.0 -> %s' % path, True, os.path.isfile(path)
        )

        reponame = 'l10n-italy'
        odoo_path = ''
        if not z0ctx['dry_run']:
            name = os.path.join(
                os.path.expanduser('~/'), 'oca%s' % branch.split('.')[0]
            )
            z0testodoo.create_repo(
                z0ctx, os.path.expanduser('~/'), reponame, branch, name=name
            )
            odoo_path = os.path.join(
                os.path.expanduser('~/'), 'OCB-%s' % branch, reponame
            )
            z0testodoo.git_clone(remote, reponame, branch, odoo_path)
        sts += self.Z.test_result(
            z0ctx, 'git clone OCA/%s/14.0' % reponame, True, os.path.isdir(odoo_path)
        )
        return sts

    def setup(self, z0ctx):
        root = os.path.expanduser('~/OCB-14.0')
        self.os_tree = [
            root,
            os.path.join(root, 'addons'),
            os.path.join(root, 'odoo'),
            os.path.join(root, 'odoo', 'addons'),
        ]
        self.Z.remove_os_tree(z0ctx, self.os_tree)
        for ver in VERSIONS:
            self.Z.remove_os_tree(z0ctx, ver)

    def tearoff(self, z0ctx):
        self.setup(z0ctx)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
