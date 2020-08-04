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
"""
     Test module wok_code
"""

# import pdb
import os
import os.path
import sys
# import unittest2
from os0 import os0
from wok_code import build

TEST_FAILED = 1
TEST_SUCCESS = 0
REQ_TEST_VERSION = "0.1.17.3"
MODULE_ID = 'wok_code'
# max # of major test id
MAX_TEST_NUM = 3
# num of test to execute (at the end must be equal to text_ctr)
TOT_TEST2EXEC = 6


class Test():

    def __init__(self, module_id):
        self.test_ctr = 0
        self.tot_test2exec = TOT_TEST2EXEC
        self.gbl_test_num = -1
        self.module_id = module_id
        self.test_conf_fn = module_id + '_test.profile'
        self.fd = None

    def msg_new_test(self, test_num):
        self.test_ctr += 1
        if test_num != self.gbl_test_num:
            self.gbl_test_num = test_num
            self.msg_test(True, test_num)
        else:
            self.msg_test(False, test_num)

    def msg_test(self, newline, test_num):
        # if test_ctr >= 39 and test_ctr <= 40:  # debug
        #     import pdb
        #     pdb.set_trace()
        txt = "Test {0:>2}){1:>3}/{2:3}".format(test_num,
                                                self.test_ctr,
                                                self.tot_test2exec)
        if not newline:
            print "\x1b[2A"
        os0.wlog(txt)

    @property
    def test_executed(self):
        return self.test_ctr

    def open_conf(self, test_id):
        valid_id = False
        test_id = '[test_%02d]' % test_id
        try:
            self.fd = open(self.test_conf_fn, 'rb')
        except BaseException:
            self.fd = None
            return False
        while not valid_id:
            line = self.fd.readline()
            if not line:
                break
            elif line.find(test_id) == 0:
                valid_id = True
        return valid_id

    def next_conf(self):
        line = self.fd.readline()
        return line

    def close_conf(self):
        try:
            self.fd.close()
        except BaseException:
            pass
        self.fd = None

    def test_00(self, test_num):
        if not self.open_conf(test_num):
            os0.wlog('test_%02d not defined in configuration file %s' %
                     (test_num, self.test_conf_fn))
            self.close_conf()
            return TEST_FAILED

        self.msg_new_test(test_num)
        prm = build.parse_args(['-btvT', 'pypi'])
        if 'template' not in prm or prm['template'] != 'pypi':
            os0.wlog('Test failed: option -T')
            return TEST_FAILED

        self.msg_new_test(test_num)
        if 'modname' not in prm or prm['modname'] != 'midea':
            os0.wlog('Test failed: default option -n')
            return TEST_FAILED

        self.msg_new_test(test_num)
        prm = build.parse_args(['-btvT', 'pypi', '-n', 'testcode'])
        if 'modname' not in prm or prm['modname'] != 'testcode':
            os0.wlog('Test failed: ption -n')
            return TEST_FAILED

        self.msg_new_test(test_num)
        conf_fn = self.module_id + '.conf'
        prm = build.parse_args(['-btvT',
                                'pypi',
                                '-c',
                                conf_fn],
                               True)
        if os.path.isfile('/etc/odoo-server.conf'):
            if 'conf_fn' not in prm or\
                    prm['conf_fn'] != ['/etc/odoo-server.conf', conf_fn]:
                os0.wlog('Test failed: option -c')
                return TEST_FAILED
        elif os.path.isfile('/etc/openerp-server.conf'):
            if 'conf_fn' not in prm or\
                    prm['conf_fn'] != ['/etc/openerp-server.conf', conf_fn]:
                os0.wlog('Test failed: option -c')
                return TEST_FAILED

        self.close_conf()
        return TEST_SUCCESS

    def test_01(self, test_num):
        if not self.open_conf(test_num):
            os0.wlog('test_%02d not defined in configuration file %s' %
                     (test_num, self.test_conf_fn))
            self.close_conf()
            return TEST_FAILED
        self.msg_new_test(test_num)
        self.msg_new_test(test_num)
        return TEST_SUCCESS
        # return TEST_FAILED

    def main(self):
        """Unit test main."""
        # Check for target software version
        required_version = os.environ.get(self.module_id.upper() + '_VERSION')
        if not required_version:
            required_version = REQ_TEST_VERSION
        pkg_version = build.version()
        if required_version and pkg_version.find(required_version) < 0:
            print "Test not executable: invalid version!"
            print "Required version:", required_version
            print "Package version:", pkg_version
            return TEST_FAILED
        # Need debug mode to avoid security fault in Linux
        os0.set_debug_mode(True)
        title = "%s regression test. Version: %s" % (self.module_id,
                                                     REQ_TEST_VERSION)
        # Remove test log file if executed previous crashed test
        tlog_fn = self.module_id + "_test.log"
        os0.set_tlog_file(tlog_fn)
        tlog_pathname = os0.tlog_fn
        # Set no file log
        os0.set_tlog_file('', echo=True)
        if os.path.isfile(tlog_pathname):
            os.remove(tlog_pathname)
        # Test if running in travis-ci emulator (DEV_ENVIRONMENT)
        if 'DEV_ENVIRONMENT' in os.environ \
                and os.environ['DEV_ENVIRONMENT'].find(self.module_id):
            LOCAL_ECHO = False
        else:
            LOCAL_ECHO = True
        tlog_fn = './' + self.module_id + "_test.log"
        os0.set_tlog_file(tlog_fn, new=True, echo=LOCAL_ECHO)
        os0.wlog(title)
        # Test execution body
        test_num = 0
        sts = 0
        for i in range(MAX_TEST_NUM):
            tname = "test_{0:02}".format(test_num)
            if hasattr(self, tname):
                sts = getattr(self, tname)(test_num)
                if sts:
                    break
            test_num += 1
        # Result
        if sts == 0:
            os0.wlog("Ran {0} {1} tests".format(self.test_ctr,
                                                MODULE_ID))
        else:
            os0.wlog("****** Test {0} failed ******".format(MODULE_ID))
        return sts


if __name__ == "__main__":
    # pdb.set_trace()
    T = Test(MODULE_ID)
    sys.exit(T.main())
