#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import os.path as pth
import sys

# allow using isolated test environment
here = pth.dirname(pth.abspath(__file__))
while pth.basename(here) in ("tests", "scripts"):
    here = pth.dirname(here)
if here not in sys.path:
    sys.path.insert(0, here)
here = pth.dirname(pth.abspath(os.getcwd()))
while pth.basename(here) in ("tests", "scripts"):
    here = pth.dirname(here)
if here not in sys.path:
    sys.path.insert(0, here)

# from z0lib import z0lib  # noqa: E402
# from z0lib.scripts.main import get_metadata  # noqa: E402
from zerobug import z0test  # noqa: E402

__version__ = "2.0.18"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def test_01(self):
        res = False
        # if not self.Z.dry_run:
        self.root = self.build_os_tree(self.os_tree)
        for path in self.os_tree:
            # if not self.Z.dry_run:
            path = os.path.join(self.root, path)
            res = os.path.isdir(path)
            self.assertTrue(res, msg_info='mkdir %s' % path)

    def test_09(self):
        res = False
        # if not self.Z.dry_run:
        self.remove_os_tree(self.os_tree)
        for path in self.os_tree:
            # if not self.Z.dry_run:
            path = os.path.join(self.root, path)
            res = os.path.isdir(path)
            self.assertFalse(res, msg_info='rmdir %s' % path)

    def setup(self):
        self.os_tree = [
            '16.0',
            '16.0/l10n-italy',
            '16.0/l10n-italy/l10n_it_base',
            '/tmp/zerobug',
        ]


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
