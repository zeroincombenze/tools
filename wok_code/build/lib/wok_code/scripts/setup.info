# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='wok_code',
      version='1.0.4',
      description='Python developers tools',
      long_description="""
Various tools at your fingertips.

The available tools are:

* cvt_csv_2_rst.py: convert csv file into rst file
* cvt_csv_2_xml.py: convert csv file into xml file
* cvt_script: parse bash script and convert to meet company standard
* gen_readme.py: generate documentation files, mainly README.rst
* odoo_dependency.py: show odoo depencies and/or Odoo module tree
* odoo_translation.py: manage Odoo translation
* pep8: parse source .py file to meet pep8 and convert across Odoo versions
* please: developer shell
* wget_odoo_repositories.py: get repository names from github.com
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
      keywords='linux travis development',
      url='https://zeroincombenze-tools.readthedocs.io',
      project_urls={
          'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
          'Source': 'https://github.com/zeroincombenze/tools',
      },
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      install_requires=['z0lib', 'future', 'lxml', 'pyyaml', 'babel', 'twine'],
      packages=find_packages(
          exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
      package_data={
          '': ['scripts/setup.info',
               './please', './please.man',
               './cvt_script', './cvt_script.man',
               'dist_pkg', './topep8',
               './to_oca.2p8', './to_zero.2p8', './to_pep8.2p8']
      },
      entry_points={
          'console_scripts': [
              'wok_code-info = wok_code.scripts.main:main',
              # 'please = wok_code.scripts.please:main',
              # 'gen_readme.py = wok_code.scripts.gen_readme:main',
              # 'cvt_script = wok_code.scripts.cvt_script:main',
              'cvt_csv_2_rst = wok_code.scripts.cvt_csv_2_rst:main',
              # 'cvt_csv_2_xml = wok_code.scripts.cvt_csv_2_xml:main',
              # 'cvt_csv_coa = wok_code.scripts.cvt_csv_coa:main',
          ],
      },
      zip_safe=False)