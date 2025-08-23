# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))

from arcangelo.scripts import license_mgnt

from zerobug import z0test, z0testodoo                                     # noqa: E402

__version__ = "2.1.0"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


MANIFEST_1 = """{
    'name': 'module_test',
    'version': '12.0.1.0',
}"""
AUTHOR_1 = """
* SHS-AV s.r.l. <http://zeroincombenze.it>
"""
CONTRIBUTORS_1 = """
* Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
"""
AUTHOR_2 = """
* Shs-av <http://zeroincombenze.it>
"""
CONTRIBUTORS_2 = """
* Antonio Vigliotti <antonio.vigliotti@libero.it>
"""
MANIFEST_2 = """{
    'name': 'module_test',
    'version': '12.0.1.0',
}"""


class RegressionTest:
    # def __init__(self, z0bug):
    #     self.Z = z0bug
    #     self.Z.inherit_cls(self)

    def create_file_author_1(self, path):
        fn = os.path.join(path, "AUTHORS.rst")
        with open(fn, "w") as fd:
            fd.write(AUTHOR_1)

    def create_file_contributor_1(self, path):
        fn = os.path.join(path, "CONTRIBUTORS.rst")
        with open(fn, "w") as fd:
            fd.write(CONTRIBUTORS_1)

    def create_file_manifest_1(self, path):
        fn = os.path.join(path, "__manifest__.py")
        with open(fn, "w") as fd:
            fd.write(MANIFEST_1)

    def create_file_author_2(self, path):
        fn = os.path.join(path, "AUTHORS.rst")
        with open(fn, "w") as fd:
            fd.write(AUTHOR_2)

    def create_file_contributor_2(self, path):
        fn = os.path.join(path, "CONTRIBUTORS.rst")
        with open(fn, "w") as fd:
            fd.write(CONTRIBUTORS_2)

    def create_file_manifest_2(self, path):
        fn = os.path.join(path, "__manifest__.py")
        with open(fn, "w") as fd:
            fd.write(MANIFEST_2)

    def prepare_env(self, odoo_ver=None, step=None):
        step = step or 1
        if not odoo_ver:
            raise (ValueError, "No odoo version supplied")
        odoo_root = z0testodoo.build_odoo_env({}, odoo_ver)
        odoo_root = os.path.join(odoo_root, odoo_ver)
        for ldir in (
            ["readme"],
            ["test_repository"],
            ["test_repository", "readme"],
            ["test_repository", "test_module"],
            ["test_repository", "test_module", "readme"],
        ):
            path = os.path.join(odoo_root, *ldir)
            if not os.path.isdir(path):
                os.mkdir(path)
        path = os.path.join(odoo_root, "test_repository", "test_module", "readme")
        if step == 1:
            self.create_file_author_1(path)
            self.create_file_contributor_1(path)
        elif step == 2:
            self.create_file_author_2(path)
            self.create_file_contributor_2(path)
        path = os.path.join(odoo_root, "test_repository", "test_module")
        if step == 1:
            self.create_file_manifest_1(path)
        elif step == 1:
            self.create_file_manifest_2(path)
        return path

    def test_01(self):
        author = False
        website = False
        # devman = False
        if not self.Z.dry_run:
            module_path = self.prepare_env(odoo_ver="12.0")
            license = license_mgnt.License(module_path)
            author = license.summary_authors()
            website = license.get_website()
            # devman = license.get_maintainer()
        self.assertEqual(
            author,
            "SHS-AV s.r.l.",
            msg_info="License author"
        )
        # self.assertEqual(
        #     website,
        #     # "https://www.zeroincombenze.it"
        #     "https://www.shs-av.com"
        # )

    def test_02(self):
        author = False
        website = False
        # devman = False
        if not self.Z.dry_run:
            module_path = self.prepare_env(odoo_ver="12.0", step=2)
            license = license_mgnt.License(module_path)
            author = license.summary_authors()
            website = license.get_website()
            # devman = license.get_maintainer()
        self.assertEqual(
            author,
            "SHS-AV s.r.l.",
            msg_info="License author"
        )
        # self.assertEqual(
        #     website,
        #     "https://www.zeroincombenze.it"
        # )


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )





