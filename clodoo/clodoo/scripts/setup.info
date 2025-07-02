# -*- coding: utf-8 -*-
import os.path as pth
import sys

from setuptools import find_packages, setup

name = "clodoo"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#clodoo"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

if sys.version_info >= (3, 0):
    install_requires = [
        "future",
        "jsonlib-python3",
        "openpyxl",
        "odoorpc<0.10.0",
        "oerplib3",
        "odoo-client-lib",
        # "os0",
        "psycopg2-binary",
        "python-plus",
        "unidecode",
        "z0lib>=2.0.11",
    ]
else:
    install_requires = [
        "future",
        "jsonlib",
        "openpyxl<=3.0",
        "odoorpc<0.10.0",
        "oerplib",
        # "os0",
        "psycopg2-binary",
        "python-plus",
        "unidecode==1.2.0",
        "z0lib>=2.0.11",
    ]

setup(
    name=name,
    version="2.0.14",
    description="Do massive operations on Odoo Cloud",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="odoo",
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="GPL-3.0-or-later",
    install_requires=install_requires,
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={
        "": [
            "scripts/setup.info",
            # "./manage_db",
            # "./manage_odoo",
            # "./manage_odoo.man",
            # "./odoo_install_repository",
            "./odoorc",
            "./transodoo.xlsx",
            "./bck_filestore.sh",
        ]
    },
    entry_points={
        "console_scripts": [
            "clodoo-info = clodoo.scripts.main:main",
            # "clodoo.py = clodoo.clodoo_main:main",
            "transodoo.py = clodoo.transodoo:main",
        ]
    },
    zip_safe=False,
)

