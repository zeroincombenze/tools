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
try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param


__version__ = "1.0.9"

DATA = {
    'zero6': {
        'dirname': '~/6.1',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo6-server.conf',
    },
    'zero7': {
        'dirname': '~/7.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo7-server.conf',
    },
    'zero8': {
        'dirname': '~/8.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo8-server.conf',
    },
    'zero9': {
        'dirname': '~/9.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo9-server.conf',
    },
    'zero10': {
        'dirname': '~/10.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo10.conf',
    },
    'zero11': {
        'dirname': '~/11.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo11.conf',
    },
    'zero12': {
        'dirname': '~/12.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo12.conf',
    },
    'librerp12': {
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
    },
    'zero13': {
        'dirname': '~/13.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo13.conf',
    },
    'librerp14': {
        'dirname': '~/14.0',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo14.conf',
        'accounting': 'git@github.com:PowERP-cloud',
        'l10n-italy': 'git@github.com:PowERP-cloud',
        'generic': 'git@gitlab.com:powerp1',
        'deploy': 'git@gitlab.com:powerp1',
        'double-trouble': 'git@github.com:LibrERP',
        'custom-addons': 'git@github.com:LibrERP',
        'profiles': '',
        'zerobug-test': 'git@github.com:zeroincombenze',
        'warehouse-logistics-stock': 'git@gitlab.com:/powerp1',
    },
    'zero14': {
        'dirname': '~/14.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo14.conf',
    },
    'zero15': {
        'dirname': '~/15.0',
        'git_org': 'git@github.com:zeroincombenze',
        'conf': 'odoo15.conf',
    },
    'librerp6': {
        'dirname': '~/librerp6',
        'git_org': 'https://github.com/iw3hxn',
        'conf': 'odoo6-librerp.conf',
    },
    'oca7': {
        'dirname': '~/oca7',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo7-oca.conf',
    },
    'oca8': {
        'dirname': '~/oca8',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo8-oca.conf',
    },
    'oca9': {
        'dirname': '~/oca9',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo9-oca.conf',
    },
    'oca10': {
        'dirname': '~/oca10',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo10-oca.conf',
    },
    'oca11': {
        'dirname': '~/oca11',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo11-oca.conf',
    },
    'oca12': {
        'dirname': '~/oca12',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo12-oca.conf',
    },
    'oca13': {
        'dirname': '~/oca13',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo13-oca.conf',
    },
    'oca14': {
        'dirname': '~/oca14',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo14-oca.conf',
        'zerobug-test': '',
    },
    'oca15': {
        'dirname': '~/oca15',
        'git_org': 'https://github.com/OCA',
        'conf': 'odoo15-oca.conf',
    },
}
INVALID_NAMES = ['addons', 'uncovered', 'oca', 'odoo']


def get_repos(hash, update=False):
    repos = []
    dirnames = {}
    with open('/etc/odoo/%s' % DATA[hash]['conf'], 'r') as fd:
        content = fd.read()
    for ln in content.split('\n'):
        if ln.startswith('addons_path'):
            value = ln.split('=')[1].strip()
            for path in value.split(','):
                repo = os.path.basename(path)
                if repo and repo not in INVALID_NAMES:
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
    if update:
        for path in os.listdir(root):
            if os.path.basename(path) in repos:
                continue
            if os.path.isdir(path) and os.path.isdir(os.path.join(path, '.git')):
                repos.append(os.path.basename(path))
    return repos, root


if __name__ == "__main__":
    parser = z0lib.parseoptargs(
        "Pull repository from OCA", "© 2021-22 by SHS-AV s.r.l.", version=__version__
    )
    parser.add_argument('-h')
    parser.add_argument(
        '-b',
        '--odoo-branch',
        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 or 15.0",
        action='store',
        dest='odoo_vid',
    )
    parser.add_argument(
        '-G',
        '--git-org',
        help="may be one of zero librerp or oca",
        action='store',
        dest='git_org',
    )
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-U', '--update', action='store_true', dest='update')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-y', '--assume-yes', action='store_true', dest='assume_yes')
    ctx = parser.parseoptargs(sys.argv[1:])
    odoo_version = build_odoo_param('FULLVER', odoo_vid=ctx['odoo_vid'], multi=True)
    if odoo_version not in (
        '15.0',
        '14.0',
        '13.0',
        '12.0',
        '11.0',
        '10.0',
        '9.0',
        '8.0',
        '7.0',
        '6.1',
    ):
        print('Invalid odoo version')
        exit(1)
    if ctx['git_org'] not in ('zero', 'oca', 'librerp'):
        ctx['git_org'] = build_odoo_param(
            'GIT_ORGID', odoo_vid=ctx['odoo_vid'], multi=True
        )
    if ctx['git_org'] not in ('zero', 'oca', 'librerp'):
        print('Invalid git organization')
        exit(1)
    hash_id = ctx['git_org'] + odoo_version.split('.')[0]
    if hash_id not in DATA:
        print('Invalid version %s or git-org %s' % (ctx['odoo_vid'], ctx['git_org']))
    repos, root = get_repos(hash_id, update=ctx['update'])
    for repo in ['OCB'] + sorted(repos):
        if repo in DATA[hash_id]:
            git_url = DATA[hash_id][repo]
        else:
            git_url = DATA[hash_id]['git_org']
        if not git_url:
            continue
        if repo in ('OCB', 'odoo'):
            git_url = '%s/%s.git' % (git_url, repo)
            tgtdir = root
        else:
            git_url = '%s/%s.git' % (git_url, repo)
            tgtdir = os.path.join(root, repo)
        if os.path.isdir(tgtdir):
            if not ctx['update']:
                if not ctx['assume_yes']:
                    print('Repo %s already exists!' % tgtdir)
                    dummy = input('Delete (y/n)? ')
                    if not dummy.lower().startswith('y'):
                        continue
                print('rm -fR %s' % tgtdir)
                shutil.rmtree(tgtdir)
        if os.path.isdir(tgtdir):
            print('$ cd %s' % tgtdir)
            os.chdir(tgtdir)
            cmd = 'git stash'
            print('$ %s' % cmd)
            if not ctx['dry_run']:
                os.system(cmd)
            cmd = 'git checkout %s &>/dev/null' % ctx['odoo_vid']
            print('$ %s' % cmd)
            sts = os.system(cmd)
            if sts:
                print('Invalid branch %s' % ctx['odoo_vid'])
                cmd = 'git checkout %s &>/dev/null' % odoo_version
                print('$ %s' % cmd)
                os.system(cmd)
            cmd = 'git pull'
        else:
            if os.getcwd() != root:
                os.chdir(root)
                print('$ cd %s' % os.getcwd())
            if git_url.startswith('git'):
                opts = '-b %s' % ctx['odoo_vid']
            else:
                opts = '-b %s --single-branch --depth=1' % ctx['odoo_vid']
            if opts:
                cmd = 'git clone %s %s/ %s' % (git_url, repo, opts)
            else:
                cmd = 'git clone %s %s/' % (git_url, repo)
        print('$ %s' % cmd)
        if not ctx['dry_run']:
            sts = os.system(cmd)
            os.system('git branch')
            if sts:
                print('*** Error ***')
                dummy = input('Press RET to continue ...')
