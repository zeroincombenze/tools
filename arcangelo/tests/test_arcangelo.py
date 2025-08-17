#!/home/odoo/devel/venv/bin/python3.8
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
from datetime import datetime, timedelta

from z0lib import z0lib
from zerobug import z0test


__version__ = "2.0.21"

MODULE_ID = "wok_code"
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def setup(self):
        # super(, self).setup()
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.path.join(os.getcwd(), "tests")
            self.rundir = os.getcwd()
        self.odoo_datadir = os.path.join(self.testdir, "data")
        self.odoo_fakedir = os.path.join(self.testdir, "data", "fake")
        self.odoo_matchdir = os.path.join(self.testdir, "data", "match")
        self.odoo_testdir = os.path.join(self.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)
        z0lib.os_system(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "arcangelo.py")
        )

    def get_fake_fullname(self, fn):
        fqn = os.path.join(self.odoo_fakedir, fn)
        if not os.path.exists(fqn):
            fqn = os.path.join(self.odoo_datadir, fn)
        return fqn

    def get_match_fullname(self, fn):
        fqn = os.path.join(self.odoo_matchdir, fn)
        if not os.path.exists(fqn):
            fqn = os.path.join(self.odoo_datadir, fn)
        return fqn

    def get_test_fullname(self, fn):
        fqn = os.path.join(self.odoo_testdir, fn)
        return fqn

    def get_all_fullname(self, src, tgt):
        src_fqn = self.get_fake_fullname(src)
        tgt_fqn = self.get_match_fullname(tgt)
        res_fqn = self.get_test_fullname(tgt)
        return src_fqn, tgt_fqn, res_fqn

    def compare_fn(self, src_ffn, tgt_ffn):
        with open(src_ffn, "r") as fd:
            source = fd.read().replace("\n\n", "\n")
            source = source.split("\n")
        with open(tgt_ffn, "r") as fd:
            target = fd.read().replace("\n\n", "\n")
            target = target.split("\n")
        src_lno = tgt_lno = 0
        while src_lno < len(source):
            if source[src_lno] == target[tgt_lno]:
                src_lno += 1
                tgt_lno += 1
                continue
            print("File %s with wrong contents" % src_ffn)
            print("|%s|==|%s|" % (source[src_lno], target[tgt_lno]))
            return False
        return True

    def compare_xmlfn(self, src_ffn, tgt_ffn):
        with open(src_ffn, "r") as fd:
            source = fd.read().replace("\n\n", "\n")
            source = source.split("\n")
        with open(tgt_ffn, "r") as fd:
            target = fd.read().replace("\n\n", "\n")
            target = target.split("\n")
        src_lno = tgt_lno = 0
        while src_lno < len(source):
            if source[src_lno].strip() == target[tgt_lno].strip():
                src_lno += 1
                tgt_lno += 1
                continue
            print("File %s with wrong contents" % src_ffn)
            print("|%s|==|%s|" % (source[src_lno], target[tgt_lno]))
            return False
        return True

    def _test_module(self, file_list, version_from=None, version_to=None):
        module_from = "odoo" + version_from.split(".")[0]
        module_to = "odoo" + version_to.split(".")[0]
        if version_from == version_to:
            cmd = "arcangelo -cifw -b%s %s -o %s -y" % (
                version_to,
                self.get_fake_fullname(module_from),
                self.get_test_fullname(module_to),
            )
        else:
            cmd = "arcangelo -cifw -F%s -b%s %s -o %s -y" % (
                version_from,
                version_to,
                self.get_fake_fullname(module_from),
                self.get_test_fullname(module_to),
            )
        sts, stdout, stderr = z0lib.os_system_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        for fn in file_list:
            if isinstance(fn, (list, tuple)):
                src_fn = os.path.join(module_from, fn[0])
                tgt_fn = os.path.join(module_to, fn[1])
            else:
                src_fn = os.path.join(module_from, fn)
                tgt_fn = os.path.join(module_to, fn)
            src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(src_fn, tgt_fn)
            self.assertTrue(
                self.compare_fn(res_fqn, tgt_fqn),
                "File %s differs %s" % (res_fqn, tgt_fqn),
            )

    def __test_01_version(self):
        sts, stdout, stderr = z0lib.os_system_traced("arcangelo --version", rtime=False)
        self.assertEqual(sts, 0, msg_info="arcangelo --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02_api_py(self):
        # Test migrate package from python 2 to python 2 (no update)
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "pkg_py2_02.py", "pkg_py2_02.py"
        )
        cmd = "arcangelo --python=2.7 --package-name=pypi -fiw %s -o %s" % (
            src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test migrate package from python 2 to python 3
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "pkg_py2_02.py", "pkg_py3_02.py"
        )
        cmd = "arcangelo --python=3.10 --package-name=pypi -fiw %s -o %s" % (
            src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test migrate package from python 3 to python 2
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "pkg_py3_02.py", "pkg_py2_02.py"
        )
        cmd = "arcangelo --python=2.7 --package-name=pypi -fiw %s -o %s" % (
            src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test migrate package from python 2 to python future
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "pkg_py2_02.py", "pkg_future_02.py"
        )
        cmd = "arcangelo --python=2+3 --package-name=pypi -fiw %s -o %s" % (
            src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

    def test_07_odoo_api_py(self):
        # Test migrate from OpenERP 7.0 with old API to Odoo 12.0 with new API
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "openerp7_old_api.py", "odoo12_new_api.py"
        )
        cmd = "arcangelo -Podoo -fiw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test backport from Odoo 12.0 with new API to OpenERP 7.0 with old API
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo12_new_api.py", "openerp7_old_api.py"
        )
        cmd = "arcangelo -Podoo -fiw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test migrate from Odoo 10.0 (python 2) to Odoo 12.0 (python 3, both new API)
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo10_new_api.py", "odoo12_new_api.py"
        )
        cmd = "arcangelo -Podoo -fiw -F10.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        # Test backport from Odoo 12.0 (python 3) to Odoo 10.0 (python 2, both new API)
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo12_new_api.py", "odoo10_new_api.py"
        )
        cmd = "arcangelo -Podoo -fiw -F12.0 -b10.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

    def test_07_old_api_xml(self):
        # Test migrate XML from OpenERP 7.0 with tag openerp to Odoo 12.0 with tag odoo
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "openerp7_old_api.xml", "odoo12_new_api.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )

        # Test backport XML from Odoo 12.0 with tag odoo to OpenERP 7.0 with tag openerp
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo12_new_api.xml", "openerp7_old_api.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )

    def test_07_old_api_data_xml(self):
        # Test migrate XML from OpenERP 7.0 with tag data to Odoo 12.0 w/o tag data
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "openerp7_old_api_data.xml", "odoo12_new_api_data.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )

        # Test backport XML from Odoo 12.0 w/o tag data to OpenERP 7.0 with tag data
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo12_new_api_data.xml", "openerp7_old_api_data.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )

    def test_12_13_migrate(self):
        # Test migrate from Odoo 12.0 to Odoo 13.0
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo12.py", "odoo13.py")
        cmd = "arcangelo -Podoo -fiw -F12.0 -b13.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo12_view.xml", "odoo13_view.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F12.0 -b13.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo6.py", "odoo7.py")
        cmd = "arcangelo -Podoo -fiw -F6.1 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo10.py", "odoo11.py")
        cmd = "arcangelo -Podoo -fiw -F10.0 -b11.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo6.py", "odoo7.py")
        cmd = "arcangelo -Podoo -fiw -F6.1 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

    def test_12_13_migrate_module(self):
        file_list = [
            "__manifest__.py",
            "__init__.py",
            "models/partner.py",
        ]
        self._test_module(file_list, version_from="12.0", version_to="13.0")

    def test_12_10_migrate_module(self):
        file_list = [
            "__manifest__.py",
            "__init__.py",
            "models/partner.py",
        ]
        self._test_module(file_list, version_from="12.0", version_to="10.0")

    def test_12_8_migrate_module(self):
        file_list = [
            ["__manifest__.py", "__openerp__.py"],
            "__init__.py",
            "models/partner.py",
        ]
        self._test_module(file_list, version_from="12.0", version_to="8.0")

    def test_12_7_migrate_module(self):
        file_list = [
            ["__manifest__.py", "__openerp__.py"],
            "__init__.py",
            "models/partner.py",
        ]
        self._test_module(file_list, version_from="12.0", version_to="7.0")

    def test_12_12_migrate_module(self):
        file_list = [
            "__manifest__.py",
            "__init__.py",
            "models/partner.py",
        ]
        self._test_module(file_list, version_from="12.0", version_to="12.0")

    def test_13_12_backport(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo13.py", "odoo12.py")
        cmd = "arcangelo -Podoo -fiw -F13.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "odoo13_view.xml", "odoo12_view.xml"
        )
        cmd = "arcangelo -Podoo -fiw -F13.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(res_fqn, tgt_fqn),
            "File %s differs %s" % (res_fqn, tgt_fqn),
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo7.py", "odoo6.py")
        cmd = "arcangelo -Podoo -fiw -F7.0 -b6.1 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo11.py", "odoo10.py")
        cmd = "arcangelo '-R -basest_str' -Podoo -fiw -F11.0 -b10.0 %s -o %s" % (
            src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

    def test_90(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname(
            "history.rst", "CHANGELOG.rst"
        )
        last_date = datetime.strftime((datetime.now() - timedelta(days=10)), "%Y-%m-%d")
        today = datetime.strftime(datetime.now(), "%Y-%m-%d")
        with open(src_fqn, "r") as fd:
            content = fd.read().replace("####-##-##", last_date)
        with open(res_fqn, "w") as fd:
            fd.write(content)
        with open(tgt_fqn, "r") as fd:
            content = fd.read().replace("####-##-##", today)
        with open(tgt_fqn, "w") as fd:
            fd.write(content)

        cmd = "arcangelo -fi --test-res-msg='%s' %s" % (
            "* [QUA] Valid result 100% (14: 0+14) [10 TestPoint]",
            res_fqn,
        )
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )

        with open(res_fqn, "r") as fd:
            content = fd.read().replace("12.0.1.2.3", "10.0.1.2.3")
        with open(res_fqn, "w") as fd:
            fd.write(content)
        cmd = "arcangelo -fi -F10.0 -b12.0 %s" % (res_fqn,)
        sts, stdout, stderr = z0lib.os_system_traced(cmd, rtime=False)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(res_fqn, tgt_fqn), "File %s differs %s" % (res_fqn, tgt_fqn)
        )


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
