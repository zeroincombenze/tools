#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-25 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
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
import os.path as pth
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


__version__ = "2.0.22"

MANIFEST_FILES = ["__manifest__.py", "__odoo__.py", "__openerp__.py", "__terp__.py"]

ODOO_VALID_VERSIONS = (
    "18.0",
    "17.0",
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

XTRA_PREFIX = [
    "connector",
    "edi",
    "hr",
    "l10n",
    "maintainer",
    "manufacture",
    "mis-builder",
    "oca",
    "odoo",
    "project",
    "vertical",
    "website",
]

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
    "librerp6": {
        "PATH": "~/librerp6",
        "URL": "https://github.com/iw3hxn",
        "CONFN": "odoo6-librerp.conf",
    },
    "oca14": {
        "zerobug-test": "",
    },
}
INVALID_NAMES = [
    "build",
    "debian",
    "dist",
    "doc",
    "docs",
    "egg-info",
    "filestore",
    "history",
    "howtos",
    "images",
    "migrations",
    "readme",
    "redhat",
    "reference",
    "scripts",
    "server",
    "setup",
    "static",
    "tests",
    "tmp",
    "tools",
    "venv_odoo",
    "win32",
]
SHORT_NAMES = {
    "zero": "zeroincombenze",
    "oca": "OCA",
}
REV_SHORT_NAMES = {
    "zeroincombenze": "zero",
    "OCA": "oca",
    "LibrERP-network": "librerp",
    "LibrERP": "librerp",
    "iw3hxn": "librerp",
}
REPO_NAMES = {
    "zero": "zeroincombenze",
    "oca": "OCA",
    "librerp": "LibrERP-network",
}
FMT_PARAMS = {
    "branch": "%(branch)-10.10s",
    "brief": "%(brief)s",
    "dif_branch": "%(dif_branch)-10.10s",
    "git_org": "%(git_org)-14.14s",
    "git_url": "%(git_url)-64.64s",
    "last_date": "%(last_date)-12.12s",
    "path": "%(path)-56.56s",
    "repo": "%(repo)-30.30s",
    "stash": "%(stash)5.5s",
    "stash_info": "%(stash_info)s",
    "stage": "%(stage)-10.10s",
    "status": "%(status)s",
    "sts": "%(sts)3.3s",
    "upstream": "%(upstream)-54.54s",
}


class OdooDeploy(object):
    """Odoo's organization/branch repositories
    self.repo_list is the repositories list of self.repo_info
    self.repo_info contains repository information
    * #: number of modules in repo
    * BRANCH: git branch
    * BRIEF: last commit message
    * GIT_ORG: git organization
    * LAST_DATE: last commit date
    * PATH: repository path
    * STAGE: staged or unstaged
    * STASH: repo with stash
    * STATUS: git status
    * STS: os status
    * UPSTREAM: upstream url
    * URL: git URL
    """

    def run_traced(self, cmd, verbose=None):
        verbose = verbose if isinstance(verbose, bool) else self.opt_args.verbose
        if self.opt_args.test and cmd.startswith("git "):
            if cmd == "git remote -v":
                tpath = pth.join(os.getcwd(), ".git", "git_remote~")
                if pth.isfile(tpath):
                    with open(tpath, "r") as fd:
                        stdout = fd.read()
                    return 0, stdout, ""
            elif cmd == "git branch":
                tpath = pth.join(os.getcwd(), ".git", "git_branch~")
                if pth.isfile(tpath):
                    with open(tpath, "r") as fd:
                        stdout = fd.read()
                    return 0, stdout, ""
        elif cmd in ("git remote -v", "git branch") and pth.isdir(".git"):
            return z0lib.run_traced(
                cmd, verbose=verbose, dry_run=False, disable_alias=True
            )
        return z0lib.run_traced(
            cmd, verbose=verbose, dry_run=self.opt_args.dry_run, disable_alias=True
        )

    def test_sim_git_clone(self, git_url, repo, branch, tgtdir):
        os.mkdir(tgtdir)
        tpath = pth.join(tgtdir, ".git")
        os.mkdir(tpath)
        if repo == "OCB":
            tpath = pth.join(tgtdir, "odoo")
            os.mkdir(tpath)
            tpath = pth.join(tgtdir, "addons")
            os.mkdir(tpath)
            tpath = pth.join(tgtdir, "odoo-bin")
            with open(tpath, "w") as fd:
                fd.write("")
        tpath = pth.join(tgtdir, ".git", "git_branch~")
        with open(tpath, "w") as fd:
            fd.write("* %s\n" % (branch or self.opt_args.odoo_branch))
        tpath = pth.join(tgtdir, ".git", "git_remote~")
        with open(tpath, "w") as fd:
            fd.write("origin %s\n" % git_url)

    def __init__(self, opt_args):
        opt_args.git_orgs = opt_args.git_orgs.split(",") if opt_args.git_orgs else []
        opt_args.link_upstream = (
            opt_args.link_upstream.split(",") if opt_args.link_upstream else []
        )
        opt_args.repos = opt_args.repos.split(",") if opt_args.repos else []
        opt_args.exclude_path = (
            opt_args.exclude_path.split(",") if opt_args.exclude_path else []
        )
        if opt_args.origin:
            opt_args.origin = pth.abspath(pth.expanduser(opt_args.origin))
        if opt_args.target_path:
            opt_args.target_path = pth.abspath(pth.expanduser(opt_args.target_path))
        if opt_args.test:
            opt_args.dry_run = True
        if opt_args.action not in (
            "amend",
            "clone",
            "git-push",
            "list",
            "merge",
            "new-branch",
            "status",
            "update",
            "unstaged",
        ):
            raise NotImplementedError("No valid action issued!")
        if (
            not opt_args.repos
            and opt_args.action in ("git-push", "merge", "status", "update", "unstaged")
            and (not opt_args.target_path and not opt_args.config)
        ):
            opt_args.target_path = "./"
        if opt_args.repos and not opt_args.target_path:
            raise ReferenceError(
                "No path issued for declared repository %s!" % opt_args.repos
            )
        if opt_args.action in (
            "amend",
            "git-push",
            "merge",
            "status",
            "update",
            "unstaged",
        ) and (not opt_args.target_path and not opt_args.config):
            raise ReferenceError(
                "No path issued to execute action %s" % opt_args.action
            )
        if opt_args.action == "new-branch" and not opt_args.target_path:
            raise ReferenceError(
                "No path issued to execute action %s" % opt_args.action
            )
        if opt_args.action == "new-branch" and not opt_args.origin:
            raise ReferenceError("Missed origin to create new-branch %s!")
        if opt_args.update_addons_conf and (
            not opt_args.target_path or not opt_args.config
        ):
            raise ReferenceError(
                "Cannot update addons_path w/o config file or target path!"
            )
        if opt_args.link_upstream and not opt_args.origin:
            raise ReferenceError(
                "Missed origin for link path %s!" % opt_args.link_upstream
            )
        if opt_args.clean_repo and opt_args.action != "update":
            raise NotImplementedError("You can clean repo only under update action!")
        if opt_args.action in ("clone", "amend") and not opt_args.odoo_branch:
            print("***** Missing Odoo branch: 17.0 will be used!")
            opt_args.odoo_branch = "17.0"
        elif opt_args.action == "new-branch" and not opt_args.odoo_branch:
            print("***** Missing Odoo branch: 18.0 will be used!")
            opt_args.odoo_branch = "18.0"

        self.opt_args = opt_args
        self.addons_path = self.repo_list = []
        self.repo_info = {}
        self.master_branch = ""
        if self.opt_args.target_path:
            self.target_path = pth.abspath(pth.expanduser(self.opt_args.target_path))
        else:
            self.target_path = ""
        getattr(self, "_init_%s" % opt_args.action.replace("-", "_"))()

    def _init_amend(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.master_branch = build_odoo_param(
            "FULLVER", odoo_vid=self.opt_args.odoo_branch
        )
        if self.opt_args.repos:
            for repo in self.opt_args.repos:
                if repo not in self.repo_info:
                    self.set_default_repo_info(
                        repo, self.opt_args.git_orgs[0], self.opt_args.odoo_branch
                    )
            self.sort_repo_list()
        else:
            self.load_all_repos_from_github()
        if self.opt_args.clean_empty_repo:
            self.remove_empty_repos()

    def _init_clone(self):
        if not self.opt_args.git_orgs:
            print("***** Missing git orgs: oca will be used!")
            self.opt_args.git_orgs = ["oca"]
        self.master_branch = build_odoo_param(
            "FULLVER", odoo_vid=self.opt_args.odoo_branch
        )
        if self.opt_args.repos:
            for repo in self.opt_args.repos:
                if repo not in self.repo_info:
                    self.set_default_repo_info(
                        repo, self.opt_args.git_orgs[0], self.opt_args.odoo_branch
                    )
            self.sort_repo_list()
        else:
            self.load_all_repos_from_github()

    def _init_git_push(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.set_default_branch()

    def _init_merge(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.set_default_branch()

    def _init_status(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.set_default_branch()

    def _init_list(self):
        return self._init_status()

    def _init_unstaged(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.set_default_branch()

    def _init_update(self):
        self.get_addons_from_config_file()
        if not self.repo_list and self.target_path:
            self.get_repos_from_path()
        self.set_default_branch()
        if self.opt_args.link_upstream:
            self.repo_list += [
                x for x in self.opt_args.link_upstream if x not in self.repo_list
            ]
        if self.opt_args.clean_empty_repo:
            self.remove_empty_repos()

    def _init_new_branch(self):
        if not self.opt_args.git_orgs:
            print("***** Missing git orgs: oca will be used!")
            self.opt_args.git_orgs = ["oca"]
        self.master_branch = build_odoo_param(
            "FULLVER", odoo_vid=self.opt_args.odoo_branch
        )
        self.opt_args.keep_root_owner = True
        if not self.opt_args.from_odoo_version:
            x = re.search("[0-9]+", self.opt_args.odoo_branch)
            if not x:
                print("***** Missing from Odoo version!")
                self.opt_args.from_odoo_version = self.opt_args.odoo_branch
            self.opt_args.from_odoo_version = self.get_prior_odoo_version(
                self.opt_args.odoo_branch
            )

        if self.opt_args.repos:
            for repo in self.opt_args.repos:
                if repo not in self.repo_info:
                    self.set_default_repo_info(
                        repo,
                        self.opt_args.git_orgs[0],
                        self.opt_args.odoo_branch,
                        root_path=self.opt_args.origin,
                    )
            self.sort_repo_list()
        else:
            self.get_repos_from_path(root_path=self.opt_args.origin)

    def get_prior_odoo_version(self, odoo_branch):
        x = re.search("[0-9]+", odoo_branch)
        if not x:
            print("***** Missing from Odoo version!")
            from_odoo_version = odoo_branch
        else:
            from_odoo_version = re.sub(
                "[0-9]+",
                str(eval(odoo_branch[x.start(): x.end()]) - 1),
                odoo_branch,
                count=1,
            )
        return from_odoo_version

    def set_default_branch(self):
        if not self.repo_list:
            raise RuntimeError("***** No repositories found!")
        self.master_branch = build_odoo_param(
            "FULLVER", odoo_vid=self.repo_info["OCB"]["BRANCH"]
        )

    def load_all_repos_from_github(self):
        for git_org in self.opt_args.git_orgs:
            self.get_repo_from_github(git_org=git_org)
        if "OCB" not in self.repo_list:
            git_org = "odoo"
            self.get_repo_from_github(git_org=git_org, only_ocb=True)

    def remove_empty_repos(self):
        for repo in [x for x in self.repo_info.keys()]:
            if self.repo_info[repo]["#"] == 0:
                del self.repo_info[repo]

    def sort_repo_list(self):
        self.repo_list = list(self.repo_info.keys())
        if "OCB" in self.repo_list and self.repo_list[0] != "OCB":
            del self.repo_list[self.repo_list.index("OCB")]
            self.repo_list.insert(0, "OCB")
        if self.repo_list and self.repo_list[0] == "OCB":
            self.repo_list = ["OCB"] + sorted(self.repo_list[1:])
        else:
            self.repo_list = sorted(self.repo_list)
        self.addons_path = []
        for repo in self.repo_list:
            self.add_addons_path(self.repo_info[repo]["PATH"], repo)

    def is_module(self, path):
        if not pth.isdir(path):
            return False
        files = os.listdir(path)
        filtered = [x for x in files if x in (MANIFEST_FILES + ["__init__.py"])]
        if len(filtered) == 2 and "__init__.py" in filtered:
            return pth.join(path, next(x for x in filtered if x != "__init__.py"))
        else:
            return False

    def get_git_org_n_url(self, git_org):
        git_org = git_org or "oca"
        if git_org.startswith("https:") or git_org.startswith("http:"):
            git_url = git_org
            item = git_org.split(":", 1)[1]
            if item.endswith(".git"):
                git_org = pth.basename(pth.dirname(item))
            else:
                git_org = pth.basename(item)
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

    def set_default_repo_info(self, repo, git_org, branch, root_path=None):
        hash_key = git_org + branch.split(".")[0]
        url = DEFAULT_DATA.get(hash_key, {}).get(repo)
        if not url:
            url = DEFAULT_DATA.get(hash_key, {}).get("URL")
        if not url:
            if self.opt_args.use_git:
                url = "git@github.com:%s" % REPO_NAMES.get(git_org, git_org)
            else:
                url = "https://github.com/%s" % REPO_NAMES.get(git_org, git_org)
        if repo == "OCB" and git_org == "odoo":
            url = "%s/%s.git" % (url, "odoo")
        else:
            url = "%s/%s.git" % (url, repo)
        tgtdir = self.get_path_of_repo(repo, root_path=root_path)
        self.repo_info[repo] = {
            "PATH": tgtdir,
            "GIT_ORG": REV_SHORT_NAMES.get(git_org, git_org),
            "URL": url,
            "BRANCH": branch,
            "LAST_DATE": "",
            "BRIEF": "",
            "STAGE": "",
            "STASH": "",
            "STATUS": "",
            "STS": 127,
        }

    def load_repo_info(self, path, repo):
        self.run_traced("cd %s" % path, verbose=False)
        (
            sts,
            repo_branch,
            git_url,
            stash_list,
            upstream,
            last_date,
            status,
            stage,
            brief,
        ) = self.get_remote_info(verbose=False)
        if sts == 0:
            org_url, rrepo, rgit_org = self.data_from_url(git_url)
        else:
            rgit_org = self.opt_args.git_orgs[0] if self.opt_args.git_orgs else "oca"
            repo_branch = self.opt_args.odoo_branch or build_odoo_param(
                "FULLVER", odoo_vid=path
            )
        if repo not in self.repo_info:
            self.repo_info[repo] = {"PATH": path}
        self.repo_info[repo]["GIT_ORG"] = REV_SHORT_NAMES.get(rgit_org, rgit_org)
        self.repo_info[repo]["URL"] = git_url
        self.repo_info[repo]["BRANCH"] = repo_branch
        self.repo_info[repo]["LAST_DATE"] = last_date
        self.repo_info[repo]["STATUS"] = status
        self.repo_info[repo]["STAGE"] = stage
        self.repo_info[repo]["STS"] = sts
        self.repo_info[repo]["STASH"] = stash_list
        self.repo_info[repo]["UPSTREAM"] = upstream
        self.repo_info[repo]["BRIEF"] = brief

    def analyze_path(self, path, repo):
        if repo == "OCB":
            while "OCB" not in self.repo_info and path != os.environ["HOME"]:
                if self.path_is_ocb(path):
                    self.repo_info[repo] = {"PATH": path, "#": 0}
                    self.load_repo_info(path, repo)
                    self.master_branch = build_odoo_param(
                        "FULLVER", odoo_vid=self.repo_info["OCB"]["BRANCH"]
                    )
                else:
                    path = pth.dirname(path)
            if "OCB" not in self.repo_info:
                print("***** Path %s is not OCB!" % path)
        else:
            while not self.is_git_repo(path=path) and path != os.environ["HOME"]:
                path = pth.dirname(path)
                repo = pth.basename(path)
            if self.path_is_ocb(path):
                # print("***** Path %s is OCB!" % path)
                pass
            elif self.is_git_repo(path=path):
                if repo not in self.repo_info:
                    self.repo_info[repo] = {"PATH": path, "#": 0}
                    if pth.islink(path):
                        self.repo_info[repo]["#"] = 1
                    self.load_repo_info(path, repo)
            else:
                print("***** Invalid path %s for repo %s!" % (path, repo))

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
                print("Invalid git organization: %s!" % git_org)
                exit(1)
        self.git_org = opt_args.git_orgs[0] if opt_args.git_orgs else "oca"
        self.target_path = build_odoo_param(
            "ROOT",
            odoo_vid=opt_args.odoo_branch,
            git_org=self.git_org,
            multi=self.opt_args.multi,
        )
        if re.match(os.environ.get("ODOO_GIT_ORGID", "oca"), git_org):
            config = pth.join(
                "/etc/odoo",
                build_odoo_param(
                    "CONFN", odoo_vid=opt_args.odoo_branch, multi=self.opt_args.multi
                ),
            )
        else:
            config = pth.join(
                "/etc/odoo",
                build_odoo_param(
                    "CONFN",
                    odoo_vid=opt_args.odoo_branch,
                    git_org=self.git_org,
                    multi=self.opt_args.multi,
                ),
            )
        if pth.isfile(config):
            self.opt_args.config = config
            self.get_addons_from_config_file()
        self.sort_repo_list()

    def get_repos_from_path(self, root_path=None):
        path = root_path or self.target_path
        if path and pth.isdir(path):
            self.analyze_path(path, "OCB")
            for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
                links = [d for d in dirs if pth.islink(pth.join(root, d))]
                dirs[:] = [
                    d
                    for d in dirs
                    if (
                        not d.startswith(".")
                        and not d.startswith("_")
                        and not d.endswith("~")
                        and d not in INVALID_NAMES
                        and not pth.islink(pth.join(root, d))
                    )
                ]
                for dir in dirs + links:
                    repo_path = pth.join(root, dir)
                    self.analyze_path(repo_path, dir)
        self.sort_repo_list()

    def repo_list_from_github(self, git_org=None, branch=None, only_ocb=None):
        git_org = git_org or self.git_org
        branch = branch or self.opt_args.odoo_branch
        opts = []
        if self.opt_args.verbose:
            opts.append("-v")
        if self.opt_args.dry_run:
            opts.append("-n")
        if self.opt_args.force:
            opts.append("-f")
        if branch:
            opts.append("-b")
            opts.append(branch)
        opts.append("-l")
        opts.append(self.opt_args.local_reps)
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
        return content

    def get_repo_from_github(self, git_org=None, branch=None, only_ocb=None):
        git_org = git_org or self.git_org
        branch = branch or self.opt_args.odoo_branch
        # hash_key = git_org + branch.split(".")[0]
        repo_list = self.repo_list_from_github(
            git_org=git_org, branch=branch, only_ocb=only_ocb
        )
        for repo in repo_list:
            if repo not in self.repo_info:
                self.set_default_repo_info(repo, git_org, branch)
        self.sort_repo_list()

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
        repo = pth.basename(path)
        if repo.endswith(".git"):
            repo = repo[:-4]
            url = pth.dirname(url)
        if repo == "odoo":
            repo = "OCB"
        if uri.startswith("bzr"):
            git_org = pth.splitext(uri[4:])[0]
        else:
            git_org = pth.splitext(pth.basename(pth.dirname(uri)))[0]
        return url, repo, REV_SHORT_NAMES.get(git_org, git_org)

    def get_addons_from_config_file(self):
        if (
            not self.opt_args.update_addons_conf
            and self.opt_args.config
            and pth.isfile(self.opt_args.config)
        ):
            config = ConfigParser.ConfigParser()
            config.read(self.opt_args.config)
            for path in config.get("options", "addons_path").split(","):
                if self.is_git_repo(path=path):
                    repo = pth.basename(path)
                    self.load_repo_info(path, repo)
                else:
                    self.analyze_path(path, "OCB")
            self.sort_repo_list()

    def find_data_dir(self, canonicalize=None, addons=None):
        if self.master_branch and int(self.master_branch.split(".")[0]) < 8:
            return False
        tgtdir = pth.join(os.environ["HOME"], ".local")
        if pth.isdir(tgtdir):
            tgtdir = pth.join(tgtdir, "share")
            if not pth.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            base = "Odoo%s" % self.master_branch.split(".")[0]
            tgtdir = pth.join(tgtdir, base)
            if not pth.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            for base in ("addons", "filestore", "sessions"):
                tgt = pth.join(tgtdir, base)
                if not pth.isdir(tgt) and canonicalize:
                    os.mkdir(tgt)
            if addons:
                tgtdir = pth.join(tgtdir, "addons")
        return tgtdir

    def update_gitignore(self, repos):
        if repos:
            tgtdir = self.get_path_of_repo("OCB")
            content = ""
            gitignore_fn = pth.join(tgtdir, ".gitignore")
            if pth.isfile(gitignore_fn):
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
            if pth.isfile(self.opt_args.config):
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
            if (
                repo.startswith(".")
                or repo.startswith("_")
                or repo in INVALID_NAMES + ["addons"]
            ):
                path = None
            elif not path:
                path = self.get_path_of_repo(repo)
        if path:
            path = pth.join(path, repo) if repo else path
            if pth.isdir(pth.join(path, ".git")) or (
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
            pth.isdir(pth.join(path, ".git"))
            and pth.isdir(pth.join(path, "addons"))
            and (
                (
                    pth.isfile(pth.join(path, "odoo-bin"))
                    and pth.isdir(pth.join(path, "odoo"))
                )
                or (
                    pth.isfile(pth.join(path, "openerp-server"))
                    and pth.isdir(pth.join(path, "openerp"))
                )
            )
        ):
            return True
        return False

    def get_path_of_repo(self, repo, root_path=None):
        tgtdir = self.repo_info.get(repo, {}).get("PATH")
        if root_path or not tgtdir:
            if self.repo_is_ocb(repo):
                tgtdir = root_path or self.target_path
            else:
                tgtdir = pth.join(root_path or self.target_path, repo)
        return tgtdir

    def get_remote_info(self, verbose=True, short=False, real_branch=False):
        verbose = verbose and self.opt_args.verbose
        branch = self.master_branch
        stash_list = url = upstream = last_date = git_stat = stage = brief = ""
        sts, stdout, stderr = self.run_traced("git branch", verbose=verbose)
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                if ln.startswith("*"):
                    branch = ln[2:]
                    if not real_branch and branch == "master":
                        branch = "18.0"
                    break
        if short:
            return sts, branch

        sts1, stdout, stderr = self.run_traced("git remote -v", verbose=verbose)
        if sts1 == 0 and stdout:
            for ln in stdout.split("\n"):
                if not ln:
                    continue
                lns = ln.split()
                if lns[0] == "origin":
                    url = lns[1]
                elif lns[0] == "upstream":
                    upstream = lns[1]
            sts1, stdout, stderr = self.run_traced("git stash list", verbose=verbose)
            stash_list = stdout
        else:
            sts = sts or sts1
            if self.path_is_ocb(os.getcwd()):
                url = "https://github.com/odoo/odoo.git"
            else:
                url = "https://github.com/OCA/%s.git" % pth.basename(os.getcwd())
        if sts == 0:
            sts1, stdout, stderr = self.run_traced(
                "git log --pretty=format:%cs%n%s -n 1", verbose=verbose
            )
            if sts1 == 0 and stdout:
                last_date, brief = stdout.split("\n")
        sts1, stdout, stderr = self.run_traced("git status", verbose=verbose)
        sts = sts or sts1
        if sts1 == 0:
            git_stat = stdout
            stage = (
                "staged"
                if (
                    "On branch" in stdout
                    and "Your branch is up to date" in stdout
                    and "working tree clean" in stdout
                )
                else "unstaged"
            )
        return sts, branch, url, stash_list, upstream, last_date, git_stat, stage, brief

    def set_upstream(self, origin_path, repo):
        if repo != "OCB":
            origin_path = pth.join(origin_path, repo)
        target_path = self.get_path_of_repo(repo, root_path=self.opt_args.target_path)
        if os.getcwd() != target_path:
            self.run_traced("cd %s" % target_path)
        if not pth.isfile(".gitignore"):
            self.run_traced("please defcon gitignore")
        if not pth.isfile(".pre-commit-config.yaml"):
            self.run_traced("please defcon precommit")
        if pth.isdir(origin_path):
            if os.getcwd() != origin_path:
                self.run_traced("cd %s" % origin_path)
            sts, stdout, stderr = self.run_traced("git remote -v")
            url_upstream = ""
            if sts == 0 and stdout:
                for ln in stdout.split("\n"):
                    lns = ln.split()
                    if len(lns) < 2:
                        continue
                    elif lns[0] == "origin":
                        url_upstream = lns[1]
                        break
            if url_upstream:
                if os.getcwd() != target_path:
                    self.run_traced("cd %s" % target_path)
                cur_upstream = ""
                for ln in stdout.split("\n"):
                    lns = ln.split()
                    if len(lns) < 2:
                        continue
                    elif lns[0] == "upstream":
                        cur_upstream = lns[1]
                        break
                if cur_upstream != url_upstream:
                    if cur_upstream:
                        self.run_traced("git remote remove upstream")
                    self.run_traced(
                        "git remote add upstream %s" % url_upstream,
                    )

    def ask_4_confirm(self, title, question):
        if not self.opt_args.assume_yes:
            if title:
                print(title)
            if self.opt_args.dry_run:
                print(question)
                x = "n"
            else:
                x = input(question)
        return True if self.opt_args.assume_yes or x.lower().startswith("y") else False

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
                        print("***** Path %s outside user root!" % path)
                        continue
                    repo = pth.basename(path)
                    if not self.is_git_repo(repo):
                        repos.append(repo)
                        dname = pth.dirname(path)
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
                if pth.isdir(pth.join(tgtdir, base)):
                    path = pth.join(tgtdir, base, "addons")
                    break
            if path:
                self.addons_path.append(path)
            self.addons_path.append(pth.join(tgtdir, "addons"))
            data_dir = self.find_data_dir(addons=True)
            if data_dir:
                self.addons_path.append(data_dir)
        else:
            self.addons_path.append(tgtdir)

    def git_clone(
        self,
        git_url,
        tgtdir,
        branch=None,
        master_branch=None,
        compact=None,
        repo=None,
    ):
        root = pth.dirname(tgtdir)
        base = pth.basename(tgtdir)
        try:
            if os.getcwd() != root:
                self.run_traced("cd %s" % root)
        except FileNotFoundError:  # noqa: F821
            # Please do not remove following code: here where current dir was removed
            self.run_traced("cd %s" % root)
        remote_branch = branch
        if branch:
            alt_branches = self.get_alt_branches(branch, master_branch=master_branch)
        else:
            alt_branches = []
        for alt_branch in [branch] + alt_branches:
            if not alt_branch:
                opts = ""
            elif git_url.startswith("git"):
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
            # Just for test
            if sts == 0 or self.opt_args.dry_run:
                if self.opt_args.test:
                    self.test_sim_git_clone(git_url, repo or base, alt_branch, tgtdir)
                if not branch or "devel" in branch:
                    remote_branch = alt_branch
                break
            if sts and self.opt_args.verbose:
                print(stdout + stderr)
        if sts and repo in self.opt_args.link_upstream:
            origin_path = pth.join(self.opt_args.origin, repo)
            if pth.isdir(origin_path):
                sts, stdout, stderr = self.run_traced(
                    "ln -s %s %s" % (origin_path, tgtdir)
                )
                remote_branch = branch
        if sts:
            print("Invalid branch %s" % branch)
        if sts == 0 and git_url.startswith("git") and self.opt_args.origin:
            rgit_org = False
            srcdir = self.get_path_of_repo(repo)
            if srcdir != tgtdir:
                curcwd = os.getcwd()
                os.chdir(srcdir)
                sts, repo_branch, rgit_url = self.get_remote_info(verbose=False)[0:3]
                if sts == 0:
                    rgit_org = self.data_from_url(rgit_url)[2]
                os.chdir(curcwd)
            self.repo_info[repo]["PATH"] = tgtdir
            self.repo_info[repo]["BRANCH"] = remote_branch
            git_org = self.data_from_url(git_url)[2]
            if git_org != rgit_org:
                self.set_upstream(self.opt_args.origin, repo)
        return sts, remote_branch

    def git_pull(self, repo, tgtdir=None, branch=None):
        tgtdir = self.get_path_of_repo(repo, root_path=tgtdir)
        repo_branch = self.repo_info[repo]["BRANCH"]
        branch = branch or self.opt_args.odoo_branch or repo_branch
        if os.getcwd() != tgtdir:
            self.run_traced("cd %s" % tgtdir)
        if pth.islink(tgtdir):
            return self.get_remote_info(short=True)
        cmd = "git stash"
        self.run_traced(cmd, verbose=False)
        sleep(1)
        alt_branches = self.get_alt_branches(branch, master_branch=self.master_branch)
        if repo_branch != branch and not self.opt_args.continue_after_error:
            if (
                repo_branch not in alt_branches
                and branch not in alt_branches
                and not self.opt_args.force
            ):
                if not self.ask_4_confirm(
                    "Current branch %s is different from required branch  %s!"
                    % (repo_branch, branch),
                    "Do checkout %s? " % branch,
                ):
                    return 1, repo_branch
            sts = self.git_checkout(repo, tgtdir, branch)
            if sts:
                return sts, repo_branch
        cmd = "git pull origin %s" % branch
        return self.run_traced(cmd)[0], repo_branch

    def git_push_new_branch(self, tgtdir):
        if pth.islink(tgtdir):
            return 1, self.opt_args.odoo_branch
        if os.getcwd() != tgtdir:
            self.run_traced("cd %s" % tgtdir)
        found = False
        sts, stdout, stderr = self.run_traced("git branch", verbose=False)
        if sts == 0 and stdout:
            regex = r"^[*]* +" + self.opt_args.odoo_branch + r" *$"
            for ln in stdout.split("\n"):
                if re.match(regex, ln):
                    found = True
                    break
        if found and not self.opt_args.keep_unrelated:
            self.run_traced("git push origin delete %s" % self.opt_args.odoo_branch)
            found = False
        self.run_traced(
            'git commit --no-verify -m "[NEW] Initial setup %s"'
            % self.opt_args.odoo_branch,
        )
        if found:
            self.run_traced("git push")
        else:
            self.run_traced(
                "git push --set-upstream origin %s" % self.opt_args.odoo_branch,
            )
        return sts, self.opt_args.odoo_branch

    def git_merge(self, repo, tgtdir=None, branch=None):
        tgtdir = self.get_path_of_repo(repo, root_path=tgtdir)
        repo_branch = self.repo_info[repo]["BRANCH"]
        branch = branch or repo_branch
        if os.getcwd() != tgtdir:
            self.run_traced("cd %s" % tgtdir)
        if pth.islink(tgtdir):
            return self.get_remote_info(sort=True)
        if repo_branch != branch:
            print(
                "Current branch %s is different from required branch  %s!"
                % (repo_branch, branch)
            )
            return 1, repo_branch
        cmd = "git stash"
        self.run_traced(cmd, verbose=False)
        sleep(1)
        cmd = "git fetch upstream %s --no-recurse-submodules" % self.master_branch
        sts, stdout, stderr = self.run_traced(cmd)
        if sts:
            print(stdout + stderr)
            print("")
            cmd = "git stash pop"
            sts1, stdout, stderr = self.run_traced(cmd)
            print(stdout + stderr)
            print("")
            return sts, repo_branch
        cmd = "git merge upstream/%s" % self.master_branch
        sts, stdout, stderr = self.run_traced(cmd)
        if sts:
            print(stdout + stderr)
            print("")
            cmd = "git merge --abort"
            sts1, stdout, stderr = self.run_traced(cmd)
            print(stdout + stderr)
            print("")
            cmd = "git stash pop"
            sts1, stdout, stderr = self.run_traced(cmd)
            print(stdout + stderr)
            print("")
        return sts, repo_branch

    def git_checkout(self, repo, target_path, branch, new_branch=False):
        if os.getcwd() != target_path:
            self.run_traced(
                "cd %s" % target_path,
            )
        (
            sts,
            repo_branch,
            git_url,
            stash_list,
            upstream,
            last_date,
            status,
            stage,
            brief,
        ) = self.get_remote_info(verbose=False)
        if new_branch and repo_branch != branch:
            cmd = ("git checkout -b %s" if new_branch else "git checkout %s") % branch
            sts, stdout, stderr = self.run_traced(cmd)
            if sts:
                print("Invalid branch %s" % branch)
                print("")
                if repo_branch != self.master_branch:
                    cmd = (
                        "git checkout -b %s" if new_branch else "git checkout %s"
                    ) % self.master_branch
                    sts, stdout, stderr = self.run_traced(cmd)
                    if sts:
                        print("Invalid branch %s" % self.master_branch)
                    else:
                        if new_branch:
                            self.repo_info[repo]["BRANCH"] = branch
                        sleep(1)
            else:
                if new_branch:
                    self.repo_info[repo]["BRANCH"] = branch
                sleep(1)
        return sts

    def git_delete_unrelated_branch(self, target_path):
        if not self.opt_args.keep_unrelated:
            if os.getcwd() != target_path:
                self.run_traced("cd %s" % target_path)
            sts, stdout, stderr = self.run_traced("git branch")
            for ln in stdout.split("\n"):
                if not ln or ln.startswith("*"):
                    continue
                self.run_traced("git branch -D %s" % ln.strip())

    def rsync_origin_path(self, repo, origin_path, target_path):
        exclude_path = self.opt_args.exclude_path
        exclude_opt = '--exclude=".*/"'
        for p in exclude_path:
            exclude_opt += ' --exclude="/%s"' % p
        if repo == "OCB":
            for p in os.listdir(origin_path):
                if (
                    p.startswith(".")
                    or p.startswith("_")
                    or pth.isdir(pth.join(origin_path, p, ".git"))
                    or p in exclude_path
                ):
                    continue
                src = pth.join(origin_path, p)
                if pth.islink(src):
                    continue
                if pth.isfile(src):
                    self.run_traced("cp %s %s" % (src, target_path))
                else:
                    self.run_traced(
                        "rsync -avz --delete %s %s/ %s/"
                        % (exclude_opt, src, pth.join(target_path, p)),
                    )
        elif not pth.islink(origin_path):
            self.run_traced(
                "rsync -avz --delete %s %s/ %s/"
                % (exclude_opt, origin_path, target_path),
            )
        if pth.isdir(target_path):
            for p in os.listdir(target_path):
                if (
                    p.startswith(".")
                    or p.startswith("_")
                    or p in ("egg-info", "readme")
                    or pth.isdir(pth.join(origin_path, p, ".git"))
                ):
                    continue
                src = pth.join(target_path, p)
                if not pth.exists(pth.join(origin_path, p)):
                    if pth.isfile(src):
                        self.run_traced("rm -f %s" % src)
                    else:
                        self.run_traced("rm -fR %s" % src)

        self.run_traced("please defcon gitignore")
        self.run_traced("please defcon precommit")
        if os.getcwd() != origin_path:
            self.run_traced("cd %s" % origin_path)
        sts, stdout, stderr = self.run_traced("git remote -v")
        url = ""
        if sts == 0 and stdout:
            for ln in stdout.split("\n"):
                lns = ln.split()
                if len(lns) < 2:
                    continue
                elif lns[0] == "origin":
                    url = lns[1]
                    break
        if os.getcwd() != target_path:
            self.run_traced("cd %s" % target_path)
        if url:
            url_upstream = ""
            for ln in stdout.split("\n"):
                lns = ln.split()
                if len(lns) < 2:
                    continue
                elif lns[0] == "upstream":
                    url_upstream = lns[1]
                    break
            if url_upstream:
                self.run_traced("git remote remove upstream")
            self.run_traced("git remote add upstream %s" % url)
        self.run_traced("git add ./")

    def git_new_branch(
        self,
        srcdir,
        tgtdir,
        repo,
    ):
        sts = self.action_clone_1_repo(
            repo,
            branch=self.opt_args.from_odoo_version,
            tgtdir=tgtdir,
            master_branch=self.get_prior_odoo_version(self.opt_args.from_odoo_version),
        )
        if sts:
            return sts, self.opt_args.odoo_branch
        sts = self.git_checkout(
            repo, tgtdir, self.opt_args.odoo_branch, new_branch=True
        )
        if sts:
            return sts, self.opt_args.odoo_branch
        self.git_delete_unrelated_branch(tgtdir)
        if self.opt_args.origin not in (".", "./"):
            self.rsync_origin_path(repo, srcdir, tgtdir)
        elif repo == "OCB":
            self.run_traced("gitignore ./")
        if self.opt_args.save_git:
            self.git_push_new_branch(tgtdir)
        return sts, self.opt_args.odoo_branch

    def action_list(self):
        return self.action_status()

    def action_status(self, format=None):
        if not self.target_path and "OCB" in self.repo_info:
            target_path = self.repo_info["OCB"]["PATH"]
        else:
            target_path = self.target_path
        print("Odoo main version..........: %s" % self.master_branch)
        print("Odoo root path.............: %s" % target_path)
        if self.opt_args.config:
            print("Odoo configuration file....: %s" % self.opt_args.config)
        fmt_list = format.split(",") if format else self.opt_args.format.split(",")
        fmt = ""
        datas = {}
        for item in fmt_list:
            fmt += " " + FMT_PARAMS[item]
            datas[item] = item.upper()
        fmt = fmt.strip()
        print(fmt % datas)
        for repo in self.repo_list:
            repo_branch = self.repo_info[repo]["BRANCH"]
            stage = self.repo_info[repo]["STAGE"]
            git_org = self.repo_info[repo]["GIT_ORG"]

            datas = {
                "branch": self.repo_info[repo]["BRANCH"],
                "brief": self.repo_info[repo]["BRIEF"],
                "dif_branch": repo_branch if repo_branch != self.master_branch else "",
                "git_org": self.repo_info[repo]["GIT_ORG"],
                "git_url": self.repo_info[repo]["URL"],
                "last_date": self.repo_info[repo]["LAST_DATE"],
                "path": self.repo_info[repo]["PATH"],
                "repo": "odoo" if repo == "OCB" and git_org == "odoo" else repo,
                "stash": "stash" if self.repo_info[repo]["STASH"] else "",
                "stash_info": self.repo_info[repo]["STASH"],
                "stage": self.repo_info[repo]["STAGE"],
                "status": self.repo_info[repo]["STATUS"],
                "sts": self.repo_info[repo]["STS"],
                "upstream": self.repo_info[repo].get("UPSTREAM", ""),
            }
            if self.opt_args.action != "unstaged" or stage == "unstaged":
                print(fmt % datas)
        if self.opt_args.show_addons:
            print()
            print(",".join(self.addons_path))
        return 0

    def action_clone_1_repo(self, repo, branch=None, tgtdir=None, master_branch=None):
        branch = branch or self.opt_args.odoo_branch
        tgtdir = tgtdir or self.get_path_of_repo(repo)
        master_branch = master_branch or self.master_branch
        bakdir = ""
        if pth.isdir(tgtdir):
            if self.opt_args.skip_if_exist:
                return 0
            elif not self.ask_4_confirm(
                "Path %s of repo %s already exists!" % (tgtdir, repo), "Delete (y/n)? "
            ):
                if self.opt_args.continue_after_error:
                    return 0
            if self.repo_is_ocb(repo):
                bakdir = "%s~" % tgtdir
                if pth.isdir(bakdir):
                    if os.getcwd() == bakdir:
                        self.run_traced("cd %s" % pth.dirname(bakdir))
                    cmd = "rm -fR %s" % bakdir
                    self.run_traced(cmd)
                cmd = "mv %s %s" % (tgtdir, bakdir)
                self.run_traced(cmd)
            elif not pth.islink(tgtdir):
                if os.getcwd() == tgtdir:
                    self.run_traced("cd %s" % pth.dirname(tgtdir))
                cmd = "rm -fR %s" % tgtdir
                self.run_traced(cmd)
        for git_org in self.opt_args.git_orgs:
            if repo == "OCB" and not self.opt_args.keep_root_owner:
                git_org = "odoo"
            self.set_default_repo_info(repo, git_org, branch)
            sts, remote_branch = self.git_clone(
                self.repo_info[repo]["URL"],
                tgtdir,
                branch,
                master_branch=master_branch,
                compact=True if git_org in ("odoo", "oca") else False,
                repo=repo,
            )
            if sts == 0:
                break
        self.repo_info[repo]["STS"] = sts
        if (
            pth.isdir(tgtdir)
            and self.repo_is_ocb(repo)
            and bakdir
            and pth.isdir(bakdir)
        ):
            for fn in os.listdir(bakdir):
                if fn.startswith((".", "_")):
                    continue
                path = pth.join(bakdir, fn)
                tgtfn = pth.join(tgtdir, fn)
                if pth.exists(tgtfn):
                    continue
                if pth.isdir(path):
                    cmd = "mv %s/ %s/" % (path, tgtfn)
                    self.run_traced(cmd)
                else:
                    cmd = "mv %s %s" % (path, tgtfn)
                    self.run_traced(cmd)
        return sts

    def action_clone(self):
        sts = 127
        if self.opt_args.repos and "OCB" not in self.opt_args.repos:
            if not self.ask_4_confirm(
                "Clone repositories %s w/o OCB" % self.opt_args.repos,
                "Proceede anyway (y/n)? ",
            ):
                return 1
        for repo in self.repo_list:
            sts1 = self.action_clone_1_repo(repo)
            sts = sts if sts != 127 else sts1
            if sts1 and not self.opt_args.continue_after_error:
                break
        if self.opt_args.verbose:
            self.action_status()
        return sts

    def action_amend(self):
        sts = 0
        for repo in self.repo_list:
            tgtdir = self.get_path_of_repo(repo)
            if pth.isdir(tgtdir):
                continue
            for git_org in self.opt_args.git_orgs:
                if repo == "OCB" and not self.opt_args.keep_root_owner:
                    git_org = "odoo"
                self.set_default_repo_info(repo, git_org, self.opt_args.odoo_branch)
                sts, remote_branch = self.git_clone(
                    self.repo_info[repo]["URL"],
                    tgtdir,
                    self.opt_args.odoo_branch,
                    master_branch=self.master_branch,
                    compact=True if git_org in ("odoo", "oca") else False,
                    repo=repo,
                )
                if sts == 0:
                    break
            self.repo_info[repo]["STS"] = sts
            if sts and not self.opt_args.continue_after_error:
                break
        if self.opt_args.verbose:
            self.action_status()
        return sts

    def action_download_or_pull_repo(self):
        sts = 0
        if not self.opt_args.verbose:
            # These info will be printed at the end by ation_status
            print("Odoo main version..........: %s" % self.master_branch)
            print("Odoo root path.............: %s" % self.target_path)
            if self.opt_args.config:
                print("Odoo configuration file....: %s" % self.opt_args.config)
        if self.opt_args.clean_repo:
            std_repositories = self.repo_list_from_github()
        for repo in self.repo_list:
            if (
                self.opt_args.clean_repo
                and repo != "OCB"
                and repo not in std_repositories
            ):
                tgtdir = self.get_path_of_repo(repo)
                if pth.isdir(tgtdir):
                    self.run_traced("rm -fR %s" % tgtdir)
            elif self.opt_args.action == "update":
                sts = self.git_pull(repo)[0]
            elif self.opt_args.action == "merge":
                sts = self.git_merge(repo)[0]
            else:
                raise IndexError("")
            if sts and not self.opt_args.continue_after_error:
                break
        if sts == 0:
            if self.opt_args.verbose and self.addons_path:
                print("addons_path = %s" % ",".join(self.addons_path))
        if self.opt_args.verbose:
            self.action_status()
        # Avoid github lock due excessive download rate
        sleep(3)
        return sts

    def action_new_branch(self):
        sts = 127
        # if (
        #         self.opt_args.repos
        #         and "OCB" not in self.opt_args.repos
        # ):
        #     if not self.ask_4_confirm(
        #             "Clone repositories %s w/o OCB" % self.opt_args.repos,
        #             "Proceede anyway (y/n)? "):
        #         return 1
        for repo in self.repo_list:
            srcdir = self.get_path_of_repo(repo)
            if not pth.isdir(srcdir):
                print("***** repo %s not found!" % repo)
                continue
            elif pth.islink(srcdir):
                print("***** repo %s (%s) is link!" % (repo, srcdir))
                continue
            elif not self.is_git_repo(path=srcdir):
                print("***** repo %s (%s) is not git repo!" % (repo, srcdir))
                continue
            tgtdir = self.get_path_of_repo(repo, root_path=self.target_path)
            sts, branch = self.git_new_branch(srcdir, tgtdir, repo)
            self.repo_info[repo]["STS"] = sts
            if sts and not self.opt_args.continue_after_error:
                break

        if self.opt_args.verbose:
            self.action_status()
        return sts


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Manage Odoo repositories", epilog="© 2021-2025 by SHS-AV s.r.l."
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
        # default="17.0",
        help="Odoo version to manage",
    )
    parser.add_argument(
        "-C",
        "--clean-repo",
        action="store_true",
        help="Remove repositories out of organization",
    )
    parser.add_argument(
        "--clean-empty-repo",
        action="store_true",
        help="Remove repositories without modules",
    )
    parser.add_argument("-c", "--config", help="Odoo configuration file")
    parser.add_argument("-D", "--default-gitorg", default="oca")
    # parser.add_argument("-d", "--deployment-mode", help="may be tree,server,odoo")
    parser.add_argument(
        "-e",
        "--skip-if-exist",
        action="store_true",
        help="Use this switch to skip existent repositories when you clone",
    )
    parser.add_argument(
        "-F",
        "--format",
        help=(
            "When status, use 1 or + of "
            "branch,brief,dif_branch,git_org,git_url,last_date,path,repo,stash,"
            "stash_info,stage,status,sts,upstream"
        ),
    )
    parser.add_argument(
        "-f",
        "--force",
        help="force download from github (ignore cache) or force branch rename",
        action="store_true",
    )
    parser.add_argument(
        "--from-odoo-version",
        help=("Clone from Odoo version"),
    )
    parser.add_argument(
        "-G",
        "--git-orgs",
        help="Git organizations, comma separated - " "May be: oca or zero",
    )
    parser.add_argument(
        "-g",
        "--use-git",
        action="store_true",
        help="When clone use git protocol instead of https",
    )
    parser.add_argument(
        "-k",
        "--continue-after-error",
        action="store_true",
        help="Continue action even after single repository error",
    )
    parser.add_argument(
        "-K",
        "--keep-root-owner",
        action="store_true",
        help="Keep git_org organization owner instead of odoo/odoo",
    )
    parser.add_argument(
        "--keep-unrelated",
        action="store_true",
        help="Keep unrelated branch when new-branch",
    )
    parser.add_argument(
        "-L",
        "--link-upstream",
        action="store_true",
        help="Create link to local original upstream (requires -o and -g)",
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
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument(
        "-o",
        "--origin",
        help="Declare origin repo path for 'merge' or 'new-branch' actions",
    )
    parser.add_argument("-p", "--target-path", help="Local directory")
    parser.add_argument(
        "-r", "--repos", help="Declare specific repositories to manage, comma separated"
    )
    parser.add_argument(
        "-S",
        "--save-git",
        action="store_true",
        help="Execute git pull after checkout of new-branch",
    )
    parser.add_argument(
        "-T", "--test", action="store_true", help="Execution for test (implies -n)"
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-X",
        "--exclude-path",
        help="Directories to exclude when new-branch (comma separated)",
        default="setup,venv_odoo",
    )
    parser.add_argument(
        "-x",
        "--extra-repo",
        help="may be: all,%s" % ",".join(XTRA_PREFIX),
    )
    parser.add_argument(
        "-y",
        "--assume-yes",
        action="store_true",
        help="Delete existent repositories when you clone (conflicts with -e)",
    )
    parser.add_argument(
        "action",
        nargs="?",
        help="May be clone,git-push,list,merge,new-branch,status,unstaged,update",
    )
    opt_args = parser.parse_args(cli_args)
    if not opt_args.format:
        if opt_args.action == "list":
            opt_args.format = "repo,branch,git_url,path"
        else:
            opt_args.format = "repo,branch,git_org,last_date,stage,stash,brief"
    deploy = OdooDeploy(opt_args)
    if opt_args.action == "list":
        sts = deploy.action_list()
    elif opt_args.action in ("status", "unstaged"):
        sts = deploy.action_status()
    elif opt_args.action == "clone":
        sts = deploy.action_clone()
    elif opt_args.action == "amend":
        sts = deploy.action_amend()
    elif opt_args.action == "new-branch":
        sts = deploy.action_new_branch()
    else:
        sts = deploy.action_download_or_pull_repo()
    if (
        sts == 0
        and opt_args.update_addons_conf
        and deploy.opt_args.config
        and pth.isfile(deploy.opt_args.config)
    ):
        deploy.update_conf()

    return sts


if __name__ == "__main__":
    exit(main())

