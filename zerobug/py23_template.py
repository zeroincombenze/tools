# -*- coding: utf-8 -*-
"""
This file contains python 2-3 code example
"""
from __future__ import print_function, unicode_literals
# from future import standard_library
from past.builtins import basestring, long
from builtins import str as text
from io import open
import os
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
    stext = text(b"Format emoticons %s") % "🏆🥇"
    print(">>> \"Format emoticons text(b'%s')\" % \"🏆🥇\"")
    utext = b"Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87".decode("utf-8")
    print("b\"Emoticons: \xf0\x9f\x8f\x86\xf0\x9f\xa5\x87\".decode(\"utf-8\")",
          type(utext), utext)
    print(utext)


def test_int():
    print("")
    k = 9223372036854775808
    print("isinstance(%s, (long, int)) -> %s" % (k, isinstance(k, (long, int))))


def test_raise():
    print("")
    print(">>> try:")
    try:
        print(">>>     fd = open(\"\", \"r\")")
        open("", "r")
    except IOError as e:
        # Python3 use FileNotFoundError but catches IOError too
        print(">>> except IOError as '%s'" % e)


def test_io(fn):
    print("")
    with open(fn, "r", encoding="utf-8") as fd:
        utext = fd.read()
    print(">>> with open(fn, \"r\", encoding=\"utf-8\") as fd:")
    print(type(utext))


def main(args):
    if len(args) > 1:
        if args[1] == "-h":
            print(args[0] + " 2|3|future to run under full python2 or python3 code")
            print("  future run under future library (it is the default)")
            return 0
        elif sys.argv[1] == "2":
            return os.system(sys.executable + " " + args[0].replace("23", "2"))
        elif sys.argv[1] == "3":
            return os.system(sys.executable + " " + args[0].replace("23", "3"))
    PYMODE = "future"
    print(args[0] + " running in " + PYMODE + " mode")
    print("Test to stderr", file=sys.stderr)
    test_raise()
    test_string()
    test_int()
    test_io(args[0])
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
