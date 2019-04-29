#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
# import oerplib
import clodoo
try:
    from z0lib.z0lib import parseoptargs
except ImportError:
    from z0lib import parseoptargs
import transodoo
# import pdb


__version__ = "0.3.8.17"

msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


def writelog(msg):
    print msg
    fd = open('./migrate_odoo.log', 'a')
    line = '%s,' % msg


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
            writelog('Error writing record %d of %s' % (rec_id, model))
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
            writelog('Error creating record %d of %s' % (id, model))
            manage_error()
            new_id = id
    if new_id != id:
        writelog("Cannot create record %d of %s" % (id, model))
        if not ctx['assume_yes']:
            raw_input('Press RET to continue')
    if last_id and last_id > 1 and last_id > id:
        sql = 'alter sequence %s restart %d;' % (table, last_id)
        try:
            ctx['_cr'].execute(sql)
        except BaseException:
            pass

def install_modules(dst_ctx, src_ctx):
    assume_yes = dst_ctx['assume_yes']
    upgrade = False
    if not dst_ctx['assume_yes']:
        dummy = raw_input('Install modules (Yes,No,All)? ')
        if dummy[0] in ('n', 'N'):
            assume_yes = 'N'
        if dummy[0] in ('a', 'A'):
            assume_yes = 'Y'
        dummy = raw_input('Upgrade installed modules (Yes,No)? ')
        if dummy[0] in ('y', 'Y'):
            upgrade = True
        if assume_yes == 'N' and not upgrade:
            return
    model = 'ir.module.module'
    for module_src in clodoo.browseL8(src_ctx, model,
            clodoo.searchL8(src_ctx, model, [('state', '=', 'installed')])):
        module = module_src.name
        msg_burst('Analyzing module %s' % (module))
        if not clodoo.searchL8(dst_ctx, model,
                               [('name', '=', module),
                                ('state', '=', 'uninstalled')]):
            if assume_yes:
                writelog('Installing module %s' % module)
                dummy = 'Y'
            else:
                if not assume_yes:
                    dummy = raw_input(
                        'Install module %s (Yes,No,All,Quit)? ' % module)
            if dummy[0] in ('n', 'N'):
                continue
            if dummy[0] in ('q', 'Q'):
                return
            if dummy[0] in ('a', 'A'):
                assume_yes = 'Y'
            sts = clodoo.act_install_modules(dst_ctx, module_list=[module])
            if sts:
                id = clodoo.searchL8(dst_ctx, model,
                               [('name', '=', module)])
                if id:
                    clodoo.writeL8(dst_ctx, model, id, {'state': 'to install'})
                else:
                    vals = {
                        'name': module_src.name,
                        'author': module_src.author,
                        'demo': module_src.demo,
                        'description': module_src.description,
                        'summary': module_src.summary,
                        'state': 'to install'
                    }
                    clodoo.createL8(dst_ctx, model, vals)
        elif upgrade:
            if clodoo.searchL8(dst_ctx, model,
                               [('name', '=', module),
                                ('state', '=', 'installed')]):
                sts = clodoo.act_upgrade_modules(dst_ctx, module_list=[module])


def set_where_from_keys(dst_ctx, src_ctx, model, rec, keys=None):
    keys = keys or dst_ctx['_kl'][model].split(',')
    keys = clodoo.extract_vals_from_rec(dst_ctx, model, rec, keys=keys)
    where = []
    for key in keys.keys():
        where.append((key, '=', keys[key]))
    return where


def cvt_value(dst_ctx, src_ctx, model, field2many, name, key, company_id):
    if not field2many:
        return False
    if dst_ctx['_ml'].get(model, 'image') == 'image':
        return field2many
    rec = clodoo.browseL8(src_ctx, model, field2many.id)
    where = set_where_from_keys(dst_ctx, src_ctx, model, rec)
    if company_id:
        where.append(('company_id', '=', company_id))
    value = clodoo.searchL8(dst_ctx,
                            model,
                            where)
    if value:
        return value[0]
    writelog('Model %s key %s does not exist' % (
        model, keys[0]))
    return False


def cvt_m2m_value(dst_ctx, src_ctx, model, rec, name, key, company_id):
    res = []
    for item in rec[name]:
        keyval = clodoo.browseL8(src_ctx,
                                 model,
                                 item.id)[key]
        where = [(key, '=', keyval)]
        if company_id:
            where.append(('company_id', '=', company_id))
        value = clodoo.searchL8(dst_ctx,
                                model,
                                where)
        if value:
            res.append(value[0])
        else:
            writelog('Model %s key %s does not exist' % (
                model, keyval))
            return []
    return [(6, 0, res)]


def copy_record(dst_ctx, src_ctx, model, rec):
    company_id = False
    name = 'company_id'
    if hasattr(rec, name):
        company_id = cvt_value(dst_ctx,
                               src_ctx,
                               'res.company',
                               rec,
                               name,
                               'vat',
                               False)

    vals = clodoo.extract_vals_from_rec(src_ctx, model, rec)
    vals = clodoo.cvt_from_ver_2_ver(dst_ctx,
                                     model,
                                     src_ctx['oe_version'],
                                     dst_ctx['oe_version'],
                                     vals)
    if company_id:
        vals[name] = company_id
    for name, model2 in (('partner_id', 'res.partner'),
                         ('commercial_partner_id', 'res.partner')):
        if hasattr(rec, name):
            vals[name] = cvt_value(dst_ctx,
                                   src_ctx,
                                   model2,
                                   getattr(rec, name),
                                   name, 
                                   'vat',
                                   False)
    for name, model2 in (('account_id', 'account.account'),
                          ('journal_id', 'account.journal'),
                          ('country_id', 'res.country')):
        if hasattr(rec, name):
            vals[name] = cvt_value(dst_ctx,
                                   src_ctx,
                                   model2,
                                   getattr(rec, name),
                                   name, 
                                   'code',
                                   company_id)
    for name, model2 in (('currency_id', 'res.currency'),
                         ('product_id', 'product.product'),
                         ('uom_id', 'product.uom'),
                         ('uos_id', 'product.uom')):
        if hasattr(rec, name):
            vals[name] = cvt_value(dst_ctx,
                                   src_ctx,
                                   model2,
                                   getattr(rec, name),
                                   name, 
                                   'name',
                                   False)
    for name, model2 in (('invoice_line_tax_id', 'account.tax'),
                         ('invoice_line_tax_ids', 'account.tax')):
        if hasattr(rec, name):
            vals[name] = cvt_m2m_value(dst_ctx,
                                       src_ctx,
                                       model2,
                                       getattr(rec, name),
                                       name,
                                       'description',
                                       company_id)
    name = 'state'
    if hasattr(rec, name):
        if vals[name] == 'open':
            vals[name] = 'draft'
    return vals


def copy_table(dst_ctx, src_ctx, model, mode=None):
    import pdb
    pdb.set_trace()
    clodoo.declare_mandatory_fields(dst_ctx, model)
    if mode == 'image' and src_ctx['_cr']:
        table = model.replace('.', '_')
        sql = 'select max(id) from %s;' % table
        src_ctx['_cr'].execute(sql)
        rows = src_ctx['_cr'].fetchall()
        last_id = rows[0][0]
        if last_id > 0:
            for id in clodoo.searchL8(dst_ctx, model,
                                      [('id', '>', last_id)]):
                try:
                    clodoo.unlinkL8(dst_ctx, model, id)
                except BaseException:
                    writelog("Cannot delete record %d of %s" % (id, model))
                    if not dst_ctx['assume_yes']:
                        dummy = raw_input('Press RET to continue')
    where = []
    for rec in clodoo.browseL8(src_ctx, model, clodoo.searchL8(
            src_ctx, model, where, order='id')):
        msg_burst('%s %d' % (model, rec.id))
        vals = copy_record(dst_ctx, src_ctx, model, rec)
        if mode == 'image':
            ids = clodoo.searchL8(dst_ctx, model,
                                  [('id', '=', rec.id)])
            if ids:
                write_no_dup(dst_ctx, model, ids, vals, rec.id)
            else:
                create_with_id(dst_ctx, model, rec.id, vals)
        else:
            where = set_where_from_keys(dst_ctx, src_ctx, model, rec)
            ids = clodoo.searchL8(dst_ctx, model,
                                  where)
            if not ids and hasattr(rec, 'active'):
                where.append(('active','=',False))
                ids = clodoo.searchL8(dst_ctx, model,
                                      where)

            if ids:
                write_no_dup(dst_ctx, model, ids, vals, rec.id)
            else:
                try:
                    clodoo.createL8(dst_ctx, model, vals)
                except:
                    writelog('Cannot create %s src id=%d' % (model, rec.id))


parser = parseoptargs("Migrate Odoo DB",
                      "© 2019 by SHS-AV s.r.l.",
                      version=__version__)
parser.add_argument('-h')
parser.add_argument("-C", "--command-file",
                    help="migration command file",
                    dest="command_file",
                    metavar="file",
                    default='./migrate_odoo.conf')
parser.add_argument("-c", "--dst-config",
                    help="target DB configuration file",
                    dest="dst_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-D", "--default-behavior",
                    action="store_true",
                    dest="default_behavior")
parser.add_argument("-d", "--dst-db_name",
                    help="Target database name",
                    dest="dst_db_name",
                    metavar="name",
                    default='demo')
parser.add_argument("-I", "--inside-openupgrade",
                    action='store_true',
                    dest="inside_openupgrade",
                    default=False)
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
parser.add_argument("-w", "--src-config",
                    help="Source DB configuration file",
                    dest="src_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-x", "--src-db_name",
                    help="Source database name",
                    dest="src_db_name",
                    metavar="name",
                    default='demo')
parser.add_argument("-y", "--assume-yes",
                    action='store_true',
                    dest="assume_yes",
                    default=False)

dst_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
src_ctx = dst_ctx.copy()
dst_ctx['db_name'] = dst_ctx['dst_db_name']
dst_ctx['conf_fn'] = dst_ctx['dst_conf_fn']
src_ctx['db_name'] = src_ctx['src_db_name']
src_ctx['conf_fn'] = src_ctx['src_conf_fn']
uid, src_ctx = clodoo.oerp_set_env(ctx=src_ctx)
uid, dst_ctx = clodoo.oerp_set_env(ctx=dst_ctx)
transodoo.read_stored_dict(src_ctx)
dst_ctx['mindroot'] = src_ctx['mindroot']
install_modules(dst_ctx, src_ctx)
if dst_ctx['default_behavior'] or not os.path.isfile(dst_ctx['command_file']):
    with open(dst_ctx['command_file'], 'w') as fd:
        fd.write(r"""
res.currency sql name
res.country sql code
res.country.state sql country_id,code
res.city
res.partner.bank
account.fiscal.position
res.partner
res.company
account.account.type
account.account
product.uom.categ
product.uom
product.category
product.template
product.product
account.tax
account.journal
account.invoice
account.invoice.line
""")
with open(dst_ctx['command_file'], 'r') as fd:
    dst_ctx['_ml'] = {}
    dst_ctx['_kl'] = {}
    dst_ctx['model_list'] = []
    for line in fd.read().split('\n'):
        line = line.strip()
        if line:
            lines = line.split(' ')
            model = lines[0]
            if len(lines) > 1:
                mode = lines[1]
            else:
                mode = 'inquire'
            if len(lines) > 2:
                keys = lines[2]
            else:
                keys = 'name'
            dst_ctx['model_list'].append(model)
            dst_ctx['_ml'][model] = mode
            dst_ctx['_kl'][model] = keys
    fd.close()
    assume_yes = 'Y' if dst_ctx['assume_yes'] else 'Q'
    mode_selection = {'i': 'image', 's': 'sql', 'N': ''}
    for model in dst_ctx['model_list']:
        mode = dst_ctx['_ml'][model] or 'inquire'
        if assume_yes == 'Y':
            if mode == 'inquire':
                dummy = raw_input(
                    'Copy table %s (Image,Sql,No)? ' % model)
                mode = mode_selection[dummy.lower()]
            else:
                writelog('Copying table %s mode %s' % (model, mode))
        elif  assume_yes == 'N':
            continue
        else:
            if mode == 'inquire':
                dummy = raw_input(
                    'Copy table %s (Image,Sql,No)? ' % model)
                mode = mode_selection[dummy.lower()]
            else:
                dummy = raw_input(
                    'Copy table %s mode %s (Yes,No,All,Quit)? ' %
                        (model, mode))
                if dummy.lower() == 'q':
                    break
                elif dummy.lower() == 'n':
                    continue
                elif dummy.lower() == 'a':
                    assume_yes = 'Y'
        if not mode:
            continue
        copy_table(dst_ctx, src_ctx, model, mode=mode)

raw_input('Press RET to validate invoices ...')
ids = clodoo.searchL8(dst_ctx, 'account.invoice', [('state', '=', 'draft')])
clodoo.upd_invoices_2_posted(ids, dst_ctx)
