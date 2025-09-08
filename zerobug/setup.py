# -*- coding: utf-8 -*-
import os.path as pth
import sys

from setuptools import find_packages, setup

name = "zerobug"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#zerobug"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

if sys.version_info >= (3, 0):
    install_requires = (
        [
            "future",
            "coverage",
            "pylint-odoo",
            "python-magic",
            "python-plus>=2.0.19",
            "z0lib>=2.1.0",
        ],
    )
else:
    install_requires = (
        [
            "future",
            "coverage",
            "pylint-odoo<=3.10.0",
            "python-magic",
            "python-plus>=2.0.19",
            "z0lib>=2.1.0",
        ],
    )

setup(
    name=name,
    version="2.0.20",
    description="Zeroincombenze continuous testing framework"
    " and tools for python and bash programs",
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
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: System Shells",
    ],
    keywords="bash, optargs",
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
    packages=find_packages(exclude=["docs", "examples", "tests", "junk"]),
    package_data={
        "": [
            "./z0testrc",
            "_travis/*",
            "_travis/cfg/*",
        ]
    },
    entry_points={
        "console_scripts": [
            "zerobug-info = zerobug.scripts.main:internal_main",
            # "travis_after_tests_success
            # = zerobug._travis.travis_after_tests_success:main",
            # "travis_install_env = zerobug.scripts.travis_install_env:main",
            # "travis_run_pypi_tests = zerobug.scripts.travis_run_pypi_tests:main",
            # "zerobug = zerobug.scripts:main",
            "zerobug = zerobug.__main__:main",
        ]
    },
    zip_safe=False,
)
