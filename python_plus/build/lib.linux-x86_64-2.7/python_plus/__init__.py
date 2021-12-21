from __future__ import print_function, unicode_literals
from past.builtins import basestring
from future.utils import PY2, PY3, with_metaclass
# import sys


__title__ = 'python_plus'
__author__ = 'Antonio Maria Vigliotti'
__license__ = 'L-GPL'
__copyright__ = 'Copyright 2018-2020 SHS-AV srl'
__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 3
__ver_sub__ = '6'
__version__ = '1.0.5'

PYCODESET = 'utf-8'
# PY2 = sys.version_info[0] == 2
# PY3 = sys.version_info[0] == 3
if PY3:
    text_type = str
    bytestr_type = bytes
elif PY2:
    text_type = unicode
    bytestr_type = str


def isunicode(object):
    if PY2:
        return isinstance(object, unicode)
    return isinstance(object, str)


def isbytestr(object):
    if PY2:
        return isinstance(object, str)
    return isinstance(object, bytes)


def _b(s):
    if isinstance(s, text_type):
        return s.encode(PYCODESET)
    return s


def _u(s):
    if isinstance(s, bytestr_type):
        if PY3:
            return s.decode(PYCODESET)
        return unicode(s, PYCODESET)
    return s


def _c(s):
    if PY2:
        return _b(s)
    return _u(s)


def bstrings(src):
    if isinstance(src, dict):
        src2 = src.copy()
        for x in src2.keys():
            if isinstance(x, text_type):
                del src[x]
            src[_b(x)] = _b(src2[x])
    elif isinstance(src, list):
        for i, x in enumerate(src):
            src[i] = _b(x)
    return src


def unicodes(src):
    if isinstance(src, dict):
        src2 = src.copy()
        for x in src2.keys():
            if isinstance(x, bytestr_type):
                del src[x]
            src[_u(x)] = _u(src2[x])
    elif isinstance(src, list):
        for i,x in enumerate(src):
            src[i] = _u(x)
    return src


def qsplit(*args, **kwargs):
    src = args[0]
    if len(args) > 1 and args[1]:
        sep = args[1]
        if isinstance(sep, (tuple, list)):
            sep = unicodes(sep)
        elif isinstance(sep, basestring):
            sep = _u(sep)
    else:
        sep=[' ', '\t', '\n', '\r']
    if len(args) > 2 and args[2]:
        maxsplit = args[2]
    else:
        maxsplit = -1
    quotes = kwargs.get('quotes', ["'", '"'])
    escape = kwargs.get('escape', False)
    enquote = kwargs.get('enquote', False)
    strip = kwargs.get('strip', False)
    source = _u(src)
    sts = False
    result = []
    item = ''
    esc_sts = False
    ctr = 0
    for ch in source:
        if maxsplit >= 0 and ctr >= maxsplit:
            item += ch
        elif esc_sts:
            esc_sts = False
            item += ch
        elif ch == escape:
            esc_sts = True
        elif ch == sts:
            sts = False
            if enquote:
                item += ch
        elif sts:
            item += ch
        elif ch in quotes:
            sts = ch
            if enquote:
                item += ch
        elif ((isinstance(sep, (tuple, list)) and ch in sep) or
              (isinstance(sep, basestring) and ch == sep)):
            if strip:
                result.append(item.strip())
            else:
                result.append(item)
            item = ''
            ctr += 1
        else:
            item += ch
    if strip:
        result.append(item.strip())
    else:
        result.append(item)
    if isinstance(src, bytestr_type):
        return bstrings(result)
    return result

# if PY3:
#     def qsplit(src, sep=None, maxsplit=-1,
#                 quotes=None, escape=None, enquote=None, strip=None):
#         return __qsplit__(src, sep=sep, maxsplit=maxsplit, quotes=quotes,
#                           escape=escape, enquote=enquote, strip=strip)
# if PY2:
#     def qsplit(*args, **kwargs):
#         return __qsplit__(*args, **kwargs)


class Base__(type):
    def __instancecheck__(cls, instance):
        if cls == __:
            return isinstance(instance, text_type)
        else:
            return issubclass(instance.__class__, cls)

class __(object, with_metaclass(Base__, text_type)):

    def qsplit(self, sep=None, maxsplit=-1,
               quotes=None, escape=None, enquote=None, strip=None):
        return qsplit(src, sep=sep, maxsplit=maxsplit, quotes=quotes,
                      escape=escape, enquote=enquote, strip=strip)
