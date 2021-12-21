#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

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
    import z0lib
import transodoo
# import pdb


__version__ = '0.3.55'

MAX_DEEP = 20
SYSTEM_MODEL_ROOT = [
    'base.config.',
    'base_import.',
    'base.language.',
    'base.module.',
    'base.setup.',
    'base.update.',
    'ir.actions.',
    'ir.exports.',
    'ir.model.',
    'ir.module.',
    'ir.qweb.',
    'report.',
    'res.config.',
    'web_editor.',
    'web_tour.',
    'workflow.',
]
SYSTEM_MODELS = [
    '_unknown',
    'base',
    # 'base.config.settings',
    'base_import',
    'change.password.wizard',
    'ir.autovacuum',
    'ir.config_parameter',
    'ir.exports',
    'ir.fields.converter',
    'ir.filters',
    'ir.http',
    'ir.logging',
    'ir.model',
    'ir.needaction_mixin',
    'ir.qweb',
    'ir.rule',
    'ir.translation',
    'ir.ui.menu',
    'ir.ui.view',
    'ir.values',
    'report',
    'res.config',
    'res.font',
    'res.request.link',
    'res.users.log',
    'web_tour',
    'workflow',
]
IGNORE_FIELDS = {
    'res.partner': ['message_follower_ids',
                    'rea_code',
                    'child_ids'],
}
MANDATORY_FIELDS = {
    'account.invoice': ['company_id'],
}
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def writelog(msg):
    print(msg)
    with open('./migrate_odoo.log', 'a') as fd:
        line = '%s,' % msg
        fd.write(line)


def manage_error():
    dummy = ''
    while dummy not in ('I', 'i', 'S', 's', 'D', 'd'):
        dummy = raw_input('(Ignore, Stop, Debug)? ')
        if not dummy:
            dummy = 'I'
        if dummy == 'S' or dummy == 's':
            sys.exit(1)
        if dummy == 'D' or dummy == 'd':
            import pdb              # pylint: disable=deprecated-module
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
            pass


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
        old_module = module_src.name
        module = transodoo.translate_from_to(src_ctx,
                                             'ir.module.module',
                                             old_module,
                                             src_ctx['oe_version'],
                                             dst_ctx['oe_version'],
                                             type='module')
        if module == old_module:
            module = transodoo.translate_from_to(src_ctx,
                                                 'ir.module.module',
                                                 old_module,
                                                 src_ctx['oe_version'],
                                                 dst_ctx['oe_version'],
                                                 type='merge')
        msg_burst('Analyzing module %s (%s)' % (module, old_module))
        if not clodoo.searchL8(dst_ctx, model,
                               [('name', '=', module),
                                ('state', '=', 'installed')]):
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
    keys = []
    for key in dst_ctx['_kl'].get(model) or primkey_table(src_ctx,
                                                          model):
        keys.append(key)
    keyval = clodoo.extract_vals_from_rec(src_ctx,
                                          model,
                                          rec,
                                          keys=keys, format='str')
    where = []
    for key in keyval:
        if keyval[key]:
            where.append((key, '=', keyval[key]))
    return where


def cvt_o2m_value(dst_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(dst_ctx, relation)
    if rel_mode == 'image':
        return value
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if value:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(src_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        clodoo.get_model_structure(dst_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        new_value = []
        if dst_ctx['_ml'].get(relation) != 'no':
            for id in value:
                if id in src_ctx['_CACHE'][model]:
                    if src_ctx['_CACHE'][model]:
                        new_value.append(src_ctx['_CACHE'][model][id])
                else:
                    rel_rec = clodoo.browseL8(src_ctx, relation, id)
                    where = set_where_from_keys(dst_ctx, src_ctx, relation,
                                                rel_rec)
                    ids = clodoo.searchL8(dst_ctx, relation, where)
                    if len(ids) > 1:
                        writelog('Wrong translation model %s id %d!' % (model,
                                                                        id))
                    if len(ids) >= 1:
                        new_value.append(ids[0])
                        src_ctx['_CACHE'][model][id] = ids[0]
                    elif not src_ctx.get('no_recurse'):
                        copy_record(dst_ctx, src_ctx,
                                    relation, rel_rec,
                                    mode=rel_mode)
                    else:
                        writelog('Model %s id %d does not exits!' % (model,
                                                                    id))
                        src_ctx['_CACHE'][model][id] = False
        value = new_value if new_value else False
    if format == 'cmd' and value:
        value = [(6, 0, value)]
    return value


def cvt_m2m_value(dst_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(dst_ctx, relation)
    if rel_mode == 'image':
        return value
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if value:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(src_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        clodoo.get_model_structure(dst_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        new_value = []
        if dst_ctx['_ml'].get(relation) != 'no':
            for id in value:
                if id in src_ctx['_CACHE'][model]:
                    if src_ctx['_CACHE'][model]:
                        new_value.append(src_ctx['_CACHE'][model][id])
                else:
                    rel_rec = clodoo.browseL8(src_ctx, relation, id)
                    where = set_where_from_keys(dst_ctx, src_ctx, relation,
                                                rel_rec)
                    ids = clodoo.searchL8(dst_ctx, relation, where)
                    if len(ids) > 1:
                        writelog('Wrong translation model %s id %d!' % (model,
                                                                        id))
                    if len(ids) >= 1:
                        new_value.append(ids[0])
                        src_ctx['_CACHE'][model][id] = ids[0]
                    elif not src_ctx.get('no_recurse'):
                        copy_record(dst_ctx, src_ctx,
                                    relation, rel_rec,
                                    mode=rel_mode)
                    else:
                        writelog('Model %s id %d does not exits!' % (model,
                                                                    id))
                        src_ctx['_CACHE'][model][id] = False
        value = new_value if new_value else False
    if format == 'cmd' and value:
        value = [(6, 0, value)]
    return value


def cvt_m2o_value(dst_ctx, src_ctx, model, name, id, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(dst_ctx, relation)
    if rel_mode == 'image':
        return id
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if id:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(src_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        clodoo.get_model_structure(dst_ctx, relation,
                                   ignore=IGNORE_FIELDS.get(relation, []))
        new_id = False
        if dst_ctx['_ml'].get(relation) != 'no':
            if id in src_ctx['_CACHE'][model]:
                if src_ctx['_CACHE'][model]:
                    new_id = src_ctx['_CACHE'][model][id]
            else:
                rel_rec = clodoo.browseL8(src_ctx, relation, id)
                where = set_where_from_keys(dst_ctx, src_ctx,
                                            relation, rel_rec)
                ids = clodoo.searchL8(dst_ctx, relation, where)
                if len(ids) > 1:
                    writelog('Wrong translation model %s id %d!' % (model,
                                                                    id))
                if len(ids) >= 1:
                    new_id = ids[0]
                    src_ctx['_CACHE'][model][id] = ids[0]
                elif not src_ctx.get('no_recurse'):
                    copy_record(dst_ctx, src_ctx,
                                relation, rel_rec,
                                mode=rel_mode)
                else:
                    writelog('Model %s id %d does not exits!' % (model,
                                                                id))
                    src_ctx['_CACHE'][model][id] = False
        id = new_id
    return id


def cvt_state_value(dst_ctx, src_ctx, model, name, value):
    if value == 'open':
        value = 'draft'
    elif value == 'paid':
        value = 'draft'
    pass


def load_record(dst_ctx, src_ctx, model, rec, mode=None):
    mode = mode or get_model_copy_mode(src_ctx, model)
    vals = clodoo.extract_vals_from_rec(src_ctx, model, rec, format='str')
    for nm in MANDATORY_FIELDS.get(model, []):
        if nm not in vals:
            vals[nm] = ''
    for name in vals:
        if src_ctx['STRUCT'][model][name]['ttype'] in ('one2many'):
            vals[name] = cvt_o2m_value(dst_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        elif src_ctx['STRUCT'][model][name]['ttype'] in ('many2many'):
            vals[name] = cvt_m2m_value(dst_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        elif src_ctx['STRUCT'][model][name]['ttype'] in ('many2one'):
            vals[name] = cvt_m2o_value(dst_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        elif name == 'state':
            vals[name] = cvt_state_value(dst_ctx, src_ctx, model, name,
                                         vals[name], format='cmd')
    vals = clodoo.cvt_from_ver_2_ver(dst_ctx,
                                     model,
                                     '7.0',
                                     dst_ctx['oe_version'],
                                     vals)
    return vals


def copy_record(dst_ctx, src_ctx, model, rec, mode=None):
    mode = mode or get_model_copy_mode(src_ctx, model)
    vals = load_record(dst_ctx, src_ctx, model, rec, mode=mode)
    if mode == 'image':
        ids = clodoo.searchL8(dst_ctx, model,
                              [('id', '=', rec.id)])
        if ids:
            write_no_dup(dst_ctx, model, ids, vals, rec.id)
        else:
            create_with_id(dst_ctx, model, rec.id, vals)
    elif dst_ctx['use_synchro'] and model in ('res.partner', ):
        clodoo.executeL8(dst_ctx,
                         model,
                         'synchro',
                         vals)
    else:
        where = set_where_from_keys(dst_ctx, src_ctx, model, rec)
        ids = clodoo.searchL8(dst_ctx, model,
                              where)
        if not ids and hasattr(rec, 'active'):
            where.append(('active','=',False))
            ids = clodoo.searchL8(dst_ctx, model,
                                  where)
        if len(ids) > 1:
            writelog('Wrong translation model %s id %d!' % (model,
                                                            rec.id))
        if len(ids) >= 1:
            write_no_dup(dst_ctx, model, ids, vals, rec.id)
        else:
            try:
                clodoo.createL8(dst_ctx, model, vals)
            except:
                writelog('Cannot create %s src id=%d' % (model, rec.id))
                manage_error()
                pass

def copy_table(dst_ctx, src_ctx, model, mode=None):
    clodoo.get_model_structure(src_ctx, model,
                               ignore=IGNORE_FIELDS.get(model, []))
    clodoo.get_model_structure(dst_ctx, model,
                               ignore=IGNORE_FIELDS.get(model, []))
    mode = mode or get_model_copy_mode(src_ctx, model)
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
                    # if not dst_ctx['assume_yes']:
                    #     dummy = raw_input('Press RET to continue')
    where = []
    for rec in clodoo.browseL8(src_ctx, model, clodoo.searchL8(
            src_ctx, model, where, order='id')):
        msg_burst('%s %d' % (model, rec.id))
        copy_record(dst_ctx, src_ctx, model, rec, mode=mode)


def is_system_model(model):
    is_system = False
    for root in SYSTEM_MODEL_ROOT:
        if model.startswith(root):
            is_system = True
            break
    if model in SYSTEM_MODELS:
        is_system = True
    return is_system


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
        if is_system_model(model):
            continue
        msg_burst('    get %s ...' % model)
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
        msg_burst('    crossdep %s ...' % model)
        for sub in models[model]['depends']:
            if model in models[sub]['depends']:
                models[model]['crossdep'] = sub
                models[sub]['crossdep'] = model
    for model in model_list:
        msg_burst('    dependencies %s ...' % model)
        models[model]['depends'] = list(set(models[model]['depends']) -
                                        set(models[model]['crossdep']))
    # missed_models = {}
    max_iter = 99
    parsing = True
    while parsing:
        parsing = False
        max_iter -= 1
        if max_iter <= 0:
            break
        for model in model_list:
            msg_burst('    sorting %s ...' % model)
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

PKEYS = {
    'res.country.state': ['country_id', 'code'],
    'res.partner': ['name', 'vat'],
    'res.company': ['vat'],
}
def primkey_table(ctx, model):
    clodoo.get_model_structure(ctx, model,
                               ignore=IGNORE_FIELDS.get(model, []))
    ir_model = 'ir.model.constraint'
    if model in PKEYS:
        names = PKEYS[model]
    else:
        names = []
        prior_name = ''
        for rec in clodoo.browseL8(ctx, ir_model,
            clodoo.searchL8(ctx, ir_model,
                [('model', '=', model), ('type', '=', 'u')], order='name')):
            name = rec.name
            if name == prior_name:
                continue
            prior_name = name
            if rec.name.startswith(model.replace('.', '_')):
                name = rec.name[len(model) + 1:]
                tok_id = ''
                for tok in name.split('_'):
                    if tok == 'id':
                        tok_id += '_id'
                        if tok_id in ctx['STRUCT'][model]:
                            names.append(tok_id)
                            tok_id = ''
                    elif tok in ctx['STRUCT'][model]:
                        names.append(tok)
                        tok_id = ''
                    else:
                        tok_id = tok
                break
    if not names:
        if clodoo.is_valid_field(ctx, model, 'company_id'):
            names = ['company_id']
        if clodoo.is_valid_field(ctx, model, 'code'):
            names.append('code')
        elif clodoo.is_valid_field(ctx, model, 'name'):
            names.append('name')
    return names


def write_tree_conf(ctx):
    print('Analizing source models ...')
    models = build_table_tree(ctx)
    with open(ctx['command_file'], 'w') as fd:
        for level in range(MAX_DEEP):
            for model in models:
                msg_burst('    keys %s ...' % model)
                names = primkey_table(ctx, model)
                if models[model].get('level', -1) == level:
                    fd.write('%d\t%s\tinquire\t%s\n' % (level,
                                                        model,
                                                        names))
        for model in models:
            msg_burst('    keys %s ...' % model)
            if models[model].get('level', -1) >= MAX_DEEP:
                names = primkey_table(ctx, model)
                fd.write('%d\t%s\tinquire\t%s\n' % (level,
                                                    model,
                                                    names))


def get_model_copy_mode(ctx, model):
    if is_system_model(model):
        return 'No'
    mode = ctx['_ml'][model] or 'inquire'
    if mode == 'inquire':
        mode_selection = {'i': 'image', 's': 'sql', 'n': 'no'}
        dummy = ''
        while not dummy:
            dummy = raw_input('Copy table %s (Image,Sql,No)? ' % model)
            if dummy and dummy[0].lower() in mode_selection:
                mode = mode_selection[dummy[0].lower()]
            else:
                dummy = ''
        ctx['_ml'][model] = mode
    return mode


parser = z0lib.parseoptargs("Manage 2 DBs",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--dst-config",
                    help="target DB configuration file",
                    dest="dst_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--dst-db_name",
                    help="Target database name",
                    dest="dst_db_name",
                    metavar="name",
                    default='demo')
parser.add_argument("-m", "--sel-model",
                    help="Model to migrate",
                    dest="sel_model",
                    metavar="name")
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument("-s", "--use-synchro",
                    action='store_true',
                    dest="use_synchro",
                    default=False)
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

src_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
dst_ctx = src_ctx.copy()
for param in ('db_name', 'conf_fn'):
    dst_ctx[param] = dst_ctx['dst_%s' % param]
    src_ctx[param] = src_ctx['src_%s' % param]
uid, src_ctx = clodoo.oerp_set_env(ctx=src_ctx)
uid, dst_ctx = clodoo.oerp_set_env(ctx=dst_ctx)
transodoo.read_stored_dict(src_ctx)
dst_ctx['mindroot'] = src_ctx['mindroot']
print("Manage 2 DBs - %s" % __version__)

with open('migrate_odoo.csv', 'r') as fd:
    dst_ctx['_ml'] = {}
    dst_ctx['_kl'] = {}
    dst_ctx['model_list'] = []
    for line in fd.read().split('\n'):
        line = line.strip()
        if line:
            lines = line.split('\t')
            level = lines[0]
            model = lines[1]
            mode = 'inquire' if len(lines[1]) <= 2 else lines[2]
            keys = 'name' if len(lines) <= 3 else eval(lines[3])
            dst_ctx['model_list'].append(model)
            dst_ctx['_ml'][model] = mode
            dst_ctx['_kl'][model] = keys
    fd.close()
assume_yes = 'Y'
if dst_ctx['sel_model']:
    dst_ctx['model_list'] = dst_ctx['sel_model'].split(',')

for model in dst_ctx['model_list']:
    clodoo.get_model_structure(src_ctx, model,
                               ignore=IGNORE_FIELDS.get(model, []))
    clodoo.get_model_structure(dst_ctx, model,
                               ignore=IGNORE_FIELDS.get(model, []))
    for rec in clodoo.browseL8(
        src_ctx, model, clodoo.searchL8(
            src_ctx, model, [], order='id')):
        msg_burst('%d, %s' % (rec.id, rec.name))
        vals = load_record(dst_ctx,
                           src_ctx,
                           model,
                           rec,
                           mode='cmd')
        clodoo.executeL8(dst_ctx,
                         model,
                         'synchro',
                         vals)
