#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys
import shutil
from zerobug import z0test, z0testodoo
from z0bug_odoo.travis.getaddons import is_module
from z0bug_odoo.travis.test_server import get_build_dir, get_server_script

__version__ = "1.0.10"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0
ODOO_VERSIONS = ('7.0', '10.0', '12.0')


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        if os.path.basename(os.getcwd()) == 'tests':
            travis_addons = os.path.abspath(
                os.path.join(os.environ.get("TRAVIS_BUILD_DIR", ".."),
                             'travis'))
        else:
            travis_addons = os.path.abspath(
                os.path.join(os.environ.get("TRAVIS_BUILD_DIR", "."),
                             'travis'))
        if travis_addons not in sys.path:
            sys.path.append(travis_addons)
        self.root = ''
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = 0
        home = os.path.expanduser('~')
        gitorg = 'odoo'
        for odoo_version in ODOO_VERSIONS:
            majver = int(odoo_version.split('.')[0])
            travis_base_dir = odoo_addons = version = False
            odoo_full = '%s/%s' % (gitorg, odoo_version)
            odoo_addons = repodir = moduledir = ''
            if not z0ctx['dry_run']:
                # Test with explicit version passed
                self.root = z0testodoo.build_odoo_env(z0ctx, odoo_version)
                odoo_root = os.path.join(
                    home, '%s-%s' % (gitorg, odoo_version))
                if eval(odoo_version.split('.')[0]) < 10:
                    odoo_addons = os.path.join(odoo_root, 'openerp', 'addons')
                else:
                    odoo_addons = os.path.join(odoo_root, 'odoo', 'addons')
                if os.path.isdir(odoo_root):
                    shutil.rmtree(odoo_root, True)
                shutil.move(os.path.join(self.root, odoo_version), odoo_root)
                travis_base_dir, version = get_build_dir(
                    odoo_full, version=odoo_version)
            sts += self.Z.test_result(
                    z0ctx,
                    'is_module(\'%s\')' % odoo_addons,
                    False,
                    is_module(odoo_addons))
            if not z0ctx['dry_run']:
                repodir = z0testodoo.create_repo(
                    z0ctx, odoo_root, 'test_repo', version)
            sts += self.Z.test_result(
                    z0ctx,
                    'is_module(\'%s\')' % repodir,
                    False,
                    is_module(repodir))
            if not z0ctx['dry_run']:
                moduledir = z0testodoo.create_module(
                    z0ctx, repodir, 'test_module', '%s.0.1.0' % odoo_version)
            sts += self.Z.test_result(
                    z0ctx,
                    'is_module(\'%s\')' % moduledir,
                    os.path.join(
                        moduledir, '__openerp__.py') if majver < 10
                    else os.path.join(
                        moduledir, '__manifest__.py'),
                    is_module(moduledir))
            sts += self.Z.test_result(
                z0ctx,
                'get_build_dir(\'%s\', version=\'%s\')' % (odoo_full,
                                                           odoo_version),
                travis_base_dir,
                odoo_addons)
            sts += self.Z.test_result(
                z0ctx,
                'get_build_dir(\'%s\', version=\'%s\')' % (odoo_full, version),
                version,
                odoo_version)
            if not z0ctx['dry_run']:
                # Test w/o explicit version passed
                travis_base_dir, version = get_build_dir(odoo_full)
            sts += self.Z.test_result(
                z0ctx,
                'get_build_dir(\'%s\')' % odoo_full,
                travis_base_dir,
                odoo_addons)
            sts += self.Z.test_result(
                z0ctx,
                'get_build_dir(\'%s\')' % odoo_full,
                version,
                odoo_version)
            if not z0ctx['dry_run']:
                pass
            sts += self.Z.test_result(
                z0ctx,
                'get_server_script(\'%s\')' % self.root,
                os.path.join(self.root,
                             'odoo-bin' if majver > 9 else 'openerp-server'),
                get_server_script(self.root))
        return sts

    def test_02(self, z0ctx):
        for odoo_version in ODOO_VERSIONS:
            pass


# Run main if executed as a script
if __name__ == "__main__":
    exit(z0test.main_local(
        z0test.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))