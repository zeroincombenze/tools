#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2021 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
import os
import sys
if sys.version_info[0] == 2:
    import urllib2 as urllib3
else:
    import urllib3
import json

try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib

__version__ = '1.0.4'

ROOT_URL = 'https://api.github.com/repos/zeroincombenze/'
USER_URL = 'https://api.github.com/users/'
TEST_REP = 'OCB'
DEVEL_REPS = ['Odoo-samples', 'VME', 'OpenUpgrade', 'dotnet', 'grymb',
              'interface-github', 'odoorpc', 'openupgradelib', 'pylint-odoo',
              'python-plus', 'rest-framework', 'runbot-addons', 'z0bug_odoo',
              'zerobug']
TEST_REP_OCB = {
    'issues_url': '%s%s/issues{/number}' % (ROOT_URL, TEST_REP),
    'deployments_url': '%s%s/deployments' % (ROOT_URL, TEST_REP),
    'stargazers_count': 0,
    'forks_url': '%s%s/forks' % (ROOT_URL, TEST_REP),
    'mirror_url': None,
    'subscription_url': '%s%s/subscription' % (ROOT_URL, TEST_REP),
    'notifications_url':
        '%s%s/notifications{?since,all,participating}' % (
            ROOT_URL, TEST_REP),
    'collaborators_url':
        '%s%s/collaborators{collaborator}' % (ROOT_URL, TEST_REP),
    'updated_at': '2013-07-15T20:26:20Z',
    'private': False,
    'pulls_url': '%s%s/pulls{/number}' % (ROOT_URL, TEST_REP),
    'disabled': False,
    'issue_comment_url':
        '%s%s/issues/comments{number}' % (ROOT_URL, TEST_REP),
    'labels_url': '%s%s/labels{/name}' % (ROOT_URL, TEST_REP),
    'has_wiki': True,
    'full_name': 'zeroincombenze/%s' % TEST_REP,
    'owner': {
        'following_url':
            '%s%s/following{other_user}' % (ROOT_URL, TEST_REP),
        'events_url':
            '%s%s/events{/privacy}' % (ROOT_URL, TEST_REP),
        'avatar_url':
            'https://avatars2.githubusercontent.com/u/234?v=4',
        'url': '%s%s' % (USER_URL, TEST_REP),
        'gists_url': '%s%s/gists{/gist_id}' % (USER_URL, TEST_REP),
        'html_url': 'https://github.com/%s' % TEST_REP,
        'subscriptions_url':
            '%s%s/subscriptions' % (USER_URL, TEST_REP),
        'node_id': 'MDQ6VXNlcjY5NzI1NTU=',
        'test_repos_url': '%s%s/test_repos' % (USER_URL, TEST_REP),
        'received_events_url':
            '%s%s/received_events' % (USER_URL, TEST_REP),
        'gravatar_id': '',
        'starred_url':
            '%s%s/starred{/owner}{/TEST_REPo}' % (USER_URL, TEST_REP),
        'site_admin': False,
        'login': 'zeroincombenze',
        'type': 'User',
        'id': 6972533,
        'followers_url':
            '%s%s/followers' % (USER_URL, TEST_REP),
        'organizations_url': '%s%s/orgs' % (USER_URL, TEST_REP),
    },
    'statuses_url': '%s%s/statuses/{sha}' % (ROOT_URL, TEST_REP),
    'id': 58389479,
    'keys_url':
        '%s%s/keys{/key_id}' % (ROOT_URL, TEST_REP),
    'description': 'Odoo Accountant closing tools',
    'tags_url': '%s%s/tags' % (ROOT_URL, TEST_REP),
    'archived': False,
    'downloads_url': '%s%s/downloads' % (ROOT_URL, TEST_REP),
    'assignees_url': '%s%s/assignees{/user}' % (ROOT_URL, TEST_REP),
    'contents_url':
        '%s%s/contents/{+path}' % (ROOT_URL, TEST_REP),
    'has_pages': False,
    'git_refs_url': '%s%s/git/refs{/sha}' % (ROOT_URL, TEST_REP),
    'open_issues_count': 0,
    'has_projects': True,
    'clone_url': '%s%s.git' % (ROOT_URL, TEST_REP),
    'watchers_count': 0,
    'git_tags_url': '%s%s/git/tags{/sha}' % (ROOT_URL, TEST_REP),
    'milestones_url':
        '%s%s/milestones{/number}' % (ROOT_URL, TEST_REP),
    'languages_url': '%s%s/languages' % (ROOT_URL, TEST_REP),
    'size': 1884251,
    'homepage': '',
    'fork': True,
    'commits_url':
        '%s%s/commits{/sha}' % (ROOT_URL, TEST_REP),
    'releases_url': '%s%s/releases{id}' % (ROOT_URL, TEST_REP),
    'issue_events_url':
        '%s%s/issues/events{/number}' % (ROOT_URL, TEST_REP),
    'archive_url':
        '%s%s/{archive_format}{/ref}' % (ROOT_URL, TEST_REP),
    'comments_url': '%s%s/comments{number}' % (ROOT_URL, TEST_REP),
    'events_url': '%s%s/events' % (ROOT_URL, TEST_REP),
    'contributors_url': '%s%s/contributors' % (ROOT_URL, TEST_REP),
    'html_url': '%s%s' % (ROOT_URL, TEST_REP),
    'forks': 0,
    'compare_url':
        '%s%s/compare/{base}...{ead}' % (ROOT_URL, TEST_REP),
    'open_issues': 0,
    'node_id': 'MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==',
    'git_url':
        'git://github.com/zeroincombenze/%s.git' % TEST_REP,
    'svn_url': '%s%s/%s' % (ROOT_URL, TEST_REP, TEST_REP),
    'merges_url': '%s%s/merges' % (ROOT_URL, TEST_REP),
    'has_issues': False,
    'ssh_url': 'git@github.com:zeroincombenze/%s.git' % TEST_REP,
    'blobs_url': '%s%s/git/blobs{/sha}' % (ROOT_URL, TEST_REP),
    'git_commits_url':
        '%s%s/git/commits{/sha}' % (ROOT_URL, TEST_REP),
    'hooks_url': '%s%s/hooks' % (ROOT_URL, TEST_REP),
    'has_downloads': True,
    'license': {
        'spdx_id': 'AGPL-3.0',
        'url': 'https://api.github.com/licenses/agpl-3.0',
        'node_id': 'MDc6TGljZW5zZTE=',
        'name': 'GNU Affero General Public License v3.0',
        'key': 'agpl-3.0'
    },
    'name': '%s' % TEST_REP,
    'language': 'Python',
    'url': '%s%s' % (ROOT_URL, TEST_REP),
    'created_at': '2016-05-09T16:03:20Z',
    'watchers': 0,
    'pushed_at': '2018-06-06T12:58:38Z',
    'forks_count': 0,
    'default_branch': '7.0',
    'teams_url': '%s%s/teams' % (ROOT_URL, TEST_REP),
    'trees_url': '%s%s/git/trees{/sha}' % (ROOT_URL, TEST_REP),
    'branches_url': '%s%s/branches{/branch}' % (ROOT_URL, TEST_REP),
    'subscribers_url': '%s%s/subscribers' % (ROOT_URL, TEST_REP),
    'stargazers_url': '%s%s/stargazers' % (ROOT_URL, TEST_REP),
}
TEST_REP = 'account-closing'
TEST_REP_ACC_CLO = {
    'issues_url': '%s%s/issues{/number}' % (ROOT_URL, TEST_REP),
    'deployments_url': '%s%s/deployments' % (ROOT_URL, TEST_REP),
    'stargazers_count': 0,
    'forks_url': '%s%s/forks' % (ROOT_URL, TEST_REP),
    'mirror_url': None,
    'subscription_url': '%s%s/subscription' % (ROOT_URL, TEST_REP),
    'notifications_url':
        '%s%s/notifications{?since,all,participating}' % (
            ROOT_URL, TEST_REP),
    'collaborators_url':
        '%s%s/collaborators{collaborator}' % (ROOT_URL, TEST_REP),
    'updated_at': '2018-03-29T20:26:20Z',
    'private': False,
    'pulls_url': '%s%s/pulls{/number}' % (ROOT_URL, TEST_REP),
    'disabled': False,
    'issue_comment_url':
        '%s%s/issues/comments{number}' % (ROOT_URL, TEST_REP),
    'labels_url': '%s%s/labels{/name}' % (ROOT_URL, TEST_REP),
    'has_wiki': True,
    'full_name': 'zeroincombenze/%s' % TEST_REP,
    'owner': {
        'following_url':
            '%s%s/following{other_user}' % (ROOT_URL, TEST_REP),
        'events_url':
            '%s%s/events{/privacy}' % (ROOT_URL, TEST_REP),
        'avatar_url':
            'https://avatars2.githubusercontent.com/u/123?v=4',
        'url': '%s%s' % (USER_URL, TEST_REP),
        'gists_url': '%s%s/gists{/gist_id}' % (USER_URL, TEST_REP),
        'html_url': 'https://github.com/%s' % TEST_REP,
        'subscriptions_url':
            '%s%s/subscriptions' % (USER_URL, TEST_REP),
        'node_id': 'MDQ6VXNlcjY5NzI1NTU=',
        'test_repos_url': '%s%s/test_repos' % (USER_URL, TEST_REP),
        'received_events_url':
            '%s%s/received_events' % (USER_URL, TEST_REP),
        'gravatar_id': '',
        'starred_url':
            '%s%s/starred{/owner}{/TEST_REPo}' % (USER_URL, TEST_REP),
        'site_admin': False,
        'login': 'zeroincombenze',
        'type': 'User',
        'id': 6972555,
        'followers_url':
            '%s%s/followers' % (USER_URL, TEST_REP),
        'organizations_url': '%s%s/orgs' % (USER_URL, TEST_REP),
    },
    'statuses_url': '%s%s/statuses/{sha}' % (ROOT_URL, TEST_REP),
    'id': 58389936,
    'keys_url':
        '%s%s/keys{/key_id}' % (ROOT_URL, TEST_REP),
    'description': 'Odoo Accountant closing tools',
    'tags_url': '%s%s/tags' % (ROOT_URL, TEST_REP),
    'archived': False,
    'downloads_url': '%s%s/downloads' % (ROOT_URL, TEST_REP),
    'assignees_url': '%s%s/assignees{/user}' % (ROOT_URL, TEST_REP),
    'contents_url':
        '%s%s/contents/{+path}' % (ROOT_URL, TEST_REP),
    'has_pages': False,
    'git_refs_url': '%s%s/git/refs{/sha}' % (ROOT_URL, TEST_REP),
    'open_issues_count': 0,
    'has_projects': True,
    'clone_url': '%s%s.git' % (ROOT_URL, TEST_REP),
    'watchers_count': 0,
    'git_tags_url': '%s%s/git/tags{/sha}' % (ROOT_URL, TEST_REP),
    'milestones_url':
        '%s%s/milestones{/number}' % (ROOT_URL, TEST_REP),
    'languages_url': '%s%s/languages' % (ROOT_URL, TEST_REP),
    'size': 1884706,
    'homepage': '',
    'fork': True,
    'commits_url':
        '%s%s/commits{/sha}' % (ROOT_URL, TEST_REP),
    'releases_url': '%s%s/releases{id}' % (ROOT_URL, TEST_REP),
    'issue_events_url':
        '%s%s/issues/events{/number}' % (ROOT_URL, TEST_REP),
    'archive_url':
        '%s%s/{archive_format}{/ref}' % (ROOT_URL, TEST_REP),
    'comments_url': '%s%s/comments{number}' % (ROOT_URL, TEST_REP),
    'events_url': '%s%s/events' % (ROOT_URL, TEST_REP),
    'contributors_url': '%s%s/contributors' % (ROOT_URL, TEST_REP),
    'html_url': '%s%s' % (ROOT_URL, TEST_REP),
    'forks': 0,
    'compare_url':
        '%s%s/compare/{base}...{ead}' % (ROOT_URL, TEST_REP),
    'open_issues': 0,
    'node_id': 'MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==',
    'git_url':
        'git://github.com/zeroincombenze/%s.git' % TEST_REP,
    'svn_url': '%s%s/%s' % (ROOT_URL, TEST_REP, TEST_REP),
    'merges_url': '%s%s/merges' % (ROOT_URL, TEST_REP),
    'has_issues': False,
    'ssh_url': 'git@github.com:zeroincombenze/%s.git' % TEST_REP,
    'blobs_url': '%s%s/git/blobs{/sha}' % (ROOT_URL, TEST_REP),
    'git_commits_url':
        '%s%s/git/commits{/sha}' % (ROOT_URL, TEST_REP),
    'hooks_url': '%s%s/hooks' % (ROOT_URL, TEST_REP),
    'has_downloads': True,
    'license': {
        'spdx_id': 'AGPL-3.0',
        'url': 'https://api.github.com/licenses/agpl-3.0',
        'node_id': 'MDc6TGljZW5zZTE=',
        'name': 'GNU Affero General Public License v3.0',
        'key': 'agpl-3.0'
    },
    'name': '%s' % TEST_REP,
    'language': 'Python',
    'url': '%s%s' % (ROOT_URL, TEST_REP),
    'created_at': '2016-05-09T16:03:20Z',
    'watchers': 0,
    'pushed_at': '2018-06-06T12:58:38Z',
    'forks_count': 0,
    'default_branch': '7.0',
    'teams_url': '%s%s/teams' % (ROOT_URL, TEST_REP),
    'trees_url': '%s%s/git/trees{/sha}' % (ROOT_URL, TEST_REP),
    'branches_url': '%s%s/branches{/branch}' % (ROOT_URL, TEST_REP),
    'subscribers_url': '%s%s/subscribers' % (ROOT_URL, TEST_REP),
    'stargazers_url': '%s%s/stargazers' % (ROOT_URL, TEST_REP),
}


def get_list_from_url(ctx, git_org):

    def name_is_valid(ctx, name):
        if ((not name.startswith('.') and
             not name.startswith('connector-') and
             not name.startswith('maintainer-') and
             not name.startswith('oca-') and
             not name.startswith('odoo-') and
             not name.startswith('vertical-') and
             not name.startswith('l10n-') and
             name not in DEVEL_REPS) or
                (name.startswith('connector-') and
                 'connector' in ctx['extra']) or
                (name.startswith('maintainer-') and
                 'maintainer' in ctx['extra']) or
                (name.startswith('oca-') and
                 'oca' in ctx['extra']) or
                (name.startswith('odoo-') and
                 'odoo' in ctx['extra']) or
                (name.startswith('vertical-') and
                 'vertical' in ctx['extra']) or
                (name in DEVEL_REPS and
                 'devel' in ctx['extra']) or
                (name.startswith('l10n-') and name in ctx['l10n'])):
            return True
        return False

    def add_repo(name):
        if ctx['opt_verbose']:
            print(name)
        repository.append(name)

    fn = os.path.join(
        os.path.dirname(__file__),
        '.%s.dat' % os.path.basename(__file__)[0:-3])
    cache = {}
    if os.path.isfile(fn):
        with open(fn, 'r') as fd:
            cache = eval(fd.read())
    baseurl = 'https://api.github.com/users/%s/repos' % git_org
    branchurl = 'https://api.github.com/repos/%s' % git_org
    done_default = False
    page = 0
    repository = []
    while 1:
        page += 1
        pageurl = '%s?q=addClass+user:mozilla&page=%d' % (baseurl, page)
        if ctx['opt_verbose']:
            print('Acquire data from github.com (page=%d)...' % page)
        if ctx['dry_run']:
            data = [TEST_REP_OCB, TEST_REP_ACC_CLO]
            if page > 1:
                data = []
        else:
            try:
                response = urllib3.urlopen(pageurl)
                data = json.loads(response.read())
            except:
                data = []
                if (not done_default and
                        git_org == 'zeroincombenze' and
                        ctx['odoo_vid'] in ('7.0', '8.0')):
                    done_default = True
                    data = [
                        {'url': '//account-closing'},
                        {'url': '//account-financial-reporting'},
                        {'url': '//account-financial-tools'},
                        {'url': '//account-invoicing'},
                        {'url': '//account-payment'},
                        {'url': '//bank-payment'},
                        {'url': '//commission'},
                        {'url': '//connector'},
                        {'url': '//contract'},
                        {'url': '//crm'},
                        {'url': '//grymb'},
                        {'url': '//knowledge'},
                        {'url': '//l10n-italy'},
                        {'url': '//l10n-italy-supplemental'},
                        {'url': '//maintainer-tools'},
                        {'url': '//management-system'},
                        {'url': '//OCB'},
                        {'url': '//Odoo-samples'},
                        {'url': '//partner-contact'},
                        {'url': '//product-attribute'},
                        {'url': '//project'},
                        {'url': '//purchase-workflow'},
                        {'url': '//python-plus'},
                        {'url': '//report-print-send'},
                        {'url': '//reporting-engine'},
                        {'url': '//sale-workflow'},
                        {'url': '//server-tools'},
                        {'url': '//stock-logistics-barcode'},
                        {'url': '//stock-logistics-tracking'}]
                    if ctx['odoo_vid'] == '7.0':
                        data.append({'url': '//profiles'})
        if not data:
            break
        if ctx['opt_verbose']:
            print('Analyzing received data ...')
        for repos in data:
            name = os.path.basename(repos['url'])
            if name_is_valid(ctx, name):
                if ctx['odoo_vid']:
                    pageurl = '%s/%s/branches' % (branchurl, name)
                    try:
                        branch_response = urllib3.urlopen(pageurl)
                        branches = json.loads(branch_response.read())
                    except:
                        branches = [
                            {'name': '7.0'},
                            {'name': '8.0'},
                            {'name': '9.0'},
                            {'name': '10.0'},
                            {'name': '11.0'},
                            {'name': '12.0'},
                            {'name': '13.0'},
                            {'name': '14.0'},
                        ]
                    if not branches or not any(
                            [x for x in branches
                             if x['name'] == ctx['odoo_vid']]):
                        continue
                add_repo(name)
            elif ctx['opt_verbose']:
                print('discaded %s' % name)

    if repository:
        if git_org == 'zeroincombenze':
            for name in ['uncovered', 'zeroincombenze']:
                if name_is_valid(ctx, name):
                    add_repo(name)
        if git_org == 'zeroincombenze' and ctx['odoo_vid'] == '7.0':
            for name in ['account_banking_cscs', 'cscs_addons']:
                if name_is_valid(ctx, name):
                    add_repo(name)
        cache[git_org] = cache.get(git_org, {})
        cache[git_org][ctx['odoo_vid']] = repository
        with open(fn, 'w') as fd:
            fd.write(str(cache))
    elif git_org in cache and ctx['odoo_vid'] in cache[git_org]:
        repository = cache[git_org][ctx['odoo_vid']]
    return repository


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Get repository list from github.com",
                                "(R) 2019-2021 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument(
        '-b', '--odoo-branch',
        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 or 14.0",
        action='store',
        dest='odoo_vid')
    parser.add_argument('-G', '--git-org',
                        help="select repository",
                        action='store',
                        dest='git_org')
    parser.add_argument('-l', '--local-reps',
                        help="select local repositories",
                        action='store',
                        dest='l10n')
    parser.add_argument('-n')
    parser.add_argument('-O', '--oca',
                        help="repository OCA",
                        action='store_true',
                        dest='oca')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument(
        '-x', '--extra-reps',
        help="may be: all,none,connector,devel,maintainer,oca,odoo,vertical",
        action='store',
        dest='extra')
    parser.add_argument('-Z', '--zeroincombenze',
                        help="repository zeroincombenze",
                        action='store_true',
                        dest='zero')
    ctx = parser.parseoptargs(sys.argv[1:])

    git_orgs = []
    repositories = []
    if ctx['git_org']:
        git_orgs = ctx['git_org'].split(',')
    else:
        if ctx['zero']:
            git_orgs.append('zeroincombenze')
        if ctx['oca']:
            git_orgs.append('OCA')
    if not ctx['l10n']:
        ctx['l10n'] = 'l10n-italy,l10n-italy-supplemental'
    ctx['l10n'] = ctx['l10n'].split(',')
    if not ctx['extra']:
        ctx['extra'] = 'none'
    ctx['extra'] = ctx['extra'].split(',')
    for git_org in git_orgs:
        repository = get_list_from_url(ctx, git_org)
        repositories = list(set(repository) | set(repositories))
    print('Found %d repositories of %s' % (len(repositories), git_orgs))
    print('\t' + ' '.join(sorted(repositories)))
