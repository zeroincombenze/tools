#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import sys
# import pdb

__version__ = "1.0.4"

params = {'clear_base_tnl': False}
me = True

for prm in sys.argv:
    if me:
        me = False
        continue
    elif prm[0] == '-':
        if prm[0:2] == '-b':
            params['branch'] = prm[2:]
        elif prm[0:2] == '-C':
            params['clear_base_tnl'] = True
        elif prm[0:2] == '-m':
            params['module'] = prm[2:]
        elif prm[0:2] == '-V':
            print(__version__)
            exit(0)
        else:
            print('makepo_it.py [-bbranch] [-C] [-mmodule] file_po')
            exit(1)
    elif 'file' not in params:
        params['file'] = prm
    else:
        print('makepo_it.py [-bbranch] [-C] [-mmodule] file_po')
        exit(1)

with open(params['file'], 'rU') as fd:
    LAST_TNL_NAME = 'Antonio M. Vigliotti'
    LAST_TNL_MAIL = 'antoniomaria.vigliotti@gmail.com'
    LAST_TEAM_NAME = 'Zeroincombenze'
    LAST_TEAM_URL = 'https://www.zeroincombenze.it'
    polines = fd.read().split('\n')
    potext = ''
    saved_lines = []
    discard_saved_lines = False
    for line in polines:
        if line.startswith('"#\t*'):
            potext += r'"# %s\n"' % params['module'] + '\n'
        elif line.startswith('"# *'):
            potext += r'"# %s\n"' % params['module'] + '\n'
        elif line.startswith('"Project-Id-Version:'):
            potext += r'"Project-Id-Version: Odoo (%s)\n"' % params[
                'branch'] + '\n'
        elif line.startswith('"Last-Translator:'):
            potext += r'"Last-Translator: %s <%s>\n"' % (
                LAST_TNL_NAME, LAST_TNL_MAIL) + '\n'
        elif line.startswith('"Language-Team:'):
            potext += r'"Language-Team: %s (%s)\n"' % (
                LAST_TEAM_NAME, LAST_TEAM_URL) + '\n'
            potext += r'"Language: it_IT\n"' + '\n'
        elif line.startswith('"Language:'):
            pass
        elif line.startswith('"language'):
            pass
        elif line.startswith('"Plural-Forms:'):
            potext += r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"' + '\n'
        elif params['clear_base_tnl']:
            if line.startswith('#. module: base'):
                saved_lines.append(line)
            elif line.startswith('#: model:ir.module.module,description'):
                saved_lines.append(line)
                discard_saved_lines = True
            elif line.startswith('#: model:ir.module.module,shortdesc'):
                saved_lines.append(line)
                discard_saved_lines = True
            elif line.startswith('#: model:ir.module.module,summary'):
                saved_lines.append(line)
                discard_saved_lines = True
            elif saved_lines:
                if not line or line.startswith('#'):
                    if not discard_saved_lines:
                        for ln in saved_lines:
                            potext += ln + '\n'
                    saved_lines = []
                    discard_saved_lines = False
                    potext += line + '\n'
                else:
                    saved_lines.append(line)
            else:
                potext += line + '\n'
        else:
            potext += line + '\n'
    if saved_lines and not discard_saved_lines:
        for ln in saved_lines:
            potext += ln + '\n'
        saved_lines = []
with open(params['file'], 'w') as fd:
    fd.write(potext)
