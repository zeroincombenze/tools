#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import csv

from os0 import os0
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib
# import transodoo
# import pdb

__version__ = "0.3.55"


VERSIONS = ['vg7', '61', '70', '80', '90', '100', '110', '120']
VERSIONS_PLUS = ['vg7', '61', '70', '80', '90', '100', '110', '120', '0']
ALIAS = {}


def get_summary(info):
    infos = info.split('\n')
    res = ''
    for i in range(len(infos)):
        if infos[i]:
            res = infos[i]
            break
    return res


def new_env():
    mod2xtl = {}
    for id in VERSIONS:
        mod2xtl[id] = []
    return mod2xtl


def add_elem(mod2xtl, id, elem):
    try:
        mod2xtl[id].append(elem)
    except BaseException:
        pass


def sort_data(mod2xtl):
    for id in VERSIONS:
        sorted_list = []
        for item in sorted(mod2xtl[id]):
            if item:
                sorted_list.append(item)
        mod2xtl[id] = sorted_list
        idx = 'ix' + id
        mod2xtl[idx] = 0
    mod2xtl['0'] = sorted(infos.keys())
    mod2xtl['ix0'] = 0


def get_next(mod2xtl):
    item = '~'
    for id in VERSIONS_PLUS:
        idx = 'ix' + id
        ix = mod2xtl[idx]
        if ix < len(mod2xtl[id]):
            itm = mod2xtl[id][ix]
            if itm < item:
                item = itm
    vers = []
    for id in VERSIONS_PLUS:
        idx = 'ix' + id
        ix = mod2xtl[idx]
        if ix < len(mod2xtl[id]):
            itm = mod2xtl[id][ix]
            if itm == item:
                vers.append(id)
                mod2xtl[idx] += 1
    return item, vers


def get_realname(item):
    global ALIAS
    if item.strip() in ALIAS:
        return ALIAS[item.strip()]
    return item.strip()


parser = z0lib.parseoptargs("Modules to install",
                            "© 2017-2020 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./clodoo.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name to connect",
                    dest="db_name",
                    metavar="file",
                    default='')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
# pdb.set_trace()
mod2xtl = new_env()
infos = {}
if os.path.isfile('Odoo_moduli.csv'):
    with open('Odoo_moduli.csv', 'rb') as f:
        hdr = False
        reader = csv.reader(f)
        for row in reader:
            if not hdr:
                hdr = True
                continue
            # infos[tech_name] = {description, author, notes, vers, repos, oev)
            item = row[1]
            infos[item] = [os0.b(row[0]),
                           os0.b(row[2]),
                           os0.b(row[4]),
                           os0.b(row[3]),
                           os0.b(row[5]),
                           '']
            add_elem(mod2xtl, '0', item)

if ctx['db_name']:
    uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                   db=ctx['db_name'],
                                   ctx=ctx)
    ixver = ctx['oe_version'].split('.')[0] + ctx['oe_version'].split('.')[1]
    model = 'ir.module.module'
    ids = clodoo.searchL8(ctx, model, [('state', '=', 'installed')])
    for id in ids:
        try:
            module = clodoo.browseL8(ctx, model, id)
            item = module.name
            if item in infos:
                notes = infos[item][2]
                summary = get_summary(infos[item][0])
            else:
                notes = ''
                summary = get_summary(os0.b(module.summary))
            infos[item] = [summary,
                           os0.b(module.author),
                           notes,
                           os0.b(module.installed_version),
                           '',
                           ixver]
        except BaseException:
            pass
with open('moduli_alias.csv', 'rb') as f:
    lines = f.read().split('\n')
    for line in lines:
        pv = line.split('=')
        if len(pv) == 2 and pv[0] not in ALIAS:
            ALIAS[pv[0].strip()] = os0.b(pv[1].strip())

with open('moduli_da_installare_vg7.csv', 'rb') as f:
    hdr = False
    reader = csv.reader(f)
    for row in reader:
        if not hdr:
            hdr = True
            continue
        # print row[1]
        add_elem(mod2xtl, 'vg7', get_realname(row[1]))

with open('code/z0_install_10.conf', 'rb') as f:
    lines = f.read().split('\n')
    for line in lines:
        if line.startswith('install_modules_'):
            pv = line.split('=')
            prm = pv[0]
            ver = prm[16:]
            id = ver.split('.')[0] + ver.split('.')[1]
            rows = pv[1].split(',')
            for row in rows:
                add_elem(mod2xtl, id, get_realname(row))

sort_data(mod2xtl)
print(','.join(mod2xtl['80']))
item = ''
ctrs = {}
for id in VERSIONS_PLUS:
    ctrs[id] = 0
# import pdb
# pdb.set_trace()
fd = open('moduli_da_installare.csv', 'w')
fmto = '%-40.40s %-3.3s %-3.3s %-3.3s %-3.3s %-3.3s' \
       ' %-4.4s %-4.4s %-4.4s %-40.40s %-20.20s %-10.10s'
fmtx = '"%s",%s,%s,%s,%s,%s,%s,%s,%s,"%s","%s","%s"\n'
print(fmto % ('Technical Name',
              VERSIONS[0],
              '%s.%s' % (VERSIONS[1][0:-1], VERSIONS[1][-1]),
              '%s.%s' % (VERSIONS[2][0:-1], VERSIONS[2][-1]),
              '%s.%s' % (VERSIONS[3][0:-1], VERSIONS[3][-1]),
              '%s.%s' % (VERSIONS[4][0:-1], VERSIONS[4][-1]),
              '%s.%s' % (VERSIONS[5][0:-1], VERSIONS[5][-1]),
              '%s.%s' % (VERSIONS[6][0:-1], VERSIONS[6][-1]),
              '%s.%s' % (VERSIONS[7][0:-1], VERSIONS[7][-1]),
              'Description',
              'Author',
              'Notes'))
line = fmtx % ('Technical Name',
               VERSIONS[0],
               '%s.%s' % (VERSIONS[1][0:-1], VERSIONS[1][-1]),
               '%s.%s' % (VERSIONS[2][0:-1], VERSIONS[2][-1]),
               '%s.%s' % (VERSIONS[3][0:-1], VERSIONS[3][-1]),
               '%s.%s' % (VERSIONS[4][0:-1], VERSIONS[4][-1]),
               '%s.%s' % (VERSIONS[5][0:-1], VERSIONS[5][-1]),
               '%s.%s' % (VERSIONS[6][0:-1], VERSIONS[6][-1]),
               '%s.%s' % (VERSIONS[7][0:-1], VERSIONS[7][-1]),
               'Description',
               'Author',
               'Notes')
fd.write(line)
while item != '~':
    item, vers = get_next(mod2xtl)
    if item != '~':
        datas = []
        for id in VERSIONS:
            if id in vers:
                datas.append('OK')
                ctrs[id] += 1
            else:
                datas.append('x')
        if item in infos:
            des = infos[item][0]
            author = infos[item][1]
            note = infos[item][2]
        else:
            des = author = note = ''
        # if infos[item][5]:
        #     for i,v in enumerate(VERSIONS):
        #         if v == infos[item][5]:
        #             datas[i] = 'OK'
        try:
            print(fmto % (item,
                          datas[0],
                          datas[1],
                          datas[2],
                          datas[3],
                          datas[4],
                          datas[5],
                          datas[6],
                          datas[7],
                          des,
                          author,
                          note))
        except BaseException:
            print(fmto % (item,
                          datas[0],
                          datas[1],
                          datas[2],
                          datas[3],
                          datas[4],
                          datas[5],
                          datas[6],
                          datas[7],
                          des,
                          '',
                          note))
        try:
            line = fmtx % (item,
                           datas[0],
                           datas[1],
                           datas[2],
                           datas[3],
                           datas[4],
                           datas[5],
                           datas[6],
                           datas[7],
                           des,
                           author,
                           note)
        except BaseException:
            line = fmtx % (item,
                           datas[0],
                           datas[1],
                           datas[2],
                           datas[3],
                           datas[4],
                           datas[5],
                           datas[6],
                           datas[7],
                           des,
                           '',
                           note)
        fd.write(line)
line = '%-65.65s' % 'TOTALE'
for id in VERSIONS:
    line = '%s %3s' % (line, ctrs[id])
print(line)
line = 'TOTALE'
for id in VERSIONS:
    line = '%s,%s' % (line, ctrs[id])
fd.write(line)
fd.close()
