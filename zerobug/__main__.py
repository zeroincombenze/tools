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
"""z0bug
"""

import os
import sys
import zerobug


__version__ = "0.2.14.3"


if __name__ == "__main__":
    if 'DEV_ENVIRONMENT' in os.environ:
        if os.path.isdir('./tests'):
            os.chdir('./tests')
            sts = execfile("test_zerobug.py")
            sys.exit(sts)

    print zerobug.z0testlib.__version__
    for text in __doc__.split('\n'):
        print text
        sys.exit(0)
