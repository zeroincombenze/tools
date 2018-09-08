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


__version__ = "0.1.0"


def parse_file(ctx):
    src_file = ctx['src_file']
    if ctx['opt_compact']:
        source = compact_file(ctx)
    else:
        fd = open(src_file, 'rb')
        source = fd.read()
        fd.close()
    SYNTAX = {
        '_1_OPENPARAM': re.compile(r'\{\{\{'),
        '_1_CLOSEPARAM': re.compile(r'\}\}\}'),
        '_2_OPENMACRO': re.compile(r'\{\{'),
        '_2_CLOSEMACRO': re.compile(r'\}\}'),
        '_2_OPENTABLE': re.compile(r'\{\|'),
        '_2_CLOSETABLE': re.compile(r'\|\}'),
        '_2_OPENLINK': re.compile(r'\[\['),
        '_2_CLOSELINK': re.compile(r'\]\]'),
        '_5_BAR': re.compile(r'\|'),
        '_9_OPEND': re.compile(r'\{'),
        '_9_CLOSED': re.compile(r'\}'),
        '__OTHER': re.compile(r'[^{|}\[\]]+')
    }
    ipos = 0
    level_macro = 0
    level_link = 0
    level_table = 0
    in_param = False
    stack = []
    tbl_stack = []
    target = ''
    # pdb.set_trace()
    while ipos < len(source):
        unknown = True
        level_stack = len(stack)
        if level_stack > 0:
            last_toktype = stack[level_stack - 1]
        else:
            last_toktype = ''
        for istkn in sorted(SYNTAX):
            open_token = istkn.replace('CLOSE', 'OPEN')
            if istkn in ('_1_CLOSEPARAM',
                         '_2_CLOSEMACRO',
                         '_2_CLOSETABLE',
                         '_2_CLOSELINK',
                         '_9_CLOSED') and last_toktype != open_token:
                continue
            x = SYNTAX[istkn].match(source[ipos:])
            if x:
                unknown = False
                i = ipos
                ipos += x.end()
                # print "(%s)->[%s]" % (istkn, source[i:ipos])
                if len(target) and target[-1] != '\n':
                    line_break = True
                else:
                    line_break = False
                lm = ' ' * (level_macro * 2)
                if istkn == '_1_OPENPARAM':
                    in_param = True
                    target += source[i:ipos]
                    stack.append(istkn)
                elif istkn == '_1_CLOSEPARAM':
                    in_param = False
                    if level_stack > 0:
                        del stack[level_stack - 1]
                    elif not ctx['opt_compact']:
                        target += '\n'
                    target += source[i:ipos]
                elif istkn == '_2_OPENMACRO':
                    if level_table:
                        lm = ''
                    elif line_break:
                        lm = '\n' + lm
                    if ctx['opt_compact']:
                        target += source[i:ipos]
                    else:
                        target += lm + source[i:ipos]
                    level_macro += 1
                    stack.append(istkn)
                elif istkn == '_2_CLOSEMACRO':
                    if level_stack > 0:
                        del stack[level_stack - 1]
                    elif not ctx['opt_compact']:
                        target += '\n'
                    if level_macro > 0:
                        level_macro -= 1
                        if level_table:
                            lm = ''
                        else:
                            lm = ' ' * (level_macro * 2)
                        if target[-1] == '\n':
                            target = target[0:-1].rstrip()
                    else:
                        lm = '<!--\n-->'
                        if line_break:
                            lm = '\n' + lm
                    if line_break:
                        target += source[i:ipos]
                    elif ctx['opt_compact']:
                        target += source[i:ipos]
                    else:
                        target += lm + source[i:ipos]
                elif istkn == '_2_OPENTABLE':
                    stack.append(istkn)
                    if line_break:
                        target += '\n'
                    target += source[i:ipos]
                    level_table += 1
                    tbl_stack.append(level_macro)
                elif istkn == '_2_CLOSETABLE':
                    if level_stack > 0:
                        del stack[level_stack - 1]
                    else:
                        target += '\n'
                    if level_table > 0:
                        level_table -= 1
                        if line_break:
                            target += '\n'
                        del tbl_stack[level_table]
                    else:
                        target += '\n'
                    target += source[i:ipos]
                elif istkn == '_2_OPENLINK':
                    level_link += 1
                    stack.append(istkn)
                    if not line_break and not ctx['opt_compact']:
                        target += lm + source[i:ipos]
                    elif target[-1] == '\n' and source[i] == '\n':
                        target += source[i + 1:ipos]
                    else:
                        target += source[i:ipos]
                elif istkn == '_2_CLOSELINK':
                    if level_stack > 0:
                        del stack[level_stack - 1]
                    else:
                        target += '\n'
                    if level_link > 0:
                        level_link -= 1
                    elif not ctx['opt_compact']:
                        target += '\n'
                    target += source[i:ipos]
                elif istkn == '_9_OPEND':
                    stack.append(istkn)
                    target += source[i:ipos]
                elif istkn == '_9_CLOSED':
                    if level_stack > 0:
                        del stack[level_stack - 1]
                    else:
                        target += '\n'
                    target += source[i:ipos]
                elif istkn == '_5_BAR':
                    if in_param or level_link:
                        if target[-1] == '\n':
                            target = target[0:-1].rstrip()
                    elif level_table:
                        if line_break and \
                                tbl_stack[level_table - 1] == level_macro:
                            target += '\n'
                    target += source[i:ipos]
                else:
                    if len(target) and target[-1] == '|':
                        target += source[i:ipos]
                    elif not line_break and not ctx['opt_compact']:
                        target += lm + source[i:ipos]
                    elif target[-1] == '\n' and source[i] == '\n':
                        target += source[i + 1:ipos]
                    else:
                        target += source[i:ipos]
                break
        if unknown:
            target += "\n<!-- Unknown token --> %s" % source[ipos]
            ipos += 1
    print target


def compact_file(ctx):
    src_file = ctx['src_file']
    fd = open(src_file, 'rb')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    target = ''
    for line in lines:
        target += line.strip()
    return target


if __name__ == "__main__":
    parser = parseoptargs("Parse_wiki",
                          "© 2017 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-C', '--compact',
                        action='store_true',
                        dest='opt_compact',
                        default=False)
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    # if ctx['opt_compact']:
    #     compact_file(ctx)
    # else:
    parse_file(ctx)
