# -*- coding: utf-8 -*-
import os.path as pth

from setuptools import find_packages, setup

name = "evolve_simulator"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="0.1.0",
    description="Evolve e-invoice web service simulator",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Framework :: Flask",
        "Topic :: Software Development :: Testing",
    ],
    keywords="odoo, fatturapa, e-invoice, sdi, evolve, simulator",
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="LGPL-3.0-or-later",
    python_requires=">=3.7",
    install_requires=[
        "flask",
        # Flask 1.x (the only one working with Odoo 12 Werkzeug) needs itsdangerous.json
        'itsdangerous<2.1;python_version<"3.8"',
        "sqlalchemy>=1.4",
        "pycryptodome",
        "pytz",
    ],
    packages=find_packages(exclude=["docs", "examples", "tests", "*.tests", "junk"]),
    package_data={"evolve_simulator": ["templates/*.html", "static/*.js", "LICENSE"]},
    entry_points={
        "console_scripts": ["evolve-simulator = evolve_simulator.scripts.main:main"]
    },
    zip_safe=False,
)
