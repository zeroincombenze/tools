#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
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


__version__ = "0.3.8.12"


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
        gid = raw_input('Type res.groups id: ')
        if gid:
            gid = int(gid)
        if gid:
            group = clodoo.browseL8(ctx, model_grp, gid, context={'lang': 'en_US'})
            cid = group.category_id.id
            categ = clodoo.browseL8(ctx, model_ctg, cid, context={'lang': 'en_US'})
            print '%6d) Category %s' % (cid, categ.name)
            for id in clodoo.searchL8(ctx, model_grp, [('category_id', '=', cid)]):
                group = clodoo.browseL8(
                    ctx, model_grp, id, context={'lang': 'en_US'})
                print '%6d) -- Value [%-16.16s] > [%s]' % (id,
                                                           group.name,
                                                           group.full_name)
def clean_translations():
    model = 'ir.translation'
    where = [('lang', '=', 'it_IT'),
             '|',
             ('name', '=', 'ir.module.module,description'),
             ('name', '=', 'ir.module.module,shortdesc')]
    ids = clodoo.searchL8(ctx, model, where)
    print 'unlink %s' % ids
    clodoo.unlinkL8(ctx, model, ids)
    print '%d records deleted' % len(ids)


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
        print po.product_qty,po.qty_received,qty_received,po.qty_invoiced
        if qty_received > 0.0:
            clodoo.writeL8(ctx,model,po.id,{'qty_received': qty_received})
            ctr += 1
    print '%d purchase order lines updated' % ctr

def inv_commission_from_order():
    print 'If missed, copy commission in invoice line from sale order line'
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
    print '%d records updated'


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
    print '%d product templates updated' % ctr

    model = 'product.product'
    ctr=0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        if pp.purchase_method != 'purchase':
            clodoo.writeL8(ctx, model, pp.id, {'purchase_method':'purchase'})
            ctr += 1
        if pp.invoice_delivery != 'order':
            clodoo.writeL8(ctx, model, pp.id, {'invoice_delivery':'order'})
            ctr += 1
    print '%d products updated' % ctr


print 'Function avaiable:'
print '    show_module_group()'
print '    clean_translations()'
print '    close_purchse_orders()'
print '    set_products_2_delivery_order()'
print '    inv_commission_from_order()'

pdb.set_trace()
