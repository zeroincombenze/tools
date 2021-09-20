# -*- coding: utf-8 -*-
"""
lis* stands for Linux Install Simplifier App

lisa is an interactive tool to install, update, remove, query and manage software for building a complete LAMP server.
LAMP means Linux Apache Mysql PHP; in recent times, Python and Postgresql were added.

lisa is just a front-end for yum and apt-get commands, it is not a real package installer.
It require yum on CentOS and Red Hat family distros, and apt-get on Ubuntu and debian family distros.
It is very useful to manage all the packages needed to build a complete LAMP server and to check the real server status.
For every main package, may be managed some dependent package; i.e. openssh-server manages openssh-client too.

You can easily write portable script to install packages on every Linux distribution.
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
        os.path.join(os.path.dirname(__file__), 'setup.conf'))
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
                    base = os.path.basename(fn)
                    if base == 'setup.conf':
                        continue
                    full_fn = os.path.abspath(os.path.join(pkgpath, fn))
                    if os.access(full_fn, os.X_OK):
                        tgt_fn = os.path.abspath(os.path.join(bin_path, base))
                    else:
                        tgt_fn = os.path.abspath(os.path.join(lib_path, base))
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
