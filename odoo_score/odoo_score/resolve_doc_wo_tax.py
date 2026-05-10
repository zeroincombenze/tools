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

    _AA = "account.account"
    _AFR = "account.full.reconcile"
    _APR = "account.partial.reconcile"
    _AI = "account.invoice"
    _AM = "account.move"
    _AML = "account.move.line"
    _AP = "account.payment"
    _AUR = "account.unreconcile"
    _RP = "res.partner"
    print("Searching for supplier")
    supplier_id = 4747
    payable_acc_id = 1010
    company_id = 3
    supplier = clodoo.browseL8(ctx, _RP, supplier_id)
    contacts_ids = clodoo.searchL8(ctx, _RP, [("parent_id", "=", supplier_id)])
    all_suppliers = contacts_ids + [supplier_id]
    print("Supplier = ", supplier_id, supplier.name)
    for id in all_suppliers:
        print("Contact: ", id, clodoo.browseL8(ctx, _RP, id).name)
    print("Payable Account = ", payable_acc_id, clodoo.browseL8(
        ctx, _AA, payable_acc_id).name)
    journals = clodoo.searchL8(
        ctx, "account.journal", [("type", "=", "purchase"),
                                 ("company_id", "=", company_id)]
    )
    print("Journal IDs = ", journals)

    print("Searching for supplier move lines")
    partner_line_ids = clodoo.searchL8(
        ctx,
        _AML,
        [
            ("account_id", "=", payable_acc_id),
            ("partner_id", "in", all_suppliers),
        ],
    )
    print('Partner line IDs = ', partner_line_ids)
    for line_id in partner_line_ids:
        line = clodoo.browseL8(ctx, _AML, line_id)
        for reconcile_id in [x.id for x in line.matched_credit_ids] + [
                x.id for x in line.matched_debit_ids]:
            clodoo.unlinkL8(ctx, _APR, reconcile_id)
        reconcile_id = clodoo.searchL8(
            ctx,
            _AFR,
            [
                ("reconciled_line_ids", "=", line_id),
            ],
        )
        if reconcile_id:
            move_line_ids = [
                x.id
                for x in clodoo.browseL8(ctx, _AFR, reconcile_id[0]).reconciled_line_ids
                if x.reconciled]
            for line_id in move_line_ids:
                line = clodoo.browseL8(ctx, _AML, line_id)
                invoice = clodoo.searchL8(
                    ctx, _AI, [("move_id", "=", line.move_id.id)])
                if invoice:
                    break
            try:
                context = {
                    "active_ids": move_line_ids,
                }
                if invoice:
                    context["invoice_id"] = invoice.id
                clodoo.executeL8(
                    ctx, _AUR, "trans_unrec", None, context
                )
            except BaseException:
                print("!!Moves %s unreconciliable!" % move_line_ids)

    print("Set all invoices to draft")
    invoice_ids = clodoo.searchL8(ctx, _AI,
                                  [("partner_id", "in", all_suppliers),
                                   ("journal_id", "in", journals)])
    for invoice_id in invoice_ids:
        invoice = clodoo.browseL8(ctx, _AI, invoice_id)
        if invoice.state != "draft":
            clodoo.executeL8(ctx, _AI, 'action_invoice_cancel', invoice_id)
            clodoo.executeL8(ctx, _AI, 'action_invoice_draft', invoice_id)
        if invoice.partner_id != supplier_id:
            clodoo.writeL8(ctx, _AI, invoice_id, {"partner_id": supplier_id})
        if clodoo.browseL8(ctx, _AI, invoice_id).state != "draft":
            print(">>> Invoice %s: invalid state" % invoice_id)

    print("Set all payments to draft")
    payment_ids = clodoo.searchL8(ctx, _AP, [("partner_id", "in", all_suppliers)])
    for payment_id in payment_ids:
        payment = clodoo.browseL8(ctx, _AP, payment_id)
        if payment.state != "draft":
            clodoo.executeL8(ctx, _AP, 'cancel', payment_id)
            if clodoo.browseL8(ctx, _AP, payment_id).state != "draft":
                print(">>> Payment %s: invalid state" % payment_id)
        if payment.partner_id != supplier_id:
            clodoo.writeL8(ctx, _AP, payment_id, {"partner_id": supplier_id})

    partner_line_ids = clodoo.searchL8(
        ctx,
        _AML,
        [
            ("account_id", "=", payable_acc_id),
            ("partner_id", "in", all_suppliers),
        ],
    )
    for line_id in partner_line_ids:
        line = clodoo.browseL8(ctx, _AML, line_id)
        move = clodoo.browseL8(ctx, _AM, line.move_id.id)
        if move.state != "draft":
            clodoo.executeL8(ctx, _AM, "button_cancel", move.id)

    print("Check for all draft invoices and payments")
    input("Press Enter to continue...")

    parsed_invoices = []
    while True:
        payment_ids = clodoo.searchL8(
            ctx, _AP,
            [("partner_id", "in", all_suppliers), ("state", "=", "draft")],
            order="payment_date")
        print("")
        invalid = False
        for payment_id in payment_ids:
            payment = clodoo.browseL8(ctx, _AP, payment_id)
            for invoice in payment.invoice_ids:
                if invoice.id in parsed_invoices:
                    print("Duplicate payment")
                    clodoo.writeL8(ctx, _AP, payment_id,
                                   {"invoice_ids": [(6, 0, [])]})
                    break
                parsed_invoices.append(invoice.id)
                print("Invoice %s, sts=%s, amt=%s, wht=%s, net_pay=%s"
                      % (invoice.id, invoice.state, invoice.amount_total,
                         invoice.withholding_tax_amount, invoice.amount_net_pay))
                pay_amount = invoice.amount_total - invoice.withholding_tax_amount
                if round(pay_amount, 2) == round(payment.amount, 2):
                    print("Pay for %s" % payment.amount)
                else:
                    print("*** Payment %s assigned=%s, due=%s ***"
                          % (payment.id, payment.amount, pay_amount))
                    invalid = True
                    clodoo.writeL8(ctx, _AP, payment_id, {"amount": pay_amount})
                clodoo.executeL8(ctx, _AI, "action_invoice_open", invoice.id)
                clodoo.executeL8(ctx, _AP, "post", payment_id)
        if not invalid:
            break
        print("Please correct payments")
        input("Press Enter to continue...")

    # import pdb; pdb.set_trace()
    print("Check for payments and invoices unreconciled")
    ctr = 2
    while ctr > 0:
        ctr -= 1
        payment_ids = clodoo.searchL8(
            ctx, _AP,
            [("partner_id", "in", all_suppliers), ("state", "=", "draft")],
            order="payment_date")
        for payment_id in payment_ids:
            invoice_ids = clodoo.searchL8(ctx, _AI,
                                          [("partner_id", "in", all_suppliers),
                                           ("journal_id", "in", journals),
                                           ("id", "not in", parsed_invoices),
                                           ("state", "!=", "paid")], order="date")
            if invoice_ids:
                invoice = clodoo.browseL8(ctx, _AI, invoice_ids[0])
                if invoice.state == "draft":
                    clodoo.executeL8(ctx, _AI, "action_invoice_open", invoice.id)
                pay_amount = invoice.amount_total - invoice.withholding_tax_amount
                clodoo.writeL8(ctx, _AP, payment_id, {
                    "invoice_ids": [(6, 0, [invoice_ids[0]])],
                    "amount": pay_amount,
                    # "partner_id": supplier_id,
                })
                parsed_invoices.append(invoice.id)
                clodoo.executeL8(ctx, _AP, "post", payment_id)


if __name__ == "__main__":
    exit(main())
