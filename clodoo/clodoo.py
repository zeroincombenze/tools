#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
    Massive operations on Zeroincombenze(R) / Odoo databases

"""

# import pdb
import os.path
import sys
from os0 import os0
import time
from datetime import datetime
import oerplib
import re
import csv
from clodoolib import parse_args
from clodoolib import init_logger
from clodoolib import msg_log
from clodoolib import debug_msg_log
from clodoolib import msg_burst
from clodoolib import tounicode
from clodoolib import crypt
from clodoolib import decrypt
from clodoocore import import_file_get_hdr
from clodoocore import eval_value
from clodoocore import get_query_id

__version__ = "0.2.69.21"
# Apply for configuration file (True/False)
APPLY_CONF = True
STS_FAILED = 1
STS_SUCCESS = 0

PAY_MOVE_STS_2_DRAFT = ('posted', )
INVOICES_STS_2_DRAFT = ('open', 'paid')
STATES_2_DRAFT = ('open', 'paid', 'posted')

db_msg_sp = 0
db_msg_stack = []


def version():
    return __version__


def print_hdr_msg(ctx):
    ctx['level'] = 0
    msg = u"Do massive operations V" + __version__
    msg_log(ctx, ctx['level'], msg)
    incr_lev(ctx)
    msg = u"Configuration from " + ctx.get('conf_fn', '')
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
    try:
        oerp = oerplib.OERP(server=ctx['db_host'],
                            protocol=ctx['svc_protocol'],
                            port=ctx['xmlrpc_port'],
                            version=ctx['oe_version'])
    except:
        msg = u"!Odoo server is not running!"
        msg_log(ctx, ctx['level'], msg)
        raise ValueError(msg)
    return oerp


def do_login(oerp, ctx):
    """Do a login into DB; try using more usernames and passwords"""
    msg = "do_login()"
    debug_msg_log(ctx, ctx['level'] + 1, msg)
    userlist = ctx['login2_user'].split(',')
    userlist.insert(0, ctx['login_user'])
    if ctx['lgi_user']:
        userlist.insert(0, ctx['lgi_user'])
    pwdlist = ctx['login2_password'].split(',')
    pwdlist.insert(0, ctx['login_password'])
    if ctx['lgi_pwd']:
        pwdlist.insert(0, ctx['lgi_pwd'])
    user_obj = False
    db_name = get_dbname(ctx, 'login')
    for username in userlist:
        for pwd in pwdlist:
            try:
                user_obj = oerp.login(user=username,
                                      passwd=decrypt(pwd),
                                      database=db_name)
                break
            except:
                user_obj = False
            try:
                user_obj = oerp.login(user=username,
                                      passwd=pwd,
                                      database=db_name)
                break
            except:
                user_obj = False
        if user_obj:
            break
    if not user_obj:
        if not ctx.get('no_warning_pwd', False):
            os0.wlog(u"!DB={0}: invalid user/pwd"
                     .format(tounicode(ctx['db_name'])))
        return
    if not ctx['multi_user']:
        ctx = init_user_ctx(oerp, ctx, user_obj.id)
        msg = ident_user(oerp, ctx, user_obj.id)
        msg_log(ctx, ctx['level'], msg)
    if ctx['set_passepartout']:
        wrong = False
        if username != ctx['login_user']:
            user_obj.login = ctx['login_user']
            wrong = True
        if pwd != ctx['login_password']:
            user_obj.password = decrypt(ctx['login_password'])
            wrong = True
        if wrong:
            try:
                oerp.write_record(user_obj)
                if not ctx.get('no_warning_pwd', False):
                    os0.wlog(u"!DB={0}: updated wrong user/pwd {1} to {2}"
                             .format(tounicode(ctx['db_name']),
                                     tounicode(username),
                                     tounicode(ctx['login_user'])))
            except:
                os0.wlog(u"!!write error!")
        if user_obj.email != ctx['zeroadm_mail']:
            user_obj.email = ctx['zeroadm_mail']
            try:
                oerp.write_record(user_obj)
                if not ctx.get('no_warning_pwd', False):
                    os0.wlog(u"!DB={0}: updated wrong user {1} to {2}"
                             .format(tounicode(ctx['db_name']),
                                     tounicode(ctx['login2_user']),
                                     tounicode(ctx['login_user'])))
            except:
                os0.wlog(u"!!write error!")
    return user_obj


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
    company_obj = oerp.browse('res.company', c_id)
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


def init_user_ctx(oerp, ctx, u_id):
    ctx['user_id'] = u_id
    user_obj = oerp.browse('res.users', u_id)
    ctx['user_partner_id'] = user_obj.partner_id
    ctx['user_name'] = user_obj.partner_id.name
    ctx['user_company_id'] = user_obj.company_id.id
    if user_obj.partner_id.country_id:
        ctx['user_country_id'] = user_obj.partner_id.country_id.id
    else:
        ctx['user_country_id'] = 0
    if ctx.get('def_company_id', 0) == 0:
        ctx['def_company_id'] = ctx['user_company_id']
        ctx['def_company_name'] = user_obj.company_id.name
    if ctx.get('def_country_id', 0) == 0 and \
            user_obj.company_id.country_id:
        ctx['def_country_id'] = user_obj.company_id.country_id.id
    return ctx


def get_dblist(oerp):
    return oerp.db.list()


def get_companylist(oerp):
    return oerp.search('res.company')


def get_userlist(oerp):
    return oerp.search('res.users')


#############################################################################
# Action interface
#
def isaction(oerp, ctx, action):
    """Return true if valid action"""
    lx_act = ctx['_lx_act']
    if action == '' or action is False or action is None:
        return True
    elif action in lx_act:
        return True
    else:
        return False


def isiteraction(oerp, ctx, action):
    """Return true if interable action"""
    if action == 'per_db' or \
            action == 'per_company' or \
            action == 'per_user':
        return True
    else:
        return False


def lexec_name(action):
    """Return local executable function name from action"""
    act = "act_" + action
    return act


def add_on_account(acc_balance, level, code, credit, debit):
    if level not in acc_balance:
        acc_balance[level] = {}
    if code:
        if code in acc_balance[level]:
            acc_balance[level][code] += credit
            acc_balance[level][code] -= debit
        else:
            acc_balance[level][code] = credit
            acc_balance[level][code] -= debit


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
    if conf_obj.has_option(action, 'actions'):
        # Local environment for group actions
        lctx = create_local_parms(ctx, action)
        if not lctx['actions']:
            return STS_FAILED
        incr_lev(ctx)
        actions = lctx['actions'].split(',')
        for act in actions:
            if isaction(oerp, lctx, act):
                if act == '' or act is False or act is None:
                    break
                elif act == action:
                    msg = u"Recursive actions " + act
                    msg_log(ctx, ctx['level'] + 1, msg)
                    sts = STS_FAILED
                    break
                sts = do_single_action(oerp, lctx, act)
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
    if isaction(oerp, ctx, action):
        if action == '' or action is False or action is None:
            return STS_SUCCESS
        if ctx['db_name'] == 'auto':
            if action not in ("list_actions", "show_params", "new_db"):
                ctx['db_name'] = get_dbname(ctx, action)
                lgiuser = do_login(oerp, ctx)
                if not lgiuser:
                    action = "unit_test"
        act = lexec_name(action)
        if act in list(globals()):
            if action == 'install_modules' and\
                    not ctx.get('module_udpated', False):
                globals()[lexec_name('update_modules')](oerp, ctx)
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
        if isaction(oerp, ctx, act):
            if isiteraction(oerp, ctx, act):
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


def create_local_parms(ctx, action):
    """Create local params dictionary"""
    conf_obj = ctx['_conf_obj']
    lctx = {}
    for n in ctx:
        lctx[n] = ctx[n]
    for p in ('actions',
              'install_modules',
              'uninstall_modules',
              'upgrade_modules'):
        if conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        else:
            lctx[p] = False
    for p in ('model',
              'model_code',
              'model_name',
              'code',
              'name',
              'filename',
              'hide_cid'):
        if conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
        elif p in lctx:
            del lctx[p]
    for p in ('lang',
              'dbfilter',
              'companyfilter',
              'userfilter',
              'chart_of_account'):
        if conf_obj.has_option(action, p):
            lctx[p] = conf_obj.get(action, p)
    for p in ('install_modules',
              'uninstall_modules',
              'actions',
              'hide_cid'):
        if p in lctx:
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
    user_obj = oerp.browse('res.users', u_id)
    msg = u"User {0:>2} {1}\t'{2}'\t{3}\t[{4}]".format(
          u_id,
          tounicode(user_obj.login),
          tounicode(ctx['user_name']),
          tounicode(user_obj.partner_id.email),
          tounicode(user_obj.company_id.name))
    return msg


#############################################################################
# Public actions
#
def act_list_actions(oerp, ctx):
    for act in sorted(ctx['_lx_act']):
        print "- %s" % act
    return STS_SUCCESS


def act_show_params(oerp, ctx):
    pwd = raw_input('password ')
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
    company_ids = get_companylist(oerp)
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
    user_ids = get_userlist(oerp)
    for u_id in user_ids:
        ctx = init_user_ctx(oerp, ctx, u_id)
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
        sts = oerp.execute('ir.actions.server',
                           'Run Unit test',
                           'banking_export_pain')
    except:
        sts = STS_FAILED
    return sts


def act_drop_db(oerp, ctx):
    """Drop a DB"""
    sts = STS_SUCCESS
    msg = "Drop DB %s" % ctx['db_name']
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        try:
            oerp.db.drop(ctx['admin_passwd'],
                         ctx['db_name'])
            time.sleep(3)
        except:
            pass
    return sts


def act_new_db(oerp, ctx):
    """Create new DB"""
    sts = STS_SUCCESS
    lang = ctx.get('lang', 'en_US')
    msg = "Create DB %s [%s]" % (ctx['db_name'], lang)
    msg_log(ctx, ctx['level'], msg)
    if not ctx['dry_run']:
        if ctx['db_name'] == 'auto':
            ctx['db_name'] = create_zero_db(oerp, ctx)
            msg = "Assigned name is %s" % (ctx['db_name'])
            msg_log(ctx, ctx['level'], msg)
        if ctx['db_name']:
            try:
                oerp.db.create_and_wait(ctx['admin_passwd'],
                                        ctx['db_name'],
                                        False,
                                        lang,
                                        decrypt(ctx['login_password']))
                ctx['no_warning_pwd'] = True
                lgiuser = do_login(oerp, ctx)
                if not lgiuser:
                    sts = STS_FAILED
            except:
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
    company_ids = get_companylist(oerp)
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for c_id in company_ids:
        company_obj = oerp.browse('res.company', c_id)
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
    user_ids = get_userlist(oerp)
    saved_actions = ctx['actions']
    sts = STS_SUCCESS
    for u_id in user_ids:
        user_obj = oerp.browse('res.users', u_id)
        if re.match(ctx['userfilter'], user_obj.name):
            ctx = init_user_ctx(oerp, ctx, u_id)
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
        oerp.execute('base.module.update',
                     "update_module",
                     [])
    return STS_SUCCESS


def act_upgrade_modules(oerp, ctx):
    """Upgrade module from list"""
    msg = u"Upgrade modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = ctx['upgrade_modules'].split(',')
    context = get_context(ctx)
    done = 0
    for m in module_list:
        if m == "":
            continue
        ids = oerp.search('ir.module.module',
                          [('name', '=', m),
                           ('state', '=', 'installed')],
                          context=context)
        if not ctx['dry_run']:
            if len(ids):
                try:
                    oerp.execute('ir.module.module',
                                 "button_immediate_upgrade",
                                 ids)
                    msg = "name={0}".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    done += 1
                except:
                    msg = "!Module {0} not upgradable!".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
            else:
                msg = "Module {0} not installed!".format(m)
                msg_log(ctx, ctx['level'] + 1, msg)
        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)

    if done > 0:
        time.sleep(done)
    return STS_SUCCESS


def act_uninstall_modules(oerp, ctx):
    """Uninstall module from list"""
    msg = u"Uninstall unuseful modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = ctx['uninstall_modules'].split(',')
    context = get_context(ctx)
    done = 0
    for m in module_list:
        if m == "":
            continue
        ids = oerp.search('ir.module.module',
                          [('name', '=', m),
                           ('state', '=', 'installed')],
                          context=context)
        if not ctx['dry_run']:
            if len(ids):
                if m != 'l10n_it_base':  # debug
                    try:
                        oerp.execute('ir.module.module',
                                     "button_immediate_uninstall",
                                     ids)
                        msg = "name={0}".format(m)
                        msg_log(ctx, ctx['level'] + 1, msg)
                        done += 1
                    except:
                        msg = "!Module {0} not uninstallable!".format(m)
                        msg_log(ctx, ctx['level'] + 1, msg)
            else:
                msg = "Module {0} already uninstalled!".format(m)
                msg_log(ctx, ctx['level'] + 1, msg)

            ids = oerp.search('ir.module.module',
                              [('name', '=', m),
                               ('state', '=', 'uninstalled')],
                              context=context)
            if len(ids):
                module_obj = oerp.browse('ir.module.module', ids[0])
                oerp.unlink_record(module_obj)

        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)

    if done > 0:
        time.sleep(done)
    return STS_SUCCESS


def act_install_modules(oerp, ctx):
    """Install modules from list"""
    msg = u"Install modules"
    msg_log(ctx, ctx['level'], msg)
    module_list = ctx['install_modules'].split(',')
    context = get_context(ctx)
    done = 0
    for m in module_list:
        if m == "":
            continue
        ids = oerp.search('ir.module.module',
                          [('name', '=', m),
                           ('state', '=', 'uninstalled')],
                          context=context)
        if not ctx['dry_run']:
            if len(ids):
                try:
                    oerp.execute('ir.module.module',
                                 "button_immediate_install",
                                 ids)
                    msg = "name={0}".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
                    done += 1
                except:
                    msg = "!Module {0} not installable!".format(m)
                    msg_log(ctx, ctx['level'] + 1, msg)
            else:
                ids = oerp.search('ir.module.module',
                                  [('name', '=', m)],
                                  context=context)
                if len(ids):
                    msg = "Module {0} already installed!".format(m)
                else:
                    msg = "!Module {0} does not exist!".format(m)
                msg_log(ctx, ctx['level'] + 1, msg)
        else:
            msg = "name({0})".format(m)
            msg_log(False, ctx['level'] + 1, msg)

    if done > 0:
        time.sleep(done)
    return STS_SUCCESS


def act_install_language(oerp, ctx):
    """Install new language"""
    lang = ctx.get('lang', 'en_US')
    msg = u"Install language %s" % lang
    msg_log(ctx, ctx['level'], msg)
    if lang != 'en_US':
        vals = {}
        vals['lang'] = lang
        vals['overwrite'] = False
        id = oerp.create('base.language.install',
                         vals)
        oerp.execute('base.language.install',
                     'lang_install',
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
    partner_ids = oerp.search('res.partner',
                              [('company_id', '=', company_id)])
    rec_ctr = 0
    for partner_id in partner_ids:
        try:
            partner_obj = oerp.browse('res.partner', partner_id)
        except:
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
                    oerp.write('res.partner', partner_id, vals)
                except:
                    msg = partner_obj.name + " WRONG VAT"
                    msg_log(ctx, ctx['level'], msg)
            elif iso == "1I" and len(vatn) == 11:
                iso = 'IT'
                vals = {}
                vals['vat'] = iso + vatn
                msg = u"Wrong VAT " + partner_obj.vat
                msg_log(ctx, ctx['level'], msg)
                try:
                    oerp.write('res.partner', partner_id, vals)
                except:
                    msg = partner_obj.name + " WRONG VAT"
                    msg_log(ctx, ctx['level'], msg)
            elif iso < "AA" or iso > "ZZ":
                msg = partner_obj.name + " WRONG VAT"
                msg_log(ctx, ctx['level'], msg)
            elif vatn.strip() == "":
                msg = partner_obj.name + " WRONG VAT"
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


def act_check_balance(oerp, ctx):
    msg = u"Check for balance; period: " \
        + ctx['date_start'] + ".." + ctx['date_stop']
    msg_log(ctx, ctx['level'], msg)
    company_id = ctx['company_id']
    period_ids = oerp.search('account.period',
                             [('company_id', '=', company_id),
                              ('date_start', '>=', ctx['date_start']),
                              ('date_stop', '<=', ctx['date_stop'])])
    acc_balance = {}
    acc_partners = {}
    move_line_ids = oerp.search('account.move.line',
                                [('company_id', '=', company_id),
                                 ('period_id', 'in', period_ids),
                                 ('state', '!=', 'draft')])
    num_moves = len(move_line_ids)
    move_ctr = 0
    for move_line_id in move_line_ids:
        move_line_obj = oerp.browse('account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        warn_rec = False
        move_hdr_id = move_line_obj.move_id.id
        account_obj = move_line_obj.account_id
        account_tax_obj = move_line_obj.account_tax_id
        journal_obj = move_line_obj.journal_id
        acctype_id = account_obj.user_type.id
        acctype_obj = oerp.browse('account.account.type', acctype_id)
        if acctype_obj.report_type not in ("asset", "liability",
                                           "income", "expense"):
            warn_rec = "Untyped"
        if account_obj.parent_id:
            parent_account_obj = account_obj.parent_id
            parent_acctype_id = parent_account_obj.user_type.id
            parent_acctype_obj = oerp.browse('account.account.type',
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

        code = account_obj.code.encode('utf-8')
        clf3 = acctype_obj.name.encode('utf-8')
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
            msg = u"Invalid company account {0} in {1:>6} {2}".format(
                code,
                move_line_id,
                move_line_obj.ref)
            msg_log(ctx, ctx['level'] + 1, msg)
        if (account_tax_obj and account_tax_obj.company_id.id != company_id):
            msg = u"Invalid company account tax {0} in {1:>6} {2}".format(
                code,
                move_line_id,
                move_line_obj.ref)
            msg_log(ctx, ctx['level'] + 1, msg)
        if (journal_obj and journal_obj.company_id.id != company_id):
            msg = u"Invalid company journal {0} in {1:>6} {2}".format(
                code,
                move_line_id,
                move_line_obj.ref)
            msg_log(ctx, ctx['level'] + 1, msg)

        if move_line_obj.partner_id and \
                move_line_obj.partner_id.id:
            partner_id = move_line_obj.partner_id.id
            kk = "X " + str(partner_id)
            if kk not in acc_partners:
                acc_partners[kk] = 0
            acc_partners[kk] += move_line_obj.credit
            acc_partners[kk] -= move_line_obj.debit

        level = '9'
        add_on_account(acc_balance,
                       level,
                       code,
                       move_line_obj.credit,
                       move_line_obj.debit)

        level = '8'
        add_on_account(acc_balance,
                       level,
                       parent_code,
                       move_line_obj.credit,
                       move_line_obj.debit)

        level = '4'
        add_on_account(acc_balance,
                       level,
                       clf3,
                       move_line_obj.credit,
                       move_line_obj.debit)

        level = '2'
        add_on_account(acc_balance,
                       level,
                       clf2,
                       move_line_obj.credit,
                       move_line_obj.debit)

        level = '1'
        add_on_account(acc_balance,
                       level,
                       clf1,
                       move_line_obj.credit,
                       move_line_obj.debit)

        level = '0'
        add_on_account(acc_balance,
                       level,
                       '_',
                       move_line_obj.credit,
                       move_line_obj.debit)

        if warn_rec:
            msg = u"Because {0:8} look at {1:>6}/{2:>6} record {3}".format(
                warn_rec,
                move_hdr_id,
                move_line_id,
                move_line_obj.ref)
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
                    msg = "{0} {1:<16} {2:11.2f}".format(
                        ident,
                        sublevel,
                        acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    crd_amt += acc_balance[level][sublevel]
                elif acc_balance[level][sublevel] < 0:
                    msg = "{0} {1:<16} {2:11}{3:11.2f}".format(
                        ident,
                        sublevel,
                        '',
                        -acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    dbt_amt -= acc_balance[level][sublevel]
                else:
                    msg = "{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                        ident,
                        sublevel,
                        0,
                        0)
                    msg_log(ctx, ctx['level'], msg)
            msg = "{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                ident,
                '---------------',
                crd_amt,
                dbt_amt)
            msg_log(ctx, ctx['level'], msg)
        for kk in sorted(acc_partners):
            partner_id = int(kk.split(" ")[1])
            partner_obj = oerp.browse('res.partner', partner_id)
            print u"{0:<12} {1:<50} {2:11.2f}".format(kk.decode('utf-8'),
                                                      partner_obj.name,
                                                      acc_partners[kk])
    return STS_SUCCESS


def act_set_4_cscs(oerp, ctx):
    msg = u"Set for cscs"
    msg_log(ctx, ctx['level'], msg)
    # sts = analyze_invoices(oerp, ctx, 'out_invoice')
    # if sts == STS_SUCCESS:
    #    sts = analyze_invoices(oerp, ctx, 'in_invoice')
    sts = set_account_type(oerp, ctx)
    return sts


def get_payment_info(oerp, move_line_obj, ctx):
    """Return move (header) and move_line (detail) ids of passed move line
    record and return payment state if needed to become draft
    """
    move_line_id = move_line_obj.id
    move_id = move_line_obj.move_id.id
    move_obj = oerp.browse('account.move', move_id)
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
    account_invoice_obj = oerp.browse('account.invoice',
                                      inv_id)
    if account_invoice_obj.payment_ids:
        partner_id = account_invoice_obj.partner_id.id
        move_id = account_invoice_obj.move_id.id
        move_lines = oerp.search('account.move.line',
                                 [('move_id', '=', move_id),
                                  ('partner_id', '=', partner_id), ])
        for move_line_id in move_lines:
            type = oerp.browse('account.account',
                               oerp.browse('account.move.line',
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
    """If invoice state id update to draft and returned to open, linked
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
    account_invoice_obj = oerp.browse('account.invoice',
                                      inv_id)
    partner_id = account_invoice_obj.partner_id.id
    if account_invoice_obj.move_id:
        move_id = account_invoice_obj.move_id.id
    else:
        move_id = False
    move_lines = oerp.search('account.move.line',
                             [('move_id', '=', move_id),
                              ('partner_id', '=', partner_id), ])
    for move_line_id in move_lines:
        type = oerp.browse('account.account',
                           oerp.browse('account.move.line',
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
        move_line_obj = oerp.browse('account.move.line', move_line_id)
        if move_line_obj.partner_id.id != partner_id or \
                move_line_obj.company_id.id != company_id:
            valid_recs = False
        else:
            new_reconciles.append(move_line_id)
    if not valid_recs:
        new_reconciles = []
    reconcile_dict = {inv_id: new_reconciles}
    return new_reconciles, reconcile_dict


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
    invoice_ids = oerp.search('account.invoice',
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
            oerp.write('account.journal', journals, vals)
        except:
            msg = u"Cannot update journals"
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
    invoice_obj = oerp.get('account.invoice')
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
            period_ids = oerp.execute('account.period',
                                      'find',
                                      str(registration_date))
            period_id = period_ids and period_ids[0] or False
            vals['period_id'] = period_id
            try:
                oerp.write('account.invoice', [inv_id], vals)
            except:
                msg = u"Cannot update registration date of %d" % inv_id
                msg_log(ctx, ctx['level'], msg)
            if 'registration_date' in vals and move_id:
                oerp.write('account.move',
                           [move_id],
                           {'date': vals['registration_date']})
                move_lines = oerp.search('account.move.line',
                                         [('move_id', '=', move_id)])
                for move_line_id in move_lines:
                    oerp.write('account.move.line',
                               [move_line_id],
                               {'date': vals['registration_date']})
    return min_rec_date


def upd_invoices_2_draft(oerp, move_dict, ctx):
    """Set invoices (header) list/dictionary to draft state.
    See upd_invoices_2_posted to return in posted state
    @ param move_dict: invoices (header) dictionary keyed on state or
                       invoices list to set in draft state
    """
    for i, state in enumerate(INVOICES_STS_2_DRAFT):
        invoices = []
        if isinstance(move_dict, dict):
            invoices = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            invoices = move_dict
        if len(invoices):
            try:
                oerp.execute('account.invoice',
                             "action_cancel",
                             invoices)
            except:
                msg = u"Cannot update invoice status"
                msg_log(ctx, ctx['level'], msg)
            try:
                msg = u"Update invoices to open %s " % invoices
                msg_log(ctx, ctx['level'], msg)
                oerp.execute('account.invoice',
                             "action_cancel_draft",
                             invoices)
            except:
                msg = u"Cannot update invoice status"
                msg_log(ctx, ctx['level'], msg)
                return STS_FAILED
    return STS_SUCCESS


def upd_invoices_2_posted(oerp, move_dict, ctx):
    """Set invoices (header) list/dictionary to posted state.
    See upd_invoices_2_draft  to set in draft state before execute this one.
    @ param move_dict: invoices (header) dictionary keyed on state or
                       invoices list to set in posted state
    """
    sts = STS_SUCCESS
    for i, state in enumerate(INVOICES_STS_2_DRAFT):
        invoices = []
        if isinstance(move_dict, dict):
            invoices = move_dict[state]
        elif isinstance(move_dict, list) and i == 0:
            invoices = move_dict
        if len(invoices):
            msg = u"Restore invoices to validated %s " % invoices
            msg_log(ctx, ctx['level'], msg)
            for inv_id in invoices:
                try:
                    oerp.exec_workflow('account.invoice',
                                       'invoice_open',
                                       inv_id)
                    # oerp.execute('account.invoice',
                    #              "invoice_validate",
                    #              invoices)
                except:
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
                msg = u"Update payments to draft %s" % payments
                msg_log(ctx, ctx['level'], msg)
                oerp.execute('account.move',
                             "button_cancel",
                             payments)
            except:
                msg = u"Cannot update payment status"
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
                msg = u"Restore payments to posted %s" % payments
                msg_log(ctx, ctx['level'], msg)
                oerp.execute('account.move',
                             "button_validate",
                             payments)
            except:
                msg = u"Cannot restore payment status"
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
        msg = u"Unreconcile invoice %d" % inv_id
        msg_log(ctx, ctx['level'], msg)
        try:
            context = {'active_ids': reconcile_dict[inv_id]}
            oerp.execute('account.unreconcile',
                         'trans_unrec',
                         None,
                         context)
        except:
            msg = u"Cannot update invoice status of %d" % inv_id
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
    return STS_SUCCESS


def reconcile_invoices(oerp, reconcile_dict, ctx):
    for inv_id in reconcile_dict:
        msg = u"Reconcile invoice %d" % inv_id
        msg_log(ctx, ctx['level'], msg)
        try:
            context = {'active_ids': reconcile_dict[inv_id]}
            oerp.execute('account.move.line.reconcile',
                         'trans_rec_reconcile_partial_reconcile',
                         None,
                         context)
            # oerp.execute('account.move.line',
            #              'reconcile',
            #              reconcile_dict[inv_id],
            #              'manual')
        except:
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
            oerp.write('account.account', accounts, vals)
        except:
            msg = u"Cannot update accounts"
            msg_log(ctx, ctx['level'], msg)
            return STS_FAILED
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
    account_ids = oerp.search('account.account', [('company_id',
                                                   '=',
                                                   company_id),
                                                  ('code',
                                                   'like',
                                                   ctx['account_code'])])
    if len(account_ids) == 0:
        return STS_FAILED
    for account_id in account_ids:
        account = oerp.browse('account.account', account_id)
        msg = u"Account %s %s" % (account.code, account.name)
        msg_log(ctx, ctx['level'], msg)
    move_line_ids = oerp.search('account.move.line',
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
        move_line_obj = oerp.browse('account.move.line', move_line_id)
        move_ctr += 1
        msg_burst(4, "Move    ", move_ctr, num_moves)
        account_obj = move_line_obj.account_id
        valid = True
        # valid = False       # debug
        if not account_obj.parent_id:
            valid = False
        acctype_id = account_obj.user_type.id
        acctype_obj = oerp.browse('account.account.type', acctype_id)
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


def analyze_invoices(oerp, ctx, inv_type):
    company_id = ctx['company_id']
    period_ids = oerp.search('account.period',
                             [('company_id', '=', company_id),
                              ('date_start', '>=', ctx['date_start']),
                              ('date_stop', '<=', ctx['date_stop'])])
    account_invoice_ids = oerp.search('account.invoice',
                                      [('company_id', '=', company_id),
                                       ('period_id', 'in', period_ids),
                                       ('type', '=', inv_type),
                                       ('internal_number', '!=', '')],
                                      # ('state', '!=', 'draft'),
                                      # ('state', '!=', 'cancel')],
                                      order='internal_number')
    num_invs = len(account_invoice_ids)
    last_number = ''
    inv_ctr = 0
    last_seq = 0
    for account_invoice_id in account_invoice_ids:
        account_invoice_obj = oerp.browse('account.invoice',
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
        #     period_ids = oerp.execute('account.period',
        #                               'find',
        #                               registration_date)
        #     period_id = period_ids and period_ids[0] or False
        #     vals['period_id'] = period_id
        #     try:
        #         oerp.write('account.invoice', account_invoice_id, vals)
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
    values = oerp.execute(setup_model,
                          'default_get',
                          [])
    db_name = values['name']
    setup_id = oerp.execute(setup_model,
                            'create',
                            values)
    oerp.execute(setup_model,
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


def get_actioname(actv):
    if isinstance(actv, basestring) and \
            actv[-4:] in ('_7.0', '_8.0', '_9.0', '_10.0'):
        act = actv[0:-4]
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
                    if row[o_model['db_type']] != ctx['db_type']:
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
            vals = {}
            for n in row:
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
                cur_obj = oerp.browse(o_model['model'], id)
                name_old = cur_obj[o_model['name']]
                msg = u"Update " + str(id) + " " + name_old
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['heavy_trx']:
                    v = {}
                    for p in vals:
                        if p != "db_type" and \
                                vals[p] != cur_obj[p]:
                            v[p] = vals[p]
                    vals = v
                    del v
                if not ctx['dry_run'] and len(vals):
                    try:
                        oerp.write(o_model['model'], ids, vals)
                        msg = u"id={0}, {1}={2}->{3}".\
                              format(cur_obj.id,
                                     tounicode(o_model['name']),
                                     tounicode(name_old),
                                     tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                    except:
                        os0.wlog(u"!!write error!")
            else:
                msg = u"insert " + name_new.decode('utf-8')
                debug_msg_log(ctx, ctx['level'] + 1, msg)
                if not ctx['dry_run']:
                    if not o_model.get('hide_cid', False):
                        vals['company_id'] = ctx['company_id']
                    try:
                        id = oerp.create(o_model['model'], vals)
                        msg = u"creat id={0}, {1}={2}"\
                              .format(id,
                                      tounicode(o_model['name']),
                                      tounicode(name_new))
                        msg_log(ctx, ctx['level'] + 1, msg)
                    except:
                        id = None
                        os0.wlog(u"!!write error!")
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
    group_id = oerp.search('res.groups',
                           [('name', '=', name)],
                           context=context)
    if len(group_id) != 1:
        msg = u"!Parameter name " + name + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    user_id = oerp.search('res.users',
                          [('login', '=', user)])
    if len(user_id) != 1:
        msg = u"!User " + user + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    user_obj = oerp.browse('res.users', user_id[0])
    if not user_obj:
        msg = u"!User " + user + " not found!"
        msg_log(ctx, ctx['level'] + 2, msg)
        return STS_FAILED
    ids = user_obj.groups_id.ids
    id = group_id[0]
    vals = {}
    if isinstance(value, bool):
        if value:
            if id not in ids:
                vals['groups_id'] = [(4, id)]
                msg = u"%s.%s = True" % (user, name)
                msg_log(ctx, ctx['level'] + 2, msg)
        else:
            if id in ids:
                vals['groups_id'] = [(3, id)]
                msg = u"%s.%s = False" % (user, name)
                msg_log(ctx, ctx['level'] + 2, msg)
    if not ctx['dry_run'] and len(vals):
        oerp.write('res.users', user_id, vals)
        # ids = oerp.search('ir.module.category',
        #                   [('name', '=', category)])
        # if len(ids):
        #     mod_cat_id = ids[0]
        #     if ctx_name is not None:
        #         ctx_sel_ids = oerp.search('res.groups',
        #                                   [('category_id', '=', mod_cat_id),
        #                                    ('name', '=', ctx_name)])
        #         ctx_label = "." + ctx_name
        #     else:
        #         ctx_sel_ids = oerp.search('res.groups',
        #                                   [('category_id', '=', mod_cat_id)])
        #         ctx_label = ""
        #     ctx_sel_name = {}
        #     for id in sorted(ctx_sel_ids):
        #         cur_obj = oerp.browse('res.groups', id)
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
    chart_template_id = oerp.search('account.chart.template',
                                    [('name',
                                      '=',
                                      name)],
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
    currency_id = oerp.browse('res.company', company_id).currency_id
    chart_values = {
        'company_id': company_id,
        'currency_id': currency_id,
        'chart_template_id': chart_template_id
    }
    chart_values.update(oerp.execute(chart_setup_model,
                                     'onchange_chart_template_id',
                                     [],
                                     1)['value'])
    chart_setup_id = oerp.execute(chart_setup_model,
                                  'create',
                                  chart_values)
    oerp.execute(chart_setup_model,
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
        res = check_actions_1_list(ctx['do_sel_action'],
                                   lx_act,
                                   conf_obj)
    elif ctx.get('actions', None):
        res = check_actions_1_list(ctx['actions'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_db', None):
        res = check_actions_1_list(ctx['actions_db'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_mc', None):
        res = check_actions_1_list(ctx['actions_mc'],
                                   lx_act,
                                   conf_obj)
    if res and ctx.get('actions_uu', None):
        res = check_actions_1_list(ctx['actions_uu'],
                                   lx_act,
                                   conf_obj)
    return res


def check_actions_1_list(list, lx_act, conf_obj):
    res = True
    if not list:
        return res
    acts = list.split(',')
    for actv in acts:
        act = get_actioname(actv)
        if act == '' or act is False or act is None:
            continue
        elif act in lx_act:
            continue
        elif conf_obj.has_section(act):
            if conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                res = check_actions_1_list(actions,
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
        lx_act = extend_actions_1_list(ctx['actions'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_db', None):
        lx_act = extend_actions_1_list(ctx['actions_db'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_mc', None):
        lx_act = extend_actions_1_list(ctx['actions_mc'],
                                       lx_act,
                                       conf_obj)
    if ctx.get('actions_uu', None):
        lx_act = extend_actions_1_list(ctx['actions_uu'],
                                       lx_act,
                                       conf_obj)
    return lx_act


def extend_actions_1_list(list, lx_act, conf_obj):
    if not list:
        return lx_act
    acts = list.split(',')
    for act in acts:
        if act == '' or act is False or act is None:
            continue
        elif act in lx_act:
            continue
        elif conf_obj.has_section(act):
            lx_act.append(act)
            if conf_obj.has_option(act, 'actions'):
                actions = conf_obj.get(act, 'actions')
                lx_act = extend_actions_1_list(actions,
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
    elif ctx.get('multi_db', False) and not do_multidb:
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
        msg = u"Operations ended"
    else:
        msg = u"Last operation FAILED!"
    msg_log(ctx, ctx['level'], msg)
    return sts


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
