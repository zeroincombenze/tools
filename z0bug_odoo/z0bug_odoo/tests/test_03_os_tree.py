# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import shutil
import sys

from z0bug_odoo.travis.test_server import get_addons_path, get_server_path
from zerobug import z0test, z0testodoo

__version__ = "2.0.16"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0
ODOO_VERSIONS = ('7.0', '10.0', '12.0')


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.root = {}
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = 0
        home = os.path.expanduser('~')
        gitorg = 'odoo'
        module_name = 'test_module'
        module2_name = 'web'
        # if not z0ctx['dry_run']:
        #     import pdb; pdb.set_trace()
        for odoo_version in ODOO_VERSIONS:
            odoo_addons = odoo_addons2 = ''
            if not z0ctx['dry_run']:
                self.root[odoo_version] = z0testodoo.build_odoo_env(z0ctx, odoo_version)
                if eval(odoo_version.split('.')[0]) < 10:
                    odoo_addons = os.path.join(
                        self.root[odoo_version], odoo_version, 'openerp', 'addons'
                    )
                else:
                    odoo_addons = os.path.join(
                        self.root[odoo_version], odoo_version, 'odoo', 'addons'
                    )
                odoo_addons2 = os.path.join(
                    self.root[odoo_version], odoo_version, 'addons'
                )
                z0testodoo.create_module(
                    z0ctx, odoo_addons, module_name, '%s.0.1.0' % odoo_version
                )
                z0testodoo.create_module(
                    z0ctx, odoo_addons2, module2_name, '%s.0.1.0' % odoo_version
                )
            odoo_root = os.path.join(home, '%s-%s' % (gitorg, odoo_version))
            if not z0ctx['dry_run']:
                if os.path.isdir(odoo_root):
                    shutil.rmtree(odoo_root, True)
                shutil.move(
                    os.path.join(self.root[odoo_version], odoo_version), odoo_root
                )
            #
            self.root[odoo_version] = odoo_root
            if eval(odoo_version.split('.')[0]) < 10:
                odoo_addons = os.path.join(self.root[odoo_version], 'openerp', 'addons')
            else:
                odoo_addons = os.path.join(self.root[odoo_version], 'odoo', 'addons')
            odoo_addons2 = os.path.join(self.root[odoo_version], 'addons')
            travis_home = os.environ.get("HOME", os.path.expanduser("~"))
            server_path = get_server_path(
                '%s/%s' % (gitorg, 'odoo'), odoo_version, travis_home
            )
            sts += self.Z.test_result(
                z0ctx,
                'get_server_path(\'%s/odoo\', \'%s\', \'%s\')'
                % (gitorg, odoo_version, travis_home),
                odoo_root,
                server_path,
            )
            dependencies_dir = os.path.join(travis_home, 'dependencies')
            if not os.path.isdir(dependencies_dir):
                os.mkdir(dependencies_dir)
            addons_path = ''
            # We must simulate the Travis environment when Odoo is testing
            # So TRAVIS_BUILD_DIR is updated to odoo_root
            SAVED_TRAVIS_BUILD_DIR = os.environ.get('TRAVIS_BUILD_DIR')
            os.putenv('TRAVIS_BUILD_DIR', odoo_root)
            os.environ['TRAVIS_BUILD_DIR'] = odoo_root
            travis_build_dir = os.environ['TRAVIS_BUILD_DIR']
            if not z0ctx['dry_run']:
                for module in ('dep1', 'dep2'):
                    z0testodoo.create_module(
                        z0ctx, dependencies_dir, module, '%s.0.1.0' % odoo_version
                    )
                addons_path = get_addons_path(
                    dependencies_dir, travis_build_dir, server_path
                )
            sts += self.Z.test_result(
                z0ctx,
                'get_addons_path(\'%s\', \'%s\', \'%s\')'
                % (dependencies_dir, travis_build_dir, server_path),
                {odoo_addons, odoo_addons2, dependencies_dir},
                set(addons_path.split(',')),
            )
            # Restore TRAVIS_BUILD_DIR value
            os.putenv('TRAVIS_BUILD_DIR', SAVED_TRAVIS_BUILD_DIR)


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )





