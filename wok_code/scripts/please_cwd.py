#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path as pth
from datetime import datetime, timedelta
import re

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import shutil

# from z0lib import z0lib

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param

__version__ = "2.0.19"

BIN_EXTS = ("xls", "xlsx", "png", "jpg")
RED = "\033[1;31m"
CLEAR = "\033[0;m"


class PleaseCwd(object):
    """NAME
        Various actions on current working directory.

    SYNOPSIS
        please [action] [cwd] [options]

        * clean: clean temporary files in current working directory and sub directories
        * clean_db: remove old databases and virtual directories
        * commit: commit PYPI sub-package
        * defcon precommit|gitignore: set default values for some configuration files
        * docs: create project documentation from egg-info or readme directory
        * edit: edit pofile or other project file
        * replace: replace master local branch of current package (only pypi pkgs)
        * translate: create it.po file with italian translation for Odoo module
        * update: update current package into devel virtual environment (only pypi pkgs)

    DESCRIPTION
        This command creates execute one of %(actions)s on current working directory.

        please clean
            Remove temporary files in current working directory and sub directories;
            this action remove old test log files too.

        please clean db
            Remove virtual directories created by travis emulator and test and templates
            databases created by test action. The test and template database have name
            like regex "(test|template)_{MODULE_NAME}_{ODO_MAJOR}"

        please commit -m "COMMIT_MESSAGE"
            This action, runs just on PYPI sub-package, does:
            1. Prepare setup.info file (in future will be removed)
            2. Execute <git add>
            3. Execute <git commit -M "COMMIT_MESSAGE">
            4. Replace source code into master directory

        please defcon FILE_NAME
            Create or update some configuration file with appropriate values for current
            directory. Current FILE_NAME are:
            1. precommit for ".pre-commit-config.yaml"
            2. gitignore for ".gitingore"

    OPTIONS
      %(options)s

    EXAMPLES
        please docs

    BUGS
        No known bugs.

    SEE ALSO
        Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>"""

    def __init__(self, please):
        self.please = please

    def action_opts(self, parser, for_help=False):
        self.please.add_argument(parser, "-B")
        self.please.add_argument(parser, "-b")
        self.please.add_argument(parser, "-C")
        self.please.add_argument(parser, "-c")
        self.please.add_argument(parser, "-d")
        if not for_help:
            self.please.add_argument(parser, "-n")
        parser.add_argument('-F', '--from-version')
        self.please.add_argument(parser, "-f")
        self.please.add_argument(parser, "-G")
        parser.add_argument('-m', '--message', help="Commit message")
        parser.add_argument(
            "--odoo-venv", action="store_true", help="Update Odoo virtual environments"
        )
        self.please.add_argument(parser, "-O")
        if not for_help:
            self.please.add_argument(parser, "-q")
        if not for_help:
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "--no-verify", action="store_true", help="Disable pre-commit on replace"
        )
        parser.add_argument(
            "--vme", action="store_true", help="Update $HOME/VME virtual environments"
        )
        parser.add_argument("args", nargs="*")
        return parser

    def cur_path_of_pkg(self):
        return (
            pth.dirname(os.getcwd())
            if pth.basename(os.getcwd()) != "tools"
            else os.getcwd())

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
        if not self.config:  # pylint: disable=access-member-before-definition
            self.config = self.please.opt_args.odoo_config or build_odoo_param(
                "CONFN", odoo_vid=".", multi=True)
        if not pth.isfile(self.config):
            self.please.log_error("No configuration file %s found!" % self.config)
            return 126
        Config = ConfigParser.RawConfigParser()
        Config.read(self.config)
        if not Config.has_section("options"):
            self.please.log_error(
                "Invalid Configuration file %s: missed [options] section!"
                % self.opt_args.config)
            return 33
        else:
            for k in (
                    "db_name",
                    "db_user",
                    "db_pwd",
                    "db_host",
                    "db_port",
                    "addons_path"):
                if Config.has_option("options", k):
                    if Config.get("options", k) == "False":
                        setattr(self, k, False)
                    else:
                        setattr(self, k, Config.get("options", k))
            if Config.has_option("options", "http_port"):
                rpcport = Config.get("options", "http_port")
            if not rpcport and Config.has_option("options", "xmlrpc_port"):
                rpcport = Config.get("options", "xmlrpc_port")
            if rpcport:
                rpcport = int(rpcport)

        if not self.db_port:  # pylint: disable=access-member-before-definition
            self.db_port = 5432
        elif self.db_port and self.db_port.isdigit():
            self.db_port = int(self.db_port)
        if not rpcport:
            rpcport = build_odoo_param(
                "RPCPORT", odoo_vid=".", multi=True)
        if self.odoo_major_version < 10:
            self.xmlrpc_port = rpcport
        else:
            self.http_port = rpcport
        return 0

    def connect_db(
            self, db_name=None, db_user=None, db_pwd=None, db_host=None, db_port=None):
        self.cnx = psycopg2.connect(
            dbname=db_name or self.db_name,
            user=db_user or self.db_user,
            password=db_pwd or self.db_pwd,
            host=db_host or self.db_host,
            port=db_port or self.db_port,
        )
        self.create_sql_cursor()

    def create_sql_cursor(self):
        if self.cnx:
            self.cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cr = self.cnx.cursor()

    def exec_sql(self, query, response=None, keep_cursor=False):
        try:
            self.cr.execute(query)
            if response:
                response = self.cr.fetchall()
            else:
                response = True
        except psycopg2.OperationalError:
            self.please.log_error("Error executing sql %s" % query)
            response = False
        if not keep_cursor:
            try:
                self.cr.close()
                self.cr = None
            except psycopg2.OperationalError:
                pass
        return response

    def assure_doc_dirs_odoo(self, is_repo=False):
        please = self.please
        branch = self.branch
        docdir = self.docdir
        if (
                please.opt_args.force
                and not please.opt_args.oca
                and not is_repo
                and (not pth.isfile(pth.join(docdir, "CONTRIBUTORS.rst"))
                     or not pth.isfile(pth.join(docdir, "AUTHORS.rst")))
        ):
            args = self.build_gen_readme_base_args(branch=branch)
            args.append("-RW")
            return please.chain_python_cmd("gen_readme.py", args)
        return 0

    def assure_doc_dirs_pypi(self):
        branch = self.branch
        docdir = self.docdir
        if not self.please.opt_args.dry_run:
            chnglog = pth.join(docdir, "CHANGELOG.rst")
            if not pth.isfile(chnglog):
                with open(chnglog, "w") as fd:
                    fd.write("%s (%s)\n" % (branch, "2023-09-23"))
                    fd.write("~~~~~~~~~~~~~~~~~~~~~~~\n")
                    fd.write("\n")
                    fd.write("* Initial implementation\n")
        return 0

    def assure_doc_dirs(self, docdir=None, pkgtype=None, is_repo=False):
        if pkgtype not in ("odoo", "pypi"):
            self.please.log_error("Invalid package type: use 'odoo' or 'pypi'")
            return 33
        please = self.please
        if pkgtype == "pypi":
            docs_dir = "./docs"
            if not pth.isdir(docs_dir):
                if not please.opt_args.force and not please.opt_args.dry_run:
                    if please.opt_args.verbose:
                        self.please.log_error("Directory %s not found!" % docs_dir)
                    return 126
                if please.opt_args.verbose:
                    self.please.log_warning("Directory %s not found!" % docs_dir)
                if not please.opt_args.dry_run:
                    os.mkdir(docs_dir)
            self.docs_dir = docs_dir
            logo = pth.join(docs_dir, "logozero_180x46.png")
            if not pth.isfile(logo):
                srclogo = pth.join(
                    please.get_pkg_tool_dir(pkgtool=True),
                    "docs",
                    "logozero_180x46.png")
                if please.opt_args.verbose:
                    print("%s cp %s %s" % (">" if please.opt_args.dry_run else "$",
                                           srclogo,
                                           logo))
                if not please.opt_args.dry_run:
                    shutil.copy(srclogo, logo)

        docdir = docdir or ("readme" if pkgtype == "odoo" else "egg-info")
        if (
                not docdir.startswith("/")
                and not docdir.startswith("./")
                and not docdir.startswith("~/")
        ):
            docdir = pth.join(".", docdir)
        if not pth.isdir(docdir):
            if not please.opt_args.force and not please.opt_args.dry_run:
                if please.opt_args.verbose:
                    self.please.log_error("Directory %s not found!" % docdir)
                return 126
            if please.opt_args.verbose:
                self.please.log_warning("Directory %s not found!" % docdir)
            if not please.opt_args.dry_run:
                os.mkdir(docdir)
        self.docdir = docdir

        if pkgtype == "odoo":
            return self.assure_doc_dirs_odoo(is_repo=is_repo)
        elif pkgtype == "pypi":
            return self.assure_doc_dirs_pypi()
        return 33

    def build_gen_readme_base_args(self, branch=None):
        branch = branch or self.branch
        args = []
        if self.please.opt_args.debug:
            args.append("-" + ("B" * self.please.opt_args.debug))
        if branch:
            args.append("-b")
            args.append(branch)
        if self.please.opt_args.force:
            args.append("-f")
        if self.please.opt_args.dry_run:
            args.append("-n")
        return args

    def do_clean(self):
        please = self.please
        is_odoo = please.is_odoo_pkg()
        is_pypi = please.is_pypi_pkg()
        if (
                is_odoo
                or is_pypi
                or please.is_repo_odoo()
                or please.is_repo_ocb()
        ):
            sts = 0
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                for fn in files:
                    if (
                            fn != "it.mo"
                            and not fn.endswith(".bak")
                            and not fn.endswith("~")
                            and not fn.endswith(".po.orig")
                            and not fn.endswith(".pot")
                    ):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.os_system(cmd, with_shell=True, rtime=True)
                    if sts:
                        break
            logdir = please.get_logdir()
            if is_odoo and pth.isdir(logdir):
                last = " "
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_\d{8}.txt$", fn) and fn[-12:] > last:
                            last = fn[-12:]
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_\d{8}.txt$", fn) and fn[-12:] != last:
                            cmd = "rm " + pth.join(root, fn)
                            sts = please.os_system(cmd)
                            if sts:
                                break
            return sts
        return please.do_iter_action("do_clean", act_all_pypi=True, act_tools=True)

    def do_clean_db(self):
        def connect_db():
            return psycopg2.connect(
                dbname="template1",
                user="odoo",
            )

        please = self.please
        sts = 126
        remove_ts = datetime.now() - timedelta(
            seconds=30 if please.opt_args.force else 1800)
        for fn in sorted(os.listdir(pth.expanduser("~/"))):
            if not fn.startswith("VENV_"):
                continue
            ffn = pth.expanduser("~/%s" % fn)
            fn_ts = max(
                datetime.fromtimestamp(pth.getmtime(ffn)),
                datetime.fromtimestamp(pth.getmtime(ffn))
            )
            if fn_ts < remove_ts:
                sts = please.os_system("rm -fR " + ffn, with_shell=True, rtime=True)
                if sts:
                    break

        cr = connect_db().cursor()
        cr.execute(
            "SELECT datname,"
            "(pg_stat_file('base/'||oid ||'/PG_VERSION')).modification as datmod,"
            "datdba::regrole"
            " FROM pg_database order by datmod"
        )
        rex = re.compile("^(test|template)_[a-z]+")
        date_limit = datetime.strftime(datetime.now() - timedelta(21), "%Y-%m-%d")
        for row in cr.fetchall():
            db_name, db_date, db_user = row[0], row[1], row[2]
            if (
                    datetime.strftime(db_date, "%Y-%m-%d") < date_limit
                    and rex.match(db_name)
            ):
                sts = please.os_system("dropdb -U%s %s" % (db_user, db_name),
                                       rtime=True)
                if sts:
                    break
                target_dir = pth.expanduser(
                    pth.join("~",
                             ".local",
                             "share",
                             db_user.capitalize(),
                             "filestore",
                             db_name))
                if pth.isdir(target_dir):
                    please.os_system(
                        "rm -fR" % target_dir, with_shell=True, rtime=True)
        return sts

    def do_commit(self):
        please = self.please
        sts = 126
        if not please.opt_args.message:
            please.log_error("Missed commit message! Please use -m 'message'")
            sts = 125
        elif please.is_pypi_pkg():
            sts = self.do_docs()
        else:
            please.log_warning("No PYPI directory found")
        if sts == 0:
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.os_system(cmd)
                    if sts:
                        please.log_warning(
                            "Cannot remove file %s!" % pth.join(root, fn))
                        break
        if sts == 0:
            tgtdir = please.get_pkg_tool_dir()
            if not pth.isdir(tgtdir):
                self.please.log_error("Tools directory %s not found!" % tgtdir)
                return 33

            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            sts = 0
            if pkgname != "tools":
                fn = pth.join(pth.dirname(srcdir), "setup.py")
                if pth.isfile(fn):
                    sts = please.os_system(
                        "cp %s %s" % (fn, pth.join(srcdir, "scripts", "setup.info")),
                        rtime=True
                    )
            if not please.opt_args.no_verify:
                sts = please.os_system("git add ../", rtime=True)
                if sts == 0:
                    sts = please.os_system(
                        "git commit -m \"" + please.opt_args.message + "\"")
            if pkgname != "tools":
                if sts == 0:
                    sts = please.os_system(
                        "rsync -a --exclude='*.pyc' --exclude='.*' --exclude='*~'"
                        " --exclude='*.log' --exclude='*.bak' %s/ %s/"
                        % (srcdir, pth.join(tgtdir, pkgname)),
                        rtime=True,
                    )
                if sts == 0:
                    for item in ("setup.py", "README.rst"):
                        fn = pth.join(pth.dirname(srcdir), item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.os_system(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            else:
                if sts == 0:
                    for item in ("egg-info", "docs", "tests", "templates",
                                 "license_text"):
                        sts = please.os_system(
                            "rsync -a --exclude='*.pyc' --exclude='.*' --exclude='*~'"
                            " --exclude='*.log' --exclude='*.bak' %s/ %s/"
                            % (pth.join(srcdir, item), pth.join(tgtdir, item)),
                            rtime=True,
                        )
                        if sts:
                            break
                if sts == 0:
                    for item in (
                        "install_tools.sh",
                        "LICENSE",
                        "odoo_template_tnl.xlsx",
                        "README.rst",
                    ):
                        fn = pth.join(srcdir, item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.os_system(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            return sts
        return please.do_iter_action("do_commit", act_all_pypi=True, act_tools=False)

    def do_defcon(self):
        self.please.log_error(
            "Missed sepcification:\nplease defcon precommit|gitignore")
        return 126

    def _do_defcon(self, tmpl_fn, tgt_fn):
        please = self.please
        branch = target = ""
        sts = 126
        submodules = []
        py23 = 3

        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_repo_ocb():
            is_odoo_pkg = True
            sts, branch = please.get_odoo_branch_from_git()
            if sts == 0:
                py23 = 2 if int(branch.split(".")[0]) <= 10 else 3
            sts = 0
        else:
            is_odoo_pkg = False

        for fn in os.listdir(os.getcwd()):
            if fn in (
                "addons_kalamitica",
                "coverage",
                "generic",
                "nardo_modules",
                "venv_odoo",
                "website-themes",
            ):
                submodules.append("/%s" % fn)
                continue
            ffn = pth.join(os.getcwd(), fn)
            if pth.isdir(pth.join(ffn, ".git")):
                submodules.append("/%s" % fn)

        srcpath = pth.join(please.get_pkg_tool_dir(pkgtool=True), "templates")
        if is_odoo_pkg and py23 == 2 and tmpl_fn == "pre-commit-config2.yaml":
            srcpath = pth.join(srcpath, "pre-commit-config2.yaml")
        else:
            srcpath = pth.join(srcpath, tmpl_fn)
        if not pth.isfile(srcpath):
            self.please.log_error("File %s not found" % srcpath)
            sts = 123
        elif sts == 126:
            sts = 0

        if sts == 0:
            max_ctr = 10
            while not pth.isdir(".git"):
                max_ctr -= 1
                if not max_ctr:
                    self.please.log_error("Git repository not found!")
                    sts = 123
                    break
                os.chdir(pth.dirname(os.getcwd()))
        if sts == 0:
            tgtpath = pth.join(os.getcwd(), tgt_fn)
            with open(srcpath, "r") as fd:
                trig = ""
                for line in fd.read().split("\n"):
                    if "entry: arcangelo" in line:
                        if branch:
                            target += re.sub("entry: arcangelo .*",
                                             "entry: arcangelo -i -b%s\n" % branch,
                                             line)
                        else:
                            target += re.sub("entry: arcangelo .*",
                                             "entry: arcangelo -i -P\n",
                                             line)
                        continue
                    found = line.startswith("!")
                    if trig == "odoo":
                        if branch and line.startswith(" "):
                            found = True
                        else:
                            for x in submodules:
                                if x == line:
                                    found = True
                                    break
                    elif trig == "pypi":
                        if not branch and line.startswith(" "):
                            found = True
                        else:
                            if (
                                ".egg-info/" not in line
                                and pth.isdir(pth.join(
                                    *[os.getcwd()] + [x for x in line.split("/") if x]
                                ))
                            ):
                                found = True
                    if not trig or found:
                        target += "%s\n" % line
                    if re.match("^ *# odoo repositories", line):
                        trig = "odoo"
                    elif re.match("^ *# tools building path", line):
                        trig = "pypi"

            if not please.opt_args.dry_run:
                if please.opt_args.verbose:
                    self.please.log_success("File %s updated/created" % tgtpath)
                with open(tgtpath, "w") as fd:
                    fd.write(target)
            elif please.opt_args.verbose:
                self.please.log_success("File %s should be updated/created" % tgtpath)
        return sts

    def do_defcon_precommit(self):
        return self._do_defcon("pre-commit-config.yaml", ".pre-commit-config.yaml")

    def do_defcon_gitignore(self):
        return self._do_defcon("gitignore", ".gitignore")

    def do_docs(self):
        please = self.please
        if please.is_odoo_pkg():
            if not pth.isdir("readme"):
                please.log_warning(
                    "Module %s w/o documentation dir!" % pth.basename(os.getcwd()))
                return 3
            sts, branch = please.get_odoo_branch_from_git(try_by_fs=True)
            if sts == 0:
                self.branch = branch
                sts = self.assure_doc_dirs(pkgtype="odoo")
                if sts:
                    return sts
                please.merge_test_result()
                odoo_major_version = int(branch.split(".")[0])
                repo_name = build_odoo_param("REPOS", odoo_vid=".", multi=True)
                if please.opt_args.oca:
                    sts = please.os_system(
                        "oca-gen-addon-readme --gen-html --branch=%s --repo-name=%s"
                        % (branch, repo_name),
                        with_shell=True, rtime=True)
                else:
                    if repo_name == "marketplace":
                        args = self.build_gen_readme_base_args(branch=branch)
                        args.append("-R")
                        sts = please.chain_python_cmd(
                            "gen_readme.py", args, rtime=True)
                    args = self.build_gen_readme_base_args(branch=branch)
                    sts = please.chain_python_cmd(
                        "gen_readme.py", args, rtime=True)
                    if sts == 0:
                        args.append("-I")
                        sts = please.chain_python_cmd(
                            "gen_readme.py", args, rtime=True)
                    if sts == 0 and odoo_major_version <= 7:
                        args = self.build_gen_readme_base_args(branch=branch)
                        args.append("-R")
                        sts = please.chain_python_cmd(
                            "gen_readme.py", args, rtime=True)
                if sts == 0:
                    self.do_clean()
                return sts
        elif (
                please.is_repo_odoo()
                or please.is_repo_ocb()
        ):
            sts, branch = please.get_odoo_branch_from_git(try_by_fs=True)
            if sts == 0:
                self.branch = branch
                sts = self.assure_doc_dirs(pkgtype="odoo", is_repo=True)
                if sts:
                    return sts
                if not please.opt_args.oca:
                    args = self.build_gen_readme_base_args(branch=branch)
                    sts = please.chain_python_cmd(
                        "gen_readme.py", args, rtime=True)
            return sts
        elif please.is_pypi_pkg():
            self.branch = please.get_pypi_version()
            # pkg_name = pth.basename(pth.dirname(os.getcwd()))
            sts = self.assure_doc_dirs(pkgtype="pypi")
            if sts:
                return sts
            if not pth.isdir(self.docs_dir):
                please.log_error(
                    "Document template directory %s not found!" % self.docs_dir)
                return 33 if not self.please.opt_args.dry_run else 0
            args = self.build_gen_readme_base_args(branch=self.branch)
            sts = self.please.chain_python_cmd(
                "gen_readme.py", args, rtime=True)
            if sts == 0:
                args.append("-I")
                sts = please.chain_python_cmd(
                    "gen_readme.py", args, rtime=True)
            if sts == 0:
                saved_pwd = os.getcwd()
                os.chdir(self.docs_dir)
                sts = please.os_system("make html", rtime=True)
                os.chdir(saved_pwd)
            if sts == 0:
                self.do_clean()
            return sts
        return please.do_iter_action("do_docs", act_all_pypi=True, act_tools=True)

    def do_edit(self):
        please = self.please
        if please.is_odoo_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=pth.join(pth.dirname(__file__), "please.sh")
            )
            return please.os_system(cmd)
        return 126

    def do_export(self):
        if self.please.is_odoo_pkg():
            return self._do_translate_export(action="export")
        return 126

    def do_publish(self):
        self.please.log_error(
            "Missed specification:\nplease publish pypi|test_pypi|marketplace")
        return 126

    def do_publish_pypi(self):
        please = self.please
        if please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=pth.join(pth.dirname(__file__), "please.sh")
            )
            return please.os_system(cmd, rtime=True)
        return 126

    def do_publish_marketplace(self):
        please = self.please
        if please.is_odoo_pkg():
            for manifest in ("__manifest__.py", "__openerp__.py"):
                if pth.isfile(manifest):
                    break
            with open(manifest, "r") as fd:
                contents = eval(fd.read())
            if not contents.get("application"):
                self.please.log_error("You can only publish application module!")
                print("  Add:")
                print("     \"application\": True")
                print("  in your manifest %s" % manifest)
                return 33
            sts, branch = please.get_odoo_branch_from_git(try_by_fs=True)
            if sts == 0:
                module_name = build_odoo_param("PKGNAME", odoo_vid=".", multi=True)
                target_dir = pth.expanduser(
                    pth.join("~", branch, "marketplace", module_name))
                if not pth.isdir(pth.dirname(target_dir)):
                    self.please.log_error(
                        "Path %s not found!" % pth.dirname(target_dir))
                    return 33
                if pth.isdir(target_dir):
                    shutil.rmtree(target_dir)
                shutil.copytree(os.getcwd(), target_dir)
                sts = please.os_system("cd " + target_dir)
                if sts == 0:
                    target_dir = please.get_logdir(path=target_dir)
                    if pth.isdir(target_dir):
                        shutil.rmtree(target_dir)
                    args = self.build_gen_readme_base_args(branch=branch)
                    args.append("-O")
                    sts = please.chain_python_cmd("gen_readme.py", args)
                if sts == 0:
                    args = self.build_gen_readme_base_args(branch=branch)
                    args.append("-O")
                    args.append("-R")
                    sts = please.chain_python_cmd("gen_readme.py", args)
                if sts == 0:
                    sts = please.os_system("git add ../", rtime=True)
                if sts == 0:
                    sts = please.os_system("pre-commit run", rtime=True)
            return sts
        return 126

    def do_replace(self):
        please = self.please
        please.log_warning("Deprecated action! Please use 'please commit'")
        sts = 126
        if please.is_pypi_pkg():
            sts = self.do_docs()
        if sts == 0:
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.os_system(cmd)
                    if sts:
                        please.log_warning(
                            "Cannot remove file %s!" % pth.join(root, fn))
                        break
        if sts == 0:
            tgtdir = please.get_pkg_tool_dir()
            if not pth.isdir(tgtdir):
                please.log_error("Tools directory %s not found!" % tgtdir)
                return 33

            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            if pkgname != "tools":
                sts = 0
                if not please.opt_args.no_verify:
                    sts = please.os_system("git add ../", rtime=True)
                    if sts == 0:
                        sts = please.os_system("pre-commit run", rtime=True)
                if sts == 0:
                    sts = please.os_system(
                        "rsync -a --exclude='*.pyc' --exclude='.*' --exclude='*~'"
                        " --exclude='*.log' --exclude='*.bak' %s/ %s/"
                        % (srcdir, pth.join(tgtdir, pkgname)),
                        rtime=True,
                    )
                if sts == 0:
                    for item in ("setup.py", "README.rst"):
                        fn = pth.join(pth.dirname(srcdir), item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.os_system(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            else:
                if not please.opt_args.no_verify:
                    sts = please.os_system("git add ./", rtime=True)
                if sts == 0:
                    for item in ("egg-info", "docs", "tests", "templates",
                                 "license_text"):
                        sts = please.os_system(
                            "rsync -a --exclude='*.pyc' --exclude='.*' --exclude='*~'"
                            " --exclude='*.log' --exclude='*.bak' %s/ %s/"
                            % (pth.join(srcdir, item), pth.join(tgtdir, item)),
                            rtime=True,
                        )
                        if sts:
                            break
                if sts == 0:
                    for item in (
                        "install_tools.sh",
                        "LICENSE",
                        "odoo_template_tnl.xlsx",
                        "README.rst",
                    ):
                        fn = pth.join(srcdir, item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.os_system(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            return sts
        return please.do_iter_action("do_replace", act_all_pypi=True, act_tools=False)

    def do_translate(self):
        if self.please.is_odoo_pkg():
            return self._do_translate_export(action="all")
        return 126

    def _do_translate_export(self, action="all"):
        def get_po_revision_date(pofile):
            po_revision_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(pofile, "r") as fd:
                for ln in fd.read().split("\n"):
                    if "PO-Revision-Date:" in ln:
                        x = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}.[0-9]{2}:[0-9]{2}",
                                      ln)
                        if ln:
                            po_revision_date = ln[x.start(): x.end()]
                            break
            return po_revision_date

        please = self.please
        if please.is_odoo_pkg():
            sts, branch = please.get_odoo_branch_from_git(try_by_fs=True)
            if sts == 0:
                if not pth.isdir("./i18n"):
                    if not please.opt_args.force:
                        please.log_warning(
                            "No directory i18n found! Use -f switch to create it")
                        return 3
                    os.mkdir("./i18n")
                self.branch = branch
                self.odoo_major_version = int(branch.split(".")[0])
                module_name = build_odoo_param("PKGNAME", odoo_vid=".", multi=True)
                pofile = "./i18n/it.po"
                if not pth.isfile(pofile):
                    if not please.opt_args.force:
                        please.log_warning(
                            "No file %s found! Use -f switch to create it" % pofile)
                        return 3
                    args = [
                        "-f",
                        "-m", module_name,
                    ]
                    if branch:
                        args.append("-b")
                        args.append(branch)
                    if please.opt_args.dry_run:
                        args.append("-n")
                    args.append(pofile)
                    please.chain_python_cmd("makepo_it.py", args)
                sts = self.get_config()
                if sts:
                    return sts
                self.connect_db(db_name="template1")
                response = self.exec_sql("SELECT datname FROM pg_catalog.pg_database",
                                         response=True)
                self.db_name = please.opt_args.database or (
                    "test_%s_%s" % (module_name, self.odoo_major_version))
                if self.db_name not in [x[0] for x in response]:
                    please.log_warning("Database %s does not exist!" % self.db_name)
                    return 3
                self.connect_db()
                query = ("select state from ir_module_module where name = '%s'"
                         % module_name)
                response = self.exec_sql(query, response=True, keep_cursor=True)
                state = response[0][0]
                if state != "installed":
                    please.log_error("Module %s not installed!" % module_name)
                    return 33
                query = ("select value from ir_config_parameter"
                         " where key='database.create_date'")
                response = self.exec_sql(query, response=True)
                db_create_date = response[0][0]
                po_revision_date = get_po_revision_date(pofile)
                action_done = False
                if (
                        sts == 0
                        and action in ("all", "translate")
                        and (please.opt_args.force or db_create_date > po_revision_date)
                ):
                    args = [
                        "-m", module_name,
                    ]
                    if branch:
                        args.append("-b")
                        args.append(branch)
                    if please.opt_args.debug:
                        args.append("-" + ("B" * please.opt_args.debug))
                    if (
                            hasattr(please.opt_args, "ignore_cache")
                            and please.opt_args.ignore_cache
                    ):
                        args.append("-C")
                    if self.config:
                        args.append("-c")
                        args.append(self.config)
                    if self.db_name:
                        args.append("-d")
                        args.append(self.db_name)
                    if please.opt_args.verbose:
                        args.append("-" + ("v" * please.opt_args.verbose))
                    if please.opt_args.dry_run:
                        args.append("-n")
                    sts = please.chain_python_cmd("odoo_translation.py", args)
                    action_done = True
                if (
                        sts == 0
                        and action in ("all", "export")
                        and (please.opt_args.force or db_create_date > po_revision_date)
                ):
                    args = [
                        "-e",
                        "-m", module_name,
                    ]
                    if branch:
                        args.append("-b")
                        args.append(branch)
                    if self.config:
                        args.append("-c")
                        args.append(self.config)
                    if self.db_name:
                        args.append("-d")
                        args.append(self.db_name)
                    if please.opt_args.verbose > 1:
                        args.append("-" + ("v" * (please.opt_args.verbose - 1)))
                    else:
                        args.append("-q")
                    if please.opt_args.dry_run:
                        args.append("-n")
                    sts = please.chain_python_cmd("run_odoo_debug.py", args)
                    action_done = True
                if not action_done:
                    self.please.log_warning("No transaction done")
                return sts
        return 126

    def do_update(self):
        please = self.please
        if please.is_pypi_pkg():
            if os.environ.get("HOME_DEVEL"):
                tgtdir = pth.join(os.environ["HOME_DEVEL"], "venv")
            else:
                tgtdir = pth.expanduser("~/devel/venv")
            if not pth.isdir(tgtdir):
                please.log_error("Tools directory %s not found!" % tgtdir)
                return 33
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            sts = 0
            if pkgname != "tools":
                fn = pth.join(pth.dirname(srcdir), "setup.py")
                if pth.isfile(fn):
                    sts = please.os_system(
                        "cp %s %s" % (fn, pth.join(srcdir, "scripts", "setup.info")),
                        rtime=True
                    )
                if sts == 0:
                    sts = please.os_system(
                        "vem %s update %s" % (tgtdir, pth.dirname(srcdir)), rtime=True
                    )
            if sts == 0 and please.opt_args.vme:
                sts = self.do_update_vme()
            if sts == 0 and please.opt_args.odoo_venv:
                sts = self.do_update_venv()
            return sts
        return please.do_iter_action(
            "do_update", act_all_pypi=True, act_tools=False,
            pypi_list=[x
                       for x in please.get_pypi_list()
                       if x not in ("os0", "travis_emulator", "wok_code", "zar")])

    def do_update_venv(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            if pkgname != "tools":
                rex = re.compile(r"[a-z0-9][a-z0-9_.]+$")
                for root, dirs, files in os.walk(pth.expanduser("~/")):
                    for fn in sorted(dirs):
                        if not rex.match(fn):
                            continue
                        tgtdir = pth.join(root, fn, "venv_odoo")
                        if not pth.isdir(tgtdir):
                            continue
                        sts = please.os_system(
                            "vem %s update %s" % (tgtdir, pth.dirname(srcdir)),
                            rtime=True,
                        )
                        if sts:
                            break
        return sts

    def do_update_vme(self):
        please = self.please
        sts = 126
        if please.is_pypi_pkg():
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            if pkgname != "tools":
                vme_dir = pth.expanduser("~/VME")
                for fn in sorted(os.listdir(vme_dir)):
                    tgtdir = pth.join(vme_dir, fn)
                    if not pth.isdir(tgtdir) or not pth.isdir(
                        pth.join(tgtdir, "bin")
                    ):
                        continue
                    sts = please.os_system(
                        "vem %s update %s" % (tgtdir, pth.dirname(srcdir)),
                        rtime=True,
                    )
                    if sts:
                        break
        return sts

    def do_version(self):
        def search_last_history(fqn):
            if pth.isfile(fqn):
                with open(fqn, "r") as fd:
                    for line in fd.read().split("\n"):
                        if re.match(r"[\d]+\.[\d]+", line):
                            x = re.match(r"[\d]+(\.[\d]+)+", line)
                            if x:
                                ver_text = line[x.start(): x.end()]
                                if ver_text != self.ref_version:
                                    print(fqn, "->", ver_text, "***")
                            break

        def update_version(fqn, regex):
            target = ""
            do_rewrite = False
            ext = fqn.rsplit(".", 1)
            ext = ext[1] if len(ext) > 1 else ""
            if ext in BIN_EXTS:
                return 0
            with open(fqn) as fd:
                try:
                    for ln in fd.read().split("\n"):
                        x = regex.match(ln)
                        if x:
                            ver_text = x.groups()[1]
                            cmp_text = re.match(r"[\d]+\.[\d]+", ver_text).string
                            if pth.basename(fqn) in ("setup.py",
                                                     "__manifest__.py",
                                                     "__openerp__.rst"):
                                self.ref_version = cmp_text
                                print(fqn, "->", ver_text)
                            elif cmp_text != self.ref_version:
                                print(fqn, "->", ver_text, "***")
                            elif please.opt_args.verbose > 1:
                                print(fqn)
                            if (
                                    please.opt_args.branch
                                    and ver_text != please.opt_args.branch
                            ):
                                ln = re.sub(
                                    r"\d+\.\d+\.\d+(\.\d+)?(\.\d+)?(\.\d+)?",
                                    please.opt_args.branch,
                                    ln
                                )
                                do_rewrite = True
                        target += ln
                        target += "\n"
                except BaseException as e:
                    do_rewrite = False
                    please.log_error("Error %s reading %s" % (e, fqn))
                if do_rewrite:
                    if please.opt_args.verbose:
                        print(fqn, "=>", please.opt_args.branch)
                    if not please.opt_args.dry_run:
                        with open(fqn, "w") as fd:
                            fd.write(target)
            return 0

        please = self.please
        if please.opt_args.from_version:
            REGEX_VER = re.compile(
                "^#? *(__version__|version|release) *= *[\"']?(%s)[\"']?"
                % please.opt_args.from_version)
            REGEX_DICT_VER = re.compile(
                "^ *([\"']version[\"']: [\"'])(%s)[\"']"
                % please.opt_args.from_version)
            REGEX_TESTENV_VER = re.compile("^(.* v)(%s)" % please.opt_args.from_version)
        else:
            REGEX_VER = re.compile(
                r"^#? *(__version__|version|release) *= *[\"']?([0-9]+\.[0-9.]+)[\"']?")
            REGEX_DICT_VER = re.compile(
                r"^ *([\"']version[\"']: [\"'])([0-9]+\.[0-9.]+)[\"']")
            REGEX_TESTENV_VER = re.compile(
                r"^(.*v)(\d+\.\d+\.\d+)")
        if please.is_pypi_pkg():
            sts = 0
            self.ref_version = ""
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                dirs[:] = [
                    d
                    for d in dirs
                    if (
                        not d.startswith(".")
                        and not d.startswith("_")
                        and not d.endswith("~")
                        and not d.endswith(".egg-info")
                        and d not in ("build",
                                      "debian",
                                      "dist",
                                      "doc",
                                      "docs",
                                      "egg-info",
                                      "filestore",
                                      "history",
                                      "howtos",
                                      "html",
                                      "images"
                                      "latex",
                                      "migrations",
                                      "redhat",
                                      "reference",
                                      "tests",
                                      "tmp",
                                      "Trash",
                                      "venv_odoo",
                                      "VME",
                                      "win32")
                    )
                ]
                for fn in files:
                    if (
                            fn.endswith(".bak")
                            or fn.endswith("~")
                            or fn.endswith(".log")
                            or fn.endswith(".pyc")
                            or fn.endswith(".svg")
                            or fn.startswith("LICENSE")
                    ):
                        continue
                    if fn in ("testenv.py", "testenv.rst", "_check4deps_.py"):
                        rex = REGEX_TESTENV_VER
                    elif fn in ("__manifest__.py", "__openerp__.rst"):
                        rex = REGEX_DICT_VER
                    else:
                        rex = REGEX_VER
                    sts = update_version(pth.join(root, fn), rex)
                    if sts:
                        break
            if sts == 0:
                fqn = pth.join(os.getcwd(), "docs", "conf.py")
                if pth.isfile(fqn):
                    sts = update_version(fqn, REGEX_VER)
            if sts == 0:
                search_last_history(pth.join("egg-info", "CHANGELOG.rst"))
            return sts
        elif please.is_odoo_pkg():
            fqn = "__manifest__.py"
            if not pth.isfile(fqn):
                fqn = "__openerp__.py"
            if not pth.isfile(fqn):
                please.log_warning("Manifest file not found!")
                return 3
            search_last_history(pth.join("readme", "CHANGELOG.rst"))
            return update_version(fqn, REGEX_DICT_VER)
        elif (please.opt_args.branch or please.opt_args.from_version):
            please.log_error("Version options are not applicable to all packages")
            return 126
        return please.do_iter_action("do_version", act_all_pypi=True, act_tools=False)
