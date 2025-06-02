#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import sys
try:
    from . import z0test
except ImportError:
    import z0testlib
    z0test = z0testlib.Z0test()
except ValueError:
    import z0testlib
    z0test = z0testlib.Z0test()

__version__ = "2.0.19"


def version():
    return __version__


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    return z0test.main(z0test.parseoptest(cli_args, version=version()))


if __name__ == "__main__":
    exit(main(sys.argv[1:]))

