#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    cmd = '%s.sh' % os.path.splitext(os.path.abspath(__file__))[0]
    if not os.path.isfile(cmd):
        cmd = os.path.split(cmd)
        cmd = os.path.join(os.path.dirname(cmd[0]), cmd[1])
    if not os.path.isfile(cmd):
        print('Internal package error: file %s not found!' % cmd)
    for arg in cli_args:
        if '<' in arg or '>' in arg:
            arg = "'%s'" % arg.replace("'", r"\'")
        elif ' ' in arg:
            if '"' in arg:
                arg = '"%s"' % arg.replace('"', r'\"')
            else:
                arg = '"%s"' % arg
        elif '"' in arg:
            arg = '"%s"' % arg.replace('"', r'\"')
        elif "'" in arg:
            arg = '"%s"' % arg
        else:
            arg = '%s' % arg
        cmd = '%s %s' % (cmd, arg)
    return subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    exit(main())
