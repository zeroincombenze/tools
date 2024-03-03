#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software manages 4 lists:
# list['python'] -> Result list
# list['python1'] -> is the list with packages w/o version
# list['python2'] -> is the list with versioned packages
#
from __future__ import print_function, unicode_literals
# from future.utils import PY2, PY3

import ast
import os
import re
import sys
from subprocess import PIPE, Popen

try:
    from python_plus import python_plus
except ImportError:
    import python_plus
try:
    from z0lib import z0lib
except ImportError:
    import z0lib


__version__ = "2.0.12"
python_version = "%s.%s" % (sys.version_info[0], sys.version_info[1])

#
# Here we assume:
#   Odoo 11.0 use python 3.6, Odoo 12.0 -> 3.7, Odoo 14.0 -> 3.8 Odoo 16.0 -> 3.9
# If version is 2.7 or 3.5 or 3.6 or 3.7 or 3.8 or 3.9 then it refers to python version
REQVERSION = {
    "acme_tiny": {"6.1": ">=4.0.3"},
    "argparse": {"0": "==1.2.1"},
    # "astroid": {"2.7": "==1.6.5", "3.5": "==2.2.0"},  # Version by test pkgs
    "astroid": {"2.7": "==1.6.5", "3.5": "==2.11.7"},  # Version by test pkgs
    "autopep8": {"0": "==1.2"},
    "Babel": {"6.1": "==1.3", "8.0": "==2.3.4", "16.0": ">=2.6.0,<=2.9.1"},
    "beautifulsoup": {"6.1": "==3.2.1"},
    "bokeh": {
        "10.0": "bokeh<1.4.0",
        "11.0": "==0.12.7",
        "12.0": "==1.1.0",
        "14.0": "==2.3.1",
        "15.0": "2.4.2"
    },
    "codicefiscale": {"6.1": "==0.9"},
    "coverage": {"2.7": "<5.6.0", "3.5": ">=5.0.0"},
    "cryptography": {"2.7": ">=2.2.2,<3.4", "3.7": ">=23.0,<38.0"},
    "decorator": {"6.1": "==3.4.0", "10.0": "==4.0.10"},
    # "docutils": {"0": "==0.14", "6.1": "==0.12", "3.7": "==0.16"},
    "docutils": {"0": "==0.16"},       # By test pkgs
    "ebaysdk": {"6.1": "==2.1.4"},
    "email_validator": {"10.0": "<1.3.0", "12.0": ">=1.3"},
    "ERPpeek": {"0": "==1.6.1"},
    "feedparser": {"6.1": "==5.1.3", "10.0": "==5.2.1"},
    "flake8": {
        "2.7": "<4.0.0",     # <<Tested 3.5.0; 3.6.0 does not work>>
        "3.6": ">=4.0.0",
    },
    "gdata": {"6.1": "==2.0.18"},
    "gevent": {
        "6.1": "==1.0.1",                # by odoo documentation
        "7.0": "==1.0.2",                # by odoo documentation
        "10.0": ">=1.1.2,<=1.4.0",       # by odoo + gevent documentation + test
        "11.0": "==1.5.0",               # by odoo documentation
        "12.0": ">=1.5.0,<=21.12.0",     # https://github.com/gevent/gevent/issues/1899
        "14.0": ">=20.9.0,<=22.10.99",   # by odoo + gevent documentation
        "15.0": "PYVER",
        "3.7": ">=22.10.0,<=22.10.99",
    },
    "greenlet": {
        "6.1": "==0.4.2",
        "7.0": ">=0.4.7,<=0.4.10",       # by odoo documentation + test
        "3.7": ">=0.4.13",
    },
    "importlib-metadata": {"3.7": "==4.8.3"},
    "ipy": {"6.1": ">=0.83"},
    "isort": {"0": "==4.3.4"},  # Version by test pkgs
    "jcconv": {"6.1": "==0.2.3"},
    "Jinja2": {"6.1": "==2.7.3", "9.0": "==2.8.1", "10.0": "==2.10.1"},
    "jupyter-server": {"0": "<1.20.0"},
    "lessc": {"0": ">=3.0.0"},
    "lxml": {
        "6.1": "<=3.3.5",
        "7.0": ">=3.3.5,<=3.4.1",
        "9.0": ">=3.4.1,<=3.4.4",
        "10.0": ">=3.5.0,<=3.6.4",
        "14.0": ">=4.5.0",
        "15.0": ">=4.6.5",
        "3.6": "==3.7.1",
        "3.7": ">=4.2.3,<=4.6.5",
        "3.8": ">=4.6.1,<=4.6.5",
        "3.10": "==4.9.2",
    },
    "mccabe": {"0": "<0.7.0,>=0.6.0"},
    "Mako": {
        "6.1": "==1.0.0", "7.0": "==1.0.1", "8.0": "==1.0.4", "10.0": ">=1.0.4",
    },
    "MarkupSafe": {"6.1": "==0.23", "14.0": "==1.1.0", "0": "<2.1.0"},  # Tested 1.0
    "matplotlib": {
        "10.0": "==3.0.3",
        # "13.0": "==3.4.1",
        "3.6": "==3.0.3",
        # "3.7": "==3.4.1"
        "3.7": "<3.3.0"     # Experimental!
    },
    "mock": {"6.1": "==1.0.1", "8.0": "==2.0.0"},
    "nbconvert": {"0": "==6.0.7"},
    "odoo_score": {"6.1": "==1.0.1", "10.0": ">=2.0.0"},
    "ofxparse": {"6.1": "==0.16"},
    "pandas": {"3.7": ">=0.22.0,<=1.1.0"},
    "passlib": {"6.1": "==1.6.2", "10.0": "==1.6.5", "16.0": ">=1.7.0"},
    "Pillow": {
        "6.1": "==3.4.1",
        "7.0": "==3.4.2",
        "8.0": "==3.4.1",
        "11.0": "==4.0.0",
        "15.0": ">=7.0.0",
        "3.6": "==4.0.0",
        "3.7": "==6.1.0",
        "3.8": ">=6.2.1",
    },
    "psutil": {"6.1": "==2.1.1", "7.0": "==2.2.0", "8.0": "==4.3.1"},
    "psycogreen": {"6.1": "==1.0"},
    "psycopg2-binary": {
        "6.1": ">=2.0.0,<2.7.3.3",
        "8.0": ">=2.5.4,<2.8.0",
        "10.0": ">=2.7.4",
        "12.0": ">=2.8.3",
        "0": ">=2.7.4",
    },
    # "pycodestyle": {"0": "==2.3.1"},
    "pydot": {"6.1": "==1.0.2", "8.0": "==1.2.3"},
    # "pyflakes": {"0": "pyflakes<1.6.0,>=1.5.0"},
    "Pygments": {
        "10.0": "==2.2.0",
        "3.5": ">=2.7.0"
    },
    "pygount": {"3.7": "==1.2.0"},
    "pylint": {
        "2.7": "<2.0.0",
        "3.5": "<2.7.0",
        "3.6": "<2.14.0",
        "3.7": "<2.15.0",
    },
    "pylint-odoo": {
        "6.1": "<3.0.0",        # to match lxml
        "11.0": "PYVER",
        "13.0": ">=3.3.1",      # from pypi documentation
        "15.0": ">=5.0.1",      # from pypi documentation
        "16.0": ">=7.0.0",      # from pypi documentation
        "3.5": "<=8.0.0",
        "3.8": ">=3.5.0,<=8.0.0",
    },
    "pylint-plugin-utils": {
        "2.7": "==0.2.6",
        "3.5": "==0.5",
        "3.6": ">=0.7",
    },
    "pyOpenSSL": {"0": ">=16.2.0,<19.0", "3.9": ">=16.2.0,<23.0"},
    "pyotp": {"2.7": "==2.3.0", "3.5": ">=2.4.0"},
    "pyPDF2": {"2.7": "==1.28.4", "3.5": "<2.0"},
    "pysftp": {"6.1": ">=0.2.9"},
    "pyparsing": {"6.1": "==1.5.7", "7.0": "==2.0.3", "10.0": "==2.1.10"},
    "pyPdf": {"6.1": "==1.13"},
    "pyserial": {"6.1": "==2.7", "10.0": ">=3.1.1"},
    "Python-Chart": {"6.1": "==1.39"},
    "python-dateutil": {
        "6.1": "==1.5", "7.0": "==2.4.0", "8.0": "==2.5.3", "11.0": "==2.5.3"
    },
    "python-ldap": {
        "6.1": "==2.4.15",
        "7.0": "==2.4.19",
        "10.0": "==2.4.27",
        "11.0": "==2.5.28",
        "13.0": "==3.1.0",
    },
    "python-openid": {"6.1": "==2.2.5"},
    "python-stdnum": {"6.1": ">=1.8.1"},
    "pytz": {"6.1": ">=2014.10", "10.0": ">=2016.7"},
    # check for: Odoo requires >=1.0.0b1, but it does conflict with other packges
    "pyusb": {"6.1": ">=1.0.0b1", "10.0": "==1.0.0", "16.0": ">=1.0.0b1"},
    "pyxb": {"6.1": "==1.2.4", "8.0": "==1.2.5", "12.0": "==1.2.6"},
    "PyWebDAV": {"6.1": "<0.9.8"},
    "PyYAML": {"6.1": "==3.11", "8.0": "==3.12", "3.7": "==3.13", "3.9": "==6.0"},
    "qrcode": {"6.1": "==5.0.1", "7.0": "==5.1", "10.0": "==5.3"},
    "readme-renderer" : {"2.7": "<25.0", "3.5": "<29.0", "3.6": ">=30.0"},
    "restructuredtext_lint": {"6.1": "==0.12.2", "0": "==1.1.3"},
    "reportlab": {"6.1": "==3.1.44", "10.0": "==3.3.0"},
    "requests": {
        "6.1": "==2.6.0",
        "10.0": ">=2.11.1,<=2.20.0",
        "13.0": ">=2.11.1,<=2.21.0",
        "14.0": "<=2.25.1",
        "3.8": ">=2.22.0",
        "3.9": ">=2.25.1",
    },
    "sentry-sdk": {"0": "<1.12.0"},
    "simplejson": {"6.1": "==3.5.3", "10.0": ">=3.5.3"},
    "six": {"6.1": "==1.7.3", "7.0": "==1.9.0", "10.0": ">=1.10.0"},
    "Sphinx": {"2.7": "==1.2.3", "3.7": ">=2.4.0"},
    "suds": {"6.1": "==0.4"},
    "suds-jurko": {"6.1": "==0.6"},
    "translators": {"0": "<5.0.0"},
    "unicodecsv": {"6.1": ">=0.14.1"},
    "unidecode": {"6.1": "==0.4.17", "10.0": "<=1.2.0", "11.0": ">1.2.0"},
    "unittest2": {"6.1": "==0.5.1", "11.0": ">=1.0.0"},
    "urllib3": {"3.5": "<1.26"},
    "validate_email": {"6.1": ">=1.3"},
    "vatnumber": {"6.1": "==1.2"},
    "vobject": {"6.1": "==0.6.6", "7.0": "==0.9.3"},  # Tested 0.9.5
    "Werkzeug": {
        "6.1": "==0.9.6",
        "10.0": "==0.11.11",
        "11.0": "==0.11.15",
        "12.0": "==0.14.1",
        "14.0": "==0.16.1",
        "3.9": "==2.0.2",

    },
    "wkhtmltopdf": {"6.1": "==0.12.1", "10.0": "==0.12.4", "12.0": "==0.12.5"},
    "wok_code": {"6.1": "<2.0.6", "10.0": ">=2.0.0"},
    "wsgiref": {"6.1": "==0.1.2"},
    "XlsxWriter": {"6.1": "==0.9.3"},  # Tested 1.0.2
    "xlrd": {"6.1": "==1.0.0"},
    "xlwt": {"6.1": "==0.7.5", "10.0": "==1.1.2", "12.0": "==1.3"},
    "z0bug_odoo": {"6.1": "==1.0.1", "10.0": ">=2.0.0"},
    "zeep": {"0": "==2.4.0"},
    "zerobug": {"6.1": "==1.0.1", "10.0": ">=2.0.0"},
}
ALIAS = {
    "babel": "Babel",
    "click": "Click",
    "crypto": "pycrypto",
    "crypto.cipher": "pycrypto",
    "dateutil": "python-dateutil",
    "gitpython": "GitPython",
    "jinja2": "Jinja2",
    "ldap": "python-ldap",
    "mako": "Mako",
    "markupsafe": "MarkupSafe",
    "openid": "python-openid",
    "openupgradelib": "openupgradelib@git+https://github.com/OCA/openupgradelib.git",
    "past": "future",
    "pillow": "Pillow",
    "psycopg2": "psycopg2-binary",
    "py-asterisk": "py-Asterisk",
    "pychart": "Python-Chart",
    "pypdf": "pyPdf",
    "pypdf2": "pyPDF2",
    "pygments": "Pygments",
    "pyldap": "python-ldap",  # pyldap is a fork!
    "python-chart": "Python-Chart",
    "python-docutils": "docutils",
    "python-levenshtein": "python-Levenshtein",
    "python-simplejson": "simplejson",
    "pywebdav": "PyWebDAV",
    "pyyaml": "PyYAML",
    "requests": "requests[security]",
    "qunitsuite": "QUnitSuite",
    "serial": "pyserial",
    "sphinx": "Sphinx",
    "stdnum": "python-stdnum",
    "usb": "pyusb",
    "werkzeug": "Werkzeug",
    "xlsxwriter": "XlsxWriter",
}
ALIAS3 = {
    "PyWebDAV": "PyWebDAV3",
    # "python-ldap": "pyldap",  # pyldap is a fork!
    "python-dev": "python3-dev",
    "python3-ldap": "ldap3",
    "jsonlib": "jsonlib-python3",
}
ALIAS_RHEL = {
    "build-essential": "groupinstall 'Development Tools'",
    "expect-dev": "expect-devel",
    "python-dev": "python-devel",
    "python3-dev": "python3-devel",
    "libcups2-dev": "cups-devel",
    "libevent-dev": "libevent-devel",
    "libffi-dev": "libffi-devel",
    "libgeos-dev": "geos-devel",
    "libldap2-dev": "openldap-devel",
    "libpq-dev": "postgresql-devel",
    "libsasl2-dev": "",
    "libssl-dev": "",
    "libxml2-dev": "libxml2-devel",
    "libxslt-dev": "libxslt-devel",
    "zlib1g": "epel-release --enablerepo=extras",
    "zlib1g-dev": "zlib-devel",
}
FORCE_ALIAS2 = {
    "docutils==0.12": "docutils==0.16",
    "pytz==2014.4": "pytz>=2014.4",
    "pytz==2014.10": "pytz>=2014.10",
    "pytz==2016.7": "pytz>=2016.7",
    "zeep==4.0.0": "zeep==2.4.0",
    "python-ldap": "python-ldap==3.1.0",
    "Mako==1.0.4": "Mako>=1.0.4",
    "rich": "rich<=12.0.0",
    "importlib-metadata": "importlib-metadata==4.8.3",
    "pygount": "pygount<=1.2.0",
    "pandas": "pandas>=0.22.0,<=1.1.0",
}
FORCE_ALIAS3 = {
    "docutils==0.12": "docutils==0.16",
    "pytz==2014.4": "pytz>=2014.4",
    "pytz==2014.10": "pytz>=2014.10",
    "pytz==2016.7": "pytz>=2016.7",
    "pytz==2019.3": "pytz>=2019.3",
    "zeep==4.0.0": "zeep==2.4.0",
    "python-ldap": "python-ldap==3.1.0",
    "Mako==1.0.4": "Mako>=1.0.4",
    "rich": "rich<=12.0.0",
    "importlib-metadata": "importlib-metadata==4.8.3",
    "pygount": "pygount<=1.2.0",
    "pandas": "pandas>=0.22.0,<=1.1.0",
}
PIP_SECURE_PACKAGES = [
    "urllib3[secure]",
    "cryptography",
    "pyOpenSSL",
    "idna",
    "certifi",
    "asn1crypto",
    "pyasn1",
]
PIP2_TEST_PACKAGES = [
    "astroid",
    "Click",
    "configparser",
    # "codecov",
    "coverage",
    # "coveralls",
    "docopt",
    "docutils",
    "flake8",
    "future",
    "GitPython",
    "isort",
    "lazy_object_proxy",
    "lxml",
    "MarkupSafe",
    "mock",
    "pbr",
    "polib",
    "pycodestyle",
    "pycparser",
    "pyflakes",
    "Pygments",
    "pylint",
    "pylint-mccabe",
    "pylint-odoo",
    "pylint-plugin-utils",
    "python-magic",
    "pyserial",
    "pytest",
    "PyWebDAV",
    "PyYAML",
    "QUnitSuite",
    "restructuredtext_lint",
    "rfc3986",
    "setuptools",
    "simplejson",
    "unittest2",
    "websocket-client",
    "whichcraft",
    "wrapt",
    "z0bug_odoo",
    "zerobug",
]
PIP3_TEST_PACKAGES = [
    "astroid",
    "Click",
    "configparser",
    # "codecov",
    "coverage",
    # "coveralls",
    "docopt",
    "docutils",
    "flake8",
    "future",
    "GitPython",
    "isort",
    "lazy_object_proxy",
    "lxml",
    "MarkupSafe",
    "mock",
    "pbr",
    "polib",
    "pycodestyle",
    "pycparser",
    "pyflakes",
    "Pygments",
    "pylint",
    "pylint-mccabe",
    "pylint-odoo",
    "pylint-plugin-utils",
    "python-magic",
    "pyserial",
    "pytest",
    "PyWebDAV",
    "PyYAML",
    "QUnitSuite",
    "restructuredtext_lint",
    "rfc3986",
    "setuptools",
    "simplejson",
    "translators",
    "unittest2",
    "websocket-client",
    "whichcraft",
    "wrapt",
    "z0bug_odoo",
    "zerobug",
]
BIN_TEST_PACKAGES = [
    "build-essential",
    "expect-dev",
    "libffi-dev",
    "libpq-dev",
    "libssl-dev",
    "python-dev",
    "python-setuptools",
]
RPC2_PACKAGES = ["clodoo", "odoorpc", "oerplib", "os0"]
RPC3_PACKAGES = ["clodoo", "odoorpc", "os0"]
PIP_BASE_PACKAGES = [
    "Babel",
    "chardet",
    "Click",
    "configparser",
    "decorator",
    "docutils",
    "feedparser",
    "future",
    "gdata",
    "gevent",
    "html2text",
    "Jinja2",
    "lxml",
    "Mako",
    "numpy",
    "passlib",
    "psutil",
    "psycogreen",
    "psycopg2-binary",
    "python-ldap",
    "python-dateutil",
    "python-openid",
    "python-plus",
    "pydot",
    "pyparsing",
    "simplejson",
    "six",
    "python-stdnum",
    # "vatnumber",
    # "wheel",
]
PIP3_BASE_PACKAGES = []
PIP_ODOO_BASE_PACKAGES = [
    "Babel",
    "chardet",
    "configparser",
    "decorator",
    "docutils",
    "feedparser",
    "future",
    "gdata",
    "gevent",
    "html2text",
    "Jinja2",
    "lessc; odoo_major>=10",
    "lxml",
    "Mako",
    "numpy",
    "num2words",
    "passlib",
    "Pillow",
    "psutil",
    "psycogreen",
    "psycopg2-binary",
    "Python-Chart",
    "python-ldap",
    "python-dateutil",
    "python-openid",
    "python-plus",
    "pydot",
    "pyparsing",
    "pyPdf",
    "pyPDF2",
    "pyserial",
    "pytz",
    "qrcode; odoo_major>=16",
    "reportlab",
    "simplejson",
    "six",
    "python-stdnum",
    "vatnumber",
    "Werkzeug",
    "zeep; odoo_major>=16"
]
BIN_BASE_PACKAGES = [
    "curl",
    "less-plugin-clean-css",
    "nodejs",
    "npm",
    "wkhtmltopdf",
    "zlib1g",
]
BIN_PACKAGES = [
    "git",
    "cups",
]
PIP_WITH_DOT = ["py3o.", "anybox."]
BUILTIN = ["csv"]
MANIFEST_NAMES = {
    "accept_language": "parse-accept-language",
    "Asterisk": "py-Asterisk",
    "cmislib": (
        "/--editable=git+https://github.com/apache/"
        "chemistry-cmislib.git@py3_compat#egg=cmislib"
    ),
    "Crypto.Cipher": "pycrypto",
    "facturx": "factur-x",
    "past": "future",
    "u2flib_server": "python-u2flib-server",
    "voicent": "Voicent-Python",
}
# Retrieve python3 version
try:
    p = Popen(["python3", "--version"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    res, err = p.communicate()
    res = res.decode()
    i = res.find("3.")
    if i >= 0:
        PY3ID = res[i] + res[i + 2]
    else:
        PY3ID = "3"
except BaseException:
    PY3ID = "3"
PY3_DEV = "python%s-dev" % PY3ID
DEPS = {
    "astroid": {"python": "six"},
    "barcode": {"python": "python-Levenshtein"},
    "gevent": {"bin": "libevent-dev"},
    "Pillow": {"python": "docutils"},
    "pycups": {"bin": "libcups2-dev"},
    "shapely": {"bin": "libgeos-dev"},
}
DEPS2 = {
    "invoice2data": {"python": "regex<2022.1.18"},
    "lxml": {
        "bin":
            ("python-dev", "python-lxml", "libxml2-dev", "libxslt1-dev", "zlib1g-dev")
    },
    "python-psycopg2": {"bin": ("python-dev", "libpq-dev")},
    "python-ldap": {"bin": ("libsasl2-dev", "libldap2-dev", "libssl-dev")},
}
DEPS3 = {
    "lxml": {
        "bin": ("PY3_DEV", "python3-lxml", "libxml2-dev", "libxslt1-dev", "zlib1g-dev")
    },
    "python-psycopg2": {"bin": ("PY3_DEV", "libpq-dev")},
    "python3-ldap": {"bin": ("libsasl2-dev", "libldap2-dev", "libssl-dev")},
}


def fake_setup(**kwargs):
    globals()["setup_args"] = kwargs


def get_naked_pkgname(pkg):
    return re.split('[!<=>@#;]', python_plus.qsplit(pkg)[0])[0].strip()


def eval_requirement_cond(line, pyver=None, odoo_ver=None):
    pyver = pyver or '3.7'
    items = line.split('#')[0].split(";")
    if len(items) == 1:
        return get_naked_pkgname(line)
    testenv = {"sys_platform": sys.platform,
               "python_version": pyver,
               "odoo_major": int(odoo_ver.split(".")[0])}
    if eval(items[1], testenv):
        return get_naked_pkgname(line)
    return False


def parse_setup(ctx, setup, pyver=None):
    # reqlist = []
    with open(setup, "r") as fd:
        contents = ""
        valid = False
        for ln in fd.read().split("\n"):
            if re.match(r"^ *[-\w]+ *= *[\w]", ln):
                continue
            if "**py2exe_options()" in ln:
                continue
            if ln.startswith("setuptools.setup"):
                valid = True
                ln = ln.replace("setuptools.setup(", "fake_setup(")
            elif ln.startswith("setup"):
                valid = True
                ln = ln.replace("setup(", "fake_setup(")
            ln = ln.replace("% lib_name:", "% '':")
            if valid:
                contents += ln
                contents += "\n"
        try:
            exec(contents)
            setup_args = globals()["setup_args"]
        except BaseException:
            setup_args = []
    if (
        "odoo_addon" in setup_args
        and not isinstance(setup_args["odoo_addon"], bool)
        and "external_dependencies_override" in setup_args["odoo_addon"]
        and "python" in setup_args["odoo_addon"]["external_dependencies_override"]
    ):
        reqlist = []
        for fn in setup_args["odoo_addon"]["external_dependencies_override"][
            "python"
        ].values():
            reqlist.append(fn)
    elif isinstance(setup_args, dict):
        reqlist = [
            x for x in setup_args.get("install_requires", []) if "-addon-" not in x
        ]
    else:
        reqlist = []
    return reqlist


def parse_requirements(ctx, reqfile, pyver=None):
    if reqfile == "openupgradelib":
        return [reqfile]
    reqlist = []
    try:
        with open(reqfile, "r") as fd:
            lines = fd.read().split("\n")
            for line in lines:
                line = re.split('[#]', line)[0].strip()
                if not line:
                    continue
                if eval_requirement_cond(line, pyver=pyver, odoo_ver=ctx["odoo_ver"]):
                    if ctx["keep_cond"]:
                        reqlist.append(line)
                    else:
                        reqlist.append(re.split('[#;]', line)[0].strip())
    except BaseException as e:
        print("File %s: error %s" % (reqfile, e))
    return reqlist


def name_n_version(full_item, with_version=None, odoo_ver=None, pyver=None):
    def comp_ver(version):
        return [int(x) for x in version.split(".")]

    item = os.path.basename(get_naked_pkgname(re.split("[!=<>]", full_item)[0]))
    if item.endswith(".git"):
        item = item[:-4]
    if not filter(lambda x: item.startswith(x), PIP_WITH_DOT):
        if '.' in item:
            full_item = full_item.replace('.' + item.split(".")[1], '')
            item = item.split(".")[0].lower()
    item_l = item.lower()
    if "openupgradelib" not in item_l and item_l in ALIAS:
        full_item = full_item.replace(item, ALIAS[item_l])
        item = ALIAS[item_l]
    if odoo_ver and int(odoo_ver.split('.')[0]) > 10:
        if "openupgradelib" not in item and item in ALIAS3:
            full_item = full_item.replace(item, ALIAS3[item])
            item = ALIAS3[item]
    if (odoo_ver or pyver) and with_version:
        def_v = "0" if "0" in REQVERSION.get(item, {}) else False
        if item in REQVERSION:
            min_v = False
            has_py3 = False
            if odoo_ver:
                for vv in sorted([(comp_ver(x), x) for x in REQVERSION[item].keys()]):
                    v = vv[1]
                    if v.split(".")[0] == "3":
                        has_py3 = True
                    if comp_ver(v) < comp_ver("6.1"):
                        continue
                    if comp_ver(v) <= comp_ver(odoo_ver):
                        if REQVERSION[item][v] == "PYVER":
                            min_v = False
                            break
                        min_v = v
                    if comp_ver(v) >= comp_ver(odoo_ver):
                        break
            if (min_v and REQVERSION[item][min_v] != "PYVER"
                    and (comp_ver(min_v) > comp_ver("10.0") or not has_py3)):
                full_item = merge_item_version(
                    full_item,
                    "%s%s" % (item, REQVERSION[item][min_v]),
                    ignore_error=True)
                def_v = False
            if not min_v or (comp_ver(min_v) <= comp_ver("10.0")
                             and pyver.startswith("3")):
                min_v = False
                for vv in sorted([(comp_ver(x), x) for x in REQVERSION[item].keys()]):
                    v = vv[1]
                    if comp_ver(v) < comp_ver("2.0") or comp_ver(v) >= comp_ver("4.0"):
                        continue
                    if (
                            odoo_ver
                            and ((comp_ver(odoo_ver) <= comp_ver("10.0")
                                  and comp_ver(v) >= comp_ver("3.0"))
                                 or (comp_ver(odoo_ver) > comp_ver("10.0")
                                     and comp_ver(v) < comp_ver("3.0")))
                    ):
                        continue
                    if comp_ver(v) <= comp_ver(pyver):
                        if REQVERSION[item][v] == "PYVER":
                            min_v = False
                            break
                        min_v = v
                    if comp_ver(v) >= comp_ver(pyver):
                        break
            if min_v and REQVERSION[item][min_v] != "PYVER":
                full_item = merge_item_version(
                    full_item,
                    "%s%s" % (item, REQVERSION[item][min_v]),
                    ignore_error=True)
                def_v = False
            if def_v:
                full_item = merge_item_version(
                    full_item,
                    "%s%s" % (item, REQVERSION[item][def_v]),
                    ignore_error=True)

    item = python_plus.qsplit(item)[0].strip()
    full_item = python_plus.qsplit(full_item)[0].strip()
    full_item = re.sub(' *([<=>]+) *', r'\1', full_item.strip())
    if pyver and pyver.startswith("2"):
        if full_item in FORCE_ALIAS2:
            full_item = FORCE_ALIAS2[full_item]
        else:
            full_item = FORCE_ALIAS2.get(full_item, full_item)
    else:
        if full_item in FORCE_ALIAS3:
            full_item = FORCE_ALIAS3[full_item]
        else:
            full_item = FORCE_ALIAS3.get(item, full_item)
    if not re.search("[<=>]+", full_item):
        full_item = ""
    return item, full_item


def version_comparable(version):
    return [int(x) if x.isdigit() else x
            for x in python_plus.qsplit(version)[0].strip().split(".")]


def maxver(left, right):
    return right if version_comparable(right) > version_comparable(left) else left


def minver(left, right):
    return right if version_comparable(right) < version_comparable(left) else left


def split_versions(full_item):
    full_item = python_plus.qsplit(
        python_plus.qsplit(full_item, "#", strip=True)[0])[0]
    ix = 0
    items = []
    while ix < len(full_item):
        x = re.search("([!=<>]+|,)", full_item[ix:])
        if x:
            if x.start():
                items.append(full_item[ix: x.start() + ix])
            items.append(full_item[x.start() + ix: x.end() + ix])
            ix += x.end()
        else:
            items.append(full_item[ix:])
            ix = len(full_item)
    return items


def merge_item_version(left, right, ignore_error=False):
    split_left = split_versions(left)
    split_right = split_versions(right)
    ix_right = 1
    while ix_right < len(split_right):
        op = split_right[ix_right]
        if op not in split_left:
            if op == "==" and any([x for x in split_left if ("<" in x or ">" in x)]):
                ix_right += 1
                split_left = [split_left[0], op, split_right[ix_right]]
            elif (">" not in op and "<" not in op) or "==" not in split_left:
                split_left.append(op)
                ix_right += 1
                split_left.append(split_right[ix_right])
            else:
                ix_right += 1
            ix_right += 1
            if ix_right < len(split_right) and split_right[ix_right] == ",":
                split_left.append(split_right[ix_right])
                ix_right += 1
        else:
            ix_right += 1
            ver_right = split_right[ix_right]
            ix_right += 2
            ix_left = split_left.index(op) + 1
            ver_left = split_left[ix_left]

            if op == "==":
                if ver_left != ver_right:
                    if not ignore_error:
                        sys.stderr.write(
                            "Modules version requirements mismatch: <%s> <%s>\n"
                            % (left, right))
                    if ver_right > ver_left:
                        split_left[ix_left] = ver_right
            elif ">" in op:
                split_left[ix_left] = maxver(ver_left, ver_right)

            else:
                split_left[ix_left] = minver(ver_left, ver_right)

    if split_left[-1] == ",":
        split_left = split_left[: -1]
    return "".join(split_left)


def add_dependencies(deps_list, item, with_version=None, odoo_ver=None, pyver=None):
    if item in DEPS:
        for kw1 in ("python", "bin"):
            if kw1 not in DEPS[item]:
                continue
            if isinstance(DEPS[item][kw1], (tuple, list)):
                for itm in DEPS[item][kw1]:
                    deps_list = add_package(
                        deps_list,
                        kw1,
                        itm,
                        with_version=with_version,
                        odoo_ver=odoo_ver,
                        pyver=pyver,
                    )
            else:
                deps_list = add_package(
                    deps_list,
                    kw1,
                    DEPS[item][kw1],
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
    if pyver and pyver.split(".")[0] == "2" and item in DEPS2:
        for kw1 in ("python", "bin"):
            if kw1 not in DEPS2[item]:
                continue
            if isinstance(DEPS2[item][kw1], (tuple, list)):
                for itm in DEPS2[item][kw1]:
                    deps_list = add_package(
                        deps_list,
                        kw1,
                        itm,
                        with_version=with_version,
                        odoo_ver=odoo_ver,
                        pyver=pyver,
                    )
            else:
                deps_list = add_package(
                    deps_list,
                    kw1,
                    DEPS2[item][kw1],
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
    if pyver and pyver.split(".")[0] == "3" and item in DEPS3:
        for kw1 in ("python", "bin"):
            if kw1 not in DEPS3[item]:
                continue
            if isinstance(DEPS3[item][kw1], (tuple, list)):
                for itm in DEPS3[item][kw1]:
                    deps_list = add_package(
                        deps_list,
                        kw1,
                        itm,
                        with_version=with_version,
                        odoo_ver=odoo_ver,
                        pyver=pyver,
                    )
            else:
                deps_list = add_package(
                    deps_list,
                    kw1,
                    DEPS3[item][kw1],
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
    return deps_list


def add_package(deps_list, kw, item, with_version=None, odoo_ver=None, pyver=None,
                ignore_deps=False):

    def add_full_item(deps_list, kw, with_version, full_item):
        kw1 = "%s1" % kw
        kw2 = "%s2" % kw
        if with_version and full_item:
            found = False
            for ix, kk in enumerate(deps_list[kw2]):
                if kk.startswith(item):
                    deps_list[kw2][ix] = merge_item_version(kk, full_item)
                    found = True
                    break
            if not found:
                deps_list[kw2].append(full_item)
            if item in deps_list[kw1]:
                del deps_list[kw1][deps_list[kw1].index(item)]
        elif item not in deps_list[kw1]:
            deps_list[kw1].append(item)
        return deps_list

    if eval_requirement_cond(item, pyver=pyver, odoo_ver=odoo_ver):
        item = re.split('[#;]', item)[0].strip()
        if item in BUILTIN:
            return deps_list
        if item == "PY3_DEV":
            item = PY3_DEV

        item, full_item = name_n_version(
            item, with_version=with_version, odoo_ver=odoo_ver, pyver=pyver
        )
        if (
            item in BIN_PACKAGES
            or item in BIN_BASE_PACKAGES
            or item in BIN_TEST_PACKAGES
        ):
            kw = "bin"

        if item not in deps_list[kw]:
            deps_list[kw].append(item)
            if kw == "python":
                deps_list = add_full_item(deps_list, kw, with_version, full_item)
                if not ignore_deps:
                    deps_list = add_dependencies(
                        deps_list, item,
                        with_version=with_version, odoo_ver=odoo_ver, pyver=pyver)
            elif kw == "bin":
                deps_list = add_full_item(deps_list, kw, with_version, full_item)

    return deps_list


def package_from_list(
    deps_list, kw, pkg_list, with_version=None, odoo_ver=None, pyver=None
):
    for item in pkg_list:
        if isinstance(item, (list, tuple)):
            for sub in item:
                deps_list = add_package(
                    deps_list,
                    kw,
                    sub,
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
        else:
            deps_list = add_package(
                deps_list,
                kw,
                item,
                with_version=with_version,
                odoo_ver=odoo_ver,
                pyver=pyver,
            )
    return deps_list


def package_from_manifest(
    deps_list, manifest_file, with_version=None, odoo_ver=None, pyver=None
):
    if manifest_file:
        try:
            with open(manifest_file, "r") as fd:
                manifest = ast.literal_eval(fd.read())
        except SyntaxError:
            print("!!Invalid manifest file %s!" % manifest_file)
            manifest = {}
        if manifest.get("external_dependencies"):
            deps = manifest["external_dependencies"]
            for kw in ("python", "bin"):
                if deps.get(kw):
                    for item in deps[kw]:
                        if item in MANIFEST_NAMES:
                            item = MANIFEST_NAMES[item]
                        deps_list = add_package(
                            deps_list,
                            kw,
                            item,
                            with_version=with_version,
                            odoo_ver=odoo_ver,
                            pyver=pyver,
                        )
        elif os.path.basename(os.path.dirname(manifest_file)) == "repository_check":
            for item in ("GitPython==3.1.2", "mercurial==5.4.1"):
                if item in MANIFEST_NAMES:
                    item = MANIFEST_NAMES[item]
                deps_list = add_package(
                    deps_list,
                    "python",
                    item,
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
        if manifest.get("depends"):
            deps = manifest["depends"]
            kw = "modules"
            for item in deps:
                deps_list = add_package(
                    deps_list,
                    kw,
                    item,
                    with_version=with_version,
                    odoo_ver=odoo_ver,
                    pyver=pyver,
                )
    return deps_list


def add_manifest(root, manifests, reqfiles, setups, files, read_from_manifest):
    if "__init__.py" in files:
        for fn in ("__manifest__.py", "__openerp__.py"):
            if fn in files:
                manifests.append(os.path.join(root, fn))
                break
    if not read_from_manifest and "requirements.txt" in files:
        reqfiles.append(os.path.join(root, "requirements.txt"))
    return manifests, reqfiles, setups


def swap(deps, itm1, itm2):
    itm1_id = -1
    itm2_id = -1
    for item in deps:
        x = re.search(r"[a-zA-Z0-9_-]+", item)
        itm0 = item[x.start(): x.end()] if x else item
        if itm0 == itm1:
            itm1_id = deps.index(item)
        elif itm0 == itm2:
            itm2_id = deps.index(item)
        if itm1_id >= 0 and itm2_id >= 0:
            break
    if itm1_id < itm2_id:
        deps[itm2_id], deps[itm1_id] = deps[itm2_id], deps[itm1_id]


def walk_dir(cdir, manifests, reqfiles, setups, read_from_manifest, recurse):

    def parse_manifest(manifests, reqfiles, setups, root, files, no_deep):
        if "/setup/" in root and "setup.py" in files:
            fn = os.path.join(root, "setup.py")
            if fn not in setups:
                setups.append(os.path.join(root, "setup.py"))
        if root.startswith(no_deep):
            return manifests, reqfiles, setups, no_deep
        if (
            not read_from_manifest
            and "__init__.py" in files
            and ("__manifest__.py" in files or "__openerp__.py" in files)
        ):
            no_deep = root
            return manifests, reqfiles, setups, no_deep
        manifests, reqfiles, setups = add_manifest(
            root, manifests, reqfiles, setups, files, read_from_manifest
        )
        return manifests, reqfiles, setups, no_deep

    no_deep = " "
    fn = os.path.join(cdir, "setup.py")
    if os.path.isfile(fn):
        setups.append(fn)

    for root, dirs, files in os.walk(cdir,
                                     topdown=True,
                                     followlinks=False):
        dirs[:] = [
            d
            for d in dirs
            if (
                not d.startswith(".")
                and not d.startswith("_")
                and not d.endswith('~')
                and d not in ("build",
                              "debian",
                              "dist",
                              "doc",
                              "docs",
                              "egg-info",
                              "filestore",
                              "history",
                              "howtos",
                              "images"
                              "migrations",
                              "redhat",
                              "reference",
                              "scripts",
                              "server",
                              # "setup",
                              "tmp",
                              "venv_odoo",
                              "win32")
            )
        ]
        manifests, reqfiles, setups, no_deep = parse_manifest(
            manifests, reqfiles, setups, root, files, no_deep
        )
        if not recurse and root != cdir and '.git' in dirs:
            no_deep = root
    return manifests, reqfiles, setups


def get_pyver_4_odoo(odoo_ver):
    odoo_major = int(odoo_ver.split(".")[0])
    if odoo_major <= 10:
        pyver = "2.7"
    else:
        pyver = "3.%d" % (int((odoo_major - 9) / 2) + 6)
    return pyver


def get_pyver(ctx):
    if not ctx.get("odoo_ver"):
        global python_version
        ctx["pyver"] = python_version
    else:
        ctx["pyver"] = get_pyver_4_odoo(ctx["odoo_ver"])
    return ctx


def get_def_odoo_ver(ctx):
    py_majver = int(ctx["pyver"].split(".")[0])
    if py_majver == 3:
        ctx["odoo_ver"] = "12.0"
    else:
        ctx["odoo_ver"] = "10.0"
    return ctx


def set_def_outfile(ctx):
    if not ctx["odoo_dir"]:
        sys.stderr.write("Please, declare odoo path to write requirements.txt file!\n")
        sys.exit(1)
    ctx["sep"] = "\n"
    ctx["from_manifest"] = True
    ctx["with_version"] = True
    ctx["itypes"] = "python"
    ctx["opt_verbose"] = False
    ctx["base_packages"] = False
    ctx["rpc_packages"] = False
    ctx["secure_packages"] = False
    ctx["test_packages"] = False
    ctx["exclude_devel"] = False
    ctx["oca_dependencies"] = False
    if os.path.isdir(os.path.join(ctx["odoo_dir"], "venv_odoo")):
        ctx["opt_fn"] = os.path.join(ctx["odoo_dir"], "venv_odoo", "requirements.txt")
    else:
        ctx["opt_fn"] = os.path.join(ctx["odoo_dir"], "requirements.txt")
    return ctx


def search_4_odoo_dir(ctx):
    for ldir in ("~/odoo/%s", "~/odoo_%s", "~/odoo-%s", "~/odoo%s", "~/%s"):
        if os.path.isdir(os.path.join(os.path.expanduser(ldir % ctx["odoo_ver"]))):
            ctx["odoo_dir"] = os.path.join(os.path.expanduser(ldir % ctx["odoo_ver"]))
    if not ctx["odoo_dir"]:
        for ldir in sys.path + [os.path.join(os.path.expanduser("~/"))]:
            if os.path.isdir(os.path.join(ldir, "odoo")):
                ctx["odoo_dir"] = os.path.join(ldir, "odoo")
    return ctx


def main(cli_args=None):
    # if not cli_args:
    #     cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs(
        "List Odoo requirements", "© 2017-2023 by SHS-AV s.r.l.", version=__version__
    )
    parser.add_argument("-h")
    parser.add_argument("-b", "--odoo-branch", action="store", dest="odoo_ver")
    parser.add_argument(
        "-B",
        "--base-packages",
        help="Add base & secure packages",
        action="store_true",
        dest="base_packages",
    )
    parser.add_argument(
        "-C",
        "--check-current-packages",
        help="Check for current installed packages",
        action="store_true",
        dest="check_current_packages",
    )
    parser.add_argument(
        "-d",
        "--dependencies-path",
        help="Follow oca dependency repositories in directory list",
        metavar="directory list (comma separated)",
        dest="oca_dependencies",
    )
    parser.add_argument(
        "-j",
        "--just-package",
        help="Return just info of supplied package",
        dest="pypi_name",
    )
    parser.add_argument(
        "-k",
        "--keep-condition",
        help="Keep condition",
        action="store_true",
        dest="keep_cond",
    )
    parser.add_argument(
        "-m",
        "--manifest",
        help="Declare manifest files if no path supplied",
        dest="manifests",
        metavar="file_list",
        default="",
    )
    parser.add_argument(
        "-M",
        "--read-from-manifest",
        help="Read from manifest instead of requirements.txt",
        dest="from_manifest",
        action="store_true",
    )
    parser.add_argument("-n")
    parser.add_argument(
        "-O",
        "--output",
        help="Write output to file requirements.txt",
        dest="out_file",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path where search manifest files",
        dest="odoo_dir",
        metavar="directory",
        default="",
    )
    parser.add_argument(
        "-P",
        "--precise",
        help="Add version to filename",
        action="store_true",
        dest="with_version",
    )
    parser.add_argument("-q")
    parser.add_argument(
        "-r",
        "--recurse",
        help="Recurse across directories",
        action="store_true",
        dest="recurse",
    )
    parser.add_argument(
        "-R",
        "--rpc-packages",
        help="Add packages for xmlrpc/jsonrpc management",
        action="store_true",
        dest="rpc_packages",
    )
    parser.add_argument(
        "-S",
        "--secure-packages",
        help="Add secure packages",
        action="store_true",
        dest="secure_packages",
    )
    parser.add_argument(
        "-s",
        "--sep",
        help="Separator character of list",
        dest="sep",
        metavar="character",
        default=",",
    )
    parser.add_argument(
        "-t",
        "--type",
        help="File type: may be bin,python,both or modules",
        dest="itypes",
        metavar="keyword",
        default="both",
    )
    parser.add_argument(
        "-T",
        "--test-packages",
        help="Add packages for test environment",
        action="store_true",
        dest="test_packages",
    )
    parser.add_argument(
        "-X",
        "--exclude-devel",
        help="Exclude base,rpc,secure and test packages from output list",
        action="store_true",
        dest="exclude_devel",
    )
    parser.add_argument("-V")
    parser.add_argument("-v")
    parser.add_argument("-y", "--python", action="store", dest="pyver")
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if ctx["pyver"]:
        global PY3_DEV
        PY3_DEV = "python%s-dev" % ctx["pyver"]
    if ctx["odoo_ver"] and not ctx["pyver"]:
        ctx = get_pyver(ctx)
    if ctx["out_file"]:
        ctx = set_def_outfile(ctx)
    if (
        not ctx["odoo_dir"]
        and ctx["odoo_ver"]
        and (not ctx["base_packages"]
             and not ctx["rpc_packages"]
             and not ctx["secure_packages"]
             and not ctx["test_packages"])
        or ctx["pypi_name"]
    ):
        ctx = search_4_odoo_dir(ctx)

    manifests = []
    reqfiles = []
    setups = []
    deps_list = {}
    for kw in (
        "python",
        "python1",
        "python2",
        "bin",
        "bin1",
        "bin2",
        "modules",
    ):
        deps_list[kw] = []

    if ctx["pypi_name"]:
        if ctx["itypes"] == "bin":
            deps_list = add_dependencies(
                deps_list,
                ctx["pypi_name"],
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"])
        else:
            if ctx["itypes"] == "both":
                ctx["itypes"] = "python"
            add_package(deps_list,
                        ctx["itypes"],
                        ctx["pypi_name"],
                        with_version=ctx["with_version"],
                        odoo_ver=ctx["odoo_ver"],
                        pyver=ctx["pyver"],
                        ignore_deps=True)
    elif ctx["manifests"]:
        for item in ctx["manifests"].split(","):
            if item.endswith(".py"):
                manifests.append(os.path.expanduser(item))
            else:
                reqfiles.append(os.path.expanduser(item))
    elif ctx["odoo_dir"]:
        if ctx["oca_dependencies"]:
            for cdir in ctx["oca_dependencies"].split(","):
                manifests, reqfiles, setups = walk_dir(
                    cdir, manifests, reqfiles, setups, ctx['from_manifest'], False
                )
        manifests, reqfiles, setups = walk_dir(
            ctx["odoo_dir"],
            manifests,
            reqfiles,
            setups,
            ctx['from_manifest'],
            ctx['recurse'],
        )

    if ctx["check_current_packages"]:
        sts, stdout, stderr = z0lib.run_traced(
            "pip list", verbose=False, dry_run=ctx['dry_run'])
        if sts == 0:
            hdr = 2
            for ln in stdout.split("\n"):
                if hdr:
                    hdr -= 1
                    continue
                if not ln:
                    continue
                pkg = ln.split()[0]
                add_package(deps_list,
                            "python",
                            pkg,
                            with_version=ctx["with_version"],
                            odoo_ver=ctx["odoo_ver"],
                            pyver=ctx["pyver"])

    for setup in setups:
        requirements = parse_setup(ctx, setup, pyver=ctx["pyver"])
        deps_list = package_from_list(
            deps_list,
            "python",
            requirements,
            with_version=ctx["with_version"],
            odoo_ver=ctx["odoo_ver"],
            pyver=ctx["pyver"],
        )
    for reqfile in reqfiles:
        requirements = parse_requirements(ctx, reqfile, pyver=ctx["pyver"])
        deps_list = package_from_list(
            deps_list,
            "python",
            requirements,
            with_version=ctx["with_version"],
            odoo_ver=ctx["odoo_ver"],
            pyver=ctx["pyver"],
        )
    for manifest_file in manifests:
        deps_list = package_from_manifest(
            deps_list,
            manifest_file,
            with_version=ctx["with_version"],
            odoo_ver=ctx["odoo_ver"],
            pyver=ctx["pyver"],
        )
    if ctx["secure_packages"]:
        deps_list = package_from_list(
            deps_list,
            "python",
            PIP_SECURE_PACKAGES,
            with_version=ctx["with_version"],
            odoo_ver=ctx["odoo_ver"],
            pyver=ctx["pyver"],
        )
    if ctx["base_packages"]:
        if not ctx["odoo_ver"]:
            deps_list = package_from_list(
                deps_list,
                "python",
                PIP_BASE_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
            if ctx['pyver'] and int(ctx['pyver'].split('.')[0]) == 3:
                deps_list = package_from_list(
                    deps_list,
                    "python",
                    PIP3_BASE_PACKAGES,
                    with_version=ctx["with_version"],
                    odoo_ver=ctx["odoo_ver"],
                    pyver=ctx["pyver"],
                )
        else:
            deps_list = package_from_list(
                deps_list,
                "python",
                PIP_ODOO_BASE_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
            # odoo_major = int(ctx["odoo_ver"].split(".")[0])
            # if odoo_major >= 10:
            #     deps_list = package_from_list(
            #         deps_list,
            #         "python",
            #         ["lessc"],
            #         with_version=ctx["with_version"],
            #         odoo_ver=ctx["odoo_ver"],
            #         pyver=ctx["pyver"],
            #     )
            deps_list = package_from_list(
                deps_list,
                "bin",
                BIN_BASE_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
    if ctx["test_packages"]:
        if ctx['pyver'] and int(ctx['pyver'].split('.')[0]) == 2:
            deps_list = package_from_list(
                deps_list,
                "python",
                PIP2_TEST_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
        else:
            deps_list = package_from_list(
                deps_list,
                "python",
                PIP3_TEST_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
        deps_list = package_from_list(
            deps_list,
            "bin",
            BIN_TEST_PACKAGES,
            with_version=ctx["with_version"],
            odoo_ver=ctx["odoo_ver"],
            pyver=ctx["pyver"],
        )
    if ctx["rpc_packages"]:
        if ctx["odoo_ver"] and int(ctx["odoo_ver"].split(".")[0]) <= 8:
            deps_list = package_from_list(
                deps_list,
                "python",
                RPC2_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )
        else:
            deps_list = package_from_list(
                deps_list,
                "python",
                RPC3_PACKAGES,
                with_version=ctx["with_version"],
                odoo_ver=ctx["odoo_ver"],
                pyver=ctx["pyver"],
            )

    deps_list["python"] = sorted(
        deps_list["python1"] + deps_list["python2"], key=lambda s: s.lower())
    deps_list["bin"] = sorted(
        deps_list["bin1"] + deps_list["bin2"], key=lambda s: s.lower())
    if ctx["exclude_devel"]:
        for item in (PIP_SECURE_PACKAGES
                     + PIP2_TEST_PACKAGES
                     + PIP3_TEST_PACKAGES
                     + BIN_TEST_PACKAGES
                     + RPC2_PACKAGES
                     + RPC3_PACKAGES):
            rm_list = []
            for ii, dep_pkg in enumerate(deps_list["python"]):
                if deps_list["python"][ii].startswith(item):
                    rm_list.append(ii)
            while len(rm_list):
                ii = rm_list.pop()
                del deps_list["python"][ii]
            for ii, dep_pkg in enumerate(deps_list["bin"]):
                if deps_list["bin"][ii].startswith(item):
                    rm_list.append(ii)
            while len(rm_list):
                ii = rm_list.pop()
                del deps_list["bin"][ii]
    for ii, dep_pkg in enumerate(deps_list["python"]):
        if ">" in dep_pkg or "<" in dep_pkg or " " in dep_pkg:
            deps_list["python"][ii] = "'%s'" % dep_pkg
    for ii, dep_pkg in enumerate(deps_list["bin"]):
        if ">" in dep_pkg or "<" in dep_pkg or " " in dep_pkg:
            deps_list["bin"][ii] = "'%s'" % dep_pkg
    # for item in DEPS:
    #     if "python" in DEPS[item]:
    #         if isinstance(DEPS[item]["python"], (tuple, list)):
    #             for itm in DEPS[item]["python"]:
    #                 swap(deps_list["python"], item, itm)
    #         else:
    #             swap(deps_list["python"], item, DEPS[item]["python"])
    # if ctx["pyver"] and ctx["pyver"].split(".")[0] == "2":
    #     for item in DEPS2:
    #         if "python" in DEPS2[item]:
    #             if isinstance(DEPS2[item]["python"], (tuple, list)):
    #                 for itm in DEPS2[item]["python"]:
    #                     swap(deps_list["python"], item, itm)
    #             else:
    #                 swap(deps_list["python"], item, DEPS2[item]["python"])
    # if ctx["pyver"] and ctx["pyver"].split(".")[0] == "3":
    #     for item in DEPS3:
    #         if "python" in DEPS3[item]:
    #             if isinstance(DEPS3[item]["python"], (tuple, list)):
    #                 for itm in DEPS3[item]["python"]:
    #                     swap(deps_list["python"], item, itm)
    #             else:
    #                 swap(deps_list["python"], item, DEPS3[item]["python"])
    if ctx["out_file"]:
        req_pkgs = []
        try:
            with open(ctx["opt_fn"], "r") as fd:
                for pkg in fd.read().split("\n"):
                    if get_naked_pkgname(pkg):
                        req_pkgs.append(pkg)
        except BaseException:
            pass
        pkgs = []
        for dep_pkg in deps_list["python"]:
            naked_pkg = get_naked_pkgname(dep_pkg)
            found = False
            for req_pkg in req_pkgs:
                pkg = get_naked_pkgname(req_pkg)
                if naked_pkg == pkg:
                    pkgs.append(req_pkg if pkg != req_pkg else dep_pkg)
                    found = True
                    break
            if not found:
                pkgs.append(dep_pkg)
        for req_pkg in req_pkgs:
            pkg = get_naked_pkgname(req_pkg)
            if pkg not in [get_naked_pkgname(x) for x in pkgs]:
                pkgs.append(
                    "%-49s # not found in any manifests" % get_naked_pkgname(req_pkg)
                )
        if len(pkgs):
            bakfile = '%s~' % ctx["opt_fn"]
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(ctx["opt_fn"]):
                os.rename(ctx["opt_fn"], bakfile)
            with open(ctx["opt_fn"], 'w') as fd:
                fd.write(ctx["sep"].join(pkgs))
        print("Updated %s file" % ctx["opt_fn"])
        print(ctx["sep"].join(pkgs))
    else:
        for kw in ("python", "bin", "modules"):
            if kw in deps_list:
                if kw == ctx["itypes"] or (
                    ctx["itypes"] == "both" and kw in ("python", "bin")
                ):
                    if ctx["opt_verbose"]:
                        print("%s=%s" % (kw, ctx["sep"].join(deps_list[kw])))
                    else:
                        print(ctx["sep"].join(deps_list[kw]))


if __name__ == "__main__":
    exit(main())



