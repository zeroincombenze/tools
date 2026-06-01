#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# from email.utils import supports_strict_parsing

import sys
import time
from builtins import *  # noqa
from builtins import input
from datetime import date, datetime, timedelta
# import itertools

from future import standard_library

# from os0 import os0  # pylint: disable=import-error
# from python_plus import _b

try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib

# import pdb  # pylint: disable=deprecated-module

standard_library.install_aliases()  # noqa: E402


__version__ = '2.1.0'


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


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs(
        "Resolve row without tax code", "© 2017-2026 by SHS-AV s.r.l.",
        version=__version__
    )
    parser.add_argument('-h')
    parser.add_argument(
        "-A",
        "--action",
        help="Actions to run:"
             " dup_addr,inv_no_tax,so_no_tax,wrong_delivery"
             ",equal_delivery,unmatch_delivery_partner,q2so",
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
    parser.add_argument(
        "-f",
        "--from-date",
    )
    parser.add_argument(
        "-l",
        "--invoice-list",
        help="invoice list",
    )
    parser.add_argument(
        "-o",
        "--order-list",
        help="order list",
    )
    parser.add_argument(
        "-s",
        "--send-mail",
        action='store_true',
        help="Activate send mail",
    )
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')

    ctx = parser.parseoptargs(cli_args, apply_conf=False)
    uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'], db=ctx['db_name'], ctx=ctx)
    ctx["action"] = ctx["action"].split(",") if ctx["action"] else False

    _AI = "account.invoice"
    _AIL = "account.invoice.line"
    _AT = "account.tax"
    _DDT = "stock.picking.package.preparation"
    _RP = "res.partner"
    _SM = "stock.move"
    _SO = "sale.order"
    _SOL = "sale.order.line"
    _SP = "stock.picking"

    company_id = 3
    tax_id = clodoo.searchL8(ctx, _AT,
                             [("amount", "=", 22),
                              ("company_id", "=", company_id)])[0]
    from_date = ctx["from_date"] or "2026-03-30"
    to_send_mail = ctx["send_mail"]


    ###########################################################################
    if not ctx["action"] or "dup_addr" in ctx["action"]:
        print("Searching for duplicate addresses")
        trace = ""
        ctr = 0
        splash = 32
        for partner in clodoo.browseL8(
                ctx, _RP, clodoo.searchL8(
                    ctx, _RP, [("type", "in", ["delivery", "invoice"])])):
            msg_burst("  ... %s" % partner.name)
            if not partner.parent_id:
                vg7_id = partner.vg7_id
                if vg7_id > 100000000:
                    parent_id = clodoo.searchL8(
                        ctx, _RP, [("vg7_id", "=", vg7_id - 100000000)])
                    if not parent_id:
                        ctr += 1
                        clodoo.writeL8(ctx, _RP, partner.id, {"active": False})
                        continue
                    clodoo.writeL8(
                        ctx, _RP, partner.id, {"parent_id": parent_id[0]})
            parent = clodoo.browseL8(ctx, _RP, partner.parent_id.id)
            if (
                parent.street == partner.street
                and parent.city == partner.city
                and parent.zip == partner.zip
            ):
                ctr += 1
                clodoo.writeL8(ctx, _RP, partner.id, {"active": False})
                continue

        print("")
        print("")
        print("%s partners updated" % ctr)
        print("")
        print(trace)

    ###########################################################################
    if not ctx["action"] or "inv_no_tax" in ctx["action"]:
        print("Searching for invoice lines without tax code")
        trace = ""
        if ctx["invoice_list"]:
            lines = []
            orders = []
            for inv_num in ctx["invoice_list"].split(","):
                invoice_id = clodoo.searchL8(
                    ctx, _AI, [("number", "=", inv_num)])
                if not invoice_id:
                    print("Invalid invoice number %s" % inv_num)
                    return 1
                orders.append(invoice_id[0])
        else:
            lines = clodoo.browseL8(
                ctx, _AIL,
                clodoo.searchL8(
                    ctx, _AIL,
                    [("invoice_id.type", "in", ("out_invoice", "out_refund")),
                     ("invoice_id.date_invoice", ">=", from_date),
                     ("company_id", "=", company_id),
                     ("invoice_line_tax_ids", "=", False)]
                )
            )

            print("Retrieving invoices")
            orders = []
            for line in lines:
                msg_burst("  ... %s" % line.name[:40])
                if line.invoice_id.id not in orders:
                    orders.append(line.invoice_id.id)

        print("Set invoices to draft")
        for invoice_id in orders:
            invoice = clodoo.browseL8(ctx, _AI, invoice_id)
            msg_burst("  ... %s" % invoice.number)
            if invoice.state != "draft":
                try:
                    clodoo.executeL8(
                        ctx, _AI, 'action_invoice_cancel', invoice_id)
                    clodoo.executeL8(
                        ctx, _AI, 'action_invoice_draft', invoice_id)
                except BaseException as e:
                    print("Invoice %s - error %s" % (invoice.number, e))
            if clodoo.browseL8(ctx, _AI, invoice_id).state != "draft":
                print(">>> Invoice %s: invalid state" % invoice.number)
            trace += "Fattura %s\n" % invoice.number

        print("Set invoice line with tax code")
        for line in lines:
            msg_burst("  ... %s" % line.name[:40])
            clodoo.writeL8(
                ctx, _AIL, line.id, {"invoice_line_tax_ids": [(6, 0, [tax_id])]})

        print("Set invoice to open")
        for invoice_id in orders:
            invoice = clodoo.browseL8(ctx, _AI, invoice_id)
            clodoo.executeL8(ctx, _AI, "compute_taxes", invoice.id)
            if to_send_mail:
                clodoo.writeL8(
                    ctx, _AI, invoice.id,{"to_send_mail": to_send_mail})
            if invoice.state == "draft":
                clodoo.executeL8(
                    ctx, _AI, "action_invoice_open", invoice.id)

        print("")
        print("")
        print("%s invoice updated" % len(orders))
        print("")
        print(trace)

    ###########################################################################
    if not ctx["action"] or "so_no_tax" in ctx["action"]:
        print("Searching for sale lines without tax code")
        trace = ""
        if ctx["order_list"]:
            lines = []
            orders = []
            for inv_num in ctx["order_list"].split(","):
                order_id = clodoo.searchL8(ctx, _SO, [("name", "=", inv_num)])
                if not order_id:
                    print("Invalid sale order %s" % inv_num)
                    return 1
                orders.append(order_id[0])
        else:
            lines = clodoo.browseL8(
                ctx, _SOL,
                clodoo.searchL8(
                    ctx, _SOL,
                    [("order_id.date_order", ">=", from_date),
                     ("company_id", "=", company_id),
                     ("tax_id", "=", False)]
                )
            )

            print("Retrieving orders")
            orders = []
            for line in lines:
                if line.order_id.id not in orders:
                    orders.append(line.order_id.id)

        for order_id in orders:
            order = clodoo.browseL8(ctx, _SO, order_id)
            trace += "Order %s\n" % order.name

        print("Set order line with tax code")
        for line in lines:
            clodoo.writeL8(ctx, _SOL, line.id, {"tax_id": [(6, 0, [tax_id])]})

        print("")
        print("")
        print("%s order updated" % len(orders))
        print("")
        print(trace)

    ###########################################################################
    if not ctx["action"] or "wrong_delivery" in ctx["action"]:
        print("Searching for sale with wrong delivery address")
        trace = ""
        if ctx["order_list"]:
            orders = []
            for inv_num in ctx["order_list"].split(","):
                order_id = clodoo.searchL8(ctx, _SO, [("name", "=", inv_num)])
                if not order_id:
                    print("Invalid sale order %s" % inv_num)
                    return 1
                orders.append(order_id[0])
        else:
            orders = clodoo.browseL8(
                ctx, _SO,
                clodoo.searchL8(
                    ctx, _SO,
                    [("partner_shipping_id.vg7_id", "<", 100000000),
                     ("company_id", "=", company_id),
                     ("date_order", ">=", from_date),]
                )
            )
        ctr = 0
        for order in orders:
            vg7_id = order.partner_shipping_id.vg7_id
            if vg7_id > 100000000 or order.partner_id == order.partner_shipping_id:
                continue
            ctr += 1
            vg7_id += 100000000
            partner_id = clodoo.searchL8(ctx, _RP, [("vg7_id", "=", vg7_id)])
            if partner_id:
                clodoo.writeL8(
                    ctx, _SO,  order.id, {"partner_shipping_id": partner_id[0]}
                )
                trace += "Order %s correct\n" % order.name
            else:
                clodoo.writeL8(
                    ctx, _SO,  order.id,
                    {"partner_shipping_id": order.partner_id.id}
                )
                trace += "Order %s forced\n" % order.name
        print("")
        print("")
        print("%s order updated" % ctr)
        print("")
        print(trace)

    ###########################################################################
    if not ctx["action"] or "equal_delivery" in ctx["action"]:
        print("Searching for sale with delivery address equal to partner")
        trace = ""
        if ctx["order_list"]:
            orders = []
            for inv_num in ctx["order_list"].split(","):
                order_id = clodoo.searchL8(ctx, _SO, [("name", "=", inv_num)])
                if not order_id:
                    print("Invalid sale order %s" % inv_num)
                    return 1
                orders.append(order_id[0])
        else:
            orders = clodoo.browseL8(
                ctx, _SO,
                clodoo.searchL8(
                    ctx, _SO,
                    [("partner_shipping_id.active", "=", False),
                     ("company_id", "=", company_id),
                     ("date_order", ">=", from_date),]
                )
            )
        ctr = 0
        for order in orders:
            ctr += 1
            clodoo.writeL8(
                ctx, _SO,  order.id,
                {"partner_shipping_id": order.partner_id.id}
            )
            trace += "Order %s forced\n" % order.name
        print("")
        print("")
        print("%s order updated" % ctr)
        print("")
        print(trace)

    ###########################################################################
    if not ctx["action"] or "unmatch_delivery_partner" in ctx["action"]:
        print("Searching for delivery partner unmatched with order")
        trace = ""
        ctr = 0
        if ctx["order_list"]:
            orders = []
            for inv_num in ctx["order_list"].split(","):
                order_id = clodoo.searchL8(ctx, _SO, [("name", "=", inv_num)])
                if not order_id:
                    print("Invalid sale order %s" % inv_num)
                    return 1
                orders.append(order_id[0])
        else:
            orders = clodoo.browseL8(
                ctx, _SO,
                clodoo.searchL8(
                    ctx, _SO,
                    [("company_id", "=", company_id),
                     ("date_order", ">=", from_date),]
                )
            )
        for order in orders:
            for picking in order.picking_ids:
                if picking.partner_id != order.partner_shipping_id:
                    clodoo.writeL8(
                        ctx, _SP, picking.id,
                        {"partner_id": order.partner_shipping_id.id})
                    trace += "Delivery %s\n" % picking.name
                    ctr += 1
                for move in picking.move_lines:
                    if move.partner_id != order.partner_shipping_id:
                        clodoo.writeL8(
                            ctx, _SM, move.id,
                            {"partner_id": order.partner_shipping_id.id})
                        trace += "Move %s\n" % move.name[:16]
                        ctr += 1
            for ddt in order.ddt_ids:
                if ddt.partner_shipping_id != order.partner_shipping_id:
                    clodoo.writeL8(
                        ctx, _DDT, ddt.id,
                        {"partner_shipping_id": order.partner_shipping_id.id})
                    trace += "DdT %s\n" % ddt.ddt_number
                    ctr += 1
        print("")
        print("")
        print("%s order updated" % ctr)
        print("")
        print(trace)

    ###########################################################################
    if "q2so" in ctx["action"]:
        print("Validate quotation")
        trace = ""
        ctr = 0

        if ctx["order_list"]:
            orders = []
            for inv_num in ctx["order_list"].split(","):
                order_id = clodoo.searchL8(ctx, _SO, [("name", "=", inv_num)])
                if not order_id:
                    print("Invalid sale order %s" % inv_num)
                    return 1
                orders.append(order_id[0])
        else:
            orders = clodoo.browseL8(
                ctx, _SO,
                clodoo.searchL8(
                    ctx, _SO,
                    [("state", "=", "draft"),
                     ("company_id", "=", company_id),
                     ("date_order", ">=", from_date),]
                )
            )
        for order in orders:
            if not order.order_line:
                try:
                    clodoo.executeL8(
                        ctx, "ir.model.synchro",
                        'trigger_one_record', "orders", "vg7", order.vg7_id)
                except BaseException as e:
                    print("Sale order %s - error %s" % (order.name, e))
                    continue
                order = clodoo.browseL8(ctx, _SO, order.id)
                if order.state == "sale":
                    trace += "Order %s\n" % order.name
                    ctr += 1
                    continue
            try:
                clodoo.executeL8(
                    ctx, _SO, 'action_confirm', order.id)
            except BaseException as e:
                print("Sale order %s - error %s" % (order.name, e))
            trace += "Order %s\n" % order.name
            ctr += 1

        print("")
        print("")
        print("%s order updated" % ctr)
        print("")
        print(trace)

    return 0



if __name__ == "__main__":
    exit(main())
