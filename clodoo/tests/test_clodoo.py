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
    Massive operations on Zeroincombenze(R) / Odoo databases

"""
import os
import sys
from os0 import os0
from datetime import date
from ..clodoo import _import_file_model
from ..clodoo import _get_model_code
from ..clodoo import _get_model_name
from ..clodoo import _import_file_dbtype
from ..clodoo import _import_file_get_hdr
from ..clodoo import _eval_value
from ..clodoo import _get_query_id
from ..clodoo import _get_model_bone
from ..clodoo import create_act_list
from ..clodoo import isaction
from ..clodoo import check_4_actions
from ..clodoo import do_action


test_ctr = 0
max_tests = 232
gbl_test_num = 0

MY_ACT = 'my_actions'
CID = 9
DEF_CID = 1
REF_ID = 1
ID_0 = 11
ID_1 = 1
ID_I = 4
MARK = u"Zeroincombenze®"
CTRY_IT = 110


def nakedname(fn):
    """Return nakedename (without extension)"""
    i = fn.rfind('.')
    if i >= 0:
        j = len(fn) - i
        if j <= 4:
            fn = fn[:i]
    return fn


class Oerp():

    """oerplib simulator for test execution
    It simulate:
    - res.zero: model w/o company (key is name, 1 record)
    - res.one: mode with company (key is name, 1 record)
    - res.two: model w/o company (key is name, many records)
    - res.three: mode with company (key is name, may records)
    - res.four: model w/o company (key is other)
    - res.five: model with company (key is other)
    """

    def __init__(self):
        self.id = 0
        self.model = ""
        self.value = ""
        # self.db = type('', (), {})
        self.db = {}
        for model in ('res.zero',
                      'res.one',
                      'res.two',
                      'res.three',
                      'res.four',
                      'res.five',
                      'ir.model.data'):
            # setattr(self.db, name, {})
            self.db['model'] = {}
            if model == 'res.zero':
                self.db[model] = {}
                self.db[model]['name'] = 'myname'
                self.db[model]['ref'] = REF_ID
                self.db[model]['id'] = ID_0
                self.db[model]['description'] = MARK
            elif model == 'res.one':
                self.db[model] = {}
                self.db[model]['name'] = 'myname'
                self.db[model]['company_id'] = CID
                self.db[model]['ref0'] = ID_0
                self.db[model]['id'] = ID_1
            elif model == 'res.two':
                self.db[model] = {}
                self.db[model]['name'] = 'myname'
                self.db[model]['id'] = REF_ID
                self.db[model]['country_id'] = CTRY_IT
            elif model == 'ir.model.data':
                self.db[model] = {}
                self.db[model]['module'] = 'base'
                self.db[model]['name'] = 'main_company'
                self.db[model]['id'] = ID_I
                self.db[model]['res_id'] = ID_0

    def search(self, model, where):
        """Search simulation
        First time simulate null result
        """
        if model == "":
            print "*** No model supplied!!!"
            return None
        if model not in self.db:
            print "*** Invalid " + model + " model!!!"
            return None
        ids = []
        condok = 0
        r = 0
        for i, cond in enumerate(where):
            n = cond[0]
            if n == "|":
                condok += 1
                r = 2
                continue
            elif n not in self.db[model]:
                print "*** Invalid " + model + "." + n + " field!!!"
                return None
            o = cond[1]
            v = cond[2]
            if isinstance(self.db[model][n], (int, long, float)):
                if o == '=' and int(v) == self.db[model][n]:
                    condok += 1
                elif r > 0:
                    r -= 1
                    condok += 1
            elif isinstance(self.db[model][n], basestring):
                if o == '=' and v == self.db[model][n]:
                    condok += 1
                elif o == 'ilike' and self.db[model][n].find(v) >= 0:
                    condok += 1
                elif r > 0:
                    r -= 1
                    condok += 1
            elif r > 0:
                r -= 1
                condok += 1
        if condok == len(where):
            if where == []:
                ids = [999, self.db[model]['id']]
            else:
                ids = [self.db[model]['id']]
            return ids
        return[]

    def browse(self, model, ids):
        if model == 'ir.model.data':
            if ids == ID_I:
                self.res_id = self.db[model]['res_id']
                self.module = self.db[model]['module']
                self.name = self.db[model]['name']
                return self
        elif model == 'res.zero':
            if ids == ID_0:
                self.name = self.db[model]['name']
                self.ref = self.db[model]['ref']
                self.description = self.db[model]['description']
                return self
        self.res_id = 0
        return self

Oerp()


class Csv():

    """csv simulator for test execution"""

    def _init(self):
        self.fieldnames = ""

Csv()


class Conf():

    """confparser simulator for test execution"""

    def _init(self):
        pass

    def has_section(self, section):
        if section == MY_ACT:
            return True
        else:
            return False

    def has_option(self, section, name):
        if section == MY_ACT and name == 'actions':
            return True
        else:
            return False

    def get(self, section, name):
        if section == MY_ACT and name == 'actions':
            return 'unit_test'
        else:
            return False
Conf()


def msg_new_test(test_num):
    global test_ctr, max_tests, gbl_test_num
    test_ctr += 1
    if test_num != gbl_test_num:
        gbl_test_num = test_num
        msg_test(True, test_num)
    else:
        msg_test(False, test_num)


def msg_test(newline, test_num):
    global test_ctr, max_tests
    # if test_ctr >= 116 and test_ctr <= 118:  # debug
    #     import pdb
    #     pdb.set_trace()

    if newline:
        print "Test {0:>2}){1:>3}/{2:3}".format(test_num,
                                                test_ctr,
                                                max_tests)
    else:
        print "\x1b[ATest {0:>2}){1:>3}/{2:3}".format(test_num,
                                                      test_ctr,
                                                      max_tests)


def init_test(model):
    oerp = Oerp()
    o_bones = {}
    prm = {}
    if model not in ('res.zero', 'res.two', 'res.four'):
        prm['def_company_id'] = DEF_CID
        prm['company_id'] = CID
    else:
        o_bones['hide_cid'] = True
    prm['def_partner_id'] = 2
    prm['def_user_id'] = 3
    prm['def_country_id'] = CTRY_IT
    conf_obj = Conf()
    prm['_conf_obj'] = conf_obj
    prm['_opt_obj'] = None
    prm['actions_db'] = ''
    prm['actions_mc'] = ''
    prm['test_unit_mode'] = True
    o_bones['db_type'] = "db_type"
    o_bones['name'] = "name"
    o_bones['code'] = "name"
    o_bones['model'] = model
    csv_fn = ""
    row = {}
    row['undef_name'] = ''
    csv_obj = Csv()
    o_bones = _import_file_get_hdr(oerp,
                                   prm,
                                   o_bones,
                                   csv_obj,
                                   csv_fn,
                                   row)
    return oerp, prm, o_bones, csv_obj, csv_fn, row


def test_01(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.zero")
    model, hide_cid = _get_model_bone(None, o_bones)
    if model != "res.zero":
        return 1
    if not hide_cid:
        return 1

    msg_new_test(test_num)
    prm['model'] = 'res.one'
    model, hide_cid = _get_model_bone(prm, o_bones)
    if model != "res.one":
        return 1
    if hide_cid:
        return 1

    for csv_fn in ('res_zero.csv', 'res-zero.csv', 'res.zero.csv'):
        msg_new_test(test_num)
        o_bones = {}
        model, hide_cid = _import_file_model(o_bones, csv_fn)
        if model != "res.zero":
            return 1
        if hide_cid:
            return 1

        msg_new_test(test_num)
        o_bones['model'] = "res.one"
        model, hide_cid = _import_file_model(o_bones, csv_fn)
        if model != "res.one":
            return 1
        if 'hide_cid' in o_bones:
            return 1

    return 0


def test_02(test_num):
    o_bones = {}
    for n in ('id', 'name', 'code', 'other'):
        msg_new_test(test_num)
        fields = ['a', 'b', n, 'z']
        name = _get_model_name(fields, o_bones)
        if n == 'other' or n == 'id':
            if name != 'name':
                return 1
        elif n != name:
            return 1

    fields = ['id', 'name', 'code', 'my_name', u'other']
    for n in ('id', 'name', 'code', 'my_name', u'other'):
        msg_new_test(test_num)
        o_bones['model_name'] = n
        name = _get_model_name(fields, o_bones)
        if name != 'name':
            return 1

    o_bones = {}
    for n in ('id', 'name', 'code', 'my_name', u'other'):
        msg_new_test(test_num)
        o_bones['name'] = n
        name = _get_model_name(fields, o_bones)
        if name != 'name':
            return 1
    return 0


def test_03(test_num):
    o_bones = {}
    for n in ('id', 'name', 'code', 'other'):
        msg_new_test(test_num)
        fields = ['a', 'b', n, 'z']
        code = _get_model_code(fields, o_bones)
        if n == 'other':
            if code != 'name':
                return 1
        elif n != code:
            return 1

    fields = ['id', 'name', 'code', 'my_name', u'other']
    for n in ('id', 'name', 'code', 'my_name', u'other'):
        msg_new_test(test_num)
        o_bones['model_code'] = n
        code = _get_model_code(fields, o_bones)
        if n != code:
            return 1

    o_bones = {}
    for n in ('id', 'name', 'code', 'my_name', u'other'):
        msg_new_test(test_num)
        o_bones['code'] = n
        code = _get_model_code(fields, o_bones)
        if n != code:
            return 1
    return 0


def test_04(test_num):
    o_bones = {}
    csv_fn = "res-zero.csv"
    for n in ('db_type', 'id', 'name', 'code', 'other'):
        msg_new_test(test_num)
        fields = ['a', 'b', n, 'z']
        name = _import_file_dbtype(o_bones, fields, csv_fn)
        if n != 'db_type':
            if name:
                return 1
        elif n != name:
            return 1

    fields = ['db_type', 'id', 'name', 'code', 'my_name', 'other']
    for n in ('id', 'name', 'code', 'my_name'):
        msg_new_test(test_num)
        o_bones['db_type'] = n
        name = _import_file_dbtype(o_bones, fields, csv_fn)
        if n != name:
            return 1
    return 0


def test_05(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.three")
    if o_bones['hide_cid']:
        return 1

    for name in ('db_type', 'id', 'name', 'code', 'my_name', u'other'):
        for value in (b'abc', u"def", True, False, 13715, 4.5,
                      date(1959, 6, 26)):
            msg_new_test(test_num)
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1

        for v in prm:
            msg_new_test(test_num)
            value = "=${" + v + "}"
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1
            elif isinstance(prm[v], (basestring, bool, int, long, float)):
                if res != prm[v]:
                    return 1

            msg_new_test(test_num)
            value = "=0-${" + v + "}-9"
            if name == "db_type" or name == "id":
                tres = None
            elif isinstance(prm[v], basestring):
                tres = "0-" + prm[v] + "-9"
            elif isinstance(prm[v], (bool, int, long, float)):
                tres = "0-" + str(prm[v]) + "-9"
            else:
                tres = prm[v]
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if res != tres:
                return 1

        for value in ("=${res.zero:myname}",
                      "=${res.one::myname}",
                      "=${res.two::myname}"):
            msg_new_test(test_num)
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1
            elif value[0:12] == "=${res.zero:":
                if res != ID_0:
                    return 1
                else:
                    return 0
            elif value[0:11] == "=${res.one:":
                if res != ID_1:
                    return 1
                else:
                    return 0
            elif value[0:11] == "=${res.two:":
                if res != REF_ID:
                    return 1
                else:
                    return 0
            else:
                return 1

            msg_new_test(test_num)
            cvalue = "=00-" + value[1:] + "-99"
            if name == "db_type" or name == "id":
                tres = None
            elif value[0:12] == "=${res.zero:":
                tres = "00-" + str(ID_0) + "-99"
            elif value[0:11] == "=${res.one:":
                tres = "00-" + str(ID_1) + "-99"
            elif value[0:11] == "=${res.two:":
                tres = "00-" + str(REF_ID) + "-99"
            else:
                tres = None
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              cvalue)
            if res != tres:
                return 1

        msg_new_test(test_num)
        value = "base.main_company"
        name = "company_id"
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if res != ID_0:
            return 1
    return 0


def test_06(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test(u"res.three")
    if o_bones['hide_cid']:
        return 1

    for name in (u'db_type', u'id', u'name', u'code', u'other'):
        for value in (b'abc', u"def", True, False, 13715, 4.5,
                      date(1959, 6, 26)):
            msg_new_test(test_num)
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1
            elif res != value:
                return 1

        for v in prm:
            msg_new_test(test_num)
            value = u"=${" + v + "}"
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1
            elif isinstance(prm[v], (basestring, bool, int, long, float)):
                if res != prm[v]:
                    return 1

        for value in (u"=${res.zero:myname}",
                      u"=${res.one::myname}",
                      u"=${res.two::myname}"):
            msg_new_test(test_num)
            res = _eval_value(oerp,
                              prm,
                              o_bones,
                              name,
                              value)
            if name == "db_type" or name == "id":
                if res is not None:
                    return 1
            elif value[0:12] == "=${res.zero:":
                if res != ID_0:
                    return 1
                else:
                    return 0
            elif value[0:11] == "=${res.one:":
                if res != ID_1:
                    return 1
                else:
                    return 0
            elif value[0:11] == "=${res.two:":
                if res != REF_ID:
                    return 1
                else:
                    return 0
            else:
                return 1

        msg_new_test(test_num)
        value = u"base.main_company"
        name = u"company_id"
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if res != ID_0:
            return 1
    return 0


def test_07(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.zero")
    if not o_bones['hide_cid']:
        return 1
    row['id'] = ''
    row['name'] = 'myname'
    row['other'] = "=${res.one:myname}"
    res = _get_query_id(oerp,
                        prm,
                        o_bones,
                        row)
    if res != [ID_0]:
        return 1

    msg_new_test(test_num)
    o_bones['code'] = "ref"
    row['ref'] = "=${res.two:~myname}"
    res = _get_query_id(oerp,
                        prm,
                        o_bones,
                        row)
    if res != [ID_0]:
        return 1

    msg_new_test(test_num)
    row['id'] = 'base.main_company'
    row['name'] = 'my_name'
    row['other'] = 'hello world'
    res = _get_query_id(oerp,
                        prm,
                        o_bones,
                        row)
    if res != [ID_0]:
        return 1

    for model in ('res.zero',
                  'res.two'):
        msg_new_test(test_num)
        oerp, prm, o_bones, csv_obj, csv_fn, row = init_test(model)
        o_bones['repl_by_id'] = True
        row['id'] = ''
        res = _get_query_id(oerp,
                            prm,
                            o_bones,
                            row)
        if len(res) <= 1:
            return 1
        if res[0] != 999:
            return 1

        for i in range(2):
            # repeat 2 time to check side effects
            msg_new_test(test_num)
            row['id'] = ''
            row['name'] = 'not_exists'
            res = _get_query_id(oerp,
                                prm,
                                o_bones,
                                row)
            if res != []:
                return 1

        for i in range(2):
            # repeat 2 time to check side effects
            msg_new_test(test_num)
            if model == 'res.zero':
                row['id'] = ID_0
            elif model == 'res.two':
                row['id'] = REF_ID
            else:
                row['id'] = ''
            row['name'] = 'not_exists'
            res = _get_query_id(oerp,
                                prm,
                                o_bones,
                                row)
            if len(res) != 1 or res[0] != row['id']:
                return 1
    return 0


def test_08(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.one")
    row['id'] = ''
    row['name'] = 'myname'
    row['other'] = "=${res.zero:myname}"
    res = _get_query_id(oerp,
                        prm,
                        o_bones,
                        row)
    if res != [ID_1]:
        return 1

    for x in (('name', 'my_name'), ('other', '=${res.zero:myname}')):
        msg_new_test(test_num)
        name = x[0]
        value = x[1]
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if name == "name" and res != "my_name":
            return 1
        if name == "other" and int(res) != ID_0:
            return 1

        msg_new_test(test_num)
        name = "ref0"
        value = "=${res.zero(name,ref):myname," + str(REF_ID) + "}"
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if int(res) != ID_0:
            return 1

        msg_new_test(test_num)
        name = "ref0"
        value = "=${res.zero(name,ref)[description]:myname,"\
            + str(REF_ID) + "}"
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if res != MARK:
            return 1

        msg_new_test(test_num)
        name = "ref0"
        value = "=${company_id+1}"
        res = _eval_value(oerp,
                          prm,
                          o_bones,
                          name,
                          value)
        if res != (CID + 1):
            return 1

    msg_new_test(test_num)
    name = "name"
    value = "=${res.two(country_id,name):"\
        + ",myname}"
    res = _eval_value(oerp,
                      prm,
                      o_bones,
                      name,
                      value)
    if res != REF_ID:
        return 1

    msg_new_test(test_num)
    name = "name"
    value = "=${res.two(country_id,name):"\
        + ",not_exists}"
    res = _eval_value(oerp,
                      prm,
                      o_bones,
                      name,
                      value)
    if res:
        return 1

    msg_new_test(test_num)
    name = "name"
    value = "=${res.one(company_id,ref0)::"\
        + "${company_id},${res.zero:myname}}"
    res = _eval_value(oerp,
                      prm,
                      o_bones,
                      name,
                      value)
    if res != ID_1:
        return 1

    return 0


def test_09(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.zero")
    prm = create_act_list(prm)
    lx = prm['_lx_act']
    if isaction(oerp, prm, lx[0]):
        prm['actions_db'] = lx[0]
        prm['actions_mc'] = lx[1]
    else:
        return 1
    if not check_4_actions(prm):
        return 1

    msg_new_test(test_num)
    prm['actions_mc'] = 'not_existent_action'
    if check_4_actions(prm):
        return 1
    return 0


def test_10(test_num):
    msg_new_test(test_num)
    oerp, prm, o_bones, csv_obj, csv_fn, row = init_test("res.zero")
    prm = create_act_list(prm)
    lx = prm['_lx_act']
    if isaction(oerp, prm, lx[0]):
        prm['actions_db'] = lx[0]
        prm['actions_mc'] = lx[1]
    else:
        return 1
    if not check_4_actions(prm):
        return 1

    msg_new_test(test_num)
    lx.append(MY_ACT)
    prm['actions_db'] = 'unit_test'
    if not check_4_actions(prm):
        return 1
    sts = do_action(oerp, prm, 'unit_test')
    if sts == 0:
        sts = do_action(oerp, prm, MY_ACT)
    return sts


def main():
    """Tool main."""
    # Need debug mode to avoid security fault in Linux
    os0.set_debug_mode(True)
    title = "clodoo regression tests. Version: 0.3.1"
    if 'DEV_ENVIRONMENT' in os.environ:
        LOCAL_ECHO = False
    else:
        LOCAL_ECHO = True
    tlog_fn = "./" + nakedname(os.path.basename(__file__)) + ".log"
    os0.set_tlog_file(tlog_fn, new=True, echo=LOCAL_ECHO)
    os0.wlog(title)
#
    test_num = 0
    max_test_num = 10
    sts = 0
    for i in range(max_test_num):
        test_num += 1
        tname = "test_{0:02}".format(test_num)
        if tname in list(globals()):
            sts = globals()[tname](test_num)
            if sts:
                break
    if sts == 0:
        os0.wlog("Test successfully ended. See {0} file" % os0.tlog_fn)
    else:
        os0.wlog("***** Test cloudoo failed ***** See {0} file" % os0.tlog_fn)
    return sts


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
