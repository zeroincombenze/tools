#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))
from z0lib import z0lib                                                    # noqa: E402

__version__ = "2.0.9"

MODULE_ID = 'z0lib'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        # sts = self.Z.test_result(
        #    z0ctx, "Version", z0lib.get_metadata("version"), __version__)
        #
        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2023 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument('-V')
        parser.add_argument('-v')
        ctx = parser.parseoptargs(['-v'])
        sts = self.Z.test_result(z0ctx, "cmd -v", 1, ctx['opt_verbose'])
        sts = self.Z.test_result(z0ctx, "cmd -v [-n]", False, ctx['dry_run'])
        return sts

    def test_02(self, z0ctx):
        # sts = TEST_SUCCESS
        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2023 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument(
            '-p',
            '--path',
            action='store',
            dest='opt_path',
            default='~/',
            metavar='path',
        )
        parser.add_argument('-q')
        parser.add_argument('-V')
        parser.add_argument('-v')
        parser.add_argument('mytarget')
        ctx = parser.parseoptargs(['mytarget'])
        if os.environ.get('VERBOSE_MODE', '') in ('0', '1'):
            TRES = int(os.environ['VERBOSE_MODE'])
        elif os.isatty(0):
            TRES = 1
        else:
            TRES = 0
        sts = self.Z.test_result(z0ctx, "cmd mytarget [-qv]", TRES, ctx['opt_verbose'])
        sts += self.Z.test_result(z0ctx, "cmd mytarget [-n]", False, ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "cmd mytarget [-p]", '~/', ctx['opt_path'])
        sts += self.Z.test_result(z0ctx, "cmd mytarget", 'mytarget', ctx['mytarget'])

        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2023 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument(
            '-p',
            '--path',
            action='store',
            dest='opt_path',
            default='~/',
            metavar='path',
        )
        parser.add_argument('-q')
        parser.add_argument('-V')
        parser.add_argument('-v')
        parser.add_argument('mytarget')
        ctx = parser.parseoptargs(['-q', 'mytarget'])
        sts += self.Z.test_result(z0ctx, "cmd mytarget -q", 0, ctx['opt_verbose'])

        parser = z0lib.parseoptargs(
            "Unit Test", "© 2015-2023 by SHS-AV s.r.l.", version=__version__
        )
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument(
            '-p',
            '--path',
            action='store',
            dest='opt_path',
            default='~/',
            metavar='path',
        )
        parser.add_argument('-q')
        parser.add_argument('-V')
        parser.add_argument('-v')
        parser.add_argument('mytarget')
        ctx = parser.parseoptargs(['-v', 'mytarget'])
        sts += self.Z.test_result(z0ctx, "cmd mytarget -v", 1, ctx['opt_verbose'])
        return sts


# Run main if executed as a script
# if __name__ == "__main__":
#     Z = Z0test
#     ctx = Z.parseoptest(sys.argv[1:],
#                         version=version())
#     exit(Z.main(ctx, RegressionTest))


