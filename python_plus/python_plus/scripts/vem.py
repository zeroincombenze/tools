#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    cmd = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..',
                     '%s.sh' % os.path.basename(__file__)[0: -3]))
    if not os.path.isfile(cmd):
        print('Internal package error: file %s not found!' % cmd)
    for arg in cli_args:
        if ' ' in arg:
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
    return os.system(cmd)
