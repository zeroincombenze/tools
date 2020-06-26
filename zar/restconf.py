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
     Restore files & scripts from Production Machine, on Development Machine
     Make 2 server quite identical, ready to use
     May be used to create a mirror server of Zeroincombenze®
"""


# import pdb
import os
import os.path
import sys
from subprocess import call
import string
import re
from . import zarlib
try:
    from os0 import os0
except ImportError:
    import os0


__version__ = "1.3.34"


def version():
    return __version__


class Restore_Image:

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
        os0.wlog("Restore configuration files", __version__)
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
        self.pid = os.getpid()
        self.ftp_rootdir = ""
        self.ftp_dir = ""
        self.dbtype = ""
        self.create_dict()

    def create_dict(self):
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
                    line = re.sub('\\s+', ' ', line).strip()
                    f = string.split(line, ' ')
                    self.add_dict_entr(f[0], f[1], f[2])
                line = cnf_fd.readline()
        except:
            os0.wlog("No dictionary file", self.fconf, "found!")

    def add_dict_entr(self, name, src, tgt):
        self.seed = self.seed + 1
        key = "{0:06d}".format(self.seed)
        val = (src, tgt)
        if name in self.dict:
            self.dict[name].append(key)
        else:
            self.dict[name] = [key]
        self.xtl[key] = val
        # os0.wlog("> s|{0}|{1}|g {2}!".format(src, tgt, name))

    def search4item(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return None

    def restore_file(self, fqn):
        # Extract dir if supplied
        p = os.path.dirname(fqn)
        f = os.path.basename(fqn)                               # Just filename
        # No dir supplied
        if p == "":
            p = self.ftp_dir
        if p != self.ftp_dir:                                   # Change dir
            self.chdir(p)                                       # Set directory
        fzero = False
        fexts = False
        fn = "{0}.new".format(f)
        ftmp = "{0}.tmp".format(f)
        fbak = "{0}.bak".format(f)
        try:
            fn_fd = open(fn, 'r')
            # Go to end of file
            fn_fd.seek(0, os.SEEK_END)
            # File len = 0 ?
            if fn_fd.tell() == 0:
                fzero = True
            # Go to begin of file
            fn_fd.seek(0, 0)
            # Read entire file
            fn_str = fn_fd.read()
            fn_fd.close()
        except:
            fzero = True
        if fzero:
            os0.wlog("  file", fn, "empty!!!")
        else:
            os0.wlog(" ", fn, "->", fqn)
            # Search for text substitution
            key_ids = self.search4item(f)
            if key_ids:
                # Text couples for substitution
                for key in key_ids:
                    src = self.xtl[key][0]
                    tgt = self.xtl[key][1]
                    # print "[{0} >subst/{1}/{2}/".format(fqn, src, tgt)
                    os0.wlog(" ", fqn, ":", src, "->", tgt)
                    # Substitute text in file
                    fn_str = fn_str.replace(src, tgt)
                ftmp_fd = open(ftmp, 'w')
                # write file with substitutions
                ftmp_fd.write(fn_str)
                ftmp_fd.close()
            else:
                # Rename file.new -> file.tmp
                os.rename(fn, ftmp)
            try:
                f_fd = open(f, 'r')
                f_fd.close()
                fexts = True
                with open(os.devnull, "w") as fdnull:
                    cmd = "diff"
                    p1 = f
                    p2 = ftmp
                    sts = call([cmd, p1, p2], stdout=fdnull, stderr=fdnull)
                    # New file for upgrade
                    if sts > 0:
                        os0.wlog("   file", f, "upgraded!!!")
                    else:
                        os0.wlog("   file", f, "not changed.")
                        fzero = True
                    fdnull.close()
            except:
                os0.wlog("   file", f, "new!!!")

        try:
            # Delete file.new (if exist)
            os.remove(fn)
        except:
            pass
        if fzero:                                               # No upgrade
            try:
                # Delete file.tmp (if exist)
                os.remove(ftmp)
            except:
                pass
        else:                                                   # Upgrade
            try:
                # Delete file.bak (if exist)
                os.remove(fbak)
            except:
                pass
            if fexts:
                # Rename file -> file.bak
                os.rename(f, fbak)
            if not self.dry_run:
                # Rename file.tmp -> file
                os.rename(ftmp, f)

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
    ctx = zarlib.parse_args(sys.argv[1:],
                            version=version(),
                            doc=__doc__)
    if ctx['do_list']:
        print ctx['saveset_list']
        return sts
    RI = Restore_Image(ctx)
    f_alrdy_run = zarlib.check_if_running(ctx, RI.pid)
    if f_alrdy_run:
        os0.wlog("({0}) ***Another instance is running!!!".format(RI.pid))
    try:
        ls_fd = open(RI.flist, "r")
    except:
        raise Exception("Command aborted: file list not found!!!")
    file_2_restore = []
    fl = ls_fd.readline()
    while fl != "":
        i = fl.rfind('\n')
        if i >= 0 and fl[0:1] != '#':
            f = fl[0:i]
            file_2_restore.append(f)
        fl = ls_fd.readline()
    # Restore files
    for fl in file_2_restore:
        fn = os.path.basename(fl)
        if fn != "restconf" \
                and fn != "restconf.py" \
                and fn != "restconf.ini" \
                and fn != "restconf-0.ini":
            f = "{0}.new".format(fl)
            if os.path.isfile(f):
                RI.restore_file(fl)
            else:
                os0.wlog("  file", fl, "not found!!!")
    return sts


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
