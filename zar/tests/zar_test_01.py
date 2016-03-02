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
    Zeroincombenze® Archives Replica Regression Test Suite
"""

# import pdb
# import os.path
import sys
from z0testlib import Z0test


__version__ = "0.1.2"

MODULE_ID = 'zar'


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, ctx):
        """Sanity autotest #1"""
        msg = 'prova'
        test_value = True
        res_value = True
        sts = self.Z.test_result(ctx, msg, test_value, res_value)
        return sts

    def test_02(self, ctx):
        """Sanity autotest #1"""
        msg = 'prova2'
        test_value = True
        res_value = True
        sts = self.Z.test_result(ctx, msg, test_value, res_value)
        return sts
#
# Run main if executed as a script
if __name__ == "__main__":
    # pdb.set_trace()
    Z = Z0test()
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
