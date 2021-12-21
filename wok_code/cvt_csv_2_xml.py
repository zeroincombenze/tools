#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""usage: cvt_csv_2_xml.py [-h] [-b ODOO_VER] [-i ID_PREFIX] [-j ID_MODE]
                        [-m ODOO_MODEL] [-n] [-q] [-R CVT-RULE] [-V] [-v]
                        src_file [dst_file]

Convert csv file into xml file

positional arguments:
  src_file
  dst_file

optional arguments:
  -h, --help            show this help message and exit
  -b ODOO_VER, --odoo-branch ODOO_VER
  -i ID_PREFIX, --id-prefix ID_PREFIX
  -j ID_MODE, --id-mode ID_MODE
                        ctr,code
  -m ODOO_MODEL, --model ODOO_MODEL
  -n, --dry-run         do nothing (dry-run)
  -q, --quiet           silent mode
  -R CVT-RULE, --cvt-rule CVT-RULE
  -V, --version         show program's version number and exit
  -v, --verbose         verbose mode

CVT_RULE may be:
l10n_it_base: convert res.country.state id of l10n_it_base module in 10.0
              odoo standard (just for 6.1 - 9.0 version)
              Old external id 'l10n_it_base.it_<?>' becomes 'base.state_it_<*>'
              where <?> is uppercase id and <*> is lowercase id of province
"""

from __future__ import print_function, unicode_literals
import os
import sys
import time
import csv
from os0 import os0
from python_plus import _c
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


def cvt_res_country_state(value):
    if value[0:3] == 'it_':
        return 'base.state_%s' % value.lower()
    elif value.startswith('l10n_it_base'):
        return 'base.state_%s' % value.split('.')[1].lower()
    return value


def convert_file(ctx):
    if os.path.isfile(ctx['src_file']):
        if ctx['opt_verbose']:
            print("Reading %s" % ctx['src_file'])
        csv.register_dialect('odoo',
                             delimiter=_c(','),
                             quotechar=_c('\"'),
                             quoting=csv.QUOTE_MINIMAL)
        majver = int(ctx['odoo_ver'].split('.')[0])
        ctr = 0
        target = '<?xml version="1.0" encoding="utf-8"?>\n'
        value = '1' if ctx['noupdate'] else '0'
        if majver >= 10:
            target += '<odoo noupdate="%s">\n' % value
        else:
            target += '<openerp>\n<data noupdate="%s">\n' % value
        with open(ctx['src_file'], 'r') as csv_fd:
            hdr_read = False
            csv_obj = csv.DictReader(csv_fd,
                                     fieldnames=[],
                                     restkey='undef_name',
                                     dialect='odoo')
            count = 0
            for row in csv_obj:
                if not hdr_read:
                    csv_obj.fieldnames = items_2_unicode(row['undef_name'])
                    hdr_read = True
                    continue
                row = items_2_unicode(row)
                count += 1
                msg_burst('%s [%d] ...' % (ctx['odoo_model'],
                                           count))
                ctr += 1
                if ('id' in row and 
                        ctx['cvt-rule'] == 'l10n_it_base' and
                        ctx['odoo_model'] == 'res.country.state' and
                        row['id'][0:3] == 'it_'):
                    row['id'] = cvt_res_country_state(row['id'])
                elif ('id' in row and
                        ctx['odoo_model'] == 'res.city'):
                    del row['id']
                if 'id' in row:
                    id = row['id']
                elif ctx['id_mode'] in row:
                    id = '%s_%s' % (ctx['id_prefix'], row[ctx['id_mode']])
                else:
                    id = '%s%d' % (ctx['id_prefix'], ctr)
                if 'id' in row:
                    line = '    <record model="%s" id="%s">\n' % (
                        ctx['odoo_model'], id)
                else:
                    line = '    <record model="%s">\n' % ctx['odoo_model']
                for name in csv_obj.fieldnames:
                    if name == 'id':
                        continue
                    nm = name if name[-3:] != '/id' else name[0:-3]
                    value = row[name].replace(b'"', b'\"')
                    if nm == 'state_id':
                        line += os0.u(
                            b'        <field name="%s" ref="%s"/>\n' % (
                                nm, cvt_res_country_state(value)))
                    elif nm != name:
                        line += os0.u(
                            b'        <field name="%s" ref="%s"/>\n' % (
                                nm, value))
                    else:
                        line += os0.u(
                            b'        <field name="%s">%s</field>\n' % (
                                nm, value))
                line += '    </record>\n'
                target += line
        if majver >= 10:
            target += '</odoo>\n'
        else:
            target += '</data>\n</openerp>\n'
        if not ctx['dst_file']:
            ctx['dst_file'] = ctx['src_file'][0: -4] + '.xml'
        if ctx['dst_file'] == '/dev/tty':
            print(target)
        else:
            with open(ctx['dst_file'], 'w') as fd:
                if ctx['opt_verbose']:
                    print("Writing %s" % ctx['dst_file'])
                fd.write(_c(target))


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Convert csv file into xml file",
                                "© 2018-2020 by SHS-AV s.r.l.",
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
    parser.add_argument('-N', '--no-update',
                        action='store_true',
                        dest='noupdate')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-R', '--cvt-rule',
                        action='store',
                        dest='cvt-rule')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = items_2_unicode(parser.parseoptargs(sys.argv[1:]))
    if not ctx['odoo_ver']:
        print(__doc__)
        print('Missing Odoo Version! Set switch -b')
        sts = 1
    elif not ctx['odoo_model']:
        print(__doc__)
        print('Missing Odoo Model! Set switch -m')
        sts = 1
    else:
        sts = convert_file(ctx)
    sys.exit(sts)