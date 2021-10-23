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
"""
    ZAR common functions
"""


# import pdb
import os
# import os.path
# import sys
import argparse
import ConfigParser
# import glob
from sys import platform as _platform
import platform
import inspect
from datetime import datetime
import re
# import string
try:
    from os0 import os0
except ImportError:
    import os0

# return code
WOW_FAILED = 1
WOW_SUCCESS = 0
# Apply for configuration file (True/False)
APPLY_CONF = False
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = ".zar.conf"
# Read Odoo configuration file (False or /etc/odoo-server.conf)
ODOO_CONF = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
OE_CONF = False
# Warning: set all LXs with no values -> LX=(), with 1 value -> LX=(value,)
# List of string parameters in [options] of config file
LX_CFG_S = ('dry_run',)
# List of pure boolean parameters in [options] of config file
LX_CFG_B = ()
# List of string parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_S = ('opt_verbose', 'db_name', 'dry_run', 'xtall')
# List of pure boolean parameters in line command; may be in LX_CFG_S list too
LX_OPT_CFG_B = ()
# List of string/boolean parameters; may be string or boolean value;
# must be declared in LX_CFG_S or LX_OPT_CFG_S
LX_SB = ('dry_run',)
#
DEFDCT = {}


class ZarLib:
    pid = os.getpid()
    homedir = os.path.expanduser("~")

    @staticmethod
    def docstring_summary(docstring):
        """Return summary of docstring."""
        for text in docstring.split('\n'):
            if text.strip():
                break
        return text.strip()

    @staticmethod
    def create_parser(version, ctx):
        """Return command-line parser.
        Some options are standard:
        -c --config     set configuration file (conf_fn)
        -h --help       show help
        -q --quiet      quiet mode
        -t --dry-run    simulation mode for test
        -U --user       set username (user)
        -v --verbose    verbose mode
        -V --version    show version
        -y --yes        confirmation w/out ask
        """
        parser = argparse.ArgumentParser(
            description=ZarLib.docstring_summary(__doc__),
            epilog="© 2015-2016 by SHS-AV s.r.l."
                   " - http://www.zeroincombenze.org")
        parser.add_argument("-0", "--install",
                            help="install & configure",
                            action="store_true",
                            dest="xtall",
                            default=False)
        parser.add_argument("-c", "--conf",
                            help="configuration file",
                            dest="conf_fn",
                            metavar="file",
                            default=CONF_FN)
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
                            default=None)
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
                            dest="opt_verbose",
                            default=ctx['run_daemon'])
        parser.add_argument("-V", "--version",
                            action="version",
                            version=version)
        parser.add_argument("saveset",
                            help="saveset",
                            nargs='?')
        return parser

    @staticmethod
    def read_config(ctx):
        """Read both user configuration and local configuration."""
        if not ctx.get('conf_fn', None):
            if CONF_FN:
                ctx['conf_fn'] = CONF_FN
            else:
                ctx['conf_fn'] = "./" + ctx['caller'] + ".conf"
        conf_obj = ConfigParser.SafeConfigParser(ZarLib.default_conf(ctx))
        if ODOO_CONF:
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

    @staticmethod
    def create_params_dict(ctx):
        """Create all params dictionary"""
        conf_obj = ctx.get('_conf_obj', None)
        ctx = ZarLib.create_def_params_dict(ctx)
        if conf_obj:
            s = "Environment"
            if not conf_obj.has_section(s):
                conf_obj.add_section(s)
            saveset_list = conf_obj.get(s, "saveset_list")
            conf_obj.set(s, "tracelog", "%(appname)s.log")
        else:
            ctx = ZarLib.default_conf(ctx)
            saveset_list = ""
        if saveset_list:
            saveset_list = saveset_list.split(',')
            for sset in saveset_list:
                s = sset.strip()
                if not conf_obj.has_section(s):
                    conf_obj.add_section(s)
                    conf_obj.set(s,
                                 "ftp_script",
                                 ZarLib.homedir + "/%(appname)s_" + s + ".ftp")
                    conf_obj.set(s,
                                 "list_file",
                                 ZarLib.homedir + "/%(appname)s_" + s + ".ls")
                    conf_obj.set(s,
                                 "data_translation",
                                 ZarLib.homedir + "/%(appname)s_" + s + ".xlt")
                    conf_obj.set(s, "path", "./*")
                    conf_obj.set(s, "cmd_bck", "")
                    conf_obj.set(s, "cp_mode", "save")
                    conf_obj.set(s, "debug", "0")
        return ctx

    @staticmethod
    def parse_args(arguments, apply_conf=False, version=None):
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
        parser = ZarLib.create_parser(version, ctx)
        ctx['_parser'] = parser
        opt_obj = parser.parse_args(arguments)
        ctx['_opt_obj'] = opt_obj
        if apply_conf:
            if hasattr(opt_obj, 'conf_fn'):
                ctx['conf_fn'] = opt_obj.conf_fn
            ctx = ZarLib.read_config(ctx)
            # opt_obj = parser.parse_args(arguments)
        ctx = ZarLib.create_params_dict(ctx)
        return ctx

    @staticmethod
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
            DEFDCT = ZarLib.default_conf(ctx)
            for p in LX_CFG_S:
                if p in DEFDCT:
                    ctx[p] = DEFDCT[p]
            for p in LX_CFG_B:
                if p in DEFDCT:
                    ctx[p] = DEFDCT[p]
        if opt_obj:
            for p in LX_OPT_CFG_S:
                if hasattr(opt_obj, p):
                    ctx[p] = getattr(opt_obj, p)
            for p in LX_OPT_CFG_B:
                if hasattr(opt_obj, p):
                    ctx[p] = os0.str2bool(getattr(opt_obj, p), None)
        for p in LX_SB:
            ctx[p] = os0.str2bool(ctx[p], ctx[p])
        return ctx

    @staticmethod
    def install(ctx):
        # pdb.set_trace()
        # create script to execute zar.py
        sts = WOW_SUCCESS
        script_fn = __file__
        i = script_fn.rfind('.py')
        if i >= 0:
            script_fn = script_fn[0:i]
        dtc = datetime.today()

        if ctx['dry_run']:
            pass
        elif _platform == "win32":
            script_fn = script_fn + ".bat"
            script_fd = open(script_fn, "w")
            script_fd.write("@echo off\n")
            script_fd.write("rem ZarLib script {0} created at {1}\n".format(
                ctx['__version__'], dtc.strftime("%Y-%m-%d")))
            script_fd.write(
                "rem (C) 2015-2016 by SHS-AV s.r.l."
                " - http://www.zeroincombenze.org\n")
            script_fd.write(
                "python {0} %1 %2 %3 %4 %5 %6 %7 %8 %9".format(__file__))
            script_fd.close()
        elif _platform == "OpenVMS":
            script_fn = script_fn + ".COM"
            script_fd = open(script_fn, "w")
            script_fd.write("$ verify off\n")
            script_fd.write("$! ZarLib script {0} created at {1}\n".format(
                ctx['__version__'], dtc.strftime("%Y-%m-%d")))
            script_fd.write(
                "$! (C) 2015-2016 by SHS-AV s.r.l."
                " - http://www.zeroincombenze.org\n")
            script_fd.write(
                "$ python {0} %1 %2 %3 %4 %5 %6 %7 %8 %9".format(__file__))
            script_fd.close()
        else:
            script_fd = open(script_fn, "w")
            script_fd.write("# ZarLib script {0} created at {1}\n".format(
                ctx['__version__'], dtc.strftime("%Y-%m-%d")))
            script_fd.write(
                "# (C) 2015-2016 by SHS-AV s.r.l. "
                "- http://www.zeroincombenze.org\n")
            script_fd.write(
                "python -u {0} $@\n".format(__file__))
            script_fd.close()
            cmd = "chmod +x {0}".format(script_fn)
            os0.muteshell(cmd)
        return sts

    @staticmethod
    def default_conf(ctx):
        """Default configuration values"""
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
        DEFDCT = {"saveset_list": "",
                  "appname": a,
                  "bckapp": b,
                  "restapp": r,
                  "specimen": "file",
                  "production_host": "shsprd14",
                  "development_host": "shsdev14",
                  "ftp_script": a + ".ftp",
                  "list_file": b + ".ls",
                  "tracelog": a + ".log",
                  "data_translation": "restconf.ini",
                  "debug": ctx.get('run_daemon', True)}
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

    def __init__(self):
        dbg_mode = True
        os0.set_debug_mode(dbg_mode)
        self.hostname = platform.node()
        self.dbg_mode = dbg_mode
        self.homedir = os.path.expanduser("~")
        return

    def check_if_running(self):
        f_alrdy_run = False
        cmd = "ps aux|grep restdb.py"
        os0.muteshell(cmd, keepout=True)
        stdinp_fd = open(os0.setlfilename(os0.bgout_fn), 'r')
        rxmatch = "root .* python .*zar.py.*"
        rxnmatch = "root .* {0} .*".format(self.pid)
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
