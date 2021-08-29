#!/home/odoo/devel/venv/bin/python2
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
"""Parse and manage text source files
"""

import pdb
# import os
import sys
import re
from z0lib import parseoptargs


__version__ = "0.0.1"


class Builder():

    def __init__(self, template=None):
        if template == 'markdown':
            self.template = template
            self.SYNTAX = ['space',
                           'h1',
                           'h2',
                            ]
            self.SYNTAX_RE = {
                'space': re.compile(r'\s+'),
                'h1': re.compile(r'^=+'),
                'h2': re.compile(r'^=-'),
            }

    def parse_file(self, src_fn):
        fd = open(src_fn, 'rb')
        source = fd.read()
        fd.close()
        self.lines = source.split('\n')
        lineno = 0
        while lineno < len(lines):
            unknown = True
            ipos = 0
            for istkn in self.SYNTAX:
                x = self.SYNTAX_RE[istkn].match(lines[lineno][ipos:])
                if x:
                    unknown = False
                    i = ipos
                    if istkn in ('space', ):
                        ipos += x.end()
                        continue
            if unknown:
                ipos += 1


def parse_file(ctx=None):
    # pdb.set_trace()
    ctx = {} if ctx is None else ctx
    B = Builder(ctx["tmpl_fn"])
    B.parse_file(ctx['src_fn'])

if __name__ == "__main__":
    parser = parseoptargs("Topep8",
                          "© 2014-2017 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument("-t", "--template",
                        help="template, maybe {markdown|}",
                        dest="tmpl_fn", metavar="file")
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_fn')
    parser.add_argument('dst_filepy',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    sts = parse_file(ctx=ctx)
    exit(sts)
