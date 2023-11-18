#!/usr/bin/env python
# -*- coding: utf-8 -*-
# template 21
"""
Travis emulator can emulate TravisCi parsing the **.travis.yml** file in
local Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**;
all the builds are executed in sequential way.
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

Read furthermore info read
`travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__
"""
import os
import sys
import pkg_resources
import gzip
import shutil


__version__ = "2.0.7"


def fake_setup(**kwargs):
    globals()["setup_args"] = kwargs


def read_setup():
    setup_info = os.path.abspath(os.path.join(os.path.dirname(__file__), "setup.info"))
    if not os.path.isfile(setup_info):
        setup_info = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "setup.py")
        )
    setup_args = {}
    if os.path.isfile(setup_info):
        with open(setup_info, "r") as fd:
            exec(fd.read().replace("setup(", "fake_setup("))
            setup_args = globals()["setup_args"]
    else:
        print("Not internal configuration file found!")
    setup_args["setup"] = setup_info
    try:
        pkg = pkg_resources.get_distribution(__package__.split(".")[0])
        setup_args["name"] = pkg.key
        setup_args["version"] = pkg.version
    except BaseException:
        pass
    return setup_args


def get_pypi_paths():
    local_venv = "/devel/venv/"
    pkgpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    bin_path = lib_path = ""
    path = pkgpath
    while not bin_path and path != "/" and path != os.environ["HOME"]:
        path = os.path.dirname(path)
        if os.path.isdir(path) and os.path.basename(path) in ("bin", "lib"):
            if (os.path.isdir(os.path.join(os.path.dirname(path), "bin")) and
                    os.path.isdir(os.path.join(os.path.dirname(path), "lib"))):
                bin_path = os.path.join(os.path.dirname(path), "bin")
                lib_path = os.path.join(os.path.dirname(path), "lib")
    if not bin_path and local_venv:
        for path in sys.path:
            if local_venv in path:
                bin_path = os.path.join(
                    path[: path.find(local_venv)],
                    *[x for x in local_venv.split("/") if x][:-1]
                )
                break
    return pkgpath, bin_path, lib_path


def copy_pkg_data(setup_args, verbose):
    if setup_args.get("package_data"):
        pkgpath, bin_path, lib_path = get_pypi_paths()
        if bin_path:
            # TODO> compatibility mode
            bin2_path = os.path.join(os.environ["HOME"], "devel")
            if not os.path.isdir(bin2_path):
                bin2_path = ""
            man_path = os.path.join(bin_path, "man", "man8")
            if not os.path.isdir(man_path):
                man_path = ""
            for pkg in setup_args["package_data"].keys():
                for fn in setup_args["package_data"][pkg]:
                    base = os.path.basename(fn)
                    if base in ("setup.info", "*"):
                        continue
                    full_fn = os.path.abspath(os.path.join(pkgpath, fn))
                    if base.endswith(".man") and man_path:
                        with open(full_fn, "r") as fd:
                            help_text = fd.read()
                        tgt_fn = os.path.join(man_path, "%s.8.gz" % base[:-4])
                        with gzip.open(tgt_fn, "w") as fd:
                            if sys.version_info[0] == 3:
                                fd.write(help_text.encode("utf-8"))
                            else:
                                fd.write(help_text)
                        if verbose:
                            print("$ gzip -c %s > %s" % (full_fn, tgt_fn))
                        continue
                    if lib_path:
                        tgt_fn = os.path.join(lib_path, base)
                        if sys.version_info[0] == 3:
                            try:
                                shutil.copy(full_fn, tgt_fn)
                                if verbose:
                                    print("$ cp %s %s" % (full_fn, tgt_fn))
                            except shutil.SameFileError:
                                pass
                        else:
                            try:
                                shutil.copy(full_fn, tgt_fn)
                                if verbose:
                                    print("$ cp %s %s" % (full_fn, tgt_fn))
                            except BaseException:
                                pass
                    # TODO> compatibility mode
                    tgt_fn = os.path.join(bin_path, base)
                    if os.path.isfile(tgt_fn):
                        os.unlink(tgt_fn)
                    if not os.path.exists(tgt_fn):
                        if verbose:
                            print("$ ln -s %s %s" % (full_fn, tgt_fn))
                        os.symlink(full_fn, tgt_fn)
                    if bin2_path:
                        tgt_fn = os.path.join(bin2_path, base)
                        if os.path.isfile(tgt_fn):
                            os.unlink(tgt_fn)
            # TODO> compatibility mode to remove early
            if lib_path and bin2_path:
                for base in ("z0librc", "odoorc", "travisrc"):
                    full_fn = os.path.join(bin2_path, base)
                    tgt_fn = os.path.join(bin_path, base)
                    if os.path.exists(full_fn) and not os.path.exists(tgt_fn):
                        if verbose:
                            print("$ cp %s %s" % (full_fn, tgt_fn))
                        shutil.copy(full_fn, tgt_fn)


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    action = "-H"
    verbose = False
    for arg in cli_args:
        if arg in ("-h", "-H", "--help", "-V", "--version", "--copy-pkg-data"):
            action = arg
        elif arg == "-v":
            verbose = True
    setup_args = read_setup()
    if action == "-h":
        print(
            "%s [-h][-H][--help][-V][--version][-C][--copy-pkg-data]"
            % setup_args["name"]
        )
    elif action in ("-V", "--version"):
        if setup_args["version"] == __version__:
            print(setup_args["version"])
        else:
            print("Version mismatch %s/%s" % (setup_args["version"], __version__))
    elif action in ("-H", "--help"):
        for text in __doc__.split("\n"):
            print(text)
    elif action in ("-C", "--copy-pkg-data"):
        copy_pkg_data(setup_args, verbose)
    return 0

