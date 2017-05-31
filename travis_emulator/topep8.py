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


__version__ = "0.1.14.16"


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
    'op': re.compile('[!%&-+/|^?<=>]+'),
}

RULES = r"""
*IS*        ^ *class.*[:tok:]
 v60        osv.osv_memory
 v61        orm.TransientModel
 v100       models.TransientModel
*IS*        ^ *class.*[:tok:]
 v60        osv.osv
 v61        orm.Model
 v100       models.Model
*IS*        ^[:tok:]
 v60        from osv import
 v70        from openerp.osv import
 v100       from odoo import
*IS*        ^from (openerp.osv|odoo) import
 v60        orm
 v80        models
*IS*        ^[:tok:]
 v60        from tools.translate import
 v70        from openerp.tools.translate import
 v100       from odoo.tools.translate import
*IS*        ^[:tok:]
 v60        import decimal_precision
 v80        import openerp.addons.decimal_precision
 v100       import odoo.addons.decimal_precision
*IS*        ^[:tok:]
 v60        import openerp.addons.decimal_precision
 v80        from openerp.addons.decimal_precision import decimal_precision
 v100       from odoo.addons.decimal_precision import decimal_precision
*IS*        ^import (api|exceptions|fields|http|loglevels|models|netsvc|\
pooler|release|sql_db)
 v60        import
 v70        from openerp import
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
 v100       models
*IS*        [:tok:]
 v60        osv.except_osv
 v100       UserError
*IS*        [:tok:]
 v60        openerp.tools.config
 v100       odoo.tools.config
*IS*   #    openerp.com
 v0         odoo.com
*IS*   #    OpenERP
 v0         Odoo
*IS*   #    openerp-italia.org
 v0         odoo-italia.org
*IS*   #    formerly Odoo
 v0         formerly OpenERP
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
*IS*   ||   ^ +or *
 v0         &
*IS*   &&   ^ +and *
 v0         &
*IS*  del1  if context is None:
 v0         context = {} if context is None else context
*IS*  del1  if ctx is None:
 v0         ctx = {} if ctx is None else ctx
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
        IS_BADGE_TXT[ix] = IS_BADGE_TXT[ix].replace('[:tok:]', tok)
        if IS_BADGE_TXT[ix][0] != '^':
            IS_BADGE_TXT[ix] = '.*' + IS_BADGE_TXT[ix]
        IS_BADGE[ix] = re.compile(IS_BADGE_TXT[ix])
    elif ver > 60:
        tokens[ver] = tokens[prior_ver(ver)]
    if '0' in tokens:
        del tokens[0]
    return tokens


def compile_1_rule(ix, tokens, metas):
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
                if ver == 0:
                    break
                if ix < 0 or (ix in TGT_TOKENS and len(TGT_TOKENS[ix])):
                    ix += 1
    else:
        for ver in (0, 60, 61, 70, 80, 90, 100):
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
                ix = compile_1_rule(ix, tokens, metas)
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


def write_license_info(lines, ctx):
    found_author = False
    if lines[0] != '# -*- coding: utf-8 -*-':
        lines.insert(0, '# -*- coding: utf-8 -*-')
    lineno = 1
    while not re.match('^# *([Cc]opyright|\(C\))', lines[lineno]):
        if lines[lineno][0] == '#':
            del lines[lineno]
        else:
            break
    while re.match(
            '^# *([Cc]opyright|\([Cc]\)|http:|https:|\w+\@[a-zA-z0-9-.]+)',
            lines[lineno]):
        found_author = True
        lineno += 1
    while lines[lineno][0] == '#':
        del lines[lineno]
    if not found_author:
            lines.insert(
                lineno,
                '# Copyright 2017, '
                'Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>')
            lineno += 1
            lines.insert(
                lineno,
                '# Copyright 2017, '
                'Associazione Odoo Italia <https://odoo-italia.org>')
            lineno += 1
    lines.insert(
        lineno,
        '# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).')
    lineno += 1
    lines.insert(lineno, '#')
    return lines


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
        elif META[ix] != '#' and ctx['open_doc']:
            continue
        if IS_BADGE[ix].match(line):
            if ctx['opt_verbose'] > 2:
                print "> if IS_BADGE[%d]=(%s).match(%s):" % (
                    ix, IS_BADGE_TXT[ix], line)
                print ">     src, tgt = extr_tokens(%d, ver['%d'])" % (
                    ix, ctx['to_ver'])
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
            if META[ix] and META[ix] != '#':
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


def split_line(line):
    ln1 = line
    ln2 = ''
    tabstop = {}
    ipos = 0
    while ipos < len(line):
        unknown = True
        for istkn in SYNTAX:
            x = SYNTAX[istkn].match(line[ipos:])
            if x:
                unknown = False
                if istkn != 'space':
                    tabstop[ipos] = istkn
                if istkn in ('begremark',
                             'begdoc1',
                             'begdoc2'):
                    ln1, ln2 = split_eol(line, ipos, istkn)
                    if ln2:
                        return ln1, ln2
                    ipos = len(line)
                elif istkn == 'begtxt1':
                    x = re.match('.*"', line[ipos:])
                    if x:
                        ipos += x.end()
                    else:
                        ipos = len(line)
                elif istkn == 'begtxt2':
                    x = re.match(".*'", line[ipos:])
                    if x:
                        ipos += x.end()
                    else:
                        ipos = len(line)
                elif x:
                    ipos += x.end()
                break
        if unknown:
            print "Unknown token %s" % line[ipos:]
            ipos += 1
    imin = -1
    ibrk = -1
    for i in sorted(tabstop):
        if imin < 0 and tabstop[i] in ('isalnum', 'begtxt1', 'begtxt2'):
            imin = i
        elif i < 79 and tabstop[i] in ('lparen',
                                       'lbrace',
                                       'lbracket',
                                       'colon'):
            if imin >=0:
                imin += 4
            ibrk = i + 1
        elif i < 79 and tabstop[i] in ('comma', ):
            ibrk = i + 1
    if imin >= 0 and ibrk >= 0:
        ln1 = line[0:ibrk]
        lm = ' ' * imin
        ln2 = lm + line[ibrk:]
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
    fd = open(src_filepy, 'r')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    ctx = init_parse(ctx)
    if ctx['opt_gpl']:
        lines = write_license_info(lines, ctx)
    lineno = 0
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
            lines, meta = update_4_api(lines,
                                       lineno,
                                       ctx)
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
            lines, meta = update_4_api(lines,
                                       lineno,
                                       ctx)
        elif ctx['open_doc']:
            lines, meta = update_4_api(lines,
                                       lineno,
                                       ctx)
        elif lines[lineno] == "":
            ctx['empty_line'] += 1
        else:
            lines, meta = update_4_api(lines,
                                       lineno,
                                       ctx)
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
                                                         False,
                                                         ctx)
                elif meta == '&&':
                    tk = "and"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == '||':
                    tk = "or"
                    move_tk_line_up(lines, lineno, tk)
                elif meta == 'del1':
                    del lines[lineno + 1]
                ctx['empty_line'] = 0
        if len(lines[lineno]) > 79:
            # import pdb
            # pdb.set_trace()
            ln1, ln2 = split_line(lines[lineno])
            if ln2:
                lines[lineno] = ln2
                lines.insert(lineno, ln1)
        lineno += 1
    lineno = len(lines) - 1
    while lineno > 2 and lines[lineno] == "":
        del lines[lineno]
        lineno = len(lines) - 1
    lineno = 0
    # while lineno < len(lines):
    #     if len(lines[lineno]) > 79:
    #         ln1, ln2 = split_line(lines[lineno])
    #         if ln2:
    #             lines[lineno] = ln2
    #             lines.insert(lineno, ln1)
    #     lineno += 1
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
    parser.add_argument('-G', '--gpl-info',
                        action='store_true',
                        dest='opt_gpl',
                        default=False)
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
        ctx['to_ver'] = ver2ix(ctx['odoo_ver'])
    else:
        ctx['to_ver'] = 70
    if ctx['from_odoo_ver']:
        ctx['from_ver'] = ver2ix(ctx['from_odoo_ver'])
    else:
        ctx['from_ver'] = 0
    sts = parse_file(src_filepy, dst_filepy, ctx)
    # sys.exit(sts)
