# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='odoo_score',
      version='1.0.4.2',
      description='Odoo super core',
      long_description="""
Odoo supercore

odoo_score is a library that extends the odoo orm functionality and makes available a simple odoo shell.
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
      keywords='odoo',
      url='https://zeroincombenze-tools.readthedocs.io',
      project_urls={
          'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
          'Source': 'https://github.com/zeroincombenze/tools',
      },
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      install_requires=['z0lib', 'future'],
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
          '': ['scripts/setup.info', './run_odoo_debug'],
      },
      entry_points={
          'console_scripts': [
              'odoo_score-info = odoo_score.scripts.main:main',
              # 'run_odoo_debug = odoo_score.scripts.run_odoo_debug:main'
          ],
      },
      zip_safe=False)
