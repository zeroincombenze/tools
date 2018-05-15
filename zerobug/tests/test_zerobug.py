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
from zerobug import Z0test


__version__ = "0.2.13"

MODULE_ID = 'zerobug'


def version():
    return __version__


#
# Run main if executed as a script
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    # Just for regression tests
    coveragerc_file = os.path.join(Z.pkg_dir, '.coveragerc')
    coveragerc_bak = os.path.join(Z.pkg_dir, 'coveragerc.bak')
    if not os.path.isfile(coveragerc_bak):
        if os.path.isfile(coveragerc_file):
            os.rename(coveragerc_file, coveragerc_bak)
    if os.path.isfile(coveragerc_file):
        os.remove(coveragerc_file)
    sts = Z0test.main_file(ctx)
    if os.path.isfile(coveragerc_file):
        os.remove(coveragerc_file)
    if os.path.isfile(coveragerc_bak):
        os.rename(coveragerc_bak, coveragerc_file)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
