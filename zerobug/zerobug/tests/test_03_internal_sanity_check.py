#!/home/odoo/devel/venv/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import os
import sys

sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))
from zerobug import z0test                                                # noqa: E402


__version__ = "2.0.10"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        z0bug.inherit_cls(self)

    def test_01(self, z0ctx):
        if z0ctx['dry_run']:
            sts = self.Z.sanity_check('-q', full=z0ctx)
            z0ctx['ctr'] = 46
        else:
            sts = self.Z.sanity_check('-e', full=z0ctx)
        self.assertEqual(sts, 0, msg_info="sanity_check()")
        self.assertEqual(
            "%d.%d" % (sys.version_info[0], sys.version_info[1]),
            os.getenv("TRAVIS_PYTHON_VERSION"),
            msg_info='python version'
        )
        return self.ret_sts()


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



