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
import ConfigParser
from os0 import os0
import glob
from sys import platform as _platform
import platform
from datetime import datetime
from zarlib import parse_args, read_config, default_conf
from zarlib import create_params_dict


__version__ = "2.1.17"


def version():
    return __version__


class Backup_Mirror:

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
        self.ftp_cfn = homedir + "/" + cfg_obj.get(s, "ftp_script")
        self.flist = homedir + "/" + cfg_obj.get(s, "list_file")    # File list
        os0.set_tlog_file(cfg_obj.get(s, "tracelog"))
        # Log begin execution
        os0.wlog("Backup configuration files", __version__)
        # Simulate backup
        self.dry_run = True
        if self.hostname == self.prodhost:
            os0.wlog("Running on production machine")
            self.bck_host = self.devhost
            self.dry_run = False
            self.fconf = homedir + "/" + \
                cfg_obj.get(s, "data_translation")
        elif self.hostname == self.mirrorhost:
            os0.wlog("Running on mirror machine")
            self.bck_host = self.devhost
            self.dry_run = False
            self.fconf = homedir + "/" + \
                cfg_obj.get(s, "no_translation")
        elif self.hostname == self.devhost:
            os0.wlog("This command cannot run on development machine")
            self.bck_host = self.prodhost
        else:
            os0.wlog("Unknown machine - Command aborted")
            raise Exception("Command aborted due unknown machine")

        self.ftp_rootdir = ""                                   # No root dir
        self.ftp_dir = ""                                       # No subdir

        self.ftp_fd = open(self.ftp_cfn, "w")
        self.ls_fd = open(self.flist, "w")
        dtc = datetime.today()
        self.ls_fd.write("# {0}\n".format(dtc.strftime("%Y%m%d")))

    def add_2_ftp(self, fl):
        # Add filename to ftp file list
        lx = ("cldb",    "bckconf",
              "bckdb",   "bckdb.py",  "bckwww",
              "purgedb", "restconf",  "restconf.py",
              "restdb",  "restdb.py", "restwww",
              "statdb",  ".zar.conf")
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
                os0.muteshell(cmd, simulate=self.dry_run)
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
            os0.muteshell(cmd, simulate=self.dry_run)
        if fn == "restconf" or fn == "restconf.py":
            self.ftp_fd.write("-rm {0}.bak\n".format(fn))
            self.ftp_fd.write("-rename {0} {0}.bak\n".format(fn))
            self.ftp_fd.write("put {0}\n".format(fn))
        elif fn == "restconf.ini" or fn == "restconf-0.ini":
            self.ftp_fd.write("-rm {0}.bak\n".format(fn))
            self.ftp_fd.write("-rename {0} {0}.bak\n".format(fn))
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
        os0.muteshell(cmd, simulate=self.dry_run, tlog=True)
        if not self.dry_run:
            os.remove(self.ftp_cfn)
            # Delete files list
            os.remove(self.flist)
            cmd = "ssh root@" + self.bck_host + " \"./restconf.py\""
            os0.muteshell(cmd, keepout=os0.debug_mode, tlog=True)


def main():
    """Tool main"""
    sts = 0
    # pdb.set_trace()
    ctx = parse_args(sys.argv[1:])
    dbg_mode = ctx['dbg_mode']
    BM = Backup_Mirror(dbg_mode)
    if ctx.get('alt', False):
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
        if os.path.isfile(fl):
            os0.wlog(" ", fl)
            BM.add_2_ftp(fl)
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
    dbg_mode = True    # temporary
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
