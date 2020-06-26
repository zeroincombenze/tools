#!/usr/bin/env python
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
    Zeroincombenze® Archives Replica

    ZAR application can backup file and db from any directory
    and can do a restore over another machine and/or directory.
    ZAR can also build a mirror tree of source,
    setting appropriate change onto target site.
    Mirrored directory/machine is ready to use.
    ZAR is used by Zeroincombenze® to backup data and create mirror sites

    ZAR can run on posix OS (all flavour of Linux), on Windows and OpenVMS.
    It requires python installed on machine
    On some OS additional software is required.
    On OpenVMS zip and unzip should be installed
    On Windows, winrar shoud be installed to same reason

    All operations are based on saveset.
    A saveset is a set of files and/or DB to manage together
    Saveset are definded in .zar.conf file
"""

# import pdb
import os
import os.path
import sys
import argparse
import ConfigParser
import glob
# from sys import platform as _platform
# import platform
# from datetime import date, timedelta
import datetime
import re
import string
try:
    from os0 import os0
except ImportError:
    import os0
from . import zarlib_new as zarlib


__version__ = "1.3.34"
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
# return code
WOW_FAILED = 1
WOW_SUCCESS = 0


def version():
    return __version__


#############################################################################
# Custom parser functions
#
def default_conf():
    """Default configuration values"""
    DEFDCT = {}
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
        epilog="© 2015 by SHS-AV s.r.l."
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

    prm['_conf_obj'] = conf_obj
    prm['_opt_obj'] = opt_obj
    prm['__version__'] = __version__
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


class Backup_Mirror(zarlib.Zarlib):

    def __init__(self, cfg_obj, s):
        # homedir = os.path.expanduser("~")
        # Temporary ftp command script
        self.ftp_cfn = cfg_obj.get(s, "ftp_script")
        self.flist = cfg_obj.get(s, "list_file")    # File list

        self.ftp_dir = ""

        dtc = datetime.today()
        self.ls_fd.write("# {0}\n".format(dtc.strftime("%Y%m%d")))

        return

#
    def init_bck(self, prm, lpath=None):
        if prm['src_host'] != prm['tgt_host']:
            self.ftp_fd = open(self.ftp_cfn, "w")
            self.ls_fd = open(self.flist, "w")

        self.ftp_dir = ""
        if lpath:
            self.chdir(lpath)

#
    def add_2_ftp(self, fl, prm):
        # Add filename to ftp file list
        p = os.path.dirname(fl)
        fn = os.path.basename(fl)
        if p == "" and self.ftp_dir != "":
            p = self.ftp_dir
        if p == "":
            p = os.getcwd()
        if p[0:1] == '/' or p[0:1] == '.':
            fqn = p + '/' + fn
        else:
            fqn = self.ftp_dir + '/' + p + '/' + fl
        p = os.path.dirname(fqn)
        if p != self.ftp_dir:
            self.chdir(p)

        os0.wlog(self.pid, "  backup", fn)
        if prm['cp_mode'] == "overlap":
            self.ftp_fd.write("put {0}\n".format(fn))
        elif prm['cp_mode'] == "keepold":
            self.ftp_fd.write("-rm {0}.bak\n".format(fn))
            self.ftp_fd.write("-rename {0} {0}.bak\n".format(fn))
            self.ftp_fd.write("put {0}\n".format(fn))
        else:
            prm['cp_mode'] = "save"
            self.ftp_fd.write("put {0} {0}.new\n".format(fn))
        self.ls_fd.write("{0}\t{1}\n".format(fqn, prm['cp_mode']))
        return

#
    def chdir(self, path):
        # Change root dir
        lpath = os0.setlfilename(path)
        os0.wlog(self.pid, " directory [{0}]".format(lpath))
        self.set_chdir(lpath)
        self.ftp_dir = lpath

#
    def set_chdir(self, path):
        # Exec chdir and store into ftp script
        os.chdir(path)
        self.ftp_fd.write("lcd {0}\n".format(path))
        self.ftp_fd.write("cd {0}\n".format(path))

#
    def set_lchdir(self, path):
        self.ftp_fd.write("lcd {0}\n".format(path))

#
    def Backup_files(self, cfg_obj, sset, prm):
        path_list = cfg_obj.get(sset, "path")
        if path_list == "":
            os0.wlog(self.pid, "No file declared!!")
            if not prm['mute']:
                print "***No file declared file!!!"
            return
        prm['cmd_bck'] = cfg_obj.get(sset, "cmd_bck").replace('{}', '{0}')
        prm['cp_mode'] = cfg_obj.get(sset, "cp_mode")
        path_list = path_list.split(',')
        self.init_bck(prm, path_list[0])
        file_2_backup = []
        for path in path_list:
            if os.path.isdir(path):
                path = os.path.join(path, "*")
            if prm['specimen'] == "file":
                file_2_backup = file_2_backup + glob.glob(path)
            elif prm['specimen'] == "dir":
                for root, dirs, files in os.walk(path):
                    for f in files:
                        file_2_backup = file_2_backup + os.path.join(root, f)
            else:
                pass
            if prm['cmd_bck'] != "":
                cmd = prm['cmd_bck'].replace('{0}', path)
                os0.trace_debug("> ", cmd)
                os0.muteshell(cmd, simulate=prm['simulate'])

        self.set_chdir(path_list[0])
        for f in file_2_backup:
            if os.path.isfile(f):
                self.add_2_ftp(f, prm)
            elif os.path.isdir(f):
                os0.wlog(self.pid, "   dir", f, "skipped")
            else:
                os0.wlog(self.pid, "   file", f, "not found!!!")
        return


class Restore_Image(zarlib.Zarlib):

    # def __init__(self, cfg_obj, s):
    def __init__(self):
        # homedir = os.path.expanduser("~")
        # Temporary ftp command script
        # self.ftp_cfn = homedir + "/" + cfg_obj.get(s, "ftp_script")
        # self.flist = homedir + "/" + cfg_obj.get(s, "list_file") # File list
        # self.fxlts = homedir + "/" + \
        #     cfg_obj.get(s, "data_translation")  # Translation file

        # self.ftp_rootdir = ""                                   # No root dir
        # self.ftp_dir = ""                                       # No subdir
        # self.create_xlts_dict()
        return

    def create_xlts_dict(self):
        self.dict = {}
        self.xlt = {}
        self.seed = 0
        try:
            cnf_fd = open(self.fxlts, "r")
            line = cnf_fd.readline()
            while line != "":
                i = line.rfind('\n')
                if i >= 0:
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
        self.xlt[key] = val


Restore_Image()


def main():
    """Tool main"""
    sts = WOW_SUCCESS
    # pdb.set_trace()
    prm = parse_args(sys.argv[1:])
    dbg_mode = prm['dbg_mode']
    conf_fn = prm['conf_fn']
    mute = prm['mute']
    list_mode = prm['list']
    opt_obj = prm['_opt_obj']
    Z = zarlib.Zarlib(dbg_mode)
    if dbg_mode:
        print __version__
    if prm['xtall']:
        sts = Z.install(prm)
        sys.exit(sts)

    if not os.path.isfile(conf_fn):
        print "Configuration file {0} not found!".format(conf_fn)
    f_alrdy_run = Z.check_if_running()

    cfg = Z.get_conf(conf_fn)
    s = "Environment"
    os0.set_tlog_file(cfg.get(s, "tracelog"))
    if prm['simulate']:
        opt = "in simulating mode"
    else:
        opt = ""
    # Log begin execution
    os0.wlog(Z.pid, "ZAR {0} beginning".format(__version__), opt)

    if f_alrdy_run:
        os0.wlog(Z.pid, "Another instance is running!!")
        if not mute:
            print "***Another instance is running!!!"
        raise SystemExit

    saveset_list = cfg.get(s, "saveset_list")
    if saveset_list == "":
        os0.wlog(
            Z.pid, "No saveset defined in {0} configuration file!!"
            .format(conf_fn))
        if not mute:
            print "***No saveset defined in {0} configuration file!!!"\
                .format(conf_fn)
        raise SystemExit

    saveset_list = saveset_list.split(',')
    if hasattr(opt_obj, "saveset"):
        sel_saveset = opt_obj.saveset
    else:
        sel_saveset = saveset_list
    for sset in saveset_list:
        s = sset.strip()
        prm['src_host'] = cfg.get(s, "source_host")
        prm['tgt_host'] = cfg.get(s, "target_host")
        prm['specimen'] = cfg.get(s, "specimen")
        if list_mode:
            if sset not in sel_saveset:
                opt = " (not selected)"
            else:
                opt = ""
            if Z.hostname == prm['src_host'] \
                    or Z.hostname == "localhost":
                print "Saveset {0}{1}: backup to {2}"\
                    .format(sset, opt, prm['tgt_host'])
            elif Z.hostname == prm['tgt_host'] \
                    or Z.hostname == "localhost":
                print "Saveset {0}{1}: restore from {2}"\
                    .format(sset, opt, prm['src_host'])
            else:
                print "Invalid saveset {0}: source={1}, target={2}"\
                    .format(sset, prm['src_host'], prm['tgt_host'])
        else:
            BM = Backup_Mirror(cfg, sset)
            # RI = Restore_Image(cfg, sset)
            if sset not in sel_saveset:
                if dbg_mode:
                    print "Saveset {0} not selected".format(sset)
                continue
            elif Z.hostname == prm['src_host'] \
                    or Z.hostname == "localhost":
                os0.wlog(
                    Z.pid,
                    "Saveset [{0}]: backup to {1}"
                    .format(sset, prm['tgt_host']))
                if not mute:
                    print "Saveset [{0}]: backup to {1}"\
                        .format(sset, prm['tgt_host'])
                if prm['specimen'] == "file" \
                        or prm['specimen'] == "dir":
                    BM.Backup_files(cfg, sset, prm)
            elif Z.hostname == prm['tgt_host'] \
                    or Z.hostname == "localhost":
                os0.wlog(
                    Z.pid,
                    "Saveset [{0}]: restore from {1}"
                    .format(sset, prm['src_host']))
                if not mute:
                    print "Saveset [{0}] restore from {1}"\
                        .format(sset, prm['src_host'])
            else:
                os0.wlog(Z.pid,
                         "Invalid saveset [{0}]: source={1}, target={2}"
                         .format(sset, prm['src_host'], prm['tgt_host']))
                print "Invalid saveset [{0}]: source={1}, target={2}"\
                    .format(sset, prm['src_host'], prm['tgt_host'])

    os0.wlog(Z.pid, "ZAR terminated!")
    return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    # if running detached
    if os.isatty(0):
        dbg_mode = False
    else:
        dbg_mode = True
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
