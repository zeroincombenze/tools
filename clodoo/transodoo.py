#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Translate Odoo name to migrate from version to another
Structure:
[pymodel]:       Odoo model name
[pymodel][ttype]: may be:
    name:    symbolic name of a field (deprecated)
    field:   field name to translate
    action:  action/function to translate
    module:  module name to translate
    merge:   module name merged with
    value:   value of field to translate (name is the field name)

[pymodel][ttype][hash]           hash entry with name.ver list
[pymodel][ttype][hash][ver.name] value for specific version
[pymodel][ttype][ver.name]       specific name entry for name.ver -> hash

the ttype 'value' has a more level for every field name:
[pymodel]['value'][fldname][hash]
[pymodel]['value'][fldname][hash][ver.name]
[pymodel]['value'][fldname][ver.name]
"""
from __future__ import print_function, unicode_literals
from builtins import input
from past.builtins import basestring
from python_plus import _c

import re
import csv
import os
import sys
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib

__version__ = "0.3.28.17"
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0')
CVT_ACC_TYPE_OLD_NEW = {
    'Bank': 'Bank and Cash',
    'Cash': 'Bank and Cash',
    'Check': 'Credit Card',
    'Asset': 'Current Assets',
    'Liability': 'Current Liabilities',
    'Tax': 'Current Liabilities',
}
CVT_ACC_TYPE_NEW_OLD = {
    'Bank and Cash': 'Bank',
    'Credit Card': 'Check',
    'Current Assets': 'Asset',
    'Non-current Assets': 'Asset',
    'Fixed Asset': 'Asset',
    'Current Liabilities': 'Liability',
    'Non-current Liabilities': 'Liability',
    'Other Income': 'Income',
    'Depreciation': 'Expense',
    'Cost of Revenue': 'Expense',
    'Prepayments': 'Expense',
    'Current Year Earnings': 'Expense',
}


def get_pymodel(model):
    # return model.replace('.', '_').lower()
    return model


def get_ver_name(name, ver):
    if name:
        return '%s__%s' % (ver, name)
    return name


def is_hash(name):
    if re.match(r'^[0-9]+\.[0-9]+__', name):
        return False
    return True


def set_hash(ttype, name, ver_names):
    if ttype == 'name':
        return name.upper()
    prior_name = ''
    key = name if ttype == 'value' else ''
    for i, ver in enumerate(VERSIONS):
        if ver_names[i] and ver_names[i] != prior_name:
            if key:
                key = '%s|%s' % (key, ver_names[i])
            else:
                key = ver_names[i]
            prior_name = ver_names[i]
    if ttype == 'value':
        return key
    return key.upper()


def build_alias_struct(mindroot, model, ttype, fld_name=False):
    pymodel = get_pymodel(model)
    mindroot[pymodel] = mindroot.get(pymodel, {})
    mindroot[pymodel][ttype] = mindroot[pymodel].get(ttype, {})
    if ttype == 'value' and fld_name:
        mindroot[pymodel][ttype][fld_name] = mindroot[
            pymodel][ttype].get(fld_name, {})
    return mindroot


def link_versioned_name(mindroot, model, hash, ttype, src_name, ver,
                        fld_name=False):
    pymodel = get_pymodel(model)
    ver_name = get_ver_name(src_name, ver)
    if ttype == 'value':
        if src_name.startswith('${') and src_name.endswith('}'):
            mindroot[pymodel][ttype][fld_name] = src_name
            item = None
        else:
            item = mindroot[pymodel][ttype][fld_name]
    else:
        item = mindroot[pymodel][ttype]
    if item is not None:
        item[hash] = item.get(hash, {})
        if ver_name:
            if ver_name in item:
                if not isinstance(item[ver_name], list):
                    item[ver_name] = [item[ver_name]]
                if hash not in item[ver_name]:
                    item[ver_name].append(hash)
            else:
                item[ver_name] = hash
        item[hash][ver] = src_name
    return mindroot


def tnl_acc_type(ctx, model, src_name, src_ver, tgt_ver, name):
    src_majver = int(src_ver.split('.')[0])
    tgt_majver = int(tgt_ver.split('.')[0])
    if src_majver < 9 and tgt_majver >= 9:
        name = CVT_ACC_TYPE_OLD_NEW.get(name, name)
    elif src_majver >= 9 and tgt_majver < 9:
        name = CVT_ACC_TYPE_NEW_OLD.get(name, name)
    return name


def tnl_by_code(ctx, model, src_name, src_ver, tgt_ver, name):
    src_majver = int(src_ver.split('.')[0])
    tgt_majver = int(tgt_ver.split('.')[0])
    if name == '${amount}':
        if isinstance(src_name, basestring):
            src_name = float(src_name)
        if (src_majver < 9 and tgt_majver >= 9 and
                src_name in (0.04, 0.05, 0.1, 0.21, 0.22)):
            name = src_name * 100
        elif (src_majver >= 9 and tgt_majver < 9 and
              src_name in (4, 5, 10, 21, 22)):
            name = src_name / 100
        else:
            name = src_name
    return name


def translate_from_to(ctx, model, src_name, src_ver, tgt_ver,
                      ttype=False, fld_name=False, type=None):
    """Translate symbol <src_name> from <src_ver> to <tgt_ver> of Odoo.
    If ttype not supplied, translation is applied for 'name' and 'field' ttypes
    If ttype is 'value', the param <fld_name> must by supplied.
    Param type is deprecated. It used just for compatibility with old version
    """
    if not ttype and type:
        ttype = type
    del type
    mindroot = ctx.get('mindroot', {})
    if src_ver not in VERSIONS:
        print('Invalid source version!')
        return ''
    if tgt_ver not in VERSIONS:
        print('Invalid target version!')
        return ''
    if ttype == 'value' and not fld_name:
        print('Translation of value require field name!')
        return ''
    pymodel = get_pymodel(model)
    ver_name = get_ver_name(src_name, src_ver)
    name = src_name
    if ver_name and pymodel in mindroot:
        names = []
        for typ in map(lambda x: x, ('name',
                                     'field')) if not ttype else [ttype]:
            if ttype == 'value':
                item = mindroot[pymodel].get(typ, {}).get(fld_name, {})
            else:
                item = mindroot[pymodel].get(typ, {})
            if isinstance(item, basestring):
                if item.startswith('${') and item.endswith('}'):
                    fct = item[2: -1]
                    if fct == 'amount':
                        names.append(tnl_by_code(ctx, model, src_name,
                                                 src_ver, tgt_ver,
                                                 item))
            elif ver_name in item:
                hash = item[ver_name]
                if not isinstance(hash, list):
                    hash = [hash]
                for xx in hash:
                    if xx in item and tgt_ver in item[xx]:
                        if item[xx][tgt_ver] not in names:
                            names.append(item[xx][tgt_ver])
        if names:
            if len(names) == 1:
                name = names[0]
            else:
                name = names
    return name


def translate_from_sym(ctx, model, sym, tgt_ver):
    mindroot = ctx.get('mindroot', {})
    if tgt_ver not in VERSIONS:
        print('Invalid target version!')
        return ''
    pymodel = get_pymodel(model)
    name = ''
    for typ in ('name', 'field'):
        if pymodel in mindroot and \
                typ in mindroot[pymodel] and \
                sym in mindroot[pymodel][typ] and \
                tgt_ver in mindroot[pymodel][typ][sym]:
            name = mindroot[pymodel][typ][sym][tgt_ver]
            break
    return name


def read_stored_dict(ctx):
    if 'mindroot' in ctx:
        return
    csv.register_dialect('transodoo',
                         delimiter=_c('\t'),
                         quotechar=_c('\"'),
                         quoting=csv.QUOTE_MINIMAL)
    if 'dict_fn' not in ctx or not ctx['dict_fn']:
        p = os.path.dirname(__file__) or '.'
        if os.path.isfile('%s/transodoo.csv' % p):
            ctx['dict_fn'] = '%s/transodoo.csv' % p
        elif os.path.isfile(os.path.join(os.path.expanduser('~'),
                                         'transodoo.csv')):
            ctx['dict_fn'] = os.path.join(os.path.expanduser('~'),
                                         'transodoo.csv')
        else:
            ctx['dict_fn'] = 'transodoo.csv'
    # ctx['dict_fn'] = './__transodoo.csv'        #debug
    mindroot = {}
    with open(ctx['dict_fn'], 'rb') as fd:
        hdr = False
        reader = csv.DictReader(fd,
                                fieldnames=[],
                                restkey='undef_name',
                                dialect='transodoo')
        for line in reader:
            row = line['undef_name']
            if not hdr:
                MODEL = row.index('model')
                NAME = row.index('name')
                TYPE = row.index('type')
                # if 'hash' in row:
                #     HASH = row.index('hash')
                # else:
                #     HASH = NAME
                VER_IX = {}
                last_ver = False
                for ver in VERSIONS:
                    if ver in row:
                        VER_IX[ver] = row.index(ver)
                        last_ver = ver
                    else:
                        VER_IX[ver] = row.index(last_ver)
                hdr = True
                continue
            mindroot = build_alias_struct(mindroot,
                                          row[MODEL],
                                          row[TYPE],
                                          fld_name=row[NAME])
            ver_names = []
            for ver in VERSIONS:
                ver_names.append(row[VER_IX[ver]])

            hash = set_hash(row[TYPE], row[NAME], ver_names)
            for ver in VERSIONS:
                mindroot = link_versioned_name(mindroot,
                                               row[MODEL],
                                               hash,
                                               row[TYPE],
                                               row[VER_IX[ver]],
                                               ver,
                                               fld_name=row[NAME])
    ctx['mindroot'] = mindroot


def write_stored_dict(ctx):
    csv.register_dialect('transodoo',
                         delimiter=_c('\t'),
                         quotechar=_c('\"'),
                         quoting=csv.QUOTE_MINIMAL)
    if 'dict_fn' not in ctx or not ctx['dict_fn']:
        p = os.path.dirname(__file__) or '.'
        if os.path.isfile('%s/transodoo.csv' % p):
            ctx['dict_fn'] = '%s/transodoo.csv' % p
        elif os.path.isfile('~/dev/transodoo.csv'):
            ctx['dict_fn'] = '~/dev/transodoo.csv'
        else:
            ctx['dict_fn'] = 'transodoo.csv'
    with open(ctx['dict_fn'], 'wb') as fd:
        writer = csv.DictWriter(
            fd,
            fieldnames=('model', 'name', 'type', 'hash') + VERSIONS,
            dialect='transodoo')
        writer.writeheader()
        mindroot = ctx['mindroot']
        for model in sorted(mindroot.keys()):
            for ttype in sorted(mindroot[model].keys()):
                if ttype == 'value':
                    iterate = sorted(mindroot[model][ttype].keys())
                else:
                    iterate = [None]
                for name in iterate:
                    if ttype == 'value':
                        items = mindroot[model][ttype][name]
                    else:
                        items = mindroot[model][ttype]
                    if isinstance(items, basestring):
                        iterate2 = [items]
                    else:
                        iterate2 = sorted(items.keys())
                    for hash in iterate2:
                        if not is_hash(hash):
                            continue
                        line = {
                            'model': model,
                            'type': ttype,
                        }
                        if ttype == 'name':
                            line['name'] = hash
                        else:
                            line['hash'] = hash
                            if ttype == 'value':
                                line['name'] = name
                        if isinstance(items, basestring):
                            for ver_name in VERSIONS:
                                line[ver_name] = hash
                        else:
                            for ver_name in sorted(items[hash].keys()):
                                if items[hash][ver_name]:
                                    line[ver_name] = items[hash][ver_name]
                        if len(line) > 4:
                            writer.writerow(line)


def transodoo_list(ctx):

    def do_line_ver(mindroot, nm, typ, fld_name):
        if not is_hash(nm):
            return ''
        line = '\n'
        if typ == 'value':
            line += '  %s\n' % fld_name
        for ver in VERSIONS:
            if typ == 'value':
                if ver in mindroot[ctx['pymodel']][typ][fld_name][nm]:
                    line += '    - %4.4s: %s\n' % (
                        ver, mindroot[ctx['pymodel']][typ][fld_name][nm][ver])
            else:
                if ver in mindroot[ctx['pymodel']][typ][nm]:
                    line += ' - %4.4s: %s\n' % (
                        ver, mindroot[ctx['pymodel']][typ][nm][ver])
        return line

    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    if ctx['pymodel'] not in mindroot:
        return
    line = '=====[ %s ]=====\n' % ctx['model']
    for typ in mindroot[ctx['pymodel']]:
        line += '\n%s\n' % typ
        if typ == 'value':
            for fld_name in mindroot[ctx['pymodel']][typ]:
                for nm in mindroot[ctx['pymodel']][typ][fld_name]:
                    line += do_line_ver(mindroot, nm, typ, fld_name)
        else:
            for nm in mindroot[ctx['pymodel']][typ]:
                line += do_line_ver(mindroot, nm, typ, False)
        print(line)


def transodoo_edit(ctx):
    if 'mindroot' not in ctx:
        mindroot = {}
    else:
        mindroot = ctx['mindroot']
    model = get_pymodel(ctx['model'])
    while True:
        while not model:
            m = input('Model (def=%s, type END to end): ' % model)
            if m.upper() == 'END':
                ctx['mindroot'] = mindroot
                return 0
            if m:
                model = get_pymodel(model)
        name = ctx['sym']
        while not name:
            name = input(
                'Symbolic name (def=%s, type END to end): ' % name).upper()
        if name == 'END':
            ctx['mindroot'] = mindroot
            return 0
        key = ctx['opt_kind']
        while not key:
            key = input(
                'Name of field (def=%s, type END to end): ' % key).upper()
        if key == 'END':
            ctx['mindroot'] = mindroot
            return 0
        mindroot = build_alias_struct(mindroot, model, name, key)
        k1 = get_pymodel(model)
        def_term = name.lower()
        print("Model %s, sym=%s, key=%s" % (model, name, key))
        for ver in VERSIONS:
            term = ''
            while not term:
                if ver in mindroot[k1]:
                    def_term = mindroot[k1][ver]
                term = input(
                    'Term[%s] (def=%s, blank=\\b, END to end): ' % (ver,
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
            mindroot[k1][ver] = term
        print(mindroot[k1])


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
            print(translate_from_to(ctx,
                                    ctx['pymodel'],
                                    ctx['sym'],
                                    ctx['oe_from_ver'],
                                    ctx['odoo_ver'],
                                    ttype=ctx['opt_kind'],
                                    fld_name=ctx['field_name']))
        else:
            print(translate_from_sym(ctx,
                                     ctx['pymodel'],
                                     ctx['sym'],
                                     ctx['odoo_ver']))
    elif ctx['action'] == 'write':
        read_stored_dict(ctx)
        write_stored_dict(ctx)
        return 0
    else:
        print("Invalid action!")
        return 1
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Transodoo",
                                "© 2017-2019 by SHS-AV s.r.l.",
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
    parser.add_argument('-k', '--kind',
                        action='store',
                        dest='opt_kind',
                        default='field')
    parser.add_argument('-l', '--language',
                        action='store',
                        dest='opt_lang',
                        default='it_IT')
    parser.add_argument('-m', '--model',
                        action='store',
                        dest='model',
                        default='res.groups')
    parser.add_argument('-N', '--field-name',
                        action='store',
                        dest='field_name')
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
    # ctx['pymodel'] = ctx['model'].replace('.', '_').lower()
    ctx['pymodel'] = ctx['model'].lower()
    if ctx['odoo_ver']:
        if ctx['odoo_ver'] not in VERSIONS:
            print('Invalid version %s!\nUse one of %s' % (ctx['odoo_ver'],
                                                          VERSIONS))
            sys.exit(1)
    if ctx['oe_from_ver']:
        if ctx['oe_from_ver'] not in VERSIONS:
            print('Invalid version %s!\nUse one of %s' % (ctx['odoo_ver'],
                                                          VERSIONS))
            sys.exit(1)
    sts = transodoo(ctx=ctx)
    exit(sts)
