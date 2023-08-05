# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
import unittest
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))
from zerobug import z0testlib                                             # noqa: E402

__version__ = "2.0.9"


def version():
    return __version__


class PypiTest(z0testlib.PypiTest):

    def test_01_version(self):
        self.assertEqual(version(), self.version(), msg_info="Version")


if __name__ == "__main__":
    exit(unittest.main())
