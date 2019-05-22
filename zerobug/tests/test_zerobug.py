#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import os.path
import sys
from zerobug import Z0test


__version__ = "0.2.14.2"

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
