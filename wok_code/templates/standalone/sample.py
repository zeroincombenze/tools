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
     Prototypes builder
     Creates prototype files for a new module named 'prototypes'.
     Run as schell script, not as web application (see 1.st line in this file)

"""

# import pdb
import os.path
import sys
import argparse
import ConfigParser
from pytok import pytok


__version__ = "0.1.3"
# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
ODOO_CONF = "/etc/odoo-server.conf"
OE_CONF = "/etc/openerp-server.conf"


class Builder():

    def __init__(self):
        pass

    def list_paths(self, prm):
        self.get_odoo_conf(prm)
        for i, p in enumerate(self.odoo_math):
            print i, p
        return 0

    def install_new_module(self, prm):
        self.get_odoo_conf(prm)
        if len(self.odoo_math) == 1:
            prm['module_path'] = self.odoo_math[0]
        elif prm['sel_path']:
            prm['module_path'] = self.odoo_math[prm['sel_path']]
        else:
            print('Invalid pathname for module {0}!'.format(prm['modname']))
            print('  use --path option')
            return
        print ('Module {0}->{1}'.format(prm['modname'],
                                        prm['module_path']))

    def get_odoo_conf(self, prm):
        if 'odoo_conf' in prm:
            odoo_conf = prm['odoo_conf']
        else:
            odoo_conf = "/etc/openerp-server.conf"
        odoo_cfg_obj = ConfigParser.SafeConfigParser()
        s = "options"
        if not odoo_cfg_obj.has_section(s):
            odoo_cfg_obj.add_section(s)
        odoo_cfg_obj.read(odoo_conf)
        mpath = odoo_cfg_obj.get(s, "addons_path")
        self.odoo_math = mpath.split(',')
        return odoo_cfg_obj

    def mkdir(self, prm):
        # modname = prm['modname']
        self.get_odoo_conf(prm)

    def build_standalone(self, prm):
        prm['pyname'] = prm['module'] + '.py'
        prm['pytmp'] = './midea/' + prm['module'] + '.py'
        src = pytok.open(__file__)
        src.decl_options(prm)
        src.parse_src()
        tgt_fd = open(prm['pytmp'], 'w')
        tgt_fd.write(src.tostring())
        tgt_fd.close()
        return 0

    def build_prgm(self, prm):
        if not prm.get('module'):
            return 1
        conf_obj = prm['_conf_obj']
        if prm['template'] and conf_obj.has_section(prm['template']):
            return self.build_standalone(prm)
        else:
            print "Invalid template", prm['template']
            return 1
Builder()


#############################################################################
# Custom parser functions
#
def default_conf():
    """Default configuration values"""
    d = {'has_wizard': 'False',
         'has_demo': 'False',
         'module': 'midea',
         'module_shortname': None,
         'menuitem': None,
         'menutext': None,
         'template': 'standalone',
         'inclass': '.*',
         'infun': 'default_conf,create_parser,'
         'nakedname,docstring_summary,'
         'parse_args,read_config,'
         'main',
         'token': '.*'}
    return d


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

    parser.add_argument("-b", "--build",
                        help="build module or program",
                        action="store_true",
                        dest="o_build",
                        default=False)
    parser.add_argument("-c", "--config",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default=CONF_FN)
    parser.add_argument("-i", "--install",
                        help="module paths",
                        action="store_true",
                        dest="o_install",
                        default=False)
    parser.add_argument("-l", "--list",
                        help="show module paths",
                        action="store_true",
                        dest="o_list",
                        default=False)
    parser.add_argument("-n", "--name",
                        help="module name",
                        dest="modname",
                        metavar="name",
                        default="midea")
    parser.add_argument("-p", "--path",
                        help="select path number",
                        dest="sel_path",
                        metavar="int",
                        default=None)
    parser.add_argument("-q", "--quiet",
                        help="run silently",
                        action="store_true",
                        dest="quiet_mode",
                        default=False)
    parser.add_argument("-t", "--dry_run",
                        help="test execution mode",
                        action="store_true",
                        dest="simulate",
                        default=False)
    parser.add_argument("-T", "--template",
                        help="template to use",
                        dest="name",
                        metavar="template",
                        default=None)
    parser.add_argument("-v", "--verbose",
                        help="run with debugging output",
                        action="store_true",
                        dest="dbg_mode",
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + __version__)
    return parser


def create_params_dict(opt_obj, conf_obj):
    """Create all params dictionary"""
    prm = {}
    s = "options"
    if not conf_obj.has_section(s):
        conf_obj.add_section(s)
    for p in ('template',
              'inclass',
              'infun',
              'token',
              'module',
              'module_shortname',
              'menuitem',
              'menutext'):
        prm[p] = conf_obj.get(s, p)

    for p in ('has_wizard',
              'has_demo'):
        prm[p] = conf_obj.getboolean(s, p)

    prm['modname'] = opt_obj.modname
    prm['sel_path'] = opt_obj.sel_path
    prm['simulate'] = opt_obj.simulate
    prm['dbg_mode'] = opt_obj.dbg_mode
    prm['quiet_mode'] = opt_obj.quiet_mode
    if prm['modname']:
        prm['module'] = prm['modname']
    if not prm['module_shortname']:
        prm['module_shortname'] = prm['module']

    if hasattr(opt_obj, 'template'):
        prm['template'] = opt_obj.template
    if opt_obj.o_list:
        prm['action'] = 'list'
    elif opt_obj.o_install:
        prm['action'] = 'install'
    elif opt_obj.o_build:
        prm['action'] = 'build'
    else:
        prm['action'] = 'help'
    prm['no_num_line'] = True
    prm['no_header'] = True
    prm['no_inherit'] = True
    prm['_conf_obj'] = conf_obj
    prm['_opt_obj'] = opt_obj

    s = "standalone"
    if not conf_obj.has_section(s):
        conf_obj.add_section(s)

    return prm


#############################################################################
# Common parser functions
#
def nakedname(fn):
    """Return nakedename (without extension)"""
    i = fn.rfind('.')
    if i >= 0:
        j = len(fn) - i
        if j <= 4:
            fn = fn[:i]
    return fn


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
            conf_fn = opt_obj.conf_fn
            conf_obj, conf_fn = read_config(opt_obj, parser, conf_fn=conf_fn)
        else:
            conf_obj, conf_fn = read_config(opt_obj, parser)
        opt_obj = parser.parse_args(arguments)
    prm = create_params_dict(opt_obj, conf_obj)
    if 'conf_fn' in globals():
        prm['conf_fn'] = conf_fn
    prm['_parser'] = parser
    return prm


def read_config(opt_obj, parser, conf_fn=None):
    """Read both user configuration and local configuration."""
    if conf_fn is None or not conf_fn:
        if CONF_FN:
            conf_fn = CONF_FN
        else:
            conf_fn = nakedname(os.path.basename(__file__)) + ".conf"
    d = default_conf()
    conf_obj = ConfigParser.SafeConfigParser(d)
    if ODOO_CONF:
        if os.path.isfile(ODOO_CONF):
            conf_fns = (ODOO_CONF, conf_fn)
        elif os.path.isfile(OE_CONF):
            conf_fns = (OE_CONF, conf_fn)
        else:
            conf_fns = conf_fn
    else:
        conf_fns = conf_fn
    conf_obj.read(conf_fns)
    return conf_obj, conf_fn


def main():
    """Tool main"""
    sts = 0
    prm = parse_args(sys.argv[1:], apply_conf=APPLY_CONF)
    B = Builder()
    if prm['action'] == "list":
        sts = B.list_paths(prm)
    elif prm['action'] == "install":
        sts = B.install_new_module(prm)
    elif prm['action'] == "build":
        sts = B.build_prgm(prm)
    else:
        prm['_parser'].print_usage()
    return sts

if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
