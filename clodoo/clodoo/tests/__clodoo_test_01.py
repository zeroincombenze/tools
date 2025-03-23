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
from __future__ import print_function, unicode_literals

import sys
from datetime import date

from past.builtins import basestring

try:
    from clodoo.clodoo import (
        check_4_actions,
        create_act_list,
        do_single_action,
        isaction,
    )
    from clodoo.clodoocore import (
        _get_model_bone,
        _get_model_code,
        _get_model_name,
        _import_file_dbtype,
        _import_file_model,
        eval_value,
        get_query_id,
        import_file_get_hdr,
        model_has_company,
    )
except BaseException:
    from clodoo import check_4_actions, create_act_list, do_single_action, isaction
    from clodoocore import (
        _get_model_bone,
        _get_model_code,
        _get_model_name,
        _import_file_dbtype,
        _import_file_model,
        model_has_company,
        eval_value,
        get_query_id,
        import_file_get_hdr,
    )

from zerobug import z0test

__version__ = "2.0.9"

MODULE_ID = "clodoo"
TEST_FAILED = 1
TEST_SUCCESS = 0
MY_ACT = "my_actions"

CID = 9
DEF_CID = 1
REF_ID = 1
ID_0 = 11
ID_1 = 1
ID_I = 4
ID_C_0 = 13
MARK = "Zeroincombenze®"
CTRY_IT = 110
PARTNER_DEF = 2
USER_DEF = 3


def version():
    return __version__


class Oerp:
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

        # system table: ir.model
        model = "ir.model"
        self.db["model"] = {}
        self.db[model] = {
            1: {
                "model": "res.zero",
                "module": "test",
                "name": "res.zero",
                "field_ids": [],
            },
            2: {
                "model": "res.one",
                "module": "test",
                "name": "res.one",
                "field_ids": [],
            },
            3: {
                "model": "res.three",
                "module": "test",
                "name": "res.three",
                "field_ids": [],
            },
            4: {
                "model": "res.four",
                "module": "test",
                "name": "res.four",
                "field_ids": [],
            },
            5: {
                "model": "res.five",
                "module": "test",
                "name": "res.five",
                "field_ids": [],
            },
        }

        # system table: ir.model.fields
        model = "ir.model.fields"
        self.db["model"] = {}
        self.db[model] = {
            1: {
                "model": "res.zero",
                "modules": "test",
                "name": "name",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "char",
            },
            2: {
                "model": "res.zero",
                "modules": "test",
                "name": "ref",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "integer",
            },
            3: {
                "model": "res.zero",
                "modules": "test",
                "name": "description",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "text",
            },
            4: {
                "model": "res.one",
                "modules": "test",
                "name": "name",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "char",
            },
            5: {
                "model": "res.one",
                "modules": "test",
                "name": "ref0",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "integer",
            },
            6: {
                "model": "res.one",
                "modules": "test",
                "name": "company_id",
                "readonly": False,
                "relation": "res.company",
                "required": True,
                "ttype": "many2one",
            },
            7: {
                "model": "res.two",
                "modules": "test",
                "name": "name",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "char",
            },
            8: {
                "model": "res.two",
                "modules": "test",
                "name": "country_id",
                "readonly": False,
                "relation": "res.country",
                "required": True,
                "ttype": "many2one",
            },
            9: {
                "model": "res.three",
                "modules": "test",
                "name": "name",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "char",
            },
            10: {
                "model": "res.three",
                "modules": "test",
                "name": "ref0",
                "readonly": False,
                "relation": False,
                "required": True,
                "ttype": "integer",
            },
            11: {
                "model": "res.three",
                "modules": "test",
                "name": "company_id",
                "readonly": False,
                "relation": "res.company",
                "required": True,
                "ttype": "many2one",
            },
        }

        # system table: ir.model.data
        model = "ir.model.data"
        self.db["model"] = {}
        self.db[model] = {
            1: {
                "model": "res.company",
                "module": "base",
                "name": "main_company",
                "res_id": ID_0,
            }
        }

        # date test table: res.zero
        # name, ref, description
        model = "res.zero"
        self.db["model"] = {}
        self.db[model] = {ID_0: {"name": "myname", "ref": REF_ID, "description": MARK}}

        # date test table: res.one
        # name, ref0, company_id
        model = "res.one"
        self.db["model"] = {}
        self.db[model] = {ID_1: {"name": "myname", "ref0": ID_0, "company_id": CID}}

        # date test table: res.two
        # name, country_id
        model = "res.two"
        self.db["model"] = {}
        self.db[model] = {REF_ID: {"name": "myname", "country_id": CTRY_IT}}

        # date test table: res.three
        # name, ref0, company_id
        model = "res.three"
        self.db["model"] = {}
        self.db[model] = {ID_1: {"name": "name àèìòù", "ref0": ID_0, "company_id": CID}}

    def comp_tuple(self, left, op, right):
        """Apply for op between 2 operands
        op may be '==', '!=' or 'ilike'
        """
        if op == "=":
            return left == right
        elif op == "!=":
            return left != right
        elif op == "ilike":
            return left.lower().find(right.lower()) >= 0
        return False

    def eval_where(self, model, where):
        """Evaluate sql where condition"""
        if model == "":
            raise IOError("*** No model supplied!!!")
        if model not in self.db:
            raise IOError("*** Invalid model %s !!!" % model)
        if len(where) == 1:
            return where[0]
        left = where[0]
        op = where[1]
        right = where[2]
        res = []
        if left == "id":
            if right in self.db[model]:
                res = [right]
            else:
                res = []
        else:
            for id in self.db[model]:
                if left not in self.db[model][id]:
                    raise IOError("*** Invalid field %s in model %s!!!" % (left, model))
                if self.comp_tuple(self.db[model][id][left], op, right):
                    res.append(id)
        return res

    def search(self, model, where, order=None, context=None):
        """Simulate search function"""
        if model == "":
            raise IOError("*** No model supplied!!!")
        if model not in self.db:
            raise IOError("*** Invalid " + model + " model!!!")
        res = [id for id in self.db[model]]
        while where:
            cond = self.eval_where(model, where.pop(0))
            if cond == "|":
                res = list(
                    set(res)
                    & (
                        set(self.eval_where(model, where.pop(0)))
                        | set(self.eval_where(model, where.pop(0)))
                    )
                )
            elif cond == "&":
                res = list(
                    set(res)
                    & set(self.eval_where(where.pop(0)))
                    & set(self.eval_where(where.pop(0)))
                )
            elif isinstance(cond, (list, tuple)):
                res = list(set(res) & set(cond))
            elif isinstance(cond, (int, float)):
                if id not in res:
                    res.append(cond)
        return res

    def browse1(self, model, id, context=None):
        """Simulate browse function on single record"""
        if model == "":
            raise IOError("*** No model supplied!!!")
        if model not in self.db:
            raise IOError("*** Invalid %s model!!!" % model)
        if id not in self.db[model]:
            return None
        for field in self.db[model][id]:
            setattr(self, field, self.db[model][id][field])
        return self

    def browse(self, model, ids, context=None):
        """Simulate browse on 1 or more records"""
        if isinstance(ids, list):
            res = []
            for id in ids:
                res.append(self.browse1(model, id, context=context))
            return res
        else:
            return self.browse1(model, ids, context=context)


class Csv:
    """csv simulator for test execution"""

    def _init(self):
        self.fieldnames = ""


class Conf:
    """confparser simulator for test execution"""

    def _init(self):
        pass

    def has_section(self, section):
        if section == MY_ACT:
            return True
        else:
            return False

    def has_option(self, section, name):
        if section == MY_ACT and name == "actions":
            return True
        else:
            return False

    def get(self, section, name):
        if section == MY_ACT and name == "actions":
            return "unit_test"
        else:
            return False


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib
        self.oerp = False
        self.dbname = False

    def new_db(self, dbname):
        if dbname != self.dbname:
            self.oerp = Oerp()
            self.dbname = dbname
        elif not self.oerp:
            self.oerp = Oerp()
        return self.oerp

    def init_test(self, model):
        oerp = self.new_db("clodoo_test")
        o_model = {}
        ctx = {}
        ctx["odoo_session"] = oerp
        ctx["server_version"] = "8.0"
        ctx["majver"] = int(ctx["server_version"].split(".")[0])
        ctx["svc_protocol"] = "xmlrpc"
        if model not in ("res.zero", "res.two", "res.four"):
            ctx["def_company_id"] = DEF_CID
            ctx["company_id"] = CID
        else:
            o_model["hide_cid"] = True
        ctx["def_partner_id"] = PARTNER_DEF
        ctx["def_user_id"] = USER_DEF
        ctx["def_country_id"] = CTRY_IT
        ctx["panda"] = "P"
        ctx["P" + str(ctx["def_partner_id"])] = "PP"
        ctx["panda" + ctx["P" + str(ctx["def_partner_id"])]] = "PPP"
        conf_obj = Conf()
        ctx["_conf_obj"] = conf_obj
        ctx["_opt_obj"] = None
        ctx["actions_db"] = ""
        ctx["actions_mc"] = ""
        ctx["test_unit_mode"] = True
        if model in ("res.zero", "res.one"):
            o_model["db_type"] = "Z"
        elif model in ("res.two",):
            o_model["db_type"] = "T"
        else:
            o_model["db_type"] = "C"
        o_model["name"] = "name"
        o_model["code"] = "name"
        o_model["model"] = model
        csv_fn = ""
        row = {}
        row["undef_name"] = ""
        csv_obj = Csv()
        o_model = import_file_get_hdr(ctx, o_model, csv_obj, csv_fn, row)
        return oerp, ctx, o_model, csv_obj, csv_fn, row

    def test_01(self, z0ctx):
        msg = "_get_model_bone"
        sts = TEST_SUCCESS
        for model_name in ("res.zero", "res.one", "res.two", "res.four"):
            oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(model_name)
            model, hide_cid = _get_model_bone(ctx, o_model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx, msg, model_name, model)
            if sts == TEST_SUCCESS:
                if model in ("res.zero", "res.two", "res.four"):
                    sts = self.Z.test_result(z0ctx, msg, True, hide_cid)
                else:
                    sts = self.Z.test_result(z0ctx, msg, False, hide_cid)

        for model_name in ("res.zero", "res.one", "res.two"):
            oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(model_name)
            del o_model["hide_cid"]
            model, hide_cid = _get_model_bone(ctx, o_model)
            sts = self.Z.test_result(z0ctx, msg, model_name, model)
            if sts == TEST_SUCCESS:
                if model in ("res.zero", "res.two", "res.four"):
                    sts = self.Z.test_result(z0ctx, msg, True, hide_cid)
                else:
                    sts = self.Z.test_result(z0ctx, msg, False, hide_cid)

        msg = "_import_file_model"
        for csv_fn in ("res_zero.csv", "res-zero.csv", "res.zero.csv"):
            o_model = {}
            if sts == TEST_SUCCESS:
                model, hide_cid = _import_file_model(ctx, o_model, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, "res.zero", model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx, msg, False, hide_cid)
            if sts == TEST_SUCCESS:
                o_model["model"] = "res.one"
                model, hide_cid = _import_file_model(ctx, o_model, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, "res.one", model)
            if sts == TEST_SUCCESS:
                sts = self.Z.test_result(z0ctx, msg, False, "hide_cid" in o_model)
        return sts

    def test_02(self, z0ctx):
        o_model = {}
        msg = "_get_model_name"
        sts = TEST_SUCCESS
        for n in ("id", "name", "code", "other"):
            if sts == TEST_SUCCESS:
                fields = ["a", "b", n, "z"]
                name = _get_model_name(fields, o_model)
                if n == "other" or n == "id":
                    sts = self.Z.test_result(z0ctx, msg, "name", name)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, name)

        fields = ["id", "name", "code", "my_name", "other"]
        for n in ("id", "name", "code", "my_name", "other"):
            if sts == TEST_SUCCESS:
                o_model["model_name"] = n
                name = _get_model_name(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, name)

        o_model = {}
        for n in ("id", "name", "code", "my_name", "other"):
            if sts == TEST_SUCCESS:
                o_model["name"] = n
                name = _get_model_name(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, name)
        return sts

    def test_03(self, z0ctx):
        o_model = {}
        msg = "_get_model_code"
        sts = TEST_SUCCESS
        for n in ("id", "name", "code", "other"):
            if sts == TEST_SUCCESS:
                fields = ["a", "b", n, "z"]
                code = _get_model_code(fields, o_model)
                if n == "other":
                    sts = self.Z.test_result(z0ctx, msg, "name", code)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, code)

        fields = ["id", "name", "code", "my_name", "other"]
        for n in ("id", "name", "code", "my_name", "other"):
            if sts == TEST_SUCCESS:
                o_model["model_code"] = n
                code = _get_model_code(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, code)

        o_model = {}
        for n in ("id", "name", "code", "my_name", "other"):
            if sts == TEST_SUCCESS:
                o_model["code"] = n
                code = _get_model_code(fields, o_model)
                sts = self.Z.test_result(z0ctx, msg, n, code)

        return sts

    def test_04(self, z0ctx):
        o_model = {}
        msg = "_import_file_dbtype"
        csv_fn = "res-zero.csv"
        sts = TEST_SUCCESS
        for n in ("db_type", "id", "name", "code", "other"):
            if sts == TEST_SUCCESS:
                fields = ["a", "b", n, "z"]
                name = _import_file_dbtype(o_model, fields, csv_fn)
                if n != "db_type":
                    sts = self.Z.test_result(z0ctx, msg, False, name)
                else:
                    sts = self.Z.test_result(z0ctx, msg, n, name)

        fields = ["db_type", "id", "name", "code", "my_name", "other"]
        for n in ("id", "name", "code", "my_name"):
            if sts == TEST_SUCCESS:
                o_model["db_type"] = n
                name = _import_file_dbtype(o_model, fields, csv_fn)
                sts = self.Z.test_result(z0ctx, msg, n, name)
        return sts

    def test_05(self, z0ctx):
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(None)
        msg = "eval_value"
        sts = TEST_SUCCESS

        name = "code"
        value = "=${panda}"
        res = eval_value(ctx, o_model, name, value)
        tres = "P"
        sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = "${panda}"
            res = eval_value(ctx, o_model, name, value)
            tres = "P"
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = "=${panda}${def_partner_id}"
            res = eval_value(ctx, o_model, name, value)
            tres = "P" + str(ctx["def_partner_id"])
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = "${panda}${def_partner_id}"
            res = eval_value(ctx, o_model, name, value)
            tres = "P" + str(ctx["def_partner_id"])
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = "=${${panda}${def_partner_id}}"
            res = eval_value(ctx, o_model, name, value)
            tres = "PP"
            sts = self.Z.test_result(z0ctx, msg, tres, res)
        if sts == TEST_SUCCESS:
            value = "=${panda${${panda}${def_partner_id}}}"
            res = eval_value(ctx, o_model, name, value)
            tres = "PPP"

        for name in ("db_type", "id", "name", "code", "my_name", "other"):
            msg = "eval_value(" + name + ")"
            for value in (b"abc", "def", True, False, 13715, 4.5, date(1959, 6, 26)):
                if sts == TEST_SUCCESS:
                    res = eval_value(ctx, o_model, name, value)
                    if value == b"abc":
                        sts = self.Z.test_result(z0ctx, msg, "abc", res)
                    else:
                        sts = self.Z.test_result(z0ctx, msg, value, res)

            for v in ctx:
                if sts == TEST_SUCCESS:
                    value = "=${" + v + "}"
                    res = eval_value(ctx, o_model, name, value)
                    if isinstance(ctx[v], (basestring, bool, int, float)):
                        sts = self.Z.test_result(z0ctx, msg, ctx[v], res)

                if sts == TEST_SUCCESS:
                    value = "=0-${" + v + "}-9"
                    if isinstance(ctx[v], basestring):
                        tres = "0-" + ctx[v] + "-9"
                    elif isinstance(ctx[v], (bool, int, float)):
                        tres = "0-" + str(ctx[v]) + "-9"
                    else:
                        tres = "0--9"
                    res = eval_value(ctx, o_model, name, value)
                    sts = self.Z.test_result(z0ctx, msg, tres, res)

            for model_name in ("res.zero", "res.one", "res.two", "res.three"):
                oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(model_name)
                if model_name == "res.three":
                    value = model_name + "::name àèìòù"
                elif model_name in ("res.zero", "res.two", "res.four"):
                    value = model_name + ":myname"
                else:
                    value = model_name + "::myname"
                if sts == TEST_SUCCESS:
                    res = eval_value(ctx, o_model, name, value)
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
                    elif model_name in ("res.zero", "res.two", "res.four"):
                        value = value + ":myname}"
                    else:
                        value = value + "::myname}"
                    res = eval_value(ctx, o_model, name, value)
                    if name == "name" and model_name == "res.three":
                        sts = self.Z.test_result(z0ctx, msg, "name àèìòù", res)
                    elif name == "name":
                        sts = self.Z.test_result(z0ctx, msg, "myname", res)
                    elif name == "db_type":
                        if model_name in ("res.zero", "res.one"):
                            tres = "Z"
                        elif model_name in ("res.two",):
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
                            sts = self.Z.test_result(z0ctx, msg, REF_ID, res)
                        elif value[0:12] == "=${res.three":
                            sts = self.Z.test_result(z0ctx, msg, ID_1, res)
                        else:
                            sts = self.Z.test_result(z0ctx, msg, False, True)
            if sts == TEST_SUCCESS:
                value = "base.main_company"
                name = "company_id"
                res = eval_value(ctx, o_model, name, value)
                sts = self.Z.test_result(z0ctx, msg, ID_0, res)
        return sts

    def test_06(self, z0ctx):
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test("res.one")
        msg = "eval_value"
        sts = TEST_SUCCESS
        for x in (("name", "my_name"), ("other", "=${res.zero:myname}")):
            if sts == TEST_SUCCESS:
                name = x[0]
                value = x[1]
                res = eval_value(ctx, o_model, name, value)
                if name == "name":
                    tres = "my_name"
                elif name == "other":
                    tres = ID_0
                sts = self.Z.test_result(z0ctx, msg, tres, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${res.zero(name,ref):myname," + str(REF_ID) + "}"
                res = eval_value(ctx, o_model, name, value)
                sts = self.Z.test_result(z0ctx, msg, ID_0, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${res.zero(name,ref)[description]:myname," + str(REF_ID) + "}"
                res = eval_value(ctx, o_model, name, value)
                sts = self.Z.test_result(z0ctx, msg, MARK, res)
            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=${company_id+1}"
                res = eval_value(ctx, o_model, name, value)
                sts = self.Z.test_result(z0ctx, msg, CID + 1, res)

            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=[(6,0,${company_id})]"
                res = eval_value(ctx, o_model, name, value)
                tres = [(6, 0, CID)]
                sts = self.Z.test_result(z0ctx, msg, tres, res)

            if sts == TEST_SUCCESS:
                name = "ref0"
                value = "=None"
                res = eval_value(ctx, o_model, name, value)
                if res is not None:
                    tres = True
                else:
                    tres = res
                sts = self.Z.test_result(z0ctx, msg, tres, res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = "=${res.two(country_id,name):" + ",myname}"
            res = eval_value(ctx, o_model, name, value)
            sts = self.Z.test_result(z0ctx, msg, REF_ID, res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = "=${res.two(country_id,name):" + ",not_exists}"
            res = eval_value(ctx, o_model, name, value)
            sts = self.Z.test_result(z0ctx, msg, "", res)

        if sts == TEST_SUCCESS:
            name = "name"
            value = (
                "=${res.one(company_id,ref0)::" + "${company_id},${res.zero:myname}}"
            )
            res = eval_value(ctx, o_model, name, value)
            sts = self.Z.test_result(z0ctx, msg, ID_1, res)
        return sts

    def test_07(self, z0ctx):
        msg = "model_has_company"
        sts = TEST_SUCCESS
        for model in ("res.zero", "res.one", "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_bones, csv_obj, csv_fn, row = self.init_test(model)
                res = model_has_company(ctx, model)
                if model == "res.zero":
                    tres = False
                elif model == "res.one":
                    tres = True
                elif model == "res.two":
                    tres = False
                sts = self.Z.test_result(z0ctx, msg, tres, res)

    def test_08(self, z0ctx):
        msg = "get_query_id"
        sts = TEST_SUCCESS
        for model in ("res.zero", "res.one", "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_bones, csv_obj, csv_fn, row = self.init_test(model)
                row["id"] = ""
                row["name"] = "myname"
                row["other"] = "=${res.one:myname}"
                res = get_query_id(ctx, o_bones, row)
                if model == "res.zero":
                    tres = [ID_0]
                elif model == "res.one":
                    tres = [ID_1]
                elif model == "res.two":
                    tres = [REF_ID]
                sts = self.Z.test_result(z0ctx, msg, tres, res)

            if model == "res.zero":
                if sts == TEST_SUCCESS:
                    o_bones["code"] = "ref"
                    row["ref"] = "=${res.two:~myname}"
                    res = get_query_id(ctx, o_bones, row)
                    sts = self.Z.test_result(z0ctx, msg, [ID_0], res)
                if sts == TEST_SUCCESS:
                    row["id"] = "base.main_company"
                    row["name"] = "my_name"
                    row["other"] = "hello world"
                    res = get_query_id(ctx, o_bones, row)
                    sts = self.Z.test_result(z0ctx, msg, [ID_0], res)

            if model in ("res.zero", "res.two"):
                if sts == TEST_SUCCESS:
                    oerp, ctx, o_bones, csv_obj, csv_fn, row = self.init_test(model)
                    o_bones["repl_by_id"] = True
                    row["id"] = ""
                    res = get_query_id(ctx, o_bones, row)
                    sts = self.Z.test_result(z0ctx, msg, [], res)

                for _i in range(2):
                    if sts == TEST_SUCCESS:
                        # repeat 2 time to check side effects
                        if model == "res.zero":
                            row["id"] = ID_0
                        elif model == "res.one":
                            row["id"] = ID_1
                        elif model == "res.two":
                            row["id"] = REF_ID
                        elif model == "res.three":
                            row["id"] = ID_1
                        row["name"] = "not_exists"
                        res = get_query_id(ctx, o_bones, row)
                        sts = self.Z.test_result(z0ctx, msg, 1, len(res))
                    if sts == TEST_SUCCESS:
                        sts = self.Z.test_result(z0ctx, msg, row["id"], res[0])

            for _i in range(2):
                if sts == TEST_SUCCESS:
                    # repeat 2 time to check side effects
                    row["id"] = ""
                    row["name"] = "not_exists"
                    res = get_query_id(ctx, o_bones, row)
                    sts = self.Z.test_result(z0ctx, msg, [], res)
        return sts

    def test_09(self, z0ctx):
        msg = "get_query_id (id)"
        sts = TEST_SUCCESS
        for model in ("res.zero", "res.one", "res.two"):
            if sts == TEST_SUCCESS:
                oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test(model)
                if model == "res.zero":
                    tres = ID_0
                elif model == "res.one":
                    tres = ID_1
                elif model == "res.two":
                    tres = REF_ID
                row["id"] = tres
                row["name"] = "myname"
                row["other"] = "=${res.zero:myname}"
                res = get_query_id(ctx, o_model, row)
                sts = self.Z.test_result(z0ctx, msg, [tres], res)
        return sts

    def test_10(self, z0ctx):
        msg = "actions"
        oerp, ctx, o_model, csv_obj, csv_fn, row = self.init_test("res.zero")
        ctx = create_act_list(ctx)
        sts = TEST_SUCCESS
        lx = ctx["_lx_act"]
        if isaction(ctx, lx[0]):
            ctx["actions_db"] = lx[0]
            ctx["actions_mc"] = lx[1]
        else:
            sts = self.Z.test_result(z0ctx, msg, True, False)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(z0ctx, msg, True, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            ctx["actions_mc"] = "not_existent_action"
            sts = self.Z.test_result(z0ctx, msg, False, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            lx.append(MY_ACT)
            ctx["actions_mc"] = "unit_test"
            sts = self.Z.test_result(z0ctx, msg, True, check_4_actions(ctx))
        if sts == TEST_SUCCESS:
            sts = do_single_action(ctx, "unit_test")
            sts = self.Z.test_result(z0ctx, msg, TEST_SUCCESS, sts)
        if sts == TEST_SUCCESS:
            sts = do_single_action(ctx, MY_ACT)
            sts = self.Z.test_result(z0ctx, msg, TEST_SUCCESS, sts)
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
