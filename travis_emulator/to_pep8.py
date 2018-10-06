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
import os
import sys
import re
from os0 import os0
from z0lib import parseoptargs
import tokenize


__version__ = "0.2.1.53"

METAS = ('0', '6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0')


class topep8():
    # Source file is parsed in tokens.
    # Every token is a list of:
    #        (id, value, (start_row, start_col), (end_row, end_col)
    #
    def __init__(self, src_filepy, ctx):
        self.src_filepy = src_filepy
        fd = open(src_filepy, 'rb')
        source = fd.read()
        fd.close()
        self.lines = source.split('\n')
        self.setup_py_header(ctx)
        self.init_parse()
        self.init_rules()
        self.tokenized = []
        abs_row = 1
        abs_col = 0
        for (tokid, tokval, (sarow, sacol), (earow, eacol),
                line) in tokenize.generate_tokens(self.readline):
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

    def setup_py_header(self, ctx):
        odoo_majver = int(ctx['to_ver'].split('.')[0])
        py_executable = ctx['set_exec']
        py_no_lint = ctx['no_lint']
        lineno = 0
        text = '#!/usr/bin/env python'
        if py_executable:
            if self.lines[lineno] != text:
                self.lines.insert(lineno, text)
                lineno += 1
        elif self.lines[lineno] == text:
            del self.lines[lineno]
        text = '# flake8: noqa'
        if py_no_lint:
            if self.lines[lineno] != text:
                self.lines.insert(lineno, text)
                lineno += 1
        elif self.lines[lineno] == text:
            del self.lines[lineno]

        text = '# -*- coding: utf-8 -*-'
        if odoo_majver < 11:
            if self.lines[lineno] != text:
                self.lines.insert(lineno, text)
                lineno += 1
        elif self.lines[lineno] == text:
            del self.lines[lineno]

    def init_parse(self):
        self.lineno = 0
        self.abs_row = 1
        self.tabstop = {}
        self.paren_ctrs = 0
        self.brace_ctrs = 0
        self.bracket_ctrs = 0
        self.any_paren = 0
        self.indent_level = 0
        self.file_header = True
        self.blk_header = True
        self.tokeno = 0
        self.last_tokid_is_nl = False


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
        self.LEX_RULES[ir]['state'] = 'active'

    def restart_state(self, ir):
        """Restart rule state"""
        self.set_active(ir)
        self.LEX_RULES[ir]['wf_id'] = 0
        self.LEX_RULES[ir]['cur_min_max'] = [1, 1]
        self.LEX_RULES[ir]['level'] = 0
        self.LEX_RULES[ir]['matched_ids'] = []
        self.LEX_RULES[ir]['token_id'] = 0

    def init_rule_state(self, ir):
        """Initialize rule state"""
        self.restart_state(ir)

    def set_next_state(self, ir):
        """Advance state to next"""
        self.LEX_RULES[ir]['wf_id'] += 1
        return self.LEX_RULES[ir]['wf_id']

    def set_waiting4parent(self, ir):
        """Set rule state to waiting for parent"""
        self.LEX_RULES[ir]['parent'] = self.cur_tokval(ir)
        self.LEX_RULES[ir]['state'] = 'wait4parent'

    def is_waiting4parent(self, ir):
        """Check for active rule"""
        if self.LEX_RULES[ir]['state'] != 'wait4parent':
            return False
        return True

    def set_waiting4more(self, ir):
        """Set rule waiting for match to end token"""
        self.set_next_state(ir)
        self.LEX_RULES[ir]['state'] = 'wait4more'

    def is_waiting4more(self, ir):
        """Check for active rule"""
        if self.LEX_RULES[ir]['state'] != 'wait4more':
            return False
        return True

    def set_waiting4expr(self, ir):
        """Set rule waiting for match to end token at the same level"""
        self.set_next_state(ir)
        self.LEX_RULES[ir]['state'] = 'wait4expr'
        self.LEX_RULES[ir]['level'] = self.any_paren

    def is_waiting4expr(self, ir):
        """Check for active rule"""
        if self.LEX_RULES[ir]['state'] != 'wait4expr' or \
                self.LEX_RULES[ir]['level'] != self.any_paren:
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
        return self.LEX_RULES[ir]['state']

    def cur_wf_id(self, ir):
        """Get current rule workflow position"""
        return self.LEX_RULES[ir]['wf_id']

    def cur_tokid(self, ir):
        if self.is_validated(ir):
            return 0
        tokids = self.LEX_RULES[ir]['keyids']
        return tokids[self.cur_wf_id(ir)]

    def cur_tokval(self, ir):
        if self.is_validated(ir):
            return ''
        keywords = self.LEX_RULES[ir]['keywords']
        return keywords[self.cur_wf_id(ir)]

    def matches(self, ir, tokid, tokval):
        """Check if tokval matches rule token or tokid matches rule id"""
        if self.cur_tokval(ir):
            if tokval == self.cur_tokval(ir):
                return True
        elif tokid == self.cur_tokid(ir):
            return True
        return False

    def cur_wf_tokid(self, ir):
        """Get current match sequence position"""
        return self.LEX_RULES[ir]['token_id']

    def store_value_to_replace(self, ir, param_list_from, tokid, tokval):
        i = self.cur_wf_tokid(ir)
        if i < len(param_list_from):
            if not param_list_from[i] or tokval == param_list_from[i]:
                self.LEX_RULES[ir]['matched_ids'].append(self.tokeno - 1)
                self.LEX_RULES[ir]['token_id'] += 1
            elif param_list_from[i]:
                self.LEX_RULES[ir]['matched_ids'] = []
                self.LEX_RULES[ir]['token_id'] = 0

    def do_action(self, ctx, ir):
        if self.LEX_RULES[ir]['action'] == 'replace':
            param_list_to = self.get_params_from_rule(ir, ctx['to_ver'])
            for i,tokeno in enumerate(self.LEX_RULES[ir]['matched_ids']):
                if i < len(param_list_to):
                    self.update_source_token(tokeno, False, param_list_to[i])

    def get_key_n_id_from_rule(self, ir):
        return self.LEX_RULES[ir]['keywords'], self.LEX_RULES[ir]['keyids']

    def get_params_from_rule(self, ir, meta):
        """Get params of rule matches version <meta>"""
        params = []
        for ver in sorted(self.LEX_RULES[ir]['meta'], reverse=True):
            if eval(ver) <= eval(meta):
                params = self.LEX_RULES[ir]['meta'][ver]
                break
        return params

    def parse_eol_rule(self, value, state, x):
        if x:
            i = state['ipos'] + x.end()
        else:
            i = state['ipos']
        state['ipos'] = len(value)
        tokval = value[i:state['ipos']].strip()
        return state, tokval

    def parse_doc_rule(self, value, state, x):
        """Found triple quote, all inside next triple quote is doc"""
        state, tokid, tokval = self.parse_eol_rule(value, state, x)
        tokid = tokenize.DOC
        return state, tokid, tokval, [1, 1]

    def parse_remarkeol_rule(self, value, state, x):
        """Found token # (hash), all following it until eol is comment"""
        state, tokval = self.parse_eol_rule(value, state, x)
        tokid = tokenize.COMMENT
        return state, tokid, tokval, [1, 1]

    def parse_escape_rule(self, value, state):
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
        i = state['ipos']
        if value[i + 1] == '?':
            return [0, 1], -1, False, state['ipos'] + 1
        elif value[i + 1] == '*':
            return [0, -1], -1, False, state['ipos'] + 1
        elif value[i + 1] == '+':
            return [1, -1], -1, False, state['ipos'] + 1
        elif value[i + 1] == '(':
            return [1, 1], tokenize.START_CAPTURE, False, state['ipos'] + 1
        elif value[i + 1] == ')':
            return [1, 1], tokenize.STOP_CAPTURE, False, state['ipos'] + 1
        x = self.SYNTAX_RE['name'].match(value[i + 1:])
        state['ipos'] += x.end() + 1
        tokval = value[i + 1:state['ipos']]
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
        return state, tokid, tokval, min_max

    def parse_txt_rule(self, value, state, endtok, esctok):
        i = state['ipos']
        x = True
        while x:
            x = self.SYNTAX_RE[endtok].match(value[state['ipos']:])
            if x:
                state['ipos'] += x.end()
                if value[state['ipos']:state['ipos'] + 1] == self.SYNTAX_RE[esctok]:
                    state['ipos'] += 1
                else:
                    x = None
            else:
                state['ipos'] = len(value)
        tokval = value[i:state['ipos']]
        tokid = tokenize.STRING
        return state, tokid, tokval, [1, 1]

    def parse_txt1_rule(self, value, state):
        return parse_txt_rule(self, value, state, 'endstr1', 'escstr1')

    def parse_txt2_rule(self, value, state):
        return parse_txt_rule(self, value, state, 'endstr2', 'escstr2')

    def parse_generic_rule(self, value, ipos, x, token_name):
        i = ipos
        ipos += x.end()
        tokval = value[i:ipos]
        tokid = token_name
        return tokid, tokval, ipos

    def init_state(self, enhanced=False, ident=False):
        return {
            'ipos': 0,
            'replacing': False,
            'enhanced': enhanced,
            'ident': ident,
        }

    def parse_1_rule(self, rule, state):
        for istkn in self.SYNTAX:
            if not state['enhanced'] and istkn == 'fullname':
                continue
            x = self.SYNTAX_RE[istkn].match(rule[state['ipos']:])
            if not x:
                continue
            unknown = False
            tokid = False
            tokval = ''
            min_max = [1,1]
            i = state['ipos']
            if istkn in ('space', ):
                state['ipos'] += x.end()
                if not state['ident'] or i > 0:
                    continue
                tokid = tokenize.INDENT
            elif istkn == 'escape':
                state, tokid, tokval, min_max = self.parse_escape_rule(
                    rule, state)
                # Token is one of prior repetition: $? $* $+
                if tokid == -1:
                    min_max_list[-1] = min_max
                    continue
                # elif tokid == tokenize.NAME:
                #     state['replacing'] = 1
                # elif tokid == tokenize.START_CAPTURE:
                #     state['replacing'] = True
                # elif tokid == tokenize.STOP_CAPTURE:
                #     state['replacing'] = False
            elif state['enhanced'] and istkn == 'remark_eol':
                state, tokid, tokval, min_max = self.parse_remarkeol_rule(
                    rule, state, x)
            elif istkn in ('strdoc1',
                           'strdoc2'):
                state, tokid, tokval, min_max = self.parse_doc_rule(
                    rule, state, x)
            elif istkn == 'string1':
                tokid, tokval, state['ipos'] = self.parse_txt1_rule(
                    rule, state['ipos'])
            elif istkn == 'string2':
                tokid, tokval, state['ipos'] = self.parse_txt2_rule(
                    rule, state['ipos'])
            elif istkn == 'name':
                tokid, tokval, state['ipos'] = self.parse_generic_rule(
                    rule, state['ipos'], x, tokenize.NAME)
            else:
                tokid, tokval, state['ipos'] = self.parse_generic_rule(
                    rule, state['ipos'], x, tokenize.OP)
            break
        if unknown:
            print "Unknown token %s" % rule[state['ipos']:]
            state['ipos'] += 1
        return state, tokid, tokval, min_max

    def compile_1_rule(self, rule):
        """Compile current rule <ir> for version <meta> parsing <value>
        All rules are stored in self.LEX_RULES dictionary by rule id (name).
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
        state = self.init_state(enhanced=True, ident=False)
        while state['ipos'] < len(rule['regex']):
            state, tokid, tokval, min_max = self.parse_1_rule(rule['regex'],
                                                              state)
            if tokid:
                keywords.append(tokval)
                keyids.append(tokid)
                min_max_list.append(min_max)
        for meta in METAS:
            if meta in rule['meta']:
                replacements[meta] = []
                state = self.init_state(enhanced=False, ident=False)
                while state['ipos'] < len(rule['meta'][meta]):
                    if keyids[0] == tokenize.COMMENT:
                        state, tokid, tokval, min_max = \
                            self.parse_remarkeol_rule(rule['meta'][meta],
                                                      state,
                                                      False)
                    else:
                        state, tokid, tokval, min_max = \
                            self.parse_1_rule(rule['meta'][meta],
                                              state)
                    replacements[meta].append(tokval)
        ir = rule['id']
        del rule['id']
        self.LEX_RULES[ir] = rule
        self.LEX_RULES[ir]['keywords'] = keywords
        self.LEX_RULES[ir]['keyids'] = keyids
        self.LEX_RULES[ir]['min_max_list'] = min_max_list
        self.LEX_RULES[ir]['meta'] = replacements
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
            state = self.init_state(enhanced=False, ident=True)
            state, tokid, tokval, min_max = self.parse_1_rule(text_rule,
                                                              state)
            if tokid == tokenize.NAME:
                id = tokval
                if cur_rule['id'] and cur_rule['id'] != id:
                    parsed = True
                else:
                    cur_rule['id'] = id
            elif tokid == tokenize.INDENT and \
                    cur_rule['id'] and \
                    not cur_rule['regex']:
                cur_rule['regex'] = text_rule[
                    state['ipos']:].strip()
                state['ipos'] = len(text_rule)
            if not parsed:
                meta = ''
                item = ''
                while state['ipos'] < len(text_rule):
                    state, tokid, tokval, min_max = self.parse_1_rule(
                        text_rule, state)
                    if tokid == tokenize.OP and tokval == ':':
                        if not cur_rule['regex']:
                            cur_rule['regex'] = text_rule[
                                state['ipos'] + 1:].strip()
                        elif meta:
                            cur_rule['meta'][meta] = text_rule[
                                state['ipos'] + 1:].strip()
                        elif item in ('action', ):
                            cur_rule[item] = text_rule[
                                state['ipos'] + 1:].strip()
                        state['ipos'] = len(text_rule)
                    elif tokid == tokenize.OP and tokval == '[' and not meta:
                        i = text_rule[state['ipos']:].find(']')
                        meta = text_rule[
                            state['ipos']: state['ipos'] + i].strip()
                        state['ipos'] += i + 1
                    elif tokid == tokenize.NAME:
                        item = tokval
                    else:
                        print 'Invalid rule %s' % text_rule
                        state['ipos'] += 1
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
        if 'id' in cur_rule:
            self.compile_1_rule(cur_rule)
        fd.close()

    def set_rulefn(self, rule_file):
        if rule_file.endswith('.py'):
            rule_file = rule_file[0:-3] + '.2p8'
        else:
            rule_file += '.2p8'
        return rule_file

    def compile_rules(self, ctx):
        self.LEX_RULES = {}
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
        if ctx['opt_ut7'] and ctx['to_ver'] == '8.0':
            for ir in self.LEX_RULES.keys():
                if ir[-3:] == '_78':
                    if '8.0' in self.LEX_RULES[ir]['meta']:
                        if '9.0' not in self.LEX_RULES[ir]['meta']:
                            self.LEX_RULES[ir]['meta']['9.0'] = self.LEX_RULES[
                                ir]['meta']['8.0']
                        del self.LEX_RULES[ir]['meta']['8.0']

    def match_parent_rule(self, ir, result):
        for ir1 in self.LEX_RULES.keys():
            if ir1 == ir:
                continue
            if self.cur_tokid(ir1) == tokenize.PARENT_RULE and \
                    self.cur_tokval(ir1) == ir:
                set_active(ir1)

    def wash_tokid(self, tokid, tokval):
        if tokid == tokenize.INDENT:
            self.indent_level += 1
        elif tokid == tokenize.DEDENT:
            self.indent_level -= 1
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

    def replace_token(self, ir, tokid, tokval):
        # pdb.set_trace()
        param_list_from = self.get_params_from_rule(ir, ctx['from_ver'])
        param_list_to = self.get_params_from_rule(ir, ctx['to_ver'])
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
        tokid = 1
        while tokid:
            tokid, tokval, (srow, scol), (erow, ecol) = self.next_token()
            if tokid == tokenize.NOOP:
                continue
            if ctx['opt_dbg']:
                print ">>> %s(%s)" % (tokid, tokval)
            validated_rule_list = []
            for ir in self.LEX_RULES.keys():
                keywords, tokids = self.get_key_n_id_from_rule(ir)
                param_list_from = self.get_params_from_rule(ir, ctx['from_ver'])
                # rule parse ended
                if self.is_waiting4parent(ir):
                    pass
                # rule child of parent rule: wait for parent result
                elif self.cur_tokid(ir) == tokenize.PARENT_RULE:
                    self.set_waiting4parent(ir)
                # replace string inside remark
                elif tokid == tokenize.COMMENT:
                    self.replace_token(ir, tokid, tokval)
                # found the <any> token rule
                elif self.cur_tokid(ir) == tokenize.ANY:
                    self.store_value_to_replace(ir,
                                                param_list_from,
                                                tokid,
                                                tokval)
                    self.set_next_state(ir)
                # found <zero, one or more> tokens rule
                elif self.cur_tokid(ir) == tokenize.MORE:
                    self.set_waiting4more(ir)
                    self.store_value_to_replace(ir,
                                                param_list_from,
                                                tokid,
                                                tokval)
                    continue
                # found expression rule
                elif self.cur_tokid(ir) == tokenize.EXPR:
                    self.set_waiting4expr(ir)
                    self.store_value_to_replace(ir,
                                                param_list_from,
                                                tokid,
                                                tokval)
                    continue
                # exact text match
                elif self.matches(ir, tokid, tokval):
                    if self.is_waiting4more(ir):
                        self.set_active(ir)
                    elif self.is_waiting4expr(ir):
                        self.set_active(ir)
                    else:
                        self.store_value_to_replace(ir,
                                                    param_list_from,
                                                tokid,
                                                tokval)
                    self.set_next_state(ir)
                # rule is waiting for <zero, one or more> tokens
                elif self.is_waiting4more(ir):
                    self.store_value_to_replace(ir,
                                                param_list_from,
                                                tokid,
                                                tokval)
                    continue
                # rule is waiting expression
                elif self.is_waiting4expr(ir):
                    self.store_value_to_replace(ir,
                                                param_list_from,
                                                tokid,
                                                tokval)
                    continue
                else:
                    self.restart_state(ir)
                # Rule is validated?
                if self.is_validated(ir):
                    validated_rule_list.append(ir)

            for ir in validated_rule_list:
                if ctx['opt_dbg']:
                    print "    match_parent_rule(%s, True)" % (ir)
                self.match_parent_rule(ir, True)
                self.do_action(ctx, ir)
                self.restart_state(ir)

    def next_token(self):
        if self.tokeno < len(self.tokenized):
            tokenized = self.tokenized[self.tokeno]
            tokid, tokval = self.wash_token(tokenized[0],
                                            tokenized[1],
                                            tokenized[2],
                                            tokenized[3])
            self.tokeno += 1
            tokid = self.wash_tokid(tokid, tokval)
            return tokid, tokval, tokenized[2], tokenized[3]
        return False, False, (0, 0), (0, 0)

    def untoken(self, tokid, tokval, start, stop):
        ln = self.add_whitespace(start)
        ln += tokval
        if tokid == tokenize.NEWLINE:
            self.last_tokid_is_nl = True
        else:
            self.last_tokid_is_nl = False
        return ln

    def add_whitespace(self, start):
        row, col = start
        ln = ''
        while row > 0:
            if not self.last_tokid_is_nl:
                ln += '\n'
            row -= 1
            self.abs_row += 1
        while col > 0:
            ln += ' '
            col -= 1
        return ln

    def readline(self):
        """Read next source line"""
        if self.lineno < len(self.lines):
            line = self.lines[self.lineno] + '\n'
            self.lineno += 1
        else:
            line = ''
        return line

    def update_source_token(self, tokeno, tokid, tokval):
        self.tokenized[tokeno][1] = tokval
        if tokid:
            self.tokenized[tokeno][0] = tokid

    def untokenize_2_text(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        self.init_parse()
        tokid = 1
        text_tgt = ''
        while tokid:
            tokid, tokval, (srow, scol), (erow, ecol) = self.next_token()
            if tokid and tokid != tokenize.NL:
                text_tgt += self.untoken(tokid,
                                         tokval,
                                         (srow, scol),
                                         (erow, ecol))
        return text_tgt


def get_filenames(ctx):
    if ctx.get('src_filepy', None) is None:
        ctx['src_filepy'] = 'example.py'
    src_filepy = ctx['src_filepy']
    if ctx.get('dst_filepy', None) is None:
        ctx['dst_filepy'] = ctx['src_filepy']
    dst_filepy = ctx['dst_filepy']
    return src_filepy, dst_filepy, ctx

def get_versions(ctx):
    if ctx.get('odoo_ver', None) is None:
        ctx['odoo_ver'] = '7.0'
    ctx['to_ver'] = ctx['odoo_ver']
    if ctx.get('from_odoo_ver', None) is None:
        ctx['from_odoo_ver'] = '0'
    ctx['from_ver'] = ctx['from_odoo_ver']
    return ctx


def parse_file(ctx=None):
    # pdb.set_trace()
    ctx = ctx or {}
    src_filepy, dst_filepy, ctx = get_filenames(ctx)
    ctx = get_versions(ctx)
    if ctx['opt_verbose']:
        print "Reading %s -o%s -b%s" % (src_filepy,
                                        ctx['from_ver'],
                                        ctx['to_ver'])
    source = topep8(src_filepy, ctx)
    source.compile_rules(ctx)
    source.tokenize_source(ctx)
    text_tgt = source.untokenize_2_text(ctx)
    if not ctx['dry_run']:
        if ctx['opt_verbose']:
            print "Writing %s" % dst_filepy
        if dst_filepy != src_filepy:
            fd = open(ctx['dst_filepy'], 'w')
            fd.write(os0.b(text_tgt))
            fd.close()
        else:
            tmpfile = '%s.tmp' % dst_filepy
            bakfile = '%s.bak' % dst_filepy
            fd = open(tmpfile, 'w')
            fd.write(os0.b(text_tgt))
            fd.close()
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            os.rename(src_filepy, bakfile)
            os.rename(tmpfile, dst_filepy)
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2015-2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-A', '--odoo-italia-associzione',
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
    parser.add_argument('-D', '--show-debug',
                        action='store_true',
                        dest='opt_dbg',
                        default=False)
    parser.add_argument('-F', '--from-odoo-ver',
                        action='store',
                        dest='from_odoo_ver')
    parser.add_argument('-G', '--gpl-info',
                        action='store_true',
                        dest='opt_gpl',
                        default=False)
    parser.add_argument('-L', '--no-lint',
                        action='store_true',
                        dest='no_lint',
                        default=False)
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-u', '--unit-test',
                        action='store_true',
                        dest='opt_ut7',
                        default=False)
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-X', '--set-executable',
                        action='store_true',
                        dest='set_exec',
                        default=False)
    parser.add_argument('src_filepy')
    parser.add_argument('dst_filepy',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    sts = parse_file(ctx=ctx)
    # sys.exit(sts)
