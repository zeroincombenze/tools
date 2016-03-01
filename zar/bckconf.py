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
     Back-up files & scripts from Production Machine to Development Machine
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
from datetime import datetime


__version__ = "2.1.16.15"
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
LX_OPT_CFG_S = ('dbg_mode', 'db_name', 'simulate')
DEFDCT = {}


def version():
    return __version__


#############################################################################
# Custom parser functions
#
def default_conf():
    """Default configuration values"""
    DEFDCT = {}
    a = os.path.basename(__file__)
    i = a.rfind('.py')
    if i >= 0:
        a = a[0:i]
    # Restore command
    if a[0:4] == "rest":
        b = "bck" + a[4:]
    else:
        b = a
    DEFDCT['appname'] = a
    DEFDCT['bckapp'] = b
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
                        dest="simulate",
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
    prm = create_def_params_dict(opt_obj, conf_obj)
    # s = "options"
    for p in ('alt', ):
        if hasattr(opt_obj, p):
            prm[p] = getattr(opt_obj, p)
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


class Backup_Mirror:

    def _init_conf(self):
        # pdb.set_trace()
        a = os.path.basename(__file__)
        i = a.rfind('.py')
        if i >= 0:
            a = a[0:i]
        # Restore command
        if a[0:4] == "rest":
            b = "bck" + a[4:]
        else:
            b = a
        cfg_obj = ConfigParser.SafeConfigParser({"appname": a,
                                                 "bckapp": b})
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
        cfg_obj.read('zar.conf')
        return cfg_obj

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
        # PC for test & debug
        self.PChost = "PC0004"
        homedir = os.path.expanduser("~")
        # Temporary ftp command script
        self.ftp_cfn = homedir + "/" + cfg_obj.get(s, "ftp_script")
        self.flist = homedir + "/" + cfg_obj.get(s, "list_file")    # File list
        os0.set_tlog_file(cfg_obj.get(s, "tracelog"))
        # Log begin execution
        os0.wlog("Backup configuration files", __version__)
        # Simulate backup
        self.simulate = True
        if self.hostname == self.prodhost:
            os0.wlog("Running on production machine")
            # Backup onto prod machine
            self.bck_host = "shsdev16"
            self.simulate = False                               # Real backup
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
        elif self.hostname == self.PChost:
            os0.wlog("Running on PC just for test")
            # Backup onto dev machine (just for test)
            self.bck_host = "95.110.187.135"
        else:
            os0.wlog("Unknown machine - Command aborted")
            raise Exception("Command aborted due unknown machine")

        self.ftp_rootdir = ""                                   # No root dir
        self.ftp_dir = ""                                       # No subdir

        self.ftp_fd = open(self.ftp_cfn, "w")
        self.ls_fd = open(self.flist, "w")
        dtc = datetime.today()
        self.ls_fd.write("# {0}\n".format(dtc.strftime("%Y%m%d")))

    def add_2_ftp(self, fl, alt=None):
        # Add filename to ftp file list
        lx = ("cldb",    "bckconf",
              "bckdb",   "bckdb.py",  "bckwww",
              "purgedb", "restconf",  "restconf.py",
              "restdb",  "restdb.py", "restwww",
              "statdb",  "zar.conf")
        # Extract subdir if supplied
        p = os.path.dirname(fl)
        fn = os.path.basename(fl)                               # Just filename
        if p == "" and os.path.dirname(__file__) != "" \
                and (fn == "restconf.py" or fn == "restdb.py"):
            os0.trace_debug("Development & Testing software execution!")
            p = os.path.dirname(__file__)
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
            if fn in lx:
                cmd = "chmod +x {0}".format(fqn)
                os0.trace_debug("$ ", cmd)
                os0.muteshell(cmd, simulate=self.simulate)
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
        if fn == "restconf.py" or fn == "restdb.py":
            cmd = "chmod +x {0}".format(fqn)
            os0.trace_debug("$ ", cmd)
            os0.muteshell(cmd, simulate=self.simulate)
        if fn == "restconf" or fn == "restconf.py":
            self.ftp_fd.write("-rm {0}.bak\n".format(fn))
            self.ftp_fd.write("-rename {0} {0}.bak\n".format(fn))
            self.ftp_fd.write("put {0}\n".format(fn))
        elif fn == "restconf.ini" or fn == "restconf-0.ini":
            self.ftp_fd.write("-rm {0}.bak\n".format(fn))
            self.ftp_fd.write("-rename {0} {0}.bak\n".format(fn))
            if alt:
                if fn == "restconf.ini":
                    self.ftp_fd.write("put restconf-0.ini {0}\n".format(fn))
                elif fn == "restconf-0.ini":
                    self.ftp_fd.write("put restconf.ini {0}\n".format(fn))
            else:
                self.ftp_fd.write("put {0}\n".format(fn))
        else:
            self.ftp_fd.write("put {0} {0}.new\n".format(fn))

    def chdir(self, path):
        # Change root dir
        lpath = os0.setlfilename(path)
        os0.wlog(" [{0}]".format(lpath))
        self.set_chdir(lpath)
        self.ftp_rootdir = lpath
        self.ftp_dir = ""

    def set_chdir(self, path):
        # Exec chdir and store into ftp script
        os.chdir(path)
        self.ftp_fd.write("lcd {0}\n".format(path))
        self.ftp_fd.write("cd {0}\n".format(path))

    def set_lchdir(self, path):
        self.ftp_fd.write("lcd {0}\n".format(path))

    def exec_bck(self):
        # Close files list
        self.ls_fd.close()
        self.set_chdir("/root")
        # Copy files list too
        self.ftp_fd.write("put {0}\n".format(self.flist))
        self.ftp_fd.close()
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
        os0.muteshell(cmd, simulate=self.simulate, tlog=True)
        if not self.simulate:
            os.remove(self.ftp_cfn)
            # Delete files list
            os.remove(self.flist)
            cmd = "ssh root@" + self.bck_host + " \"./restconf.py\""
            os0.muteshell(cmd, keepout=os0.debug_mode, tlog=True)


def main():
    """Tool main"""
    sts = 0
    # pdb.set_trace()
    prm = parse_args(sys.argv[1:])
    dbg_mode = prm['dbg_mode']
    BM = Backup_Mirror(dbg_mode)
    if prm.get('alt', False):
        BM.bck_host = BM.mirrorhost
# Backup files in root directory
    BM.chdir("/root")
    file_2_backup = ["av_php",   "bckconf",     "bckconf.py",
                     "bckdb",    "bckdb.py",    "bckwww",
                     "cldb",     "purgedb",
                     "restconf", "restconf.py",
                     "restconf.ini",            "restconf-0.ini",
                     "restdb",   "restdb.py",   "restwww",
                     "ssl_certificate",         "statdb"]
    for fl in file_2_backup:
        msgalt = ""
        if fl == "restconf-0.ini" or fl == "restconf.ini":
            cmd = "touch restconf-0.ini"
            os0.trace_debug("$ ", cmd)
            os0.muteshell(cmd)
            msgalt = "(alt)"
        if os.path.isfile(fl):
            if prm.get('alt', False):
                os0.wlog(" ", fl, msgalt)
            else:
                os0.wlog(" ", fl)
            BM.add_2_ftp(fl, alt=prm.get('alt', False))
        else:
            os0.wlog("  file", fl, "not found!!!")
# Backup configuration file for http server
    BM.chdir("/etc/httpd/conf/sites-enabled")

    file_2_backup = glob.glob("/etc/httpd/conf/sites-enabled/*.conf")
    for f in file_2_backup:
        fl = os.path.basename(f)                            # Just filename
        if os.path.isfile(fl):
            os0.wlog(" ", fl)
            BM.add_2_ftp(fl)
        else:
            os0.wlog("  file", fl, "not found!!!")
# Backup web files
    BM.chdir("/var/www/html")
    file_2_backup = ["openerp/index.html"]
    for fl in file_2_backup:
        if os.path.isfile(fl):
            os0.wlog(" ", fl)
            BM.add_2_ftp(fl)
        else:
            os0.wlog("  file", fl, "not found!!!")
# Backup web certificates
    BM.chdir("/var/www/certs")
    file_2_backup = ["shop.zeroincombenze.it.crt",
                     "shop.zeroincombenze.it.CA.crt",
                     "shop.zeroincombenze.it.pem",
                     "19340476.crt",
                     "19340476.ca-bundle",
                     "19340476.pem",
                     "zi-oe.csr",
                     "zi-oe.pem",
                     "www.shs-av.com.csr",
                     "shs-av.com.pem",
                     "StartCom.CA.csr"]
    for fl in file_2_backup:
        if os.path.isfile(fl):
            os0.wlog(" ", fl)
            BM.add_2_ftp(fl)
        else:
            os0.wlog("  file", fl, "not found!!!")

# Backup postgres configuration files
    BM.chdir("/var/lib/pgsql/data")
    # file_2_backup = ["pg_hba.conf", ]
    # for fl in file_2_backup:
    #     if os.path.isfile(fl):
    #         os0.wlog(" ", fl)
    #         BM.add_2_ftp(fl)
    #     else:
    #        os0.wlog("  file", fl, "not found!!!")

    BM.exec_bck()
    return sts


if __name__ == "__main__":
    # if running detached
    if os.isatty(0):
        dbg_mode = False
    else:
        dbg_mode = True
    dbg_mode = False    # temporary
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
