#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Run odoo server to export translation
"""

# import pdb
import os
import sys
import csv
# import re
from z0lib import parseoptargs


__version__ = "0.1.0"
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0')


def transodoo_list(ctx):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    for t in mindroot:
        print '%-20.20s %-20.20s\n    %s' % (t.split('.')[0],
                                             t.split('.')[1],
                                             mindroot[t])


def transodoo_build(ctx):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    model = ''
    while True:
        while not model:
            model = raw_input('Model (type END to end): ')
        if model.upper() == 'END':
            ctx['mindroot'] = mindroot
            return 0
        model = model.replace('.', '_').lower()
        name = ''
        while not name:
            name = raw_input('Name (type END to end): ').upper()
        if name == 'END':
            ctx['mindroot'] = mindroot
            return 0
        kk = model + '.' + name
        if kk not in mindroot:
            mindroot[kk] = {}
        def_term = name.lower()
        for vers in VERSIONS:
            term = ''
            while not term:
                term = raw_input('Term[%s] (def=%s): ' % (vers, def_term))
                if not term:
                    term = def_term
                else:
                    def_term = term
            mindroot[kk][vers] = term
        print mindroot


def translate_from_to(ctx, model, source, src_ver, tgt_ver):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    if src_ver not in VERSIONS:
        print 'Invalid source version!'
        return ''
    if tgt_ver not in VERSIONS:
        print 'Invalid target version!'
        return ''
    model = model.replace('.', '_').lower()
    name = ''
    for t in mindroot:
        if t.find(model) == 0 and source == mindroot[t][src_ver]:
            name = mindroot[t][tgt_ver]
            break
    return name


def translate_from_sym(ctx, model, sym, tgt_ver):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    if tgt_ver not in VERSIONS:
        print 'Invalid target version!'
        return ''
    model = model.replace('.', '_').lower()
    kk = model + '.' + sym.upper()
    name = ''
    if kk in mindroot:
        name = mindroot[kk][tgt_ver]
    return name


def read_stored_dict(ctx):
    csv.register_dialect('transodoo',
                         delimiter='\t',
                         quotechar='\"',
                         quoting=csv.QUOTE_MINIMAL)
    if 'dict_fn' not in ctx or not ctx['dict_fn']:
        p = os.path.dirname(__file__) or '.'
        if os.path.isfile('%s/transodoo.csv' % p):
            ctx['dict_fn'] = '%s/transodoo.csv' % p
        elif os.path.isfile('~/dev/transodoo.csv'):
            ctx['dict_fn'] = '~/dev/transodoo.csv'
        else:
            ctx['dict_fn'] = 'transodoo.csv'
    mindroot = {}
    with open(ctx['dict_fn'], 'rb') as f:
        hdr = False
        reader = csv.DictReader(f,
                                fieldnames=[],
                                restkey='undef_name',
                                dialect='transodoo')
        for line in reader:
            if not hdr:
                hdr = True
                continue
            row = line['undef_name']
            kk = row[0].replace('.', '_').lower() + '.' + row[1]
            mindroot[kk] = {}
            i = 1
            for vers in VERSIONS:
                i += 1
                mindroot[kk][vers] = row[i]
    ctx['mindroot'] = mindroot


def write_stored_dict(ctx):
    csv.register_dialect('transodoo',
                         delimiter='\t',
                         quotechar='\"',
                         quoting=csv.QUOTE_MINIMAL)
    if 'dict_fn' not in ctx or not ctx['dict_fn']:
        p = os.path.dirname(__file__) or '.'
        if os.path.isfile('%s/transodoo.csv' % p):
            ctx['dict_fn'] = '%s/transodoo.csv' % p
        elif os.path.isfile('~/dev/transodoo.csv'):
            ctx['dict_fn'] = '~/dev/transodoo.csv'
        else:
            ctx['dict_fn'] = 'transodoo.csv'
    with open(ctx['dict_fn'], 'wb') as f:
        writer = csv.DictWriter(f,
                                fieldnames=('model', 'name')+VERSIONS,
                                dialect='transodoo')
        writer.writeheader()
        mindroot = ctx['mindroot']
        for kk in mindroot:
            line = mindroot[kk]
            line['model'] = kk.split('.')[0]
            line['name'] = kk.split('.')[1]
            writer.writerow(line)


def transodoo(ctx=None):
    if ctx['action'] == 'build':
        read_stored_dict(ctx)
        transodoo_build(ctx)
        write_stored_dict(ctx)
        return 0
    elif ctx['action'] == 'list':
        read_stored_dict(ctx)
        transodoo_list(ctx)
    elif ctx['action'] == 'test':
        read_stored_dict(ctx)
        for vers in VERSIONS:
            name = translate_from_sym(ctx, 'res.groups', 'SALES', vers)
            print 'SALES = %s[%s]' % (name,
                                      vers)
        source = 'Sales'
        for vers in VERSIONS:
            name = translate_from_to(ctx, 'res.groups', source, '7.0', vers)
            print 'Source=%s[%s] => Target=%s[%s]' % (source,
                                                      '7.0',
                                                      name,
                                                      vers)
    else:
        print "Invalid action!"
        return 1
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Transodoo",
                          "© 2017-2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--branch',
                        action='store',
                        dest='odoo_ver',
                        default='10.0')
    parser.add_argument('-l', '--language',
                        action='store',
                        dest='opt_lang',
                        default='it_IT')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('action',
                        help='build')
    ctx = parser.parseoptargs(sys.argv[1:])
    sts = transodoo(ctx=ctx)
    exit(sts)
