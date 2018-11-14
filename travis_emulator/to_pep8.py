# -*- coding: utf-8 -*-
#
# Copyright 2018-19 SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Convert src python to PEP8 with OCA rules

Based non rule file.

All rules are stored in self.LEX_RULES dictionary by rule id (name).
Every rule has a python name; if name ends with _78, rule may not applied
to odoo 8.0 if -u switch is supplied: means convert to odoo 8.0 holding old api

Every entry is composed by:
    'regex':        regular expresion to validate rule (text)
    'keywords':     list of keywords of above 'regex'
    'keyids':       list of keyids of above 'regex'
    'min_max_list': list of min/max repetition for every above keyword/keyid
                    item (-1 means no limit)
    'action':       action to apply when rule is validated
    'meta':         dictionay with Odoo version keywords to replace/evaluate
    'meta_ids':     dictionay with Odoo version keyids to replace/evaluate
    'state':        rule status, may be
                    ('active', 'wait4parent', 'wait4more', 'wait4expr')
    'wf_id':        current id in parsing workflow
    'min_max':      min and max repetition for current token
    'level':        level of parens when waiting for expression
    'matched_ids':  matched tokens list from source to replace against
                    parameters, while rule parsing
    'token_id':     next param token to match
    'parent':       parent rule while state is waiting for parent
"""

import pdb
import os
import re
import sys
import tokenize

from os0 import os0

from z0lib import parseoptargs

__version__ = "0.2.1.66"

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
        if ctx['opt_gpl']:
            self.write_license_info(ctx)
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
            tokid = self.wash_tokid(tokid, tokval)
            self.tokenized.append([tokid, tokval,
                                   (srow, scol),
                                   (erow, ecol)])
        self.init_parse()

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

    def write_license_info(self, ctx):
        odoo_majver = int(ctx['to_ver'].split('.')[0])
        req_copyrights = ctx['opt_copy'].split(',')
        for org in req_copyrights:
            if org not in ('oca', 'oia', 'shs', 'zero'):
                print('Invalid copyright option! Values are zero, oca or oia')
                return
        auth_antoniov = 'Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>'
        website_oia = 'https://www.odoo-italia.org'
        website_shs = 'https://www.shs-av.com'
        website_zero = 'https://www.zeroincombenze.it'
        website_oca = 'https://odoo-community.org'
        copy_found = []
        lineno = 0
        while lineno < len(self.lines) and \
                self.lines[lineno] in ('#!/usr/bin/env python',
                                       '# flake8: noqa',
                                       '# -*- coding: utf-8 -*-',
                                       ):
            lineno +=1
        while lineno < len(self.lines) and \
                self.lines[lineno] and \
                not re.match(r'^# *([Cc]opyright|\(C\)|©)',
                             self.lines[lineno]):
            if self.lines[lineno] == '' or self.lines[lineno][0] == '#':
                del self.lines[lineno]
            else:
                break
        self.lines.insert(lineno, '#')
        lineno += 1
        rex = r'^# *([Cc]opyright|\([Cc]\)|©|http:|https:|\w+\@[a-zA-z0-9-.]+)'
        while lineno < len(self.lines) and \
                self.lines[lineno] and \
                re.match(rex, self.lines[lineno]):
            if re.search('antoniomaria.vigliotti@gmail.com',
                        self.lines[lineno]):
                copy_found.append('antoniov')
                if 'zero' in req_copyrights:
                    del self.lines[lineno]
                    continue
            elif re.search('https*://[w.]*odoo-italia.org',
                          self.lines[lineno]):
                copy_found.append('oia')
                self.lines[lineno] = self.lines[lineno].replace(
                    'http://odoo-italia.org', website_oia)
                self.lines[lineno] = self.lines[lineno].replace(
                    'http://www.odoo-italia.org', website_oia)
            elif re.search('https*://odoo-community.org',
                          self.lines[lineno]):
                copy_found.append('oia')
                self.lines[lineno] = self.lines[lineno].replace(
                    'http://odoo-italia.org', website_oia)
                self.lines[lineno] = self.lines[lineno].replace(
                    'http://www.odoo-italia.org', website_oia)
            elif re.search('https*://[w.]*shs-av.com',
                          self.lines[lineno]) or \
                    re.search('Odoo Community Association',
                             self.lines[lineno]):
                copy_found.append('oca')
            elif re.search('https*://[w.]*zeroincombenze.it',
                          self.lines[lineno]):
                copy_found.append('zero')
                self.lines[lineno] = self.lines[lineno].replace(
                    'https://www.zeroincombenze.it', website_zero)
            ipos = 1
            x = re.match('^ *([Cc]opyright|\([Cc]\)|©)',
                         self.lines[lineno][ipos:])
            if x:
                ipos += x.end() + 1
            x = re.match('^ *([Cc]opyright|\([Cc]\)|©)',
                         self.lines[lineno][ipos:])
            if x:
                ipos += x.end() + 1
            new_line = '# Copyright'
            x = re.match('^ *[0-9]+',
                         self.lines[lineno][ipos:])
            if x:
                i = ipos + x.end()
                new_line += ' '
                new_line += self.lines[lineno][ipos:i]
                ipos = i
                if self.lines[lineno][ipos] == '-':
                    new_line += self.lines[lineno][ipos]
                    ipos += 1
                    x = re.match('[0-9]+', self.lines[lineno][ipos:])
                    if x:
                        i = x.end()
                        if i == 4:
                            ipos += 2
                            i = ipos + i -2
                        else:
                            i += ipos
                        new_line += self.lines[lineno][ipos:i]
                        ipos = i
                else:
                    while self.lines[lineno][ipos] == ' ':
                        ipos += 1
                    new_line += '    '
                new_line += self.lines[lineno][ipos:]
            else:
                new_line += ' 2018-19 '
                new_line += self.lines[lineno][ipos:]
            if new_line[16:19] == '-20':
                new_line = new_line[0:17] + new_line[19:]
            self.lines[lineno] = new_line
            lineno += 1
        for org in req_copyrights:
            if org not in copy_found:
                if org == 'oca':
                    line = '# Copyright 2018-19 - Odoo Community Association' \
                           ' <%s>' % website_oca
                elif org == 'oia':
                    line = '# Copyright 2018-19 - Odoo Italia Associazione' \
                           ' <%s>' % website_oia
                elif org == 'shs':
                    line = '# Copyright 2018-19 - SHS-AV s.r.l.' \
                           ' <%s>' % website_shs
                elif org == 'zero':
                    line = '# Copyright 2018-19 - SHS-AV s.r.l.' \
                           ' <%s>' % website_zero
                else:
                    line = '# Copyright 2018-19 - %s' % auth_antoniov
                self.lines.insert(lineno, line)
                lineno += 1
        while lineno < len(self.lines) and \
                (not self.lines[lineno] or
                 self.lines[lineno] == '#' or
                 re.match('^# License .GPL', self.lines[lineno])):
            del self.lines[lineno]
        self.lines.insert(lineno, '#')
        lineno += 1
        if odoo_majver > 8:
            self.lines.insert(
                lineno,
                '# License LGPL-3.0 or later ' \
                '(http://www.gnu.org/licenses/lgpl).')
        else:
            self.lines.insert(
                lineno,
                '# License AGPL-3.0 or later ' \
                '(http://www.gnu.org/licenses/agpl).')
        lineno += 1
        self.lines.insert(lineno, '#')
        while lineno < len(self.lines) and \
                (self.lines[lineno] and
                 self.lines[lineno][0] == '#' and
                 not re.match('^# .*This program is free software',
                              self.lines[lineno])):
            lineno += 1
        if lineno < len(self.lines) and \
                (self.lines[lineno] and
                 re.match('^# .*This program is free software',
                          self.lines[lineno])):
            while lineno < len(self.lines) and \
                    self.lines[lineno] and \
                    not re.match('^# .*http://www.gnu.org/licenses',
                                 self.lines[lineno]):
                del self.lines[lineno]
            if lineno < len(self.lines) and \
                    self.lines[lineno] and \
                    re.match('^# .*http://www.gnu.org/licenses',
                                 self.lines[lineno]):
                del self.lines[lineno]
            while lineno < len(self.lines) and \
                    self.lines[lineno] and \
                    (self.lines[lineno] == '#' or
                     self.lines[lineno][0:4] == '####'):
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
        self.last_newlines = 0


    def init_rules(self):
        """Configuration .2p8 file syntax initialization"""
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
        tokenize.TOKENS = tokenize.N_TOKENS + 24
        tokenize.tok_name[tokenize.TOKENS] = 'TOKENS'
        #
        self.INDENTS = [tokenize.INDENT,  tokenize.DEDENT]
        self.NEWLINES = [tokenize.NEWLINE, tokenize.NL]
        self.GHOST_TOKENS = [tokenize.INDENT,  tokenize.DEDENT,
                             tokenize.NOOP, tokenize.NL]
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

    def store_value_to_replace(self, ctx, ir, tokid, tokval):
        param_list_from, ids_from_list = self.get_params_from_rule(
            ir, ctx['from_ver'], 'from')
        if tokid == tokenize.COMMENT:
            param_list_to, ids_from_list = self.get_params_from_rule(
                ir, ctx['to_ver'], 'to')
            remark = tokval
            for i,tok in enumerate(param_list_from):
                if remark.find(tok) >= 0:
                    remark = remark.replace(param_list_from[i],
                                            param_list_to[i])
            if remark != tokval:
                self.LEX_RULES[ir]['matched_ids'] = [self.tokeno - 1]
                self.LEX_RULES[ir]['token_id'] = 1
            return
        i = self.cur_wf_tokid(ir)
        if i < len(param_list_from):
            if ids_from_list[i] == tokenize.START_CAPTURE:
                while i < len(ids_from_list) and \
                        ids_from_list[i] != tokenize.STOP_CAPTURE:
                    i += 1
                i += 1
                self.LEX_RULES[ir]['token_id'] += i
            if ids_from_list[i] == tokenize.MORE:
                if tokval == param_list_from[i + 1]:
                    self.LEX_RULES[ir]['token_id'] += 1
            # elif not param_list_from[i] or tokval == param_list_from[i]:
            elif tokval == param_list_from[i]:
                self.LEX_RULES[ir]['matched_ids'].append(self.tokeno - 1)
                self.LEX_RULES[ir]['token_id'] += 1
            elif param_list_from[i]:
                self.LEX_RULES[ir]['matched_ids'] = []
                self.LEX_RULES[ir]['token_id'] = 0

    def do_action(self, ctx, ir):
        if self.LEX_RULES[ir]['action'] == 'replace':
            if self.LEX_RULES[ir]['matched_ids']:
                param_list_to, ids_from_list = self.get_params_from_rule(
                    ir, ctx['to_ver'], 'to')
                offset = 0
                for i,tokeno in enumerate(self.LEX_RULES[ir]['matched_ids']):
                    if i < len(param_list_to):
                        self.update_source_token(tokeno,
                                                 ids_from_list[i],
                                                 param_list_to[i],
                                                 ir=ir,
                                                 ctx=ctx)
                    else:
                        tokeno -= offset
                        offset += 1
                        # param_to has less values than matched source
                        self.delete_source_token(tokeno)
                # check if param_to has more values than matched source
                i = len(self.LEX_RULES[ir]['matched_ids'])
                tokeno = self.LEX_RULES[ir]['matched_ids'][-1] + 1
                while i < len(param_list_to):
                    self.insert_source_token(tokeno,
                                             ids_from_list[i],
                                             param_list_to[i])
                    i += 1
                    tokeno += 1


    def get_key_n_id_from_rule(self, ir):
        return self.LEX_RULES[ir]['keywords'], self.LEX_RULES[ir]['keyids']

    def get_from_ver_in_rule(self, ir, meta, direction):
        if direction == 'from' and '0' in self.LEX_RULES[ir]['meta']:
            return '0'
        top = 0.0
        meta_val = eval(meta)
        for ver in self.LEX_RULES[ir]['meta']:
            if eval(ver) <= meta_val and eval(ver) >= top:
                res = ver
                top = eval(ver)
        return res

    def get_params_from_rule(self, ir, meta, direction):
        """Get params of rule matches version <meta>"""
        params = []
        param_ids = []
        ver = self.get_from_ver_in_rule(ir, meta, direction)
        params = self.LEX_RULES[ir]['meta'][ver]
        param_ids = self.LEX_RULES[ir]['meta_ids'][ver]
        return params, param_ids

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
            state['ipos'] += 2
            return state, -1, False, [0, 1]
        elif value[i + 1] == '*':
            state['ipos'] += 2
            return state, -1, False, [0, -1]
        elif value[i + 1] == '+':
            state['ipos'] += 2
            return state, -1, False, [1, -1]
        elif value[i + 1] == '(':
            state['ipos'] += 2
            return state, tokenize.START_CAPTURE, False, [1, 1]
        elif value[i + 1] == ')':
            state['ipos'] += 2
            return state, tokenize.STOP_CAPTURE, False, [1, 1]
        x = self.SYNTAX_RE['name'].match(value[i + 1:])
        state['ipos'] += x.end() + 1
        tokval = value[i + 1:state['ipos']]
        if tokval in ('name', 'any', 'tokens'):
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

    def parse_token_text(self, text, state):
        """Parse 1 token from source text"""
        for istkn in self.SYNTAX:
            if not state['enhanced'] and istkn == 'fullname':
                continue
            x = self.SYNTAX_RE[istkn].match(text[state['ipos']:])
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
                    text, state)
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
                    text, state, x)
            elif istkn in ('strdoc1',
                           'strdoc2'):
                state, tokid, tokval, min_max = self.parse_doc_rule(
                    text, state, x)
            elif istkn == 'string1':
                tokid, tokval, state['ipos'] = self.parse_txt1_rule(
                    text, state['ipos'])
            elif istkn == 'string2':
                tokid, tokval, state['ipos'] = self.parse_txt2_rule(
                    text, state['ipos'])
            elif istkn == 'name':
                tokid, tokval, state['ipos'] = self.parse_generic_rule(
                    text, state['ipos'], x, tokenize.NAME)
            else:
                tokid, tokval, state['ipos'] = self.parse_generic_rule(
                    text, state['ipos'], x, tokenize.OP)
            break
        if unknown:
            print "Unknown token %s" % text[state['ipos']:]
            state['ipos'] += 1
        return state, tokid, tokval, min_max

    def compile_1_rule(self, rule):
        """Compile current rule for version <meta> parsing <value>
        """
        # pdb.set_trace()
        keywords = []
        keyids = []
        min_max_list = []
        replacements = {}
        replacem_ids = {}
        state = self.init_state(enhanced=True, ident=False)
        while state['ipos'] < len(rule['regex']):
            state, tokid, tokval, min_max = self.parse_token_text(
                rule['regex'],
                state)
            keywords.append(tokval)
            keyids.append(tokid)
            min_max_list.append(min_max)
        for meta in METAS:
            if meta in rule['meta']:
                replacements[meta] = []
                replacem_ids[meta] = []
                state = self.init_state(enhanced=False, ident=False)
                while state['ipos'] < len(rule['meta'][meta]):
                    if keyids[0] == tokenize.COMMENT:
                        state, tokid, tokval, min_max = \
                            self.parse_remarkeol_rule(rule['meta'][meta],
                                                      state,
                                                      False)
                    else:
                        state, tokid, tokval, min_max = \
                            self.parse_token_text(rule['meta'][meta],
                                                  state)
                    # if tokid not in (tokenize.START_CAPTURE,
                    #                  tokenize.STOP_CAPTURE):
                    replacements[meta].append(tokval)
                    replacem_ids[meta].append(tokid)
        ir = rule['id']
        del rule['id']
        self.LEX_RULES[ir] = rule
        self.LEX_RULES[ir]['keywords'] = keywords
        self.LEX_RULES[ir]['keyids'] = keyids
        self.LEX_RULES[ir]['min_max_list'] = min_max_list
        self.LEX_RULES[ir]['meta'] = replacements
        self.LEX_RULES[ir]['meta_ids'] = replacem_ids
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
            state, tokid, tokval, min_max = self.parse_token_text(text_rule,
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
                    state, tokid, tokval, min_max = self.parse_token_text(
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
                    'meta_ids': {},
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
        self.read_rules_from_file(ctx, self.set_rulefn(sys.argv[0]))
        self.read_rules_from_file(ctx, self.set_rulefn(ctx['src_filepy']))
        for ir in self.LEX_RULES.keys():
            if ir[-3:] == '_78' and ctx['opt_ut7'] and ctx['to_ver'] == '8.0':
                if '8.0' in self.LEX_RULES[ir]['meta']:
                    if '9.0' not in self.LEX_RULES[ir]['meta']:
                        self.LEX_RULES[ir]['meta']['9.0'] = self.LEX_RULES[
                            ir]['meta']['8.0']
                        self.LEX_RULES[ir]['meta_ids']['9.0'] = self.LEX_RULES[
                            ir]['meta_ids']['8.0']
                    del self.LEX_RULES[ir]['meta']['8.0']
                    del self.LEX_RULES[ir]['meta_ids']['8.0']
            if tokenize.TOKENS in self.LEX_RULES[ir]['keyids']:
                stop_capture = len(self.LEX_RULES[ir]['keyids'])
                if 'START_CAPTURE' not in self.LEX_RULES[ir]['keyids']:
                    start_capture = -1
                    del_items = True
                else:
                    start_capture = stop_capture
                    del_items = False
                ix = self.LEX_RULES[ir]['keyids'].index(tokenize.TOKENS)
                del self.LEX_RULES[ir]['keywords'][ix]
                del self.LEX_RULES[ir]['keyids'][ix]
                ver = self.get_from_ver_in_rule(ir, ctx['from_ver'], 'from')
                # items_to_delete = []
                offset = 0
                for i in range(len(self.LEX_RULES[ir]['meta'][ver])):
                    if self.LEX_RULES[ir]['meta_ids'][ver][i] == tokenize.START_CAPTURE:
                         start_capture = i
                         offset -= 1
                         continue
                    elif self.LEX_RULES[ir]['meta_ids'][ver][i] == tokenize.STOP_CAPTURE:
                         stop_capture = i
                         offset -= 1
                         continue
                    if i > stop_capture:
                        break
                    if i <= start_capture:
                        continue
                    self.LEX_RULES[ir]['keywords'].insert(
                        ix + i + offset,
                        self.LEX_RULES[ir]['meta'][ver][i])
                    self.LEX_RULES[ir]['keyids'].insert(
                        ix + i + offset,
                        self.LEX_RULES[ir]['meta_ids'][ver][i])
                    # if del_items:
                    #     items_to_delete.insert(0, i)
                # for i in items_to_delete:
                #     del self.LEX_RULES[ir]['meta'][ver][i]
                #     del self.LEX_RULES[ir]['meta_ids'][ver][i]

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
        if tokid == tokenize.STRING and self.blk_header:
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
        if self.any_paren:
            if tokid in self.INDENTS:
                tokid = tokenize.NOOP
            elif tokid == tokenize.NEWLINE:
                tokid = tokenize.NL
        elif tokid == tokenize.NL:
            tokid = tokenize.NEWLINE
        return tokid

    def wash_token(self, tokid, tokval, (srow, scol), (erow, ecol)):
        if tokid in self.GHOST_TOKENS:
            if srow:
                self.tabstop = {}
                self.abs_row += srow
        else:
            self.start = (srow, scol)
            self.stop = (erow, ecol)
        # tokid = self.wash_tokid(tokid, tokval)
        if tokid != tokenize.COMMENT:
            self.file_header = False
            self.blk_header = False
        self.tabstop[scol] = tokenize.tok_name[tokid]
        return tokid, tokval

    def tokenize_source(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        tokid = 1
        while tokid:
            tokid, tokval, (srow, scol), (erow, ecol) = self.next_token()
            if tokid in self.GHOST_TOKENS:
                continue
            if ctx['opt_dbg']:
                print ">>> %s(%s)" % (tokid, tokval)
            validated_rule_list = []
            for ir in self.LEX_RULES.keys():
                # rule waiting for parent validation
                if self.is_waiting4parent(ir):
                    pass
                # rule child of parent rule: set wait for parent result
                elif self.cur_tokid(ir) == tokenize.PARENT_RULE:
                    self.set_waiting4parent(ir)
                # replace string inside remark
                elif self.cur_tokid(ir) == tokenize.COMMENT and \
                        tokid == tokenize.COMMENT:
                    # import pdb
                    # pdb.set_trace()
                    # self.action_replace_token(ir, tokid, tokval)
                    self.store_value_to_replace(ctx,
                                                ir,
                                                tokid,
                                                tokval)
                    self.set_next_state(ir)
                # found the <any> token rule
                elif self.cur_tokid(ir) == tokenize.ANY:
                    self.store_value_to_replace(ctx,
                                                ir,
                                                tokid,
                                                tokval)
                    self.set_next_state(ir)
                # found <zero, one or more> tokens rule
                elif self.cur_tokid(ir) == tokenize.MORE:
                    self.set_waiting4more(ir)
                    self.store_value_to_replace(ctx,
                                                ir,
                                                tokid,
                                                tokval)
                    continue
                # found expression rule
                elif self.cur_tokid(ir) == tokenize.EXPR:
                    self.set_waiting4expr(ir)
                    self.store_value_to_replace(ctx,
                                                ir,
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
                        self.store_value_to_replace(ctx,
                                                    ir,
                                                    tokid,
                                                    tokval)
                    self.set_next_state(ir)
                # rule is waiting for <zero, one or more> tokens
                elif self.is_waiting4more(ir):
                    self.store_value_to_replace(ctx,
                                                ir,
                                                tokid,
                                                tokval)
                    continue
                # rule is waiting expression
                elif self.is_waiting4expr(ir):
                    self.store_value_to_replace(ctx,
                                                ir,
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
            return tokid, tokval, tokenized[2], tokenized[3]
        return False, False, (0, 0), (0, 0)

    def untoken(self, tokid, tokval, start, stop):
        ln = self.add_whitespace(start)
        ln += tokval
        if tokid in self.NEWLINES:
            self.last_newlines += 1
        else:
            self.last_newlines = 0
        return ln

    def add_whitespace(self, start):
        row, col = start
        ln = ''
        while row > 0:
            if not self.last_newlines:
                ln += '\n'
                self.last_newlines -= 1
            row -= 1
            self.abs_row += 1
        ln += ' ' * col
        return ln

    def readline(self):
        """Read next source line"""
        if self.lineno < len(self.lines):
            line = self.lines[self.lineno] + '\n'
            self.lineno += 1
        else:
            line = ''
        return line

    def update_source_token(self, tokeno, tokid, tokval, ir=None, ctx=None):
        if tokid == tokenize.COMMENT:
            ir = ir or ''
            ctx = ctx or {}
            param_list_from, ids_from_list = self.get_params_from_rule(
                    ir, ctx['from_ver'], 'from')
            param_list_to, ids_from_list = self.get_params_from_rule(
                    ir, ctx['to_ver'], 'to')
            remark = self.tokenized[tokeno][1]
            for i,tok in enumerate(param_list_from):
                if remark.find(tok) >= 0:
                    remark = remark.replace(param_list_from[i],
                                            param_list_to[i])
            self.tokenized[tokeno][1] = remark
        else:
            self.tokenized[tokeno][1] = tokval
            if tokid:
                self.tokenized[tokeno][0] = tokid

    def insert_source_token(self, tokeno, tokid, tokval):
        self.tokenized.insert(tokeno, [tokid, tokval, [0,0], [0,0]])

    def delete_source_token(self, tokeno):
        del self.tokenized[tokeno]

    def untokenize_2_text(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        self.init_parse()
        tokid = 1
        text_tgt = ''
        while tokid:
            tokid, tokval, (srow, scol), (erow, ecol) = self.next_token()
            if tokid:
                text_tgt += self.untoken(tokid,
                                         tokval,
                                         (srow, scol),
                                         (erow, ecol))
        if ctx['no_nl_eof']:
            while (text_tgt[-2:]) == '\n\n':
                text_tgt = text_tgt[0: -1]
        else:
            while (text_tgt[-3:]) == '\n\n\n':
                text_tgt = text_tgt[0: -1]
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
        ctx['odoo_ver'] = '11.0'
    ctx['to_ver'] = ctx['odoo_ver']
    if ctx.get('from_odoo_ver', None) is None:
        ctx['from_odoo_ver'] = '7.0'
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
    parser.add_argument('-C', '--copyright',
                        action='store',
                        dest='opt_copy',
                        default='oia')
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
    parser.add_argument('-N', '--no-nl-eof',
                        action='store_true',
                        dest='no_nl_eof',
                        default=False)
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
