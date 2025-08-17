# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    os0 Regression Test Suite
"""
from __future__ import print_function, unicode_literals

# import os
# import os.path
import sys

from zerobug import z0test

# from past.builtins import basestring


__version__ = "2.0.1"

MODULE_ID = 'os0'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main(
            z0test.parseoptest(sys.argv[1:], version=version()),
            unittest_list=['__doctest_${rundir}/egg-info/os0_${os_name}.rst'],
        )
    )
