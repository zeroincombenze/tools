#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. (http://www.shs-av.com/)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""@mainpage
Massive operations on Zeroincombenze® / Odoo databases
========================================================

Clodoo is a tool can do massive operation on 1 or more Odoo database base on
different Odoo versions. Main operation are:

- create consistent database to run tests
- repeat consistent action on many db with same or different Odoo version
- repeat above actions on every new database

It is called by bash console, there is no funcional web/GUI interface.

It requires OERPLIB and ODOORPC.

Tool syntax:

    $ usage: clodoo.py [-h] [-A actions] [-b version] [-c file] [-d regex] [-D]
                 [-l iso_lang] [-n] [-p dir] [-P password] [-q] [-r port]
                 [-U username] [-u list] [-v] [-V] [-x]

    optional arguments:
      -h, --help            show this help message and exit
      -A actions, --action-to-do actions
                            action to do (use help to dir)
      -b version, --odoo-branch version
                            talk server Odoo version
      -c file, --config file
                            configuration command file
      -d regex, --dbfilter regex
                            DB filter
      -D, --with-demo       create db with demo data
      -l iso_lang, --lang iso_lang
                            user language
      -n, --dry-run         test execution mode
      -p dir, --data-path dir
                            Import file path
      -P password, --pwd password
                            login password
      -q, --quiet           run silently
      -r port, --xmlrpc-port port
                            xmlrpc port
      -U username, --user username
                            login username
      -u list, --upgrade-modules list
                            Module list to upgrade
      -v, --verbose         run with debugging output
      -V, --version         show program's version number and exit
      -x, --exit-on-error   exit on error



Import_file
-----------

Import file loads data from a csv file into DB. This action works as standard
Odoo but has some enhanced features.
Field value may be:
- external identifier, format module.name (as Odoo standard)
  i.e. 'base.main_company'
- text with macros, format ${macro} (no Odoo standard), dictionary passed
  i.e. '${company_id}'
  text may contains one or more macros
- text with DB extraction, format ${model:values} (w/o company, no Odoo std)
  i.e. '${res.company:your company}'
  data is searched by name
- text with DB extraction, format ${model::values} (with company, no Odoo std)
  i.e. '${res.partner::Odoo SA}'
  data is searched by name, company from ctx['company_id']
- text with DB extraction, format ${model(params):values} (w/o company)
  i.e. '${res.company(zip):1010}'
  data is searched by param(s)
- text with function, format ${function(params)::values} (add company)
  i.e. '${res.partner(zip)::1010}'
  data is searched by param(s), company from ctx['company_id']
- full text function, format ${function[field](params):values} (w/o company)
  full text function, format ${function[field](params)::values} (add company)
  i.e. '${res.partner[name](zip)::1010}'
  data is searched as in above function;
  returned value is not id but `field`
- crypted data, begins with $1$!
  i.e '$1$!abc'
- expression, begin with = (deprecated)
- odoo multiversion text, format model.constant.0 (in model replace '.' by '_')
  i.e. 'res_groups.SALES.0'
- odoo versioned value, format model.value.majversion
  i.e. 'res_groups.Sales.8'

Predefines macros (in ctx):
company_id     default company_id
company_name   name of default company (if company_id not valid)
country_code   ISO-3166 default country (see def_country_id)
customer-supplier if field contains 'customer' or 'client' set customer=True
                  if it contains 'supplier' or 'vendor' or 'fornitore'
                      set supplier=True
def_country_id default country id (from company or from user)
def_email      default mail; format: {username}{majversion}@example.com
full_model     load all field values, even if not in csv
header_id      id of header when import header/details files
lang           language, format lang_COUNTRY, i.e. it_IT (default en_US)
name2          if present, is merged with name
name_first     if present with name last, are merged to compose name
name_last      if present with name first, are merged to compose name
street2        if present and just numeric, is merged with street
zeroadm_mail   default user mail from config file or <def_mail> if -D switch
zeroadm_login  default admin username from config file
oneadm_mail    default user2 mail from config file or <def_mail> if -D switch
oneadm_login   default admin2 username from config file
botadm_mail    default bot user mail from config file or <def_mail> if -D switch
botadm_login   default bot username from config file
_today         date.today()
_current_year  date.today().year
_last_year'    date.today().year - 1
TNL_DICT       dictionary with field translation, format csv_name: field_name;
               i.e {'partner_name': 'name'}
               or csv_position: field_name, i.e. {'0': 'name'}
TNL_VALUE      dictionary with value translation for field;
               format is field_name: {csv_value: field_value, ...}
               i.e. {'country': {'Inghilterra': 'Regno Unito'}}
               special value '$BOOLEAN' return True or False
DEFAULT        dictionary with default value, format field_name: value
EXPR           evaluate value from expression, format csv_name: expression;
               expression can refer to other fields of csv record in format
               csv[field_name]
               or other fields of record in format row[field_name]
               i.e. {'is_company': 'row["ref"] != ""'}
                    {'is_company': 'csv["CustomerRef"] != ""'}
MANDATORY      dictionary with mandatory field names


Import searches for existing data (this behavior differs from Odoo standard)
Search is based on <o_model> dictionary;
default field to search is 'name' or 'id', if passed.

File csv can contain some special fields:
db_type: select record if DB name matches db type; values are
    'D' for demo,
    'T' for test,
    'Z' for zeroincombenze production,
    'V' for VG7 customers
    'C' other customers
oe_versions: select record if matches Odoo version
    i.e  +11.0+10.0 => select record if Odoo 11.0 or 10.0
    i.e  -6.1-7.0 => select record if Odoo is not 6.1 and not 7.0
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import inspect
import os.path
import platform
import re
import sys
import time

# from builtins import *                                           # noqa: F403
from datetime import date

from future import standard_library
from past.builtins import basestring

# try:
#     import odoorpc
# except ImportError:
#     raise ImportError("Package odoorpc not found!")
# if sys.version_info[0] == 2:
#     try:
#         import oerplib
#     except ImportError:
#         raise ImportError("Package oerplib not found!")
# else:
#     try:
#         import oerplib3 as oerplib
#     except ImportError:
#         raise ImportError("Package oerplib3 not found!")

# from passlib.context import CryptContext
# from os0 import os0
from python_plus import _c, _u, str2bool

try:
    from clodoo.clodoocore import browseL8              # noqa: F401
    from clodoo.clodoocore import build_model_struct    # noqa: F401
    from clodoo.clodoocore import connectL8             # noqa: F401
    from clodoo.clodoocore import execute_action_L8     # noqa: F401
    from clodoo.clodoocore import extr_table_generic    # noqa: F401
    from clodoo.clodoocore import extract_vals_from_rec  # noqa: F401
    from clodoo.clodoocore import get_val_from_field    # noqa: F401
    from clodoo.clodoocore import import_file_get_hdr   # noqa: F401
    from clodoo.clodoocore import model_has_company     # noqa: F401
    from clodoo.clodoocore import put_model_alias       # noqa: F401
    from clodoo.clodoocore import (                     # noqa: F401
        Clodoo,
        createL8,
        cvt_from_ver_2_ver,
        eval_value,
        exec_sql,
        executeL8,
        get_company_id,
        get_model_model,
        get_model_name,
        get_model_structure,
        get_query_id,
        get_res_users,
        is_required_field,
        is_valid_field,
        psql_connect,
        searchL8,
        set_some_values,
        sql_reconnect,
        unlinkL8,
        writeL8,
        create_model_object,
    )
except ImportError:
    from clodoocore import browseL8             # noqa: F401
    from clodoocore import build_model_struct   # noqa: F401
    from clodoocore import connectL8            # noqa: F401
    from clodoocore import execute_action_L8    # noqa: F401
    from clodoocore import extr_table_generic   # noqa: F401
    from clodoocore import extract_vals_from_rec  # noqa: F401
    from clodoocore import get_val_from_field   # noqa: F401
    from clodoocore import import_file_get_hdr  # noqa: F401
    from clodoocore import model_has_company    # noqa: F401
    from clodoocore import put_model_alias      # noqa: F401
    from clodoocore import (   # noqa: F401
        createL8,
        cvt_from_ver_2_ver,
        eval_value,
        exec_sql,
        executeL8,
        get_company_id,
        get_model_model,
        get_model_name,
        get_model_structure,
        get_query_id,
        get_res_users,
        is_required_field,
        is_valid_field,
        psql_connect,
        searchL8,
        set_some_values,
        sql_reconnect,
        unlinkL8,
        writeL8,
        create_model_object,
    )
try:
    from clodoo.clodoolib import init_logger    # noqa: F401
    from clodoo.clodoolib import msg_burst      # noqa: F401
    from clodoo.clodoolib import tounicode      # noqa: F401
    from clodoo.clodoolib import (
        build_odoo_param,       # noqa: F401
        crypt,
        debug_msg_log,
        decrypt,
        default_conf,
        msg_log,
        parse_args,
        read_config,
        set_base_ctx,
    )
except ImportError:
    from clodoolib import init_logger   # noqa: F401
    from clodoolib import msg_burst     # noqa: F401
    from clodoolib import tounicode     # noqa: F401
    from clodoolib import (             # noqa: F401
        build_odoo_param,
        crypt,
        debug_msg_log,
        decrypt,
        default_conf,
        msg_log,
        parse_args,
        read_config,
        set_base_ctx,
    )
try:
    from transodoo import read_stored_dict, translate_from_to
except ImportError:
    from clodoo.transodoo import read_stored_dict, translate_from_to

# TMP
from subprocess import PIPE, Popen

standard_library.install_aliases()  # noqa: E402

__version__ = "2.0.14"

# Apply for configuration file (True/False)
APPLY_CONF = True
STS_FAILED = 1
STS_SUCCESS = 0

PAY_MOVE_STS_2_DRAFT = ['posted']
INVOICES_STS_2_DRAFT = ['open', 'paid']
STATES_2_DRAFT = ['open', 'paid', 'posted']
CV_PROJECT_ID = 3504
PSQL = 'psql -Upostgres -c"%s;" %s'

db_msg_sp = 0
db_msg_stack = []


def version():
    return __version__


def writelog(xmodel, model, exclusion, all=None):
    if all:
        exclusion = [('id', '=', 0)]
    if exclusion:
        fd = open('./ir_save_table.csv', 'a')
        f = exclusion[0][0]
        if exclusion[0][1] == '!=':
            op = '='
        elif exclusion[0][1] == '=':
            op = '!='
        else:
            op = 'in'
        x = exclusion[0][2]
        line = '%s,True,%s,True,%s,"%s","%s"\n' % (xmodel, model, f, op, str(x))
        fd.write(line)
        fd.close()


def print_hdr_msg(ctx):
    ctx['level'] = 0
    msg = "====== Do massive operations V%s ======" % __version__
    msg_log(ctx, ctx['level'], msg)
    incr_lev(ctx)
    msg = "Configuration from"
    for f in ctx.get('confns'):
        msg = msg + ' ' + f
    msg_log(ctx, ctx['level'], msg)


def decr_lev(ctx):
    if 'level' in ctx:
        ctx['level'] -= 1
    else:
        ctx['level'] = 0


def incr_lev(ctx):
    if 'level' in ctx:
        ctx['level'] += 1
    else:
        ctx['level'] = 0


#############################################################################
# Connection and database
#
def open_connection(ctx):
    """Open connection to Odoo service"""
    res = connectL8(ctx)
    if isinstance(res, basestring):
        raise RuntimeError(res)  # pragma: no cover
    return res


def do_login(ctx):
    """Do a login into DB; try using more usernames and passwords"""
    user = ctx["self"].do_login()
    if not user:
        if not ctx.get('no_warning_pwd', False):
            print("!DB={}: invalid user/pwd".format(tounicode(ctx['db_name'])))
        return
    if not ctx['multi_user']:
        ctx = init_user_ctx(ctx, user)
        msg = ident_user(ctx, user.id)
        msg_log(ctx, ctx['level'], msg)
    return user


def oerp_set_env(
    confn=None,
    db=None,
    xmlrpc_port=None,
    oe_version=None,
    user=None,
    pwd=None,
    lang=None,
    ctx={},
    http_port=None,
):
    for (item, arg) in (
        ("confn", "confn"),
        ("db_name", "db"),
        ("xmlrpc_port", "xmlrpc_port"),
        ("odoo_version", "oe_version"),
        ("login_user", "user"),
        ("login_password", "pwd"),
        ("lang", "lang"),
        ("http_port", "http_port"),
    ):
        if locals()[arg]:
            ctx[item] = locals()[arg]
    open_connection(ctx)
    if ctx['no_login']:
        return False, ctx
    if ctx["user"] and hasattr(ctx["user"], "id"):
        lgiuser = ctx["user"]
    else:
        lgiuser = do_login(ctx)
    if not lgiuser:
        raise RuntimeError('Invalid user or password!')  # pragma: no cover
    uid = lgiuser.id
    ctx["_cr"] = ctx["self"]._cr
    return uid, ctx


def get_context(ctx):
    context = {}
    context['lang'] = 'en_US'
    return context


def set_msg(msg, modname, ignore_not_installed):
    sts = STS_SUCCESS
    if ignore_not_installed:
        fmt = msg
        msg = fmt % modname
    else:
        fmt = '!%s!!' % msg
        msg = fmt % modname
        sts = STS_FAILED
    return msg, sts


def init_db_ctx(ctx, db):
    """ "Clear company parameters"""
    for n in (
        'def_company_id',
        'def_company_name',
        'def_country_id',
        'user_id',
        'user_name',
        'user_partner_id',
        'user_country_id',
        'user_company_id',
        'company_id',
        'company_name',
        'company_country_id',
        'company_partner_id',
        'module_udpated',
    ):
        if n in ctx:
            del ctx[n]
    ctx['db_name'] = db
    if re.match(ctx['dbfilterd'], ctx['db_name']):
        ctx['db_type'] = "D"  # Demo
    elif re.match(ctx['dbfiltert'], ctx['db_name']):
        ctx['db_type'] = "T"  # Test
    elif re.match(ctx['dbfilterz'], ctx['db_name']):
        ctx['db_type'] = "Z"  # Zeroincombenze
    elif platform.node()[0:7] == 'vg7odoo':
        ctx['db_type'] = "V"  # VG7
    else:
        ctx['db_type'] = "C"  # Customer
    if not ctx['botadm_pwd']:
        ctx['botadm_pwd'] = 'ADM13!%s' % ctx['db_name']
    return ctx


def init_company_ctx(ctx, c_id):
    ctx['company_id'] = c_id
    company = browseL8(ctx, 'res.company', c_id)
    ctx['company_name'] = company.name
    if company.country_id:
        ctx['company_country_id'] = company.country_id.id
    else:
        ctx['company_country_id'] = 0
    ctx['company_partner_id'] = company.partner_id.id
    ctx['def_company_id'] = ctx['company_id']
    ctx['def_company_name'] = ctx['company_name']
    if ctx.get('company_country_id', 0) != 0:
        ctx['def_country_id'] = ctx['company_country_id']
        ctx['country_code'] = browseL8(ctx, 'res.country', ctx['def_country_id']).code
    return ctx


def init_user_ctx(ctx, user):
    # ctx['user_id'] = user.id
    if ctx['oe_version'] != "6.1":
        ctx['user_partner_id'] = user.partner_id.id
    ctx['user_name'] = get_res_users(ctx, user, 'name')
    ctx['def_email'] = '%s%s@example.com' % (
        user.login,
        ctx['oe_version'].split('.')[0],
    )
    ctx['user_company_id'] = user.company_id.id
    ctx['user_country_id'] = get_res_users(ctx, user, 'country_id')
    if ctx.get('def_company_id', 0) == 0:
        ctx['def_company_id'] = ctx['user_company_id']
        ctx['def_company_name'] = user.company_id.name
    return ctx


def get_dblist(ctx):
    # Interface xmlrpc and jsonrpc are the same
    if ctx['oe_version'] == '12.0':  # FIX: odoorpc wont work 12.0
        res, err = Popen(
            ['psql', '-Atl'], stdin=PIPE, stdout=PIPE, stderr=PIPE
        ).communicate()
        list = []
        for r in res.split('\n'):
            rs = r.split('|')
            if len(rs) > 2 and rs[1] == 'odoo12':
                list.append(rs[0])
        return list
    elif ctx['oe_version'] == '7.0':  # FIX
        time.sleep(1)
    return ctx['odoo_cnx'].db.list()


def get_companylist(ctx):
    return searchL8(ctx, 'res.company', [], order='id desc')


def get_userlist(ctx):
    return searchL8(ctx, 'res.users', [])


#############################################################################
# Action interface
#
def isaction(ctx, action):
    """Return true if valid action"""
    lx_act = ctx['_lx_act']
    if action == '' or action is False or action is None:
        return True
    elif get_real_actname(ctx, action) in lx_act:
        return True
    else:
        return False


def isiteraction(ctx, action):
    """Return true if interable action"""
    if action == 'per_db' or action == 'per_company' or action == 'per_user':
        return True
    else:
        return False


def lexec_name(ctx, action):
    """Return local executable function name from action"""
    act = "act_" + get_real_actname(ctx, action)
    return act


def add_on_account(acc_balance, level, code, debit, credit):
    if level not in acc_balance:
        acc_balance[level] = {}
    if code:
        if code in acc_balance[level]:
            acc_balance[level][code] += debit
            acc_balance[level][code] -= credit
        else:
            acc_balance[level][code] = debit
            acc_balance[level][code] -= credit


def action_id(lexec):
    """Return action name from local executable function name"""
    if lexec[0:4] == 'act_':
        action_name = lexec[4:]
    else:
        action_name = None
    return action_name


def do_group_action(ctx, action):
    """Do group actions (recursive)"""
    if ctx.get('dbg_mode') or 'test_unit_mode' not in ctx:
        msg = "> do_group_action(%s)" % action
        msg_log(ctx, ctx['level'] + 1, msg)
    conf_obj = ctx['_conf_obj']
    sts = STS_SUCCESS
    if conf_obj.has_option(get_real_actname(ctx, action), 'actions'):
        # Local environment for group actions
        lctx = create_local_parms(ctx, action)
        if not lctx['actions']:
            return STS_FAILED
        incr_lev(ctx)
        actions = lctx['actions'].split(',')
        for act in actions:
            if isaction(lctx, act):
                if act == '' or act is False or act is None:
                    break
                elif act == action:
                    msg = "Recursive actions " + act
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
                    break
                sts = do_single_action(lctx, act)
                if sts == STS_SUCCESS and 'header_id' in lctx:
                    ctx['header_id'] = lctx['header_id']
            else:
                msg = "Invalid action " + act
                msg_log(ctx, ctx['level'] + 1, msg)
                sts = STS_FAILED
                break
        decr_lev(ctx)
    else:
        msg = "Undefined action"
        msg_log(ctx, ctx['level'] + 1, msg)
        sts = STS_FAILED
    return sts


def do_single_action(ctx, action):
    """Do single action (recursive)"""
    if isaction(ctx, action):
        if action == '' or action is False or action is None:
            return STS_SUCCESS
        if ctx.get('dbg_mode'):
            msg = "> do_single_action(%s)" % action
            msg_log(ctx, ctx['level'] + 1, msg)
        if ctx.get('db_name', '') == 'auto':
            if action not in ("help", "list_actions", "show_params", "new_db"):
                ctx['db_name'] = get_dbname(ctx, action)
                lgiuser = do_login(ctx)
                if not lgiuser:
                    action = 'unit_test'
        act = lexec_name(ctx, action)
        if act in list(globals()):
            if action in (
                'install_modules',
                'upgrade_modules',
                'uninstall_modules',
            ) and not ctx.get('module_udpated', False):
                globals()[lexec_name(ctx, 'update_modules')](ctx)
                ctx['module_udpated'] = True
            return globals()[act](ctx)
        else:
            return do_group_action(ctx, action)
    else:
        return STS_FAILED


def do_actions(ctx):
    """Do actions (recursive)"""
    actions = ctx['actions']
    if not actions:
        return STS_FAILED
    if ctx['dbg_mode']:
        msg = "> do_actions(%s)" % actions
        msg_log(ctx, ctx['level'] + 1, msg)
    actions = actions.split(',')
    sts = STS_SUCCESS
    if len(actions) > 0:
        act = actions[0]
        actions = actions[1:]
    else:
        act = None
    while act:
        if isaction(ctx, act):
            if isiteraction(ctx, act):
                incr_lev(ctx)
                if act == 'per_db':
                    ctx['multi_user'] = multiuser(ctx, actions)
                ctx['actions'] = ','.join(actions)
                if act == 'per_db' and 'actions_db' in ctx:
                    del ctx['actions_db']
                if act == 'per_company' and 'actions_mc' in ctx:
                    del ctx['actions_mc']
                if act == 'per_user' and 'actions_uu' in ctx:
                    del ctx['actions_uu']
                sts = do_single_action(ctx, act)
                if 'actions' in ctx:
                    del ctx['actions']
                actions = []
                decr_lev(ctx)
            else:
                sts = do_single_action(ctx, act)
        else:
            sts = STS_FAILED
        if sts == STS_SUCCESS and len(actions) > 0:
            act = actions[0]
            actions = actions[1:]
        else:
            act = None
    return sts


def create_local_parms(ctx, act):
    """Create local params dictionary"""
    action = get_real_actname(ctx, act)
    conf_obj = ctx['_conf_obj']
    lctx = ctx.copy()
    for p in (
        'actions',
        'install_modules',
        'uninstall_modules',
        'upgrade_modules',
        'purge_modules',
        'data_selection',
        'modules_2_manage',
    ):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        else:
            lctx[p] = False
    for p in (
        'model',
        'model_code',
        'model_name',
        'model_action',
        'model_keyids',
        'filename',
        'hide_cid',
        'alias_model2',
        'alias_field',
        'modelA',
        'modelA_code',
        'modelA_name',
        'modelA_action',
        'modelA_keyids',
        'aliasA_model2',
        'aliasA_field',
        'modelB',
        'modelB_code',
        'modelB_name',
        'modelB_action',
        'modelB_keyids',
        'aliasB_model2',
        'aliasB_field',
        'hideB_cid',
    ):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        elif p in lctx:
            del lctx[p]
    DEFDCT = default_conf(lctx)
    for p in ('lang', 'dbfilter', 'companyfilter', 'userfilter', 'chart_of_account'):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            pv = conf_obj.get(action, p)
            if pv != DEFDCT[p]:
                lctx[p] = pv
    for p in (
        'install_modules',
        'uninstall_modules',
        'purge_modules',
        'actions',
        'hide_cid',
    ):
        pv = get_param_ver(ctx, p)
        if pv in lctx:
            lctx[pv] = str2bool(lctx[pv], lctx[pv])
        elif p in lctx:
            lctx[p] = str2bool(lctx[p], lctx[p])
    return lctx


def ident_db(ctx, db):
    db_name = get_dbname(ctx, '')
    msg = "DB=" + db + " [" + ctx.get('db_type', '') + "]"
    if db_name != db:
        msg = msg + " - default " + db_name
    return msg


def ident_company(ctx, c_id):
    msg = "Company {:>3})\t'{}'".format(c_id, tounicode(ctx.get('company_name', '')))
    return msg


def ident_user(ctx, u_id):
    user = browseL8(ctx, 'res.users', u_id)
    msg = "DB=%-24.24s uid=%-3d user=%-16.16s" " email=%-24.24s company=%-24.24s" % (
        tounicode(ctx['db_name']),
        u_id,
        tounicode(user.login),
        # tounicode(ctx['user_name']),
        tounicode(get_res_users(ctx, user, 'email')),
        tounicode(user.company_id.name),
    )
    return msg


def get_data_selection(ctx):
    if not ctx['data_selection'] or ctx['data_selection'] == 'all':
        ctx['data_selection'] = (
            'account_move,sale,purchase,project,mail,crm,'
            'inventory,marketing,hr,analytic,sequence'
        )
    return ctx['data_selection'].split(',')


def env_ref(ctx, xref):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        ids = searchL8(
            ctx, 'ir.model.data', [('module', '=', xrefs[0]), ('name', '=', xrefs[1])]
        )
        if ids:
            return browseL8(ctx, 'ir.model.data', ids[0]).res_id
    return False


#############################################################################
# Public actions
#
def act_help(ctx):
    print('%s' % ','.join(sorted(ctx['_lx_act'])))
    return STS_SUCCESS


def act_list_actions(ctx):
    """List avaiable actions and doc"""
    for act in sorted(ctx['_lx_act']):
        print("- %s: %s" % (act, globals()['act_%s' % act].__doc__))
    return STS_SUCCESS


def act_show_params(ctx):
    """Show system params; no username required"""
    if ctx['dbg_mode']:
        pwd = input('password ')
    else:
        pwd = False
    print("- hostname/port = %s:%s " % (ctx['db_host'], ctx['db_port']))
    print("- protocol      = %s " % ctx['svc_protocol'])
    print("- xmlrpc_port   = %s " % ctx['xmlrpc_port'])
    print("- odoo version  = %s " % ctx['oe_version'])
    if pwd:
        print("- password      = %s " % crypt(pwd))
    return STS_SUCCESS


def act_list_db(ctx):
    """List DBs to connect; no username required"""
    dblist = get_dblist(ctx)
    for db in sorted(dblist):
        ctx = init_db_ctx(ctx, db)
        sts = act_echo_db(ctx)
    return sts


def act_echo_db(ctx):
    """Show current DB name"""
    if not ctx['quiet_mode']:
        msg = ident_db(ctx, ctx['db_name'])
        ident = ' ' * ctx['level']
        print(" %s%s" % (ident, msg))
    return STS_SUCCESS


def act_show_db_params(ctx):
    """Show current DB name and tye"""
    ident = ' ' * ctx['level']
    print("%s- DB name       = %s " % (ident, ctx.get('db_name', "")))
    print("%s- DB type       = %s " % (ident, ctx.get('db_type', "")))
    return STS_SUCCESS


def act_list_companies(ctx):
    """List companies of current DB"""
    company_ids = get_companylist(ctx)
    for c_id in company_ids:
        ctx = init_company_ctx(ctx, c_id)
        sts = act_echo_company(ctx)
    return sts


def act_echo_company(ctx):
    """Show current company name"""
    if not ctx['quiet_mode']:
        c_id = ctx['company_id']
        msg = ident_company(ctx, c_id)
        ident = ' ' * ctx['level']
        print(" %s%s" % (ident, msg))
    return STS_SUCCESS


def act_show_company_params(ctx):
    """Show current company name, country and partner"""
    if not ctx.get('company_id'):
        init_company_ctx(ctx, get_company_id(ctx))
    ident = ' ' * ctx['level']
    print("%s- company_id    = %d " % (ident, ctx.get('company_id', 0)))
    print("%s- company name  = %s " % (ident, ctx.get('company_name', "")))
    print("%s- c. country_id = %d " % (ident, ctx.get('company_country_id', 0)))
    print("%s- c. partner_id = %d " % (ident, ctx.get('company_partner_id', 0)))
    return STS_SUCCESS


def act_list_users(ctx):
    """List users of current DB"""
    user_ids = get_userlist(ctx)
    for u_id in user_ids:
        user = browseL8(ctx, 'res.users', u_id)
        ctx = init_user_ctx(ctx, user)
        sts = act_echo_user(ctx)
    return sts


def act_echo_user(ctx):
    """Show current username"""
    if not ctx['quiet_mode']:
        u_id = ctx['user_id']
        msg = ident_user(ctx, u_id)
        ident = ' ' * ctx['level']
        if 'test_unit_mode' not in ctx:
            print(" %s%s" % (ident, msg))
    return STS_SUCCESS


def act_show_user_params(ctx):
    """Show current username, partner, country and def company"""
    ident = ' ' * ctx['level']
    print("%s- user_id       = %d " % (ident, ctx.get('user_id', 0)))
    print("%s- user name     = %s " % (ident, ctx.get('user_name', "")))
    print("%s- u. partner_id = %d " % (ident, ctx.get('user_partner_id', 0)))
    print("%s- u. country_id = %d " % (ident, ctx.get('user_country_id', 0)))
    print("%s- u. company_id = %d " % (ident, ctx.get('user_company_id', 0)))
    return STS_SUCCESS


def act_unit_test(ctx):
    """This function does nothing, it acts just for unit test"""
    msg_log(ctx, ctx.get('level', 0), globals()[inspect.stack()[0][3]].__doc__)
    return STS_SUCCESS


def act_per_db(ctx):
    """Iter action on DBs"""
    dblist = get_dblist(ctx)
    if 'actions_db' in ctx:
        del ctx['actions_db']
    saved_actions = ctx['actions']
    if ctx['dbg_mode']:
        msg = "> per_db(%s =~ %s)" % (dblist, ctx['dbfilter'])
        msg_log(ctx, ctx['level'] + 1, msg)
    sts = STS_SUCCESS
    db_ctr = 0
    for db in sorted(dblist):
        if re.match(ctx['dbfilter'], db):
            ctx = init_db_ctx(ctx, db)
            msg = ident_db(ctx, db)
            msg_log(ctx, ctx['level'], msg)
            if ctx['dbtypefilter']:
                if ctx['db_type'] != ctx['dbtypefilter']:
                    msg = "DB skipped by invalid db_type"
                    debug_msg_log(ctx, ctx['level'] + 1, msg)
                    continue
            lgiuser = do_login(ctx)
            if lgiuser:
                db_ctr += 1
                ctx['actions'] = saved_actions
                sts = do_actions(ctx)
            else:
                sts = STS_FAILED
            if sts != STS_SUCCESS:
                break
    if db_ctr == 0:
        msg = "No DB matches"
        msg_log(ctx, ctx['level'], msg)
        sts = STS_FAILED
    return sts


def act_per_company(ctx):
    """iter on companies"""
    if 'actions_mc' in ctx:
        del ctx['actions_mc']
    company_ids = get_companylist(ctx)
    saved_actions = ctx['actions']
    if ctx['dbg_mode']:
        msg = "> per_company(%s =~ %s)" % (company_ids, ctx['companyfilter'])
        msg_log(ctx, ctx['level'] + 1, msg)
    sts = STS_SUCCESS
    for c_id in company_ids:
        company = browseL8(ctx, 'res.company', c_id)
        if re.match(ctx['companyfilter'], company.name):
            ctx = init_company_ctx(ctx, c_id)
            msg = ident_company(ctx, c_id)
            msg_log(ctx, ctx['level'], msg)
            ctx['actions'] = saved_actions
            sts = do_actions(ctx)
            if sts != STS_SUCCESS:
                if ctx['dbg_mode']:
                    msg = "> break action(per_company)"
                    msg_log(ctx, ctx['level'] + 1, msg)
                break
    return sts


def act_per_user(ctx):
    """iter on companies"""
    if 'actions_uu' in ctx:
        del ctx['actions_uu']
    user_ids = get_userlist(ctx)
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for u_id in user_ids:
        user = browseL8(ctx, 'res.users', u_id)
        if re.match(ctx['userfilter'], user.name):
            ctx = init_user_ctx(ctx, user)
            msg = ident_user(ctx, u_id)
            msg_log(ctx, ctx['level'], msg)
            ctx['actions'] = saved_actions
            sts = do_actions(ctx)
            ctx['def_company_id'] = ctx['company_id']
            ctx['def_company_name'] = ctx['company_name']
            if ctx.get('company_country_id', 0) != 0:
                ctx['def_country_id'] = ctx['company_country_id']
                ctx['country_code'] = browseL8(
                    ctx, 'res.country', ctx['def_country_id']
                ).code
            if sts != STS_SUCCESS:
                break
    return sts


def act_execute(ctx):
    sts = STS_SUCCESS
    o_model = build_model_struct(ctx)
    model = get_model_model(ctx, o_model)
    if (
        not o_model.get('model')
        or not o_model.get('model_action')
        or not o_model.get('model_keyids')
    ):
        msg = 'Excecute w/o model or key'
        msg_log(ctx, ctx['level'] + 1, msg)
        sts = STS_FAILED
    else:
        where = []
        model_name = get_model_name(ctx, o_model)
        if model_name:
            where.append([model_name, 'like', o_model['model_keyids']])
            ids = searchL8(ctx, model, where)
        else:
            ids = [o_model['model_keyids']]
        if (
            model == 'account.move'
            and o_model['model_action'] == 'button_validate'
            and ctx['majver'] >= 10
        ):
            o_model['model_action'] = 'post'
        try:
            executeL8(ctx, model, o_model['model_action'], ids)
        except BaseException:
            msg = 'Excecute (%s, %s, %s) Failed!' % (
                model,
                o_model['model_action'],
                str(ids),
            )
            msg_log(ctx, ctx['level'] + 1, msg)
            sts = STS_FAILED
    return sts


def upd_del_in_journal(ctx, journals, value=None):
    """Before set invoices to draft, invoice has to set in cancelled state.
    To do this, journal has to be enabled
    @param journals: journal list to enable update_posted
    """
    value = value if isinstance(value, bool) else True
    if len(journals):
        vals = {'update_posted': value}
        try:
            msg = "Journals %s: update_posted=%s " % (str(journals), value)
            msg_log(ctx, ctx['level'], msg)
            writeL8(ctx, 'account.journal', journals, vals)
        except BaseException:
            msg = "Cannot update journals %s" % str(journals)
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def act_check_xid(ctx):
    if not ctx['dry_run']:
        model = 'ir.model.data'
        ids = searchL8(ctx, model, [])
        for i, id in enumerate(ids):
            xref = browseL8(ctx, model, id)
            msg_burst(ctx['level'] + 1, 'xreference', i, len(ids))
            try:
                browseL8(ctx, xref.model, xref.res_id)
            except BaseException:
                print('!! Invalid external reference %s.%s' % (xref.module, xref.name))
                unlinkL8(ctx, model, id)
    return STS_SUCCESS


def act_ena_del_in_journal(ctx):
    """Enable delete flag of journals"""
    msg_log(ctx, ctx['level'], globals()[inspect.stack()[0][3]].__doc__)
    model = 'account.journal'
    return upd_del_in_journal(
        ctx, searchL8(ctx, model, [('update_posted', '=', False)])
    )


def act_dis_del_in_journal(ctx):
    """Disable delete flag of journals"""
    msg_log(ctx, ctx['level'], globals()[inspect.stack()[0][3]].__doc__)
    model = 'account.journal'
    return upd_del_in_journal(
        ctx, searchL8(ctx, model, [('update_posted', '=', True)]), value=False
    )


def append_2_where(model, code, op, value, where, ctx):
    where.append((code, op, value))
    return where


def build_where(model, hide_cid, exclusion, ctx):
    where = []
    if not hide_cid and 'company_id' in ctx:
        company_id = ctx['company_id']
        where = append_2_where(model, 'company_id', '=', company_id, where, ctx)
    if exclusion:
        for rule in exclusion:
            code = rule[0]
            op = rule[1]
            value = rule[2]
            where = append_2_where(model, code, op, value, where, ctx)
    return where


def sql_where(code, op, value):
    if isinstance(value, list):
        query = "%s %s (%s)" % (code, op, value)
    else:
        query = "%s %s %s" % (code, op, value)
    return query


def build_sql_where(model, hide_cid, exclusion, where, ctx):
    query = ''
    if not hide_cid and 'company_id' in ctx:
        company_id = ctx['company_id']
        query += "company_id=%d" % company_id
    if exclusion:
        for rule in exclusion:
            code = rule[0]
            op = rule[1]
            value = rule[2]
            if query.strip():
                query += " and %s" % sql_where(code, op, value)
            else:
                query = sql_where(code, op, value)
    if where:
        if query.strip():
            query += " and %s" % where
        else:
            query = where
    if query.strip():
        query = "delete from %s where %s;" % (model.replace('.', '_'), query)
    else:
        query = "delete from %s;" % (model.replace('.', '_'))
    return query


def build_exclusion(model, records2keep, ctx):
    exclusion = None
    if model in records2keep:
        if isinstance(records2keep[model], list):
            exclusion = [('id', 'not in', records2keep[model])]
        else:
            exclusion = [('id', '!=', records2keep[model])]
    return exclusion


def workflow_model_all_records(model, hide_cid, signal, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = "Searching for records to execute workflow in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(model, hide_cid, exclusion, ctx)
    record_ids = searchL8(ctx, model, where)
    if not ctx['dry_run'] and len(record_ids) > 0:
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Upstate ", move_ctr, num_moves)
            move_ctr += 1
            try:
                ctx['odoo_session'].exec_workflow(model, signal, record_id)
            except BaseException:
                msg = "Workflow of %s.%d do not executed" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def setstate_model_all_records(
    model, hide_cid, field_name, new_value, ctx, exclusion=None
):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = "Searching for records to update status in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(model, hide_cid, exclusion, ctx)
    if is_valid_field(ctx, model, field_name):
        where = append_2_where(model, field_name, '!=', new_value, where, ctx)
    record_ids = searchL8(ctx, model, where)
    if (
        is_valid_field(ctx, model, 'state')
        and not ctx['dry_run']
        and len(record_ids) > 0
    ):
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Upstate ", move_ctr, num_moves)
            move_ctr += 1
            try:
                if (
                    model in ('purchase.order', 'sale.order')
                    and field_name == 'state'
                    and new_value == 'cancel'
                ):
                    executeL8(ctx, model, 'action_cancel', [record_id])
                elif (
                    model == 'purchase.requisition'
                    and field_name == 'state'
                    and new_value == 'cancel'
                ):
                    executeL8(ctx, model, 'tender_cancel', [record_id])
                elif (
                    model == 'procurement.order'
                    and field_name == 'state'
                    and new_value == 'cancel'
                ):
                    executeL8(ctx, model, 'cancel', [record_id])
                elif (
                    model == 'account.move'
                    and field_name == 'state'
                    and new_value == 'cancel'
                ):
                    executeL8(ctx, model, 'button_cancel', [record_id])
                elif (
                    model == 'account.voucher'
                    and field_name == 'state'
                    and new_value == 'cancel'
                ):
                    executeL8(ctx, model, 'cancel_voucher', [record_id])
                elif (
                    model == 'project.task'
                    and field_name == 'state'
                    and new_value == 'cancelled'
                ):
                    executeL8(ctx, model, 'do_cancel', [record_id])
                elif (
                    model == 'project.project'
                    and field_name == 'state'
                    and new_value == 'cancelled'
                ):
                    executeL8(ctx, model, 'set_cancel', [record_id])
                else:
                    writeL8(ctx, model, [record_id], {field_name: new_value})
            except BaseException:
                msg = "Cannot update status of %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def reactivate_model_all_records(
    model, hide_cid, field_name, sel_value, new_value, ctx, exclusion=None
):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = "Searching for records to reactivate in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(model, hide_cid, exclusion, ctx)
    if is_valid_field(ctx, model, field_name):
        where = append_2_where(model, field_name, '=', sel_value, where, ctx)
    record_ids = searchL8(ctx, model, where)
    if (
        is_valid_field(ctx, model, 'state')
        and not ctx['dry_run']
        and len(record_ids) > 0
    ):
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Reactive", move_ctr, num_moves)
            move_ctr += 1
            try:
                if (
                    model == 'project.project'
                    and field_name == 'state'
                    and sel_value == 'close'
                    and new_value == 'set_open'
                ):
                    executeL8(ctx, model, 'set_open', [record_id])
                else:
                    writeL8(ctx, model, [record_id], {field_name: new_value})
            except BaseException:
                msg = "Cannot reactivate %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def deactivate_model_all_records(model, hide_cid, ctx, exclusion=None, reverse=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    if reverse is None:
        reverse = False
    if is_valid_field(ctx, model, 'active'):
        where = build_where(model, hide_cid, exclusion, ctx)
        if reverse:
            msg = "Searching for records to reactivate in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(model, 'active', '=', False, where, ctx)

        else:
            msg = "Searching for records to cancel in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(model, 'active', '=', True, where, ctx)
        record_ids = searchL8(ctx, model, where)
        if not ctx['dry_run'] and len(record_ids) > 0:
            try:
                if reverse:
                    writeL8(ctx, model, record_ids, {'active': True})
                else:
                    writeL8(ctx, model, record_ids, {'active': False})
            except BaseException:
                if ctx['exit_onerror']:
                    sts = STS_FAILED
    decr_lev(ctx)
    return sts


def hard_del_sql(model, hide_cid, ctx, where=None, exclusion=None):
    if ctx.get('_cr'):
        query = build_sql_where(model, hide_cid, exclusion, where, ctx)
        incr_lev(ctx)
        msg = ">>>%s" % query
        msg_log(ctx, ctx['level'], msg)
        decr_lev(ctx)
        try:
            ctx['_cr'].execute(query)
        except BaseException:
            msg_log(ctx, ctx['level'], 'Error excuting sql')


def remove_model_all_records(model, hide_cid, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = "Searching for records to delete in %s" % model
    msg_log(ctx, ctx['level'], msg)
    writelog(model, model, exclusion)
    where = build_where(model, hide_cid, exclusion, ctx)
    record_ids = searchL8(ctx, model, where)
    if not ctx['dry_run'] and len(record_ids) > 0:
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Unlink  ", move_ctr, num_moves)
            move_ctr += 1
            try:
                unlinkL8(ctx, model, [record_id])
            except BaseException:
                msg = "Cannot remove %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break

        if model == 'project.project':
            hard_del_sql(
                model, hide_cid, ctx, where="state='cancelled'", exclusion=exclusion
            )
    decr_lev(ctx)
    return sts


def reset_sequence(ctx):
    sts = STS_SUCCESS
    incr_lev(ctx)
    model = 'ir.sequence'
    msg = "Reset sequence %s" % model
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        exclusion = [('company_id', '!=', 1)]
        remove_model_all_records(model, True, ctx, exclusion=exclusion)
    record_ids = searchL8(ctx, model, [])
    if not ctx['dry_run']:
        for record_id in record_ids:
            obj = browseL8(ctx, model, record_id)
            f_deleted = False
            if ctx['custom_act'] == 'cscs':
                for i in (2014, 2015, 2016, 2017, 2018, 2019, 2020):
                    x = '/' + str(i) + '/'
                    if obj.prefix and obj.prefix.find(x) > 0:
                        try:
                            unlinkL8(ctx, model, [record_id])
                            f_deleted = True
                        except BaseException:
                            msg = "Cannot remove %s.%d" % (model, record_id)
                            msg_log(ctx, ctx['level'], msg)
                            if ctx['exit_onerror']:
                                sts = STS_FAILED
                        break
                if f_deleted:
                    continue
            if obj.code != 'account.analytic.account':
                writeL8(ctx, model, [record_id], {'number_next_actual': 1})
    decr_lev(ctx)
    return sts


def reset_menuitem(ctx):
    sts = STS_SUCCESS
    incr_lev(ctx)
    model = 'ir.ui.menu'
    msg = "Reset sequence %s" % model
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        record_ids = (367, 368, 473, 495, 530, 688, 699, 725, 844, 845)
        for record_id in record_ids:
            try:
                unlinkL8(ctx, model, [record_id])
            except BaseException:
                msg = "Cannot remove %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
    decr_lev(ctx)
    return sts


def validate_models(ctx, models):
    cur_models = []
    for model in models:
        if searchL8(ctx, 'ir.model', [('model', '=', model)]):
            cur_models.append(model)
    return cur_models


#############################################################################
# Private actions
#
def multiuser(ctx, actions):
    if "per_user" in actions:
        return True
    else:
        return False


def create_zero_db(ctx):
    lgiuser = do_login(ctx)
    if not lgiuser:
        return None
    setup_model = 'zi.dbmgr.db.create.database.wizard'
    values = executeL8(ctx, setup_model, 'default_get', [])
    db_name = values['name']
    setup_id = executeL8(ctx, setup_model, 'create', values)
    executeL8(ctx, setup_model, 'execute', [setup_id], None)
    fd = open('clodoo_last.conf', 'w')
    fd.write('db_name=%s\n' % db_name)
    fd.close()
    return db_name


def get_dbname(ctx, action):
    if ctx['db_name'] == 'auto':
        if action == 'login':
            dbname = ctx['catalog_db']
        elif action == 'new_db':
            dbname = ctx['db_name']
        else:
            fd = open('clodoo_last.conf', 'r')
            line = fd.readline()
            fd.close()
            dbname = line.split('=')[1].split()[0]
    else:
        dbname = ctx['db_name']
    return dbname


def get_param_ver(ctx, param):
    param_ver = '%s_%s' % (param, ctx['oe_version'])
    return param_ver


def get_real_paramvalue(ctx, param):
    param_ver = '%s_%s' % (param, ctx['oe_version'])
    if param_ver in ctx:
        value = ctx[param_ver]
    elif param in ctx:
        value = ctx[param]
    else:
        value = False
    return value


def get_real_actname(ctx, actv):
    if isinstance(actv, basestring) and actv[-4:] in (
        '_6.1',
        '_7.0',
        '_8.0',
        '_9.0',
        '_10.0',
        '_11.0',
        '_12.0',
        '_13.0',
        '_14.0',
        '_15.0',
        '_16.0',
    ):
        if actv[-3:] == ctx['oe_version']:
            act = actv[0:-4]
        else:
            act = 'unit_test'
    else:
        act = actv
    return act


def add_external_name(ctx, o_model, row, id):
    model = get_model_model(ctx, o_model)
    if 'id' in row and row['id'] and not row['id'].isdigit():
        put_model_alias(ctx, model=model, ref=row['id'], id=id)
    if (
        o_model.get('alias_model2', '')
        and o_model.get('alias_field', '')
        and o_model['alias_field'] in row
        and row[o_model['alias_field']].find('None') < 0
    ):
        res_id = browseL8(ctx, model, id)[o_model['alias_field']].id
        put_model_alias(
            ctx,
            model=o_model['alias_model2'],
            ref=row[o_model['alias_field']],
            id=res_id,
        )


def translate_ext_names(ctx, o_model, csv, csv_obj):
    def translate_from_param(ctx, n, nm):
        values = ctx['TNL_VALUE'][nm]
        if csv[n] in values:
            row[nm] = values[csv[n]]
        elif '$BOOLEAN' in values:
            if csv[n]:
                row[nm] = values['$BOOLEAN']
            else:
                row[nm] = not values['$BOOLEAN']

    row = {}
    if not ctx.get('validated_fields'):
        ctx['validated_fields'] = []
    model = get_model_model(ctx, o_model)
    for n in csv:
        nm = translate_from_to(ctx, model, n, '7.0', ctx['oe_version'])
        if not nm:
            continue
        if n in csv_obj.fieldnames:
            ipos = csv_obj.fieldnames.index(n)
        else:
            ipos = -1
        if ctx.get('TNL_DICT') and ipos in ctx['TNL_DICT']:
            nm = ctx['TNL_DICT'][ipos] or nm
        elif ctx.get('TNL_DICT') and nm in ctx.get('TNL_DICT'):
            nm = ctx['TNL_DICT'][nm] or nm
        else:
            nm = nm.split('/')[0].split(':')[0]
        if (
            ctx['no_fvalidation']
            or nm
            in (
                'id',
                'db_type',
                'oe_versions',
                'name2',
                'name_first',
                'name_last',
                'customer-supplier',
            )
            or (len(ctx['validated_fields']) and nm in ctx['validated_fields'])
            or is_valid_field(ctx, model, nm)
        ):
            if nm in ctx.get('TNL_VALUE', ''):
                translate_from_param(ctx, n, nm)
            elif csv[n] != 'None':
                row[nm] = csv[n]
    if 'company_id' not in row and not o_model.get('hide_cid', False):
        row['company_id'] = False
    if ctx.get('MANDATORY'):
        for nm in ctx['MANDATORY']:
            if nm not in row:
                row[nm] = ''
    for nm in row.keys():
        if not row[nm] and nm in ctx.get('EXPR', ''):
            row[nm] = eval(ctx['EXPR'][nm])
        else:
            row[nm] = set_some_values(ctx, o_model, nm, row[nm], row=row)
    if 'name2' in row:
        if 'name' in row:
            row['name'] = '%s %s' % (row['name'], row['name2'])
        else:
            row['name'] = row['name2']
        del row['name2']
    if (
        'name_first' in row
        and 'name_last' in row
        and (
            not row.get('is_company', True)
            or row.get('company_type') == 'person'
            or not row.get('name')
        )
    ):
        row['name'] = '%s %s' % (row['name_last'], row['name_first'])
        del row['name_first'], row['name_last']
    if 'street2' in row and row['street2'].isdigit() and 'street' in row:
        row['street'] = '%s, %s' % (row['street'], row['street2'])
        row['street2'] = ''
    if (
        'customer-supplier' in row
        or not row.get('is_company', True)
        or row.get('company_type') == 'person'
    ):
        if 'customer' in row:
            row['customer'] = False
        if 'supplier' in row:
            row['supplier'] = False
    if 'customer-supplier' in row:
        if (
            row['customer-supplier'].lower().find('customer') >= 0
            or row['customer-supplier'].lower().find('client') >= 0
        ):
            row['customer'] = True
        if (
            row['customer-supplier'].lower().find('supplier') >= 0
            or row['customer-supplier'].lower().find('vendor') >= 0
            or row['customer-supplier'].lower().find('fornitore') >= 0
        ):
            row['supplier'] = True
        del row['customer-supplier']
    return row


def parse_in_fields(ctx, o_model, row, ids, cur_obj):
    name_new = ''
    update_header_id = True
    vals = {}
    if row.get('name'):
        name_new = row['name']
    elif row.get('code'):
        name_new = row['code']
    elif row.get('key'):
        name_new = row['key']
    for nm in row:
        if not nm or nm in (
            'id',
            'db_type',
            'oe_versions',
            'name2',
            'name_first',
            'name_last',
            'customer-supplier',
            o_model['alias_field'],
        ):
            continue
        if isinstance(row[nm], basestring):
            # if nm == o_model['alias_field']:
            #    continue
            if row[nm].find('${header_id}') >= 0:
                update_header_id = False
            row[nm] = row[nm].replace('\\n', '\n')
        val = eval_value(ctx, o_model, nm, row[nm])
        if val is not None:
            if (nm != 'fiscalcode' or val != '') and (
                len(ids) == 0 or tounicode(val) != cur_obj[nm]
            ):
                vals[nm] = tounicode(val)
        msg = "{}={}".format(nm, tounicode(val))
        debug_msg_log(ctx, ctx['level'] + 2, msg)
    return vals, update_header_id, name_new


def import_file(ctx, o_model, csv_fn):
    """Import data form file: it is like standard import
    Every field can be an expression enclose between '=${' and '}' tokens
    Any expression may be a standard macro (like def company id) or
    a query selection in format
     'model::value' -> get value id of model of current company
    or
     'model:value' -> get value id of model w/o company
    value may be an exact value or a like value
    """
    msg = "Import file " + csv_fn
    debug_msg_log(ctx, ctx['level'] + 1, msg)
    model = get_model_model(ctx, o_model)
    get_model_structure(ctx, model)
    if not ctx.get('company_id'):
        init_company_ctx(ctx, get_company_id(ctx))
    if 'company_id' in ctx:
        company_id = ctx['company_id']
    if ctx.get('full_model'):
        ctx['MANDATORY'] = extr_table_generic(ctx, model)
    csv.register_dialect(
        'odoo', delimiter=_c(','), quotechar=_c('\"'), quoting=csv.QUOTE_MINIMAL
    )
    csv_ffn = os.path.join(ctx['data_path'], csv_fn)
    if csv_ffn[-4:] == '.csv':
        ver_csv = '%s_%s%s' % (csv_ffn[0:-4], ctx['oe_version'], csv_ffn[-4:])
    if os.path.isfile(ver_csv):
        csv_ffn = ver_csv
    if not os.path.isfile(csv_ffn):
        csv_ffn = csv_fn
    if os.path.isfile(csv_ffn):
        csv_fd = open(csv_ffn, 'rb')
        hdr_read = False
        csv_obj = csv.DictReader(
            csv_fd, fieldnames=[], restkey='undef_name', dialect='odoo'
        )
        for row in csv_obj:
            if not hdr_read:
                hdr_read = True
                o_model = import_file_get_hdr(ctx, o_model, csv_obj, csv_fn, row)
                msg = "Model=%s, Code=%s Name=%s NoCompany=%s" % (
                    model,
                    tounicode(o_model['code']),
                    tounicode(o_model['name']),
                    o_model.get('hide_cid', False),
                )
                debug_msg_log(ctx, ctx['level'] + 2, msg)
                if o_model['name'] and o_model['code']:
                    continue
                else:
                    msg = "!File " + csv_fn + " without key!"
                    msg_log(ctx, ctx['level'] + 1, msg)
                    break
            row = translate_ext_names(ctx, o_model, row, csv_obj)
            # Data for specific db type (i.e. just for test)
            if o_model.get('db_type', ''):
                if row[o_model['db_type']]:
                    if row[o_model['db_type']].find(ctx['db_type']) < 0:
                        msg = "Record not imported by invalid db_type"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
            if row.get('oe_versions'):
                if row['oe_versions'].find('-') >= 0:
                    if row['oe_versions'].find(ctx['oe_version']) >= 0:
                        msg = "Record not imported by invalid version"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
                elif row['oe_versions'].find('+') >= 0:
                    if row['oe_versions'].find(ctx['oe_version']) < 0:
                        msg = "Record not imported by invalid version"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
            if model == 'res.users' and 'login' in row:
                ctx['def_email'] = '%s%s@example.com' % (
                    row['login'],
                    ctx['oe_version'].split('.')[0],
                )
            if 'undef_name' in row:
                msg = "!Invalid line format!"
                msg_log(ctx, ctx['level'], msg)
                del row['undef_name']
            # Does record exist ?
            saved_hide_id = o_model['hide_id']
            if o_model['repl_by_id'] and row.get('id', False):
                o_model['hide_id'] = False
            ids = get_query_id(ctx, o_model, row)
            o_model['hide_id'] = saved_hide_id
            if len(ids):
                id = ids[0]
                cur_obj = browseL8(ctx, model, id)
                if model == 'res.users' and len(ids) == 1:
                    cur_login = cur_obj.login
                    if 'login' in row:
                        ctx['def_email'] = '%s%s@example.com' % (
                            cur_obj.login,
                            ctx['oe_version'].split('.')[0],
                        )
            else:
                cur_obj = False
            vals, update_header_id, name_new = parse_in_fields(
                ctx, o_model, row, ids, cur_obj
            )
            if 'company_id' in ctx and 'company_id' in vals:
                if vals['company_id'] != company_id:
                    continue
            if len(ids):
                if update_header_id:
                    ctx['header_id'] = ids[0]
                name_old = cur_obj[o_model['name']]
                if not isinstance(name_old, basestring):
                    name_old = ''
                msg = "Update %d %s" % (id, name_old)
                debug_msg_log(ctx, ctx['level'] + 1, msg)
            if model == 'res.users' and 'new_password' in vals and len(ids) == 0:
                vals['password'] = vals['new_password']
                del vals['new_password']
                vals['password_crypt'] = ''
            written = False
            if len(ids):
                if not ctx['dry_run'] and len(vals):
                    try:
                        writeL8(ctx, model, ids, vals)
                        msg = "id=%d, %s=%s->%s" % (
                            cur_obj.id,
                            o_model['name'],
                            tounicode(name_old),
                            tounicode(name_new),
                        )
                        msg_log(ctx, ctx['level'] + 1, msg)
                        written = True
                    except BaseException:
                        msg = "!!write error! id=%d, %s=%s" % (
                            cur_obj.id,
                            o_model['name'],
                            tounicode(name_new),
                        )
                        print(msg)
                    if written:
                        if (
                            model == 'res.users'
                            and 'login' in vals
                            and cur_login == ctx['login_user']
                        ):
                            if 'login' in vals:
                                ctx['login_user'] = vals['login']
                            if 'new_password' in vals:
                                if vals['new_password'].find('$1$!') == 0:
                                    ctx['crypt_password'] = vals['new_password']
                                else:
                                    ctx['login_password'] = vals['new_password']
                            do_login(ctx)
                        try:
                            add_external_name(ctx, o_model, row, ids[0])
                        except BaseException:
                            msg = "!!No set external name id=%d, %s=%s" % (
                                cur_obj.id,
                                o_model['name'],
                                tounicode(name_new),
                            )
                            print(msg)
            else:
                msg = "insert " + _u(name_new)
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['dry_run']:
                    if not o_model.get('hide_cid', False) and 'company_id' not in vals:
                        vals['company_id'] = ctx['company_id']
                    try:
                        id = createL8(ctx, model, vals)
                        if update_header_id:
                            ctx['header_id'] = id
                        msg = "creat id={}, {}={}".format(
                            id, tounicode(o_model['name']), tounicode(name_new)
                        )
                        msg_log(ctx, ctx['level'] + 1, msg)
                        written = True
                    except BaseException:
                        id = None
                        msg = "!!create error! %s[%s]=%s" % (
                            tounicode(o_model.get('model')),
                            tounicode(o_model['name']),
                            tounicode(name_new),
                        )
                        print(msg)
                    if written and id:
                        try:
                            add_external_name(ctx, o_model, row, id)
                        except BaseException:
                            msg = "!!No set external name id=%d, %s=%s" % (
                                cur_obj.id,
                                o_model['name'],
                                tounicode(name_new),
                            )
                            print(msg)
                else:
                    ctx['header_id'] = -1
        csv_fd.close()
    else:
        msg = "Import file " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def import_config_file(ctx, csv_fn):
    csv.register_dialect(
        'odoo', delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL
    )

    csv_ffn = os.path.join(ctx['data_path'], csv_fn)
    if csv_ffn[-4:] == '.csv':
        ver_csv = '%s_%s%s' % (csv_ffn[0:-4], ctx['oe_version'], csv_ffn[-4:])
    if os.path.isfile(ver_csv):
        csv_ffn = ver_csv
    if not os.path.isfile(csv_ffn):
        csv_ffn = csv_fn
    if os.path.isfile(csv_ffn):
        csv_fd = open(csv_ffn, 'rb')
        hdr_read = False
        csv_obj = csv.DictReader(
            csv_fd, fieldnames=[], restkey='undef_name', dialect='odoo'
        )
        select_4_ver = False
        for row in csv_obj:
            if not hdr_read:
                csv_obj.fieldnames = row['undef_name']
                hdr_read = True
                file_valid = True
                if 'user' not in csv_obj.fieldnames:
                    file_valid = False
                if 'name' not in csv_obj.fieldnames:
                    file_valid = False
                if 'value' not in csv_obj.fieldnames:
                    file_valid = False
                if 'oe_versions' in csv_obj.fieldnames:
                    select_4_ver = True
                if file_valid:
                    continue
                else:
                    msg = "!Invalid header of " + csv_fn
                    msg = msg + " Should be: user,name,value"
                    msg_log(ctx, ctx['level'] + 1, msg)
                    return STS_FAILED
            if select_4_ver and row['oe_versions'].strip():
                if row['oe_versions'].find('-') >= 0:
                    item = '-' + ctx['oe_version']
                    if row['oe_versions'].find(item) >= 0:
                        continue
                else:
                    item = '+' + ctx['oe_version']
                    if row['oe_versions'].find(item) < 0:
                        continue
            user = eval_value(ctx, None, None, row['user'])
            name = eval_value(ctx, None, None, row['name'])
            value = eval_value(ctx, None, None, row['value'])
            if name:
                if user:
                    sts = setup_user_config_param(ctx, user, name, value)
                else:
                    sts = setup_global_config_param(ctx, name, value)
                if sts != STS_SUCCESS:
                    break
            else:
                msg = "!Unmanaged parameter %s " % row['name']
                msg_log(ctx, ctx['level'] + 1, msg)
        csv_fd.close()
    else:
        msg = "!File " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def setup_user_config_param(ctx, username, name, value):
    context = get_context(ctx)
    sts = STS_SUCCESS
    v = str2bool(value, None)
    if v is not None:
        value = v
    if isinstance(value, bool):
        if isinstance(name, int):
            group_ids = [name]
        else:
            group_ids = searchL8(
                ctx, 'res.groups', [('name', '=', name)], context=context
            )
    else:
        cat_ids = searchL8(
            ctx, 'ir.module.category', [('name', '=', name)], context=context
        )
        if isinstance(value, int):
            group_ids = [value]
        else:
            group_ids = searchL8(
                ctx,
                'res.groups',
                [('category_id', 'in', cat_ids), ('name', '=', value)],
                context=context,
            )
    if len(group_ids) != 1:
        if isinstance(value, bool):
            msg = "!!Parameter name '%s' not found!!" % tounicode(name)
        else:
            msg = "!!Parameter name '%s/%s' not found!!" % (
                tounicode(name),
                tounicode(value),
            )
        msg_log(ctx, ctx['level'] + 2, msg)
        return sts
    if isinstance(username, int):
        user_ids = [username]
    else:
        user_ids = searchL8(ctx, 'res.users', [('login', '=', username)])
        if len(user_ids) != 1:
            msg = "!!User " + tounicode(username) + " not found!!"
            msg_log(ctx, ctx['level'] + 2, msg)
            return STS_FAILED
    user = browseL8(ctx, 'res.users', user_ids[0])
    if not user:
        if isinstance(username, int):
            msg = "!!Invalid %d username!!" % username
        else:
            msg = "!!Invalid username: %s!!" % tounicode(username)
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    group_id = group_ids[0]
    vals = {}
    if isinstance(value, bool):
        if value and group_id not in user.groups_id.ids:
            vals['groups_id'] = [(4, group_id)]
            msg = "%s.%s = True" % (tounicode(username), tounicode(name))
            msg_log(ctx, ctx['level'] + 2, msg)
        elif not value and group_id in user.groups_id.ids:
            vals['groups_id'] = [(3, group_id)]
            msg = "%s.%s = False" % (tounicode(username), tounicode(name))
            msg_log(ctx, ctx['level'] + 2, msg)
    else:
        for id in searchL8(
            ctx, 'res.groups', [('category_id', 'in', cat_ids)], context=context
        ):
            if id != group_id and id in user.groups_id.ids:
                vals['groups_id'] = [(3, id)]
                try:
                    writeL8(ctx, 'res.users', user_ids, vals)
                except BaseException:
                    msg = "!!Error writing parameter %s" % name
                    msg_log(ctx, ctx['level'] + 2, msg)
        if group_id not in user.groups_id.ids:
            vals['groups_id'] = [(4, group_id)]
            if isinstance(value, bool):
                msg = "%s.%s = True" % (tounicode(username), tounicode(name))
            else:
                msg = "%s.%s/%s" % (
                    tounicode(username),
                    tounicode(name),
                    tounicode(value),
                )
            msg_log(ctx, ctx['level'] + 2, msg)
    if not ctx['dry_run'] and len(vals):
        writeL8(ctx, 'res.users', user_ids, vals)
    return sts


def setup_global_config_param(ctx, name, value):
    # context = get_context(ctx)
    sts = STS_SUCCESS
    items = name.split('.')
    if len(items) > 1:
        model = '.'.join(items[0: len(items) - 1])
        name = items[-1]
    else:
        model = 'res.config.settings'
    if isinstance(value, bool):
        try:
            id = max(searchL8(ctx, model, []))
            cur = browseL8(ctx, model, id)[name]
            if cur == value:
                return sts
        except BaseException:
            pass
    else:
        items = value.split('.')
        if len(items) == 1:
            try:
                id = max(searchL8(ctx, model, []))
                cur = browseL8(ctx, model, id)[name]
                if cur == value:
                    return sts
            except BaseException:
                pass
        else:
            model2 = '.'.join(items[0: len(items) - 1])
            value = items[-1]
            id = searchL8(ctx, model2, [('name', '=', value)])
            if not id:
                return STS_FAILED
            value = id[0]
            try:
                id = max(searchL8(ctx, model, []))
                cur = browseL8(ctx, model, id)[name]
                if cur.id == value:
                    return sts
            except BaseException:
                pass
    try:
        msg = "%s/%s" % (tounicode(name), tounicode(value))
        msg_log(ctx, ctx['level'] + 2, msg)
        id = createL8(ctx, model, {name: value})
        executeL8(ctx, model, 'execute', [id])
    except BaseException:
        sts = STS_FAILED
    return sts


def install_chart_of_account(ctx, name):
    sts = STS_SUCCESS
    context = get_context(ctx)
    chart_template_id = searchL8(
        ctx, 'account.chart.template', [('name', '=', name)], context=context
    )
    if len(chart_template_id) == 0:
        msg = "!Invalid chart of account " + tounicode(name) + "!!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    chart_template_id = chart_template_id[0]
    if 'company_id' not in ctx:
        msg = "!No company declared!!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    company_id = ctx['company_id']
    currency_id = browseL8(ctx, 'res.company', company_id).currency_id
    chart_values = {
        'company_id': company_id,
        'currency_id': currency_id,
        'chart_template_id': chart_template_id,
    }
    model = 'account.account'
    ids = searchL8(ctx, model, [('company_id', '=', company_id)])
    # Check if example coa installed
    if len(ids) > 0 and len(ids) < 16:
        unlinkL8(ctx, model, ids)
    if ctx['oe_version'] in ('6.1', '7.0', '8.0'):
        chart_setup_model = 'wizard.multi.charts.accounts'
        chart_values.update(
            executeL8(ctx, chart_setup_model, 'onchange_chart_template_id', [], 1)[
                'value'
            ]
        )
        chart_setup_id = executeL8(ctx, chart_setup_model, 'create', chart_values)
        executeL8(ctx, chart_setup_model, 'execute', [chart_setup_id])
    else:
        if company_id != ctx.get('user_company_id', 0):
            writeL8(ctx, 'res.users', ctx['user_id'], {'company_id': company_id})
        executeL8(
            ctx,
            'account.chart.template',
            'try_loading_for_current_company',
            [chart_template_id],
        )
        if company_id != ctx.get('user_company_id', 0):
            writeL8(
                ctx,
                'res.users',
                ctx['user_id'],
                {'company_id': ctx.get('user_company_id', 0)},
            )
    if sts == STS_SUCCESS:
        time.sleep(5)
    return sts


#############################################################################
# Public action list
#
def create_simple_act_list():
    """Return action list of local executable functions
    This function is project to be smart for future version
    """
    lx_act = []
    for a in list(globals()):
        if action_id(a):
            lx_act.append(action_id(a))
    return lx_act


def create_act_list(ctx):
    lx_act = create_simple_act_list()
    res = check_actions_list(ctx, lx_act)
    if res:
        lx_act = extend_actions_list(ctx, lx_act)
    ctx['_lx_act'] = lx_act
    return ctx


def check_actions_list(ctx, lx_act):
    """Merge local action list with user defined action list"""
    if lx_act is None:
        lx_act = create_simple_act_list()
    conf_obj = ctx['_conf_obj']
    res = True
    if ctx.get('do_sel_action', False):
        res = check_actions_1_list(ctx, ctx['do_sel_action'], lx_act, conf_obj)
    elif ctx.get('actions', None):
        res = check_actions_1_list(ctx, ctx['actions'], lx_act, conf_obj)
    if res and ctx.get('actions_db', None):
        res = check_actions_1_list(ctx, ctx['actions_db'], lx_act, conf_obj)
    if res and ctx.get('actions_mc', None):
        res = check_actions_1_list(ctx, ctx['actions_mc'], lx_act, conf_obj)
    if res and ctx.get('actions_uu', None):
        res = check_actions_1_list(ctx, ctx['actions_uu'], lx_act, conf_obj)
    return res


def check_actions_1_list(ctx, list, lx_act, conf_obj):
    res = True
    if not list:
        return res
    acts = list.split(',')
    for actv in acts:
        act = get_real_actname(ctx, actv)
        if act == '' or act is False or act is None:
            continue
        elif act in lx_act:
            continue
        elif conf_obj.has_section(act):
            pv = get_param_ver(ctx, 'actions')
            if conf_obj.has_option(act, pv):
                actions = conf_obj.get(act, pv)
                res = check_actions_1_list(ctx, actions, lx_act, conf_obj)
                if not res:
                    break
            elif conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                res = check_actions_1_list(ctx, actions, lx_act, conf_obj)
                if not res:
                    break
            else:
                res = False
                break
        else:
            res = False
            break
    return res


def extend_actions_list(ctx, lx_act):
    conf_obj = ctx['_conf_obj']
    if ctx.get('actions', None):
        lx_act = extend_actions_1_list(ctx, ctx['actions'], lx_act, conf_obj)
    if ctx.get('actions_db', None):
        lx_act = extend_actions_1_list(ctx, ctx['actions_db'], lx_act, conf_obj)
    if ctx.get('actions_mc', None):
        lx_act = extend_actions_1_list(ctx, ctx['actions_mc'], lx_act, conf_obj)
    if ctx.get('actions_uu', None):
        lx_act = extend_actions_1_list(ctx, ctx['actions_uu'], lx_act, conf_obj)
    return lx_act


def extend_actions_1_list(ctx, list, lx_act, conf_obj):
    if not list:
        return lx_act
    acts = list.split(',')
    for actv in acts:
        act = get_real_actname(ctx, actv)
        if act == '' or act is False or act is None:
            continue
        elif act in lx_act:
            continue
        elif conf_obj.has_section(act):
            lx_act.append(act)
            pv = get_param_ver(ctx, 'actions')
            if conf_obj.has_option(act, pv):
                actions = conf_obj.get(act, pv)
                lx_act = extend_actions_1_list(ctx, actions, lx_act, conf_obj)
            elif conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                lx_act = extend_actions_1_list(ctx, actions, lx_act, conf_obj)
            else:
                break
    return lx_act


def check_4_actions(ctx):
    if 'test_unit_mode' in ctx:
        log = False
    else:
        log = True
    if '_lx_act' in ctx:
        lx_act = ctx['_lx_act']
    else:
        lx_act = create_simple_act_list()
    valid_actions = check_actions_list(ctx, lx_act)
    if not valid_actions and log:
        msg = "Invalid action declarative "
        msg_log(ctx, ctx['level'], msg)
        msg = "Use one or more in following parameters:"
        msg_log(ctx, ctx['level'], msg)
        msg = "actions=" + ",".join(str(e) for e in sorted(lx_act))
        msg_log(ctx, ctx['level'], msg)
    return valid_actions


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    sts = STS_SUCCESS
    ctx = parse_args(
        cli_args, apply_conf=APPLY_CONF, version=version(), doc=__doc__
    )
    read_stored_dict(ctx)
    ctx['_today'] = str(date.today())
    ctx['_current_year'] = str(date.today().year)
    ctx['_last_year'] = str(date.today().year - 1)
    init_logger(ctx)
    # print_hdr_msg(ctx)
    if not check_4_actions(ctx):
        return STS_FAILED
    ctx = create_act_list(ctx)
    conn2do = False
    login2do = False
    do_newdb = False
    do_multidb = False
    for act in ctx['actions'].split(','):
        if act not in ("help", "list_actions", "show_params"):
            conn2do = True
            if act not in ("drop_db", "list_db"):
                login2do = True
        if act == "per_db":
            do_multidb = True
        if act == "new_db":
            do_newdb = True
    if conn2do:
        ctx = read_config(ctx)
        open_connection(ctx)
        print_hdr_msg(ctx)
    ctx['multi_user'] = multiuser(ctx, ctx['actions'].split(','))
    if do_newdb:
        if ctx.get('multi_db', False):
            ctx['db_name'] = ctx['dbfilter']
        if not ctx['db_name']:
            msg = "!No DB name supplied!!"
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    elif conn2do and ctx.get('multi_db', False) and not do_multidb:
        ctx['actions'] = 'per_db,' + ctx['actions']
        do_multidb = True
    if not do_newdb and conn2do and not do_multidb and ctx['db_name']:
        ctx = init_db_ctx(ctx, ctx['db_name'])
        msg = ident_db(ctx, ctx['db_name'])
        msg_log(ctx, ctx['level'], msg)
        if login2do:
            lgiuser = do_login(ctx)
            if lgiuser:
                sts = do_actions(ctx)
            else:
                sts = STS_FAILED
        else:
            sts = do_actions(ctx)
    else:
        sts = do_actions(ctx)
    decr_lev(ctx)
    if sts == STS_SUCCESS:
        msg = "------ Operations ended ------"
    else:
        msg = "###??? Last operation FAILED!!! ###???"
    msg_log(ctx, ctx['level'], msg)
    return sts


if __name__ == "__main__":
    exit(main())
