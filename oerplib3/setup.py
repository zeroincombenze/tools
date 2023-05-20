# -*- coding: UTF-8 -*-
from setuptools import find_packages, setup

setup(
    name='oerplib3',
    version='0.8.4',
    description='Python3 oerlib porting',
    long_description="""OERPLib3 is a Python module providing an easy way to pilot
     your OpenERP and Odoo servers through RPC.
     Pleas do not yet use this code: it is experimental code
""",
    classifiers=[
        'Development Status :: 3 - Alpha',
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
