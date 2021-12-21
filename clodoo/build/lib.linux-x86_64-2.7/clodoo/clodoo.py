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
Massive operations on Zeroincombenze(R) / Odoo databases
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
zeroadm_mail   default user mail from conf file or <def_mail> if -D switch
zeroadm_login  default admin username from conf file
oneadm_mail    default user2 mail from conf file or <def_mail> if -D switch
oneadm_login   default admin2 username from conf file
botadm_mail    default bot user mail from conf file or <def_mail> if -D switch
botadm_login   default bot username from conf file
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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from future import standard_library
from builtins import input
# from builtins import str
# from builtins import range
from past.builtins import basestring
# from builtins import *                                           # noqa: F403
from builtins import object
import calendar
import csv
import os.path
import re
import sys
import time
import inspect
import platform
from datetime import date, datetime, timedelta
# from passlib.context import CryptContext
from os0 import os0
from python_plus import _c

try:
    from clodoo.clodoocore import (                           # noqa: F401
        is_valid_field, searchL8, browseL8,                   # noqa: F401
        eval_value, get_query_id, import_file_get_hdr,        # noqa: F401
        createL8, writeL8, unlinkL8, executeL8, connectL8,    # noqa: F401
        get_res_users, psql_connect, put_model_alias,         # noqa: F401
        set_some_values, get_company_id, build_model_struct,  # noqa: F401
        get_model_model, get_model_name, extr_table_generic,  # noqa: F401
        get_model_structure, execute_action_L8,               # noqa: F401
        is_required_field, model_has_company,                 # noqa: F401
        exec_sql, extract_vals_from_rec,                      # noqa: F401
        sql_reconnect, get_val_from_field,                    # noqa: F401
        cvt_from_ver_2_ver)                                   # noqa: F401
except:
    from clodoocore import (                                  # noqa: F401
        is_valid_field, searchL8, browseL8,                   # noqa: F401
        eval_value, get_query_id, import_file_get_hdr,        # noqa: F401
        createL8, writeL8, unlinkL8, executeL8, connectL8,    # noqa: F401
        get_res_users, psql_connect, put_model_alias,         # noqa: F401
        set_some_values, get_company_id, build_model_struct,  # noqa: F401
        get_model_model, get_model_name, extr_table_generic,  # noqa: F401
        get_model_structure, execute_action_L8,               # noqa: F401
        is_required_field, model_has_company,                 # noqa: F401
        exec_sql, extract_vals_from_rec,                      # noqa: F401
        sql_reconnect, get_val_from_field,                    # noqa: F401
        cvt_from_ver_2_ver)                                   # noqa: F401
try:
    from clodoo.clodoolib import (                            # noqa: F401
        crypt, debug_msg_log, decrypt, msg_burst,             # noqa: F401
        msg_log, parse_args, tounicode,                       # noqa: F401
        read_config, init_logger,                             # noqa: F401
        default_conf, build_odoo_param)                       # noqa: F401
except:
    from clodoolib import (                                   # noqa: F401
        crypt, debug_msg_log, decrypt, msg_burst,             # noqa: F401
        msg_log, parse_args, tounicode,                       # noqa: F401
        read_config, init_logger,                             # noqa: F401
        default_conf, build_odoo_param)                       # noqa: F401
try:
    from transodoo import (read_stored_dict, translate_from_to)
except:
    from clodoo.transodoo import (read_stored_dict, translate_from_to)

# TMP
from subprocess import PIPE, Popen
standard_library.install_aliases()                                 # noqa: E402

__version__ = "0.3.55"

# Apply for configuration file (True/False)
APPLY_CONF = True
STS_FAILED = 1
STS_SUCCESS = 0

PAY_MOVE_STS_2_DRAFT = ['posted', ]
INVOICES_STS_2_DRAFT = ['open', 'paid']
STATES_2_DRAFT = ['open', 'paid', 'posted']
CV_PROJECT_ID = 3504
PSQL = 'psql -Upostgres -c"%s;" %s'

db_msg_sp = 0
db_msg_stack = []


class Clodoo(object):

    def __init__(self):
        pass


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
        line = '%s,True,%s,True,%s,"%s","%s"\n' % (xmodel,
                                                   model,
                                                   f,
                                                   op,
                                                   str(x))
        fd.write(line)
        fd.close()


def print_hdr_msg(ctx):
    ctx['level'] = 0
    msg = u"====== Do massive operations V%s ======" % __version__
    msg_log(ctx, ctx['level'], msg)
    incr_lev(ctx)
    msg = u"Configuration from"
    for f in ctx.get('conf_fns'):
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
        raise RuntimeError(res)                              # pragma: no cover
    return ctx['odoo_session']


def do_login(ctx):
    """Do a login into DB; try using more usernames and passwords"""

    def get_login_user(ctx):
        return ctx['odoo_session'].env.user

    msg = "do_login()"
    debug_msg_log(ctx, ctx['level'] + 1, msg)
    userlist = ctx['login_user'].split(',')
    for u in ctx['login2_user'].split(','):
        if u and u not in userlist:
            userlist.append(u)
    if ctx.get('lgi_user'):
        for u in ctx['lgi_user'].split(','):
            if u and u not in userlist:
                userlist.insert(0, u)
    if ctx['login_password']:
        pwdlist = ctx['login_password'].split(',')
    else:
        pwdlist = []
    if ctx['crypt_password']:
        cryptlist = ctx['crypt_password'].split(',')
    else:
        cryptlist = []
    if ctx['login2_password']:
        for p in ctx['login2_password'].split(','):
            if p and p not in pwdlist:
                pwdlist.append(p)
    if ctx['crypt2_password']:
        for p in ctx['crypt2_password'].split(','):
            if p and p not in cryptlist:
                cryptlist.append(p)
    if ctx.get('lgi_pwd', 'admin') is None:
        ctx['lgi_pwd'] = 'admin'
    if ctx.get('lgi_pwd', 'admin'):
        for p in ctx.get('lgi_pwd', 'admin').split(','):
            if p and p not in pwdlist:
                pwdlist.insert(0, p)
    user = False
    db_name = get_dbname(ctx, 'login')
    for username in userlist:
        for pwd in cryptlist:
            crypted = True
            msg = "do_login_%s(%s,$1$%s)" % (ctx['svc_protocol'],
                                             username,
                                             pwd)
            debug_msg_log(ctx, ctx['level'] + 2, msg)
            if ctx['svc_protocol'] == 'jsonrpc':
                try:
                    ctx['odoo_session'].login(
                        db=db_name, login=username, password=decrypt(pwd))
                except BaseException:
                    continue
                # Keep out of try / except to catch user error
                user = get_login_user(ctx)
                break
            else:
                try:
                    user = ctx['odoo_session'].login(database=db_name,
                                                     user=username,
                                                     passwd=decrypt(pwd))
                    break
                except BaseException:
                    pass
        if not user:
            crypted = False
            for pwd in pwdlist:
                try:
                    msg = "do_login_%s(%s,$1$%s)" % (ctx['svc_protocol'],
                                                     username,
                                                     crypt(pwd))
                    debug_msg_log(ctx, ctx['level'] + 2, msg)
                    if ctx['svc_protocol'] == 'jsonrpc':
                        ctx['odoo_session'].login(db=db_name,
                                                  login=username,
                                                  password=pwd)
                        user = get_login_user(ctx)
                    else:
                        user = ctx['odoo_session'].login(database=db_name,
                                                         user=username,
                                                         passwd=pwd)
                    break
                except BaseException:
                    pass
        if user:
            break
    if not user:
        if not ctx.get('no_warning_pwd', False):
            os0.wlog(u"!DB={0}: invalid user/pwd"
                     .format(tounicode(ctx['db_name'])))
        return
    if not ctx['multi_user']:
        ctx = init_user_ctx(ctx, user)
        msg = ident_user(ctx, user.id)
        msg_log(ctx, ctx['level'], msg)
    if ctx['set_passepartout']:
        vals = {}
        if user.login != ctx['login_user']:
            vals['login'] = ctx['login_user']
        if ctx['crypt_password'] and crypted and pwd != ctx['crypt_password']:
            vals['password'] = decrypt(ctx['crypt_password'])
        elif (ctx['crypt_password'] and not crypted and
              pwd != decrypt(ctx['crypt_password'])):
            vals['password'] = decrypt(ctx['crypt_password'])
        elif (ctx['login_password'] and crypted and
              decrypt(pwd) != ctx['login_password']):
            vals['password'] = ctx['login_password']
        elif (ctx['login_password'] and not crypted and
              pwd != ctx['login_password']):
            vals['password'] = ctx['login_password']
        if ctx['oe_version'] != '6.1':
            if ((ctx['with_demo'] and user.email != ctx['def_email']) or
                    (not ctx['with_demo'] and
                     user.email != ctx['zeroadm_mail'])):
                vals['email'] = set_some_values(ctx,
                                                None,
                                                'email',
                                                user.email,
                                                model='res.users')
        if vals:
            if vals.get('password'):
                # ctx['password_crypt'] = CryptContext(
                #     ['pbkdf2_sha512']).encrypt(vals.get('new_password'))
                if 'password_crypt' in vals:
                    del vals['password_crypt']
            try:
                writeL8(ctx, 'res.users', user.id, vals)
                if not ctx.get('no_warning_pwd', False):
                    os0.wlog(u"DB=%s: updated user/pwd/mail %s to %s" % (
                             tounicode(ctx['db_name']),
                             tounicode(username),
                             tounicode(ctx['login_user'])))
                    os0.wlog(u"You should restart the Odoo service")
            except BaseException:
                os0.wlog(u"!!Passpartout user %s/%s write error!" % (
                    tounicode(username),
                    tounicode(ctx['login_user'])))
    if user:
        ctx['_cr'] = psql_connect(ctx)
    return user


def oerp_set_env(confn=None, db=None, xmlrpc_port=None, oe_version=None,
                 user=None, pwd=None, lang=None, ctx=None):
    D_LIST = ('ena_inquire', 'caller', 'level', 'dry_run', 'multi_user',
              'set_passepartout', 'no_login')
    P_LIST = ('db_host', 'db_port', 'db_name', 'db_user', 'db_password',
              'admin_passwd',
              'login_user', 'login_password', 'crypt_password',
              'login2_user', 'login2_password', 'crypt2_password',
              'svc_protocol', 'oe_version', 'xmlrpc_port',
              'lang', 'psycopg2')
    DEFLT = default_conf(ctx)

    def oerp_env_fill(db=None, xmlrpc_port=None, oe_version=None,
                      user=None, pwd=None, lang=None, ctx=None,
                      inquire=None):
        ctx = ctx or {}
        for p in D_LIST + P_LIST:
            if p == 'db_name' and db:
                ctx[p] = db
            elif p == 'login_user' and user:
                ctx[p] = user
            elif p == 'login_password' and pwd:
                ctx[p] = pwd
            elif p == 'xmlrpc_port' and xmlrpc_port:
                if isinstance(xmlrpc_port, basestring):
                    ctx[p] = int(xmlrpc_port)
                else:
                    ctx[p] = xmlrpc_port
            # elif p == 'db_port' and xmlrpc_port:
            #     if isinstance(xmlrpc_port, basestring):
            #         ctx[p] = int(xmlrpc_port)
            #     else:
            #         ctx[p] = xmlrpc_port
            elif p == 'oe_version' and oe_version and oe_version != '*':
                ctx[p] = oe_version
                if not ctx.get('odoo_vid'):
                    ctx['odoo_vid'] = ctx['oe_version']
            elif p == 'svc_protocol' and (p not in ctx or not ctx[p]):
                if ctx.get('oe_version') in ('6.1', '7.0', '8.0'):
                    ctx[p] = 'xmlrpc'
                elif ctx.get('oe_version'):
                    ctx[p] = 'jsonrpc'
            elif p == 'lang' and lang:
                ctx[p] = lang
            elif p not in ctx and p in DEFLT:
                ctx[p] = DEFLT[p]
            elif p not in ctx and inquire:
                ctx[p] = input('%s[def=%s]? ' % (p, ctx[p]))
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:
            ctx['run_daemon'] = True
        return ctx

    ctx = ctx or {}
    if confn:
        ctx['conf_fn'] = confn
        if 'conf_fns' in ctx:
            del ctx['conf_fns']
    ctx = read_config(ctx)
    ctx = oerp_env_fill(db=db,
                        xmlrpc_port=xmlrpc_port,
                        user=user, pwd=pwd,
                        oe_version=oe_version or ctx.get('oe_version'),
                        lang=lang,
                        ctx=ctx)
    open_connection(ctx)
    if ctx['no_login']:
        return False, ctx
    lgiuser = do_login(ctx)
    if not lgiuser:
        raise RuntimeError('Invalid user or password!')      # pragma: no cover
    uid = lgiuser.id
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
    """"Clear company parameters"""
    for n in ('def_company_id',
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
              'module_udpated'):
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
        ctx['country_code'] = browseL8(ctx,
                                       'res.country',
                                       ctx['def_country_id']).code
    return ctx


def init_user_ctx(ctx, user):
    ctx['user_id'] = user.id
    if ctx['oe_version'] != "6.1":
        ctx['user_partner_id'] = user.partner_id.id
    ctx['user_name'] = get_res_users(ctx, user, 'name')
    ctx['def_email'] = '%s%s@example.com' % (user.login,
                                             ctx['oe_version'].split('.')[0])
    ctx['user_company_id'] = user.company_id.id
    ctx['user_country_id'] = get_res_users(ctx, user, 'country_id')
    if ctx.get('def_company_id', 0) == 0:
        ctx['def_company_id'] = ctx['user_company_id']
        ctx['def_company_name'] = user.company_id.name
    return ctx


def get_dblist(ctx):
    # Interface xmlrpc and jsonrpc are the same
    if ctx['oe_version'] == '12.0':     # FIX: odoorpc wont work 12.0
        res, err = Popen(['psql', '-Atl'],
                         stdin=PIPE,
                         stdout=PIPE,
                         stderr=PIPE).communicate()
        list = []
        for r in res.split('\n'):
            rs = r.split('|')
            if len(rs) > 2 and rs[1] == 'odoo12':
                list.append(rs[0])
        return list
    elif ctx['oe_version'] == '7.0':     # FIX
        time.sleep(1)
    return ctx['odoo_session'].db.list()


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
    if action == 'per_db' or \
            action == 'per_company' or \
            action == 'per_user':
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
    if ctx['dbg_mode'] or 'test_unit_mode' not in ctx:
        msg = u"> do_group_action(%s)" % action
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
                    msg = u"Recursive actions " + act
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
                    break
                sts = do_single_action(lctx, act)
                if sts == STS_SUCCESS and 'header_id' in lctx:
                    ctx['header_id'] = lctx['header_id']
            else:
                msg = u"Invalid action " + act
                msg_log(ctx, ctx['level'] + 1, msg)
                sts = STS_FAILED
                break
        decr_lev(ctx)
    else:
        msg = u"Undefined action"
        msg_log(ctx, ctx['level'] + 1, msg)
        sts = STS_FAILED
    return sts


def do_single_action(ctx, action):
    """Do single action (recursive)"""
    if isaction(ctx, action):
        if action == '' or action is False or action is None:
            return STS_SUCCESS
        if ctx['dbg_mode']:
            msg = u"> do_single_action(%s)" % action
            msg_log(ctx, ctx['level'] + 1, msg)
        if ctx.get('db_name', '') == 'auto':
            if action not in ("help", "list_actions", "show_params", "new_db"):
                ctx['db_name'] = get_dbname(ctx, action)
                lgiuser = do_login(ctx)
                if not lgiuser:
                    action = 'unit_test'
        act = lexec_name(ctx, action)
        if act in list(globals()):
            if (action in ('install_modules',
                           'upgrade_modules',
                           'uninstall_modules') and
                    not ctx.get('module_udpated', False)):
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
        msg = u"> do_actions(%s)" % actions
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
                    ctx['multi_user'] = multiuser(ctx,
                                                  actions)
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
    for p in ('actions',
              'install_modules',
              'uninstall_modules',
              'upgrade_modules',
              'purge_modules',
              'data_selection',
              'modules_2_manage',):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        else:
            lctx[p] = False
    for p in ('model',
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
              'hideB_cid'):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        elif p in lctx:
            del lctx[p]
    DEFDCT = default_conf(lctx)
    for p in ('lang',
              'dbfilter',
              'companyfilter',
              'userfilter',
              'chart_of_account'):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            pv = conf_obj.get(action, p)
            if pv != DEFDCT[p]:
                lctx[p] = pv
    for p in ('install_modules',
              'uninstall_modules',
              'purge_modules',
              'actions',
              'hide_cid'):
        pv = get_param_ver(ctx, p)
        if pv in lctx:
            lctx[pv] = os0.str2bool(lctx[pv], lctx[pv])
        elif p in lctx:
            lctx[p] = os0.str2bool(lctx[p], lctx[p])
    return lctx


def ident_db(ctx, db):
    db_name = get_dbname(ctx, '')
    msg = u"DB=" + db + " [" + ctx.get('db_type', '') + "]"
    if db_name != db:
        msg = msg + " - default " + db_name
    return msg


def ident_company(ctx, c_id):
    msg = u"Company {0:>3})\t'{1}'".format(c_id,
                                           tounicode(ctx.get('company_name',
                                                             '')))
    return msg


def ident_user(ctx, u_id):
    user = browseL8(ctx, 'res.users', u_id)
    msg = u"DB=%-24.24s uid=%-3d user=%-16.16s" \
          u" email=%-24.24s company=%-24.24s" % (
              tounicode(ctx['db_name']),
              u_id,
              tounicode(user.login),
              # tounicode(ctx['user_name']),
              tounicode(get_res_users(ctx, user, 'email')),
              tounicode(user.company_id.name))
    return msg


def get_data_selection(ctx):
    if not ctx['data_selection'] or ctx['data_selection'] == 'all':
        ctx['data_selection'] = 'account_move,sale,purchase,project,mail,crm,'\
                                'inventory,marketing,hr,analytic,sequence'
    return ctx['data_selection'].split(',')


def env_ref(ctx, xref):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        ids = searchL8(ctx, 'ir.model.data', [('module', '=', xrefs[0]),
                                              ('name', '=', xrefs[1])])
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


def act_set_qweb(ctx):
    """Add system param to convert web.base.url to https"""
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__)
    ident = ' ' * ctx['level']
    model = 'ir.config_parameter'
    ids = searchL8(ctx, model, [('key', '=', 'web.base.url.cvt2https')])
    if not ids:
        createL8(ctx, model, {'key': 'web.base.url.cvt2https',
                              'value': True})
    ids = searchL8(ctx, model, [('key', '=', 'web.base.url.cvt2https')])
    if ids:
        ids = searchL8(ctx, model, [('key', '=', 'web.base.url')])
    if ids:
        param = browseL8(ctx, model, ids[0])
        if param.value.find('localhost') < 0:
            web_url = param.value.replace('http:', 'https:')
        else:
            localhost = platform.node()
            majver = ctx['majver']
            web_url = ''
            if localhost == 'shsprd17':
                web_url = 'https://erp%d.zeroincombenze.it' % majver
            elif localhost == 'shs17fid':
                web_url = 'https://dev%d.zeroincombenze.it' % majver
            elif localhost == 'vg7odoopro' and majver == 10:
                web_url = 'https://%s.pro%d.odoo.vg7.it' % (ctx['db_name'],
                                                            majver)
            elif localhost == 'vg7odoopro' and majver == 8:
                web_url = 'https://%s.pro.odoo.vg7.it' % ctx['db_name']
            elif localhost == 'vg7odoodev' and majver == 10:
                web_url = 'https://dev%d.odoo.vg7.it' % majver
            elif localhost == 'vg7odoodev' and majver == 8:
                web_url = 'https://dev.odoo.vg7.it'

        if web_url != param.value:
            writeL8(ctx, model, ids[0], {'value': web_url})
            print("%sParam %s updated to %s" % (ident, param.key, web_url))
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
    print("%s- c. country_id = %d " % (ident, ctx.get('company_country_id',
                                                      0)))
    print("%s- c. partner_id = %d " % (ident, ctx.get('company_partner_id',
                                                      0)))
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
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__)
    return STS_SUCCESS


def act_run_unit_tests(ctx):
    """"Run module unit test (no yet avaiable)"""
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__)
    try:
        executeL8(ctx,
                  'ir.actions.server',
                  'Run Unit test',
                  'banking_export_pain')
    except BaseException:
        return STS_FAILED
    return STS_SUCCESS


def act_drop_db(ctx, db_name=None):
    """Drop a DB %s, if exists"""
    db_name = db_name or ctx['db_name']
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__ % db_name)
    sts = STS_SUCCESS
    if not ctx['dry_run']:
        ctr = 3
        sts = STS_FAILED
        while sts == STS_FAILED and ctr > 0:
            try:
                cmd = 'pg_db_active -wa %s' % db_name
                os0.muteshell(cmd, simulate=False, keepout=False)
                if ctx['oe_version'] == '12.0': # FIX: odoorpc wont work 12.0
                    os0.muteshell("dropdb -Upostgres --if-exists " +
                                  db_name)
                else:
                    ctx['odoo_session'].db.drop(ctx['admin_passwd'],
                                                db_name)
                # ctx['odoo_session'].db.drop(ctx['admin_passwd'],
                #                             db_name)
                sts = STS_SUCCESS
                if db_name[0:11] != 'clodoo_test':
                    time.sleep(2)
            except BaseException:
                ctr -= 1
                if db_name[0:11] != 'clodoo_test':
                    time.sleep(3)
    return sts


def act_wep_company(ctx):
    """Wipe company %s: delete all records of company but not res_parter"""
    if not ctx.get('company_name'):
        msg_log(ctx, ctx['level'], 'No wipe action due to missed company!!!')
        return STS_FAILED
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__ % ctx.get('company_name'))
    data_selection = get_data_selection(ctx)
    sts = STS_SUCCESS
    # c_id = ctx['company_id']
    msg = ','.join(data_selection)
    msg_log(ctx, ctx['level'], msg)
    set_server_isolated(ctx)
    if sts == STS_SUCCESS and 'mail' in data_selection:
        sts = remove_company_mail_records(ctx)
    if sts == STS_SUCCESS and 'project' in data_selection:
        sts = remove_company_project_records(ctx)
    if sts == STS_SUCCESS and 'purchase' in data_selection:
        sts = remove_company_purchases_records(ctx)
    if sts == STS_SUCCESS and 'crm' in data_selection:
        sts = remove_company_crm_records(ctx)
    if sts == STS_SUCCESS and 'sale' in data_selection:
        sts = remove_company_sales_records(ctx)
    if sts == STS_SUCCESS and 'inventory' in data_selection:
        sts = remove_company_inventory_records(ctx)
    if sts == STS_SUCCESS and 'marketing' in data_selection:
        sts = remove_company_marketing_records(ctx)
    if sts == STS_SUCCESS and 'hr' in data_selection:
        sts = remove_company_hr_records(ctx)
    if sts == STS_SUCCESS and 'analytic' in data_selection:
        sts = remove_company_analytics_records(ctx)
    if sts == STS_SUCCESS and 'account_move' in data_selection:
        sts = remove_company_account_move_records(ctx)
    if sts == STS_SUCCESS and 'product' in data_selection:
        sts = remove_company_product_records(ctx)
    if sts == STS_SUCCESS and 'partner' in data_selection:
        sts = remove_company_partner_records(ctx)
    if sts == STS_SUCCESS and 'account_base' in data_selection:
        sts = remove_company_account_base_records(ctx)
    if sts == STS_SUCCESS and 'company' in data_selection:
        if not ctx['dry_run']:
            company_id = ctx['company_id']
            model = 'res.company'
            if company_id == 1:
                writeL8(ctx, model,
                        [company_id],
                        {'name': 'Your company %d' % company_id,
                         'street': '',
                         'city': ''})
            else:
                try:
                    unlinkL8(ctx, model,
                             [company_id])
                except BaseException:
                    msg = u"Cannot remove %s.%d" % (model, company_id)
                    msg_log(ctx, ctx['level'], msg)
                    writeL8(ctx, model,
                            [company_id],
                            {'name': 'Do not use %d' % company_id,
                             'street': '',
                             'city': ''})
    return sts


def act_wep_db(ctx):
    """Wipe DB %s: delete all records of DB but not res_parter"""
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__ % ctx.get('db_name'))
    data_selection = get_data_selection(ctx)
    sts = STS_SUCCESS
    msg = ','.join(data_selection)
    msg_log(ctx, ctx['level'], msg)
    set_server_isolated(ctx)
    if sts == STS_SUCCESS and 'mail' in data_selection:
        sts = remove_all_mail_records(ctx)
    if sts == STS_SUCCESS and 'mail' in data_selection:
        sts = remove_all_note_records(ctx)
    if sts == STS_SUCCESS and 'project' in data_selection:
        sts = remove_all_project_records(ctx)
    if sts == STS_SUCCESS and 'purchase' in data_selection:
        sts = remove_all_purchases_records(ctx)
    if sts == STS_SUCCESS and 'crm' in data_selection:
        sts = remove_all_crm_records(ctx)
    if sts == STS_SUCCESS and 'sale' in data_selection:
        sts = remove_all_sales_records(ctx)
    if sts == STS_SUCCESS and 'inventory' in data_selection:
        sts = remove_all_inventory_records(ctx)
    if sts == STS_SUCCESS and 'marketing' in data_selection:
        sts = remove_all_marketing_records(ctx)
    if sts == STS_SUCCESS and 'account_move' in data_selection:
        sts = remove_all_account_move_records(ctx)
    if sts == STS_SUCCESS and 'hr' in data_selection:
        sts = remove_all_hr_records(ctx)
    if sts == STS_SUCCESS and 'product' in data_selection:
        sts = remove_all_product_records(ctx)
    if sts == STS_SUCCESS and 'partner' in data_selection:
        sts = remove_all_partner_records(ctx)
    if sts == STS_SUCCESS and 'user' in data_selection:
        sts = remove_all_user_records(ctx)
    if sts == STS_SUCCESS and 'sequence' in data_selection:
        sts = reset_sequence(ctx)
    if sts == STS_SUCCESS:
        sts = reset_menuitem(ctx)
    return sts


def act_new_db(ctx):
    """Create new DB"""
    sts = STS_SUCCESS
    lang = ctx.get('lang', 'en_US')
    msg = "Create DB %s [lang=%s, demo=%s]" % (ctx['db_name'],
                                               lang,
                                               str(ctx['with_demo']))
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        if ctx['db_name'] == 'auto':
            ctx['db_name'] = create_zero_db(ctx)
            msg = "Assigned name is %s" % (ctx['db_name'])
            msg_log(ctx, ctx['level'], msg)
        if ctx['db_name']:
            if ctx['crypt_password']:
                pwd = decrypt(ctx['crypt_password'])
                ctx['server_version'] = ctx['odoo_session'].version
            else:
                pwd = ctx['login_password']
                try:
                    ctx['server_version'] = ctx[
                        'odoo_session'].db.server_version()
                except BaseException:
                    ctx['server_version'] = ctx['odoo_session'].version
            try:
                if ctx['svc_protocol'] == 'jsonrpc':
                    ctx['odoo_session'].db.create(ctx['admin_passwd'],
                                                  ctx['db_name'],
                                                  ctx['with_demo'],
                                                  lang,
                                                  pwd)
                    time.sleep(3)
                    open_connection(ctx)        # Needed for 11.0
                elif ctx['server_version'] == '7.0':
                    ctx['odoo_session'].db.create_and_wait(ctx['admin_passwd'],
                                                           ctx['db_name'],
                                                           ctx['with_demo'],
                                                           lang,
                                                           pwd)
                else:
                    ctx['odoo_session'].db.create_database(ctx['admin_passwd'],
                                                           ctx['db_name'],
                                                           ctx['with_demo'],
                                                           lang,
                                                           pwd)
                    time.sleep(3)
            except BaseException:
                sts = STS_FAILED
            if sts == STS_SUCCESS:
                ctx['no_warning_pwd'] = True
                lgiuser = do_login(ctx)
                if not lgiuser:
                    sts = STS_FAILED
        else:
            sts = STS_FAILED
    return sts


def act_per_db(ctx):
    """Iter action on DBs"""
    dblist = get_dblist(ctx)
    if 'actions_db' in ctx:
        del ctx['actions_db']
    saved_actions = ctx['actions']
    if ctx['dbg_mode']:
        msg = u"> per_db(%s =~ %s)" % (dblist, ctx['dbfilter'])
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
                    msg = u"DB skipped by invalid db_type"
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
        msg = u"No DB matches"
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
        msg = u"> per_company(%s =~ %s)" % (company_ids, ctx['companyfilter'])
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
                    msg = u"> break action(per_company)"
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
                ctx['country_code'] = browseL8(ctx,
                                               'res.country',
                                               ctx['def_country_id']).code
            if sts != STS_SUCCESS:
                break
    return sts


def act_execute(ctx):
    sts = STS_SUCCESS
    o_model = build_model_struct(ctx)
    model = get_model_model(ctx, o_model)
    if not o_model.get('model') or \
            not o_model.get('model_action') or \
            not o_model.get('model_keyids'):
        msg = 'Excecute w/o model or key'
        msg_log(ctx, ctx['level'] + 1, msg)
        sts = STS_FAILED
    else:
        where = []
        model_name = get_model_name(ctx, o_model)
        if model_name:
            where.append(
                [model_name, 'like', o_model['model_keyids']])
            ids = searchL8(ctx, model, where)
        else:
            ids = [o_model['model_keyids']]
        if model == 'account.move' and \
                o_model['model_action'] == 'button_validate' and \
                ctx['majver'] >= 10:
            o_model['model_action'] = 'post'
        try:
            executeL8(ctx,
                      model,
                      o_model['model_action'],
                      ids)
        except BaseException:
            msg = 'Excecute (%s, %s, %s) Failed!' % (model,
                                                     o_model['model_action'],
                                                     str(ids))
            msg_log(ctx, ctx['level'] + 1, msg)
            sts = STS_FAILED
    return sts


def act_workflow(ctx):
    sts = STS_SUCCESS
    o_model = build_model_struct(ctx)
    model = get_model_model(ctx, o_model)
    if not o_model.get('model') or \
            not o_model.get('model_action') or \
            not o_model.get('model_keyids'):
        msg = 'Excecute w/o model or key'
        msg_log(ctx, ctx['level'] + 1, msg)
        sts = STS_FAILED
    else:
        where = []
        model_name = get_model_name(ctx, o_model)
        if model_name:
            where.append(
                [model_name, 'like', o_model['model_keyids']])
            ids = searchL8(ctx, model, where)
            if len(ids) == 0:
                msg = 'Excecute w/o model or key'
                msg_log(ctx, ctx['level'] + 1, msg)
                sts = STS_FAILED
                id = 0
            else:
                id = ids[0]
        else:
            id = o_model['model_keyids']
        try:
            execute_action_L8(ctx, model, o_model.get('model_action'), ids)
        except BaseException:
            msg = 'Workflow (%s, %s, %d) Failed!' % (model,
                                                     o_model['model_action'],
                                                     id)
            msg_log(ctx, ctx['level'] + 1, msg)
            sts = STS_FAILED
    return sts


def act_update_modules(ctx):
    """Update module list on DB"""
    msg = u"Update module list"
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        model = 'ir.module.module'
        ids = searchL8(ctx, model, [('name', '=like', '__old_%')])
        if len(ids):
            unlinkL8(ctx, model, ids)
        executeL8(ctx,
                  'base.module.update',
                  'update_module',
                  [])
        ids = searchL8(ctx, model,
                       [('state', '=', 'to install')])
        if ids:
            msg = u"Found module to install ..."
            msg_log(ctx, ctx['level'] + 1, msg)
            try:
                executeL8(ctx,
                          model,
                          'button_install_cancel',
                          ids)
                time.sleep(3)
            except BaseException:
                pass
        ids = searchL8(ctx, model,
                       [('state', '=', 'to upgrade')])
        if ids:
            msg = u"Found module to upgrade ..."
            msg_log(ctx, ctx['level'] + 1, msg)
            try:
                executeL8(ctx,
                          model,
                          'button_upgrade_cancel',
                          ids)
                time.sleep(3)
            except BaseException:
                pass
        ids = searchL8(ctx, model,
                       [('state', '=', 'to remove')])
        if ids:
            msg = u"Found module to uninstall ..."
            msg_log(ctx, ctx['level'] + 1, msg)
            try:
                executeL8(ctx,
                          model,
                          'button_uninstall_cancel',
                          ids)
                time.sleep(3)
            except BaseException:
                pass
    return STS_SUCCESS


def act_upgrade_modules(ctx, module_list=None):
    """Upgrade module from list"""
    msg = u"Upgrade modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = module_list or get_real_paramvalue(
        ctx, 'upgrade_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    model = 'ir.module.module'
    sts = STS_SUCCESS
    for mx in module_list:
        if mx == "":
            continue
        if mx[-1] == '!':
            modname = mx[0:-1]
            ignore_not_installed = True
        else:
            modname = mx
            ignore_not_installed = False
        msg = "name(%s) .." % mx
        msg_log(False, ctx['level'] + 1, msg)
        module_ids = searchL8(ctx, model,
                              [('name', '=', modname)],
                              context=context)
        if not module_ids:
            msg, sts = set_msg('Module %s not found!',
                               modname,
                               True)
            msg_log(ctx, ctx['level'] + 1, msg)
            continue
        if ctx['dry_run']:
            continue
        module = browseL8(ctx, model, module_ids[0])
        if module.state == 'installed':
            if cur_lang != 'en_US':
                cur_lang = 'en_US'
                set_user_lang(ctx, cur_lang)
            try:
                executeL8(ctx,
                          'ir.module.module',
                          'button_immediate_upgrade',
                          module_ids)
                time.sleep(len(module.dependencies_id) + 1)
            except BaseException:
                msg, sts = set_msg('Error upgrading %s!',
                                   modname,
                                   ignore_not_installed)
                msg_log(ctx, ctx['level'] + 1, msg)
        module = browseL8(ctx, model, module_ids[0])
        if module.state != 'installed':
            msg, sts = set_msg('Module %s not upgraded!',
                               modname,
                               ignore_not_installed)
            msg_log(ctx, ctx['level'] + 1, msg)
        if sts == STS_FAILED and ctx['exit_onerror']:
            break
    if cur_lang != user_lang:
        set_user_lang(ctx, user_lang)
    return sts


def act_purge_modules(ctx, module_list=None):
    """Purge module from list"""
    msg = u"Purge unuseful modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = module_list or get_real_paramvalue(
        ctx, 'purge_modules').split(',')
    if not ctx.get('_cr'):
        msg = u"Purge require sql access!"
        msg_log(ctx, ctx['level'], msg)
        msg = u"Please set sql parameters (db_* odoo params)"
        msg_log(ctx, ctx['level'], msg)
        return STS_FAILED
    sts = STS_SUCCESS
    for mx in module_list:
        if mx == "":
            continue
        for table in ('ir_translation',
                      'base.module.upgrade',
                      ):
            query = '''delete from %s where module='%s' ''' % (table, mx)
            incr_lev(ctx)
            msg = u">>>%s" % query
            msg_log(ctx, ctx['level'], msg)
            decr_lev(ctx)
            try:
                ctx['_cr'].execute(query)
            except BaseException:
                msg_log(ctx, ctx['level'], 'Error excuting sql')

    return sts


def act_uninstall_modules(ctx, module_list=None):
    """Uninstall module from list"""
    msg = u"Uninstall unuseful modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = module_list or get_real_paramvalue(
        ctx, 'uninstall_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    model = 'ir.module.module'
    sts = STS_SUCCESS
    for mx in module_list:
        if mx == "":
            continue
        if mx[-1] == '!':
            modname = mx[0:-1]
            ignore_not_installed = True
        else:
            modname = mx
            ignore_not_installed = False
        msg = "name(%s) .." % mx
        msg_log(False, ctx['level'] + 1, msg)
        module_ids = searchL8(ctx, model,
                              [('name', '=', modname)],
                              context=context)
        if not module_ids:
            msg, sts = set_msg('Module %s not found!',
                               modname,
                               True)
            msg_log(ctx, ctx['level'] + 1, msg)
            continue
        if ctx['dry_run']:
            continue
        module = browseL8(ctx, model, module_ids[0])
        if module.state != 'uninstalled':
            if cur_lang != 'en_US':
                cur_lang = 'en_US'
                set_user_lang(ctx, cur_lang)
            try:
                executeL8(ctx,
                          model,
                          'button_immediate_uninstall',
                          module_ids)
                time.sleep(3)
            except BaseException:
                msg = 'Error uninstalling %s!' % modname
                msg_log(ctx, ctx['level'] + 1, msg)
        module = browseL8(ctx, model, module_ids[0])
        if module.state != 'uninstalled':
            msg, sts = set_msg('Module %s not uninstalled!',
                               modname,
                               ignore_not_installed)
            msg_log(ctx, ctx['level'] + 1, msg)
        if sts == STS_FAILED and ctx['exit_onerror']:
            break
    if cur_lang != user_lang:
        set_user_lang(ctx, user_lang)
    return sts


def act_install_modules(ctx, module_list=None):
    """Install modules from list"""

    msg = u"Install modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = module_list or get_real_paramvalue(
        ctx, 'install_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    model = 'ir.module.module'
    sts = STS_SUCCESS
    for mx in module_list:
        if mx == "":
            continue
        if mx[-1] == '!':
            modname = mx[0:-1]
            ignore_not_installed = True
        else:
            modname = mx
            ignore_not_installed = False
        msg = "name(%s) .." % mx
        msg_log(False, ctx['level'] + 1, msg)
        module_ids = searchL8(ctx, model,
                              [('name', '=', modname)],
                              context=context)
        if not module_ids:
            msg, sts = set_msg('Module %s not found!',
                               modname,
                               ignore_not_installed)
            msg_log(ctx, ctx['level'] + 1, msg)
            if ctx['exit_onerror']:
                break
            else:
                continue
        if ctx['dry_run']:
            continue
        module = browseL8(ctx, model, module_ids[0])
        if module.state != 'installed':
            if cur_lang != 'en_US':
                cur_lang = 'en_US'
                set_user_lang(ctx, cur_lang)
            try:
                executeL8(ctx,
                          model,
                          'button_immediate_install',
                          module_ids)
                time.sleep(len(module.dependencies_id) + 1)
            except BaseException:
                msg = 'Error installing %s!' % modname
                msg_log(ctx, ctx['level'] + 1, msg)
        module = browseL8(ctx, model, module_ids[0])
        if module.state != 'installed':
            msg, sts = set_msg('Module %s not installed!',
                               modname,
                               ignore_not_installed)
            msg_log(ctx, ctx['level'] + 1, msg)
        if sts == STS_FAILED and ctx['exit_onerror']:
            break
    if cur_lang != user_lang:
        set_user_lang(ctx, user_lang)
    return sts


def act_install_language(ctx):
    """Install new language"""
    lang = ctx.get('lang', 'en_US')
    model = 'res.lang'
    ids = searchL8(ctx, model, [('code', '=', lang)])
    if not ids:
        ids = searchL8(ctx, model, [('code', '=', lang),
                                    ('active', '=', False)])
        if len(ids):
            msg = u"Activate language %s" % lang
            msg_log(ctx, ctx['level'], msg)
            writeL8(ctx, model, ids[0], {'active': True})
    if len(ids) == 0:
        msg = u"Install language %s" % lang
        msg_log(ctx, ctx['level'], msg)
        vals = {}
        vals['lang'] = lang
        vals['overwrite'] = True
        id = createL8(ctx, 'base.language.install', vals)
        executeL8(ctx,
                  'base.language.install',
                  'lang_install',
                  [id])
    if lang != 'en_US':
        msg = u"Translate language %s terms" % lang
        msg_log(ctx, ctx['level'], msg)
        id = createL8(ctx, 'base.update.translations', {'lang': lang})
        executeL8(ctx,
                  'base.update.translations',
                  'act_update',
                  [id])
    return STS_SUCCESS


def act_install_chart_of_account(ctx):
    """Install chart of account"""
    coa = ctx.get('chart_of_account',
                  'Italy - Piano dei conti Zeroincombenze(R)')
    msg = u"Install chart of account %s" % coa
    msg_log(ctx, ctx['level'], msg)
    return install_chart_of_account(ctx, coa)


def act_import_file(ctx):
    o_model = build_model_struct(ctx)
    if 'filename' in ctx:
        csv_fn = ctx['filename']
    elif 'model' not in o_model:
        msg = u"!Wrong import file!"
        msg_log(ctx, ctx['level'], msg)
        return STS_FAILED
    else:
        csv_fn = get_model_model(ctx, o_model).replace('.', '_') + ".csv"
    msg = u"Import file " + csv_fn
    msg_log(ctx, ctx['level'], msg)
    return import_file(ctx, o_model, csv_fn)


def act_import_config_file(ctx):
    if 'filename' in ctx:
        csv_fn = ctx['filename']
    msg = u"Import config file " + csv_fn
    msg_log(ctx, ctx['level'], msg)
    return import_config_file(ctx, csv_fn)


def act_check_coa(ctx):

    def set_acc_type(type_id, prefix):
        if type_id:
            for rec in browseL8(
                ctx, model, searchL8(
                    ctx, model, [('code', 'like', prefix)])):
                if rec.code.startswith(prefix):
                    writeL8(ctx, model, rec.id, {'user_type_id': type_id})

    msg = u"Check for chart of account"
    msg_log(ctx, ctx['level'], msg)
    model = 'account.account'
    for acc in browseL8(ctx, model, searchL8(ctx, model, [])):
        if acc.type in ('receivable', 'payable'):
            reconcile = True
        elif acc.type in ('income', 'expense', 'view', 'liquidity'):
            reconcile = False
        elif acc.name.find('IVA') >= 0 or \
                acc.name.find('VAT') >= 0 or \
                acc.name.find('TAX') >= 0:
            reconcile = False
        else:
            reconcile = None
        if reconcile is not None:
            if acc.reconcile != reconcile:
                writeL8(ctx, model, [acc.id], {'reconcile': reconcile})
    set_acc_type(env_ref(ctx, 'account.data_account_type_fixed_assets'), '120')
    set_acc_type(env_ref(ctx, 'account.data_account_type_fixed_assets'), '121')
    set_acc_type(env_ref(ctx, 'account.data_account_type_fixed_assets'), '122')
    set_acc_type(env_ref(ctx, 'account.data_account_type_fixed_assets'), '123')
    set_acc_type(env_ref(ctx, 'account.data_account_type_fixed_assets'), '124')
    set_acc_type(env_ref(ctx, 'account.data_account_type_equity'), '211')
    set_acc_type(env_ref(ctx, 'account.data_account_type_revenue'), '51')
    set_acc_type(env_ref(ctx, 'account.data_account_type_revenue'), '52')
    set_acc_type(env_ref(ctx, 'account.data_account_type_revenue'), '53')
    set_acc_type(env_ref(ctx, 'account.data_account_type_revenue'), '54')
    set_acc_type(env_ref(ctx, 'account.data_account_type_revenue'), '55')
    set_acc_type(env_ref(ctx, 'account.data_account_type_direct_costs'), '61')
    set_acc_type(env_ref(ctx, 'account.data_account_type_expenses'), '62')
    set_acc_type(env_ref(ctx, 'account.data_account_type_depreciation'), '65')
    set_acc_type(env_ref(ctx, 'account.data_account_type_other_income'), '73')
    return STS_SUCCESS


def act_check_tax(ctx):
    msg = u"Check for tax compliance"
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    model = 'italy.ade.tax.nature'
    tax_nature = {}
    for tax in browseL8(ctx, model, searchL8(ctx, model, [])):
        tax_nature[tax.code] = tax.id
        tax_nature[tax.id] = tax.code
    model = 'account.account'
    sale_vat_acc = searchL8(ctx, model, [('company_id', '=', company_id),
                                         ('code', '=', '260010')])
    purch_vat_acc = searchL8(ctx, model, [('company_id', '=', company_id),
                                          ('code', '=', '153010')])
    sale_def_acc = searchL8(ctx, model, [('company_id', '=', company_id),
                                         ('code', '=', '260030')])
    purch_def_acc = searchL8(ctx, model, [('company_id', '=', company_id),
                                          ('code', '=', '153030')])
    model = 'account.tax'
    for tax in browseL8(ctx, model, searchL8(
            ctx, model, [('company_id', '=', company_id)])):
        nature_id = False
        payability = False
        account_id = False
        if tax.amount:
            if tax.type_tax_use == 'sale':
                account_id = sale_vat_acc
            elif tax.type_tax_use == 'purchase':
                account_id = purch_vat_acc
            if tax.amount not in ():
                if ((ctx['majver'] < 9 and
                        not tax.parent_id and
                        abs(tax.amount) not in (0.04, 0.1, 0.21, .22)) or
                    (ctx['majver'] >= 9 and
                        not tax.parent_tax_ids and
                        abs(tax.amount) not in (4, 10, 21, 22))):
                    writeL8(ctx, model, [tax.id],
                            {'active': False})
                    msg = 'Tax code %s deactivated' % tax.description
                    msg_log(ctx, ctx['level'] + 1, msg)
            if re.search('[Aa]rt[ .]*17[ -./]ter', tax.name):
                payability = 'S'
            elif re.search('[Ss]plit[ -./][Pp]aym', tax.name):
                payability = 'S'
            elif re.search('cassa', tax.name):
                payability = 'D'
            if re.search('[Aa]rt[ .]*74[- .,]*c(omma)?[- ./]*[78][^0-9]',
                    tax.name):
                # N6.1: cessione rottami > Art. 74c7/8
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.1']
            elif re.search('[Aa]rt[ .]*74[- .,]*c(omma)?[- ./]*5[^0-9]',
                    tax.name):
                # N6.2: oro e argento > Art. 74c5
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.2']
            elif re.search(
                    '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etr.]*a[- ./]+bis',
                    tax.name):
                # N6.4: cessione fabbricati > Art. 17c6 lett.a-bis
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.4']
            elif re.search(
                '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etr.]*a[- ./]+ter',
                    tax.name):
                # N6.7: prestazioni comparto edile > Art. 17c6 lett.a-ter
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.7']
            elif re.search(
                    '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etra.]*b',
                    tax.name):
                # N6.4: cellulari > Art. 17c6 lett.b
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.5']
            elif re.search(
                    '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etra.]*b',
                    tax.name):
                # N6.4: cellulari > Art. 17c6 lett.c
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.6']
            elif re.search(
                    '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etra.]*a',
                    tax.name):
                # N6.4: subappalto edile > Art. 17c6 lett.a
                # Attenzione! Non spostare in alto
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.3']
            elif re.search(
                    '[Aa]rt[ .]*17[- .,]*c(omma)?[- ./]*6[- ./]*l[etra.]*d[- ./]+(ter|quater)',
                    tax.name):
                # N6.8: prestazioni energetichee > Art. 17c6 lett.d-ter/quater
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.8']
            elif re.search(
                    '[Aa]rt[ .]*4[12] *([a-zA-Z.](331|427).*)?$', tax.name):
                # N6.9: altri rc > Art. 41/42 DL.331
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.9']
                elif tax.type_tax_use == 'sale':
                    nature_id = tax_nature['N3.2']

            elif re.search('[Aa]rt[ .]*38[- .]*ter', tax.name):
                # N6.8: prestazioni energetichee > Art. 17c6 lett.d-ter/quater
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6.8']

            elif re.search('[Aa]rt[^0-9]38[^0-9]?', tax.name):
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6']
            elif re.search('[Aa]rt[^0-9]40[^0-9]?', tax.name):
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6']
            elif re.search('[Rr]ev[a-zA-Z]* [Cc]harge', tax.name):
                if tax.type_tax_use == 'purchase':
                    nature_id = tax_nature['N6']
            if payability in ('S', 'D'):
                if tax.type_tax_use == 'sale':
                    account_id = sale_def_acc
                elif tax.type_tax_use == 'purchase':
                    account_id = purch_def_acc
        else:
            if re.search('[Rr]eg[a-zA-Z]* [Mm]in', tax.name):
                nature_id = tax_nature['N2']
            elif re.search('[Rr](eg)?[a-zA-Z]* [Ff]orf', tax.name):
                nature_id = tax_nature['N2']
            elif re.search('[Aa]rt[^0-9]40[^0-9]?c[-./a-zA-Z]*[34][^0-9]', tax.name):
                nature_id = tax_nature['N7']
            elif re.search('[Aa]rt[^0-9]41[^0-9]?c[-./a-zA-Z]*1[^0-9]?.*b', tax.name):
                nature_id = tax_nature['N7']
            elif re.search('[Aa]rt[^0-9]7[^0-9]?[ -./]*sex.*f', tax.name):
                nature_id = tax_nature['N7']
            elif re.search('[Aa]rt[^0-9]74[^0-9]?[ -./]*sex', tax.name):
                nature_id = tax_nature['N7']
            elif re.search('[Rr]eg[a-zA-Z]* [Mm]arg', tax.name):
                nature_id = tax_nature['N5']
            elif re.search('[Ii][Vv][Aa] n[-./a-zA-Z] esp', tax.name):
                nature_id = tax_nature['N5']
            elif re.search('[Aa]rt[^0-9]10[^0-9]?', tax.name):
                nature_id = tax_nature['N4']
            elif re.search('[Aa]rt[^0-9][89][^0-9]', tax.name):
                nature_id = tax_nature['N3']
            elif re.search('[Aa]rt[^0-9]7[12][^0-9]', tax.name):
                nature_id = tax_nature['N3']
            elif re.search('[Aa]rt[^0-9]7[^0-9]?[ -./]*(bis|ter|quater|quinq)',
                           tax.name):
                nature_id = tax_nature['N2']
            elif re.search('[Aa]rt[^0-9]2[^0-9]', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Aa]rt[^0-9]3[^0-9]', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Aa]rt[^0-9]5[^0-9]', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Aa]rt[^0-9]13[^0-9]', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Aa]rt[^0-9]15[^0-9]', tax.name):
                nature_id = tax_nature['N1']
            elif re.match('[Ee]sente', tax.name):
                nature_id = tax_nature['N4']
            elif re.match(r'N\.?I\.?', tax.name):
                nature_id = tax_nature['N3']
            elif re.match('[Nn][a-zA-Z]* [Ii]mp', tax.name):
                nature_id = tax_nature['N3']
            elif re.match('[Nn][a-zA-Z]* [Ss]ogg', tax.name):
                nature_id = tax_nature['N2']
            elif re.match('[Ss]enza [Ii][Vv][Aa]', tax.name):
                nature_id = tax_nature['N2']
            elif re.match('[Ee]scl', tax.name):
                nature_id = tax_nature['N1']
            elif re.match(r'F\.?C\.?', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Ff]uori [Cc]ampo', tax.name):
                nature_id = tax_nature['N1']
            elif re.search('[Aa]rt[^0-9]17[^0-9][-./a-zA-Z]*', tax.name):
                nature_id = tax_nature['N1']
        vals = {}
        if nature_id:
            if ctx['majver'] < 9:
                vals = {
                    'nature_id': nature_id,
                    'non_taxable_nature': tax_nature[nature_id],
                }
            else:
                vals = {
                    'nature_id': nature_id,
                }
        if payability:
            vals['payability'] = payability
        if account_id:
            vals['vat_statement_account_id'] = account_id[0]
        if vals:
            writeL8(ctx, model, [tax.id], vals)
            if nature_id:
                msg = 'Tax code %s: nature=%s' % (tax.description,
                                                  tax_nature[nature_id])
            else:
                msg = 'Tax code %s: pay=%s' % (tax.description, payability)
            msg_log(ctx, ctx['level'] + 1, msg)
    return STS_SUCCESS


def act_check_xid(ctx):
    if not ctx['dry_run']:
        model = 'ir.model.data'
        ids = searchL8(ctx, model, [])
        for i, id in enumerate(ids):
            xref = browseL8(ctx, model, id)
            msg_burst(ctx['level'] + 1,
                      'xreference',
                      i,
                      len(ids))
            try:
                browseL8(ctx, xref.model, xref.res_id)
            except BaseException:
                print('!! Invalid external reference %s.%s' % (xref.module,
                                                               xref.name))
                unlinkL8(ctx, model, id)
    return STS_SUCCESS


def act_check_config(ctx):

    def cvt_rec_2_vals(rec):
        values = {'is_company': True, 'parent_id': False}
        for fld in ('name', 'street', 'zip', 'city', 'vat', 'customer',
                    'supplier'):
            values[fld] = rec[fld]
        for fld in ('country_id', 'state_id'):
            values[fld] = rec[fld].id
        return values

    def book_partner(avaiable_partner_ids, vals):
        if len(avaiable_partner_ids):
            new_part_id = avaiable_partner_ids.pop()
        else:
            new_part_id = createL8(ctx, model_partner, vals)
        return new_part_id, avaiable_partner_ids

    if ctx['dry_run'] or 'def_company_id' not in ctx:
        return STS_FAILED

    msg = u"Check config"
    msg_log(ctx, ctx['level'], msg)
    model = 'res.users'
    user_root = env_ref(ctx, 'base.user_root')
    user_demo = env_ref(ctx, 'base.user_demo')
    partner_root = env_ref(ctx, 'base.partner_root')
    main_company = env_ref(ctx, 'base.main_company')
    if user_root:
        writeL8(ctx, model, user_root,
                {
                    'company_ids': [(4, main_company)],
                })
        writeL8(ctx, model, user_root,
                {
                    'company_id': main_company,
                    'partner_id': partner_root,
                })
    if user_demo:
        writeL8(ctx, model, user_demo,
                {
                    'company_ids': [(4, main_company)],
                })
        writeL8(ctx, model, user_demo,
                {
                    'company_id': main_company,
                    'partner_id': partner_root,
                })

    model = 'ir.model.data'
    # Rename old state_id entries (Odoo 7.0 l10n_it_base)
    for xid in browseL8(ctx, model,
             searchL8(ctx, model, [('module', '=', 'l10n_it_base'),
                                   ('model', '=', 'res.county.state'),
                                   ('name', 'like', r'it\_%')])):
        if xid.name.startswith('it_') and len(xid.name) == 5:
            writeL8(ctx, model, xid.id, {
                'module': 'base',
                'name': 'state_%s' % xid.name.lower()})
            msg_log(
                ctx, ctx['level'] + 1,
                'External id %d renamed l10n_it_base -> base' % xid.id)
    # Rename old state_id entries (Odoo 7.0 l10n_it_bbone)
    for xid in searchL8(ctx, model, [('module', '=', 'l10n_it_bbone'),
                                     ('model', '=', 'res.county.state'),
                                     ('name', 'like', r'it\_%')]):
        if xid.name.startswith('it_') and len(xid.name) == 5:
            unlinkL8(ctx, model, [xid])
            msg_log(
                ctx, ctx['level'] + 1,
                'External id %d (l10n_it_bbone) removed' % xid.id)
    # Rename deprecated testing prefix (base2/z0incombenze)
    for xid in browseL8(ctx, model,
             searchL8(ctx, model, [('module', '=', 'base2')])):
        writeL8(ctx, model, xid.id, {'module': 'z0bug'})
        msg_log(
            ctx, ctx['level'] + 1,
            'External id %d renamed from base2 to z0bug' % xid.id)
    for xid in browseL8(ctx, model,
             searchL8(ctx, model, [('module', '=', 'z0incombenze')])):
        writeL8(ctx, model, xid.id, {'module': 'z0bug'})
        msg_log(
            ctx, ctx['level'] + 1,
            'External id %d renamed from z0incombenze to z0bug' % xid.id)
    # Check for testing environment
    ids = searchL8(ctx, model, [('module', '=', 'base'),
                                ('name', 'in', ('mycompany',
                                                'partner_mycompany',
                                                'user_admin2',
                                                'partner_admin2',
                                                'user_bot',
                                                'partner_bot'))])
    for id in ids:
        writeL8(ctx, model, id, {'module': 'z0bug'})
        msg_log(ctx, ctx['level'] + 1,
                'External id %d renamed from base to z0bug' % id)
    # Rename invoice refs
    invoice_xrefs = []
    for pfx in ('SO', 'PO'):
        for yr in ('17', '18', '19', '20'):
            for nr in ('01', '02', '03', '04', '05'):
                invoice_xrefs.append('invoice_%s%s%s' % (pfx, yr, nr))
    ids = searchL8(ctx, model, [('module', '=', 'account'),
                                ('name', 'in', invoice_xrefs)])
    for id in ids:
        writeL8(ctx, model, id, {'module': 'z0bug'})
        msg_log(ctx, ctx['level'] + 1,
                'External id %d renamed from account to z0bug' % id)
    # Search for partners with demo ref and testing refs that give errors
    # in Odoo update
    model_partner = 'res.partner'
    model_user = 'res.users'
    model_company = 'res.company'
    model_invoice = 'account.invoice'
    xref_names = {}
    xref_partner_ids = {}
    xref_ids = {}
    xref_dups = {}
    xref_dups_id = {}
    avaiable_xrefs = []
    replacement_list = {}
    for id in searchL8(ctx, model,
                       [('model', '=', model_partner)], order='module'):
        rec = browseL8(ctx, model, id)
        xname = '%s.%s' % (rec.module, rec.name)
        if xname == 'base.public_user_res_partner':
            continue
        part_id = rec.res_id
        if part_id in xref_partner_ids:
            # Duplicate id
            xref_dups[xname] = part_id
            xref_dups_id[xname] = id
        else:
            xref_partner_ids[part_id] = xname
            xref_names[xname] = part_id
            xref_ids[xname] = id
    excl_list_user = [x.partner_id.id for x in browseL8(
        ctx, model_user, searchL8(ctx, model_user, []))]
    excl_list_company = [x.partner_id.id for x in browseL8(
        ctx, model_company, searchL8(ctx, model_company, []))]
    excl_xref = [x.res_id for x in browseL8(
        ctx, model, searchL8(ctx, model,
                             [('model', '=', model_partner),
                              ('module', '!=', 'z0bug')]))]
    partners_no_use = excl_list_user + excl_list_company + excl_xref
    partners_no_use = list(set(partners_no_use))
    avaiable_partner_ids = searchL8(
        ctx, model_partner, [('id', 'not in', partners_no_use),
                             ('parent_id', '=', False)], order='id')
    for xname in xref_dups:
        part_id = xref_dups[xname]
        partner = browseL8(ctx, model_partner, part_id)
        vals = cvt_rec_2_vals(partner)
        if part_id in xref_partner_ids:
            new_id = xref_names[xref_partner_ids[part_id]]
        else:
            new_id, avaiable_partner_ids = book_partner(
                avaiable_partner_ids, vals)
        writeL8(ctx, model_partner, new_id, vals)
        replacement_list[part_id] = new_id
        xref_names[xname] = new_id
        xref_partner_ids[new_id] = xname
        xref_ids[xref_dups_id[xname]] = xname
        writeL8(ctx, model, xref_dups_id[xname], {'res_id': new_id})

    for ix in range(9):
        xname = 'z0bug.res_partner_%d' % (ix + 1)
        if xname in xref_names:
            continue
        avaiable_xrefs.append(xname)

    for part_id in excl_list_company:
        if part_id in excl_list_user:
            ids = searchL8(ctx, model_company,
                           [('partner_id', '=', part_id)])
            if ids:
                partner = browseL8(ctx, model_partner, part_id)
                vals = cvt_rec_2_vals(partner)
                new_id, avaiable_partner_ids = book_partner(
                    avaiable_partner_ids, vals)
                excl_list_company.append(new_id)
                partners_no_use.append(new_id)
                msg_log(ctx, ctx['level'] + 1,
                        'New partner no user id %d for the company %s' % (
                            new_id, vals['name']))
                writeL8(ctx, model_company, ids[0],
                        {'partner_id': new_id})
                msg_log(ctx, ctx['level'] + 1,
                        'Company id %d has a new partner id %d' % (
                            ids[0], new_id))
                ids2 = searchL8(ctx, model,
                                [('module', '=', 'z0bug'),
                                 ('model', '=', model_partner),
                                 ('res_id', '=', ids[0])])
                if ids2:
                    writeL8(ctx, model, ids2[0], {'res_id': new_id})
                    msg_log(ctx, ctx['level'] + 1,
                            'External id %d with new res_id %d' % (
                            ids2[0], new_id))
    z0_invoice_xid_list = searchL8(ctx, model,
                                   [('model', '=', model_invoice),
                                    ('module', '=', 'z0bug')])
    for inv_xid in browseL8(ctx, model, z0_invoice_xid_list):
        inv = browseL8(ctx, model_invoice, inv_xid.res_id)
        part_id = inv.partner_id.id
        if part_id in partners_no_use:
            partner = browseL8(ctx, model_partner, part_id)
            vals = cvt_rec_2_vals(partner)
            if part_id in xref_partner_ids:
                new_id = xref_names[xref_partner_ids[part_id]]
            else:
                new_id, avaiable_partner_ids = book_partner(
                    avaiable_partner_ids, vals)
            writeL8(ctx, model_partner, new_id, vals)
            replacement_list[part_id] = new_id

    for part_id in replacement_list:
        where = [('partner_id', '=', part_id)]
        if not ctx['db_name'].startswith('demo'):
            excl = []
            for xref in browseL8(
                    ctx, model, searchL8(
                        ctx, model, [('module', '=', 'z0bug'),
                                     ('name', 'in', invoice_xrefs)])):
                excl.append(xref, id)
            where.append(('id', 'in', excl))
        invoice_ids = searchL8(ctx, model_invoice, where)
        for inv in browseL8(ctx, model_invoice, invoice_ids):
            # inv_state = inv.state
            if inv.state in INVOICES_STS_2_DRAFT:
                reconcile_dict, move_dict = get_reconcile_from_invoices(
                    [inv.id], ctx)
                unreconcile_invoices(reconcile_dict, ctx)
                upd_invoices_2_draft(move_dict, ctx)
            writeL8(ctx, model_invoice, inv.id,
                    {'partner_id': replacement_list[inv.partner_id.id]})
            msg_log(ctx, ctx['level'] + 1,
                    'Invoice id %d, new partner id=%d' % (
                        inv.id, replacement_list[inv.partner_id.id]))
            if inv.state in INVOICES_STS_2_DRAFT:
                upd_invoices_2_posted(move_dict, ctx)
                reconciles = reconcile_dict[inv.id]
                if len(reconciles):
                    cur_reconciles, cur_reconcile_dict = \
                        refresh_reconcile_from_inv(
                            inv.id, reconciles, ctx)
                    reconcile_invoices(cur_reconcile_dict, ctx)

    DEMO_PARTNERS = {
        '1': {
            'name': 'ASUSTek',
            'supplier': True,
            'customer': False,
            'country_id': env_ref(ctx, 'base.tw'),
            'vat': False,
            'electronic_invoice_subjected': False,
        },
        '2': {
            'name': 'Agrolait',
            'supplier': False,
            'customer': True,
            'country_id': env_ref(ctx, 'base.be'),
            'vat': False,
            'electronic_invoice_subjected': False,
        },
        '3': {
            'name': 'China Export',
            'supplier': True,
            'customer': False,
            'country_id': env_ref(ctx, 'base.cn'),
            'vat': False,
            'electronic_invoice_subjected': False,
        },
        '4': {
            'name': 'Delta PC',
            'supplier': False,
            'customer': True,
            'country_id': env_ref(ctx, 'base.us'),
            'vat': False,
            'electronic_invoice_subjected': False,
        },
    }
    for id in DEMO_PARTNERS:
        ref = 'base.res_partner_%s' % id
        rec_id = env_ref(ctx, ref)
        if rec_id:
            writeL8(ctx, model_partner, rec_id, DEMO_PARTNERS[id])

    DEMO_PARTNERS = {
        '1': {
            'name': 'Prima Distribuzione S.p.A.',
            'supplier': True,
            'customer': True,
            'country_id': env_ref(ctx, 'base.it'),
            'vat': 'IT00115719999',
        },
        '2': {
            'name': 'Agro Latte Due  s.n.c.',
            'supplier': False,
            'customer': True,
            'country_id': env_ref(ctx, 'base.it'),
            'vat': 'IT02345670018',
        },
        '3': {
            'name': 'Import Export Trifoglio s.r.l.',
            'supplier': True,
            'customer': True,
            'country_id': env_ref(ctx, 'base.it'),
            'vat': 'IT01234560017',
        },
        '4': {
            'name': 'Delta 4 s.r.l.',
            'supplier': False,
            'customer': True,
            'country_id': env_ref(ctx, 'base.it'),
            'vat': 'IT06631580013',
        },
    }
    for id in DEMO_PARTNERS:
        ref = 'z0bug.res_partner_%s' % id
        rec_id = env_ref(ctx, ref)
        if rec_id:
            writeL8(ctx, model_partner, rec_id, DEMO_PARTNERS[id])

    return STS_SUCCESS


def act_check_partners(ctx):
    msg = u"Check for partners"
    msg_log(ctx, ctx['level'], msg)
    model = 'res.partner'

    italy_id = searchL8(ctx,
                        'res.country',
                        [('code', '=', 'IT')])[0]
    partner_ids = searchL8(ctx, 'res.partner', [])
    rec_ctr = 0
    for partner_id in partner_ids:
        try:
            partner = browseL8(ctx, model, partner_id)
        except BaseException:
            msg = u"Wrong partner id=%d" % partner_id
            msg_log(ctx, ctx['level'], msg)
            continue
        rec_ctr += 1
        msg_burst(4, 'Partner ',
                  rec_ctr,
                  partner.name)
        vals = {}
        if not partner.country_id and (partner.street or partner.city):
            vals['country_id'] = italy_id
            msg = u"Wrong country of %s (%d)" % (partner.name, partner.id)
            msg_log(ctx, ctx['level'], msg)
        elif partner.country_id:
            vals['country_id'] = partner.country_id.id
        else:
            vals['country_id'] = False
        if is_valid_field(ctx, model, 'province'):
            if (partner.province and
                    vals['country_id'] == italy_id and
                    not partner.state_id):
                state_ids = searchL8(ctx,
                                     'res.country.state',
                                     [('code', '=', partner.province.code),
                                      ('country_id', '=', vals['country_id'])])
                if state_ids:
                    vals['state_id'] = state_ids[0]
                    msg = u"Wrong province of %s" % partner.name
                    msg_log(ctx, ctx['level'], msg)

        if (not vals.get('state_id') and
                not partner.state_id and
                partner.zip and
                vals['country_id'] == italy_id):
            city_ids = searchL8(ctx,
                                'res.city',
                                [('zip', '=', partner.zip),
                                 ('country_id', '=', vals['country_id'])])
            if not len(city_ids):
                city_ids = searchL8(ctx,
                                    'res.city',
                                    [('zip', '=', '%s%%' % partner.zip[0:4]),
                                     ('country_id', '=', vals['country_id'])])
            if not len(city_ids):
                city_ids = searchL8(
                    ctx,
                    'res.city',
                    [('zip', '=', '%s%%%%' % partner.zip[0:3]),
                     ('country_id', '=', vals['country_id'])])
            state_id = None
            for id in city_ids:
                city = browseL8(ctx, 'res.city', id)
                if state_id is None:
                    state_id = city.state_id.id
                    msg = u"Wrong province of %s" % partner.name
                    msg_log(ctx, ctx['level'], msg)
                elif city.state_id.id != state_id:
                    state_id = False
                    break
            if state_id:
                vals['state_id'] = state_id

        if partner.vat:
            iso = partner.vat.upper()[0:2]
            vatn = partner.vat[2:]
            if iso != 'IT' and iso != partner.vat[0:2]:
                msg = u"Wrong VAT %s of %s" % (partner.vat, partner.name)
                vals['vat'] = iso + vatn
            if iso == 'IT':
                new_vat = partner.vat.upper().replace(' ', '')
                if new_vat != partner.vat:
                    vals['vat'] = new_vat
                    msg = u"Wrong VAT %s" % partner.vat
                    msg_log(ctx, ctx['level'], msg)
            elif (vals['country_id'] == italy_id and
                    partner.vat.isdigit() and
                    len(partner.vat) == 11):
                iso = 'IT'
                vatn = partner.vat
                vals['vat'] = iso + vatn
                msg = u"Wrong VAT %s of %s" % (partner.vat, partner.name)
                msg_log(ctx, ctx['level'], msg)
            elif iso < 'AA' or iso > 'ZZ':
                msg = '%s WRONG VAT' % partner.name
                msg_log(ctx, ctx['level'], msg)
            elif vatn.strip() == '':
                vals['vat'] = False
                msg = '%s WRONG VAT' % partner.name
                msg_log(ctx, ctx['level'], msg)
            if not partner.is_company:
                vals['is_company'] = True
                msg = '%s (%d) is company not person' % (
                    partner.name, partner.id)
                msg_log(ctx, ctx['level'], msg)

        if partner.fiscalcode and vals['country_id'] == italy_id:
            new_fc = partner.fiscalcode.upper()
            if new_fc != partner.fiscalcode.upper():
                vals['fiscalcode'] = new_fc
                msg = '%s wrong fiscalcode' % partner.name
                msg_log(ctx, ctx['level'], msg)

        if partner.zip:
            new_zip = partner.zip.strip()
            if new_zip != partner.zip:
                vals['zip'] = new_zip
                msg = '%s wrong zip' % partner.name
                msg_log(ctx, ctx['level'], msg)

        if (not vals['country_id'] or
                vals['country_id'] == partner.country_id.id):
            del vals['country_id']
        if vals:
            try:
                writeL8(ctx, 'res.partner', [partner_id], vals)
            except BaseException:
                msg = 'ERROR updating %s' % partner.name
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_set_periods(ctx):
    msg = u"Set account periods "
    msg_log(ctx, ctx['level'], msg)
    majver = ctx['majver']
    company_id = ctx['company_id']
    fiscalyear_id, process_it, last_name, last_start, last_stop = \
        read_last_fiscalyear(company_id, ctx)
    if process_it and fiscalyear_id == 0:
        name, date_start, date_stop = \
            evaluate_date_n_name(ctx,
                                 last_name,
                                 last_start,
                                 last_stop,
                                 'year')
        if majver < 10:
            model = 'account.fiscalyear'
            code = re.findall('[0-9./-]+', name)[0]
            fiscal_year_id = createL8(ctx, model, {
                'name': name,
                'code': code,
                'date_start': str(date_start),
                'date_stop': str(date_stop),
                'company_id': company_id})
        else:
            model = 'date.range.type'
            ids = searchL8(ctx, model,
                           [('company_id', '=', company_id),
                            ('name', '=', 'Annual')])
            if not ids:
                date_type_id = fiscal_year_id = createL8(
                    ctx, model, {
                        'name': 'Annual',
                        'company_id': company_id
                    })
            else:
                date_type_id = ids[0]
            model = 'date.range'
            fiscal_year_id = createL8(ctx, model, {
                'name': name,
                'date_start': str(date_start),
                'date_end': str(date_stop),
                'company_id': company_id,
                'type_id': date_type_id})
        msg = u"Added fiscalyear %s" % name
        msg_log(ctx, ctx['level'], msg)
        if majver < 10:
            add_periods(ctx,
                        company_id,
                        fiscal_year_id,
                        last_name,
                        last_start,
                        last_stop)
    if majver >= 10:
        add_periods(ctx,
                    company_id,
                    False,
                    last_name,
                    last_start,
                    last_stop)
    set_journal_per_year(ctx)
    return STS_SUCCESS


def act_check_tax_balance(ctx):
    msg = u"Check for tax balance; period: " + \
        ctx['date_start'] + ".." + ctx['date_stop']
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    period_ids = searchL8(ctx, 'account.period',
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    STATES = STATES_2_DRAFT
    if ctx['draft_recs']:
        STATES.append('draft')
    move_line_ids = searchL8(ctx, 'account.move.line',
                             [('company_id', '=', company_id),
                              ('period_id', 'in', period_ids),
                              ('state', '!=', 'draft')])
    tax_balance = {}
    num_moves = len(move_line_ids)
    move_ctr = 0
    for move_line_id in move_line_ids:
        move_line = browseL8(ctx,
                             'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        tax_code = move_line.tax_code_id
        if tax_code:
            # move_hdr_id = move_line.move_id.id
            level = '9'
            while True:
                code = tax_code.code
                name = tax_code.name
                if isinstance(code, basestring):
                    x = code
                else:
                    x = ''
                if isinstance(name, basestring):
                    x = x + ' - ' + name
                add_on_account(tax_balance,
                               level,
                               x,
                               move_line.tax_amount,
                               0)
                if not tax_code.parent_id:
                    break
                tax_code = tax_code.parent_id
                level = str(int(level) - 1)
    format = ctx.get('format', 'csv')
    for level in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        if level in tax_balance:
            if format == 'csv':
                ident = '%s,%s,%.2f'
            else:
                ident = '%-' + str(int(level) + 1) + 's'
                x = str(65 - int(level))
                ident = ident + ' %-' + x + '.' + x + 's'
                ident = ident + ' %13.2f'
            for kk in sorted(tax_balance[level]):
                msg = ident % (level, kk, tax_balance[level][kk])
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_ena_del_in_journal(ctx):
    """Enable delete flag of journals"""
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__)
    model = 'account.journal'
    return upd_del_in_journal(
        ctx, searchL8(ctx, model, [('update_posted', '=', False)]))


def act_dis_del_in_journal(ctx):
    """Disable delete flag of journals"""
    msg_log(ctx, ctx['level'],
            globals()[inspect.stack()[0][3]].__doc__)
    model = 'account.journal'
    return upd_del_in_journal(
        ctx, searchL8(ctx, model, [('update_posted', '=', True)]), value=False)


def act_check_balance(ctx):
    msg = u"Check for balance; period: " + \
        ctx['date_start'] + ".." + ctx['date_stop']
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    period_ids = searchL8(ctx, 'account.period',
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    acc_balance = {}
    acc_partners = {}
    STATES = STATES_2_DRAFT
    if ctx['draft_recs']:
        STATES.append('draft')
    move_line_ids = searchL8(ctx, 'account.move.line',
                             [('company_id', '=', company_id),
                              ('period_id', 'in', period_ids),
                              ('state', '!=', 'draft')])
    num_moves = len(move_line_ids)
    move_ctr = 0
    for move_line_id in move_line_ids:
        move_line = browseL8(ctx,
                             'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        warn_rec = False
        move_hdr_id = move_line.move_id.id
        account = move_line.account_id
        account_tax = move_line.account_tax_id
        journal = move_line.journal_id
        acctype_id = account.user_type.id
        acc_type = browseL8(ctx,
                            'account.account.type', acctype_id)
        if acc_type.report_type not in ("asset", "liability",
                                        "income", "expense"):
            warn_rec = "Untyped"
        if account.parent_id:
            parent_account = account.parent_id
            parent_acctype_id = parent_account.user_type.id
            parent_acc_type = browseL8(ctx, 'account.account.type',
                                       parent_acctype_id)
            parent_code = parent_account.code
        else:
            parent_account = None
            parent_acctype_id = 0
            parent_acc_type = None
            parent_code = None
            warn_rec = 'Orphan'
        if parent_acc_type and\
                parent_acc_type.report_type and\
                parent_acc_type.report_type != 'none':
            if parent_acc_type.report_type in ("asset",
                                               "liability",
                                               "income",
                                               "expense") and \
                    acc_type.report_type != parent_acc_type.report_type:
                warn_rec = "Mismatch"

        code = account.code
        clf3 = acc_type.name
        clf = acc_type.report_type
        if clf == "asset":
            clf2 = "attivo"
            clf1 = "patrimoniale"
        elif clf == "liability":
            clf2 = "passivo"
            clf1 = "patrimoniale"
        elif clf == "income":
            clf2 = "ricavi"
            clf1 = "conto economico"
        elif clf == "expense":
            clf2 = "costi"
            clf1 = "conto economico"
        else:
            clf2 = "unknown"
            clf1 = "unknown"

        if (account.company_id.id != company_id):
            msg = u"Invalid company account {0} in {1:>6}/{2:>6}  {3}".format(
                os0.u(code),
                move_hdr_id,
                move_line_id,
                os0.u(move_line.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (account_tax and account_tax.company_id.id != company_id):
            msg = u"Invalid company account tax {0} in {1:>6}/{2:>6}  {3}".\
                format(os0.u(code),
                       move_hdr_id,
                       move_line_id,
                       os0.u(move_line.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (journal and journal.company_id.id != company_id):
            msg = u"Invalid company journal {0} in {1:>6}/{2:>6}  {3}".format(
                os0.u(code),
                move_hdr_id,
                move_line_id,
                os0.u(move_line.ref))
            msg_log(ctx, ctx['level'] + 1, msg)

        if move_line.partner_id and \
                move_line.partner_id.id:
            partner_id = move_line.partner_id.id
            if clf3 == "Crediti":
                kk = 'C'
            elif clf3 == "Debiti":
                kk = 'S'
            else:
                kk = 'X'
            kk = kk + '\n' + code + '\n' + str(partner_id)
            if kk not in acc_partners:
                acc_partners[kk] = 0
            acc_partners[kk] += move_line.debit
            acc_partners[kk] -= move_line.credit

        level = '9'
        add_on_account(acc_balance,
                       level,
                       code,
                       move_line.debit,
                       move_line.credit)

        level = '8'
        add_on_account(acc_balance,
                       level,
                       parent_code,
                       move_line.debit,
                       move_line.credit)

        level = '4'
        add_on_account(acc_balance,
                       level,
                       clf3,
                       move_line.debit,
                       move_line.credit)

        level = '2'
        add_on_account(acc_balance,
                       level,
                       clf2,
                       move_line.debit,
                       move_line.credit)

        level = '1'
        add_on_account(acc_balance,
                       level,
                       clf1,
                       move_line.debit,
                       move_line.credit)

        level = '0'
        add_on_account(acc_balance,
                       level,
                       '_',
                       move_line.debit,
                       move_line.credit)

        if warn_rec:
            msg = u"Because {0:8} look at {1:>6}/{2:>6} record {3}".format(
                warn_rec,
                move_hdr_id,
                move_line_id,
                os0.u(move_line.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
            warn_rec = False

    if '0' in acc_balance:
        for level in ('0', '1', '2', '4', '8'):
            if level == '0':
                ident = "- {0:<10}".format('GT')
            elif level == '1':
                ident = " - {0:<9}".format('TOTALE')
            elif level == '2':
                ident = "  - {0:<8}".format('Totale')
            elif level == '4':
                ident = "   - {0:<7}".format('Grp')
            elif level == '8':
                ident = "    - {0:<6}".format('Mastro')
            else:
                ident = "     - {0:<5}".format('conto')
            crd_amt = 0.0
            dbt_amt = 0.0
            for sublevel in acc_balance[level]:
                if acc_balance[level][sublevel] > 0:
                    msg = u"{0} {1:<16} {2:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    crd_amt += acc_balance[level][sublevel]
                elif acc_balance[level][sublevel] < 0:
                    msg = u"{0} {1:<16} {2:11}{3:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        '', -acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    dbt_amt -= acc_balance[level][sublevel]
                else:
                    msg = u"{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        0,
                        0)
                    msg_log(ctx, ctx['level'], msg)
            msg = u"{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                os0.u(ident),
                '---------------',
                crd_amt,
                dbt_amt)
            msg_log(ctx, ctx['level'], msg)
        level = '9'
        for kk in sorted(acc_partners):
            if acc_partners[kk] != 0.0:
                partner_id = int(kk.split('\n')[2])
                partner = browseL8(ctx, 'res.partner', partner_id)
                msg = u"{0:<16} {1:<60} {2:11.2f}".format(
                    os0.u(kk.replace('\n', '.')),
                    os0.u(partner.name),
                    acc_partners[kk])
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_recompute_tax_balance(ctx):
    msg = u"Recompute tax balance"
    msg_log(ctx, ctx['level'], msg)
    sts = recompute_tax_balance(ctx)
    return sts


def act_recompute_balance(ctx):
    msg = u"Recompute balance"
    msg_log(ctx, ctx['level'], msg)
    sts = recompute_balance(ctx)
    return sts


def act_complete_partners(ctx):
    # It looks for partners to update and update them.
    msg = u"Convert partners"
    msg_log(ctx, ctx['level'], msg)
    italy_id = searchL8(ctx,
                        'res.country',
                        [('code', '=', 'IT')])[0]
    model = 'res.partner'
    if is_valid_field(ctx, model, 'province'):
        partner_ids = searchL8(ctx,
                               model,
                               [('province', '!=', None),
                                ('state_id', '=', None),
                                '|',
                                ('country_id', '=', False),
                                ('country_id', '=', italy_id)])
    else:
        partner_ids = []
    for i, partner_id in enumerate(partner_ids):
        partner = browseL8(ctx, 'res.partner', partner_id)
        msg_burst(4, '%-40.40s' % partner.name, i, len(partner_ids))
        vals = {}
        if not partner.country_id:
            vals['country_id'] = italy_id
        if partner.province:
            state_ids = searchL8(ctx,
                                 'res.country.state',
                                 [('code', '=', partner.province.code),
                                  ('country_id', '=', italy_id)])
            if state_ids:
                vals['state_id'] = state_ids[0]
        if vals:
            writeL8(ctx, 'res.partner', partner_id, vals)

    partner_ids = searchL8(ctx,
                           'res.partner',
                           [('state_id', '=', None),
                            '|',
                            ('country_id', '=', False),
                            ('country_id', '=', italy_id)])
    for i, partner_id in enumerate(partner_ids):
        partner = browseL8(ctx, 'res.partner', partner_id)
        msg_burst(4, '%-40.40s' % partner.name, i, len(partner_ids))
        vals = {}
        if partner.zip:
            city_ids = searchL8(ctx,
                                'res.city',
                                [('zip', '=', partner.zip),
                                 ('country_id', '=', italy_id)])
            if not len(city_ids):
                city_ids = searchL8(ctx,
                                    'res.city',
                                    [('zip', '=', '%s%%' % partner.zip[0:4]),
                                     ('country_id', '=', italy_id)])
            if not len(city_ids):
                city_ids = searchL8(
                    ctx,
                    'res.city',
                    [('zip', '=', '%s%%%%' % partner.zip[0:3]),
                     ('country_id', '=', italy_id)])
            state_id = None
            for id in city_ids:
                city = browseL8(ctx, 'res.city', id)
                if state_id is None:
                    state_id = city.state_id.id
                elif city.state_id.id != state_id:
                    state_id = False
                    break
            if state_id:
                vals['state_id'] = state_id
        if vals:
            if not partner.country_id:
                vals['country_id'] = italy_id
            writeL8(ctx, 'res.partner', partner_id, vals)
    return STS_SUCCESS


def act_set_4_cscs(ctx):
    msg = u"Set for cscs"
    msg_log(ctx, ctx['level'], msg)
    sts = set_account_type(ctx)
    return sts


def act_hard_clean_module(ctx):
    def drop_data_table(ctx, model, module_name):
        for id in searchL8(ctx, model, [('module', '=', module_name)]):
            try:
                unlinkL8(ctx, model, [id])
                msg_log(
                    ctx, ctx['level'] + 1,
                    'Record id %s.%d (%s) removed' % (model, id, module_name))
            except BaseException:
                pass

    msg = u"Hard_clean_module"
    msg_log(ctx, ctx['level'], msg)
    model = 'ir.module.module'
    for module_name in ctx['modules_2_manage']:
        ids = searchL8(ctx, model,
                       [('name', '=', module_name)])
        if not ids:
            continue
        module = browseL8(ctx, model, ids[0])
        if module.state == 'installed':
            continue
        try:
            unlinkL8(ctx, model, [module.id])
            msg = u"Clean module %s" % module_name
            msg_log(ctx, ctx['level'] + 1, msg)
        except BaseException:
            pass
        drop_data_table(ctx, 'ir.model.data', module_name)
        drop_data_table(ctx, 'ir.module.module.dependency', module_name)
        drop_data_table(ctx, 'ir.translation', module_name)
    return STS_SUCCESS


def act_upgrade_l10n_it_base(ctx):
    msg = u"Upgrade module l10n_it_base"
    msg_log(ctx, ctx['level'], msg)
    sts = act_update_modules(ctx)
    model = 'ir.module.module'
    ids = searchL8(ctx, model,
                   [('name', 'in', ['l10n_it_base',
                                    'l10n_it_spesometro',
                                    'zeroincombenze',
                                    'l10n_it_base_crm',
                                    'l10n_it_vat_registries',
                                    'l10n_it_fiscalcode',
                                    'l10n_it_rea',
                                    'l10n_it_fatturapa',
                                    'l10n_it_bbone'])])
    prior_state = {}
    # l10n_it_bb_id = 0
    l10n_it_bb_state = ''
    l10n_it_base_state = ''
    for id in ids:
        module_obj = browseL8(ctx, model, id)
        prior_state[id] = module_obj.state
        if module_obj.name == 'l10n_it_base':
            l10n_it_base_state = module_obj.state
        else:
            if module_obj.name == 'l10n_it_bbone':
                # l10n_it_bb_id = id
                l10n_it_bb_state = module_obj.state
            writeL8(ctx, model, [id], {'state': 'uninstalled'})
    if l10n_it_bb_state == 'installed' and l10n_it_base_state == 'installed':
        sts = cvt_ir_ui_view('l10n_it_bbone',
                             'l10n_it_base',
                             'res.city',
                             ctx)
    if l10n_it_bb_state == 'installed':
        for model in ('res.country',
                      'res.region',
                      'res.country.state',
                      'res.province',
                      'res.city'):
            sts = cvt_ir_model_data('l10n_it_bbone',
                                    'l10n_it_base',
                                    model,
                                    ctx)
    model = 'ir.module.module'
    for id in prior_state:
        state = prior_state[id]
        writeL8(ctx, model, [id], {'state': state})
    if l10n_it_base_state == 'installed':
        ctx['upgrade_modules'] = 'l10n_it_base'
        sts = act_upgrade_modules(ctx)
    if l10n_it_bb_state == 'installed':
        ctx['upgrade_modules'] = 'l10n_it_bbone'
        sts = act_upgrade_modules(ctx)
    ctx['upgrade_modules'] = ''
    s = ''
    for id in prior_state:
        module_obj = browseL8(ctx, model, id)
        if module_obj.name != 'l10n_it_base' and \
                module_obj.name != 'l10n_it_bbone' and \
                module_obj.name != 'zeroincombenze':
            ctx['upgrade_modules'] += s
            ctx['upgrade_modules'] += module_obj.name
            s = ','
    if ctx['upgrade_modules']:
        sts = act_upgrade_modules(ctx)
    return sts


def read_last_fiscalyear(company_id, ctx):
    majver = ctx['majver']
    if majver < 10:
        model = 'account.fiscalyear'
    else:
        model = 'date.range'
    fiscalyear_ids = searchL8(ctx, model,
                              [('company_id', '=', company_id)])
    if fiscalyear_ids:
        last_start = date(1970, 1, 1)
        last_stop = date(1970, 12, 31)
        process_it = False
        last_name = ''
    else:
        last_start = date(datetime.now().year - 1, 1, 1)
        last_stop = date(datetime.now().year - 1, 12, 31)
        process_it = True
        last_name = str(datetime.now().year - 1)
    valid_fiscalyear_id = 0
    for fiscalyear_id in fiscalyear_ids:
        fiscalyear = browseL8(ctx, model, fiscalyear_id)
        name = fiscalyear.name
        date_start = fiscalyear.date_start
        if majver < 10:
            date_stop = fiscalyear.date_stop
            # ids = searchL8(ctx, 'account.period',
            #                [('company_id', '=', company_id),
            #                 ('date_start', '>=', str(date_start)),
            #                 ('date_stop', '<=', str(date_stop))])
        else:
            date_stop = fiscalyear.date_end
            # ids = []
        if date_stop > last_stop:
            last_stop = date_stop
            if date_stop < date.today():
                process_it = True
                last_name = name
            else:
                valid_fiscalyear_id = fiscalyear_id
                process_it = False
                last_name = ''
            if date_start > last_start:
                last_start = date_start
    return valid_fiscalyear_id, process_it, last_name, last_start, last_stop


def add_periods(ctx, company_id, fiscalyear_id,
                last_name, last_start, last_stop):
    majver = ctx['majver']
    if majver < 10:
        model = 'account.period'
        period_ids = searchL8(ctx, model,
                              [('company_id', '=', company_id),
                               ('date_start', '>=', str(last_start)),
                               ('date_stop', '<=', str(last_stop))])
        for period_id in period_ids:
            period = browseL8(ctx, model, period_id)
            name = period.name
            date_start = period.date_start
            date_stop = period.date_stop
            special = period.special
            name, date_start, date_stop = \
                evaluate_date_n_name(ctx,
                                     name,
                                     date_start,
                                     date_stop,
                                     'period')
            ids = searchL8(ctx, model,
                           [('company_id', '=', company_id),
                            ('date_start', '=', str(date_start)),
                            ('date_stop', '=', str(date_stop)),
                            ('special', '=', special)])
            if len(ids) == 0:
                code = re.findall('[0-9./-]+', name)[0]
                createL8(ctx, model, {'name': name,
                                      'code': code,
                                      'fiscalyear_id': fiscalyear_id,
                                      'date_start': str(date_start),
                                      'date_stop': str(date_stop),
                                      'special': special,
                                      'company_id': company_id})
                msg = u"Added period %s" % name
                msg_log(ctx, ctx['level'], msg)
    else:
        model = 'date.range.type'
        ids = searchL8(ctx, model,
                       [('company_id', '=', company_id),
                        ('name', '=', 'Monthly')])
        if not ids:
            date_type_id = createL8(
                ctx, model, {
                    'name': 'Monthly',
                    'company_id': company_id
                })
        else:
            date_type_id = ids[0]
        model = 'date.range'
        for month in range(12):
            date_start = date(last_start.year, month + 1, 1)
            day = calendar.monthrange(last_start.year, month + 1)[1]
            date_stop = date(last_start.year, month + 1, day)
            name = '%d/%02d' % (last_start.year, month + 1)
            ids = searchL8(ctx, model,
                           [('company_id', '=', company_id),
                            ('date_start', '=', str(date_start)),
                            ('date_end', '=', str(date_stop))])
            if not ids:
                createL8(ctx, model, {'name': name,
                                      'date_start': str(date_start),
                                      'date_end': str(date_stop),
                                      'company_id': company_id,
                                      'type_id': date_type_id})
                msg = u"Added period %s" % name
                msg_log(ctx, ctx['level'], msg)

        model = 'date.range.type'
        ids = searchL8(ctx, model,
                       [('company_id', '=', company_id),
                        ('name', '=', 'Quarter')])
        if not ids:
            date_type_id = createL8(
                ctx, model, {
                    'name': 'Quarter',
                    'company_id': company_id
                    })
        else:
            date_type_id = ids[0]
        model = 'date.range'
        for quarter in range(4):
            bmonth = quarter * 3 + 1
            emonth = quarter * 3 + 3
            date_start = date(last_start.year, bmonth, 1)
            day = calendar.monthrange(last_start.year, emonth)[1]
            date_stop = date(last_start.year, emonth, day)
            name = '%d/%dQ' % (last_start.year, quarter + 1)
            ids = searchL8(ctx, model,
                           [('company_id', '=', company_id),
                            ('date_start', '=', str(date_start)),
                            ('date_end', '=', str(date_stop))])
            if not ids:
                createL8(ctx, model, {'name': name,
                                      'date_start': str(date_start),
                                      'date_end': str(date_stop),
                                      'company_id': company_id,
                                      'type_id': date_type_id})
                msg = u"Added period %s" % name
                msg_log(ctx, ctx['level'], msg)


def set_journal_per_year(ctx):
    company_id = ctx['company_id']
    majver = ctx['majver']
    if majver < 10:
        model = 'account.fiscalyear'
        fy_ids = searchL8(ctx, model, [('company_id', '=', company_id)])
        if len(fy_ids) == 0:
            return
        fy_name = ''
        last_date = date(1970, 1, 1)
        for id in fy_ids:
            if browseL8(ctx,  model, id).date_stop > last_date:
                last_date = browseL8(ctx, model, id).date_stop
                fy_name = str(last_date.year)
    else:
        model = 'date.range'
        fy_ids = searchL8(ctx, model, [('company_id', '=', company_id)])
        if len(fy_ids) == 0:
            return
        fy_name = ''
        date_stop = date(1970, 1, 1)
        for id in fy_ids:
            if browseL8(ctx,  model, id).date_end > date_stop:
                date_stop = browseL8(ctx, model, id).date_end
                date_start = browseL8(ctx, model, id).date_start
    model = 'account.journal'
    journal_ids = searchL8(ctx,
                           model, [('company_id', '=', company_id),
                                   ('type', '!=', 'situation')])
    primary_ir_sequences = []
    for journal_id in journal_ids:
        id = browseL8(ctx, model, journal_id)
        primary_ir_sequences.append(id.sequence_id.id)
    if len(primary_ir_sequences) == 0:
        return
    model = 'ir.sequence'
    ir_ids = searchL8(ctx, model,
                      [('company_id', '=', company_id),
                       ('id', 'in', primary_ir_sequences)])
    for ir_id in ir_ids:
        ir_sequence = browseL8(ctx, model, ir_id)
        fy = []
        if majver < 10:
            for o in ir_sequence.fiscal_ids:
                fy_id = o.fiscalyear_id.id
                fy.append(fy_id)
            for fy_id in fy_ids:
                if fy_id not in fy:
                    fy_name = str(browseL8(ctx, 'account.fiscalyear',
                                           fy_id).date_stop.year)
                    vals = {}
                    name = ir_sequence.name
                    if len(name) > 59:
                        vals['name'] = name[0:59] + ' ' + fy_name
                    else:
                        vals['name'] = name + ' ' + fy_name
                    vals['implementation'] = ir_sequence.implementation
                    vals['prefix'] = ir_sequence.prefix
                    vals['suffix'] = ir_sequence.suffix
                    vals['number_next'] = 1
                    vals['number_increment'] = ir_sequence.number_increment
                    vals['padding'] = ir_sequence.padding
                    vals['company_id'] = company_id
                    vals['code'] = False
                    pfx = vals['prefix']
                    sfx = vals['suffix']
                    if vals['prefix']:
                        vals['prefix'] = vals['prefix'].replace('%(year)s',
                                                                fy_name)
                    if vals['suffix']:
                        vals['suffix'] = vals['suffix'].replace('%(year)s',
                                                                fy_name)
                    if pfx != vals['prefix'] or sfx != vals['suffix']:
                        new_id = createL8(ctx, model, vals)
                        createL8(ctx, 'account.sequence.fiscalyear',
                                 {'sequence_id': new_id,
                                  'sequence_main_id': ir_id,
                                  'fiscalyear_id': fy_id})
            for asf_id in searchL8(ctx, 'account.sequence.fiscalyear',
                                   [('sequence_main_id', '=', ir_id)]):
                id = browseL8(ctx, 'account.sequence.fiscalyear',
                              asf_id).sequence_id.id
                fy_id = browseL8(ctx, 'account.sequence.fiscalyear',
                                 asf_id).fiscalyear_id.id
                fy_name = str(browseL8(ctx, 'account.fiscalyear',
                                       fy_id).date_stop.year)
                name = browseL8(ctx, model, id).name
                if not name.endswith(' ' + fy_name):
                    vals = {}
                    if name.endswith(fy_name):
                        name = name[0: -4]
                    if len(name) > 59:
                        vals['name'] = name[0:59] + ' ' + fy_name
                    else:
                        vals['name'] = name + ' ' + fy_name
                    writeL8(ctx, model, [id], vals)
        else:
            found_range = False
            for o in ir_sequence.date_range_ids:
                if o.date_from >= date_start and o.date_to <= date_stop:
                    found_range = True
                    break
            if not found_range:
                createL8(ctx,
                         'ir.sequence.date_range',
                         {'sequence_id': ir_id,
                          'date_from': str(date_start),
                          'date_to': str(date_stop),
                          'number_next': 1})


def evaluate_date_n_name(ctx, last_name, last_start, last_stop, yp):
    if yp == 'range':
        yp_year = last_start.year
    else:
        yp_year = last_start.year + 1
    if yp == 'year':
        date_start = last_stop + timedelta(1)
    else:
        if last_start.day >= 28:
            day = calendar.monthrange(yp_year, last_start.month)[1]
        else:
            day = last_start.day
        date_start = date(yp_year,
                          last_start.month,
                          day)
    if yp == 'range':
        yp_year = last_stop.year
    else:
        yp_year = last_stop.year + 1
    if last_stop.day >= 28:
        day = calendar.monthrange(yp_year, last_stop.month)[1]
    else:
        day = last_stop.day
    date_stop = date(yp_year,
                     last_stop.month,
                     day)
    n = yp_year % 100
    o = last_stop.year % 100
    name = last_name.replace(str(o), str(n))
    n = o
    o = (yp_year - 1) % 100
    name = name.replace(str(o), str(n))
    return name, date_start, date_stop


def get_payment_info(move_line, ctx):
    """Return move (header) and move_line (detail) ids of passed move line
    record and return payment state if needed to become draft
    """
    move_line_id = move_line.id
    move_id = move_line.move_id.id
    move_obj = browseL8(ctx, 'account.move', move_id)
    mov_state = False
    if move_obj.state in PAY_MOVE_STS_2_DRAFT:
        mov_state = move_obj.state
    return move_id, move_line_id, mov_state


def get_reconcile_from_inv(inv_id, ctx):
    """Return a list of reconciled move lines of passed (included) invoice
    List may be used to set unreconcile all movements, set draft all of them,
    update something and then reconcile again all movements.
    If there no reconcile movements, returned list is empty
    @param inv_id: invoice (header) id
    @return: list of reconciled move lines of passed (included) invoice
    @return: dictionary of posted movements (header) to set to draft state
    """
    # Payment move line (detail) list
    reconciles = []
    # For every state, store move (header) list to update state
    move_dict = {}
    for state in STATES_2_DRAFT:
        move_dict[state] = []
    model = 'account.invoice'
    account_invoice = browseL8(ctx, model,
                               inv_id)
    if ctx['majver'] >= 10:
        if account_invoice.payment_move_line_ids:
            for move_line_id in account_invoice.payment_move_line_ids:
                reconciles.append(move_line_id.id)
    elif account_invoice.payment_ids:
        partner_id = account_invoice.partner_id.id
        move_id = account_invoice.move_id.id
        move_line_ids = searchL8(ctx, 'account.move.line',
                                 [('move_id', '=', move_id),
                                  ('partner_id', '=', partner_id), ])
        for move_line_id in move_line_ids:
            # type = browseL8(ctx, 'account.account',
            #                 browseL8(ctx, 'account.move.line',
            #                          move_line_id).account_id.id).type
            type = browseL8(ctx, 'account.move.line',
                move_line_id).account_id.type
        if type in ('receivable', 'payable'):
            reconciles.append(move_line_id)
        for move_line in account_invoice.payment_ids:
            move_id, move_line_id, mov_state = \
                get_payment_info(move_line, ctx)
            reconciles.append(move_line_id)
            if mov_state:
                move_dict[state].append(move_id)
    if account_invoice.state in INVOICES_STS_2_DRAFT:
        move_dict[account_invoice.state].append(inv_id)
    return reconciles, move_dict


def refresh_reconcile_from_inv(inv_id, reconciles, ctx):
    """If invoice state is update to draft and returned to open, linked
    account move is changed. So move_id and all move_line_ids read by
    'get_reconcile_from_inv' and/or 'get_reconcile_list_from_move_line'
    are no more valid, while payments reference are still valid.
    So all invoice reference are update with new reference.
    @ param inv_id: invoice (header) id (CANNOT BE CHANGED BY PRIOR READ)
    @ param reconciles: prior reconciled move lines
    @ return: list of reconciled move lines of passed (included) invoice
    @ return: dictionary of posted movements (header) to set to draft state
    """
    # Payment move line (detail) list
    new_reconciles = []
    model = 'account.invoice'
    account_invoice = browseL8(ctx, model,
                               inv_id)
    partner_id = account_invoice.partner_id.id
    if account_invoice.move_id:
        move_id = account_invoice.move_id.id
    else:
        move_id = False
    move_line_ids = searchL8(ctx, 'account.move.line',
                             [('move_id', '=', move_id)])
    for move_line_id in move_line_ids:
        if ctx['majver'] >= 10:
            type = browseL8(ctx, 'account.move.line',
                move_line_id).account_id.user_type_id.type
        else:
            # type = browseL8(ctx, 'account.account',
            #                 browseL8(ctx, 'account.move.line',
            #                          move_line_id).account_id.id).type
            type = browseL8(ctx, 'account.move.line',
                move_line_id).account_id.type
        if type in ('receivable', 'payable'):
            new_reconciles.append(move_line_id)
    partner_id = account_invoice.partner_id.id
    if account_invoice.move_id:
        move_id = account_invoice.move_id.id
    else:
        move_id = False
    company_id = account_invoice.company_id.id
    valid_recs = True
    for move_line_id in reconciles[1:]:
        try:
            move_line = browseL8(ctx,
                                 'account.move.line', move_line_id)
        except BaseException:
            move_line = False
        if move_line:
            if move_line.partner_id.id != partner_id or \
                    move_line.company_id.id != company_id:
                valid_recs = False
            else:
                new_reconciles.append(move_line_id)
    if not valid_recs:
        new_reconciles = []
    reconcile_dict = {inv_id: new_reconciles}
    return new_reconciles, reconcile_dict


def get_user_lang(ctx):
    model = 'res.users'
    user_id = ctx.get('user_id', 1)
    user = browseL8(ctx, model, user_id)
    if not user:
        msg = u"!User %s not found" % user_id
        msg_log(ctx, ctx['level'] + 2, msg)
        return False
    return get_res_users(ctx, user, 'lang')


def set_user_lang(ctx, lang):
    model = 'res.users'
    user_id = ctx.get('user_id', 1)
    user = browseL8(ctx, model, user_id)
    if not user:
        msg = u"!User %s not found" % user_id
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    try:
        writeL8(ctx, 'res.users', user_id, {'lang': lang})
    except BaseException:
        msg = u"!Language %s not found" % lang
        msg_log(ctx, ctx['level'] + 2, msg)
    return STS_SUCCESS


def get_reconcile_list_from_move_line(move_line, ctx):
    """Like get_reconcile_from_inv but it is passed move_line id
    If move_line is not of an invoice, returned lists are empties.
    @param move_line: record of move_line (may be invoice or not)
    @return: list of reconciled move lines of passed (included) invoice
    @return: dictionary of posted movements (header) to set to draft state
    """
    # For every invoice id, store payment move line (detail) list
    reconcile_dict = {}
    # For every state, store move (header) list to update state
    move_dict = {}
    for state in STATES_2_DRAFT:
        move_dict[state] = []
    move_id = move_line.move_id.id
    model = 'account.invoice'
    invoice_ids = searchL8(ctx, model,
                           [('move_id', '=', move_id)])
    if len(invoice_ids):
        for inv_id in invoice_ids:
            reconciles, inv_move_dict = \
                get_reconcile_from_inv(inv_id,
                                       ctx)
            for state in STATES_2_DRAFT:
                if len(inv_move_dict[state]):
                    move_dict[state] = list(set(move_dict[state]) |
                                            set(inv_move_dict[state]))
            if inv_id in reconcile_dict:
                reconcile_dict[inv_id] = \
                    list(set(reconcile_dict[inv_id]) | reconciles)
            else:
                reconcile_dict[inv_id] = reconciles
    else:
        move_id, move_line_id, mov_state = get_payment_info(move_line,
                                                            ctx)
        if mov_state:
            move_dict[mov_state].append(move_id)
    return reconcile_dict, move_dict


def get_reconcile_from_invoices(invoices, ctx):
    """Search for payments of all invoices and return reconcile list
    List may be used to set unreconcile all movements, set draft all of them,
    update something and then reconcile again all movements.
    @param invoices: invoice (header) list
    @return: dictionary of reconciled move lines of passed (included) invoice
    @return: list of posted payments to set draft
    @return: flag true if invoice is to set in draft state to update
    """
    reconcile_dict = {}
    move_dict = {}
    for state in STATES_2_DRAFT:
        move_dict[state] = []
    if len(invoices):
        for inv_id in invoices:
            inv_reconciles, inv_move_dict = \
                get_reconcile_from_inv(inv_id,
                                       ctx)
            reconcile_dict[inv_id] = inv_reconciles
            for state in STATES_2_DRAFT:
                if len(inv_move_dict[state]):
                    move_dict[state] = list(set(move_dict[state]) |
                                            set(inv_move_dict[state]))
    return reconcile_dict, move_dict


def upd_del_in_journal(ctx, journals, value=None):
    """Before set invoices to draft, invoice has to set in cancelled state.
    To do this, journal has to be enabled
    @param journals: journal list to enable update_posted
    """
    value = value if isinstance(value, bool) else True
    if len(journals):
        vals = {'update_posted': value}
        try:
            msg = u"Journals %s: update_posted=%s " % (str(journals), value)
            msg_log(ctx, ctx['level'], msg)
            writeL8(ctx, 'account.journal', journals, vals)
        except BaseException:
            msg = u"Cannot update journals %s" % str(journals)
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def put_invoices_record_date(invoices, min_rec_date, ctx):
    """Update invoices (header) list/dictionary registration_date and period_id
    Notice:
        All invoices MUST be in draft or cancelled state
        All invoices must belong to the same journal and company
    @ param invoices:     invoices (header) list
    @ param min_rec_date: last record date; record date may not be less than
                          this value
    @ return: min record date
    """
    model = 'account.invoice'
    invoice_model = ctx['odoo_session'].get(model)
    list_keys = {}
    company_id = None
    journal_id = None
    move_name = translate_from_to(ctx,
                                  model,
                                  'move_name'
                                  '10.0',
                                  ctx['oe_version'])
    for inv_id in invoices:
        invoice = invoice_model.browse(inv_id)
        if not company_id:
            company_id = invoice.company_id.id
        elif invoice.company_id.id != company_id:
            return None
        if not journal_id:
            journal_id = invoice.journal_id.id
        elif invoice.journal_id.id != journal_id:
            return None
        if invoice[move_name]:
            list_keys[invoice[move_name]] = inv_id
    for internal_number in sorted(list_keys):
        inv_id = list_keys[internal_number]
        vals = {}
        invoice = invoice_model.browse(inv_id)
        date_invoice = invoice.date_invoice
        registration_date = invoice.registration_date
        inv_type = invoice.type
        if invoice.move_id:
            move_id = invoice.move_id.id
        else:
            move_id = False
        if inv_type in ('out_invoice', 'out_refund'):
            if not registration_date and date_invoice:
                vals['registration_date'] = str(date_invoice)
                registration_date = date_invoice
            elif not date_invoice:
                if registration_date:
                    vals['date_invoice'] = str(registration_date)
                    date_invoice = registration_date
                elif min_rec_date:
                    vals['date_invoice'] = str(min_rec_date)
                    date_invoice = min_rec_date
            if registration_date != date_invoice:
                if registration_date < date_invoice:
                    vals['registration_date'] = str(date_invoice)
                    registration_date = date_invoice
                elif date_invoice and min_rec_date and \
                        date_invoice >= min_rec_date:
                    vals['registration_date'] = str(date_invoice)
                    registration_date = date_invoice
                elif date_invoice and not min_rec_date:
                    vals['registration_date'] = str(date_invoice)
                    registration_date = date_invoice
                elif min_rec_date:
                    vals['registration_date'] = str(min_rec_date)
                    registration_date = min_rec_date
            if min_rec_date and registration_date < min_rec_date:
                vals['registration_date'] = str(min_rec_date)
                registration_date = min_rec_date
        elif inv_type in ('in_invoice', 'in_refund'):
            if min_rec_date and registration_date and \
                    registration_date < min_rec_date:
                vals['registration_date'] = str(min_rec_date)
                registration_date = min_rec_date
            elif min_rec_date and not registration_date:
                vals['registration_date'] = str(min_rec_date)
                registration_date = min_rec_date
        if not min_rec_date or \
                (registration_date and registration_date < min_rec_date):
            min_rec_date = registration_date
        if len(vals):
            period_ids = executeL8(ctx,
                                   'account.period',
                                   'find',
                                   str(registration_date))
            period_id = period_ids and period_ids[0] or False
            vals['period_id'] = period_id
            try:
                writeL8(ctx, model, [inv_id], vals)
            except BaseException:
                msg = u"Cannot update registration date of %d" % inv_id
                msg_log(ctx, ctx['level'], msg)
            if 'registration_date' in vals and move_id:
                writeL8(ctx, 'account.move',
                        [move_id],
                        {'date': vals['registration_date']})
                move_line_ids = searchL8(ctx, 'account.move.line',
                                         [('move_id', '=', move_id)])
                for move_line_id in move_line_ids:
                    writeL8(ctx, 'account.move.line',
                            [move_line_id],
                            {'date': vals['registration_date']})
    return min_rec_date


def upd_invoices_2_cancel(move_dict, ctx):
    """Set invoices (header) list/dictionary to cancel state.
    See upd_invoices_2_posted to return in posted state
    @ param move_dict: invoices (header) dictionary keyed on state or
                       invoices list to set in draft state
    """
    model = 'account.invoice'
    for i, state in enumerate(INVOICES_STS_2_DRAFT):
        invoices = []
        if isinstance(move_dict, dict):
            invoices = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            invoices = move_dict
        if len(invoices):
            try:
                executeL8(ctx, model,
                          'action_invoice_cancel',
                          invoices)
            except BaseException:
                # zero-amount invoices have not payments so keep 'paid' state
                for inv_id in invoices:
                    if browseL8(ctx, model, inv_id).state == 'paid':
                        try:
                            writeL8(ctx, model,
                                    [inv_id],
                                    {'state': 'cancel'})
                        except BaseException:
                            msg = u"Cannot update invoice status (%d)" % inv_id
                            msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def upd_invoices_2_draft(move_dict, ctx):
    """Set invoices (header) list/dictionary to draft state.
    See upd_invoices_2_posted to return in posted state
    @ param move_dict: invoices (header) dictionary keyed on state or
                       invoices list to set in draft state
    """
    model = 'account.invoice'
    passed = []
    for i, state in enumerate(INVOICES_STS_2_DRAFT):
        invoices = []
        if isinstance(move_dict, dict):
            invoices = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            invoices = move_dict
        if len(invoices):
            try:
                executeL8(ctx,
                          model,
                          'action_invoice_cancel',
                          invoices)
            except RuntimeError:
                # zero-amount invoices have not payments so keep 'paid' state
                for inv_id in invoices:
                    if browseL8(ctx, model, inv_id).state == 'paid':
                        try:
                            writeL8(ctx, model,
                                    [inv_id],
                                    {'state': 'draft'})
                            passed.append(inv_id)
                        except BaseException:
                            msg = u"Cannot update invoice status (%d)" % inv_id
                            msg_log(ctx, ctx['level'], msg)
                invoices = list(set(invoices) - set(passed))
            try:
                executeL8(ctx,
                          model,
                          'action_invoice_draft',
                          invoices)
            except BaseException:
                msg = u"Cannot update invoice status %s" % str(invoices)
                msg_log(ctx, ctx['level'], msg)
                return STS_FAILED
    return STS_SUCCESS


def upd_invoices_2_posted(move_dict, ctx):
    """Set invoices (header) list/dictionary to posted state.
    See upd_invoices_2_draft  to set in draft state before execute this one.
    @ param move_dict: invoices (header) dictionary keyed on state or
                       invoices list to set in posted state
    """
    model = 'account.invoice'
    sts = STS_SUCCESS
    for i, state in enumerate(INVOICES_STS_2_DRAFT):
        invoices = []
        if isinstance(move_dict, dict):
            invoices = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            invoices = move_dict
        if len(invoices):
            # msg = u"Restore invoices to validated %s " % invoices
            # msg_log(ctx, ctx['level'], msg)
            for inv_id in invoices:
                try:
                    execute_action_L8(ctx, model,
                                      'action_invoice_open',
                                      inv_id)
                except RuntimeError:
                    msg = u"Cannot restore invoice status of %d" % inv_id
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
                #
                inv = browseL8(ctx, 'account.invoice', inv_id)
                if inv.comment:
                    i = inv.comment.find('\a\axml_id=')
                    if i >= 0:
                        atts = inv.comment[i:]
                        comment = inv.comment[0:i]
                        fatturapa_attachment_out_id = eval(atts[8:])
                        try:
                            writeL8(ctx, 'account.invoice', inv_id,
                                    {'fatturapa_attachment_out_id':
                                        fatturapa_attachment_out_id,
                                     'comment': comment})
                        except BaseException:
                            return 1
    return sts


def upd_payments_2_draft(move_dict, ctx):
    """Set payments (header) list/dictionary to draft state.
    See upd_payments_2_posted to return in posted state
    @ param move_dict: payments (header) dictionary keyed on state or
                       payments list to set in draft state
    """
    for i, state in enumerate(PAY_MOVE_STS_2_DRAFT):
        payments = []
        if isinstance(move_dict, dict):
            payments = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            payments = move_dict
        if len(payments):
            try:
                # msg = u"Update payments to draft %s" % payments
                # msg_log(ctx, ctx['level'], msg)
                executeL8(ctx,
                          'account.move',
                          'button_cancel',
                          payments)
            except BaseException:
                msg = u"Cannot update payment status %s" % str(payments)
                msg_log(ctx, ctx['level'], msg)
                return STS_FAILED
    return STS_SUCCESS


def upd_payments_2_posted(move_dict, ctx):
    """Set payments (header) list/dictionary to posted state.
    See upd_payments_2_draft  to set in draft state before execute this one.
    @ param move_dict: payments (header) dictionary keyed on state or
                       payments list to set in posted state
    """
    for i, state in enumerate(PAY_MOVE_STS_2_DRAFT):
        payments = []
        if isinstance(move_dict, dict):
            payments = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            payments = move_dict
        if len(payments):
            try:
                # msg = u"Restore payments to posted %s" % payments
                # msg_log(ctx, ctx['level'], msg)
                executeL8(ctx,
                          'account.move',
                          'button_validate',
                          payments)
            except BaseException:
                msg = u"Cannot restore payment status %s" % str(payments)
                msg_log(ctx, ctx['level'], msg)
                return STS_FAILED
    return STS_SUCCESS


def upd_movements_2_draft(move_dict, ctx):
    """Set invoice and payments (header) dict to draft state.
    See upd_movements_2_posted to return in posted state
    Notice: do not pass a list (like called functions); dictionary is needed
    to recognize invoices from payments.
    @param move_dict: invoices & payments (header) dictionary keyed on state
    """
    sts = upd_payments_2_draft(move_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_invoices_2_draft(move_dict, ctx)
    return sts


def upd_movements_2_posted(move_dict, ctx):
    """Set invoice and payments (header) dict to posted state.
    See upd_movements_2_draft to set in draft state before execute this one.
    Notice: do not pass a list (like called functions); dictionary is needed
    to recognize invoices from payments.
    @param move_dict: invoices & payments (header) dictionary keyed on state
    """
    sts = upd_invoices_2_posted(move_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_payments_2_posted(move_dict, ctx)
    return sts


def unreconcile_invoices(reconcile_dict, ctx):
    for inv_id in reconcile_dict:
        try:
            context = {'active_ids': reconcile_dict[inv_id]}
            executeL8(ctx,
                      'account.unreconcile',
                      'trans_unrec',
                      None,
                      context)
        except BaseException:
            msg = u"Cannot update invoice status of %d" % inv_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def unreconcile_payments(ctx):
    msg = u"Unreconcile payments"
    msg_log(ctx, ctx['level'], msg)
    reconciled_name = translate_from_to(ctx,
                                        'account.move.line',
                                        'reconciled',
                                        '7.0',
                                        ctx['oe_version'])
    reconcile_list = searchL8(ctx, 'account.move.line',
                              [(reconciled_name, '!=', False)])
    try:
        context = {'active_ids': reconcile_list}
        executeL8(ctx,
                  'account.unreconcile',
                  'trans_unrec',
                  None,
                  context)
    except BaseException:
        msg = u"Cannot update payment status %s" % str(reconcile_list)
        msg_log(ctx, ctx['level'], msg)
        return STS_FAILED
    return STS_SUCCESS


def reconcile_invoices(reconcile_dict, ctx):
    for inv_id in reconcile_dict:
        msg = u"Reconcile invoice %d" % inv_id
        msg_log(ctx, ctx['level'], msg)
        try:
            context = {'active_ids': reconcile_dict[inv_id]}
            executeL8(ctx,
                      'account.move.line.reconcile',
                      'trans_rec_reconcile_partial_reconcile',
                      None,
                      context)
        except BaseException:
            msg = u"Cannot reconcile invoice of %d" % inv_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def upd_acc_2_bank(accounts, ctx):
    if len(accounts):
        vals = {}
        vals['type'] = 'liquidity'
        vals['user_type'] = 4
        try:
            msg = u"Update accounts " + str(accounts)
            msg_log(ctx, ctx['level'], msg)
            writeL8(ctx, 'account.account', accounts, vals)
        except BaseException:
            msg = u"Cannot update accounts %s" % str(accounts)
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def cvt_ir_ui_view(old_module, new_module, model_name, ctx):
    model = 'ir.ui.view'
    # name = old_module + '.%'
    id1 = searchL8(ctx, model, [('xml_id', '=like', old_module),
                                ('model', '=', model_name)])
    id2 = searchL8(ctx, model,
                   [('arch', '=like', '%it_partner_updated%')])
    id3 = searchL8(ctx, model,
                   [('arch', '=like', '%birthday%'),
                    '|',
                    ('xml_id', '=like', old_module),
                    ('xml_id', '=like', new_module)])
    ids = list(set(id1 + id2 + id3))
    for id in ids:
        try:
            view = browseL8(ctx, model, id)
            unlinkL8(ctx, model, [id])
            msg = u"Remove view id %d/%s of %s " % (id,
                                                    view.name,
                                                    view.xml_id)
            msg_log(ctx, ctx['level'], msg)
        except BaseException:
            pass
    return STS_SUCCESS


def cvt_ir_model_data(old_module, new_module, model_name, ctx):
    model = 'ir.model.data'
    ids = searchL8(ctx, model, [('module', '=', old_module),
                                ('model', '=', model_name)])
    for id in ids:
        seq_name = browseL8(ctx, model, id)
        name = seq_name.name
        res_id = seq_name.res_id
        display = seq_name.display_name
        cname = seq_name.complete_name
        new_ids = searchL8(ctx, model, [('module', '=', new_module),
                                        ('model', '=', model_name),
                                        ('name', '=', name)])
        if len(new_ids):
            new_seq_name = browseL8(ctx, model, new_ids[0])
            new_res_id = new_seq_name.res_id
            new_display = new_seq_name.display_name
            new_cname = new_seq_name.complete_name
        else:
            new_seq_name = False
            new_res_id = False
            new_display = False
            new_cname = False
        if not new_seq_name:
            new_cname = new_module + '.' + name
            writeL8(ctx, model, [id], {'module': new_module,
                                       'complete_name': new_cname})
            msg = u"Update module name of id %d" % id
            msg_log(ctx, ctx['level'], msg)
        elif res_id != new_res_id:
            msg = u"Name %s/%s has two different res_ids %d %d" % (name,
                                                                   display,
                                                                   res_id,
                                                                   new_res_id)
            msg_log(ctx, ctx['level'], msg)
            if model_name == 'res.city':
                unlinkL8(ctx, model_name, [res_id])
                msg = u"Remove record id %d/%s of %s " % (res_id,
                                                          display,
                                                          model_name)
                msg_log(ctx, ctx['level'], msg)
                unlinkL8(ctx, model, [id])
                msg = u"Remove duplicate id %d (%s)" % (id, cname)
                msg_log(ctx, ctx['level'], msg)
        elif display != new_display:
            msg = u"Name %d has two different display %s %s" % (name,
                                                                display,
                                                                new_display)
            msg_log(ctx, ctx['level'], msg)
        else:
            if not new_cname:
                new_cname = new_module + '.' + name
                writeL8(ctx, model, new_ids, {'complete_name': new_cname})
                msg = u"Update complete name of id %d" % new_ids[0]
                msg_log(ctx, ctx['level'], msg)
            unlinkL8(ctx, model, [id])
            msg = u"Remove duplicate id %d of %s " % (id, cname)
            msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def set_account_type(ctx):
    """Read all account movements and correct account type if wrong
    If needed
    1. unreconcile invoices,
    2. set payments of invoices to draft,
    3. set invoices to draft,
    4. do needed operations,
    5. restore invoices to original states
    6. restore payments to original states
    7. restore reconciliation
    """
    company_id = ctx['company_id']
    account_ids = searchL8(ctx, 'account.account',
                           [('company_id', '=', company_id),
                            ('code', 'like', ctx['account_code'])])
    if len(account_ids) == 0:
        return STS_FAILED
    for account_id in account_ids:
        account = browseL8(ctx, 'account.account', account_id)
        msg = u"Account %s %s" % (account.code, account.name)
        msg_log(ctx, ctx['level'], msg)
    move_line_ids = searchL8(ctx, 'account.move.line',
                             [('company_id', '=', company_id),
                              ('account_id', 'in', account_ids)])
    accounts = []
    # Journals to enable update posted
    journals = []
    # For every invoice id, store payment move line (detail) list
    reconcile_dict = {}
    # For every state, store move (header) list to update state
    move_dict = {}
    for state in STATES_2_DRAFT:
        move_dict[state] = []
    num_moves = len(move_line_ids)
    move_ctr = 0
    for move_line_id in move_line_ids:
        move_line = browseL8(ctx, 'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        account = move_line.account_id
        valid = True
        # valid = False       # debug
        if not account.parent_id:
            valid = False
        acctype_id = account.user_type.id
        acc_type = browseL8(ctx, 'account.account.type', acctype_id)
        if acc_type.report_type not in ("asset", "liability",
                                        "income", "expense"):
            valid = False
        if not valid:
            account_id = account.id
            if account_id not in accounts:
                accounts.append(account_id)
            if not move_line.journal_id.update_posted:
                journal_id = move_line.journal_id.id
                if journal_id not in journals:
                    journals.append(journal_id)
            inv_reconcile_dict, inv_move_dict = \
                get_reconcile_list_from_move_line(move_line, ctx)
            for inv_id in inv_reconcile_dict:
                if inv_id in reconcile_dict:
                    reconcile_dict[inv_id] = \
                        list(set(reconcile_dict[inv_id]) |
                             set(inv_reconcile_dict[inv_id]))
                else:
                    reconcile_dict[inv_id] = inv_reconcile_dict[inv_id]
            for state in STATES_2_DRAFT:
                if len(inv_move_dict[state]):
                    move_dict[state] = list(set(move_dict[state]) |
                                            set(inv_move_dict[state]))
    sts = upd_del_in_journal(ctx, journals)
    if sts == STS_SUCCESS:
        sts = unreconcile_invoices(reconcile_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_movements_2_draft(move_dict, ctx)
    raw_input('Press RET to continue')
    if sts == STS_SUCCESS:
        sts = upd_movements_2_posted(move_dict, ctx)
        if sts == STS_SUCCESS:
            for inv_id in reconcile_dict:
                reconciles = reconcile_dict[inv_id]
                new_reconciles, new_reconcile_dict = \
                    refresh_reconcile_from_inv(inv_id, reconciles, ctx)
                sts = reconcile_invoices(new_reconcile_dict, ctx)
    return sts


def recompute_tax_balance(ctx):
    sts = STS_SUCCESS
    company_id = ctx['company_id']
    model = 'account.period'
    period_ids = searchL8(ctx, model,
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    if ctx['custom_act'] == 'cscs':
        model = 'account.tax'
        tax_00_sell = searchL8(ctx, model,
                               [('description', '=', '00%VDCServ')])
        tax_00_pur = searchL8(ctx, model,
                              [('description', '=', '00%ACCServ')])

    model = 'account.invoice'
    model2 = 'account.invoice.line'
    invoice_ids = searchL8(ctx, model, [('period_id', 'in', period_ids),
                                        ('state', '!=', 'draft'),
                                        ('state', '!=', 'cancel')])
    num_moves = len(invoice_ids)
    move_ctr = 0
    for invoice_id in invoice_ids:
        move_ctr += 1
        msg_burst(ctx['level'], "Processing ", move_ctr, num_moves)
        rec_ids = [invoice_id]
        reconcile_dict, move_dict = get_reconcile_from_invoices(
            rec_ids, ctx)
        unreconcile_invoices(reconcile_dict, ctx)
        upd_invoices_2_draft(move_dict, ctx)
        line_ids = searchL8(ctx, model2,
                            [('invoice_id', '=', invoice_id)])
        if ctx['custom_act'] == 'cscs':
            for line_id in line_ids:
                line = browseL8(ctx, model2, line_id)
                if not line.invoice_line_tax_id:
                    type = browseL8(ctx, model, invoice_id).type
                    tax = False
                    if type in ('in_invoice', 'in_refund'):
                        tax = [(6, 0, tax_00_pur)]
                    elif type in ('out_invoice', 'out_refund'):
                        tax = [(6, 0, tax_00_sell)]
                    if tax:
                        writeL8(ctx, model2, [line_id],
                                {'invoice_line_tax_id': tax})
        upd_invoices_2_posted(move_dict, ctx)
        reconciles = reconcile_dict[invoice_id]
        if len(reconciles):
            try:
                cur_reconciles, cur_reconcile_dict = \
                    refresh_reconcile_from_inv(invoice_id,
                                               reconciles,
                                               ctx)
                reconcile_invoices(cur_reconcile_dict,
                                   ctx)
            except BaseException:
                msg = u"**** Warning invoice %d ****" % invoice_id
                msg_log(ctx, ctx['level'], msg)
    return sts


def recompute_balance(ctx):
    company_id = ctx['company_id']
    model = 'account.period'
    period_ids = searchL8(ctx, model,
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    model = 'account.move'
    move_ids = searchL8(ctx, model, [('period_id', 'in', period_ids),
                                     ('state', '!=', 'draft')])
    num_moves = len(move_ids)
    move_ctr = 0
    for move_id in move_ids:
        move_ctr += 1
        msg_burst(ctx['level'], "Processing ", move_ctr, num_moves)
        try:
            # msg = u"Update payments to draft %d" % move_id
            # msg_log(ctx, ctx['level'], msg)
            executeL8(ctx,
                      'account.move',
                      'button_cancel',
                      [move_id])
        except BaseException:
            msg = u"Cannot update payment status %d" % move_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
        try:
            # msg = u"Restore payments to posted %d" % move_id
            # msg_log(ctx, ctx['level'], msg)
            executeL8(ctx,
                      'account.move',
                      'button_validate',
                      [move_id])
        except BaseException:
            msg = u"Cannot restore payment status %d" % move_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def append_2_where(model, code, op, value, where, ctx):
    where.append((code, op, value))
    return where


def build_where(model, hide_cid, exclusion, ctx):
    where = []
    if not hide_cid and 'company_id' in ctx:
        company_id = ctx['company_id']
        where = append_2_where(model,
                               'company_id',
                               '=',
                               company_id,
                               where,
                               ctx)
    if exclusion:
        for rule in exclusion:
            code = rule[0]
            op = rule[1]
            value = rule[2]
            where = append_2_where(model,
                                   code,
                                   op,
                                   value,
                                   where,
                                   ctx)
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


def workflow_model_all_records(model, hide_cid, signal, ctx,
                               exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to execute workflow in %s" % model
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
                msg = u"Workflow of %s.%d do not executed" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def setstate_model_all_records(model, hide_cid, field_name,
                               new_value, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to update status in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(model, hide_cid, exclusion, ctx)
    if is_valid_field(ctx, model, field_name):
        where = append_2_where(model,
                               field_name,
                               '!=',
                               new_value,
                               where,
                               ctx)
    record_ids = searchL8(ctx, model, where)
    if is_valid_field(ctx, model, 'state') and \
            not ctx['dry_run'] and len(record_ids) > 0:
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Upstate ", move_ctr, num_moves)
            move_ctr += 1
            try:
                if model in ('purchase.order', 'sale.order') and \
                        field_name == 'state' and \
                        new_value == 'cancel':
                    executeL8(ctx,
                              model,
                              'action_cancel',
                              [record_id])
                elif model == 'purchase.requisition' and \
                        field_name == 'state' and \
                        new_value == 'cancel':
                    executeL8(ctx,
                              model,
                              'tender_cancel',
                              [record_id])
                elif model == 'procurement.order' and \
                        field_name == 'state' and \
                        new_value == 'cancel':
                    executeL8(ctx,
                              model,
                              'cancel',
                              [record_id])
                elif model == 'account.move' and \
                        field_name == 'state' and \
                        new_value == 'cancel':
                    executeL8(ctx,
                              model,
                              'button_cancel',
                              [record_id])
                elif model == 'account.voucher' and \
                        field_name == 'state' and \
                        new_value == 'cancel':
                    executeL8(ctx,
                              model,
                              'cancel_voucher',
                              [record_id])
                elif model == 'project.task' and \
                        field_name == 'state' and \
                        new_value == 'cancelled':
                    executeL8(ctx,
                              model,
                              'do_cancel',
                              [record_id])
                elif model == 'project.project' and \
                        field_name == 'state' and \
                        new_value == 'cancelled':
                    executeL8(ctx,
                              model,
                              'set_cancel',
                              [record_id])
                else:
                    writeL8(ctx, model,
                            [record_id],
                            {field_name: new_value})
            except BaseException:
                msg = u"Cannot update status of %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def reactivate_model_all_records(model, hide_cid, field_name,
                                 sel_value, new_value, ctx,
                                 exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to reactivate in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(model, hide_cid, exclusion, ctx)
    if is_valid_field(ctx, model, field_name):
        where = append_2_where(model,
                               field_name,
                               '=',
                               sel_value,
                               where,
                               ctx)
    record_ids = searchL8(ctx, model, where)
    if is_valid_field(ctx, model, 'state') and \
            not ctx['dry_run'] and len(record_ids) > 0:
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Reactive", move_ctr, num_moves)
            move_ctr += 1
            try:
                if model == 'project.project' and \
                        field_name == 'state' and \
                        sel_value == 'close' and \
                        new_value == 'set_open':
                    executeL8(ctx,
                              model,
                              'set_open',
                              [record_id])
                else:
                    writeL8(ctx, model,
                            [record_id],
                            {field_name: new_value})
            except BaseException:
                msg = u"Cannot reactivate %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def deactivate_model_all_records(model, hide_cid, ctx,
                                 exclusion=None, reverse=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    if reverse is None:
        reverse = False
    if is_valid_field(ctx, model, 'active'):
        where = build_where(model, hide_cid, exclusion, ctx)
        if reverse:
            msg = u"Searching for records to reactivate in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(model,
                                   'active',
                                   '=',
                                   False,
                                   where,
                                   ctx)

        else:
            msg = u"Searching for records to cancel in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(model,
                                   'active',
                                   '=',
                                   True,
                                   where,
                                   ctx)
        record_ids = searchL8(ctx, model, where)
        if not ctx['dry_run'] and len(record_ids) > 0:
            try:
                if reverse:
                    writeL8(ctx, model,
                            record_ids,
                            {'active': True})
                else:
                    writeL8(ctx, model,
                            record_ids,
                            {'active': False})
            except BaseException:
                if ctx['exit_onerror']:
                    sts = STS_FAILED
    decr_lev(ctx)
    return sts


def hard_del_sql(model, hide_cid, ctx, where=None, exclusion=None):
    if ctx.get('_cr'):
        query = build_sql_where(model, hide_cid, exclusion, where, ctx)
        incr_lev(ctx)
        msg = u">>>%s" % query
        msg_log(ctx, ctx['level'], msg)
        decr_lev(ctx)
        try:
            ctx['_cr'].execute(query)
        except BaseException:
            msg_log(ctx, ctx['level'], 'Error excuting sql')


def remove_model_all_records(model, hide_cid, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to delete in %s" % model
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
                unlinkL8(ctx, model,
                         [record_id])
            except BaseException:
                msg = u"Cannot remove %s.%d" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break

        if model == 'project.project':
            hard_del_sql(model, hide_cid, ctx,
                         where="state='cancelled'",
                         exclusion=exclusion)
    decr_lev(ctx)
    return sts


def remove_group_records(models, records2keep, ctx, hide_cid=None,
                         special=None, specparams=None, tables2save=None):
    sts = STS_SUCCESS
    for xmodel in models:
        exclusion = build_exclusion(xmodel, records2keep, ctx)
        act = None
        if xmodel.endswith('.2') or \
                xmodel.endswith('.3') or \
                xmodel.endswith('.4') or \
                xmodel.endswith('.5'):
            model = xmodel[0:-2]
        else:
            model = xmodel
        if tables2save and model in tables2save:
            writelog(xmodel, model, [], all=True)
            return sts
        if sts == STS_SUCCESS:
            writelog(xmodel, model, exclusion)
            if special and xmodel in special:
                act = special[xmodel]
                if act == 'deactivate':
                    sts = deactivate_model_all_records(model,
                                                       hide_cid,
                                                       ctx,
                                                       exclusion=exclusion,
                                                       reverse=True)
                elif act == 'reactivate':
                    if specparams and xmodel in specparams:
                        field_name = specparams[xmodel][0]
                        sel_value = specparams[xmodel][1]
                        new_value = specparams[xmodel][2]
                        sts = reactivate_model_all_records(model,
                                                           hide_cid,
                                                           field_name,
                                                           sel_value,
                                                           new_value,
                                                           ctx,
                                                           exclusion=exclusion)
                    else:
                        msg = u"Invalid parameters in %s on model %s!" % \
                            (act, model)
                        msg_log(ctx, ctx['level'], msg)
                        sts = STS_FAILED
                elif act == 'set_state':
                    if specparams and xmodel in specparams:
                        field_name = specparams[xmodel][0]
                        sel_value = specparams[xmodel][1]
                        sts = setstate_model_all_records(model,
                                                         hide_cid,
                                                         field_name,
                                                         sel_value,
                                                         ctx,
                                                         exclusion=exclusion)
                    else:
                        msg = u"Invalid parameters in %s on model %s!" % \
                            (act, model)
                        msg_log(ctx, ctx['level'], msg)
                        sts = STS_FAILED
                elif act == 'wf':
                    if specparams and xmodel in specparams:
                        signal = specparams[xmodel]
                        sts = workflow_model_all_records(model,
                                                         hide_cid,
                                                         signal,
                                                         ctx,
                                                         exclusion=None)
                    else:
                        msg = u"Invalid parameters in %s on model %s!" % \
                            (act, model)
                        msg_log(ctx, ctx['level'], msg)
                        sts = STS_FAILED
                else:
                    msg = u"Invalid action %s on model %s!" % (act, model)
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
        if sts == STS_SUCCESS and \
                ctx['custom_act'] == 'cscs' and \
                model == 'project.project':
            where = build_where(model, hide_cid, exclusion, ctx)
            where = append_2_where(model,
                                   'x_stakeholders',
                                   '!=',
                                   False,
                                   where,
                                   ctx)
            record_ids = searchL8(ctx, model, where)
            if len(record_ids):
                writeL8(ctx, model,
                        record_ids,
                        {'x_stakeholders': [(5, 0)]})
            where = build_where(model, hide_cid, exclusion, ctx)
            record_ids = searchL8(ctx, model, where)
            if len(record_ids):
                for record_id in record_ids:
                    try:
                        obj = browseL8(ctx, model, record_id)
                        date_start = obj.date_start
                        date_stop = obj.date
                        if not date_start:
                            date_start = date.today()
                        if not date_stop:
                            date_stop = date(2013, 7, 15)
                        if date_start > date_stop:
                            today = str(date.today())
                            writeL8(ctx, model,
                                    record_id,
                                    {'date_start': today, 'date': today})
                    except BaseException:
                        pass
        if sts == STS_SUCCESS and model == 'account.move' and model == xmodel:
            unreconcile_payments(ctx)
        if sts == STS_SUCCESS and model == xmodel:
            if model == 'account.fiscalyear':
                company_id = ctx['company_id']
                exclusion = [('company_id', '!=', company_id),
                             ('code', '!=', str(date.today().year))]
            elif model == 'account.period':
                company_id = ctx['company_id']
                exclusion = [('company_id', '!=', company_id),
                             ('code', 'not like',
                              str(date.today().year))]
            sts = remove_model_all_records(model, hide_cid, ctx,
                                           exclusion=exclusion)
        if sts == STS_SUCCESS and act == 'deactivate':
            sts = deactivate_model_all_records(model,
                                               hide_cid,
                                               ctx,
                                               exclusion=exclusion)
        if model in ('project.task.work',
                     'account.analytic.line',
                     'purchase.order',
                     'sale.order',):
            if model == 'purchase.order':
                hard_del_sql('purchase.order.line', hide_cid, ctx)
            elif model == 'sale.order':
                hard_del_sql('sale.order.line', hide_cid, ctx)
            hard_del_sql(model, hide_cid, ctx, exclusion=exclusion)
    return sts


def set_server_isolated(ctx):
    """Isolate server to avoid notification mail for some events
    like remove tasks
    """
    sts = STS_SUCCESS
    if not ctx['dry_run']:
        if sts == STS_SUCCESS:
            model = 'fetchmail.server'
            sts = deactivate_model_all_records(model, True, ctx)
        if sts == STS_SUCCESS:
            model = 'ir.mail_server'
            sts = deactivate_model_all_records(model, True, ctx)
        if sts == STS_SUCCESS:
            model = 'mail.followers'
            sts = remove_model_all_records(model, True, ctx)
    return sts


def reset_sequence(ctx):
    sts = STS_SUCCESS
    incr_lev(ctx)
    model = 'ir.sequence'
    msg = u"Reset sequence %s" % model
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
                            unlinkL8(ctx, model,
                                     [record_id])
                            f_deleted = True
                        except BaseException:
                            msg = u"Cannot remove %s.%d" % (model, record_id)
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
    msg = u"Reset sequence %s" % model
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        record_ids = (367, 368, 473, 495,
                      530, 688, 699, 725,
                      844, 845)
        for record_id in record_ids:
            try:
                unlinkL8(ctx, model,
                         [record_id])
            except BaseException:
                msg = u"Cannot remove %s.%d" % (model, record_id)
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


def remove_company_mail_records(ctx):
    models = validate_models(ctx, ('ir.attachment',))
    records2keep = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False)
    return sts


def remove_all_mail_records(ctx):
    models = validate_models(ctx, ('mail.message',
                                   'mail.mail',
                                   'mail.notification',
                                   'mail.alias',
                                   ))
    records2keep = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True)
    return sts


def remove_all_note_records(ctx):
    models = validate_models(ctx, ('note.stage',
                                   'note.note',
                                   'document.page',
                                   ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'note.stage': 8}
    else:
        records2keep = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True)
    return sts


def remove_company_crm_records(ctx):
    models = validate_models(ctx, ('crm.lead',
                                   'crm.helpdesk',
                                   'crm.phonecall',
                                   ))
    records2keep = {}
    special = {'crm.lead': 'deactivate'}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False, special=special)
    return sts


def remove_all_crm_records(ctx):
    models = validate_models(ctx, ('crm.meeting',
                                   'calendar.event',
                                   'calendar.todo',
                                   ))
    records2keep = {}
    special = {'crm.lead': 'deactivate'}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False, special=special)

    return sts


def remove_company_purchases_records(ctx):
    models = validate_models(ctx, ('procurement.order',
                                   'purchase.order.2',
                                   'purchase.order',
                                   'purchase.requisition',
                                   'product.pricelist.version',
                                   'product.pricelist',
                                   ))
    records2keep = {}
    special = {'procurement.order': 'reactivate',
               'procurement.order.2': 'set_state',
               'purchase.order.2': 'wf',
               'purchase.order': 'set_state',
               'purchase.requisition': 'set_state',
               }
    specparams = {'procurement.order': ('state', 'done', 'draft'),
                  'procurement.order.2': ('state', 'cancel'),
                  'purchase.order.2': 'state_draft_set',
                  'purchase.order': ('state', 'cancel'),
                  'purchase.requisition': ('state', 'cancel'),
                  }
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_purchases_records(ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_sales_records(ctx):
    models = validate_models(ctx, ('sale.order',
                                   'sale.shop',
                                   ))
    records2keep = {'sale.shop': 1}
    special = {'sale.order': 'set_state',
               }
    specparams = {'sale.order': ('state', 'cancel'),
                  }
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_sales_records(ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_inventory_records(ctx):
    models = validate_models(ctx, ('stock.inventory',
                                   'stock.pack.operation',
                                   # 'wk.order.mapping',
                                   'stock.picking.package.preparation',
                                   'stock.picking.out',
                                   'stock.picking.in',
                                   'stock.picking',
                                   'stock.move',
                                   'stock.location',
                                   'stock.warehouse',
                                   ))
    records2keep = {}
    special = {'stock.picking.out': 'reactivate',
               'stock.picking.in': 'reactivate',
               'stock.picking': 'reactivate',
               'stock.move': 'reactivate',
               }
    specparams = {'stock.picking.out': ('state', 'cancel', 'draft'),
                  'stock.picking.in': ('state', 'cancel', 'draft'),
                  'stock.picking': ('state', 'cancel', 'draft'),
                  'stock.move': ('state', 'cancel', 'draft'),
                  }
    if ctx['custom_act'] == 'cscs':
        tables2save = ('stock.location',
                       'stock.warehouse',
                       )
    else:
        tables2save = None
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams,
                               tables2save=tables2save)
    return sts


def remove_all_inventory_records(ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_project_records(ctx):
    models = validate_models(ctx, ('project.task.work',
                                   'project.task',
                                   'account.analytic.line'
                                   ))
    records2keep = {}
    if ctx['custom_act'] == 'cscs':
        model = 'project.task'
        records2keep['project.task'] = searchL8(ctx, model,
                                                [('project_id',
                                                  '=',
                                                  CV_PROJECT_ID)])
        records2keep['project.task'].append(8771)
    if ctx['oe_version'] == '7.0:':
        special = {'project.task': 'set_state', }
        specparams = {'project.task': ('state', 'cancelled'), }
    else:
        special = {}
        specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_project_records(ctx):
    models = validate_models(ctx, ('survey.page',
                                   'survey.request',
                                   'survey',
                                   'project.phase'
                                   'project.project.2',
                                   'project.project',
                                   ))
    records2keep = {}
    records2keep['project.project'] = (260, 265, 2869, 3026,
                                       3027, 3028, 3029, 3030,
                                       3031, 3032, 3033, 3034,
                                       3035, 3036, 3037, 3038,
                                       3039, 3040, 3187, 3361,
                                       3504, 3664, 3932)
    if ctx['oe_version'] == '7.0:':
        special = {'project.project.2': 'reactivate',
                   'project.project': 'set_state',
                   }
        specparams = {'project.project.2': ('state', 'close', 'set_open'),
                      'project.project': ('state', 'cancelled')
                      }
    else:
        special = {'project.project.2': 'reactivate',
                   'project.project': 'set_state',
                   }
        specparams = {'project.project.2': ('state', 'close', 'set_open'),
                      'project.project': ('state', 'cancelled')
                      }
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_marketing_records(ctx):
    sts = STS_SUCCESS
    return sts


def remove_all_marketing_records(ctx):
    models = validate_models(ctx, ('marketing.campaign.workitem',
                                   'marketing.campaign.segment',
                                   'marketing.campaign',
                                   'booking.resource',
                                   'campaign.analysis',
                                   ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_hr_records(ctx):
    models = validate_models(ctx, ('hr.expense.expense.2',
                                   'hr.expense.expense.3',
                                   'hr.expense.expense.4',
                                   'hr.expense.expense.5',
                                   'hr.expense.expense',
                                   ))
    records2keep = {}
    special = {'hr.expense.expense.2': 'wf',
               'hr.expense.expense.3': 'wf',
               'hr.expense.expense.4': 'wf',
               'hr.expense.expense.5': 'wf',
               'hr.expense.expense': 'set_state',
               }
    specparams = {'hr.expense.expense.2': 'draft',
                  'hr.expense.expense.3': 'edit',
                  'hr.expense.expense.4': 'set_draft',
                  'hr.expense.expense.5': 'state_draft_set',
                  'hr.expense.expense': ('state', 'draft'),
                  }
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_hr_records(ctx):
    models = validate_models(ctx, ('hr_timesheet_sheet.sheet.account',
                                   'hr_timesheet_sheet.sheet',
                                   'hr.analytic.timesheet',
                                   'hr.expense.line',
                                   'hr.contract',
                                   'hr.holidays',
                                   'hr.payslip',
                                   'hr.attendance',
                                   'hr.applicant',
                                   'hr.department',
                                   'hr.employee',
                                   ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_product_records(ctx):
    models = validate_models(ctx, ('product.template',
                                   ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_product_records(ctx):
    models = validate_models(ctx, ('product.category',
                                   'product.uom.categ',
                                   'product.uom',
                                   'product.product',
                                   ))
    records2keep = {}
    special = {}
    specparams = {}
    if ctx['custom_act'] == 'cscs':
        tables2save = ('product.category',
                       'product.product',
                       'product.uom.categ',
                       'product.uom',
                       )
    else:
        tables2save = None
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams,
                               tables2save=tables2save)
    return sts


def remove_company_partner_records(ctx):
    models = validate_models(ctx, ('res.partner.bank',
                                   'res.partner',
                                   ))
    company_id = ctx['company_id']
    if ctx['custom_act'] == 'cscs':
        records2keep = {'res.partner': (1, 3, 4, 5, 33523, 33783,
                                        browseL8(ctx, 'res.company',
                                                 company_id).id),
                        }
    else:
        records2keep = {'res.partner': browseL8(ctx, 'res.company',
                                                company_id).id
                        }
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_analytics_records(ctx):
    models = validate_models(ctx, ('account.analytic.account',
                                   'account.analytic.journal',
                                   ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'account.analytic.account': (48, 3932)}
    else:
        records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_partner_records(ctx):
    models = validate_models(ctx, ('res.partner.category',
                                   'res.partner'
                                   ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'res.partner': (1, 3, 4, 5, 33890, 33523, 33783)}
    else:
        records2keep = {'res.partner': 1}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_user_records(ctx):
    models = validate_models(ctx, ('ir.default',
                                   'res.users',
                                   ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'res.users': (1, 4, 95)}
    else:
        records2keep = {'res.users': 1}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_account_move_records(ctx):
    sts = STS_SUCCESS
    model = 'account.invoice'
    move_name = translate_from_to(ctx,
                              model,
                              'move_name',
                              '10.0',
                              ctx['oe_version'])
    if not ctx['dry_run']:
        company_id = ctx['company_id']
        if sts == STS_SUCCESS:
            msg = u"Searching for invoices to delete"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id),
                                   '|',
                                   ('state', '=', 'paid'),
                                   ('state', '=', 'open')])
            reconcile_dict, move_dict = get_reconcile_from_invoices(record_ids,
                                                                    ctx)
            sts = unreconcile_invoices(reconcile_dict, ctx)
        if sts == STS_SUCCESS:
            msg = u"Setting invoices to cancel state"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id)])
            if len(record_ids) > 0:
                try:
                    sts = upd_invoices_2_cancel(record_ids, ctx)
                except BaseException:
                    msg = u"Cannot delete invoices"
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
    if sts == STS_SUCCESS:
        company_id = ctx['company_id']
        models = validate_models(ctx,
                                 ('account.invoice',
                                  'account.move',
                                  'account.voucher',
                                  'payment.order',
                                  'account.bank.statement',
                                  'account.period',
                                  'account.fiscalyear',
                                  'account.banking.account.settings',
                                  'spesometro.comunicazione',
                                  'payment.mode',
                                  ))
        records2keep = {}
        special = {'account.invoice': 'set_state',
                   'account.move': 'set_state',
                   'account.voucher': 'set_state',
                   }
        specparams = {'account.invoice': (move_name, ''),
                      'account.move': ('state', 'cancel'),
                      'account.voucher': ('state', 'cancel'),
                      }
        sts = remove_group_records(models, records2keep, ctx,
                                   hide_cid=False,
                                   special=special,
                                   specparams=specparams)
    return sts


def remove_company_account_base_records(ctx):
    sts = STS_SUCCESS
    model = 'account.invoice'
    if not ctx['dry_run']:
        company_id = ctx['company_id']
        if sts == STS_SUCCESS:
            msg = u"Searching for invoices to delete"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id),
                                   '|',
                                   ('state', '=', 'paid'),
                                   ('state', '=', 'open')])
            reconcile_dict, move_dict = get_reconcile_from_invoices(record_ids,
                                                                    ctx)
            sts = unreconcile_invoices(reconcile_dict, ctx)
        if sts == STS_SUCCESS:
            msg = u"Setting invoices to cancel state"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id)])
            if len(record_ids) > 0:
                try:
                    sts = upd_invoices_2_cancel(record_ids, ctx)
                except BaseException:
                    msg = u"Cannot delete invoices"
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
    if sts == STS_SUCCESS:
        company_id = ctx['company_id']
        models = validate_models(ctx,
                                 ('account.fiscal.position',
                                  'account.tax.code',
                                  'account.tax',
                                  'account.journal',
                                  'account.account',
                                  ))
        if ctx['custom_act'] == 'cscs':
            records2keep = {'account.account': (1, 2, 31, 32,
                                                54, 55, 109, 158, 159,
                                                172, 174, 225, 226,
                                                227, 263, 264, 265),
                            'account.tax': (23, 24),
                            'account.tax.code': (1, 4, 5, 6, 45, 46),
                            'account.journal': (77, 78, 79, 80,
                                                81, 82, 93, 84,
                                                85, 86, 87, 88)
                            }
        else:
            records2keep = {}
        special = {'account.journal': 'deactivate',
                   'account.tax': 'deactivate',
                   }
        specparams = {}
        sts = remove_group_records(models, records2keep, ctx,
                                   hide_cid=False,
                                   special=special,
                                   specparams=specparams)
    return sts


def remove_all_account_move_records(ctx):
    models = validate_models(ctx, ('payment.line'))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def analyze_invoices(ctx, inv_type):
    company_id = ctx['company_id']
    model = 'account.invoice'
    move_name = translate_from_to(ctx,
                                  model,
                                  'move_name',
                                  '10.0',
                                  ctx['oe_version'])
    period_ids = searchL8(ctx, 'account.period',
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    account_invoice_ids = searchL8(ctx, model,
                                   [('company_id', '=', company_id),
                                    ('period_id', 'in', period_ids),
                                    ('type', '=', inv_type),
                                    (move_name, '!=', '')],
                                   order=move_name)
    num_invs = len(account_invoice_ids)
    last_number = ''
    inv_ctr = 0
    last_seq = 0
    for account_invoice_id in account_invoice_ids:
        account_invoice = browseL8(ctx, model,
                                   account_invoice_id)
        inv_ctr += 1
        msg_burst(4,
                  "Invoice %s       " % account_invoice[move_name],
                  inv_ctr, num_invs)
        # vals = {}
        if last_number[:-4] != account_invoice[move_name][0:-4]:
            last_number = ''
        if last_number == '':
            last_number = account_invoice[move_name]
            last_rec_date = datetime.strptime(ctx['date_start'],
                                              "%Y-%m-%d").date()
            last_seq = 0
        last_seq += 1
        if str.isdigit(account_invoice[move_name][-4:]) and \
                int(account_invoice[move_name][-4:]) != last_seq:
            msg = u"In {0} invalid number sequence {1}".format(
                account_invoice_id,
                account_invoice[move_name])
            msg_log(ctx, ctx['level'] + 1, msg)
            last_seq = int(account_invoice[move_name][-4:])
        last_rec_date = put_invoices_record_date([account_invoice_id],
                                                 last_rec_date,
                                                 ctx)
        last_number = account_invoice[move_name]
    return STS_SUCCESS


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
    values = executeL8(ctx,
                       setup_model,
                       'default_get',
                       [])
    db_name = values['name']
    setup_id = executeL8(ctx,
                         setup_model,
                         'create',
                         values)
    executeL8(ctx,
              setup_model,
              'execute',
              [setup_id],
              None)
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
    if isinstance(actv, basestring) and \
            actv[-4:] in ('_6.1', '_7.0', '_8.0', '_9.0',
                          '_10.0', '_11.0', '_12.0'):
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
        put_model_alias(ctx,
                        model=model,
                        ref=row['id'],
                        id=id)
    if o_model.get('alias_model2', '') and \
            o_model.get('alias_field', '') and \
            o_model['alias_field'] in row and \
            row[o_model['alias_field']].find('None') < 0:
        res_id = browseL8(ctx,
                          model,
                          id)[o_model['alias_field']].id
        put_model_alias(ctx,
                        model=o_model['alias_model2'],
                        ref=row[o_model['alias_field']],
                        id=res_id)


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
        nm = translate_from_to(ctx,
                               model,
                               n,
                               '7.0',
                               ctx['oe_version'])
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
        if ctx['no_fvalidation'] or nm in ('id', 'db_type', 'oe_versions',
                                           'name2', 'name_first', 'name_last',
                                           'customer-supplier') or \
                (len(ctx['validated_fields']) and
                 nm in ctx['validated_fields']) or \
                is_valid_field(ctx, model, nm):
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
    for nm in row:
        if not row[nm] and nm in ctx.get('EXPR', ''):
            row[nm] = eval(ctx['EXPR'][nm])
        else:
            row[nm] = set_some_values(ctx,
                                      o_model,
                                      nm,
                                      row[nm],
                                      row=row)
    if 'name2' in row:
        if 'name' in row:
            row['name'] = '%s %s' % (row['name'], row['name2'])
        else:
            row['name'] = row['name2']
        del row['name2']
    if 'name_first' in row and 'name_last' in row and \
            (not row.get('is_company', True) or
             row.get('company_type') == 'person' or
             not row.get('name')):
        row['name'] = '%s %s' % (row['name_last'], row['name_first'])
        del row['name_first'], row['name_last']
    if 'street2' in row and row['street2'].isdigit() and 'street' in row:
        row['street'] = '%s, %s' % (row['street'], row['street2'])
        row['street2'] = ''
    if 'customer-supplier' in row or not row.get('is_company', True) or \
            row.get('company_type') == 'person':
        if 'customer' in row:
            row['customer'] = False
        if 'supplier' in row:
            row['supplier'] = False
    if 'customer-supplier' in row:
        if row['customer-supplier'].lower().find('customer') >= 0 or \
                row['customer-supplier'].lower().find('client') >= 0:
            row['customer'] = True
        if row['customer-supplier'].lower().find('supplier') >= 0 or \
                row['customer-supplier'].lower().find('vendor') >= 0 or \
                row['customer-supplier'].lower().find('fornitore') >= 0:
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
        if not nm or nm in ('id',
                            'db_type',
                            'oe_versions',
                            'name2',
                            'name_first',
                            'name_last',
                            'customer-supplier',
                            o_model['alias_field']):
            continue
        if isinstance(row[nm], basestring):
            # if nm == o_model['alias_field']:
            #    continue
            if row[nm].find('${header_id}') >= 0:
                update_header_id = False
            row[nm] = row[nm].replace('\\n', '\n')
        val = eval_value(ctx,
                         o_model,
                         nm,
                         row[nm])
        if val is not None:
            if (nm != 'fiscalcode' or val != '') and \
                    (len(ids) == 0 or tounicode(val) != cur_obj[nm]):
                vals[nm] = tounicode(val)
        msg = u"{0}={1}".format(nm, tounicode(val))
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
    msg = u"Import file " + csv_fn
    debug_msg_log(ctx, ctx['level'] + 1, msg)
    model = get_model_model(ctx, o_model)
    get_model_structure(ctx, model)
    if not ctx.get('company_id'):
        init_company_ctx(ctx, get_company_id(ctx))
    if 'company_id' in ctx:
        company_id = ctx['company_id']
    if ctx.get('full_model'):
        ctx['MANDATORY'] = extr_table_generic(ctx, model)
    csv.register_dialect('odoo',
                         delimiter=_c(','),
                         quotechar=_c('\"'),
                         quoting=csv.QUOTE_MINIMAL)
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
        csv_obj = csv.DictReader(csv_fd,
                                 fieldnames=[],
                                 restkey='undef_name',
                                 dialect='odoo')
        for row in csv_obj:
            if not hdr_read:
                hdr_read = True
                o_model = import_file_get_hdr(ctx,
                                              o_model,
                                              csv_obj,
                                              csv_fn,
                                              row)
                msg = u"Model=%s, Code=%s Name=%s NoCompany=%s" % (
                    model,
                    tounicode(o_model['code']),
                    tounicode(o_model['name']),
                    o_model.get('hide_cid', False))
                debug_msg_log(ctx, ctx['level'] + 2, msg)
                if o_model['name'] and o_model['code']:
                    continue
                else:
                    msg = u"!File " + csv_fn + " without key!"
                    msg_log(ctx, ctx['level'] + 1, msg)
                    break
            row = translate_ext_names(ctx, o_model, row, csv_obj)
            # Data for specific db type (i.e. just for test)
            if o_model.get('db_type', ''):
                if row[o_model['db_type']]:
                    if row[o_model['db_type']].find(ctx['db_type']) < 0:
                        msg = u"Record not imported by invalid db_type"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
            if row.get('oe_versions'):
                if row['oe_versions'].find('-') >= 0:
                    if row['oe_versions'].find(ctx['oe_version']) >= 0:
                        msg = u"Record not imported by invalid version"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
                elif row['oe_versions'].find('+') >= 0:
                    if row['oe_versions'].find(ctx['oe_version']) < 0:
                        msg = u"Record not imported by invalid version"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
            if model == 'res.users' and 'login' in row:
                ctx['def_email'] = '%s%s@example.com' % (
                    row['login'],
                    ctx['oe_version'].split('.')[0])
            if 'undef_name' in row:
                msg = u"!Invalid line format!"
                msg_log(ctx, ctx['level'], msg)
                del row['undef_name']
            # Does record exist ?
            saved_hide_id = o_model['hide_id']
            if o_model['repl_by_id'] and row.get('id', False):
                o_model['hide_id'] = False
            ids = get_query_id(ctx,
                               o_model,
                               row)
            o_model['hide_id'] = saved_hide_id
            if len(ids):
                id = ids[0]
                cur_obj = browseL8(ctx, model, id)
                if model == 'res.users' and\
                        len(ids) == 1:
                    cur_login = cur_obj.login
                    if 'login' in row:
                        ctx['def_email'] = '%s%s@example.com' % (
                            cur_obj.login,
                            ctx['oe_version'].split('.')[0])
            else:
                cur_obj = False
            vals, update_header_id, name_new = parse_in_fields(ctx,
                                                               o_model,
                                                               row,
                                                               ids,
                                                               cur_obj)
            if 'company_id' in ctx and 'company_id' in vals:
                if vals['company_id'] != company_id:
                    continue
            if len(ids):
                if update_header_id:
                    ctx['header_id'] = ids[0]
                name_old = cur_obj[o_model['name']]
                if not isinstance(name_old, basestring):
                    name_old = ''
                msg = u"Update %d %s" % (id, name_old)
                debug_msg_log(ctx, ctx['level'] + 1, msg)
            if (model == 'res.users' and
                    'new_password' in vals and
                    len(ids) == 0):
                vals['password'] = vals['new_password']
                del vals['new_password']
                vals['password_crypt'] = ''
            written = False
            if len(ids):
                if not ctx['dry_run'] and len(vals):
                    try:
                        writeL8(ctx, model, ids, vals)
                        msg = u"id=%d, %s=%s->%s" % (cur_obj.id,
                                                     o_model['name'],
                                                     tounicode(name_old),
                                                     tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                        written = True
                    except BaseException:
                        msg = u"!!write error! id=%d, %s=%s" % (
                            cur_obj.id,
                            o_model['name'],
                            tounicode(name_new))
                        os0.wlog(msg)
                    if written:
                        if (model == 'res.users' and
                                'login' in vals and
                                cur_login == ctx['login_user']):
                            if 'login' in vals:
                                ctx['login_user'] = vals['login']
                            if 'new_password' in vals:
                                if vals['new_password'].find('$1$!') == 0:
                                    ctx['crypt_password'] = vals[
                                        'new_password']
                                else:
                                    ctx['login_password'] = vals[
                                        'new_password']
                            do_login(ctx)
                        try:
                            add_external_name(ctx, o_model, row, ids[0])
                        except BaseException:
                            msg = u"!!No set external name id=%d, %s=%s" % (
                                cur_obj.id,
                                o_model['name'],
                                tounicode(name_new))
                            os0.wlog(msg)
            else:
                msg = u"insert " + os0.u(name_new)
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['dry_run']:
                    if not o_model.get('hide_cid', False) and \
                            'company_id' not in vals:
                        vals['company_id'] = ctx['company_id']
                    try:
                        id = createL8(ctx, model, vals)
                        if update_header_id:
                            ctx['header_id'] = id
                        msg = u"creat id={0}, {1}={2}"\
                              .format(id,
                                      tounicode(o_model['name']),
                                      tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                        written = True
                    except BaseException:
                        id = None
                        msg = u"!!create error! %s[%s]=%s" % (
                            tounicode(o_model.get('model')),
                            tounicode(o_model['name']),
                            tounicode(name_new))
                        os0.wlog(msg)
                    if written and id:
                        try:
                            add_external_name(ctx, o_model, row, id)
                        except BaseException:
                            msg = u"!!No set external name id=%d, %s=%s" % (
                                cur_obj.id,
                                o_model['name'],
                                tounicode(name_new))
                            os0.wlog(msg)
                else:
                    ctx['header_id'] = -1
        csv_fd.close()
    else:
        msg = u"Import file " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def import_config_file(ctx, csv_fn):
    csv.register_dialect('odoo',
                         delimiter=',',
                         quotechar='\"',
                         quoting=csv.QUOTE_MINIMAL)

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
        csv_obj = csv.DictReader(csv_fd,
                                 fieldnames=[],
                                 restkey='undef_name',
                                 dialect='odoo')
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
                    msg = u"!Invalid header of " + csv_fn
                    msg = msg + u" Should be: user,name,value"
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
            user = eval_value(ctx,
                              None,
                              None,
                              row['user'])
            name = eval_value(ctx,
                              None,
                              None,
                              row['name'])
            value = eval_value(ctx,
                               None,
                               None,
                               row['value'])
            if name:
                if user:
                    sts = setup_user_config_param(ctx, user, name, value)
                else:
                    sts = setup_global_config_param(ctx, name, value)
                if sts != STS_SUCCESS:
                    break
            else:
                msg = u"!Unmanaged parameter %s " % row['name']
                msg_log(ctx, ctx['level'] + 1, msg)
        csv_fd.close()
    else:
        msg = u"!File " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def setup_user_config_param(ctx, username, name, value):
    context = get_context(ctx)
    sts = STS_SUCCESS
    v = os0.str2bool(value, None)
    if v is not None:
        value = v
    if isinstance(value, bool):
        if isinstance(name, (int, long)):
            group_ids = [name]
        else:
            group_ids = searchL8(ctx, 'res.groups',
                                 [('name', '=', name)],
                                 context=context)
    else:
        cat_ids = searchL8(ctx, 'ir.module.category',
                           [('name', '=', name)],
                           context=context)
        if isinstance(value, (int, long)):
            group_ids = [value]
        else:
            group_ids = searchL8(ctx, 'res.groups',
                                 [('category_id', 'in', cat_ids),
                                  ('name', '=', value)],
                                 context=context)
    if len(group_ids) != 1:
        if isinstance(value, bool):
            msg = u"!!Parameter name '%s' not found!!" % tounicode(name)
        else:
            msg = u"!!Parameter name '%s/%s' not found!!" % (tounicode(name),
                                                             tounicode(value))
        msg_log(ctx, ctx['level'] + 2, msg)
        return sts
    if isinstance(username, int):
        user_ids = [username]
    else:
        user_ids = searchL8(ctx, 'res.users',
                            [('login', '=', username)])
        if len(user_ids) != 1:
            msg = u"!!User " + tounicode(username) + " not found!!"
            msg_log(ctx, ctx['level'] + 2, msg)
            return STS_FAILED
    user = browseL8(ctx, 'res.users', user_ids[0])
    if not user:
        if isinstance(username, int):
            msg = u"!!Invalid %d username!!" % username
        else:
            msg = u"!!Invalid username: %s!!" % tounicode(username)
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    group_id = group_ids[0]
    vals = {}
    if isinstance(value, bool):
        if value and group_id not in user.groups_id.ids:
            vals['groups_id'] = [(4, group_id)]
            msg = u"%s.%s = True" % (tounicode(username), tounicode(name))
            msg_log(ctx, ctx['level'] + 2, msg)
        elif not value and group_id in user.groups_id.ids:
            vals['groups_id'] = [(3, group_id)]
            msg = u"%s.%s = False" % (tounicode(username), tounicode(name))
            msg_log(ctx, ctx['level'] + 2, msg)
    else:
        for id in searchL8(ctx, 'res.groups',
                           [('category_id', 'in', cat_ids)],
                           context=context):
            if id != group_id and id in user.groups_id.ids:
                vals['groups_id'] = [(3, id)]
                try:
                    writeL8(ctx, 'res.users', user_ids, vals)
                except BaseException:
                    msg = u"!!Error writing parameter %s" % name
                    msg_log(ctx, ctx['level'] + 2, msg)
        if group_id not in user.groups_id.ids:
            vals['groups_id'] = [(4, group_id)]
            if isinstance(value, bool):
                msg = u"%s.%s = True" % (tounicode(username),
                                         tounicode(name))
            else:
                msg = u"%s.%s/%s" % (tounicode(username),
                                     tounicode(name),
                                     tounicode(value))
            msg_log(ctx, ctx['level'] + 2, msg)
    if not ctx['dry_run'] and len(vals):
        writeL8(ctx, 'res.users', user_ids, vals)
    return sts


def setup_global_config_param(ctx, name, value):
    # context = get_context(ctx)
    sts = STS_SUCCESS
    items = name.split('.')
    if len(items) > 1:
        model = '.'.join(items[0:len(items)-1])
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
            model2 = '.'.join(items[0:len(items)-1])
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
        msg = u"%s/%s" % (tounicode(name), tounicode(value))
        msg_log(ctx, ctx['level'] + 2, msg)
        id = createL8(ctx, model, {name: value})
        executeL8(ctx, model, 'execute', [id])
    except BaseException:
        sts = STS_FAILED
    return sts


def install_chart_of_account(ctx, name):
    sts = STS_SUCCESS
    context = get_context(ctx)
    chart_template_id = searchL8(ctx, 'account.chart.template',
                                 [('name', '=', name)],
                                 context=context)
    if len(chart_template_id) == 0:
        msg = u"!Invalid chart of account " + tounicode(name) + "!!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    chart_template_id = chart_template_id[0]
    if 'company_id' not in ctx:
        msg = u"!No company declared!!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    company_id = ctx['company_id']
    currency_id = browseL8(ctx, 'res.company', company_id).currency_id
    chart_values = {
        'company_id': company_id,
        'currency_id': currency_id,
        'chart_template_id': chart_template_id
    }
    model = 'account.account'
    ids = searchL8(ctx, model, [('company_id', '=', company_id)])
    # Check if example coa installed
    if len(ids) > 0 and len(ids) < 16:
        unlinkL8(ctx, model, ids)
    if ctx['oe_version'] in ('6.1', '7.0', '8.0'):
        chart_setup_model = 'wizard.multi.charts.accounts'
        chart_values.update(executeL8(ctx, chart_setup_model,
                                      'onchange_chart_template_id',
                                      [],
                                      1)['value'])
        chart_setup_id = executeL8(ctx, chart_setup_model,
                                   'create',
                                   chart_values)
        executeL8(ctx, chart_setup_model,
                  'execute',
                  [chart_setup_id])
    else:
        if company_id != ctx.get('user_company_id', 0):
            writeL8(ctx, 'res.users', ctx['user_id'],
                    {'company_id': company_id})
        executeL8(ctx,
                  'account.chart.template',
                  'try_loading_for_current_company',
                  [chart_template_id])
        if company_id != ctx.get('user_company_id', 0):
            writeL8(ctx, 'res.users', ctx['user_id'],
                    {'company_id': ctx.get('user_company_id', 0)})
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
        res = check_actions_1_list(ctx,
                                   ctx['do_sel_action'],
                                   lx_act,
                                   conf_obj)
    elif ctx.get('actions', None):
        res = check_actions_1_list(ctx,
                                   ctx['actions'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_db', None):
        res = check_actions_1_list(ctx,
                                   ctx['actions_db'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_mc', None):
        res = check_actions_1_list(ctx,
                                   ctx['actions_mc'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_uu', None):
        res = check_actions_1_list(ctx,
                                   ctx['actions_uu'],
                                   lx_act,
                                   conf_obj)
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
                res = check_actions_1_list(ctx,
                                           actions,
                                           lx_act,
                                           conf_obj)
                if not res:
                    break
            elif conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                res = check_actions_1_list(ctx,
                                           actions,
                                           lx_act,
                                           conf_obj)
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
        lx_act = extend_actions_1_list(ctx,
                                       ctx['actions'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_db', None):
        lx_act = extend_actions_1_list(ctx,
                                       ctx['actions_db'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_mc', None):
        lx_act = extend_actions_1_list(ctx,
                                       ctx['actions_mc'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_uu', None):
        lx_act = extend_actions_1_list(ctx,
                                       ctx['actions_uu'],
                                       lx_act,
                                       conf_obj)
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
                lx_act = extend_actions_1_list(ctx,
                                               actions,
                                               lx_act,
                                               conf_obj)
            elif conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                lx_act = extend_actions_1_list(ctx,
                                               actions,
                                               lx_act,
                                               conf_obj)
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
        msg = u"Invalid action declarative "
        msg_log(ctx, ctx['level'], msg)
        msg = u"Use one or more in following parameters:"
        msg_log(ctx, ctx['level'], msg)
        msg = u"actions=" + ",".join(str(e) for e in sorted(lx_act))
        msg_log(ctx, ctx['level'], msg)
    return valid_actions


def main():
    """Tool main"""
    sts = STS_SUCCESS
    ctx = parse_args(sys.argv[1:],
                     apply_conf=APPLY_CONF,
                     version=version(),
                     doc=__doc__)
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
    ctx['multi_user'] = multiuser(ctx,
                                  ctx['actions'].split(','))
    if do_newdb:
        if ctx.get('multi_db', False):
            ctx['db_name'] = ctx['dbfilter']
        if not ctx['db_name']:
            msg = u"!No DB name supplied!!"
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
        msg = u"------ Operations ended ------"
    else:
        msg = u"###??? Last operation FAILED!!! ###???"
    msg_log(ctx, ctx['level'], msg)
    return sts


if __name__ == "__main__":
    sys.exit(main())
