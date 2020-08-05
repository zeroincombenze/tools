#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import os.path
import sys
from zerobug import Z0BUG


__version__ = "0.3.9.10"

MODULE_ID = 'odoo_score'


def version():
    return __version__


if __name__ == "__main__":
    exit(Z0BUG.main(
        Z0BUG.parseoptest(sys.argv[1:],
                          version=version()))
    )
