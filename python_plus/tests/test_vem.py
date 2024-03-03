# -*- coding: utf-8 -*-
# Copyright (C) 2015-2024 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
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

MODULE_ID = 'python_plus'
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
    def __init__(self, z):
        self.Z = z
        self.venv_dir = os.path.join(self.Z.testdir, 'SAMPLE')
        os.chdir(os.environ['HOME'])
        self.SAVED_HOME = os.getcwd()
        self.SAVED_VENV = os.environ['VIRTUAL_ENV']

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "vem.py"))

    def clear_venv(self):
        if os.path.isdir(self.venv_dir):
            shutil.rmtree(self.venv_dir)

    def check_4_paths(self, z0ctx):
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        for nm in ('bin', 'lib'):
            tgtdir = os.path.join(self.venv_dir, nm)
            sts = self.Z.test_result(
                z0ctx, "- dir %s" % tgtdir, True, os.path.isdir(tgtdir)
            )

        tgtfile = os.path.join(self.venv_dir, 'bin', 'python%s' % pyver)
        sts += self.Z.test_result(
            z0ctx, "- file %s" % tgtfile, True, os.path.isfile(tgtfile)
        )
        return sts

    def check_4_homedir(self, z0ctx, homedir):
        cmd = 'vem %s -q exec "cd; pwd"' % self.venv_dir
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(
            z0ctx,
            "- home %s" % homedir,
            homedir,
            stdout.split()[-1] if stdout else "<None>"
        )
        return sts

    def check_4_install(self, z0ctx):
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        libdir = os.path.join(self.venv_dir, "lib", 'python%s' % pyver, "site-packages")
        pypi = "Werkzeug"
        tgtdir = os.path.join(libdir, pypi.lower())
        cmd = 'vem %s -q install %s' % (self.venv_dir, pypi)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts)
        sts += self.Z.test_result(
            z0ctx, "- pkgdir %s" % tgtdir, True, os.path.isdir(tgtdir)
        )

        cmd = 'vem %s -q info %s' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        sts += self.Z.test_result(
            z0ctx, "- infodir %s" % pypi, os.path.dirname(tgtdir), res
        )

        werkz_version = ""
        if sys.version_info[0] == 2:
            werkz_version = "0.11.11"
        elif sys.version_info[0:2] >= (3, 9):
            werkz_version = "2.0.2"
        else:
            werkz_version = "0.16.1"
        cmd = 'vem %s -q update %s==%s' % (self.venv_dir, pypi, werkz_version)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        cmd = 'vem %s -q info %s' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Version:"):
                res = ln.split(" ")[1].strip()
                break
        sts += self.Z.test_result(
            z0ctx, "- pkg version %s" % pypi, werkz_version, res
        )

        cmd = 'vem %s -q uninstall %s -y' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        sts += self.Z.test_result(
            z0ctx, "- rmdir %s" % tgtdir, False, os.path.isdir(tgtdir)
        )

        pypi = "zar"
        cmd = 'vem %s -q install %s' % (
            self.venv_dir,
            os.path.join(os.environ["TRAVIS_SAVED_HOME_DEVEL"], "pypi", pypi))
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        cmd = 'vem %s -q info %s' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        sts += self.Z.test_result(
            z0ctx, "- infodir %s" % pypi, os.path.dirname(tgtdir), res
        )

        cmd = 'vem %s -q uninstall %s -y' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        sts += self.Z.test_result(
            z0ctx, "- rmdir %s" % tgtdir, False, os.path.isdir(tgtdir)
        )

        cmd = 'vem %s -q install %s -BBB' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        cmd = 'vem %s -q info %s' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        sts += self.Z.test_result(
            z0ctx, "- infodir %s" % pypi, os.path.dirname(tgtdir), res
        )

        return sts

    def check_installed(self, z0ctx, pypi):
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        libdir = os.path.join(self.venv_dir, "lib", 'python%s' % pyver, "site-packages")
        tgtdir = os.path.join(libdir, pypi.lower())
        cmd = 'vem %s -q info %s' % (self.venv_dir, pypi)
        sts1, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts = self.Z.test_result(z0ctx, "%s" % cmd, 0, sts1)
        res = ""
        for ln in stdout.split("\n"):
            if ln.startswith("Location:"):
                res = ln.split(" ")[1].strip()
                break
        if pypi == "lessc":
            sts += self.Z.test_result(
                z0ctx, "- infodir %s" % pypi, tgtdir != "", True
            )
        else:
            sts += self.Z.test_result(
                z0ctx, "- infodir %s" % pypi, os.path.dirname(tgtdir), res
            )
        return sts

    def check_4_exec(self, z0ctx):
        test_python = os.path.join(self.venv_dir, 'test.py')
        if not z0ctx['dry_run']:
            with open(test_python, 'w') as fd:
                fd.write(TEST_PYTHON)
        cmd = 'vem -qf %s exec "python %s"' % (self.venv_dir, test_python)
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        if sys.version_info[0] == 2:
            # Python2 version is issued on stderr
            sts += self.Z.test_result(
                z0ctx,
                "- exec",
                '1.2.3.4',
                stderr.split()[-1] if stderr else "<None>"
            )
        else:
            sts += self.Z.test_result(
                z0ctx,
                "- exec",
                '1.2.3.4',
                stdout.split()[-1] if stdout else "<None>"
            )
        return sts

    def test_01(self, z0ctx):
        self.clear_venv()
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        # Not isolated environment
        cmd = 'vem -qf -p%s create %s' % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, True, os.path.isdir(self.venv_dir))
        sts += self.Z.test_result(z0ctx, "- status %s" % cmd, 0, sts)
        sts += self.check_4_paths(z0ctx)
        sts += self.check_4_homedir(z0ctx, self.SAVED_HOME)
        sts += self.check_4_install(z0ctx)
        sts += self.check_4_exec(z0ctx)

        return sts

    def test_02(self, z0ctx):
        self.clear_venv()
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        # Isolated environment
        cmd = 'vem -qIf -p%s create %s' % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, True, os.path.isdir(self.venv_dir))
        sts += self.Z.test_result(z0ctx, "- status %s" % cmd, 0, sts)
        sts += self.check_4_paths(z0ctx)
        sts += self.check_4_homedir(z0ctx, self.venv_dir)
        sts += self.check_4_install(z0ctx)
        sts += self.check_4_exec(z0ctx)

        return sts

    def test_03(self, z0ctx):
        self.clear_venv()
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        # Isolated environment + devel packages
        cmd = 'vem -qDIf -p%s create %s' % (pyver, self.venv_dir)
        print(cmd, "... please wait for a minute")
        sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
        sts += self.Z.test_result(z0ctx, "%s" % cmd, True, os.path.isdir(self.venv_dir))
        sts += self.Z.test_result(z0ctx, "- status %s" % cmd, 0, sts)
        sts += self.check_4_paths(z0ctx)
        sts += self.check_4_homedir(z0ctx, self.venv_dir)
        sts += self.check_4_install(z0ctx)
        sts += self.check_4_exec(z0ctx)

        return sts

    def test_04(self, z0ctx):
        self.clear_venv()
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        if sys.version_info[0] == 2:
            odoo_ver = "10.0"
            odoo_versions = ["10.0", "7.0", "8.0", "6.1"]
        elif sys.version_info[1] <= 7:
            odoo_ver = "12.0"
            odoo_versions = ["12.0", "14.0"]
        else:
            odoo_ver = "16.0"
            odoo_versions = ["16.0", "14.0"]
        for odoo_ver in odoo_versions:
            majver = int(odoo_ver.split(".")[0])
            # Isolated environment + devel packages + Odoo
            cmd = 'vem -qDIf -p%s create %s -O %s' % (pyver, self.venv_dir, odoo_ver)
            print(cmd, "... please wait for a minute")
            sts, stdout, stderr = z0lib.run_traced(cmd, dry_run=z0ctx['dry_run'])
            # Weird behavior for pyYAML with python 3.9
            # if odoo_ver == "16.0":
            #     z0lib.run_traced('vem %s install pyyaml' % self.venv_dir,
            #                      dry_run=z0ctx['dry_run'])
            sts += self.Z.test_result(
                z0ctx, "%s" % cmd, True, os.path.isdir(self.venv_dir))
            sts += self.Z.test_result(z0ctx, "- status %s" % cmd, 0, sts)
            sts += self.check_4_paths(z0ctx)
            sts += self.check_4_homedir(z0ctx, self.venv_dir)
            for pypi in ("Babel",
                         "gevent",
                         "lessc",
                         "Pillow",
                         "pylint",
                         "pyPdf",
                         "Python-Chart",
                         "zeep"):
                if pypi == "zeep" and majver < 16:
                    continue
                # if pypi == "gevent" and odoo_ver == "16.0":
                #     continue
                elif pypi == "lessc" and majver < 10:
                    continue
                sts += self.check_installed(z0ctx, pypi)
            sts += self.check_4_exec(z0ctx)

        return sts


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


