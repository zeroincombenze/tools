# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

# import os
# import os.path
import sys
from zerobug import Z0BUG
# from python_plus import isbytestr, qsplit

MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "1.0.0.21"


def version():
    return __version__


# Run main if executed as a script
if __name__ == "__main__":
    ctx = Z0BUG.parseoptest(sys.argv[1:],
                        version=version())
    UT_LIST = ["__doctest_${rundir}/egg-info/python_plus.rst"]
    exit(Z0BUG.main(ctx, UT=UT_LIST))
