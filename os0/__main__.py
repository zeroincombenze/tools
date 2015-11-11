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
"""!
Package os0
===========

Operating System indipendent interface
--------------------------------------

This module extends python os module with a few new functionality
 to interface operating system.
It recognizes file name structure and manages both URI standard name
 both local name, as UNC and ODS5.

- URI (Uniform Resource Identifier) is standard posix filename.
- UNC (Uniform Naming Convention) is windows standard
- ODS5 is used for define OpenVMS standard filenames

An example of URI filename is '/home/myfile'.
UNC example for the same of previous URI name is '\\home\\myfile'
 (with single backslash)
ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'

See https://en.wikipedia.org/wiki/Path_(computing

How to use.
    >>> from os0 import os0

First method is set local filename of URI file.
Set local filename of URI name is the same URI name
    >>> os0.setlfilename('myFile')
    'myFile'

Set local filename has optional parameter. FLAT means generic file name
    >>> os0.setlfilename('myFile', os0.LFN_FLAT)
    'myFile'

Executable file in Windows or OpenVMS have .EXE extension.
Conversion of URI name must add .EXE suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile'
or
    'myFile.exe'

Command file in Windows has .BAT suffix while in OpenVMS haS .COM extension.
Conversion of URI name must add these suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile'
or
    'myFile.bat'
or
    'myFile.com'

    See http://wiki.zeroincombenze.org/en/Python/opt/os0
"""

import os
import sys
# from subprocess import call
from os0 import os0

if __name__ == "__main__":
    # """
    # Check for developer environment
    # """
    if 'DEV_ENVIRONMENT' in os.environ:
        if os.path.isdir('./tests'):
            os.chdir('./tests')
            # sts = call("all_tests")
            sts = execfile("test_os0.py")
            sys.exit(sts)

    print os0.version
    for text in __doc__.split('\n'):
        print text
        sys.exit(0)
