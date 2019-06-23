#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import print_function

import sys
import time
import re
import getpass
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


__version__ = "0.3.8.40"


MAX_DEEP = 20
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
            ctx, inv_model, [])):
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
            ctx, ord_model, [])):
        if ord_line.agents:
            clodoo.unlinkL8(ctx, sale_agent_model, ord_line.agents.id)
        rec = []
        for agent in ord_line.order_id.partner_id.agents:
            rec.append({
                'agent': ord_line.order_id.partner_id.agents.id,
                'commission': ord_line.order_id.partner_id.agents.commission.id,
            })
        clodoo.writeL8(ctx, ord_model, ord_line.id,
                       {'agents': [(0, 0, rec[0])]})
        ctr += 1
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


def synchro(ctx, model, vals):
    sts = 0
    ids = []
    if 'id' in vals:
        ids = clodoo.searchL8(ctx, model, [('id', '=', vals['id'])])
        if not ids or ids[0] != vals['id']:
            raise IOError('ID %d does not exist in %s' %
                            vals['id'], model)
        del vals['id']
    # if not ids and 'vg7_id' in vals:
    #     ids = clodoo.searchL8(ctx, model, [('vg7_id', '=', vals['vg7_id'])])
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


def create_RA_config(ctx):
    print('Set withholding tax configuration to test')
    model = 'res.company'
    ids = clodoo.searchL8(ctx, model,
                          [('name', 'ilike', ctx['def_company_name'])],
                          order='id')
    if len(ids) == 0:
        print('No company found!')
        return
    elif len(ids) == 1:
        company_id = ids[0]
    elif len(ids) > 1:
        company_id = ids[1]
    company = clodoo.browseL8(ctx, model, company_id)
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
                            model2, rec2.id, rec2.name, rec.type,
                            get_agent_names(rec.agents)))
                    elif model == 'account.invoice':
                        print('    %s %4d %-32.32s %s' % (
                            model2, rec2.id, rec2.name,
                            get_agent_names_line(rec2.agents)))
                    else:
                        print('    %s %4d %-32.32s %s' % (
                            model2, rec2.id, rec2.name,
                            get_agent_names_line(rec2.agents)))



def reset_email_vg7bot(ctx):
    model = 'res.users'
    model2 = 'res.partner'
    ids = clodoo.searchL8(ctx, model,
                          [('login', '=', 'vg7bot')])
    if len(ids) == 0:
        print('No user found!')
        return
    ctr = 0
    for user in clodoo.browseL8(ctx, model, ids):
        partner_id = user.partner_id.id
        partner = clodoo.browseL8(ctx, model2, partner_id)
        if partner.email != 'noreply@vg7.it':
            clodoo.writeL8(ctx, model2, partner_id, {'email': 'noreply@vg7.it'})
            ctr += 1
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
        if customer.vat in CUSTOMERS:
            CUSTOMERS[customer.vat]['id'] = customer.id
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

if ctx['function']:
    function = ctx['function']
    globals()[function](ctx)
    exit()

print('Function avaiable:')
print('    show_module_group(ctx)')
print('    clean_translations(ctx)')
print('    close_purchse_orders(ctx)')
print('    set_products_2_delivery_order(ctx)')
print('    set_products_2_consumable(ctx)')
print('    order_commission_by_partner(ctx)')
print('    inv_commission_from_order(ctx)')
print('    update_einvoice_out_attachment(ctx)')
print('    revaluate_due_date_in_invoces(ctx)')
print('    print_tax_codes(ctx)')
print('    simulate_user_profile(ctx)')
print('    reset_email_vg7bot(ctx)')
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

pdb.set_trace()
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
