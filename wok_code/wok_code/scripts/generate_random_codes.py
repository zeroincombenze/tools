#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# import os
import argparse
from random import random, randint
import vatnumber


__version__ = "2.0.12"


def gen_vatnumber(opt_args):
    found = False
    while not found:
        seed = "%7.7s%3.03i" % (random() * 10000000, randint(1, 99))
        for i in range(10):
            vat = "%s%s%s" % (opt_args.iso, seed, i)
            if vatnumber.check_vat_it(vat):
                found = True
                break
    print(vat)
    return 0


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Generate random VAT number", epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument("-i", "--iso", default="IT")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-w", "--what", help="Kind of code: mey be vat")
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if opt_args.what == "vat":
        return gen_vatnumber(opt_args)
    else:
        print("Invalid kind of code!")
    return sts


if __name__ == "__main__":
    exit(main())

