# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='zar',
    version='2.0.0',
    description='Zeroincombenze Archive Replica',
    long_description="""
ZAR stand for Zeroincombenze® Archive Replica.
It is a tool kit to backup, restore, replicate files and/or database.

ZAR manages easily backup for Odoo database, keeps last nth copies and purges oldest copies.
""",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: System Shells',
    ],
    keywords='backup, restore, replica',
    project_urls={
        'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
        'Source': 'https://github.com/zeroincombenze/tools',
    },
    author='Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license='Affero GPL',
    packages=['zar'],
    zip_safe=False,
)
