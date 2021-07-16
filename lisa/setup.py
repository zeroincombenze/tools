from setuptools import setup

setup(name='lisa',
      version='0.3.1.12',
      description='Linux Install Simplifier App',
      long_description="""
Interactive tool to install, update, remove, query and manage software
for building a complete LAMP server or Odoo server.
LAMP means Linux Apache Mysql PHP;
in recent times, Python, Postgresql and Mariadb were added.
This software is just a front-end for yum, apt-get, pip and other commands,
it is not a real package installer.
You can easily write portable script to install packages
over every Linux distribution.
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: POSIX',
          'Programming Language :: Unix Shell',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: System :: System Shells',
      ],
      keywords='bash, LAMP, install, odoo',
      url='http://wiki.zeroincombenze.org/it/Linux',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['lisa'],
      zip_safe=False)
