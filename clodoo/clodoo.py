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

Clodoo is a tool can do some massive operation on 1 or more Odoo database to:

- create consistent database to run tests
- repeat consistent action on many databases
- repeat above actions on every new database

It is called by bash console, there is no funcion on web/GUI interface.

It requires OERPLIB.

Tool syntax:

    $ clodoo.py [-h] [-A actions] [-c file] [-d regex] [-n] [-p dir]
                [-P password] [-q] [-r port] [-U username] [-v] [-V]

    where:
      -h, --help            show this help message and exit
      -A actions, --action-to-do actions
                            action to do (use list_actions to dir)
      -c file, --config file
                            configuration command file
      -d regex, --dbfilter regex
                            DB filter
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
      -v, --verbose         run with debugging output
      -V, --version         show program's version number and exit

Action may be one of:

- check_balance
- check_config
- check_partners
- check_taxes
- drop_db
- echo_company
- echo_db
- echo_user
- import_config_file
- import_file
- install_chart_of_account
- install_language
- install_modules
- list_actions
- list_companies
- list_db
- list_users
- new_db
- per_company
- per_db
- per_user
- run_unit_tests
- set_4_cscs
- set_periods
- show_company_params
- show_db_params
- show_params
- show_user_params
- uninstall_modules
- unit_test
- update_modules
- upgrade_modules
- wep_company
- wep_db
"""

import calendar
import csv
# import pdb
import os.path
import re
import sys
import time
from datetime import date, datetime, timedelta
from os0 import os0

from clodoocore import (eval_value, get_query_id, import_file_get_hdr,
                        validate_field, searchL8, browseL8, write_recordL8,
                        createL8, writeL8, unlinkL8, executeL8, connectL8,
                        get_res_users, psql_connect)
from clodoolib import (crypt, debug_msg_log, decrypt, init_logger, msg_burst,
                       msg_log, parse_args, tounicode)


__version__ = "0.3.2"

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


class Clodoo():

    def __init__(self):
        pass


def version():
    return __version__


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


def do_login(oerp, ctx):
    """Do a login into DB; try using more usernames and passwords"""
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
    pwdlist = ctx['login_password'].split(',')
    for p in ctx['login2_password'].split(','):
        if p and p not in pwdlist:
            pwdlist.append(p)
    if ctx.get('lgi_pwd'):
        for p in ctx['lgi_pwd'].split(','):
            if p and p not in pwdlist:
                pwdlist.insert(0, p)
    user = False
    db_name = get_dbname(ctx, 'login')
    for username in userlist:
        for pwd in pwdlist:
            try:
                if ctx['svc_protocol'] == 'jsonrpc':
                    oerp.login(db_name,
                               login=username,
                               password=decrypt(pwd))
                    user = oerp.env.user
                else:
                    user = oerp.login(database=db_name,
                                      user=username,
                                      passwd=decrypt(pwd))
                break
            except BaseException:
                user = False
            try:
                if ctx['svc_protocol'] == 'jsonrpc':
                    oerp.login(db_name,
                               login=username,
                               password=pwd)
                    user = oerp.env.user
                else:
                    user = oerp.login(database=db_name,
                                      user=username,
                                      passwd=pwd)
                break
            except BaseException:
                user = False
        if user:
            break
    if not user:
        if not ctx.get('no_warning_pwd', False):
            os0.wlog(u"!DB={0}: invalid user/pwd"
                     .format(tounicode(ctx['db_name'])))
        return
    if not ctx['multi_user']:
        ctx = init_user_ctx(oerp, ctx, user)
        msg = ident_user(oerp, ctx, user.id)
        msg_log(ctx, ctx['level'], msg)
    if ctx['set_passepartout']:
        wrong = False
        if username != ctx['login_user']:
            user.login = ctx['login_user']
            wrong = True
        if pwd != ctx['login_password']:
            user.password = decrypt(ctx['login_password'])
            wrong = True
        if wrong:
            try:
                write_recordL8(ctx, user)
                if not ctx.get('no_warning_pwd', False):
                    os0.wlog(u"!DB={0}: updated wrong user/pwd {1} to {2}"
                             .format(tounicode(ctx['db_name']),
                                     tounicode(username),
                                     tounicode(ctx['login_user'])))
            except BaseException:
                os0.wlog(u"!!write error!")
        if user.email != ctx['zeroadm_mail']:
            user.email = ctx['zeroadm_mail']
            try:
                write_recordL8(ctx, user)
                if not ctx.get('no_warning_pwd', False):
                    os0.wlog(u"!DB={0}: updated wrong user {1} to {2}"
                             .format(tounicode(ctx['db_name']),
                                     tounicode(ctx['login2_user']),
                                     tounicode(ctx['login_user'])))
            except BaseException:
                os0.wlog(u"!!write error!")
    if user:
        ctx['_cr'] = psql_connect(ctx)
    return user


def oerp_set_env(confn=None, db=None, ctx=None):
    P_LIST = ('db_host', 'login_user', 'login_password', 'db_name',
              'xmlrpc_port', 'oe_version', 'svc_protocol')
    def oerp_env_def(ctx=None):
        ctx = ctx or {}
        if 'db_host' not in ctx or not ctx['db_host']:
            ctx['db_host'] = 'localhost'
        if 'db_name' not in ctx or not ctx['db_name']:
            ctx['db_name'] = 'demo'
        if 'login_user' not in ctx or not ctx['login_user']:
            ctx['login_user'] = 'admin'
        if 'login_password' not in ctx or not ctx['login_password']:
            ctx['login_password'] = 'admin'
        if 'xmlrpc_port' not in ctx or not ctx['xmlrpc_port']:
            ctx['xmlrpc_port'] = 8069
        if 'oe_version' not in ctx or not ctx['oe_version']:
            ctx['oe_version'] = '7.0'
        if 'svc_protocol' not in ctx or not ctx['svc_protocol']:
            if ctx['oe_version'] in ('6.1', '7.0'):
                ctx['svc_protocol'] = 'xmlrpc'
            else:
                ctx['svc_protocol'] = 'jsonrpc'
        ctx['level'] = 4
        if 'dry_run' not in ctx:
            ctx['dry_run'] = False
        if 'login2_user' not in ctx:
            ctx['login2_user'] = ''
        if 'login2_password' not in ctx:
            ctx['login2_password'] = ''
        if 'multi_user' not in ctx:
            ctx['multi_user'] = False
        if 'set_passepartout' not in ctx:
            ctx['set_passepartout'] = False
        return ctx
    ctx = oerp_env_def(ctx=ctx)
    confn = confn or ctx.get('conf_fn', './inv2draft_n_restore.conf')
    write_confn = False
    try:
        fd = open(confn, 'rU')
        lines = fd.read().split('\n')
        for line in lines:
            tkn = line.split('=')
            for p in P_LIST:
                if tkn[0] == p:
                    if p == 'xmlrpc_port':
                        ctx[p] = int(tkn[1])
                    else:
                        ctx[p] = tkn[1]
        fd.close()
    except:
        write_confn = True
        ctx = oerp_env_def(ctx=ctx)
        for p in (P_LIST):
            ctx[p] = raw_input('%s[def=%s]? ' % (p, ctx[p]))
        ctx = oerp_env_def(ctx=ctx)
    oerp = open_connection(ctx)
    lgiuser = do_login(oerp, ctx)
    if not lgiuser:
        raise RuntimeError('Invalid user or password!')      # pragma: no cover
    uid = lgiuser.id
    if write_confn:
        fd = open(confn, 'w')
        for p in (P_LIST):
            if p == 'xmlrpc_port':
                if ctx[p] != 8069:
                    fd.write('%s=%d\n' % (p, ctx[p]))
            elif p == 'oe_version' and ctx[p] == '7.0':
                pass
            elif p == 'svc_protocol' and ctx[p] == 'xmlrpc':
                pass
            elif p == 'db_host' and ctx[p] == 'localhost':
                pass
            else:
                fd.write('%s=%s\n' % (p, ctx[p]))
        fd.close()
    return oerp, uid, ctx


def get_context(ctx):
    context = {}
    context['lang'] = 'en_US'
    return context


def init_db_ctx(oerp, ctx, db):
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
    else:
        ctx['db_type'] = "C"  # Customer
    return ctx


def init_company_ctx(oerp, ctx, c_id):
    ctx['company_id'] = c_id
    company_obj = browseL8(ctx, 'res.company', c_id)
    ctx['company_name'] = company_obj.name
    if company_obj.country_id:
        ctx['company_country_id'] = company_obj.country_id.id
    else:
        ctx['company_country_id'] = 0
    ctx['company_partner_id'] = company_obj.partner_id.id
    ctx['def_company_id'] = ctx['company_id']
    ctx['def_company_name'] = ctx['company_name']
    if ctx.get('company_country_id', 0) != 0:
        ctx['def_country_id'] = ctx['company_country_id']
    return ctx


def init_user_ctx(oerp, ctx, user):
    ctx['user_id'] = user.id
    if ctx['oe_version'] != "6.1":
        ctx['user_partner_id'] = user.partner_id.id
    ctx['user_name'] = get_res_users(ctx, user, 'name')
    ctx['user_company_id'] = user.company_id.id
    ctx['user_country_id'] = get_res_users(ctx, user, 'country_id')
    if ctx.get('def_company_id', 0) == 0:
        ctx['def_company_id'] = ctx['user_company_id']
        ctx['def_company_name'] = user.company_id.name
    return ctx


def get_dblist(oerp):
    # Interface xmlrpc and jsonrpc are the same
    return oerp.db.list()


def get_companylist(oerp, ctx):
    return searchL8(ctx, 'res.company', [], order='id desc')


def get_userlist(oerp, ctx):
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


def do_group_action(oerp, ctx, action):
    """Do group actions (recursive)"""
    if 'test_unit_mode' not in ctx:
        msg = u"Do group actions"
        msg_log(ctx, ctx['level'], msg)
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
                sts = do_single_action(oerp, lctx, act)
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


def do_single_action(oerp, ctx, action):
    """Do single action (recursive)"""
    if isaction(ctx, action):
        if action == '' or action is False or action is None:
            return STS_SUCCESS
        if ctx.get('db_name', '') == 'auto':
            if action not in ("list_actions", "show_params", "new_db"):
                ctx['db_name'] = get_dbname(ctx, action)
                lgiuser = do_login(oerp, ctx)
                if not lgiuser:
                    action = 'unit_test'
        act = lexec_name(ctx, action)
        if act in list(globals()):
            if action == 'install_modules' and\
                    not ctx.get('module_udpated', False):
                globals()[lexec_name(ctx, 'update_modules')](oerp, ctx)
                ctx['module_udpated'] = True
            return globals()[act](oerp, ctx)
        else:
            return do_group_action(oerp, ctx, action)
    else:
        return STS_FAILED


def do_actions(oerp, ctx):
    """Do actions (recursive)"""
    actions = ctx['actions']
    if not actions:
        return STS_FAILED
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
                sts = do_single_action(oerp, ctx, act)
                if 'actions' in ctx:
                    del ctx['actions']
                actions = []
                decr_lev(ctx)
            else:
                sts = do_single_action(oerp, ctx, act)
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
    lctx = {}
    for n in ctx:
        lctx[n] = ctx[n]
    for p in ('actions',
              'install_modules',
              'uninstall_modules',
              'upgrade_modules'):
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
              # 'code',
              # 'name',
              'filename',
              'hide_cid'):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        elif p in lctx:
            del lctx[p]
    for p in ('lang',
              'dbfilter',
              'companyfilter',
              'userfilter',
              'chart_of_account'):
        pv = get_param_ver(ctx, p)
        if conf_obj.has_option(action, pv):
            lctx[p] = conf_obj.get(action, pv)
        elif conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
    for p in ('install_modules',
              'uninstall_modules',
              'actions',
              'hide_cid'):
        pv = get_param_ver(ctx, p)
        if pv in lctx:
            lctx[pv] = os0.str2bool(lctx[pv], lctx[pv])
        elif p in lctx:
            lctx[p] = os0.str2bool(lctx[p], lctx[p])
    return lctx


def ident_db(oerp, ctx, db):
    db_name = get_dbname(ctx, '')
    msg = u"DB=" + db + " [" + ctx.get('db_type', '') + "]"
    if db_name != db:
        msg = msg + " - default " + db_name
    return msg


def ident_company(oerp, ctx, c_id):
    msg = u"Company {0:>3})\t'{1}'".format(c_id,
                                           tounicode(ctx.get('company_name',
                                                             '')))
    return msg


def ident_user(oerp, ctx, u_id):
    user = browseL8(ctx, 'res.users', u_id)
    msg = u"User {0:>2} {1}\t'{2}'\t{3}\t[{4}]".format(
          u_id,
          tounicode(user.login),
          tounicode(ctx['user_name']),
          tounicode(get_res_users(ctx, user, 'email')),
          tounicode(user.company_id.name))
    return msg


#############################################################################
# Public actions
#
def act_list_actions(oerp, ctx):
    for act in sorted(ctx['_lx_act']):
        print "- %s" % act
    return STS_SUCCESS


def act_show_params(oerp, ctx):
    if ctx['dbg_mode']:
        pwd = raw_input('password ')
    else:
        pwd = False
    print "- hostname      = %s " % ctx['db_host']
    print "- protocol      = %s " % ctx['svc_protocol']
    print "- port          = %s " % ctx['xmlrpc_port']
    print "- odoo version  = %s " % ctx['oe_version']
    if pwd:
        print "- password      = %s " % crypt(pwd)
    return STS_SUCCESS


def act_list_db(oerp, ctx):
    dblist = get_dblist(oerp)
    for db in sorted(dblist):
        ctx = init_db_ctx(oerp, ctx, db)
        sts = act_echo_db(oerp, ctx)
    return sts


def act_echo_db(oerp, ctx):
    msg = ident_db(oerp, ctx, ctx['db_name'])
    ident = ' ' * ctx['level']
    print " %s%s" % (ident, msg)
    return STS_SUCCESS


def act_show_db_params(oerp, ctx):
    ident = ' ' * ctx['level']
    print "%s- DB name       = %s " % (ident, ctx.get('db_name', ""))
    print "%s- DB type       = %s " % (ident, ctx.get('db_type', ""))
    return STS_SUCCESS


def act_list_companies(oerp, ctx):
    company_ids = get_companylist(oerp, ctx)
    for c_id in company_ids:
        ctx = init_company_ctx(oerp, ctx, c_id)
        sts = act_echo_company(oerp, ctx)
    return sts


def act_echo_company(oerp, ctx):
    c_id = ctx['company_id']
    msg = ident_company(oerp, ctx, c_id)
    ident = ' ' * ctx['level']
    print " %s%s" % (ident, msg)
    return STS_SUCCESS


def act_show_company_params(oerp, ctx):
    ident = ' ' * ctx['level']
    print "%s- company_id    = %d " % (ident, ctx.get('company_id', 0))
    print "%s- company name  = %s " % (ident, ctx.get('company_name', ""))
    print "%s- c. country_id = %d " % (ident, ctx.get('company_country_id', 0))
    print "%s- c. partner_id = %d " % (ident, ctx.get('company_partner_id', 0))
    return STS_SUCCESS


def act_list_users(oerp, ctx):
    user_ids = get_userlist(oerp, ctx)
    for u_id in user_ids:
        user_obj = browseL8(ctx, 'res.users', u_id)
        ctx = init_user_ctx(oerp, ctx, user_obj)
        sts = act_echo_user(oerp, ctx)
    return sts


def act_echo_user(oerp, ctx):
    u_id = ctx['user_id']
    msg = ident_user(oerp, ctx, u_id)
    ident = ' ' * ctx['level']
    print " %s%s" % (ident, msg)
    return STS_SUCCESS


def act_show_user_params(oerp, ctx):
    ident = ' ' * ctx['level']
    print "%s- user_id       = %d " % (ident, ctx.get('user_id', 0))
    print "%s- user name     = %s " % (ident, ctx.get('user_name', ""))
    print "%s- u. partner_id = %d " % (ident, ctx.get('user_partner_id', 0))
    print "%s- u. country_id = %d " % (ident, ctx.get('user_country_id', 0))
    print "%s- u. company_id = %d " % (ident, ctx.get('user_company_id', 0))
    return STS_SUCCESS


def act_unit_test(oerp, ctx):
    """This function acts just for unit test"""
    return STS_SUCCESS


def act_run_unit_tests(oerp, ctx):
    """"Run module unit test"""
    try:
        executeL8(ctx,
                  'ir.actions.server',
                  'Run Unit test',
                  'banking_export_pain')
    except BaseException:
        return STS_FAILED
    return STS_SUCCESS


def act_drop_db(oerp, ctx):
    """Drop a DB"""
    sts = STS_SUCCESS
    msg = "Drop DB %s" % ctx['db_name']
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        try_again = True
        sts = STS_FAILED
        while sts != STS_SUCCESS:
            try:
                oerp.db.drop(ctx['admin_passwd'],
                             ctx['db_name'])
                sts = STS_SUCCESS
                if ctx['db_name'][0:11] != 'clodoo_test':
                    time.sleep(2)
            except BaseException:
                sts = STS_FAILED
                if try_again:
                    cmd = 'pg_db_active -wa %s' % ctx['db_name']
                    os0.muteshell(cmd, simulate=False, keepout=False)
                    try_again = False
                else:
                    break
    return sts


def act_wep_company(oerp, ctx):
    """Wep a DB (delete all record of company but keep res_parter"""
    sts = STS_SUCCESS
    c_id = ctx['company_id']
    msg = ident_company(oerp, ctx, c_id)
    msg = "Wep company %s" % ctx['company_name']
    msg_log(ctx, ctx['level'], msg)
    set_server_isolated(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_mail_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_project_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_purchases_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_crm_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_sales_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_logistic_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_marketing_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_hr_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_analytics_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_account_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_product_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_company_partner_records(oerp, ctx)
    if sts == STS_SUCCESS:
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


def act_wep_db(oerp, ctx):
    """Wep a DB (delete all record but keep res_parter)"""
    sts = STS_SUCCESS
    msg = "Wep DB %s" % ctx['db_name']
    msg_log(ctx, ctx['level'], msg)
    set_server_isolated(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_mail_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_note_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_project_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_purchases_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_crm_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_sales_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_logistic_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_marketing_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_account_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_hr_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_product_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_partner_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = remove_all_user_records(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = reset_sequence(oerp, ctx)
    if sts == STS_SUCCESS:
        sts = reset_menuitem(oerp, ctx)
    return sts


def act_new_db(oerp, ctx):
    """Create new DB"""
    sts = STS_SUCCESS
    lang = ctx.get('lang', 'en_US')
    msg = "Create DB %s [lang=%s, demo=%s]" % (ctx['db_name'],
                                               lang,
                                               str(ctx['with_demo']))
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        if ctx['db_name'] == 'auto':
            ctx['db_name'] = create_zero_db(oerp, ctx)
            msg = "Assigned name is %s" % (ctx['db_name'])
            msg_log(ctx, ctx['level'], msg)
        if ctx['db_name']:
            try:
                if ctx['svc_protocol'] == 'jsonrpc':
                    oerp.db.create(ctx['admin_passwd'],
                                   ctx['db_name'],
                                   ctx['with_demo'],
                                   lang,
                                   decrypt(ctx['login_password']))
                    time.sleep(3)

                elif oerp.db.server_version() == '7.0':
                    oerp.db.create_and_wait(ctx['admin_passwd'],
                                            ctx['db_name'],
                                            ctx['with_demo'],
                                            lang,
                                            decrypt(ctx['login_password']))
                else:
                    oerp.db.create_database(ctx['admin_passwd'],
                                            ctx['db_name'],
                                            ctx['with_demo'],
                                            lang,
                                            decrypt(ctx['login_password']))
                    time.sleep(3)
                ctx['no_warning_pwd'] = True
                lgiuser = do_login(oerp, ctx)
                if not lgiuser:
                    sts = STS_FAILED
            except BaseException:
                sts = STS_FAILED
        else:
            sts = STS_FAILED
    return sts


def act_per_db(oerp, ctx):
    """Iter action on DBs"""
    dblist = get_dblist(oerp)
    if 'actions_db' in ctx:
        del ctx['actions_db']
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for db in sorted(dblist):
        if re.match(ctx['dbfilter'], db):
            ctx = init_db_ctx(oerp, ctx, db)
            msg = ident_db(oerp, ctx, db)
            msg_log(ctx, ctx['level'], msg)
            if ctx['dbtypefilter']:
                if ctx['db_type'] != ctx['dbtypefilter']:
                    msg = u"DB skipped by invalid db_type"
                    debug_msg_log(ctx, ctx['level'] + 1, msg)
                    continue
            lgiuser = do_login(oerp, ctx)
            if lgiuser:
                ctx['actions'] = saved_actions
                sts = do_actions(oerp, ctx)
            else:
                sts = STS_FAILED
            if sts != STS_SUCCESS:
                break
    return sts


def act_per_company(oerp, ctx):
    """iter on companies"""
    if 'actions_mc' in ctx:
        del ctx['actions_mc']
    company_ids = get_companylist(oerp, ctx)
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for c_id in company_ids:
        company_obj = browseL8(ctx, 'res.company', c_id)
        if re.match(ctx['companyfilter'], company_obj.name):
            ctx = init_company_ctx(oerp, ctx, c_id)
            msg = ident_company(oerp, ctx, c_id)
            msg_log(ctx, ctx['level'], msg)
            ctx['actions'] = saved_actions
            sts = do_actions(oerp, ctx)
            if sts != STS_SUCCESS:
                break
    return sts


def act_per_user(oerp, ctx):
    """iter on companies"""
    if 'actions_uu' in ctx:
        del ctx['actions_uu']
    user_ids = get_userlist(oerp, ctx)
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for u_id in user_ids:
        user_obj = browseL8(ctx, 'res.users', u_id)
        if re.match(ctx['userfilter'], user_obj.name):
            ctx = init_user_ctx(oerp, ctx, user_obj)
            msg = ident_user(oerp, ctx, u_id)
            msg_log(ctx, ctx['level'], msg)
            ctx['actions'] = saved_actions
            sts = do_actions(oerp, ctx)
            ctx['def_company_id'] = ctx['company_id']
            ctx['def_company_name'] = ctx['company_name']
            if ctx.get('company_country_id', 0) != 0:
                ctx['def_country_id'] = ctx['company_country_id']
            if sts != STS_SUCCESS:
                break
    return sts


def act_update_modules(oerp, ctx):
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
    return STS_SUCCESS


def act_upgrade_modules(oerp, ctx):
    """Upgrade module from list"""
    msg = u"Upgrade modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = get_real_paramvalue(ctx, 'upgrade_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    sts = STS_SUCCESS
    for m in module_list:
        if m == "":
            continue
        ids = searchL8(ctx, 'ir.module.module',
                       [('name', '=', m),
                        ('state', '=', 'installed')],
                       context=context)
        if not ctx['dry_run']:
            if len(ids):
                if cur_lang != 'en_US':
                    cur_lang = 'en_US'
                    set_user_lang(oerp, cur_lang, ctx)
                try:
                    executeL8(ctx,
                              'ir.module.module',
                              'button_immediate_upgrade',
                              ids)
                    msg = "name={0}".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    time.sleep(2)
                except BaseException:
                    msg = "!Module {0} not upgradable!".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
            else:
                msg = "Module {0} not installed!".format(m)
                msg_log(ctx, ctx['level'] + 1, msg)
        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)
    if cur_lang != user_lang:
        set_user_lang(oerp, user_lang, ctx)
    return sts


def act_uninstall_modules(oerp, ctx):
    """Uninstall module from list"""
    msg = u"Uninstall unuseful modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = get_real_paramvalue(ctx, 'uninstall_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    model = 'ir.module.module'
    sts = STS_SUCCESS
    for m in module_list:
        if m == "":
            continue
        ids = searchL8(ctx, model,
                       [('name', '=', m),
                        ('state', '=', 'installed')],
                       context=context)
        if not ctx['dry_run']:
            if len(ids):
                if cur_lang != 'en_US':
                    cur_lang = 'en_US'
                    set_user_lang(oerp, cur_lang, ctx)
                try:
                    executeL8(ctx,
                              model,
                              'button_immediate_uninstall',
                              ids)
                    msg = "name={0}".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    time.sleep(2)
                except BaseException:
                    msg = "!Module {0} not uninstallable!".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
            else:
                msg = "Module {0} already uninstalled!".format(m)
                msg_log(ctx, ctx['level'] + 1, msg)
            ids = oerp.search(model,
                              [('name', '=', m),
                               ('state', '==', 'uninstalled')],
                              context=context)
            if len(ids):
                unlinkL8(ctx, model, ids)
        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)
    if cur_lang != user_lang:
        set_user_lang(oerp, user_lang, ctx)
    return sts


def act_install_modules(oerp, ctx):
    """Install modules from list"""
    msg = u"Install modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = get_real_paramvalue(ctx, 'install_modules').split(',')
    context = get_context(ctx)
    user_lang = get_user_lang(ctx)
    cur_lang = user_lang
    model = 'ir.module.module'
    sts = STS_SUCCESS
    for m in module_list:
        if m == "":
            continue
        ids = searchL8(ctx, model,
                       [('name', '=', m),
                        ('state', '=', 'uninstalled')],
                       context=context)
        if not ctx['dry_run']:
            if len(ids):
                if cur_lang != 'en_US':
                    cur_lang = 'en_US'
                    set_user_lang(oerp, cur_lang, ctx)
                try:
                    executeL8(ctx,
                              model,
                              'button_immediate_install',
                              ids)
                    msg = "name={0}".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    time.sleep(2)
                except BaseException:
                    msg = "!Module {0} not installable!".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
            else:
                ids = searchL8(ctx, 'ir.module.module',
                               [('name', '=', m)],
                               context=context)
                if len(ids):
                    msg = "Module {0} already installed!".format(m)
                else:
                    msg = "!Module {0} does not exist!".format(m)
                    sts = STS_FAILED
                msg_log(ctx, ctx['level'] + 1, msg)
        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)
    if cur_lang != user_lang:
        set_user_lang(oerp, user_lang, ctx)
    return sts


def act_install_language(oerp, ctx):
    """Install new language"""
    lang = ctx.get('lang', 'en_US')
    msg = u"Install language %s" % lang
    msg_log(ctx, ctx['level'], msg)
    model = 'res.lang'
    ids = searchL8(ctx, model, [('code', '=', lang)])
    if len(ids) == 0:
        vals = {}
        vals['lang'] = lang
        vals['overwrite'] = True
        id = createL8(ctx, 'base.language.install', vals)
        executeL8(ctx,
                  'base.language.install',
                  'lang_install',
                  [id])
    id = createL8(ctx, 'base.update.translations', {'lang': lang})
    executeL8(ctx,
              'base.update.translations',
              'act_update',
              [id])
    return STS_SUCCESS


def act_install_chart_of_account(oerp, ctx):
    """Install chart of account"""
    coa = ctx.get('chart_of_account',
                  'Italy - Piano dei conti Zeroincombenze(R)')
    msg = u"Install chart of account %s" % coa
    msg_log(ctx, ctx['level'], msg)
    return install_chart_of_account(oerp, ctx, coa)


def act_import_file(oerp, ctx):
    o_model = {}
    for p in ('model',
              'model_code',
              'model_name',
              'hide_cid'):
        if p in ctx:
            o_model[p] = ctx[p]
    if 'filename' in ctx:
        csv_fn = ctx['filename']
    elif 'model' not in o_model:
        msg = u"!Wrong import file!"
        msg_log(ctx, ctx['level'], msg)
        return STS_FAILED
    else:
        csv_fn = o_model['model'].replace('.', '_') + ".csv"
    msg = u"Import file " + csv_fn
    msg_log(ctx, ctx['level'], msg)
    return import_file(oerp, ctx, o_model, csv_fn)


def act_import_config_file(oerp, ctx):
    if 'filename' in ctx:
        csv_fn = ctx['filename']
    msg = u"Import config file " + csv_fn
    msg_log(ctx, ctx['level'], msg)
    return import_config_file(oerp, ctx, csv_fn)


def act_check_config(oerp, ctx):
    if not ctx['dry_run'] and 'def_company_id' in ctx:
        if ctx['def_company_id'] is not None:
            msg = u"Check config"
            msg_log(ctx, ctx['level'], msg)

            o_model = {}
            csv_fn = "sale-shop.csv"
            import_file(oerp, ctx, o_model, csv_fn)


def act_check_partners(oerp, ctx):
    msg = u"Check for partners"
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    partner_ids = searchL8(ctx, 'res.partner',
                           [('company_id', '=', company_id)])
    rec_ctr = 0
    for partner_id in partner_ids:
        try:
            partner_obj = browseL8(ctx, 'res.partner', partner_id)
        except BaseException:
            msg = u"Wrong partner id=" + str(partner_id)
            msg_log(ctx, ctx['level'], msg)
            continue
        rec_ctr += 1
        msg_burst(4, "Partner ",
                  rec_ctr,
                  partner_obj.name)
        if partner_obj.vat:
            iso = partner_obj.vat.upper()[0:2]
            vatn = partner_obj.vat[2:]
            if iso >= "00" and iso <= "99" and len(partner_obj.vat) == 11:
                iso = 'IT'
                vatn = partner_obj.vat
                vals = {}
                vals['vat'] = iso + vatn
                msg = u"Wrong VAT " + partner_obj.vat
                msg_log(ctx, ctx['level'], msg)
                try:
                    writeL8(ctx, 'res.partner', partner_id, vals)
                except BaseException:
                    msg = partner_obj.name + " WRONG VAT"
                    msg_log(ctx, ctx['level'], msg)
            elif iso == "1I" and len(vatn) == 11:
                iso = 'IT'
                vals = {}
                vals['vat'] = iso + vatn
                msg = u"Wrong VAT " + partner_obj.vat
                msg_log(ctx, ctx['level'], msg)
                try:
                    writeL8(ctx, 'res.partner', [partner_id], vals)
                except BaseException:
                    msg = partner_obj.name + " WRONG VAT"
                    msg_log(ctx, ctx['level'], msg)
            elif iso < "AA" or iso > "ZZ":
                msg = partner_obj.name + " WRONG VAT"
                msg_log(ctx, ctx['level'], msg)
            elif vatn.strip() == "":
                msg = partner_obj.name + " WRONG VAT"
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_set_periods(oerp, ctx):
    msg = u"Set account periods "
    msg_log(ctx, ctx['level'], msg)
    model = 'account.fiscalyear'
    company_id = ctx['company_id']
    fiscalyear_id, process_it, last_name, last_start, last_stop = \
        read_last_fiscalyear(oerp, company_id, ctx)
    if process_it and fiscalyear_id == 0:
        name, date_start, date_stop = \
            evaluate_date_n_name(oerp,
                                 last_name,
                                 last_start,
                                 last_stop,
                                 'year',
                                 ctx)
        code = re.findall('[0-9./-]+', name)[0]
        fiscal_year_id = createL8(ctx, model, {'name': name,
                                               'code': code,
                                               'date_start': str(date_start),
                                               'date_stop': str(date_stop),
                                               'company_id': company_id})
        msg = u"Added fiscalyear %s" % name
        msg_log(ctx, ctx['level'], msg)
        add_periods(oerp,
                    company_id,
                    fiscal_year_id,
                    last_name,
                    last_start,
                    last_stop,
                    ctx)
    set_journal_per_year(oerp, ctx)
    return STS_SUCCESS


def act_check_taxes(oerp, ctx):
    msg = u"Check for taxes; period: " + \
        ctx['date_start'] + ".." + ctx['date_stop']
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    period_ids = searchL8(ctx, 'account.period',
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    # model = 'account.tax'
    # ids = searchL8(ctx, model,
    #                   [('company_id', '=', company_id)])
    # base_vat = {}
    # vat_base = {}
    # base_vat_nc = {}
    # vat_base_nc = {}
    # for id in ids:
    #     tax_obj = browseL8(ctx,  model, id)
    #     id_imp = tax_obj.base_code_id.id
    #     id_iva = tax_obj.tax_code_id.id
    #     base_vat[id_imp] = id_iva
    #     vat_base[id_iva] = id_imp
    #     id_imp_nc = tax_obj.ref_base_code_id.id
    #     id_iva_nc = tax_obj.ref_tax_code_id.id
    #     base_vat_nc[id_imp_nc] = id_iva_nc
    #     vat_base_nc[id_iva_nc] = id_imp_nc
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
        move_line_obj = browseL8(ctx,
                                 'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        tax_code_obj = move_line_obj.tax_code_id
        if tax_code_obj:
            # move_hdr_id = move_line_obj.move_id.id
            level = '9'
            while True:
                code = tax_code_obj.code
                name = tax_code_obj.name
                if isinstance(code, basestring):
                    x = code
                else:
                    x = ''
                if isinstance(name, basestring):
                    x = x + ' - ' + name
                add_on_account(tax_balance,
                               level,
                               x,
                               move_line_obj.tax_amount,
                               0)
                if not tax_code_obj.parent_id:
                    break
                tax_code_obj = tax_code_obj.parent_id
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


def act_check_balance(oerp, ctx):
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
        move_line_obj = browseL8(ctx,
                                 'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        warn_rec = False
        move_hdr_id = move_line_obj.move_id.id
        account_obj = move_line_obj.account_id
        account_tax_obj = move_line_obj.account_tax_id
        journal_obj = move_line_obj.journal_id
        acctype_id = account_obj.user_type.id
        acctype_obj = browseL8(ctx,
                               'account.account.type', acctype_id)
        if acctype_obj.report_type not in ("asset", "liability",
                                           "income", "expense"):
            warn_rec = "Untyped"
        if account_obj.parent_id:
            parent_account_obj = account_obj.parent_id
            parent_acctype_id = parent_account_obj.user_type.id
            parent_acctype_obj = browseL8(ctx, 'account.account.type',
                                          parent_acctype_id)
            parent_code = parent_account_obj.code
        else:
            parent_account_obj = None
            parent_acctype_id = 0
            parent_acctype_obj = None
            parent_code = None
            warn_rec = 'Orphan'
        if parent_acctype_obj and\
                parent_acctype_obj.report_type and\
                parent_acctype_obj.report_type != 'none':
            if parent_acctype_obj.report_type in ("asset",
                                                  "liability",
                                                  "income",
                                                  "expense") and \
                    acctype_obj.report_type != parent_acctype_obj.report_type:
                warn_rec = "Mismatch"

        code = account_obj.code
        clf3 = acctype_obj.name
        clf = acctype_obj.report_type
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

        if (account_obj.company_id.id != company_id):
            msg = u"Invalid company account {0} in {1:>6}/{2:>6}  {3}".format(
                os0.u(code),
                move_hdr_id,
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (account_tax_obj and account_tax_obj.company_id.id != company_id):
            msg = u"Invalid company account tax {0} in {1:>6}/{2:>6}  {3}".\
                format(os0.u(code),
                       move_hdr_id,
                       move_line_id,
                       os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (journal_obj and journal_obj.company_id.id != company_id):
            msg = u"Invalid company journal {0} in {1:>6}/{2:>6}  {3}".format(
                os0.u(code),
                move_hdr_id,
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)

        if move_line_obj.partner_id and \
                move_line_obj.partner_id.id:
            partner_id = move_line_obj.partner_id.id
            if clf3 == "Crediti":
                kk = 'C'
            elif clf3 == "Debiti":
                kk = 'S'
            else:
                kk = 'X'
            kk = kk + '\n' + code + '\n' + str(partner_id)
            if kk not in acc_partners:
                acc_partners[kk] = 0
            acc_partners[kk] += move_line_obj.debit
            acc_partners[kk] -= move_line_obj.credit

        level = '9'
        add_on_account(acc_balance,
                       level,
                       code,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '8'
        add_on_account(acc_balance,
                       level,
                       parent_code,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '4'
        add_on_account(acc_balance,
                       level,
                       clf3,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '2'
        add_on_account(acc_balance,
                       level,
                       clf2,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '1'
        add_on_account(acc_balance,
                       level,
                       clf1,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '0'
        add_on_account(acc_balance,
                       level,
                       '_',
                       move_line_obj.debit,
                       move_line_obj.credit)

        if warn_rec:
            msg = u"Because {0:8} look at {1:>6}/{2:>6} record {3}".format(
                warn_rec,
                move_hdr_id,
                move_line_id,
                os0.u(move_line_obj.ref))
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
                partner_obj = browseL8(ctx, 'res.partner', partner_id)
                msg = u"{0:<16} {1:<60} {2:11.2f}".format(
                    os0.u(kk.replace('\n', '.')),
                    os0.u(partner_obj.name),
                    acc_partners[kk])
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_recompute_tax_balance(oerp, ctx):
    msg = u"Recompute tax balance"
    msg_log(ctx, ctx['level'], msg)
    sts = recompute_tax_balance(oerp, ctx)
    return sts


def act_recompute_balance(oerp, ctx):
    msg = u"Recompute balance"
    msg_log(ctx, ctx['level'], msg)
    sts = recompute_balance(oerp, ctx)
    return sts


def act_set_4_cscs(oerp, ctx):
    msg = u"Set for cscs"
    msg_log(ctx, ctx['level'], msg)
    # sts = analyze_invoices(oerp, ctx, 'out_invoice')
    # if sts == STS_SUCCESS:
    #    sts = analyze_invoices(oerp, ctx, 'in_invoice')
    sts = set_account_type(oerp, ctx)
    return sts


def act_update_4_next_generation(oerp, ctx):
    msg = u"Upgrade next generation"
    msg_log(ctx, ctx['level'], msg)
    model = 'ir.module.module'
    model2 = 'ir.module.module.dependency'
    ids = searchL8(ctx, model, [('state', '=', 'uninstallable')])
    for id in ids:
        try:
            unlinkL8(ctx, model, [id])
        except BaseException:
            pass
    sts = act_update_modules(oerp, ctx)
    ids = searchL8(ctx, model, [])
    for id in ids:
        module = oerp.read(model, [id], ['name', 'dependencies_id'])
        if module[0]['dependencies_id']:
            for id2 in module[0]['dependencies_id']:
                module2 = oerp.read(model2, [id2], ['name'])
                if len(module2) == 0:
                    msg = 'dependency %d (%s) not found!' % (id2,
                                                             module[0]['name'])
                    msg_log(ctx, ctx['level'], msg)
                    writeL8(ctx, model, [id],
                            {'dependencies_id': [(2, id2)]})
    ids = searchL8(ctx, model,
                   ['|',
                    ('state', '=', 'installed'),
                    ('state', '=', 'to upgrade')])
    module_ids = []
    for id in ids:
        module_ids.append(id)
        writeL8(ctx, model, [id], {'state': 'to upgrade'})
    for module in ('base', 'web', 'base_setup',
                   'report_webkit', 'base_status', 'board', 'base_iban',
                   'process', 'decimal_precision', 'plugin',
                   'web_gantt', 'web_diagram', 'web_kanban', 'web_graph',
                   'web_calendar', 'web_analytics', 'web_color',
                   'web_export_view', 'base_import', 'web_gantt_chart',
                   'mail', 'email_template', 'analytic',
                   'product', 'account', 'knowledge',
                   'document', 'fetchmail'):
        ids = searchL8(ctx, model,
                       [('name', '=', module)])
        if len(ids) and ids[0] in module_ids:
            msg = 'Check for %s' % (module)
            msg_log(ctx, ctx['level'], msg)
            id = ids[0]
            ix = module_ids.index(id)
            del module_ids[ix]
            writeL8(ctx, model, [id], {'state': 'installed'})
            ctx['upgrade_modules'] = module
            act_upgrade_modules(oerp, ctx)
    again = True
    max_depth = 16
    msg = 'Analyzing all dependencies'
    msg_log(ctx, ctx['level'], msg)
    while again:
        again = False
        max_depth -= 1
        if max_depth == 0:
            msg = 'Module inheritance too deep'
            msg_log(ctx, ctx['level'], msg)
            break
        noop = False
        for id in module_ids:
            module = oerp.read(model, [id], ['name',
                                             'state',
                                             'dependencies_id'])
            msg = 'Check for %s (%s)' % (module[0]['name'],
                                         module[0]['state'])
            msg_log(ctx, ctx['level'], msg)
            if module[0]['state'] != 'installed':
                if module[0]['dependencies_id']:
                    for id2 in module[0]['dependencies_id']:
                        module2 = oerp.read(model2, [id2], ['name', 'state'])
                        if module2[0]['state'] != 'installed':
                            noop = True
                            break
                if noop:
                    noop = False
                    continue
                ix = module_ids.index(id)
                del module_ids[ix]
                writeL8(ctx, model, [id], {'state': 'installed'})
                ctx['upgrade_modules'] = module[0]['name']
                act_upgrade_modules(oerp, ctx)
                again = True
    return sts


def act_upgrade_l10n_it_base(oerp, ctx):
    msg = u"Upgrade module l10n_it_base"
    msg_log(ctx, ctx['level'], msg)
    sts = act_update_modules(oerp, ctx)
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
        module_obj = browseL8(ctx,  model, id)
        prior_state[id] = module_obj.state
        if module_obj.name == 'l10n_it_base':
            l10n_it_base_state = module_obj.state
        else:
            if module_obj.name == 'l10n_it_bbone':
                # l10n_it_bb_id = id
                l10n_it_bb_state = module_obj.state
            writeL8(ctx, model, [id], {'state': 'uninstalled'})
    if l10n_it_bb_state == 'installed' and l10n_it_base_state == 'installed':
        sts = cvt_ur_ui_view(oerp,
                             'l10n_it_bbone',
                             'l10n_it_base',
                             'res.city',
                             ctx)
    if l10n_it_bb_state == 'installed':
        for model in ('res.country',
                      'res.region',
                      'res.country.state',
                      'res.province',
                      'res.city'):
            sts = cvt_ir_model_data(oerp,
                                    'l10n_it_bbone',
                                    'l10n_it_base',
                                    model,
                                    ctx)
    model = 'ir.module.module'
    for id in prior_state:
        state = prior_state[id]
        writeL8(ctx, model, [id], {'state': state})
    if l10n_it_base_state == 'installed':
        ctx['upgrade_modules'] = 'l10n_it_base'
        sts = act_upgrade_modules(oerp, ctx)
    if l10n_it_bb_state == 'installed':
        ctx['upgrade_modules'] = 'l10n_it_bbone'
        sts = act_upgrade_modules(oerp, ctx)
    ctx['upgrade_modules'] = ''
    s = ''
    for id in prior_state:
        module_obj = browseL8(ctx,  model, id)
        if module_obj.name != 'l10n_it_base' and \
                module_obj.name != 'l10n_it_bbone' and \
                module_obj.name != 'zeroincombenze':
            ctx['upgrade_modules'] += s
            ctx['upgrade_modules'] += module_obj.name
            s = ','
    if ctx['upgrade_modules']:
        sts = act_upgrade_modules(oerp, ctx)
    return sts


def read_last_fiscalyear(oerp, company_id, ctx):
    model = 'account.fiscalyear'
    fiscalyear_ids = searchL8(ctx, model,
                              [('company_id', '=', company_id)])
    last_start = date(1970, 1, 1)
    last_stop = date(1970, 12, 31)
    last_name = ''
    valid_fiscalyear_id = 0
    process_it = False
    for fiscalyear_id in fiscalyear_ids:
        fiscalyear = browseL8(ctx,  model, fiscalyear_id)
        name = fiscalyear.name
        date_start = fiscalyear.date_start
        date_stop = fiscalyear.date_stop
        ids = searchL8(ctx, 'account.period',
                       [('company_id', '=', company_id),
                        ('date_start', '>=', str(date_start)),
                        ('date_stop', '<=', str(date_stop))])
        if date.today() >= date_start and date.today() <= date_stop:
            valid_fiscalyear_id = fiscalyear_id
        elif len(ids) == 0:
            valid_fiscalyear_id = fiscalyear_id
        else:
            if date_start > last_start:
                last_start = date_start
                process_it = True
                last_name = name
            if date_stop > last_stop:
                last_stop = date_stop
    return valid_fiscalyear_id, process_it, last_name, last_start, last_stop


def add_periods(oerp, company_id, fiscalyear_id,
                last_name, last_start, last_stop, ctx):
    model = 'account.period'
    period_ids = searchL8(ctx, model,
                          [('company_id', '=', company_id),
                           ('date_start', '>=', str(last_start)),
                           ('date_stop', '<=', str(last_stop))])
    for period_id in period_ids:
        period = browseL8(ctx,  model, period_id)
        name = period.name
        date_start = period.date_start
        date_stop = period.date_stop
        special = period.special
        name, date_start, date_stop = \
            evaluate_date_n_name(oerp,
                                 name,
                                 date_start,
                                 date_stop,
                                 'period',
                                 ctx)
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


def set_journal_per_year(oerp, ctx):
    company_id = ctx['company_id']
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


def evaluate_date_n_name(oerp, last_name, last_start, last_stop, yp, ctx):
    if yp == 'year':
        date_start = last_stop + timedelta(1)
    else:
        if last_start.day >= 28:
            day = calendar.monthrange(last_start.year + 1, last_start.month)[1]
        else:
            day = last_start.day
        date_start = date(last_start.year + 1,
                          last_start.month,
                          day)
    if last_stop.day >= 28:
        day = calendar.monthrange(last_stop.year + 1, last_stop.month)[1]
    else:
        day = last_stop.day
    date_stop = date(last_stop.year + 1,
                     last_stop.month,
                     day)
    n = (last_stop.year + 1) % 100
    o = last_stop.year % 100
    name = last_name.replace(str(o), str(n))
    n = o
    o = (last_stop.year - 1) % 100
    name = name.replace(str(o), str(n))
    return name, date_start, date_stop


def get_payment_info(oerp, move_line_obj, ctx):
    """Return move (header) and move_line (detail) ids of passed move line
    record and return payment state if needed to become draft
    """
    move_line_id = move_line_obj.id
    move_id = move_line_obj.move_id.id
    move_obj = browseL8(ctx, 'account.move', move_id)
    mov_state = False
    if move_obj.state in PAY_MOVE_STS_2_DRAFT:
        mov_state = move_obj.state
    return move_id, move_line_id, mov_state


def get_reconcile_from_inv(oerp, inv_id, ctx):
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
    account_invoice_obj = browseL8(ctx, model,
                                   inv_id)
    if account_invoice_obj.payment_ids:
        partner_id = account_invoice_obj.partner_id.id
        move_id = account_invoice_obj.move_id.id
        move_lines = searchL8(ctx, 'account.move.line',
                              [('move_id', '=', move_id),
                               ('partner_id', '=', partner_id), ])
        for move_line_id in move_lines:
            type = browseL8(ctx, 'account.account',
                            browseL8(ctx, 'account.move.line',
                                     move_line_id).account_id.id).type
            if type == 'receivable' or type == 'payable':
                reconciles.append(move_line_id)
        for move_line_obj in account_invoice_obj.payment_ids:
            move_id, move_line_id, mov_state = \
                get_payment_info(oerp, move_line_obj, ctx)
            reconciles.append(move_line_id)
            if mov_state:
                move_dict[state].append(move_id)
    if account_invoice_obj.state in INVOICES_STS_2_DRAFT:
        move_dict[account_invoice_obj.state].append(inv_id)
    return reconciles, move_dict


def refresh_reconcile_from_inv(oerp, inv_id, reconciles, ctx):
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
    account_invoice_obj = browseL8(ctx, model,
                                   inv_id)
    partner_id = account_invoice_obj.partner_id.id
    if account_invoice_obj.move_id:
        move_id = account_invoice_obj.move_id.id
    else:
        move_id = False
    move_lines = searchL8(ctx, 'account.move.line',
                          [('move_id', '=', move_id),
                           ('partner_id', '=', partner_id), ])
    for move_line_id in move_lines:
        type = browseL8(ctx, 'account.account',
                        browseL8(ctx, 'account.move.line',
                                 move_line_id).account_id.id).type
        if type == 'receivable' or type == 'payable':
            new_reconciles.append(move_line_id)
    partner_id = account_invoice_obj.partner_id.id
    if account_invoice_obj.move_id:
        move_id = account_invoice_obj.move_id.id
    else:
        move_id = False
    company_id = account_invoice_obj.company_id.id
    valid_recs = True
    for move_line_id in reconciles[1:]:
        move_line_obj = browseL8(ctx,
                                 'account.move.line', move_line_id)
        if move_line_obj.partner_id.id != partner_id or \
                move_line_obj.company_id.id != company_id:
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


def set_user_lang(oerp, lang, ctx):
    model = 'res.users'
    user_id = ctx.get('user_id', 1)
    user_obj = browseL8(ctx, model, user_id)
    if not user_obj:
        msg = u"!User %s not found" % user_id
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    writeL8(ctx, 'res.users', user_id, {'lang': lang})


def get_reconcile_list_from_move_line(oerp, move_line_obj, ctx):
    """Like get_reconcile_from_inv but it is passed move_line id
    If move_line is not of an invoice, returned lists are empties.
    @param move_line_obj: record of move_line (may be invoice or not)
    @return: list of reconciled move lines of passed (included) invoice
    @return: dictionary of posted movements (header) to set to draft state
    """
    # For every invoice id, store payment move line (detail) list
    reconcile_dict = {}
    # For every state, store move (header) list to update state
    move_dict = {}
    for state in STATES_2_DRAFT:
        move_dict[state] = []
    move_id = move_line_obj.move_id.id
    model = 'account.invoice'
    invoice_ids = searchL8(ctx, model,
                           [('move_id', '=', move_id)])
    if len(invoice_ids):
        for inv_id in invoice_ids:
            reconciles, inv_move_dict = \
                get_reconcile_from_inv(oerp,
                                       inv_id,
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
        move_id, move_line_id, mov_state = get_payment_info(oerp,
                                                            move_line_obj,
                                                            ctx)
        if mov_state:
            move_dict[mov_state].append(move_id)
    return reconcile_dict, move_dict


def get_reconcile_from_invoices(oerp, invoices, ctx):
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
                get_reconcile_from_inv(oerp,
                                       inv_id,
                                       ctx)
            reconcile_dict[inv_id] = inv_reconciles
            for state in STATES_2_DRAFT:
                if len(inv_move_dict[state]):
                    move_dict[state] = list(set(move_dict[state]) |
                                            set(inv_move_dict[state]))
    return reconcile_dict, move_dict


def upd_journals_ena_del(oerp, journals, ctx):
    """Before set invoices to draft, invoice has to set in cancelled state.
    To do this, journal has to be enabled
    @param journals: journal list to enable update_posted
    """
    if len(journals):
        vals = {}
        vals['update_posted'] = True
        try:
            msg = u"Update journals " + str(journals)
            msg_log(ctx, ctx['level'], msg)
            writeL8(ctx, 'account.journal', journals, vals)
        except BaseException:
            msg = u"Cannot update journals %s" % str(journals)
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def put_invoices_record_date(oerp, invoices, min_rec_date, ctx):
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
    invoice_obj = oerp.get(model)
    list_keys = {}
    company_id = None
    journal_id = None
    for inv_id in invoices:
        invoice = invoice_obj.browse(inv_id)
        if not company_id:
            company_id = invoice.company_id.id
        elif invoice.company_id.id != company_id:
            return None
        if not journal_id:
            journal_id = invoice.journal_id.id
        elif invoice.journal_id.id != journal_id:
            return None
        if invoice.internal_number:
            list_keys[invoice.internal_number] = inv_id
    for internal_number in sorted(list_keys):
        inv_id = list_keys[internal_number]
        vals = {}
        invoice = invoice_obj.browse(inv_id)
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
                move_lines = searchL8(ctx, 'account.move.line',
                                      [('move_id', '=', move_id)])
                for move_line_id in move_lines:
                    writeL8(ctx, 'account.move.line',
                            [move_line_id],
                            {'date': vals['registration_date']})
    return min_rec_date


def upd_invoices_2_cancel(oerp, move_dict, ctx):
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
                          'action_cancel',
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


def upd_invoices_2_draft(oerp, move_dict, ctx):
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
                          'action_cancel',
                          invoices)
            except BaseException:
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
                # msg = u"Update invoices to open %s " % invoices
                # msg_log(ctx, ctx['level'], msg)
                executeL8(ctx,
                          model,
                          'action_cancel_draft',
                          invoices)
            except BaseException:
                msg = u"Cannot update invoice status %s" % str(invoices)
                msg_log(ctx, ctx['level'], msg)
                return STS_FAILED
    return STS_SUCCESS


def upd_invoices_2_posted(oerp, move_dict, ctx):
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
                    executeL8(ctx,
                              'account.invoice',
                              'button_compute',
                              [inv_id])
                    executeL8(ctx,
                              'account.invoice',
                              'button_reset_taxes',
                              [inv_id])
                except BaseException:
                    pass
                try:
                    oerp.exec_workflow(model,
                                       'invoice_open',
                                       inv_id)
                except BaseException:
                    msg = u"Cannot restore invoice status of %d" % inv_id
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
    return sts


def upd_payments_2_draft(oerp, move_dict, ctx):
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


def upd_payments_2_posted(oerp, move_dict, ctx):
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


def upd_movements_2_draft(oerp, move_dict, ctx):
    """Set invoice and payments (header) dict to draft state.
    See upd_movements_2_posted to return in posted state
    Notice: do not pass a list (like called functions); dictionary is needed
    to recognize invoices from payments.
    @param move_dict: invoices & payments (header) dictionary keyed on state
    """
    sts = upd_payments_2_draft(oerp, move_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_invoices_2_draft(oerp, move_dict, ctx)
    return sts


def upd_movements_2_posted(oerp, move_dict, ctx):
    """Set invoice and payments (header) dict to posted state.
    See upd_movements_2_draft to set in draft state before execute this one.
    Notice: do not pass a list (like called functions); dictionary is needed
    to recognize invoices from payments.
    @param move_dict: invoices & payments (header) dictionary keyed on state
    """
    sts = upd_invoices_2_posted(oerp, move_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_payments_2_posted(oerp, move_dict, ctx)
    return sts


def unreconcile_invoices(oerp, reconcile_dict, ctx):
    for inv_id in reconcile_dict:
        # msg = u"Unreconcile invoice %d" % inv_id
        # msg_log(ctx, ctx['level'], msg)
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


def unreconcile_payments(oerp, ctx):
    msg = u"Unreconcile payments"
    msg_log(ctx, ctx['level'], msg)
    reconcile_list = searchL8(ctx, 'account.move.line',
                              [('reconcile_id', '!=', False)])
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


def reconcile_invoices(oerp, reconcile_dict, ctx):
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
            # executeL8(oerp, ctx, 'account.move.line',
            #              'reconcile',
            #              reconcile_dict[inv_id],
            #              'manual')
        except BaseException:
            msg = u"Cannot reconcile invoice of %d" % inv_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def upd_acc_2_bank(oerp, accounts, ctx):
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


def cvt_ur_ui_view(oerp, old_module, new_module, model_name, ctx):
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


def cvt_ir_model_data(oerp, old_module, new_module, model_name, ctx):
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


def set_account_type(oerp, ctx):
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
        move_line_obj = browseL8(ctx, 'account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        account_obj = move_line_obj.account_id
        valid = True
        # valid = False       # debug
        if not account_obj.parent_id:
            valid = False
        acctype_id = account_obj.user_type.id
        acctype_obj = browseL8(ctx, 'account.account.type', acctype_id)
        if acctype_obj.report_type not in ("asset", "liability",
                                           "income", "expense"):
            valid = False
        if not valid:
            account_id = account_obj.id
            if account_id not in accounts:
                accounts.append(account_id)
            if not move_line_obj.journal_id.update_posted:
                journal_id = move_line_obj.journal_id.id
                if journal_id not in journals:
                    journals.append(journal_id)
            inv_reconcile_dict, inv_move_dict = \
                get_reconcile_list_from_move_line(oerp, move_line_obj, ctx)
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
    sts = upd_journals_ena_del(oerp, journals, ctx)
    if sts == STS_SUCCESS:
        sts = unreconcile_invoices(oerp, reconcile_dict, ctx)
    if sts == STS_SUCCESS:
        sts = upd_movements_2_draft(oerp, move_dict, ctx)
    # if sts == STS_SUCCESS:
    #     sts = upd_acc_2_bank(oerp, accounts, ctx)
    raw_input('Press RET to continue')
    if sts == STS_SUCCESS:
        sts = upd_movements_2_posted(oerp, move_dict, ctx)
        if sts == STS_SUCCESS:
            for inv_id in reconcile_dict:
                reconciles = reconcile_dict[inv_id]
                new_reconciles, new_reconcile_dict = \
                    refresh_reconcile_from_inv(oerp, inv_id, reconciles, ctx)
                sts = reconcile_invoices(oerp, new_reconcile_dict, ctx)
    return sts


def recompute_tax_balance(oerp, ctx):
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
            oerp, rec_ids, ctx)
        unreconcile_invoices(oerp, reconcile_dict, ctx)
        upd_invoices_2_draft(oerp, move_dict, ctx)
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
        upd_invoices_2_posted(oerp, move_dict, ctx)
        reconciles = reconcile_dict[invoice_id]
        if len(reconciles):
            try:
                cur_reconciles, cur_reconcile_dict = \
                    refresh_reconcile_from_inv(oerp,
                                               invoice_id,
                                               reconciles,
                                               ctx)
                reconcile_invoices(oerp,
                                   cur_reconcile_dict,
                                   ctx)
            except BaseException:
                msg = u"**** Warning invoice %d ****" % invoice_id
                msg_log(ctx, ctx['level'], msg)
    return sts


def recompute_balance(oerp, ctx):
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


def append_2_where(oerp, model, code, op, value, where, ctx):
    where.append((code, op, value))
    return where


def build_where(oerp, model, hide_cid, exclusion, ctx):
    where = []
    if not hide_cid and 'company_id' in ctx:
        company_id = ctx['company_id']
        where = append_2_where(oerp,
                               model,
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
            where = append_2_where(oerp,
                                   model,
                                   code,
                                   op,
                                   value,
                                   where,
                                   ctx)
    return where


def build_exclusion(oerp, model, records2keep, ctx):
    exclusion = None
    if model in records2keep:
        if isinstance(records2keep[model], list):
            exclusion = [('id', 'not in', records2keep[model])]
        else:
            exclusion = [('id', '!=', records2keep[model])]
    return exclusion


def workflow_model_all_records(oerp, model, hide_cid, signal, ctx,
                               exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to execute workflow in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(oerp, model, hide_cid, exclusion, ctx)
    record_ids = searchL8(ctx, model, where)
    if not ctx['dry_run'] and len(record_ids) > 0:
        num_moves = len(record_ids)
        move_ctr = 0
        for record_id in record_ids:
            msg_burst(ctx['level'], "Upstate ", move_ctr, num_moves)
            move_ctr += 1
            try:
                oerp.exec_workflow(model, signal, record_id)
            except BaseException:
                msg = u"Workflow of %s.%d do not executed" % (model, record_id)
                msg_log(ctx, ctx['level'], msg)
                if ctx['exit_onerror']:
                    sts = STS_FAILED
                    break
    decr_lev(ctx)
    return sts


def setstate_model_all_records(oerp, model, hide_cid, field_name,
                               new_value, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to update status in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(oerp, model, hide_cid, exclusion, ctx)
    if validate_field(ctx, model, field_name):
        where = append_2_where(oerp,
                               model,
                               field_name,
                               '!=',
                               new_value,
                               where,
                               ctx)
    record_ids = searchL8(ctx, model, where)
    if validate_field(ctx, model, 'state') and \
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


def reactivate_model_all_records(oerp, model, hide_cid, field_name,
                                 sel_value, new_value, ctx,
                                 exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to reactivate in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(oerp, model, hide_cid, exclusion, ctx)
    if validate_field(ctx, model, field_name):
        where = append_2_where(oerp,
                               model,
                               field_name,
                               '=',
                               sel_value,
                               where,
                               ctx)
    record_ids = searchL8(ctx, model, where)
    if validate_field(ctx, model, 'state') and \
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


def deactivate_model_all_records(oerp, model, hide_cid, ctx,
                                 exclusion=None, reverse=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    if reverse is None:
        reverse = False
    if validate_field(ctx, model, 'active'):
        where = build_where(oerp, model, hide_cid, exclusion, ctx)
        if reverse:
            msg = u"Searching for records to reactivate in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(oerp,
                                   model,
                                   'active',
                                   '=',
                                   False,
                                   where,
                                   ctx)

        else:
            msg = u"Searching for records to cancel in %s" % model
            msg_log(ctx, ctx['level'], msg)
            where = append_2_where(oerp,
                                   model,
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


def remove_model_all_records(oerp, model, hide_cid, ctx, exclusion=None):
    sts = STS_SUCCESS
    incr_lev(ctx)
    msg = u"Searching for records to delete in %s" % model
    msg_log(ctx, ctx['level'], msg)
    where = build_where(oerp, model, hide_cid, exclusion, ctx)
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

        if ctx['custom_act'] == 'cscs' and model == 'project.project':
            sql = "delete from project_project where state='cancelled'"
            company_id = ctx['company_id']
            sql = sql + ' and company_id=' + str(company_id)
            cmd = PSQL % (sql, ctx['db_name'])
            os0.muteshell(cmd, simulate=False, keepout=False)
    decr_lev(ctx)
    return sts


def remove_group_records(oerp, models, records2keep, ctx, hide_cid=None,
                         special=None, specparams=None, tables2save=None):
    sts = STS_SUCCESS
    for xmodel in models:
        exclusion = build_exclusion(oerp, xmodel, records2keep, ctx)
        act = None
        if xmodel.endswith('.2') or \
                xmodel.endswith('.3') or \
                xmodel.endswith('.4') or \
                xmodel.endswith('.5'):
            model = xmodel[0:-2]
        else:
            model = xmodel
        if tables2save and model in tables2save:
            return sts
        if sts == STS_SUCCESS:
            if special and xmodel in special:
                act = special[xmodel]
                if act == 'deactivate':
                    sts = deactivate_model_all_records(oerp,
                                                       model,
                                                       hide_cid,
                                                       ctx,
                                                       exclusion=exclusion,
                                                       reverse=True)
                elif act == 'reactivate':
                    if specparams and xmodel in specparams:
                        field_name = specparams[xmodel][0]
                        sel_value = specparams[xmodel][1]
                        new_value = specparams[xmodel][2]
                        sts = reactivate_model_all_records(oerp,
                                                           model,
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
                        sts = setstate_model_all_records(oerp,
                                                         model,
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
                        sts = workflow_model_all_records(oerp,
                                                         model,
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
            where = build_where(oerp, model, hide_cid, exclusion, ctx)
            where = append_2_where(oerp,
                                   model,
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
            where = build_where(oerp, model, hide_cid, exclusion, ctx)
            record_ids = searchL8(ctx, model, where)
            if len(record_ids):
                for record_id in record_ids:
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
        if sts == STS_SUCCESS and model == 'account.move' and model == xmodel:
            unreconcile_payments(oerp, ctx)
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
            sts = remove_model_all_records(oerp, model, hide_cid, ctx,
                                           exclusion=exclusion)
        if sts == STS_SUCCESS and act == 'deactivate':
            sts = deactivate_model_all_records(oerp,
                                               model,
                                               hide_cid,
                                               ctx,
                                               exclusion=exclusion)
        if ctx.get('_cr'):
            company_id = ctx['company_id']
            if model == 'project.task.work':
                query = "delete from project_task_work"
                query += " where company_id=%d;" % company_id
                ctx['_cr'].execute(query)
    return sts


def set_server_isolated(oerp, ctx):
    """Isolate server to avoid notification mail for some events
    like remove tasks
    """
    sts = STS_SUCCESS
    if not ctx['dry_run']:
        if sts == STS_SUCCESS:
            model = 'fetchmail.server'
            sts = deactivate_model_all_records(oerp, model, True, ctx)
        if sts == STS_SUCCESS:
            model = 'ir.mail_server'
            sts = deactivate_model_all_records(oerp, model, True, ctx)
        if sts == STS_SUCCESS:
            model = 'mail.followers'
            sts = remove_model_all_records(oerp, model, True, ctx)
    return sts


def reset_sequence(oerp, ctx):
    sts = STS_SUCCESS
    incr_lev(ctx)
    model = 'ir.sequence'
    msg = u"Reset sequence %s" % model
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        exclusion = [('company_id', '!=', 1)]
        remove_model_all_records(oerp, model, True, ctx, exclusion=exclusion)
    record_ids = searchL8(ctx, model, [])
    if not ctx['dry_run']:
        for record_id in record_ids:
            obj = browseL8(ctx, model, record_id)
            f_deleted = False
            if ctx['custom_act'] == 'cscs':
                for i in (2014, 2015, 2016, 2017, 2018):
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


def reset_menuitem(oerp, ctx):
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


def validate_models(oerp, ctx, models):
    cur_models = []
    for model in models:
        if searchL8(ctx, 'ir.model', [('model', '=', model)]):
            cur_models.append(model)
    return cur_models


def remove_company_mail_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('ir.attachment',))
    records2keep = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False)
    return sts


def remove_all_mail_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('mail.message',
                                         'mail.mail',
                                         'mail.notification',
                                         'mail.alias',
                                         ))
    records2keep = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True)
    return sts


def remove_all_note_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('note.stage',
                                         'note.note',
                                         'document.page',
                                         ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'note.stage': 8}
    else:
        records2keep = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True)
    return sts


def remove_company_crm_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('crm.lead',
                                         'crm.helpdesk',
                                         'crm.phonecall',
                                         ))
    records2keep = {}
    special = {'crm.lead': 'deactivate'}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False, special=special)
    return sts


def remove_all_crm_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('crm.meeting',
                                         'calendar.event',
                                         'calendar.todo',
                                         ))
    records2keep = {}
    special = {'crm.lead': 'deactivate'}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False, special=special)

    return sts


def remove_company_purchases_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('procurement.order',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_purchases_records(oerp, ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_sales_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('sale.order',
                                         'sale.shop',
                                         ))
    records2keep = {'sale.shop': 1}
    special = {'sale.order': 'set_state',
               }
    specparams = {'sale.order': ('state', 'cancel'),
                  }
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_sales_records(oerp, ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_logistic_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('stock.picking.out',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams,
                               tables2save=tables2save)
    return sts


def remove_all_logistic_records(oerp, ctx):
    sts = STS_SUCCESS
    return sts


def remove_company_project_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('project.task.work',
                                         'project.task',
                                         'project.project.2',
                                         'project.project',
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
        records2keep['project.project'] = (260, 265, 2869, 3026,
                                           3027, 3028, 3029, 3030,
                                           3031, 3032, 3033, 3034,
                                           3035, 3036, 3037, 3038,
                                           3039, 3040, 3187, 3361,
                                           3504, 3664, 3932)
    if ctx['oe_version'] == '7.0:':
        special = {'project.task': 'set_state',
                   'project.project.2': 'reactivate',
                   'project.project': 'set_state',
                   }
        specparams = {'project.task': ('state', 'cancelled'),
                      'project.project.2': ('state', 'close', 'set_open'),
                      'project.project': ('state', 'cancelled')
                      }
    else:
        special = {'project.project.2': 'reactivate',
                   'project.project': 'set_state',
                   }
        specparams = {'project.project.2': ('state', 'close', 'set_open'),
                      'project.project': ('state', 'cancelled')
                      }
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_project_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('survey.page',
                                         'survey.request',
                                         'survey',
                                         'project.phase'
                                         ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_marketing_records(oerp, ctx):
    sts = STS_SUCCESS
    return sts


def remove_all_marketing_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('marketing.campaign.workitem',
                                         'marketing.campaign.segment',
                                         'marketing.campaign',
                                         'booking.resource',
                                         'campaign.analysis',
                                         ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_hr_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('hr.expense.expense.2',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_hr_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('hr_timesheet_sheet.sheet.account',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_product_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('product.template',
                                         ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_product_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('product.category',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=True,
                               special=special,
                               specparams=specparams,
                               tables2save=tables2save)
    return sts


def remove_company_partner_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('res.partner.bank',
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
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_analytics_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('account.analytic.account',
                                         'account.analytic.journal',
                                         ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'account.analytic.account': (48, 3932)}
    else:
        records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_partner_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('res.partner.category',
                                         'res.partner'
                                         ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'res.partner': (1, 3, 4, 5, 33890, 33523, 33783)}
    else:
        records2keep = {'res.partner': 1}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_all_user_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('ir.default',
                                         'res.users',
                                         ))
    if ctx['custom_act'] == 'cscs':
        records2keep = {'res.users': (1, 4, 95)}
    else:
        records2keep = {'res.users': 1}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def remove_company_account_records(oerp, ctx):
    sts = STS_SUCCESS
    if not ctx['dry_run']:
        company_id = ctx['company_id']
        if sts == STS_SUCCESS:
            model = 'account.invoice'
            msg = u"Searching for invoices to delete"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id),
                                   '|',
                                   ('state', '=', 'paid'),
                                   ('state', '=', 'open')])
            reconcile_dict, move_dict = get_reconcile_from_invoices(oerp,
                                                                    record_ids,
                                                                    ctx)
            sts = unreconcile_invoices(oerp, reconcile_dict, ctx)
        if sts == STS_SUCCESS:
            msg = u"Setting invoices to cancel state"
            msg_log(ctx, ctx['level'], msg)
            record_ids = searchL8(ctx, model,
                                  [('company_id', '=', company_id)])
            if len(record_ids) > 0:
                try:
                    sts = upd_invoices_2_cancel(oerp, record_ids, ctx)
                except BaseException:
                    msg = u"Cannot delete invoices"
                    msg_log(ctx, ctx['level'], msg)
                    sts = STS_FAILED
    if sts == STS_SUCCESS:
        company_id = ctx['company_id']
        models = validate_models(oerp, ctx,
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
                                  'account.fiscal.position',
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
        special = {'account.invoice': 'set_state',
                   'account.move': 'set_state',
                   'account.voucher': 'set_state',
                   'account.journal': 'deactivate',
                   'account.tax': 'deactivate',
                   }
        specparams = {'account.invoice': ('internal_number', ''),
                      'account.move': ('state', 'cancel'),
                      'account.voucher': ('state', 'cancel'),
                      }
        sts = remove_group_records(oerp, models, records2keep, ctx,
                                   hide_cid=False,
                                   special=special,
                                   specparams=specparams)
    return sts


def remove_all_account_records(oerp, ctx):
    models = validate_models(oerp, ctx, ('payment.line',
                                         ))
    records2keep = {}
    special = {}
    specparams = {}
    sts = remove_group_records(oerp, models, records2keep, ctx,
                               hide_cid=False,
                               special=special,
                               specparams=specparams)
    return sts


def analyze_invoices(oerp, ctx, inv_type):
    company_id = ctx['company_id']
    period_ids = searchL8(ctx, 'account.period',
                          [('company_id', '=', company_id),
                           ('date_start', '>=', ctx['date_start']),
                           ('date_stop', '<=', ctx['date_stop'])])
    model = 'account.invoice'
    account_invoice_ids = searchL8(ctx, model,
                                   [('company_id', '=', company_id),
                                    ('period_id', 'in', period_ids),
                                    ('type', '=', inv_type),
                                    ('internal_number', '!=', '')],
                                   order='internal_number')
    num_invs = len(account_invoice_ids)
    last_number = ''
    inv_ctr = 0
    last_seq = 0
    for account_invoice_id in account_invoice_ids:
        account_invoice_obj = browseL8(ctx, model,
                                       account_invoice_id)
        inv_ctr += 1
        msg_burst(4,
                  "Invoice " + account_invoice_obj.internal_number + "      ",
                  inv_ctr, num_invs)
        # vals = {}
        if last_number[:-4] != account_invoice_obj.internal_number[0:-4]:
            last_number = ''
        if last_number == '':
            last_number = account_invoice_obj.internal_number
            last_rec_date = datetime.strptime(ctx['date_start'],
                                              "%Y-%m-%d").date()
            last_seq = 0
        last_seq += 1
        if str.isdigit(account_invoice_obj.internal_number[-4:]) and \
                int(account_invoice_obj.internal_number[-4:]) != last_seq:
            msg = u"In {0} invalid number sequence {1}".format(
                account_invoice_id,
                account_invoice_obj.internal_number)
            msg_log(ctx, ctx['level'] + 1, msg)
            last_seq = int(account_invoice_obj.internal_number[-4:])
        last_rec_date = put_invoices_record_date(oerp,
                                                 [account_invoice_id],
                                                 last_rec_date,
                                                 ctx)
        # date_invoice = account_invoice_obj.date_invoice
        # registration_date = account_invoice_obj.registration_date
        # if not date_invoice:
        #     vals['date_invoice'] = str(last_rec_date)
        #     date_invoice = last_rec_date
        # # if not registration_date:
        # vals['registration_date'] = str(date_invoice)
        # registration_date = date_invoice
        # if inv_type == 'out_invoice' and\
        #        registration_date != date_invoice:
        #     msg = u"In {0} invalid registration date {1}".format(
        #         account_invoice_id,
        #         str(account_invoice_obj.registration_date))
        #     msg_log(ctx, ctx['level'] + 1, msg)
        #     vals['registration_date'] = str(date_invoice)
        #     registration_date = date_invoice
        # elif registration_date < last_rec_date:
        #     msg = u"In {0} invalid registration date {1}".format(
        #         account_invoice_id,
        #         str(account_invoice_obj.registration_date))
        #     msg_log(ctx, ctx['level'] + 1, msg)
        #     vals['registration_date'] = str(last_rec_date)
        #     registration_date = last_rec_date
        # if len(vals):
        #     period_ids = executeL8(oerp, ctx, 'account.period',
        #                               'find',
        #                               registration_date)
        #     period_id = period_ids and period_ids[0] or False
        #     vals['period_id'] = period_id
        #     try:
        #         writeL8(model, account_invoice_id, vals)
        #     except:
        #         msg = u"Cannot update registration date"
        #         msg_log(ctx, ctx['level'], msg)
        # last_rec_date = registration_date
        last_number = account_invoice_obj.internal_number
    return STS_SUCCESS


#############################################################################
# Private actions
#
def multiuser(ctx, actions):
    if "per_user" in actions:
        return True
    else:
        return False


def create_zero_db(oerp, ctx):
    lgiuser = do_login(oerp, ctx)
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
            actv[-4:] in ('_6.1', '_7.0', '_8.0', '_9.0', '_10.0', '_11.0'):
        if actv[-3:] == ctx['oe_version']:
            act = actv[0:-4]
        else:
            act = 'unit_test'
    else:
        act = actv
    return act


def import_file(oerp, ctx, o_model, csv_fn):
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
    if 'company_id' in ctx:
        company_id = ctx['company_id']
    csv.register_dialect('odoo',
                         delimiter=',',
                         quotechar='\"',
                         quoting=csv.QUOTE_MINIMAL)
    csv_ffn = ctx['data_path'] + "/" + csv_fn
    if csv_ffn[-4:] == '.csv':
        ver_csv = '%s_%s%s' % (csv_ffn[0:-4], ctx['oe_version'], csv_ffn[-4:])
    if os.path.isfile(ver_csv):
        csv_ffn = ver_csv
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
                o_model = import_file_get_hdr(oerp,
                                              ctx,
                                              o_model,
                                              csv_obj,
                                              csv_fn,
                                              row)
                msg = u"Model={0}, Code={1} Name={2} NoCompany={3}"\
                    .format(o_model['model'],
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
            # Data for specific db type (i.e. just for test)
            if o_model.get('db_type', ''):
                if row[o_model['db_type']]:
                    if row[o_model['db_type']].find(ctx['db_type']) < 0:
                        msg = u"Record not imported by invalid db_type"
                        debug_msg_log(ctx, ctx['level'] + 2, msg)
                        continue
            # Does record exist ?
            if o_model['code'] == 'id' and row['id']:
                o_model['saved_hide_id'] = o_model['hide_id']
                o_model['hide_id'] = False
                ids = get_query_id(oerp,
                                   ctx,
                                   o_model,
                                   row)
                o_model['hide_id'] = o_model['saved_hide_id']
            else:
                ids = get_query_id(oerp,
                                   ctx,
                                   o_model,
                                   row)
            name_new = ""
            update_header_id = True
            vals = {}
            for n in row:
                if isinstance(row[n], basestring) and \
                        row[n].find('${header_id}') >= 0:
                    update_header_id = False
                val = eval_value(oerp,
                                 ctx,
                                 o_model,
                                 n,
                                 row[n])
                if val is not None:
                    x = n.split('/')[0]
                    if x != 'fiscalcode' or val != '':
                        vals[x] = tounicode(val)
                msg = u"{0}={1}".format(n, tounicode(val))
                debug_msg_log(ctx, ctx['level'] + 2, msg)
                if n == o_model['name']:
                    name_new = val
            if 'company_id' in ctx and 'company_id' in vals:
                if int(vals['company_id']) != company_id:
                    continue
            if 'id' in vals:
                del vals['id']
            if len(ids):
                id = ids[0]
                if update_header_id:
                    ctx['header_id'] = id
                cur_obj = browseL8(ctx, o_model['model'], id)
                name_old = cur_obj[o_model['name']]
                msg = u"Update " + str(id) + " " + name_old
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['heavy_trx']:
                    v = {}
                    for p in vals:
                        if p != "db_type":
                            # if isinstance(cur_obj[p], (int, long, float)) and \
                            #         vals[p].isdigit():
                            #     vals[p] = eval(vals[p])
                            if vals[p] != cur_obj[p]:
                                v[p] = vals[p]
                    vals = v
                    del v
                if not ctx['dry_run'] and len(vals):
                    try:
                        writeL8(ctx, o_model['model'], ids, vals)
                        msg = u"id={0}, {1}={2}->{3}".\
                              format(cur_obj.id,
                                     tounicode(o_model['name']),
                                     tounicode(name_old),
                                     tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                    except BaseException:
                        os0.wlog(u"!!write error!")
            else:
                msg = u"insert " + os0.u(name_new)
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['dry_run']:
                    if not o_model.get('hide_cid', False):
                        vals['company_id'] = ctx['company_id']
                    try:
                        id = createL8(ctx, o_model['model'], vals)
                        if update_header_id:
                            ctx['header_id'] = id
                        msg = u"creat id={0}, {1}={2}"\
                              .format(id,
                                      tounicode(o_model['name']),
                                      tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                    except BaseException:
                        id = None
                        os0.wlog(u"!!write error!")
                else:
                    ctx['header_id'] = -1
        csv_fd.close()
    else:
        msg = u"Import file " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def import_config_file(oerp, ctx, csv_fn):
    csv.register_dialect('odoo',
                         delimiter=',',
                         quotechar='\"',
                         quoting=csv.QUOTE_MINIMAL)
    csv_ffn = ctx['data_path'] + "/" + csv_fn
    if csv_ffn[-4:] == '.csv':
        ver_csv = '%s_%s%s' % (csv_ffn[0:-4], ctx['oe_version'], csv_ffn[-4:])
    if os.path.isfile(ver_csv):
        csv_ffn = ver_csv
    if os.path.isfile(csv_ffn):
        csv_fd = open(csv_ffn, 'rb')
        hdr_read = False
        csv_obj = csv.DictReader(csv_fd,
                                 fieldnames=[],
                                 restkey='undef_name',
                                 dialect='odoo')
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
                if file_valid:
                    continue
                else:
                    msg = u"!Invalid header of " + csv_fn
                    msg = msg + u" Should be: user,name,value"
                    msg_log(ctx, ctx['level'] + 1, msg)
                    return STS_FAILED
            user = eval_value(oerp,
                              ctx,
                              None,
                              None,
                              row['user'])
            name = eval_value(oerp,
                              ctx,
                              None,
                              None,
                              row['name'])
            value = eval_value(oerp,
                               ctx,
                               None,
                               None,
                               row['value'])
            sts = setup_config_param(oerp, ctx, user, name, value)
            if sts != STS_SUCCESS:
                break
        csv_fd.close()
    else:
        msg = u"!File " + csv_fn + " not found!"
        msg_log(ctx, ctx['level'] + 1, msg)
        return STS_FAILED
    return STS_SUCCESS


def setup_config_param(oerp, ctx, user, name, value):
    context = get_context(ctx)
    sts = STS_SUCCESS
    v = os0.str2bool(value, None)
    if v is not None:
        value = v
    if isinstance(value, bool):
        group_ids = searchL8(ctx, 'res.groups',
                             [('name', '=', name)],
                             context=context)
    else:
        full_name = '%s / %s' % (name, value)
        group_ids = searchL8(ctx, 'res.groups',
                             [('full_name', '=', full_name)],
                             context=context)
        if len(group_ids) == 0 and value == 'See all Leads':
            value = 'User: All Leads'
            full_name = '%s / %s' % (name, value)
            group_ids = searchL8(ctx, 'res.groups',
                                 [('full_name', '=', full_name)],
                                 context=context)
    if len(group_ids) != 1:
        msg = u"!Parameter name " + name + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    group_id = group_ids[0]
    user_id = searchL8(ctx, 'res.users',
                       [('login', '=', user)])
    if len(user_id) != 1:
        msg = u"!User " + user + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    user_obj = browseL8(ctx, 'res.users', user_id[0])
    if not user_obj:
        msg = u"!User " + user + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    vals = {}
    if value:
        if group_id not in user_obj.groups_id.ids:
            vals['groups_id'] = [(4, group_id)]
            if isinstance(value, bool):
                msg = u"%s.%s = True" % (user, name)
            else:
                msg = u"%s.%s" % (user, full_name)
            msg_log(ctx, ctx['level'] + 2, msg)
    else:
        if group_id in user_obj.groups_id.ids:
            vals['groups_id'] = [(3, group_id)]
            msg = u"%s.%s = False" % (user, name)
            msg_log(ctx, ctx['level'] + 2, msg)
    if not ctx['dry_run'] and len(vals):
        writeL8(ctx, 'res.users', user_id, vals)
        # ids = searchL8(ctx, 'ir.module.category',
        #                   [('name', '=', category)])
        # if len(ids):
        #     mod_cat_id = ids[0]
        #     if ctx_name is not None:
        #         ctx_sel_ids = searchL8(ctx, 'res.groups',
        #                                   [('category_id', '=', mod_cat_id),
        #                                    ('name', '=', ctx_name)])
        #         ctx_label = "." + ctx_name
        #     else:
        #         ctx_sel_ids = searchL8(ctx, 'res.groups',
        #                                   [('category_id', '=', mod_cat_id)])
        #         ctx_label = ""
        #     ctx_sel_name = {}
        #     for id in sorted(ctx_sel_ids):
        #         cur_obj = browseL8(ctx, 'res.groups', id)
        #         ctx_sel_name[cur_obj.name] = id
        #     if len(ctx_sel_ids) > 1:
        #         if value in ctx_sel_name:
        #             msg = u"Param (" + category + ctx_label + \
        #                 ") = " + value + "(" + str(ctx_sel_name[value]) + ")"
        #         else:
        #             msg = u"!Param (" + category + ctx_label + \
        #                 ") value " + value + " not valid!"
        #             w = "("
        #             for x in ctx_sel_name.keys():
        #                 msg = msg + w + x
        #                 w = ","
        #             msg = msg + ")"
        #         msg_log(ctx, ctx['level'] + 2, msg)
        #     elif len(ctx_sel_ids) == 1:
        #         if os0.str2bool(value, False):
        #             msg = u"!Param " + category + ctx_label + " = True"
        #         else:
        #             msg = u"!Param " + category + ctx_label + " = False"
        #         msg_log(ctx, ctx['level'] + 2, msg)
        #     else:
        #         msg = u"!Param " + category + ctx_label + " not found!"
        #         msg_log(ctx, ctx['level'] + 2, msg)
        # else:
    return sts


def install_chart_of_account(oerp, ctx, name):
    sts = STS_SUCCESS
    context = get_context(ctx)
    chart_setup_model = 'wizard.multi.charts.accounts'
    chart_template_id = searchL8(ctx, 'account.chart.template',
                                 [('name', '=', name)],
                                 context=context)
    if len(chart_template_id) == 0:
        msg = u"!Invalid chart of account " + name + "!!"
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
    ctx['_today'] = str(date.today())
    ctx['_current_year'] = str(date.today().year)
    ctx['_last_year'] = str(date.today().year - 1)
    if ctx.get('do_sel_action', False):
        ctx['actions'] = ctx['do_sel_action']
    elif not ctx.get('actions', None):
        if ctx.get('actions_db', None):
            ctx['actions'] = 'per_db,' + ctx['actions_db']
            del ctx['actions_db']
        elif ctx.get('actions_mc', None):
            ctx['actions'] = 'per_company,' + ctx['actions_mc']
            del ctx['actions_mc']
        elif ctx.get('actions_uu', None):
            ctx['actions'] = 'per_users,' + ctx['actions_uu']
            del ctx['actions_uu']
    init_logger(ctx)
    print_hdr_msg(ctx)
    if not check_4_actions(ctx):
        return STS_FAILED
    ctx = create_act_list(ctx)
    do_conn = False
    do_newdb = False
    do_multidb = False
    for act in ctx['actions'].split(','):
        if act not in ("list_actions", "show_params"):
            do_conn = True
        if act == "per_db":
            do_multidb = True
        if act == "new_db":
            do_newdb = True
    if do_conn:
        oerp = open_connection(ctx)
    else:
        oerp = None
    ctx['multi_user'] = multiuser(ctx,
                                  ctx['actions'].split(','))
    if do_newdb:
        if ctx.get('multi_db', False):
            ctx['db_name'] = ctx['dbfilter']
        if not ctx['db_name']:
            msg = u"!No DB name supplied!!"
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    elif do_conn and ctx.get('multi_db', False) and not do_multidb:
        ctx['actions'] = 'per_db,' + ctx['actions']
        do_multidb = True
    if not do_newdb and do_conn and not do_multidb and ctx['db_name']:
        ctx = init_db_ctx(oerp, ctx, ctx['db_name'])
        msg = ident_db(oerp, ctx, ctx['db_name'])
        msg_log(ctx, ctx['level'], msg)
        lgiuser = do_login(oerp, ctx)
        if lgiuser:
            sts = do_actions(oerp, ctx)
        else:
            sts = STS_FAILED
    else:
        sts = do_actions(oerp, ctx)
    decr_lev(ctx)
    if sts == STS_SUCCESS:
        msg = u"------ Operations ended ------"
    else:
        msg = u"###??? Last operation FAILED!!! ###???"
    msg_log(ctx, ctx['level'], msg)
    return sts


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
