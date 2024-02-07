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


__version__ = "2.0.14"

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
        self.odoo_fakedir = os.path.join(self.testdir, "data", "fake")
        self.odoo_matchdir = os.path.join(self.testdir, "data", "match")
        self.odoo_testdir = os.path.join(self.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "arcangelo.py")
        )

    def get_fake_fullname(self, fn):
        fqn = os.path.join(self.odoo_fakedir, fn)
        if not os.path.isfile(fqn):
            fqn = os.path.join(self.odoo_datadir, fn)
        return fqn

    def get_match_fullname(self, fn):
        fqn = os.path.join(self.odoo_matchdir, fn)
        if not os.path.isfile(fqn):
            fqn = os.path.join(self.odoo_testdir, fn)
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

    def test_02_api_py(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("old_api_02.py",
                                                          "new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("old_api_bis_02.py",
                                                          "new_api_py3_02.py")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("new_api_py3_02.py",
                                                          "old_api_02.py")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("new_api_py2_02.py",
                                                          "new_api_py3_02.py")
        cmd = "arcangelo -fw -F10.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("new_api_py3_02.py",
                                                          "new_api_py2_02.py")
        cmd = "arcangelo -fw -F12.0 -b10.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_03_api_xml(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("old_api_03.xml",
                                                          "new_api_03.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("new_api_03.xml",
                                                          "old_api_03.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_04_api_xml(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("old_api_04.xml",
                                                          "new_api_04.xml")
        cmd = "arcangelo -fw -F7.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("new_api_04.xml",
                                                          "old_api_04.xml")
        cmd = "arcangelo -fw -F12.0 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_05_api_py(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("pkg_py2_05.py",
                                                          "pkg_py2_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("pkg_py3_05.py",
                                                          "pkg_py2_05.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_06_api(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("pkg_py2_06.py",
                                                          "pkg_py2_06.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("pkg_py3_06.py",
                                                          "pkg_py2_06.py")
        cmd = "arcangelo -fw --pypi-package %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_07_migrate(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo12.py",
                                                          "odoo13.py")
        cmd = "arcangelo -fw -F12.0 -b13.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo12_view.xml",
                                                          "odoo13_view.xml")
        cmd = "arcangelo -fw -F12.0 -b13.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo6.py",
                                                          "odoo7.py")
        cmd = "arcangelo -fw -F6.1 -b7.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        # src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo7.py",
        #                                                   "odoo8.py")
        # cmd = "arcangelo -fw -F7.0 -b8.0 %s -o %s" % (src_fqn, res_fqn)
        # sts, stdout, stderr = z0lib.run_traced(cmd)
        # self.assertEqual(sts, 0, msg_info=cmd)
        # self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
        #                 "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_08_backport(self):
        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo13.py",
                                                          "odoo12.py")
        cmd = "arcangelo -fw -F13.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo13_view.xml",
                                                          "odoo12_view.xml")
        cmd = "arcangelo -fw -F13.0 -b12.0 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_xmlfn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

        src_fqn, tgt_fqn, res_fqn = self.get_all_fullname("odoo7.py",
                                                          "odoo6.py")
        cmd = "arcangelo -fw -F7.0 -b6.1 %s -o %s" % (src_fqn, res_fqn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg_info=cmd)
        self.assertTrue(self.compare_fn(res_fqn, tgt_fqn),
                        "File %s differs %s" % (res_fqn, tgt_fqn))

    def test_90(self):
        src_ffn = self.get_fake_fullname("CHANGELOG.rst")
        tgt_ffn = self.get_fake_fullname("history.rst")
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

