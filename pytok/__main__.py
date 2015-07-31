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

    pytok library extracts pieces of python code on selection criteria.
    Filters can be set on class(es), function(s).
    You could image pytok like an enhanced Linux command grep.

    pytok evaluates the first inheritance level.

    pytok recognizes the Odoo models too.

    See http://wiki.zeroincombenze.org/en/Python/opt/pytok
"""

import os
import sys
from pytok import pytok

if __name__ == "__main__":
    """
    Check for developer environment
    """
    if 'DEV_ENVIRONMENT' in os.environ:
        if os.path.isdir('./tests'):
            os.chdir('./tests')
            sts = execfile("test_pytok.py")
            sys.exit(sts)

    print pytok.version
    for text in __doc__.split('\n'):
        print text
        sys.exit(0)
