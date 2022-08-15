#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Devel Tools unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys

from wok_code import license_mgnt
from zerobug import z0test, z0testodoo

__version__ = "2.0.0"

MODULE_ID = 'devel_tool'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


MANIFEST_1 = """{
    'name': 'module_test',
    'version': '12.0.1.0',
}"""
AUTHOR_2 = """
* Powerp <http://powerp.it>
* Shs-av <http://zeroincombenze.it>
"""
CONTRIBUTORS_2 = """
* Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
"""
MANIFEST_2 = """{
    'name': 'module_test',
    'version': '12.0.1.0',
}"""


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug

    def create_file_author_1(self, path):
        fn = os.path.join(path, 'authors.txt')
        with open(fn, 'wb') as fd:
            fd.write("""* Powerp <http://www.powerp.it/>""")

    def create_file_contributor_1(self, path):
        fn = os.path.join(path, 'contributors.txt')
        with open(fn, 'wb') as fd:
            fd.write("""* <antonio.vigliotti@libero.it>""")

    def create_file_manifest_1(self, path):
        fn = os.path.join(path, '__manifest__.py')
        with open(fn, 'wb') as fd:
            fd.write(MANIFEST_1)

    def create_file_author_2(self, path):
        fn = os.path.join(path, 'authors.txt')
        with open(fn, 'wb') as fd:
            fd.write(AUTHOR_2)

    def create_file_contributor_2(self, path):
        fn = os.path.join(path, 'contributors.txt')
        with open(fn, 'wb') as fd:
            fd.write(CONTRIBUTORS_2)

    def create_file_manifest_2(self, path):
        fn = os.path.join(path, '__manifest__.py')
        with open(fn, 'wb') as fd:
            fd.write(MANIFEST_2)

    def prepare_env(self, z0ctx, odoo_ver=None, step=None):
        step = step or 1
        if not odoo_ver:
            raise (ValueError, 'No odoo version supplied')
        odoo_root = z0testodoo.build_odoo_env(z0ctx, odoo_ver)
        odoo_root = os.path.join(odoo_root, odoo_ver)
        for ldir in (
            ['egg-info'],
            ['test_repository'],
            ['test_repository', 'egg-info'],
            ['test_repository', 'test_module'],
            ['test_repository', 'test_module', 'egg-info'],
        ):
            path = os.path.join(odoo_root, *ldir)
            if not os.path.isdir(path):
                os.mkdir(path)
        path = os.path.join(odoo_root, 'test_repository', 'test_module', 'egg-info')
        if step == 1:
            self.create_file_author_1(path)
            self.create_file_contributor_1(path)
        elif step == 2:
            self.create_file_author_2(path)
            self.create_file_contributor_2(path)
        path = os.path.join(odoo_root, 'test_repository', 'test_module')
        if step == 1:
            self.create_file_manifest_1(path)
        elif step == 1:
            self.create_file_manifest_2(path)
        return path

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        author = False
        website = False
        devman = False
        if not z0ctx['dry_run']:
            module_path = self.prepare_env(z0ctx, odoo_ver='12.0')
            license = license_mgnt.License(module_path)
            author = license.summary_authors()
            website = license.get_website()
            devman = license.get_maintainer()
        sts += self.Z.test_result(
            z0ctx, 'License author', 'powERP enterprise network', author
        )
        sts += self.Z.test_result(
            z0ctx, 'License website', 'https://www.powerp.it', website
        )
        sts += self.Z.test_result(
            z0ctx, 'License maintainer', 'powERP enterprise network', devman
        )
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        author = False
        website = False
        devman = False
        if not z0ctx['dry_run']:
            module_path = self.prepare_env(z0ctx, odoo_ver='12.0', step=2)
            license = license_mgnt.License(module_path)
            author = license.summary_authors()
            website = license.get_website()
            devman = license.get_maintainer()
        sts += self.Z.test_result(
            z0ctx, 'License author', 'powERP enterprise network, SHS-AV s.r.l.', author
        )
        sts += self.Z.test_result(
            z0ctx, 'License website', 'https://www.powerp.it', website
        )
        sts += self.Z.test_result(
            z0ctx, 'License maintainer', 'powERP enterprise network', devman
        )
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
