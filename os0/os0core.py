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
r"""@package docstring
!OS routines for Linux, OpenVMS and Windows
!
!This module expands standard os.py module.
!os0 is platform independent and can run on Linux, OpenVMS and Linux.
!See http://www.zeroincombenze.eu about os differences.

This exports:
  - osx.setlfilename set local filename from URI (linux) filename

URI filename conversion rules
Case                Linux              Windows            OpenVMS
Simple file         myfile.ext         myfile.ext         myfile.ext
Abs pathname        /root/myfile.ext   \root\myfile.ext   [root]myfile.ext
Rel pathname        lib/myfile.ext     lib\myfile.ext     [.lib]myfile.ext
CWD pathname        ./myfile.ext       .\myfile.ext       []myfile.ext
Updir pathname      ../myfile.ext      ..\myfile.ext      [-]myfile.ext
Root file           /myfile.ext        \myfile.ext        [000000]myfile.ext
dotted pathname     /u/os.1.0/a.b.c    \u\os.1.0/a.b.c    [u.os^.1^.0]a^.^.b.c
hidden/leading dot  .myfile            .myfile            .myfile ??

executable          myfile             myfile.exe         myfile.exe
command file        myfile             myfile.bat         myfile.com
directory           mydir/             mydir              mydir.DIR

dev null            /dev/null          nul                NL0:
dev/disk/myfile     /dev/disk/myfile   c:\myfile          disk:[000000]myfile
system disk         /c/temp/myfile     c:\temp\myfile     c:[temp]myfile

Notes:
1.URL username (user@) is not supported by this version
2.URL port number o service (http: ftp:) is not supported by this version
3.URL server domain (//server) is not supported by this version
4.URL character encoding (%%20) is not supported by this version
5.Linux has not disk device in pathname; in order to manager Windows and
  OpenVMS devices here is used /dev/disk where disk may be a letter in Windows
  or a name in OpenVMS.
  Both Windows and OpenVMS use colon (:) at the end of disk device in local
  pathname (see last but one example above)
6.Here is also implemented a brief form for disk device, if exist on hosting
  machine
  Brief form is /dev/pathname like /c/windows/ or /sys$sysdevice/sys0/
  This brief form may be not universal translatable (see last example above)
7.Updir (..) may be recursive -> ../../myfile -> ..\..\myfile -> [-.-]myfile
8.Home dir (~/myfile) is no supported by this version
9.OpenVMS logical names use dollar sign, such as sys$sysdevice;
  in Linux dollar start a macro
  Need to verify about some trouble
10.OpenVMS files have version; syntax is 'myfile.exe;ver' where ';ver'
   can be omitted
   No any other OS has this feature, so in version of module there is no
   support for filename version

"""

import os
import os.path
import sys
import logging
import inspect
from sys import platform as _platform
from subprocess import call
# from datetime import datetime


__version__ = "0.2.11"


class Os0():

    def __init__(self, doinit=False):
        """Module initialization"""
        self.LFN_FLAT = 0
        self.LFN_EXE = 1
        self.LFN_CMD = 2
        self.LFN_DIR = 4
        self.PYCODESET = 'utf-8'
        self.tlog_fn = None
        if not hasattr(self, 'fh'):
            self.fh = None
        if not hasattr(self, 'ch'):
            self.ch = None

        self.debug_mode = False
        self.homedir = os.path.expanduser("~")
        bg = os.path.basename(inspect.getfile(sys._getframe(1)))
        i = bg.rfind('.py')
        if i >= 0:
            bg = bg[0:i]
        self.bgout_fn = self.homedir + "/" + bg + \
            "-{0:08x}".format(os.getpid()) + ".out"
        self.bginp_fn = os.devnull
        if doinit:
            self.set_logger("")

        self._xtl_dev_win = {'null:': 'nul'}
        self._xtl_dev_vms = {'null:': 'NL0:'}

        if _platform == "OpenVMS":
            self.bginp_fn = self.setlfilename("/dev/null", self.LFN_FLAT)

    def set_codeset(self, cs):
        self.PYCODESET = cs

    def b(self, s):
        if isinstance(s, unicode):
            return s.encode(self.PYCODESET)
        return s

    def u(self, s):
        if isinstance(s, str):
            return unicode(s, self.PYCODESET)
        return s

    def str2bool(self, t, dflt):
        """Convert text to bool"""
        if isinstance(t, bool):
            return t
        elif t.lower() in ["true", "t", "1", "y", "yes", "on", "enabled"]:
            return True
        elif t.lower() in ["false", "f", "0", "n", "no", "off", "disabled"]:
            return False
        else:
            return dflt

    def nakedname(self, fn):
        """Return nakedename (without extension)"""
        i = fn.rfind('.')
        if i >= 0:
            j = len(fn) - i
            if j <= 4:
                fn = fn[:i]
        return fn

    def extract_device(self, filename):
        """Extract device name form path name (Windows and OpenVMS)"""
        if filename[0:5] == "/dev/":
            x = filename.split('/')
            dev = x[2] + ":"
            filename = ""
            i = 3
            while i < len(x):
                if i == 3:
                    filename = x[i]
                else:
                    filename = filename + '/' + x[i]
                i = i + 1
        elif _platform == "OpenVMS" or _platform == "win32":
            dev = ""
            i = filename.find('/')
            if i >= 0:
                x = filename.split('/')
                d = x[1] + ":"
                if len(x) > 1 and \
                        x[0] == "" and \
                        (os.path.exists(d) or
                         (_platform == "OpenVMS" and
                          os.path.exists(x[1]))):
                    dev = x[1] + ":"
                    filename = ""
                    for i in range(2, len(x)):
                        filename = filename + '/' + x[i]
        else:
            dev = ""
        return filename, dev

    def setlfn_win(self, filename, cnv_type):
        """Windows local filename"""
        filename, dev = self.extract_device(filename)
        if dev in self._xtl_dev_win:
            dev = self._xtl_dev_win[dev]

        filename = filename.replace('/', os.sep)
        if cnv_type == self.LFN_EXE:
            if filename[0: -4] != ".exe" and filename[0: -4] != ".EXE":
                filename = filename + ".exe"
        elif cnv_type == self.LFN_CMD:
            if filename[0: -4] != ".bat" and filename[0: -4] != ".BAT":
                filename = filename + ".bat"
        f = dev + filename
        return f

    def setlfn_linux(self, filename, cnv_type):
        """Posix/Linux local filename"""
        return filename

    def setlfn_vms(self, filename, cnv_type):
        """OpenVMs local filename"""
        filename, dev = self.extract_device(filename)
        if dev in self._xtl_dev_vms:
            dev = self._xtl_dev_vms[dev]

        x = filename.split('/')
        if len(x) > 1:
            if x[0] == "":
                sep1 = "["
                x[0] = "000000"
            else:
                sep1 = "[."
            fn = x[len(x) - 1]
            sep = sep1
            p = ""
            for i in range(0, len(x) - 1):
                if x[i] == "..":
                    p = p + sep + "-"
                elif x[i] == ".":
                    p = p + sep
                else:
                    p = p + sep + x[i].replace('.', "^.")
                sep = "/"
            p = p + "]"
            p = p.replace('//', '/')
            p = p.replace('/', '.')
            if p[0:8] == "[000000.":
                p = "[" + p[8:]
            elif p[0:3] == "[.-":
                p = "[-" + p[3:]
            elif p == "[.]":
                p = "[]"

            i = fn.rfind('.')
            if i >= 0:
                left = fn[0:i].replace('.', "^.")
                right = fn[i + 1:]
                fn = left + '.' + right
            filename = p + fn
        else:
            i = filename.rfind('.')
            if i >= 0:
                left = filename[0:i].replace('.', "^.")
                right = filename[i + 1:]
                filename = left + '.' + right
        if cnv_type == self.LFN_EXE:
            if filename[0: -4] != ".exe" and filename[0: -4] != ".EXE":
                filename = filename + ".exe"
        elif cnv_type == self.LFN_CMD:
            if filename[0: -4] != ".com" and filename[0: -4] != ".COM":
                filename = filename + ".com"
        elif cnv_type == self.LFN_DIR:
            if filename[0: -4] != ".dir" and filename[0: -4] != ".DIR":
                filename = filename + ".DIR"
        f = dev + filename
        return f

    def setlfilename(self, filename, cnv_type=None):
        """Convert URI name into local filename"""
        if cnv_type is None:
            cnv_type = self.LFN_FLAT
        # Translate Linux filename into local OS
        if _platform == "win32":
            return (self.setlfn_win(filename, cnv_type))
        elif _platform == "OpenVMS":
            return (self.setlfn_vms(filename, cnv_type))
        return (self.setlfn_linux(filename, cnv_type))

    def set_tlog_file(self, filename, new=False, dir4debug=None, echo=False):
        """Set tracelog filename
        If filename has not path, path is set to
        /var/log for Poisx/Linux, otherwise homedir
        @filename:        filename with or w/o path
        @new:             if True, create a new empty tracelog file
        @echo:            echo message onto console
        """
        if filename:
            p = os.path.dirname(filename)
            fn = os.path.basename(filename)
            if p == "~":
                p = self.homedir
            if p == "":
                if dir4debug is None:
                    dir4debug = self.debug_mode
                if dir4debug:
                    p = self.homedir
                elif _platform == "linux" or _platform == "linux2":
                    p = "/var/log"
                else:
                    p = self.homedir
            file_log = p + os.sep + fn
        else:
            file_log = filename
        self.set_logger(file_log, new=new, echo=echo)

    def set_logger(self, file_log, new=False, echo=False):
        """Set up python logger
        @file_log:        filename with or w/o path
        @new:             if True, create a new empty tracelog file
        @echo:            echo message onto console
        """
        # import pdb
        # pdb.set_trace()
        if self.fh:
            self.fh.flush()
            self.fh.close()
            if hasattr(self, '_logger'):
                self._logger.removeHandler(self.fh)
            self.fh = None
        if self.ch:
            self.ch.flush()
            self.ch.close()
            if hasattr(self, '_logger'):
                self._logger.removeHandler(self.ch)
            self.ch = None
        self.tlog_fn = file_log
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        if file_log:
            if new:
                fh = logging.FileHandler(file_log, 'w')
            else:
                fh = logging.FileHandler(file_log)
            if self.debug_mode:
                fh.setLevel(logging.DEBUG)
            else:
                fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self._logger.addHandler(fh)
            self.fh = fh
        if not file_log or echo:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            if self.debug_mode:
                ch.setLevel(logging.DEBUG)
            else:
                ch.setLevel(logging.INFO)
            ch.setFormatter(logging.Formatter('%(message)s'))
            self._logger.addHandler(ch)
            self.ch = ch

    def set_debug_mode(self, dbg_mode=None):
        """Set debug mode for tracelog"""
        if dbg_mode is None:
            dbg_mode = True
        self.debug_mode = dbg_mode
        if hasattr(self, 'fh') and self.fh:
            if self.debug_mode:
                self.fh.setLevel(logging.DEBUG)
            else:
                self.fh.setLevel(logging.INFO)
        if hasattr(self, 'ch') and self.ch:
            if self.debug_mode:
                self.ch.setLevel(logging.DEBUG)
            else:
                self.ch.setLevel(logging.INFO)

    def wlog(self, *args):
        """Write a log/debug message onto tracelog file"""
        txt = ""
        sp = ''
        for arg in args:
            try:
                if isinstance(arg, unicode):
                    txt = txt + sp + arg.encode('utf-8')
                elif isinstance(arg, str):
                    txt = txt + sp + arg
                else:
                    txt = txt + sp + str(arg).encode('utf-8')
            except:
                x = unichr(0x3b1) + unichr(0x3b2) + unichr(0x3b3)
                txt = txt + sp + x.encode('utf-8')
            sp = ' '
        self.trace_msg(txt, dbg_mode=False)

    def wlog1(self, *args):
        """Write a log/debug message onto tracelog file"""
        txt = ""
        for arg in args:
            try:
                if isinstance(arg, unicode):
                    txt = txt + arg.encode('utf-8')
                elif isinstance(arg, str):
                    txt = txt + arg
                else:
                    txt = txt + str(arg).encode('utf-8')
            except:
                x = unichr(0x3b1) + unichr(0x3b2) + unichr(0x3b3)
                txt = txt + x.encode('utf-8')
        self.trace_msg(txt, dbg_mode=False)

    def trace_debug(self, *args):
        """Likw wlog but only if debug mode is active """
        txt = ""
        sp = ''
        for arg in args:
            try:
                if isinstance(arg, unicode):
                    txt = txt + sp + arg.encode('utf-8')
                elif isinstance(arg, str):
                    txt = txt + sp + arg
                else:
                    txt = txt + sp + str(arg).encode('utf-8')
            except:
                x = unichr(0x3b1) + unichr(0x3b2) + unichr(0x3b3)
                txt = txt + sp + x.encode('utf-8')
            sp = ' '
        self.trace_msg(txt, dbg_mode=True)

    def trace_msg(self, txt, dbg_mode=None):
        if dbg_mode:
            self._logger.debug(txt)
        else:
            self._logger.info(txt)

    def muteshell(self, cmd, simulate=False, tlog=False, keepout=False):
        """Execute script file using OS shell and redirect output into file
        @simulate:        if true, simulate command without execute it
        @tlog:            class object with wlog method to trace; may be null
        @keepout:         if true, do not delete redirect output file
                          (ignored if simulate)
        """
        if tlog:
            self.wlog("> {0}".format(cmd))
        if _platform == "OpenVMS":
            # !!debug temporary!!
            if simulate:
                cmd = "write sys$output \"" + cmd + "\""
            bgout_mb, bginp_mb, bgerr_mb = os.popen3(cmd)
            bgout_mb.write("logout /brief")
            if simulate or keepout:
                stdout_fd = open(self.bgout_fn, "w")
                s = bginp_mb.read()
                stdout_fd.write(s)
                stdout_fd.close()
        else:
            stdout_fd = open(self.bgout_fn, "w")
            stdinp_fd = open(self.bginp_fn, "r")
            if simulate:
                cmd = "echo " + cmd
            call(cmd, stdin=stdinp_fd, stdout=stdout_fd, shell=True)
            stdout_fd.close()
            stdinp_fd.close()
            if not simulate and not keepout:
                os.remove(self.bgout_fn)

    @property
    def version(self):
        return __version__

Os0()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
