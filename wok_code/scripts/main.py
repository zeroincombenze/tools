# -*- coding: utf-8 -*-
"""
Various tools at your fingertips.

The available tools are:

* cvt_csv_2_rst.py: convert csv file into rst file
* cvt_csv_2_xml.py: convert csv file into xml file
* cvt_script: parse bash script and convert to meet company standard
* gen_readme.py: generate documentation files, mainly README.rst
* odoo_dependency.py: show odoo depencies and/or Odoo module tree
* odoo_translation.py: manage Odoo translation
* pep8: parse source .py file to meet pep8 and convert across Odoo versions
* please: developer shell
* wget_odoo_repositories.py: get repository names from github.com
"""
import os
import sys


__version__ = '1.0.2.99'


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
