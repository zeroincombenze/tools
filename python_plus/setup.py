# -*- coding: utf-8 -*-
import os.path as pth
import sys

from setuptools import find_packages, setup

name = "python_plus"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#python_plus"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="2.0.12",
    description="python useful function",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
    keywords="unit test virtual environment venv",
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    install_requires=["configparser", "future", "z0lib"],
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={"": ["scripts/setup.info", "scripts/vem.sh", "./vem.man"]},
    entry_points={
        "console_scripts": [
            "python-plus-info = python_plus.scripts.main:main",
            "vem = python_plus.scripts.vem:main",
            'list_requirements.py = python_plus.scripts.list_requirements:main',
        ]
    },
    zip_safe=False,
)



