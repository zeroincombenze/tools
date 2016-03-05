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
"""
     Restore database files from Production Machine to Development Machine
     Make 2 server quite identical, ready to use
     May be used to create a mirror server of Zeroincombenze®
"""


# import pdb
import os
import os.path
import sys
import argparse
import ConfigParser
from os0 import os0
import glob
import platform
from datetime import date, datetime, timedelta
import time
import string
import re


__version__ = "2.1.21.20"
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


def version():
    return __version__


#############################################################################
# Custom parser functions
#
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
                        default=dbg_mode)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("saveset",
                        help="saveset",
                        nargs='?')
    return parser


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


#############################################################################
# Common parser functions
#

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


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


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


class Restore_Image:

    def _init_conf(self):
        cfg_obj = ConfigParser.SafeConfigParser(default_conf())
        s = "Environment"
        cfg_obj.add_section(s)
        cfg_obj.set(s, "production_host", "shsprd16")
        cfg_obj.set(s, "development_host", "shsdev16")
        cfg_obj.set(s, "mirror_host", "shsprd14")
        cfg_obj.set(s, "ftp_script", "%(appname)s.ftp")
        cfg_obj.set(s, "list_file", "%(bckapp)s.ls")
        cfg_obj.set(s, "tracelog", "/var/log/%(appname)s.log")
        cfg_obj.set(s, "data_translation", "restconf.ini")
        cfg_obj.set(s, "no_translation", "restconf-0.ini")
        cfg_obj.set(s, "debug", "0")
        cfg_obj.read('.zar.conf')
        return cfg_obj

    def __init__(self, dbg_mode):
        self.hostname = platform.node()                         # Get Hostname
        self.pid = os.getpid()
        cfg_obj = self._init_conf()
        s = "Environment"
        if (dbg_mode is None):
            dbg_mode = cfg_obj.getboolean(s, "debug")
        os0.set_debug_mode(dbg_mode)
        # Production machine
        self.prodhost = cfg_obj.get(s, "production_host")
        # Development machine
        self.devhost = cfg_obj.get(s, "development_host")
        # Mirror machine
        self.mirrorhost = cfg_obj.get(s, "mirror_host")
        homedir = os.path.expanduser("~")
        # Temporary ftp command script
        self.ftpcf = homedir + "/" + cfg_obj.get(s, "ftp_script")
        # File list
        self.flist = homedir + "/" + cfg_obj.get(s, "list_file")
        # Tracelog file
        os0.set_tlog_file(cfg_obj.get(s, "tracelog"))
        # Translation file
        self.fconf = homedir + "/" + \
            cfg_obj.get(s, "data_translation")
        # Log begin execution
        os0.wlog("Restore database files {0} ({1})".format(
            __version__, self.pid))
        # Simulate backup
        self.dry_run = True
        if self.hostname == self.prodhost:
            os0.wlog("This command cannot run on production machine")
            # Restore onto prod machine
            self.bck_host = "shsdev16"
            # Restore onto prod machine !?
            raise Exception("Command aborted due production machine")
        elif self.hostname == self.mirrorhost:
            os0.wlog("Running on mirror machine")
            # Backup onto prod machine
            self.bck_host = "shsprd14"
            self.dry_run = False                               # Real restore
        elif self.hostname == self.devhost:
            os0.wlog("Running on development machine")
            # Restore onto dev machine !?
            self.bck_host = "shsprd14"
            self.dry_run = False                               # Real restore
        else:
            os0.wlog("Unknown machine - Command aborted")
            raise Exception("Command aborted due unknown machine")

        self.ftp_rootdir = ""                                   # No root dir
        self.ftp_dir = ""                                       # No subdir

        # May be (.gz or .bz2)
        self.tar_ext = ".gz"
        # May be (z or j)
        self.tar_opt = "z"
        # May be (null or .sql)
        self.pre_ext = ".sql"
        # May be (null or .sql)
        self.sql_ext = ".sql"

        self.psql_uu = "postgres"                               # Postgres UID
        self.psql_db = "postgres"                               # Default DB
        self.mysql_uu = "mysql"                                 # Mysql UID
        self.mysql_db = "mysql"                                 # Default DB
        self.dbtype = ""

        self.create_dict()

    def create_dict(self):
        # pdb.set_trace()
        self.dict = {}
        self.xtl = {}
        self.seed = 0
        try:
            cnf_fd = open(self.fconf, "r")
            line = cnf_fd.readline()
            while line != "":
                i = line.rfind('\n')
                if i >= 0 and line[0:1] != "#":
                    line = line.replace("\\ ", "\\b")
                    line = re.sub('s+', ' ', line).strip()
                    f = string.split(line, ' ')
                    self.add_dict_entr(f[0], f[1], f[2])
                line = cnf_fd.readline()
        except:
            pass

    def add_dict_entr(self, name, src, tgt):
        self.seed = self.seed + 1
        key = "{0:06d}".format(self.seed)
        val = (src, tgt)
        if name in self.dict:
            self.dict[name].append(key)
        else:
            self.dict[name] = [key]
        self.xtl[key] = val
        # print "[{0}] !{1}->{2}!".format(name, src, tgt)

    def search4item(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return None

    def restore_file(self, fqn):
        # pdb.set_trace()
        dbtype = ""
        # Extract dir if supplied
        p = os.path.dirname(fqn)
        f = os.path.basename(fqn)                               # Just filename
        # No dir supplied
        if p == "":
            p = self.ftp_dir
        elif p == "/var/lib/pgsql/backups":
            dbtype = "psql"
        elif p == "/var/lib/mysql/backups":
            dbtype = "mysql"
        if dbtype != self.dbtype:
            if dbtype == "psql":
                cmd = "service postgresql restart"
                os0.trace_debug("$", cmd)
                os0.muteshell(cmd,
                              simulate=self.dry_run,
                              keepout=os0.debug_mode)
            elif dbtype == "mysql":
                cmd = "service mysqld restart"
                os0.trace_debug("$", cmd)
                os0.muteshell(cmd,
                              simulate=self.dry_run,
                              keepout=os0.debug_mode)
        if p != self.ftp_dir:                                   # Change dir
            self.chdir(p)                                       # Set directory
        l = len(self.sql_ext) + 9
        # i = len(f) - l
        # Extract dbname from XXXXX-YYYYMMDD.SQL
        dbname = f[0:-l]
        # if dbname == "wp-zi-it":
        #     os0.wlog("  db", dbname, "not upgradable!!!")
        if os.path.isfile(f):
            self.restore_db(dbtype, dbname, fqn)
        else:
            os0.wlog("  file", f, "not found!!!")

    def get_params(self, f):
        ctx = {}
        ctx['prefix'] = ""
        ctx['siteURL'] = ""
        ctx['testURL'] = ""
        ctx['siteURI'] = ""
        ctx['testURI'] = ""
        ctx['admin_email'] = ""
        ctx['conf_file'] = ""
        ctx['conf_file2'] = ""
        ctx['conf_file3'] = ""
        ctx['index_html'] = ""
        key_ids = self.search4item(f)
        if key_ids:
            # fxch = True
            # Text couples for substitution
            for key in key_ids:
                src = self.xtl[key][0]
                src = src.replace("\\b", " ")
                tgt = self.xtl[key][1]
                tgt = tgt.replace("\\b", " ")
                if src == ".prefix":
                    ctx['prefix'] = tgt
                elif src == ".siteURL":
                    ctx['siteURL'] = tgt
                    i = ctx['siteURL'].find(".")
                    if i < 0:
                        ctx['siteURL'] = "http://www." + ctx['siteURL']
                    i = ctx['siteURL'].find(":")
                    if i < 0:
                        ctx['siteURL'] = "http://" + ctx['siteURL']
                    i = ctx['siteURL'].find(".")
                    if ctx['admin_email'] == "":
                        ctx['admin_email'] = "postmaster@" + \
                            ctx['siteURL'][i + 1:]
                    if ctx['testURL'] == "":
                        ctx['testURL'] = ctx['siteURL'][0:i] + \
                            "1" + ctx['siteURL'][i:]
                    if ctx['siteURI'] == "":
                        x = ctx['siteURL'].split("://")
                        ctx['siteURI'] = x[1]
                    if ctx['testURI'] == "":
                        x = ctx['testURL'].split("://")
                        ctx['testURI'] = x[1]
                elif src == ".testURL":
                    ctx['testURL'] = tgt
                    x = ctx['testURL'].split("://")
                    ctx['testURI'] = x[1]
                elif src == ".siteURI":
                    ctx['siteURI'] = tgt
                elif src == ".testURI":
                    ctx['testURI'] = tgt
                elif src == ".admin_email":
                    ctx['admin_email'] = tgt
                elif src == ".conf_file":
                    ctx['conf_file'] = tgt
                elif src == ".conf_file2":
                    ctx['conf_file2'] = tgt
                elif src == ".conf_file3":
                    ctx['conf_file3'] = tgt
                elif src == ".index_html":
                    ctx['index_html'] = tgt
                else:
                    raise ValueError('Invalid param {0}!'.format(src))
        return ctx

    def repl_data_wp(self, ctx, fqn_str):
        os0.trace_debug(
            "> update URL (wp) {0}->{1}"
            .format(ctx['siteURL'], ctx['testURL']))
        stmt = "update {0}options set option_value='{1}'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], ctx['testURL'], "siteurl")
        fqn_str = fqn_str + stmt + ";\n"
        stmt = "update {0}options set option_value='{1}'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], ctx['testURL'], "home")
        fqn_str = fqn_str + stmt + ";\n"
        stmt = "update {0}options set option_value='{1}/'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], ctx['testURL'], "ga_default_domain")
        fqn_str = fqn_str + stmt + ";\n"
        stmt = "update {0}options set option_value='{1}'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], ctx['siteURI'], "ga_root_domain")
        fqn_str = fqn_str + stmt + ";\n"
        stmt = "update {0}options set option_value='{1}'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], ctx['admin_email'], "admin_email")
        fqn_str = fqn_str + stmt + ";\n"
        stmt = "update {0}options set option_value='{1}'"\
               " where option_name='{2}'"\
               .format(ctx['prefix'], "0", "blog_public")
        fqn_str = fqn_str + stmt + ";\n"

        src_str = ctx['siteURL']
        ix = fqn_str.find(src_str)
        while ix >= 0:
            l = len(ctx['siteURL'])
            j = ix - 1
            sep = ' '
            while sep == ' ':
                while fqn_str[j] != '\"' and fqn_str[j] != '\'':
                    j = j - 1
                sep = fqn_str[j]
                j = j - 1
                if fqn_str[j] == '\\':
                    if sep == '\'':
                        sep = ' '
                    else:
                        j = j - 1
                        if fqn_str[j] != ':':
                            sep = ' '
                        else:
                            j = j - 1
            if sep == '\"':
                ix1 = j + 1
                while fqn_str[j].isdigit():
                    j = j - 1
                n = fqn_str[j + 1:ix1]
                i = int(n)
                if i >= l:
                    src = fqn_str[j + 1:ix] + ctx['siteURL']
                    j = len(ctx['testURL'])
                    n = str(i + j - l)
                    tgt = n + fqn_str[ix1:ix] + ctx['testURL']
                    os0.trace_debug(
                        "> sed|{0}|{1}|".format(src, tgt))
                    fqn_str = fqn_str.replace(src, tgt)
            ix = fqn_str.find(src_str, ix + 1)
        return fqn_str

    def repl_data(self, dbname, fqn):
        fzero = False
        try:
            fqn_fd = open(fqn, 'r')
            # Go to end of file
            fqn_fd.seek(0, os.SEEK_END)
            # File len = 0 ?
            if fqn_fd.tell() == 0:
                fzero = True
            # Go to begin of file
            fqn_fd.seek(0, 0)
            # Read entire file
            fqn_str = fqn_fd.read()
            fqn_fd.close()
        except:
            fzero = True
        if fzero:
            os0.wlog("  file", fqn, "empty!!!")
        else:
            fxch = False

            # Search for text substitution (Wordpress)
            f = dbname + "->wp"
            ctx = self.get_params(f)
            if ctx['prefix'] != "" and ctx['siteURL'] != "":
                fxch = True
                fqn_str = self.repl_data_wp(ctx, fqn_str)

            f = dbname + "/"
            # Search for text substitution
            key_ids = self.search4item(f)
            if key_ids:
                fxch = True
                # Text couples for substitution
                for key in key_ids:
                    src = self.xtl[key][0]
                    src = src.replace("\\b", " ")
                    tgt = self.xtl[key][1]
                    tgt = tgt.replace("\\b", " ")
                    fqn_str = fqn_str + src + " " + tgt + ";\n"

            f = dbname + self.sql_ext
            # Search for text substitution
            key_ids = self.search4item(f)
            if key_ids:
                fxch = True
                # Text couples for substitution
                for key in key_ids:
                    src = self.xtl[key][0]
                    src = src.replace("\\b", " ")
                    tgt = self.xtl[key][1]
                    tgt = tgt.replace("\\b", " ")
                    os0.trace_debug("> sed|{0}|{1}|".format(src, tgt))
                    # Substitute text in file
                    fqn_str = fqn_str.replace(src, tgt)

            if fxch:
                fqn_fd = open(fqn, 'w')
                # write file with substitutions
                fqn_fd.write(fqn_str)
                fqn_fd.close()

            f = dbname + "->wiki"
            ctx = self.get_params(f)
            if ctx['siteURL'] != "":
                fqns = ctx['conf_file'].split(',')
                for fqn in fqns:
                    self.replace_file(ctx, f, fqn)
                if ctx['conf_file2']:
                    fqns = ctx['conf_file2'].split(',')
                    for fqn in fqns:
                        self.replace_file(ctx, f, fqn)
                if ctx['conf_file3']:
                    fqns = ctx['conf_file3'].split(',')
                    for fqn in fqns:
                        self.replace_file(ctx, f, fqn)
                fqn = ctx['index_html']
                self.replace_file(ctx, f, fqn)

    def replace_file(self, ctx, f, fqn):
        os0.trace_debug("> replace file", fqn)
        try:
            fn_fd = open(fqn, 'r')
            fn_str = fn_fd.read()
            fn_fd.close()
            key_ids = self.search4item(f)
            if key_ids:
                src = ctx['siteURL']
                tgt = ctx['testURL']
                fn_str = fn_str.replace(src, tgt)
                src = ctx['siteURI']
                tgt = ctx['testURI']
                fn_str = fn_str.replace(src, tgt)
                fn_fd = open(fqn, 'w')
                fn_fd.write(fn_str)
                fn_fd.close()
        except:
            pass

    def restore_db(self, dbtype, dbname, fqn):
        # pdb.set_trace()
        os0.wlog("  restoring", dbname, " ({0})".format(fqn))
        homedir = os.path.expanduser("~")

        tar_ext = self.tar_ext
        tar_opt = self.tar_opt
        fzip_fn = dbname + tar_ext
        if not os.path.isfile(fzip_fn):
            if self.tar_ext == ".gz":
                tar_ext = ".bz2"
                tar_opt = "j"
                fzip_fn = dbname + tar_ext
                if not os.path.isfile(fzip_fn):
                    tar_ext = self.tar_ext
                    tar_opt = self.tar_opt
                    # No compressed file found
                    fzip_fn = ""
            elif self.tar_ext == ".bz2":
                tar_ext = ".gz"
                tar_opt = "z"
                fzip_fn = dbname + tar_ext
                if not os.path.isfile(fzip_fn):
                    tar_ext = self.tar_ext
                    tar_opt = self.tar_opt
                    # No compressed file found
                    fzip_fn = ""

        f = os.path.basename(fqn)                               # Just filename
        l = len(self.sql_ext) + 9
        i = len(f) - l
        # Extract date (YYYYMMDD) from XXXXX-YYYYMMDD.SQL
        dts = f[i + 1:i + 9]
        if dbtype == "psql":
            cmd = "chown " + self.psql_uu + ":" + self.psql_uu + " " + fqn
        elif dbtype == "mysql":
            cmd = "chown " + self.mysql_uu + ":" + self.mysql_uu + " " + fqn
        os0.trace_debug("$", cmd)
        os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)

        sql_fn = homedir + "/restdb.sql"
        cmd = "cp " + fqn + " " + sql_fn
        os0.trace_debug("$", cmd)
        os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
        cmd = "sed -i -e \"s|Owner: openerp|Owner: odoo|g\""\
              " -e \"s|OWNER TO openerp|OWNER TO odoo|g\" ~/restdb.sql"
        os0.trace_debug("$", cmd)
        os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
        if dbtype == "psql":
            cmd = "chown " + self.psql_uu + ":" + self.psql_uu + " " + sql_fn
        elif dbtype == "mysql":
            cmd = "chown " + self.mysql_uu + ":" + self.mysql_uu + " " + sql_fn
        os0.trace_debug("$", cmd)
        os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
        self.repl_data(dbname, sql_fn)

        psh_fn = homedir + "/restdb.psh"
        psh_fd = open(psh_fn, "w")
        if dbtype == "psql":
            user = self.psql_uu
            defdb = self.psql_db
            psh_fd.write("\\c {0}\n".format(defdb))
            psh_fd.write(
                "DROP DATABASE IF EXISTS \"{0}-{1}\";\n".format(dbname, dts))
            psh_fd.write("DROP DATABASE IF EXISTS \"{0}\";\n".format(dbname))
            psh_fd.write(
                "CREATE DATABASE \"{0}\" TEMPLATE template1;\n".format(dbname))
            psh_fd.write("\\c \"{0}\"\n".format(dbname))
            psh_fd.write("\\i {0}\n".format(sql_fn))
            psh_fd.write(
                "ALTER DATABASE \"{0}\" OWNER TO odoo;\n".format(dbname))
            cmd = "psql -f " + psh_fn + " -U" + user + " " + defdb
            psh_fd.close()
            os0.trace_debug("$", cmd)
            os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
        elif dbtype == "mysql":
            user = "root"
            pwd = "SHS13mgr"
            # defdb = self.psql_db
            psh_fd.write(
                "mysqladmin -u{0} --password={1} -f drop \"{2}-{3}\" ||true\n"
                .format(user, pwd, dbname, dts))
            psh_fd.write(
                "mysqladmin -u{0} --password={1} -f drop \"{2}\" || true\n"
                .format(user, pwd, dbname))
            psh_fd.write(
                "mysqladmin -u{0} --password={1} -f create \"{2}\"\n"
                .format(user, pwd, dbname))
            psh_fd.write(
                "mysql -u{0} --password=SHS13mgr -G -e \"source {1}\" {2}\n"
                .format(user, sql_fn, dbname))
            psh_fd.close()
            cmd = "chmod +x " + psh_fn
            os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
            cmd = psh_fn
            os0.trace_debug("$", cmd)
            os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
        else:
            os0.wlog("  unknown", dbname, "database type!!!")
            cmd = "echo Error"

        # Compressed file found
        if fzip_fn != "":
            if dbtype == "psql":
                cmd = "chown " + self.psql_uu + \
                    ":" + self.psql_uu + " " + fzip_fn
            elif dbtype == "mysql":
                cmd = "chown " + self.mysql_uu + \
                    ":" + self.mysql_uu + " " + fzip_fn
            os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)

            cmd = "tar --keep-newer-files -x" + tar_opt + "f " + fzip_fn
            os0.muteshell(cmd, simulate=self.dry_run, keepout=os0.debug_mode)
            if not self.dry_run:
                os.remove(fzip_fn)

        self.purge_db(dbtype, dbname)

    def purge_db(self, dbtype, f):
        # pdb.set_trace()
        if self.sql_ext != self.pre_ext:
            self.change_file_ext(f)

        dtc = date.today() - timedelta(90)
        os0.wlog("  removing file older than", dtc.strftime("%Y-%m-%d"))
        fzip_fn = f + self.tar_ext
        force_change_ext = False
        for i in range(180, 120, -1):
            dtc = datetime.today() - timedelta(i)
            dts = dtc.strftime("%Y%m%d")
            fsql = f + "-" + dts + self.sql_ext
            if not os.path.isfile(fsql) and self.sql_ext != self.pre_ext:
                ftmp = f + "-" + dts + self.pre_ext
                if os.path.isfile(ftmp):
                    try:
                        os0.wlog("$ mv", ftmp, fsql)
                        if not self.dry_run:
                            # Rename old ext -> nex ext
                            os.rename(ftmp, fsql)
                        # Force change sql file extension
                        force_change_ext = True
                    except:
                        pass

            if dtc.day != 1:
                if not self.remove_sql_file(fsql) \
                        and self.sql_ext != self.pre_ext:
                    fsql = f + "-" + dts + self.pre_ext
                    self.remove_sql_file(fsql)

        if force_change_ext:
            self.change_file_ext(f)

        fsql = f + "-????????" + self.sql_ext
        if dbtype == "psql":
            cmd = "chown " + self.psql_uu + ":" + self.psql_uu + " " + fsql
        elif dbtype == "mysql":
            cmd = "chown " + self.mysql_uu + ":" + self.mysql_uu + " " + fsql
        os0.trace_debug("$ ", cmd)
        os0.muteshell(cmd, simulate=self.dry_run)

        cmd = "tar --remove-files -c" + \
            self.tar_opt + "f " + fzip_fn + " " + fsql
        os0.trace_debug("$ ", cmd)
        os0.muteshell(cmd, simulate=self.dry_run)

        if dbtype == "psql":
            cmd = "chown " + self.psql_uu + ":" + self.psql_uu + " " + fzip_fn
        elif dbtype == "mysql":
            cmd = "chown " + self.mysql_uu + \
                ":" + self.mysql_uu + " " + fzip_fn
        os0.trace_debug("$ ", cmd)
        os0.muteshell(cmd, simulate=self.dry_run)

        os0.wlog("  removing archived files")
        fsql = f + "-????????" + self.sql_ext
        f_ids = glob.glob(fsql)
        for fsql in f_ids:
            self.remove_sql_file(fsql)

    def change_file_ext(self, f):
        os0.wlog("  changing extension files")
        fsql = f + "-????????" + self.pre_ext
        f_ids = glob.glob(fsql)
        for f in f_ids:
            l = len(f) - len(self.pre_ext)
            fsql = f[0:l] + self.sql_ext
            if not os.path.isfile(fsql):
                ftmp = f
                if os.path.isfile(ftmp):
                    try:
                        os0.wlog("$ mv", ftmp, fsql)
                        if not self.dry_run:
                            # Rename old ext -> nex ext
                            os.rename(ftmp, fsql)
                    except:
                        pass

    def remove_sql_file(self, fsql):
        try:
            fzip_fd = open(fsql, "r")
            fzip_fd.close()
            os0.trace_debug("$ rm", fsql)
            if not self.dry_run:
                os.remove(fsql)
            sts = True
        except:
            sts = False
        return sts

    def extract_fn_2_restore(self):
        file_2_restore = ""
        # self.commit_fn_restored()
        ls_fd = open(self.flist, "r+")
        # ftmp = self.flist + ".lst"
        # lst_fd = open(ftmp, "w")
        p = ls_fd.tell()
        fl = ls_fd.readline()
        # f_copy = False
        while fl != "":
            i = fl.rfind('\n')
            if file_2_restore == "" and i >= 0 and fl[0:1] != '#':
                f = fl[0:i]
                file_2_restore = f
                # f_copy = True
                f = "#" + f[1:]
                ls_fd.seek(p, os.SEEK_SET)
                ls_fd.write(f)
            p = ls_fd.tell()
            fl = ls_fd.readline()
            # if f_copy:
            #     lst_fd.write(fl)
        ls_fd.close()
        # if not f_copy:
        #     lst_fd.close()
        #     lst_fd = open(self.flist, "w")
        # dtc = datetime.today()
        # lst_fd.write("# {0}\n".format(dtc.strftime("%Y%m%d %H:%M:%S")))
        # lst_fd.close()
        return file_2_restore

    def commit_fn_restored(self):
        ftmp = self.flist + ".lst"
        fbak = self.flist + ".bak"
        if os.path.isfile(ftmp):
            fn_fd = open(ftmp, 'r')
            fzero = True
            fl = fn_fd.readline()
            while fl != "" and fzero:
                i = fl.rfind('\n')
                if i >= 0:
                    fzero = False
                fl = fn_fd.readline()
            fn_fd.close()
            if not fzero:
                cmd = "rm -f {2}; mv {0} {2}; mv {1} {0}".format(
                    self.flist, ftmp, fbak)
                os0.trace_debug("$ ", cmd)
                os0.muteshell(cmd, simulate=self.dry_run)
            else:
                if not self.dry_run:
                    os.remove(ftmp)

    def chdir(self, path):
        # Change root dir
        lpath = os0.setlfilename(path)
        os0.wlog(" [{0}]".format(lpath))
        self.set_chdir(lpath)
        self.ftp_dir = path                                    # Remember dir

    def set_chdir(self, path):
        # Exec chdir and store into ftp script
        os.chdir(path)


def main():
    """Tool main"""
    sts = 0
    # pdb.set_trace()
    ctx = parse_args(sys.argv[1:])
    dbg_mode = ctx['dbg_mode']
    RI = Restore_Image(dbg_mode)
    # dbname="wp-zi-com"      ##debug
    # sql_fn="restdb.sql"     ##debug
    # RI.repl_data(dbname, sql_fn)  ###debug
    # exit    ##debug
    # Check for another instance running
    f_alrdy_run = False
    cmd = "ps aux|grep restdb.py"
    os0.muteshell(cmd, keepout=True)
    stdinp_fd = open(os0.setlfilename(os0.bgout_fn), 'r')
    rxmatch = "root .* python .*restdb.py.*"
    rxnmatch = "root .* {0} .*".format(RI.pid)
    line = stdinp_fd.readline()
    while line != "" and not f_alrdy_run:
        i = line.rfind('\n')
        if i >= 0:
            if re.match(rxmatch, line) and not re.match(rxnmatch, line):
                f_alrdy_run = True
                os0.wlog("({0}) ***Another instance is running!!!"
                         .format(RI.pid))
        line = stdinp_fd.readline()
    stdinp_fd.close()
    # Restore files
    file_r_ctr = 0
    file_u_ctr = 0
    if not f_alrdy_run:
        fl = RI.extract_fn_2_restore()
        while fl != "":
            file_r_ctr = file_r_ctr + 1
            if os.path.isfile(fl):
                RI.restore_file(fl)
                file_u_ctr = file_u_ctr + 1
            else:
                os0.wlog("  file", fl, "not found!!!")
            RI.commit_fn_restored()
            fl = RI.extract_fn_2_restore()
            if fl == "":
                os0.wlog("  wait for next db")
                # Wait if another file supplied
                time.sleep(90)
                fl = RI.extract_fn_2_restore()
                os0.wlog("  found", fl, "?")
    if not dbg_mode and os.path.isfile(os0.setlfilename(os0.bgout_fn)):
        os.remove(os0.setlfilename(os0.bgout_fn))
    if not f_alrdy_run:
        os0.wlog("Restore DB ended."
                 " {0} DB to restore, {1} DB restored ({2})."
                 .format(file_u_ctr, file_u_ctr, RI.pid))
    return sts


if __name__ == "__main__":
    # if running detached
    if os.isatty(0):
        dbg_mode = False
    else:
        dbg_mode = True
    dbg_mode = True     # debug
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
