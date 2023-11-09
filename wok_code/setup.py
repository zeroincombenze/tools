# -*- coding: utf-8 -*-
import os.path as pth
import sys
from setuptools import find_packages, setup

name = "wok_code"
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

install_requires = [
    "clodoo", "z0lib", "os0",
    "future", "Babel", "lxml", "openpyxl", "pyyaml"
]
if sys.version_info >= (3, 0):
    install_requires.append("translators")
    install_requires.append("twine")
else:
    install_requires.append("twine==1.15.0")

setup(
    name=name,
    version="2.0.12",
    description="Python developers tools",
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
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
    ],
    keywords="linux travis development",
    url=github_url,
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    install_requires=install_requires,
    packages=find_packages(exclude=["docs", "examples", "tests", "junk"]),
    package_data={
        "": [
            "scripts/setup.info",
            "scripts/dist_pkg.sh",
            "scripts/please.sh",
            "scripts/config/*",
            "scripts/run_odoo_debug.sh",
            "./please.man",
            "./cvt_script",
            "./cvt_script.man",
            "./topep8",
            "./to_oca.2p8",
            "./to_zero.2p8",
            "./to_pep8.2p8",
            "./pypi.sh",
            "./install_python_3_from_source.sh",
            "./cvt_csv_2_xml.py",
        ]
    },
    entry_points={
        "console_scripts": [
            "wok_code-info = wok_code.scripts.main:main",
            "cvt_csv_2_rst.py = wok_code.scripts.cvt_csv_2_rst:main",
            "cvt_csv_coa = wok_code.scripts.cvt_csv_coa:main",
            "deploy_odoo = wok_code.scripts.deploy_odoo:main",
            "dist_pkg = wok_code.scripts.dist_pkg:main",
            "do_gitignore = wok_code.do_gitignore:main",
            "do_git_checkout_new_branch = wok_code.do_git_checkout_new_branch:main",
            "arcangelo = wok_code.scripts.arcangelo:main",
            "do_odoo_site.py = wok_code.scripts.do_odoo_site:main",
            "gen_readme.py = wok_code.scripts.gen_readme:main",
            "lint_2_compare = wok_code.scripts.lint_2_compare:main",
            "makepo_it.py = wok_code.scripts.makepo_it:main",
            "odoo_dependencies.py = wok_code.scripts.odoo_dependencies:main",
            "odoo_translation.py = wok_code.scripts.odoo_translation:main",
            "please = wok_code.scripts.please:main",
            "to_pep8.py = wok_code.scripts.to_pep8:main",
            "wget_odoo_repositories.py = wok_code.scripts.wget_odoo_repositories:main",
            "run_odoo_debug = wok_code.scripts.run_odoo_debug:main",
        ]
    },
    zip_safe=False,
)

