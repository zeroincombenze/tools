#!/usr/bin/env python3
# flake8: noqa - pylint: skip-file
"""
This file contains python3 code from python 2-3 template
"""
# from __future__ import print_function, unicode_literals
# from future import standard_library
# import os
import sys


def test_string():
    print("")
    stext = "abcd"
    print(">>> stext = \"abcd\"  # type is", type(stext))
    utext = u"unicode"
    print(">>> utext = u\"unicode\"  # type is", type(utext))
    btext = b"bytes"
    print(">>> btext = b\"bytes\"  # type is", type(btext))
    print(">>> isinstance(stext, str) -> ", isinstance(stext, str))
    print(">>> isinstance(utext, str) -> ", isinstance(utext, str))
    print(">>> isinstance(btext, str) -> ", isinstance(btext, str))
    print("")
    stext = "String formatting %s" % "like C"
    print(">>> \"String formatting %s\" % \"like C\"")
    stext = "Format emoticons %s" % "🏆🥇"
    print(">>> \"Format emoticons %s\" % \"🏆🥇\"")
    stext = str(b"Format emoticons %s") % "🏆🥇"
    print(">>> \"Format emoticons str(b'%s')\" % \"🏆🥇\"")
    utext = b"Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87".decode("utf-8")
    print("b\"Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87\".decode(\"utf-8\")",
          type(utext), utext)
    print(utext)


def test_int():
    print("")
    k = 9223372036854775808
    print("isinstance(%s, int) -> %s" % (k, isinstance(k, int)))


def test_raise():
    print("")
    print(">>> try:")
    try:
        print(">>>     fd = open(\"\", \"r\")")
        open("", "r")
    except FileNotFoundError as e:
        print(">>> except FileNotFoundError as '%s'" % e)


def test_io(fn):
    print("")
    with open(fn, "r") as fd:
        utext = fd.read()
    print(">>> with open(fn, \"r\") as fd:")
    print(type(utext))


def main(args):
    PYMODE = "3"
    print(args[0] + " running in python" + PYMODE + " pure mode")
    print("Test to stderr", file=sys.stderr)
    test_raise()
    test_string()
    test_int()
    test_io(args[0])
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
