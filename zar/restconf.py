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
import ConfigParser
from os0 import os0
import platform
from subprocess import call
import string
import re
from zarlib import parse_args, read_config, default_conf
from zarlib import create_params_dict

__version__ = "2.0.29"


def version():
    return __version__


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
        self.ftp_cfn = homedir + "/" + cfg_obj.get(s, "ftp_script")
        self.flist = homedir + "/" + cfg_obj.get(s, "list_file")    # File list
        os0.set_tlog_file(cfg_obj.get(s, "tracelog"))
        # Log begin execution
        os0.wlog("Restore configuration files", __version__)
        # Simulate backup
        self.dry_run = True
        if self.hostname == self.prodhost:
            os0.wlog("This command cannot run on production machine")
            self.bck_host = self.devhost
            raise Exception("Command aborted due production machine")
        elif self.hostname == self.mirrorhost:
            os0.wlog("Running on mirror machine")
            self.bck_host = self.prodhost
            self.dry_run = False
            self.fconf = homedir + "/" + \
                cfg_obj.get(s, "no_translation")
        elif self.hostname == self.devhost:
            os0.wlog("Running on development machine")
            self.bck_host = self.prodhost
            self.dry_run = False
            self.fconf = homedir + "/" + \
                cfg_obj.get(s, "data_translation")
        else:
            os0.wlog("Unknown machine - Command aborted")
            raise Exception("Command aborted due unknown machine")

        self.ftp_dir = ""                                       # No subdir
        self.create_dict()

    def create_dict(self):
        self.dict = {}
        self.xtl = {}
        self.seed = 0
        # pdb.set_trace()
        try:
            cnf_fd = open(self.fconf, "r")
            line = cnf_fd.readline()
            while line != "":
                i = line.rfind('\n')
                if i >= 0:
                    line = re.sub('\\s+', ' ', line).strip()
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
    ctx = parse_args(sys.argv[1:])
    dbg_mode = ctx['dbg_mode']
    RI = Restore_Image(dbg_mode)
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
    # if running detached
    if os.isatty(0):
        dbg_mode = False
    else:
        dbg_mode = True
    dbg_mode = True    # temporary
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
