# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
"""Clodoo common library
"""

import os
from datetime import date
import time
# import platform
import argparse
import inspect
import ConfigParser
from os0 import os0
import re

# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = "./clodoo.conf"
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = ["/etc/odoo/odoo-server.conf",
             "/etc/odoo-server.conf",
             "/etc/openerp/openerp-server.conf",
             "/etc/openerp-server.conf",
             "/etc/odoo/openerp-server.conf",
             "/etc/openerp/odoo-server.conf"]
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
            'actions',
            'actions_db',
            'actions_mc',
            'actions_uu',
            'heavy_trx',
            'install_modules',
            'uninstall_modules',
            'upgrade_modules',
            'chart_of_account')
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
            'setup_banks',
            'setup_account_journal',
            'setup_partners',
            'setup_partner_banks',
            'check_config')
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_S = ('dbg_mode', 'do_sel_action', 'dry_run', 'lgi_user', 'lgi_pwd',
            'logfn', 'quiet_mode')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_B = ()
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

__version__ = "0.1.3"


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
        except:
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
        except:
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
              'login_password': 'admin',
              'login2_user': 'admin',
              'login2_password': 'admin',
              'db_host': 'localhost',
              'svc_protocol': 'xmlrpc',
              'xmlrpc_port': '8069',
              'dbfilter': '.*',
              'dbfilterd': 'demo',
              'dbfiltert': 'openerp.*',
              'dbfilterz': 'zi[0-9]{8}',
              'dbtypefilter': '',
              'companyfilter': '.*',
              'userfilter': '.*',
              'lang': 'en_US',
              'date_start': dts_start,
              'date_stop': dts_stop,
              'adm_uids': '1',
              'set_passepartout': '0',
              'check_balance': '0',
              'setup_banks': '0',
              'setup_account_journal': '0',
              'setup_partners': '0',
              'setup_partner_banks': '0',
              'check_config': '0',
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
              'chart_of_account': 'configurable_chart_template'}
    return DEFDCT


def create_def_params_dict(ctx):
    """Create default params dictionary"""
    opt_obj = ctx.get('_opt_obj', None)
    conf_obj = ctx.get('_conf_obj', None)
    s = "options"
    if conf_obj:
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
        for p in LX_CFG_S:
            ctx[p] = conf_obj.get(s, p)
        for p in LX_CFG_B:
            ctx[p] = conf_obj.getboolean(s, p)
    else:
        DEFDCT = default_conf(ctx)
        for p in LX_CFG_S:
            if p in DEFDCT:
                ctx[p] = DEFDCT[p]
        for p in LX_CFG_B:
            if p in DEFDCT:
                ctx[p] = DEFDCT[p]
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
                ctx[p] = getattr(opt_obj, p)
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
    if not conf_obj.has_section(s):
        conf_obj.add_section(s)
    ctx['db_pwd'] = conf_obj.get(s, "db_password")
    for p in ():
        ctx[p] = conf_obj.getint(s, p)
    if opt_obj.dbfilter != "":
        ctx['dbfilter'] = opt_obj.dbfilter
        ctx['multi_db'] = True
    if opt_obj.data_path != "":
        ctx['data_path'] = opt_obj.data_path
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
        if CONF_FN:
            ctx['conf_fn'] = CONF_FN
        else:
            ctx['conf_fn'] = "./" + ctx['caller'] + ".conf"
    conf_obj = ConfigParser.SafeConfigParser(default_conf(ctx))
    if ODOO_CONF:
        if isinstance(ODOO_CONF, list):
            found = False
            for f in ODOO_CONF:
                if os.path.isfile(f):
                    ctx['conf_fns'] = (f, ctx['conf_fn'])
                    found = True
                    break
            if not found:
                ctx['conf_fns'] = ctx['conf_fn']
        else:
            if os.path.isfile(ODOO_CONF):
                ctx['conf_fns'] = (ODOO_CONF, ctx['conf_fn'])
            elif os.path.isfile(OE_CONF):
                ctx['conf_fns'] = (OE_CONF, ctx['conf_fn'])
            else:
                ctx['conf_fns'] = ctx['conf_fn']
    else:
        ctx['conf_fns'] = ctx['conf_fn']
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
        epilog="© 2015 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-A", "--list-actions",
                        help="do nothig, list actions",
                        dest="do_sel_action",
                        metavar="action",
                        default=None)
    parser.add_argument("-c", "--config",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default=CONF_FN)
    parser.add_argument("-d", "--dbfilter",
                        help="DB filter",
                        dest="dbfilter",
                        metavar="regex",
                        default="")
    parser.add_argument("-n", "--dry_run",
                        help="test execution mode",
                        action="store_true",
                        dest="dry_run",
                        default=False)
    parser.add_argument("-p", "--data_path",
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
    # parser.add_argument("filesrc",
    #                     help="Files to convert")
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
