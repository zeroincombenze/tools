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

import pdb
import os
import sys
import re
from z0lib import parseoptargs


__version__ = "0.1.14.5"


ISALNUM = re.compile('[A-Za-z_]+')
ISDOCSEP1 = re.compile('"""')
ISDOCSEP2 = re.compile("'''")

RULES = """
IS  ^ *class.*[:tok:]
V6  osv.osv_memory
V7  orm.TransientModel
V10 models.TransientModel
IS  ^ *class.*[:tok:]
V6  osv.osv
V7  orm.Model
V10 models.Model
IS  ^[:tok:]
V6  from osv import
V7  from openerp.osv import
V10 from odoo import
IS  ^from (openerp.osv|odoo) import
V6  orm
V8  models
IS  ^[:tok:]
V6  from tools.translate import
V7  from openerp.tools.translate import
V10 from odoo.tools.translate import
IS  ^[:tok:]
V6  import decimal_precision
V7  import openerp.addons.decimal_precision
V10 import odoo.addons.decimal_precision
IS  ^import (api|exceptions|fields|http|loglevels|models|netsvc|pooler|release|sql_db)
V6  import
V7  from openerp import
V10 from odoo import
IS  ^from (openerp|odoo)\.addons\.web import http
V6  from openerp.addons.web import http
V10 from odoo import http
IS  ^.*import (openerp|odoo)\.addons\.web\.http
V6  openerp.addons.web.http
V10 odoo.http
IS  ^[:tok:]
V6  from openerp import
V10 from odoo import
IS  ^ *class\.*orm\.
V6  orm
V10 models
IS  [:tok:]
V6  osv.except_osv
V10 UserError
IS  [:tok:]
V6  openerp.tools.config
V10 odoo.tools.config
IS  [:tok:]
V6  openerp.com
V7  odoo.com
IS  [:tok:]
V6  OpenERP
V7  Odoo
IS  formerly (OpenERP|Odoo)
V6  formerly OpenERP
"""
IS_META = {}
IS_META_TXT = {}
SRC_TOKENS = {}
TGT_TOKENS = {}

def set_4_ver(ix, tokens, ver):
    if tokens.get(ver, False):
        IS_META_TXT[ix + 1] = IS_META_TXT[ix]
        tok = tokens[ver].replace('.', '\.')
        IS_META_TXT[ix] = IS_META_TXT[ix].replace('[:tok:]', tok)
        IS_META[ix] = re.compile(IS_META_TXT[ix])
        SRC_TOKENS[ix] = tokens[ver]
    elif ver > 6:
        tokens[ver] = tokens[ver - 1]
    return tokens


def compile_1_rule(ix, tokens):
    if not ctx['from_ver']:
        for ver in (6, 7, 8, 9, 10):
            if tokens.get(ver, False):
                tokens = set_4_ver(ix, tokens, ver)
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
                # print "%d if(%s) %s | %s" % (ix, IS_META_TXT[ix], SRC_TOKENS[ix], TGT_TOKENS[ix])  # debug
                ix += 1
    else:
        for ver in (6, 7, 8, 9, 10):
            if ctx['from_ver'] == ver:
                tokens = set_4_ver(ix, tokens, ver)
        TGT_TOKENS[ix] = tokens
    return ix

def extr_tokens(ix, ctx):
    tokens = TGT_TOKENS[ix]
    return SRC_TOKENS[ix], tokens[ctx['to_ver']]


def compile_rules(ctx):
    ix = -1
    tokens = {}
    for rule in RULES.split('\n'):
        id = rule[0:4]
        value = rule[4:]
        if id == 'IS  ':
            if ix >= 0:
                ix = compile_1_rule(ix, tokens)
            ix += 1
            tokens = {}
            IS_META_TXT[ix] = value
        elif id == 'V6  ':
            tokens[6] = value
        elif id == 'V7  ':
            tokens[7] = value
        elif id == 'V8  ':
            tokens[8] = value
        elif id == 'V9  ':
            tokens[9] = value
        elif id == 'V10 ':
            tokens[10] = value
    compile_1_rule(ix, tokens)


def update_new_api(line):
    for ix in IS_META.keys():
        if IS_META[ix].match(line):
            src, tgt = extr_tokens(ix, ctx)
            line = line.replace(src, tgt)
    line = line.rstrip()
    return line


def recall_debug(line):
    open_stmt = 0
    if re.match("^ +# tndb\.", line):
        line = line.replace("# tndb.",
                            "tndb.", 1)
        if line[-1] != ')':
            while line[open_stmt] == ' ':
                open_stmt += 1
            open_stmt += 1
    if re.match("^ +# pdb\.", line):
        line = line.replace("# pdb.",
                            "pdb.", 1)
    if re.match("^# import pdb", line):
        line = line.replace("# import",
                            "import", 1)
    if re.match("^# from tndb", line):
        line = line.replace("# from tndb",
                            "from tndb", 1)
    return line, open_stmt


def recall_close_line(line, open_stmt):
    if open_stmt:
        lm = ' ' * (open_stmt - 1)
        lm1 = lm + '# '
        line = line.replace(lm1, lm, 1)
        if line[-1] == ')':
            open_stmt = 0
    return line, open_stmt


def hide_debug(line):
    open_stmt = 0
    if re.match("^ +tndb\.", line):
        line = line.replace("tndb.",
                            "# tndb.", 1)
        if line[-1] != ')':
            while line[open_stmt] == ' ':
                open_stmt += 1
            open_stmt += 1
    if re.match("^ +pdb\.", line):
        line = line.replace("pdb.",
                            "# pdb.", 1)
    if re.match("^import pdb", line):
        line = line.replace("import",
                            "# import", 1)
    if re.match("^from tndb", line):
        line = line.replace("from tndb",
                            "# from tndb", 1)
    return line, open_stmt


def hide_close_line(line, open_stmt):
    if open_stmt:
        lm = ' ' * (open_stmt - 1)
        lm1 = lm + '# '
        line = line.replace(lm, lm1, 1)
        if line[-1] == ')':
            open_stmt = 0
    return line, open_stmt


def move_tk_line_up(tk, n, lines):
    if n > 0:
        i = lines[n].find(tk)
        l = len(tk)
        newln = lines[n][0:i] + lines[n][i+l+1:]
        if newln.strip() == "":
            lines[n] = ""
        else:
            lines[n] = newln
        n -= 1
        if lines[n][-2:] == ' \\':
            lines[n] = lines[n][0:-1] + tk + " \\"
        elif lines[n][-1] == '\\':
            lines[n] = lines[n][0:-1] + " " + tk + " \\"
        else:
            lines[n] = lines[n] + " " + tk


def split_line(line):
    ln1 = line
    ln2 = ''
    MINLM = 20
    if line[0] == '#':
        i = len(line) / 4 * 3
        if i > 79:
            i = 79
        while i > MINLM and line[i] != ' ':
            i -= 1
        if i > MINLM:
            ln1 = line[0:i]
            ln2 = '#' + line[i:]
    return ln1, ln2


def exec_W503(src_filepy, dst_filepy, ctx):
    if ctx['opt_verbose']:
        print "Compiling rules"
    compile_rules(ctx)
    if ctx['opt_verbose']:
        print "Reading %s" % src_filepy
    fd = open(src_filepy, 'r')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    empty_line = 0
    open_stmt = 0
    n = 0
    while n < len(lines):
        if lines[n] == "":
            empty_line += 1
        else:
            if re.match("^report_sxw.report_sxw", lines[n]) or \
                    re.match("^if __name__ == .__main__.:", lines[n]):
                if empty_line > 2:
                    del lines[n - 1]
                    empty_line -= 1
                    n -= 1
                else:
                    while empty_line < 2:
                        lines.insert(n, '')
                        empty_line += 1
                        n += 1
            elif re.match("^[a-zA-Z0-9_]+.*\(\)$", lines[n]):
                if empty_line > 2:
                    del lines[n - 1]
                    empty_line -= 1
                    n -= 1
                else:
                    while empty_line < 2:
                        lines.insert(n, '')
                        empty_line += 1
                        n += 1
            empty_line = 0
            if open_stmt:
                if ctx['opt_recall_dbg']:
                    lines[n], open_stmt = recall_close_line(lines[n],
                                                            open_stmt)
                else:
                    lines[n], open_stmt = hide_close_line(lines[n],
                                                          open_stmt)
            else:
                if ctx['opt_recall_dbg']:
                    lines[n], open_stmt = recall_debug(lines[n])
                else:
                    lines[n], open_stmt = hide_debug(lines[n])
                lines[n] = update_new_api(lines[n])
        ln = lines[n].strip()
        if ln == "or":
            tk = "or"
            move_tk_line_up(tk, n, lines)
        elif ln == "and":
            tk = "and"
            move_tk_line_up(tk, n, lines)
        if ln[0:3] == "or ":
            tk = "or"
            move_tk_line_up(tk, n, lines)
        elif ln[0:4] == "and ":
            tk = "and"
            move_tk_line_up(tk, n, lines)
        n += 1
    n = len(lines) - 1
    while n > 2 and lines[n] == "":  # and lines[n - 1] == "":
        del lines[n]
        n = len(lines) - 1
    n = 0
    while n < len(lines):
        if len(lines[n]) > 79:
            ln1, ln2 = split_line(lines[n])
            if ln2:
                lines[n] = ln2
                lines.insert(n, ln1)
        n += 1
    if not ctx['dry_run'] and len(lines):
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        fd = open(dst_filepy, 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close()
    return 0


if __name__ == "__main__":
    # pdb.set_trace()
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
        # if ctx['to_ver'] == 10.0:
        #     ctx['from_ver'] = 9.0
        # elif ctx['to_ver'] == 9.0:
        #     ctx['from_ver'] = 8.0
        # elif ctx['to_ver'] == 8.0:
        #     ctx['from_ver'] = 7.0
        # else:
        #     ctx['from_ver'] = 6.0
    sts = exec_W503(src_filepy, dst_filepy, ctx)
    # sys.exit(sts)
