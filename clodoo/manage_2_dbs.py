#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# import oerplib
import clodoo
from z0lib import parseoptargs
# import pdb


__version__ = "0.1.1"


def get_inv_ids(ctx):
    user = clodoo.browseL8(ctx, 'res.users', ctx['user_id'])
    company_id = ctx.get('company_id', user.company_id.id)
    model = 'account.period'
    period_ids = clodoo.searchL8(ctx, model,
                                 [('date_start', '>=', '2017-01-01'),
                                  ('date_stop', '<=', '2017-12-31'),
                                  ('company_id', '=', company_id)])
    model = 'account.journal'
    journal_id = clodoo.searchL8(ctx, model,
                                 [('code', '=', 'EXJ'),
                                  ('company_id', '=', company_id)])[0]
    model = 'account.invoice'
    return clodoo.searchL8(ctx, model,
                           [('period_id', 'in', period_ids),
                            ('journal_id', '=', journal_id),
                            ('state', 'in', ['open', 'paid'])],
                           order='registration_date,number')


def next_ix(ctx, rec_ids):
    ix = -1
    if ctx['ix'] < len(rec_ids):
        ix = ctx['ix']
        ctx['ix'] += 1
    return ix


def get_id_n_number(ctx, rec_ids, ix):
    if ix < 0:
        return ix, '~'
    id = rec_ids[ix]
    return id, clodoo.browseL8(ctx, 'account.invoice', id).number


def merge_diff_inv(left_ctx, right_ctx):
    left_rec_ids = get_inv_ids(left_ctx)
    right_rec_ids = get_inv_ids(right_ctx)
    # pdb.set_trace()
    left_ctx['ix'] = 0
    right_ctx['ix'] = 0
    left_ix = next_ix(left_ctx, left_rec_ids)
    right_ix = next_ix(right_ctx, right_rec_ids)
    left_id, left_number = get_id_n_number(left_ctx, left_rec_ids, left_ix)
    right_id, right_number = get_id_n_number(right_ctx,
                                             right_rec_ids,
                                             right_ix)
    while left_ix >= 0 and right_ix >= 0:
        if left_number < right_number:
            print '  > Missing %s' % left_number
            left_ix = next_ix(left_ctx, left_rec_ids)
            left_id, left_number = get_id_n_number(left_ctx,
                                                   left_rec_ids,
                                                   left_ix)
        elif left_number > right_number:
            print '< Missing %s' % right_number
            right_ix = next_ix(right_ctx, right_rec_ids)
            right_id, right_number = get_id_n_number(right_ctx,
                                                     right_rec_ids, right_ix)
        else:
            if left_id != right_id:
                print 'Warning! %s(%d,%d)' % (left_number, left_id, right_id)
            left_ix = next_ix(left_ctx, left_rec_ids)
            left_id, left_number = get_id_n_number(left_ctx,
                                                   left_rec_ids,
                                                   left_ix)
            right_ix = next_ix(right_ctx, right_rec_ids)
            right_id, right_number = get_id_n_number(right_ctx,
                                                     right_rec_ids,
                                                     right_ix)


parser = parseoptargs("Manage 2 DBs",
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
right_oerp, uid, ctx = clodoo.oerp_set_env(ctx=right_ctx)
left_oerp, uid, ctx = clodoo.oerp_set_env(ctx=left_ctx)

# pdb.set_trace()
