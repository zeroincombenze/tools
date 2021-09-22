# -*- coding: utf-8 -*-
"""
Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**; all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

    `travis show`

    `less -R ~/travis_log/<build_name>.log`

A travis build executes the following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Optional install packages `apt addons` (emulatore makes just the check)
* Optional install packages `cache`
* Set global values `env global`
* Execute code `before_install`
* Execute matrix initialization, included python version
* Execute build code `install`
* Execute build code `before_script`
* Execute build code `script`
* Execute build `before_cache` (only if cache is effective, not emulated)
* Execute build code `after_success` (emulated) or `after_failure` (not emulated)
* Optional code `before_deploy` (only if deployment is effective, not emulated)
* Optional code `deploy` (not emulated)
* Optional code `after_deploy` (only if deployment is effective, not emulated)
* Execute code `after_script` (not emulated)
* Wep from local .travis.conf (not in travis-ci.org)

Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__
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
                    if base == 'setup.conf':
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
