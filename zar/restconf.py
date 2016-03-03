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
import argparse
import ConfigParser
from os0 import os0
import platform
from subprocess import call
import string
import re


__version__ = "2.0.28.10"
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
