#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import print_function

from python_plus import unicodes
import os
import sys
from datetime import datetime,date
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


__version__ = "0.1.0.2"


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
parser.add_argument("-x", "--exec",
                    help="internal function to execute",
                    dest="function",
                    metavar="python_name",
                    default='')
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


ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)
msg_time = time.time()
os0.set_tlog_file('./test_env.log', echo=True)


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def env_ref(ctx, xref):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        ids = clodoo.searchL8(ctx, 'ir.model.data', [('module', '=', xrefs[0]),
                                                     ('name', '=', xrefs[1])])
        if ids:
            return clodoo.browseL8(ctx, 'ir.model.data', ids[0]).res_id
    return False


def synchro(ctx, model, vals):
    sts = 0
    ids = []
    if 'id' in vals:
        ids = clodoo.searchL8(ctx, model, [('id', '=', vals['id'])])
        if not ids or ids[0] != vals['id']:
            raise IOError('ID %d does not exist in %s' %
                            vals['id'], model)
        del vals['id']
    if not ids and 'code' in vals:
        where = [('code', '=', vals['code'])]
        if 'company_id' in vals:
            where.append(('company_id', '=', vals['company_id']))
        ids = clodoo.searchL8(ctx, model, where)
    if not ids and 'name' in vals:
        where = [('name', '=', vals['name'])]
        if 'company_id' in vals:
            where.append(('company_id', '=', vals['company_id']))
        ids = clodoo.searchL8(ctx, model, where)
    if ids:
        ids = ids[0]
        clodoo.writeL8(ctx, model, ids, vals)
    else:
        ids = clodoo.createL8(ctx, model, vals)
    return ids


def delivery_addr_same_customer(ctx):
    print('Set delivery address to the same of customer')
    model = 'sale.order'
    numbers = raw_input('Sale Order number like: ')
    ctr = 0
    for so in clodoo.browseL8(
        ctx,model,clodoo.searchL8(
            ctx, model, [('name', 'like', numbers)])):
        if (so.partner_shipping_id != so.partner_id or
                so.partner_invoice_id != so.partner_id):
            clodoo.writeL8(ctx, model, so.id,
                           {'partner_shipping_id': so.partner_id.id,
                            'partner_invoice_id': so.partner_id.id})
            print('so.number=%s' % so.name)
            ctr += 1
    print('%d sale orders updated' % ctr)


def order_commission_by_partner(ctx):
    print('If missed, set commission in order lines from customer')
    if ctx['param_1'] == 'help':
        print('order_commission_by_partner [Add,Recalculate] from_date|ids')
        return
    ord_model = 'sale.order'
    ord_line_model = 'sale.order.line'
    sale_agent_model = 'sale.order.line.agent'
    mode = ctx['param_1'] or 'A'
    while not mode.startswith('A') and not mode.startswith('R'):
        mode = raw_input('Mode (Add_missed,Recalculate)? ')
        mode = mode[0].upper() if mode else ''
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
    date_ids = ctx['param_2'] or from_date
    if not date_ids:
        date_ids = raw_input(
            'IDS to manage or date yyyy-mm-dd (empty means all)? ')
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, ord_model,
                              [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            where = [('order_id', '=', ids)]
            where1 = [('id', '=', ids)]
        else:
            where = [('order_id', 'in', ids)]
            where1 = [('id', 'in', ids)]
    else:
        where = []
        where1 = []
    print('Starting mode %s from %s' % (mode, date_ids))
    ctr = 0
    for ord_line in clodoo.browseL8(
        ctx, ord_line_model, clodoo.searchL8(
            ctx, ord_line_model, where, order='order_id desc,id')):
        msg_burst('%s ...' % ord_line.order_id.name)
        if ord_line.agents:
            if mode == 'A':
                continue
            clodoo.unlinkL8(ctx, sale_agent_model, ord_line.agents.id)
        rec = []
        for agent in ord_line.order_id.partner_id.agents:
            rec.append({
                'agent': ord_line.order_id.partner_id.agents.id,
                'commission': ord_line.order_id.partner_id.agents.commission.id,
            })
        if rec:
            clodoo.writeL8(ctx, ord_line_model, ord_line.id,
                           {'agents': [(0, 0, rec[0])]})
            ctr += 1
    # Force line update
    for order in clodoo.browseL8(
        ctx, ord_model, clodoo.searchL8(
            ctx, ord_model, where1, order='id desc')):
        msg_burst('%s ...' % order.name)
        clodoo.writeL8(ctx, ord_model, order.id,
            {'name': order.name})
    print('%d sale order lines updated' % ctr)


def inv_commission_from_order(ctx):
    print('If missed, copy commission in invoice lines from sale order lines')
    if ctx['param_1'] == 'help':
        print('inv_commission_from_order [Add,Recalculate] from_date|ids')
        return
    inv_model = 'account.invoice'
    inv_line_model = 'account.invoice.line'
    inv_agent_model = 'account.invoice.line.agent'
    ctr = 0
    mode = ctx['param_1'] or 'A'
    while not mode.startswith('A') and not mode.startswith('R'):
        mode = raw_input('Mode (Add_missed,Recalculate)? ')
        mode = mode[0].upper() if mode else ''
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
    date_ids = ctx['param_2'] or from_date
    if not date_ids:
        date_ids = raw_input(
            'IDS to manage or date yyyy-mm-dd (empty means all)? ')
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, inv_model,
                              [('date_invoice', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, int):
            where = [('invoice_id', '=', ids)]
            where1 = [('id', '=', ids)]
        else:
            where = [('invoice_id', 'in', ids)]
            where1 = [('id', 'in', ids)]
    else:
        where = []
        where1 = []
    where.append(('invoice_id.type', 'in', ('out_invoice', 'out_refund')))
    where1.append(('type', 'in', ('out_invoice', 'out_refund')))
    for inv_line in clodoo.browseL8(
        ctx, inv_line_model, clodoo.searchL8(
            ctx, inv_line_model, where, order='invoice_id desc,id')):
        msg_burst('%s ...' % inv_line.invoice_id.number)
        if inv_line.agents:
            if mode == 'A':
                continue
            clodoo.unlinkL8(ctx, inv_agent_model, inv_line.agents.id)
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
    for invoice in clodoo.browseL8(
        ctx, inv_model, clodoo.searchL8(
            ctx, inv_model, where1, order='id desc')):
        msg_burst('%s ...' % invoice.number)
        clodoo.writeL8(ctx, inv_model, invoice.id,
            {'number': invoice.number})
    print('%d invoice lines updated' % ctr)


def update_einvoice_out_attachment(ctx):
    print('Update e-attachment of invoice')
    model = 'account.invoice'
    inv_id = raw_input('Invoice id: ')
    if inv_id:
        inv_id = eval(inv_id)
        inv = clodoo.browseL8(ctx, model, inv_id)
        att = inv.fatturapa_attachment_out_id
        if not att:
            print('Invoice %s w/o attachment' % inv.number)
            return
        print('Processing invoice %s' % inv.number)
        model = 'fatturapa.attachment.out'
        att = clodoo.browseL8(ctx, model, att.id)
        print('Attachment ID = %d, state=%s' % (att.id, att.state))
        state = raw_input(
            'State (ready,sent,sender|recipient_error,reject,validated): ')
        if state:
            clodoo.writeL8(ctx, model, att.id, {'state': state})


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
        tax_id = clodoo.searchL8(ctx,
                                 'account.tax',
                                 [('description', '=', '22v'),
                                  ('company_id', '=', invoice.company_id.id)])
        if tax_id:
            tax_id = tax_id[0]
        else:
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
    where = [('lang', '=', 'it_IT'),
             '|',
             ('name', '=', 'ir.module.module,description'),
             ('name', '=', 'ir.module.module,shortdesc')]
    ids = clodoo.searchL8(ctx, model, where)
    print('unlink %s' % ids)
    clodoo.unlinkL8(ctx, model, ids)
    print('%d records deleted' % len(ids))


def close_purchase_orders(ctx):
    print('Close purchase orders lines that are delivered')
    model = 'purchase.order.line'
    ctr = 0
    for po in clodoo.browseL8(ctx,model,clodoo.searchL8(ctx,model,[])):
        if po.qty_invoiced == 0.0:
            qty_received = po.product_qty
        elif po.qty_received == 0.0:
            qty_received = po.product_qty
        else:
            qty_received = 0.0
        print(po.product_qty,po.qty_received,qty_received,po.qty_invoiced)
        if qty_received > 0.0:
            clodoo.writeL8(ctx,model,po.id,{'qty_received': qty_received})
            ctr += 1
    print('%d purchase order lines updated' % ctr)


def products_2_delivery_order(ctx):
    print('Set purchase methods to purchase in all products')
    model = 'product.template'
    ctr=0
    for pp in clodoo.browseL8(ctx, model,clodoo.searchL8(ctx, model, [])):
        if pp.purchase_method != 'purchase':
            clodoo.writeL8(ctx, model, pp.id, {'purchase_method':'purchase'})
            ctr += 1
        if pp.invoice_delivery != 'order':
            clodoo.writeL8(ctx, model, pp.id, {'invoice_delivery':'order'})
            ctr += 1
    print('%d product templates updated' % ctr)

    model = 'product.product'
    ctr=0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        if pp.purchase_method != 'purchase':
            clodoo.writeL8(ctx, model, pp.id, {'purchase_method':'purchase'})
            ctr += 1
        if pp.invoice_delivery != 'order':
            clodoo.writeL8(ctx, model, pp.id, {'invoice_delivery':'order'})
            ctr += 1
    print('%d products updated' % ctr)


def set_products_2_consumable(ctx):
    print('Set consumable of the stockable products')
    model = 'product.template'
    ctr=0
    for pp in clodoo.browseL8(ctx, model,clodoo.searchL8(ctx, model,
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


def reset_report_config(ctx):
    print('Reset report and multireport configuration')
    print('Require module "base_multireport"')
    ctr = 0
    mr_t_odoo = env_ref(ctx, 'base_multireport.mr_t_odoo')
    model = 'multireport.style'
    vals = {
        'template_sale_order': mr_t_odoo,
        'template_stock_picking_package_preparation': mr_t_odoo,
        'template_account_invoice': mr_t_odoo,
        'template_purchase_order': mr_t_odoo,
    }
    for style in clodoo.browseL8(
        ctx, model,
            clodoo.searchL8(ctx, model, [('origin', '!=', 'odoo')])):
        print('Processing style %s' % style.name)
        clodoo.writeL8(ctx, model, style.id, vals)
        ctr += 1
    model = 'ir.actions.report.xml'
    vals = {
        'code_mode': '',
        'description_mode': '',
        'payment_term_position': '',
        'header_mode': '',
        'footer_mode': '',
        'template': mr_t_odoo,
        'order_ref_text': '',
        'ddt_ref_text': ''
    }
    where = [('model', 'in', ('sale.order',
                              'stock.picking.package.preparation',
                              'account.invoice',
                              'purchase.order'))]
    for rpt in clodoo.browseL8(
        ctx, model,
            clodoo.searchL8(ctx, model, [])):
        print('Processing report %s' % rpt.name)
        clodoo.writeL8(ctx, model, rpt.id, vals)
        ctr += 1
    where = [('model', 'not in', ('sale.order',
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
        'order_ref_text': 'Vs. Ordine: %(client_order_ref)s / '\
                          'Ns. Ordine: %(order_name)s del %(date_order)s',
        'ddt_ref_text': 'DdT %(ddt_number)s - %(date_ddt)s'
    }
    model = 'ir.ui.view'
    where = [('key', '=', 'base_multireport.external_layout_header')]
    ids = clodoo.searchL8(ctx, model, where)
    if len(ids) == 1:
        vals['header_id'] = ids[0]
    where = [('key', '=', 'base_multireport.external_layout_footer')]
    ids = clodoo.searchL8(ctx, model, where)
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


def set_payment_data_on_report(ctx):
    print('Set payment data layout on invoice and order reports')
    print('Require module "base_multireport"')
    model = 'ir.actions.report.xml'
    mode = raw_input('Mode (odoo,auto,footer,header,none): ')
    ctr = 0
    if mode:
        for rpt in clodoo.browseL8(
            ctx, model,
                clodoo.searchL8(ctx, model,
                                [('model', 'in', ('account.invoice',
                                                  'sale.order'))])):
            print('Processing report %s' % rpt.name)
            clodoo.writeL8(ctx, model, rpt.id, {'payment_term_position': mode})
            ctr += 1
    print('%d reports updated' % ctr)


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
    where = [('name', 'ilike', 'ritenut')]
    if company_id:
        where.append(('company_id', '=', company_id))
    for acc in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, where)):
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
    where = [('name', 'ilike', '15')]
    ids = clodoo.searchL8(ctx, model, where)
    model = 'withholding.tax'
    vals = {'name': '1040',
            'account_receivable_id': credit_acc_id,
            'account_payable_id': debit_acc_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040'
        vals['company_id'] = company_id
    if ids:
        vals['payment_term'] = ids[0]
    synchro(ctx, model, vals)


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
    company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')

    acctype_expense_id = env_ref(ctx, 'account.data_account_type_expenses')

    model = 'account.account'
    vals = {
        'code': '490050',
        'name': 'Transitorio Reverse Charge',
        'company_id': company_id,
        'user_type_id': acctype_expense_id,
    }
    account_rc_id = synchro(ctx, model, vals)


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
            where = [('customer', '=', True), ('parent_id', '=', False)]
        elif model == 'account.invoice':
            print('%-15.15s %4s %-20.20s %s' % (
                'model', 'id', 'number', 'agents')
            )
            model2 = 'account.invoice.line'
            where = []
        else:
            print('%-10.10s %4s %-16.16s %-32.32s %s' % (
                'model', 'id', 'name', 'customer', 'agents')
            )
            model2 = 'sale.order.line'
            where = []
        for rec in clodoo.browseL8(ctx, model,
                                   clodoo.searchL8(ctx, model, where)):
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
                    where = [('parent_id', '=', rec.id)]
                elif model2 == 'account.invoice.line':
                    where = [('invoice_id', '=', rec.id)]
                else:
                    where = [('order_id', '=', rec.id)]
                for rec2 in clodoo.browseL8(
                    ctx, model2, clodoo.searchL8(
                        ctx, model2, where)):
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
            clodoo.createL8(ctx, model, vals)
            ictr += 1
        else:
            clodoo.writeL8(ctx, model, AGENTS[agent]['id'], vals)
            uctr += 1

    model = 'res.partner'
    CUSTOMERS = {
        'IT12345670017': {'id': False, 'agents': AGENTS['Agente B']['id']},
        'IT02345670018': {'id': False, 'agents': AGENTS['Agente A']['id']},
        'IT00118439991': {'id': False, 'agents': AGENTS['Agente A']['id']},
        'IT03675290286': {'id': False, 'agents': AGENTS['Agente B']['id']},
    }
    for customer in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [])):
        msg_burst('%s ...' % customer.name)
        if not customer.parent_id and customer.vat in CUSTOMERS:
            CUSTOMERS[customer.vat]['id'] = customer.id
        elif customer.parent_id and customer.agents:
            clodoo.writeL8(ctx, model, customer.id, {'agents': [(6, 0, [])]})
    for customer in CUSTOMERS:
        vals = {
            'agents': [(6, 0, [CUSTOMERS[customer]['agents']])],
        }
        if not CUSTOMERS[customer]['id']:
            clodoo.createL8(ctx, model, vals)
            ictr += 1
        else:
            clodoo.writeL8(ctx, model, CUSTOMERS[customer]['id'], vals)
            uctr += 1
    print('%d records created, %d records updated' % (ictr, uctr))


def show_empty_ddt(ctx):
    print('Show DdT without lines')
    model='stock.picking.package.preparation'
    for ddt in clodoo.browseL8(ctx,model,clodoo.searchL8(ctx,model,[])):
        msg_burst('%s ...' % ddt.ddt_number)
        if not ddt.line_ids:
            print('DdT n.%s del %s (Id=%d) without lines' % (
                ddt.ddt_number, ddt.date, ddt.id))


def change_ddt_number(ctx):
    print('Change DdT number of validated record')
    model='stock.picking.package.preparation'
    ddt_id = raw_input('DdT id: ')
    if ddt_id:
        ddt_id = int(ddt_id)
        ddt = clodoo.browseL8(ctx, model, ddt_id)
        print('Currnt DdT number is: %s' % ddt.ddt_number)
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
            ctx, model, [], order='name')):
        msg_burst('%s ...' % partner.name)
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

def test_synchro_vg7(ctx):

    def general_check(ctx, TNL, model, id, vals):
        if not id or id < 1:
            raise IOError('!!Syncro %s Failed!' % model)
        if 'company_id' in vals:
            company_id = vals['company_id']
        else:
            company_id = env_ref(ctx, 'z0bug.mycompany') 
        rec = clodoo.browseL8(ctx, model, id)
        if model == 'res.partner' and vals['vg7_id'] == 17:
            if rec.name != 'Rossi Mario':
                raise IOError('!!Invalid field %s.name!' % model)
            if rec.id not in ctx['partner_MR_ids']:
                raise IOError('!!Invalid id of %s!' % model)
            if rec.is_company:
                raise IOError('!!Invalid field %s.is_company!' % model)
        elif model == 'res.partner':
            if not rec.is_company:
                raise IOError('!!Invalid field %s.is_company!' % model)
        for ext_ref in vals:
            if (model in ('sale.order.line', 'account.invoice.line') and
                    ext_ref == 'partner_id'):
                continue
            elif ext_ref in ('vg7_id', 'vg7:id'):
                if isinstance(vals[ext_ref], basestring):
                    vals[ext_ref] = int(vals[ext_ref])
                if getattr(rec, 'vg7_id') != vals[ext_ref]:
                    raise IOError('!!Invalid field %s.%s!' % (model, 'vg7_id'))
                continue
            elif ext_ref.startswith('vg7:'):
                if ext_ref == 'vg7:name':
                    continue
                loc_name = ext_ref[4:]
                if loc_name in ('street_number', 'surename'):
                    continue
                elif (model in ('res.country',) and loc_name == 'description'):
                    continue
                elif (model in ('product.product', ) and
                        loc_name == 'description'):
                    loc_name = 'name'
                elif model == 'res.partner' and loc_name == 'piva':
                    loc_name = 'vat'
                elif model == 'res.partner' and loc_name == 'company':
                    loc_name = 'name'
            else:
                if ext_ref.startswith('vg7_'):
                    loc_name = ext_ref[4:]
                else:
                    loc_name = ext_ref
            if model == 'account.invoice' and loc_name == 'number':
                loc_name = 'move_name'
            elif model == 'res.partner' and loc_name == 'region':
                loc_name = 'state_id'
            elif model == 'res.partner' and loc_name == 'postal_code':
                loc_name = 'zip'
            if hasattr(rec, loc_name):
                if loc_name == 'vat' and model in ('res.partner',):
                    value = getattr(rec, loc_name)[2:]
                elif loc_name == 'street' and model in ('res.partner',):
                    value = getattr(rec, loc_name)
                    vals[ext_ref] = vals[ext_ref] + ', 13'
                elif ((loc_name == 'tax_id' and model == 'sale.order.line') or
                      (loc_name == 'invoice_line_tax_ids' and
                       model == 'account.invoice.line')):
                    id = clodoo.searchL8(ctx, 'account.tax',
                                         [('description', '=', vals[ext_ref]),
                                          ('company_id', '=', company_id)])
                    if not rec[loc_name] or id != [x.id for x in rec[loc_name]]:
                        raise IOError('!!Invalid VAT code!')
                    continue
                elif ext_ref == 'state':
                    value = getattr(rec, loc_name)
                    vals[ext_ref] = 'draft'
                else:
                    try:
                        value = getattr(rec, loc_name).id
                    except BaseException:
                        value = getattr(rec, loc_name)
                    if (ext_ref != 'vg7_id' and
                            ext_ref.startswith('vg7_')):
                        if loc_name == 'product_id':
                            if value in TNL['product.product']['LOC']:
                                value = TNL['product.product']['LOC'][value]
                        elif loc_name == 'order_id':
                            if value in TNL['sale.order']['LOC']:
                                value = TNL['sale.order']['LOC'][value]
                        elif loc_name == 'invoice_id':
                            if value in TNL['account.invoice']['LOC']:
                                value = TNL['account.invoice']['LOC'][value]
                        elif loc_name == 'partner_id':
                            if value in TNL['res.partner']['LOC']:
                                value = TNL['res.partner']['LOC'][value]
                    elif model == 'res.partner' and loc_name == 'country_id':
                        if value in TNL['res.country']['LOC']:
                            value = TNL['res.country']['LOC'][value]
                    elif model == 'res.partner' and loc_name == 'state_id':
                        value = clodoo.browseL8(ctx,
                            'res.country.state', value).name.upper()
                if value != vals[ext_ref]:
                    raise IOError('!!Invalid field %s.%s!' % (model, loc_name))

    def check_country(ctx, TNL, country_id, vals):
        general_check(ctx, TNL, 'res.country', country_id, vals)

    def check_country_state(ctx, TNL, country_state_id, vals):
        general_check(ctx, TNL, 'res.country.state', country_state_id, vals)

    def write_country(ctx, TNL, vg7_id=None, code=None, name=None):
        model = 'res.country'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}
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
        if isinstance(vg7_id, basestring):
            TNL[model]['LOC'][country_id] = int(vg7_id)
            TNL[model]['EXT'][int(vg7_id)] = country_id
        else:
            TNL[model]['LOC'][country_id] = vg7_id
            TNL[model]['EXT'][vg7_id] = country_id
        check_country(ctx, TNL, country_id, vals)

        model = 'res.country.state'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}

        vg7_id = vg7_id or 11
        code = 'TO'
        name = 'Torino'
        vals = {
            'country_id': country_id,
            'code': code,
            'name': name,
        }
        country_state_id = clodoo.executeL8(ctx,
                                            model,
                                            'synchro',
                                            vals)
        check_country_state(ctx, TNL, country_state_id, vals)

        vg7_id = vg7_id or 2
        code = 'MI'
        name = 'Milano'
        vals = {
            'code': code,
            'name': name,
        }
        country_state_id = clodoo.executeL8(ctx,
                                            model,
                                            'synchro',
                                            vals)
        check_country_state(ctx, TNL, country_state_id, vals)

        return vg7_id

    def check_product(ctx, TNL, product_id, vals):
        general_check(ctx, TNL, 'product.product', product_id, vals)

    def write_product(ctx, TNL, company_id, vg7_id=None, code=None, name=None):
        model = 'product.product'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}
        vg7_id = vg7_id or 1
        code = code or 'A'
        name = name or 'Product A'
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
        TNL[model]['LOC'][product_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = product_id
        check_product(ctx, TNL, product_id, vals)
        return vg7_id

    def check_partner(ctx, TNL, partner_id, vals):
        general_check(ctx, TNL, 'res.partner', partner_id, vals)

    def write_partner(ctx, TNL, company_id, vg7_id=None, name=None):
        model = 'res.partner'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}
        vg7_id = vg7_id or 7
        if vg7_id == 2:
            vals = {
                'vg7_id': vg7_id,
                'id': env_ref(ctx, 'z0bug.res_partner_2'),
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
                'company_id': company_id,
                'vg7_id': vg7_id,
                'vg7:company': name,
                'vg7:street': 'Via Porta Nuova',
                'vg7:street_number': '13',
                'vg7:postal_code': '10100',
                'vg7:city': 'Torino',
                'vg7:country_id': 39,
                'vg7:region': 'TORINO',
            }
        if vg7_id == 7:
            vals['vg7:piva'] = '00385870480'
        partner_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        TNL[model]['LOC'][partner_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = partner_id
        check_partner(ctx, TNL, partner_id, vals)
        return vg7_id

    def check_sale_order(ctx, TNL, order_id, vals):
        general_check(ctx, TNL, 'sale.order', order_id, vals)

    def check_sale_order_line(ctx, TNL, line_id, vals):
        general_check(ctx, TNL, 'sale.order.line', line_id, vals)

    def write_sale_order(ctx, TNL, company_id, partner_id=None,
                         vg7_order_id=None, state=None):
        model = 'sale.order'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}

        partner_id = partner_id or ctx[
            'odoo_session'].env.ref('z0bug.res_partner_2').id
        vg7_id = vg7_order_id or 1
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'partner_id': partner_id,
        }
        if state:
            vals['state'] = state
            vals['vg7_partner_id'] = 2
        # Search for sale order if connector uninstalled
        ids = clodoo.searchL8(ctx, model,
                              [('name', '=', 'SO002'),
                               ('vg7_id', '=', False)])
        if ids:
            vals['name'] = 'SO002'
        order_id = clodoo.executeL8(ctx,
                                    model,
                                    'synchro',
                                    vals)
        TNL[model]['LOC'][order_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = order_id
        check_sale_order(ctx, TNL, order_id, vals)

        model = 'sale.order.line'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}
        vg7_order_id = vg7_id
        vg7_id = vg7_order_id * 100
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_order_id': vg7_order_id,
            'partner_id': partner_id,
            'name': 'Product A',
            'vg7_product_id': ctx['vg7_id_product_a'],
            'price_unit': 10.50,
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        TNL[model]['LOC'][line_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = line_id
        check_sale_order_line(ctx, TNL, line_id, vals)

        print('Write %s ..' % model)
        vg7_id = vg7_order_id * 100 + 1
        # Field partner_id does not exit: test to avoid crash
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_order_id': vg7_order_id,
            'partner_id': partner_id,
            'name': 'Product B',
            'vg7_product_id': ctx['vg7_id_product_b'],
            'price_unit': 25.50,
            'tax_id': '22v',
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        TNL[model]['LOC'][line_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = line_id
        check_sale_order_line(ctx, TNL, line_id, vals)

        if not state:
            print('Write %s ..' % model)
            vg7_id = vg7_order_id * 100 + 2
            vals = {
                'vg7_id': vg7_id,
                'vg7_order_id': vg7_order_id,
                'partner_id': partner_id,
                'name': 'Product MISC',
                'product_id': ctx['vg7_id_product_x'],
                'price_unit': 12.34,
                'tax_id': '22v',
            }
            line_id = clodoo.executeL8(ctx,
                                       model,
                                       'synchro',
                                       vals)
            TNL[model]['LOC'][line_id] = vg7_id
            TNL[model]['EXT'][vg7_id] = line_id
            check_sale_order_line(ctx, TNL, line_id, vals)

        id = clodoo.executeL8(ctx,
                              'sale.order',
                              'commit',
                              order_id)
        if id < 0:
            raise IOError('!!Commit Failed!')
        rec = clodoo.browseL8(ctx, 'sale.order', order_id)
        if state:
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
            if len(rec['order_line']) != 2:
                raise IOError('!!Invalid # of details!')
        else:
            if len(rec['order_line']) != 3:
                raise IOError('!!Invalid # of details!')
        return vg7_id

    def check_invoice(ctx, TNL, invoice_id, vals):
        general_check(ctx, TNL, 'account.invoice', invoice_id, vals)

    def check_invoice_line(ctx, TNL, line_id, vals):
        general_check(ctx, TNL, 'account.invoice.line', line_id, vals)

    def write_invoice(ctx, TNL, company_id, partner_id=None,
                      vg7_invoice_id=None, state=None):
        model = 'account.invoice'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}

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
                              [('number', '=', 'FAT/2019/0006'),
                               ('vg7_id', '=', False)])
        if ids:
            vals['number'] = 'FAT/2019/0006'
        invoice_id = clodoo.executeL8(ctx,
                                      model,
                                      'synchro',
                                      vals)
        TNL[model]['LOC'][invoice_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = invoice_id
        check_invoice(ctx, TNL, invoice_id, vals)

        model = 'account.invoice.line'
        print('Write %s ..' % model)
        if model not in TNL:
            TNL[model] = {}
            TNL[model]['LOC'] = {}
            TNL[model]['EXT'] = {}
        vg7_invoice_id = vg7_id
        vg7_id = vg7_invoice_id * 200
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product A',
            'vg7_product_id': ctx['vg7_id_product_a'],
            'price_unit': 10.50,
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        TNL[model]['LOC'][line_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = line_id
        check_invoice_line(ctx, TNL, line_id, vals)

        print('Write %s ..' % model)
        vg7_id = vg7_invoice_id * 200 + 1
        # Field partner_id does not exit: test to avoid crash
        vals = {
            'company_id': company_id,
            'vg7_id': vg7_id,
            'vg7_invoice_id': vg7_invoice_id,
            'partner_id': partner_id,
            'name': 'Product B',
            'vg7_product_id': ctx['vg7_id_product_b'],
            'price_unit': 25.50,
            'invoice_line_tax_ids': '22v',
        }
        line_id = clodoo.executeL8(ctx,
                                   model,
                                   'synchro',
                                   vals)
        TNL[model]['LOC'][line_id] = vg7_id
        TNL[model]['EXT'][vg7_id] = line_id
        check_invoice_line(ctx, TNL, line_id, vals)

        if not state:
            print('Write %s ..' % model)
            vg7_id = vg7_invoice_id * 200 + 2
            vals = {
                'vg7_id': vg7_id,
                'vg7_invoice_id': vg7_invoice_id,
                'partner_id': partner_id,
                'name': 'Product MISC',
                'product_id': ctx['vg7_id_product_x'],
                'price_unit': 12.34,
                'invoice_line_tax_ids': '22v',
            }
            line_id = clodoo.executeL8(ctx,
                                       model,
                                       'synchro',
                                       vals)
            TNL[model]['LOC'][line_id] = vg7_id
            TNL[model]['EXT'][vg7_id] = line_id
            check_invoice_line(ctx, TNL, line_id, vals)

        id = clodoo.executeL8(ctx,
                              'account.invoice',
                              'commit',
                              invoice_id)
        if id < 0:
            raise IOError('!!Commit Failed!')
        rec = clodoo.browseL8(ctx, 'account.invoice', invoice_id)
        if state:
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
            if len(rec['invoice_line_ids']) != 2:
                raise IOError('!!Invalid # of details!')
        else:
            if len(rec['invoice_line_ids']) != 3:
                raise IOError('!!Invalid # of details!')
        return vg7_id

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')

    TNL = {}
    TNL['LOC'] = {}
    TNL['EXT'] = {}

    partner_MR_ids = clodoo.searchL8(ctx, 'res.partner',
                                    [('name','like','Rossi')])
    if partner_MR_ids:
        for id in partner_MR_ids:
            partner = clodoo.browseL8(ctx, 'res.partner', id)
            if partner.split_mode != 'LF':
                clodoo.browseL8(ctx, 'res.partner', id,
                                {'splitmode': 'LF',
                                 'name': 'Rossi Mario'})
    ctx['partner_MR_ids'] = partner_MR_ids

    product_x_ids = clodoo.searchL8(ctx, 'product.product',
                                    [('default_code','like','MISC')])
    if product_x_ids:
        ctx['vg7_id_product_x'] = product_x_ids[0]
    else:
        ctx['vg7_id_product_x'] = clodoo.searchL8(
            ctx, 'product.product', [])[0]

    # Repeat 2 times to check correct synchronization
    write_country(ctx, TNL)
    write_country(ctx, TNL, vg7_id='39')

    # Repeat 2 times to check correct synchronization
    vg7_id_product_a = write_product(ctx, TNL, company_id)
    vg7_id_product_a = write_product(ctx, TNL, company_id, vg7_id='1')

    vg7_id_product_b = write_product(ctx, TNL, company_id,
                                     vg7_id=2, code='B', name='Product B')
    ctx['vg7_id_product_a'] = vg7_id_product_a
    ctx['vg7_id_product_b'] = vg7_id_product_b

    # Repeat 2 times to check correct synchronization
    write_partner(ctx, TNL, company_id)
    write_partner(ctx, TNL, company_id)

    write_partner(ctx, TNL, company_id, vg7_id=17)
    # Partner fo sale order & invoice
    write_partner(ctx, TNL, company_id, vg7_id=2)

    # Repeat 2 times with different state
    write_sale_order(ctx, TNL, company_id)
    write_sale_order(ctx, TNL, company_id, state='sale')

    # Repeat 2 times with different state
    write_invoice(ctx, TNL, company_id)
    write_invoice(ctx, TNL, company_id, state='open')

    write_country(ctx, TNL)


def test_synchro_mdb(ctx):

    def bulk_cmd(src_ctx, tgt_ctx, model):
        return ['python',
                os.path.join(os.path.dirname(__file__), 'migrate_odoo_db.py'),
                '-w', src_ctx['from_confn'],
                '-z', src_ctx['from_dbname'],
                '-d', tgt_ctx['db_name'],
                '-c', tgt_ctx['conf_fn'],
                '-m', model]

    def run_traced(cmd):
        print('>>> %s' % ' '.join(cmd))
        os.system(' '.join(cmd))

    def general_check(src_ctx, tgt_ctx, model, id):
        if not id or id < 1:
            raise IOError('!!Syncro %s Failed!' % model)
        src_rec = clodoo.browseL8(src_ctx, model, id,
                                  context={'lang': 'en_US'})
        if model in ('res.country', 'account.account'):
            code = src_rec.code
            tgt_ids = clodoo.searchL8(tgt_ctx, model, [('code', '=', code)])
            if not tgt_ids or len(tgt_ids) != 1:
                raise IOError('!!Syncro %s Failed!' % model)
            tgt_rec = clodoo.browseL8(tgt_ctx, model, tgt_ids[0])
            if src_rec.code != tgt_rec.code:
                raise IOError('!!Syncro %s Failed!' % model)
        elif model in ('account.account.type', ):
            name = src_rec.name
            tgt_ids = clodoo.searchL8(tgt_ctx, model, [('name', '=', name)])
            if not tgt_ids or len(tgt_ids) != 1:
                raise IOError('!!Syncro %s Failed!' % model)
            tgt_rec = clodoo.browseL8(tgt_ctx, model, tgt_ids[0],
                                      context={'lang': 'en_US'})
            if src_rec.name != tgt_rec.name:
                raise IOError('!!Syncro %s Failed!' % model)
        else:
            raise IOError('!!Syncro %s Failed!' % model)
        if model in ('account.account', ):
            if src_rec.name != tgt_rec.name:
                raise IOError('!!Syncro %s Failed!' % model)

    def check_country(src_ctx, tgt_ctx, country_id):
        general_check(src_ctx, tgt_ctx, 'res.country', country_id)

    def write_country(src_ctx, tgt_ctx, code=None, name=None):
        model = 'res.country'
        print('Write %s ..' % model)
        code = code or 'IT'
        ids = clodoo.searchL8(src_ctx, model, [('code', '=', code)])
        if not ids:
            raise 'Test interrupted due record %s not found in %s' % (code,
                                                                      model)
        cmd = bulk_cmd(src_ctx, tgt_ctx, model)
        cmd.append('-i')
        cmd.append(str(ids)[1:-1])
        run_traced(cmd)
        return ids[0]

    def check_account_type(src_ctx, tgt_ctx, acc_id):
        general_check(src_ctx, tgt_ctx, 'account.account.type', acc_id)

    def write_account_type(src_ctx, tgt_ctx, code=None, name=None):
        model = 'account.account.type'
        print('Write %s ..' % model)
        ids = clodoo.searchL8(src_ctx, model, [])
        if not ids:
            raise 'Test interrupted due record %s not found in %s' % (code,
                                                                      model)
        cmd = bulk_cmd(src_ctx, tgt_ctx, model)
        cmd.append('-i')
        cmd.append(str(ids[0]))
        run_traced(cmd)
        return ids[0]

    def check_account_account(src_ctx, tgt_ctx, acc_id):
        general_check(src_ctx, tgt_ctx, 'account.account', acc_id)

    def write_account_account(src_ctx, tgt_ctx, company_id,
                              code=None, name=None):
        model = 'account.account'
        print('Write %s ..' % model)
        ids = clodoo.searchL8(
            src_ctx, model, [('code', '=', '152100'),
                             ('company_id', '=', company_id)])
        if not ids:
            raise 'Test interrupted due record %s not found in %s' % (code,
                                                                      model)
        cmd = bulk_cmd(src_ctx, tgt_ctx, model)
        cmd.append('-i')
        cmd.append(str(ids[0]))
        cmd.append('-C')
        run_traced(cmd)
        return ids[0]

    print('Test synchro migrate DB')
    if not ctx['from_confn'] or not ctx['from_dbname']:
        print('Missed multi-DB parameter: -w -z')
        return
    tgt_ctx = ctx
    src_ctx = ctx.copy()
    src_ctx['db_name'] = src_ctx['from_dbname']
    src_ctx['conf_fn'] = src_ctx['from_confn']
    uid, src_ctx = clodoo.oerp_set_env(ctx=src_ctx)
    src_company_id = env_ref(src_ctx, 'z0bug.mycompany')
    if not src_company_id:
        raise IOError('!!Internal error: no company to test found in src!')
    tgt_company_id = env_ref(tgt_ctx, 'z0bug.mycompany')
    if not tgt_company_id:
        raise IOError('!!Internal error: no company to test found in tgt!')

    src_ctx['partner_MR_ids'] = clodoo.searchL8(src_ctx, 'res.partner',
                                                [('name','like','Rossi')])
    product_x_ids = clodoo.searchL8(src_ctx, 'product.product',
                                    [('default_code','like','MISC')])
    if product_x_ids:
        src_ctx['vg7_id_product_x'] = product_x_ids[0]
    else:
        src_ctx['vg7_id_product_x'] = clodoo.searchL8(
            src_ctx, 'product.product', [])[0]

    country_id = write_country(src_ctx, tgt_ctx)
    check_country(src_ctx, tgt_ctx,country_id)

    acc_type_id = write_account_type(src_ctx, tgt_ctx)
    check_account_type(src_ctx, tgt_ctx, acc_type_id)

    account_id = write_account_account(src_ctx, tgt_ctx, src_company_id)
    check_account_account(src_ctx, tgt_ctx, account_id)


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
                if sale_line.order_id.partner_id.id != invoice.partner_id.id:
                    os0.wlog('!!!!! Invoice %s (%d) partner differs from '
                             'sale order %s (%d) partner!!!!!' % (
                                 invoice.number,
                                 invoice.id,
                                 sale_line.order_id.name,
                                 sale_line.order_id.id,))
                    err_ctr += 1
                    clodoo.writeL8(ctx, model_invline, invoice_line.id,
                                   {'sale_line_ids': [(3, sale_line.id)]})
        for invoice_line in invoice.invoice_line_ids:
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
                        invoice_line.ddt_line_id.sale_line_id.order_id.\
                        partner_id.id != invoice.partner_id.id):
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


def set_comment_on_invoice(ctx):
    model = 'account.invoice'
    date = raw_input('Date invoice to update (yyyy-mm-dd): ')
    comment = raw_input('Text to insert on invoice comment: ')
    comment = comment.replace('\'', '\\\'')
    ctr = 0
    for inv in clodoo.browseL8(
        ctx, model, clodoo.searchL8(
            ctx,model,[('date_invoice', '=', date)])):
        msg_burst('%s ...' % inv.number)
        clodoo.writeL8(ctx, model, inv.id, {'comment': comment})
        ctr += 1
    print('%d record updated' % ctr)


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
        query = "update account_account set code='%s$' where code = '%s'" % (
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

print('Function avaiable:')
print('  Sale orders                         Account invoices')
print('  - order_commission_by_partner(ctx)  - inv_commission_from_order(ctx)')
print('  - delivery_addr_same_customer(ctx)  - revaluate_due_date_in_invoces(ctx)')
print('                                      - update_einvoice_out_attachment(ctx)')
print('                                      - set_tax_code_on_invoice(ctx)')
print('                                      - set_comment_on_invoice(ctx)')
print('  Purchase orders                     Deliveries/Shipping')
print('  - close_purchase_orders(ctx)        - change_ddt_number(ctx)')
print('                                      - show_empty_ddt(ctx)')
print('  Products/Partners                   RiBA')
print('  - set_products_2_consumable(ctx)    - configure_RiBA(ctx)')
print('  - products_2_delivery_order(ctx)    - manage_riba(ctx)')
print('  Partners/Users                      Commissions')
print('  - deduplicate_partner(ctx)          - create_commission_env(ctx)')
print('  - reset_email_admins(ctx)')
print('  - simulate_user_profile(ctx)')
print('  System                              Other tables')
print('  - show_module_group(ctx)            - print_tax_codes(ctx)')
print('  - clean_translations(ctx)           - set_payment_data_on_report(ctx)')
print('  - configure_email_template(ctx)     - rename_coa(ctx)')
print('  - test_synchro_vg7(ctx)             - display_module(ctx)')
print('  - check_rec_links(ctx)              - reset_report_config(ctx)')

pdb.set_trace()


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


model = 'account.account.type'
for rec in clodoo.browseL8(
    ctx,model,
        clodoo.searchL8(ctx, model, []),
            context={'lang': 'en_US'}):
    print(rec.name)

models = build_table_tree()
for level in range(MAX_DEEP):
    for model in models:
        if models[model].get('level', -1) == level:
            print('%2d %s%s' % (level, ' ' * level, model))
for model in models:
    if models[model].get('level', -1) >= MAX_DEEP:
        print('%s %s (%s)' % ('-' * MAX_DEEP,
                              model,
                              models[model].get('status', '')))

for rec in clodoo.browseL8(ctx,model,clodoo.searchL8(ctx,model,[])):
    print(rec.name)

model = 'account.invoice'
for inv in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model,
        [('type', 'in', ('in_invoice', 'in_refund')),
         ('payment_term_id', '=', False)],order='number')):
    if ((not inv.date_due or inv.date_invoice == inv.date_due) and
            not inv.payment_term_id):
        revaluate_due_date_in_invoces(inv.id)
