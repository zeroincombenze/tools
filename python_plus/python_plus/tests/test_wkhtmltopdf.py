# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import os
import os.path
import sys

from z0lib import z0lib
from zerobug import z0test

MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "2.0.11"


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
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "vem.py")
        )

    def check_pattern(self, stdout, pattern, cmd):
        for ln in stdout.split("\n"):
            if ln.startswith("Download"):
                self.assertEqual(pattern, ln.split(" ")[1], msg_info=cmd)
                break

    def specific_test(self, disto, version, pattern):
        FH = "RHEL" if disto.startswith("centos") else "Debian"
        cmd = ("python3 ~/build/python_plus/scripts/vem.py -nvv -F%s -E%s "
               "install wkhtmltopdf==%s" % (FH, disto, version))
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.check_pattern(stdout, pattern, cmd)

    def test_01(self):
        version = "0.12.6"
        disto = "ubuntu24"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/packaging/releases/download/"
            "0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
        )

        version = "0.12.6"
        disto = "ubuntu22"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/packaging/releases/download/"
            "0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
        )

        version = "0.12.5"
        disto = "ubuntu22"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/"
            "0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"
        )

        version = "0.12.5"
        disto = "ubuntu20"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/"
            "0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"
        )

        version = "0.12.4"
        disto = "ubuntu20"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/"
            "0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz"
        )

        version = "0.12.1"
        disto = "ubuntu20"
        self.specific_test(
            disto,
            version,
            "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/"
            "0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb"
        )


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


