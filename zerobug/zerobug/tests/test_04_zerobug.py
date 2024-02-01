#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))
from zerobug import z0test                                                # noqa: E402

__version__ = "2.0.14"

MODULE_ID = 'zerobug'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    # def __init__(self, z0bug):
    #     z0bug.inherit_cls(self)

    def test_01(self):
        self.assertTrue(True, msg_info="assertTrue()")
        self.assertFalse(False, msg_info="assertFalse()")
        self.assertEqual("equal", "equal", msg_info="assertEqual()")
        self.assertNotEqual("left", "right", msg_info="assertNotEqual()")
        self.assertLess(1, 2, msg_info="assertLess()")
        self.assertLessEqual(1, 1, msg_info="assertLessEqual()")
        self.assertLessEqual(1, 2, msg_info="assertLessEqual()")
        self.assertGreater(2, 1, msg_info="assertGreater()")
        self.assertGreaterEqual(1, 1, msg_info="assertGreaterEqual()")
        self.assertGreaterEqual(2, 1, msg_info="assertGreaterEqual()")
        self.assertIn("a", "abc", msg_info="assertIn()")
        self.assertIn("a", ["a", "b", "c"], msg_info="assertIn()")
        self.assertNotIn("z", "abc", msg_info="assertNotIn()")
        self.assertNotIn("z", ["a", "b", "c"], msg_info="assertNotIn()")
        self.assertMatch("abc", ".*", msg_info="assertMatch()")
        self.assertNotMatch("abc", "[0-9]", msg_info="assertNotMatch()")


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )





