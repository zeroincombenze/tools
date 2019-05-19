#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, unicode_literals
from __future__ import print_function

import sys
import time
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


__version__ = "0.3.8.23"


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


def show_module_group():
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
            for id in clodoo.searchL8(ctx, model_grp, [('category_id', '=', cid)]):
                group = clodoo.browseL8(
                    ctx, model_grp, id, context={'lang': 'en_US'})
                ir_md = clodoo.browseL8(ctx, model_ir_md,
                    clodoo.searchL8(ctx, model_ir_md,
                                    [('model', '=', model_grp),
                                     ('res_id', '=', id)]))
                print('%6d) -- Value [%-16.16s] > [%-32.32s] as "%s.%s"' % (
                    id,
                    group.name,
                    group.full_name,
                    ir_md.module,
                    ir_md.name))


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


def print_user_profile(ctx):

    def get_agent_names(agents):
        agent_names = []
        for agent in agents:
            agent_names.append(agent.name)
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
        for rec in clodoo.browseL8(ctx, model,
                                   clodoo.searchL8(ctx, model, [])):
            if model == 'res.partner':
                print('%s %4d %-16.16s %s %s' % (
                    model, rec.id, rec.name, rec.agent,
                    get_agent_names(rec.agents)))
            elif model == 'account.invoice':
                print('%s %4d %-16.16s %s' % (
                    model, rec.id, rec.number, get_agent_names(rec.agents)))
            else:
                print('%s %4d %-16.16s %s' % (
                    model, rec.id, rec.name, get_agent_names(rec.agents)))


def simulate_user_profile():
    dummy = raw_input('Username ID to simulate: ')
    user = clodoo.browseL8(ctx, 'res.users', int(dummy))
    print('***** %s *****' % user.name)
    model_ir = 'ir.rule'
    for model in 'sale.order', 'account.invoice', 'res.partner':
        print('\n[%s]' % model)
        model_id = clodoo.searchL8(ctx, 'ir.model', [('model', '=', model)])
        for rule in clodoo.browseL8(
                ctx, model_ir, clodoo.searchL8(
                    ctx, model_ir, [('model_id', '=', model_id)])):
            print('\n[%s] %s' % (model, rule.name))
            for rec in clodoo.browseL8(ctx, model,
                                       clodoo.searchL8(ctx,
                                                       model,
                                                       rule.domain)):
                if model == 'res.partner':
                    print('%s %3d %-16.16s %s' % (
                        model, rec.id, rec.name, rec.agent))
                elif model == 'account.invoice':
                    print('%s %3d %-16.16s %s' % (
                        model, rec.id, rec.number, rec.agents))
                else:
                    print('%s %3d %-16.16s %s' % (
                        model, rec.id, rec.name, rec.agents))

print('Function avaiable:')
print('    show_module_group()')
print('    clean_translations()')
print('    close_purchse_orders()')
print('    set_products_2_delivery_order()')
print('    inv_commission_from_order()')
print('    update_einvoice_out_attachment()')
print('    revaluate_due_date_in_invoces()')
print('    print_tax_codes()')
print('    print_user_profile(ctx)')
print('    simulate_user_profile()')
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

pdb.set_trace()

print_user_profile(ctx)
simulate_user_profile()

for rec in clodoo.browseL8(ctx,model,clodoo.searchL8(ctx,model,[])):
    print(rec.name)

model = 'account.invoice'
for inv in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model,
        [('type', 'in', ('in_invoice', 'in_refund')),
         ('payment_term_id', '=', False)],order='number')):
    if ((not inv.date_due or inv.date_invoice == inv.date_due) and
            not inv.payment_term_id):
        revaluate_due_date_in_invoces(inv.id)
