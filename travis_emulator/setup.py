# -*- coding: utf-8 -*-
import os.path as pth

from setuptools import find_packages, setup

name = "travis_emulator"
github_url = "https://github.com/zeroincombenze/tools"
author = "Antonio Maria Vigliotti"
author_email = "antoniomaria.vigliotti@gmail.com"
source_url = "%s/tree/master/%s" % (github_url, name)
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/#travis_emulator"
changelog_url = "%s/blob/master/%s/egg-info/CHANGELOG.rst" % (github_url, name)
try:
    long_description = open(pth.join(pth.dirname(__file__), "README.rst")).read()
except IOError:
    long_description = ""

setup(
    name=name,
    version="2.0.8",
    description="Travis CI emulator for local develop environment",
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
    install_requires=["z0lib", "configparser","future"],
    packages=find_packages(exclude=["docs", "examples", "tests", "junk"]),
    package_data={"": [
        "scripts/setup.info",
        "./template_travis.yml",
        "scripts//travis.sh",
        "scripts//travisrc",
        "./travis.man"
    ]},
    entry_points={
        "console_scripts": [
            "travis_emulator-info = travis_emulator.scripts.main:main",
            "travis = travis_emulator.scripts.travis:main",
            "make_travis_conf = travis_emulator.make_travis_conf:make_travis_conf",
        ]
    },
    zip_safe=False,
)
