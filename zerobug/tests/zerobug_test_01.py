#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import os.path
import sys
# pdb.set_trace()
from zerobug import Z0test
import dummylib


__version__ = "0.2.11"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


# Run main if executed as a script
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    if os.name == 'posix':
        if os.environ.get('HOSTENV', '') == 'travis':
            UT_LIST = ["__version_0_" + __version__]
        else:
            UT_LIST = ["__version_0_" + __version__,
                       "__version_1_0.2.3/etc/z0librc"]
        UT_LIST.append("__version_V_0.2.0" + os.path.join(Z.test_dir,
                                                          "dummy_01.py"))
        UT_LIST.append("__version_v_0.2.1" + os.path.join(Z.test_dir,
                                                          "dummy_01.py"))
        UT_LIST.append("__version_P_0.2.2" + os.path.join(Z.test_dir,
                                                          "dummy_01.py"))
    else:                                                   # pragma: no cover
        UT_LIST = ["__version_0_" + __version__,
                   "__version_V_0.2.0" + os.path.join(Z.test_dir,
                                                      "dummy_01.py"),
                   "__version_v_0.2.1" + os.path.join(Z.test_dir,
                                                      "dummy_01.py"),
                   "__version_P_0.2.2" + os.path.join(Z.test_dir,
                                                      "dummy_01.py")]
    sts = Z.main_file(ctx, UT=UT_LIST)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
