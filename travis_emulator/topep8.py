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
"""recover W503
"""

# import pdb
# import os
import sys
import re
from z0lib import parseoptargs


__version__ = "0.1.14.8"


ISALNUM_B = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*')
ISDOCSEP1 = re.compile('"""')
ISDOCSEP2 = re.compile("'''")
IS_ASSIGN = re.compile('[a-zA-Z_][a-zA-Z0-9_]* *=')
IS_ASSIGN_B = re.compile('^[a-zA-Z_][a-zA-Z0-9_]* *=')
IS_DEF = re.compile('def +')
IS_CLASS = re.compile('class +')

SYNTAX = {
    'open_lparen': re.compile(' *\('),
    'open_rparen': re.compile(' *\)'),
    'open_lbrace': re.compile(' *\['),
    'open_rbrace': re.compile(' *\]'),
    'open_lbracket': re.compile(' *\{'),
    'open_rbracket': re.compile(' *\}'),
    'isalnum': re.compile(' *[a-zA-Z_][\w]*'),
    'isdigit': re.compile(' *[\d]+'),
    'begdoc1': re.compile(' *"""'),
    'begdoc2': re.compile(' *"""'),
}

RULES = r"""
*IS*    ^ *class.*[:tok:]
 v6     osv.osv_memory
 v7     orm.TransientModel
 v10    models.TransientModel
*IS*    ^ *class.*[:tok:]
 v6     osv.osv
 v7     orm.Model
 v10    models.Model
*IS*    ^[:tok:]
 v6     from osv import
 v7     from openerp.osv import
 v10    from odoo import
*IS*    ^from (openerp.osv|odoo) import
 v6     orm
 v8     models
*IS*    ^[:tok:]
 v6     from tools.translate import
 v7     from openerp.tools.translate import
 v10    from odoo.tools.translate import
*IS*    ^[:tok:]
 v6     import decimal_precision
 v7     import openerp.addons.decimal_precision
 v10    import odoo.addons.decimal_precision
*IS*    ^import (api|exceptions|fields|http|loglevels|models|netsvc|pooler|\
release|sql_db)
 v6     import
 v7     from openerp import
 v10    from odoo import
*IS*    ^from (openerp|odoo)\.addons\.web import http
 v6     from openerp.addons.web import http
 v10    from odoo import http
*IS*    ^.*import (openerp|odoo)\.addons\.web\.http
 v6     openerp.addons.web.http
 v10    odoo.http
*IS*    ^[:tok:]
 v6     from openerp import
 v10    from odoo import
*IS*    ^ *class\.*orm\.
 v6     orm
 v10    models
*IS*    [:tok:]
 v6     osv.except_osv
 v10    UserError
*IS*    [:tok:]
 v6     openerp.tools.config
 v10    odoo.tools.config
*IS*    openerp.com
 v0     odoo.com
*IS*    OpenERP
 v0     Odoo
*IS*    formerly Odoo
 v0     formerly OpenERP
*IS* +2 ^[a-zA-Z_][\w.]* *\(
 v0     &
*IS* +2 ^if __name__ == .__main__.:
 v0     &
*IS* +2 ^def +
 v0     &
*IS* +2 ^class +
 v0     &
*IS* *2 ^[a-zA-Z_][\w.]* *=
 v0     &
#
*IS* +B ^ +tndb\.
 v0     # tndb.
*IS* +b ^from tndb
 v0     # from tndb
*IS* +b ^ +pdb\.
 v0     # pdb.
*IS* +b ^import pdb
 v0     # import pdb
*IS* -B # tndb\.
 v0     tndb.
*IS* -b # from tndb
 v0     from tndb
*IS* -b # pdb
 v0     pdb
*IS* -b # import pdb
 v0     import pdb
*IS* || ^ +or *
 v0     &
*IS* && ^ +and *
 v0     &
"""
IS_BADGE = {}
IS_BADGE_TXT = {}
META = {}
SRC_TOKENS = {}
TGT_TOKENS = {}


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
        '\.', '.')
    return tok


def set_4_ver(ix, tokens, metas, ver):
    if tokens.get(ver, False):
        if ver == 0:
            if not tokens.get(6, False):
                tokens[6] = tokens[0]
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
        IS_BADGE_TXT[ix] = IS_BADGE_TXT[ix].replace('[:tok:]', tok)
        if IS_BADGE_TXT[ix][0] != '^':
            IS_BADGE_TXT[ix] = '.*' + IS_BADGE_TXT[ix]
        IS_BADGE[ix] = re.compile(IS_BADGE_TXT[ix])
    elif ver > 6:
        tokens[ver] = tokens[ver - 1]
    if '0' in tokens:
        del tokens[0]
    return tokens


def compile_1_rule(ix, tokens, metas):
    if not ctx['from_ver']:
        for ver in (0, 6, 7, 8, 9, 10):
            if tokens.get(ver, False):
                tokens = set_4_ver(ix, tokens, metas, ver)
                tokens2 = {}
                for ver2 in (6, 7, 8, 9, 10):
                    if tokens.get(ver2, False):
                        tokens2[ver2] = tokens[ver2]
                    else:
                        if ver2 > 6:
                            tokens2[ver2] = tokens2[ver2 - 1]
                        else:
                            tokens2[ver2] = tokens[ver2]
                TGT_TOKENS[ix] = tokens2
                if ver == 0:
                    break
                if ix < 0 or (ix in TGT_TOKENS and len(TGT_TOKENS[ix])):
                    ix += 1
    else:
        for ver in (0, 6, 7, 8, 9, 10):
            if not ver or ctx['from_ver'] == ver:
                tokens = set_4_ver(ix, tokens, metas, ver)
        TGT_TOKENS[ix] = tokens
    return ix


def extr_tokens(ix, ctx):
    tokens = TGT_TOKENS[ix]
    return SRC_TOKENS[ix], tokens[ctx['to_ver']]


def compile_rules(ctx):
    ix = -1
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
            id = rule[0:4]
            meta = rule[4:8].strip()
            value = rule[8:]
        if value and value[-1] == '\\':
            value = value[0:-1]
            cont_break = True
            continue
        cont_break = False
        if id[0] == '#':
            continue
        elif id == '*IS*':
            if ix >= 0:
                ix = compile_1_rule(ix, tokens, metas)
            if ix < 0 or (ix in TGT_TOKENS and len(TGT_TOKENS[ix])):
                ix += 1
            tokens = {}
            metas = {}
            IS_BADGE_TXT[ix] = value
            META[ix] = meta
        elif id == ' v0 ':
            tokens[0] = value
            metas[0] = meta
        elif id == ' v6 ':
            tokens[6] = value
            metas[6] = meta
        elif id == ' v7 ':
            tokens[7] = value
            metas[7] = meta
        elif id == ' v8 ':
            tokens[8] = value
            metas[8] = meta
        elif id == ' v9 ':
            tokens[9] = value
            metas[9] = meta
        elif id == ' v10':
            tokens[10] = value
            metas[10] = meta
        else:
            print "Invalid rule %d -> %s " % (ix, rule)
    compile_1_rule(ix, tokens, metas)
    if ix > 0:
        if ix not in TGT_TOKENS or ix not in SRC_TOKENS:
            ix -= 1
        elif not TGT_TOKENS[ix] or not SRC_TOKENS[ix]:
            ix -= 1
    if ctx['opt_verbose'] > 1:
        for ii in IS_BADGE_TXT.keys():
            print "%d [%s] if re.match('%s'): replace('%s'|%s)" % (
                ii,
                META[ii],
                IS_BADGE_TXT[ii],
                SRC_TOKENS.get(ii, ''),
                TGT_TOKENS.get(ii, ''))


def update_4_api(lines, lineno, ctx):
    line = lines[lineno]
    if ctx['opt_verbose'] > 2:
        print "%s" % line
    meta = ''
    for ix in IS_BADGE.keys():
        if META[ix] in ('+B', '+b') and ctx['opt_recall_dbg']:
            continue
        elif META[ix] in ('-B', '-b') and not ctx['opt_recall_dbg']:
            continue
        if IS_BADGE[ix].match(line):
            if ctx['opt_verbose'] > 2:
                print "> if IS_BADGE[%d]=(%s).match(%s):" % (
                    ix, IS_BADGE_TXT[ix], line)
                print ">     src, tgt = extr_tokens(%d, ctx)" % ix
            src, tgt = extr_tokens(ix, ctx)
            if tgt != '&' and src != tgt:
                line = line.replace(src, tgt)
                if ctx['opt_verbose'] > 2:
                    print ">     '%s'=replace(%s,%s)" % (line, src, tgt)
            meta = META[ix]
            if META[ix] in ('+B', '-B'):
                if line[-1] != ')':
                    lm = ''
                    i = 0
                    while line[i] == ' ':
                        lm += ' '
                        i += 1
                    if META[ix] == '+B':
                        lm1 = lm + '# '
                    else:
                        lm1 = lm
                        lm = lm + '# '
                    while line and line[-1] != ')':
                        lines[lineno] = line.rstrip()
                        lineno += 1
                        line = lines[lineno].replace(lm, lm1, 1)
            if META[ix]:
                break
    lines[lineno] = line.rstrip()
    return lines, meta


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


def split_line(line):
    ln1 = line
    ln2 = ''
    MINLM = 20
    if line[0] == '#':
        ipos = len(line) / 4 * 3
        if ipos > 79:
            ipos = 79
        while ipos > MINLM and line[ipos] != ' ':
            ipos -= 1
        if ipos > MINLM:
            ln1 = line[0:ipos]
            ln2 = '#' + line[ipos:]
    elif SYNTAX['begdoc1'].match(line) or SYNTAX['begdoc2'].match(line):
        ipos = len(line) / 4 * 3
        if ipos > 79:
            ipos = 79
        while ipos > MINLM and line[ipos] != ' ':
            ipos -= 1
        if ipos > MINLM:
            lm = ''
            i = 0
            while line[i] == ' ':
                lm += ' '
                i += 1
            ln1 = line[0:ipos]
            ln2 = lm + line[ipos:].strip()
    return ln1, ln2


def init_parse(ctx):
    if ctx['opt_verbose']:
        print "Compiling rules"
    compile_rules(ctx)
    ctx['empty_line'] = 0
    ctx['open_stmt'] = 0
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
    fd = open(src_filepy, 'r')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    ctx = init_parse(ctx)
    lineno = 0
    while lineno < len(lines):
        if lines[lineno] == "":
            ctx['empty_line'] += 1
        else:
            lines, meta = update_4_api(lines,
                                       lineno,
                                       ctx)
            if meta:
                if meta in ('+B', '-B', '+b', '-b'):
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
                                                         False,
                                                         ctx)
                elif meta == '&&':
                    tk = "and"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == '||':
                    tk = "or"
                    move_tk_line_up(lines, lineno, tk)
                ctx['empty_line'] = 0
        lineno += 1
    lineno = len(lines) - 1
    while lineno > 2 and lines[lineno] == "":
        del lines[lineno]
        lineno = len(lines) - 1
    lineno = 0
    while lineno < len(lines):
        if len(lines[lineno]) > 79:
            ln1, ln2 = split_line(lines[lineno])
            if ln2:
                lines[lineno] = ln2
                lines.insert(lineno, ln1)
        lineno += 1
    if not ctx['dry_run'] and len(lines):
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        fd = open(dst_filepy, 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close()
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2015-2017 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-B', '--recall-debug-statements',
                        action='store_true',
                        dest='opt_recall_dbg',
                        default=False)
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-o', '--original-branch',
                        action='store',
                        dest='from_odoo_ver')
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
        ctx['to_ver'] = eval(ctx['odoo_ver'])
    else:
        ctx['to_ver'] = 7.0
    if ctx['from_odoo_ver']:
        ctx['from_ver'] = eval(ctx['from_odoo_ver'])
    else:
        ctx['from_ver'] = 0.0
    sts = parse_file(src_filepy, dst_filepy, ctx)
    # sys.exit(sts)
