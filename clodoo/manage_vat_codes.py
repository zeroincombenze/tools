#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import oerplib
import re
from z0lib import parseoptargs
# import clodoo
import pdb


__version__ = "0.0.5"


RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
YELLOW_LIGHT = "\033[33m"
CLEAR = "\033[0;m"


VAT_SYNTAX = {
    '1_lAW_ID': re.compile(r'[Ll][.]?[0-9]+(/[0-9]+)?'),
    '1_WORD': re.compile(r'N\.[a-zA-Z]+[.]?'),
    '1_DPR': re.compile(r'DPR[.]?633'),
    '2_ABBR': re.compile(r'[A-Z][A-Z.]+[^a-z0-9]'),
    '2_VATP': re.compile(r'[0-9]+%'),
    '3_LAWITEM': re.compile(
        r'([0-9][-0-9a-z]+|a[0-9][-0-9a-z]*|l[0-9a]+)|art[0-9][-0-9a-z]*'),
    '4_WORD': re.compile(r'[a-zA-Z]+[.]?'),
    '5_NUMBER': re.compile(r'[0-9]+'),
    '9_LPAREN': re.compile(r'\('),
    '9_RPAREN': re.compile(r'\)'),
}


MARKER_DEBIT = ['debito',
                'Vend.',
                'vendite',
                'Vendite'
                ]

MARKER_CREDIT = ['credito',
                 'Acq.',
                 'acquisti',
                 'Acquisti',
                 ]

MARKER_SUSP = ['sospensione',
               'sospens.',
               'sosp.',
               'Sosp.']

MARKER_TAXABLE = ['imponibile',
                  'Imponibile']

MARKER_NOTAXABLE = ['NI',
                    'N.I',
                    'N.I.']

MARKER_EXCLUSION = ['escluso',
                    'Escluso',
                    'escl.',
                    'Escl.']

MARKER_EXEMPTION = ['esente',
                    'Esente',
                    'esen.',
                    'Esen.',
                    'es.',
                    'Es.']

MARKER_OUTOFSCOPE = ['fuori',
                     'Fuori',
                     'FC',
                     'F.C.']

MARKER_NOOBJ = ['N.Sogg.',
                'N.Sogg',
                'Sogg.',
                'Soggetto',
                'soggetto']

MARKER_WOTAX = ['senza',
                'Senza', ]

MARKER_REVCHARGE = ['reverse',
                    'Reverse',
                    'rev.',
                    'Rev.',
                    'rev.charge',
                    'Rev.charge',
                    'Rev.Charge',
                    'rev.Charge']

MARKER_VAT = ['IVA',
              'Iva',
              'I.V.A.']

MARKER_UNDEDUCTIBLE = ['indetraibile',
                       'indetr.',
                       'indet.',
                       'ind.']

MARKER_DEDUCTIBLE = ['detraibile',
                     'detr.',
                     'det.']

MARKER_CREDIT = MARKER_CREDIT + MARKER_UNDEDUCTIBLE + MARKER_DEDUCTIBLE

MARKER_REG_MINIMO = ['minimo',
                     'Minimo',
                     'min.',
                     'Min.', ]

MARKER_REG_MARGINE = ['margine',
                      'Margine',
                      'marg.',
                      'Marg.', ]

MARKER_SPECIAL = MARKER_REG_MINIMO + MARKER_REG_MARGINE

MARKER_REGIME = ['regime',
                 'Regime',
                 'reg.',
                 'Reg.', ]

MARKER_OTHERS = ['DPR633',
                 'quota',
                 'campo',
                 'da',
                 'su',
                 'no',
                 'No', ] + MARKER_REGIME

XTL_VATSCOPE = {'purchase': 'credit',
                'sale': 'debit',
                }

# OCA Italy
CODE_ITEM_OCA = {'prefix': 'IV',
                 'pfx_credit': 'C',
                 'pfx_debit': 'D',
                 'pfx_later_credit': 'P',
                 'pfx_later_debit': 'S',
                 'pfx_det': 'det',
                 'pfx_ind': 'ind',
                 'sfx_credit': '',
                 'sfx_debit': '',
                 'sfx_amt': 'I',
                 'sfx_det_amt': 'I',
                 'sfx_undet_amt': 'I',
                 'sfx_vat': '',
                 'sfx_det': '',
                 'sfx_undet': 'N',
                 }

# Zeroincombenze
CODE_ITEM_OIA = {'prefix': 'IT',
                 'pfx_credit': 'C',
                 'pfx_debit': 'D',
                 'pfx_later_credit': 'P',
                 'pfx_later_debit': 'S',
                 'pfx_det': 'd',
                 'pfx_ind': '',
                 'sfx_credit': '',
                 'sfx_debit': '',
                 'sfx_amt': 'D',
                 'sfx_det_amt': 'D',
                 'sfx_undet_amt': 'I',
                 'sfx_vat': 'V',
                 'sfx_det': 'V',
                 'sfx_undet': 'N',
                 }

CODE_ITEM_TAX = {'prefix': '',
                 'prefix_noVAT': 'a',
                 'prefix_law': 'l',
                 'pfx_credit': '',
                 'pfx_debit': '',
                 'pfx_later_credit': '',
                 'pfx_later_debit': '',
                 'pfx_det': '',
                 'pfx_ind': '',
                 'sfx_credit': 'a',
                 'sfx_debit': 'v',
                 'sfx_amt': '',
                 'sfx_det_amt': '',
                 'sfx_undet_amt': '',
                 'sfx_vat': '',
                 'sfx_det': 'a',
                 'sfx_undet': 'b',
                 }


def oerp_set_env(confn=None, db=None, ctx=None):
    xmlrpc_port = 8069
    db_name = 'demo'
    user = 'admin'
    passwd = 'admin'
    oe_ver = '7.0'
    svc_protocol = ''
    confn = confn or './inv2draft_n_restore.conf'
    write_confn = False
    try:
        fd = open(confn, 'r')
        lines = fd.read().split('\n')
        for line in lines:
            tkn = line.split('=')
            if tkn[0] == 'login_user':
                user = tkn[1]
            elif tkn[0] == 'login_password':
                passwd = tkn[1]
            elif tkn[0] == 'db_name':
                database = tkn[1]
            elif tkn[0] == 'xmlrpc_port':
                xmlrpc_port = int(tkn[1])
            elif tkn[0] == 'oe_version':
                oe_ver = tkn[1]
            elif tkn[0] == 'svc_protocol':
                svc_protocol = tkn[1]
        fd.close()
    except:
        write_confn = True
        database = raw_input('database[def=demo]? ')
        user = raw_input('username[def=admin]? ')
        passwd = raw_input('password[def=admin]? ')
        p = raw_input('port[def=8069]? ')
        if p:
            xmlrpc_port = int(p)
        p = raw_input('odoo version[def=7.0]? ')
        if p:
            oe_ver = p
        p = raw_input('protocol(jsonrpc|xmlrpc)? ')
        if p:
            svc_protocol = p

    oerp = oerplib.OERP(port=xmlrpc_port, version=oe_ver)
    if db:
        uid = oerp.login(user=user,
                         passwd=passwd, database=db)
    else:
        uid = oerp.login(user=user,
                         passwd=passwd, database=database)
    if write_confn:
        fd = open(confn, 'w')
        fd.write('login_user=%s\n' % user)
        fd.write('login_password=%s\n' % passwd)
        fd.write('db_name=%s\n' % database)
        if xmlrpc_port != 8069:
            fd.write('xmlrpc_port=%d\n' % xmlrpc_port)
        if oe_ver:
            fd.write('oe_version=%s\n' % oe_ver)
        if svc_protocol:
            fd.write('svc_protocol=%s\n' % svc_protocol)
        fd.close()

    ctx = ctx or {}
    ctx['level'] = 4
    if 'dry_run' not in ctx:
        ctx['dry_run'] = False
    if not svc_protocol:
        if oe_ver in ('6.1', '7.0'):
            svc_protocol = 'xmlrpc'
        else:
            svc_protocol = 'jsonrpc'
    ctx['svc_protocol'] = svc_protocol
    ctx['odoo_session'] = oerp
    return oerp, uid, ctx


def pdet2pind(value):
    return str(100 - int(value))


def pind2pdet(value):
    return str(100 - int(value))


def exp_des(i, des, words, tokids):
    valid = False
    j = i
    while i < len(tokids):
        if tokids[i] not in ('9_LPAREN', '9_RPAREN',
                             '1_lAW_ID', '1_DPR') and \
                words[i] not in MARKER_DEBIT and \
                words[i] not in MARKER_CREDIT and \
                words[i] not in MARKER_SUSP and \
                words[i] not in MARKER_TAXABLE and \
                words[i] not in MARKER_NOTAXABLE and \
                words[i] not in MARKER_EXCLUSION and \
                words[i] not in MARKER_EXEMPTION and \
                words[i] not in MARKER_OUTOFSCOPE and \
                words[i] not in MARKER_NOOBJ and \
                words[i] not in MARKER_WOTAX and \
                words[i] not in MARKER_REVCHARGE and \
                words[i] not in MARKER_VAT and \
                words[i] not in MARKER_UNDEDUCTIBLE and \
                words[i] not in MARKER_DEDUCTIBLE and \
                words[i] not in MARKER_SPECIAL and \
                words[i] not in MARKER_OTHERS:
            valid = True
        i += 1
    i = j
    if valid:
        sp = ''
        while i < len(tokids):
            if tokids[i] == '9_LPAREN':
                des += ' ' + words[i]
                sp = ''
            elif tokids[i] == '9_RPAREN':
                des += words[i]
                sp = ' '
            elif tokids[i] not in ('1_lAW_ID', '1_DPR') and \
                    words[i] not in MARKER_DEBIT and \
                    words[i] not in MARKER_CREDIT and \
                    words[i] not in MARKER_SUSP and \
                    words[i] not in MARKER_TAXABLE and \
                    words[i] not in MARKER_NOTAXABLE and \
                    words[i] not in MARKER_EXCLUSION and \
                    words[i] not in MARKER_EXEMPTION and \
                    words[i] not in MARKER_OUTOFSCOPE and \
                    words[i] not in MARKER_NOOBJ and \
                    words[i] not in MARKER_WOTAX and \
                    words[i] not in MARKER_REVCHARGE and \
                    words[i] not in MARKER_VAT and \
                    words[i] not in MARKER_UNDEDUCTIBLE and \
                    words[i] not in MARKER_DEDUCTIBLE and \
                    words[i] not in MARKER_SPECIAL and \
                    words[i] not in MARKER_OTHERS:
                des += sp + words[i]
                sp = ' '
            i += 1
    return des


def parse_des(des):
    """Extract word from description into list"""
    words = []
    tokids = []
    ipos = 0
    while ipos < len(des):
        unknown = True
        for istkn in sorted(VAT_SYNTAX):
            x = VAT_SYNTAX[istkn].match(des[ipos:])
            # print "<<<%s>>>" % (istkn)
            if x:
                unknown = False
                i = ipos
                ipos += x.end()
                token = des[i:ipos].strip()
                break
        if unknown:
            # print "<%s>" % des[ipos]
            ipos += 1
        else:
            # print "<<%s>>" % des[i:ipos]
            words.append(token)
            tokids.append(istkn)
    return words, tokids


def set_code_meaning(code, chash=None, table=None, defcd=None, is_quota=None):
    """Parse code into dictionary code_meaning
    - owner: rule coding (OCA | Odoo Italia Association)
    - crddbt: size (debit | credit | later_debit | later_credit)
    - type: (amt | vat | undet_amt | det_amt | undet)
    - aliq: VAT aliquote or VAT application law
    - code_aliq: aliq code
    - detr: deductible quote
    - vat_apply: (apply, | no_vat)
    """
    table = table or 'tax.code'
    defcd = defcd or ''
    code_meaning = {}
    for p in ('crddbt', 'type', 'code_aliq', 'aliq', 'vat_apply', 'pind'):
        code_meaning[p] = ''
    code_meaning['company'] = ''
    if chash:
        for c in chash:
            if not c or not code:
                continue
            minpos = len(code) - len(c) - 1
            i = code.rfind(c)
            if minpos >= 0 and i >= minpos:
                code_meaning['company'] = c
                j = i + len(c)
                if j < len(code):
                    code = code[0:i] + code[j:]
                else:
                    code = code[0:i]
    code_subtype = ''
    if table == 'tax.code':
        if not code or code[0:2] == 'IT':
            code_meaning['owner'] = 'OIA'
            CODE_ITEM = CODE_ITEM_OIA
        else:
            code_meaning['owner'] = 'OCA'
            CODE_ITEM = CODE_ITEM_OCA
    else:
        code_meaning['owner'] = 'OIA'
        CODE_ITEM = CODE_ITEM_TAX
    if code:
        if table == 'tax.code':
            ipos = 2
            if code[ipos] == CODE_ITEM['pfx_credit']:
                code_meaning['crddbt'] = 'credit'
            elif code[ipos] == CODE_ITEM['pfx_debit']:
                code_meaning['crddbt'] = 'debit'
            elif code[ipos] == CODE_ITEM['pfx_later_credit']:
                code_meaning['crddbt'] = 'later_credit'
            elif code[ipos] == CODE_ITEM['pfx_later_debit']:
                code_meaning['crddbt'] = 'later_debit'
            else:
                code_meaning['crddbt'] = '?'
            type_def = False
            if code_meaning['owner'] == 'OIA':
                if code[-1] == CODE_ITEM['sfx_amt']:
                    code_meaning['type'] = 'amt'
                elif code[-1] == CODE_ITEM['sfx_undet_amt']:
                    code_meaning['type'] = 'undet_amt'
                    code_meaning['pind'] = '100'
                elif code[-1] == CODE_ITEM['sfx_det_amt']:
                    code_meaning['type'] = 'det_amt'
                elif code[-1] == CODE_ITEM['sfx_vat']:
                    code_meaning['type'] = 'vat'
                elif code[-1] == CODE_ITEM['sfx_undet']:
                    code_meaning['type'] = 'undet'
                    code_meaning['pind'] = '100'
                elif code[-1] == CODE_ITEM['sfx_det']:
                    code_meaning['type'] = 'det'
                else:
                    code_meaning['type'] = 'vat'
                    type_def = True
            ipos += 1
        else:
            ipos = 0
            if code[ipos] == CODE_ITEM['prefix_noVAT']:
                ipos += 1
            if code[ipos] == CODE_ITEM['prefix_law']:
                ipos += 1
        code_meaning['aliq'] = '?'
        x = VAT_SYNTAX['5_NUMBER'].match(code[ipos:])
        if x:
            i = ipos
            ipos += x.end()
            if (ipos - i) > 2:
                ipos -= 2
                code_meaning['code_aliq'] = code[i:ipos]
                i += 2
                ipos +=2
                code_meaning['pind'] = pdet2pind(code[i:ipos])
            else:
                code_meaning['code_aliq'] = code[i:ipos]
            if int(code_meaning['code_aliq']) == 0 and (len(code) - ipos) > 1:
                x = False
        if x:
            code_meaning['aliq'] = code_meaning['code_aliq'] + '%'
            if code_meaning['aliq'] == '0%':
                code_meaning['aliq'] = ''
            code_meaning['vat_apply'] = 'apply'
        else:
            if type_def:
                x = VAT_SYNTAX['3_LAWITEM'].match(code[ipos:])
            else:
                x = VAT_SYNTAX['3_LAWITEM'].match(code[ipos:-1])
            if x:
                i = ipos
                ipos += x.end()
                code_meaning['code_aliq'] = code[i:ipos]
                if code_meaning['code_aliq'][0:3] == 'art':
                    code_meaning['aliq'] = code_meaning['code_aliq'][3:]
                elif code_meaning['code_aliq'][0] == 'a' or \
                        code_meaning['code_aliq'][0] == 'l':
                    code_meaning['aliq'] = code_meaning['code_aliq'][1:]
                else:
                    code_meaning['aliq'] = code_meaning['code_aliq']
            code_meaning['vat_apply'] = 'no_vat'
        if ipos < len(code) and code[ipos].startswith(CODE_ITEM['pfx_det']):
            ipos += len(CODE_ITEM['pfx_det'])
            x = VAT_SYNTAX['5_NUMBER'].match(code[ipos:])
            if x:
                i = ipos
                ipos += x.end()
                code_meaning['pind'] = pdet2pind(code[i:ipos])
        elif ipos < len(code) and code[ipos].startswith(CODE_ITEM['pfx_ind']):
            ipos += len(CODE_ITEM['pfx_ind'])
            x = VAT_SYNTAX['5_NUMBER'].match(code[ipos:])
            if x:
                i = ipos
                ipos += x.end()
                code_meaning['pind'] = code[i:ipos]
        if defcd and code_meaning['crddbt'] in ('?', ''):
            code_meaning['crddbt'] = defcd
        if table != 'tax.code':
            if 'pind'in code_meaning:
                code_meaning['type'] = 'undet'
            else:
                code_meaning['type'] = 'vat'
    return code_meaning, CODE_ITEM


def w_undet(i, found_quota, des_meaning):
    if found_quota:
        des_meaning['quota'] = 'indet'
    if des_meaning['crddbt'] == '?':
        des_meaning['crddbt'] = 'credit'
    i += 1
    return i, des_meaning


def w_det(i, found_quota, des_meaning):
    des_meaning['pind'] = '%s%%' % pind2pdet(des_meaning['pind'][0:-1])
    if found_quota:
        des_meaning['quota'] = 'detr'
    if des_meaning['crddbt'] == '?':
        des_meaning['crddbt'] = 'credit'
    i += 1
    return i, des_meaning


def set_des_meaning(des, table=None, is_quota=None):
    """Parse description into dictionary des_meaning
    - crddbt: size (debit | credit | later_debit | later_credit)
    - type: (amt | vat | undet_amt | det_amt | undet)
    - aliq: VAT aliquote or VAT application law
    - detr: deductible quote
    - vat_apply: (
          imponibile | N.I. | escluso | esente | iva | regime | N.Sogg. | senza IVA | rev.charge)
    - next: next word to append
    - quota: if record is VAT quota (detr | indet)
    """
    table = table or 'tax.code'
    words, tokids = parse_des(des)
    des_meaning = {}
    des_meaning['pind'] = ''
    des_meaning['law'] = ''
    if [x for x in MARKER_DEBIT if x in words]:
        des_meaning['crddbt'] = 'debit'
    elif [x for x in MARKER_CREDIT if x in words]:
        des_meaning['crddbt'] = 'credit'
    else:
        des_meaning['crddbt'] = '?'
    if [x for x in MARKER_SUSP if x in words]:
        des_meaning['crddbt'] = 'later_' + des_meaning['crddbt']

    des_meaning['type'] = 'vat'
    if [x for x in MARKER_TAXABLE if x in words]:
        des_meaning['vat_apply'] = 'imponibile'
        if [x for x in MARKER_UNDEDUCTIBLE if x in words]:
            des_meaning['type'] = 'undet_amt'
            if des_meaning['crddbt'] == '?':
                des_meaning['crddbt'] = 'credit'
            des_meaning['pind'] = '100%'
        else:
            des_meaning['type'] = 'amt'
    elif [x for x in MARKER_NOTAXABLE if x in words]:
        des_meaning['vat_apply'] = 'N.I.'
        if [x for x in MARKER_VAT if x in words]:
            des_meaning['type'] = 'vat'
        else:
            des_meaning['type'] = 'amt'
    elif [x for x in MARKER_EXCLUSION if x in words]:
        des_meaning['vat_apply'] = 'escluso'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_EXEMPTION if x in words]:
        des_meaning['vat_apply'] = 'esente'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_OUTOFSCOPE if x in words]:
        des_meaning['vat_apply'] = 'FC IVA'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_NOOBJ if x in words]:
        des_meaning['vat_apply'] = 'N.Sogg.'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_WOTAX if x in words]:
        des_meaning['vat_apply'] = 'senza IVA'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_REVCHARGE if x in words]:
        des_meaning['vat_apply'] = 'rev.charge'
        if [x for x in MARKER_VAT if x in words]:
            des_meaning['type'] = 'vat'
        else:
            des_meaning['type'] = 'amt'
    elif [x for x in MARKER_SPECIAL if x in words]:
        des_meaning['vat_apply'] = 'regime'
        des_meaning['type'] = 'amt'
    elif [x for x in MARKER_VAT if x in words]:
        des_meaning['vat_apply'] = 'iva'
        if [x for x in MARKER_UNDEDUCTIBLE if x in words]:
            des_meaning['type'] = 'undet'
            if des_meaning['crddbt'] == '?':
                des_meaning['crddbt'] = 'credit'
        else:
            des_meaning['type'] = 'vat'
    else:
        des_meaning['vat_apply'] = '?'
    des_meaning['aliq'] = '?'
    i = 0
    while i < len(tokids):
        if tokids[i] == '2_VATP':
            des_meaning['aliq'] = words[i]
            break
        elif tokids[i] == '3_LAWITEM':
            des_meaning['aliq'] = words[i]
            break
        elif tokids[i] == '5_NUMBER':
            des_meaning['aliq'] = words[i]
            break
        i += 1
    i += 1
    if i < len(tokids) and tokids[i] in ('1_lAW_ID', '1_DPR'):
        des_meaning['law'] = words[i]
        i += 1
    if i < len(tokids):
        des_meaning['next'] = i
    else:
        des_meaning['next'] = ''
    if is_quota:
        found_quota = True
    else:
        found_quota = False
    pos_idet = 0
    while i < len(tokids):
        if words[i] == 'quota':
            found_quota = True
        elif words[i] in MARKER_UNDEDUCTIBLE:
            pos_idet = i
        elif words[i] in MARKER_DEDUCTIBLE:
            pos_idet = i
        elif tokids[i] == '2_VATP':
            des_meaning['pind'] = words[i]
            break
        i += 1
    if i < len(tokids):
        i += 1
    if pos_idet:
        if words[pos_idet] in MARKER_UNDEDUCTIBLE:
            pos_idet, des_meaning = w_undet(pos_idet, found_quota, des_meaning)
        elif words[pos_idet] in MARKER_DEDUCTIBLE:
            pos_idet, des_meaning = w_det(pos_idet, found_quota, des_meaning)
    elif i < len(tokids):
        if words[i] in MARKER_UNDEDUCTIBLE:
            i, des_meaning = w_undet(i, found_quota, des_meaning)
        elif words[i] in MARKER_DEDUCTIBLE:
            i, des_meaning = w_det(i, found_quota, des_meaning)
    if found_quota and 'quota' not in des_meaning:
        des_meaning['quota'] = 'indet'
    if i < len(tokids) or pos_idet:
        des_meaning['next'] = i
    return des_meaning, words, tokids


def build_code(code_meaning, CODE_ITEM, table=None, is_quota=None):
    table = table or 'tax.code'
    newcode = CODE_ITEM['prefix']
    x = 'pfx_' + code_meaning['crddbt']
    if x in CODE_ITEM:
        newcode += CODE_ITEM[x]
    newcode += code_meaning['code_aliq']
    if code_meaning['pind'] and \
            code_meaning['pind'] != '0' and \
            code_meaning['pind'] != '100':
        if table == 'tax.code':
            newcode += CODE_ITEM['pfx_det']
        newcode += pind2pdet(code_meaning['pind'])
    if table == 'tax.code' or is_quota:
        if code_meaning['type'] == 'undet_amt' and \
                code_meaning['pind'] != '100':
            x = 'sfx_amt'
        else:
            x = 'sfx_' + code_meaning['type']
        if x in CODE_ITEM:
            newcode += CODE_ITEM[x]
    elif not code_meaning['pind']:
        x = 'sfx_' + code_meaning['crddbt']
        if x in CODE_ITEM:
            newcode += CODE_ITEM[x]
    if code_meaning.get('company', ''):
        newcode += code_meaning['company'].lower()
    return newcode


def build_des(des_meaning, words, tokids, table=None):
    table = table or 'tax.code'
    newdes = ''
    if des_meaning['vat_apply'] in ('N.I.', 'escluso',
                                    'FC IVA', 'esente',
                                    'N.Sogg.', 'senza IVA',
                                    'rev.charge', 'regime'):
        if des_meaning['vat_apply'] == 'N.I.' and 'IVA' in words:
            if des_meaning['crddbt'] == 'credit':
                newdes += 'Integrazione IVA'
            else:
                newdes = 'IVA'
        elif des_meaning['vat_apply'] == 'rev.charge':
            if 'IVA' in words:
                if des_meaning['crddbt'] == 'debit':
                    newdes += 'IVA autofatture'
                else:
                    newdes = 'IVA'
            else:
                newdes += 'Rev.charge'
        elif des_meaning['crddbt'] == 'credit':
            newdes += 'Acq.'
            if des_meaning['vat_apply'] != 'regime':
                newdes += des_meaning['vat_apply']
        elif des_meaning['crddbt'] == 'debit':
            newdes += 'Vend.'
            if des_meaning['vat_apply'] != 'regime':
                newdes += des_meaning['vat_apply']
        newdes += ' art.%s' % des_meaning['aliq']
        if 'law' in des_meaning:
            newdes += ' %s' % des_meaning['law']
        if [x for x in MARKER_REGIME if x in words]:
            if [x for x in MARKER_REG_MINIMO if x in words]:
                newdes += ' (regime minimo)'
            elif [x for x in MARKER_REG_MARGINE if x in words]:
                newdes += ' (reg. di margine)'
    else:
        if des_meaning['vat_apply'] == 'imponibile':
            newdes = 'Imponibile'
        elif des_meaning['vat_apply'] == 'iva':
            newdes = 'IVA'
        if des_meaning['aliq']:
            newdes += ' ' + des_meaning['aliq']
        if des_meaning['crddbt'] == 'credit':
            if table != 'tax.code' and 'quota' in des_meaning:
                if table == 'tax.code' or des_meaning['pind'] == '100%':
                    newdes += ' indetraibile'
            elif (des_meaning['type'] == 'undet' or
                    des_meaning['type'] == 'undet_amt') and \
                    'quota' not in des_meaning:
                if table == 'tax.code' or des_meaning['pind'] == '100%':
                    newdes += ' indetraibile'
            else:
                if des_meaning['aliq']:
                    newdes += ' da acq.'
                else:
                    newdes += ' da acquisti'
        elif des_meaning['crddbt'] == 'debit':
            if des_meaning['aliq']:
                newdes += ' su vend.'
            else:
                newdes += ' su vendite'
        elif des_meaning['crddbt'] == 'later_credit':
            if des_meaning['aliq']:
                newdes += ' cred. per cassa'
            else:
                newdes += ' credito per cassa'
        elif des_meaning['crddbt'] == 'later_debit':
            if des_meaning['aliq']:
                newdes += ' debito sosp. per cassa'
            else:
                newdes += ' in sospensione a debito per cassa'
        if des_meaning['pind'] and ('quota' in des_meaning or
                                    des_meaning['pind'] not in ('100%', '0%')):
            if 'quota' in des_meaning:
                if des_meaning['quota'] == 'indet':
                    newdes += ' (quota %s indet.)' % des_meaning['pind']
                else:
                    if table == 'tax.code':
                        newdes += ' (quota %s%% detr.)' % pind2pdet(
                            des_meaning['pind'][0:-1])
                    else:
                        newdes += ' detraibile %s%%' % pind2pdet(
                            des_meaning['pind'][0:-1])
            else:
                if table == 'tax.code':
                    # newdes += ' (%s indetr.)' % des_meaning['pind']
                    newdes += ' (quota %s%% detr.)' % pind2pdet(
                        des_meaning['pind'][0:-1])
                else:
                    newdes += ' detraibile %s%%' % pind2pdet(
                        des_meaning['pind'][0:-1])
    if des_meaning['next']:
        newdes = exp_des(des_meaning['next'], newdes, words, tokids)
    return newdes


def hint_code_des(code, des, chash=None, table=None, defcd=None, is_quota=None):
    table = table or 'tax.code'
    record_sts = 'active'
    chash = ['Cserv', 'CServ', 'cserv', 'Cstudi', 'Cstudi', 'cstudi']
    code_meaning, CODE_ITEM = set_code_meaning(code, chash=chash,
                                               table=table, defcd=defcd,
                                               is_quota=is_quota)
    # print code_meaning      # debug
    des_meaning, words, tokids = set_des_meaning(des, table=table,
                                                 is_quota=is_quota)
    # print des_meaning      # debug
    # match code and description meaning
    code_des_match = True
    for p in ('crddbt', 'type', 'aliq', 'vat_apply'):
        if code_meaning[p] != des_meaning[p]:
            # code does not math description
            if code_meaning[p] == '?':
                code_meaning[p] = des_meaning[p]
            elif des_meaning[p] == '?':
                des_meaning[p] = code_meaning[p]
            elif p == 'crddbt':
                if code_meaning[p].startswith('later_') and \
                        code_meaning[p].find(des_meaning[p]) >= 0:
                    des_meaning[p] = 'later_' + des_meaning[p]
                elif des_meaning[p].startswith('later_') and \
                        des_meaning[p].find(code_meaning[p]) >= 0:
                    code_meaning[p] = 'later_' + code_meaning[p]
                elif des_meaning[p] == ('later_?') and \
                        code_meaning[p].startswith('later_'):
                    des_meaning[p] = code_meaning[p]
                else:
                    code_des_match = False
            elif p == 'type':
                # - type: (amt, vat, undet_amt, undet)
                if code_meaning[p] == 'undet' and \
                        des_meaning[p] == 'undet_amt':
                    code_meaning[p] = des_meaning[p]
                elif des_meaning[p] == 'undet' and \
                        code_meaning[p] == 'undet_amt':
                    des_meaning[p] = code_meaning[p]
                elif des_meaning[p] == 'amt' and \
                        code_meaning[p] == 'undet_amt':
                    des_meaning[p] = code_meaning[p]
                elif code_meaning[p] == 'undet' and \
                        des_meaning[p] == 'vat':
                    des_meaning[p] = code_meaning[p]
                else:
                    code_des_match = False
            elif p == 'aliq':
                if 'law' in des_meaning and \
                        des_meaning['law'].find(code_meaning['aliq']) >= 0:
                    pass
                elif code_meaning['aliq'].isdigit() and \
                        des_meaning['aliq'].find(code_meaning['aliq']) >= 0:
                    pass
                elif des_meaning['aliq'].isdigit() and \
                        code_meaning['aliq'].find(des_meaning['aliq']) >= 0:
                    pass
            elif p == 'vat_apply':
                if code_meaning[p] == 'apply' and \
                        des_meaning[p] in ('imponibile', 'iva'):
                    code_meaning[p] = des_meaning[p]
                elif code_meaning[p] == 'no_vat' and \
                        des_meaning[p] in ('N.I.',
                                           'escluso',
                                           'FC IVA',
                                           'N.Sogg.',
                                           'senza IVA',
                                           'rev.charge',
                                           'esente',
                                           'regime'):
                    code_meaning[p] = des_meaning[p]
                else:
                    code_des_match = False
    if code_meaning['aliq'] == '20%' or code_meaning['aliq'] == '21%' or \
            code_meaning['aliq'] == '12%':
        record_sts = ''
    if code_des_match:   # debug
        newdes = build_des(des_meaning, words, tokids, table=table)
        newcode = build_code(code_meaning, CODE_ITEM,
                             table=table, is_quota=is_quota)
    else:
        print "<<<Code %s not managed>>>" % code
        newcode = code
        newdes = des
    if table == 'tax.code':
        proposed = build_code(code_meaning, CODE_ITEM_OIA,
                              table=table, is_quota=is_quota)
    else:
        proposed = build_code(code_meaning, CODE_ITEM,
                              table=table, is_quota=is_quota)
    return newcode, newdes, proposed


if __name__ == "__main__":
    parser = parseoptargs("Manage VAT code",
                          "© 2017-2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    oerp, uid, ctx = oerp_set_env(ctx=ctx)

    company_ids = oerp.search('res.company')
    # pdb.set_trace()

    print
    print 'Analyzing Taxes'
    kk = 'description'
    table='tax'
    for company_id in company_ids:
        # pdb.set_trace()
        model = 'account.tax'
        tax_ids = oerp.search(model,
                              [('company_id', '=', company_id)],
                              order=kk)
        for tax_id in tax_ids:
            tax = oerp.browse(model, tax_id)
            is_quota = tax.parent_id
            print '%s%2.2d  %-12.12s %-60.60s%s' % (RED,
                                                    company_id,
                                                    tax[kk],
                                                    tax.name,
                                                    CLEAR)
            newcode, newdes, proposed = hint_code_des(tax[kk],
                                                      tax.name,
                                                      table=table,
                                                      defcd=XTL_VATSCOPE[
                                                          tax.type_tax_use],
                                                      is_quota=is_quota)
            print '%s%2.2d  %-12.12s %-60.60s%s' % (GREEN,
                                                    company_id,
                                                    newcode,
                                                    newdes,
                                                    CLEAR)
            if newcode != tax[kk]:
                print "^^^^^ ??????"
    sys.exit(0)

    print
    print 'Analyzing Tax Accounts'
    kk = 'code'
    table='tax.code'
    for company_id in company_ids:
        # pdb.set_trace()
        model = 'account.tax.code'
        tax_ids = oerp.search(model,
                              [('company_id', '=', company_id)],
                              order=kk)
        for tax_id in tax_ids:
            tax = oerp.browse(model, tax_id)
            print '%s%2.2d  %-12.12s %-60.60s%s' % (RED,
                                                    company_id,
                                                    tax[kk],
                                                    tax.name,
                                                    CLEAR)
            newcode, newdes, proposed = hint_code_des(tax[kk],
                                                      tax.name,
                                                      table=table)
            print '%s%2.2d  %-12.12s %-60.60s%s' % (GREEN,
                                                    company_id,
                                                    newcode,
                                                    newdes,
                                                    CLEAR)
            if newcode != tax[kk]:
                print "^^^^^ ??????"
            # break    # debug
        print
        print
