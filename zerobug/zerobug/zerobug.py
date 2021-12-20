#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2021 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
    You can use this file as main all_tests.py too
"""
import sys
from . import z0test

__version__ = "1.0.5"


def version():
    return __version__


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    return z0test.main(z0test.parseoptest(cli_args, version=version()))


if __name__ == "__main__":
    exit(main(sys.argv))