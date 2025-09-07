# -*- coding: utf-8 -*-
import os.path as pth
from setuptools import find_packages, setup

name = "arcangelo"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#arcangelo"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

install_requires = [
    "python_plus>=2.0.19",
    "clodoo",
    "future",
]
# if sys.version_info >= (3, 0):
#     install_requires.append("twine")
#     if sys.version_info >= (3, 7):
#         install_requires.append("distro")
# else:
#     install_requires.append("twine==1.15.0")

setup(
    name=name,
    version="2.1.1",
    description="Source code mass automatic upgrade",
    long_description_content_type="text/x-rst",
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
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
    ],
    keywords="linux odoo documentation development",
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
            "scripts/config/*",
            "scripts/cvt_script.sh",
        ]
    },
    entry_points={
        "console_scripts": [
            "arcangelo = arcangelo.scripts.arcangelo:main",
            "gen_readme.py = arcangelo.scripts.gen_readme:main",
            "cvt_script = arcangelo.scripts.cvt_script:main",
            "cvt_2_rst.py = arcangelo.scripts.cvt_2_rst:main",
        ]
    },
    zip_safe=False,
)
