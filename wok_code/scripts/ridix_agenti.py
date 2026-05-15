#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from python_plus import _c, unicodes

try:
    from z0lib import z0lib
except ImportError:
    import z0lib


__version__ = "2.0.23"

msg_time = time.time()

CVT = {
    "Andolcetti": "Andolcetti Luca",
    "Belgeri": "Belgeri Eugenio",
    "Caiazza": "Caiazza Emanuele",
    "Carraro": "Carraro Alberto",
    "Checchin": "Checchin Andrea",
    "Direzionale": "Cliente Direzionale",
    "Coenda": "Coenda Lorenzo",
    "Costamagna": "Costamagna Mirko",
    "De Notariis": "De Notariis Filippo",
    "Della Ragione": "Della Ragione Marco",
    "Di Benedetto": "Di Benedetto Luca",
    "Dian": "Dian Mauro",
    "Garbi": "Garbi Giuliano",
    "Gobbi": "GOCOTEC s.a.s. di Gobbi",
    "Ianiro": "Ianiro Pasquale",
    "Leoni": "Leoni Enrico",
    "Mazzocchi": "Mazzocchi Mauro",
    "Melloni": "Melloni Nicola",
    "Merli": "Merli Fabrizio",
    "Nacci": "Nacci Domenico",
    "Pepe": "Pepe Gaetano",
    "Perali": "Perali Cesare",
    "Poletti": "Poletti Davide",
    "Rocco": "Rocco Luca",
    "Sisti": "Sisti Adamo",
    "Valenti": "Valenti Luca",
    "Vascello": "Vascello Enrico",
    "Venturini": "Venturini Massimo",
    "RA.VEN": "RA.VEN s.n.c di Venturini Massimo",
    "Villa": "Villa Davide",
    "Villani": "Villani Simone",
}


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if t > 3:
        print(text)
        msg_time = time.time()


def convert_file(ctx):
    if not os.path.isfile(ctx['src_file']):
        print("File %s not found!" % ctx['src_file'])
        return 1
    if ctx['opt_verbose']:
        print("Reading %s" % ctx['src_file'])
    csv.register_dialect(
        'ridix', delimiter=_c('|'), quotechar=_c('\"'), quoting=csv.QUOTE_MINIMAL
    )
    ctr = 0
    with open(ctx['src_file'], 'r') as csv_fd:
        csv_obj = csv.DictReader(
            csv_fd, fieldnames=[], restkey='undef_name', dialect='ridix'
        )
        csv_fd_out = open(ctx['src_file'] + ".tmp", "w")
        csv_obj_out = csv.writer(csv_fd_out, dialect='ridix')
        hdr_read = False
        count = 0
        list_agents = [x for x in CVT.values()]
        row = {}
        last_row = {}
        for row in csv_obj:
            if not hdr_read:
                csv_obj.fieldnames = unicodes(row['undef_name'])
                hdr_read = True
                csv_obj_out.writerow(csv_obj.fieldnames)
                continue
            row = unicodes(row)
            count += 1
            ctr += 1
            for name in csv_obj.fieldnames:
                if isinstance(row[name], str):
                    row[name] = row[name].strip().replace("'", "")
                if not ctx['field_name'] or name != ctx['field_name']:
                    continue
                item_t = row[ctx['field_name']].strip().title()
                if item_t.endswith("Gobbi"):
                    item_t = "GOCOTEC s.a.s. di Gobbi"
                elif row[ctx['field_name']].strip().startswith("RA.VEN"):
                    item_t = "RA.VEN"
                if item_t in CVT:
                    # print(item_t, "->", CVT[item_t])
                    row[ctx['field_name']] = CVT[item_t]
                elif item_t in list_agents:
                    # print(item_t)
                    row[ctx['field_name']] = item_t
                else:
                    # print(row[ctx['field_name']])
                    pass
            if (
                last_row and (
                    not ctx["compact_code"]
                    or row[ctx["compact_code"]] != last_row.get(ctx["compact_code"]))
            ):
                csv_obj_out.writerow(last_row.values())
            if ctx["compact_code"]:
                if row[ctx["compact_code"]] != last_row.get(ctx["compact_code"]):
                    last_row = row.copy()
                elif ctx['field_name']:
                    last_row[ctx['field_name']] += "," + item_t

    if (
        last_row and ctx["compact_code"]
        and row[ctx["compact_code"]] != last_row.get(ctx["compact_code"])
    ):
        csv_obj_out.writerow(last_row.values())
    os.rename(ctx['src_file'], ctx['src_file'] + ".csv")
    os.rename(ctx['src_file'] + ".tmp", ctx['src_file'])
    return 0


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs(
        "Adapt sale agent in csv files",
        "© 2018-2026 by Zeroincombenze s.r.l.s.",
        version=__version__,
    )
    parser.add_argument('-h')
    parser.add_argument('-C', '--compact-code', action='store')
    parser.add_argument('-f', '--field-name', action='store')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file', nargs='?')
    ctx = unicodes(parser.parseoptargs(cli_args))
    sys.exit(convert_file(ctx))


if __name__ == "__main__":
    exit(main())
