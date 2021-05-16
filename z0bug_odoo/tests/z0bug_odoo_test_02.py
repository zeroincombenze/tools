#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys
import shutil
# from zerobug import Z0BUG
# from z0bug_odoo import test_common
from zerobug import Z0testOdoo

__version__ = "1.0.2"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


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
        sys.path.append(travis_addons)
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = 0
        # import pdb
        # pdb.set_trace()
        from test_server import get_build_dir
        # import importlib
        home = os.path.expanduser('~')
        gitorg = 'odoo'
        # for odoo_version in ('7.0', '10.0', '12.0'):
        for odoo_version in ('10.0', ):
            # importlib.reload(test_server.get_build_dir)   # noqa: F821
            travis_base_dir = odoo_addons = version = False
            odoo_full = '%s/%s' % (gitorg, odoo_version)
            if not z0ctx['dry_run']:
                self.root = Z0testOdoo.build_odoo_env(z0ctx, odoo_version)
                odoo_root = os.path.join(home, '%s-%s' % (gitorg, odoo_version))
                if eval(odoo_version.split('.')[0]) < 10:
                    odoo_addons = os.path.join(odoo_root, 'openerp', 'addons')
                else:
                    odoo_addons = os.path.join(odoo_root, 'odoo', 'addons')
                shutil.move(os.path.join(self.root, odoo_version), odoo_root)
                travis_base_dir, version = get_build_dir(
                    odoo_full, version=odoo_version)
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
                shutil.rmtree(odoo_root, True)
        return sts


# if __name__ == "__main__":
#     exit(Z0BUG.main_local(
#         Z0BUG.parseoptest(sys.argv[1:],
#                           version=version()), RegressionTest))
