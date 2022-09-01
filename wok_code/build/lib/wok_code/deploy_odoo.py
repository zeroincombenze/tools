#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-22 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
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
import shutil

try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param
try:
    from wok_code.wok_code.wget_odoo_repositories import get_list_from_url
except ImportError:
    from wok_code.wget_odoo_repositories import get_list_from_url


__version__ = "2.0.0"

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

ODOO_VALID_GITORGS = ('oca', 'librerp', 'zero')

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
INVALID_NAMES = ["addons", "debian", "doc", "egg-info", "oca", "odoo"]


class OdooDeploy(object):

    def __init__(self, opt_args):
        self.opt_args = opt_args
        self.root = None
        self.addons_path = []
        self.DATA = {}
        for git_org in ODOO_VALID_GITORGS:
            for branch in ODOO_VALID_VERSIONS:
                if git_org == 'librerp' and branch not in ('12.0', '14.0'):
                    continue
                hash_id = git_org + branch.split(".")[0]
                if git_org == self.opt_args.default_gitorg:
                    odoo_vid = branch
                else:
                    odoo_vid = hash_id
                self.DATA[hash_id] = {}
                if hash_id in DEFAULT_DATA:
                    for key, item in DEFAULT_DATA[hash_id].items():
                        self.DATA[hash_id][key] = item
                if 'PATH' not in self.DATA[hash_id]:
                    self.DATA[hash_id]['PATH'] = build_odoo_param(
                        "ROOT", odoo_vid=odoo_vid, multi=True)
                if "URL" not in self.DATA[hash_id]:
                    if git_org == 'zero':
                        self.DATA[hash_id]["URL"] = "git@github.com:zeroincombenze"
                    elif git_org == 'oca':
                        self.DATA[hash_id]["URL"] = "https://github.com/OCA"
                    elif git_org == 'librerp':
                        self.DATA[hash_id]["URL"] = "git@github.com:LibrERP-network"
                    if opt_args.config:
                        self.DATA[hash_id]['CONFN'] = opt_args.config
                    elif 'CONFN' not in self.DATA[hash_id]:
                        self.DATA[hash_id]['CONFN'] = os.path.basename(build_odoo_param(
                            "CONFN", odoo_vid=odoo_vid, multi=True))

    def list_data(self):
        for git_org in ODOO_VALID_GITORGS:
            if self.opt_args.git_org and git_org != self.opt_args.git_org:
                continue
            for branch in ODOO_VALID_VERSIONS:
                if self.opt_args.odoo_branch and branch != self.opt_args.odoo_branch:
                    continue
                hash_id = git_org + branch.split(".")[0]
                if hash_id not in self.DATA:
                    continue
                print('[%s]' % hash_id)
                if hash_id in sorted(self.DATA.keys()):
                    for key in ('CONFN', 'PATH', "URL"):
                        if key in self.DATA[hash_id]:
                            print('  %-12.12s = "%s"' % (key, self.DATA[hash_id][key]))
                    for key, item in sorted(self.DATA[hash_id].items()):
                        if key in ('CONFN', 'PATH', "URL"):
                            continue
                        print('    %-20.20s = "%s"' % (key, item))

    def find_data_dir(self, canonicalize=None):
        tgtdir = os.path.join(os.environ['HOME'], ".local")
        if os.path.isdir(tgtdir):
            tgtdir = os.path.join(tgtdir, "share")
            if not os.path.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            odoo_master_branch = build_odoo_param(
                "FULLVER", odoo_vid=self.opt_args.odoo_branch, multi=True)
            base = 'Odoo%s' % odoo_master_branch.split('.')[0]
            tgtdir = os.path.join(tgtdir, base)
            if not os.path.isdir(tgtdir) and canonicalize:
                os.mkdir(tgtdir)
            for base in ('addons', 'filestore', 'sessions'):
                tgt = os.path.join(tgtdir, base)
                if not os.path.isdir(tgt) and canonicalize:
                    os.mkdir(tgt)
            tgtdir = os.path.join(tgtdir, 'addons')
        return tgtdir

    def update_conf(self, git_org=None, branch=None):
        if self.addons_path:
            data_dir = self.find_data_dir(canonicalize=True)
            git_org = git_org or self.opt_args.git_org
            branch = branch or self.opt_args.odoo_branch
            hash_id = git_org + branch.split(".")[0]
            with open("/etc/odoo/%s" % self.DATA[hash_id]["CONFN"], "r") as fd:
                content = fd.read()
            config = ''
            for ln in content.split("\n"):
                if ln.startswith("addons_path"):
                    ln = 'addons_path = %s' % ','.join(self.addons_path)
                elif ln.startswith("data_dir"):
                    ln = 'data_dir = %s' % data_dir
                config += ('%s\n' % ln)
            if not self.opt_args.dry_run:
                with open("/etc/odoo/%s" % self.DATA[hash_id]["CONFN"], "w") as fd:
                    fd.write(config)

    def is_git_repo(self, repo):
        res = bool(repo)
        if repo:
            if repo.startswith('.') or repo.startswith('_'):
                res = False
            elif repo in INVALID_NAMES:
                res = False
            elif self.root:
                tgtdir = self.get_path_of_repo(repo)
                res = os.path.isdir(os.path.join(tgtdir, '.git'))
        return res

    def get_alt_gitorg(self, git_org=None):
        git_org = git_org or self.opt_args.git_org
        return {
            'odoo': 'oca',
            'librerp': 'zero',
            'zero': 'oca',
        }.get(git_org)

    def explore_root_dir(self, repos):
        if self.root:
            for repo in os.listdir(self.root):
                if self.is_git_repo(repo) and repo not in repos:
                    repos.append(repo)
        return repos

    def repo_is_ocb(self, repo):
        return repo in ("OCB", "odoo")

    def get_path_of_repo(self, repo):
        if self.repo_is_ocb(repo):
            tgtdir = self.root
        else:
            tgtdir = os.path.join(self.root, repo)
        return tgtdir

    def get_repo_info(self, git_org=None, branch=None):
        git_org = git_org or self.opt_args.git_org
        branch = branch or self.opt_args.odoo_branch
        hash_id = git_org + branch.split(".")[0]
        repos = []
        if hash_id not in self.DATA:
            return repos
        with_ocb = False
        if self.opt_args.create_new:
            content = get_list_from_url(
                {
                    'opt_verbose': self.opt_args.verbose,
                    'dry_run': False,
                    'def_repo': self.opt_args.dry_run,
                    'odoo_vid': branch,
                    'extra': 'none',
                    'l10n': ['l10n-italy', 'l10n-italy-supplemental'],
                },
                {
                    'zero': 'zeroincombenze',
                    'oca': 'OCA'
                }.get(git_org, git_org)
            )
            self.root = os.path.expanduser(self.DATA[hash_id]['PATH'])
            for repo in content:
                # if not self.is_git_repo(repo):
                #     continue
                if self.repo_is_ocb(repo):
                    with_ocb = True
                    continue
                repos.append(repo)
        elif self.opt_args.update_addons_conf or self.opt_args.only_update:
            self.root = os.path.expanduser(self.DATA[hash_id]['PATH'])
            repos = self.explore_root_dir(repos)
            if repos:
                with_ocb = True
        else:
            dirnames = {}
            HOME = os.environ["HOME"]
            with open("/etc/odoo/%s" % self.DATA[hash_id]["CONFN"], "r") as fd:
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
                            dirnames[dname] += 1
                    break
            root = False
            ctr = 0
            for dname in dirnames.keys():
                if dirnames[dname] > ctr:
                    root = dname
                    ctr = dirnames[dname]
            if root:
                self.root = root
        if with_ocb:
            repos = ['OCB'] + sorted(repos)
        else:
            repos = sorted(repos)
        return repos

    def download_single_repo(self, repo, git_org=None, branch=None):
        git_org = git_org or self.opt_args.git_org
        branch = branch or self.opt_args.odoo_branch
        odoo_master_branch = build_odoo_param("FULLVER", odoo_vid=branch, multi=True)
        hash_id = git_org + branch.split(".")[0]
        if self.repo_is_ocb(repo) and not self.opt_args.keep_root_owner:
            git_url = 'https://github.com/odoo'
            repo = 'odoo'
        elif repo in self.DATA[hash_id]:
            git_url = self.DATA[hash_id][repo]
        else:
            git_url = self.DATA[hash_id]["URL"]
        if not git_url:
            return 127
        git_url = "%s/%s.git" % (git_url, repo)
        bakdir = ''
        tgtdir = self.get_path_of_repo(repo)
        if not os.path.isdir(tgtdir) and self.opt_args.only_update:
            return 127
        elif os.path.isdir(tgtdir) and not self.opt_args.only_update:
            if self.opt_args.skip_if_exist:
                return self.git_pull(tgtdir, branch, master_branch=odoo_master_branch)
            elif not self.opt_args.assume_yes:
                print("Path %s of repo %s already exists!" % (tgtdir, repo))
                dummy = input("Delete (y/n)? ")
                if not dummy.lower().startswith("y"):
                    return 3
            if self.repo_is_ocb(repo):
                bakdir = '%s~' % tgtdir
                if os.path.isdir(bakdir):
                    cmd = "rm -fR %s" % bakdir
                    run_traced(self.opt_args, cmd)
                cmd = "mv %s %s" % (tgtdir, bakdir)
                run_traced(self.opt_args, cmd)
            else:
                cmd = "rm -fR %s" % tgtdir
                run_traced(self.opt_args, cmd)
        if os.path.isdir(tgtdir) and self.opt_args.only_update:
            sts = self.git_pull(tgtdir, branch, master_branch=odoo_master_branch)
        else:
            sts = self.git_clone(
                git_url, tgtdir, branch, master_branch=odoo_master_branch)
            if not os.path.isdir(tgtdir):
                sts = 0 if self.opt_args.dry_run else 1
            if sts == 0:
                cmd = "cd %s" % tgtdir
                run_traced(self.opt_args, cmd)
                if self.repo_is_ocb(repo) and bakdir and os.path.isdir(bakdir):
                    for fn in os.listdir(bakdir):
                        if fn.startswith('.') or fn.startswith('_'):
                            continue
                        path = os.path.join(bakdir, fn)
                        tgtfn = os.path.join(tgtdir, fn)
                        if os.path.exists(tgtfn):
                            continue
                        if os.path.isdir(path):
                            cmd = "mv %s/ %s/" % (path, tgtfn)
                            run_traced(self.opt_args, cmd)
                        else:
                            cmd = "mv %s %s" % (path, tgtfn)
                            run_traced(self.opt_args, cmd)
        if sts == 0:
            self.add_addons_path(tgtdir, repo)
            run_traced(self.opt_args, "git branch")
        if sts:
            print("*** Error ***")
            dummy = input("Press RET to continue ...")
        return sts

    def use_alter_branch(self, cmd, branch, master_branch):
        sts = 0
        if branch.endswith("-devel"):
            sts = run_traced(self.opt_args, cmd.replace("-devel", "_devel"))
        elif branch.endswith("_devel"):
            sts = run_traced(self.opt_args, cmd.replace("_devel", "-devel"))
        if sts and master_branch:
            cmd = cmd.replace(branch, master_branch)
            sts = run_traced(self.opt_args, cmd)
        return sts

    def add_addons_path(self, tgtdir, repo):
        if self.repo_is_ocb(repo):
            path = ""
            for base in ('odoo', 'openerp'):
                if os.path.isdir(os.path.join(tgtdir, base)):
                    path = os.path.join(tgtdir, base, 'addons')
                    break
            if path:
                self.addons_path.append(path)
            self.addons_path.append(os.path.join(tgtdir, 'addons'))
            self.addons_path.append(self.find_data_dir())
        else:
            self.addons_path.append(tgtdir)

    def git_clone(self, git_url, tgtdir, branch, master_branch=None):
        root = os.path.dirname(tgtdir)
        base = os.path.basename(tgtdir)
        if os.getcwd() != root:
            cmd = "cd %s" % root
            run_traced(self.opt_args, cmd)
        if git_url.startswith("git"):
            opts = "-b %s" % branch
        else:
            opts = "-b %s --no-single-branch --depth=1" % branch
        if opts:
            cmd = "git clone %s %s/ %s" % (git_url, base, opts)
        else:
            cmd = "git clone %s %s/" % (git_url, base)
        sts = run_traced(self.opt_args, cmd)
        if sts:
            sts = self.use_alter_branch(cmd, branch, master_branch)
        if sts:
            print("Invalid branch %s" % branch)
        return sts

    def git_pull(self, tgtdir, branch, master_branch=None):
        cmd = "cd %s" % tgtdir
        run_traced(self.opt_args, cmd)
        cmd = "git stash"
        run_traced(self.opt_args, cmd)
        cmd = "git checkout %s &>/dev/null" % branch
        sts = run_traced(self.opt_args, cmd)
        if sts:
            sts = self.use_alter_branch(cmd, branch, master_branch)
        if sts:
            print("Invalid branch %s" % branch)
        cmd = "git pull"
        return run_traced(self.opt_args, cmd)


def run_traced(opt_args, cmd):
    if opt_args.verbose:
        print('>>> %s' % cmd)
    if cmd.startswith("cd "):
        tgtdir = cmd[3:]
        if not opt_args.dry_run or os.path.isdir(tgtdir):
            return os.chdir(tgtdir)
        return 0
    elif not opt_args.dry_run:
        if cmd.startswith("rm -fR "):
            tgtdir = cmd[7:]
            return shutil.rmtree(tgtdir)
        elif cmd.startswith("mkdir "):
            tgtdir = cmd[6:]
            return os.mkdir(tgtdir)
        return os.system(cmd)
    return 0


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Deploy Oddo repositories from git",
        epilog="© 2021-2022 by SHS-AV s.r.l."
    )
    parser.add_argument('-A', '--update-addons-conf',
                        action='store_true',
                        help='Update addons_path in Odoo configuration file')
    parser.add_argument('-b', '--odoo-branch', dest='odoo_branch')
    parser.add_argument('-c', '--config',
                        help='Odoo configuration file')
    parser.add_argument('-D', '--default-gitorg', default='zero')
    parser.add_argument('-e', '--skip-if-exist', action='store_true')
    parser.add_argument('-G', '--git-org', help='May be: oca librerp or zero')
    parser.add_argument('-K', '--keep-root-owner',
                        action='store_true',
                        help='keep OCB/odoo organization owner')
    parser.add_argument('-L', '--list',
                        action='store_true',
                        help='List configuration data')
    parser.add_argument('-N', '--create-new',
                        action='store_true',
                        help='create all repositories of organization')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-R', '--reclone',
                        action='store_true',
                        help='reclone existent repositories')
    parser.add_argument('-U', '--only-update',
                        action='store_true',
                        help='update (pull) repositories')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument('-y', '--assume-yes', action='store_true')
    opt_args = parser.parse_args(cli_args)
    if opt_args.list:
        deploy = OdooDeploy(opt_args)
        deploy.list_data()
        return 0
    odoo_master_branch = build_odoo_param(
        "FULLVER", odoo_vid=opt_args.odoo_branch, multi=True)
    if odoo_master_branch not in ODOO_VALID_VERSIONS:
        print("Invalid odoo version")
        exit(1)
    if opt_args.git_org not in ODOO_VALID_GITORGS:
        opt_args.git_org = build_odoo_param(
            "GIT_ORGID", odoo_vid=opt_args.odoo_branch, multi=True
        )
    if opt_args.git_org not in ODOO_VALID_GITORGS:
        print("Invalid git organization")
        exit(1)
    if not opt_args.only_update and not opt_args.create_new and not opt_args.reclone:
        print("No action issued! Please use -U or -N or -R switch")
        exit(1)
    if ((opt_args.only_update and opt_args.create_new)
            or (opt_args.create_new and opt_args.reclone)
            or (opt_args.only_update and opt_args.reclone)):
        print("Too switches -U or _N or -R!")
        exit(1)

    # import pdb; pdb.set_trace()
    deploy = OdooDeploy(opt_args)
    repos = deploy.get_repo_info()
    for repo in repos:
        deploy.download_single_repo(repo)
    if not opt_args.only_update:
        alt_git_org = deploy.get_alt_gitorg()
        if alt_git_org:
            opt_args.skip_if_exist = True
            alt_deploy = OdooDeploy(opt_args)
            alt_repos = alt_deploy.get_repo_info(git_org=alt_git_org)
            alt_repos = sorted(list(set(alt_repos) - set(repos)))
            if alt_repos:
                repos = repos + alt_repos
    if opt_args.verbose:
        print('addons_path = %s' % ','.join(deploy.addons_path))
    if opt_args.update_addons_conf:
        deploy.update_conf()


if __name__ == "__main__":
    exit(main())
