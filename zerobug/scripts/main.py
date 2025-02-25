#!/usr/bin/env python
# -*- coding: utf-8 -*-
# template 25
"""
Python supplemental features
----------------------------

python_plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code
from Python 2 to Python 3 and still have it run on Python 2.


vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package is released with a nice command:
**vem** that is an interactive tool with some nice features to manage standard
virtual environment.
"""
import os
import os.path as pth
import sys
import gzip
import shutil


__version__ = "2.0.18"


def get_pypi_info(pkgname):
    pypi_metadata = {
        "name": pkgname, "version": False, "where": "pylib",
        "long_description": __doc__,
    }
    if sys.version_info[0] == 2:
        import pkg_resources
        try:
            pypi_metadata["version"] = pkg_resources.get_distribution(pkgname).version
        except BaseException:
            pass
    else:
        if sys.version_info < (3, 8):
            import importlib_metadata as metadata
        else:
            from importlib import metadata
        try:
            pypi_metadata["version"] = metadata.version(pkgname)
            # for ln in metadata.metadata(pkgname).items():
            #     if ln[0] == "Description":
            #         pypi_metadata["long_description"] = ln[1]
            #         break
        except BaseException:
            pass
    return pypi_metadata


def fake_setup(**kwargs):
    globals()["pypi_metadata"] = kwargs


def get_metadata():
    # Searching metadata in test environment because package is not really installed
    pypi_metadata = {}
    ctr = 3
    home = os.path.expanduser("~")
    here = pth.abspath(pth.dirname(pth.realpath(__file__)))
    setup_info = pth.join(here, "setup.py")
    while not pth.isfile(setup_info):
        here = pth.dirname(here)
        if not pth.basename(here) in ("test", "scripts"):
            ctr -= 1
        elif pth.basename(here) in (__package__, "build"):
            ctr = 1
        if ctr == 0 or not here.startswith(home):
            break
        setup_info = pth.join(here, "setup.py")
    if pth.isfile(setup_info):
        with open(setup_info, "r") as fd:
            exec(fd.read().replace("setup(", "fake_setup("))
            pypi_metadata = globals()["pypi_metadata"]
    if not pypi_metadata:
        # Search for metadata in python environment
        return get_pypi_info(__package__.split(".")[0])
    # readme = pth.join(pkgpath, "README.rst")
    # with open(readme, "r") as fd:
    #     pypi_metadata["long_description"] = fd.read()
    pypi_metadata["where"] = "local"
    return pypi_metadata


def get_pypi_paths():
    local_venv = "/devel/venv/"
    pkgpath = pth.abspath(pth.join(pth.dirname(__file__), ".."))
    bin_path = lib_path = ""
    path = pkgpath
    while not bin_path and path != "/" and path != os.environ["HOME"]:
        path = pth.dirname(path)
        if pth.isdir(path) and pth.basename(path) in ("bin", "lib"):
            if (
                    pth.isdir(pth.join(pth.dirname(path), "bin"))
                    and pth.isdir(pth.join(pth.dirname(path), "lib"))
            ):
                bin_path = pth.join(pth.dirname(path), "bin")
                lib_path = pth.join(pth.dirname(path), "lib")
    if not bin_path and local_venv:
        for path in sys.path:
            if local_venv in path:
                bin_path = pth.join(
                    path[: path.find(local_venv)],
                    *[x for x in local_venv.split("/") if x][:-1]
                )
                break
    return pkgpath, bin_path, lib_path


def copy_pkg_data(pypi_metadata, verbose):
    if pypi_metadata.get("package_data"):
        pkgpath, bin_path, lib_path = get_pypi_paths()
        if bin_path:
            # TODO> compatibility mode
            bin2_path = pth.join(os.environ["HOME"], "devel")
            if not pth.isdir(bin2_path):
                bin2_path = ""
            man_path = pth.join(bin_path, "man", "man8")
            if not pth.isdir(man_path):
                man_path = ""
            for pkg in pypi_metadata["package_data"].keys():
                for fn in pypi_metadata["package_data"][pkg]:
                    base = pth.basename(fn)
                    if base in ("setup.info", "*"):
                        continue
                    full_fn = pth.abspath(pth.join(pkgpath, fn))
                    if base.endswith(".man") and man_path:
                        with open(full_fn, "r") as fd:
                            help_text = fd.read()
                        tgt_fn = pth.join(man_path, "%s.8.gz" % base[:-4])
                        with gzip.open(tgt_fn, "w") as fd:
                            if sys.version_info[0] == 3:
                                fd.write(help_text.encode("utf-8"))
                            else:
                                fd.write(help_text)
                        if verbose:
                            print("$ gzip -c %s > %s" % (full_fn, tgt_fn))
                        continue
                    if lib_path:
                        tgt_fn = pth.join(lib_path, base)
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
                    tgt_fn = pth.join(bin_path, base)
                    if pth.isfile(tgt_fn):
                        os.unlink(tgt_fn)
                    if not pth.exists(tgt_fn):
                        if verbose:
                            print("$ ln -s %s %s" % (full_fn, tgt_fn))
                        os.symlink(full_fn, tgt_fn)
                    if bin2_path:
                        tgt_fn = pth.join(bin2_path, base)
                        if pth.isfile(tgt_fn):
                            os.unlink(tgt_fn)
            # TODO> compatibility mode to remove early
            if lib_path and bin2_path:
                for base in ("z0librc", "odoorc", "travisrc"):
                    full_fn = pth.join(bin2_path, base)
                    tgt_fn = pth.join(bin_path, base)
                    if pth.exists(full_fn) and not pth.exists(tgt_fn):
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
    # setup_args = read_setup()
    pypi_metadata = get_metadata()
    if action == "-h":
        print(
            "%s [-h][-H][--help][-V][--version][-C][--copy-pkg-data]"
            # % setup_args["name"]
            % pypi_metadata["name"]
        )
    elif action in ("-V", "--version"):
        if pypi_metadata["version"] == __version__:
            print(pypi_metadata["version"])
        else:
            print("Version mismatch %s/%s" % (pypi_metadata["version"], __version__))
    elif action in ("-H", "--help"):
        for text in pypi_metadata["long_description"].split("\n"):
            print(text)
    elif action in ("-C", "--copy-pkg-data"):
        copy_pkg_data(pypi_metadata, verbose)
    return 0
