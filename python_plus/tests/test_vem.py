# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import os
import os.path
import shutil
import sys

from z0lib import z0lib
from zerobug import z0test

MODULE_ID = "python_plus"
TEST_FAILED = 1
TEST_SUCCESS = 0

TEST_PYTHON = """
from z0lib import z0lib
parser = z0lib.parseoptargs("Test","(C) SHS-AV",version="1.2.3.4")
parser.add_argument('-h')
parser.add_argument('-V')
ctx = parser.parseoptargs(['-V'])
"""

__version__ = "2.0.11"


def version():
    return __version__


class RegressionTest:

    def setup(self):
        self.venv_dir = os.path.join(self.Z.testdir, "SAMPLE")
        os.chdir(os.environ["HOME"])
        self.SAVED_HOME = os.getcwd()
        self.SAVED_VENV = os.environ["VIRTUAL_ENV"]
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "vem.py")
        )

    def clear_venv(self):
        if os.path.isdir(self.venv_dir):
            shutil.rmtree(self.venv_dir)

    def check_4_paths(self):
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        for nm in ("bin", "lib"):
            tgtdir = os.path.join(self.venv_dir, nm)
            self.assertTrue(os.path.isdir(tgtdir), msg_info="- dir %s" % tgtdir)

        tgtfile = os.path.join(self.venv_dir, "bin", "python%s" % pyver)
        self.assertTrue(os.path.isfile(tgtfile), msg_info="- file %s" % tgtfile)

    def check_4_homedir(self, homedir):
        cmd = 'vem %s -q exec "cd; pwd"' % self.venv_dir
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertEqual(
            homedir,
            stdout.split()[-1] if stdout else "<None>",
            msg_info="- home %s" % homedir,
        )

    def check_4_install(self):
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        libdir = os.path.join(self.venv_dir, "lib", "python%s" % pyver, "site-packages")
        pypi = "Werkzeug"
        tgtdir = os.path.join(libdir, pypi.lower())
        cmd = "vem %s -q install %s" % (self.venv_dir, pypi)
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertTrue(os.path.isdir(tgtdir))

        cmd = "vem %s -q info %s" % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        self.assertEqual(os.path.dirname(tgtdir), res, msg_info="- infodir %s" % pypi)

        if sys.version_info[0] == 2:
            werkz_version = "0.11.11"
        elif sys.version_info[0:2] >= (3, 9):
            werkz_version = "2.0.2"
        else:
            werkz_version = "0.16.1"
        cmd = "vem %s -q update %s==%s" % (self.venv_dir, pypi, werkz_version)
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        cmd = "vem %s -q info %s" % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Version:"):
                res = ln.split(" ")[1].strip()
                break
        self.assertEqual(werkz_version, res, msg_info="- pkg version %s" % pypi)

        cmd = "vem %s -q uninstall %s -y" % (self.venv_dir, pypi)
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertFalse(os.path.isdir(tgtdir))

        pypi = "zar"
        cmd = "vem %s -q install %s" % (
            self.venv_dir,
            os.path.join(os.environ["TRAVIS_SAVED_HOME_DEVEL"], "pypi", pypi),
        )
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        cmd = "vem %s -q info %s" % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        self.assertEqual(os.path.dirname(tgtdir), res, msg_info="- infodir %s" % pypi)

        cmd = "vem %s -q uninstall %s -y" % (self.venv_dir, pypi)
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertFalse(os.path.isdir(tgtdir), msg_info="- rmdir %s" % tgtdir)

        cmd = "vem %s -q install %s -BBB" % (self.venv_dir, pypi)
        sts = z0lib.os_system(cmd)
        self.assertEqual(0, sts, msg_info=cmd)
        cmd = "vem %s -q info %s" % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        self.assertEqual(os.path.dirname(tgtdir), res, msg_info="- infodir %s" % pypi)

    def check_installed(self, pypi):
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        libdir = os.path.join(self.venv_dir, "lib", "python%s" % pyver, "site-packages")
        tgtdir = os.path.join(libdir, pypi.lower())
        cmd = "vem %s -q info %s" % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        if pypi == "lessc":
            self.assertTrue(tgtdir, msg_info="- infodir %s" % pypi)
        else:
            self.assertEqual(
                os.path.dirname(tgtdir), res, msg_info="- infodir %s" % pypi
            )

    def check_4_exec(self):
        test_python = os.path.join(self.venv_dir, "test_python.py")
        if not self.Z.dry_run:
            with open(test_python, "w") as fd:
                fd.write(TEST_PYTHON)
        cmd = 'vem -qf %s exec "python %s"' % (self.venv_dir, test_python)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        if sys.version_info[0] == 2:
            # Python2 version is issued on stderr
            self.assertEqual(
                "1.2.3.4", stderr.split()[-1] if stderr else "<None>", msg_info="- exec"
            )
        else:
            self.assertEqual(
                "1.2.3.4", stdout.split()[-1] if stdout else "<None>", msg_info="- exec"
            )

    def test_01(self):
        self.clear_venv()
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        # Not isolated environment
        cmd = "vem -qf -p%s create %s" % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertTrue(os.path.isdir(self.venv_dir), msg_info=cmd)
        self.check_4_paths()
        self.check_4_homedir(self.SAVED_HOME)
        self.check_4_install()
        self.check_4_exec()

    def test_02(self):
        self.clear_venv()
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        # Isolated environment
        cmd = "vem -qIf -p%s create %s" % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertTrue(os.path.isdir(self.venv_dir), msg_info=cmd)
        self.check_4_paths()
        self.check_4_homedir(self.venv_dir)
        self.check_4_install()
        self.check_4_exec()

    def test_03(self, z0ctx):
        self.clear_venv()
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        # Isolated environment + devel packages
        cmd = "vem -qDIf -p%s create %s" % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
        self.assertEqual(0, sts, msg_info=cmd)
        self.assertTrue(os.path.isdir(self.venv_dir), msg_info=cmd)
        self.check_4_paths()
        self.check_4_homedir(self.venv_dir)
        self.check_4_install()
        self.check_4_exec()

    def test_04(self, z0ctx):
        self.clear_venv()
        pyver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
        if sys.version_info[0] == 2:
            # odoo_ver = "10.0"
            odoo_versions = ["10.0", "7.0", "8.0", "6.1"]
        elif sys.version_info[1] <= 7:
            # odoo_ver = "12.0"
            odoo_versions = ["12.0", "14.0"]
        else:
            # odoo_ver = "16.0"
            odoo_versions = ["16.0", "14.0"]
        for odoo_ver in odoo_versions:
            majver = int(odoo_ver.split(".")[0])
            # Isolated environment + devel packages + Odoo
            cmd = "vem -qDIf -p%s create %s -O %s" % (pyver, self.venv_dir, odoo_ver)
            print(cmd, "... please wait for a minute")
            sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=self.Z.dry_run)
            self.assertEqual(0, sts, msg_info=cmd)
            # Weird behavior for pyYAML with python 3.9
            # if odoo_ver == "16.0":
            #     z0lib.run_traced('vem %s install pyyaml' % self.venv_dir,
            #                      dry_run=z0ctx['dry_run'])
            self.assertTrue(os.path.isdir(self.venv_dir), msg_info=cmd)
            self.check_4_paths()
            self.check_4_homedir(self.venv_dir)
            for pypi in (
                "Babel",
                "gevent",
                "lessc",
                "Pillow",
                "pylint",
                "pyPdf",
                "Python-Chart",
                "zeep",
            ):
                if pypi == "zeep" and majver < 16:
                    continue
                elif pypi == "lessc" and majver < 10:
                    continue
                self.check_installed(pypi)
            self.check_4_exec()


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
