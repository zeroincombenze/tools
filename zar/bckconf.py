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
import glob
from sys import platform as _platform
from datetime import datetime
from . import zarlib
try:
    from os0 import os0
except ImportError:
    import os0


__version__ = "1.3.34"


def version():
    return __version__


class Backup_Mirror:

    def __init__(self, ctx):
        self.hostname = ctx['hostname']
        os0.set_debug_mode(ctx['dbg_mode'])
        self.prodhost = ctx['production_host']
        self.devhost = ctx['development_host']
        self.mirrorhost = ctx['mirror_host']
        self.pgdir = ctx['pg_dir']
        self.mysqldir = ctx['mysql_dir']
        homedir = os.path.expanduser("~")
        self.ftp_cfn = homedir + "/" + ctx['ftp_script']
        self.flist = homedir + "/" + ctx['list_file']
        os0.set_tlog_file(ctx['logfn'])
        # Log begin execution
        os0.wlog("Backup configuration files", __version__)
        # Simulate backup
        self.dry_run = ctx['dry_run']
        if ctx['saveset'] == "bckdb" or \
                ctx['saveset'] == "bckconf" or \
                ctx['saveset'] == "bckwww":
            if self.hostname == self.prodhost:
                os0.wlog("Running on production machine")
                if ctx['alt']:
                    self.bck_host = self.mirrorhost
                    self.fconf = homedir + "/" + \
                        ctx['no_translation']
                else:
                    self.bck_host = self.devhost
                    self.fconf = homedir + "/" + \
                        ctx['data_translation']
            elif self.hostname == self.mirrorhost:
                os0.wlog("Running on mirror machine")
                if ctx['alt']:
                    self.bck_host = self.prodhost
                    self.fconf = homedir + "/" + \
                        ctx['no_translation']
                else:
                    self.bck_host = self.devhost
                    self.fconf = homedir + "/" + \
                        ctx['data_translation']
            elif self.hostname == self.devhost:
                os0.wlog("This command cannot run on development machine")
                if not ctx['dry_run']:
                    raise Exception("Command aborted due invalid machine")
            else:
                os0.wlog("Unknown machine - Command aborted")
                if not ctx['dry_run']:
                    raise Exception("Command aborted due unknown machine")
        elif ctx['saveset'] == "restdb" or \
                ctx['saveset'] == "restconf" or \
                ctx['saveset'] == "restwww":
            if self.hostname == self.prodhost:
                os0.wlog("This command cannot run on production machine")
                if not ctx['dry_run']:
                    raise Exception("Command aborted due production machine")
            elif self.hostname == self.mirrorhost:
                os0.wlog("Running on mirror machine")
                if ctx['alt']:
                    self.bck_host = self.prodhost
                    self.fconf = homedir + "/" + \
                        ctx['no_translation']
                else:
                    self.bck_host = self.devhost
                    self.fconf = homedir + "/" + \
                        ctx['data_translation']
            elif self.hostname == self.devhost:
                os0.wlog("Running on development machine")
                if ctx['alt']:
                    self.bck_host = self.mirrorhost
                    self.fconf = homedir + "/" + \
                        ctx['data_translation']
                else:
                    self.bck_host = self.devhost
                    self.fconf = homedir + "/" + \
                        ctx['data_translation']
            else:
                os0.wlog("Unknown machine - Command aborted")
                if not ctx['dry_run']:
                    raise Exception("Command aborted due unknown machine")
        # May be (.gz or .bz2)
        self.tar_ext = ctx['tar_ext']
        # May be (z or j)
        self.tar_opt = ctx['tar_opt']
        # May be (null or .sql)
        self.pre_ext = ctx['pre_ext']
        # May be (null or .sql)
        self.sql_ext = ctx['sql_ext']
        self.psql_uu = ctx['pgsql_user']
        self.psql_db = ctx['pgsql_def_db']
        self.mysql_uu = ctx['mysql_user']
        self.mysql_db = ctx['mysql_def_db']
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
    ctx = zarlib.parse_args(sys.argv[1:],
                            version=version(),
                            doc=__doc__)
    if ctx['do_list']:
        print ctx['saveset_list']
        return sts
    BM = Backup_Mirror(ctx)
# Backup files in root directory
    BM.chdir("/root")
    file_2_backup = ["av_php",   "bckconf",     "bckconf.py",
                     "bckdb",    "bckdb.py",    "bckwww",
                     "cldb",     "purgedb",
                     "restconf", "restconf.py",
                     "restconf.ini",            "restconf-0.ini",
                     "restdb",   "restdb.py",   "restwww",
                     "ssl_certificate",         "statdb",
                     "zarlib.py"]
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
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
