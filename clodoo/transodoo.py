#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Run odoo server to export translation
"""

import csv
# import pdb
import os
import sys

# import re
from z0lib import parseoptargs


__version__ = "0.3.6.10"
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0')


def get_key1(model, sym):
    kk = model.replace('.', '_').lower()
    if sym:
        kk += '.' + sym.upper()
    return kk


def get_key2(model, name):
    kk = model.replace('.', '_').lower()
    if name:
        kk += '.' + name
    return kk


def set_alias(mindroot, model, name, key):
    k1 = get_key1(model, name)
    if k1 not in mindroot:
        mindroot[k1] = {}
    if key:
        k2 = get_key2(model, key)
        if k2 not in mindroot:
            mindroot[k2] = {}
        mindroot[k2]['0'] = k1
    return mindroot


def transodoo_list(ctx):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    for t in mindroot:
        if t.split('.')[0] == ctx['model']:
            line = '%s %s\n' % (t.split('.')[0],
                                t.split('.')[1])
            for vers in VERSIONS:
                if not ctx['odoo_ver'] or vers == ctx['odoo_ver']:
                    line += ' - [%s]="%s"\n' % (vers, mindroot[t][vers])
            print line


def transodoo_edit(ctx):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    model = get_key1(ctx['model'], '')
    while True:
        while not model:
            m = raw_input('Model (def=%s, type END to end): ' % model)
            if m.upper() == 'END':
                ctx['mindroot'] = mindroot
                return 0
            if m:
                model = get_key1(model, '')
        name = ctx['sym']
        while not name:
            name = raw_input(
                'Symbolic name (def=%s, type END to end): ' % name).upper()
        if name == 'END':
            ctx['mindroot'] = mindroot
            return 0
        key = ctx['opt_key']
        while not key:
            key = raw_input(
                'Name of field (def=%s, type END to end): ' % key).upper()
        if key == 'END':
            ctx['mindroot'] = mindroot
            return 0
        mindroot = set_alias(mindroot, model, name, key)
        k1 = get_key1(model, name)
        def_term = name.lower()
        print "Model %s, sym=%s, key=%s" % (model, name, key)
        for vers in VERSIONS:
            term = ''
            while not term:
                if vers in mindroot[k1]:
                    def_term = mindroot[k1][vers]
                term = raw_input(
                    'Term[%s] (def=%s, blank=\\b, END to end): ' % (vers,
                                                                    def_term))
                if term == 'END':
                    ctx['mindroot'] = mindroot
                    return 0
                if not term:
                    term = def_term
                elif term == r'\b':
                    term = ''
                elif term != r'\N':
                    def_term = term
            mindroot[k1][vers] = term
        print mindroot[k1]


def translate_from_to(ctx, model, key, src_name, src_ver, tgt_ver):
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
    name = src_name
    k2 = get_key2(model, key)
    if k2 in mindroot:
        k1 = mindroot[k2]['0']
        name = mindroot[k1][tgt_ver]
    return name


def translate_from_sym(ctx, model, sym, tgt_ver):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    if tgt_ver not in VERSIONS:
        print 'Invalid target version!'
        return ''
    k1 = get_key1(model, sym)
    name = ''
    if k1 in mindroot:
        name = mindroot[k1][tgt_ver]
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
            row = line['undef_name']
            if not hdr:
                MODEL = 0
                NAME = 1
                KEY = -1
                V6 = 2
                for i in (0, 1, 2):
                    if row[i] == 'model':
                        MODEL = i
                    elif row[i] == 'name':
                        NAME = i
                    elif row[i] == 'key':
                        KEY = i
                        V6 = 3
                hdr = True
                continue
            if KEY < 0:
                mindroot = set_alias(mindroot, row[MODEL], row[NAME], '')
            else:
                mindroot = set_alias(mindroot, row[MODEL], row[NAME], row[KEY])
            k1 = get_key1(row[MODEL], row[NAME])
            i = V6 - 1
            for vers in VERSIONS:
                i += 1
                if i >= len(row):
                    mindroot[k1][vers] = row[i - 1]
                else:
                    mindroot[k1][vers] = row[i]
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
                                fieldnames=('model', 'name', 'key') + VERSIONS,
                                dialect='transodoo')
        writer.writeheader()
        mindroot = ctx['mindroot']
        for k1 in mindroot:
            line = mindroot[k1]
            if '0' not in line:
                line['model'] = k1.split('.')[0]
                line['name'] = k1.split('.')[1]
                line['key'] = ''
                for k2 in mindroot:
                    if '0' in mindroot[k2]:
                        if mindroot[k2]['0']:
                            line['key'] = k2.split('.')[1]
                            break
                writer.writerow(line)


def transodoo(ctx=None):
    if ctx['action'] == 'edit':
        read_stored_dict(ctx)
        transodoo_edit(ctx)
        write_stored_dict(ctx)
        return 0
    elif ctx['action'] == 'list':
        read_stored_dict(ctx)
        transodoo_list(ctx)
    elif ctx['action'] == 'translate':
        read_stored_dict(ctx)
        if ctx['oe_from_ver']:
            print translate_from_to(ctx,
                                    ctx['model'],
                                    ctx['opt_key'],
                                    ctx['sym'],
                                    ctx['oe_from_ver'],
                                    ctx['odoo_ver'])
        else:
            print translate_from_sym(ctx,
                                     ctx['model'],
                                     ctx['sym'],
                                     ctx['odoo_ver'])
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
                        default='')
    parser.add_argument('-f', '--from-branch',
                        action='store',
                        dest='oe_from_ver',
                        default='')
    parser.add_argument('-k', '--key',
                        action='store',
                        dest='opt_key',
                        default='')
    parser.add_argument('-l', '--language',
                        action='store',
                        dest='opt_lang',
                        default='it_IT')
    parser.add_argument('-m', '--model',
                        action='store',
                        dest='model',
                        default='res.groups')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-s', '--symbol',
                        action='store',
                        dest='sym',
                        default='')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('action',
                        help='edit,list,translate,test')
    ctx = parser.parseoptargs(sys.argv[1:])
    ctx['model'] = ctx['model'].replace('.', '_').lower()
    if ctx['odoo_ver']:
        if ctx['odoo_ver'] not in VERSIONS:
            print 'Invalid version %s!\nUse one of %s' % (ctx['odoo_ver'],
                                                          VERSIONS)
            sys.exit(1)
    if ctx['oe_from_ver']:
        if ctx['oe_from_ver'] not in VERSIONS:
            print 'Invalid version %s!\nUse one of %s' % (ctx['odoo_ver'],
                                                          VERSIONS)
            sys.exit(1)
    sts = transodoo(ctx=ctx)
    exit(sts)
