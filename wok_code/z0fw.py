#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
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
     Little firewall

"""

# import pdb
import os
import os.path
import sys
import argparse
import ConfigParser
from os0 import os0


__version__ = "0.1.2"
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
LX_CFG_S = ()
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ()
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_CFG_S = ('simulate',)
DEFDCT = {}


def version():
    return __version__


#############################################################################
# Custom parser functions
#
def default_conf():
    """Default configuration values"""
    return DEFDCT


def create_parser():
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
        description=docstring_summary(__doc__),
        epilog="© 2015 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org")
    parser.add_argument("-t", "--dry_run",
                        help="test execution mode",
                        action="store_true",
                        dest="simulate",
                        default=False)

    return parser


def create_params_dict(opt_obj, conf_obj):
    """Create all params dictionary"""
    prm = create_def_params_dict(opt_obj, conf_obj)

    # s = "options"

    prm['_conf_obj'] = conf_obj
    prm['_opt_obj'] = opt_obj
    return prm


#############################################################################
# Common parser functions
#

def create_def_params_dict(opt_obj, conf_obj):
    """Create default params dictionary"""
    prm = {}
    s = "options"
    if conf_obj:
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
        for p in LX_CFG_S:
            prm[p] = conf_obj.get(s, p)
        for p in LX_CFG_B:
            prm[p] = conf_obj.getboolean(s, p)
    for p in LX_CFG_SB:
        prm[p] = os0.str2bool(prm[p], prm[p])
    for p in LX_OPT_CFG_S:
        if hasattr(opt_obj, p):
            prm[p] = getattr(opt_obj, p)
    return prm


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


def parse_args(arguments, apply_conf=False):
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
    prm = create_params_dict(opt_obj, conf_obj)
    if 'conf_fns' in locals():
        prm['conf_fn'] = conf_fns
    prm['_parser'] = parser
    return prm


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


class Fw():
    def __init__(self, prm):
        self.simulate = prm['simulate']

    def analyze(self, prm):
        cmd = "netstat -nat | awk '{print $6}' | sort | uniq -c | sort -n"
        os0.muteshell(cmd, simulate=self.simulate, keepout=True)
        stdinp_fd = open(os0.setlfilename(os0.bgout_fn), 'r')
        line = stdinp_fd.readline()
        total_conn = 0
        total_dos_conn = 0
        total_overload = 0
        while line != "":
            fields = line.strip().split()
            # Check for DOS attack
            if fields[1] == "SYS_SENT":
                total_dos_conn += int(fields[0])
            # Check for overload
            elif fields[1] == "SYN_RECV" or fields[1] == "TIME_WAIT":
                total_overload += int(fields[0])
            total_conn += int(fields[0])
            line = stdinp_fd.readline()
        stdinp_fd.close()
        try:
            os.remove(os0.setlfilename(os0.bgout_fn))
        except:
            pass
        perc_dos_conn = (total_dos_conn * 100) / total_conn
        perc_overload = (total_overload * 100) / total_conn
        prm['total_conn'] = total_conn
        prm['total_dos_conn'] = total_dos_conn
        prm['total_overload'] = total_overload
        prm['perc_dos_conn'] = perc_dos_conn
        prm['perc_overload'] = perc_overload
        return prm


def main():
    """Tool main"""
    sts = 0
    # pdb.set_trace()
    prm = parse_args(sys.argv[1:])
    fw = Fw(prm)
    prm = fw.analyze(prm)
    print "Total connecction.........: %d" % prm['total_conn']
    print "Total DOS connections.....: %d (%d%%)" % (prm['total_dos_conn'],
                                                     prm['perc_dos_conn'])
    print "Total overload connections: %d (%d%%)" % (prm['total_overload'],
                                                     prm['perc_overload'])
    if prm['perc_dos_conn'] > 50 or prm['perc_overload'] > 50:
        sts = 1
    return sts

if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
