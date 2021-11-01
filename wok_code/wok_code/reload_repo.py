#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018-21 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
from __future__ import print_function, unicode_literals
from builtins import input

import sys
import os
import shutil
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib
# import pdb


__version__ = "1.0.2.7"

DATA = {
    'powerp12': {
        'dirname': '~/12.0',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo12.conf',
        'accounting': 'git@github.com:PowERP-cloud',
        'l10n-italy': 'git@github.com:PowERP-cloud',
        'generic': 'git@gitlab.com:powerp1',
        'deploy': 'git@gitlab.com:powerp1',
        'double-trouble': 'git@github.com:LibrERP',
        'custom-addons': 'git@github.com:LibrERP',
        'addons_kalamitica': '',
        'connector-prestashop': 'https://github.com/LibrERP',
        'profiles': '',
        'zerobug-test': 'git@github.com:zeroincombenze',
        'warehouse-logistics-stock': 'git@gitlab.com:/powerp1',
    }
}
INVALID_NAMES = ['addons', 'uncovered']


def get_repos(ctx):
    repos = []
    with open('/etc/odoo/%s' % DATA[hash]['conf'], 'r') as fd:
        content = fd.read()
    for ln in content.split('\n'):
        if ln.startswith('addons_path'):
            value = ln.split('=')[1].strip()
            for path in value.split(','):
                module = os.path.basename(path)
                if module and module not in INVALID_NAMES:
                    repos.append(module)
            break
    return repos


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Pull repository from OCA",
                                "© 2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument(
        '-b', '--odoo-branch',
        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 or 15.0",
        action='store',
        dest='odoo_vid')
    parser.add_argument(
        '-G', '--git-org',
        help="may be one of zero powerp librerp or oca",
        action='store',
        dest='git_org')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument(
        '-U', '--update',
        action='store_true',
        dest='update')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument(
        '-y', '--assume-yes',
        action='store_true',
        dest='assume_yes')
    ctx = parser.parseoptargs(sys.argv[1:])
    # pdb.set_trace()
    if ctx['odoo_vid'] not in (
            '15.0', '14.0', '13.0', '12.0', '11.0',
            '10.0', '9.0', '8.0', '7.0', '6.1'):
        print('Invalid odoo version')
        exit(1)
    if ctx['git_org'] not in (
            'zero', 'powerp', 'oca', 'librerp'):
        print('Invalid git organization')
        exit(1)
    hash = ctx['git_org'] + ctx['odoo_vid'].split('.')[0]
    if hash not in DATA:
        print('Invalid version %s or git-org %s' % (ctx['odoo_vid'],
                                                    ctx['git_org']))
    repos = get_repos(ctx)
    root = os.path.expanduser(DATA[hash]['dirname'])
    for repo in repos:
        if os.getcwd() != root:
            os.chdir(root)
            print('$ cd %s' % os.getcwd())
        if repo in DATA[hash]:
            git_url = DATA[hash][repo]
        else:
            git_url = DATA[hash]['git_org']
        if not git_url:
            continue
        git_url = '%s/%s.git' % (git_url, repo)
        tgtdir = os.path.join(root, repo)
        if os.path.isdir(repo):
            if not ctx['update'] and not ctx['assume_yes']:
                print('Repo %s already exists!' % repo)
                dummy = input('Delete (y/n)? ')
                if not dummy.lower().startswith('y'):
                    continue
                print('rm -fR %s' % repo)
                shutil.rmtree(repo)
        if os.path.isdir(repo):
            print('$ cd %s' % tgtdir)
            os.chdir(tgtdir)
            cmd = 'git stash'
            print('$ %s' % cmd)
            os.system(cmd)
            #TODO
            cmd = 'git checkout 12.0-devel'
            print('$ %s' % cmd)
            sts = os.system(cmd)
            if sts:
                cmd = 'git checkout 12.0_devel'
                print('$ %s' % cmd)
                sts = os.system(cmd)
            cmd = 'git pull'
        else:
            if git_url.startswith('git'):
                opts = ''
                if ctx['git_org'] != 'powerp':
                    opts ='-b %s' % ctx['odoo_vid']
            else:
                opts = '-b %s --single-branch --depth=1' % ctx['odoo_vid']
            if opts:
                cmd = 'git clone %s %s/ %s' % (git_url, repo, opts)
            else:
                cmd = 'git clone %s %s/' % (git_url, repo)
        print('$ %s' % cmd)
        os.system(cmd)
