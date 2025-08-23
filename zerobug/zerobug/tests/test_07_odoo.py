#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
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


__version__ = "2.0.18"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0
VERSIONS = ('16.0', '12.0', '10.0', '7.0', '8.0')


def version():
    return __version__


class RegressionTest:

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

    def do_test_ocb(self, ver, name=None, hy=None):
        # sts = TEST_SUCCESS
        OS_TREE, hy = self.get_ocb_tree(ver, name=name, hy=hy)
        # res = False
        # if not z0ctx['dry_run']:
        self.root = z0testodoo.build_odoo_env(ver, name=name, hierarchy=hy)
        for path in OS_TREE:
            # if not z0ctx['dry_run']:
            path = os.path.join(self.root, path)
            res = os.path.isdir(path)
            # sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, res)
            self.assertTrue(res, msg_info='odoo %s' % path)

        # if not z0ctx['dry_run']:
        path = os.path.join(self.root, OS_TREE[2], 'release.py')
        # sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, os.path.isfile(path))
        self.assertTrue(os.path.isfile(path), msg_info='odoo %s' % path)
        # if not z0ctx['dry_run']:
        base = "openerp-server" if int(ver.split(".")[0]) < 10 else 'odoo-bin'
        path = os.path.join(self.root, OS_TREE[0], base)
        # sts += self.Z.test_result(z0ctx, 'odoo %s' % path, True, os.path.isfile(path))
        self.assertTrue(os.path.isfile(path), msg_info='odoo %s' % path)

    def do_test_repo(self, ver, name=None, hy=None):
        ocb_name = name if name else ver
        repotype = 'oca' if name else 'zero'
        # sts = TEST_SUCCESS
        # repodir = False
        # if not z0ctx['dry_run']:
        repodir = z0testodoo.create_repo(
            self.root,
            'test_repo',
            ver,
            hierarchy=hy,
            name=name,
            repotype=repotype,
        )
        # sts += self.Z.test_result(
        #     z0ctx,
        #     '%s/test_repo' % ocb_name,
        #     repodir,
        #     os.path.join(self.root, ocb_name, 'test_repo'),
        # )
        self.assertEqual(
            os.path.join(self.root, ocb_name, 'test_repo'),
            repodir,
            msg_info='%s/test_repo' % ocb_name
        )

        moduledir = ''
        # if not z0ctx['dry_run']:
        moduledir = z0testodoo.create_module(repodir, 'test_module', ver)
        # sts += self.Z.test_result(
        #     z0ctx,
        #     '%s/test_repo/test_module' % ocb_name,
        #     moduledir,
        #     os.path.join(self.root, ocb_name, 'test_repo', 'test_module'),
        # )
        self.assertEqual(
            os.path.join(self.root, ocb_name, 'test_repo', 'test_module'),
            moduledir,
            msg_info='%s/test_repo/test_module' % ocb_name
        )

    def do_remove_tree(self, ver, name=None, hy=None):
        # sts = TEST_SUCCESS
        OS_TREE, hy = self.get_ocb_tree(ver, name=name, hy=hy)
        # res = False
        # if not z0ctx['dry_run']:
        self.remove_os_tree(OS_TREE)
        for path in OS_TREE:
            # if not z0ctx['dry_run']:
            path = os.path.join(self.root, path)
            res = os.path.isdir(path)
            # sts += self.Z.test_result(z0ctx, 'rmdir %s' % path, False, res)
            self.assertFalse(res, msg_info='rmdir %s' % path)

    def test_01(self):
        # sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            self.do_test_ocb(ver)
            self.do_test_repo(ver)
            self.do_test_ocb(ver, name=name)
            self.do_test_repo(ver, name=name)
            name = os.path.expanduser('~/%s' % ver)
            self.do_test_ocb(ver, name=name)

    def test_02(self):
        # sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            self.do_remove_tree(ver)
            self.do_remove_tree(ver, name=name)
            name = os.path.expanduser('~/%s' % ver)
            self.do_remove_tree(ver, name=name)

    def test_03(self):
        # sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            self.do_test_ocb(ver, hy=True)
            self.do_test_ocb(ver, name=name, hy=True)

    def test_04(self):
        # sts = TEST_SUCCESS
        for ver in VERSIONS:
            name = 'oca%s' % ver.split('.')[0]
            self.do_remove_tree(ver, hy=True)
            self.do_remove_tree(ver, name=name, hy=True)

    def test_05(self):
        # sts = TEST_SUCCESS
        # res = False
        remote = 'OCA'
        reponame = 'OCB'
        branch = '14.0'
        # if not z0ctx['dry_run']:
        name = os.path.join(
            os.path.expanduser('~/'), 'oca%s' % branch.split('.')[0]
        )
        self.root = z0testodoo.build_odoo_env(branch, name=name)
        odoo_path = os.path.join(os.path.expanduser('~/'), 'OCB-%s' % branch)
        z0testodoo.git_clone(remote, reponame, branch, odoo_path)
        for path in self.os_tree:
            # if not z0ctx['dry_run']:
            res = os.path.isdir(path)
            # sts += self.Z.test_result(z0ctx, 'mkdir %s' % path, True, res)
            self.assertTrue(res, msg_info='mkdir %s' % path)

        # if not z0ctx['dry_run']:
        path = os.path.join(self.root, self.os_tree[2], 'release.py')
        # sts += self.Z.test_result(
        #     z0ctx, 'git clone OCA/OCB/14.0 -> %s' % path, True, os.path.isfile(path)
        # )
        self.assertTrue(
            os.path.isfile(path), msg_info='git clone OCA/OCB/14.0 -> %s' % path)

        # if not z0ctx['dry_run']:
        path = os.path.join(self.root, self.os_tree[0], 'odoo-bin')
        # sts += self.Z.test_result(
        #     z0ctx, 'git clone OCA/OCB/14.0 -> %s' % path, True, os.path.isfile(path)
        # )
        self.assertTrue(
            os.path.isfile(path), msg_info='git clone OCA/OCB/14.0 -> %s' % path)

        reponame = 'l10n-italy'
        odoo_path = ''
        # if not z0ctx['dry_run']:
        name = os.path.join(
            os.path.expanduser('~/'), 'oca%s' % branch.split('.')[0]
        )
        z0testodoo.create_repo(
            os.path.expanduser('~/'), reponame, branch, name=name
        )
        odoo_path = os.path.join(
            os.path.expanduser('~/'), 'OCB-%s' % branch, reponame
        )
        z0testodoo.git_clone(remote, reponame, branch, odoo_path)
        # sts += self.Z.test_result(
        #     z0ctx, 'git clone OCA/%s/14.0' % reponame, True, os.path.isdir(odoo_path)
        # )
        self.assertTrue(
            os.path.isdir(odoo_path), msg_info='git clone OCA/%s/14.0' % reponame)

    def setup(self):
        root = os.path.expanduser('~/OCB-14.0')
        self.os_tree = [
            root,
            os.path.join(root, 'addons'),
            os.path.join(root, 'odoo'),
            os.path.join(root, 'odoo', 'addons'),
        ]
        self.remove_os_tree(self.os_tree)
        for ver in VERSIONS:
            self.remove_os_tree(ver)

    def tearoff(self):
        self.setup()


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
