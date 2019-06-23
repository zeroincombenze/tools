#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from past.builtins import basestring

import sys
import logging
import csv
from python_plus import unicodes
# import re
_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
except ImportError as err:
    _logger.debug(err)
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = '0.3.8.40'

def wep_text(text):
    if text:
        return unidecode(text).strip()
    return text

def dim_text(text):
    text = wep_text(text)
    if text:
        res = ''
        for ch in text:
            if ch.isalnum():
                res += ch.lower()
        text = res
    return text


CVT_TBL = {
    'crediti v/clienti ': 'Crediti v/clienti Italia',
    'debiti v/fornitori ': 'Debiti v/fornitori Italia',
    'costi di impianto ': 'Spese di Impianto e di Ampliamento',
    'arredamento ': 'Mobili e Arredi Ufficio',
    'attrezzature commerciali ': 'Attrezzature Industriali e Commerciali',
    'banche c/c passivi ': 'Banche c/c passivi nazionali',
    'banche c/effetti scontati ': 'Effetti allo sconto',
    'beni di terzi ': 'Beni di terzi presso l\'impresa,'
                      ' a titolo di deposito o comodato',
    'bilancio di apertura ': 'Stato patrimoniale iniziale',
    'bilancio di chiusura ': 'Stato patrimoniale finale',
    'cambiali all\'incasso ': 'Banche c/cambiali all\'incasso',
    'cambiali allo sconto ': 'Effetti allo sconto (+12M)',
    'cambiali attive ':  'Cambiali attive (+12M)',
    'rischi per fideiussioni ': 'Rischi assunti dall\'impresa, Fideiussioni',
    'sconti passivi bancari ': 'Spese e commissioni bancarie',
    'software ': 'Programmi Software e Licenze',
    'stato patrimoniale': 'Stato patrimoniale (da risultato di esercizio)',
    'TFRL ': 'TFR: trattamento di fine rapporto',
    'titolare c/ritenute subite ': 'Crediti per ritenute subite',
    'utile d\'esercizio ': 'Utile (perdita) d\'esercizio ',
    'merci c/vendite ': 'Merci c/vendita',
    'costi di pubblicità ': 'Costi pubblicitari',
    'FA costi di impianto ': 'FA Costi di Impianto e di Ampliamento',
    'FA software ': 'FA Programmi Software e Licenze',
    'macchine d\'ufficio ': 'Macchine Ufficio Elettroniche',
    'imballaggi durevoli ': 'Imballaggi durevoli da riutilizzare',
    'fornitori immobilizzazioni c/acconti ':
        'Acconti a Fornitori su Immobilizzazioni',
    'Mutui passivi': 'Mutui passivi',
    # 'mutui attivi ': 'Mutui passivi',
    'materie di consumo ': 'Materie prime e di consumo',
    'merci ': 'Prodotti finiti e Merci',
    'IVA c/acconto ': 'Imposte c/acconto IVA',
    'debiti per TFRL': 'Debiti per TFR',
    'crediti per IVA ': 'Crediti IVA c/erario',
    'fatture da ricevere ': 'Fornitori Fatture da ricevere ',
    'clienti c/acconti ': 'Debiti v/clienti c/anticipi',
    'merci c/apporti ': 'Costi Merce c/apporti',
    'perdita d\'esercizio ': 'Perdita da esercizio precedente',
    'merci c/acquisti': 'Spese accessorie su Acquisti',
    'costi di trasporto ': 'Costi di trasporto e spedizione',
    'fondo ammortamento costi di impianto ':
        'FA Costi di Impianto e di Ampliamento',
    'fondo ammortamento software ': 'FA Programmi Software e Licenze',
    'fatture da emettere ': 'Clienti fatture da emettere',
}
def read_csv_file(csv_fn):
    coa = {}
    rev_coa = {}
    with open(csv_fn, 'rb') as f:
        hdr = False
        reader = csv.reader(f)
        for row in reader:
            if not hdr:
                hdr = True
                CODE = row.index('code')
                NAME = row.index('name')
                continue
            row = unicodes(row)
            if row[NAME] in CVT_TBL:
                row[NAME] = CVT_TBL[row[NAME]]
            elif row[NAME].lower().startswith('ammortamento '):
                row[NAME] = 'QA' + row[NAME][12:]
            elif row[NAME].lower().startswith('fondo ammortamento '):
                row[NAME] = 'FA' + row[NAME][18:]
            coa[('%s000000' % row[CODE])[0:6]] = row[NAME]
            dim_name = dim_text(row[NAME])
            rev_coa[dim_name] = ('%s000000' % row[CODE])[0:6]
    return coa, rev_coa

def rename_coa(ctx):
    uid, ctx = clodoo.oerp_set_env(ctx=ctx)
    coa_z0, rev_coa_z0 = read_csv_file(ctx['csv_fn_z0'])
    coa_oca, rev_coa_oca = read_csv_file(ctx['csv_fn_oca'])
    cvt_coa = {}
    to_delete_z0 = []
    to_delete_oca = []
    for k1 in rev_coa_oca:
        if k1 in rev_coa_z0:
            cvt_coa[rev_coa_oca[k1]] = rev_coa_z0[k1]
            # to_delete_z0.append(rev_coa_z0[k1])
            to_delete_oca.append(rev_coa_oca[k1])
    # for code in to_delete_z0:
    #     del rev_coa_z0[dim_text(coa_z0[code])]
    #     del coa_z0[code]
    for code in to_delete_oca:
        del rev_coa_oca[dim_text(coa_oca[code])]
        del coa_oca[code]
    coa_code_z0 = sorted(coa_z0.keys())
    coa_code_oca = sorted(coa_oca.keys())
    for ix,k1 in enumerate(coa_code_oca):
        if ix < len(coa_code_z0):
            k2 = coa_code_z0[ix]
            d2 = coa_z0[k2]
        else:
            k2 = ''
            d2 = ''
        print('%s==%s (%s==%s)' % (k1, k2, coa_oca[k1], d2))
    if ctx.get('_cr'):
        for code in sorted(cvt_coa,reverse=True):
            query = "update account_account set code='%s' where code = '%s'" % (
                cvt_coa[code], code)
            print(">>>%s" % query)
            try:
                ctx['_cr'].execute(query)
            except BaseException:
                print('Error excuting sql')
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Convert CoA from OCA to Zeroincombenze",
                                "© 2019 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default='/etc/odoo/odoo10.conf')
    parser.add_argument("-d", "--dbname",
                        help="DB name",
                        dest="db_name",
                        metavar="file",
                        default='shs-av')
    parser.add_argument(
        "-o", "--oca-csv-file",
        help="csv file to read",
        dest="csv_fn_oca",
        metavar="file",
        default='/opt/odoo/10.0/addons/l10n_it/data/'
                'account.account.template.csv')
    parser.add_argument(
        "-z", "--z0-csv-file",
        help="csv file to read",
        dest="csv_fn_z0",
        metavar="file",
        default='/opt/odoo/10.0/l10n-italy/l10n_it_fiscal/data/'
                'account.account.template.csv')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    sys.exit(rename_coa(ctx))
