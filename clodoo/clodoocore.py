# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Clodoo core functions
"""

from os0 import os0

from clodoolib import debug_msg_log


__version__ = "0.1.15.7"


def _get_model_bone(oerp, ctx, o_model):
    """Inherit model structure from a parent model"""
    model = None
    hide_cid = False
    if ctx is not None:
        if 'model' in ctx:
            model = ctx['model']
            if model == '':
                model = None
            else:
                if 'hide_cid' in ctx:
                    hide_cid = ctx['hide_cid']
                else:
                    hide_cid = not _model_has_company(oerp,
                                                      ctx,
                                                      model)
    if model is None:
        if 'model' in o_model:
            model = o_model['model']
            if model == '':
                model = None
            if 'hide_cid' in o_model:
                hide_cid = o_model['hide_cid']
            else:
                hide_cid = not _model_has_company(oerp,
                                                  ctx,
                                                  model)
    return model, hide_cid


def _import_file_model(oerp, o_model, csv_fn):
    """Get model name of import file"""
    model, hide_cid = _get_model_bone(oerp, None, o_model)
    if model is None:
        model = os0.nakedname(csv_fn).replace('-', '.').replace('_', '.')
    return model, hide_cid


def _get_model_code(ctx, o_model):
    """Get key field(s) name of  model"""
    if 'model_code' in o_model:
        code = o_model['model_code']
    elif 'code' in o_model:
        code = o_model['code']
    elif 'name' in o_model:
        code = o_model['name']
    elif 'code' in ctx:
        code = 'code'
    elif 'name' in ctx:
        code = 'name'
    elif 'id' in ctx:
        code = 'id'
    else:
        code = 'name'
    return code


def _get_model_name(ctx, o_model):
    """Get description field(s) name of  model"""
    if 'name' in ctx:
        name = 'name'
    elif 'code' in ctx:
        name = 'code'
    elif 'model_name' in o_model:
        name = o_model['model_name']
    elif 'name' in o_model:
        name = o_model['name']
    elif 'code' in o_model:
        name = o_model['code']
    else:
        name = 'name'
    return name


def _import_file_dbtype(o_model, fields, csv_fn):
    """Get db selector name of import file"""
    if 'db_type' in o_model:
        db_type = o_model['db_type']
    elif 'db_type' in fields:
        db_type = 'db_type'
    else:
        db_type = False
    return db_type


def import_file_get_hdr(oerp, ctx, o_model, csv_obj, csv_fn, row):
    """Analyze csv file header and get header names
    Header will be used to load value in table
    @ return:
    @ [model]      model name
    @ [name]       field name which is the record description
    @ [code]       field name which is the record key
    @ [db_type]    field name which is db type selection
    @ [repl_by_id] true if no record key name found (search for id)
    @ [hide_id]    if true, no id will be returned
    """
    o_skull = {}
    for n in o_model:
        o_skull[n] = o_model[n]
    csv_obj.fieldnames = row['undef_name']
    o_skull['model'], o_skull['hide_cid'] = _import_file_model(oerp,
                                                               o_model,
                                                               csv_fn)
    o_skull['name'] = _get_model_name(csv_obj.fieldnames,
                                      o_model)
    o_skull['code'] = _get_model_code(csv_obj.fieldnames,
                                      o_model)
    o_skull['db_type'] = _import_file_dbtype(o_model,
                                             csv_obj.fieldnames,
                                             csv_fn)
    if o_skull['code'] != 'id' and 'id' in csv_obj.fieldnames:
        o_skull['repl_by_id'] = True
    else:
        o_skull['repl_by_id'] = False
    o_skull['hide_id'] = True
    return o_skull


def eval_value(oerp, ctx, o_model, name, value):
    """Evaluate value read form csv file: may be a function or macro
    @ oerp:        oerplib object
    @ ctx:         global parameters
    @ o_model:     special names
    @ name:        field name
    @ value:       field value (constant, macro or expression)
    """
    msg = u"eval_value(name=%s, value=%s)" % (os0.u(name), os0.u(value))
    debug_msg_log(ctx, 6, msg)
    if isinstance(value, basestring):
        if is_db_alias(oerp, value):
            value = expr(oerp,
                         ctx,
                         o_model,
                         name,
                         value)
        elif value[0:1] == "=":
            value = expr(oerp,
                         ctx,
                         o_model,
                         name,
                         value[1:])
            if isinstance(value, basestring) and \
                    (value == "None" or
                     (value[0:2] == "[(" and value[-2:] == ")]")):
                try:
                    value = eval(value, None, ctx)
                except BaseException:
                    pass
    return value


def expr(oerp, ctx, o_model, code, value):
    """Evaluate python expression value"""
    if isinstance(value, basestring):
        i, j = get_macro_pos(value)
        if i >= 0 and j > i:
            v = value[i + 2:j]
            x, y = get_macro_pos(v)
            while x >= 0 and y > i:
                v = expr(oerp, ctx, o_model, code, v)
                value = value[0:i + 2] + v + value[j:]
                i, j = get_macro_pos(value)
                v = value[i + 2:j]
                x, y = get_macro_pos(v)
            res = ""
            while i >= 0 and j > i:
                v = value[i + 2:j]
                if v.find(':') >= 0:
                    v = _query_expr(oerp, ctx, o_model, code, v)
                else:
                    try:
                        v = eval(v, None, ctx)
                    except BaseException:
                        pass
                if i > 0:
                    res = concat_res(res, value[0:i])
                value = value[j + 1:]
                res = concat_res(res, v)
                i, j = get_macro_pos(value)
            value = concat_res(res, value)
    if isinstance(value, basestring):
        if is_db_alias(oerp, value):
            model, name, value, hide_cid = get_model_alias(value)
            ids = _get_simple_query_id(oerp,
                                       ctx,
                                       model,
                                       name,
                                       value,
                                       hide_cid)
            if isinstance(ids, list):
                if len(ids):
                    if name == 'id' or isinstance(name, list):
                        value = ids[0]
                    else:
                        o = oerp.browse(model, ids[0])
                        value = getattr(o, name)
                else:
                    value = None
    return value


def _get_simple_query_id(oerp, ctx, model, code, value, hide_cid):
    """Execute a simple query to get ids from selection field(s)
    Do not expand value
    @ oerp:        oerplib object
    @ ctx:         global parameters
    @ model:       model name
    @ code:        field name
    @ value:       field value (just constant)
    @ hide_cid:    hide company_id
    """
    ids = _get_raw_query_id(oerp, ctx, model, code, value, hide_cid, '=')
    if model == 'ir.model.data' and len(ids) == 1:
        try:
            o = oerp.browse('ir.model.data', ids[0])
            ids = [o.res_id]
        except BaseException:
            ids = None
    if ids is None:
        return []
    if len(ids) == 0:
        ids = _get_raw_query_id(oerp,
                                ctx,
                                model,
                                code,
                                value,
                                hide_cid,
                                'ilike')
    return ids


def _get_raw_query_id(oerp, ctx, model, code, value, hide_cid, op):
    if not hide_cid and 'company_id' in ctx:
        company_id = ctx['company_id']
    else:
        company_id = None
    where = []
    if isinstance(code, list) and isinstance(value, list):
        for i, c in enumerate(code):
            if i < len(value):
                where = append_2_where(oerp,
                                       ctx,
                                       model,
                                       c,
                                       value[i],
                                       where,
                                       op)
            else:
                where = append_2_where(oerp,
                                       ctx,
                                       model,
                                       c,
                                       '',
                                       where,
                                       op)
    else:
        where = append_2_where(oerp,
                               ctx,
                               model,
                               code,
                               value,
                               where,
                               op)
    if company_id is not None:
        where.append(('company_id', '=', company_id))
    try:
        ids = oerp.search(model, where)
    except BaseException:
        ids = None
    return ids


def append_2_where(oerp, ctx, model, code, value, where, op):
    if value is not None and value != "":
        value = eval_value(oerp, ctx, model, code, value)
        if isinstance(value, basestring) and value[0] == '~':
            where.append('|')
            where.append((code, op, value))
            where.append((code, op, value[1:]))
        elif not isinstance(value, basestring) and \
                op in ('like', 'ilike', '=like', '=ilike'):
            where.append((code, '=', value))
        else:
            where.append((code, op, value))
    elif code == "country_id":
        where.append((code, '=', ctx['def_country_id']))
    elif code != "id" and code[-3:] == "_id":
        where.append((code, '=', ""))
    return where


def get_query_id(oerp, ctx, o_model, row):
    """Execute a query to get ids from fields in row read from csv
    Value may be expanded
    @ oerp:        oerplib object
    @ o_model:     special names
    @ ctx:         global parameters
    @ row:         record fields
    """
    msg = "get_query_id()"
    debug_msg_log(ctx, 6, msg)
    code = o_model['code']
    model, hide_cid = _get_model_bone(oerp, ctx, o_model)
    msg += "model=%s, hide_company=%s" % (model, hide_cid)
    value = row.get(code, '')
    if model is None:
        ids = []
    else:
        ids = _get_simple_query_id(oerp,
                                   ctx,
                                   model,
                                   code,
                                   value,
                                   hide_cid)
        if len(ids) == 0 and o_model['repl_by_id'] and row.get('id', None):
            o_skull = {}
            for n in o_model:
                o_skull[n] = o_model[n]
            o_skull['code'] = 'id'
            o_skull['hide_id'] = False
            value = eval_value(oerp,
                               ctx,
                               o_skull,
                               'id',
                               row['id'])
            ids = oerp.search(model,
                              [('id', '=', value)])
    return ids


def _query_expr(oerp, ctx, o_model, code, value):
    msg = "_quer_expr(value=%s)" % value
    debug_msg_log(ctx, 6, msg)
    model, name, value, hide_cid, fldname = _get_model_parms(oerp,
                                                             ctx,
                                                             o_model,
                                                             value)
    if model:
        if fldname == 'db_type':
            value = o_model.get('db_type', '')
        else:
            value = _get_simple_query_id(oerp,
                                         ctx,
                                         model,
                                         name,
                                         value,
                                         hide_cid)
            if isinstance(value, list):
                if len(value):
                    value = value[0]
                    if fldname != 'id':
                        o = oerp.browse(model, value)
                        value = getattr(o, fldname)
                else:
                    value = None
    return value


def validate_field(oerp, model, name):
    if oerp.search('ir.model.fields',
                   [('model', '=', model),
                    ('name', '=', name)]):
        return True
    return False


def _model_has_company(oerp, ctx, model):
    return validate_field(oerp, model, 'company_id')


def get_macro_pos(value):
    i = value.find("${")
    o = 0
    j = value.find("}", o)
    if i >= 0:
        p = i + 2
        k = value.find("${", p)
    else:
        k = -1
    while k >= 0 and j >= 0 and k < j:
        o = j + 1
        j = value.find("}", o)
        p = k + 1
        k = value.find("${", p)
    return i, j


def _get_model_parms(oerp, ctx, o_model, value):
    """Extract model parameters and pure value from value and structure"""
    model, hide_cid = _get_model_bone(oerp, ctx, o_model)
    sep = '::'
    name = 'name'
    fldname = 'id'
    i = value.find(sep)
    if i >= 0:
        hide_cid = False
    else:
        sep = ':'
        i = value.find(sep)
        if i >= 0:
            hide_cid = True
    if i < 0:
        n, v = is_db_alias(oerp, value)
        if n:
            model = "ir.model.data"
            name = ['module', 'name']
            value = v
            hide_cid = True
        else:
            model = None
            try:
                value = eval(value, None, ctx)
            except BaseException:
                pass
    else:
        model = value[:i]
        # value = prefix + value[i + len(sep):] + suffix
        value = value[i + len(sep):]
        model, fldname = _get_name_n_ix(model, deflt=fldname)
        model, x = _get_name_n_params(model, name)
        if x.find(',') >= 0:
            name = x.split(',')
            value = value.split(',')
        else:
            name = x
    return model, name, value, hide_cid, fldname


def concat_res(res, value):
    if isinstance(res, basestring) and res:
        if isinstance(value, basestring):
            res = res + value
        elif isinstance(value, (bool, int, long, float)):
            res = res + str(value)
    elif isinstance(res, (bool, int, long, float)):
        if isinstance(value, basestring) and value:
            res = str(res) + value
        elif isinstance(value, (bool, int, long, float)):
            res = str(res) + str(value)
    else:
        res = value
    return res


def is_db_alias(oerp, value):
    model, name, value, hide_cid = get_model_alias(value)
    if model and name and value and oerp.search(model,
                                                [(name[0],'=', value[0]),
                                                 (name[1], '=', value[1])]):
        return True
    return False


def get_model_alias(value):
    if value:
        i = value.find('.')
        j = value.find('.', i + 1)
        if i >=0 and j < 0 and value[0] >= 'a' and value[0] <= 'z':
            model = "ir.model.data"
            name = ['module', 'name']
            value = [value[0:i], value[i + 1:]]
            hide_cid = True
            return model, name, value, hide_cid
    return None, None, value, None


def _get_name_n_params(name, deflt=None):
    """Extract name and params from string like 'name(params)'"""
    deflt = '' if deflt is None else deflt
    i = name.find('(')
    j = name.rfind(')')
    if i >= 0 and j >= i:
        n = name[:i]
        p = name[i + 1:j]
    else:
        n = name
        p = deflt
    return n, p


def _get_name_n_ix(name, deflt=None):
    """Extract name and subscription from string like 'name[ix]'"""
    deflt = '' if deflt is None else deflt
    i = name.find('[')
    j = name.rfind(']')
    if i >= 0 and j >= i:
        n = name[:i]
        x = name[i + 1:j]
    else:
        n = name
        x = deflt
    return n, x
