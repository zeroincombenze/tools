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
from zerobug import Z0BUG


__version__ = "0.2.2.24"

MODULE_ID = 'maintainer-quality-tools'


def version():
    return __version__


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0BUG.main_file(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()))
    )

