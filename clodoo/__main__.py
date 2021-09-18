#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""clodoo
Massive operations on Zeroincombenze(R) / Odoo databases
"""

from __future__ import print_function, unicode_literals
# from __future__ import absolute_import
import os
import sys


__version__ = "0.3.34.8"


def fake_setup(**kwargs):
    globals()['dict_setup'] = kwargs


def read_setup():
    to_copy = False
    setup_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
    setup_copy = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'setup.py'))
    if not os.path.isfile(setup_file):
        setup_file = setup_copy
    elif not os.path(setup_copy):
        to_copy = True
    # dict_setup = {}
    if os.path.isfile(setup_file):
        with open(setup_file, 'r') as fd:
            content = fd.read()
            if to_copy:
                with open(setup_copy) as fd2:
                    fd2.write(content)
            content = content.replace('setup(', 'fake_setup(')
            exec (content)
    return globals()['dict_setup']


if __name__ == "__main__":
    action = False if len(sys.argv) < 2 else sys.argv[1]
    dict_setup = read_setup()
    if action == '-h':
        print('%s [-h] [--help] [-H] [-V]' % dict_setup['name'])
        sys.exit(0)
    # import pdb
    # pdb.set_trace()
    # bindir = os.path.dirname(__file__)
    if action not in ('-H', '--help'):
        if dict_setup['version'] == __version__:
            print(dict_setup['version'])
        else:
            print('Version mismatch %s/%s' % (dict_setup['version'],
                                              __version__))
    if action != '-V':
        for text in __doc__.split('\n'):
            print(text)
    sys.exit(0)
