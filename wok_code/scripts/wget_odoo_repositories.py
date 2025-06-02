#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2025 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
import os
import sys
import json
import argparse
from datetime import datetime, timedelta

if sys.version_info[0] == 2:
    from urllib2 import urlopen as urlopen
else:
    from urllib.request import urlopen as urlopen

__version__ = "2.0.22"


ODOO_BRANCHES = (
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
XTRA_REPS = [
    "agreement",
    "apps-store",
    "business-requirement",
    "cooperative",
    "debian",
    "department",
    "doc",
    "donation",
    "event",
    "field-service",
    "fleet",
    "geospatial",
    "infrastructure",
    "iot",
    "operating-unit",
    "pos",
    "webkit-tools",
]
DEVEL_REPS = [
    "Odoo-samples",
    "VME",
    "OpenUpgrade",
    "dotnet",
    "grymb",
    "interface-github",
    "odoorpc",
    "openupgradelib",
    "project-agile",
    "pylint-odoo",
    "python-plus",
    "rest-framework",
    "runbot-addons",
    "z0bug_odoo",
    "zerobug",
    "zeroincombenze",
]


def cache_init():
    return {}


def cache_fqn():
    return os.path.join(
        os.path.expanduser("~/.local/share"),
        ".%s.dat" % os.path.splitext(os.path.basename(__file__))[0],
    )


def cache_load():
    fqn = cache_fqn()
    if os.path.isfile(fqn):
        with open(fqn, "r") as fd:
            return eval(fd.read())
    return cache_init()


def cache_save(cache):
    fqn = cache_fqn()
    if not os.path.isdir(os.path.dirname(fqn)):
        os.makedirs(os.path.dirname(fqn))
    with open(fqn, "w") as fd:
        fd.write(str(cache))


def cache_hash_name(git_org, branch):
    return git_org + "/" + branch


def cache_add_entry(cache, git_org, branch, keep_cache=None):
    hash_name = cache_hash_name(git_org, branch)
    if hash_name not in cache:
        cache[hash_name] = {
            "expire": (
                (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT%H:%M:%S.000")
                if keep_cache
                else datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
            ),
            # "lst": []
        }
    # Weird bug
    if "lst" not in cache[hash_name]:
        cache[hash_name]["lst"] = []
    return cache


def cache_add_repo(cache, git_org, branch, repo):
    hash_name = cache_hash_name(git_org, branch)
    cache = cache_add_entry(cache, git_org, branch)
    if repo not in cache[hash_name]["lst"]:
        cache[hash_name]["lst"].append(repo)
    return cache


def cache_default_repositories(git_org, branch):
    data = []
    if git_org == "odoo":
        data = ["odoo"]
    elif git_org == "librerp":
        data = ["accounting", "custom-addons", "l10n-italy"]
    elif git_org in ("oca", "zeroincombenze"):
        data = [
            "account-analytic",
            "account-budgeting",
            "account-closing",
            "account-consolidation",
            "account-financial-reporting",
            "account-financial-tools",
            "account-fiscal-rule",
            "account-invoice-reporting",
            "account-invoicing",
            "account-payment",
            "account-reconcile",
            "apps-store",
            "bank-payment",
            "bank-statement-import",
            "brand",
            "business-requirement",
            "calendar",
            "commission",
            "community-data-files",
            "connector",
            "contract",
            "credit-control",
            "crm",
            "currency",
            "data-protection",
            "ddmrp",
            "debian",
            "delivery-carrier",
            "dms",
            "doc",
            "e-commerce",
            "edi",
            "geospatial",
            "helpdesk",
            "hr",
            "intrastat-extrastat",
            "iot",
            "knowledge",
            "l10n-italy",
            "maintenance",
            "management-system",
            "manufacture",
            "manufacture-reporting",
            "margin-analysis",
            "mgmtsystem",
            "mis-builder",
            "mis-builder-contrib",
            "multi-company",
            "partner-contact",
            "pos",
            "product-attribute",
            "product-kitting",
            "product-pack",
            "product-variant",
            "project",
            "project-agile",
            "project-reporting",
            "purchase-reporting",
            "purchase-workflow",
            "queue",
            "report-print-send",
            "reporting-engine",
            "requirements.txt",
            "rma",
            "sale-financial",
            "sale-reporting",
            "sale-workflow",
            "search-engine",
            "server-auth",
            "server-backend",
            "server-brand",
            "server-env",
            "server-tools",
            "server-ux",
            "social",
            "stock-logistics-barcode",
            "stock-logistics-reporting",
            "stock-logistics-tracking",
            "stock-logistics-transport",
            "stock-logistics-warehouse",
            "stock-logistics-workflow",
            "storage",
            "timesheet",
            "web",
            "webhook",
            "webkit-tools",
            "website",
            "website-cms",
            "wms",
        ]
    if git_org == "zeroincombenze":
        data.append("grymb")
        data.append("l10n-italy-supplemental")
        data.append("marketplace")
        data.append("Odoo-samples")
        data.append("profiles")
        data.append("tools")
        data.append("uncovered")
        data.append("zerobug")
        data.append("zerobug-test")
        if branch == "7.0":
            data.append("account_banking_cscs")
            data.append("cscs_addons")
    return data


def cache_load_from_github(cache, git_org, branch, verbose=0):
    baseurl = "https://api.github.com/users/%s/repos" % git_org
    rooturl = "https://api.github.com/repos/%s" % git_org
    page = 0
    touch = False
    while 1:
        page += 1
        pageurl = "%s?q=addClass+user:mozilla&page=%d" % (baseurl, page)
        if verbose:
            print("Acquiring data from github.com (page=%d)..." % page)
        try:
            response = urlopen(pageurl)
            data = json.loads(response.read())
        except BaseException:
            data = []
        if not data:
            break
        if verbose:
            print("Analyzing received data ...")
        for repoinfo in data:
            repo = os.path.basename(repoinfo["url"])
            if repo.startswith("."):
                continue
            if branch:
                pageurl = "%s/%s/branches" % (rooturl, repo)
                try:
                    branch_response = urlopen(pageurl)
                    branches = [x["name"] for x in json.loads(branch_response.read())]
                    touch = True
                except BaseException:
                    branches = ODOO_BRANCHES
                for repobranch in branches:
                    if repobranch in ODOO_BRANCHES:
                        cache = cache_add_repo(cache, git_org, repobranch, repo)
                    else:
                        hash_name = cache_hash_name(git_org, repobranch)
                        if hash_name in cache:
                            del cache[hash_name]
                for repobranch in ODOO_BRANCHES:
                    if repobranch not in branches:
                        hash_name = cache_hash_name(git_org, repobranch)
                        # Weird bug
                        if hash_name in cache and "lst" not in cache[hash_name]:
                            cache[hash_name]["lst"] = []
                        if hash_name in cache and repo in cache[hash_name]["lst"]:
                            del cache[hash_name]["lst"]
    if touch:
        hash_name = cache_hash_name(git_org, branch)
        if "lst" not in cache[hash_name]:
            cache[hash_name]["expire"] = (datetime.now() + timedelta(11)).strftime(
                "%Y-%m-%dT%H:%M:%S.000"
            )
        else:
            cache = cache_validate_repos(cache, git_org, branch)
    else:
        cache = cache_validate_repos(cache, git_org, branch)
    return cache


def cache_validate_repos(cache, git_org, branch, verbose=0):
    if verbose:
        print("Validating repo cache ...")
    pageurl = "https://github.com/%s/%s/tree/%s"
    hash_name = cache_hash_name(git_org, branch)
    for repo in cache[hash_name]["lst"]:
        try:
            urlopen(pageurl % (git_org, repo, branch))
        except BaseException:
            del cache[hash_name]["lst"][cache[hash_name]["lst"].index(repo)]
    cache[hash_name]["expire"] = (datetime.now() + timedelta(7)).strftime(
        "%Y-%m-%dT%H:%M:%S.000"
    )
    return cache


def cache_load_default(cache, git_org, branch):
    hash_name = cache_hash_name(git_org, branch)
    for repo in cache_default_repositories(git_org, branch):
        if repo not in cache[hash_name]["lst"]:
            cache[hash_name]["lst"].append(repo)
    return cache


def cache_get_repolist(
    cache, git_org, branch, verbose=0, force=False, ignore_github=False
):
    cache = cache_add_entry(
        cache, git_org, branch, keep_cache=not force or not ignore_github
    )
    hash_name = cache_hash_name(git_org, branch)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
    if cache[hash_name]["expire"] < now or force:
        cache = cache_load_default(cache, git_org, branch)
        if not ignore_github:
            cache = cache_load_from_github(cache, git_org, branch, verbose=verbose)
        elif cache[hash_name]["expire"] < now or force:
            cache = cache_validate_repos(cache, git_org, branch)
    if (
        "mgmtsystem" in cache[hash_name]["lst"]
        and "management-system" in cache[hash_name]["lst"]
    ):
        del cache[hash_name]["lst"][cache[hash_name]["lst"].index("mgmtsystem")]
    return sorted(cache[hash_name]["lst"])


def repo_is_valid(opt_args, repo):
    if (
        (
            "." not in repo
            and all([not repo.startswith(x + "-") for x in XTRA_PREFIX])
            and repo not in XTRA_REPS
            and repo not in DEVEL_REPS
        )
        or any([repo.startswith(x + "-") and x in opt_args.extra for x in XTRA_PREFIX])
        or (repo in XTRA_REPS and repo in opt_args.extra)
        or (repo in DEVEL_REPS and "devel" in opt_args.extra)
        or (repo.startswith("l10n-") and repo in opt_args.l10n)
    ):
        return True
    return False


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Get repository list from github",
        epilog="© 2019-2025 by SHS-AV s.r.l.",
    )
    parser.add_argument(
        "-b",
        "--odoo-branch",
        help="may be one from 6.1 to 18.0",
        action="store",
        dest="branch",
    )
    parser.add_argument(
        "-D",
        "--default",
        help="Default repositories (no from github)",
        action="store_true",
        dest="def_repo",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="force download from github (ignore cache)",
        action="store_true",
    )
    parser.add_argument(
        "-G", "--git-org", help="select repository", action="store", dest="git_org"
    )
    parser.add_argument(
        "-l",
        "--local-reps",
        help="select local repositories",
        action="store",
        dest="l10n",
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument(
        "-O", "--oca", help="repository OCA", action="store_true", dest="oca"
    )
    # parser.add_argument('-q')
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-x",
        "--extra-reps",
        help="may be: all,%s" % ",".join(XTRA_PREFIX),
        action="store",
        dest="extra",
    )
    parser.add_argument(
        "-Z",
        "--zeroincombenze",
        help="repository zeroincombenze",
        action="store_true",
        dest="zero",
    )
    parser.add_argument("--return-repos", action="store_true")
    opt_args = parser.parse_args(cli_args)

    git_orgs = []
    if opt_args.git_org:
        git_orgs = []
        for x in opt_args.git_org.split(","):
            x = x if x != "zero" else "zeroincombenze"
            x = x if x != "OCA" else "oca"
            git_orgs.append(x)
    else:
        if opt_args.zero:
            git_orgs.append("zeroincombenze")
        if opt_args.oca:
            git_orgs.append("oca")
    if not opt_args.l10n:
        opt_args.l10n = "l10n-italy,l10n-italy-supplemental"
    opt_args.l10n = opt_args.l10n.split(",")
    if not opt_args.extra:
        opt_args.extra = "none"
    elif opt_args.extra == "all":
        opt_args.extra = ",".join(XTRA_PREFIX)
    opt_args.extra = opt_args.extra.split(",")

    repositories = []
    cache = cache_load()
    for git_org in git_orgs:
        repositories += [
            repo
            for repo in cache_get_repolist(
                cache,
                git_org,
                opt_args.branch,
                verbose=opt_args.verbose,
                force=opt_args.force or opt_args.def_repo,
                ignore_github=opt_args.dry_run or opt_args.def_repo,
            )
            if repo_is_valid(opt_args, repo)
        ]
    cache_save(cache)
    if opt_args.return_repos:
        return repositories
    print("Found %d repositories of %s" % (len(repositories), git_orgs))
    print("\t" + " ".join(sorted(repositories)))
    return 0


if __name__ == "__main__":
    exit(main())

