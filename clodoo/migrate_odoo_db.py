#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
from __future__ import print_function, unicode_literals

from python_plus import _b

import sys
import os
import time
import inspect
import getpass
import contextlib
import shutil
import re
from subprocess import Popen
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
from unidecode import unidecode
from os0 import os0
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


__version__ = "0.3.55"
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
    'res.country': (['code'], ['name']),
    'res.country.state': (['name'],
                          ['code', 'country_id'],
                          ['dim_name'],),
    'res.partner': (['vat', 'fiscalcode', 'is_company', 'type'],
                    ['vat', 'fiscalcode', 'is_company'],
                    ['rea_code'],
                    ['vat', 'name', 'is_company', 'type'],
                    ['fiscalcode', 'type'],
                    ['vat', 'is_company'],
                    ['name', 'is_company'],
                    ['vat'],
                    ['name'],
                    ['dim_name'],),
    'res.company': (['vat'],),
    'account.account.type': (['name'],),
    'account.account': (['code', 'company_id'],
                        ['name', 'company_id'],
                        ['dim_name', 'company_id'],),
    'product.template': (['name', 'default_code']),
    'product.product': (['name', 'default_code'],
                        ['name', 'barcode'],
                        ['name'],
                        ['default_code'],
                        ['barcode'],
                        ['dim_name'],),
}
DET_FIELD = {
    'account.invoice': 'invoice_line',
    'sale.order': 'order_line',
}
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0')
DEF_CONF = {}
MODULES_2_LEAVE_BEHIND = [
    'process',
]
PRE_MIGRATION = '''
# -*- coding: utf-8 -*-
from openerp.openupgrade import openupgrade
from openerp.addons.openupgrade_records.lib import apriori

# XML_IDS format is [(old_xid, new_xid)...]
xml_ids = [
    ${xml_ids}
]


def cleanup_modules(cr):
    # Module merged format is [(old_module, new_module)...]
    openupgrade.update_module_names(
        cr, [
            ${module_merged}
        ], merge_modules=True,
    )


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute('drop view if exists report_document_user cascade')
    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )
    openupgrade.rename_xmlids(cr, xml_ids)
    openupgrade.check_values_selection_field(
        cr, 'ir_act_report_xml', 'report_type',
        ['controller', 'pdf', 'qweb-html', 'qweb-pdf', 'sxw', 'webkit'])
    openupgrade.check_values_selection_field(
        cr, 'ir_ui_view', 'type', [
            'calendar', 'diagram', 'form', 'gantt', 'graph', 'kanban',
            'qweb', 'search', 'tree'])
    cleanup_modules(cr)
'''
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


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
            import pdb          # pylint: disable=deprecated-module
            pdb.set_trace()


def exec_sql(ctx, query, response=None):
    return clodoo.exec_sql(ctx, query, response=response)


def copy_db(ctx, old_db, new_db):
    sql = 'drop database if exists "%s"' % new_db
    run_traced('pg_db_active', '-wa', '%s' % new_db)
    exec_sql(ctx, sql)
    sql = 'create database "%s" with template "%s"' % (new_db, old_db)
    clodoo.sql_reconnect(ctx)
    run_traced('pg_db_active', '-wa', '%s' % old_db)
    if not exec_sql(ctx, sql):
        sql = 'create database "%s"' % new_db
        exec_sql(ctx, sql)
        os.environ['PGUSER'] = ctx['db_user']
        if not os.environ.get('PGHOST'):
            os.environ['PGHOST'] = ctx['db_host']
        if not os.environ.get('PGPORT'):
            os.environ['PGPORT'] = str(ctx['db_port'])
        cmd = 'pg_dump -U%s --format=custom --no-password %s ' \
              '| pg_restore -U%s --no-password --dbname=%s' % (
                  ctx['db_user'], old_db, ctx['db_user'], new_db)
        os0.wlog('>>> %s' % cmd)
        sts = 0
        if not src_ctx['dry_run']:
            sts = os.system(cmd)
        return (sts == 0)
    return True


def env_ref(ctx, xref):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        ids = clodoo.searchL8(ctx, 'ir.model.data', [('module', '=', xrefs[0]),
                                                     ('name', '=', xrefs[1])])
        if ids:
            return clodoo.browseL8(ctx, 'ir.model.data', ids[0]).res_id
    return False


def py_reassign_db_owner(ctx, dbname, old_user, new_user):
    for sql in (
            "GRANT ALL PRIVILEGES ON DATABASE %s TO %s" % (dbname, new_user),
            "ALTER DATABASE %s OWNER TO %s" % (dbname, new_user),
            "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO %s" %
                new_user,
            "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO %s" %
                new_user,
            "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO %s" %
                new_user,
            "ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO %s" % new_user,
            "ALTER DEFAULT PRIVILEGES GRANT ALL ON SEQUENCES TO %s" % new_user
            ):
        sts = exec_sql(ctx, sql)
        if sts:
            return sts
    sql = "select tablename from pg_tables where schemaname = 'public'"
    recs = exec_sql(ctx, sql, response=True)
    for rec in recs:
        sql = 'ALTER TABLE "%s" OWNER TO %s' % (rec[0], new_user)
        sts = exec_sql(ctx, sql)
        if sts:
            return sts
        sql = 'GRANT ALL PRIVILEGES ON TABLE "%s" TO %s' % (rec[0], new_user)
        exec_sql(ctx, sql)
        if sts:
            return sts
    sql = "select sequence_name from information_schema.sequences " \
          "where sequence_schema = 'public'"
    recs = exec_sql(ctx, sql, response=True)
    for rec in recs:
        sql = 'ALTER SEQUENCE "%s" OWNER TO %s' % (rec[0], new_user)
        exec_sql(ctx, sql)
        if sts:
            return sts
        sql = 'GRANT ALL PRIVILEGES ON SEQUENCE "%s" TO %s' % (rec[0], new_user)
        exec_sql(ctx, sql)
        if sts:
            return sts
    sql = "select table_name from information_schema.views " \
           "where table_schema = 'public'"
    recs = exec_sql(ctx, sql, response=True)
    for rec in recs:
        sql = 'ALTER VIEW "%s" OWNER TO %s' % (rec[0], new_user)
        exec_sql(ctx, sql)
        if sts:
            return sts
        sql = 'GRANT ALL PRIVILEGES ON TABLE "%s" TO %s' % (rec[0], new_user)
        exec_sql(ctx, sql)
        if sts:
            return sts
    sql = 'GRANT %s TO %s' % (old_user, new_user)
    return exec_sql(ctx, sql)


def reassign_db_owner(ctx, dbname, old_user, new_user):
    run_traced('pg_db_active', '-wa', '%s' % tgt_ctx['db_name'])
    sts = py_reassign_db_owner(tgt_ctx,
                               tgt_ctx['db_name'],
                               src_ctx['db_user'],
                               tgt_ctx['db_user'])
    if sts:
        run_traced('pg_db_reassign_owner',
                   '-d', tgt_ctx['db_name'],
                   '-o', src_ctx['db_user'],
                   '-U', tgt_ctx['db_user'])

def drop_session(ctx, dbname, datadir=None, odoo_vid=None):
    if not odoo_vid:
        odoo_vid = ctx.get('tgt_vid')
    if not odoo_vid:
        odoo_vid = ctx.get('src_vid')
    if not datadir:
        datadir = ctx.get('data_dir')
    if not datadir:
        datadir = clodoo.build_odoo_param(
            'DDIR', odoo_vid=odoo_vid, multi=True)
    odoo_ver = clodoo.build_odoo_param(
        'MAJVER', odoo_vid=odoo_vid, multi=True)
    if odoo_ver < 8:
        os.system('''for f in $(grep -l "%s" /tmp/oe-sessions-odoo/*); do
        rm -f $f; done''' % (dbname))
    else:
        os.system('''for f in $(grep -l "%s" %s/sessions/*); do
        rm -f $f; done''' % (dbname, datadir))


def get_cache(ctx):
    ctx['_CACHE'] = ctx.get('_CACHE', {})
    return ctx['_CACHE']


def cache_is_entry(cache, model, id):
    cache[model] = cache.get(model, {})
    return (id in cache[model])


def cache_get_entry(cache, model, id):
    cache[model] = cache.get(model, {})
    return cache[model].get('id', False)


def cache_store_entry(cache, model, id, keep=None):
    cache[model] = cache.get(model, {})
    if id or keep:
        cache[model]['id'] = id
    elif id in cache[model]:
        del cache[model]['id']
    return cache[model]


def set_tmp_keys(ctx, model, id, vals):
    try_again = False
    if 'code' in vals:
        vals['code'] = str(id)
        try_again = True
    if 'name' in vals:
        vals['name'] = 'ID=%d %s' % (id, vals['name'])
        try_again = True
    return try_again, vals


def run_traced(*args):
    os0.wlog('>>> %s' % ' '.join(args))
    return Popen(args).wait()


def sed(*args):
    filename = args[0]
    with open(filename, 'r') as fd:
        lines = fd.read().split('\n')
    for arg in args[1:]:
        if not isinstance(arg, (tuple, list)):
            raise KeyError('Invalid parametes')
        for lineno in range(len(lines)):
            lines[lineno] = re.sub(arg[0], arg[1], lines[lineno])
    with open(filename, 'w') as fd:
        fd.write(_b('\n'.join(lines)))


def sed_append(*args):
    filename = args[0]
    with open(filename, 'r') as fd:
        lines = fd.read().split('\n')
    for arg in args[1:]:
        lines.append(arg)
    with open(filename, 'w') as fd:
        fd.write(_b('\n'.join(lines)))


def config_get_list(config, item):
    return config.get('options', item).strip().split(',')


def run_odoo_alltest(odoo_vid, confn, db_name, logfile, modules=None):
    if modules:
        modules = ','.join(modules)
    else:
        modules = 'all'
    src_odoo_bin = clodoo.build_odoo_param(
            'BIN', odoo_vid=odoo_vid, multi=True)
    run_traced(src_odoo_bin,
               '-c', confn,
               '-d', db_name,
               '-u', modules,
               '--stop-after-init',
               '--no-xmlrpc',
               '--logfile=%s' % logfile)


def db_exist(ctx, dbname):
    session = clodoo.connectL8(ctx)
    if isinstance(session, basestring):
        os0.wlog('Connection error %s' % session)
        raise IOError(session)
    if dbname in ctx['odoo_session'].db.list():
        return True
    return False


def wep_logs(ctx):
    if os.path.isdir(ctx['opt_oulpath']):
        shutil.rmtree(ctx['opt_oulpath'])
    for ver in VERSIONS:
        tmp_dir = os.path.join(ctx['opt_oupath'], 'ou_%s' % ver)
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
    tmp_dir = os.path.join(ctx['opt_oupath'], 'openupgrade')
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    flog_dir =  os.path.dirname(ctx['logfn'])
    if not os.path.isdir(flog_dir):
        os.mkdir(flog_dir)
    if os.path.isfile(ctx['logfn']):
        os.remove(ctx['logfn'])
    if os.path.isfile(ctx['logfile']):
        os.remove(ctx['logfile'])
    if ctx['oca_migrate']:
        if os.path.isdir(os.path.join(os.path.expanduser('~'), 'openupgrade')):
            shutil.rmtree(os.path.join(os.path.expanduser('~'), 'openupgrade'))


def drop_db(src_ctx, tgt_ctx, dbname, dbname2):
    for db in (dbname, dbname2):
        cmd = 'pg_db_active -wa %s|dropdb -U%s %s' % (
            db, tgt_ctx['db_user'], db)
        os.system(cmd)
        cmd = 'pg_db_active -wa %s|dropdb -U%s %s' % (
            db, src_ctx['db_user'], db)
        os.system(cmd)


def set_uninstalled_by_sql(tgt_ctx, bad_module_list):
    os0.wlog('set_uninstalled_by_sql%s' % bad_module_list)
    query = "update ir_module_module set state='uninstalled'" \
            " where name in (%s) and state<>'installed';" % str(
                bad_module_list)[1:-1]
    exec_sql(tgt_ctx, query)


def set_installed_by_sql(tgt_ctx, bad_module_list):
    os0.wlog('set_installed_by_sql%s' % bad_module_list)
    query = "update ir_module_module set state='installed'" \
            " where name in (%s);" % str(bad_module_list)[1:-1]
    exec_sql(tgt_ctx, query)


def ren_db(old_dbname, new_dbname, db_user):
    cmd = 'pg_db_active -wa %s|' \
          'psql -U%s -c "ALTER DATABASE %s RENAME TO %s;" template1' % (
              old_dbname, db_user, old_dbname, new_dbname)
    os.system(cmd)


def new_dbname(db, odoo_ver, oca_migrated):
    if oca_migrated:
        return '%s_migrated' % db
    prior = odoo_ver - 1
    if db.endswith(str(prior)):
        return '%s_%d' % (db[0: -len(str(prior))], odoo_ver)
    return '%s_%d' % (db, odoo_ver)


def drop_module(ctx, module, force=None):
    if force:
        os0.wlog('>>> uninstall %s' % module)
        return clodoo.act_uninstall_modules(ctx, module_list=[module])
    else:
        module_id = clodoo.searchL8(ctx, 'ir.module.module',
                                    [('name', '=', module)])
        ids = clodoo.searchL8(ctx, 'ir.module.module.dependency',
                              [('name', '=', module)])
        if not ids:
            os0.wlog('>>> uninstall %s' % module)
            return clodoo.act_uninstall_modules(ctx, module_list=[module])
    return 1
 

def remove_unmigrable_modules(src_ctx, tgt_ctx, bad_module_list):
    MODULES_2_DROP = {
        '12.0': [],
        '11.0': [],
        '10.0': [],
        '9.0': ['account_financial_report_webkit_xls',
                'base_headers_webkit',
                'edi',
                'knowledge',
                'multi_company',
                'report_xls',
                'share'],
        '8.0': [],
        '7.0': [],
        '6.1': [],
    }
    MODULES_FORCE_2_DROP = {
        '12.0': [],
        '11.0': [],
        '10.0': [],
        '9.0': ['attachment_preview',
                'l10n_it_split_payment'],
        '8.0': [],
        '7.0': [],
        '6.1': [],
    }
    odoo_fver = tgt_ctx['tgt_odoo_fver']
    uid, ctx = clodoo.oerp_set_env(ctx=src_ctx, db=tgt_ctx['db_name'])
    # FIX oerp_set_env change dry_run
    src_ctx['dry_run'] = tgt_ctx['dry_run']
    for module in bad_module_list:
        if module in MODULES_2_DROP[odoo_fver]:
            drop_module(ctx, module)
        elif module in MODULES_FORCE_2_DROP[odoo_fver]:
            drop_module(ctx, module, force=True)
    run_traced('pg_db_active', '-wa', '%s' % tgt_ctx['db_name'])


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
                    exec_sql(ctx, sql)
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
    except IOError:
        try_again = True
        drop_out_originals(ctx, model, ids[0], vals)
    if try_again:
        try:
            try_again = False
            clodoo.writeL8(ctx, model, ids, vals)
        except IOError:
            try_again, vals = set_tmp_keys(ctx, model, ids[0], vals)
    if try_again:
        try:
            try_again = False
            clodoo.writeL8(ctx, model, ids, vals)
        except IOError, e:
            os0.wlog('%s Error writing record %d of %s' % (e, src_id, model))
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
        rows = exec_sql(ctx, sql_last, response=True)
        last_id = rows[0][0]
        if id > 0:
            if last_id != id:
                sql_seq = 'alter sequence %s restart %d;' % (table, id)
                exec_sql(ctx, sql_seq)
    try_again = False
    new_id = 0
    try:
        new_id = clodoo.createL8(ctx, model, vals)
    except IOError:
        try_again = True
        drop_out_originals(ctx, model, id, vals)
    if try_again:
        try:
            try_again = False
            if sql_seq:
                exec_sql(ctx, sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except IOError:
            try_again, vals = set_tmp_keys(ctx, model, id, vals)
    if try_again:
        try:
            try_again = False
            if sql_seq:
                exec_sql(ctx, sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except IOError:
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
                exec_sql(ctx, sql_seq)
            new_id = clodoo.createL8(ctx, model, vals)
        except IOError:
            os0.wlog('Error creating record %d of %s' % (id, model))
            manage_error()
            new_id = id
    if new_id != id:
        os0.wlog("Cannot create record %d of %s" % (id, model))
        if not ctx['assume_yes']:
            raw_input('Press RET to continue')
    if last_id and last_id > 1 and last_id > id:
        sql = 'alter sequence %s restart %d;' % (table, last_id)
        exec_sql(ctx, sql)


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
                os0.wlog('Installing module %s' % module)
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


def get_foreign_value(tgt_ctx, src_ctx, relation, value,
                      tomany=None, format=False):

    def bind_foreign_ref(tgt_ctx, src_ctx, model, id, rel_mode):
        new_value = False
        cache = get_cache(src_ctx)
        if rel_mode == 'image':
            if clodoo.searchL8(tgt_ctx, relation, [('id', '=', id)]):
                new_value = id
        elif cache_is_entry(cache, model, id):
            new_value = cache_get_entry(cache, model, id)
        else:
            rel_rec = clodoo.browseL8(src_ctx, relation, id,
                                      context={'lang': 'en_US'})
            keyval = clodoo.extract_vals_from_rec(src_ctx,
                                                  model,
                                                  rel_rec,
                                                  format='str')
            id = search4rec(tgt_ctx, model, keyval)
            if id >= 1:
                new_value = id
                cache_store_entry(cache, model, id)
            elif not src_ctx.get('no_recurse'):
                new_value = synchro(tgt_ctx, relation, keyval)
            else:
                cache_store_entry(cache, model, new_value)
        return new_value

    if not value:
        return False
    if not relation:
        raise RuntimeError('No relation %s found' % relation)
    rel_mode = get_model_copy_mode(tgt_ctx, relation)
    clodoo.get_model_structure(
        src_ctx, relation,
        ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
    clodoo.get_model_structure(
        tgt_ctx, relation,
        ignore=IGNORE_FIELDS.get(relation, []) + IGNORE_FIELDS['*'])
    new_value = False
    if tgt_ctx['_ml'].get(relation) != 'no':
        if isinstance(value, basestring):
            pass    # TODO
            if tomany:
                new_value = [new_value]
        elif isinstance(relation, (list, tuple)):
            new_value = []
            for id in value:
                new_value.append(
                    bind_foreign_ref(tgt_ctx, src_ctx, relation, id, rel_mode))
        else:
            new_value = bind_foreign_ref(
                tgt_ctx, src_ctx, relation, value, rel_mode)
    if format == 'cmd' and value and tomany:
        value = [(6, 0, value)]
    return new_value


def cvt_o2m_value(tgt_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    return get_foreign_value(tgt_ctx, src_ctx, relation, value, tomany=True)


def cvt_m2m_value(tgt_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    return get_foreign_value(tgt_ctx, src_ctx, relation, value, tomany=True)


def cvt_m2o_value(tgt_ctx, src_ctx, model, name, value, format=False):
    relation = src_ctx['STRUCT'][model][name]['relation']
    return get_foreign_value(tgt_ctx, src_ctx, relation, value)


def load_record(tgt_ctx, src_ctx, model, rec, mode=None):
    mode = mode or get_model_copy_mode(src_ctx, model)
    vals = clodoo.extract_vals_from_rec(src_ctx, model, rec, format='str')
    vals = clodoo.cvt_from_ver_2_ver(tgt_ctx,
                                     model,
                                     src_ctx['oe_version'],
                                     tgt_ctx['oe_version'],
                                     vals)
    for name in vals.copy():
        if name not in tgt_ctx['STRUCT'][model]:
            del vals[name]
            continue
        elif name == 'company_id' and src_ctx['by_company']:
            continue
        elif tgt_ctx['STRUCT'][model][name]['ttype'] in ('one2many'):
            vals[name] = cvt_o2m_value(tgt_ctx, tgt_ctx, model, name,
                                       vals[name], format='cmd')
        elif tgt_ctx['STRUCT'][model][name]['ttype'] in ('many2many'):
            vals[name] = cvt_m2m_value(tgt_ctx, tgt_ctx, model, name,
                                       vals[name], format='cmd')
        elif tgt_ctx['STRUCT'][model][name]['ttype'] in ('many2one'):
            vals[name] = cvt_m2o_value(tgt_ctx, tgt_ctx, model, name,
                                       vals[name], format='cmd')
        if (vals[name] is False and
                tgt_ctx['STRUCT'][model][name]['ttype'] != 'boolean'):
            del vals[name]
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


def set_actual_state(tgt_ctx, model, id, state):
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
    rec = False
    if not ids:
        id = False
    else:
        id = ids[0]
    tgt_ctx['_COMMIT'][model] = {'id': id}
    if 'state' in vals:
        tgt_ctx['_COMMIT'][model]['state'] = vals['state']
    elif id:
        rec = clodoo.browseL8(tgt_ctx, model, id)
        if 'state' in rec:
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
    id = False
    if tgt_ctx['_COMMIT'].get(model):
        id = tgt_ctx['_COMMIT'][model]['id']
        if use_synchro(tgt_ctx, model):
            id = clodoo.executeL8(tgt_ctx,
                                  model,
                                  'commit',
                                  id)
        else:
            set_actual_state(
                tgt_ctx, model, id, tgt_ctx['_COMMIT'][model]['state'])
    tgt_ctx['_COMMIT'][model] = False
    return id


def synchro(tgt_ctx, model, vals):
    tgt_ctx['_COMMIT'][model] = False
    cache = get_cache(src_ctx)
    # if 'company_id' in vals and tgt_ctx.get('by_company'):
    #     vals['company_id'] = tgt_ctx['company_id']
    id = search4rec(tgt_ctx, model, vals)
    if id > 0:
        vals, sts = set_state_to_draft(tgt_ctx, model, [id], vals)
        write_no_dup(tgt_ctx, model, [id], vals, id)
        cache_store_entry(cache, model, id)
    else:
        try:
            vals, sts = set_state_to_draft(tgt_ctx, model, False, vals)
            id = clodoo.createL8(tgt_ctx, model, vals)
            cache_store_entry(cache, model, id)
            tgt_ctx['_COMMIT'][model]['id'] = id
        except IOError, e:
            os0.wlog('%s Cannot create %s src id=%d' % (e, model, id))
            manage_error()



def search4rec(tgt_ctx, model, vals):

    def dim_text(text):
        if text:
            text = unidecode(text).strip()
            res = ''
            for ch in text:
                if ch.isalnum():
                    res += ch.lower()
            text = res
        return text

    company_id =  tgt_ctx.get('company_id', False)
    id = -1
    for keys in tgt_ctx['_kl'][model]:
        where = []
        for key in keys:
            if (key not in vals and
                    key == 'dim_name' and
                    vals.get('name')):
                where.append(('dim_name',
                              '=',
                              dim_text(vals['name'])))
            elif key not in vals and key == 'company_id':
                where.append((key, '=', company_id))
            elif key not in vals:
                where = []
                break
            else:
                where.append((key, '=', vals[key]))
        if where:
            ids = clodoo.searchL8(tgt_ctx, model, where)
            if not ids and 'active' in tgt_ctx['STRUCT'][model]:
                where.append(('active', '=', False))
                ids = clodoo.searchL8(tgt_ctx, model, where)
            if ids:
                id = ids[0]
                break
    return id


def copy_record(tgt_ctx, src_ctx, model, rec, mode=None):
    msg_burst('%s %d' % (model, rec.id))
    mode = mode or get_model_copy_mode(src_ctx, model)
    # Avoid loop nesting
    cache = get_cache(src_ctx)
    if cache_is_entry(cache, model, rec.id):
        return
    cache_store_entry(cache, model, False, keep=True)
    vals = load_record(tgt_ctx, src_ctx, model, rec, mode=mode)
    if not vals:
        return
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
        synchro(tgt_ctx, model, vals)


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
        rows = exec_sql(src_ctx, sql, response=True)
        last_id = rows[0][0]
        if last_id > 0:
            for id in clodoo.searchL8(tgt_ctx, model,
                                      [('id', '>', last_id)]):
                try:
                    clodoo.unlinkL8(tgt_ctx, model, id)
                except IOError:
                    os0.wlog("Cannot delete record %d of %s" % (id, model))
                    if not tgt_ctx['assume_yes']:
                        dummy = raw_input('Press RET to continue')
    where = set_where_from_txtids(src_ctx['sel_ids'])
    if src_ctx['by_company']:
        company_id = env_ref(src_ctx, 'z0bug.mycompany')
        if not company_id:
            print('!!Internal error: no company found!')
        else:
            where.append(('company_id', '=', company_id))
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
                names = (names)
                break
    if not names:
        if clodoo.is_valid_field(ctx, model, 'company_id'):
            names = ['company_id']
        if clodoo.is_valid_field(ctx, model, 'code'):
            names.append('code')
        elif clodoo.is_valid_field(ctx, model, 'name'):
            names.append('name')
        names = (names)
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
                   'product.template',
                   'res.partner'):
        mode = 'sql'
    if mode == 'inquire':
        mode_selection = {'i': 'image', 's': 'sql', 'n': 'no'}
        dummy = ''
        while not dummy:
            if ctx['sel_model']:
                if model in ctx['sel_model']:
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


def migrate_sel_tables(src_ctx, tgt_ctx):
    src_ctx = init_ctx(src_ctx)
    import pdb
    pdb.set_trace()
    src_ctx, tgt_ctx, src_config, tgt_config = adjust_ctx(src_ctx, tgt_ctx)
    uid, src_ctx = clodoo.oerp_set_env(ctx=src_ctx)
    # FIX oerp_set_env change dry_run
    src_ctx['dry_run'] = tgt_ctx['dry_run']
    uid, tgt_ctx = clodoo.oerp_set_env(ctx=tgt_ctx)
    # FIX oerp_set_env change dry_run
    tgt_ctx['dry_run'] = src_ctx['dry_run']
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
                if model in PKEYS:
                    tgt_ctx['_kl'][model] = PKEYS[model]
                else:
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


def init_ctx(src_ctx):
    src_ctx['src_vid'] = src_ctx['from_branch']
    src_ctx['src_odoo_fver'] = clodoo.build_odoo_param(
            'FULLVER', odoo_vid=src_ctx['from_branch'], multi=True)
    src_ctx['from_odoo_fver'] = src_ctx['src_odoo_fver']
    src_ctx['src_odoo_ver'] = clodoo.build_odoo_param(
            'MAJVER', odoo_vid=src_ctx['from_branch'], multi=True)
    src_ctx['src_conf_fn'] = src_ctx['from_confn']
    src_ctx['src_db_name'] = src_ctx['from_dbname']
    return src_ctx


def get_config_fns(ctx, src_tgt):
    if src_tgt not in ('src', 'tgt'):
        raise('Invalid parameter src/tgt')
    item = 'conf_fn'
    odoo_confn = clodoo.build_odoo_param(
        'CONFN', odoo_vid=ctx['%s_vid' % src_tgt], multi=True)
    if src_tgt == 'src' and ctx['%s_vid' % src_tgt] == ctx['from_branch']:
        ctx[item] = ctx['src_%s' % item]
        if not os.path.isfile(odoo_confn):
            odoo_confn = False
    elif src_tgt == 'tgt' and ctx['%s_odoo_ver' % src_tgt] == ctx['final_ver']:
        if ctx.get('final_confn'):
            ctx[item] = tgt_ctx['final_confn']
            if not os.path.isfile(odoo_confn):
                odoo_confn = False
        else:
            ctx[item] = odoo_confn
            odoo_confn = False
    else:
        ctx[item] = odoo_confn
        odoo_confn = False
    if not os.path.isfile(ctx[item]):
        raise IOError('File %s not found' % ctx[item])
    config = ConfigParser.SafeConfigParser()
    if odoo_confn:
        config.read([ctx[item], odoo_confn])
    else:
        config.read(ctx[item])
    return config


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


def load_openupgradelib(ctx, odoo_fver):
    oulpath_parentdir =  os.path.dirname(ctx['opt_oulpath'])
    oulname =  os.path.basename(ctx['opt_oulpath'])
    oulpath_bindir = os.path.join(ctx['opt_oulpath'], 'openupgradelib')
    oulpath_script = os.path.join(oulpath_bindir, 'openupgrade.py')
    oul_git = 'https://github.com/OCA/openupgradelib.git'
    os0.wlog('>>> load_openupgradelib(%s)' % odoo_fver)

    if not os.path.isdir(oulpath_bindir) or not os.path.isfile(oulpath_script):
        with pushd(oulpath_parentdir):
            if os.path.isdir(ctx['opt_oulpath']):
                shutil.rmtree(ctx['opt_oulpath'])
            run_traced('git', 'clone', oul_git, oulname,
                       '--single-branch',
                       '--depth', '1')
    else:
        os0.wlog('Found valid directory %s' % oulpath_bindir)
    # sys.path.append(ctx['opt_oulpath'])
    os.environ['PYTHONPATH'] = ':'.join(filter(None, [
        ctx['opt_oulpath'], os.environ.get('PYTHONPATH')]))


def load_openupgrade(ctx, odoo_fver):
    if odoo_fver:
        oupath_parentdir = os.path.dirname(ctx['opt_oupath'])
        oupath_dir = ctx['opt_oupath']
        ou_ver_path = os.path.join(ctx['opt_oupath'], 'ou_%s' % odoo_fver)
    else:
        oupath_parentdir = os.path.expanduser('~')
        oupath_dir = oupath_parentdir
        ou_ver_path = os.path.join(os.path.expanduser('~'), 'openupgrade')
    oupath_bindir9 = os.path.join(ou_ver_path, 'openerp')
    oupath_bindir10 = os.path.join(ou_ver_path, 'odoo')
    ou_git = 'https://github.com/OCA/openupgrade.git'
    os0.wlog('>>> load_openupgrade(%s)' % ctx['tgt_odoo_fver'])

    def get_ou_release(oupath_bindir):
        with pushd(oupath_bindir):
            sys.path.insert(0, '')
            import release
            x = re.match(r'[0-9]+\.[0-9]+', release.version)
            if x:
                ou_ver = release.version[0:x.end()]
            else:
                ou_ver = release.version
            del sys.path[0]
        return ou_ver

    ou_ver = ''
    if not os.path.exists(ou_ver_path):
        if not os.path.exists(oupath_parentdir):
            os.mkdir(oupath_parentdir)
        if odoo_fver and not os.path.exists(ctx['opt_oupath']):
            os.mkdir(ctx['opt_oupath'])
        os.mkdir(ou_ver_path)
    elif os.path.isdir(oupath_bindir10):
        ou_ver = get_ou_release(oupath_bindir10)
    elif os.path.isdir(oupath_bindir9):
        ou_ver = get_ou_release(oupath_bindir9)
    if ou_ver != ctx['tgt_odoo_fver']:
        with pushd(oupath_dir):
            if odoo_fver and os.path.isdir(ou_ver_path):
                shutil.rmtree(ou_ver_path)
            run_traced('git', 'clone', ou_git,
                       os.path.basename(ou_ver_path),
                       '-b', ctx['tgt_odoo_fver'],
                       '--single-branch',
                       '--depth', '1')
            apply_patch(ou_ver_path, ctx['tgt_odoo_fver'])
    else:
        os0.wlog('Found valid directory %s' % ctx['opt_oupath'])
    if not src_ctx['no_venv'] and not src_ctx['dry_run']:
        venv_path = os.path.join(tgt_ctx['venv_oupath'], 'openupgrade')
        if not os.path.isdir(venv_path):
            os.symlink(ou_ver_path, venv_path)
    return ou_ver_path


def apply_patch(ou_ver_path, odoo_fver):
    if odoo_fver == '9.0':
        file = os.path.join(ou_ver_path, 'openerp', 'addons', 'base',
                            'migrations', '9.0.1.3', 'post-migration.py')
        if os.path.isfile(file):
            sed(file,
                [r"^ *'ir_actions': \[", "#     'ir_actions': ["],
                [r"^ *\('help', None, None\),",
                 "#         ('help', None, None),"],
                ["^ *],", "#     ],"],
                )


def add_tnl_item(ctx, model, module, new_module, src_fver, tgt_fver,
                 type=False):
    tnl = transodoo.translate_from_to(ctx, model, module, src_fver, tgt_fver,
                                      type=type)
    if tnl != new_module:
        os0.wlog('Translate module %s -> %s' % (module, new_module))
        ver_names = {}
        name = module
        for ver in VERSIONS:
            if ver == ctx['tgt_odoo_fver']:
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


def do_tnl_module_list(ctx, module_list, src_fver, tgt_fver, tgt_module_list,
                       pure=None):
    sys.path.append(os.path.dirname(__file__))
    transodoo.read_stored_dict(ctx)
    tnl_module_list = []
    bad_module_list = []
    model = 'ir.module.module'
    for item in module_list:
        tnl = transodoo.translate_from_to(
            ctx, model, item, src_fver, tgt_fver, type='module')
        if tnl == item:
            tnl = transodoo.translate_from_to(
                ctx, model, item, src_fver, tgt_fver, type='merge')
        if tgt_module_list and tnl not in tgt_module_list:
            bad_module_list.append(item)
            if not pure:
                tnl_module_list.append(tnl)
        else:
            tnl_module_list.append(tnl)
    return tnl_module_list, bad_module_list


def odoo_dependencies(ctx, action, db_name, lconf, paths, odoo_fver,
                      matches=None, depends_by=None):
    with pushd('/opt/odoo/dev/pypi/wok_code/wok_code'):
        sys.path.append('')
        import odoo_dependencies
        ctx['branch'] = odoo_fver
        if db_name:
            ctx['conf_fn'] = lconf
            ctx = odoo_dependencies.retrieve_db_modules(ctx)
            matches = ctx['modules_to_match']
        if action == 'dep':
            res = odoo_dependencies.get_dependencies_list(paths,
                                                          matches=matches)
        elif action == 'mod':
            res = odoo_dependencies.get_modules_list(paths, matches=matches)
        elif action == 'rev':
            res = odoo_dependencies.get_dependents_list(
                paths, matches=matches, depends_by=depends_by)
    del sys.path[-1]
    return res


def add_versioned_tnl(ctx, src_fver, tgt_fver):
    os0.wlog('Upgrading translation name from %s to %s' % (src_fver, tgt_fver))
    ou_ver_path = os.path.join(ctx['opt_oupath'], 'ou_%s' % tgt_fver)
    with pushd(ou_ver_path):
        sys.path.append('')
        sys.path.append(os.path.dirname(__file__))
        if int(tgt_fver.split('.')[0]) < 10:
            import openerp.addons.openupgrade_records.lib.apriori as apriori
        else:
            import odoo.addons.openupgrade_records.lib.apriori as apriori
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


def adjust_ctx(src_ctx, tgt_ctx):
    for item in ('odoo_ver', 'odoo_fver', 'vid', 'conf_fn', 'svc_protocol',
                 'db_host', 'db_name', 'db_user', 'db_port', 'db_password',
                 'level',  'xmlrpc_port', 'psycopg2',
                 'login_user', 'login_password', 'logfile', 'without_demo'):
        src_param = 'src_%s' % item
        tgt_param = 'tgt_%s' % item
        if item == 'odoo_ver':
            if not src_ctx['sel_model']:
                tgt_ctx[tgt_param] = src_ctx[src_param] + 1
        elif item == 'odoo_fver':
            if not src_ctx['sel_model']:
                tgt_ctx[tgt_param] = src_ctx[src_param].replace(
                    str(src_ctx['src_odoo_ver']),
                    str(tgt_ctx['tgt_odoo_ver']))
        elif item == 'vid':
            if not src_ctx['sel_model']:
                tgt_ctx[tgt_param] = src_ctx[src_param].replace(
                    str(src_ctx['src_odoo_ver']),
                    str(tgt_ctx['tgt_odoo_ver']))
                if tgt_ctx[tgt_param].startswith('v'):
                    tgt_ctx[tgt_param] = tgt_ctx['tgt_odoo_fver']
            else:
                tgt_ctx[tgt_param] = tgt_ctx['final_branch']
                tgt_ctx['tgt_odoo_fver'] = clodoo.build_odoo_param(
                    'FULLVER', odoo_vid=tgt_ctx['final_branch'], multi=True)
                tgt_ctx['tgt_odoo_ver'] = clodoo.build_odoo_param(
                    'MAJVER', odoo_vid=tgt_ctx['final_branch'], multi=True)
        elif item == 'conf_fn':
            src_config = get_config_fns(src_ctx, 'src')
            tgt_config = get_config_fns(tgt_ctx, 'tgt')
        elif item == 'svc_protocol':
            src_ctx['branch'] = src_ctx['src_odoo_fver']
            src_ctx['oe_version'] = src_ctx['src_odoo_fver']
            src_config.set('options', 'oe_version', src_ctx['oe_version'])
            if not src_ctx.get(item):
                if src_ctx['oe_version'] in ('6.1', '7.0', '8.0'):
                    src_ctx['svc_protocol'] = 'xmlrpc'
                elif src_ctx['oe_version']:
                    src_ctx['svc_protocol'] = 'jsonrpc'
            tgt_ctx['branch'] = tgt_ctx['tgt_odoo_fver']
            tgt_ctx['oe_version'] = tgt_ctx['tgt_odoo_fver']
            tgt_config.set('options', 'oe_version', tgt_ctx['oe_version'])
            if tgt_ctx['oe_version'] in ('6.1', '7.0', '8.0'):
                tgt_ctx['svc_protocol'] = 'xmlrpc'
            elif tgt_ctx['oe_version']:
                tgt_ctx['svc_protocol'] = 'jsonrpc'
        elif item == 'db_name':
            if src_ctx['src_vid'] == src_ctx['from_branch']:
                src_ctx[item] = src_ctx[src_param]
            if tgt_ctx['tgt_odoo_ver'] == tgt_ctx['final_ver']:
                if tgt_ctx['final_dbname']:
                    tgt_ctx[item] = tgt_ctx['final_dbname']
                else:
                    tgt_ctx[item] = new_dbname(src_ctx[item],
                                               tgt_ctx['tgt_odoo_ver'],
                                               tgt_ctx['oca_migrate'])
            else:
                tgt_ctx[item] = new_dbname(src_ctx[item],
                                           tgt_ctx['tgt_odoo_ver'],
                                           tgt_ctx['oca_migrate'])
        elif item == 'level':
            src_ctx[item] = DEF_CONF[item]
            tgt_ctx[item] = DEF_CONF[item]
        elif item in ('db_host', 'db_user', 'db_port', 'db_password',
                      'xmlrpc_port'):
            if src_config.has_option('options', item):
                src_ctx[item] = src_config.get('options', item)
                if src_ctx[item] == 'False':
                    src_ctx[item] = DEF_CONF[item]
            elif item == 'db_user':
                src_ctx[item] = 'odoo'
            else:
                src_ctx[item] = DEF_CONF[item]
            if isinstance(src_ctx[item], basestring):
                src_config.set('options', item, src_ctx[item])
            else:
                src_config.set('options', item, str(src_ctx[item]))
            if tgt_config.has_option('options', item):
                tgt_ctx[item] = tgt_config.get('options', item)
                if tgt_ctx[item] == 'False':
                    tgt_ctx[item] = DEF_CONF[item]
            else:
                tgt_ctx[item] = DEF_CONF[item]
            if isinstance(tgt_ctx[item], basestring):
                tgt_config.set('options', item, tgt_ctx[item])
            else:
                tgt_config.set('options', item, str(tgt_ctx[item]))
        elif item == 'psycopg2':
            src_ctx[item] = 'True'
            src_config.set('options', item, str(src_ctx[item]))
            tgt_ctx[item] = 'True'
            tgt_config.set('options', item, str(tgt_ctx[item]))
        elif item == 'logfile':
            src_config.set('options', item, str(src_ctx[item]))
            tgt_config.set('options', item, str(tgt_ctx[item]))
        elif item == 'login_user':
            if src_config.has_option('options', item):
                src_ctx[item] = src_config.get('options', item)
            elif src_ctx.get(item):
                src_config.set('options', item, src_ctx[item])
            elif src_ctx.get('lgi_user'):
                src_ctx[item] = src_ctx['lgi_user']
                src_config.set('options', item, src_ctx[item])
            if tgt_config.has_option('options', item):
                tgt_ctx[item] = tgt_config.get('options', item)
            elif tgt_ctx.get(item) and tgt_ctx[item] != 'admin':
                tgt_config.set('options', item, tgt_ctx[item])
            elif tgt_ctx.get('lgi_user') and tgt_ctx['lgi_user'] != 'admin':
                tgt_ctx[item] = tgt_ctx['lgi_user']
                tgt_config.set('options', item, tgt_ctx[item])
            else:
                tgt_ctx[item] = src_ctx[item]
                tgt_config.set('options', item, tgt_ctx[item])
            found_pwd = False
            for nm in ('crypt_password', 'login_password'):
                if src_ctx.get(nm):
                    src_config.set('options', nm, src_ctx[nm])
                    found_pwd = True
                elif src_config.has_option('options', nm):
                    src_ctx[nm] = src_config.get('options', nm)
                    found_pwd = True
                elif not found_pwd:
                    src_ctx['login_password'] = getpass.getpass(
                            'Password for login user %s: ' %
                            src_ctx['lgi_user'])
                    src_config.set('options', 'login_password',
                                   src_ctx['login_password'])
                if tgt_ctx.get(nm):
                    tgt_config.set('options', nm, tgt_ctx[nm])
                elif tgt_config.has_option('options', nm):
                    tgt_ctx[nm] = tgt_config.get('options', nm)
                elif src_ctx.get(nm):
                    tgt_ctx[nm] = src_ctx[nm]
                    tgt_config.set('options', nm, tgt_ctx[nm])
        elif item == 'without_demo':
            src_ctx[item] = 'True'
            src_config.set('options', item, src_ctx[item])
            tgt_ctx[item] = 'True'
            tgt_config.set('options', item, tgt_ctx[item])
    if src_ctx['no_venv']:
        src_ctx['venv_oupath'] = src_ctx['opt_oupath']
    else:
        src_ctx['venv_oupath'] = os.path.join(
            os.path.expanduser('~'), 'VENV-%s' % tgt_ctx['tgt_odoo_fver'])
    tgt_ctx['venv_oupath'] = src_ctx['venv_oupath']
    return src_ctx, tgt_ctx, src_config, tgt_config


def shift_ctx(src_ctx, tgt_ctx, phase=None):
    phase = phase or 1
    for item in ('vid', 'odoo_fver', 'odoo_ver'):
        src_ctx['src_%s' % item], tgt_ctx[
            'tgt_%s' % item] = tgt_ctx['tgt_%s' % item], False
    for item in ('db_name', 'conf_fn', 'xmlrpc_port', 'db_user'):
        src_ctx[item], tgt_ctx[item] = tgt_ctx[item], False
    for item in ('db_host', 'login_user', 'login_password', 'crypt_password'):
        if tgt_ctx.get(item):
            src_ctx[item] = tgt_ctx[item]
    return src_ctx, tgt_ctx


def prepare_config_file(ctx, src_config, ou_ver_path=None, paths=None):
    if ou_ver_path:
        src_lconf = 'openupgrade.conf'
        full_lconf = os.path.join(ou_ver_path, src_lconf)
    else:
        src_lconf = clodoo.build_odoo_param(
            'LCONFN', odoo_vid=ctx['src_vid'], multi=True)
        full_lconf = os.path.join(os.path.expanduser('~'),
                                  src_lconf)
        for fn in ('.openerp_serverrc', '.odoorc'):
            tmp_lconf = os.path.join(os.path.expanduser('~'), fn)
            if os.path.isfile(tmp_lconf):
                os.remove(tmp_lconf)
    if paths:
        src_config.set('options', 'addons_path', ','.join(paths))
    if ou_ver_path:
        src_config.set('options', 'root_path', ou_ver_path)
    src_config.write(open(full_lconf, 'w+'))
    src_config.read(full_lconf)
    return full_lconf


def hard_clean_module(ctx, module_name):
    def drop_data_table(ctx, model, module_name, coln=None, id=None):
        coln = coln or 'module'
        if id:
            query = "delete from %s where %s=%d" % (model, coln, id)
        else:
            query = "delete from %s where %s='%s'" % (model, coln, module_name)
        recs = exec_sql(ctx, query)

    query = "select id,name,state from ir_module_module where name='%s'" % \
            module_name
    recs = exec_sql(ctx, query, response=True)
    if not len(recs):
        return
    state = recs[0][2]
    id = recs[0][0]
    if state == 'installed':
        return
    drop_data_table(ctx, 'ir_model_data', module_name)
    drop_data_table(ctx, 'ir_module_module_dependency',
                    module_name, coln='module_id', id=id)
    drop_data_table(ctx, 'ir_translation', module_name)
    set_uninstalled_by_sql(ctx, [_b(module_name)])


def fix_bug_pre(src_ctx, tgt_ctx, src_full_lconf, src_paths):
    saved_db, src_ctx['db_name'] = src_ctx['db_name'], tgt_ctx['db_name']
    if (src_ctx['src_odoo_fver'] == '7.0' and
            tgt_ctx['tgt_odoo_fver'] == '8.0'):
        query = '''update ir_ui_view
                set arch=REGEXP_REPLACE(arch, '<field name="menu_id".*/>', '')
                where model='res.users' and
                      arch like '%<field name=_menu_id_%';'''
        exec_sql(src_ctx, query)
    elif (src_ctx['src_odoo_fver'] == '8.0' and
            tgt_ctx['tgt_odoo_fver'] == '9.0'):
        if 'account_payment' in src_ctx['src_module_list']:
            sts = clodoo.act_install_modules(
                src_ctx, module_list=['account_banking_payment_export'])
    src_ctx['db_name'] = saved_db


def fix_bug_post(src_ctx, tgt_ctx, tgt_full_lconf, tgt_paths):
    if (src_ctx['src_odoo_fver'] == '7.0' and
            tgt_ctx['tgt_odoo_fver'] == '8.0'):
        pass


def migrate_odoo(src_ctx, tgt_ctx, src_config, tgt_config, phase=None):

    def get_wrong_modules(ctx, bad_module_list=None):
        if src_ctx['dry_run']:
            return []
        if bad_module_list:
            if len(bad_module_list) == 1:
                query = '''select id,name,state from ir_module_module
                           where state not in 
                           ('installed', 'uninstalled', 'uninstallable') and
                           name = '%s';''' % bad_module_list[0]
            else:
                query = '''select id,name,state from ir_module_module
                           where state not in 
                           ('installed', 'uninstalled', 'uninstallable') and
                           name in (%s);''' % (
                               "'%s'" % "','".join(bad_module_list))

        else:
            query = '''select id,name,state from ir_module_module
                       where state not in
                       ('installed', 'uninstalled', 'uninstallable');'''
        rows = exec_sql(ctx, query, response=True)
        wrong_list = []
        for row in rows:
            if not bad_module_list or row[1] not in bad_module_list:
                wrong_list.append(row[1])
        return wrong_list

    def run_openupgrade(tgt_ctx, ou_ver_path, tgt_full_lconf):
        oupath_script = False
        for p in ('', 'odoo', 'openerp', 'server'):
            if oupath_script:
                break
            for n in ('odoo-bin', 'openerp-server'):
                if p:
                    script = os.path.join(ou_ver_path, p, n)
                else:
                    script = os.path.join(ou_ver_path, n)
                if os.path.isfile(script):
                    oupath_script = script
                    break
        if src_ctx['no_venv']:
            sts = run_traced(oupath_script,
                             '-c', tgt_full_lconf,
                             '-d', tgt_ctx['db_name'],
                             '-u', 'all',
                             '--stop-after-init',
                             '--no-xmlrpc',
                             '--logfile=%s' % tgt_ctx['logfile'])
        else:
            script = os.path.join(ou_ver_path, 'migrate.sh')
            fd = open(script, 'w')
            fd.write('cd %s\n' % tgt_ctx['venv_oupath'])
            fd.write(b'source ./bin/activate\n')
            fd.write(b'%s -c %s -d %s -u all --stop-after-init --no-xmlrpc'
                     b' --logfile=%s\n' % (
                         oupath_script, tgt_full_lconf,
                         tgt_ctx['db_name'],
                         tgt_ctx['logfile']))
            fd.write(b'sts=$?\n')
            fd.write(b'deactivate\n')
            fd.write(b'exit $sts\n')
            fd.close()
            os.chmod(script, 0744)
            sts = 0
            if not src_ctx['dry_run']:
                sts = os.system(script)
        if sts:
            os0.wlog('*** Return code %d ***')
        elif not src_ctx['dry_run']:
            time.sleep(5)

    phase = phase or 2
    tgt_saved_fconf = tgt_ctx['conf_fn']
    src_full_lconf = prepare_config_file(src_ctx, src_config)
    if (src_ctx['src_vid'] == src_ctx['from_branch'] and
            get_wrong_modules(src_ctx)):
        if phase == 1:
            os0.wlog('*** Unstable installation ***')
        else:
            os0.wlog('*** Unstable installation: try to correct errors ***')
            run_odoo_alltest(src_ctx['tgt_vid'], src_full_lconf,
                             src_ctx['db_name'], src_ctx['logfile'])
            bad_modules = get_wrong_modules(src_ctx)
            if bad_modules:
                os0.wlog('*** Unstable installation due to %s ***' % bad_modules)
                os0.wlog('*** MIGRATION STOPPED ***')
                sys.exit(1)

    src_paths = config_get_list(src_config, 'addons_path')
    tgt_paths = config_get_list(tgt_config, 'addons_path')
    os0.wlog('addons_path=%s' % src_paths)
    if phase > 1 or src_ctx['src_vid'] == src_ctx['from_branch']:
        os0.wlog('Test connection to source db %s' % src_ctx['db_name'])
        uid, src_ctx = clodoo.oerp_set_env(
            ctx=src_ctx, confn=src_full_lconf, db=src_ctx['db_name'])
        # FIX oerp_set_env change dry_run
        src_ctx['dry_run'] = tgt_ctx['dry_run']
        if phase > 1:
            if (src_ctx['opt_safe'] and
                    src_ctx['src_vid'] == src_ctx['from_branch']):
                clodoo.act_check_config(src_ctx)
            if (src_ctx['uninstall_modules'] and
                    src_ctx['src_vid'] == src_ctx['from_branch']):
                for module in src_ctx['uninstall_modules'].split(','):
                    drop_module(src_ctx, module, force=True)
        src_ctx['src_module_list'] = odoo_dependencies(
            src_ctx, 'mod', src_ctx['db_name'], src_full_lconf, src_paths,
            src_ctx['src_odoo_fver'])
        os0.wlog('Module list to migrate=%s' % src_ctx['src_module_list'])
    if not src_ctx.get('original_module_list'):
        src_ctx['original_module_list'] = src_ctx['src_module_list']
    src_all_module_list = odoo_dependencies(
        src_ctx, 'mod', False, False, src_paths,
        src_ctx['src_odoo_fver'])
    tgt_all_module_list = odoo_dependencies(
        tgt_ctx, 'mod', False, False, tgt_paths,
        tgt_ctx['tgt_odoo_fver'])
    src_ctx['tnl_module_list'], bad_module_list = \
        do_tnl_module_list(src_ctx,
                           src_ctx['src_module_list'],
                           src_ctx['src_odoo_fver'],
                           tgt_ctx['tgt_odoo_fver'],
                           tgt_all_module_list,
                           pure=True)
    os0.wlog(
        'Translated list after migration=%s' % src_ctx['tnl_module_list'])
    full_tnl_module_list = odoo_dependencies(
        tgt_ctx, 'dep', False, False, tgt_paths,
        tgt_ctx['src_odoo_fver'], matches=src_ctx['tnl_module_list'])
    os0.wlog(
        'Target list with dependencies=%s' % full_tnl_module_list)
    os0.wlog(
        'Not avaiable modules on target=%s' % bad_module_list)
    if (bad_module_list and
            src_ctx['reducted_module_set'] and
            not src_ctx['dry_run']):
        for i,module in enumerate(bad_module_list):
            sts = drop_module(src_ctx, module)
            if sts:
                del bad_module_list[i]
    soft_uninstall_list = hard_uninstall_list = []
    if tgt_ctx['oca_migrate'] and tgt_ctx['tgt_odoo_ver'] < 10:
        ou_ver_path = load_openupgrade(tgt_ctx, tgt_ctx['tgt_odoo_fver'])
        cmd = os.path.join(ou_ver_path, 'scripts', 'migrate.py')
        if src_ctx['no_venv']:
            run_traced(cmd,
                       '-C', src_full_lconf,
                       '-D', src_ctx['db_name'],
                       '-B', src_ctx['opt_oupath'],
                       '-R', tgt_ctx['tgt_odoo_fver'])
        else:
            script = os.path.join(ou_ver_path, 'migrate.sh')
            fd = open(script, 'w')
            fd.write('cd %s\n' % tgt_ctx['venv_oupath'])
            fd.write('source ./bin/activate\n')
            fd.write('%s -C %s -D %s -B %s -R %s\n' % (
                cmd, src_full_lconf,
                src_ctx['db_name'],
                src_ctx['opt_oupath'],
                tgt_ctx['tgt_odoo_fver']))
            fd.write('deactivate\n')
            fd.close()
            os.chmod(script, 0744)
            if not src_ctx['dry_run']:
                os.system(script)
        if not src_ctx['dry_run']:
            time.sleep(5)
        tmp_dbname = new_dbname(src_ctx['db_name'],
                                tgt_ctx['tgt_odoo_ver'],
                                tgt_ctx['oca_migrate'])
        if not src_ctx['dry_run']: 
            if tgt_ctx['db_name'] != tmp_dbname:
                ren_db(tmp_dbname, tgt_ctx['db_name'], src_ctx['db_user'])
            if src_ctx['db_user'] != tgt_ctx['db_user']:
                reassign_db_owner(tgt_ctx,
                                  tgt_ctx['db_name'],
                                  src_ctx['db_user'],
                                  tgt_ctx['db_user'])
        tgt_full_lconf = tgt_ctx['conf_fn']
    else:
        ou_ver_path = load_openupgrade(tgt_ctx, tgt_ctx['tgt_odoo_fver'])
        if not src_ctx['dry_run']: 
            load_openupgradelib(src_ctx, tgt_ctx['tgt_odoo_fver'])
        if tgt_ctx['upd_translation']:
            add_versioned_tnl(src_ctx, src_ctx['src_odoo_fver'],
                              tgt_ctx['tgt_odoo_fver'])
        addons_path = os.path.join(ou_ver_path, 'addons')
        if tgt_ctx['tgt_odoo_ver'] < 10:
            root_path = os.path.join(ou_ver_path, 'openerp', 'addons')
        else:
            root_path = os.path.join(ou_ver_path, 'odoo', 'addons')
        if not src_ctx['dry_run']: 
            for repo in tgt_paths:
                for name in os.listdir(repo):
                    if (os.path.isdir(os.path.join(repo, name)) and
                            not os.path.isdir(
                                os.path.join(addons_path, name)) and
                            not os.path.isdir(os.path.join(root_path, name))):
                        os.symlink(os.path.join(repo, name),
                                   os.path.join(addons_path, name))
        tgt_paths = []
        tgt_paths.insert(0, addons_path)
        tgt_paths.insert(0, root_path)
        tgt_full_lconf = prepare_config_file(tgt_ctx, tgt_config,
                                             ou_ver_path=ou_ver_path,
                                             paths=tgt_paths)
        if not src_ctx['dry_run']:
            if not copy_db(src_ctx, src_ctx['db_name'], tgt_ctx['db_name']):
                exit(1)
            fix_bug_pre(src_ctx, tgt_ctx, src_full_lconf, src_paths)
            if src_ctx['db_user'] != tgt_ctx['db_user']:
                reassign_db_owner(tgt_ctx,
                                  tgt_ctx['db_name'],
                                  src_ctx['db_user'],
                                  tgt_ctx['db_user'])
            # Some modules not available on intermediate version might be 
            # available on current target odoo version
            if tgt_ctx['try_reinstall']:
                modules_to_restore = bad_list = []
                if src_ctx['original_module_list'] != src_ctx[
                        'src_module_list']:
                    modules_to_restore, bad_list = do_tnl_module_list(
                        tgt_ctx,
                        src_ctx['original_module_list'],
                        src_ctx['from_odoo_fver'],
                        tgt_ctx['tgt_odoo_fver'],
                        tgt_all_module_list,
                        pure=True)
                    modules_to_restore = list(set(modules_to_restore) - 
                                              set(src_ctx['src_module_list']))
                    if modules_to_restore:
                        set_installed_by_sql(tgt_ctx, modules_to_restore)
            drop_session(tgt_ctx, tgt_ctx['db_name'],
                         odoo_vid=tgt_ctx['tgt_vid'])
        run_openupgrade(tgt_ctx, ou_ver_path, tgt_full_lconf)
        if not src_ctx['dry_run']:
            fix_bug_post(src_ctx, tgt_ctx, src_full_lconf, src_paths)

    # Test for not migrated modules
    tgt_ctx['conf_fn'] = tgt_saved_fconf 
    to_uninstall_list = get_wrong_modules(tgt_ctx)
    if to_uninstall_list:
        os0.wlog('*** Wrong state for modules %s ***' % to_uninstall_list)
    hard_uninstall_list = list(
        set(to_uninstall_list) & set(MODULES_2_LEAVE_BEHIND))
    soft_uninstall_list = list(
        set(to_uninstall_list) - set(hard_uninstall_list))
    if soft_uninstall_list:
        set_uninstalled_by_sql(tgt_ctx, soft_uninstall_list)
    if hard_uninstall_list:
        os0.wlog('*** Unstable DB: wrong module state %s ***' %
                 hard_uninstall_list)
    for module in hard_uninstall_list:
        os0.wlog('  ++ Hard uninstall: %s' % module)
        hard_clean_module(tgt_ctx, module)
    if soft_uninstall_list or hard_uninstall_list:
        bad_modules = list(set(soft_uninstall_list) | set(hard_uninstall_list))
        run_odoo_alltest(tgt_ctx['tgt_vid'], tgt_ctx['conf_fn'],
                         tgt_ctx['db_name'], tgt_ctx['logfile'],
                         modules=bad_modules)
    elif tgt_ctx['opt_safe'] and not src_ctx['dry_run']:
        run_odoo_alltest(tgt_ctx['tgt_vid'], tgt_ctx['conf_fn'],
                         tgt_ctx['db_name'], tgt_ctx['logfile'])
    bad_modules = get_wrong_modules(tgt_ctx)
    if bad_modules:
        os0.wlog('*** Unstable DB after clean: wrong module state %s ***' %
                 bad_modules)
        hard_uninstall_list = list(
            set(bad_modules) & set(MODULES_2_LEAVE_BEHIND))
        bad_modules = list(
            set(bad_modules) - set(MODULES_2_LEAVE_BEHIND))
        if bad_modules:
            set_uninstalled_by_sql(tgt_ctx, bad_modules)
        if hard_uninstall_list:
            for module in hard_uninstall_list:
                os0.wlog('  ++ Hard uninstall: %s' % module)
                if not src_ctx['dry_run']:
                    hard_clean_module(tgt_ctx, module)

    if not src_ctx['dry_run']:
        os0.wlog('Test connection to target db %s' % tgt_ctx['db_name'])
        uid, tgt_ctx = clodoo.oerp_set_env(
            ctx=tgt_ctx, confn=tgt_full_lconf, db=tgt_ctx['db_name'])
        # FIX oerp_set_env change dry_run
        src_ctx['dry_run'] = tgt_ctx['dry_run']

    return tgt_full_lconf


def migrate_database_pass(src_ctx, tgt_ctx, phase=None):
    phase = phase or 2
    disable_venv = False
    if phase == 1:
        saved_dry_run = src_ctx['dry_run']
        src_ctx['dry_run'] = True
        tgt_ctx['dry_run'] = src_ctx['dry_run']
    while 1:
        os0.wlog('-' * 80)
        src_ctx, tgt_ctx, src_config, tgt_config = adjust_ctx(src_ctx, tgt_ctx)
        for param in ('vid', 'odoo_fver', 'odoo_ver'):
            os0.wlog('Pass %d migration: %s from %s to %s ..' %
                 (phase, param,
                  src_ctx['src_%s' % param], tgt_ctx['tgt_%s' % param]))
        for param in ('db_name', 'conf_fn', 'xmlrpc_port', 'db_user'):
            os0.wlog('Pass %d migration: %s from %s to %s ..' %
                 (phase, param, src_ctx[param], tgt_ctx[param]))
        if phase == 1:
            if not os.path.isdir(tgt_ctx['venv_oupath']):
                os0.wlog('Directory %s not found!' % tgt_ctx['venv_oupath'])
                disable_venv = True
        elif not src_ctx['dry_run']:
            drop_db(src_ctx, tgt_ctx, tgt_ctx['db_name'],
                    new_dbname(src_ctx['db_name'],
                               tgt_ctx['tgt_odoo_ver'],
                               tgt_ctx['oca_migrate']))
        full_lconf = migrate_odoo(src_ctx, tgt_ctx,
                                  src_config, tgt_config, phase=phase)
        if tgt_ctx['tgt_odoo_ver'] >= src_ctx['final_ver']:
            if disable_venv:
                src_ctx['venv_oupath'] = src_ctx['opt_oupath']
                tgt_ctx['venv_oupath'] = src_ctx['venv_oupath']
            break
        if not src_ctx['no_venv'] and not src_ctx['dry_run']:
            venv_path = os.path.join(tgt_ctx['venv_oupath'], 'openupgrade')
            # TODO
            # if not os.path.isdir(venv_path):
            #    os.unlink(os.path.join(venv_path, ou_ver_path))
        src_ctx, tgt_ctx = shift_ctx(src_ctx, tgt_ctx, phase=phase)

    if phase == 1:
        src_ctx['dry_run'] = saved_dry_run 
        tgt_ctx['dry_run'] = src_ctx['dry_run']


def migrate_database(src_ctx, tgt_ctx):
    if src_ctx['phase_1']:
        src_ctx = init_ctx(src_ctx)
        migrate_database_pass(src_ctx, tgt_ctx, phase=1)
        for nm in ('original_module_list',):
            del src_ctx[nm]
    src_ctx = init_ctx(src_ctx)
    migrate_database_pass(src_ctx, tgt_ctx, phase=2)
    print('Database %s successfully miograted into %s' % (
        src_ctx['from_dbname'], tgt_ctx['db_name']))


def parse_ctx(src_ctx):
    global DEF_CONF
    if not src_ctx['from_branch'] and not src_ctx['from_confn']:
        raise KeyError('Missed original odoo version! Please use -F switch')
    elif src_ctx['from_branch']:
        src_ctx['src_odoo_fver'] = clodoo.build_odoo_param(
            'FULLVER', odoo_vid=src_ctx['from_branch'], multi=True)
        if not src_ctx['from_confn']:
            src_ctx['from_confn'] = clodoo.build_odoo_param(
                'CONFN', odoo_vid=src_ctx['from_branch'], multi=True)
    if not os.path.isfile(src_ctx['from_confn']):
        raise IOError('File %s not found' % src_ctx['from_confn'])
    if not src_ctx['from_branch']:
        src_config = ConfigParser.SafeConfigParser()
        src_config.read(src_ctx['from_confn'])
        src_ctx['src_odoo_fver'] = src_config.get('options', 'oe_version')
        src_ctx['from_branch'] = src_ctx['src_odoo_fver']
    src_ctx['src_odoo_ver'] = clodoo.build_odoo_param(
            'MAJVER', odoo_vid=src_ctx['from_branch'], multi=True)

    if not src_ctx['final_branch'] and not src_ctx['final_confn']:
        raise KeyError('Missed final odoo version! Please use -b switch')
    elif src_ctx['final_branch']:
        src_ctx['tgt_odoo_fver'] = clodoo.build_odoo_param(
            'FULLVER', odoo_vid=src_ctx['final_branch'], multi=True)
        if not src_ctx['final_confn']:
            src_ctx['final_confn'] = clodoo.build_odoo_param(
                'CONFN', odoo_vid=src_ctx['final_branch'], multi=True)
    if not os.path.isfile(src_ctx['final_confn']):
        raise IOError('File %s not found' % src_ctx['final_confn'])
    if not src_ctx['final_branch']:
        tgt_config = ConfigParser.SafeConfigParser()
        tgt_config.read(src_ctx['final_confn'])
        src_ctx['tgt_odoo_fver'] = tgt_config.get('options', 'oe_version')
        src_ctx['final_branch'] = src_ctx['tgt_odoo_fver']
    src_ctx['tgt_odoo_ver'] = clodoo.build_odoo_param(
            'MAJVER', odoo_vid=src_ctx['final_branch'], multi=True)

    if ((src_ctx['src_odoo_ver'] >= src_ctx['tgt_odoo_ver'] and
            not src_ctx['sel_model']) or
        (src_ctx['src_odoo_ver'] > src_ctx['tgt_odoo_ver'] and
            src_ctx['sel_model'])):
        raise KeyError('Final version must be greater than original version')

    if not src_ctx['opt_oupath']:
        src_ctx['opt_oupath'] = os.path.join(os.path.expanduser('~'), 'tmp')
    if not src_ctx['opt_oulpath']:
        src_ctx['opt_oulpath'] = os.path.join(src_ctx['opt_oupath'],
                                              'openupgradelib')
 
    if src_ctx['final_dbname'] and not src_ctx['from_dbname']:
        src_ctx['from_dbname'], src_ctx['final_dbname'] = \
            src_ctx['final_dbname'], '%s_2021' % src_ctx['final_dbname']
    elif not src_ctx['final_dbname'] and src_ctx['from_dbname']:
        src_ctx['final_dbname'] = '%s_2021' % src_ctx['from_dbname']
    elif not src_ctx['final_dbname'] and not src_ctx['from_dbname']:
        raise KeyError('Missed database to upgrade! Please use -d switch')

    if not src_ctx['logfn']:
        if src_ctx['oca_migrate']:
            src_ctx['logfn'] = os.path.join(src_ctx['opt_oupath'],
                                            'migrate_by_openupgrade.log')
        else:
            src_ctx['logfn'] = os.path.join(src_ctx['opt_oupath'],
                                            'migrate_odoo_db.log')
    src_ctx['logfile'] = os.path.join(src_ctx['opt_oupath'],
                                      'migrate_odoo_db-server.log')
    src_ctx['final_ver'] = src_ctx['tgt_odoo_ver']
    tgt_ctx = src_ctx.copy()
    DEF_CONF = clodoo.default_conf(src_ctx)
    return src_ctx, tgt_ctx


_DEPRECATED_MODULES = [
    ("account_analytic_analysis", "oca_moved", "contract",
        "Moved to OCA/contract"),
    ("account_analytic_plans", "oca_moved", "account_analytic_distribution",
        "Moved to OCA/account_analytic"),
    ("account_anglo_saxon", "removed"),
    ("account_bank_statement_extensions", "removed"),
    ("account_chart", "merged", "account"),
    ("account_check_writing", "renamed", "account_check_printing"),
    ("account_followup", "removed"),
    ("account_payment", "oca_moved", "account_payment_order",
        "Moved to OCA/bank-payment"),
    ("account_sequence", "removed"),
    ("analytic_contract_hr_expense", "removed"),
    ("analytic_user_function", "removed"),
    ("anglo_saxon_dropshipping", "removed"),
    ("auth_openid", "removed"),
    ("base_report_designer", "removed"),
    ("contacts", "merged", "mail"),
    ("crm_helpdesk", "removed"),
    ("crm_mass_mailing", "removed"),
    ("crm_profiling", "removed"),
    ("edi", "removed"),
    ("email_template", "merged", "mail_template"),
    ("hr_applicant_document", "removed"),
    ("hr_timesheet_invoice", "removed"),
    ("im_chat", "merged", "mail"),
    ("knowledge", "oca_moved", "knowledge", "Moved to OCA/knowledge"),
    ("l10n_be_coda", "removed"),
    ("l10n_fr_rib", "removed"),
    ("marketing_crm", "merged", "crm"),
    ("multi_company", "removed"),
    ("portal_claim", "renamed", "website_crm_claim"),
    ("portal_project", "merged", "project"),
    ("portal_project_issue", "merged", "project_issue"),
    ("procurement_jit_stock", "merged", "procurement_jit"),
    ("purchase_analytic_plans", "oca_moved", "purchase_analytic_distribution",
        "Moved to OCA/account-analytic"),
    ("purchase_double_validation", "removed"),
    ("sale_analytic_plans", "oca_moved", "sale_analytic_distribution",
        "Moved to OCA/account-analytic"),
    ("sale_journal", "removed"),
    ("share", "removed"),
    ("stock_invoice_directly", "removed"),
    ("web_api", "removed"),
    ("web_gantt", "merged", "web"),
    ("web_graph", "merged", "web"),
    ("web_kanban_sparkline", "merged", "web"),
    ("web_tests", "merged", "web"),
    ("web_tests_demo", "removed"),
    ("website_certification", "removed"),
    ("website_instantclick", "removed"),
    ("website_mail_group", "renamed", "website_mail_channel"),
    ("website_report", "merged", "report"),
]

if __name__ == "__main__":
    parser = z0lib.parseoptargs("Migrate Odoo DB",
                                "© 2019-21 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-B", "--openupgrade-branch-path",
                        help="openupgrade branch path",
                        dest="opt_oupath",
                        metavar="path")
    parser.add_argument('-b', '--branch',
                        action='store',
                        dest='final_branch',
                        metavar='version')
    parser.add_argument("-C", "--by-company",
                        action="store_true",
                        help="select only records of main company",
                        dest="by_company")
    parser.add_argument("-c", "--tgt-config",
                        help="target DB configuration file",
                        dest="final_confn",
                        metavar="file")
    parser.add_argument("-D", "--del-db-if-exist",
                        action="store_true",
                        dest="opt_del")
    parser.add_argument("-d", "--tgt-db_name",
                        help="target database name",
                        dest="final_dbname",
                        metavar="name")
    parser.add_argument("-E", "--no-venv",
                        help="disable virtualenv",
                        action='store_true',
                        dest="no_venv")
    parser.add_argument('-F', '--from-odoo-ver',
                        action='store',
                        dest='from_branch',
                        metavar="ver")
    parser.add_argument("-I", "--image",
                        help="image mode",
                        action='store_true',
                        dest="image_mode",
                        default=False)
    parser.add_argument("-i", "--ids",
                        help="ids to migrate",
                        dest="sel_ids",
                        metavar="list")
    parser.add_argument("-J", "--try-reinstall",
                        help="try to reinstall",
                        action='store_true',
                        dest="try_reinstall",
                        default=False)
    parser.add_argument("-K", "--command-file",
                        help="migration command file",
                        dest="command_file",
                        metavar="file",
                        default='./migrate_odoo.csv')
    parser.add_argument("-k", "--default-behavior",
                        help="default behavior",
                        action="store_true",
                        dest="default_behavior")
    parser.add_argument("-l", "--file-log",
                        help="log file",
                        dest="logfn",
                        metavar="file")
    parser.add_argument("-M", "--oca-migrate",
                        action="store_true",
                        dest="oca_migrate",
                        help="use OCA migrate (final version < 10.0)")
    parser.add_argument("-m", "--sel-model",
                        help="model to migrate",
                        dest="sel_model",
                        metavar="name")
    parser.add_argument('-n')
    parser.add_argument("-O", "--openupgradelib-path",
                        help="Openupgradelib path",
                        dest="opt_oulpath",
                        metavar="path")
    parser.add_argument('-q')
    parser.add_argument("-R", "--reducted-module-set",
                        action='store_true',
                        dest="reducted_module_set",
                        default=False)
    parser.add_argument("-S", "--safe-mode",
                        action="store_true",
                        dest="opt_safe",
                        help="safe mode")
    parser.add_argument("-s", "--use-synchro",
                        help="use module synchro",
                        action='store_true',
                        dest="use_synchro",
                        default=False)
    parser.add_argument("-T", "--upd-translation",
                        action='store_true',
                        dest="upd_translation",
                        default=False)
    parser.add_argument("-U", "--user",
                        help="login username",
                        dest="lgi_user",
                        metavar="username",
                        default="admin")
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument("-W", "--wep-log",
                        help="del logs before migration",
                        action='store_true',
                        dest="wep_logs",
                        default=False)
    parser.add_argument("-w", "--src-config",
                        help="source DB configuration file",
                        dest="from_confn",
                        metavar="file")
    parser.add_argument("-Y", "--uninstall-modules",
                        help="modules to uninstalla before migration",
                        dest="uninstall_modules",
                        metavar="list")
    parser.add_argument("-y", "--assume-yes",
                        help="assume yes",
                        action='store_true',
                        dest="assume_yes",
                        default=False)
    parser.add_argument("-z", "--src-db_name",
                        help="source database name",
                        dest="from_dbname",
                        metavar="name")
    parser.add_argument("-1", "--do-pass1",
                        help="exec pass 1",
                        action='store_true',
                        dest="phase_1")

    src_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    src_ctx, tgt_ctx = parse_ctx(src_ctx)
    if src_ctx['wep_logs']:
        wep_logs(src_ctx)
    os0.set_tlog_file(src_ctx['logfn'], echo=True)
    os0.wlog('=' * 80)
    os0.wlog("Migration database %s beginning ...", __version__)
    if src_ctx['sel_model']:
        migrate_sel_tables(src_ctx, tgt_ctx)
    else:
        migrate_database(src_ctx, tgt_ctx)
