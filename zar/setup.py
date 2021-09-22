# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='zar',
      version='1.3.36.99',
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
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
          '': ['scripts/setup.conf', './pg_db_active.sh', './zar_bck']
      },
      entry_points={
          'console_scripts': [
              'zar-info = zar.scripts.main:main',
              'pg_db_active = zar.scripts.pg_db_active:main'
          ],
      },
      zip_safe=False)
