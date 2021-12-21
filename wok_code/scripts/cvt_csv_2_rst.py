#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
usage: cvt_csv_2_rst.py [-h] [-b ODOO_VER] [-m MAX_COL_WIDTH] [-n] [-q] [-V]
                        [-v]
                        src_file [dst_file]

Convert csv file into xml file

positional arguments:
  src_file
  dst_file

optional arguments:
  -h, --help            show this help message and exit
  -b ODOO_VER, --odoo-branch ODOO_VER
  -m MAX_COL_WIDTH, --max-col-width MAX_COL_WIDTH
  -n, --dry-run         do nothing (dry-run)
  -q, --quiet           silent mode
  -V, --version         show program's version number and exit
  -v, --verbose         verbose mode
"""

from __future__ import print_function, unicode_literals
import os
import sys
from io import StringIO
import time
import csv
from os0 import os0
from python_plus import _c, _u
try:
    from z0lib import z0lib
except ImportError:
    import z0lib


__version__ = "1.0.4"

msg_time = time.time()

def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def items_2_unicode(src):
    if isinstance(src, dict):
        for x in src.keys():
            src[x] = os0.u(src[x])
    elif isinstance(src, list):
        for i, x in enumerate(src):
            src[i] = os0.u(x)
    return src


def format_line(col_size, row, sep=None, flist=None):
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


def convert_text(ctx, src_string):
    max_col_width = int(ctx['max_col_width'])
    csv.register_dialect('odoo',
                         delimiter=_c(','),
                         quotechar=_c('\"'),
                         quoting=csv.QUOTE_MINIMAL)
    ctr = 0
    col_size = {}
    text = ''
    csv_fd = StringIO(src_string)
    hdr_read = False
    csv_obj = csv.DictReader(csv_fd,
                             fieldnames=[],
                             restkey='undef_name',
                             dialect='odoo')
    for row in csv_obj:
        if not hdr_read:
            csv_obj.fieldnames = items_2_unicode(row['undef_name'])
            for p in csv_obj.fieldnames:
                col_size[p] = min(len(p), 16)
            hdr_read = True
            continue
        if row[csv_obj.fieldnames[0]][0:4] == '.. $':
            pass
        else:
            for p in csv_obj.fieldnames:
                col_size[p] = max(col_size[p], min(len(row[p]), max_col_width))
    csv_fd.close()
    csv_fd = StringIO(src_string)
    hdr_read = False
    csv_obj = csv.DictReader(csv_fd,
                             fieldnames=[],
                             restkey='undef_name',
                             dialect='odoo')
    for row in csv_obj:
        if not hdr_read:
            row['undef_name'] = items_2_unicode(row['undef_name'])
            csv_obj.fieldnames = row['undef_name']
            hdr_read = True
            text += format_line(col_size, row['undef_name'], sep=True)
            text += format_line(col_size, row['undef_name'])
            text += format_line(col_size, row['undef_name'], sep=True)
            continue
        row = items_2_unicode(row)
        if row[csv_obj.fieldnames[0]][0:4] == '.. $':
            text += row[csv_obj.fieldnames[0]]
            text += '\n'
        else:
            ctr += 1
            text += format_line(col_size, row, flist=csv_obj.fieldnames)
            text += format_line(col_size, row, sep=True,
                                flist=csv_obj.fieldnames)
    csv_fd.close()
    return text


def convert_file(ctx):
    if os.path.isfile(ctx['src_file']):
        if ctx['opt_verbose']:
            print("Reading %s" % ctx['src_file'])
        with open(ctx['src_file'], 'r') as fd:
            src_string = _u(fd.read())
            target = convert_text(ctx, src_string)
        if not ctx['dst_file']:
            ctx['dst_file'] = ctx['src_file'][0: -4] + '.rst'
        if ctx['dst_file'] == '/dev/tty':
            print(target)
        else:
            if ctx['opt_verbose']:
                print("Writing %s" % ctx['dst_file'])
            with open(ctx['dst_file'], 'w') as fd:
                fd.write(_c(target))


def main(cli_args=None):
    # if not cli_args:
    #     cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs("Convert csv file into xml file",
                                "© 2018-2021 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-m', '--max-col-width',
                        action='store',
                        dest='max_col_width',
                        default="250")
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = items_2_unicode(parser.parseoptargs(sys.argv[1:]))
    return convert_file(ctx)