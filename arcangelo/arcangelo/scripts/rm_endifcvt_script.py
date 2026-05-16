#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re


def process(source):
    if not os.path.exists(source):
        print("Source does not exist")
        return -1
    target = ""
    with open(source, "r") as fd:
        lines = fd.readlines()
        for line in lines:
            if re.match("^ *# *end[_\- ]\w+", line):
                continue
            target += line
    if target:
        print("File %s processed" % source)
        with open(source, "w") as fd:
            fd.write(target)

def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    source = ""
    for arg in cli_args:
        if not arg.startswith("-"):
            source = arg
    return process(source)

if __name__ == "__main__":
    exit(main())
