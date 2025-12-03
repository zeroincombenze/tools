#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from clodoo import internal_main, clodoo_main

__version__ = "2.0.18"


def version():
    return __version__


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    if cli_args and any(
            [arg in ("-V", "--version", "--copy-pkg-data") for arg in cli_args]):
        return internal_main(cli_args)
    return clodoo_main(cli_args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
