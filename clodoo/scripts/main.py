#!/usr/bin/env python
# -*- coding: utf-8 -*-
# template 26
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
import os.path as pth
import sys


__version__ = "2.0.15"


def get_pypi_info(pypi):   # pragma: no cover
    pypi_metadata = {
        "name": pypi,
        "version": False,
        "long_description": __doc__,
        "requires": [],
        "package_data": [],
        "libpath": __file__,
    }
    while (pth.basename(pypi_metadata["libpath"]) not in (
            "site-packages", "bin", "lib")):
        pypi_metadata["libpath"] = pth.dirname(pypi_metadata["libpath"])
    if sys.version_info[0] == 2:
        import pkg_resources
        pypi_metadata["version"] = pkg_resources.get_distribution(pypi).version
        # TODO> compatibility mode to remove early
        for base in ("z0librc", "odoorc", "odooctl", "travisrc"):
            fn = pth.join(
                pypi_metadata["libpath"],
                pkg_resources.resource_filename(pypi, base))
            if pth.isfile(fn):
                pypi_metadata["package_data"].append(fn)
                if base == "odoorc":
                    pypi_metadata["package_data"].append(pth.dirname(fn))
                elif base == "travisrc":
                    pypi_metadata["package_data"].append(
                        pth.join(pth.dirname(fn), "travis"))
    else:
        if sys.version_info < (3, 8):
            import importlib_metadata as metadata
        else:
            from importlib import metadata
        pypi_metadata["version"] = metadata.version(pypi)
        for base in ("z0librc", "odoorc", "odooctl", "travisrc"):
            util = [p for p in metadata.files(pypi) if base in str(p)]
            if util:
                fn = str(util[0].locate())
                pypi_metadata["package_data"].append(fn)
                if base == "odoorc":
                    pypi_metadata["package_data"].append(pth.dirname(fn))
                elif base == "travisrc":
                    pypi_metadata["package_data"].append(
                        pth.join(pth.dirname(fn), "travis"))
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
            if pth.exists(fqn):
                if pth.islink(tgt_fqn):
                    os.unlink(tgt_fqn)
                print("$ ln -s %s %s" % (fqn, tgt_fqn))
            os.symlink(fqn, tgt_fqn)


def main(cli_args=None):  # pragma: no cover
    if not cli_args:
        cli_args = sys.argv[1:]
    action = "-H"
    verbose = False
    for arg in cli_args:
        if arg in ("-h", "-H", "--help", "-V", "--version", "-C", "--copy-pkg-data"):
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
