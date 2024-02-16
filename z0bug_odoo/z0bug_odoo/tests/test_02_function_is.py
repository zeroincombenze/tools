# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import shutil
import sys

from z0bug_odoo.travis.getaddons import (get_addons, get_modules,
                                         get_modules_info, is_addons,
                                         is_module)
from zerobug import z0test, z0testodoo

# from z0bug_odoo.travis.test_server import get_build_dir, get_server_script

__version__ = "2.0.16"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0
ODOO_VERSIONS = ('7.0', '10.0', '12.0')


def version():
    return __version__


class RegressionTest:
    def setup(self):
        if os.path.basename(os.getcwd()) == 'tests':
            travis_addons = os.path.abspath(
                os.path.join(os.environ.get("TRAVIS_BUILD_DIR", ".."), 'travis')
            )
        else:
            travis_addons = os.path.abspath(
                os.path.join(os.environ.get("TRAVIS_BUILD_DIR", "."), 'travis')
            )
        if travis_addons not in sys.path:
            sys.path.append(travis_addons)
        self.root = {}

    def test_01(self, z0ctx):
        sts = 0
        for odoo_version in ODOO_VERSIONS:
            odoo_addons = moduledir = ''
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
            sts += self.Z.test_result(
                z0ctx, 'is_module(\'%s\')' % odoo_addons, False, is_module(odoo_addons)
            )
            if not z0ctx['dry_run']:
                moduledir = z0testodoo.create_module(
                    z0ctx, odoo_addons, 'test_module', '%s.0.1.0' % odoo_version
                )
            sts += self.Z.test_result(
                z0ctx, 'is_module(\'%s\')' % moduledir, True, bool(is_module(moduledir))
            )
            sts += self.Z.test_result(
                z0ctx, 'is_addons(\'%s\')' % moduledir, False, is_addons(moduledir)
            )
            sts += self.Z.test_result(
                z0ctx, 'is_addons(\'%s\')' % odoo_addons, True, is_addons(odoo_addons)
            )
        return sts

    def test_02(self, z0ctx):
        sts = 0
        home = os.path.expanduser('~')
        gitorg = 'odoo'
        module_name = 'test_module'
        module2_name = 'web'
        for odoo_version in ODOO_VERSIONS:
            modules = []
            odoo_root = os.path.join(home, '%s-%s' % (gitorg, odoo_version))
            if eval(odoo_version.split('.')[0]) < 10:
                odoo_addons = os.path.join(odoo_root, 'openerp', 'addons')
            else:
                odoo_addons = os.path.join(odoo_root, 'odoo', 'addons')
            odoo_addons2 = os.path.join(odoo_root, 'addons')
            if not z0ctx['dry_run']:
                if os.path.isdir(odoo_root):
                    shutil.rmtree(odoo_root, True)
                shutil.move(
                    os.path.join(self.root[odoo_version], odoo_version), odoo_root
                )
                modules = get_modules_info(odoo_addons)
            sts += self.Z.test_result(
                z0ctx,
                'get_modules_info(\'%s\')' % odoo_addons,
                True,
                module_name in modules,
            )
            if not z0ctx['dry_run']:
                modules = get_modules_info(odoo_root, depth=99)
            sts += self.Z.test_result(
                z0ctx,
                'get_modules_info(\'%s\', depth=99)' % odoo_root,
                True,
                module_name in modules,
            )
            if not z0ctx['dry_run']:
                z0testodoo.create_module(
                    z0ctx, odoo_addons2, module2_name, '%s.0.1.0' % odoo_version
                )
            if not z0ctx['dry_run']:
                modules = get_modules_info(odoo_root, depth=99)
            sts += self.Z.test_result(
                z0ctx,
                'get_modules_info(\'%s\', depth=99)' % odoo_root,
                True,
                module2_name in modules,
            )
            sts += self.Z.test_result(z0ctx, '# modules', 2, len(modules))
            #
            if not z0ctx['dry_run']:
                modules = get_modules(odoo_root, depth=99)
            sts += self.Z.test_result(
                z0ctx,
                'get_modules(\'%s\', depth=99))' % odoo_root,
                [module_name, module2_name],
                modules,
            )
            #
            addons = []
            if not z0ctx['dry_run']:
                addons = get_addons(odoo_root, depth=99)
            sts += self.Z.test_result(
                z0ctx,
                'get_addons(\'%s\', depth=99))' % odoo_root,
                {odoo_addons, odoo_addons2},
                set(addons),
            )


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



