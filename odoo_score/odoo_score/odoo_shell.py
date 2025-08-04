#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random

from past.builtins import long

import csv
import getpass
import re
import os
import sys
import time
from builtins import *  # noqa
from builtins import input
from datetime import date, datetime, timedelta
# import itertools

from future import standard_library

from os0 import os0  # pylint: disable=import-error
from python_plus import _b

try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib

import pdb  # pylint: disable=deprecated-module

standard_library.install_aliases()  # noqa: E402


__version__ = '2.0.11'


MAX_DEEP = 20
PAY_MOVE_STS_2_DRAFT = ['posted']
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
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if t > 4:
        print(text, '\r')
        msg_time = time.time()


def env_ref(ctx, xref, retxref_id=None):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        model = 'ir.model.data'
        ids = clodoo.searchL8(
            ctx, model, [('module', '=', xrefs[0]), ('name', '=', xrefs[1])]
        )
        if ids:
            if retxref_id:
                return ids[0]
            return clodoo.browseL8(ctx, model, ids[0]).res_id
    return False


def add_xref(ctx, xref, model, res_id):
    xrefs = xref.split('.')
    if len(xrefs) != 2:
        raise ('Invalid xref %s' % xref)
    vals = {'module': xrefs[0], 'name': xrefs[1], 'model': model, 'res_id': res_id}
    model = 'ir.model.data'
    id = env_ref(ctx, xref, retxref_id=True)
    if not id:
        return clodoo.createL8(ctx, model, vals)
    clodoo.writeL8(ctx, model, id, vals)
    return id


def _synchro(ctx, model, vals):
    # sts = 0
    ids = []
    if 'id' in vals:
        ids = clodoo.searchL8(ctx, model, [('id', '=', vals['id'])])
        if not ids or ids[0] != vals['id']:
            raise IOError('ID %d does not exist in %s' % (vals['id'], model))
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
    tax_id = clodoo.searchL8(
        ctx,
        'account.tax',
        [('description', '=', code), ('company_id', '=', company_id)],
    )
    if not tax_id and code.startswith('a17c'):
        tax_id = clodoo.searchL8(
            ctx,
            'account.tax',
            [('description', '=', 'a%s' % code), ('company_id', '=', company_id)],
        )
    if tax_id:
        tax_id = tax_id[0]
    else:
        tax_id = False
    return tax_id


def param_date(param, date_field=None):
    """Return record ids of model by user request;
    param values:
        'yyyy-mm-dd': specific date
        '+n': from today + n days
        '': from current month (if day >= 15) or from prior month (if day < 15)
        'n': record n of model
        '[n,..]': records n ... of model
    date_field: Odoo model field with date to manage (means return domain)
    """
    if param == '?':
        domain = False
    elif not param:
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
        domain = [(date_field, '>=', from_date)]
    elif param.isdigit():
        domain = [('id', '=', int(param))]
    elif "," in param:
        domain = [('id', 'in', [int(x) for x in param.split(",")])]
    elif param and param.startswith('+'):
        date_ids = date.strftime(
            date.today() - timedelta(eval(param)), '%04Y-%02m-%02d'
        )
        domain = [(date_field, '>=', date_ids)]
    elif ".." in param:
        domain = [(date_field, '>=', param.split("..")[0]),
                  (date_field, '<=', param.split("..")[1])]
    else:
        domain = [(date_field, '>=', param)]
    return domain


def param_product_agent(param):
    product_id = agent_id = False
    if param:
        if param.startswith('P'):
            product_id = eval(param[1:])
        elif param.startswith('A'):
            agent_id = eval(param[1:])
    return product_id, agent_id


def show_module_group(ctx):
    print('Show group infos and external names')
    model_grp = 'res.groups'
    model_ctg = 'ir.module.category'
    model_ir_md = 'ir.model.data'
    gid = True
    while gid:
        gid = input('Res.groups id: ')
        if gid:
            gid = eval(gid)
        if gid:
            group = clodoo.browseL8(ctx, model_grp, gid, context={'lang': 'en_US'})
            cid = group.category_id.id
            categ = clodoo.browseL8(ctx, model_ctg, cid, context={'lang': 'en_US'})
            print('%d) Category %s' % (cid, categ.name))
            uniq_field = []
            grp_ids = clodoo.searchL8(ctx, model_grp,
                                      [('category_id', '=', cid)])
            for group in clodoo.browseL8(ctx, model_grp, grp_ids):
                if group.implied_ids:
                    uniq_field.append(group.name)
                    uniq_field += [x.name for x in group.implied_ids]
            for group in clodoo.browseL8(ctx, model_grp, grp_ids,
                                         context={'lang': 'en_US'}):
                ir_md = clodoo.browseL8(ctx, model_ir_md,
                                        clodoo.searchL8(ctx, model_ir_md,
                                                        [('model', '=', model_grp),
                                                         ('res_id', '=', group.id)]))
                if group.name in uniq_field:
                    tag = '*'
                else:
                    tag = ''
                print('%d) -- Value [%-16.16s] > [%-32.32s] as "%s.%s" {%s}' % (
                    group.id,
                    group.name,
                    group.full_name,
                    ir_md.module,
                    ir_md.name,
                    tag))


def all_addr_same_customer(ctx):
    print('Set delivery address to the same of customer on sale order')
    if ctx['param_1'] == 'help':
        print(
            'delivery_addr_same_customer '
            '[FROM_DATE|+DAYS|IDS] [Inv|Delivery|Both] [partner_id]'
        )
        return
    resource_so = 'sale.order'
    domain = param_date(ctx['param_1'], date_field='date_order')
    select = 'B'
    if ctx['param_2'] in ('I', 'D', 'B'):
        select = ctx['param_2']
    if ctx['param_3']:
        force_partner_id = eval(ctx['param_3'])
    else:
        force_partner_id = False
    ctr = 0
    for so in clodoo.browseL8(ctx, resource_so, domain):
        vals = {}
        if force_partner_id:
            if so.partner_id != force_partner_id:
                vals['partner_id'] = force_partner_id
        else:
            if select in ('B', 'D') and so.partner_shipping_id != so.partner_id:
                vals['partner_shipping_id'] = so.partner_id.id
            if select in ('B', 'I') and so.partner_invoice_id != so.partner_id:
                vals['partner_invoice_id'] = so.partner_id.id
        if vals:
            clodoo.writeL8(ctx, resource_so, so.id, vals)
            print('so.number=%s' % so.name)
            ctr += 1
    print('%d sale orders updated' % ctr)


def hide_invoice_delivery_address(ctx):
    print('Hide invoice and/od delivery addresses on partners')
    if ctx['param_1'] == 'help':
        print(
            'def hide_invoice_delivery_address (auto|invoice|delivery|both)'
        )
        return
    resource_part = 'res.partner'
    ctr = 0
    for partner in clodoo.browseL8(
        ctx, resource_part, clodoo.searchL8(
            ctx, resource_part, [])):
        msg_burst('%s ...' % partner.name)
        childs = {}
        for partype in ("invoice", "delivery"):
            childs[partype] = []
        for child in partner.child_ids:
            if child.type not in childs:
                childs[child.type] = []
            childs[child.type].append(child)
        if ctx['param_1'] in ("invoice", "delivery"):
            if ctx['param_1'] in childs:
                for child in childs[ctx['param_1']]:
                    clodoo.writeL8(ctx, resource_part, child.id, {"active": False})
                    ctr += 1
        elif ctx['param_1'] == "both":
            for partype in ("invoice", "delivery"):
                for child in childs[partype]:
                    clodoo.writeL8(ctx, resource_part, child.id, {"active": False})
                    ctr += 1
        else:
            for partype in ("invoice", "delivery"):
                for child in childs[partype]:
                    if len(childs[partype]) != 1:
                        continue
                    if partner.name == child.name and partner.street == child.street:
                        clodoo.writeL8(
                            ctx, resource_part, child.id, {"active": False})
                        ctr += 1
    print('%d partner hided' % ctr)


def order_inv_group_by_partner(ctx):
    print('Set order invoicing group by customer setting')
    if ctx['param_1'] == 'help':
        print('order_inv_group_by_partner' '[FROM_DATE|+DAYS|IDS]')
        return
    resource_so = 'sale.order'
    domain = param_date(ctx['param_1'], date_field='date_order')
    ctr = 0
    for order in clodoo.browseL8(
        ctx, resource_so, clodoo.searchL8(
            ctx, resource_so, domain, order='name desc,id')):
        msg_burst('%s ...' % order.name)
        partner_group = order.partner_id.ddt_invoicing_group
        sale_group = order.ddt_invoicing_group
        if sale_group != partner_group:
            print('Changing group of %s' % order.name)
            clodoo.writeL8(
                ctx, resource_so, order.id, {'ddt_invoicing_group': partner_group})
            ctr += 1
    print('%d sale order updated' % ctr)


def recalc_delivery_price(ctx):
    print('Recalculate delivery price on DdT')

    resource_ddt = 'stock.picking.package.preparation'
    resource_line = 'stock.picking.package.preparation.line'
    resource_soline = 'sale.order.line'
    resource_carrier = 'delivery.carrier'
    if ctx['param_1'] == 'help':
        print('recalc_delivery_price [FROM_DATE|+DAYS|IDS]')
        return
    shipping_ids = []
    for delivery in clodoo.browseL8(ctx, resource_carrier,
                                    clodoo.searchL8(ctx, resource_carrier, [])):
        shipping_ids.append(delivery.product_id.id)
    domain = param_date(ctx['param_1'], date_field='date')
    domain.append(("carrier_id", "!=", False))
    ctr_read = ctr_upd = 0
    for ddt in clodoo.browseL8(
        ctx, resource_ddt, clodoo.searchL8(
            ctx, resource_ddt, domain)):
        msg_burst('%s ...' % ddt.id)
        clodoo.executeL8(ctx, resource_ddt, "delivery_set", ddt.id)
        ctr_read += 1
        ddt = clodoo.browseL8(ctx, resource_ddt, ddt.id)
        sale_id = False
        delivery_price = 0.0
        if ddt.delivery_price == 0.0:
            for line in clodoo.browseL8(
                ctx, resource_line, clodoo.searchL8(
                    ctx, resource_line, [("package_preparation_id", "=", ddt.id)])):
                if line.sale_id:
                    sale_id = line.sale_id.id
                    break
        if sale_id:
            for soline in clodoo.browseL8(
                ctx, resource_soline, clodoo.searchL8(
                    ctx, resource_soline, [("order_id", "=", sale_id),
                                           ("product_id", "in", shipping_ids)])):
                delivery_price += soline.price_subtotal
        if delivery_price:
            clodoo.writeL8(
                ctx, resource_ddt, ddt.id, {"delivery_price": delivery_price})
            ctr_upd += 1

    print('%d delivery notes read, %d written' % (ctr_read, ctr_upd))


def close_sale_orders(ctx):
    print('Close sale orders with linked invoice')

    resource_so = 'sale.order'
    resource_line = 'sale.order.line'
    resource_carrier = 'delivery.carrier'
    resource_company = 'res.company'

    if ctx['param_1'] == 'help':
        print('close_sale_orders [no|to invoice|invoiced] [FROM_DATE|+DAYS|IDS]')
        return
    if ctx['param_1'] in ('no', 'to invoice', 'both'):
        sel_state = ctx['param_1']
    else:
        sel_state = 'both'
    domain = param_date(ctx['param_2'], date_field='date_order')
    domain.append(('state', '=', 'sale'))

    shipping_ids = []
    for delivery in clodoo.browseL8(ctx, resource_carrier,
                                    clodoo.searchL8(ctx, resource_carrier, [])):
        shipping_ids.append(delivery.product_id.id)
    conai_product_ids = []
    for company in clodoo.browseL8(ctx, resource_company,
                                   clodoo.searchL8(ctx, resource_company, [])):
        if (
            hasattr(company, 'conai_product_id')
            and not callable(company.conai_product_id)
            and company.conai_product_id
        ):
            conai_product_ids.append(company.conai_product_id.id)

    ctr_read = ctr_upd = ctr_wrong = 0
    if sel_state != 'both':
        domain.append(('invoice_status', '=', sel_state))
    for so in clodoo.browseL8(ctx, resource_so,
                              clodoo.searchL8(ctx, resource_so, domain)):
        msg_burst('%s (%d/%d) ...' % (so.name, ctr_upd, ctr_read))
        ctr_read += 1
        if so.state not in ("sale", "done"):
            if so.invoice_status == "invoiced":
                clodoo.writeL8(ctx,
                               resource_so,
                               so.id,
                               {
                                   'invoiced': 'no'
                               })
                print('Order %s -> %s' % (so.name, 'no'))
                ctr_upd += 1
            continue

        invoice_status = 'invoiced'
        if not so.force_invoiced:
            for ln in so.order_line:
                msg_burst('%s (%d/%d) ...' % (so.name, ctr_upd, ctr_read))
                if (
                    ln.product_id and (
                        ln.product_id.id in shipping_ids
                        or ln.product_id.id in conai_product_ids)
                ):
                    if (
                            ln.product_id.id not in conai_product_ids
                            and (not so.carrier_id
                                 or so.carrier_id.product_id != ln.product_id)
                    ):
                        print("*** Order %s - '%s' - Inv. %s - multiple amount %s ***"
                              % (so.name,
                                 ln.name[:40],
                                 (ln.invoice_lines
                                  and ln.invoice_lines[0].invoice_id.number),
                                 ln.price_subtotal))
                        ctr_wrong += 1
                    if ln.qty_invoiced != ln.product_qty:
                        clodoo.writeL8(ctx,
                                       resource_line,
                                       ln.id,
                                       {
                                           'qty_invoiced': ln.product_qty,
                                           'qty_to_invoice': 0.0,
                                       })
                        ctr_upd += 1
                    continue

                if ln.invoice_lines:
                    continue
                invoice_status = 'to invoice'
                if so.invoice_status != invoice_status:
                    print("\nSO=%s - %s\n" % (so.name, ln.name[:40]))
                break

        if so.invoice_status != invoice_status:
            clodoo.writeL8(ctx,
                           resource_so,
                           so.id,
                           {
                               'invoice_status': invoice_status,
                           })
            print('Order %s -> %s' % (so.name, invoice_status))
            ctr_upd += 1

    print('%d sale order updated of %d read!' % (ctr_upd, ctr_read))


def close_ddts(ctx):
    print('Close Delivery Document Type with linked invoice')
    if ctx['param_1'] == 'help':
        print('close_ddts [FROM_DATE|+DAYS|IDS]')
        return
    domain = param_date(ctx['param_1'], date_field='date')

    resource_ddt = 'stock.picking.package.preparation'
    resource_product = 'product.product'

    ctr_read = ctr_upd = 0
    transportation_reason = False
    for ddt in clodoo.browseL8(ctx, resource_ddt,
                               clodoo.searchL8(ctx, resource_ddt, domain)):
        msg_burst('%s (%d/%d) ...' % ((ddt.ddt_number or ddt.name), ctr_upd, ctr_read))
        ctr_read += 1
        if ddt.transportation_reason_id != transportation_reason:
            transportation_reason = ddt.transportation_reason_id
        if ddt.state != "done" or not transportation_reason.to_be_invoiced:
            if ddt.to_be_invoiced != transportation_reason.to_be_invoiced:
                clodoo.writeL8(ctx,
                               resource_ddt,
                               ddt.id,
                               {
                                   'to_be_invoiced':
                                       transportation_reason.to_be_invoiced
                               })
                ctr_upd += 1
            continue

        invoice_id = to_be_invoiced = False
        for ln in ddt.line_ids:
            msg_burst('%s (%d/%d) ...' % (
                (ddt.ddt_number or ddt.name), ctr_upd, ctr_read))
            if ln.invoice_line_id:
                if not invoice_id:
                    invoice_id = ln.invoice_line_id.invoice_id.id
                continue
            if (
                ln.sale_line_id
                and ln.sale_line_id.order_id
                and ln.sale_line_id.order_id.invoice_status == 'invoiced'
            ):
                continue
            if ln.product_id:
                product = clodoo.browseL8(ctx, resource_product, ln.product_id.id)
                if product.type == 'service':
                    continue
            to_be_invoiced = True
            break
        if ddt.to_be_invoiced != to_be_invoiced:
            clodoo.writeL8(ctx,
                           resource_ddt,
                           ddt.id,
                           {
                               'to_be_invoiced': to_be_invoiced,
                               'invoice_id': invoice_id,
                           })
            ctr_upd += 1

    print('%d DdT updated of %d read!' % (ctr_upd, ctr_read))


def close_purchase_orders(ctx):
    print('Close purchase orders lines that are delivered')
    if ctx['param_1'] == 'help':
        print('close_purchase_orders ' '[byLine|Header] [from_date|+days|ids]')
        return
    if ctx['param_1'] not in ('L', 'H'):
        print('Invalid param #1: use L!H ')
        return
    mode = ctx['param_1']
    model = 'purchase.order'
    model_line = 'purchase.order.line'
    date_ids = param_date(ctx['param_2'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, model, [('date_order', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if ids:
        if isinstance(ids, (int, long)):
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
            ctx, model_line, clodoo.searchL8(ctx, model_line, domain)
        ):
            if po.qty_invoiced == 0.0:
                qty_received = po.product_qty
            elif po.qty_received == 0.0:
                qty_received = po.product_qty
            else:
                qty_received = 0.0
            print(po.product_qty, po.qty_received, qty_received, po.qty_invoiced)
            if qty_received > 0.0:
                clodoo.writeL8(ctx, model_line, po.id, {'qty_received': qty_received})
                ctr += 1
    elif mode == 'H':
        for po in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, domain1)):
            clodoo.writeL8(ctx, model, po.id, {'invoice_status': 'invoiced'})
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
        ctx, model_vat, [('description', '=', taxv), ('company_id', '=', company_id)]
    )
    if not taxv:
        print('Code tax %s not found!' % taxv)
        return
    taxa_ids = clodoo.searchL8(
        ctx, model_vat, [('description', '=', taxa), ('company_id', '=', company_id)]
    )
    if not taxa:
        print('Code tax %s not found!' % taxa)
        return
    accv_ids = clodoo.searchL8(
        ctx, model_acc, [('code', '=', accv), ('company_id', '=', company_id)]
    )
    if not accv:
        print('Account code %s not found!' % accv)
        return
    acca_ids = clodoo.searchL8(
        ctx, model_acc, [('code', '=', acca), ('company_id', '=', company_id)]
    )
    if not accv:
        print('Account code %s not found!' % acca)
        return
    ctr = 0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if taxv_ids[0] not in pp.taxes_id.ids:
            clodoo.writeL8(ctx, model, pp.id, {'taxes_id': [(6, 0, taxv_ids)]})
            ctr += 1
        if taxa_ids[0] not in pp.supplier_taxes_id.ids:
            clodoo.writeL8(ctx, model, pp.id, {'supplier_taxes_id': [(6, 0, taxa_ids)]})
            ctr += 1
        if accv_ids[0] != pp.property_account_income_id.id:
            clodoo.writeL8(
                ctx, model, pp.id, {'property_account_income_id': accv_ids[0]}
            )
            ctr += 1
        if acca_ids[0] != pp.property_account_expense_id.id:
            clodoo.writeL8(
                ctx, model, pp.id, {'property_account_expense_id': acca_ids[0]}
            )
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
    ctr = 0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if pp.purchase_method != purchase_method:
            clodoo.writeL8(ctx, model, pp.id, {'purchase_method': purchase_method})
            ctr += 1
        if pp.invoice_policy != invoice_policy:
            clodoo.writeL8(ctx, model, pp.id, {'invoice_policy': invoice_policy})
            ctr += 1
    print('%d product templates updated' % ctr)

    model = 'product.product'
    ctr = 0
    for pp in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % pp.name)
        if pp.purchase_method != purchase_method:
            clodoo.writeL8(ctx, model, pp.id, {'purchase_method': purchase_method})
            ctr += 1
        if pp.invoice_policy != invoice_policy:
            clodoo.writeL8(ctx, model, pp.id, {'invoice_policy': invoice_policy})
            ctr += 1
    print('%d products updated' % ctr)


def set_products_2_consumable(ctx):
    print('Set consumable of the stockable products')
    model = 'product.template'
    ctr = 0
    for pp in clodoo.browseL8(
        ctx, model, clodoo.searchL8(ctx, model, [('type', '=', 'product')])
    ):
        clodoo.writeL8(ctx, model, pp.id, {'type': 'consu'})
        ctr += 1
    print('%d product templates updated' % ctr)

    model = 'product.product'
    ctr = 0
    for pp in clodoo.browseL8(
        ctx, model, clodoo.searchL8(ctx, model, [('type', '=', 'product')])
    ):
        clodoo.writeL8(ctx, model, pp.id, {'type': 'consu'})
        ctr += 1
    print('%d products updated' % ctr)


def set_report_config(ctx):
    print('Set report and multireport configuration')
    print('Require module "base_multireport"')
    if ctx['param_1'] == 'help':
        print(
            'reset_report_config header_mode footer_mode payment_term '
            'ord_ref|False|Default ddt_ref|False|Default print|Default'
        )
        return
    company_id = env_ref(ctx, 'z0bug.mycompany')
    if company_id:
        company_partner_id = env_ref(ctx, 'z0bug.partner_mycompany')
        clodoo.writeL8(
            ctx, 'res.partner', company_partner_id, {'codice_destinatario': 'URCROKA'}
        )

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
        ctx, model, clodoo.searchL8(ctx, model, [('origin', '!=', 'odoo')])
    ):
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
    domain = [
        (
            'model',
            'in',
            (
                'sale.order',
                'stock.picking.package.preparation',
                'account.invoice',
                'purchase.order',
            ),
        )
    ]
    for rpt in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        print('Processing report %s' % rpt.name)
        clodoo.writeL8(ctx, model, rpt.id, vals)
        ctr += 1
    domain = [
        (
            'model',
            'not in',
            (
                'sale.order',
                'stock.picking.package.preparation',
                'account.invoice',
                'purchase.order',
            ),
        )
    ]
    del vals['template']
    for rpt in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        print('Processing report %s' % rpt.name)
        clodoo.writeL8(ctx, model, rpt.id, vals)
        ctr += 1

    vals = {'address_mode': ''}
    if order_ref_text:
        if order_ref_text == 'False':
            vals['order_ref_text'] = ''
        elif order_ref_text == 'Default':
            vals['order_ref_text'] = (
                'Vs. Ordine: %(client_order_ref)s / '
                'Ns. Ordine: %(order_name)s del %(date_order)s'
            )
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
        for rpt in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
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
    for acc in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, domain)):
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

    model = 'account.journal'
    journal_id = clodoo.searchL8(
        ctx,
        model,
        [
            '|',
            ('code', '=', 'MISC'),
            ('code', '=', 'VARIE'),
            ('company_id', '=', company_id),
        ],
    )
    journal_id = journal_id[0] if journal_id else False

    ctr_rec = 0
    model = 'withholding.tax'
    wt_1040 = clodoo.searchL8(ctx, model, [('name', '=', '1040')])
    wt_1040 = wt_1040[0] if wt_1040 else False
    paycode = clodoo.searchL8(ctx, model_paycode, [('code', '=', 'A')])
    paycode = paycode[0] if paycode else False
    vals = {
        'name': '1040 - 20% su 100% (A)',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 20, 'base': 1})],
        'journal_id': journal_id,
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
    _synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {
        'name': '1040 - 23% su 100% (A)',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 1})],
        'journal_id': journal_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/100-A'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    _synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {
        'name': '1040 - 23% su 50% (A)',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 0.5})],
        'journal_id': journal_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/50-A'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    _synchro(ctx, model, vals)
    ctr_rec += 1

    paycode = clodoo.searchL8(ctx, model_paycode, [('code', '=', 'R')])
    paycode = paycode[0] if paycode else False
    vals = {
        'name': '1040 - 23% su 100% ®',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 1})],
        'journal_id': journal_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/100-R'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    _synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {
        'name': '1040 - 23% su 50% ® (ex 1038)',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 23, 'base': 0.5})],
        'journal_id': journal_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = '1040-23%/50-R'
        vals['company_id'] = company_id
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    _synchro(ctx, model, vals)
    ctr_rec += 1

    vals = {
        'name': 'Enasarco 16,50% su 50%',
        'account_receivable_id': credit_acc_id,
        'account_payable_id': debit_acc_id,
        'rate_ids': [(5, 0), (0, 0, {'tax': 16.5, 'base': 0.5})],
        'journal_id': journal_id,
    }
    if ctx['majver'] >= 10:
        vals['code'] = 'Enasarco'
        vals['company_id'] = company_id
        vals['wt_types'] = 'enasarco'
    if payment_ids:
        vals['payment_term'] = payment_ids[0]
    if paycode:
        vals['causale_pagamento_id'] = paycode
    _synchro(ctx, model, vals)
    ctr_rec += 1
    print('%d records inserted/updated' % ctr_rec)


def configure_email_template(ctx):
    print('Configure e-mail template')
    model_ids = clodoo.searchL8(
        ctx, 'ir.model', [('model', 'in', ('account.invoice', 'sale.order'))]
    )
    model = 'mail.template'
    email_from = (
        '${(object.company_id.email and \'%s <%s>\' % '
        '(object.company_id.name, object.company_id.email) or '
        '\'\')|safe}'
    )
    reply_to = '${object.company_id.email}'
    RPT_NAME = {}
    RPT_NAME[
        'account.invoice'
    ] = """
    ${{'out_invoice':'Fattura','out_refund': 'NotaCredito',
     'in_invoice':'Fattura','in_refund':'NC',
     }[object.type]}_${(object.number or 'bozza').replace('/','-')}
    """
    RPT_NAME[
        'sale.order'
    ] = """
    ${{'draft':'Offerta','sent':'Ordine','sale':'Ordine',
     'done':'Conferma','cancel':'Bozza',
     }[object.state]}_${(object.name or 'bozza').replace('/','-')}
    """
    for template in clodoo.browseL8(
        ctx, model, clodoo.searchL8(ctx, model, [('model_id', 'in', model_ids)])
    ):
        print(template.name)
        vals = {
            'reply_to': reply_to,
            'email_from': email_from,
            'report_name': RPT_NAME[template.model_id.model],
        }
        clodoo.writeL8(ctx, model, template.id, vals)


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

    user = input('Username to simulate: ')
    pwd = getpass.getpass()
    pwd = pwd if pwd else 'prova2019'
    uid, ctx = clodoo.oerp_set_env(
        confn=ctx['conf_fn'], db=ctx['db_name'], user=user, pwd=pwd, ctx=ctx
    )
    user = clodoo.browseL8(ctx, 'res.users', uid)
    print('***** %s *****' % user.name)
    for model in 'sale.order', 'account.invoice', 'res.partner':
        print('\n[%s]' % model)
        if model == 'res.partner':
            print(
                '%-11.11s %4s %-32.32s %s %s'
                % ('model', 'id', 'name', 'type', 'agents')
            )
            model2 = model
            domain = [('customer', '=', True), ('parent_id', '=', False)]
        elif model == 'account.invoice':
            print('%-15.15s %4s %-20.20s %s' % ('model', 'id', 'number', 'agents'))
            model2 = 'account.invoice.line'
            domain = []
        else:
            print(
                '%-10.10s %4s %-16.16s %-32.32s %s'
                % ('model', 'id', 'name', 'customer', 'agents')
            )
            model2 = 'sale.order.line'
            domain = []
        for rec in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, domain)):
            if model == 'res.partner':
                print(
                    '%s %4d %-32.32s %s %s'
                    % (model, rec.id, rec.name, rec.type, get_agent_names(rec.agents))
                )
            elif model == 'account.invoice':
                print(
                    '%s %4d %-20.20s %s'
                    % (model, rec.id, rec.number, get_agent_names(rec.agents))
                )
            else:
                print(
                    '%s %4d %-16.16s %-32.32s %s'
                    % (
                        model,
                        rec.id,
                        rec.name,
                        rec.partner_id.name,
                        get_agent_names(rec.agents),
                    )
                )
            if model2:
                if model == 'res.partner':
                    domain = [('parent_id', '=', rec.id)]
                elif model2 == 'account.invoice.line':
                    domain = [('invoice_id', '=', rec.id)]
                else:
                    domain = [('order_id', '=', rec.id)]
                for rec2 in clodoo.browseL8(
                    ctx, model2, clodoo.searchL8(ctx, model2, domain)
                ):
                    if model == 'res.partner':
                        print(
                            '    %s %4d %-32.32s %s %s'
                            % (
                                model2,
                                rec2.id,
                                rec2.name,
                                rec2.type,
                                get_agent_names(rec2.agents),
                            )
                        )
                    elif model == 'account.invoice':
                        print(
                            '    %s %4d %-32.32s %s'
                            % (
                                model2,
                                rec2.id,
                                rec2.name,
                                get_agent_names_line(rec2.agents),
                            )
                        )
                    else:
                        print(
                            '    %s %4d %-32.32s %s'
                            % (
                                model2,
                                rec2.id,
                                rec2.name,
                                get_agent_names_line(rec2.agents),
                            )
                        )


def reset_email_admins(ctx):
    def reset_email_user(ctx, username):
        model = 'res.users'
        model2 = 'res.partner'
        email = {
            'vg7bot': 'vg7bot@vg7.it',
            'vg7admin': 'noreply@vg7.it',
            'zeroadm': 'noreply@zeroincombenze.it',
        }[username]
        ctr = 0
        ids = clodoo.searchL8(ctx, model, [('login', '=', username)])
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
    for commission in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        if commission.name in COMMISSIONS:
            COMMISSIONS[commission.name]['id'] = commission.id
    for commission in COMMISSIONS:
        vals = {'name': commission, 'fix_qty': COMMISSIONS[commission]['fix_qty']}
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
    for agent in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
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
        env_ref(ctx, 'z0bug.res_partner_2'): {'agents': AGENTS['Agente A']['id']},
        env_ref(ctx, 'z0bug.res_partner_4'): {'agents': AGENTS['Agente B']['id']},
        env_ref(ctx, 'z0bug.res_partner_1'): {'agents': AGENTS['Agente A']['id']},
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
        ctx, model, clodoo.searchL8(ctx, model, [], order='id')
    ):
        vals = {
            'name': 'Consegna gratuita',
            'ddt_carrier_id': False,
            'transportation_method_id': env_ref(
                ctx, 'l10n_it_ddt.transportation_method_DES'
            ),
            'carriage_condition_id': env_ref(ctx, 'l10n_it_ddt.carriage_condition_PF'),
            'note': 'Trasporto con mezzi propri',
        }
        clodoo.writeL8(ctx, model, carrier.id, vals)
        ctr += 1
        break
    model = 'stock.ddt.type'
    for ddt_type in clodoo.browseL8(
        ctx, model, clodoo.searchL8(ctx, model, [], order='id')
    ):
        vals = {
            'default_transportation_reason_id': env_ref(
                ctx, 'l10n_it_ddt.transportation_reason_VEN'
            ),
            'default_goods_description_id': env_ref(
                ctx, 'l10n_it_ddt.goods_description_CAR'
            ),
            'company_id': company_id,
        }
        clodoo.writeL8(ctx, model, ddt_type.id, vals)
        ctr += 1
        break
    model = 'res.partner'
    # partner=clodoo.browseL8(ctx, model, env_ref(ctx, 'z0bug.res_partner_2'))
    vals = {
        'ddt_show_price': True,
        'goods_description_id': env_ref(ctx, 'l10n_it_ddt.goods_description_SFU'),
        'carriage_condition_id': env_ref(ctx, 'l10n_it_ddt.carriage_condition_PAF'),
        'transportation_method_id': env_ref(
            ctx, 'l10n_it_ddt.transportation_method_COR'
        ),
    }
    clodoo.writeL8(ctx, model, env_ref(ctx, 'z0bug.res_partner_2'), vals)
    ctr += 1
    print('%d record updated' % ctr)


def show_empty_ddt(ctx):
    print('Show DdT without lines')
    model = 'stock.picking.package.preparation'
    for ddt in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % ddt.ddt_number)
        if not ddt.line_ids:
            print(
                'DdT n.%s del %s (Id=%d) without lines'
                % (ddt.ddt_number, ddt.date, ddt.id)
            )


def change_ddt_number(ctx):
    print('Change DdT number of validated record')
    model = 'stock.picking.package.preparation'
    ddt_id = input('DdT id: ')
    if ddt_id:
        ddt_id = eval(ddt_id)
        ddt = clodoo.browseL8(ctx, model, ddt_id)
        print('Current DdT number is: %s' % ddt.ddt_number)
        ddt_number = input('New number: ')
        if ddt_number:
            clodoo.writeL8(ctx, model, ddt_id, {'ddt_number': ddt_number})
            ddt = clodoo.browseL8(ctx, model, ddt_id)
            print('DdT number of id %d changed with %s' % (ddt_id, ddt.ddt_number))


def deduplicate_partner(ctx):
    print('Deduplicate partners')
    model = 'res.partner'
    prior_name = ''
    prior_partner = False
    for partner in clodoo.browseL8(
        ctx,
        model,
        clodoo.searchL8(ctx, model, [('parent_id', '=', False)], order='name'),
    ):
        msg_burst('%s ...' % partner.name)
        if partner.vat:
            ids = clodoo.searchL8(ctx, model, [('vat', '=', partner.vat)])
            if len(ids) > 1:
                print('Found duplicate vat %s in %s records' % (partner.vat, ids))
                for partner_id in ids:
                    dup = clodoo.browseL8(ctx, model, partner_id)
                    if dup.parent_id or dup.type in ('invoice', 'delivery'):
                        clodoo.writeL8(ctx, model, partner_id, {'vat': False})
                        print('Dropped vat from %s (%d)' % (dup.name, partner_id))
        if partner.name and partner.name == prior_name:
            print(
                'Found duplicate name %s as %d and %d'
                % (partner.name, partner.id, prior_partner.id)
            )
            candidate = False
            if prior_partner.id > partner.id:
                if (
                    prior_partner.activities_count == 0
                    and len(prior_partner.invoice_ids) == 0
                ):
                    candidate = prior_partner
            if not candidate and prior_partner.id < partner.id:
                if partner.activities_count == 0 and len(partner.invoice_ids) == 0:
                    candidate = partner
            if not candidate:
                if partner.activities_count == 0 and len(partner.invoice_ids) == 0:
                    candidate = partner
                elif (
                    prior_partner.activities_count == 0
                    and len(prior_partner.invoice_ids) == 0
                ):
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
                        print(
                            'Assigned vg7_id %d to record %d'
                            % (vg7_id, prior_partner.id)
                        )
                    elif candidate == prior_partner:
                        clodoo.writeL8(ctx, model, partner.id, vals)
                        print('Assigned vg7_id %d to record %d' % (vg7_id, partner.id))
        prior_name = partner.name
        prior_partner = partner


def print_model_synchro_data(ctx):
    print('Show XML data to build model for synchro module')
    model = ''
    while not model:
        model = input('Model to build: ')
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
            ctx,
            'ir.model.fields',
            clodoo.searchL8(ctx, 'ir.model.fields', [('model_id', '=', model_id)]),
        ):
            if field.name == 'code':
                key_name = field.name
            elif field.name in TECH_FIELDS:
                continue
            doc += template % (
                model_name,
                field.name,
                field.name,
                field.name,
                model_name,
            )
        doc = (
            '''
    <record forcecreate="1" id="%s" model="synchro.channel.model">
        <field name="name">%s</field>
        <field name="field_uname">%s</field>
        <field name="search_keys">([%s],)</field>
        <field name="synchro_channel_id" ref="channel_vg7"/>
    </record>
        '''
            % (model_name, model, key_name, key_name)
            + doc
        )
        print(doc)

    def write_product(ctx, company_id):
        model = 'product.product'
        print('Write %s ...' % model)
        vg7_id = 1
        code = 'AAA'
        name = 'Product Alpha'
        vals = {
            'company_id': company_id,
            'vg7:id': vg7_id,
            'vg7:code': code,
            'vg7:description': name,
        }
        product_id = clodoo.executeL8(ctx, model, 'synchro', vals)
        return product_id

    def write_sale_order(
        ctx, company_id, order_num, vg7_partner_id, vg7_shipping_addr_id, product_a_id
    ):
        model = 'sale.order'
        print('Write %s ...' % model)
        order_name = '%06d' % eval(order_num)
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
        order_id = clodoo.executeL8(ctx, model, 'synchro', vals)

        model = 'sale.order.line'
        print('Write %s ...' % model)
        vg7_id = eval(order_num) * 10
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
        clodoo.executeL8(ctx, model, 'synchro', vals)
        id = clodoo.executeL8(ctx, 'sale.order', 'commit', order_id)
        if id < 0:
            raise IOError('!!Commit Failed (%d)!' % id)

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')
    clodoo.executeL8(ctx, 'ir.model.synchro.cache', 'set_loglevel', 0, 'debug')
    clodoo.executeL8(ctx, 'ir.model.synchro.cache', 'clean_cache', 0, None, None, 5)
    # ord_model = 'sale.order'
    partner_model = 'res.partner'
    order_num = ctx['param_1'] or '1234'
    partner_id = env_ref(ctx, 'z0bug.res_partner_2')
    vg7_partner_id = 2
    vals = {'vg7_id': vg7_partner_id}
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
        'fiscalcode': '',
    }
    sync_partner_id = clodoo.executeL8(ctx, partner_model, 'synchro', vals)
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
        'vg7:id': 2,
    }
    vg7_shipping_addr_id = sync_partner_id = clodoo.executeL8(
        ctx, partner_model, 'synchro', vals
    )
    product_a_id = write_product(ctx, company_id)
    write_sale_order(
        ctx, company_id, order_num, vg7_partner_id, vg7_shipping_addr_id, product_a_id
    )


def unlink_ddt_from_invoice(ctx):
    if ctx['param_1'] == 'help':
        print('Unlink DDT form invoice [from_date|+days|ids]')
        return
    print('Unlink DdT from invoice')
    invoice_model = 'account.invoice'
    invoice_line_model = 'account.invoice.line'
    ddt_model = 'stock.picking.package.preparation'
    ddt_line_model = 'stock.picking.package.preparation.line'
    date_ids = param_date(ctx['param_1'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', date_ids):
        ids = clodoo.searchL8(ctx, invoice_model, [('date_invoice', '>=', date_ids)])
    else:
        ids = eval(date_ids)
    if not ids:
        print('Too many records!')
        return
    ctr = 0
    inv_line_ids = []
    ddt_line_ids = []
    for invoice in clodoo.browseL8(ctx, invoice_model, ids):
        for ln in invoice.invoice_line_ids:
            ddt_line_ids.append(ln.ddt_line_id.id)
            clodoo.writeL8(ctx, invoice_line_model, ln.id, {'ddt_line_id': False})
            ctr += 1
            inv_line_ids.append(ln.id)
    ddt_ids = []
    for ln in clodoo.browseL8(
        ctx,
        ddt_line_model,
        clodoo.searchL8(
            ctx,
            ddt_line_model,
            ['|', ('id', 'in', ddt_line_ids), ('invoice_line_id', 'in', inv_line_ids)],
        ),
    ):
        clodoo.writeL8(ctx, ddt_line_model, ln.id, {'invoice_line_id': False})
        ctr += 1
        if ln.package_preparation_id.id not in ddt_ids:
            clodoo.writeL8(
                ctx,
                ddt_model,
                ln.package_preparation_id.id,
                {'to_be_invoiced': True, 'invoice_id': False},
            )
            ddt_ids.append(ln.package_preparation_id.id)
            ctr += 1
    print('%d record unlinked!' % ctr)


def check_rec_links(ctx):
    print('Check link for invoice records to DdTs and orders')
    if ctx['param_1'] == 'help':
        print('check_rec_links(inv__date|ids ddt_date!ids)')
        return

    def parse_sale_from_invline(invoice_line, ctr, err_ctr, orders):
        for sale_line in invoice_line.sale_line_ids:
            ctr += 1
            if sale_line.order_id.id not in orders:
                orders.append(sale_line.order_id.id)
            if invoice.partner_id.id not in (
                sale_line.order_id.partner_id.id,
                sale_line.order_id.partner_invoice_id.id,
                sale_line.order_id.partner_shipping_id.id,
            ):
                os0.wlog(
                    '!!! Invoice %s (%d) partner differs from '
                    'sale order %s (%d) partner!!!'
                    % (
                        invoice.number,
                        invoice.id,
                        sale_line.order_id.name,
                        sale_line.order_id.id,
                    )
                )
                err_ctr += 1
                clodoo.writeL8(
                    ctx,
                    invline_model,
                    invoice_line.id,
                    {'sale_line_ids': [(3, sale_line.id)]},
                )
        order_line_ids = clodoo.searchL8(
            ctx, soline_model, [('invoice_lines', '=', invoice_line.id)]
        )
        if not order_line_ids and invoice_line.product_id:
            order_line_ids = clodoo.searchL8(
                ctx,
                soline_model,
                [
                    ('company_id', '=', invoice_line.company_id.id),
                    ('order_partner_id', '=', invoice_line.partner_id.id),
                    ('product_id', '=', invoice_line.product_id.id),
                ],
            )
            for soline in clodoo.browseL8(ctx, soline_model, order_line_ids):
                if invoice_line.id in soline.invoice_lines:
                    continue
                if soline.product_qty == soline.qty_invoiced:
                    continue
                if soline.invoice_lines:
                    print('Found SO %s' % (soline.order_id.name))
                    dummy = input('Link this order (y/N)? ')
                    if dummy != 'y':
                        continue
                if soline.product_uom and soline.product_uom != invoice_line.uom_id:
                    print(
                        'Invalid uom so=%s inv=%s'
                        % (
                            soline.product_uom and soline.product_uom.id,
                            invoice_line.uom_id and invoice_line.uom_id.id,
                        )
                    )
                    clodoo.writeL8(
                        ctx,
                        invline_model,
                        invoice_line.id,
                        {'uom_id': soline.product_uom.id},
                    )
                clodoo.writeL8(
                    ctx,
                    soline_model,
                    soline.id,
                    {'invoice_lines': [(4, invoice_line.id)]},
                )
                err_ctr += 1
                print(
                    'Linked invoice line %d to sale.order.line id %d'
                    % (invoice_line.id, soline.id)
                )
        return ctr, err_ctr, orders

    def parse_ddt_from_invline(invoice_line, ctr, err_ctr, ddts):
        if invoice_line.product_id.type == 'service':
            return ctr, err_ctr, ddts
        if invoice_line.ddt_line_id:
            ddts.append(invoice_line.ddt_line_id.package_preparation_id.id)
            if (
                invoice_line.ddt_line_id.sale_line_id
                and invoice_line.ddt_line_id.sale_line_id.order_id.id not in orders
            ):
                os0.wlog(
                    '!!! Invoice sale orders differs from '
                    'DdT sale order %s (%d)!!!'
                    % (
                        invoice_line.ddt_line_id.sale_line_id.order_id.name,
                        invoice_line.ddt_line_id.sale_line_id.order_id.id,
                    )
                )
                err_ctr += 1
                clodoo.writeL8(
                    ctx, invline_model, invoice_line.id, {'ddt_line_id': False}
                )
            elif (
                invoice_line.ddt_line_id
                and invoice_line.ddt_line_id.sale_line_id
                and (
                    invoice.partner_id.id
                    not in (
                        invoice_line.ddt_line_id.sale_line_id.order_id.partner_id.id,
                        (
                            invoice_line.ddt_line_id.sale_line_id.order_id.
                            partner_invoice_id.id
                        ),
                        (
                            invoice_line.ddt_line_id.sale_line_id.order_id.
                            partner_shipping_id.id
                        ),
                    )
                )
            ):
                os0.wlog(
                    '!!! Invoice %s (%d) partner differs from '
                    'ddt sale order %s (%d) partner!!!'
                    % (
                        invoice.number,
                        invoice.id,
                        invoice_line.ddt_line_id.sale_line_id.order_id.name,
                        invoice_line.ddt_line_id.sale_line_id.order_id.id,
                    )
                )
                err_ctr += 1
                clodoo.writeL8(
                    ctx, invline_model, invoice_line.id, {'ddt_line_id': False}
                )
        elif invoice_line.sale_line_ids:
            for sale_line in invoice_line.sale_line_ids:
                for inv_line in sale_line.invoice_lines:
                    if inv_line.id == invoice_line.id:
                        os0.wlog(
                            '!!! Missed DdT line for invoice %s (%d) '
                            'order %s!!!'
                            % (invoice.number, invoice.id, sale_line.order_id.id)
                        )
                        err_ctr += 1
                        ids = clodoo.searchL8(
                            ctx,
                            'stock.picking.package.preparation.line',
                            [('sale_line_id', '=', sale_line.id)],
                        )
                        if ids:
                            clodoo.writeL8(
                                ctx,
                                invline_model,
                                invoice_line.id,
                                {'ddt_line_id': ids[0]},
                            )
                        break
        return ctr, err_ctr, ddts

    invoice_model = 'account.invoice'
    invline_model = 'account.invoice.line'
    ddt_model = 'stock.picking.package.preparation'
    ddtline_model = 'stock.picking.package.preparation.line'
    # so_model = 'sale.order'
    soline_model = 'sale.order.line'
    inv_date_ids = param_date(ctx['param_1'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', inv_date_ids):
        ids = clodoo.searchL8(
            ctx, invoice_model, [('date_invoice', '>=', inv_date_ids)]
        )
    else:
        ids = eval(inv_date_ids)
    if ids:
        if isinstance(ids, (int, long)):
            # inv_domain = [('invoice_id', '=', ids)]
            inv_domain1 = [('id', '=', ids)]
        else:
            # inv_domain = [('invoice_id', 'in', ids)]
            inv_domain1 = [('id', 'in', ids)]
    else:
        # inv_domain = []
        inv_domain1 = []
    inv_domain1.append(('type', 'in', ('out_invoice', 'out_refund')))
    ddt_date_ids = param_date(ctx['param_2'])
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', ddt_date_ids):
        ids = clodoo.searchL8(ctx, ddt_model, [('date', '>=', ddt_date_ids)])
    else:
        ids = eval(ddt_date_ids)
    if ids:
        if isinstance(ids, (int, long)):
            # ddt_domain = [('package_preparation_id', '=', ids)]
            ddt_domain1 = [('id', '=', ids)]
        else:
            # ddt_domain = [('package_preparation_id', 'in', ids)]
            ddt_domain1 = [('id', 'in', ids)]
    else:
        # ddt_domain = []
        ddt_domain1 = []

    err_ctr = 0
    ctr = 0
    for invoice in clodoo.browseL8(
        ctx,
        invoice_model,
        clodoo.searchL8(ctx, invoice_model, inv_domain1, order='number desc'),
    ):
        msg_burst('%s ...' % invoice.number)
        orders = []
        ddts = []
        for invoice_line in invoice.invoice_line_ids:
            msg_burst('  - %s ...' % invoice_line.name[0:80])
            (ctr, err_ctr, orders) = parse_sale_from_invline(
                invoice_line, ctr, err_ctr, orders
            )
            (ctr, err_ctr, ddts) = parse_ddt_from_invline(
                invoice_line, ctr, err_ctr, ddts
            )
        diff = list({x.id for x in invoice.ddt_ids} - set(ddts))
        do_write = False
        if diff:
            os0.wlog(
                '!!! Found some DdT %s in invoice %s (%d) header '
                'not detected in invoice lines!!!' % (diff, invoice.number, invoice.id)
            )
            err_ctr += 1
            do_write = True
        diff = list(set(ddts) - {x.id for x in invoice.ddt_ids})
        if diff:
            os0.wlog(
                '!!! Some DdT (%s) in invoice lines are not detected '
                'in invoice %s (%d)!!!' % (diff, invoice.number, invoice.id)
            )
            err_ctr += 1
            do_write = True
        if do_write:
            clodoo.writeL8(ctx, invoice_model, invoice.id, {'ddt_ids': [(6, 0, ddts)]})

    for ddt in clodoo.browseL8(
        ctx,
        ddt_model,
        clodoo.searchL8(ctx, ddt_model, ddt_domain1, order='ddt_number desc'),
    ):
        msg_burst('%s ...' % ddt.ddt_number)
        ctr += 1
        invoices = [ddt.invoice_id.id] if ddt.invoice_id else []
        found_link = False
        for ddt_line in ddt.line_ids:
            if ddt_line.invoice_line_id:
                found_link = True
                break
        for ddt_line in ddt.line_ids:
            ctr += 1
            if (
                ddt_line.invoice_line_id
                and ddt_line.invoice_line_id.invoice_id.id not in invoices
            ):
                invoices.append(ddt_line.invoice_line_id.invoice_id.id)
            elif not found_link and ddt.invoice_id:
                ids = clodoo.searchL8(
                    ctx,
                    invline_model,
                    [
                        ('invoice_id', '=', ddt_line.invoice_line_id.invoice_id.id),
                        ('product_id', '=', ddt_line.product_id.id),
                        ('quantity', '=', ddt_line.product_uom_qty),
                        '|',
                        ('ddt_line_id', '=', ddt_line.id),
                        ('ddt_line_id', '=', False),
                    ],
                )
                if len(ids) == 1:
                    clodoo.writeL8(
                        ctx, ddtline_model, ddt_line.id, {'invoice_line_id': ids[0]}
                    )
                err_ctr += 1
                os0.wlog('!!! Found line of DdT %s w/o invoice line ref!!!' % (ddt.id))
        diff = list(set(invoices) - {x.id for x in ddt.invoice_ids})
        if diff:
            ddt_state = ddt.state
            err_ctr += 1
            os0.wlog('!!! Invoice refs updated in DdT %s!!!' % (ddt.id))
            if ctx['_cr']:
                query = "update %s set %s=%s,%s='%s' where id=%d" % (
                    ddt_model.replace('.', '_'),
                    'invoice_id',
                    'null',
                    'state',
                    'draft',
                    ddt.id,
                )
                clodoo.exec_sql(ctx, query)
            clodoo.writeL8(ctx, ddt_model, ddt.id, {'invoice_ids': [(6, 0, invoices)]})
            if ctx['_cr']:
                query = "update %s set %s=%s,%s='%s' where id=%d" % (
                    ddt_model.replace('.', '_'),
                    'invoice_id',
                    max(invoices),
                    'state',
                    ddt_state,
                    ddt.id,
                )
                clodoo.exec_sql(ctx, query)

    print('%d record read, %d record with wrong links!' % (ctr, err_ctr))


def relink_records(ctx):
    print('Relink data on partners. Require a 2nd DB')
    if ctx['param_1'] == 'help':
        print('relink_records src_db FISCALPOS|CHILD')
        return
    if ctx['param_1']:
        src_db = ctx['param_1']
    else:
        src_db = input('Source DB name? ')
    src_ctx = ctx.copy()
    uid, src_ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'], db=src_db, ctx=src_ctx)
    scope = ctx['param_2'].lower() or 'fiscalpos'
    model = 'res.partner'
    err_ctr = 0
    ctr = 0
    TNL = {1: 1, 2: 2, 3: 3, 4: 1, 5: 2, 6: 3, 7: 7}
    for partner in clodoo.browseL8(src_ctx, model, clodoo.searchL8(src_ctx, model, [])):
        msg_burst('%s ...' % partner.name)
        if scope == 'fiscalpos':
            if partner.property_account_position_id:
                try:
                    cur_partner = clodoo.browseL8(ctx, model, partner.id)
                    if not cur_partner.property_account_position_id:
                        position_id = TNL[partner.property_account_position_id.id]
                        clodoo.writeL8(
                            ctx,
                            model,
                            cur_partner.id,
                            {'property_account_position_id': position_id},
                        )
                        ctr += 1
                except BaseException:
                    pass
        elif scope == 'child':
            try:
                cur_partner = clodoo.browseL8(ctx, model, partner.id)
                ctr += 1
                if partner.name != cur_partner.name:
                    print(
                        '... name of %d changed "%s"->"%s"'
                        % (partner.id, partner.name, cur_partner.name)
                    )
                to_check = False
                if (partner.parent_id.id or False) != (
                    cur_partner.parent_id.id or False
                ):
                    print(
                        'Partner %d: parent is changed %s ->%s'
                        % (
                            partner.id,
                            partner.parent_id and partner.parent_id.id or '',
                            cur_partner.parent_id and cur_partner.parent_id.id or '',
                        )
                    )
                    if partner.parent_id:
                        to_check = True
                if partner.type != cur_partner.type:
                    print(
                        'Partner %d: type is changed %s ->%s'
                        % (partner.id, partner.type, cur_partner.type)
                    )
                    to_check = True
                if to_check:
                    err_ctr += 1
                    action = ''
                    while not action:
                        parent = ''
                        if partner.parent_id:
                            parent = partner.parent_id.name
                        print('Partner %s -> %s' % (cur_partner.name, parent))
                        print(' 0. Do nothing')
                        print(' 1. Copy parent_id')
                        print(' 2. Copy type')
                        print(' 3. Copy both')
                        action = input('Action (0,1,2,3): ')
                        if action not in ('0', '1', '2', '3'):
                            action = ''
                    vals = {}
                    if action in ('1', '2'):
                        vals['parent_id'] = partner.parent_id.id
                    if action in ('1', '3'):
                        vals['type'] = partner.type
                    if vals:
                        clodoo.writeL8(ctx, model, cur_partner.id, vals)
            except BaseException:
                pass
    print('%d record read, %d record with wrong links!' % (ctr, err_ctr))


def link_sale_2_invoice(ctx):
    def link_sale_line(ctx, invl_model, inv, invline, soline):
        if ctx.get('_cr'):
            prior_state = inv.state
            query = "UPDATE account_invoice set state='draft' where id=%d" % inv.id
            clodoo.exec_sql(ctx, query)
        clodoo.writeL8(ctx, invl_model, invline.id, {'sale_line_ids': [(3, soline.id)]})
        print('Order line %d.%d linked ...' % (soline.id, soline.order_id.id))
        if ctx.get('_cr'):
            query = "UPDATE account_invoice set state='%s' " "where id=%d" % (
                prior_state,
                inv.id,
            )
            clodoo.exec_sql(ctx, query)

    print('Link sale order lines to invoice lines')
    if ctx['param_1'] == 'help':
        print('link_sale_2_invoice SO INV')
        return
    if ctx['param_1']:
        so_id = eval(ctx['param_1'])
    else:
        so_id = input('Sale Order ID? ')
    if ctx['param_2']:
        inv_id = eval(ctx['param_2'])
    else:
        inv_id = input('Invoice ID? ')
    odoo_ver = eval(ctx['oe_version'].split('.')[0])
    so_model = 'sale.order'
    # sol_model = 'sale.order.line'
    inv_model = 'account.invoice'
    invl_model = 'account.invoice.line'
    so = clodoo.browseL8(ctx, so_model, so_id)
    invs = []
    for id in so.invoice_ids:
        invs.append(id.id)
    print('Read Sale Order [%s] -> %s ...' % (so.name, invs))
    for soline in so.order_line:
        invls = []
        for id in soline.invoice_lines:
            invls.append(id.id)
        print('Reading line [%d] %s -> %s...' % (soline.id, soline.name, invls))
    inv = clodoo.browseL8(ctx, inv_model, inv_id)
    if inv_id in invs:
        action = 'upd'
    else:
        action = 'new'
    sos = []
    if odoo_ver < 10:
        for id in inv.origin_orders:
            sos.append(id.id)
    print('Invoice [%d].%s %s -> %s' % (inv_id, action, inv.number, sos))
    childs = 'invoice_line' if odoo_ver < 10 else 'invoice_line_ids'
    for invline in inv[childs]:
        sols = []
        if odoo_ver >= 10:
            for id in invline.sale_line_ids:
                sols.append(id.id)
        print('Reading line [%d] %s -> %s...' % (invline.id, invline.name, sols))
        linked = False
        for soline in so.order_line:
            if soline.id in sols:
                linked = True
            if soline.id not in sols and soline.product_id == invline.product_id:
                link_sale_line(ctx, invl_model, inv, invline, soline)
        if not linked:
            link_sale_line(ctx, invl_model, inv, invline, soline)


def set_comment_on_invoice(ctx):
    print('Set comment on invoices')
    if ctx['param_1'] == 'help':
        print('set_comment_on_invoice ' '[from_date|+days|ids] [Ask] [Order]')
        return
    if ctx['param_3'] and ctx['param_3'].startswith('O'):
        model = 'sale.order'
        date_field = 'confirmation_date'
        name_field = 'name'
    else:
        model = 'account.invoice'
        date_field = 'date_invoice'
        name_field = 'number'
    date_ids = param_date(ctx['param_1'], model=model, date_field=date_field, ctx=ctx)
    if ctx['param_2'] and ctx['param_2'].startswith('A'):
        comment = input('Text to insert on invoice comment: ')
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
        print('set_ppf_on_partner ' '[ids] [True/False]')
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
    for rec in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % rec.number)
        if not rec.move_id:
            continue
        for line in rec.move_id.line_ids:
            if not line.partner_id:
                if not rec.partner_id.commercial_partner_id:
                    print('Partner %d w/o commercial id' % rec.partner_id.id)
                    clodoo.writeL8(
                        ctx, model_line, line.id, {'partner_id': rec.partner_id.id}
                    )
                    continue
                clodoo.writeL8(
                    ctx,
                    model_line,
                    line.id,
                    {'partner_id': rec.partner_id.commercial_partner_id.id},
                )
    print('%d record updated' % ctr)


def solve_unamed(ctx):
    print('Solve unamed partners')
    if ctx['param_1'] == 'help':
        print('solve_unamed')
        return
    if not ctx.get('_cr'):
        print('No sql support found!')
        print('Some operationes could not be executed!')
        input('Press RET to continue')
    model = 'res.partner'
    ctr = 0
    for rec in clodoo.browseL8(
        ctx,
        model,
        clodoo.searchL8(ctx, model, [('name', '=', False), ('parent_id', '=', False)]),
    ):
        if ctx.get('_cr'):
            query = (
                "select id,partner_id from sale_order "
                "where partner_shipping_id=%d" % rec.id
            )
            response = clodoo.exec_sql(ctx, query, response=True)
            for resp in response:
                query = (
                    "update sale_order set partner_shipping_id=%d "
                    "where id=%d" % (resp[1], resp[0])
                )
                clodoo.exec_sql(ctx, query)
        try:
            clodoo.unlinkL8(ctx, model, rec.id)
            ctr += 1
        except BaseException:
            pass
    for rec in clodoo.browseL8(
        ctx,
        model,
        clodoo.searchL8(
            ctx,
            model,
            [('name', '=', False), ('type', 'in', ['invoice', 'delivery', 'other'])],
        ),
    ):
        if rec.is_company:
            clodoo.writeL8(ctx, model, rec.id, {'is_company': False})
            ctr += 1
    if ctx.get('_cr'):
        query = "select partner_id from sale_order group by(partner_id)"
        response = clodoo.exec_sql(ctx, query, response=True)
        ids = [x[0] for x in response]
        for id in clodoo.searchL8(
            ctx, model, [('customer', '=', False), ('id', 'in', ids)]
        ):
            clodoo.writeL8(ctx, model, id, {'customer': True})
    for rec in clodoo.browseL8(
        ctx,
        model,
        clodoo.searchL8(
            ctx,
            model,
            ['|', ('display_name', '=', False), ('commercial_partner_id', '=', False)],
        ),
    ):
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
    for rec in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        msg_burst('%s ...' % rec.name)
        if rec.electronic_invoice_subjected and not rec.codice_destinatario:
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
        ctx, model, clodoo.searchL8(ctx, model, [('vat', '!=', False)], order='vat')
    ):
        msg_burst('%s ...' % rec.name)
        if rec.vat != prior_vat:
            prior_id = rec.id
            prior_vat = rec.vat
            prior_name = rec.name
            if rec.type != 'contact' or rec.parent_id:
                prior_candidate = True
            else:
                prior_candidate = False
            if (rec.type == 'delivery' and rec.electronic_invoice_subjected) or (
                rec.parent_id and rec.type != 'invoice'
            ):
                vals = {'electronic_invoice_subjected': False}
                clodoo.writeL8(ctx, model, rec.id, vals)
                ctr += 1
            continue
        if rec.type != 'contact' or rec.parent_id:
            vals = {'vat': False}
            if (rec.type == 'delivery' and rec.electronic_invoice_subjected) or (
                rec.parent_id and rec.type != 'invoice'
            ):
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
    model = 'account.account'
    model2 = 'account.group'
    for rec in clodoo.browseL8(ctx, model2, clodoo.searchL8(ctx, model2, [])):
        if len(rec.code_prefix) == 3:
            parent_code = rec.code_prefix[0:2]
        elif len(rec.code_prefix) == 2:
            parent_code = rec.code_prefix[0:1]
        else:
            continue
        parents = clodoo.searchL8(ctx, model2, [('code_prefix', '=', parent_code)])
        if parents:
            clodoo.writeL8(ctx, model, rec.id, {'parent_id': parents[0]})
    for rec in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, [])):
        print(rec.code)
        prefix = rec.code[0:3]
        groups = clodoo.searchL8(ctx, model2, [('code_prefix', '=', prefix)])
        if groups:
            clodoo.writeL8(ctx, model, rec.id, {'group_id': groups[0]})
    #
    model = 'account.financial.report'
    vals = {
        'name': 'Bilancio di verifica semplificato',
        'sequence': 0,
        'account_report_id': False,
    }
    root_id = _synchro(ctx, model, vals)
    vals = {
        'name': 'STATO PATRIMONIALE',
        'sequence': 1,
        'parent_id': root_id,
        'sign': 1,
        'type': 'sum',
        'account_report_id': False,
    }
    asset_liabilities_id = _synchro(ctx, model, vals)
    vals = {
        'name': 'ATTIVITÀ',
        'sequence': 2,
        'parent_id': asset_liabilities_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [
            (
                6,
                9,
                [
                    env_ref(ctx, 'account.data_account_type_credit_card'),
                    env_ref(ctx, 'account.data_account_type_current_assets'),
                    env_ref(ctx, 'account.data_account_type_fixed_assets'),
                    env_ref(ctx, 'account.data_account_type_non_current_assets'),
                    env_ref(ctx, 'account.data_account_type_receivable'),
                    env_ref(ctx, 'account.data_account_type_liquidity'),
                ],
            )
        ],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    asset_id = _synchro(ctx, model, vals)
    vals = {
        'name': 'Liquidità',
        'sequence': 3,
        'parent_id': asset_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [
            (6, 9, [env_ref(ctx, 'account.data_account_type_liquidity')])
        ],
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
        'account_type_ids': [
            (
                6,
                9,
                [
                    env_ref(ctx, 'account.data_account_type_current_liabilities'),
                    env_ref(ctx, 'account.data_account_type_depreciation'),
                    env_ref(ctx, 'account.data_account_type_equity'),
                    env_ref(ctx, 'account.data_account_type_non_current_liabilities'),
                    env_ref(ctx, 'account.data_account_type_payable'),
                    env_ref(ctx, 'account.data_account_type_prepayments'),
                ],
            )
        ],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    _synchro(ctx, model, vals)
    vals = {
        'name': 'Utile (perdita) lordo pre-imposte',
        'sequence': 10,
        'parent_id': root_id,
        'sign': -1,
        'type': 'sum',
        'account_report_id': False,
    }
    lp_id = _synchro(ctx, model, vals)
    vals = {
        'name': 'RICAVI',
        'sequence': 11,
        'parent_id': lp_id,
        'sign': -1,
        'type': 'account_type',
        'account_type_ids': [
            (
                6,
                9,
                [
                    env_ref(ctx, 'account.data_account_type_revenue'),
                    env_ref(ctx, 'account.data_account_type_other_income'),
                    env_ref(ctx, 'account.data_unaffected_earnings'),
                ],
            )
        ],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    _synchro(ctx, model, vals)
    vals = {
        'name': 'COSTI',
        'sequence': 12,
        'parent_id': lp_id,
        'sign': 1,
        'type': 'account_type',
        'account_type_ids': [
            (
                6,
                9,
                [
                    env_ref(ctx, 'account.data_account_type_direct_costs'),
                    env_ref(ctx, 'account.data_account_type_depreciation'),
                    env_ref(ctx, 'account.data_account_type_expenses'),
                ],
            )
        ],
        'display_detail': 'detail_with_hierarchy',
        'account_report_id': False,
    }
    _synchro(ctx, model, vals)


def export_csv(ctx):
    print('Export file CSV')
    if ctx['param_1'] == 'help':
        print('export_csv model domain w|a')
        return
    if ctx['param_1']:
        model = ctx['param_1']
    else:
        model = input('Model? ')
    if ctx['param_2']:
        domain = eval(ctx['param_2'])
    else:
        domain = []
    if ctx['param_3']:
        file_mode = '%sb' % ctx['param_3']
    else:
        file_mode = 'wb'
    # csv_fn = '%s.csv' % model.replace('.', '_')
    csv_fn = '%s.csv' % model
    fields_get = clodoo.executeL8(ctx, model, 'fields_get')
    field_list = [
        x
        for x in fields_get.keys()
        if fields_get[x]['type'] not in ('one2many', 'many2many')
    ]
    ctr = 0
    with open(csv_fn, file_mode) as fd:
        writer = csv.DictWriter(fd, fieldnames=field_list)
        writer.writeheader()
        for rec in clodoo.browseL8(ctx, model, clodoo.searchL8(ctx, model, domain)):
            msg_burst('Id %d...' % rec.id)
            vals = {}
            for field in field_list:
                if rec[field] is False:
                    vals[field] = ''
                elif fields_get[field]['type'] == 'many2one':
                    vals[field] = rec[field].id
                else:
                    vals[field] = _b(rec[field])
            writer.writerow(vals)
            ctr += 1
    print('%d records' % ctr)


def fix_weburl(ctx):
    print('Fix web url to avoid print trouble ...')
    if ctx['param_1'] == 'help':
        print('fix_weburl URL|.')
        return
    if not ctx['param_1']:
        print('Missed URL')
        return
    web_url = ctx['param_1']
    model = 'ir.config_parameter'
    ids = clodoo.searchL8(ctx, model, [('key', '=', 'web.base.url')])
    if len(ids) != 1:
        print('Wrong Odoo configuration')
        return
    cur_web_url = clodoo.browseL8(ctx, model, ids[0]).value
    if web_url == '.':
        web_url = cur_web_url
    if cur_web_url != web_url:
        clodoo.writeL8(ctx, model, ids[0], {'value': web_url})
    ids = clodoo.searchL8(ctx, model, [('key', '=', 'web.base.url.freeze')])
    if ids:
        clodoo.writeL8(ctx, model, ids[0], {'value': '1'})
    else:
        clodoo.createL8(ctx, model, {'key': 'web.base.url.freeze', 'value': '1'})


def revalidate_invoice(ctx):
    print('Revalidate invoices')
    if ctx['param_1'] == 'help':
        print('revalidate_invoice from_date|ids')
        return
    model = 'account.invoice'
    rec_ids = param_date(
        ctx['param_1'],
        model=model,
        date_field='date',
        domain=[('state', '=', 'open')],
        ctx=ctx,
    )
    ctr_read = ctr_err = ctr_upd = 0
    for rec_id in rec_ids:
        ctr_read += 1
        pre_inv = clodoo.browseL8(ctx, model, rec_id)
        msg_burst('%s ...' % pre_inv.number)
        try:
            clodoo.executeL8(ctx, model, 'action_invoice_cancel', rec_id)
        except BaseException:
            continue
        clodoo.executeL8(ctx, model, 'action_invoice_draft', rec_id)
        clodoo.writeL8(ctx, model, rec_id, {})
        clodoo.executeL8(ctx, model, 'action_invoice_open', rec_id)
        post_inv = clodoo.browseL8(ctx, model, rec_id)
        if post_inv.state != 'open':
            ctr_err += 1
            print('Invoice %s [%s] with wrong state!' % (pre_inv.number, rec_id))
        elif (
            post_inv.amount_total != pre_inv.amount_total
            or post_inv.amount_untaxed != pre_inv.amount_untaxed
            or post_inv.amount_tax != pre_inv.amount_tax
            or post_inv.residual != pre_inv.residual
        ):
            ctr_upd += 1
            print('Update invoice %s [%s]!' % (pre_inv.number, rec_id))
    print(
        '%d records read, %d records updated, %d wrong records'
        % (ctr_read, ctr_upd, ctr_err)
    )


def reconcile_invoice(ctx):
    print('Reconcile invoices')
    if ctx['param_1'] == 'help':
        print('revalidate_invoice from_date|ids')
        return
    if not ctx.get('_cr'):
        print('No sql support found!')
        print('Some operationes could not be executed!')
        input('Press RET to continue')
    model = 'account.move.line'
    acctype = clodoo.searchL8(
        ctx, 'account.account.type', [('type', 'in', ('receivable', 'payable'))]
    )
    journals = clodoo.searchL8(
        ctx, 'account.journal', [('type', 'in', ('sale', 'purchase'))]
    )
    rec_ids = param_date(
        ctx['param_1'],
        model=model,
        date_field='date',
        domain=[
            ('user_type_id', 'in', acctype),
            ('journal_id', 'in', journals),
            ('reconciled', '=', False),
        ],
        ctx=ctx,
    )
    ctr_read = ctr_err = ctr_upd = 0
    for line in clodoo.browseL8(ctx, model, rec_ids):
        ctr_read += 1
        print(line)
        match_ids = clodoo.searchL8(
            ctx,
            model,
            [
                ('account_id', '=', line.account_id.id),
                ('partner_id', '=', line.partner_id.id),
                ('reconciled', '=', False),
                ('debit', '=', line.credit),
                ('credit', '=', line.debit),
            ],
        )
        for match_line in clodoo.browseL8(ctx, model, match_ids):
            print('reconcile %s with %s' % (line, match_line))
            try:
                clodoo.executeL8(
                    ctx, 'account.move.line', 'reconcile', [line.id, match_line.id]
                )
                ctr_upd += 1
            except BaseException:
                pass
    print(
        '%d records read, %d records updated, %d wrong records'
        % (ctr_read, ctr_upd, ctr_err)
    )


def reset_statement(ctx):
    print('reconfigure_warehouse')
    if ctx['param_1'] == 'help':
        print('reset_statement STMT_ID hard')
        return
    statement_id = int(ctx['param_1'])
    # hard = ctx['param_2']
    ctr_ulk = 0
    ctr_upd = 0
    model_stmt = "account.bank.statement"
    model_bank = "account.bank.statement.line"
    model_move = "account.move"
    model_line = "account.move.line"
    if ctx.get('param_2', '') == 'hard':
        print('Hard reset of statement id %d' % statement_id)
        for stmt_line in clodoo.browseL8(
                ctx, model_bank, clodoo.searchL8(ctx, model_bank, [
                    ("statement_id", "=", statement_id,
                     "|",
                     ("journal_entry_ids", "!=", []),
                     ('move_name', '!=', False))])):
            clodoo.writeL8(
                ctx, model_bank, stmt_line.id,
                {"move_name": False, "journal_entry_ids": [(5, 0)]})
            ctr_upd += 1
        for move_line in clodoo.browseL8(
                ctx, model_line, clodoo.searchL8(
                    ctx, model_line, [("statement_id", "=", statement_id)])):
            clodoo.writeL8(ctx, model_line, move_line.id, {"statement_id": False})
            ctr_upd += 1
    print('Search for move line wrong linked to this bank statement')
    stmt = clodoo.browseL8(ctx, model_stmt, statement_id)
    to_unlink = []
    for move_line in clodoo.browseL8(
            ctx, model_line, clodoo.searchL8(
                ctx, model_line, [('statement_id', '=', statement_id)])):
        move_name = move_line.move_id.name
        msg_burst('move %s (%s)...' % (move_name, move_line.debit - move_line.credit))
        if move_line in stmt.move_line_ids:
            move_line_linked = True
        else:
            move_line_linked = False
        stmt_line_preferred = False
        for stmt_line in stmt.line_ids:
            # stmt_line in clodoo.browseL8(ctx, model2, stmt_line_id)
            msg_burst('  stmt %s (%s)...' % (stmt_line.name, stmt_line.amount))
            if not stmt_line_preferred and move_line_linked:
                if stmt_line.amount > 0 and stmt_line.amount == move_line.debit:
                    stmt_line_preferred = stmt_line
                elif stmt_line.amount < 0 and -stmt_line.amount == move_line.credit:
                    stmt_line_preferred = stmt_line
            if move_line.move_id.id in stmt_line.journal_entry_ids:
                stmt_line_preferred = stmt_line
                if move_line_linked and not stmt_line.move_name:
                    clodoo.writeL8(
                        ctx, model_bank, stmt_line.id, {'move_name': move_name})
                    ctr_upd += 1
                break
            # if stmt_line.move_name == move_name:
            #     stmt_line_preferred = stmt_line
            #     break
        if stmt_line_preferred and move_line_linked:
            move = clodoo.browseL8(ctx, model_move, move_line.move_id.id)
            move_ids = clodoo.searchL8(
                ctx, model_move, [('statement_line_id', '=', stmt_line_preferred.id)])
            if move_ids and move.id not in move_ids:
                saved_move_id = [x for x in move_ids]
                vals = {}
                vals['statement_line_id'] = stmt_line_preferred.id
                clodoo.writeL8(ctx, 'account.move', move.id, vals)
                ctr_upd += 1
                move_ids = clodoo.searchL8(
                    ctx, model_move,
                    [('statement_line_id', '=', stmt_line_preferred.id)])
                saved_move_id.append(move.id)
                if set(move_ids) != set(saved_move_id):
                    print('Error: moves %s and %s point to the same stmt %s' % (
                        move_ids, move_line.move_id.id, stmt_line_preferred.id
                    ))
                    input('Press RET to continue ...')
            else:
                vals = {}
                if move.statement_line_id != stmt_line_preferred:
                    vals['statement_line_id'] = stmt_line_preferred.id
                    clodoo.writeL8(ctx, 'account.move', move.id, vals)
                    ctr_upd += 1
                vals = {}
                if not stmt_line_preferred.move_name:
                    vals['move_name'] = move_name
                    clodoo.writeL8(ctx, model_bank, stmt_line_preferred.id, vals)
                    ctr_upd += 1
        elif stmt_line_preferred and not move_line_linked:
            to_unlink.append(move_line.id)
            ctr_ulk += 1
        elif not stmt_line_preferred and move_line_linked:
            stmt.move_line_ids = [(3, move_line.id)]
            to_unlink.append(move_line.id)
            ctr_ulk += 1
    if to_unlink:
        clodoo.writeL8(ctx, model_line, to_unlink, {'statement_id': False})
    print('%d records unlinked, %d record updated' % (ctr_ulk, ctr_upd))


def recalc_group_left_right(ctx):
    resorce_group = "account.group"
    ctr = 0
    for group in clodoo.browseL8(
        ctx, resorce_group, clodoo.searchL8(
            ctx, resorce_group, [("parent_id", "=", False)], order="code_prefix")):
        ctr += 1
        print("%s.group.parent_left %s -> %s, level %s -> %s " % (
            group.code_prefix, group.parent_left, ctr, group.level, 1))
        clodoo.writeL8(ctx, resorce_group, group.id, {"parent_left": ctr})
        for group1 in clodoo.browseL8(
            ctx, resorce_group, clodoo.searchL8(
                ctx, resorce_group, [("parent_id", "=", group.id)],
                order="code_prefix")):
            ctr += 1
            print("%s.group.parent_left %s -> %s, level %s -> %s " % (
                group1.code_prefix, group1.parent_left, ctr, group1.level, 2))
            clodoo.writeL8(ctx, resorce_group, group1.id, {"parent_left": ctr})
            for group2 in clodoo.browseL8(
                ctx, resorce_group, clodoo.searchL8(
                    ctx, resorce_group, [("parent_id", "=", group1.id)],
                    order="code_prefix")):
                ctr += 1
                print("%s.group.parent_left %s -> %s, level %s -> %s " % (
                    group2.code_prefix, group2.parent_left, ctr, group2.level, 3))
                clodoo.writeL8(ctx, resorce_group, group2.id, {"parent_left": ctr})
                for group3 in clodoo.browseL8(
                    ctx, resorce_group, clodoo.searchL8(
                        ctx, resorce_group, [("parent_id", "=", group2.id)],
                        order="code_prefix")):
                    ctr += 1
                    print("%s.group.parent_left %s -> %s, level %s -> %s " % (
                        group3.code_prefix, group3.parent_left, ctr, group3.level, 4))
                    clodoo.writeL8(ctx, resorce_group, group3.id, {"parent_left": ctr})
                    for group4 in clodoo.browseL8(
                        ctx, resorce_group, clodoo.searchL8(
                            ctx, resorce_group, [("parent_id", "=", group3.id)],
                            order="code_prefix")):
                        ctr += 1
                        print("%s.group.parent_left %s -> %s, level %s -> %s " % (
                            group4.code_prefix, group4.parent_left, ctr, group4.level,
                            5))
                        clodoo.writeL8(ctx, resorce_group, group4.id,
                                       {"parent_left": ctr})
                        ctr += 1
                        print("%s.group.parent_right %s -> %s" % (
                            group4.code_prefix, group4.parent_right, ctr))
                        clodoo.writeL8(ctx, resorce_group, group4.id,
                                       {"parent_right": ctr})
                    ctr += 1
                    print("%s.group.parent_right %s -> %s" % (
                        group3.code_prefix, group3.parent_right, ctr))
                    clodoo.writeL8(ctx, resorce_group, group3.id, {"parent_right": ctr})
                ctr += 1
                print("%s.group.parent_right %s -> %s" % (
                    group2.code_prefix, group2.parent_right, ctr))
                clodoo.writeL8(ctx, resorce_group, group2.id, {"parent_right": ctr})
            ctr += 1
            print("%s.group.parent_right %s -> %s" % (
                group1.code_prefix, group1.parent_right, ctr))
            clodoo.writeL8(ctx, resorce_group, group1.id, {"parent_right": ctr})
        ctr += 1
        print("%s.group.parent_right %s -> %s" % (
            group.code_prefix, group.parent_right, ctr))
        clodoo.writeL8(ctx, resorce_group, group.id, {"parent_right": ctr})


def rebuild_database(ctx):
    def get_jids_no_vat(ctx):
        return clodoo.searchL8(
            ctx,
            resource_journal,
            ["|",
             ("type", "not in", ["sale", "purchase"]),
             ("code", "in", ("SAJ2", "XIT", "EXJ"))])

    def reset_sequence(ctx):
        resource_journal = "account.journal"
        resource_sequence = "ir.sequence"
        ctr = 0
        for ir_seq in clodoo.browseL8(
            ctx, resource_sequence, clodoo.searchL8(
                ctx, resource_sequence,
                ["|", ("prefix", "like", "%201_/"), ("prefix", "like", "%202_/")])):
            if not clodoo.searchL8(ctx,
                                   resource_journal,
                                   [("sequence_id", "=", ir_seq.id)]):
                clodoo.unlinkL8(ctx, resource_sequence, ir_seq.id)
        journal_no_vat_ids = get_jids_no_vat(ctx)
        for journal in clodoo.browseL8(
            ctx, resource_journal, clodoo.searchL8(
                ctx, resource_journal, [("id", "in", journal_no_vat_ids)])):
            msg_burst("Resetting <%s> ..." % journal.name)
            ir_seq = clodoo.browseL8(ctx, resource_sequence, journal.sequence_id.id)
            if ir_seq.prefix and ir_seq.prefix.startswith("%"):
                prefix = ir_seq.prefix.replace("%(year)s", "%(range_year)s")
            else:
                prefix = journal.code + "/%(range_year)s/"
            vals = {"prefix": prefix} if prefix != ir_seq.prefix else {}
            vals["use_date_range"] = True
            vals["number_next"] = 1
            vals["number_next_actual"] = 1
            clodoo.writeL8(ctx, resource_sequence, journal.sequence_id.id, vals)
            ctr += 1
            for move in ir_seq.date_range_ids:
                clodoo.writeL8(
                    ctx, resource_sequence_range, move.id,
                    {"number_next": 1, "number_next_actual": 1})
                ctr += 1
        return ctr

    def load_inv_att_file(ctx, fn_attach_list):
        attachments = {}
        if os.path.isfile(fn_attach_list):
            with open(fn_attach_list, "r") as fd:
                hdr = True
                csv_obj = csv.DictReader(fd, fieldnames=[], restkey='undef_name')
                for row in csv_obj:
                    if hdr:
                        hdr = False
                        csv_obj.fieldnames = row['undef_name']
                        continue
                    vals = {}
                    for item in ("out", "in", "rc_p", "rc_self", "rc_sp"):
                        if row[item]:
                            vals[item] = int(row[item])
                    attachments[int(row["id"])] = vals
        return attachments

    def store_inv_att_file(ctx, attachments, fn_attach_list):
        with open(fn_attach_list, "w") as fd:
            writer = csv.DictWriter(
                fd, fieldnames=("id", "out", "in", "rc_p", "rc_self", "rc_sp"))
            writer.writeheader()
            for rec_id in attachments.keys():
                vals = {"id": rec_id}
                for item in ("out", "in", "rc_p", "rc_self", "rc_sp"):
                    vals[item] = attachments[rec_id].get(item, "")
                writer.writerow(vals)

    def check_move_type(ctx, move, journal=None):
        resource_invoice = "account.invoice"
        resource_move = "account.move"
        if not journal:
            journal = move.journal_id
        invs = clodoo.searchL8(ctx, resource_invoice, [("move_id", "=", move.id)])
        if invs:
            move_type = move_type_match[clodoo.browseL8(
                ctx, resource_invoice, invs[0]).type]
        elif journal.type in move_type_match:
            move_type = move_type_match[journal.type]
        elif journal.type in ("sale", "purchase"):
            print("Invalid move %d (%s)" % (move.id, move.name))
            move_type = move.move_type
            if move.line_ids:
                print("*** Please recover move %d" % move.id)
            else:
                if move.state == "post":
                    clodoo.executeL8(ctx, resource_move, "button_cancel", move.id)
                clodoo.unlinkL8(ctx, resource_move, move.id)
                return False
        else:
            move_type = "other"
        if move_type != move.move_type:
            print("Invalid move type of id %d" % move.id)
            clodoo.writeL8(ctx, resource_move, move.id, {"move_type": move_type})
        return True

    def cancel_inv_n_save_attachments(ctx):
        def save_attachment(ctx, inv, attachments):
            msg_burst('Saving attachment inv %s (%d) ...' % (inv.number, inv.id))
            vals = {}
            for item, field in (
                ("out", "fatturapa_attachment_out_id"),
                ("in", "fatturapa_attachment_in_id"),
                ("rc_p", "rc_purchase_invoice_id"),
                ("rc_self", "rc_self_invoice_id"),
                ("rc_sp", "rc_self_purchase_invoice_id"),
            ):
                if inv[field]:
                    vals[item] = inv[field].id
            if vals:
                attachments[inv.id] = vals
            query = (
                "update account_invoice"
                " set fatturapa_attachment_out_id=null"
                ",fatturapa_attachment_in_id=null"
                # ",rc_purchase_invoice_id=null"
                # ",rc_self_invoice_id=null"
                # ",rc_self_purchase_invoice_id=null"
                " where id=%d"
            ) % inv.id
            clodoo.exec_sql(ctx, query)

        ctr = 0
        if ctx['_cr']:
            query = (
                "update account_invoice"
                " set state='open'"
                " where state='paid' and amount_total=0.0"
            )
            clodoo.exec_sql(ctx, query)

        fn_attach_list = os.path.expanduser("~/attachments_saved.csv")
        attachments = load_inv_att_file(ctx, fn_attach_list)
        resource_invoice = "account.invoice"
        for inv in clodoo.browseL8(
            ctx, resource_invoice, clodoo.searchL8(
                ctx, resource_invoice, [("type", "in", ["in_invoice", "in_refund"])],
                order="date,id")):
            save_attachment(ctx, inv, attachments)
            if inv.rc_self_invoice_id:
                sinv_id = inv.rc_self_invoice_id.id
                sinv = clodoo.browseL8(ctx, resource_invoice, sinv_id)
                save_attachment(ctx, sinv, attachments)

            if inv.state in ("draft", "open"):
                msg_burst('Cancelling inv %s (%d) ...' % (inv.number, inv.id))
                try:
                    clodoo.executeL8(
                        ctx, resource_invoice, "action_invoice_cancel", inv.id)
                    time.sleep(0.3)
                    ctr += 1
                except BaseException:
                    print("Cannot cancel invoice %s (%d)" % (inv.number, inv.id))
                    input("Press RET to continue")
                    continue
            clodoo.writeL8(ctx, resource_invoice, inv.id, {"move_name": False})
            if inv.rc_self_invoice_id:
                sinv_id = inv.rc_self_invoice_id.id
                sinv = clodoo.browseL8(ctx, resource_invoice, sinv_id)
                if sinv.state != "cancel":
                    print("Self-invoice %s (%d) not cancelled!"
                          % (sinv.move_name, sinv.id))
                    try:
                        clodoo.executeL8(
                            ctx, resource_invoice, "action_invoice_cancel", sinv.id)
                        time.sleep(0.3)
                        ctr += 1
                    except BaseException:
                        print("Cannot cancel invoice %s (%d)" % (sinv.number, sinv.id))
                        input("Press RET to continue")
                        continue
                clodoo.writeL8(ctx, resource_invoice, sinv_id, {"move_name": False})

        store_inv_att_file(ctx, attachments, fn_attach_list)
        return ctr, attachments

    def delete_reconciliations(ctx):
        print("Deleting reconcilations ....")

        ctr = 0

        model = "account.full.reconcile"
        for rec_id in clodoo.searchL8(ctx, model, []):
            try:
                clodoo.unlinkL8(ctx, model, rec_id)
                ctr += 1
            except BaseException:
                pass

        model = "account.partial.reconcile"
        for rec_id in clodoo.searchL8(ctx, model, []):
            try:
                clodoo.unlinkL8(ctx, model, rec_id)
                ctr += 1
            except BaseException:
                pass

        query = "delete from account_full_reconcile"
        clodoo.exec_sql(ctx, query)

        query = "delete from account_partial_reconcile"
        clodoo.exec_sql(ctx, query)

        query = "delete from account_payment"
        clodoo.exec_sql(ctx, query)

        query = "update account_move_line set full_reconcile_id=null,reconciled=false"
        clodoo.exec_sql(ctx, query)

        return ctr

    def cancel_moves(ctx, min_date, company_id):
        print("Canceling moves ...")
        ctr = 0
        journal_no_vat_ids = get_jids_no_vat(ctx)
        domain = [("state", "=", "posted"),
                  ("journal_id", "in", journal_no_vat_ids),
                  ("company_id", "=", company_id),
                  ("date", ">", str(min_date))]
        for rec_id in clodoo.searchL8(ctx, resource_move, domain, order="date,id"):
            msg_burst('Cancelling move id %d ...' % rec_id)
            try:
                clodoo.executeL8(ctx, resource_move, "button_cancel", rec_id)
                ctr += 1
            except BaseException:
                print("Cannot cancel move id %d" % rec_id)
                input("Press RET to continue")
                continue
            query = (
                "update account_move"
                " set name='/'"
                " where id=%d"
            ) % rec_id
            clodoo.exec_sql(ctx, query)
        query = (
            "delete from account_move where journal_id=22"
        )
        clodoo.exec_sql(ctx, query)
        return ctr

    def validate_invoices(ctx):
        print("Validation invoices ...")
        resource_partner = "res.partner"
        ctr = 0
        for inv in clodoo.browseL8(
            ctx, resource_invoice, clodoo.searchL8(
                ctx, resource_invoice,
                [("type", "in", ["in_invoice", "in_refund"])],
                order="date,id")):
            msg_burst('Validating inv %s ...' % inv.move_name)

            if inv.state == "cancel":
                try:
                    clodoo.executeL8(
                        ctx, resource_invoice, "action_invoice_draft", inv.id)
                    time.sleep(0.3)
                    ctr += 1
                    inv.state = "draft"
                except BaseException:
                    pass
            if inv.state != "draft":
                print("Cannot set invoice id %d to draft" % inv.id)
                input("Press RET to continue")
                continue

            if inv.rc_self_invoice_id:
                sinv_id = inv.rc_self_invoice_id.id
                sinv = clodoo.browseL8(ctx, resource_invoice, sinv_id)
                if sinv.state != "draft":
                    print("Cannot set invoice id %d to draft" % sinv.id)
                    input("Press RET to continue")
                    continue

            clodoo.executeL8(ctx, resource_invoice, "compute_taxes", inv.id)
            inv = clodoo.browseL8(ctx, resource_invoice, inv.id)
            vals = {
                "check_total": inv.amount_total
            }
            if not inv.fiscal_position_id:
                partner = clodoo.browseL8(ctx, resource_partner, inv.partner_id.id)
                vals["fiscal_position_id"] = partner.property_account_position_id.id
            clodoo.writeL8(
                ctx, resource_invoice, inv.id, vals)
            try:
                clodoo.executeL8(ctx, resource_invoice, "action_invoice_open", inv.id)
                time.sleep(0.3)
                ctr += 1
            except BaseException:
                pass

            inv = clodoo.browseL8(ctx, resource_invoice, inv.id)
            if inv.state not in ["open", "paid"]:
                print("Cannot validate invoice id %d" % inv.id)
                input("Press RET to continue")
                continue

            if inv.rc_self_invoice_id:
                sinv_id = inv.rc_self_invoice_id.id
                sinv = clodoo.browseL8(ctx, resource_invoice, sinv_id)
                if sinv.state not in ["open", "paid"]:
                    print("Cannot set invoice id %d to draft" % sinv.id)
                    input("Press RET to continue")
                    continue

            inv = clodoo.browseL8(ctx, resource_invoice, inv.id)
            # recalc_sequence(ctx, inv.journal_id, inv.number)
            if inv.rc_self_invoice_id:
                sinv_id = False
                att_out = False
                if inv.id in attachments:
                    if "rc_self" in attachments[inv.id]:
                        sinv_id = attachments[inv.id]["rc_self"]
                    else:
                        print("Warning! Invoice %s (%d) configuration changed"
                              % (inv.number, inv.id))
                    if sinv_id and "out" in attachments[sinv_id]:
                        att_out = attachments[sinv_id]["out"]
                    else:
                        print("Invalid self invoice %s (%d) configuration"
                              % (inv.number, inv.id))
                        # input("Press RET to continue")
                else:
                    print("Invoice %s (%d) configuration not found"
                          % (inv.number, inv.id))
                    # input("Press RET to continue")
                if att_out:
                    # Move attachment from prior self-invoice to current
                    self_inv = clodoo.browseL8(
                        ctx, resource_invoice, inv.rc_self_invoice_id.id)
                    if self_inv.fatturapa_attachment_out_id:
                        try:
                            clodoo.unlinkL8(
                                ctx,
                                resource_att_out,
                                self_inv.fatturapa_attachment_out_id.id)
                        except BaseException:
                            print("Cannot delete attachment id %d" %
                                  self_inv.fatturapa_attachment_out_id.id)
                    clodoo.writeL8(
                        ctx,
                        resource_invoice,
                        self_inv.id, {"fatturapa_attachment_out_id": att_out})

                if sinv_id in attachments and "rc_self" in attachments[sinv_id]:
                    del attachments[inv.id]["rc_self"]
                if inv.id in attachments and not attachments[inv.id]:
                    del attachments[inv.id]
            elif inv.id in attachments and "rc_self" in attachments[inv.id]:
                print("Invoice %s (%d): self-invoice configuration lost"
                      % (inv.number, inv.id))
                input("Press RET to continue")

            if inv.id in attachments and "out" in attachments[inv.id]:
                att_out = attachments[inv.id]["out"]
                state = clodoo.browseL8(ctx, "fatturapa.attachment.out", att_out)
                try:
                    clodoo.writeL8(
                        ctx,
                        resource_invoice,
                        inv.id,
                        {
                            "fatturapa_attachment_out_id": att_out,
                            "fatturapa_state": state,
                        })
                except BaseException:
                    print("Cannot link attachment %d to invoice %d" % (att_out, inv.id))
                    continue
                del attachments[inv.id]["out"]
                if not attachments[inv.id]:
                    del attachments[inv.id]

            if inv.id in attachments and "in" in attachments[inv.id]:
                att_in = attachments[inv.id]["in"]
                try:
                    clodoo.writeL8(
                        ctx,
                        resource_invoice,
                        inv.id,
                        {"fatturapa_attachment_in_id": att_in})
                except BaseException:
                    print("Cannot link attachment %d to invoice %d" % (att_in, inv.id))
                    continue
                clodoo.writeL8(
                    ctx, "fatturapa.attachment.in", att_in, {"registered": True})
                del attachments[inv.id]["in"]
                if not attachments[inv.id]:
                    del attachments[inv.id]
        return ctr

    def validate_moves(ctx):
        print("Validation moves ...")
        journal_no_vat_ids = get_jids_no_vat(ctx)
        ctr = 0
        domain = [("state", "=", "draft"), ("journal_id", "in", journal_no_vat_ids)]
        for move in clodoo.browseL8(
            ctx, resource_move, clodoo.searchL8(
                ctx, resource_move, domain, order="date,oe7_id,id")):
            msg_burst('Validating move id %d ...' % move.id)
            check_move_type(ctx, move)
            try:
                clodoo.writeL8(ctx, resource_move, move.id, {"name": "/"})
            except BaseException:
                print("Cannot removing entry name %d" % move.id)
            try:
                clodoo.executeL8(ctx, resource_move, "post", move.id)
                ctr += 1
                # recalc_sequence(ctx, move.journal_id, move.name)
            except BaseException:
                print("Cannot post move id %d" % move.id)
        return ctr

    def reconcile_invoices(ctx, sel_account_id, journals):
        _mv = "account.move"
        _ml = "account.move.line"
        _afr = "account.full.reconcile"
        query = (
            "select partner_id from account_invoice"
            " group by partner_id order by partner_id")
        response = clodoo.exec_sql(ctx, query, response=True)
        for res in response:
            sel_partner_id = res[0]
            for ln in clodoo.browseL8(
                    ctx, _ml, clodoo.searchL8(
                        ctx, _ml, [
                            ("account_id", "=", sel_account_id),
                            ("partner_id", "=", sel_partner_id),
                            ("journal_id.type", "in", journals)],
                        order="date,id")):
                ln2_ids = clodoo.searchL8(
                    ctx,
                    _ml,
                    [
                        ("account_id", "=", sel_account_id),
                        ("partner_id", "=", sel_partner_id),
                        ("debit" if ln.credit > 0.0 else "credit",
                         "=", ln.credit if ln.credit > 0.0 else ln.debit),
                        ("date", ">=", datetime.strftime(ln.date, "%Y-%m-%d"))
                    ],
                    order="date,id")
                if not ln2_ids:
                    continue
                if ln.full_reconcile_id:
                    reconcile = clodoo.browseL8(ctx, _afr, ln.full_reconcile_id.id)
                    reconcile_ids = [x.id for x in reconcile.reconciled_line_ids]
                else:
                    reconcile_ids = []
                mv = clodoo.browseL8(ctx, _mv, ln.move_id.id)
                print("Inv to reconcile %d - %s in %s (%s) - (%d - %s)"
                      % (mv.id, mv.name,
                         datetime.strftime(mv.date, "%d-%m-%Y"),
                         mv.ref, ln.id, ln.name,))
                for ln2_id in ln2_ids:
                    ln2 = clodoo.browseL8(ctx, _ml, ln2_id)
                    mv2 = clodoo.browseL8(ctx, _mv, ln2.move_id.id)
                    flag = "*" if ln2_id in reconcile_ids else "-"
                    print(" %s Pay %d - %s in %s (%s) - (%d - %s)"
                          % (flag, mv2.id, mv2.name,
                             datetime.strftime(mv.date, "%d-%m-%Y"),
                             mv2.ref, ln2.id, ln2.name))
                if len(ln2_ids) == 1 and flag == "*":
                    continue
                dummy = input("Action (Continue,ID)? ")
                if dummy and dummy.isdigit():
                    new_rec_id = int(dummy)
                    if new_rec_id not in ln2_ids:
                        print("Invalid choice!")
                        continue
                    print("Reconcile %d with %d" % (ln.id, new_rec_id))
                    ln2 = clodoo.browseL8(ctx, _ml, ln2_id)
                    reconciles = [ln.id, new_rec_id]
                    try:
                        context = {
                            'active_ids':
                                [x.id for x in ln.full_reconcile_id.reconciled_line_ids]
                        }
                        clodoo.executeL8(
                            ctx, 'account.unreconcile', 'trans_unrec', None, context
                        )
                    except BaseException:
                        print('!!Move %d unreconciliable!' % mv.id)
                        # continue
                    try:
                        context = {
                            'active_ids':
                                [x.id
                                 for x in ln2.full_reconcile_id.reconciled_line_ids]
                        }
                        clodoo.executeL8(
                            ctx, 'account.unreconcile', 'trans_unrec', None, context
                        )
                    except BaseException:
                        print('!!Move %d unreconciliable!' % ln2.id)
                        # continue
                    try:
                        clodoo.executeL8(
                            ctx, 'account.move.line', 'reconcile', reconciles
                        )
                    except BaseException:
                        print('!!Moves %s not reconciliable!' % reconciles)

    def recalc_sequence(ctx, journal, name):
        resource_sequence = "ir.sequence"
        ir_seq = clodoo.browseL8(ctx, resource_sequence, journal.sequence_id.id)
        prefix = ir_seq.prefix.replace("%(year)s", "%(range_year)s")
        if prefix != ir_seq.prefix:
            clodoo.writeL8(ctx, resource_sequence, ir_seq.id, {"prefix": prefix})
        parts = name.split("/")
        if len(parts) == 3 and len(parts[1]) == 4 and parts[1].startswith("2"):
            # i.e. "SAJ/2023/1234
            next_number = int(parts[2]) + 1
            year = int(parts[1])
        elif (
            len(parts) == 2 and len(parts[0]) == 4 and parts[0].startswith("2")
        ):
            # i.e. "2013/0123"
            next_number = int(parts[1]) + 1
            year = int(parts[0])
        else:
            print("Unrecognized number %s" % name)
            return
        range_ids = clodoo.searchL8(
            ctx, resource_sequence_range, [
                ("sequence_id", "=", journal.sequence_id.id),
                ("date_from", ">=", "%d-01-01" % year),
                ("date_to", "<=", "%d-12-31" % year),
            ])
        if len(range_ids) > 1:
            print("Invalid sequence range %s for id %s" % (year, journal.code))
        elif not range_ids:
            clodoo.createL8(ctx, resource_sequence_range, {
                "sequence_id": journal.sequence_id.id,
                "date_from": "%d-01-01" % year,
                "date_to": "%d-12-31" % year,
                "number_next": next_number,
                "number_next_actual": next_number,
            })
        else:
            ir_seq_range = clodoo.browseL8(ctx, resource_sequence_range, range_ids[0])
            if (
                ir_seq_range.number_next < next_number
                or ir_seq_range.number_next_actual < next_number
            ):
                clodoo.writeL8(ctx,
                               resource_sequence_range,
                               range_ids[0],
                               {
                                   "number_next": next_number,
                                   "number_next_actual": next_number,
                               })

    print('🎺🎺🎺 Rebuild database')
    if ctx['param_1'] == 'help':
        print('rebuild_database [no-invoice|no-reconcile]')
        return

    move_type_match = {
        "out_invoice": "receivable",
        "out_refund": "receivable_refund",
        "in_invoice": "payable",
        "in_refund": "payable_refund",
        "bank": "liquidity",
        "cash": "liquidity",
    }
    resource_company = "res.company"
    # resource_partner = "res.partner"
    resource_invoice = "account.invoice"
    resource_move = "account.move"
    resource_journal = "account.journal"
    # resource_sequence = "ir.sequence"
    resource_sequence_range = "ir.sequence.date_range"
    resource_att_out = "fatturapa.attachment.out"
    # resource_att_in = "fatturapa.attachment.in"
    ctr = 0

    company_id = 3
    company = clodoo.browseL8(ctx, resource_company, company_id)
    min_date = company.fiscalyear_lock_date or "2013-01-01"
    if company.period_lock_date and company.period_lock_date < min_date:
        min_date = company.period_lock_date

    # reconcile_invoices(ctx, 854, ["sale", "sale_refund"])
    # reconcile_invoices(ctx, 1010, ["purchase", "purchase_refund"])

    print("Resetting sequences ...")
    for rec_id in clodoo.searchL8(ctx,
                                  resource_journal,
                                  [("update_posted", "=", False),
                                   ("company_id", "=", company_id)]):
        clodoo.writeL8(ctx, resource_journal, rec_id, {"update_posted": True})
        ctr += 1
    ctr += reset_sequence(ctx)

    if not ctx['param_1'] or "no-rec" not in ctx['param_1']:
        ctr += delete_reconciliations(ctx)

    attachments = {}
    if not ctx['param_1'] or "no-inv" not in ctx['param_1']:
        ctr, attachments = cancel_inv_n_save_attachments(ctx)

    ctr += cancel_moves(ctx, min_date, company_id)

    if not ctx['param_1'] or "no-inv" not in ctx['param_1']:
        ctr += validate_invoices(ctx)

    fn_attach_list = os.path.expanduser("~/attachments_saved.csv")
    store_inv_att_file(ctx, attachments, fn_attach_list)

    ctr += validate_moves(ctx)

    print("%d records update!" % ctr)


def migrate_project_timesheet(ctx):
    print('Migrate timesheet of a project. Require a 2nd DB')
    if ctx['param_1'] == 'help':
        print('migrate_project_timesheet src-prjtsk_id')
        return
    if not ctx['from_dbname']:
        print("Missed DB name! Use -z")
        return
    if not ctx['from_confn']:
        print("Missed confn! Use -w")
        return
    if not ctx['param_1']:
        print("Missed source task_id! Use -1")
        return
    if not ctx['param_2']:
        print("Missed target project task_id! Use -2")
        return

    src_ctx = ctx.copy()
    src_ctx["confn"] = src_ctx['from_confn']
    src_ctx["db_name"] = src_ctx['from_dbname']
    del src_ctx["odoo_vid"]
    # src_ctx["svc_protocol"] = "xmlrpc"
    # src_ctx["oe_version"] = "xmlrpc"
    uid, src_ctx = clodoo.oerp_set_env(confn=src_ctx['confn'],
                                       db=src_ctx['db_name'],
                                       ctx=src_ctx)

    _prj_task_work = "project.task.work"
    _prj_task = "project.task"
    _acc_anline = "account.analytic.line"
    prj_task = clodoo.browseL8(ctx, _prj_task, int(ctx['param_2']))

    for ln in clodoo.browseL8(
            src_ctx, _prj_task_work, clodoo.searchL8(
                src_ctx, _prj_task_work, [
                    ("task_id", "=", int(ctx['param_1']))])):
        print("%-60.60s %6s %s" % (ln.name, ln.hours, ln.date))
        vals = {
            "account_id": False,
            "amount": 0.0,
            "company_id": prj_task.company_id.id,
            "date": datetime.strftime(ln.date, "%Y-%m-%d"),
            "name": ln.name,
            "partner_id": False,
            "project_id": prj_task.project_id.id,
            "task_id": prj_task.id,
            "unit_amount": ln.hours,
            "user_id": prj_task.project_id.user_id.id,
        }
        clodoo.createL8(ctx, _acc_anline, vals)


RND_NAME_IT = [
    "Giuseppe", "Giovanni", "Antonio", "Mario", "Luigi",
    "Maria", "Anna", "Rosa", "Angela", "Teresa", "Lucia",
    "Andrea", "Leonardo", "Alessandro", "Aurora", "Giulia",
    "Gaia", "Alice", "Marco", "Lorenzo", "Luca", "Nicholas",
    "Azzurra", "Bianca", "Celeste", "Viola", "Michele",
    "Raffaele", "Daniele", "Pietro", "Vincenzo", "Bruno",
    "Natale", "Rita", "Margherita", "Aldo", "Paolo",
    "Luciano", "Sergio", "Alessio", "Tommaso", "Riccardo",
    "Edoardo", "Federico", "Beatrice", "Francesco", "Vittorio",
    "Ludovica", "Enea", "Virgilio", "Cesare", "Augusto",
    "Leone", "Felice", "Umberto", "Filippo", "Ciro",
    "Cinzia", "Antonello",
]
RND_NAME_XX = [
    "Noah", "John", "Francis", "Jackob", "William", "Geroge",
    "Emma", "Olivia", "Sophia", "Abigail", "Emily", "Elizabeth",
    "Jack", "Harry", "Gil", "Rosemary", "Lilith", "Amelia",
    "Sienna", "Ethan", "Charlie", "Thomas", "Edward", "Dylan",
    "Bert", "Billy", "Giles", "Harold", "Quincy",
    "Simon", "Teddy", "Tony", "Walter",
]
RND_LASTNAME_IT = [
    "ROSSI", "FERRARI", "BIANCHI", "ROMANO", "VERDI",
    "GENOVESE", "TOSCANO", "ANCONETANO", "NAPOLITANO", "PUGLISI",
    "MARINO", "GRECO", "LOMBARDI", "COLOMBO", "GALLI", "GENTILE",
    "FONTANA", "PADOVANO", "PERUGINO", "SICILIANO", "FERRERO",
    "MORETTI", "GIORDANO", "TESTA", "NERI", "MAZZA", "MARTINELLI",
    "DI LORENZO", "FAGIANI", "SANTORO", "BARBIERI", "CASANOVA",
    "COSTA", "LONGO", "DE LUCA", "ESPOSITO", "SAVASTA",
    "RIZZO", "SERRA", "PELLEGRINI", "POLLI", "PORTOGHESE",
    "SPAGNOLO", "FRANCO", "TURCO", "PACIFICO",
]
RND_LASTNAME_XX = [
    "BROOKS", "CHAPMAN", "COOPER", "FISHER", "FOX",
    "HAMILTON", "JACKSON", "LEE", "PALMER", "TAYLOR",
    "SMITH", "WELLS", "MARTIN", "GARCIA", "ROUX",
    "JONES", "BROWN", "WILSON", "WRIGHT", "WALKER", "WHITE",
    "LEROY", "MERCIERS", "DUMONT", "FISCHER",
]
RND_CITY_IT = [
    "Torino", "Milano", "Roma", "Napoli", "Pistoia", "Genova",
    "Firenze", "Bologna", "Venezia", "Bari", "Palermo",
    "Cagliari", "Pescara", "Domodossola", "Empoli", "Jesolo",
    "Lucca", "Montecatini", "Sassari", "Catania", "Lecce",
    "Salerno", "Perugia", "Sanremo", "Brescia", "Bergamo",
    "Verona", "Trieste", "Ravenna", "Matera", "Crotone",
    "Siracusa", "Agrigento", "Marsala", "La Spezia",
]
RND_CITY_PREFIX_IT = [
    "Quarto", "Quinto", "Sesto", "Settimo", "Finale", "Marina"
]
RND_CITY_XX = [
    "Wien", "Antwerpen", "Sofija", "Zagreb", "Copenaghen",
    "Helsinki", "Paris", "Berlin", "Athina", "Dublin",
    "Amsterdam", "Warszawa", "Lisboa", "London", "Praha",
    "Madrid", "Budapest", "Tel Aviv", "Casablanca", "New York",
    "Los Angeles", "Atalanta", "Motevideo",
]
RND_TLD = [
    "gmail.com", "outlook.com", "libero.it", "example.com",
    "hotmail.com",
]


def anonimize_database(ctx):
    def rnd_item(ctx, rndlist):
        return rndlist[random.randint(0, len(rndlist) - 1)]

    def read_partner(id):
        try:
            partner = clodoo.browseL8(ctx, _partner, id)
            vals = {}
        except BaseException:
            vals = {
                "name": "Unknown %d" % id,
                "vat": False,
                "codicefiscale": False,
            }
        if vals:
            clodoo.writeL8(ctx, _partner, id, vals)
            partner = clodoo.browseL8(ctx, _partner, id)
        return partner

    def build_random_data(ctx, id):
        partner = read_partner(id)
        if partner.country_id and partner.country_id.id != country_it_id:
            name = rnd_item(ctx, RND_NAME_XX) + " " + rnd_item(ctx, RND_LASTNAME_XX)
            city = rnd_item(ctx, RND_CITY_XX)
            zip = ""
            if partner.vat:
                name += " Ltd"
        else:
            name = rnd_item(ctx, RND_NAME_IT) + " " + rnd_item(ctx, RND_LASTNAME_IT)
            if id % 3:
                city = rnd_item(ctx, RND_CITY_IT)
            else:
                city = rnd_item(ctx, RND_CITY_PREFIX_IT) + " di " + rnd_item(
                    ctx, RND_CITY_IT)
            zip = "%03d00" % random.randint(1, 999)
            if partner.vat:
                name += " s.r.l."
        email = name.lower().replace(" ", ".") + "@" + rnd_item(ctx, RND_TLD)
        phone = "0%d" % random.randint(200000000, 999999999)
        mobile = "3%d" % random.randint(200000000, 999999999)
        return {
            "name": name,
            "city": city,
            "email": email,
            "zip": zip,
            "phone": phone,
            "mobile": mobile,
            "comment": "",
            "text_GECS": "",
        }

    print('🎺🎺🎺 Anonimize database')
    if ctx['param_1'] == 'help':
        print('anonimize_database')
        return

    _partner = "res.partner"
    _user = "res.users"
    _company = "res.company"
    _country = "res.country"
    country_it_id = clodoo.searchL8(ctx, _country, [("code", "in", ["it", "IT"])])[0]
    protected_partner_ids = []
    for id in clodoo.searchL8(ctx, _user, []):
        try:
            user = clodoo.browseL8(ctx, _user, id)
            msg_burst('%d) %s ...' % (id, user.login))
            protected_partner_ids.append(user.partner_id.id)
        except BaseException:
            pass
    for id in clodoo.searchL8(ctx, _company, []):
        clodoo.writeL8(ctx, _company, id, {"name": "Test Company %d" % id})
    for id in clodoo.searchL8(ctx,
                              _partner,
                              [("id", "not in", protected_partner_ids)],
                              order="id"):
        vals = build_random_data(ctx, id)
        msg_burst('%d) %s ...' % (id, vals["name"]))
        try:
            clodoo.writeL8(ctx, _partner, id, vals)
        except BaseException:
            pass


def move_database_by_postgres(ctx):
    print('🎺🎺🎺 Move database from postgres version to another')
    if ctx['param_1'] == 'help':
        print('move_database_by_postgres pg_port_orig pg_port_dest role')
        return
    if not ctx.get('param_1'):
        print("Missed postgres port of orig")
        print('move_database_by_postgres pg_port_orig pg_port_dest role')
        return
    if not ctx.get('param_2'):
        print("Missed postgres port of dest")
        print('move_database_by_postgres pg_port_orig pg_port_dest role')
        return
    if not ctx.get('param_3'):
        print("Missed postgres role")
        print('move_database_by_postgres pg_port_orig pg_port_dest role')
        return
    if not ctx['_cr']:
        print("Cannot connect via SQL")
        return
    pg_port_orig = ctx['param_1']
    pg_port_dest = ctx['param_2']
    role = ctx['param_3']
    response = clodoo.exec_sql(
        ctx,
        ("SELECT d.datname,pg_catalog.pg_get_userbyid(d.datdba)"
         " FROM pg_catalog.pg_database d order by d.datname"),
        response=True)
    dry_run = False
    sqlfn = os.path.expanduser("~/db.sql")
    ctr = 0
    for rec in response:
        db = rec[0]
        if (
            db.startswith("template")
            or db.startswith("test")
            or db.startswith("postgres")
            or db.startswith("demo")
            or db.startswith("oca")
        ):
            continue
        owner = rec[1]
        if owner != role:
            continue
        if os.path.isfile(sqlfn):
            os.unlink(sqlfn)
        sts, stdout, stderr = z0lib.run_traced(
            "pg_dump -p%s -d \"%s\" -U%s -Fp -f %s" % (pg_port_orig, db, role, sqlfn),
            verbose=True, dry_run=dry_run)
        print(stdout)
        if not dry_run and sts:
            print("Error %d" % sts)
            print(stderr)
            return
        if not os.path.isfile(sqlfn):
            print("Non sql file %s found" % sqlfn)
            return
        sts, stdout, stderr = z0lib.run_traced(
            "createdb -p%s -U%s \"%s\"" % (pg_port_dest, role, db),
            verbose=True, dry_run=dry_run)
        print(stdout)
        if not dry_run and sts:
            print("Error %d" % sts)
            print(stderr)
            return
        sts, stdout, stderr = z0lib.run_traced(
            "psql -p%s -U%s \"%s\" -f %s" % (pg_port_dest, role, db, sqlfn),
            verbose=True, dry_run=dry_run)
        # print(stdout)
        if not dry_run and sts:
            print("Error %d" % sts)
            print(stderr)
            return
        os.unlink(sqlfn)
        ctr += 1
    print("%d databases moved")


def display_stock(ctx):
    _picking = "stock.picking"
    # _operation = "stock.pack.operation"
    # _product = "product.product"
    picking_id = 0
    while picking_id >= 0:
        picking_id = input("\nPicking ID (-1 to end): ")
        picking_id = eval(picking_id) if picking_id else 0
        if picking_id == 0:
            continue
        elif picking_id < 0:
            break
        try:
            picking = clodoo.browseL8(ctx, _picking, picking_id)
        except BaseException:
            print("Picking %d not found!" % picking_id)
            continue
        print("Picking name: %s" % picking.name)
        print("Picking state: %s" % picking.state)
        fmt = (
            "prod.%(product_id)5s %(product_name)-30.30s %(ordered_qty)7s"
            " %(product_qty)7s  %(qty_done)7s %(ln_move_ids)8s"
        )
        fmt_m = (
            "move.%(move_id)5s %(name)-30.30s %(ordered_qty)7s"
            " %(product_qty)7s"
        )
        print(fmt % {
            "product_id": "id",
            "product_name": "product_name",
            "product_qty": "p.qty",
            "ordered_qty": "o.qty",
            "qty_done": "done",
            "ln_move_ids": "ln",
        })
        for operation in picking.pack_operation_product_ids:
            params = {
                "product_id": operation.id,
                "product_name": operation.product_id.name,
                "product_qty": operation.product_qty,
                "ordered_qty": operation.ordered_qty,
                "qty_done": operation.qty_done,
                "ln_move_ids": operation.linked_move_operation_ids.ids,
            }
            print(fmt % params)
            for ln in operation.linked_move_operation_ids:
                params_m = {
                    "move_id": ln.move_id.id,
                    "name": ln.move_id.name,
                    "product_qty": ln.move_id.product_qty,
                    "ordered_qty": ln.move_id.ordered_qty,
                }
                print(fmt_m % params_m)


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs(
        "Odoo test environment", "© 2017-2021 by SHS-AV s.r.l.", version=__version__
    )
    parser.add_argument('-h')
    parser.add_argument(
        "-A",
        "--action",
        help="internal action to execute",
        dest="function",
        metavar="python_name",
        default='',
    )
    parser.add_argument(
        "-c",
        "--config",
        help="configuration command file",
        dest="conf_fn",
        metavar="file",
        default='./inv2draft_n_restore.conf',
    )
    parser.add_argument(
        "-d",
        "--dbname",
        help="DB name to connect",
        dest="db_name",
        metavar="file",
        default='',
    )
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument(
        "-w",
        "--src-config",
        help="Source DB configuration file",
        dest="from_confn",
        metavar="file",
    )
    parser.add_argument(
        "-z",
        "--src-db_name",
        help="Source database name",
        dest="from_dbname",
        metavar="name",
    )
    parser.add_argument(
        "-1", "--param-1", help="value to pass to called function", dest="param_1"
    )
    parser.add_argument(
        "-2", "--param-2", help="value to pass to called function", dest="param_2"
    )
    parser.add_argument(
        "-3", "--param-3", help="value to pass to called function", dest="param_3"
    )
    parser.add_argument(
        "-4", "--param-4", help="value to pass to called function", dest="param_4"
    )
    parser.add_argument(
        "-5", "--param-5", help="value to pass to called function", dest="param_5"
    )
    parser.add_argument(
        "-6", "--param-6", help="value to pass to called function", dest="param_6"
    )

    ctx = parser.parseoptargs(cli_args, apply_conf=False)
    uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'], db=ctx['db_name'], ctx=ctx)
    # os0.set_tlog_file('./odoo_shell.log', echo=True)

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
    print(' - set_products_delivery_policy  - unlink_ddt_from_invoice')
    print(' - set_fiscal_on_products        COMMISSION')
    print(' ACCOUNT                         - create_commission_env')
    print(' - create_RA_config              DELIVERY/SHIPPING')
    print(' - manage_due_line               - change_ddt_number')
    print(' PARTNER/USER                    - create_delivery_env')
    print(' - check_integrity_by_vg7        - show_empty_ddt')
    print('                                 RIBA')
    print(' - set_ppf_on_partner            - configure_RiBA')
    print(' - deduplicate_partner           - manage_riba')
    print(' - reset_email_admins             OTHER TABLES')
    print(' - solve_unamed                   - set_report_config')
    print(' - solve_flag_einvoice            - setup_balance_report')
    print(' - simulate_user_profile          - show_module_group')
    print(' SYSTEM                           - check_rec_links')
    print(' - clean_translations             - display_module')
    print(' - configure_email_template')
    print(' - test_synchro_vg7')
    print(' - set_db_4_test')
    print(' - fix_weburl')

    pdb.set_trace()
    print('\n\n')
    pdb.set_trace()


if __name__ == "__main__":
    exit(main())
