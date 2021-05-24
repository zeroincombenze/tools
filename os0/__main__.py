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

from __future__ import print_function, unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
from python_plus import _u
import os
import sys
import subprocess

try:
    import z0testlib
    Z0BUG = z0testlib.Z0test()
except ImportError:
    from zerobug import Z0BUG
standard_library.install_aliases()


__version__ = "1.0.1"
STS_FAILED = 1
STS_SUCCESS = 0

if __name__ == "__main__":
    action = False
    if len(sys.argv) > 1:
        action = sys.argv[1]
    if action == '-h':
        print('%s [-h] [-H] [-T] [-V]' % Z0BUG.module_id)
        sys.exit(STS_SUCCESS)
    test_file = 'zerobug'
    if (action == '-T' or ('DEV_ENVIRONMENT' in os.environ and
            os.environ['DEV_ENVIRONMENT'] == Z0BUG.module_id)):
        if (os.path.isdir('./tests') and
                os.path.isfile(os.path.join('tests', test_file))):
            os.chdir('./tests')
            sts = subprocess.call(test_file)
        elif os.path.isfile(test_file):
            sts = subprocess.call(test_file)
        else:
            sts = STS_FAILED
        sys.exit(sts)

    if action != '-H':
        to_copy = False
        setup_file = './setup.py'
        if os.path.isfile('../setup.py') and os.path.isfile('./setup.py'):
            to_copy = True
            setup_file = '../setup.py'
        with open(setup_file, 'r') as fd:
            do_copy = False
            content = _u(fd.read())
            for line in content.split('\n'):
                if line.find('version=') >= 0:
                    version = line.split('=')[1].strip()
                    if version[1:-2] == __version__:
                        print(version[1:-2])
                        do_copy = True
                    else:
                        print('Version mismatch %s/%s' % (version[1:-2],
                                                          __version__))
                    break
            if to_copy and do_copy:
                fd2 = open('./setup.py', 'w')
                fd2.write(content)
                fd2.close()
    if action != '-V':
        for text in __doc__.split('\n'):
            print(text)
    sys.exit(0)
