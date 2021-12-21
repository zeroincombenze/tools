#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
from __future__ import print_function, unicode_literals
# from past.builtins import basestring

import re
import csv
# import pdb
import os
import sys
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib

__version__ = "0.3.55"
VERSIONS = ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0')



def get_pymodel(model):
    return model.replace('.', '_').lower()


def get_ver_name(name, ver):
    if name:
        return '%s__%s' % (ver, name)
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


def clean_transodoo(ctx=None):
    csv.register_dialect('transodoo',
                         delimiter=b'\t',
                         quotechar=b'\"',
                         quoting=csv.QUOTE_MINIMAL)
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
                prior_ver_names = []
                continue
            if row[TYPE] == 'merge':
                continue
            mindroot = build_alias_struct(mindroot,
                                          row[MODEL],
                                          row[NAME],
                                          row[TYPE])
            ver_names = []
            for ver in VERSIONS:
                ver_names.append(row[VER_IX[ver]])
            if prior_ver_names:
                for i in range(len(ver_names)):
                    if ver_names[i] and ver_names[i] == prior_ver_names[i]:
                        print('Duplicate record\n   %s\n   %s' % (
                            prior_ver_names,ver_names))
                        break
            prior_ver_names = ver_names
            # uname = set_uname(row[TYPE], row[NAME], ver_names)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Clean Transodoo",
                                "© 2019 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-f', '--tnl-file',
                        action='store',
                        dest='dict_fn',
                        default='transodoo.csv')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    p = os.path.dirname(__file__) or '.'
    if os.path.isfile('%s/transodoo.csv' % p):
        ctx['dict_fn'] = '%s/transodoo.csv' % p
    elif os.path.isfile(os.path.join(os.path.expanduser('~'),
                                     'transodoo.csv')):
        ctx['dict_fn'] = os.path.join(os.path.expanduser('~'),
                                     'transodoo.csv')
    else:
        ctx['dict_fn'] = 'transodoo.csv'
    exit(clean_transodoo(ctx=ctx))
