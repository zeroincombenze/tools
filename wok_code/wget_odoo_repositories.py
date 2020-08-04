#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
import os
import sys
import urllib2
import json

try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib

__version__ = ''


def get_list_from_url(ctx, git_org):
    baseurl = 'https://api.github.com/users/%s/repos' % git_org
    page = 0
    if git_org == 'zeroincombenze':
        repository = ['account_banking_cscs', 'cscs_addons', 'didotech_80',
                      'l10n-italy-supplemental ', 'profiles', 'uncovered',
                      'zerobug-test', 'zeroincombenze']
    else:
        repository = []

    while 1:
        page += 1
        pageurl = '%s?q=addClass+user:mozilla&page=%d' % (baseurl, page)
        if ctx['opt_verbose']:
            print('Acquire data from github.com (page=%d)...' % page)
        if ctx['dry_run']:
            root_url = 'https://api.github.com/repos/zeroincombenze/'
            user_url = 'https://api.github.com/users/'
            rep = 'account-closing'
            data = [
                {
                    'issues_url': '%s%s/issues{/number}' % (root_url, rep),
                    'deployments_url': '%s%s/deployments' % (root_url, rep),
                    'stargazers_count': 0,
                    'forks_url': '%s%s/forks' % (root_url, rep),
                    'mirror_url': None,
                    'subscription_url': '%s%s/subscription' % (root_url, rep),
                    'notifications_url':
                         '%s%s/notifications{?since,all,participating}' % (
                             root_url, rep),
                    'collaborators_url':
                         '%s%s/collaborators{collaborator}' % (root_url, rep),
                    'updated_at': '2018-03-29T20:26:20Z',
                    'private': False,
                    'pulls_url': '%s%s/pulls{/number}' % (root_url, rep),
                    'disabled': False,
                    'issue_comment_url':
                        '%s%s/issues/comments{number}' % (root_url, rep),
                    'labels_url': '%s%s/labels{/name}' % (root_url, rep),
                    'has_wiki': True,
                    'full_name': 'zeroincombenze/%s' % rep,
                    'owner': {
                        'following_url':
                            '%s%s/following{other_user}' % (root_url, rep),
                        'events_url':
                            '%s%s/events{/privacy}' % (root_url, rep),
                        'avatar_url':
                            'https://avatars2.githubusercontent.com/u/123?v=4',
                        'url': '%s%s' % (user_url, rep),
                        'gists_url': '%s%s/gists{/gist_id}' % (user_url, rep),
                        'html_url': 'https://github.com/%s' % rep,
                        'subscriptions_url':
                            '%s%s/subscriptions' % (user_url, rep),
                        'node_id': 'MDQ6VXNlcjY5NzI1NTU=',
                        'repos_url': '%s%s/repos' % (user_url, rep),
                         'received_events_url':
                             '%s%s/received_events' % (user_url, rep),
                        'gravatar_id': '',
                        'starred_url':
                            '%s%s/starred{/owner}{/repo}' % (user_url, rep),
                        'site_admin': False,
                        'login': 'zeroincombenze',
                        'type': 'User',
                        'id': 6972555,
                         'followers_url':
                             '%s%s/followers' % (user_url, rep),
                        'organizations_url': '%s%s/orgs' % (user_url, rep),
                    },
                    'statuses_url': '%s%s/statuses/{sha}' % (root_url, rep),
                    'id': 58389936,
                    'keys_url':
                        '%s%s/keys{/key_id}' % (root_url, rep),
                    'description': 'Odoo Accountant closing tools',
                    'tags_url': '%s%s/tags' % (root_url, rep),
                    'archived': False,
                    'downloads_url': '%s%s/downloads' % (root_url, rep),
                    'assignees_url': '%s%s/assignees{/user}' % (root_url, rep),
                    'contents_url':
                         '%s%s/contents/{+path}' % (root_url, rep),
                    'has_pages': False,
                    'git_refs_url': '%s%s/git/refs{/sha}' % (root_url, rep),
                    'open_issues_count': 0,
                    'has_projects': True,
                    'clone_url': '%s%s.git' % (root_url, rep),
                    'watchers_count': 0,
                    'git_tags_url': '%s%s/git/tags{/sha}' % (root_url, rep),
                    'milestones_url':
                        '%s%s/milestones{/number}' % (root_url, rep),
                    'languages_url': '%s%s/languages' % (root_url, rep),
                    'size': 1884706,
                    'homepage': '',
                    'fork': True,
                    'commits_url':
                        '%s%s/commits{/sha}' % (root_url, rep),
                    'releases_url': '%s%s/releases{id}' % (root_url, rep),
                    'issue_events_url':
                        '%s%s/issues/events{/number}' % (root_url, rep),
                    'archive_url':
                        '%s%s/{archive_format}{/ref}' % (root_url, rep),
                    'comments_url': '%s%s/comments{number}' % (root_url, rep),
                    'events_url': '%s%s/events' % (root_url, rep),
                    'contributors_url': '%s%s/contributors' % (root_url, rep),
                    'html_url': '%s%s' % (root_url, rep),
                    'forks': 0,
                    'compare_url':
                        '%s%s/compare/{base}...{ead}' % (root_url, rep),
                    'open_issues': 0,
                    'node_id': 'MDEwOlJlcG9zaXRvcnk1ODM4OTkzNg==',
                    'git_url':
                        'git://github.com/zeroincombenze/%s.git' % rep,
                    'svn_url': '%s%s/%s' % (root_url, rep, rep),
                    'merges_url': '%s%s/merges' % (root_url, rep),
                    'has_issues': False,
                    'ssh_url': 'git@github.com:zeroincombenze/%s.git' % rep,
                    'blobs_url': '%s%s/git/blobs{/sha}' % (root_url, rep),
                    'git_commits_url':
                        '%s%s/git/commits{/sha}' % (root_url, rep),
                    'hooks_url': '%s%s/hooks' % (root_url, rep),
                    'has_downloads': True,
                    'license': {
                        'spdx_id': 'AGPL-3.0',
                        'url': 'https://api.github.com/licenses/agpl-3.0',
                        'node_id': 'MDc6TGljZW5zZTE=',
                        'name': 'GNU Affero General Public License v3.0',
                        'key': 'agpl-3.0'
                    },
                    'name': '%s' % rep,
                    'language': 'Python',
                    'url': '%s%s' % (root_url, rep),
                    'created_at': '2016-05-09T16:03:20Z',
                    'watchers': 0,
                    'pushed_at': '2018-06-06T12:58:38Z',
                    'forks_count': 0,
                    'default_branch': '7.0',
                    'teams_url': '%s%s/teams' % (root_url, rep),
                    'trees_url': '%s%s/git/trees{/sha}' % (root_url, rep),
                    'branches_url': '%s%s/branches{/branch}' % (root_url, rep),
                    'subscribers_url': '%s%s/subscribers' % (root_url, rep),
                    'stargazers_url': '%s%s/stargazers' % (root_url, rep),
                },
            ]
            if page > 1:
                data = []
        else:
            response = urllib2.urlopen(pageurl)
            data = json.loads(response.read())
        if not data:
            break
        if ctx['opt_verbose']:
            print('Analyzing received data ...')
        for repos in data:
            name = os.path.basename(repos['url'])
            if ctx['opt_verbose']:
                print(name)
            if not name.startswith('l10n-') or name == 'l10n-it':
                repository.append(name)
    return repository


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Get repository list from github.com",
                                "(R) 2019-2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument(
        '-b', '--odoo-branch',
        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 or 13.0",
        action='store',
        dest='odoo_vid')
    parser.add_argument('-G', '--git-org',
                        help="select repository",
                        action='store',
                        dest='git_org')
    parser.add_argument('-n')
    parser.add_argument('-O', '--oca',
                        help="repository OCA",
                        action='store_true',
                        dest='oca')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
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
    for git_org in git_orgs:
        repository = get_list_from_url(ctx, git_org)
        repositories = list(set(repository) | set(repositories))
    print('Found %d repositories of %s' % (len(repositories), git_orgs))
    print('\t' + ' '.join(sorted(repositories)))
