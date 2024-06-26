# -*- coding: utf-8 -*-
"""
This package is an plug-in of zerobug package and aim to easily create odoo tests.

It replaces OCA MQT with some nice additional features.

z0bug_odoo is built on follow concepts:

* Odoo version independent; it can test Odoo from 6.1 until 13.0
* It is designed to run in local environment too, using `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_
* It can run with full or reduced set of pylint tests
* Test using ready-made database records
* Quality Check Id
"""
import os
import sys
import pkg_resources
import shutil


__version__ = '1.0.2.99'


def fake_setup(**kwargs):
    globals()['setup_args'] = kwargs


def read_setup():
    setup_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'setup.info'))
    if not os.path.isfile(setup_file):
        setup_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
    if not os.path.isfile(setup_file):
        setup_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'setup.py'))
    setup_args = {}
    if os.path.isfile(setup_file):
        with open(setup_file, 'r') as fd:
            content = fd.read().replace('setup(', 'fake_setup(')
            exec(content)
            setup_args = globals()['setup_args']
    else:
        print('Not internal configuration file found!')
    pkg = pkg_resources.get_distribution(__package__.split('.')[0])
    setup_args['setup'] = setup_file
    setup_args['name'] = pkg.key
    setup_args['version'] = pkg.version
    return setup_args


def get_pypi_paths():
    pkgpath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..'))
    bin_path = lib_path = ''
    path = pkgpath
    while not bin_path and path != '/':
        path = os.path.dirname(path)
        if os.path.isdir(path) and os.path.basename(path) == 'lib':
            bin_path = os.path.join(os.path.dirname(path), 'bin')
            lib_path = path
    return pkgpath, bin_path, lib_path


def copy_pkg_data(setup_args):
    if setup_args.get('package_data'):
        pkgpath, bin_path, lib_path = get_pypi_paths()
        if bin_path:
            for pkg in setup_args['package_data'].keys():
                for fn in setup_args['package_data'][pkg]:
                    base = os.path.basename(fn)
                    if base == 'setup.info':
                        continue
                    full_fn = os.path.abspath(os.path.join(pkgpath, fn))
                    tgt_fn = os.path.abspath(os.path.join(lib_path, base))
                    print('$ cp %s %s' % (full_fn, tgt_fn))
                    shutil.copy(full_fn, tgt_fn)


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    action = '-H' if not cli_args else cli_args[0]
    setup_args = read_setup()
    if action == '-h':
        print('%s [-h][-H][--help][-V][--version][-C][--copy-pkg-data]' %
              setup_args['name'])
    elif action in ('-V', '--version'):
        if setup_args['version'] == __version__:
            print(setup_args['version'])
        else:
            print('Version mismatch %s/%s' % (setup_args['version'],
                                              __version__))
    elif action in ('-H', '--help'):
        for text in __doc__.split('\n'):
            print(text)
    elif action in ('-C', '--copy-pkg-data'):
        copy_pkg_data(setup_args)
    return 0
