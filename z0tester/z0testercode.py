#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
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
"""@package docstring
"""


# import pdb
from os0 import os0
import os.path
import sys
from lxml import etree
from struct import *


__version__ = "0.1.2"
TEST_FAILED = 1
TEST_SUCCESS = 0
MODULE_ID = 'z0testercode'
TESTDIR = 'tests'
ALL_TEST_SH = ''
REQ_TEST_VERSION = None
# max # of major test id
MAX_TEST_NUM = 3
# num of test to execute (at the end must be equal to text_ctr)
TOT_TEST2EXEC = 6


class Z0tester():

    def __init__(self, module_id, module_version,
                 ctr=None, abort_on_fail=None):
        self.module_id = module_id
        self.module_version = module_version
        if ctr is None:
            self.test_ctr = 0
        else:
            self.test_ctr = ctr
        if abort_on_fail is None:
            self.abort_on_fail = False
        else:
            self.abort_on_fail = abort_on_fail
        # Test if running in travis-ci emulator (DEV_ENVIRONMENT)
        if 'DEV_ENVIRONMENT' in os.environ \
                and os.environ['DEV_ENVIRONMENT'].find(self.module_id):
            LOCAL_ECHO = False
        else:
            LOCAL_ECHO = True
        tlog_fn = './' + self.module_id + "_test.log"
        os0.set_tlog_file(tlog_fn, echo=LOCAL_ECHO, dir4debug=True)
        title = "%s regression test. Version: %s" % (self.module_id,
                                                     self.module_version)
        os0.wlog(title)

    def test_result(self, test_brief, expected_value, result_value):
        self.test_ctr += 1
        test_msg = "Test %d %s" % (self.test_ctr, test_brief)
        os0.wlog(test_msg)
        if expected_value != result_value:
            os0.wlog("Test failed: expected '%s', found '%s'" %
                     (expected_value, result_value))
            if self.abort_on_fail:
                raise ValueError("Test Failed")
            return TEST_FAILED
        return TEST_SUCCESS


class Z0tester_lxml(Z0tester):
    """Test package lxml
    """
    def all_tests(self):
        sts = 0
        for i in range(MAX_TEST_NUM):
            tname = "test_{0:02}".format(i)
            if hasattr(self, tname):
                sts = getattr(self, tname)()
                if sts:
                    break
        # Result
        if sts == 0:
            os0.wlog("Ran {0} {1} tests".format(self.test_ctr,
                                                self.module_id))
        else:
            os0.wlog("****** Test {0} failed ******".format(self.module_id))
        return sts

    def test_01(self):
        root = etree.Element("root")
        TRES = root.tag
        if self.test_result("root tag",
                            "root",
                            TRES):
            return TEST_FAILED

        root.append(etree.Element("child1"))
        # child2 = etree.SubElement(root, "child2")
        # child3 = etree.SubElement(root, "child3")
        TRES = etree.tostring(root, pretty_print=True)
        TVAL = """<root>
  <child1/>
  <child2/>
  <child3/>
</root>
"""
        if self.test_result("xml tree",
                            TVAL,
                            TRES):
            return TEST_FAILED

        child = root[0]
        TRES = child.tag
        TVAL = "child1"
        if self.test_result("parse tree 1",
                            TVAL,
                            TRES):
            return TEST_FAILED

        TRES = len(root)
        TVAL = 3
        if self.test_result("parse tree 2",
                            TVAL,
                            TRES):
            return TEST_FAILED

        TRES = root.index(root[1])
        TVAL = 1
        if self.test_result("parse tree 3",
                            TVAL,
                            TRES):
            return TEST_FAILED

        return TEST_SUCCESS

    def test_02(self):
        TRES = calcsize('hHiIlL')
        TVAL = 32
        if self.test_result("struct.calcsize",
                            TVAL,
                            TRES):
            return TEST_FAILED

        return TEST_SUCCESS


def main(module_id):
    """Unit test main."""
    # pdb.set_trace()
    # Check for target software version
    required_version = os.environ.get(module_id.upper() + '_VERSION')
    if not required_version:
        required_version = REQ_TEST_VERSION
    # pkg_version = lxml.version()
    # if required_version and pkg_version.find(required_version) < 0:
    #     os0.wlog("Test not executable: invalid version!")
    #     os0.wlog("Required version:", required_version)
    #     os0.wlog("Package version:", pkg_version)
    #     return TEST_FAILED
    # Need debug mode to avoid security fault in Linux
    os0.set_debug_mode(True)
    T = Z0tester_lxml(module_id, REQ_TEST_VERSION, ctr=0)
    return T.all_tests()


if __name__ == "__main__":
    sys.exit(main(MODULE_ID))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
