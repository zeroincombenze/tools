# -*- coding: utf-8 -*-
# import os
from setuptools import find_packages, setup

name = 'os0'
# fn = './%s/README.rst' % name
# README = ''
# if not os.path.exists(fn):
#     fn = './README.rst'
# try:
#     with open(fn, 'r') as fd:
#         README = fd.read()
# except IOError:
#     print('Module %s without long description' % name)

setup(
    name=name,
    version='2.0.1',
    description='OS indipendent interface',
    long_description_content_type='text/x-rst',
    long_description="""
This module extends python os module with a few new functionality
to interface operating system.

It recognizes file name structure and manages both URI standard name
both local name, as UNC and ODS5.

- URI (Uniform Resource Identifier) is standard posix filename.
- UNC (Uniform Naming Convention) is windows standard
- ODS5 is used for define OpenVMS standard filenames

An example of URI filename is '/home/myfile'.

UNC example for the same of previous URI name is '\\home\\myfile'
(with single backslash).

ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'
""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Operating System :: OS Independent',
    ],
    keywords='os path linux windows openvms',
    url='https://zeroincombenze-tools.readthedocs.io',
    project_urls={
        'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
        'Source': 'https://github.com/zeroincombenze/tools',
    },
    author='Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license="GPL-3.0-or-later",
    install_requires=['z0lib', 'future'],
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    # package_data={'': ['scripts/setup.info']},
    entry_points={'console_scripts': ['os0-info = os0.scripts.main:internal_main']},
    zip_safe=False,
)
