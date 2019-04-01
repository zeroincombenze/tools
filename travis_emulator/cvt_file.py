#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import os
import sys
try:
    from z0lib import z0lib
except ImportError:
    import z0lib


__version__ = "0.2.2.4"


def parse_source(source):
    return source


def parse_file(ctx):
    if not os.path.isfile(ctx['src_file']):
            raise IOError('File %s not found' % ctx['src_file'])
    if ctx['opt_verbose']:
        print("Reading %s" % ctx['src_file'])
    fd = open(ctx['src_file'], 'rb')
    source = fd.read()
    fd.close()
    target = parse_source(source)
    if source == target:
        if ctx['opt_verbose']:
            print("No change done")
    else:
        if ctx['dst_file'] and ctx['dst_file'] != ctx['src_file']:
            if ctx['opt_verbose']:
                print("Reading %s" % ctx['dst_file'])
            fd = open(ctx['dst_file'], 'w')
            fd.write(target)
            fd.close()
        else:
            if ctx['opt_verbose']:
                print("Reading %s" % ctx['src_file'])
            tmpfile = '%s.tmp' % ctx['dst_file']
            bakfile = '%s.bak' % ctx['dst_file']
            fd = open(tmpfile, 'w')
            fd.write(target)
            fd.close()
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            os.rename(ctx['src_file'], bakfile)
            os.rename(tmpfile, ctx['dst_file'])


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Convert file",
                                "© 2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    sts = parse_file(ctx)
    sys.exit(sts)
