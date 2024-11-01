#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from z0lib import z0lib


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    cmd = "%s.sh" % os.path.splitext(os.path.abspath(__file__))[0]
    if not os.path.isfile(cmd):
        # search for script into upper path
        cmd = os.path.split(cmd)
        cmd = os.path.join(os.path.dirname(cmd[0]), cmd[1])
    if not os.path.isfile(cmd):
        print("Internal package error: file %s not found!" % cmd)
        return 126
    return z0lib.os_system([cmd] + cli_args, with_shell=True, rtime=True)


if __name__ == "__main__":
    exit(main())
