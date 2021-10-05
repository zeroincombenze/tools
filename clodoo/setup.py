# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages
import sys

if sys.version_info >= (3, 0):
    install_requires = [
        'future', 'jsonlib-python3', 'openpyxl', 'odoorpc', 'oerplib',
        'psycopg2-binary', 'python-plus', 'unidecode', 'z0lib'
    ]
else:
    install_requires = [
<<<<<<< HEAD
        'future', 'jsonlib', 'openpyxl', 'odoorpc', 'oerplib',
=======
        'future', 'jsonlib', 'openpyxl<=3.0', 'odoorpc', 'oerplib',
>>>>>>> stash
        'psycopg2-binary', 'python-plus', 'unidecode==1.2.0', 'z0lib'
    ]

setup(name='clodoo',
<<<<<<< HEAD
      version='0.3.34.99',
=======
      version='0.3.36',
>>>>>>> stash
      description='Do massive operations on Odoo Cloud',
      long_description="""
Clodoo is a set of tools to manage to manage multiple Odoo installations with many DBs.

With clodoo you can do massive operations on 1 or more Odoo databases based on
different Odoo versions. Main operation are:

* create consistent database to run tests
* repeat consistent action on many db with same or different Odoo version
* repeat above actions on every new database

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 13.0)
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
      ],
      keywords='odoo',
<<<<<<< HEAD
=======
      url='https://zeroincombenze-tools.readthedocs.io',
>>>>>>> stash
      project_urls={
          'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
          'Source': 'https://github.com/zeroincombenze/tools',
      },
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
<<<<<<< HEAD
          '': ['scripts/setup.conf', './odoorc'],
=======
          '': ['scripts/setup.info', './odoorc', './list_requirements.py'],
>>>>>>> stash
      },
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'clodoo-info = clodoo.scripts.main:main',
<<<<<<< HEAD
              'list_requirements = clodoo.scripts.list_requirements:main',
=======
              # 'list_requirements = clodoo.scripts.list_requirements:main',
>>>>>>> stash
          ],
      },
      zip_safe=False)
