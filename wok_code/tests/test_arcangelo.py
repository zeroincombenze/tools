#!/home/odoo/devel/venv/bin/python3.8
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
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


__version__ = "2.0.13"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def setup(self):
        # super(RegressionTest, self).setup()
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.path.join(os.getcwd(), "tests")
            self.rundir = os.getcwd()
        self.odoo_datadir = os.path.join(self.testdir, "data")
        if not os.path.isdir(self.odoo_datadir):
            os.mkdir(self.odoo_datadir)
        self.odoo_testdir = os.path.join(self.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "arcangelo.py")
        )

    def get_data_fullname(self, fn):
        ffn = os.path.join(self.odoo_datadir, fn)
        return ffn

    def get_test_fullname(self, fn):
        ffn = os.path.join(self.odoo_testdir, fn)
        return ffn

    def compare_fn(self, src_ffn, tgt_ffn):
        with open(src_ffn, "r") as fd:
            source = fd.read().split("\n")
        with open(tgt_ffn, "r") as fd:
            target = fd.read().split("\n")
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
            source = fd.read().split("\n")
        with open(tgt_ffn, "r") as fd:
            target = fd.read().split("\n")
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

    def test_01_version(self):
        sts, stdout, stderr = z0lib.run_traced("arcangelo --version")
        self.assertEqual(sts, 0, msg_info="arcangelo --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02_api(self):
        src_ffn = self.get_data_fullname("old_api_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("new_api_py3_02.py")))

        src_ffn = self.get_data_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("old_api_02.py")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("old_api_02.py")))

        src_ffn = self.get_data_fullname("new_api_py2_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F10.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("new_api_py3_02.py")))

        src_ffn = self.get_data_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py2_02.py")
        cmd = "arcangelo -fw -F12.0 -b10.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("new_api_py2_02.py")))

        src_ffn = self.get_data_fullname("old_api_b_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("new_api_py3_02.py")))

    def test_03_api(self):
        src_ffn = self.get_data_fullname("old_api_03.xml")
        tgt_ffn = self.get_test_fullname("new_api_03.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_data_fullname("new_api_03.xml")))

        src_ffn = self.get_data_fullname("new_api_03.xml")
        tgt_ffn = self.get_test_fullname("old_api_03.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_data_fullname("old_api_03.xml")))

    def test_04_api(self):
        src_ffn = self.get_data_fullname("old_api_04.xml")
        tgt_ffn = self.get_test_fullname("new_api_04.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_data_fullname("new_api_04.xml")))

        src_ffn = self.get_data_fullname("new_api_04.xml")
        tgt_ffn = self.get_test_fullname("old_api_04.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_data_fullname("old_api_04.xml")))

    def test_05_api(self):
        src_ffn = self.get_data_fullname("pkg_py2_05.py")
        tgt_ffn = self.get_test_fullname("pkg_py3_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        # With future result is like python2
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("pkg_py2_05.py")))

        src_ffn = self.get_data_fullname("pkg_py3_05.py")
        tgt_ffn = self.get_test_fullname("pkg_py2_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("pkg_py2_05.py")))

    def test_06_api(self):
        src_ffn = self.get_data_fullname("pkg_py2_06.py")
        tgt_ffn = self.get_test_fullname("pkg_py3_06.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        # With future result is like python2
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("pkg_py2_06.py")))

        src_ffn = self.get_data_fullname("pkg_py3_06.py")
        tgt_ffn = self.get_test_fullname("pkg_py2_06.py")
        cmd = "arcangelo -fw --pypi-package --python=2 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("pkg_py2_06.py")))

    def test_07_odoo_12_13(self):
        src_ffn = self.get_data_fullname("odoo12.py")
        tgt_ffn = self.get_test_fullname("odoo13.py")
        cmd = "arcangelo -fw -F12.0 -b13.0 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("odoo13_migrated.py")))

        src_ffn = self.get_data_fullname("odoo13.py")
        tgt_ffn = self.get_test_fullname("odoo12.py")
        cmd = "arcangelo -fw -F13.0 -b12.0 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("odoo12.py")))

        src_ffn = self.get_data_fullname("odoo12_view.xml")
        tgt_ffn = self.get_test_fullname("odoo13_view.xml")
        cmd = "arcangelo -fw -F12.0 -b13.0 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_data_fullname("odoo13_view.xml")))

        src_ffn = self.get_data_fullname("odoo13_view.xml")
        tgt_ffn = self.get_test_fullname("odoo12_view.xml")
        cmd = "arcangelo -fw -F13.0 -b12.0 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        # TODO>
        self.assertTrue(
            self.compare_fn(tgt_ffn,
                            self.get_data_fullname("odoo12_view_migrated.xml")))

    def test_90(self):
        src_ffn = self.get_data_fullname("CHANGELOG.rst")
        tgt_ffn = self.get_data_fullname("history.rst")
        last_date = datetime.strftime((datetime.now() - timedelta(days=10)), "%Y-%m-%d")
        today = datetime.strftime(datetime.now(), "%Y-%m-%d")
        with open(src_ffn, "r") as fd:
            content = fd.read().replace("####-##-##", last_date)
        with open(src_ffn, "w") as fd:
            fd.write(content)
        with open(tgt_ffn, "r") as fd:
            content = fd.read().replace("####-##-##", today)
        with open(tgt_ffn, "w") as fd:
            fd.write(content)

        cmd = "arcangelo -f --test-res-msg='%s' %s" % (
            "* [QUA] Valid result 100% (14: 0+14) [10 TestPoint]",
            src_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, src_ffn))

        cmd = "arcangelo -f --test-res-msg='%s' %s" % (
            "* [QUA] Valid result 100% (14: 0+14) [6 TestPoint]\n[4 TestPoint]",
            src_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, src_ffn))


#
# Run main if executed as a script
if __name__ == "__main__":
    # # exit(unittest.main())
    # exit(z0testlib.main())
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
