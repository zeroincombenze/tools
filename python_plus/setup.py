# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='python_plus',
<<<<<<< HEAD
      version='1.0.3.99',
=======
      version='1.0.3.7',
>>>>>>> stash
      description='python useful function',
      long_description="""
Python supplemental features
----------------------------

python_plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from Python 2 to Python 3 and still have it run on Python 2.


vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package is released with an nice command:
**vem** that is an interactive tool with some nice features to manage standard virtual environment and it is osx/darwin compatible.
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
      keywords='unit test virtual environment venv',
      project_urls={
          'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
          'Source': 'https://github.com/zeroincombenze/tools',
      },
<<<<<<< HEAD
=======
      url='https://zeroincombenze-tools.readthedocs.io',
>>>>>>> stash
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
<<<<<<< HEAD
          '': ['scripts/setup.conf', './vem.sh', './vem.man']
=======
          '': ['scripts/setup.info', './vem', './vem.man']
>>>>>>> stash
      },
      entry_points={
          'console_scripts': [
              'python-plus-info = python_plus.scripts.main:main',
<<<<<<< HEAD
              'vem = python_plus.scripts.vem:main'
          ],
      },
=======
              # 'vem = python_plus.scripts.vem:main'
          ],
      },
      # install_requires=['clodoo'],        # circular dependency!!!
>>>>>>> stash
      zip_safe=False)
