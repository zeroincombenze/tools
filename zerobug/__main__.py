#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import sys
from zerobug import z0test, internal_main

__version__ = "2.0.20"


def version():
    return __version__


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    if cli_args and any(
            [arg in ("-V", "--version", "--copy-pkg-data") for arg in cli_args]):
        return internal_main(cli_args)
    return z0test.main(z0test.parseoptest(cli_args, version=version()))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
