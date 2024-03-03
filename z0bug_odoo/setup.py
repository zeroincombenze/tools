# -*- coding: utf-8 -*-
import os.path as pth
# import sys

from setuptools import find_packages, setup

name = "z0bug_odoo"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/z0bug_odoo"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="2.0.17",
    description="Odoo testing framework",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: System Shells",
    ],
    keywords="unit test debug",
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    install_requires=["future", "python-magic", "zerobug", "gitPython", "Click"],
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={
        "": [
            "scripts/setup.info",
            "data/*",
            "travis/cfg/*",
            "travis/pylint_deprecated_modules/*",
            "travis/pylint_deprecated_modules/openerp/*",
            "travis/pylint_deprecated_modules/openerp/osv/*",
            "travis/clone_oca_dependencies",
            "travis/test_flake8",
            "travis/test_pylint",
            "travis/travis_makepot",
            "travis/travis_run_flake8",
            "travis/travis_run_tests",
            "travis/travis_test_dependencies",
        ]
    },
    entry_points={
        "console_scripts": [
            "z0bug-odoo-info = z0bug_odoo.scripts.main:main",
            # "travis_run_tests = z0bug_odoo.travis.travis_run_tests:main",
        ]
    },
    zip_safe=False,
)





