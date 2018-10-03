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


__version__ = "0.2.1.51"

METAS = ('0', '61', '70', '80', '90', '100', '110', '120')


class topep8():
    # Source file is parsed in tokens.
    # Every token is a list of:
    #        (id, value, (start_row, start_col), (end_row, end_col)
    #
    def __init__(self, src_filepy):
        self.src_filepy = src_filepy
        fd = open(src_filepy, 'rb')
        source = fd.read()
        fd.close()
        self.lines = source.split('\n')
        self.init_parse()
        self.init_rules()
        self.tokenized = []
        abs_row = 0
        abs_col = 0
        for (tokid, tokval,
             (sarow, sacol),
             (earow, eacol), line) in tokenize.generate_tokens(self.readline):
            srow = sarow - abs_row
            if sarow != abs_row:
                scol = sacol
            else:
                scol = sacol - abs_col
            abs_row = sarow
            abs_col = sacol 
            erow = earow - abs_row
            if earow != abs_row:
                ecol = eacol
            else:
                ecol = eacol - abs_col
            abs_row = earow
            abs_col = eacol 
            self.tokenized.append([tokid, tokval,
                                   (srow, scol),
                                   (erow, ecol)])

    def init_parse(self):
        self.lineno = 0
        self.abs_row = 0
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


    def init_rules(self):
        """Configuration .2p8 file syntax initialization"""
        self.GHOST_TOKENS = [tokenize.INDENT,  tokenize.DEDENT,
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
            'strdoc1': re.compile(r"'''"),
            'strdoc2': re.compile(r'"""'),
            'string1': re.compile(r"'{1,2}($|[^'])"),
            'endstr1': re.compile(r"('[^']*')"),
            'escstr1': r"\'",
            'string2': re.compile(r'"{1,2}($|[^"])'),
            'endstr2': re.compile(r'("[^"]*")'),
            'escstr2': r'\"',
            'remark_eol': re.compile(r'#'),
            'fullname': re.compile(r'[a-zA-Z_](\w*\.\w*)+'),
            'int': re.compile(r'[\d]+'),
            'name': re.compile(r'[a-zA-Z_]\w*'),
        }

    def set_active(self, ir):
        """Set rule state to active"""
        self.SYTX_RULES[ir]['state'] = 'active'

    def restart_state(self, ir):
        """Restart rule state"""
        self.set_active(ir)
        self.SYTX_RULES[ir]['wf_id'] = 0

    def init_rule_state(self, ir):
        """Initialize rule state"""
        self.restart_state(ir)
        self.SYTX_RULES[ir]['cur_min_max'] = [1, 1]
        self.SYTX_RULES[ir]['level'] = 0
        self.SYTX_RULES[ir]['matched_ids'] = []
        self.SYTX_RULES[ir]['token_id'] = 0

    def set_next_state(self, ir):
        """Advance state to next"""
        self.SYTX_RULES[ir]['wf_id'] += 1
        return self.SYTX_RULES[ir]['wf_id']

    def set_waiting4parent(self, ir):
        """Set rule state to waiting for parent"""
        self.SYTX_RULES[ir]['parent'] = self.cur_tokval(ir)
        self.SYTX_RULES[ir]['state'] = 'wait4parent'

    def is_waiting4parent(self, ir):
        """Check for active rule"""
        if self.SYTX_RULES[ir]['state'] != 'wait4parent':
            return False
        return True

    def set_waiting4more(self, ir):
        """Set rule waiting for match to end token"""
        self.set_next_state(self, ir)
        self.SYTX_RULES[ir]['state'] = 'wait4more'

    def is_waiting4more(self, ir):
        """Check for active rule"""
        if self.SYTX_RULES[ir]['state'] != 'wait4more':
            return False
        return True

    def set_waiting4expr(self, ir):
        """Set rule waiting for match to end token at the same level"""
        self.set_next_state(self, ir)
        self.SYTX_RULES[ir]['state'] = 'wait4expr'
        self.SYTX_RULES[ir]['level'] = self.any_paren

    def is_waiting4expr(self, ir):
        """Check for active rule"""
        if self.SYTX_RULES[ir]['state'] != 'wait4expr' or \
                self.SYTX_RULES[ir]['level'] != self.any_paren:
            return False
        return True

    def is_validated(self, ir):
        """Check for validated rule"""
        keywords, tokids = self.get_key_n_id_from_rule(ir)
        if self.cur_wf_id(ir) >= len(keywords):
            return True
        return False

    def cur_state(self, ir):
        """Get current active/valid rule state"""
        return self.SYTX_RULES[ir]['state']

    def cur_wf_id(self, ir):
        """Get current rule workflow position"""
        return self.SYTX_RULES[ir]['wf_id']

    def cur_tokid(self, ir):
        tokids = self.SYTX_RULES[ir]['keyids']
        return tokids[self.cur_wf_id(ir)]

    def cur_tokval(self, ir):
        keywords = self.SYTX_RULES[ir]['keywords']
        return keywords[self.cur_wf_id(ir)]

    def matches(self, ir, tokid, tokval):
        """Check if tokval matches rule token or tokid matches rule id"""
        if tokid == self.cur_tokid(ir) or tokval == self.cur_tokval(ir):
            return True
        return False

    def cur_wf_tknid(self, ir):
        """Get current match sequence position"""
        return self.SYTX_RULES[ir]['token_id']

    def store_value_to_replace(self, ir, tokeno):
        self.SYTX_RULES[ir]['matched_ids'].append(tokeno)
        self.SYTX_RULES[ir]['token_id'] += 1

    def replace_text_by_meta(self, ctx, ir):
        param_list_from = self.get_params_from_rule(ir, ctx['from_ver'])
        param_list_to = self.get_params_from_rule(ir, ctx['to_ver'])
        for tokeno in self.SYTX_RULES[ir]['matched_ids']:
            pass

    def readline(self):
        """Read next source line"""
        if self.lineno < len(self.lines):
            line = self.lines[self.lineno] + '\n'
            self.lineno += 1
        else:
            line = ''
        return line

    def get_key_n_id_from_rule(self, ir):
        return self.SYTX_RULES[ir]['keywords'], self.SYTX_RULES[ir]['keyids']

    def get_params_from_rule(self, ir, meta):
        """Get params of rule matches version <meta>"""
        params = []
        for ver in sorted(self.SYTX_RULES[ir]['meta'], reverse=True):
            if ver <= meta:
                params = self.SYTX_RULES[ir]['meta'][ver]
                break
        return params

    def parse_eol_rule(self, value, ipos, x):
        i = ipos + x.end()
        ipos = len(value)
        tokval = value[i:ipos].strip()
        return tokval, ipos

    def parse_doc_rule(self, value, ipos, x):
        """Found triple quote, all inside next triple quote is doc"""
        tokval, ipos = self.parse_eol_rule(value, ipos, x)
        tokid = tokenize.DOC
        return tokid, tokval, ipos

    def parse_remarkeol_rule(self, value, ipos, x):
        """Found token # (hash), all following it until eol is comment"""
        tokval, ipos = self.parse_eol_rule(value, ipos, x)
        tokid = tokenize.COMMENT
        return tokid, tokval, ipos

    def parse_escape_rule(self, value, ipos):
        """Escape token replaces single python keyword. Escape rule may be:
        $any     means any python token
        $more    means zero, one o more python tokens
                 (until token following $more in rule is matched)
        $name    means any python name
        $expr    means all tokens until global paren level decreases
        $?       previous token may be found zero or one time
        $*       previous token may be found zero, one or more time
        $+       previous token may be found one or more time
        $(       start capture replacement tokens
        $)       stop capture replacement tokens
        Every other value means current rule depends on another rule.
        @return: min_max, token_id, token, next_ipos
        """
        min_max = [1, 1]
        i = ipos
        if value[i + 1] == '?':
            return [0, 1], -1, False, ipos + 1
        elif value[i + 1] == '*':
            return [0, -1], -1, False, ipos + 1
        elif value[i + 1] == '+':
            return [1, -1], -1, False, ipos + 1
        elif value[i + 1] == '(':
            return [1, 1], tokenize.START_CAPTURE, False, ipos + 1
        elif value[i + 1] == ')':
            return [1, 1], tokenize.STOP_CAPTURE, False, ipos + 1
        x = self.SYNTAX_RE['name'].match(value[i + 1:])
        ipos += x.end() + 1
        tokval = value[i + 1:ipos]
        if tokval in ('name', 'any'):
            tokid = getattr(tokenize, tokval.upper())
            tokval = False
        elif tokval in ('more', 'expr'):
            tokid = getattr(tokenize, tokval.upper())
            tokval = False
            min_max = [0, -1]
        else:
            tokval = False
            tokid = tokenize.PARENT_RULE
        return min_max, tokid, tokval, ipos

    def parse_txt_rule(self, value, ipos, endtok, esctok):
        i = ipos
        x = True
        while x:
            x = self.SYNTAX_RE[endtok].match(value[ipos:])
            if x:
                ipos += x.end()
                if value[ipos:ipos + 1] == self.SYNTAX_RE[esctok]:
                    ipos += 1
                else:
                    x = None
            else:
                ipos = len(value)
        tokval = value[i:ipos]
        tokid = tokenize.STRING
        return tokid, tokval, ipos

    def parse_txt1_rule(self, value, ipos):
        return parse_txt_rule(self, value, ipos, 'endstr1', 'escstr1')

    def parse_txt2_rule(self, value, ipos):
        return parse_txt_rule(self, value, ipos, 'endstr2', 'escstr2')

    def parse_generic_rule(self, value, ipos, x, token_name):
        i = ipos
        ipos += x.end()
        tokval = value[i:ipos]
        tokid = token_name
        return tokid, tokval, ipos

    def compile_1_rule(self, rule):
        """Compile current rule <ir> for version <meta> parsing <value>
        All rules are stored in self.SYTX_RULES dictionary by rule id (name).
        Every entry is composed by:
            'regex':     regular expresion to validate rule
            'meta':      dictionay with Odoo version parameters
            'action':    action when rule is validated
                         for every version list of keywords of above regex
            'keywords':  list of keywords of above regex
            'keyids':    list of keyids of above regex
            'min_max_list':  list of min/max repetition for every above
                         keyword/keyid  (-1 means no limit)
            'state':     rule status, may be
                         ('active', 'wait4parent', 'wait4more', 'wait4expr')
            'wf_id':    current id in parsing workflow
            'min_max':  min and max repetition for current token
            'level':    level of parens when waiting for expression
            'matched_ids': matched tokens list against parameters
                        while rule parsing
            'token_id': next param token to match
            'parent':   parent rule while state is waiting for parent
            """
        # pdb.set_trace()
        keywords = []
        keyids = []
        min_max_list = []
        replacements = {}
        ipos = 0
        replacing = False
        while ipos < len(rule['regex']):
            unknown = True
            for istkn in self.SYNTAX:
                x = self.SYNTAX_RE[istkn].match(rule['regex'][ipos:])
                if not x:
                    continue
                unknown = False
                tokid = False
                min_max = [1,1]
                i = ipos
                if istkn in ('space', ):
                    ipos += x.end()
                    continue
                elif istkn == 'escape':
                    min_max, tokid, tokval, ipos = self.parse_escape_rule(
                        rule['regex'], ipos)
                    # Token is one of prior repetition: $? $* $+
                    if tokid == -1:
                        min_max_list[-1] = min_max
                        continue
                    # elif tokid == tokenize.NAME:
                    #     replacing = 1
                    # elif tokid == tokenize.START_CAPTURE:
                    #     replacing = True
                    # elif tokid == tokenize.STOP_CAPTURE:
                    #     replacing = False
                elif istkn == 'remark_eol':
                    tokid, tokval, ipos = self.parse_remarkeol_rule(
                        rule['regex'], ipos, x)
                elif istkn in ('strdoc1',
                               'strdoc2'):
                    tokid, tokval, ipos = self.parse_doc_rule(
                        rule['regex'], ipos)
                elif istkn == 'string1':
                    tokid, tokval, ipos = self.parse_txt1_rule(
                        rule['regex'], ipos)
                elif istkn == 'string2':
                    tokid, tokval, ipos = self.parse_txt2_rule(
                        rule['regex'], ipos)
                elif istkn == 'name':
                    tokid, tokval, ipos = self.parse_generic_rule(
                        rule['regex'], ipos, x, tokenize.NAME)
                else:
                    tokid, tokval, ipos = self.parse_generic_rule(
                        rule['regex'], ipos, x, tokenize.OP)
                break
            if unknown:
                print "Unknown token %s" % rule['regex'][ipos:]
                ipos += 1
            if tokid:
                keywords.append(tokval)
                keyids.append(tokid)
                min_max_list.append(min_max)
        for meta in METAS:
            if meta in rule['meta']:
                replacements[meta] = []
                ipos = 0
                tokval = ''
                while ipos < len(rule['meta'][meta]):
                    for istkn in self.SYNTAX:
                        if istkn == 'fullname':
                            continue
                        x = self.SYNTAX_RE[istkn].match(
                            rule['meta'][meta][ipos:])
                        if not x:
                            continue
                        if istkn in ('space', ):
                            ipos += x.end()
                            continue
                        elif istkn == 'string1':
                            tokid, tokval, ipos = self.parse_txt1_rule(
                                rule['meta'][meta], ipos)
                        elif istkn == 'string2':
                            tokid, tokval, ipos = self.parse_txt2_rule(
                                rule['meta'][meta], ipos)
                        elif istkn == 'name':
                            tokid, tokval, ipos = self.parse_generic_rule(
                                rule['meta'][meta], ipos, x, tokenize.NAME)
                        else:
                            tokid, tokval, ipos = self.parse_generic_rule(
                                rule['meta'][meta], ipos, x, tokenize.OP)
                        break
                    replacements[meta].append(tokval)
        ir = rule['id']
        del rule['id']
        self.SYTX_RULES[ir] = rule
        self.SYTX_RULES[ir]['keywords'] = keywords
        self.SYTX_RULES[ir]['keyids'] = keyids
        self.SYTX_RULES[ir]['min_max_list'] = min_max_list
        self.SYTX_RULES[ir]['meta'] = replacements
        self. init_rule_state(ir)


    def extr_tokens_from_line(self, text_rule, cur_rule, parsed, cont_break):
        """Extract from line rule elements"""
        next_cont = False
        parsed = False
        if not text_rule:
            pass
        if text_rule[-1] == '\n':
            text_rule = text_rule[0: -1]
        if text_rule[0] != '#' and text_rule[-1] == '\\':
            text_rule = text_rule[0: -1]
            next_cont = True
        if cont_break:
            cur_rule['regex'] += text_rule.rstrip()
            cont_break = next_cont
        elif text_rule[0] != '#':
            ipos = 0
            x = self.SYNTAX_RE['name'].match(text_rule[ipos:])
            if x:
                id = text_rule[ipos:x.end()]
                ipos += x.end()
                if cur_rule['id'] and cur_rule['id'] != id:
                    parsed = True
                else:
                    cur_rule['id'] = id
            if not parsed:
                meta = ''
                item = ''
                while ipos < len(text_rule):
                    x = self.SYNTAX_RE['space'].match(text_rule[ipos:])
                    if x:
                        ipos += x.end()
                    if text_rule[ipos] == ':':
                        if not cur_rule['regex']:
                            cur_rule['regex'] = text_rule[ipos + 1:].strip()
                        elif meta:
                            cur_rule['meta'][meta] = text_rule[
                                ipos + 1:].strip()
                        elif item in ('action', ):
                            cur_rule[item] = text_rule[ipos + 1:].strip()
                        ipos = len(text_rule)
                    elif text_rule[ipos] == '[' and not meta:
                        i = text_rule[ipos + 1:].find(']')
                        meta = text_rule[ipos + 1:ipos + 1 + i].strip()
                        ipos += i + 2
                    else:
                        x = self.SYNTAX_RE['name'].match(text_rule[ipos:])
                        if x:
                            item = text_rule[ipos:x.end()]
        return cur_rule, parsed, cont_break

    def read_rules_from_file(self, ctx, rule_file):
        def clear_cur_rule():
            return {'id': '',
                    'meta': {},
                    'regex': '',
                    'action': 'replace',
            }
        try:
            fd = open(rule_file, 'r')
        except:
            return
        cur_rule = clear_cur_rule()
        cont_break = False
        for text_rule in fd:
            cur_rule, parsed, cont_break = self.extr_tokens_from_line(
                text_rule, cur_rule, False, cont_break)
            while parsed:
                self.compile_1_rule(cur_rule)
                cur_rule = clear_cur_rule()
                cur_rule, parsed, cont_break = self.extr_tokens_from_line(
                    text_rule, cur_rule, parsed, cont_break)
        fd.close()

    def set_rulefn(self, rule_file):
        if rule_file.endswith('.py'):
            rule_file = rule_file[0:-3] + '.2p8'
        else:
            rule_file += '.2p8'
        return rule_file

    def compile_rules(self, ctx):
        self.SYTX_RULES = {}
        tokenize.NOOP = tokenize.N_TOKENS + 16
        tokenize.tok_name[tokenize.NOOP] = 'NOOP'
        tokenize.PARENT_RULE = tokenize.N_TOKENS + 17
        tokenize.tok_name[tokenize.PARENT_RULE] = 'PARENT_RULE'
        tokenize.DOC = tokenize.N_TOKENS + 18
        tokenize.tok_name[tokenize.DOC] = 'DOC'
        tokenize.ANY = tokenize.N_TOKENS + 19
        tokenize.tok_name[tokenize.ANY] = 'ANY'
        tokenize.MORE = tokenize.N_TOKENS + 20
        tokenize.tok_name[tokenize.MORE] = 'MORE'
        tokenize.EXPR = tokenize.N_TOKENS + 21
        tokenize.tok_name[tokenize.EXPR] = 'EXPR'
        tokenize.START_CAPTURE = tokenize.N_TOKENS + 22
        tokenize.tok_name[tokenize.START_CAPTURE] = 'START_CAPTURE'
        tokenize.STOP_CAPTURE = tokenize.N_TOKENS + 23
        tokenize.tok_name[tokenize.STOP_CAPTURE] = 'END_CAPTURE'
        #
        self.read_rules_from_file(ctx, self.set_rulefn(sys.argv[0]))
        self.read_rules_from_file(ctx, self.set_rulefn(ctx['src_filepy']))

    def match_parent_rule(self, ir, result):
        for ir1 in self.SYTX_RULES.keys():
            if ir1 == ir:
                continue
            if self.cur_tokid(ir1) == tokenize.PARENT_RULE and \
                    self.cur_tokval(ir1) == ir:
                set_active(ir1)

    def wash_tokid(self, tokid, tokval):
        if tokid == tokenize.INDENT:
            self.deep_level += 1
        elif tokid == tokenize.DEDENT:
            self.deep_level -= 1
        if tokid == tokenize.NL:
            pass
        elif tokid == tokenize.NEWLINE:
            pass
        elif tokid == tokenize.STRING and self.blk_header:
            if tokval[0:3] == '"""' or tokval[0:3] == "'''":
                tokid = tokenize.DOC
        elif tokid == tokenize.OP:
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
        if self.any_paren and tokid in self.GHOST_TOKENS:
            tokid = tokenize.NOOP
        return tokid

    def wash_token(self, tokid, tokval, (srow, scol), (erow, ecol)):
        if tokid in self.GHOST_TOKENS:
            if srow:
                self.tabstop = {}
                self.abs_row += srow
        else:
            self.start = (srow, scol)
            self.stop = (erow, ecol)
        tokid = self.wash_tokid(tokid, tokval)
        if tokid != tokenize.COMMENT:
            self.file_header = False
            self.blk_header = False
        self.tabstop[scol] = tokenize.tok_name[tokid]
        return tokid, tokval

    def replace_token(self, ir, tokid, tokval, param_list_from, param_list_to):
        # pdb.set_trace()
        if tokid == tokenize.COMMENT:
            for tok in param_list_from:
                if tokval.find(tok) >= 0:
                    tokval.replace(param_list_from, param_list_to)
        elif param_list_from and tokval in param_list_from:
            ix = param_list_from.index(tokval)
            if ir not in self.rule_param_list_to:
                self.rule_param_list_from[ir] = {}
                self.rule_param_list_to[ir] = {}
            self.rule_param_list_from[ir][tokeno] = param_list_from[ix]
            self.rule_param_list_to[ir][tokeno] = param_list_to[ix]

    def tokenize_source(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        # for tokeno, (tokid, tokval,
        #              (srow, scol),
        #              (erow, ecol)) in enumerate(self.tokenized):
        tokeno = 0
        while tokeno < len(self.tokenized):
            tokid, tokval, (srow, scol), (erow, ecol) = self.tokenized[tokeno]
            tokeno += 1
            tokid = self.wash_tokid(tokid, tokval)
            if tokid == tokenize.NOOP:
                continue
            if ctx['opt_dbg']:
                print ">>> %s(%s)" % (tokval, tokid)
            validated_rule_list = []
            for ir in self.SYTX_RULES.keys():
                keywords, tokids = self.get_key_n_id_from_rule(ir)
                param_list_from = self.get_params_from_rule(ir, ctx['from_ver'])
                # rule parse ended
                if self.is_waiting4parent(ir):
                    pass
                # rule child of parent rule: wait for parent result
                elif self.cur_tokid(ir) == tokenize.PARENT_RULE:
                    self.set_waiting4parent(ir)
                # replace string inside remark
                elif self.cur_tokid(ir) == tokenize.COMMENT:
                    self.replace_token(ir, tokid, tokval,
                                       param_list_from, param_list_to)
                # found the <any> token rule
                elif self.cur_tokid(ir) == tokenize.ANY:
                    self.set_next_state(ir)
                # found <zero, one or more> tokens rule
                elif self.cur_tokid(ir) == tokenize.MORE:
                    self.set_waiting4more(ir)
                    continue
                # found expression rule
                elif self.cur_tokid(ir) == tokenize.EXPR:
                    self.set_waiting4expr(ir)
                    continue
                # exact text match
                elif self.matches(ir, tokid, tokval):
                    if self.is_waiting4more(ir):
                        self.set_active(ir)
                    elif self.is_waiting4expr(ir):
                        self.set_active(ir)
                # rule is waiting for <zero, one or more> tokens
                elif self.is_waiting4more(ir):
                    continue
                # rule is waiting expression
                elif self.is_waiting4expr(ir):
                    continue
                # Rule is validated?
                if self.is_validated(ir):
                    validated_rule_list.append(ir)
                else:
                    i = self.cur_wf_tknid(ir)
                    if i < len(param_list_from) and \
                            tokval == param_list_from[i]:
                        self.store_value_to_replace(ir, tokeno)


            for ir in validated_rule_list:
                if ctx['opt_dbg']:
                    print "    match_parent_rule(%s, True)" % (ir)
                self.match_parent_rule(ir, True)
            # yield tokid, tokval

    def next_token(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        if self.tokeno < len(self.tokenized):
            tokenized = self.tokenized[self.tokeno]
            tokid, tokval = self.wash_token(tokenized[0],
                                            tokenized[1],
                                            tokenized[2],
                                            tokenized[3])
            self.tokeno += 1
            return tokid, tokval
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

    def untoken(self, tokid, tokval):
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
    pdb.set_trace()
    ctx = ctx or {}
    src_filepy, dst_filepy, ctx = get_filenames(ctx)
    ctx = get_versions(ctx)
    if ctx['opt_verbose']:
        print "Reading %s -o%s -b%s" % (src_filepy,
                                        ctx['from_ver'],
                                        ctx['to_ver'])
    source = topep8(src_filepy)
    source.compile_rules(ctx)
    source.tokenize_source(ctx)
    target = ""
    EOF = False
    while not EOF:
        tokid, tokval = source.next_token(ctx=ctx)
        if tokid is False:
            EOF = True
        else:
            target += source.untoken(tokid, tokval)
    if not ctx['dry_run']:
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        fd = open(dst_filepy, 'w')
        fd.write(target)
        fd.close()
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2015-2018 by SHS-AV s.r.l.",
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
