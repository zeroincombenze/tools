# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Clodoo Regression Test Suite
"""

# import pdb
# import os.path
import sys
from datetime import date

from clodoo.clodoo import (check_4_actions, create_act_list, do_single_action,
                           isaction)
from clodoo.clodoocore import (_get_model_bone, _get_model_code,
                               _get_model_name, _import_file_dbtype,
                               _import_file_model, _model_has_company,
                               eval_value, get_query_id, import_file_get_hdr)
from zerobug import Z0test
__version__ = "0.3.6.20"


MODULE_ID = 'clodoo'
TEST_FAILED = 1
TEST_SUCCESS = 0
MY_ACT = 'my_actions'
CID = 9
DEF_CID = 1
REF_ID = 1
ID_0 = 11
ID_1 = 1
ID_I = 4
ID_C_0 = 13
MARK = u"Zeroincombenze®"
CTRY_IT = 110


def version():
    return __version__


class Oerp():
    """oerplib simulator for test execution
    It simulates:
    - res.zero: model w/o company (key is name, 1 record)
    - res.one: model with company (key is name, 1 record)
    - res.two: model w/o company (key is name, many records)
    - res.three: model with company (key is name, may records)
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
                      'ir.model.data',
                      'ir.model.fields'):
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
            elif model == 'res.three':
                self.db[model] = {}
                self.db[model]['name'] = 'name àèìòù'
                self.db[model]['company_id'] = CID
                self.db[model]['ref0'] = ID_0
                self.db[model]['id'] = ID_1
            elif model == 'ir.model.data':
                self.db[model] = {}
                self.db[model]['module'] = 'base'
                self.db[model]['name'] = 'main_company'
                self.db[model]['id'] = ID_I
                self.db[model]['res_id'] = ID_0
            elif model == 'ir.model.fields':
                self.db[model] = {}
                self.db[model]['model'] = 'res.one'
                self.db[model]['name'] = 'company_id'
                self.db[model]['id'] = ID_C_0

    def search(self, model, where, order=None, context=None):
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

    def browse(self, model, ids, context=None):
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
        elif model == 'res.one':
            if ids == ID_1:
                self.name = self.db[model]['name']
                self.ref0 = self.db[model]['ref0']
                self.company_id = self.db[model]['company_id']
                return self
        elif model == 'res.two':
            if ids == REF_ID:
                self.name = self.db[model]['name']
                self.country_id = self.db[model]['country_id']
                return self
        elif model == 'res.three':
            if ids == ID_1:
                self.name = self.db[model]['name']
                self.ref0 = self.db[model]['ref0']
                self.company_id = self.db[model]['company_id']
                return self
        else:
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


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def init_test(self, model):
        oerp = Oerp()
        o_model = {}
        ctx = {}
        ctx['odoo_session'] = oerp
        ctx['svc_protocol'] = 'xmlrpc'
        if model not in ('res.zero', 'res.two', 'res.four'):
            ctx['def_company_id'] = DEF_CID
            ctx['company_id'] = CID
        else:
            o_model['hide_cid'] = True
        ctx['def_partner_id'] = 2
        ctx['def_user_id'] = 3
        ctx['def_country_id'] = CTRY_IT
        ctx['panda'] = 'P'
        ctx['P' + str(ctx['def_partner_id'])] = 'PP'
        ctx['panda' + ctx['P' + str(ctx['def_partner_id'])]] = 'PPP'
        conf_obj = Conf()
        ctx['_conf_obj'] = conf_obj
        ctx['_opt_obj'] = None
        ctx['actions_db'] = ''
        ctx['actions_mc'] = ''
        ctx['test_unit_mode'] = True
        if model in ('res.zero', 'res.one'):
            o_model['db_type'] = "Z"
        elif model in ('res.two', ):
            o_model['db_type'] = "T"
        else:
            o_model['db_type'] = "C"
        o_model['name'] = "name"
        o_model['code'] = "name"
        o_model['model'] = model
        csv_fn = ""
        row = {}
        row['undef_name'] = ''
        csv_obj = Csv()
        o_model = import_file_get_hdr(oerp,
                                      ctx,
                                      o_model,
                                      csv_obj,
                                      csv_fn,
                                      row)
        return oerp, ctx, o_model, csv_obj, csv_fn, row

    def test_01(self, z0ctx):
        msg = '_get_model_bone'
        sts = TEST_SUCCESS
        for model_name in ('res.zero', 'res.one', 'res.two',
                           'res.four'):
            oerp, ctx, o_model, csv_obj, csv_fn, row = \
                self.init_test(model_name)
            model, hide_cid = _get_model_bone(ctx, o_model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx, msg, model_name, model)
            if sts == TEST_SUCCESS:
                if model in ('res.zero', 'res.two', 'res.four'):
                    sts = self.Z.test_result(z0ctx, msg, True, hide_cid)
                else:
                    sts = self.Z.test_result(z0ctx, msg, False, hide_cid)

        for model_name in ('res.zero', 'res.one', 'res.two'):
            oerp, ctx, o_model, csv_obj, csv_fn, row = \
                self.init_test(model_name)
            del o_model['hide_cid']
            model, hide_cid = _get_model_bone(ctx, o_model)
            sts = self.Z.test_result(z0ctx, msg, model_name, model)
            if sts == TEST_SUCCESS:
                if model in ('res.zero', 'res.two', 'res.four'):
                    sts = self.Z.test_result(z0ctx, msg, True, hide_cid)
                else:
                    sts = self.Z.test_result(z0ctx, msg, False, hide_cid)

        msg = '_import_file_model'
        for csv_fn in ('res_zero.csv', 'res-zero.csv', 'res.zero.csv'):
            o_model = {}
            if sts == TEST_SUCCESS:
                model, hide_cid = _import_file_model(ctx, o_model, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, "res.zero", model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx, msg, False, hide_cid)
            if sts == TEST_SUCCESS:
                o_model['model'] = "res.one"
                model, hide_cid = _import_file_model(ctx, o_model, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, "res.one", model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx,
                                         msg,
                                         False,
                                         'hide_cid' in o_model)
        return sts

    def test_02(self, z0ctx):
        o_model = {}
        msg = '_get_model_name'
        sts = TEST_SUCCESS
        for n in ('id', 'name', 'code', 'other'):
            if sts == TEST_SUCCESS:
                fields = ['a', 'b', n, 'z']
                name = _get_model_name(fields, o_model)
                if n == 'other' or n == 'id':
                    sts = self.Z.test_result(z0ctx, msg, 'name', name)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, name)

        fields = ['id', 'name', 'code', 'my_name', u'other']
        for n in ('id', 'name', 'code', 'my_name', u'other'):
            if sts == TEST_SUCCESS:
                o_model['model_name'] = n
                name = _get_model_name(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, name)

        o_model = {}
        for n in ('id', 'name', 'code', 'my_name', u'other'):
            if sts == TEST_SUCCESS:
                o_model['name'] = n
                name = _get_model_name(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, name)
        return sts

    def test_03(self, z0ctx):
        o_model = {}
        msg = '_get_model_code'
        sts = TEST_SUCCESS
        for n in ('id', 'name', 'code', 'other'):
            if sts == TEST_SUCCESS:
                fields = ['a', 'b', n, 'z']
                code = _get_model_code(fields, o_model)
                if n == 'other':
                    sts = self.Z.test_result(z0ctx, msg, 'name', code)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, code)

        fields = ['id', 'name', 'code', 'my_name', u'other']
        for n in ('id', 'name', 'code', 'my_name', u'other'):
            if sts == TEST_SUCCESS:
                o_model['model_code'] = n
                code = _get_model_code(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, code)

        o_model = {}
        for n in ('id', 'name', 'code', 'my_name', u'other'):
            if sts == TEST_SUCCESS:
                o_model['code'] = n
                code = _get_model_code(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, code)

        return sts

    def test_04(self, z0ctx):
        o_model = {}
        msg = '_import_file_dbtype'
        csv_fn = "res-zero.csv"
        sts = TEST_SUCCESS
        for n in ('db_type', 'id', 'name', 'code', 'other'):
            if sts == TEST_SUCCESS:
                fields = ['a', 'b', n, 'z']
                name = _import_file_dbtype(o_model, fields, csv_fn)
                if n != 'db_type':
                    sts = self.Z.test_result(z0ctx, msg, False, name)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, name)

        fields = ['db_type', 'id', 'name', 'code', 'my_name', 'other']
        for n in ('id', 'name', 'code', 'my_name'):
            if sts == TEST_SUCCESS:
                o_model['db_type'] = n
                name = _import_file_dbtype(o_model, fields, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, n, name)
        return sts

    def test_05(self, z0ctx):
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(None)
        msg = 'eval_value'
        sts = TEST_SUCCESS

        name = 'code'
        value = '=${panda}'
        res = eval_value(oerp,
                         ctx,
                         o_model,
                         name,
                         value)
        tres = 'P'
        sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = '=${panda}${def_partner_id}'
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            tres = 'P' + str(ctx['def_partner_id'])
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = '=${${panda}${def_partner_id}}'
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            tres = 'PP'
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = '=${panda${${panda}${def_partner_id}}}'
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            tres = 'PPP'

        for name in ('db_type', 'id', 'name', 'code', 'my_name', u'other'):
            msg = 'eval_value(' + name + ')'
            for value in (b'abc', u"def", True, False, 13715, 4.5,
                          date(1959, 6, 26)):
                if sts == TEST_SUCCESS:
                    res = eval_value(oerp,
                                     ctx,
                                     o_model,
                                     name,
                                     value)
                    sts = self.Z.test_result(z0ctx, msg, value, res)

            for v in ctx:
                if sts == TEST_SUCCESS:
                    value = "=${" + v + "}"
                    res = eval_value(oerp,
                                     ctx,
                                     o_model,
                                     name,
                                     value)
                    if isinstance(ctx[v], (basestring,
                                           bool,
                                           int,
                                           long,
                                           float)):
                        sts = self.Z.test_result(z0ctx, msg, ctx[v], res)

                if sts == TEST_SUCCESS:
                    value = "=0-${" + v + "}-9"
                    if isinstance(ctx[v], basestring):
                        tres = "0-" + ctx[v] + "-9"
                    elif isinstance(ctx[v], (bool, int, long, float)):
                        tres = "0-" + str(ctx[v]) + "-9"
                    else:
                        tres = "0--9"
                    res = eval_value(oerp,
                                     ctx,
                                     o_model,
                                     name,
                                     value)
                    sts = self.Z.test_result(z0ctx, msg, tres, res)

            for model_name in ("res.zero",
                               "res.one",
                               "res.two",
                               "res.three"):
                oerp, ctx, o_model, csv_obj, csv_fn, row = \
                    self.init_test(model_name)
                if model_name == "res.three":
                    value = model_name + "::name àèìòù"
                elif model_name in ('res.zero', 'res.two', 'res.four'):
                    value = model_name + ":myname"
                else:
                    value = model_name + "::myname"
                if sts == TEST_SUCCESS:
                    res = eval_value(oerp,
                                     ctx,
                                     o_model,
                                     name,
                                     value)
                    sts = self.Z.test_result(z0ctx, msg, value, res)
                if sts == TEST_SUCCESS:
                    if name == "id":
                        value = "=${" + model_name
                    elif name == "name" or name == "db_type":
                        value = "=${" + model_name + "[" + name + "]"
                    else:
                        value = "=${" + model_name + "[id]"
                    if model_name == "res.three":
                        value = value + "::name àèìòù}"
                    elif model_name in ('res.zero', 'res.two', 'res.four'):
                        value = value + ":myname}"
                    else:
                        value = value + "::myname}"
                    res = eval_value(oerp,
                                     ctx,
                                     o_model,
                                     name,
                                     value)
                    if name == "name" and model_name == 'res.three':
                        sts = self.Z.test_result(z0ctx,
                                                 msg,
                                                 "name àèìòù",
                                                 res)
                    elif name == "name":
                        sts = self.Z.test_result(z0ctx,
                                                 msg,
                                                 "myname",
                                                 res)
                    elif name == "db_type":
                        if model_name in ('res.zero', 'res.one'):
                            tres = "Z"
                        elif model_name in ('res.two', ):
                            tres = "T"
                        else:
                            tres = "C"
                        sts = self.Z.test_result(z0ctx, msg, tres, res)
                    else:
                        if value[0:11] == "=${res.zero":
                            sts = self.Z.test_result(z0ctx, msg, ID_0, res)
                        elif value[0:10] == "=${res.one":
                            sts = self.Z.test_result(z0ctx, msg, ID_1, res)
                        elif value[0:10] == "=${res.two":
                            sts = self.Z.test_result(z0ctx,
                                                     msg,
                                                     REF_ID,
                                                     res)
                        elif value[0:12] == "=${res.three":
                            sts = self.Z.test_result(z0ctx, msg, ID_1, res)
                        else:
                            sts = self.Z.test_result(z0ctx,
                                                     msg,
                                                     False,
                                                     True)
            if sts == TEST_SUCCESS:
                value = "base.main_company"
                name = "company_id"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                sts = self.Z.test_result(z0ctx, msg, ID_0, res)
        return sts

    def test_06(self, z0ctx):
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test("res.one")
        msg = 'eval_value'
        sts = TEST_SUCCESS
        for x in (('name', 'my_name'), ('other', '=${res.zero:myname}')):
            if sts == TEST_SUCCESS:
                name = x[0]
                value = x[1]
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                if name == "name":
                    tres = "my_name"
                elif name == "other":
                    tres = ID_0
                sts = self.Z.test_result(z0ctx, msg, tres, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${res.zero(name,ref):myname," + str(REF_ID) + "}"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                sts = self.Z.test_result(z0ctx, msg, ID_0, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${res.zero(name,ref)[description]:myname," + \
                    str(REF_ID) + "}"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                sts = self.Z.test_result(z0ctx, msg, MARK, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${company_id+1}"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                sts = self.Z.test_result(z0ctx, msg, CID + 1, res)

            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=[(6,0,${company_id})]"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                tres = [(6, 0, CID)]
                sts = self.Z.test_result(z0ctx, msg, tres, res)

            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=None"
                res = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 name,
                                 value)
                if res is not None:
                    tres = True
                else:
                    tres = res
                sts = self.Z.test_result(z0ctx, msg, tres, res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = "=${res.two(country_id,name):" + ",myname}"
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            sts = self.Z.test_result(z0ctx, msg, REF_ID, res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = "=${res.two(country_id,name):" + ",not_exists}"
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            sts = self.Z.test_result(z0ctx, msg, "", res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = "=${res.one(company_id,ref0)::" + \
                "${company_id},${res.zero:myname}}"
            res = eval_value(oerp,
                             ctx,
                             o_model,
                             name,
                             value)
            sts = self.Z.test_result(z0ctx, msg, ID_1, res)
        return sts

    def test_07(self, z0ctx):
        msg = '_model_has_company'
        sts = TEST_SUCCESS
        for model in ("res.zero",
                      "res.one",
                      "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_bones, csv_obj, csv_fn, row = \
                    self.init_test(model)
                res = _model_has_company(ctx,
                                         model)
                if model == "res.zero":
                    tres = False
                elif model == "res.one":
                    tres = True
                elif model == "res.two":
                    tres = False
                sts = self.Z.test_result(z0ctx, msg, tres, res)

    def test_08(self, z0ctx):
        msg = 'get_query_id'
        sts = TEST_SUCCESS
        for model in ("res.zero",
                      "res.one",
                      "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_bones, csv_obj, csv_fn, row = \
                    self.init_test(model)
                row['id'] = ''
                row['name'] = 'myname'
                row['other'] = "=${res.one:myname}"
                res = get_query_id(oerp,
                                   ctx,
                                   o_bones,
                                   row)
                if model == "res.zero":
                    tres = [ID_0]
                elif model == "res.one":
                    tres = [ID_1]
                elif model == "res.two":
                    tres = [REF_ID]
                sts = self.Z.test_result(z0ctx,
                                         msg,
                                         tres,
                                         res)

            if model == "res.zero":
                if sts == TEST_SUCCESS:
                    o_bones['code'] = "ref"
                    row['ref'] = "=${res.two:~myname}"
                    res = get_query_id(oerp,
                                       ctx,
                                       o_bones,
                                       row)
                    sts = self.Z.test_result(z0ctx, msg, [ID_0], res)
                if sts == TEST_SUCCESS:
                    row['id'] = 'base.main_company'
                    row['name'] = 'my_name'
                    row['other'] = 'hello world'
                    res = get_query_id(oerp,
                                       ctx,
                                       o_bones,
                                       row)
                    sts = self.Z.test_result(z0ctx, msg, [ID_0], res)

            if model in ('res.zero', 'res.two'):
                if sts == TEST_SUCCESS:
                    oerp, ctx, o_bones, csv_obj, csv_fn, row = \
                        self.init_test(model)
                    o_bones['repl_by_id'] = True
                    row['id'] = ''
                    res = get_query_id(oerp,
                                       ctx,
                                       o_bones,
                                       row)
                    if len(res) <= 1:
                        sts = self.Z.test_result(z0ctx, msg, False, True)
                    else:
                        sts = self.Z.test_result(z0ctx, msg, True, True)
                    if sts == TEST_SUCCESS:
                        sts = self.Z.test_result(z0ctx, msg, 999, res[0])

                for i in range(2):
                    if sts == TEST_SUCCESS:
                        # repeat 2 time to check side effects
                        if model == 'res.zero':
                            row['id'] = ID_0
                        elif model == 'res.two':
                            row['id'] = REF_ID
                        else:
                            row['id'] = ''
                        row['name'] = 'not_exists'
                        res = get_query_id(oerp,
                                           ctx,
                                           o_bones,
                                           row)
                        sts = self.Z.test_result(z0ctx, msg, 1, len(res))
                    if sts == TEST_SUCCESS:
                        sts = self.Z.test_result(z0ctx, msg, row['id'], res[0])

            for i in range(2):
                if sts == TEST_SUCCESS:
                    # repeat 2 time to check side effects
                    row['id'] = ''
                    row['name'] = 'not_exists'
                    res = get_query_id(oerp,
                                       ctx,
                                       o_bones,
                                       row)
                    sts = self.Z.test_result(z0ctx, msg, [], res)
        return sts

    def test_09(self, z0ctx):
        msg = 'get_query_id (id)'
        sts = TEST_SUCCESS
        for model in ("res.zero",
                      "res.one",
                      "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_model, csv_obj, csv_fn, row = \
                    self.init_test(model)
                if model == "res.zero":
                    tres = ID_0
                elif model == "res.one":
                    tres = ID_1
                elif model == "res.two":
                    tres = REF_ID
                row['id'] = tres
                row['name'] = 'myname'
                row['other'] = "=${res.zero:myname}"
                res = get_query_id(oerp,
                                   ctx,
                                   o_model,
                                   row)
                sts = self.Z.test_result(z0ctx, msg, [tres], res)
        return sts

    def test_10(self, z0ctx):
        msg = 'actions'
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test("res.zero")
        ctx = create_act_list(ctx)
        sts = TEST_SUCCESS
        lx = ctx['_lx_act']
        if isaction(oerp, ctx, lx[0]):
            ctx['actions_db'] = lx[0]
            ctx['actions_mc'] = lx[1]
        else:
            sts = self.Z.test_result(z0ctx, msg, True, False)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, msg, True, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            ctx['actions_mc'] = 'not_existent_action'
            sts = self.Z.test_result(z0ctx, msg, False, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            lx.append(MY_ACT)
            ctx['actions_mc'] = 'unit_test'
            sts = self.Z.test_result(z0ctx, msg, True, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            sts = do_single_action(oerp, ctx, 'unit_test')
            sts = self.Z.test_result(z0ctx, msg, TEST_SUCCESS, sts)
        if sts == TEST_SUCCESS:
            sts = do_single_action(oerp, ctx, MY_ACT)
            sts = self.Z.test_result(z0ctx, msg, TEST_SUCCESS, sts)
        return sts


#
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)
