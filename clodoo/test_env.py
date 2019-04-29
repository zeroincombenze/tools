#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, unicode_literals
from __future__ import print_function

import sys
from symbol import except_clause
# import oerplib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib
import pdb


__version__ = "0.3.8.16"


PAY_MOVE_STS_2_DRAFT = ['posted', ]
INVOICES_STS_2_DRAFT = ['open', 'paid']
STATES_2_DRAFT = ['open', 'paid', 'posted']

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
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)

def show_module_group():
    model_grp = 'res.groups'
    model_ctg = 'ir.module.category'
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
            for id in clodoo.searchL8(ctx, model_grp, [('category_id', '=', cid)]):
                group = clodoo.browseL8(
                    ctx, model_grp, id, context={'lang': 'en_US'})
                print('%6d) -- Value [%-16.16s] > [%s]' % (id,
                                                           group.name,
                                                           group.full_name))
def clean_translations():
    model = 'ir.translation'
    where = [('lang', '=', 'it_IT'),
             '|',
             ('name', '=', 'ir.module.module,description'),
             ('name', '=', 'ir.module.module,shortdesc')]
    ids = clodoo.searchL8(ctx, model, where)
    print('unlink %s' % ids)
    clodoo.unlinkL8(ctx, model, ids)
    print('%d records deleted' % len(ids))


def close_purchse_orders():
    model='purchase.order.line'
    ctr=0
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

def inv_commission_from_order():
    print('If missed, copy commission in invoice line from sale order line')
    inv_model = 'account.invoice.line'
    ord_model = 'sale.order.line'
    agt_model = 'account.invoice.line.agent'
    ctr = 0
    for inv_line in clodoo.browseL8(ctx, inv_model, clodoo.searchL8(
        ctx, inv_model, [])):
        if not inv_line.agents.amount:
            for ord_line in inv_line.sale_line_ids:
                if ord_line.agents.amount:
                    agents = [(0, 0, {'agent': x.agent.id,
                                      'commission': x.commission.id}) for x in ord_line.agents]
                    clodoo.writeL8(
                        ctx, inv_model, inv_line.id,
                        {'agents': agents})
                    ctr += 1
    print('%d records updated')


def set_products_2_delivery_order():
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


def update_einvoice_out_attachment():
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

def revaluate_due_date_in_invoces(inv_id):
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


def print_tax_codes():
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


print('Function avaiable:')
print('    show_module_group()')
print('    clean_translations()')
print('    close_purchse_orders()')
print('    set_products_2_delivery_order()')
print('    inv_commission_from_order()')
print('    update_einvoice_out_attachment()')
print('    revaluate_due_date_in_invoces()')
print('    print_tax_codes()')

pdb.set_trace()
model = 'account.invoice'
for inv in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model,
        [('type', 'in', ('in_invoice', 'in_refund')),
         ('payment_term_id', '=', False)],order='number')):
    if ((not inv.date_due or inv.date_invoice == inv.date_due) and
            not inv.payment_term_id):
        revaluate_due_date_in_invoces(inv.id)
