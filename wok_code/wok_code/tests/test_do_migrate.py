#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys

from z0lib import z0lib
from zerobug import z0test


__version__ = "2.0.6"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.root = ''
        self.odoo_datadir = os.path.join(self.Z.testdir, "data")
        if not os.path.isdir(self.odoo_datadir):
            os.mkdir(self.odoo_datadir)
        self.odoo_testdir = os.path.join(self.Z.testdir, "res")
        if not os.path.isdir(self.odoo_testdir):
            os.mkdir(self.odoo_testdir)

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

    def test_01(self, z0ctx):
        sts, stdout, stderr = z0lib.run_traced("do_migrate --version")
        if sts:
            self.Z.test_result(
                z0ctx, "do_migrate --version", 0, sts)
            return sts
        self.Z.test_result(z0ctx, "do_migrate --version", __version__,
                           (stdout + stderr).split("\n")[0])
        return sts

    def test_02(self, z0ctx):
        src_ffn = self.get_fullname("old_api_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "do_migrate -f -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py3_02.py")),
            True)

        src_ffn = self.get_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("old_api_02.py")
        cmd = "do_migrate -f -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(z0ctx,
                           cmd.replace(self.Z.testdir, "."),
                           self.compare_fn(tgt_ffn, self.get_fullname("old_api_02.py")),
                           True)

        src_ffn = self.get_fullname("new_api_py2_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py3_02.py")
        cmd = "do_migrate -f -F10.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py3_02.py")),
            True)

        src_ffn = self.get_fullname("new_api_py3_02.py")
        tgt_ffn = self.get_test_fullname("new_api_py2_02.py")
        cmd = "do_migrate -f -F12.0 -b10.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_fn(tgt_ffn, self.get_fullname("new_api_py2_02.py")),
            True)

    def test_03(self, z0ctx):
        src_ffn = self.get_fullname("old_api_03.xml")
        tgt_ffn = self.get_test_fullname("new_api_03.xml")
        cmd = "do_migrate -f -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_xmlfn(tgt_ffn, self.get_fullname("new_api_03.xml")),
            True)

        src_ffn = self.get_fullname("new_api_03.xml")
        tgt_ffn = self.get_test_fullname("old_api_03.xml")
        cmd = "do_migrate -f -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_xmlfn(tgt_ffn, self.get_fullname("old_api_03.xml")),
            True)

    def test_04(self, z0ctx):
        src_ffn = self.get_fullname("old_api_04.xml")
        tgt_ffn = self.get_test_fullname("new_api_04.xml")
        cmd = "do_migrate -f -F7.0 -b12.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_xmlfn(tgt_ffn, self.get_fullname("new_api_04.xml")),
            True)

        src_ffn = self.get_fullname("new_api_04.xml")
        tgt_ffn = self.get_test_fullname("old_api_04.xml")
        cmd = "do_migrate -f -F12.0 -b7.0 %s -o %s" % (src_ffn, tgt_ffn)
        sts, stdout, stderr = z0lib.run_traced(cmd)
        if sts:
            print("Error %d file %s" % (sts, src_ffn))
            print(stderr)
            return sts
        self.Z.test_result(
            z0ctx,
            cmd.replace(self.Z.testdir, "."),
            self.compare_xmlfn(tgt_ffn, self.get_fullname("old_api_04.xml")),
            True)

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "do_migrate.py"))

    def tearoff(self, z0ctx):
        pass


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )