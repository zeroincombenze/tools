#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()                                 # noqa: E402
from past.builtins import basestring
from builtins import *                                             # noqa
from builtins import input

import os
import sys
from datetime import date, datetime
import time
from os0 import os0
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
import pdb      # pylint: disable=deprecated-module

__version__ = "1.0.0.3"

L_NUM_FATT1 = 'FAT/2020/0001'
L_NUM_FATT2 = 'FAT/2020/0002'
X_NUM_DDT = '1234'
# X_NUM_ORDER = '1234'
L_NUM_ORDER = 'SO002'
CANDIDATE_KEYS = ('acc_number', 'login','default_code', 'code', 'key',
                  'serial_number', 'description', 'comment', 'name',
                  'dim_name')
RESET_FIELD = ('prezzo_unitario', 'goods_description_id',
               'carriage_condition_id', 'transportation_method_id')
TNL_TABLE = {
    'account.account': '',
    'account.account.type': '',
    'account.invoice': '',
    'account.invoice.line': '',
    'account.payment.term': 'payments',
    'account.tax': 'tax_codes',
    # 'crm.team': '',
    'italy.conai.product.category': 'conai',
    'italy.conai.partner.category': 'esenzione_conai',
    'product.product': 'products',
    'product.template': '',
    'product.uom': 'ums',
    'res.currency': '',
    'res.country': 'countries',
    'res.country.state': 'regions',
    'res.partner': 'customers',
    'res.partner.shipping': 'customers_shipping_addresses',
    'res.partner.supplier': 'suppliers',
    'stock.picking.package.preparation': 'ddt',
    'stock.picking.package.preparation.line': '',
    'stock.picking.transportation_reason': '',
    'sale.order': '',
    'sale.order.line': '',
}

BORDERLINE_TABLE = {
    'account.account': {
    },
    'account.account.type': {
    },
    'account.invoice': {
        'number': 'move_name',
    },
    'account.invoice.line': {
        'partner_id': False,
        'vg7_partner_id': False,
    },
    'account.payment.term': {
        'code': False,
        'description': 'name',
    },
    'account.payment.term.line': {
        'scadenza': False,
        'fine_mese': False,
        'giorni_fine_mese': 'payment_days',
    },
    'account.tax': {
        'aliquota': 'amount',
        'code': ['name', 'nounknown'],
        'description': ['name', 'nounknown'],
    },
    'italy.conai.product.category': {
        'description': 'name',
        'prezzo_unitario': 'conai_price_unit',
    },
    'product.product': {
        'conai_id': 'conai_category_id',
        'code': 'default_code',
        'description': 'name',
    },
    'product.template': {
        'conai_id': False,
        'code': 'default_code',
        'description': 'name',
    },
    'product.uom': {
        'code': 'name',
    },
    'res.country': {
        'description': ['name', 'nocase'],
    },
    'res.country.state': {
        'description': ['name', 'nocase'],
    },
    'res.partner': {
        'bank_id': False,
        'billing_pec': 'pec_destinatario',
        'cf': 'fiscalcode',
        'codice_univoco': 'codice_destinatario',
        'company': 'name',
        'country': 'country_id',
        'customer_id': 'parent_id',
        'esonerato_fe': 'electronic_invoice_subjected',
        'name': 'firstname',
        'note': 'invoice_warn_msg',
        'payment_id': 'property_payment_term_id',
        'piva': 'vat',
        'postal_code': 'zip',
        'region': 'state_id',
        'region_id': 'state_id',
        'surename': 'lastname',
        'tax_code_id': False,
        'telephone2': 'mobile',
        'telephone': 'phone',
        'street_number': False,
    },
    'res.partner.bank': {
        'IBAN': 'acc_number',
        'customer_id': 'partner_id',
        'description': False,
    },
    'sale.order': {
        'name': 'client_order_ref',
        'date': 'date_order',
        'order_number': ['name', 'nounknown'],
        'customer_id': 'partner_id',
        'payment_id': 'payment_term_id',
        'customer_shipping_id': 'partner_shipping_id',
        'courier_id': False,
        'agent_id': False
    },
    'sale.order.line': {
        'product_name': 'name',
        'unitary_price': 'price_unit',
        'quantity': 'product_uom_qty',
        'partner_id': False,
        'vg7_partner_id': False,
    },
    'stock.picking.package.preparation': {
        'numero_colli': 'parcels',
        'customer_id': 'partner_id',
        'customer_shipping_id': 'partner_shipping_id',
        'vettori_prima_riga': False,
        'voce_doganale': False,
        'aspetto_esteriore_dei_beni': 'goods_description_id',
        'causal_id': 'transportation_reason_id',
        'vettori_seconda_riga': False,
        'note': False,
        'peso_netto': False,
        'tipo_porto': False,
        'peso_lordo': False,
        'ora_ritiro': False,
        'data_emissione': 'date',
        'data_ritiro': 'date_done',
        'mezzo': False,
    },
    'stock.picking.package.preparation.line': {
        # 'ddt_id': 'package_preparation_id',
        'ddt_id': False,
        'descrizione': 'name',
        'quantita': 'product_uom_qty',
        'prezzo_unitario': 'price_unit',
        'order_id': 'sale_id',
        'order_row_id': 'sale_line_id',
        'vg7:tax_code_id': 'tax_ids',
        'product_id': False,
        'tax_code_id': False,
        'tax_id': False,
        'peso': 'weight',
        'um': False,
        'um_id': 'product_uom_id',
        # 'um_id': False,
        'conai_id': 'conai_category_id',
    },
    'stock.picking.transportation_reason': {
        'description': 'name',
    },
}

TABLE_OF_FIELD = {
    'company_id': 'res.company',
    'country_id': 'res.country',
    'conai_category_id': 'italy.conai.product.category',
    'goods_description_id': 'stock.picking.goods_description',
    'invoice_id': 'account.invoice',
    'journal_id': 'account.journal',
    'order_id': 'sale.order',
    'partner_id': 'res.partner',
    'partner_shipping_id': 'res.partner',
    'payment_term_id': 'account.payment.term',
    'product_id': 'product.product',
    'product_tmpl_id': 'product.template',
    'product_uom_id': 'product.uom',
    'property_payment_term_id': 'account.payment.term',
    'sale_id': 'sale.order',
    'sale_line_id': 'sale.order.line',
    'state_id': 'res.country.state',
    'transportation_reason_id': 'stock.picking.transportation_reason',
    'user_type_id': 'account.account.type',
}

MODULE_LIST = [
    'account', 'account_payment_term_extension', 'purchase',
    'sale', 'stock',
    'l10n_it_fiscalcode', 'l10n_it_ddt',
    'l10n_it_einvoice_out', 'l10n_it_ricevute_bancarie',
    'connector_vg7',
    'partner_bank',
]

RES_COUNTRY = [
    {'id': 39, 'code': 'IT', 'description': 'Italia'},
]
RES_COUNTRY_STATE = [
    {'id': 2, 'code': 'MI', 'description': 'Milano'},
    {'id': 11, 'code': 'TO', 'description': 'Torino'},
    {'id': 54, 'code': 'BO', 'description': 'Bologna'},
]
ACCOUNT_TAX = [
    {'id': 22, 'code': '22%', 'description': '', 'aliquota': 22},
    {'id': 4, 'code': '4%', 'description': '', 'aliquota': 4},
    {'id': 101, 'code': 'a101', 'description': 'Forfettario art 101',
     'aliquota': 0},
]
ACCOUNT_TAX_DEFAULT = [
    {'description': '22v', 'name': 'IVA 22%', 'amount': 22},
    {'description': '4v', 'name': 'IVA 4%', 'amount': 4},
]
ACCOUNT_PAYMENT_TERM = [
    {'id': 30, 'code': '30', 'description': 'RiBA 30GG/FM'},
    {'id': 3060, 'code': '31', 'description': 'RiBA 30/60 GG/FM'},
]
ACCOUNT_CONAI = [
    {'id': 1, 'code': 'CA', 'description': 'Carta', 'prezzo_unitario': 35},
]
PRODUCT_PRODUCT = [
    {'id': 1, 'code': 'AAA', 'description': 'Product Alpha', 'conai_id': 1},
    {'id': 2, 'code': 'BBB', 'description': 'Product Beta', 'conai_id': 1},
    {'id': 3, 'code': 'CCC', 'description': 'Product CC', 'conai_id': False},
]
PRODUCT_TEMPLATE = [
    {'id': 1, 'code': 'AA', 'description': 'Product Alpha', 'conai_id': 1},
    {'id': 2, 'code': 'BB', 'description': 'Product Beta', 'conai_id': 1},
    {'id': 3, 'code': 'CCC', 'description': 'Product CC', 'conai_id': False},
]
RES_PARTNER = [
    {'id': 7, 'company': 'Partner A', 'name': None, 'surename': None,
     'street': 'Via Porta Nuova',
     'street_number': '13',
     'postal_code': '10100',
     'city': 'Torino',
     'region': 'TORINO',
     'region_id': 11,
     'country_id': 'Italia',
     'esonerato_fe': '1',
     'piva': '00385870480',
     'payment_id': 30,
     'goods_description_id': False,
     'carriage_condition_id': False,
     'transportation_method_id': False,
     'electronic_invoice_subjected': False,
     },
    {'id': 2, 'company': None, 'name': None, 'surename': None,
     'street': None,
     'street_number': None,
     'postal_code': None,
     'city': None,
     'region': None,
     'region_id': None,
     'country_id': None,
     'esonerato_fe': None,
     'piva': None,
     'payment_id': None,
     'goods_description_id': 'l10n_it_ddt.goods_description_SFU',
     'carriage_condition_id': 'l10n_it_ddt.carriage_condition_PAF',
     'transportation_method_id': 'l10n_it_ddt.transportation_method_COR',
    },
    {'id': 17, 'company': None, 'name': 'Mario', 'surename': 'Rossi',
     'street': None,
     'street_number': None,
     'postal_code': None,
     'city': None,
     'region': None,
     'region_id': None,
     'country_id': None,
     'esonerato_fe': None,
     'piva': None,
     'payment_id': None,
     'goods_description_id': False,
     'carriage_condition_id': False,
     'transportation_method_id': False,
     },
]

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

def delete_record(ctx, model, domain, multi=False, action=None,
                  childs=None, company_id=False):
    if isinstance(domain, basestring):
        ids = env_ref(ctx, domain)
        ids = [ids] if ids else []
    else:
        if company_id:
            domain.append(('company_id', '=', company_id))
        ids = clodoo.searchL8(ctx, model, domain)
    if (not multi and len(ids) == 1) or (multi and len(ids)):
        if action:
            if not isinstance(action, (list, tuple)):
                action = [action]
            for act in action:
                if act == 'move_name=':
                    clodoo.writeL8(ctx, model, ids, {'move_name': ''})
                else:
                    try:
                        clodoo.executeL8(ctx, model, act, ids)
                    except BaseException:
                        print('Warning! Cannot execute %s.%s' % (
                            model, act
                        ))
        if childs:
            for parent in clodoo.browseL8(ctx, model, ids):
                for rec in parent[childs]:
                    clodoo.unlinkL8(ctx, model, rec.id)
        clodoo.unlinkL8(ctx, model, ids)

def write_record(ctx, model, domain, vals, company_id=False, create=None,
                 unique=None):
    if isinstance(domain, basestring):
        ids = env_ref(ctx, domain)
        ids = [ids] if ids else []
    else:
        if company_id:
            domain.append(('company_id', '=', company_id))
        ids = clodoo.searchL8(ctx, model, domain)
    if ids:
        clodoo.writeL8(ctx, model, ids, vals)
        if unique and len(ids) > 1:
            print('Warning: Too many records "%s.%s"' % (model, domain))
            delete_record(
                ctx, model, [('id', 'in', ids[1:])])
    elif create:
        ids = [clodoo.createL8(ctx, model, vals)]
    return ids

def unlink_vg7(model):
    domain = ['|']
    if model == 'res.partner':
        domain.append('|')
    for nm in ('vg7_id', 'oe8_id'):
        domain.append((nm, '>', 0))
    if model == 'res.partner':
        domain.append(('vg72_id', '>', '0'))
    vals = {
        'vg7_id': False,
        'oe8_id': False,
    }
    if model == 'res.partner':
        vals['vg72_id'] = False
    ids = clodoo.searchL8(ctx, model, domain)
    for id in ids:
        clodoo.writeL8(ctx, model, id, vals)

def rm_file_2_pull(ext_model):
    if os.path.isfile(os.path.expanduser('~/clodoo/%s.csv' % ext_model)):
        os.unlink(os.path.expanduser('~/clodoo/%s.csv' % ext_model))

def set_sequence(ctx, domain, next_number, multi=False, company_id=False):
    model = 'ir.sequence'
    if company_id:
        domain.append(('company_id', '=', company_id))
    ids = clodoo.searchL8(ctx, model, domain)
    if (not multi and len(ids) == 1) or (multi and len(ids)):
        for rec in clodoo.browseL8(ctx, model, ids):
            clodoo.writeL8(
                ctx, model, ids, {'number_next_actual': next_number,
                                  'number_next': next_number})
            for rec1 in rec.date_range_ids:
                if rec1.date_from < date.today() <= rec1.date_to:
                    clodoo.writeL8(
                        ctx, '%s.date_range' % model, rec1.id,
                        {'number_next_actual': next_number,
                         'number_next': next_number})

def store_id(ctx, model, id, vg7_id):
    if model not in BORDERLINE_TABLE:
        BORDERLINE_TABLE[model] = {}
    if 'EXT' not in BORDERLINE_TABLE[model]:
        BORDERLINE_TABLE[model]['LOC'] = {}
        BORDERLINE_TABLE[model]['EXT'] = {}
    if isinstance(vg7_id, basestring):
        BORDERLINE_TABLE[model]['LOC'][id] = eval(vg7_id)
        BORDERLINE_TABLE[model]['EXT'][eval(vg7_id)] = id
    else:
        BORDERLINE_TABLE[model]['LOC'][id] = vg7_id
        BORDERLINE_TABLE[model]['EXT'][vg7_id] = id

def write_file_2_pull(ext_model, vals, mode=None, identity=None):
    mode = mode or 'w'
    if mode == 'a':
        data = '%s\n' % (
            ','.join(map(lambda x: str(vals[x]), vals.keys()))
        )
    else:
        data = '%s\n%s\n' % (
            ','.join(vals.keys()),
            ','.join(map(lambda x: str(vals[x]), vals.keys()))
        )
    if identity:
        fn = os.path.expanduser('~/clodoo/%s/%s.csv' % (identity, ext_model))
    else:
        fn = os.path.expanduser('~/clodoo/%s.csv' % ext_model)
    with open(fn, mode) as fd:
        fd.write(data)

def get_vg7id_from_id(ctx, model, id):
    return clodoo.browseL8(ctx, model, id).vg7_id

def get_id_from_vg7id(ctx, model, vg7_id, name=None):
    name = name or 'vg7_id'
    ids = clodoo.searchL8(ctx, model, [(name, '=', vg7_id)])
    if ids:
        return ids[0]
    return -1

def jacket_vals(vals, prefix=None):
    prefix = prefix or 'vg7:'
    for nm in vals.copy():
        if not nm.startswith('%s'):
            vals['%s%s' % (prefix, nm)] = vals[nm]
            del vals[nm]
    return vals

def shirt_vals(vals):
    for nm in vals.copy():
        new_name = nm.replace('billing_', '').replace('shipping_', '')
        if new_name != nm:
            vals[new_name] = vals[nm]
            del vals[nm]
    return vals

def get_loc_name(model, field):
    mode = False
    if model in BORDERLINE_TABLE and field in BORDERLINE_TABLE[model]:
        loc_name = BORDERLINE_TABLE[model][field]
        if loc_name and isinstance(loc_name, (tuple, list)):
            mode = loc_name[1]
            loc_name = loc_name[0]
    else:
        loc_name = field
    return loc_name, mode

def load_n_test_model(
        ctx, model, default, mode=None, store=None, test_pfx=None,
        test_suppl=None):
    if model == 'res.partner':
        pdb.set_trace()
    ext_model = TNL_TABLE[model]
    main_ext_id = False
    wa = 'w'
    for datas in default:
        vals = datas.copy()
        for field in datas:
            if vals[field] is None:
                del vals[field]
                continue
            loc_name, dummy = get_loc_name(model, field)
            if not ctx['opts']['conai'] and field == 'conai_id':
                del vals[field]
                continue
            if (model == 'res.partner' and loc_name in RESET_FIELD and
                    vals[field].split('.') == 2):
                del vals[field]
        if not main_ext_id and vals.get('id'):
            main_ext_id = vals['id']
        if store:
            write_file_2_pull(ext_model, vals, wa)
            wa = 'a'
        if mode == 'upper' and 'description' in vals:
            vals['description'] = vals['description'].upper()
        if mode == 'wrong' and 'region' in vals:
            vals['region'] = '(TO)'
            if 'region_id' in vals:
                del vals['region_id']
        if test_pfx and vals.get('id'):
            ext_id = vals['id']
            if mode == 'only_amount':
                del vals['code']
            vals = jacket_vals(vals, test_pfx)
            rec_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
            store_id(ctx, model, rec_id, ext_id)
            if test_suppl == 'country_id':
                vals['country_id'] = ctx['res.country.IT']
            if model == 'product.product' and vals['vg7:code'] == 'AAA':
                vals['product_tmpl_id'] = ctx['product.product.A']
            elif model == 'product.product' and vals['vg7:code'] == 'BBB':
                vals['product_tmpl_id'] = ctx['product.product.B']
            general_check(ctx, model, rec_id, vals)
            if model == 'product.product':
                rec_id = clodoo.browseL8(ctx, model, rec_id).product_tmpl_id.id
                general_check(ctx, 'product.template', rec_id, vals)
    return main_ext_id

def reset_model(ctx, model, default, company_id=None,
                notranslate=None, test_pfx=None, delrecs=None):
    print('Reset model %s ...' % model)
    if model == 'res.partner':
        pdb.set_trace()
    ext_id = False
    if test_pfx:
        ext_name = '%s_id' % test_pfx.split(':')[0]
    for datas in default:
        vals = {}
        for field in datas:
            if datas[field] is None:
                continue
            if field == 'id' and not notranslate:
                if ext_name:
                    ext_id = datas[field]
                continue
            else:
                loc_name = field
            if not notranslate:
                loc_name, dummy = get_loc_name(model, field)
            if not ctx['opts']['conai'] and field == 'conai_id':
                loc_name = False
            elif (model == 'res.partner' and
                  loc_name in ('country_id', 'state_id',
                               'firstname', 'lastname', 'vat')):
                loc_name = False
            if loc_name:
                if loc_name in RESET_FIELD:
                    vals[loc_name] = False
                else:
                    vals[loc_name] = datas[field]
        if model == 'product.product' and vals['default_code'] == 'AAA':
            vals['product_tmpl_id'] = ctx['product.product.A']
        elif model == 'product.product' and vals['default_code'] == 'BBB':
            vals['product_tmpl_id'] = ctx['product.product.B']
        domain = ids = []
        if ext_id:
            domain = [(ext_name, '=', ext_id)]
            ids = clodoo.searchL8(ctx, model, domain)
        if not ids:
            for kk in CANDIDATE_KEYS:
                if kk in vals:
                    if kk in ('default_code', 'name'):
                        domain = [(kk, 'like', vals[kk])]
                    else:
                        domain = [(kk, '=', vals[kk])]
                    break
            if domain:
                if model == 'res.country.state':
                    domain.append(('country_id', '=', ctx['res.country.IT']))
        if domain:
            if company_id:
                domain.append(('company_id', '=', company_id))
        if domain:
            ids = clodoo.searchL8(ctx, model, domain)
        if ids:
            if len(ids) > 1:
                print('Warning: Too many records "%s.%s"' % (model, domain))
            clodoo.writeL8(ctx, model, ids, vals)
            if model == 'res.country' and vals['code'] == 'IT':
                ctx['res.country.IT'] = ids[0]
            elif (model == 'product.template' and
                  vals['default_code'].startswith('AA')):
                ctx['product.product.A'] = ids[0]
            elif (model == 'product.template' and
                  vals['default_code'].startswith('BB')):
                ctx['product.product.B'] = ids[0]
        else:
            print('Warning: No records found "%s.%s"' % (model, domain))
    ext_model = TNL_TABLE[model]
    rm_file_2_pull(ext_model)
    if delrecs:
        for item in delrecs:
            domain = []
            if isinstance(item, basestring):
                for kk in ('id', 'description', 'code'):
                    if kk in datas:
                        domain = [(kk, '=', item)]
                        break
            else:
                domain = [(ext_name, '=', item)]
            if domain:
                delete_record(
                    ctx, model, domain, company_id=company_id)
    unlink_vg7(model)

def init_test(ctx):
    print('This test requires following modules installed:')
    print('1. account, sale, stock, purchase, partner_bank')
    print('2. l10n_it_einvoice_out, l10n_it_ricevute_bancarie')
    print('3. l10n_it_ddt, l10n_it_fiscalcode, '
          'account_payment_term_extension')
    if ctx['opts']['conai']:
        print('4. connector_vg7, connector_vg7_conai')
    else:
        print('4. connector_vg7')
    print('Then')
    print('5. Partners & product of test environment (mk_test_env)')
    if ctx['opts']['ask']:
        input('Requirements are satisfied?')
    # Log level debug
    clodoo.executeL8(ctx,
        'ir.model.synchro.cache',
        'set_loglevel',
        0,
        'debug')
    # Reset cache
    clodoo.executeL8(ctx,
        'ir.model.synchro.cache',
        'clean_cache',
        0,
        None, None, 5)

    if ctx['opts']['conai']:
        MODULE_LIST.append('connector_vg7_conai')
    model = 'ir.module.module'
    if ctx['opts']['module']:
        for modname in MODULE_LIST:
            vals = {'name': modname}
            clodoo.executeL8(ctx,
                model,
                'synchro',
                vals)
        time.sleep(4)
    if not ctx['opts']['conai']:
        MODULE_LIST.append('connector_vg7_conai')
    for modname in MODULE_LIST:
        print('checking module %s ...' % modname)
        module_ids = clodoo.searchL8(ctx, model,
            [('name', '=', modname)])
        if modname == 'connector_vg7_conai' and not ctx['opts']['conai']:
            pass
        elif not module_ids:
            raise IOError('Module %s does not exist!!!' % modname)
        module = clodoo.browseL8(ctx, model, module_ids[0])
        if modname == 'connector_vg7_conai':
            if ctx['opts']['conai'] and module.state != 'installed':
                raise IOError('Module %s not installed!!!' % modname)
            elif not ctx['opts']['conai'] and module.state == 'installed':
                raise IOError(
                    'Module %s installed! Please use conai option' %
                    modname)
        elif module.state != 'installed':
            raise IOError('Module %s not installed!!!' % modname)

    if ctx['opts']['lang']:
        model = 'res.lang'
        vals = {'code': 'it_IT'}
        print('Installing language %s ...' % vals['code'])
        clodoo.executeL8(ctx,
            model,
            'synchro',
            vals)

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')

    print('Initializing environment ...')
    # Default company for current user
    clodoo.writeL8(
        ctx, 'res.users', ctx['user_id'], {'company_id': company_id})
    # Set message note
    ctx['company_note'] = 'Si prega di controllate i dati entro le 24h.'
    clodoo.writeL8(ctx, 'res.company', company_id,
                   {'sale_note': ctx['company_note']})
    # Configure VG7 channel
    # Wrong method. Will be set forward, in order to test cache
    model = 'synchro.channel'
    write_record(ctx, model, [], {
        'method': 'JSON',
        'exchange_path': os.path.expanduser('~/clodoo'),
        'trace': True,
    })
    for model, datas, notranslate, delrecs, company in (
            ('res.country', RES_COUNTRY, False, False, False),
            ('res.country.state', RES_COUNTRY_STATE, False, False, False),
            ('account.tax', ACCOUNT_TAX_DEFAULT, True, [101], company_id),
            ('account.payment.term', ACCOUNT_PAYMENT_TERM, False, [30, 3060],
             company_id),
            ('italy.conai.product.category', ACCOUNT_CONAI, False, False,
             False),
            ('product.template', PRODUCT_TEMPLATE, False, False, False),
            ('product.product', PRODUCT_PRODUCT, False, False, False),
            ('res.partner', RES_PARTNER, False, [7, 17], False),
    ):
        reset_model(ctx, model, datas, company_id=company,
            notranslate=notranslate, test_pfx='vg7:', delrecs=delrecs)

    # Delete file csv & unlink external ids
    records_to_delete = {}
    model = 'res.partner'
    ids = clodoo.searchL8(ctx, model, [('vg7_id', '=', 1001)])
    if ids:
        records_to_delete[model] = ids
    model = 'product.template'
    ids = clodoo.searchL8(ctx, model, [('vg7_id', '=', 3)])
    if ids:
        records_to_delete[model] = ids
    model = 'product.product'
    ids = clodoo.searchL8(ctx, model, [('vg7_id', '=', 3)])
    if ids:
        records_to_delete[model] = ids
    model = 'account.move'
    ids = clodoo.searchL8(ctx, model, [('oe8_id', '=', 201130)])
    if ids:
        records_to_delete[model] = ids

    # Delete invoice
    write_record(
        ctx, 'ir.sequence', [('prefix', 'like', 'INV/%range_year')], {
            'prefix': 'FAT/%(range_year)s/',
        })
    model = 'account.invoice'
    delete_record(
        ctx, model, [('number', '=', L_NUM_FATT2)],
        action=['move_name=', 'action_invoice_cancel'],
        company_id=company_id)
    delete_record(
        ctx, model, [('number', '=', L_NUM_FATT1)],
        action=['move_name=', 'action_invoice_cancel'],
        company_id=company_id)
    set_sequence(
        ctx, [('prefix', 'like', 'FAT/%range_year')], 1,
        company_id=company_id, multi=True)

    # Delete DdT
    if not ctx.get('_cr'):
        print('No sql support found!')
        if ctx['opts']['ask']:
            input('Press RET to continue')
    else:
        try:
            query = "delete from procurement_order"
            clodoo.exec_sql(ctx, query)
        except BaseException:
            pass
        try:
            query = "delete from stock_pack_operation"
            clodoo.exec_sql(ctx, query)
        except BaseException:
            pass
        try:
            query = "delete from stock_move"
            clodoo.exec_sql(ctx, query)
        except BaseException:
            pass
    model = 'stock.picking.package.preparation'
    delete_record(
        ctx, model, [('ddt_number', '=', X_NUM_DDT)],
        action=['action_cancel', 'set_draft'],
        company_id=company_id)

    # Delete sale order
    model = 'sale.order'
    delete_record(ctx, model, [('name', '=', '2187')],
        action='action_cancel')
    delete_record(
        ctx, model, [('name', '=', L_NUM_ORDER)], action='action_cancel')
    set_sequence(ctx, [('code', '=', 'sale.order')], 2)

    # Delete shipping address
    model = 'res.partner'
    delete_record(
        ctx, model, [('name', 'like', 'Partner A%'),
                     ('type', '=', 'contact')],
        multi=True, childs='child_ids')

    # Se partner (person) name
    model = 'res.partner'
    ctx['partner_MR_ids'] = write_record(
        ctx, model, [('name', 'like', 'Rossi')], {
            'splitmode': 'LF',
            'name': 'Rossi Mario',
            'company_id': company_id,
            'fiscalcode': 'RSSMRA69C02D612M',
        }, create=True, unique=True)
    delete_record(
        ctx, model, [('name', '=', 'La Romagnola srl'),
                     ('type', '=', 'contact')],
        childs='child_ids', multi=True)
    delete_record(
        ctx, model, [('fiscalcode', '=', 'RSSMRA60T45L219M')],
        childs='child_ids', multi=True)
    ids = write_record(ctx, model, [('name', 'like', 'Delta')], {
        'city': False,
        'state_id': False,
        'customer': False,
        'supplier': True,
    }, create=True, unique=True)
    write_record(ctx, model, 'base.res_partner_1', {
        'name': 'ASUSTek',
        'supplier': True,
        'customer': False,
        'country_id': env_ref(ctx, 'base.tw'),
        'company_id': company_id,
    })
    write_record(ctx, model, 'base.res_partner_2', {
        'name': 'Agrolait',
        'supplier': False,
        'customer': True,
        'country_id': env_ref(ctx, 'base.be'),
        'company_id': company_id,
    })
    write_record(ctx, model, 'base.res_partner_3', {
        'name': 'China Export',
        'supplier': True,
        'customer': False,
        'country_id': env_ref(ctx, 'base.cn'),
        'company_id': company_id,
    })
    write_record(ctx, model, 'base.res_partner_4', {
        'name': 'Delta PC',
        'supplier': False, 'customer': True,
        'country_id': env_ref(ctx, 'base.us'),
        'company_id': company_id,
    })

    # Productc (MISC)
    model = 'product.template'
    model2 = 'product.product'
    if ctx['opts']['conai']:
        conai_category_id = clodoo.searchL8(
            ctx, 'italy.conai.product.category', [('code', '=', 'L')])[0]
    for ii in range(28):
        if ii == 0:
            code = code2 = 'MISC'
        elif ii == 27:
            code = '__'
            code2 = '___'
        else:
            code = chr(ii - 1 + ord('A')) * 2
            code2 = code + code[0]
        xid = 'z0bug.product_template_%d' % ii
        vals = {
            'company_id': company_id,
            'vg7_id': False,
            'default_code': code,
        }
        if code == 'MISC':
            vals['vg7_id'] = 99
            vals['weight'] = 0.9
            if ctx['opts']['conai']:
                vals['conai_category_id'] = clodoo.searchL8(
                    ctx, 'italy.conai.product.category',
                    [('code', '=', 'PLA')])[0]
        elif code in ('AA', 'BB'):
            if ctx['opts']['conai']:
                vals['conai_category_id'] = conai_category_id
            vals['weight'] = 1.0
        ids = write_record(ctx, model, xid, vals, unique=True)
        if not ids:
            ids = write_record(
                ctx, model, [('default_code', '=', code)], vals,
                create=True, unique=True)
        if vals['vg7_id']:
            store_id(ctx, model, ids[0], vals['vg7_id'])
        vals['default_code'] = code2
        vals['product_tmpl_id'] = ids[0]
        # Default code was changed from XX to XXX so search for both codes
        xid = 'z0bug.product_product_%d' % ii
        ids = write_record(ctx, model2, xid, vals)
        if not ids:
            ids = write_record(
                ctx, model2, [('default_code', '=', code2)], vals,
                create=True, unique=True)
        if vals['vg7_id']:
            store_id(ctx, model2, ids[0], vals['vg7_id'])
            if code == 'MISC':
                ctx['test_product_x_id'] = ids[0]
        if ids:
            delete_record(
                ctx, model2, [('id', '!=', ids[0]), '|',
                              ('default_code', '=', code),
                              ('default_code', '=', code2)], multi=True)
    vals = {
        'name': 'Spese Bancarie',
        'default_code': 'SP-BANC',
        'type': 'service',
        'lst_price': 3.5,
        'property_account_income_id': clodoo.searchL8(
            ctx, 'account.account',
            [('code', '=', '512000'),
             ('company_id', '=', company_id)])[0],
        'taxes_id': [(6, 0, clodoo.searchL8(
            ctx, 'account.tax',
            [('description', '=', '22v'),
             ('company_id', '=', company_id)]))],
        'company_id': company_id,
        'vg7_id': False,
    }
    ids = write_record(
        ctx, model, [('default_code', '=', 'SP-BANC')], vals,
        create=True, unique=True)
    vals['product_tmpl_id'] = ids[0]
    product_id = write_record(
        ctx, model2, [('default_code', '=', 'SP-BANC')], vals,
        create=True, unique=True)[0]
    clodoo.writeL8(
        ctx, 'res.company',
        company_id,
        {
            'due_cost_service_id': product_id,
            # TODO: not found error
            'tax_stamp_product_id': env_ref(
                ctx,
                'l10n_it_einvoice_stamp.l10n_it_einvoice_stamp_2_euro')
        })
    # Journal
    model = 'account.journal'
    write_record(
        ctx, model, [], {'update_posted': True})


    # Delete other records
    model = 'res.country.state'
    delete_record(ctx, model, [('name', 'like', '(TO)')])
    model = 'stock.picking.goods_description'
    delete_record(ctx, model, [('name', '=', 'BANCALI')])
    model = 'crm.team'
    delete_record(ctx, model, [('name', '=', 'Sale Example Team')])
    model = 'ir.model.synchro.data'
    delete_record(ctx, model, [], multi=True)
    for item in records_to_delete.items():
        model = item[0]
        domain = [('id', 'in', item[1])]
        delete_record(ctx, model, domain)
    model = 'account.account'
    delete_record(ctx, model, [('code', '=', '180111')])
    channel_ids = clodoo.searchL8(
        ctx, 'synchro.channel', [('identity', '!=', 'odoo')])
    if channel_ids:
        model = 'synchro.channel.model'
        delete_record(
            ctx, model, [('synchro_channel_id', '!=', channel_ids[0])],
            multi=True)
    return ctx, company_id

def compare(ctx, rec_value, ext_value, mode):
    if mode == 'nounknown':
        return not rec_value.startswith('Unknown')
    elif mode == 'unknown':
        return rec_value.startswith('Unknown')
    elif mode == 'individual':
        return rec_value in ctx['partner_MR_ids']
    elif mode == 'nocase':
        return rec_value.lower() == ext_value.lower()
    elif rec_value or ext_value:
        return rec_value == ext_value
    return True

def general_check(ctx, model, id, vals):

    def get_loc_value(ext_ref, ext_name, loc_name, vals):
        mode = False
        if loc_name.endswith('_id'):
            try:
                loc_value = getattr(loc_rec, loc_name).id
            except BaseException:
                loc_value = getattr(loc_rec, loc_name)
            ckstr = False
            if loc_name in TABLE_OF_FIELD:
                ref_model = TABLE_OF_FIELD[loc_name]
                if TABLE_OF_FIELD[loc_name] in BORDERLINE_TABLE:
                    loc_value = BORDERLINE_TABLE[
                        ref_model]['LOC'].get(loc_value,
                        loc_value)
                ckstr = True
            elif loc_name == 'parent_id':
                if model in BORDERLINE_TABLE:
                    loc_value = BORDERLINE_TABLE[
                        model]['LOC'].get(loc_value, loc_value)
                ckstr = True
            if ckstr and isinstance(vals[ext_ref], basestring):
                ids = clodoo.searchL8(
                    ctx, ref_model,
                    [('name', 'ilike', vals[ext_ref])],
                    context={'lang': 'it_IT'})
                if not ids:
                    ids = clodoo.searchL8(
                        ctx, ref_model,
                        [('name', 'ilike', vals[ext_ref])])
                if len(ids) >= 1:
                    if len(ids) >= 1:
                        print('Warning: '
                              'multiple records %s.%s detected' % (
                                  ref_model, vals[ext_ref]))
                    if ref_model in BORDERLINE_TABLE:
                        vals[ext_ref] = BORDERLINE_TABLE[
                            ref_model]['LOC'].get(ids[0],
                            ids[0])
                    else:
                        vals[ext_ref] = ids[0]
        else:
            loc_value = getattr(loc_rec, loc_name)
            if isinstance(loc_value, datetime):
                if ext_ref in ('vg7:data_emissione',
                               'vg7:data_ritiro'):
                    loc_value = datetime.strftime(
                        loc_value, '%Y-%m-%d')
                else:
                    loc_value = datetime.strftime(
                        loc_value, '%Y-%m-%d %H:%M:%S')
            elif isinstance(loc_value, date):
                loc_value = datetime.strftime(
                    loc_value, '%Y-%m-%d')
            elif model == 'product.uom' and loc_value == 'Unità':
                loc_value = 'Unit(s)'
            elif (model == 'account.invoice' and loc_name == 'number' and
                  loc_rec.state != 'draft'):
                mode = 'nounknown'
        return loc_value, mode

    def get_ext_value(ext_ref, ext_name, loc_name, vals):
        mode = False
        if (ext_ref in ('vg7:id', 'vg7_id', 'oe8:id', 'oe8_id') and
                (isinstance(vals[ext_ref], basestring) and
                 vals[ext_ref].isdigit())):
            ext_value = eval(vals[ext_ref])
        elif loc_name == 'company_id':
            ext_value = env_ref(ctx, 'z0bug.mycompany')
        elif (loc_name.endswith('_id') and
                isinstance(vals[ext_ref], basestring) and
                vals[ext_ref].isdigit()):
            ext_value = eval(vals[ext_ref])
        elif loc_name == 'street' and ext_ref.startswith('vg7:'):
            ext_value = '%s, %s' % (
                vals[ext_ref], vals.get('vg7:street_number', ''))
        elif ext_ref == 'state':
            ext_value = 'draft'
        elif loc_name == 'vat' and ext_ref.startswith('vg7:'):
            ext_value = 'IT%s' % vals[ext_ref]
        else:
            ext_value = vals[ext_ref]
        if (model == 'res.partner' and ext_ref == 'vg7:name' and
                vals.get('vg7_id') == 17):
            mode = 'individual'
        return ext_value, mode

    if not id or id < 1:
        raise IOError('!!Syncro %s Failed (%d)!' % (model, id))
    loc_rec = clodoo.browseL8(ctx, model, id)

    for ext_ref in vals:
        if ext_ref in (
                'vg7:date_scadenza', 'vg7:shipping', 'vg7:billing',
                'vg7:surename', 'vg7:name', 'id', 'vg7:street_number'):
            continue
        loc_name = ext_name = ext_ref
        if ext_ref in ('vg7:id', 'oe8:id'):
            loc_name = ext_ref.replace(':', '_')
            ext_name = 'id'
        elif (ext_ref.startswith('vg7:') or
              ext_ref.startswith('oe8:')):
            ext_name = ext_ref[4:]
            loc_name, dummy = get_loc_name(model, ext_ref)
            if loc_name == ext_ref:
                loc_name, dummy = get_loc_name(model, ext_name)
        if not loc_name:
            continue
        if isinstance(loc_name, (tuple, list)):
            mode = loc_name[1]
            loc_name = loc_name[0]
        else:
            mode = False

        loc_value, mode2 = get_loc_value(ext_ref, ext_name, loc_name, vals)
        mode = mode or mode2
        ext_value, mode2 = get_ext_value(ext_ref, ext_name, loc_name, vals)
        mode = mode or mode2

        if vals[ext_ref] == '' and not mode:
            continue
        if not compare(ctx, loc_value, ext_value, mode):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s> # %s' % (
                    model, id, loc_name, loc_value, ext_value, mode))
        ctx['ctr'] += 1
        if mode == 'individual':
            if not compare(ctx, loc_rec.name, 'Rossi Mario', False):
                raise IOError(
                    '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                        model, id, loc_name, loc_value, ext_value))
            ctx['ctr'] += 1
            if not compare(ctx, loc_rec.individual, True, False):
                raise IOError(
                    '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                        model, id, loc_name, loc_value, ext_value))
            ctx['ctr'] += 1
    if model == 'res.partner' and loc_rec.type == 'contact':
        if not compare(ctx, loc_rec.is_company, True, False):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                    model, id, loc_name, loc_value, ext_value))
        ctx['ctr'] += 1
    if model == 'res.partner' and loc_rec.type != 'contact':
        if not compare(ctx, loc_rec.is_company, False, False):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                    model, id, loc_name, loc_value, ext_value))
        ctx['ctr'] += 1

def test_synchro_vg7(ctx):
    print('Test synchronization VG7 module')
    if ctx['param_1'] == 'help':
        print('test_synchro_vg7 [--[no-]conai] [--[no-]ask] [--[no-]-module]')
        return
    ctx['opts'] = {
        'conai': True,
        'ask': True,
        'module': True,
        'lang': True,
    }
    for opt_param in ('param_1', 'param_2', 'param_3', 'param_4', 'param_5'):
        if not ctx[opt_param]:
            continue
        for param in ('conai', 'ask', 'module', 'lang'):
            if ctx[opt_param].find('--%s' % param) >= 0:
                ctx['opts'][param] = True
            elif ctx[opt_param].find('--no-%s' % param) >= 0:
                ctx['opts'][param] = False
    ctx['ctr'] = 0

    def write_country(ctx, mode=None):
        model = 'res.country'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, RES_COUNTRY,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['res.country.IT'] = vg7_id

        model = 'res.country.state'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, RES_COUNTRY_STATE,
            mode=mode, store=not mode, test_pfx='vg7:',
            test_suppl='country_id')
        ctx['res.country.state.MI'] = vg7_id

    def write_tax(ctx, mode=None):
        model = 'account.tax'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, ACCOUNT_TAX,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['account.tax.22v'] = vg7_id

    def write_payment(ctx, mode=None):
        model = 'account.payment.term'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, ACCOUNT_PAYMENT_TERM,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['account.payment.term.30GG'] = vg7_id

    def write_conai(ctx, mode=None):
        model = 'italy.conai.product.category'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, ACCOUNT_CONAI,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['italy.conai.product.category.CA'] = vg7_id

    def write_product(ctx, mode=None):
        model = 'product.product'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, PRODUCT_TEMPLATE,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['product.product.A'] = vg7_id

    def write_partner(ctx, mode=None):
        model = 'res.partner'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, RES_PARTNER,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['res.partner.A'] = vg7_id

    def prepare_vals(ctx, model, partner_id, rectype, name, vg7_id, vg7_id2,
                     vals_shipping, vals_billing, wrong_data):
        if rectype == 'delivery':
            rec_vg7_id = vg7_id2 + 100000000
            rec_vals = vals_shipping
            rec_vals['vg7_id'] = rec_vals['customer_shipping_id']
            del rec_vals['customer_shipping_id']
        elif rectype == 'invoice':
            rec_vg7_id = vg7_id + 200000000
            rec_vals = vals_billing
            if 'billing_payment_id' in rec_vals:
                rec_vals['property_payment_term_id'] = rec_vals[
                    'billing_payment_id']
                del rec_vals['billing_payment_id']
        ids = clodoo.searchL8(ctx, model,
                              [('parent_id', '=', partner_id),
                               ('vg7_id', '=', rec_vg7_id)])
        if ((not wrong_data and rectype == 'invoice' and len(ids)) or
                ((wrong_data or rectype != 'invoice') and len(ids) != 1)):
            raise IOError(
                '!!Syncro %s: wrong # of childs!' % model)
        ctx['ctr'] += 1
        if ids:
            rec_id = ids[0]
        else:
            rec_id = False
        for nm in rec_vals.copy():
            new_name = nm.replace(
                'shipping_', 'vg7:').replace('billing_', 'vg7:')
            if new_name != name:
                rec_vals[new_name] = rec_vals[nm]
                del rec_vals[nm]
        for nm in ('vg7:piva', 'vg7:cf', 'vg7:name'):
            if nm in rec_vals:
                del rec_vals[nm]
        rec_vals['name'] = name
        rec_vals['vg7_id'] = rec_vg7_id
        return rec_id, rec_vals

    def write_partner_pull(ctx, company_id, vg7_id=None, name=None,
                           wrong_data=None):
        model = 'res.partner'
        print('Write %s (full pull) ...' % model)
        vg7_id = vg7_id or 7
        if vg7_id == 7:
            name = name or 'Partner A'
            vals_shipping = {
                'customer_shipping_id': 107,
                'customer_id': 7,
                'id': 16789,
                'shipping_country_id': 39,
                'shipping_name': ' ',
                'shipping_postal_code': '35100',
                'shipping_city': 'Padova',
                'shipping_piva': '00385870480'
            }
            vals_billing = {
                'billing_country_id': 39,
                'billing_company': name,
                'billing_name': ' ',
                'billing_street': 'Via Porta Nuova',
                'billing_street_number': '13',
                'billing_postal_code': '10121',
                'billing_city': 'Torino',
                'billing_piva': '00385870480',
                'billing_codice_univoco': 'ABC1234',
                'billing_esonerato_fe': False,
                'billing_payment_id': 3060,
            }
            vals = {
                'vg7:id': vg7_id,
                'vg7:shipping': vals_shipping,
                'vg7:billing': vals_billing,
            }
            if wrong_data:
                vals['vg7:street'] = 'Via Porta Vecchia'
        if vg7_id == 2:
            name = clodoo.browseL8(
                ctx, model, env_ref(ctx, 'z0bug.res_partner_2')).name
            vals_shipping = {
                'shipping_country_id': 39,
                'shipping_name': ' ',
                'shipping_postal_code': '10061',
                'shipping_city': 'S. Secondo fraz. Pinasca',
            }
            vals_billing = {
                'billing_country_id': 39,
                'billing_name': ' ',
                'postal_code': '10135',
                'city': 'Torino',
            }
            vals = {
                # 'company_id': company_id,
                'vg7_id': vg7_id,
                'vg7:company': name,
                'vg7:shipping': vals_shipping,
                'vg7:billing': vals_billing,
            }
        partner_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, partner_id, vg7_id)
        # All field but not street!
        for nm in ('country_id', 'company', 'name',
                   'street_number', 'postal_code', 'city', 'piva',
                   'codice_univoco', 'esonerato_fe'):
            vals['vg7:%s' % nm] = vals_billing['billing_%s' % nm]
        # check_partner(ctx, partner_id, vals)

        for rectype in ('delivery', 'invoice'):
            rec_id, rec_vals = prepare_vals(
                ctx, model, partner_id, rectype, name, vg7_id, 107,
                vals_shipping, vals_billing, wrong_data)
            # if rec_id:
            #    # check_partner(ctx, rec_id, rec_vals)
        return vg7_id

    def write_partner_shipping(ctx, company_id, vg7_id=None, name=None,
                      wrong_data=None):
        model = 'res.partner'
        print('Write %s (shipping)..' % model)
        vg7_id = vg7_id or 107
        name = name or 'Partner AA'
        vals = {
            'vg7:customer_shipping_id': vg7_id,
            'vg7:customer_id': 7,
            'vg7:shipping_country_id': 39,
            'vg7:shipping_company': name,
            'vg7:shipping_street': 'Via della Porta Vecchia',
            'vg7:shipping_street_number': '13',
            'vg7:shipping_postal_code': '35100',
            'vg7:shipping_city': 'Padova',
        }
        shipping_id = clodoo.executeL8(ctx,
                                      '%s.shipping' %model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, shipping_id, vg7_id)
        vals['vg7_id'] = vals['vg7:customer_shipping_id'] + 100000000
        del vals['vg7:customer_shipping_id']
        for nm in vals.copy():
            new_name = nm.replace('shipping_', '')
            if new_name != nm:
                vals[new_name] = vals[nm]
                del vals[nm]
        # check_partner(ctx, shipping_id, vals)
        return vg7_id

    def write_partner_supplier(ctx, company_id, vg7_id=None, name=None,
                      wrong_data=None):
        model = 'res.partner'
        print('Write %s (supplier)..' % model)
        vg7_id = 14
        vals = {
            'vg7:id': vg7_id,
            'vg7:company': 'Delta 4 s.r.l.',
            'vg7:postal_code': '20864',
            'vg7:street': 'Via Sofocle',
            'vg7:street_number': '13',
            'vg7:city': 'Milano',
            'vg7:region': 'MILANO',
            'vg7:region_id': 2,
            'vg7:tax_code_id': 0,
            'vg7:bank_id': 372,
            'vg7:piva': '00723670964',
            'vg7:cf': '01781920150',
            'vg7:country_id': 39,
            # 'supplier': True,
            'vg7:telephone': '0396898792-6210086',
        }
        supplier_id = clodoo.executeL8(ctx,
                                      '%s.supplier' %model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, supplier_id, vg7_id)
        vals['vg72_id'] = vals['vg7:id']
        del vals['vg7:id']
        # check_partner(ctx, supplier_id, vals)
        return supplier_id

    def check_uom(ctx, uom_id, vals):
        general_check(ctx, 'product.uom', uom_id, vals)

    def write_uom(ctx, vg7_id=None, code=None, name=None):
        model = 'product.uom'
        print('Write %s ...' % model)

        vg7_id = vg7_id or 13
        name = name or 'Unit(s)'
        vals = {
            'vg7:id': vg7_id,
            'vg7:code': name,
        }
        uom_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, uom_id, vg7_id)
        check_uom(ctx, uom_id, vals)
        return vg7_id

    def check_transport_reason(ctx, causal_id, vals):
        general_check(ctx, 'stock.picking.transportation_reason', causal_id, vals)

    def write_transport_reason(ctx, vg7_id=None, code=None, name=None):
        model = 'stock.picking.transportation_reason'
        print('Write %s ...' % model)

        vg7_id = vg7_id or 3
        name = name or 'Vendita'
        vals = {
            'vg7:id': vg7_id,
            'vg7:description': name,
        }
        causal_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, causal_id, vg7_id)
        check_transport_reason(ctx, causal_id, vals)
        return vg7_id

    def check_sale_order(ctx, order_id, vals, state=None, note=None):
        general_check(ctx, 'sale.order', order_id, vals)
        order = clodoo.browseL8(ctx, 'sale.order', order_id)
        if state:
            if order.state != state:
                raise IOError('!!Invalid state of order %d!' % order_id)
            ctx['ctr'] += 1
        if order.partner_id.id == env_ref(ctx, 'z0bug.res_partner_2'):
            if order.goods_description_id.id != env_ref(
                    ctx, 'l10n_it_ddt.goods_description_SFU'):
                raise IOError('!!Invalid good des. order %d!' % order_id)
            ctx['ctr'] += 1
            if order.carriage_condition_id.id != env_ref(
                    ctx, 'l10n_it_ddt.carriage_condition_PAF'):
                raise IOError('!!Invalid carriage cond. order %d!' % order_id)
            ctx['ctr'] += 1
            if order.transportation_method_id.id != env_ref(
                    ctx, 'l10n_it_ddt.transportation_method_COR'):
                raise IOError('!!Invalid trans. meth. order %d!' % order_id)
            ctx['ctr'] += 1
        if note and order.note != note:
            raise IOError('!!Invalid order %d note!' % order_id)
        ctx['ctr'] += 1

    def check_sale_order_line(ctx, line_id, vals):
        general_check(ctx, 'sale.order.line', line_id, vals)

    def write_sale_order(ctx, company_id, partner_id=None, vg7_order_id=None,
                         state=None, note=None, newprod=None, new_prot=None):
        model = 'sale.order'
        print('Write %s ...' % model)

        partner_id = partner_id or env_ref(ctx, 'z0bug.res_partner_2')
        vg7_id = vg7_order_id or 1
        if new_prot:
            vals = {
                'vg7:id': vg7_id,
                'vg7:customer_id': get_vg7id_from_id(
                    ctx, 'res.partner', partner_id),
                'shipping': {
                    "customer_shipping_id": 1001,
                },
            }
            if not newprod:
                vals['vg7:customer_shipping_id'] = 1001
        else:
            vals = {
                'vg7_id': vg7_id,
                'vg7_partner_id': get_vg7id_from_id(
                    ctx, 'res.partner', partner_id)
            }
        if state:
            vals['state'] = state
        if newprod:
            id = get_id_from_vg7id(ctx, model, vg7_id)
            clodoo.writeL8(ctx, model, id, {'vg7_id': False})
        # Search for sale order if connector uninstalled
        ids = clodoo.searchL8(ctx, model,
                              [('name', '=', L_NUM_ORDER),
                               '|', ('vg7_id', '=', False),
                                    ('vg7_id', '=', 0)])
        if ids:
            vals['name'] = L_NUM_ORDER
            if not state:
                vals['state'] = 'draft'
        order_id = clodoo.executeL8(ctx,
                                    model,
                                    'synchro',
                                    vals)
        if ids:
            if order_id != ids[0]:
                raise IOError(
                    '!!Duplicate document: %d -> %d!' % (ids[0], order_id))
            ctx['ctr'] += 1
        store_id(ctx, model, order_id, vg7_id)
        check_sale_order(ctx, order_id, vals, state='draft', note=note)

        model = 'sale.order.line'
        print('Write %s ...' % model)
        vg7_order_id = vg7_id
        vg7_id = vg7_order_id * 100
        vals = {
            'vg7_id': vg7_id,
            'vg7_order_id': vg7_order_id,
            'vg7_partner_id': get_vg7id_from_id(ctx, 'res.partner', partner_id),
            'name': 'Product Alpha',
            'vg7_product_id': ctx['vg7_id_product_a'],
            'price_unit': 10.50,
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_sale_order_line(ctx, line_id, vals)

        print('Write %s ...' % model)
        vg7_id = vg7_order_id * 100 + 1
        # Field partner_id does not exit: test to avoid crash
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_order_id': vg7_order_id,
            'vg7_partner_id': get_vg7id_from_id(ctx, 'res.partner', partner_id),
            'name': 'Product Beta',
            'vg7_product_id': ctx['vg7_id_product_b'],
            'price_unit': 25.50,
            'tax_id': '22v',
        }
        if state == 'sale':
            vals['tax_id'] = '4v'
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_sale_order_line(ctx, line_id, vals)

        if not state or state == 'draft' or newprod:
            print('Write %s ...' % model)
            vg7_id = vg7_order_id * 100 + 2
            vals = {
                'vg7_id': vg7_id,
                'vg7_order_id': vg7_order_id,
                'vg7_partner_id': get_vg7id_from_id(ctx, 'res.partner',
                                                    partner_id),
                'name': 'Product MISC',
                'vg7_product_id': get_vg7id_from_id(
                    ctx, 'product.product', ctx['test_product_x_id']),
                'price_unit': 12.34,
                'tax_id': '4v',
            }
            if newprod:
                vals['vg7_product_id'] = 3
                vals['name'] = 'New product CC'
            line_id = clodoo.executeL8(ctx,
                                       model,
                                       'synchro',
                                       vals)
            store_id(ctx, model, line_id, vg7_id)
            if newprod:
                id = get_id_from_vg7id(ctx, 'product.product', 3)
                store_id(ctx, 'product.product', id, 3)
            check_sale_order_line(ctx, line_id, vals)

        if newprod:
            # Test for cache: reset cache before commit
            clodoo.executeL8(ctx,
                             'ir.model.synchro.cache',
                             'clean_cache',
                             0,
                             None, None, 5)
        id = clodoo.executeL8(ctx,
                              'sale.order',
                              'commit',
                              order_id)
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)
        ctx['ctr'] += 1
        rec = clodoo.browseL8(ctx, 'sale.order', order_id)
        if state and not newprod:
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
            ctx['ctr'] += 1
            if len(rec['order_line']) != 2:
                raise IOError('!!Invalid # of details!')
            ctx['ctr'] += 1
        else:
            if len(rec['order_line']) != 3:
                raise IOError('!!Invalid # of details!')
            ctx['ctr'] += 1
        if state == 'sale':
            check_sale_order_line(ctx, line_id, {
                'vg7_order_id': vg7_order_id, 'tax_id': '4v'})
        if rec.payment_term_id != rec.partner_id.property_payment_term_id:
            raise IOError('!!Invalid payment term!')
        ctx['ctr'] += 1
        return vg7_id

    def check_invoice(ctx, invoice_id, vals):
        general_check(ctx, 'account.invoice', invoice_id, vals)

    def check_invoice_line(ctx, line_id, vals):
        general_check(ctx, 'account.invoice.line', line_id, vals)

    def write_invoice(ctx, company_id, partner_id=None,
                      vg7_invoice_id=None, state=None):
        model = 'account.invoice'
        print('Write %s ...' % model)

        partner_id = partner_id or ctx[
            'odoo_session'].env.ref('z0bug.res_partner_2').id
        vg7_id = vg7_invoice_id or 5
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'partner_id': partner_id,
        }
        if state:
            vals['state'] = state
        # Search for account invoice if connector uninstalled
        ids = clodoo.searchL8(ctx, model,
                              [('number', '=', L_NUM_FATT1)])
        if ids:
            vals['number'] = L_NUM_FATT1
            if not state:
                vals['state'] = 'draft'
        invoice_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, invoice_id, vg7_id)
        check_invoice(ctx, invoice_id, vals)

        model = 'account.invoice.line'
        print('Write %s ...' % model)
        vg7_invoice_id = vg7_id
        vg7_id = vg7_invoice_id * 200
        vals = {
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product Alpha',
            'vg7_product_id': ctx['vg7_id_product_a'],
            'price_unit': 10.50,
        }
        # if ctx['opts']['conai']:
        #     vals['vg7:conai_id'] = 1
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_invoice_line(ctx, line_id, vals)

        print('Write %s ...' % model)
        vg7_id = vg7_invoice_id * 200 + 1
        # Field partner_id does not exit: test to avoid crash
        vals = {
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product Beta',
            'vg7_product_id': ctx['vg7_id_product_b'],
            'price_unit': 25.50,
            'invoice_line_tax_ids': '22v',
        }
        # if ctx['opts']['conai']:
        #    vals['vg7:conai_id'] = 1
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_invoice_line(ctx, line_id, vals)

        if not state or state == 'draft':
            print('Write %s ...' % model)
            vg7_id = vg7_invoice_id * 200 + 2
            vals = {
                'vg7_id': vg7_id,
                'vg7_invoice_id': vg7_invoice_id,
                'partner_id': partner_id,
                'name': 'Product MISC',
                'vg7_product_id': get_vg7id_from_id(
                    ctx, 'product.product', ctx['test_product_x_id']),
                'price_unit': 12.34,
                'invoice_line_tax_ids': '22v',
            }
            line_id = clodoo.executeL8(ctx,
                                       model,
                                       'synchro',
                                       vals)
            store_id(ctx, model, line_id, vg7_id)
            check_invoice_line(ctx, line_id, vals)

        id = clodoo.executeL8(ctx,
                              'account.invoice',
                              'commit',
                              invoice_id)
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)
        ctx['ctr'] += 1
        rec = clodoo.browseL8(ctx, 'account.invoice', invoice_id)
        if state:
            detail_ctr = 2
            if rec.payment_term_id.riba:
                detail_ctr += 1
            if ctx['opts']['conai']:
                detail_ctr += 1
        else:
            detail_ctr = 3
        if state:
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
            ctx['ctr'] += 1
        if len(rec['invoice_line_ids']) != detail_ctr:
            raise IOError('!!Invalid # of details (expected %d)!' % detail_ctr)
        ctx['ctr'] += 1
        if rec.payment_term_id != rec.partner_id.property_payment_term_id:
            raise IOError('!!Invalid payment term (default value)!')
        ctx['ctr'] += 1
        return vg7_id

    def check_ddt(ctx, ddt_id, vals):
        general_check(ctx, 'stock.picking.package.preparation', ddt_id, vals)

    def check_ddt_line(ctx, ddt_line_id, vals):
        general_check(ctx, 'stock.picking.package.preparation.line',
                      ddt_line_id, vals)

    def write_ddt(ctx, company_id, partner_id=None,
                  vg7_id=None, state=None, shipping_id=None):
        model = 'stock.picking.package.preparation'
        print('Write %s ...' % model)
        partner_id = partner_id or 7
        vg7_id = vg7_id or 17
        vals = {
            'vg7_id': vg7_id,
            'vg7:ddt_number': X_NUM_DDT,
            'vg7:numero_colli': 1,
            'vg7:customer_id': partner_id,
            'vg7:vettori_prima_riga': '',
            'vg7:voce_doganale': '',
            'vg7:aspetto_esteriore_dei_beni': 'BANCALI',
            'vg7:causal_id': 3,
            'vg7:vettori_seconda_riga': '',
            'vg7:note': '',
            'vg7:peso_netto': 9.0,
            'vg7:tipo_porto': 'FRANCO',
            'vg7:peso_lordo': 10.0,
            'vg7:ora_ritiro': '18:30:00',
            'vg7:data_emissione': '2020-04-30',
            'vg7:data_ritiro': '2020-04-30',
            'vg7:mezzo': u'MITTENTE'
        }
        if state:
            vals['state'] = state
        if shipping_id:
            vals['vg7:customer_shipping_id'] = shipping_id
        ddt_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, ddt_id, vg7_id)
        if not shipping_id:
            vals['vg7:customer_shipping_id'] = partner_id
        else:
            store_id(ctx,
                     'res.partner',
                     get_id_from_vg7id(
                         ctx, 'res.partner', shipping_id + 100000000),
                     shipping_id)
        check_ddt(ctx, ddt_id, vals)

        sale_id = False
        sale_line_id = False
        ids = clodoo.searchL8(ctx, 'sale.order',
                              [('name', '=', L_NUM_ORDER)])
        if ids:
            sale_id = get_vg7id_from_id(ctx, 'sale.order', ids[0])
            store_id(ctx, 'sale.order', ids[0], sale_id)
            ids = clodoo.searchL8(ctx, 'sale.order.line',
                              [('order_id', '=', ids[0])])
            sale_line_id = get_vg7id_from_id(ctx, 'sale.order.line', ids[0])
            store_id(ctx, 'sale.order.line', ids[0], sale_line_id)
        model = 'stock.picking.package.preparation.line'
        print('Write %s ...' % model)
        vg7_ddt_id = vg7_id
        vg7_id = vg7_ddt_id * 300
        vals = {
            'vg7_id': vg7_id,
            'vg7:ddt_id': vg7_ddt_id,
            'vg7:descrizione': 'Product Alpha',
            'vg7:product_id': ctx['vg7_id_product_a'],
            'vg7:prezzo_unitario': 10.50,
            'vg7:quantita': 2,
            'vg7:tax_code_id': 22,
            'vg7:tax_id': u'22v',
            'vg7:peso': 1.5,
            'vg7:um': 'N',
            'vg7:um_id': get_vg7id_from_id(
                ctx, 'product.uom', env_ref(ctx, 'product.product_uom_unit')),
        }
        if sale_line_id:
            vals['vg7:order_id'] = sale_id
            vals['vg7:order_row_id'] = sale_line_id
        if ctx['opts']['conai']:
            vals['vg7:conai_id'] = 1
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_ddt_line(ctx, line_id, vals)

        id = clodoo.executeL8(ctx,
                              'stock.picking.package.preparation',
                              'commit',
                              ddt_id)
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)
        ctx['ctr'] += 1

    def check_4_translation(ctx, model, name10, name8):
        print('Checking translation %s.%s -> %s ...' % (model, name10, name8))
        sync_model = 'synchro.channel'
        channel_ids = clodoo.searchL8(
            ctx, sync_model, [('identity', '=', 'odoo'),
                              ('prefix', '=', 'oe8')])
        if len(channel_ids) != 1:
            raise IOError('No odoo 8.0 channel found!')
        sync_model = 'synchro.channel.model'
        model_ids = clodoo.searchL8(
            ctx, sync_model, [('synchro_channel_id', '=', channel_ids[0]),
                              ('name', '=', model)])
        if len(model_ids) != 1:
            raise IOError('No odoo model %s 8.0 found!' % model)
        sync_model = 'synchro.channel.model.fields'
        fld_ids = clodoo.searchL8(
            ctx, sync_model, [('model_id', '=', model_ids[0]),
                              ('name', '=', name10)])
        if len(fld_ids) != 1:
            raise IOError('No odoo field model %s 8.0 found!' % name10)
        rec = clodoo.browseL8(ctx, sync_model, fld_ids[0])
        if rec.counterpart_name != name8:
            raise IOError('Invalid translation %s: expected %s found %s!' % (
                name10, name8, rec.counterpart_name))
        ctx['ctr'] += 1

    def check_2_user(ctx, user_id, vals):
        general_check(ctx, 'res.users', user_id, vals)

    def write_2_user(ctx, oe8_id=None, login=None, name=None):
        model = 'res.users'
        print('Write %s ...' % model)

        oe8_id = oe8_id or 1
        login = login or 'zeroadm'
        name = name or 'Administrator'
        vals = {
            'oe8:id': oe8_id,
            'oe8:login': login,
            'oe8:name': name,
        }
        user_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, user_id, oe8_id)
        check_2_user(ctx, user_id, vals)
        return oe8_id

    def check_2_company(ctx, company_id, vals):
        general_check(ctx, 'res.company', company_id, vals)

    def write_2_company(ctx, oe8_id=None, partner_id=None):
        model = 'res.company'
        print('Write %s ...' % model)

        oe8_id = oe8_id or 1
        partner_id = partner_id or env_ref(ctx, 'z0bug.partner_mycompany')
        clodoo.writeL8(ctx, 'res.partner', partner_id, {'oe8_id': 1001})
        name = clodoo.browseL8(ctx, 'res.partner', partner_id).name
        vals = {
            'oe8:id': oe8_id,
            'oe8:name': name,
            'oe8:vat': 'IT10978280013',
        }
        company_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, company_id, oe8_id)
        check_2_company(ctx, company_id, vals)
        return oe8_id

    def check_2_account_type(ctx, company_id, vals):
        general_check(ctx, 'account.account.type', company_id, vals)


    def write_2_account_type(ctx, oe8_id=None, code=None, name=None,
                             utype=None, utype_new=None, uid_new=None):
        model = 'account.account.type'
        print('Write %s ...' % model)

        oe8_id = oe8_id or 1
        code = code or 'bank'
        name = name or 'Bank and Cash'
        utype = utype or 'liquidity'
        utype_new = utype_new or 'liquidity'
        vals = {
            'oe8:id': oe8_id,
            'oe8:code': code,
            'oe8:name': name,
            'oe8:report_type': utype,
        }
        acc_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        if uid_new:
            if uid_new != env_ref(ctx, uid_new):
                raise IOError('!!Invalid record id of account.type!')
        store_id(ctx, model, acc_id, oe8_id)
        vals['type'] = utype_new
        del vals['oe8:report_type']
        del vals['oe8:code']
        check_2_account_type(ctx, acc_id, vals)
        return oe8_id

    def check_2_account(ctx, company_id, vals):
        general_check(ctx, 'account.account', company_id, vals)

    def write_2_account(ctx, company_id, oe8_id=None, code=None,
                        name=None, utype=None, type_xref=None):
        model = 'account.account'
        print('Write %s ...' % model)

        oe8_id = oe8_id or 567
        code = code or '180111'
        name = name or 'Bank'
        utype = utype or 'liquidity'
        type_xref = type_xref or 'account.data_account_type_liquidity'
        vals = {
            'oe8:id': oe8_id,
            'oe8:company_id': 1,
            'oe8:code': code,
            'oe8:name': name,
            'oe8:type': utype,
            'oe8:user_type': {
                'account.data_account_type_liquidity': 1,
                'account.data_account_type_receivable': 2,
            }[type_xref],
        }
        acc_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, acc_id, oe8_id)
        store_id(ctx, 'res.company', company_id, 1)
        vals['internal_type'] = utype
        vals['user_type_id'] = env_ref(ctx, type_xref)
        del vals['oe8:type']
        del vals['oe8:user_type']
        check_2_account(ctx, acc_id, vals)
        return oe8_id

    def check_2_tax(ctx, tax_id, vals):
        general_check(ctx, 'account.tax', tax_id, vals)

    def write_2_tax(ctx, oe8_id=None, code=None, name=None, utype=None):
        model = 'account.tax'
        print('Write %s ...' % model)
        oe8_id = oe8_id or 101
        code = code or 'a101'
        name = name or 'Forfettario art 101'
        utype = utype or 'all'
        vals = {
            'oe8:id': oe8_id,
            'oe8:description': code,
            'oe8:name': name,
            'oe8:type': utype,
            'oe8:company_id': 1,
        }
        tax_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, tax_id, oe8_id)
        vals['type_tax_use'] = 'purchase'
        del vals['oe8:type']
        check_2_tax(ctx, tax_id, vals)
        return oe8_id

    def check_2_currency(ctx, ccy_id, vals):
        general_check(ctx, 'res.currency', ccy_id, vals)

    def write_2_currency(ctx, oe8_id=None, code=None, name=None):
        model = 'res.currency'
        print('Write %s ...' % model)
        oe8_id = oe8_id or 13
        name = name or 'EUR'
        vals = {
            'oe8:id': oe8_id,
            'oe8:name': name,
        }
        ccy_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, ccy_id, oe8_id)
        store_id(ctx, 'res.currency', ccy_id, oe8_id)
        check_2_currency(ctx, ccy_id, vals)
        return ccy_id

    def check_2_partner(ctx, partner_id, vals):
        general_check(ctx, 'res.partner', partner_id, vals)

    def write_2_partner(ctx, oe8_id=None, name=None, wrong_data=None):
        model = 'res.partner'
        print('Write %s ...' % model)
        oe8_id = oe8_id or 807
        name = name or 'Partner A'
        vals = {
            'oe8:id': oe8_id,
            'oe8:name': name,
            'oe8:street': 'Via della Porta Nuova, 813',
            'oe8:zip': '10128',
            'oe8:city': 'Torino',
            'country_id': env_ref(ctx, 'base.it'),
            'oe8:is_company': True,
            'oe8:vat': 'IT00385870480',
        }
        partner_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, partner_id, oe8_id)
        # check_partner(ctx, partner_id, vals)
        return oe8_id

    def check_2_account_journal(ctx, journal_id, vals):
        general_check(ctx, 'account.journal', journal_id, vals)

    def write_2_account_journal(ctx, oe8_id=None, name=None):
        model = 'account.journal'
        print('Write %s ...' % model)
        oe8_id = oe8_id or 5
        name = name or 'Operazioni varie'
        vals = {
            'id': oe8_id,
            'name': name,
            'company_id': 1,
            'code': 'MISC',
            'type': 'general',
        }
        write_file_2_pull(model, vals)
        journal_id = clodoo.executeL8(ctx,
                                      'ir.model.synchro',
                                      'trigger_one_record',
                                      model,
                                      'oe8',
                                      oe8_id)
        store_id(ctx, model, journal_id, oe8_id)
        check_2_account_journal(ctx, journal_id, vals)
        return oe8_id

    def check_2_account_move(ctx, move_id, vals):
        general_check(ctx, 'account.move', move_id, vals)

    def write_2_account_move(ctx, oe8_id=None, name=None):
        model = 'account.move'
        print('Write %s ...' % model)
        oe8_id = oe8_id or 201130
        name = name or 'Giroconto'
        vals = {
            'id': oe8_id,
            'name': name,
            'ref': '2020-11',
            'company_id': 1,
            'date': '2020-11-30',
            'journal_id': 5,
            'state': 'posted',
            'line_id': '''"[
            {
                'account_id': 567,
                'credit': 2606.59,
                'debit': 0.0,
                'name': 'Giroconto',
                'ref': '2020-122',
            },
            {
                'account_id': 555,
                'credit': 0.0,
                'debit': 2606.59,
                'name': 'Giroconto',
                'ref': '2020-122',
            },
            ]"'''.replace('\n', '').replace(' ', '')
        }
        write_file_2_pull(model, vals)
        move_id = clodoo.executeL8(ctx,
                                   'ir.model.synchro',
                                   'trigger_one_record',
                                   model,
                                   'oe8',
                                   oe8_id)
        store_id(ctx, model, move_id, oe8_id)
        check_2_account_move(ctx, move_id, jacket_vals(vals, prefix='oe8:'))
        return oe8_id

    ctx, company_id = init_test(ctx)
    #
    # Repeat tests 2 times to check correct synchronization
    #
    write_country(ctx)
    write_country(ctx, mode='upper')

    write_tax(ctx, mode='only_amount')
    write_tax(ctx)

    write_payment(ctx)
    write_payment(ctx, mode=True)

    if ctx['opts']['conai']:
        write_conai(ctx)
        write_conai(ctx, mode=True)

    write_product(ctx)
    write_product(ctx, mode=True)

    write_partner(ctx, mode='wrong')
    write_partner(ctx)

    print('%d tests connector_vg7 successfully ended' % ctx['ctr'])
    ## return

    write_partner_pull(ctx, company_id)
    write_partner_pull(ctx, company_id, wrong_data=True)
    write_partner_shipping(ctx, company_id)
    write_partner_supplier(ctx, company_id)
    write_partner_supplier(ctx, company_id)
    write_uom(ctx)
    write_transport_reason(ctx)

    # Repeat 2 times with different state
    write_sale_order(ctx, company_id, note=ctx['company_note'])
    write_sale_order(ctx, company_id, state='sale', note=ctx['company_note'])

    # Set method CSV, cache should be reset (it serves to interactive test)
    model = 'synchro.channel'
    clodoo.writeL8(ctx, model, clodoo.searchL8(
        ctx, model, []), {
                       'method': 'CSV',
                       'exchange_path': os.path.expanduser('~/clodoo'),
                       'trace': True,
                   })

    # Repeat 2 times with different state
    write_invoice(ctx, company_id)
    write_invoice(ctx, company_id, state='open')
    # Repeat 2 times with different state
    write_ddt(ctx, company_id)
    write_ddt(ctx, company_id, shipping_id=107)

    # Interactive test
    # model = 'res.partner.bank'
    ext_model = 'banks'
    vals = {
        'id': 133,
        'IBAN': 'IT31Z0306909420615282446606',
        'description': 'Intesa San Paolo Ag.7 MI',
        'customer_id': env_ref(ctx, 'z0bug.res_partner_2'),
    }
    write_file_2_pull(ext_model, vals)
    bank_vals = {
        'id': 123,
        'IBAN': 'IT99A0123412345000000987654',
        'description': 'BPT Banca Popolare di Test',
        'customer_id': 7,
    }
    write_file_2_pull(ext_model, bank_vals, mode='a')

    model = 'res.partner'
    ext_model = 'customers'
    vg7_id = 7
    vals7 = {
        'id': vg7_id,
        'note': 'Partner test: please remove it!',
        'billing_bank_id': 123,
        'billing_cf': '',
        'billing_city': '',
        'billing_codice_univoco': '',
        'billing_company': 'Partner AAA',
        'billing_name': '',
        'billing_surename': '',
        'billing_country': '',
        'billing_country_id': 39,
        'billing_email': '',
        'billing_esonerato_fe': 1,
        'billing_piva': '',
        'billing_postal_code': '20100',
        'billing_region': 'Milano',
        'billing_region_id': 2,
        'billing_street': 'V.le delle Rose',
        'billing_street_number': '13',
        'billing_telephone': '+39 555 999999',
        'billing_telephone2': '',
    }
    write_file_2_pull(ext_model, vals7)
    print('Go to web page, menù customer, partner "AAA"')
    print('then click on synchronize button')
    if ctx['opts']['ask']:
        dummy = input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    else:
        dummy = 'n'
    if not dummy.startswith('n') and not dummy.startswith('N'):
        bank_id = get_id_from_vg7id(
            ctx, 'res.partner.bank', 123, name='vg7_id')
        store_id(ctx, 'res.partner.bank', bank_id, 123)
        # check_partner(ctx,
        #               get_id_from_vg7id(ctx, model, vg7_id),
        #               jacket_vals(shirt_vals(vals7.copy())))
        general_check(ctx, 'res.partner.bank', bank_id, jacket_vals(bank_vals))
    # Rewrite to run trigger test below (it is the 1st record)
    vals7['billing_city'] = 'Milano'
    vals7['billing_postal_code'] = '20123'
    write_file_2_pull(ext_model, vals7)

    model = 'res.partner'
    ext_model = 'suppliers'
    vg7_id = 14
    vals = {
        'id': vg7_id,
        'city': 'Quarto Flegreo',
        'company': 'Delta Quattro s.r.l.',
        'country_id': 39,
        'postal_code': '80010',
        'region': 'Napoli',
    }
    write_file_2_pull(ext_model, vals)
    print('Go to web page, menù supplier, partner "Delta 4"')
    print('then click on synchronize button')
    if ctx['opts']['ask']:
        dummy = input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    else:
        dummy = 'n'
    if not dummy.startswith('n') and not dummy.startswith('N'):
        id = get_id_from_vg7id(ctx, model, vg7_id, name='vg72_id')
        vals = jacket_vals(vals)
        vals['vg72_id'] = vals['vg7:id']
        del vals['vg7:id']
        # check_partner(ctx, id, vals)

    model = 'product.product'
    ext_model = 'products'
    vg7_id = 1
    vals = {
        'id': vg7_id,
        'code': 'A4',
        'description': 'Product AAAA',
    }
    write_file_2_pull(ext_model, vals)
    print('Go to web page, menù product, product "AA"')
    print('then click on synchronize button')
    if ctx['opts']['ask']:
        dummy = input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    else:
        dummy = 'n'
    # if not dummy.startswith('n') and not dummy.startswith('N'):
    #     check_product(
    #         ctx, get_id_from_vg7id(ctx, model, vg7_id), jacket_vals(vals))

    print('>>> Starting trigger tests')
    vg7_id = 3
    vals = {
        'id': vg7_id,
        'code': 'CC',
        'description': 'Product CC',
    }
    write_file_2_pull(ext_model, vals, mode='a')
    write_sale_order(ctx, company_id, state='sale', newprod=True)
    # check_product(
    #     ctx, get_id_from_vg7id(
    #          ctx, 'product.product', vg7_id), jacket_vals(vals))

    # model = 'res.partner.shipping'
    ext_model = 'customers_shipping_addresses'
    vg7_id = 1001
    vals = {
        'customer_shipping_id': vg7_id,
        'customer_id': 7,
        'shipping_city': '',
        'shipping_company': 'Another Address',
        'shipping_country': '',
        'shipping_country_id': 39,
        'shipping_postal_code': '',
        'shipping_region': '',
        'shipping_region_id': '',
        'shipping_street': '',
        'shipping_street_number': '',
    }
    write_file_2_pull(ext_model, vals)
    write_ddt(ctx, company_id, shipping_id=vg7_id)
    vals['id'] = vals['customer_shipping_id'] + 100000000
    del vals['customer_shipping_id']
    # check_partner(
    #     ctx, get_id_from_vg7id(ctx, 'res.partner', vg7_id + 100000000),
    #     jacket_vals(shirt_vals(vals)))

    print('*** Starting trigger test ***')

    model = 'account.payment.term'
    print('Write %s ...' % model)
    ext_model = 'payments'
    vals = {
        'id': 25,
        'description': 'Paypal',
        'code': 'PP',
        'date_scadenza': '''"[
        {
            'scadenza': 30,
            'giorni_fine_mese': 0,
            'fine_mese': 1,
        },
        ]"'''.replace('\n', '').replace(' ', '')
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.country'
    print('Write %s ...' % model)
    ext_model = 'countries'
    vals = {
        'code': 'IT',
        'name': 'Italia',
        'id': 39,
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.country.state'
    print('Write %s ...' % model)
    ext_model = 'regions'
    vals = {
        'code': 'TO',
        'name': 'Torino',
        'id': 11,
    }
    write_file_2_pull(ext_model, vals)
    vals = {
        'code': 'MI',
        'name': 'Milano',
        'id': 2,
    }
    write_file_2_pull(ext_model, vals, mode='a')
    vals = {
        'code': 'BO',
        'name': 'Bologna',
        'id': 54,
    }
    write_file_2_pull(ext_model, vals, mode='a')
    BO_id = clodoo.searchL8(ctx, model, [('name', 'ilike', 'BOLOGNA')])[0]
    store_id(ctx, model, BO_id, 54)
    state_vals = vals

    model = 'res.partner'
    print('Write %s ...' % model)
    ext_model = 'customers'

    name = 'La Romagnola srl'
    vg7_id = 44
    vals_billing = {
        'id': vg7_id,
        'note': '',
        'billing_bank_id': '',
        'billing_cf': '02151140361',
        'billing_city': 'Imola',
        'billing_codice_univoco': 'X12345Y',
        'billing_company': name,
        'billing_name': '',
        'billing_surename': '',
        'billing_country': 'Italia',
        'billing_country_id': 39,
        'billing_email': 'antoniomaria@laromagnola.it',
        'billing_esonerato_fe': 0,
        'billing_piva': '01598041208',
        'billing_postal_code': '40026',
        'billing_region': 'BOLOGNA',
        'billing_region_id': 54,
        'billing_street': 'Via Emilia',
        'billing_street_number': '17',
        'billing_telephone': '0542 640502',
        'billing_telephone2': '',
    }
    write_file_2_pull(ext_model, vals_billing, mode='a')

    ext_model = 'customers_shipping_addresses'
    vg7_id2 = 2
    vals_shipping = {
        'customer_shipping_id': vg7_id2,
        'customer_id': vg7_id,
        'shipping_city': 'Imola',
        'shipping_company': name,
        'shipping_country': 'Italia',
        'shipping_country_id': 39,
        'shipping_postal_code': '40026',
        'shipping_region': 'BOLOGNA',
        'shipping_region_id': 54,
        'shipping_street': 'Piazza Maggiore',
        'shipping_street_number': '43',
    }
    write_file_2_pull(ext_model, vals_shipping, mode='a')

    partner_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers',
                                  'vg7',
                                  vg7_id)
    clodoo.executeL8(ctx,
        'ir.model.synchro',
        'trigger_one_record',
        'customers_shipping_addresses',
        'vg7',
        vg7_id2)
    for rectype in ('delivery', 'invoice'):
        rec_id, rec_vals = prepare_vals(
            ctx, model, partner_id, rectype, name, vg7_id, vg7_id2,
            vals_shipping, vals_billing, False)
        # if rec_id:
        #     check_partner(ctx, rec_id, rec_vals)
    general_check(ctx, 'res.country.state', BO_id, jacket_vals(state_vals))

    model = 'sale.order'
    print('Write %s ...' % model)
    vals = {
        'vg7:payment_id': 25,
        'name': '2187',
        'vg7_id': 2187,
        'vg7:customer_id': vg7_id,
        'vg7:customer_shipping_id': vg7_id2,
        'state': 'sale',
        'partner_shipping_id': 16789,
        'vg7:courier_id': 0,
        'partner_id': 17906,
        'vg7:agent_id': 8,
    }
    sale_id = clodoo.executeL8(ctx,
                               model,
                               'synchro',
                               vals)
    ids = clodoo.searchL8(ctx, 'account.payment.term', [('vg7_id', '=', 25)])
    store_id(ctx, 'account.payment.term', ids[0], 25)
    ids = clodoo.searchL8(ctx, 'res.partner', [('vg7_id', '=', vg7_id)])
    store_id(ctx, 'res.partner', ids[0], vg7_id)
    ids = clodoo.searchL8(ctx, 'res.partner',
                          [('vg7_id', '=', vg7_id2 + 100000000)])
    store_id(ctx, 'res.partner', ids[0], vg7_id2)
    general_check(ctx, model, sale_id, vals)
    # Special test
    ids = clodoo.searchL8(ctx, 'res.partner',
                          [('vg7_id', '=', vg7_id2 + 100000000)])
    clodoo.writeL8(ctx, 'res.partner', ids, {'vg7_id': False})
    sale_id = clodoo.executeL8(ctx,
                               model,
                               'synchro',
                               vals)
    ids = clodoo.searchL8(ctx, 'res.partner',
                          [('vg7_id', '=', vg7_id2 + 100000000)])
    store_id(ctx, 'res.partner', ids[0], vg7_id2)
    general_check(ctx, model, sale_id, vals)

    # Test supplier and customer (at the end of test flow)
    ext_model = 'customers'
    vals114 = {
        'id': 114,
        'note': '',
        'billing_bank_id': '',
        'billing_cf': '01781920150',
        'billing_city': 'Milano',
        'billing_codice_univoco': '',
        'billing_company': 'Delta 4 s.r.l.',
        'billing_name': '',
        'billing_surename': '',
        'billing_country': 'Italia',
        'billing_country_id': 39,
        'billing_email': '',
        'billing_esonerato_fe': 1,
        'billing_piva': '00723670964',
        'billing_postal_code': '20864',
        'billing_region': 'MILANO',
        'billing_region_id': 2,
        'billing_street': 'Via Sofocle',
        'billing_street_number': '13',
        'billing_telephone': '0396898792-6210086',
        'billing_telephone2': '',
    }
    write_file_2_pull(ext_model, vals114, mode='a')

    vg7_id = 117
    # name = 'Rossi Maria'
    vals117 = {
        'id': vg7_id,
        'note': '',
        'billing_bank_id': '',
        'billing_cf': 'RSSMRA60T45L219M',
        'billing_city': 'TORINO',
        'billing_codice_univoco': '0000000',
        'billing_company': '',
        'billing_name': 'Maria',
        'billing_surename': 'Rossi',
        'billing_country': 'Italia',
        'billing_country_id': 39,
        'billing_email': 'maria.rossi.60@gmail.com',
        'billing_esonerato_fe': 0,
        'billing_piva': '',
        'billing_postal_code': '10121',
        'billing_region': 'TORINO',
        'billing_region_id': 11,
        'billing_street': 'Via Roma',
        'billing_street_number': '17',
        'billing_telephone': '342.8740910',
        'billing_telephone2': '',
    }
    write_file_2_pull(ext_model, vals117, mode='a')

    partner_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers',
                                  'vg7',
                                  114)
    vals114 = jacket_vals(shirt_vals(vals114))
    vals114['customer'] = True
    vals114['supplier'] = True
    vals114['vg72_id'] = 14
    general_check(ctx, 'res.partner', partner_id, vals114)

    partner_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers',
                                  'vg7',
                                  7)
    general_check(
        ctx, 'res.partner', partner_id, jacket_vals(shirt_vals(vals7)))

    partner_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers',
                                  'vg7',
                                  117)
    if partner_id < 1:
        raise IOError('!!Error creating res.parter w/o vat!')
    if partner_id in ctx['partner_MR_ids']:
        raise IOError('!!Wrong partner_id %s: should be a new record!')
    vals114 = jacket_vals(shirt_vals(vals117))
    vals114['customer'] = True
    vals114['supplier'] = False
    general_check(ctx, 'res.partner', partner_id, vals117)


    print('*** Starting odoo to odoo test ***')

    write_2_user(ctx)
    write_2_company(ctx)
    write_2_partner(ctx)
    write_2_currency(ctx)
    write_2_account_type(ctx)
    check_4_translation(ctx, 'account.account.type', 'type', 'report_type')
    for (oe8_id, code, name, utype, utype_new, id_new) in (
            (1, 'bank', 'Bank and Cash', 'liquidity', 'liquidity',
             'account.data_account_type_liquidity'),
            (2, 'receivable', 'Receivable', 'receivable', 'receivable',
             'account.data_account_type_receivable'),
            (3, 'payable', 'Payable', 'payable', 'payable',
             'account.data_account_type_payable'),
            (4, 'asset', 'Assets', 'other', 'other',
             'account.data_account_type_current_assets'),
            (5, 'liability', 'Current Liabilities', 'other', 'other',
             'account.data_account_type_current_liabilities'),
            (6, 'income', 'Income', 'other', 'other',
             'account.data_account_type_revenue'),
            (7, 'expense', 'Expenses', 'other', 'other',
             'account.data_account_type_expenses'),
    ):
        write_2_account_type(ctx, oe8_id=oe8_id, code=code, name=name,
            utype=utype, utype_new=utype_new)
    write_2_account(ctx, company_id)
    check_4_translation(ctx, 'account.account', 'user_type_id', 'user_type')
    check_4_translation(ctx, 'account.account', 'internal_type', 'type')
    write_2_account(ctx, company_id)
    write_2_account(ctx, company_id, oe8_id=555, code='152100',
        name='Crediti v/clienti Italia', utype='receivable',
        type_xref='account.data_account_type_receivable')
    write_2_tax(ctx, company_id)
    check_4_translation(ctx, 'account.tax', 'type_tax_use', 'type')
    write_2_account_journal(ctx)
    # pdb.set_trace()
    ## write_2_account_move(ctx)

    print('*** Starting pull record test ***')

    model = 'account.payment.term'
    ext_model = 'payments'
    # code 30 & 3060 already in DB by previous tests
    vals1 = {
        'id': 30,
        'code': '30',
        'description': 'RiBA 30GG/FM',
        'date_scadenza': '''"[
        {
            'scadenza': 30,
            'giorni_fine_mese': 0,
            'fine_mese': 1,
        },
        ]"'''.replace('\n', '').replace(' ', '')
    }
    write_file_2_pull(ext_model, vals1)
    vals2 = {
        'id': 3060,
        'code': '31',
        'description': 'RiBA 30/60 GG/FM',
        'date_scadenza': '''"[
        {
            'scadenza': 30,
            'giorni_fine_mese': 0,
            'fine_mese': 1,
        },
        {
            'scadenza': 60,
            'giorni_fine_mese': 0,
            'fine_mese': 'S',
        }
        ]"'''.replace('\n', '').replace(' ', '')
    }
    write_file_2_pull(ext_model, vals2, mode='a')
    vals3 = {
        'id': 10,
        'code': 'BB3060',
        'description': 'BB 30/60GG',
        'date_scadenza': '''"[
        {
            'scadenza': 30,
            'giorni_fine_mese': 0,
            'fine_mese': 1,
        },
        {
            'scadenza': 60,
            'giorni_fine_mese': 0,
            'fine_mese': 'S',
        }
        ]"'''.replace('\n', '').replace(' ','')
    }
    write_file_2_pull(ext_model, vals3, mode='a')
    print('Go to web page, menù Setting > Technical > DB > sync channel')
    print('then import account.payment.term of vg7 channel')
    if ctx['opts']['ask']:
        dummy = input('Did you import %s records (Yes,No)? ' % ext_model)
    else:
        dummy = 'n'
    if not dummy.startswith('n') and not dummy.startswith('N'):
        payment_id = get_id_from_vg7id(ctx, model, 10)
        store_id(ctx, model, payment_id, 10)
        del vals3['code']
        general_check(ctx, model, payment_id, jacket_vals(vals3))
        model = 'account.payment.term.line'
        ids = clodoo.searchL8(ctx, model, [('payment_id', '=', payment_id)])
        if len(ids) != 2:
            raise IOError('!!Invalid # of payment lines!')
        ctx['ctr'] += 1
        for ii, id in enumerate(ids):
            vals = eval(vals3['vg7:date_scadenza'][1:-1])[ii]
            vals['payment_id'] = payment_id
            general_check(ctx, model, id, jacket_vals(vals))

    print('*** Starting test on unmanaged tables ***')

    ext_model = 'crm.team'
    model = ext_model
    vals = {'id': 1, 'name': 'Sale Example Team'}
    write_file_2_pull(ext_model, vals, mode='w')
    crm_ids = clodoo.searchL8(ctx, model, [('name', '=', 'Sale Example Team')])
    if crm_ids:
        raise IOError('Record %s already present in %s' % (vals, model))
    ctx['ctr'] += 1
    crm_id = clodoo.executeL8(ctx,
                              'ir.model.synchro',
                              'trigger_one_record',
                              ext_model,
                              'oe8',
                              1)
    if not crm_id or crm_id < 1:
        raise IOError('Record %s not written in %s' % (vals, model))
    ctx['ctr'] += 1
    crm_ids = clodoo.searchL8(ctx, model, [('name', '=', 'Sale Example Team')])
    if not crm_ids or crm_ids[0] != crm_id:
        raise IOError('Record %s not found in %s' % (vals, model))
    ctx['ctr'] += 1
    crm_id2 = clodoo.executeL8(ctx,
                               'ir.model.synchro',
                               'trigger_one_record',
                               ext_model,
                               'oe8',
                               1)
    if crm_id != crm_id2:
        raise IOError(
            'Record %s not rewritten in %s.%d' % (vals, model, crm_id))
    ctx['ctr'] += 1

    print('%d tests connector_vg7 successfully ended' % ctx['ctr'])


parser = z0lib.parseoptargs("Odoo test environment",
                            "© 2017-2019 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
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
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
parser.add_argument("-1", "--param-1",
                    help="value to pass to called function",
                    dest="param_1")
parser.add_argument("-2", "--param-2",
                    help="value to pass to called function",
                    dest="param_2")
parser.add_argument("-3", "--param-3",
                    help="value to pass to called function",
                    dest="param_3")
parser.add_argument("-4", "--param-4",
                    help="value to pass to called function",
                    dest="param_4")
parser.add_argument("-5", "--param-5",
                    help="value to pass to called function",
                    dest="param_5")
parser.add_argument("-6", "--param-6",
                    help="value to pass to called function",
                    dest="param_6")

ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)
msg_time = time.time()
os0.set_tlog_file('./odoo_shell.log', echo=True)
test_synchro_vg7(ctx)
exit(0)
