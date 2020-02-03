#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
"""Python source diff
"""
import sys
import tokenize
# import pdb


__version__ = "0.0.1"


def get_token(tok_obj):
    # toktype, tokval, (srow, scol), (erow, ecol), line = tok_obj.next()
    return tok_obj.next()


fn_left = sys.argv[1]
fn_right = sys.argv[2]
sts = 1
if fn_left[-3:] == ".py" and fn_right[-3:] == ".py":
    fd_left = open(fn_left, 'rb')
    fd_right = open(fn_right, 'rb')
    left_obj = tokenize.generate_tokens(
        fd_left.readline,
        )
    right_obj = tokenize.generate_tokens(
        fd_right.readline,
        )

    for toktype, tokval, (srow, scol), (erow, ecol), line in left_obj:
        print "%d,%d-%d,%d:\t%s\t%s" % \
            (srow, scol, erow, ecol, tokenize.tok_name[toktype], repr(tokval))
    sts = 0
sys.exit(sts)
