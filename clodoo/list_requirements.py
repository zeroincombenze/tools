#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys
import os
import re
import z0lib


__version__ = '0.3.6.23'

"""
pip_pkgver__lxml=3.4.1
pip_pkgver__mako=1.0.1
pip_pkgver__mock=1.0.1
pip_pkgver__passlib=1.6.2
pip_pkgver__pillow=2.7.0
pip_pkgver__psutil=2.2.0
pip_pkgver__psycogreen=1.0
pip_pkgver__psycopg2=2.5.4
pip_pkgver__pydot=1.0.2
pip_pkgver__pyparsing=2.0.3
pip_pkgver__pypdf=1.13
pip_pkgver__pyserial=2.7
pip_pkgver__python-dateutil=2.4.0
pip_pkgver__python-ldap=2.4.19
pip_pkgver__python-openid=2.2.5
pip_pkgver__pytz=2014.10
pip_pkgver__pyusb=1.0.0b2
pip_pkgver__pyyaml=3.11
pip_pkgver__qrcode=5.1
pip_pkgver__reportlab=3.1.44
pip_pkgver__requests=2.6.0
pip_pkgver__simplejson=3.5.3
pip_pkgver__six=1.9.0
pip_pkgver__unittest2=0.5.1
pip_pkgver__vatnumber=1.2
pip_pkgver__werkzeug=0.9.6
pip_pkgver__xlwt=0.7.5

pip_pkgver__pylint=1.6.4
pip_pkgver__pylint-plugin-utils=0.2.4
pip_pkgver__pygments=2.0.2
pip_pkgver__restructuredtext_lint=0.12.2
pip_pkgver__unidecode=0.04.17
pip_pkgver__pyxb=1.2.4
"""
REQVERSION = {
    'astroid': {'7.0': '==1.4.8'},
    'Babel': {'7.0': '==1.3', '8.0': '==2.3.4'},
    'decorator': {'7.0': '==3.4.0', '10.0': '==4.0.10'},
    'docutils': {'7.0': '==0.12'},
    'ebaysdk': {'7.0': '==2.1.4'},
    'feedparser': {'7.0': '==5.1.3', '10.0': '==5.2.1'},
    'gdata': {'7.0': '=2.0.18'},
    'gevent': {'7.0': '==1.0.2', '10.0': '==1.1.2'},
    'Jinja2': {'7.0': '==2.7.3', '10.0': '==2.8'},
}
REQVERSION7 = {
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
    'psycopg2': '>=2.0.0',     # Warning! 10.0 require 2.6.2
    'pygments': '==2.0.2',
    'pydot': '==1.2.3',
    'pylint': '==1.6.4',
    'pylint-plugin-utils': '==0.3.5.11',
    'pyparsing': '<2',         # Warning! 10.0 require 2.1.10
    'pyPdf': '==1.13',
    'pyserial': '==3.1.1',
    'Python-Chart': '==1.39',
    'python-dateutil': '==2.5.3',
    'python-ldap': '==2.4.25',
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
    'flake8': '==3.4.1',
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
    'python-ldap': '==2.4.25',     # warning OCA declare 2.4.27!?
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
    'lxml': 'lxml',
}
PIP_TEST_PACKAGES = ['astroid',
                     'click',
                     'coveralls',
                     'flake8',
                     'lazy_object_proxy',
                     'MarkupSafe',
                     'mock',
                     'pbr',
                     'pylint',
                     'pylint-mccabe',
                     'pylint_odoo',
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
RPC_PACKAGES = ['clodoo',
                'odoorpc',
                'oerplib',
                'os0',
                ]
PIP_BASE_PACKAGES = ['Babel',
                     'configparser',
                     'decorator',
                     'docutils',
                     'feedparser',
                     'gdata',
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
                     'stdnum',
                     'vatnumber',
                     'Werkzeug',
                     ]
BIN_BASE_PACKAGES = ['simplejson',
                     'python-ldap',
                     'wkhtmltopdf',
                     ]


def parse_requirements(reqfile):
    lines = open(reqfile).read().split('\n')
    reqlist = []
    for line in lines:
        if line and line[0] != '#':
            items = line.split(';')
            if len(items) == 1 or eval(items[1].strip().replace('_','.')):
                reqlist.append(items[0].strip())
    return reqlist


def name_n_version(full_item, with_version=None, odoo_ver=None):
    item = re.split('[!=<>]', full_item)
    if len(item) == 1:
        full_item = ''
    item = item[0]
    # item = os.path.basename(item).split('.')[0]
    item = os.path.basename(item)
    itm = item.plit('.')[0]
    if itm in ALIAS:
        item = ALIAS[itm]
    defver = False
    if with_version:
        if full_item:
            pass
        elif odoo_ver in ('10.0', '11.0'):
            if item in REQVERSION_10:
                full_item = '%s%s' % (item, REQVERSION_10[item])
                defver = True
        else:
            if with_version and item in REQVERSION7:
                full_item = '%s%s' % (item, REQVERSION7[item])
                defver = True
    return item, full_item, defver


def add_package(deps_list, kw, item, with_version=None, odoo_ver=None):
    item, full_item, defver = name_n_version(item,
                                             with_version=with_version,
                                             odoo_ver=odoo_ver)
    if item == 'cups':
        kw = 'bin'
    if item not in deps_list[kw]:
        deps_list[kw].append(item)
        if kw == 'python':
            if full_item:
                kw = 'python2'
                deps_list[kw].append(full_item)
            else:
                kw = 'python1'
                deps_list[kw].append(item)
            if item == 'barcode':
                deps_list = add_package(deps_list, kw,
                                        'python-Levenshtein',
                                        with_version=with_version,
                                        odoo_ver=odoo_ver)
    elif kw == 'python' and full_item:
        if item in deps_list['python1']:
            i = deps_list['python1'].index(item)
            del deps_list['python1'][i]
            deps_list['python2'].append(full_item)
        elif not defver:
            print 'Version mismatch: package %s' % full_item
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
        if manifest.get('depends'):
            deps = manifest['depends']
            kw = 'modules'
            for item in deps:
                deps_list = add_package(deps_list,
                                        kw,
                                        item,
                                        with_version=with_version,
                                        odoo_ver=odoo_ver)
    return deps_list


def add_manifest(root, manifests, reqfiles, files):
    for f in files:
        if f == '__openerp__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
        elif f == '__manifest__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
        elif f == 'requirements.txt':
            ffn = os.path.join(root, f)
            reqfiles.append(ffn)
    return manifests, reqfiles


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
                        help="Path where search manifest files",
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
                        help="Type of files; may be bin,python,both or modules",
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
        reqfiles = []
        if ctx['oca_dependencies']:
            for cdir in ctx['oca_dependencies'].split(','):
                for root, dirs, files in os.walk(cdir,
                                                 followlinks=True):
                    manifests, reqfiles = add_manifest(root,
                                                       manifests,
                                                       reqfiles,
                                                       files)
        for root, dirs, files in os.walk(ctx['odoo_dir']):
            manifests, reqfiles = add_manifest(root,
                                               manifests,
                                               reqfiles,
                                               files)
    else:
        manifests = ctx['manifests'].split(',')
        reqfiles = []
    deps_list = {}
    for kw in ('python', 'python1', 'python2', 'bin', 'modules'):
        deps_list[kw] = []
    for reqfile in reqfiles:
        requirements = parse_requirements(reqfile)
        deps_list = package_from_list(deps_list, 'python', requirements,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
    for manifest_file in manifests:
        deps_list = package_from_manifest(deps_list,
                                          manifest_file,
                                          with_version=ctx['with_version'],
                                          odoo_ver=ctx['odoo_ver'])
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
    if ctx['out_file']:
        try:
            pkgs = open(ctx['opt_fn']).read().split('\n')
        except BaseException:
            pkgs = []
        for kw in ('python1', 'python2'):
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
        deps_list['python'] = deps_list['python1'] + deps_list['python2']
        for kw in ('python', 'bin', 'modules'):
            if kw in deps_list:
                if kw == ctx['itypes'] or (ctx['itypes'] == 'both' and
                        kw in ('python', 'bin')):
                    if ctx['opt_verbose']:
                        print '%s=%s' % (kw, ctx['sep'].join(deps_list[kw]))
                    else:
                        print ctx['sep'].join(deps_list[kw])


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
