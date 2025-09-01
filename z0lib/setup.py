# -*- coding: utf-8 -*-
import os.path as pth

from setuptools import find_packages, setup

name = "z0lib"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#z0lib"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="2.0.17",
    description="Bash zeroincombenze lib",
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
    install_requires=["configparser", "future"],
    packages=find_packages(exclude=["docs", "examples", "tests", "junk"]),
    package_data={"": ["./xuname", "./z0librc"]},
    entry_points={"console_scripts": ["z0lib-info = z0lib.scripts.main:internal_main"]},
    zip_safe=False,
)
