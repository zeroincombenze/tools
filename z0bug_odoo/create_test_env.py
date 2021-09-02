#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create Test Environment base

-A action: one of folowing actions
    help: show this help
    create: create environment (default)
-G groups: one or more following group, comma separated
    BA: base data (Partners)
    FI: account data (Chart of Account, Fiscal Position)
    LO: logistic data (products, product template)
    SD: sale data (sale order)
    ALL: all data (default)
"""
from __future__ import print_function, unicode_literals
from past.builtins import basestring
from builtins import int

from python_plus import unicodes
import os
import sys
from datetime import date, datetime, timedelta
# import time
# import re
import base64
# import csv
# import getpass
# from unidecode import unidecode
from os0 import os0
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
from z0bug_odoo import z0bug_odoo_lib

__version__ = "1.0.5"


def env_ref(ctx, xref, retxref_id=None):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        model = 'ir.model.data'
        ids = clodoo.searchL8(ctx, model, [('module', '=', xrefs[0]),
                                           ('name', '=', xrefs[1])])
        if ids:
            if retxref_id:
                return ids[0]
            return clodoo.browseL8(ctx, model, ids[0]).res_id
    return False


def add_xref(ctx, xref, model, res_id):
    xrefs = xref.split('.')
    if len(xrefs) != 2:
        raise('Invalid xref %s' % xref)
    vals = {
        'module': xrefs[0],
        'name': xrefs[1],
        'model': model,
        'res_id': res_id
    }
    model = 'ir.model.data'
    id = env_ref(ctx, xref, retxref_id=True)
    if not id:
        return clodoo.createL8(ctx, model, vals)
    clodoo.writeL8(ctx, model, id, vals)
    return id


def setup_model_structure(ctx, model):
    """Store model structure into memory"""
    if not model:
        return
    ctx['STRUCT'] = ctx.get('STRUCT', {})
    if model in ctx['STRUCT']:
        return
    ctx['STRUCT'][model] = ctx['STRUCT'].get(model, {})
    for ir_id in clodoo.searchL8(
            ctx, 'ir.model.fields', [('model', '=', model)]):
        field = clodoo.browseL8(ctx, 'ir.model.fields', ir_id)
        attrs = {}
        for attr in ('required', 'readonly'):
            attrs[attr] = field[attr]
        if attrs['required']:
            attrs['readonly'] = False
        if (field.ttype in ('binary', 'reference') or
                (field.related and not field.required)):
            attrs['readonly'] = True
        attrs['ttype'] = field.ttype
        attrs['relation'] = field.relation
        ctx['STRUCT'][model][field.name] = attrs


def get_domain_field(ctx, model, vals, company_id,
                     field=None, parent_id=None, parent_name=None):
    for nm in ('code', 'acc_number', 'login', 'description', 'origin',
               'sequence', 'name'):
        if nm == 'code' and model == 'product.product':
            continue
        if nm in vals and nm in ctx['STRUCT'][model]:
            break
    domain = [(nm, '=', vals[field or nm])]
    if 'company_id' in ctx['STRUCT'][model]:
        domain.append(('company_id', '=', company_id))
    if parent_id and parent_name in ctx['STRUCT'][model]:
        domain.append((parent_name, '=', parent_id))
    ids = clodoo.searchL8(
        ctx, model, domain, context={'lang': 'en_US'})
    if len(ids) == 1:
        return ids[0]
    return False


def print_error(ctx, msg):
    if msg not in ctx['ERRORS']:
        ctx['ERRORS'].append(msg)
        print(msg)


def bind_fields(ctx, model, vals, company_id,
                parent_id=None, parent_model=None):
    setup_model_structure(ctx, model)
    parent_name = False
    for field in vals.copy():
        attrs = ctx['STRUCT'][model].get(field, {})
        if not attrs:
            print_error(ctx, 'Invalid field %s!' % field)
            if (model == 'account.payment.term.line' and
                    field == 'months' and
                    vals[field]):
                vals['days'] = (int(vals[field]) * 30) - 2
            del vals[field]
            continue
        if (model == 'account.account' and
                field == 'id' and
                vals[field].startswith('z0bug.')):
            xrefs = vals[field].split('.')
            ids = clodoo.searchL8(
                ctx, 'ir.model.data', [('module', '=', 'l10n_it_fiscal'),
                                       ('name', 'like', xrefs[1]),
                                       ('model', '=', 'account.account')])
            for xid in ids:
                xref = clodoo.browseL8(ctx, 'ir.model.data', xid)
                if xref and xref.name.endswith(xrefs[1]):
                    acc = clodoo.browseL8(ctx, model, xref.res_id)
                    if acc.company_id.id == company_id:
                        vals[field] = acc.id
                        break
            if 'user_type_id' in vals:
                if ctx['STRUCT'][model].get('nature', {}):
                    if isinstance(vals['user_type_id'], int):
                        acc = clodoo.browseL8(
                            ctx, 'account.account.type', vals['user_type_id'])
                    else:
                        acc = clodoo.browseL8(
                            ctx, 'account.account.type',
                            env_ref(ctx, vals['user_type_id']))
                    if acc.nature:
                        vals['nature'] = acc.nature
            continue
        elif model == 'account.payment.term.line' and field == 'option':
            if (vals[field] == 'fix_day_following_month' and
                    ctx['odoo_ver'] == '12.0'):
                vals[field] = 'day_following_month'
        elif field == 'id':
            continue
        elif parent_id and attrs.get('relation') == parent_model:
            vals[field] = parent_id
            parent_name = field
        elif field == 'company_id':
            vals[field] = company_id
            continue
        elif (attrs['ttype'] in (
                    'many2one', 'one2many', 'many2many') and
              len(os0.u(vals[field]).split('.')) == 2):
            vals[field] = env_ref(ctx, os0.u(vals[field]))
            continue
        elif attrs['ttype'] == 'boolean':
            vals[field] = os0.str2bool(vals[field], True)
        elif attrs['ttype'] == 'date':
            if vals[field].startswith('+'):
                vals[field] = str(
                    date.today() + timedelta(int(vals[field][1:])))
            elif vals[field].startswith('-'):
                vals[field] = str(
                    date.today() - timedelta(int(vals[field][1:])))
            elif vals[field].find('<#') >= 0:
                items = vals[field].split('-')
                for i, item in enumerate(items):
                    if item == '<#':
                        if i == 0:
                            items[i] = date.today().year - 1
                        elif i == 1:
                            items[i] = date.today().month - 1
                        elif i == 2:
                            items[i] = date.today().day - 1
                        if item[i] == 0:
                            item[i] = 1
                vals[field] = '%04d-%02d-%02d' % (
                    int(items[0]), int(items[1]), int(items[2]))
            elif vals[field].find('#>') >= 0:
                items = vals[field].split('-')
                for i, item in enumerate(items):
                    if item == '#>':
                        if i == 0:
                            items[i] = date.today().year + 1
                        elif i == 1:
                            items[i] = date.today().month + 1
                            if item[i] > 12:
                                item[i] = 12
                        elif i == 2:
                            items[i] = date.today().day + 1
                            if item[i] > 31:
                                item[i] = 31
                vals[field] = '%04d-%02d-%02d' % (
                    int(items[0]), int(items[1]), int(items[2]))
            elif vals[field].find('#') >= 0:
                items = vals[field].split('-')
                for i,item in enumerate(items):
                    if item == '#':
                        if i == 0:
                            items[i] = date.today().year
                        elif i == 1:
                            items[i] = date.today().month
                        elif i == 2:
                            items[i] = date.today().day
                vals[field] = '%04d-%02d-%02d' % (
                    int(items[0]), int(items[1]), int(items[2]))
        elif attrs['ttype'] == 'datetime':
            if vals[field].startswith('+'):
                vals[field] = str(
                    datetime.today() + timedelta(int(vals[field][1:])))
            elif vals[field].startswith('-'):
                vals[field] = str(
                    datetime.today() - timedelta(int(vals[field][1:])))
        elif attrs.get('relation'):
            setup_model_structure(ctx, attrs['relation'])
            value = get_domain_field(ctx, model, vals, company_id, field=field)
            if value:
                vals[field] = value
            else:
                del vals[field]
    if parent_id and parent_model:
        vals['id'] = get_domain_field(
            ctx, model, vals, company_id,
            parent_id=parent_id, parent_name=parent_name)
        if not vals['id']:
            del vals['id']
    if ctx['load_images'] and 'image' in ctx['STRUCT'][model]:
        file_image = os.path.join(
            os.path.dirname(__file__),
            'data',
            '%s.png' % vals['id'])
        if os.path.isfile(file_image):
            with open(file_image, 'rb') as fd:
                image = fd.read()
            vals['image'] = base64.b64encode(image)
    return vals, parent_name


def drop_unchanged_fields(ctx, vals, model, xid):
    rec = None
    if model and xid:
        rec = clodoo.browseL8(ctx, model, xid)
    for field in vals.copy():
        attrs = ctx['STRUCT'][model].get(field, {})
        if not attrs:
            del vals[field]
        if rec:
            if attrs['ttype'] == 'many2one':
                if rec[field] and vals[field] == rec[field].id:
                    del vals[field]
            elif attrs['ttype'] == 'boolean':
                if isinstance(vals[field], bool) and vals[field] == rec[field]:
                    del vals[field]
                elif os0.str2bool(vals[field], False) == rec[field]:
                    del vals[field]
            elif (isinstance(vals[field], (basestring, int)) and
                  vals[field] == rec[field]):
                del vals[field]
    return vals


def write_diff(ctx, model, xid, vals):
    vals = drop_unchanged_fields(ctx, vals, model, xid)
    if vals:
        if 'id' in vals:
            del vals['id']
        clodoo.writeL8(ctx, model, xid, vals)


def store_xref(ctx, xref, model, company_id,
               parent_id=None, parent_model=None):
    if parent_id and parent_model:
        print('%s->%s %s' % (parent_model, model, xref))
        xid = False
    else:
        xid = env_ref(ctx, xref)
        print(model, xref, xid)
    if ctx['dry_run']:
        return
    if not xid or ctx['force_test_values']:
        vals = unicodes(
            z0bug_odoo_lib.Z0bugOdoo().get_test_values(model, xref))
        vals, parent_name = bind_fields(ctx, model, vals, company_id,
                                        parent_id=parent_id,
                                        parent_model=parent_model)
        if xid:
            write_diff(ctx, model, xid, vals)
        else:
            if vals.get('id') and isinstance(vals['id'], int):
                xid = vals['id']
            else:
                xid = get_domain_field(ctx, model, vals, company_id,
                                       parent_id=parent_id,
                                       parent_model=parent_model)
            if xid:
                write_diff(ctx, model, xid, vals)
            else:
                if 'id' in vals:
                    del vals['id']
                xid = clodoo.createL8(ctx, model, vals)
            if not parent_id or not parent_model:
                add_xref(ctx, xref, model, xid)
    return xid


def mk_account_account(ctx, company_id):
    model = 'account.account'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs.sort()
    for xref in xrefs:
        # Prima i mastri
        if len(xref) == 12:
            store_xref(ctx, xref, model, company_id)
    for xref in xrefs:
        # poi i capoconti
        if len(xref) == 13:
            store_xref(ctx, xref, model, company_id)
    for xref in xrefs:
        # infine i sottoconti
        if len(xref) > 13:
            store_xref(ctx, xref, model, company_id)


def mk_fiscal_position(ctx, company_id):
    model = 'account.fiscal.position'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs.sort()
    for xref in xrefs:
        store_xref(ctx, xref, model, company_id)


def mk_date_range(ctx, company_id):
    model = 'date.range.type'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs.sort()
    for xref in xrefs:
        store_xref(ctx, xref, model, company_id)
    model = 'date.range'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs.sort()
    for xref in xrefs:
        store_xref(ctx, xref, model, company_id)


def mk_payment(ctx, company_id):
    model = 'account.payment.term'
    model2 = 'account.payment.term.line'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs = xrefs + z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model2)
    xrefs.sort()
    parent_id = False
    for xref in xrefs:
        if len(xref) == 15:
            parent_id = store_xref(ctx, xref, model, company_id)
            seq = 10
            for id in clodoo.searchL8(
                    ctx, model2, [('payment_id', '=', parent_id)],
                    order='sequence,id'):
                clodoo.writeL8(ctx, model2, id, {'sequence': seq})
                seq += 10
        else:
            store_xref(ctx, xref, model2, company_id,
                       parent_id=parent_id, parent_model=model)


def mk_partner(ctx, company_id):
    model = 'res.partner'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs.sort()
    parent_id = False
    for xref in xrefs:
        if len(xref) <= 20 or xref == 'z0bug.partner_mycompany':
            parent_id = store_xref(ctx, xref, model, company_id)
        else:
            store_xref(ctx, xref, model, company_id, parent_id=parent_id)


def mk_product(ctx, company_id):
    model = 'product.template'
    model2 = 'product.product'
    for num in range(28):
        xref = 'z0bug.product_template_%d' % num
        store_xref(ctx, xref, model, company_id)
        xref = 'z0bug.product_product_%d' % num
        store_xref(ctx, xref, model2, company_id)


def mk_account_invoice(ctx, company_id):
    model = 'account.invoice'
    model2 = 'account.invoice.line'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs = xrefs + z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model2)
    xrefs.sort()
    parent_id = False
    for xref in xrefs:
        if len(xref) <= 19:
            parent_id = store_xref(ctx, xref, model, company_id)
        else:
            store_xref(ctx, xref, model2, company_id,
                       parent_id=parent_id, parent_model=model)


def mk_sale_order(ctx, company_id):
    model = 'sale.order'
    model2 = 'sale.order.line'
    xrefs = z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model)
    xrefs = xrefs + z0bug_odoo_lib.Z0bugOdoo().get_test_xrefs(model2)
    xrefs.sort()
    parent_id = False
    for xref in xrefs:
        if len(xref) == 21:
            parent_id = store_xref(ctx, xref, model, company_id)
        else:
            store_xref(ctx, xref, model2, company_id,
                       parent_id=parent_id, parent_model=model)


def init_test(ctx, company_id):
    ctx['ERRORS'] = []
    if 'FI' in ctx['data_group'] or 'ALL' in ctx['data_group']:
        mk_account_account(ctx, company_id)
        mk_fiscal_position(ctx, company_id)
        mk_payment(ctx, company_id)
    if 'BA' in ctx['data_group'] or 'ALL' in ctx['data_group']:
        mk_partner(ctx, company_id)
        mk_date_range(ctx, company_id)
    if 'LO' in ctx['data_group'] or 'ALL' in ctx['data_group']:
        mk_product(ctx, company_id)


def create_env(ctx):
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company found!')
    ctx['company_id'] = company_id
    init_test(ctx, company_id)
    if 'SD' in ctx['data_group'] or 'ALL' in ctx['data_group']:
        mk_sale_order(ctx, company_id)
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Create test Environment",
                                "© 2018-2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-A", "--action",
                        help="action to execute (help to more info)",
                        dest="action",
                        metavar="python_name",
                        default='create')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default='./inv2draft_n_restore.conf')
    parser.add_argument("-d", "--dbname",
                        help="DB name to connect",
                        dest="db_name",
                        metavar="file",
                        default='')
    parser.add_argument("-f", "--force-test-values",
                        action='store_true',
                        help="Force values to original test values",
                        dest="force_test_values",
                        default=False)
    parser.add_argument("-G", "--data-groups",
                        help="Group of data",
                        dest="data_group",
                        default='ALL')
    parser.add_argument("-I", "--not-load-images",
                        action='store_false',
                        help="Load images into records",
                        dest="load_images",
                        default=True)
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                   db=ctx['db_name'],
                                   ctx=ctx)
    ctx['data_group'] = ctx['data_group'].split(',')
    if ctx['action'] == 'help':
        print(__doc__)
        sts = 0
    elif ctx['action'] == 'create':
        sts = create_env(ctx)
    else:
        print('Invalid action: use help to more info!')
        sts = 1
    sys.exit(sts)
