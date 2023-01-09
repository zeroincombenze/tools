#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

__version__ = '2.0.4'


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Manage Odoo repositories",
        epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument("-B", "--debug", action="count", default=0)
    parser.add_argument("-b", "--odoo-branch",
                        dest="odoo_branch",
                        default="12.0",
                        help="default Odoo version")
    # parser.add_argument("-C", "--config",
    #                     help="Configuration file")
    parser.add_argument("-c", "--odoo-config",
                        help="Odoo configuration file")
    parser.add_argument("-d", "--database")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="force copy/build")
    parser.add_argument("-k", "--keep",
                        action="store_true",
                        help="keep data after action")
    parser.add_argument("-m", "--missing",
                        action="store_true",
                        help="show missing line after test")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-p", "--target-path",
                        help="Local directory")
    parser.add_argument("-q", "--quiet",
                        action="store_false",
                        dest="verbose",
                        help="silent mode")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-y", "--assume-yes", action="store_true")
    parser.add_argument("action",
                        nargs="?")
    parser.add_argument("sub1",
                        nargs="?")
    parser.add_argument("sub2",
                        nargs="?")
    parser.parse_args(cli_args)

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
    return os.system(cmd)


if __name__ == "__main__":
    exit(main())
