#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018-19 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
from __future__ import print_function, unicode_literals

# from python_plus import b

import sys
import os
import re
from subprocess import Popen
# try:
#     import ConfigParser
# except ImportError:
#     import configparser as ConfigParser
# from unidecode import unidecode
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
# import pdb


__version__ = "1.0.2.5"


def run_traced(*args):
    os0.wlog('>>> %s' % ' '.join(args))
    Popen(args).wait()


def rsync_module(ctx, srcdir, tgtdir, repo, xtgy, src, sub=False):
    b = os.path.basename(tgtdir)
    OCB_SUBDIRS_RE = clodoo.build_odoo_param('OCB_SUBDIRS_RE')
    OCB_SUBDIRS_RE = OCB_SUBDIRS_RE[0: -2] + '|.git|.github)$'
    cmd_rsync_prio = ['rsync', '-a', '--ignore-existing', srcdir, tgtdir]

    if b.endswith('.bak') or b in ('__to_remove', 'setup'):
        return
    elif b.startswith('.git'):
        if src != 'oca':
            run_traced(cmd_rsync_prio)
        elif src == 'oca':
            return


def parse_ctx(ctx):
    regex = '^/.*/tests/res/'
    if re.match(regex, ctx['tgtpath']):
        ctx['test_mode'] = True
        ctx['SAVED_HOME'] = os.environ['HOME']
        x = re.match(regex, ctx['tgtpath'])
        os.putenv('HOME', ctx['tgtpath'][0:x.end()-1])
    else:
        ctx['test_mode'] = False
    ctx['tgt_odoo_dir'] = os.path.dirname(ctx['tgtpath'])
    ctx['odoo_fver'] = clodoo.build_odoo_param(
        'FULLVER', odoo_vid=ctx['tgtpath'], multi=True)
    # TODO: FIX odoo version
    ctx['odoo_fver'] = ctx['odoo_vid']
    # if ctx['odoo_fver'] != ctx['odoo_vid']:
    #     print('Directory %s is %s: not for Odoo %s!' % (
    #         ctx['tgtpath'], ctx['odoo_fver'], ctx['odoo_vid']))
    #     exit(1)
    ctx['repo'] = clodoo.build_odoo_param(
        'REPOS', odoo_vid=ctx['tgtpath'], multi=True)
    return ctx


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Pull repository from OCA",
                                "© 2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        help="may be one of 6.1 7.0 8.0 9.0 10.0 11.0 or 12.0",
                        action='store',
                        dest='odoo_vid')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('tgtpath')
    ctx = parser.parseoptargs(sys.argv[1:])
    # Avoid empty basename when path ends with slash
    ctx['tgtpath'] = os.path.expanduser(ctx['tgtpath'])
    if not os.path.basename(ctx['tgtpath']):
        ctx['tgtpath'] = os.path.dirname(ctx['tgtpath'])
    if not os.path.isdir(ctx['tgtpath']):
        print('Directory %s not found!' % ctx['tgtpath'])
        exit(1)
    if ctx['odoo_vid'] not in (
            '12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1'):
        print('Invalid odoo version')
        exit(1)
    ctx = parse_ctx(ctx)
    print(ctx['repo'])
