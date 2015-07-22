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
"""
    python parser and tokenizer

"""
# import pdb
import re


__version__ = "0.1.17"


class Pytok():

    def __init__(self):
        self.prm = {}
        self.prm['inclass_op'] = []
        self.prm['inclass'] = True
        self.prm['infun_op'] = []
        self.prm['infun'] = True
        self.prm['tokens'] = True
        self.prm['model'] = False
        self.prm['no_num_line'] = False
        self.prm['no_inherit'] = False
        self.prm['gap'] = 3

    def switch_2_parent(self):
        self._close_remark()
        self._close_decorator()
        if 'r_parent_class' in self.prm:
            self.decl_classes_2_search(self.prm['r_parent_class'])
        self.prm['r_range'] = []
        self.prm['r_parent_class'] = []

    @staticmethod
    def line_decorator(line):
        """Return true if python line is decorator"""
        if re.match('^ *@', line):
            return True
        else:
            return False

    @staticmethod
    def line_remark(line):
        """Return true if python line is only remark or empty line"""
        if line.strip() == '' or re.match('^ *#', line):
            return True
        else:
            return False

    @staticmethod
    def line_fun_def(line):
        """Return true if python line is function def"""
        if re.match('^ *def .*:', line):
            lev = int(line.find('def') / 4) + 1
            return lev
        else:
            return False

    @staticmethod
    def line_class_def(line):
        """Return true if python line is class def"""
        if re.match('^ *class .*:', line):
            return True
        else:
            return False

    @staticmethod
    def line_end_class(line, classname):
        """Return true if python line is end class"""
        if classname:
            tok = '^' + classname + ' *()'
            if re.match(tok, line):
                return True
        return False

    @staticmethod
    def strip_comment(line):
        """Remove comments from source line"""
        i = line.rfind('#')
        if i >= 0:
            line = line[:i].strip()
        return line

    @staticmethod
    def line_wout_key(line, keyword):
        """Return line without initial keyword and all remarks"""
        i = line.find(keyword)
        if i >= 0:
            l = len(keyword)
            line = line[i + l:].strip()
        line = Pytok.strip_comment(line)
        if line[-1] == ':':
            line = line[:-1].strip()
        return line

    @staticmethod
    def decorator_name(line):
        """Return decoratore name(s) if decorator line"""
        i = line.find('@')
        if i >= 0:
            name = line[i + 1:].strip()
            line = Pytok.strip_comment(name)
            return name
        return None

    @staticmethod
    def get_name_n_params(name, deflt=None):
        """Extract name and params from string like 'name(params)'"""
        deflt = '' if deflt is None else deflt
        i = name.find('(')
        j = name.rfind(')')
        if i >= 0 and j >= i:
            n = name[:i].strip()
            p = name[i + 1:j].strip()
        else:
            n = name
            p = deflt
        return n, p

    @staticmethod
    def get_name_n_ix(name, deflt=None):
        """Extract name and subscription from string like 'name[ix]'"""
        deflt = '' if deflt is None else deflt
        i = name.find('[')
        j = name.rfind(']')
        if i >= 0 and j >= i:
            n = name[:i].strip()
            x = name[i + 1:j].strip()
        else:
            n = name
            x = deflt
        return n, x

    def _open_decorator(self, name):
        if not self.prm.get('decorator_line', False):
            self.prm['decorator_names'] = []
            self.prm['decorator_line'] = self.prm['line']
        self.prm['decorator_names'].append(name)

    def _close_decorator(self):
        self.prm['decorator_line'] = False
        self.prm['decorator_names'] = []

    def _open_remark(self):
        if not self.prm.get('rem_line', False):
            self.prm['rem_line'] = self.prm['line']

    def _close_remark(self):
        self.prm['rem_line'] = False

    def _get_start_line(self):
        numline = self.prm['line']
        if self.prm.get('rem_line', False):
            numline = min(numline, self.prm['rem_line'])
        if self.prm.get('decorator_line', False):
            numline = min(numline, self.prm['decorator_line'])
        return numline

    def _open_fun(self, fun_name, params, level):
        if params[0:4] == 'self':
            is_public = True
        elif 'staticmethod' in self.prm['decorator_names']:
            is_public = True
        elif 'classmethod' in self.prm['decorator_names']:
            is_public = True
        else:
            is_public = False
        max_funlev = self.prm.get('max_funlev', 0)
        full_fun_name = ''
        lev = 2
        while lev < level:
            clev_fun = 'cur_fun' + str(lev)
            full_fun_name += self.prm[clev_fun] + '.'
            lev += 1
        if level > max_funlev:
            self.prm['max_funlev'] = level
        full_fun_name += fun_name
        clev_fun = 'cur_fun' + str(level)
        if self.prm['cur_class'] and is_public:
            self.prm[clev_fun] = self.prm['cur_class'] + '.' + full_fun_name
        else:
            self.prm[clev_fun] = full_fun_name
        pub_fun = 'fun_pub' + str(level)
        if level == 1:
            self.prm[pub_fun] = True
        else:
            self.prm[pub_fun] = is_public
        cline_fun = 'fun_line' + str(level)
        self.prm[cline_fun] = self._get_start_line()
        if level > 1 and is_public:
            self.prm['fun_pub1'] = True
            self.prm['fun_line1'] = self.prm[cline_fun]
            self.prm['cur_fun1'] = self.prm['cur_class'] + '.' + full_fun_name

    def _close_fun(self, level):
        if level == 0:
            max_funlev = self.prm.get('max_funlev', 0)
            for lev in range(max_funlev):
                self._close_fun(lev + 1)
            self.prm['max_funlev'] = 0
            return
        clev_fun = 'cur_fun' + str(level)
        cline_fun = 'fun_line' + str(level)
        if level == 1:
            pub_fun = True
        else:
            pub_fun = 'fun_pub' + str(level)
            pub_fun = self.prm.get(pub_fun, False)
        if clev_fun in self.prm:
            nline_start = self.prm[cline_fun]
            nline_stop = self._get_start_line()
            nline_stop -= 1
            fun_name = self.prm[clev_fun]
            if not self.prm.get('t_range', False):
                self.prm['sym_fun'][fun_name] = [nline_start, nline_stop]
            self.prm['sym_pub'][fun_name] = pub_fun
        self.prm[clev_fun] = ""
        self.prm[cline_fun] = 0

    def _init_class(self):
        self.prm['cur_class'] = ""
        self.prm['parent_class'] = []
        self.prm['class_line'] = 0
        self.prm['found_model'] = False
        self._close_fun(0)

    def _open_class(self, class_name, params):
        if not params:
            self.prm['parent_class'] = []
        else:
            self.prm['parent_class'] = map(lambda x: x.strip() + '()',
                                           params.split(','))
        self.prm['cur_class'] = class_name
        self.prm['class_line'] = self._get_start_line()

    def _close_class(self, is_stmnt):
        self._close_fun(0)
        if self.prm['cur_class']:
            nline_start = self.prm['class_line']
            nline_stop = self.prm['line']
            # Auto close prior class: end line is previous
            if not is_stmnt:
                if self.prm.get('rem_line', False):
                    nline_stop = min(nline_stop, self.prm['rem_line'])
                elif self.prm.get('decorator_line', False):
                    nline_stop = min(nline_stop, self.prm['decorator_line'])
                nline_stop -= 1
            class_name = self.prm['cur_class']
            if not self.prm.get('t_range', False):
                self.prm['sym_class'][class_name] = [nline_start, nline_stop]

    def _close_super_class(self, close_class):
        if close_class:
            self._close_class(False)
        if self.prm['model'] and not self.prm.get('t_range', False):
            if self.prm['found_model']:
                self._add_parent_range()
        elif self.isinclass():
            self._add_parent_range()

    def op_comp(self, left, op, right):
        if op == '*':
            if re.match(left, right):
                return True
            return False
        elif op == '=':
            if left == right:
                return True
            return False
        elif op == '(' or op == ':':
            left = left + op
            if re.match(left, right):
                return True
            return False
        else:
            return False

    def isinfun(self):
        clev_fun = 'cur_fun' + str(1)
        if isinstance(self.prm['infun'], bool):
            return self.prm['infun']
        elif clev_fun not in self.prm:
            return False
        elif isinstance(self.prm['infun'], list):
            for i, v in enumerate(self.prm['infun']):
                if self.op_comp(v,
                                self.prm['infun_op'][i],
                                self.extr_fun_name(self.prm[clev_fun])):
                    return True
        else:
            if self.op_comp(self.prm['infun'],
                            self.prm['infun_op'],
                            self.extr_fun_name(self.prm[clev_fun])):
                return True
        return False

    def isinclass(self):
        if isinstance(self.prm['inclass'], bool):
            return self.prm['inclass']
        elif isinstance(self.prm['inclass'], list):
            for i, v in enumerate(self.prm['inclass']):
                if self.op_comp(v,
                                self.prm['inclass_op'][i],
                                self.prm['cur_class']):
                    return True
                if not self.prm['no_inherit']:
                    for name in self.prm['parent_class']:
                        class_name, params = self.get_name_n_params(name, None)
                        if self.op_comp(v,
                                        self.prm['inclass_op'][i],
                                        class_name):
                            return True
        else:
            if self.op_comp(self.prm['inclass'],
                            self.prm['inclass_op'],
                            self.prm['cur_class']):
                return True
            if not self.prm['no_inherit']:
                for name in self.prm['parent_class']:
                    class_name, params = self.get_name_n_params(name, None)
                    if self.op_comp(self.prm['inclass'],
                                    self.prm['inclass_op'],
                                    class_name):
                        return True
        return False

    def isvalidline(self, type):
        if self.isinclass():
            if type == 'class' or type == 'end' or self.isinfun():
                return True
        return False

    def found_model(self, line):
        token = self.prm.get('model', False)
        if token:
            if isinstance(token, list):
                for t in token:
                    if re.match(t, line):
                        return True
            else:
                if re.match(token, line):
                    return True
        return False

    def extr_fun_name(self, f):
        i = f.find('.')
        if i < 0:
            return f
        else:
            return f.split('.')[1]

    def hdr_fn(self, name):
        if name is None:
            name = self.prm['cur_file']
        x = "====" + self.prm['cur_file'] + "===="
        return x

    def hdr_class(self, name):
        if name is None:
            name = self.prm['cur_class']
        x = "class " + name + "():"
        return x

    def hdr_fun(self, name):
        if name is None:
            name = self.prm['cur_fun']
        x = "    def " + self.extr_fun_name(name) + "():"
        return x

    def out_line(self, output, *args):
        """Output results"""
        txt = ''
        for arg in args:
            try:
                if isinstance(arg, unicode):
                    txt = txt + arg.encode('utf-8')
                elif isinstance(arg, str):
                    txt = txt + arg
                else:
                    txt = txt + str(arg).encode('utf-8')
            except:
                x = unichr(0x3b1) + unichr(0x3b2) + unichr(0x3b3)
                txt = txt + x.encode('utf-8')
        class_name, c, fun_name, f = self._set_names()
        if self.prm['cur_file'] and self.prm['line'] == 1:
            x = self.hdr_fn(None)
            self.formatted_out(output, x, False)
        if class_name and\
                class_name != self.prm['cur_class'] and\
                not c:
            x = self.hdr_class(class_name)
            self.formatted_out(output, x, False)
        self.prm['cur_class'] = class_name
        if fun_name and\
                fun_name != self.prm['cur_fun'] and\
                not f:
            x = self.hdr_fun(fun_name)
            self.formatted_out(output, x, False)
        self.prm['cur_fun'] = fun_name
        self.formatted_out(output, txt, True)

    def formatted_out(self, output, txt, f):
        if not self.prm.get('no_num_line', False):
            if f:
                txt = "{0:>4} {1}".format(self.prm['line'], txt)
            else:
                txt = "{0:>4} {1}".format('', txt)
        if output:
            output(txt)
        else:
            txt = txt + '\n'
            self.prm['tostring'] += txt

    def _set_names(self):
        numline = self.prm['line']
        c = False
        found = False
        for class_name in self.prm['sym_class']:
            start = self.prm['sym_class'][class_name][0]
            stop = self.prm['sym_class'][class_name][1]
            if numline >= start and numline <= stop:
                found = True
                if numline == start:
                    c = True
                break
        if not found:
            class_name = ''
        f = False
        found = False
        for fun_name in self.prm['sym_fun']:
            if fun_name:
                start = self.prm['sym_fun'][fun_name][0]
                stop = self.prm['sym_fun'][fun_name][1]
                if numline >= start and numline <= stop:
                    found = True
                    if numline == start:
                        f = True
                    break
        if not found:
            fun_name = ''
        return class_name, c, fun_name, f

    def _add_parent_range(self, parent_class=None):
        if 'r_parent_class' not in self.prm:
            self.prm['r_parent_class'] = []
        if parent_class is None:
            parent_class = self.prm['parent_class']
        else:
            parent_class = parent_class.split(',')
        for name in parent_class:
            class_name, params = self.get_name_n_params(name, None)
            if class_name in self.prm['sym_class'] and \
                    isinstance(self.prm['sym_class'][class_name], list):
                self.prm['r_parent_class'].append(name)
                nline_start = self.prm['sym_class'][class_name][0]
                nline_stop = self.prm['sym_class'][class_name][1]
                self.add_line_range(nline_start, nline_stop, 'r_range')

    def _get_ix_range(self, ix, range_id):
        last_range = self.prm[range_id][ix]
        if isinstance(last_range, list):
            range_start = last_range[0]
            range_stop = last_range[1]
        else:
            range_start = last_range
            range_stop = last_range
        return range_start, range_stop

    def _search_ix(self, nline_start, nline_stop=None, range_id=None):
        """Return index which intersect lines or index position to insert
        if return -1 means append"""
        range_id = 'range' if range_id is None else range_id
        nline_stop = nline_start if nline_stop is None else nline_stop
        found = False
        ix = len(self.prm[range_id]) - 1
        while ix >= -1 and not found:
            if ix < 0:
                range_start = 0
                range_stop = 0
            else:
                range_start, range_stop = self._get_ix_range(ix, range_id)
            if nline_start in range(range_start, range_stop + 1) or\
                    nline_stop in range(range_start, range_stop + 1):
                found = True
                break
            elif nline_start > range_stop:
                ix += 1
                if ix >= len(self.prm[range_id]):
                    ix = -1
                break
            ix -= 1
        return found, ix, range_start, range_stop

    def add_line_range(self, nline_start=None, nline_stop=None,
                       range_id=None):
        range_id = 'range' if range_id is None else range_id
        nline_start = self.prm['line'] if nline_start is None else nline_start
        nline_stop = nline_start if nline_stop is None else nline_stop
        isrange = (nline_start != nline_stop)
        if range_id not in self.prm:
            self.prm[range_id] = []
        found, ix, range_start, range_stop = self._search_ix(nline_start,
                                                             nline_stop,
                                                             range_id)
        if not found and nline_start <= (range_stop + self.prm['gap']):
            if ix < 0:
                ix = len(self.prm[range_id]) - 1
                found = True
            elif ix > 0:
                ix -= 1
                found = True
            nline_start = range_stop
            if nline_start == 0:
                nline_start = 1
            isrange = (nline_start != nline_stop)
        if not isrange:
            if ix < 0:
                self.prm[range_id].append(nline_start)
            elif not found:
                self.prm[range_id].insert(ix, nline_start)
        else:
            if ix < 0:
                self.prm[range_id].append([nline_start, nline_stop])
            elif found:
                while found:
                    del self.prm[range_id][ix]
                    nline_start = min(nline_start, range_start)
                    nline_stop = max(nline_stop, range_stop)
                    found = False
                    if ix > 0:
                        range_start, range_stop = self._get_ix_range(ix - 1,
                                                                     range_id)
                        if nline_start <= range_stop:
                            ix -= 1
                            found = True
                self.prm[range_id].insert(ix, [nline_start, nline_stop])
            else:
                self.prm[range_id].insert(ix, [nline_start, nline_stop])

    def add_tok_range(self):
        nline_stop = self.prm['line']
        nline_start = self._get_start_line()
        self.add_line_range(nline_start, nline_stop)

    def search_tok(self, line):
        if isinstance(self.prm['tokens'], bool):
            if self.prm['tokens']:
                self.add_tok_range()
        elif isinstance(self.prm['tokens'], list):
            for i, v in enumerate(self.prm['tokens']):
                if self.op_comp(v,
                                self.prm['tokens_op'][i],
                                line):
                    self.add_tok_range()
        else:
            if self.op_comp(self.prm['tokens'],
                            self.prm['tokens_op'],
                            line):
                self.add_tok_range()

    def parse_line_type(self, line, type):
        if self.isvalidline(type):
            if type == 'class':
                if not self.prm['model']:
                    self.search_tok(line)
                elif self.prm.get('t_range', False):
                    self.search_tok(line)
            elif type == 'end':
                if self.prm['model'] and not self.prm.get('t_range', False):
                    if self.prm['found_model']:
                        self._add_parent_range(self.prm['cur_class'])
                self._add_parent_range()
                self.search_tok(line)
            else:
                if self.prm['model'] and not self.prm.get('t_range', False):
                    if self.found_model(line):
                        self.prm['found_model'] = True
                else:
                    self.search_tok(line)
        self._close_remark()
        self._close_decorator()

    def parse_line(self, numline):
        self.prm['line'] = numline
        line = self.src_txt[numline - 1]
        if self.line_remark(line):
            self._open_remark()
        elif self.line_decorator(line):
            name = self.decorator_name(line)
            self._open_decorator(name)
        elif self.line_class_def(line):
            self._close_class(False)
            tok = 'class'
            ln = self.line_wout_key(line, tok)
            class_name, params = self.get_name_n_params(ln, None)
            self._open_class(class_name, params)
            self.parse_line_type(line, tok)
        elif self.line_end_class(line, self.prm['cur_class']):
            self._close_class(True)
            self.parse_line_type(line, 'end')
            self._init_class()
        elif self.line_fun_def(line):
            lev = self.line_fun_def(line)
            if lev == 1:
                self._close_super_class(True)
                self._init_class()
            else:
                self._close_fun(lev)
            tok = 'def'
            ln = self.line_wout_key(line, tok)
            fun_name, params = self.get_name_n_params(ln, None)
            self._open_fun(fun_name, params, lev)
            self.parse_line_type(line, tok)
        else:
            self.parse_line_type(line, '')

    def parse_src(self):
        """Parse source to search token(s) in instance"""
        self._init_class()
        self.prm['line'] = 0
        self.prm['sym_class'] = {}
        self.prm['sym_fun'] = {}
        self.prm['sym_pub'] = {}
        for ix in range(len(self.src_txt)):
            numline = ix + 1
            self.parse_line(numline)
        self._close_super_class(True)
        if 'r_range' in self.prm:
            self.prm['t_range'] = self.prm['r_range']
            self.switch_2_parent()
            for ix in self.prm['t_range']:
                if isinstance(ix, list):
                    range_start = ix[0]
                    range_stop = ix[1] + 1
                    for numline in range(range_start, range_stop):
                        self.prm['line'] = numline
                        self.parse_line(numline)
                else:
                    self.prm['line'] = ix
                    self.parse_line(numline)
            self._close_super_class(True)

    def get_range(self):
        if 'range' not in self.prm:
            return []
        return self.prm['range']

    def decl_options(self, output=None, no_num_line=None):
        if output:
            self.prm['output'] = output
        if no_num_line:
            self.prm['no_num_line'] = no_num_line

    def decl_classes_2_search(self, classes):
        """Declare class(es) in instance (comma separated)
        where tokens have to be searched
        """
        self.prm['inclass_op'] = []
        self.prm['inclass'] = []
        if isinstance(classes, list):
            for x in classes:
                i = x.rfind('(')
                if i >= 0:
                    self.prm['inclass'].append(x[:i])
                    self.prm['inclass_op'].append('=')
                else:
                    self.prm['inclass'].append(x)
                    self.prm['inclass_op'].append('*')
        else:
            for x in classes.split(','):
                i = x.rfind('(')
                if i >= 0:
                    self.prm['inclass'].append(x[:i])
                    self.prm['inclass_op'].append('=')
                else:
                    self.prm['inclass'].append(x)
                    self.prm['inclass_op'].append('*')

    def decl_funs_2_search(self, funs):
        """Declare function(s) in instance (comma separated)
        where tokens have to be searched
        """
        self.prm['infun_op'] = []
        self.prm['infun'] = []
        for x in funs.split(','):
            i = x.rfind('(')
            if i >= 0:
                self.prm['infun'].append(x[:i])
                self.prm['infun_op'].append('=')
            else:
                self.prm['infun'].append(x)
                self.prm['infun_op'].append('*')

    def decl_tokens_2_search(self, tokens):
        """Declare token(s) to search in instance (comma separated)"""
        self.prm['tokens_op'] = []
        self.prm['tokens'] = []
        for x in tokens.split(','):
            if x != '.*':
                x = '.*' + x + '.*'
            i = x.rfind('(')
            if i >= 0:
                self.prm['tokens'].append(x[:i])
                self.prm['tokens_op'].append('(')
            else:
                self.prm['tokens'].append(x)
                self.prm['tokens_op'].append('*')

    def decl_model_2_search(self, tokens):
        """Declare model(s) in which search(comma separated)"""
        self.prm['model'] = []
        for x in tokens.split(','):
            self.prm['model'].append("^ *_inherit *= *['\"]" + x + "['\"]")
            self.prm['model'].append("^ *_name *= *['\"]" + x + "['\"]")

    def tostring(self, output=None):
        """Output program as string source"""
        self.prm['hdrn'] = False
        self.prm['hdrc'] = False
        self.prm['hdrf'] = False
        self.prm['cur_fun'] = ''
        self.prm['cur_class'] = ''
        if output is None:
            output = self.prm.get('output', None)
        elif self.prm['output'] is None:
            self.prm['output'] = output
        self.prm['tostring'] = ''
        self._init_class()
        if 'range' in self.prm:
            for ix in self.prm['range']:
                if isinstance(ix, list):
                    range_start = ix[0]
                    range_stop = ix[1] + 1
                    for numline in range(range_start, range_stop):
                        line = self.src_txt[numline - 1]
                        self.prm['line'] = numline
                        self.out_line(output, line)
                else:
                    line = self.src_txt[ix - 1]
                    self.prm['line'] = ix
                    self.out_line(output, line)
        return self.prm['tostring']

    @staticmethod
    def open(self, file):
        """New instance of Pytok from python source file"""
        p = Pytok()
        return p._open(file)

    def _open(self, file):
        fd = open(file, 'rb')
        self.src_txt = fd.read().split('\n')
        fd.close()
        self.prm['cur_file'] = file
        return self

    @staticmethod
    def new(text=None):
        """New instance of Pytok from text string"""
        p = Pytok()
        return p._new(text)

    def _new(self, text=None):
        if text is None:
            self.src_txt = []
        elif not isinstance(text, list):
            self.src_txt = text.split('\n')
        self.prm['cur_file'] = ''
        return self

Pytok()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
