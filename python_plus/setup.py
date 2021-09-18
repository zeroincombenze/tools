# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='python_plus',
      version='1.0.3.99',
      description='python useful function',
      long_description="""
Various functions.
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
      keywords='unit test virtual environment venv',
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
          '': ['./vem.sh', './vem.man']
      },
      entry_points={
          'console_scripts': [
              'python-plus = z0lib.scripts.main:main',
              'vem = python_plus.scripts.vem:main'
          ],
      },
      zip_safe=False)
