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
"""ZAR common library
"""

import os
import platform
import argparse
import inspect
import ConfigParser
import re
try:
    from os0 import os0
except ImportError:
    import os0


# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = "./zar.conf"
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False


# Warning: if following LX have no values LX=(), if have 1 value LX=(value,)
# list of string parameters in [options] of config file
LX_CFG_S = ('saveset_list',
            'hostname',
            'production_host',
            'development_host',
            'mirror_host',
            'ftp_script',
            'list_file',
            'tlog',
            'pg_dir',
            'mysql_dir',
            'data_translation',
            'no_translation',
            'tar_ext',
            'tar_opt',
            'pre_ext',
            'sql_ext',
            'pgsql_user',
            'pgsql_pwd',
            'pgsql_def_db',
            'mysql_user',
            'mysql_pwd',
            'mysql_def_db')
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ()
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_S = ('dbg_mode', 'db_name', 'dry_run', 'saveset', 'logfn', 'x_db_name')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_B = ('alt', 'xtall', 'do_list')
# List of numeric parameters in line command; may be in LX_CFG_S list too
LX_OPT_N = ()
# list of opponent options
LX_OPT_OPPONENT = {'dbg_mode': 'verbose'}
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_S
LX_SB = ()
# switch values of options
LX_OPT_ARGS = {}
DEFDCT = {}

__version__ = "1.3.34"


def default_conf(ctx):
    """Default configuration values"""
    DEFDCT = {}
    a = ctx['caller']
    if a[0:4] == "rest":
        b = "bck" + a[4:]
    elif a[0:3] == "bck":
        b = a
    else:
        b = a + "_bck"
    if a[0:3] == "bck":
        r = "rest" + a[3:]
    elif a[0:4] == "rest":
        r = a
    else:
        r = a + "_rest"
    DEFDCT = {"saveset_list": "bckdb,restdb,bckconf,restconf",
              "appname": a,
              "bckapp": b,
              "restapp": r,
              "specimen": "file",
              "production_host": "shsdef16",
              "development_host": "shsita16",
              "mirror_host": "shsprd14",
              "ftp_script": a + ".ftp",
              "list_file": b + ".ls",
              "tlog": "/var/log/" + a + ".log",
              "data_translation": "restconf.ini",
              "no_translation": "restconf-0.ini",
              "debug": ctx.get('run_daemon', True),
              # May be (.gz or .bz2)
              "tar_ext": ".gz",
              # May be (z or j)
              "tar_opt": "z",
              # May be (null or .sql)
              "pre_ext": ".sql",
              # May be (null or .sql)
              "sql_ext": ".sql",
              "pgsql_user": "postgres",
              "mysql_user": "mysql",
              "pgsql_def_db": "postgres",
              "mysql_def_db": "mysql"}
    found = False
    for fn in ("pgsql", "postgresql"):
        pn = "/var/lib/" + fn
        if os.path.isdir(pn):
            for v in ("8.4", "9.0", "9.1", "9.2", "9.3", "9.4"):
                pn = "/var/lib/" + fn + "/" + v
                if os.path.isdir(pn):
                    found = True
                    break
            pn = "/var/lib/" + fn
            found = True
            break
    if found:
        DEFDCT["pg_dir"] = pn
    else:
        DEFDCT["pg_dir"] = ""
    if os.path.isdir("/var/lib/mysql"):
        DEFDCT["mysql_dir"] = "/var/lib/mysql"
    else:
        DEFDCT["mysql_dir"] = ""
    DEFDCT["hostname"] = platform.node()
    return DEFDCT


def create_def_params_dict(ctx):
    """Create default params dictionary"""
    opt_obj = ctx.get('_opt_obj', None)
    conf_obj = ctx.get('_conf_obj', None)
    # s = "options"
    s = "Environment"
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
    conf_obj = ctx.get('_conf_obj', None)
    if ctx['dbg_mode'] is None:
        ctx['dbg_mode'] = ctx['run_daemon']
    if ctx['saveset'] is None:
        ctx['saveset'] = ctx['caller']
    if not ctx['logfn'] or ctx['logfn'] == '':
        if 'tlog' in ctx:
            ctx['logfn'] = ctx['tlog']
        else:
            ctx['logfn'] = "~/" + ctx['caller'] + ".log"
    if ctx['saveset']:
        s = ctx['saveset'].strip()
        if conf_obj.has_section(s):
            pass
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
    -n --dry-run    simulation mode for test (dry_run)
    -q --quiet      quiet mode
    -U --user       set username (user)
    -v --verbose    verbose mode (dbg_mode)
    -V --version    show version
    -y --yes        confirmation w/out ask
    """
    parser = argparse.ArgumentParser(
        description=docstring_summary(doc),
        epilog="© 2015-2016 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-0", "--install",
                        help="install & configure",
                        action="store_true",
                        dest="xtall",
                        default=False)
    parser.add_argument("-A", "--alternate",
                        help="backup on alternate host",
                        action="store_true",
                        dest="alt",
                        default=False)
    parser.add_argument("-c", "--config",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default=CONF_FN)
    parser.add_argument("-d", "--dbname",
                        help="single db operation",
                        dest="db_name",
                        metavar="file",
                        default="")
    parser.add_argument("-l", "--logname",
                        help="set logfile name",
                        dest="logfn",
                        metavar="file")
    parser.add_argument("-L", "--list",
                        help="list configuration saveset names",
                        action="store_true",
                        dest="do_list",
                        default=False)
    parser.add_argument("-n", "--dry_run",
                        help="test execution mode",
                        action="store_true",
                        dest="dry_run",
                        default=False)
    parser.add_argument("-q", "--quiet",
                        help="run without output",
                        action="store_false",
                        dest="verbose",
                        default=True)
    parser.add_argument("-s", "--select",
                        help="saveset to backup/restore",
                        dest="saveset",
                        metavar="saveset")
    parser.add_argument("-v", "--verbose",
                        help="run with a lot of debugging output",
                        action="store_true",
                        dest="dbg_mode",
                        # default=dbg_mode)
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + version)
    parser.add_argument("-x", "--exclude",
                        help="exclude DB",
                        dest="x_db_name",
                        metavar="file",
                        default="")
    parser.add_argument("saveset",
                        help="saveset",
                        nargs='?')
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
        ctx['tlog'] = "/var/log/" + caller + ".log"
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
