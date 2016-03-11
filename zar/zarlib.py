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
import argparse
import ConfigParser
from os0 import os0

# Apply for configuration file (True/False)
APPLY_CONF = False
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = False
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
# Warning: if following LX have no values LX=(), if have 1 value LX=(value,)
# list of string parameters in [options] of config file
LX_CFG_S = ()
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ()
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_CFG_S = ('dbg_mode', 'db_name', 'dry_run')
DEFDCT = {}


def default_conf():
    """Default configuration values"""
    DEFDCT = {}
    a = os0.nakedname(os.path.basename(__file__))
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
    DEFDCT['appname'] = a
    DEFDCT['bckapp'] = b
    DEFDCT['restapp'] = r
    return DEFDCT


def create_def_params_dict(opt_obj, conf_obj):
    """Create default params dictionary"""
    ctx = {}
    s = "options"
    if conf_obj:
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
        for p in LX_CFG_S:
            ctx[p] = conf_obj.get(s, p)
        for p in LX_CFG_B:
            ctx[p] = conf_obj.getboolean(s, p)
    for p in LX_CFG_SB:
        ctx[p] = os0.str2bool(ctx[p], ctx[p])
    for p in LX_OPT_CFG_S:
        if hasattr(opt_obj, p):
            ctx[p] = getattr(opt_obj, p)
    return ctx


def create_params_dict(opt_obj, conf_obj):
    """Create all params dictionary"""
    ctx = create_def_params_dict(opt_obj, conf_obj)
    # s = "options"
    for p in ('alt', ):
        if hasattr(opt_obj, p):
            ctx[p] = getattr(opt_obj, p)
    ctx['_conf_obj'] = conf_obj
    ctx['_opt_obj'] = opt_obj
    return ctx


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


def read_config(opt_obj, parser, conf_fn=None):
    """Read both user configuration and local configuration."""
    if conf_fn is None or not conf_fn:
        if CONF_FN:
            conf_fn = CONF_FN
        else:
            conf_fn = os0.nakedname(os.path.basename(__file__)) + ".conf"
    conf_obj = ConfigParser.SafeConfigParser(default_conf())
    if ODOO_CONF:
        if os.path.isfile(ODOO_CONF):
            conf_fns = (ODOO_CONF, conf_fn)
        elif os.path.isfile(OE_CONF):
            conf_fns = (OE_CONF, conf_fn)
        else:
            conf_fns = conf_fn
    else:
        conf_fns = conf_fn
    conf_fns = conf_obj.read(conf_fns)
    return conf_obj, conf_fns


def create_parser():
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
        description=docstring_summary(__doc__),
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
    parser.add_argument("-c", "--conf",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default=".zar.conf")
    parser.add_argument("-d", "--dbname",
                        help="single db operation",
                        dest="db_name",
                        metavar="file",
                        default="")
    parser.add_argument("-L", "--list",
                        help="list configuration saveset names",
                        action="store_true",
                        dest="list",
                        default=False)
    parser.add_argument("-n", "--dry_run",
                        help="test execution mode",
                        action="store_true",
                        dest="dry_run",
                        default=False)
    parser.add_argument("-q", "--quiet",
                        help="run without output",
                        action="store_true",
                        dest="mute",
                        default=False)
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
                        # version="%(prog)s " + __version__)
                        version="%(prog)s ")
    parser.add_argument("saveset",
                        help="saveset",
                        nargs='?')
    return parser


def parse_args(arguments, apply_conf=False, version=None, tlog=None):
    """Parse command-line options."""
    parser = create_parser()
    opt_obj = parser.parse_args(arguments)
    if apply_conf:
        if hasattr(opt_obj, 'conf_fn'):
            conf_fns = opt_obj.conf_fn
            conf_obj, conf_fns = read_config(opt_obj,
                                             parser,
                                             conf_fn=conf_fns)
        else:
            conf_obj, conf_fns = read_config(opt_obj,
                                             parser)
        opt_obj = parser.parse_args(arguments)
    else:
        conf_obj = None
    ctx = create_params_dict(opt_obj, conf_obj)
    if 'conf_fns' in locals():
        ctx['conf_fn'] = conf_fns
    ctx['_parser'] = parser
    return ctx


class ZarLib:

    def __init__(self):
        pass
