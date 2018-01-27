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

# import platform
import argparse
import ConfigParser
import inspect
# import pdb
import os
import re
import time
from datetime import date

from os0 import os0


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
            'login_user',
            'login2_user',
            'login_password',
            'login2_password',
            'admin_passwd',
            'db_host',
            'xmlrpc_port',
            'oe_version',
            'zeroadm_mail',
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
            'upgrade_modules',
            'chart_of_account',
            'catalog_db',
            'custom_act',
            'model',
            'model_code',
            'model_name',
            'filename',
            'hide_cid',
            'psycopg2',
            )
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ('install_modules',
             'uninstall_modules',
             'actions',
             'actions_db',
             'actions_mc',
             'actions_uu',
             'heavy_trx')
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ('set_passepartout',
            'check_balance',
            'with_demo',
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
LX_OPT_S = ('dbg_mode', 'do_sel_action', 'dry_run', 'lang', 'with_demo'
            'lgi_user', 'lgi_pwd', 'logfn', 'quiet_mode', 'xmlrpc_port',
            'oe_version')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_B = ('dry_run', 'with_demo')
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


__version__ = "0.3.2"


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
    print txt


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
            txt = u">{0}({1})".format(ident, tounicode(text))
        else:
            txt = u">{0}{1}".format(ident, tounicode(text))
        print txt
        os0.wlog(txt)


def crypt(s):
    k = "Caserta1959"
    t = ""
    for i, c in enumerate(s):
        j = ord(k[i])
        x = (((ord(c) - 33) + j - (i * 3)) % 95) + 33
        t = t + chr(x)
    return t


def decrypt(t):
    k = "Caserta1959"
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
    DEFDCT = {'login_user': 'admin',
              'login_password': 'Ec{fu',
              'login2_user': 'admin',
              'login2_password': 'admin',
              'admin_passwd': 'admin',
              'db_user': 'postgres',
              'db_host': 'localhost',
              'svc_protocol': '',
              'xmlrpc_port': '8069',
              'oe_version': '7.0',
              'dbfilter': '.*',
              'dbfilterd': 'demo',
              'dbfiltert': 'openerp.*',
              'dbfilterz': 'zi[0-9]{8}',
              'dbtypefilter': '',
              'companyfilter': '(?![Zz]eroincombenze.*)',
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
              'upgrade_modules': False,
              'zeroadm_mail': 'cc@shs-av.com',
              'data_path': './data',
              'actions': '',
              'actions_db': '',
              'actions_mc': '',
              'actions_uu': '',
              'heavy_trx': False,
              'chart_of_account': 'configurable_chart_template',
              'catalog_db': 'zeroincombenze',
              'psycopg2': 'False',
              # 'model_name': 'name',
              }
    return DEFDCT


def get_versioned_option(conf_obj, sect, param, is_bool=None, defval=None):
    is_bool = is_bool or False
    found = False
    if conf_obj:
        for sfx in ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0'):
            vparam = '%s_%s' % (param, sfx)
            if conf_obj.has_option(sect, vparam):
                found = True
                break
    if not found:
        vparam = param
        if not conf_obj or not conf_obj.has_option(sect, vparam):
            if defval and vparam in defval:
                return defval[vparam]
            else:
                return None
    if is_bool:
        return conf_obj.getboolean(sect, vparam)
    else:
        return conf_obj.get(sect, vparam)


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
    return ctx


def create_params_dict(ctx):
    """Create all params dictionary"""
    ctx = create_def_params_dict(ctx)
    DEFDCT = default_conf(ctx)
    if ctx['dbg_mode'] is None:
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
    if opt_obj.dbfilter != "":
        ctx['dbfilter'] = opt_obj.dbfilter
        ctx['multi_db'] = True
    if opt_obj.upgrade_modules:
        ctx['upgrade_modules'] = opt_obj.upgrade_modules
    if opt_obj.data_path != "":
        ctx['data_path'] = opt_obj.data_path
    if ctx['db_host'] == 'False':
        ctx['db_host'] = 'localhost'
    if not ctx['svc_protocol']:
        if ctx['oe_version'] in ('9.0', '10.0', '11.0'):
            ctx['svc_protocol'] = 'jsonrpc'
        else:
            ctx['svc_protocol'] = 'xmlrpc'
    return ctx


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


def read_config(ctx):
    """Read both user configuration and local configuration."""
    if not ctx.get('conf_fn', None):
        ctx['conf_fn'] = "./" + ctx['caller'] + ".conf"
    conf_obj = ConfigParser.SafeConfigParser(default_conf(ctx))
    ctx['conf_fns'] = []
    if ODOO_CONF:
        if isinstance(ODOO_CONF, list):
            for f in ODOO_CONF:
                if os.path.isfile(f):
                    ctx['conf_fns'].append(f)
                    break
        elif os.path.isfile(ODOO_CONF):
            ctx['conf_fns'].append(ODOO_CONF)
        elif os.path.isfile(OE_CONF):
            ctx['conf_fns'].append(OE_CONF)
        if CONF_FN and CONF_FN not in ctx['conf_fns']:
            ctx['conf_fns'].append(CONF_FN)
        if ctx['conf_fn'] not in ctx['conf_fns']:
            ctx['conf_fns'].append(ctx['conf_fn'])
    ctx['conf_fns'] = conf_obj.read(ctx['conf_fns'])
    ctx['_conf_obj'] = conf_obj
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
        epilog="© 2015-2018 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-A", "--action-to-do",
                        help="action to do (use list_actions to dir)",
                        dest="do_sel_action",
                        metavar="actions",
                        default=None)
    parser.add_argument("-b", "--odoo-branch",
                        help="talk server Odoo version",
                        dest="oe_version",
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
    parser.add_argument("-D", "--with-demo",
                        help="create db with demo data",
                        action="store_true",
                        dest="with_demo",
                        default=False)
    parser.add_argument("-l", "--lang",
                        help="user language",
                        dest="lang",
                        metavar="iso_lang",
                        default='en_US')
    parser.add_argument("-n", "--dry-run",
                        help="test execution mode",
                        action="store_true",
                        dest="dry_run",
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
                        default=None)
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
    parser.add_argument("-U", "--user",
                        help="login username",
                        dest="lgi_user",
                        metavar="username",
                        default=None)
    parser.add_argument("-u", "--upgrade-modules",
                        help="Module list to upgrade",
                        dest="upgrade_modules",
                        metavar="list",
                        default="")
    parser.add_argument("-v", "--verbose",
                        help="run with debugging output",
                        action="store_true",
                        dest="dbg_mode",
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + version)
    return parser


def parse_args(arguments,
               apply_conf=APPLY_CONF, version=None, tlog=None, doc=None):
    """Parse command-line options."""
    ctx = {}
    caller_fqn = inspect.stack()[1][1]
    ctx['caller_fqn'] = caller_fqn
    caller = os0.nakedname(os.path.basename(caller_fqn))
    ctx['caller'] = caller
    if os.isatty(0):
        ctx['run_daemon'] = False
    else:
        ctx['run_daemon'] = True
    ctx['run_tty'] = os.isatty(0)
    if tlog:
        ctx['tlog'] = tlog
    else:
        ctx['tlog'] = "./" + caller + ".log"
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
        ctx = read_config(ctx)
        opt_obj = parser.parse_args(arguments)
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
