# -*- coding: utf-8 -*-
"""
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

See https://en.wikipedia.org/wiki/Path_(computing)
"""
import os
import sys


__version__ = '1.0.1.99'


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
