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
     Back-up database files from Production Machine to Development Machine
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
from sys import platform as _platform
import platform
from datetime import date, timedelta
import re


__version__ = "2.1.24.14"
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
LX_OPT_CFG_S = ('dbg_mode', 'db_name')
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


class Backup_Mirror:

    def _init_conf(self):
        # pdb.set_trace()
        cfg_obj = ConfigParser.SafeConfigParser(default_conf())
        s = "Environment"
        cfg_obj.add_section(s)
        cfg_obj.set(s, "production_host", "shsprd14")
        cfg_obj.set(s, "development_host", "shsdev16")
        cfg_obj.set(s, "mirror_host", "shsprd16")
        cfg_obj.set(s, "ftp_script", "%(appname)s.ftp")
        cfg_obj.set(s, "list_file", "%(bckapp)s.ls")
        cfg_obj.set(s, "tracelog", "%(appname)s.log")
        cfg_obj.set(s, "data_translation", "restconf.ini")
        cfg_obj.set(s, "debug", "0")
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
            cfg_obj.set(s, "pg_dir", pn)
        else:
            cfg_obj.set(s, "pg_dir", "")
        if os.path.isdir("/var/lib/mysql"):
            cfg_obj.set(s, "mysql_dir", "/var/lib/mysql")
        else:
            cfg_obj.set(s, "mysql_dir", "")
        cfg_obj.read('zar.conf')
        return cfg_obj

    def init_bck(self, lpath=None):
        self.ftp_fd = open(self.ftp_cfn, "w")
        self.ls_fd = open(self.flist, "w")

        self.ftp_rootdir = ""                                   # No root dir
        self.ftp_dir = ""                                       # No subdir
        if lpath:
            self.chdir(lpath)

    def __init__(self, dbg_mode):
        self.hostname = platform.node()                         # Get Hostname
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
        # Postgresql directory
        self.pgdir = cfg_obj.get(s, "pg_dir")
        # Mysql directory
        self.mysqldir = cfg_obj.get(s, "mysql_dir")
        homedir = os.path.expanduser("~")
        # Temporary ftp command script
        self.ftp_cfn = homedir + "/" + cfg_obj.get(s, "ftp_script")
        self.flist = homedir + "/" + cfg_obj.get(s, "list_file")    # File list
        os0.set_tlog_file(cfg_obj.get(s, "tracelog"))           # Tracelog file

        # Log begin execution
        os0.wlog("Backup database files", __version__)
        # Simulate backup
        self.dry_run = True
        if self.hostname == self.prodhost:
            os0.wlog("Running on production machine")
            # Backup onto prod machine
            self.bck_host = "shsdev16"
            self.dry_run = False                               # Real backup
        elif self.hostname == self.mirrorhost:
            os0.wlog("Running on mirror machine")
            # Backup onto prod machine
            self.bck_host = self.devhost
#            raise Exception("Command aborted due development machine")
        elif self.hostname == self.devhost:
            os0.wlog("This command cannot run on development machine")
            # Backup onto dev machine !?
            self.bck_host = "shsprd14"
#            raise Exception("Command aborted due development machine")
        else:
            os0.wlog("Unknown machine - Command aborted")
            raise Exception("Command aborted due unknown machine")

        # May be (.gz or .bz2)
        self.tar_ext = ".gz"
        # May be (z or j)
        self.tar_opt = "z"
        # May be (null or .sql)
        self.pre_ext = ".sql"
        # May be (null or .sql)
        self.sql_ext = ".sql"

        self.psql_uu = "postgres"                               # Postgres UID
        self.mysql_uu = "mysql"                                 # Mysql UID

        self.init_bck()

    def gen_db_list(self, dbtype, user, sqlcmd):
        # pdb.set_trace()
        dblist = []
        os0.wlog(" Creating", dbtype, "db list")

        if dbtype == "psql":
            cmd = sqlcmd + " -U" + user + " -l"
            cmdlog = cmd
        elif dbtype == "mysql":
            cmd = sqlcmd + " -u " + user + \
                " --password=SHS13mgr -e \"show databases;\" mysql"
            cmdlog = sqlcmd + " -u " + user + " -e \"show databases;\" mysql"
        else:
            cmd = ""
            cmdlog = cmd
        os0.trace_debug("$", cmdlog)
        os0.muteshell(cmd, simulate=self.dry_run, keepout=True)
        stdinp_fd = open(os0.setlfilename(os0.bgout_fn), 'r')
        line = stdinp_fd.readline()
        while line != "":
            i = line.rfind('\n')
            if i >= 0:
                if dbtype == "psql":
                    if line[0:1] == ' ' and line[1:2] != ' ':
                        x = line.split('|')
                        dbname = x[0].strip()
                        if re.match("z[ei].*|demo", dbname):
                            dblist.append(dbname)
                            if os0.debug_mode:
                                os0.wlog("$ dblist.append({0})".format(dbname))
                elif dbtype == "mysql":
                    dbname = line.strip()
                    if re.match("w.*|mg.*|assioma.*", dbname):
                        dblist.append(dbname)
                        if os0.debug_mode:
                            os0.wlog("$ dblist.append({0})".format(dbname))
            line = stdinp_fd.readline()
        stdinp_fd.close()

        if not os0.debug_mode and not self.dry_run and os0.bgout_fn != "":
            # Delete files list
            os.remove(os0.setlfilename(os0.bgout_fn, 'r'))

        return dblist

    def bck_db(self, dbtype, dblist, user, sqlcmd):
        # pdb.set_trace()
        # save_ftp_rootdir = self.ftp_rootdir
        p = "backups"
        # Make full dir path (root + sub)
        lpath = self.ftp_rootdir + '/' + p
        self.chdir(lpath)                                       # Set directory

        for f in dblist:
            tar_ext = self.tar_ext
            tar_opt = self.tar_opt
            fzip_fn = f + tar_ext
            if not os.path.isfile(fzip_fn):
                if self.tar_ext == ".gz":
                    tar_ext = ".bz2"
                    tar_opt = "j"
                    fzip_fn = f + tar_ext
                    if not os.path.isfile(fzip_fn):
                        tar_ext = self.tar_ext
                        tar_opt = self.tar_opt
                        # No compressed file found
                        fzip_fn = ""
                elif self.tar_ext == ".bz2":
                    tar_ext = ".gz"
                    tar_opt = "z"
                    fzip_fn = f + tar_ext
                    if not os.path.isfile(fzip_fn):
                        tar_ext = self.tar_ext
                        tar_opt = self.tar_opt
                        # No compressed file found
                        fzip_fn = ""

            # Compressed file found
            if fzip_fn != "":
                cmd = "tar -x" + tar_opt + "f " + fzip_fn
                os0.trace_debug("$", cmd)
                os0.muteshell(cmd, simulate=self.dry_run)
                if not self.dry_run:
                    os.remove(fzip_fn)

            dts = date.today().strftime("%Y%m%d")
            fsql = f + "-" + dts + self.sql_ext
            if dbtype == "psql":
                cmd = sqlcmd + " -U" + user + " -F p -f " + fsql + " " + f
                cmdlog = cmd
            elif dbtype == "mysql":
                cmd = sqlcmd + " -u " + user + \
                    " --password=SHS13mgr " + f + " -r " + fsql
                cmdlog = sqlcmd + " -u " + user + " " + f + " -r " + fsql
            else:
                cmd = ""
                cmdlog = cmd
            os0.trace_debug("$", cmdlog)
            os0.muteshell(cmd, simulate=self.dry_run)

            if os.path.isfile(fsql):
                os0.wlog(" ", fsql)
                self.add_2_ftp(fsql)
            else:
                os0.wlog("  file", fsql, "not found!!!")

            self.purge_db(dbtype, f)

    def purge_db(self, dbtype, f):
        if self.sql_ext != self.pre_ext:
            self.change_file_ext(f)

        if f[6:9] > "000" and f[6:9] <= "086":
            deltatm = 30
        else:
            deltatm = 60
        dtc = date.today() - timedelta(deltatm)
        os0.wlog("  removing file older than", dtc.strftime("%Y-%m-%d"))
        fzip_fn = f + self.tar_ext
        force_change_ext = False
        for i in range(180, deltatm, -1):
            dtc = date.today() - timedelta(i)
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

        cmd = "tar -c" + self.tar_opt + "f " + fzip_fn + " " + fsql
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
        dts = date.today().strftime("%Y%m%d")
        fsql_nodel = f + "-" + dts + self.sql_ext
        f_ids = glob.glob(fsql)
        for fsql in f_ids:
            if fsql != fsql_nodel:
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

    def exec_bck(self):
        # Close files list
        self.ls_fd.close()
        self.set_chdir("/root")
        # Copy files list too
        self.ftp_fd.write(
            "put {0} {0}.tmp\n".format(os.path.basename(self.flist)))
        self.ftp_fd.close()
        self.ftp_fd = None
        fn = os.path.basename(self.ftp_cfn)
        if _platform == "win32":
            cmd = "ftp"
            p1 = "-s:" + fn
            p2 = self.bck_host
        else:
            cmd = "sftp"
            p1 = "-b" + fn
            p2 = "root@" + self.bck_host
        cmd = cmd + " " + p1 + " " + p2
        os0.muteshell(cmd, simulate=self.dry_run, tlog=True)
        if not self.dry_run:
            # os.remove(self.ftp_cfn)
            # os.remove(self.flist)                               # Delete
            # files list
            cmd = "ssh {0} \"cat {1}.tmp>>{1}; rm {1}.tmp\"".format(
                self.bck_host, self.flist)
            os0.muteshell(cmd, keepout=os0.debug_mode, tlog=True)
            cmd = "ssh root@" + self.bck_host + " \"at -f ./restdb now\""
            os0.muteshell(cmd, keepout=os0.debug_mode, tlog=True)

    def chdir(self, path):
        # Change root dir
        lpath = os0.setlfilename(path)
        os0.wlog(" [{0}]".format(lpath))
        self.set_chdir(lpath)
        self.ftp_rootdir = lpath
        self.ftp_dir = ""
        return lpath

    def set_chdir(self, path):
        # Exec chdir and store into ftp script
        os.chdir(path)
        if self.ftp_fd:
            self.ftp_fd.write("lcd {0}\n".format(path))
            self.ftp_fd.write("cd {0}\n".format(path))

    def add_2_ftp(self, fl):
        # Add filename to ftp file list
        # Extract subdir if supplied
        p = os.path.dirname(fl)
        fn = os.path.basename(fl)                               # Just filename
        # No dir supplied
        if p == "":
            # If prior subdir ..
            if self.ftp_dir != "":
                # .. return to root dir
                self.set_chdir(self.ftp_rootdir)
                # Forget prior subdir
                self.ftp_dir = ""
            fqn = self.ftp_rootdir + '/' + fl
        elif p[0:1] == '/' or p[0:1] == '.':
            fqn = p + '/' + fn
            fqn = self.ftp_rootdir + '/' + fn
            # Set local directory
            self.set_lchdir(p)
            self.ftp_dir = p
        else:
            fqn = self.ftp_rootdir + '/' + p + '/' + fl
            if p != self.ftp_dir:                             # Change subdir
                # Make full dir path (root + sub)
                lpath = self.ftp_rootdir + '/' + p
                self.set_chdir(lpath)                       # Set directory
                self.ftp_dir = p                            # Remember subdir
        self.ls_fd.write("{0}\n".format(fqn))
        self.ftp_fd.write("put {0}\n".format(fn))


def main():
    """Tool main"""
    sts = 0
    # pdb.set_trace()
    ctx = parse_args(sys.argv[1:])
    dbg_mode = ctx['dbg_mode']
    BM = Backup_Mirror(dbg_mode)
    if ctx.get('alt', False):
        BM.bck_host = BM.mirrorhost
#
# Backup postgres database
    if BM.pgdir:
        BM.chdir(BM.pgdir)
        dblist = BM.gen_db_list("psql", "openerp", "psql")
        if ctx['db_name'] != "":
            if ctx['db_name'] in dblist:
                dblist = []
                dblist.append(ctx['db_name'])
            else:
                dblist = []
        for db in dblist:
            BM.init_bck(BM.chdir(BM.pgdir))
            BM.bck_db("psql", [db], "openerp", "pg_dump")
            BM.exec_bck()
#
# Backup mysql database
    if BM.mysqldir:
        BM.init_bck(BM.chdir(BM.mysqldir))
        # BM.chdir("/var/lib/mysql")
        dblist = BM.gen_db_list("mysql", "root", "mysql")
        if ctx['db_name'] != "":
            if ctx['db_name'] in dblist:
                dblist = []
                dblist.append(ctx['db_name'])
            else:
                dblist = []
        BM.bck_db("mysql", dblist,  "root", "mysqldump")
        BM.exec_bck()

    os0.wlog("Backup DB ended.")
    return sts

if __name__ == "__main__":
    # if running detached
    # if os.isatty(0):
    #     dbg_mode = False
    # else:
    #     dbg_mode = True
    dbg_mode = True
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
