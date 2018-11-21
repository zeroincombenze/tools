#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
# import oerplib
import clodoo
from z0lib import parseoptargs
import transodoo
# import pdb


__version__ = "0.1.1.1"

msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


def manage_error():
    dummy = ''
    while dummy not in ('I', 'i', 'S', 's', 'D', 'd'):
        dummy = raw_input('(Ignore, Stop, Debug)? ')
        if not dummy:
            dummy = 'I'
        if dummy == 'S' or dummy == 's':
            sys.exit(1)
        if dummy == 'D' or dummy == 'd':
            import pdb
            pdb.set_trace()


def set_tmp_keys(ctx, model, id, vals):
    try_again = False
    if 'code' in vals:
        vals['code'] = str(id)
        try_again = True
    if 'name' in vals:
        vals['name'] = 'ID=%d %s' % (id, vals['name'])
        try_again = True
    return try_again, vals


def drop_out_originals(ctx, model, id, vals):
    def drop_out_original_field(ctx, model, id, vals, name):
        do_ids = clodoo.searchL8(ctx, model,
                                 [(name, '=', vals[name])])
        if do_ids:
            for do_id in do_ids:
                if ctx['_cr']:
                    table = model.replace('.', '_')
                    sql = "update %s set %s='(id=%d) =>%d' where id=%d;" % (
                        table, name, do_id, id, do_id)
                    try:
                        ctx['_cr'].execute(sql)
                    except BaseException:
                        pass
                else:
                    try:
                        clodoo.writeL8(ctx, model, do_ids,
                                       {name: '(id=%d) =>%d' % (
                                           do_id, id)})
                    except BaseException:
                        pass
    if 'code' in vals:
        drop_out_original_field(ctx, model, id, vals, 'code')
    if 'name' in vals:
        drop_out_original_field(ctx, model, id, vals, 'name')


def write_no_dup(ctx, model, ids, vals, rec_id):
    try_again = False
    try:
        clodoo.writeL8(ctx, model, ids, vals)
    except BaseException:
        try_again = True
        drop_out_originals(ctx, model, ids[0], vals)
    if try_again:
        try:
            try_again = False
            clodoo.writeL8(ctx, model, ids, vals)
        except BaseException:
            try_again, vals = set_tmp_keys(ctx, model, ids[0], vals)
    if try_again:
        try:
            try_again = False
            clodoo.writeL8(ctx, model, ids, vals)
        except BaseException:
            print 'Error writing record %d of %s' % (rec_id, model)
            manage_error()


def create_with_id(ctx, model, id, vals):
    last_id = 0
    sql_last = ''
    sql_seq = ''
    if ctx['_cr']:
        table = '%s_id_seq' % model
        table = table.replace('.', '_')
        sql_last = 'select last_value from %s;' % table
        ctx['_cr'].execute(sql_last)
        rows = ctx['_cr'].fetchall()
        last_id = rows[0][0]
        if id > 0:
            sql_seq = 'alter sequence %s restart %d;' % (table, id)
            if last_id != id:
                ctx['_cr'].execute(sql_seq)
    try_again = False
    new_id = 0
    try:
        new_id = clodoo.createL8(ctx, model, vals)
    except BaseException:
        try_again = True
        drop_out_originals(ctx, model, id, vals)
    if try_again:
        try:
            try_again = False
            if sql_seq:
                ctx['_cr'].execute(sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except BaseException:
            try_again, vals = set_tmp_keys(ctx, model, id, vals)
    if try_again:
        try:
            try_again = False
            if sql_seq:
                ctx['_cr'].execute(sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except BaseException:
            if ctx['_cr']:
                try_again = True
                table = '%s' % model
                table = table.replace('.', '_')
                sql_del = 'delete from %s where id=%s;' % (table, id)
                try:
                    ctx['_cr'].execute(sql_del)
                except BaseException:
                    try_again = False
    if try_again:
        try:
            if sql_seq:
                ctx['_cr'].execute(sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except BaseException:
            print 'Error creating record %d of %s' % (id, model)
            manage_error()
            new_id = id
    if new_id != id:
        print "Cannot create record %d of %s" % (id, model)
        raw_input('Press RET to continue')
    if last_id and last_id > 1 and last_id > id:
        sql = 'alter sequence %s restart %d;' % (table, last_id)
        try:
            ctx['_cr'].execute(sql)
        except BaseException:
            pass


def copy_table(left_ctx, right_ctx, model):
    dummy = raw_input('Copy table %s (Y,n)? ' % model)
    if dummy == 'n' or dummy == 'N':
        return
    clodoo.declare_mandatory_fields(left_ctx, model)
    if right_ctx['_cr']:
        table = model.replace('.', '_')
        sql = 'select max(id) from %s;' % table
        right_ctx['_cr'].execute(sql)
        rows = right_ctx['_cr'].fetchall()
        last_id = rows[0][0]
        if last_id > 0:
            for id in clodoo.searchL8(left_ctx, model,
                                      [('id', '>', last_id)]):
                try:
                    clodoo.unlinkL8(left_ctx, model, id)
                except BaseException:
                    print "Cannot delete record %d of %s" % (id, model)
                    dummy = raw_input('Press RET to continue')
    where = []
    if model == 'res.lang':
        where = [('id', '>', 1)]
    elif model == 'res.partner':
        where = [('parent_id', '=', False)]
    for rec in clodoo.browseL8(right_ctx, model, clodoo.searchL8(
            right_ctx, model, where, order='id')):
        vals = clodoo.extract_vals_from_rec(right_ctx, model, rec)
        vals = clodoo.cvt_from_ver_2_ver(left_ctx,
                                         model,
                                         right_ctx['oe_version'],
                                         left_ctx['oe_version'],
                                         vals)
        msg_burst('%s %d' % (model, rec.id))
        ids = clodoo.searchL8(left_ctx, model,
                              [('id', '=', rec.id)])
        if ids:
            write_no_dup(left_ctx, model, ids, vals, rec.id)
        else:
            create_with_id(left_ctx, model, rec.id, vals)


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
uid, right_ctx = clodoo.oerp_set_env(ctx=right_ctx)
uid, left_ctx = clodoo.oerp_set_env(ctx=left_ctx)
transodoo.read_stored_dict(right_ctx)
left_ctx['mindroot'] = right_ctx['mindroot']

for model in ('res.country.state', 'res.city', 'res.partner.bank'):
    copy_table(left_ctx, right_ctx, model)
for model in ('account.fiscal.position', 'res.partner'):
    copy_table(left_ctx, right_ctx, model)
for model in ('res.company', 'account.account.type', 'account.account'):
    copy_table(left_ctx, right_ctx, model)
for model in ('product.uom.categ', 'product.uom', 'product.category'):
    copy_table(left_ctx, right_ctx, model)
for model in ('product.template', 'product.product', ):
    copy_table(left_ctx, right_ctx, model)
for model in ('account.tax', 'account.journal'):
    copy_table(left_ctx, right_ctx, model)
for model in ('account.invoice', 'account.invoice.line'):
    copy_table(left_ctx, right_ctx, model)

raw_input('Press RET to validate invoices ...')
ids = clodoo.searchL8(left_ctx, 'account.invoice', [('state', '=', 'draft')])
clodoo.upd_invoices_2_posted(ids, left_ctx)
