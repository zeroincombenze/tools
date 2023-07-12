#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
"""
This file contains python2 code from python 2-3 template
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
    print(">>> isinstance(stext, basestring) -> ", isinstance(stext, basestring))
    print(">>> isinstance(utext, basestring) -> ", isinstance(utext, basestring))
    print(">>> isinstance(btext, basestring) -> ", isinstance(btext, basestring))
    print("")
    stext = "String formatting %s" % "like C"
    print(">>> \"String formatting %s\" % \"like C\"")
    stext = "Format emoticons %s" % "🏆🥇"
    print(">>> \"Format emoticons %s\" % \"🏆🥇\"")
    stext = unicode("Format emoticons %s") % u"🏆🥇"
    print(">>> \"Format emoticons unicode(u'%s')\" % \"🏆🥇\"")
    print("")
    utext = "Emoticons: 🏆🥇".decode("utf-8")
    print("\"Emoticons: 🏆🥇\".decode(\"utf-8\")", type(utext))
    utext = "Emoticons: 🏆🥇".decode("utf-8")
    print("\"Emoticons: 🏆🥇\".decode(\"utf-8\")", type(utext))
    utext = "Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87".decode("utf-8")
    print("\"Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87\".decode(\"utf-8\")",
          type(utext))
    print(utext)

def test_int():
    print("")
    k = 9223372036854775808L
    print("isinstance(%sL, (long, int)) -> %s" % (k, isinstance(k, (long, int))))


def test_raise():
    print("")
    print(">>> try:")
    try:
        print(">>>     fd = open(\"\", \"r\")")
        open("", "r")
    except IOError, e:
        print(">>> except IOError as '%s'" % e)


def test_io(fn):
    print("")
    with open(fn, "r") as fd:
        utext = fd.read().decode("utf-8")
    print(">>> with open(fn, \"r\") as fd:")
    print(type(utext))


def main(args):
    PYMODE = "2"
    print(args[0] + " running in python" + PYMODE + " pure mode")
    print >> sys.stderr, "Test to stderr"
    test_raise()
    test_string()
    test_int()
    test_io(args[0])
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
