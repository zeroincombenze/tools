# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(name='lisa',
      version='0.3.2.1',
      description='Linux Install Simplifier App',
      long_description="""
lis* stands for Linux Install Simplifier App

lisa is an interactive tool to install, update, remove, query and manage software for building a complete LAMP server.
LAMP means Linux Apache Mysql PHP; in recent times, Python and Postgresql were added.

lisa is just a front-end for yum and apt-get commands, it is not a real package installer.
It require yum on CentOS and Red Hat family distros, and apt-get on Ubuntu and debian family distros.
It is very useful to manage all the packages needed to build a complete LAMP server and to check the real server status.
For every main package, may be managed some dependent package; i.e. openssh-server manages openssh-client too.

You can easily write portable script to install packages on every Linux distribution.
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
      keywords='bash, LAMP, install, odoo',
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
          '': ['./lisa.sh', 'lisa.man', 'lisa.conf.sample', 'lisa_bld_ods']
      },
      entry_points={
          'console_scripts': [
              'lisa-info = lisa.scripts.main:main',
              'lisa = lisa.scripts.lisa:main'
          ],
      },
      zip_safe=False)
