#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys
from datetime import datetime

from z0lib import z0lib
from zerobug import z0test, z0testodoo


__version__ = "2.0.12"

MODULE_ID = 'wok_code'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.Z.inherit_cls(self)
        self.root = ''

    def _touch_file(self, fn):
        if not os.path.isfile(fn):
            with open(fn, "w") as fd:
                fd.write("# Fake\n")

    def test_01(self, z0ctx):
        cmd = "please --version"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual(
            (stdout + stderr).split("\n")[0],
            __version__)

        cmd = "please"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            "please is an interactive developers shell aims to help", stdout)

        cmd = "please help"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            "please is an interactive developers shell aims to help", stdout)

        cmd = "please help z0bug"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(" please test", stdout)

        cmd = "please -h"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn("2015-2023 by SHS-AV s.r.l.", (stdout + stderr))

        cmd = "please z0bug -h"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn("-T REGEX, --trace REGEX", (stdout + stderr))

        return self.ret_sts()

    def test_02(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please z0bug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual(stdout.split("\n")[0], "> travis emulate -vn")

        os.chdir(self.tool_pkgdir)
        cmd = "please zerobug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual(stdout.split("\n")[0], "> travis emulate -vn")

        os.chdir(self.pypi_dir)
        cmd = "please zerobug -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual(stdout.split("\n")[0], "> travis emulate -vn")

        # Test result (<PYTHON> = ~/VENV_*/bin/python
        #              <SCRIPT> = ~/VENV_*/build/local/wok_code/scripts
        #              <TMODARS> = -m test_module -b 12.0
        #              <DBARGS> = -c /etc/odoo/odoo12.conf -d test_test_module_12):
        # 0 "> git add ./"
        # 1 "> pre-commit run"
        # 2 "> <SCRIPT>/please.sh lint -vfn"
        # 3 "> <PYTHON> <SCRIPT>/run_odoo_debug.py -T -m test_module -b 12.0 -f -v -n"
        # 4 "> <PYTHON> <SCRIPT>/gen_readme.py -b 12.0 -f -n -RW"
        # 5 "> <PYTHON> <SCRIPT>/gen_readme.py -b 12.0 -f -n"
        # 6 "> <PYTHON> <SCRIPT>/gen_readme.py -b 12.0 -f -n -I"
        # 7 "Test log file not found!"
        # 8 "> git add ./"
        # 9 "> <PYTHON> <SCRIPT>/odoo_translation.py <TMODARS> <DBARGS> -v -n"
        # 10 "> <PYTHON> <SCRIPT>/run_odoo_debug.py -e <TMODARS> <DBARGS> -v -n
        #
        os.chdir(self.odoo_moduledir)
        rdme_dir = os.path.join(self.odoo_moduledir, "readme")
        if not os.path.isdir(rdme_dir):
            os.mkdir(rdme_dir)
        chnglog = os.path.join(self.odoo_moduledir, "readme", "CHANGELOG.rst")
        if os.path.isfile(chnglog):
            os.unlink(chnglog)
        i18n_dir = os.path.join(self.odoo_moduledir, "i18n")
        if not os.path.isdir(i18n_dir):
            os.mkdir(i18n_dir)
        pofile = os.path.join(self.odoo_moduledir, "i18n", "it.po")
        self.create_pofile(pofile)
        self.create_database("test_test_module_12")
        TMODARS = "-m test_module -b 12.0"
        DBARGS = "-c /etc/odoo/odoo12.conf -d test_test_module_12"

        cmd = "please zerobug -vfn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn("pre-commit run",
                      stdout.split("\n")[1],
                      msg="Bash command not found in stdout")
        self.assertIn("please.sh lint -vfn",
                      stdout.split("\n")[2],
                      msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[3],
            ".*/python .*/run_odoo_debug.py -T -m test_module -b 12.0 -f -v -n",
            msg="Bash command not found in stdout")
        # self.assertMatch(
        #     stdout.split("\n")[4],
        #     ".*/python .*/gen_readme.py -b 12.0 -f -n -RW",
        #     msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[4],
            ".*/python .*/gen_readme.py -b 12.0 -f -n",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[5],
            ".*/python .*/gen_readme.py -b 12.0 -f -n -I",
            msg="Bash command not found in stdout")
        self.assertIn("git add ./",
                      stdout.split("\n")[7],
                      msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[8],
            ".*/odoo_translation.py %s %s -v -n" % (TMODARS, DBARGS),
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[9],
            ".*/run_odoo_debug.py -e %s %s -v -n" % (TMODARS, DBARGS),
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_moduledir)
        cmd = "please zerobug -vn --no-verify --no-translate"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn("please.sh lint -vn",
                      stdout.split("\n")[0],
                      msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            ".*/run_odoo_debug.py",
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def test_03(self, z0ctx):
        cmd = "please create apache erp.example.com -qn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual("File ~/erp.example.com.conf will be created",
                         stdout.split("\n")[0])

        os.chdir(self.pypi_dir)
        cmd = "please defcon gitignore -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            r".*\.gitignore should be updated/created",
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_repodir)
        cmd = "please defcon gitignore -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            r".*\.gitignore should be updated/created",
            msg="Bash command not found in stdout")

        os.chdir(self.pypi_dir)
        cmd = "please defcon precommit -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            r".*\.pre-commit-config.yaml should be updated/created",
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_repodir)
        cmd = "please defcon precommit -vn"
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            r".*\.pre-commit-config.yaml should be updated/created",
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def test_04(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        with open("please.py~", "w") as fd:
            fd.write("# Fake file\n")
        cmd = "please clean -vn"
        target_file = os.path.join(os.getcwd(), "please.py~")
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertEqual(
            stdout.split("\n")[0],
            "> rm -f " + target_file)

        cmd = "please clean -v"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            " rm -f " + target_file,
            stdout.split("\n")[0]
        )

        return self.ret_sts()

    def test_05(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            " travis test -vn",
            stdout.split("\n")[0]
        )

        os.chdir(self.pypi_dir)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            " travis test -vn",
            stdout.split("\n")[0]
        )

        TMODARS = "-m test_module -b 12.0"
        DBARGS = "-c /etc/odoo/odoo12.conf -d test_test_module_12"
        os.chdir(self.odoo_moduledir)
        chnglog = os.path.join(self.odoo_moduledir, "readme", "CHANGELOG.rst")
        if os.path.isfile(chnglog):
            os.unlink(chnglog)
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            ".*run_odoo_debug.py",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            ".*/gen_readme.py -b 12.0 -n",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[2],
            ".*/gen_readme.py -b 12.0 -n -I",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[4],
            ".*git add ./",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[5],
            ".*/odoo_translation.py %s %s -v -n" % (TMODARS, DBARGS),
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[6],
            ".*/run_odoo_debug.py -e %s %s -v -n" % (TMODARS, DBARGS),
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_moduledir)
        chnglog = os.path.join(self.odoo_moduledir, "readme", "CHANGELOG.rst")
        if os.path.isfile(chnglog):
            os.unlink(chnglog)
        cmd = "please test -vn --no-translate"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            ".*/python .*/run_odoo_debug.py -T -m test_module -b 12.0 -v -n",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            ".*/gen_readme.py -b 12.0 -n",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[2],
            ".*/gen_readme.py -b 12.0 -n -I",
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def test_06(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            "> pre-commit run",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            "> travis lint -vn",
            msg="Bash command not found in stdout")

        os.chdir(self.pypi_dir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            "> pre-commit run",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            "> travis lint -vn",
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_moduledir)
        cmd = "please lint -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            ".*git add ./",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[1],
            "> pre-commit run",
            msg="Bash command not found in stdout")
        self.assertMatch(
            stdout.split("\n")[2],
            ".*/please.sh lint -vn",
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_moduledir)
        cmd = "please lint -vn --no-verify"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            ".*/please.sh lint -v",
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def _test_07(self, z0ctx):
        os.chdir(self.tool_pkgdir)
        cmd = "please show -n"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            "> travis show",
            msg="Bash command not found in stdout")

        os.chdir(self.pypi_dir)
        cmd = "please show -n"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertMatch(
            stdout.split("\n")[0],
            "> travis show",
            msg="Bash command not found in stdout")

        os.chdir(self.odoo_moduledir)
        fn = os.path.join(self.odoo_moduledir, "tests", "logs", "show-log.sh")
        cmd = "please test -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            fn,
            stdout.split("\n")[0],
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def test_08(self, z0ctx):
        os.chdir(self.pypi_dir)
        cmd = "please replace -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        # self.assertIn(
        #     " rsync -a ",
        #     stdout,
        #     msg="Bash command not found in stdout")

        os.chdir(self.pypi_dir)
        cmd = "please commit -m \"Test message\" -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        # self.assertIn(
        #     "> rsync -a ",
        #     stdout.split("\n")[3],
        #     msg="Bash command not found in stdout")

        os.chdir(self.pypi_dir)
        cmd = "please update -vn"
        sts, stdout, stderr = z0lib.run_traced(cmd)
        self.assertEqual(sts, 0, msg="%s -> sts=%s" % (cmd, sts), msg_info="%s" % cmd)
        self.assertIn(
            "> vem ",
            stdout.split("\n")[1],
            msg="Bash command not found in stdout")

        return self.ret_sts()

    def create_pofile(self, pofile):
        if os.path.isfile(pofile):
            os.unlink(pofile)
        with open(pofile, "w") as fd:
            fd.write("msgid \"\"\n")
            fd.write("msgstr \"\"\n")
            fd.write("PO-Revision-Date: %s 00:01+0000\n\""
                     % datetime.now().strftime("%Y-%m-%d"))

    def create_database(self, database):
        os.system("dropdb %s" % database)
        os.system("createdb %s" % database)
        os.system(("psql -c "
                   "\"create table ir_module_module  ("
                   "id integer, "
                   "name varchar(64), "
                   "state varchar(32), "
                   "latest_version varchar(16), "
                   "published_version varchar(16))\" %s") % database)
        os.system((
            "psql -c "
            "\"insert into ir_module_module (id, name, state, published_version) "
            "values (1, 'test_module', 'installed', '12.0.1')\" %s" % database))
        os.system(("psql -c "
                   "\"create table ir_config_parameter  ("
                   "id integer, "
                   "key varchar(32), "
                   "value varchar(32))\" %s" % database))
        os.system(("psql -c "
                   "\"insert into ir_config_parameter (id, key, value) "
                   "values (1, 'database.create_date', '%s')\" %s"
                   % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), database)))

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "please.py")
        )
        # TODO> weird situation
        z0lib.run_traced(
            "find ~/tools/ -type f -name \"*~\" -delete"
        )
        if not z0ctx['dry_run']:
            self.tool_pkgdir = os.path.expanduser("~/tools/wok_code")

            devel_root = os.path.expanduser("~/devel")
            self.Z.build_os_tree(
                z0ctx,
                [
                    devel_root,
                    os.path.join(devel_root, "pypi"),
                    os.path.join(devel_root, "pypi", ".git"),
                    os.path.join(devel_root, "pypi", "wok_code"),
                    os.path.join(devel_root, "pypi", "wok_code", "wok_code"),
                ],
            )
            self.pypi_dir = os.path.join(devel_root, "pypi", "wok_code", "wok_code")
            self._touch_file(os.path.join(devel_root, "pypi", "wok_code", "setup.py"))
            self._touch_file(os.path.join(devel_root, "pypi", "wok_code", "README.rst"))
            self._touch_file(
                os.path.join(devel_root, "pypi", "wok_code", "wok_code", "__init__.py")
            )

            self.odoo_root = z0testodoo.build_odoo_env(z0ctx, "12.0")
            self.odoo_repodir = z0testodoo.create_repo(
                z0ctx,
                self.odoo_root,
                'test_repo',
                "12.0",
            )
            self.odoo_moduledir = z0testodoo.create_module(
                z0ctx, self.odoo_repodir, 'test_module', "12.0"
            )
            if not os.path.isdir(os.path.join(self.odoo_moduledir, "tests")):
                os.mkdir(os.path.join(self.odoo_moduledir, "tests"))
            if not os.path.isdir(os.path.join(self.odoo_moduledir, "tests", "logs")):
                os.mkdir(os.path.join(self.odoo_moduledir, "tests", "logs"))
            self._touch_file(
                os.path.join(self.odoo_moduledir, "tests", "logs", "show-log.sh")
            )

    def tearoff(self, z0ctx):
        os.system("dropdb test_test_module_12")


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )

