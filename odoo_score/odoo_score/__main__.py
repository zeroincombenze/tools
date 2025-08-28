#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from odoo_score import internal_main

__version__ = "2.0.11"


def version():
    return __version__


def main(cli_args=None):
    if cli_args and any(
            [arg in ("-V", "--version", "--copy-pkg-data") for arg in cli_args]):
        return internal_main(cli_args)
    return 126


if __name__ == "__main__":
    sys.exit(main())
