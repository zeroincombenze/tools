#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-23 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
from __future__ import print_function, unicode_literals

from builtins import input
import argparse
import sys
import os
from time import sleep
import re
from z0lib import z0lib

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from wget_odoo_repositories import main as get_list_from_url
except ImportError:
    from wok_code.scripts.wget_odoo_repositories import main as get_list_from_url
try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param


__version__ = "2.0.12"

MANIFEST_FILES = ["__manifest__.py", "__odoo__.py", "__openerp__.py", "__terp__.py"]

ODOO_VALID_VERSIONS = (
    "16.0",
    "15.0",
    "14.0",
    "13.0",
    "12.0",
    "11.0",
    "10.0",
    "9.0",
    "8.0",
    "7.0",
    "6.1",
)

ODOO_VALID_GITORGS = ("oca", "librerp", "zero")

DEFAULT_DATA = {
    "librerp12": {
        "PATH": "~/12.0",
        "URL": "git@github.com:LibrERP-network",
        "CONFN": "odoo12.conf",
        "addons_kalamitica": "",
        "addons_nardo": "",
        "aeroo_reports": "",
        "connector-prestashop": "https://github.com/LibrERP",
        "custom-addons": "git@github.com:LibrERP",
        "deploy": "git@gitlab.com:powerp1",
        "double-trouble": "git@github.com:LibrERP",
        "fixed_modules": "",
        "generic": "",
        "profiles": "",
        "warehouse-logistics-stock": "git@gitlab.com:/powerp1",
        "zerobug-test": "git@github.com:zeroincombenze",
    },
    "librerp14": {
        "PATH": "~/14.0",
        "URL": "git@github.com:LibrERP-network",
        "CONFN": "odoo14.conf",
        "custom-addons": "git@github.com:LibrERP",
        "deploy": "git@gitlab.com:powerp1",
        "double-trouble": "git@github.com:LibrERP",
        "generic": "git@gitlab.com:powerp1",
        "profiles": "",
        "warehouse-logistics-stock": "git@gitlab.com:/powerp1",
        "zerobug-test": "git@github.com:zeroincombenze",
    },
    "librerp6": {
        "PATH": "~/librerp6",
        "URL": "https://github.com/iw3hxn",
        "CONFN": "odoo6-librerp.conf",
    },
    "oca14": {
        "zerobug-test": "",
    },
}
INVALID_NAMES = ["addons", "debian", "doc", "egg-info"]
SHORT_NAMES = {
    "zero": "zeroincombenze",
    "oca": "OCA",
}
REV_SHORT_NAMES = {
    "zeroincombenze": "zero",
    "OCA": "oca",
    "LibrERP-network": "librerp",
    "LibrERP": "librerp",
    "powerp1": "librerp",
    "iw3hxn": "librerp",
}
REPO_NAMES = {
    "zero": "zeroincombenze",
    "oca": "OCA",
    "librerp": "LibrERP-network",
}
FMT_PARAMS = {
    "repo": "%(repo)-30.30s",
    "sts": "%(sts)3.3s",
    "branch": "%(branch)-10.10s",
    "dif_branch": "%(branch)-10.10s",
    "git_org": "%(git_org)-14.14s",
    "git_url": "%(git_url)-64.64s",
    "path": "%(path)-56.56s",
    "stash": "%(stash)5.5s",
    "status": "%(status)s",
    "brief": "%(brief)s",
    "stage": "%(stage)-10.10s",
}


class OdooDeploy(object):
    """Odoo's organization/branch repositories
    self.repo_list is the repositories list of self.repo_info
    self.repo_info contains repository information
    * BRANCH: git branch
    * PATH: repository path
    * URL: git URL
    * GIT_ORG: git organization
    * STS: os status
    """

    def __init__(self, opt_args):
        self.opt_args = opt_args
        self.opt_args.git_orgs = self.opt_args.git_orgs or []
        self.addons_path = []
        self.master_branch = ""
        self.target_path = ""
        self.get_addons_from_config_file()

        if self.opt_args.action in ("clone", "reclone"):
            if not self.opt_args.odoo_branch:
                print("***** Missing Odoo branch: 12.0 will be used!")
                self.opt_args.odoo_branch = "12.0"
            if not self.opt_args.git_orgs:
                print("***** Missing git orgs: oca will be used!")
                self.opt_args.git_orgs = ["oca"]

        if self.opt_args.action == "clone":
            self.master_branch = build_odoo_param(
                "FULLVER", odoo_vid=opt_args.odoo_branch
            )

        if self.opt_args.action in ("clone", "reclone") and not self.opt_args.repos:
            # Get info from github about repositories of git organizations
            for git_org in opt_args.git_orgs:
                self.get_repo_from_github(git_org=git_org)
            if "OCB" not in self.repo_list:
                git_org = "odoo"
                self.get_repo_from_github(git_org=git_org, only_ocb=True)
            if opt_args.link_oca and "oca" not in self.opt_args.git_orgs:
                self.get_repo_from_github(git_org="oca")

        if self.opt_args.repos:
            if not self.opt_args.target_path:
                print("***** Missing target path (switch -p)!")
                self.target_path = build_odoo_param(
                    "ROOT", odoo_vid=self.master_branch,
                    git_org=opt_args.git_orgs[0], multi=self.opt_args.multi
                )
            self.get_repo_from_switch()

        if not self.repo_list and not self.opt_args.target_path:
            self.get_repo_from_config()

        if not self.repo_list:
            self.target_path = os.path.expanduser(self.opt_args.target_path)
            self.get_repo_from_path()

        if not self.repo_list:
            print("***** No repositories found!")

        for repo in self.repo_list:
            path = self.repo_info[repo]["PATH"]
            git_org = self.opt_args.git_orgs[0] if self.opt_args.git_orgs else "oca"
            if os.path.isdir(path):
                z0lib.run_traced("cd %s" % path, verbose=False, dry_run=False)
                sts, repo_branch, git_url, stash_list = self.get_remote_info(
                    verbose=False
                )
                if sts == 0:
                    org_url, rrepo, rgit_org = self.data_from_url(git_url)
                if self.opt_args.action == "clone":
                    self.repo_info[repo]["GIT_ORG"] = git_org
                    # self.repo_info[repo]["URL"] = git_url
                    self.repo_info[repo]["BRANCH"] = self.opt_args.odoo_branch
                else:
                    self.repo_info[repo]["GIT_ORG"] = rgit_org
                    self.repo_info[repo]["URL"] = git_url
                    self.repo_info[repo]["BRANCH"] = repo_branch
                self.repo_info[repo]["STS"] = sts
                if stash_list:
                    self.repo_info[repo]["STASH"] = stash_list
            if git_org and git_org not in self.opt_args.git_orgs:
                self.opt_args.git_orgs.append(git_org)
            if (
                    self.opt_args.action != "clone"
                    and rgit_org
                    and rgit_org not in self.opt_args.git_orgs
            ):
                self.opt_args.git_orgs.append(rgit_org)

            if repo == "OCB" and not self.master_branch:
                self.master_branch = build_odoo_param(
                    "FULLVER", odoo_vid=self.repo_info[repo]["BRANCH"]
                )
            if opt_args.action in ("list", "status", "unstaged"):
                self.add_addons_path(path, repo)

        self.git_org = opt_args.git_orgs[0] if opt_args.git_orgs else "oca"
        if self.repo_list:
            if "OCB" in self.repo_list and self.repo_list[0] != "OCB":
                del self.repo_list[self.repo_list.index("OCB")]
                self.repo_list.insert(0, "OCB")
            if self.repo_list[0] == "OCB":
                self.repo_list = ["OCB"] + sorted(self.repo_list[1:])
            else:
                self.repo_list = sorted(self.repo_list)

    def run_traced(self, cmd, verbose=None):
        verbose = verbose if isinstance(verbose, bool) else self.opt_args.verbose
        return z0lib.run_traced(
            cmd, verbose=verbose, dry_run=self.opt_args.dry_run, disable_alias=True
        )

    def is_module(self, path):
        if not os.path.isdir(path):
            return False
        files = os.listdir(path)
        filtered = [x for x in files if x in (MANIFEST_FILES + ["__init__.py"])]
        if len(filtered) == 2 and "__init__.py" in filtered:
            return os.path.join(path, next(x for x in filtered if x != "__init__.py"))
        else:
            return False

    def get_git_org_n_url(self, git_org):
        git_org = git_org or "oca"
        if git_org.startswith("https:") or git_org.startswith("http:"):
            git_url = git_org
            item = git_org.split(":", 1)[1]
            if item.endswith(".git"):
                git_org = os.path.basename(os.path.dirname(item))
            else:
                git_org = os.path.basename(item)
            if git_org == "OCA":
                git_org = "oca"
        else:
            if git_org == "zero":
                git_org = "zeroincombenze"
            elif git_org == "librerp" and self.opt_args.odoo_branch == "12.0":
                git_org = "LibrERP-network"
            elif git_org == "librerp" and self.opt_args.odoo_branch == "6.0":
                git_org = "iw3hxn"
            if self.opt_args.use_git:
                git_url = "git@github.com:%s" % git_org
            elif git_org == "oca":
                git_url = "https://github.com/%s" % git_org.upper()
            else:
                git_url = "https://github.com/%s" % git_org
        return git_url, git_org

    def get_repo_from_switch(self):
        self.repo_list = []
        self.repo_info = {}
        for repo in self.opt_args.repos.split(","):
            self.repo_info[repo] = {"PATH": self.get_path_of_repo(repo), "#": 1}
        self.repo_list = sorted(self.repo_info.keys())
        if "OCB" in self.repo_list and self.repo_list[0] != "OCB":
            del self.repo_list[self.repo_list.index("OCB")]
            self.repo_list = ["OCB"] + self.repo_list

    def get_repo_from_config(self):
        opt_args = self.opt_args
        self.master_branch = build_odoo_param("FULLVER", odoo_vid=opt_args.odoo_branch)
        if not opt_args.git_orgs:
            opt_args.git_orgs = [
                build_odoo_param(
                    "GIT_ORGID",
                    odoo_vid=opt_args.odoo_branch,
                    multi=self.opt_args.multi,
                )
            ]
        for git_org in opt_args.git_orgs:
            if git_org not in ODOO_VALID_GITORGS:
                print("Invalid git organization: %s" % git_org)
                exit(1)
        self.git_org = opt_args.git_orgs[0] if opt_args.git_orgs else "oca"
        self.target_path = build_odoo_param(
            "ROOT",
            odoo_vid=opt_args.odoo_branch,
            git_org=self.git_org,
            multi=self.opt_args.multi,
        )
        if re.match(os.environ.get("ODOO_GIT_ORGID", "oca"), git_org):
            config = os.path.join(
                "/etc/odoo",
                build_odoo_param(
                    "CONFN", odoo_vid=opt_args.odoo_branch, multi=self.opt_args.multi
                ),
            )
        else:
            config = os.path.join(
                "/etc/odoo",
                build_odoo_param(
                    "CONFN",
                    odoo_vid=opt_args.odoo_branch,
                    git_org=self.git_org,
                    multi=self.opt_args.multi,
                ),
            )
        if os.path.isfile(config):
            self.opt_args.config = config
            self.get_addons_from_config_file()

    def get_repo_from_path(self):
        def analyze_path(path, dir):
            if self.path_is_ocb(path):
                self.repo_info["OCB"] = {"PATH": path, "#": 0}
            elif self.is_git_repo(path=path):
                self.repo_info[dir] = {"PATH": path, "#": 0}
                if os.path.islink(path):
                    self.repo_info[dir]["#"] = 1
            elif self.is_module(path):
                repo = os.path.basename(root)
                if repo == "addons":
                    repo = os.path.basename(os.path.dirname(root))
                    if repo in (
                        "odoo",
                        "openerp",
                        os.path.basename(self.repo_info.get("OCB", {}).get("PATH", "")),
                    ):
                        repo = "OCB"
                if repo in self.repo_info:
                    self.repo_info[repo]["#"] += 1

        if self.target_path:
            # repo = "OCB"
            # if self.is_git_repo(path=self.target_path):
            #     self.repo_info[repo] = {"PATH": self.target_path, "#": 0}
            analyze_path(self.target_path, "OCB")
            for root, dirs, files in os.walk(
                self.target_path, topdown=True, followlinks=False
            ):
                links = [d for d in dirs if os.path.islink(os.path.join(root, d))]
                dirs[:] = [
                    d
                    for d in dirs
                    if (
                        not d.startswith(".")
                        and not d.startswith("_")
                        and not d.endswith("~")
                        and d
                        not in (
                            "build",
                            "debian",
                            "dist",
                            "doc",
                            "docs",
                            "egg-info",
                            "filestore",
                            "history",
                            "howtos",
                            "images" "migrations",
                            "redhat",
                            "reference",
                            "scripts",
                            "server",
                            "setup",
                            "static",
                            "tests",
                            "tmp",
                            "venv_odoo",
                            "win32",
                        )
                        and not os.path.islink(os.path.join(root, d))
                    )
                ]
                for dir in dirs + links:
                    path = os.path.join(root, dir)
                    analyze_path(path, dir)
            for repo in [x for x in self.repo_info.keys()]:
                if self.repo_info[repo]["#"] == 0:
                    del self.repo_info[repo]
            self.repo_list = sorted(self.repo_info.keys())
            if "OCB" in self.repo_list:
                del self.repo_list[self.repo_list.index("OCB")]
                self.repo_list = ["OCB"] + self.repo_list

    def get_repo_from_github(self, git_org=None, branch=None, only_ocb=None):
        git_org = git_org or self.git_org
        branch = branch or self.opt_args.odoo_branch
        if self.opt_args.target_path:
            self.target_path = os.path.expanduser(self.opt_args.target_path)
        else:
            self.target_path = build_odoo_param(
                "ROOT", odoo_vid=branch, git_org=git_org, multi=self.opt_args.multi
            )
        hash_key = git_org + branch.split(".")[0]
        opts = []
        if self.opt_args.verbose:
            opts.append("-v")
        if self.opt_args.dry_run:
            opts.append("-D")
        if branch:
            opts.append("-b")
            opts.append(branch)
        opts.append("-l")
        opts.append(self.opt_args.local_reps)
        # opts.append("l10n-italy,l10n-italy-supplemental")
        opts.append("-G")
        opts.append(SHORT_NAMES.get(git_org, git_org))
        if self.opt_args.extra_repo:
            opts.append("-x")
            opts.append(self.opt_args.extra_repo)
        opts.append("--return-repos")
        if only_ocb:
            content = ["OCB"]
        else:
            content = get_list_from_url(opts)
        for repo in content:
            if repo not in self.repo_list:
                url = DEFAULT_DATA.get(hash_key, {}).get(repo)
                if not url:
                    url = DEFAULT_DATA.get(hash_key, {}).get("URL")
                if not url:
                    if self.opt_args.use_git:
                        url = "git@github.com:%s" % REPO_NAMES.get(git_org, git_org)
                    else:
                        url = "https://github.com/%s" % REPO_NAMES.get(git_org, git_org)
                url = "%s/%s.git" % (url, repo)
                tgtdir = self.get_path_of_repo(repo)
                self.repo_list.append(repo)
                self.repo_info[repo] = {
                    "GIT_ORG": git_org,
                    "BRANCH": branch,
                    "URL": url,
                    "PATH": tgtdir,
                }

    def data_from_url(self, url):
        if "git@github.com:" in url:
            path = url.split(":")[1]
            uri = url.split("@")[1].split(":")[1]
        elif "@bzr." in url and ":" in url:
            path = url.split(":")[1]
            uri = url.split("@")[1].split(":")[0]
        elif "https:" in url:
            path = url.split(":")[1]
            uri = url.split(":")[1]
        else:
            path = uri = url
        repo = os.path.basename(path)
        if repo.endswith(".git"):
            repo = repo[:-4]
            url = os.path.dirname(url)
        if repo == "odoo":
            repo = "OCB"
        if uri.startswith("bzr"):
            git_org = os.path.splitext(uri[4:])[0]
        else:
            git_org = os.path.splitext(os.path.basename(os.path.dirname(uri)))[0]
        return url, repo, REV_SHORT_NAMES.get(git_org, git_org)

    def get_addons_from_config_file(self):
        def add_repo(repo, path):
            if repo not in self.repo_list:
                self.repo_list.append(repo)
            self.repo_info[repo] = {"PATH": path}
            if not path.startswith(HOME):
                print("Path %s or path outside user root!" % path)

        self.repo_list = []
        self.repo_info = {}
        if self.opt_args.config and os.path.isfile(self.opt_args.config):
            HOME = os.environ["HOME"]
            config = ConfigParser.ConfigParser()
            config.read(self.opt_args.config)
            for path in config.get("options", "addons_path").split(","):
                if self.is_git_repo(path=path):
                    repo = os.path.basename(path)
                    add_repo(repo, path)
                    continue
                if os.path.basename(path) == "addons" and os.path.isdir(
                    os.path.join(path, "..", ".git")
                ):
                    path = os.path.dirname(path)
                if not os.path.isdir(path):
                    print("Path %s does not exist!" % path)
                    continue
                if not self.is_git_repo(path=path):
                    continue
                add_repo("OCB", path)

    def find_data_dir(self, canonicalize=None):
        if self.master_branch and int(self.master_branch.split(".")[0]) < 8:
            return False
        tgtdir = os.path.join(os.environ["HOME"], ".local")
        if os.path.isdir(tgtdir):
            tgtdir = os.path.join(tgtdir, "share")
            if not os.path.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            odoo_master_branch = build_odoo_param(
                "FULLVER", odoo_vid=self.opt_args.odoo_branch
            )
            base = "Odoo%s" % odoo_master_branch.split(".")[0]
            tgtdir = os.path.join(tgtdir, base)
            if not os.path.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            for base in ("addons", "filestore", "sessions"):
                tgt = os.path.join(tgtdir, base)
                if not os.path.isdir(tgt) and canonicalize:
                    os.mkdir(tgt)
            tgtdir = os.path.join(tgtdir, "addons")
        return tgtdir

    def update_gitignore(self, repos):
        if repos:
            tgtdir = self.get_path_of_repo("OCB")
            content = ""
            gitignore_fn = os.path.join(tgtdir, ".gitignore")
            if os.path.isfile(gitignore_fn):
                with open(gitignore_fn, "r") as fd:
                    content = fd.read()
            updated = False
            for repo in repos:
                if repo == "OCB":
                    continue
                if ("\n%s\n" % repo) in content or ("\n/%s\n" % repo) in content:
                    continue
                content += "/%s\n" % repo
                updated = True
            if updated and not self.opt_args.dry_run:
                with open(gitignore_fn, "w") as fd:
                    fd.write(content)

    def update_conf(self, addons_path=None, git_org=None, branch=None):
        addons_path = addons_path or self.addons_path
        if addons_path:
            data_dir = self.find_data_dir(canonicalize=True)
            if os.path.isfile(self.opt_args.config):
                config = ConfigParser.ConfigParser()
                config.read(self.opt_args.config)
                config.set("options", "addons_path", ",".join(addons_path))
                if data_dir:
                    config.set("options", "data_dir", data_dir)
                if not self.opt_args.dry_run:
                    config.write(open(self.opt_args.config, "w+"))

    def is_git_repo(self, repo=None, path=None):
        res = bool(repo)
        if repo:
            res = False
            if repo.startswith(".") or repo.startswith("_") or repo in INVALID_NAMES:
                path = None
            elif not path:
                path = self.get_path_of_repo(repo)
        if path:
            path = os.path.join(path, repo) if repo else path
            if os.path.isdir(os.path.join(path, ".git")) or (
                not res and repo and self.repo_is_ocb(repo) and self.path_is_ocb(path)
            ):
                res = path
        return res

    def get_alt_gitorg(self, git_org=None):
        git_org = git_org or self.git_org
        return {
            "odoo": "oca",
            "librerp": "zero",
            "zero": "oca",
        }.get(git_org)

    def repo_is_ocb(self, repo):
        return repo in ("OCB", "odoo")

    def path_is_ocb(self, path):
        if (
            os.path.isdir(os.path.join(path, ".git"))
            and os.path.isdir(os.path.join(path, "addons"))
            and (
                (
                    os.path.isfile(os.path.join(path, "odoo-bin"))
                    and os.path.isdir(os.path.join(path, "odoo"))
                )
                or (
                    os.path.isfile(os.path.join(path, "openerp-server"))
                    and os.path.isdir(os.path.join(path, "openerp"))
                )
            )
        ):
            return True
        return False

    def get_path_of_repo(self, repo):
        tgtdir = self.repo_info.get(repo, {}).get("PATH")
        if not tgtdir:
            if self.repo_is_ocb(repo):
                tgtdir = self.target_path
            else:
                tgtdir = os.path.join(
                    self.target_path or self.opt_args.target_path, repo
                )
        return tgtdir

    def get_remote_info(self, verbose=True):
        verbose = verbose and self.opt_args.verbose
        branch = self.master_branch
        stash_list = ""
        url = ""
        sts, stdout, stderr = z0lib.run_traced("git branch", verbose=verbose)
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                if ln.startswith("*"):
                    branch = ln[2:]
                    break
        sts, stdout, stderr = z0lib.run_traced("git remote -v", verbose=verbose)
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                if not ln:
                    continue
                lns = ln.split()
                if lns[0] == "origin":
                    url = lns[1]
                    break
            sts, stdout, stderr = z0lib.run_traced("git stash list", verbose=False)
            stash_list = stdout
        else:
            if self.path_is_ocb(os.getcwd()):
                url = "https://github.com/odoo/odoo.git"
            else:
                url = "https://github.com/OCA/%s.git" % os.path.basename(os.getcwd())
        return sts, branch, url, stash_list

    def get_root_from_addons(self, repos, git_org=None, branch=None):
        git_org = git_org or self.git_org
        branch = branch or self.opt_args.odoo_branch
        hash_key = git_org + branch.split(".")[0]
        dirnames = {}
        HOME = os.environ["HOME"]
        with open("/etc/odoo/%s" % self.DATA[hash_key]["CONFN"], "r") as fd:
            content = fd.read()
        for ln in content.split("\n"):
            if ln.startswith("addons_path"):
                value = ln.split("=")[1].strip()
                for path in value.split(","):
                    if not path.startswith(HOME):
                        print("Path %s outside user root!" % path)
                        continue
                    repo = os.path.basename(path)
                    if not self.is_git_repo(repo):
                        repos.append(repo)
                        dname = os.path.dirname(path)
                        if dname not in dirnames:
                            dirnames[dname] = 0
                        dirnames[dname] += 2 if repo == "addons" else 1
                break
        root = False
        ctr = 0
        for dname in dirnames.keys():
            if dirnames[dname] > ctr:
                root = dname
                ctr = dirnames[dname]
        return root, repos

    def get_alt_branches(self, branch, master_branch=None):
        alts = []
        if branch.endswith("-devel"):
            alts.append(branch.replace("-devel", "_devel"))
        elif branch.endswith("_devel"):
            alts.append(branch.replace("_devel", "-devel"))
        if branch.endswith("devel"):
            alts.append(branch[:-6])
        if master_branch and master_branch not in alts:
            alts.append(master_branch)
        return alts

    def add_addons_path(self, tgtdir, repo):
        if self.repo_is_ocb(repo):
            path = ""
            for base in ("odoo", "openerp"):
                if os.path.isdir(os.path.join(tgtdir, base)):
                    path = os.path.join(tgtdir, base, "addons")
                    break
            if path:
                self.addons_path.append(path)
            self.addons_path.append(os.path.join(tgtdir, "addons"))
            data_dir = self.find_data_dir()
            if data_dir:
                self.addons_path.append(data_dir)
        else:
            self.addons_path.append(tgtdir)

    def git_clone(
        self,
        git_url,
        tgtdir,
        branch,
        master_branch=None,
        compact=None,
        link_oca=None,
    ):
        root = os.path.dirname(tgtdir)
        base = os.path.basename(tgtdir)
        try:
            if os.getcwd() != root:
                self.run_traced("cd %s" % root)
        except FileNotFoundError:  # noqa: F821
            self.run_traced("cd %s" % root)
        remote_branch = branch
        alt_branches = self.get_alt_branches(branch, master_branch=master_branch)
        for alt_branch in [branch] + alt_branches:
            if git_url.startswith("git"):
                opts = "-b %s" % alt_branch
            elif compact:
                opts = "-b %s --depth=1 --single-branch" % alt_branch
            else:
                opts = "-b %s --depth=1 --no-single-branch" % alt_branch
            if opts:
                cmd = "git clone %s %s/ %s" % (git_url, base, opts)
            else:
                cmd = "git clone %s %s/" % (git_url, base)
            sts, stdout, stderr = self.run_traced(cmd)
            if sts == 0 or self.opt_args.dry_run and "devel" in branch:
                remote_branch = alt_branch
                break
        if sts and link_oca and self.opt_args.link_oca:
            git_org = "oca"
            srcdir = build_odoo_param(
                "ROOT", odoo_vid=branch, multi=self.opt_args.multi, git_org=git_org
            )
            if os.path.isdir(srcdir):
                sts, stdout, stderr = self.run_traced("ln -s %s %s" % (srcdir, tgtdir))
                remote_branch = branch
        if sts:
            print("Invalid branch %s" % branch)
        return sts, remote_branch

    def git_pull(self, tgtdir, branch, master_branch=None):
        if os.getcwd() != tgtdir:
            self.run_traced("cd %s" % tgtdir)
        if os.path.islink(tgtdir):
            sts, repo_branch, git_url, stash_list = self.get_remote_info()
            return sts, repo_branch
        cmd = "git stash"
        self.run_traced(cmd, verbose=False)
        sleep(1)
        sts, repo_branch, git_url, stash_list = self.get_remote_info()
        alt_branches = self.get_alt_branches(branch, master_branch=master_branch)
        if repo_branch != branch and repo_branch not in alt_branches:
            for alt_branch in [branch] + alt_branches:
                cmd = "git checkout %s" % alt_branch
                sts, stdout, stderr = self.run_traced(cmd)
                if sts == 0:
                    # remote_branch = alt_branch
                    break
                sleep(1)
        if sts:
            print("Invalid branch %s" % branch)
        sleep(1)
        cmd = "git pull"
        return self.run_traced(cmd)[0], repo_branch

    def git_push(self, repo, tgtdir):
        if os.getcwd() != tgtdir:
            self.run_traced("cd %s" % tgtdir)
        sts, repo_branch, git_url, stash_list = self.get_remote_info()
        if os.path.islink(tgtdir):
            return sts, repo_branch
        cmd = "git push"
        sts, stdout, stderr = self.run_traced(cmd, verbose=False)
        if sts:
            sts, stdout, stderr = z0lib.run_traced(
                "git branch -r", verbose=self.opt_args.verbose
            )
            tag = "origin/%s" % repo_branch
            for ln in stdout.split("\n"):
                if tag in ln:
                    if not self.opt_args.assume_yes:
                        print("Remove remote branch %s of %s!" % (repo_branch, repo))
                        if self.opt_args.dry_run:
                            print("Delete (y/n)? ")
                            dummy = "n"
                        else:
                            dummy = input("Delete (y/n)? ")
                    if self.opt_args.assume_yes or dummy.lower().startswith("y"):
                        self.run_traced(
                            "git push origin -d %s" % repo_branch,
                            verbose=self.opt_args.verbose,
                        )
                    self.run_traced(
                        "git commit --no-verify -m \"[NEW] Initial setup %s\""
                        % repo_branch,
                        verbose=self.opt_args.verbose,
                    )
                    break
            cmd = "git push --set-upstream origin %s" % repo_branch
            sts, stdout, stderr = self.run_traced(cmd, verbose=self.opt_args.verbose)
        sleep(1)
        if sts == 0:
            sts, repo_branch, git_url, stash_list = self.get_remote_info()
        if sts:
            print("***ERROR\n%s\n%s" % (stdout, stderr))
        return sts, repo_branch

    def download_single_repo(self, repo, git_org=None, branch=None):
        git_org = git_org or self.git_org
        branch = branch or self.opt_args.odoo_branch
        odoo_master_branch = build_odoo_param("FULLVER", odoo_vid=branch)
        git_url = stash_list = ""
        tgtdir = self.get_path_of_repo(repo)
        if self.opt_args.action in ("update", "git-push"):
            if not os.path.isdir(tgtdir):
                return 127
            if os.getcwd() != tgtdir:
                self.run_traced("cd %s" % tgtdir)
            sts, repo_branch, git_url, stash_list = self.get_remote_info()
            if sts == 0:
                org_url, repo, repo_org = self.data_from_url(git_url)
        elif self.repo_is_ocb(repo) and not self.opt_args.keep_root_owner:
            git_url = "https://github.com/odoo/odoo.git"
            # repo = "odoo"
        elif repo in self.repo_list:
            repo_branch = self.repo_info[repo].get("BRANCH", branch)
            if repo_branch == "12.0" and git_org == "librerp" and repo == "OCB":
                git_url = DEFAULT_DATA["librerp12"]["URL"] + "/odoo.git"
            else:
                git_url = self.repo_info[repo].get("URL")
                if not git_url:
                    git_url, git_org = self.get_git_org_n_url(git_org)
                    git_url = git_url + "/" + repo + ".git"
        if not git_url:
            return 127
        bakdir = ""
        if os.path.isdir(tgtdir) and self.opt_args.action not in ("update", "git-push"):
            if self.opt_args.skip_if_exist:
                return self.git_pull(tgtdir, branch, master_branch=odoo_master_branch)
            elif not self.opt_args.assume_yes:
                print("Path %s of repo %s already exists!" % (tgtdir, repo))
                if self.opt_args.dry_run:
                    print("Delete (y/n)? ")
                    dummy = "y"
                else:
                    dummy = input("Delete (y/n)? ")
                if not dummy.lower().startswith("y"):
                    return 3
            if self.repo_is_ocb(repo):
                bakdir = "%s~" % tgtdir
                if os.path.isdir(bakdir):
                    if os.getcwd() != bakdir:
                        self.run_traced("cd %s" % os.path.dirname(bakdir))
                    cmd = "rm -fR %s" % bakdir
                    self.run_traced(cmd)
                cmd = "mv %s %s" % (tgtdir, bakdir)
                self.run_traced(cmd)
            elif not os.path.islink(tgtdir):
                if os.getcwd() != tgtdir:
                    self.run_traced("cd %s" % os.path.dirname(tgtdir))
                cmd = "rm -fR %s" % tgtdir
                self.run_traced(cmd)
        if os.path.isdir(tgtdir) and self.opt_args.action == "update":
            sts, remote_branch = self.git_pull(
                tgtdir, branch, master_branch=odoo_master_branch
            )
        elif os.path.isdir(tgtdir) and self.opt_args.action == "git-push":
            sts, remote_branch = self.git_push(repo, tgtdir)
        else:
            sts, remote_branch = self.git_clone(
                git_url,
                tgtdir,
                branch,
                master_branch=odoo_master_branch,
                compact=True if git_org in ("odoo", "oca") else False,
            )
        if sts == 0 and not os.path.isdir(tgtdir) and not self.opt_args.dry_run:
            sts = 1
        if repo not in self.repo_list:
            self.repo_list.append(repo)
        self.repo_info[repo]["STS"] = sts
        self.repo_info[repo]["PATH"] = tgtdir
        self.repo_info[repo]["GIT_ORG"] = git_org
        self.repo_info[repo]["URL"] = git_url
        self.repo_info[repo]["BRANCH"] = remote_branch
        if stash_list:
            self.repo_info[repo]["STASH"] = stash_list
        if os.path.isdir(tgtdir) or self.opt_args.dry_run:
            cmd = "cd %s" % tgtdir
            self.run_traced(cmd)
        if os.path.isdir(tgtdir):
            if self.repo_is_ocb(repo) and bakdir and os.path.isdir(bakdir):
                for fn in os.listdir(bakdir):
                    if fn.startswith(".") or fn.startswith("_"):
                        continue
                    path = os.path.join(bakdir, fn)
                    tgtfn = os.path.join(tgtdir, fn)
                    if os.path.exists(tgtfn):
                        continue
                    if os.path.isdir(path):
                        cmd = "mv %s/ %s/" % (path, tgtfn)
                        self.run_traced(cmd)
                    else:
                        cmd = "mv %s %s" % (path, tgtfn)
                        self.run_traced(cmd)
        if os.path.isdir(tgtdir) or repo == "OCB" or self.opt_args.dry_run:
            self.add_addons_path(tgtdir, repo)
        if sts:
            print("*** Error ***")
            if not self.opt_args.verbose:
                dummy = input("Press RET to continue ...")
        return sts

    def action_list(self):
        print("Odoo main version..........: %s" % self.master_branch)
        if self.opt_args.config:
            print("Odoo configuration file....: %s" % self.opt_args.config)
        fmt_list = self.opt_args.format.split(",")
        fmt = ""
        datas = {}
        for item in fmt_list:
            fmt += " " + FMT_PARAMS[item]
            datas[item] = item.upper()
        fmt = fmt.strip()
        print(fmt % datas)
        for repo in self.repo_list:
            datas = {
                "repo": repo,
                "sts": self.repo_info[repo].get("STS"),
                "branch": self.repo_info[repo].get("BRANCH"),
                "dif_branch": self.repo_info[repo].get("BRANCH")
                if self.repo_info[repo].get("BRANCH") != self.master_branch
                else "",
                "git_org": self.repo_info[repo].get("GIT_ORG"),
                "git_url": self.repo_info[repo].get("URL"),
                "path": self.repo_info[repo].get("PATH"),
                "stash": "stash" if self.repo_info[repo].get("STASH") else "",
            }
            print(fmt % datas)
        if self.opt_args.show_addons:
            print()
            print(",".join(self.addons_path))

    def action_status(self):
        print("Odoo main version..........: %s" % self.master_branch)
        if self.opt_args.config:
            print("Odoo configuration file....: %s" % self.opt_args.config)
        fmt_list = self.opt_args.format.split(",")
        fmt = ""
        datas = {}
        for item in fmt_list:
            fmt += " " + FMT_PARAMS[item]
            datas[item] = item.upper()
        fmt = fmt.strip()
        print(fmt % datas)
        for repo in self.repo_list:
            git_org = git_stat = brief = ""
            stage = "staged"
            tgtdir = self.get_path_of_repo(repo)
            self.run_traced("cd %s" % tgtdir, verbose=False)
            sts, repo_branch, git_url, stash_list = self.get_remote_info(verbose=False)
            if sts == 0:
                org_url, repo, git_org = self.data_from_url(git_url)
                sts, stdout, stderr = self.run_traced("git status", verbose=False)
                if sts == 0:
                    git_stat = stdout
                    for ln in stdout.split("\n"):
                        if (
                            ln.strip()
                            and "Your branch is up to date" not in ln
                            and "working tree clean" not in ln
                        ):
                            brief += ln + "\n"
                            if "On branch" not in ln:
                                stage = "unstaged"

            datas = {
                "repo": repo,
                "sts": sts,
                "branch": repo_branch,
                "dif_branch": repo_branch if repo_branch != self.master_branch else "",
                "git_org": git_org,
                "git_url": git_url,
                "path": tgtdir,
                "stash": "stash" if self.repo_info.get(repo, {}).get("STASH") else "",
                "status": git_stat,
                "brief": brief,
                "stage": stage,
            }
            if self.opt_args.action != "unstaged" or stage == "unstaged":
                print(fmt % datas)
        if self.opt_args.show_addons:
            print()
            print(",".join(self.addons_path))

    def action_download_or_pull_repo(self):
        print("Odoo main version..........: %s" % self.master_branch)
        if self.opt_args.config:
            print("Odoo configuration file....: %s" % self.opt_args.config)
        for repo in self.repo_list:
            self.download_single_repo(repo)
        if self.opt_args.verbose and self.addons_path:
            print("addons_path = %s" % ",".join(self.addons_path))
        if self.opt_args.update_addons_conf:
            self.update_conf()
        if self.opt_args.verbose:
            self.action_status()


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Manage Odoo repositories", epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument(
        "-A",
        "--update-addons-conf",
        action="store_true",
        help="Update addons_path in Odoo configuration file",
    )
    parser.add_argument(
        "-a",
        "--show-addons",
        action="store_true",
        help="Show addons_path after action",
    )
    parser.add_argument(
        "-b",
        "--odoo-branch",
        dest="odoo_branch",
        default="12.0",
        help="Default Odoo version",
    )
    parser.add_argument("-c", "--config", help="Odoo configuration file")
    parser.add_argument("-D", "--default-gitorg", default="zero")
    # parser.add_argument("-d", "--deployment-mode", help="may be tree,server,odoo")
    parser.add_argument(
        "-e",
        "--skip-if-exist",
        action="store_true",
        help="Use this switch to add missed repositories when you reclone",
    )
    parser.add_argument(
        "-F",
        "--format",
        help=(
            "Use 1 or + of "
            "sts,repo,branch,brief,git_org,git_url,path,stash,stage,status"
        ),
        default="repo,stage,branch,git_org,git_url,stash",
    )
    parser.add_argument(
        "-G",
        "--git-orgs",
        help="Git organizations, comma separated - " "May be: oca librerp or zero",
    )
    parser.add_argument(
        "-g",
        "--use-git",
        action="store_true",
        help="When clone use git protocol instead of https",
    )
    parser.add_argument(
        "-K",
        "--keep-root-owner",
        action="store_true",
        help="Keep OCB/odoo organization owner",
    )
    parser.add_argument(
        "-L", "--list", action="store_true", help="Deprecated: use 'list' action!"
    )
    parser.add_argument(
        "-l",
        "--local-reps",
        default="l10n-italy,l10n-italy-supplemental",
        help="Local repositories to load; default: l10n-italy,l10n-italy-supplemental",
    )
    parser.add_argument(
        "-m", "--multi", action="store_true", help="Multi version environment"
    )
    parser.add_argument(
        "-N",
        "--clone",
        action="store_true",
        help="Deprecated: use 'clone' action!",
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-o", "--origin", help="Declare origin repo for 'merge' action")
    parser.add_argument(
        "-O", "--link-oca", action="store_true", help="Link to more OCA repositories"
    )
    parser.add_argument("-p", "--target-path", help="Local directory")
    parser.add_argument(
        "-R", "--reclone", action="store_true", help="Deprecated: use 'reclone' action!"
    )
    parser.add_argument(
        "-r", "--repos", help="Declare specific repositories to manage, comma separated"
    )
    parser.add_argument(
        "-S", "--status", action="store_true", help="Deprecated: use 'status' action!"
    )
    parser.add_argument(
        "-U",
        "--only-update",
        action="store_true",
        help="Deprecated: use 'update' action!",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-x",
        "--extra-repo",
        help="May be: all,none,connector,devel,maintainer,oca,odoo,vertical",
    )
    parser.add_argument("-y", "--assume-yes", action="store_true")
    parser.add_argument(
        "action",
        nargs="?",
        help="May be clone,git-push,list,reclone,status,unstaged,update",
    )
    opt_args = parser.parse_args(cli_args)

    if not opt_args.action:
        if opt_args.clone:
            opt_args.action = "clone"
        elif opt_args.list:
            opt_args.action = "list"
        elif opt_args.reclone:
            opt_args.action = "reclone"
        elif opt_args.status:
            opt_args.action = "status"
        elif opt_args.only_update:
            opt_args.action = "update"
    opt_args.git_orgs = opt_args.git_orgs.split(",") if opt_args.git_orgs else []

    if opt_args.action not in (
        "clone",
        "git-push",
        "list",
        "reclone",
        "status",
        "update",
        "unstaged",
    ):
        print("No valid action issued!")
        exit(1)

    if opt_args.repos and not opt_args.target_path:
        print("No path issued for declared repositories")
        exit(1)

    deploy = OdooDeploy(opt_args)
    if opt_args.action == "list":
        deploy.action_list()
    elif opt_args.action in ("status", "unstaged"):
        deploy.action_status()
    else:
        deploy.action_download_or_pull_repo()
    return 0


if __name__ == "__main__":
    exit(main())

