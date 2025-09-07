#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import os.path as pth
import sys
from datetime import datetime


# allow using isolated test environment
def pkg_here(here):
    while (
        pth.basename(here) in ("tests", "scripts")
        or pth.basename(pth.dirname(here)) == "local"
    ):
        here = pth.dirname(here)
    if here not in sys.path:
        sys.path.insert(0, here)


pkg_here(pth.dirname(pth.abspath(__file__)))  # noqa: E402
pkg_here(pth.abspath(os.getcwd()))  # noqa: E402
from z0lib import z0lib  # noqa: E402
from zerobug import z0test, z0testodoo  # noqa: E402

__version__ = "2.0.14"

MODULE_ID = "z0lib"


def version():
    return __version__


class RegressionTest:

    def setup(self):
        self.os_tree = [
            "devel",
            "devel/pypi",
            "devel/pypi/.git",
            "devel/pypi/zerobug",
            "devel/pypi/zerobug/zerobug",
        ]

    def test_01(self):
        self.oe_ver = "18.0"
        self.oe_maj = 18
        self.oe_root = z0testodoo.build_odoo_env(self.oe_ver)
        self.ocb_repo = os.path.join(self.oe_root, self.oe_ver)
        self.repodir = z0testodoo.create_repo(
            self.oe_root,
            "test_repo",
            self.oe_ver,
        )
        self.moduledir = z0testodoo.create_module(
            self.repodir, "test_module", self.oe_ver)

        package = z0lib.Package(self.moduledir)
        self.assertEqual("Odoo", package.prjname, msg_info="Test package Odoo")
        self.assertEqual(
            self.oe_ver, package.version, msg_info="- Odoo self.oe_version")
        self.assertEqual(
            self.oe_maj, package.majver, msg_info="- Odoo major version")
        self.assertEqual("test_module", package.name, msg_info="- Module name")
        self.assertEqual(self.moduledir, package.path, msg_info="- Module path")
        self.assertEqual(self.moduledir, package.rundir, msg_info="- Module rundir")
        self.assertEqual(self.repodir, package.prjpath, msg_info="- Repo path")
        self.assertEqual("oca", package.git_orgid, msg_info="- Repo orgid")
        self.assertEqual("module", package.dir_level, msg_info="- Package kind")
        self.assertTrue(package.read_only, msg_info="- Read only")
        logdir = package.get_log_dir()
        self.assertEqual(pth.join(os.environ["TRAVIS_SAVED_HOME"], "travis_log"),
                         logdir,
                         msg_info="- Log directory")
        self.assertEqual(self.ocb_repo, package.root, msg_info="- root")

    def test_02(self):
        self.pypi_root = self.build_os_tree(self.os_tree)
        self.pypi_repo = os.path.join(self.pypi_root, self.os_tree[1])
        self.pkgpath = os.path.join(self.pypi_root, self.os_tree[3])
        self.rundir = os.path.join(self.pypi_root, self.os_tree[4])
        with open(os.path.join(self.rundir, "__init__.py"), "w") as fd:
            fd.write("\n")
        self.setup_path = os.path.join(self.pkgpath, "setup.py")
        with open(self.setup_path, "w") as fd:
            fd.write("from setuptools import setup\n"
                     "setup(\n"
                     "    name='name',\n"
                     "    version='%s',\n"
                     ")" % __version__)
        package = z0lib.Package(self.rundir)
        self.assertEqual("Z0tools", package.prjname, msg_info="Test package PYPI")
        self.assertEqual(__version__, package.version, msg_info="- Pypi version")
        self.assertEqual("zerobug", package.name, msg_info="- Pypi name")
        self.assertEqual(self.pkgpath, package.path, msg_info="- Pypi path")
        self.assertEqual(self.rundir, package.rundir, msg_info="- Pypi rundir")
        self.assertEqual(self.pypi_repo, package.prjpath, msg_info="- Repo path")
        self.assertEqual("zero", package.git_orgid, msg_info="- Repo orgid")
        self.assertEqual("module", package.dir_level, msg_info="- Package kind")
        self.assertFalse(package.read_only, msg_info="- Read only")
        logdir = package.get_log_dir()
        self.assertEqual(pth.join(self.rundir, "tests", "logs"),
                         logdir,
                         msg_info="- Log directory")

    def test_03(self):
        package = z0lib.Package(self.repodir)
        self.assertEqual("Odoo", package.prjname, msg_info="Test package Odoo")
        self.assertEqual(
            self.oe_ver, package.version, msg_info="- Odoo self.oe_version")
        self.assertEqual(
            self.oe_maj, package.majver, msg_info="- Odoo major version")
        self.assertEqual("test_repo", package.name, msg_info="- Repo name")
        self.assertEqual(self.repodir, package.prjpath, msg_info="- Repo path")
        self.assertEqual("oca", package.git_orgid, msg_info="- Repo orgid")
        self.assertEqual("repo", package.dir_level, msg_info="- Package kind")
        self.assertEqual(self.ocb_repo, package.root, msg_info="- root")

    def test_04(self):
        package = z0lib.Package(self.ocb_repo)
        self.assertEqual("Odoo", package.prjname, msg_info="Test package Odoo")
        self.assertEqual(
            self.oe_ver, package.version, msg_info="- Odoo self.oe_version")
        self.assertEqual(
            self.oe_maj, package.majver, msg_info="- Odoo major version")
        self.assertEqual("OCB", package.name, msg_info="- Repo name")
        self.assertEqual(self.ocb_repo, package.prjpath, msg_info="- Repo path")
        self.assertEqual("oca", package.git_orgid, msg_info="- Repo orgid")
        self.assertEqual("repo", package.dir_level, msg_info="- Package kind")
        self.assertEqual(self.ocb_repo, package.root, msg_info="- root")

    def test_05(self):
        package = z0lib.Package(self.pypi_repo)
        self.assertEqual("Z0tools", package.prjname, msg_info="Test package PYPI")
        self.assertEqual("pypi", package.name, msg_info="- Pypi name")
        self.assertEqual(self.pypi_repo, package.prjpath, msg_info="- Repo path")
        self.assertEqual("zero", package.git_orgid, msg_info="- Repo orgid")
        self.assertEqual("repo", package.dir_level, msg_info="- Package kind")

    def test_06(self):
        package = z0lib.Package(self.rundir)
        logdir = os.environ["TRAVIS_SAVED_PKGPATH"].replace("z0lib", "zerobug")
        logdir = package.get_log_dir(
            fqn=os.path.join(logdir, "tests", "logs", "test.log"))
        if not os.path.isdir(logdir):
            os.mkdir(logdir)
        udi, umli = package.get_uniqid()
        dt = datetime.today().isoformat()[:10].replace("-", "")
        # Do not modify sequence: test is based on thi wrong sequence
        # To avoid conflicts with real log files with use value > 86400
        logs = []
        for tm in ("87123",  "91456", "89345"):
            log_fqn = os.path.join(logdir, "%s-%s+%s.log" % (umli, dt, tm))
            with open(log_fqn, "w") as fd:
                fd.write("")
            logs.append(log_fqn)
        prior = "zzzzzzzzzzzzzzzzzzzz"
        ctr = 0
        for fn in package.list_log_filename():
            self.assertGreater(
                prior,
                fn,
                msg="Wrong sort in log dir"
            )
            prior = fn
            if fn in logs:
                ctr += 1
        self.assertEqual(3, ctr, msg_info="Log list")
        for fqn in logs:
            os.unlink(fqn)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
