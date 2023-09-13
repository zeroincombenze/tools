#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path as pth
from datetime import datetime, timedelta
import re

import psycopg2

try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param

__version__ = "2.0.11"
BIN_EXTS = ("xls", "xlsx", "png", "jpg")


class PleaseCwd(object):
    """NAME
        Various actions on current working directory.

    SYNOPSIS
        please [action] [cwd] [options]

        * clean: clean temporary file in current working directory and sub directories
        * clean_db: remove old databases
        * defcon precommit|gitignore: set default values for some configuration files
        * docs: create project documentation from egg-info or readme directory
        * edit: edit pofile or other project file
        * replace: replace master local barnch of current package (only pypi pkgs)
        * translate: create it.po file with italian translation for Odoo module
        * update: update current package into devel virtual environment (only pypi pkgs)

    DESCRIPTION
        This command creates execute one of %(actions)s
        on current working directory.

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
        self.please.add_argument(parser, "-c")
        if not for_help:
            self.please.add_argument(parser, "-n")
        parser.add_argument('-F', '--from-version')
        self.please.add_argument(parser, "-f")
        parser.add_argument('-m', '--message', help="Commit message")
        parser.add_argument(
            "--odoo-venv", action="store_true", help="Update Odoo virtual environments"
        )
        self.please.add_argument(parser, "-O")
        if not for_help:
            self.please.add_argument(parser, "-q")
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
                            not fn.endswith(".bak")
                            and not fn.endswith("~")
                            and not fn.endswith(".po.orig")
                    ):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        break
            logdir = pth.join(os.getcwd(), "tests", "logs")
            if is_odoo and pth.isdir(logdir):
                last = " "
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_\d{8}.txt$", fn) and fn[12:] > last:
                            last = fn[12:]
                for root, dirs, files in os.walk(logdir):
                    for fn in files:
                        if re.match(r".*_\d{8}.txt$", fn) and fn[12:] != last:
                            cmd = "rm " + pth.join(root, fn)
                            sts = please.run_traced(cmd)
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
                sts = please.run_traced("rm -fR " + ffn, rtime=True)
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
        date_limit = datetime.strftime(datetime.now() - timedelta(30), "%Y-%m-%d")
        for row in cr.fetchall():
            db_name, db_date, db_user = row[0], row[1], row[2]
            if (
                    datetime.strftime(db_date, "%Y-%m-%d") < date_limit
                    and rex.match(db_name)
            ):
                sts = please.run_traced("dropdb -U%s %s" % (db_user, db_name),
                                        rtime=True)
                if sts:
                    break
        return sts

    def do_commit(self):
        please = self.please
        sts = 126
        if not please.opt_args.message:
            print("Missed commit message! Please use -m 'message'")
            sts = 1
        elif please.is_pypi_pkg():
            sts = self.do_docs()
        else:
            print("No PYPI directory found")
        if sts == 0:
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        print("Cannot remove file %s!" % pth.join(root, fn))
                        break
        if sts == 0:
            if os.environ.get("HOME_DEVEL"):
                tgtdir = pth.join(
                    pth.dirname(os.environ["HOME_DEVEL"]), "tools"
                )
            elif pth.isdir("~/odoo/tools"):
                tgtdir = pth.expanduser("~/odoo/tools")
            else:
                tgtdir = pth.expanduser("~/tools")
            if not pth.isdir(tgtdir):
                print("Tools directory %s not found!" % tgtdir)
                return 2
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            sts = 0
            if pkgname != "tools":
                fn = pth.join(pth.dirname(srcdir), "setup.py")
                if pth.isfile(fn):
                    sts = please.run_traced(
                        "cp %s %s" % (fn, pth.join(srcdir, "scripts", "setup.info")),
                        rtime=True
                    )
            if not please.opt_args.no_verify:
                sts = please.run_traced("git add ../", rtime=True)
                if sts == 0:
                    sts = please.run_traced(
                        "git commit -m \"" + please.opt_args.message + "\"")
            if pkgname != "tools":
                if sts == 0:
                    sts = please.run_traced(
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
                        sts = please.run_traced(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            else:
                if sts == 0:
                    for item in ("egg-info", "docs", "tests", "templates",
                                 "license_text"):
                        sts = please.run_traced(
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
                        "odoo_default_tnl.xlsx",
                        "odoo_template_tnl.xlsx",
                        "README.rst",
                    ):
                        fn = pth.join(srcdir, item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.run_traced(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            return sts
        return please.do_iter_action("do_replace", act_all_pypi=True, act_tools=False)

    def do_defcon(self):
        print("Missed sepcification:\nplease defcon precommit|gitignore")
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

        if please.opt_args.debug:
            if os.environ.get("HOME_DEVEL"):
                srcpath = pth.join(os.environ["HOME_DEVEL"], "pypi")
            elif pth.isdir("~/odoo/tools"):
                srcpath = pth.expanduser("~/odoo/devel/pypi")
            else:
                srcpath = pth.expanduser("~/devel/pypi")
            srcpath = pth.join(srcpath, "tools", "templates")
        else:
            if os.environ.get("HOME_DEVEL"):
                srcpath = pth.join(
                    pth.dirname(os.environ["HOME_DEVEL"]), "tools"
                )
            elif pth.isdir("~/odoo/tools"):
                srcpath = pth.expanduser("~/odoo/tools")
            else:
                srcpath = pth.expanduser("~/odoo/tools")
            srcpath = pth.join(srcpath, "templates")

        if is_odoo_pkg and py23 == 2 and tmpl_fn == "pre-commit-config2.yaml":
            srcpath = pth.join(srcpath, "pre-commit-config2.yaml")
        else:
            srcpath = pth.join(srcpath, tmpl_fn)
        if not pth.isfile(srcpath):
            print("File %s not found" % srcpath)
            sts = 1
        elif sts == 126:
            sts = 0

        if sts == 0:
            max_ctr = 10
            while not pth.isdir(".git"):
                max_ctr -= 1
                if not max_ctr:
                    print("Git repository not found!")
                    sts = 1
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
                    print("File %s updated/created" % tgtpath)
                with open(tgtpath, "w") as fd:
                    fd.write(target)
            elif please.opt_args.verbose:
                print("File %s should be updated/created" % tgtpath)
        return sts

    def do_defcon_precommit(self):
        return self._do_defcon("pre-commit-config.yaml", ".pre-commit-config.yaml")

    def do_defcon_gitignore(self):
        return self._do_defcon("gitignore", ".gitignore")

    def do_docs(self):
        please = self.please
        if please.is_odoo_pkg():
            sts, branch = please.get_odoo_branch_from_git(try_by_fs=True)
            if sts == 0:
                odoo_major_version = int(branch.split(".")[0])
                # module_name = build_odoo_param("PKGNAME", odoo_vid=".", multi=True)
                repo_name = build_odoo_param("REPOS", odoo_vid=".", multi=True)
                if not pth.isdir("./static"):
                    os.mkdir("./static")
                if odoo_major_version <= 7:
                    if not pth.isdir("./static/src"):
                        os.mkdir("./static/src")
                    if not pth.isdir("./static/src/img"):
                        os.mkdir("./static/src/img")
                else:
                    if not pth.isdir("./static/description"):
                        os.mkdir("./static/description")
                if not pth.isdir("./readme"):
                    os.mkdir("./readme")
                    with open("./readme/CHANGELOG.rst", "w") as fd:
                        # Convetional date on Odoo Days (1st October Thursday)
                        fd.write(
                            "%s.0.1.0 %s\n" % (
                                branch,
                                {
                                    6: "2012-10-04",
                                    7: "2013-10-03",
                                    8: "2014-10-02",
                                    9: "2015-10-01",
                                    10: "2016-10-06",
                                    11: "2017-10-05",
                                    12: "2018-10-04",
                                    13: "2019-10-03",
                                    14: "2020-10-01",
                                    15: "2021-10-07",
                                    16: "2022-10-06",
                                    17: "2023-10-05",
                                }[odoo_major_version]
                            )
                        )
                        fd.write("~~~~~~~~~~~~~~~~~~~~~\n")
                        fd.write("\n")
                        fd.write("* Initial implementation\n")
                if please.opt_args.oca:
                    sts = please.run_traced(
                        "oca-gen-addon-readme --gen-html --branch=%s --repo-name=%s"
                        % (branch, repo_name),
                        rtime=True)
                else:
                    sts = please.chain_python_cmd("gen_readme.py", [])
                    if sts == 0:
                        sts = please.chain_python_cmd("gen_readme.py -H", [])
                    if sts == 0 and odoo_major_version <= 7:
                        sts = please.chain_python_cmd("gen_readme.py -RW", [])
                if sts == 0:
                    please.merge_test_result()
                    self.do_clean()
                return sts
        elif (
                please.is_repo_odoo()
                or please.is_repo_ocb()
                or please.is_pypi_pkg()
        ):
            please.sh_subcmd = please.pickle_params(
                rm_obj=True,
                slist=[("replace", "docs"),
                       ("commit", "docs"),
                       ("-F", ""),
                       ("--from-version", ""),
                       ("--no-verify", ""),
                       ("--vme", ""),
                       ("--odoo-venv", "")])
            cmd = please.build_sh_me_cmd(
                cmd=pth.join(pth.dirname(__file__), "please.sh")
            )
            sts = please.run_traced(cmd, rtime=True)
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
            return please.run_traced(cmd)
        return 1

    def do_publish(self):
        print("Missed specification:\nplease publish pypi|test_pypi")
        return 126

    def do_publish_pypi(self):
        please = self.please
        if please.is_pypi_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=pth.join(pth.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd, rtime=True)
        return 126

    def do_replace(self):
        please = self.please
        print("Deprecated action! Please use 'please commit'")
        sts = 126
        if please.is_pypi_pkg():
            sts = self.do_docs()
        if sts == 0:
            for root, dirs, files in os.walk(self.cur_path_of_pkg()):
                for fn in files:
                    if not fn.endswith(".bak") and not fn.endswith("~"):
                        continue
                    cmd = "rm -f " + pth.join(root, fn)
                    sts = please.run_traced(cmd)
                    if sts:
                        print("Cannot remove file %s!" % pth.join(root, fn))
                        break
        if sts == 0:
            if os.environ.get("HOME_DEVEL"):
                tgtdir = pth.join(
                    pth.dirname(os.environ["HOME_DEVEL"]), "tools"
                )
            elif pth.isdir("~/odoo/tools"):
                tgtdir = pth.expanduser("~/odoo/tools")
            else:
                tgtdir = pth.expanduser("~/tools")
            if not pth.isdir(tgtdir):
                print("Tools directory %s not found!" % tgtdir)
                return 2
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            if pkgname != "tools":
                sts = 0
                if not please.opt_args.no_verify:
                    sts = please.run_traced("git add ../", rtime=True)
                    if sts == 0:
                        sts = please.run_traced("pre-commit run", rtime=True)
                if sts == 0:
                    sts = please.run_traced(
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
                        sts = please.run_traced(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            else:
                if not please.opt_args.no_verify:
                    sts = please.run_traced("git add ./", rtime=True)
                if sts == 0:
                    for item in ("egg-info", "docs", "tests", "templates",
                                 "license_text"):
                        sts = please.run_traced(
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
                        "odoo_default_tnl.xlsx",
                        "odoo_template_tnl.xlsx",
                        "README.rst",
                    ):
                        fn = pth.join(srcdir, item)
                        if not pth.isfile(fn):
                            continue
                        sts = please.run_traced(
                            "cp %s %s" % (fn, pth.join(tgtdir, pkgname)), rtime=True
                        )
                        if sts:
                            break
            return sts
        return please.do_iter_action("do_replace", act_all_pypi=True, act_tools=False)

    def do_translate(self):
        please = self.please
        if please.is_odoo_pkg():
            please.sh_subcmd = please.pickle_params(rm_obj=True)
            cmd = please.build_sh_me_cmd(
                cmd=pth.join(pth.dirname(__file__), "please.sh")
            )
            return please.run_traced(cmd, rtime=True)
        return 1

    def do_update(self):
        please = self.please
        if please.is_pypi_pkg():
            if os.environ.get("HOME_DEVEL"):
                tgtdir = pth.join(os.environ["HOME_DEVEL"], "venv")
            else:
                tgtdir = pth.expanduser("~/devel/venv")
            if not pth.isdir(tgtdir):
                print("Tools directory %s not found!" % tgtdir)
                return 2
            srcdir = os.getcwd()
            pkgname = pth.basename(srcdir)
            if pkgname != "tools":
                fn = pth.join(pth.dirname(srcdir), "setup.py")
                if pth.isfile(fn):
                    sts = please.run_traced(
                        "cp %s %s" % (fn, pth.join(srcdir, "scripts", "setup.info")),
                        rtime=True
                    )
                if sts == 0:
                    sts = please.run_traced(
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
                        sts = please.run_traced(
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
                    sts = please.run_traced(
                        "vem %s update %s" % (tgtdir, pth.dirname(srcdir)),
                        rtime=True,
                    )
                    if sts:
                        break
        return sts

    def do_version(self):
        def update_version(fqn, regex, sep):
            target = ""
            do_rewrite = False
            # tag_found = False
            ext = fqn.rsplit(".", 1)
            ext = ext[1] if len(ext) > 1 else ""
            if ext in BIN_EXTS:
                return 0
            with open(fqn) as fd:
                try:
                    for ln in fd.read().split("\n"):
                        # x = regex.match(ln) if not tag_found else None
                        x = regex.match(ln)
                        if x:
                            # tag_found = True
                            if sep:
                                ver_text = ln[x.start(): x.end()].split(sep)[-1].strip()
                            else:
                                ver_text = ln[x.start(): x.end()].strip()
                            ver_text = re.sub(
                                r".*(\d+\.\d+\.\d+(\.\d+)?(\.\d+)?(\.\d+)?).*",
                                r"\1",
                                ver_text
                            )
                            if pth.basename(fqn) in ("setup.py",
                                                     "__manifest__.py",
                                                     "__openerp__.rst"):
                                self.ref_version = ver_text
                                print(fqn, "->", ver_text)
                            elif ver_text != self.ref_version:
                                print(fqn, "->", ver_text, "***")
                            elif please.opt_args.verbose > 1:
                                print(fqn)
                            if (
                                    please.opt_args.branch
                                    and ver_text != please.opt_args.branch
                            ):
                                # ln = ln.replace(ver_text, please.opt_args.branch)
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
                    print("Error %s reading %s" % (e, fqn))
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
                "^#? *(__version__|version|release) *= *[\"']?%s[\"']?"
                % please.opt_args.from_version)
            REGEX_DICT_VER = re.compile(
                "^ *[\"']version[\"']: [\"']%s[\"']"
                % please.opt_args.from_version)
            REGEX_TESTENV_VER = re.compile("^.* v%s" % please.opt_args.from_version)
        else:
            REGEX_VER = re.compile(
                "^#? *(__version__|version|release) *= *[\"']?[0-9.]+[\"']?")
            REGEX_DICT_VER = re.compile(
                "^ *[\"']version[\"']: [\"'][0-9.]+[\"']")
            REGEX_TESTENV_VER = re.compile(
                r"^.* v\d\.\d\.\d+")
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
                    if fn in ("testenv.py", "testenv.rst"):
                        rex = REGEX_TESTENV_VER
                        sep = "v"
                    elif fn in ("__manifest__.py", "__openerp__.rst"):
                        rex = REGEX_DICT_VER
                        sep = ":"
                    else:
                        rex = REGEX_VER
                        sep = "="
                    sts = update_version(pth.join(root, fn), rex, sep)
                    if sts:
                        break
            if sts == 0:
                sts = update_version(pth.join(os.getcwd(), "docs", "conf.py"),
                                     REGEX_VER,
                                     "=")
            return sts
        elif please.is_odoo_pkg():
            fqn = "__manifest__.py"
            if not pth.isfile(fqn):
                fqn = "__openerp__.py"
            if not pth.isfile(fqn):
                print("Manifest file not found!")
                return 3
            return update_version(fqn, REGEX_DICT_VER, ":")
        elif (please.opt_args.branch or please.opt_args.from_version):
            print("Version options are not applicable to all packages")
            return 126
        return please.do_iter_action("do_version", act_all_pypi=True, act_tools=False)
