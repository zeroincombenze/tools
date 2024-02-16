# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import sys
import os

# from zerobug import Z0BUG
from python_plus import (_b, _u, bstrings, bytestr_type, qsplit, text_type,
                         unicodes)
from zerobug import z0test

MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "2.0.11"


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        sts = self.Z.test_result(z0ctx,
                                 'python version',
                                 os.getenv("TRAVIS_PYTHON_VERSION"),
                                 "%d.%d" % (sys.version_info[0], sys.version_info[1]))

        btext = b'abcdef'
        res = isinstance(btext, bytestr_type)
        sts += self.Z.test_result(
            z0ctx, "isinstance(b'abcdef', bytestr_type)", True, res
        )

        utext = 'abcdef'
        res = isinstance(utext, text_type)
        sts += self.Z.test_result(
            z0ctx, "res = isinstance(u'abcdef', text_type)", True, res
        )

        res = isinstance(_b(btext), bytestr_type)
        sts += self.Z.test_result(
            z0ctx, "isinstance(_b(b'abcdef'), bytestr_type)", True, res
        )

        res = isinstance(_u(btext), text_type)
        sts += self.Z.test_result(
            z0ctx, "isinstance(_u(b'abcdef'), text_type)", True, res
        )

        res = isinstance(_u(utext), text_type)
        sts += self.Z.test_result(
            z0ctx, "isinstance(_u(u'abcdef'), text_type)", True, res
        )

        res = isinstance(_b(utext), bytestr_type)
        sts += self.Z.test_result(
            z0ctx, "isinstance(_b(u'abcdef'), bytestr_type)", True, res
        )
        return sts

    def test_02(self, z0ctx):
        btext = [b'abc', b'def']
        res = unicodes(btext)
        sts = self.Z.test_result(
            z0ctx, "unicodes([b'abc',b'def'])", ['abc', 'def'], res
        )

        res = bstrings(btext)
        sts += self.Z.test_result(
            z0ctx, "bstrings([b'abc',b'def'])", [b'abc', b'def'], res
        )

        utext = ['abc', 'def']
        res = bstrings(utext)
        sts += self.Z.test_result(
            z0ctx, "bstrings([u'abc',u'def'])", [b'abc', b'def'], res
        )

        res = unicodes(utext)
        sts += self.Z.test_result(
            z0ctx, "unicodes([u'abc',u'def'])", ['abc', 'def'], res
        )
        return sts

    def test_03(self, z0ctx):
        btext = {b'1': b'abc', b'2': b'def'}
        res = unicodes(btext)
        sts = self.Z.test_result(
            z0ctx,
            "unicodes({{b'1': b'abc', b'2':  b'def'})",
            {'1': 'abc', '2': 'def'},
            res,
        )

        res = bstrings(btext)
        sts += self.Z.test_result(
            z0ctx,
            "bstrings({{b'1': b'abc', b'2':  b'def'})",
            {b'1': b'abc', b'2': b'def'},
            res,
        )

        utext = {'1': 'abc', '2': 'def'}
        res = bstrings(utext)
        sts += self.Z.test_result(
            z0ctx,
            "bstrings({u'1': u'abc', u'2':  u'def'})",
            {b'1': b'abc', b'2': b'def'},
            res,
        )

        res = unicodes(utext)
        sts += self.Z.test_result(
            z0ctx,
            "unicodes({u'1': u'abc', u'2':  u'def'})",
            {'1': 'abc', '2': 'def'},
            res,
        )
        return sts

    def test_04(self, z0ctx):
        res = qsplit(b'abc,def', b',')
        sts = self.Z.test_result(
            z0ctx, "qsplit(b'abc,def', b',')", [b'abc', b'def'], res
        )
        res = qsplit(b'"a,b",def', b',')
        sts += self.Z.test_result(
            z0ctx, "qsplit(b'\"a,b\",def', b',')", [b'a,b', b'def'], res
        )
        res = qsplit(b'"\'a\',b",def', b',')
        sts += self.Z.test_result(
            z0ctx, "qsplit(b'\"\'a\',b\",def', b',')", [b'\'a\',b', b'def'], res
        )
        return sts

    def test_05(self, z0ctx):
        res = qsplit(b'abc,def', b',', enquote=True)
        sts = self.Z.test_result(
            z0ctx, "qsplit(b'abc,def', b','), enquote=True", [b'abc', b'def'], res
        )
        res = qsplit(b'"a,b",def', b',', enquote=True)
        sts += self.Z.test_result(
            z0ctx, "qsplit(b'\"a,b\",def', b','), enquote=True", [b'"a,b"', b'def'], res
        )
        res = qsplit(b'"\'a\',b",def', b',', enquote=True)
        sts += self.Z.test_result(
            z0ctx,
            "qsplit(b'\"\'a\',b\",def', b','), enquote=True",
            [b'"\'a\',b"', b'def'],
            res,
        )
        return sts

    def test_06(self, z0ctx):
        res = qsplit(b'"\\\"abc\\\"",def', b',', escape='\\')
        sts = self.Z.test_result(
            z0ctx,
            "qsplit(b'\"\\\"abc\\\"\",def', b','), escape='\\'",
            [b'"abc"', b'def'],
            res,
        )
        res = qsplit(b'abc, def', b',', strip=True)
        sts += self.Z.test_result(
            z0ctx, "qsplit(b'abc, def', b','), strip=True", [b'abc', b'def'], res
        )
        res = qsplit(b'abc,def,ghi', b',', 1)
        sts += self.Z.test_result(
            z0ctx, "qsplit(b'abc,def', b',', 1)", [b'abc', b'def,ghi'], res
        )
        return sts

    def test_07(self, z0ctx):
        res = qsplit('abc,def', ',')
        sts = self.Z.test_result(
            z0ctx, "qsplit(u'abc,def', u',')", ['abc', 'def'], res
        )
        res = qsplit('"a,b",def', ',')
        sts += self.Z.test_result(
            z0ctx, "qsplit(u'\"a,b\",def', u',')", ['a,b', 'def'], res
        )
        res = qsplit('"\'a\',b",def', ',')
        sts += self.Z.test_result(
            z0ctx, "qsplit(u'\"\'a\',b\",def', u',')", ['\'a\',b', 'def'], res
        )
        return sts


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


