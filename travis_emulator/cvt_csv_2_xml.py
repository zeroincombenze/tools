#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import io
import ast
import os
import re
import sys
import csv
from os0 import os0
import z0lib


__version__ = "0.2.1.66"


def convert_file(ctx):
    if os.path.isfile(ctx['src_file']):
        if ctx['opt_verbose']:
            print("Reading %s" % ctx['src_file'])
        csv.register_dialect('odoo',
                             delimiter=',',
                             quotechar='\"',
                             quoting=csv.QUOTE_MINIMAL)
        majver = int(ctx['odoo_ver'].split('.')[0])
        ctr = 0
        target = '<?xml version="1.0" encoding="utf-8"?>\n'
        if majver >= 10:
            target += '<odoo>\n'
        else:
            target += '<openerp>\n<data>\n'
        with open(ctx['src_file'], 'rb') as csv_fd:
            hdr_read = False
            csv_obj = csv.DictReader(csv_fd,
                                     fieldnames=[],
                                     restkey='undef_name',
                                     dialect='odoo')
            for row in csv_obj:
                if not hdr_read:
                    csv_obj.fieldnames = row['undef_name']
                    hdr_read = True
                    continue
                ctr += 1
                if 'id' in row:
                    id = row['id']
                elif ctx['id_mode'] in row:
                    id = '%s_%s' % (ctx['id_prefix'], row[ctx['id_mode']])
                else:
                    id = '%s%d' % (ctx['id_prefix'], ctr)
                line = '    <record model="%s" id="%s">\n' % (
                    ctx['odoo_model'], id)
                for name in csv_obj.fieldnames:
                    if name == 'id':
                        continue
                    value = row[name].replace('"', '\"')
                    line += '        <field name="%s">%s</field>\n' % (
                        name, value)
                line += '    </record>\n'
                target += line
        if majver >= 10:
            target += '</odoo>\n'
        else:
            target += '</data>\n</openerp>\n'
        target_fn = ctx['src_file'][0: -4] + '.xml'
        with open(target_fn, 'w') as fd:
            fd.write(target)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Convert csv file into xml file",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-i', '--id-prefix',
                        action='store',
                        dest='id_prefix')
    parser.add_argument('-j', '--id-mode',
                        action='store',
                        help='ctr,code',
                        dest='id_mode')
    parser.add_argument('-m', '--model',
                        action='store',
                        dest='odoo_model')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['odoo_ver']:
        print('Missing Odoo Version! Set switch -b')
        sts = 1
    elif not ctx['odoo_model']:
        print('Missing Odoo Model! Set switch -m')
        sts = 1
    else:
        sts = convert_file(ctx)
    sys.exit(sts)
