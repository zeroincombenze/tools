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


__version__ = "0.1.12"


def update_to_8(line):
    line = line.rstrip()
    if re.match("^from osv import", line):
        line = line.replace("from osv import",
                            "from openerp.osv import")
    if re.match("^import decimal_precision", line):
        line = line.replace("import decimal_precision",
                            "import openerp.addons.decimal_precision")
    if re.match("^from tools.translate import", line):
        line = line.replace("from tools.translate import",
                            "from openerp.tools.translate import")
    if re.match("^import netsvc", line):
        line = line.replace("import netsvc",
                            "from openerp import netsvc")
    if re.match("^import pooler", line):
        line = line.replace("import pooler",
                            "from openerp import pooler")
    return line


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


def exec_W503(filepy):
    fd = open(filepy, 'r')
    source = fd.read()
    fd.close()
    lines = source.split('\n')
    n = len(lines) - 1
    while n > 2 and lines[n] == "" and lines[n - 1] == "":
        del lines[n]
        n = len(lines) - 1
    empty_line = 0
    for n in range(len(lines)):
        if lines[n] == "":
            empty_line += 1
        else:
            empty_line = 0
            if re.match("^report_sxw.report_sxw", lines[n]):
                if empty_line == 1:
                    line.insert(n,'')
                elif empty_line > 2:
                    del line[n - 1]
                    n -= 1
            elif re.match("^[a-zA-Z0-9_]+\(\)", lines[n]):
                if empty_line == 1:
                    line.insert(n,'')
                elif empty_line > 2:
                    del line[n - 1]
                    n -= 1
            lines[n] = update_to_8(lines[n])
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
    fd = open(filepy, 'w')
    for n in range(len(lines)):
        if n == len(lines) - 1:
            ln = lines[n]
        else:
            ln = lines[n] + "\n"
        fd.write(ln)
    fd.close()
    return 0


if __name__ == "__main__":
    filepy = sys.argv[1]
    sts = exec_W503(filepy)
    sys.exit(sts)
