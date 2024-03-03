# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from past.builtins import basestring, long
from future.utils import PY2, PY3, with_metaclass
from datetime import datetime, date, timedelta
import calendar
from . import scripts


__title__ = 'python_plus'
__author__ = 'Antonio Maria Vigliotti'
__copyright__ = 'Copyright 2018-2024 SHS-AV srl'
__version__ = '2.0.12'

PYCODESET = 'utf-8'
if PY3:
    text_type = unicode = str
    bytestr_type = bytes
elif PY2:
    # unicode exist only for python2
    text_type = unicode
    bytestr_type = str


def isunicode(object):  # pylint: disable=redefined-builtin
    if PY2:
        return isinstance(object, unicode)
    return isinstance(object, str)


def isbytestr(object):  # pylint: disable=redefined-builtin
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
    elif isinstance(src, (list, tuple)):
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
    elif isinstance(src, (list, tuple)):
        for i, x in enumerate(src):
            src[i] = _u(x)
    return src


def str2bool(item, default=True):
    """Convert text to bool"""
    if isinstance(item, bool):
        return item
    elif isinstance(item, (int, long)):
        return item != 0
    elif isinstance(item, float):
        return item != 0.0
    elif not isinstance(item, basestring):
        return default
    elif item.lower() in ["true", "t", "1", "y", "yes", "on", "enabled"]:
        return True
    elif item.lower() in ["false", "f", "0", "n", "no", "off", "disabled"]:
        return False
    else:
        return default


def qsplit(*args, **kwargs):
    """quoted split
    Like python split but manage quoted strings
    Args:
        item (str): text to split
        sep (str|list|tuple): separators characters (default spaces)
        max (int): max splitting

        quotes (list|tuple): quote character (default ["\"", "'"])
        escape (bool): enable escape char "\"
        enquote (bool): add quoted characters in split fields
        strip (bool): strip results
    """
    src = args[0]
    if len(args) > 1 and args[1]:
        sep = args[1]
        if isinstance(sep, (tuple, list)):
            sep = unicodes(sep)
        elif isinstance(sep, basestring):
            sep = _u(sep)
    else:
        sep = [' ', '\t', '\n', '\r']
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
        elif (isinstance(sep, (tuple, list)) and ch in sep) or (
            isinstance(sep, basestring) and ch == sep
        ):
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


def compute_date(value, refdate=None):
    """Evaluate an encoded date string against reference date or today().
    This function applies for some standard python date[time] functions;
    it is useful for test environment.
    String format is like ISO, with 3 groups separated by '-' (dash).
    Every group may be an integer or a special notation:
    - starting with '<' meas subtract; i.e. '<2' means minus 2
    - ending with '>' meas add; i.e. '2>' means plus 2
    - '#' with '<' or '>' means 1; i.e. '<###' means minus 1
    - all '#' means same value of reference date
    A special notation '+N' and '-N', where N is an integer means add N days
    or subtract N day from reference date.
    Here, in following examples, are used python iso date convention:
    '+N': return date + N days to refdate (python timedelta)
    '-N': return date - N days from refdate (python timedelta)
    '%Y-%m-%d': strftime of issued value
    '%Y-%m-%dT%H:%M:%S': same datetime
    '%Y-%m-%d %H:%M:%S': same datetime
    '####-%m-%d': year from refdate (or today), month '%m', day '%d'
    '####-##-%d': year and month from refdate (or today), day '%d'
    '2022-##-##': year 2022, month and day from refdate (or today)
    '<###-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
    '<001-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
    '<###-#>-%d': year -1  from refdate, month +1 from refdate, day '%d'
    '<005-2>-##': year -5, month +2 and day from refdate
    Notes:
        Returned date is always a ISO string of date or datetime
        Returned date is always a valid date; i.e. '####-#>-31',
        with ref month January result '####-02-31' becomes '####-03-03'
        To force last day of month, set '99': i.e. '####-<#-99' becomes the
        last day of previous month of refdate
    """

    def cur_prior_month(items):
        while items[1] < 1:
            items[0] -= 1
            items[1] += 12
        return items

    def cur_next_month(items):
        while items[1] > 12:
            items[0] += 1
            items[1] -= 12
        return items

    if not value or not isinstance(value, (basestring, int, long)):
        return value
    refdate = refdate or date.today()
    if isinstance(refdate, basestring):
        refdate = datetime.strptime(refdate, "%Y-%m-%d")
    sep = tm = None
    if isinstance(value, basestring):
        if 'T' in value:
            sep = 'T'
        elif ' ' in value:
            sep = ' '
        if sep:
            value, tm = value.split(sep)
    if isinstance(value, (int, long)):
        value = (refdate + timedelta(value)).strftime('%Y-%m-%d')
    elif ((value.startswith('+') or value.startswith('-')) and value[1:].isdigit()):
        value = (refdate + timedelta(int(value))).strftime('%Y-%m-%d')
    else:
        items = value.split('-')
        refs = [refdate.year, refdate.month, refdate.day]
        for i, item in enumerate(items):
            if item.startswith('<'):
                v = int(item[1:]) if item[1:].isdigit() else 1
                items[i] = refs[i] - v
            elif item.endswith('>'):
                v = int(item[:-1]) if item[0].isdigit() else 1
                items[i] = refs[i] + v
            elif item in ('#', '##', '####', '00', '0000'):
                items[i] = refs[i]
            else:
                items[i] = int(items[i]) or refs[i]
        while items[2] < 1:
            items[1] -= 1
            items = cur_prior_month(items)
            dd = calendar.monthrange(items[0], items[1])[1]
            items[2] += dd
        items = cur_prior_month(items)
        items = cur_next_month(items)
        if items[2] == 99:
            items[2] = calendar.monthrange(items[0], items[1])[1]
        while items[2] > calendar.monthrange(items[0], items[1])[1]:
            items[2] -= calendar.monthrange(items[0], items[1])[1]
            items[1] += 1
            items = cur_next_month(items)
        value = '%04d-%02d-%02d' % (items[0], items[1], items[2])
    if tm:
        value = '%s%s%s' % (value, sep, tm)
    return value


class Base__(type):
    def __instancecheck__(cls, instance):
        if cls == __:
            return isinstance(instance, text_type)
        else:
            return issubclass(instance.__class__, cls)


class __(object, with_metaclass(Base__, text_type)):
    def qsplit(
        self, sep=None, maxsplit=-1, quotes=None, escape=None, enquote=None, strip=None
    ):
        return qsplit(
            self,
            sep=sep,
            maxsplit=maxsplit,
            quotes=quotes,
            escape=escape,
            enquote=enquote,
            strip=strip,
        )



