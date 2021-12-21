#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
usage: cvt_csv_coa.py [-h] -A ACTION -b ODOO_VER -f CSV_ODOO_VER [-n] [-q] [-V]
                        [-v]
                        src_csvfile dst_csvfile

Manage csv file of Odoo CoA

positional arguments:
  src_csvfile
  dst_csvfile

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
from python_plus import unicodes, bstrings, _b
import os
import sys
# import StringIO
import time
import csv
from os0 import os0
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
from clodoo import transodoo


__version__ = "1.0.4"

msg_time = time.time()
VALID_ACTIONS = ('export-comparable', 'export-full', 'export-group')


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


def manage_coa(ctx):
    TNLFLD = {
        'USER_TYPE': {
            'old': 'user_type',
            'new': 'user_type_id',
        },
        'TYPE': {
            'old': 'type',
            'new': 'internal_type',
        },
    }

    def read_csv_file(csv_fn, src_ver, tgt_ver, action):
        coa = []
        group = []
        tnlctx = {}
        transodoo.read_stored_dict(tnlctx)
        src_majver = eval(src_ver.split('.')[0])
        tgt_majver = eval(tgt_ver.split('.')[0])
        # Do not remove 'b' (binary= to avoid utf-8 conflicts!
        with open(csv_fn, 'rbU') as fd:
            hdr = False
            reader = csv.reader(fd)
            for row in reader:
                if not hdr:
                    hdr = True
                    ix = len(row)
                    ID = row.index('id')
                    CODE = row.index('code')
                    NAME = row.index('name')
                    RECONCILE = row.index('reconcile')
                    if 'user_type_id:id' in row:
                        USER_TYPE = row.index('user_type_id:id')
                    elif 'user_type:id' in row:
                        USER_TYPE = row.index('user_type:id')
                    else:
                        USER_TYPE = False
                    if 'type' in row:
                        TYPE = row.index('type')
                    elif 'user_type' in row:
                        TYPE = row.index('user_type')
                    else:
                        TYPE = ix
                        ix += 1
                    if 'parent_id:id' in row:
                        PARENT = row.index('parent_id:id')
                    else:
                        PARENT = ix
                        ix += 1
                    if 'chart_template_id:id' in row:
                        CHART = row.index('chart_template_id:id')
                    else:
                        CHART = ix
                        ix += 1
                    continue
                line = unicodes(row)
                while len(line) < ix:
                    line.append('')
                row = {}
                for item in ('ID', 'CODE', 'NAME'):
                    row[item] = line[locals()[item]]
                for item in ('TYPE', 'USER_TYPE'):
                    if tgt_majver > 9 and item == 'TYPE':
                        continue
                    value = transodoo.translate_from_to(
                        tnlctx, 'ir.model.data',
                        line[locals()[item]] or 'other',
                        src_ver, tgt_ver, ttype='xref',
                        fld_name=TNLFLD[item][
                            'old' if src_majver < 10 else 'new'])
                    if isinstance(value, (list, tuple)):
                        row[item] = value[0]
                    else:
                        row[item] = value
                item = 'USER_TYPE'
                if tgt_majver > 9:
                    if (row['CODE'].startswith('121') or
                            row['CODE'].startswith('123')):
                        row[item] = 'account.data_account_type_fixed_assets'
                    elif row['CODE'].startswith('211'):
                        row[item] = 'account.data_account_type_equity'
                    elif row['CODE'].startswith('65'):
                        row[item] = 'account.data_account_type_depreciation'
                    elif ((row['CODE'].startswith('190') or
                          row['CODE'].startswith('290')) and
                          row['CODE'].endswith('20')):
                        row[item] = 'account.data_account_type_prepayments'
                    elif (row['CODE'].startswith('610') and
                          row[item] == 'account.data_account_type_expenses'):
                        row[item] = 'account.data_account_type_direct_costs'
                    elif (row['CODE'].startswith('8') and
                          row[item] == 'account.data_account_type_income'):
                        row[item] = 'account.data_account_type_other_income'
                    elif row['CODE'] == '870230':
                        row[item] = 'account.data_unaffected_earnings'
                    elif (row[item] == 'account.data_account_type_current_assets' and
                          '+12 M' in row['NAME']):
                        row[item] = 'account.data_account_type_non_current_assets'
                    elif (row[item] == 'account.data_account_type_liability' and
                          '+12 M' in row['NAME']):
                        row[item] = 'account.data_account_type_non_current_liabilities'
                    item = 'PARENT'
                if not line[locals()[item]]:
                    if len(row['CODE']) >= 6:
                        row[item] = line[CODE][0:3]
                    elif len(row['CODE']) >= 3:
                        row[item] = line[CODE][0:2]
                    elif len(row['CODE']) >= 2:
                        row[item] = line[CODE][0:1]
                    else:
                        row[item] = ''
                else:
                    row[item] = line[locals()[item]]
                if len(row['PARENT']) < 2 and tgt_majver > 9:
                    row['PARENT'] = ''
                item = 'RECONCILE'
                row[item] = line[locals()[item]]
                item = 'CHART'
                row[item] = 'l10n_chart_it_zeroincombenze'
                if action == 'export-comparable':
                    if len(row['CODE']) < 6:
                        continue
                    line = (row['CODE'], row['NAME'], row['USER_TYPE'])
                    print(line)
                    coa.append(line)
                    continue
                if len(row['CODE']) < 6 and tgt_majver > 9:
                    line = (row['ID'], row['CODE'], row['NAME'], row['PARENT'])
                    if len(row['CODE']) < 2:
                        continue
                    print(line)
                    group.append(line)
                    continue
                if tgt_majver > 9:
                    line = (row['ID'], row['CODE'], row['NAME'], row['USER_TYPE'],
                            row['PARENT'], row['RECONCILE'], row['CHART'])
                else:
                    line = (row['ID'], row['CODE'], row['NAME'], row['USER_TYPE'],
                            row['TYPE'], row['PARENT'], row['RECONCILE'],
                            row['CHART'])
                if action != 'export-group':
                    print(line)
                coa.append(line)
        return coa, group

    def merge_coa(coa, merge_coa, group, merge_group):
        left_ix = 0
        right_ix = 0
        left_rec = coa[left_ix]
        right_rec = merge_coa[right_ix]
        tgt_coa = []
        while left_ix < len(coa) and right_ix < len(merge_coa):
            if (left_ix >= len(coa) or
                    eval(left_rec[left_ix][1]) > eval(right_rec[right_ix][1])):
                tgt_coa.append(right_rec)
                right_ix += 1
            elif (right_ix >= len(merge_coa) or
                  eval(left_rec[left_ix][1]) < eval(right_rec[right_ix][1])):
                tgt_coa.append(left_rec)
                left_ix += 1
            else:
                tgt_coa.append(left_rec)
                left_ix += 1
                right_ix += 1
        left_ix = 0
        right_ix = 0
        left_rec = coa[left_ix]
        right_rec = merge_coa[right_ix]
        tgt_group = []
        while left_ix < len(group) and right_ix < len(merge_group):
            if (left_ix >= len(group) or
                    eval(left_rec[left_ix][1]) > eval(right_rec[right_ix][1])):
                tgt_group.append(right_rec)
                right_ix += 1
            elif (right_ix >= len(merge_group) or
                  eval(left_rec[left_ix][1]) < eval(right_rec[right_ix][1])):
                tgt_group.append(left_rec)
                left_ix += 1
            else:
                tgt_group.append(left_rec)
                left_ix += 1
                right_ix += 1
        return tgt_coa, tgt_group

    VERSIONS = ['6.1', '7.0', '8.0', '9.0', '10.0',
                '11.0', '12.0', '13.0', '14.0']
    # ORGS = ('zero', 'powerp', 'librerp')
    action = ctx['action']
    if action not in VALID_ACTIONS:
        print('Invalid action %s!' % action)
        print('Valid action are: %s' % ','.join(VALID_ACTIONS))
        return 1
    src_ver = ctx['from_odoo_ver']
    if src_ver not in VERSIONS:
        print('Invalid Odoo source version %s' % src_ver)
        return 1
    tgt_ver = ctx['odoo_ver']
    if tgt_ver not in VERSIONS:
        print('Invalid Odoo target version %s' % tgt_ver)
        return 1
    csv_fn = os.path.expanduser(ctx['src_csvfile'])
    if not os.path.isfile(csv_fn):
        print('File %s not found!' % csv_fn)
        return 1
    merge_fn = None
    if ctx['merge_csvfile']:
        merge_fn = ctx['merge_csvfile']
        if not os.path.isfile(merge_fn):
            print('File %s not found!' % merge_fn)
            return 1
        merge_coa, merge_group = read_csv_file(
            merge_fn, src_ver, tgt_ver, 'export-full')

    coa, group = read_csv_file(csv_fn, src_ver, tgt_ver, action)
    if merge_fn:
        coa, group = merge_coa(coa, merge_coa, group, merge_group)
    # src_majver = eval(src_ver.split('.')[0])
    tgt_majver = eval(tgt_ver.split('.')[0])
    if ctx['dst_csvfile']:
        out_fn = ctx['dst_csvfile']
    elif action == 'export-group':
        out_fn = os.path.join(os.path.dirname(csv_fn),
                              'account.group.tmp.csv')
    else:
        out_fn = '%s.tmp.csv' % csv_fn[0: -4]
    if action == 'export-comparable':
        header = ['code', 'name',
                  TNLFLD['USER_TYPE']['old' if tgt_majver < 10 else 'new']]
    elif action == 'export-group':
        header = ['id', 'code_prefix', 'name', 'parent_id:id']
    else:
        if tgt_majver > 9:
            header = [
                'id', 'code', 'name',
                '%s:id' % TNLFLD['USER_TYPE']['new'],
                'parent_id:id', 'reconcile', 'chart_template_id:id']
        else:
            header = [
                'id', 'code', 'name',
                '%s:id' % TNLFLD['USER_TYPE']['old'],
                '%s:id' % TNLFLD['TYPE']['old'],
                'parent_id:id', 'reconcile', 'chart_template_id:id']
    if action == 'export-group':
        with open(out_fn, mode='wb') as fd:
            csv_obj = csv.writer(fd)
            csv_obj.writerow(bstrings(header))
            for line in group:
                ln = []
                for x in line:
                    ln.append(_b(x))
                csv_obj.writerow(ln)
    else:
        with open(out_fn, mode='wb') as fd:
            csv_obj = csv.writer(fd)
            csv_obj.writerow(bstrings(header))
            for line in coa:
                ln = []
                for x in line:
                    ln.append(_b(x))
                csv_obj.writerow(ln)
    print('File %s created' % out_fn)
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Manage csv file of Odoo CoA",
                                "© 2020-2021 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-A', '--action',
                        action='store',
                        dest='action',
                        help='Actions are %s' % ','.join(VALID_ACTIONS))
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-f', '--from-odoo-branch',
                        action='store',
                        dest='from_odoo_ver')
    parser.add_argument('-m', '--merge-csv',
                        action='store',
                        dest='merge_csvfile')
    parser.add_argument('-o', '--out-csvfile',
                        action='store',
                        dest='dst_csvfile')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_csvfile')
    ctx = items_2_unicode(parser.parseoptargs(sys.argv[1:]))
    sys.exit(manage_coa(ctx))
