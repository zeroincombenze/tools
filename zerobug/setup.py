# -*- coding: utf-8 -*-
import os.path as pth
import sys

from setuptools import find_packages, setup

author = "Antonio Maria Vigliotti"
author_email = "<info@shs-av.com>"
source_url = "https://github.com/zeroincombenze/tools/tree/master/zerobug"
doc_url = "https://zeroincombenze-tools.readthedocs.io/en/latest/zerobug"
changelog_url = "https://github.com/zeroincombenze/tools/blob/master/zerobug/egg-info/CHANGELOG.rst"


if sys.version_info >= (3, 0):
    install_requires = (
        [
            'future',
            'coverage',
            'pylint-odoo',
            'python-magic',
            'python-plus',
            'os0',
            'z0lib',
        ],
    )
else:
    install_requires = (
        [
            'future',
            'coverage',
            # 'pylint-odoo<=5.0.0',
            'pylint-odoo==3.5.0',
            'python-magic',
            'python-plus',
            'os0',
            'z0lib',
        ],
    )

setup(
    name='zerobug',
    version='2.0.9',
    description='Zeroincombenze continuous testing framework'
    ' and tools for python and bash programs',
    long_description=open(pth.join(pth.dirname(__file__), "README.rst")).read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: System Shells',
    ],
    keywords='bash, optargs',
    url="https://github.com/zeroincombenze/tools",
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license='Affero GPL',
    install_requires=install_requires,
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    package_data={
        '': [
            'scripts/setup.info',
            './z0testrc',
            '_travis/*',
            '_travis/cfg/*',
            # '_travis/travis_install_env.sh',
            # '_travis/travis_run_pypi_tests.sh'
        ]
    },
    entry_points={
        'console_scripts': [
            'zerobug-info = zerobug.scripts.main:main',
            # 'travis_after_tests_success = zerobug._travis.travis_after_tests_success:main',
            # 'travis_install_env = zerobug.scripts.travis_install_env:main',
            # 'travis_run_pypi_tests = zerobug.scripts.travis_run_pypi_tests:main',
            # 'zerobug = zerobug.scripts:main',
            'zerobug = zerobug.zerobug:main',
        ]
    },
    zip_safe=False,
)




