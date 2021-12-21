# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Clodoo common library
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from future import standard_library
# from builtins import chr
# from builtins import str
# from builtins import *                                           # noqa: F403
from past.builtins import unicode
import argparse
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import inspect
import os
import re
import time
import subprocess
from datetime import date

from os0 import os0
standard_library.install_aliases()                                 # noqa: E402

# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = "./clodoo.conf"
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = ["/etc/odoo/odoo-server.conf",
             "/etc/odoo/odoo.conf",
             "/etc/odoo-server.conf",
             "/etc/odoo.conf",
             "/etc/openerp/openerp-server.conf",
             "/etc/openerp-server.conf",
             "/etc/odoo/openerp-server.conf", ]
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
# Warning: if following LX have no values LX=(), if have 1 value LX=(value,)
# list of string parameters in [options] of config file
LX_CFG_S = ('db_name',
            'db_user',
            'db_password',
            'login_user',
            'login2_user',
            'crypt_password',
            'login_password',
            'crypt2_password',
            'login2_password',
            'admin_passwd',
            'db_host',
            'db_port',
            'data_dir',
            'xmlrpc_port',
            'oe_version',
            'zeroadm_mail',
            'zeroadm_login',
            'oneadm_mail',
            'oneadm_login',
            'oneadm_pwd',
            'botadm_mail',
            'botadm_login',
            'botadm_pwd',
            'svc_protocol',
            'dbfilter',
            'dbfilterd',
            'dbfiltert',
            'dbfilterz',
            'dbtypefilter',
            'companyfilter',
            'userfilter',
            'lang',
            'adm_uids',
            'data_path',
            'date_start',
            'date_stop',
            'account_code',
            'actions',
            'actions_db',
            'actions_mc',
            'actions_uu',
            'heavy_trx',
            'install_modules',
            'uninstall_modules',
            'purge_modules',
            'upgrade_modules',
            'data_selection',
            'modules_2_manage',
            'chart_of_account',
            'catalog_db',
            'custom_act',
            'model',
            'model_code',
            'model_name',
            'model_action',
            'model_keyids',
            'alias_model2',
            'alias_field',
            'hide_cid',
            'modelA',
            'modelA_code',
            'modelA_name',
            'modelA_action',
            'modelA_keyids',
            'aliasA_model2',
            'aliasA_field',
            'hideA_cid',
            'modelB',
            'modelB_code',
            'modelB_name',
            'modelB_action',
            'modelB_keyids',
            'aliasB_model2',
            'aliasB_field',
            'hideB_cid',
            'filename',
            'psycopg2',
            'TRANSDICT',
            )
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ('install_modules',
             'uninstall_modules',
             'purge_modules',
             'actions',
             'actions_db',
             'actions_mc',
             'actions_uu',
             'heavy_trx',
             'psycopg2',)
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ('set_passepartout',
            'check_balance',
            'with_demo',
            'no_fvalidation',
            'draft_recs',
            'setup_banks',
            'setup_account_journal',
            'setup_partners',
            'setup_partner_banks',
            'check_config',
            'exit_onerror',
            )
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_S = ('db_name', 'dbfilter', 'dbg_mode', 'do_sel_action', 'dry_run',
            'lang', 'with_demo', 'no_fvalidation', 'lgi_user', 'lgi_pwd',
            'logfn', 'quiet_mode', 'xmlrpc_port', 'odoo_vid', 'exit_onerror',
            'data_selection')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_B = ('dry_run', 'with_demo', 'no_fvalidation', 'exit_onerror')
# List of numeric parameters in line command; may be in LX_CFG_S list too
LX_OPT_N = ()
# list of opponent options
LX_OPT_OPPONENT = {}
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_S
LX_SB = ()
# switch values of options
LX_OPT_ARGS = {}
DEFDCT = {}

msg_time = time.time()


__version__ = "0.3.55"


#############################################################################
# Message and output
#
def init_logger(ctx):
    if ctx['quiet_mode']:
        os0.set_tlog_file(ctx['logfn'],
                          echo=False)
    else:
        os0.set_tlog_file(ctx['logfn'],
                          echo=True)


def msg_burst(level, text, i, n):
    """Show a message per second from burst sequence as a gauge"""
    global msg_time
    t = time.time() - msg_time
    if (t > 1):
        ident = ' ' * level
        print(u"\x1b[A{0}[{1:>6}/{2:>6}] {3}".format(ident,
                                                     i,
                                                     n,
                                                     tounicode(text)))
        msg_time = time.time()


def msg(level, text):
    """Show and log a message"""
    ident = ' ' * level
    txt = u"{0}{1}".format(ident, tounicode(text))
    print(txt)


def msg_log(ctx, level, text):
    """Log a message and show if needed"""
    ident = ' ' * level
    if ctx:
        if 'test_unit_mode' in ctx:
            return
        elif ctx['dry_run'] and level > 0:
            txt = u"{0}({1})".format(ident, tounicode(text))
        else:
            txt = u"{0}{1}".format(ident, tounicode(text))
    else:
        txt = u"{0}{1}".format(ident, tounicode(text))
    os0.wlog(txt)


def debug_msg_log(ctx, level, text):
    """Log a debug message and show if needed"""
    global db_msg_sp, db_msg_stack
    # if level == -999:
    #     db_msg_sp += 1
    #     return
    ident = ' ' * abs(level)
    if ctx.get('dbg_mode', False):
        if 'test_unit_mode' in ctx:
            return
        elif ctx['dry_run'] and level > 0:
            txt = u">%s(%s)" % (ident, tounicode(text))
        else:
            txt = u">%s%s" % (ident, tounicode(text))
        print(txt)
        # os0.wlog(txt)


def crypt(s):
    k = "Caserta1959!TO61TV"
    t = ""
    for i, c in enumerate(s):
        j = ord(k[i])
        x = (((ord(c) - 33) + j - (i * 3)) % 95) + 33
        t = t + chr(x)
    return t


def decrypt(t):
    k = "Caserta1959!TO61TV"
    s = ""
    for i, c in enumerate(t):
        j = ord(k[i])
        x = (((ord(c) - 33) - j + (i * 3)) % 95) + 33
        s = s + chr(x)
    return s


def ismbcs(t):
    """"Return true id string contains mbcs"""
    if isinstance(t, str):
        try:
            t = unicode(t)
            return False
        except BaseException:
            return True
    return False


def strtype(t):
    """Return string type: ascii, mbcs or unicode"""
    if isinstance(t, unicode):
        return 'unicode'
    elif isinstance(t, str):
        try:
            t = unicode(t)
            return 'ascii'
        except BaseException:
            return 'mbcs'
    else:
        return None


def tounicode(s):
    """Return unicode string from basestring"""
    if strtype(s) == 'unicode':
        return s
    elif strtype(s) == 'mbcs':
        return s.decode('utf-8')
    elif strtype(s) == 'ascii':
        return unicode(s)
    else:
        return s


#############################################################################
def default_conf(ctx):
    """Default configuration values"""
    y = date.today().year
    dfmt = "%Y-%m-%d"
    dts_start = date(y, 1, 1).strftime(dfmt)
    dts_stop = date(y, 12, 31).strftime(dfmt)
    return {'login_user': 'admin',
            'crypt_password': 'Ec{fu',
            'login_password': '',
            'login2_user': 'admin',
            'crypt2_password': '',
            'login2_password': '',
            'admin_passwd': 'admin',
            'db_user': 'postgres',
            'db_host': 'localhost',
            'data_dir': '',
            'db_port': 5432,
            'oe_version': '*',
            'svc_protocol': '',
            'xmlrpc_port': 8069,
            'odoo_vid': '12.0',
            'db_name': 'demo',
            'logfile': False,
            'dbfilter': '.*',
            'dbfilterd': 'demo',
            'dbfiltert': '(openerp|odoo|test)',
            'dbfilterz': 'zi[0-9]{8}',
            'dbtypefilter': '',
            'companyfilter': r'(?![Zz]eroincombenze.*)',
            'userfilter': '.*',
            'lang': 'en_US',
            'with_demo': '0',
            'date_start': dts_start,
            'date_stop': dts_stop,
            'draft_recs': '0',
            'account_code': '000000',
            'adm_uids': '1',
            'set_passepartout': '0',
            'check_balance': '0',
            'setup_banks': '0',
            'setup_account_journal': '0',
            'setup_partners': '0',
            'setup_partner_banks': '0',
            'check_config': '0',
            'exit_onerror': '0',
            'custom_act': '',
            'install_modules': False,
            'uninstall_modules': False,
            'purge_modules': False,
            'upgrade_modules': False,
            'data_selection': 'account_move,sale,purchase,project,mail,crm,'
                              'inventory,marketing,hr,analytic',
            'modules_2_manage': '',
            'zeroadm_mail': 'cc@shs-av.com',
            'zeroadm_login': 'zeroadm',
            'oneadm_mail': 'admin@example.com',
            'oneadm_login': 'admin',
            'oneadm_pwd': 'admin',
            'botadm_mail': 'zerobot@example.com',
            'botadm_login': 'zerobot',
            'botadm_pwd': '',
            'data_path': './data',
            'actions': '',
            'actions_db': '',
            'actions_mc': '',
            'actions_uu': '',
            'heavy_trx': False,
            'chart_of_account': 'configurable_chart_template',
            'catalog_db': 'zeroincombenze',
            'psycopg2': 'False',
            'caller': '',
            'level': 4,
            'dry_run': False,
            'multi_user': False,
            'ena_inquire': False,
            'no_login': False,
            'TRANSDICT': {}
            }


def get_versioned_option(conf_obj, sect, param, is_bool=None, defval=None):
    is_bool = is_bool or False
    found = False
    if conf_obj:
        for sfx in ('6.1', '7.0', '8.0', '9.0', '10.0',
                    '11.0', '12.0', '13.0', '14.0'):
            vparam = '%s_%s' % (param, sfx)
            if conf_obj.has_option(sect, vparam):
                found = True
                break
    if not found:
        vparam = param
        if conf_obj and conf_obj.has_option(sect, vparam):
            found = True
    if found:
        if is_bool:
            return conf_obj.getboolean(sect, vparam)
        value = conf_obj.get(sect, vparam)
        if value != 'False':
            return value
    if defval and param in defval:
        return defval[param]
    else:
        return None


def create_def_params_dict(ctx):
    """Create default params dictionary"""
    opt_obj = ctx.get('_opt_obj', None)
    conf_obj = ctx.get('_conf_obj', None)
    s = "options"
    if conf_obj and not conf_obj.has_section(s):
        conf_obj.add_section(s)
    DEFDCT = default_conf(ctx)
    for p in LX_CFG_S:
        v = get_versioned_option(conf_obj, s, p, defval=DEFDCT)
        if v is not None:
            ctx[p] = v
    for p in LX_CFG_B:
        v = get_versioned_option(conf_obj, s, p, is_bool=True)
        if v is not None:
            ctx[p] = v
    if opt_obj:
        for p in LX_OPT_S:
            if p in LX_OPT_OPPONENT:
                a = LX_OPT_OPPONENT[p]
                if hasattr(opt_obj, a) and \
                        getattr(opt_obj, a) is False:
                    ctx[p] = False
                elif hasattr(opt_obj, p) and \
                        getattr(opt_obj, p):
                    ctx[p] = True
                else:
                    ctx[p] = None
            elif hasattr(opt_obj, p):
                tmp = getattr(opt_obj, p)
                if p not in ctx or tmp:
                    ctx[p] = tmp
        for p in LX_OPT_B:
            if hasattr(opt_obj, p):
                ctx[p] = os0.str2bool(getattr(opt_obj, p), None)
        for p in LX_OPT_N:
            if hasattr(opt_obj, p) and getattr(opt_obj, p):
                ctx[p] = int(getattr(opt_obj, p))
    for p in LX_CFG_SB:
        ctx[p] = os0.str2bool(ctx[p], ctx[p])
    if ctx.get('LX_CFG_S', ''):
        ctx['LX_CFG_S'] = eval(ctx['LX_CFG_S'])
    return ctx


def create_params_dict(ctx):
    """Create all params dictionary"""
    ctx = create_def_params_dict(ctx)
    DEFDCT = default_conf(ctx)
    if ctx.get('dbg_mode', None) is None:
        ctx['dbg_mode'] = ctx['run_daemon']
    if not ctx.get('logfn', None):
        if 'tlog' in ctx:
            ctx['logfn'] = ctx['tlog']
        else:
            ctx['logfn'] = "~/" + ctx['caller'] + ".log"
    conf_obj = ctx.get('_conf_obj', None)
    opt_obj = ctx.get('_opt_obj', None)
    s = "options"
    if conf_obj and not conf_obj.has_section(s):
        conf_obj.add_section(s)
    v = get_versioned_option(conf_obj, s, 'db_password', defval=DEFDCT)
    if v is not None:
        ctx['db_pwd'] = v
    else:
        ctx['db_pwd'] = ''
    for p in ():
        ctx[p] = conf_obj.getint(s, p)
    if opt_obj:
        if hasattr(opt_obj, 'dbfilter') and opt_obj.dbfilter != "":
            ctx['dbfilter'] = opt_obj.dbfilter
            ctx['multi_db'] = True
        if (hasattr(opt_obj, 'modules_2_manage') and
                hasattr(opt_obj, 'do_sel_action')):
            if opt_obj.do_sel_action in ('install_modules',
                                         'uninstall_modules',
                                         'upgrade_modules',
                                         'purge_modules'):
                ctx[opt_obj.do_sel_action] = opt_obj.modules_2_manage
        if hasattr(opt_obj, 'data_path') and opt_obj.data_path != "":
            ctx['data_path'] = opt_obj.data_path
    # if ctx['db_host'] == 'False':
    #     ctx['db_host'] = 'localhost'
    if 'oe_version' in ctx and not ctx.get('odoo_vid'):
        ctx['odoo_vid'] = ctx['oe_version']
    else:
        ctx['oe_version'] = build_odoo_param('FULLVER', ctx['odoo_vid'])
    if not ctx['svc_protocol']:
        if ctx['oe_version'] in ('9.0', '8.0', '7.0', '6.1'):
            ctx['svc_protocol'] = 'xmlrpc'
        else:
            ctx['svc_protocol'] = 'jsonrpc'
    if ctx.get('do_sel_action', False):
        ctx['actions'] = ctx['do_sel_action']
    elif ctx.get('actions_db', None):
        ctx['actions'] = 'per_db,' + ctx['actions_db']
        del ctx['actions_db']
    elif ctx.get('actions_mc', None):
        ctx['actions'] = 'per_company,' + ctx['actions_mc']
        del ctx['actions_mc']
    elif ctx.get('actions_uu', None):
        ctx['actions'] = 'per_users,' + ctx['actions_uu']
        del ctx['actions_uu']
    return ctx


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


def fullname_conf(ctx):
    if ctx.get('conf_fn'):
        confs = []
        for confn in ctx['conf_fn'].split(','):
            if not os.path.isfile(confn):
                for path in ('.', './confs', './conf', './code'):
                    if os.path.isfile('%s/%s' % (path, confn)):
                        confn = '%s/%s' % (path, confn)
                        break
            confs.append(confn)
        if len(confs) == 1:
            ctx['conf_fn'] = confs[0]
        else:
            ctx['conf_fn'] = ','.join(confs)
    return ctx


def read_config(ctx):
    """Read both user configuration and local configuration."""

    def set_confs(ctx):
        version_is_set = False
        for ver in ('odoo_vid', 'oe_version'):
            if ctx.get(ver):
                fnver = build_odoo_param('CONFN', ctx[ver], multi=True)
                if os.path.isfile(fnver) and fnver not in ctx['conf_fns']:
                    ctx['conf_fns'].insert(0, fnver)
                    version_is_set = True
                else:
                    fnver = build_odoo_param('CONFN', ctx[ver])
                    if os.path.isfile(fnver) and fnver not in ctx['conf_fns']:
                        ctx['conf_fns'].insert(0, fnver)
                        version_is_set = True
        return ctx, version_is_set

    if not ctx.get('conf_fn', None):
        ctx['conf_fn'] = ctx.get('caller', 'clodoo') + ".conf"
    ctx = fullname_conf(ctx)
    ctx['conf_fns'] = ctx['conf_fn'].split(',')
    ctx, version_is_set = set_confs(ctx)
    ctx['_conf_obj'] = ConfigParser.RawConfigParser(default_conf(ctx))
    ctx['conf_fns'] = ctx['_conf_obj'].read(ctx['conf_fns'])
    if not ctx['conf_fns']:
        raise IOError('No configuration file found!')
    ctx = create_params_dict(ctx)
    if not version_is_set:
        ctx, version_is_set = set_confs(ctx)
        ctx['conf_fns'] = ctx['_conf_obj'].read(ctx['conf_fns'])
        ctx = create_params_dict(ctx)
    return ctx


def create_parser(version, doc, ctx):
    """Return command-line parser.
    Some options are standard:
    -c --config     set configuration file (conf_fn)
    -h --help       show help
    -q --quiet      quiet mode
    -t --dry-run    simulation mode for test (simulate)
    -U --user       set username (user)
    -v --verbose    verbose mode (dbg_mode)
    -V --version    show version
    -y --yes        confirmation w/out ask
    """
    parser = argparse.ArgumentParser(
        description=docstring_summary(doc),
        epilog="© 2015-2021 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-A", "--action-to-do",
                        help="action to do (use list_actions to dir)",
                        dest="do_sel_action",
                        metavar="actions",
                        default=None)
    parser.add_argument("-b", "--odoo-branch",
                        help="talk server Odoo version",
                        dest="odoo_vid",
                        metavar="version",
                        default="")
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default=CONF_FN)
    parser.add_argument("-d", "--dbfilter",
                        help="DB filter",
                        dest="dbfilter",
                        metavar="regex",
                        default="")
    parser.add_argument("-i", "--ignore-name-validation",
                        help="ignore name validation fo csv columns",
                        action="store_true",
                        dest="no_fvalidation",
                        default=False)
    parser.add_argument("-l", "--lang",
                        help="user language",
                        dest="lang",
                        metavar="iso_lang",
                        default=False)
    parser.add_argument("-m", "--modules-2-manage",
                        help="Module list to upgrade",
                        dest="modules_2_manage",
                        metavar="list",
                        default="")
    parser.add_argument("-n", "--dry-run",
                        help="test execution mode",
                        action="store_true",
                        dest="dry_run",
                        default=False)
    parser.add_argument("-o", "--with-demo",
                        help="create db with demo data",
                        action="store_true",
                        dest="with_demo",
                        default=False)
    parser.add_argument("-p", "--data-path",
                        help="Import file path",
                        dest="data_path",
                        metavar="dir",
                        default="")
    parser.add_argument("-P", "--pwd",
                        help="login password",
                        dest="lgi_pwd",
                        metavar="password",
                        default='admin')
    parser.add_argument("-q", "--quiet",
                        help="run silently",
                        action="store_true",
                        dest="quiet_mode",
                        default=False)
    parser.add_argument("-r", "--xmlrpc-port",
                        help="xmlrpc port",
                        dest="xmlrpc_port",
                        metavar="port",
                        default="")
    parser.add_argument("-S", "--data-selection",
                        help="Select data to remove",
                        dest="data_selection",
                        metavar="list",
                        default="")
    parser.add_argument("-U", "--user",
                        help="login username",
                        dest="lgi_user",
                        metavar="username",
                        default=None)
    parser.add_argument("-v", "--verbose",
                        help="run with debugging output",
                        action="store_true",
                        dest="dbg_mode",
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + version)
    parser.add_argument("-x", "--exit-on-error",
                        help="exit on error",
                        action="store_true",
                        dest="exit_onerror",
                        default=False)
    return parser


def parse_args(arguments,
               apply_conf=APPLY_CONF, version=None, tlog=None, doc=None):
    """Parse command-line options."""
    ctx = {}
    ctx['caller_fqn'] = inspect.stack()[1][1]
    ctx['caller'] = os0.nakedname(os.path.basename(ctx['caller_fqn']))
    ctx['run_daemon'] = False if os.isatty(0) else True
    ctx['run_tty'] = os.isatty(0)
    if tlog:
        ctx['tlog'] = tlog
    else:
        ctx['tlog'] = "./%s.log" % ctx['caller']
    # running autotest
    if version is None:
        ctx['_run_autotest'] = True
    parser = create_parser(version, doc, ctx)
    ctx['_parser'] = parser
    opt_obj = parser.parse_args(arguments)
    ctx['_opt_obj'] = opt_obj
    if apply_conf:
        if hasattr(opt_obj, 'conf_fn'):
            ctx['conf_fn'] = opt_obj.conf_fn
        if hasattr(opt_obj, 'odoo_vid') and opt_obj.odoo_vid:
            ctx['odoo_vid'] = opt_obj.odoo_vid
        ctx = read_config(ctx)
        opt_obj = parser.parse_args(arguments)
    ctx['level'] = 0
    ctx = create_params_dict(ctx)
    return ctx


def check_if_running(ctx, pid):
    f_alrdy_run = False
    id_str = ctx['caller'] + ".py"
    cmd = "ps aux|grep " + id_str
    os0.muteshell(cmd, keepout=True)
    stdinp_fd = open(os0.setlfilename(os0.bgout_fn), 'r')
    rxmatch = "root .* python .*" + id_str + ".*"
    rxnmatch = "root .* {0} .*".format(pid)
    line = stdinp_fd.readline()
    while line != "" and not f_alrdy_run:
        i = line.rfind('\n')
        if i >= 0:
            if re.match(rxmatch, line) and not re.match(rxnmatch, line):
                f_alrdy_run = True
        line = stdinp_fd.readline()
    stdinp_fd.close()
    if os.path.isfile(os0.setlfilename(os0.bgout_fn)):
        os.remove(os0.setlfilename(os0.bgout_fn))
    return f_alrdy_run


def get_odoo_full_ver(odoo_vid):
    v = re.search(r'[0-9]+(\.[0-9])?', odoo_vid).group()
    if v == '6':
        odoo_fver = '6.1'
    elif v.find('.') >= 0:
        odoo_fver = v
    else:
        odoo_fver = v + '.0'
    return odoo_fver


def build_odoo_param(item, odoo_vid=None, debug=None, suppl=None,
                     git_org=None, multi=None):
    odoorc = os.path.join(os.path.dirname(__file__), 'odoorc')
    if multi:
        cmd = 'opt_multi=1 %s %s "%s" "%s" "%s"' % (
            odoorc,
            item,
            odoo_vid,
            suppl or '',
            git_org or '')
    else:
        cmd = '%s %s "%s" "%s" "%s"' % (
            odoorc,
            item,
            odoo_vid,
            suppl or '',
            git_org or '')
    out, err = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True).communicate()
    if not out:
        return False
    out = os0.u(out)
    if item in ('LPPORT', 'MAJVER', 'RPCPORT'):
        return eval(out.split('\n')[0])
    return out.split('\n')[0]