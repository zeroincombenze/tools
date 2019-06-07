# -*- coding: utf-8 -*-
# Copyright (C) 2013-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
     Test module os0
     This module provide OS indipendent interface
     Can manage: linux, Windows and OpenVMS

     Execution test results:
     Date        Author      Linux           Windows        OpenVMS
     2015-01-27  antoniov    python V2.6.6   python V2.7.6  python V2.7.9
                             CentOS V6.5     Windows 7      OpenVMS-IA64 V8.4
     2016-07-01  antoniov    python 2.7.5
                             CentOS V7.0
"""
# from __future__ import print_function,unicode_literals
from __future__ import print_function
from past.builtins import basestring
from builtins import chr

# import pdb
import os
import os.path
from os0 import os0
from sys import platform as _platform
import sys
from zerobug import Z0BUG

MODULE_ID = 'os0'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "0.2.14.3"

TITLE = "os0 regression test. Version: " + __version__
FLOGTMP = "os0_test.log"


def version():
    return __version__


class RegressionTest:
    # Execute code tests os.path library at low level
    # The purpose is not test os.path module but OpenVMS version on module.
    # Local OpenVMS filesystem has some structure like Windows
    # (Windows inherited filesystem from old PDP/VMS)
    # This program is tested on Linux, Windows and OpenVMS platform
    # in order to verify results (see above header)
    def __init__(self, zarlib):
        self.Z = zarlib

    def SetUp(self, ctx):
        """Remove test log file if executed previous crashed test"""
        # Need debug mode to avoid security fault in Linux
        os0.set_debug_mode(True)

    def test_01(self, ctx):
        self.SetUp(ctx)
        fzero = False
        fexts = False
        if not ctx.get('dry_run', False):
            os0.set_tlog_file(FLOGTMP)
        tlog_pathname = os.path.join(os.environ['HOME'],
                                     FLOGTMP)
        sts = self.Z.test_result(ctx,
                                 "set logfile",
                                 tlog_pathname,
                                 os0.tlog_fn)
        if not ctx.get('dry_run', False):
            tlog_fd = open(os0.tlog_fn, 'w')
            tlog_fd.close()
            os0.set_tlog_file(FLOGTMP, new=True, echo=ctx['opt_echo'])
            try:
                tlog_fd = open(os0.tlog_fn, 'r')
                fexts = True
                tlog_fd.seek(0, os.SEEK_END)
                if tlog_fd.tell() == 0:
                    fzero = True
                tlog_fd.close()
            except:
                pass
        sts = self.Z.test_result(ctx,
                                 "new logfile (1)",
                                 True,
                                 fexts)
        sts = self.Z.test_result(ctx,
                                 "new logfile (2)",
                                 True,
                                 fzero)
        if os.path.isfile(tlog_pathname):
            os.remove(tlog_pathname)
        tlog_pathname = os.path.join('.',
                                     FLOGTMP)
        fzero = False
        fexts = False
        if not ctx.get('dry_run', False):
            os0.set_tlog_file(tlog_pathname, new=True, echo=ctx['opt_echo'])
            try:
                tlog_fd = open(os0.tlog_fn, 'r')
                fexts = True
                tlog_fd.seek(0, os.SEEK_END)
                if tlog_fd.tell() == 0:
                    fzero = True
                tlog_fd.close()
            except:
                pass
        sts = self.Z.test_result(ctx,
                                 "new logfile (3)",
                                 True,
                                 fexts)
        sts = self.Z.test_result(ctx,
                                 "new logfile (4)",
                                 True,
                                 fzero)
        if os.path.isfile(tlog_pathname):
            os.remove(tlog_pathname)
        tlog_pathname = os.path.join(self.Z.testdir,
                                     FLOGTMP)
        fzero = False
        fexts = False
        if not ctx.get('dry_run', False):
            os0.set_tlog_file(ctx['logfn'],
                              new=ctx['opt_new'],
                              echo=ctx['opt_echo'])
        if ctx.get('dry_run', False):
            os0.wlog("Since now, test messages are store in", os0.tlog_fn)
        return sts

    def test_02(self, ctx):
        fzero = False
        fexts = False
        if not ctx.get('dry_run', False):
            title = TITLE
            os0.trace_debug("- Inititializing ...")
            os0.set_debug_mode(False)
            os0.trace_debug("TEST FAILED!!!!")
            os0.set_debug_mode(True)
            os0.trace_debug("- Inititializing (2) ...")
            os0.wlog(title)
            os0.wlog("- os0 version:", os0.version)
            os0.wlog("- platform:", _platform)
            os0.set_tlog_file("os0_test.log", echo=ctx['opt_echo'])
            try:
                tlog_fd = open(os0.tlog_fn, 'r')
                fexts = True
                tlog_fd.seek(0, os.SEEK_END)
                if tlog_fd.tell() == 0:
                    fzero = True
                tlog_fd.close()
            except:
                pass
        sts = self.Z.test_result(ctx,
                                 "Check for empty tracelog",
                                 True,
                                 fexts)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "Check for empty tracelog",
                                     True,
                                     fzero)
        return sts

    def test_03(self, ctx):
        if not ctx.get('dry_run', False):
            wchar_string = u"- Unicode string àèìòù"
            os0.wlog(wchar_string)
            # if wlog fails follow statemente is not executed
        sts = self.Z.test_result(ctx,
                                 "Check for unicode support",
                                 True,
                                 True)
        if not ctx.get('dry_run', False):
            x = unichr(0x3b1) + unichr(0x3b2) + unichr(0x3b3)
            os0.wlog("- Greek letters", x)
        sts = self.Z.test_result(ctx,
                                 "- Greek letters",
                                 True,
                                 True)
        res = None
        ustr = None
        bstr = None
        if not ctx.get('dry_run', False):
            res = os0.str2bool('true', None)
        sts = self.Z.test_result(ctx,
                                 "str2bool(true)",
                                 True,
                                 res)
        if not ctx.get('dry_run', False):
            res = os0.str2bool('0', None)
        sts = self.Z.test_result(ctx,
                                 "str2bool(0)",
                                 False,
                                 res)
        if not ctx.get('dry_run', False):
            res = os0.str2bool(False, None)
        sts = self.Z.test_result(ctx,
                                 "str2bool(0)",
                                 False,
                                 res)
        if not ctx.get('dry_run', False):
            res = os0.str2bool('invalid', False)
        sts = self.Z.test_result(ctx,
                                 "str2bool(0)",
                                 False,
                                 res)
        if not ctx.get('dry_run', False):
            res = os0.nakedname('myfile')
        sts = self.Z.test_result(ctx,
                                 "nakedname(myfile)",
                                 'myfile',
                                 res)
        if not ctx.get('dry_run', False):
            res = os0.nakedname('myfile.py')
        sts = self.Z.test_result(ctx,
                                 "nakedname(myfile.py)",
                                 'myfile',
                                 res)
        if not ctx.get('dry_run', False):
            bstr = 'text àèìòù'
            ustr = u"text àèìòù"
            res = os0.u(bstr)
        sts = self.Z.test_result(ctx,
                                 "unicode(string)",
                                 ustr,
                                 res)
        sts = self.Z.test_result(ctx,
                                 "unicode(string)",
                                 ustr,
                                 os0.u(ustr))
        if not ctx.get('dry_run', False):
            bstr = 'text àèìòù'
            ustr = u"text àèìòù"
            res = os0.b(ustr)
        sts = self.Z.test_result(ctx,
                                 "bstring(string)",
                                 bstr,
                                 res)
        sts = self.Z.test_result(ctx,
                                 "bstring(string)",
                                 os0.b(bstr),
                                 res)
        return sts

    def test_04(self, ctx):
        if _platform == "win32":
            self.test_path_win(ctx)
        elif _platform == "OpenVMS":
            self.test_path_vms(ctx)
        else:
            self.test_path_linux(ctx)

    def test_05(self, ctx):
        if _platform == "win32":
            sts = self.test_fn_win(ctx)
        elif _platform == "OpenVMS":
            sts = self.test_fn_vms(ctx)
        else:
            sts = self.test_fn_linux(ctx)
        return sts

    def test_06(self, ctx):
        if not ctx.get('dry_run', False):
            if os.path.dirname(__file__) == "":
                if __file__ == "__main__.py":
                    cmd = "dir " + os0.setlfilename("../")
                else:
                    cmd = "dir " + os0.setlfilename("./")
            else:
                cmd = "dir " + os0.setlfilename(os.path.dirname(__file__))
            try:
                os.remove(os0.setlfilename(os0.bgout_fn))
            except:
                pass
            os0.muteshell(cmd, keepout=True)
            self.check_4_tkn_in_stdout(os.path.basename(__file__))
        sts = self.Z.test_result(ctx,
                                 "os0.dir",
                                 True,
                                 os.path.isfile(os0.bgout_fn))
        if not ctx.get('dry_run', False):
            if _platform == "win32":
                cmd = "del"
            elif _platform == "OpenVMS":
                cmd = "delete"
            else:
                cmd = "rm"
            cmd = cmd + " " + (os0.setlfilename(os0.bgout_fn))
            os0.muteshell(cmd, simulate=True, tlog=True)
            self.check_4_tkn_in_stdout(cmd)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "os0.del",
                                     True,
                                     os.path.isfile(os0.bgout_fn))
        if not ctx.get('dry_run', False):
            if not ctx.get('dry_run', False):
                cmd = "dir"
                os0.muteshell(cmd)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "os0.dir",
                                     False,
                                     os.path.isfile(os0.bgout_fn))
        return sts

    def test_path_splitdrive(self, txtid, fsrc, dtgt, ftgt, ctx):
        d, p = os.path.splitdrive(fsrc)
        if d != dtgt or p != ftgt:
            res = False
        else:
            res = True
        sts = self.Z.test_result(ctx,
                                 "Test %s: os.path.splitdrive%s->%s" % (txtid,
                                                                        dtgt,
                                                                        ftgt),
                                 True,
                                 res)
        return sts

    def test_path_linux(self, ctx):
        self.test_path_splitdrive("0.12",
                                  "myFile.ext",
                                  "", "myFile.ext",
                                  ctx)
        self.test_path_splitdrive("0.13",
                                  "/usr1/lib/myFile.ext",
                                  "", "/usr1/lib/myFile.ext",
                                  ctx)
        self.test_path_splitdrive("0.14",
                                  "//machine/usr1/lib/myFile.ext",
                                  "", "//machine/usr1/lib/myFile.ext",
                                  ctx)

#
    def test_path_vms(self, ctx):
        self.test_path_splitdrive("0.12",
                                  "myFile.ext",
                                  "", "myFile.ext")
        self.test_path_splitdrive("0.13",
                                  "[usr1.lib]myFile.ext",
                                  "", "[usr1.lib]myFile.ext")
        self.test_path_splitdrive("0.14",
                                  "/usr1/lib/myFile.ext",
                                  "", "/usr1/lib/myFile.ext")
        self.test_path_splitdrive("0.15",
                                  "machine::[usr1.lib]myFile.ext",
                                  "", "machine::[usr1.lib]myFile.ext")
        self.test_path_splitdrive("0.16",
                                  "//machine/usr1/lib/myFile.ext",
                                  "", "//machine/usr1/lib/myFile.ext")
        self.test_path_splitdrive("0.17",
                                  "sys$sysdevice:[usr1.lib]myFile.ext",
                                  "sys$sysdevice:", "[usr1.lib]myFile.ext")

#
    def test_path_win(self, ctx):
        self.test_path_splitdrive("0.12", "myFile.ext",
                                  "", "myFile.ext")
        self.test_path_splitdrive("0.13", "\\usr1\\lib\\myFile.ext",
                                  "", "\\usr1\\lib\\myFile.ext")
        self.test_path_splitdrive("0.14", "/usr1/lib/myFile.ext",
                                  "", "/usr1/lib/myFile.ext")
        self.test_path_splitdrive("0.15",
                                  "\\\\machine\\usr1\\lib\\myFile.ext",
                                  "", "\\\\machine\\usr1\\lib\\myFile.ext")
        self.test_path_splitdrive("0.16", "//machine/usr1/lib/myFile.ext",
                                  "", "//machine/usr1/lib/myFile.ext")
        self.test_path_splitdrive("0.17", "c:\\usr1\\lib\\myFile.ext",
                                  "c:", "\\usr1\\lib\\myFile.ext")

    def check_4_lfile(self, fsrc, ftgt):
        f = os0.setlfilename(fsrc, os0.LFN_FLAT)
        if f != ftgt:
            return False
        else:
            return True

    def check_4_lfile_exe(self, fsrc, ftgt):
        f = os0.setlfilename(fsrc, os0.LFN_EXE)
        if f != ftgt:
            return False
        else:
            return True

    def check_4_lfile_cmd(self, fsrc, ftgt):
        f = os0.setlfilename(fsrc, os0.LFN_CMD)
        if f != ftgt:
            return False
        else:
            return True

    def check_4_lfile_dir(self, fsrc, ftgt):
        f = os0.setlfilename(fsrc, os0.LFN_DIR)
        if f != ftgt:
            return False
        else:
            return True

    def test_fn(self, txtid, fsrc, ftgt, ctx):
        sts = self.Z.test_result(ctx,
                                 txtid,
                                 True,
                                 self.check_4_lfile(fsrc,
                                                    ftgt))
        return sts

#
    def test_fn_linux(self, ctx):
        sts = self.test_fn("1.01", "myFile", "myFile", ctx)
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "1.02 setlfilename(myFile, exe)",
                                     True,
                                     self.check_4_lfile_exe("myFile",
                                                            "myFile"))

        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "1.03 setlfilename(myFile, cmd)",
                                     True,
                                     self.check_4_lfile_cmd("myFile",
                                                            "myFile"))
        if sts == TEST_SUCCESS:
            sts = self.Z.test_result(ctx,
                                     "1.04 setlfilename(myFile, dir)",
                                     True,
                                     self.check_4_lfile_dir("myFile",
                                                            "myFile"))
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.05", "myFile.py", "myFile.py", ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.06",
                               "/root/myFile.py",
                               "/root/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.07",
                               "/usr1/lib/myFile.py",
                               "/usr1/lib/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.08",
                               "lib/myFile.py",
                               "lib/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.09",
                               "./myFile.py",
                               "./myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.10",
                               "../myFile.py",
                               "../myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.11",
                               "../lib/myFile.py",
                               "../lib/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.12",
                               "../../myFile.py",
                               "../../myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.13",
                               "/myFile.py",
                               "/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.20",
                               "/usr1/lib/python.2.7/myFile.py",
                               "/usr1/lib/python.2.7/myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.21",
                               "not.myFile.py",
                               "not.myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.22",
                               "/usr1/lib/python.2.7/not.myFile.py",
                               "/usr1/lib/python.2.7/not.myFile.py",
                               ctx)
        if sts == TEST_SUCCESS:
            sts = self.test_fn("1.30", "/dev/null", "/dev/null", ctx)
        return sts

#
    def test_fn_vms(self, ctx):

        self.test_fn("1.01", "myFile", "myFile")

        os0.wlog("Test 1.02 setlfilename(myFile, exe)")
        if not self.check_4_lfile_exe("myFile", "myFile.exe"):
            os0.wlog("Test 1.02 failed")
            raise Exception("Test 1.02 failed: !!!")
        os0.wlog("Test 1.03 setlfilename(myFile, cmd)")
        if not self.check_4_lfile_cmd("myFile", "myFile.com"):
            os0.wlog("Test 1.03 failed")
            raise Exception("Test 1.03 failed: !!!")
        os0.wlog("Test 1.04 setlfilename(myFile, dir)")
        if not self.check_4_lfile_dir("myFile", "myFile.DIR"):
            os0.wlog("Test 1.04 failed")
            raise Exception("Test 1.04 failed: !!!")

        self.test_fn("1.05", "myFile.py", "myFile.py")
        self.test_fn("1.06", "/root/myFile.py", "[root]myFile.py")
        self.test_fn("1.07", "/usr1/lib/myFile.py", "[usr1.lib]myFile.py")
        self.test_fn("1.08", "lib/myFile.py", "[.lib]myFile.py")
        self.test_fn("1.09", "./myFile.py", "[]myFile.py")
        self.test_fn("1.10", "../myFile.py", "[-]myFile.py")
        self.test_fn("1.11", "../lib/myFile.py", "[-.lib]myFile.py")
        self.test_fn("1.12", "../../myFile.py", "[-.-]myFile.py")
        self.test_fn("1.13", "/myFile.py", "[000000]myFile.py")

        self.test_fn("1.20", "/usr1/lib/python.2.7/myFile.py",
                     "[usr1.lib.python^.2^.7]myFile.py")
        self.test_fn("1.21", "not.myFile.py", "not^.myFile.py")
        self.test_fn("1.22", "/usr1/lib/python.2.7/not.myFile.py",
                     "[usr1.lib.python^.2^.7]not^.myFile.py")

        self.test_fn("1.30", "/dev/null", "NL0:")

        self.test_fn("1.90", "/sys$sysdevice/myfile",
                     "sys$sysdevice:[000000]myfile")
        self.test_fn("1.91", "/sys$sysdevice/usr1/myfile",
                     "sys$sysdevice:[usr1]myfile")

#
    def test_fn_win(self, ctx):
        os0.wlog("- Specific test for Windows platform")

        os0.wlog("Test 1.01 setlfilename(myFile)")
        if not self.check_4_lfile("myFile", "myFile"):
            os0.wlog("Test 1.01 failed")
            raise Exception("Test 1.01 failed: !!!")
        os0.wlog("Test 1.02 setlfilename(myFile, exe)")
        if not self.check_4_lfile_exe("myFile", "myFile.exe"):
            os0.wlog("Test 1.02 failed")
            raise Exception("Test 1.02 failed: !!!")
        os0.wlog("Test 1.03 setlfilename(myFile, cmd)")
        if not self.check_4_lfile_cmd("myFile", "myFile.bat"):
            os0.wlog("Test 1.03 failed")
            raise Exception("Test 1.03 failed: !!!")
        os0.wlog("Test 1.04 setlfilename(myFile, dir)")
        if not self.check_4_lfile_dir("myFile", "myFile"):
            os0.wlog("Test 1.04 failed")
            raise Exception("Test 1.04 failed: !!!")

#
        self.test_fn("1.05", "myFile.py", "myFile.py")
        self.test_fn("1.06", "/root/myFile.py", "\\root\\myFile.py")
        self.test_fn("1.07", "/usr1/lib/myFile.py", "\\usr1\\lib\\myFile.py")
        self.test_fn("1.08", "lib/myFile.py", "lib\\myFile.py")
        self.test_fn("1.09", "./myFile.py", ".\\myFile.py")
        self.test_fn("1.10", "../myFile.py", "..\\myFile.py")
        self.test_fn("1.11", "../lib/myFile.py", "..\\lib\\myFile.py")
        self.test_fn("1.12", "../../myFile.py", "..\\..\\myFile.py")
        self.test_fn("1.13", "/myFile.py", "\\myFile.py")

        self.test_fn("1.20", "/usr1/lib/python.2.7/myFile.py",
                     "\\usr1\\lib\\python.2.7\\myFile.py")
        self.test_fn("1.21", "not.myFile.py", "not.myFile.py")
        self.test_fn("1.22", "/usr1/lib/python.2.7/not.myFile.py",
                     "\\usr1\\lib\\python.2.7\\not.myFile.py")

        self.test_fn("1.30", "/dev/null", "nul")

        self.test_fn("1.90", "/c/myfile", "c:\\myfile")
        self.test_fn("1.91", "/c/usr1/myfile", "c:\\usr1\\myfile")

#
    def check_4_tkn_in_stdout(self, token):
        # Now search for this program name in output;
        # if found muteshell worked right!
        found_chunk = False
        try:
            stdout_fd = open(os0.setlfilename(os0.bgout_fn, 'r'))
            f = stdout_fd.read()
            if f.find(token) >= 0:
                found_chunk = True
            stdout_fd.close()
        except:
            pass
        if not found_chunk:
            os0.wlog("Test failed: muteshell did not work!!!")
            raise Exception("Test failed: muteshell did not work!!!")


if __name__ == "__main__":
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest)
    )