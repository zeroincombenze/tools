#!/home/odoo/devel/venv/bin/python3.8
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
# import sys
from datetime import datetime, timedelta
# import unittest

from z0lib import z0lib
# from zerobug import z0test
from zerobug import z0testlib                                             # noqa: E402


__version__ = "2.0.11"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


# class RegressionTest:
class PypiTest(z0testlib.PypiTest):
    # def __init__(self, z0bug):
    #     self.Z = z0bug
    #     self.root = ''
    #     self.odoo_datadir = os.path.join(self.Z.testdir, "data")
    #     if not os.path.isdir(self.odoo_datadir):
    #         os.mkdir(self.odoo_datadir)
    #     self.odoo_testdir = os.path.join(self.Z.testdir, "res")
    #     if not os.path.isdir(self.odoo_testdir):
    #         os.mkdir(self.odoo_testdir)

    def setUp(self):
        super(PypiTest, self).setUp()
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.stat.join(os.getcwd(), "tests")
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

    def get_fullname(self, fn):
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

    def test_01(self):
        sts, stdout, stderr = z0lib.run_traced("arcangelo --version")
        self.assertEqual(sts, 0, msg_info="arcangelo --version")
        self.assertEqual(__version__, (stdout + stderr).split("\n")[0])

    def test_02(self):
        src_ffn = self.get_fullname("old_api_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py3_02.py")))

        src_ffn = self.get_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("old_api_02.py")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("old_api_02.py")))

        src_ffn = self.get_fullname("new_api_py2_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F10.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py3_02.py")))

        src_ffn = self.get_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py2_02.py")
        cmd = "arcangelo -fw -F12.0 -b10.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py2_02.py")))

        src_ffn = self.get_fullname("old_api_b_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py3_02.py")))

    def test_03(self):
        src_ffn = self.get_fullname("old_api_03.xml")
        tgt_ffn = self.get_test_fullname("new_api_03.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_fullname("new_api_03.xml")))

        src_ffn = self.get_fullname("new_api_03.xml")
        tgt_ffn = self.get_test_fullname("old_api_03.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_fullname("old_api_03.xml")))

    def test_04(self):
        src_ffn = self.get_fullname("old_api_04.xml")
        tgt_ffn = self.get_test_fullname("new_api_04.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_fullname("new_api_04.xml")))

        src_ffn = self.get_fullname("new_api_04.xml")
        tgt_ffn = self.get_test_fullname("old_api_04.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_xmlfn(tgt_ffn, self.get_fullname("old_api_04.xml")))

    def test_05(self):
        src_ffn = self.get_fullname("pkg_py2_05.py")
        tgt_ffn = self.get_test_fullname("pkg_py3_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        # With future result is like python2
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("pkg_py2_05.py")))

        src_ffn = self.get_fullname("pkg_py3_05.py")
        tgt_ffn = self.get_test_fullname("pkg_py2_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("pkg_py2_05.py")))

    def test_06(self):
        src_ffn = self.get_fullname("pkg_py2_06.py")
        tgt_ffn = self.get_test_fullname("pkg_py3_06.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        # With future result is like python2
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("pkg_py2_06.py")))

        src_ffn = self.get_fullname("pkg_py3_06.py")
        tgt_ffn = self.get_test_fullname("pkg_py2_06.py")
        cmd = "arcangelo -fw --pypi-package --python=2 %s -o %s" % (
            src_ffn,
            tgt_ffn,
        )
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(
            self.compare_fn(tgt_ffn, self.get_fullname("pkg_py2_06.py")))

    def test_90(self):
        src_ffn = self.get_fullname("CHANGELOG.rst")
        tgt_ffn = self.get_fullname("history.rst")
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
    # exit(unittest.main())
    exit(z0testlib.main())

