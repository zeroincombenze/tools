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
from zerobug import z0test


__version__ = "2.0.9"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        if z0ctx['dry_run']:
            sts = self.Z.sanity_check('-q', full=z0ctx)
            z0ctx['ctr'] = 46
        else:
            sts = self.Z.sanity_check('-e', full=z0ctx)
        sts += self.Z.test_result(
            z0ctx,
            'python version',
            os.getenv("TRAVIS_PYTHON_VERSION"),
            "%d.%d" % (sys.version_info[0], sys.version_info[1]),
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
