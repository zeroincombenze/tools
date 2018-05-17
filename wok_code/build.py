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
import os
import os.path
import sys
import argparse
import ConfigParser
from pytok import pytok
from os0 import os0


__version__ = "0.1.16"
# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = False
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = "/etc/odoo-server.conf"
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = "/etc/openerp-server.conf"
# Warning: if following LX have no values LX=(), if have 1 value LX=(value,)
# list of string parameters in [options] of config file
LX_CFG_S = ('template',
            'inclass',
            'infun',
            'token',
            'module',
            'module_shortname',
            'menuitem',
            'menutext')
# list of string/boolean parameters in [options] of config file
# Must be declared in LX_CFG_S
LX_CFG_SB = ()
# list of pure boolean parameters in [options] of config file
LX_CFG_B = ('has_wizard',
            'has_demo')
# list of string parameters in both [options] of config file and line command
# or else are just in line command
LX_OPT_CFG_S = ('modname',
                'sel_path',
                'simulate',
                'dbg_mode',
                'quiet_mode',
                'template')
DEFDCT = {'has_wizard': 'False',
          'has_demo': 'False',
          'module': 'midea',
          'module_shortname': None,
          'menuitem': None,
          'menutext': None,
          'template': 'standalone',
          'inclass': '.*',
          'infun': '.*',
          'token': '.*'}


def version():
    return __version__


class Builder():

    def __init__(self):
        pass

    def echo(self, *args):
        # for p in args:
        #     print p,
        # print
        os0.wlog(args)

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

    def copybinfile(self, prm, tgtfile, srcfile):
        self.echo('copybinfile(', tgtfile, '=', srcfile, ')')
        src_fd = open(srcfile, 'rb')
        tgt_fd = open(tgtfile, 'wb')
        tgt_fd.write(src_fd.read())
        tgt_fd.close()
        src_fd.close()
        return 0

    def copypyfile(self, prm, tgtfile, srcfile):
        self.echo('copypyfile(', tgtfile, '=', srcfile, ')')
        conf_obj = prm['_conf_obj']
        s = os.path.basename(srcfile)
        if conf_obj.has_section(s):
            for p in ('inclass',
                      'infun',
                      'token'):
                if conf_obj.has_option(s, p):
                    prm[p] = conf_obj.get(s, p)
                self.echo('> prm[', p, ']=', prm[p], ")")
        src = pytok.open(srcfile)
        src.decl_options(prm)
        src.parse_src()
        tgt_fd = open(tgtfile, 'w')
        tgt_fd.write(src.tostring())
        tgt_fd.close()
        return 0

    def copyfile(self, prm, tgtfile, srcfile):
        if srcfile[-3:] == '.py':
            return self.copypyfile(prm, tgtfile, srcfile)
        else:
            return self.copybinfile(prm, tgtfile, srcfile)

    def mktree(self, prm, tgt_path, src_path):
        self.echo('mktree(', tgt_path, '=', src_path, ')')
        sts = 0
        for f in os.listdir(src_path):
            tgtfile = tgt_path + '/' + f
            srcfile = src_path + '/' + f
            if os.path.isfile(srcfile):
                sts = sts or self.copyfile(prm, tgtfile, srcfile)
            else:
                if not os.path.isdir(tgtfile):
                    self.echo('mkdir(', tgtfile, ')')
                    os.mkdir(tgtfile)
                sts = sts or self.mktree(prm, tgtfile, srcfile)
        return sts

    def build_tree(self, prm):
        tpl_path = prm['tpl_path']
        tgt_path = prm['tgt_path']
        return self.mktree(prm, tgt_path, tpl_path)

    def build_prgm(self, prm):
        if not prm.get('module'):
            return 1
        conf_obj = prm['_conf_obj']
        if prm['template'] and conf_obj.has_section(prm['template']):
            prm['tpl_path'] = './templates/' + prm['template']
            prm['tgt_path'] = './building'
            s = prm['template']
            p = 'config_fn'
            if conf_obj.has_option(s, p):
                tpl_config_fn = conf_obj.get(s, p)
            else:
                tpl_config_fn = prm['template'] + ".conf"
            tpl_config_ffn = prm['tpl_path'] + '/' + tpl_config_fn
            if os.path.isfile(tpl_config_ffn):
                conf_obj = ConfigParser.SafeConfigParser(default_conf())
                conf_fns = prm['conf_fn']
                if isinstance(prm['conf_fn'], list):
                    conf_fns = prm['conf_fn']
                    conf_fns.append(tpl_config_ffn)
                else:
                    conf_fns = [prm['conf_fn'], tpl_config_ffn]
                conf_obj.read(conf_fns)
            prm['logfile'] = os.path.abspath(prm['tpl_path'] +
                                             '/_' + prm['module'] + '.log')
            os0.set_tlog_file(prm['logfile'], echo=True)
            return self.build_tree(prm)
        else:
            print "Invalid template", prm['template']
            return 1
Builder()


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
                        dest="template",
                        metavar="name",
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
    prm = create_def_params_dict(opt_obj, conf_obj)

    s = "options"
    if prm['modname']:
        prm['module'] = prm['modname']
    if not prm.get('module_shortname', None):
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

    if conf_obj:
        # default template standalone
        s = "standalone"
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
            conf_obj.set(s, 'inclass', '.*')
            conf_obj.set(s, 'infun', '.*')
            conf_obj.set(s, 'token', '.*')

        # default template pypi
        s = "pypi"
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
            conf_obj.set(s, 'inclass', '.*')
            v = 'default_conf,create_parser,'
            v += 'docstring_summary,'
            v += 'parse_args,read_config,main'
            conf_obj.set(s, 'infun', v)
            conf_obj.set(s, 'token', '.*')

        # default template odoo
        s = "odoo"
        if not conf_obj.has_section(s):
            conf_obj.add_section(s)
            conf_obj.set(s, 'inclass', '.*')
            conf_obj.set(s, 'infun', '.*')
            conf_obj.set(s, 'token', '.*')

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
