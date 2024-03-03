# -*- coding: utf-8 -*-
# Copyright (C) 2015-2024 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function
from future.utils import PY2

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

    def test_01(self):
        self.assertEqual(os.getenv("TRAVIS_PYTHON_VERSION"),
                         "%d.%d" % (sys.version_info[0], sys.version_info[1]))

        btext = 'abcdef' if PY2 else b'abcdef'
        self.assertTrue(isinstance(btext, bytestr_type),
                        msg_info="isinstance(b'abcdef', bytestr_type)")

        utext = u'abcdef' if PY2 else 'abcdef'
        self.assertTrue(isinstance(utext, text_type),
                        msg_info="isinstance(u'abcdef', text_type)")

        self.assertTrue(isinstance(_b(btext), bytestr_type),
                        msg_info="isinstance(_b(b'abcdef'), bytestr_type)")

        self.assertTrue(isinstance(_u(btext), text_type),
                        msg_info="isinstance(_u(b'abcdef'), text_type)")

        self.assertTrue(isinstance(_u(utext), text_type),
                        msg_info="isinstance(_u(u'abcdef'), text_type)")

        self.assertTrue(isinstance(_b(utext), bytestr_type),
                        msg_info="isinstance(_b(u'abcdef'), bytestr_type)")

    def test_02(self):
        btext = ['abc', 'def'] if PY2 else [b'abc', b'def']
        self.assertEqual(
            [u'abc', u'def'],
            unicodes(btext),
            msg_info="unicodes([b'abc',b'def'])"
        )

        self.assertEqual(
            [b'abc', b'def'],
            bstrings(btext),
            msg_info="bstrings([b'abc',b'def'])"
        )

        utext = [u'abc', u'def'] if PY2 else ['abc', 'def']
        self.assertEqual(
            [b'abc', b'def'],
            bstrings(utext),
            msg_info="bstrings([u'abc',u'def'])"
        )

        self.assertEqual(
            [u'abc', u'def'],
            unicodes(utext),
            msg_info="unicodes([u'abc',u'def'])"
        )

    def test_03(self):
        btext = {'1': 'abc', '2': 'def'} if PY2 else {b'1': b'abc', b'2': b'def'}
        self.assertEqual(
            {u'1': u'abc', u'2': u'def'},
            unicodes(btext),
            msg_info="unicodes({b'1': b'abc', b'2': b'def'})"
        )

        self.assertEqual(
            {b'1': b'abc', b'2': b'def'},
            bstrings(btext),
            msg_info="bstrings({u'1': u'abc', u'2': u'def'})"
        )

        utext = {u'1': u'abc', u'2': u'def'} if PY2 else {'1': 'abc', '2': 'def'}
        self.assertEqual(
            {b'1': b'abc', b'2': b'def'},
            bstrings(utext),
            msg_info="bstrings({u'1': u'abc', u'2': u'def'})"
        )

        self.assertEqual(
            {u'1': u'abc', u'2': u'def'},
            unicodes(utext),
            msg_info="unicodes({u'1': u'abc', u'2': u'def'})"
        )

    def test_04(self):
        self.assertEqual(
            ['abc', 'def'] if PY2 else [b'abc', b'def'],
            qsplit(b'abc,def', b','),
            msg_info="qsplit(b'abc,def', b',')"
        )

        self.assertEqual(
            ['a,b', 'def'] if PY2 else [b'a,b', b'def'],
            qsplit(b'"a,b",def', b','),
            msg_info="qsplit(b'\"a,b\",def', b',')"
        )

        self.assertEqual(
            ['\'a\',b', 'def'] if PY2 else [b'\'a\',b', b'def'],
            qsplit(b'"\'a\',b",def', b','),
            msg_info="qsplit(b'\"\'a\',b\",def', b',')"
        )

    def test_05(self):
        self.assertEqual(
            ['abc', 'def'] if PY2 else [b'abc', b'def'],
            qsplit(b'abc,def', b',', enquote=True),
            msg_info="qsplit(b'abc,def', b','), enquote=True"
        )

        self.assertEqual(
            ['"a,b"', 'def'] if PY2 else [b'"a,b"', b'def'],
            qsplit(b'"a,b",def', b',', enquote=True),
            msg_info="qsplit(b'\"a,b\",def', b','), enquote=True"
        )

        self.assertEqual(
            ['"\'a\',b"', 'def'] if PY2 else [b'"\'a\',b"', b'def'],
            qsplit(b'"\'a\',b",def', b',', enquote=True),
            msg_info="qsplit(b'\"\'a\',b\",def', b','), enquote=True"
        )

    def test_06(self):
        self.assertEqual(
            ['"abc"', 'def'] if PY2 else [b'"abc"', b'def'],
            qsplit(b'"\\\"abc\\\"",def', b',', escape='\\'),
            msg_info="qsplit(b'\"\\\"abc\\\"\",def', b','), escape='\\'"
        )

        self.assertEqual(
            ['abc', 'def'] if PY2 else [b'abc', b'def'],
            qsplit(b'abc, def', b',', strip=True),
            msg_info="qsplit(b'abc, def', b','), strip=True"
        )

        self.assertEqual(
            ['abc', 'def,ghi'] if PY2 else [b'abc', b'def,ghi'],
            qsplit(b'abc,def,ghi', b',', 1),
            msg_info="qsplit(b'abc,def', b',', 1)"
        )

    def test_07(self, z0ctx):
        self.assertEqual(
            [u'abc', u'def'] if PY2 else ['abc', 'def'],
            qsplit('abc,def', ','),
            msg_info="qsplit(u'abc,def', u',')"
        )

        self.assertEqual(
            [u'a,b', u'def'] if PY2 else ['a,b', 'def'],
            qsplit('"a,b",def', ','),
            msg_info="qsplit(u'\"a,b\",def', u',')"
        )

        self.assertEqual(
            [u'\'a\',b', u'def'] if PY2 else ['\'a\',b', 'def'],
            qsplit('"\'a\',b",def', ','),
            msg_info="qsplit(u'\"\'a\',b\",def', u',')"
        )


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


