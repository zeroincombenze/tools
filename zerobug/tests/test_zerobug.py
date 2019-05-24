#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import os.path
import sys
from zerobug import Z0BUG


__version__ = "0.2.14.4"


def version():
    return __version__

if __name__ == "__main__":
    ctx = Z0BUG.parseoptest(sys.argv[1:],
                            version=version())
    # Just for regression tests
    coveragerc_file = os.path.join(Z0BUG.rundir, '.coveragerc')
    coveragerc_bak = os.path.join(Z0BUG.rundir, 'coveragerc.bak')
    if not os.path.isfile(coveragerc_bak):
        if os.path.isfile(coveragerc_file):
            os.rename(coveragerc_file, coveragerc_bak)
    if os.path.isfile(coveragerc_file):
        os.remove(coveragerc_file)
    sts = Z0BUG.main_file(ctx)
    if os.path.isfile(coveragerc_file):
        os.remove(coveragerc_file)
    if os.path.isfile(coveragerc_bak):
        os.rename(coveragerc_bak, coveragerc_file)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
