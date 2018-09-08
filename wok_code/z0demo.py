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
# For software version see builder.version
"""Update Odoo demo files in order to build Italian Demo for Zeroincombenze(R)
"""

# import pdb
import os
import sys
import argparse
import inspect
import ConfigParser
from shutil import copyfile
# import re

# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = False
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
# Warning: if following LX have no values LX=(), if have 1 value LX=(value,)
# list of string parameters in [options] of config file
LX_CFG_S = ('demo_files_dir',
            'demo_files',
            'xtl_file')
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ()
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_S = ('dbg_mode',
            'quiet_mode',
            'dry_run')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_B = ('dbg_mode',
            'quiet_mode',
            'dry_run')
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


__version__ = "0.1.1"


def str2bool(t, dflt):
    """Convert text to bool"""
    if isinstance(t, bool):
        return t
    elif t.lower() in ["true", "t", "1", "y", "yes", "on", "enabled"]:
        return True
    elif t.lower() in ["false", "f", "0", "n", "no", "off", "disabled"]:
        return False
    else:
        return dflt


def nakedname(fn):
    """Return nakedename (without extension)"""
    i = fn.rfind('.')
    if i >= 0:
        j = len(fn) - i
        if j <= 4:
            fn = fn[:i]
    return fn


#############################################################################
def default_conf(ctx):
    """Default configuration values"""
    DEFDCT = {}
    DEFDCT['demo_files_dir'] = '/opt/odoo/v7/addons/account/demo'
    DEFDCT['demo_files'] = 'account_minimal.xml' + \
        ',account_invoice_demo.xml,account_demo.xml'
    DEFDCT['xtl_file'] = './z0demo.xtl'
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
                ctx[p] = str2bool(getattr(opt_obj, p), None)
        for p in LX_OPT_N:
            if hasattr(opt_obj, p) and getattr(opt_obj, p):
                ctx[p] = int(getattr(opt_obj, p))
    for p in LX_CFG_SB:
        ctx[p] = str2bool(ctx[p], ctx[p])
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
    # opt_obj = ctx.get('_opt_obj', None)
    s = "options"
    if not conf_obj.has_section(s):
        conf_obj.add_section(s)
    for p in ():
        ctx[p] = conf_obj.getint(s, p)
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
        epilog="© 2016 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-c", "--config",
                        help="File di configurazione",
                        dest="conf_fn",
                        metavar="file",
                        default=CONF_FN)
    parser.add_argument("-n", "--dry_run",
                        help="esecuzione di prova",
                        action="store_true",
                        dest="dry_run",
                        default=False)
    parser.add_argument("-q", "--quiet",
                        help="esecuzione silenziosa",
                        action="store_true",
                        dest="quiet_mode",
                        default=False)
    parser.add_argument("-v", "--verbose",
                        help="informazioni durante esecuzione",
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
    caller = nakedname(os.path.basename(caller_fqn))
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


class Demo:

    def __init__(self):
        pass

    def update_files(self, ctx):
        demo_files_dir = ctx['demo_files_dir']
        file_list = ctx['demo_files'].split(',')
        xtl_file = ctx['xtl_file']
        for f in file_list:
            fqn = os.path.join(demo_files_dir, f)
            orig_fn = fqn + '.orig'
            if not os.path.isfile(orig_fn):
                copyfile(fqn, orig_fn)
            self.update_1_file(orig_fn, fqn, xtl_file)
        return 0

    def update_1_file(self, src, tgt, xtl):
        pass


if __name__ == "__main__":
    sts = 0
    ctx = parse_args(sys.argv[1:],
                     apply_conf=APPLY_CONF,
                     version=__version__,
                     doc=__doc__)
    demo = Demo()
    sts = demo.update_files(ctx)
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
