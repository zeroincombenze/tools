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


__version__ = "0.2.1.50"


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
        for (tokid, tokval,
             (srow, scol),
             (erow, ecol), line) in tokenize.generate_tokens(self.readline):
            self.tokenized.append([tokid, tokval,
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

    def reset_state(self, ir):
        self.SYTX_WF_ID[ir] = 0
        self.SYTX_STATE[ir] = False

    def set_suspended(self, ir):
        """Set rule state to suspended"""
        self.SYTX_WF_ID[ir] = -1 - self.SYTX_WF_ID[ir]

    def set_active(self, ir):
        """Set rule state to active"""
        self.SYTX_WF_ID[ir] = abs(self.SYTX_WF_ID[ir] + 1)
        return self.SYTX_WF_ID[ir]

    def set_next_state(self, ir):
        """Advance state to next"""
        self.SYTX_WF_ID[ir] += 1
        return self.SYTX_WF_ID[ir]

    def set_waiting_4_more(self, ir):
        """Set rule waiting for match to end token"""
        self.SYTX_WF_ID[ir] += 1
        self.SYTX_STATE[ir] = True

    def reset_waiting_4_more(self, ir):
        """Reset rule waiting for match to end token"""
        self.SYTX_STATE[ir] = False

    def cur_wf_id(self, ir):
        """Get current rule workflow position"""
        return self.SYTX_WF_ID[ir]

    def cur_valid_state(self, ir):
        """Get current active/valid rule state"""
        return abs(self.SYTX_WF_ID[ir] + 1)

    def is_active(self, ir):
        """Check for active rule"""
        if self.cur_wf_id(ir) < 0:
            return False
        keywords, tokids = self.get_key_n_id_from_rule(ir)
        if self.cur_wf_id(ir) >= len(keywords):
            return False
        return True

    def is_completed(self, ir):
        """Check for completed rule"""
        keywords, tokids = self.get_key_n_id_from_rule(ir)
        if self.cur_wf_id(ir) >= len(keywords):
            return True
        return False

    def is_waiting(self, ir):
        """Check for rule waiting for a specific token or event"""
        if isinstance(self.SYTX_STATE[ir], bool) or \
                            self.SYTX_STATE[ir] == self.any_paren + 1:
            return True
        return False

    def cur_tokid(self, ir):
        keywords, tokids = self.get_key_n_id_from_rule(ir)
        return tokids[self.cur_wf_id(ir)]

    def cur_tokval(self, ir):
        keywords, tokids = self.get_key_n_id_from_rule(ir)
        return keywords[self.cur_wf_id(ir)]

    def matches(self, ir, tokid, tokval):
        """Check if tokval matches rule token or tokid matches rule id"""
        if tokval == self.cur_tokval(ir):
            return True
        elif tokid == self.cur_tokid(ir):
            return True
        return False

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

    def readline(self):
        """Read next source line"""
        if self.lineno < len(self.lines):
            line = self.lines[self.lineno] + '\n'
            self.lineno += 1
        else:
            line = ''
        return line

    def init_rule_state(self, ir):
        if ir not in self.SYTX_WF_ID:
            self.SYTX_WF_ID[ir] = 0
        if ir not in self.SYTX_MIN_MAX:
            self.SYTX_MIN_MAX[ir] = [1, 1]
        if ir not in self.SYTX_STATE:
            self.SYTX_STATE[ir] = False

    def init_rule_prms(self, ir):
        if ir not in self.SYTX_PRMS:
            self.SYTX_PRMS[ir] = {}

    def init_rule_keyids(self, ir):
        if ir not in self.SYTX_KEYIDS:
            self.SYTX_KEYIDS[ir] = []
        for i, t in enumerate(self.SYTX_KEYWORDS[ir]):
            if i >= len(self.SYTX_KEYIDS[ir]):
                self.SYTX_KEYIDS[ir].append(tokenize.NOOP)

    def init_rule_all(self, ir):
        self.init_rule_state(ir)
        self.init_rule_prms(ir)
        self.init_rule_keyids(ir)

    def check_rule_integrity(self):
        """Check for rule integrity"""
        for ir in self.SYTX_KEYWORDS.keys():
            if ir not in self.SYTX_PRMS:
                print "Invalid rule (%s)" % (ir)

    def store_rule(self, ir, keywords, keyids, ctr):
        self.SYTX_KEYWORDS[ir] = keywords
        self.SYTX_KEYIDS[ir] = keyids
        self.SYTX_CTR = ctr

    def store_meta_subrule(self, ir, meta, keywords, keyids):
        ver = eval(meta)
        if ir in self.SYTX_KEYWORDS:
            self.init_rule_prms(ir)
            self.SYTX_PRMS[ir][ver] = keywords
        else:
            print "Invalid rule %s[%s]" % (ir, meta)

    def get_key_n_id_from_rule(self, ir):
        return self.SYTX_KEYWORDS[ir], self.SYTX_KEYIDS[ir]

    def get_prms_from_rule(self, ir, meta):
        """Get params of rule matches version <meta>"""
        prms = False
        for ver in sorted(self.SYTX_PRMS[ir], reverse=True):
            if ver <= meta:
                prms = self.SYTX_PRMS[ir][ver]
                break
        return prms

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
            # print "Unknown token %s" % value[i:]
            tokval = False
            tokid = tokenize.SUBRULE
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

    def compile_1_rule(self, ir, meta, value):
        """Compile current rule <ir> for version <meta> parsing <value>
        All rules are stored in self.SYTX_* variables
        self.SYTX_KEYWORDS -> dict of all keywords of rule
        self.SYTX_KEYIDS -> dict of all keyword ids as from tokenizer package
        self.SYTX_PRMS -> dict of params list for every version <meta>
        self.SYTX_CTR -> Min/Max repetition of every keyword/ids
                         (-1 means no limit)"""
        # pdb.set_trace()
        keywords = []
        keyids = []
        ctr = []
        ipos = 0
        if ir in self.SYTX_KEYIDS and tokenize.COMMENT in self.SYTX_KEYIDS[ir]:
            keywords.append(value)
            keyids.append(tokenize.COMMENT)
            ctr.append([1, 1])
            ipos = len(value)
        while ipos < len(value):
            unknown = True
            for istkn in self.SYNTAX:
                x = self.SYNTAX_RE[istkn].match(value[ipos:])
                if x:
                    unknown = False
                    tokid = False
                    min_max = [1,1]
                    i = ipos
                    if istkn in ('space', ):
                        ipos += x.end()
                        continue
                    elif istkn == 'escape':
                        min_max, tokid, tokval, ipos = self.parse_escape_rule(
                            value, ipos)
                        if tokid == -1:
                            ctr[-1] = min_max
                            continue
                    elif istkn == 'remark_eol':
                        tokid, tokval, ipos = self.parse_remarkeol_rule(value,
                                                                        ipos,
                                                                        x)
                    elif istkn in ('strdoc1',
                                   'strdoc2'):
                        tokid, tokval, ipos = self.parse_doc_rule(value,
                                                                  ipos)
                    elif istkn == 'string1':
                        tokid, tokval, ipos = self.parse_txt1_rule(value,
                                                                   ipos)
                    elif istkn == 'string2':
                        tokid, tokval, ipos = self.parse_txt2_rule(value,
                                                                   ipos)
                    elif istkn == 'name':
                        tokid, tokval, ipos = self.parse_generic_rule(
                            value, ipos, x, tokenize.NAME)
                    else:
                        tokid, tokval, ipos = self.parse_generic_rule(
                            value, ipos, x, tokenize.OP)
                    break
            if unknown:
                print "Unknown token %s" % value[ipos:]
                ipos += 1
            if tokid:
                keywords.append(tokval)
                keyids.append(tokid)
                ctr.append(min_max)
        # match rule against version
        if meta and self.SYNTAX_RE['int'].match(meta):
            self.store_meta_subrule(ir, meta, keywords, keyids)
        else:
            self.store_rule(ir, keywords, keyids, ctr)
        self.init_rule_all(ir)

    def extr_tokens_from_line(self, rule, meta, value, cont_break):
        """Extract from line rule elements"""
        if rule and rule[-1] == '\n':
            rule = rule[0: -1]
        id = False
        # meta = False
        if not rule:
            pass
        elif rule[0] == '#':
            pass
        elif cont_break:
            value += rule
        else:
            cont_break = False
            i = rule.find(':')
            if i < 0:
                value += rule
            else:
                left = rule[0:i].strip()
                value = rule[i + 1:].lstrip()
                i = left.find('[')
                if i < 0:
                    meta = False
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
        return id, meta, value, cont_break

    def read_rules_from_file(self, rule_file, ctx):
        # pdb.set_trace()
        try:
            fd = open(rule_file, 'r')
            value = ''
            cont_break = False
            meta = ''
            for rule in fd:
                id, meta, value, cont_break = self.extr_tokens_from_line(
                    rule, meta, value, cont_break)
                if not id or cont_break:
                    continue
                self.compile_1_rule(id, meta, value)
            fd.close()
            self.check_rule_integrity()
        except:
            pass

    def set_rulefn(self, rule_file):
        if rule_file.endswith('.py'):
            rule_file = rule_file[0:-3] + '.2p8'
        else:
            rule_file += '.2p8'
        return rule_file

    def compile_rules(self, ctx):
        self.SYTX_KEYWORDS = {}
        self.SYTX_KEYIDS = {}
        self.SYTX_PRMS = {}
        self.SYTX_CTR = {}
        self.SYTX_WF_ID = {}
        self.SYTX_STATE = {}
        self.SYTX_MIN_MAX = {}
        self.rule_re_matches = {}
        self.rule_re_replaces = {}
        self.re_matches = {}
        self.re_replaces = {}
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
        for ir1 in self.SYTX_KEYWORDS.keys():
            if ir1 == ir:
                continue
            keywords, tokids = self.get_key_n_id_from_rule(ir)
            if self.cur_valid_state(ir) >= len(tokids):
                continue
            if tokids[self.set_active(ir)] == tokenize.SUBRULE and \
                    keywords[self.set_active(ir)] == ir:
                set_suspended(ir)
                if result:
                    self.SYTX_WF_ID[ir] += 1
                else:
                    self.SYTX_WF_ID[ir] = 0
                self.match_parent_rule(ir1, result)

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
            if srow != self.last_row:
                self.tabstop = {}
                self.last_row = srow
        else:
            self.start = (srow, scol)
            self.stop = (erow, ecol)
        tokid = self.wash_tokid(tokid, tokval)
        if tokid != tokenize.COMMENT:
            self.file_header = False
            self.blk_header = False
        self.tabstop[scol] = tokenize.tok_name[tokid]
        return tokid, tokval

    def replace_token(self, ir, tokid, tokval, re_matches, re_replaces):
        # pdb.set_trace()
        if tokid == tokenize.COMMENT:
            for tok in re_matches:
                if tokval.find(tok) >= 0:
                    tokval.replace(re_matches, re_replaces)
        elif re_matches and tokval in re_matches:
            ix = re_matches.index(tokval)
            if ir not in self.rule_re_replaces:
                self.rule_re_matches[ir] = {}
                self.rule_re_replaces[ir] = {}
            self.rule_re_matches[ir][tokeno] = re_matches[ix]
            self.rule_re_replaces[ir][tokeno] = re_replaces[ix]

    def tokenize_source(self, ctx=None):
        # pdb.set_trace()
        ctx = ctx or {}
        for tokeno, (tokid, tokval,
                     (srow, scol),
                     (erow, ecol)) in enumerate(self.tokenized):
            tokid = self.wash_tokid(tokid, tokval)
            if tokid == tokenize.NOOP:
                continue
            if ctx['opt_dbg']:
                print ">>> %s(%s)" % (tokval, tokid)
            completed_rules = []
            reset_rules = []
            for ir in self.SYTX_KEYWORDS.keys():
                keywords, tokids = self.get_key_n_id_from_rule(ir)
                re_matches = self.get_prms_from_rule(ir, ctx['from_ver'])
                re_replaces = self.get_prms_from_rule(ir, ctx['to_ver'])
                # rule parse ended
                if not self.is_active(ir):
                    pass
                # rule child of parent rule: wait for parent result
                elif self.cur_tokid(ir) == tokenize.SUBRULE:
                    self.set_suspended(ir)
                # found any token rule
                elif self.cur_tokid(ir) == tokenize.ANY:
                    self.set_next_state(ir)
                # replace string inside remark
                elif self.cur_tokid(ir) == tokenize.COMMENT:
                    self.replace_token(ir, tokid, tokval,
                                       re_matches, re_replaces)
                # found zero, one or more tokens rule
                elif self.cur_tokid(ir) == tokenize.MORE:
                    self.set_waiting_4_more(ir)
                    continue
                # found expression rule
                elif self.cur_tokid(ir) == tokenize.EXPR:
                    self.set_waiting_4_more(ir)
                    continue
                # exact text match
                elif self.matches(ir, tokid, tokval):
                    if self.is_waiting(ir):
                        self.reset_waiting_4_more(ir)
                    self.set_next_state(ir)
                # waiting for zero, one or more tokens
                elif self.is_waiting(ir):
                    continue
                if self.is_completed(ir):
                    completed_rules.append(ir)
            for ir in self.SYTX_KEYWORDS.keys():
                # rule finally matches
                if ir in completed_rules:
                    if ctx['opt_dbg']:
                        print "    match_parent_rule(%s, True)" % (ir)
                    self.match_parent_rule(ir, True)
                    # replace src text by re_replaces
                    for i in self.rule_re_replaces[ir]:
                        self.re_matches[i] = self.rule_re_matches[ir][i]
                        self.re_replaces[i] = self.rule_re_replaces[ir][i]
                    self.rule_re_matches[ir] = {}
                    self.rule_re_replaces[ir] = {}
                    self.SYTX_WF_ID[ir] = 0
                # rule does not match
                elif ir in reset_rules:
                    if ctx['opt_dbg']:
                        print "    match_parent_rule(%s, False)" % (ir)
                    self.match_parent_rule(ir, False)
                    self.rule_re_matches[ir] = {}
                    self.rule_re_replaces[ir] = {}
                elif ctx['opt_dbg']:
                    print "    match_rule(%s, evaluating)" % (ir)
            # yield tokid, tokval

    def apply_for_rules(self, ctx=None):
        ctx = ctx or {}
        self.tokenize_source(ctx=ctx)
        for tokeno in self.re_replaces:
            self.tokenized[tokeno][1] = self.re_replaces[tokeno]
        self.init_parse()

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
    # pdb.set_trace()
    ctx = ctx or {}
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
