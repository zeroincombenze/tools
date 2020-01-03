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
[pymodel][type]: may be:
    name:    symbolic name of a field
    field:   field name to translate
    action:  action/function to translate
    module:  module name to translate
    merge:   module name merged with
    value:value of field to translate (name is the field name)

[pymodel][type]['name']    entry for name
[pymodel][type]['name'][name]  specific name entry
[pymodel][type]['name'][name][ver] = versioned name

[pymodel][type]['field']    entry for field
[pymodel][type]['name'][name.ver] = SYM of field
[pymodel][type]['field'][SYM]    entry for SYM field
[pymodel][type]['name'][SYM][ver] = versioned name

"""
from __future__ import print_function, unicode_literals
from past.builtins import basestring

import re
import csv
# import pdb
import os
import sys
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib

__version__ = "0.1.0.9"
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0')


def get_pymodel(model):
    return model.replace('.', '_').lower()


def get_ver_name(name, ver):
    if name:
        return  '%s__%s' % (ver, name)
    return name


def is_uname(name):
    if re.match(r'^[0-9]+\.[0-9]+__', name):
        return False
    return True


def set_uname(type, name, ver_names):
    if type == 'name':
        return name.upper()
    prior_name = ''
    key = ''
    for i, ver in enumerate(VERSIONS):
        if ver_names[i] and ver_names[i] != prior_name:
            if key:
                key = '%s|%s' % (key, ver_names[i])
            else:
                key = ver_names[i]
            prior_name = ver_names[i]
    if type == 'value':
        return key
    return key.upper()


def build_alias_struct(mindroot, model, uname, type, fld_name=False):
    pymodel = get_pymodel(model)
    if pymodel not in mindroot:
        mindroot[pymodel] = {}
    if type not in mindroot[pymodel]:
        mindroot[pymodel][type] = {}
    if type != 'value' and uname not in mindroot[pymodel][type]:
        mindroot[pymodel][type][uname] = {}
    if (type == 'value' and
            fld_name and
            (uname.find('^${') < 0 or
             not uname.endswith('}'))):
        if fld_name not in mindroot[pymodel][type]:
            mindroot[pymodel][type][fld_name] = {}
        if uname not in mindroot[pymodel][type][fld_name]:
            mindroot[pymodel][type][fld_name][uname] = {}
    return mindroot


def link_versioned_name(mindroot, model, uname, type, src_name, ver,
                        fld_name=False):
    mindroot = build_alias_struct(mindroot, model, uname, type,
                                  fld_name=fld_name)
    pymodel = get_pymodel(model)
    ver_name = get_ver_name(src_name, ver)
    if type == 'value':
        if src_name.startswith('${') and src_name.endswith('}'):
            mindroot[pymodel][type][fld_name] = src_name
        else:
            if ver_name:
                mindroot[pymodel][type][fld_name][ver_name] = uname
            mindroot[pymodel][type][fld_name][uname][ver] = src_name
    else:
        if ver_name:
            mindroot[pymodel][type][ver_name] = uname
        mindroot[pymodel][type][uname][ver] = src_name
    return mindroot


def tnl_by_code(ctx, model, src_name, src_ver, tgt_ver, name):
    src_majver = int(src_ver.split('.')[0])
    tgt_majver = int(tgt_ver.split('.')[0])
    if name == '${amount}':
        if isinstance(src_name, basestring):
            src_name = float(src_name)
        if (src_majver < 9 and tgt_majver >= 9):
            if src_name in (0.04, 0,05, 0.1, .22):
                name = src_name * 100
        elif (src_majver >= 9 and tgt_majver < 9):
            if src_name in (4, 5, 10, 22):
                name = src_name / 100
        else:
            name = src_name
    return name


def translate_from_to(ctx, model, src_name, src_ver, tgt_ver,
                      type=False, fld_name=False):
    """Translate the symbol <src_name> from <src_ver> of odoo into
    <tgt_ver> of odoo.
    If type not supplied, transaltion is applied for <name> and <fld_name> types
    The param <fld_name> must by supplied just if type is <value>; if field name
    is dependent by version, last version of name must be used
    """
    mindroot = ctx.get('mindroot', {})
    if src_ver not in VERSIONS:
        print('Invalid source version!')
        return ''
    if tgt_ver not in VERSIONS:
        print('Invalid target version!')
        return ''
    if type == 'value' and not fld_name:
        print('Translation of value require field name!')
        return ''
    pymodel = get_pymodel(model)
    ver_name = get_ver_name(src_name, src_ver)
    name = src_name
    if ver_name:
        for typ in map(lambda x:x, ('name', 'field')) if not type else [type]:
            if typ != 'value':
                if (pymodel in mindroot and
                        typ in mindroot[pymodel] and
                        ver_name in mindroot[pymodel][typ]):
                    uname = mindroot[pymodel][typ][ver_name]
                    if (uname in mindroot[pymodel][typ] and
                            tgt_ver in mindroot[pymodel][typ][uname]):
                        name = mindroot[pymodel][typ][uname][tgt_ver]
                        break
            else:
                if (pymodel in mindroot and
                        typ in mindroot[pymodel] and
                        fld_name in mindroot[pymodel][typ]):
                    if ver_name in mindroot[pymodel][typ][fld_name]:
                        uname = mindroot[pymodel][typ][fld_name][ver_name]
                        if (uname in mindroot[pymodel][typ][fld_name] and
                                tgt_ver in mindroot[
                                    pymodel][typ][fld_name][uname]):
                            name = mindroot[
                                pymodel][typ][fld_name][uname][tgt_ver]
                            break
                    elif (mindroot[pymodel][typ][fld_name].startswith('${') and
                            mindroot[pymodel][typ][fld_name].endswith('}')):
                        name = tnl_by_code(ctx, model, src_name, src_ver,
                                           tgt_ver,
                                           mindroot[pymodel][typ][fld_name])
                        break
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


def debug_show(mindroot, model=None):
    for ln1 in mindroot:
        if model and model != ln1:
            continue
        print('%s' % ln1)
        if iter(mindroot[ln1]):
            for ln2 in mindroot[ln1]:
                print('    %s' % ln2)
                if iter(mindroot[ln1][ln2]):
                    for ln3 in mindroot[ln1][ln2]:
                        print('        %s' % ln3)
                        if not isinstance(mindroot[ln1][ln2][ln3], basestring) and iter(mindroot[ln1][ln2][ln3]):
                            for ln4 in mindroot[ln1][ln2][ln3]:
                                print('            %s' % ln4)
                                if not isinstance(mindroot[ln1][ln2][ln3][ln4], basestring) and iter(mindroot[ln1][ln2][ln3][ln4]):
                                    for ln5 in mindroot[ln1][ln2][ln3][ln4]:
                                        print('                %s' % ln5)


def read_stored_dict(ctx):
    if 'mindroot' in ctx:
        return
    csv.register_dialect('transodoo',
                         delimiter=b'\t',
                         quotechar=b'\"',
                         quoting=csv.QUOTE_MINIMAL)
    if 'dict_fn' not in ctx or not ctx['dict_fn']:
        p = os.path.dirname(__file__) or '.'
        if os.path.isfile('%s/transodoo.csv' % p):
            ctx['dict_fn'] = '%s/transodoo.csv' % p
        elif os.path.isfile('~/dev/transodoo.csv'):
            ctx['dict_fn'] = '~/dev/transodoo.csv'
        else:
            ctx['dict_fn'] = 'transodoo.csv'
    # ctx['dict_fn'] = './__transodoo.csv'        #debug
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
                MODEL = row.index('model')
                NAME = row.index('name')
                TYPE = row.index('type')
                VER_IX = {}
                for ver in VERSIONS:
                    VER_IX[ver] = row.index(ver)
                hdr = True
                continue
            mindroot = build_alias_struct(mindroot,
                                          row[MODEL],
                                          row[NAME],
                                          row[TYPE])
            ver_names = []
            for ver in VERSIONS:
                ver_names.append(row[VER_IX[ver]])

            uname = set_uname(row[TYPE], row[NAME], ver_names)
            for ver in VERSIONS:
                mindroot = link_versioned_name(mindroot,
                                               row[MODEL],
                                               uname,
                                               row[TYPE],
                                               row[VER_IX[ver]],
                                               ver,
                                               fld_name=row[NAME])
    ctx['mindroot'] = mindroot


def write_stored_dict(ctx):
    csv.register_dialect('transodoo',
                         delimiter=b'\t',
                         quotechar=b'\"',
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
                                fieldnames=('model', 'name', 'type') + VERSIONS,
                                dialect='transodoo')
        writer.writeheader()
        mindroot = ctx['mindroot']
        for pymodel in sorted(mindroot.keys()):
            if pymodel == 'ir_model':
                model = 'ir.model'
            elif pymodel == 'ir_module_module':
                model = 'ir.module.module'
            elif pymodel == 'account_account':
                model = 'account.account'
            elif pymodel == 'account_account_type':
                model = 'account.account.type'
            elif pymodel == 'account_invoice':
                model = 'account.invoice'
            elif pymodel == 'account_tax':
                model = 'account.tax'
            elif pymodel == 'res_city':
                model = 'res.city'
            elif pymodel == 'res_partner':
                model = 'res.partner'
            elif pymodel == 'res_users':
                model = 'res.users'
            elif pymodel == 'sale_order':
                model = 'sale.order'
            else:
                model = pymodel
            for typ in sorted(mindroot[pymodel].keys()):
                for uname in sorted(mindroot[pymodel][typ].keys()):
                    if not is_uname(uname):
                        continue
                    if typ != 'value':
                        line = {
                            'model': model,
                            'type': typ,
                            'name':  uname,
                        }
                        for ver_name in sorted(
                                mindroot[pymodel][typ][uname].keys()):
                            line[ver_name] = mindroot[
                                pymodel][typ][uname][ver_name]
                        if len(line) > 3:
                            writer.writerow(line)
                        continue
                    if isinstance(mindroot[pymodel][typ][uname], basestring):
                        line = {
                            'model': model,
                            'type': typ,
                            'name':  uname,
                        }
                        for ver_name in VERSIONS:
                            line[ver_name] = mindroot[pymodel][typ][uname]
                        if len(line) > 3:
                            writer.writerow(line)
                        continue
                    for fld in mindroot[pymodel][typ][uname]:
                        if not is_uname(fld):
                            continue
                        line = {
                            'model': model,
                            'type': typ,
                            'name':  uname,
                        }
                        for ver_name in sorted(
                                mindroot[pymodel][typ][uname][fld].keys()):
                            line[ver_name] = mindroot[
                                pymodel][typ][uname][fld][ver_name]
                        if len(line) > 3:
                            writer.writerow(line)


def transodoo_list(ctx):

    def do_line_ver(mindroot, nm, typ, fld_name):
        if not is_uname(nm):
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
            m = raw_input('Model (def=%s, type END to end): ' % model)
            if m.upper() == 'END':
                ctx['mindroot'] = mindroot
                return 0
            if m:
                model = get_pymodel(model)
        name = ctx['sym']
        while not name:
            name = raw_input(
                'Symbolic name (def=%s, type END to end): ' % name).upper()
        if name == 'END':
            ctx['mindroot'] = mindroot
            return 0
        key = ctx['opt_kind']
        while not key:
            key = raw_input(
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
                term = raw_input(
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
                                    type=ctx['opt_kind'],
                                    fld_name=ctx['field_name']))
        else:
            print(translate_from_sym(ctx,
                                     ctx['pymodel'],
                                     ctx['sym'],
                                     ctx['odoo_ver']))
    elif ctx['action'] == 'test':
        read_stored_dict(ctx)
        for ver in VERSIONS:
            name = translate_from_sym(ctx, 'res.groups', 'SALES', ver)
            print('SALES = %s[%s]' % (name,
                                      ver))
        source = 'Sales'
        for ver in VERSIONS:
            name = translate_from_to(ctx, 'res.groups', source, '7.0', ver)
            print('Source=%s[%s] => Target=%s[%s]' % (source,
                                                      '7.0',
                                                      name,
                                                      ver))
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
    ctx['pymodel'] = ctx['model'].replace('.', '_').lower()
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
