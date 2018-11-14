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


def format_line(ctx, col_size, row, sep=None, flist=None):
    sep = sep or False
    flist = flist or row
    if sep:
        line = '+'
    else:
        line = '|'
    for i, p in enumerate(flist):
        if sep:
            line += '-' * (col_size[p] + 2)
            line += '+'
        elif isinstance(row, list):
            fmt_line = ' %%-%d.%ds |' % (col_size[p], col_size[p])
            line += fmt_line % row[i]
        else:
            fmt_line = ' %%-%d.%ds |' % (col_size[p], col_size[p])
            line += fmt_line % row[p]
    line += '\n'
    return line


def convert_file(ctx):
    if os.path.isfile(ctx['src_file']):
        if ctx['opt_verbose']:
            print("Reading %s" % ctx['src_file'])
        csv.register_dialect('odoo',
                             delimiter=',',
                             quotechar='\"',
                             quoting=csv.QUOTE_MINIMAL)
        ctr = 0
        col_size = {}
        text = ''
        with open(ctx['src_file'], 'rb') as csv_fd:
            hdr_read = False
            csv_obj = csv.DictReader(csv_fd,
                                     fieldnames=[],
                                     restkey='undef_name',
                                     dialect='odoo')
            for row in csv_obj:
                if not hdr_read:
                    csv_obj.fieldnames = row['undef_name']
                    for p in csv_obj.fieldnames:
                        col_size[p] = min(len(os0.u(p)), 16)
                    hdr_read = True
                    continue
                for p in csv_obj.fieldnames:
                    col_size[p] = max(col_size[p], min(len(os0.u(row[p])), 40))
        with open(ctx['src_file'], 'rb') as csv_fd:
            hdr_read = False
            csv_obj = csv.DictReader(csv_fd,
                                     fieldnames=[],
                                     restkey='undef_name',
                                     dialect='odoo')
            import pdb
            pdb.set_trace()
            for row in csv_obj:
                if not hdr_read:
                    csv_obj.fieldnames = row['undef_name']
                    hdr_read = True
                    text += format_line(ctx, col_size, row['undef_name'],
                                        sep=True)
                    text += format_line(ctx, col_size, row['undef_name'])
                    text += format_line(ctx, col_size, row['undef_name'],
                                        sep=True)
                    continue
                ctr += 1
                text += format_line(ctx, col_size, row,
                                    flist=csv_obj.fieldnames)
                text += format_line(ctx, col_size, row, sep=True,
                                    flist=csv_obj.fieldnames)
        with open(ctx['dst_file'], 'w') as fd:
            fd.write(os0.b(text))


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
    sts = convert_file(ctx)
    sys.exit(sts)
