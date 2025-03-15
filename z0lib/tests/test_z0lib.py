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
def pkg_here(here):
    while (
        pth.basename(here) in ("tests", "scripts")
        or pth.basename(pth.dirname(here)) == "local"
    ):
        here = pth.dirname(here)
    if here not in sys.path:
        sys.path.insert(0, here)


pkg_here(pth.dirname(pth.abspath(__file__)))  # noqa: E402
pkg_here(pth.abspath(os.getcwd()))  # noqa: E402
from z0lib import z0lib  # noqa: E402
# from z0lib.scripts.main import get_metadata  # noqa: E402
from zerobug import z0test  # noqa: E402

__version__ = "2.0.14"

MODULE_ID = "z0lib"
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def test_01(self):
        # self.assertEqual(__version__, get_metadata()["version"])
        if os.getenv("TRAVIS_PYTHON_VERSION"):
            self.assertEqual(
                os.getenv("TRAVIS_PYTHON_VERSION"),
                "%d.%d" % (sys.version_info[0], sys.version_info[1]))

        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2025 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument("-h")
        parser.add_argument("-n")
        parser.add_argument("-V")
        parser.add_argument("-v")
        ctx = parser.parseoptargs(["-v"])
        self.assertEqual(1, ctx["opt_verbose"], msg_info="cmd -v")
        self.assertEqual(False, ctx["dry_run"], msg_info="cmd -v [-n]")

    def test_02(self):
        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2025 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument("-h")
        parser.add_argument("-n")
        parser.add_argument(
            "-p",
            "--path",
            action="store",
            dest="opt_path",
            default="~/",
            metavar="path",
        )
        parser.add_argument("-q")
        parser.add_argument("-V")
        parser.add_argument("-v")
        parser.add_argument("mytarget")
        ctx = parser.parseoptargs(["mytarget"])
        if os.environ.get("VERBOSE_MODE", "") in ("0", "1"):
            TRES = int(os.environ["VERBOSE_MODE"])
        else:
            TRES = 0
        self.assertEqual(TRES, ctx["opt_verbose"], msg_info="cmd mytarget [-qv]")
        self.assertEqual(False, ctx["dry_run"], msg_info="cmd mytarget [-n]")
        self.assertEqual("~/", ctx["opt_path"], msg_info="cmd mytarget [-p]")
        self.assertEqual("mytarget", ctx["mytarget"], msg_info="cmd mytarget")

        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2025 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument("-h")
        parser.add_argument("-n")
        parser.add_argument(
            "-p",
            "--path",
            action="store",
            dest="opt_path",
            default="~/",
            metavar="path",
        )
        parser.add_argument("-q")
        parser.add_argument("-V")
        parser.add_argument("-v")
        parser.add_argument("mytarget")
        ctx = parser.parseoptargs(["-q", "mytarget"])
        self.assertEqual(0, ctx["opt_verbose"], msg_info="cmd mytarget -q")

        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2025 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument("-h")
        parser.add_argument("-n")
        parser.add_argument(
            "-p",
            "--path",
            action="store",
            dest="opt_path",
            default="~/",
            metavar="path",
        )
        parser.add_argument("-q")
        parser.add_argument("-V")
        parser.add_argument("-v")
        parser.add_argument("mytarget")
        ctx = parser.parseoptargs(["-v", "mytarget"])
        self.assertEqual(1, ctx["opt_verbose"], msg_info="cmd mytarget -v")


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
