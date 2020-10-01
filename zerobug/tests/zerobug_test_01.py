# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function,unicode_literals
# from past.builtins import basestring

# import os
import os.path
import sys
from zerobug import Z0BUG

__version__ = "1.0.0.4"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


# Run main if executed as a script
if __name__ == "__main__":
    ctx = Z0BUG.parseoptest(sys.argv[1:],
                            version=version())
    z0lib_file = ''
    for fn in ('../../z0lib/z0lib/z0librc',
               '../z0lib/z0librc',
               os.path.expanduser('~/tools/z0lib/z0librc')):
        if os.path.isfile(fn):
            z0lib_file = fn
            break
    UT_LIST = ["__version_0_" + __version__]
    if z0lib_file:
        UT_LIST.append("__version_1_1.0.0%s" % z0lib_file)
    UT_LIST.append("__version_V_0.2.0${testdir}/dummy_01.py")
    UT_LIST.append("__version_v_0.2.1${testdir}/dummy_01.py")
    UT_LIST.append("__version_P_0.2.2${testdir}/dummy_01.py")
    exit(Z0BUG.main(ctx, UT=UT_LIST))
