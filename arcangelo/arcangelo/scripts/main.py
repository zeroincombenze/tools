#!/usr/bin/env python
# -*- coding: utf-8 -*-
# template 26
"""
**arcangelo** is an automatic editor for mass building python source code.
**arcangelo** is used to perform basic text transformation based on user rules.
While in some ways is similar to an editor which permits scripted edits (such as
ed or sed), **arcangelo** operates by making change command from rule files.
Rule files are simple yaml files, read by arcangelo which apply these rules to every
line of files processed.

In this way migration workflow is very simple, accurate, precise and fast
"""
import os
import os.path as pth
import sys


__version__ = "2.1.1"

PKG_FILES = (
    "bck_filestore.sh",
    "force_password.sh",
    "odooctl",
    "odoorc",
    "pg_db_reassign_owner",
    "set_workers",
    "travis",
    "travisrc",
    "xuname",
    "z0librc",
)
BIN_FILES = (
    "bck_filestore.sh",
    "build_cmdd",
    "force_password.sh",
    "list_requirements.py",
    "odooctl",
    "pg_db_active",
    "pg_db_reassign_owner",
    "set_workers",
    "travis",
    "travis_after_tests_success",
    "travis_run_pypi_tests",
    "xuname",
)


def get_fn_from_base_2(pkg_resources, pypi, pypi_metadata, base):
    fn = pth.abspath(pth.join(
        pypi_metadata["libpath"],
        pkg_resources.resource_filename(pypi, base)))
    if not pth.isfile(fn) and not pth.isdir(fn):
        fn = ""
    return fn


def get_fn_from_base_3(metadata, pypi, base):
    fn = ""
    util = [p for p in metadata.files(pypi) if pth.basename(str(p)) == base]
    if util:
        fn = pth.abspath(str(util[0].locate()))
    return fn


def get_pypi_info(pypi):
    pypi_metadata = {
        "name": pypi,
        "version": False,
        "long_description": __doc__,
        "requires": [],
        "package_data": [],
        "bin_files": [],
        "libpath": __file__,
    }
    while (pth.basename(pypi_metadata["libpath"]) not in (
            "site-packages", "bin", "lib", "pypi")):
        pypi_metadata["libpath"] = pth.dirname(pypi_metadata["libpath"])
    if sys.version_info[0] == 2:
        import pkg_resources
        pypi_metadata["version"] = pkg_resources.get_distribution(pypi).version
        for base in PKG_FILES:
            fn = get_fn_from_base_2(pkg_resources, pypi, pypi_metadata, base)
            if fn:
                pypi_metadata["package_data"].append(fn)
        for base in BIN_FILES:
            fn = get_fn_from_base_2(pkg_resources, pypi, pypi_metadata, base)
            if fn:
                pypi_metadata["bin_files"].append(fn)
    else:
        if sys.version_info < (3, 8):
            import importlib_metadata as metadata
        else:
            from importlib import metadata
        pypi_metadata["version"] = metadata.version(pypi)
        for base in PKG_FILES:
            fn = get_fn_from_base_3(metadata, pypi, base)
            if fn:
                pypi_metadata["package_data"].append(fn)
        for base in BIN_FILES:
            fn = get_fn_from_base_3(metadata, pypi, base)
            if fn:
                pypi_metadata["bin_files"].append(fn)
    return pypi_metadata


def get_metadata():   # pragma: no cover
    # Searching metadata in test environment because package is not really installed
    return get_pypi_info(__package__.split(".")[0])


def get_pypi_path(pypi_metadata):   # pragma: no cover
    bin_path = lib_path = ""
    path = pypi_metadata["libpath"]
    while not bin_path and path != "/" and path != os.environ["HOME"]:
        if pth.isdir(path) and pth.basename(path) in ("bin", "lib"):
            if (
                    pth.isdir(pth.join(pth.dirname(path), "bin"))
                    and pth.isdir(pth.join(pth.dirname(path), "lib"))
            ):
                bin_path = pth.join(pth.dirname(path), "bin")
                lib_path = pth.join(pth.dirname(path), "lib")
                continue
        path = pth.dirname(path)
    return bin_path, lib_path


def copy_pkg_data(pypi_metadata, verbose):  # pragma: no cover
    if pypi_metadata.get("package_data"):
        bin_path, lib_path = get_pypi_path(pypi_metadata)
        for fqn in pypi_metadata.get("package_data"):
            base = pth.basename(fqn)
            tgt_fqn = pth.join(bin_path, base)
            if pth.exists(fqn) and pth.islink(tgt_fqn):
                os.unlink(tgt_fqn)
            if pth.exists(fqn) and not pth.exists(tgt_fqn):
                if verbose:
                    print("$ ln -s %s %s" % (fqn, tgt_fqn))
                os.symlink(fqn, tgt_fqn)
    for fqn in pypi_metadata.get("bin_files"):
        if verbose:
            print("$ chmod +x %s" % fqn)
        os.system("chmod +x %s" % fqn)


def internal_main(cli_args=None):  # pragma: no cover
    if not cli_args:
        cli_args = sys.argv[1:]
    action = "-H"
    verbose = False
    for arg in cli_args:
        if arg in ("-h", "-H", "--help", "-V", "--version", "-C", "--copy-pkg-data"):
            action = arg
        elif arg == "-v":
            verbose = True
        elif arg == "-q":
            verbose = False
    pypi_metadata = get_metadata()
    if action == "-h":
        print(
            "%s [-h][-H][--help][-V][--version][-C][--copy-pkg-data]"
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
