# -*- coding: utf-8 -*-
"""
Clodoo is a set of tools to manage to manage multiple Odoo installations with many DBs.

With clodoo you can do massive operations on 1 or more Odoo databases based on
different Odoo versions. Main operation are:

* create consistent database to run tests
* repeat consistent action on many db with same or different Odoo version
* repeat above actions on every new database

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 13.0)
"""
import os
import sys
import shutil


__version__ = '0.3.34.8'


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
        globals()['setup_args']['setup'] = setup_file
    return globals()['setup_args']


def copy_pkg_data(setup_args):
    if setup_args.get('package_data'):
        pkgpath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        bin_path = lib_path = ''
        path = pkgpath
        while not bin_path and path != '/':
            path = os.path.dirname(path)
            if os.path.isdir(path) and os.path.basename(path) == 'lib':
                bin_path = os.path.join(os.path.dirname(path), 'bin')
                lib_path = path
        if bin_path:
            for pkg in setup_args['package_data'].keys():
                for fn in setup_args['package_data'][pkg]:
                    full_fn = os.path.abspath(os.path.join(pkgpath, fn))
                    if os.access(full_fn, os.X_OK):
                        tgt_fn = os.path.abspath(os.path.join(bin_path, fn))
                    else:
                        tgt_fn = os.path.abspath(os.path.join(lib_path, fn))
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
