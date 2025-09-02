# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="travis_emulator",
    version="2.0.11",
    description="Travis CI emulator for local develop environment",
    long_description='''
Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local Linux
machine. You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**;
all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

    `travis show`

    `less -R ~/travis_log/<build_name>.log`

A travis build executes the following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Optional install packages `apt addons` (emulatore makes just the check)
* Optional install packages `cache`
* Set global values `env global`
* Execute code `before_install`
* Execute matrix initialization, included python version
* Execute build code `install`
* Execute build code `before_script`
* Execute build code `script`
* Execute build `before_cache` (only if cache is effective, not emulated)
* Execute build code `after_success` (emulated) or `after_failure` (not emulated)
* Optional code `before_deploy` (only if deployment is effective, not emulated)
* Optional code `deploy` (not emulated)
* Optional code `after_deploy` (only if deployment is effective, not emulated)
* Execute code `after_script` (not emulated)
* Wep from local .travis.conf (not in travis-ci.org)

Read furthermore info read `travis-ci phase
<https://docs.travis-ci.com/user/job-lifecycle/>`__
''',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        # "Programming Language :: Python :: 3.11",
        # "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
    ],
    keywords="linux travis development",
    url="https://zeroincombenze-tools.readthedocs.io",
    project_urls={
        "Documentation": "https://zeroincombenze-tools.readthedocs.io",
        "Source": "https://github.com/zeroincombenze/tools",
    },
    author="Antonio Maria Vigliotti",
    author_email="antoniomaria.vigliotti@gmail.com",
    license="GPL-3.0-or-later",
    install_requires=["z0lib>=2.0.12", "future"],
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={"": [
        # "scripts/setup.info",
        "./template_travis.yml",
        # "scripts/travis.sh",
        "./travis",
        "./travisrc",
        "./travis.man"
    ]},
    entry_points={
        "console_scripts": [
            # "travis = travis_emulator.scripts.travis:main",
            "travis_emulator-info = travis_emulator.scripts.main:internal_main",
            "make_travis_conf = travis_emulator.make_travis_conf:make_travis_conf",
        ]
    },
    zip_safe=False,
)
