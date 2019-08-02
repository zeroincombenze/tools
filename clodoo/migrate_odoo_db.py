#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import print_function

import sys
import os
import time
import inspect
import contextlib
import shutil


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
# from odoo10_score import odoo_score
import transodoo
# import pdb


__version__ = "0.3.8.45"
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
    'res.partner': ['rea_code',
                    'child_ids',],
                    # 'commercial_partner_id'],
    'account.account': ['parent_id',
                        'parent_left',
                        'parent_right'],
    '*':  ['message_follower_ids',
           'message_ids',],

}
MANDATORY_FIELDS = {
    'account.invoice': ['company_id'],
}
PKEYS = {
    'res.country.state': ['country_id', 'code'],
    'res.partner': ['name', 'vat'],
    'res.company': ['vat'],
    'account.account.type': ['name'],
    'product.template': ['name', 'default_code'],
    'product.product': ['name', 'default_code'],
}
DET_FIELD = {
    'account.invoice': 'invoice_line',
    'sale.order': 'order_line',
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
    fd = open('./migrate_odoo.log', 'a')
    line = '%s,' % msg


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


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


def wep_fields(ctx, vals):
    for nm in ('create_date', 'create_uid', 'id',
               'message_channel_ids', 'message_follower_ids',
               'message_ids', 'message_is_follower',
               'message_last_post', 'message_needaction',
               'message_needaction_counter', 'message_unread',
               'message_unread_counter',
               'write_date', 'write_uid'):
        if nm in vals:
            del vals[nm]
    return vals


def write_no_dup(ctx, model, ids, vals, src_id):
    vals = wep_fields(ctx, vals)
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
            writelog('Error writing record %d of %s' % (src_id, model))
            manage_error()
            pass


def create_with_id(ctx, model, id, vals):
    vals = wep_fields(ctx, vals)
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
            if last_id != id:
                sql_seq = 'alter sequence %s restart %d;' % (table, id)
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

def install_modules(tgt_ctx, src_ctx):
    assume_yes = tgt_ctx['assume_yes']
    upgrade = False
    if not tgt_ctx['assume_yes']:
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
                                             tgt_ctx['oe_version'],
                                             type='module')
        if module == old_module:
            module = transodoo.translate_from_to(src_ctx,
                                                 'ir.module.module',
                                                 old_module,
                                                 src_ctx['oe_version'],
                                                 tgt_ctx['oe_version'],
                                                 type='merge')
        msg_burst('Analyzing module %s (%s)' % (module, old_module))
        if not clodoo.searchL8(tgt_ctx, model,
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
            sts = clodoo.act_install_modules(tgt_ctx, module_list=[module])
            if sts:
                id = clodoo.searchL8(tgt_ctx, model,
                               [('name', '=', module)])
                if id:
                    clodoo.writeL8(tgt_ctx, model, id, {'state': 'to install'})
                else:
                    vals = {
                        'name': module_src.name,
                        'author': module_src.author,
                        'demo': module_src.demo,
                        'description': module_src.description,
                        'summary': module_src.summary,
                        'state': 'to install'
                    }
                    clodoo.createL8(tgt_ctx, model, vals)
        elif upgrade:
            if clodoo.searchL8(tgt_ctx, model,
                               [('name', '=', module),
                                ('state', '=', 'installed')]):
                sts = clodoo.act_upgrade_modules(tgt_ctx, module_list=[module])


def set_where_from_keys(tgt_ctx, src_ctx, model, rec, keys=None):
    keys = []
    for key in tgt_ctx['_kl'].get(model) or primkey_table(src_ctx,
                                                          model):
        keys.append(key)
    keyval = clodoo.extract_vals_from_rec(src_ctx,
                                          model,
                                          rec,
                                          keys=keys, format='str')


    if (model == 'account.account.type' and
            keys[0] in ('user_type', 'user_type_id')):
        keyval = transodoo.translate_from_to(src_ctx,
                                             model,
                                             keys[0],
                                             src_ctx['oe_version'],
                                             tgt_ctx['oe_version'],
                                             type='value',
                                             fld_name='report_type')
    where = []
    for key in keyval:
        if keyval[key]:
            where.append((key, '=', keyval[key]))
    return where


def cvt_o2m_value(tgt_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(tgt_ctx, relation)
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if '_CACHE' not in tgt_ctx:
        tgt_ctx['_CACHE'] = {}
    if model not in tgt_ctx['_CACHE']:
        tgt_ctx['_CACHE'][model] = {}
    if value:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(
            src_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        clodoo.get_model_structure(
            tgt_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        new_value = []
        if tgt_ctx['_ml'].get(relation) != 'no':
            for id in value:
                if rel_mode == 'image':
                    ids = clodoo.searchL8(tgt_ctx, relation, [('id', '=', id)])
                    if ids:
                        new_value.append(id)
                elif id in src_ctx['_CACHE'][model]:
                    if src_ctx['_CACHE'][model]:
                        new_value.append(src_ctx['_CACHE'][model][id])
                else:
                    rel_rec = clodoo.browseL8(src_ctx, relation, id,
                                              context={'lang': 'en_US'})
                    where = set_where_from_keys(tgt_ctx, src_ctx, relation,
                                                rel_rec)
                    ids = clodoo.searchL8(tgt_ctx, relation, where)
                    if len(ids) > 1:
                        writelog('Too rel records of model %s id %d!' % (model,
                                                                         id))
                    if len(ids) >= 1:
                        new_value.append(ids[0])
                        src_ctx['_CACHE'][model][id] = ids[0]
                    elif not src_ctx.get('no_recurse'):
                        copy_record(tgt_ctx, src_ctx,
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


def cvt_m2m_value(tgt_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(tgt_ctx, relation)
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if '_CACHE' not in tgt_ctx:
        tgt_ctx['_CACHE'] = {}
    if model not in tgt_ctx['_CACHE']:
        tgt_ctx['_CACHE'][model] = {}
    if value:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(
            src_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        clodoo.get_model_structure(
            tgt_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        new_value = []
        if tgt_ctx['_ml'].get(relation) != 'no':
            for id in value:
                if rel_mode == 'image':
                    ids = clodoo.searchL8(tgt_ctx, relation, [('id', '=', id)])
                    if ids:
                        new_value.append(id)
                elif id in src_ctx['_CACHE'][model]:
                    if src_ctx['_CACHE'][model]:
                        new_value.append(src_ctx['_CACHE'][model][id])
                else:
                    rel_rec = clodoo.browseL8(src_ctx, relation, id,
                                              context={'lang': 'en_US'})
                    where = set_where_from_keys(tgt_ctx, src_ctx, relation,
                                                rel_rec)
                    ids = clodoo.searchL8(tgt_ctx, relation, where)
                    if len(ids) > 1:
                        writelog('Too rel records of model %s id %d!' % (model,
                                                                         id))
                    if len(ids) >= 1:
                        new_value.append(ids[0])
                        src_ctx['_CACHE'][model][id] = ids[0]
                    elif not src_ctx.get('no_recurse'):
                        copy_record(tgt_ctx, src_ctx,
                                    relation, rel_rec,
                                    mode=rel_mode)
                    else:
                        writelog('Rel model %s id %d does not exits!' % (model,
                                                                         id))
                        src_ctx['_CACHE'][model][id] = False
        value = new_value if new_value else False
    if not value and str(
        inspect.getmembers(
            value,inspect.isclass)[0][1]).startswith('<class'):
        value = False
    if format == 'cmd' and value:
        value = [(6, 0, value)]
    return value


def cvt_m2o_value(tgt_ctx, src_ctx, model, name, id, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    rel_mode = get_model_copy_mode(tgt_ctx, relation)
    if '_CACHE' not in src_ctx:
        src_ctx['_CACHE'] = {}
    if model not in src_ctx['_CACHE']:
        src_ctx['_CACHE'][model] = {}
    if '_CACHE' not in tgt_ctx:
        tgt_ctx['_CACHE'] = {}
    if model not in tgt_ctx['_CACHE']:
        tgt_ctx['_CACHE'][model] = {}
    if id:
        if not relation:
            raise RuntimeError('No relation for field %s of %s' % (name,
                                                                   model))
        clodoo.get_model_structure(
            src_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        clodoo.get_model_structure(
            tgt_ctx, relation,
            ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
        new_id = False
        if tgt_ctx['_ml'].get(relation) != 'no':
            if rel_mode == 'image':
                ids = clodoo.searchL8(tgt_ctx, relation, [('id', '=', id)])
                if ids:
                    new_id = id
            elif id in src_ctx['_CACHE'][model]:
                if src_ctx['_CACHE'][model]:
                    new_id = src_ctx['_CACHE'][model][id]
            else:
                rel_rec = clodoo.browseL8(src_ctx, relation, id,
                                          context={'lang': 'en_US'})
                where = set_where_from_keys(tgt_ctx, src_ctx,
                                            relation, rel_rec)
                ids = clodoo.searchL8(tgt_ctx, relation, where)
                if len(ids) > 1:
                    writelog('Too rel records of model %s id %d!' % (model,
                                                                     id))
                if len(ids) >= 1:
                    new_id = ids[0]
                    src_ctx['_CACHE'][model][id] = ids[0]
                elif not src_ctx.get('no_recurse'):
                    copy_record(tgt_ctx, src_ctx,
                                relation, rel_rec,
                                mode=rel_mode)
                else:
                    writelog('Model %s id %d does not exits!' % (model,
                                                                id))
                    src_ctx['_CACHE'][model][id] = False
        id = new_id
    return id


def load_record(tgt_ctx, src_ctx, model, rec, mode=None):
    mode = mode or get_model_copy_mode(src_ctx, model)
    vals = clodoo.extract_vals_from_rec(src_ctx, model, rec, format='str')
    for nm in MANDATORY_FIELDS.get(model, []):
        if nm not in vals:
            vals[nm] = ''
    for name in vals.copy():
        if src_ctx['STRUCT'][model][name]['ttype'] in ('one2many'):
            vals[name] = cvt_o2m_value(tgt_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        elif src_ctx['STRUCT'][model][name]['ttype'] in ('many2many'):
            vals[name] = cvt_m2m_value(tgt_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        elif src_ctx['STRUCT'][model][name]['ttype'] in ('many2one'):
            vals[name] = cvt_m2o_value(tgt_ctx, src_ctx, model, name,
                                       vals[name], format='cmd')
        if (vals[name] is False and
                src_ctx['STRUCT'][model][name]['ttype'] != 'boolean'):
            del vals[name]
    vals = clodoo.cvt_from_ver_2_ver(tgt_ctx,
                                     model,
                                     src_ctx['oe_version'],
                                     tgt_ctx['oe_version'],
                                     vals)
    return vals


def use_synchro(tgt_ctx, model):
    if tgt_ctx['use_synchro'] and model in ('res.country',
                                            'res.partner',
                                            'account.account',
                                            'account.account.type',
                                            'account.invoice',
                                            'account.invoice.line',
                                            'account.tax',
                                            'product.template',
                                            'product.product',
                                            'sale.order',
                                            'sale.order.line'):
        return True
    return False


def set_actual_state(model, id, state):
    if model == 'account.invoice':
        if id:
            rec = clodoo.browseL8(tgt_ctx, model, id)
            if state == 'draft':
                action = ''
                return rec.id
            elif rec.state != 'draft':
                return -4
            elif rec.original_state == 'open':
                rec.action_invoice_open()
            elif rec.original_state == 'cancel':
                rec.action_invoice_cancel()
    elif model == 'sale.order':
        if id:
            rec = clodoo.browseL8(tgt_ctx, model, id)
            rec._compute_tax_id()
            if rec.state == rec.original_state:
                return rec.id
            elif rec.state != 'draft':
                return -4
            elif rec.original_state == 'sale':
                rec.action_confirm()
            elif rec.original_state == 'cancel':
                rec.action_cancel()
    return rec.id


def set_state_to_draft(tgt_ctx, model, ids, vals):
    if not ids:
        rec = False
        tgt_ctx['_COMMIT'][model] = {'id': False}
    else:
        id = ids[0]
        rec = clodoo.browseL8(tgt_ctx, model, id)
        tgt_ctx['_COMMIT'][model] = {'id': id}
    if 'state' in vals:
        tgt_ctx['_COMMIT'][model]['state'] = vals['state']
    elif rec:
        tgt_ctx['_COMMIT'][model]['state'] = rec.state
    if model == 'account.invoice':
        if rec:
            if rec.state == 'paid':
                return vals, -4
            elif rec.state == 'open':
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_invoice_cancel',
                                      ids)
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_invoice_draft',
                                      ids)
            elif rec.state == 'cancel':
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_invoice_draft',
                                      ids)
        vals['state'] = 'draft'
    elif model == 'sale.order':
        if rec:
            if rec.state == 'done':
                return vals, -4
            elif rec.state == 'sale':
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_cancel',
                                      ids)
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_draft',
                                      ids)
            elif rec.state == 'cancel':
                id = clodoo.executeL8(tgt_ctx,
                                      model,
                                      'action_draft',
                                      ids)
        vals['state'] = 'draft'
    return vals, 0


def commit_table(tgt_ctx, src_ctx, model):
    if tgt_ctx['_COMMIT'].get(model):
        id = tgt_ctx['_COMMIT'][model]['id']
        if use_synchro(tgt_ctx, model):
            id = clodoo.executeL8(tgt_ctx,
                                  model,
                                  'commit',
                                  id)
        else:
            set_actual_state(model, id, tgt_ctx['_COMMIT'][model]['state'])
    tgt_ctx['_COMMIT'][model] = False
    return id


def copy_record(tgt_ctx, src_ctx, model, rec, mode=None):
    msg_burst('%s %d' % (model, rec.id))
    mode = mode or get_model_copy_mode(src_ctx, model)
    # Avoid loop nesting
    src_ctx['_CACHE'] = src_ctx.get('_CACHE', {})
    src_ctx['_CACHE'][model] = src_ctx['_CACHE'].get(model, {})
    tgt_ctx['_CACHE'] = tgt_ctx.get('_CACHE', {})
    tgt_ctx['_CACHE'][model] = tgt_ctx['_CACHE'].get(model, {})
    tgt_ctx['_COMMIT'][model] = False
    if rec.id in src_ctx['_CACHE'][model]:
        return
    src_ctx['_CACHE'][model][rec.id] = False
    vals = load_record(tgt_ctx, src_ctx, model, rec, mode=mode)
    if model == 'account.account.type':
        if 'type' in vals and vals.get('type'):
            vals['type'] = transodoo.translate_from_to(src_ctx,
                                                       model,
                                                       vals['type'],
                                                       src_ctx['oe_version'],
                                                       tgt_ctx['oe_version'],
                                                       type='value',
                                                       fld_name='report_type')
    elif model == 'account.account':
        if vals.get('child_id'):
            return
        if 'user_type_id' in vals and vals.get('use_type_id'):
            vals['user_type_id'] = transodoo.translate_from_to(
                src_ctx,
                model,
                vals['user_type_id'],
                src_ctx['oe_version'],
                tgt_ctx['oe_version'],
                type='value',
                fld_name='report_type')
    elif model == 'account.tax':
        if 'amount' in vals and vals.get('amount'):
            vals['amount'] = transodoo.translate_from_to(src_ctx,
                                                         model,
                                                         vals['amount'],
                                                         src_ctx['oe_version'],
                                                         tgt_ctx['oe_version'],
                                                         type='value',
                                                         fld_name='amount')
    if mode == 'image':
        ids = clodoo.searchL8(tgt_ctx, model,
                              [('id', '=', rec.id)])
        if ids:
            write_no_dup(tgt_ctx, model, ids, vals, rec.id)
        else:
            id = create_with_id(tgt_ctx, model, rec.id, vals)
    elif use_synchro(tgt_ctx, model):
        vals['oe7_id'] = rec.id
        id = clodoo.executeL8(tgt_ctx,
                              model,
                              'synchro',
                              vals)
    else:
        where = set_where_from_keys(tgt_ctx, src_ctx, model, rec)
        ids = clodoo.searchL8(tgt_ctx, model,
                              where)
        if not ids and hasattr(rec, 'active'):
            where.append(('active','=',False))
            ids = clodoo.searchL8(tgt_ctx, model,
                                  where)
        if len(ids) > 1:
            writelog('Multiple translations model %s id %d!' % (model,
                                                                rec.id))
        if len(ids) >= 1:
            ids = [ids[0]]
            vals, id = set_state_to_draft(tgt_ctx, model, ids, vals)
            write_no_dup(tgt_ctx, model, ids, vals, rec.id)
            src_ctx['_CACHE'][model][rec.id] = ids[0]
        else:
            try:
                vals, id = set_state_to_draft(tgt_ctx, model, False, vals)
                id = clodoo.createL8(tgt_ctx, model, vals)
                src_ctx['_CACHE'][model][rec.id] = id
                tgt_ctx['_COMMIT'][model]['id'] = id
            except:
                writelog('Cannot create %s src id=%d' % (model, rec.id))
                manage_error()
                pass


def detail_model(model):
    if model in ('account.invoice', 'sale.order'):
        return '%s.line' % model
    return False


def set_where_from_txtids(value):
    where = []
    if value:
        ids = eval(value)
        if isinstance(ids, (int, long)):
            where.append(('id', '=', ids))
        else:
            where.append(('id', 'in', ids))
    return where


def copy_table(tgt_ctx, src_ctx, model, mode=None):
    clodoo.get_model_structure(
        src_ctx, model,
        ignore=IGNORE_FIELDS.get(model, []) + IGNORE_FIELDS['*'])
    clodoo.get_model_structure(
        tgt_ctx, model,
        ignore=IGNORE_FIELDS.get(model, []) + IGNORE_FIELDS['*'])
    det_model = detail_model(model)
    if det_model:
        clodoo.get_model_structure(
            src_ctx, det_model,
            ignore=IGNORE_FIELDS.get(det_model, []) + IGNORE_FIELDS['*'])
        clodoo.get_model_structure(
            tgt_ctx, det_model,
            ignore=IGNORE_FIELDS.get(det_model, []) + IGNORE_FIELDS['*'])
    tgt_ctx['_COMMIT'] = {}

    mode = mode or get_model_copy_mode(src_ctx, model)
    if mode == 'image' and src_ctx['_cr']:
        table = model.replace('.', '_')
        sql = 'select max(id) from %s;' % table
        src_ctx['_cr'].execute(sql)
        rows = src_ctx['_cr'].fetchall()
        last_id = rows[0][0]
        if last_id > 0:
            for id in clodoo.searchL8(tgt_ctx, model,
                                      [('id', '>', last_id)]):
                try:
                    clodoo.unlinkL8(tgt_ctx, model, id)
                except BaseException:
                    writelog("Cannot delete record %d of %s" % (id, model))
                    if not tgt_ctx['assume_yes']:
                        dummy = raw_input('Press RET to continue')
    where = set_where_from_txtids(src_ctx['sel_ids'])
    for rec in clodoo.browseL8(
        src_ctx, model, clodoo.searchL8(
            src_ctx, model, where, order='id'), context={'lang': 'en_US'}):
        copy_record(tgt_ctx, src_ctx, model, rec, mode=mode)
        if det_model:
            det_field = transodoo.translate_from_to(src_ctx,
                                                    model,
                                                    DET_FIELD[model],
                                                    '7.0',
                                                    src_ctx['oe_version'],
                                                    type='field')
            for det_rec in rec[det_field]:
                copy_record(tgt_ctx, src_ctx, det_model, det_rec, mode=mode)
    if det_model:
        commit_table(tgt_ctx, src_ctx, model)


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


def primkey_table(ctx, model):
    clodoo.get_model_structure(
        ctx, model,
        ignore=IGNORE_FIELDS.get(model, []) + IGNORE_FIELDS['*'])
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
    mode = ctx['_ml'].get(model) or 'inquire'
    if ctx['image_mode']:
        mode = 'image'
    elif model in ('account.account',
                   'account.account.type',
                   'account.tax',
                   'product.product',
                   'res.partner'):
        mode = 'sql'
    if mode == 'inquire':
        mode_selection = {'i': 'image', 's': 'sql', 'n': 'no'}
        dummy = ''
        while not dummy:
            if tgt_ctx['sel_model']:
                if model in tgt_ctx['sel_model']:
                    dummy = 'S'
                else:
                    dummy = 'N'
            else:
                dummy = raw_input('Copy table %s (Image,Sql,No)? ' % model)
            if dummy and dummy[0].lower() in mode_selection:
                mode = mode_selection[dummy[0].lower()]
            else:
                dummy = ''
        ctx['_ml'][model] = mode
    return mode


def migrate_1_table(src_ctx, tgt_ctx):
    uid, src_ctx = clodoo.oerp_set_env(ctx=src_ctx)
    uid, tgt_ctx = clodoo.oerp_set_env(ctx=tgt_ctx)
    transodoo.read_stored_dict(src_ctx)
    tgt_ctx['mindroot'] = src_ctx['mindroot']
    if not tgt_ctx['sel_model']:
        install_modules(tgt_ctx, src_ctx)

    if (src_ctx['default_behavior'] or
            not os.path.isfile(src_ctx['command_file'])):
        write_tree_conf(src_ctx)

    with open(tgt_ctx['command_file'], 'r') as fd:
        tgt_ctx['_ml'] = {}
        tgt_ctx['_kl'] = {}
        tgt_ctx['model_list'] = []
        for line in fd.read().split('\n'):
            line = line.strip()
            if line:
                lines = line.split('\t')
                level = lines[0]
                model = lines[1]
                mode = 'inquire' if len(lines[1]) <= 2 else lines[2]
                keys = 'name' if len(lines) <= 3 else eval(lines[3])
                tgt_ctx['model_list'].append(model)
                tgt_ctx['_ml'][model] = mode
                tgt_ctx['_kl'][model] = keys
        fd.close()
    assume_yes = 'Y' if tgt_ctx['assume_yes'] else 'Q'
    if tgt_ctx['sel_model']:
        tgt_ctx['model_list'] = tgt_ctx['sel_model'].split(',')
    for model in tgt_ctx['model_list']:
        mode = get_model_copy_mode(tgt_ctx, model)
        if mode not in ('sql', 'image'):
            continue
        copy_table(tgt_ctx, src_ctx, model, mode=mode)


def migrate_database_pass(src_ctx, tgt_ctx, phase=None):
    phase = phase or 1
    if phase == 1:
        saved_dry_run = src_ctx['dry_run']
        src_ctx['dry_run'] = True
        tgt_ctx['dry_run'] = src_ctx['dry_run']
    src_vid = src_ctx['opt_from']
    src_odoo_fver = src_ctx['src_odoo_fver']
    src_odoo_ver = src_ctx['src_odoo_ver']
    src_db = src_ctx['src_db_name']
    if src_ctx['src_conf_fn']:
        confn = src_ctx['src_conf_fn']
    elif src_ctx['tgt_conf_fn']:
        confn = src_ctx['tgt_conf_fn']
    else:
        confn = clodoo.build_odoo_param('CONFN', odoo_vid=src_vid, multi=True)
    while 1:
        tgt_odoo_ver = src_odoo_ver + 1
        tgt_odoo_fver = src_odoo_fver.replace(str(src_odoo_ver),
                                              str(tgt_odoo_ver))
        tgt_vid = src_vid.replace(str(src_odoo_ver), str(tgt_odoo_ver))
        if tgt_vid.startswith('v'):
            tgt_vid = tgt_odoo_fver
        src_user = clodoo.build_odoo_param(
            'USER', odoo_vid=src_vid, multi=True)
        tgt_user = clodoo.build_odoo_param(
            'USER', odoo_vid=tgt_vid, multi=True)
        if src_vid != src_ctx['opt_from']:
            confn = clodoo.build_odoo_param(
                'CONFN', odoo_vid=src_vid, multi=True)
        lconf = clodoo.build_odoo_param(
            'LCONFN', odoo_vid=src_vid, multi=True)
        odoo_bin = clodoo.build_odoo_param(
            'BIN', odoo_vid=src_vid, multi=True)
        if tgt_odoo_ver == src_ctx['final_ver']:
            tgt_db = src_ctx['tgt_db_name']
        else:
            tgt_db = '%s_migrated' % src_db
        print('Pass %d: migration from db %s (%s) to %s (%s) ..' %
              (phase, src_db, src_vid, tgt_db, tgt_vid))
        if not os.path.isfile(confn):
            raise IOError('File %s not found' % confn)
        if phase > 1:
            load_openupgrade(src_ctx, tgt_odoo_fver)
            add_versioned_tnl(src_ctx, src_odoo_fver, tgt_odoo_fver)

        if src_user != tgt_user:
            cmd = 'reassign_owner %s %s %s' % (tgt_db, src_user, tgt_user)

        if tgt_odoo_ver >= src_ctx['final_ver']:
            break
        src_vid = tgt_vid
        src_odoo_fver = tgt_odoo_fver
        src_odoo_ver = tgt_odoo_ver
        src_db = tgt_db

    if phase == 1:
        src_ctx['dry_run'] = saved_dry_run 
        tgt_ctx['dry_run'] = src_ctx['dry_run']


def migrate_database(src_ctx, tgt_ctx):
    migrate_database_pass(src_ctx, tgt_ctx, phase=1)
    migrate_database_pass(src_ctx, tgt_ctx, phase=2)


def check_conf(confn, param):
    fd = open(confn, 'rU')
    lines = fd.read().split('\n')
    value = False
    for line in lines:
        tkn = line.split('=')
        tkn = map(lambda x: x.strip(), tkn)
        if tkn[0] == param:
            value = tkn[1]
            break
    fd.close()
    return value

def load_openupgrade(ctx, odoo_fver):
    ou_ver = ''
    oupath_parentdir = os.path.dirname(ctx['opt_oupath'])
    oupath_scriptdir = os.path.join(ctx['opt_oupath'], 'scripts')
    oupath_script = os.path.join(ctx['opt_oupath'], 'scripts', 'migrate.py')
    oupath_bindir9 = os.path.join(ctx['opt_oupath'], 'openerp')
    oupath_release9 = os.path.join(oupath_bindir9, 'release.py')
    oupath_bindir10 = os.path.join(ctx['opt_oupath'], 'odoo')
    oupath_release10 = os.path.join(oupath_bindir10, 'release.py')
    ou_git = 'https://github.com/OCA/openupgrade.git'

    def get_ou_release(oupath_bindir):
        with pushd(oupath_bindir):
            sys.path.insert(0, '')
            import release
            ou_ver = release.version
            del sys.path[0]
        return ou_ver

    if os.path.isdir(oupath_scriptdir):
        if os.path.isfile(oupath_release10):
            ou_ver = get_ou_release(oupath_bindir10)
        elif os.path.isfile(oupath_release9):
            ou_ver = get_ou_release(oupath_bindir9)
    if ou_ver != odoo_fver:
        with pushd(oupath_parentdir):
            if os.path.isdir(ctx['opt_oupath']):
                shutil.rmtree(ctx['opt_oupath'])
            cmd = 'git clone %s %s -b %s --depth 1' % (
                ou_git, 
                'openupgrade',
                odoo_fver)
            os.system(cmd)
    if (not os.path.isdir(ctx['opt_oupath']) or
            not os.path.isfile(oupath_script)):
        raise IOError('Package openupgrade not found!')


def add_tnl_item(ctx, model, module, new_module, src_fver, tgt_fver,
                 type=False):
    VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0')
    tnl = transodoo.translate_from_to(ctx, model, module, src_fver, tgt_fver,
                                      type=type)
    if tnl != new_module:
        ver_names = {}
        name = module
        for ver in VERSIONS:
            if ver == '$tgt_fver':
                name = new_module
            ver_names[ver] = name
        uname = transodoo.set_uname(type, name,
                                    [ver_names[x] for x in VERSIONS])
        for ver in VERSIONS:
            ctx['mindroot']  = transodoo.link_versioned_name(
                ctx['mindroot'],
                model,
                uname,
                type,
                ver_names[ver],
                ver)
    return ctx


def add_versioned_tnl(ctx, src_fver, tgt_fver):
    with pushd(ctx['opt_oupath']):
        sys.path.append('')
        sys.path.append(os.path.dirname(__file__))
        import transodoo
        import openerp.addons.openupgrade_records.lib.apriori as apriori
        transodoo.read_stored_dict(ctx)
        model = 'ir.module.module'
        if hasattr(apriori, 'renamed_modules'):
            typ = 'module'
            for module in apriori.renamed_modules:
                new_module = apriori.renamed_modules[module]
                ctx = add_tnl_item(ctx, model, module, new_module,
                                   src_fver, tgt_fver, type=typ)
        if hasattr(apriori, 'merged_modules'):
            typ = 'merge'
            for item in apriori.merged_modules:
                module = item[0]
                new_module = item[1]
                ctx = add_tnl_item(ctx, model, module, new_module,
                                   src_fver, tgt_fver, type=typ)
        if hasattr(apriori, 'renamed_models'):
            model = 'ir.model'
            typ = 'model'
            for item in apriori.renamed_models:
                module = item[0]
                new_module = item[1]
                ctx = add_tnl_item(ctx, model, module, new_module,
                                   src_fver, tgt_fver, type=typ)
        transodoo.write_stored_dict(ctx)
        del sys.path[-1]
        del sys.path[-1]


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Migrate Odoo DB",
                                "© 2019 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-B', '--debug-statements',
                        action='store_true',
                        dest='opt_debug',
                        default=False)
    parser.add_argument('-b', '--branch',
                        action='store',
                        dest='opt_branch',
                        default='')
    parser.add_argument("-C", "--command-file",
                        help="migration command file",
                        dest="command_file",
                        metavar="file",
                        default='./migrate_odoo.csv')
    parser.add_argument("-c", "--tgt-config",
                        help="target DB configuration file",
                        dest="tgt_conf_fn",
                        metavar="file")
    parser.add_argument("-D", "--del-db-if-exist",
                        action="store_true",
                        dest="opt_del")
    parser.add_argument("-d", "--tgt-db_name",
                        help="Target database name",
                        dest="tgt_db_name",
                        metavar="name")
    parser.add_argument('-F', '--from-odoo-ver',
                        action='store',
                        dest='opt_from')
    parser.add_argument("-I", "--image",
                        action='store_true',
                        dest="image_mode",
                        default=False)
    parser.add_argument("-i", "--ids",
                        help="Ids to migrate",
                        dest="sel_ids",
                        metavar="ids")
    parser.add_argument("-k", "--default-behavior",
                        action="store_true",
                        dest="default_behavior")
    parser.add_argument("-m", "--sel-model",
                        help="Model to migrate",
                        dest="sel_model",
                        metavar="name")
    parser.add_argument('-n')
    parser.add_argument("-O", "--openupgrade-path",
                        help="Openupgrade path",
                        dest="opt_oupath",
                        metavar="directory")
    parser.add_argument("-P", "--openupgrade-working-path",
                        help="Openupgrade working path",
                        dest="opt_dpath",
                        metavar="directory")
    parser.add_argument('-q')
    parser.add_argument("-S", "--safe-mode",
                        action="store_true",
                        dest="opt_safe",
                        help="safe mode (do upgrade all before upgrade)")
    parser.add_argument("-s", "--use-synchro",
                        action='store_true',
                        dest="use_synchro",
                        default=False)
    parser.add_argument("-U", "--user",
                        help="login username",
                        dest="lgi_user",
                        metavar="username",
                        default="admin")
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument("-w", "--src-config",
                        help="Source DB configuration file",
                        dest="src_conf_fn",
                        metavar="file")
    parser.add_argument("-x", "--src-db_name",
                        help="Source database name",
                        dest="src_db_name",
                        metavar="name")
    parser.add_argument("-y", "--assume-yes",
                        action='store_true',
                        dest="assume_yes",
                        default=False)

    src_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if not src_ctx['opt_oupath']:
        src_ctx['opt_oupath'] = os.path.join(os.path.expanduser('~'),
                                             'openupgrade')
    if not src_ctx['opt_dpath']:
        src_ctx['opt_dpath'] = os.path.join(os.path.expanduser('~'), 'tmp')
    if src_ctx['tgt_db_name'] and not src_ctx['src_db_name']:
        src_ctx['src_db_name'], src_ctx['tgt_db_name'] = \
            src_ctx['tgt_db_name'], '%s_migrated' % src_ctx['tgt_db_name']
    elif not src_ctx['tgt_db_name'] and src_ctx['src_db_name']:
        src_ctx['tgt_db_name'] = '%s_migrated' % src_ctx['tgt_db_name']
    elif not src_ctx['tgt_db_name'] and not src_ctx['src_db_name']:
        raise KeyError('Missed database to upgrade! Please use -d switch')
    if not src_ctx['opt_from'] and not src_ctx['src_conf_fn']:
        raise KeyError('Missed original odoo version! Please use -F switch')
    if not src_ctx['opt_branch'] and not src_ctx['tgt_conf_fn']:
        raise KeyError('Missed final odoo version! Please use -b switch')
    if src_ctx['opt_from']:
        src_ctx['src_odoo_fver'] = clodoo.build_odoo_param(
            'FULLVER', odoo_vid=src_ctx['opt_from'], multi=True)
    else:
        src_ctx['src_odoo_fver'] = check_conf(src_ctx['src_conf_fn'],
                                              'oe_version')
    src_ctx['src_odoo_ver'] = clodoo.build_odoo_param(
        'MAJVER', odoo_vid=src_ctx['src_odoo_fver'], multi=True)
    if src_ctx['opt_branch']:
        src_ctx['tgt_odoo_fver'] = clodoo.build_odoo_param(
            'FULLVER', odoo_vid=src_ctx['opt_branch'], multi=True)
    else:
        src_ctx['tgt_odoo_fver'] = check_conf(src_ctx['tgt_conf_fn'],
                                              'oe_version')
    src_ctx['tgt_odoo_ver'] = clodoo.build_odoo_param(
        'MAJVER', odoo_vid=src_ctx['tgt_odoo_fver'], multi=True)
    if ((src_ctx['src_odoo_ver'] >= src_ctx['tgt_odoo_ver'] and
            not src_ctx['sel_model']) or
        (src_ctx['src_odoo_ver'] > src_ctx['tgt_odoo_ver'] and
            src_ctx['sel_model'])):
        raise KeyError('Final version must be greater than original version')
    src_ctx['final_ver'] = src_ctx['tgt_odoo_ver']
    tgt_ctx = src_ctx.copy()
    for param in ('db_name', 'conf_fn'):
        tgt_ctx[param] = tgt_ctx['tgt_%s' % param]
        src_ctx[param] = src_ctx['src_%s' % param]

    if src_ctx['sel_model']:
        migrate_1_table(src_ctx, tgt_ctx)
    else:
        migrate_database(src_ctx, tgt_ctx)

