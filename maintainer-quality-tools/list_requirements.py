#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys
import os
import z0lib


__version__ = '0.1.1'


def print_deps(manifest_file, deps_list=None):
    deps_list = deps_list or {}
    if manifest_file:
        manifest = ast.literal_eval(open(manifest_file).read())
        if manifest.get('external_dependencies'):
            deps = manifest['external_dependencies']
            for kw in ('python', 'bin'):
                if deps.get(kw):
                    if kw not in deps_list:
                        deps_list[kw] = []
                    for item in deps[kw]:
                        if item not in deps_list[kw]:
                            deps_list[kw].append(item)
    return deps_list


def main():
    # global __version__
    parser = z0lib.parseoptargs("List Odoo reuirements",
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-p", "--path",
                        help="Path to search manifest files",
                        dest="odoo_dir",
                        metavar="directory",
                        default="")
    parser.add_argument("-m", "--manifest",
                        help="Manifest files",
                        dest="manifests",
                        metavar="file list",
                        default="")
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    deps_list = {}
    if ctx['odoo_dir']:
        manifests = []
        for root, dirs, files in os.walk(ctx['odoo_dir']):
            for f in files:
                if f == '__openerp__.py':
                    ffn = '%s/%s' % (root, f)
                    manifests.append(ffn)
                elif f == '__manifest__.py':
                    ffn = '%s/%s' % (root, f)
                    manifests.append(ffn)
    else:
        manifests = ctx['manifests'].split(',')
    for manifest_file in manifests:
        deps_list = print_deps(manifest_file, deps_list=deps_list)
    for kw in ('python', 'bin'):
        if kw in deps_list:
            print ','.join(deps_list[kw])


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
