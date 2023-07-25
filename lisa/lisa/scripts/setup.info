# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='lisa',
    version='2.0.2',
    description='Linux Install Simplifier App',
    long_description="""
Interactive tool to install, update, remove, query and manage software
for building a complete LAMP server or Odoo server.
LAMP means Linux Apache Mysql PHP;
in recent times, Python, Postgresql and Mariadb were added.
This software is just a front-end for yum, apt-get, pip and other commands,
it is not a real package installer.
You can easily write portable script to install packages
over every Linux distribution.
""",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Unix Shell',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: System Shells',
    ],
    keywords='bash, LAMP, install, odoo',
    url='http://wiki.zeroincombenze.org/it/Linux',
    author='Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license='Affero GPL',
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    package_data={'': [
        'scripts/setup.info',
        'scripts/lisa_bld_ods.sh',
        'scripts/odoo-server_Debian',
        'scripts/odoo-server_RHEL',
    ]},
    entry_points={
        'console_scripts': [
            'lisa-info = lisa.scripts.main:main',
            'lisa_bld_ods = lisa.scripts.lisa_bld_ods:main',
        ]
    },
    zip_safe=False,
)
