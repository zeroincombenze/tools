#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2023 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
import os
import sys
import json
import argparse

if sys.version_info[0] == 2:
    from urllib2 import urlopen as urlopen
else:
    from urllib.request import urlopen as urlopen

# try:
#     from z0lib.z0lib import z0lib
# except ImportError:
#     try:
#         from z0lib import z0lib
#     except ImportError:
#         import z0lib

__version__ = "2.0.12"

ROOT_URL = "https://api.github.com/repos/zeroincombenze/"
USER_URL = "https://api.github.com/users/"
REPNAME_ACC_CLO = "OCB"
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
REPNAME_OCB = "OCB"
TEST_REP_OCB = {
    "issues_url": "%s%s/issues{/number}" % (ROOT_URL, REPNAME_OCB),
    "deployments_url": "%s%s/deployments" % (ROOT_URL, REPNAME_OCB),
    "stargazers_count": 0,
    "forks_url": "%s%s/forks" % (ROOT_URL, REPNAME_OCB),
    "mirror_url": None,
    "subscription_url": "%s%s/subscription" % (ROOT_URL, REPNAME_OCB),
    "notifications_url": "%s%s/notifications{?since,all,participating}"
    % (ROOT_URL, REPNAME_OCB),
    "collaborators_url": "%s%s/collaborators{collaborator}" % (ROOT_URL, REPNAME_OCB),
    "updated_at": "2013-07-15T20:26:20Z",
    "private": False,
    "pulls_url": "%s%s/pulls{/number}" % (ROOT_URL, REPNAME_OCB),
    "disabled": False,
    "issue_comment_url": "%s%s/issues/comments{number}" % (ROOT_URL, REPNAME_OCB),
    "labels_url": "%s%s/labels{/name}" % (ROOT_URL, REPNAME_OCB),
    "has_wiki": True,
    "full_name": "zeroincombenze/%s" % REPNAME_OCB,
    "owner": {
        "following_url": "%s%s/following{other_user}" % (ROOT_URL, REPNAME_OCB),
        "events_url": "%s%s/events{/privacy}" % (ROOT_URL, REPNAME_OCB),
        "avatar_url": "https://avatars2.githubusercontent.com/u/234?v=4",
        "url": "%s%s" % (USER_URL, REPNAME_OCB),
        "gists_url": "%s%s/gists{/gist_id}" % (USER_URL, REPNAME_OCB),
        "html_url": "https://github.com/%s" % REPNAME_OCB,
        "subscriptions_url": "%s%s/subscriptions" % (USER_URL, REPNAME_OCB),
        "node_id": "MDQ6VXNlcjY5NzI1NTU=",
        "test_repos_url": "%s%s/test_repos" % (USER_URL, REPNAME_OCB),
        "received_events_url": "%s%s/received_events" % (USER_URL, REPNAME_OCB),
        "gravatar_id": "",
        "starred_url": "%s%s/starred{/owner}{/TEST_REPo}" % (USER_URL, REPNAME_OCB),
        "site_admin": False,
        "login": "zeroincombenze",
        "type": "User",
        "id": 6972533,
        "followers_url": "%s%s/followers" % (USER_URL, REPNAME_OCB),
        "organizations_url": "%s%s/orgs" % (USER_URL, REPNAME_OCB),
    },
    "statuses_url": "%s%s/statuses/{sha}" % (ROOT_URL, REPNAME_OCB),
    "id": 58389479,
    "keys_url": "%s%s/keys{/key_id}" % (ROOT_URL, REPNAME_OCB),
    "description": "Odoo Accountant closing tools",
    "tags_url": "%s%s/tags" % (ROOT_URL, REPNAME_OCB),
    "archived": False,
    "downloads_url": "%s%s/downloads" % (ROOT_URL, REPNAME_OCB),
    "assignees_url": "%s%s/assignees{/user}" % (ROOT_URL, REPNAME_OCB),
    "contents_url": "%s%s/contents/{+path}" % (ROOT_URL, REPNAME_OCB),
    "has_pages": False,
    "git_refs_url": "%s%s/git/refs{/sha}" % (ROOT_URL, REPNAME_OCB),
    "open_issues_count": 0,
    "has_projects": True,
    "clone_url": "%s%s.git" % (ROOT_URL, REPNAME_OCB),
    "watchers_count": 0,
    "git_tags_url": "%s%s/git/tags{/sha}" % (ROOT_URL, REPNAME_OCB),
    "milestones_url": "%s%s/milestones{/number}" % (ROOT_URL, REPNAME_OCB),
    "languages_url": "%s%s/languages" % (ROOT_URL, REPNAME_OCB),
    "size": 1884251,
    "homepage": "",
    "fork": True,
    "commits_url": "%s%s/commits{/sha}" % (ROOT_URL, REPNAME_OCB),
    "releases_url": "%s%s/releases{id}" % (ROOT_URL, REPNAME_OCB),
    "issue_events_url": "%s%s/issues/events{/number}" % (ROOT_URL, REPNAME_OCB),
    "archive_url": "%s%s/{archive_format}{/ref}" % (ROOT_URL, REPNAME_OCB),
    "comments_url": "%s%s/comments{number}" % (ROOT_URL, REPNAME_OCB),
    "events_url": "%s%s/events" % (ROOT_URL, REPNAME_OCB),
    "contributors_url": "%s%s/contributors" % (ROOT_URL, REPNAME_OCB),
    "html_url": "%s%s" % (ROOT_URL, REPNAME_OCB),
    "forks": 0,
    "compare_url": "%s%s/compare/{base}...{ead}" % (ROOT_URL, REPNAME_OCB),
    "open_issues": 0,
    "node_id": "MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==",
    "git_url": "git://github.com/zeroincombenze/%s.git" % REPNAME_OCB,
    "svn_url": "%s%s/%s" % (ROOT_URL, REPNAME_OCB, REPNAME_OCB),
    "merges_url": "%s%s/merges" % (ROOT_URL, REPNAME_OCB),
    "has_issues": False,
    "ssh_url": "git@github.com:zeroincombenze/%s.git" % REPNAME_OCB,
    "blobs_url": "%s%s/git/blobs{/sha}" % (ROOT_URL, REPNAME_OCB),
    "git_commits_url": "%s%s/git/commits{/sha}" % (ROOT_URL, REPNAME_OCB),
    "hooks_url": "%s%s/hooks" % (ROOT_URL, REPNAME_OCB),
    "has_downloads": True,
    "license": {
        "spdx_id": "AGPL-3.0",
        "url": "https://api.github.com/licenses/agpl-3.0",
        "node_id": "MDc6TGljZW5zZTE=",
        "name": "GNU Affero General Public License v3.0",
        "key": "agpl-3.0",
    },
    "name": "%s" % REPNAME_OCB,
    "language": "Python",
    "url": "%s%s" % (ROOT_URL, REPNAME_OCB),
    "created_at": "2016-05-09T16:03:20Z",
    "watchers": 0,
    "pushed_at": "2018-06-06T12:58:38Z",
    "forks_count": 0,
    "default_branch": "7.0",
    "teams_url": "%s%s/teams" % (ROOT_URL, REPNAME_OCB),
    "trees_url": "%s%s/git/trees{/sha}" % (ROOT_URL, REPNAME_OCB),
    "branches_url": "%s%s/branches{/branch}" % (ROOT_URL, REPNAME_OCB),
    "subscribers_url": "%s%s/subscribers" % (ROOT_URL, REPNAME_OCB),
    "stargazers_url": "%s%s/stargazers" % (ROOT_URL, REPNAME_OCB),
}
REPNAME_ACC_CLO = "account-closing"
TEST_REP_ACC_CLO = {
    "issues_url": "%s%s/issues{/number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "deployments_url": "%s%s/deployments" % (ROOT_URL, REPNAME_ACC_CLO),
    "stargazers_count": 0,
    "forks_url": "%s%s/forks" % (ROOT_URL, REPNAME_ACC_CLO),
    "mirror_url": None,
    "subscription_url": "%s%s/subscription" % (ROOT_URL, REPNAME_ACC_CLO),
    "notifications_url": "%s%s/notifications{?since,all,participating}"
    % (ROOT_URL, REPNAME_ACC_CLO),
    "collaborators_url": "%s%s/collaborators{collaborator}"
    % (ROOT_URL, REPNAME_ACC_CLO),
    "updated_at": "2018-03-29T20:26:20Z",
    "private": False,
    "pulls_url": "%s%s/pulls{/number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "disabled": False,
    "issue_comment_url": "%s%s/issues/comments{number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "labels_url": "%s%s/labels{/name}" % (ROOT_URL, REPNAME_ACC_CLO),
    "has_wiki": True,
    "full_name": "zeroincombenze/%s" % REPNAME_ACC_CLO,
    "owner": {
        "following_url": "%s%s/following{other_user}" % (ROOT_URL, REPNAME_ACC_CLO),
        "events_url": "%s%s/events{/privacy}" % (ROOT_URL, REPNAME_ACC_CLO),
        "avatar_url": "https://avatars2.githubusercontent.com/u/123?v=4",
        "url": "%s%s" % (USER_URL, REPNAME_ACC_CLO),
        "gists_url": "%s%s/gists{/gist_id}" % (USER_URL, REPNAME_ACC_CLO),
        "html_url": "https://github.com/%s" % REPNAME_ACC_CLO,
        "subscriptions_url": "%s%s/subscriptions" % (USER_URL, REPNAME_ACC_CLO),
        "node_id": "MDQ6VXNlcjY5NzI1NTU=",
        "test_repos_url": "%s%s/test_repos" % (USER_URL, REPNAME_ACC_CLO),
        "received_events_url": "%s%s/received_events" % (USER_URL, REPNAME_ACC_CLO),
        "gravatar_id": "",
        "starred_url": "%s%s/starred{/owner}{/TEST_REPo}" % (USER_URL, REPNAME_ACC_CLO),
        "site_admin": False,
        "login": "zeroincombenze",
        "type": "User",
        "id": 6972555,
        "followers_url": "%s%s/followers" % (USER_URL, REPNAME_ACC_CLO),
        "organizations_url": "%s%s/orgs" % (USER_URL, REPNAME_ACC_CLO),
    },
    "statuses_url": "%s%s/statuses/{sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "id": 58389936,
    "keys_url": "%s%s/keys{/key_id}" % (ROOT_URL, REPNAME_ACC_CLO),
    "description": "Odoo Accountant closing tools",
    "tags_url": "%s%s/tags" % (ROOT_URL, REPNAME_ACC_CLO),
    "archived": False,
    "downloads_url": "%s%s/downloads" % (ROOT_URL, REPNAME_ACC_CLO),
    "assignees_url": "%s%s/assignees{/user}" % (ROOT_URL, REPNAME_ACC_CLO),
    "contents_url": "%s%s/contents/{+path}" % (ROOT_URL, REPNAME_ACC_CLO),
    "has_pages": False,
    "git_refs_url": "%s%s/git/refs{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "open_issues_count": 0,
    "has_projects": True,
    "clone_url": "%s%s.git" % (ROOT_URL, REPNAME_ACC_CLO),
    "watchers_count": 0,
    "git_tags_url": "%s%s/git/tags{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "milestones_url": "%s%s/milestones{/number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "languages_url": "%s%s/languages" % (ROOT_URL, REPNAME_ACC_CLO),
    "size": 1884706,
    "homepage": "",
    "fork": True,
    "commits_url": "%s%s/commits{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "releases_url": "%s%s/releases{id}" % (ROOT_URL, REPNAME_ACC_CLO),
    "issue_events_url": "%s%s/issues/events{/number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "archive_url": "%s%s/{archive_format}{/ref}" % (ROOT_URL, REPNAME_ACC_CLO),
    "comments_url": "%s%s/comments{number}" % (ROOT_URL, REPNAME_ACC_CLO),
    "events_url": "%s%s/events" % (ROOT_URL, REPNAME_ACC_CLO),
    "contributors_url": "%s%s/contributors" % (ROOT_URL, REPNAME_ACC_CLO),
    "html_url": "%s%s" % (ROOT_URL, REPNAME_ACC_CLO),
    "forks": 0,
    "compare_url": "%s%s/compare/{base}...{ead}" % (ROOT_URL, REPNAME_ACC_CLO),
    "open_issues": 0,
    "node_id": "MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==",
    "git_url": "git://github.com/zeroincombenze/%s.git" % REPNAME_ACC_CLO,
    "svn_url": "%s%s/%s" % (ROOT_URL, REPNAME_ACC_CLO, REPNAME_ACC_CLO),
    "merges_url": "%s%s/merges" % (ROOT_URL, REPNAME_ACC_CLO),
    "has_issues": False,
    "ssh_url": "git@github.com:zeroincombenze/%s.git" % REPNAME_ACC_CLO,
    "blobs_url": "%s%s/git/blobs{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "git_commits_url": "%s%s/git/commits{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "hooks_url": "%s%s/hooks" % (ROOT_URL, REPNAME_ACC_CLO),
    "has_downloads": True,
    "license": {
        "spdx_id": "AGPL-3.0",
        "url": "https://api.github.com/licenses/agpl-3.0",
        "node_id": "MDc6TGljZW5zZTE=",
        "name": "GNU Affero General Public License v3.0",
        "key": "agpl-3.0",
    },
    "name": "%s" % REPNAME_ACC_CLO,
    "language": "Python",
    "url": "%s%s" % (ROOT_URL, REPNAME_ACC_CLO),
    "created_at": "2016-05-09T16:03:20Z",
    "watchers": 0,
    "pushed_at": "2018-06-06T12:58:38Z",
    "forks_count": 0,
    "default_branch": "7.0",
    "teams_url": "%s%s/teams" % (ROOT_URL, REPNAME_ACC_CLO),
    "trees_url": "%s%s/git/trees{/sha}" % (ROOT_URL, REPNAME_ACC_CLO),
    "branches_url": "%s%s/branches{/branch}" % (ROOT_URL, REPNAME_ACC_CLO),
    "subscribers_url": "%s%s/subscribers" % (ROOT_URL, REPNAME_ACC_CLO),
    "stargazers_url": "%s%s/stargazers" % (ROOT_URL, REPNAME_ACC_CLO),
}
REPNAME_L10N_IT = "l10n-italy"
TEST_REP_L10N_IT = {
    "issues_url": "%s%s/issues{/number}" % (ROOT_URL, REPNAME_L10N_IT),
    "deployments_url": "%s%s/deployments" % (ROOT_URL, REPNAME_L10N_IT),
    "stargazers_count": 0,
    "forks_url": "%s%s/forks" % (ROOT_URL, REPNAME_L10N_IT),
    "mirror_url": None,
    "subscription_url": "%s%s/subscription" % (ROOT_URL, REPNAME_L10N_IT),
    "notifications_url": "%s%s/notifications{?since,all,participating}"
    % (ROOT_URL, REPNAME_L10N_IT),
    "collaborators_url": "%s%s/collaborators{collaborator}"
    % (ROOT_URL, REPNAME_L10N_IT),
    "updated_at": "2018-03-29T20:26:20Z",
    "private": False,
    "pulls_url": "%s%s/pulls{/number}" % (ROOT_URL, REPNAME_L10N_IT),
    "disabled": False,
    "issue_comment_url": "%s%s/issues/comments{number}" % (ROOT_URL, REPNAME_L10N_IT),
    "labels_url": "%s%s/labels{/name}" % (ROOT_URL, REPNAME_L10N_IT),
    "has_wiki": True,
    "full_name": "zeroincombenze/%s" % REPNAME_L10N_IT,
    "owner": {
        "following_url": "%s%s/following{other_user}" % (ROOT_URL, REPNAME_L10N_IT),
        "events_url": "%s%s/events{/privacy}" % (ROOT_URL, REPNAME_L10N_IT),
        "avatar_url": "https://avatars2.githubusercontent.com/u/123?v=4",
        "url": "%s%s" % (USER_URL, REPNAME_L10N_IT),
        "gists_url": "%s%s/gists{/gist_id}" % (USER_URL, REPNAME_L10N_IT),
        "html_url": "https://github.com/%s" % REPNAME_L10N_IT,
        "subscriptions_url": "%s%s/subscriptions" % (USER_URL, REPNAME_L10N_IT),
        "node_id": "MDQ6VXNlcjY5NzI1NTU=",
        "test_repos_url": "%s%s/test_repos" % (USER_URL, REPNAME_L10N_IT),
        "received_events_url": "%s%s/received_events" % (USER_URL, REPNAME_L10N_IT),
        "gravatar_id": "",
        "starred_url": "%s%s/starred{/owner}{/TEST_REPo}" % (USER_URL, REPNAME_L10N_IT),
        "site_admin": False,
        "login": "zeroincombenze",
        "type": "User",
        "id": 6972556,
        "followers_url": "%s%s/followers" % (USER_URL, REPNAME_L10N_IT),
        "organizations_url": "%s%s/orgs" % (USER_URL, REPNAME_L10N_IT),
    },
    "statuses_url": "%s%s/statuses/{sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "id": 58389937,
    "keys_url": "%s%s/keys{/key_id}" % (ROOT_URL, REPNAME_L10N_IT),
    "description": "Italy localization",
    "tags_url": "%s%s/tags" % (ROOT_URL, REPNAME_L10N_IT),
    "archived": False,
    "downloads_url": "%s%s/downloads" % (ROOT_URL, REPNAME_L10N_IT),
    "assignees_url": "%s%s/assignees{/user}" % (ROOT_URL, REPNAME_L10N_IT),
    "contents_url": "%s%s/contents/{+path}" % (ROOT_URL, REPNAME_L10N_IT),
    "has_pages": False,
    "git_refs_url": "%s%s/git/refs{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "open_issues_count": 0,
    "has_projects": True,
    "clone_url": "%s%s.git" % (ROOT_URL, REPNAME_L10N_IT),
    "watchers_count": 0,
    "git_tags_url": "%s%s/git/tags{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "milestones_url": "%s%s/milestones{/number}" % (ROOT_URL, REPNAME_L10N_IT),
    "languages_url": "%s%s/languages" % (ROOT_URL, REPNAME_L10N_IT),
    "size": 1884707,
    "homepage": "",
    "fork": True,
    "commits_url": "%s%s/commits{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "releases_url": "%s%s/releases{id}" % (ROOT_URL, REPNAME_L10N_IT),
    "issue_events_url": "%s%s/issues/events{/number}" % (ROOT_URL, REPNAME_L10N_IT),
    "archive_url": "%s%s/{archive_format}{/ref}" % (ROOT_URL, REPNAME_L10N_IT),
    "comments_url": "%s%s/comments{number}" % (ROOT_URL, REPNAME_L10N_IT),
    "events_url": "%s%s/events" % (ROOT_URL, REPNAME_L10N_IT),
    "contributors_url": "%s%s/contributors" % (ROOT_URL, REPNAME_L10N_IT),
    "html_url": "%s%s" % (ROOT_URL, REPNAME_L10N_IT),
    "forks": 0,
    "compare_url": "%s%s/compare/{base}...{ead}" % (ROOT_URL, REPNAME_L10N_IT),
    "open_issues": 0,
    "node_id": "MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==",
    "git_url": "git://github.com/zeroincombenze/%s.git" % REPNAME_L10N_IT,
    "svn_url": "%s%s/%s" % (ROOT_URL, REPNAME_L10N_IT, REPNAME_L10N_IT),
    "merges_url": "%s%s/merges" % (ROOT_URL, REPNAME_L10N_IT),
    "has_issues": False,
    "ssh_url": "git@github.com:zeroincombenze/%s.git" % REPNAME_L10N_IT,
    "blobs_url": "%s%s/git/blobs{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "git_commits_url": "%s%s/git/commits{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "hooks_url": "%s%s/hooks" % (ROOT_URL, REPNAME_L10N_IT),
    "has_downloads": True,
    "license": {
        "spdx_id": "AGPL-3.0",
        "url": "https://api.github.com/licenses/agpl-3.0",
        "node_id": "MDc6TGljZW5zZTE=",
        "name": "GNU Affero General Public License v3.0",
        "key": "agpl-3.0",
    },
    "name": "%s" % REPNAME_L10N_IT,
    "language": "Python",
    "url": "%s%s" % (ROOT_URL, REPNAME_L10N_IT),
    "created_at": "2016-05-09T16:03:20Z",
    "watchers": 0,
    "pushed_at": "2018-06-06T12:58:38Z",
    "forks_count": 0,
    "default_branch": "7.0",
    "teams_url": "%s%s/teams" % (ROOT_URL, REPNAME_L10N_IT),
    "trees_url": "%s%s/git/trees{/sha}" % (ROOT_URL, REPNAME_L10N_IT),
    "branches_url": "%s%s/branches{/branch}" % (ROOT_URL, REPNAME_L10N_IT),
    "subscribers_url": "%s%s/subscribers" % (ROOT_URL, REPNAME_L10N_IT),
    "stargazers_url": "%s%s/stargazers" % (ROOT_URL, REPNAME_L10N_IT),
}


def get_list_from_url(opt_args, git_org):
    def name_is_valid(opt_args, name):
        if (
            (
                not name.startswith(".")
                and not name.startswith("connector-")
                and not name.startswith("maintainer-")
                and not name.startswith("oca-")
                and not name.startswith("odoo-")
                and not name.startswith("vertical-")
                and not name.startswith("l10n-")
                and name not in DEVEL_REPS
            )
            or (name.startswith("connector-") and "connector" in opt_args.extra)
            or (name.startswith("maintainer-") and "maintainer" in opt_args.extra)
            or (name.startswith("oca-") and "oca" in opt_args.extra)
            or (name.startswith("odoo-") and "odoo" in opt_args.extra)
            or (name.startswith("vertical-") and "vertical" in opt_args.extra)
            or (name in DEVEL_REPS and "devel" in opt_args.extra)
            or (name.startswith("l10n-") and name in opt_args.l10n)
        ):
            return True
        return False

    def default_repositories(opt_args, git_org):
        data = []
        if git_org == "odoo":
            data = [
                {"url": "//odoo"},
            ]
        elif git_org == "librerp":
            data = [
                {"url": "//accounting"},
                {"url": "//custom-addons"},
                {"url": "//l10n-italy"},
            ]
        elif git_org == "oca":
            data = [
                {"url": "//account-analytic"},
                {"url": "//account-budgeting"},
                {"url": "//account-closing"},
                {"url": "//account-consolidation"},
                {"url": "//account-financial-reporting"},
                {"url": "//account-financial-tools"},
                {"url": "//account-fiscal-rule"},
                {"url": "//account-invoice-reporting"},
                {"url": "//account-invoicing"},
                {"url": "//account-payment"},
                {"url": "//account-reconcile"},
                {"url": "//apps-store"},
                {"url": "//bank-payment"},
                {"url": "//bank-statement-import"},
                {"url": "//brand"},
                {"url": "//business-requirement"},
                {"url": "//calendar"},
                {"url": "//commission"},
                {"url": "//community-data-files"},
                {"url": "//connector"},
                {"url": "//connector-ecommerce"},
                {"url": "//connector-magento"},
                {"url": "//contract"},
                {"url": "//credit-control"},
                {"url": "//crm"},
                {"url": "//currency"},
                {"url": "//data-protection"},
                {"url": "//ddmrp"},
                {"url": "//delivery-carrier"},
                {"url": "//dms"},
                {"url": "//e-commerce"},
                {"url": "//edi"},
                {"url": "//geospatial"},
                {"url": "//helpdesk"},
                {"url": "//hr"},
                {"url": "//intrastat-extrastat"},
                {"url": "//iot"},
                {"url": "//knowledge"},
                {"url": "//l10n-italy"},
                {"url": "//l10n-switzerland"},
                {"url": "//l10n-usa"},
                {"url": "//maintainer-quality-tools"},
                {"url": "//maintainer-tools"},
                {"url": "//maintenance"},
                {"url": "//management-system"},
                {"url": "//manufacture"},
                {"url": "//manufacture-reporting"},
                {"url": "//margin-analysis"},
                {"url": "//mis-builder"},
                {"url": "//mis-builder-contrib"},
                {"url": "//mgmtsystem"},
                {"url": "//multi-company"},
                {"url": "//OCB"},
                {"url": "//partner-contact"},
                {"url": "//pos"},
                {"url": "//product-attribute"},
                {"url": "//product-kitting"},
                {"url": "//product-pack"},
                {"url": "//product-variant"},
                {"url": "//project"},
                {"url": "//project-agile"},
                {"url": "//project-reporting"},
                {"url": "//purchase-reporting"},
                {"url": "//purchase-workflow"},
                {"url": "//queue"},
                {"url": "//reporting-engine"},
                {"url": "//report-print-send"},
                {"url": "//rma"},
                {"url": "//sale-financial"},
                {"url": "//sale-reporting"},
                {"url": "//sale-workflow"},
                {"url": "//search-engine"},
                {"url": "//server-auth"},
                {"url": "//server-backend"},
                {"url": "//server-brand"},
                {"url": "//server-env"},
                {"url": "//server-tools"},
                {"url": "//server-ux"},
                {"url": "//social"},
                {"url": "//stock-logistics-barcode"},
                {"url": "//stock-logistics-reporting"},
                {"url": "//stock-logistics-tracking"},
                {"url": "//stock-logistics-transport"},
                {"url": "//stock-logistics-warehouse"},
                {"url": "//stock-logistics-workflow"},
                {"url": "//storage"},
                {"url": "//timesheet"},
                {"url": "//vertical-association"},
                {"url": "//vertical-hotel"},
                {"url": "//vertical-isp"},
                {"url": "//web"},
                {"url": "//webhook"},
                {"url": "//webkit-tools"},
                {"url": "//website"},
                {"url": "//website-cms"},
                {"url": "//wms"},
            ]
        elif git_org == "zeroincombenze":
            data = [
                {"url": "//account-closing"},
                {"url": "//account-financial-reporting"},
                {"url": "//account-financial-tools"},
                {"url": "//account-invoicing"},
                {"url": "//account-payment"},
                {"url": "//bank-payment"},
                {"url": "//commission"},
                {"url": "//connector"},
                {"url": "//contract"},
                {"url": "//crm"},
                {"url": "//grymb"},
                {"url": "//knowledge"},
                {"url": "//l10n-italy"},
                {"url": "//l10n-italy-supplemental"},
                {"url": "//management-system"},
                {"url": "//OCB"},
                {"url": "//Odoo-samples"},
                {"url": "//partner-contact"},
                {"url": "//product-attribute"},
                {"url": "//profiles"},
                {"url": "//project"},
                {"url": "//purchase-workflow"},
                {"url": "//report-print-send"},
                {"url": "//reporting-engine"},
                {"url": "//sale-workflow"},
                {"url": "//server-ux"},
                {"url": "//stock-logistics-barcode"},
                {"url": "//stock-logistics-tracking"},
                {"url": "//stock-logistics-workflow"},
                {"url": "//tools"},
                {"url": "//uncovered"},
                {"url": "//VME"},
                {"url": "//zerobug"},
                {"url": "//zerobug-test"},
                {"url": "//zeroincombenze"},
            ]
            if opt_args.odoo_vid == "7.0":
                data.append({"url": "//account_banking_cscs"})
                data.append({"url": "//cscs_addons"})
        return data

    def add_repo(name):
        if opt_args.verbose:
            print(name)
        repositories.append(name)

    fn = os.path.join(
        os.path.dirname(__file__),
        ".%s.dat" % os.path.splitext(os.path.basename(__file__))[0],
    )
    cache = {}
    if os.path.isfile(fn):
        with open(fn, "r") as fd:
            cache = eval(fd.read())
    baseurl = "https://api.github.com/users/%s/repos" % git_org
    branchurl = "https://api.github.com/repos/%s" % git_org
    done_default = False
    page = 0
    repositories = []
    while 1:
        page += 1
        pageurl = "%s?q=addClass+user:mozilla&page=%d" % (baseurl, page)
        if opt_args.verbose:
            print("Acquire data from github.com (page=%d)..." % page)
        if opt_args.dry_run:
            data = [TEST_REP_OCB, TEST_REP_ACC_CLO, TEST_REP_L10N_IT]
            if page > 1:
                data = []
        elif opt_args.def_repo:
            data = []
            if not done_default:
                data = default_repositories(opt_args, git_org)
                done_default = True
        else:
            try:
                response = urlopen(pageurl)
                data = json.loads(response.read())
            except BaseException:
                if (
                    not repositories
                    and git_org in cache
                    and opt_args.odoo_vid in cache[git_org]
                ):
                    break
                data = []
                if not done_default:
                    data = default_repositories(opt_args, git_org)
                    done_default = True
        if not data:
            break
        if opt_args.verbose:
            print("Analyzing received data ...")
        for repos in data:
            name = os.path.basename(repos["url"])
            if name_is_valid(opt_args, name):
                if opt_args.odoo_vid:
                    pageurl = "%s/%s/branches" % (branchurl, name)
                    try:
                        branch_response = urlopen(pageurl)
                        branches = json.loads(branch_response.read())
                    except BaseException:
                        branches = [
                            {"name": "6.1"},
                            {"name": "7.0"},
                            {"name": "8.0"},
                            {"name": "9.0"},
                            {"name": "10.0"},
                            {"name": "11.0"},
                            {"name": "12.0"},
                            {"name": "13.0"},
                            {"name": "14.0"},
                            {"name": "15.0"},
                            {"name": "16.0"},
                        ]
                    if not branches or not any(
                        [x for x in branches if x["name"] == opt_args.odoo_vid]
                    ):
                        continue
                add_repo(name)
            elif opt_args.verbose:
                print("discarded %s" % name)

    if repositories:
        cache[git_org] = cache.get(git_org, {})
        cache[git_org][opt_args.odoo_vid] = repositories
        with open(fn, "w") as fd:
            fd.write(str(cache))
    elif git_org in cache and opt_args.odoo_vid in cache[git_org]:
        repositories = cache[git_org][opt_args.odoo_vid]
    return repositories


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Get repository list from github",
        epilog="© 2019-2023 by SHS-AV s.r.l.",
    )
    parser.add_argument(
        "-b",
        "--odoo-branch",
        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 or 16.0",
        action="store",
        dest="odoo_vid",
    )
    parser.add_argument(
        "-D",
        "--default",
        help="Default repositories",
        action="store_true",
        dest="def_repo",
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
        help="may be: all,none,connector,devel,maintainer,oca,odoo,vertical",
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
    repositories = []
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
        opt_args.extra = "connector,maintainer,oca,odoo,vertical,devel"
    opt_args.extra = opt_args.extra.split(",")
    for git_org in git_orgs:
        repository = get_list_from_url(opt_args, git_org)
        repositories = list(set(repositories) | set(repository))
    if opt_args.return_repos:
        return repositories
    print("Found %d repositories of %s" % (len(repositories), git_orgs))
    print("\t" + " ".join(sorted(repositories)))
    return 0


if __name__ == "__main__":
    exit(main())

