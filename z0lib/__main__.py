#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
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
"""z0lib

bash library for tools
"""
from __future__ import print_function
import os
import sys
# try:
#     from wok_code import build
# except:
#     from . import build

# __main__.py is a just dispatcher of module package
# If execution is inside travis-ci emulator or travis-ci environment,
#  (environment variable DEV_ENVIRONMENT is module name)
#  it runs regression test
# Otherwise show module version and docs

MODULE_ID = 'z0lib'
TESTDIR = 'tests'
ALL_TEST_SH = 'all_tests'
VERSION_SH = 'z0lib -V'

if __name__ == "__main__":
    # Test if running in travis-ci emulator (DEV_ENVIRONMENT)
    if 'DEV_ENVIRONMENT' in os.environ \
            and os.environ['DEV_ENVIRONMENT'].find(MODULE_ID):
        if os.path.isdir('./' + TESTDIR):
            os.chdir('./' + TESTDIR)
            if os.path.isfile(ALL_TEST_SH):
                sts = os.system(ALL_TEST_SH)
            else:
                sts = execfile('test_' + MODULE_ID + '.py')
            sys.exit(sts)

    # if called from python modulename
    if VERSION_SH:
        if os.path.isdir(MODULE_ID):
            os.chdir(MODULE_ID)
        os.system(VERSION_SH)
    for text in __doc__.split('\n'):
        print(text)
    sys.exit(0)
