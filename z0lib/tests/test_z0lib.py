#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
# import pdb
import os
import sys
from zerobug import Z0test
from z0lib import z0lib


__version__ = "0.2.9"

MODULE_ID = 'z0lib'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        sts = self.Z.test_result(z0ctx,
                                 "Version",
                                 z0lib.__version__,
                                 __version__)
        #
        sts = TEST_SUCCESS
        parser = z0lib.parseoptargs("Unit Test",
                                    "© 2015-2018 by SHS-AV s.r.l.",
                                    version=__version__)
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument('-V')
        parser.add_argument('-v')
        ctx = parser.parseoptargs(['-v'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd -v",
                                 1,
                                 ctx['opt_verbose'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd -v [-n]",
                                 False,
                                 ctx['dry_run'])
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        parser = z0lib.parseoptargs("Unit Test",
                                    "© 2015-2018 by SHS-AV s.r.l.",
                                    version=__version__)
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument('-p', '--path',
                            action='store',
                            dest='opt_path',
                            default='~/',
                            metavar='path')
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
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget [-qv]",
                                 TRES,
                                 ctx['opt_verbose'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget [-n]",
                                 False,
                                 ctx['dry_run'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget [-p]",
                                 '~/',
                                 ctx['opt_path'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget",
                                 'mytarget',
                                 ctx['mytarget'])

        parser = z0lib.parseoptargs("Unit Test",
                                    "© 2015-2018 by SHS-AV s.r.l.",
                                    version=__version__)
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument('-p', '--path',
                            action='store',
                            dest='opt_path',
                            default='~/',
                            metavar='path')
        parser.add_argument('-q')
        parser.add_argument('-V')
        parser.add_argument('-v')
        parser.add_argument('mytarget')
        ctx = parser.parseoptargs(['-q', 'mytarget'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget -q",
                                 0,
                                 ctx['opt_verbose'])

        parser = z0lib.parseoptargs("Unit Test",
                                    "© 2015-2018 by SHS-AV s.r.l.",
                                    version=__version__)
        parser.add_argument('-h')
        parser.add_argument('-n')
        parser.add_argument('-p', '--path',
                            action='store',
                            dest='opt_path',
                            default='~/',
                            metavar='path')
        parser.add_argument('-q')
        parser.add_argument('-V')
        parser.add_argument('-v')
        parser.add_argument('mytarget')
        ctx = parser.parseoptargs(['-v', 'mytarget'])
        sts = self.Z.test_result(z0ctx,
                                 "cmd mytarget -v",
                                 1,
                                 ctx['opt_verbose'])
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main(ctx, RegressionTest)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
