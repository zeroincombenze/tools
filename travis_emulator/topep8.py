#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Convert src python to PEP8 with OCA rules
"""

# import pdb
# import os
import sys
import re
from z0lib import parseoptargs
import tokenize


__version__ = "0.2.0.15"


ISALNUM_B = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*')
ISDOCSEP1 = re.compile('"""')
ISDOCSEP2 = re.compile("'''")
IS_ASSIGN = re.compile('[a-zA-Z_][a-zA-Z0-9_]* *=')
IS_ASSIGN_B = re.compile('^[a-zA-Z_][a-zA-Z0-9_]* *=')
IS_DEF = re.compile('def +')
IS_CLASS = re.compile('class +')

SYNTAX = {
    'space': re.compile('\s+'),
    'lparen': re.compile('\('),
    'rparen': re.compile('\)'),
    'lbrace': re.compile('\['),
    'rbrace': re.compile('\]'),
    'lbracket': re.compile('\{'),
    'rbracket': re.compile('\}'),
    'isalnum': re.compile('[a-zA-Z_][\w]*'),
    'isdigit': re.compile('[\d]+'),
    'begdoc1': re.compile('"""'),
    'begdoc2': re.compile('"""'),
    'begremark': re.compile('#'),
    'begtxt1': re.compile('"{1,2}($|[^"])'),
    'begtxt2': re.compile("'{1,2}($|[^'])"),
    'dot': re.compile('\.'),
    'comma': re.compile(','),
    'colon': re.compile(':'),
    'assign': re.compile('='),
    'op': re.compile(r'[-\\!%&+/|^?<=>]+'),
}

RULES = r"""
*IS*        ^ *class.*[:tok:]
 v60        osv.osv_memory
 v61        orm.TransientModel
 v80        models.TransientModel
*IS*        ^ *class.*[:tok:]
 v60        osv.osv
 v61        orm.Model
 v80        models.Model
*IS*        import .*[:tok:]
 v60        osv
 v61        orm
 v80        models
*IS*        ^from [:tok:]
 v60        osv
 v61        openerp.osv
 v100       odoo
*IS*        ^[:tok:]
 v60        from tools.translate import
 v61        from openerp.tools.translate import
 v100       from odoo.tools.translate import
*IS*        ^[:tok:]
 v60        import decimal_precision
 v80        import openerp.addons.decimal_precision
 v100       import odoo.addons.decimal_precision
*IS*        ^[:tok:]
 v60        import openerp.addons.decimal_precision
 v80        from openerp.addons.decimal_precision import decimal_precision
 v100       from odoo.addons.decimal_precision import decimal_precision
*IS*        [:tok:]
 v60        openerp.addons.base
 v100       odoo.addons.base
*IS*        ^import (api|exceptions|fields|http|loglevels|models|netsvc|\
pooler|release|sql_db)
 v60        import
 v61        from openerp import
 v100       from odoo import
*IS*        ^from (openerp|odoo)\.addons\.web import http
 v60        from openerp.addons.web import http
 v100       from odoo import http
*IS*        ^.*import (openerp|odoo)\.addons\.web\.http
 v60        openerp.addons.web.http
 v100       odoo.http
*IS*        ^[:tok:]
 v60        from openerp import
 v100       from odoo import
*IS*        ^ *class\.*orm\.
 v60        orm
 v80        models
*IS*        [:tok:]
 v60        osv.except_osv
 v80        UserError
*IS*        [:tok:]
 v60        openerp.tools.config
 v100       odoo.tools.config
*IS*        [:tok:]
 v60        fields.boolean
 v90        fields.Boolean
*IS*        [:tok:]
 v60        fields.char
 v90        fields.Char
*IS*        [:tok:]
 v60        fields.text
 v90        fields.Text
*IS*        [:tok:]
 v60        fields.html
 v90        fields.Html
*IS*        [:tok:]
 v60        fields.integer
 v90        fields.Integer
*IS*        [:tok:]
 v60        fields.float
 v90        fields.Float
*IS*        [:tok:]
 v60        fields.date
 v90        fields.Date
*IS*        [:tok:]
 v60        fields.datetime
 v90        fields.Datetime
*IS*        [:tok:]
 v60        fields.binary
 v90        fields.Binary
*IS*        [:tok:]
 v60        fields.selection
 v90        fields.Selection
*IS*        [:tok:]
 v60        fields.reference
 v90        fields.Reference
*IS*        [:tok:]
 v60        fields.many2one
 v90        fields.Many2one
*IS*        [:tok:]
 v60        fields.one2many
 v90        fields.One2many
*IS*        [:tok:]
 v60        fields.many2many
 v90        fields.Many2many
*IS*   #    openerp.com
 v0         odoo.com
*IS*   #    OpenERP
 v0         Odoo
*IS*   #    openerp-italia.org
 v0         odoo-italia.org
*IS*   #    formerly Odoo
 v0         formerly OpenERP
*IS*   -u   class [\w.]+\((TransactionCase|SingleTransactionCase|RpcCase)\)
 v0         &
*IS*   +2   ^[a-zA-Z_][\w.]* *\(
 v0         &
*IS*   +2   ^if __name__ == .__main__.:
 v0         &
*IS*   +2   ^def +
 v0         &
*IS*   +2   ^class +
 v0         &
*IS*   *2   ^[a-zA-Z_][\w.]* *=
 v0         &
#
*IS*   +B   ^ +tndb\.
 v0         # tndb.
*IS*   +b   ^from tndb
 v0         # from tndb
*IS*   +b   ^ +pdb\.
 v0         # pdb.
*IS*   +b   ^import pdb
 v0         # import pdb
*IS*   -B   # tndb\.
 v0         tndb.
*IS*   -b   # from tndb
 v0         from tndb
*IS*   -b   # pdb
 v0         pdb
*IS*   -b   # import pdb
 v0         import pdb
*IS*   ||   ^( +or +.*| +or)$
 v0         &
*IS*   &&   ^( +and +.*| +and)$
 v0         &
*IS*   ^+   ^ +\+ *
 v0         &
*IS*   ^-   ^ +- *
 v0         &
*IS*  del1  if context is None:
 v0         context = {} if context is None else context
*IS*  del1  if ctx is None:
 v0         ctx = {} if ctx is None else ctx
*IS*   -u1  \.search\(
 v0         &
*IS*   -u1  \.env\[
 v0         &
*IS*   -u1  \.write\(
 v0         &
*IS*   -u1  \.create\(
 v0         &
*IS*   -u1  \.browse\(
 v0         &
*IS*   -u1  \.unlink\(
 v0         &
*IS*   -u1  \.find\(\)
 v0         &
*IS*   -u1  \.env\.ref\(
 v0         &
*IS*  trvs  ^ *except[ :]
 v0         &
*IS*  trvs  ^ *raise[ ]
 v0         &
"""

SPEC_SYNTAX = {
    'equ1': [True, '='],
    'equ2': [True, '.', True, '='],
    'env1': ['self', '.', 'env', '['],
    'env2': ['self', '.', 'env', '.', 'ref', '('],
    'icr1': ['self', '.', True, '.', 'search', '('],
    'icr2': ['self', '.', True, '.', 'write', '('],
    'icr3': ['self', '.', True, '.', 'create', '('],
    'icr4': ['self', '.', True, '.', 'browse', '('],
    'icr5': ['self', '.', True, '.', 'unlink', '('],
    'icr6': ['self', '.', True, '.', 'find', '('],
    'clo1': [')', ],
    'clo2': [']', ],
    'clo3': ['}', ],
    'clo4': [')', '.', True],
}

IS_BADGE = {}
IS_BADGE_TXT = {}
META = {}
RID = {}
REPL_CTRS = {}
SRC_TOKENS = {}
TGT_TOKENS = {}
LAST_RID = -1


def txt2regex(token):
    if token[0] != '^':
        token = '.*' + token
    return token.replace('.', '\.')


def regex2txt(token):
    if token and token[0] == '^':
        token = token[1:]
    if token[-1] == '$':
        token = token[0:-1]
    tok = token.replace(
        '.*', '').replace(
        ' *', '').replace(
        ' +', '').replace(
        '\(', '(').replace(
        '\)', ')').replace(
        '\[', '[').replace(
        '\[', '[').replace(
        '\{', '}').replace(
        '\{', '}').replace(
        '\.', '.')
    return tok


def prior_ver(ver):
    if ver == 61:
        return 60
    elif ver == 70:
        return 61
    return ver - 10


def ver2ix(ver):
    if ver in ('6.0', '6.1', '7.0', '8.0', '9.0', '10.0'):
        return int(eval(ver) * 10)
    return 0


def set_4_ver(ix, tokens, metas, ver):
    if tokens.get(ver, False):
        if ver == 0:
            if not tokens.get(60, False):
                tokens[60] = tokens[0]
            if IS_BADGE_TXT[ix][0] != '^':
                SRC_TOKENS[ix] = regex2txt(IS_BADGE_TXT[ix])
            else:
                SRC_TOKENS[ix] = regex2txt(IS_BADGE_TXT[ix][1:])
        else:
            SRC_TOKENS[ix] = regex2txt(tokens[ver])
        IS_BADGE_TXT[ix + 1] = IS_BADGE_TXT[ix]
        if metas[ver]:
            META[ix] = metas[ver]
        META[ix + 1] = META[ix]
        tok = txt2regex(tokens[ver])
        i = IS_BADGE_TXT[ix].find('[:tok:]')
        if i < 0:
            REPL_CTRS[ix] = 99
        else:
            REPL_CTRS[ix] = 1
        IS_BADGE_TXT[ix] = IS_BADGE_TXT[ix].replace('[:tok:]', tok)
        if IS_BADGE_TXT[ix][0] != '^':
            IS_BADGE_TXT[ix] = '.*' + IS_BADGE_TXT[ix]
        IS_BADGE[ix] = re.compile(IS_BADGE_TXT[ix])
    elif ver > 60:
        tokens[ver] = tokens[prior_ver(ver)]
    if '0' in tokens:
        del tokens[0]
    return tokens


def compile_1_rule(ix, rid, tokens, metas):
    rid += 1
    if not ctx['from_ver']:
        for ver in (0, 60, 61, 70, 80, 90, 100):
            if tokens.get(ver, False):
                tokens = set_4_ver(ix, tokens, metas, ver)
                tokens2 = {}
                for ver2 in (60, 61, 70, 80, 90, 100):
                    if tokens.get(ver2, False):
                        tokens2[ver2] = tokens[ver2]
                    else:
                        if ver2 > 60:
                            tokens2[ver2] = tokens2[prior_ver(ver2)]
                        else:
                            tokens2[ver2] = tokens[ver2]
                TGT_TOKENS[ix] = tokens2
                RID[ix] = rid
                if ver == 0:
                    break
                if ix < 0 or (ix in TGT_TOKENS and len(TGT_TOKENS[ix])):
                    ix += 1
    else:
        for ver in (0, 60, 61, 70, 80, 90, 100):
            if not ver or ctx['from_ver'] == ver:
                tokens = set_4_ver(ix, tokens, metas, ver)
        TGT_TOKENS[ix] = tokens
        RID[ix] = rid
    return ix, rid


def extr_tokens(ix, ctx):
    tokens = TGT_TOKENS[ix]
    return SRC_TOKENS[ix], tokens[ctx['to_ver']]


def compile_rules(ctx):
    ix = -1
    rid = 0
    tokens = {}
    metas = {}
    cont_break = False
    value = ''
    for rule in RULES.split('\n'):
        if not rule:
            continue
        if cont_break:
            value += rule
        else:
            id = rule[0:6].strip()
            meta = rule[6:12].strip()
            value = rule[12:]
        if value and value[-1] == '\\':
            value = value[0:-1]
            cont_break = True
            continue
        cont_break = False
        if id[0] == '#':
            continue
        elif id == '*IS*':
            if ix >= 0:
                ix, rid = compile_1_rule(ix, rid, tokens, metas)
            if ix < 0 or (ix in TGT_TOKENS and len(TGT_TOKENS[ix])):
                ix += 1
            tokens = {}
            metas = {}
            IS_BADGE_TXT[ix] = value
            META[ix] = meta
        elif id == 'v0':
            tokens[0] = value
            metas[0] = meta
        elif id in ('v60', 'v61', 'v70', 'v80', 'v90', 'v100'):
            i = int(eval(id[1:]))
            tokens[i] = value
            metas[i] = meta
        else:
            print "Invalid rule %d -> %s " % (ix, rule)
    compile_1_rule(ix, rid, tokens, metas)
    if ix > 0:
        if ix not in TGT_TOKENS or ix not in SRC_TOKENS or ix not in RID:
            ix -= 1
        elif not TGT_TOKENS[ix] or not SRC_TOKENS[ix]:
            ix -= 1
    if ctx['opt_verbose'] > 1:
        for ii in IS_BADGE_TXT.keys():
            print "%d.%d [%s] if re.match('%s'): replace('%s'|%s)" % (
                ii, RID.get(ii, 0),
                META[ii],
                IS_BADGE_TXT[ii],
                SRC_TOKENS.get(ii, ''),
                TGT_TOKENS.get(ii, ''))


def write_license_info(lines, ctx):
    auth_antoniov = 'Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>'
    found_author = False
    found_oia = False
    if lines[0] != '# -*- coding: utf-8 -*-':
        lines.insert(0, '# -*- coding: utf-8 -*-')
    lineno = 1
    while lines[lineno] and not re.match('^# *([Cc]opyright|\(C\)|©)',
                                         lines[lineno]):
        if lines[lineno][0] == '#':
            del lines[lineno]
        else:
            break
    lines.insert(lineno, '#')
    lineno += 1
    while re.match(
            '^# *([Cc]opyright|\([Cc]\)|©|http:|https:|\w+\@[a-zA-z0-9-.]+)',
            lines[lineno]):
        found_author = True
        if lines[lineno].find(auth_antoniov) >= 0:
            found_oia = True
        if lines[lineno].find('Copyright') < 0:
            lines[lineno] = lines[lineno].replace(
                '(C)', 'Copyright').replace('©', 'Copyright')
        else:
            lines[lineno] = lines[lineno].replace(
                '(C)', '').replace('©', '')
        lines[lineno] = lines[lineno].replace(
            'Copyright  ', 'Copyright ').replace(
                '(<', '<').replace(
                '>)  ', '>')
        while lines[lineno][0:3] == '#  ':
            lines[lineno] = lines[lineno].replace('#  ', '# ')
        if re.match('^# Copyright [0-9]+', lines[lineno]):
            x = re.search('[-0-9]+', lines[lineno])
            if x:
                i = x.end()
                if lines[lineno][i] != ',':
                    lines[
                        lineno] = lines[lineno][0:i] + ',' + lines[lineno][i:]
        lineno += 1
    while lineno < len(lines) and (not lines[lineno] or
                                   lines[lineno] == '#' or
                                   re.match('^# License AGPL', lines[lineno])):
        del lines[lineno]
    if not found_author or (ctx['opt_oia'] and not found_oia):
            lines.insert(
                lineno,
                '# Copyright 2017-2018, %s' % auth_antoniov)
            lineno += 1
            lines.insert(
                lineno,
                '# Copyright 2017-2018, '
                'Associazione Odoo Italia <https://odoo-italia.org>')
            lineno += 1
    lines.insert(lineno, '#')
    lineno += 1
    lines.insert(
        lineno,
        '# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).')
    lineno += 1
    lines.insert(lineno, '#')
    while lineno < len(lines) and (lines[lineno] and
                                   lines[lineno][0] == '#' and
                                   not re.match(
                                       '^# .*This program is free software',
                                       lines[lineno])):
        lineno += 1
    if lineno < len(lines) and (lines[lineno] and
                                re.match(
                                    '^# .*This program is free software',
                                    lines[lineno])):
        while lines[lineno] and not re.match(
                '^# .*http://www.gnu.org/licenses', lines[lineno]):
            del lines[lineno]
        if lines[lineno] and re.match(
                '^# .*http://www.gnu.org/licenses', lines[lineno]):
            del lines[lineno]
        while lines[lineno] == "#" or lines[lineno][0:4] == '####':
            del lines[lineno]
    return lines


def update_4_api(lines, lineno, ctx, ignore=None, select=None):
    line = lines[lineno]
    rid = -1
    if ctx['opt_verbose'] > 2:
        print "%s" % line
    meta = ''
    for ix in IS_BADGE.keys():
        if META[ix] in ('+B', '+b') and ctx['opt_recall_dbg']:
            continue
        elif META[ix] in ('-B', '-b') and not ctx['opt_recall_dbg']:
            continue
        elif META[ix] in ('-u', '-u0', '-u1', '-u2', '-u3') and \
                not ctx['opt_ut7']:
            continue
        elif META[ix] != '#' and ctx['open_doc']:
            continue
        elif META[ix] == '#' and not ctx['open_doc'] and \
                line and line[0] != '#':
            continue
        elif META[ix] == ignore:
            continue
        elif RID[ix] == rid:
            continue
        elif select and META[ix] != select:
            continue
        x = IS_BADGE[ix].match(line)
        if x:
            rid = RID[ix]
            if ctx['opt_verbose'] > 2:
                print "> if IS_BADGE[%d]=(%s).match(%s):" % (
                    ix, IS_BADGE_TXT[ix], line)
                print ">     src, tgt = extr_tokens(%d, ver['%d'])" % (
                    ix, ctx['to_ver'])
            src, tgt = extr_tokens(ix, ctx)
            if tgt != '&' and src != tgt:
                i = 0
                if REPL_CTRS[ix] == 1:
                    i = x.end() - len(src) - 1
                    if i < 0:
                        i = 0
                line = line[0:i] + \
                    line[i:].replace(src, tgt, REPL_CTRS[ix])
                if ctx['opt_verbose'] > 2:
                    print ">     '%s'=replace(%s,%s)" % (line, src, tgt)
            meta = META[ix]
            if META[ix] in ('+B', '-B'):
                # pdb.set_trace()
                tabstop, line_ctrs = parse_tokens_line(line)
                lm = ' ' * line_ctrs['lm']
                if META[ix] == '+B':
                    tabstop, line_ctrs = parse_tokens_line(
                        line[line_ctrs['lm'] + 1:])
                if line_ctrs['any_paren'] > 0 or line_ctrs['cont_line']:
                    if META[ix] == '+B':
                        lm1 = lm + '# '
                    else:
                        lm1 = lm
                        lm = lm + '# '
                    while line_ctrs['any_paren'] > 0 or line_ctrs['cont_line']:
                        lines[lineno] = line.rstrip()
                        lineno += 1
                        line = lines[lineno].replace(lm, lm1, 1)
                        tabstop, line_ctrs = parse_tokens_line(line,
                                                               ctrs=line_ctrs)
                        if META[ix] == '+B':
                            tabstop, line_ctrs = parse_tokens_line(
                                line[line_ctrs['lm'] + 1:],
                                ctrs=line_ctrs)
            elif META[ix] == 'trvs':
                tok = '# pragma: no cover'
                if lines[lineno].find(tok) < 0:
                    spc = ' ' * 79
                    i = 79 - len(tok)
                    line = (line + spc)[0:i] + tok
            if META[ix] and META[ix] != '#':
                break
    lines[lineno] = line.rstrip()
    return lines, meta, rid


def move_tk_line_up(lines, lineno, tk):
    if lineno > 0:
        i = lines[lineno].find(tk)
        l = len(tk)
        newln = lines[lineno][0:i] + lines[lineno][i+l+1:]
        if newln.strip() == "":
            lines[lineno] = ""
        else:
            lines[lineno] = newln
        lineno -= 1
        if lines[lineno][-2:] == ' \\':
            lines[lineno] = lines[lineno][0:-1] + tk + " \\"
        elif lines[lineno][-1] == '\\':
            lines[lineno] = lines[lineno][0:-1] + " " + tk + " \\"
        else:
            lines[lineno] = lines[lineno] + " " + tk


def split_eol(line, ipos, istkn):
    imin = len(line) / 5 + 1
    ibrk = imin * 4
    if ibrk > 79:
        ibrk = 79
    if imin > ipos and imin < ibrk:
        while ibrk > imin and line[ibrk] != ' ':
            ibrk -= 1
        if ibrk > imin:
            ln1 = line[0:ibrk]
            if istkn == 'begremark':
                lm = ' ' * ipos
                ln2 = lm + '#' + line[ibrk:]
            elif istkn in ('begdoc1',
                           'begdoc2'):
                lm = ''
                i = 0
                while line[i] == ' ':
                    lm += ' '
                    i += 1
                ln2 = lm + line[ibrk:].strip()
            return ln1, ln2
    return line, ''


def parse_tokens_line(line, ctrs=None):
    # pdb.set_trace()
    tabstop = {}
    if ctrs is None:
        line_ctrs = {}
        line_ctrs['paren'] = 0
        line_ctrs['brace'] = 0
        line_ctrs['bracket'] = 0
    else:
        line_ctrs = ctrs
    line_ctrs['lm'] = 0
    ipos = 0
    while ipos < len(line):
        unknown = True
        for istkn in SYNTAX:
            x = SYNTAX[istkn].match(line[ipos:])
            if x:
                unknown = False
                if istkn != 'space' and line_ctrs['lm'] == 0:
                    line_ctrs['lm'] = ipos
                tabstop[ipos] = istkn
                if istkn in ('begremark',
                             'begdoc1',
                             'begdoc2'):
                    ipos = len(line)
                elif istkn == 'begtxt1':
                    while x:
                        x = re.match('("[^"]*")', line[ipos:])
                        if x:
                            ipos += x.end()
                            if line[ipos:ipos + 1] == r'\"':
                                ipos += 1
                            else:
                                x = None
                        else:
                            ipos = len(line)
                elif istkn == 'begtxt2':
                    while x:
                        x = re.match("('[^']*')", line[ipos:])
                        if x:
                            ipos += x.end()
                            if line[ipos:ipos + 1] == r"\'":
                                ipos += 1
                            else:
                                x = None
                        else:
                            ipos = len(line)
                elif istkn == 'lparen':
                    line_ctrs['paren'] += 1
                    ipos += x.end()
                elif istkn == 'rparen':
                    line_ctrs['paren'] -= 1
                    ipos += x.end()
                elif istkn == 'lbrace':
                    line_ctrs['brace'] += 1
                    ipos += x.end()
                elif istkn == 'rbrace':
                    line_ctrs['brace'] -= 1
                    ipos += x.end()
                elif istkn == 'lbracket':
                    line_ctrs['bracket'] += 1
                    ipos += x.end()
                elif istkn == 'rbracket':
                    line_ctrs['bracket'] -= 1
                    ipos += x.end()
                elif x:
                    ipos += x.end()
                break
        if unknown:
            print "Unknown token %s" % line[ipos:]
            ipos += 1
    tabstop[len(line)] = 'eol'
    # i = len(line) - 1
    if line[-1] == '\\':
        line_ctrs['cont_line'] = True
    else:
        line_ctrs['cont_line'] = False
    line_ctrs['any_paren'] = line_ctrs['paren'] + \
        line_ctrs['brace'] + line_ctrs['bracket']
    return tabstop, line_ctrs


def split_line(line):
    # pdb.set_trace()
    tabstop, line_ctrs = parse_tokens_line(line)
    ln1 = line
    ln2 = ''
    imin = -1
    ibrk1 = -1
    ibrk2 = -1
    idnt = 0
    for ipos in sorted(tabstop):
        if ipos >= 79:
            break
        istkn = tabstop[ipos]
        if istkn in ('space'):
            continue
        elif istkn in ('begremark',
                       'begdoc1',
                       'begdoc2'):
            ln1, ln2 = split_eol(line, ipos, istkn)
            if ln2:
                return ln1, ln2
        # elif istkn == 'begtxt1':
        #     pass
        # elif istkn == 'begtxt2':
        #     pass
        elif imin < 0 and tabstop[ipos] in ('isalnum', 'begtxt1', 'begtxt2'):
            imin = ipos
        elif tabstop[ipos] in ('lparen',
                               'lbrace',
                               'lbracket',
                               'colon'):
            idnt = 4
            ibrk1 = ipos + 1
        elif tabstop[ipos] in ('comma', ):
            idnt = 0
            ibrk2 = ipos + 1
    if imin >= 0:
        imin += idnt
    if ibrk1 >= 0:
        ibrk = ibrk1
    else:
        ibrk = ibrk2
    if imin >= 0 and ibrk >= 0:
        ln1 = line[0:ibrk]
        lm = ' ' * imin
        ln2 = lm + line[ibrk:].strip()
    return ln1, ln2


def init_parse(ctx):
    if ctx['opt_verbose']:
        print "Compiling rules"
    compile_rules(ctx)
    ctx['empty_line'] = 0
    ctx['open_stmt'] = 0
    ctx['open_doc'] = 0
    return ctx


def set_empty_lines(lines, lineno, nebef, force, ctx):
    if ctx['empty_line'] > nebef:
        del lines[lineno - 1]
        ctx['empty_line'] -= 1
        lineno -= 1
    elif ctx['empty_line'] or force:
        while ctx['empty_line'] < nebef:
            lines.insert(lineno, '')
            ctx['empty_line'] += 1
            lineno += 1
    return lines, lineno, ctx


def parse_file(src_filepy, dst_filepy, ctx):
    # pdb.set_trace()
    if ctx['opt_verbose']:
        print "Reading %s" % src_filepy
    fd = open(src_filepy, 'rb')
    tokenize.generate_tokens(
        fd.readline,
        )
    fd.close()
    fd = open(src_filepy, 'rb')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    ctx = init_parse(ctx)
    if ctx['opt_gpl']:
        lines = write_license_info(lines, ctx)
    LAST_RID = -1
    lineno = 0
    del_empty_line = True
    ignore = None
    while lineno < len(lines):
        if ctx['open_doc'] != 2 and re.match('.*"""', lines[lineno]):
            if len(lines[lineno]) > 79:
                ln1, ln2 = split_line(lines[lineno])
                if ln2:
                    lines[lineno] = ln2
                    lines.insert(lineno, ln1)
            if ctx['open_doc'] == 1:
                ctx['open_doc'] = 0
            elif re.match('.*""".*"""', lines[lineno]):
                pass
            else:
                ctx['open_doc'] = 1
            lines, meta, rid = update_4_api(lines,
                                            lineno,
                                            ctx)
            del_empty_line = False
        elif ctx['open_doc'] != 1 and re.match('\s*"""', lines[lineno]):
            if len(lines[lineno]) > 79:
                ln1, ln2 = split_line(lines[lineno])
                if ln2:
                    lines[lineno] = ln2
                    lines.insert(lineno, ln1)
            if ctx['open_doc'] == 2:
                ctx['open_doc'] = 0
            elif re.match(".*'''.*'''", lines[lineno]):
                pass
            else:
                ctx['open_doc'] = 2
            lines, meta, rid = update_4_api(lines,
                                            lineno,
                                            ctx)
            del_empty_line = False
        elif ctx['open_doc']:
            lines, meta, rid = update_4_api(lines,
                                            lineno,
                                            ctx)
            del_empty_line = False
        elif lines[lineno] == "":
            if del_empty_line:
                del lines[lineno]
                lineno -= 1
            else:
                ctx['empty_line'] += 1
        else:
            if lines[lineno][0] != '#':
                del_empty_line = False
            lines, meta, rid = update_4_api(lines,
                                            lineno,
                                            ctx,
                                            ignore=ignore)
            ignore = None
            if meta:
                if meta in ('+B', '-B', '+b', '-b', '#'):
                    pass
                elif meta[0] == '+':
                    nebef = eval(meta[1])
                    lines, lineno, ctx = set_empty_lines(lines,
                                                         lineno,
                                                         nebef,
                                                         True,
                                                         ctx)
                elif meta[0] == '*':
                    nebef = eval(meta[1])
                    lines, lineno, ctx = set_empty_lines(lines,
                                                         lineno,
                                                         nebef,
                                                         rid != LAST_RID,
                                                         ctx)
                elif meta == '&&':
                    ignore = meta
                    tk = "and"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == '||':
                    ignore = meta
                    tk = "or"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == '^+':
                    ignore = meta
                    tk = "+"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == '^-':
                    ignore = meta
                    tk = "-"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == 'del1':
                    del lines[lineno + 1]
                elif meta == '-u':
                    ignore = meta
                    nebef = 2
                    lines, lineno, ctx = set_empty_lines(lines,
                                                         lineno,
                                                         nebef,
                                                         True,
                                                         ctx)
                    lineno += 1
                    lines.insert(lineno, '    def env7(self, model):')
                    lineno += 1
                    lines.insert(lineno, '        return self.registry(model)')
                elif meta in ('-u0', '-u1', '-u2', '-u3'):
                    ignore = meta
                    line = lines[lineno]
                    tabstop, line_ctrs = parse_tokens_line(line)
                    if line_ctrs['any_paren'] >= 0:
                        # lm = ' ' * line_ctrs['lm']
                        while line_ctrs['any_paren'] > 0 or \
                                line_ctrs['cont_line']:
                            if line_ctrs['cont_line']:
                                line = line[0:-1]
                            del lines[lineno]
                            tabstop, line_ctrs = parse_tokens_line(
                                lines[lineno], ctrs=line_ctrs)
                            line = line + ' ' + lines[lineno].strip()
                        del lines[lineno]
                        tabstop, line_ctrs = parse_tokens_line(line)
                        # print "<%s>" % (line) #debug
                        ipos = -1
                        states = {}
                        tabstop_rule = {}
                        tabstop_beg = {}
                        tabstop_end = {}
                        paren_ctrs = {}
                        line_ctrs['paren'] = 0
                        line_ctrs['brace'] = 0
                        line_ctrs['bracket'] = 0
                        paren_ctrs['paren'] = -1
                        paren_ctrs['brace'] = -1
                        paren_ctrs['bracket'] = -1
                        for inxt in sorted(tabstop):
                            if tabstop[inxt] == 'space':
                                continue
                            elif ipos < 0:
                                ipos = inxt
                                continue
                            istkn = tabstop[ipos]
                            tok = line[ipos:inxt].strip()
                            if istkn == 'rparen':
                                line_ctrs['paren'] -= 1
                            elif istkn == 'rbrace':
                                line_ctrs['brace'] -= 1
                            elif istkn == 'rbracket':
                                line_ctrs['bracket'] -= 1
                            for ir in SPEC_SYNTAX.keys():
                                irule = SPEC_SYNTAX[ir]
                                if ir not in states:
                                    states[ir] = 0
                                    tabstop_rule[ir] = ipos
                                if states[ir] < 0:
                                    pass
                                elif isinstance(irule[states[ir]], bool):
                                    if irule[states[ir]]:
                                        if states[ir] == 0:
                                            tabstop_rule[ir] = ipos
                                        states[ir] += 1
                                    else:
                                        states[ir] = 0
                                elif tok == irule[states[ir]]:
                                    if states[ir] == 0:
                                        tabstop_rule[ir] = ipos
                                    states[ir] += 1
                                else:
                                    tabstop_rule[ir] = ipos
                                    if ir[0:3] == 'equ':
                                        states[ir] = -1
                                    else:
                                        states[ir] = 0
                                if states[ir] >= len(irule):
                                    if istkn == 'rparen' and \
                                            paren_ctrs['paren'] < \
                                            line_ctrs['paren']:
                                        states[ir] = 0
                                    elif istkn == 'rbrace' and \
                                            paren_ctrs['brace'] < \
                                            line_ctrs['brace']:
                                        states[ir] = 0
                                    elif istkn == 'rbracket' and \
                                            paren_ctrs['bracket'] < \
                                            line_ctrs['bracket']:
                                        states[ir] = 0
                                    elif ir == 'clo1':
                                        ir1 = paren_ctrs['-paren']
                                        if ir == 'icr1' or ir1 == 'env2':
                                            states[ir] = 0
                                if states[ir] >= len(irule):
                                    if ir[0:3] == 'clo':
                                        if ir == 'clo1' or ir == 'clo4':
                                            ir1 = paren_ctrs['-paren']
                                        elif ir == 'clo2':
                                            ir1 = paren_ctrs['-brace']
                                        elif ir == 'clo3':
                                            ir1 = paren_ctrs['-bracket']
                                        ir1 = '-' + ir1
                                        tabstop_beg[ir1] = tabstop_rule[ir]
                                        tabstop_end[ir1] = inxt
                                        if ir1 == '-icr1' or ir1 == '-env2':
                                            tabstop_beg[ir1] += 1
                                    elif ir[0:3] == 'equ':
                                        tabstop_beg[ir] = tabstop_rule[ir]
                                        tabstop_end[ir] = ipos
                                    elif ir[0:3] == 'icr':
                                        tabstop_beg[ir] = ipos + 1
                                        tabstop_end[ir] = inxt
                                    else:
                                        tabstop_beg[ir] = tabstop_rule[ir]
                                        tabstop_end[ir] = inxt
                                    if ir[0:3] == 'equ':
                                        states[ir] = -1
                                    else:
                                        states[ir] = 0
                                    if istkn == 'lparen':
                                        paren_ctrs['paren'] = \
                                            line_ctrs['paren']
                                        paren_ctrs['-paren'] = ir
                                    elif istkn == 'lbrace':
                                        paren_ctrs['brace'] = \
                                            line_ctrs['brace']
                                        paren_ctrs['-brace'] = ir
                                    elif istkn == 'lbracket':
                                        paren_ctrs['bracket'] = \
                                            line_ctrs['bracket']
                                        paren_ctrs['-bracket'] = ir
                            if istkn == 'lparen':
                                line_ctrs['paren'] += 1
                            elif istkn == 'lbrace':
                                line_ctrs['brace'] += 1
                            elif istkn == 'lbracket':
                                line_ctrs['bracket'] += 1
                            ipos = inxt
                        tabstop_rule = {}
                        line1 = ''
                        found_srch = False
                        for ir in tabstop_beg:
                            ipos = tabstop_beg[ir]
                            tabstop_rule[ipos] = ir
                        for ipos in sorted(tabstop_rule, reverse=True):
                            ir = tabstop_rule[ipos]
                            if ir == '-icr1':
                                found_srch = True
                                line1 = line[ipos:]
                                line = line[0:ipos] + line[tabstop_end[ir]:]
                            elif ir == '-env2':
                                line = line[0:ipos] + line[tabstop_end[ir]:]
                            elif ir[0:4] == '-env':
                                line = line[0:ipos] + ')' + line[ipos + 1:]
                            elif ir[0:3] == 'icr':
                                line = line[0:ipos] + 'self.cr, self.uid, ' + \
                                    line[ipos:]
                            elif ir == 'env1':
                                tok = line[tabstop_beg[ir]:tabstop_end[ir]]
                                tok = tok.replace('env[', 'env7(')
                                line = line[0:ipos] + tok + \
                                    line[tabstop_end[ir]:]
                            elif ir[0:3] == 'env':
                                tok = line[tabstop_beg[ir]:tabstop_end[ir]]
                                tok = tok.replace('self.env.ref(',
                                                  'self.ref(')
                                line = line[0:ipos] + tok + \
                                    line[tabstop_end[ir]:]
                            elif ir[0:3] == 'equ' and found_srch:
                                line1 = line[0:tabstop_beg['icr1'] - 7] + \
                                    'browse(ids[0])' + line1
                                line = line[0:ipos] + 'ids ' + \
                                    line[tabstop_end[ir]:]
                        lines.insert(lineno, line)
                        if line1:
                            lines.insert(lineno + 1, line1)
                        ignore = None
                ctx['empty_line'] = 0
        if len(lines[lineno]) > 79:
            ln1, ln2 = split_line(lines[lineno])
            if ln2:
                lines[lineno] = ln2
                lines.insert(lineno, ln1)
        if not ignore or not lines[lineno]:
            lineno += 1
        LAST_RID = rid
    lineno = len(lines) - 1
    while lineno > 2 and lines[lineno] == "":
        del lines[lineno]
        lineno = len(lines) - 1
    lineno = 0
    if not ctx['dry_run'] and len(lines):
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        fd = open(dst_filepy, 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close()
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2015-2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-A', '--odoo-italia-associazione',
                        action='store_true',
                        dest='opt_oia',
                        default=False)
    parser.add_argument('-B', '--recall-debug-statements',
                        action='store_true',
                        dest='opt_recall_dbg',
                        default=False)
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-G', '--gpl-info',
                        action='store_true',
                        dest='opt_gpl',
                        default=False)
    parser.add_argument('-n')
    parser.add_argument('-o', '--original-branch',
                        action='store',
                        dest='from_odoo_ver')
    parser.add_argument('-q')
    parser.add_argument('-u', '--unit-test',
                        action='store_true',
                        dest='opt_ut7',
                        default=False)
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_filepy')
    parser.add_argument('dst_filepy',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    src_filepy = ctx['src_filepy']
    if ctx['dst_filepy']:
        dst_filepy = ctx['dst_filepy']
    else:
        dst_filepy = src_filepy
    if ctx['odoo_ver']:
        ctx['to_ver'] = ver2ix(ctx['odoo_ver'])
    else:
        ctx['to_ver'] = 70
    if ctx['from_odoo_ver']:
        ctx['from_ver'] = ver2ix(ctx['from_odoo_ver'])
    else:
        ctx['from_ver'] = 0
    sts = parse_file(src_filepy, dst_filepy, ctx)
    # sys.exit(sts)
