# -*- coding: utf-8 -*-
# template 17
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
import pkg_resources
import gzip
import shutil


__version__ = '1.0.5'


def fake_setup(**kwargs):
    globals()['setup_args'] = kwargs


def read_setup():
    setup_info = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'setup.info'))
    if not os.path.isfile(setup_info):
        setup_info = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'setup.py'))
    setup_args = {}
    if os.path.isfile(setup_info):
        with open(setup_info, 'r') as fd:
            exec(fd.read().replace('setup(', 'fake_setup('))
            setup_args = globals()['setup_args']
    else:
        print('Not internal configuration file found!')
    setup_args['setup'] = setup_info
    try:
        pkg = pkg_resources.get_distribution(__package__.split('.')[0])
        setup_args['name'] = pkg.key
        setup_args['version'] = pkg.version
    except BaseException:
        pass
    return setup_args


def get_pypi_paths():
    local_venv = '/devel/venv/'
    pkgpath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..'))
    bin_path = lib_path = ''
    path = pkgpath
    while not bin_path and path != '/' and path != os.environ['HOME']:
        path = os.path.dirname(path)
        if os.path.isdir(path) and os.path.basename(path) == 'lib':
            bin_path = os.path.join(os.path.dirname(path), 'bin')
            lib_path = path
    if not bin_path and local_venv:
        for path in sys.path:
            if local_venv in path:
                bin_path = os.path.join(
                    path[:path.find(local_venv)],
                    *[x for x in local_venv.split('/') if x][:-1])
                break
    return pkgpath, bin_path, lib_path


def copy_pkg_data(setup_args, verbose):
    if setup_args.get('package_data'):
        pkgpath, bin_path, lib_path = get_pypi_paths()
        if bin_path:
            # TODO> compatibility mode
            bin2_path = os.path.join(os.environ['HOME'], 'devel')
            if not os.path.isdir(bin2_path):
                bin2_path = ''
            man_path = os.path.join(bin_path, 'man', 'man8')
            if not os.path.isdir(man_path):
                man_path = ''
            for pkg in setup_args['package_data'].keys():
                for fn in setup_args['package_data'][pkg]:
                    base = os.path.basename(fn)
                    if base in ('setup.info', '*'):
                        continue
                    full_fn = os.path.abspath(os.path.join(pkgpath, fn))
                    if base.endswith('.man') and man_path:
                        with open(full_fn, 'r') as fd:
                            help_text = fd.read()
                        tgt_fn = os.path.join(man_path, '%s.8.gz' % base[:-4])
                        with gzip.open(tgt_fn, 'w') as fd:
                            fd.write(help_text)
                        continue
                    if lib_path:
                        tgt_fn = os.path.join(lib_path, base)
                        if verbose:
                            print('$ cp %s %s' % (full_fn, tgt_fn))
                        shutil.copy(full_fn, tgt_fn)
                    # TODO> compatibility mode
                    tgt_fn = os.path.join(bin_path, base)
                    if os.path.isfile(tgt_fn):
                        os.unlink(tgt_fn)
                    if not os.path.exists(tgt_fn):
                        if verbose:
                            print('$ ln -s %s %s' % (full_fn, tgt_fn))
                        os.symlink(full_fn, tgt_fn)
                    if bin2_path:
                        tgt_fn = os.path.join(bin2_path, base)
                        if os.path.isfile(tgt_fn):
                            os.unlink(tgt_fn)
                        # if not os.path.exists(tgt_fn):
                        #     if verbose:
                        #         print('$ ln -s %s %s' % (full_fn, tgt_fn))
                        #     os.symlink(full_fn, tgt_fn)
            # TODO> compatibility mode to remove early
            if lib_path and bin2_path:
                for base in ('z0librc', 'odoorc', 'travisrc'):
                    full_fn = os.path.join(bin2_path, base)
                    tgt_fn = os.path.join(bin_path, base)
                    if os.path.exists(full_fn) and not os.path.exists(tgt_fn):
                        if verbose:
                            print('$ cp %s %s' % (full_fn, tgt_fn))
                        shutil.copy(full_fn, tgt_fn)


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    action = '-H'
    verbose = False
    for arg in cli_args:
        if arg in ('-h', '-H', '--help', '-V', '--version', '--copy-pkg-data'):
            action = arg
        elif arg == '-v':
            verbose = True
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
        copy_pkg_data(setup_args, verbose)
    return 0
