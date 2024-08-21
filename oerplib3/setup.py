# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

def names(fn, email=None):
    def nm(item):
        return (item.split("*", 1)[1].split("<", 1)[0].strip()
                if item.startswith("*") else item.split("<", 1)[0].strip())
    def em(item):
        return ("<" + item.split("*", 1)[1].split("<", 1)[1].strip()
                if item.startswith("*") else "<" + item.split("<", 1)[1].strip())
    def al(item):
        return (item.split("*", 1)[0].strip() if item.startswith("*") else item.strip())
    if email == "name":
        with open(fn, "r") as fd:
            return ", ".join([nm(x) for x in fd.read().split("\n") if x])
    elif email == "email":
        with open(fn, "r") as fd:
            return ", ".join([em(x) for x in fd.read().split("\n") if x])
    else:
        with open(fn, "r") as fd:
            return ", ".join([al(x) for x in fd.read().split("\n") if x])

setup(
    name='oerplib3',
    version='0.8.5',
    description='Python3 oerlib porting',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='openerp odoo server client xml-rpc xmlrpc net-rpc netrpc webservice',
    url='https://zeroincombenze-tools.readthedocs.io',
    project_urls={
        'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
        'Source': 'https://github.com/zeroincombenze/tools',
    },
    author='Sébastien Alix, Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license='Affero GPL',
    install_requires=['future', 'configparser'],
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    package_data={'': [
    ]},
    entry_points={
        'console_scripts': [
        ]
    },
    zip_safe=False,
)
