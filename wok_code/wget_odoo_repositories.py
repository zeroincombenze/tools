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

from os0 import os0

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
        repository = ['account_banking_cscs', 'cscs_addons', 'didotech_80', 'l10n-italy-supplemental ',
                      'profiles', 'uncovered', 'zerobug-test', 'zeroincombenze']
    else:
        repository = []

    while 1:
        page += 1
        pageurl = '%s?q=addClass+user:mozilla&page=%d' % (baseurl, page)
        print('Acquire data from github.com (page=%d)...' % page)
        # response = urllib2.urlopen(pageurl)
        # data = json.loads(response.read())
        data = {}
        if not data:
            break
        print('Analyzing received data ...')
        for repos in data:
            name = os.path.basename(repos['url'])
            print(name)
            if not name.startswith('l10n-') or name == 'l10n-it':
                repository.append(name)
    return repository


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Get repository list from github.com",
                                "® 2019-2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 or 12.0",
                        action='store',
                        dest='odoo_vid')
    parser.add_argument('-n')
    parser.add_argument('-O', '--no-oca',
                        help="no repository OCA",
                        action='store',
                        dest='no_oca')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-Z', '--no-zero',
                        help="no repository zeroincombenze",
                        action='store',
                        dest='no_zero')
    ctx = parser.parseoptargs(sys.argv[1:])

    repository_zero = repository_oca = []
    if not ctx['no_zero']:
        repository_zero = get_list_from_url(ctx, 'zeroincombenze')
    if not ctx['no_oca']:
        repository_oca = get_list_from_url(ctx, 'OCA')
    repository = repository_zero + repository_oca
    print('Found %d repositories' % len(repository))
    print('\t' + ' '.join(sorted(repository)))
