#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse
from subprocess import call

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from clodoo import clodoo
except ImportError:
    import clodoo

import psycopg2

__version__ = "2.0.12"
GIT_ORGIDS = ("oca", "odoo", "zero", "librerp")


class RunOdoo(object):

    def __init__(self, cli_args):
        self.parse_args(cli_args)
        if not self.opt_args.multi:
            self.opt_args.multi = clodoo.build_odoo_param("IS_MULTI")

        self.parse_branch()
        self.get_config()
        self.get_odoo_bin()
        self.get_actual_odoo_version()
        self.get_virtualenv()

    def base_opts(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=("Run odoo for debug or for regression test"),
            epilog=(
                "© 2015-2023 by SHS-AV s.r.l.\n"
                "Author: antoniomaria.vigliotti@gmail.com\n"
                "Full documentation at: https://zeroincombenze-tools.readthedocs.io/\n"
            ),
        )
        parser.add_argument(
            "-B", "--debug", action="count", default=0,
            help="Debug mode (-BB debug via pycharm)"
        )
        parser.add_argument(
            "-b", "--odoo-branch",
            metavar="BRANCH",
            help="Default Odoo version",
        )
        parser.add_argument(
            "-C", "--no-coverage",
            action="store_true",
            help="No use coverage when run regression test",
        )
        parser.add_argument(
            "-c", "--config", metavar="FILE", help="Odoo configuration file"
        )
        parser.add_argument(
            "-D", "--daemon",
            action="store_true",
            help="Run odoo as daemon",
        )
        parser.add_argument(
            "-d", "--database", metavar="NAME", help="Database name"
        )
        parser.add_argument(
            "-e", "--export-i18n",
            action="store_true",
            help="Export translation (conflicts with -i -u -I -T)",
        )
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="Force update or install modules or create db template",
        )
        parser.add_argument(
            "-G", "--git_org", metavar="NAME", help="Git organizzation"
        )
        parser.add_argument(
            "-H", "--home-devel", metavar="PATH", help="Home devel directory"
        )
        parser.add_argument(
            "-K", "--no-ext-test",
            action="store_true",
            help="Do not run external test (tests/concurrent_test/test_*.py)",
        )
        parser.add_argument(
            "-k",  "--keep",
            action="store_true",
            help="Do not create new DB and keep it after run",
        )
        parser.add_argument(
            "-I", "--install",
            action="store_true",
            help="Install module (conflicts with -e -i -u -T)"
        )
        parser.add_argument(
            "-i", "--import-i18n",
            action="store_true",
            help="Import translation (conflicts with -e -u -I -T, -i is deprecated)",
        )
        parser.add_argument(
            "-L", "--log-level",
            help="set log level: may be info or debug"
        )
        parser.add_argument(
            "-l", "--lang", action="store_true",
            help="Load language"
        )
        parser.add_argument(
            "-M", "--multi", action="store_true",
            help="Multi version/instances odoo environment",
        )
        parser.add_argument(
            "-m", "--modules", metavar="MODULES",
            help="Modules to test, translate or upgrade (comma separated)"
        )
        parser.add_argument(
            "-n",
            "--dry-run",
            action="store_true",
            help="Do nothing (dry-run)",
        )
        parser.add_argument(
            "-p", "--path",
            help="Odoo root path",
        )
        parser.add_argument(
            "-q",  "--quiet",
            action="store_false",
            dest="verbose",
            help="Silent mode",
        )
        parser.add_argument(
            "-s", "--stop-after-init", action="store_true",
            help="Stop the server after its initialization"
        )
        parser.add_argument(
            "-T", "--test", action="store_true",
            help="Launch python test on module (conflicts with -e -i -I -u)"
        )
        parser.add_argument(
            "-U", "--db-user",
            help="Database user name",
        )
        parser.add_argument(
            "-u", "--update",
            action="store_true",
            help="Upgrade module (conflict with -e -i -I -T)",
        )
        parser.add_argument("-V", "--version", action="version", version=__version__)
        parser.add_argument(
            "-v", "--verbose", help="Verbose mode", action="count", default=0
        )
        parser.add_argument(
            "-W", "--virtualenv", metavar="PATH",
            help="Odoo virtual environment",
        )
        parser.add_argument(
            "-w", "--web-server",
            action="store_true",
            help="Run as web server",
        )
        parser.add_argument(
            "-x", "--xmlrpc-port", metavar="PORT",
            help="Odoo http/rpc port",
        )
        return parser

    def parse_args(self, cli_args):
        self.opt_args = self.base_opts().parse_args(cli_args)
        if self.opt_args.verbose:
            self.opt_args.verbose -= 1

    def connect_db(self, db_name="demo", db_user="odoo", db_pwd="admin",
                   db_host="localhost", db_port=5432):
        return psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pwd,
            host=db_host,
            port=db_port,
        )

    def parse_branch(self):
        for (k, v) in (
                ("branch", None),
                ("version", "0.0"),
                ("odoo_maj_version", 0),
                ("script", None),
                ("config", None),
                ("git_org", self.opt_args.git_org)):
            if not hasattr(self, k):
                setattr(self, k, v)

        if self.opt_args.odoo_branch:
            if os.path.isfile(self.opt_args.odoo_branch):
                self.config = self.opt_args.odoo_branch
                self.get_config()
            else:
                self.branch = self.opt_args.odoo_branch
        items = [self.branch or self.git_org, "", ""]
        if self.branch:
            m = re.search(r"[0-9]+\.[0-9]+", self.branch)
            if m:
                items = [self.branch[:m.start()]] + [self.branch[m.start():m.end()]] + [
                    x for x in self.branch[m.end():].split("-")]
            else:
                m = re.search("[0-9]+", self.branch)
                if m and 6 < int(self.branch[m.start():m.end()]) <= 17:
                    items = [self.branch[:m.start()]] + [
                        self.branch[m.start():m.end()]] + [
                        x for x in self.branch[m.end():].split("-")]
            for item in items:
                if item in GIT_ORGIDS:
                    self.git_org = item
                    break
        elif self.git_org and self.git_org not in GIT_ORGIDS:
            print("Invalid git organization %s" % self.git_org)
            self.git_org = None
        if items[1]:
            self.version = items[1]
            self.odoo_maj_version = int(items[1].split(".")[0])
        else:
            self.version = clodoo.build_odoo_param(
                "FULLVER",
                odoo_vid=self.opt_args.odoo_branch,
                multi=self.opt_args.odoo_branch)
            self.odoo_maj_version = clodoo.build_odoo_param(
                "MAJVER",
                odoo_vid=self.opt_args.odoo_branch,
                multi=self.opt_args.odoo_branch)
        if not self.config and self.odoo_maj_version and any([x for x in items[2:]]):
            confn = "/etc/odoo/odoo%d%s.conf" % (self.odoo_maj_version,
                                                 "-".join(items[2:]))
            if os.path.isfile(confn):
                self.config = confn
        if not self.config and self.branch and self.odoo_maj_version:
            if self.git_org:
                confn = "/etc/odoo/odoo%d-%s.conf" % (self.odoo_maj_version,
                                                      self.git_org)
            elif self.odoo_maj_version < 10:
                confn = "/etc/odoo/odoo%d-server.conf" % self.odoo_maj_version
            else:
                confn = "/etc/odoo/odoo%d.conf" % self.odoo_maj_version
            if os.path.isfile(confn):
                self.config = confn

    def prepare_os_cmd(self):
        cmd = "%s.sh" % os.path.splitext(os.path.abspath(__file__))[0]
        opts = ""
        if self.opt_args.debug:
            opts += ("B" * self.opt_args.debug)
        if self.opt_args.no_coverage:
            opts += "C"
        if self.opt_args.daemon:
            opts += "D"
        if self.opt_args.export_i18n:
            opts += "e"
        if self.opt_args.force:
            opts += "f"
        if self.opt_args.no_ext_test:
            opts += "K"
        if self.opt_args.keep:
            opts += "k"
        if self.opt_args.import_i18n:
            opts += "I"
        if self.opt_args.lang:
            opts += "l"
        if self.opt_args.multi:
            opts += "M"
        if self.opt_args.dry_run:
            opts += "n"
        if self.opt_args.stop_after_init:
            opts += "s"
        if self.opt_args.test:
            opts += "T"
        if self.opt_args.update:
            opts += "u"
        if self.opt_args.web_server:
            opts += "w"
        if opts:
            cmd += (" -" + opts)
        if self.opt_args.odoo_branch:
            cmd += (" -b" + self.opt_args.odoo_branch)
        if self.opt_args.config and os.path.isfile(self.opt_args.config):
            cmd += (" -c" + self.opt_args.config)
        if self.opt_args.database:
            cmd += (" -d" + self.opt_args.database)
        if self.opt_args.log_level:
            cmd += (" -L" + self.opt_args.log_level)
        if self.opt_args.modules:
            cmd += (" -m" + self.opt_args.modules)
        if self.opt_args.db_user:
            cmd += (" -U" + self.opt_args.db_user)
        # if self.opt_args.virtualenv:
        #     cmd += (" -W" + self.opt_args.virtualenv)
        if self.opt_args.xmlrpc_port:
            cmd += (" -x" + self.opt_args.xmlrpc_port)
        if self.opt_args.verbose:
            cmd += (" -" + ("v" * self.opt_args.verbose))
        else:
            cmd += " -q"
        return cmd

    def get_odoo_bin(self):
        script = None
        if not self.script:
            if self.opt_args.path:
                for name in ("odoo-bin", "openerp-server"):
                    if os.path.isfile(os.path.join(self.opt_args.path, name)):
                        self.script = os.path.join(self.opt_args.path, name)
                        break
        if not self.script:
            try:
                script = next(
                    x for x in map(
                        lambda x: os.path.join(os.path.dirname(x), "odoo-bin"),
                        self.addons_path)
                    if os.path.isfile(x)
                )
            except StopIteration:
                try:
                    script = next(
                        x for x in map(
                            lambda x: os.path.join(os.path.dirname(x),
                                                   "openerp-server"),
                            self.addons_path)
                        if os.path.isfile(x)
                    )
                except StopIteration:
                    pass
            if script:
                self.script = script

    def get_actual_odoo_version(self):
        if self.script:
            release = os.path.join(os.path.dirname(self.script), "odoo", "release.py")
            if not os.path.isfile(release):
                release = os.path.join(
                    os.path.dirname(self.script), "openerp", "release.py")
            if os.path.isfile(release):
                with open(release, "r") as fd:
                    for line in fd.read().split("\n"):
                        x = re.match(r"version_info *= *\([0-9]+ *, *[0-9]+", line)
                        if x:
                            version_info = eval(
                                line[x.start(): x.end()].split("=")[1] + ")")
                            self.version = "%s.%s" % (version_info[0], version_info[1])
                            self.odoo_maj_version = version_info[0]
                            break

    def get_virtualenv(self):
        if not self.opt_args.virtualenv and self.script:
            venv = os.path.join(os.path.dirname(self.script), "venv_odoo")
            if os.path.isdir(venv):
                self.opt_args.virtualenv = venv
        if not self.opt_args.virtualenv and self.odoo_maj_version:
            venv = os.path.expanduser("~/VENV%d" % self.odoo_maj_version)
            if os.path.isdir(venv):
                self.opt_args.virtualenv = venv
        if not self.opt_args.virtualenv or not os.path.isdir(self.opt_args.virtualenv):
            if self.opt_args.virtualenv:
                print("Virtual environment path %s not found!"
                      % self.opt_args.virtualenv)
            self.opt_args.virtualenv = None
            return
        fn = os.path.join(self.opt_args.virtualenv, "bin", "activate")
        if not os.path.isfile(fn):
            print("Invalid virtual environment path %s!" % self.opt_args.virtualenv)
            self.opt_args.virtualenv = None

    def get_config(self):
        for (k, v) in (
                ("config", None),
                ("db_name", "demo"),
                ("db_user", "odoo"),
                ("db_pwd", "admin"),
                ("db_host", "localhost"),
                ("db_port", ""),
                ("http_port", None),
                ("xmlrpc_port", None),
                ("addons_path", [])):
            if not hasattr(self, k):
                setattr(self, k, v)

        rpcport = ""
        if not self.config and self.opt_args.config:
            self.config = self.opt_args.config
        if self.config and not os.path.isfile(self.config):
            self.config = None
        if self.config:
            Config = ConfigParser.RawConfigParser()
            Config.read(self.config)
            if not Config.has_section("options"):
                print("Invalid Configuration file %s: missed [options] section!"
                      % self.opt_args.config)
            else:
                for k in (
                        "db_name",
                        "db_user",
                        "db_pwd",
                        "db_host",
                        "db_port",
                        "addons_path"):
                    if Config.has_option("options", k):
                        setattr(self, k, Config.get("options", k))
                if Config.has_option("options", "http_port"):
                    rpcport = Config.get("options", "http_port")
                if not rpcport and Config.has_option("options", "xmlrpc_port"):
                    rpcport = Config.get("options", "xmlrpc_port")
                if rpcport:
                    rpcport = int(rpcport)
        if self.db_port and self.db_port.isdigit():
            self.db_port = int(self.db_port)
        if not rpcport:
            rpcport = clodoo.build_odoo_param(
                "RPCPORT",
                odoo_vid=self.opt_args.odoo_branch,
                multi=self.opt_args.multi)
        if self.odoo_maj_version < 10:
            self.xmlrpc_port = rpcport
        else:
            self.http_port = rpcport
        return 0

    def export_i18n(self):
        return call(self.prepare_os_cmd(), shell=True)

    def install_modules(self):
        return call(self.prepare_os_cmd(), shell=True)

    def import_i18n(self):
        return call(self.prepare_os_cmd(), shell=True)

    def update_modules(self):
        return call(self.prepare_os_cmd(), shell=True)

    def run_tests(self):
        return call(self.prepare_os_cmd(), shell=True)

    def run(self):
        return call(self.prepare_os_cmd(), shell=True)


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]

    run_odoo_debug = RunOdoo(cli_args)
    if (
            run_odoo_debug.opt_args.export_i18n
            and run_odoo_debug.opt_args.install
            and run_odoo_debug.opt_args.import_i18n
            and run_odoo_debug.opt_args.test
            and run_odoo_debug.opt_args.update
    ):
        print("Option switches conflict!")
        sts = 1
    elif run_odoo_debug.opt_args.export_i18n:
        sts = run_odoo_debug.export_i18n()
    elif run_odoo_debug.opt_args.install:
        sts = run_odoo_debug.install_modules()
    elif run_odoo_debug.opt_args.import_i18n:
        sts = run_odoo_debug.import_i18n()
    elif run_odoo_debug.opt_args.test:
        sts = run_odoo_debug.run_tests()
    elif run_odoo_debug.opt_args.update:
        sts = run_odoo_debug.update_modules()
    else:
        sts = run_odoo_debug.run()
    return sts


if __name__ == "__main__":
    exit(main())

