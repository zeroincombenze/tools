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
    import z0lib

# import pdb

__version__ = "0.0.3"


def wlog(txt):
    fd = open('./renum.log', 'a')
    fd.write('%s\n' % txt)
    fd.close()
    print '###### %s #####' % txt


def wchnum(id, old, new):
    fd = open('./renum.txt', 'a')
    fd.write('%s=%s\n' % (old, new))
    fd.close()
    print 'Processing id=%d, old_number=%s, new_number=%s' % (inv_id,
                                                              old_number,
                                                              number)


def get_inv_ids():
    company_id = 1
    model = 'account.period'
    period_ids = oerp.search(model, [('date_start', '>=', '2016-01-01'),
                                     ('date_stop', '<=', '2016-12-31'),
                                     ('company_id', '=', company_id)])
    model = 'account.journal'
    journal_id = oerp.search(model, [('code', '=', 'EXJ'),
                                     ('company_id', '=', company_id)])[0]
    model = 'account.invoice'
    return oerp.search(model,
                       [('period_id', 'in', period_ids),
                        ('journal_id', '=', journal_id),
                        ('state', 'in', ['open', 'paid'])],
                       order='registration_date,number')


parser = z0lib.parseoptargs("Renum Odoo DB",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--db_name",
                    help="Database name",
                    dest="db_name",
                    metavar="name",
                    default='lastyear')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')

ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
oerp, uid, ctx = clodoo.oerp_set_env(ctx=ctx)
print "Renum - %s" % __version__

rec_ids = get_inv_ids()
model = 'account.invoice'
old_recs = {}
for id in rec_ids:
    old_recs[id] = oerp.browse(model, id).number
# pdb.set_trace()

oerp, uid, ctx = clodoo.oerp_set_env()
rec_ids = get_inv_ids()
invoice_num = 0
for inv_id in rec_ids:
    if inv_id in old_recs:
        old_number = old_recs[inv_id]
    else:
        old_number = oerp.browse(model, inv_id).number
        i = int(old_number[9:13]) + 402
        old_number = 'EXJ/2016/%04d' % i
    move_dict = {}
    reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
        oerp, [inv_id], ctx)
    clodoo.unreconcile_invoices(oerp, reconcile_dict, ctx)
    invoice_num += 1
    number = 'EXJ/2016/%04d' % invoice_num
    wchnum(inv_id, old_number, number)
    try:
        clodoo.upd_invoices_2_draft(oerp, move_dict, ctx)
    except BaseException:
        wlog('Cannot set draft status '
             'inv_id=%d, old_number=%s, new_number=%s' % (
                 inv_id, old_number, number))
    try:
        oerp.write(model, [inv_id], {'internal_number': number})
    except BaseException:
        wlog('Cannot update number '
             'inv_id=%d, old_number=%s, new_number=%s' % (
                 inv_id, old_number, number))
    try:
        clodoo.upd_invoices_2_posted(oerp, move_dict, ctx)
    except BaseException:
        wlog('Cannot restore posted status '
             'inv_id=%d, old_number=%s, new_number=%s' % (
                 inv_id, old_number, number))
    reconciles = reconcile_dict[inv_id]
    if len(reconciles):
        try:
            cur_reconciles, cur_reconcile_dict = clodoo.\
                refresh_reconcile_from_inv(oerp, inv_id, reconciles, ctx)
            clodoo.reconcile_invoices(oerp, cur_reconcile_dict, ctx)
        except BaseException:
            wlog('Cannot reconcile inv_id=%d, old_number=%s, new_number=%s' % (
                inv_id, old_number, number))
    if oerp.browse(model, inv_id).number != number:
        wlog('Failed to renum id %d: expected %s found %s!' % (
            inv_id, number, oerp.browse(model, inv_id).number))
