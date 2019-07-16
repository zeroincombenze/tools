#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import print_function

import sys
import time
import re
import getpass
from symbol import except_clause
from cgitb import reset
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


__version__ = "0.3.8.43"


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
parser.add_argument("-x", "--exec",
                    help="internal function to execute",
                    dest="function",
                    metavar="python_name",
                    default='')
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)
msg_time = time.time()


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
        clodoo.writeL8(ctx, model, ids, vals)
    else:
        ids = [clodoo.createL8(ctx, model, vals)]
    return ids


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


def close_purchse_orders(ctx):
    print('Close purchase orders')
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


def inv_commission_from_order(ctx):
    print('If missed, copy commission in invoice lines from sale order lines')
    inv_model = 'account.invoice.line'
    ord_model = 'sale.order.line'
    agt_model = 'account.invoice.line.agent'
    ctr = 0
    for inv_line in clodoo.browseL8(
        ctx, inv_model, clodoo.searchL8(
            ctx, inv_model, [], order='invoice_id')):
        msg_burst('%s ...' % inv_line.invoice_id.name)
        if inv_line.agents.amount:
            continue
        for ord_line in inv_line.sale_line_ids:
            if not ord_line.agents.amount:
                continue
            agents = [(0, 0,
                       {'agent': x.agent.id,
                        'commission':
                            x.commission.id}) for x in ord_line.agents]
            clodoo.writeL8(
                ctx, inv_model, inv_line.id,
                {'agents': agents})
            ctr += 1
    inv_model = 'account.invoice'
    for invoice in clodoo.browseL8(
        ctx, inv_model, clodoo.searchL8(
            ctx, inv_model, [])):
        msg_burst('%s ...' % invoice.number)
        clodoo.writeL8(ctx, inv_model, invoice.id,
            {'number': invoice.number})
    print('%d invoice lines updated' % ctr)


def order_commission_by_partner(ctx):
    ctr = 0
    print('If missed, set commission in order lines from customer')
    ord_model = 'sale.order.line'
    sale_agent_model = 'sale.order.line.agent'
    agt_model = 'account.invoice.line.agent'
    ctr = 0
    for ord_line in clodoo.browseL8(
        ctx, ord_model, clodoo.searchL8(
            ctx, ord_model, [], order='order_id')):
        msg_burst('%s ...' % ord_line.order_id.name)
        if ord_line.agents:
            clodoo.unlinkL8(ctx, sale_agent_model, ord_line.agents.id)
        rec = []
        for agent in ord_line.order_id.partner_id.agents:
            rec.append({
                'agent': ord_line.order_id.partner_id.agents.id,
                'commission': ord_line.order_id.partner_id.agents.commission.id,
            })
        if rec:
            clodoo.writeL8(ctx, ord_model, ord_line.id,
                           {'agents': [(0, 0, rec[0])]})
            ctr += 1
    ord_model = 'sale.order'
    for order in clodoo.browseL8(
        ctx, ord_model, clodoo.searchL8(
            ctx, ord_model, [])):
        msg_burst('%s ...' % order.name)
        clodoo.writeL8(ctx, ord_model, order.id,
            {'name': order.name})
    print('%d sale order lines updated' % ctr)


def set_products_2_delivery_order(ctx):
    print('Set purchase methos to purchase in all products')
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
    print('Set consumable in the stockable products')
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


def delivery_address_same_customer(ctx):
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


def manage_riba(ctx):
    print('Do various actions on RiBA list')
    riba_id = False
    while not riba_id:
        riba_id = raw_input('RiBA list id: ')
        if not riba_id:
            return
        riba_id = int(riba_id)
        riba_list = clodoo.browseL8(ctx, 'riba.distinta', riba_id)
        print('Riba list # %s' % riba_list.name)
        print('Riba list state: %s' % riba_list.state)
        if riba_list.state == 'accepted':
            action = raw_input('Action: Cancel,Draft,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'C':
                print('Cancelling RiBA list ..')
                for move in riba_list.acceptance_move_ids:
                    clodoo.executeL8(ctx,
                                     'account.move',
                                     'button_cancel',
                                      move.id)
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
                            print('!!Move unceconiliable!')
                for move in riba_list.acceptance_move_ids:
                    clodoo.unlinkL8(ctx,
                                    'account.move',
                                    move.id)
                for riba in riba_list.line_ids:
                    clodoo.writeL8(ctx, 'riba.distinta.line', riba.id,
                                   {'state': 'draft',})
                clodoo.writeL8(ctx, 'riba.distinta', riba_id,
                               {'state': 'draft',
                                'date_accepted': False})
                try:
                    clodoo.executeL8(ctx,
                                     'riba.distinta',
                                     'riba_cancel',
                                     riba_id)
                    # clodoo.executeL8(ctx,
                    #                  'riba.distinta',
                    #                  'confirm',
                    #                  riba_id)
                except BaseException:
                    pass
            elif action == 'D':
                for riba in riba_list.line_ids:
                    clodoo.writeL8(ctx, 'riba.distinta.line', riba.id,
                                   {'state': 'draft',})
                clodoo.writeL8(ctx, 'riba.distinta', riba_id,
                               {'state': 'draft',
                                'date_accepted': False})
        elif riba_list.state == 'draft':
            action = raw_input('Action: Accepted,Quit: ')
            action = action[0].upper() if action else 'Q'
            if action == 'A':
                clodoo.writeL8(ctx, 'riba.distinta', riba_id,
                               {'state': 'accepted'})
        riba_id = ''

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

def create_RiBA_config(ctx):
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
                elif (model in ('res.country', 'product.product') and
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
        if vg7_id == 17:
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

        id = clodoo.executeL8(ctx,
                              'sale.order',
                              'commit',
                              order_id)
        if id < 0:
            raise IOError('!!Commit Failed!')
        if state:
            rec = clodoo.browseL8(ctx, 'sale.order', order_id)
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
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

        id = clodoo.executeL8(ctx,
                              'account.invoice',
                              'commit',
                              invoice_id)
        if id < 0:
            raise IOError('!!Commit Failed!')
        if state:
            rec = clodoo.browseL8(ctx, 'account.invoice', invoice_id)
            if rec['state'] != state:
                raise IOError('!!Invalid state!')
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

    # Repeat 2 times with different state
    write_sale_order(ctx, TNL, company_id)
    write_sale_order(ctx, TNL, company_id, state='sale')

    # Repeat 2 times with different state
    write_invoice(ctx, TNL, company_id)
    write_invoice(ctx, TNL, company_id, state='open')


if ctx['function']:
    function = ctx['function']
    globals()[function](ctx)
    exit()

print('Function avaiable:')
print('    show_module_group(ctx)')
print('    clean_translations(ctx)')
print('    close_purchse_orders(ctx)')
print('    inv_commission_from_order(ctx)')
print('    order_commission_by_partner(ctx)')
print('    set_products_2_delivery_order(ctx)')
print('    set_products_2_consumable(ctx)')
print('    update_einvoice_out_attachment(ctx)')
print('    revaluate_due_date_in_invoces(ctx)')
print('    delivery_address_same_customer(ctx)')
print('    print_tax_codes(ctx)')
print('    set_tax_code_on_invoice(ctx)')
print('    set_payment_data_on_report(ctx)')
print('    simulate_user_profile(ctx)')
print('    reset_email_admins(ctx)')
print('    show_empty_ddt(ctx)')
print('    change_ddt_number(ctx)')

pdb.set_trace()
test_synchro_vg7(ctx)


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


pdb.set_trace()

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
