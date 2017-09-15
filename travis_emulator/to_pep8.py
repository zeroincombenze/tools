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

import pdb
# import os
import sys
import re
from z0lib import parseoptargs
import tokenize


__version__ = "0.1.15"


class topep8():

    def __init__(self, src_filepy):
        self.src_filepy = src_filepy
        fd = open(src_filepy, 'rb')
        source = fd.read()
        fd.close()
        self.lines = source.split('\n')
        self.init_parse()
        self.init_rules()
        self.tokenized = []
        for (toktype, tokval,
             (srow, scol),
             (erow, ecol), line) in tokenize.generate_tokens(self.readline):
            self.tokenized.append([toktype, tokval,
                                   (srow, scol),
                                   (erow, ecol)])

    def init_parse(self):
        self.lineno = 0
        self.last_row = -1
        self.tabstop = {}
        self.paren_ctrs = 0
        self.brace_ctrs = 0
        self.bracket_ctrs = 0
        self.any_paren = 0
        self.deep_level = 0
        self.file_header = True
        self.blk_header = True
        self.prev_row = 1
        self.prev_col = 0
        self.tokeno = 0

    def toggle_state(self, state):
        return -1 - state

    def valid_state(self, state):
        return abs(state + 1)

    def init_rules(self):
        self.ghost = [tokenize.INDENT,  tokenize.DEDENT,
                      tokenize.NEWLINE, tokenize.NL]
        self.SYNTAX = ['space',
                       'escape',
                       'lparen',
                       'rparen',
                       'lbrace',
                       'rbrace',
                       'lbracket',
                       'rbracket',
                       'dot',
                       'comma',
                       'colon',
                       'assign',
                       'op',
                       'strdoc1',
                       'strdoc2',
                       'string1',
                       'string2',
                       'remark_eol',
                       'fullname',
                       'int',
                       'name' ]
        self.SYNTAX_RE = {
            'space': re.compile(r'\s+'),
            'escape': re.compile(r'\$'),
            'lparen': re.compile(r'\('),
            'rparen': re.compile(r'\)'),
            'lbrace': re.compile(r'\['),
            'rbrace': re.compile(r'\]'),
            'lbracket': re.compile(r'\{'),
            'rbracket': re.compile(r'\}'),
            'dot': re.compile(r'\.'),
            'comma': re.compile(r','),
            'colon': re.compile(r':'),
            'assign': re.compile(r'='),
            'op': re.compile(r'[-\\!%&+/|^?<>]+'),
            'strdoc1': re.compile(r'"""'),
            'strdoc2': re.compile(r"'''"),
            'string1': re.compile(r'"{1,2}($|[^"])'),
            'endstr1': re.compile(r'("[^"]*")'),
            'string2': re.compile(r"'{1,2}($|[^'])"),
            'endstr2': re.compile(r"('[^']*')"),
            'remark_eol': re.compile(r'#'),
            'fullname': re.compile(r'([a-zA-Z_]\w*|\.)+'),
            'int': re.compile(r'[\d]+'),
            'name': re.compile(r'[a-zA-Z_]\w*'),
        }

    def readline(self):
        if self.lineno < len(self.lines):
            line = self.lines[self.lineno] + '\n'
            self.lineno += 1
        else:
            line = ''
        return line

    def init_rule_state(self, ir):
        if ir not in self.syntax_state:
            self.syntax_state[ir] = 0
        if ir not in self.syntax_more:
            self.syntax_more[ir] = False

    def init_rule_prms(self, ir):
        if ir not in self.SYTX_PRMS:
            self.SYTX_PRMS[ir] = {}

    def init_rule_tokv(self, ir):
        if ir not in self.SYTX_TOKV:
            self.SYTX_TOKV[ir] = []
        for i, t in enumerate(self.SYTX_KEYW[ir]):
            if i >= len(self.SYTX_TOKV[ir]):
                self.SYTX_TOKV[ir].append(tokenize.NOOP)

    def init_rule_all(self, ir):
        self.init_rule_state(ir)
        self.init_rule_prms(ir)
        self.init_rule_tokv(ir)

    def parse_escape_rule(self, value, ipos):
        i = ipos
        x = self.SYNTAX_RE['name'].match(value[i + 1:])
        ipos += x.end() + 1
        tokval = value[i + 1:ipos]
        if tokval in ('name', 'any', 'more', 'expr'):
            toktype = getattr(tokenize, tokval.upper())
            tokval = False
        else:
            print "Unknown token %s" % value[i:]
            tokval = False
            toktype = tokenize.SUBRULE
        return toktype, tokval, ipos

    def parse_txt1_rule(self, value, ipos):
        i = ipos
        x = True
        while x:
            x = self.SYNTAX_RE['endstr1'].match(value[ipos:])
            if x:
                ipos += x.end()
                if value[ipos:ipos + 1] == r'\"':
                    ipos += 1
                else:
                    x = None
            else:
                ipos = len(value)
        tokval = value[i:ipos]
        toktype = tokenize.STRING
        return toktype, tokval, ipos

    def parse_txt2_rule(self, value, ipos):
        i = ipos
        x = True
        while x:
            x = self.SYNTAX_RE['endstr2'].match(value[ipos:])
            if x:
                ipos += x.end()
                if value[ipos:ipos + 1] == r"\'":
                    ipos += 1
                else:
                    x = None
            else:
                ipos = len(value)
        tokval = value[i:ipos]
        toktype = tokenize.STRING
        return toktype, tokval, ipos

    def compile_1_rule(self, ir, meta, value):
        # pdb.set_trace()
        keyw = []
        tokv = []
        ipos = 0
        while ipos < len(value):
            unknown = True
            for istkn in self.SYNTAX:
                x = self.SYNTAX_RE[istkn].match(value[ipos:])
                if x:
                    unknown = False
                    toktype = False
                    i = ipos
                    if istkn in ('space', ):
                        ipos += x.end()
                        continue
                    elif istkn == 'escape':
                        toktype, tokval, ipos = self.parse_escape_rule(value,
                                                                       ipos)
                    elif istkn == 'remark_eol':
                        ipos = len(value)
                        tokval = value[i:ipos]
                        toktype = tokenize.COMMENT
                    elif istkn in ('strdoc1',
                                   'strdoc2'):
                        ipos = len(value)
                        tokval = value[i:ipos]
                        toktype = tokenize.DOC
                    elif istkn == 'string1':
                        toktype, tokval, ipos = self.parse_txt1_rule(value,
                                                                     ipos)
                    elif istkn == 'string2':
                        toktype, tokval, ipos = self.parse_txt2_rule(value,
                                                                     ipos)
                    elif istkn == 'name':
                        ipos += x.end()
                        tokval = value[i:ipos]
                        toktype = tokenize.NAME
                    else:
                        ipos += x.end()
                        tokval = value[i:ipos]
                        toktype = tokenize.OP
                    break
            if unknown:
                print "Unknown token %s" % value[ipos:]
                ipos += 1
            if toktype:
                keyw.append(tokval)
                tokv.append(toktype)
        if self.SYNTAX_RE['int'].match(meta):
            ver = eval(meta)
            if ir in self.SYTX_KEYW:
                self.init_rule_prms(ir)
                self.SYTX_PRMS[ir][ver] = keyw
            else:
                print "Invalid rule %s[%s]" % (ir, meta)
        else:
            self.SYTX_KEYW[ir] = keyw
            self.SYTX_TOKV[ir] = tokv
        self.init_rule_all(ir)

    def extr_tokens_from_line(self, rule, value, cont_break):
        if rule[-1] == '\n':
            rule = rule[0: -1]
        id = False
        meta = False
        if not rule:
            pass
        elif rule[0] == '#':
            pass
        elif cont_break:
            value += rule
        else:
            i = rule.find(':')
            if i < 0:
                value += rule
            else:
                left = rule[0:i].strip()
                value = rule[i + 1:].lstrip()
                i = left.find('[')
                if i < 0:
                    meta = ''
                    id = left
                else:
                    j = left.find(']')
                    if j < 0:
                        j = len(left)
                    meta = rule[i + 1:j].strip()
                    id = left[0:i]
        if value and value[-1] == '\\':
            value = value[0:-1]
            cont_break = True
        else:
            cont_break = False
        return id, meta, value, cont_break

    def read_rules_from_file(self, rule_file, ctx):
        # pdb.set_trace()
        try:
            fd = open(rule_file, 'r')
            value = ''
            cont_break = False
            for rule in fd:
                id, meta, value, cont_break = self.extr_tokens_from_line(
                    rule, value, cont_break)
                if not id:
                    continue
                self.compile_1_rule(id, meta, value)
            fd.close()
        except:
            pass

    def set_rulefn(self, rule_file):
        if rule_file.endswith('.py'):
            rule_file = rule_file[0:-3] + '.2p8'
        else:
            rule_file += '.2p8'
        return rule_file

    def compile_rules(self, ctx):
        self.SYTX_KEYW = {}
        self.SYTX_TOKV = {}
        self.SYTX_PRMS = {}
        self.syntax_state = {}
        self.syntax_more = {}
        self.syntax_replacement = {}
        self.replacements = {}
        tokenize.NOOP = tokenize.N_TOKENS + 16
        tokenize.tok_name[tokenize.NOOP] = 'NOOP'
        tokenize.SUBRULE = tokenize.N_TOKENS + 17
        tokenize.tok_name[tokenize.SUBRULE] = 'SUBRULE'
        tokenize.DOC = tokenize.N_TOKENS + 18
        tokenize.tok_name[tokenize.DOC] = 'DOC'
        tokenize.ANY = tokenize.N_TOKENS + 19
        tokenize.tok_name[tokenize.ANY] = 'ANY'
        tokenize.MORE = tokenize.N_TOKENS + 20
        tokenize.tok_name[tokenize.MORE] = 'MORE'
        tokenize.EXPR = tokenize.N_TOKENS + 21
        tokenize.tok_name[tokenize.EXPR] = 'EXPR'
        #
        self.read_rules_from_file(self.set_rulefn(sys.argv[0]), ctx)
        self.read_rules_from_file(self.set_rulefn(ctx['src_filepy']), ctx)

    def match_parent_rule(self, ir, result):
        for ir1 in self.SYTX_KEYW.keys():
            if ir1 == ir:
                continue
            keyw = self.SYTX_KEYW[ir1]
            tokv = self.SYTX_TOKV[ir1]
            if self.valid_state(self.syntax_state[ir]) >= len(tokv):
                continue
            if tokv[self.valid_state(
                    self.syntax_state[ir])] == tokenize.SUBRULE and \
                    keyw[self.valid_state(self.syntax_state[ir])] == ir:
                self.syntax_state[ir] = self.toggle_state(
                    self.syntax_state[ir])
                if result:
                    self.syntax_state[ir] += 1
                else:
                    self.syntax_state[ir] = 0
                self.match_parent_rule(ir1, result)

    def wash_toktype(self, toktype, tokval):
        if toktype == tokenize.INDENT:
            self.deep_level += 1
        elif toktype == tokenize.DEDENT:
            self.deep_level -= 1
        if toktype == tokenize.NL:
            pass
        elif toktype == tokenize.NEWLINE:
            pass
        elif toktype == tokenize.STRING and self.blk_header:
            if tokval[0:3] == '"""' or tokval[0:3] == "'''":
                toktype = tokenize.DOC
        elif toktype == tokenize.OP:
            if tokval == '(':
                self.paren_ctrs += 1
            elif tokval == ')':
                self.paren_ctrs -= 1
            elif tokval == '[':
                self.brace_ctrs += 1
            elif tokval == ']':
                self.brace_ctrs -= 1
            elif tokval == '{':
                self.bracket_ctrs += 1
            elif tokval == '}':
                self.bracket_ctrs -= 1
            self.any_paren = self.paren_ctrs + self.brace_ctrs + \
                self.bracket_ctrs
        return toktype

    def wash_token(self, toktype, tokval, (srow, scol), (erow, ecol)):
        if toktype in (tokenize.INDENT,  tokenize.DEDENT,
                       tokenize.NEWLINE, tokenize.NL):
            if srow != self.last_row:
                self.tabstop = {}
                self.last_row = srow
        else:
            self.start = (srow, scol)
            self.stop = (erow, ecol)
        toktype = self.wash_toktype(toktype, tokval)
        if toktype != tokenize.COMMENT:
            self.file_header = False
            self.blk_header = False
        self.tabstop[scol] = tokenize.tok_name[toktype]
        return toktype, tokval

    def tokenize_source(self, ctx=None):
        # pdb.set_trace()
        ctx = {} if ctx is None else ctx
        for tokeno, (toktype, tokval,
                     (srow, scol),
                     (erow, ecol)) in enumerate(self.tokenized):
            toktype = self.wash_toktype(toktype, tokval)
            if self.any_paren and toktype in self.ghost:
                continue
            if ctx['opt_dbg']:
                print ">>> %s(%s)" % (tokval, toktype)
            completed = []
            reset = []
            for ir in self.SYTX_KEYW.keys():
                keyw = self.SYTX_KEYW[ir]
                tokv = self.SYTX_TOKV[ir]
                src_tkns = False
                for ver in sorted(self.SYTX_PRMS[ir], reverse=True):
                    if ver <= ctx['from_ver']:
                        src_tkns = self.SYTX_PRMS[ir][ver]
                        break
                tgt_tkns = False
                for ver in sorted(self.SYTX_PRMS[ir], reverse=True):
                    if ver <= ctx['to_ver']:
                        tgt_tkns = self.SYTX_PRMS[ir][ver]
                        break
                # rule parse ended
                if self.syntax_state[ir] < 0 or \
                        self.syntax_state[ir] >= len(keyw):
                    pass
                # rule child of parent rule
                elif tokv[self.syntax_state[ir]] == tokenize.SUBRULE:
                    self.syntax_state[ir] = self.toggle_state(
                        self.syntax_state[ir])
                # any token is valid
                elif tokv[self.syntax_state[ir]] == tokenize.ANY:
                    self.syntax_state[ir] += 1
                # zero, one or more tokens are valid until next match
                elif tokv[self.syntax_state[ir]] == tokenize.MORE:
                    self.syntax_state[ir] += 1
                    self.syntax_more[ir] = True
                    if keyw[self.syntax_state[ir]]:
                        if tokval == keyw[self.syntax_state[ir]]:
                            self.syntax_state[ir] += 1
                            self.syntax_more[ir] = False
                    elif toktype:
                        if toktype == tokv[self.syntax_state[ir]]:
                            self.syntax_state[ir] += 1
                            self.syntax_more[ir] = False
                # expression: match until right paren at the same level
                elif tokv[self.syntax_state[ir]] == tokenize.EXPR:
                    self.syntax_state[ir] += 1
                    self.syntax_more[ir] = self.any_paren + 1
                    if keyw[self.syntax_state[ir]]:
                        if tokval == keyw[self.syntax_state[ir]]:
                            self.syntax_state[ir] += 1
                            self.syntax_more[ir] = False
                    elif toktype:
                        if toktype == tokv[self.syntax_state[ir]]:
                            self.syntax_state[ir] += 1
                            self.syntax_more[ir] = False
                # matching more ...
                elif self.syntax_more[ir]:
                    if isinstance(self.syntax_more[ir], bool) or \
                            self.syntax_more[ir] == self.any_paren + 1:
                        if keyw[self.syntax_state[ir]]:
                            if tokval == keyw[self.syntax_state[ir]]:
                                self.syntax_state[ir] += 1
                                self.syntax_more[ir] = False
                        elif toktype:
                            if toktype == tokv[self.syntax_state[ir]]:
                                self.syntax_state[ir] += 1
                                self.syntax_more[ir] = False
                # exact text match
                elif keyw[self.syntax_state[ir]]:
                    if tokval == keyw[self.syntax_state[ir]]:
                        self.syntax_state[ir] += 1
                    else:
                        self.syntax_state[ir] = 0
                        reset.append(ir)
                elif toktype:
                    # match token type
                    if toktype == tokv[self.syntax_state[ir]]:
                        if src_tkns and tokval in src_tkns:
                            ix = src_tkns.index(tokval)
                            if ir not in self.syntax_replacement:
                                self.syntax_replacement[ir] = {}
                            self.syntax_replacement[ir][tokeno] = tgt_tkns[ix]
                        self.syntax_state[ir] += 1
                    # does not match
                    else:
                        self.syntax_state[ir] = 0
                        reset.append(ir)
                # token matches
                else:
                    # print "    else: self.syntax_state[ir] += 1"   # debug
                    self.syntax_state[ir] += 1
                if self.syntax_state[ir] >= len(keyw):
                    completed.append(ir)
            for ir in self.SYTX_KEYW.keys():
                # rule finally matches
                if ir in completed:
                    if ctx['opt_dbg']:
                        print "    match_parent_rule(%s, True)" % (ir)
                    self.match_parent_rule(ir, True)
                    # replace src text by replacements
                    for i in self.syntax_replacement[ir]:
                        self.replacements[i] = self.syntax_replacement[ir][i]
                    self.syntax_replacement[ir] = {}
                    self.syntax_state[ir] = 0
                # rule does not match
                elif ir in reset:
                    if ctx['opt_dbg']:
                        print "    match_parent_rule(%s, False)" % (ir)
                    self.match_parent_rule(ir, False)
                    self.syntax_replacement[ir] = {}
                elif ctx['opt_dbg']:
                    print "    match_rule(%s, evaluating)" % (ir)
            # yield toktype, tokval

    def apply_for_rules(self, ctx=None):
        ctx = {} if ctx is None else ctx
        self.tokenize_source(ctx=ctx)
        for tokeno in self.replacements:
            self.tokenized[tokeno][1] = self.replacements[tokeno]
        self.init_parse()

    def next_token(self, ctx=None):
        # pdb.set_trace()
        ctx = {} if ctx is None else ctx
        if self.tokeno < len(self.tokenized):
            tokenized = self.tokenized[self.tokeno]
            toktype, tokval = self.wash_token(tokenized[0],
                                              tokenized[1],
                                              tokenized[2],
                                              tokenized[3])
            self.tokeno += 1
            return toktype, tokval
        return False, False

    def add_whitespace(self, start):
        row, col = start
        ln = ''
        while row > self.prev_row:
            ln += '\n'
            self.prev_row += 1
            self.prev_col = 0
        col_offset = col - self.prev_col
        if col_offset:
            ln += ' ' * col_offset
        return ln

    def untoken(self, toktype, tokval):
        ln = self.add_whitespace(self.start)
        ln += tokval
        row, col = self.stop
        self.prev_row = row
        self.prev_col = col
        return ln


def get_filenames(ctx):
    if ctx.get('src_filepy', None) is None:
        ctx['src_filepy'] = 'example.py'
    src_filepy = ctx['src_filepy']
    if ctx.get('dst_filepy', None) is None:
        ctx['dst_filepy'] = ctx['src_filepy']
    dst_filepy = ctx['dst_filepy']
    return src_filepy, dst_filepy, ctx


def ver2ix(ver):
    if ver in ('6.0', '6.1', '7.0', '8.0', '9.0', '10.0'):
        return int(eval(ver) * 10)
    return 0


def get_versions(ctx):
    if ctx.get('odoo_ver', None) is None:
        ctx['odoo_ver'] = '7.0'
    ctx['to_ver'] = ver2ix(ctx['odoo_ver'])
    if ctx.get('from_odoo_ver', None) is None:
        ctx['from_odoo_ver'] = '0.0'
    ctx['from_ver'] = ver2ix(ctx['from_odoo_ver'])
    return ctx


def parse_file(ctx=None):
    # pdb.set_trace()
    ctx = {} if ctx is None else ctx
    src_filepy, dst_filepy, ctx = get_filenames(ctx)
    ctx = get_versions(ctx)
    if ctx['opt_verbose']:
        print "Reading %s -o%s -b%s" % (src_filepy,
                                        ctx['from_ver'],
                                        ctx['to_ver'])
    source = topep8(src_filepy)
    source.compile_rules(ctx)
    source.apply_for_rules(ctx)
    target = ""
    EOF = False
    while not EOF:
        toktype, tokval = source.next_token(ctx=ctx)
        if toktype is False:
            EOF = True
        else:
            target += source.untoken(toktype, tokval)
    if not ctx['dry_run']:
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        fd = open(dst_filepy, 'w')
        fd.write(target)
        fd.close()
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2015-2017 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-B', '--recall-debug-statements',
                        action='store_true',
                        dest='opt_recall_dbg',
                        default=False)
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-D', '--show-debug',
                        action='store_true',
                        dest='opt_dbg',
                        default=False)
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
    sts = parse_file(ctx=ctx)
    # sys.exit(sts)
