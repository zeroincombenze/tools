# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='z0lib',
      version='1.0.5',
      description='Bash zeroincombenze lib',
      long_description="""
General purpose bash and python library for zeroincombenze(R) tools

Features:

* xuname: unix/linux platform recognizer (tested on various environments)
* parseoptargs: line command parser; expands python argparse and adds same functionalities to bash scripts
* tracelog: manage tracelog (only bash)
* findpkg: find package in file system (only bash)
* run_traced: execute (or dry_run) shell command (only bash)
* CFG: local dictionary values from config file like python ConfigParser (only bash)
""",
      classifiers=[
          'Development Status :: 4 - Beta',
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
      keywords='bash, optargs',
      url='https://zeroincombenze-tools.readthedocs.io',
      project_urls={
          'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
          'Source': 'https://github.com/zeroincombenze/tools',
      },
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      install_requires=['future'],
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
          '': ['scripts/setup.info', './z0librc']
      },
      entry_points={
          'console_scripts': [
              'z0lib-info = z0lib.scripts.main:main'
          ],
      },
      zip_safe=False)
