#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
"""
    Unit Test for pytok package

"""
import sys
import os
import logging
from pytok import pytok


test_ctr = 0
max_tests = 42
gbl_test_num = -1
wlog = None
res = ""

TEST_FAILED = 1
TEST_SUCCESS = 0
APPLY_CONF = True
SRC_1 = """
'''
    Sample for pytok unit test
'''

import sys


class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0

    def do_something(self):
        return self.myvalue


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()


# Follow class is just to fill white paper!
class dummy:    # no useful class

    # Hidden function
    def do_nothing():   # nothing to do
        pass

    # Function without class call
    @staticmethod
    def do_public():
        return 0


class My_Child(Parent_Class):

    uresponse = 42

    @classmethod
    def universal_response(cls):
        return cls.uresponse

    def do_something(self):
        v = super(My_Child, self).do_something()
        if v == 0:
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                value += 1
                return value
        return _think_positive(value)


def main():
    # tool main
    sts = dummy.do_public()
    if sts == 0:
        A = My_Class()
        sts = A.do_something()
    if sts == 0:
        sts = Parent_Class().do_something()
    if sts == 0:
        sts = My_Child().do_something() - 42
    if sts == 0:
        M = My_Child()
        sts = 1 - M.do_think_different(1)
    if sts == 0:
        sts = 1 - M.do_think_different(0)
    if sts == 0:
        sts = M.do_think_different(-1)
    return sts


if __name__ == "__main__":
    sts = main()
    if sts:
        raise ValueError
    sys.exit(sts)
    """


def init_logger():
    global wlog
    file_log = nakedname(os.path.basename(__file__)) + ".log"
    wlog = logging.getLogger()
    wlog.setLevel(logging.DEBUG)
    fh = logging.FileHandler(file_log, 'w')
    ch = logging.StreamHandler()
    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    ch.setFormatter(logging.Formatter('%(message)s'))
    wlog.addHandler(ch)
    wlog.addHandler(fh)


def msg_new_test(test_num):
    global test_ctr, max_tests, gbl_test_num
    if test_ctr == 0:
        init_logger()
    test_ctr += 1
    if test_num != gbl_test_num:
        gbl_test_num = test_num
        msg_test(True, test_num)
    else:
        msg_test(False, test_num)


def msg_test(newline, test_num):
    # if test_ctr >= 39 and test_ctr <= 40:  # debug
    #     import pdb
    #     pdb.set_trace()
    txt = "Test {0:>2}){1:>3}/{2:3}".format(test_num,
                                            test_ctr,
                                            max_tests)
    if newline:
        wlog.info(txt)
    else:
        print "\x1b[A" + txt
        wlog.debug(txt)


def generic_test(o=None, c=None, d=None, t=None, m=None, h=None, i=None):
    """Call test with parameters
    o: output
    c: classes selection
    d: functions selection
    t: tokens selection
    m: module selection
    h: no header
    """
    global res, test_ctr
    src = pytok.new(text=SRC_1)
    prm = {}
    prm['no_num_line'] = True
    if test_ctr % 2:
        if c:
            prm['inclass'] = c
        if d:
            prm['infun'] = d
        if t:
            prm['tokens'] = t
        if m:
            prm['model'] = m
    else:
        if c:
            src.decl_classes_2_search(c)
        if d:
            src.decl_funs_2_search(d)
        if t:
            src.decl_tokens_2_search(t)
        if m:
            src.decl_model_2_search(m)
    if o:
        prm['output'] = lambda x: acquire(x)
    if h:
        prm['no_header'] = h
    if i:
        prm['no_inherit'] = i
    src.decl_options(prm)
    src.parse_src()
    if o:
        res = ""
        src.tostring()
    else:
        res = src.tostring()
    return res


def acquire(txt):
    global res
    res += txt + '\n'


def test_00(test_num):
    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = [1, 2, 3, [4, 5], [6, 8], [10, 12], [20, 25], [3, 4], [13, 19]]
    tgtlines = [[1, 19], [20, 25]]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = [[1, 3], [4, 5], 6, 7, 9, [11, 12], 20, [2, 4], [10, 19]]
    tgtlines = [[1, 19], 20]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = [[1, 3], [10, 15], [20, 30], [2, 12], 19, 17, [15, 22]]
    tgtlines = [[1, 30]]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = [[27, 42], [13, 26]]
    tgtlines = [[13, 26], [27, 42]]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = [[13, 26], [32, 42], [43, 50]]
    tgtlines = [[13, 26], [32, 50]]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    msg_new_test(test_num)
    prm = {}
    prm['output'] = lambda x: acquire(x)
    src = pytok.new(text=SRC_1)
    srclines = 71, [76, 80], [84, 85], [71, 82]
    tgtlines = [[71, 82], [84, 85]]
    for grplines in srclines:
        if isinstance(grplines, list):
            start = grplines[0]
            stop = grplines[1]
            src.add_line_range(start, stop)
        else:
            src.add_line_range(grplines)
    reslines = src.get_range()
    if reslines != tgtlines:
        return TEST_FAILED

    return TEST_SUCCESS


def test_01(test_num):
    global SRC_1, res

    msg_new_test(test_num)
    res = generic_test(o=True)
    if res.strip() != SRC_1.strip():
        return TEST_FAILED

    # Repeated test to check parameters supplied
    msg_new_test(test_num)
    res = generic_test(o=True)
    if res.strip() != SRC_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_02(test_num):
    global SRC_1

    msg_new_test(test_num)
    res = generic_test()
    if res.strip() != SRC_1.strip():
        return TEST_FAILED

    TGT_2_1 = """


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class')
    if res.strip() != TGT_2_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub')
    if res.strip() != TGT_2_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class()')
    if res.strip() != TGT_2_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_03(test_num):
    global SRC_1

    TGT_3_1 = """


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Class,Not_Exists_Class')
    if res.strip() != TGT_3_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Class(),Not_Exists_Class')
    if res.strip() != TGT_3_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class,Not_Exists_Class')
    if res.strip() != TGT_3_1.strip():
        return TEST_FAILED
    return TEST_SUCCESS


def test_04(test_num):
    global SRC_1

    msg_new_test(test_num)
    res = generic_test()
    if res.strip() != SRC_1.strip():
        return TEST_FAILED

    TGT_4_1 = """



class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0

    def do_something(self):
        return self.myvalue


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()


class My_Child(Parent_Class):

    uresponse = 42

    @classmethod
    def universal_response(cls):
        return cls.uresponse

    def do_something(self):
        v = super(My_Child, self).do_something()
        if v == 0:
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                value += 1
                return value
        return _think_positive(value)
    """

    msg_new_test(test_num)
    res = generic_test(c='My_')
    if res.strip() != TGT_4_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_05(test_num):
    global SRC_1

    msg_new_test(test_num)
    res = generic_test()
    if res.strip() != SRC_1.strip():
        return TEST_FAILED

    TGT_5_1 = """

class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class')
    if res.strip() != TGT_5_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub')
    if res.strip() != TGT_5_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class()')
    if res.strip() != TGT_5_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_06(test_num):
    global SRC_1

    TGT_6_1 = """
    """

    msg_new_test(test_num)
    res = generic_test(c='My(),Not_Exists_Class()')
    if res.strip() != TGT_6_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='Not_Exists_Class', d='my()')
    if res.strip() != TGT_6_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_07(test_num):
    global SRC_1

    TGT_7_1 = """
class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0

    def do_something(self):
        return self.myvalue


class My_Child(Parent_Class):

    uresponse = 42

    @classmethod
    def universal_response(cls):
        return cls.uresponse

    def do_something(self):
        v = super(My_Child, self).do_something()
        if v == 0:
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                value += 1
                return value
        return _think_positive(value)
    """

    msg_new_test(test_num)
    res = generic_test(c='Parent_Class')
    if res.strip() != TGT_7_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='Parent_Class()')
    if res.strip() != TGT_7_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='Parent')
    if res.strip() != TGT_7_1.strip():
        return TEST_FAILED

    TGT_7_2 = """
class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0

    def do_something(self):
        return self.myvalue


class My_Child(Parent_Class):

    def do_something(self):
        v = super(My_Child, self).do_something()
        if v == 0:
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                value += 1
                return value
        return _think_positive(value)
    """

    msg_new_test(test_num)
    res = generic_test(c='Parent', d='__,do')
    if res.strip() != TGT_7_2.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_08(test_num):
    global SRC_1

    TGT_8_1 = """
class My_Class():
    def __init__(self):
        pass


class My_Sub_Class(My_Class):

    def __init__(self):
        pass
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init__')
    if res.strip() != TGT_8_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init')
    if res.strip() != TGT_8_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init__()')
    if res.strip() != TGT_8_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_09(test_num):
    global SRC_1

    TGT_09_1 = """
class Parent_Class(object):

    def do_something(self):
        return self.myvalue


# Follow class is just to fill white paper!
class dummy:    # no useful class

    # Function without class call
    @staticmethod
    def do_public():
        return 0


class My_Child(Parent_Class):

    def do_something(self):
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                return value
        return _think_positive(value)
    """

    msg_new_test(test_num)
    res = generic_test(c='Parent,dummy', d='__init__,do', t='return')
    if res.strip() != TGT_09_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='Parent,dummy', d='__init__,do', t='ret')
    if res.strip() != TGT_09_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_10(test_num):
    global SRC_1

    TGT_10_1 = """


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()
    """

    msg_new_test(test_num)
    res = generic_test(m='res.partner')
    if res.strip() != TGT_10_1.strip():
        return TEST_FAILED

    # Repeated test to check parameters supplied
    msg_new_test(test_num)
    res = generic_test(m='res.partner')
    if res.strip() != TGT_10_1.strip():
        return TEST_FAILED

    TGT_10_2 = """
class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0


class My_Class():
    def __init__(self):
        pass


class My_Sub_Class(My_Class):

    def __init__(self):
        pass
    """

    msg_new_test(test_num)
    res = generic_test(d='__init__()')
    if res.strip() != TGT_10_2.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_11(test_num):
    global SRC_1

    TGT_11_1 = """
class My_Sub_Class(My_Class):

    def __init__(self):
        pass
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init__', i=True)
    if res.strip() != TGT_11_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init', i=True)
    if res.strip() != TGT_11_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', d='__init__()', i=True)
    if res.strip() != TGT_11_1.strip():
        return TEST_FAILED

    TGT_11_2 = """
class My_Sub_Class(My_Class):

    def __init__(self):
    """

    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', t='__init__()', i=True)
    if res.strip() != TGT_11_2.strip():
        return TEST_FAILED

    # Repeated test to check parameters supplied
    msg_new_test(test_num)
    res = generic_test(c='My_Sub_Class', t='__init__()', i=True)
    if res.strip() != TGT_11_2.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def test_12(test_num):
    global SRC_1

    TGT_12_1 = """
        return self.myvalue
        return 0
            return self.universal_response()
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
                return value
        return _think_positive(value)
    """

    msg_new_test(test_num)
    res = generic_test(c='Parent,dummy', d='__init__,do', t='return', h=True)
    if res.strip() != TGT_12_1.strip():
        return TEST_FAILED

    msg_new_test(test_num)
    res = generic_test(c='Parent,dummy', d='__init__,do', t='ret', h=True)
    if res.strip() != TGT_12_1.strip():
        return TEST_FAILED

    return TEST_SUCCESS


def nakedname(fn):
    """Return nakedename (without extension)"""
    i = fn.rfind('.')
    if i >= 0:
        j = len(fn) - i
        if j <= 4:
            fn = fn[:i]
    return fn


def main():
    """Tool main."""
    required_version = os.environ.get('PYTOK_VERSION')
    pkg_version = pytok.version
    if required_version and pkg_version.find(required_version) < 0:
        print "Required version:", required_version
        print "Package version:", pkg_version
        return TEST_FAILED
    print "Pytok", pytok.version, "regression test"
    test_num = 0
    max_test_num = 13
    sts = 0
    for i in range(max_test_num):
        tname = "test_{0:02}".format(test_num)
        if tname in list(globals()):
            sts = globals()[tname](test_num)
            if sts:
                break
        test_num += 1
    return sts


if __name__ == "__main__":
    sts = main()
    if sts == 0:
        print "{0} pytok tests successfully ended".format(test_ctr)
    else:
        print "****** Test pytok failed ******"
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
