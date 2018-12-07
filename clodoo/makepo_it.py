#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import sys

params = {}
me = True
for prm in sys.argv:
    if me:
        me = False
        continue
    elif prm[0] == '-':
        if prm[0:2] == '-b':
            params['branch'] = prm[2:]
        elif prm[0:2] == '-m':
            params['module'] = prm[2:]
        else:
            print('makepo_it.py [-bbranch] [-mmodule] file_po')
            exit(1)
    elif 'file' not in params:
        params['file'] = prm
    else:
        print('makepo_it.py [-bbranch] [-mmodule] file_po')
        exit(1)

with open(params['file'], 'rU') as fd:
    polines = fd.read().split('\n')
    potext = ''
    for line in polines:
        if line.startswith('"#\t*'):
            potext += r'"# %s\n"' % params['module'] + '\n'
        elif line.startswith('"# *'):
            potext += r'"# %s\n"' % params['module'] + '\n'
        elif line.startswith('"Project-Id-Version:'):
            potext += r'"Project-Id-Version: Odoo (%s)\n"' % params['branch'] + '\n'
        elif line.startswith('"Last-Translator:'):
            potext += r'"Last-Translator: Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>\n"' + '\n'
        elif line.startswith('"Language-Team:'):
            potext += r'"Language-Team: Zeroincombenze (https://www.zeroincombenze.it/)\n"' + '\n'
            potext += r'"Language: it_IT\n"' + '\n'
        elif line.startswith('"Language:'):
            pass
        elif line.startswith('"language'):
            pass
        elif line.startswith('"Plural-Forms:'):
            potext += r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"' + '\n'
        else:
            potext += line + '\n'
with open(params['file'], 'w') as fd:
    fd.write(potext)
