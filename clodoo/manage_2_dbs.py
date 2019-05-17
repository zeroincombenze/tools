#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
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
import transodoo
# import pdb


__version__ = '0.3.8.21'

msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


def cvt_value(left_ctx, right_ctx, model, rec, name, key, company_id):
    if not getattr(rec, name):
        return False
    keyval = clodoo.browseL8(left_ctx,
                             model,
                             getattr(rec, name).id)[key]
    if model == 'account.account' and keyval == '152100':
        keyval = '150100'
    elif model == 'account.account' and keyval[0:3] == '510':
        keyval = '310100'
    elif model == 'account.journal' and keyval in ('SAJ', 'SCNJ'):
        keyval = 'FAT'
    where = [(key, '=', keyval)]
    if company_id:
        where.append(('company_id', '=', company_id))
    value = clodoo.searchL8(right_ctx,
                            model,
                            where)
    if value:
        return value[0]
    print 'Model %s key %s does not exist' % (
        model, keyval)
    return False


def cvt_m2m_value(left_ctx, right_ctx, model, rec, name, key, company_id):
    res = []
    for item in rec[name]:
        keyval = clodoo.browseL8(left_ctx,
                                 model,
                                 item.id)[key]
        where = [(key, '=', keyval)]
        if company_id:
            where.append(('company_id', '=', company_id))
        value = clodoo.searchL8(right_ctx,
                                model,
                                where)
        if value:
            res.append(value[0])
        else:
            print 'Model %s key %s does not exist' % (
                model, keyval)
            return []
    return [(6, 0, res)]


def copy_record(left_ctx, right_ctx, model, rec):
    name = 'company_id'
    company_id = cvt_value(left_ctx,
                           right_ctx,
                           'res.company',
                           rec,
                           name,
                           'vat',
                           False)

    vals = clodoo.extract_vals_from_rec(right_ctx, model, rec)
    vals[name] = company_id
    name = 'partner_id'
    vals[name] = cvt_value(left_ctx,
                           right_ctx,
                           'res.partner',
                           rec,
                           name, 
                           'vat',
                           False)
    name = 'account_id'
    vals[name] = cvt_value(left_ctx,
                           right_ctx,
                           'account.account',
                           rec,
                           name, 
                           'code',
                           company_id)
    if model == 'account.invoice':
        name = 'currency_id'
        vals[name] = cvt_value(left_ctx,
                               right_ctx,
                               'res.currency',
                               rec,
                               name, 
                               'name',
                               False)
        name = 'commercial_partner_id'
        vals[name] = cvt_value(left_ctx,
                               right_ctx,
                               'res.partner',
                               rec,
                               name, 
                               'vat',
                               False)
        name = 'journal_id'
        vals[name] = cvt_value(left_ctx,
                               right_ctx,
                               'account.journal',
                               rec,
                               name, 
                               'code',
                               company_id)
        name = 'state'
        if vals[name] == 'open':
            vals[name] = 'draft'
        vals['move_name'] = vals['internal_number']
        if 'internal_number' in vals:
            del vals['internal_number']
        vals['fiscal_position'] = False
    if model == 'account.invoice.line':
        name = 'product_id'
        vals[name] = cvt_value(left_ctx,
                               right_ctx,
                               'product.product',
                               rec,
                               name, 
                               'name',
                               False)
        if 'uos_id' in vals:
            name = 'uos_id'
            vals['uom_id'] = cvt_value(left_ctx,
                                       right_ctx,
                                       'product.uom',
                                       rec,
                                       name, 
                                       'name',
                                       False)
            del vals['uos_id']
        name = 'invoice_line_tax_id'
        vals['invoice_line_tax_ids'] = cvt_m2m_value(left_ctx,
                                                     right_ctx,
                                                     'account.tax',
                                                     rec,
                                                     name,
                                                     'description',
                                                     company_id)
        del vals['invoice_line_tax_id']
    return vals


parser = z0lib.parseoptargs("Manage 2 DBs",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--left-config",
                    help="configuration command file",
                    dest="left_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--left-db_name",
                    help="Database name",
                    dest="left_db_name",
                    metavar="name",
                    default='demo')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
parser.add_argument("-w", "--right-config",
                    help="configuration command file",
                    dest="right_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-x", "--right-db_name",
                    help="Database name",
                    dest="right_db_name",
                    metavar="name",
                    default='demo')

left_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
right_ctx = left_ctx.copy()
left_ctx['db_name'] = left_ctx['left_db_name']
left_ctx['conf_fn'] = left_ctx['left_conf_fn']
right_ctx['db_name'] = right_ctx['right_db_name']
right_ctx['conf_fn'] = right_ctx['right_conf_fn']
uid, right_ctx = clodoo.oerp_set_env(ctx=right_ctx)
uid, left_ctx = clodoo.oerp_set_env(ctx=left_ctx)
# transodoo.read_stored_dict(right_ctx)
# left_ctx['mindroot'] = right_ctx['mindroot']
print "Manage 2 DBs - %s" % __version__
while True:
    model = 'account.invoice'
    while model == '':
        msg = "Model to copy (type exit to exit)? "
        model = raw_input(msg)
    if model == 'exit':
        break
    left_id = 0
    while left_id == 0:
        msg = "Original ID to copy? "
        left_id = int(raw_input(msg))
    right_id = 0
    while right_id == 0:
        msg = "Target ID (-1 if new record)? "
        right_id = int(raw_input(msg))
    rec = clodoo.browseL8(left_ctx, model, left_id)
    vals = copy_record(left_ctx, right_ctx, model, rec)
    if right_id > 0:
        clodoo.writeL8(right_ctx, model, right_id, vals)
    else:
        right_id = clodoo.createL8(right_ctx, model, vals)
    model = 'account.invoice.line'
    clodoo.unlinkL8(right_ctx, model,
                    clodoo.searchL8(right_ctx, model,
                                    [('invoice_id', '=', right_id)]))
    for line in clodoo.browseL8(left_ctx, model,
            clodoo.searchL8(left_ctx, model, [('invoice_id', '=', left_id)])):
        vals = copy_record(left_ctx, right_ctx, model, line)
        vals['invoice_id'] = right_id
        clodoo.createL8(right_ctx, model, vals)
    model = 'account.invoice'
    clodoo.executeL8(right_ctx,
                     model,
                     'compute_taxes',
                     [right_id])
