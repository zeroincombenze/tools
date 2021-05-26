# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function,unicode_literals
# from past.builtins import basestring

import sys
from zerobug import Z0BUG


__version__ = "1.0.1.1"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


# Run main if executed as a script
if __name__ == "__main__":
    UT_LIST = ["__doctest_${rundir}/egg-info/description.rst"]
    exit(Z0BUG.main(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        UT=UT_LIST))
