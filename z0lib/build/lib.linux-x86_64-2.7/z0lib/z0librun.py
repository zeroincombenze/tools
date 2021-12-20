# -*- coding: utf-8 -*-
"""@mainpage
Zeroincombenze® general purpose library
=======================================

Library with various functionalities for python and bash programs.
Area managed:
- parseoptargs: line command parser; expands python argparse and adds same
                functionalities to bash scripts
- xuname:       platform recognition (only bash); return info about host
- tracelog:     manage tracelog (only bash)
- run_traced:   execute (or dry_run) shell command (only bash)
- findpkg:      find package in file system (only bash)
- CFG:          manage a dictionay value from config file
                like python ConfigParser (only bash)

@author: Antonio M. Vigliotti antoniomaria.vigliotti@gmail.com
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library
# from builtins import *                                             # noqa: F403
from builtins import object
import os
import argparse
import inspect
import configparser

standard_library.install_aliases()                                 # noqa: E402


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
DEFDCT = {}
__version__ = "1.0.5"


def nakedname(path):
    return os.path.splitext(os.path.basename(path))[0]


class CountAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None):
        super(CountAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        # new_count = argparse._ensure_value(namespace, self.dest, 0)
        new_count = self.dest if isinstance(self.dest, int) else 0
        if option_string != '-q':
            new_count += 1
        setattr(namespace, self.dest, new_count)


class parseoptargs(object):

    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(description=args[0],
                                              epilog=args[1])
        if 'version' in kwargs:
            self.version = kwargs['version']
        self.param_list = []

    def add_argument(self, *args, **kwargs):
        """Add argument to param list
        @param *args    positional arg; format may be '-x', '--xx' or 'xxx'
        @param action   action done when option is encountered; may be
                    - 'store' ('=' in bash); get value follows param
                        i.e. --opt=value -l value
                    - 'store_const'  (then constant value in bash);
                        set constant value from 'const' param
                    - 'store_true' 'store_false': same above, boolean value
                    - 'append' (not implemented in bash)
                    - 'count' ('+' in bash); how many times option occurs
                    - CountAction; same ad 'count' but may reset by '-q' option
                    - 'help'
                    - 'version'
        @param dest     internal name of param
        @param default  declare default value
        @param metavar  complete help for action_store
        """
        if len(args) and args[0][0] != '-':
            self.param_list.append(args[0])
            self.parser.add_argument(*args, **kwargs)
        elif args[0] != '-h' and args[0] != '--help':
            if len(args) == 1:
                if args[0] == '-n' or args[0] == '--dry-run':
                    self.parser.add_argument(
                        '-n', '--dry-run',
                        help='do nothing (dry-run)',
                        action='store_true',
                        dest='dry_run',
                        default=False)
                    self.param_list.append('dry_run')
                elif args[0] == '-q' or args[0] == '--quite':
                    self.parser.add_argument(
                        '-q', '--quiet',
                        help="silent mode",
                        action=CountAction,
                        dest="opt_verbose",)
                    self.param_list.append('opt_verbose')
                elif args[0] == '-V' or args[0] == '--version':
                    self.parser.add_argument(
                        '-V', '--version',
                        action='version',
                        version=self.version)
                elif args[0] == '-v' or args[0] == '--verbose':
                    self.parser.add_argument(
                        '-v', '--verbose',
                        help="verbose mode",
                        action=CountAction,
                        dest="opt_verbose")
                    self.param_list.append('opt_verbose')
                else:
                    raise NotImplementedError
            else:
                if 'dest' in kwargs:
                    self.param_list.append(kwargs['dest'])
                self.parser.add_argument(*args, **kwargs)

    def default_conf(self, ctx):
        return DEFDCT

    def get_this_fqn(self):
        i = 1
        valid = False
        while not valid:
            this_fqn = os.path.abspath(inspect.stack()[i][1])
            this = nakedname(this_fqn)
            if this in ("__init__", "pdb", "cmd", "z0testlib", "z0lib"):
                i += 1
            else:
                valid = True
        return this_fqn

    # def create_params_dict(self, ctx):
    #     """Create all params dictionary"""
    #     ctx = self.create_def_params_dict(ctx)
    #     return ctx
    def create_params_dict(self, ctx):
        """Create default params dictionary"""
        opt_obj = ctx.get('_opt_obj', None)
        # conf_obj = ctx.get('_conf_obj', None)
        # s = "options"
        # if conf_obj:                                       # pragma: no cover
        #     if not conf_obj.has_section(s):
        #         conf_obj.add_section(s)
        #     for p in LX_CFG_S:
        #         ctx[p] = conf_obj.get(s, p)
        #     for p in LX_CFG_B:
        #         ctx[p] = conf_obj.getboolean(s, p)
        # else:
        #     DEFDCT = self.default_conf(ctx)
        #     for p in LX_CFG_S:
        #         if p in DEFDCT:
        #             ctx[p] = DEFDCT[p]
        #     for p in LX_CFG_B:
        #         if p in DEFDCT:
        #             ctx[p] = DEFDCT[p]
        if opt_obj:
            for p in self.param_list:
                ctx[p] = getattr(opt_obj, p)
        return ctx

    def read_config(self, ctx):
        """Read both user configuration and local configuration."""
        if not ctx.get('conf_fn', None):
            if CONF_FN:
                ctx['conf_fn'] = CONF_FN
            else:
                ctx['conf_fn'] = "./" + ctx['caller'] + ".conf"
        conf_obj = configparser.ConfigParser(self.default_conf(ctx))
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

    def parseoptargs(self, arguments,
                     apply_conf=APPLY_CONF, version=None, tlog=None, doc=None):
        """Parse command-line options.
        @param arguments list of arguments; should argv from command line
        @param version   software version to displya with -V option
                         in bash version reports __version__ variable of script
        """
        ctx = {}
        this_fqn = self.get_this_fqn()
        ctx['this_fqn'] = this_fqn
        this = nakedname(this_fqn)
        ctx['this'] = this
        if os.isatty(0):
            ctx['run_daemon'] = False
        else:                                               # pragma: no cover
            ctx['run_daemon'] = True
        ctx['run_tty'] = os.isatty(0)
        if tlog:
            ctx['tlog'] = tlog
        else:
            ctx['tlog'] = this + '.log'
        # running autotest
        if version is None:
            ctx['_run_autotest'] = True
        ctx['_parser'] = self.parser
        opt_obj = self.parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        if apply_conf:
            if hasattr(opt_obj, 'conf_fn'):
                ctx['conf_fn'] = opt_obj.conf_fn
            ctx = self.read_config(ctx)
            opt_obj = self.parser.parse_args(arguments)
        ctx = self.create_params_dict(ctx)
        p = 'opt_verbose'
        if p in ctx and ctx[p] is None:
            if os.environ.get('VERBOSE_MODE', '') in ('0', '1'):
                ctx[p] = int(os.environ['VERBOSE_MODE'])
            elif os.isatty(0):
                ctx[p] = 1
            else:
                ctx[p] = 0
        # elif p in ctx and ctx[p] == -1:
        #     ctx[0] = 0
        return ctx
