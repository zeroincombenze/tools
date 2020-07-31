#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
    You can use this file as main all_tests.py too
"""
import os
import sys
try:
    import z0testlib
    Z0BUG = z0testlib.Z0test()
except ImportError:
    from zerobug import Z0BUG


__version__ = "0.2.15.3"


def version():
    return __version__

if __name__ == "__main__":
    exit(Z0BUG.main(
        Z0BUG.parseoptest(sys.argv[1:],
                          version=version()))
    )