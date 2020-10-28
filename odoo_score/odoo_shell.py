#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from python_plus import unicodes
import os
import sys
from datetime import date, datetime, timedelta
import time
import re
import csv
import getpass
from unidecode import unidecode
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


__version__ = "0.1.0.9"


MAX_DEEP = 20
PAY_MOVE_STS_2_DRAFT = ['posted', ]
INVOICES_STS_2_DRAFT = ['open', 'paid']
STATES_2_DRAFT = ['open', 'paid', 'posted']
TECH_FIELDS = [
    'create_date',
    'create_uid',
    'display_name',
    'id',
    'image',
    '__last_update',
    'oe7_id',
    'vg7_id',
    'write_date',
    'write_uid',
]
parser = z0lib.parseoptargs("Odoo test environment",
                            "© 2017-2019 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-A", "--action",
                    help="internal action to execute",
                    dest="function",
                    metavar="python_name",
                    default='')
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
parser.add_argument("-w", "--src-config",
                    help="Source DB configuration file",
                    dest="from_confn",
                    metavar="file")
parser.add_argument("-z", "--src-db_name",
                    help="Source database name",
                    dest="from_dbname",
                    metavar="name")
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


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text,'\r',)
        msg_time = time.time()


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


def synchro(ctx, model, vals):
    sts = 0
    ids = []
    if 'id' in vals:
        ids = clodoo.searchL8(ctx, model, [('id', '=', vals['id'])])
        if not ids or ids[0] != vals['id']:
            raise IOError('ID %d does not exist in %s' %
                            vals['id'], model)
        del vals['id']
    if not ids and model == 'account.rc.type.tax':
        domain = []
        for nm in ('rc_type_id', 'purchase_tax_id', 'sale_tax_id'):
            if nm in vals:
                domain.append((nm, '=', vals[nm]))
        if domain:
            ids = clodoo.searchL8(ctx, model, domain)
            if len(ids) != 1:
                ids = []
    elif model == 'account.fiscal.position.tax':
        domain = []
        for nm in ('position_id', 'tax_src_id', 'tax_dest_id'):
            if nm in vals:
                domain.append((nm, '=', vals[nm]))
        if domain:
            ids = clodoo.searchL8(ctx, model, domain)
            if len(ids) != 1:
                ids = []
    if not ids:
        candidate = []
        for nm in ('description', 'code', 'name'):
            if nm == 'description' and model != 'account.tax':
                continue
            if nm in vals:
                domain = [(nm, '=', vals[nm])]
                ids = clodoo.searchL8(ctx, model, domain)
                if len(ids) == 1:
                    break
                elif not candidate or len(candidate) > len(ids):
                    candidate = ids
                if 'company_id' in vals:
                    domain.append(('company_id', '=', vals['company_id']))
                    ids = clodoo.searchL8(ctx, model, domain)
                    if len(ids) == 1:
                        break
                    elif not candidate or len(candidate) >= len(ids):
                        candidate = ids
        if not ids and candidate:
            ids = candidate
    if ids:
        ids = ids[0]
        clodoo.writeL8(ctx, model, ids, vals)
    else:
        ids = clodoo.createL8(ctx, model, vals)
    return ids


def _get_tax_record(ctx, code=None, company_id=None):
    code = code or '22v'
    company_id = company_id or env_ref(ctx, 'z0bug.mycompany')
    tax_id = clodoo.searchL8(ctx,
                             'account.tax',
                             [('description', '=', code),
                              ('company_id', '=', company_id)])
    if not tax_id and code.startswith('a17c'):
        tax_id = clodoo.searchL8(ctx,
                                 'account.tax',
                                 [('description', '=', 'a%s' % code),
                                  ('company_id', '=', company_id)])
    if tax_id:
        tax_id = tax_id[0]
    else:
        tax_id = False
    return tax_id


def param_date(param, model=None, date_field=None, ctx=ctx):
    if param == '?':
        date_ids = False
    else:
        if param and param.startswith('+'):
            date_ids = date.strftime(
                date.today() - timedelta(int(param)), '%04Y-%02m-%02d')
        else:
            day = datetime.now().day
            month = datetime.now().month
            year = datetime.now().year
            if day < 15:
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
            day = 1
            from_date = '%04d-%02d-%02d' % (year, month, day)
            date_ids = param or from_date
    if not date_ids:
        date_ids = raw_input(
            'IDS to manage or date yyyy-mm-dd (empty means all)? ')
    if model and date_field:
        if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
            date_ids = clodoo.searchL8(ctx, model,
                                       [(date_field, '>=', date_ids)])
        else:
            date_ids = eval(date_ids)
    return date_ids


def param_mode_commission(param):
    mode = ctx['param_1'] or 'A'
    while mode not in ('A', 'R', 'C'):
        mode = raw_input('Mode (Add_missed,Recalculate,Check)? ')
        mode = mode[0].upper() if mode else ''
    return mode


def param_product_agent(param):
    product_id = agent_id = False
    if param:
        if param.startswith('P'):
            product_id = int(param[1:])
        elif param.startswith('A'):
            agent_id = int(param[1:])
    return product_id, agent_id


def all_addr_same_customer(ctx):
    print('Set delivery address to the same of customer on sale order')
    if ctx['param_1'] == 'help':
        print('delivery_addr_same_customer '
              '[from_date|+days|ids] [Inv|Del|Both] [partner_id]')
        return
    model = 'sale.order'
    date_ids = param_date(ctx['param_1'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, model,
                              [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    select = 'B'
    if ctx['param_2'] in ('I', 'D', 'B'):
        select = ctx['param_2']
    if ctx['param_3']:
        force_partner_id = int(ctx['param_3'])
    else:
        force_partner_id = False
    ctr = 0
    for so in clodoo.browseL8(ctx,model,ids):
        vals = {}
        if force_partner_id:
            vals['partner_id'] = force_partner_id
        else:
            if (select in ('B', 'D') and
                    so.partner_shipping_id != so.partner_id):
                vals['partner_shipping_id'] = so.partner_id.id
            if (select in ('B', 'I') and
                    so.partner_invoice_id != so.partner_id):
                vals['partner_invoice_id'] = so.partner_id.id
        if vals:
            clodoo.writeL8(ctx, model, so.id, vals)
            print('so.number=%s' % so.name)
            ctr += 1
    print('%d sale orders updated' % ctr)


def set_db_4_test(ctx):
    print('Set database ready for tests')
    if ctx['param_1'] == 'help':
        print('set_db_4_test')
        return
    main_company = env_ref(ctx, 'base.main_company')
    company_id = env_ref(ctx, 'z0bug.mycompany')
    partner_company = env_ref(ctx, 'z0bug.partner_mycompany')
    if not company_id or company_id == main_company:
        model = 'res.company'
        domain = [('id', '!=', main_company)]
        if partner_company:
            domain.append(('partner_id', '=', partner_company))
        companies = clodoo.searchL8(ctx, model, domain)
        if not companies and partner_company:
            print('Wrong config! Company partner is not the declared one!')
            domain = [('id', '!=', main_company)]
            companies = clodoo.searchL8(ctx, model, domain)
        if not companies:
            raise IOError('!!No company to test!')
        add_xref(ctx, 'z0bug.mycompany', 'res.company', companies[0])
        print('Database set to test')
    else:
        print('Database is already set to test')
    model = 'res.company'
    company_id = env_ref(ctx, 'z0bug.mycompany')
    partner_company_id = env_ref(ctx, 'z0bug.partner_mycompany')
    company = clodoo.browseL8(ctx, model, company_id)
    if company.partner_id != partner_company_id:
        print('Wrong config! Company partner is not the declared one!')
        valid_partner = False
        if partner_company_id:
            partner = clodoo.browseL8(ctx, 'res.partner', partner_company_id)
            if partner.city == 'Ozzero':
                valid_partner = True
        if valid_partner:
            clodoo.writeL8(
                ctx, model, company_id, {'partner_id': partner_company_id})
        else:
            add_xref(ctx, 'z0bug.partner_mycompany', 'res.partner',
                     company.partner_id.id)


def order_inv_group_by_partner(ctx):
    print('Set order invoicing group by customer')
    if ctx['param_1'] == 'help':
        print('order_inv_group_by_partner'
              '[from_date|+days|ids]')
        return
    model = 'sale.order'
    date_ids = param_date(ctx['param_1'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, model,
                              [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            domain = [('order_id', '=', ids)]
        else:
            domain = [('order_id', 'in', ids)]
    else:
        domain = []
    ctr = 0
    for order in clodoo.browseL8(
            ctx, model, clodoo.searchL8(
                ctx, model, domain, order='name desc,id')):
        msg_burst('%s ...' % order.name)
        partner_group = order.partner_id.ddt_invoicing_group
        sale_group = order.ddt_invoicing_group
        if sale_group != partner_group:
            print('Changing group of %s' % order.name)
            clodoo.writeL8(ctx, model, order.id,
                           {'ddt_invoicing_group': partner_group})
            ctr += 1
    print('%d sale order updated' % ctr)


def order_commission_by_partner(ctx):
    print('If missed, set commission in order lines from customer')
    if ctx['param_1'] == 'help':
        print('order_commission_by_partner '
              '[Add|Recalc|Check] [from_date|+days|ids]'
              ' [Pproduct_id|Aagent_id]')
        return
    ord_model = 'sale.order'
    ord_line_model = 'sale.order.line'
    sale_agent_model = 'sale.order.line.agent'
    mode = param_mode_commission(ctx['param_1'])
    date_ids = param_date(ctx['param_2'])
    product_id, agent_id = param_product_agent(ctx['param_3'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, ord_model,
                              [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            domain = [('order_id', '=', ids)]
            domain1 = [('id', '=', ids)]
        else:
            domain = [('order_id', 'in', ids)]
            domain1 = [('id', 'in', ids)]
    else:
        domain = []
        domain1 = []
    if product_id:
        domain.append(('product_id', '=', product_id))
    print('Starting mode %s from %s' % (mode, date_ids))
    ctr = 0
    for ord_line in clodoo.browseL8(
        ctx, ord_line_model, clodoo.searchL8(
            ctx, ord_line_model, domain, order='order_id desc,id')):
        msg_burst('%s ...' % ord_line.order_id.name)
        commission_free = ord_line.product_id.commission_free
        if ord_line.agents and not commission_free:
            if mode in ('A', 'C'):
                continue
            clodoo.unlinkL8(ctx, sale_agent_model, ord_line.agents.id)
        if mode == 'C':
            if not commission_free:
                print('Ord. %s to %-30.30s line %-30.30s w/o commission' % (
                    ord_line.order_id.number,
                    ord_line.order_id.partner_id.name,
                    ord_line.name))
            continue
        rec = {}
        if not commission_free:
            for agent in ord_line.order_id.partner_id.agents:
                rec = {
                    'agent': agent.id,
                    'commission': agent.commission.id,
                }
                break
        vals = {}
        if rec:
            vals['agents'] = [(0, 0, rec)]
        if commission_free:
            vals['commission_free'] = commission_free
        if vals:
            clodoo.writeL8(ctx, ord_line_model, ord_line.id, vals)
            ctr += 1
    if mode != 'C':
        # Force line update
        for order in clodoo.browseL8(
            ctx, ord_model, clodoo.searchL8(
                ctx, ord_model, domain1, order='id desc')):
            msg_burst('%s ...' % order.name)
            clodoo.writeL8(ctx, ord_model, order.id,
                {'name': order.name})
    print('%d sale order lines updated' % ctr)


def inv_commission_by_partner(ctx):
    print('If missed, set commission in invoice lines from customer')
    if ctx['param_1'] == 'help':
        print('inv_commission_by_partner [Add,Recalc|Check] from_date|ids')
        return
    inv_model = 'account.invoice'
    inv_line_model = 'account.invoice.line'
    inv_agent_model = 'account.invoice.line.agent'
    mode = param_mode_commission(ctx['param_1'])
    date_ids = param_date(ctx['param_2'])
    product_id, agent_id = param_product_agent(ctx['param_3'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, inv_model,
                              [('date_invoice', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            domain = [('invoice_id', '=', ids)]
            domain1 = [('id', '=', ids)]
        else:
            domain = [('invoice_id', 'in', ids)]
            domain1 = [('id', 'in', ids)]
    else:
        domain = []
        domain1 = []
    if product_id:
        domain.append(('product_id', '=', product_id))
    domain.append(('invoice_id.type', 'in', ('out_invoice', 'out_refund')))
    domain1.append(('type', 'in', ('out_invoice', 'out_refund')))
    print('Starting mode %s from %s' % (mode, date_ids))
    ctr = 0
    for inv_line in clodoo.browseL8(
        ctx, inv_line_model, clodoo.searchL8(
            ctx, inv_line_model, domain, order='invoice_id desc,id')):
        msg_burst('%s ...' % inv_line.invoice_id.number)
        commission_free = False
        if commission_free == inv_line.product_id:
            commission_free = inv_line.product_id.commission_free
        if inv_line.agents and not commission_free:
            if mode in ('A', 'C'):
                continue
            clodoo.unlinkL8(ctx, inv_agent_model, inv_line.agents.id)
        if mode == 'C':
            if not commission_free:
                print('Inv. %s to %-30.30s line %-30.30s w/o commission' % (
                    inv_line.invoice_id.number,
                    inv_line.invoice_id.partner_id.name,
                    inv_line.name))
            continue
        rec = {}
        if not commission_free:
            for agent in inv_line.invoice_id.partner_id.agents:
                rec = {
                    'agent': agent.id,
                    'commission': agent.commission.id,
                }
                break
        vals = {}
        if rec:
            vals['agents'] = [(0, 0, rec)]
        if commission_free:
            vals['commission_free'] = commission_free
        if vals:
            clodoo.writeL8(ctx, inv_line_model, inv_line.id, vals)
            ctr += 1
    if mode != 'C':
        # Force line update
        for invoice in clodoo.browseL8(
            ctx, inv_model, clodoo.searchL8(
                ctx, inv_model, domain1, order='id desc')):
            msg_burst('%s ...' % invoice.name)
            clodoo.writeL8(ctx, inv_model, invoice.id,
                {'name': invoice.name})
    print('%d account invoice lines updated' % ctr)


def inv_commission_from_order(ctx):
    print('If missed, copy commission in invoice lines from sale order lines')
    if ctx['param_1'] == 'help':
        print('inv_commission_from_order [Add,Recalc|Check] from_date|ids')
        return
    inv_model = 'account.invoice'
    inv_line_model = 'account.invoice.line'
    inv_agent_model = 'account.invoice.line.agent'
    ctr = 0
    mode = param_mode_commission(ctx['param_1'])
    date_ids = param_date(ctx['param_2'])
    product_id, agent_id = param_product_agent(ctx['param_3'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, inv_model,
                              [('date_invoice', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            domain = [('invoice_id', '=', ids)]
            domain1 = [('id', '=', ids)]
        else:
            domain = [('invoice_id', 'in', ids)]
            domain1 = [('id', 'in', ids)]
    else:
        domain = []
        domain1 = []
    if product_id:
        domain.append(('product_id', '=', product_id))
    domain.append(('invoice_id.type', 'in', ('out_invoice', 'out_refund')))
    domain1.append(('type', 'in', ('out_invoice', 'out_refund')))
    for inv_line in clodoo.browseL8(
        ctx, inv_line_model, clodoo.searchL8(
            ctx, inv_line_model, domain, order='invoice_id desc,id')):
        msg_burst('%s ...' % inv_line.invoice_id.number)
        commission_free = False
        if commission_free == inv_line.product_id:
            commission_free = inv_line.product_id.commission_free
        if inv_line.agents and not commission_free:
            if mode in ('A', 'C'):
                continue
            clodoo.unlinkL8(ctx, inv_agent_model, inv_line.agents.id)
        if mode == 'C':
            if not commission_free:
                print('Inv. %s to %-30.30s line %-30.30s w/o commission' % (
                    inv_line.invoice_id.number,
                    inv_line.invoice_id.partner_id.name,
                    inv_line.name))
            continue
        for ord_line in inv_line.sale_line_ids:
            if not ord_line.agents.amount:
                continue
            agents = [(0, 0,
                       {'agent': x.agent.id,
                        'commission':
                            x.commission.id}) for x in ord_line.agents]
            clodoo.writeL8(
                ctx, inv_line_model, inv_line.id,
                {'agents': agents})
            ctr += 1
    if mode != 'C':
        for invoice in clodoo.browseL8(
            ctx, inv_model, clodoo.searchL8(
                ctx, inv_model, domain1, order='id desc')):
            msg_burst('%s ...' % invoice.number)
            clodoo.writeL8(ctx, inv_model, invoice.id,
                {'number': invoice.number})
    print('%d invoice lines updated' % ctr)


def update_einvoice_out_attachment(ctx):
    print('Update e-attachment of invoice')
    model = 'account.invoice'
    if ctx['param_1'] == 'help':
        print('update_einvoice_out_attachment invoice_id [state]')
        return
    if ctx['param_1']:
        inv_id = int(ctx['param_1'])
    else:
        inv_id = raw_input('Invoice id: ')
        inv_id = int(inv_id) if inv_id else 0
    if inv_id:
        inv = clodoo.browseL8(ctx, model, inv_id)
        att = inv.fatturapa_attachment_out_id
        if not att:
            print('Invoice %s w/o attachment' % inv.number)
            return
        print('Processing invoice %s' % inv.number)
        model_att = 'fatturapa.attachment.out'
        att = clodoo.browseL8(ctx, model_att, att.id)
        print('Attachment ID = %d, state=%s' % (att.id, att.state))
        state = ctx['param_2']
        while state not in ('ready', 'sent', 'sender_error',
                            'recipient_error', 'reject', 'validated'):
            state = raw_input(
                'State (ready,sent,sender|recipient_error,reject,validated): ')
        clodoo.writeL8(ctx, model_att, att.id, {'state': state})


def unlink_einvoice_out_attachment(ctx):
    print('Unlink e-attachment of invoice')
    model = 'account.invoice'
    if ctx['param_1'] == 'help':
        print('unlink_einvoice_out_attachment invoice_id IN|OUT')
        return
    if ctx['param_1']:
        inv_id = int(ctx['param_1'])
    else:
        inv_id = raw_input('Invoice id: ')
        inv_id = int(inv_id) if inv_id else 0
    if ctx['param_2'] in ('IN', 'in', 'OUT', 'out'):
        in_out = ctx['param_2'].lower()
    else:
        in_out = raw_input('IN/OUT: ')
        if in_out.lower() == 'in':
            field = 'fatturapa_attachment_in_id'
        else:
            field = 'fatturapa_attachment_out_id'
    if inv_id:
        inv = clodoo.browseL8(ctx, model, inv_id)
        print('Processing invoice %s' % inv.number)
        clodoo.writeL8(ctx, model, inv.id,
                       {field: False})


def revaluate_due_date_in_invoces(ctx, inv_id=False):
    print('Revaluate all due dates of invoices from xml')
    model = 'account.invoice'
    if not inv_id:
        inv_id = raw_input('Invoice id: ')
        if inv_id:
            inv_id = eval(inv_id)
    if inv_id:
        inv = clodoo.browseL8(ctx, model, inv_id)
        att = inv.fatturapa_attachment_in_id
        if not att:
            print('Invoice %s w/o attachment' % inv.number)
            return
        print('Processing invoice %s' % inv.number)
        inv_state = inv.state
        if inv.state in INVOICES_STS_2_DRAFT:
            reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
                [inv_id], ctx)
            clodoo.unreconcile_invoices(reconcile_dict, ctx)
            try:
                clodoo.upd_invoices_2_draft(move_dict, ctx)
            except BaseException:
                return
        clodoo.executeL8(ctx,
                         'fatturapa.attachment.in',
                         'revaluate_due_date',
                         att.id,
                         )
        if inv_state in INVOICES_STS_2_DRAFT:
            try:
                clodoo.upd_invoices_2_posted(move_dict, ctx)
            except BaseException:
                return
            reconciles = reconcile_dict[inv_id]
            if len(reconciles):
                cur_reconciles, cur_reconcile_dict = \
                    clodoo.refresh_reconcile_from_inv(
                        inv_id, reconciles, ctx)
                clodoo.reconcile_invoices(cur_reconcile_dict, ctx)


def set_tax_code_on_invoice(ctx):
    print('Set tax code on invoice lines, if missed and if no line amount')
    inv_model = 'account.invoice'
    inv_line_model = 'account.invoice.line'
    inv_id = raw_input('Invoice id: ')
    if inv_id:
        inv_id = int(inv_id)
        invoice = clodoo.browseL8(ctx, inv_model, inv_id)
        tax_id = _get_tax_record(ctx, company_id=invoice.company_id.id)
        if not tax_id:
            print('Tax 22v not found!')
        ctr = 0
        for inv_line in clodoo.browseL8(
            ctx, inv_line_model, clodoo.searchL8(
                ctx, inv_line_model, [('invoice_id', '=', inv_id)])):
            msg_burst('%s ...' % inv_line.name)
            if inv_line.invoice_line_tax_ids:
                continue
            if inv_line.price_subtotal != 0.0:
                print('Line w/o tax but with total amount!')
                continue
            clodoo.writeL8(
                ctx, inv_line_model, inv_line.id,
                    {'invoice_line_tax_ids': [(6, 0, [tax_id])]})
            ctr += 1

        clodoo.writeL8(ctx, inv_model, inv_id,
                {'number': invoice.number})
    print('%d invoice lines updated' % ctr)


def show_module_group(ctx):
    print('Show group infos and external names')
    model_grp = 'res.groups'
    model_ctg = 'ir.module.category'
    model_ir_md = 'ir.model.data'
    gid = True
    while gid:
        gid = raw_input('Res.groups id: ')
        if gid:
            gid = int(gid)
        if gid:
            group = clodoo.browseL8(ctx, model_grp, gid, context={'lang': 'en_US'})
            cid = group.category_id.id
            categ = clodoo.browseL8(ctx, model_ctg, cid, context={'lang': 'en_US'})
            print('%6d) Category %s' % (cid, categ.name))
            uniq_field = []
            grp_ids = clodoo.searchL8(ctx, model_grp,
                                      [('category_id', '=', cid)])
            for group in clodoo.browseL8(ctx, model_grp, grp_ids):
                if group.implied_ids:
                    uniq_field.append(group.id)
                    uniq_field += [x.id for x in group.implied_ids]
            for group in clodoo.browseL8(ctx, model_grp, grp_ids,
                                         context={'lang': 'en_US'}):
                ir_md = clodoo.browseL8(ctx, model_ir_md,
                    clodoo.searchL8(ctx, model_ir_md,
                                    [('model', '=', model_grp),
                                     ('res_id', '=', group.id)]))
                if group.id in uniq_field:
                    tag = '*'
                else:
                    tag = ''
                print('%6d) -- Value [%-16.16s] > [%-32.32s] as "%s.%s" {%s}' % (
                    group.id,
                    group.name,
                    group.full_name,
                    ir_md.module,
                    ir_md.name,
                    tag))


def clean_translations(ctx):
    print('Delete unuseful translations')
    model = 'ir.translation'
    domain = [('lang', '=', 'it_IT'),
             '|',
             ('name', '=', 'ir.module.module,description'),
             ('name', '=', 'ir.module.module,shortdesc')]
    ids = clodoo.searchL8(ctx, model, domain)
    print('unlink %s' % ids)
    clodoo.unlinkL8(ctx, model, ids)
    print('%d records deleted' % len(ids))


def close_sale_orders(ctx):
    print('Close sale orders with linked invoice')
    if ctx['param_1'] == 'help':
        print('close_sale_orders')
        return
    model = 'sale.order'
    ctr = 0
    for so in clodoo.browseL8(ctx, model, clodoo.searchL8(
            ctx, model, [('state', '=', 'sale'),
                         ('invoice_status', '=', 'to invoice')])):
        if so.invoice_ids:
            clodoo.writeL8(ctx, model, so.id, {'invoice_status': 'invoiced'})
            ctr += 1
    print('%d sale order updated!' % ctr)


def close_purchase_orders(ctx):
    print('Close purchase orders lines that are delivered')
    if ctx['param_1'] == 'help':
        print('close_purchase_orders '
              '[byLine|Header] [from_date|+days|ids]')
        return
    if ctx['param_1'] not in ('L', 'H'):
        print('Invalid param #1: use L!H ')
        return
    mode = ctx['param_1']
    model = 'purchase.order'
    model_line = 'purchase.order.line'
    date_ids = param_date(ctx['param_2'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, model,
                              [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            domain = [('order_id', '=', ids)]
            domain1 = [('id', '=', ids)]
        else:
            domain = [('order_id', 'in', ids)]
            domain1 = [('id', 'in', ids)]
    else:
        domain = []
        domain1 = []
    ctr = 0
    if mode == 'L':
        for po in clodoo.browseL8(
            ctx, model_line, clodoo.searchL8(
                ctx, model_line, domain)):
            if po.qty_invoiced == 0.0:
                qty_received = po.product_qty
            elif po.qty_received == 0.0:
                qty_received = po.product_qty
            else:
                qty_received = 0.0
            print(po.product_qty,po.qty_received,qty_received,po.qty_invoiced)
            if qty_received > 0.0:
                clodoo.writeL8(ctx,model_line,po.id,{'qty_received': qty_received})
                ctr += 1
    elif mode == 'H':
        for po in clodoo.browseL8(
            ctx, model, clodoo.searchL8(
                ctx, model, domain1)):
            clodoo.writeL8(ctx, model, po.id, {'invoice_status':'invoiced'})
            ctr += 1
    print('%d purchase order [lines] updated' % ctr)


def set_fiscal_on_products(ctx):
    print('Set vat and account code on products')
    model = 'product.template'
    if ctx['param_1'] == 'help':
        print('set_fiscal_on_products 22v 22a accv acca')
        return
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company found!')
    taxv = ctx['param_1'] or '22v'
    taxa = ctx['param_2'] or '22a'
    accv = ctx['param_3'] or '510000'
    acca = ctx['param_4'] or '610100'
    model_vat = 'account.tax'
    model_acc = 'account.account'
    taxv_ids = clodoo.searchL8(
        ctx, model_vat, [('description', '=', taxv),
                         ('company_id', '=', company_id)])
    if not taxv:
        print('Code tax %s not found!' % taxv)
        return
    taxa_ids = clodoo.searchL8(
        ctx, model_vat, [('description', '=', taxa),
                         ('company_id', '=', company_id)])
    if not taxa:
        print('Code tax %s not found!' % taxa)
        return
    accv_ids = clodoo.searchL8(
        ctx, model_acc, [('code', '=', accv),
                         ('company_id', '=', company_id)])
    if not accv:
        print('Account code %s not found!' % accv)
        return
    acca_ids = clodoo.searchL8(
        ctx, model_acc, [('code', '=', acca),
                         ('company_id', '=', company_id)])
    if not accv:
        print('Account code %s not found!' % acca)
        return
    ctr = 0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if taxv_ids[0] not in pp.taxes_id.ids:
            clodoo.writeL8(ctx, model, pp.id,
                           {'taxes_id': [(6, 0, taxv_ids)]})
            ctr += 1
        if taxa_ids[0] not in pp.supplier_taxes_id.ids:
            clodoo.writeL8(ctx, model, pp.id,
                           {'supplier_taxes_id': [(6, 0, taxa_ids)]})
            ctr += 1
        if accv_ids[0] != pp.property_account_income_id.id:
            clodoo.writeL8(ctx, model, pp.id,
                           {'property_account_income_id': accv_ids[0]})
            ctr += 1
        if acca_ids[0] != pp.property_account_expense_id.id:
            clodoo.writeL8(ctx, model, pp.id,
                           {'property_account_expense_id': acca_ids[0]})
            ctr += 1
    print('%d product templates updated' % ctr)


def set_products_delivery_policy(ctx):
    print('Set purchase methods to purchase in all products')
    model = 'product.template'
    if ctx['param_1'] == 'help':
        print('set_products_delivery_policy order|delivery')
        return
    invoice_policy = ctx['param_1'] or 'order'
    if invoice_policy == 'order':
        purchase_method = 'purchase'
    else:
        purchase_method = 'receive'
    ctr=0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if pp.purchase_method != purchase_method:
            clodoo.writeL8(ctx, model, pp.id,
                           {'purchase_method': purchase_method})
            ctr += 1
        if pp.invoice_policy != invoice_policy:
            clodoo.writeL8(ctx, model, pp.id,
                           {'invoice_policy': invoice_policy})
            ctr += 1
    print('%d product templates updated' % ctr)

    model = 'product.product'
    ctr=0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if pp.purchase_method != purchase_method:
            clodoo.writeL8(ctx, model, pp.id,
                           {'purchase_method': purchase_method})
            ctr += 1
        if pp.invoice_policy != invoice_policy:
            clodoo.writeL8(ctx, model, pp.id,
                           {'invoice_policy': invoice_policy})
            ctr += 1
    print('%d products updated' % ctr)


def set_products_2_consumable(ctx):
    print('Set consumable of the stockable products')
    model = 'product.template'
    ctr=0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model,
            [('type', '=', 'product')])):
        clodoo.writeL8(ctx, model, pp.id, {'type':'consu'})
        ctr += 1
    print('%d product templates updated' % ctr)

    model = 'product.product'
    ctr=0
    for pp in clodoo.browseL8(ctx, model,clodoo.searchL8(ctx, model,
            [('type', '=', 'product')])):
        clodoo.writeL8(ctx, model, pp.id, {'type':'consu'})
        ctr += 1
    print('%d products updated' % ctr)


def print_tax_codes(ctx):
    print('Show all tax codes')
    model = 'account.tax'
    for rec in clodoo.browseL8(ctx, model,
                               clodoo.searchL8(ctx, model, [])):
        if ctx['majver'] < 9:
            print('%-10.10s %-60.60s %.3f %s' % (
                rec.description, rec.name, rec.amount, rec.parent_id))
        else:
            print('%-10.10s %-60.60s %.3f %s' % (
                rec.description, rec.name, rec.amount, rec.parent_tax_ids))
    if ctx['majver'] < 9:
        dummy = raw_input('Press RET do print account.tax.code')
        model = 'account.tax.code'
        for rec in clodoo.browseL8(ctx, model,
                                   clodoo.searchL8(ctx, model, [])):
            print('%-16.16s %-60.60s' % (rec.code, rec.name))


def set_report_config(ctx):
    print('Set report and multireport configuration')
    print('Require module "base_multireport"')
    if ctx['param_1'] == 'help':
        print('reset_report_config header_mode footer_mode payment_term '
              'ord_ref|False|Default ddt_ref|False|Default print|Default')
        return
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if company_id:
        company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')
        clodoo.writeL8(
            ctx, 'res.partner', company_partner_id,
            {'codice_destinatario': 'URCROKA'})

    header_mode = ctx['param_1']
    footer_mode = ctx['param_2']
    payment_term_position = ctx['param_3']
    order_ref_text = ctx['param_4']
    ddt_ref_text = ctx['param_5']
    code_mode = ctx['param_6']
    ctr = 0
    mr_t_odoo = env_ref(ctx, 'base_multireport.mr_t_odoo')
    model = 'multireport.style'
    vals = {
        'template_sale_order': mr_t_odoo,
        'template_stock_picking_package_preparation': mr_t_odoo,
        'template_account_invoice': mr_t_odoo,
        'template_purchase_order': mr_t_odoo,
        'address_mode': 'standard',
        'custom_footer': '<p>Codice Destinatario: %(codice_destinatario)s</p>',
    }
    if code_mode:
        if code_mode == 'code':
            vals['code_mode'] = 'print'
            vals['description_mode'] = 'nocode'
        elif code_mode == 'Default':
            vals['code_mode'] = 'noprint'
            vals['description_mode'] = 'as_is'
    if header_mode:
        vals['header_mode'] = header_mode
    if footer_mode:
        vals['footer_mode'] = footer_mode
    if payment_term_position:
        vals['payment_term_position'] = payment_term_position
    for style in clodoo.browseL8(
        ctx, model,
            clodoo.searchL8(ctx, model, [('origin', '!=', 'odoo')])):
        print('Processing style %s' % style.name)
        clodoo.writeL8(ctx, model, style.id, vals)
        ctr += 1
    model = 'ir.actions.report.xml'
    vals = {
        # 'code_mode': '',
        # 'description_mode': '',
        # 'payment_term_position': '',
        # 'header_mode': '',
        # 'footer_mode': '',
        'template': mr_t_odoo,
        'order_ref_text': '',
        'ddt_ref_text': '',
        'address_mode': '',
    }
    domain = [('model', 'in', ('sale.order',
                              'stock.picking.package.preparation',
                              'account.invoice',
                              'purchase.order'))]
    for rpt in clodoo.browseL8(
        ctx, model,
            clodoo.searchL8(ctx, model, [])):
        print('Processing report %s' % rpt.name)
        clodoo.writeL8(ctx, model, rpt.id, vals)
        ctr += 1
    domain = [('model', 'not in', ('sale.order',
                                  'stock.picking.package.preparation',
                                  'account.invoice',
                                  'purchase.order'))]
    del vals['template']
    for rpt in clodoo.browseL8(
        ctx, model,
            clodoo.searchL8(ctx, model, [])):
        print('Processing report %s' % rpt.name)
        clodoo.writeL8(ctx, model, rpt.id, vals)
        ctr += 1

    vals = {
        'address_mode': '',
    }
    if order_ref_text:
        if order_ref_text == 'False':
            vals['order_ref_text'] = ''
        elif order_ref_text == 'Default':
            vals['order_ref_text'] = 'Vs. Ordine: %(client_order_ref)s / '\
                'Ns. Ordine: %(order_name)s del %(date_order)s'
        else:
            vals['order_ref_text'] = order_ref_text
    if ddt_ref_text:
        if ddt_ref_text == 'False':
            vals['ddt_ref_text'] = ''
        elif ddt_ref_text == 'Default':
            vals['ddt_ref_text'] = 'DdT %(ddt_number)s - %(date_ddt)s'
        else:
            vals['ddt_ref_text'] = ddt_ref_text
    model = 'ir.ui.view'
    domain = [('key', '=', 'base_multireport.external_layout_header')]
    ids = clodoo.searchL8(ctx, model, domain)
    if len(ids) == 1:
        vals['header_id'] = ids[0]
    domain = [('key', '=', 'base_multireport.external_layout_footer')]
    ids = clodoo.searchL8(ctx, model, domain)
    if len(ids) == 1:
        vals['footer_id'] = ids[0]
    model = 'multireport.template'
    if vals:
        for rpt in clodoo.browseL8(
            ctx, model,
                clodoo.searchL8(ctx, model, [])):
            print('Processing template %s' % rpt.name)
            clodoo.writeL8(ctx, model, rpt.id, vals)
            ctr += 1

    model = 'res.company'
    mr_style_odoo = env_ref(ctx, 'base_multireport.mr_style_odoo')
    vals = {'report_model_style': mr_style_odoo}
    for company_id in clodoo.searchL8(ctx, model, []):
        try:
            clodoo.writeL8(ctx, model, company_id, vals)
            ctr += 1
        except IOError:
            pass
    print('%d reports updated' % ctr)


def create_document_test_env(ctx):
    print('create_document_test_env')
    print('Requirement to test module "base_multireport"')
    if ctx['param_1'] == 'help':
        print('create_document_test_env')
        return
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if company_id:
        company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')
        clodoo.writeL8(
            ctx, 'res.partner', company_partner_id,
            {'codice_destinatario': 'URCROKA'})

    def write_products(ctx, company_id):
        model = 'account.tax'
        tax22v = clodoo.searchL8(
            ctx, model, [('description', '=', '22v'),
                         ('company_id', '=', company_id)])[0]
        tax22a = clodoo.searchL8(
            ctx, model, [('description', '=', '22a'),
                         ('company_id', '=', company_id)])[0]
        taxa15v = clodoo.searchL8(
            ctx, model, [('description', '=', 'a15v'),
                         ('company_id', '=', company_id)])[0]
        taxa15a = clodoo.searchL8(
            ctx, model, [('description', '=', 'a15a'),
                         ('company_id', '=', company_id)])[0]

        model = 'product.template'
        model2 = 'product.product'
        print('Write %s ..' % model)
        PROD_LIST = {
            'AA': 'Product Alpha',
            'BB': 'Product Beta',
            'CC': 'Product Chi/Xi',
            'DD': 'Product Delta',
            'EE': 'Product Epsilon',
            'FF': 'Product Phi',
            'GG': 'Product Gamma',
            'HH': 'Product Hospice/Eta',
            'II': 'Product Iota',
            'JJ': 'Product Juvenilia/Psi',
            'KK': 'Product Kappa',
            'LL': 'Product Lambda',
            'MM': 'Product Micro/Mu',
            'NN': 'Product New/Nu',
            'OO': 'Product Omicron',
            'PP': 'Product Greek Pi',
            'QQ': 'Product Quality/Omega',
            'RR': 'Product Rho',
            'SS': 'Product Sigma',
            'TT': 'Product Tau',
            'UU': 'Product Upsilon',
            'VV': 'Product Theta',
            'WW': 'Special Worldwide service',
            'XX': 'Product Xi',
            'YY': 'Special service for Young people',
            'ZZ': 'Product Zeta',
        }
        for nr, code in enumerate(PROD_LIST):
            name = PROD_LIST[code]
            vals = {
                'default_code': code,
                'name': name,
            }
            vals['lst_price'] = (100.0 - len(name)) / (nr * 7 + 19)
            if name.startswith('Special'):
                vals['type'] = 'service'
                vals['standard_price'] = 0.0
            else:
                vals['type'] = 'consu'
                vals['standard_price'] = vals['lst_price'] / 2
            if code in ('JJ', 'YY'):
                vals['taxes_id'] = [(6, 0, [taxa15v])]
                vals['supplier_taxes_id'] = [(6, 0, [taxa15a])]
            else:
                vals['taxes_id'] = [(6, 0, [tax22v])]
                vals['supplier_taxes_id'] = [(6, 0, [tax22a])]
            ids = clodoo.searchL8(ctx, model, [('default_code', '=', code)])
            if ids:
                tmpl_id = ids[0]
                clodoo.writeL8(ctx, model, tmpl_id, vals)
            else:
                tmpl_id = clodoo.createL8(ctx, model, vals)
            vals['product_tmpl_id'] = tmpl_id
            ids = clodoo.searchL8(ctx, model2, [('default_code', '=', code)])
            if ids:
                prod_id = ids[0]
                clodoo.writeL8(ctx, model2, prod_id, vals)
            else:
                prod_id = clodoo.createL8(ctx, model2, vals)

    def write_sale_order(ctx, company_id):
        model = 'sale.order'
        print('Write %s ..' % model)
        vals = {
            'company_id': company_id,
            'partner_id': env_ref(ctx, 'z0bug.res_partner_2'),
            'client_order_ref': '20200123',
            'origin': 'Italy',
        }
        ids = clodoo.searchL8(
            ctx, model, [('client_order_ref', '=', '20200123')])
        if ids:
            order_id = ids[0]
            clodoo.writeL8(ctx, model, order_id, vals)
        else:
            order_id = clodoo.createL8(ctx, model, vals)
        model_prod = 'product.product'
        prod_ids = clodoo.searchL8(
            ctx, model_prod, [('default_code', '!=', ''),
                              ('default_code', '!=', False)],
            order='default_code')
        prod_ids = prod_ids + clodoo.searchL8(
            ctx, model_prod, ['|', ('default_code', '=', ''),
                              ('default_code', '=', False)])
        model = 'sale.order.line'
        def_tax = False
        for nr, product in enumerate(
                clodoo.browseL8(ctx, model_prod, prod_ids)):
            print('Write %s ..' % model)
            if not def_tax:
                def_tax = product.taxes_id.id
            seq = (nr + 1) * 10
            vals = {
                'order_id': order_id,
                'sequence': seq,
                'company_id': company_id,
                'name': product.name,
                'product_id': product.id,
                'price_unit': product.lst_price,
                'product_uom_qty': nr + 1,
                # 'tax_id': [(6, 0, [product.taxes_id.id])],
            }
            if not product.default_code:
                vals['product_uom_qty'] = 1.0
            # if not product.taxes_id:
            #     del vals['tax_id']
            ids = clodoo.searchL8(
                ctx, model, [('order_id', '=', order_id),
                             ('sequence', '=', seq)])
            if ids:
                line_id = ids[0]
                clodoo.writeL8(ctx, model, line_id, vals)
            else:
                line_id = clodoo.createL8(ctx, model, vals)
        # vals = {
        #     'order_id': order_id,
        #     'sequence': 999,
        #     'company_id': company_id,
        #     'name': 'Unclassificated product for test',
        #     'product_id': False,
        #     'price_unit': 10.0,
        #     'product_uom_qty': 3,
        #     'tax_id': [(6, 0, [def_tax])],
        # }
        # ids = clodoo.searchL8(
        #     ctx, model, [('order_id', '=', order_id),
        #                  ('sequence', '=', seq)])
        # if ids:
        #     line_id = ids[0]
        #     clodoo.writeL8(ctx, model, line_id, vals)
        # else:
        #     line_id = clodoo.createL8(ctx, model, vals)
        return order_id

    def write_purchase_order(ctx, company_id):
        model = 'purchase.order'
        print('Write %s ..' % model)
        vals = {
            'company_id': company_id,
            'partner_id': env_ref(ctx, 'z0bug.res_partner_2'),
            'partner_ref': '2020-1234-PO'
        }
        ids = clodoo.searchL8(
            ctx, model, [('partner_ref', '=', '2020-1234-PO')])
        if ids:
            order_id = ids[0]
            clodoo.writeL8(ctx, model, order_id, vals)
        else:
            order_id = clodoo.createL8(ctx, model, vals)
        model_prod = 'product.product'
        prod_ids = clodoo.searchL8(
            ctx, model_prod, [('default_code', '!=', ''),
                              ('default_code', '!=', False)],
            order='default_code')
        prod_ids = prod_ids + clodoo.searchL8(
            ctx, model_prod, ['|', ('default_code', '=', ''),
                              ('default_code', '=', False)])
        model = 'purchase.order.line'
        tax_id = False
        for nr, product in enumerate(
                clodoo.browseL8(ctx, model_prod, prod_ids)):
            print('Write %s ..' % model)
            if product.supplier_taxes_id:
                tax_id = product.supplier_taxes_id.id
            seq = (nr + 1) * 10
            vals = {
                'order_id': order_id,
                'sequence': seq,
                'company_id': company_id,
                'name': product.name,
                'product_id': product.id,
                'price_unit': product.lst_price,
                'product_uom': product.uom_po_id.id,
                'product_qty': nr + 1,
                'date_planned': str(date.today() + timedelta(7)),
                'taxes_id': [(6, 0, [tax_id])],
            }
            if not product.default_code:
                vals['product_qty'] = 1.0
            # if not product.taxes_id:
            #     del vals['tax_id']
            ids = clodoo.searchL8(
                ctx, model, [('order_id', '=', order_id),
                             ('sequence', '=', seq)])
            if ids:
                line_id = ids[0]
                clodoo.writeL8(ctx, model, line_id, vals)
            else:
                line_id = clodoo.createL8(ctx, model, vals)

    write_products(ctx, company_id)
    write_sale_order(ctx, company_id)
    write_purchase_order(ctx, company_id)


def create_RA_config(ctx):
    print('Set withholding tax configuration to test')
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company found!')
    company = clodoo.browseL8(ctx, 'res.company', company_id)
    print('Campany setup is %s' % company.name)
    model = 'account.account'
    credit_acc_id = False
    debit_acc_id = False
    domain = [('name', 'ilike', 'ritenut')]
    if company_id:
        domain.append(('company_id', '=', company_id))
    for acc in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, domain)):
        if re.match('[Er]rario.*[Rr]itenut.*autonom', acc.name):
            debit_acc_id = acc.id
        elif re.match('[Cr]redit.*[Rr]itenut.*acc', acc.name):
            credit_acc_id = acc.id
        elif re.match('[Dd]ebit.*[Rr]itenut.*acc', acc.name):
            debit_acc_id = acc.id
        elif re.match('[Cr]redit.*RA', acc.name):
            credit_acc_id = acc.id
        elif re.match('[Dd]ebit.*RA', acc.name):
            debit_acc_id = acc.id
        elif re.match('[Cr]redit.*[Rr]itenut', acc.name) and not credit_acc_id:
            credit_acc_id = acc.id
        elif re.match('[Dd]ebit.*[Rr]itenut', acc.name) and not debit_acc_id:
            debit_acc_id = acc.id
    model = 'account.payment.term'
    domain = [('name', 'ilike', '15')]
    payment_ids = clodoo.searchL8(ctx, model, domain)
    model_paycode = 'causale.pagamento'
    model = 'withholding.tax'
    ctr_rec = 0

    wt_1040 = clodoo.searchL8(ctx, model, [('name', '=', '1040')])
    wt_1040 = wt_1040[0] if wt_1040 else False
    paycode = clodoo.searchL8(ctx, model_paycode, [('code', '=', 'A')])
    paycode = paycode[0] if paycode else False
    vals = {'name': '1040 - 20% su 100% (A)',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5,0), (0, 0, {'tax': 20, 'base': 1})]
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-20%/100-A'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    if wt_1040:
        vals['id'] = wt_1040
    synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {'name': '1040 - 23% su 100% (A)',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 1})]
            }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/100-A'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {'name': '1040 - 23% su 50% (A)',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 0.5})]
            }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/50-A'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    synchro(ctx, model, vals)
    ctr_rec += 1

    paycode = clodoo.searchL8(ctx, model_paycode, [('code', '=', 'R')])
    paycode = paycode[0] if paycode else False
    vals = {'name': '1040 - 23% su 100% (R)',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 1})]
            }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/100-R'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {'name': '1040 - 23% su 50% (R) (ex 1038)',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 0.5})]
            }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/50-R'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {'name': 'Enasarco 16,50% su 50%',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
            'rate_ids': [(5, 0), (0, 0, {'tax': 16.5, 'base': 0.5})]
            }
    if ctx['majver'] >= 10:
        vals['code'] = 'Enasarco'
        vals['company_id'] = company_id
        vals['wt_types'] = 'enasarco'
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    synchro(ctx, model, vals)
    ctr_rec += 1
    print('%d records inserted/updated' % ctr_rec)


def configure_RiBA(ctx):
    print('Set RiBA configuration to test')
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company found!')
    company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')
    banks = clodoo.browseL8(ctx, 'res.partner', company_partner_id).bank_ids
    journal_id = clodoo.searchL8(ctx, 'account.journal',
                                 [('type', '=', 'bank'),
                                  ('company_id', '=', company_id)])[0]
    account_riba_id = clodoo.searchL8(ctx, 'account.account',
                                 [('code', '=', '152210'), 
                                  ('user_type_id.type', '=', 'receivable'),
                                  ('company_id', '=', company_id)])[0]
    account_riba_in_bank_id = clodoo.searchL8(
        ctx, 'account.account', [('code', '=', '152220'), 
                                 ('user_type_id.type', '=', 'receivable'),
                                 ('company_id', '=', company_id)])[0]
    account_unsolved_id = clodoo.searchL8(
        ctx, 'account.account', [('code', '=', '152230'), 
                                 ('user_type_id.type', '=', 'receivable'),
                                 ('company_id', '=', company_id)])[0]
    account_expense_id = clodoo.searchL8(
        ctx, 'account.account', [('code', '=', '731140'), 
                                 ('company_id', '=', company_id)])[0]
    account_bank_id = clodoo.browseL8(
        ctx, 'account.journal', journal_id).default_credit_account_id.id
    riba_id = False
    if banks:
        bank_name = banks[0].acc_number.strip()
        model = 'riba.configuration'
        for id in clodoo.searchL8(ctx, model, []):
            riba_conf = clodoo.browseL8(ctx, model, id)
            if riba_conf.bank_id.acc_number.strip() == bank_name:
                riba_id = id
                break
    else:
        print('Missed bank account of company')
        return
    vals = {
        'name': '%s SBF' % bank_name,
        'type': 'sbf',
        'bank_id': banks[0].id,
        'company_id': company_id,
        'acceptance_journal_id': journal_id,
        'acceptance_account_id': account_riba_id,
        'accreditation_journal_id': journal_id,
        'accreditation_account_id': account_riba_in_bank_id,
        'unsolved_journal_id': journal_id,
        'overdue_effects_account_id': account_unsolved_id,
        'bank_expense_account_id': account_expense_id,
        'protest_charge_account_id': account_expense_id,
        'settlement_journal_id': journal_id,
        'bank_account_id': account_bank_id,
    }
    if not riba_id:
        riba_id = clodoo.createL8(ctx, model, vals)
        print('RiBA configuration created')
    else:
        clodoo.writeL8(ctx, model, riba_id, vals)
        print('RiBA configuration updated')


def manage_riba(ctx):

    def set_riba_state(ctx, riba_list, state):
        line_state = {
            'draft': 'draft',
            'accepted': 'confirmed',
            'accredited': 'accredited',
            'paid': 'paid',
            'unsolved': 'unsolved',
            'cancel': 'cancel',
        }[state]
        for riba in riba_list.line_ids:
            clodoo.writeL8(ctx, 'riba.distinta.line', riba.id,
                           {'state': line_state,})
        vals = {'state': state}
        if state in ('draft', 'cancel'):
            vals['date_accepted'] = False
        if state in ('draft', 'cancel', 'accepted'):
            vals['date_accreditation'] = False
        if state in ('draft', 'cancel', 'accepted', 'accredited'):
            vals['date_paid'] = False
        clodoo.writeL8(ctx, 'riba.distinta', riba_id, vals)

    def unreconcile_move(ctx, move):
        for line in move.line_ids:
            if (line.user_type_id.type != 'receivable' or
                    not line.reconciled):
                continue
            try:
                move_ids = [x.id for x in 
                    line.full_reconcile_id.reconciled_line_ids]
                context = {'active_ids': move_ids}
                clodoo.executeL8(ctx,
                                 'account.unreconcile',
                                 'trans_unrec',
                                 None,
                                 context)
            except BaseException:
                print('!!Move %d unreconciliable!' % move.id)

    def cancel_riba_moves(ctx, riba_list, moves, by_line=None):
        if not moves:
            return
        try:
            move_list = iter(moves)
            move_list = moves
        except TypeError:
            move_list = [moves]
        for item in move_list:
            if by_line:
                move = item.move_id
            else:
                move = item
            unreconcile_move(ctx, move)
            clodoo.executeL8(ctx,
                             'account.move',
                             'button_cancel',
                              move.id)
        for item in move_list:
            if by_line:
                move = item.move_id
            else:
                move = item
            try:
                clodoo.unlinkL8(ctx,
                                'account.move',
                                move.id)
            except BaseException:
                print('!!Move %d not deleted!' % move.id)

    def riba_new(ctx, riba_list):
        set_riba_state(ctx, riba_list, 'draft')

    print('Do various actions on RiBA list')
    riba_id = False
    while not riba_id:
        riba_id = raw_input('RiBA list id: ')
        if not riba_id:
            return
        riba_id = int(riba_id)
        riba_list = clodoo.browseL8(ctx, 'riba.distinta', riba_id)
        print('Riba list # %s -  state: %s' % (riba_list.name,
                                               riba_list.state))
        for move in riba_list.unsolved_move_ids:
            print('- Unsolved %d' % move.id)
        if riba_list.state == 'paid':
            action = raw_input('Action: Accredited,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'A':
                print('Restore RiBA list to Accredited ..')
                cancel_riba_moves(ctx, riba_list,
                                  riba_list.payment_ids, by_line=True)
                set_riba_state(ctx, riba_list, 'accredited')
        elif riba_list.state == 'accredited':
            action = raw_input('Action: do_Paid,Accepted,State_paid,Quit,Unsolved: ')
            action = action[0].upper() if action else 'Q'
            if action == 'P':
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_paid',
                                     riba_id)
                except BaseException:
                    pass
            elif action == 'A':
                print('Restore RiBA list to accepted ..')
                cancel_riba_moves(ctx, riba_list,
                                  riba_list.accreditation_move_id)
                set_riba_state(ctx, riba_list, 'accepted')
            elif action == 'S':
                set_riba_state(ctx, riba_list, 'paid')
            elif action == 'U':
                for move in riba_list.unsolved_move_ids:
                    print('- Unsolved %d' % move.id)
                    sub = raw_input('Move: Delete,Skip')
                    sub = sub[0].upper() if sub else 'S'
                    if sub == 'D':
                        unreconcile_move(ctx, move)
                        clodoo.executeL8(ctx,
                                         'account.move',
                                         'button_cancel',
                                          move.id)
                        try:
                            clodoo.unlinkL8(ctx,
                                            'account.move',
                                            move.id)
                        except BaseException:
                            print('!!Move %d not deleted!' % move.id)
        elif riba_list.state == 'accepted':
            action = raw_input('Action: do_Accredited,Cancel,State_accredited,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'A':
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_accredited',
                                     riba_id)
                except BaseException:
                    pass
            elif action == 'C':
                print('Cancelling RiBA list ..')
                # TODO: remove after debug
                cancel_riba_moves(ctx, riba_list,
                                  riba_list.accreditation_move_id)
                cancel_riba_moves(ctx, riba_list,
                                  riba_list.acceptance_move_ids)
                set_riba_state(ctx, riba_list, 'draft')
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_cancel',
                                     riba_id)
                except BaseException:
                    pass
            elif action == 'S':
                set_riba_state(ctx, riba_list, 'accredited')
        elif riba_list.state == 'draft':
            action = raw_input('Action: do_Accepted,State_accepted,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'A':
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_accepted',
                                     riba_id)
                except BaseException:
                    pass
            elif action == 'S':
                set_riba_state(ctx, riba_list, 'accepted')
        elif riba_list.state == 'cancel':
            action = raw_input('Action: do_Draft,State_cancel,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'A':
                # riba_new(ctx, riba_list)
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_new',
                                     riba_id)
                except BaseException:
                    pass
            elif action == 'S':
                set_riba_state(ctx, riba_list, 'cancel')
        riba_id = ''


def configure_email_template(ctx):
    print('Configure e-mail template')
    model_ids = clodoo.searchL8(ctx, 'ir.model',
                                [('model', 'in', ('account.invoice',
                                                   'sale.order'))])
    model = 'mail.template'
    email_from = '${(object.company_id.email and \'%s <%s>\' % '\
                 '(object.company_id.name, object.company_id.email) or '\
                 '\'\')|safe}'
    reply_to = '${object.company_id.email}'
    RPT_NAME = {}
    RPT_NAME['account.invoice'] = """
    ${{'out_invoice':'Fattura','out_refund': 'NotaCredito',
     'in_invoice':'Fattura','in_refund':'NC',
     }[object.type]}_${(object.number or 'bozza').replace('/','-')}
    """
    RPT_NAME['sale.order'] = """
    ${{'draft':'Offerta','sent':'Ordine','sale':'Ordine',
     'done':'Conferma','cancel':'Bozza',
     }[object.state]}_${(object.name or 'bozza').replace('/','-')}
    """
    for template in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [('model_id', 'in', model_ids)])):
        print(template.name)
        vals = {'reply_to': reply_to,
                'email_from': email_from,
                'report_name': RPT_NAME[template.model_id.model]}
        clodoo.writeL8(ctx, model, template.id, vals)


def configure_fiscal_position(ctx):
    print('Configure Fiscal Position')
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')

    model = 'account.account'
    vals = {
        'code': '490050',
        'name': 'Transitorio Reverse Charge',
        'company_id': company_id,
        'user_type_id': env_ref(ctx, 'account.data_account_type_expenses'),
    }
    account_rc_id = synchro(ctx, model, vals)

    vals = {
        'code': '153050',
        'name': 'Integr. IVA da c/acquisti UE (L.427/93)',
        'company_id': company_id,
        'user_type_id': env_ref(ctx,
                                'account.data_account_type_current_assets'),
    }
    account_vat_eup_id = synchro(ctx, model, vals)

    vals = {
        'code': '260050',
        'name': 'IVA autofatture da c/acquisti UE',
        'company_id': company_id,
        'user_type_id': env_ref(
            ctx, 'account.data_account_type_current_liabilities'),
    }
    account_vat_eus_id = synchro(ctx, model, vals)

    vals = {
        'code': '260030',
        'name': 'IVA n/deb. split-payment',
        'company_id': company_id,
        'user_type_id': env_ref(
            ctx, 'account.data_account_type_current_liabilities'),
    }
    account_vat_sp_id = synchro(ctx, model, vals)

    model = 'account.journal'
    vals = {
        'code': 'SAJ2',
        'name': 'Integrazione acquisti UE',
        'company_id': company_id,
        'type': 'sale',
        'reverse_charge': True,
        'update_posted': True,
        'show_on_dashboard': False,
    }
    journal_id = synchro(ctx, model, vals)

    vals = {
        'code': 'GCRC',
        'name': 'G/conti reverse charge',
        'company_id': company_id,
        'type': 'general',
        'update_posted': True,
        'default_debit_account': account_rc_id,
        'default_credit_account': account_rc_id,
        'show_on_dashboard': False,
    }
    journal_gcrc_id = synchro(ctx, model, vals)

    model = 'account.tax'
    vat_a17c2a_id = _get_tax_record(ctx, code='a17c2a')
    vals = {
        'description': 'a17c2a',
        'name': 'N.I. art.17 c.2 DPR633',
        'type_type_use': 'purchase',
        'account_id': account_vat_eup_id,
        'refund_account_id': account_vat_eup_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n6'),
        'payability': 'I',
        'law_reference': False,
    }
    if vat_a17c2a_id:
        vals['id'] = vat_a17c2a_id
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c2a_id = synchro(ctx, model, vals)

    vat_a17c2v_id = _get_tax_record(ctx, code='a17c2v')
    vals = {
        'description': 'aa17c2v',
        'name': 'Rev. charge art.17 c.2 DPR633',
        'type_type_use': 'sale',
        'account_id': account_vat_eus_id,
        'refund_account_id': account_vat_eus_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'payability': 'I',
        'law_reference': False,
    }
    if vat_a17c2v_id:
        vals['id'] = vat_a17c2v_id
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c2v_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a17c6ba',
        'name': 'N.I. art.17 c.6 lett. B DPR633 (Cellulari)',
        'type_type_use': 'purchase',
        'account_id': account_vat_eup_id,
        'refund_account_id': account_vat_eup_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n6'),
        'payability': 'I',
        'law_reference': False,
    }
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c6ba_id = synchro(ctx, model, vals)

    vat_a17c6bv_id = _get_tax_record(ctx, code='a17c6bv')
    vals = {
        'description': 'aa17c6bv',
        'name': 'Rev. Charge art.17 c.6 lett. B DPR633 (Cellulari)',
        'type_type_use': 'sale',
        'account_id': account_vat_eus_id,
        'refund_account_id': account_vat_eus_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': False,
        'payability': 'I',
        'law_reference': False,
    }
    if vat_a17c6bv_id:
        vals['id'] = vat_a17c6bv_id
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c6bv_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a17c6ca',
        'name': 'N.I. Art.17 c.6 lett. C DPR633 (Elettronici)',
        'type_type_use': 'purchase',
        'account_id': account_vat_eup_id,
        'refund_account_id': account_vat_eup_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n6'),
        'payability': 'I',
        'law_reference': False,
    }
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c6ca_id = synchro(ctx, model, vals)

    vat_a17c6cv_id = _get_tax_record(ctx, code='a17c6cv')
    vals = {
        'description': 'aa17c6cv',
        'name': 'Rev. Charge Art.17 c.6 lett. C DPR633 (Elettronici)',
        'type_type_use': 'sale',
        'account_id': account_vat_eus_id,
        'refund_account_id': account_vat_eus_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': False,
        'payability': 'I',
        'law_reference': False,
    }
    if vat_a17c6cv_id:
        vals['id'] = vat_a17c6cv_id
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_a17c6cv_id = synchro(ctx, model, vals)

    vat_22spv_id = _get_tax_record(ctx, code='22SPv')
    vals = {
        'description': '22SPv',
        'name': 'Art. 17ter - split-payment',
        'type_type_use': 'sale',
        'account_id': account_vat_eus_id,
        'refund_account_id': account_vat_sp_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': False,
        'payability': 'S',
        'law_reference': 'Art. 17ter DPR633- split-payment',
    }
    if vat_22spv_id:
        vals['id'] = vat_22spv_id
    if ctx['majver'] < 9:
        vals['amount'] = 0.22
    else:
        vals['amount'] = 22.0
    vat_22spv_id = synchro(ctx, model, vals)

    vat_storno22spv_id = _get_tax_record(ctx, code='-22SPv')
    vals = {
        'description': '-22SPv',
        'name': 'Storno split-payment',
        'type_type_use': 'sale',
        'account_id': account_vat_eus_id,
        'refund_account_id': account_vat_sp_id,
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': False,
        'payability': 'S',
        'law_reference': False,
    }
    if vat_storno22spv_id:
        vals['id'] = vat_storno22spv_id
    if ctx['majver'] < 9:
        vals['amount'] = -0.22
    else:
        vals['amount'] = -22.0
    vat_storno22spv_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a8c2v',
        'name': 'Vend.N.I. art.8c2 DPR633 (lett.Intento)',
        'type_type_use': 'sale',
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n3'),
        'law_reference': 'N.I. art.8c2 DPR633 (lett.Intento)'
    }
    vat_a8c2v_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a41v',
        'name': 'Vend.N.I. art.41 L.427/93',
        'type_type_use': 'sale',
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n3'),
        'law_reference': 'Vend.N.I. art.41 L.427/93'
    }
    vat_a41v_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a8av',
        'name': 'Vend.N.I. art.8a DPR633 (Dogana)',
        'type_type_use': 'sale',
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n3'),
        'law_reference': 'N.I. art.8a DPR633 (Dogana)'
    }
    vat_a8av_id = synchro(ctx, model, vals)

    vals = {
        'description': 'a7tv',
        'name': 'Vend.NI art.7ter DPR633 (servizi xUE)',
        'type_type_use': 'sale',
        'amount_type': 'percent',
        'company_id': company_id,
        'nature_id': env_ref(ctx, 'l10n_it_ade.n2'),
        'law_reference': 'NI art.7ter DPR633 (servizi xUE)'
    }
    vat_a7tv_id = synchro(ctx, model, vals)

    model = 'account.rc.type'
    rc_type_id = env_ref(ctx, 'l10n_it_reverse_charge.account_rc_type_1')
    if rc_type_id:
        rc_type = clodoo.browseL8(ctx, model, rc_type_id)
        vals = {
            'name': 'Acquisti in reverse charge',
            'description': 'Acquisti Intra-UE con autofattura',
            'method': 'selfinvoice',
            'partner_type': 'other',
            'partner_id': company_partner_id,
        }
        if journal_id:
            vals['journal_id'] = journal_id
        if journal_gcrc_id:
            vals['payment_journal_id'] = journal_gcrc_id
        rc_type_id = synchro(ctx, model, vals)

        model = 'account.rc.type.tax'
        purchase_tax_id = _get_tax_record(ctx, code='a17c2a')
        sale_tax_id = _get_tax_record(ctx, code='a17c2v')
        vals = {
            'rc_type_id': rc_type_id,
            'purchase_tax_id': purchase_tax_id,
            'sale_tax_id': sale_tax_id,
        }
        synchro(ctx, model, vals)
        model = 'account.rc.type.tax'
        purchase_tax_id = _get_tax_record(ctx, code='a17c6ba')
        sale_tax_id = _get_tax_record(ctx, code='a17c6bv')
        vals = {
            'rc_type_id': rc_type_id,
            'purchase_tax_id': purchase_tax_id,
            'sale_tax_id': sale_tax_id,
        }
        synchro(ctx, model, vals)
        purchase_tax_id = _get_tax_record(ctx, code='a17c6ca')
        sale_tax_id = _get_tax_record(ctx, code='a17c6cv')
        vals = {
            'rc_type_id': rc_type_id,
            'purchase_tax_id': purchase_tax_id,
            'sale_tax_id': sale_tax_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'Reverse charge',
        'company_id': company_id,
        'rc_type_id': rc_type_id,
    }
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx, code='22a'),
            'tax_dest_id': vat_a17c6ba_id,
        }
        synchro(ctx, model, vals)
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx, code='22a'),
            'tax_dest_id': vat_a17c6ba_id,
        }
        synchro(ctx, model, vals)
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx, code='22a'),
            'tax_dest_id': vat_a17c6ca_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'Split Payment',
        'company_id': company_id,
        'split_payment': True,
        'note': 'Operazione effettuata ai sensi degli art. 17-ter comma 1 / '
                '17-quater DPR 633/72 - scissione pagamenti (split payment)',
    }
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': vat_22spv_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'Lettera d\'intento',
        'company_id': company_id,
        'note': 'Operazione senza IVA Vs. lettera d\'intento n. ______ '
                'del __/__/____',
    }
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': vat_a8c2v_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'Regime Intra comunitario',
        'company_id': company_id,
    }
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': vat_a41v_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'Regime Extra comunitario',
        'company_id': company_id,
    }
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': vat_a8av_id,
        }
        synchro(ctx, model, vals)
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': vat_a7tv_id,
        }
        synchro(ctx, model, vals)

    model = 'account.fiscal.position'
    vals = {
        'name': 'IVA al 4%',
        'company_id': company_id,
    }
    ids = clodoo.searchL8(ctx, model, [('name', 'ilike', 'IVA%4')])
    if len(ids) != 1:
        ids = clodoo.searchL8(ctx, model, [('name', 'ilike', 'IVA%4'),
                                           ('company_id', '=', company_id)])
    if len(ids) == 1:
        vals['id'] = ids[0]
    fiscal_pos_id = synchro(ctx, model, vals)
    if fiscal_pos_id:
        model = 'account.fiscal.position.tax'
        vals = {
            'position_id': fiscal_pos_id,
            'tax_src_id': _get_tax_record(ctx),
            'tax_dest_id': _get_tax_record(ctx, code='4v'),
        }
        synchro(ctx, model, vals)

    vals = {
        'sp_account_id': account_vat_sp_id,
        'sp_tax_id': vat_storno22spv_id,
    }
    clodoo.writeL8(ctx, 'res.company', company_id, vals)

    print('Set fiscal positions for RC, Split-payment, lett., EU, xEU and 4%')


def simulate_user_profile(ctx):
    print('Show data as required user')

    def get_agent_names(agents):
        agent_names = []
        try:
            for agent in agents:
                agent_names.append(agent.name)
        except BaseException:
            agent_names.append('N/A')
        return agent_names

    def get_agent_names_line(agents):
        agent_names = []
        try:
            for agent in agents.agent:
                agent_names.append(agent.name)
        except BaseException:
            agent_names.append('N/A')
        return agent_names

    user = raw_input('Username to simulate: ')
    pwd = getpass.getpass()
    pwd = pwd if pwd else 'prova2019'
    uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                   db=ctx['db_name'],
                                   user=user,
                                   pwd=pwd,
                                   ctx=ctx)
    user = clodoo.browseL8(ctx, 'res.users', uid)
    print('***** %s *****' % user.name)
    for model in 'sale.order', 'account.invoice', 'res.partner':
        print('\n[%s]' % model)
        if model == 'res.partner':
            print('%-11.11s %4s %-32.32s %s %s' % (
                'model', 'id', 'name', 'type', 'agents')
            )
            model2 = model
            domain = [('customer', '=', True), ('parent_id', '=', False)]
        elif model == 'account.invoice':
            print('%-15.15s %4s %-20.20s %s' % (
                'model', 'id', 'number', 'agents')
            )
            model2 = 'account.invoice.line'
            domain = []
        else:
            print('%-10.10s %4s %-16.16s %-32.32s %s' % (
                'model', 'id', 'name', 'customer', 'agents')
            )
            model2 = 'sale.order.line'
            domain = []
        for rec in clodoo.browseL8(ctx, model,
                                   clodoo.searchL8(ctx, model, domain)):
            if model == 'res.partner':
                print('%s %4d %-32.32s %s %s' % (
                    model, rec.id, rec.name, rec.type,
                    get_agent_names(rec.agents)))
            elif model == 'account.invoice':
                print('%s %4d %-20.20s %s' % (
                    model, rec.id, rec.number, get_agent_names(rec.agents)))
            else:
                print('%s %4d %-16.16s %-32.32s %s' % (
                    model, rec.id, rec.name, rec.partner_id.name,
                    get_agent_names(rec.agents)))
            if model2:
                if model == 'res.partner':
                    domain = [('parent_id', '=', rec.id)]
                elif model2 == 'account.invoice.line':
                    domain = [('invoice_id', '=', rec.id)]
                else:
                    domain = [('order_id', '=', rec.id)]
                for rec2 in clodoo.browseL8(
                    ctx, model2, clodoo.searchL8(
                        ctx, model2, domain)):
                    if model == 'res.partner':
                        print('    %s %4d %-32.32s %s %s' % (
                            model2, rec2.id, rec2.name, rec2.type,
                            get_agent_names(rec2.agents)))
                    elif model == 'account.invoice':
                        print('    %s %4d %-32.32s %s' % (
                            model2, rec2.id, rec2.name,
                            get_agent_names_line(rec2.agents)))
                    else:
                        print('    %s %4d %-32.32s %s' % (
                            model2, rec2.id, rec2.name,
                            get_agent_names_line(rec2.agents)))


def reset_email_admins(ctx):

    def reset_email_user(ctx, username):
        model = 'res.users'
        model2 = 'res.partner'
        email = {'vg7bot': 'vg7bot@vg7.it',
                 'vg7admin': 'noreply@vg7.it',
                 'zeroadm': 'noreply@zeroincombenze.it',}[username]
        ctr = 0
        ids = clodoo.searchL8(ctx, model,
                              [('login', '=', username)])
        if len(ids) == 0:
            print('No user %s found!' % username)
            return ctr
        for user in clodoo.browseL8(ctx, model, ids):
            partner_id = user.partner_id.id
            partner = clodoo.browseL8(ctx, model2, partner_id)
            if partner.email != 'noreply@vg7.it':
                clodoo.writeL8(ctx, model2, partner_id, {'email': email})
                ctr += 1
                print('User %s mail changed!' % username)
        return ctr
    ctr = 0
    ctr += reset_email_user(ctx, 'vg7bot')
    ctr += reset_email_user(ctx, 'vg7admin')
    ctr += reset_email_user(ctx, 'zeroadm')
    print('%d record updated' % ctr)


def create_commission_env(ctx):
    print('Set commission configuration to test')
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    ictr = 0
    uctr = 0
    model = 'sale.commission'
    COMMISSIONS = {
        'prov10': {'id': False, 'fix_qty': 10},
        'prov5': {'id': False, 'fix_qty': 5},
    }
    for commission in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [])):
        if commission.name in COMMISSIONS:
            COMMISSIONS[commission.name]['id'] = commission.id
    for commission in COMMISSIONS:
        vals = {
            'name': commission,
            'fix_qty': COMMISSIONS[commission]['fix_qty'],
        }
        if not COMMISSIONS[commission]['id']:
            id = clodoo.createL8(ctx, model, vals)
            COMMISSIONS[commission]['id'] = id
            ictr += 1
        else:
            clodoo.writeL8(ctx, model, COMMISSIONS[commission]['id'], vals)
            uctr += 1

    model = 'res.partner'
    AGENTS = {
        'Agente A': {'id': False, 'commission': COMMISSIONS['prov10']['id']},
        'Agente B': {'id': False, 'commission': COMMISSIONS['prov5']['id']},
    }
    for agent in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [])):
        if agent.name in AGENTS:
            AGENTS[agent.name]['id'] = agent.id
    for agent in AGENTS:
        vals = {
            'name': agent,
            'agent': True,
            'is_company': True,
            'customer': False,
            'supplier': True,
            'commission': AGENTS[agent]['commission'],
        }
        if not AGENTS[agent]['id']:
            id = clodoo.createL8(ctx, model, vals)
            AGENTS[agent]['id'] = id
            ictr += 1
        else:
            clodoo.writeL8(ctx, model, AGENTS[agent]['id'], vals)
            uctr += 1

    model = 'res.partner'
    CUSTOMERS = {
        env_ref(ctx, 'z0bug.res_partner_2'):
            {'agents': AGENTS['Agente A']['id'],},
        env_ref(ctx, 'z0bug.res_partner_4'):
            {'agents': AGENTS['Agente B']['id'],},
        env_ref(ctx, 'z0bug.res_partner_1'):
            {'agents': AGENTS['Agente A']['id'],},
    }
    for customer_id in CUSTOMERS:
        vals = {
            'agents': [(6, 0, [CUSTOMERS[customer_id]['agents']])],
            'customer': True,
        }
        clodoo.writeL8(ctx, model, customer_id, vals)
        uctr += 1

    model = 'product.product'
    for id in clodoo.searchL8(ctx, model, [('type', '=', 'service')]):
        clodoo.writeL8(ctx, model, id, {'commission_free': True})
        uctr += 1
    for id in clodoo.searchL8(ctx, model, [('default_code', '=', 'MISC')]):
        clodoo.writeL8(ctx, model, id, {'commission_free': False})
        uctr += 1

    print('%d records created, %d records updated' % (ictr, uctr))


def create_delivery_env(ctx):
    print('Set delivery configuration to test')
    if ctx['param_1'] == 'help':
        print('create_delivery_env')
        return
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    ctr = 0
    model = 'delivery.carrier'
    for carrier in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [], order='id')):
        vals = {
            'name': 'Consegna gratuita',
            'ddt_carrier_id': False,
            'transportation_method_id': env_ref(
                ctx,'l10n_it_ddt.transportation_method_DES'),
            'carriage_condition_id': env_ref(
                ctx,'l10n_it_ddt.carriage_condition_PF'),
            'note': 'Trasporto con mezzi propri'
        }
        clodoo.writeL8(ctx, model, carrier.id, vals)
        ctr += 1
        break
    model = 'stock.ddt.type'
    for ddt_type in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [], order='id')):
        vals = {
            'default_transportation_reason_id': env_ref(
                ctx,'l10n_it_ddt.transportation_reason_VEN'),
            'default_goods_description_id': env_ref(
                ctx,'l10n_it_ddt.goods_description_CAR'),
            'company_id': company_id,
        }
        clodoo.writeL8(ctx, model, ddt_type.id, vals)
        ctr += 1
        break
    model = 'res.partner'
    partner = clodoo.browseL8(ctx, model, env_ref(ctx, 'z0bug.res_partner_2'))
    vals = {
        'ddt_show_price': True,
        'goods_description_id': env_ref(
                ctx,'l10n_it_ddt.goods_description_SFU'),
        'carriage_condition_id': env_ref(
                ctx,'l10n_it_ddt.carriage_condition_PAF'),
        'transportation_method_id': env_ref(
                ctx,'l10n_it_ddt.transportation_method_COR'),
    }
    clodoo.writeL8(ctx, model, env_ref(ctx, 'z0bug.res_partner_2'), vals)
    ctr += 1
    print('%d record updated' % ctr)


def show_empty_ddt(ctx):
    print('Show DdT without lines')
    model = 'stock.picking.package.preparation'
    for ddt in clodoo.browseL8(ctx,model,clodoo.searchL8(ctx,model,[])):
        msg_burst('%s ...' % ddt.ddt_number)
        if not ddt.line_ids:
            print('DdT n.%s del %s (Id=%d) without lines' % (
                ddt.ddt_number, ddt.date, ddt.id))


def change_ddt_number(ctx):
    print('Change DdT number of validated record')
    model = 'stock.picking.package.preparation'
    ddt_id = raw_input('DdT id: ')
    if ddt_id:
        ddt_id = int(ddt_id)
        ddt = clodoo.browseL8(ctx, model, ddt_id)
        print('Current DdT number is: %s' % ddt.ddt_number)
        ddt_number = raw_input('New number: ')
        if ddt_number:
            clodoo.writeL8(ctx, model, ddt_id, {'ddt_number': ddt_number})
            ddt = clodoo.browseL8(ctx, model, ddt_id)
            print('DdT number of id %d changed with %s' % (ddt_id,
                                                           ddt.ddt_number))

def deduplicate_partner(ctx):
    print('Deduplicate partners')
    model = 'res.partner'
    prior_name = ''
    prior_partner = False
    for partner in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [('parent_id', '=', False)], order='name')):
        msg_burst('%s ...' % partner.name)
        if partner.vat:
            ids = clodoo.searchL8(ctx, model, [('vat', '=', partner.vat)])
            if len(ids) > 1:
                print('Found duplicate vat %s in %s records' % (
                    partner.vat, ids))
                for partner_id in ids:
                    dup = clodoo.browseL8(ctx, model, partner_id)
                    if dup.parent_id or dup.type in ('invoice', 'delivery'):
                        clodoo.writeL8(ctx, model, partner_id, {'vat': False})
                        print('Dropped vat from %s (%d)' % (
                            dup.name, partner_id))
        if partner.name and partner.name == prior_name:
            print('Found duplicate name %s as %d and %d' % (
                partner.name, partner.id, prior_partner.id))
            candidate = False
            if prior_partner.id > partner.id:
                if (prior_partner.activities_count == 0 and
                        len(prior_partner.invoice_ids) == 0):
                    candidate = prior_partner
            if not candidate and prior_partner.id < partner.id:
                if (partner.activities_count == 0 and
                        len(partner.invoice_ids) == 0):
                    candidate = partner
            if not candidate:
                if (partner.activities_count == 0 and
                        len(partner.invoice_ids) == 0):
                    candidate = partner
                elif (prior_partner.activities_count == 0 and
                        len(prior_partner.invoice_ids) == 0):
                    candidate = prior_partner
            if candidate:
                vals = {}
                if candidate.type == 'contact':
                    vals = {'active': False}
                vg7_id = False
                if candidate.vg7_id:
                    vg7_id = candidate.vg7_id
                    vals['vg7_id'] = False
                if vals:
                    print('Candidate to delete is %d' % candidate.id)
                    clodoo.writeL8(ctx, model, candidate.id, vals)
                if vg7_id:
                    vals = {'vg7_id': vg7_id}
                    if candidate == partner:
                        clodoo.writeL8(ctx, model, prior_partner.id, vals)
                        print('Assigned vg7_id %d to record %d' % (
                            vg7_id, prior_partner.id))
                    elif candidate == prior_partner:
                        clodoo.writeL8(ctx, model, partner.id, vals)
                        print('Assigned vg7_id %d to record %d' % (
                            vg7_id, partner.id))
        prior_name = partner.name
        prior_partner = partner


def print_model_synchro_data(ctx):
    print('Show XML data to build model for synchro module')
    model = ''
    while not model:
        model = raw_input('Model to buld: ')
        if not model:
            return
        rec = clodoo.searchL8(ctx, 'ir.model', [('model', '=', model)])
        if not rec:
            print('Model %s not found!' % model)
            continue
        model_id = rec[0]
        model_name = model.replace('.', '_')
        doc = ''
        template = '''
    <record forcecreate="1" id="%s_%s" model="synchro.channel.model.fields">
        <field name="name">%s</field>
        <field name="counterpart_name">%s</field>
        <field name="model_id" ref="%s"/>
    </record>
        '''
        key_name = 'name'
        for field in clodoo.browseL8(
            ctx, 'ir.model.fields', clodoo.searchL8(
                ctx, 'ir.model.fields', [('model_id', '=', model_id)])):
            if field.name == 'code':
                key_name = field.name
            elif field.name in TECH_FIELDS:
                continue
            doc += template % (model_name,
                               field.name,
                               field.name,
                               field.name,
                               model_name)
        doc = '''
    <record forcecreate="1" id="%s" model="synchro.channel.model">
        <field name="name">%s</field>
        <field name="field_uname">%s</field>
        <field name="search_keys">([%s],)</field>
        <field name="synchro_channel_id" ref="channel_vg7"/>
    </record>
        ''' % (model_name, model, key_name, key_name) + doc
        print(doc)


    def write_product(ctx, company_id):
        model = 'product.product'
        print('Write %s ..' % model)
        vg7_id = 1
        code = 'AA'
        name = 'Product Alpha'
        vals = {
            'company_id': company_id,
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
        }
        product_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        return product_id

    def write_sale_order(ctx, company_id, order_num,
                         vg7_partner_id, vg7_shipping_addr_id, product_a_id):
        model = 'sale.order'
        print('Write %s ..' % model)
        order_name = '%06d' % int(order_num)
        vals = {
            'company_id': company_id,
            'vg7_id': order_num,
            'partner_id': env_ref(ctx, 'z0bug.res_partner_2'),
            'state': 'sale',
            'name': order_name,
            'vg7_partner_id': vg7_partner_id,
            'partner_shipping_id': vg7_shipping_addr_id,
            'vg7_partner_shipping_id': vg7_partner_id + 100000000,
        }
        order_id = clodoo.executeL8(ctx,
                                    model,
                                    'synchro',
                                    vals)

        model = 'sale.order.line'
        print('Write %s ..' % model)
        vg7_id = int(order_num) * 10
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_order_id': order_num,
            'partner_id': env_ref(ctx, 'z0bug.res_partner_2'),
            'name': 'Product Alpha',
            'product_id': product_a_id,
            'vg7_product_id': 1,
            'price_unit': 10.50,
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        id = clodoo.executeL8(ctx,
                              'sale.order',
                              'commit',
                              order_id)
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    clodoo.executeL8(ctx,
                     'ir.model.synchro.cache',
                     'set_loglevel',
                     0,
                     'debug')
    clodoo.executeL8(ctx,
                     'ir.model.synchro.cache',
                     'clean_cache',
                     0,
                     None, None, 5)
    ord_model = 'sale.order'
    partner_model = 'res.partner'
    order_num = ctx['param_1'] or '1234'
    partner_id = env_ref(ctx, 'z0bug.res_partner_2')
    vg7_partner_id = 2
    vals = {
        'vg7_id': vg7_partner_id,
    }
    clodoo.writeL8(ctx, partner_model, partner_id, vals)
    print('- sending partner ...')
    vals = {
        'vg7_id': vg7_partner_id,
        'city': 'S. Secondo Pinerolo',
        'codice_destinatario': 'ABCDEFG',
        'name': 'Agro Latte Due s.n.c.',
        'zip': '10060',
        'mobile': '',
        'electronic_invoice_subjected': True,
        'vg7:region': 'TORINO',
        'vg7:region_id': 11,
        'id': partner_id,
        'phone': '+39 0121555123',
        'street': 'Via II Giugno, 22',
        'is_company': True,
        'vg7:country_id': 'Italia',
        'customer': True,
        'email': 'agrolait@libero.it',
        'vat': 'IT02345670018',
        'fiscalcode': ''
    }
    sync_partner_id = clodoo.executeL8(ctx,
                                       partner_model,
                                       'synchro',
                                       vals)
    if sync_partner_id != partner_id:
        raise IOError('Invalid partner ID received')
    print('- sending shipping address ...')
    vals = {
        'customer': False,
        'city': 'Torino',
        'name': 'Magazzino Agro Latte Due s.n.c.',
        'zip': '10126',
        'mobile': '',
        'vg7:region': 'TORINO',
        'vg7:region_id': 11,
        # 'id': 1852,
        'phone': '',
        'street': 'FERMO DEPOSITO GLS',
        'vg7:country_id': 'Italia',
        'type': 'delivery',
        'email': 'agrolait@libero.it',
        'vg7:id': 2
    }
    vg7_shipping_addr_id = sync_partner_id = clodoo.executeL8(ctx,
                                                              partner_model,
                                                              'synchro',
                                                              vals)
    product_a_id = write_product(ctx, company_id)
    write_sale_order(ctx, company_id, order_num,
                         vg7_partner_id, vg7_shipping_addr_id, product_a_id)


def test_synchro_vg7(ctx):
    print('Test synchronization VG7 module')
    if ctx['param_1'] == 'help':
        print('test_synchro_vg7 [conai]')
        return
    test_conai = False
    if ctx['param_1']:
        test_conai = True

    L_NUM_FATT1 = 'FAT/2020/0001'
    L_NUM_FATT2 = 'FAT/2019/0006'
    X_NUM_DDT = '1234'
    X_NUM_ORDER = '1234'
    L_NUM_ORDER = 'SO002'

    TNL_TABLE = {
        'account.invoice': '',
        'account.invoice.line': '',
        'account.payment.term': 'payments',
        'account.tax': 'tax_codes',
        'product.product': 'products',
        'product.template': '',
        'product.uom': 'ums',
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
    if test_conai:
        TNL_TABLE['italy.conai.product.category'] = ''
        TNL_TABLE['italy.conai.partner.category'] = ''

    BORDER_TABLE = {
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
        'account.tax': {
            'aliquota': 'amount',
            'code': 'description',
            'description': False,
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
        'res.country' : {
            'description': False,
        },
        'res.country.state': {
            'description': 'name',
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
            'data_emissione': False,
            'data_ritiro': False,
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
        'country_id': 'res.country',
        'conai_category_id': 'italy.conai.product.category',
        'goods_description_id': 'stock.picking.goods_description',
        'invoice_id': 'account.invoice',
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
    }
    ctx['ctr'] = 0

    def init_test(ctx, company_id):
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
        # Set message note
        ctx['company_note'] = 'Si prega di controllate i dati entro le 24h.'
        clodoo.writeL8(ctx, 'res.company', company_id,
                        {'sale_note': ctx['company_note']})
        # Configure VG7 channel
        # Wrong method. Will be set forward, in order to test cache
        model = 'synchro.channel'
        clodoo.writeL8(ctx, model, clodoo.searchL8(
            ctx, model, []), {
            'method': 'JSON',
            'exchange_path': '/opt/odoo/clodoo/',
            'trace': True,
        })
        # Delete file csv & unlink external ids
        for model in TNL_TABLE:
            ext_model = TNL_TABLE[model]
            if ext_model:
                file_csv = '/opt/odoo/clodoo/%s.csv' % ext_model
                if os.path.isfile(file_csv):
                    os.unlink(file_csv)
            if not model.startswith('res.partner.'):
                unlink_vg7(model)
        model = 'sale.order'
        delete_record(ctx, model, [('name', '=', '2187')],
                      action='action_cancel')
        # Se partner (person) name
        model = 'res.partner'
        partner_MR_ids = clodoo.searchL8(ctx, model,
                                         [('name', 'like', 'Rossi')])
        if partner_MR_ids:
            for id in partner_MR_ids:
                partner = clodoo.browseL8(ctx, model, id)
                if partner.split_mode != 'LF':
                    clodoo.writeL8(ctx, model, id,
                                   {'splitmode': 'LF',
                                    'name': 'Rossi Mario'})
        delete_record(
            ctx, model, [('name', '=', 'La Romagnola srl')],
            childs='child_ids')
        ctx['partner_MR_ids'] = partner_MR_ids
        ids = clodoo.searchL8(ctx, model, [('name', 'like', 'Delta')])
        for id in ids:
            clodoo.writeL8(ctx, model, id, {'city': False, 'state_id': False})
        clodoo.writeL8(
            ctx, model, env_ref(
                ctx, 'base.res_partner_1'),
            {'name': 'ASUSTek', 'supplier': True, 'customer': False,
             'country_id': env_ref(ctx, 'base.tw')})
        clodoo.writeL8(
            ctx, model, env_ref(
                ctx, 'base.res_partner_2'),
            {'name': 'Agrolait', 'supplier': False, 'customer': True,
             'country_id': env_ref(ctx, 'base.be')})
        clodoo.writeL8(
            ctx, model, env_ref(
                ctx, 'base.res_partner_3'),
            {'name': 'China Export', 'supplier': True, 'customer': False,
             'country_id': env_ref(ctx, 'base.cn')})
        clodoo.writeL8(
            ctx, model, env_ref(
                ctx, 'base.res_partner_4'),
            {'name': 'Delta PC', 'supplier': False, 'customer': True,
             'country_id': env_ref(ctx, 'base.us')})

        # Productc (MISC)
        model = 'product.product'
        product_x_ids = clodoo.searchL8(ctx, model,
                                        [('default_code', '=', 'MISC')])
        if not product_x_ids:
            product_x_ids = clodoo.searchL8(ctx, model,
                                            [('default_code', 'like', 'MISC')])
        if product_x_ids:
            ctx['test_product_x_id'] = product_x_ids[0]
        else:
            ctx['test_product_x_id'] = clodoo.searchL8(
                ctx, model, [])[0]
        vals = {'vg7_id': 99,
                'weight': 1.0}
        if test_conai:
            conai_category_id = clodoo.searchL8(
                ctx, 'italy.conai.product.category', [('code', '=', 'PLA')])[0]
            vals['conai_category_id'] = conai_category_id
        clodoo.writeL8(ctx, model, ctx['test_product_x_id'], vals)
        store_id(ctx, model, ctx['test_product_x_id'], 99)
        id = clodoo.browseL8(
            ctx, model, ctx['test_product_x_id']).product_tmpl_id.id
        clodoo.writeL8(ctx, 'product.template', id, {'vg7_id': 99})
        store_id(ctx, model, id, 99)
        delete_record(
            ctx, model, [('vg7_id', '=', 3)])
        if test_conai:
            conai_category_id = clodoo.searchL8(
                ctx, 'italy.conai.product.category',[('code', '=', 'L')])[0]
            for code in ('AA', 'BB'):
                vals = {'conai_category_id': conai_category_id,
                        'weight': 1.0}
                id = clodoo.searchL8(
                    ctx, model, [('code', '=', code)])[0]
                clodoo.writeL8(ctx, model, id, vals)
        # Tax
        model = 'account.tax'
        for id in clodoo.searchL8(ctx, model, [('description', '=', '22v')]):
            clodoo.writeL8(ctx, model, id, {'name': 'IVA 22%'})

        # Delete sale order
        model = 'sale.order'
        delete_record(
            ctx, model, [('name', '=', L_NUM_ORDER)], action='action_cancel')
        set_sequence(ctx, [('code', '=', 'sale.order')], 2)

        # Delete invoice
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
            ctx,[('prefix', 'like', 'FAT/%')], 1, company_id=company_id)

        # Delete DdT
        model = 'stock.picking.package.preparation'
        delete_record(
            ctx, model, [('ddt_number', '=', X_NUM_DDT)],
            company_id=company_id)

        # Delete shipping address
        model = 'res.partner'
        delete_record(
            ctx, model, [('name', 'like', 'Partner A%'),
                         ('type', '=', 'contact')], childs='child_ids')
        delete_record(
            ctx, model, [('vg7_id', '=', 1001)])

        # Delete other records
        model = 'res.country.state'
        delete_record(ctx, model, [('name', '=', '(TO)')])
        model = 'stock.picking.goods_description'
        delete_record(ctx, model, [('name', '=', 'BANCALI')])
        model = 'account.payment.term'
        delete_record(ctx, model, [('vg7_id', 'in', [10, 30, 3060])])
        return ctx

    def write_file_2_pull(ext_model, vals, mode=None):
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
        with open('/opt/odoo/clodoo/%s.csv' % ext_model, mode) as fd:
            fd.write(data)

    def rm_file_2_pull(ext_model):
        if os.path.isfile('/opt/odoo/clodoo/%s.csv' % ext_model):
            os.unlink('/opt/odoo/clodoo/%s.csv' % ext_model)

    def compare(rec_value, ext_ref, vals, model, check_fct):
        if check_fct == 'nounknown':
            return not rec_value.startswith('Unknown')
        return rec_value == vals[ext_ref]

    def general_check(ctx, model, id, vals):
        if not id or id < 1:
            raise IOError('!!Syncro %s Failed (%d)!' % (model, id))
        if 'company_id' in vals:
            company_id = vals['company_id']
        else:
            company_id = env_ref(ctx, 'z0bug.mycompany')
        if 'vg7:id' in vals and 'vg7_id' not in vals:
            vals['vg7_id'] = vals['vg7:id']
            del vals['vg7:id']
        if 'oe8:id' in vals and 'oe8_id' not in vals:
            vals['oe8_id'] = vals['oe8:id']
            del vals['oe8:id']
        rec = clodoo.browseL8(ctx, model, id)
        if model == 'res.partner':
            if vals.get('vg7_id') == 17:
                ctx['ctr'] += 1
                if rec.id not in ctx['partner_MR_ids']:
                    raise IOError('!!Invalid id of %s!' % model)
                vals['name'] = 'Rossi Mario'
                vals['individual'] = True
            if rec.type == 'contact':
                vals['is_company'] = True
        elif model == 'sale.order':
            vals['vg7:order_number'] = False
            if 'partner_id' in vals and 'vg7:customer_id' in vals:
                del vals['partner_id']
            if ('partner_shipping_id' in vals and
                    'vg7:customer_shipping_id' in vals):
                del vals['partner_shipping_id']
        elif model == 'account.invoice':
            ctx['ctr'] += 1
            if rec.number and rec.number.startswith('Unknown'):
                raise IOError('!!Invalid field %s.number!' % model)
        for ext_ref in vals:
            if vals[ext_ref] == '':
                continue
            ref_model = False
            if ext_ref in ('vg7:shipping', 'vg7:billing', 'vg7:name', 'id'):
                continue
            elif ext_ref in ('vg7_id', 'vg7:id', 'oe8:id'):
                if (isinstance(vals[ext_ref], basestring) and
                        vals[ext_ref].isdigit()):
                    vals[ext_ref] = int(vals[ext_ref])
                if getattr(rec, 'vg7_id') != vals[ext_ref]:
                    raise IOError('!!Invalid field %s.%s!' % (model, 'vg7_id'))
                ctx['ctr'] += 1
                continue
            elif (ext_ref.startswith('vg7:') or
                  ext_ref.startswith('vg7_') or
                  ext_ref.startswith('oe8:')):
                loc_name = ext_ref[4:]
                if not ext_ref.startswith('oe8:') and model in BORDER_TABLE:
                    if (ext_ref.startswith('vg7:') or
                            ext_ref.startswith('oe8:')):
                        if loc_name in BORDER_TABLE[model]:
                            loc_name = BORDER_TABLE[model][loc_name]
                    else:
                        if ext_ref in BORDER_TABLE[model]:
                            loc_name = BORDER_TABLE[model][ext_ref]
                if not loc_name:
                    continue
                if (loc_name in ('electronic_invoice_subjected',
                                 'codice_destinatario') and
                        vals['vg7_id'] > 100000000):
                    ctx['ctr'] += 1
                    continue
            else:
                loc_name = ext_ref
            if isinstance(loc_name, (tuple, list)):
                check_fct = loc_name[1]
                loc_name = loc_name[0]
            else:
                check_fct = False
            if (loc_name.endswith('_id') and
                    isinstance(vals[ext_ref], basestring) and
                    vals[ext_ref].isdigit()):
                vals[ext_ref] = int(vals[ext_ref])
            rec_value = False
            if not ext_ref.startswith('oe8:'):
                if model == 'res.partner':
                    if loc_name == 'name' and rec.type != 'contact':
                        if (rec.type == 'delivery' and
                                vals['vg7_id'] == 100001001 and
                                rec.name == 'Another Address'):
                            ctx['ctr'] += 1
                            continue
                        if rec.name and rec.name != 'Partner AA':
                            raise IOError(
                                '!!Invalid field %s.%d.name!' % (model, id))
                        else:
                            ctx['ctr'] += 1
                            continue
                    elif loc_name == 'vat':
                        if getattr(rec, loc_name):
                            rec_value = getattr(rec, loc_name)[2:]
                        else:
                            rec_value = getattr(rec, loc_name)
                    elif loc_name == 'street':
                        rec_value = getattr(rec, loc_name)
                        vals[ext_ref] = vals[ext_ref] + ', 13'
            if rec_value:
                # if rec_value != vals[ext_ref]:
                if not compare(rec_value, ext_ref, vals, model, check_fct):
                        raise IOError(
                        '!!Invalid field %s.%d.%s!' % (
                            model, id, loc_name))
                ctx['ctr'] += 1
                continue
            if ((loc_name == 'tax_id' and model == 'sale.order.line') or
                  (loc_name == 'invoice_line_tax_ids' and
                   model == 'account.invoice.line')):
                id = clodoo.searchL8(ctx, 'account.tax',
                                     [('description', '=', vals[ext_ref]),
                                      ('company_id', '=', company_id)])
                if not rec[loc_name] or id != [x.id for x in rec[loc_name]]:
                    raise IOError('!!Invalid VAT code!')
                continue
            elif ext_ref == 'state':
                rec_value = getattr(rec, loc_name)
                vals[ext_ref] = 'draft'
            elif ext_ref == 'vg7:esonerato_fe':
                rec_value = not getattr(rec, loc_name)
                vals[ext_ref] = os0.str2bool(vals[ext_ref], None)
            else:
                try:
                    rec_value = getattr(rec, loc_name).id
                    if (ext_ref != 'vg7_id' and
                            (ext_ref.startswith('vg7_') or
                             ext_ref.startswith('vg7:'))):
                        ckstr = False
                        if loc_name in TABLE_OF_FIELD:
                            ref_model = TABLE_OF_FIELD[loc_name]
                            if TABLE_OF_FIELD[loc_name] in BORDER_TABLE:
                                rec_value = BORDER_TABLE[
                                    ref_model]['LOC'].get(rec_value,rec_value)
                            ckstr = True
                        elif loc_name == 'parent_id':
                            if model in BORDER_TABLE:
                                rec_value = BORDER_TABLE[
                                    model]['LOC'].get(rec_value,rec_value)
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
                            if len(ids) == 1:
                                if ref_model in BORDER_TABLE:
                                    vals[ext_ref] = BORDER_TABLE[
                                        ref_model]['LOC'].get(ids[0],
                                                              ids[0])
                                else:
                                    vals[ext_ref] = ids[0]
                except BaseException:
                    rec_value = getattr(rec, loc_name)
                    if model == 'product.uom' and rec_value == 'Unità':
                        rec_value = 'Unit(s)'
            # if rec_value != vals[ext_ref]:
            if not compare(rec_value, ext_ref, vals, model, check_fct):
                raise IOError(
                    '!!Invalid field %s.%d.%s!' % (model, id, loc_name))
            ctx['ctr'] += 1
            if (ext_ref == 'vg7:customer_shipping_id' and
                    vals[ext_ref] != vals['vg7:customer_id']):
                ids = clodoo.searchL8(ctx, 'res.partner',
                                      [('vg7_id', '=', rec_value + 100000000)])
                part = False
                if ids:
                    part = clodoo.browseL8(ctx, 'res.partner', ids[0])
                if (not part or
                        not part.parent_id or
                        part.type != 'delivery'):
                    raise IOError(
                        '!!Invalid shipping address %d type!' % rec_value)
                ctx['ctr'] += 1

    def store_id(ctx, model, id, vg7_id):
        if model not in BORDER_TABLE:
            BORDER_TABLE[model] = {}
        if 'EXT' not in BORDER_TABLE[model]:
            BORDER_TABLE[model]['LOC'] = {}
            BORDER_TABLE[model]['EXT'] = {}
        if isinstance(vg7_id, basestring):
            BORDER_TABLE[model]['LOC'][id] = int(vg7_id)
            BORDER_TABLE[model]['EXT'][int(vg7_id)] = id
        else:
            BORDER_TABLE[model]['LOC'][id] = vg7_id
            BORDER_TABLE[model]['EXT'][vg7_id] = id

    def get_vg7id_from_id(ctx, model, id):
        return clodoo.browseL8(ctx, model, id).vg7_id

    def get_id_from_vg7id(ctx, model, vg7_id, name=None):
        name = name or 'vg7_id'
        ids = clodoo.searchL8(ctx, model, [(name, '=', vg7_id)])
        if ids:
            return  ids[0]
        return -1

    def jacket_vals(vals):
        for nm in vals.copy():
            if not nm.startswith('vg7:'):
                vals['vg7:%s' % nm] = vals[nm]
                del vals[nm]
        return vals

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

    def delete_record(ctx, model, domain, multi=False, action=None,
                      childs=None, company_id=False):
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
                        clodoo.executeL8(ctx, model, act, ids)
            if childs:
                for parent in clodoo.browseL8(ctx, model, ids):
                    for rec in parent[childs]:
                        clodoo.unlinkL8(ctx, model, rec.id)
            clodoo.unlinkL8(ctx, model, ids)

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

    def check_country(ctx, country_id, vals):
        general_check(ctx, 'res.country', country_id, vals)

    def check_country_state(ctx, country_state_id, vals):
        general_check(ctx, 'res.country.state', country_state_id, vals)

    def write_country(ctx, vg7_id=None, code=None, name=None):
        model = 'res.country'
        print('Write %s ..' % model)

        vg7_id = vg7_id or 39
        code = code or 'IT'
        name = name or 'Italia'
        vals = {
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
        }
        country_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, country_id, vg7_id)
        check_country(ctx, country_id, vals)

        model = 'res.country.state'
        print('Write %s ..' % model)

        vg7_id = 11
        code = 'TO'
        name = 'Torino'
        vals = {
            # 'country_id': country_id,
            'vg7:code': code,
            'vg7:description': name,
            'vg7:id': vg7_id,
        }
        country_state_id = clodoo.executeL8(ctx,
                                            model,
                                            'synchro',
                                            vals)
        store_id(ctx, model, country_state_id, vg7_id)
        check_country_state(ctx, country_state_id, vals)

        vg7_id = 2
        code = 'MI'
        name = 'Milano'
        vals = {
            'vg7:code': code,
            'vg7:description': name,
            'vg7_id': vg7_id,
        }
        country_state_id = clodoo.executeL8(ctx,
                                            model,
                                            'synchro',
                                            vals)
        store_id(ctx, model, country_state_id, vg7_id)
        check_country_state(ctx, country_state_id, vals)

        return vg7_id

    def check_tax(ctx, vat_id, vals):
        general_check(ctx, 'account.tax', vat_id, vals)

    def write_tax(ctx, vg7_id=None, code=None, name=None, only_amount=None):
        model = 'account.tax'
        print('Write %s ..' % model)

        vg7_id = vg7_id or 22
        code = code or '22v'
        name = name or '22%'
        if only_amount:
            vals = {
                'vg7:id': vg7_id,
                'vg7:aliquota': 22,
            }
        else:
            vals = {
                'vg7:id': vg7_id,
                'vg7:code': code,
                'vg7:description': name,
                'vg7:aliquota': 22,
            }
        vat_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, vat_id, vg7_id)
        if only_amount:
            vals['description'] = code
            vals['name'] = 'IVA 22%'
        check_tax(ctx, vat_id, vals)
        return vg7_id

    def check_payment(ctx, payment_id, vals):
        general_check(ctx, 'account.payment.term', payment_id, vals)

    def write_payment(ctx, vg7_id=None, code=None, name=None):
        model = 'account.payment.term'
        print('Write %s ..' % model)

        vg7_id = vg7_id or 3060
        if vg7_id == 30:
            code = code or '30'
            name = name or 'RiBA 30GG/FM'
        else:
            code = code or '31'
            name = name or 'RiBA 30/60 GG/FM'
        vals = {
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
        }
        vat_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, vat_id, vg7_id)
        check_payment(ctx, vat_id, vals)
        return vg7_id

    def check_conai(ctx, vat_id, vals):
        general_check(ctx, 'italy.conai.product.category', vat_id, vals)

    def write_conai(ctx, vg7_id=None, code=None, name=None):
        model = 'italy.conai.product.category'
        print('Write %s ..' % model)

        vg7_id = vg7_id or 1
        code = code or 'CA'
        name = name or 'Carta'
        vals = {
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
            'vg7:prezzo_unitario': 35,
        }
        vat_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
        store_id(ctx, model, vat_id, vg7_id)
        check_conai(ctx, vat_id, vals)
        return vg7_id

    def check_product(ctx, product_id, vals):
        general_check(ctx, 'product.product', product_id, vals)

    def check_product_template(ctx, vg7_id, vals):
        model = 'product.template'
        tmpl_id = get_id_from_vg7id(ctx, model, vg7_id)
        store_id(ctx, model, tmpl_id, vg7_id)
        general_check(ctx, model, tmpl_id, vals)
        return tmpl_id

    def write_product(ctx, company_id, vg7_id=None, code=None, name=None):
        model = 'product.product'
        print('Write %s ..' % model)
        vg7_id = vg7_id or 1
        code = code or 'AA'
        name = name or 'Product Alpha'
        vals = {
            # 'company_id': company_id,
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
        }
        if test_conai:
            vals['vg7:conai_id'] = 1
        product_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, product_id, vg7_id)
        tmpl_id = check_product_template(ctx, vg7_id, vals)
        vals['product_tmpl_id'] = tmpl_id
        check_product(ctx, product_id, vals)
        return vg7_id

    def check_partner(ctx, partner_id, vals):
        general_check(ctx, 'res.partner', partner_id, vals)

    def write_partner(ctx, company_id, vg7_id=None, name=None,
                      wrong_data=None):
        model = 'res.partner'
        vg7_id = vg7_id or 7
        if vg7_id == 2:
            # Test partner with its data all filled
            partner = clodoo.browseL8(
                ctx, model, env_ref(ctx, 'z0bug.res_partner_2'))
            vals = {
                'vg7_id': vg7_id,
                'id': env_ref(ctx, 'z0bug.res_partner_2'),
                'vg7:company': partner.name,
                'goods_description_id': env_ref(
                    ctx, 'l10n_it_ddt.goods_description_SFU'),
                'carriage_condition_id': env_ref(
                    ctx, 'l10n_it_ddt.carriage_condition_PAF'),
                'transportation_method_id': env_ref(
                    ctx, 'l10n_it_ddt.transportation_method_COR'),
                'electronic_invoice_subjected': True,
            }
        elif vg7_id == 17:
            vals = {
                'vg7_id': vg7_id,
                'vg7:name': 'Mario',
                'vg7:surename': 'Rossi',
            }
        else:
            name = name or 'Partner A'
            vals = {
                'vg7:id': vg7_id,
                'vg7:company': name,
                'vg7:street': 'Via Porta Nuova',
                'vg7:street_number': '13',
                'vg7:postal_code': '10100',
                'vg7:city': 'Torino',
                'vg7:country_id': 'Italia',
                'vg7:esonerato_fe': '1',
                'vg7:piva': '00385870480',
                'vg7:payment_id': 30,
            }
            if wrong_data:
                vals['vg7:region'] = '(TO)'
            else:
                vals['vg7:region'] = 'TORINO'
                vals['vg7:region_id'] = 11
        print('Write %s (%s) ..' % (
            model, vals.get('vg7:company') or vals['vg7:surename']))
        partner_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        store_id(ctx, model, partner_id, vg7_id)
        check_partner(ctx, partner_id, vals)
        return vg7_id

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
        print('Write %s (full pull) ..' % model)
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
        check_partner(ctx, partner_id, vals)

        for rectype in ('delivery', 'invoice'):
            rec_id, rec_vals = prepare_vals(
                ctx, model, partner_id, rectype, name, vg7_id, 107,
                vals_shipping, vals_billing, wrong_data)
            if rec_id:
                check_partner(ctx, rec_id, rec_vals)
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
        check_partner(ctx, shipping_id, vals)
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
        check_partner(ctx, supplier_id, vals)
        return supplier_id

    def check_uom(ctx, uom_id, vals):
        general_check(ctx, 'product.uom', uom_id, vals)

    def write_uom(ctx, vg7_id=None, code=None, name=None):
        model = 'product.uom'
        print('Write %s ..' % model)

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
        print('Write %s ..' % model)

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
        print('Write %s ..' % model)

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
        print('Write %s ..' % model)
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

        print('Write %s ..' % model)
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
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_sale_order_line(ctx, line_id, vals)

        if not state or state == 'draft' or newprod:
            print('Write %s ..' % model)
            vg7_id = vg7_order_id * 100 + 2
            vals = {
                'vg7_id': vg7_id,
                'vg7_order_id': vg7_order_id,
                'vg7_partner_id': get_vg7id_from_id(ctx, 'res.partner',
                                                    partner_id),
                'name': 'Product MISC',
                # 'vg7:product_id': get_vg7id_from_id(
                #     ctx, 'product.product', ctx['test_product_x_id']),
                'vg7_product_id': get_vg7id_from_id(
                    ctx, 'product.product', ctx['test_product_x_id']),
                'price_unit': 12.34,
                'tax_id': '22v',
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
        print('Write %s ..' % model)

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
        print('Write %s ..' % model)
        vg7_invoice_id = vg7_id
        vg7_id = vg7_invoice_id * 200
        vals = {
            # 'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product Alpha',
            'vg7_product_id': ctx['vg7_id_product_a'],
            'price_unit': 10.50,
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_invoice_line(ctx, line_id, vals)

        print('Write %s ..' % model)
        vg7_id = vg7_invoice_id * 200 + 1
        # Field partner_id does not exit: test to avoid crash
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product Beta',
            'vg7_product_id': ctx['vg7_id_product_b'],
            'price_unit': 25.50,
            'invoice_line_tax_ids': '22v',
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        store_id(ctx, model, line_id, vg7_id)
        check_invoice_line(ctx, line_id, vals)

        if not state or state == 'draft':
            print('Write %s ..' % model)
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
                              invoice_id )
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)
        ctx['ctr'] += 1
        rec = clodoo.browseL8(ctx, 'account.invoice', invoice_id)
        if state:
            detail_ctr = 2
            if rec.payment_term_id.riba:
                detail_ctr += 1
            if test_conai:
                detail_ctr += 1
        else:
            detail_ctr = 3
        if state:
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
            ctx['ctr'] += 1
            if len(rec['invoice_line_ids']) != detail_ctr:
                raise IOError('!!Invalid # of details!')
            ctx['ctr'] += 1
        else:
            if len(rec['invoice_line_ids']) != detail_ctr:
                raise IOError('!!Invalid # of details!')
            ctx['ctr'] += 1
        if rec.payment_term_id != rec.partner_id.property_payment_term_id:
            raise IOError('!!Invalid payment term!')
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
        print('Write %s ..' % model)
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
            'vg7:data_emissione': '2019-12-12',
            'vg7:data_ritiro': '2019-12-13',
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
        print('Write %s ..' % model)
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
        if test_conai:
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

    def check_2_user(ctx, user_id, vals):
        general_check(ctx, 'res.users', user_id, vals)

    def write_2_user(ctx, oe8_id=None, login=None, name=None):
        model = 'res.users'
        print('Write %s ..' % model)

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
        print('Write %s ..' % model)

        oe8_id = oe8_id or 1
        partner_id = partner_id or env_ref(ctx, 'z0bug.partner_mycompany')
        clodoo.writeL8(ctx, 'res.partner', partner_id, {'oe8_id': 1001})
        name = clodoo.browseL8(ctx, 'res.partner', partner_id).name
        vals = {
            'oe8:id': oe8_id,
            # 'oe8:partner_id': 1001,
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

    def check_2_partner(ctx, partner_id, vals):
        general_check(ctx, 'res.partner', partner_id, vals)

    def write_2_partner(ctx, oe8_id=None, name=None, wrong_data=None):
        model = 'res.partner'
        print('Write %s ..' % model)
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
        check_partner(ctx, partner_id, vals)
        return oe8_id

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    ctx = init_test(ctx, company_id)

    # Repeat 2 times to check correct synchronization
    write_country(ctx)
    write_country(ctx, vg7_id='39')

    # Repeat 2 times to check correct synchronization
    write_tax(ctx, only_amount=True)
    write_tax(ctx)

    # Repeat 2 times to check correct synchronization
    write_payment(ctx)
    write_payment(ctx)
    write_payment(ctx, vg7_id=30)

    if test_conai:
        write_conai(ctx)
        write_conai(ctx)

    # Repeat 2 times to check correct synchronization
    vg7_id_product_a = write_product(ctx, company_id)
    vg7_id_product_a = write_product(ctx, company_id, vg7_id='1')

    vg7_id_product_b = write_product(ctx, company_id,
                                     vg7_id=2, code='BB', name='Product Beta')
    ctx['vg7_id_product_a'] = vg7_id_product_a
    ctx['vg7_id_product_b'] = vg7_id_product_b

    # Repeat 2 times to check correct synchronization
    write_partner(ctx, company_id, wrong_data=True)
    write_partner(ctx, company_id)
    write_partner(ctx, company_id, vg7_id=17)
    # Partner for sale order & invoice
    write_partner(ctx, company_id, vg7_id=2)
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
                       'exchange_path': '/opt/odoo/clodoo/',
                       'trace': True,
                   })

    # Repeat 2 times with different state
    write_invoice(ctx, company_id)
    write_invoice(ctx, company_id, state='open')
    # Repeat 2 times with different state
    write_ddt(ctx, company_id)
    write_ddt(ctx, company_id, shipping_id=107)

    # Interactive test

    model = 'res.partner'
    ext_model = 'customers'
    vg7_id = 7
    vals = {
        'id': vg7_id,
        'company': 'Partner AAA',
        'street': 'V.le delle Rose',
        'street_number': '13',
        'postal_code': '20100',
        'city': 'Milano',
        'region': 'Milano',
        'region_id': 2,
        'email': '',
        'piva': '',
        'cf': '',
        'telephone': '+39 555 999999'
    }
    write_file_2_pull(ext_model, vals)
    print('Go to web page, menù customer, partner "AAA"')
    print('then click on synchronize button')
    dummy = raw_input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    if not dummy.startswith('n') and not dummy.startswith('N'):
        check_partner(
            ctx, get_id_from_vg7id(ctx, model, vg7_id), jacket_vals(vals))

    model = 'res.partner'
    ext_model = 'suppliers'
    ext_model = 'suppliers'
    vg7_id = 14
    vals = {
        'id': vg7_id,
        'company': 'Delta Quattro s.r.l.',
        'postal_code': '80010',
        'city': 'Quarto Flegreo',
        'region': 'Napoli',
    }
    write_file_2_pull(ext_model, vals)
    print('Go to web page, menù supplier, partner "Delta 4"')
    print('then click on synchronize button')
    dummy = raw_input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    if not dummy.startswith('n') and not dummy.startswith('N'):
        id = get_id_from_vg7id(ctx, model, vg7_id, name='vg72_id')
        vals = jacket_vals(vals)
        vals['vg72_id'] = vals['vg7:id']
        del vals['vg7:id']
        check_partner(ctx, id, vals)

    model = 'product.product'
    ext_model = 'products'
    vg7_id = 1
    vals = {
        'id': vg7_id,
        'code': 'AAA',
        'description': 'Product AAA',
    }
    write_file_2_pull(ext_model, vals)
    print('Go to web page, menù product, product "AA"')
    print('then click on synchronize button')
    dummy = raw_input('Did you synchronize %s record (Yes,No)? ' % ext_model)
    if not dummy.startswith('n') and not dummy.startswith('N'):
        check_product(
            ctx, get_id_from_vg7id(ctx, model, vg7_id), jacket_vals(vals))

    vg7_id = 3
    vals = {
        'id': vg7_id,
        'code': 'CC',
        'description': 'Product CC',
    }
    write_file_2_pull(ext_model, vals)
    write_sale_order(ctx, company_id, state='sale', newprod=True)
    check_product(
        ctx, get_id_from_vg7id(
            ctx, 'product.product', vg7_id), jacket_vals(vals))

    model = 'res.partner.shipping'
    ext_model = 'customers_shipping_addresses'
    vg7_id = 1001
    vals = {
        'customer_shipping_id': vg7_id,
        'customer_id': 7,
        'country_id': 39,
        'company': 'Another Address',
    }
    write_file_2_pull(ext_model, vals)
    write_ddt(ctx, company_id, shipping_id=vg7_id)
    vals['id'] = vals['customer_shipping_id'] + 100000000
    del vals['customer_shipping_id']
    check_partner(
        ctx, get_id_from_vg7id(
            ctx, 'res.partner', vg7_id + 100000000), jacket_vals(vals))

    print('*** Starting trigger test ***')

    model = 'account.payment.term'
    print('Write %s ..' % model)
    ext_model = 'payments'
    vals = {
        'id': 25,
        'description': 'Paypal',
        'code': 'PP',
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.country'
    print('Write %s ..' % model)
    ext_model = 'countries'
    vals = {
        'code': 'IT',
        'name': 'Italia',
        'id': 39,
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.country.state'
    print('Write %s ..' % model)
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

    model = 'res.partner'
    print('Write %s ..' % model)
    ext_model = 'customers'
    state_vals = vals
    name = 'La Romagnola srl'
    vg7_id = 44
    vals_billing = {
        'id': vg7_id,
        'billing_city': 'Imola',
        'billing_codice_univoco': 'X12345Y',
        'billing_company': name,
        'billing_postal_code': '40026',
        'billing_telephone2': '',
        'billing_esonerato_fe': 0,
        'billing_region': 'BOLOGNA',
        'billing_region_id': 54,
        'billing_telephone': '0542 640502',
        'billing_street': 'Via Emilia',
        'billing_street_number': '13',
        'billing_country': 'Italia',
        'billing_country_id': 39,
        'billing_email': 'antoniomaria@laromagnola.it',
        'billing_piva': '01598041208',
        'billing_cf': '02151140361',
    }
    write_file_2_pull(ext_model, vals_billing)
    ext_model = 'customers_shipping_addresses'
    vg7_id2 = 2
    vals_shipping = {
        'customer_shipping_id': vg7_id2,
        'customer_id': vg7_id,
        'shipping_city': 'Imola',
        'shipping_company': name,
        'shipping_postal_code': '40026',
        'shipping_region': 'BOLOGNA',
        'shipping_region_id': 54,
        'shipping_street': 'Piazza Maggiore',
        'shipping_street_number': '13',
        'shipping_country': 'Italia',
        'shipping_country_id': 39,
    }
    write_file_2_pull(ext_model, vals_shipping)

    partner_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers',
                                  'vg7',
                                  vg7_id)
    shipping_id = clodoo.executeL8(ctx,
                                  'ir.model.synchro',
                                  'trigger_one_record',
                                  'customers_shipping_addresses',
                                  'vg7',
                                   vg7_id2)
    for rectype in ('delivery', 'invoice'):
        rec_id, rec_vals = prepare_vals(
            ctx, model, partner_id, rectype, name, vg7_id, vg7_id2,
            vals_shipping, vals_billing, False)
        if rec_id:
            check_partner(ctx, rec_id, rec_vals)
    general_check(ctx, 'res.country.state', BO_id, jacket_vals(state_vals))

    model = 'sale.order'
    print('Write %s ..' % model)
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
    general_check(ctx, model, sale_id, vals)

    print('*** Starting odoo to odoo test ***')

    write_2_user(ctx)
    write_2_company(ctx)
    write_2_partner(ctx)

    print('*** Starting pull record test ***')

    model = 'account.payment.term'
    ext_model = 'payments'
    # code 30 & 3060 already in DB by previous tests
    vals1 = {
        'id': 30,
        'code': '30',
        'description': 'RiBA 30GG/FM'
    }
    write_file_2_pull(ext_model, vals1)
    vals2 = {
        'id': 3060,
        'code': '31',
        'description': 'RiBA 30/60 GG/FM',
    }
    write_file_2_pull(ext_model, vals2, mode='a')
    vals3 = {
        'id': 10,
        'code': 'BB30',
        'description': 'BB 30GG',
    }
    write_file_2_pull(ext_model, vals3, mode='a')
    print('Go to web page, menù Setting > Technical > DB > sync channel')
    print('then import account.payment.term')
    dummy = raw_input('Did you import %s records (Yes,No)? ' % ext_model)
    if not dummy.startswith('n') and not dummy.startswith('N'):
        payment_id = get_id_from_vg7id(ctx, model, 10)
        store_id(ctx, model, payment_id, 10)
        del vals3['code']
        general_check(ctx, model, payment_id, jacket_vals(vals3))

    print('%d tests connector_vg7 successfully ended' % ctx['ctr'])

 
def simulate_vg7(ctx):
    print('Simulate VG7')
    if ctx['param_1'] == 'help':
        print('simulate_vg7')
        return

    def write_file_2_pull(ext_model, vals, mode=None):
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
        with open('/opt/odoo/clodoo/%s.csv' % ext_model, mode) as fd:
            fd.write(data)

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

    def delete_record(ctx, model, domain, multi=False, action=None,
                      childs=None, company_id=False):
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
                        clodoo.executeL8(ctx, model, act, ids)
            if childs:
                for parent in clodoo.browseL8(ctx, model, ids):
                    for rec in parent[childs]:
                        clodoo.unlinkL8(ctx, model, rec.id)
            clodoo.unlinkL8(ctx, model, ids)

    def init_test(ctx, company_id):
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
        # Configure VG7 channel
        model = 'synchro.channel'
        clodoo.writeL8(ctx, model, clodoo.searchL8(
            ctx, model, []), {
            'method': 'CSV',
            'exchange_path': '/opt/odoo/clodoo/',
            'trace': True,
        })
        model = 'account.payment.term'
        delete_record(ctx, model, [('vg7_id', '=', '25')])
        model = 'sale.order'
        delete_record(ctx, model, [('name', '=', '2187')],
                      action='action_cancel')
        model = 'res.partner'
        delete_record(ctx, model, [('name', '=',
                                    'La Romagnola srl')])
        for model in ('account.payment.term',
                      'res.country',
                      'res.country.state',
                      'res.partner',
                      'sale.order'):
            unlink_vg7(model)

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    init_test(ctx, company_id)
    # Simulate sale order from VG7 (copy of real datas)

    model = 'res.country'
    ext_model = 'countries'
    vals = {
        'code': 'IT',
        'name': 'Italia',
        'id': 39,
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.country.state'
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

    model = 'account.payment.term'
    ext_model = 'payments'
    vals = {
        'id': 25,
        'description': 'Paypal',
        'code': 'PP',
    }
    write_file_2_pull(ext_model, vals)

    model = 'res.partner'
    ext_model = 'customers'
    name = 'La Romagnola srl'
    vg7_id = 44
    vals_billing = {
        'id': vg7_id,
        'billing_city': 'Imola',
        'billing_codice_univoco': 'X12345Y',
        'billing_company': name,
        'billing_postal_code': '40026',
        'billing_mobile': '',
        'billing_esonerato_fe': 0,
        'billing_region': 'BOLOGNA',
        'billing_region_id': 54,
        'billing_phone': '0542 640502',
        'billing_street': 'Via Emilia',
        'billing_street_number': '13',
        'billing_country': 'Italia',
        'billing_country_id': 39,
        'billing_email': 'antoniomaria@laromagnola.it',
        'billing_piva': '01598041208',
        'billing_cf': '02151140361',
    }
    write_file_2_pull(ext_model, vals_billing)
    ext_model = 'customers_shipping_addresses'
    vg7_id2 = 45
    vals_shipping = {
        'customer_shipping_id': vg7_id2,
        'customer_id': vg7_id,
        'shipping_city': 'Imola',
        'shipping_company': name,
        'shipping_postal_code': '40026',
        'shipping_region': 'BOLOGNA',
        'shipping_region_id': 54,
        'shipping_street': 'Piazza Maggiore',
        'shipping_street_number': '13',
        'shipping_country': 'Italia',
        'shipping_country_id': 39,
    }
    write_file_2_pull(ext_model, vals_shipping)
    vals = {
        'vg7_id': vg7_id,
        'city': 'Imola',
        'codice_destinatario': 'X12345Y',
        'name': name,
        'zip': '40026',
        'mobile': '',
        'electronic_invoice_subjected': True,
        'vg7:region': 'BOLOGNA',
        'id': 17906,
        'phone': '0542 640502',
        'street': 'Via Emilia, 13',
        'is_company': True,
        'vg7:country': 'Italia',
        'customer': True,
        'email': 'antoniomaria@laromagnola.it',
        'vat': '01598041208',
        'fiscalcode': '02151140361'
    }
    partner_id = clodoo.executeL8(ctx,
                                  model,
                                  'synchro',
                                  vals)
    model = 'sale.order'
    vals = {
        'vg7:payment_id': 25,
        'name': '2187',
        'vg7:id': 2187,
        'vg7:customer_id': 44,
        'vg7:customer_shipping_id': -1,
        'state': 'sale',
        'vg7:courier_id': 0,
        'vg7:agent_id': 8,
    }
    sale_id = clodoo.executeL8(ctx,
                               model,
                               'synchro',
                               vals)
    if sale_id < 1:
        raise IOError('Error writing %s' % model)
    model = 'sale.order.line'
    vals = {
        'name': 'Tipologia prodotto: Generico\r\nNome lavoro: prova\r\nLOTTO N.1234',
        'vg7_id': 3111,
        'price_unit': 145.0,
        'product_uom_qty': 1,
        # 'company_id': 3,
        'vg7:order_id': 2187,
        'product_qty': 1,
        'vg7_product_id': 100000006,
        'tax_id': '22v'
    }
    line_id = clodoo.executeL8(ctx,
                               model,
                               'synchro',
                               vals)
    if line_id < 1:
        raise IOError('Error writing %s' % model)
    id = clodoo.executeL8(ctx,
                          'sale.order',
                          'commit',
                          sale_id)
    if id < 0:
        raise IOError('!!Commit Failed (%d)!' % id)


def test_einvoice_in(ctx):

    def read_xml_content(xml_dir, xml_file):
        fd = open(os.path.join(xml_dir, xml_file), 'rb')
        content = fd.read()
        b64 = content.encode('base64')
        return b64

    def create_att(xml_dir, xml_file):
        model = 'fatturapa.attachment.in'
        att = clodoo.createL8(ctx, model,
                              {'name': xml_file,
                               'datas': read_xml_content(xml_dir, xml_file)})
        return att

    def get_att(xml_dir, xml_file):
        ids = clodoo.searchL8(ctx,model,[('name','=',xml_file)])
        if ids:
            att_id = ids[0]
        else:
            att_id = create_att(xml_dir, xml_file)
        return att_id

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    xml_dir = './xml_4_test'
    if not os.path.isdir(xml_dir):
        raise IOError('!!XML directory %s not found!' % xml_dir)
    model = 'fatturapa.attachment.in'
    wizard_model = 'wizard.import.fatturapa'
    print('Creating xml record ...')
    xml_file = 'IT06631580013_00001.xml'
    if not os.path.isfile(os.path.join(xml_dir, xml_file)):
        raise IOError('!!XML file %s not found!' % xml_file)
    att_id =  get_att(xml_dir, xml_file)
    res = clodoo.executeL8(ctx,
                           wizard_model,
                           'importFatturaPA',
                           [att_id])
    invoice_id = clodoo.executeL8(ctx, wizard_model,
                                  'create',
                                  res)
    clodoo.executeL8(ctx, wizard_model,
                     'execute',
                     [invoice_id])


def relinks_order_ddt(ctx):
    print('Link lost DdT line with sale order line')
    model = 'stock.picking.package.preparation.line'
    model_ord = 'sale.order.line'
    for line in clodoo.browseL8(ctx, model, [('sale_line_id', '=', False)]):
        # partner_id = line.move_id.partner_id.id
        ids = clodoo.searchL8(ctx, model_ord,
                              [('product_id', '=', line.product_id)
                               ()])


def check_rec_links(ctx):
    print('Check link for invoice records to DdTs and orders')
    model_inv = 'account.invoice'
    model_invline = 'account.invoice.line'
    err_ctr = 0
    ctr = 0
    for invoice in clodoo.browseL8(
        ctx, model_inv, clodoo.searchL8(
            ctx, model_inv, [('type', '=', 'out_invoice')],
            order='number desc')):
        msg_burst('%s ...' % invoice.number)
        orders = []
        for invoice_line in invoice.invoice_line_ids:
            msg_burst('  - %s ...' % invoice_line.name[0:80])
            for sale_line in invoice_line.sale_line_ids:
                ctr += 1
                if sale_line.order_id.id not in orders:
                    orders.append(sale_line.order_id.id)
                if (invoice.partner_id.id not in (
                        sale_line.order_id.partner_id.id,
                        sale_line.order_id.partner_invoice_id.id,
                        sale_line.order_id.partner_shipping_id.id)):
                    os0.wlog('!!!!! Invoice %s (%d) partner differs from '
                             'sale order %s (%d) partner!!!!!' % (
                                 invoice.number,
                                 invoice.id,
                                 sale_line.order_id.name,
                                 sale_line.order_id.id,))
                    err_ctr += 1
                    clodoo.writeL8(ctx, model_invline, invoice_line.id,
                                   {'sale_line_ids': [(3, sale_line.id)]})
        # for invoice_line in invoice.invoice_line_ids:
            if (invoice_line.ddt_line_id):
                if (invoice_line.ddt_line_id.sale_line_id and
                        invoice_line.ddt_line_id.sale_line_id.order_id.id
                        not in orders):
                    os0.wlog('!!!!! Invoice sale orders differs from '
                             'DdT sale order %s (%d)!!!!!' % (
                                invoice_line.ddt_line_id.sale_line_id.\
                                    order_id.name,
                                invoice_line.ddt_line_id.sale_line_id.\
                                    order_id.id))
                    err_ctr += 1
                    clodoo.writeL8(ctx, model_invline, invoice_line.id,
                                   {'ddt_line_id': False})
                elif (invoice_line.ddt_line_id.sale_line_id and
                        (invoice.partner_id.id not in (
                            invoice_line.ddt_line_id.sale_line_id.order_id.\
                            partner_id.id,
                            invoice_line.ddt_line_id.sale_line_id.order_id.\
                            partner_invoice_id.id,
                            invoice_line.ddt_line_id.sale_line_id.order_id.\
                            partner_shipping_id.id))):
                    os0.wlog('!!!!! Invoice %s (%d) partner differs from '
                             'ddt sale order %s (%d) partner!!!!!' % (
                                 invoice.number,
                                 invoice.id,
                                 invoice_line.ddt_line_id.sale_line_id.\
                                    order_id.name,
                                 invoice_line.ddt_line_id.sale_line_id.\
                                    order_id.id,))
                    err_ctr += 1
                    clodoo.writeL8(ctx, model_invline, invoice_line.id,
                                   {'ddt_line_id': False})
    print('%d record read, %d record with wrong links!' % (ctr, err_ctr))


def relink_records(ctx):
    print('Relink fiscal position on partners. Require a 2nd DB')
    if ctx['param_1'] == 'help':
        print('relink_records src_db')
        return
    if ctx['param_1']:
        src_db = ctx['param_1']
    else:
        src_db = raw_input('Source DB name? ')
    src_ctx = ctx.copy()
    uid, src_ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                       db=src_db,
                                       ctx=src_ctx)
    model = 'res.partner'
    err_ctr = 0
    ctr = 0
    TNL = {1: 1, 2: 2, 3: 3, 4: 1, 5: 2, 6: 3, 7: 7}
    for partner in clodoo.browseL8(
        src_ctx, model,
            clodoo.searchL8(src_ctx, model, [])):
        msg_burst('%s ...' % partner.name)
        if partner.property_account_position_id:
            try:
                cur_partner = clodoo.browseL8(ctx, model, partner.id)
                if not cur_partner.property_account_position_id:
                    position_id = TNL[partner.property_account_position_id.id]
                    clodoo.writeL8(
                        ctx, model, cur_partner.id,
                        {'property_account_position_id': position_id})
                    ctr += 1
            except BaseException:
                pass
    # model_inv = 'account.invoice'
    # model_invline = 'account.invoice.line'
    # err_ctr = 0
    # ctr = 0
    # model_sale = 'sale.order'
    # model_saleline = 'sale.order.line'
    # for order in clodoo.browseL8(
    #     ctx, model_sale, clodoo.searchL8(
    #         ctx, model_sale,[], order='name desc')):
    #     msg_burst('%s ...' % order.name)
    #     for order_line in order.order_line:
    #         msg_burst('  - %s ...' % order_line.name[0:80])
    #         ctr += 1
    #         if not order_line.invoice_lines:
    #             try:
    #                 src_line = clodoo.browseL8(
    #                     src_ctx, model_saleline, order_line.id)
    #             except:
    #                 continue
    #             rec = []
    #             for inv_line in src_line.invoice_lines:
    #                 rec.append(inv_line.id)
    #             if rec:
    #                 clodoo.writeL8(ctx, model_saleline, order_line.id,
    #                                {'invoice_lines': [(6, 0, rec)]})
    #                 err_ctr += 1
    # for invoice in clodoo.browseL8(
    #     ctx, model_inv, clodoo.searchL8(
    #         ctx, model_inv, [('type', '=', 'out_invoice')],
    #         order='number desc')):
    #     msg_burst('%s ...' % invoice.number)
    #     orders = []
    #     for invoice_line in invoice.invoice_line_ids:
    #         msg_burst('  - %s ...' % invoice_line.name[0:80])
    #         ctr += 1
    #         if not invoice_line.sale_line_ids:
    #             try:
    #                 src_line = clodoo.browseL8(
    #                     src_ctx, model_invline, invoice_line.id)
    #             except:
    #                 continue
    #             rec = []
    #             for sale_line in src_line.sale_line_ids:
    #                 rec.append(sale_line.id)
    #             if rec:
    #                 clodoo.writeL8(ctx, model_invline, invoice_line.id,
    #                                {'sale_line_ids': [(6, 0, rec)]})
    #                 err_ctr += 1
    print('%d record read, %d record with wrong links!' % (ctr, err_ctr))


def check_integrity_by_vg7(ctx):

    def check_partner_child(ctx, model, partner):
        parent = clodoo.browseL8(ctx, model, partner.parent_id.id)
        if partner.name and partner.name != parent.name:
            print('Current partner %d name %s differs from its parent %s' % (
                partner.id, partner.name, parent.name
            ))
            dummy = raw_input('Action: Confirm,Standard,Unlink? ')
            if dummy.upper() == 'S':
                clodoo.writeL8(ctx, model, partner.id, {'name': False})
                ctx['ctr'] += 1
            elif dummy.upper() == 'U':
                clodoo.writeL8(ctx, model, partner.id, {'parent_id': False})
                ctx['ctr'] += 1
        elif partner.name and partner.name == parent.name:
            clodoo.writeL8(ctx, model, partner.id, {'name': False})
            ctx['ctr'] += 1
        if partner.customer:
            clodoo.writeL8(ctx, model, partner.id, {'customer': False})
            ctx['ctr'] += 1
        if partner.supplier:
            clodoo.writeL8(ctx, model, partner.id, {'supplier': False})
            ctx['ctr'] += 1

    def check_partner_root(ctx, model, partner):
        if partner.type != 'contact':
            print('Current partner %d name %s has wrong type %s' % (
                partner.id, partner.name, partner.type
            ))
            msg = 'Action: '
            if partner.vg7_id:
                if partner.vg7 > 200000000:
                    if partner.type != 'invoice':
                        msg = '%s,Invoice' % msg
                elif partner.vg7 > 100000000:
                    if partner.type != 'delivery':
                        msg = '%s,Delivery' % msg
                else:
                    msg = '%s,Contact' % msg
            else:
                msg = '%s,Contact,Remove' % msg
            msg = '%s,Link2,Nop? ' % msg
            dummy = raw_input(msg)
            if dummy.upper() == 'C':
                clodoo.writeL8(ctx, model, partner.id, {'type': 'contact'})
                ctx['ctr'] += 1
            elif dummy.upper() == 'D':
                clodoo.writeL8(ctx, model, partner.id, {'type': 'delivery'})
                ctx['ctr'] += 1
            elif dummy.upper() == 'I':
                clodoo.writeL8(ctx, model, partner.id, {'type': 'invoice'})
                ctx['ctr'] += 1
            elif dummy.upper() == 'L':
                dummy = raw_input('Id of parent? ')
                if dummy.isdigit():
                    clodoo.writeL8(
                        ctx, model, partner.id, {'parent_id': int(dummy)})
                    ctx['ctr'] += 1
            elif dummy.upper() == 'R':
                try:
                    clodoo.unlinkL8(ctx, model, partner.id)
                    ctx['ctr'] += 1
                except BaseException:
                    print('Partner non deletable!')
                    check_partner_root(ctx, model, partner)

    model = 'res.partner'
    ctx['ctr'] = 0
    for partner in clodoo.browseL8(
            ctx, model, clodoo.searchL8(
                ctx, model, [])):
        msg_burst('%s ...' % partner.name)
        if partner.parent_id:
            check_partner_child(ctx, model, partner)
        else:
            check_partner_root(ctx, model, partner)
    print('%d record updated' % ctx['ctr'])


def set_comment_on_invoice(ctx):
    print('Set comment on invoices')
    if ctx['param_1'] == 'help':
        print('set_comment_on_invoice '
              '[from_date|+days|ids] [Ask] [Order]')
        return
    if ctx['param_3'] and ctx['param_3'].startswith('O'):
        model = 'sale.order'
        date_field = 'confirmation_date'
        name_field = 'name'
    else:
        model = 'account.invoice'
        date_field = 'date_invoice'
        name_field = 'number'
    date_ids = param_date(
        ctx['param_1'], model=model, date_field=date_field, ctx=ctx)
    if ctx['param_2'] and ctx['param_2'].startswith('A'):
        comment = raw_input('Text to insert on invoice comment: ')
    else:
        company_id = env_ref(ctx, 'z0bug.mycompany')
        if not company_id:
            raise IOError('!!Internal error: no company found!')
        comment = clodoo.browseL8(ctx, 'res.company', company_id).sale_note
    comment = comment.replace('\'', '\\\'')
    ctr = 0
    for rec in clodoo.browseL8(ctx, model, date_ids):
        msg_burst('%s ...' % rec[name_field])
        clodoo.writeL8(ctx, model, rec.id, {'comment': comment})
        ctr += 1
    print('%d record updated' % ctr)


def set_ppf_on_partner(ctx):
    print('Set/reset print price flag on partners')
    if ctx['param_1'] == 'help':
        print('set_ppf_on_partner '
              '[ids] [True/False]')
        return
    model = 'res.partner'
    if ctx['param_1']: 
        ids = ctx['param_1']
        domain = [('id', 'in', ids)]
    else:
        domain = []
    if ctx['param_2'] == 'F':
        value = False
    else:
        value = True
    domain.append(('ddt_show_price', '!=', value))
    domain.append('|')
    domain.append(('customer', '=', True))
    domain.append(('type', '=', 'invoice'))
    ctr = 0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, domain)):
        msg_burst('%s ...' % pp.name)
        clodoo.writeL8(ctx, model, pp.id, {'ddt_show_price': value})
        ctr += 1
    print('%d record updated' % ctr)


def set_move_partner_from_invoice(ctx):
    print('Set partner_id in account_move of invoices')
    if ctx['param_1'] == 'help':
        print('set_move_partner_from_invoice')
        return
    model = 'account.invoice'
    model_line = 'account.move.line'
    ctr = 0
    for rec in clodoo.browseL8(
            ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % rec.number)
        if not rec.move_id:
            continue
        for line in rec.move_id.line_ids:
            if not line.partner_id:
                if not rec.partner_id.commercial_partner_id:
                    print('Partner %d w/o commercial id' % rec.partner_id.id)
                    clodoo.writeL8(
                        ctx, model_line, line.id,
                        {'partner_id': rec.partner_id.id})
                    continue
                clodoo.writeL8(
                    ctx, model_line, line.id,
                    {'partner_id': rec.partner_id.commercial_partner_id.id})
    print('%d record updated' % ctr)


def solve_unnamed(ctx):
    print('Solve unnamed partners')
    if ctx['param_1'] == 'help':
        print('solve_unnamed')
        return
    model = 'res.partner'
    ctr = 0
    for rec in clodoo.browseL8(
            ctx, model, clodoo.searchL8(
                ctx, model, ['|', ('display_name', '=', False),
                             ('commercial_partner_id', '=', False)])):
        msg_burst('%s ...' % rec.name)
        vals = {}
        if not rec.commercial_partner_id:
            if rec.is_company or not rec.parent_id:
                vals = {'commercial_partner_id': rec.id}
            else:
                vals = {'commercial_partner_id': rec.parent_id}
        vals['name'] = rec.name + ' '
        clodoo.writeL8(ctx, model, rec.id, vals)
        clodoo.writeL8(ctx, model, rec.id, {'name': rec.name.strip()})
        ctr += 1
    print('%d record updated' % ctr)

def solve_flag_einvoice(ctx):
    print('solve_flag_einvoice')
    if ctx['param_1'] == 'help':
        print('solve_flag_einvoice')
        return
    model = 'res.partner'
    ctr = 0
    for rec in clodoo.browseL8(
            ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % rec.name)
        if (rec.electronic_invoice_subjected and
                not rec.codice_destinatario):
            vals = {'electronic_invoice_subjected': False}
            clodoo.writeL8(ctx, model, rec.id, vals)
            ctr += 1
    print('%d record updated' % ctr)

def check_4_duplicate_vat(ctx):
    print('Check for duplicate vat')
    if ctx['param_1'] == 'help':
        print('check_4_duplicate_vat')
        return
    model = 'res.partner'
    ctr = 0
    prior_vat = ''
    prior_id = False
    prior_candidate = False
    prior_name = ''
    for rec in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [('vat', '!=', False)], order='vat')):
        msg_burst('%s ...' % rec.name)
        if rec.vat != prior_vat:
            prior_id = rec.id
            prior_vat = rec.vat
            prior_name = rec.name
            if rec.type != 'contact' or rec.parent_id:
                prior_candidate = True
            else:
                prior_candidate = False
            if ((rec.type == 'delivery' and
                 rec.electronic_invoice_subjected) or
                    (rec.parent_id and rec.type != 'invoice')):
                vals = {'electronic_invoice_subjected': False}
                clodoo.writeL8(ctx, model, rec.id, vals)
                ctr += 1
            continue
        if rec.type != 'contact' or rec.parent_id:
            vals = {'vat': False}
            if ((rec.type == 'delivery' and
                 rec.electronic_invoice_subjected) or
                    (rec.parent_id and rec.type != 'invoice')):
                vals['electronic_invoice_subjected'] = False
            print('** Removing VAT from %s (%d)' % (rec.name, rec.id))
            clodoo.writeL8(ctx, model, rec.id, vals)
            ctr += 1
        if prior_candidate:
            vals = {'vat': False}
            print('** Removing VAT from %s (%d)' % (prior_name, prior_id))
            clodoo.writeL8(ctx, model, prior_id, vals)
            ctr += 1
    print('%d record updated' % ctr)


def setup_balance_report(ctx):
    print('Setup trial balance report')
    if ctx['param_1'] == 'help':
        print('setup_balance_report')
        return
    model = 'account.financial.report'
    vals = {
        'name': 'Bilancio di verifica semplificato',
        'sequence': 0,
        'account_report_id': False
    }
    root_id = synchro(ctx, model, vals)
    vals = {
        'name': 'STATO PATRIMONIALE',
        'sequence': 1,
        'parent_id': root_id,
        'sign': 1,
        'type': 'sum',
        'account_report_id': False
    }
    asset_liabilities_id = synchro(ctx, model, vals)
    vals = {
        'name': 'ATTIVITÀ',
        'sequence': 2,
        'parent_id': asset_liabilities_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [(6, 9, [
            env_ref(ctx, 'account.data_account_type_credit_card'),
            env_ref(ctx, 'account.data_account_type_current_assets'),
            env_ref(ctx, 'account.data_account_type_fixed_assets'),
            env_ref(ctx, 'account.data_account_type_non_current_assets'),
            env_ref(ctx, 'account.data_account_type_receivable'),
            env_ref(ctx, 'account.data_account_type_liquidity'),
        ])],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    asset_id = synchro(ctx, model, vals)
    vals = {
        'name': 'Liquidità',
        'sequence': 3,
        'parent_id': asset_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [(6, 9, [
            env_ref(ctx, 'account.data_account_type_liquidity'),
        ])],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    # asset_id = synchro(ctx, model, vals)
    vals = {
        'name': 'PASSIVITÀ',
        'sequence': 3,
        'parent_id': asset_liabilities_id,
        'sign': -1,
        'type': 'account_type',
        'account_type_ids': [(6, 9, [
            env_ref(ctx, 'account.data_account_type_current_liabilities'),
            env_ref(ctx, 'account.data_account_type_depreciation'),
            env_ref(ctx, 'account.data_account_type_equity'),
            env_ref(ctx, 'account.data_account_type_non_current_liabilities'),
            env_ref(ctx, 'account.data_account_type_payable'),
            env_ref(ctx, 'account.data_account_type_prepayments'),
        ])],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    liabilities_id = synchro(ctx, model, vals)
    vals = {
        'name': 'Utile (perdita) lordo pre-imposte',
        'sequence': 10,
        'parent_id': root_id,
        'sign': -1,
        'type': 'sum',
        'account_report_id': False
    }
    lp_id = synchro(ctx, model, vals)
    vals = {
        'name': 'RICAVI',
        'sequence': 11,
        'parent_id': lp_id,
        'sign': -1,
        'type': 'account_type',
        'account_type_ids': [(6, 9, [
            env_ref(ctx, 'account.data_account_type_revenue'),
            env_ref(ctx, 'account.data_account_type_other_income'),
            env_ref(ctx, 'account.data_unaffected_earnings'),
        ])],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    income_id = synchro(ctx, model, vals)
    vals = {
        'name': 'COSTI',
        'sequence': 12,
        'parent_id': lp_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [(6, 9, [
            env_ref(ctx, 'account.data_account_type_direct_costs'),
            env_ref(ctx, 'account.data_account_type_depreciation'),
            env_ref(ctx, 'account.data_account_type_expenses'),
        ])],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    cost_id = synchro(ctx, model, vals)


def rename_coa(ctx):
    CVT_TBL = {
        'crediti v/clienti ': 'Crediti v/clienti Italia',
        'debiti v/fornitori ': 'Debiti v/fornitori Italia',
        'costi di impianto ': 'Spese di Impianto e di Ampliamento',
        'arredamento ': 'Mobili e Arredi Ufficio',
        'attrezzature commerciali ': 'Attrezzature Industriali e Commerciali',
        'banche c/c passivi ': 'Banche c/c passivi nazionali',
        'banche c/effetti scontati ': 'Effetti allo sconto',
        'beni di terzi ': 'Beni di terzi presso l\'impresa,'
                          ' a titolo di deposito o comodato',
        'bilancio di apertura ': 'Stato patrimoniale iniziale',
        'bilancio di chiusura ': 'Stato patrimoniale finale',
        'cambiali all\'incasso ': 'Banche c/cambiali all\'incasso',
        'cambiali allo sconto ': 'Effetti allo sconto (+12M)',
        'cambiali attive ':  'Cambiali attive (+12M)',
        'rischi per fideiussioni ':
            'Rischi assunti dall\'impresa, Fideiussioni',
        'sconti passivi bancari ': 'Spese e commissioni bancarie',
        'software ': 'Programmi Software e Licenze',
        'stato patrimoniale': 'Stato patrimoniale (da risultato di esercizio)',
        'TFRL ': 'TFR: trattamento di fine rapporto',
        'titolare c/ritenute subite ': 'Crediti per ritenute subite',
        'utile d\'esercizio ': 'Utile (perdita) d\'esercizio ',
        'merci c/vendite ': 'Merci c/vendita',
        'costi di pubblicità ': 'Costi pubblicitari',
        'FA costi di impianto ': 'FA Costi di Impianto e di Ampliamento',
        'FA software ': 'FA Programmi Software e Licenze',
        'macchine d\'ufficio ': 'Macchine Ufficio Elettroniche',
        'imballaggi durevoli ': 'Imballaggi durevoli da riutilizzare',
        'fornitori immobilizzazioni c/acconti ':
            'Acconti a Fornitori su Immobilizzazioni',
        'Mutui passivi': 'Mutui passivi',
        # 'mutui attivi ': 'Mutui passivi',
        'materie di consumo ': 'Materie prime e di consumo',
        'merci ': 'Prodotti finiti e Merci',
        'IVA c/acconto ': 'Imposte c/acconto IVA',
        'debiti per TFRL': 'Debiti per TFR',
        'crediti per IVA ': 'Crediti IVA c/erario',
        'fatture da ricevere ': 'Fornitori Fatture da ricevere ',
        'clienti c/acconti ': 'Debiti v/clienti c/anticipi',
        'merci c/apporti ': 'Costi Merce c/apporti',
        'perdita d\'esercizio ': 'Perdita da esercizio precedente',
        'merci c/acquisti': 'Spese accessorie su Acquisti',
        'costi di trasporto ': 'Costi di trasporto e spedizione',
        'fondo ammortamento costi di impianto ':
            'FA Costi di Impianto e di Ampliamento',
        'fondo ammortamento software ': 'FA Programmi Software e Licenze',
        'fatture da emettere ': 'Clienti fatture da emettere',
    }

    def dim_text(text):
        if text:
            text = unidecode(text).strip()
            res = ''
            for ch in text:
                if ch.isalnum():
                    res += ch.lower()
            text = res
        return text

    def read_csv_file(csv_fn):
        coa = {}
        rev_coa = {}
        with open(csv_fn, 'rb') as f:
            hdr = False
            reader = csv.reader(f)
            for row in reader:
                if not hdr:
                    hdr = True
                    CODE = row.index('code')
                    NAME = row.index('name')
                    continue
                row = unicodes(row)
                if row[NAME] in CVT_TBL:
                    row[NAME] = CVT_TBL[row[NAME]]
                elif row[NAME].lower().startswith('ammortamento '):
                    row[NAME] = 'QA' + row[NAME][12:]
                elif row[NAME].lower().startswith('fondo ammortamento '):
                    row[NAME] = 'FA' + row[NAME][18:]
                coa[('%s000000' % row[CODE])[0:6]] = row[NAME]
                dim_name = dim_text(row[NAME])
                rev_coa[dim_name] = ('%s000000' % row[CODE])[0:6]
        return coa, rev_coa

    print('Rename Chart of Account codes from OCA to zeroincombenze')
    uid, ctx = clodoo.oerp_set_env(ctx=ctx)
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company found!')
    if not ctx.get('_cr'):
        print('No sql support found!')
        print('No operatione will be done')
        dummy = raw_input('Press RET to continue')
    oca_path = '/opt/odoo/10.0/addons/l10n_it/data'
    z0_path = '/opt/odoo/10.0/l10n-italy/l10n_it_fiscal/data'
    csv_fn_oca = os.path.join(oca_path, 'account.account.template.csv')
    csv_fn_z0 = os.path.join(z0_path, 'account.account.template.csv')
    coa_z0, rev_coa_z0 = read_csv_file(csv_fn_z0)
    coa_oca, rev_coa_oca = read_csv_file(csv_fn_oca)
    # ren_coa, rev_ren_coa = cvt_rules()
    cvt_coa = {}
    cvt_codes = {
        '999': ['4900'],
        '524': ['7311'],
        '521': ['7310'],
        '514': ['7304'],
        '511': ['7201'],
        '430': ['6301'],
        '413': ['6103'],
        '412': ['6102'],
        '293': ['4300'],
        '292': ['4200'],
        '291': ['4100'],
        '281': ['2600'],
        '261': ['2504'],
        '230': ['2460'],
        '220': ['2205'],
        '183': ['1830'],
        '182': ['1820'],
        '181': ['1810'],
        '180': ['1800'],
        '161': ['1544'],
        '153': ['1535'],
        '152': ['1533'],
        '151': ['1532'],
        '130': ['1500'],
    }
    to_delete_z0 = []
    to_delete_oca = []
    for k1 in rev_coa_oca:
        if k1 in rev_coa_z0:
            cvt_coa[rev_coa_oca[k1]] = rev_coa_z0[k1]
            to_delete_oca.append(rev_coa_oca[k1])
            kk = rev_coa_oca[k1][0:3]
            if kk not in cvt_codes:
                cvt_codes[kk] = [rev_coa_z0[k1][0:4]]
            elif rev_coa_z0[k1][0:3] not in cvt_codes[kk]:
                cvt_codes[kk].append(rev_coa_z0[k1][0:4])
    for code in to_delete_oca:
        del rev_coa_oca[dim_text(coa_oca[code])]
        del coa_oca[code]
    if cvt_coa['150100'] != '152100':
        print('Invalid CoA structure or CoA already renamed!')
        return 1
    model = 'account.account'
    ids = clodoo.searchL8(ctx, model,
                          [('company_id', '=', company_id)])
    rev_cvt_coa = {}
    for acc in clodoo.browseL8(ctx, model, ids):
        code = acc.code
        new_code = ''
        if code in cvt_coa:
            new_code = cvt_coa[code]
        else:
            if code[0:3] in cvt_codes:
                new_codes = cvt_codes[code[0:3]]
                if len(new_codes) == 1 or new_codes[0][0:2] == new_codes[1][0:2]:
                    new_code = new_codes[0] + code[3:5]
                else:
                    new_code = new_codes[0]
                    diff = abs(int(new_codes[0]) - int(code[0:3]))
                    for x in new_codes[1:]:
                        i = abs(int(x) - int(code[0:3]))
                        if i < diff:
                            new_code = x
                            diff = i
                    new_code = new_code + code[3:5]
            if not new_code:
                print('Code %s without translation!' % code)
                cvt_coa[code] = code
                continue
        while new_code in rev_cvt_coa:
            print('Duplicate code %s' % new_code)
            i = int(new_code[5]) + 1
            new_code = new_code[0:5] + str(i)
        cvt_coa[code] = new_code
        rev_cvt_coa[new_code] = code

    for acc in clodoo.browseL8(ctx, model, ids):
        code = acc.code
        if code not in cvt_coa:
            continue
        new_code = cvt_coa[code]
        query = "update account_account set code='%s$' domain code = '%s'" % (
            new_code, code)
        print(">>> %s (%s)" % (query, acc.name))
        if ctx.get('_cr') and not ctx['dry_run']:
            clodoo.exec_sql(ctx, query)
    query = "update account_account set code=substring(code from 1 for 6)"
    clodoo.exec_sql(ctx, query)
    return 0

if ctx['function']:
    function = ctx['function']
    globals()[function](ctx)
    exit()

print('Avaiable functions:')
print(' SALE ORDER                      ACCOUNT INVOICE')
print(' - order_commission_by_partner   - inv_commission_from_order')
print(' - all_addr_same_customer        - inv_commission_by_partner')
print(' - close_sale_orders             - revaluate_due_date_in_invoces')
print(' - order_inv_group_by_partner    - update_einvoice_out_attachment')
print(' PURCHASE ORDER                  - unlink_einvoice_out_attachment')
print(' - close_purchase_orders         - set_tax_code_on_invoice')
print(' PRODUCT                         - set_comment_on_invoice')
print(' - set_products_2_consumable     - set_move_partner_from_invoice')
print(' - set_products_delivery_policy  COMMISSION')
print(' - set_fiscal_on_products        - create_commission_env')
print(' ACCOUNT                         DELIVERY/SHIPPING')
print(' - create_RA_config              - change_ddt_number')
print(' PARTNER/USER                    - create_delivery_env')
print(' - check_integrity_by_vg7        - show_empty_ddt')
print(' - configure_fiscal_position     RIBA')
print(' - set_ppf_on_partner            - configure_RiBA')
print(' - deduplicate_partner           - manage_riba')
print(' - reset_email_admins             OTHER TABLES')
print(' - solve_unnamed                  - set_report_config')
print(' - solve_flag_einvoice            - rename_coa')
print(' - simulate_user_profile          - setup_balance_report')
print(' SYSTEM                           - show_module_group')
print(' - clean_translations             - display_module')
print(' - configure_email_template       - print_tax_codes')
print(' - test_synchro_vg7               - check_rec_links')
print(' - set_db_4_test')

pdb.set_trace()

def read_csv_file(csv_fn):
    model = 'account.account'
    with open(csv_fn, 'rb') as f:
        hdr = False
        reader = csv.reader(f)
        for row in reader:
            if not hdr:
                hdr = True
                CODE = row.index('code')
                NAME = row.index('description')
                UTYPE = row.index('tipo')
                continue
            row = unicodes(row)
            ids = clodoo.searchL8(ctx, model, [('code', '=', row[CODE])])
            vals = {
                'code': row[CODE],
                'name': row[NAME],
                'user_type_id': env_ref(ctx, row[UTYPE]),
            }
            if ids:
                clodoo.writeL8(ctx, model, ids[0], vals)
            else:
                vals['reconcile'] = True
                clodoo.createL8(ctx, model, vals)
    return

model = 'account.account'
CVT = {
    '123382': '09047',
    '151500': '01600',
    '152100': '19010',
    '153010': '19031',
    '153030': '49998',
    '153050': '19033',
    '250100': '04000',
    '260010': '19032',
    '510000': '10000',
    '610100': '09205',
    '621600': '09090',
    '731140': '09406',
    '180003': '01233',
}
# read_csv_file('/opt/odoo/clodoo/pentagraf/account.account.csv')
company_id = int(raw_input('company_id)? '))
db = raw_input('database)? ')
CVT = {}
for id in clodoo.searchL8(ctx, model, []):
    try:
        clodoo.unlinkL8(ctx, model, id)
        print('deleted id=%d' % id)
    except:
        print('error deleting id=%d' % id)
        acc = clodoo.browseL8(ctx, model, id)
        if acc.company_id.id != company_id:
            continue
        print('code=%s' % acc.code)
        if acc.code in CVT:
            new_code = CVT[acc.code]
            query = 'update account_account set code=\'%s\' domain id=%d;' % (
                new_code, id)
            os.system('psql -Uodoo10 -c "%s" %s' % (query, db))

# read_csv_file('/opt/odoo/clodoo/pentagraf/account.account.csv')


def build_table_tree():
    def new_empty_model(models, model):
        if model not in models:
            models[model] = {}
            models[model]['depends'] = []
            models[model]['maydepends'] = []
            models[model]['m2m'] = []
            models[model]['crossdep'] = []
    model_list = []
    models = {}
    for model_rec in clodoo.browseL8(
        ctx, 'ir.model', clodoo.searchL8(
            ctx, 'ir.model', [])):
        model = model_rec.model
        msg_burst('%s ...' % model)
        model_list.append(model)
        new_empty_model(models, model)
        level = 0
        for field in clodoo.browseL8(
            ctx, 'ir.model.fields', clodoo.searchL8(
                ctx, 'ir.model.fields', [('model', '=', model)])):
            if field.ttype == 'many2one' and field.relation != model:
                if field.relation not in models:
                    new_empty_model(models, field.relation)
                if (field.required and
                        field.relation not in models[model]['depends']):
                    models[model]['depends'].append(field.relation)
                    level = -1
                if (not field.required and
                        field.relation not in models[model]['maydepends']):
                    models[model]['maydepends'].append(field.relation)
            elif field.ttype == 'one2many' and field.relation != model:
                if field.relation not in models:
                    new_empty_model(models, field.relation)
                if (field.required and
                        model not in models[field.relation]['depends']):
                    models[field.relation]['depends'].append(model)
                    level = -1
                if (not field.required and
                        model not in models[field.relation]['maydepends']):
                    models[field.relation]['maydepends'].append(model)
            elif field.ttype in 'many2many' and field.relation != model:
                if field.relation not in models:
                    new_empty_model(models, field.relation)
                if field.relation not in models[model]['m2m']:
                    models[model]['m2m'].append(field.relation)
                if model not in models[field.relation]['m2m']:
                    models[field.relation]['m2m'].append(model)
        if level == 0:
            models[model]['level'] = level
    for model in model_list:
        msg_burst('%s ...' % model)
        for sub in models[model]['depends']:
            if model in models[sub]['depends']:
                models[model]['crossdep'] = sub
                models[sub]['crossdep'] = model
    for model in model_list:
        msg_burst('%s ...' % model)
        models[model]['depends'] = list(set(models[model]['depends']) -
                                        set(models[model]['crossdep']) )
    missed_models = {}
    max_iter = 99
    parsing = True
    while parsing:
        parsing = False
        max_iter -= 1
        if max_iter <= 0:
            break
        for model in model_list:
            msg_burst('%s ...' % model)
            if 'level' not in models[model]:
                parsing = True
                cur_level = 0
                for sub in models[model]['depends']:
                    if 'level' in models[sub]:
                        cur_level = max(cur_level, models[sub]['level'] + 1)
                        if cur_level > MAX_DEEP:
                            cur_level = MAX_DEEP
                            models[model]['status'] = 'too deep'
                            break
                        else:
                            models[model]['status'] = 'OK'
                    elif model in models[sub]['depends']:
                        models[model]['status'] = 'cross dep. with %s' % sub
                        models[sub]['status'] = 'cross dep. with %s' % model
                    else:
                        cur_level = -1
                        models[model]['status'] = 'broken by %s' % sub
                        break
                if cur_level >= MAX_DEEP:
                    models[model]['level'] = MAX_DEEP
                elif cur_level >= 0:
                    models[model]['level'] = cur_level
    for model in model_list:
        if 'level' not in models[model]:
            models[model]['level'] = MAX_DEEP + 1
    return models


def display_modules(ctx):
    model = 'ir.module.module'
    mlist = []
    for i,app in enumerate(clodoo.browseL8(
        ctx,model,clodoo.searchL8(
            ctx,model,[('state','=','installed')], order='name'))):
        print('%3d %-40.40s %s' % (i+1, app.name, app.author))
        mlist.append(app.name)
    print(mlist)
