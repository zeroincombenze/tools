# -*- coding: utf-8 -*-
import os.path as pth

from setuptools import find_packages, setup

name = "zar"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/zerobug"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="2.0.7",
    description="Zeroincombenze Archive Replica",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: System :: System Shells",
    ],
    keywords="backup, restore, replica",
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={
        "": [
            "scripts/setup.info",
            "scripts/pg_db_active.sh",
            "./bck_filestore.sh",
            "./pg_db_reassign_owner",
            "./zar_bck",
            "./zar_cptbl",
            "./zar_purge",
            "./zar_rest",
            "./zar_upd",
            "./zarrc",
        ]
    },
    entry_points={
        'console_scripts': [
            'pg_db_active = zar.scripts.pg_db_active:main',
        ]
    },
    zip_safe=False,
)
