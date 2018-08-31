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

import re

import odoorpc
import oerplib
from os0 import os0

from clodoolib import debug_msg_log, msg_log, decrypt
from transodoo import translate_from_sym, translate_from_to

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    postgres_drive = True
except BaseException:                                        # pragma: no cover
    postgres_drive = False


STS_FAILED = 1
STS_SUCCESS = 0


__version__ = "0.3.7.28"


#############################################################################
# Low level (driver) functions
def psql_connect(ctx):
    cr = False
    if postgres_drive and ctx.get('psycopg2', False):
        params = ctx['psycopg2'].split(',')
        for prm in params:
            pv = prm.split(':')
            if pv[0] in ('False', 'false', '0'):
                return cr
            if pv[0] in ('db_name', 'db_user', 'db_password') and \
                    (pv[0] not in ctx or not ctx[pv[0]]):
                ctx[pv[0]] = pv[1]
        dbname = ctx['db_name']
        dbuser = ctx['db_user']
        pwd = ctx.get('db_password')
        cnx = psycopg2.connect(dbname=dbname, user=dbuser, password=pwd)
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cr = cnx.cursor()
    return cr


#############################################################################
# Connection and database
#
def connectL8(ctx):
    """Open connection to Odoo service"""
    try:
        if ctx['svc_protocol'] == 'jsonrpc':
            odoo = odoorpc.ODOO(ctx['db_host'],
                                ctx['svc_protocol'],
                                ctx['xmlrpc_port'])
        else:
            odoo = oerplib.OERP(server=ctx['db_host'],
                                protocol=ctx['svc_protocol'],
                                port=ctx['xmlrpc_port'],
                                version=ctx['oe_version'])
    except BaseException:                                    # pragma: no cover
        return u"!Odoo server %s is not running!" % ctx['oe_version']
    if ctx['svc_protocol'] == 'jsonrpc':
        ctx['server_version'] = odoo.version
    else:
        try:
            ctx['server_version'] = odoo.db.server_version()
        except BaseException:
            ctx['server_version'] = odoo.version
    x = re.match(r'[0-9]+\.[0-9]+', ctx['server_version'])
    if ctx['server_version'][0:x.end()] != ctx['oe_version']:
        return u"!Invalid Odoo Server version: expected %s, found %s!" % \
            (ctx['oe_version'], ctx['server_version'])
    ctx['majver'] = int(ctx['server_version'].split('.')[0])
    ctx['odoo_session'] = odoo
    return True


#############################################################################
# Primitive version indipendent
#
def searchL8(ctx, model, where, order=None, context=None):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].search(where, order=order,
                                                     context=context)
    else:
        return ctx['odoo_session'].search(model, where, order=order,
                                          context=context)


def browseL8(ctx, model, id, context=None):
    if ctx['svc_protocol'] == 'jsonrpc':
        res = ctx['odoo_session'].env[model].browse(id)
    else:
        res = ctx['odoo_session'].browse(model, id, context=context)
    return bound_6_to_z0(ctx, model, res)


def createL8(ctx, model, vals):
    vals = bound_z0_to_6(ctx, model, vals)
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].create(vals)
    else:
        return ctx['odoo_session'].create(model, vals)


def write_recordL8(ctx, record):
    # vals = bound_z0_to_6(ctx, model, vals)
    if ctx['svc_protocol'] == 'jsonrpc':
        ctx['odoo_session'].write(record)
    else:
        ctx['odoo_session'].write_record(record)


def writeL8(ctx, model, ids, vals):
    vals = bound_z0_to_6(ctx, model, vals)
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].write(ids,
                                                    vals)
    else:
        return ctx['odoo_session'].write(model,
                                         ids,
                                         vals)


def unlinkL8(ctx, model, ids):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].unlink(ids)
    else:
        return ctx['odoo_session'].unlink(model, ids)


def executeL8(ctx, model, action, *args):
    return ctx['odoo_session'].execute(model,
                                       action,
                                       *args)


###########################################################
# Version adaptive functions
#
def bound_z0_to_6(ctx, model, vals, btable=None):
    """Convert universal (z0) format to original (6.1) format.
    Designed to convert 7.0 record to 6.1,
    may be used to any Odoo version translation.
    If btable is empty, build bound table to translate fields.
    Bound table ha format 6_name=z0_name.
    6_name is 6.1 field name
    z0_name is 7.0 field name or False is does not exist,
    In res.user, this function always remove country_id field.
    """
    if btable:
        for p in btable:
            if isinstance(btable[p], basestring):
                if p not in vals and btable[p] in vals:
                    vals[p] = vals[btable[p]]
                if btable[p] in vals:
                    del vals[btable[p]]
            else:
                if p in vals:
                    del vals[p]
    elif model == 'res.users':
        if ctx['oe_version'] == "6.1":
            btable = {
                'partner_id': False,
                'context_lang': 'lang',
                'context_tz': 'tz',
                'user_email': 'email',
                'country_id': False,
            }
            return bound_z0_to_6(ctx, model, vals, btable=btable)
    return vals


def bound_6_to_z0(ctx, model, res, btable=None):
    """Convert browsed res from original (6.1) format to universal (z0) format.
    Designed to convert 6.1 record to 7.0,
    may be used to any Odoo version translation.
    If btable is empty, build bound table to translate fields.
    Bound table ha format z0_name=6_name.
    z0_name is 7.0 field name,
    6_name is 6.1 field name or False is does not exist
    Field name may have format res_id.name , which refer to another model.
    In res.user, this function always add country_id field.
    """
    if btable:
        for p in btable:
            if isinstance(btable[p], basestring):
                i = btable[p].find('.')
                if i >= 0:
                    p1 = btable[p][0:i]
                    p2 = btable[p][i + 1:]
                    setattr(res, p, res[p1][p2])
                else:
                    setattr(res, p, res[btable[p]])
                # delattr(res, btable[p])
            else:
                setattr(res, p, btable[p])
    elif model == 'res.users':
        if ctx['oe_version'] == "6.1":
            btable = {
                'partner_id': False,
                'lang': 'context_lang',
                'tz': 'context_tz',
                'email': 'user_email',
                'country_id': 'company_id.country_id',
            }
            return bound_6_to_z0(ctx, model, res, btable=btable)
    return res


def get_res_users(ctx, user, field):
    if field == 'name':
        if ctx['oe_version'] == "6.1":
            return user.name
        else:
            return user.partner_id.name
    elif field == 'lang':
        if ctx['oe_version'] == "6.1":
            return user.context_lang
        else:
            return user.partner_id.lang
    elif field == 'email':
        if ctx['oe_version'] == "6.1":
            return user.user_email
        else:
            return user.partner_id.email
    elif field == 'country_id':
        if ctx['oe_version'] == "6.1":
            if user.company_id.country_id:
                return user.company_id.country_id.id
            return False
        else:
            if user.partner_id.country_id:
                return user.partner_id.country_id.id
            elif user.company_id.country_id:
                return user.company_id.country_id.id
            return False
    return user[field]


###########################################################
# Others
#
def _get_model_bone(ctx, o_model):
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
                    hide_cid = not _model_has_company(ctx,
                                                      model)
    if model is None:
        if 'model' in o_model:
            model = o_model['model']
            if model == '':
                model = None
            if 'hide_cid' in o_model:
                hide_cid = o_model['hide_cid']
            else:
                hide_cid = not _model_has_company(ctx,
                                                  model)
    return model, hide_cid


def _import_file_model(ctx, o_model, csv_fn):
    """Get model name of import file"""
    model, hide_cid = _get_model_bone(ctx, o_model)
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
    if 'model_name' in o_model:
        name = o_model['model_name']
    elif 'name' in o_model:
        name = o_model['name']
    elif 'code' in o_model:
        name = o_model['code']
    elif 'name' in ctx:
        name = 'name'
    elif 'code' in ctx:
        name = 'code'
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


def import_file_get_hdr(ctx, o_model, csv_obj, csv_fn, row):
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
    o_skull = o_model.copy()
    csv_obj.fieldnames = row['undef_name']
    o_skull['model'], o_skull['hide_cid'] = _import_file_model(ctx,
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
    o_skull['alias_model2'] = o_model.get('alias_model2', '')
    o_skull['alias_field'] = o_model.get('alias_field', '')
    return o_skull


def get_company_id(ctx):
    value = get_db_alias(ctx, 'base.mycompany')
    if not value or not value.isdigit(): 
        model = 'res.company'
        company_name = ctx.get('company_name', 'La % Azienda')
        ids = searchL8(ctx, model, [('name', 'ilike', company_name)])
        if not ids:
            ids = searchL8(ctx, model, [('id', '>', 1)])
        if ids:
            value = ids[0]
        else:
            value =  1
    if 'company_id' not in ctx:
        ctx['company_id'] = value
    return value


def get_country_id(ctx, value):
    if value:
        model = 'res.country'
        ids = searchL8(ctx, model,
                       [('code', '=', value.upper())])
        if not ids:
            ids = searchL8(ctx, model,
                           [('name', 'ilike', value)])
        if ids:
            value = ids[0]
        else:
            value = False
    else:
        value = ctx['def_country_id']
    return value


def get_state_id(ctx, value, country_id=None):
    if value:
        if not country_id:
            country_id = ctx['def_country_id']
        model = 'res.country.state'
        ids = searchL8(ctx, model,
                       [('country_id', '=', country_id),
                        ('code', '=', value.upper())])
        if not ids:
            ids = searchL8(ctx, model,
                           [('country_id', '=', country_id),
                            ('name', 'ilike', value)])
        if ids:
            value = ids[0]
        else:
            value = False
    return value


def set_some_values(ctx, o_model, name, value, model=None, row=None):
    """Set default value for empties fields"""
    if not model and o_model and o_model['model']:
        model = o_model['model']
    if not value and name in ctx.get('DEFAULT', ''):
        value = ctx['DEFAULT'][name]
    elif name == 'company_id':
        if not value:
            value = ctx['company_id']
    elif name == 'country_id':
        value = get_country_id(ctx, value)
    elif model == 'res.partner':
        if name == 'is_company':
            return True
        elif name == 'vat':
            if ctx.get('country_code') == 'IT' and value.isdigit():
                value = 'IT%011d' % int(value)
        elif name == 'state_id':
            if row and 'country_id' in row:
                value = get_state_id(ctx, value, country_id=row['country_id'])
            else:
                value = get_state_id(ctx, value)
    elif model == 'res.users':
        if name == 'email':
            if ctx['with_demo']:
                return ctx['def_email']
            elif not ctx['with_demo']:
                return ctx['zeroadm_mail']
    return value


def eval_value(ctx, o_model, name, value):
    """Evaluate value read form csv file: may be a function or macro
    @ ctx:         global parameters
    @ o_model:     special names
    @ name:        field name
    @ value:       field value (constant, macro or expression)
    """
    msg = u"eval_value(name=%s, value=%s)" % (os0.u(name), os0.u(value))
    debug_msg_log(ctx, 6, msg)
    if not value:
        return set_some_values(ctx, o_model, name, value)
    elif isinstance(value, basestring):
        eval_dict = True
        if value.find('$1$!') == 0:
            value = decrypt(value[4:])
        if is_db_alias(ctx, value):
            value = get_db_alias(ctx, value)
        else:
            if value and value[0] == '=':
                value = expr(ctx,
                             o_model,
                             name,
                             value[1:])
                eval_dict = False
            elif value.find("${") >= 0 and value.find("}") >= 0:
                value = expr(ctx,
                             o_model,
                             name,
                             value)
                eval_dict = False
            elif value[0:2] == "[(" and value[-2:] == ")]":
                value = expr(ctx,
                             o_model,
                             name,
                             value)
                eval_dict = False
        if isinstance(value, basestring):
            if value in ('None', 'True', 'False') or \
                    (value[0:2] == "[(" and value[-2:] == ")]"):
                if eval_dict:
                    try:
                        value = eval(value, None, ctx)
                    except BaseException:                    # pragma: no cover
                        pass
                else:
                    try:
                        value = eval(value)
                    except BaseException:            # pragma: no cover
                        pass
            elif value.isdigit():
                ir_model = 'ir.model.fields'
                ids = searchL8(ctx,
                               ir_model,
                               [('model', '=', o_model),
                                ('name', '=', name)])
                if ids:
                    ttype = browseL8(ctx,
                                     ir_model,
                                     ids[0]).ttype
                    if ttype in ('integer', 'float', 'many2one'):
                        try:
                            value = eval(value)
                        except BaseException:            # pragma: no cover
                            pass
    return value


def expr(ctx, o_model, code, value):
    """Evaluate python expression value"""
    if isinstance(value, basestring):
        i, j = get_macro_pos(value)
        if i >= 0 and j > i:
            v = value[i + 2:j]
            x, y = get_macro_pos(v)
            while x >= 0 and y > i:
                v = expr(ctx, o_model, code, v)
                value = value[0:i + 2] + v + value[j:]
                i, j = get_macro_pos(value)
                v = value[i + 2:j]
                x, y = get_macro_pos(v)
            res = ""
            while i >= 0 and j > i:
                v = value[i + 2:j]
                if v.find(':') >= 0:
                    v = _query_expr(ctx, o_model, code, v)
                else:
                    if v == 'zeroadm_email' and ctx['with_demo']:
                        v = 'def_email'
                    try:
                        v = eval(v, None, ctx)
                    except BaseException:                    # pragma: no cover
                        pass
                if i > 0:
                    res = concat_res(res, value[0:i])
                value = value[j + 1:]
                res = concat_res(res, v)
                i, j = get_macro_pos(value)
            value = concat_res(res, value)
    if isinstance(value, basestring) and \
            value[0:2] == "[(" and value[-2:] == ")]":
        res = []
        for v in value[2:-2].split(','):
            res.append(get_db_alias(ctx, v, fmt='string'))
        value = '[(%s)]' % ','.join(res)
    if isinstance(value, basestring):
        value = get_db_alias(ctx, value)
    return value


def _get_simple_query_id(ctx, model, code, value, hide_cid):
    """Execute a simple query to get ids from selection field(s)
    Do not expand value
    @ ctx:         global parameters
    @ model:       model name
    @ code:        field name
    @ value:       field value (just constant)
    @ hide_cid:    hide company_id
    """
    ids = _get_raw_query_id(ctx, model, code, value, hide_cid, '=')
    if model == 'ir.model.data' and len(ids) == 1:
        try:
            ids = [browseL8(ctx, 'ir.model.data', ids[0]).res_id]
        except BaseException:                                # pragma: no cover
            ids = None
    if ids is None:
        return []
    if len(ids) == 0 and model != 'res.users':
        ids = _get_raw_query_id(ctx,
                                model,
                                code,
                                value,
                                hide_cid,
                                'ilike')
    return ids


def _get_raw_query_id(ctx, model, code, value, hide_cid, op):
    if not hide_cid and 'company_id' in ctx:
        where = [('company_id', '=', ctx['company_id'])]
    else:
        where = []
    if isinstance(code, list) and isinstance(value, list):
        for i, c in enumerate(code):
            if i < len(value):
                where = append_2_where(ctx,
                                       model,
                                       c,
                                       value[i],
                                       where,
                                       op)
            else:
                where = append_2_where(ctx,
                                       model,
                                       c,
                                       '',
                                       where,
                                       op)
    else:
        where = append_2_where(ctx,
                               model,
                               code,
                               value,
                               where,
                               op)
    try:
        ids = searchL8(ctx, model, where)
    except BaseException:                                    # pragma: no cover
        ids = None
    return ids


def append_2_where(ctx, model, code, value, where, op):
    if value is not None and value != "":
        value = eval_value(ctx, model, code, value)
        if isinstance(value, basestring) and value and value[0] == '~':
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


def get_query_id(ctx, o_model, row):
    """Execute a query to get ids from fields in row read from csv
    Value may be expanded
    @ o_model:     special names
    @ ctx:         global parameters
    @ row:         record fields
    """
    model, hide_cid = _get_model_bone(ctx, o_model)
    msg = "get_query_id(model=%s, hide_company=%s)" % (model, hide_cid)
    debug_msg_log(ctx, 6, msg)
    ids = []
    if o_model['repl_by_id'] and row.get('id', None):
        o_skull = o_model.copy()
        o_skull['code'] = 'id'
        o_skull['hide_id'] = False
        value = eval_value(ctx,
                           o_skull,
                           'id',
                           row['id'])
        if isinstance(value, (int, long)):
            ids = searchL8(ctx, model, [('id', '=', value)])
    if not ids:
        if o_model['code'].find(',') >= 0:
            code = o_model['code'].split(',')
        else:
            code = o_model['code']
        if isinstance(code, list):
            value = []
            for p in code:
                value.append(row.get(p, ''))
        else:
            value = row.get(code, '')
        if not value:
            if o_model['name'].find(',') >= 0:
                code = o_model['name'].split(',')
            else:
                code = o_model['name']
            if isinstance(code, list):
                value = []
                for p in code:
                    value.append(row.get(p, ''))
            else:
                value = row.get(code, '')
        if model is None or not value:
            ids = []
        else:
            ids = _get_simple_query_id(ctx,
                                       model,
                                       code,
                                       value,
                                       hide_cid)
    return ids


def _query_expr(ctx, o_model, code, value):
    msg = "_quer_expr(value=%s)" % value
    debug_msg_log(ctx, 6, msg)
    model, name, value, hide_cid, fldname = _get_model_parms(ctx,
                                                             o_model,
                                                             value)
    if model:
        if fldname == 'db_type':
            value = o_model.get('db_type', '')
        elif fldname == 'oe_versions':
            value = value == ctx['server_version']
        else:
            value = _get_simple_query_id(ctx,
                                         model,
                                         name,
                                         value,
                                         hide_cid)
            if isinstance(value, list):
                if len(value):
                    value = value[0]
                    if fldname != 'id':
                        o = browseL8(ctx, model, value)
                        value = getattr(o, fldname)
                else:
                    value = None
    return value


def validate_field(ctx, model, name):
    # FIX for Odoo 7.0
    if model in ('res.users', 'res.partner') and name in ('id', 'name'):
        return True
    elif searchL8(ctx,
                'ir.model.fields',
                [('model', '=', model),
                 ('name', '=', name)]):
        return True
    return False


def _model_has_company(ctx, model):
    return validate_field(ctx, model, 'company_id')


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


def _get_model_parms(ctx, o_model, value):
    """Extract model parameters and pure value from value and structure"""
    model, hide_cid = _get_model_bone(ctx, o_model)
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
        n, v = is_db_alias(ctx, value)
        if n:
            model = "ir.model.data"
            name = ['module', 'name']
            value = v
            hide_cid = True
        else:
            model = None
            try:
                value = eval(value, None, ctx)
            except BaseException:                            # pragma: no cover
                pass
    else:
        model = value[:i]
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


def is_db_alias(ctx, value):
    model, name, value, hide_cid = get_model_alias(value)
    if model == 'ir.transodoo':
        if value[2] and value[2] != '0':
            return translate_from_to(ctx,
                                     value[0],
                                     name,
                                     value[1],
                                     value[2],
                                     ctx['oe_version']) != ''
        else:
            return translate_from_sym(ctx,
                                      value[0],
                                      value[1],
                                      ctx['oe_version']) != ''
    if ctx['svc_protocol'] == 'jsonrpc':
        if model and name and value and ctx['odoo_session'].env[model].search(
                [(name[0], '=', value[0]),
                 (name[1], '=', value[1])]):
            return True
    else:
        if model and name and value and searchL8(
                ctx,
                model,
                [(name[0], '=', value[0]),
                 (name[1], '=', value[1])]):
            return True
    return False


def get_db_alias(ctx, value, fmt=None):
    if is_db_alias(ctx, value):
        model, name, value, hide_cid = get_model_alias(value)
        if model == 'ir.transodoo':
            if value[2] and value[2] != '0':
                return translate_from_to(ctx,
                                         value[0],
                                         value[1],
                                         value[2],
                                         ctx['oe_version'])
            else:
                return translate_from_sym(ctx,
                                          value[0],
                                          value[1],
                                          ctx['oe_version'])
        ids = _get_simple_query_id(ctx,
                                   model,
                                   name,
                                   value,
                                   hide_cid)
        if isinstance(ids, list):
            if len(ids):
                if name == 'id' or isinstance(name, list):
                    value = ids[0]
                    if fmt == 'string':
                        value = str(value)
                else:
                    o = browseL8(ctx, model, ids[0])
                    value = getattr(o, name)
            else:
                value = None
    return value


def get_model_alias(value):
    if value:
        items = value.split('.')
        if len(items) == 3 and items[0][0] >= 'a' and items[0][0] <= 'z' and \
                items[-1][0].isdigit():
            model = "ir.transodoo"
            name = ['module', 'name', 'version']
            value = [items[0], items[1], items[2]]
            hide_cid = True
            return model, name, value, hide_cid
        elif len(items) == 2 and items[0][0] >= 'a' and items[0][0] <= 'z':
            model = "ir.model.data"
            name = ['module', 'name']
            value = [items[0], items[1]]
            hide_cid = True
            return model, name, value, hide_cid
    return None, None, value, None


def put_model_alias(ctx,
                    model=None, name=None, ref=None, id=None, module=None):
    if ref:
        refs = ref.split('.')
        if len(refs):
            if not module:
                module = refs[0]
            if not name:
                name = refs[1]
    module = module or 'base'
    if model and name and id:
        ids = searchL8(ctx, 'ir.model.data',
                       [('model', '=', model),
                        ('module', '=', module),
                        ('name', '=', name)])
        if ids:
            writeL8(ctx, 'ir.model.data', ids, {'res_id': id})
        else:
            vals = {
                'module': module,
                'model': model,
                'name': name,
                'res_id': id,
            }
            createL8(ctx, 'ir.model.data', vals)
    else:
        msg = 'Invalid alias ref'
        msg_log(ctx, ctx['level'], msg)


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
