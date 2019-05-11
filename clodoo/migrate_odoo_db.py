#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import print_function

import sys
import os
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


__version__ = "0.3.8.19"
MAX_DEEP = 20
SYSTEM_MODELS = [
    '_unknown',
    'base inquire',
    'base_import.import',
    'base_import.tests.models.char.noreadonly',
    'base_import.tests.models.char.readonly',
    'base_import.tests.models.char.required',
    'base_import.tests.models.char.states',
    'base_import.tests.models.char.stillreadonly',
    'base_import.tests.models.char',
    'base_import.tests.models.m2o.related',
    'base_import.tests.models.m2o.required.related',
    'base_import.tests.models.m2o',
    'base_import.tests.models.o2m.child',
    'base_import.tests.models.o2m',
    'base_import.tests.models.preview',
    'base.language.export',
    'base.language.import',
    'base.language.install',
    'base.module.update',
    'base.update.translations',
    'base',
    'change.password.wizard',
    'ir.actions.act_url',
    'ir.actions.act_window_close',
    'ir.actions.actions',
    'ir.actions.client',
    'ir.actions.report.xml',
    'ir.autovacuum',
    'ir.config_parameter',
    'ir.exports',
    'ir.fields.converter',
    'ir.filters',
    'ir.http inquire',
    'ir.http',
    'ir.logging',
    'ir.model.data',
    'ir.model.fields',
    'ir.module.category',
    'ir.module.module',
    'ir.module.module.dependency',
    'ir.needaction_mixin',
    'ir.qweb',
    'ir.qweb.field.contact',
    'ir.qweb.field.date',
    'ir.qweb.field.datetime',
    'ir.qweb.field.duration',
    'ir.qweb.field.html',
    'ir.qweb.field.image',
    'ir.qweb.field.integer',
    'ir.qweb.field.many2one',
    'ir.qweb.field.monetary',
    'ir.qweb.field.qweb',
    'ir.qweb.field.text',
    'ir.qweb.field',
    'ir.translation',
    'ir.ui.menu',
    'ir.ui.view',
    'ir.values',
    'report.base.report_irmodulereference',
    'res.config.installer',
    'res.config.settings',
    'res.config',
    'res.font',
    'res.request.link',
    'res.users.log',
    'web_editor.converter.test',
    'web_editor.converter.test.sub',
    'web_tour.tour',
    'workflow',
    'workflow.instance',
]
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def writelog(msg):
    print(msg)
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
    keys = clodoo.extract_vals_from_rec(dst_ctx, model, rec,
                                        keys=keys, format='str')
    where = []
    for key in keys.keys():
        where.append((key, '=', keys[key]))
    return where


def cvt_value(dst_ctx, src_ctx, model, field2many, name, key, company_id):
    if not field2many:
        return False
    # if dst_ctx['_ml'].get(model, 'image') == 'image':
    #     return field2many
    where = set_where_from_keys(dst_ctx, src_ctx, model, field2many)
    if company_id:
        where.append(('company_id', '=', company_id))
    value = clodoo.searchL8(dst_ctx,
                            model,
                            where)
    if value:
        return value[0]
    writelog('Model %s key %s does not exist' % (
        model, where[0][2]))
    return False


def cvt_m2m_value(dst_ctx, src_ctx, model, rec, name, key, company_id):
    res = []
    for item in rec[name]:
        if key == 'id':
            keyval = item.id
        else:
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
    # if hasattr(rec, name):
    #     company_id = cvt_value(dst_ctx,
    #                            src_ctx,
    #                            'res.company',
    #                            rec,
    #                            name,
    #                            'vat',
    #                            False)
    #
    vals = clodoo.extract_vals_from_rec(src_ctx, model, rec, format='cmd')
    vals = clodoo.cvt_from_ver_2_ver(dst_ctx,
                                     model,
                                     src_ctx['oe_version'],
                                     dst_ctx['oe_version'],
                                     vals)
    # if company_id:
    #     vals[name] = company_id
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


def build_table_tree(ctx):
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
        if model in SYSTEM_MODELS:
            continue
        if model in ('base', 'base_import', 'report',
                     'web_tour',):
            continue
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


def primkey_table(ctx, model):
    names = []
    if model == 'res.country.state':
        names = 'country_id,code'
    elif clodoo.is_valid_field(ctx, model, 'code'):
        names = 'code'
    else:
        names = 'name'
    return names


def write_tree_conf(ctx):
    models = build_table_tree(ctx)
    with open(ctx['command_file'], 'w') as fd:
        for level in range(MAX_DEEP):
            for model in models:
                names = primkey_table(ctx, model)
                if models[model].get('level', -1) == level:
                    fd.write('%s inquire %s\n' % (model,
                                                  names))
        for model in models:
            if models[model].get('level', -1) >= MAX_DEEP:
                names = primkey_table(ctx, model)
                if models[model].get('level', -1) == level:
                    fd.write('%s inquire %s\n' % (model,
                                                  names))


parser = z0lib.parseoptargs("Migrate Odoo DB",
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
parser.add_argument("-m", "--sel-model",
                    help="Model to migrate",
                    dest="sel_model",
                    metavar="name")
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
if not dst_ctx['sel_model']:
    install_modules(dst_ctx, src_ctx)

if (dst_ctx['default_behavior'] or
        not os.path.isfile(dst_ctx['command_file'])):
    write_tree_conf(dst_ctx)
with open(dst_ctx['command_file'], 'r') as fd:
    dst_ctx['_ml'] = {}
    dst_ctx['_kl'] = {}
    dst_ctx['model_list'] = []
    for line in fd.read().split('\n'):
        line = line.strip()
        if line:
            lines = line.split(' ')
            model = lines[0]
            mode = 'inquire' if len(lines[0]) == 0 else lines[1]
            keys = 'name' if len(lines) <= 2 else lines[2]
            dst_ctx['model_list'].append(model)
            dst_ctx['_ml'][model] = mode
            dst_ctx['_kl'][model] = keys
    fd.close()
assume_yes = 'Y' if dst_ctx['assume_yes'] else 'Q'
mode_selection = {'i': 'image', 's': 'sql', 'n': ''}
if dst_ctx['sel_model']:
    dst_ctx['model_list'] = dst_ctx['sel_model'].split(',')
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
