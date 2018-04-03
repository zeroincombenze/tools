#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys
import os
import z0lib


__version__ = '0.3.6.11'


REQVERSION = {
    'astroid': '==1.4.8',
    'Babel': '==2.3.4',
    'decorator': '==3.4.0',    # Warning! 10.0 require 4.0.10
    'docutils': '==0.12',
    'ebaysdk': '==2.1.4',
    'feedparser': '==5.1.3',   # Warning! 10.0 require 5.2.1
    'gevent': '==1.0.2',       # Warning! 10.0 require 1.1.2
    'greenlet': '==0.4.10',
    'jcconv': '==0.2.3',
    'Jinja2': '==2.7.3',       # Warning! 10.0 require 2.8
    'lxml': '==3.5.0',
    'Mako': '==1.0.4',
    'MarkupSafe': '==0.23',
    'mock': '==2.0.0',
    'ofxparse': '==0.16',
    'passlib': '==1.6.2',      # Warning! 10.0 require 1.6.5
    'Pillow': '==3.4.2',       # Warning! 10.0 require 3.4.1
    'psutil': '==4.3.1',
    'psycogreen': '==1.0',
    'psycopg2': '==2.6.2',
    'pygments': '==2.0.2',
    'pydot': '==1.2.3',
    'pylint': '==1.6.4',
    'pylint-plugin-utils': '==0.3.5.11',
    'pyparsing': '<2',         # Warning! 10.0 require 2.1.10
    'pyPdf': '==1.13',
    'pyserial': '==3.1.1',
    'Python-Chart': '==1.39',
    'python-dateutil': '==2.5.3',
    'python-ldap': '==2.4.27',
    'python-openid': '==2.2.5',
    'pytz': '==2016.7',
    'pyusb': '>=1.0.0b1',      # Warning! 10.0 require 1.0.0
    'pyxb': '==1.2.4',
    'PyYAML': '==3.12',
    'qrcode': '==5.3',
    'reportlab': '==3.1.44',   # Warning! 10.0 require 3.3.0
    'requests': '==2.11.1',
    'restructuredtext_lint': '==0.12.2',
    'six': '==1.10.0',
    'suds-jurko': '==0.6',
    'vatnumber': '==1.2',
    'vobject': '==0.9.3',
    'Werkzeug': '==0.11.11',
    'wkhtmltopdf': '==0.12.1',
    'wsgiref': '==0.1.2',
    'XlsxWriter': '==0.9.3',
    'xlwt': '==1.1.2',
    'xlrd': '==1.0.0',
}
REQVERSION_10 = {
    'astroid': '==1.4.8',
    'Babel': '==2.3.4',
    'decorator': '==4.0.10',
    'docutils': '==0.12',
    'ebaysdk': '==2.1.4',
    'feedparser': '==5.2.1',
    'gevent': '==1.1.2',
    'greenlet': '==0.4.10',
    'jcconv': '==0.2.3',
    'Jinja2': '==2.8',
    'lxml': '==3.5.0',
    'Mako': '==1.0.4',
    'MarkupSafe': '==0.23',
    'mock': '==2.0.0',
    'ofxparse': '==0.16',
    'passlib': '==1.6.5',
    'Pillow': '==3.4.1',
    'psutil': '==4.3.1',
    'psycogreen': '==1.0',
    'psycopg2': '==2.6.2',
    'pygments': '==2.0.2',
    'pydot': '==1.2.3',
    'pylint': '==1.6.4',
    'pylint-plugin-utils': '==0.3.5.11',
    'pyparsing': '==2.1.10',
    'pyPdf': '==1.13',
    'pyserial': '==3.1.1',
    'Python-Chart': '==1.39',
    'python-dateutil': '==2.5.3',
    'python-ldap': '==2.4.27',
    'python-openid': '==2.2.5',
    'pytz': '==2016.7',
    'pyusb': '==1.0.0',
    'pyxb': '==1.2.4',
    'PyYAML': '==3.12',
    'qrcode': '==5.3',
    'reportlab': '==3.3.0',
    'requests': '==2.11.1',
    'restructuredtext_lint': '==0.12.2',
    'six': '==1.10.0',
    'suds-jurko': '==0.6',
    'vatnumber': '==1.2',
    'vobject': '==0.9.3',
    'Werkzeug': '==0.11.11',
    'wkhtmltopdf': '==0.12.1',
    'wsgiref': '==0.1.2',
    'XlsxWriter': '==0.9.3',
    'xlwt': '==1.1.2',
    'xlrd': '==1.0.0',
}
ALIAS = {
    'dateutil': 'python-dateutil',
    'stdnum': 'python-stdnum',
    'ldap': 'python-ldap',
    'openid': 'python-openid',
    'usb': 'pyusb',
}
PIP_TEST_PACKAGES = ['astroid',
                     'click',
                     'coveralls',
                     'flake8',
                     'lazy_object_proxy',
                     'mock',
                     'pylint',
                     # 'pylint-plugin-utils',
                     'PyYAML',
                     'QUnitSuite',
                     'restructuredtext_lint',
                     'unittest2',
                     'wrapt',
                     'zerobug',
                     ]
BIN_TEST_PACKAGES = ['expect-dev',
                     'python-dev',
                     'python-setuptools',
                     ]
RPC_PACKAGES = ['odoorpc',
                'oerplib',
                'os0',
                ]
PIP_BASE_PACKAGES = ['Babel',
                     'configparser',
                     'decorator',
                     'docutils',
                     'feedparser',
                     'gevent',
                     'Jinja2',
                     'lxml',
                     'Mako',
                     'passlib',
                     'Pillow',
                     'psutil',
                     'psycogreen',
                     'psycopg2',
                     'psycopg2-binary',
                     'Python-Chart',
                     'python-dateutil',
                     'python-openid',
                     'pydot',
                     'pyparsing',
                     'pypdf',
                     'pyserial',
                     'pytz',
                     'reportlab',
                     'vatnumber',
                     'Werkzeug',
                     ]
BIN_BASE_PACKAGES = ['simplejson',
                     'python-ldap',
                     'wkhtmltopdf',
                     ]


def parse_requirements(reqfile):
    reqlist = []
    for line in reqfile:
        if line and line[0] != '#':
            reqlist.append(line)
    return reqlist


def name_n_version(item, with_version=None, odoo_ver=None):
    versioned = False
    item = os.path.basename(item).split('.')[0]
    if item in ALIAS:
        item = ALIAS[item]
    if odoo_ver == '10.0':
        if with_version and item in REQVERSION_10:
            item = '%s%s' % (item, REQVERSION_10[item])
            versioned = True
    else:
        if with_version and item in REQVERSION:
            item = '%s%s' % (item, REQVERSION[item])
            versioned = True
    return item, versioned


def add_package(deps_list, kw, item, with_version=None, odoo_ver=None):
    full_item, versioned = name_n_version(item,
                                          with_version=with_version,
                                          odoo_ver=odoo_ver)
    if kw == 'python' and versioned:
        kw = 'python2'
    if full_item not in deps_list[kw]:
        deps_list[kw].append(full_item)
    return deps_list


def package_from_list(deps_list, kw, PKG_LIST,
                      with_version=None, odoo_ver=None):
    for item in PKG_LIST:
        deps_list = add_package(deps_list, kw, item,
                                with_version=with_version,
                                odoo_ver=odoo_ver)
    return deps_list


def package_from_manifest(deps_list, manifest_file,
                          with_version=None, odoo_ver=None):
    if manifest_file:
        manifest = ast.literal_eval(open(manifest_file).read())
        if manifest.get('external_dependencies'):
            deps = manifest['external_dependencies']
            for kw in ('python', 'bin'):
                if deps.get(kw):
                    for item in deps[kw]:
                        deps_list = add_package(deps_list,
                                                kw,
                                                item,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
    return deps_list


def add_manifest(root, manifests, files):
    for f in files:
        if f == '__openerp__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
        elif f == '__manifest__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
    return manifests


def main():
    # global __version__
    parser = z0lib.parseoptargs("List Odoo requirements",
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument("-B", "--base-packages",
                        help="Add base packages",
                        action="store_true",
                        dest="base_pkgs")
    parser.add_argument("-m", "--manifest",
                        help="Declare manifest files if no path supplied",
                        dest="manifests",
                        metavar="file list",
                        default="")
    parser.add_argument('-n')
    parser.add_argument("-o", "--output",
                        help="Write output to file requirements.txt",
                        dest="out_file",
                        action="store_true")
    parser.add_argument("-p", "--path",
                        help="Path to search manifest files",
                        dest="odoo_dir",
                        metavar="directory",
                        default="")
    parser.add_argument("-O", "--oca-dependencies-path",
                        help="Follow oca_dependencies.txt in directory",
                        metavar="directory",
                        dest="oca_dependencies")
    parser.add_argument("-P", "--precise",
                        help="Add version to filename",
                        action="store_true",
                        dest="with_version")
    parser.add_argument('-q')
    parser.add_argument("-R", "--rpc-packages",
                        help="Add packages to use xmlrpc/jsonrpc",
                        action="store_true",
                        dest="rpc_pkgs")
    parser.add_argument("-s", "--sep",
                        help="Separator character of list",
                        dest="sep",
                        metavar="character",
                        default=",")
    parser.add_argument("-t", "--type",
                        help="Type of files; may be bin,python or both",
                        dest="itypes",
                        metavar="keyword",
                        default="both")
    parser.add_argument("-T", "--tests-packages",
                        help="Add packages to test",
                        action="store_true",
                        dest="test_pkgs")
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if ctx['out_file']:
        if not ctx['odoo_dir']:
            print "Please, declare odoo path to write requirements.txt file!"
            sys.exit(1)
        ctx['sep'] = '\n'
        ctx['with_version'] = True
        ctx['itypes'] = 'python'
        ctx['opt_verbose'] = False
        ctx['base_pkgs'] = False
        ctx['rpc_pkgs'] = False
        ctx['test_pkgs'] = False
        ctx['oca_dependencies'] = False
        ctx['opt_fn'] = '/'.join([ctx['odoo_dir'], 'requirements.txt'])
    if ctx['odoo_dir']:
        manifests = []
        if ctx['oca_dependencies']:
            for root, dirs, files in os.walk(ctx['oca_dependencies'],
                                             followlinks=True):
                manifests = add_manifest(root, manifests, files)
        for root, dirs, files in os.walk(ctx['odoo_dir']):
            manifests = add_manifest(root, manifests, files)
    else:
        manifests = ctx['manifests'].split(',')
    deps_list = {}
    for kw in ('python', 'python2', 'bin'):
        deps_list[kw] = []
    if ctx['base_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_BASE_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_BASE_PACKAGES,
                                      with_version=False,
                                      odoo_ver=ctx['odoo_ver'])
    if ctx['test_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_TEST_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_TEST_PACKAGES,
                                      with_version=False,
                                      odoo_ver=ctx['odoo_ver'])
    if ctx['rpc_pkgs']:
        deps_list = package_from_list(deps_list, 'python', RPC_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
    for manifest_file in manifests:
        deps_list = package_from_manifest(deps_list,
                                          manifest_file,
                                          with_version=ctx['with_version'],
                                          odoo_ver=ctx['odoo_ver'])
    if ctx['out_file']:
        try:
            pkgs = open(ctx['opt_fn']).read().split('\n')
        except BaseException:
            pkgs = []
        for kw in ('python', 'python2'):
            for p in deps_list[kw]:
                if p not in pkgs:
                    pkgs.append(p)
        if len(pkgs):
            fd = open(ctx['opt_fn'], 'w')
            fd.write(ctx['sep'].join(pkgs))
            fd.close()
        print "Updated %s file" % ctx['opt_fn']
        print ctx['sep'].join(pkgs)
    else:
        deps_list['python'] = deps_list['python'] + deps_list['python2']
        for kw in ('python', 'bin'):
            if (ctx['itypes'] == 'both' or
                    kw == ctx['itypes']) and kw in deps_list:
                if ctx['opt_verbose']:
                    print '%s=%s' % (kw, ctx['sep'].join(deps_list[kw]))
                else:
                    print ctx['sep'].join(deps_list[kw])


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
