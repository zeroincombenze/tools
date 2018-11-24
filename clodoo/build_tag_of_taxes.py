#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import csv
# import re
from z0lib import parseoptargs
# import clodoo


__version__ = '0.3.8'


def read_csv_file(csv_fn):
    # import pdb
    # pdb.set_trace()
    tag_list = {}
    with open(csv_fn, 'rb') as f:
        hdr = False
        reader = csv.reader(f)
        for row in reader:
            if not hdr:
                hdr = True
                # ID = row.index('id')
                DES = row.index('description')
                NAME = row.index('name')
                # SEQ = row.index('sequence')
                TYPE = row.index('amount_type')
                USE = row.index('type_tax_use')
                id = 0
                continue
            if row[TYPE] == 'group':
                groups = '"%sa,%sb"' % (row[DES], row[DES])
            else:
                groups = ''
            if row[USE] != 'none':
                id += 1
                tag = 'tag_%02d' % id
                print '%s,%s,%s,%s' % (row[DES], row[NAME], tag, groups)
                tag_list[tag] = row[DES]
            else:
                print '%s,%s,%s,%s' % (row[DES], row[NAME], '', groups)
        print
        template = r"""        <record id="%s" model="account.account.tag">
            <field name="name">%s</field>
            <field name="applicability">taxes</field>
        </record>"""
        for tag in sorted(tag_list):
            print template % (tag, tag_list[tag])


def print_tags(ctx):
    read_csv_file(ctx['csv_fn'])
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Build tag from taxes file csv",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-c", "--csv-file",
                        help="csv file to read",
                        dest="csv_fn",
                        metavar="file",
                        default='./account.tax.template.csv')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    sys.exit(print_tags(ctx))
