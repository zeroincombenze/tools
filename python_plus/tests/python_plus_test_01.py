# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Python-plus Regression Test Suite
"""

import os
import os.path
import sys
from zerobug import Z0test
from python_plus import *


__version__ = "0.1.0"

MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0



def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        res = qsplit(b'abc,def', b',')
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'abc,def', b',')",
                                 [b'abc', b'def'],
                                 res)
        res = qsplit(b'"a,b",def', b',')
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"a,b\",def', b',')",
                                  [b'a,b', b'def'],
                                  res)
        res = qsplit(b'"\'a\',b",def', b',')
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"\'a\',b\",def', b',')",
                                  [b'\'a\',b', b'def'],
                                  res)
        return sts

    def test_02(self, z0ctx):
        res = qsplit(b'abc,def', b',', quoted=True)
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'abc,def', b','), quoted=True",
                                 [b'abc', b'def'],
                                 res)
        res = qsplit(b'"a,b",def', b',', quoted=True)
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"a,b\",def', b','), quoted=True",
                                  [b'"a,b"', b'def'],
                                  res)
        res = qsplit(b'"\'a\',b",def', b',', quoted=True)
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"\'a\',b\",def', b','), quoted=True",
                                  [b'"\'a\',b"', b'def'],
                                  res)
        return sts

    def test_03(self, z0ctx):
        res = qsplit(b'"\\\"abc\\\"",def', b',', e='\\')
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'\"\\\"abc\\\"\",def', b','), e='\\'",
                                 [b'"abc"', b'def'],
                                 res)
        res = qsplit(b'abc, def', b',', strip=True)
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'abc, def', b','), strip=True",
                                 [b'abc', b'def'],
                                 res)
        res = qsplit(b'abc,def,ghi', b',', 1)
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'abc,def', b',', 1)",
                                 [b'abc', b'def,ghi'],
                                 res)
        return sts

    def test_04(self, z0ctx):
        res = qsplit(u'abc,def', u',')
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(u'abc,def', u',')",
                                 [u'abc', u'def'],
                                 res)
        res = qsplit(u'"a,b",def', u',')
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(u'\"a,b\",def', u',')",
                                  [u'a,b', u'def'],
                                  res)
        res = qsplit(u'"\'a\',b",def', u',')
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(u'\"\'a\',b\",def', u',')",
                                  [u'\'a\',b', u'def'],
                                  res)
        return sts

if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)
