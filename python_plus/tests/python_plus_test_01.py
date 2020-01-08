# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

# import pdb
import os
import os.path
import sys
from zerobug import Z0BUG
from python_plus import (text_type, bytestr_type,
                         unicodes, bstrings,
                         _u, _b,
                         isbytestr, qsplit)


MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "0.1.2.3"


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        res = sys.version_info[0]
        sts = self.Z.test_result(z0ctx,
                                 "python%s" % res,
                                 res,
                                 res)

        btext = b'abcdef'
        res = isinstance(btext, bytestr_type)
        sts = self.Z.test_result(z0ctx,
                                 "isinstance(b'abcdef', bytestr_type)",
                                 True,
                                 res)

        utext = u'abcdef'
        res = isinstance(utext, text_type)
        sts = self.Z.test_result(z0ctx,
                                 "res = isinstance(u'abcdef', text_type)",
                                 True,
                                 res)

        res = isinstance(_b(btext), bytestr_type)
        sts = self.Z.test_result(z0ctx,
                                 "isinstance(_b(b'abcdef'), bytestr_type)",
                                 True,
                                 res)

        res = isinstance(_u(btext), text_type)
        sts = self.Z.test_result(z0ctx,
                                 "isinstance(_u(b'abcdef'), text_type)",
                                 True,
                                 res)

        res = isinstance(_u(utext), text_type)
        sts = self.Z.test_result(z0ctx,
                                 "isinstance(_u(u'abcdef'), text_type)",
                                 True,
                                 res)

        res = isinstance(_b(utext), bytestr_type)
        sts = self.Z.test_result(z0ctx,
                                 "isinstance(_b(u'abcdef'), bytestr_type)",
                                 True,
                                 res)

    def test_02(self, z0ctx):
        btext = [b'abc', b'def']
        res = unicodes(btext)
        sts = self.Z.test_result(z0ctx,
                                 "unicodes([b'abc',b'def'])",
                                 [u'abc', u'def'],
                                 res)

        res = bstrings(btext)
        sts = self.Z.test_result(z0ctx,
                                 "bstrings([b'abc',b'def'])",
                                 [b'abc', b'def'],
                                 res)

        utext = [u'abc', u'def']
        res = bstrings(utext)
        sts = self.Z.test_result(z0ctx,
                                 "bstrings([u'abc',u'def'])",
                                 [b'abc', b'def'],
                                 res)

        res = unicodes(utext)
        sts = self.Z.test_result(z0ctx,
                                 "unicodes([u'abc',u'def'])",
                                 [u'abc', u'def'],
                                 res)

    def test_03(self, z0ctx):
        btext = {b'1': b'abc',
                 b'2':  b'def'}
        res = unicodes(btext)
        sts = self.Z.test_result(z0ctx,
                                 "unicodes({{b'1': b'abc', b'2':  b'def'})",
                                 {u'1': u'abc', u'2':  u'def'},
                                 res)

        res = bstrings(btext)
        sts = self.Z.test_result(z0ctx,
                                 "bstrings({{b'1': b'abc', b'2':  b'def'})",
                                 {b'1': b'abc', b'2':  b'def'},
                                 res)

        utext = {u'1': u'abc',
                 u'2':  u'def'}
        res = bstrings(utext)
        sts = self.Z.test_result(z0ctx,
                                 "bstrings({u'1': u'abc', u'2':  u'def'})",
                                 {b'1': b'abc', b'2':  b'def'},
                                 res)

        res = unicodes(utext)
        sts = self.Z.test_result(z0ctx,
                                 "unicodes({u'1': u'abc', u'2':  u'def'})",
                                 {u'1': u'abc', u'2':  u'def'},
                                 res)

    def test_04(self, z0ctx):
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

    def test_05(self, z0ctx):
        res = qsplit(b'abc,def', b',', enquote=True)
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'abc,def', b','), enquote=True",
                                 [b'abc', b'def'],
                                 res)
        res = qsplit(b'"a,b",def', b',', enquote=True)
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"a,b\",def', b','), enquote=True",
                                  [b'"a,b"', b'def'],
                                  res)
        res = qsplit(b'"\'a\',b",def', b',', enquote=True)
        sts += self.Z.test_result(z0ctx,
                                  "qsplit(b'\"\'a\',b\",def', b','), enquote=True",
                                  [b'"\'a\',b"', b'def'],
                                  res)
        return sts

    def test_06(self, z0ctx):
        res = qsplit(b'"\\\"abc\\\"",def', b',', escape='\\')
        sts = self.Z.test_result(z0ctx,
                                 "qsplit(b'\"\\\"abc\\\"\",def', b','), escape='\\'",
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

    def test_07(self, z0ctx):
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
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        Test))
