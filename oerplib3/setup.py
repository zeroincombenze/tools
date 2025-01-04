# -*- coding: utf-8 -*-
import os.path as pth
import sys

from setuptools import find_packages, setup

name = "oerp3lib"
github_url = "https://github.com/zeroincombenze/tools"
author = "Sébastien Alix, Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#oerp3lib"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name='oerplib3',
    version='1.0.0',
    description='Python3 oerlib porting',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='openerp odoo server client xml-rpc xmlrpc net-rpc netrpc webservice',
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    install_requires=["future", "configparser"],
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={"": []},
    entry_points={"console_scripts": []},
    zip_safe=False,
)
