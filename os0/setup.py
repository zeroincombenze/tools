# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='os0',
      version='1.0.1.1',
      description='OS indipendent interface',
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
 (with single backslash)
ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'

See https://en.wikipedia.org/wiki/Path_(computing)
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
      license='Affero GPL',
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
          '': ['scripts/setup.info'],
      },
      entry_points={
          'console_scripts': [
              'os0-info = os0.scripts.main:main'
          ],
      },
      zip_safe=False)
