#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2018-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
# import os
# import os.path
import sys
from zerobug import Z0test


__version__ = "1.0.0.3"

MODULE_ID = 'z0bug_odoo'


def version():
    return __version__


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0test.main(
        Z0test.parseoptest(sys.argv[1:],
            version=version())))
