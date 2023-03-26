#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import re
import sys
import os
import argparse

from z0lib import z0lib

__version__ = "2.0.6"


class RepoCheckout(object):

    def __init__(self, opt_args):
        self.opt_args = opt_args
        if opt_args.odoo_branch not in ("16.0", "15.0", "14.0", "13.0", "12.0", "11.0",
                                        "10,0", "9.0", "8.0", "7.0", "6.1"):
            print("Invalid Odoo branch")
            exit(2)
        if (
            not opt_args.oca_path
            or not os.path.isdir(os.path.expanduser(opt_args.oca_path))
        ):
            print("Missed OCA path: use -o PATH!")
            exit(2)
        self.opt_args.oca_path = os.path.expanduser(opt_args.oca_path)
        if not opt_args.target_path:
            print("Missed target path: use -p PATH!")
            exit(2)
        self.opt_args.target_path = os.path.expanduser(opt_args.target_path)
        if not opt_args.git_org:
            print("Missed git organization: use -G ORG!")
            exit(2)
        self.opt_args.use_git = True
        if opt_args.git_org == "zero":
            self.opt_args.git_org = "zeroincombenze"
        self.git_url, self.git_org = self.get_git_org_n_url(opt_args.git_org)

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

    def is_git_repo(self, path):
        return os.path.isdir(os.path.join(path, ".git"))

    def build_new_repo(self, repo, oca_path):
        target_path = self.opt_args.target_path if repo == "OCB" else os.path.join(
            self.opt_args.target_path, repo)
        if os.path.isdir(target_path):
            if not self.opt_args.update:
                print("Path %s already exists!" % target_path)
                return 1
        else:
            z0lib.run_traced("cd %s" % os.path.dirname(target_path),
                             verbose=self.opt_args.verbose,
                             dry_run=self.opt_args.dry_run)
            git_repo = self.git_url + "/" + repo
            if repo == "OCB":
                z0lib.run_traced(
                    ("git clone %s %s --depth=1 --no-single-branch "
                     "--no-recurse-submodules")
                    % (git_repo, os.path.basename(target_path)),
                    verbose=self.opt_args.verbose,
                    dry_run=self.opt_args.dry_run)
            else:
                z0lib.run_traced("git clone %s --depth=1 --no-single-branch" % git_repo,
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
        if not os.path.isdir(target_path):
            print("Directory %s not created" % target_path)
            return 0
        z0lib.run_traced("cd %s" % target_path,
                         verbose=self.opt_args.verbose,
                         dry_run=self.opt_args.dry_run)
        z0lib.run_traced("git checkout -b %s" % self.opt_args.odoo_branch,
                         verbose=self.opt_args.verbose,
                         dry_run=self.opt_args.dry_run)
        sts, stdout, stderr = z0lib.run_traced("git branch",
                                               verbose=self.opt_args.verbose,
                                               dry_run=self.opt_args.dry_run)
        for ln in stdout.split("\n"):
            if not ln or ln.startswith("*"):
                continue
            z0lib.run_traced("git branch -D %s" % ln.strip(),
                             verbose=self.opt_args.verbose,
                             dry_run=self.opt_args.dry_run)
        if repo == "OCB":
            for p in os.listdir(oca_path):
                if (
                    p.startswith(".")
                    or p.startswith("_")
                    or os.path.isdir(os.path.join(oca_path, p, ".git"))
                ):
                    continue
                src = os.path.join(oca_path, p)
                if os.path.isfile(src):
                    z0lib.run_traced("cp %s %s" % (src, target_path),
                                     verbose=self.opt_args.verbose,
                                     dry_run=self.opt_args.dry_run)
                else:
                    z0lib.run_traced("rsync -avzC --delete  --exclude \".*/\" %s/ %s/"
                                     % (src, os.path.join(target_path, p)),
                                     verbose=self.opt_args.verbose,
                                     dry_run=self.opt_args.dry_run)
        else:
            z0lib.run_traced("rsync -avzC --delete  --exclude \".*/\" %s/ %s/"
                             % (oca_path, target_path),
                             verbose=self.opt_args.verbose,
                             dry_run=self.opt_args.dry_run)
        for p in os.listdir(target_path):
            if (
                p.startswith(".")
                or p.startswith("_")
                or p in ("egg-info", "readme")
                or os.path.isdir(os.path.join(oca_path, p, ".git"))
            ):
                continue
            src = os.path.join(target_path, p)
            if not os.path.exists(os.path.join(oca_path, p)):
                if os.path.isfile(src):
                    z0lib.run_traced("rm -f %s" % src,
                                     verbose=self.opt_args.verbose,
                                     dry_run=self.opt_args.dry_run)
                else:
                    z0lib.run_traced("rm -fR %s" % src,
                                     verbose=self.opt_args.verbose,
                                     dry_run=self.opt_args.dry_run)
        z0lib.run_traced("cd %s" % oca_path,
                         verbose=self.opt_args.verbose,
                         dry_run=self.opt_args.dry_run)
        sts, stdout, stderr = z0lib.run_traced("git remote -v",
                                               verbose=self.opt_args.verbose,
                                               dry_run=self.opt_args.dry_run)
        if sts == 0 and stdout:
            url = ""
            for ln in stdout.split("\n"):
                lns = ln.split()
                if lns[0] == "origin":
                    url = lns[1]
                    break
            if url:
                if os.getcwd() != target_path:
                    z0lib.run_traced("cd %s" % target_path,
                                     verbose=self.opt_args.verbose,
                                     dry_run=self.opt_args.dry_run)
                z0lib.run_traced("git remote add oca %s" % url,
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
        if sts == 0 and self.opt_args.save_git:
            if os.getcwd() != target_path:
                z0lib.run_traced("cd %s" % target_path,
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
            found = False
            sts, stdout, stderr = z0lib.run_traced("git branch")
            if sts == 0 and stdout:
                regex = r"^[*]* +" + self.opt_args.odoo_branch + r" *$"
                for ln in stdout.split("\n"):
                    if re.match(regex, ln):
                        found = True
                        break
            if found and self.opt_args.remove_remote_branch:
                z0lib.run_traced("git push origin delete %s"
                                 % self.opt_args.odoo_branch,
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
                found = False
            z0lib.run_traced("git add ./",
                             verbose=self.opt_args.verbose,
                             dry_run=self.opt_args.dry_run)
            z0lib.run_traced("git commit --no-verify -m \"[NEW] Initial setup %s\""
                             % self.opt_args.odoo_branch,
                             verbose=self.opt_args.verbose,
                             dry_run=self.opt_args.dry_run)
            if found:
                z0lib.run_traced("git push",
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
            else:
                z0lib.run_traced("git push --set-upstream origin %s"
                                 % self.opt_args.odoo_branch,
                                 verbose=self.opt_args.verbose,
                                 dry_run=self.opt_args.dry_run)
        return 0

    def git_checkout(self):
        path = self.opt_args.oca_path
        if self.is_git_repo(path):
            sts = self.build_new_repo("OCB", path)
        if sts == 0:
            for repo in sorted(os.listdir(self.opt_args.oca_path)):
                path = os.path.join(self.opt_args.oca_path, repo)
                if self.is_git_repo(path):
                    sts = self.build_new_repo(repo, path)
                    if sts:
                        break
        return sts


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create new repo branch",
        epilog="© 2022-2023 by SHS-AV s.r.l."
    )
    parser.add_argument("-b", "--odoo-branch",
                        dest="odoo_branch",
                        help="New Odoo branch")
    parser.add_argument("-G", "--git-org",
                        help="Git organization")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-o", "--oca-path",
                        help="Local directory")
    parser.add_argument("-p", "--target-path",
                        help="Local directory")
    parser.add_argument("-R", "--remove-remote-branch", action="store_true")
    parser.add_argument("-S", "--save-git", action="store_true")
    parser.add_argument("-U", "--update", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    opt_args = parser.parse_args(cli_args)
    repo = RepoCheckout(opt_args)
    return repo.git_checkout()


if __name__ == "__main__":
    exit(main(None))
