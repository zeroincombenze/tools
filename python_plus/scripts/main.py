# -*- coding: utf-8 -*-
"""
Python supplemental features
----------------------------

python_plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from Python 2 to Python 3 and still have it run on Python 2.


vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package is released with an nice command:
**vem** that is an interactive tool with some nice features to manage standard virtual environment and it is osx/darwin compatible.
"""
import os
import sys


__version__ = '1.0.3'


def fake_setup(**kwargs):
    globals()['setup_args'] = kwargs


def read_setup():
    to_copy = False
    setup_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
    setup_bup = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'setup.py'))
    if not os.path.isfile(setup_file):
        setup_file = setup_bup
    elif os.path.isfile((setup_bup)):
        to_copy = True
    if os.path.isfile(setup_file):
        with open(setup_file, 'r') as fd:
            content = fd.read()
            if to_copy:
                with open(setup_bup) as fd2:
                    fd2.write(content)
            content = content.replace('setup(', 'fake_setup(')
            exec(content)
    return globals()['setup_args']


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    action = False if not cli_args else cli_args[0]
    setup_args = read_setup()
    if action == '-h':
        print('%s [-h] [--help] [-H] [-V]' % setup_args['name'])
        return 0
    if action not in ('-H', '--help'):
        if setup_args['version'] == __version__:
            print(setup_args['version'])
        else:
            print('Version mismatch %s/%s' % (setup_args['version'],
                                              __version__))
    if action != '-V':
        for text in __doc__.split('\n'):
            print(text)
    return 0
